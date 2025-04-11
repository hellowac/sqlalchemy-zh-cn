# dialects/sqlite/pysqlcipher.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


"""
.. dialect:: sqlite+pysqlcipher
    :name: pysqlcipher
    :dbapi: sqlcipher 3 or pysqlcipher
    :connectstring: sqlite+pysqlcipher://:passphrase@/file_path[?kdf_iter=<iter>]

    Dialect for support of DBAPIs that make use of the
    `SQLCipher <https://www.zetetic.net/sqlcipher>`_ backend.


驱动
------

Driver

.. tab:: 中文

    当前方言的选择逻辑如下：

    * 如果通过 :paramref:`_sa.create_engine.module` 参数提供了一个 DBAPI 模块，
      则使用该模块。
    * 否则，在 Python 3 中优先选择 https://pypi.org/project/sqlcipher3/
    * 若该模块不可用，则回退到 https://pypi.org/project/pysqlcipher3/
    * 对于 Python 2，则使用 https://pypi.org/project/pysqlcipher/

    .. warning:: ``pysqlcipher3`` 和 ``pysqlcipher`` DBAPI 驱动已经不再维护；
       截至目前，``sqlcipher3`` 驱动仍处于活跃状态。为了兼容未来，
       可使用任何兼容 pysqlcipher 的 DBAPI，方式如下::

            import sqlcipher_compatible_driver

            from sqlalchemy import create_engine

            e = create_engine(
                "sqlite+pysqlcipher://:password@/dbname.db",
                module=sqlcipher_compatible_driver,
            )

    这些驱动使用 SQLCipher 引擎。该系统主要通过向 SQLite 引入新的 PRAGMA 命令，
    允许设置密码短语及其他加密参数，从而实现数据库文件的加密。

.. tab:: 英文

    Current dialect selection logic is:

    * If the :paramref:`_sa.create_engine.module` parameter supplies a DBAPI module,
      that module is used.
    * Otherwise for Python 3, choose https://pypi.org/project/sqlcipher3/
    * If not available, fall back to https://pypi.org/project/pysqlcipher3/
    * For Python 2, https://pypi.org/project/pysqlcipher/ is used.

    .. warning:: The ``pysqlcipher3`` and ``pysqlcipher`` DBAPI drivers are no
       longer maintained; the ``sqlcipher3`` driver as of this writing appears
       to be current.  For future compatibility, any pysqlcipher-compatible DBAPI
       may be used as follows::

            import sqlcipher_compatible_driver

            from sqlalchemy import create_engine

            e = create_engine(
                "sqlite+pysqlcipher://:password@/dbname.db",
                module=sqlcipher_compatible_driver,
            )

    These drivers make use of the SQLCipher engine. This system essentially
    introduces new PRAGMA commands to SQLite which allows the setting of a
    passphrase and other encryption parameters, allowing the database file to be
    encrypted.


连接字符串
---------------

Connect Strings

.. tab:: 中文

    连接字符串的格式与 :mod:`~sqlalchemy.dialects.sqlite.pysqlite` 驱动完全一致，
    唯一区别是现在接受一个 "password" 字段，用于包含加密所需的密码短语::

        e = create_engine("sqlite+pysqlcipher://:testing@/foo.db")

    若需指定绝对路径，数据库名应以两个斜杠开头::

        e = create_engine("sqlite+pysqlcipher://:testing@//path/to/foo.db")

    SQLCipher 所支持的一系列附加加密相关的 PRAGMA（详见 https://www.zetetic.net/sqlcipher/sqlcipher-api/）
    可以通过查询字符串形式传入，并将在每个新连接上被调用。目前支持的参数包括
    ``cipher``、``kdf_iter``、``cipher_page_size`` 以及 ``cipher_use_hmac``::

        e = create_engine(
            "sqlite+pysqlcipher://:testing@/foo.db?cipher=aes-256-cfb&kdf_iter=64000"
        )

    .. warning:: 旧版本的 SQLAlchemy 并未处理 URL 中传入的加密相关 PRAGMA 参数，
       它们会被悄然忽略。这可能导致无法打开由旧版 SQLAlchemy 创建的数据库文件，
       如果加密选项不匹配则可能报错。

.. tab:: 英文

    The format of the connect string is in every way the same as that
    of the :mod:`~sqlalchemy.dialects.sqlite.pysqlite` driver, except that the
    "password" field is now accepted, which should contain a passphrase::

        e = create_engine("sqlite+pysqlcipher://:testing@/foo.db")

    For an absolute file path, two leading slashes should be used for the
    database name::

        e = create_engine("sqlite+pysqlcipher://:testing@//path/to/foo.db")

    A selection of additional encryption-related pragmas supported by SQLCipher
    as documented at https://www.zetetic.net/sqlcipher/sqlcipher-api/ can be passed
    in the query string, and will result in that PRAGMA being called for each
    new connection.  Currently, ``cipher``, ``kdf_iter``
    ``cipher_page_size`` and ``cipher_use_hmac`` are supported::

        e = create_engine(
            "sqlite+pysqlcipher://:testing@/foo.db?cipher=aes-256-cfb&kdf_iter=64000"
        )

    .. warning:: Previous versions of sqlalchemy did not take into consideration
       the encryption-related pragmas passed in the url string, that were silently
       ignored. This may cause errors when opening files saved by a
       previous sqlalchemy version if the encryption options do not match.


连接池行为
----------------

Pooling Behavior

.. tab:: 中文

    该驱动会修改 pysqlite 默认的连接池行为，如 :ref:`pysqlite_threading_pooling` 所述。
    观察发现 pysqlcipher 驱动的连接性能明显低于 pysqlite，
    很可能是由于加密开销的缘故，因此此方言默认使用 :class:`.SingletonThreadPool`
    而非 pysqlite 默认的 :class:`.NullPool`。如同以往，连接池的实现方式完全可以通过
    :paramref:`_sa.create_engine.poolclass` 参数进行配置；对于单线程使用场景，
    :class:`.StaticPool` 可能更合适；若希望防止长时间保持未加密的连接，
    可以选择 :class:`.NullPool`，但代价是每次新建连接的启动时间更长。

.. tab:: 英文

    The driver makes a change to the default pool behavior of pysqlite
    as described in :ref:`pysqlite_threading_pooling`.   The pysqlcipher driver
    has been observed to be significantly slower on connection than the
    pysqlite driver, most likely due to the encryption overhead, so the
    dialect here defaults to using the :class:`.SingletonThreadPool`
    implementation,
    instead of the :class:`.NullPool` pool used by pysqlite.  As always, the pool
    implementation is entirely configurable using the
    :paramref:`_sa.create_engine.poolclass` parameter; the :class:`.
    StaticPool` may
    be more feasible for single-threaded use, or :class:`.NullPool` may be used
    to prevent unencrypted connections from being held open for long periods of
    time, at the expense of slower startup time for new connections.


"""  # noqa

from .pysqlite import SQLiteDialect_pysqlite
from ... import pool


class SQLiteDialect_pysqlcipher(SQLiteDialect_pysqlite):
    driver = "pysqlcipher"
    supports_statement_cache = True

    pragmas = ("kdf_iter", "cipher", "cipher_page_size", "cipher_use_hmac")

    @classmethod
    def import_dbapi(cls):
        try:
            import sqlcipher3 as sqlcipher
        except ImportError:
            pass
        else:
            return sqlcipher

        from pysqlcipher3 import dbapi2 as sqlcipher

        return sqlcipher

    @classmethod
    def get_pool_class(cls, url):
        return pool.SingletonThreadPool

    def on_connect_url(self, url):
        super_on_connect = super().on_connect_url(url)

        # pull the info we need from the URL early.  Even though URL
        # is immutable, we don't want any in-place changes to the URL
        # to affect things
        passphrase = url.password or ""
        url_query = dict(url.query)

        def on_connect(conn):
            cursor = conn.cursor()
            cursor.execute('pragma key="%s"' % passphrase)
            for prag in self.pragmas:
                value = url_query.get(prag, None)
                if value is not None:
                    cursor.execute('pragma %s="%s"' % (prag, value))
            cursor.close()

            if super_on_connect:
                super_on_connect(conn)

        return on_connect

    def create_connect_args(self, url):
        plain_url = url._replace(password=None)
        plain_url = plain_url.difference_update_query(self.pragmas)
        return super().create_connect_args(plain_url)


dialect = SQLiteDialect_pysqlcipher
