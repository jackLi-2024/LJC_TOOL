#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""

import os
import sys
import json
import base64
import requests
import random
from urllib.parse import urlencode
from requests_toolbelt.multipart.encoder import MultipartEncoder


class Request():
    def POST_json(self, url, **kwargs):
        try:
            return requests.post(url=url, **kwargs).json()
        except Exception as e:
            raise Exception(f"请求失败 [POST]--> {url}")

    def GET_json(self, url, **kwargs):
        try:
            return requests.get(url=url, **kwargs).json()
        except Exception as e:
            raise Exception(f"请求失败 [GET]--> {url}")

    def POST_str(self, url, **kwargs):
        try:
            return requests.post(url=url, **kwargs).text
        except Exception as e:
            raise Exception(f"请求失败 [POST]--> {url}")

    def GET_str(self, url, **kwargs):
        try:
            return requests.get(url=url, **kwargs).text
        except Exception as e:
            raise Exception(f"请求失败 [GET]--> {url}")

    def DELETE_str(self, url, **kwargs):
        try:
            return requests.delete(url=url, **kwargs).text
        except Exception as e:
            raise Exception(f"请求失败 [DELETE]--> {url}")


class Activiti(Request):
    username = "kermit"
    password = "kermit"
    service_url = "https://cq-platform.pand-iot.com/activiti-rest/service"

    @property
    def login(self):
        encode_data = f"{self.username}:{self.password}"
        basic_auth = "Basic {}".format(base64.standard_b64encode(encode_data.encode("utf8")).decode("utf8"))
        return {"Authorization": basic_auth}

    @property
    def headers(self):
        headers = {"Content-Type": "application/json"}
        dic = self.login
        dic.update(headers)
        return dic

    #### 部署
    def deployment_upload(self, filename):
        """
        上传部署pbmn文件
        http://shouce.jb51.net/activiti/#N13350
        """
        url = self.service_url + "repository/deployments"
        multipart_encoder = MultipartEncoder(
            fields={
                'save_name': filename,
                'save_data': (filename, open(filename, 'rb'), 'application/octet-stream')
            },
            boundary='-----------------------------' + str(random.randint(1e28, 1e29 - 1))
        )
        headers = self.headers
        headers["Content-Type"] = multipart_encoder.content_type
        return self.POST_json(url=url, data=multipart_encoder, headers=headers)

    def deployments_search(self, name=None, nameLike=None,
                           category=None, categoryNotEquals=None,
                           tenantId=None, tenantIdLike=None,
                           withoutTenantId=None, sort="id",
                           order="asc", start=0, size=10):
        """
        查询部署列表
        http://shouce.jb51.net/activiti/#N1326F
        """
        param = self.join_params(name=name, nameLike=nameLike,
                                 category=category, categoryNotEquals=categoryNotEquals,
                                 tenantId=tenantId, tenantIdLike=tenantIdLike,
                                 withoutTenantId=withoutTenantId, sort=sort,
                                 order=order, start=start, size=size)
        url = self.service_url + f"/repository/deployments?" + param
        return self.GET_json(url=url, headers=self.headers)

    def deployment_search(self, deploymentId):
        """
        查询某一个部署
        http://shouce.jb51.net/activiti/#N1330A
        """
        url = self.service_url + f"/repository/deployments/{deploymentId}"
        return self.GET_json(url=url, headers=self.headers)

    def deployment_delete(self, deploymentId):
        """
        删除一个部署
        http://shouce.jb51.net/activiti/#N13390
        :return:
        """
        url = self.service_url + f"/repository/deployments/{deploymentId}"
        return self.DELETE_str(url=url, headers=self.headers)

    #### 流程




    def join_params(self, **kwargs):
        s = {}
        for k, v in kwargs.items():
            if v == None:
                continue
            s[k] = v
        return urlencode(s)


if __name__ == '__main__':
    ac = Activiti()
    print(ac.deployments_search(name="Demo processes"))
