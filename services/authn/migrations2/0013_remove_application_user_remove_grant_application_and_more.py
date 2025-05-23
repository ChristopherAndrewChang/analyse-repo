# Generated by Django 4.2.16 on 2024-11-08 08:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authn', '0012_platform_salt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='application',
            name='user',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='application',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='user',
        ),
        migrations.RemoveField(
            model_name='idtoken',
            name='application',
        ),
        migrations.RemoveField(
            model_name='idtoken',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='refreshtoken',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='refreshtoken',
            name='access_token',
        ),
        migrations.RemoveField(
            model_name='refreshtoken',
            name='application',
        ),
        migrations.RemoveField(
            model_name='refreshtoken',
            name='user',
        ),
        migrations.AlterUniqueTogether(
            name='userapplication',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='userapplication',
            name='application',
        ),
        migrations.RemoveField(
            model_name='userapplication',
            name='user',
        ),
        migrations.DeleteModel(
            name='AccessToken',
        ),
        migrations.DeleteModel(
            name='Application',
        ),
        migrations.DeleteModel(
            name='Grant',
        ),
        migrations.DeleteModel(
            name='IDToken',
        ),
        migrations.DeleteModel(
            name='RefreshToken',
        ),
        migrations.DeleteModel(
            name='UserApplication',
        ),
    ]
