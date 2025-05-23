# Generated by Django 4.2.16 on 2024-11-23 18:28

import authn.models.two_fa.totp
from django.db import migrations, models
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0016_user_phone'),
    ]

    operations = [
        migrations.CreateModel(
            name='TOTP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('secret', models.BinaryField(default=authn.models.two_fa.totp.generate_secret, max_length=40, verbose_name='secret')),
                ('algorithm', models.CharField(choices=[('sha1', 'SHA1'), ('sha256', 'SHA256'), ('sha512', 'SHA512')], default='sha1', max_length=16, verbose_name='algorithm')),
                ('digits', models.PositiveSmallIntegerField(choices=[(6, 6), (7, 7), (8, 8), (9, 9)], default=6, help_text='The number of digits to expect in a token.', verbose_name='digits')),
                ('period', models.PositiveSmallIntegerField(default=30, help_text='The token period in seconds.', verbose_name='period')),
                ('t0', models.BigIntegerField(default=0, help_text='The Unix time at which to begin counting steps.', verbose_name='t0')),
                ('tolerance', models.PositiveSmallIntegerField(default=1, help_text='The number of time steps in the past or future to allow.', verbose_name='tolerance')),
                ('drift', models.SmallIntegerField(default=0, help_text='The number of time steps the prover is known to deviate from our clock.', verbose_name='drift')),
                ('last_t', models.BigIntegerField(default=-1, help_text='The t value of the latest verified token. The next token must be at a higher time step.', verbose_name='last t')),
                ('failure_timestamp', models.DateTimeField(blank=True, help_text='A timestamp of the last failed verification attempt. Null if last attempt succeeded.', null=True)),
                ('failure_count', models.PositiveIntegerField(default=0, help_text='Number of successive failed attempts.')),
                ('last_used_at', models.DateTimeField(blank=True, help_text='The most recent date and time this device was used.', null=True, verbose_name='last used at')),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date and time when this device was initially created in the system.', verbose_name='created at')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
