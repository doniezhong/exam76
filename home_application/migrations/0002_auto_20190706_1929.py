# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home_application', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='monitoritem',
            name='bk_cloud',
        ),
        migrations.AddField(
            model_name='monitoritem',
            name='bk_cloud_id',
            field=models.IntegerField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]
