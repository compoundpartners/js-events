# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-10-25 11:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0027_auto_20191024_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='speaker',
            name='link_text',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='link text'),
        ),
        migrations.AddField(
            model_name='speaker',
            name='open_in_new_window',
            field=models.BooleanField(default=False, verbose_name='Open link in new window'),
        ),
    ]
