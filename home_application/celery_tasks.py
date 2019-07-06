# -*- coding: utf-8 -*-
"""
celery 任务示例

本地启动celery命令: python  manage.py  celery  worker  --settings=settings
周期性任务还需要启动celery调度命令：python  manage.py  celerybeat --settings=settings
"""
import datetime

from celery.schedules import crontab
from celery.task import periodic_task
from celery import task
# @periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
# def performance():
#     execute_job()
from blueking.component.shortcuts import get_client_by_user
from common.log import logger
from home_application.api_manager import JobApiManager
from home_application.models import MonitorData, MonitorItem


@task()
def async_task(x, y):
    """
    定义一个 celery 异步任务
    """
    logger.error(u"celery 定时任务执行成功，执行结果：{:0>2}:{:0>2}".format(x, y))
    return x + y


def execute_task():
    """
    执行 celery 异步任务

    调用celery任务方法:
        task.delay(arg1, arg2, kwarg1='x', kwarg2='y')
        task.apply_async(args=[arg1, arg2], kwargs={'kwarg1': 'x', 'kwarg2': 'y'})
        delay(): 简便方法，类似调用普通函数
        apply_async(): 设置celery的额外执行选项时必须使用该方法，如定时（eta）等
                      详见 ：http://celery.readthedocs.org/en/latest/userguide/calling.html
    """
    now = datetime.datetime.now()
    logger.error(u"celery 定时任务启动，将在60s后执行，当前时间：{}".format(now))
    # 调用定时任务
    async_task.apply_async(args=[now.hour, now.minute], eta=now + datetime.timedelta(seconds=60))


@periodic_task(run_every=crontab(minute='*/5', hour='*', day_of_week="*"))
def get_time():
    """
    celery 周期任务示例

    run_every=crontab(minute='*/5', hour='*', day_of_week="*")：每 5 分钟执行一次任务
    periodic_task：程序运行时自动触发周期任务
    """
    execute_task()
    now = datetime.datetime.now()
    logger.error(u"celery 周期任务调用成功，当前时间：{}".format(now))


@periodic_task(run_every=crontab(minute='*/1', hour='*', day_of_week="*"))
def monitor_process():
    client = get_client_by_user('admin')
    job_api = JobApiManager(client=client)
    all_items = MonitorItem.objects.all()
    script_content = '''MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
                                DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
                                CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
                                DATE=$(date "+%Y-%m-%d %H:%M:%S")
                                echo -e "$DATE|$MEMORY|$DISK|$CPU"'''
    biz_item_dict = {}
    monitor_id_dict = {}
    for item in all_items:
        ip_list = biz_item_dict.setdefault(item.bk_biz_id, [])
        ip_list.append({
            'ip': item.ip,
            'bk_cloud_id': item.bk_cloud_id,
        })
        host_key = '%s|%s' % (item.ip, item.bk_cloud_id)
        monitor_id_dict[host_key] = item.id

    for bk_biz_id, ip_list in biz_item_dict.items():
        job_param = {
            'bk_biz_id': bk_biz_id,
            'script_content': script_content,
            'ip_list': ip_list
        }
        res_log = job_api.execute_and_get_log(**job_param)
        for host_key, log in res_log.items():
            host = host_key.split('|')
            datas = log.split('|')
            MonitorData.objects.create(
                monitor_id=monitor_id_dict.get(host_key),
                mem=float(datas[1][:-1]),
                disk=float(datas[2][:-1]),
                cpu=float(datas[3][:-2])
            )
