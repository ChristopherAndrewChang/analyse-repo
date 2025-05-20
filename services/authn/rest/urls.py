from django.urls import path, include
from .auth import urls as auth_urls
from .enrollment import urls as enrollment_urls
from .forget_password import urls as forget_password_urls
from .mobile_otp import urls as mobile_otp_urls
from .multi_factors import urls as multi_factors_urls
from .security import urls as security_urls
from .tenant import urls as tenant_urls
# from .two_fa import urls as two_fa_urls
from .user import urls as user_urls


app_name = "authn"


urlpatterns = [
    path('enrollment/', include(enrollment_urls)),
    path('forget-password/', include(forget_password_urls)),
    path('mobile-otp/', include(mobile_otp_urls)),
    path('multi-factors/', include(multi_factors_urls)),
    path('security/', include(security_urls)),
    path('tenant/', include(tenant_urls)),
    path('user/', include(user_urls)),
    # path('2fa/', include(two_fa_urls)),
    path('', include(auth_urls)),
]


