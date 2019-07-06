# -*- coding: utf-8 -*-
import base64
import json
import os

from django.conf import settings
from django.http import StreamingHttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from account.decorators import login_exempt
from common.mymako import render_mako_context
from blueking.component.shortcuts import get_client_by_request
from home_application.api_manager import JobApiManager, CCApiManager
from home_application.celery_tasks import my_test
from home_application.models import MonitorItem
from home_application.resource import Chart, TopoTreeHandle, get_search_dict
from home_application.utils import now_time, now_time_str, time_operation
from utilities.response import *
from conf.default import APP_ID, APP_TOKEN
from utilities.error import try_exception


def api_test(request):
    # celery
    # my_test.apply_async(args=['HEIHA'], eta=time_operation(now_time(), seconds=10))
    cc_api = CCApiManager(request)
    bizs = cc_api.search_business()
    res = cc_api.search_biz_inst_topo({'bk_biz_id': 3})
    params = {
        "condition": [
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": []
            }, {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "object",
                "fields": [],
                "condition": [
                    {
                        "field": "bk_inst_id",
                        "operator": "$eq",
                        "value": 162
                    }
                ]
            }
        ]
    }
    host_res = cc_api.search_host(params)
    for host in host_res['info']:
        if host['module']:
            i = 1
    # cc_api = CCApiManager(request)
    # res = cc_api.search_module({
    #     "bk_biz_id": 2,
    #     "fields": [
    #     ],
    #     "condition": {
    #         "bk_module_id": "13"
    #     },
    #     "page": {
    #         "start": 0,
    #         "limit": 10
    #     }})
    return success_result()


def aget_list_host(request):
    cc_api = CCApiManager(request)
    params = {
        "ip": {
            "data": request.GET.get('ips', '').split(';'),
            "exact": 1,
            "flag": "bk_host_innerip|bk_host_outerip"
        },
        "bk_biz_id": int(request.GET.get('bk_biz_id')),
        "condition": [
            {
                "bk_obj_id": "host",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "module",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "set",
                "fields": [],
                "condition": []
            },
            {
                "bk_obj_id": "biz",
                "fields": [],
                "condition": [
                ]
            },
        ]
    }
    host_result = cc_api.search_host(params)
    monitor_items = MonitorItem.objects.filter(bk_biz_id=int(request.GET['bk_biz_id']))
    res_data = []
    monitor_ips = [item.ip for item in monitor_items]
    for host in host_result['info']:
        res_data.append({
            'inner_ip': host['host']['bk_host_innerip'],
            'os_name': host['host']['bk_os_name'],
            'host_name': host['host']['bk_host_name'],
            'bk_cloud': host['host']['bk_cloud_id'][0]['bk_inst_name'],
            'bk_cloud_id': host['host']['bk_cloud_id'][0]['id'],
            'bk_biz_id': int(request.GET.get('bk_biz_id')),
            'is_monitor': host['host']['bk_host_innerip'] in monitor_ips,
            'mem': '--',
            'cpu': '--',
            'disk': '--',
        })

    return success_result(res_data)


def apost_show_usage(request):
    param = json.loads(request.body)
    job_api = JobApiManager(request)
    script_content = '''MEMORY=$(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
                            DISK=$(df -h | awk '$NF=="/"{printf "%s", $5}')
                            CPU=$(top -bn1 | grep load | awk '{printf "%.2f%%", $(NF-2)}')
                            DATE=$(date "+%Y-%m-%d %H:%M:%S")
                            echo -e "$DATE|$MEMORY|$DISK|$CPU"'''
    job_param = {
        'bk_biz_id': param['bk_biz_id'],
        'script_content': script_content,
        'ip_list': [
            {
                'ip': param['inner_ip'],
                'bk_cloud_id': param['bk_cloud_id']
            }
        ]
    }
    job_log = job_api.execute_and_get_log(**job_param)
    host_key = '%s|%s' % (param['inner_ip'], param['bk_cloud_id'])
    datas = job_log[host_key].split('|')
    result_data = {
        'mem': datas[1],
        'disk': datas[2],
        'cpu': datas[3],
    }
    return success_result(result_data)


def apost_add_monitor(request):
    param = json.loads(request.body)
    MonitorItem.objects.create(
        bk_biz_id=param['bk_biz_id'],
        bk_cloud_id=param['bk_cloud_id'],
        ip=param['inner_ip']
    )
    return success_result()


def apost_remove_monitor(request):
    param = json.loads(request.body)
    MonitorItem.objects.filter(
        bk_biz_id=param['bk_biz_id'],
        bk_cloud_id=param['bk_cloud_id'],
        ip=param['inner_ip']
    ).delete()
    return success_result()
