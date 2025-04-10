.. _pooling_toplevel:

连接池
==================

Connection Pooling

.. module:: sqlalchemy.pool

.. tab:: 中文

    连接池是一种标准技术，用于在内存中维护长时间运行的连接以实现高效重用，并管理应用程序可能同时使用的总连接数。

    特别是对于服务器端Web应用程序，连接池是维护内存中活动数据库连接“池(pool)”的标准方法，这些连接在请求之间重用。

    SQLAlchemy包括几种连接池实现，它们与 :class:`_engine.Engine` 集成。它们也可以直接用于希望为普通DBAPI方法添加池化的应用程序。

.. tab:: 英文

    A connection pool is a standard technique used to maintain
    long running connections in memory for efficient re-use,
    as well as to provide
    management for the total number of connections an application
    might use simultaneously.

    Particularly for
    server-side web applications, a connection pool is the standard way to
    maintain a "pool" of active database connections in memory which are
    reused across requests.

    SQLAlchemy includes several connection pool implementations
    which integrate with the :class:`_engine.Engine`.  They can also be used
    directly for applications that want to add pooling to an otherwise
    plain DBAPI approach.

连接池配置
-----------------------------

Connection Pool Configuration

.. tab:: 中文

    :func:`~sqlalchemy.create_engine` 函数返回的 :class:`_engine.Engine` 在大多数情况下默认集成了 :class:`.QueuePool`，并且已经预先配置了合理的连接池默认值。如果你阅读本节只是为了了解如何启用连接池——恭喜你！你已经完成了。

    最常用的 :class:`.QueuePool` 调优参数可以作为关键字参数直接传递给 :func:`~sqlalchemy.create_engine`：包括 ``pool_size``、 ``max_overflow``、 ``pool_recycle`` 和 ``pool_timeout``。例如::

        engine = create_engine(
            "postgresql+psycopg2://me@localhost/mydb", pool_size=20, max_overflow=0
        )

    所有 SQLAlchemy 的连接池实现有一个共同点： **不会“预创建”连接** —— 所有实现都会在首次使用时才创建连接。在那一时刻，如果没有更多的并发连接请求，那么也不会创建更多的连接。因此，:func:`_sa.create_engine` 默认使用一个大小为 5 的 :class:`.QueuePool` 是完全可以接受的，而不需要考虑应用是否真的需要五个连接排队 —— 连接池只会在应用实际并发使用了五个连接时才增长到该大小，在这种情况下使用一个小型连接池是完全合理的默认行为。

    .. note:: 
        
        :class:`.QueuePool` **不兼容 asyncio**。
        当使用 :class:`_asyncio.create_async_engine` 创建 :class:`.AsyncEngine` 实例时，
        会使用 :class:`_pool.AsyncAdaptedQueuePool` 类，该类基于 asyncio 兼容的队列实现。

.. tab:: 英文

    The :class:`_engine.Engine` returned by the
    :func:`~sqlalchemy.create_engine` function in most cases has a :class:`.QueuePool`
    integrated, pre-configured with reasonable pooling defaults.  If
    you're reading this section only to learn how to enable pooling - congratulations!
    You're already done.

    The most common :class:`.QueuePool` tuning parameters can be passed
    directly to :func:`~sqlalchemy.create_engine` as keyword arguments:
    ``pool_size``, ``max_overflow``, ``pool_recycle`` and
    ``pool_timeout``.  For example::

        engine = create_engine(
            "postgresql+psycopg2://me@localhost/mydb", pool_size=20, max_overflow=0
        )

    All SQLAlchemy pool implementations have in common
    that none of them "pre create" connections - all implementations wait
    until first use before creating a connection.   At that point, if
    no additional concurrent checkout requests for more connections
    are made, no additional connections are created.   This is why it's perfectly
    fine for :func:`_sa.create_engine` to default to using a :class:`.QueuePool`
    of size five without regard to whether or not the application really needs five connections
    queued up - the pool would only grow to that size if the application
    actually used five connections concurrently, in which case the usage of a
    small pool is an entirely appropriate default behavior.

    .. note:: The :class:`.QueuePool` class is **not compatible with asyncio**.
        When using :class:`_asyncio.create_async_engine` to create an instance of
        :class:`.AsyncEngine`, the :class:`_pool.AsyncAdaptedQueuePool` class,
        which makes use of an asyncio-compatible queue implementation, is used
        instead.


.. _pool_switching:

切换池实现
------------------------------

Switching Pool Implementations

.. tab:: 中文

    使用 :func:`_sa.create_engine` 使用其他类型的连接池的常规方法是使用 ``poolclass`` 参数。该参数接受从 ``sqlalchemy.pool`` 模块导入的类，并自动处理构建连接池的细节。一个常见的用例是禁用连接池，可以通过使用 :class:`.NullPool` 实现来实现该目标::

        from sqlalchemy.pool import NullPool

        engine = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test", poolclass=NullPool
        )

.. tab:: 英文

    The usual way to use a different kind of pool with :func:`_sa.create_engine`
    is to use the ``poolclass`` argument.   This argument accepts a class
    imported from the ``sqlalchemy.pool`` module, and handles the details
    of building the pool for you.   A common use case here is when
    connection pooling is to be disabled, which can be achieved by using
    the :class:`.NullPool` implementation::

        from sqlalchemy.pool import NullPool

        engine = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test", poolclass=NullPool
        )

使用自定义连接函数
----------------------------------

Using a Custom Connection Function

.. tab:: 中文

    请参阅 :ref:`custom_dbapi_args` 部分，了解各种连接定制例程的概述。

.. tab:: 英文

    See the section :ref:`custom_dbapi_args` for a rundown of the various connection customization routines.



构建连接池
-------------------

Constructing a Pool

.. tab:: 中文

    要单独使用 :class:`_pool.Pool`，唯一必需的参数是 ``creator`` 函数，它作为第一个参数传入，其后可以附加其他选项::

        import sqlalchemy.pool as pool
        import psycopg2


        def getconn():
            c = psycopg2.connect(user="ed", host="127.0.0.1", dbname="test")
            return c


        mypool = pool.QueuePool(getconn, max_overflow=10, pool_size=5)

    然后可以使用 :meth:`_pool.Pool.connect` 方法从连接池中获取 DBAPI 连接。该方法返回一个 DBAPI 连接对象，但该对象被封装在一个透明代理中::

        # 获取连接
        conn = mypool.connect()

        # 使用连接
        cursor_obj = conn.cursor()
        cursor_obj.execute("select foo")

    该透明代理的目的是拦截 ``close()`` 调用，使其不会真正关闭 DBAPI 连接，而是将其归还给连接池::

        # “关闭”连接 —— 实际上是将其归还给连接池
        conn.close()

    当代理对象被垃圾回收时，它也会将其内部的 DBAPI 连接归还给连接池，但由于 Python 中垃圾回收的非确定性（尽管在 cPython 中通常是及时的），因此不推荐依赖此行为；特别是在 asyncio DBAPI 驱动下，这种用法是不受支持的。

.. tab:: 英文

    To use a :class:`_pool.Pool` by itself, the ``creator`` function is
    the only argument that's required and is passed first, followed
    by any additional options::

        import sqlalchemy.pool as pool
        import psycopg2


        def getconn():
            c = psycopg2.connect(user="ed", host="127.0.0.1", dbname="test")
            return c


        mypool = pool.QueuePool(getconn, max_overflow=10, pool_size=5)

    DBAPI connections can then be procured from the pool using the
    :meth:`_pool.Pool.connect` function. The return value of this method is a DBAPI
    connection that's contained within a transparent proxy::

        # get a connection
        conn = mypool.connect()

        # use it
        cursor_obj = conn.cursor()
        cursor_obj.execute("select foo")

    The purpose of the transparent proxy is to intercept the ``close()`` call,
    such that instead of the DBAPI connection being closed, it is returned to the
    pool::

        # "close" the connection.  Returns
        # it to the pool.
        conn.close()

    The proxy also returns its contained DBAPI connection to the pool when it is
    garbage collected, though it's not deterministic in Python that this occurs
    immediately (though it is typical with cPython). This usage is not recommended
    however and in particular is not supported with asyncio DBAPI drivers.

.. _pool_reset_on_return:

返回时重置
---------------

Reset On Return

.. tab:: 中文

    该连接池实现包含了“返回时重置”行为 —— 在连接归还到连接池时会调用 DBAPI 连接的 ``rollback()`` 方法。这是为了清除连接上的任何事务状态，不仅包括未提交的数据，还包括表和行级别的锁。对大多数 DBAPI 而言，调用 ``rollback()`` 的开销很小；如果当前并没有活动事务，该方法通常是空操作（no-op）。

.. tab:: 英文

    The pool includes "reset on return" behavior which will call the ``rollback()``
    method of the DBAPI connection when the connection is returned to the pool.
    This is so that any existing transactional state is removed from the
    connection, which includes not just uncommitted data but table and row locks as
    well. For most DBAPIs, the call to ``rollback()`` is inexpensive, and if the
    DBAPI has already completed a transaction, the method should be a no-op.


禁用非事务性连接的返回时重置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disabling Reset on Return for non-transactional connections

.. tab:: 中文

    在某些特定场景下，这种 ``rollback()`` 行为可能是不必要的，例如当连接被配置为
    :ref:`autocommit <dbapi_autocommit_understanding>` 模式，或所使用的数据库引擎（如 MySQL 的 MyISAM 引擎）本身不具备 ACID 能力时。这种情况下通常出于性能考虑，会禁用返回时的重置行为。可以通过设置 :class:`_pool.Pool` 的 :paramref:`_pool.Pool.reset_on_return` 参数来实现禁用，也可以通过 :func:`_sa.create_engine` 的 :paramref:`_sa.create_engine.pool_reset_on_return` 参数传入 ``None`` 值来设置。例如，结合 :paramref:`.create_engine.isolation_level` 参数设为 ``AUTOCOMMIT``::

        non_acid_engine = create_engine(
            "mysql://scott:tiger@host/db",
            pool_reset_on_return=None,
            isolation_level="AUTOCOMMIT",
        )

    上述 engine 在连接归还连接池时将不会执行 ROLLBACK；因为启用了 AUTOCOMMIT，驱动也不会执行 BEGIN 操作。

.. tab:: 英文

    For very specific cases where this ``rollback()`` is not useful, such as when
    using a connection that is configured for
    :ref:`autocommit <dbapi_autocommit_understanding>` or when using a database
    that has no ACID capabilities such as the MyISAM engine of MySQL, the
    reset-on-return behavior can be disabled, which is typically done for
    performance reasons. This can be affected by using the
    :paramref:`_pool.Pool.reset_on_return` parameter of :class:`_pool.Pool`, which
    is also available from :func:`_sa.create_engine` as
    :paramref:`_sa.create_engine.pool_reset_on_return`, passing a value of ``None``.
    This is illustrated in the example below, in conjunction with the
    :paramref:`.create_engine.isolation_level` parameter setting of
    ``AUTOCOMMIT``::

        non_acid_engine = create_engine(
            "mysql://scott:tiger@host/db",
            pool_reset_on_return=None,
            isolation_level="AUTOCOMMIT",
        )

    The above engine won't actually perform ROLLBACK when connections are returned
    to the pool; since AUTOCOMMIT is enabled, the driver will also not perform
    any BEGIN operation.


自定义返回时重置方案
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Custom Reset-on-Return Schemes

.. tab:: 中文

    仅仅使用 ``rollback()`` 进行“重置”对于某些用例来说可能还不够充分；特别是对于使用临时表的应用，可能希望连接归还时自动清除这些临时表。部分（但并非所有）后端数据库提供了“重置”这些连接作用域资源的机制，这可能是连接池重置行为中所期望的功能。其他资源如 prepared statement 句柄、服务器端语句缓存等也可能在连接归还后继续存在，这取决于具体情况是否合适。某些后端（同样，并非全部）也可能提供相关的状态重置机制。SQLAlchemy 提供的 dialect 中，有两个已知支持此类重置机制的包括：

    - Microsoft SQL Server：有一个非官方但广为人知的存储过程 ``sp_reset_connection``；
    - PostgreSQL：提供一组文档化良好的命令，如 ``DISCARD``、``RESET``、``DEALLOCATE`` 和 ``UNLISTEN``。

    .. note:: 下一段及其示例应与 `mssql/base.py` 示例保持一致

    下面的示例展示了如何使用 Microsoft SQL Server 的 ``sp_reset_connection`` 存储过程替换默认的“返回时重置”行为，通过 :meth:`.PoolEvents.reset` 事件钩子实现。我们将 :paramref:`_sa.create_engine.pool_reset_on_return` 设置为 ``None``，从而完全禁用默认行为，并由自定义方案取代。在实现中仍然调用了 ``.rollback()``，以确保 DBAPI 内部的提交/回滚状态与事务状态保持一致::

        from sqlalchemy import create_engine
        from sqlalchemy import event

        mssql_engine = create_engine(
            "mssql+pyodbc://scott:tiger^5HHH@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            # 禁用默认的“返回时重置”机制
            pool_reset_on_return=None,
        )


        @event.listens_for(mssql_engine, "reset")
        def _reset_mssql(dbapi_connection, connection_record, reset_state):
            if not reset_state.terminate_only:
                dbapi_connection.execute("{call sys.sp_reset_connection}")

            # 保证 DBAPI 自身状态的一致性
            dbapi_connection.rollback()

    .. versionchanged:: 2.0.0b3  
        为 :meth:`.PoolEvents.reset` 事件添加了更多状态参数，并确保该事件在所有“重置”场景中均被触发，使其成为自定义“重置”处理器的推荐位置。  
        之前依赖 :meth:`.PoolEvents.checkin` 的方案仍然可用。

    .. seealso::

        * :ref:`mssql_reset_on_return` - 位于 :ref:`mssql_toplevel` 文档中
        * :ref:`postgresql_reset_on_return` - 位于 :ref:`postgresql_toplevel` 文档中

.. tab:: 英文

    "reset on return" consisting of a single ``rollback()`` may not be sufficient
    for some use cases; in particular, applications which make use of temporary
    tables may wish for these tables to be automatically removed on connection
    checkin. Some (but notably not all) backends include features that can "reset"
    such tables within the scope of a database connection, which may be a desirable
    behavior for connection pool reset. Other server resources such as prepared
    statement handles and server-side statement caches may persist beyond the
    checkin process, which may or may not be desirable, depending on specifics.
    Again, some (but again not all) backends may provide for a means of resetting
    this state.  The two SQLAlchemy included dialects which are known to have
    such reset schemes include Microsoft SQL Server, where an undocumented but
    widely known stored procedure called ``sp_reset_connection`` is often used,
    and PostgreSQL, which has a well-documented series of commands including
    ``DISCARD`` ``RESET``, ``DEALLOCATE``, and ``UNLISTEN``.

    .. note: next paragraph + example should match mssql/base.py example

    The following example illustrates how to replace reset on return with the
    Microsoft SQL Server ``sp_reset_connection`` stored procedure, using the
    :meth:`.PoolEvents.reset` event hook. The
    :paramref:`_sa.create_engine.pool_reset_on_return` parameter is set to ``None``
    so that the custom scheme can replace the default behavior completely. The
    custom hook implementation calls ``.rollback()`` in any case, as it's usually
    important that the DBAPI's own tracking of commit/rollback will remain
    consistent with the state of the transaction::

        from sqlalchemy import create_engine
        from sqlalchemy import event

        mssql_engine = create_engine(
            "mssql+pyodbc://scott:tiger^5HHH@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            # disable default reset-on-return scheme
            pool_reset_on_return=None,
        )


        @event.listens_for(mssql_engine, "reset")
        def _reset_mssql(dbapi_connection, connection_record, reset_state):
            if not reset_state.terminate_only:
                dbapi_connection.execute("{call sys.sp_reset_connection}")

            # so that the DBAPI itself knows that the connection has been
            # reset
            dbapi_connection.rollback()

    .. versionchanged:: 2.0.0b3  Added additional state arguments to
        the :meth:`.PoolEvents.reset` event and additionally ensured the event
        is invoked for all "reset" occurrences, so that it's appropriate
        as a place for custom "reset" handlers.   Previous schemes which
        use the :meth:`.PoolEvents.checkin` handler remain usable as well.

    .. seealso::

        * :ref:`mssql_reset_on_return` - in the :ref:`mssql_toplevel` documentation
        * :ref:`postgresql_reset_on_return` in the :ref:`postgresql_toplevel` documentation




记录返回时重置事件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Logging reset-on-return events

.. tab:: 中文

    连接池事件（包括“返回时重置”）的日志记录可以通过将 ``sqlalchemy.pool`` 记录器的日志级别设置为 ``logging.DEBUG`` 来启用，或者在使用 :func:`_sa.create_engine` 时，将 :paramref:`_sa.create_engine.echo_pool` 参数设为 ``"debug"`` 来启用::

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("postgresql://scott:tiger@localhost/test", echo_pool="debug")

    上述连接池将在日志中显示详细信息，包括“返回时重置”行为::

        >>> c1 = engine.connect()
        DEBUG sqlalchemy.pool.impl.QueuePool Created new connection <connection object ...>
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> checked out from pool
        >>> c1.close()
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> being returned to pool
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> rollback-on-return

.. tab:: 英文

    Logging for pool events including reset on return can be set
    ``logging.DEBUG``
    log level along with the ``sqlalchemy.pool`` logger, or by setting
    :paramref:`_sa.create_engine.echo_pool` to ``"debug"`` when using
    :func:`_sa.create_engine`::

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("postgresql://scott:tiger@localhost/test", echo_pool="debug")

    The above pool will show verbose logging including reset on return::

        >>> c1 = engine.connect()
        DEBUG sqlalchemy.pool.impl.QueuePool Created new connection <connection object ...>
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> checked out from pool
        >>> c1.close()
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> being returned to pool
        DEBUG sqlalchemy.pool.impl.QueuePool Connection <connection object ...> rollback-on-return


池事件
-----------

Pool Events

.. tab:: 中文

    连接池支持一个事件接口，允许在首次连接、每次新建连接、以及连接的借出（checkout）与归还（checkin）时执行钩子操作。详见 :class:`_events.PoolEvents`。

.. tab:: 英文

    Connection pools support an event interface that allows hooks to execute
    upon first connect, upon each new connection, and upon checkout and
    checkin of connections.   See :class:`_events.PoolEvents` for details.

.. _pool_disconnects:

处理断开连接
------------------------

Dealing with Disconnects

.. tab:: 中文

    连接池具备刷新单个连接及其整体连接集的能力，能够将先前保留的连接标记为“无效（invalid）”。这种机制的一个常见用途是当数据库服务器重启导致所有已有连接失效时，允许连接池平稳恢复。对此有两种常见策略。

.. tab:: 英文

    The connection pool has the ability to refresh individual connections as well as
    its entire set of connections, setting the previously pooled connections as
    "invalid".   A common use case is allow the connection pool to gracefully recover
    when the database server has been restarted, and all previously established connections
    are no longer functional.   There are two approaches to this.

.. _pool_disconnects_pessimistic:

断开连接处理 - 悲观
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disconnect Handling - Pessimistic

.. tab:: 中文

    悲观策略（Pessimistic Approach）是在每次连接借出时执行一条测试语句，以验证数据库连接仍然有效。其实现依赖于具体的方言（dialect），可以使用 DBAPI 特定的 ping 方法，或执行一条简单的 SQL 语句（如 `"SELECT 1"`）来检测连接是否存活。

    这种方法在连接借出的过程中引入了少许额外开销，但它是最简单可靠的方法，能够有效防止由于过期连接导致的数据库错误。应用程序无需自行组织逻辑来处理连接池中借出的过期连接。

    可以通过 :paramref:`_pool.Pool.pre_ping` 参数启用借出时的连接测试功能，使用 :func:`_sa.create_engine` 时可通过 :paramref:`_sa.create_engine.pool_pre_ping` 参数设置::

        engine = create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)

    “预 ping”功能是基于每个方言实现的。如果方言支持 DBAPI 的“ping”方法，则会调用该方法；否则将发出等效于 “SELECT 1” 的 SQL 查询，并捕获错误以判断是否为“断开连接”的情况。如果判断出连接不可用，该连接将被立即回收，并且所有旧于当前时间的其他连接也将被标记为无效，这样它们下次被借出时也会被自动回收。

    如果在“预 ping”运行时数据库仍不可用，则初始连接会失败，并正常抛出连接失败的错误。在一种少见情况下，如果数据库能接受连接但无法响应“ping”，则“预 ping”最多重试三次，若仍失败，则抛出最后捕获的数据库错误。

    需要特别注意的是，“预 ping”方法 **无法处理在事务过程中或其他 SQL 操作中连接中断的情况** 。如果在事务执行过程中数据库变得不可用，则该事务将丢失，同时抛出数据库错误。尽管 :class:`_engine.Connection` 对象会检测到“断开连接”状态，并自动回收该连接并使整个连接池失效，但引发异常的具体操作将无法恢复，应用程序必须自行决定是否放弃该操作或重试整个事务。如果 engine 使用 DBAPI 级别的自动提交（autocommit）连接（详见 :ref:`dbapi_autocommit`），那么在操作中间可能会通过事件机制自动重新连接。有关示例请参阅 :ref:`faq_execute_retry`。

    对于那些通过执行 “SELECT 1” 并捕获错误来判断断连的方言，可以使用 :meth:`_events.DialectEvents.handle_error` 钩子扩展对新后端特定错误信息的处理能力。

.. tab:: 英文

    The pessimistic approach refers to emitting a test statement on the SQL
    connection at the start of each connection pool checkout, to test
    that the database connection is still viable.   The implementation is
    dialect-specific, and makes use of either a DBAPI-specific ping method,
    or by using a simple SQL statement like "SELECT 1", in order to test the
    connection for liveness.

    The approach adds a small bit of overhead to the connection checkout process,
    however is otherwise the most simple and reliable approach to completely
    eliminating database errors due to stale pooled connections.   The calling
    application does not need to be concerned about organizing operations
    to be able to recover from stale connections checked out from the pool.

    Pessimistic testing of connections upon checkout is achievable by
    using the :paramref:`_pool.Pool.pre_ping` argument, available from :func:`_sa.create_engine`
    via the :paramref:`_sa.create_engine.pool_pre_ping` argument::

        engine = create_engine("mysql+pymysql://user:pw@host/db", pool_pre_ping=True)

    The "pre ping" feature operates on a per-dialect basis either by invoking a
    DBAPI-specific "ping" method, or if not available will emit SQL equivalent to
    "SELECT 1", catching any errors and detecting the error as a "disconnect"
    situation. If the ping / error check determines that the connection is not
    usable, the connection will be immediately recycled, and all other pooled
    connections older than the current time are invalidated, so that the next time
    they are checked out, they will also be recycled before use.

    If the database is still not available when "pre ping" runs, then the initial
    connect will fail and the error for failure to connect will be propagated
    normally.  In the uncommon situation that the database is available for
    connections, but is not able to respond to a "ping", the "pre_ping" will try up
    to three times before giving up, propagating the database error last received.

    It is critical to note that the pre-ping approach **does not accommodate for
    connections dropped in the middle of transactions or other SQL operations**. If
    the database becomes unavailable while a transaction is in progress, the
    transaction will be lost and the database error will be raised.   While the
    :class:`_engine.Connection` object will detect a "disconnect" situation and
    recycle the connection as well as invalidate the rest of the connection pool
    when this condition occurs, the individual operation where the exception was
    raised will be lost, and it's up to the application to either abandon the
    operation, or retry the whole transaction again.  If the engine is
    configured using DBAPI-level autocommit connections, as described at
    :ref:`dbapi_autocommit`, a connection **may** be reconnected transparently
    mid-operation using events.  See the section :ref:`faq_execute_retry` for
    an example.

    For dialects that make use of "SELECT 1" and catch errors in order to detect
    disconnects, the disconnection test may be augmented for new backend-specific
    error messages using the :meth:`_events.DialectEvents.handle_error` hook.

.. _pool_disconnects_pessimistic_custom:

自定义/旧式悲观 Ping
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom / Legacy Pessimistic Ping

.. tab:: 中文

    在 :paramref:`_sa.create_engine.pool_pre_ping` 参数被添加之前，"预 ping" 策略历来是通过手动方式实现的，即使用 :meth:`_events.ConnectionEvents.engine_connect` 引擎事件。以下是该方式的常见示例，供参考使用，特别适用于已经采用此方案的应用程序，或需要自定义行为的场景::

        from sqlalchemy import exc
        from sqlalchemy import event
        from sqlalchemy import select

        some_engine = create_engine(...)

        @event.listens_for(some_engine, "engine_connect")
        def ping_connection(connection, branch):
            if branch:
                # 从 SQLAlchemy 2.0 开始，该参数始终为 False，
                # 但事件钩子仍然接受它。在 SQLAlchemy 1.x 中，应跳过“分支”连接。
                return

            try:
                # 执行一条 SELECT 1 查询。使用 core 的 select()
                # 可以确保无表的标量查询格式符合后端要求。
                connection.scalar(select(1))
            except exc.DBAPIError as err:
                # 捕获 SQLAlchemy 的 DBAPIError，它是 DBAPI 异常的包装器。
                # 该异常包含 .connection_invalidated 属性，用于标识是否为“断开连接”情况，
                # 判断依据是当前方言对原始异常的解析。
                if err.connection_invalidated:
                    # 再次执行相同的 SELECT 查询，连接将自我验证并建立新连接。
                    # 同时，该断连检测还会导致整个连接池失效，从而丢弃所有过期连接。
                    connection.scalar(select(1))
                else:
                    raise

    上述示例的优势在于，它利用了 SQLAlchemy 提供的机制来检测那些已知表示“断开连接”的 DBAPI 异常，同时结合 :class:`_engine.Engine` 对象在此类情况下自动使连接池失效，并允许当前的 :class:`_engine.Connection` 使用新的 DBAPI 连接重新验证的能力。

.. tab:: 英文

    Before :paramref:`_sa.create_engine.pool_pre_ping` was added, the "pre-ping"
    approach historically has been performed manually using
    the :meth:`_events.ConnectionEvents.engine_connect` engine event.
    The most common recipe for this is below, for reference
    purposes in case an application is already using such a recipe, or special
    behaviors are needed::

        from sqlalchemy import exc
        from sqlalchemy import event
        from sqlalchemy import select

        some_engine = create_engine(...)


        @event.listens_for(some_engine, "engine_connect")
        def ping_connection(connection, branch):
            if branch:
                # this parameter is always False as of SQLAlchemy 2.0,
                # but is still accepted by the event hook.  In 1.x versions
                # of SQLAlchemy, "branched" connections should be skipped.
                return

            try:
                # run a SELECT 1.   use a core select() so that
                # the SELECT of a scalar value without a table is
                # appropriately formatted for the backend
                connection.scalar(select(1))
            except exc.DBAPIError as err:
                # catch SQLAlchemy's DBAPIError, which is a wrapper
                # for the DBAPI's exception.  It includes a .connection_invalidated
                # attribute which specifies if this connection is a "disconnect"
                # condition, which is based on inspection of the original exception
                # by the dialect in use.
                if err.connection_invalidated:
                    # run the same SELECT again - the connection will re-validate
                    # itself and establish a new connection.  The disconnect detection
                    # here also causes the whole connection pool to be invalidated
                    # so that all stale connections are discarded.
                    connection.scalar(select(1))
                else:
                    raise

    The above recipe has the advantage that we are making use of SQLAlchemy's
    facilities for detecting those DBAPI exceptions that are known to indicate
    a "disconnect" situation, as well as the :class:`_engine.Engine` object's ability
    to correctly invalidate the current connection pool when this condition
    occurs and allowing the current :class:`_engine.Connection` to re-validate onto
    a new DBAPI connection.


断开连接处理 - 乐观
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disconnect Handling - Optimistic

.. tab:: 中文

    当未启用悲观处理机制，或数据库在连接使用过程中（例如事务中）被关闭或重启时，另一种处理过期/关闭连接的方式是让 SQLAlchemy 在异常发生时自动处理断连情况。此时，连接池中的所有连接都会被失效处理，即被视为过期，在下次借出时自动刷新。此行为依赖于 :class:`_pool.Pool` 与 :class:`_engine.Engine` 联合使用。:class:`_engine.Engine` 包含可检测断连事件并自动刷新连接池的逻辑。

    当 :class:`_engine.Connection` 尝试使用 DBAPI 连接并遇到表示“断连”的异常时，该连接将被标记为失效。此时 :class:`_engine.Connection` 会调用 :meth:`_pool.Pool.recreate` 方法，从而使所有未借出的连接失效，在下次借出时替换为新连接。以下示例展示了此流程::

        from sqlalchemy import create_engine, exc

        e = create_engine(...)
        c = e.connect()

        try:
            # 假设数据库已被重启。
            c.execute(text("SELECT * FROM table"))
            c.close()
        except exc.DBAPIError as e:
            # 抛出异常，连接被标记为失效。
            if e.connection_invalidated:
                print("Connection was invalidated!")

        # 在失效事件之后，下一次连接将使用新的连接池连接。
        c = e.connect()
        c.execute(text("SELECT * FROM table"))

    以上示例说明在检测到断连事件后无需额外干预，连接池将正常继续工作。但需要注意的是，对于每一个在断连事件发生时正在使用的连接，都会抛出一次数据库异常。在典型的使用 ORM Session 的 Web 应用中，这通常表现为某个请求返回 500 错误，而应用之后会继续正常运行。因此，该方法是“乐观”的，即假设数据库不会频繁重启。

.. tab:: 英文

    When pessimistic handling is not employed, as well as when the database is
    shutdown and/or restarted in the middle of a connection's period of use within
    a transaction, the other approach to dealing with stale / closed connections is
    to let SQLAlchemy handle disconnects as  they occur, at which point all
    connections in the pool are invalidated, meaning they are assumed to be
    stale and will be refreshed upon next checkout.  This behavior assumes the
    :class:`_pool.Pool` is used in conjunction with a :class:`_engine.Engine`.
    The :class:`_engine.Engine` has logic which can detect
    disconnection events and refresh the pool automatically.

    When the :class:`_engine.Connection` attempts to use a DBAPI connection, and an
    exception is raised that corresponds to a "disconnect" event, the connection
    is invalidated. The :class:`_engine.Connection` then calls the :meth:`_pool.Pool.recreate`
    method, effectively invalidating all connections not currently checked out so
    that they are replaced with new ones upon next checkout.  This flow is
    illustrated by the code example below::

        from sqlalchemy import create_engine, exc

        e = create_engine(...)
        c = e.connect()

        try:
            # suppose the database has been restarted.
            c.execute(text("SELECT * FROM table"))
            c.close()
        except exc.DBAPIError as e:
            # an exception is raised, Connection is invalidated.
            if e.connection_invalidated:
                print("Connection was invalidated!")

        # after the invalidate event, a new connection
        # starts with a new Pool
        c = e.connect()
        c.execute(text("SELECT * FROM table"))

    The above example illustrates that no special intervention is needed to
    refresh the pool, which continues normally after a disconnection event is
    detected.   However, one database exception is raised, per each connection
    that is in use while the database unavailability event occurred.
    In a typical web application using an ORM Session, the above condition would
    correspond to a single request failing with a 500 error, then the web application
    continuing normally beyond that.   Hence the approach is "optimistic" in that frequent
    database restarts are not anticipated.


.. _pool_setting_recycle:

设置池回收
~~~~~~~~~~~~~~~~~~~~

Setting Pool Recycle

.. tab:: 中文

    为增强“乐观”策略的健壮性，可以设置连接池的 recycle 参数。该参数用于避免使用已存在超过指定时长的连接，适用于如 MySQL 这类会在空闲一段时间后自动关闭连接的后端数据库::

        from sqlalchemy import create_engine

        e = create_engine("mysql+mysqldb://scott:tiger@localhost/test", pool_recycle=3600)

    如上所示，任何存在时间超过一小时的 DBAPI 连接在下一次借出时都会被自动标记为失效并替换。注意，该失效 **仅** 在借出时发生——不会影响当前已借出的连接。``pool_recycle`` 是 :class:`_pool.Pool` 的一个特性，与是否使用 :class:`_engine.Engine` 无关。

.. tab:: 英文

    An additional setting that can augment the "optimistic" approach is to set the
    pool recycle parameter.   This parameter prevents the pool from using a particular
    connection that has passed a certain age, and is appropriate for database backends
    such as MySQL that automatically close connections that have been stale after a particular
    period of time::

        from sqlalchemy import create_engine

        e = create_engine("mysql+mysqldb://scott:tiger@localhost/test", pool_recycle=3600)

    Above, any DBAPI connection that has been open for more than one hour will be invalidated and replaced,
    upon next checkout.   Note that the invalidation **only** occurs during checkout - not on
    any connections that are held in a checked out state.     ``pool_recycle`` is a function
    of the :class:`_pool.Pool` itself, independent of whether or not an :class:`_engine.Engine` is in use.


.. _pool_connection_invalidation:

更多关于失效的信息
^^^^^^^^^^^^^^^^^^^^

More on Invalidation

.. tab:: 中文

    :class:`_pool.Pool` 提供了“连接失效”机制，支持显式失效和自动失效两种方式，用于处理那些已无法继续使用的连接。

    “失效”指的是某个 DBAPI 连接将被从连接池中移除并丢弃。如果当前不确定连接是否已关闭，将调用其 ``.close()`` 方法；若此方法抛出异常，该异常会被记录，但整体操作仍将继续。

    在使用 :class:`_engine.Engine` 时，通常通过 :meth:`_engine.Connection.invalidate` 方法触发显式失效。其他可能触发失效的情况包括：

    * 当调用 ``connection.execute()`` 等方法时，发生如 :class:`.OperationalError` 的 DBAPI 异常，并被识别为“断开连接”情况。由于 Python DBAPI 并未标准化异常分类，SQLAlchemy 各个方言使用一个名为 ``is_disconnect()`` 的机制来检查异常对象的内容（包括错误信息字符串和错误码等）以判断连接是否已不可用。如是，将调用 :meth:`._ConnectionFairy.invalidate` 方法并丢弃连接。

    * 当连接归还到连接池，在执行 ``connection.rollback()`` 或 ``connection.commit()`` 方法（依据连接池“返回时重置”策略）时抛出异常。此时会最后尝试执行 ``.close()``，之后丢弃连接。

    * 当某个实现了 :meth:`_events.PoolEvents.checkout` 的事件监听器抛出 :class:`~sqlalchemy.exc.DisconnectionError` 异常，表示该连接不可用，需重新建立连接。

    所有失效事件都会触发 :meth:`_events.PoolEvents.invalidate` 事件。

.. tab:: 英文

    The :class:`_pool.Pool` provides "connection invalidation" services which allow
    both explicit invalidation of a connection as well as automatic invalidation
    in response to conditions that are determined to render a connection unusable.
    
    "Invalidation" means that a particular DBAPI connection is removed from the
    pool and discarded.  The ``.close()`` method is called on this connection
    if it is not clear that the connection itself might not be closed, however
    if this method fails, the exception is logged but the operation still proceeds.
    
    When using a :class:`_engine.Engine`, the :meth:`_engine.Connection.invalidate` method is
    the usual entrypoint to explicit invalidation.   Other conditions by which
    a DBAPI connection might be invalidated include:
    
    * a DBAPI exception such as :class:`.OperationalError`, raised when a
      method like ``connection.execute()`` is called, is detected as indicating
      a so-called "disconnect" condition.   As the Python DBAPI provides no
      standard system for determining the nature of an exception, all SQLAlchemy
      dialects include a system called ``is_disconnect()`` which will examine
      the contents of an exception object, including the string message and
      any potential error codes included with it, in order to determine if this
      exception indicates that the connection is no longer usable.  If this is the
      case, the :meth:`._ConnectionFairy.invalidate` method is called and the
      DBAPI connection is then discarded.
    
    * When the connection is returned to the pool, and
      calling the ``connection.rollback()`` or ``connection.commit()`` methods,
      as dictated by the pool's "reset on return" behavior, throws an exception.
      A final attempt at calling ``.close()`` on the connection will be made,
      and it is then discarded.
    
    * When a listener implementing :meth:`_events.PoolEvents.checkout` raises the
      :class:`~sqlalchemy.exc.DisconnectionError` exception, indicating that the connection
      won't be usable and a new connection attempt needs to be made.
    
    All invalidations which occur will invoke the :meth:`_events.PoolEvents.invalidate`
    event.

.. _pool_new_disconnect_codes:

支持断开连接场景的新数据库错误代码
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Supporting new database error codes for disconnect scenarios

.. tab:: 中文

以下是翻译后的 rst 文本，保留了原有的 rst 格式和 SQLAlchemy 技术风格：

---

    SQLAlchemy 的各个方言（dialect）都实现了一个名为 ``is_disconnect()`` 的例程，在遇到 DBAPI 异常时会调用该方法。该方法接收 DBAPI 异常对象作为参数，并通过方言特定的启发式方法来判断错误码是否表明数据库连接已被“断开”，或处于其他不可用状态，需要进行回收。此处使用的启发式方法可通过事件钩子 :meth:`_events.DialectEvents.handle_error` 进行定制，通常通过所属的 :class:`_engine.Engine` 对象来注册该事件钩子。使用此钩子时，所有发生的错误都会传入一个上下文对象 :class:`.ExceptionContext`。自定义事件钩子可以控制某个错误是否应被视为“断开”状态，以及该断开是否应导致整个连接池被失效。

    例如，为了让 Oracle 数据库驱动错误码 ``DPY-1001`` 和 ``DPY-4011`` 被识别为断开错误码，可以在创建引擎之后添加如下事件处理器::

        import re

        from sqlalchemy import create_engine

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "handle_error")
        def handle_exception(context: ExceptionContext) -> None:
            if not context.is_disconnect and re.match(
                r"^(?:DPY-1001|DPY-4011)", str(context.original_exception)
            ):
                context.is_disconnect = True

            return None

    上述错误处理函数将在所有 Oracle 数据库错误触发时被调用，包括当启用 :ref:`pool pre ping <pool_disconnects_pessimistic>` 功能时（此功能在 2.0 中引入）所捕获的错误。

    .. seealso::

        :meth:`_events.DialectEvents.handle_error`

.. tab:: 英文

    SQLAlchemy dialects each include a routine called ``is_disconnect()`` that is
    invoked whenever a DBAPI exception is encountered. The DBAPI exception object
    is passed to this method, where dialect-specific heuristics will then determine
    if the error code received indicates that the database connection has been
    "disconnected", or is in an otherwise unusable state which indicates it should
    be recycled. The heuristics applied here may be customized using the
    :meth:`_events.DialectEvents.handle_error` event hook, which is typically
    established via the owning :class:`_engine.Engine` object. Using this hook, all
    errors which occur are delivered passing along a contextual object known as
    :class:`.ExceptionContext`. Custom event hooks may control whether or not a
    particular error should be considered a "disconnect" situation or not, as well
    as if this disconnect should cause the entire connection pool to be invalidated
    or not.

    For example, to add support to consider the Oracle Database driver error codes
    ``DPY-1001`` and ``DPY-4011`` to be handled as disconnect codes, apply an event
    handler to the engine after creation::

        import re

        from sqlalchemy import create_engine

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "handle_error")
        def handle_exception(context: ExceptionContext) -> None:
            if not context.is_disconnect and re.match(
                r"^(?:DPY-1001|DPY-4011)", str(context.original_exception)
            ):
                context.is_disconnect = True

            return None

    The above error processing function will be invoked for all Oracle Database
    errors raised, including those caught when using the :ref:`pool pre ping
    <pool_disconnects_pessimistic>` feature for those backends that rely upon
    disconnect error handling (new in 2.0).

    .. seealso::

        :meth:`_events.DialectEvents.handle_error`

.. _pool_use_lifo:

使用 FIFO 与 LIFO
-------------------

Using FIFO vs. LIFO

.. tab:: 中文

    :class:`.QueuePool` 类包含一个名为 :paramref:`.QueuePool.use_lifo` 的标志，也可以通过 :func:`_sa.create_engine` 函数的参数 :paramref:`_sa.create_engine.pool_use_lifo` 进行设置。将此标志设为 ``True`` 会使连接池的“队列”行为改为“栈”行为，即最后归还到连接池的连接会是下一次请求中最先使用的。与连接池默认的先进先出（FIFO）行为相对，后进先出（LIFO）模式允许多余的连接在池中保持空闲，从而让服务器端的超时机制关闭这些连接。FIFO 与 LIFO 之间的区别，本质上在于是否希望连接池在空闲期间依然保持完整的连接集::

        engine = create_engine("postgresql://", pool_use_lifo=True, pool_pre_ping=True)

    上述示例中，我们还启用了 :paramref:`_sa.create_engine.pool_pre_ping` 标志，以便连接池在服务器端关闭连接时能够优雅处理，并替换为新的连接。

    请注意，该标志仅适用于 :class:`.QueuePool`。

    .. seealso::

        :ref:`pool_disconnects`

.. tab:: 英文

    The :class:`.QueuePool` class features a flag called
    :paramref:`.QueuePool.use_lifo`, which can also be accessed from
    :func:`_sa.create_engine` via the flag :paramref:`_sa.create_engine.pool_use_lifo`.
    Setting this flag to ``True`` causes the pool's "queue" behavior to instead be
    that of a "stack", e.g. the last connection to be returned to the pool is the
    first one to be used on the next request. In contrast to the pool's long-
    standing behavior of first-in-first-out, which produces a round-robin effect of
    using each connection in the pool in series, lifo mode allows excess
    connections to remain idle in the pool, allowing server-side timeout schemes to
    close these connections out.   The difference between FIFO and LIFO is
    basically whether or not its desirable for the pool to keep a full set of
    connections ready to go even during idle periods::

        engine = create_engine("postgresql://", pool_use_lifo=True, pool_pre_ping=True)

    Above, we also make use of the :paramref:`_sa.create_engine.pool_pre_ping` flag
    so that connections which are closed from the server side are gracefully
    handled by the connection pool and replaced with a new connection.

    Note that the flag only applies to :class:`.QueuePool` use.

    .. seealso::

        :ref:`pool_disconnects`


.. _pooling_multiprocessing:

使用具有多处理或 os.fork() 的连接池
--------------------------------------------------------

Using Connection Pools with Multiprocessing or os.fork()

.. tab:: 中文

    当使用连接池（从而也包括通过 :func:`_sa.create_engine` 创建的 :class:`_engine.Engine`）时， **务必不要将连接池共享给子进程** 。TCP 连接由文件描述符表示，这些描述符通常能跨进程使用，这意味着可能会导致多个独立 Python 解释器状态同时访问同一个文件描述符。
    
    根据驱动和操作系统的不同，可能出现的情况从连接无法使用到多个进程同时使用一个 socket 连接而导致的消息错乱（通常是最常见的情况）。
    
    SQLAlchemy 的 :class:`_engine.Engine` 对象引用的是一个已存在数据库连接的连接池。因此当该对象被复制到子进程时，目标是确保不会将任何数据库连接带入子进程。有以下四种通用方法可实现此目的：
    
    1. 使用 :class:`.NullPool` 禁用连接池。这是一种最简单的一次性机制，确保 :class:`_engine.Engine` 创建的连接不会被重复使用::
    
        from sqlalchemy.pool import NullPool
    
        engine = create_engine("mysql+mysqldb://user:pass@host/dbname", poolclass=NullPool)
    
    2. 在子进程初始化阶段对任何给定的 :class:`_engine.Engine` 调用 :meth:`_engine.Engine.dispose`，并传入参数 :paramref:`.Engine.dispose.close=False`。这样可确保子进程不会触及父进程的连接，而是从新连接开始使用。
       **这是推荐方式**::
    
            from multiprocessing import Pool
    
            engine = create_engine("mysql+mysqldb://user:pass@host/dbname")
    
    
            def run_in_process(some_data_record):
                with engine.connect() as conn:
                    conn.execute(text("..."))
    
    
            def initializer():
                """确保子进程不会使用父进程的连接"""
                engine.dispose(close=False)
    
    
            with Pool(10, initializer=initializer) as p:
                p.map(run_in_process, data)
    
       .. versionadded:: 1.4.33  
          添加了 :paramref:`.Engine.dispose.close` 参数，用于在子进程中替换连接池而不干扰父进程连接的使用。
    
    3. 在创建子进程 **之前** 直接调用 :meth:`.Engine.dispose`。这也能使子进程从新的连接池开始，同时确保父进程的连接不会被转移::
    
            engine = create_engine("mysql://user:pass@host/dbname")
    
    
            def run_in_process():
                with engine.connect() as conn:
                    conn.execute(text("..."))
    
    
            # 在进程启动前调用 dispose()
            engine.dispose()
            p = Process(target=run_in_process)
            p.start()
    
    4. 可以为连接池添加事件处理器，用于检测连接是否被跨进程共享，并使其失效::
    
        from sqlalchemy import event
        from sqlalchemy import exc
        import os
    
        engine = create_engine("...")
    
    
        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            connection_record.info["pid"] = os.getpid()
    
    
        @event.listens_for(engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            pid = os.getpid()
            if connection_record.info["pid"] != pid:
                connection_record.dbapi_connection = connection_proxy.dbapi_connection = None
                raise exc.DisconnectionError(
                    "连接记录属于进程 %s，"
                    "当前尝试在进程 %s 中检出" % (connection_record.info["pid"], pid)
                )
    
    上述方法中，我们采用了与 :ref:`pool_disconnects_pessimistic` 中描述的方法类似的手段，将来源于其他父进程的 DBAPI 连接视为“无效”，强制连接池回收并创建新连接。
    
    以上策略适用于 :class:`_engine.Engine` 被多个进程共享的情况。对于跨进程共享某个特定 :class:`_engine.Connection` 的情况，上述做法并不充分；应始终确保某个特定的 :class:`_engine.Connection` 仅限于单个进程（和线程）使用。同样，不支持将任何处于事务状态的对象直接跨进程共享，例如已启动事务并持有活动 :class:`_orm.Connection` 实例的 ORM :class:`_orm.Session` 对象；在新进程中应创建新的 :class:`_orm.Session` 实例。

.. tab:: 英文

    It's critical that when using a connection pool, and by extension when
    using an :class:`_engine.Engine` created via :func:`_sa.create_engine`, that
    the pooled connections **are not shared to a forked process**.  TCP connections
    are represented as file descriptors, which usually work across process
    boundaries, meaning this will cause concurrent access to the file descriptor
    on behalf of two or more entirely independent Python interpreter states.
    
    Depending on specifics of the driver and OS, the issues that arise here range
    from non-working connections to socket connections that are used by multiple
    processes concurrently, leading to broken messaging (the latter case is
    typically the most common).
    
    The SQLAlchemy :class:`_engine.Engine` object refers to a connection pool of existing
    database connections.  So when this object is replicated to a child process,
    the goal is to ensure that no database connections are carried over.  There
    are four general approaches to this:
    
    1. Disable pooling using :class:`.NullPool`.  This is the most simplistic,
       one shot system that prevents the :class:`_engine.Engine` from using any connection
       more than once::
    
        from sqlalchemy.pool import NullPool
    
        engine = create_engine("mysql+mysqldb://user:pass@host/dbname", poolclass=NullPool)
    
    2. Call :meth:`_engine.Engine.dispose` on any given :class:`_engine.Engine`,
       passing the :paramref:`.Engine.dispose.close` parameter with a value of
       ``False``, within the initialize phase of the child process.  This is
       so that the new process will not touch any of the parent process' connections
       and will instead start with new connections.
       **This is the recommended approach**::
    
            from multiprocessing import Pool
    
            engine = create_engine("mysql+mysqldb://user:pass@host/dbname")
    
    
            def run_in_process(some_data_record):
                with engine.connect() as conn:
                    conn.execute(text("..."))
    
    
            def initializer():
                """ensure the parent proc's database connections are not touched
                in the new connection pool"""
                engine.dispose(close=False)
    
    
            with Pool(10, initializer=initializer) as p:
                p.map(run_in_process, data)
    
       .. versionadded:: 1.4.33  Added the :paramref:`.Engine.dispose.close`
          parameter to allow the replacement of a connection pool in a child
          process without interfering with the connections used by the parent
          process.
    
    3. Call :meth:`.Engine.dispose` **directly before** the child process is
       created.  This will also cause the child process to start with a new
       connection pool, while ensuring the parent connections are not transferred
       to the child process::
    
            engine = create_engine("mysql://user:pass@host/dbname")
    
    
            def run_in_process():
                with engine.connect() as conn:
                    conn.execute(text("..."))
    
    
            # before process starts, ensure engine.dispose() is called
            engine.dispose()
            p = Process(target=run_in_process)
            p.start()
    
    4. An event handler can be applied to the connection pool that tests for
       connections being shared across process boundaries, and invalidates them::
    
        from sqlalchemy import event
        from sqlalchemy import exc
        import os
    
        engine = create_engine("...")
    
    
        @event.listens_for(engine, "connect")
        def connect(dbapi_connection, connection_record):
            connection_record.info["pid"] = os.getpid()
    
    
        @event.listens_for(engine, "checkout")
        def checkout(dbapi_connection, connection_record, connection_proxy):
            pid = os.getpid()
            if connection_record.info["pid"] != pid:
                connection_record.dbapi_connection = connection_proxy.dbapi_connection = None
                raise exc.DisconnectionError(
                    "Connection record belongs to pid %s, "
                    "attempting to check out in pid %s" % (connection_record.info["pid"], pid)
                )
    
       Above, we use an approach similar to that described in
       :ref:`pool_disconnects_pessimistic` to treat a DBAPI connection that
       originated in a different parent process as an "invalid" connection,
       coercing the pool to recycle the connection record to make a new connection.
    
    The above strategies will accommodate the case of an :class:`_engine.Engine`
    being shared among processes. The above steps alone are not sufficient for the
    case of sharing a specific :class:`_engine.Connection` over a process boundary;
    prefer to keep the scope of a particular :class:`_engine.Connection` local to a
    single process (and thread). It's additionally not supported to share any kind
    of ongoing transactional state directly across a process boundary, such as an
    ORM :class:`_orm.Session` object that's begun a transaction and references
    active :class:`_orm.Connection` instances; again prefer to create new
    :class:`_orm.Session` objects in new processes.

直接使用连接池实例
------------------------------

Using a pool instance directly

.. tab:: 中文

    连接池实现可以在不使用 Engine 的情况下直接使用。这种方式适用于只希望使用连接池行为，而不需要 SQLAlchemy 其他功能的应用程序。

    下面的示例中，通过 :func:`_sa.create_pool_from_url` 获取了 ``MySQLdb`` 方言的默认连接池::

        from sqlalchemy import create_pool_from_url

        my_pool = create_pool_from_url(
            "mysql+mysqldb://", max_overflow=5, pool_size=5, pre_ping=True
        )

        con = my_pool.connect()
        # 使用连接
        ...
        # 然后关闭它
        con.close()

    如果未显式指定要创建的连接池类型，将使用该方言的默认连接池类型。若希望明确指定连接池类型，可使用 ``poolclass`` 参数，如下示例所示::

        from sqlalchemy import create_pool_from_url
        from sqlalchemy import NullPool

        my_pool = create_pool_from_url("mysql+mysqldb://", poolclass=NullPool)

.. tab:: 英文

    A pool implementation can be used directly without an engine. This could be used
    in applications that just wish to use the pool behavior without all other
    SQLAlchemy features.
    In the example below the default pool for the ``MySQLdb`` dialect is obtained using
    :func:`_sa.create_pool_from_url`::

        from sqlalchemy import create_pool_from_url

        my_pool = create_pool_from_url(
            "mysql+mysqldb://", max_overflow=5, pool_size=5, pre_ping=True
        )

        con = my_pool.connect()
        # use the connection
        ...
        # then close it
        con.close()

    If the type of pool to create is not specified, the default one for the dialect
    will be used. To specify it directly the ``poolclass`` argument can be used,
    like in the following example::

        from sqlalchemy import create_pool_from_url
        from sqlalchemy import NullPool

        my_pool = create_pool_from_url("mysql+mysqldb://", poolclass=NullPool)

.. _pool_api:

API 文档 - 可用的连接池实现
--------------------------------------------------

API Documentation - Available Pool Implementations

.. tab:: 中文

.. tab:: 英文

.. autoclass:: sqlalchemy.pool.Pool
    :members:

.. autoclass:: sqlalchemy.pool.QueuePool
    :members:

.. autoclass:: sqlalchemy.pool.AsyncAdaptedQueuePool
    :members:

.. autoclass:: SingletonThreadPool
    :members:

.. autoclass:: AssertionPool
    :members:

.. autoclass:: NullPool
    :members:

.. autoclass:: StaticPool
    :members:

.. autoclass:: ManagesConnection
    :members:

.. autoclass:: ConnectionPoolEntry
    :members:
    :inherited-members:

.. autoclass:: PoolProxiedConnection
    :members:
    :inherited-members:

.. autoclass:: _ConnectionFairy

.. autoclass:: _ConnectionRecord
