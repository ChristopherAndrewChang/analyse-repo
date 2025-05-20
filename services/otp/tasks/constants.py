from idvalid_integration.tasks import constants


EXCHANGE = constants.EXCHANGE_OTP

QUEUE_EXTERNAL = "idvalid.otp.external"
ROUTING_EXTERNAL = constants.ROUTING_OTP_EXTERNAL
TASK_EXTERNAL_OTP_CREATE = constants.TASK_EXTERNAL_OTP_CREATE

QUEUE_SIGNAL = "idvalid.otp.signal"
ROUTING_SIGNAL = "otp.signal"
TASK_SIGNAL_CODE_POST_CREATE = "idvalid.otp.signal.code.post_create"
TASK_SIGNAL_OTP_POST_CREATE = "idvalid.otp.signal.otp.post_create"
TASK_SIGNAL_OTP_APPLY = "idvalid.otp.signal.otp.apply"
