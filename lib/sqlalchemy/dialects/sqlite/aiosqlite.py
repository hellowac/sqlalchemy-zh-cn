# dialects/sqlite/aiosqlite.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


r"""

.. dialect:: sqlite+aiosqlite
    :name: aiosqlite
    :dbapi: aiosqlite
    :connectstring: sqlite+aiosqlite:///file_path
    :url: https://pypi.org/project/aiosqlite/

.. tab:: 中文

    ``aiosqlite`` 方言为运行在 pysqlite 之上的 SQLAlchemy asyncio 接口提供支持。

    aiosqlite 是 pysqlite 的一个封装器，它为每个连接使用一个后台线程。由于 SQLite 数据库并不是基于套接字的，它并不真正使用非阻塞 IO。然而，它确实提供了一个可用的 asyncio 接口，适用于测试和原型开发场景。

    通过一个特殊的 asyncio 中介层，``aiosqlite`` 方言可以作为 :ref:`SQLAlchemy asyncio <asyncio_toplevel>` 扩展包的后端使用。

    该方言通常应仅与 :func:`_asyncio.create_async_engine` 引擎创建函数搭配使用::

        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("sqlite+aiosqlite:///filename")

    URL 中的所有参数都会传递给 ``pysqlite`` 驱动，因此所有连接参数与 :ref:`pysqlite` 相同。

.. tab:: 英文

    The aiosqlite dialect provides support for the SQLAlchemy asyncio interface
    running on top of pysqlite.

    aiosqlite is a wrapper around pysqlite that uses a background thread for
    each connection.   It does not actually use non-blocking IO, as SQLite
    databases are not socket-based.  However it does provide a working asyncio
    interface that's useful for testing and prototyping purposes.

    Using a special asyncio mediation layer, the aiosqlite dialect is usable
    as the backend for the :ref:`SQLAlchemy asyncio <asyncio_toplevel>`
    extension package.

    This dialect should normally be used only with the
    :func:`_asyncio.create_async_engine` engine creation function::

        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("sqlite+aiosqlite:///filename")

    The URL passes through all arguments to the ``pysqlite`` driver, so all
    connection arguments are the same as they are for that of :ref:`pysqlite`.

.. _aiosqlite_udfs:

用户定义的函数
----------------------

User-Defined Functions

.. tab:: 中文

    aiosqlite 扩展了 pysqlite，以支持 async，因此我们可以在 Python 中创建自定义函数（UDF），并像在 SQLite 查询中使用它们一样使用，详见 :ref:`pysqlite_udfs`。

.. tab:: 英文

    aiosqlite extends pysqlite to support async, so we can create our own user-defined functions (UDFs)
    in Python and use them directly in SQLite queries as described here: :ref:`pysqlite_udfs`.

.. _aiosqlite_serializable:

可序列化隔离/保存点/事务 DDL（asyncio版本）
-------------------------------------------------------------------------

Serializable isolation / Savepoints / Transactional DDL (asyncio version)

.. tab:: 中文

    与 pysqlite 类似，aiosqlite 也不支持 SAVEPOINT 功能。

    解决方案与 :ref:`pysqlite_serializable` 类似，可通过异步事件监听器实现::

        from sqlalchemy import create_engine, event
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("sqlite+aiosqlite:///myfile.db")


        @event.listens_for(engine.sync_engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # 完全禁用 aiosqlite 对 BEGIN 语句的自动发出行为。
            # 同时也防止其在任何 DDL 前发出 COMMIT。
            dbapi_connection.isolation_level = None


        @event.listens_for(engine.sync_engine, "begin")
        def do_begin(conn):
            # 手动发出 BEGIN
            conn.exec_driver_sql("BEGIN")

    .. warning:: 使用上述方案时，不建议在 SQLite 驱动中使用
        :class:`_engine.Connection` 与 :func:`_sa.create_engine` 的
        :paramref:`.Connection.execution_options.isolation_level` 设置，
        因为该函数也会修改 ``.isolation_level`` 设置，可能导致行为不一致。

.. tab:: 英文

    Similarly to pysqlite, aiosqlite does not support SAVEPOINT feature.

    The solution is similar to :ref:`pysqlite_serializable`. This is achieved by the event listeners in async::

        from sqlalchemy import create_engine, event
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("sqlite+aiosqlite:///myfile.db")


        @event.listens_for(engine.sync_engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # disable aiosqlite's emitting of the BEGIN statement entirely.
            # also stops it from emitting COMMIT before any DDL.
            dbapi_connection.isolation_level = None


        @event.listens_for(engine.sync_engine, "begin")
        def do_begin(conn):
            # emit our own BEGIN
            conn.exec_driver_sql("BEGIN")

    .. warning:: When using the above recipe, it is advised to not use the
        :paramref:`.Connection.execution_options.isolation_level` setting on
        :class:`_engine.Connection` and :func:`_sa.create_engine`
        with the SQLite driver,
        as this function necessarily will also alter the ".isolation_level" setting.

.. _aiosqlite_pooling:

连接池行为
----------------

Pooling Behavior

.. tab:: 中文

    SQLAlchemy 的 ``aiosqlite`` DBAPI 根据请求的 SQLite 数据库类型，以不同的方式建立连接池：

    * 当指定为 ``:memory:`` SQLite 数据库时，方言默认使用 :class:`.StaticPool`。
      此连接池维护一个单一连接，使得所有访问该 engine 的操作都使用相同的 ``:memory:`` 数据库。
    * 当指定为基于文件的数据库时，方言将使用 :class:`.AsyncAdaptedQueuePool`
      作为连接来源。

      .. versionchanged:: 2.0.38

            SQLite 文件数据库引擎现在默认使用 :class:`.AsyncAdaptedQueuePool`。
            之前默认使用的是 :class:`.NullPool`。若需使用 :class:`.NullPool`，可通过
            :paramref:`_sa.create_engine.poolclass` 参数指定。

.. tab:: 英文

    The SQLAlchemy ``aiosqlite`` DBAPI establishes the connection pool differently
    based on the kind of SQLite database that's requested:

    * When a ``:memory:`` SQLite database is specified, the dialect by default
      will use :class:`.StaticPool`. This pool maintains a single
      connection, so that all access to the engine
      use the same ``:memory:`` database.
    * When a file-based database is specified, the dialect will use
      :class:`.AsyncAdaptedQueuePool` as the source of connections.

      .. versionchanged:: 2.0.38

            SQLite file database engines now use :class:`.AsyncAdaptedQueuePool` by default.
            Previously, :class:`.NullPool` were used.  The :class:`.NullPool` class
            may be used by specifying it via the
            :paramref:`_sa.create_engine.poolclass` parameter.

"""  # noqa

import asyncio
from functools import partial

from .base import SQLiteExecutionContext
from .pysqlite import SQLiteDialect_pysqlite
from ... import pool
from ...connectors.asyncio import AsyncAdapt_dbapi_connection
from ...connectors.asyncio import AsyncAdapt_dbapi_cursor
from ...connectors.asyncio import AsyncAdapt_dbapi_ss_cursor
from ...util.concurrency import await_


class AsyncAdapt_aiosqlite_cursor(AsyncAdapt_dbapi_cursor):
    __slots__ = ()


class AsyncAdapt_aiosqlite_ss_cursor(AsyncAdapt_dbapi_ss_cursor):
    __slots__ = ()


class AsyncAdapt_aiosqlite_connection(AsyncAdapt_dbapi_connection):
    __slots__ = ()

    _cursor_cls = AsyncAdapt_aiosqlite_cursor
    _ss_cursor_cls = AsyncAdapt_aiosqlite_ss_cursor

    @property
    def isolation_level(self):
        return self._connection.isolation_level

    @isolation_level.setter
    def isolation_level(self, value):
        # aiosqlite's isolation_level setter works outside the Thread
        # that it's supposed to, necessitating setting check_same_thread=False.
        # for improved stability, we instead invent our own awaitable version
        # using aiosqlite's async queue directly.

        def set_iso(connection, value):
            connection.isolation_level = value

        function = partial(set_iso, self._connection._conn, value)
        future = asyncio.get_event_loop().create_future()

        self._connection._tx.put_nowait((future, function))

        try:
            return await_(future)
        except Exception as error:
            self._handle_exception(error)

    def create_function(self, *args, **kw):
        try:
            await_(self._connection.create_function(*args, **kw))
        except Exception as error:
            self._handle_exception(error)

    def rollback(self):
        if self._connection._connection:
            super().rollback()

    def commit(self):
        if self._connection._connection:
            super().commit()

    def close(self):
        try:
            await_(self._connection.close())
        except ValueError:
            # this is undocumented for aiosqlite, that ValueError
            # was raised if .close() was called more than once, which is
            # both not customary for DBAPI and is also not a DBAPI.Error
            # exception. This is now fixed in aiosqlite via my PR
            # https://github.com/omnilib/aiosqlite/pull/238, so we can be
            # assured this will not become some other kind of exception,
            # since it doesn't raise anymore.

            pass
        except Exception as error:
            self._handle_exception(error)

    def _handle_exception(self, error):
        if isinstance(error, ValueError) and error.args[0].lower() in (
            "no active connection",
            "connection closed",
        ):
            raise self.dbapi.sqlite.OperationalError(error.args[0]) from error
        else:
            super()._handle_exception(error)


class AsyncAdapt_aiosqlite_dbapi:
    def __init__(self, aiosqlite, sqlite):
        self.aiosqlite = aiosqlite
        self.sqlite = sqlite
        self.paramstyle = "qmark"
        self._init_dbapi_attributes()

    def _init_dbapi_attributes(self):
        for name in (
            "DatabaseError",
            "Error",
            "IntegrityError",
            "NotSupportedError",
            "OperationalError",
            "ProgrammingError",
            "sqlite_version",
            "sqlite_version_info",
        ):
            setattr(self, name, getattr(self.aiosqlite, name))

        for name in ("PARSE_COLNAMES", "PARSE_DECLTYPES"):
            setattr(self, name, getattr(self.sqlite, name))

        for name in ("Binary",):
            setattr(self, name, getattr(self.sqlite, name))

    def connect(self, *arg, **kw):
        creator_fn = kw.pop("async_creator_fn", None)
        if creator_fn:
            connection = creator_fn(*arg, **kw)
        else:
            connection = self.aiosqlite.connect(*arg, **kw)
            # it's a Thread.   you'll thank us later
            connection.daemon = True

        return AsyncAdapt_aiosqlite_connection(
            self,
            await_(connection),
        )


class SQLiteExecutionContext_aiosqlite(SQLiteExecutionContext):
    def create_server_side_cursor(self):
        return self._dbapi_connection.cursor(server_side=True)


class SQLiteDialect_aiosqlite(SQLiteDialect_pysqlite):
    driver = "aiosqlite"
    supports_statement_cache = True

    is_async = True

    supports_server_side_cursors = True

    execution_ctx_cls = SQLiteExecutionContext_aiosqlite

    @classmethod
    def import_dbapi(cls):
        return AsyncAdapt_aiosqlite_dbapi(
            __import__("aiosqlite"), __import__("sqlite3")
        )

    @classmethod
    def get_pool_class(cls, url):
        if cls._is_url_file_db(url):
            return pool.AsyncAdaptedQueuePool
        else:
            return pool.StaticPool

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.OperationalError):
            err_lower = str(e).lower()
            if "no active connection" in err_lower or "connection closed" in err_lower:
                return True

        return super().is_disconnect(e, connection, cursor)

    def get_driver_connection(self, connection):
        return connection._connection


dialect = SQLiteDialect_aiosqlite
