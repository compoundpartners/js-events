# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-09 23:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('js_events', '0018_event_link_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='nofollow',
            field=models.BooleanField(default=False, verbose_name='nofollow'),
        ),
        migrations.AddField(
            model_name='event',
            name='noindex',
            field=models.BooleanField(default=False, verbose_name='noindex'),
        ),
        migrations.AddField(
            model_name='event',
            name='show_on_sitemap',
            field=models.BooleanField(default=True, verbose_name='Show on sitemap'),
        ),
        migrations.AddField(
            model_name='event',
            name='show_on_xml_sitemap',
            field=models.BooleanField(default=True, verbose_name='Show on xml sitemap'),
        ),
    ]
