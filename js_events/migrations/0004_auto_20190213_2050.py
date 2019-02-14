# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-02-13 20:50
from __future__ import unicode_literals

import cms.models.fields
from django.db import migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0020_old_tree_cleanup'),
        ('js_events', '0003_eventrelatedplugin'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='registration_content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_event_registration_content', slotname='Hide After Happened', to='cms.Placeholder'),
        ),
        migrations.AlterField(
            model_name='event',
            name='content',
            field=cms.models.fields.PlaceholderField(editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='events_event_content', slotname='Event Content', to='cms.Placeholder'),
        ),
    ]
