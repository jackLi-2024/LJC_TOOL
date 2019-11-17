#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@JackLee.com
===========================================
"""
import decimal
import logging
import os
import sys
import json
import cx_Oracle
import pymysql
import pymongo
import redis

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from elasticsearch import Elasticsearch
from elasticsearch import helpers

# os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"
os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.ZHS16GBK"


class Oracle():
    """
    oracle 数据库读操作
    # >>> from LJC_tool.db import Oracle
    # >>> host = "xxx.xxx.xxx.xxx"
    # >>> port = "xxx"
    # >>> service_name = "ORCL"
    # >>> user = "xxx"
    # >>> password = "xxx"
    # >>> oracle = Oracle(host=host, port=port,
    # >>> ...    service_name=service_name, user=user, password=password)
    # >>> sql="select * from db.test;"
    # >>> oracle.execute(sql=sql)
    # >>> data = list(oracle.fetch("fetchall()"))
    # >>> print(data)
    """

    def __init__(self, host=None, port=None, service_name="ORCL", user=None, password=None,
                 conf=dict()):
        host = conf.get("host", host)
        port = conf.get("port", port)
        service_name = conf.get("ORCL", service_name)
        user = conf.get("user", user)
        password = conf.get("password", password)
        try:
            dsn_tns = cx_Oracle.makedsn(host, port, service_name=service_name)
            self.client = cx_Oracle.connect(
                user=user, password=password, dsn=dsn_tns)
            self.cursor = self.client.cursor()
        except Exception as e:
            self.output(str(e))
            raise Exception("---Connnect Error---")

    def fetch(self, query=""):
        """
        fetch data by sql (select)
        :param query: fetchmany(size=20)
        :return:
        """
        try:

            return eval("self.cursor.%s" % query)
        except Exception as e:
            self.output(str(e))

    def execute(self, sql=""):
        """
        excute sql
        :param query:
        :param args:
        :return:
        """
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.output(str(e))

    def commit(self):
        """commit insert sql"""
        try:
            self.client.commit()
        except Exception as e:
            self.output(str(e))
            raise e

    def rollback(self):
        """rollback sql"""
        try:
            self.client.rollback()
        except Exception as e:
            self.output(str(e))
            raise e

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

    def output(self, arg):
        print(str(arg))
        logging.exception(str(arg))


class MysqlDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    http://mysql-python.sourceforge.net/MySQLdb.html#
    # >>> from LJC_tool.db import MysqlDB
    # >>> host = "xxx.xxx.xxx.xxx"
    # >>> port = 3306
    # >>> user = "root"
    # >>> password = "xxx"
    # >>> cursorclass = "pymysql.cursors.DictCursor"
    # >>> db = "test"
    # >>> mysql = MysqlDB(host=host, port=port, user=user, password=password, db=db, cursorclass=cursorclass)
    # >>> mysql.execute(sql="select * from customers;")
    # >>> data = list(mysql.fetch("fetchmany(size=10)"))
    # >>> print(data)
    """

    def __init__(self, host=None, port=3306, user="root", password="123456", db="test",
                 ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor", conf={}):
        self.db = conf.get("db", db)
        host = conf.get("host", host)
        port = int(conf.get("port", port))
        user = conf.get("user", user)
        password = conf.get("password", password)
        cursorclass = eval(conf.get("cursorclass", cursorclass))
        ssl_ca = conf.get("ssl_ca", ssl_ca)
        ssl_cert = conf.get("ssl_cert", ssl_cert)
        ssl_key = conf.get("ssl_key", ssl_key)
        if ssl_ca:
            ssl = {"ssl": {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}}
        else:
            ssl = None
        try:
            self.client = pymysql.connect(host=host, port=port, passwd=password, user=user,
                                          ssl=ssl,
                                          cursorclass=cursorclass)
            self.cursor = self.client.cursor()
            self.create_database()
        except Exception as e:
            raise Exception("---Connect MysqlServer Error--- [%s]" % str(e))

    def create_database(self):
        try:
            self.cursor.execute('CREATE DATABASE IF NOT EXISTS %s' % self.db)
        except Exception as e:
            self.output(str(e))
        self.client.select_db(self.db)

    def create_table(self, sql=""):
        """
        create table
        :param sql: CREATE TABLE test (id int primary key,name varchar(30))
        :return:
        """
        try:
            self.cursor.execute(sql)
        except Exception as e:
            self.output(str(e))
            raise e

    def fetch(self, query=""):
        """
        fetch data by sql (select)
        :param query: fetchmany(size=20)
        :return:
        """
        try:
            return eval("self.cursor.%s" % query)
        except Exception as e:
            self.output(str(e))
            raise e

    def execute(self, sql="", args=None):
        """
        excute sql
        :param sql: 执行sql语句
        :param args:
        :return:
        """
        try:
            self.cursor.execute(query=sql, args=args)
        except Exception as e:
            self.output(str(e))
            raise e

    def commit(self):
        """commit insert sql"""
        try:
            self.client.commit()
        except Exception as e:
            self.output(str(e))
            raise e

    def rollback(self):
        """commit insert sql"""
        try:
            self.client.rollback()
        except Exception as e:
            self.output(str(e))
            raise e

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

    def output(self, arg):
        # print(str(arg))
        logging.exception(str(arg))


class SqlDBOrm():
    """
    # >>> from LJC_tool.db import SqlDBOrm
    # >>> host = "mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8"
    # >>> mysql = SqlDBOrm(host)
    # >>> baseClass = mysql.get_modelClass()
    # >>> Stations = baseClass.stations
    # # sql查询
    # >>> data = session.execute(sql="select * from customers;")
    # >>> data = list(data.fetchall())
    # >>> print(data)
    # # orm查询
    # >>> session = mysql.get_session()
    # >>> condition = [Stations.id==1]
    # >>> with mysql.session_maker(session) as sess:
    # >>> ... res = sess.query(Stations).filter(*condition).all()
    # >>> ... for station in res:
    # >>> ...         result = mysql.attr_to_dict(station)
    # >>> ...         print(result)

    """

    def __init__(self, host="mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8",
                 poolclass=NullPool, ssl_ca="", ssl_cert="", ssl_key="",
                 cursorclass="pymysql.cursors.SSCursor"):
        connect_args = {}
        if ssl_ca:
            connect_args["ssl"] = {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}
        # if cursorclass:
        #     connect_args["cursorclass"] = cursorclass
        # if not connect_args:
        #     connect_args = None
        self.engine = create_engine(host,
                                    poolclass=poolclass, connect_args=connect_args, echo=False
                                    )
        Base = automap_base()
        Base.prepare(self.engine, reflect=True)
        self.modelClass = Base.classes
        self.session = Session(self.engine)

    def get_modelClass(self):
        return self.modelClass

    def get_session(self):
        return self.session

    def close(self):
        try:
            self.session.close()
            self.engine.dispose()
        except:
            pass

    def __del__(self):
        self.close()

    @staticmethod
    @contextmanager
    def session_maker(session=None):
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    @staticmethod
    def attr_to_dict(model):
        dic = dict()
        for c in model.__table__.columns:
            k = c.name
            v = getattr(model, c.name)
            if isinstance(v, datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                dic[k] = v
            elif isinstance(v, decimal.Decimal):
                v = float(v)
                dic[k] = v
            else:
                dic[k] = v
        return dic


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
    # >>> collection = "test"
    # >>> mongodb = MongoDB(host=host, port=port, auth_user=auth_user, auth_password=auth_password, auth_db=auth_db,
    # >>> ...                  collection=collection, auth_method="DEFAULT")
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
                 collection=None,
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
            self.collection = self.db[collection]

        except Exception as e:
            raise Exception("---Connect Error---\
                            \n[ %s ]" % str(e))

    def collection_operate(self, operation):
        return eval("self.collection.%s" % operation)

    def get_collection(self):
        return self.collection

    def get_database(self):
        return self.db

    def __del__(self):
        try:
            self.close()
        except Exception as e:
            pass

    def close(self):
        self.client.close()

    def output(self, arg):
        logging.exception(str(arg))
        print(str(arg))


class EsDB():
    """
    Mainly for batch read-write encapsulation of database, reduce the load of database
    # >>> from LJC_tool.db import EsDB
    # >>> cluster = ["http://xxxx:9200/"]
    # >>> index_name = "1234"
    # >>> es = EsDB(cluster=cluster, index_name=index_name)
    # >>> client = es.get_client()
    # >>> body ={
    # >>> ...   "query": {
    # >>> ...       "term": {"1": 2}
    # >>> ...   }
    # >>> ... }
    # ### 查询
    # >>> client.search(index=index_name,body=body)
    # >>> data = [{
    # >>> ...    "_index": "1234",
    # >>> ...   "_type": "1234",
    # >>> ...    "_id": 111,
    # >>> ...    "_source": {
    # >>> ...        "1": 1
    # >>> ...    }
    # >>> ... }]
    # ### 批量写
    # >>> es.bulk(data)
    """

    def __init__(self, cluster=None, index_name=None, schema_mapping=None, **kwargs):
        self.index_name = index_name
        self.cluster = cluster
        self.schema_mapping = schema_mapping
        try:
            self.client = Elasticsearch(cluster, **kwargs)
            if not self.index_exist():
                self.create_index(body=schema_mapping)
            else:
                print("Current index already exists(index name = %s)" %
                      self.index_name)
        except Exception as e:
            self.output(str(e))

    def get_client(self):
        return self.client

    def bulk(self, actions):
        helpers.bulk(self.client, actions=actions)

    def __del__(self):
        self.close()

    def close(self):
        try:
            del self.client
        except:
            pass

    def index_exist(self):
        return self.client.indices.exists(self.index_name)

    def create_index(self, body):
        self.client.indices.create(index=self.index_name, body=body)

    def output(self, arg):
        logging.exception(str(arg))
        # print(str(arg))
