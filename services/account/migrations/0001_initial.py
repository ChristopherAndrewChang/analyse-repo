# Generated by Django 4.2.14 on 2024-09-24 07:38

import idvalid_core.validators
from django.db import migrations, models
import idvalid_core.generators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('enrollment_id', models.CharField(max_length=64, unique=True, verbose_name='enrollment id')),
                ('auth_id', models.CharField(max_length=64, unique=True, verbose_name='auth id')),
                ('profile_id', models.CharField(max_length=64, unique=True, verbose_name='profile id')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and ./_ only.', max_length=150, unique=True, validators=[
                    idvalid_core.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
