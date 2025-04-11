# dialects/mssql/pyodbc.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

r"""
.. dialect:: mssql+pyodbc
    :name: PyODBC
    :dbapi: pyodbc
    :connectstring: mssql+pyodbc://<username>:<password>@<dsnname>
    :url: https://pypi.org/project/pyodbc/

连接到 PyODBC
--------------------

Connecting to PyODBC

.. tab:: 中文

    此处的 URL 将被转换为 PyODBC 连接字符串，如 `ConnectionStrings <https://code.google.com/p/pyodbc/wiki/ConnectionStrings>`_ 中所述。

.. tab:: 英文

    The URL here is to be translated to PyODBC connection strings, as detailed in `ConnectionStrings <https://code.google.com/p/pyodbc/wiki/ConnectionStrings>`_.

DSN 连接
^^^^^^^^^^^^^^^

DSN Connections

.. tab:: 中文

    ODBC 中的 DSN 连接意味着客户端计算机上配置了一个预先存在的 ODBC 数据源。应用程序随后指定该数据源的名称，该名称包含诸如使用的特定 ODBC 驱动程序以及数据库的网络地址等详细信息。假设客户端已配置数据源，基本的基于 DSN 的连接如下所示::

        engine = create_engine("mssql+pyodbc://scott:tiger@some_dsn")

    上述代码将把以下连接字符串传递给 PyODBC：

    .. sourcecode:: text

        DSN=some_dsn;UID=scott;PWD=tiger

    如果省略用户名和密码，DSN 形式也会将 ``Trusted_Connection=yes`` 指令添加到 ODBC 字符串中。

.. tab:: 英文

    A DSN connection in ODBC means that a pre-existing ODBC datasource is
    configured on the client machine.   The application then specifies the name
    of this datasource, which encompasses details such as the specific ODBC driver
    in use as well as the network address of the database.   Assuming a datasource
    is configured on the client, a basic DSN-based connection looks like::

        engine = create_engine("mssql+pyodbc://scott:tiger@some_dsn")

    Which above, will pass the following connection string to PyODBC:

    .. sourcecode:: text

        DSN=some_dsn;UID=scott;PWD=tiger

    If the username and password are omitted, the DSN form will also add
    the ``Trusted_Connection=yes`` directive to the ODBC string.

主机名连接
^^^^^^^^^^^^^^^^^^^^

Hostname Connections

.. tab:: 中文

    PyODBC 也支持基于主机名的连接。这些连接通常比 DSN 更容易使用，另外，它们的一个优点是可以在 URL 中本地指定要连接的具体数据库名称，而不是将其作为数据源配置的一部分固定。

    使用主机名连接时，必须在 URL 的查询参数中指定驱动程序名称。由于这些名称通常包含空格，因此名称必须进行 URL 编码，即使用加号代替空格::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@myhost:port/databasename?driver=ODBC+Driver+17+for+SQL+Server"
        )

    ``driver`` 关键字对 pyodbc 方言至关重要，必须小写书写。

    查询字符串中传递的任何其他名称都会传递到 pyodbc 连接字符串中，如 ``authentication``、``TrustServerCertificate`` 等。多个关键字参数必须用和号（``&``）分隔；当生成内部 pyodbc 连接字符串时，这些参数会被转换为分号::

        e = create_engine(
            "mssql+pyodbc://scott:tiger@mssql2017:1433/test?"
            "driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
            "&authentication=ActiveDirectoryIntegrated"
        )

    等效的 URL 可以使用 :class:`_sa.engine.URL` 构建::

        from sqlalchemy.engine import URL

        connection_url = URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="mssql2017",
            port=1433,
            database="test",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "TrustServerCertificate": "yes",
                "authentication": "ActiveDirectoryIntegrated",
            },
        )

.. tab:: 英文

    Hostname-based connections are also supported by pyodbc.  These are often
    easier to use than a DSN and have the additional advantage that the specific
    database name to connect towards may be specified locally in the URL, rather
    than it being fixed as part of a datasource configuration.

    When using a hostname connection, the driver name must also be specified in the
    query parameters of the URL.  As these names usually have spaces in them, the
    name must be URL encoded which means using plus signs for spaces::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@myhost:port/databasename?driver=ODBC+Driver+17+for+SQL+Server"
        )

    The ``driver`` keyword is significant to the pyodbc dialect and must be
    specified in lowercase.

    Any other names passed in the query string are passed through in the pyodbc
    connect string, such as ``authentication``, ``TrustServerCertificate``, etc.
    Multiple keyword arguments must be separated by an ampersand (``&``); these
    will be translated to semicolons when the pyodbc connect string is generated
    internally::

        e = create_engine(
            "mssql+pyodbc://scott:tiger@mssql2017:1433/test?"
            "driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
            "&authentication=ActiveDirectoryIntegrated"
        )

    The equivalent URL can be constructed using :class:`_sa.engine.URL`::

        from sqlalchemy.engine import URL

        connection_url = URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="mssql2017",
            port=1433,
            database="test",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "TrustServerCertificate": "yes",
                "authentication": "ActiveDirectoryIntegrated",
            },
        )

传递精确的 Pyodbc 字符串
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Pass through exact Pyodbc string

.. tab:: 中文

    也可以直接发送 PyODBC 格式的连接字符串，正如在 `PyODBC 文档
    <https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-databases>`_ 中所指定，使用参数 ``odbc_connect``。使用 :class:`_sa.engine.URL` 对象可以简化此操作::

        from sqlalchemy.engine import URL

        connection_string = "DRIVER={SQL Server Native Client 10.0};SERVER=dagger;DATABASE=test;UID=user;PWD=password"
        connection_url = URL.create(
            "mssql+pyodbc", query={"odbc_connect": connection_string}
        )

        engine = create_engine(connection_url)

.. tab:: 英文

    A PyODBC connection string can also be sent in pyodbc's format directly, as
    specified in `the PyODBC documentation
    <https://github.com/mkleehammer/pyodbc/wiki/Connecting-to-databases>`_,
    using the parameter ``odbc_connect``.  A :class:`_sa.engine.URL` object
    can help make this easier::

        from sqlalchemy.engine import URL

        connection_string = "DRIVER={SQL Server Native Client 10.0};SERVER=dagger;DATABASE=test;UID=user;PWD=password"
        connection_url = URL.create(
            "mssql+pyodbc", query={"odbc_connect": connection_string}
        )

        engine = create_engine(connection_url)

.. _mssql_pyodbc_access_tokens:

使用访问令牌连接到数据库
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Connecting to databases with access tokens

.. tab:: 中文

    一些数据库服务器仅接受访问令牌进行登录。例如，SQL Server 允许使用 Azure Active Directory 令牌连接到数据库。这需要使用 ``azure-identity`` 库创建凭证对象。有关身份验证步骤的更多信息，请参见 `Microsoft 文档
    <https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?tabs=bash>`_。

    获取引擎后，每次请求连接时需要将凭证发送给 ``pyodbc.connect``。一种方法是在引擎上设置事件监听器，将凭证令牌添加到方言的连接调用中。这在 :ref:`engines_dynamic_tokens` 中有更广泛的讨论。对于 SQL Server，凭证作为 ODBC 连接属性传递，数据结构 `由 Microsoft 描述
    <https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory#authenticating-with-an-access-token>`_。

    以下代码片段将创建一个使用 Azure 凭证连接到 Azure SQL 数据库的引擎::

        import struct
        from sqlalchemy import create_engine, event
        from sqlalchemy.engine.url import URL
        from azure import identity

        # 访问令牌的连接选项，定义在 msodbcsql.h 中
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        TOKEN_URL = "https://database.windows.net/"  # 任何 Azure SQL 数据库的令牌 URL

        connection_string = "mssql+pyodbc://@my-server.database.windows.net/myDb?driver=ODBC+Driver+17+for+SQL+Server"

        engine = create_engine(connection_string)

        azure_credentials = identity.DefaultAzureCredential()


        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            # 删除 SQLAlchemy 添加的 "Trusted_Connection" 参数
            cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")

            # 创建令牌凭证
            raw_token = azure_credentials.get_token(TOKEN_URL).token.encode(
                "utf-16-le"
            )
            token_struct = struct.pack(
                f"<I{len(raw_token)}s", len(raw_token), raw_token
            )

            # 将其应用于关键字参数
            cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    .. tip::

        ``Trusted_Connection`` 令牌当前由 SQLAlchemy pyodbc 方言在没有用户名或密码时添加。根据 Microsoft 的
        `Azure 访问令牌文档
        <https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory#authenticating-with-an-access-token>`_，
        需要删除它，说明当使用访问令牌时，连接字符串不能包含 ``UID``、``PWD``、``Authentication`` 或 ``Trusted_Connection`` 参数。

.. tab:: 英文

    Some database servers are set up to only accept access tokens for login. For
    example, SQL Server allows the use of Azure Active Directory tokens to connect
    to databases. This requires creating a credential object using the
    ``azure-identity`` library. More information about the authentication step can be
    found in `Microsoft's documentation
    <https://docs.microsoft.com/en-us/azure/developer/python/azure-sdk-authenticate?tabs=bash>`_.

    After getting an engine, the credentials need to be sent to ``pyodbc.connect``
    each time a connection is requested. One way to do this is to set up an event
    listener on the engine that adds the credential token to the dialect's connect
    call. This is discussed more generally in :ref:`engines_dynamic_tokens`. For
    SQL Server in particular, this is passed as an ODBC connection attribute with
    a data structure `described by Microsoft
    <https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory#authenticating-with-an-access-token>`_.

    The following code snippet will create an engine that connects to an Azure SQL
    database using Azure credentials::

        import struct
        from sqlalchemy import create_engine, event
        from sqlalchemy.engine.url import URL
        from azure import identity

        # Connection option for access tokens, as defined in msodbcsql.h
        SQL_COPT_SS_ACCESS_TOKEN = 1256
        TOKEN_URL = "https://database.windows.net/"  # The token URL for any Azure SQL database

        connection_string = "mssql+pyodbc://@my-server.database.windows.net/myDb?driver=ODBC+Driver+17+for+SQL+Server"

        engine = create_engine(connection_string)

        azure_credentials = identity.DefaultAzureCredential()


        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            # remove the "Trusted_Connection" parameter that SQLAlchemy adds
            cargs[0] = cargs[0].replace(";Trusted_Connection=Yes", "")

            # create token credential
            raw_token = azure_credentials.get_token(TOKEN_URL).token.encode(
                "utf-16-le"
            )
            token_struct = struct.pack(
                f"<I{len(raw_token)}s", len(raw_token), raw_token
            )

            # apply it to keyword arguments
            cparams["attrs_before"] = {SQL_COPT_SS_ACCESS_TOKEN: token_struct}

    .. tip::

        The ``Trusted_Connection`` token is currently added by the SQLAlchemy
        pyodbc dialect when no username or password is present.  This needs
        to be removed per Microsoft's
        `documentation for Azure access tokens
        <https://docs.microsoft.com/en-us/sql/connect/odbc/using-azure-active-directory#authenticating-with-an-access-token>`_,
        stating that a connection string when using an access token must not contain
        ``UID``, ``PWD``, ``Authentication`` or ``Trusted_Connection`` parameters.

.. _azure_synapse_ignore_no_transaction_on_rollback:

避免 Azure Synapse Analytics 上出现与事务相关的异常
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Avoiding transaction-related exceptions on Azure Synapse Analytics

.. tab:: 中文

    Azure Synapse Analytics 在事务处理方面与普通 SQL Server 有显著差异；在某些情况下，Synapse 中事务内部的错误可能导致该事务在服务器端被任意中止，这会导致 DBAPI 的 ``.rollback()`` 方法（以及 ``.commit()``）失败。该问题打破了 DBAPI 的常规契约，即在没有事务的情况下允许 ``.rollback()`` 静默通过，因为驱动程序不会预期这种情况。该问题的症状是在某些操作失败后尝试执行 ``.rollback()`` 时抛出类似 `'No corresponding transaction found. (111214)'` 的异常。

    可以通过将 ``ignore_no_transaction_on_rollback=True`` 参数传递给 SQL Server 方言，并使用 :func:`_sa.create_engine` 函数来处理此特定情况，如下所示::

        engine = create_engine(
            connection_url, ignore_no_transaction_on_rollback=True
        )

    使用上述参数，方言将在 ``connection.rollback()`` 期间捕获 ``ProgrammingError`` 异常，如果错误消息包含代码 ``111214``，则会发出警告，但不会抛出异常。

    .. versionadded:: 1.4.40
       增加了 ``ignore_no_transaction_on_rollback=True`` 参数。

.. tab:: 英文

    Azure Synapse Analytics has a significant difference in its transaction
    handling compared to plain SQL Server; in some cases an error within a Synapse
    transaction can cause it to be arbitrarily terminated on the server side, which
    then causes the DBAPI ``.rollback()`` method (as well as ``.commit()``) to
    fail. The issue prevents the usual DBAPI contract of allowing ``.rollback()``
    to pass silently if no transaction is present as the driver does not expect
    this condition. The symptom of this failure is an exception with a message
    resembling 'No corresponding transaction found. (111214)' when attempting to
    emit a ``.rollback()`` after an operation had a failure of some kind.

    This specific case can be handled by passing ``ignore_no_transaction_on_rollback=True`` to
    the SQL Server dialect via the :func:`_sa.create_engine` function as follows::

        engine = create_engine(
            connection_url, ignore_no_transaction_on_rollback=True
        )

    Using the above parameter, the dialect will catch ``ProgrammingError``
    exceptions raised during ``connection.rollback()`` and emit a warning
    if the error message contains code ``111214``, however will not raise
    an exception.

    .. versionadded:: 1.4.40  Added the
        ``ignore_no_transaction_on_rollback=True`` parameter.

为 Azure SQL 数据仓库 (DW) 连接启用自动提交
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Enable autocommit for Azure SQL Data Warehouse (DW) connections

.. tab:: 中文

    Azure SQL Data Warehouse 不支持事务，这可能会导致 SQLAlchemy 的“自动启动事务”（autobegin）行为（以及隐式提交/回滚）出现问题。可以通过在 pyodbc 和 engine 层都启用自动提交来避免这些问题::

        connection_url = sa.engine.URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="dw.azure.example.com",
            database="mydb",
            query={
                "driver": "ODBC Driver 17 for SQL Server",
                "autocommit": "True",
            },
        )

        engine = create_engine(connection_url).execution_options(
            isolation_level="AUTOCOMMIT"
        )

.. tab:: 英文

    Azure SQL Data Warehouse does not support transactions,
    and that can cause problems with SQLAlchemy's "autobegin" (and implicit
    commit/rollback) behavior. We can avoid these problems by enabling autocommit
    at both the pyodbc and engine levels::

        connection_url = sa.engine.URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="dw.azure.example.com",
            database="mydb",
            query={
                "driver": "ODBC Driver 17 for SQL Server",
                "autocommit": "True",
            },
        )

        engine = create_engine(connection_url).execution_options(
            isolation_level="AUTOCOMMIT"
        )

避免以 TEXT/NTEXT 格式发送大型字符串参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Avoiding sending large string parameters as TEXT/NTEXT

.. tab:: 中文

    出于历史原因，Microsoft 的 SQL Server ODBC 驱动程序默认会将长字符串参数（超过 4000 个 SBCS 字符或 2000 个 Unicode 字符）作为 TEXT/NTEXT 类型发送。TEXT 和 NTEXT 类型已被弃用多年，并开始在新版 SQL Server/Azure 中引发兼容性问题。有关示例，请参见 `此问题 <https://github.com/mkleehammer/pyodbc/issues/835>`_。

    从 SQL Server 的 ODBC Driver 18 开始，可以通过连接字符串参数 ``LongAsMax=Yes`` 覆盖这一旧有行为，将长字符串作为 varchar(max)/nvarchar(max) 传递::

        connection_url = sa.engine.URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="mssqlserver.example.com",
            database="mydb",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "LongAsMax": "Yes",
            },
        )

.. tab:: 英文

    By default, for historical reasons, Microsoft's ODBC drivers for SQL Server
    send long string parameters (greater than 4000 SBCS characters or 2000 Unicode
    characters) as TEXT/NTEXT values. TEXT and NTEXT have been deprecated for many
    years and are starting to cause compatibility issues with newer versions of
    SQL_Server/Azure. For example, see `this
    issue <https://github.com/mkleehammer/pyodbc/issues/835>`_.

    Starting with ODBC Driver 18 for SQL Server we can override the legacy
    behavior and pass long strings as varchar(max)/nvarchar(max) using the
    ``LongAsMax=Yes`` connection string parameter::

        connection_url = sa.engine.URL.create(
            "mssql+pyodbc",
            username="scott",
            password="tiger",
            host="mssqlserver.example.com",
            database="mydb",
            query={
                "driver": "ODBC Driver 18 for SQL Server",
                "LongAsMax": "Yes",
            },
        )

Pyodbc 池化/连接关闭行为
------------------------------------------

Pyodbc Pooling / connection close behavior

.. tab:: 中文

    PyODBC 默认使用内部 `连接池机制
    <https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#pooling>`_，这意味着连接的生命周期会比 SQLAlchemy 自身的连接更长。由于 SQLAlchemy 本身也有连接池机制，通常建议禁用 PyODBC 的连接池。该行为只能在 PyODBC 模块级别全局禁用，且必须在建立任何连接 **之前** 进行设置::

        import pyodbc

        pyodbc.pooling = False

        # 在禁用连接池之前不要使用 engine
        engine = create_engine("mssql+pyodbc://user:pass@dsn")

    如果此变量保持默认值 ``True``，**即使 SQLAlchemy 的 engine 彻底丢弃了连接或已被 dispose，应用程序仍会保持活动数据库连接**。

    .. seealso::

        `连接池 <https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#pooling>`_ -
        来自 PyODBC 文档。

.. tab:: 英文

    PyODBC uses internal `pooling
    <https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#pooling>`_ by
    default, which means connections will be longer lived than they are within
    SQLAlchemy itself.  As SQLAlchemy has its own pooling behavior, it is often
    preferable to disable this behavior.  This behavior can only be disabled
    globally at the PyODBC module level, **before** any connections are made::

        import pyodbc

        pyodbc.pooling = False

        # don't use the engine before pooling is set to False
        engine = create_engine("mssql+pyodbc://user:pass@dsn")

    If this variable is left at its default value of ``True``, **the application
    will continue to maintain active database connections**, even when the
    SQLAlchemy engine itself fully discards a connection or if the engine is
    disposed.

    .. seealso::

        `pooling <https://github.com/mkleehammer/pyodbc/wiki/The-pyodbc-Module#pooling>`_ -
        in the PyODBC documentation.

驱动程序/Unicode 支持
-------------------------

Driver / Unicode Support

.. tab:: 中文

    PyODBC 在使用 Microsoft ODBC 驱动程序时表现最佳，特别是在 Python 2 和 Python 3 的 Unicode 支持方面。

    在 Linux 或 OSX 上使用 FreeTDS ODBC 驱动程序配合 PyODBC **不推荐**；在此方面历史上存在许多 Unicode 相关问题，尤其是在 Microsoft 尚未为 Linux 和 OSX 提供 ODBC 驱动时。现在 Microsoft 已为所有平台提供官方驱动，因此推荐在 PyODBC 中使用这些驱动。而 FreeTDS 在用于如 pymssql 这类非 ODBC 驱动时仍然非常实用。

.. tab:: 英文

    PyODBC works best with Microsoft ODBC drivers, particularly in the area
    of Unicode support on both Python 2 and Python 3.

    Using the FreeTDS ODBC drivers on Linux or OSX with PyODBC is **not**
    recommended; there have been historically many Unicode-related issues
    in this area, including before Microsoft offered ODBC drivers for Linux
    and OSX.   Now that Microsoft offers drivers for all platforms, for
    PyODBC support these are recommended.  FreeTDS remains relevant for
    non-ODBC drivers such as pymssql where it works very well.


行数支持
----------------

Rowcount Support

.. tab:: 中文

    在 SQLAlchemy 2.0.5 中，ORM 的“版本控制行（versioned rows）”特性与 PyODBC 之间的限制已被修复。参见 :ref:`mssql_rowcount_versioning` 中的说明。

.. tab:: 英文

    Previous limitations with the SQLAlchemy ORM's "versioned rows" feature with
    Pyodbc have been resolved as of SQLAlchemy 2.0.5. See the notes at
    :ref:`mssql_rowcount_versioning`.

.. _mssql_pyodbc_fastexecutemany:

快速执行模式
---------------------

Fast Executemany Mode

.. tab:: 中文

    PyODBC 驱动程序支持一种名为 “fast executemany” 的快速执行模式，该模式在使用 Microsoft ODBC 驱动程序时能极大减少 DBAPI ``executemany()`` 调用的往返次数，适用于 **可全部装入内存的小批量数据** 。该功能通过在 DBAPI 游标上设置 ``.fast_executemany`` 属性来启用。当使用 Microsoft ODBC 驱动程序时，SQLAlchemy 的 pyodbc SQL Server 方言支持通过 :func:`_sa.create_engine` 传递 ``fast_executemany`` 参数启用该功能::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            fast_executemany=True,
        )

    .. versionchanged:: 2.0.9
       ``fast_executemany`` 参数现在在所有使用多组参数但不包含 RETURNING 的 INSERT 语句中生效。此前，在 SQLAlchemy 2.0 中，:term:`insertmanyvalues` 特性曾导致即使指定了该参数，也在大多数情况下未被启用。

    .. seealso::

        `fast executemany <https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API#fast_executemany>`_
        - 来自 github

.. tab:: 英文

    The PyODBC driver includes support for a "fast executemany" mode of execution
    which greatly reduces round trips for a DBAPI ``executemany()`` call when using
    Microsoft ODBC drivers, for **limited size batches that fit in memory**.  The
    feature is enabled by setting the attribute ``.fast_executemany`` on the DBAPI
    cursor when an executemany call is to be used.   The SQLAlchemy PyODBC SQL
    Server dialect supports this parameter by passing the
    ``fast_executemany`` parameter to
    :func:`_sa.create_engine` , when using the **Microsoft ODBC driver only**::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            fast_executemany=True,
        )

    .. versionchanged:: 2.0.9 - the ``fast_executemany`` parameter now has its
    intended effect of this PyODBC feature taking effect for all INSERT
    statements that are executed with multiple parameter sets, which don't
    include RETURNING.  Previously, SQLAlchemy 2.0's :term:`insertmanyvalues`
    feature would cause ``fast_executemany`` to not be used in most cases
    even if specified.

    .. seealso::

        `fast executemany <https://github.com/mkleehammer/pyodbc/wiki/Features-beyond-the-DB-API#fast_executemany>`_
        - on github

.. _mssql_pyodbc_setinputsizes:

设置输入大小支持
-----------------------

Setinputsizes Support

.. tab:: 中文

    从 SQLAlchemy 2.0 起，除启用了 ``fast_executemany=True`` 的 ``cursor.executemany()`` 调用外，pyodbc 方言在执行所有语句时均使用 ``cursor.setinputsizes()`` 方法（假设未显式禁用 :ref:`insertmanyvalues <engine_insertmanyvalues>`，则 INSERT 语句在任何情况下都不会触发 fast executemany）。

    可以通过向 :func:`_sa.create_engine` 传递 ``use_setinputsizes=False`` 来禁用 ``cursor.setinputsizes()`` 的使用。

    当 ``use_setinputsizes`` 保持默认值 ``True`` 时，可以通过 :meth:`.DialectEvents.do_setinputsizes` 钩子以编程方式自定义传递给 ``cursor.setinputsizes()`` 的每种类型的具体标记。请参阅该方法以获取使用示例。

    .. versionchanged:: 2.0
        mssql+pyodbc 方言现在默认对所有语句执行使用 ``use_setinputsizes=True``，除了启用了 fast_executemany 的 ``cursor.executemany()`` 调用。该行为可通过向 :func:`_sa.create_engine` 传递 ``use_setinputsizes=False`` 来关闭。

.. tab:: 英文

    As of version 2.0, the pyodbc ``cursor.setinputsizes()`` method is used for
    all statement executions, except for ``cursor.executemany()`` calls when
    fast_executemany=True where it is not supported (assuming
    :ref:`insertmanyvalues <engine_insertmanyvalues>` is kept enabled,
    "fastexecutemany" will not take place for INSERT statements in any case).

    The use of ``cursor.setinputsizes()`` can be disabled by passing
    ``use_setinputsizes=False`` to :func:`_sa.create_engine`.

    When ``use_setinputsizes`` is left at its default of ``True``, the
    specific per-type symbols passed to ``cursor.setinputsizes()`` can be
    programmatically customized using the :meth:`.DialectEvents.do_setinputsizes`
    hook. See that method for usage examples.

    .. versionchanged:: 2.0  The mssql+pyodbc dialect now defaults to using
    ``use_setinputsizes=True`` for all statement executions with the exception of
    cursor.executemany() calls when fast_executemany=True.  The behavior can
    be turned off by passing ``use_setinputsizes=False`` to
    :func:`_sa.create_engine`.

"""  # noqa

import datetime
import decimal
import re
import struct

from .base import _MSDateTime
from .base import _MSUnicode
from .base import _MSUnicodeText
from .base import BINARY
from .base import DATETIMEOFFSET
from .base import MSDialect
from .base import MSExecutionContext
from .base import VARBINARY
from .json import JSON as _MSJson
from .json import JSONIndexType as _MSJsonIndexType
from .json import JSONPathType as _MSJsonPathType
from ... import exc
from ... import types as sqltypes
from ... import util
from ...connectors.pyodbc import PyODBCConnector
from ...engine import cursor as _cursor


class _ms_numeric_pyodbc:
    """Turns Decimals with adjusted() < 0 or > 7 into strings.

    The routines here are needed for older pyodbc versions
    as well as current mxODBC versions.

    """

    def bind_processor(self, dialect):
        super_process = super().bind_processor(dialect)

        if not dialect._need_decimal_fix:
            return super_process

        def process(value):
            if self.asdecimal and isinstance(value, decimal.Decimal):
                adjusted = value.adjusted()
                if adjusted < 0:
                    return self._small_dec_to_string(value)
                elif adjusted > 7:
                    return self._large_dec_to_string(value)

            if super_process:
                return super_process(value)
            else:
                return value

        return process

    # these routines needed for older versions of pyodbc.
    # as of 2.1.8 this logic is integrated.

    def _small_dec_to_string(self, value):
        return "%s0.%s%s" % (
            (value < 0 and "-" or ""),
            "0" * (abs(value.adjusted()) - 1),
            "".join([str(nint) for nint in value.as_tuple()[1]]),
        )

    def _large_dec_to_string(self, value):
        _int = value.as_tuple()[1]
        if "E" in str(value):
            result = "%s%s%s" % (
                (value < 0 and "-" or ""),
                "".join([str(s) for s in _int]),
                "0" * (value.adjusted() - (len(_int) - 1)),
            )
        else:
            if (len(_int) - 1) > value.adjusted():
                result = "%s%s.%s" % (
                    (value < 0 and "-" or ""),
                    "".join([str(s) for s in _int][0 : value.adjusted() + 1]),
                    "".join([str(s) for s in _int][value.adjusted() + 1 :]),
                )
            else:
                result = "%s%s" % (
                    (value < 0 and "-" or ""),
                    "".join([str(s) for s in _int][0 : value.adjusted() + 1]),
                )
        return result


class _MSNumeric_pyodbc(_ms_numeric_pyodbc, sqltypes.Numeric):
    pass


class _MSFloat_pyodbc(_ms_numeric_pyodbc, sqltypes.Float):
    pass


class _ms_binary_pyodbc:
    """Wraps binary values in dialect-specific Binary wrapper.
    If the value is null, return a pyodbc-specific BinaryNull
    object to prevent pyODBC [and FreeTDS] from defaulting binary
    NULL types to SQLWCHAR and causing implicit conversion errors.
    """

    def bind_processor(self, dialect):
        if dialect.dbapi is None:
            return None

        DBAPIBinary = dialect.dbapi.Binary

        def process(value):
            if value is not None:
                return DBAPIBinary(value)
            else:
                # pyodbc-specific
                return dialect.dbapi.BinaryNull

        return process


class _ODBCDateTimeBindProcessor:
    """Add bind processors to handle datetimeoffset behaviors"""

    has_tz = False

    def bind_processor(self, dialect):
        def process(value):
            if value is None:
                return None
            elif isinstance(value, str):
                # if a string was passed directly, allow it through
                return value
            elif not value.tzinfo or (not self.timezone and not self.has_tz):
                # for DateTime(timezone=False)
                return value
            else:
                # for DATETIMEOFFSET or DateTime(timezone=True)
                #
                # Convert to string format required by T-SQL
                dto_string = value.strftime("%Y-%m-%d %H:%M:%S.%f %z")
                # offset needs a colon, e.g., -0700 -> -07:00
                # "UTC offset in the form (+-)HHMM[SS[.ffffff]]"
                # backend currently rejects seconds / fractional seconds
                dto_string = re.sub(r"([\+\-]\d{2})([\d\.]+)$", r"\1:\2", dto_string)
                return dto_string

        return process


class _ODBCDateTime(_ODBCDateTimeBindProcessor, _MSDateTime):
    pass


class _ODBCDATETIMEOFFSET(_ODBCDateTimeBindProcessor, DATETIMEOFFSET):
    has_tz = True


class _VARBINARY_pyodbc(_ms_binary_pyodbc, VARBINARY):
    pass


class _BINARY_pyodbc(_ms_binary_pyodbc, BINARY):
    pass


class _String_pyodbc(sqltypes.String):
    def get_dbapi_type(self, dbapi):
        if self.length in (None, "max") or self.length >= 2000:
            return (dbapi.SQL_VARCHAR, 0, 0)
        else:
            return dbapi.SQL_VARCHAR


class _Unicode_pyodbc(_MSUnicode):
    def get_dbapi_type(self, dbapi):
        if self.length in (None, "max") or self.length >= 2000:
            return (dbapi.SQL_WVARCHAR, 0, 0)
        else:
            return dbapi.SQL_WVARCHAR


class _UnicodeText_pyodbc(_MSUnicodeText):
    def get_dbapi_type(self, dbapi):
        if self.length in (None, "max") or self.length >= 2000:
            return (dbapi.SQL_WVARCHAR, 0, 0)
        else:
            return dbapi.SQL_WVARCHAR


class _JSON_pyodbc(_MSJson):
    def get_dbapi_type(self, dbapi):
        return (dbapi.SQL_WVARCHAR, 0, 0)


class _JSONIndexType_pyodbc(_MSJsonIndexType):
    def get_dbapi_type(self, dbapi):
        return dbapi.SQL_WVARCHAR


class _JSONPathType_pyodbc(_MSJsonPathType):
    def get_dbapi_type(self, dbapi):
        return dbapi.SQL_WVARCHAR


class MSExecutionContext_pyodbc(MSExecutionContext):
    _embedded_scope_identity = False

    def pre_exec(self):
        """where appropriate, issue "select scope_identity()" in the same
        statement.

        Background on why "scope_identity()" is preferable to "@@identity":
        https://msdn.microsoft.com/en-us/library/ms190315.aspx

        Background on why we attempt to embed "scope_identity()" into the same
        statement as the INSERT:
        https://code.google.com/p/pyodbc/wiki/FAQs#How_do_I_retrieve_autogenerated/identity_values?

        """

        super().pre_exec()

        # don't embed the scope_identity select into an
        # "INSERT .. DEFAULT VALUES"
        if (
            self._select_lastrowid
            and self.dialect.use_scope_identity
            and len(self.parameters[0])
        ):
            self._embedded_scope_identity = True

            self.statement += "; select scope_identity()"

    def post_exec(self):
        if self._embedded_scope_identity:
            # Fetch the last inserted id from the manipulated statement
            # We may have to skip over a number of result sets with
            # no data (due to triggers, etc.)
            while True:
                try:
                    # fetchall() ensures the cursor is consumed
                    # without closing it (FreeTDS particularly)
                    rows = self.cursor.fetchall()
                except self.dialect.dbapi.Error:
                    # no way around this - nextset() consumes the previous set
                    # so we need to just keep flipping
                    self.cursor.nextset()
                else:
                    if not rows:
                        # async adapter drivers just return None here
                        self.cursor.nextset()
                        continue
                    row = rows[0]
                    break

            self._lastrowid = int(row[0])

            self.cursor_fetch_strategy = _cursor._NO_CURSOR_DML
        else:
            super().post_exec()


class MSDialect_pyodbc(PyODBCConnector, MSDialect):
    supports_statement_cache = True

    # note this parameter is no longer used by the ORM or default dialect
    # see #9414
    supports_sane_rowcount_returning = False

    execution_ctx_cls = MSExecutionContext_pyodbc

    colspecs = util.update_copy(
        MSDialect.colspecs,
        {
            sqltypes.Numeric: _MSNumeric_pyodbc,
            sqltypes.Float: _MSFloat_pyodbc,
            BINARY: _BINARY_pyodbc,
            # support DateTime(timezone=True)
            sqltypes.DateTime: _ODBCDateTime,
            DATETIMEOFFSET: _ODBCDATETIMEOFFSET,
            # SQL Server dialect has a VARBINARY that is just to support
            # "deprecate_large_types" w/ VARBINARY(max), but also we must
            # handle the usual SQL standard VARBINARY
            VARBINARY: _VARBINARY_pyodbc,
            sqltypes.VARBINARY: _VARBINARY_pyodbc,
            sqltypes.LargeBinary: _VARBINARY_pyodbc,
            sqltypes.String: _String_pyodbc,
            sqltypes.Unicode: _Unicode_pyodbc,
            sqltypes.UnicodeText: _UnicodeText_pyodbc,
            sqltypes.JSON: _JSON_pyodbc,
            sqltypes.JSON.JSONIndexType: _JSONIndexType_pyodbc,
            sqltypes.JSON.JSONPathType: _JSONPathType_pyodbc,
            # this excludes Enum from the string/VARCHAR thing for now
            # it looks like Enum's adaptation doesn't really support the
            # String type itself having a dialect-level impl
            sqltypes.Enum: sqltypes.Enum,
        },
    )

    def __init__(
        self,
        fast_executemany=False,
        use_setinputsizes=True,
        **params,
    ):
        super().__init__(use_setinputsizes=use_setinputsizes, **params)
        self.use_scope_identity = (
            self.use_scope_identity
            and self.dbapi
            and hasattr(self.dbapi.Cursor, "nextset")
        )
        self._need_decimal_fix = self.dbapi and self._dbapi_version() < (
            2,
            1,
            8,
        )
        self.fast_executemany = fast_executemany
        if fast_executemany:
            self.use_insertmanyvalues_wo_returning = False

    def _get_server_version_info(self, connection):
        try:
            # "Version of the instance of SQL Server, in the form
            # of 'major.minor.build.revision'"
            raw = connection.exec_driver_sql(
                "SELECT CAST(SERVERPROPERTY('ProductVersion') AS VARCHAR)"
            ).scalar()
        except exc.DBAPIError:
            # SQL Server docs indicate this function isn't present prior to
            # 2008.  Before we had the VARCHAR cast above, pyodbc would also
            # fail on this query.
            return super()._get_server_version_info(connection)
        else:
            version = []
            r = re.compile(r"[.\-]")
            for n in r.split(raw):
                try:
                    version.append(int(n))
                except ValueError:
                    pass
            return tuple(version)

    def on_connect(self):
        super_ = super().on_connect()

        def on_connect(conn):
            if super_ is not None:
                super_(conn)

            self._setup_timestampoffset_type(conn)

        return on_connect

    def _setup_timestampoffset_type(self, connection):
        # output converter function for datetimeoffset
        def _handle_datetimeoffset(dto_value):
            tup = struct.unpack("<6hI2h", dto_value)
            return datetime.datetime(
                tup[0],
                tup[1],
                tup[2],
                tup[3],
                tup[4],
                tup[5],
                tup[6] // 1000,
                datetime.timezone(datetime.timedelta(hours=tup[7], minutes=tup[8])),
            )

        odbc_SQL_SS_TIMESTAMPOFFSET = -155  # as defined in SQLNCLI.h
        connection.add_output_converter(
            odbc_SQL_SS_TIMESTAMPOFFSET, _handle_datetimeoffset
        )

    def do_executemany(self, cursor, statement, parameters, context=None):
        if self.fast_executemany:
            cursor.fast_executemany = True
        super().do_executemany(cursor, statement, parameters, context=context)

    def is_disconnect(self, e, connection, cursor):
        if isinstance(e, self.dbapi.Error):
            code = e.args[0]
            if code in {
                "08S01",
                "01000",
                "01002",
                "08003",
                "08007",
                "08S02",
                "08001",
                "HYT00",
                "HY010",
                "10054",
            }:
                return True
        return super().is_disconnect(e, connection, cursor)


dialect = MSDialect_pyodbc
