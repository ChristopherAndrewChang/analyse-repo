# Generated by Django 4.2.18 on 2025-05-07 08:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0057_usermfa_mobile_logged_in_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='platform',
            name='platform_type',
            field=models.CharField(choices=[('mobile', 'Mobile'), ('desktop', 'Desktop'), ('web', 'Web'), ('other', 'Other')], default='web', max_length=32, verbose_name='platform type'),
        ),
    ]
