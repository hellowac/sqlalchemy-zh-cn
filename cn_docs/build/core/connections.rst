.. _connections_toplevel:

====================================
使用Engines和Connection
====================================

Working with Engines and Connections

.. module:: sqlalchemy.engine

.. tab:: 中文

    本节详细介绍了 :class:`_engine.Engine` ，:class:`_engine.Connection` 及相关对象的直接使用。需要注意的是，当使用SQLAlchemy ORM时，通常不会直接访问这些对象；取而代之的是使用 :class:`.Session` 对象作为数据库接口。然而，对于围绕直接使用文本SQL语句和/或SQL表达式构造而构建的应用程序，不涉及ORM的高级管理服务， :class:`_engine.Engine` 和 :class:`_engine.Connection` 是关键对象 - 继续阅读。

.. tab:: 英文

    This section details direct usage of the :class:`_engine.Engine`,
    :class:`_engine.Connection`, and related objects. Its important to note that when
    using the SQLAlchemy ORM, these objects are not generally accessed; instead,
    the :class:`.Session` object is used as the interface to the database.
    However, for applications that are built around direct usage of textual SQL
    statements and/or SQL expression constructs without involvement by the ORM's
    higher level management services, the :class:`_engine.Engine` and
    :class:`_engine.Connection` are king (and queen?) - read on.

基本用法
-----------

Basic Usage

.. tab:: 中文

    回顾 :doc:`/core/engines` 中的内容，:class:`_engine.Engine` 是通过调用 :func:`_sa.create_engine` 创建的::

        engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test")

    :func:`_sa.create_engine` 的典型用法是针对某个特定数据库 URL 只调用一次，并在整个应用程序进程的生命周期中全局持有。一个 :class:`_engine.Engine` 实例代表应用程序进程的一组 :term:`DBAPI` 连接，并设计为可在并发场景中被调用。:class:`_engine.Engine` **并不等同于** DBAPI 的 ``connect()`` 函数，后者仅代表一个单一的连接资源。:class:`_engine.Engine` 最有效的使用方式是只创建一次，位于应用程序的模块级别，而不是在每个对象或函数调用中重复创建。

    .. sidebar:: 提示

        当在多个 Python 进程中使用 :class:`_engine.Engine`（例如使用 ``os.fork`` 或 Python 的 ``multiprocessing`` 时），
        每个进程都应单独初始化一个 Engine。详见 :ref:`pooling_multiprocessing`。

    :class:`_engine.Engine` 最基本的功能是提供访问 :class:`_engine.Connection` 的方式，后者可用来执行 SQL 语句。向数据库发送文本语句的基本方式如下::

        from sqlalchemy import text

        with engine.connect() as connection:
            result = connection.execute(text("select username from users"))
            for row in result:
                print("username:", row.username)

    如上所示，:meth:`_engine.Engine.connect` 方法返回一个 :class:`_engine.Connection` 对象，并通过 Python 的上下文管理器（即 ``with:`` 语句）使用，在代码块结束时会自动调用 :meth:`_engine.Connection.close` 方法。:class:`_engine.Connection` 是一个实际 DBAPI 连接的 **代理** 对象。该 DBAPI 连接在创建 :class:`_engine.Connection` 时从连接池中获取。

    返回的对象是 :class:`_engine.CursorResult`，它引用了一个 DBAPI 游标，并提供与 DBAPI 游标类似的获取行的方法。当其所有结果行（如果有）都被消费后，:class:`_engine.CursorResult` 将关闭该 DBAPI 游标。若没有返回结果行（例如 UPDATE 语句），游标资源会在构造时立即被释放。

    当 ``with:`` 代码块结束时关闭 :class:`_engine.Connection`，所引用的 DBAPI 连接会被 :term:`释放` 到连接池中。从数据库的角度来看，连接池通常不会真正“关闭”连接，而是将其保留以供下次使用。在连接返回池中等待复用时，连接池机制会对 DBAPI 连接执行 ``rollback()``，以移除事务状态或锁（该过程称为 :ref:`pool_reset_on_return`），从而使连接为下次使用做好准备。

    上面的例子演示了如何执行一个 SQL 字符串，这种字符串应通过 :func:`_expression.text` 构造来调用，以表明我们要使用文本 SQL。当然，:meth:`_engine.Connection.execute` 方法还支持更多功能；详见 :ref:`unified_tutorial` 中的 :ref:`tutorial_working_with_data` 教程。

.. tab:: 英文

    Recall from :doc:`/core/engines` that an :class:`_engine.Engine` is created via
    the :func:`_sa.create_engine` call::

        engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test")

    The typical usage of :func:`_sa.create_engine` is once per particular database
    URL, held globally for the lifetime of a single application process. A single
    :class:`_engine.Engine` manages many individual :term:`DBAPI` connections on behalf of
    the process and is intended to be called upon in a concurrent fashion. The
    :class:`_engine.Engine` is **not** synonymous to the DBAPI ``connect()`` function, which
    represents just one connection resource - the :class:`_engine.Engine` is most
    efficient when created just once at the module level of an application, not
    per-object or per-function call.

    .. sidebar:: tip

        When using an :class:`_engine.Engine` with multiple Python processes, such as when
        using ``os.fork`` or Python ``multiprocessing``, it's important that the
        engine is initialized per process.  See :ref:`pooling_multiprocessing` for
        details.

    The most basic function of the :class:`_engine.Engine` is to provide access to a
    :class:`_engine.Connection`, which can then invoke SQL statements.   To emit
    a textual statement to the database looks like::

        from sqlalchemy import text

        with engine.connect() as connection:
            result = connection.execute(text("select username from users"))
            for row in result:
                print("username:", row.username)

    Above, the :meth:`_engine.Engine.connect` method returns a :class:`_engine.Connection`
    object, and by using it in a Python context manager (e.g. the ``with:``
    statement) the :meth:`_engine.Connection.close` method is automatically invoked at the
    end of the block.  The :class:`_engine.Connection`, is a **proxy** object for an
    actual DBAPI connection. The DBAPI connection is retrieved from the connection
    pool at the point at which :class:`_engine.Connection` is created.

    The object returned is known as :class:`_engine.CursorResult`, which
    references a DBAPI cursor and provides methods for fetching rows
    similar to that of the DBAPI cursor.   The DBAPI cursor will be closed
    by the :class:`_engine.CursorResult` when all of its result rows (if any) are
    exhausted.  A :class:`_engine.CursorResult` that returns no rows, such as that of
    an UPDATE statement (without any returned rows),
    releases cursor resources immediately upon construction.

    When the :class:`_engine.Connection` is closed at the end of the ``with:`` block, the
    referenced DBAPI connection is :term:`released` to the connection pool.   From
    the perspective of the database itself, the connection pool will not actually
    "close" the connection assuming the pool has room to store this connection  for
    the next use.  When the connection is returned to the pool for re-use, the
    pooling mechanism issues a ``rollback()`` call on the DBAPI connection so that
    any transactional state or locks are removed (this is known as
    :ref:`pool_reset_on_return`), and the connection is ready for its next use.

    Our example above illustrated the execution of a textual SQL string, which
    should be invoked by using the :func:`_expression.text` construct to indicate that
    we'd like to use textual SQL.  The :meth:`_engine.Connection.execute` method can of
    course accommodate more than that; see :ref:`tutorial_working_with_data`
    in the :ref:`unified_tutorial` for a tutorial.


使用事务
------------------

Using Transactions

.. tab:: 中文

    .. note::

        本节介绍在直接使用 :class:`_engine.Engine` 和 :class:`_engine.Connection` 对象时如何处理事务。
        若使用 SQLAlchemy ORM，事务控制的公共 API 是通过 :class:`.Session` 对象实现的，后者在内部使用 :class:`.Transaction` 对象。
        更多内容参见 :ref:`unitofwork_transaction`。

.. tab:: 英文

    .. note::

        This section describes how to use transactions when working directly
        with :class:`_engine.Engine` and :class:`_engine.Connection` objects. When using the
        SQLAlchemy ORM, the public API for transaction control is via the
        :class:`.Session` object, which makes usage of the :class:`.Transaction`
        object internally. See :ref:`unitofwork_transaction` for further
        information.

随时提交
~~~~~~~~~~~~~~~~

Commit As You Go

.. tab:: 中文

    :class:`~sqlalchemy.engine.Connection` 对象始终在事务块的上下文中执行 SQL 语句。首次调用 :meth:`_engine.Connection.execute` 方法执行 SQL 语句时，事务会自动开始，这种行为称为 **autobegin**。事务在 :class:`_engine.Connection` 对象的作用域内持续，直到调用 :meth:`_engine.Connection.commit` 或 :meth:`_engine.Connection.rollback` 方法。事务结束后，:class:`_engine.Connection` 会等待下一次调用 :meth:`_engine.Connection.execute`，此时会再次自动开启一个新事务。

    这种调用风格被称为 **commit as you go**，如下例所示::

        with engine.connect() as connection:
            connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

            connection.commit()  # 提交事务

    .. topic:: Python 的 DBAPI 是 autobegin 实际发生的地方

        “commit as you go” 的设计旨在与 :term:`DBAPI`（SQLAlchemy 所使用的底层数据库接口）的行为相辅相成。
        在 DBAPI 中，``connection`` 对象不会假设对数据库的更改会自动提交，因此通常需要显式调用 ``connection.commit()`` 方法。
        需要注意的是，DBAPI 本身 **并不包含 begin() 方法**。所有 Python DBAPI 实现都将 “autobegin” 作为管理事务的主要方式，
        并在首次执行 SQL 语句时负责发送类似 BEGIN 的语句。
        SQLAlchemy 的 API 只是以更高层次的 Python 对象重新表达了这一行为。

    在 “commit as you go” 风格中，我们可以在执行一系列通过 :meth:`_engine.Connection.execute` 发出的语句的同时，
    随意调用 :meth:`_engine.Connection.commit` 和 :meth:`_engine.Connection.rollback` 方法；
    每次事务结束后，只要再次执行新语句，就会隐式开启一个新事务::

        with engine.connect() as connection:
            connection.execute(text("<some statement>"))
            connection.commit()  # 提交 “some statement”

            # 开始新事务
            connection.execute(text("<some other statement>"))
            connection.rollback()  # 回滚 “some other statement”

            # 开始新事务
            connection.execute(text("<a third statement>"))
            connection.commit()  # 提交 “a third statement”

    .. versionadded:: 2.0  
        “commit as you go” 风格是 SQLAlchemy 2.0 中的新特性。
        在 SQLAlchemy 1.4 的“过渡”模式中使用“future”风格的 Engine 时也可用。

.. tab:: 英文

    The :class:`~sqlalchemy.engine.Connection` object always emits SQL statements
    within the context of a transaction block.   The first time the
    :meth:`_engine.Connection.execute` method is called to execute a SQL
    statement, this transaction is begun automatically, using a behavior known
    as **autobegin**.  The transaction remains in place for the scope of the
    :class:`_engine.Connection` object until the :meth:`_engine.Connection.commit`
    or :meth:`_engine.Connection.rollback` methods are called.  Subsequent
    to the transaction ending, the :class:`_engine.Connection` waits for the
    :meth:`_engine.Connection.execute` method to be called again, at which point
    it autobegins again.

    This calling style is known as **commit as you go**, and is
    illustrated in the example below::

        with engine.connect() as connection:
            connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

            connection.commit()  # commit the transaction

    .. topic::  the Python DBAPI is where autobegin actually happens

        The design of "commit as you go" is intended to be complementary to the
        design of the :term:`DBAPI`, which is the underlying database interface
        that SQLAlchemy interacts with. In the DBAPI, the ``connection`` object does
        not assume changes to the database will be automatically committed, instead
        requiring in the default case that the ``connection.commit()`` method is
        called in order to commit changes to the database. It should be noted that
        the DBAPI itself **does not have a begin() method at all**.  All
        Python DBAPIs implement "autobegin" as the primary means of managing
        transactions, and handle the job of emitting a statement like BEGIN on the
        connection when SQL statements are first emitted.
        SQLAlchemy's API is basically re-stating this behavior in terms of higher
        level Python objects.

    In "commit as you go" style, we can call upon :meth:`_engine.Connection.commit`
    and :meth:`_engine.Connection.rollback` methods freely within an ongoing
    sequence of other statements emitted using :meth:`_engine.Connection.execute`;
    each time the transaction is ended, and a new statement is
    emitted, a new transaction begins implicitly::

        with engine.connect() as connection:
            connection.execute(text("<some statement>"))
            connection.commit()  # commits "some statement"

            # new transaction starts
            connection.execute(text("<some other statement>"))
            connection.rollback()  # rolls back "some other statement"

            # new transaction starts
            connection.execute(text("<a third statement>"))
            connection.commit()  # commits "a third statement"

    .. versionadded:: 2.0 "commit as you go" style is a new feature of
        SQLAlchemy 2.0.  It is also available in SQLAlchemy 1.4's "transitional"
        mode when using a "future" style engine.

开始一次
~~~~~~~~~~

Begin Once

.. tab:: 中文

    :class:`_engine.Connection` 对象提供了一种更为显式的事务管理风格，称为 **begin once（一次开启）**。与“边提交边执行”（commit as you go）不同，“一次开启”允许显式声明事务的起始点，并且可以将整个事务框定在一个上下文管理器代码块中，这样事务的结束就变成了隐式的。要使用“一次开启”，需调用 :meth:`_engine.Connection.begin` 方法，该方法返回一个代表 DBAPI 事务的 :class:`.Transaction` 对象。  
    该对象也支持通过自身的 :meth:`_engine.Transaction.commit` 和 :meth:`_engine.Transaction.rollback` 方法进行显式管理，但推荐的做法是使用上下文管理器接口：当代码块正常结束时自动提交事务，若发生异常则回滚事务，并在回滚后将异常向外抛出。下面演示了一个“一次开启”代码块的形式::

        with engine.connect() as connection:
            with connection.begin():
                connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
                connection.execute(
                    some_other_table.insert(), {"q": 8, "p": "this is some more data"}
                )

            # transaction is committed（事务已提交）

.. tab:: 英文

    The :class:`_engine.Connection` object provides a more explicit transaction
    management style known as **begin once**. In contrast to "commit as
    you go", "begin once" allows the start point of the transaction to be
    stated explicitly,
    and allows that the transaction itself may be framed out as a context manager
    block so that the end of the transaction is instead implicit. To use
    "begin once", the :meth:`_engine.Connection.begin` method is used, which returns a
    :class:`.Transaction` object which represents the DBAPI transaction.
    This object also supports explicit management via its own
    :meth:`_engine.Transaction.commit` and :meth:`_engine.Transaction.rollback`
    methods, but as a preferred practice also supports the context manager interface,
    where it will commit itself when
    the block ends normally and emit a rollback if an exception is raised, before
    propagating the exception outwards. Below illustrates the form of a "begin
    once" block::

        with engine.connect() as connection:
            with connection.begin():
                connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
                connection.execute(
                    some_other_table.insert(), {"q": 8, "p": "this is some more data"}
                )

            # transaction is committed

从引擎连接并开始一次
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Connect and Begin Once from the Engine

.. tab:: 中文

    上述“一次开启”代码块可以简写为使用 :class:`_engine.Engine` 对象的 :meth:`_engine.Engine.begin` 方法，无需分别调用 :meth:`_engine.Engine.connect` 和 :meth:`_engine.Connection.begin`；  
    :meth:`_engine.Engine.begin` 方法返回一个特殊的上下文管理器，同时维护了 :class:`_engine.Connection` 和 :class:`_engine.Transaction` 的上下文管理::

        with engine.begin() as connection:
            connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

        # transaction is committed, and Connection is released to the connection
        # pool（事务已提交，连接被释放回连接池）

    .. tip::

        在 :meth:`_engine.Engine.begin` 块中，我们可以调用
        :meth:`_engine.Connection.commit` 或 :meth:`_engine.Connection.rollback` 方法，
        提前终止由该代码块自动控制的事务。但如果这样做了，则在代码块结束之前，
        不可再在该 :class:`_engine.Connection` 上执行任何 SQL 操作::

            >>> from sqlalchemy import create_engine
            >>> e = create_engine("sqlite://", echo=True)
            >>> with e.begin() as conn:
            ...     conn.commit()
            ...     conn.begin()
            2021-11-08 09:49:07,517 INFO sqlalchemy.engine.Engine BEGIN (implicit)
            2021-11-08 09:49:07,517 INFO sqlalchemy.engine.Engine COMMIT
            Traceback (most recent call last):
            ...
            sqlalchemy.exc.InvalidRequestError: Can't operate on closed transaction inside
            context manager.  Please complete the context manager before emitting
            further commands.

.. tab:: 英文

    A convenient shorthand form for the above "begin once" block is to use
    the :meth:`_engine.Engine.begin` method at the level of the originating
    :class:`_engine.Engine` object, rather than performing the two separate
    steps of :meth:`_engine.Engine.connect` and :meth:`_engine.Connection.begin`;
    the :meth:`_engine.Engine.begin` method returns a special context manager
    that internally maintains both the context manager for the :class:`_engine.Connection`
    as well as the context manager for the :class:`_engine.Transaction` normally
    returned by the :meth:`_engine.Connection.begin` method::

        with engine.begin() as connection:
            connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

        # transaction is committed, and Connection is released to the connection
        # pool

    .. tip::

        Within the :meth:`_engine.Engine.begin` block, we can call upon the
        :meth:`_engine.Connection.commit` or :meth:`_engine.Connection.rollback`
        methods, which will end the transaction normally demarcated by the block
        ahead of time.  However, if we do so, no further SQL operations may be
        emitted on the :class:`_engine.Connection` until the block ends::

            >>> from sqlalchemy import create_engine
            >>> e = create_engine("sqlite://", echo=True)
            >>> with e.begin() as conn:
            ...     conn.commit()
            ...     conn.begin()
            2021-11-08 09:49:07,517 INFO sqlalchemy.engine.Engine BEGIN (implicit)
            2021-11-08 09:49:07,517 INFO sqlalchemy.engine.Engine COMMIT
            Traceback (most recent call last):
            ...
            sqlalchemy.exc.InvalidRequestError: Can't operate on closed transaction inside
            context manager.  Please complete the context manager before emitting
            further commands.

混合样式
~~~~~~~~~~~~~

Mixing Styles

.. tab:: 中文

    “边提交边执行”和“一次开启”这两种事务风格可以在单个 :meth:`_engine.Engine.connect` 块中自由混用，只要 :meth:`_engine.Connection.begin` 的调用不与“自动开启”（autobegin）机制冲突即可。  
    为此，:meth:`_engine.Connection.begin` 应仅在尚未执行任何 SQL 语句之前，或在前一次调用 :meth:`_engine.Connection.commit` 或 :meth:`_engine.Connection.rollback` 之后调用::

        with engine.connect() as connection:
            with connection.begin():
                # run statements in a "begin once" block（在一次开启块中执行语句）
                connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})

            # transaction is committed（事务已提交）

            # run a new statement outside of a block. The connection
            # autobegins（块外执行语句，连接自动开启事务）
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

            # commit explicitly（显式提交）
            connection.commit()

            # can use a "begin once" block here（此处可再次使用一次开启块）
            with connection.begin():
                # run more statements（执行更多语句）
                connection.execute(...)

    当编写使用“一次开启”风格的代码时，如果事务已经是“自动开启”的状态，SQLAlchemy 会抛出 :class:`_exc.InvalidRequestError` 异常。

.. tab:: 英文

    The "commit as you go" and "begin once" styles can be freely mixed within
    a single :meth:`_engine.Engine.connect` block, provided that the call to
    :meth:`_engine.Connection.begin` does not conflict with the "autobegin"
    behavior.  To accomplish this, :meth:`_engine.Connection.begin` should only
    be called either before any SQL statements have been emitted, or directly
    after a previous call to :meth:`_engine.Connection.commit` or :meth:`_engine.Connection.rollback`::

        with engine.connect() as connection:
            with connection.begin():
                # run statements in a "begin once" block
                connection.execute(some_table.insert(), {"x": 7, "y": "this is some data"})

            # transaction is committed

            # run a new statement outside of a block. The connection
            # autobegins
            connection.execute(
                some_other_table.insert(), {"q": 8, "p": "this is some more data"}
            )

            # commit explicitly
            connection.commit()

            # can use a "begin once" block here
            with connection.begin():
                # run more statements
                connection.execute(...)

    When developing code that uses "begin once", the library will raise
    :class:`_exc.InvalidRequestError` if a transaction was already "autobegun".

.. _dbapi_autocommit:

设置事务隔离级别（包括 DBAPI 自动提交）
---------------------------------------------------------------

Setting Transaction Isolation Levels including DBAPI Autocommit

.. tab:: 中文

    大多数 DBAPI 支持可配置的事务 :term:`隔离级别 <isolation>`，传统上包括四种：“READ UNCOMMITTED”、“READ COMMITTED”、“REPEATABLE READ” 和 “SERIALIZABLE”。  
    这些隔离级别通常在 DBAPI 连接开启新事务之前设置；大多数 DBAPI 在首次发出 SQL 语句时会隐式开启事务。

    支持隔离级别的 DBAPI 通常也支持真正的“自动提交”（autocommit）模式，即 DBAPI 连接处于非事务性模式。  
    这通常意味着 DBAPI 不再自动向数据库发送 “BEGIN” 指令，但也可能包含其他行为。SQLAlchemy 将“自动提交”视作一种隔离级别；  
    它不仅不具备“读提交”的特性，也失去了原子性。

    .. tip::

        需要注意的是，正如下方 :ref:`dbapi_autocommit_understanding` 部分进一步讨论的那样，  
        “自动提交”隔离级别与其他隔离级别一样，**不会影响** :class:`_engine.Connection` 对象的“事务性”行为，  
        它仍会调用 DBAPI 的 ``.commit()`` 和 ``.rollback()`` 方法（只是在自动提交模式下这些方法无效），  
        同样，``.begin()`` 方法假定 DBAPI 会隐式启动一个事务（这意味着 SQLAlchemy 的 "begin" **不会改变自动提交模式**）。

    SQLAlchemy 的方言应尽可能支持这些隔离级别和自动提交模式。

.. tab:: 英文

    Most DBAPIs support the concept of configurable transaction :term:`isolation` levels.
    These are traditionally the four levels "READ UNCOMMITTED", "READ COMMITTED",
    "REPEATABLE READ" and "SERIALIZABLE".  These are usually applied to a
    DBAPI connection before it begins a new transaction, noting that most
    DBAPIs will begin this transaction implicitly when SQL statements are first
    emitted.

    DBAPIs that support isolation levels also usually support the concept of true
    "autocommit", which means that the DBAPI connection itself will be placed into
    a non-transactional autocommit mode. This usually means that the typical DBAPI
    behavior of emitting "BEGIN" to the database automatically no longer occurs,
    but it may also include other directives. SQLAlchemy treats the concept of
    "autocommit" like any other isolation level; in that it is an isolation level
    that loses not only "read committed" but also loses atomicity.

    .. tip::

        It is important to note, as will be discussed further in the section below at
        :ref:`dbapi_autocommit_understanding`, that "autocommit" isolation level like
        any other isolation level does **not** affect the "transactional" behavior of
        the :class:`_engine.Connection` object, which continues to call upon DBAPI
        ``.commit()`` and ``.rollback()`` methods (they just have no effect under
        autocommit), and for which the ``.begin()`` method assumes the DBAPI will
        start a transaction implicitly (which means that SQLAlchemy's "begin" **does
        not change autocommit mode**).

    SQLAlchemy dialects should support these isolation levels as well as autocommit
    to as great a degree as possible.

为连接设置隔离级别或 DBAPI 自动提交
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting Isolation Level or DBAPI Autocommit for a Connection

.. tab:: 中文

    对于通过 :meth:`.Engine.connect` 获取的单个 :class:`_engine.Connection` 对象，可以通过 :meth:`_engine.Connection.execution_options` 方法在该对象的生命周期内设置隔离级别。该参数名为 :paramref:`_engine.Connection.execution_options.isolation_level`，其值通常为以下字符串的子集::

        # Connection.execution_options(isolation_level="<值>") 的可能取值

        "AUTOCOMMIT"
        "READ COMMITTED"
        "READ UNCOMMITTED"
        "REPEATABLE READ"
        "SERIALIZABLE"

    并非所有 DBAPI 都支持上述所有值；如果为某个后端指定了不支持的值，将会引发错误。

    例如，要在某个特定连接上强制使用 REPEATABLE READ，并启动一个事务::

        with engine.connect().execution_options(
            isolation_level="REPEATABLE READ"
        ) as connection:
            with connection.begin():
                connection.execute(text("<statement>"))

    .. tip::  
        :meth:`_engine.Connection.execution_options` 方法的返回值与调用该方法的 :class:`_engine.Connection` 对象相同，  
        即它会就地修改该 :class:`_engine.Connection` 对象的状态。这是 SQLAlchemy 2.0 中的新行为。  
        这种行为不适用于 :meth:`_engine.Engine.execution_options` 方法；后者仍然返回 :class:`.Engine` 的副本，  
        可用于构建多个具有不同执行选项的 :class:`.Engine` 实例，这些实例共享相同的方言和连接池。

    .. note::  
        :paramref:`_engine.Connection.execution_options.isolation_level` 参数不会应用于语句级别的选项，  
        例如 :meth:`_sql.Executable.execution_options`；如果尝试在该级别设置，将被拒绝。  
        因为该选项必须基于每个事务设置在 DBAPI 连接上。

.. tab:: 英文

    For an individual :class:`_engine.Connection` object that's acquired from
    :meth:`.Engine.connect`, the isolation level can be set for the duration of
    that :class:`_engine.Connection` object using the
    :meth:`_engine.Connection.execution_options` method. The parameter is known as
    :paramref:`_engine.Connection.execution_options.isolation_level` and the values
    are strings which are typically a subset of the following names::

        # possible values for Connection.execution_options(isolation_level="<value>")

        "AUTOCOMMIT"
        "READ COMMITTED"
        "READ UNCOMMITTED"
        "REPEATABLE READ"
        "SERIALIZABLE"

    Not every DBAPI supports every value; if an unsupported value is used for a
    certain backend, an error is raised.

    For example, to force REPEATABLE READ on a specific connection, then
    begin a transaction::

        with engine.connect().execution_options(
            isolation_level="REPEATABLE READ"
        ) as connection:
            with connection.begin():
                connection.execute(text("<statement>"))

    .. tip::  The return value of
        the :meth:`_engine.Connection.execution_options` method is the same
        :class:`_engine.Connection` object upon which the method was called,
        meaning, it modifies the state of the :class:`_engine.Connection`
        object in place.  This is a new behavior as of SQLAlchemy 2.0.
        This behavior does not apply to the :meth:`_engine.Engine.execution_options`
        method; that method still returns a copy of the :class:`.Engine` and
        as described below may be used to construct multiple :class:`.Engine`
        objects with different execution options, which nonetheless share the same
        dialect and connection pool.

    .. note:: The :paramref:`_engine.Connection.execution_options.isolation_level`
        parameter necessarily does not apply to statement level options, such as
        that of :meth:`_sql.Executable.execution_options`, and will be rejected if
        set at this level. This because the option must be set on a DBAPI connection
        on a per-transaction basis.

为引擎设置隔离级别或 DBAPI 自动提交
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting Isolation Level or DBAPI Autocommit for an Engine

.. tab:: 中文

    也可以在整个引擎级别设置 :paramref:`_engine.Connection.execution_options.isolation_level` 选项，这通常是更推荐的做法。  
    可以通过向 :func:`.sa.create_engine` 传入 :paramref:`_sa.create_engine.isolation_level` 参数来实现::

        from sqlalchemy import create_engine

        eng = create_engine(
            "postgresql://scott:tiger@localhost/test", isolation_level="REPEATABLE READ"
        )

    上述配置将使每个新创建的 DBAPI 连接在初始化时即采用 ``"REPEATABLE READ"`` 隔离级别，适用于之后的所有操作。

.. tab:: 英文

    The :paramref:`_engine.Connection.execution_options.isolation_level` option may
    also be set engine wide, as is often preferable.  This may be
    achieved by passing the :paramref:`_sa.create_engine.isolation_level`
    parameter to :func:`.sa.create_engine`::

        from sqlalchemy import create_engine

        eng = create_engine(
            "postgresql://scott:tiger@localhost/test", isolation_level="REPEATABLE READ"
        )

    With the above setting, each new DBAPI connection the moment it's created will
    be set to use a ``"REPEATABLE READ"`` isolation level setting for all
    subsequent operations.

.. _dbapi_autocommit_multiple:

为单个引擎维护多个隔离级别
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Maintaining Multiple Isolation Levels for a Single Engine

.. tab:: 中文

    还可以通过其他方式在引擎级别设置隔离级别，提供更多灵活性，例如使用 :func:`_sa.create_engine` 的  
    :paramref:`_sa.create_engine.execution_options` 参数，或使用 :meth:`_engine.Engine.execution_options` 方法。  
    后者会创建一个新的 :class:`.Engine` 副本，该副本与原始引擎共享方言和连接池，但拥有自己的每连接隔离级别设置::

        from sqlalchemy import create_engine

        eng = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test",
            execution_options={"isolation_level": "REPEATABLE READ"},
        )

    使用上述配置后，DBAPI 连接将在每次开启新事务时被设置为 ``"REPEATABLE READ"`` 隔离级别；  
    但当连接返回连接池时，它会被重置为初始隔离级别。  
    从 :func:`_sa.create_engine` 的角度看，其最终效果与使用 :paramref:`_sa.create_engine.isolation_level` 参数并无不同。

    然而，对于频繁需要以不同隔离级别运行操作的应用程序，可能希望基于主 :class:`_engine.Engine` 创建多个“子引擎”，  
    每个引擎配置不同的隔离级别。例如，一个应用将操作划分为“事务性操作”和“只读操作”，  
    此时可以为 ``"AUTOCOMMIT"`` 模式单独创建一个 :class:`_engine.Engine`::

        from sqlalchemy import create_engine

        eng = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = eng.execution_options(isolation_level="AUTOCOMMIT")

    如上，:meth:`_engine.Engine.execution_options` 方法会创建一个原始 :class:`_engine.Engine` 的浅拷贝。  
    ``eng`` 和 ``autocommit_engine`` 共享相同的方言和连接池。  
    但从 ``autocommit_engine`` 获取连接时，会启用 "AUTOCOMMIT" 模式。

    无论使用哪种隔离级别，当连接返回连接池时，该设置都会被无条件重置。

    .. seealso::

        :ref:`SQLite Transaction Isolation <sqlite_isolation_level>`

        :ref:`PostgreSQL Transaction Isolation <postgresql_isolation_level>`

        :ref:`MySQL Transaction Isolation <mysql_isolation_level>`

        :ref:`SQL Server Transaction Isolation <mssql_isolation_level>`

        :ref:`Oracle Database Transaction Isolation <oracle_isolation_level>`

        :ref:`session_transaction_isolation` - 用于 ORM 的事务隔离配置

        :ref:`faq_execute_retry_autocommit` - 使用 DBAPI 自动提交模式自动重连数据库的示例方案

.. tab:: 英文

    The isolation level may also be set per engine, with a potentially greater
    level of flexibility, using either the
    :paramref:`_sa.create_engine.execution_options` parameter to
    :func:`_sa.create_engine` or the :meth:`_engine.Engine.execution_options`
    method, the latter of which will create a copy of the :class:`.Engine` that
    shares the dialect and connection pool of the original engine, but has its own
    per-connection isolation level setting::

        from sqlalchemy import create_engine

        eng = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test",
            execution_options={"isolation_level": "REPEATABLE READ"},
        )

    With the above setting, the DBAPI connection will be set to use a
    ``"REPEATABLE READ"`` isolation level setting for each new transaction
    begun; but the connection as pooled will be reset to the original isolation
    level that was present when the connection first occurred.   At the level
    of :func:`_sa.create_engine`, the end effect is not any different
    from using the :paramref:`_sa.create_engine.isolation_level` parameter.

    However, an application that frequently chooses to run operations within
    different isolation levels may wish to create multiple "sub-engines" of a lead
    :class:`_engine.Engine`, each of which will be configured to a different
    isolation level. One such use case is an application that has operations that
    break into "transactional" and "read-only" operations, a separate
    :class:`_engine.Engine` that makes use of ``"AUTOCOMMIT"`` may be separated off
    from the main engine::

        from sqlalchemy import create_engine

        eng = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = eng.execution_options(isolation_level="AUTOCOMMIT")

    Above, the :meth:`_engine.Engine.execution_options` method creates a shallow
    copy of the original :class:`_engine.Engine`.  Both ``eng`` and
    ``autocommit_engine`` share the same dialect and connection pool.  However, the
    "AUTOCOMMIT" mode will be set upon connections when they are acquired from the
    ``autocommit_engine``.

    The isolation level setting, regardless of which one it is, is unconditionally
    reverted when a connection is returned to the connection pool.


    .. seealso::

        :ref:`SQLite Transaction Isolation <sqlite_isolation_level>`

        :ref:`PostgreSQL Transaction Isolation <postgresql_isolation_level>`

        :ref:`MySQL Transaction Isolation <mysql_isolation_level>`

        :ref:`SQL Server Transaction Isolation <mssql_isolation_level>`

        :ref:`Oracle Database Transaction Isolation <oracle_isolation_level>`

        :ref:`session_transaction_isolation` - for the ORM

        :ref:`faq_execute_retry_autocommit` - a recipe that uses DBAPI autocommit
        to transparently reconnect to the database for read-only operations

.. _dbapi_autocommit_understanding:

了解 DBAPI 级自动提交隔离级别
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Understanding the DBAPI-Level Autocommit Isolation Level

.. tab:: 中文
    
    在上一级章节中，我们介绍了 :paramref:`_engine.Connection.execution_options.isolation_level` 参数的概念，以及它如何用于设置数据库的隔离级别，其中包括被 SQLAlchemy 视为一种事务隔离级别的 DBAPI 级别 “autocommit”（自动提交）。在本节中，我们将尝试澄清这种方法的影响。
    
    如果我们想获取一个 :class:`_engine.Connection` 对象并以 "autocommit" 模式使用它，我们可以按如下方式操作::
    
        with engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text("<statement>"))
            connection.execute(text("<statement>"))
    
    上述示例展示了 "DBAPI autocommit" 模式的正常使用方式。我们无需调用诸如 :meth:`_engine.Connection.begin` 或 :meth:`_engine.Connection.commit` 的方法，因为所有语句都会立即提交到数据库中。当代码块结束时，:class:`_engine.Connection` 对象会恢复 "autocommit" 隔离级别，且 DBAPI 连接会被释放回连接池，此时通常会调用 DBAPI 的 ``connection.rollback()`` 方法，但由于上述语句已提交，这个回滚操作不会对数据库状态产生任何影响。
    
    需要注意的是，即使调用了 :meth:`_engine.Connection.begin` 方法，"autocommit" 模式仍然会持续存在；DBAPI 不会向数据库发送 BEGIN，也不会在调用 :meth:`_engine.Connection.commit` 时发送 COMMIT。这种用法并不是错误场景，因为可以预期某些本应处于事务上下文中的代码，仍可能应用 "autocommit" 隔离级别；归根结底，“隔离级别”只是事务自身的一个配置细节，和其他隔离级别并无区别。
    
    在下方示例中，无论是否存在 SQLAlchemy 级别的事务块，语句依然会 **自动提交**::
    
        with engine.connect() as connection:
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")
    
            # 此 begin() 不会影响 DBAPI 连接，隔离级别仍为 AUTOCOMMIT
            with connection.begin() as trans:
                connection.execute(text("<statement>"))
                connection.execute(text("<statement>"))
    
    如果我们在启用日志的情况下运行如上代码块，日志将试图指出，虽然调用了 DBAPI 级别的 ``.commit()``，但由于 autocommit 模式，这个调用很可能不会产生任何效果：
    
    .. sourcecode:: text
    
        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        ...
        INFO sqlalchemy.engine.Engine COMMIT using DBAPI connection.commit(), DBAPI should ignore due to autocommit mode
    
    与此同时，尽管我们使用的是 "DBAPI autocommit"，SQLAlchemy 的事务语义——也就是 :meth:`_engine.Connection.begin` 在 Python 层面的行为，以及 "autobegin" 的行为—— **仍然有效，即便它们对 DBAPI 连接本身没有影响** 。为了说明这一点，下面的代码将会抛出一个错误，因为在自动开启事务（autobegin）之后又尝试调用 :meth:`_engine.Connection.begin`::
    
        with engine.connect() as connection:
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")
    
            # "transaction" 是自动开启的（但由于 autocommit 并无实际效果）
            connection.execute(text("<statement>"))
    
            # 此处将抛出异常；"transaction" 已经开始
            with connection.begin() as trans:
                connection.execute(text("<statement>"))
    
    上面的示例也再次说明了一个主题：即 "autocommit" 隔离级别只是底层数据库事务的一个配置细节，和 SQLAlchemy Connection 对象的 begin/commit 行为是相互独立的。"autocommit" 模式不会与 :meth:`_engine.Connection.begin` 产生任何交互，:class:`_engine.Connection` 在处理与事务相关的状态变化时，也不会参考这个隔离状态（除了在日志中提示该块并未真正提交事务）。这种设计的理由是为了维护一致的 :class:`_engine.Connection` 使用模式，使得 DBAPI autocommit 模式可以独立更改，而无需在其他地方进行代码调整。

.. tab:: 英文

    In the parent section, we introduced the concept of the
    :paramref:`_engine.Connection.execution_options.isolation_level`
    parameter and how it can be used to set database isolation levels, including
    DBAPI-level "autocommit" which is treated by SQLAlchemy as another transaction
    isolation level.   In this section we will attempt to clarify the implications
    of this approach.

    If we wanted to check out a :class:`_engine.Connection` object and use it
    "autocommit" mode, we would proceed as follows::

        with engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")
            connection.execute(text("<statement>"))
            connection.execute(text("<statement>"))

    Above illustrates normal usage of "DBAPI autocommit" mode.   There is no
    need to make use of methods such as :meth:`_engine.Connection.begin`
    or :meth:`_engine.Connection.commit`, as all statements are committed
    to the database immediately.  When the block ends, the :class:`_engine.Connection`
    object will revert the "autocommit" isolation level, and the DBAPI connection
    is released to the connection pool where the DBAPI ``connection.rollback()``
    method will normally be invoked, but as the above statements were already
    committed, this rollback has no change on the state of the database.

    It is important to note that "autocommit" mode
    persists even when the :meth:`_engine.Connection.begin` method is called;
    the DBAPI will not emit any BEGIN to the database, nor will it emit
    COMMIT when :meth:`_engine.Connection.commit` is called.  This usage is also
    not an error scenario, as it is expected that the "autocommit" isolation level
    may be applied to code that otherwise was written assuming a transactional context;
    the "isolation level" is, after all, a configurational detail of the transaction
    itself just like any other isolation level.

    In the example below, statements remain
    **autocommitting** regardless of SQLAlchemy-level transaction blocks::

        with engine.connect() as connection:
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")

            # this begin() does not affect the DBAPI connection, isolation stays at AUTOCOMMIT
            with connection.begin() as trans:
                connection.execute(text("<statement>"))
                connection.execute(text("<statement>"))

    When we run a block like the above with logging turned on, the logging
    will attempt to indicate that while a DBAPI level ``.commit()`` is called,
    it probably will have no effect due to autocommit mode:

    .. sourcecode:: text

        INFO sqlalchemy.engine.Engine BEGIN (implicit)
        ...
        INFO sqlalchemy.engine.Engine COMMIT using DBAPI connection.commit(), DBAPI should ignore due to autocommit mode

    At the same time, even though we are using "DBAPI autocommit", SQLAlchemy's
    transactional semantics, that is, the in-Python behavior of :meth:`_engine.Connection.begin`
    as well as the behavior of "autobegin", **remain in place, even though these
    don't impact the DBAPI connection itself**.  To illustrate, the code
    below will raise an error, as :meth:`_engine.Connection.begin` is being
    called after autobegin has already occurred::

        with engine.connect() as connection:
            connection = connection.execution_options(isolation_level="AUTOCOMMIT")

            # "transaction" is autobegin (but has no effect due to autocommit)
            connection.execute(text("<statement>"))

            # this will raise; "transaction" is already begun
            with connection.begin() as trans:
                connection.execute(text("<statement>"))

    The above example also demonstrates the same theme that the "autocommit"
    isolation level is a configurational detail of the underlying database
    transaction, and is independent of the begin/commit behavior of the SQLAlchemy
    Connection object. The "autocommit" mode will not interact with
    :meth:`_engine.Connection.begin` in any way and the :class:`_engine.Connection`
    does not consult this status when performing its own state changes with regards
    to the transaction (with the exception of suggesting within engine logging that
    these blocks are not actually committing). The rationale for this design is to
    maintain a completely consistent usage pattern with the
    :class:`_engine.Connection` where DBAPI-autocommit mode can be changed
    independently without indicating any code changes elsewhere.

在隔离级别之间切换
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Changing Between Isolation Levels

.. tab:: 中文
    
    .. topic:: 总结 
    
        建议使用各自具有一个隔离级别的独立 :class:`_engine.Connection` 对象，
        而不要在单个 :class:`_engine.Connection` 上切换隔离级别。
        这样代码更易于阅读，出错概率也更低。
    
    隔离级别设置（包括 autocommit 模式）会在连接释放回连接池时自动重置。因此，尽量避免在一个 :class:`_engine.Connection` 对象上来回切换隔离级别，这样会导致代码冗长。
    
    为了演示如何在一个 :class:`_engine.Connection` 检出范围内临时使用 "autocommit"，需要使用 :paramref:`_engine.Connection.execution_options.isolation_level` 参数重新应用先前的隔离级别。前面的章节中展示了一个示例，即在 autocommit 生效期间调用 :meth:`_engine.Connection.begin` 来开启事务；我们可以通过在调用 :meth:`_engine.Connection.begin` 之前先恢复隔离级别来重写该示例::
    
        # 如果我们想在同一个连接上切换 autocommit 开关/
        # 虽然……我们通常不建议这么做。
    
        with engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")
    
            # 在 autocommit 模式下运行语句
            connection.execute(text("<statement>"))
    
            # “提交” 自动开启的“事务”
            connection.commit()
    
            # 切换回默认隔离级别
            connection.execution_options(isolation_level=connection.default_isolation_level)
    
            # 使用一个 begin 块
            with connection.begin() as trans:
                connection.execute(text("<statement>"))
    
    在上面，我们手动恢复隔离级别时使用了 :attr:`_engine.Connection.default_isolation_level` 属性来还原默认隔离级别（前提是我们确实希望如此）。不过，更好的做法可能是配合 :class:`_engine.Connection` 的架构设计使用，因为它在连接回收时会自动重置隔离级别。上述写法的 **推荐方式** 是使用两个代码块::
    
        # 使用 autocommit 块
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            # 在 autocommit 模式下执行语句
            connection.execute(text("<statement>"))
    
        # 使用普通事务块
        with engine.begin() as connection:
            connection.execute(text("<statement>"))
    
    总结如下：
    
    1. “DBAPI 级别的 autocommit” 隔离级别与 :class:`_engine.Connection` 对象的 “begin” 和 “commit” 概念完全独立；
    2. 每种隔离级别都应使用单独的 :class:`_engine.Connection` 检出；
       避免在同一个连接上来回切换 "autocommit" 状态；应让引擎自动恢复默认隔离级别。

.. tab:: 英文

    .. topic:: TL;DR;
    
        prefer to use individual :class:`_engine.Connection` objects
        each with just one isolation level, rather than switching isolation on a single
        :class:`_engine.Connection`.  The code will be easier to read and less
        error prone.
    
    Isolation level settings, including autocommit mode, are reset automatically
    when the connection is released back to the connection pool. Therefore it is
    preferable to avoid trying to switch isolation levels on a single
    :class:`_engine.Connection` object as this leads to excess verbosity.
    
    To illustrate how to use "autocommit" in an ad-hoc mode within the scope of a
    single :class:`_engine.Connection` checkout, the
    :paramref:`_engine.Connection.execution_options.isolation_level` parameter
    must be re-applied with the previous isolation level.
    The previous section illustrated an attempt to call :meth:`_engine.Connection.begin`
    in order to start a transaction while autocommit was taking place; we can
    rewrite that example to actually do so by first reverting the isolation level
    before we call upon :meth:`_engine.Connection.begin`::
    
        # if we wanted to flip autocommit on and off on a single connection/
        # which... we usually don't.
    
        with engine.connect() as connection:
            connection.execution_options(isolation_level="AUTOCOMMIT")
    
            # run statement(s) in autocommit mode
            connection.execute(text("<statement>"))
    
            # "commit" the autobegun "transaction"
            connection.commit()
    
            # switch to default isolation level
            connection.execution_options(isolation_level=connection.default_isolation_level)
    
            # use a begin block
            with connection.begin() as trans:
                connection.execute(text("<statement>"))
    
    Above, to manually revert the isolation level we made use of
    :attr:`_engine.Connection.default_isolation_level` to restore the default
    isolation level (assuming that's what we want here). However, it's
    probably a better idea to work with the architecture of of the
    :class:`_engine.Connection` which already handles resetting of isolation level
    automatically upon checkin. The **preferred** way to write the above is to
    use two blocks ::
    
        # use an autocommit block
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            # run statement in autocommit mode
            connection.execute(text("<statement>"))
    
        # use a regular block
        with engine.begin() as connection:
            connection.execute(text("<statement>"))
    
    To sum up:
    
    1. "DBAPI level autocommit" isolation level is entirely independent of the
       :class:`_engine.Connection` object's notion of "begin" and "commit"
    2. use individual :class:`_engine.Connection` checkouts per isolation level.
       Avoid trying to change back and forth between "autocommit" on a single
       connection checkout; let the engine do the work of restoring default
       isolation levels

.. _engine_stream_results:

使用服务器端游标（又称流结果）
-------------------------------------------------

Using Server Side Cursors (a.k.a. stream results)

.. tab:: 中文
    
    某些后端明确支持“服务器端游标（server side cursors）”与“客户端游标（client side cursors）”的概念。这里的客户端游标是指数据库驱动在语句执行返回前会将结果集中的所有行完全提取到内存中。像 PostgreSQL 和 MySQL/MariaDB 这样的驱动通常默认使用客户端游标。相比之下，服务器端游标表示结果行在客户端消费时仍保留在数据库服务器的状态中。例如，Oracle 数据库的驱动通常使用“服务器端”模型；而 SQLite 虽然不是真正意义上的“客户端 / 服务器”架构，但它仍采用非缓冲（unbuffered）的结果提取方式，即在消费前结果行并不加载进进程内存。
    
    .. topic:: 我们真正要说的是“缓冲（buffered）”与“非缓冲（unbuffered）”结果
    
        服务器端游标在关系数据库中也意味着更广泛的一组特性，例如可以向前或向后“滚动”游标。
        SQLAlchemy 并未显式支持这些行为；在 SQLAlchemy 中，一般使用“服务器端游标”指代“非缓冲结果”，
        而“客户端游标”则指结果行在返回第一行前就被缓存在内存中。要使用特定 DBAPI 驱动所支持的更丰富的“服务器端游标”特性，
        请参见章节 :ref:`dbapi_connections_cursor`。
    
    基于上述架构，“服务器端游标”在获取非常大的结果集时更具内存效率，
    但与此同时在客户端/服务器通信过程中可能引入更多复杂性，
    对于小型结果集（通常小于 10000 行）则可能效率更低。
    
    对于那些支持缓冲或非缓冲结果的 dialect，在使用“非缓冲”或服务器端游标模式时通常有注意事项。
    例如，在使用 psycopg2 dialect 时，如果对任何 DML 或 DDL 语句使用服务器端游标，会抛出错误。
    在使用 MySQL 驱动的服务器端游标时，DBAPI 连接处于较脆弱的状态，遇到错误时恢复能力较差，
    并且在游标完全关闭前不允许执行回滚操作。
    
    因此，SQLAlchemy 的各个 dialect 总是默认使用更不易出错的游标模式。
    对于 PostgreSQL 和 MySQL dialect，默认使用缓冲的“客户端”游标，
    即在调用任何提取方法之前，完整的结果集会被加载到内存中。
    这种操作模式在 **绝大多数** 场景下都是合适的；
    非缓冲游标通常只在应用程序以分批处理的方式获取大量行时才有用，
    即在提取更多行之前可以处理完当前的一批行。
    
    对于提供客户端与服务器端游标选项的数据库驱动，
    可以通过 :paramref:`_engine.Connection.execution_options.stream_results`
    与 :paramref:`_engine.Connection.execution_options.yield_per` 执行选项，
    在每个 :class:`_engine.Connection` 或每条语句的基础上启用“服务器端游标”。
    在使用 ORM 的 :class:`_orm.Session` 时也存在类似选项。


.. tab:: 英文

    Some backends feature explicit support for the concept of "server side cursors"
    versus "client side cursors".  A client side cursor here means that the
    database driver fully fetches all rows from a result set into memory before
    returning from a statement execution.  Drivers such as those of PostgreSQL and
    MySQL/MariaDB generally use client side cursors by default.  A server side
    cursor, by contrast, indicates that result rows remain pending within the
    database server's state as result rows are consumed by the client.  The drivers
    for Oracle Database generally use a "server side" model, for example, and the
    SQLite dialect, while not using a real "client / server" architecture, still
    uses an unbuffered result fetching approach that will leave result rows outside
    of process memory before they are consumed.

    .. topic:: What we really mean is "buffered" vs. "unbuffered" results

        Server side cursors also imply a wider set of features with relational
        databases, such as the ability to "scroll" a cursor forwards and backwards.
        SQLAlchemy does not include any explicit support for these behaviors; within
        SQLAlchemy itself, the general term "server side cursors" should be considered
        to mean "unbuffered results" and "client side cursors" means "result rows
        are buffered into memory before the first row is returned".   To work with
        a richer "server side cursor" featureset specific to a certain DBAPI driver,
        see the section :ref:`dbapi_connections_cursor`.

    From this basic architecture it follows that a "server side cursor" is more
    memory efficient when fetching very large result sets, while at the same time
    may introduce more complexity in the client/server communication process
    and be less efficient for small result sets (typically less than 10000 rows).

    For those dialects that have conditional support for buffered or unbuffered
    results, there are usually caveats to the use of the "unbuffered", or server
    side cursor mode.   When using the psycopg2 dialect for example, an error is
    raised if a server side cursor is used with any kind of DML or DDL statement.
    When using MySQL drivers with a server side cursor, the DBAPI connection is in
    a more fragile state and does not recover as gracefully from error conditions
    nor will it allow a rollback to proceed until the cursor is fully closed.

    For this reason, SQLAlchemy's dialects will always default to the less error
    prone version of a cursor, which means for PostgreSQL and MySQL dialects
    it defaults to a buffered, "client side" cursor where the full set of results
    is pulled into memory before any fetch methods are called from the cursor.
    This mode of operation is appropriate in the **vast majority** of cases;
    unbuffered cursors are not generally useful except in the uncommon case
    of an application fetching a very large number of rows in chunks, where
    the processing of these rows can be complete before more rows are fetched.

    For database drivers that provide client and server side cursor options,
    the :paramref:`_engine.Connection.execution_options.stream_results`
    and :paramref:`_engine.Connection.execution_options.yield_per` execution
    options provide access to "server side cursors" on a per-:class:`_engine.Connection`
    or per-statement basis.    Similar options exist when using an ORM
    :class:`_orm.Session` as well.


通过 Yield_per 使用固定缓冲区进行流式传输
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Streaming with a fixed buffer via yield_per

.. tab:: 中文
    
    由于完全非缓冲的服务器端游标每次获取单行操作的开销较大，
    因此 :paramref:`_engine.Connection.execution_options.yield_per` 执行选项
    会配置 :class:`_engine.Connection` 或语句使用可用的服务器端游标，
    同时配置一个固定大小的行缓冲区，从服务器按批提取数据。
    该参数可以设置为一个正整数，并通过
    :class:`_engine.Connection` 的 :meth:`_engine.Connection.execution_options` 方法，
    或通过语句的 :meth:`.Executable.execution_options` 方法来配置。
    
    .. versionadded:: 1.4.40
        :paramref:`_engine.Connection.execution_options.yield_per` 是 SQLAlchemy 1.4.40 中新增的 Core-only 选项；
        在 1.4 之前的版本中，可通过结合使用
        :paramref:`_engine.Connection.execution_options.stream_results` 与
        :meth:`_engine.Result.yield_per` 实现相同功能。
    
    使用该选项等价于手动设置
    :paramref:`_engine.Connection.execution_options.stream_results`（下节描述），
    然后在 :class:`_engine.Result` 对象上调用
    :meth:`_engine.Result.yield_per` 方法并传入整数值。
    这两种方式的组合具有如下效果：
    
    * 为指定的 backend 启用服务器端游标模式（若可用，且未为默认行为）；
    * 在提取结果行时，将按批缓冲结果行，每一批的大小等于
      :paramref:`_engine.Connection.execution_options.yield_per` 参数或
      :meth:`_engine.Result.yield_per` 方法提供的整数值，直到最后一批；
    * 若使用 :meth:`_engine.Result.partitions` 方法，其默认分区大小也等于此整数值。
    
    下方示例展示了这些行为的结合使用方式::
    
        with engine.connect() as conn:
            with conn.execution_options(yield_per=100).execute(
                text("select * from table")
            ) as result:
                for partition in result.partitions():
                    # partition 是一个最多包含 100 项的可迭代对象
                    for row in partition:
                        print(f"{row}")
    
    上述示例结合使用了 ``yield_per=100`` 与 :meth:`_engine.Result.partitions` 方法，
    以批处理方式处理与服务器匹配的行缓冲大小。
    :meth:`_engine.Result.partitions` 的使用是可选的；
    若直接对 :class:`_engine.Result` 进行迭代，每迭代 100 行将缓冲一次新的行批次。
    不应调用 :meth:`_engine.Result.all` 方法，
    因为这将一次性提取所有剩余行，从而失去了使用 ``yield_per`` 的意义。
    
    .. tip::
    
        如上所示，:class:`.Result` 对象可作为上下文管理器使用。
        在使用服务器端游标进行迭代时，这是确保在迭代过程中即使抛出异常也能正确关闭 :class:`.Result` 对象的最佳方式。
    
    :paramref:`_engine.Connection.execution_options.yield_per` 选项也可移植至 ORM，
    用于 :class:`_orm.Session` 提取 ORM 对象时限制每次生成的对象数量。
    请参阅 :ref:`queryguide_toplevel` 中的 :ref:`orm_queryguide_yield_per` 小节，
    了解在 ORM 中使用 :paramref:`_engine.Connection.execution_options.yield_per` 的更多背景。
    
    .. versionadded:: 1.4.40
       新增 :paramref:`_engine.Connection.execution_options.yield_per`，
       作为 Core 层级的执行选项，便于一次性设置流式结果、缓冲区大小与分区大小，
       同时兼容 ORM 中的类似用法。

.. tab:: 英文

    As individual row-fetch operations with fully unbuffered server side cursors
    are typically more expensive than fetching batches of rows at once, The
    :paramref:`_engine.Connection.execution_options.yield_per` execution option
    configures a :class:`_engine.Connection` or statement to make use of
    server-side cursors as are available, while at the same time configuring a
    fixed-size buffer of rows that will retrieve rows from the server in batches as
    they are consumed. This parameter may be to a positive integer value using the
    :meth:`_engine.Connection.execution_options` method on
    :class:`_engine.Connection` or on a statement using the
    :meth:`.Executable.execution_options` method.
    
    .. versionadded:: 1.4.40 :paramref:`_engine.Connection.execution_options.yield_per` as a
        Core-only option is new as of SQLAlchemy 1.4.40; for prior 1.4 versions,
        use :paramref:`_engine.Connection.execution_options.stream_results`
        directly in combination with :meth:`_engine.Result.yield_per`.
    
    Using this option is equivalent to manually setting the
    :paramref:`_engine.Connection.execution_options.stream_results` option,
    described in the next section, and then invoking the
    :meth:`_engine.Result.yield_per` method on the :class:`_engine.Result`
    object with the given integer value.   In both cases, the effect this
    combination has includes:
    
    * server side cursors mode is selected for the given backend, if available
      and not already the default behavior for that backend
    * as result rows are fetched, they will be buffered in batches, where the
      size of each batch up until the last batch will be equal to the integer
      argument passed to the
      :paramref:`_engine.Connection.execution_options.yield_per` option or the
      :meth:`_engine.Result.yield_per` method; the last batch is then sized against
      the remaining rows fewer than this size
    * The default partition size used by the :meth:`_engine.Result.partitions`
      method, if used, will be made equal to this integer size as well.
    
    These three behaviors are illustrated in the example below::
    
        with engine.connect() as conn:
            with conn.execution_options(yield_per=100).execute(
                text("select * from table")
            ) as result:
                for partition in result.partitions():
                    # partition is an iterable that will be at most 100 items
                    for row in partition:
                        print(f"{row}")
    
    The above example illustrates the combination of ``yield_per=100`` along
    with using the :meth:`_engine.Result.partitions` method to run processing
    on rows in batches that match the size fetched from the server.   The
    use of :meth:`_engine.Result.partitions` is optional, and if the
    :class:`_engine.Result` is iterated directly, a new batch of rows will be
    buffered for each 100 rows fetched.    Calling a method such as
    :meth:`_engine.Result.all` should **not** be used, as this will fully
    fetch all remaining rows at once and defeat the purpose of using ``yield_per``.
    
    .. tip::
    
        The :class:`.Result` object may be used as a context manager as illustrated
        above.  When iterating with a server-side cursor, this is the best way to
        ensure the :class:`.Result` object is closed, even if exceptions are
        raised within the iteration process.
    
    The :paramref:`_engine.Connection.execution_options.yield_per` option
    is portable to the ORM as well, used by a :class:`_orm.Session` to fetch
    ORM objects, where it also limits the amount of ORM objects generated at once.
    See the section :ref:`orm_queryguide_yield_per` - in the :ref:`queryguide_toplevel`
    for further background on using
    :paramref:`_engine.Connection.execution_options.yield_per` with the ORM.
    
    .. versionadded:: 1.4.40 Added
       :paramref:`_engine.Connection.execution_options.yield_per`
       as a Core level execution option to conveniently set streaming results,
       buffer size, and partition size all at once in a manner that is transferrable
       to that of the ORM's similar use case.

.. _engine_stream_results_sr:

使用 stream_results 使用动态增长缓冲区进行流式传输
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Streaming with a dynamically growing buffer using stream_results

.. tab:: 中文

    要启用服务端游标而不指定具体的分区大小，可以使用
    :paramref:`_engine.Connection.execution_options.stream_results` 选项。该选项与
    :paramref:`_engine.Connection.execution_options.yield_per` 类似，可以用于
    :class:`_engine.Connection` 对象或语句对象。
    
    当使用 :paramref:`_engine.Connection.execution_options.stream_results` 选项生成的
    :class:`_engine.Result` 对象被直接迭代时，内部将采用默认的缓冲策略：首先缓冲一小部分行，
    然后在每次获取时逐步扩大缓冲区，直到达到预设的 1000 行的限制。这个缓冲区的最大大小可以通过
    :paramref:`_engine.Connection.execution_options.max_row_buffer` 执行选项来控制：
    
    ::
    
        with engine.connect() as conn:
            with conn.execution_options(stream_results=True, max_row_buffer=100).execute(
                text("select * from table")
            ) as result:
                for row in result:
                    print(f"{row}")
    
    虽然 :paramref:`_engine.Connection.execution_options.stream_results` 选项可以与
    :meth:`_engine.Result.partitions` 方法结合使用，但建议为 :meth:`_engine.Result.partitions`
    提供一个具体的分区大小，以避免一次性获取整个结果集。通常在准备使用
    :meth:`_engine.Result.partitions` 方法时，使用
    :paramref:`_engine.Connection.execution_options.yield_per` 选项会更加直接明了。
    
    .. seealso::
    
        :ref:`orm_queryguide_yield_per` - 位于 :ref:`queryguide_toplevel`
    
        :meth:`_engine.Result.partitions`
    
        :meth:`_engine.Result.yield_per`

.. tab:: 英文

    To enable server side cursors without a specific partition size, the
    :paramref:`_engine.Connection.execution_options.stream_results` option may be
    used, which like :paramref:`_engine.Connection.execution_options.yield_per` may
    be called on the :class:`_engine.Connection` object or the statement object.

    When a :class:`_engine.Result` object delivered using the
    :paramref:`_engine.Connection.execution_options.stream_results` option
    is iterated directly, rows are fetched internally
    using a default buffering scheme that buffers first a small set of rows,
    then a larger and larger buffer on each fetch up to a pre-configured limit
    of 1000 rows.   The maximum size of this buffer can be affected using the
    :paramref:`_engine.Connection.execution_options.max_row_buffer` execution option::

        with engine.connect() as conn:
            with conn.execution_options(stream_results=True, max_row_buffer=100).execute(
                text("select * from table")
            ) as result:
                for row in result:
                    print(f"{row}")

    While the :paramref:`_engine.Connection.execution_options.stream_results`
    option may be combined with use of the :meth:`_engine.Result.partitions`
    method, a specific partition size should be passed to
    :meth:`_engine.Result.partitions` so that the entire result is not fetched.
    It is usually more straightforward to use the
    :paramref:`_engine.Connection.execution_options.yield_per` option when setting
    up to use the :meth:`_engine.Result.partitions` method.

    .. seealso::

        :ref:`orm_queryguide_yield_per` - in the :ref:`queryguide_toplevel`

        :meth:`_engine.Result.partitions`

        :meth:`_engine.Result.yield_per`


.. _schema_translating:

模式名称的转换
---------------------------

Translation of Schema Names

.. tab:: 中文
    
    为了支持将一组通用表分布到多个 schema 的多租户应用程序，
    可以使用 :paramref:`.Connection.execution_options.schema_translate_map`
    执行选项，在不修改表结构定义的前提下，将一组 :class:`_schema.Table` 对象重定向到不同的 schema 名称下。
    
    给定如下表结构：
    
    ::
    
        user_table = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
    
    此 :class:`_schema.Table` 的 "schema" 由 :paramref:`_schema.Table.schema` 属性定义，此处为 ``None``。
    可以通过 :paramref:`.Connection.execution_options.schema_translate_map` 指定所有 schema 为 ``None`` 的
    :class:`_schema.Table` 对象实际渲染为 ``user_schema_one``：
    
    ::
    
        connection = engine.connect().execution_options(
            schema_translate_map={None: "user_schema_one"}
        )
    
        result = connection.execute(user_table.select())
    
    上述代码将在数据库中生成如下 SQL：
    
    .. sourcecode:: sql
    
        SELECT user_schema_one.user.id, user_schema_one.user.name FROM
        user_schema_one.user
    
    也就是说，schema 名称被替换为我们设定的映射值。此映射可以指定任意数量的 schema 替换关系：
    
    ::
    
        connection = engine.connect().execution_options(
            schema_translate_map={
                None: "user_schema_one",  # 无 schema 名 -> "user_schema_one"
                "special": "special_schema",  # schema="special" 替换为 "special_schema"
                "public": None,  # schema="public" 的 Table 对象将渲染为无 schema
            }
        )
    
    :paramref:`.Connection.execution_options.schema_translate_map` 参数会影响所有由
    SQL 表达式语言生成的 DDL 和 SQL 构造，这些构造来源于 :class:`_schema.Table` 或 :class:`.Sequence` 对象。
    **不会**影响使用 :func:`_expression.text` 构造或通过 :meth:`_engine.Connection.execute` 直接传入的字面 SQL 字符串。
    
    该功能 **仅在** schema 名称直接来源于 :class:`_schema.Table` 或 :class:`.Sequence` 对象时生效；
    不影响那些显式传入 schema 字符串的 API。
    按此逻辑，它适用于例如 :meth:`_schema.MetaData.create_all` 或
    :meth:`_schema.MetaData.drop_all` 等方法中的 “可创建 / 可删除” 检查，
    也适用于基于 :class:`_schema.Table` 对象的表反射。但它 **不适用于**
    :class:`_reflection.Inspector` 对象中的操作，因为这些操作需要显式提供 schema 名称。
    
    .. tip::
    
      要在 ORM 的 :class:`_orm.Session` 中使用 schema 翻译功能，
      请在 :class:`_engine.Engine` 层设置该选项，然后将该 engine 传入 :class:`_orm.Session`。
      :class:`_orm.Session` 在每次事务中使用新的 :class:`_engine.Connection`：
    
      ::
    
          schema_engine = engine.execution_options(schema_translate_map={...})
    
          session = Session(schema_engine)
    
          ...
    
      .. warning::
    
        如果在没有扩展的情况下使用 ORM 的 :class:`_orm.Session`，
        schema 翻译功能仅支持 **每个 Session 使用一个 schema_translate_map**。
        如果尝试为每条语句指定不同的 schema_translate_map，则 **将无法生效**，
        因为 ORM 的 :class:`_orm.Session` 不会对单个对象考虑当前的 schema_translate 配置。
    
        若要使用单个 :class:`_orm.Session` 支持多个不同的 ``schema_translate_map`` 配置，
        可以使用 :ref:`horizontal_sharding_toplevel` 扩展。参见示例 :ref:`examples_sharding`。
    
.. tab:: 英文
    
    To support multi-tenancy applications that distribute common sets of tables
    into multiple schemas, the
    :paramref:`.Connection.execution_options.schema_translate_map`
    execution option may be used to repurpose a set of :class:`_schema.Table` objects
    to render under different schema names without any changes.
    
    Given a table::
    
        user_table = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )
    
    The "schema" of this :class:`_schema.Table` as defined by the
    :paramref:`_schema.Table.schema` attribute is ``None``.  The
    :paramref:`.Connection.execution_options.schema_translate_map` can specify
    that all :class:`_schema.Table` objects with a schema of ``None`` would instead
    render the schema as ``user_schema_one``::
    
        connection = engine.connect().execution_options(
            schema_translate_map={None: "user_schema_one"}
        )
    
        result = connection.execute(user_table.select())
    
    The above code will invoke SQL on the database of the form:
    
    .. sourcecode:: sql
    
        SELECT user_schema_one.user.id, user_schema_one.user.name FROM
        user_schema_one.user
    
    That is, the schema name is substituted with our translated name.  The
    map can specify any number of target->destination schemas::
    
        connection = engine.connect().execution_options(
            schema_translate_map={
                None: "user_schema_one",  # no schema name -> "user_schema_one"
                "special": "special_schema",  # schema="special" becomes "special_schema"
                "public": None,  # Table objects with schema="public" will render with no schema
            }
        )
    
    The :paramref:`.Connection.execution_options.schema_translate_map` parameter
    affects all DDL and SQL constructs generated from the SQL expression language,
    as derived from the :class:`_schema.Table` or :class:`.Sequence` objects.
    It does **not** impact literal string SQL used via the :func:`_expression.text`
    construct nor via plain strings passed to :meth:`_engine.Connection.execute`.
    
    The feature takes effect **only** in those cases where the name of the
    schema is derived directly from that of a :class:`_schema.Table` or :class:`.Sequence`;
    it does not impact methods where a string schema name is passed directly.
    By this pattern, it takes effect within the "can create" / "can drop" checks
    performed by methods such as :meth:`_schema.MetaData.create_all` or
    :meth:`_schema.MetaData.drop_all` are called, and it takes effect when
    using table reflection given a :class:`_schema.Table` object.  However it does
    **not** affect the operations present on the :class:`_reflection.Inspector` object,
    as the schema name is passed to these methods explicitly.
    
    .. tip::
    
      To use the schema translation feature with the ORM :class:`_orm.Session`,
      set this option at the level of the :class:`_engine.Engine`, then pass that engine
      to the :class:`_orm.Session`.  The :class:`_orm.Session` uses a new
      :class:`_engine.Connection` for each transaction::
    
          schema_engine = engine.execution_options(schema_translate_map={...})
    
          session = Session(schema_engine)
    
          ...
    
      .. warning::
    
        When using the ORM :class:`_orm.Session` without extensions, the schema
        translate feature is only supported as
        **a single schema translate map per Session**.   It will **not work** if
        different schema translate maps are given on a per-statement basis, as
        the ORM :class:`_orm.Session` does not take current schema translate
        values into account for individual objects.
    
        To use a single :class:`_orm.Session` with multiple ``schema_translate_map``
        configurations, the :ref:`horizontal_sharding_toplevel` extension may
        be used.  See the example at :ref:`examples_sharding`.

.. _sql_caching:


SQL 编译缓存
-----------------------

SQL Compilation Caching

.. tab:: 中文
    
    .. versionadded:: 1.4  
       SQLAlchemy 现在具备一个透明的查询缓存系统，大幅降低了在 Core 和 ORM 中
       将 SQL 语句结构转换为 SQL 字符串所需的 Python 计算开销。
       详见介绍 :ref:`change_4639`。
    
    SQLAlchemy 包含一个完整的 SQL 编译器缓存系统及其 ORM 变体。
    该缓存系统在 :class:`.Engine` 内部是透明的，保证给定的 Core 或 ORM SQL 语句在编译为 SQL 字符串、
    以及构建与该语句相关的结果提取机制时，只需执行一次编译，随后对所有结构相同的语句对象都复用缓存。
    这里的“结构相同”通常是指一个在函数中构建的 SQL 语句，每次调用函数时重新构建：
    
    ::
    
        def run_my_statement(connection, parameter):
            stmt = select(table)
            stmt = stmt.where(table.c.col == parameter)
            stmt = stmt.order_by(table.c.id)
            return connection.execute(stmt)
    
    上述语句将生成类似如下 SQL：
    
    ``SELECT id, col FROM table WHERE col = :col ORDER BY id``
    
    注意 ``parameter`` 的值是普通的 Python 对象，如字符串或整数，但语句的 SQL 字符串形式并不包含该值，
    因为使用了绑定参数。随后对 ``run_my_statement()`` 函数的调用将会在
    ``connection.execute()`` 的作用域中重用缓存编译结果，从而提升性能。
    
    .. note::
    
       请注意，SQL 编译缓存仅缓存 **传递给数据库的 SQL 字符串**，
       **不缓存查询返回的数据**。它完全不影响某个 SQL 语句的结果，
       也不涉及任何与结果行提取相关的内存使用。
    
    尽管 SQLAlchemy 从早期的 1.x 版本开始就已有简单的语句缓存机制，
    并且还为 ORM 提供了 “Baked Query” 扩展，但这些系统都要求较为特殊的 API 使用方式才能生效。
    而 1.4 起的新缓存机制则是完全自动化的，不需要改变任何编程风格即可使用。
    
    该缓存机制在默认配置下自动启用，无需特别设置。以下各节将详细介绍该缓存的配置与高级用法。

.. tab:: 英文

    .. versionadded:: 1.4  SQLAlchemy now has a transparent query caching system
       that substantially lowers the Python computational overhead involved in
       converting SQL statement constructs into SQL strings across both
       Core and ORM.   See the introduction at :ref:`change_4639`.
    
    SQLAlchemy includes a comprehensive caching system for the SQL compiler as well
    as its ORM variants.   This caching system is transparent within the
    :class:`.Engine` and provides that the SQL compilation process for a given Core
    or ORM SQL statement, as well as related computations which assemble
    result-fetching mechanics for that statement, will only occur once for that
    statement object and all others with the identical
    structure, for the duration that the particular structure remains within the
    engine's "compiled cache". By "statement objects that have the identical
    structure", this generally corresponds to a SQL statement that is
    constructed within a function and is built each time that function runs::
    
        def run_my_statement(connection, parameter):
            stmt = select(table)
            stmt = stmt.where(table.c.col == parameter)
            stmt = stmt.order_by(table.c.id)
            return connection.execute(stmt)
    
    The above statement will generate SQL resembling
    ``SELECT id, col FROM table WHERE col = :col ORDER BY id``, noting that
    while the value of ``parameter`` is a plain Python object such as a string
    or an integer, the string SQL form of the statement does not include this
    value as it uses bound parameters.  Subsequent invocations of the above
    ``run_my_statement()`` function will use a cached compilation construct
    within the scope of the ``connection.execute()`` call for enhanced performance.
    
    .. note:: it is important to note that the SQL compilation cache is caching
       the **SQL string that is passed to the database only**, and **not the data**
       returned by a query.   It is in no way a data cache and does not
       impact the results returned for a particular SQL statement nor does it
       imply any memory use linked to fetching of result rows.
    
    While SQLAlchemy has had a rudimentary statement cache since the early 1.x
    series, and additionally has featured the "Baked Query" extension for the ORM,
    both of these systems required a high degree of special API use in order for
    the cache to be effective.  The new cache as of 1.4 is instead completely
    automatic and requires no change in programming style to be effective.
    
    The cache is automatically used without any configurational changes and no
    special steps are needed in order to enable it. The following sections
    detail the configuration and advanced usage patterns for the cache.


配置
~~~~~~~~~~~~~

Configuration

.. tab:: 中文
    
    缓存本身是一个类字典对象，称为 ``LRUCache``，它是 SQLAlchemy 的内部字典子类，用于追踪特定键的使用情况，并具备定期“修剪”步骤：当缓存大小达到一定阈值时，会移除最少使用的项目。该缓存的默认大小为 500，可以使用 :paramref:`_sa.create_engine.query_cache_size` 参数进行配置::
    
        engine = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test", query_cache_size=1200
        )
    
    缓存大小最多可以增长到设定值的 150%，之后会被修剪回目标大小。上述大小为 1200 的缓存可以增长至 1800 个元素，然后再被修剪回 1200。
    
    缓存的大小是基于每个唯一的 SQL 语句在每个 engine 上的单个条目计算的。由 Core 和 ORM 生成的 SQL 语句一视同仁。DDL 语句通常不会被缓存。若想了解缓存的行为，可通过 engine 日志获取详情，下一节将进行介绍。

.. tab:: 英文

    The cache itself is a dictionary-like object called an ``LRUCache``, which is
    an internal SQLAlchemy dictionary subclass that tracks the usage of particular
    keys and features a periodic "pruning" step which removes the least recently
    used items when the size of the cache reaches a certain threshold.  The size
    of this cache defaults to 500 and may be configured using the
    :paramref:`_sa.create_engine.query_cache_size` parameter::

        engine = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test", query_cache_size=1200
        )

    The size of the cache can grow to be a factor of 150% of the size given, before
    it's pruned back down to the target size.  A cache of size 1200 above can therefore
    grow to be 1800 elements in size at which point it will be pruned to 1200.

    The sizing of the cache is based on a single entry per unique SQL statement rendered,
    per engine.   SQL statements generated from both the Core and the ORM are
    treated equally.  DDL statements will usually not be cached.  In order to determine
    what the cache is doing, engine logging will include details about the
    cache's behavior, described in the next section.


.. _sql_caching_logging:

使用日志记录估计缓存性能
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Estimating Cache Performance Using Logging

.. tab:: 中文
    
    上面配置的 1200 缓存大小实际上是相当大的。对于小型应用，100 的大小可能就足够了。若内存充足，可依据为目标 engine 渲染的唯一 SQL 字符串数量来估算最佳缓存大小。最直接的观察方法是启用 SQL 回显功能，可以通过 :paramref:`_sa.create_engine.echo` 参数，或通过 Python 的日志系统实现；关于日志配置的背景，请参见 :ref:`dbengine_logging` 一节。
    
    以下是一个示例程序，其日志将用于说明::
    
        from sqlalchemy import Column
        from sqlalchemy import create_engine
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import select
        from sqlalchemy import String
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm import Session
    
        Base = declarative_base()
    
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
            data = Column(String)
            bs = relationship("B")
    
    
        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))
            data = Column(String)
    
    
        e = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(e)
    
        s = Session(e)
    
        s.add_all([A(bs=[B(), B(), B()]), A(bs=[B(), B(), B()]), A(bs=[B(), B(), B()])])
        s.commit()
    
        for a_rec in s.scalars(select(A)):
            print(a_rec.bs)
    
    运行时，每条 SQL 日志语句会在参数之前显示一个方括号包围的缓存状态标记。我们可能看到以下四种消息类型：
    
    * ``[raw sql]`` - 驱动或最终用户使用 :meth:`.Connection.exec_driver_sql` 执行原始 SQL —— 不适用于缓存
    
    * ``[no key]`` - 语句对象是未被缓存的 DDL 语句，或包含无法缓存的元素，例如用户自定义构造或非常大的 VALUES 子句。
    
    * ``[generated in Xs]`` - 该语句是一次 **缓存未命中**，需要编译并存入缓存，耗时 X 秒。X 通常为很小的秒数。
    
    * ``[cached since Xs ago]`` - 该语句是一次 **缓存命中**，无需重新编译。该语句自 X 秒前起就已存入缓存。
    
    每种标记将在下文中进一步说明。
    
    上述程序最先产生的语句是 SQLite 方言检查 "a" 和 "b" 表是否存在：
    
    .. sourcecode:: text
    
      INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("a")
      INFO sqlalchemy.engine.Engine [raw sql] ()
      INFO sqlalchemy.engine.Engine PRAGMA main.table_info("b")
      INFO sqlalchemy.engine.Engine [raw sql] ()
    
    这两条 SQLite PRAGMA 语句对应的标记是 ``[raw sql]``，表示驱动将 Python 字符串直接发送至数据库，使用的是 :meth:`.Connection.exec_driver_sql`。这种语句不适用缓存，因为它们本身已是字符串形式，SQLAlchemy 无法预解析其可能返回的结果。
    
    接下来是 CREATE TABLE 语句：
    
    .. sourcecode:: sql
    
      INFO sqlalchemy.engine.Engine
      CREATE TABLE a (
        id INTEGER NOT NULL,
        data VARCHAR,
        PRIMARY KEY (id)
      )
    
      INFO sqlalchemy.engine.Engine [no key 0.00007s] ()
      INFO sqlalchemy.engine.Engine
      CREATE TABLE b (
        id INTEGER NOT NULL,
        a_id INTEGER,
        data VARCHAR,
        PRIMARY KEY (id),
        FOREIGN KEY(a_id) REFERENCES a (id)
      )
    
      INFO sqlalchemy.engine.Engine [no key 0.00006s] ()
    
    这些语句的标记为 ``[no key 0.00006s]``，表示这些 DDL 类型的 :class:`_schema.CreateTable` 构造未生成缓存键，因此未缓存。DDL 构造通常不参与缓存，因为它们不太可能被重复执行，同时 DDL 更侧重数据库配置，性能并非关键因素。
    
    ``[no key]`` 标记还有另一种用途：当 SQL 语句本可以缓存，但因包含某些目前无法缓存的子构造时也会显示。常见示例包括未定义缓存参数的自定义 SQL 元素，以及会生成不可预测的长 SQL 字符串的构造，如 :class:`.Values` 和通过 :meth:`.Insert.values` 使用的“多值插入”。
    
    至此缓存仍为空。但接下来的语句将会被缓存，其片段如下：
    
    .. sourcecode:: sql
    
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [generated in 0.00011s] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [cached since 0.0003533s ago] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [cached since 0.0005326s ago] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [generated in 0.00010s] (1, None)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [cached since 0.0003232s ago] (1, None)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [cached since 0.0004887s ago] (1, None)
    
    在这里，我们实际上看到两个唯一 SQL 字符串：``"INSERT INTO a (data) VALUES (?)"`` 和 ``"INSERT INTO b (a_id, data) VALUES (?, ?)"``。由于 SQLAlchemy 对所有字面值都使用绑定参数，即使为不同对象重复执行，实际的 SQL 字符串也保持不变。
    
    .. note:: 上述两个语句由 ORM 的 unit of work 机制生成，并实际缓存于每个 mapper 的独立缓存中。但其机制和术语相同。下面的 :ref:`engine_compiled_cache` 一节将介绍如何在用户代码中按语句使用备用缓存容器。
    
    每条语句第一次出现时的标记为 ``[generated in 0.00011s]``，表示该语句 **不在缓存中，编译耗时 0.00011s，并已缓存**。看到 ``[generated]`` 标记就表示发生了 **缓存未命中**。对于首次出现的语句，这很正常。但如果一个长期运行的应用中频繁出现 ``[generated]``，可能说明 :paramref:`_sa.create_engine.query_cache_size` 设置得太小。当原已缓存的语句被 LRU 策略移出缓存，下次再使用时就会显示为 ``[generated]``。
    
    而后续出现的相同语句的标记如 ``[cached since 0.0003533s ago]``，表示该语句 **已从缓存中命中，最初缓存时间为 0.0003533 秒前**。值得注意的是，尽管 ``[generated]`` 和 ``[cached since]`` 都涉及秒数，但含义不同：``[generated]`` 表示语句编译耗时，时间非常短；而 ``[cached since]`` 表示语句在缓存中已存在的时间，对于运行 6 小时的应用，可能显示为 ``[cached since 21600 seconds ago]``，这是件好事。这个值越大，说明该语句长期未被驱逐。反之，如果该数值频繁很小，可能说明语句频繁未命中，需考虑增加 :paramref:`_sa.create_engine.query_cache_size`。
    
    我们的示例程序接着执行了一些 SELECT 操作，可以看到类似的“generated”与“cached”模式，分别针对 "a" 表的 SELECT 以及后续 "b" 表的延迟加载：
    
    .. sourcecode:: text
    
      INFO sqlalchemy.engine.Engine SELECT a.id AS a_id, a.data AS a_data
      FROM a
      INFO sqlalchemy.engine.Engine [generated in 0.00009s] ()
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
      INFO sqlalchemy.engine.Engine [generated in 0.00010s] (1,)
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
      INFO sqlalchemy.engine.Engine [cached since 0.0005922s ago] (2,)
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
    
    在该程序的完整运行过程中，总共缓存了四条不同的 SQL 字符串，说明 **缓存大小为四** 就足够了。显然这是一个非常小的数值，因此默认大小 500 一般无需修改。

.. tab:: 英文

    The above cache size of 1200 is actually fairly large.   For small applications,
    a size of 100 is likely sufficient.  To estimate the optimal size of the cache,
    assuming enough memory is present on the target host, the size of the cache
    should be based on the number of unique SQL strings that may be rendered for the
    target engine in use.    The most expedient way to see this is to use
    SQL echoing, which is most directly enabled by using the
    :paramref:`_sa.create_engine.echo` flag, or by using Python logging; see the
    section :ref:`dbengine_logging` for background on logging configuration.
    
    As an example, we will examine the logging produced by the following program::
    
        from sqlalchemy import Column
        from sqlalchemy import create_engine
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import select
        from sqlalchemy import String
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm import Session
    
        Base = declarative_base()
    
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
            data = Column(String)
            bs = relationship("B")
    
    
        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))
            data = Column(String)
    
    
        e = create_engine("sqlite://", echo=True)
        Base.metadata.create_all(e)
    
        s = Session(e)
    
        s.add_all([A(bs=[B(), B(), B()]), A(bs=[B(), B(), B()]), A(bs=[B(), B(), B()])])
        s.commit()
    
        for a_rec in s.scalars(select(A)):
            print(a_rec.bs)
    
    When run, each SQL statement that's logged will include a bracketed
    cache statistics badge to the left of the parameters passed.   The four
    types of message we may see are summarized as follows:
    
    * ``[raw sql]`` - the driver or the end-user emitted raw SQL using
      :meth:`.Connection.exec_driver_sql` - caching does not apply
    
    * ``[no key]`` - the statement object is a DDL statement that is not cached, or
      the statement object contains uncacheable elements such as user-defined
      constructs or arbitrarily large VALUES clauses.
    
    * ``[generated in Xs]`` - the statement was a **cache miss** and had to be
      compiled, then stored in the cache.  it took X seconds to produce the
      compiled construct.  The number X will be in the small fractional seconds.
    
    * ``[cached since Xs ago]`` - the statement was a **cache hit** and did not
      have to be recompiled.  The statement has been stored in the cache since
      X seconds ago.  The number X will be proportional to how long the application
      has been running and how long the statement has been cached, so for example
      would be 86400 for a 24 hour period.
    
    Each badge is described in more detail below.
    
    The first statements we see for the above program will be the SQLite dialect
    checking for the existence of the "a" and "b" tables:
    
    .. sourcecode:: text
    
      INFO sqlalchemy.engine.Engine PRAGMA temp.table_info("a")
      INFO sqlalchemy.engine.Engine [raw sql] ()
      INFO sqlalchemy.engine.Engine PRAGMA main.table_info("b")
      INFO sqlalchemy.engine.Engine [raw sql] ()
    
    For the above two SQLite PRAGMA statements, the badge reads ``[raw sql]``,
    which indicates the driver is sending a Python string directly to the
    database using :meth:`.Connection.exec_driver_sql`.  Caching does not apply
    to such statements because they already exist in string form, and there
    is nothing known about what kinds of result rows will be returned since
    SQLAlchemy does not parse SQL strings ahead of time.
    
    The next statements we see are the CREATE TABLE statements:
    
    .. sourcecode:: sql
    
      INFO sqlalchemy.engine.Engine
      CREATE TABLE a (
        id INTEGER NOT NULL,
        data VARCHAR,
        PRIMARY KEY (id)
      )
    
      INFO sqlalchemy.engine.Engine [no key 0.00007s] ()
      INFO sqlalchemy.engine.Engine
      CREATE TABLE b (
        id INTEGER NOT NULL,
        a_id INTEGER,
        data VARCHAR,
        PRIMARY KEY (id),
        FOREIGN KEY(a_id) REFERENCES a (id)
      )
    
      INFO sqlalchemy.engine.Engine [no key 0.00006s] ()
    
    For each of these statements, the badge reads ``[no key 0.00006s]``.  This
    indicates that these two particular statements, caching did not occur because
    the DDL-oriented :class:`_schema.CreateTable` construct did not produce a
    cache key.  DDL constructs generally do not participate in caching because
    they are not typically subject to being repeated a second time and DDL
    is also a database configurational step where performance is not as critical.
    
    The ``[no key]`` badge is important for one other reason, as it can be produced
    for SQL statements that are cacheable except for some particular sub-construct
    that is not currently cacheable.   Examples of this include custom user-defined
    SQL elements that don't define caching parameters, as well as some constructs
    that generate arbitrarily long and non-reproducible SQL strings, the main
    examples being the :class:`.Values` construct as well as when using "multivalued
    inserts" with the :meth:`.Insert.values` method.
    
    So far our cache is still empty.  The next statements will be cached however,
    a segment looks like:
    
    .. sourcecode:: sql
    
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [generated in 0.00011s] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [cached since 0.0003533s ago] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO a (data) VALUES (?)
      INFO sqlalchemy.engine.Engine [cached since 0.0005326s ago] (None,)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [generated in 0.00010s] (1, None)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [cached since 0.0003232s ago] (1, None)
      INFO sqlalchemy.engine.Engine INSERT INTO b (a_id, data) VALUES (?, ?)
      INFO sqlalchemy.engine.Engine [cached since 0.0004887s ago] (1, None)
    
    Above, we see essentially two unique SQL strings; ``"INSERT INTO a (data) VALUES (?)"``
    and ``"INSERT INTO b (a_id, data) VALUES (?, ?)"``.  Since SQLAlchemy uses
    bound parameters for all literal values, even though these statements are
    repeated many times for different objects, because the parameters are separate,
    the actual SQL string stays the same.
    
    .. note:: the above two statements are generated by the ORM unit of work
       process, and in fact will be caching these in a separate cache that is
       local to each mapper.  However the mechanics and terminology are the same.
       The section :ref:`engine_compiled_cache` below will describe how user-facing
       code can also use an alternate caching container on a per-statement basis.
    
    The caching badge we see for the first occurrence of each of these two
    statements is ``[generated in 0.00011s]``. This indicates that the statement
    was **not in the cache, was compiled into a String in .00011s and was then
    cached**.   When we see the ``[generated]`` badge, we know that this means
    there was a **cache miss**.  This is to be expected for the first occurrence of
    a particular statement.  However, if lots of new ``[generated]`` badges are
    observed for a long-running application that is generally using the same series
    of SQL statements over and over, this may be a sign that the
    :paramref:`_sa.create_engine.query_cache_size` parameter is too small.  When a
    statement that was cached is then evicted from the cache due to the LRU
    cache pruning lesser used items, it will display the ``[generated]`` badge
    when it is next used.
    
    The caching badge that we then see for the subsequent occurrences of each of
    these two statements looks like ``[cached since 0.0003533s ago]``.  This
    indicates that the statement **was found in the cache, and was originally
    placed into the cache .0003533 seconds ago**.   It is important to note that
    while the ``[generated]`` and ``[cached since]`` badges refer to a number of
    seconds, they mean different things; in the case of ``[generated]``, the number
    is a rough timing of how long it took to compile the statement, and will be an
    extremely small amount of time.   In the case of ``[cached since]``, this is
    the total time that a statement has been present in the cache.  For an
    application that's been running for six hours, this number may read ``[cached
    since 21600 seconds ago]``, and that's a good thing.    Seeing high numbers for
    "cached since" is an indication that these statements have not been subject to
    cache misses for a long time.  Statements that frequently have a low number of
    "cached since" even if the application has been running a long time may
    indicate these statements are too frequently subject to cache misses, and that
    the
    :paramref:`_sa.create_engine.query_cache_size` may need to be increased.
    
    Our example program then performs some SELECTs where we can see the same
    pattern of "generated" then "cached", for the SELECT of the "a" table as well
    as for subsequent lazy loads of the "b" table:
    
    .. sourcecode:: text
    
      INFO sqlalchemy.engine.Engine SELECT a.id AS a_id, a.data AS a_data
      FROM a
      INFO sqlalchemy.engine.Engine [generated in 0.00009s] ()
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
      INFO sqlalchemy.engine.Engine [generated in 0.00010s] (1,)
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
      INFO sqlalchemy.engine.Engine [cached since 0.0005922s ago] (2,)
      INFO sqlalchemy.engine.Engine SELECT b.id AS b_id, b.a_id AS b_a_id, b.data AS b_data
      FROM b
      WHERE ? = b.a_id
    
    From our above program, a full run shows a total of four distinct SQL strings
    being cached.   Which indicates a cache size of **four** would be sufficient.   This is
    obviously an extremely small size, and the default size of 500 is fine to be left
    at its default.

缓存使用多少内存？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How much memory does the cache use?

.. tab:: 中文

    上一节详细介绍了一些技术手段，用于检查 :paramref:`_sa.create_engine.query_cache_size` 是否需要更大。那么我们如何判断缓存是否过大呢？我们之所以可能希望将 :paramref:`_sa.create_engine.query_cache_size` 设置为不超过某个特定数值，是因为某些应用程序可能会使用大量不同的语句，例如一个根据搜索界面动态构建查询的应用程序。如果在过去的 24 小时内运行了十万条不同的查询，并且全部被缓存，那么我们可能不希望主机因此耗尽内存。

    衡量 Python 数据结构占用多少内存是非常困难的，不过我们可以通过监视进程在执行 ``top`` 命令时内存的增长情况，并逐步将 250 条新语句加入缓存，从而估算其内存使用。结果显示，一个中等大小的 Core 语句大约占用 12K，而一个较小的 ORM 语句大约占用 20K，其中还包括了结果提取结构，这在 ORM 中会显著增大。

.. tab:: 英文

    The previous section detailed some techniques to check if the
    :paramref:`_sa.create_engine.query_cache_size` needs to be bigger.   How do we know
    if the cache is not too large?   The reason we may want to set
    :paramref:`_sa.create_engine.query_cache_size` to not be higher than a certain
    number would be because we have an application that may make use of a very large
    number of different statements, such as an application that is building queries
    on the fly from a search UX, and we don't want our host to run out of memory
    if for example, a hundred thousand different queries were run in the past 24 hours
    and they were all cached.

    It is extremely difficult to measure how much memory is occupied by Python
    data structures, however using a process to measure growth in memory via ``top`` as a
    successive series of 250 new statements are added to the cache suggest a
    moderate Core statement takes up about 12K while a small ORM statement takes about
    20K, including result-fetching structures which for the ORM will be much greater.


.. _engine_compiled_cache:

禁用或使用备用字典来缓存部分（或全部）语句
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Disabling or using an alternate dictionary to cache some (or all) statements

.. tab:: 中文

    内部使用的缓存类型为 ``LRUCache``，但其本质上只是一个字典。任何字典都可以被用作缓存语句的容器，通过将 :paramref:`.Connection.execution_options.compiled_cache` 作为执行选项传入。执行选项可以设置在语句本身、:class:`_engine.Engine` 或 :class:`_engine.Connection` 上，也可以在使用 ORM 的 :meth:`_orm.Session.execute` 方法时传入，以符合 SQLAlchemy 2.0 的调用方式。例如，要将一系列 SQL 语句缓存到特定字典中，可以这样做::

        my_cache = {}
        with engine.connect().execution_options(compiled_cache=my_cache) as conn:
            conn.execute(table.select())

    SQLAlchemy ORM 使用上述技术在工作单元（unit of work）“flush”过程中维持每个 mapper 的缓存，这些缓存是独立于 :class:`_engine.Engine` 上配置的默认缓存的，同时也用于某些关系加载器查询。

    也可以通过传入 ``None`` 来禁用缓存::

        # 禁用该连接的缓存
        with engine.connect().execution_options(compiled_cache=None) as conn:
            conn.execute(table.select())

.. tab:: 英文

    The internal cache used is known as ``LRUCache``, but this is mostly just
    a dictionary.  Any dictionary may be used as a cache for any series of
    statements by using the :paramref:`.Connection.execution_options.compiled_cache`
    option as an execution option.  Execution options may be set on a statement,
    on an :class:`_engine.Engine` or :class:`_engine.Connection`, as well as
    when using the ORM :meth:`_orm.Session.execute` method for SQLAlchemy-2.0
    style invocations.   For example, to run a series of SQL statements and have
    them cached in a particular dictionary::

        my_cache = {}
        with engine.connect().execution_options(compiled_cache=my_cache) as conn:
            conn.execute(table.select())

    The SQLAlchemy ORM uses the above technique to hold onto per-mapper caches
    within the unit of work "flush" process that are separate from the default
    cache configured on the :class:`_engine.Engine`, as well as for some
    relationship loader queries.

    The cache can also be disabled with this argument by sending a value of
    ``None``::

        # disable caching for this connection
        with engine.connect().execution_options(compiled_cache=None) as conn:
            conn.execute(table.select())

.. _engine_thirdparty_caching:

第三方方言缓存
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Caching for Third Party Dialects

.. tab:: 中文

    启用缓存功能要求方言（dialect）的编译器生成的 SQL 字符串在给定的缓存键下是可以安全复用的。这意味着语句中的任何字面值（例如 SELECT 的 LIMIT/OFFSET 值）不能被硬编码进方言的编译逻辑中，否则编译后的字符串将不可复用。SQLAlchemy 提供了 :meth:`_sql.BindParameter.render_literal_execute` 方法来支持渲染绑定参数的功能，可以通过自定义编译器应用到现有的 ``Select._limit_clause`` 和 ``Select._offset_clause`` 属性中，后文会有示例说明。

    由于存在大量第三方方言，其中许多可能仍在生成包含字面值的 SQL 语句，而未使用新的“literal execute”特性，从 SQLAlchemy 1.4.5 版本开始，添加了一个方言属性 :attr:`_engine.Dialect.supports_statement_cache`。该属性在运行时会直接在方言类上检查，即使该属性在父类中已经定义，子类中也必须显式声明，才能启用缓存。因此，即使是继承自支持缓存的 SQLAlchemy 方言（如 ``sqlalchemy.dialects.postgresql.PGDialect``）的第三方方言，也必须显式声明此属性。只有当方言已经完成必要的修改，并验证编译后的 SQL 语句在参数变化下可安全复用，才应启用该属性。

    对于不支持该属性的所有第三方方言，其日志中会显示 ``dialect does not support caching``。

    当一个方言已经完成缓存功能的测试，尤其是其 SQL 编译器已确保不会将字面 LIMIT / OFFSET 值直接渲染到 SQL 字符串中时，方言作者可以如下添加该属性::

        from sqlalchemy.engine.default import DefaultDialect


        class MyDialect(DefaultDialect):
            supports_statement_cache = True

    该属性也需要添加到所有的方言子类中::

        class MyDBAPIForMyDialect(MyDialect):
            supports_statement_cache = True

    .. versionadded:: 1.4.5

        新增 :attr:`.Dialect.supports_statement_cache` 属性。

    方言修改的典型场景如下。

.. tab:: 英文

    The caching feature requires that the dialect's compiler produces SQL
    strings that are safe to reuse for many statement invocations, given
    a particular cache key that is keyed to that SQL string.  This means
    that any literal values in a statement, such as the LIMIT/OFFSET values for
    a SELECT, can not be hardcoded in the dialect's compilation scheme, as
    the compiled string will not be re-usable.   SQLAlchemy supports rendered
    bound parameters using the :meth:`_sql.BindParameter.render_literal_execute`
    method which can be applied to the existing ``Select._limit_clause`` and
    ``Select._offset_clause`` attributes by a custom compiler, which
    are illustrated later in this section.

    As there are many third party dialects, many of which may be generating literal
    values from SQL statements without the benefit of the newer "literal execute"
    feature, SQLAlchemy as of version 1.4.5 has added an attribute to dialects
    known as :attr:`_engine.Dialect.supports_statement_cache`. This attribute is
    checked at runtime for its presence directly on a particular dialect's class,
    even if it's already present on a superclass, so that even a third party
    dialect that subclasses an existing cacheable SQLAlchemy dialect such as
    ``sqlalchemy.dialects.postgresql.PGDialect`` must still explicitly include this
    attribute for caching to be enabled. The attribute should **only** be enabled
    once the dialect has been altered as needed and tested for reusability of
    compiled SQL statements with differing parameters.

    For all third party dialects that don't support this attribute, the logging for
    such a dialect will indicate ``dialect does not support caching``.

    When a dialect has been tested against caching, and in particular the SQL
    compiler has been updated to not render any literal LIMIT / OFFSET within
    a SQL string directly, dialect authors can apply the attribute as follows::

        from sqlalchemy.engine.default import DefaultDialect


        class MyDialect(DefaultDialect):
            supports_statement_cache = True

    The flag needs to be applied to all subclasses of the dialect as well::

        class MyDBAPIForMyDialect(MyDialect):
            supports_statement_cache = True

    .. versionadded:: 1.4.5

        Added the :attr:`.Dialect.supports_statement_cache` attribute.

    The typical case for dialect modification follows.

示例：使用后编译参数呈现 LIMIT / OFFSET
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Example: Rendering LIMIT / OFFSET with post compile parameters

.. tab:: 中文
    
    假设一个方言重写了 :meth:`.SQLCompiler.limit_clause` 方法，用于生成 SQL 语句的 "LIMIT / OFFSET" 子句，如下所示::
    
        # pre 1.4 风格的代码
        def limit_clause(self, select, **kw):
            text = ""
            if select._limit is not None:
                text += " \n LIMIT %d" % (select._limit,)
            if select._offset is not None:
                text += " \n OFFSET %d" % (select._offset,)
            return text
    
    上述代码会将 :attr:`.Select._limit` 和 :attr:`.Select._offset` 的整数值直接嵌入 SQL 语句中。这在不支持在 SELECT 语句的 LIMIT/OFFSET 子句中使用绑定参数的数据库中是常见的需求。然而，在初始编译阶段渲染字面整数的方式与缓存机制是 **不兼容** 的，因为 :class:`.Select` 对象的 limit 和 offset 值并不是缓存键的一部分，这意味着多个带有不同 limit/offset 的 :class:`.Select` 语句将无法正确复用缓存。
    
    正确做法是将字面整数移动到 SQLAlchemy 的 :ref:`post-compile <change_4808>` 机制中，在语句执行阶段而非编译阶段进行渲染。这可以通过在编译阶段使用 :meth:`_sql.BindParameter.render_literal_execute` 方法，并结合使用 :attr:`.Select._limit_clause` 和 :attr:`.Select._offset_clause` 属性实现，如下::
    
        # 1.4 兼容缓存的代码
        def limit_clause(self, select, **kw):
            text = ""
    
            limit_clause = select._limit_clause
            offset_clause = select._offset_clause
    
            if select._simple_int_clause(limit_clause):
                text += " \n LIMIT %s" % (
                    self.process(limit_clause.render_literal_execute(), **kw)
                )
            elif limit_clause is not None:
                # 假设数据库不支持 LIMIT 使用 SQL 表达式，否则可正常渲染
                raise exc.CompileError(
                    "dialect 'mydialect' can only render simple integers for LIMIT"
                )
            if select._simple_int_clause(offset_clause):
                text += " \n OFFSET %s" % (
                    self.process(offset_clause.render_literal_execute(), **kw)
                )
            elif offset_clause is not None:
                # 假设数据库不支持 OFFSET 使用 SQL 表达式，否则可正常渲染
                raise exc.CompileError(
                    "dialect 'mydialect' can only render simple integers for OFFSET"
                )
    
            return text
    
    上述方法会生成如下形式的编译 SELECT 语句：
    
    .. sourcecode:: sql
    
        SELECT x FROM y
        LIMIT __[POSTCOMPILE_param_1]
        OFFSET __[POSTCOMPILE_param_2]
    
    其中 ``__[POSTCOMPILE_param_1]`` 与 ``__[POSTCOMPILE_param_2]`` 会在语句执行阶段被替换为对应的整数值，此时 SQL 字符串已从缓存中获取。
    
    在完成类似上述修改后，应将 :attr:`.Dialect.supports_statement_cache` 标志设置为 ``True``。强烈建议第三方方言使用
    `第三方方言测试套件 <https://github.com/sqlalchemy/sqlalchemy/blob/main/README.dialects.rst>`_
    来确保诸如带 LIMIT/OFFSET 的 SELECT 语句能被正确渲染并缓存。
    
    .. seealso::
    
        :ref:`faq_new_caching` - 位于 :ref:`faq_toplevel` 部分

.. tab:: 英文
    
    As an example, suppose a dialect overrides the :meth:`.SQLCompiler.limit_clause`
    method, which produces the "LIMIT / OFFSET" clause for a SQL statement,
    like this::
    
        # pre 1.4 style code
        def limit_clause(self, select, **kw):
            text = ""
            if select._limit is not None:
                text += " \n LIMIT %d" % (select._limit,)
            if select._offset is not None:
                text += " \n OFFSET %d" % (select._offset,)
            return text
    
    The above routine renders the :attr:`.Select._limit` and
    :attr:`.Select._offset` integer values as literal integers embedded in the SQL
    statement. This is a common requirement for databases that do not support using
    a bound parameter within the LIMIT/OFFSET clauses of a SELECT statement.
    However, rendering the integer value within the initial compilation stage is
    directly **incompatible** with caching as the limit and offset integer values
    of a :class:`.Select` object are not part of the cache key, so that many
    :class:`.Select` statements with different limit/offset values would not render
    with the correct value.
    
    The correction for the above code is to move the literal integer into
    SQLAlchemy's :ref:`post-compile <change_4808>` facility, which will render the
    literal integer outside of the initial compilation stage, but instead at
    execution time before the statement is sent to the DBAPI.  This is accessed
    within the compilation stage using the :meth:`_sql.BindParameter.render_literal_execute`
    method, in conjunction with using the :attr:`.Select._limit_clause` and
    :attr:`.Select._offset_clause` attributes, which represent the LIMIT/OFFSET
    as a complete SQL expression, as follows::
    
        # 1.4 cache-compatible code
        def limit_clause(self, select, **kw):
            text = ""
    
            limit_clause = select._limit_clause
            offset_clause = select._offset_clause
    
            if select._simple_int_clause(limit_clause):
                text += " \n LIMIT %s" % (
                    self.process(limit_clause.render_literal_execute(), **kw)
                )
            elif limit_clause is not None:
                # assuming the DB doesn't support SQL expressions for LIMIT.
                # Otherwise render here normally
                raise exc.CompileError(
                    "dialect 'mydialect' can only render simple integers for LIMIT"
                )
            if select._simple_int_clause(offset_clause):
                text += " \n OFFSET %s" % (
                    self.process(offset_clause.render_literal_execute(), **kw)
                )
            elif offset_clause is not None:
                # assuming the DB doesn't support SQL expressions for OFFSET.
                # Otherwise render here normally
                raise exc.CompileError(
                    "dialect 'mydialect' can only render simple integers for OFFSET"
                )
    
            return text
    
    The approach above will generate a compiled SELECT statement that looks like:
    
    .. sourcecode:: sql
    
        SELECT x FROM y
        LIMIT __[POSTCOMPILE_param_1]
        OFFSET __[POSTCOMPILE_param_2]
    
    Where above, the ``__[POSTCOMPILE_param_1]`` and ``__[POSTCOMPILE_param_2]``
    indicators will be populated with their corresponding integer values at
    statement execution time, after the SQL string has been retrieved from the
    cache.
    
    After changes like the above have been made as appropriate, the
    :attr:`.Dialect.supports_statement_cache` flag should be set to ``True``.
    It is strongly recommended that third party dialects make use of the
    `dialect third party test suite <https://github.com/sqlalchemy/sqlalchemy/blob/main/README.dialects.rst>`_
    which will assert that operations like
    SELECTs with LIMIT/OFFSET are correctly rendered and cached.
    
    .. seealso::
    
        :ref:`faq_new_caching` - in the :ref:`faq_toplevel` section


.. _engine_lambda_caching:

使用 Lambda 显著提高语句生成速度
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Lambdas to add significant speed gains to statement production

.. tab:: 中文

    .. deepalchemy:: 除非在性能要求极高的场景中，一般无需使用此技术，它更适用于有经验的 Python 程序员。
        尽管该技术相对简单，但涉及的元编程概念并不适合 Python 初学者。
        使用 lambda 的方式也可以在后续对已有代码中轻松应用，几乎不需要改动。

    Python 函数，通常以 lambda 表达式的形式出现，可以用于生成 SQL 表达式；
    这些表达式可根据 lambda 函数本身在 Python 代码中的位置以及其闭包变量进行缓存。
    其核心目的是在 SQLAlchemy 原本只缓存字符串化 SQL 表达式的基础上，
    进一步缓存 Python 层面上 SQL 表达式结构的组合逻辑，从而减少一部分 Python 层的开销。

    lambda SQL 表达式功能是一项用于提升性能的可选功能，
    并可被用于 :func:`_orm.with_loader_criteria` 这个 ORM 选项中，以提供通用的 SQL 片段。

.. tab:: 英文

    .. deepalchemy:: This technique is generally non-essential except in very performance
        intensive scenarios, and intended for experienced Python programmers.
        While fairly straightforward, it involves metaprogramming concepts that are
        not appropriate for novice Python developers.  The lambda approach can be
        applied to at a later time to existing code with a minimal amount of effort.

    Python functions, typically expressed as lambdas, may be used to generate
    SQL expressions which are cacheable based on the Python code location of
    the lambda function itself as well as the closure variables within the
    lambda.   The rationale is to allow caching of not only the SQL string-compiled
    form of a SQL expression construct as is SQLAlchemy's normal behavior when
    the lambda system isn't used, but also the in-Python composition
    of the SQL expression construct itself, which also has some degree of
    Python overhead.

    The lambda SQL expression feature is available as a performance enhancing
    feature, and is also optionally used in the :func:`_orm.with_loader_criteria`
    ORM option in order to provide a generic SQL fragment.

概要
^^^^^^^^

Synopsis

.. tab:: 中文

    lambda 语句通过调用 :func:`_sql.lambda_stmt` 函数构造，
    该函数返回一个 :class:`_sql.StatementLambdaElement` 实例，
    它本身是一个可执行的语句结构。可以使用 Python 的加法操作符 ``+`` 添加附加的修饰或条件，
    或者使用 :meth:`_sql.StatementLambdaElement.add_criteria` 方法来提供更多选项。

    通常假设 :func:`_sql.lambda_stmt` 构造位于某个外层函数或方法中，
    该函数或方法会在应用中被多次调用，从而在第一次执行之后，
    可以利用已编译好的 SQL 缓存。在 lambda 被定义于函数体内时，
    该 lambda 也可能包含闭包变量，这对于整个机制是关键的一部分::

        from sqlalchemy import lambda_stmt

        def run_my_statement(connection, parameter):
            stmt = lambda_stmt(lambda: select(table))
            stmt += lambda s: s.where(table.c.col == parameter)
            stmt += lambda s: s.order_by(table.c.id)

            return connection.execute(stmt)

        with engine.connect() as conn:
            result = run_my_statement(some_connection, "some parameter")

    如上所示，三次 ``lambda`` 调用定义了 SELECT 语句的结构，它们仅会被调用一次，
    生成的 SQL 字符串随后被缓存在 engine 的编译缓存中。
    之后每次调用 ``run_my_statement()`` 函数时，内部的 ``lambda`` 不再被执行，
    而是仅作为缓存键使用，从而获取已编译的 SQL。

    .. note:: 值得注意的是，即使不使用 lambda 系统，SQLAlchemy 也已经具备 SQL 缓存机制。
        lambda 系统只是额外增加了一层缓存逻辑，减少每条 SQL 语句构造时的工作量，
        并采用更简化的缓存键。

.. tab:: 英文

    Lambda statements are constructed using the :func:`_sql.lambda_stmt` function,
    which returns an instance of :class:`_sql.StatementLambdaElement`, which is
    itself an executable statement construct.    Additional modifiers and criteria
    are added to the object using the Python addition operator ``+``, or
    alternatively the :meth:`_sql.StatementLambdaElement.add_criteria` method which
    allows for more options.

    It is assumed that the :func:`_sql.lambda_stmt` construct is being invoked
    within an enclosing function or method that expects to be used many times
    within an application, so that subsequent executions beyond the first one
    can take advantage of the compiled SQL being cached.  When the lambda is
    constructed inside of an enclosing function in Python it is then subject
    to also having closure variables, which are significant to the whole
    approach::

        from sqlalchemy import lambda_stmt


        def run_my_statement(connection, parameter):
            stmt = lambda_stmt(lambda: select(table))
            stmt += lambda s: s.where(table.c.col == parameter)
            stmt += lambda s: s.order_by(table.c.id)

            return connection.execute(stmt)


        with engine.connect() as conn:
            result = run_my_statement(some_connection, "some parameter")

    Above, the three ``lambda`` callables that are used to define the structure
    of a SELECT statement are invoked exactly once, and the resulting SQL
    string cached in the compilation cache of the engine.   From that point
    forward, the ``run_my_statement()`` function may be invoked any number
    of times and the ``lambda`` callables within it will not be called, only
    used as cache keys to retrieve the already-compiled SQL.

    .. note::  It is important to note that there is already SQL caching in place
        when the lambda system is not used.   The lambda system only adds an
        additional layer of work reduction per SQL statement invoked by caching
        the building up of the SQL construct itself and also using a simpler
        cache key.


Lambda 快速指南
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quick Guidelines for Lambdas

.. tab:: 中文

    在整个 lambda SQL 系统中，最重要的原则是确保 lambda 所生成的缓存键
    与其生成的 SQL 字符串严格一致。
    :class:`_sql.LambdaElement` 及相关对象会运行并分析提供的 lambda，
    以确定其缓存策略，并尝试检测潜在问题。以下是一些基本指南：
    
    * **支持所有类型的语句** —— 尽管 :func:`_sql.select` 是最常见的使用方式，
      但 DML 语句（如 :func:`_sql.insert`、:func:`_sql.update`）同样适用::
    
        def upd(id_, newname):
            stmt = lambda_stmt(lambda: users.update())
            stmt += lambda s: s.values(name=newname)
            stmt += lambda s: s.where(users.c.id == id_)
            return stmt
    
        with engine.begin() as conn:
            conn.execute(upd(7, "foo"))
    
      ..
    
    * **同样适用于 ORM 场景** —— :func:`_sql.lambda_stmt` 可完全支持 ORM 功能，
      可直接用于 :meth:`_orm.Session.execute`::
    
        def select_user(session, name):
            stmt = lambda_stmt(lambda: select(User))
            stmt += lambda s: s.where(User.name == name)
    
            row = session.execute(stmt).first()
            return row
    
      ..
    
    * **绑定参数自动支持** —— 与 SQLAlchemy 早期的“预烘焙查询（baked query）”系统不同，
      lambda SQL 系统会自动识别闭包中的 Python 字面值并将其作为绑定参数。
      即便每个 lambda 仅执行一次，其闭包中提取的值仍会被用于参数绑定：
    
      .. sourcecode:: pycon+sql
    
            >>> def my_stmt(x, y):
            ...     stmt = lambda_stmt(lambda: select(func.max(x, y)))
            ...     return stmt
            >>> engine = create_engine("sqlite://", echo=True)
            >>> with engine.connect() as conn:
            ...     print(conn.scalar(my_stmt(5, 10)))
            ...     print(conn.scalar(my_stmt(12, 8)))
            {execsql}SELECT max(?, ?) AS max_1
            [generated in 0.00057s] (5, 10){stop}
            10
            {execsql}SELECT max(?, ?) AS max_1
            [cached since 0.002059s ago] (12, 8){stop}
            12
    
      上例中，:class:`_sql.StatementLambdaElement` 每次调用时都从 lambda 的闭包中提取 ``x`` 和 ``y``，
      并将它们作为绑定参数传递给缓存的 SQL 结构。
    
    * **lambda 理应始终生成一致的 SQL 结构** —— 避免在 lambda 中使用条件语句或自定义函数，
      否则可能生成结构不同的 SQL。如果确实需要使用不同的 SQL 片段，应分别使用多个 lambda::
    
            # **不要这样做：**
    
            def my_stmt(parameter, thing=False):
                stmt = lambda_stmt(lambda: select(table))
                stmt += lambda s: (
                    s.where(table.c.x > parameter) if thing else s.where(table.c.y == parameter)
                )
                return stmt
    
            # **应该这样做：**
    
            def my_stmt(parameter, thing=False):
                stmt = lambda_stmt(lambda: select(table))
                if thing:
                    stmt += lambda s: s.where(table.c.x > parameter)
                else:
                    stmt += lambda s: s.where(table.c.y == parameter)
                return stmt
    
      如果 lambda 不生成一致的 SQL 构造，可能会出现各种问题，目前有些问题尚无法自动检测。
    
    * **不要在 lambda 内调用函数来生成绑定值** —— lambda SQL 系统要求绑定值在 lambda 闭包中可直接获取。
      如果值来自函数调用，:class:`_sql.LambdaElement` 会抛出错误::
    
        >>> def my_stmt(x, y):
        ...     def get_x():
        ...         return x
        ...
        ...     def get_y():
        ...         return y
        ...
        ...     stmt = lambda_stmt(lambda: select(func.max(get_x(), get_y())))
        ...     return stmt
        >>> with engine.connect() as conn:
        ...     print(conn.scalar(my_stmt(5, 10)))
        Traceback (most recent call last):
          # ...
        sqlalchemy.exc.InvalidRequestError: 无法在 lambda 表达式中调用 Python 函数 get_x()
        生成绑定值；lambda SQL 系统不会实际调用 lambda 或其内部函数来提取绑定参数。
    
      上述示例中，应将 ``get_x()`` 和 ``get_y()`` 的结果提前获取并赋值为局部变量::
    
        >>> def my_stmt(x, y):
        ...     def get_x():
        ...         return x
        ...
        ...     def get_y():
        ...         return y
        ...
        ...     x_param, y_param = get_x(), get_y()
        ...     stmt = lambda_stmt(lambda: select(func.max(x_param, y_param)))
        ...     return stmt
    
      ..
    
    * **避免在 lambda 中引用非 SQL 构造对象，因为它们默认不可缓存** ——
      :class:`_sql.LambdaElement` 会将 lambda 的闭包中所有变量都视为缓存关键部分。
      默认情况下，没有对象会被假定为可缓存。以下代码会抛出详细错误::
    
        >>> class Foo:
        ...     def __init__(self, x, y):
        ...         self.x = x
        ...         self.y = y
        >>> def my_stmt(foo):
        ...     stmt = lambda_stmt(lambda: select(func.max(foo.x, foo.y)))
        ...     return stmt
        >>> with engine.connect() as conn:
        ...     print(conn.scalar(my_stmt(Foo(5, 10))))
        Traceback (most recent call last):
          # ...
        sqlalchemy.exc.InvalidRequestError: lambda 闭包中名为 'foo' 的变量不是可缓存的 SQL 元素，
        同时也不被认为是绑定参数；为生成正确的缓存键，应将该变量移出 lambda 范围，
        或设置 track_on=[<elements>] 来显式声明要追踪的闭包变量，
        或设置 track_closure_variables=False 排除闭包变量参与缓存键。
    
      此错误表明，:class:`_sql.LambdaElement` 默认不会假定传入的 ``Foo`` 实例始终行为一致，
      也不会自动将其作为缓存键的一部分。
    
      正确的做法是不要在 lambda 中引用 ``foo``，应在 lambda 外部提取其属性::
    
        >>> def my_stmt(foo):
        ...     x_param, y_param = foo.x, foo.y
        ...     stmt = lambda_stmt(lambda: select(func.max(x_param, y_param)))
        ...     return stmt
    
      如果可以确保 lambda 所生成的 SQL 结构永远不会因输入而变化，
      也可以将 ``track_closure_variables=False``，从而关闭闭包变量的跟踪功能::
    
        >>> def my_stmt(foo):
        ...     stmt = lambda_stmt(
        ...         lambda: select(func.max(foo.x, foo.y)), track_closure_variables=False
        ...     )
        ...     return stmt
    
      也可以使用 ``track_on`` 参数，显式指定某些对象作为缓存键，
      并防止其他闭包变量干扰缓存逻辑。
      适用于 SQL 来自上下文对象、但这些对象具有多种值的情况::
    
        >>> def my_stmt(self, foo):
        ...     stmt = lambda_stmt(
        ...         lambda: select(*self.column_expressions), track_closure_variables=False
        ...     )
        ...     stmt = stmt.add_criteria(lambda: self.where_criteria, track_on=[self])
        ...     return stmt
    
      使用 ``track_on`` 表示这些对象将被长期保留在 lambda 的内部缓存中，
      并维持强引用，直到缓存（默认最多 1000 项）被清除。


.. tab:: 英文

    Above all, the emphasis within the lambda SQL system is ensuring that there
    is never a mismatch between the cache key generated for a lambda and the
    SQL string it will produce.   The :class:`_sql.LambdaElement` and related
    objects will run and analyze the given lambda in order to calculate how
    it should be cached on each run, trying to detect any potential problems.
    Basic guidelines include:
    
    * **Any kind of statement is supported** - while it's expected that
      :func:`_sql.select` constructs are the prime use case for :func:`_sql.lambda_stmt`,
      DML statements such as :func:`_sql.insert` and :func:`_sql.update` are
      equally usable::
    
        def upd(id_, newname):
            stmt = lambda_stmt(lambda: users.update())
            stmt += lambda s: s.values(name=newname)
            stmt += lambda s: s.where(users.c.id == id_)
            return stmt
    
    
        with engine.begin() as conn:
            conn.execute(upd(7, "foo"))
    
      ..
    
    * **ORM use cases directly supported as well** - the :func:`_sql.lambda_stmt`
      can accommodate ORM functionality completely and used directly with
      :meth:`_orm.Session.execute`::
    
        def select_user(session, name):
            stmt = lambda_stmt(lambda: select(User))
            stmt += lambda s: s.where(User.name == name)
    
            row = session.execute(stmt).first()
            return row
    
      ..
    
    * **Bound parameters are automatically accommodated** - in contrast to SQLAlchemy's
      previous "baked query" system, the lambda SQL system accommodates for
      Python literal values which become SQL bound parameters automatically.
      This means that even though a given lambda runs only once, the values that
      become bound parameters are extracted from the **closure** of the lambda
      on every run:
    
      .. sourcecode:: pycon+sql
    
            >>> def my_stmt(x, y):
            ...     stmt = lambda_stmt(lambda: select(func.max(x, y)))
            ...     return stmt
            >>> engine = create_engine("sqlite://", echo=True)
            >>> with engine.connect() as conn:
            ...     print(conn.scalar(my_stmt(5, 10)))
            ...     print(conn.scalar(my_stmt(12, 8)))
            {execsql}SELECT max(?, ?) AS max_1
            [generated in 0.00057s] (5, 10){stop}
            10
            {execsql}SELECT max(?, ?) AS max_1
            [cached since 0.002059s ago] (12, 8){stop}
            12
    
      Above, :class:`_sql.StatementLambdaElement` extracted the values of ``x``
      and ``y`` from the **closure** of the lambda that is generated each time
      ``my_stmt()`` is invoked; these were substituted into the cached SQL
      construct as the values of the parameters.
    
    * **The lambda should ideally produce an identical SQL structure in all cases** -
      Avoid using conditionals or custom callables inside of lambdas that might make
      it produce different SQL based on inputs; if a function might conditionally
      use two different SQL fragments, use two separate lambdas::
    
            # **Don't** do this:
    
    
            def my_stmt(parameter, thing=False):
                stmt = lambda_stmt(lambda: select(table))
                stmt += lambda s: (
                    s.where(table.c.x > parameter) if thing else s.where(table.c.y == parameter)
                )
                return stmt
    
    
            # **Do** do this:
    
    
            def my_stmt(parameter, thing=False):
                stmt = lambda_stmt(lambda: select(table))
                if thing:
                    stmt += lambda s: s.where(table.c.x > parameter)
                else:
                    stmt += lambda s: s.where(table.c.y == parameter)
                return stmt
    
      There are a variety of failures which can occur if the lambda does not
      produce a consistent SQL construct and some are not trivially detectable
      right now.
    
    * **Don't use functions inside the lambda to produce bound values** - the
      bound value tracking approach requires that the actual value to be used in
      the SQL statement be locally present in the closure of the lambda.  This is
      not possible if values are generated from other functions, and the
      :class:`_sql.LambdaElement` should normally raise an error if this is
      attempted::
    
        >>> def my_stmt(x, y):
        ...     def get_x():
        ...         return x
        ...
        ...     def get_y():
        ...         return y
        ...
        ...     stmt = lambda_stmt(lambda: select(func.max(get_x(), get_y())))
        ...     return stmt
        >>> with engine.connect() as conn:
        ...     print(conn.scalar(my_stmt(5, 10)))
        Traceback (most recent call last):
          # ...
        sqlalchemy.exc.InvalidRequestError: Can't invoke Python callable get_x()
        inside of lambda expression argument at
        <code object <lambda> at 0x7fed15f350e0, file "<stdin>", line 6>;
        lambda SQL constructs should not invoke functions from closure variables
        to produce literal values since the lambda SQL system normally extracts
        bound values without actually invoking the lambda or any functions within it.
    
      Above, the use of ``get_x()`` and ``get_y()``, if they are necessary, should
      occur **outside** of the lambda and assigned to a local closure variable::
    
        >>> def my_stmt(x, y):
        ...     def get_x():
        ...         return x
        ...
        ...     def get_y():
        ...         return y
        ...
        ...     x_param, y_param = get_x(), get_y()
        ...     stmt = lambda_stmt(lambda: select(func.max(x_param, y_param)))
        ...     return stmt
    
      ..
    
    * **Avoid referring to non-SQL constructs inside of lambdas as they are not
      cacheable by default** - this issue refers to how the :class:`_sql.LambdaElement`
      creates a cache key from other closure variables within the statement.  In order
      to provide the best guarantee of an accurate cache key, all objects located
      in the closure of the lambda are considered to be significant, and none
      will be assumed to be appropriate for a cache key by default.
      So the following example will also raise a rather detailed error message::
    
        >>> class Foo:
        ...     def __init__(self, x, y):
        ...         self.x = x
        ...         self.y = y
        >>> def my_stmt(foo):
        ...     stmt = lambda_stmt(lambda: select(func.max(foo.x, foo.y)))
        ...     return stmt
        >>> with engine.connect() as conn:
        ...     print(conn.scalar(my_stmt(Foo(5, 10))))
        Traceback (most recent call last):
          # ...
        sqlalchemy.exc.InvalidRequestError: Closure variable named 'foo' inside of
        lambda callable <code object <lambda> at 0x7fed15f35450, file
        "<stdin>", line 2> does not refer to a cacheable SQL element, and also
        does not appear to be serving as a SQL literal bound value based on the
        default SQL expression returned by the function.  This variable needs to
        remain outside the scope of a SQL-generating lambda so that a proper cache
        key may be generated from the lambda's state.  Evaluate this variable
        outside of the lambda, set track_on=[<elements>] to explicitly select
        closure elements to track, or set track_closure_variables=False to exclude
        closure variables from being part of the cache key.
    
      The above error indicates that :class:`_sql.LambdaElement` will not assume
      that the ``Foo`` object passed in will continue to behave the same in all
      cases.    It also won't assume it can use ``Foo`` as part of the cache key
      by default; if it were to use the ``Foo`` object as part of the cache key,
      if there were many different ``Foo`` objects this would fill up the cache
      with duplicate information, and would also hold long-lasting references to
      all of these objects.
    
      The best way to resolve the above situation is to not refer to ``foo``
      inside of the lambda, and refer to it **outside** instead::
    
        >>> def my_stmt(foo):
        ...     x_param, y_param = foo.x, foo.y
        ...     stmt = lambda_stmt(lambda: select(func.max(x_param, y_param)))
        ...     return stmt
    
      In some situations, if the SQL structure of the lambda is guaranteed to
      never change based on input, to pass ``track_closure_variables=False``
      which will disable any tracking of closure variables other than those
      used for bound parameters::
    
        >>> def my_stmt(foo):
        ...     stmt = lambda_stmt(
        ...         lambda: select(func.max(foo.x, foo.y)), track_closure_variables=False
        ...     )
        ...     return stmt
    
      There is also the option to add objects to the element to explicitly form
      part of the cache key, using the ``track_on`` parameter; using this parameter
      allows specific values to serve as the cache key and will also prevent other
      closure variables from being considered.  This is useful for cases where part
      of the SQL being constructed originates from a contextual object of some sort
      that may have many different values.  In the example below, the first
      segment of the SELECT statement will disable tracking of the ``foo`` variable,
      whereas the second segment will explicitly track ``self`` as part of the
      cache key::
    
        >>> def my_stmt(self, foo):
        ...     stmt = lambda_stmt(
        ...         lambda: select(*self.column_expressions), track_closure_variables=False
        ...     )
        ...     stmt = stmt.add_criteria(lambda: self.where_criteria, track_on=[self])
        ...     return stmt
    
      Using ``track_on`` means the given objects will be stored long term in the
      lambda's internal cache and will have strong references for as long as the
      cache doesn't clear out those objects (an LRU scheme of 1000 entries is used
      by default).
    
      ..


缓存键生成
^^^^^^^^^^^^^^^^^^^^

Cache Key Generation

.. tab:: 中文

    为了理解与 lambda SQL 构造相关的一些选项和行为，了解缓存系统是有帮助的。
    
    SQLAlchemy 的缓存系统通常通过生成一个缓存键来表示给定的 SQL 表达式构造，生成一个表示构造内部所有状态的结构::
    
        >>> from sqlalchemy import select, column
        >>> stmt = select(column("q"))
        >>> cache_key = stmt._generate_cache_key()
        >>> print(cache_key)  # 部分简化版
        CacheKey(key=(
        '0',
        <class 'sqlalchemy.sql.selectable.Select'>,
        '_raw_columns',
        (
            (
            '1',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
                <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
            ),
        ),
        # 更复杂的 SELECT 语句中会有更多元素
        ),)
    
    上面的缓存键被存储在缓存中，缓存本质上是一个字典，值是一个构造体，其中包含 SQL 语句的字符串形式，在此例中是 "SELECT q"。我们可以观察到，即使对于一个极其简短的查询，缓存键也非常冗长，因为它必须表示关于渲染和执行的所有可变部分。
    
    与此不同，lambda 构造系统会创建一个不同类型的缓存键::
    
        >>> from sqlalchemy import lambda_stmt
        >>> stmt = lambda_stmt(lambda: select(column("q")))
        >>> cache_key = stmt._generate_cache_key()
        >>> print(cache_key)
        CacheKey(key=(
        <code object <lambda> at 0x7fed1617c710, file "<stdin>", line 1>,
        <class 'sqlalchemy.sql.lambdas.StatementLambdaElement'>,
        ),)
    
    上面，我们看到一个比非 lambda 语句缓存键短得多的缓存键，此外， ``select(column("q"))`` 构造本身甚至没有必要生成；Python lambda 本身包含一个名为 ``__code__`` 的属性，指向一个 Python 代码对象，在应用程序运行时该对象是不可变和永久的。
    
    当 lambda 还包括闭包变量时，在正常情况下，如果这些变量引用 SQL 构造（例如列对象），它们会成为缓存键的一部分；如果它们引用将绑定的参数的字面值，它们将被放置在缓存键的另一个元素中::
    
        >>> def my_stmt(parameter):
        ...     col = column("q")
        ...     stmt = lambda_stmt(lambda: select(col))
        ...     stmt += lambda s: s.where(col == parameter)
        ...     return stmt
    
    上述的 `class:_sql.StatementLambdaElement` 包含两个 lambda，这两个 lambda 都引用了 ``col`` 闭包变量，因此缓存键将表示这两个部分以及 ``column()`` 对象::
    
    
        >>> stmt = my_stmt(5)
        >>> key = stmt._generate_cache_key()
        >>> print(key)
        CacheKey(key=(
        <code object <lambda> at 0x7f07323c50e0, file "<stdin>", line 3>,
        (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
            <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
        ),
        <code object <lambda> at 0x7f07323c5190, file "<stdin>", line 4>,
        <class 'sqlalchemy.sql.lambdas.LinkedLambdaElement'>,
        (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
            <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
        ),
        (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
            <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
        ),
        ),)
    
    缓存键的第二部分已检索到将在调用语句时使用的绑定参数::
    
        >>> key.bindparams
        [BindParameter('%(139668884281280 parameter)s', 5, type_=Integer())]
    
    关于 “lambda” 缓存的多个示例和性能比较，请参见 :ref:`examples_performance` 性能示例中的 "short_selects" 测试集。
    
.. tab:: 英文

    In order to understand some of the options and behaviors which occur
    with lambda SQL constructs, an understanding of the caching system
    is helpful.
    
    SQLAlchemy's caching system normally generates a cache key from a given
    SQL expression construct by producing a structure that represents all the
    state within the construct::
    
        >>> from sqlalchemy import select, column
        >>> stmt = select(column("q"))
        >>> cache_key = stmt._generate_cache_key()
        >>> print(cache_key)  # somewhat paraphrased
        CacheKey(key=(
          '0',
          <class 'sqlalchemy.sql.selectable.Select'>,
          '_raw_columns',
          (
            (
              '1',
              <class 'sqlalchemy.sql.elements.ColumnClause'>,
              'name',
              'q',
              'type',
              (
                <class 'sqlalchemy.sql.sqltypes.NullType'>,
              ),
            ),
          ),
          # a few more elements are here, and many more for a more
          # complicated SELECT statement
        ),)
    
    
    The above key is stored in the cache which is essentially a dictionary, and the
    value is a construct that among other things stores the string form of the SQL
    statement, in this case the phrase "SELECT q".  We can observe that even for an
    extremely short query the cache key is pretty verbose as it has to represent
    everything that may vary about what's being rendered and potentially executed.
    
    The lambda construction system by contrast creates a different kind of cache
    key::
    
        >>> from sqlalchemy import lambda_stmt
        >>> stmt = lambda_stmt(lambda: select(column("q")))
        >>> cache_key = stmt._generate_cache_key()
        >>> print(cache_key)
        CacheKey(key=(
          <code object <lambda> at 0x7fed1617c710, file "<stdin>", line 1>,
          <class 'sqlalchemy.sql.lambdas.StatementLambdaElement'>,
        ),)
    
    Above, we see a cache key that is vastly shorter than that of the non-lambda
    statement, and additionally that production of the ``select(column("q"))``
    construct itself was not even necessary; the Python lambda itself contains
    an attribute called ``__code__`` which refers to a Python code object that
    within the runtime of the application is immutable and permanent.
    
    When the lambda also includes closure variables, in the normal case that these
    variables refer to SQL constructs such as column objects, they become
    part of the cache key, or if they refer to literal values that will be bound
    parameters, they are placed in a separate element of the cache key::
    
        >>> def my_stmt(parameter):
        ...     col = column("q")
        ...     stmt = lambda_stmt(lambda: select(col))
        ...     stmt += lambda s: s.where(col == parameter)
        ...     return stmt
    
    The above :class:`_sql.StatementLambdaElement` includes two lambdas, both
    of which refer to the ``col`` closure variable, so the cache key will
    represent both of these segments as well as the ``column()`` object::
    
        >>> stmt = my_stmt(5)
        >>> key = stmt._generate_cache_key()
        >>> print(key)
        CacheKey(key=(
          <code object <lambda> at 0x7f07323c50e0, file "<stdin>", line 3>,
          (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
              <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
          ),
          <code object <lambda> at 0x7f07323c5190, file "<stdin>", line 4>,
          <class 'sqlalchemy.sql.lambdas.LinkedLambdaElement'>,
          (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
              <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
          ),
          (
            '0',
            <class 'sqlalchemy.sql.elements.ColumnClause'>,
            'name',
            'q',
            'type',
            (
              <class 'sqlalchemy.sql.sqltypes.NullType'>,
            ),
          ),
        ),)
    
    
    The second part of the cache key has retrieved the bound parameters that will
    be used when the statement is invoked::
    
        >>> key.bindparams
        [BindParameter('%(139668884281280 parameter)s', 5, type_=Integer())]
    
    
    For a series of examples of "lambda" caching with performance comparisons,
    see the "short_selects" test suite within the :ref:`examples_performance`
    performance example.

.. _engine_insertmanyvalues:

INSERT 语句的“插入多个值”行为
---------------------------------------------------

"Insert Many Values" Behavior for INSERT statements

.. tab:: 中文
    
    .. versionadded:: 2.0 
        
        参见 :ref:`change_6047` 获取关于更改的背景信息，包括性能测试示例。
    
    .. tip:: 
        
        `insertmanyvalues` 特性是一个 **透明可用的** 性能特性，用户无需干预即可在需要时启用。 本节描述了该特性的架构，并介绍了如何衡量其性能以及调整其行为以优化批量 INSERT 语句的速度，特别是在 ORM 中的应用。
    
    随着更多数据库支持 `INSERT..RETURNING`，SQLAlchemy 在处理需要获取服务器生成的值的 INSERT 语句方面发生了重大变化，最重要的是获取服务器生成的主键值，这使得新行可以在后续操作中被引用。特别是，在 ORM 中，这个场景长期以来一直是一个显著的性能问题，ORM 依赖于能够检索服务器生成的主键值，以便正确填充 :term:`identity map`。
    
    随着最近 SQLite 和 MariaDB 对 RETURNING 的支持，SQLAlchemy 不再需要依赖 :term:`DBAPI` 提供的单行 `cursor.lastrowid <https://peps.python.org/pep-0249/#lastrowid>`_ 属性；RETURNING 现在可以用于所有 :ref:`SQLAlchemy-included <included_dialects>` 后端，除了 MySQL。剩下的性能限制，即 `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_ DBAPI 方法不允许获取行，已经通过避免使用 ``executemany()`` 并重新结构化单独的 INSERT 语句来解决，每个语句都能在单个语句中容纳大量行，并通过 ``cursor.execute()`` 调用。这种方法起源于 ``psycopg2`` DBAPI 的 `psycopg2 fast execution helpers <https://www.psycopg.org/docs/extras.html#fast-execution-helpers>`_ 特性，SQLAlchemy 在最近的版本中逐步增加了对该特性的支持。

.. tab:: 英文

    .. versionadded:: 2.0 see :ref:`change_6047` for background on the change
       including sample performance tests
    
    .. tip:: The :term:`insertmanyvalues` feature is a **transparently available**
       performance feature which requires no end-user intervention in order for
       it to take place as needed.   This section describes the architecture
       of the feature as well as how to measure its performance and tune its
       behavior in order to optimize the speed of bulk INSERT statements,
       particularly as used by the ORM.
    
    As more databases have added support for INSERT..RETURNING, SQLAlchemy has
    undergone a major change in how it approaches the subject of INSERT statements
    where there's a need to acquire server-generated values, most importantly
    server-generated primary key values which allow the new row to be referenced in
    subsequent operations. In particular, this scenario has long been a significant
    performance issue in the ORM, which relies on being able to retrieve
    server-generated primary key values in order to correctly populate the
    :term:`identity map`.
    
    With recent support for RETURNING added to SQLite and MariaDB, SQLAlchemy no
    longer needs to rely upon the single-row-only
    `cursor.lastrowid <https://peps.python.org/pep-0249/#lastrowid>`_ attribute
    provided by the :term:`DBAPI` for most backends; RETURNING may now be used for
    all :ref:`SQLAlchemy-included <included_dialects>` backends with the exception
    of MySQL. The remaining performance
    limitation, that the
    `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_ DBAPI
    method does not allow for rows to be fetched, is resolved for most backends by
    foregoing the use of ``executemany()`` and instead restructuring individual
    INSERT statements to each accommodate a large number of rows in a single
    statement that is invoked using ``cursor.execute()``. This approach originates
    from the
    `psycopg2 fast execution helpers <https://www.psycopg.org/docs/extras.html#fast-execution-helpers>`_
    feature of the ``psycopg2`` DBAPI, which SQLAlchemy incrementally added more
    and more support towards in recent release series.

当前支持
~~~~~~~~~~~~~~~

Current Support

.. tab:: 中文
    
    此功能适用于 SQLAlchemy 中所有支持 RETURNING 的后端，Oracle 数据库除外，后者的 python-oracledb 和 cx_Oracle 驱动程序提供了自己的等效功能。该功能通常在使用 :meth:`_dml.Insert.returning` 方法与 :term:`executemany` 执行一起使用时生效，当将字典列表传递给 :paramref:`_engine.Connection.execute.parameters` 参数时，发生在 :meth:`_engine.Connection.execute` 或 :meth:`_orm.Session.execute` 方法（以及 :ref:`asyncio <asyncio_toplevel>` 和简写方法如 :meth:`_orm.Session.scalars` 下的等效方法）中执行。此外，当使用像 :meth:`_orm.Session.add` 和 :meth:`_orm.Session.add_all` 这样的方法添加行时，它也会在 ORM 的 :term:`unit of work` 过程中生效。
    
    对于 SQLAlchemy 包含的方言，当前支持或等效支持如下：
    
    * SQLite - 支持 SQLite 版本 3.35 及以上
    * PostgreSQL - 所有支持的 PostgreSQL 版本（9 及以上）
    * SQL Server - 所有支持的 SQL Server 版本 [#]_
    * MariaDB - 支持 MariaDB 版本 10.5 及以上
    * MySQL - 不支持，缺少 RETURNING 功能
    * Oracle 数据库 - 使用本地 python-oracledb / cx_Oracle API 支持 RETURNING 与 executemany，适用于所有支持的 Oracle 数据库版本 9 及以上，使用多行 OUT 参数。这与 "executemanyvalues" 实现不同，但具有相同的使用模式和等效的性能优势。
    
    .. versionchanged:: 2.0.10
    
       .. [#] Microsoft SQL Server 的 "insertmanyvalues" 支持在版本 2.0.9 中暂时禁用后已恢复。

.. tab:: 英文
    
    The feature is enabled for all backend included in SQLAlchemy that support
    RETURNING, with the exception of Oracle Database for which both the
    python-oracledb and cx_Oracle drivers offer their own equivalent feature. The
    feature normally takes place when making use of the
    :meth:`_dml.Insert.returning` method of an :class:`_dml.Insert` construct in
    conjunction with :term:`executemany` execution, which occurs when passing a
    list of dictionaries to the :paramref:`_engine.Connection.execute.parameters`
    parameter of the :meth:`_engine.Connection.execute` or
    :meth:`_orm.Session.execute` methods (as well as equivalent methods under
    :ref:`asyncio <asyncio_toplevel>` and shorthand methods like
    :meth:`_orm.Session.scalars`). It also takes place within the ORM :term:`unit
    of work` process when using methods such as :meth:`_orm.Session.add` and
    :meth:`_orm.Session.add_all` to add rows.
    
    For SQLAlchemy's included dialects, support or equivalent support is currently
    as follows:
    
    * SQLite - supported for SQLite versions 3.35 and above
    * PostgreSQL - all supported Postgresql versions (9 and above)
    * SQL Server - all supported SQL Server versions [#]_
    * MariaDB - supported for MariaDB versions 10.5 and above
    * MySQL - no support, no RETURNING feature is present
    * Oracle Database - supports RETURNING with executemany using native python-oracledb / cx_Oracle
      APIs, for all supported Oracle Database versions 9 and above, using multi-row OUT
      parameters. This is not the same implementation as "executemanyvalues", however has
      the same usage patterns and equivalent performance benefits.
    
    .. versionchanged:: 2.0.10
    
       .. [#] "insertmanyvalues" support for Microsoft SQL Server
          is restored, after being temporarily disabled in version 2.0.9.

禁用该功能
~~~~~~~~~~~~~~~~~~~~~

Disabling the feature

.. tab:: 中文

    要禁用给定后端的 "insertmanyvalues" 功能，可以为 :class:`.Engine` 传递 :paramref:`_sa.create_engine.use_insertmanyvalues` 参数并设置为 ``False``，如以下所示::

        engine = create_engine(
            "mariadb+mariadbconnector://scott:tiger@host/db", use_insertmanyvalues=False
        )

    也可以通过将 :paramref:`_schema.Table.implicit_returning` 参数设置为 ``False`` 来禁用某个特定 :class:`_schema.Table` 对象隐式使用此功能::

        t = Table(
            "t",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("x", Integer),
            implicit_returning=False,
        )

    禁用特定表的 RETURNING 功能的原因是绕过特定后端的限制。

.. tab:: 英文

    To disable the "insertmanyvalues" feature for a given backend for an
    :class:`.Engine` overall, pass the
    :paramref:`_sa.create_engine.use_insertmanyvalues` parameter as ``False`` to
    :func:`_sa.create_engine`::

        engine = create_engine(
            "mariadb+mariadbconnector://scott:tiger@host/db", use_insertmanyvalues=False
        )

    The feature can also be disabled from being used implicitly for a particular
    :class:`_schema.Table` object by passing the
    :paramref:`_schema.Table.implicit_returning` parameter as ``False``::

        t = Table(
            "t",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("x", Integer),
            implicit_returning=False,
        )

    The reason one might want to disable RETURNING for a specific table is to
    work around backend-specific limitations.


批处理模式操作
~~~~~~~~~~~~~~~~~~~~~~

Batched Mode Operation

.. tab:: 中文

    该功能有两种操作模式，根据方言和 :class:`_schema.Table` 来透明选择。其一是 **批处理模式**，它通过重写如下形式的 INSERT 语句来减少数据库往返次数：

    .. sourcecode:: sql

        INSERT INTO a (data, x, y) VALUES (%(data)s, %(x)s, %(y)s) RETURNING a.id

    变为类似这样的 "批处理" 形式：

    .. sourcecode:: sql

        INSERT INTO a (data, x, y) VALUES
            (%(data_0)s, %(x_0)s, %(y_0)s),
            (%(data_1)s, %(x_1)s, %(y_1)s),
            (%(data_2)s, %(x_2)s, %(y_2)s),
            ...
            (%(data_78)s, %(x_78)s, %(y_78)s)
        RETURNING a.id

    在上面的语句中，语句是按输入数据的子集（"批次"）进行组织的，批次的大小由数据库后端决定，并且每个批次中的参数数量必须符合已知的语句大小/参数数量限制。该功能随后为每个输入数据批次执行一次 INSERT 语句，直到所有记录都被处理，并将每个批次的 RETURNING 结果连接到一个单独的大行集，供一个 :class:`_result.Result` 对象访问。

    这种 "批处理" 形式允许使用更少的数据库往返插入许多行，并且在大多数后端支持的情况下，已证明能显著提高性能。

.. tab:: 英文

    The feature has two modes of operation, which are selected transparently on a
    per-dialect, per-:class:`_schema.Table` basis. One is **batched mode**,
    which reduces the number of database round trips by rewriting an
    INSERT statement of the form:

    .. sourcecode:: sql

        INSERT INTO a (data, x, y) VALUES (%(data)s, %(x)s, %(y)s) RETURNING a.id

    into a "batched" form such as:

    .. sourcecode:: sql

        INSERT INTO a (data, x, y) VALUES
            (%(data_0)s, %(x_0)s, %(y_0)s),
            (%(data_1)s, %(x_1)s, %(y_1)s),
            (%(data_2)s, %(x_2)s, %(y_2)s),
            ...
            (%(data_78)s, %(x_78)s, %(y_78)s)
        RETURNING a.id

    where above, the statement is organized against a subset (a "batch") of the
    input data, the size of which is determined by the database backend as well as
    the number of parameters in each batch to correspond to known limits for
    statement size / number of parameters.  The feature then executes the INSERT
    statement once for each batch of input data until all records are consumed,
    concatenating the RETURNING results for each batch into a single large
    rowset that's available from a single :class:`_result.Result` object.

    This "batched" form allows INSERT of many rows using much fewer database round
    trips, and has been shown to allow dramatic performance improvements for most
    backends where it's supported.

.. _engine_insertmanyvalues_returning_order:

将 RETURNING 行关联到参数集
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Correlating RETURNING rows to parameter sets

.. versionadded:: 2.0.10

.. tab:: 中文

    前一节中说明的“批处理”模式查询并不保证返回的记录顺序与输入数据的顺序一致。当SQLAlchemy ORM的 :term:`unit of work` 过程使用时，以及在需要将返回的服务器生成值与输入数据相关联的应用程序中， :meth:`_dml.Insert.returning` 和 :meth:`_dml.UpdateBase.return_defaults` 方法包含一个选项 :paramref:`_dml.Insert.returning.sort_by_parameter_order`，该选项表示“insertmanyvalues”模式应保证这种对应关系。这与数据库后端实际插入记录的顺序无关，后者在任何情况下都 **不** 作假设；只是返回的记录应该按原始输入数据传递的顺序进行组织。

    当 :paramref:`_dml.Insert.returning.sort_by_parameter_order` 参数存在时，对于使用服务器生成的整数主键值（如 ``IDENTITY``、PostgreSQL ``SERIAL``、MariaDB ``AUTO_INCREMENT`` 或SQLite的 ``ROWID`` 方案）的表，"批处理"模式可能会选择使用更复杂的 INSERT..RETURNING 形式，结合基于返回值的行后排序，或者如果此形式不可用，"insertmanyvalues" 功能可能会优雅地降级为“非批处理”模式，这将为每个参数集运行单独的 INSERT 语句。

    例如，在 SQL Server 上，当使用自动递增的 ``IDENTITY`` 列作为主键时，将使用以下 SQL 形式：

    .. sourcecode:: sql

        INSERT INTO a (data, x, y)
        OUTPUT inserted.id, inserted.id AS id__1
        SELECT p0, p1, p2 FROM (VALUES
            (?, ?, ?, 0), (?, ?, ?, 1), (?, ?, ?, 2),
            ...
            (?, ?, ?, 77)
        ) AS imp_sen(p0, p1, p2, sen_counter) ORDER BY sen_counter

    对于 PostgreSQL，当主键列使用 SERIAL 或 IDENTITY 时，也使用类似的形式。上面的形式 **不** 保证行插入的顺序。然而，它保证 IDENTITY 或 SERIAL 值会随着每个参数集按顺序创建 [#]_。然后，“insertmanyvalues”功能按递增的整数身份对上述 INSERT 语句返回的行进行排序。

    对于 SQLite 数据库，没有适当的 INSERT 形式可以将新生成的 ROWID 值与传递参数集的顺序相关联。因此，当使用服务器生成的主键值时，SQLite 后端在请求有序的 RETURNING 时将降级为“非批处理”模式。对于 MariaDB，insertmanyvalues 使用的默认 INSERT 形式足够，因为该数据库后端会在使用 InnoDB 时将 AUTO_INCREMENT 的顺序与输入数据的顺序对齐 [#]_。

    对于客户端生成的主键，例如使用 Python ``uuid.uuid4()`` 函数生成新的 :class:`.Uuid` 列的值时，“insertmanyvalues”功能会透明地将此列包括在 RETURNING 记录中，并将其值与给定输入记录的值相关联，从而保持输入记录和结果行之间的对应关系。因此，当使用客户端生成的主键值时，所有后端都允许批量、参数相关的 RETURNING 顺序。

    “insertmanyvalues” “批处理”模式如何确定用于作为输入参数和 RETURNING 行之间对应关系的列被称为 :term:`insert sentinel`，它是用于跟踪这些值的特定列或列。通常，"insert sentinel" 会自动选择，但在极特殊的情况下也可以进行用户配置；有关详细信息，请参见 :ref:`engine_insertmanyvalues_sentinel_columns`。

    对于没有提供适当 INSERT 形式的后端，这些形式无法将服务器生成的值与输入值确定性对齐，或者对于具有其他类型服务器生成主键值的 :class:`_schema.Table` 配置，当要求保证 RETURNING 排序时，"insertmanyvalues" 模式将使用 **非批处理** 模式。

    .. seealso::

        .. [#]

        * Microsoft SQL Server 原因

        "使用 SELECT 与 ORDER BY 填充行的 INSERT 查询保证了身份值的计算顺序，但不保证行插入的顺序。"
        https://learn.microsoft.com/en-us/sql/t-sql/statements/insert-transact-sql?view=sql-server-ver16#limitations-and-restrictions

        * PostgreSQL 批量 INSERT 讨论

        2018年原始描述 https://www.postgresql.org/message-id/29386.1528813619@sss.pgh.pa.us

        2023年跟进 - https://www.postgresql.org/message-id/be108555-da2a-4abc-a46b-acbe8b55bd25%40app.fastmail.com

        .. [#]

    * MariaDB AUTO_INCREMENT 行为（使用与 MySQL 相同的 InnoDB 引擎）:

        https://dev.mysql.com/doc/refman/8.0/en/innodb-auto-increment-handling.html

        https://dba.stackexchange.com/a/72099


.. tab:: 英文

    The "batch" mode query illustrated in the previous section does not guarantee
    the order of records returned would correspond with that of the input data.
    When used by the SQLAlchemy ORM :term:`unit of work` process, as well as for
    applications which correlate returned server-generated values with input data,
    the :meth:`_dml.Insert.returning` and :meth:`_dml.UpdateBase.return_defaults`
    methods include an option
    :paramref:`_dml.Insert.returning.sort_by_parameter_order` which indicates that
    "insertmanyvalues" mode should guarantee this correspondence. This is **not
    related** to the order in which records are actually INSERTed by the database
    backend, which is **not** assumed under any circumstances; only that the
    returned records should be organized when received back to correspond to the
    order in which the original input data was passed.
    
    When the :paramref:`_dml.Insert.returning.sort_by_parameter_order` parameter is
    present, for tables that use server-generated integer primary key values such
    as ``IDENTITY``, PostgreSQL ``SERIAL``, MariaDB ``AUTO_INCREMENT``, or SQLite's
    ``ROWID`` scheme, "batch" mode may instead opt to use a more complex
    INSERT..RETURNING form, in conjunction with post-execution sorting of rows
    based on the returned values, or if
    such a form is not available, the "insertmanyvalues" feature may gracefully
    degrade to "non-batched" mode which runs individual INSERT statements for each
    parameter set.
    
    For example, on SQL Server when an auto incrementing ``IDENTITY`` column is
    used as the primary key, the following SQL form is used:
    
    .. sourcecode:: sql
    
        INSERT INTO a (data, x, y)
        OUTPUT inserted.id, inserted.id AS id__1
        SELECT p0, p1, p2 FROM (VALUES
            (?, ?, ?, 0), (?, ?, ?, 1), (?, ?, ?, 2),
            ...
            (?, ?, ?, 77)
        ) AS imp_sen(p0, p1, p2, sen_counter) ORDER BY sen_counter
    
    A similar form is used for PostgreSQL as well, when primary key columns use
    SERIAL or IDENTITY. The above form **does not** guarantee the order in which
    rows are inserted. However, it does guarantee that the IDENTITY or SERIAL
    values will be created in order with each parameter set [#]_. The
    "insertmanyvalues" feature then sorts the returned rows for the above INSERT
    statement by incrementing integer identity.
    
    For the SQLite database, there is no appropriate INSERT form that can
    correlate the production of new ROWID values with the order in which
    the parameter sets are passed.  As a result, when using server-generated
    primary key values, the SQLite backend will degrade to "non-batched"
    mode when ordered RETURNING is requested.
    For MariaDB, the default INSERT form used by insertmanyvalues is sufficient,
    as this database backend will line up the
    order of AUTO_INCREMENT with the order of input data when using InnoDB [#]_.
    
    For a client-side generated primary key, such as when using the Python
    ``uuid.uuid4()`` function to generate new values for a :class:`.Uuid` column,
    the "insertmanyvalues" feature transparently includes this column in the
    RETURNING records and correlates its value to that of the given input records,
    thus maintaining correspondence between input records and result rows. From
    this, it follows that all backends allow for batched, parameter-correlated
    RETURNING order when client-side-generated primary key values are used.
    
    The subject of how "insertmanyvalues" "batch" mode determines a column or
    columns to use as a point of correspondence between input parameters and
    RETURNING rows is known as an :term:`insert sentinel`, which is a specific
    column or columns that are used to track such values. The "insert sentinel" is
    normally selected automatically, however can also be user-configuration for
    extremely special cases; the section
    :ref:`engine_insertmanyvalues_sentinel_columns` describes this.
    
    For backends that do not offer an appropriate INSERT form that can deliver
    server-generated values deterministically aligned with input values, or
    for :class:`_schema.Table` configurations that feature other kinds of
    server generated primary key values, "insertmanyvalues" mode will make use
    of **non-batched** mode when guaranteed RETURNING ordering is requested.
    
    .. seealso::
    
        .. [#]
    
        * Microsoft SQL Server rationale
    
          "INSERT queries that use SELECT with ORDER BY to populate rows guarantees
          how identity values are computed but not the order in which the rows are inserted."
          https://learn.microsoft.com/en-us/sql/t-sql/statements/insert-transact-sql?view=sql-server-ver16#limitations-and-restrictions
    
        * PostgreSQL batched INSERT Discussion
    
          Original description in 2018 https://www.postgresql.org/message-id/29386.1528813619@sss.pgh.pa.us
    
          Follow up in 2023 - https://www.postgresql.org/message-id/be108555-da2a-4abc-a46b-acbe8b55bd25%40app.fastmail.com
    
        .. [#]
    
       * MariaDB AUTO_INCREMENT behavior (using the same InnoDB engine as MySQL):
    
         https://dev.mysql.com/doc/refman/8.0/en/innodb-auto-increment-handling.html
    
         https://dba.stackexchange.com/a/72099

.. _engine_insertmanyvalues_non_batch:

非批处理模式操作
~~~~~~~~~~~~~~~~~~~~~~~~~~

Non-Batched Mode Operation

.. tab:: 中文

    对于没有客户端主键值的 :class:`_schema.Table` 配置，并且提供服务器生成的主键值（或没有主键）的数据库，这些数据库无法以相对多个参数集的确定性或可排序的方式调用这些主键值，当要求满足 :paramref:`_dml.Insert.returning.sort_by_parameter_order` 的 :class:`_dml.Insert` 语句时，"insertmanyvalues" 功能可能会选择使用 **非批处理模式**。

    在此模式下，保持原始 SQL INSERT 形式不变，并且 "insertmanyvalues" 功能将为每个参数集单独运行语句，按顺序组织返回的行以形成完整的结果集。与以前的 SQLAlchemy 版本不同，它在一个紧密的循环中运行，最大限度地减少了 Python 开销。在某些情况下，例如在 SQLite 上，“非批处理”模式的性能与“批处理”模式一样好。

.. tab:: 英文

    For :class:`_schema.Table` configurations that do not have client side primary
    key values, and offer server-generated primary key values (or no primary key)
    that the database in question is not able to invoke in a deterministic or
    sortable way relative to multiple parameter sets, the "insertmanyvalues"
    feature when tasked with satisfying the
    :paramref:`_dml.Insert.returning.sort_by_parameter_order` requirement for an
    :class:`_dml.Insert` statement may instead opt to use **non-batched mode**.

    In this mode, the original SQL form of INSERT is maintained, and the
    "insertmanyvalues" feature will instead run the statement as given for each
    parameter set individually, organizing the returned rows into a full result
    set. Unlike previous SQLAlchemy versions, it does so in a tight loop that
    minimizes Python overhead. In some cases, such as on SQLite, "non-batched" mode
    performs exactly as well as "batched" mode.

语句执行模型
~~~~~~~~~~~~~~~~~~~~~~~~~

Statement Execution Model

.. tab:: 中文

    无论是“批处理”模式还是“非批处理”模式，该功能都必然会使用 **多个 INSERT 语句**，并通过 DBAPI 的 ``cursor.execute()`` 方法调用，在 **单次** 调用 :meth:`_engine.Connection.execute` 方法的范围内，每个语句包含最多固定数量的参数集。此限制可以通过 :ref:`engine_insertmanyvalues_page_size` 进行配置。单独的 ``cursor.execute()`` 调用会单独记录，并且也会单独传递给事件监听器，例如 :meth:`.ConnectionEvents.before_cursor_execute`（请参见 :ref:`engine_insertmanyvalues_events`）。

.. tab:: 英文

    For both "batched" and "non-batched" modes, the feature will necessarily
    invoke **multiple INSERT statements** using the DBAPI ``cursor.execute()`` method,
    within the scope of  **single** call to the Core-level
    :meth:`_engine.Connection.execute` method,
    with each statement containing up to a fixed limit of parameter sets.
    This limit is configurable as described below at :ref:`engine_insertmanyvalues_page_size`.
    The separate calls to ``cursor.execute()`` are logged individually and
    also individually passed along to event listeners such as
    :meth:`.ConnectionEvents.before_cursor_execute` (see :ref:`engine_insertmanyvalues_events`
    below).




.. _engine_insertmanyvalues_sentinel_columns:

配置 Sentinel 列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuring Sentinel Columns

.. tab:: 中文

    在典型情况下，“insertmanyvalues”功能为了提供具有确定行顺序的 INSERT..RETURNING，会自动从给定表的主键中确定一个哨兵列，如果无法识别，则优雅地降级为“逐行”模式。作为一个完全 **可选** 的功能，为了获得具有完整“insertmanyvalues”批量性能的表，如果表的服务器生成主键的默认生成函数与“哨兵”用例不兼容，其他非主键列可以被标记为“哨兵”列，前提是它们符合某些要求。一个典型的例子是使用客户端默认（如 Python ``uuid.uuid4()`` 函数）生成的新 UUID 非主键列。还有一种构造方法，可以创建简单的整数列，带有面向“insertmanyvalues”用例的客户端整数计数器。

    哨兵列可以通过将 :paramref:`_schema.Column.insert_sentinel` 添加到符合条件的列来指示。最基本的“符合条件”列是一个不可为空的、唯一的列，带有客户端默认值，如下面的 UUID 列：

        import uuid

        from sqlalchemy import Column
        from sqlalchemy import FetchedValue
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Uuid

        my_table = Table(
            "some_table",
            metadata,
            # 假设某个任意的服务器端函数生成
            # 主键值，因此无法通过批量插入进行跟踪
            Column("id", String(50), server_default=FetchedValue(), primary_key=True),
            Column("data", String(50)),
            Column(
                "uniqueid",
                Uuid(),
                default=uuid.uuid4,
                nullable=False,
                unique=True,
                insert_sentinel=True,
            ),
        )

    在使用 ORM 声明式模型时，同样的形式可通过 :class:`_orm.mapped_column` 构造函数实现：

        import uuid

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class MyClass(Base):
            __tablename__ = "my_table"

            id: Mapped[str] = mapped_column(primary_key=True, server_default=FetchedValue())
            data: Mapped[str] = mapped_column(String(50))
            uniqueid: Mapped[uuid.UUID] = mapped_column(
                default=uuid.uuid4, unique=True, insert_sentinel=True
            )

    由默认生成器生成的值 **必须** 是唯一的，然而，上述“哨兵”列上的实际 UNIQUE 约束（由 ``unique=True`` 参数指示）是可选的，如果不需要，可以省略。

    还有一种特殊形式的“insert sentinel”，它是一个专门的可空整数列，利用一个特殊的默认整数计数器，该计数器仅在“insertmanyvalues”操作期间使用；作为附加行为，该列将从 SQL 语句和结果集中省略，并以一种几乎透明的方式运行。然而，它确实需要物理存在于实际的数据库表中。可以使用函数 :func:`_schema.insert_sentinel` 构造这种类型的 :class:`_schema.Column`：

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Uuid
        from sqlalchemy import insert_sentinel

        Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", String(50)),
            insert_sentinel("sentinel"),
        )

    在使用 ORM 声明式时，也可以使用适用于声明式的 :func:`_schema.insert_sentinel` 版本，称为 :func:`_orm.orm_insert_sentinel`，它可以在 Base 类或 mixin 中使用；如果通过 :func:`_orm.declared_attr` 打包，该列将应用于所有绑定的子类，包括联合继承层次结构中的子类：

        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import orm_insert_sentinel


        class Base(DeclarativeBase):
            @declared_attr
            def _sentinel(cls) -> Mapped[int]:
                return orm_insert_sentinel()


        class MyClass(Base):
            __tablename__ = "my_table"

            id: Mapped[str] = mapped_column(primary_key=True, server_default=FetchedValue())
            data: Mapped[str] = mapped_column(String(50))


        class MySubClass(MyClass):
            __tablename__ = "sub_table"

            id: Mapped[str] = mapped_column(ForeignKey("my_table.id"), primary_key=True)


        class MySingleInhClass(MyClass):
            pass

    在上面的例子中，“my_table”和“sub_table”都会有一个额外的整数列，名为“_sentinel”，该列可以被“insertmanyvalues”功能使用，以帮助优化 ORM 使用的批量插入。

.. tab:: 英文

    In typical cases, the "insertmanyvalues" feature in order to provide
    INSERT..RETURNING with deterministic row order will automatically determine a
    sentinel column from a given table's primary key, gracefully degrading to "row
    at a time" mode if one cannot be identified. As a completely **optional**
    feature, to get full "insertmanyvalues" bulk performance for tables that have
    server generated primary keys whose default generator functions aren't
    compatible with the "sentinel" use case, other non-primary key columns may be
    marked as "sentinel" columns assuming they meet certain requirements. A typical
    example is a non-primary key :class:`_sqltypes.Uuid` column with a client side
    default such as the Python ``uuid.uuid4()`` function.  There is also a construct to create
    simple integer columns with a a client side integer counter oriented towards
    the "insertmanyvalues" use case.

    Sentinel columns may be indicated by adding :paramref:`_schema.Column.insert_sentinel`
    to qualifying columns.   The most basic "qualifying" column is a not-nullable,
    unique column with a client side default, such as a UUID column as follows::

        import uuid

        from sqlalchemy import Column
        from sqlalchemy import FetchedValue
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Uuid

        my_table = Table(
            "some_table",
            metadata,
            # assume some arbitrary server-side function generates
            # primary key values, so cannot be tracked by a bulk insert
            Column("id", String(50), server_default=FetchedValue(), primary_key=True),
            Column("data", String(50)),
            Column(
                "uniqueid",
                Uuid(),
                default=uuid.uuid4,
                nullable=False,
                unique=True,
                insert_sentinel=True,
            ),
        )

    When using ORM Declarative models, the same forms are available using
    the :class:`_orm.mapped_column` construct::

        import uuid

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class MyClass(Base):
            __tablename__ = "my_table"

            id: Mapped[str] = mapped_column(primary_key=True, server_default=FetchedValue())
            data: Mapped[str] = mapped_column(String(50))
            uniqueid: Mapped[uuid.UUID] = mapped_column(
                default=uuid.uuid4, unique=True, insert_sentinel=True
            )

    While the values generated by the default generator **must** be unique, the
    actual UNIQUE constraint on the above "sentinel" column, indicated by the
    ``unique=True`` parameter, itself is optional and may be omitted if not
    desired.

    There is also a special form of "insert sentinel" that's a dedicated nullable
    integer column which makes use of a special default integer counter that's only
    used during "insertmanyvalues" operations; as an additional behavior, the
    column will omit itself from SQL statements and result sets and behave in a
    mostly transparent manner.  It does need to be physically present within
    the actual database table, however.  This style of :class:`_schema.Column`
    may be constructed using the function :func:`_schema.insert_sentinel`::

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Uuid
        from sqlalchemy import insert_sentinel

        Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", String(50)),
            insert_sentinel("sentinel"),
        )

    When using ORM Declarative, a Declarative-friendly version of
    :func:`_schema.insert_sentinel` is available called
    :func:`_orm.orm_insert_sentinel`, which has the ability to be used on the Base
    class or a mixin; if packaged using :func:`_orm.declared_attr`, the column will
    apply itself to all table-bound subclasses including within joined inheritance
    hierarchies::


        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import orm_insert_sentinel


        class Base(DeclarativeBase):
            @declared_attr
            def _sentinel(cls) -> Mapped[int]:
                return orm_insert_sentinel()


        class MyClass(Base):
            __tablename__ = "my_table"

            id: Mapped[str] = mapped_column(primary_key=True, server_default=FetchedValue())
            data: Mapped[str] = mapped_column(String(50))


        class MySubClass(MyClass):
            __tablename__ = "sub_table"

            id: Mapped[str] = mapped_column(ForeignKey("my_table.id"), primary_key=True)


        class MySingleInhClass(MyClass):
            pass

    In the example above, both "my_table" and "sub_table" will have an additional
    integer column named "_sentinel" that can be used by the "insertmanyvalues"
    feature to help optimize bulk inserts used by the ORM.


.. _engine_insertmanyvalues_page_size:

控制批处理大小
~~~~~~~~~~~~~~~~~~~~~~~~~~

Controlling the Batch Size

.. tab:: 中文

    “insertmanyvalues”的一个关键特性是，INSERT 语句的大小受限于固定的最大“values”子句数量，以及每次 INSERT 语句中可表示的固定参数总数。当前参数字典的数量超过固定限制时，或者当单个 INSERT 语句中渲染的总参数数量超过固定限制时（这两个限制是分开的），将会在单个 :meth:`_engine.Connection.execute` 调用的范围内调用多个 INSERT 语句，每个 INSERT 语句处理一部分参数字典，称为“批次”。每个“批次”中表示的参数字典数量被称为“批次大小”。例如，批次大小为 500，意味着每个发出的 INSERT 语句最多插入 500 行。

    能够调整批次大小可能很重要，因为较大的批次大小可能对一个值集相对较小的 INSERT 操作表现得更好，而较小的批次大小可能对包含非常大值集的 INSERT 操作更合适，在这种情况下，渲染的 SQL 大小以及通过一个语句传递的总数据大小可能会受益于基于后端行为和内存限制的大小限制。因此，批次大小可以在每个 :class:`.Engine` 以及每个语句的基础上进行配置。另一方面，参数限制是基于正在使用的数据库的已知特性而固定的。

    对于大多数后端，批次大小默认为 1000，并且有一个每个方言的“最大参数数量”限制因素，这可能会在每个语句的基础上进一步减少批次大小。最大参数数量因方言和服务器版本而异；最大值为 32700（选择这个值是因为它远离 PostgreSQL 的 32767 限制和 SQLite 的现代 32766 限制，同时为语句中的额外参数以及 DBAPI 的特殊行为留出空间）。旧版本的 SQLite（3.32.0 之前）将此值设置为 999。MariaDB 没有明确的限制，但 32700 仍然是 SQL 消息大小的限制因素。

    “批次大小”的值可以通过 :class:`_engine.Engine` 在全局范围内通过 :paramref:`_sa.create_engine.insertmanyvalues_page_size` 参数进行调整。例如，要影响 INSERT 语句，使每个语句包含最多 100 个参数集：

        e = create_engine("sqlite://", insertmanyvalues_page_size=100)

    批次大小也可以在每个语句的基础上使用 :paramref:`_engine.Connection.execution_options.insertmanyvalues_page_size` 执行选项进行调整，如每次执行：

        with e.begin() as conn:
            result = conn.execute(
                table.insert().returning(table.c.id),
                parameterlist,
                execution_options={"insertmanyvalues_page_size": 100},
            )

    或者在语句本身进行配置：

        stmt = (
            table.insert()
            .returning(table.c.id)
            .execution_options(insertmanyvalues_page_size=100)
        )
        with e.begin() as conn:
            result = conn.execute(stmt, parameterlist)


.. tab:: 英文

    A key characteristic of "insertmanyvalues" is that the size of the INSERT
    statement is limited on a fixed max number of "values" clauses as well as a
    dialect-specific fixed total number of bound parameters that may be represented
    in one INSERT statement at a time. When the number of parameter dictionaries
    given exceeds a fixed limit, or when the total number of bound parameters to be
    rendered in a single INSERT statement exceeds a fixed limit (the two fixed
    limits are separate), multiple INSERT statements will be invoked within the
    scope of a single :meth:`_engine.Connection.execute` call, each of which
    accommodate for a portion of the parameter dictionaries, known as a
    "batch".  The number of parameter dictionaries represented within each
    "batch" is then known as the "batch size".  For example, a batch size of
    500 means that each INSERT statement emitted will INSERT at most 500 rows.

    It's potentially important to be able to adjust the batch size,
    as a larger batch size may be more performant for an INSERT where the value
    sets themselves are relatively small, and a smaller batch size may be more
    appropriate for an INSERT that uses very large value sets, where both the size
    of the rendered SQL as well as the total data size being passed in one
    statement may benefit from being limited to a certain size based on backend
    behavior and memory constraints.  For this reason the batch size
    can be configured on a per-:class:`.Engine` as well as a per-statement
    basis.   The parameter limit on the other hand is fixed based on the known
    characteristics of the database in use.

    The batch size defaults to 1000 for most backends, with an additional
    per-dialect "max number of parameters" limiting factor that may reduce the
    batch size further on a per-statement basis. The max number of parameters
    varies by dialect and server version; the largest size is 32700 (chosen as a
    healthy distance away from PostgreSQL's limit of 32767 and SQLite's modern
    limit of 32766, while leaving room for additional parameters in the statement
    as well as for DBAPI quirkiness). Older versions of SQLite (prior to 3.32.0)
    will set this value to 999. MariaDB has no established limit however 32700
    remains as a limiting factor for SQL message size.

    The value of the "batch size" can be affected :class:`_engine.Engine`
    wide via the :paramref:`_sa.create_engine.insertmanyvalues_page_size` parameter.
    Such as, to affect INSERT statements to include up to 100 parameter sets
    in each statement::

        e = create_engine("sqlite://", insertmanyvalues_page_size=100)

    The batch size may also be affected on a per statement basis using the
    :paramref:`_engine.Connection.execution_options.insertmanyvalues_page_size`
    execution option, such as per execution::

        with e.begin() as conn:
            result = conn.execute(
                table.insert().returning(table.c.id),
                parameterlist,
                execution_options={"insertmanyvalues_page_size": 100},
            )

    Or configured on the statement itself::

        stmt = (
            table.insert()
            .returning(table.c.id)
            .execution_options(insertmanyvalues_page_size=100)
        )
        with e.begin() as conn:
            result = conn.execute(stmt, parameterlist)

.. _engine_insertmanyvalues_events:

日志记录和事件
~~~~~~~~~~~~~~~~~~

Logging and Events

.. tab:: 中文

    “insertmanyvalues” 特性与 SQLAlchemy 的 :ref:`statement logging <dbengine_logging>` 和游标事件（如 :meth:`.ConnectionEvents.before_cursor_execute`）完全集成。当参数列表被分解为单独的批次时， **每个 INSERT 语句都会单独记录并传递给事件处理程序**。这与 SQLAlchemy 1.x 系列中仅适用于 psycopg2 的特性有所不同，在之前的版本中，多次 INSERT 语句的生成是隐藏在日志和事件中的。日志显示将截断较长的参数列表以提高可读性，并会指明每个语句的批次。下面的示例展示了日志记录的一部分：
    
    .. sourcecode:: text
    
        INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
        [generated in 0.00177s (insertmanyvalues) 1/10 (unordered)] ('d0', 0, 0, 'd1',  ...
        INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
        [insertmanyvalues 2/10 (unordered)] ('d100', 100, 1000, 'd101', ...

        ...

        INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
        [insertmanyvalues 10/10 (unordered)] ('d900', 900, 9000, 'd901', ...
    
    当发生 :ref:`非批处理模式 <engine_insertmanyvalues_non_batch>` 时，日志会显示这一点，并附带 insertmanyvalues 消息：
    
    .. sourcecode:: text
    
        ...
        
        INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
        [insertmanyvalues 67/78 (ordered; batch not supported)] ('d66', 66, 66)
        INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
        [insertmanyvalues 68/78 (ordered; batch not supported)] ('d67', 67, 67)
        INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
        [insertmanyvalues 69/78 (ordered; batch not supported)] ('d68', 68, 68)
        INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
        [insertmanyvalues 70/78 (ordered; batch not supported)] ('d69', 69, 69)
        
        ...
    
    .. seealso::
    
        :ref:`dbengine_logging`

.. tab:: 英文

    The "insertmanyvalues" feature integrates fully with SQLAlchemy's :ref:`statement
    logging <dbengine_logging>` as well as cursor events such as :meth:`.ConnectionEvents.before_cursor_execute`.
    When the list of parameters is broken into separate batches, **each INSERT
    statement is logged and passed to event handlers individually**.   This is a major change
    compared to how the psycopg2-only feature worked in previous 1.x series of
    SQLAlchemy, where the production of multiple INSERT statements was hidden from
    logging and events.  Logging display will truncate the long lists of parameters for readability,
    and will also indicate the specific batch of each statement. The example below illustrates
    an excerpt of this logging:
    
    .. sourcecode:: text
    
      INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
      [generated in 0.00177s (insertmanyvalues) 1/10 (unordered)] ('d0', 0, 0, 'd1',  ...
      INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
      [insertmanyvalues 2/10 (unordered)] ('d100', 100, 1000, 'd101', ...
    
      ...
    
      INSERT INTO a (data, x, y) VALUES (?, ?, ?), ... 795 characters truncated ...  (?, ?, ?), (?, ?, ?) RETURNING id
      [insertmanyvalues 10/10 (unordered)] ('d900', 900, 9000, 'd901', ...
    
    When :ref:`non-batch mode <engine_insertmanyvalues_non_batch>` takes place, logging
    will indicate this along with the insertmanyvalues message:
    
    .. sourcecode:: text
    
      ...
    
      INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
      [insertmanyvalues 67/78 (ordered; batch not supported)] ('d66', 66, 66)
      INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
      [insertmanyvalues 68/78 (ordered; batch not supported)] ('d67', 67, 67)
      INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
      [insertmanyvalues 69/78 (ordered; batch not supported)] ('d68', 68, 68)
      INSERT INTO a (data, x, y) VALUES (?, ?, ?) RETURNING id
      [insertmanyvalues 70/78 (ordered; batch not supported)] ('d69', 69, 69)
    
      ...
    
    .. seealso::
    
        :ref:`dbengine_logging`

Upsert 支持
~~~~~~~~~~~~~~

Upsert Support

.. tab:: 中文

    PostgreSQL、SQLite 和 MariaDB 方言提供了后端特定的 "upsert" 构造，如 :func:`_postgresql.insert`、:func:`_sqlite.insert` 和 :func:`_mysql.insert`，这些构造是具有额外方法（例如 ``on_conflict_do_update()`` 或 ``on_duplicate_key()``）的 :class:`_dml.Insert` 构造。当这些构造与 RETURNING 一起使用时，它们也支持 "insertmanyvalues" 行为，从而使高效的 upsert 操作得以进行。

.. tab:: 英文

    The PostgreSQL, SQLite, and MariaDB dialects offer backend-specific
    "upsert" constructs :func:`_postgresql.insert`, :func:`_sqlite.insert`
    and :func:`_mysql.insert`, which are each :class:`_dml.Insert` constructs that
    have an additional method such as ``on_conflict_do_update()` or
    ``on_duplicate_key()``.   These constructs also support "insertmanyvalues"
    behaviors when they are used with RETURNING, allowing efficient upserts
    with RETURNING to take place.


.. _engine_disposal:

引擎处置
---------------

Engine Disposal

.. tab:: 中文

    :class:`_engine.Engine` 是一个连接池，这意味着在正常情况下，只要 :class:`_engine.Engine` 对象仍然驻留在内存中，就会存在打开的数据库连接。当 :class:`_engine.Engine` 被垃圾回收时，它的连接池将不再被引用，假设它的连接没有被借出，则连接池和连接也会被垃圾回收，最终关闭实际的数据库连接。然而，在其他情况下，:class:`_engine.Engine` 将保留打开的数据库连接，假设它使用的是默认的 :class:`.QueuePool` 连接池实现。

    :class:`_engine.Engine` 通常应作为一个永久的组件，在应用程序的生命周期内建立并保持。它 **不** 应按连接基础创建和销毁；而应作为一个注册表，维护一个连接池以及数据库和 DBAPI 使用的配置信息，并且还会有一定程度的数据库资源的内部缓存。

    但是，在许多情况下，完全关闭所有由 :class:`_engine.Engine` 引用的连接资源是很有必要的。在这些情况下，通常不建议依赖 Python 的垃圾回收来完成此操作；而是应该显式调用 :meth:`_engine.Engine.dispose` 方法来释放连接池，并用一个新的空池替换它。如果此时丢弃 :class:`_engine.Engine` 并且不再使用它，那么它引用的所有 **已检查入** 的连接也会被完全关闭。

    调用 :meth:`_engine.Engine.dispose` 的有效使用案例包括：

    * 当程序希望释放连接池中仍持有的连接，并且期望不再连接到该数据库。
    * 当程序使用多处理或 ``fork()`` 时，且 :class:`_engine.Engine` 对象被复制到子进程中，应调用 :meth:`_engine.Engine.dispose`，以便引擎为该 fork 创建新的本地数据库连接。
    * 在测试套件或多租户场景中，可能会创建和销毁许多临时的、短生命周期的 :class:`_engine.Engine` 对象。

    当连接处于 **借出** 状态时，它们不会在引擎被丢弃或垃圾回收时被丢弃，因为这些连接在应用程序的其他地方仍然有强引用。然而，在调用 :meth:`_engine.Engine.dispose` 后，这些连接将不再与 :class:`_engine.Engine` 相关联；当它们关闭时，它们将返回到它们现在成为孤立的连接池中，最终被垃圾回收。由于这个过程难以控制，强烈建议仅在所有借出连接已检查入或被移除池后调用 :meth:`_engine.Engine.dispose`。

    如果应用程序对 :class:`_engine.Engine` 使用连接池的方式受到负面影响，可以选择完全禁用连接池。这样做通常只会对使用新连接的性能产生适度影响，并且每次检查入连接时都会完全关闭，而不会在内存中保持。有关如何禁用连接池的更多指导，请参见 :ref:`pool_switching`。 

    .. seealso::

        :ref:`pooling_toplevel`

        :ref:`pooling_multiprocessing`

.. tab:: 英文

    The :class:`_engine.Engine` refers to a connection pool, which means under normal
    circumstances, there are open database connections present while the
    :class:`_engine.Engine` object is still resident in memory.   When an :class:`_engine.Engine`
    is garbage collected, its connection pool is no longer referred to by
    that :class:`_engine.Engine`, and assuming none of its connections are still checked
    out, the pool and its connections will also be garbage collected, which has the
    effect of closing out the actual database connections as well.   But otherwise,
    the :class:`_engine.Engine` will hold onto open database connections assuming
    it uses the normally default pool implementation of :class:`.QueuePool`.
    
    The :class:`_engine.Engine` is intended to normally be a permanent
    fixture established up-front and maintained throughout the lifespan of an
    application.  It is **not** intended to be created and disposed on a
    per-connection basis; it is instead a registry that maintains both a pool
    of connections as well as configurational information about the database
    and DBAPI in use, as well as some degree of internal caching of per-database
    resources.
    
    However, there are many cases where it is desirable that all connection resources
    referred to by the :class:`_engine.Engine` be completely closed out.  It's
    generally not a good idea to rely on Python garbage collection for this
    to occur for these cases; instead, the :class:`_engine.Engine` can be explicitly disposed using
    the :meth:`_engine.Engine.dispose` method.   This disposes of the engine's
    underlying connection pool and replaces it with a new one that's empty.
    Provided that the :class:`_engine.Engine`
    is discarded at this point and no longer used, all **checked-in** connections
    which it refers to will also be fully closed.
    
    Valid use cases for calling :meth:`_engine.Engine.dispose` include:
    
    * When a program wants to release any remaining checked-in connections
      held by the connection pool and expects to no longer be connected
      to that database at all for any future operations.
    
    * When a program uses multiprocessing or ``fork()``, and an
      :class:`_engine.Engine` object is copied to the child process,
      :meth:`_engine.Engine.dispose` should be called so that the engine creates
      brand new database connections local to that fork.   Database connections
      generally do **not** travel across process boundaries.  Use the
      :paramref:`.Engine.dispose.close` parameter set to False in this case.
      See the section :ref:`pooling_multiprocessing` for more background on this
      use case.
    
    * Within test suites or multitenancy scenarios where many
      ad-hoc, short-lived :class:`_engine.Engine` objects may be created and disposed.
    
    
    Connections that are **checked out** are **not** discarded when the
    engine is disposed or garbage collected, as these connections are still
    strongly referenced elsewhere by the application.
    However, after :meth:`_engine.Engine.dispose` is called, those
    connections are no longer associated with that :class:`_engine.Engine`; when they
    are closed, they will be returned to their now-orphaned connection pool
    which will ultimately be garbage collected, once all connections which refer
    to it are also no longer referenced anywhere.
    Since this process is not easy to control, it is strongly recommended that
    :meth:`_engine.Engine.dispose` is called only after all checked out connections
    are checked in or otherwise de-associated from their pool.
    
    An alternative for applications that are negatively impacted by the
    :class:`_engine.Engine` object's use of connection pooling is to disable pooling
    entirely.  This typically incurs only a modest performance impact upon the
    use of new connections, and means that when a connection is checked in,
    it is entirely closed out and is not held in memory.  See :ref:`pool_switching`
    for guidelines on how to disable pooling.
    
    .. seealso::
    
        :ref:`pooling_toplevel`
    
        :ref:`pooling_multiprocessing`

.. _dbapi_connections:

使用驱动程序 SQL 和原始 DBAPI 连接
-------------------------------------------------

Working with Driver SQL and Raw DBAPI Connections

.. tab:: 中文

    在使用 :meth:`_engine.Connection.execute` 的介绍中，使用了 :func:`_expression.text` 构造来演示如何调用文本 SQL 语句。在使用 SQLAlchemy 时，文本 SQL 实际上更像是例外，而不是常规，因为 Core 表达式语言和 ORM 都抽象了 SQL 的文本表示。然而， :func:`_expression.text` 构造本身也提供了一些文本 SQL 的抽象，因为它规范化了绑定参数的传递方式，并且支持参数和结果集行的数据类型行为。

.. tab:: 英文

    The introduction on using :meth:`_engine.Connection.execute` made use of the
    :func:`_expression.text` construct in order to illustrate how textual SQL statements
    may be invoked.  When working with SQLAlchemy, textual SQL is actually more
    of the exception rather than the norm, as the Core expression language
    and the ORM both abstract away the textual representation of SQL.  However, the
    :func:`_expression.text` construct itself also provides some abstraction of textual
    SQL in that it normalizes how bound parameters are passed, as well as that
    it supports datatyping behavior for parameters and result set rows.

直接向驱动程序调用 SQL 字符串
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Invoking SQL strings directly to the driver

.. tab:: 中文

    对于那些希望直接调用传递给底层驱动程序（即 :term:`DBAPI`）的文本 SQL 而不经过 :func:`_expression.text` 构造干预的用例，可以使用 :meth:`_engine.Connection.exec_driver_sql` 方法::

        with engine.connect() as conn:
            conn.exec_driver_sql("SET param='bar'")

    .. versionadded:: 1.4  增加了 :meth:`_engine.Connection.exec_driver_sql` 方法。

.. tab:: 英文

    For the use case where one wants to invoke textual SQL directly passed to the
    underlying driver (known as the :term:`DBAPI`) without any intervention
    from the :func:`_expression.text` construct, the :meth:`_engine.Connection.exec_driver_sql`
    method may be used::

        with engine.connect() as conn:
            conn.exec_driver_sql("SET param='bar'")

    .. versionadded:: 1.4  Added the :meth:`_engine.Connection.exec_driver_sql` method.

.. _dbapi_connections_cursor:

直接使用 DBAPI 游标
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Working with the DBAPI cursor directly

.. tab:: 中文

    在一些情况下，SQLAlchemy 并未提供一种通用的方式来访问某些 :term:`DBAPI` 函数，例如调用存储过程以及处理多个结果集。在这些情况下，直接使用原始 DBAPI 连接会更加高效。

    访问原始 DBAPI 连接最常见的方式是直接从已经存在的 :class:`_engine.Connection` 对象获取。可以使用 :attr:`_engine.Connection.connection` 属性来访问::

        connection = engine.connect()
        dbapi_conn = connection.connection

    这里的 DBAPI 连接实际上是“代理”的，属于原始连接池的实现细节，不过在大多数情况下可以忽略不计。由于这个 DBAPI 连接仍然被包含在拥有的 :class:`_engine.Connection` 对象的作用域内，因此最好还是使用 :class:`_engine.Connection` 对象来执行大多数操作，比如事务控制以及调用 :meth:`_engine.Connection.close` 方法；如果直接对 DBAPI 连接执行这些操作，拥有的 :class:`_engine.Connection` 将不会意识到这些状态的变化。

    为了克服拥有的 :class:`_engine.Connection` 所维护的 DBAPI 连接的局限性，还可以通过 :meth:`_engine.Engine.raw_connection` 方法直接获取一个 DBAPI 连接，而无需先获取 :class:`_engine.Connection`::

        dbapi_conn = engine.raw_connection()

    这个 DBAPI 连接仍然是一个“代理”的形式，和之前一样。代理的目的现在变得明显，当我们调用该连接的 ``.close()`` 方法时，DBAPI 连接通常并不会真正关闭，而是被“释放”回引擎的连接池::

        dbapi_conn.close()

    虽然 SQLAlchemy 在未来可能会为更多的 DBAPI 用例添加内建的模式，但由于这些用例往往不常见，而且它们高度依赖于使用的 DBAPI 类型，因此直接的 DBAPI 调用模式始终可用于那些需要它的场景。

    .. seealso::

        :ref:`faq_dbapi_connection` - 包含有关如何访问 DBAPI 连接以及在使用 asyncio 驱动程序时如何访问“驱动”连接的更多详细信息。

    以下是一些 DBAPI 连接使用的示例。

.. tab:: 英文

    There are some cases where SQLAlchemy does not provide a genericized way
    at accessing some :term:`DBAPI` functions, such as calling stored procedures as well
    as dealing with multiple result sets.  In these cases, it's just as expedient
    to deal with the raw DBAPI connection directly.

    The most common way to access the raw DBAPI connection is to get it
    from an already present :class:`_engine.Connection` object directly.  It is
    present using the :attr:`_engine.Connection.connection` attribute::

        connection = engine.connect()
        dbapi_conn = connection.connection

    The DBAPI connection here is actually a "proxied" in terms of the
    originating connection pool, however this is an implementation detail
    that in most cases can be ignored.    As this DBAPI connection is still
    contained within the scope of an owning :class:`_engine.Connection` object, it is
    best to make use of the :class:`_engine.Connection` object for most features such
    as transaction control as well as calling the :meth:`_engine.Connection.close`
    method; if these operations are performed on the DBAPI connection directly,
    the owning :class:`_engine.Connection` will not be aware of these changes in state.

    To overcome the limitations imposed by the DBAPI connection that is
    maintained by an owning :class:`_engine.Connection`, a DBAPI connection is also
    available without the need to procure a
    :class:`_engine.Connection` first, using the :meth:`_engine.Engine.raw_connection` method
    of :class:`_engine.Engine`::

        dbapi_conn = engine.raw_connection()

    This DBAPI connection is again a "proxied" form as was the case before.
    The purpose of this proxying is now apparent, as when we call the ``.close()``
    method of this connection, the DBAPI connection is typically not actually
    closed, but instead :term:`released` back to the
    engine's connection pool::

        dbapi_conn.close()

    While SQLAlchemy may in the future add built-in patterns for more DBAPI
    use cases, there are diminishing returns as these cases tend to be rarely
    needed and they also vary highly dependent on the type of DBAPI in use,
    so in any case the direct DBAPI calling pattern is always there for those
    cases where it is needed.

    .. seealso::

        :ref:`faq_dbapi_connection` - includes additional details about how
        the DBAPI connection is accessed as well as the "driver" connection
        when using asyncio drivers.

    Some recipes for DBAPI connection use follow.

.. _stored_procedures:

调用存储过程和用户​​定义函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Calling Stored Procedures and User Defined Functions

.. tab:: 中文
    
    SQLAlchemy 支持多种方式调用存储过程和用户定义函数。请注意，不同的 DBAPI 具有不同的实践，因此必须查阅底层 DBAPI 的文档，以了解与特定用法相关的细节。以下示例是假设的，可能不适用于您的底层 DBAPI。
    
    对于具有特殊语法或参数要求的存储过程或函数，可以使用 DBAPI 级别的 `callproc <https://legacy.python.org/dev/peps/pep-0249/#callproc>`_ 来调用您的 DBAPI。以下是这种模式的示例：
    
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("my_procedure", ["x", "y", "z"])
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
    
    .. note::
    
      并非所有 DBAPI 都使用 `callproc`，整体使用细节会有所不同。上面的示例仅仅是如何使用特定 DBAPI 函数的示例。
    
    您的 DBAPI 可能不需要 ``callproc`` *或者* 可能需要使用另一种模式来调用存储过程或用户定义函数，例如使用普通的 SQLAlchemy 连接。当前文档撰写时，一个示例是，使用 psycopg2 DBAPI 执行 PostgreSQL 数据库中的存储过程，应该使用普通连接调用：
    
        connection.execute("CALL my_procedure();")
    
    这个示例是假设的。底层数据库不一定支持这些情况下的 "CALL" 或 "SELECT"，并且关键字可能会根据函数是存储过程还是用户定义函数而有所不同。在这些情况下，您应查阅底层 DBAPI 和数据库文档，以确定正确的语法和使用模式。

.. tab:: 英文

    SQLAlchemy supports calling stored procedures and user defined functions
    several ways. Please note that all DBAPIs have different practices, so you must
    consult your underlying DBAPI's documentation for specifics in relation to your
    particular usage. The following examples are hypothetical and may not work with
    your underlying DBAPI.
    
    For stored procedures or functions with special syntactical or parameter concerns,
    DBAPI-level `callproc <https://legacy.python.org/dev/peps/pep-0249/#callproc>`_
    may potentially be used with your DBAPI. An example of this pattern is::
    
        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.callproc("my_procedure", ["x", "y", "z"])
            results = list(cursor_obj.fetchall())
            cursor_obj.close()
            connection.commit()
        finally:
            connection.close()
    
    .. note::
    
      Not all DBAPIs use `callproc` and overall usage details will vary. The above
      example is only an illustration of how it might look to use a particular DBAPI
      function.
    
    Your DBAPI may not have a ``callproc`` requirement *or* may require a stored
    procedure or user defined function to be invoked with another pattern, such as
    normal SQLAlchemy connection usage. One example of this usage pattern is,
    *at the time of this documentation's writing*, executing a stored procedure in
    the PostgreSQL database with the psycopg2 DBAPI, which should be invoked
    with normal connection usage::
    
        connection.execute("CALL my_procedure();")
    
    This above example is hypothetical. The underlying database is not guaranteed to
    support "CALL" or "SELECT" in these situations, and the keyword may vary
    dependent on the function being a stored procedure or a user defined function.
    You should consult your underlying DBAPI and database documentation in these
    situations to determine the correct syntax and patterns to use.


多个结果集
~~~~~~~~~~~~~~~~~~~~

Multiple Result Sets

.. tab:: 中文

    通过原始 DBAPI 游标可以支持多个结果集，使用 `nextset <https://legacy.python.org/dev/peps/pep-0249/#nextset>`_ 方法::

        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.execute("select * from table1; select * from table2")
            results_one = cursor_obj.fetchall()
            cursor_obj.nextset()
            results_two = cursor_obj.fetchall()
            cursor_obj.close()
        finally:
            connection.close()

.. tab:: 英文

    Multiple result set support is available from a raw DBAPI cursor using the
    `nextset <https://legacy.python.org/dev/peps/pep-0249/#nextset>`_ method::

        connection = engine.raw_connection()
        try:
            cursor_obj = connection.cursor()
            cursor_obj.execute("select * from table1; select * from table2")
            results_one = cursor_obj.fetchall()
            cursor_obj.nextset()
            results_two = cursor_obj.fetchall()
            cursor_obj.close()
        finally:
            connection.close()

注册新方言
------------------------

Registering New Dialects

.. tab:: 中文

    :meth:`_sa.create_engine` 函数调用通过 setuptools 条目定位给定的方言。这些条目可以通过 setup.py 脚本为第三方方言进行设置。例如，要创建一个新的方言 "foodialect://"，步骤如下：

    1. 创建一个名为 ``foodialect`` 的包。
    2. 该包应包含一个模块，该模块包含方言类，通常是 :class:`sqlalchemy.engine.default.DefaultDialect` 的子类。在本示例中，我们假设它叫做 ``FooDialect``，模块通过 ``foodialect.dialect`` 访问。
    3. 可以在 ``setup.cfg`` 中如下面所示建立条目：

    .. sourcecode:: ini

            [options.entry_points]
            sqlalchemy.dialects =
                foodialect = foodialect.dialect:FooDialect

    如果该方言在现有的 SQLAlchemy 支持的数据库上提供对特定 DBAPI 的支持，可以包括数据库限定名称。例如，如果 ``FooDialect`` 实际上是一个 MySQL 方言，则可以这样设置条目：

    .. sourcecode:: ini

        [options.entry_points]
        sqlalchemy.dialects
            mysql.foodialect = foodialect.dialect:FooDialect

    上述条目将通过 ``create_engine("mysql+foodialect://")`` 进行访问。

.. tab:: 英文

    The :func:`_sa.create_engine` function call locates the given dialect
    using setuptools entrypoints.   These entry points can be established
    for third party dialects within the setup.py script.  For example,
    to create a new dialect "foodialect://", the steps are as follows:
    
    1. Create a package called ``foodialect``.
    2. The package should have a module containing the dialect class,
       which is typically a subclass of :class:`sqlalchemy.engine.default.DefaultDialect`.
       In this example let's say it's called ``FooDialect`` and its module is accessed
       via ``foodialect.dialect``.
    3. The entry point can be established in ``setup.cfg`` as follows:
    
       .. sourcecode:: ini
    
              [options.entry_points]
              sqlalchemy.dialects =
                  foodialect = foodialect.dialect:FooDialect
    
    If the dialect is providing support for a particular DBAPI on top of
    an existing SQLAlchemy-supported database, the name can be given
    including a database-qualification.  For example, if ``FooDialect``
    were in fact a MySQL dialect, the entry point could be established like this:
    
    .. sourcecode:: ini
    
          [options.entry_points]
          sqlalchemy.dialects
              mysql.foodialect = foodialect.dialect:FooDialect
    
    The above entrypoint would then be accessed as ``create_engine("mysql+foodialect://")``.


在进程内注册方言
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Registering Dialects In-Process

.. tab:: 中文

    SQLAlchemy 还允许在当前进程中注册一个方言，从而跳过单独安装的步骤。可以使用 ``register()`` 函数，如下所示::

        from sqlalchemy.dialects import registry

        registry.register("mysql.foodialect", "myapp.dialect", "MyMySQLDialect")

    上述操作将响应 ``create_engine("mysql+foodialect://")`` 并加载来自 ``myapp.dialect`` 模块的 ``MyMySQLDialect`` 类。

.. tab:: 英文

    SQLAlchemy also allows a dialect to be registered within the current process, bypassing
    the need for separate installation.   Use the ``register()`` function as follows::

        from sqlalchemy.dialects import registry


        registry.register("mysql.foodialect", "myapp.dialect", "MyMySQLDialect")

    The above will respond to ``create_engine("mysql+foodialect://")`` and load the
    ``MyMySQLDialect`` class from the ``myapp.dialect`` module.


连接 / 引擎API
-----------------------

Connection / Engine API

.. autoclass:: Connection
   :members:

.. autoclass:: CreateEnginePlugin
   :members:

.. autoclass:: Engine
   :members:

.. autoclass:: ExceptionContext
   :members:

.. autoclass:: NestedTransaction
    :members:
    :inherited-members:

.. autoclass:: RootTransaction
    :members:
    :inherited-members:

.. autoclass:: Transaction
    :members:

.. autoclass:: TwoPhaseTransaction
    :members:
    :inherited-members:


结果集 API
---------------

Result Set API

.. autoclass:: ChunkedIteratorResult
    :members:

.. autoclass:: CursorResult
    :members:
    :inherited-members:

.. autoclass:: FilterResult
    :members:

.. autoclass:: FrozenResult
    :members:

.. autoclass:: IteratorResult
    :members:

.. autoclass:: MergedResult
    :members:

.. autoclass:: Result
    :members:
    :inherited-members:

.. autoclass:: ScalarResult
    :members:
    :inherited-members:

.. autoclass:: MappingResult
    :members:
    :inherited-members:

.. autoclass:: Row
    :members:
    :private-members: _asdict, _fields, _mapping, _t, _tuple

.. autoclass:: RowMapping
    :members:

.. autoclass:: TupleResult
