import logging

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.exceptions import APIError, BusinessRuleError, NotFoundError
from apps.users.models import UserSession

from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    DisableMFASerializer,
    EnableMFASerializer,
    LoginSerializer,
    ResetPasswordConfirmSerializer,
    ResetPasswordSerializer,
    TokenRefreshSerializer,
    VerifyMFASerializer,
)
from .services import AuthService

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        response_data = {
            "access": data["access"],
            "refresh": data["refresh"],
            "user": data.get("user", {}),
        }

        refresh_token = RefreshToken(data["refresh"])
        token_jti = str(refresh_token["jti"])
        user = serializer.user
        session = AuthService.create_session(user, token_jti, request)
        response_data["session_id"] = str(session.id)

        logger.info("User %s logged in successfully.", user.email)
        return Response(response_data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.jti = token["jti"]
                token.blacklist()
        except Exception:
            pass

        AuthService.logout(request.user)

        logger.info("User %s logged out.", request.user.email)
        return Response(
            {"message": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        refresh_token_value = serializer.validated_data["refresh"]
        try:
            refresh = RefreshToken(refresh_token_value)
        except Exception:
            raise APIError(
                code="INVALID_TOKEN",
                message="Invalid or expired refresh token.",
                status_code=401,
            )

        AuthService.refresh_token(refresh.user)

        new_access = str(refresh.access_token)

        from rest_framework_simplejwt.settings import api_settings as jwt_settings

        if getattr(jwt_settings, "ROTATE_REFRESH_TOKENS", False):
            new_refresh = str(refresh)
            if getattr(jwt_settings, "BLACKLIST_AFTER_ROTATION", False):
                refresh.blacklist()
            return Response(
                {"access": new_access, "refresh": new_refresh},
                status=status.HTTP_200_OK,
            )

        return Response(
            {"access": new_access},
            status=status.HTTP_200_OK,
        )


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info("User %s changed their password.", request.user.email)
        return Response(
            {"message": "Password changed successfully."},
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(
            {"message": result["message"]},
            status=status.HTTP_200_OK,
        )


class ResetPasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ResetPasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password has been reset successfully. You may now log in with your new password."},
            status=status.HTTP_200_OK,
        )


class EnableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = EnableMFASerializer(data={}, context={"request": request})
        data = serializer.to_representation(None)
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if user.mfa_enabled:
            raise BusinessRuleError("MFA is already enabled for this account.")
        secret = AuthService.generate_mfa_secret()
        user.mfa_secret = secret
        user.save(update_fields=["mfa_secret", "updated_at"])

        otp_uri = AuthService.get_mfa_uri(user, secret)

        import base64
        import io

        import qrcode

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(otp_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return Response(
            {
                "secret": secret,
                "otp_uri": otp_uri,
                "qr_code_url": f"data:image/png;base64,{qr_code_base64}",
                "message": "Scan the QR code with your authenticator app, then verify with the code to complete setup.",
            },
            status=status.HTTP_200_OK,
        )


class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerifyMFASerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        logger.info("User %s verified MFA code.", request.user.email)
        return Response(result, status=status.HTTP_200_OK)


class DisableMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DisableMFASerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        logger.info("User %s disabled MFA.", request.user.email)
        return Response(result, status=status.HTTP_200_OK)


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.get_full_name(),
            "role": user.role,
            "tenant_id": str(user.tenant_id) if user.tenant else None,
            "is_active": user.is_active,
            "mfa_enabled": user.mfa_enabled,
            "force_password_change": user.force_password_change,
            "email_verified": user.email_verified,
            "phone_verified": user.phone_verified,
            "phone_number": user.phone_number,
            "date_joined": user.date_joined.isoformat() if user.date_joined else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        if user.tenant:
            data["tenant"] = {
                "id": str(user.tenant.id),
                "name": user.tenant.name,
                "code": user.tenant.code,
                "slug": user.tenant.slug,
            }
        else:
            data["tenant"] = None
        return Response(data, status=status.HTTP_200_OK)


class SessionListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sessions = AuthService.get_user_sessions(request.user)
        data = []
        for session in sessions:
            data.append(
                {
                    "id": str(session.id),
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "device_info": session.device_info,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "is_active": session.is_active,
                }
            )
        return Response({"sessions": data}, status=status.HTTP_200_OK)


class SessionDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, session_id):
        AuthService.delete_session(request.user, session_id)
        return Response(
            {"message": "Session has been deactivated successfully."},
            status=status.HTTP_200_OK,
        )
