# -*- coding: utf-8 -*-
from django.conf.urls import patterns

from home_application import views

urls = [
    (r'^$', 'home'),
    (r'^demo/$', 'demo'),
    (r'^curd/$', 'curd'),
    (r'^form/$', 'form'),
    (r'^host_status/$', 'host_status'),
    (r'^chart/$', 'chart'),
    (r'^api_test$', 'api_test'),
    (r'^api/test/', 'test'),
    (r'^cc/search_business$', 'search_business'),
]

auto_urls = []
for view, view_obj in views.__dict__.items():
    if not callable(view_obj):
        continue

    view_name_split = view.split('_')
    if len(view_name_split) > 1:
        view_name = "_".join(view_name_split[1:])
        if view_name_split[0] == 'aget':
            url_str = r'^%s$' % (view_name + r"/")
        elif view_name_split[0] == 'apost':
            url_str = r'^%s$' % view_name
        else:
            continue

        auto_urls.append((url_str, view))

all_urls = urls + auto_urls
urlpatterns = patterns('home_application.views', *all_urls)
