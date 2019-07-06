# -*- coding: utf-8 -*-
import base64
import time

from blueking.component.client import BaseComponentClient
from blueking.component.shortcuts import get_client_by_request


def api_exception(func):
    def wrapper(*args, **kwargs):
        res = func(*args, **kwargs)
        if res['result']:
            return res['data']

        raise ApiException(res['message'])

    return wrapper


class ApiManager(object):
    module = ''

    def __init__(self, request=None, client=None):
        if client:
            self.client = client
        else:
            self.client = get_client_by_request(request)

        if self.module:
            self.module_client = getattr(self.client, self.module, None)
        else:
            self.module_client = None

    def __getattr__(self, item):
        if self.module_client:
            func = getattr(self.module_client, item)
            return api_exception(func)


class CCApiManager(ApiManager):
    module = 'cc'

    def get_hosts_by_biz(self, bk_biz_ids):
        if isinstance(bk_biz_ids, int):
            bk_biz_ids = [bk_biz_ids]

        params = {
            "condition": [
                {
                    "bk_obj_id": "host",
                    "fields": [],
                    "condition": []
                }, {
                    "bk_obj_id": "biz",
                    "fields": [],
                    "condition": [
                        {
                            "field": "bk_biz_id",
                            "operator": "$in",
                            "value": bk_biz_ids
                        }
                    ]
                },
            ]
        }
        return self.search_host(params)

    def get_hosts_by_inst(self, bk_obj_id, bk_inst_id):
        params = {
            "condition": [
                {
                    "bk_obj_id": "host",
                    "fields": [],
                    "condition": []
                }, {
                    "bk_obj_id": "biz",
                    "fields": [],
                    "condition": [
                        {
                            "field": "bk_inst_id",
                            "operator": "$eq",
                            "value": ''
                        }
                    ]
                },
            ]
        }
        return ''


class JobApiManager(ApiManager):
    module = 'job'

    def execute_script(self, bk_biz_id, script_content, ip_list):
        params = {
            "bk_biz_id": bk_biz_id,
            "script_content": base64.b64encode(script_content),
            "account": "root",
            "is_param_sensitive": 0,
            "script_type": 1,
            "ip_list": ip_list,
        }
        res = self.fast_execute_script(params)
        return res

    def get_instance_log(self, bk_biz_id, instance_id):
        params = {
            'bk_biz_id': bk_biz_id,
            'job_instance_id': instance_id
        }
        res = self.get_job_instance_log(params)
        if res[0]['is_finished']:
            step_result = res[0]['step_results'][0]
            if step_result['ip_status'] == 9:
                report = {}
                for log in step_result['ip_logs']:
                    key = '%s|%s' % (log['ip'], log['bk_cloud_id'])
                    value = log['log_content']
                    report[key] = value

                return True, report
            else:
                raise ApiException('脚本执行不成功')
        else:
            return False, {}

    def execute_and_get_log(self, bk_biz_id, script_content, ip_list):
        instance_id = self.execute_script(bk_biz_id, script_content, ip_list)['job_instance_id']
        is_finished = False
        res = {}
        i = 0
        while i < 3 and not is_finished:
            is_finished, res = self.get_instance_log(bk_biz_id, instance_id)
            i += 1
            time.sleep(2)

        return res


class ApiException(Exception):
    def __init__(self, message=''):
        super(ApiException, self).__init__(message)
        self.message = 'Api Exception:%s' % message

    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message
