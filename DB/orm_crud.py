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
import decimal
import os
import sys
import json
import shortuuid
import logging
import time
from sqlalchemy.orm import aliased
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import text
from sqlalchemy import func
from hashids import Hashids

try:
    reload(sys)
    sys.setdefaultencoding("utf8")
except:
    pass


class SqlDBOrm():
    """
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
                 poolclass=NullPool, ssl_ca="", ssl_cert="", ssl_key=""):
        connect_args = {}
        if ssl_ca:
            connect_args["ssl"] = {"ca": ssl_ca, "cert": ssl_cert, "ssl_key": ssl_key}
        # if cursorclass:
        #     connect_args["cursorclass"] = cursorclass
        # if not connect_args:
        #     connect_args = None
        engine = create_engine(host,
                               poolclass=poolclass, connect_args=connect_args
                               )
        Base = automap_base()
        Base.prepare(engine, reflect=True)
        self.modelClass = Base.classes
        self.session = Session(engine)

    @property
    def get_modelClass(self):
        return self.modelClass

    @property
    def get_session(self):
        return self.session

    def close(self):
        try:
            self.session.close()
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
                dic[k] = float(v)
            else:
                dic[k] = v
        return dic


try:
    cur_dir = os.path.split(os.path.realpath(__file__))[0]
    sys.path.append("%s/" % cur_dir)
    from config import Conf

    host = Conf().ORM_HOST
    map_code = Conf().map_code
    table_replication = Conf().ORM_TABLE_REPLICATION
except:
    # raise Exception("同级目录缺少配置文件config.py---[ORM_HOST,map_code,ORM_TABLE_REPLICATION]")
    host = "mysql+pymysql://xxx"
    map_code = {}
    table_replication = 2
mysql = SqlDBOrm(host=host)
session = mysql.get_session
model = mysql.get_modelClass

for m in model.__dir__():
    if m[0] == "_":
        continue
    exec("{} = model.{}".format(m, m))
    for i in range(1, table_replication + 1):
        exec("{}_{} = aliased({})".format(m, i, m))


class OrmCrud():
    """
    *** 主要简化多表联查的情况, 注意每个表都有附表***
    base_model: 查询基础模型名称，即数据库表名
    join_model: 左外连接查询条件，注意模型的先后顺序,完全按照filter()语法，model2.field2 == model1.field1
    filter_filed: kwargs参数arguments中的字段，需要加入filter进行过滤
    sort_field ：参数sort_field字段，需要加入排序order_by进行排序
    special_filter: 特殊过滤条件,完全按照filter()语法，model2.field2 == model1.field1
    True_False_field: 查询的返回字段，进行汉化，例如 0 -- > 否 ，1 --> 是
    map_field：意思同上，实现返回字段，进行汉化，例如 1000 --> 成功， 1001 --> 失败(映射关系一般来自数据字典)
    样例：
        base_model = "city"
        join_model = {"province": ["province.id == city,id"]}
        filter_filed = {"city":["name","latitude","lontitude"]}
        sort_field = {"create_time": "city"}
        special_filter = ["city.city_code == '400000'"]
        True_False_field = ["is_delete"]
        map_field = ["status"]
    """
    base_model = ""
    join_model = {}
    filter_filed = {}
    sort_field = {}
    special_filter = []
    True_False_field = []
    map_field = []

    def __init__(self, args=None, **kwargs):
        """

        :param args:  用于接受额外其他参数
        :param kwargs: 固定参数
            ｛
                "page_num": 1,
                ""page_size: 10,
                "order_field": "-create_time",
                "arguments": {
                    "city_code": "40000"
                }
            ｝
        """
        self.page_num = kwargs.get("page_num", 1)
        self.page_size = kwargs.get("page_size", 10)
        self.order_field = kwargs.get("order_field", "")
        self.arguments = kwargs.get("arguments", {})
        self.kwargs = kwargs
        self.args = args

    def set_page_size_limit(self, page_num=None, page_size=2000):
        """设置当前查询的最大数量限制"""
        if page_num:
            self.page_num = page_num
        self.page_size = page_size

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

    def attr_to_dict(self, model):
        if not model:
            return {}
        dic = dict()
        for c in model.__table__.columns:
            k = c.name
            v = getattr(model, c.name)
            if isinstance(v, datetime):
                v = v.strftime("%Y-%m-%d %H:%M:%S")
                dic[k] = v
            elif isinstance(v, decimal.Decimal):
                dic[k] = float(v)

            elif k in self.True_False_field:
                if v == 0 or v == "0":
                    dic[k] = v
                    dic["{}_value".format(k)] = "否"
                elif v == 1 or v == "1":
                    dic[k] = v
                    dic["{}_value".format(k)] = "是"
                else:
                    dic[k] = v
            elif k in self.map_field:
                if v in map_code:
                    dic[k] = v
                    dic["{}_value".format(k)] = map_code[v]
                else:
                    dic[k] = v
            else:
                dic[k] = v
        return dic

    def deal_filter_field(self):
        """
        filter_filed = {
            "model_name":["field1","field2"]
            }
        :return:
        """
        actions = []
        for k, v in self.filter_filed.items():
            for one in v:
                if self.arguments.get(one) != None and type(self.arguments.get(one)) != list:
                    actions.append(eval("{}.{}".format(k, one)) == self.arguments.get(one))
                elif self.arguments.get(one) != None and type(self.arguments.get(one)) == list and len(
                        self.arguments.get(one)) == 2:
                    actions.append(eval("{}.{}".format(k, one)) >= self.arguments.get(one)[0])
                    actions.append(eval("{}.{}".format(k, one)) <= self.arguments.get(one)[1])
        return actions

    def deal_order_field(self):
        """
        sort_field = {
            "field":"model_name"
            }
        :return:
        """
        for k, v in self.order_field.items():
            if self.sort_field and type(self.sort_field) == str:
                if self.sort_field[1:] == k:
                    return text("{}{}.{}".format(self.sort_field[0], v, self.sort_field[1:]))
        return text("")

    def deal_read_model(self):
        if not self.base_model:
            raise Exception("base_model can't be null")
        join_models = []
        for i in list(self.join_model.keys()):
            join_models.append(eval(i))
        filter_condition = self.deal_filter_field()
        for one in self.special_filter:
            filter_condition.append(eval(one))
        new_model = session.query(eval(self.base_model), *join_models).filter(*filter_condition)
        for k, v in self.join_model.items():
            for i in v:
                new_model = new_model.outerjoin(eval(k), eval(i))
        new_model = new_model.order_by(self.deal_order_field()).limit(self.page_size).offset(
            (self.page_num - 1) * self.page_size)
        return new_model

    @property
    def ids(self):
        """
        :return: 查询的ids
        """
        ids_ = []
        result = self.read()
        for i in result:
            for j in i:
                ids_.append(j.get("id"))
        return ids_

    @property
    def total(self):
        """
        :return: 查询的数量
        """
        new_model = self.deal_read_model()
        return new_model.count()

    def read(self):
        """读操作"""
        new_model = self.deal_read_model()
        result = new_model.all()
        out = []
        for info in result:
            middle = []
            if not self.join_model:
                info = [info]
            for m in info:
                middle.append(self.attr_to_dict(m))
            out.append(middle)
        return out

    def add(self, model_name: str, data: dict):
        """添加操作"""
        data = data
        return session.add(eval("{}".format(model_name))(**data))

    def add_all(self, model_name: str, datas: list):
        """批量添加操作"""
        if not datas:
            return
        actions = []
        for dic in datas:
            actions.append(eval("{}".format(model_name))(**dic))
        return session.add_all(actions)

    def update(self, model_name: str, ids: list, update_data: dict):
        """更新操作"""
        return session.query(eval(model_name)).filter(eval(model_name).id.in_(ids)).update(update_data,
                                                                                           synchronize_session=False)

    def run(self):
        """程序运行入口"""
        try:
            data = self.deal()
            session.commit()
        except Exception as e:
            try:
                session.rollback()
            except:
                pass
            try:
                session.close()
            except:
                pass
            raise e
        return data

    def deal(self):
        """处理器,用户需要这里自行定义逻辑"""
        # data = {"city_code": "40000"}
        # res = self.orm_add(model_name="pd_city_area", data=data)
        # datas = [{"city_code": "50000"}, {"city_code": "60000"}]
        # res = self.orm_add_all(model_name="pd_city_area", datas=datas)
        # update_data = {"city_code": "40000"}
        # res = self.orm_update(model_name="pd_city_area", ids=[1,2], update_data=update_data)
        # res = self.orm_delete(model_name="pd_city_area", ids=[1, 2])
        # print(res)
        # print(self.deal_filter_field())
        print(self.read())
