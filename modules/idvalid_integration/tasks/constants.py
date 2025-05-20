# ############## #
# publish events #
# ############## #
EXCHANGE_PUBLISHER = "idvalid.publisher"

# > enrollment events
ROUTING_ENROLLMENT = "enrollment.enrollment"
TASK_CONSUME_ENROLLMENT_PUBLISH = "idvalid.enrollment.consume.enrollment.publish"

# > otp events
ROUTING_OTP_PUBLISH_PREFIX = "otp.otp.publish"
TASK_CONSUME_OTP_PUBLISH = "idvalid.otp.consume.otp.publish"

# > authn events
ROUTING_AUTH_PUBLISH_PREFIX = "auth.user.publish"
TASK_CONSUME_AUTH_USER_LOGGED_IN = "idvalid.auth.consume.user.logged_in"

ROUTING_AUTH_PLATFORM_PUBLISH_PREFIX = "auth.platform.publish"
TASK_CONSUME_AUTH_PLATFORM_CREATE = "idvalid.auth.consume.platform.create"
TASK_CONSUME_AUTH_PLATFORM_UPDATE = "idvalid.auth.consume.platform.update"
TASK_CONSUME_AUTH_PLATFORM_DELETE = "idvalid.auth.consume.platform.delete"

ROUTING_AUTH_SESSION_PUBLISH_PREFIX = "auth.session.publish"
TASK_CONSUME_AUTH_SESSION_CREATE = "idvalid.auth.consume.session.create"
TASK_CONSUME_AUTH_SESSION_DELETE = "idvalid.auth.consume.session.delete"

ROUTING_AUTH_ACCOUNT_PUBLISH_PREFIX = "auth.account.publish"
TASK_CONSUME_AUTH_ACCOUNT_CREATE = "idvalid.auth.consume.account.create"

ROUTING_AUTH_USER_PUBLISH_PREFIX = "auth.user.publish"
TASK_CONSUME_AUTH_USER_ACTIVE_FLAG = "idvalid.auth.consume.user.active_flag"

ROUTING_AUTH_PROFILE_PUBLISH_PREFIX = "auth.profile.publish"
TASK_CONSUME_AUTH_PROFILE_UPDATE = "idvalid.auth.consume.profile.update"

# > authn external
ROUTING_AUTH_EXTERNAL = "auth.external"
TASK_EXTERNAL_AUTH_SESSION_REVOKE = "idvalid.auth.external.session.revoke"

# > device events
ROUTING_DEVICE_PUBLISH_PREFIX = "device.device.publish"
TASK_CONSUME_DEVICE_DELETE = "idvalid.device.consume.device.delete"

# > tenant events
ROUTING_TENANT_PUBLISH_PREFIX = "tenant.tenant.publish"
TASK_CONSUME_TENANT_PUBLISH = "idvalid.tenant.consume.tenant.publish"

ROUTING_TENANT_USER_PUBLISH_PREFIX = "tenant.tenant_user.publish"
TASK_CONSUME_TENANT_USER_PUBLISH = "idvalid.tenant.consume.tenant_user.publish"
TASK_CONSUME_TENANT_USER_DELETE = "idvalid.tenant.consume.tenant_user.delete"

# > rbac events
ROUTING_RBAC_ROLE_USER_PUBLISH_PREFIX = "rbac.role-user.publish"
TASK_CONSUME_RBAC_ROLE_USER_CREATE = "idvalid.rbac.consume.role_user.create"
TASK_CONSUME_RBAC_ROLE_USER_DELETE = "idvalid.rbac.consume.role_user.delete"

# ROUTING_OTP_APPLY_PREFIX = "otp.otp.apply"
# TASK_CONSUME_OTP_APPLY = "idvalid.otp.consume.otp.apply"

# ############### #
# external events #
# ############### #
EXCHANGE_ACCOUNT = "idvalid.account"

EXCHANGE_ENROLLMENT = "idvalid.enrollment"
ROUTING_ENROLLMENT_EXTERNAL = "enrollment.external"

EXCHANGE_OTP = "idvalid.otp"
ROUTING_OTP_EXTERNAL = "otp.external"
TASK_EXTERNAL_OTP_CREATE = "idvalid.otp.external.otp.create"

EXCHANGE_AUTH = "idvalid.auth"
# ROUTING_PUBLISH_ENROLLMENT_CODE = "enrollment.code"


EXCHANGE_DEVICE = "idvalid.device"


EXCHANGE_OAUTH = "idvalid.oauth"


EXCHANGE_TENANT = "idvalid.tenant"


EXCHANGE_RBAC = "idvalid.rbac"
