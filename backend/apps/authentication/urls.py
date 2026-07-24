from django.urls import path

from . import views

app_name = "authentication"

urlpatterns = [
    path("login/", views.CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("token/refresh/", views.RefreshTokenView.as_view(), name="token_refresh"),
    path("change-password/", views.ChangePasswordView.as_view(), name="change_password"),
    path("password-reset/", views.ResetPasswordView.as_view(), name="password_reset"),
    path("password-reset/confirm/", views.ResetPasswordConfirmView.as_view(), name="password_reset_confirm"),
    path("mfa/enable/", views.EnableMFAView.as_view(), name="mfa_enable"),
    path("mfa/verify/", views.VerifyMFAView.as_view(), name="mfa_verify"),
    path("mfa/disable/", views.DisableMFAView.as_view(), name="mfa_disable"),
    path("me/", views.CurrentUserView.as_view(), name="current_user"),
    path("sessions/", views.SessionListView.as_view(), name="session_list"),
    path("sessions/<uuid:session_id>/", views.SessionDeleteView.as_view(), name="session_delete"),
]
