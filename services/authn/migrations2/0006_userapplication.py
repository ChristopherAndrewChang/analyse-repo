# Generated by Django 4.2.14 on 2024-10-17 16:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0005_application_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('last_accessed', models.DateTimeField(blank=True, null=True, verbose_name='last accessed')),
                ('application', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allowed_users', to=settings.OAUTH2_PROVIDER_APPLICATION_MODEL, verbose_name='application')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='allowed_applications', to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'unique_together': {('user', 'application')},
            },
        ),
    ]
