# Generated by Django 4.2.16 on 2025-01-24 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0006_remove_platform_platform_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='last_login_ip_address',
            field=models.GenericIPAddressField(blank=True, help_text='Last login ip to this device.', null=True, verbose_name='last login ip address'),
        ),
    ]
