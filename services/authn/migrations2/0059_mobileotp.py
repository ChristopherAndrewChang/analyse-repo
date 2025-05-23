# Generated by Django 4.2.18 on 2025-05-08 02:02

import authn.models.two_fa.mobile
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0058_alter_platform_platform_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='MobileOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('pin', models.CharField(blank=True, max_length=128, null=True, verbose_name='pin')),
                ('valid_until', models.DateTimeField(default=authn.models.two_fa.mobile.generate_valid_time, help_text='The timestamp of the moment of expiry of the saved token.', verbose_name='valid until')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='created at')),
                ('user', models.ForeignKey(help_text='The user that this device belongs to.', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
