# Generated by Django 4.2.16 on 2024-12-19 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0002_alter_device_last_login'),
    ]

    operations = [
        migrations.AlterField(
            model_name='devicehistory',
            name='last_login',
            field=models.DateTimeField(blank=True, help_text='Last login date to this device.', null=True, verbose_name='last login'),
        ),
    ]
