from idvalid_integration.tasks import constants


OTP_USAGE = "email-enrollment"


EXCHANGE_PUBLISHER = constants.EXCHANGE_PUBLISHER

QUEUE_CONSUME = "enrollment.consume"
ROUTING_CONSUME_OTP_PUBLISH = (
    f"{constants.ROUTING_OTP_PUBLISH_PREFIX}.{OTP_USAGE}")
TASK_CONSUME_OTP_PUBLISH = constants.TASK_CONSUME_OTP_PUBLISH
# ROUTING_CONSUME_OTP_APPLY = (
#     f"{constants.ROUTING_OTP_APPLY_PREFIX}.{OTP_USAGE}")
# TASK_CONSUME_OTP_APPLY = constants.TASK_CONSUME_OTP_APPLY


EXCHANGE = constants.EXCHANGE_ENROLLMENT

QUEUE_SIGNAL = "enrollment.signal"
ROUTING_SIGNAL = "enrollment.signal"
TASK_SIGNAL_EMAIL_POST_CREATE = "idvalid.enrollment.signal.email.post_create"
TASK_SIGNAL_CODE_POST_CREATE = "idvalid.enrollment.signal.code.post_create"
TASK_SIGNAL_CODE_POST_APPLY = "idvalid.enrollment.signal.code.post_apply"
