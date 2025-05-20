from django.dispatch import Signal


# Don't user django.contrib.auth.signals.user_logged_in signal
# to avoid conflict with django admin login
user_logged_in = Signal()
user_logged_out = Signal()

session_revoke = Signal()

email_otp_post_challenge_create = Signal()

account_post_create = Signal()
user_post_active_flag_update = Signal()
