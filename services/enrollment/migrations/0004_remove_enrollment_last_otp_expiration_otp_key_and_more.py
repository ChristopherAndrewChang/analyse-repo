# Generated by Django 4.2.14 on 2024-09-13 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0003_otp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='last_otp_expiration',
        ),
        migrations.AddField(
            model_name='otp',
            name='key',
            field=models.BinaryField(default=None, verbose_name='key'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='last_otp_id',
            field=models.CharField(blank=True, editable=False, max_length=64, null=True, unique=True, verbose_name='last otp id'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='last_otp_sent',
            field=models.DateTimeField(blank=True, editable=False, null=True, verbose_name='last otp sent date'),
        ),
    ]
