# Generated by Django 4.2.18 on 2025-05-06 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0055_roleuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='is_mobile',
            field=models.BooleanField(default=False, verbose_name='mobile status'),
        ),
    ]
