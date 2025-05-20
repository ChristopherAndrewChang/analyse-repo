from django.contrib import admin

from mailer.models import (
    Sender,
    DeveloperEmail,
    Template,
    MessageTemplate,
    MessageQueue,
    QueueAlternative,
    QueueAttachment)
# Register your models here.


@admin.register(Sender)
class SenderAdmin(admin.ModelAdmin):
    list_display = ('code', "username")
    search_fields = ("code", "username")


@admin.register(DeveloperEmail)
class DeveloperEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active")
    search_fields = ("email",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("code", "is_active")
    search_fields = ("code",)


@admin.register(MessageTemplate)
class MessageTemplateAdmin(admin.ModelAdmin):
    list_display = ("pk", "code", "sender", "body_template", "to")
    list_select_related = ("sender", "body_template")
    list_filter = ("sender",)
    search_fields = ("code",)
    autocomplete_fields = ("sender", "body_template", "alternatives")


class QueueAlternativeInline(admin.TabularInline):
    model = QueueAlternative
    extra = 0


class QueueAttachmentInline(admin.TabularInline):
    model = QueueAttachment
    extra = 0


@admin.register(MessageQueue)
class MessageQueueAdmin(admin.ModelAdmin):
    radio_fields = {"sender": admin.VERTICAL}
    ordering = ("-created", )

    list_display = ("pk", "subject", "sender", "to", "cc")
    list_filter = ("sender", "body_template")
    list_select_related = ("sender",)
    list_per_page = 25
    autocomplete_fields = ("body_template", )

    search_fields = (
        "subject",
        "sender__username", "sender__code",
        "body_template__code", "body_template__mimetype",
        "from_email", "to", "cc", "bcc", "reply_to")

    date_hierarchy = "created"

    inlines = [QueueAlternativeInline, QueueAttachmentInline]
