# Generated by Django 4.2.18 on 2025-02-17 01:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('oauth', '0006_application_prompt_callback_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='PromptRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('user_id', models.PositiveBigIntegerField(verbose_name='user id')),
                ('expires', models.DateTimeField(blank=True, null=True, verbose_name='expires')),
                ('answer', models.TextField(blank=True, choices=[('accepted', 'accepted'), ('reject', 'rejected')], max_length=32, null=True, verbose_name='answer')),
                ('answer_time', models.DateTimeField(blank=True, null=True, verbose_name='answer time')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
