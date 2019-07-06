# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MonitorData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_name', models.CharField(max_length=20)),
                ('update_name', models.CharField(max_length=20)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('monitor_id', models.IntegerField()),
                ('mem', models.FloatField()),
                ('disk', models.FloatField()),
                ('cpu', models.FloatField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MonitorItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_name', models.CharField(max_length=20)),
                ('update_name', models.CharField(max_length=20)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('ip', models.CharField(max_length=20)),
                ('bk_cloud', models.CharField(max_length=50)),
                ('bk_biz_id', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
