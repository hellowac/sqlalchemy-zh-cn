.. _engines_toplevel:

====================
Engine 配置
====================

Engine Configuration

.. tab:: 中文

    :class:`_engine.Engine` 是任何SQLAlchemy应用程序的起点。它是实际数据库及其 :term:`DBAPI` 的“基地”，通过连接池和描述如何与特定类型的数据库/DBAPI组合通信的 :class:`.Dialect` 提供给SQLAlchemy应用程序。

    一般结构可以如下图所示：

    .. image:: sqla_engine_arch.png

    在上图中，:class:`_engine.Engine` 引用 :class:`.Dialect` 和 :class:`_pool.Pool`，它们共同解释DBAPI的模块函数以及数据库的行为。

    创建引擎只需发出一个简单的调用 :func:`_sa.create_engine()`::

        from sqlalchemy import create_engine

        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase")

    上述引擎创建了一个针对PostgreSQL定制的 :class:`.Dialect` 对象，以及一个在首次收到连接请求时将在 ``localhost:5432`` 建立DBAPI连接的 :class:`_pool.Pool` 对象。注意 :class:`_engine.Engine` 及其底层的 :class:`_pool.Pool` 在调用 :meth:`_engine.Engine.connect` 或 :meth:`_engine.Engine.begin` 方法之前不会建立第一个实际的DBAPI连接。这些方法中的任意一个也可能被其他首次需要数据库连接的SQLAlchemy :class:`_engine.Engine` 依赖对象（如ORM的 :class:`_orm.Session` 对象）调用。通过这种方式，可以说 :class:`_engine.Engine` 和 :class:`_pool.Pool` 具有 *延迟初始化* 行为。

    创建后，可以直接使用 :class:`_engine.Engine` 与数据库交互，或将其传递给 :class:`.Session` 对象以使用ORM。本节介绍了配置 :class:`_engine.Engine` 的详细信息。下一节 :ref:`connections_toplevel` 将详细介绍 :class:`_engine.Engine` 及类似对象的使用API，通常用于非ORM应用程序。

.. tab:: 英文

    The :class:`_engine.Engine` is the starting point for any SQLAlchemy application. It's
    "home base" for the actual database and its :term:`DBAPI`, delivered to the SQLAlchemy
    application through a connection pool and a :class:`.Dialect`, which describes how
    to talk to a specific kind of database/DBAPI combination.

    The general structure can be illustrated as follows:

    .. image:: sqla_engine_arch.png

    Where above, an :class:`_engine.Engine` references both a
    :class:`.Dialect` and a :class:`_pool.Pool`,
    which together interpret the DBAPI's module functions as well as the behavior
    of the database.

    Creating an engine is just a matter of issuing a single call,
    :func:`_sa.create_engine()`::

        from sqlalchemy import create_engine

        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost:5432/mydatabase")

    The above engine creates a :class:`.Dialect` object tailored towards
    PostgreSQL, as well as a :class:`_pool.Pool` object which will establish a
    DBAPI connection at ``localhost:5432`` when a connection request is first
    received. Note that the :class:`_engine.Engine` and its underlying
    :class:`_pool.Pool` do **not** establish the first actual DBAPI connection
    until the :meth:`_engine.Engine.connect` or :meth:`_engine.Engine.begin`
    methods are called.  Either of these methods may also be invoked by other
    SQLAlchemy :class:`_engine.Engine` dependent objects such as the ORM
    :class:`_orm.Session` object when they first require database connectivity.
    In this way, :class:`_engine.Engine` and :class:`_pool.Pool` can be said to
    have a *lazy initialization* behavior.

    The :class:`_engine.Engine`, once created, can either be used directly to interact with the database,
    or can be passed to a :class:`.Session` object to work with the ORM.   This section
    covers the details of configuring an :class:`_engine.Engine`.   The next section, :ref:`connections_toplevel`,
    will detail the usage API of the :class:`_engine.Engine` and similar, typically for non-ORM
    applications.

.. _supported_dbapis:

支持的数据库
===================

Supported Databases

.. tab:: 中文

    SQLAlchemy 包含许多适用于各种后端的 :class:`.Dialect` 实现。SQLAlchemy 已包含最常见数据库的方言；其他一些数据库的方言则需要额外安装单独的方言。

    有关各种可用后端的信息，请参阅 :ref:`dialect_toplevel` 部分。

.. tab:: 英文

    SQLAlchemy includes many :class:`.Dialect` implementations for various backends.   Dialects for the most common databases are included with SQLAlchemy; a handful of others require an additional install of a separate dialect.

    See the section :ref:`dialect_toplevel` for information on the various backends available.

.. _database_urls:

数据库 URL
=============

Database URLs

.. tab:: 中文

    :func:`_sa.create_engine` 函数基于 URL 生成一个 :class:`_engine.Engine` 对象。URL 的格式通常遵循 `RFC-1738 <https://www.ietf.org/rfc/rfc1738.txt>`_，但也有一些例外，例如在“scheme”部分可以使用下划线，而不能使用短划线或句点。URL 通常包含用户名、密码、主机名、数据库名称字段，以及用于附加配置的可选关键字参数。在某些情况下，可以使用文件路径，而在其他情况下，可以使用“数据源名称”替换“主机”和“数据库”部分。数据库 URL 的典型格式如下：

    .. sourcecode:: text

        dialect+driver://username:password@host:port/database

    方言名称包括 SQLAlchemy 方言的标识名称，例如“sqlite”、“mysql”、“postgresql”、“oracle”或“mssql”。驱动程序名称是用于连接数据库的 DBAPI 的名称，所有名称均使用小写字母。如果未指定，则会导入“默认”DBAPI（如果可用）——此默认驱动程序通常是该后端最知名的驱动程序。

.. tab:: 英文

    The :func:`_sa.create_engine` function produces an :class:`_engine.Engine` object based on a URL. The format of the URL generally follows `RFC-1738 <https://www.ietf.org/rfc/rfc1738.txt>`_, with some exceptions, including that underscores, not dashes or periods, are accepted within the "scheme" portion. URLs typically include username, password, hostname, database name fields, as well as optional keyword arguments for additional configuration. In some cases a file path is accepted, and in others a "data source name" replaces the "host" and "database" portions. The typical form of a database URL is:

    .. sourcecode:: text

        dialect+driver://username:password@host:port/database

    Dialect names include the identifying name of the SQLAlchemy dialect, a name such as ``sqlite``, ``mysql``, ``postgresql``, ``oracle``, or ``mssql``. The drivername is the name of the DBAPI to be used to connect to the database using all lowercase letters. If not specified, a "default" DBAPI will be imported if available - this default is typically the most widely known driver available for that backend.

转义密码中的特殊字符，例如 @ 符号
----------------------------------------------------------

Escaping Special Characters such as @ signs in Passwords

.. tab:: 中文

    在构造传递给 :func:`_sa.create_engine` 的完整 URL 字符串时， 
    **用户名和密码中可能包含的特殊字符需要进行 URL 编码，才能被正确解析。**
     **这包括 @ 符号。**

    下面是一个包含密码 ``"kx@jj5/g"`` 的 URL 示例，其中 "at" 符号和斜杠字符分别表示为
    ``%40`` 和 ``%2F``：

    .. sourcecode:: text

        postgresql+pg8000://dbuser:kx%40jj5%2Fg@pghost10/appdb

    上述密码的编码可以使用 `urllib.parse <https://docs.python.org/3/library/urllib.parse.html>`_ 生成::

    >>> import urllib.parse
    >>> urllib.parse.quote_plus("kx@jj5/g")
    'kx%40jj5%2Fg'

    然后可以将该 URL 字符串传递给 :func:`_sa.create_engine`::

        from sqlalchemy import create_engine

        engine = create_engine("postgresql+pg8000://dbuser:kx%40jj5%2Fg@pghost10/appdb")

    除了通过转义特殊字符来构建完整的 URL 字符串外，
    还可以将一个 :class:`.URL` 对象实例传递给 :func:`_sa.create_engine`，
    这样可以跳过字符串解析过程，并直接处理未转义的字符串。
    有关示例，请参见下一节。

    .. versionchanged:: 1.4

        已修复对主机名和数据库名称中 ``@`` 符号的支持。
        由于该修复，密码中的 ``@`` 符号现在必须进行转义。

.. tab:: 英文

    When constructing a fully formed URL string to pass to
    :func:`_sa.create_engine`, **special characters such as those that may
    be used in the user and password need to be URL encoded to be parsed correctly.**.
    **This includes the @ sign**.

    Below is an example of a URL that includes the password ``"kx@jj5/g"``, where the
    "at" sign and slash characters are represented as ``%40`` and ``%2F``,
    respectively:

    .. sourcecode:: text

        postgresql+pg8000://dbuser:kx%40jj5%2Fg@pghost10/appdb


    The encoding for the above password can be generated using
    `urllib.parse <https://docs.python.org/3/library/urllib.parse.html>`_::

    >>> import urllib.parse
    >>> urllib.parse.quote_plus("kx@jj5/g")
    'kx%40jj5%2Fg'

    The URL may then be passed as a string to :func:`_sa.create_engine`::

        from sqlalchemy import create_engine

        engine = create_engine("postgresql+pg8000://dbuser:kx%40jj5%2Fg@pghost10/appdb")

    As an alternative to escaping special characters in order to create a complete
    URL string, the object passed to :func:`_sa.create_engine` may instead be an
    instance of the :class:`.URL` object, which bypasses the parsing
    phase and can accommodate for unescaped strings directly.  See the next
    section for an example.

    .. versionchanged:: 1.4

        Support for ``@`` signs in hostnames and database names has been
        fixed.   As a side effect of this fix, ``@`` signs in passwords must be
        escaped.

以编程方式创建 URL
-------------------------------

Creating URLs Programmatically

.. tab:: 中文

    传递给 :func:`_sa.create_engine` 的参数可以是一个 :class:`.URL` 实例，
    而不是一个普通字符串，这样就不需要执行字符串解析，也不需要提供已转义的 URL 字符串。

    :class:`.URL` 对象是使用 :meth:`_engine.URL.create()` 构造方法创建的，
    每个字段都单独传入。密码中的特殊字符可以直接传递，无需修改::

        from sqlalchemy import URL

        url_object = URL.create(
            "postgresql+pg8000",
            username="dbuser",
            password="kx@jj5/g",  # 原始（未转义）文本
            host="pghost10",
            database="appdb",
        )

    构造好的 :class:`.URL` 对象随后可以直接传递给 :func:`_sa.create_engine`，
    用于替代字符串参数::

        from sqlalchemy import create_engine

        engine = create_engine(url_object)

    .. seealso::

        :class:`.URL`

        :meth:`.URL.create`


.. tab:: 英文

    The value passed to :func:`_sa.create_engine` may be an instance of
    :class:`.URL`, instead of a plain string, which bypasses the need for string
    parsing to be used, and therefore does not need an escaped URL string to be
    provided.

    The :class:`.URL` object is created using the :meth:`_engine.URL.create()`
    constructor method, passing all fields individually.   Special characters
    such as those within passwords may be passed without any modification::

        from sqlalchemy import URL

        url_object = URL.create(
            "postgresql+pg8000",
            username="dbuser",
            password="kx@jj5/g",  # plain (unescaped) text
            host="pghost10",
            database="appdb",
        )

    The constructed :class:`.URL` object may then be passed directly to
    :func:`_sa.create_engine` in place of a string argument::

        from sqlalchemy import create_engine

        engine = create_engine(url_object)

    .. seealso::

        :class:`.URL`

        :meth:`.URL.create`

后端特定的 URL
----------------------

Backend-Specific URLs

.. tab:: 中文

.. tab:: 英文

Examples for common connection styles follow below.  For a full index of
detailed information on all included dialects as well as links to third-party
dialects, see :ref:`dialect_toplevel`.

PostgreSQL
^^^^^^^^^^

PostgreSQL

.. tab:: 中文

.. tab:: 英文

The PostgreSQL dialect uses psycopg2 as the default DBAPI.  Other
PostgreSQL DBAPIs include pg8000 and asyncpg::

    # default
    engine = create_engine("postgresql://scott:tiger@localhost/mydatabase")

    # psycopg2
    engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/mydatabase")

    # pg8000
    engine = create_engine("postgresql+pg8000://scott:tiger@localhost/mydatabase")

More notes on connecting to PostgreSQL at :ref:`postgresql_toplevel`.

MySQL
^^^^^^^^^^

MySQL

.. tab:: 中文

    MySQL 方言使用 mysqlclient 作为默认 DBAPI。还有其他可用的 MySQL DBAPI，包括 PyMySQL::

        # default
        engine = create_engine("mysql://scott:tiger@localhost/foo")

        # mysqlclient (a maintained fork of MySQL-Python)
        engine = create_engine("mysql+mysqldb://scott:tiger@localhost/foo")

        # PyMySQL
        engine = create_engine("mysql+pymysql://scott:tiger@localhost/foo")

    有关连接到 MySQL 的更多说明，请参阅 :ref:`mysql_toplevel`.

.. tab:: 英文

    The MySQL dialect uses mysqlclient as the default DBAPI.  There are other MySQL DBAPIs available, including PyMySQL::

        # default
        engine = create_engine("mysql://scott:tiger@localhost/foo")

        # mysqlclient (a maintained fork of MySQL-Python)
        engine = create_engine("mysql+mysqldb://scott:tiger@localhost/foo")

        # PyMySQL
        engine = create_engine("mysql+pymysql://scott:tiger@localhost/foo")

    More notes on connecting to MySQL at :ref:`mysql_toplevel`.

Oracle
^^^^^^^^^^

Oracle

.. tab:: 中文

.. tab:: 英文

    首选的 Oracle 数据库方言使用 python-oracledb 驱动程序作为 DBAPI::

        engine = create_engine(
            "oracle+oracledb://scott:tiger@127.0.0.1:1521/?service_name=freepdb1"
        )

        engine = create_engine("oracle+oracledb://scott:tiger@tnsalias")

    由于历史原因，Oracle 方言使用过时的 cx_Oracle 驱动程序作为默认 DBAPI::

        engine = create_engine("oracle://scott:tiger@127.0.0.1:1521/?service_name=freepdb1")

        engine = create_engine("oracle+cx_oracle://scott:tiger@tnsalias")

    有关连接到 Oracle 数据库的更多说明，请访问 :ref:`oracle_toplevel`.

Microsoft SQL Server
^^^^^^^^^^^^^^^^^^^^

Microsoft SQL Server

.. tab:: 中文

    SQL Server 方言使用 pyodbc 作为默认 DBAPI。pymssql 也可用::

        # pyodbc
        engine = create_engine("mssql+pyodbc://scott:tiger@mydsn")

        # pymssql
        engine = create_engine("mssql+pymssql://scott:tiger@hostname:port/dbname")

    有关连接到 SQL Server 的更多说明，请参阅 :ref:`mssql_toplevel`.

.. tab:: 英文

    The SQL Server dialect uses pyodbc as the default DBAPI.  pymssql is also available::

        # pyodbc
        engine = create_engine("mssql+pyodbc://scott:tiger@mydsn")

        # pymssql
        engine = create_engine("mssql+pymssql://scott:tiger@hostname:port/dbname")

    More notes on connecting to SQL Server at :ref:`mssql_toplevel`.

SQLite
^^^^^^^

SQLite

.. tab:: 中文

    SQLite 连接基于文件的数据库，默认使用 Python 内置模块 ``sqlite3``.

    由于 SQLite 连接到本地文件，URL 格式略有不同。URL 中的“file”部分是数据库的文件名。对于相对文件路径，需要三个斜杠::

        # sqlite://<nohostname>/<path>
        # where <path> is relative:
        engine = create_engine("sqlite:///foo.db")

    对于绝对文件路径，三个斜杠后面是绝对路径::

        # Unix/Mac - 4 initial slashes in total
        engine = create_engine("sqlite:////absolute/path/to/foo.db")

        # Windows
        engine = create_engine("sqlite:///C:\\path\\to\\foo.db")

        # Windows alternative using raw string
        engine = create_engine(r"sqlite:///C:\path\to\foo.db")

    要使用 SQLite ``:memory:`` 数据库，请指定一个空的 URL::

        engine = create_engine("sqlite://")

    有关连接到 SQLite 的更多说明 :ref:`sqlite_toplevel`.

.. tab:: 英文

    SQLite connects to file-based databases, using the Python built-in module ``sqlite3`` by default.

    As SQLite connects to local files, the URL format is slightly different. The "file" portion of the URL is the filename of the database. For a relative file path, this requires three slashes::

        # sqlite://<nohostname>/<path>
        # where <path> is relative:
        engine = create_engine("sqlite:///foo.db")

    And for an absolute file path, the three slashes are followed by the absolute path::

        # Unix/Mac - 4 initial slashes in total
        engine = create_engine("sqlite:////absolute/path/to/foo.db")

        # Windows
        engine = create_engine("sqlite:///C:\\path\\to\\foo.db")

        # Windows alternative using raw string
        engine = create_engine(r"sqlite:///C:\path\to\foo.db")

    To use a SQLite ``:memory:`` database, specify an empty URL::

        engine = create_engine("sqlite://")

    More notes on connecting to SQLite at :ref:`sqlite_toplevel`.

其他
^^^^^^

Others

.. tab:: 中文

    请参阅 :ref:`dialect_toplevel` ，这是所有其他方言文档的顶级页面。

.. tab:: 英文

    See :ref:`dialect_toplevel`, the top-level page for all additional dialect documentation.

.. _create_engine_args:

引擎创建 API
===================

Engine Creation API

.. autofunction:: sqlalchemy.create_engine

.. autofunction:: sqlalchemy.engine_from_config

.. autofunction:: sqlalchemy.create_mock_engine

.. autofunction:: sqlalchemy.engine.make_url

.. autofunction:: sqlalchemy.create_pool_from_url

.. autoclass:: sqlalchemy.engine.URL
    :members:

连接池
=======

Pooling

.. tab:: 中文

    当调用 ``connect()`` 或 ``execute()`` 方法时，:class:`_engine.Engine` 会向连接池请求一个连接。默认的连接池 :class:`~.QueuePool` 会根据需要建立与数据库的连接。随着并发语句的执行，:class:`.QueuePool` 会将其连接池扩展到默认的五个连接，并允许默认“溢出”数量为十个。由于 :class:`_engine.Engine` 本质上是连接池的“主控中心”，因此应该在应用中为每个数据库仅创建一个 :class:`_engine.Engine` 实例，而不是为每次连接都新建一个实例。

    .. note::

        SQLite 引擎默认不使用 :class:`.QueuePool`。有关 SQLite 连接池的使用详情，请参阅 :ref:`sqlite_toplevel`。

    有关连接池的更多信息，请参阅 :ref:`pooling_toplevel`。


.. tab:: 英文

    The :class:`_engine.Engine` will ask the connection pool for a connection when the ``connect()`` or ``execute()`` methods are called. The default connection pool, :class:`~.QueuePool`, will open connections to the database on an as-needed basis. As concurrent statements are executed, :class:`.QueuePool` will grow its pool of connections to a default size of five, and will allow a default "overflow" of ten. Since the :class:`_engine.Engine` is essentially "home base" for the connection pool, it follows that you should keep a single :class:`_engine.Engine` per database established within an application, rather than creating a new one for each connection.

    .. note::

        :class:`.QueuePool` is not used by default for SQLite engines.  See
        :ref:`sqlite_toplevel` for details on SQLite connection pool usage.

    For more information on connection pooling, see :ref:`pooling_toplevel`.


.. _custom_dbapi_args:

自定义 DBAPI connect() 参数/连接例程
=======================================================

Custom DBAPI connect() arguments / on-connect routines

.. tab:: 中文


    在需要特殊连接方式的场景中，在绝大多数情况下，最合适的做法是使用 :func:`_sa.create_engine` 提供的多个钩子之一来自定义连接过程。相关内容将在后续小节中介绍。

.. tab:: 英文

    For cases where special connection methods are needed, in the vast majority of cases, it is most appropriate to use one of several hooks at the :func:`_sa.create_engine` level in order to customize this process. These are described in the following sub-sections.

传递给 dbapi.connect() 的特殊关键字参数
---------------------------------------------------

Special Keyword Arguments Passed to dbapi.connect()

.. tab:: 中文

    所有 Python DBAPI 都接受除基本连接参数外的附加参数。常见的参数包括用于指定字符集编码和超时值的选项；更复杂的则可能包括特殊的 DBAPI 常量、对象及 SSL 子参数。有两种基本方式可以简单地传递这些参数。

.. tab:: 英文

    All Python DBAPIs accept additional arguments beyond the basics of connecting. Common parameters include those to specify character set encodings and timeout values; more complex data includes special DBAPI constants and objects and SSL sub-parameters. There are two rudimentary means of passing these arguments without complexity.

将参数添加到 URL 查询字符串
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Add Parameters to the URL Query string

.. tab:: 中文

    简单的字符串值，以及部分数值和布尔标志，通常可以直接通过 URL 的查询字符串传递。一个常见示例是 DBAPI 接受 ``encoding`` 参数来指定字符编码，例如大多数 MySQL 的 DBAPI 实现::

        engine = create_engine("mysql+pymysql://user:pass@host/test?charset=utf8mb4")

    使用查询字符串的优点是可以将附加的 DBAPI 选项以一种对 URL 中指定的 DBAPI 具有可移植性的方式写入配置文件。在此层级传递的具体参数会因 SQLAlchemy 方言（dialect）而异。有些方言会将所有参数按字符串形式传递，而另一些方言会对特定的数据类型进行解析，并将参数移至不同的位置，例如驱动层级的 DSN 或连接字符串。由于每种方言在此方面的行为目前仍存在差异，应查阅所使用方言的文档，以确认特定参数是否在该层级被支持。

    .. tip::

        一种通用技巧可用于查看为某个 URL 实际传递给 DBAPI 的参数，
        可通过直接调用 :meth:`.Dialect.create_connect_args` 方法来实现::

                >>> from sqlalchemy import create_engine
                >>> engine = create_engine(
                ...     "mysql+pymysql://some_user:some_pass@some_host/test?charset=utf8mb4"
                ... )
                >>> args, kwargs = engine.dialect.create_connect_args(engine.url)
                >>> args, kwargs
                ([], {'host': 'some_host', 'database': 'test', 'user': 'some_user', 'password': 'some_pass', 'charset': 'utf8mb4', 'client_flag': 2})

        上述 ``args, kwargs`` 对通常以 ``dbapi.connect(*args, **kwargs)`` 的形式传递给 DBAPI。

.. tab:: 英文

    Simple string values, as well as some numeric values and boolean flags, may be
    often specified in the query string of the URL directly. A common example of
    this is DBAPIs that accept an argument ``encoding`` for character encodings,
    such as most MySQL DBAPIs::

        engine = create_engine("mysql+pymysql://user:pass@host/test?charset=utf8mb4")

    The advantage of using the query string is that additional DBAPI options may be
    specified in configuration files in a manner that's portable to the DBAPI
    specified in the URL. The specific parameters passed through at this level vary
    by SQLAlchemy dialect. Some dialects pass all arguments through as strings,
    while others will parse for specific datatypes and move parameters to different
    places, such as into driver-level DSNs and connect strings. As per-dialect
    behavior in this area currently varies, the dialect documentation should be
    consulted for the specific dialect in use to see if particular parameters are
    supported at this level.

    .. tip::

        A general technique to display the exact arguments passed to the DBAPI
        for a given URL may be performed using the :meth:`.Dialect.create_connect_args`
        method directly as follows::

                >>> from sqlalchemy import create_engine
                >>> engine = create_engine(
                ...     "mysql+pymysql://some_user:some_pass@some_host/test?charset=utf8mb4"
                ... )
                >>> args, kwargs = engine.dialect.create_connect_args(engine.url)
                >>> args, kwargs
                ([], {'host': 'some_host', 'database': 'test', 'user': 'some_user', 'password': 'some_pass', 'charset': 'utf8mb4', 'client_flag': 2})

        The above ``args, kwargs`` pair is normally passed to the DBAPI as
        ``dbapi.connect(*args, **kwargs)``.

使用 connect_args 字典参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the connect_args dictionary parameter

.. tab:: 中文

    一个更通用的方式，可以将任何参数传递给 ``dbapi.connect()`` 函数，并且可以确保在任何时候都传递所有参数，即使用 :paramref:`_sa.create_engine.connect_args` 字典参数。该参数适用于以下场景：当通过查询字符串添加参数时无法被方言识别，或者需要将特殊的子结构或对象传递给 DBAPI。有时，仅仅是某个特定的标志需要以 ``True`` 的形式传递，而 SQLAlchemy 的方言并不知道要将其从 URL 中的字符串形式转换为布尔值。以下示例展示了如何使用 psycopg2 的 “连接工厂” 替代底层连接实现::

        engine = create_engine(
            "postgresql+psycopg2://user:pass@hostname/dbname",
            connect_args={"connection_factory": MyConnectionFactory},
        )

    另一个示例是 pyodbc 的 “timeout” 参数::

        engine = create_engine(
            "mssql+pyodbc://user:pass@sqlsrvr?driver=ODBC+Driver+13+for+SQL+Server",
            connect_args={"timeout": 30},
        )

    上述示例还说明，URL 查询字符串参数和 :paramref:`_sa.create_engine.connect_args` 参数可以同时使用；对于 pyodbc 来说，URL 中的 “driver” 关键字具有特殊含义。

.. tab:: 英文

    A more general system of passing any parameter to the ``dbapi.connect()``
    function that is guaranteed to pass all parameters at all times is the
    :paramref:`_sa.create_engine.connect_args` dictionary parameter. This may be
    used for parameters that are otherwise not handled by the dialect when added to
    the query string, as well as when special sub-structures or objects must be
    passed to the DBAPI. Sometimes it's just that a particular flag must be sent as
    the ``True`` symbol and the SQLAlchemy dialect is not aware of this keyword
    argument to coerce it from its string form as presented in the URL. Below
    illustrates the use of a psycopg2 "connection factory" that replaces the
    underlying implementation the connection::


        engine = create_engine(
            "postgresql+psycopg2://user:pass@hostname/dbname",
            connect_args={"connection_factory": MyConnectionFactory},
        )

    Another example is the pyodbc "timeout" parameter::

        engine = create_engine(
            "mssql+pyodbc://user:pass@sqlsrvr?driver=ODBC+Driver+13+for+SQL+Server",
            connect_args={"timeout": 30},
        )

    The above example also illustrates that both URL "query string" parameters as
    well as :paramref:`_sa.create_engine.connect_args` may be used at the same
    time; in the case of pyodbc, the "driver" keyword has special meaning
    within the URL.

控制如何将参数传递给 DBAPI connect() 函数
---------------------------------------------------------------------

Controlling how parameters are passed to the DBAPI connect() function

.. tab:: 中文

    除了操作传递给 ``connect()`` 的参数之外，我们还可以进一步自定义调用 DBAPI 的 ``connect()`` 函数的方式，方法是使用 :meth:`.DialectEvents.do_connect` 事件钩子。该钩子接收方言将发送给 ``connect()`` 的完整 ``*args, **kwargs``。你可以在钩子中就地修改这些参数集合，以改变它们的使用方式::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            cparams["connection_factory"] = MyConnectionFactory

.. tab:: 英文

    Beyond manipulating the parameters passed to ``connect()``, we can further
    customize how the DBAPI ``connect()`` function itself is called using the
    :meth:`.DialectEvents.do_connect` event hook. This hook is passed the full
    ``*args, **kwargs`` that the dialect would send to ``connect()``. These
    collections can then be modified in place to alter how they are used::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            cparams["connection_factory"] = MyConnectionFactory

.. _engines_dynamic_tokens:

生成动态身份验证令牌
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Generating dynamic authentication tokens

.. tab:: 中文

    :meth:`.DialectEvents.do_connect` 也是在 :class:`_sa.engine.Engine` 生命周期内动态插入认证令牌的理想方式。例如，如果令牌是通过 ``get_authentication_token()`` 生成的，并通过 ``token`` 参数传递给 DBAPI，可以这样实现::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            cparams["token"] = get_authentication_token()

    .. seealso::

        :ref:`mssql_pyodbc_access_tokens` - 一个更具体的 SQL Server 示例

.. tab:: 英文

    :meth:`.DialectEvents.do_connect` is also an ideal way to dynamically
    insert an authentication token that might change over the lifespan of an
    :class:`_sa.engine.Engine`. For example, if the token gets generated by
    ``get_authentication_token()`` and passed to the DBAPI in  a ``token``
    parameter, this could be implemented as::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def provide_token(dialect, conn_rec, cargs, cparams):
            cparams["token"] = get_authentication_token()

    .. seealso::

        :ref:`mssql_pyodbc_access_tokens` - a more concrete example involving
        SQL Server

在连接后修改 DBAPI 连接，或在连接后运行命令
-------------------------------------------------------------------------------

Modifying the DBAPI connection after connect, or running commands after connect

.. tab:: 中文

    如果 SQLAlchemy 能够成功创建 DBAPI 连接，但你希望在连接实际使用之前对其进行修改（例如设置特殊标志或执行某些命令），那么 :meth:`.PoolEvents.connect` 事件钩子是最合适的选择。该钩子在每个新连接创建后被调用，并且是在连接被 SQLAlchemy 使用之前::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            cursor_obj = dbapi_connection.cursor()
            cursor_obj.execute("SET some session variables")
            cursor_obj.close()


.. tab:: 英文

    For a DBAPI connection that SQLAlchemy creates without issue, but where we
    would like to modify the completed connection before it's actually used, such
    as for setting special flags or running certain commands, the
    :meth:`.PoolEvents.connect` event hook is the most appropriate hook.  This
    hook is called for every new connection created, before it is used by
    SQLAlchemy::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            cursor_obj = dbapi_connection.cursor()
            cursor_obj.execute("SET some session variables")
            cursor_obj.close()

完全替换 DBAPI ``connect()`` 函数
------------------------------------------------

Fully Replacing the DBAPI ``connect()`` function

.. tab:: 中文

    最后，:meth:`.DialectEvents.do_connect` 事件钩子还允许我们完全接管连接过程，自己建立连接并返回连接::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            # 返回我们想要的新的 DBAPI 连接
            return psycopg2.connect(*cargs, **cparams)

    :meth:`.DialectEvents.do_connect` 钩子优于之前的 :paramref:`_sa.create_engine.creator` 钩子，尽管后者仍然可用。:meth:`.DialectEvents.do_connect` 的一个显著优点是，URL 解析出的完整参数也会传递给用户定义的函数，而 :paramref:`_sa.create_engine.creator` 并没有做到这一点。

.. tab:: 英文

    Finally, the :meth:`.DialectEvents.do_connect` event hook can also allow us to take
    over the connection process entirely by establishing the connection
    and returning it::

        from sqlalchemy import event

        engine = create_engine("postgresql+psycopg2://user:pass@hostname/dbname")


        @event.listens_for(engine, "do_connect")
        def receive_do_connect(dialect, conn_rec, cargs, cparams):
            # return the new DBAPI connection with whatever we'd like to
            # do
            return psycopg2.connect(*cargs, **cparams)

    The :meth:`.DialectEvents.do_connect` hook supersedes the previous
    :paramref:`_sa.create_engine.creator` hook, which remains available.
    :meth:`.DialectEvents.do_connect` has the distinct advantage that the
    complete arguments parsed from the URL are also passed to the user-defined
    function which is not the case with :paramref:`_sa.create_engine.creator`.

.. _dbengine_logging:

配置日志记录
===================

Configuring Logging

.. tab:: 中文

    Python 的标准 `logging
    <https://docs.python.org/library/logging.html>`_ 模块用于实现 SQLAlchemy 的信息和调试日志输出。这使得 SQLAlchemy 的日志能够以标准方式与其他应用程序和库集成。还存在两个参数 :paramref:`_sa.create_engine.echo` 和 :paramref:`_sa.create_engine.echo_pool`，它们可以在 :func:`_sa.create_engine` 上使用，用于将日志直接输出到 ``sys.stdout``，以便本地开发使用；这些参数最终与下面描述的常规 Python 日志记录器进行交互。
    
    本节假设读者已经熟悉上述链接的日志模块。SQLAlchemy 执行的所有日志记录都位于 ``sqlalchemy`` 命名空间下，使用 ``logging.getLogger('sqlalchemy')`` 来访问。当日志记录已被配置（例如通过 ``logging.basicConfig()``）时，可以打开的 SA 日志记录器的一般命名空间如下：
    
    * ``sqlalchemy.engine`` - 控制 SQL 回显。设置为 ``logging.INFO`` 用于 SQL 查询输出，设置为 ``logging.DEBUG`` 用于查询和结果集输出。这些设置等价于 :paramref:`_sa.create_engine.echo` 上的 ``echo=True`` 和 ``echo="debug"``。
    
    * ``sqlalchemy.pool`` - 控制连接池日志。设置为 ``logging.INFO`` 以记录连接失效和回收事件；设置为 ``logging.DEBUG`` 以同时记录所有池的检查和归还事件。这些设置等价于 :paramref:`_sa.create_engine.echo_pool` 上的 ``pool_echo=True`` 和 ``pool_echo="debug"``。
    
    * ``sqlalchemy.dialects`` - 控制 SQL 方言的自定义日志记录，具体取决于特定方言中是否使用日志记录，通常是最少的。
    
    * ``sqlalchemy.orm`` - 控制 ORM 函数的日志记录，具体取决于 ORM 中是否使用日志记录，通常也是最少的。设置为 ``logging.INFO`` 以记录一些有关映射器配置的顶级信息。
    
    例如，使用 Python 日志记录来记录 SQL 查询，而不是使用 ``echo=True`` 标志::
    
        import logging
    
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    
    默认情况下，整个 ``sqlalchemy`` 命名空间的日志级别设置为 ``logging.WARN``，因此不会执行任何日志操作，即使应用程序启用了其他日志记录。
    
    .. note::
    
       SQLAlchemy 的 :class:`_engine.Engine` 会通过仅在当前日志级别被检测为 ``logging.INFO`` 或 ``logging.DEBUG`` 时才发出日志语句，从而节省 Python 函数调用的开销。它仅在从连接池中获取新连接时检查此级别。因此，在更改已经运行的应用程序的日志配置时，任何当前活动的 :class:`_engine.Connection`，或更常见的 :class:`~.orm.session.Session` 对象，直到获取新连接后（在 :class:`~.orm.session.Session` 中，这是在当前事务结束并开始新的事务之后）才会根据新配置记录 SQL。

.. tab:: 英文

    Python's standard `logging
    <https://docs.python.org/library/logging.html>`_ module is used to
    implement informational and debug log output with SQLAlchemy. This allows
    SQLAlchemy's logging to integrate in a standard way with other applications
    and libraries.   There are also two parameters
    :paramref:`_sa.create_engine.echo` and :paramref:`_sa.create_engine.echo_pool`
    present on :func:`_sa.create_engine` which allow immediate logging to ``sys.stdout``
    for the purposes of local development; these parameters ultimately interact
    with the regular Python loggers described below.
    
    This section assumes familiarity with the above linked logging module. All
    logging performed by SQLAlchemy exists underneath the ``sqlalchemy``
    namespace, as used by ``logging.getLogger('sqlalchemy')``. When logging has
    been configured (i.e. such as via ``logging.basicConfig()``), the general
    namespace of SA loggers that can be turned on is as follows:
    
    * ``sqlalchemy.engine`` - controls SQL echoing.  Set to ``logging.INFO`` for
      SQL query output, ``logging.DEBUG`` for query + result set output.  These
      settings are equivalent to ``echo=True`` and ``echo="debug"`` on
      :paramref:`_sa.create_engine.echo`, respectively.
    
    * ``sqlalchemy.pool`` - controls connection pool logging.  Set to
      ``logging.INFO`` to log connection invalidation and recycle events; set to
      ``logging.DEBUG`` to additionally log all pool checkins and checkouts.
      These settings are equivalent to ``pool_echo=True`` and ``pool_echo="debug"``
      on :paramref:`_sa.create_engine.echo_pool`, respectively.
    
    * ``sqlalchemy.dialects`` - controls custom logging for SQL dialects, to the
      extent that logging is used within specific dialects, which is generally
      minimal.
    
    * ``sqlalchemy.orm`` - controls logging of various ORM functions to the extent
      that logging is used within the ORM, which is generally minimal.  Set to
      ``logging.INFO`` to log some top-level information on mapper configurations.
    
    For example, to log SQL queries using Python logging instead of the
    ``echo=True`` flag::
    
        import logging
    
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    
    By default, the log level is set to ``logging.WARN`` within the entire
    ``sqlalchemy`` namespace so that no log operations occur, even within an
    application that has logging enabled otherwise.
    
    .. note::
    
       The SQLAlchemy :class:`_engine.Engine` conserves Python function call
       overhead by only emitting log statements when the current logging level is
       detected as ``logging.INFO`` or ``logging.DEBUG``.  It only checks this
       level when a new connection is procured from the connection pool.  Therefore
       when changing the logging configuration for an already-running application,
       any :class:`_engine.Connection` that's currently active, or more commonly a
       :class:`~.orm.session.Session` object that's active in a transaction, won't
       log any SQL according to the new configuration until a new
       :class:`_engine.Connection` is procured (in the case of
       :class:`~.orm.session.Session`, this is after the current transaction ends
       and a new one begins).

有关 Echo 标志的更多信息
---------------------

More on the Echo Flag

.. tab:: 中文

    如前所述，:paramref:`_sa.create_engine.echo` 和 :paramref:`_sa.create_engine.echo_pool` 参数是立即将日志记录到 ``sys.stdout`` 的快捷方式::

        >>> from sqlalchemy import create_engine, text
        >>> e = create_engine("sqlite://", echo=True, echo_pool="debug")
        >>> with e.connect() as conn:
        ...     print(conn.scalar(text("select 'hi'")))
        2020-10-24 12:54:57,701 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Created new connection <sqlite3.Connection object at 0x7f287819ac60>
        2020-10-24 12:54:57,701 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> checked out from pool
        2020-10-24 12:54:57,702 INFO sqlalchemy.engine.Engine select 'hi'
        2020-10-24 12:54:57,702 INFO sqlalchemy.engine.Engine ()
        hi
        2020-10-24 12:54:57,703 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> being returned to pool
        2020-10-24 12:54:57,704 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> rollback-on-return

    使用这些标志的效果大致等同于::

        import logging

        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

    需要注意的是，这两个标志 **独立于** 任何现有的日志配置，并且会无条件地使用 ``logging.basicConfig()``。这会导致在任何现有的日志配置之外进行配置。因此， **在显式配置日志时，请确保所有 echo 标志始终设置为 False**，以避免出现重复的日志行。


.. tab:: 英文

    As mentioned previously, the :paramref:`_sa.create_engine.echo` and :paramref:`_sa.create_engine.echo_pool`
    parameters are a shortcut to immediate logging to ``sys.stdout``::
    
    
        >>> from sqlalchemy import create_engine, text
        >>> e = create_engine("sqlite://", echo=True, echo_pool="debug")
        >>> with e.connect() as conn:
        ...     print(conn.scalar(text("select 'hi'")))
        2020-10-24 12:54:57,701 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Created new connection <sqlite3.Connection object at 0x7f287819ac60>
        2020-10-24 12:54:57,701 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> checked out from pool
        2020-10-24 12:54:57,702 INFO sqlalchemy.engine.Engine select 'hi'
        2020-10-24 12:54:57,702 INFO sqlalchemy.engine.Engine ()
        hi
        2020-10-24 12:54:57,703 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> being returned to pool
        2020-10-24 12:54:57,704 DEBUG sqlalchemy.pool.impl.SingletonThreadPool Connection <sqlite3.Connection object at 0x7f287819ac60> rollback-on-return
    
    Use of these flags is roughly equivalent to::
    
        import logging
    
        logging.basicConfig()
        logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
        logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)
    
    It's important to note that these two flags work **independently** of any
    existing logging configuration, and will make use of ``logging.basicConfig()``
    unconditionally.  This has the effect of being configured **in addition** to
    any existing logger configurations. Therefore, **when configuring logging
    explicitly, ensure all echo flags are set to False at all times**, to avoid
    getting duplicate log lines.

设置日志记录名称
-------------------------

Setting the Logging Name

.. tab:: 中文

    :class:`~sqlalchemy.engine.Engine` 或 :class:`~sqlalchemy.pool.Pool` 的日志记录器名称设置为对象的模块限定类名。这个名称可以通过 :paramref:`_sa.create_engine.logging_name` 和 :paramref:`_sa.create_engine.pool_logging_name` 参数与 :func:`sqlalchemy.create_engine` 一起进一步限定；该名称将附加到现有的类限定日志记录名称上。建议在同时使用多个全局 :class:`.Engine` 实例的应用程序中使用此功能，以便可以在日志中区分它们::

        >>> import logging
        >>> from sqlalchemy import create_engine
        >>> from sqlalchemy import text
        >>> logging.basicConfig()
        >>> logging.getLogger("sqlalchemy.engine.Engine.myengine").setLevel(logging.INFO)
        >>> e = create_engine("sqlite://", logging_name="myengine")
        >>> with e.connect() as conn:
        ...     conn.execute(text("select 'hi'"))
        2020-10-24 12:47:04,291 INFO sqlalchemy.engine.Engine.myengine select 'hi'
        2020-10-24 12:47:04,292 INFO sqlalchemy.engine.Engine.myengine ()

    .. tip::

        :paramref:`_sa.create_engine.logging_name` 和 :paramref:`_sa.create_engine.pool_logging_name` 参数也可以与 :paramref:`_sa.create_engine.echo` 和 :paramref:`_sa.create_engine.echo_pool` 一起使用。然而，如果其他引擎的 echo 标志设置为 True 且 **没有** 设置日志名称，将不可避免地出现双重日志记录条件。这是因为会自动为 ``sqlalchemy.engine.Engine`` 添加一个处理程序，该处理程序将同时记录无名称引擎和具有日志名称的引擎的消息。例如::

            from sqlalchemy import create_engine, text

            e1 = create_engine("sqlite://", echo=True, logging_name="myname")
            with e1.begin() as conn:
                conn.execute(text("SELECT 1"))

            e2 = create_engine("sqlite://", echo=True)
            with e2.begin() as conn:
                conn.execute(text("SELECT 2"))

            with e1.begin() as conn:
                conn.execute(text("SELECT 3"))

        上述场景将会重复记录 ``SELECT 3``。为了解决此问题，确保所有引擎都设置了 ``logging_name``，或者在不使用 :paramref:`_sa.create_engine.echo` 和 :paramref:`_sa.create_engine.echo_pool` 的情况下使用显式的日志记录器/处理程序设置。

.. tab:: 英文

    The logger name for :class:`~sqlalchemy.engine.Engine` or
    :class:`~sqlalchemy.pool.Pool` is set to be the module-qualified class name of the
    object.  This name can be further qualified with an additional name
    using the
    :paramref:`_sa.create_engine.logging_name` and
    :paramref:`_sa.create_engine.pool_logging_name` parameters with
    :func:`sqlalchemy.create_engine`; the name will be appended to existing
    class-qualified logging name.   This use is recommended for applications that
    make use of multiple global :class:`.Engine` instances simultaenously, so
    that they may be distinguished in logging::

        >>> import logging
        >>> from sqlalchemy import create_engine
        >>> from sqlalchemy import text
        >>> logging.basicConfig()
        >>> logging.getLogger("sqlalchemy.engine.Engine.myengine").setLevel(logging.INFO)
        >>> e = create_engine("sqlite://", logging_name="myengine")
        >>> with e.connect() as conn:
        ...     conn.execute(text("select 'hi'"))
        2020-10-24 12:47:04,291 INFO sqlalchemy.engine.Engine.myengine select 'hi'
        2020-10-24 12:47:04,292 INFO sqlalchemy.engine.Engine.myengine ()

    .. tip::

        The :paramref:`_sa.create_engine.logging_name` and
        :paramref:`_sa.create_engine.pool_logging_name` parameters may also be used in
        conjunction with :paramref:`_sa.create_engine.echo` and
        :paramref:`_sa.create_engine.echo_pool`. However, an unavoidable double logging
        condition will occur if other engines are created with echo flags set to True
        and **no** logging name. This is because a handler will be added automatically
        for ``sqlalchemy.engine.Engine`` which will log messages both for the name-less
        engine as well as engines with logging names.   For example::

            from sqlalchemy import create_engine, text

            e1 = create_engine("sqlite://", echo=True, logging_name="myname")
            with e1.begin() as conn:
                conn.execute(text("SELECT 1"))

            e2 = create_engine("sqlite://", echo=True)
            with e2.begin() as conn:
                conn.execute(text("SELECT 2"))

            with e1.begin() as conn:
                conn.execute(text("SELECT 3"))

        The above scenario will double log ``SELECT 3``.  To resolve, ensure
        all engines have a ``logging_name`` set, or use explicit logger / handler
        setup without using :paramref:`_sa.create_engine.echo` and
        :paramref:`_sa.create_engine.echo_pool`.

.. _dbengine_logging_tokens:

设置每个连接/子引擎令牌
------------------------------------------

Setting Per-Connection / Sub-Engine Tokens

.. versionadded:: 1.4.0b2

.. tab:: 中文


    尽管日志记录名称适合用于长期存在的 :class:`_engine.Engine` 对象，但它不足以灵活应对具有任意多名称的情况，特别是在需要跟踪单独连接和/或事务的日志消息时。

    对于这种使用情况，可以通过 :class:`_engine.Connection` 和 :class:`_engine.Result` 对象生成的日志消息，增加额外的标识符，如事务或请求标识符。:paramref:`_engine.Connection.execution_options.logging_token` 参数接受一个字符串参数，该参数可用于建立每个连接的跟踪令牌::

        >>> from sqlalchemy import create_engine
        >>> e = create_engine("sqlite://", echo="debug")
        >>> with e.connect().execution_options(logging_token="track1") as conn:
        ...     conn.execute(text("select 1")).all()
        2021-02-03 11:48:45,754 INFO sqlalchemy.engine.Engine [track1] select 1
        2021-02-03 11:48:45,754 INFO sqlalchemy.engine.Engine [track1] [raw sql] ()
        2021-02-03 11:48:45,754 DEBUG sqlalchemy.engine.Engine [track1] Col ('1',)
        2021-02-03 11:48:45,755 DEBUG sqlalchemy.engine.Engine [track1] Row (1,)

    :paramref:`_engine.Connection.execution_options.logging_token` 参数也可以通过 :paramref:`_sa.create_engine.execution_options` 或 :meth:`_engine.Engine.execution_options` 在引擎或子引擎上进行设置。这对于应用不同的日志记录令牌到应用程序的不同组件而不创建新引擎时非常有用::

        >>> from sqlalchemy import create_engine
        >>> e = create_engine("sqlite://", echo="debug")
        >>> e1 = e.execution_options(logging_token="track1")
        >>> e2 = e.execution_options(logging_token="track2")
        >>> with e1.connect() as conn:
        ...     conn.execute(text("select 1")).all()
        2021-02-03 11:51:08,960 INFO sqlalchemy.engine.Engine [track1] select 1
        2021-02-03 11:51:08,960 INFO sqlalchemy.engine.Engine [track1] [raw sql] ()
        2021-02-03 11:51:08,960 DEBUG sqlalchemy.engine.Engine [track1] Col ('1',)
        2021-02-03 11:51:08,961 DEBUG sqlalchemy.engine.Engine [track1] Row (1,)

        >>> with e2.connect() as conn:
        ...     conn.execute(text("select 2")).all()
        2021-02-03 11:52:05,518 INFO sqlalchemy.engine.Engine [track2] Select 1
        2021-02-03 11:52:05,519 INFO sqlalchemy.engine.Engine [track2] [raw sql] ()
        2021-02-03 11:52:05,520 DEBUG sqlalchemy.engine.Engine [track2] Col ('1',)
        2021-02-03 11:52:05,520 DEBUG sqlalchemy.engine.Engine [track2] Row (1,)

.. tab:: 英文


    While the logging name is appropriate to establish on an
    :class:`_engine.Engine` object that is long lived, it's not flexible enough
    to accommodate for an arbitrarily large list of names, for the case of
    tracking individual connections and/or transactions in log messages.

    For this use case, the log message itself generated by the
    :class:`_engine.Connection` and :class:`_engine.Result` objects may be
    augmented with additional tokens such as transaction or request identifiers.
    The :paramref:`_engine.Connection.execution_options.logging_token` parameter
    accepts a string argument that may be used to establish per-connection tracking
    tokens::

        >>> from sqlalchemy import create_engine
        >>> e = create_engine("sqlite://", echo="debug")
        >>> with e.connect().execution_options(logging_token="track1") as conn:
        ...     conn.execute(text("select 1")).all()
        2021-02-03 11:48:45,754 INFO sqlalchemy.engine.Engine [track1] select 1
        2021-02-03 11:48:45,754 INFO sqlalchemy.engine.Engine [track1] [raw sql] ()
        2021-02-03 11:48:45,754 DEBUG sqlalchemy.engine.Engine [track1] Col ('1',)
        2021-02-03 11:48:45,755 DEBUG sqlalchemy.engine.Engine [track1] Row (1,)

    The :paramref:`_engine.Connection.execution_options.logging_token` parameter
    may also be established on engines or sub-engines via
    :paramref:`_sa.create_engine.execution_options` or :meth:`_engine.Engine.execution_options`.
    This may be useful to apply different logging tokens to different components
    of an application without creating new engines::

        >>> from sqlalchemy import create_engine
        >>> e = create_engine("sqlite://", echo="debug")
        >>> e1 = e.execution_options(logging_token="track1")
        >>> e2 = e.execution_options(logging_token="track2")
        >>> with e1.connect() as conn:
        ...     conn.execute(text("select 1")).all()
        2021-02-03 11:51:08,960 INFO sqlalchemy.engine.Engine [track1] select 1
        2021-02-03 11:51:08,960 INFO sqlalchemy.engine.Engine [track1] [raw sql] ()
        2021-02-03 11:51:08,960 DEBUG sqlalchemy.engine.Engine [track1] Col ('1',)
        2021-02-03 11:51:08,961 DEBUG sqlalchemy.engine.Engine [track1] Row (1,)

        >>> with e2.connect() as conn:
        ...     conn.execute(text("select 2")).all()
        2021-02-03 11:52:05,518 INFO sqlalchemy.engine.Engine [track2] Select 1
        2021-02-03 11:52:05,519 INFO sqlalchemy.engine.Engine [track2] [raw sql] ()
        2021-02-03 11:52:05,520 DEBUG sqlalchemy.engine.Engine [track2] Col ('1',)
        2021-02-03 11:52:05,520 DEBUG sqlalchemy.engine.Engine [track2] Row (1,)


隐藏参数
------------------

Hiding Parameters

.. tab:: 中文

    由 :class:`_engine.Engine` 发出的日志也会指示特定语句中存在的 SQL 参数摘录。为了出于隐私目的防止记录这些参数，可以启用 :paramref:`_sa.create_engine.hide_parameters` 标志::

        >>> e = create_engine("sqlite://", echo=True, hide_parameters=True)
        >>> with e.connect() as conn:
        ...     conn.execute(text("select :some_private_name"), {"some_private_name": "pii"})
        2020-10-24 12:48:32,808 INFO sqlalchemy.engine.Engine select ?
        2020-10-24 12:48:32,808 INFO sqlalchemy.engine.Engine [SQL parameters hidden due to hide_parameters=True]

.. tab:: 英文

    The logging emitted by :class:`_engine.Engine` also indicates an excerpt
    of the SQL parameters that are present for a particular statement.  To prevent
    these parameters from being logged for privacy purposes, enable the
    :paramref:`_sa.create_engine.hide_parameters` flag::

        >>> e = create_engine("sqlite://", echo=True, hide_parameters=True)
        >>> with e.connect() as conn:
        ...     conn.execute(text("select :some_private_name"), {"some_private_name": "pii"})
        2020-10-24 12:48:32,808 INFO sqlalchemy.engine.Engine select ?
        2020-10-24 12:48:32,808 INFO sqlalchemy.engine.Engine [SQL parameters hidden due to hide_parameters=True]
