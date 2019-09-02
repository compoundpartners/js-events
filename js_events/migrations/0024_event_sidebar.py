# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-08-21 12:33
from __future__ import unicode_literals

import cms.models.fields
from django.db import migrations
import django.db.models.deletion
from django.apps import apps as django_apps


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0020_old_tree_cleanup'),
        ('js_events', '0023_eventtranslation_display_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='sidebar',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_event_sidebar', slotname='Event Sidebar', to='cms.Placeholder'),
        ),
    ]