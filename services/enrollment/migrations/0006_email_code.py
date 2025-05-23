# Generated by Django 4.2.14 on 2024-10-04 05:27

from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('enrollment', '0005_alter_otp_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
                ('resend_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='resend_date')),
                ('is_registered', models.BooleanField(default=False, editable=False, verbose_name='registered flag')),
                ('registered_date', models.DateTimeField(blank=True, editable=False, null=True, verbose_name='registered')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('device_id', models.CharField(max_length=64, verbose_name='device id')),
                ('state', models.CharField(max_length=128, verbose_name='state')),
                ('user_agent', models.CharField(max_length=512, verbose_name='user agent')),
                ('expires', models.DateTimeField(verbose_name='expired date')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('email', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_set', to='enrollment.email', verbose_name='email')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
