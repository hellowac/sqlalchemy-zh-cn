# dialects/sqlite/pysqlite.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


r"""
.. dialect:: sqlite+pysqlite
    :name: pysqlite
    :dbapi: sqlite3
    :connectstring: sqlite+pysqlite:///file_path
    :url: https://docs.python.org/library/sqlite3.html

    Note that ``pysqlite`` is the same driver as the ``sqlite3``
    module included with the Python distribution.

驱动
------

Driver

.. tab:: 中文

    ``sqlite3`` Python DBAPI 是所有现代 Python 版本的标准；对于 cPython 和 Pypy，无需额外安装。

.. tab:: 英文

    The ``sqlite3`` Python DBAPI is standard on all modern Python versions; for cPython and Pypy, no additional installation is necessary.


连接字符串
---------------

Connect Strings

.. tab:: 中文

    SQLite 数据库的文件路径由 URL 中的 "database" 部分指定。请注意，SQLAlchemy 的 URL 格式如下：

    .. sourcecode:: text

        driver://user:pass@host/database

    这意味着实际使用的文件名是第三个斜杠右边的内容。因此，连接到一个相对路径的数据库的方式如下所示::

        # 相对路径
        e = create_engine("sqlite:///path/to/database.db")

    如果是绝对路径，需要以斜杠开头，这时就需要 **四个** 斜杠::

        # 绝对路径
        e = create_engine("sqlite:////path/to/database.db")

    在 Windows 上使用路径时，可以直接使用驱动器标识符和反斜杠，通常需要双反斜杠::

        # Windows 上的绝对路径
        e = create_engine("sqlite:///C:\\path\\to\\database.db")

    要使用 SQLite 的 ``:memory:`` 数据库，只需将其作为文件名提供，即 ``sqlite:///:memory:``。如果未提供任何路径，仅使用 ``sqlite://``，也会默认创建内存数据库::

        # 内存数据库（注意有三个斜杠）
        e = create_engine("sqlite:///:memory:")
        # 也是内存数据库
        e2 = create_engine("sqlite://")

.. tab:: 英文

    The file specification for the SQLite database is taken as the "database"
    portion of the URL.  Note that the format of a SQLAlchemy url is:

    .. sourcecode:: text

        driver://user:pass@host/database

    This means that the actual filename to be used starts with the characters to
    the **right** of the third slash.   So connecting to a relative filepath
    looks like::

        # relative path
        e = create_engine("sqlite:///path/to/database.db")

    An absolute path, which is denoted by starting with a slash, means you
    need **four** slashes::

        # absolute path
        e = create_engine("sqlite:////path/to/database.db")

    To use a Windows path, regular drive specifications and backslashes can be
    used. Double backslashes are probably needed::

        # absolute path on Windows
        e = create_engine("sqlite:///C:\\path\\to\\database.db")

    To use sqlite ``:memory:`` database specify it as the filename using
    ``sqlite:///:memory:``. It's also the default if no filepath is
    present, specifying only ``sqlite://`` and nothing else::

        # in-memory database (note three slashes)
        e = create_engine("sqlite:///:memory:")
        # also in-memory database
        e2 = create_engine("sqlite://")

.. _pysqlite_uri_connections:

URI 连接
^^^^^^^^^^^^^^^

URI Connections

.. tab:: 中文

    现代版本的 SQLite 支持一种替代连接机制，即使用 `驱动级 URI <https://www.sqlite.org/uri.html>`_，它的优点是可以传递额外的驱动参数，比如只读选项。“sqlite3” Python 驱动在现代 Python 3 版本中支持该模式。SQLAlchemy 的 pysqlite 驱动也支持该模式，只需在 URL 查询字符串中指定 "uri=true"。SQLite 级别的 URI 被保留为 SQLAlchemy URL 中的 "database" 部分（即斜杠后面）::

        e = create_engine("sqlite:///file:path/to/database?mode=ro&uri=true")

    .. note:: 参数 "uri=true" 必须出现在 URL 的 **查询字符串** 中。如果它仅出现在 :paramref:`_sa.create_engine.connect_args` 参数字典中，将不会按预期工作。

    SQLAlchemy 会区分 SQLAlchemy 查询字符串和 SQLite URI 查询字符串的参数来源，分别传递给 Python sqlite3 驱动与 SQLite URI。这通过一个已知的 Python 驱动参数固定列表实现。例如，如果同时传递 Python sqlite3 的 "timeout" 和 "check_same_thread" 参数，以及 SQLite 的 "mode" 和 "nolock" 参数，可以如下设置::

        e = create_engine(
            "sqlite:///file:path/to/database?"
            "check_same_thread=true&timeout=10&mode=ro&nolock=1&uri=true"
        )

    上述配置将被转换为传递给 pysqlite/sqlite3 DBAPI 的参数::

        sqlite3.connect(
            "file:path/to/database?mode=ro&nolock=1",
            check_same_thread=True,
            timeout=10,
            uri=True,
        )

    关于未来可能添加到 Python 驱动或 SQLite 原生驱动的新参数名：新增加的 SQLite URI 参数会自动被该机制支持。对于新增的 Python 驱动参数，可通过 :paramref:`_sa.create_engine.connect_args` 字典临时支持，直到 SQLAlchemy 提供正式支持。如果 SQLite 驱动新增的参数名与已知的 Python 驱动参数冲突（比如 "timeout"），则 SQLAlchemy 的方言层需要进行调整以继续支持该 URL 机制。

    如同其他 SQLAlchemy 方言一样，整个 URL 处理过程都可以通过 :func:`_sa.create_engine` 的 :paramref:`_sa.create_engine.creator` 参数绕过，该参数允许提供一个可调用对象直接创建底层 sqlite3 驱动连接。

    .. seealso::

        `Uniform Resource Identifiers <https://www.sqlite.org/uri.html>`_ - 来自 SQLite 文档。

.. tab:: 英文

    Modern versions of SQLite support an alternative system of connecting using a
    `driver level URI <https://www.sqlite.org/uri.html>`_, which has the  advantage
    that additional driver-level arguments can be passed including options such as
    "read only".   The Python sqlite3 driver supports this mode under modern Python
    3 versions.   The SQLAlchemy pysqlite driver supports this mode of use by
    specifying "uri=true" in the URL query string.  The SQLite-level "URI" is kept
    as the "database" portion of the SQLAlchemy url (that is, following a slash)::

        e = create_engine("sqlite:///file:path/to/database?mode=ro&uri=true")

    .. note::  The "uri=true" parameter must appear in the **query string**
       of the URL.  It will not currently work as expected if it is only
       present in the :paramref:`_sa.create_engine.connect_args`
       parameter dictionary.

    The logic reconciles the simultaneous presence of SQLAlchemy's query string and
    SQLite's query string by separating out the parameters that belong to the
    Python sqlite3 driver vs. those that belong to the SQLite URI.  This is
    achieved through the use of a fixed list of parameters known to be accepted by
    the Python side of the driver.  For example, to include a URL that indicates
    the Python sqlite3 "timeout" and "check_same_thread" parameters, along with the
    SQLite "mode" and "nolock" parameters, they can all be passed together on the
    query string::

        e = create_engine(
            "sqlite:///file:path/to/database?"
            "check_same_thread=true&timeout=10&mode=ro&nolock=1&uri=true"
        )

    Above, the pysqlite / sqlite3 DBAPI would be passed arguments as::

        sqlite3.connect(
            "file:path/to/database?mode=ro&nolock=1",
            check_same_thread=True,
            timeout=10,
            uri=True,
        )

    Regarding future parameters added to either the Python or native drivers. new
    parameter names added to the SQLite URI scheme should be automatically
    accommodated by this scheme.  New parameter names added to the Python driver
    side can be accommodated by specifying them in the
    :paramref:`_sa.create_engine.connect_args` dictionary,
    until dialect support is
    added by SQLAlchemy.   For the less likely case that the native SQLite driver
    adds a new parameter name that overlaps with one of the existing, known Python
    driver parameters (such as "timeout" perhaps), SQLAlchemy's dialect would
    require adjustment for the URL scheme to continue to support this.

    As is always the case for all SQLAlchemy dialects, the entire "URL" process
    can be bypassed in :func:`_sa.create_engine` through the use of the
    :paramref:`_sa.create_engine.creator`
    parameter which allows for a custom callable
    that creates a Python sqlite3 driver level connection directly.

    .. seealso::

        `Uniform Resource Identifiers <https://www.sqlite.org/uri.html>`_ - in the SQLite documentation

.. _pysqlite_regexp:

正则表达式支持
---------------------------

Regular Expression Support

.. versionadded:: 1.4

.. tab:: 中文

    对 :meth:`_sql.ColumnOperators.regexp_match` 操作符的支持是通过 Python 的 re.search_ 函数实现的。SQLite 本身并未实现正则表达式操作符；它仅提供了一个 ``REGEXP`` 占位符，该操作符会调用一个必须由用户提供的自定义函数。

    SQLAlchemy 的实现方式是通过 pysqlite 的 create_function_ 钩子，如下所示::

        def regexp(a, b):
            return re.search(a, b) is not None


        sqlite_connection.create_function(
            "regexp",
            2,
            regexp,
        )

    目前尚不支持将正则表达式标志作为单独参数传递，因为 SQLite 的 REGEXP 操作符不支持这种方式，但可以将标志内联到正则表达式字符串中。具体语法参见 `Python 正则表达式`_。

    .. seealso::

        `Python 正则表达式`_：Python 正则表达式语法的官方文档。

.. tab:: 英文

    Support for the :meth:`_sql.ColumnOperators.regexp_match` operator is provided
    using Python's re.search_ function.  SQLite itself does not include a working
    regular expression operator; instead, it includes a non-implemented placeholder
    operator ``REGEXP`` that calls a user-defined function that must be provided.

    SQLAlchemy's implementation makes use of the pysqlite create_function_ hook
    as follows::


        def regexp(a, b):
            return re.search(a, b) is not None


        sqlite_connection.create_function(
            "regexp",
            2,
            regexp,
        )

    There is currently no support for regular expression flags as a separate
    argument, as these are not supported by SQLite's REGEXP operator, however these
    may be included inline within the regular expression string.  See `Python regular expressions`_ for
    details.

    .. seealso::

        `Python regular expressions`_: Documentation for Python's regular expression syntax.

.. _create_function: https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.create_function

.. _re.search: https://docs.python.org/3/library/re.html#re.search

.. _Python regular expressions: https://docs.python.org/3/library/re.html#re.search

.. _Python 正则表达式: https://docs.python.org/3/library/re.html#re.search


与 SQLite3 原生日期和日期时间类型的兼容性
-----------------------------------------------------------

Compatibility with sqlite3 "native" date and datetime types

.. tab:: 中文

    pysqlite 驱动提供了 `sqlite3.PARSE_DECLTYPES` 和 `sqlite3.PARSE_COLNAMES` 选项，其作用是将显式转换为 "date" 或 "timestamp" 的列或表达式转换为 Python 的 date 或 datetime 对象。然而，pysqlite 方言提供的 date 和 datetime 类型目前与这些选项不兼容，因为它们会以包含微秒的 ISO 格式渲染，而 pysqlite 驱动不支持这种格式。

    此外，SQLAlchemy 当前不会自动渲染 "cast" 语法，使得像 "current_timestamp" 和 "current_date" 这样的独立函数返回 datetime/date 类型。更糟糕的是，pysqlite 并不会在 ``cursor.description`` 中提供标准 DBAPI 类型信息，导致 SQLAlchemy 无法在不引入昂贵的逐行类型检查的情况下自动识别这些类型。

    鉴于 pysqlite 的解析选项并不推荐使用，也通常不应在 SQLAlchemy 中使用，如果确有需求，可以在 create_engine() 中设置 ``native_datetime=True`` 强制使用 PARSE_DECLTYPES::

        engine = create_engine(
            "sqlite://",
            connect_args={
                "detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            },
            native_datetime=True,
        )

    启用该选项后，DATE 和 TIMESTAMP 类型（注意：不包括 DATETIME 或 TIME 类型...是不是有点混乱？）将不会执行绑定参数或结果处理。执行 "func.current_date()" 会返回一个字符串。而 "func.current_timestamp()" 在 SQLAlchemy 中注册为 DATETIME 类型，因此仍会执行 SQLAlchemy 层级的结果处理。

.. tab:: 英文

    The pysqlite driver includes the sqlite3.PARSE_DECLTYPES and
    sqlite3.PARSE_COLNAMES options, which have the effect of any column
    or expression explicitly cast as "date" or "timestamp" will be converted
    to a Python date or datetime object.  The date and datetime types provided
    with the pysqlite dialect are not currently compatible with these options,
    since they render the ISO date/datetime including microseconds, which
    pysqlite's driver does not.   Additionally, SQLAlchemy does not at
    this time automatically render the "cast" syntax required for the
    freestanding functions "current_timestamp" and "current_date" to return
    datetime/date types natively.   Unfortunately, pysqlite
    does not provide the standard DBAPI types in ``cursor.description``,
    leaving SQLAlchemy with no way to detect these types on the fly
    without expensive per-row type checks.

    Keeping in mind that pysqlite's parsing option is not recommended,
    nor should be necessary, for use with SQLAlchemy, usage of PARSE_DECLTYPES
    can be forced if one configures "native_datetime=True" on create_engine()::

        engine = create_engine(
            "sqlite://",
            connect_args={
                "detect_types": sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
            },
            native_datetime=True,
        )

    With this flag enabled, the DATE and TIMESTAMP types (but note - not the
    DATETIME or TIME types...confused yet ?) will not perform any bind parameter
    or result processing. Execution of "func.current_date()" will return a string.
    "func.current_timestamp()" is registered as returning a DATETIME type in
    SQLAlchemy, so this function still receives SQLAlchemy-level result
    processing.

.. _pysqlite_threading_pooling:

线程/池行为
---------------------------

Threading/Pooling Behavior

.. tab:: 中文

    ``sqlite3`` DBAPI 默认禁止在创建连接的线程之外的线程中使用该连接。随着 SQLite 的不断成熟，其在多线程环境下的行为也有所改进，甚至包括了对内存数据库在多线程中使用的支持选项。

    这个线程限制被称为 "check same thread"，可以通过 ``sqlite3`` 参数 ``check_same_thread`` 控制以启用或禁用该检查。SQLAlchemy 在此的默认行为是：只要使用的是基于文件的数据库，就会自动将 ``check_same_thread`` 设置为 ``False``，以实现与默认连接池类 :class:`.QueuePool` 的兼容。

    SQLAlchemy 的 ``pysqlite`` DBAPI 会根据请求的 SQLite 数据库类型，以不同方式建立连接池：

    * 当指定 SQLite 数据库为 ``:memory:`` 时，方言默认使用 :class:`.SingletonThreadPool`。该连接池在每个线程中维护一个单独的连接，从而使得当前线程对引擎的所有访问都使用相同的 ``:memory:`` 数据库——其他线程则访问不同的 ``:memory:`` 数据库。此时 ``check_same_thread`` 参数默认设为 ``True``。
    * 当指定为基于文件的数据库时，方言会使用 :class:`.QueuePool` 作为连接来源，同时，除非显式覆盖，``check_same_thread`` 参数默认被设置为 ``False``。

      .. versionchanged:: 2.0

        SQLite 文件数据库引擎现在默认使用 :class:`.QueuePool`。此前使用的是 :class:`.NullPool`。可以通过 :paramref:`_sa.create_engine.poolclass` 参数指定使用 :class:`.NullPool` 类。

.. tab:: 英文

    The ``sqlite3`` DBAPI by default prohibits the use of a particular connection
    in a thread which is not the one in which it was created.  As SQLite has
    matured, it's behavior under multiple threads has improved, and even includes
    options for memory only databases to be used in multiple threads.

    The thread prohibition is known as "check same thread" and may be controlled
    using the ``sqlite3`` parameter ``check_same_thread``, which will disable or
    enable this check. SQLAlchemy's default behavior here is to set
    ``check_same_thread`` to ``False`` automatically whenever a file-based database
    is in use, to establish compatibility with the default pool class
    :class:`.QueuePool`.

    The SQLAlchemy ``pysqlite`` DBAPI establishes the connection pool differently
    based on the kind of SQLite database that's requested:

    * When a ``:memory:`` SQLite database is specified, the dialect by default
      will use :class:`.SingletonThreadPool`. This pool maintains a single
      connection per thread, so that all access to the engine within the current
      thread use the same ``:memory:`` database - other threads would access a
      different ``:memory:`` database.  The ``check_same_thread`` parameter
      defaults to ``True``.
    * When a file-based database is specified, the dialect will use
      :class:`.QueuePool` as the source of connections.   at the same time,
      the ``check_same_thread`` flag is set to False by default unless overridden.

      .. versionchanged:: 2.0

        SQLite file database engines now use :class:`.QueuePool` by default.
        Previously, :class:`.NullPool` were used.  The :class:`.NullPool` class
        may be used by specifying it via the
        :paramref:`_sa.create_engine.poolclass` parameter.

禁用文件数据库的连接池
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disabling Connection Pooling for File Databases

.. tab:: 中文

    若要禁用基于文件的数据库的连接池行为，可通过 :func:`_sa.create_engine.poolclass` 参数指定使用 :class:`.NullPool` 实现类::

        from sqlalchemy import NullPool

        engine = create_engine("sqlite:///myfile.db", poolclass=NullPool)

    观察表明：由于 :class:`.QueuePool` 实现了连接复用，使用 :class:`.NullPool` 实现类在频繁获取连接时会带来极小的性能开销。然而，如果应用遇到了文件被锁定的问题，使用该类可能会带来好处。

.. tab:: 英文

    Pooling may be disabled for a file based database by specifying the
    :class:`.NullPool` implementation for the :func:`_sa.create_engine.poolclass`
    parameter::

        from sqlalchemy import NullPool

        engine = create_engine("sqlite:///myfile.db", poolclass=NullPool)

    It's been observed that the :class:`.NullPool` implementation incurs an
    extremely small performance overhead for repeated checkouts due to the lack of
    connection re-use implemented by :class:`.QueuePool`.  However, it still
    may be beneficial to use this class if the application is experiencing
    issues with files being locked.

在多线程中使用内存数据库
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using a Memory Database in Multiple Threads

.. tab:: 中文

    若要在多线程场景中使用 ``:memory:`` 数据库，必须在线程间共享同一个连接对象，因为该数据库仅存在于该连接的作用域中。可使用 :class:`.StaticPool` 实现类在全局维持一个连接，并将 ``check_same_thread`` 参数设置为 ``False`` 传递给 Pysqlite::

        from sqlalchemy.pool import StaticPool

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    请注意，在多线程中使用 ``:memory:`` 数据库需要较新的 SQLite 版本。

.. tab:: 英文

    To use a ``:memory:`` database in a multithreaded scenario, the same
    connection object must be shared among threads, since the database exists
    only within the scope of that connection.   The
    :class:`.StaticPool` implementation will maintain a single connection
    globally, and the ``check_same_thread`` flag can be passed to Pysqlite
    as ``False``::

        from sqlalchemy.pool import StaticPool

        engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )

    Note that using a ``:memory:`` database in multiple threads requires a recent
    version of SQLite.

在 SQLite 中使用临时表
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Temporary Tables with SQLite

.. tab:: 中文

    由于 SQLite 对临时表的处理方式，如果希望在基于文件的 SQLite 数据库中跨多个连接池连接使用临时表（例如在使用 ORM 的 :class:`.Session` 时希望在调用 :meth:`.Session.commit` 或 :meth:`.Session.rollback` 后临时表仍保留），必须使用仅维护单个连接的连接池。如果作用域仅限于当前线程，请使用 :class:`.SingletonThreadPool`；若需要跨线程作用域，请使用 :class:`.StaticPool`::

        # 每个线程维持同一个连接
        from sqlalchemy.pool import SingletonThreadPool

        engine = create_engine("sqlite:///mydb.db", poolclass=SingletonThreadPool)


        # 所有线程共享同一个连接
        from sqlalchemy.pool import StaticPool

        engine = create_engine("sqlite:///mydb.db", poolclass=StaticPool)

    注意，:class:`.SingletonThreadPool` 应针对使用的线程数量进行配置；超过该数量后，连接将以不确定方式被关闭。

.. tab:: 英文

    Due to the way SQLite deals with temporary tables, if you wish to use a
    temporary table in a file-based SQLite database across multiple checkouts
    from the connection pool, such as when using an ORM :class:`.Session` where
    the temporary table should continue to remain after :meth:`.Session.commit` or
    :meth:`.Session.rollback` is called, a pool which maintains a single
    connection must be used.   Use :class:`.SingletonThreadPool` if the scope is
    only needed within the current thread, or :class:`.StaticPool` is scope is
    needed within multiple threads for this case::

        # maintain the same connection per thread
        from sqlalchemy.pool import SingletonThreadPool

        engine = create_engine("sqlite:///mydb.db", poolclass=SingletonThreadPool)


        # maintain the same connection across all threads
        from sqlalchemy.pool import StaticPool

        engine = create_engine("sqlite:///mydb.db", poolclass=StaticPool)

    Note that :class:`.SingletonThreadPool` should be configured for the number
    of threads that are to be used; beyond that number, connections will be
    closed out in a non deterministic way.


处理混合字符串/二进制列
------------------------------------------------------

Dealing with Mixed String / Binary Columns

.. tab:: 中文

    SQLite 是弱类型数据库，因此在使用二进制值时（在 Python 中表示为 ``b'some string'`` ），某些 SQLite 数据库中的某些行可能返回为 ``b''`` 值，而其他则可能返回为 Python 字符串（如 ``''`` 值）。如果始终使用 SQLAlchemy 的 :class:`.LargeBinary` 数据类型，这种情况不会发生；但若某个 SQLite 数据库的数据是通过 Pysqlite 驱动直接插入的，或者先使用了 SQLAlchemy 的 :class:`.String` 类型后又更改为 :class:`.LargeBinary`，则该表可能无法被一致读取，因为 :class:`.LargeBinary` 类型不会处理字符串，因此无法“编码”字符串格式的值。

    若要处理某个列中同时包含字符串/二进制混合数据的 SQLite 表，可使用一个自定义类型来对每一行进行检查处理::

        from sqlalchemy import String
        from sqlalchemy import TypeDecorator


        class MixedBinary(TypeDecorator):
            impl = String
            cache_ok = True

            def process_result_value(self, value, dialect):
                if isinstance(value, str):
                    value = bytes(value, "utf-8")
                elif value is not None:
                    value = bytes(value)

                return value

    然后在需要使用 :class:`.LargeBinary` 的地方，改为使用上述 ``MixedBinary`` 数据类型。

.. tab:: 英文

    The SQLite database is weakly typed, and as such it is possible when using
    binary values, which in Python are represented as ``b'some string'``, that a
    particular SQLite database can have data values within different rows where
    some of them will be returned as a ``b''`` value by the Pysqlite driver, and
    others will be returned as Python strings, e.g. ``''`` values.   This situation
    is not known to occur if the SQLAlchemy :class:`.LargeBinary` datatype is used
    consistently, however if a particular SQLite database has data that was
    inserted using the Pysqlite driver directly, or when using the SQLAlchemy
    :class:`.String` type which was later changed to :class:`.LargeBinary`, the
    table will not be consistently readable because SQLAlchemy's
    :class:`.LargeBinary` datatype does not handle strings so it has no way of
    "encoding" a value that is in string format.

    To deal with a SQLite table that has mixed string / binary data in the
    same column, use a custom type that will check each row individually::

        from sqlalchemy import String
        from sqlalchemy import TypeDecorator


        class MixedBinary(TypeDecorator):
            impl = String
            cache_ok = True

            def process_result_value(self, value, dialect):
                if isinstance(value, str):
                    value = bytes(value, "utf-8")
                elif value is not None:
                    value = bytes(value)

                return value

    Then use the above ``MixedBinary`` datatype in the place where
    :class:`.LargeBinary` would normally be used.

.. _pysqlite_serializable:

可序列化隔离/保存点/事务性 DDL
-------------------------------------------------------

Serializable isolation / Savepoints / Transactional DDL

.. tab:: 中文

    在 :ref:`sqlite_concurrency` 一节中，我们提到了 pysqlite 驱动存在的一系列问题，这些问题阻碍了 SQLite 若干特性的正常工作。pysqlite DBAPI 驱动存在若干长期未修复的 bug，影响其事务行为的正确性。在默认操作模式下，SQLite 的一些功能（如 SERIALIZABLE 隔离级别、事务性的 DDL 以及 SAVEPOINT 支持）是无效的，要使用这些功能就必须采用一些变通方法。

    问题的本质在于，驱动试图“猜测”用户的意图，常常不会启动事务，有时甚至会过早结束事务，其目的是尽可能减少 SQLite 的文件锁定行为，尽管 SQLite 自身在只读操作中使用的是“共享”锁。

    SQLAlchemy 默认不会更改该行为，因为这是 pysqlite 驱动长期以来的预期行为；如果 pysqlite 驱动未来修复了这些问题，那么 SQLAlchemy 的默认行为可能也会随之改变。

    好消息是，我们可以通过几个事件监听器完全实现事务支持：即完全禁用 pysqlite 的自动事务行为，并由我们自行发出 BEGIN 语句。下面展示了如何通过两个事件监听器来实现这一点::

        from sqlalchemy import create_engine, event

        engine = create_engine("sqlite:///myfile.db")


        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # 完全禁用 pysqlite 的 BEGIN 发出行为。
            # 同时也会阻止其在任何 DDL 前自动发出 COMMIT。
            dbapi_connection.isolation_level = None


        @event.listens_for(engine, "begin")
        def do_begin(conn):
            # 手动发出 BEGIN
            conn.exec_driver_sql("BEGIN")

    .. warning:: 使用上述方案时，不建议在 SQLite 驱动中使用
       :class:`_engine.Connection` 与 :func:`_sa.create_engine` 的
       :paramref:`.Connection.execution_options.isolation_level` 设置，
       因为该设置也会更改 ``.isolation_level`` 的值，影响上述逻辑。

    如上，我们在每次创建新的 pysqlite 连接时拦截它，并禁用其事务集成功能。然后，在 SQLAlchemy 知道事务范围即将开始时，由我们自己发出 ``"BEGIN"``。

    一旦我们掌控了 ``"BEGIN"``，也就可以直接控制 SQLite 的锁模式（详见：
    `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_），
    可以将所需的锁模式添加到 ``"BEGIN"`` 语句中::

        @event.listens_for(engine, "begin")
        def do_begin(conn):
            conn.exec_driver_sql("BEGIN EXCLUSIVE")

    .. seealso::

        `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_ -
        来自 SQLite 官方文档

        `sqlite3 SELECT does not BEGIN a transaction <https://bugs.python.org/issue9924>`_ -
        来自 Python bug 跟踪系统

        `sqlite3 module breaks transactions and potentially corrupts data <https://bugs.python.org/issue10740>`_ -
        来自 Python bug 跟踪系统

.. tab:: 英文

    In the section :ref:`sqlite_concurrency`, we refer to the pysqlite
    driver's assortment of issues that prevent several features of SQLite
    from working correctly.  The pysqlite DBAPI driver has several
    long-standing bugs which impact the correctness of its transactional
    behavior.   In its default mode of operation, SQLite features such as
    SERIALIZABLE isolation, transactional DDL, and SAVEPOINT support are
    non-functional, and in order to use these features, workarounds must
    be taken.

    The issue is essentially that the driver attempts to second-guess the user's
    intent, failing to start transactions and sometimes ending them prematurely, in
    an effort to minimize the SQLite databases's file locking behavior, even
    though SQLite itself uses "shared" locks for read-only activities.

    SQLAlchemy chooses to not alter this behavior by default, as it is the
    long-expected behavior of the pysqlite driver; if and when the pysqlite
    driver attempts to repair these issues, that will be more of a driver towards
    defaults for SQLAlchemy.

    The good news is that with a few events, we can implement transactional
    support fully, by disabling pysqlite's feature entirely and emitting BEGIN
    ourselves. This is achieved using two event listeners::

        from sqlalchemy import create_engine, event

        engine = create_engine("sqlite:///myfile.db")


        @event.listens_for(engine, "connect")
        def do_connect(dbapi_connection, connection_record):
            # disable pysqlite's emitting of the BEGIN statement entirely.
            # also stops it from emitting COMMIT before any DDL.
            dbapi_connection.isolation_level = None


        @event.listens_for(engine, "begin")
        def do_begin(conn):
            # emit our own BEGIN
            conn.exec_driver_sql("BEGIN")

    .. warning:: When using the above recipe, it is advised to not use the
       :paramref:`.Connection.execution_options.isolation_level` setting on
       :class:`_engine.Connection` and :func:`_sa.create_engine`
       with the SQLite driver,
       as this function necessarily will also alter the ".isolation_level" setting.


    Above, we intercept a new pysqlite connection and disable any transactional
    integration.   Then, at the point at which SQLAlchemy knows that transaction
    scope is to begin, we emit ``"BEGIN"`` ourselves.

    When we take control of ``"BEGIN"``, we can also control directly SQLite's
    locking modes, introduced at
    `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_,
    by adding the desired locking mode to our ``"BEGIN"``::

        @event.listens_for(engine, "begin")
        def do_begin(conn):
            conn.exec_driver_sql("BEGIN EXCLUSIVE")

    .. seealso::

        `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_ -
        on the SQLite site

        `sqlite3 SELECT does not BEGIN a transaction <https://bugs.python.org/issue9924>`_ -
        on the Python bug tracker

        `sqlite3 module breaks transactions and potentially corrupts data <https://bugs.python.org/issue10740>`_ -
        on the Python bug tracker

.. _pysqlite_udfs:

用户定义函数
----------------------

User-Defined Functions

.. tab:: 中文

    pysqlite 支持一个 `create_function() <https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.create_function>`_
    方法，允许我们用 Python 定义自定义函数（UDF）并在 SQLite 查询中直接使用。这些函数会注册到特定的 DBAPI 连接上。

    SQLAlchemy 在使用基于文件的 SQLite 数据库时启用了连接池，因此我们需要确保在连接创建时将 UDF 附加到连接上。可通过事件监听器实现::

        from sqlalchemy import create_engine
        from sqlalchemy import event
        from sqlalchemy import text


        def udf():
            return "udf-ok"


        engine = create_engine("sqlite:///./db_file")


        @event.listens_for(engine, "connect")
        def connect(conn, rec):
            conn.create_function("udf", 0, udf)


        for i in range(5):
            with engine.connect() as conn:
                print(conn.scalar(text("SELECT UDF()")))

.. tab:: 英文

    pysqlite supports a `create_function() <https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.create_function>`_
    method that allows us to create our own user-defined functions (UDFs) in Python and use them directly in SQLite queries.
    These functions are registered with a specific DBAPI Connection.

    SQLAlchemy uses connection pooling with file-based SQLite databases, so we need to ensure that the UDF is attached to the
    connection when it is created. That is accomplished with an event listener::

        from sqlalchemy import create_engine
        from sqlalchemy import event
        from sqlalchemy import text


        def udf():
            return "udf-ok"


        engine = create_engine("sqlite:///./db_file")


        @event.listens_for(engine, "connect")
        def connect(conn, rec):
            conn.create_function("udf", 0, udf)


        for i in range(5):
            with engine.connect() as conn:
                print(conn.scalar(text("SELECT UDF()")))

"""  # noqa

import math
import os
import re

from .base import DATE
from .base import DATETIME
from .base import SQLiteDialect
from ... import exc
from ... import pool
from ... import types as sqltypes
from ... import util


class _SQLite_pysqliteTimeStamp(DATETIME):
    def bind_processor(self, dialect):
        if dialect.native_datetime:
            return None
        else:
            return DATETIME.bind_processor(self, dialect)

    def result_processor(self, dialect, coltype):
        if dialect.native_datetime:
            return None
        else:
            return DATETIME.result_processor(self, dialect, coltype)


class _SQLite_pysqliteDate(DATE):
    def bind_processor(self, dialect):
        if dialect.native_datetime:
            return None
        else:
            return DATE.bind_processor(self, dialect)

    def result_processor(self, dialect, coltype):
        if dialect.native_datetime:
            return None
        else:
            return DATE.result_processor(self, dialect, coltype)


class SQLiteDialect_pysqlite(SQLiteDialect):
    default_paramstyle = "qmark"
    supports_statement_cache = True
    returns_native_bytes = True

    colspecs = util.update_copy(
        SQLiteDialect.colspecs,
        {
            sqltypes.Date: _SQLite_pysqliteDate,
            sqltypes.TIMESTAMP: _SQLite_pysqliteTimeStamp,
        },
    )

    description_encoding = None

    driver = "pysqlite"

    @classmethod
    def import_dbapi(cls):
        from sqlite3 import dbapi2 as sqlite

        return sqlite

    @classmethod
    def _is_url_file_db(cls, url):
        if (url.database and url.database != ":memory:") and (
            url.query.get("mode", None) != "memory"
        ):
            return True
        else:
            return False

    @classmethod
    def get_pool_class(cls, url):
        if cls._is_url_file_db(url):
            return pool.QueuePool
        else:
            return pool.SingletonThreadPool

    def _get_server_version_info(self, connection):
        return self.dbapi.sqlite_version_info

    _isolation_lookup = SQLiteDialect._isolation_lookup.union(
        {
            "AUTOCOMMIT": None,
        }
    )

    def set_isolation_level(self, dbapi_connection, level):
        if level == "AUTOCOMMIT":
            dbapi_connection.isolation_level = None
        else:
            dbapi_connection.isolation_level = ""
            return super().set_isolation_level(dbapi_connection, level)

    def on_connect(self):
        def regexp(a, b):
            if b is None:
                return None
            return re.search(a, b) is not None

        if self._get_server_version_info(None) >= (3, 9):
            # sqlite must be greater than 3.8.3 for deterministic=True
            # https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.create_function
            # the check is more conservative since there were still issues
            # with following 3.8 sqlite versions
            create_func_kw = {"deterministic": True}
        else:
            create_func_kw = {}

        def set_regexp(dbapi_connection):
            dbapi_connection.create_function("regexp", 2, regexp, **create_func_kw)

        def floor_func(dbapi_connection):
            # NOTE: floor is optionally present in sqlite 3.35+ , however
            # as it is normally non-present we deliver floor() unconditionally
            # for now.
            # https://www.sqlite.org/lang_mathfunc.html
            dbapi_connection.create_function("floor", 1, math.floor, **create_func_kw)

        fns = [set_regexp, floor_func]

        def connect(conn):
            for fn in fns:
                fn(conn)

        return connect

    def create_connect_args(self, url):
        if url.username or url.password or url.host or url.port:
            raise exc.ArgumentError(
                "Invalid SQLite URL: %s\n"
                "Valid SQLite URL forms are:\n"
                " sqlite:///:memory: (or, sqlite://)\n"
                " sqlite:///relative/path/to/file.db\n"
                " sqlite:////absolute/path/to/file.db" % (url,)
            )

        # theoretically, this list can be augmented, at least as far as
        # parameter names accepted by sqlite3/pysqlite, using
        # inspect.getfullargspec().  for the moment this seems like overkill
        # as these parameters don't change very often, and as always,
        # parameters passed to connect_args will always go to the
        # sqlite3/pysqlite driver.
        pysqlite_args = [
            ("uri", bool),
            ("timeout", float),
            ("isolation_level", str),
            ("detect_types", int),
            ("check_same_thread", bool),
            ("cached_statements", int),
        ]
        opts = url.query
        pysqlite_opts = {}
        for key, type_ in pysqlite_args:
            util.coerce_kw_type(opts, key, type_, dest=pysqlite_opts)

        if pysqlite_opts.get("uri", False):
            uri_opts = dict(opts)
            # here, we are actually separating the parameters that go to
            # sqlite3/pysqlite vs. those that go the SQLite URI.  What if
            # two names conflict?  again, this seems to be not the case right
            # now, and in the case that new names are added to
            # either side which overlap, again the sqlite3/pysqlite parameters
            # can be passed through connect_args instead of in the URL.
            # If SQLite native URIs add a parameter like "timeout" that
            # we already have listed here for the python driver, then we need
            # to adjust for that here.
            for key, type_ in pysqlite_args:
                uri_opts.pop(key, None)
            filename = url.database
            if uri_opts:
                # sorting of keys is for unit test support
                filename += "?" + (
                    "&".join("%s=%s" % (key, uri_opts[key]) for key in sorted(uri_opts))
                )
        else:
            filename = url.database or ":memory:"
            if filename != ":memory:":
                filename = os.path.abspath(filename)

        pysqlite_opts.setdefault("check_same_thread", not self._is_url_file_db(url))

        return ([filename], pysqlite_opts)

    def is_disconnect(self, e, connection, cursor):
        return isinstance(
            e, self.dbapi.ProgrammingError
        ) and "Cannot operate on a closed database." in str(e)


dialect = SQLiteDialect_pysqlite


class _SQLiteDialect_pysqlite_numeric(SQLiteDialect_pysqlite):
    """numeric dialect for testing only

    internal use only.  This dialect is **NOT** supported by SQLAlchemy
    and may change at any time.

    """

    supports_statement_cache = True
    default_paramstyle = "numeric"
    driver = "pysqlite_numeric"

    _first_bind = ":1"
    _not_in_statement_regexp = None

    def __init__(self, *arg, **kw):
        kw.setdefault("paramstyle", "numeric")
        super().__init__(*arg, **kw)

    def create_connect_args(self, url):
        arg, opts = super().create_connect_args(url)
        opts["factory"] = self._fix_sqlite_issue_99953()
        return arg, opts

    def _fix_sqlite_issue_99953(self):
        import sqlite3

        first_bind = self._first_bind
        if self._not_in_statement_regexp:
            nis = self._not_in_statement_regexp

            def _test_sql(sql):
                m = nis.search(sql)
                assert not m, f"Found {nis.pattern!r} in {sql!r}"

        else:

            def _test_sql(sql):
                pass

        def _numeric_param_as_dict(parameters):
            if parameters:
                assert isinstance(parameters, tuple)
                return {str(idx): value for idx, value in enumerate(parameters, 1)}
            else:
                return ()

        class SQLiteFix99953Cursor(sqlite3.Cursor):
            def execute(self, sql, parameters=()):
                _test_sql(sql)
                if first_bind in sql:
                    parameters = _numeric_param_as_dict(parameters)
                return super().execute(sql, parameters)

            def executemany(self, sql, parameters):
                _test_sql(sql)
                if first_bind in sql:
                    parameters = [_numeric_param_as_dict(p) for p in parameters]
                return super().executemany(sql, parameters)

        class SQLiteFix99953Connection(sqlite3.Connection):
            def cursor(self, factory=None):
                if factory is None:
                    factory = SQLiteFix99953Cursor
                return super().cursor(factory=factory)

            def execute(self, sql, parameters=()):
                _test_sql(sql)
                if first_bind in sql:
                    parameters = _numeric_param_as_dict(parameters)
                return super().execute(sql, parameters)

            def executemany(self, sql, parameters):
                _test_sql(sql)
                if first_bind in sql:
                    parameters = [_numeric_param_as_dict(p) for p in parameters]
                return super().executemany(sql, parameters)

        return SQLiteFix99953Connection


class _SQLiteDialect_pysqlite_dollar(_SQLiteDialect_pysqlite_numeric):
    """numeric dialect that uses $ for testing only

    internal use only.  This dialect is **NOT** supported by SQLAlchemy
    and may change at any time.

    """

    supports_statement_cache = True
    default_paramstyle = "numeric_dollar"
    driver = "pysqlite_dollar"

    _first_bind = "$1"
    _not_in_statement_regexp = re.compile(r"[^\d]:\d+")

    def __init__(self, *arg, **kw):
        kw.setdefault("paramstyle", "numeric_dollar")
        super().__init__(*arg, **kw)
