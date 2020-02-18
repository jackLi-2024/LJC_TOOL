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

    def DELETE_status(self, url, **kwargs):
        try:
            return requests.delete(url=url, **kwargs).status_code
        except Exception as e:
            raise Exception(f"请求失败 [DELETE]--> {url}")


class Activiti(Request):
    username = "kermit"
    password = "kermit"
    service_url = "https://cq-platform.pand-iot.com/activiti-rest/service/"

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
        url = self.service_url + f"repository/deployments?" + param
        return self.GET_json(url=url, headers=self.headers)

    def deployment_search(self, deploymentId):
        """
        查询某一个部署
        http://shouce.jb51.net/activiti/#N1330A
        """
        url = self.service_url + f"repository/deployments/{deploymentId}"
        return self.GET_json(url=url, headers=self.headers)

    def deployment_delete(self, deploymentId):
        """
        删除一个部署
        http://shouce.jb51.net/activiti/#N13390
        :return:
        """
        url = self.service_url + f"repository/deployments/{deploymentId}"
        return self.DELETE_status(url=url, headers=self.headers)

    #### 流程
    def process_definitions_search(self, version=None, name=None, nameLike=None, key=None,
                                   keyLike=None, resourceName=None, resourceNameLike=None,
                                   category=None, categoryLike=None, categoryNotEquals=None,
                                   deploymentId=None, startableByUser=None, latest=True,
                                   suspended=None, sort="id",
                                   order="asc", start=0, size=10):
        """
        流程定义列表
        http://shouce.jb51.net/activiti/#N134FC
        :return:
        """
        param = self.join_params(version=version, name=name, nameLike=nameLike,
                                 key=key, keyLike=keyLike, resourceName=resourceName,
                                 resourceNameLike=resourceNameLike, category=category,
                                 categoryLike=categoryLike, categoryNotEquals=categoryNotEquals,
                                 deploymentId=deploymentId, startableByUser=startableByUser,
                                 latest=latest, suspended=suspended, sort=sort,
                                 order=order, start=start, size=size)
        url = self.service_url + f"repository/process-definitions/?" + param
        return self.GET_json(url=url, headers=self.headers)

    def process_definition_search(self, processDefinitionId):
        """
        获得一个流程定义
        http://shouce.jb51.net/activiti/#N135E1
        :param processDefinitionId:
        :return:
        """
        url = self.service_url + f"repository/process-definitions/{processDefinitionId}"
        return self.GET_json(url=url, headers=self.headers)

    def process_definition_model_search(self, processDefinitionId):
        """
        流程定义模型查询
        http://shouce.jb51.net/activiti/#N1369F
        :param processDefinitionId:
        :return: 返回流程图
        """
        url = self.service_url + f"repository/process-definitions/{processDefinitionId}/model"
        return self.GET_json(url=url, headers=self.headers)

    def process_definition_resource(self, processDefinitionId):
        """
        流程定义资源内容查询
        http://shouce.jb51.net/activiti/#N13670
        :return:
        """
        url = self.service_url + f"repository/process-definitions/{processDefinitionId}/resourcedata"
        return self.GET_str(url=url, headers=self.headers)

    def process_instance_start(self, processDefinitionId=None, businessKey=None,
                               variables=None, processDefinitionKey=None,
                               tenantId=None, message=None):
        """
        流程实例启动
        http://shouce.jb51.net/activiti/#N13CC0
        :return:
        """
        body = {
            "processDefinitionId": processDefinitionId,
            "businessKey": businessKey,
            "variables": variables,
            "processDefinitionKey": processDefinitionKey,
            "tenantId": tenantId,
            "message": message
        }
        url = self.service_url + f"runtime/process-instances"
        return self.POST_json(url=url, json=body, headers=self.headers)

    def process_instances_search(self, id=None,
                                 processDefinitionKey=None,
                                 processDefinitionId=None,
                                 businessKey=None,
                                 involvedUser=None,
                                 suspended=None,
                                 superProcessInstanceId=None,
                                 subProcessInstanceId=None,
                                 excludeSubprocesses=None,
                                 includeProcessVariables=None,
                                 tenantId=None,
                                 tenantIdLike=None,
                                 withoutTenantId=None, sort="id",
                                 order="asc", start=0, size=10):
        """
        流程实例列表查询
        http://shouce.jb51.net/activiti/#restProcessInstancesGet
        :return:
        """
        params = self.join_params(id=id,
                                  processDefinitionKey=processDefinitionKey,
                                  processDefinitionId=processDefinitionId,
                                  businessKey=businessKey,
                                  involvedUser=involvedUser,
                                  suspended=suspended,
                                  superProcessInstanceId=superProcessInstanceId,
                                  subProcessInstanceId=subProcessInstanceId,
                                  excludeSubprocesses=excludeSubprocesses,
                                  includeProcessVariables=includeProcessVariables,
                                  tenantId=tenantId,
                                  tenantIdLike=tenantIdLike,
                                  withoutTenantId=withoutTenantId, sort=sort,
                                  order=order, start=start, size=size)
        url = self.service_url + f"runtime/process-instances/?" + params
        return self.GET_json(url=url, headers=self.headers)

    def process_instance_search(self, processInstanceId):
        """
        流程实例查询（单个）
        http://shouce.jb51.net/activiti/#N13E42
        :return:
        """
        url = self.service_url + f"runtime/process-instances/{processInstanceId}"
        return self.GET_json(url=url, headers=self.headers)

    def process_instance_delete(self, processInstanceId):
        """
        流程实例删除（单个）
        http://shouce.jb51.net/activiti/#N13C2A
        :return:
        """
        url = self.service_url + f"runtime/process-instances/{processInstanceId}"
        return self.DELETE_status(url=url, headers=self.headers)

    def process_instance_variables_search(self, processInstanceId):
        """
        流程实例变量查询
        http://shouce.jb51.net/activiti/#N13F8E
        :param processInstanceId:
        :return:
        """
        url = self.service_url + f"runtime/process-instances/{processInstanceId}/variables"
        return self.GET_json(url=url, headers=self.headers)

    def process_instance_variable_search(self, processInstanceId, variableName):
        """
        流程实例变量查询（指定特定变量名称）
        http://shouce.jb51.net/activiti/#N13FDD
        :param processInstanceId:
        :param variableName:
        :return:
        """
        url = self.service_url + f"runtime/process-instances/{processInstanceId}/variables/{variableName}"
        return self.GET_json(url=url, headers=self.headers)

    ## 任务

    def tasks_search(self, name=None,
                     nameLike=None,
                     description=None,
                     priority=None,
                     minimumPriority=None,
                     maximumPriority=None,
                     assignee=None,
                     assigneeLike=None,
                     owner=None,
                     ownerLike=None,
                     unassigned=None,
                     delegationState=None,
                     candidateUser=None,
                     candidateGroup=None,
                     involvedUser=None,
                     taskDefinitionKey=None,
                     taskDefinitionKeyLike=None,
                     processInstanceId=None,
                     processInstanceBusinessKey=None,
                     processInstanceBusinessKeyLike=None,
                     processDefinitionKey=None,
                     processDefinitionKeyLike=None,
                     processDefinitionName=None,
                     processDefinitionNameLike=None,
                     executionId=None,
                     createdOn=None,
                     createdBefore=None,
                     createdAfter=None,
                     dueOn=None,
                     dueBefore=None,
                     dueAfter=None,
                     withoutDueDate=None,
                     excludeSubTasks=None,
                     active=None,
                     includeTaskLocalVariables=None,
                     includeProcessVariables=None,
                     tenantId=None,
                     tenantIdLike=None,
                     withoutTenantId=None, ):
        """
        查询任务列表
        http://shouce.jb51.net/activiti/#restTasksGet
        :return:
        """
        params = self.join_params(name=name,
                                  nameLike=nameLike,
                                  description=description,
                                  priority=priority,
                                  minimumPriority=minimumPriority,
                                  maximumPriority=maximumPriority,
                                  assignee=assignee,
                                  assigneeLike=assigneeLike,
                                  owner=owner,
                                  ownerLike=ownerLike,
                                  unassigned=unassigned,
                                  delegationState=delegationState,
                                  candidateUser=candidateUser,
                                  candidateGroup=candidateGroup,
                                  involvedUser=involvedUser,
                                  taskDefinitionKey=taskDefinitionKey,
                                  taskDefinitionKeyLike=taskDefinitionKeyLike,
                                  processInstanceId=processInstanceId,
                                  processInstanceBusinessKey=processInstanceBusinessKey,
                                  processInstanceBusinessKeyLike=processInstanceBusinessKeyLike,
                                  processDefinitionKey=processDefinitionKey,
                                  processDefinitionKeyLike=processDefinitionKeyLike,
                                  processDefinitionName=processDefinitionName,
                                  processDefinitionNameLike=processDefinitionNameLike,
                                  executionId=executionId,
                                  createdOn=createdOn,
                                  createdBefore=createdBefore,
                                  createdAfter=createdAfter,
                                  dueOn=dueOn,
                                  dueBefore=dueBefore,
                                  dueAfter=dueAfter,
                                  withoutDueDate=withoutDueDate,
                                  excludeSubTasks=excludeSubTasks,
                                  active=active,
                                  includeTaskLocalVariables=includeTaskLocalVariables,
                                  includeProcessVariables=includeProcessVariables,
                                  tenantId=tenantId,
                                  tenantIdLike=tenantIdLike,
                                  withoutTenantId=withoutTenantId)
        url = self.service_url + f"runtime/tasks/?" + params
        return self.GET_json(url=url, headers=self.headers)

    def task_search(self, taskId):
        """
        查询特定任务
        http://shouce.jb51.net/activiti/#N14658
        :return:
        """
        url = self.service_url + f"runtime/tasks/{taskId}"
        return self.GET_json(url=url, headers=self.headers)

    def task_variables_search(self, taskId, scope="local"):
        """
        获取任务的变量
        http://shouce.jb51.net/activiti/#N149AA
        :return:
        """
        url = self.service_url + f"runtime/tasks/{taskId}/variables?scope={scope}"
        return self.GET_json(url=url, headers=self.headers)

    def task_variable_search(self, taskId, variableName, scope="local"):
        """
        获取任务的一个变量
        http://shouce.jb51.net/activiti/#N14A03
        :return:
        """
        url = self.service_url + f"runtime/tasks/{taskId}/variables/{variableName}?scope={scope}"
        return self.GET_json(url=url, headers=self.headers)

    def task_action(self, taskId, action="complete", variables=None):
        """
        执行任务
        http://shouce.jb51.net/activiti/#N148EB
        :return:
        """
        url = self.service_url + f"runtime/tasks/{taskId}"
        body = {
            "action": action,
            "variables": variables
        }
        return self.POST_json(url=url, json=body, headers=self.headers)

    def task_delete(self, taskId, cascadeHistory=False, deleteReason=""):
        """
        删除任务
        http://shouce.jb51.net/activiti/#N14953
        :return:
        """
        url = self.service_url + f"runtime/tasks/{taskId}?cascadeHistory={cascadeHistory}&deleteReason={deleteReason}"
        return self.DELETE_status(url=url, headers=self.headers)

    def join_params(self, **kwargs):
        s = {}
        for k, v in kwargs.items():
            if v == None:
                continue
            s[k] = v
        return urlencode(s)


def test():
    ac = Activiti()
    # print(ac.deployment_upload(filename="./reviewSaledLead.bpmn20.xml"))
    # print(ac.deployments_search())
    # print(ac.process_definitions_search(nameLike="Review sales lead"))
    # print(json.dumps(ac.process_definition_model_search(processDefinitionId="reviewSaledLead:2:43")))
    print(ac.process_definition_resource(processDefinitionId="reviewSaledLead:2:43"))


if __name__ == '__main__':
    test()
