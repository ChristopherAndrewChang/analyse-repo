# Generated by Django 4.2.14 on 2024-10-07 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0002_enrollment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='enrollment',
            name='enrollment_id',
        ),
        migrations.AddField(
            model_name='enrollment',
            name='device_id',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='device id'),
        ),
        migrations.AddField(
            model_name='enrollment',
            name='email_id',
            field=models.CharField(default=None, max_length=64, unique=True, verbose_name='email id'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='enrollment',
            name='state',
            field=models.CharField(blank=True, max_length=180, null=True, verbose_name='state'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='email'),
        ),
        migrations.AlterField(
            model_name='enrollment',
            name='is_registered',
            field=models.BooleanField(blank=True, null=True, verbose_name='registered flag'),
        ),
    ]
