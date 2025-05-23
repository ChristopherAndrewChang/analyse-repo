# Generated by Django 4.2.16 on 2025-01-28 06:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0008_rename_last_login_ip_address_device_last_login_ip'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='revoked',
            field=models.BooleanField(default=False, verbose_name='revoke flag'),
        ),
        migrations.AddField(
            model_name='device',
            name='revoked_at',
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name='revoke at'),
        ),
        migrations.AlterField(
            model_name='device',
            name='registered_at',
            field=models.DateTimeField(auto_now_add=True, help_text='Registered date for the first time.', verbose_name='registered at'),
        ),
    ]
