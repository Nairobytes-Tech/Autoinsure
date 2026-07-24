import hashlib
import secrets
import uuid

import pyotp
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.core.exceptions import (
    APIError,
    BusinessRuleError,
    NotFoundError,
    UnauthorizedError,
)
from apps.users.models import PasswordResetToken, UserSession

User = get_user_model()

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 30
PASSWORD_RESET_TOKEN_EXPIRY_MINUTES = 60


class AuthService:
    @staticmethod
    def authenticate_user(email, password):
        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            return None, "Invalid email or password."
        if not user.is_active:
            return None, "This account has been deactivated."
        if user.is_locked:
            return None, (
                "Account is locked due to too many failed login attempts. "
                "Please try again later or contact an administrator."
            )
        if not user.check_password(password):
            user.failed_login_attempts += 1
            update_fields = ["failed_login_attempts"]
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.lock_account(minutes=LOCKOUT_MINUTES)
                return None, (
                    "Account has been locked due to too many failed login attempts. "
                    "Please try again later or contact an administrator."
                )
            user.save(update_fields=update_fields)
            remaining = MAX_FAILED_ATTEMPTS - user.failed_login_attempts
            return None, f"Invalid email or password. {remaining} attempt(s) remaining before account lock."
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            user.save(update_fields=["failed_login_attempts"])
        return user, None

    @staticmethod
    def login(user, request_data=None):
        if user.force_password_change:
            return {
                "force_password_change": True,
                "message": "You must change your password before continuing.",
            }
        if user.mfa_enabled:
            return {
                "mfa_required": True,
                "message": "Multi-factor authentication code required.",
            }
        return None

    @staticmethod
    def create_session(user, token_jti, request=None):
        ip_address = None
        user_agent = ""
        device_info = {}
        if request:
            ip_address = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip() or request.META.get("REMOTE_ADDR")
            user_agent = request.META.get("HTTP_USER_AGENT", "")
        session = UserSession.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            device_info=device_info,
            token_jti=token_jti,
        )
        return session

    @staticmethod
    def logout(user, token_jti=None):
        deactivated = 0
        if token_jti:
            sessions = UserSession.objects.filter(user=user, token_jti=token_jti, is_active=True)
            deactivated = sessions.update(is_active=False)
        else:
            sessions = UserSession.objects.filter(user=user, is_active=True)
            deactivated = sessions.update(is_active=False)
        return deactivated

    @staticmethod
    def refresh_token(user):
        if not user.is_active:
            raise UnauthorizedError("This account has been deactivated.")
        if user.is_locked:
            raise UnauthorizedError("This account is locked.")
        return True

    @staticmethod
    def generate_mfa_secret():
        secret = pyotp.random_base32()
        return secret

    @staticmethod
    def get_mfa_uri(user, secret):
        issuer = getattr(settings, "MFA_ISSUER_NAME", "AutoInsure Connect")
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(name=user.email, issuer_name=issuer)

    @staticmethod
    def verify_mfa_code(secret, code):
        if not code or not secret:
            return False
        totp = pyotp.TOTP(secret)
        return totp.verify(code, valid_window=1)

    @staticmethod
    def enable_mfa(user):
        secret = AuthService.generate_mfa_secret()
        uri = AuthService.get_mfa_uri(user, secret)
        user.mfa_secret = secret
        user.mfa_enabled = True
        user.save(update_fields=["mfa_secret", "mfa_enabled", "updated_at"])
        return {
            "otp_uri": uri,
            "secret": secret,
        }

    @staticmethod
    def confirm_enable_mfa(user, code):
        if not user.mfa_secret:
            raise BusinessRuleError("MFA setup has not been initiated.")
        if not AuthService.verify_mfa_code(user.mfa_secret, code):
            raise UnauthorizedError("Invalid MFA code. Please try again.")
        user.mfa_enabled = True
        user.save(update_fields=["mfa_enabled", "updated_at"])
        return True

    @staticmethod
    def disable_mfa(user, password, code):
        if not user.mfa_enabled:
            raise BusinessRuleError("MFA is not enabled for this account.")
        if not user.check_password(password):
            raise UnauthorizedError("Invalid password.")
        if not AuthService.verify_mfa_code(user.mfa_secret, code):
            raise UnauthorizedError("Invalid MFA code.")
        user.mfa_enabled = False
        user.mfa_secret = ""
        user.save(update_fields=["mfa_enabled", "mfa_secret", "updated_at"])
        return True

    @staticmethod
    def create_password_reset_token(user):
        token_value = secrets.token_urlsafe(48)
        expires_at = timezone.now() + timezone.timedelta(minutes=PASSWORD_RESET_TOKEN_EXPIRY_MINUTES)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token=token_value,
            expires_at=expires_at,
        )
        return reset_token.token, expires_at

    @staticmethod
    def verify_password_reset_token(token):
        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise NotFoundError("Password reset token")
        if not reset_token.is_valid:
            raise BusinessRuleError("Password reset token has expired or has already been used.")
        return reset_token

    @staticmethod
    def reset_password(token, new_password):
        reset_token = AuthService.verify_password_reset_token(token)
        user = reset_token.user
        user.set_password(new_password)
        user.force_password_change = False
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["password", "force_password_change", "failed_login_attempts", "locked_until", "updated_at"])
        reset_token.used = True
        reset_token.save(update_fields=["used"])
        UserSession.objects.filter(user=user, is_active=True).update(is_active=False)
        return True

    @staticmethod
    def change_password(user, old_password, new_password):
        if not user.check_password(old_password):
            raise UnauthorizedError("Current password is incorrect.")
        user.set_password(new_password)
        if user.force_password_change:
            user.force_password_change = False
        user.save(update_fields=["password", "force_password_change", "updated_at"])
        return True

    @staticmethod
    def lock_account(user, minutes=None):
        if minutes is None:
            minutes = LOCKOUT_MINUTES
        user.lock_account(minutes=minutes)
        return True

    @staticmethod
    def unlock_account(user):
        user.unlock_account()
        return True

    @staticmethod
    def get_user_sessions(user):
        return UserSession.objects.filter(user=user, is_active=True).order_by("-last_activity")

    @staticmethod
    def delete_session(user, session_id):
        try:
            session = UserSession.objects.get(id=session_id, user=user, is_active=True)
        except UserSession.DoesNotExist:
            raise NotFoundError("Session", session_id)
        session.deactivate()
        return True
