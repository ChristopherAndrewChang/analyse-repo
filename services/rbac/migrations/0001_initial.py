# Generated by Django 4.2.18 on 2025-04-28 08:27

from django.db import migrations, models
import django.db.models.deletion
import idvalid_core.generators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('codename', models.CharField(max_length=64, unique=True, verbose_name='codename')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('codename', models.CharField(max_length=64, unique=True, verbose_name='codename')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='rbac.module', verbose_name='module')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Policy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('tenant_id', models.PositiveBigIntegerField(verbose_name='tenant_id')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active statue')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('codename', models.CharField(max_length=64, unique=True, verbose_name='codename')),
                ('name', models.CharField(max_length=128, verbose_name='name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='description')),
                ('is_active', models.BooleanField(default=True, verbose_name='active status')),
                ('created_time', models.DateTimeField(auto_now_add=True, verbose_name='created time')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subid', models.CharField(blank=True, db_column='subid', default=idvalid_core.generators.default_subid_generator, editable=False, help_text='Primary key shown to user.', max_length=64, null=True, unique=True, verbose_name='subid')),
                ('name', models.CharField(blank=True, max_length=256, null=True, verbose_name='name')),
                ('is_active', models.BooleanField(verbose_name='active flag')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='module',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='modules', to='rbac.service', verbose_name='service'),
        ),
        migrations.CreateModel(
            name='UserRole',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.role', verbose_name='role')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.user', verbose_name='user')),
            ],
            options={
                'unique_together': {('user', 'role')},
            },
        ),
        migrations.CreateModel(
            name='RolePolicy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.policy')),
                ('role', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.role', verbose_name='role')),
            ],
            options={
                'unique_together': {('role', 'policy')},
            },
        ),
        migrations.CreateModel(
            name='PolicyPermission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.permission', verbose_name='permission')),
                ('policy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rbac.policy', verbose_name='policy')),
            ],
            options={
                'unique_together': {('policy', 'permission')},
            },
        ),
    ]
