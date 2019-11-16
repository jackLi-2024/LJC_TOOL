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

    @property
    def map_code(self):
        """数据字典"""
        return {}

    @property
    def ORM_HOST(self):
        """orm host参数"""
        return "mysql+pymysql://xxxx"

    @property
    def ORM_TABLE_REPLICATION(self):
        """orm 表备份数"""
        return 2
