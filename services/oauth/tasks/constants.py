from idvalid_integration.tasks import constants


EXCHANGE = constants.EXCHANGE_OAUTH

QUEUE_SIGNAL = "idvalid.oauth.signal"
ROUTING_SIGNAL = "oauth.signal"
TASK_SIGNAL_PROMPT_REQUEST_POST_ANSWER = "idvalid.oauth.signal.prompt_request.post_answer"
