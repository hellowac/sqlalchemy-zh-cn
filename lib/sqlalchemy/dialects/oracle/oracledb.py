# dialects/oracle/oracledb.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

r""".. dialect:: oracle+oracledb
    :name: python-oracledb
    :dbapi: oracledb
    :connectstring: oracle+oracledb://user:pass@hostname:port[/dbname][?service_name=<service>[&key=value&key=value...]]
    :url: https://oracle.github.io/python-oracledb/

描述
-----------

Description

.. tab:: 中文

    Python-oracledb 是 Oracle 数据库的 Python 驱动程序。它默认采用 "thin" 客户端模式，无需任何依赖项，并支持可选的 "thick" 模式，该模式使用 Oracle 客户端库。它支持包括双阶段事务和 Asyncio 在内的 SQLAlchemy 功能。

    Python-oracledb 是经过重命名和更新的 cx_Oracle 驱动程序。Oracle 不再在 cx_Oracle 命名空间中发布任何新版本。

    SQLAlchemy 的 ``oracledb`` 方言在同一个方言名称下同时提供同步（sync）和异步（async）实现。实际使用哪种版本，取决于引擎的创建方式：

    * 使用 ``oracle+oracledb://...`` 调用 :func:`_sa.create_engine` 会自动选择同步版本::

        from sqlalchemy import create_engine

        sync_engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost?service_name=FREEPDB1"
        )

    * 使用 ``oracle+oracledb://...`` 调用 :func:`_asyncio.create_async_engine` 会自动选择异步版本::

        from sqlalchemy.ext.asyncio import create_async_engine

        asyncio_engine = create_async_engine(
            "oracle+oracledb://scott:tiger@localhost?service_name=FREEPDB1"
        )

      你也可以显式使用 ``oracledb_async`` 后缀来指定异步版本::

          from sqlalchemy.ext.asyncio import create_async_engine

          asyncio_engine = create_async_engine(
              "oracle+oracledb_async://scott:tiger@localhost?service_name=FREEPDB1"
          )

    .. versionadded:: 2.0.25
       新增对 oracledb 异步版本的支持。

.. tab:: 英文

    Python-oracledb is the Oracle Database driver for Python. It features a default
    "thin" client mode that requires no dependencies, and an optional "thick" mode
    that uses Oracle Client libraries.  It supports SQLAlchemy features including
    two phase transactions and Asyncio.

    Python-oracle is the renamed, updated cx_Oracle driver. Oracle is no longer
    doing any releases in the cx_Oracle namespace.

    The SQLAlchemy ``oracledb`` dialect provides both a sync and an async
    implementation under the same dialect name. The proper version is
    selected depending on how the engine is created:

    * calling :func:`_sa.create_engine` with ``oracle+oracledb://...`` will
      automatically select the sync version::

        from sqlalchemy import create_engine

        sync_engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost?service_name=FREEPDB1"
        )

    * calling :func:`_asyncio.create_async_engine` with ``oracle+oracledb://...``
      will automatically select the async version::

        from sqlalchemy.ext.asyncio import create_async_engine

        asyncio_engine = create_async_engine(
            "oracle+oracledb://scott:tiger@localhost?service_name=FREEPDB1"
        )

      The asyncio version of the dialect may also be specified explicitly using the
      ``oracledb_async`` suffix::

          from sqlalchemy.ext.asyncio import create_async_engine

          asyncio_engine = create_async_engine(
              "oracle+oracledb_async://scott:tiger@localhost?service_name=FREEPDB1"
          )

    .. versionadded:: 2.0.25 added support for the async version of oracledb.

Thick模式支持
------------------

Thick mode support

.. tab:: 中文

    默认情况下，python-oracledb 驱动以 "thin" 模式运行，无需安装 Oracle 客户端库。该驱动还支持使用 Oracle 客户端库的 "thick" 模式，以获取如 Oracle Application Continuity 等高级功能。

    要启用 thick 模式，可显式调用 `oracledb.init_oracle_client() <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.init_oracle_client>`_，或在 :func:`_sa.create_engine` 中传入 ``thick_mode=True``。若需为 ``init_oracle_client()`` 传递自定义参数（如 ``lib_dir`` 路径），可以传入一个字典，例如::

        engine = sa.create_engine(
            "oracle+oracledb://...",
            thick_mode={
                "lib_dir": "/path/to/oracle/client/lib",
                "config_dir": "/path/to/network_config_file_directory",
                "driver_name": "my-app : 1.0.0",
            },
        )

    注意：仅在 macOS 或 Windows 上指定 ``lib_dir`` 路径。在 Linux 上其行为可能不会如预期。

    .. seealso::

        python-oracledb 文档
        `启用 python-oracledb Thick 模式 <https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#enabling-python-oracledb-thick-mode>`_

.. tab:: 英文

    By default, the python-oracledb driver runs in a "thin" mode that does not
    require Oracle Client libraries to be installed. The driver also supports a
    "thick" mode that uses Oracle Client libraries to get functionality such as
    Oracle Application Continuity.

    To enable thick mode, call `oracledb.init_oracle_client()
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.init_oracle_client>`_
    explicitly, or pass the parameter ``thick_mode=True`` to
    :func:`_sa.create_engine`. To pass custom arguments to
    ``init_oracle_client()``, like the ``lib_dir`` path, a dict may be passed, for
    example::

        engine = sa.create_engine(
            "oracle+oracledb://...",
            thick_mode={
                "lib_dir": "/path/to/oracle/client/lib",
                "config_dir": "/path/to/network_config_file_directory",
                "driver_name": "my-app : 1.0.0",
            },
        )

    Note that passing a ``lib_dir`` path should only be done on macOS or
    Windows. On Linux it does not behave as you might expect.

    .. seealso::

        python-oracledb documentation `Enabling python-oracledb Thick mode
        <https://python-oracledb.readthedocs.io/en/latest/user_guide/initialization.html#enabling-python-oracledb-thick-mode>`_

连接到 Oracle 数据库
-----------------------------

Connecting to Oracle Database

.. tab:: 中文

    python-oracledb 提供了多种方式来指定目标数据库。该方言可以解析多种 URL 格式。

    给定目标数据库的主机名、端口和服务名，可以使用 ``service_name`` 查询参数在 SQLAlchemy 中进行连接::

        engine = create_engine(
            "oracle+oracledb://scott:tiger@hostname:port?service_name=myservice"
        )

.. tab:: 英文

    python-oracledb provides several methods of indicating the target database.
    The dialect translates from a series of different URL forms.

    Given the hostname, port and service name of the target database, you can
    connect in SQLAlchemy using the ``service_name`` query string parameter::

        engine = create_engine(
            "oracle+oracledb://scott:tiger@hostname:port?service_name=myservice"
        )

使用 Easy Connect 字符串连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting with Easy Connect strings

.. tab:: 中文

    你也可以将任何有效的 python-oracledb 连接字符串作为 ``dsn`` 关键字的值，传入 :paramref:`_sa.create_engine.connect_args` 字典中。参见 python-oracledb 文档
    `Oracle Net Services 连接字符串 <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#oracle-net-services-connection-strings>`_。

    例如，若希望使用 `Easy Connect 字符串 <https://download.oracle.com/ocomdocs/global/Oracle-Net-Easy-Connect-Plus.pdf>`_，并设置连接超时为 30 秒（防止网络无法连接时卡顿），以及 60 秒的 keep-alive（避免空闲连接被防火墙终止）::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "hostname:port/myservice?transport_connect_timeout=30&expire_time=60",
            },
        )

    Oracle 数据库在其发展过程中增强了 Easy Connect 语法。请查阅与你数据库版本匹配的文档。当前文档见
    `理解 Easy Connect 命名方法 <https://www.oracle.com/pls/topic/lookup?ctx=dblatest&id=GUID-B0437826-43C1-49EC-A94D-B650B6A4A6EE>`_。

    通用语法类似于：

    .. sourcecode:: text

        [[protocol:]//]host[:port][/[service_name]][?parameter_name=value{&parameter_name=value}]

    请注意，虽然 SQLAlchemy 的 URL 语法 ``hostname:port/dbname`` 看起来与 Oracle 的 Easy Connect 类似，但实际上它们是不同的。SQLAlchemy 的 URL 要求 ``dbname`` 组件是系统标识符（SID）::

        engine = create_engine("oracle+oracledb://scott:tiger@hostname:port/sid")

    Easy Connect 语法不支持 SID。它使用服务名（service name），这是连接 Oracle 数据库的首选方式。

.. tab:: 英文

    You can pass any valid python-oracledb connection string as the ``dsn`` key
    value in a :paramref:`_sa.create_engine.connect_args` dictionary.  See
    python-oracledb documentation `Oracle Net Services Connection Strings
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#oracle-net-services-connection-strings>`_.

    For example to use an `Easy Connect string
    <https://download.oracle.com/ocomdocs/global/Oracle-Net-Easy-Connect-Plus.pdf>`_
    with a timeout to prevent connection establishment from hanging if the network
    transport to the database cannot be establishd in 30 seconds, and also setting
    a keep-alive time of 60 seconds to stop idle network connections from being
    terminated by a firewall::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "hostname:port/myservice?transport_connect_timeout=30&expire_time=60",
            },
        )

    The Easy Connect syntax has been enhanced during the life of Oracle Database.
    Review the documentation for your database version.  The current documentation
    is at `Understanding the Easy Connect Naming Method
    <https://www.oracle.com/pls/topic/lookup?ctx=dblatest&id=GUID-B0437826-43C1-49EC-A94D-B650B6A4A6EE>`_.

    The general syntax is similar to:

    .. sourcecode:: text

        [[protocol:]//]host[:port][/[service_name]][?parameter_name=value{&parameter_name=value}]

    Note that although the SQLAlchemy URL syntax ``hostname:port/dbname`` looks
    like Oracle's Easy Connect syntax, it is different. SQLAlchemy's URL requires a
    system identifier (SID) for the ``dbname`` component::

        engine = create_engine("oracle+oracledb://scott:tiger@hostname:port/sid")

    Easy Connect syntax does not support SIDs. It uses services names, which are
    the preferred choice for connecting to Oracle Database.

传递 python-oracledb 连接参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Passing python-oracledb connect arguments

.. tab:: 中文

    其他 python-oracledb 驱动的 `连接选项
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.connect>`_
    可以通过 ``connect_args`` 传递。例如::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "hostname:port/myservice",
                "events": True,
                "mode": oracledb.AUTH_MODE_SYSDBA,
            },
        )

.. tab:: 英文

    Other python-oracledb driver `connection options
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.connect>`_
    can be passed in ``connect_args``.  For example::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "hostname:port/myservice",
                "events": True,
                "mode": oracledb.AUTH_MODE_SYSDBA,
            },
        )

使用 tnsnames.ora TNS 别名连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting with tnsnames.ora TNS aliases

.. tab:: 中文

    如果未提供端口、数据库名称或服务名，方言将使用 Oracle 数据库 DSN "连接字符串"。该方式会将 URL 中的 "hostname" 部分作为数据源名称。例如，如果 ``tnsnames.ora`` 文件中包含如下的 `TNS 别名
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#tns-aliases-for-connection-strings>`_
    ``myalias``：

    .. sourcecode:: text

        myalias =
        (DESCRIPTION =
            (ADDRESS = (PROTOCOL = TCP)(HOST = mymachine.example.com)(PORT = 1521))
            (CONNECT_DATA =
            (SERVER = DEDICATED)
            (SERVICE_NAME = orclpdb1)
            )
        )

    当 URL 中的 hostname 部分为 ``myalias`` 且未指定端口、数据库名或 ``service_name`` 时，python-oracledb 方言将连接到此数据库服务::

        engine = create_engine("oracle+oracledb://scott:tiger@myalias")

.. tab:: 英文

    If no port, database name, or service name is provided, the dialect will use an
    Oracle Database DSN "connection string".  This takes the "hostname" portion of
    the URL as the data source name.  For example, if the ``tnsnames.ora`` file
    contains a `TNS Alias
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#tns-aliases-for-connection-strings>`_
    of ``myalias`` as below:

    .. sourcecode:: text

        myalias =
        (DESCRIPTION =
            (ADDRESS = (PROTOCOL = TCP)(HOST = mymachine.example.com)(PORT = 1521))
            (CONNECT_DATA =
            (SERVER = DEDICATED)
            (SERVICE_NAME = orclpdb1)
            )
        )

    The python-oracledb dialect connects to this database service when ``myalias`` is the
    hostname portion of the URL, without specifying a port, database name or
    ``service_name``::

        engine = create_engine("oracle+oracledb://scott:tiger@myalias")

连接到 Oracle 自治数据库
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting to Oracle Autonomous Database

.. tab:: 中文

    使用 Oracle Autonomous Database 的用户应使用上述 TNS 别名 URL，或将 TNS 别名作为 ``dsn`` 键值传入
    :paramref:`_sa.create_engine.connect_args` 字典中。

    如果 Oracle Autonomous Database 配置为使用双向 TLS（"mTLS"）连接，则需要额外配置，详见 `连接到 Oracle Cloud Autonomous Databases
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#connecting-to-oracle-cloud-autonomous-databases>`_。简而言之，Thick 模式的用户应配置文件路径，并在 ``sqlnet.ora`` 中正确设置钱包路径::

        e = create_engine(
            "oracle+oracledb://@",
            thick_mode={
                # 包含 tnsnames.ora 和 cwallet.so 的目录
                "config_dir": "/opt/oracle/wallet_dir",
            },
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "mydb_high",
            },
        )

    Thin 模式下的 mTLS 用户应在创建引擎时提供相应目录和 PEM 钱包密码，示例如下::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "mydb_high",
                "config_dir": "/opt/oracle/wallet_dir",  # 包含 tnsnames.ora 的目录
                "wallet_location": "/opt/oracle/wallet_dir",  # 包含 ewallet.pem 的目录
                "wallet_password": "top secret",  # PEM 文件的密码
            },
        )

    通常情况下，``config_dir`` 和 ``wallet_location`` 是同一个目录，即解压 Oracle Autonomous Database 钱包 zip 文件的路径。请注意应保护该目录。

.. tab:: 英文

    Users of Oracle Autonomous Database should use either use the TNS Alias URL
    shown above, or pass the TNS Alias as the ``dsn`` key value in a
    :paramref:`_sa.create_engine.connect_args` dictionary.

    If Oracle Autonomous Database is configured for mutual TLS ("mTLS")
    connections, then additional configuration is required as shown in `Connecting
    to Oracle Cloud Autonomous Databases
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#connecting-to-oracle-cloud-autonomous-databases>`_. In
    summary, Thick mode users should configure file locations and set the wallet
    path in ``sqlnet.ora`` appropriately::

        e = create_engine(
            "oracle+oracledb://@",
            thick_mode={
                # directory containing tnsnames.ora and cwallet.so
                "config_dir": "/opt/oracle/wallet_dir",
            },
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "mydb_high",
            },
        )

    Thin mode users of mTLS should pass the appropriate directories and PEM wallet
    password when creating the engine, similar to::

        e = create_engine(
            "oracle+oracledb://@",
            connect_args={
                "user": "scott",
                "password": "tiger",
                "dsn": "mydb_high",
                "config_dir": "/opt/oracle/wallet_dir",  # directory containing tnsnames.ora
                "wallet_location": "/opt/oracle/wallet_dir",  # directory containing ewallet.pem
                "wallet_password": "top secret",  # password for the PEM file
            },
        )

    Typically ``config_dir`` and ``wallet_location`` are the same directory, which
    is where the Oracle Autonomous Database wallet zip file was extracted.  Note
    this directory should be protected.

连接池
------------------

Connection Pooling

.. tab:: 中文

    具有多个并发用户的应用应使用连接池。对于长时间运行但不频繁使用连接的单用户应用，使用最小连接池也会带来好处。

    python-oracledb 驱动提供了自身的连接池实现，可替代 SQLAlchemy 的连接池功能。该连接池支持高可用特性，如死连接检测、计划内数据库停机时的连接抽取（draining）、Oracle Application Continuity 和 Transparent Application Continuity，以及对 `Database Resident Connection Pooling（DRCP）
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#database-resident-connection-pooling-drcp>`_ 的支持。

    要使用 python-oracledb 的连接池，可通过 :paramref:`_sa.create_engine.creator` 参数传入一个返回新连接的函数，并将
    :paramref:`_sa.create_engine.pool_class` 设置为 ``NullPool``，以禁用 SQLAlchemy 自带的连接池::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # 取消注释以启用可选的 python-oracledb Thick 模式。
        # 请参考 python-oracledb 文档，使用合适的参数
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
        )
        engine = create_engine(
            "oracle+oracledb://", creator=pool.acquire, poolclass=NullPool
        )

    之后可正常使用该引擎。连接池将在内部由 python-oracledb 管理::

        with engine.connect() as conn:
            print(conn.scalar(text("select 1 from dual")))

    有关创建连接池时可用参数，请参阅 python-oracledb 文档中 `oracledb.create_pool()
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.create_pool>`_ 的说明。

.. tab:: 英文

    Applications with multiple concurrent users should use connection pooling. A
    minimal sized connection pool is also beneficial for long-running, single-user
    applications that do not frequently use a connection.

    The python-oracledb driver provides its own connection pool implementation that
    may be used in place of SQLAlchemy's pooling functionality.  The driver pool
    gives support for high availability features such as dead connection detection,
    connection draining for planned database downtime, support for Oracle
    Application Continuity and Transparent Application Continuity, and gives
    support for `Database Resident Connection Pooling (DRCP)
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#database-resident-connection-pooling-drcp>`_.

    To take advantage of python-oracledb's pool, use the
    :paramref:`_sa.create_engine.creator` parameter to provide a function that
    returns a new connection, along with setting
    :paramref:`_sa.create_engine.pool_class` to ``NullPool`` to disable
    SQLAlchemy's pooling::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # Uncomment to use the optional python-oracledb Thick mode.
        # Review the python-oracledb doc for the appropriate parameters
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
        )
        engine = create_engine(
            "oracle+oracledb://", creator=pool.acquire, poolclass=NullPool
        )

    The above engine may then be used normally. Internally, python-oracledb handles
    connection pooling::

        with engine.connect() as conn:
            print(conn.scalar(text("select 1 from dual")))

    Refer to the python-oracledb documentation for `oracledb.create_pool()
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#oracledb.create_pool>`_
    for the arguments that can be used when creating a connection pool.

.. _drcp:

使用 Oracle 数据库驻留连接池 (DRCP)
--------------------------------------------------------

Using Oracle Database Resident Connection Pooling (DRCP)

.. tab:: 中文

    使用 Oracle 数据库的 Database Resident Connection Pooling（DRCP）时，最佳实践是指定连接类（connection class）和 "purity"。参见 `python-oracledb 的 DRCP 文档
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#database-resident-connection-pooling-drcp>`_。示例如下::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # 取消注释以启用可选的 python-oracledb Thick 模式。
        # 请参考 python-oracledb 文档，使用合适的参数
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
            cclass="MYCLASS",
            purity=oracledb.PURITY_SELF,
        )
        engine = create_engine(
            "oracle+oracledb://", creator=pool.acquire, poolclass=NullPool
        )

    之后即可正常使用该引擎，python-oracledb 管理应用连接池，Oracle 数据库使用 DRCP::

        with engine.connect() as conn:
            print(conn.scalar(text("select 1 from dual")))

    如果希望为不同连接使用不同的连接类或 purity，可封装 ``pool.acquire()``::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # 取消注释以启用 python-oracledb Thick 模式。
        # 请参考 python-oracledb 文档，使用合适的参数
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
            cclass="MYCLASS",
            purity=oracledb.PURITY_SELF,
        )


        def creator():
            return pool.acquire(cclass="MYOTHERCLASS", purity=oracledb.PURITY_NEW)


        engine = create_engine(
            "oracle+oracledb://", creator=creator, poolclass=NullPool
        )

.. tab:: 英文

    When using Oracle Database's Database Resident Connection Pooling (DRCP), the
    best practice is to specify a connection class and "purity". Refer to the
    `python-oracledb documentation on DRCP
    <https://python-oracledb.readthedocs.io/en/latest/user_guide/connection_handling.html#database-resident-connection-pooling-drcp>`_.
    For example::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # Uncomment to use the optional python-oracledb Thick mode.
        # Review the python-oracledb doc for the appropriate parameters
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
            cclass="MYCLASS",
            purity=oracledb.PURITY_SELF,
        )
        engine = create_engine(
            "oracle+oracledb://", creator=pool.acquire, poolclass=NullPool
        )

    The above engine may then be used normally where python-oracledb handles
    application connection pooling and Oracle Database additionally uses DRCP::

        with engine.connect() as conn:
            print(conn.scalar(text("select 1 from dual")))

    If you wish to use different connection classes or purities for different
    connections, then wrap ``pool.acquire()``::

        import oracledb
        from sqlalchemy import create_engine
        from sqlalchemy import text
        from sqlalchemy.pool import NullPool

        # Uncomment to use python-oracledb Thick mode.
        # Review the python-oracledb doc for the appropriate parameters
        # oracledb.init_oracle_client(<your parameters>)

        pool = oracledb.create_pool(
            user="scott",
            password="tiger",
            dsn="localhost:1521/freepdb1",
            min=1,
            max=4,
            increment=1,
            cclass="MYCLASS",
            purity=oracledb.PURITY_SELF,
        )


        def creator():
            return pool.acquire(cclass="MYOTHERCLASS", purity=oracledb.PURITY_NEW)


        engine = create_engine(
            "oracle+oracledb://", creator=creator, poolclass=NullPool
        )

驱动程序外部 SQLAlchemy oracledb 方言使用的引擎选项
--------------------------------------------------------------------------------

Engine Options consumed by the SQLAlchemy oracledb dialect outside of the driver

.. tab:: 中文

    SQLAlchemy 的 oracledb 方言还支持一些由自身消费的选项。这些选项始终通过 :func:`_sa.create_engine` 直接传入，例如::

        e = create_engine("oracle+oracledb://user:pass@tnsalias", arraysize=500)

    oracledb 方言所支持的参数如下：

    * ``arraysize`` - 设置驱动的 cursor.arraysize 值。默认为 ``None``，表示使用驱动的默认值 100。
    此设置控制在获取行时缓冲的行数，若在返回大量数据的查询中调高此值，可能会显著提升性能。

    .. versionchanged:: 2.0.26 - 默认值由 50 更改为 None，以使用驱动自身的默认值。

    * ``auto_convert_lobs`` - 默认为 True；详见 :ref:`oracledb_lob`。

    * ``coerce_to_decimal`` - 详见 :ref:`oracledb_numeric`。

    * ``encoding_errors`` - 详见 :ref:`oracledb_unicode_encoding_errors`。

.. tab:: 英文

    There are also options that are consumed by the SQLAlchemy oracledb dialect
    itself.  These options are always passed directly to :func:`_sa.create_engine`,
    such as::

        e = create_engine("oracle+oracledb://user:pass@tnsalias", arraysize=500)

    The parameters accepted by the oracledb dialect are as follows:

    * ``arraysize`` - set the driver cursor.arraysize value. It defaults to
      ``None``, indicating that the driver default value of 100 should be used.
      This setting controls how many rows are buffered when fetching rows, and can
      have a significant effect on performance if increased for queries that return
      large numbers of rows.

      .. versionchanged:: 2.0.26 - changed the default value from 50 to None,
        to use the default value of the driver itself.

    * ``auto_convert_lobs`` - defaults to True; See :ref:`oracledb_lob`.

    * ``coerce_to_decimal`` - see :ref:`oracledb_numeric` for detail.

    * ``encoding_errors`` - see :ref:`oracledb_unicode_encoding_errors` for detail.

.. _oracledb_unicode:

Unicode
-------

Unicode

.. tab:: 中文

    在 Python 3 下，所有 DBAPI 都以 Unicode 字符串为基础，字符串天然为 Unicode 类型。

.. tab:: 英文

    As is the case for all DBAPIs under Python 3, all strings are inherently Unicode strings.

确保客户端编码正确
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Ensuring the Correct Client Encoding

.. tab:: 中文

    在 python-oracledb 中，用于所有字符数据的编码为 "UTF-8"。

.. tab:: 英文

    In python-oracledb, the encoding used for all character data is "UTF-8".

Unicode 特定的列数据类型
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unicode-specific Column datatypes

.. tab:: 中文

    Core 表达式语言通过使用 :class:`.Unicode` 与 :class:`.UnicodeText` 数据类型来处理 Unicode 数据。
    默认情况下，这些类型分别对应于 Oracle 数据库的 VARCHAR2 和 CLOB 类型。
    当使用这些类型处理 Unicode 数据时，预期数据库应配置为支持 Unicode 的字符集，
    以便 VARCHAR2 和 CLOB 类型可以正确容纳数据。

    若 Oracle 数据库未配置为 Unicode 字符集，有两种替代方式：一是显式使用 :class:`_types.NCHAR` 和
    :class:`_oracle.NCLOB` 数据类型，二是向 :func:`_sa.create_engine` 传入参数 ``use_nchar_for_unicode=True``，
    此时 SQLAlchemy 方言将在使用 :class:`.Unicode` / :class:`.UnicodeText` 数据类型时，自动改用 NCHAR/NCLOB，而非默认的 VARCHAR/CLOB。

.. tab:: 英文

    The Core expression language handles unicode data by use of the
    :class:`.Unicode` and :class:`.UnicodeText` datatypes.  These types correspond
    to the VARCHAR2 and CLOB Oracle Database datatypes by default.  When using
    these datatypes with Unicode data, it is expected that the database is
    configured with a Unicode-aware character set so that the VARCHAR2 and CLOB
    datatypes can accommodate the data.

    In the case that Oracle Database is not configured with a Unicode character
    set, the two options are to use the :class:`_types.NCHAR` and
    :class:`_oracle.NCLOB` datatypes explicitly, or to pass the flag
    ``use_nchar_for_unicode=True`` to :func:`_sa.create_engine`, which will cause
    the SQLAlchemy dialect to use NCHAR/NCLOB for the :class:`.Unicode` /
    :class:`.UnicodeText` datatypes instead of VARCHAR/CLOB.

.. _oracledb_unicode_encoding_errors:

编码错误
^^^^^^^^^^^^^^^

Encoding Errors

.. tab:: 中文

    在较为少见的场景中，若 Oracle 数据库中的数据编码存在异常，方言提供了 ``encoding_errors`` 参数以控制 Unicode 解码时的错误处理行为。
    该参数的值将传入 Python 的 `decode
    <https://docs.python.org/3/library/stdtypes.html#bytes.decode>`_ 函数，
    并同时通过 python-oracledb 的 ``encodingErrors`` 参数传递给 ``Cursor.var()``，
    以及传递给 SQLAlchemy 自身的解码函数，因为 oracledb 方言在不同场景下可能会使用其中任意一个。

.. tab:: 英文

    For the unusual case that data in Oracle Database is present with a broken
    encoding, the dialect accepts a parameter ``encoding_errors`` which will be
    passed to Unicode decoding functions in order to affect how decoding errors are
    handled.  The value is ultimately consumed by the Python `decode
    <https://docs.python.org/3/library/stdtypes.html#bytes.decode>`_ function, and
    is passed both via python-oracledb's ``encodingErrors`` parameter consumed by
    ``Cursor.var()``, as well as SQLAlchemy's own decoding function, as the
    python-oracledb dialect makes use of both under different circumstances.

.. _oracledb_setinputsizes:

使用 setinputsizes 对 python-oracledb 数据绑定进行细粒度控制
-------------------------------------------------------------------------

Fine grained control over python-oracledb data binding with setinputsizes

.. tab:: 中文

    python-oracledb DBAPI 在设计上高度依赖 DBAPI 的 ``setinputsizes()`` 调用。
    该调用的作用是为即将绑定到 SQL 语句的 Python 参数设定相应的数据库数据类型。
    虽然几乎所有其他 DBAPI 都很少或根本不使用 ``setinputsizes()``，但 python-oracledb 的实现对此调用极为依赖，
    并且在某些场景下，SQLAlchemy 无法自动准确地判断应该如何绑定数据。
    部分设置可能会对性能产生显著影响，同时也会改变类型转换行为。

    **强烈建议** oracledb 方言的用户阅读 python-oracledb 所提供的 `数据库类型符号列表
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#database-types>`_。
    请注意，在某些情况下，使用这些类型可能会引发明显的性能下降。

    在 SQLAlchemy 一侧，可以使用 :meth:`.DialectEvents.do_setinputsizes` 事件来实现对 ``setinputsizes()`` 过程的运行时观察（如日志记录），
    或完全按语句级别控制其行为。

.. tab:: 英文

    The python-oracle DBAPI has a deep and fundamental reliance upon the usage of
    the DBAPI ``setinputsizes()`` call.  The purpose of this call is to establish
    the datatypes that are bound to a SQL statement for Python values being passed
    as parameters.  While virtually no other DBAPI assigns any use to the
    ``setinputsizes()`` call, the python-oracledb DBAPI relies upon it heavily in
    its interactions with the Oracle Database, and in some scenarios it is not
    possible for SQLAlchemy to know exactly how data should be bound, as some
    settings can cause profoundly different performance characteristics, while
    altering the type coercion behavior at the same time.

    Users of the oracledb dialect are **strongly encouraged** to read through
    python-oracledb's list of built-in datatype symbols at `Database Types
    <https://python-oracledb.readthedocs.io/en/latest/api_manual/module.html#database-types>`_
    Note that in some cases, significant performance degradation can occur when
    using these types vs. not.

    On the SQLAlchemy side, the :meth:`.DialectEvents.do_setinputsizes` event can
    be used both for runtime visibility (e.g. logging) of the setinputsizes step as
    well as to fully control how ``setinputsizes()`` is used on a per-statement
    basis.

示例 1 - 记录所有 setinputsizes 调用
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example 1 - logging all setinputsizes calls

.. tab:: 中文

    下列示例展示了如何从 SQLAlchemy 的角度记录在转换为原始 ``setinputsizes()`` 参数字典之前的中间值。该字典的键是 :class:`.BindParameter` 对象，每个对象具有 ``.key`` 和 ``.type`` 属性::

        from sqlalchemy import create_engine, event

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "do_setinputsizes")
        def _log_setinputsizes(inputsizes, cursor, statement, parameters, context):
            for bindparam, dbapitype in inputsizes.items():
                log.info(
                    "Bound parameter name: %s  SQLAlchemy type: %r DBAPI object: %s",
                    bindparam.key,
                    bindparam.type,
                    dbapitype,
                )

.. tab:: 英文

    The following example illustrates how to log the intermediary values from a
    SQLAlchemy perspective before they are converted to the raw ``setinputsizes()``
    parameter dictionary.  The keys of the dictionary are :class:`.BindParameter`
    objects which have a ``.key`` and a ``.type`` attribute::

        from sqlalchemy import create_engine, event

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "do_setinputsizes")
        def _log_setinputsizes(inputsizes, cursor, statement, parameters, context):
            for bindparam, dbapitype in inputsizes.items():
                log.info(
                    "Bound parameter name: %s  SQLAlchemy type: %r DBAPI object: %s",
                    bindparam.key,
                    bindparam.type,
                    dbapitype,
                )

示例 2 - 移除所有与 CLOB 的绑定
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example 2 - remove all bindings to CLOB

.. tab:: 中文

    出于性能考虑，SQLAlchemy 默认将 Oracle 数据库中的 ``Text`` 类型映射为 LOB 类型。该行为可如下修改::

        from sqlalchemy import create_engine, event
        from oracledb import CLOB

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "do_setinputsizes")
        def _remove_clob(inputsizes, cursor, statement, parameters, context):
            for bindparam, dbapitype in list(inputsizes.items()):
                if dbapitype is CLOB:
                    del inputsizes[bindparam]

.. tab:: 英文

    For performance, fetching LOB datatypes from Oracle Database is set by default
    for the ``Text`` type within SQLAlchemy.  This setting can be modified as
    follows::


        from sqlalchemy import create_engine, event
        from oracledb import CLOB

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "do_setinputsizes")
        def _remove_clob(inputsizes, cursor, statement, parameters, context):
            for bindparam, dbapitype in list(inputsizes.items()):
                if dbapitype is CLOB:
                    del inputsizes[bindparam]

.. _oracledb_lob:

LOB 数据类型
--------------

LOB Datatypes

.. tab:: 中文

    LOB 数据类型指的是“大对象”类型，如 CLOB、NCLOB 和 BLOB。Oracle 数据库可以高效地将这些类型作为单一缓冲区返回。SQLAlchemy 默认使用类型处理器（type handler）来完成此行为。

    若要禁用类型处理器并将 LOB 对象作为传统的带 ``read()`` 方法的缓冲对象返回，可在调用 :func:`_sa.create_engine` 时传入参数 ``auto_convert_lobs=False``。

.. tab:: 英文

    LOB datatypes refer to the "large object" datatypes such as CLOB, NCLOB and
    BLOB. Oracle Database can efficiently return these datatypes as a single
    buffer. SQLAlchemy makes use of type handlers to do this by default.

    To disable the use of the type handlers and deliver LOB objects as classic
    buffered objects with a ``read()`` method, the parameter
    ``auto_convert_lobs=False`` may be passed to :func:`_sa.create_engine`.

.. _oracledb_returning:

返回支持
-----------------

RETURNING Support

.. tab:: 中文

    oracledb 方言通过 OUT 参数实现了 RETURNING 功能，方言完全支持 RETURNING 子句。

.. tab:: 英文

    The oracledb dialect implements RETURNING using OUT parameters.  The dialect supports RETURNING fully.

两阶段事务支持
-----------------------------

Two Phase Transaction Support

.. tab:: 中文

    python-oracledb 完全支持两阶段事务（Thin 模式需 python-oracledb 2.3 及以上版本）。相关 API 可在 Core 层通过 :meth:`_engine.Connection.begin_twophase` 提供，
    也可通过 :paramref:`_orm.Session.twophase` 供 ORM 层透明使用。

    .. versionchanged:: 2.0.32 增加对两阶段事务的支持

.. tab:: 英文

    Two phase transactions are fully supported with python-oracledb. (Thin mode
    requires python-oracledb 2.3).  APIs for two phase transactions are provided at
    the Core level via :meth:`_engine.Connection.begin_twophase` and
    :paramref:`_orm.Session.twophase` for transparent ORM use.

    .. versionchanged:: 2.0.32 added support for two phase transactions

.. _oracledb_numeric:

精度数值
------------------

Precision Numerics

.. tab:: 中文

    SQLAlchemy 的数值类型可以以 Python 的 ``Decimal`` 对象或 float 对象的形式接收和返回数据。当使用 :class:`.Numeric` 类型或其子类（如 :class:`.Float`、:class:`_oracle.DOUBLE_PRECISION` 等）时，
    :paramref:`.Numeric.asdecimal` 标志决定了是否将返回值强制转换为 ``Decimal``，或以 float 对象返回。
    在 Oracle 数据库中，这一处理更为复杂，因为 ``NUMBER`` 类型在 "scale" 为零时也可以表示整数。
    为此，Oracle 特定的 :class:`_oracle.NUMBER` 类型也考虑到了此特性。

    oracledb 方言广泛使用连接级与游标级的 "outputtypehandler" 可调用对象，以按需对数值类型进行强制转换。
    这些处理器针对当前使用的 :class:`.Numeric` 类型的具体形式，也可用于不带 SQLAlchemy 类型对象的场景。
    已观察到某些场景下 Oracle 数据库返回的数值类型信息可能不完整或模糊，例如在多层子查询中嵌套的数值类型。
    类型处理器在所有场景下都尽力做出合理判断，在可能的情况下委托底层 python-oracledb DBAPI 做最终决定。

    当未使用任何类型对象（例如执行原始 SQL 字符串）时，将启用默认的 "outputtypehandler"，其通常会将指定了精度和小数位的数值以 Python 的 ``Decimal`` 对象返回。
    若因性能考虑希望禁用这种 Decimal 强制转换行为，可传入参数 ``coerce_to_decimal=False`` 给 :func:`_sa.create_engine`::

        engine = create_engine(
            "oracle+oracledb://scott:tiger@tnsalias", coerce_to_decimal=False
        )

    ``coerce_to_decimal`` 标志仅影响那些未与 :class:`.Numeric` 类型（或其子类）相关联的原始字符串 SQL 语句的返回结果。

    .. versionadded:: 2.0.0 添加对 python-oracledb 驱动的支持。

.. tab:: 英文

    SQLAlchemy's numeric types can handle receiving and returning values as Python
    ``Decimal`` objects or float objects.  When a :class:`.Numeric` object, or a
    subclass such as :class:`.Float`, :class:`_oracle.DOUBLE_PRECISION` etc. is in
    use, the :paramref:`.Numeric.asdecimal` flag determines if values should be
    coerced to ``Decimal`` upon return, or returned as float objects.  To make
    matters more complicated under Oracle Database, the ``NUMBER`` type can also
    represent integer values if the "scale" is zero, so the Oracle
    Database-specific :class:`_oracle.NUMBER` type takes this into account as well.

    The oracledb dialect makes extensive use of connection- and cursor-level
    "outputtypehandler" callables in order to coerce numeric values as requested.
    These callables are specific to the specific flavor of :class:`.Numeric` in
    use, as well as if no SQLAlchemy typing objects are present.  There are
    observed scenarios where Oracle Database may send incomplete or ambiguous
    information about the numeric types being returned, such as a query where the
    numeric types are buried under multiple levels of subquery.  The type handlers
    do their best to make the right decision in all cases, deferring to the
    underlying python-oracledb DBAPI for all those cases where the driver can make
    the best decision.

    When no typing objects are present, as when executing plain SQL strings, a
    default "outputtypehandler" is present which will generally return numeric
    values which specify precision and scale as Python ``Decimal`` objects.  To
    disable this coercion to decimal for performance reasons, pass the flag
    ``coerce_to_decimal=False`` to :func:`_sa.create_engine`::

        engine = create_engine(
            "oracle+oracledb://scott:tiger@tnsalias", coerce_to_decimal=False
        )

    The ``coerce_to_decimal`` flag only impacts the results of plain string
    SQL statements that are not otherwise associated with a :class:`.Numeric`
    SQLAlchemy type (or a subclass of such).

    .. versionadded:: 2.0.0 added support for the python-oracledb driver.

"""  # noqa

from __future__ import annotations

import collections
import re
from typing import Any
from typing import TYPE_CHECKING

from . import cx_oracle as _cx_oracle
from ... import exc
from ...connectors.asyncio import AsyncAdapt_dbapi_connection
from ...connectors.asyncio import AsyncAdapt_dbapi_cursor
from ...connectors.asyncio import AsyncAdapt_dbapi_ss_cursor
from ...engine import default
from ...util import await_

if TYPE_CHECKING:
    from oracledb import AsyncConnection
    from oracledb import AsyncCursor


class OracleExecutionContext_oracledb(_cx_oracle.OracleExecutionContext_cx_oracle):
    pass


class OracleDialect_oracledb(_cx_oracle.OracleDialect_cx_oracle):
    supports_statement_cache = True
    execution_ctx_cls = OracleExecutionContext_oracledb

    driver = "oracledb"
    _min_version = (1,)

    def __init__(
        self,
        auto_convert_lobs=True,
        coerce_to_decimal=True,
        arraysize=None,
        encoding_errors=None,
        thick_mode=None,
        **kwargs,
    ):
        super().__init__(
            auto_convert_lobs,
            coerce_to_decimal,
            arraysize,
            encoding_errors,
            **kwargs,
        )

        if self.dbapi is not None and (thick_mode or isinstance(thick_mode, dict)):
            kw = thick_mode if isinstance(thick_mode, dict) else {}
            self.dbapi.init_oracle_client(**kw)

    @classmethod
    def import_dbapi(cls):
        import oracledb

        return oracledb

    @classmethod
    def is_thin_mode(cls, connection):
        return connection.connection.dbapi_connection.thin

    @classmethod
    def get_async_dialect_cls(cls, url):
        return OracleDialectAsync_oracledb

    def _load_version(self, dbapi_module):
        version = (0, 0, 0)
        if dbapi_module is not None:
            m = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?", dbapi_module.version)
            if m:
                version = tuple(int(x) for x in m.group(1, 2, 3) if x is not None)
        self.oracledb_ver = version
        if self.oracledb_ver > (0, 0, 0) and self.oracledb_ver < self._min_version:
            raise exc.InvalidRequestError(
                f"oracledb version {self._min_version} and above are supported"
            )

    def do_begin_twophase(self, connection, xid):
        conn_xis = connection.connection.xid(*xid)
        connection.connection.tpc_begin(conn_xis)
        connection.connection.info["oracledb_xid"] = conn_xis

    def do_prepare_twophase(self, connection, xid):
        should_commit = connection.connection.tpc_prepare()
        connection.info["oracledb_should_commit"] = should_commit

    def do_rollback_twophase(self, connection, xid, is_prepared=True, recover=False):
        if recover:
            conn_xid = connection.connection.xid(*xid)
        else:
            conn_xid = None
        connection.connection.tpc_rollback(conn_xid)

    def do_commit_twophase(self, connection, xid, is_prepared=True, recover=False):
        conn_xid = None
        if not is_prepared:
            should_commit = connection.connection.tpc_prepare()
        elif recover:
            conn_xid = connection.connection.xid(*xid)
            should_commit = True
        else:
            should_commit = connection.info["oracledb_should_commit"]
        if should_commit:
            connection.connection.tpc_commit(conn_xid)

    def do_recover_twophase(self, connection):
        return [
            # oracledb seems to return bytes
            (
                fi,
                gti.decode() if isinstance(gti, bytes) else gti,
                bq.decode() if isinstance(bq, bytes) else bq,
            )
            for fi, gti, bq in connection.connection.tpc_recover()
        ]

    def _check_max_identifier_length(self, connection):
        if self.oracledb_ver >= (2, 5):
            max_len = connection.connection.max_identifier_length
            if max_len is not None:
                return max_len
        return super()._check_max_identifier_length(connection)


class AsyncAdapt_oracledb_cursor(AsyncAdapt_dbapi_cursor):
    _cursor: AsyncCursor
    __slots__ = ()

    @property
    def outputtypehandler(self):
        return self._cursor.outputtypehandler

    @outputtypehandler.setter
    def outputtypehandler(self, value):
        self._cursor.outputtypehandler = value

    def var(self, *args, **kwargs):
        return self._cursor.var(*args, **kwargs)

    def close(self):
        self._rows.clear()
        self._cursor.close()

    def setinputsizes(self, *args: Any, **kwargs: Any) -> Any:
        return self._cursor.setinputsizes(*args, **kwargs)

    def _aenter_cursor(self, cursor: AsyncCursor) -> AsyncCursor:
        try:
            return cursor.__enter__()
        except Exception as error:
            self._adapt_connection._handle_exception(error)

    async def _execute_async(self, operation, parameters):
        # override to not use mutex, oracledb already has a mutex

        if parameters is None:
            result = await self._cursor.execute(operation)
        else:
            result = await self._cursor.execute(operation, parameters)

        if self._cursor.description and not self.server_side:
            self._rows = collections.deque(await self._cursor.fetchall())
        return result

    async def _executemany_async(
        self,
        operation,
        seq_of_parameters,
    ):
        # override to not use mutex, oracledb already has a mutex
        return await self._cursor.executemany(operation, seq_of_parameters)


class AsyncAdapt_oracledb_ss_cursor(
    AsyncAdapt_dbapi_ss_cursor, AsyncAdapt_oracledb_cursor
):
    __slots__ = ()

    def close(self) -> None:
        if self._cursor is not None:
            self._cursor.close()
            self._cursor = None  # type: ignore


class AsyncAdapt_oracledb_connection(AsyncAdapt_dbapi_connection):
    _connection: AsyncConnection
    __slots__ = ()

    thin = True

    _cursor_cls = AsyncAdapt_oracledb_cursor
    _ss_cursor_cls = None

    @property
    def autocommit(self):
        return self._connection.autocommit

    @autocommit.setter
    def autocommit(self, value):
        self._connection.autocommit = value

    @property
    def outputtypehandler(self):
        return self._connection.outputtypehandler

    @outputtypehandler.setter
    def outputtypehandler(self, value):
        self._connection.outputtypehandler = value

    @property
    def version(self):
        return self._connection.version

    @property
    def stmtcachesize(self):
        return self._connection.stmtcachesize

    @stmtcachesize.setter
    def stmtcachesize(self, value):
        self._connection.stmtcachesize = value

    @property
    def max_identifier_length(self):
        return self._connection.max_identifier_length

    def cursor(self):
        return AsyncAdapt_oracledb_cursor(self)

    def ss_cursor(self):
        return AsyncAdapt_oracledb_ss_cursor(self)

    def xid(self, *args: Any, **kwargs: Any) -> Any:
        return self._connection.xid(*args, **kwargs)

    def tpc_begin(self, *args: Any, **kwargs: Any) -> Any:
        return await_(self._connection.tpc_begin(*args, **kwargs))

    def tpc_commit(self, *args: Any, **kwargs: Any) -> Any:
        return await_(self._connection.tpc_commit(*args, **kwargs))

    def tpc_prepare(self, *args: Any, **kwargs: Any) -> Any:
        return await_(self._connection.tpc_prepare(*args, **kwargs))

    def tpc_recover(self, *args: Any, **kwargs: Any) -> Any:
        return await_(self._connection.tpc_recover(*args, **kwargs))

    def tpc_rollback(self, *args: Any, **kwargs: Any) -> Any:
        return await_(self._connection.tpc_rollback(*args, **kwargs))


class OracledbAdaptDBAPI:
    def __init__(self, oracledb) -> None:
        self.oracledb = oracledb

        for k, v in self.oracledb.__dict__.items():
            if k != "connect":
                self.__dict__[k] = v

    def connect(self, *arg, **kw):
        creator_fn = kw.pop("async_creator_fn", self.oracledb.connect_async)
        return AsyncAdapt_oracledb_connection(self, await_(creator_fn(*arg, **kw)))


class OracleExecutionContextAsync_oracledb(OracleExecutionContext_oracledb):
    # restore default create cursor
    create_cursor = default.DefaultExecutionContext.create_cursor

    def create_default_cursor(self):
        # copy of OracleExecutionContext_cx_oracle.create_cursor
        c = self._dbapi_connection.cursor()
        if self.dialect.arraysize:
            c.arraysize = self.dialect.arraysize

        return c

    def create_server_side_cursor(self):
        c = self._dbapi_connection.ss_cursor()
        if self.dialect.arraysize:
            c.arraysize = self.dialect.arraysize

        return c


class OracleDialectAsync_oracledb(OracleDialect_oracledb):
    is_async = True
    supports_server_side_cursors = True
    supports_statement_cache = True
    execution_ctx_cls = OracleExecutionContextAsync_oracledb

    _min_version = (2,)

    # thick_mode mode is not supported by asyncio, oracledb will raise
    @classmethod
    def import_dbapi(cls):
        import oracledb

        return OracledbAdaptDBAPI(oracledb)

    def get_driver_connection(self, connection):
        return connection._connection


dialect = OracleDialect_oracledb
dialect_async = OracleDialectAsync_oracledb
