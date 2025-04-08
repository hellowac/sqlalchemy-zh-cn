# ext/serializer.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

"""
.. tab:: 中文

    用于 SQLAlchemy 查询结构的序列化器/反序列化器对象，允许实现“上下文感知”的反序列化。
    
    .. legacy::
    
        序列化器扩展是 **遗留功能**，不建议在新的开发中使用。
    
    任何 SQLAlchemy 的查询结构，无论基于 ``sqlalchemy.sql.*`` 还是 ``sqlalchemy.orm.*``，都可以使用。
    结构中引用的映射器（Mapper）、表（Table）、列（Column）、会话（Session）等对象不会以序列化形式持久化，
    而是在反序列化时重新关联到该查询结构。
    
    .. warning:: 序列化器扩展使用 Python 的 pickle 模块进行对象的序列化和反序列化，因此需要遵循
       `Python 官方文档 <https://docs.python.org/3/library/pickle.html>`_ 中关于安全性的说明。
    
    用法几乎与标准的 Python pickle 模块相同::
    
        from sqlalchemy.ext.serializer import loads, dumps
    
        metadata = MetaData(bind=some_engine)
        Session = scoped_session(sessionmaker())
    
        # ... 定义映射器
    
        query = (
            Session.query(MyClass)
            .filter(MyClass.somedata == "foo")
            .order_by(MyClass.sortkey)
        )
    
        # 序列化查询对象
        serialized = dumps(query)
    
        # 反序列化。传入 metadata 和 scoped_session
        query2 = loads(serialized, metadata, Session)
    
        print(query2.all())
    
    使用限制与原生 pickle 相似；被映射的类必须本身是可 pickle 的，即它们必须能从模块级命名空间中被导入。
    
    该序列化器模块仅适用于查询结构。不适用于以下情况：
    
    * 用户自定义类的实例。通常情况下这些实例不包含对引擎、会话或表达式结构的引用，因此可以直接序列化。
    
    * 需要完全从序列化结构中加载的表元数据（即在应用中尚未声明的）。对于这种情况，可以直接使用标准的
      ``pickle.loads()/dumps()`` 来完整序列化任何 ``MetaData`` 对象，通常用于将某个时间点反射得到的
      数据库结构保存下来。序列化器模块则是为另一种情况而设计 —— 当表元数据已存在于内存中时使用。


.. tab:: 英文

    Serializer/Deserializer objects for usage with SQLAlchemy query structures,
    allowing "contextual" deserialization.
    
    .. legacy::
    
        The serializer extension is **legacy** and should not be used for
        new development.
    
    Any SQLAlchemy query structure, either based on sqlalchemy.sql.*
    or sqlalchemy.orm.* can be used.  The mappers, Tables, Columns, Session
    etc. which are referenced by the structure are not persisted in serialized
    form, but are instead re-associated with the query structure
    when it is deserialized.
    
    .. warning:: The serializer extension uses pickle to serialize and
       deserialize objects, so the same security consideration mentioned
       in the `python documentation
       <https://docs.python.org/3/library/pickle.html>`_ apply.
    
    Usage is nearly the same as that of the standard Python pickle module::
    
        from sqlalchemy.ext.serializer import loads, dumps
    
        metadata = MetaData(bind=some_engine)
        Session = scoped_session(sessionmaker())
    
        # ... define mappers
    
        query = (
            Session.query(MyClass)
            .filter(MyClass.somedata == "foo")
            .order_by(MyClass.sortkey)
        )
    
        # pickle the query
        serialized = dumps(query)
    
        # unpickle.  Pass in metadata + scoped_session
        query2 = loads(serialized, metadata, Session)
    
        print(query2.all())
    
    Similar restrictions as when using raw pickle apply; mapped classes must be
    themselves be pickleable, meaning they are importable from a module-level
    namespace.
    
    The serializer module is only appropriate for query structures.  It is not
    needed for:
    
    * instances of user-defined classes.   These contain no references to engines,
      sessions or expression constructs in the typical case and can be serialized
      directly.
    
    * Table metadata that is to be loaded entirely from the serialized structure
      (i.e. is not already declared in the application).   Regular
      pickle.loads()/dumps() can be used to fully dump any ``MetaData`` object,
      typically one which was reflected from an existing database at some previous
      point in time.  The serializer module is specifically for the opposite case,
      where the Table metadata is already present in memory.

"""

from io import BytesIO
import pickle
import re

from .. import Column
from .. import Table
from ..engine import Engine
from ..orm import class_mapper
from ..orm.interfaces import MapperProperty
from ..orm.mapper import Mapper
from ..orm.session import Session
from ..util import b64decode
from ..util import b64encode


__all__ = ["Serializer", "Deserializer", "dumps", "loads"]


class Serializer(pickle.Pickler):

    def persistent_id(self, obj):
        # print "serializing:", repr(obj)
        if isinstance(obj, Mapper):
            id_ = "mapper:" + b64encode(pickle.dumps(obj.class_))
        elif isinstance(obj, MapperProperty):
            id_ = (
                "mapperprop:"
                + b64encode(pickle.dumps(obj.parent.class_))
                + ":"
                + obj.key
            )
        elif isinstance(obj, Table):
            if "parententity" in obj._annotations:
                id_ = "mapper_selectable:" + b64encode(
                    pickle.dumps(obj._annotations["parententity"].class_)
                )
            else:
                id_ = f"table:{obj.key}"
        elif isinstance(obj, Column) and isinstance(obj.table, Table):
            id_ = f"column:{obj.table.key}:{obj.key}"
        elif isinstance(obj, Session):
            id_ = "session:"
        elif isinstance(obj, Engine):
            id_ = "engine:"
        else:
            return None
        return id_


our_ids = re.compile(
    r"(mapperprop|mapper|mapper_selectable|table|column|"
    r"session|attribute|engine):(.*)"
)


class Deserializer(pickle.Unpickler):

    def __init__(self, file, metadata=None, scoped_session=None, engine=None):
        super().__init__(file)
        self.metadata = metadata
        self.scoped_session = scoped_session
        self.engine = engine

    def get_engine(self):
        if self.engine:
            return self.engine
        elif self.scoped_session and self.scoped_session().bind:
            return self.scoped_session().bind
        else:
            return None

    def persistent_load(self, id_):
        m = our_ids.match(str(id_))
        if not m:
            return None
        else:
            type_, args = m.group(1, 2)
            if type_ == "attribute":
                key, clsarg = args.split(":")
                cls = pickle.loads(b64decode(clsarg))
                return getattr(cls, key)
            elif type_ == "mapper":
                cls = pickle.loads(b64decode(args))
                return class_mapper(cls)
            elif type_ == "mapper_selectable":
                cls = pickle.loads(b64decode(args))
                return class_mapper(cls).__clause_element__()
            elif type_ == "mapperprop":
                mapper, keyname = args.split(":")
                cls = pickle.loads(b64decode(mapper))
                return class_mapper(cls).attrs[keyname]
            elif type_ == "table":
                return self.metadata.tables[args]
            elif type_ == "column":
                table, colname = args.split(":")
                return self.metadata.tables[table].c[colname]
            elif type_ == "session":
                return self.scoped_session()
            elif type_ == "engine":
                return self.get_engine()
            else:
                raise Exception("Unknown token: %s" % type_)


def dumps(obj, protocol=pickle.HIGHEST_PROTOCOL):
    buf = BytesIO()
    pickler = Serializer(buf, protocol)
    pickler.dump(obj)
    return buf.getvalue()


def loads(data, metadata=None, scoped_session=None, engine=None):
    buf = BytesIO(data)
    unpickler = Deserializer(buf, metadata, scoped_session, engine)
    return unpickler.load()
