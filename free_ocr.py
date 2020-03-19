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
import random
import sys
import json
import base64

import requests


def deployments(filename):
    """暂时用postman执行"""

    url = "https://up.gaitubao.net/"
    files = {'file': open(filename, 'rb')}
    data = {"token":"8ee8584c790d154b7edff0ce53b7f1d6"}
    result = requests.post(url=url, files=files,data=data).json()
    print(result)
    data ={"cmd":"ocr","keys":json.dumps([result["key"]])}
    headers ={
        "Host": "www.gaitubao.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Referer": "https://www.gaitubao.com/tupian-wenzi/",
    }
    result = requests.post(url="https://www.gaitubao.com/do/process",headers=headers,data=data).json()
    print(json.dumps(result,ensure_ascii=False))
    return result
if __name__ == '__main__':
    deployments(filename="./images/_#30.png")



