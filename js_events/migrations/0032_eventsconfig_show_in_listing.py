# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-12-13 11:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0031_auto_20191202_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsconfig',
            name='show_in_listing',
            field=models.BooleanField(default=True, help_text='Include articles in listing pages and admin selects?', verbose_name='Include in Listings?'),
        ),
    ]