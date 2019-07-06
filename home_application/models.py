# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models

from home_application.utils import datetime_to_str


class BaseOperateModel(models.Model):

    create_name = models.CharField(max_length=20)
    update_name = models.CharField(max_length=20)
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    def to_dic(self):
        result_dict = {}
        for f in self._meta.fields:
            f_val = getattr(self, f.name, None)
            if isinstance(f_val, datetime):
                f_val = datetime_to_str(f_val)

            result_dict[f.name] = f_val

        return result_dict

    class Meta:
        abstract = True


class Tmp(BaseOperateModel):
    TCHOICES = (
        ('1', '一'),
        ('2', '二'),
        ('3', '三'),
        ('4', '四'),
    )

    tchar = models.CharField(max_length=20, choices=TCHOICES)
    ttext = models.TextField()
    tint = models.IntegerField()
    tdate = models.DateField()
    tbinary = models.BinaryField()

    class Meta:
        abstract = True


class MonitorItem(BaseOperateModel):
    ip = models.CharField(max_length=20)
    bk_cloud_id = models.IntegerField(max_length=50)
    bk_biz_id = models.IntegerField()


class MonitorData(BaseOperateModel):
    monitor_id = models.IntegerField()
    mem = models.FloatField()
    disk = models.FloatField()
    cpu = models.FloatField()