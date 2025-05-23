# Generated by Django 4.2.18 on 2025-04-29 14:04

from django.db import migrations, models
import idvalid_core.generators


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0009_roleuser_subid'),
    ]

    operations = [
        migrations.AddField(
            model_name='rolepolicy',
            name='subid',
            field=models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid'),
        ),
    ]
