from __future__ import annotations
from typing import TYPE_CHECKING

from esl_core.generators import subid_generator

if TYPE_CHECKING:
    from .models import Sender


def cert_file_path(instance: Sender, filename: str) -> str:
    return f"mailer/sender/{subid_generator()}c"


def key_file_path(instance: Sender, filename: str) -> str:
    return f"mailer/sender/{subid_generator()}k"


def queue_attachment_file_path(instance, filename: str) -> str:
    return f"mailer/queue/{subid_generator()}"
