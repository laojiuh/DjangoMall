# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2020-08-30 01:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_imagefile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagefile',
            options={'verbose_name': '图片表', 'verbose_name_plural': '图片表'},
        ),
        migrations.AlterModelOptions(
            name='news',
            options={'ordering': ['-reorder'], 'verbose_name': '新闻及通知', 'verbose_name_plural': '新闻及通知'},
        ),
        migrations.AlterModelOptions(
            name='slider',
            options={'ordering': ['-reorder'], 'verbose_name': '轮播图', 'verbose_name_plural': '轮播图'},
        ),
        migrations.AlterField(
            model_name='news',
            name='is_valid',
            field=models.BooleanField(default=True, verbose_name='是否有效'),
        ),
        migrations.AlterField(
            model_name='slider',
            name='is_valid',
            field=models.BooleanField(default=True, verbose_name='是否有效'),
        ),
    ]
