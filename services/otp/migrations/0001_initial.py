# Generated by Django 4.2.14 on 2024-09-03 07:50

from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('code', models.CharField(editable=False, max_length=128, null=True, verbose_name='code')),
                ('expires', models.DateTimeField(verbose_name='expires')),
                ('confirmed', models.BooleanField(default=False, verbose_name='confirmed')),
                ('replied', models.BooleanField(default=False, verbose_name='replied')),
                ('key', models.BinaryField(verbose_name='private key')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Issuer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='RecipientType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Usage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='name')),
            ],
        ),
        migrations.CreateModel(
            name='Recipient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recipient', models.CharField(max_length=128)),
                ('tp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='otp.recipienttype', verbose_name='type')),
            ],
            options={
                'unique_together': {('tp', 'recipient')},
            },
        ),
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=128, verbose_name='tag')),
                ('description', models.TextField(verbose_name='description')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='otp.code', verbose_name='code')),
            ],
        ),
        migrations.AddField(
            model_name='code',
            name='issuer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='otp.issuer', verbose_name='issuer'),
        ),
        migrations.AddField(
            model_name='code',
            name='recipient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='otp.recipient', verbose_name='recipient'),
        ),
        migrations.AddField(
            model_name='code',
            name='usage',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='otp.usage', verbose_name='usage'),
        ),
    ]
