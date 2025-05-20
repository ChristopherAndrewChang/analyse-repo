from django.urls import path, include
# from .views import (
#     SummaryView,
#     AuthenticatorView,
#     ConfirmTOTPView,
#     SecurityCodeView,
# )
from .authenticator import urls as authenticator_urls
from .backup_code import urls as backup_code_urls
# from .email_otp import urls as email_otp_urls
from .passkey import urls as passkey_urls
from .security_code import urls as security_code_urls
# from .summary import urls as summary_urls


app_name = "security"


urlpatterns = [
    path('authenticator/', include(authenticator_urls)),
    path('backup-code/', include(backup_code_urls)),
    # path('email/', include(email_otp_urls)),
    path('passkey/', include(passkey_urls)),
    path('security-code/', include(security_code_urls)),
    # path('summary/', include(summary_urls)),
]
