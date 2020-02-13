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
import time

import pymysql
import logging
import configparser
import jwt
import hashlib
import redis
import shortuuid
from hashids import Hashids
from sql import *
from sql.aggregate import *
from sql.conditionals import *
from sql.operators import *


class RedisDB():
    def __init__(self, host='localhost', port=6379,
                 db=0, password=None, socket_timeout=None,
                 socket_connect_timeout=None,
                 socket_keepalive=None, socket_keepalive_options=None,
                 connection_pool=None, unix_socket_path=None,
                 encoding='utf-8', encoding_errors='strict',
                 charset=None, errors=None,
                 decode_responses=False, retry_on_timeout=False,
                 ssl=False, ssl_keyfile=None, ssl_certfile=None,
                 ssl_cert_reqs='required', ssl_ca_certs=None,
                 max_connections=None):
        self.client = redis.Redis(host=host, port=port,
                                  db=db, password=password, socket_timeout=socket_timeout,
                                  socket_connect_timeout=socket_connect_timeout,
                                  socket_keepalive=socket_keepalive, socket_keepalive_options=socket_keepalive_options,
                                  connection_pool=connection_pool, unix_socket_path=unix_socket_path,
                                  encoding=encoding, encoding_errors=encoding_errors,
                                  charset=charset, errors=errors,
                                  decode_responses=decode_responses, retry_on_timeout=retry_on_timeout,
                                  ssl=ssl, ssl_keyfile=ssl_keyfile, ssl_certfile=ssl_certfile,
                                  ssl_cert_reqs=ssl_cert_reqs, ssl_ca_certs=ssl_ca_certs,
                                  max_connections=max_connections)

    def get_client(self):
        return self.client

    def __del__(self):
        self.close()

    def close(self):
        try:
            del self.client
        except:
            pass


class SQL():
    """
    https://pypi.org/project/python-sql/
    :argument:
        sort_field: 参数排序字段
        page_num: 参数页数
        page_size: 参数页数容量
    """
    eq_argument = {}
    like_argument = {}
    in_argument = {}
    arguments = {}
    order_argument = {}
    section_argument = {}

    def __init__(self):
        self.page_size = self.arguments.get("page_size", 10)
        self.page_num = self.arguments.get("page_num", 1)

    def deal_sql(self, sql_obj):
        s = tuple(sql_obj)
        sql_, value = s[0], s[1]
        sql_ = sql_ % value
        return str(sql_).replace("\"", "")

    @property
    def where_eq_arguments(self):
        out = None
        for k, v in self.eq_argument.items():
            arg = self.arguments.get(k)
            if arg == None:
                continue
            if out == None:
                out = (v == f"'{arg}'")
            else:
                out = out & (v == f"'{arg}'")
        return out

    @property
    def where_like_arguments(self):
        out = None
        for k, v in self.like_argument.items():
            arg = self.arguments.get(k)
            if arg == None:
                continue
            if out == None:
                out = (v.like(f"'%{arg}%'"))
            else:
                out = out & (v.like(f"'%{arg}%'"))
        return out

    @property
    def where_in_arguments(self):
        out = None
        for k, v in self.in_argument.items():
            arg = self.arguments.get(k)
            if arg == None or not arg:
                continue
            args = []
            for i in arg:
                args.append(f"'{i}'")
            if out == None:
                out = (v.in_(args))
            else:
                out = out & (v.in_(args))
        return out

    @property
    def where_section_arguments(self):
        out = None
        for k, v in self.section_argument.items():
            arg = self.arguments.get(k, [])
            if type(arg) != list or len(arg) != 2:
                continue
            if not arg:
                continue
            args1 = arg[0]
            args2 = arg[1]
            if out == None:
                out = (v >= f"'{args1}'") & (v <= f"'{args2}'")
            else:
                out = out & (v >= f"'{args1}'") & (v <= f"'{args2}'")
        return out

    @property
    def where(self):
        out = None
        if self.where_eq_arguments:
            out = self.where_eq_arguments
        if self.where_like_arguments:
            if out:
                out = out & self.where_like_arguments
            else:
                out = self.where_like_arguments
        if self.where_in_arguments:
            if out:
                out = out & self.where_in_arguments
            else:
                out = self.where_in_arguments
        if self.where_section_arguments:
            if out:
                out = out & self.where_section_arguments
            else:
                out = self.where_section_arguments
        return out

    @property
    def order(self):
        ASC = False
        sort_field = self.arguments.get("sort_field")
        if "-" in sort_field:
            name = sort_field[1:]
            ASC = True
        else:
            name = sort_field
        obj = self.order_argument.get(name)
        if obj:
            if ASC:
                return Asc(obj)
            else:
                return obj
        return None

    def reset_page_size(self, page_size=2000):
        self.page_size = page_size

    @property
    def limit(self):
        return self.page_size

    @property
    def offset(self):
        return (self.page_num - 1) * self.page_size

    @property
    def count(self):
        return Count(Literal(1)).as_("count")


class MySQLDB():
    conf = {}

    def __init__(self, host=None, port=3306, user="root", password="123456", db="test",
                 ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor"):
        self.db = self.conf.get("db", db)
        host = self.conf.get("host", host)
        port = int(self.conf.get("port", port))
        user = self.conf.get("user", user)
        password = self.conf.get("password", password)
        cursorclass = eval(self.conf.get("cursorclass", cursorclass))
        ssl_ca = self.conf.get("ssl_ca", ssl_ca)
        ssl_cert = self.conf.get("ssl_cert", ssl_cert)
        ssl_key = self.conf.get("ssl_key", ssl_key)
        if ssl_ca:
            ssl = {"ssl": {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}}
        else:
            ssl = None
        self.connect_args = {"host": host, "port": port, "passwd": password, "user": user, "ssl": ssl,
                             "cursorclass": cursorclass}
        self.connect(**self.connect_args)

    def connect(self, **connect_args):
        try:
            self.client = pymysql.connect(**connect_args)
            self.cursor = self.client.cursor()
            self.client.select_db(self.db)
        except Exception as e:
            raise Exception("---Connect MysqlServer Error--- [%s]" % str(e))

    def connect_again(self, func):
        def wrapper(*args, **kwargs):
            if self.cursor == None:
                self.connect(**self.connect_args)
            return func(*args, **kwargs)

        return wrapper

    def execute(self, sql=None):
        if self.cursor == None:
            self.connect(**self.connect_args)
        self.cursor.execute(sql)

    def read_all(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        return list(self.cursor.fetchall())

    def read_many(self, size):
        if self.cursor == None:
            self.connect(**self.connect_args)
        while True:
            result = list(self.cursor.fetchmany(size=size))
            if not result:
                break
            yield result

    def read_one(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        while True:
            result = list(self.cursor.fetchone())
            if not result:
                break
            yield result

    def commit(self):
        """commit insert sql"""
        self.client.commit()

    def rollback(self):
        """commit insert sql"""
        self.client.rollback()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        try:
            self.cursor.close()
        except Exception as e:
            pass
        try:
            self.client.close()
        except Exception as e:
            pass
        self.cursor = None
        self.client = None

    def output(self, arg):
        logging.exception(str(arg))

    def create_database(self):
        if self.cursor == None:
            self.connect(**self.connect_args)
        try:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        except Exception as e:
            pass


class RandomString():
    def get_hashid(self, min_length=16, salt="PAND"):
        """
        生成随机加密字符串
        :param salt:
        :return:
        """
        ts = int(time.time() * 10000000)
        num = int(shortuuid.ShortUUID(alphabet='0123456789').random(length=8))
        hashids_ = Hashids(min_length=min_length, salt=salt)
        hashid = hashids_.encode(ts, num)
        return hashid


class MySQLCrud(SQL, MySQLDB, RandomString):
    def __init__(self, **kwargs):
        super(MySQLDB, self).__init__(**kwargs)
        super(SQL, self).__init__()
        super(RandomString, self).__init__()

    def dealer(self):
        pass

    def run(self):
        try:
            data = self.dealer()
            self.commit()
        except Exception as e:
            try:
                self.rollback()
            except:
                pass
            try:
                self.close()
            except:
                pass
            raise e
        return data


class NoneCrud(RandomString):
    def __init__(self):
        super(RandomString, self).__init__()

    def dealer(self):
        pass

    def run(self):
        data = self.dealer()
        return data


class Test(MySQLCrud):
    conf = {
        "host": "117.78.42.21",
        "port": 8050,
        "user": "root",
        "password": "qCqRZJthZe",
        "cursorclass": "pymysql.cursors.SSDictCursor",
        "db": "test1"
    }
    user_group = Table("user_group")
    log = Table("log")
    log1 = Table("log")

    eq_argument = {
        "log_id": log.log_id,
        "log_name": log.log_name
    }
    like_argument = {
        "name": user_group.name
    }

    def dealer(self):
        self.arguments = {"log_id": 1}
        s = self.log.join(self.log1, condition=self.log1.log_id == self.log.log_id)
        a = s.select(self.count, where=self.where)
        sql = self.deal_sql(a)
        self.execute(sql)
        print(self.read_all())
        print(self.read_all())
