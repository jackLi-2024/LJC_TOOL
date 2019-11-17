#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""
import logging
import os
import sys
import json

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass

import pymongo

try:
    cur_dir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append("%s/" % cur_dir)
    from config import Conf

    MONGO_HOST = Conf().MONGO_HOST
except Exception as e:
    logging.exception(e)
    # raise Exception("同级目录缺少配置文件config.py---[MONGO_HOST]")
    MONGO_HOST = {}


class MongoDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    api document: http://api.mongodb.com/python/current/examples/bulk.html
    # >>> from LJC_tool.db import MongoDB
    # >>> host = "xxx.xxx.xxx.xxx"
    # >>> port = 27017
    # >>> auth_user = "root"
    # >>> auth_password = "xxxx"
    # >>> auth_db = "PAND"
    # >>> mongodb = MongoDB(host=host, port=port, auth_user=auth_user, auth_password=auth_password, auth_db=auth_db,
    # >>> ...                  auth_method="DEFAULT")
    # >>> l = list(mongodb.get_collection().find())
    # >>> print(str(mongodb.get_database().list_collection_names()))
    # >>> print(l)
    """

    def __init__(self, host=None,
                 port=None,
                 document_class=dict,
                 tz_aware=None,
                 connect=None,
                 type_registry=None,
                 auth_user=None,
                 auth_password=None,
                 auth_db=None,
                 auth_method="SCRAM-SHA-1",
                 **kwargs):
        try:
            self.client = pymongo.MongoClient(host=host,
                                              port=int(port),
                                              document_class=document_class,
                                              tz_aware=tz_aware,
                                              connect=connect,
                                              type_registry=type_registry,
                                              **kwargs)

            if all([auth_db, auth_user, auth_password]):
                self.db = self.client[auth_db]
                self.db.authenticate(
                    auth_user, auth_password, mechanism=auth_method)
            else:
                self.db = self.client[auth_db]

        except Exception as e:
            raise Exception("---Connect Error---\
                            \n[ %s ]" % str(e))

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            pass

    def close(self):
        self.client.close()


class MongoCrud():
    def __init__(self, MONGO_HOST=MONGO_HOST):
        self.mongodb = MongoDB(**MONGO_HOST)
        self.db = self.mongodb.db

    @property
    def get_collections(self):
        return self.mongodb.db.list_collection_names()

    def get_collection(self, collection_name):
        return self.db[collection_name]

    def run(self):
        """程序运行入口"""
        try:
            data = self.deal()
        except Exception as e:
            try:
                self.mongodb.close()
            except:
                pass
            raise e
        return data

    def deal(self):
        a = self.get_collections
        test = self.get_collection("test")
        print(a)
        result = list(test.find())
        print(result)
