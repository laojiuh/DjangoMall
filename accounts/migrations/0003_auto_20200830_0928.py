# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-08-30 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20200828_0830'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='loginrecord',
            options={'verbose_name': '登录历史', 'verbose_name_plural': '登陆历史'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': '用户基础信息', 'verbose_name_plural': '用户基础信息'},
        ),
        migrations.AlterModelOptions(
            name='useraddress',
            options={'ordering': ['is_default', '-updated_at'], 'verbose_name': '用户地址', 'verbose_name_plural': '用户地址'},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'verbose_name': '用户详细信息', 'verbose_name_plural': '用户详细信息'},
        ),
        migrations.AlterField(
            model_name='useraddress',
            name='phone',
            field=models.CharField(max_length=32, verbose_name='收件人的电话'),
        ),
    ]
