import base64
import io

import pyotp
import qrcode
from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.exceptions import (
    APIError,
    BusinessRuleError,
    NotFoundError,
    UnauthorizedError,
)
from apps.users.models import PasswordResetToken, User, UserSession
from apps.authentication.services import AuthService


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    mfa_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def validate(self, attrs):
        email = attrs.get("email", "").strip()
        password = attrs.get("password", "")
        mfa_code = attrs.get("mfa_code")

        user, error_message = AuthService.authenticate_user(email, password)
        if error_message:
            raise UnauthorizedError(error_message)

        if user.mfa_enabled:
            if not mfa_code:
                raise APIError(
                    code="MFA_REQUIRED",
                    message="Multi-factor authentication code is required.",
                    status_code=400,
                )
            if not AuthService.verify_mfa_code(user.mfa_secret, mfa_code):
                raise UnauthorizedError("Invalid MFA code. Please try again.")

        attrs["user"] = user
        attrs["email"] = email
        return attrs


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    mfa_code = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.fields:
            del self.fields["username"]

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["first_name"] = user.first_name
        token["last_name"] = user.last_name
        token["role"] = user.role
        if user.tenant:
            token["tenant_id"] = str(user.tenant_id)
        else:
            token["tenant_id"] = None
        return token

    def validate(self, attrs):
        email = attrs.get("email", "").strip()
        password = attrs.get("password", "")
        mfa_code = attrs.get("mfa_code")

        user, error_message = AuthService.authenticate_user(email, password)
        if error_message:
            raise UnauthorizedError(error_message)

        if user.mfa_enabled:
            if not mfa_code:
                raise APIError(
                    code="MFA_REQUIRED",
                    message="Multi-factor authentication code is required.",
                    status_code=400,
                )
            if not AuthService.verify_mfa_code(user.mfa_secret, mfa_code):
                user.failed_login_attempts += 1
                update_fields = ["failed_login_attempts"]
                if user.failed_login_attempts >= 5:
                    user.lock_account(minutes=30)
                    raise APIError(
                        code="ACCOUNT_LOCKED",
                        message="Account locked due to too many failed MFA attempts.",
                        status_code=423,
                    )
                user.save(update_fields=update_fields)
                raise UnauthorizedError("Invalid MFA code. Please try again.")

        login_result = AuthService.login(user)
        if login_result:
            if login_result.get("force_password_change"):
                raise APIError(
                    code="FORCE_PASSWORD_CHANGE",
                    message=login_result["message"],
                    status_code=403,
                )
            if login_result.get("mfa_required"):
                raise APIError(
                    code="MFA_REQUIRED",
                    message=login_result["message"],
                    status_code=400,
                )

        if user.tenant and user.tenant.is_trial_expired:
            raise APIError(
                code="TENANT_TRIAL_EXPIRED",
                message="Your company subscription has expired. Please contact support.",
                status_code=403,
            )

        data = super().validate(attrs)
        refresh = self.get_token(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        data["user"] = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "tenant_id": str(user.tenant_id) if user.tenant else None,
            "mfa_enabled": user.mfa_enabled,
            "force_password_change": user.force_password_change,
        }
        return data


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, attrs):
        refresh_token = attrs.get("refresh")
        if not refresh_token:
            raise APIError(
                code="VALIDATION_ERROR",
                message="Refresh token is required.",
                status_code=400,
            )
        attrs["refresh"] = refresh_token
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, trim_whitespace=False)
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, min_length=12)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise UnauthorizedError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        from django.contrib.auth.password_validation import validate_password
        user = self.context["request"].user
        validate_password(value, user=user)
        if value == self.initial_data.get("old_password", ""):
            raise BusinessRuleError("New password must be different from the current password.")
        return value

    def validate(self, attrs):
        if attrs["old_password"] == attrs["new_password"]:
            raise BusinessRuleError("New password must be different from the current password.")
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        AuthService.change_password(user, self.validated_data["old_password"], self.validated_data["new_password"])
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email__iexact=value, is_active=True)
        except User.DoesNotExist:
            return value
        return value

    def save(self, **kwargs):
        email = self.validated_data["email"]
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
            token, expires_at = AuthService.create_password_reset_token(user)
            return {
                "message": "If an account with that email exists, a password reset link has been sent.",
                "token": token,
                "expires_at": expires_at,
            }
        except User.DoesNotExist:
            return {
                "message": "If an account with that email exists, a password reset link has been sent.",
            }


class ResetPasswordConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, trim_whitespace=False, min_length=12)

    def validate_new_password(self, value):
        from django.contrib.auth.password_validation import validate_password
        validate_password(value)
        return value

    def validate_token(self, value):
        try:
            reset_token = PasswordResetToken.objects.get(token=value)
        except PasswordResetToken.DoesNotExist:
            raise NotFoundError("Password reset token")
        if not reset_token.is_valid:
            raise BusinessRuleError("Password reset token has expired or has already been used.")
        return value

    def validate(self, attrs):
        return attrs

    def save(self, **kwargs):
        AuthService.reset_password(
            self.validated_data["token"],
            self.validated_data["new_password"],
        )
        return True


class EnableMFASerializer(serializers.Serializer):
    def to_representation(self, instance):
        user = self.context["request"].user
        if user.mfa_enabled:
            raise BusinessRuleError("MFA is already enabled for this account.")
        secret = AuthService.generate_mfa_secret()
        otp_uri = AuthService.get_mfa_uri(user, secret)
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return {
            "secret": secret,
            "otp_uri": otp_uri,
            "qr_code_url": f"data:image/png;base64,{qr_code_base64}",
            "message": "Scan the QR code with your authenticator app, then verify with the code to complete setup.",
        }


class VerifyMFASerializer(serializers.Serializer):
    code = serializers.CharField(max_length=6, min_length=6)
    secret = serializers.CharField(required=False, allow_blank=True)

    def validate_code(self, value):
        if not value.isdigit():
            raise APIError(
                code="VALIDATION_ERROR",
                message="MFA code must be exactly 6 digits.",
                status_code=400,
            )
        return value

    def validate(self, attrs):
        code = attrs["code"]
        user = self.context["request"].user
        secret = attrs.get("secret") or user.mfa_secret
        if not secret:
            raise BusinessRuleError("MFA has not been initiated. Please enable MFA first.")
        if not AuthService.verify_mfa_code(secret, code):
            raise UnauthorizedError("Invalid MFA code. Please try again.")
        attrs["secret"] = secret
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        secret = self.validated_data["secret"]
        if user.mfa_enabled:
            if not user.mfa_secret:
                user.mfa_secret = secret
                user.mfa_enabled = True
                user.save(update_fields=["mfa_secret", "mfa_enabled", "updated_at"])
            return {"message": "MFA code verified successfully.", "mfa_enabled": True}
        else:
            user.mfa_secret = secret
            user.mfa_enabled = True
            user.save(update_fields=["mfa_secret", "mfa_enabled", "updated_at"])
            return {"message": "MFA has been enabled successfully.", "mfa_enabled": True}


class DisableMFASerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise UnauthorizedError("Invalid password.")
        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise APIError(
                code="VALIDATION_ERROR",
                message="MFA code must be exactly 6 digits.",
                status_code=400,
            )
        return value

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.mfa_enabled:
            raise BusinessRuleError("MFA is not enabled for this account.")
        if not AuthService.verify_mfa_code(user.mfa_secret, attrs["code"]):
            raise UnauthorizedError("Invalid MFA code.")
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        AuthService.disable_mfa(user, self.validated_data["password"], self.validated_data["code"])
        return {"message": "MFA has been disabled successfully.", "mfa_enabled": False}
