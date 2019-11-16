#!/usr/bin/python
# coding:utf-8

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

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass


class Conf():
    ORM_HOST = "mysql+pymysql://xxxxxx"
    ORM_TABLE_REPLICATION = 2

    @property
    def map_code(self):
        """数据字典"""
        return {}
