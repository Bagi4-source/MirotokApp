# Generated by Django 4.2.1 on 2023-06-03 22:18

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Codes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None, unique=True)),
                ('code', models.CharField(max_length=8, verbose_name='Code')),
            ],
            options={
                'verbose_name': 'Code',
                'verbose_name_plural': 'Codes',
            },
        ),
        migrations.CreateModel(
            name='Tariffs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('days', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Duration (days)')),
                ('title', models.CharField(max_length=128, verbose_name='Title')),
                ('description', models.CharField(blank=True, max_length=512, null=True, verbose_name='Description')),
                ('price', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Price')),
                ('currency', models.CharField(max_length=6, verbose_name='Currency')),
            ],
            options={
                'verbose_name': 'Tariff',
                'verbose_name_plural': 'Tariffs',
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('number', models.CharField(max_length=30, unique=True, verbose_name='Phone')),
                ('subscription_end', models.DateField(default=datetime.date.today, verbose_name='Дата окончания подписки')),
                ('role', models.IntegerField(choices=[(1, 'Admin'), (0, 'Client')], default=0, verbose_name='Role')),
            ],
            options={
                'verbose_name': 'Login',
                'verbose_name_plural': 'Logins',
            },
        ),
        migrations.CreateModel(
            name='UserInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('surname', models.CharField(max_length=100, verbose_name='Surname')),
                ('height', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Height')),
                ('weight', models.FloatField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Weight')),
                ('age', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Age')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.users', verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Info',
                'verbose_name_plural': 'User Info',
            },
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('token', models.CharField(max_length=64, unique=True, verbose_name='Token')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.users', verbose_name='User')),
            ],
            options={
                'verbose_name': 'Token',
                'verbose_name_plural': 'Tokens',
            },
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('percent', models.IntegerField(validators=[django.core.validators.MinValueValidator(-76), django.core.validators.MaxValueValidator(152)], verbose_name='Result percent')),
                ('result', models.JSONField(blank=True, null=True, verbose_name='Result info')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.users', verbose_name='User')),
            ],
            options={
                'verbose_name': 'Result',
                'verbose_name_plural': 'Results',
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('text', models.CharField(max_length=1000, verbose_name='Text')),
                ('private', models.BooleanField(default=False, verbose_name='Private')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.users', verbose_name='User ID')),
            ],
            options={
                'verbose_name': 'Message',
                'verbose_name_plural': 'Messages',
            },
        ),
        migrations.CreateModel(
            name='FBids',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('fBid', models.CharField(max_length=512, unique=True, verbose_name='FBid')),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.token', verbose_name='Token')),
            ],
            options={
                'verbose_name': 'FBid',
                'verbose_name_plural': 'FBids',
            },
        ),
        migrations.CreateModel(
            name='Diary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('text', models.CharField(max_length=1000, verbose_name='Text')),
                ('type', models.IntegerField(choices=[(0, 'Здоровье'), (1, 'Финансы'), (2, 'Личностный рост'), (3, 'Семья')], verbose_name='Type')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='API.users', verbose_name='User ID')),
            ],
            options={
                'verbose_name': 'Diary',
                'verbose_name_plural': 'Diaries',
            },
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Update time')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creation time')),
                ('amount', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Amount')),
                ('status', models.BooleanField(default=False, verbose_name='Status')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.tariffs', verbose_name='Product')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='API.users', verbose_name='User ID')),
            ],
            options={
                'verbose_name': 'Bill',
                'verbose_name_plural': 'Bills',
            },
        ),
    ]