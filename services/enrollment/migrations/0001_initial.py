# Generated by Django 4.2.14 on 2024-08-22 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('last_otp_expiration', models.DateTimeField(verbose_name='last otp expiration date')),
                ('is_registered', models.BooleanField(default=False)),
                ('registered_date', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
