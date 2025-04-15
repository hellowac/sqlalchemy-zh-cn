:orphan:

.. _errors:

==============
错误消息
==============

Error Messages

.. tab:: 中文

    本节列出了 SQLAlchemy 抛出或发出的常见错误消息和警告的描述和背景。

    SQLAlchemy 通常在 SQLAlchemy 特定的异常类的上下文中引发错误。有关这些类的详细信息，请参阅 :ref:`core_exceptions_toplevel` 和 :ref:`orm_exceptions_toplevel`。

    SQLAlchemy 错误大致可以分为两类： **编程时错误(programming-time error)** 和 **运行时错误(runtime error)**。编程时错误是由于函数或方法被调用时传递了不正确的参数，或者其他配置方法（如无法解析的映射器配置）导致的错误。编程时错误通常是即时的和确定的。另一方面，运行时错误表示程序运行时响应某些任意条件（例如数据库连接耗尽或某些数据相关问题发生）而发生的失败。运行时错误更有可能出现在运行中的应用程序日志中，因为程序在响应负载和数据时遇到了这些状态。

    由于运行时错误不容易重现，通常发生在程序运行时响应某些任意条件，因此它们更难调试，也会影响已经投入生产的程序。

    在本节中，目标是尝试提供一些最常见的运行时错误以及编程时错误的背景信息。

.. tab:: 英文

    This section lists descriptions and background for common error messages
    and warnings raised or emitted by SQLAlchemy.

    SQLAlchemy normally raises errors within the context of a SQLAlchemy-specific
    exception class.  For details on these classes, see
    :ref:`core_exceptions_toplevel` and :ref:`orm_exceptions_toplevel`.

    SQLAlchemy errors can roughly be separated into two categories, the
    **programming-time error** and the **runtime error**.     Programming-time
    errors are raised as a result of functions or methods being called with
    incorrect arguments, or from other configuration-oriented methods such  as
    mapper configurations that can't be resolved.   The programming-time error is
    typically immediate and deterministic.    The runtime error on the other hand
    represents a failure that occurs as a program runs in response to some
    condition that occurs arbitrarily, such as database connections being
    exhausted or some data-related issue occurring.   Runtime errors are more
    likely to be seen in the logs of a running application as the program
    encounters these states in response to load and data being encountered.

    Since runtime errors are not as easy to reproduce and often occur in response
    to some arbitrary condition as the program runs, they are more difficult to
    debug and also affect programs that have already been put into production.

    Within this section, the goal is to try to provide background on some of the
    most common runtime errors as well as programming time errors.



连接和会话
----------------------------

Connections and Transactions

.. _error_3o7r:

QueuePool 大小限制 <x> 已达到溢出 <y>，连接超时，超时 <z>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

QueuePool limit of size <x> overflow <y> reached, connection timed out, timeout <z>

.. tab:: 中文

    这可能是最常见的运行时错误，因为它直接涉及应用程序的负载超出了配置的上限，而这个上限通常适用于几乎所有 SQLAlchemy 应用程序。
    
    以下几点总结了该错误的含义，从最基础的点开始，这些内容大多数 SQLAlchemy 用户应已熟悉：
    
    * **SQLAlchemy 的 Engine 对象默认使用连接池** —— 这意味着，当通过 :class:`_engine.Engine` 对象使用一个 SQL 数据库连接资源，并随后 :term:`释放` 该资源时，该数据库连接本身仍保持与数据库的连接状态，并被返回到一个内部队列中以便重用。尽管代码看上去像是结束了与数据库的交互，但在许多情况下，应用程序实际上仍然会保持一组固定数量的数据库连接，直到应用退出或显式释放连接池。
    
    * 由于存在连接池，当应用程序使用数据库连接（通常是通过调用 :meth:`_engine.Engine.connect` 或使用 ORM 的 :class:`.Session` 进行查询）时，获取连接对象的操作并不一定会立刻建立一个新的数据库连接；相反，它会从连接池中获取连接，这通常意味着重用一个现有的连接。如果没有可用连接，连接池会创建一个新连接，但前提是尚未超过配置的最大容量。
    
    * 默认使用的连接池通常是 :class:`.QueuePool`。当请求连接但没有可用连接时，只有在当前使用中的连接数量 **小于配置值** 时，它才会创建新连接。这个配置值等于 **连接池大小加上最大溢出数（max overflow）**。例如，以下配置：
    
      .. sourcecode:: python
    
        engine = create_engine("mysql+mysqldb://u:p@host/db", pool_size=10, max_overflow=20)
    
      上述 :class:`_engine.Engine` 对象最多允许同时使用 **30 个连接**，不包括那些已从 engine 分离或已失效的连接。如果此时有新的连接请求，而已有 30 个连接被其他部分占用，连接池会阻塞一段固定时间，随后超时报错并抛出本错误。
    
      若需要同时使用更多连接，可通过 :func:`_sa.create_engine` 函数传入 :paramref:`_sa.create_engine.pool_size` 与 :paramref:`_sa.create_engine.max_overflow` 参数来调整池容量。等待连接可用的超时时间通过 :paramref:`_sa.create_engine.pool_timeout` 参数进行配置。
    
    * 若将 :paramref:`_sa.create_engine.max_overflow` 设置为 -1，即可将连接池配置为 **无限溢出** 。此时连接池仍然维护固定的连接池数量，但不会在无连接可用时阻塞，而是无条件地创建新连接。
    
      但若以此方式运行，当应用程序耗尽所有可用的数据库连接资源时，最终仍会触发数据库本身的连接数上限，并再次报错。更严重的是，一旦应用程序耗尽数据库连接，往往已消耗了大量系统资源，并可能影响其他应用程序或依赖数据库可用性的系统组件。
    
      基于以上原因，连接池应被视为 **连接使用的安全阀** ，为防止异常应用导致数据库整体不可用提供了一层关键保护。当出现此错误时，更优的做法是修复连接过度使用的问题，或正确配置连接上限，而非允许无限溢出，因为那并不能真正解决根本问题。
    
    那么，导致应用耗尽连接的常见原因有哪些？
    
    * **应用程序处理了过多并发请求，超出配置的连接池容量** —— 这是最直接的原因。例如，如果你有一个线程池支持最多 30 个并发线程的应用程序，并且每个线程使用一个数据库连接，如果连接池未配置为至少支持 30 个并发连接，一旦并发请求数达到上限，就会抛出该错误。解决方法是增加连接池限制，或减少并发线程数。
    
    * **应用程序未将连接归还至连接池** —— 另一个常见原因是，应用程序虽然使用了连接池，但未正确 :term:`释放` 连接，而是长时间保持连接处于打开状态。连接池以及 ORM 的 :class:`.Session` 均实现了当连接对象或 session 被垃圾回收时释放底层连接资源的逻辑，但该行为并不能确保及时释放资源。
    
      这种问题常见于使用 ORM session 后未调用 :meth:`.Session.close` 显式关闭的情况。解决方法是确保在工作完成后关闭 ORM 的 session（若使用 ORM），或关闭绑定到 engine 的 :class:`_engine.Connection` 对象（若使用 Core），可通过调用 ``.close()`` 方法或使用上下文管理器（如 "with:" 语句）来正确释放资源。
    
    * **应用程序运行了长时间事务** —— 数据库事务是非常昂贵的资源， **绝不能长时间闲置等待某个事件** 。例如：应用在等待用户点击按钮、等待长时间任务队列的结果，或维持持久连接与浏览器通信的过程中， **都不应保持事务处于打开状态**。应在真正需要与数据库交互时才打开事务，完成后立即关闭。
    
    * **应用程序发生死锁** —— 这是另一个常见且更难排查的原因。如果因应用端或数据库端的死锁，导致应用无法完成连接的使用，则可能耗尽所有可用连接，导致新的连接请求报错。死锁可能由以下原因造成：
    
      * 使用如 gevent 或 eventlet 的隐式异步系统，但未正确 monkeypatch 所有 socket 库和驱动程序，或 monkeypatch 不完整；也可能是异步系统处理 CPU 密集型任务时，greenlet 长时间未响应数据库操作。对于大多数关系型数据库操作来说，无论是隐式还是显式的异步编程框架通常都不是必须或合适的。如果某些功能区必须使用异步，最好将数据库操作放在传统线程中运行，通过消息传递与异步部分通信。
    
      * 数据库层面的死锁，例如两个事务互相等待对方释放行锁。
    
      * 线程死锁错误，例如互相等待的 mutex，或在同一线程中对已加锁的 mutex 进行重复加锁。
    
    请注意，使用连接池并不是强制的，也可以选择完全关闭连接池。参见 :ref:`pool_switching` 获取更多背景。但需要强调的是，当此类错误出现时， **问题总是出在应用本身** ；连接池只是帮助更早暴露出该问题而已。
    
    .. seealso::
    
        :ref:`pooling_toplevel`
    
        :ref:`connections_toplevel`

.. tab:: 英文

    This is possibly the most common runtime error experienced, as it directly
    involves the work load of the application surpassing a configured limit, one
    which typically applies to nearly all SQLAlchemy applications.
    
    The following points summarize what this error means, beginning with the
    most fundamental points that most SQLAlchemy users should already be
    familiar with.
    
    * **The SQLAlchemy Engine object uses a pool of connections by default** - What
      this means is that when one makes use of a SQL database connection resource
      of an :class:`_engine.Engine` object, and then :term:`releases` that resource,
      the database connection itself remains connected to the database and
      is returned to an internal queue where it can be used again.  Even though
      the code may appear to be ending its conversation with the database, in many
      cases the application will still maintain a fixed number of database connections
      that persist until the application ends or the pool is explicitly disposed.
    
    * Because of the pool, when an application makes use of a SQL database
      connection, most typically from either making use of :meth:`_engine.Engine.connect`
      or when making queries using an ORM :class:`.Session`, this activity
      does not necessarily establish a new connection to the database at the
      moment the connection object is acquired; it instead consults the
      connection pool for a connection, which will often retrieve an existing
      connection from the pool to be re-used.  If no connections are available,
      the pool will create a new database connection, but only if the
      pool has not surpassed a configured capacity.
    
    * The default pool used in most cases is called :class:`.QueuePool`.  When
      you ask this pool to give you a connection and none are available, it
      will create a new connection **if the total number of connections in play
      are less than a configured value**.  This value is equal to the
      **pool size plus the max overflow**.     That means if you have configured
      your engine as::
    
       engine = create_engine("mysql+mysqldb://u:p@host/db", pool_size=10, max_overflow=20)
    
      The above :class:`_engine.Engine` will allow **at most 30 connections** to be in
      play at any time, not including connections that were detached from the
      engine or invalidated.  If a request for a new connection arrives and
      30 connections are already in use by other parts of the application,
      the connection pool will block for a fixed period of time,
      before timing out and raising this error message.
    
      In order to allow for a higher number of connections be in use at once,
      the pool can be adjusted using the
      :paramref:`_sa.create_engine.pool_size` and :paramref:`_sa.create_engine.max_overflow`
      parameters as passed to the :func:`_sa.create_engine` function.      The timeout
      to wait for a connection to be available is configured using the
      :paramref:`_sa.create_engine.pool_timeout` parameter.
    
    * The pool can be configured to have unlimited overflow by setting
      :paramref:`_sa.create_engine.max_overflow` to the value "-1".  With this setting,
      the pool will still maintain a fixed pool of connections, however it will
      never block upon a new connection being requested; it will instead unconditionally
      make a new connection if none are available.
    
      However, when running in this way, if the application has an issue where it
      is using up all available connectivity resources, it will eventually hit the
      configured limit of available connections on the database itself, which will
      again return an error.  More seriously, when the application exhausts the
      database of connections, it usually will have caused a great
      amount of  resources to be used up before failing, and can also interfere
      with other applications and database status mechanisms that rely upon being
      able to connect to the database.
    
      Given the above, the connection pool can be looked at as a **safety valve
      for connection use**, providing a critical layer of protection against
      a rogue application causing the entire database to become unavailable
      to all other applications.   When receiving this error message, it is vastly
      preferable to repair the issue using up too many connections and/or
      configure the limits appropriately, rather than allowing for unlimited
      overflow which does not actually solve the underlying issue.
    
    What causes an application to use up all the connections that it has available?
    
    * **The application is fielding too many concurrent requests to do work based
      on the configured value for the pool** - This is the most straightforward
      cause.  If you have
      an application that runs in a thread pool that allows for 30 concurrent
      threads, with one connection in use per thread, if your pool is not configured
      to allow at least 30 connections checked out at once, you will get this
      error once your application receives enough concurrent requests. Solution
      is to raise the limits on the pool or lower the number of concurrent threads.
    
    * **The application is not returning connections to the pool** - This is the
      next most common reason, which is that the application is making use of the
      connection pool, but the program is failing to :term:`release` these
      connections and is instead leaving them open.   The connection pool as well
      as the ORM :class:`.Session` do have logic such that when the session and/or
      connection object is garbage collected, it results in the underlying
      connection resources being released, however this behavior cannot be relied
      upon to release resources in a timely manner.
    
      A common reason this can occur is that the application uses ORM sessions and
      does not call :meth:`.Session.close` upon them one the work involving that
      session is complete. Solution is to make sure ORM sessions if using the ORM,
      or engine-bound :class:`_engine.Connection` objects if using Core, are explicitly
      closed at the end of the work being done, either via the appropriate
      ``.close()`` method, or by using one of the available context managers (e.g.
      "with:" statement) to properly release the resource.
    
    * **The application is attempting to run long-running transactions** - A
      database transaction is a very expensive resource, and should **never be
      left idle waiting for some event to occur**.  If an application is waiting
      for a user to push a button, or a result to come off of a long running job
      queue, or is holding a persistent connection open to a browser, **don't
      keep a database transaction open for the whole time**.  As the application
      needs to work with the database and interact with an event, open a short-lived
      transaction at that point and then close it.
    
    * **The application is deadlocking** - Also a common cause of this error and
      more difficult to grasp, if an application is not able to complete its use
      of a connection either due to an application-side or database-side deadlock,
      the application can use up all the available connections which then leads to
      additional requests receiving this error.   Reasons for deadlocks include:
    
      * Using an implicit async system such as gevent or eventlet without
        properly monkeypatching all socket libraries and drivers, or which
        has bugs in not fully covering for all monkeypatched driver methods,
        or less commonly when the async system is being used against CPU-bound
        workloads and greenlets making use of database resources are simply waiting
        too long to attend to them.  Neither implicit nor explicit async
        programming frameworks are typically
        necessary or appropriate for the vast majority of relational database
        operations; if an application must use an async system for some area
        of functionality, it's best that database-oriented business methods
        run within traditional threads that pass messages to the async part
        of the application.
    
      * A database side deadlock, e.g. rows are mutually deadlocked
    
      * Threading errors, such as mutexes in a mutual deadlock, or calling
        upon an already locked mutex in the same thread
    
    Keep in mind an alternative to using pooling is to turn off pooling entirely.
    See the section :ref:`pool_switching` for background on this.  However, note
    that when this error message is occurring, it is **always** due to a bigger
    problem in the application itself; the pool just helps to reveal the problem
    sooner.
    
    .. seealso::
    
        :ref:`pooling_toplevel`
    
        :ref:`connections_toplevel`

.. _error_pcls:

Pool类不能与 asyncio 引擎一起使用（反之亦然）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pool class cannot be used with asyncio engine (or vice versa)

.. tab:: 中文

    :class:`_pool.QueuePool` 连接池类内部使用了 ``thread.Lock``，因此不兼容 asyncio。如果使用 :func:`_asyncio.create_async_engine` 函数创建 :class:`.AsyncEngine`，则会自动使用适用于 asyncio 的 :class:`_pool.AsyncAdaptedQueuePool`，无需显式指定。

    除了 :class:`_pool.AsyncAdaptedQueuePool` 之外，:class:`_pool.NullPool` 与 :class:`_pool.StaticPool` 这两种连接池类型不使用锁机制，因此也适用于异步引擎。

    在极少数情况下，如果通过 :func:`_sa.create_engine` 显式指定使用 :class:`_pool.AsyncAdaptedQueuePool`，也可能抛出该错误的反向版本。

    .. seealso::

        :ref:`pooling_toplevel`

.. tab:: 英文

    The :class:`_pool.QueuePool` pool class uses a ``thread.Lock`` object internally
    and is not compatible with asyncio.  If using the :func:`_asyncio.create_async_engine`
    function to create an :class:`.AsyncEngine`, the appropriate queue pool class
    is :class:`_pool.AsyncAdaptedQueuePool`, which is used automatically and does
    not need to be specified.

    In addition to :class:`_pool.AsyncAdaptedQueuePool`, the :class:`_pool.NullPool`
    and :class:`_pool.StaticPool` pool classes do not use locks and are also
    suitable for use with async engines.

    This error is also raised in reverse in the unlikely case that the
    :class:`_pool.AsyncAdaptedQueuePool` pool class is indicated explicitly with
    the :func:`_sa.create_engine` function.

    .. seealso::

        :ref:`pooling_toplevel`

.. _error_8s2b:

无效事务回滚前无法重新连接。要继续前请先完全回滚(rollback)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Can't reconnect until invalid transaction is rolled back.  Please rollback() fully before proceeding

.. tab:: 中文

    当出现该错误情况时，表示一个 :class:`_engine.Connection` 连接已被作废（invalidated），这可能是由于数据库断开被检测到，或显式调用了 :meth:`_engine.Connection.invalidate` 方法导致的；但此时仍然存在一个事务，该事务可能是通过 :meth:`_engine.Connection.begin` 方法显式启动的，或是在 SQLAlchemy 2.x 系列中，当执行任意 SQL 语句时，连接自动开启事务所产生的。当连接被作废后，任何正在进行中的 :class:`_engine.Transaction` 事务都处于无效状态，必须显式回滚（rollback）以将其从 :class:`_engine.Connection` 上移除。

.. tab:: 英文

    This error condition refers to the case where a :class:`_engine.Connection` was
    invalidated, either due to a database disconnect detection or due to an
    explicit call to :meth:`_engine.Connection.invalidate`, but there is still a
    transaction present that was initiated either explicitly by the :meth:`_engine.Connection.begin`
    method, or due to the connection automatically beginning a transaction as occurs
    in the 2.x series of SQLAlchemy when any SQL statements are emitted.  When a connection is invalidated, any :class:`_engine.Transaction`
    that was in progress is now in an invalid state, and must be explicitly rolled
    back in order to remove it from the :class:`_engine.Connection`.

.. _error_dbapi:

DBAPI 错误
------------

DBAPI Errors

.. tab:: 中文

    Python 数据库 API（DBAPI）是数据库驱动程序的一项规范，可在 `Pep-249 <https://www.python.org/dev/peps/pep-0249/>`_ 中找到。该 API 规定了一组异常类，以涵盖数据库可能发生的所有失败模式。

    SQLAlchemy 本身并不会直接抛出这些异常。相反，它会拦截来自数据库驱动的异常，并将其包装为 SQLAlchemy 提供的异常类 :class:`.DBAPIError`， **但异常中的消息内容是由驱动程序生成的，而非 SQLAlchemy**。

.. tab:: 英文

    The Python database API, or DBAPI, is a specification for database drivers
    which can be located at `Pep-249 <https://www.python.org/dev/peps/pep-0249/>`_.
    This API specifies a set of exception classes that accommodate the full range
    of failure modes of the database.

    SQLAlchemy does not generate these exceptions directly.  Instead, they are
    intercepted from the database driver and wrapped by the SQLAlchemy-provided
    exception :class:`.DBAPIError`, however the messaging within the exception is
    **generated by the driver, not SQLAlchemy**.

.. _error_rvf5:

接口错误
~~~~~~~~~~~~~~

InterfaceError

.. tab:: 中文

    抛出此异常表示发生了与数据库接口有关的错误，而非数据库本身的问题。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

    在某些情况下，当数据库连接被断开，或无法连接数据库时，驱动程序会抛出 ``InterfaceError`` 异常。有关如何应对此类情况的建议，请参阅 :ref:`pool_disconnects` 一节。

.. tab:: 英文

    Exception raised for errors that are related to the database interface rather
    than the database itself.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

    The ``InterfaceError`` is sometimes raised by drivers in the context
    of the database connection being dropped, or not being able to connect
    to the database.   For tips on how to deal with this, see the section
    :ref:`pool_disconnects`.

.. _error_4xp6:

数据库错误
~~~~~~~~~~~~~

DatabaseError

.. tab:: 中文

    抛出此异常表示发生了与数据库本身有关的错误，而不是与接口或传递数据相关的问题。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

.. tab:: 英文

    Exception raised for errors that are related to the database itself, and not
    the interface or data being passed.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

.. _error_9h9h:

数据错误
~~~~~~~~~

DataError

.. tab:: 中文

    抛出此异常表示处理的数据出现问题，例如除以零、数值超出范围等。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

.. tab:: 英文

    Exception raised for errors that are due to problems with the processed data
    like division by zero, numeric value out of range, etc.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

.. _error_e3q8:

操作错误
~~~~~~~~~~~~~~~~

OperationalError

.. tab:: 中文

    抛出此异常表示数据库操作过程中发生了错误，这类错误通常不完全受程序员控制，例如：

    - 意外断开连接；
    - 未找到数据源名称；
    - 事务无法处理；
    - 处理过程中出现内存分配错误等。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

    ``OperationalError`` 是驱动程序在数据库连接断开或无法连接数据库时最常使用（但不是唯一使用）的错误类型。有关应对此类情况的建议，请参阅 :ref:`pool_disconnects` 一节。

.. tab:: 英文

    Exception raised for errors that are related to the database's operation and
    not necessarily under the control of the programmer, e.g. an unexpected
    disconnect occurs, the data source name is not found, a transaction could not
    be processed, a memory allocation error occurred during processing, etc.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

    The ``OperationalError`` is the most common (but not the only) error class used
    by drivers in the context of the database connection being dropped, or not
    being able to connect to the database.   For tips on how to deal with this, see
    the section :ref:`pool_disconnects`.

.. _error_gkpj:

完整性错误
~~~~~~~~~~~~~~

IntegrityError

.. tab:: 中文

    抛出此异常表示数据库的关系完整性受到影响，例如外键检查失败。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

.. tab:: 英文

    Exception raised when the relational integrity of the database is affected,
    e.g. a foreign key check fails.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

.. _error_2j85:

内部错误
~~~~~~~~~~~~~

InternalError

.. tab:: 中文

    抛出此异常表示数据库遇到了内部错误，例如游标不再有效、事务状态不同步等。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

    在某些情况下，当数据库连接被断开或无法连接数据库时，驱动程序可能会抛出 ``InternalError``。有关如何应对此类情况的建议，请参阅 :ref:`pool_disconnects` 一节。

.. tab:: 英文

    Exception raised when the database encounters an internal error, e.g. the
    cursor is not valid anymore, the transaction is out of sync, etc.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

    The ``InternalError`` is sometimes raised by drivers in the context
    of the database connection being dropped, or not being able to connect
    to the database.   For tips on how to deal with this, see the section
    :ref:`pool_disconnects`.

.. _error_f405:

编程错误
~~~~~~~~~~~~~~~~

ProgrammingError

.. tab:: 中文

    抛出此异常表示发生了编程错误，例如数据表不存在或已存在、SQL 语句语法错误、参数个数错误等。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

    在某些情况下，当数据库连接被断开或无法连接数据库时，驱动程序可能会抛出 ``ProgrammingError``。有关如何应对此类情况的建议，请参阅 :ref:`pool_disconnects` 一节。

.. tab:: 英文

    Exception raised for programming errors, e.g. table not found or already
    exists, syntax error in the SQL statement, wrong number of parameters
    specified, etc.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

    The ``ProgrammingError`` is sometimes raised by drivers in the context
    of the database connection being dropped, or not being able to connect
    to the database.   For tips on how to deal with this, see the section
    :ref:`pool_disconnects`.

.. _error_tw8g:

不支持错误
~~~~~~~~~~~~~~~~~

NotSupportedError

.. tab:: 中文

    抛出此异常表示使用了数据库不支持的方法或 API，例如在不支持事务或已关闭事务的连接上调用 `.rollback()` 方法。

    此错误属于 :ref:`DBAPI Error <error_dbapi>` 类型，其来源是数据库驱动（DBAPI），而非 SQLAlchemy 自身。

.. tab:: 英文

    Exception raised in case a method or database API was used which is not
    supported by the database, e.g. requesting a .rollback() on a connection that
    does not support transaction or has transactions turned off.

    This error is a :ref:`DBAPI Error <error_dbapi>` and originates from
    the database driver (DBAPI), not SQLAlchemy itself.

SQL 表达式语言
-----------------------

SQL Expression Language

.. _error_cprf:
.. _caching_caveats:

对象不会产生缓存键，性能影响
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Object will not produce a cache key, Performance Implications

.. tab:: 中文

    从 SQLAlchemy 1.4 版本开始，提供了一个 :ref:`SQL 编译缓存机制 <sql_caching>`，用于缓存 Core 和 ORM 中 SQL 构造对象的字符串化形式以及用于从语句中提取结果的结构信息，从而在下一次使用结构上等价的构造对象时跳过相对昂贵的字符串编译过程。该机制依赖于所有 SQL 构造对象的功能支持，包括像 :class:`_schema.Column` 、 :func:`_sql.select` 和 :class:`_types.TypeEngine` 这样的对象，来生成一个能完整表示其状态、并影响 SQL 编译过程的 **缓存键（cache key）**。

    如果相关警告指向的是广泛使用的对象，例如 :class:`_schema.Column`，并且这些警告影响到了大多数被发出的 SQL 构造（可参考 :ref:`sql_caching_logging` 所述的估算方法），导致缓存机制整体上未能启用，这将对性能产生负面影响，在某些情况下甚至会 **造成比旧版本更差的性能退化**。详见 :ref:`faq_new_caching` 中的相关说明。

.. tab:: 英文

    SQLAlchemy as of version 1.4 includes a
    :ref:`SQL compilation caching facility <sql_caching>` which will allow
    Core and ORM SQL constructs to cache their stringified form, along with other
    structural information used to fetch results from the statement, allowing the
    relatively expensive string compilation process to be skipped when another
    structurally equivalent construct is next used. This system
    relies upon functionality that is implemented for all SQL constructs, including
    objects such as  :class:`_schema.Column`,
    :func:`_sql.select`, and :class:`_types.TypeEngine` objects, to produce a
    **cache key** which fully represents their state to the degree that it affects
    the SQL compilation process.

    If the warnings in question refer to widely used objects such as
    :class:`_schema.Column` objects, and are shown to be affecting the majority of
    SQL constructs being emitted (using the estimation techniques described at
    :ref:`sql_caching_logging`) such that caching is generally not enabled for an
    application, this will negatively impact performance and can in some cases
    effectively produce a **performance degradation** compared to prior SQLAlchemy
    versions. The FAQ at :ref:`faq_new_caching` covers this in additional detail.

如果有任何疑问，缓存会自行禁用
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Caching disables itself if there's any doubt

.. tab:: 中文

    缓存依赖于能够生成准确、一致地表示语句结构的缓存键。如果某个 SQL 构造对象（或类型）没有提供正确的指令来生成缓存键，则无法安全地启用缓存：

    * 缓存键必须能表示 **完整结构**：如果某个构造对象的两个实例可能生成不同的 SQL，而缓存键未能捕获二者之间的差异，那么用第一个实例生成并缓存的 SQL 会在使用第二个实例时被错误复用，导致不正确的 SQL 被生成。

    * 缓存键必须具有 **一致性**：如果一个构造对象包含每次使用都变化的状态（例如字面量值），从而每次生成不同 SQL，则不应启用缓存。否则重复使用该构造会快速填满语句缓存，生成大量一次性 SQL 字符串，违背了缓存机制的初衷。

    基于以上两点，SQLAlchemy 的缓存系统在决定是否对某个对象启用 SQL 缓存时是 **极为保守的**。

.. tab:: 英文

    Caching relies on being able to generate a cache key that accurately represents
    the **complete structure** of a statement in a **consistent** fashion. If a particular
    SQL construct (or type) does not have the appropriate directives in place which
    allow it to generate a proper cache key, then caching cannot be safely enabled:
    
    * The cache key must represent the **complete structure**: If the usage of two
      separate instances of that construct may result in different SQL being
      rendered, caching the SQL against the first instance of the element using a
      cache key that does not capture the distinct differences between the first and
      second elements will result in incorrect SQL being cached and rendered for the
      second instance.
    
    * The cache key must be **consistent**: If a construct represents state that
      changes every time, such as a literal value, producing unique SQL for every
      instance of it, this construct is also not safe to cache, as repeated use of
      the construct will quickly fill up the statement cache with unique SQL strings
      that will likely not be used again, defeating the purpose of the cache.
    
    For the above two reasons, SQLAlchemy's caching system is **extremely
    conservative** about deciding to cache the SQL corresponding to an object.

缓存的断言属性
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Assertion attributes for caching

.. tab:: 中文

    警告的触发基于以下标准。每条标准的具体解释参见 :ref:`faq_new_caching`：

    * :class:`.Dialect` 本身（即我们传递给 :func:`_sa.create_engine` 的 URL 中的方言模块，比如 ``postgresql+psycopg2://`` ）必须声明其已被评估并支持缓存。这由其 :attr:`.Dialect.supports_statement_cache` 属性被设置为 ``True`` 来表示。若使用第三方方言，请联系其维护者，协助其完成 :ref:`启用缓存的步骤 <engine_thirdparty_caching>` 并发布新版本。

    * 继承自 :class:`.TypeDecorator` 或 :class:`.UserDefinedType` 的第三方或用户自定义类型，必须在定义中包含 :attr:`.ExternalType.cache_ok` 属性，其所有派生子类亦然，具体规则见该属性的 docstring。若类型来源于第三方库，请联系其维护者提供必要的改动并发布新版。

    * 继承自 :class:`.ClauseElement` 、 :class:`_schema.Column` 、 :class:`_dml.Insert` 等类的第三方或用户自定义 SQL 构造类（包括简单子类和通过 :ref:`sqlalchemy.ext.compiler_toplevel` 扩展机制实现的类）应设置 :attr:`.HasCacheKey.inherit_cache` 属性为 ``True`` 或 ``False``，根据设计需要设置，并遵循 :ref:`compilerext_caching` 中的指导。

    .. seealso::

        :ref:`sql_caching_logging` - 关于缓存行为与效率的观察手段背景资料

        :ref:`faq_new_caching` - 位于 :ref:`faq_toplevel` 部分的常见问题解答

.. tab:: 英文

    The warning is emitted based on the criteria below.  For further detail on
    each, see the section :ref:`faq_new_caching`.
    
    * The :class:`.Dialect` itself (i.e. the module that is specified by the
      first part of the URL we pass to :func:`_sa.create_engine`, like
      ``postgresql+psycopg2://``), must indicate it has been reviewed and tested
      to support caching correctly, which is indicated by the
      :attr:`.Dialect.supports_statement_cache` attribute being set to ``True``.
      When using third party dialects, consult with the maintainers of the dialect
      so that they may follow the :ref:`steps to ensure caching may be enabled
      <engine_thirdparty_caching>` in their dialect and publish a new release.
    
    * Third party or user defined types that inherit from either
      :class:`.TypeDecorator` or :class:`.UserDefinedType` must include the
      :attr:`.ExternalType.cache_ok` attribute in their definition, including for
      all derived subclasses, following the guidelines described in the docstring
      for :attr:`.ExternalType.cache_ok`. As before, if these datatypes are
      imported from third party libraries, consult with the maintainers of that
      library so that they may provide the necessary changes to their library and
      publish a new release.
    
    * Third party or user defined SQL constructs that subclass from classes such
      as :class:`.ClauseElement`, :class:`_schema.Column`, :class:`_dml.Insert`
      etc, including simple subclasses as well as those which are designed to
      work with the :ref:`sqlalchemy.ext.compiler_toplevel`, should normally
      include the :attr:`.HasCacheKey.inherit_cache` attribute set to ``True``
      or ``False`` based on the design of the construct, following the guidelines
      described at :ref:`compilerext_caching`.
    
    .. seealso::
    
        :ref:`sql_caching_logging` - background on observing cache behavior
        and efficiency
    
        :ref:`faq_new_caching` - in the :ref:`faq_toplevel` section


.. _error_l7de:

编译器 StrSQLCompiler 无法呈现类型为 <element type> 的元素
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compiler StrSQLCompiler can't render element of type <element type>

.. tab:: 中文
    
    该错误通常发生在尝试将一个 SQL 表达式构造转为字符串时，其中包含了一些不是默认编译流程支持的元素；此类错误通常会针对 :class:`.StrSQLCompiler` 类发出。在不太常见的情况下，如果使用了不适用于特定数据库后端的 SQL 表达式类型，也可能触发该错误；这时会提及其他 SQL 编译器类，例如 ``SQLCompiler`` 或 ``sqlalchemy.dialects.postgresql.PGCompiler``。以下说明主要针对“字符串化（stringification）”的用例，但也涵盖了整体背景信息。
    
    通常，Core SQL 构造或 ORM 的 :class:`_query.Query` 对象可以直接字符串化，例如使用 ``print()``：
    
    .. sourcecode:: pycon+sql
    
      >>> from sqlalchemy import column
      >>> print(column("x") == 5)
      {printsql}x = :x_1
    
    在上述 SQL 表达式被字符串化时，会使用 :class:`.StrSQLCompiler` 编译器类。该类是一个特殊的语句编译器，用于在未指定方言信息的情况下对构造进行字符串化。
    
    然而，有许多构造是特定于某些数据库方言的，:class:`.StrSQLCompiler` 无法将其转换为字符串，例如 PostgreSQL 的 :ref:`postgresql_insert_on_conflict` 构造::
    
      >>> from sqlalchemy.dialects.postgresql import insert
      >>> from sqlalchemy import table, column
      >>> my_table = table("my_table", column("x"), column("y"))
      >>> insert_stmt = insert(my_table).values(x="foo")
      >>> insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["y"])
      >>> print(insert_stmt)
      Traceback (most recent call last):
    
      ...
    
      sqlalchemy.exc.UnsupportedCompilationError:
      Compiler <sqlalchemy.sql.compiler.StrSQLCompiler object at 0x7f04fc17e320>
      can't render element of type
      <class 'sqlalchemy.dialects.postgresql.dml.OnConflictDoNothing'>
    
    要对特定于某后端的构造进行字符串化，必须使用 :meth:`_expression.ClauseElement.compile` 方法，并传入 :class:`_engine.Engine` 或 :class:`.Dialect` 对象以调用正确的编译器。如下示例使用 PostgreSQL 方言：
    
    .. sourcecode:: pycon+sql
    
      >>> from sqlalchemy.dialects import postgresql
      >>> print(insert_stmt.compile(dialect=postgresql.dialect()))
      {printsql}INSERT INTO my_table (x) VALUES (%(x)s) ON CONFLICT (y) DO NOTHING
    
    对于 ORM 的 :class:`_query.Query` 对象，可以通过 :attr:`~.orm.query.Query.statement` 属性获取对应语句::
    
        statement = query.statement
        print(statement.compile(dialect=postgresql.dialect()))
    
    更多关于 SQL 元素字符串化/编译的细节，请参考下方 FAQ 链接。
    
    .. seealso::
    
      :ref:`faq_sql_expression_string`

.. tab:: 英文

    This error usually occurs when attempting to stringify a SQL expression
    construct that includes elements which are not part of the default compilation;
    in this case, the error will be against the :class:`.StrSQLCompiler` class.
    In less common cases, it can also occur when the wrong kind of SQL expression
    is used with a particular type of database backend; in those cases, other
    kinds of SQL compiler classes will be named, such as ``SQLCompiler`` or
    ``sqlalchemy.dialects.postgresql.PGCompiler``.  The guidance below is
    more specific to the "stringification" use case but describes the general
    background as well.
    
    Normally, a Core SQL construct or ORM :class:`_query.Query` object can be stringified
    directly, such as when we use ``print()``:
    
    .. sourcecode:: pycon+sql
    
      >>> from sqlalchemy import column
      >>> print(column("x") == 5)
      {printsql}x = :x_1
    
    When the above SQL expression is stringified, the :class:`.StrSQLCompiler`
    compiler class is used, which is a special statement compiler that is invoked
    when a construct is stringified without any dialect-specific information.
    
    However, there are many constructs that are specific to some particular kind
    of database dialect, for which the :class:`.StrSQLCompiler` doesn't know how
    to turn into a string, such as the PostgreSQL
    :ref:`postgresql_insert_on_conflict` construct::
    
      >>> from sqlalchemy.dialects.postgresql import insert
      >>> from sqlalchemy import table, column
      >>> my_table = table("my_table", column("x"), column("y"))
      >>> insert_stmt = insert(my_table).values(x="foo")
      >>> insert_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["y"])
      >>> print(insert_stmt)
      Traceback (most recent call last):
    
      ...
    
      sqlalchemy.exc.UnsupportedCompilationError:
      Compiler <sqlalchemy.sql.compiler.StrSQLCompiler object at 0x7f04fc17e320>
      can't render element of type
      <class 'sqlalchemy.dialects.postgresql.dml.OnConflictDoNothing'>
    
    In order to stringify constructs that are specific to particular backend,
    the :meth:`_expression.ClauseElement.compile` method must be used, passing either an
    :class:`_engine.Engine` or a :class:`.Dialect` object which will invoke the correct
    compiler.   Below we use a PostgreSQL dialect:
    
    .. sourcecode:: pycon+sql
    
      >>> from sqlalchemy.dialects import postgresql
      >>> print(insert_stmt.compile(dialect=postgresql.dialect()))
      {printsql}INSERT INTO my_table (x) VALUES (%(x)s) ON CONFLICT (y) DO NOTHING
    
    For an ORM :class:`_query.Query` object, the statement can be accessed using the
    :attr:`~.orm.query.Query.statement` accessor::
    
        statement = query.statement
        print(statement.compile(dialect=postgresql.dialect()))
    
    See the FAQ link below for additional detail on direct stringification /
    compilation of SQL elements.
    
    .. seealso::
    
      :ref:`faq_sql_expression_string`


TypeError：'ColumnProperty' 和 <something> 的实例之间不支持 <operator>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TypeError: <operator> not supported between instances of 'ColumnProperty' and <something>

.. tab:: 中文

    当试图在 SQL 表达式上下文中使用 :func:`.column_property` 或 :func:`.deferred` 对象时，通常会遇到类似错误，这种情况多出现在声明式（declarative）使用场景中，例如::

        class Bar(Base):
            __tablename__ = "bar"

            id = Column(Integer, primary_key=True)
            cprop = deferred(Column(Integer))

            __table_args__ = (CheckConstraint(cprop > 5),)

    如上所示，``cprop`` 属性在映射完成之前被内联使用，然而该 ``cprop`` 并不是一个 :class:`_schema.Column`，而是一个 :class:`.ColumnProperty`，它是一个中间对象，因此不具备 :class:`_schema.Column` 对象或完成映射后的 :class:`.InstrumentedAttribute` 的完整功能。

    虽然 :class:`.ColumnProperty` 定义了 ``__clause_element__()`` 方法，使其在某些列上下文中可以使用，但它不能在开放式比较中使用，如上所示，因为它没有定义 Python 的 ``__eq__()`` 方法，无法将 ``> 5`` 解释为 SQL 表达式，而会被误认为是普通的 Python 比较操作。

    解决方案是通过 :attr:`.ColumnProperty.expression` 属性直接访问其底层的 :class:`_schema.Column` 对象::

        class Bar(Base):
            __tablename__ = "bar"

            id = Column(Integer, primary_key=True)
            cprop = deferred(Column(Integer))

            __table_args__ = (CheckConstraint(cprop.expression > 5),)

.. tab:: 英文

    This often occurs when attempting to use a :func:`.column_property` or
    :func:`.deferred` object in the context of a SQL expression, usually within
    declarative such as::

        class Bar(Base):
            __tablename__ = "bar"

            id = Column(Integer, primary_key=True)
            cprop = deferred(Column(Integer))

            __table_args__ = (CheckConstraint(cprop > 5),)

    Above, the ``cprop`` attribute is used inline before it has been mapped,
    however this ``cprop`` attribute is not a :class:`_schema.Column`,
    it's a :class:`.ColumnProperty`, which is an interim object and therefore
    does not have the full functionality of either the :class:`_schema.Column` object
    or the :class:`.InstrumentedAttribute` object that will be mapped onto the
    ``Bar`` class once the declarative process is complete.

    While the :class:`.ColumnProperty` does have a ``__clause_element__()`` method,
    which allows it to work in some column-oriented contexts, it can't work in an
    open-ended comparison context as illustrated above, since it has no Python
    ``__eq__()`` method that would allow it to interpret the comparison to the
    number "5" as a SQL expression and not a regular Python comparison.

    The solution is to access the :class:`_schema.Column` directly using the
    :attr:`.ColumnProperty.expression` attribute::

        class Bar(Base):
            __tablename__ = "bar"

            id = Column(Integer, primary_key=True)
            cprop = deferred(Column(Integer))

            __table_args__ = (CheckConstraint(cprop.expression > 5),)

.. _error_cd3x:

绑定参数 <x> 需要一个值（在参数组 <y> 中）
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A value is required for bind parameter <x> (in parameter group <y>)

.. tab:: 中文

    当语句中显式或隐式使用了 :func:`.bindparam`，但在执行时未提供值时，将触发此类错误::

        stmt = select(table.c.column).where(table.c.id == bindparam("my_param"))

        result = conn.execute(stmt)

    如上所示，并未为参数 "my_param" 提供任何值。正确的做法是提供一个值::

        result = conn.execute(stmt, {"my_param": 12})

    当错误信息的形式为 “a value is required for bind parameter <x> in parameter group <y>” 时，表示该语句以 “executemany” 的方式执行。在这种情形下，语句通常是 INSERT、UPDATE 或 DELETE，并且传入的是参数字典组成的列表。此时语句会基于 **第一个参数集** 推断所有需要的参数，从而确定最终的语句字符串格式。

    例如，下面的语句基于第一个参数集生成 INSERT 所需的参数 ``a``、``b`` 和 ``c``，这些名字决定了 SQL 的参数格式。但第二个参数集未包含 ``b``，因此会抛出错误::

        m = MetaData()
        t = Table("t", m, Column("a", Integer), Column("b", Integer), Column("c", Integer))

        e.execute(
            t.insert(),
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "c": 4},
                {"a": 3, "b": 4, "c": 5},
            ],
        )

    .. code-block::

        sqlalchemy.exc.StatementError: (sqlalchemy.exc.InvalidRequestError)
        A value is required for bind parameter 'b', in parameter group 1
        [SQL: u'INSERT INTO t (a, b, c) VALUES (?, ?, ?)']
        [parameters: [{'a': 1, 'c': 3, 'b': 2}, {'a': 2, 'c': 4}, {'a': 3, 'c': 5, 'b': 4}]]

    由于参数 ``b`` 是必需的，可以将其传入 ``None``，使得 INSERT 语句可以顺利执行::

        e.execute(
            t.insert(),
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "b": None, "c": 4},
                {"a": 3, "b": 4, "c": 5},
            ],
        )

    .. seealso::

        :ref:`tutorial_sending_parameters`

.. tab:: 英文

    This error occurs when a statement makes use of :func:`.bindparam` either
    implicitly or explicitly and does not provide a value when the statement
    is executed::

        stmt = select(table.c.column).where(table.c.id == bindparam("my_param"))

        result = conn.execute(stmt)

    Above, no value has been provided for the parameter "my_param".  The correct
    approach is to provide a value::

        result = conn.execute(stmt, {"my_param": 12})

    When the message takes the form "a value is required for bind parameter <x>
    in parameter group <y>", the message is referring to the "executemany" style
    of execution.  In this case, the statement is typically an INSERT, UPDATE,
    or DELETE and a list of parameters is being passed.   In this format, the
    statement may be generated dynamically to include parameter positions for
    every parameter given in the argument list, where it will use the
    **first set of parameters** to determine what these should be.

    For example, the statement below is calculated based on the first parameter
    set to require the parameters, "a", "b", and "c" - these names determine
    the final string format of the statement which will be used for each
    set of parameters in the list.  As the second entry does not contain "b",
    this error is generated::

        m = MetaData()
        t = Table("t", m, Column("a", Integer), Column("b", Integer), Column("c", Integer))

        e.execute(
            t.insert(),
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "c": 4},
                {"a": 3, "b": 4, "c": 5},
            ],
        )

    .. code-block::

        sqlalchemy.exc.StatementError: (sqlalchemy.exc.InvalidRequestError)
        A value is required for bind parameter 'b', in parameter group 1
        [SQL: u'INSERT INTO t (a, b, c) VALUES (?, ?, ?)']
        [parameters: [{'a': 1, 'c': 3, 'b': 2}, {'a': 2, 'c': 4}, {'a': 3, 'c': 5, 'b': 4}]]

    Since "b" is required, pass it as ``None`` so that the INSERT may proceed::

        e.execute(
            t.insert(),
            [
                {"a": 1, "b": 2, "c": 3},
                {"a": 2, "b": None, "c": 4},
                {"a": 3, "b": 4, "c": 5},
            ],
        )

    .. seealso::

        :ref:`tutorial_sending_parameters`

.. _error_89ve:

预期为 FROM 子句，得到 Select。要创建 FROM 子句，请使用 .subquery() 方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Expected FROM clause, got Select.  To create a FROM clause, use the .subquery() method

.. tab:: 中文

    这是从 SQLAlchemy 1.4 开始引入的一个变更，指的是通过 :func:`_expression.select` 等函数生成的 SELECT 语句（包括 union 和文本形式的 SELECT 表达式）不再被视为 :class:`_expression.FromClause` 对象，不能再直接放入另一个 SELECT 语句的 FROM 子句中，除非先将其包装为一个 :class:`.Subquery` 对象。这是 SQLAlchemy Core 中的一个重要概念变更，完整的原由可参考 :ref:`change_4617`。

    以下示例中::

        m = MetaData()
        t = Table("t", m, Column("a", Integer), Column("b", Integer), Column("c", Integer))
        stmt = select(t)

    上述 ``stmt`` 表示一个 SELECT 语句。当我们尝试将 ``stmt`` 直接用作另一个 SELECT 的 FROM 子句时，就会触发错误，例如::

        new_stmt_1 = select(stmt)

    或用于 JOIN 中的 FROM 子句::

        new_stmt_2 = select(some_table).select_from(some_table.join(stmt))

    在旧版本的 SQLAlchemy 中，在另一个 SELECT 中嵌套 SELECT 会自动生成一个加括号的匿名子查询。然而，在大多数情况下，这种 SQL 形式并不实用，因为像 MySQL 和 PostgreSQL 等数据库要求 FROM 子句中的子查询必须具名（即具备别名）。因此必须使用 :meth:`_expression.SelectBase.alias` 方法或从 1.4 开始推荐使用的 :meth:`_expression.SelectBase.subquery` 方法。

    在其他数据库中，虽然可能不强制要求别名，但为子查询命名仍有助于避免后续引用子查询中的列名时产生歧义。

    除了上述实际原因外，还有许多 SQLAlchemy 相关的架构理由促成了这一更改。因此，正确的写法应使用 :meth:`_expression.SelectBase.subquery`，如下所示::

        subq = stmt.subquery()

        new_stmt_1 = select(subq)

        new_stmt_2 = select(some_table).select_from(some_table.join(subq))

    .. seealso::

        :ref:`change_4617`

.. tab:: 英文

    This refers to a change made as of SQLAlchemy 1.4 where a SELECT statement as generated
    by a function such as :func:`_expression.select`, but also including things like unions and textual
    SELECT expressions are no longer considered to be :class:`_expression.FromClause` objects and
    can't be placed directly in the FROM clause of another SELECT statement without them
    being wrapped in a :class:`.Subquery` first.   This is a major conceptual change in the
    Core and the full rationale is discussed at :ref:`change_4617`.
    
    Given an example as::
    
        m = MetaData()
        t = Table("t", m, Column("a", Integer), Column("b", Integer), Column("c", Integer))
        stmt = select(t)
    
    Above, ``stmt`` represents a SELECT statement.  The error is produced when we want
    to use ``stmt`` directly as a FROM clause in another SELECT, such as if we
    attempted to select from it::
    
        new_stmt_1 = select(stmt)
    
    Or if we wanted to use it in a FROM clause such as in a JOIN::
    
        new_stmt_2 = select(some_table).select_from(some_table.join(stmt))
    
    In previous versions of SQLAlchemy, using a SELECT inside of another SELECT
    would produce a parenthesized, unnamed subquery.   In most cases, this form of
    SQL is not very useful as databases like MySQL and PostgreSQL require that
    subqueries in FROM clauses have named aliases, which means using the
    :meth:`_expression.SelectBase.alias` method or as of 1.4 using the
    :meth:`_expression.SelectBase.subquery` method to produce this.   On other databases, it
    is still much clearer for the subquery to have a name to resolve any ambiguity
    on future references to column  names inside the subquery.
    
    Beyond the above practical reasons, there are a lot of other SQLAlchemy-oriented
    reasons the change is being made.  The correct form of the above two statements
    therefore requires that :meth:`_expression.SelectBase.subquery` is used::
    
        subq = stmt.subquery()
    
        new_stmt_1 = select(subq)
    
        new_stmt_2 = select(some_table).select_from(some_table.join(subq))
    
    .. seealso::
    
        :ref:`change_4617`

.. _error_xaj1:

正在为原始子句元素自动生成别名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alias is being generated automatically for raw clauseelement

.. versionadded:: 1.4.26

.. tab:: 中文

    该弃用警告涉及一种非常古老且鲜为人知的模式，适用于传统的 :meth:`_orm.Query.join` 方法以及 :term:`2.0 style` 中的 :meth:`_sql.Select.join` 方法，其中 JOIN 是基于 :func:`_orm.relationship` 定义的，但目标是 :class:`_schema.Table` 或其他 Core 可选对象，而不是映射类或 :func:`_orm.aliased` 构造。例如::

        a1 = Address.__table__

        q = (
            s.query(User)
            .join(a1, User.addresses)
            .filter(Address.email_address == "ed@foo.com")
            .all()
        )

    上述模式也适用于任意 Core 选择对象，如 :class:`_sql.Join` 或 :class:`_sql.Alias` 对象，但这些对象不会被自动适配，因此必须显式引用 Core 对象::

        a1 = Address.__table__.alias()

        q = (
            s.query(User)
            .join(a1, User.addresses)
            .filter(a1.c.email_address == "ed@foo.com")
            .all()
        )

    更正确的做法是始终使用映射类本身，或使用 :class:`_orm.aliased` 对象，并通过 :meth:`_orm.PropComparator.of_type` 修饰器设置别名::

        # 正常的实体关系连接
        q = s.query(User).join(User.addresses).filter(Address.email_address == "ed@foo.com")

        # 显式指定 Address 目标（不是必须，但合法）
        q = (
            s.query(User)
            .join(Address, User.addresses)
            .filter(Address.email_address == "ed@foo.com")
        )

    连接到别名::

        from sqlalchemy.orm import aliased

        a1 = aliased(Address)

        # 推荐的 of_type() 形式
        q = (
            s.query(User)
            .join(User.addresses.of_type(a1))
            .filter(a1.email_address == "ed@foo.com")
        )

        # 目标 + onclause 形式
        q = s.query(User).join(a1, User.addresses).filter(a1.email_address == "ed@foo.com")

.. tab:: 英文


    This deprecation warning refers to a very old and likely not well known pattern
    that applies to the legacy :meth:`_orm.Query.join` method as well as the
    :term:`2.0 style` :meth:`_sql.Select.join` method, where a join can be stated
    in terms of a :func:`_orm.relationship` but the target is the
    :class:`_schema.Table` or other Core selectable to which the class is mapped,
    rather than an ORM entity such as a mapped class or :func:`_orm.aliased`
    construct::

        a1 = Address.__table__

        q = (
            s.query(User)
            .join(a1, User.addresses)
            .filter(Address.email_address == "ed@foo.com")
            .all()
        )

    The above pattern also allows an arbitrary selectable, such as
    a Core :class:`_sql.Join` or :class:`_sql.Alias` object,
    however there is no automatic adaptation of this element, meaning the
    Core element would need to be referenced directly::

        a1 = Address.__table__.alias()

        q = (
            s.query(User)
            .join(a1, User.addresses)
            .filter(a1.c.email_address == "ed@foo.com")
            .all()
        )

    The correct way to specify a join target is always by using the mapped
    class itself or an :class:`_orm.aliased` object, in the latter case using the
    :meth:`_orm.PropComparator.of_type` modifier to set up an alias::

        # normal join to relationship entity
        q = s.query(User).join(User.addresses).filter(Address.email_address == "ed@foo.com")

        # name Address target explicitly, not necessary but legal
        q = (
            s.query(User)
            .join(Address, User.addresses)
            .filter(Address.email_address == "ed@foo.com")
        )

    Join to an alias::

        from sqlalchemy.orm import aliased

        a1 = aliased(Address)

        # of_type() form; recommended
        q = (
            s.query(User)
            .join(User.addresses.of_type(a1))
            .filter(a1.email_address == "ed@foo.com")
        )

        # target, onclause form
        q = s.query(User).join(a1, User.addresses).filter(a1.email_address == "ed@foo.com")

.. _error_xaj2:

由于表格重叠，正在自动生成别名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alias is being generated automatically due to overlapping tables

.. versionadded:: 1.4.26

.. tab:: 中文

    该警告通常在使用 :meth:`_sql.Select.join` 或传统 :meth:`_orm.Query.join` 进行联接操作，并且涉及了联合表继承（joined table inheritance）映射时产生。问题在于，当两个使用了联合继承的模型共享同一基础表，并尝试相互联接时，无法直接构建出正确的 SQL JOIN，除非对其中一方应用别名。SQLAlchemy 默认会为 JOIN 的右侧应用别名。

    例如，定义如下联合继承结构::

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            manager_id = Column(ForeignKey("manager.id"))
            name = Column(String(50))
            type = Column(String(50))

            reports_to = relationship("Manager", foreign_keys=manager_id)

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "inherit_condition": id == Employee.id,
            }

    以上映射表示 ``Employee`` 和 ``Manager`` 之间存在关系，并且两者都映射到同一个 ``employee`` 数据表。从 SQL 层面看，这是一个 :ref:`self referential relationship <self_referential>` （自引用关系）。若尝试将两个模型连接查询，在 SQL 中必须重复引用  ``employee`` 表，因此需要对其应用别名。

    若使用 ORM 执行此类 JOIN，生成的 SQL 类似于：

    .. sourcecode:: pycon+sql

        >>> stmt = select(Employee, Manager).join(Employee.reports_to)
        >>> print(stmt)
        {printsql}SELECT employee.id, employee.manager_id, employee.name,
        employee.type, manager_1.id AS id_1, employee_1.id AS id_2,
        employee_1.manager_id AS manager_id_1, employee_1.name AS name_1,
        employee_1.type AS type_1
        FROM employee JOIN
        (employee AS employee_1 JOIN manager AS manager_1 ON manager_1.id = employee_1.id)
        ON manager_1.id = employee.manager_id

    上述 SQL 中，初始的 ``employee`` 表用于 ``Employee`` 实体，接着通过右嵌套 JOIN 联接 ``employee AS employee_1 JOIN manager AS manager_1``，其中 ``employee`` 表第二次出现，并被命名为匿名别名 ``employee_1``。这就是警告所说的“自动别名生成”。

    当 ORM 加载同时包含 ``Employee`` 和 ``Manager`` 对象的行时，必须将来自 ``employee_1`` 和 ``manager_1`` 的别名行转换回未别名的 ``Manager`` 类实例。这个过程在内部非常复杂，不能兼容所有 API 功能，尤其是当使用如 :func:`_orm.contains_eager` 等预加载机制时，在更深层嵌套查询中可能会失败。

    由于这一模式在复杂场景下不可靠，并且涉及自动决策过程难以预测和调试，因此触发警告提示，此用法或将被视为遗留特性。更好的做法是使用与其他自引用关系相同的方式，通过显式的 :func:`_orm.aliased` 构造实现。

    对于联合继承及其他联接导向映射，建议同时使用 :paramref:`_orm.aliased.flat` 参数，这样可以在不嵌套 JOIN 子查询的情况下，将 JOIN 中的每个表分别应用别名：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import aliased
        >>> manager_alias = aliased(Manager, flat=True)
        >>> stmt = select(Employee, manager_alias).join(Employee.reports_to.of_type(manager_alias))
        >>> print(stmt)
        {printsql}SELECT employee.id, employee.manager_id, employee.name,
        employee.type, manager_1.id AS id_1, employee_1.id AS id_2,
        employee_1.manager_id AS manager_id_1, employee_1.name AS name_1,
        employee_1.type AS type_1
        FROM employee JOIN
        (employee AS employee_1 JOIN manager AS manager_1 ON manager_1.id = employee_1.id)
        ON manager_1.id = employee.manager_id

    如果我们还希望使用 :func:`_orm.contains_eager` 填充 ``reports_to`` 属性，可以这样引用别名::

        >>> stmt = (
        ...     select(Employee)
        ...     .join(Employee.reports_to.of_type(manager_alias))
        ...     .options(contains_eager(Employee.reports_to.of_type(manager_alias)))
        ... )

    如果不使用显式的 :func:`_orm.aliased` 对象，在某些更深嵌套的场景中，:func:`_orm.contains_eager` 可能因缺乏上下文而无法正确加载关联数据，尤其是在 ORM 自动别名机制介入时。因此，推荐始终使用显式 SQL 构造来避免不确定行为。

.. tab:: 英文

    This warning is typically generated when querying using the
    :meth:`_sql.Select.join` method or the legacy :meth:`_orm.Query.join` method
    with mappings that involve joined table inheritance. The issue is that when
    joining between two joined inheritance models that share a common base table, a
    proper SQL JOIN between the two entities cannot be formed without applying an
    alias to one side or the other; SQLAlchemy applies an alias to the right side
    of the join. For example given a joined inheritance mapping as::

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            manager_id = Column(ForeignKey("manager.id"))
            name = Column(String(50))
            type = Column(String(50))

            reports_to = relationship("Manager", foreign_keys=manager_id)

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "inherit_condition": id == Employee.id,
            }

    The above mapping includes a relationship between the ``Employee`` and
    ``Manager`` classes.  Since both classes make use of the "employee" database
    table, from a SQL perspective this is a
    :ref:`self referential relationship <self_referential>`.  If we wanted to
    query from both the ``Employee`` and ``Manager`` models using a join, at the
    SQL level the "employee" table needs to be included twice in the query, which
    means it must be aliased.   When we create such a join using the SQLAlchemy
    ORM, we get SQL that looks like the following:

    .. sourcecode:: pycon+sql

        >>> stmt = select(Employee, Manager).join(Employee.reports_to)
        >>> print(stmt)
        {printsql}SELECT employee.id, employee.manager_id, employee.name,
        employee.type, manager_1.id AS id_1, employee_1.id AS id_2,
        employee_1.manager_id AS manager_id_1, employee_1.name AS name_1,
        employee_1.type AS type_1
        FROM employee JOIN
        (employee AS employee_1 JOIN manager AS manager_1 ON manager_1.id = employee_1.id)
        ON manager_1.id = employee.manager_id

    Above, the SQL selects FROM the ``employee`` table, representing the
    ``Employee`` entity in the query. It then joins to a right-nested join of
    ``employee AS employee_1 JOIN manager AS manager_1``, where the ``employee``
    table is stated again, except as an anonymous alias ``employee_1``. This is the
    'automatic generation of an alias' to which the warning message refers.

    When SQLAlchemy loads ORM rows that each contain an ``Employee`` and a
    ``Manager`` object, the ORM must adapt rows from what above is the
    ``employee_1`` and ``manager_1`` table aliases into those of the un-aliased
    ``Manager`` class. This process is internally complex and does not accommodate
    for all API features, notably when trying to use eager loading features such as
    :func:`_orm.contains_eager` with more deeply nested queries than are shown
    here.  As the pattern is unreliable for more complex scenarios and involves
    implicit decisionmaking that is difficult to anticipate and follow,
    the warning is emitted and this pattern may be considered a legacy feature. The
    better way to write this query is to use the same patterns that apply to any
    other self-referential relationship, which is to use the :func:`_orm.aliased`
    construct explicitly.  For joined-inheritance and other join-oriented mappings,
    it is usually desirable to add the use of the :paramref:`_orm.aliased.flat`
    parameter, which will allow a JOIN of two or more tables to be aliased by
    applying an alias to the individual tables within the join, rather than
    embedding the join into a new subquery:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import aliased
        >>> manager_alias = aliased(Manager, flat=True)
        >>> stmt = select(Employee, manager_alias).join(Employee.reports_to.of_type(manager_alias))
        >>> print(stmt)
        {printsql}SELECT employee.id, employee.manager_id, employee.name,
        employee.type, manager_1.id AS id_1, employee_1.id AS id_2,
        employee_1.manager_id AS manager_id_1, employee_1.name AS name_1,
        employee_1.type AS type_1
        FROM employee JOIN
        (employee AS employee_1 JOIN manager AS manager_1 ON manager_1.id = employee_1.id)
        ON manager_1.id = employee.manager_id

    If we then wanted to use :func:`_orm.contains_eager` to populate the
    ``reports_to`` attribute, we refer to the alias::

        >>> stmt = (
        ...     select(Employee)
        ...     .join(Employee.reports_to.of_type(manager_alias))
        ...     .options(contains_eager(Employee.reports_to.of_type(manager_alias)))
        ... )

    Without using the explicit :func:`_orm.aliased` object, in some more nested
    cases the :func:`_orm.contains_eager` option does not have enough context to
    know where to get its data from, in the case that the ORM is "auto-aliasing"
    in a very nested context.  Therefore it's best not to rely on this feature
    and instead keep the SQL construction as explicit as possible.


对象关系映射
-------------------------

Object Relational Mapping

.. _error_isce:

IllegalStateChangeError 和并发异常
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

IllegalStateChangeError and concurrency exceptions

.. tab:: 中文

    SQLAlchemy 2.0 引入了一个新系统，如 :ref:`change_7433` 所描述的，它可以主动检测在单个 :class:`_orm.Session` 实例上调用的并发方法，以及继承自 :class:`_asyncio.AsyncSession` 的代理对象。这些并发访问调用通常会发生在多个并发线程共享同一个 :class:`_orm.Session` 实例，且没有进行同步访问，或者类似地，在多个并发任务（例如使用 `asyncio.gather()` 函数时）共享同一个 :class:`_asyncio.AsyncSession` 实例时。这些使用模式并不是这些对象的正确用法，如果没有 SQLAlchemy 实施的主动警告系统，仍然可能在对象内部产生无效状态，导致难以调试的错误，包括数据库连接本身的驱动级错误。

    :class:`_orm.Session` 和 :class:`_asyncio.AsyncSession` 实例是 **可变的、有状态的对象，且没有内建的同步机制** ，它们代表了 **单个数据库连接上的单个正在进行的数据库事务** ，该连接与特定的 :class:`.Engine` 或 :class:`.AsyncEngine` 绑定（请注意，这些对象支持同时绑定到多个引擎，但在此情况下，每个引擎内的事务只会涉及一个连接）。单个数据库事务不适合并发执行 SQL 命令；因此，运行并发数据库操作的应用程序应该使用并发事务。因此，正确的模式是每个线程一个 :class:`_orm.Session`，每个任务一个 :class:`_asyncio.AsyncSession`。

    有关并发性的更多背景，请参见 :ref:`session_faq_threadsafe` 部分。

.. tab:: 英文

    SQLAlchemy 2.0 introduced a new system described at :ref:`change_7433`, which
    proactively detects concurrent methods being invoked on an individual instance of
    the :class:`_orm.Session`
    object and by extension the :class:`_asyncio.AsyncSession` proxy object.
    These concurrent access calls typically, though not exclusively, would occur
    when a single instance of :class:`_orm.Session` is shared among multiple
    concurrent threads without such access being synchronized, or similarly
    when a single instance of :class:`_asyncio.AsyncSession` is shared among
    multiple concurrent tasks (such as when using a function like ``asyncio.gather()``).
    These use patterns are not the appropriate use of these objects, where without
    the proactive warning system SQLAlchemy implements would still otherwise produce
    invalid state within the objects, producing hard-to-debug errors including
    driver-level errors on the database connections themselves.

    Instances of :class:`_orm.Session` and :class:`_asyncio.AsyncSession` are
    **mutable, stateful objects with no built-in synchronization** of method calls,
    and represent a **single, ongoing database transaction** upon a single database
    connection at a time for a particular :class:`.Engine` or :class:`.AsyncEngine`
    to which the object is bound (note that these objects both support being bound
    to multiple engines at once, however in this case there will still be only one
    connection per engine in play within the scope of a transaction).  A single
    database transaction is not an appropriate target for concurrent SQL commands;
    instead, an application that runs concurrent database operations should use
    concurrent transactions. For these objects then it follows that the appropriate
    pattern is :class:`_orm.Session` per thread, or :class:`_asyncio.AsyncSession`
    per task.

    For more background on concurrency see the section
    :ref:`session_faq_threadsafe`.


.. _error_bhk3:

父实例 <x> 未绑定到会话；（延迟加载/延迟加载/刷新/等）操作无法继续
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parent instance <x> is not bound to a Session; (lazy load/deferred load/refresh/etc.) operation cannot proceed

.. tab:: 中文
    
    这是使用 ORM 时最常见的错误消息，通常由 ORM 广泛使用的技术引起，这种技术被称为 :term:`lazy loading`（延迟加载）。延迟加载是一种常见的对象关系映射模式，其中一个由 ORM 持久化的对象维持一个数据库的代理，以便在访问对象的各种属性时，属性的值可以被“懒加载”出来。此方法的优势在于对象可以从数据库中检索，而无需一次加载所有属性或相关数据，而是仅在需要时加载那些数据。然而，主要的缺点恰恰是优势的镜像，即如果加载大量已知在所有情况下都需要某些数据的对象，则逐步加载额外的数据会导致浪费。
    
    延迟加载的另一个警告是，为了进行延迟加载，对象必须 **保持与一个 Session 的关联**，才能从数据库中检索其状态。此错误消息意味着对象已经与其 :class:`.Session` 断开关联，并被要求从数据库中延迟加载数据。
    
    对象与 :class:`.Session` 断开关联的最常见原因是 session 本身已经关闭，通常是通过 :meth:`.Session.close` 方法关闭的。然后这些对象会继续存在并被进一步访问，通常出现在 Web 应用程序中，当它们被传递给服务器端模板引擎时，要求进一步访问其无法加载的属性。
    
    减轻此错误的方法包括以下技术：
    
    * **尽量避免使用断开关联的对象；不要过早关闭 session** - 通常，应用程序会在将相关对象传递给其他系统之前关闭事务，这样就会导致错误。有时事务不需要那么早关闭；例如，在 Web 应用程序中，事务在视图渲染之前就关闭了。这通常是为了“正确性”，但可能被视为对“封装”的误应用，因为这个术语指的是代码组织，而不是实际的操作。使用 ORM 对象的模板是采用 `proxy pattern <https://en.wikipedia.org/wiki/Proxy_pattern>`_，它将数据库逻辑与调用者分离。如果 :class:`.Session` 可以保持打开状态，直到对象的生命周期结束，这是最好的做法。
    
    * **否则，预先加载所有需要的数据** - 在更复杂的应用程序中，通常无法保持事务打开，特别是当对象需要传递给其他无法在同一上下文中运行的系统时。此时，应用程序应该准备好处理 :term:`detached`（脱离的）对象，并应尽量合理使用 :term:`eager loading`（急切加载），以确保对象在开始时就有它们需要的数据。
    
    * **并且，重要的是，将 expire_on_commit 设置为 False** - 在处理脱离的对象时，最常见的需要重新加载数据的原因是对象在上次调用 :meth:`_orm.Session.commit` 时被过期了。在处理脱离的对象时，不应使用此过期机制；因此，应该将 :paramref:`_orm.Session.expire_on_commit` 参数设置为 ``False``。通过防止对象在事务外过期，已加载的数据将保持存在，并且在访问这些数据时不会触发额外的延迟加载。
    
      还需要注意的是，:meth:`_orm.Session.rollback` 方法会无条件地过期 :class:`_orm.Session` 中的所有内容，应该避免在非错误情况下使用。
    
      .. seealso::
    
        :ref:`loading_toplevel` - 详细的急切加载和其他关系加载技术文档
    
        :ref:`session_committing` - 会话提交的背景
    
        :ref:`session_expire` - 属性过期的背景

.. tab:: 英文

    This is likely the most common error message when dealing with the ORM, and it
    occurs as a result of the nature of a technique the ORM makes wide use of known
    as :term:`lazy loading`.   Lazy loading is a common object-relational pattern
    whereby an object that's persisted by the ORM maintains a proxy to the database
    itself, such that when various attributes upon the object are accessed, their
    value may be retrieved from the database *lazily*.   The advantage to this
    approach is that objects can be retrieved from the database without having
    to load all of their attributes or related data at once, and instead only that
    data which is requested can be delivered at that time.   The major disadvantage
    is basically a mirror image of the advantage, which is that if lots of objects
    are being loaded which are known to require a certain set of data in all cases,
    it is wasteful to load that additional data piecemeal.
    
    Another caveat of lazy loading beyond the usual efficiency concerns is that
    in order for lazy loading to proceed, the object has to **remain associated
    with a Session** in order to be able to retrieve its state.  This error message
    means that an object has become de-associated with its :class:`.Session` and
    is being asked to lazy load data from the database.
    
    The most common reason that objects become detached from their :class:`.Session`
    is that the session itself was closed, typically via the :meth:`.Session.close`
    method.   The objects will then live on to be accessed further, very often
    within web applications where they are delivered to a server-side templating
    engine and are asked for further attributes which they cannot load.
    
    Mitigation of this error is via these techniques:
    
    * **Try not to have detached objects; don't close the session prematurely** - Often, applications will close
      out a transaction before passing off related objects to some other system
      which then fails due to this error.   Sometimes the transaction doesn't need
      to be closed so soon; an example is the web application closes out
      the transaction before the view is rendered.  This is often done in the name
      of "correctness", but may be seen as a mis-application of "encapsulation",
      as this term refers to code organization, not actual actions. The template that
      uses an ORM object is making use of the `proxy pattern <https://en.wikipedia.org/wiki/Proxy_pattern>`_
      which keeps database logic encapsulated from the caller.   If the
      :class:`.Session` can be held open until the lifespan of the objects are done,
      this is the best approach.
    
    * **Otherwise, load everything that's needed up front** - It is very often impossible to
      keep the transaction open, especially in more complex applications that need
      to pass objects off to other systems that can't run in the same context
      even though they're in the same process.  In this case, the application
      should prepare to deal with :term:`detached` objects,
      and should try to make appropriate use of :term:`eager loading` to ensure
      that objects have what they need up front.
    
    * **And importantly, set expire_on_commit to False** - When using detached objects, the
      most common reason objects need to re-load data is because they were expired
      from the last call to :meth:`_orm.Session.commit`.   This expiration should
      not be used when dealing with detached objects; so the
      :paramref:`_orm.Session.expire_on_commit` parameter be set to ``False``.
      By preventing the objects from becoming expired outside of the transaction,
      the data which was loaded will remain present and will not incur additional
      lazy loads when that data is accessed.
    
      Note also that :meth:`_orm.Session.rollback` method unconditionally expires
      all contents in the :class:`_orm.Session` and should also be avoided in
      non-error scenarios.
    
      .. seealso::
    
        :ref:`loading_toplevel` - detailed documentation on eager loading and other
        relationship-oriented loading techniques
    
        :ref:`session_committing` - background on session commit
    
        :ref:`session_expire` - background on attribute expiry


.. _error_7s2a:

由于刷新期间发生先前的异常，此会话的事务已被回滚
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Session's transaction has been rolled back due to a previous exception during flush

.. tab:: 中文

    :class:`.Session` 的刷新过程，如 :ref:`session_flushing` 所描述的，将在遇到错误时回滚数据库事务，以保持内部一致性。然而，一旦发生这种情况，session 的事务就变为“非活动”状态，必须由调用应用程序显式回滚，就像在没有发生错误的情况下需要显式提交一样。

    这是使用 ORM 时常见的错误，通常适用于尚未正确“框架化”其 :class:`.Session` 操作的应用程序。更多详细信息请参见 FAQ 中的 :ref:`faq_session_rollback`。

.. tab:: 英文

    The flush process of the :class:`.Session`, described at
    :ref:`session_flushing`, will roll back the database transaction if an error is
    encountered, in order to maintain internal consistency.  However, once this
    occurs, the session's transaction is now "inactive" and must be explicitly
    rolled back by the calling application, in the same way that it would otherwise
    need to be explicitly committed if a failure had not occurred.

    This is a common error when using the ORM and typically applies to an
    application that doesn't yet have correct "framing" around its
    :class:`.Session` operations. Further detail is described in the FAQ at
    :ref:`faq_session_rollback`.

.. _error_bbf0:

对于关系 <relationship>，delete-orphan 级联通常仅配置在一对多关系的“一”侧，而不是多对一或多对多关系的“多”侧。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For relationship <relationship>, delete-orphan cascade is normally configured only on the "one" side of a one-to-many relationship, and not on the "many" side of a many-to-one or many-to-many relationship.

.. tab:: 中文

    当在多对一或多对多关系上设置了 "delete-orphan" :ref:`cascade <unitofwork_cascades>` 时，可能会引发以下错误::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            # 这将在映射配置步骤时触发错误消息
            a = relationship("A", back_populates="bs", cascade="all, delete-orphan")


        configure_mappers()

    在上述代码中， ``B.a`` 上的 "delete-orphan" 设置表明，当每个指向特定 ``A`` 的 ``B`` 对象被删除时， ``A`` 应该也会被删除。也就是说，它表达了“孤儿”对象应该是 ``A`` 对象，当每个指向它的 ``B`` 被删除时， ``A`` 成为“孤儿”。

    然而， “delete-orphan” 级联模型并不支持这种功能。它只会考虑通过删除单个对象来产生孤儿的情况，这样一个对象会变成孤儿，并且与之相关的对象也会被删除。换句话说，它的设计是只跟踪每个孤儿的创建，基于删除一个且仅一个“父”对象的情况，这在一对多关系中是自然的，删除“一方”的对象会导致相关的“多方”对象被删除。

    为了实现上述功能，级联设置应该放在一对多关系的“一方”上，如下所示::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a", cascade="all, delete-orphan")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship("A", back_populates="bs")

    在这种情况下，意图是当 ``A`` 被删除时，所有与之关联的 ``B`` 对象也会被删除。

    接下来，错误消息还建议使用 :paramref:`_orm.relationship.single_parent` 标志。此标志可用于强制规定，虽然数据库外键关系暗示多个对象可能会引用某个对象，但在实际应用中一次只能有一个对象引用该目标对象。这种不常见的情况可以通过以下示例来演示::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship(
                "A",
                back_populates="bs",
                single_parent=True,
                cascade="all, delete-orphan",
            )

    上述配置将安装一个验证器，强制确保每次只能有一个 ``B`` 对象与 ``A`` 关联，且该关系是唯一的::

        >>> b1 = B()
        >>> b2 = B()
        >>> a1 = A()
        >>> b1.a = a1
        >>> b2.a = a1
        sqlalchemy.exc.InvalidRequestError: Instance <A at 0x7eff44359350> is
        already associated with an instance of <class '__main__.B'> via its
        B.a attribute, and is only allowed a single parent.

    需要注意的是，这个验证器的作用范围是有限的，它不会阻止通过另一方向创建多个“父对象”。例如，它不会检测 ``A.bs`` 中的设置::

        >>> a1.bs = [b1, b2]
        >>> session.add_all([a1, b1, b2])
        >>> session.commit()
        {execsql}
        INSERT INTO a DEFAULT VALUES
        ()
        INSERT INTO b (a_id) VALUES (?)
        (1,)
        INSERT INTO b (a_id) VALUES (?)
        (1,)

    但是稍后事情不会按预期进行，因为 "delete-orphan" 级联将继续作用于 **单一** 主对象。这意味着，如果删除 **任何** 一个 ``B`` 对象，``A`` 会被删除。另一个 ``B`` 会保留，ORM 通常会聪明地将外键属性设置为 NULL，但这通常不是所期望的::

        >>> session.delete(b1)
        >>> session.commit()
        {execsql}
        UPDATE b SET a_id=? WHERE b.id = ?
        (None, 2)
        DELETE FROM b WHERE b.id = ?
        (1,)
        DELETE FROM a WHERE a.id = ?
        (1,)
        COMMIT

    对于所有上述示例，类似的逻辑也适用于多对多关系；如果多对多关系在一侧设置了 ``single_parent=True``，则该侧可以使用 "delete-orphan" 级联，但这通常不是期望的行为，因为多对多关系的目的是使得可以在任一方向上有多个对象引用目标对象。

    总体而言，"delete-orphan" 级联通常应用于一对多关系的“一方”，以便删除“多方”对象，而不是反向操作。

    .. seealso::

        :ref:`unitofwork_cascades`

        :ref:`cascade_delete_orphan`

        :ref:`error_bbf1`

.. tab:: 英文


    This error arises when the "delete-orphan" :ref:`cascade <unitofwork_cascades>`
    is set on a many-to-one or many-to-many relationship, such as::


        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            # this will emit the error message when the mapper
            # configuration step occurs
            a = relationship("A", back_populates="bs", cascade="all, delete-orphan")


        configure_mappers()

    Above, the "delete-orphan" setting on ``B.a`` indicates the intent that
    when every ``B`` object that refers to a particular ``A`` is deleted, that the
    ``A`` should then be deleted as well.   That is, it expresses that the "orphan"
    which is being deleted would be an ``A`` object, and it becomes an "orphan"
    when every ``B`` that refers to it is deleted.

    The "delete-orphan" cascade model does not support this functionality.   The
    "orphan" consideration is only made in terms of the deletion of a single object
    which would then refer to zero or more objects that are now "orphaned" by
    this single deletion, which would result in those objects being deleted as
    well.  In other words, it is designed only to track the creation of "orphans"
    based on the removal of one and only one "parent" object per orphan,  which is
    the natural case in a one-to-many relationship where a deletion of the
    object on the "one" side results in the subsequent deletion of the related
    items on the "many" side.

    The above mapping in support of this functionality would instead place the
    cascade setting on the one-to-many side, which looks like::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a", cascade="all, delete-orphan")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship("A", back_populates="bs")

    Where the intent is expressed that when an ``A`` is deleted, all of the
    ``B`` objects to which it refers are also deleted.

    The error message then goes on to suggest the usage of the
    :paramref:`_orm.relationship.single_parent` flag.    This flag may be used
    to enforce that a relationship which is capable of having many objects
    refer to a particular object will in fact have only **one** object referring
    to it at a time.   It is used for legacy or other less ideal
    database schemas where the foreign key relationships suggest a "many"
    collection, however in practice only one object would actually refer
    to a given target object at at time.  This uncommon scenario
    can be demonstrated in terms of the above example as follows::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)

            bs = relationship("B", back_populates="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship(
                "A",
                back_populates="bs",
                single_parent=True,
                cascade="all, delete-orphan",
            )

    The above configuration will then install a validator which will enforce
    that only one ``B`` may be associated with an ``A`` at at time, within
    the scope of the ``B.a`` relationship::

        >>> b1 = B()
        >>> b2 = B()
        >>> a1 = A()
        >>> b1.a = a1
        >>> b2.a = a1
        sqlalchemy.exc.InvalidRequestError: Instance <A at 0x7eff44359350> is
        already associated with an instance of <class '__main__.B'> via its
        B.a attribute, and is only allowed a single parent.

    Note that this validator is of limited scope and will not prevent multiple
    "parents" from being created via the other direction.  For example, it will
    not detect the same setting in terms of ``A.bs``:

    .. sourcecode:: pycon+sql

        >>> a1.bs = [b1, b2]
        >>> session.add_all([a1, b1, b2])
        >>> session.commit()
        {execsql}
        INSERT INTO a DEFAULT VALUES
        ()
        INSERT INTO b (a_id) VALUES (?)
        (1,)
        INSERT INTO b (a_id) VALUES (?)
        (1,)

    However, things will not go as expected later on, as the "delete-orphan" cascade
    will continue to work in terms of a **single** lead object, meaning if we
    delete **either** of the ``B`` objects, the ``A`` is deleted.   The other ``B`` stays
    around, where the ORM will usually be smart enough to set the foreign key attribute
    to NULL, but this is usually not what's desired:

    .. sourcecode:: pycon+sql

        >>> session.delete(b1)
        >>> session.commit()
        {execsql}
        UPDATE b SET a_id=? WHERE b.id = ?
        (None, 2)
        DELETE FROM b WHERE b.id = ?
        (1,)
        DELETE FROM a WHERE a.id = ?
        (1,)
        COMMIT

    For all the above examples, similar logic applies to the calculus of a
    many-to-many relationship; if a many-to-many relationship sets single_parent=True
    on one side, that side can use the "delete-orphan" cascade, however this is
    very unlikely to be what someone actually wants as the point of a many-to-many
    relationship is so that there can be many objects referring to an object
    in either direction.

    Overall, "delete-orphan" cascade is usually applied
    on the "one" side of a one-to-many relationship so that it deletes objects
    in the "many" side, and not the other way around.

    .. seealso::

        :ref:`unitofwork_cascades`

        :ref:`cascade_delete_orphan`

        :ref:`error_bbf1`



.. _error_bbf1:

实例 <instance> 已通过其 <attribute> 属性与 <instance> 的一个实例关联，并且只允许有一个父级。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instance <instance> is already associated with an instance of <instance> via its <attribute> attribute, and is only allowed a single parent.

.. tab:: 中文

    此错误会在使用 :paramref:`_orm.relationship.single_parent` 标志时发生，并且一次有多个对象被分配为一个对象的“父对象”。

    给定以下映射::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship(
                "A",
                single_parent=True,
                cascade="all, delete-orphan",
            )

    意图是每个 ``A`` 对象只能有一个 ``B`` 对象::

        >>> b1 = B()
        >>> b2 = B()
        >>> a1 = A()
        >>> b1.a = a1
        >>> b2.a = a1
        sqlalchemy.exc.InvalidRequestError: Instance <A at 0x7eff44359350> is
        already associated with an instance of <class '__main__.B'> via its
        B.a attribute, and is only allowed a single parent.

    当此错误意外发生时，通常是因为 :paramref:`_orm.relationship.single_parent` 标志是响应 :ref:`error_bbf0` 中描述的错误消息而应用的，问题实际上是对 "delete-orphan" 级联设置的误解。有关更多详细信息，请参阅该消息。

    .. seealso::

        :ref:`error_bbf0`

.. tab:: 英文


    This error is emitted when the :paramref:`_orm.relationship.single_parent` flag
    is used, and more than one object is assigned as the "parent" of an object at
    once.

    Given the following mapping::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))

            a = relationship(
                "A",
                single_parent=True,
                cascade="all, delete-orphan",
            )

    The intent indicates that no more than a single ``B`` object may refer
    to a particular ``A`` object at once::

        >>> b1 = B()
        >>> b2 = B()
        >>> a1 = A()
        >>> b1.a = a1
        >>> b2.a = a1
        sqlalchemy.exc.InvalidRequestError: Instance <A at 0x7eff44359350> is
        already associated with an instance of <class '__main__.B'> via its
        B.a attribute, and is only allowed a single parent.

    When this error occurs unexpectedly, it is usually because the
    :paramref:`_orm.relationship.single_parent` flag was applied in response
    to the error message described at :ref:`error_bbf0`, and the issue is in
    fact a misunderstanding of the "delete-orphan" cascade setting.  See that
    message for details.


    .. seealso::

        :ref:`error_bbf0`


.. _error_qzyx:

关系 X 将把 Q 列复制到 P 列，这与关系“Y”相冲突
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

relationship X will copy column Q to column P, which conflicts with relationship(s): 'Y'

.. tab:: 中文

    这个警告指的是当两个或更多关系在刷新时会写入相同的列，但 ORM 没有任何方式来协调这些关系时的情况。根据具体情况，解决方案可能是需要通过 :paramref:`_orm.relationship.back_populates` 使两个关系相互引用，或者一个或多个关系应该配置为 :paramref:`_orm.relationship.viewonly` 以防止冲突写入，或者有时配置是完全故意的，并应配置 :paramref:`_orm.relationship.overlaps` 来消除每个警告。

    对于缺少 :paramref:`_orm.relationship.back_populates` 的典型示例，给定以下映射::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            children = relationship("Child")

        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))
            parent = relationship("Parent")

    上面的映射将生成警告::

        SAWarning: relationship 'Child.parent' will copy column parent.id to column child.parent_id,
        which conflicts with relationship(s): 'Parent.children' (copies parent.id to child.parent_id).

    关系 ``Child.parent`` 和 ``Parent.children`` 看起来存在冲突。解决方案是应用 :paramref:`_orm.relationship.back_populates`::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            children = relationship("Child", back_populates="parent")

        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))
            parent = relationship("Parent", back_populates="children")

    对于可能故意存在的“重叠”情况，且无法解决的自定义关系， :paramref:`_orm.relationship.overlaps` 参数可以指定不应触发警告的关系名称。这通常发生在两个或多个关系指向同一底层表，并且每个关系包含自定义的 :paramref:`_orm.relationship.primaryjoin` 条件，以限制每种情况下的相关项::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            c1 = relationship(
                "Child",
                primaryjoin="and_(Parent.id == Child.parent_id, Child.flag == 0)",
                backref="parent",
                overlaps="c2, parent",
            )
            c2 = relationship(
                "Child",
                primaryjoin="and_(Parent.id == Child.parent_id, Child.flag == 1)",
                overlaps="c1, parent",
            )

        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))
            flag = Column(Integer)

    在上面的例子中，ORM 会知道 ``Parent.c1``、``Parent.c2`` 和 ``Child.parent`` 之间的重叠是故意的。

.. tab:: 英文

    This warning refers to the case when two or more relationships will write data
    to the same columns on flush, but the ORM does not have any means of
    coordinating these relationships together. Depending on specifics, the solution
    may be that two relationships need to be referenced by one another using
    :paramref:`_orm.relationship.back_populates`, or that one or more of the
    relationships should be configured with :paramref:`_orm.relationship.viewonly`
    to prevent conflicting writes, or sometimes that the configuration is fully
    intentional and should configure :paramref:`_orm.relationship.overlaps` to
    silence each warning.

    For the typical example that's missing
    :paramref:`_orm.relationship.back_populates`, given the following mapping::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            children = relationship("Child")


        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))
            parent = relationship("Parent")

    The above mapping will generate warnings:

    .. sourcecode:: text

        SAWarning: relationship 'Child.parent' will copy column parent.id to column child.parent_id,
        which conflicts with relationship(s): 'Parent.children' (copies parent.id to child.parent_id).

    The relationships ``Child.parent`` and ``Parent.children`` appear to be in conflict.
    The solution is to apply :paramref:`_orm.relationship.back_populates`::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            children = relationship("Child", back_populates="parent")


        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))
            parent = relationship("Parent", back_populates="children")

    For more customized relationships where an "overlap" situation may be
    intentional and cannot be resolved, the :paramref:`_orm.relationship.overlaps`
    parameter may specify the names of relationships for which the warning should
    not take effect. This typically occurs for two or more relationships to the
    same underlying table that include custom
    :paramref:`_orm.relationship.primaryjoin` conditions that limit the related
    items in each case::

        class Parent(Base):
            __tablename__ = "parent"
            id = Column(Integer, primary_key=True)
            c1 = relationship(
                "Child",
                primaryjoin="and_(Parent.id == Child.parent_id, Child.flag == 0)",
                backref="parent",
                overlaps="c2, parent",
            )
            c2 = relationship(
                "Child",
                primaryjoin="and_(Parent.id == Child.parent_id, Child.flag == 1)",
                overlaps="c1, parent",
            )


        class Child(Base):
            __tablename__ = "child"
            id = Column(Integer, primary_key=True)
            parent_id = Column(ForeignKey("parent.id"))

            flag = Column(Integer)

    Above, the ORM will know that the overlap between ``Parent.c1``,
    ``Parent.c2`` and ``Child.parent`` is intentional.

.. _error_lkrp:

对象无法转换为“持久”状态，因为此身份映射不再有效。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Object cannot be converted to 'persistent' state, as this identity map is no longer valid.

.. versionadded:: 1.4.26

.. tab:: 中文

    此消息的添加是为了处理一种情况，即在源 :class:`_orm.Session` 已关闭或已调用其 :meth:`_orm.Session.expunge_all` 方法之后，迭代将返回 ORM 对象的 :class:`_result.Result` 对象。当 :class:`_orm.Session` 一次性移除所有对象时，该 :class:`_orm.Session` 使用的内部 :term:`identity map` 会被新的替换，原有的被丢弃。一个未消费且未缓冲的 :class:`_result.Result` 对象将内部保持对被丢弃的 identity map 的引用。因此，当消费 :class:`_result.Result` 时，所返回的对象无法与该 :class:`_orm.Session` 关联。这种安排是设计使然，因为通常不建议在事务上下文之外迭代未缓冲的 :class:`_result.Result` 对象::

        # 上下文管理器创建新 Session
        with Session(engine) as session_obj:
            result = sess.execute(select(User).where(User.id == 7))

        # 上下文管理器关闭，因此 session_obj 关闭，identity map 被替换

        # 迭代 result 对象时无法将对象与 Session 关联，抛出此错误。
        user = result.first()

    上述情况通常不会在使用 ``asyncio`` ORM 扩展时发生，因为当 :class:`.AsyncSession` 返回同步风格的 :class:`_result.Result` 时，结果在语句执行时已被预缓冲。这是为了允许二级预加载器在无需额外 ``await`` 调用的情况下调用。

    要在使用常规 :class:`_orm.Session` 的相同情况中像 ``asyncio`` 扩展一样预缓冲结果，可以按如下方式使用 ``prebuffer_rows`` 执行选项::

        # 上下文管理器创建新 Session
        with Session(engine) as session_obj:
            # 结果内部预取所有对象
            result = sess.execute(
                select(User).where(User.id == 7), execution_options={"prebuffer_rows": True}
            )

        # 上下文管理器关闭，因此 session_obj 关闭，identity map 被替换

        # 返回预缓冲的对象
        user = result.first()

        # 然而它们已与会话分离，且该会话已关闭
        assert inspect(user).detached
        assert inspect(user).session is None

    在上述情况下，所选的 ORM 对象完全在 ``session_obj`` 块内生成，与 ``session_obj`` 关联并缓冲在 :class:`_result.Result` 对象中供迭代使用。块外，``session_obj`` 被关闭并清除了这些 ORM 对象。迭代 :class:`_result.Result` 对象时，会返回这些 ORM 对象，但由于其源 :class:`_orm.Session` 已清除，它们将以 :term:`detached` 状态交付。

    .. note:: 
        
        上述“预缓冲”和“未缓冲”的 :class:`_result.Result` 对象指的是 ORM 将来自 :term:`DBAPI` 的原始数据库行转换为 ORM 对象的过程。这并不意味着底层的 ``cursor`` 对象本身（它表示来自 DBAPI 的待处理结果）是否被缓冲或未缓冲，因为这实际上是缓冲的较低层次。有关 ``cursor`` 结果缓冲的背景信息，请参见 :ref:`engine_stream_results` 部分。

.. tab:: 英文


    This message was added to accommodate for the case where a
    :class:`_result.Result` object that would yield ORM objects is iterated after
    the originating :class:`_orm.Session` has been closed, or otherwise had its
    :meth:`_orm.Session.expunge_all` method called. When a :class:`_orm.Session`
    expunges all objects at once, the internal :term:`identity map` used by that
    :class:`_orm.Session` is replaced with a new one, and the original one
    discarded. An unconsumed and unbuffered :class:`_result.Result` object will
    internally maintain a reference to that now-discarded identity map. Therefore,
    when the :class:`_result.Result` is consumed, the objects that would be yielded
    cannot be associated with that :class:`_orm.Session`. This arrangement is by
    design as it is generally not recommended to iterate an unbuffered
    :class:`_result.Result` object outside of the transactional context in which it
    was created::
    
        # context manager creates new Session
        with Session(engine) as session_obj:
            result = sess.execute(select(User).where(User.id == 7))
    
        # context manager is closed, so session_obj above is closed, identity
        # map is replaced
    
        # iterating the result object can't associate the object with the
        # Session, raises this error.
        user = result.first()
    
    The above situation typically will **not** occur when using the ``asyncio``
    ORM extension, as when :class:`.AsyncSession` returns a sync-style
    :class:`_result.Result`, the results have been pre-buffered when the statement
    was executed.  This is to allow secondary eager loaders to invoke without needing
    an additional ``await`` call.
    
    To pre-buffer results in the above situation using the regular
    :class:`_orm.Session` in the same way that the ``asyncio`` extension does it,
    the ``prebuffer_rows`` execution option may be used as follows::
    
        # context manager creates new Session
        with Session(engine) as session_obj:
            # result internally pre-fetches all objects
            result = sess.execute(
                select(User).where(User.id == 7), execution_options={"prebuffer_rows": True}
            )
    
        # context manager is closed, so session_obj above is closed, identity
        # map is replaced
    
        # pre-buffered objects are returned
        user = result.first()
    
        # however they are detached from the session, which has been closed
        assert inspect(user).detached
        assert inspect(user).session is None
    
    Above, the selected ORM objects are fully generated within the ``session_obj``
    block, associated with ``session_obj`` and buffered within the
    :class:`_result.Result` object for iteration. Outside the block,
    ``session_obj`` is closed and expunges these ORM objects. Iterating the
    :class:`_result.Result` object will yield those ORM objects, however as their
    originating :class:`_orm.Session` has expunged them, they will be delivered in
    the :term:`detached` state.
    
    .. note:: The above reference to a "pre-buffered" vs. "un-buffered"
       :class:`_result.Result` object refers to the process by which the ORM
       converts incoming raw database rows from the :term:`DBAPI` into ORM
       objects.  It does not imply whether or not the underlying ``cursor``
       object itself, which represents pending results from the DBAPI, is itself
       buffered or unbuffered, as this is essentially a lower layer of buffering.
       For background on buffering of the ``cursor`` results itself, see the
       section :ref:`engine_stream_results`.

.. _error_zlpr:

无法将类型注释解释为带注释的声明表形式
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Type annotation can't be interpreted for Annotated Declarative Table form

.. tab:: 中文

    SQLAlchemy 2.0 引入了一个新的 :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 声明系统，该系统在运行时通过 :pep:`484` 注解从类定义中派生 ORM 映射属性信息。此形式的要求是，所有 ORM 注解必须使用名为 :class:`_orm.Mapped` 的通用容器才能正确注解。包含显式 :pep:`484` 类型注解的遗留 SQLAlchemy 映射（例如使用遗留的 Mypy 扩展进行类型支持的映射）可能包含诸如 :func:`_orm.relationship` 之类的指令，但这些指令没有包括此通用容器。

    为了解决此问题，可以使用 ``__allow_unmapped__`` 布尔属性标记这些类，直到它们完全迁移到 2.0 语法。有关示例，请参见 :ref:`migration_20_step_six` 中的迁移说明。

    .. seealso::

        :ref:`migration_20_step_six` - 在 :ref:`migration_20_toplevel` 文档中

.. tab:: 英文

    SQLAlchemy 2.0 introduces a new
    :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` declarative
    system which derives ORM mapped attribute information from :pep:`484`
    annotations within class definitions at runtime. A requirement of this form is
    that all ORM annotations must make use of a generic container called
    :class:`_orm.Mapped` to be properly annotated. Legacy SQLAlchemy mappings which
    include explicit :pep:`484` typing annotations, such as those which use the
    legacy Mypy extension for typing support, may include
    directives such as those for :func:`_orm.relationship` that don't include this
    generic.

    To resolve, the classes may be marked with the ``__allow_unmapped__`` boolean
    attribute until they can be fully migrated to the 2.0 syntax. See the migration
    notes at :ref:`migration_20_step_six` for an example.

    .. seealso::

        :ref:`migration_20_step_six` - in the :ref:`migration_20_toplevel` document

.. _error_dcmx:

将 <cls> 转换为数据类时，属性源自非数据类的超类 <cls>。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When transforming <cls> to a dataclass, attribute(s) originate from superclass <cls> which is not a dataclass.

.. tab:: 中文

    当使用 SQLAlchemy ORM 映射数据类特性（如 :ref:`orm_declarative_native_dataclasses` 中所述）与任何非数据类的混入类或抽象基类一起使用时，会发生此警告，下面是一个示例::

        from __future__ import annotations

        import inspect
        from typing import Optional
        from uuid import uuid4

        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Mixin:
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)


        class Base(DeclarativeBase, MappedAsDataclass):
            pass


        class User(Base, Mixin):
            __tablename__ = "sys_user"

            uid: Mapped[str] = mapped_column(
                String(50), init=False, default_factory=uuid4, primary_key=True
            )
            username: Mapped[str] = mapped_column()
            email: Mapped[str] = mapped_column()

    在上面的代码中，由于 ``Mixin`` 本身没有从 :class:`_orm.MappedAsDataclass` 扩展，因此会生成以下警告：

        SADeprecationWarning: When transforming <class '__main__.User'> to a
        dataclass, attribute(s) "create_user", "update_user" originates from
        superclass <class
        '__main__.Mixin'>, which is not a dataclass. This usage is deprecated and
        will raise an error in SQLAlchemy 2.1. When declaring SQLAlchemy
        Declarative Dataclasses, ensure that all mixin classes and other
        superclasses which include attributes are also a subclass of
        MappedAsDataclass.

    修复方法是将 :class:`_orm.MappedAsDataclass` 添加到 ``Mixin`` 的签名中，如下所示::

        class Mixin(MappedAsDataclass):
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)

    Python 的 :pep:`681` 规范不支持在非数据类的父类上声明的属性；根据 Python 数据类的行为，这些字段会被忽略，如下所示::

        from dataclasses import dataclass
        from dataclasses import field
        import inspect
        from typing import Optional
        from uuid import uuid4


        class Mixin:
            create_user: int
            update_user: Optional[int] = field(default=None)


        @dataclass
        class User(Mixin):
            uid: str = field(init=False, default_factory=lambda: str(uuid4()))
            username: str
            password: str
            email: str

    在上面的代码中， ``User`` 类将不会在其构造函数中包含 ``create_user``，也不会尝试将 ``update_user`` 解释为数据类属性。这是因为 ``Mixin`` 不是数据类。

    SQLAlchemy 2.0 系列中的数据类特性未正确遵循这一行为；相反，非数据类混入类和父类上的属性被视为最终数据类配置的一部分。然而，像 Pyright 和 Mypy 这样的类型检查器不会将这些字段视为数据类构造函数的一部分，因为它们应该被忽略，依据 :pep:`681`。由于其存在性不明确，SQLAlchemy 2.1 将要求具有 SQLAlchemy 映射属性的混入类必须是数据类。

.. tab:: 英文

    This warning occurs when using the SQLAlchemy ORM Mapped Dataclasses feature
    described at :ref:`orm_declarative_native_dataclasses` in conjunction with
    any mixin class or abstract base that is not itself declared as a
    dataclass, such as in the example below::

        from __future__ import annotations

        import inspect
        from typing import Optional
        from uuid import uuid4

        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Mixin:
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)


        class Base(DeclarativeBase, MappedAsDataclass):
            pass


        class User(Base, Mixin):
            __tablename__ = "sys_user"

            uid: Mapped[str] = mapped_column(
                String(50), init=False, default_factory=uuid4, primary_key=True
            )
            username: Mapped[str] = mapped_column()
            email: Mapped[str] = mapped_column()

    Above, since ``Mixin`` does not itself extend from :class:`_orm.MappedAsDataclass`,
    the following warning is generated:

    .. sourcecode:: none

        SADeprecationWarning: When transforming <class '__main__.User'> to a
        dataclass, attribute(s) "create_user", "update_user" originates from
        superclass <class
        '__main__.Mixin'>, which is not a dataclass. This usage is deprecated and
        will raise an error in SQLAlchemy 2.1. When declaring SQLAlchemy
        Declarative Dataclasses, ensure that all mixin classes and other
        superclasses which include attributes are also a subclass of
        MappedAsDataclass.

    The fix is to add :class:`_orm.MappedAsDataclass` to the signature of
    ``Mixin`` as well::

        class Mixin(MappedAsDataclass):
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)

    Python's :pep:`681` specification does not accommodate for attributes declared
    on superclasses of dataclasses that are not themselves dataclasses; per the
    behavior of Python dataclasses, such fields are ignored, as in the following
    example::

        from dataclasses import dataclass
        from dataclasses import field
        import inspect
        from typing import Optional
        from uuid import uuid4


        class Mixin:
            create_user: int
            update_user: Optional[int] = field(default=None)


        @dataclass
        class User(Mixin):
            uid: str = field(init=False, default_factory=lambda: str(uuid4()))
            username: str
            password: str
            email: str

    Above, the ``User`` class will not include ``create_user`` in its constructor
    nor will it attempt to interpret ``update_user`` as a dataclass attribute.
    This is because ``Mixin`` is not a dataclass.

    SQLAlchemy's dataclasses feature within the 2.0 series does not honor this
    behavior correctly; instead, attributes on non-dataclass mixins and
    superclasses are treated as part of the final dataclass configuration.  However
    type checkers such as Pyright and Mypy will not consider these fields as
    part of the dataclass constructor as they are to be ignored per :pep:`681`.
    Since their presence is ambiguous otherwise, SQLAlchemy 2.1 will require that
    mixin classes which have SQLAlchemy mapped attributes within a dataclass
    hierarchy have to themselves be dataclasses.


.. _error_dcte:

为 <classname> 创建数据类时遇到 Python 数据类错误
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Python dataclasses error encountered when creating dataclass for <classname>

.. tab:: 中文

    当使用 :class:`_orm.MappedAsDataclass` 混入类或 :meth:`_orm.registry.mapped_as_dataclass` 装饰器时，SQLAlchemy 会使用 Python 标准库中的实际 `Python 数据类 <dataclasses_>`_ 模块，以便将数据类行为应用于目标类。此 API 有其自身的错误场景，其中大多数涉及在用户定义的类上构造 ``__init__()`` 方法；类上声明属性的顺序以及在父类上的声明，决定了如何构造 ``__init__()`` 方法，并且有具体的规则来组织属性以及如何使用 ``init=False``、``kw_only=True`` 等参数。**SQLAlchemy 不控制或实现这些规则**。因此，针对这类错误，请查阅 `Python 数据类 <dataclasses_>`_ 文档，特别关注应用于 `继承 <dc_superclass_>`_ 的规则。

    .. seealso::

    :ref:`orm_declarative_native_dataclasses` - SQLAlchemy 数据类文档

    `Python 数据类 <dataclasses_>`_ - 在 python.org 网站上

    `继承 <dc_superclass_>`_ - 在 python.org 网站上

.. tab:: 英文

    When using the :class:`_orm.MappedAsDataclass` mixin class or
    :meth:`_orm.registry.mapped_as_dataclass` decorator, SQLAlchemy makes use
    of the actual `Python dataclasses <dataclasses_>`_ module that's in the Python standard library
    in order to apply dataclass behaviors to the target class.   This API has
    its own error scenarios, most of which involve the construction of an
    ``__init__()`` method on the user defined class; the order of attributes
    declared on the class, as well as `on superclasses <dc_superclass_>`_, determines
    how the ``__init__()`` method will be constructed and there are specific
    rules in how the attributes are organized as well as how they should make
    use of parameters such as ``init=False``, ``kw_only=True``, etc.   **SQLAlchemy
    does not control or implement these rules**.  Therefore, for errors of this nature,
    consult the `Python dataclasses <dataclasses_>`_ documentation, with special
    attention to the rules applied to `inheritance <dc_superclass_>`_.

    .. seealso::

        :ref:`orm_declarative_native_dataclasses` - SQLAlchemy dataclasses documentation

        `Python dataclasses <dataclasses_>`_ - on the python.org website

        `inheritance <dc_superclass_>`_ - on the python.org website

.. _dataclasses: https://docs.python.org/3/library/dataclasses.html

.. _dc_superclass: https://docs.python.org/3/library/dataclasses.html#inheritance


.. _error_bupq:

每行 ORM 按主键批量更新要求记录包含主键值
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

per-row ORM Bulk Update by Primary Key requires that records contain primary key values

.. tab:: 中文

    此错误发生在使用 :ref:`orm_queryguide_bulk_update` 功能时，未在给定记录中提供主键值，如下所示::

        >>> session.execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )

    在上述代码中，参数字典列表与使用 :class:`_orm.Session` 执行启用了 ORM 的 UPDATE 语句结合使用时，将自动使用按主键进行的 ORM 批量更新，这要求参数字典包含主键值，例如::

        >>> session.execute(
        ...     update(User),
        ...     [
        ...         {"id": 1, "fullname": "Spongebob Squarepants"},
        ...         {"id": 3, "fullname": "Patrick Star"},
        ...         {"id": 5, "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )

    若要在不提供每条记录主键值的情况下调用 UPDATE 语句，请使用 :meth:`_orm.Session.connection` 获取当前的 :class:`_engine.Connection`，然后用该连接执行::

        >>> session.connection().execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )

    .. seealso::

            :ref:`orm_queryguide_bulk_update`

            :ref:`orm_queryguide_bulk_update_disabling`

.. tab:: 英文

    This error occurs when making use of the :ref:`orm_queryguide_bulk_update`
    feature without supplying primary key values in the given records, such as::


        >>> session.execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )

    Above, the presence of a list of parameter dictionaries combined with usage of
    the :class:`_orm.Session` to execute an ORM-enabled UPDATE statement will
    automatically make use of ORM Bulk Update by Primary Key, which expects
    parameter dictionaries to include primary key values, e.g.::

        >>> session.execute(
        ...     update(User),
        ...     [
        ...         {"id": 1, "fullname": "Spongebob Squarepants"},
        ...         {"id": 3, "fullname": "Patrick Star"},
        ...         {"id": 5, "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )

    To invoke the UPDATE statement without supplying per-record primary key values,
    use :meth:`_orm.Session.connection` to acquire the current :class:`_engine.Connection`,
    then invoke with that::

        >>> session.connection().execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )


    .. seealso::

            :ref:`orm_queryguide_bulk_update`

            :ref:`orm_queryguide_bulk_update_disabling`



AsyncIO 异常
------------------

AsyncIO Exceptions

.. _error_xd1r:

AwaitRequired
~~~~~~~~~~~~~

AwaitRequired

.. tab:: 中文

    SQLAlchemy 的异步模式要求使用异步驱动程序连接到数据库。通常，当尝试在与非兼容的 :term:`DBAPI` 配合使用时，会引发此错误。

.. tab:: 英文

    The SQLAlchemy async mode requires an async driver to be used to connect to the db.
    This error is usually raised when trying to use the async version of SQLAlchemy
    with a non compatible :term:`DBAPI`.

.. seealso::

    :ref:`asyncio_toplevel`

.. _error_xd2s:

MissingGreenlet
~~~~~~~~~~~~~~~

MissingGreenlet

.. tab:: 中文

    通常在 SQLAlchemy AsyncIO 代理类设置的 greenlet spawn 上下文之外发起了对异步 :term:`DBAPI` 的调用。此错误通常发生在尝试在意外位置进行 I/O 时，使用了一种不直接支持 ``await`` 关键字的调用模式。在使用 ORM 时，这几乎总是由于使用了 :term:`lazy loading`，而 asyncio 下没有直接支持的方式，必须进行额外的步骤和/或使用替代加载器模式才能成功使用。

    .. seealso::

        :ref:`asyncio_orm_avoid_lazyloads` - 涵盖了大多数可能发生此问题的 ORM 场景，并提供了缓解方法，包括在懒加载场景中使用的特定模式。

.. tab:: 英文

    A call to the async :term:`DBAPI` was initiated outside the greenlet spawn
    context usually setup by the SQLAlchemy AsyncIO proxy classes. Usually this
    error happens when an IO was attempted in an unexpected place, using a
    calling pattern that does not directly provide for use of the ``await`` keyword.
    When using the ORM this is nearly always due to the use of :term:`lazy loading`,
    which is not directly supported under asyncio without additional steps
    and/or alternate loader patterns in order to use successfully.

    .. seealso::

        :ref:`asyncio_orm_avoid_lazyloads` - covers most ORM scenarios where
        this problem can occur and how to mitigate, including specific patterns
        to use with lazy load scenarios.

.. _error_xd3s:

无可用检查
~~~~~~~~~~~~~~~~~~~~~~~

No Inspection Available

.. tab:: 中文

    直接在 :class:`_asyncio.AsyncConnection` 或 :class:`_asyncio.AsyncEngine` 对象上使用 :func:`_sa.inspect` 函数当前是不支持的，因为尚未提供可等待的 :class:`_reflection.Inspector` 对象形式。相反，可以通过使用 :func:`_sa.inspect` 函数以某种方式获取该对象，该方式将引用 :class:`_asyncio.AsyncConnection` 对象的底层 :attr:`_asyncio.AsyncConnection.sync_connection` 属性；然后通过使用 :meth:`_asyncio.AsyncConnection.run_sync` 方法，结合一个自定义函数来执行所需的操作，以“同步”调用方式使用 :class:`_engine.Inspector`::

        async def async_main():
            async with engine.connect() as conn:
                tables = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_table_names()
                )

    .. seealso::

        :ref:`asyncio_inspector` - 使用 :func:`_sa.inspect` 与 asyncio 扩展的更多示例。

.. tab:: 英文

    Using the :func:`_sa.inspect` function directly on an
    :class:`_asyncio.AsyncConnection` or :class:`_asyncio.AsyncEngine` object is
    not currently supported, as there is not yet an awaitable form of the
    :class:`_reflection.Inspector` object available. Instead, the object
    is used by acquiring it using the
    :func:`_sa.inspect` function in such a way that it refers to the underlying
    :attr:`_asyncio.AsyncConnection.sync_connection` attribute of the
    :class:`_asyncio.AsyncConnection` object; the :class:`_engine.Inspector` is
    then used in a "synchronous" calling style by using the
    :meth:`_asyncio.AsyncConnection.run_sync` method along with a custom function
    that performs the desired operations::

        async def async_main():
            async with engine.connect() as conn:
                tables = await conn.run_sync(
                    lambda sync_conn: inspect(sync_conn).get_table_names()
                )

    .. seealso::

        :ref:`asyncio_inspector` - additional examples of using :func:`_sa.inspect`
        with the asyncio extension.


核心异常类
----------------------

Core Exception Classes

.. tab:: 中文

    见 :ref:`core_exceptions_toplevel` 中的 Core 异常类.

.. tab:: 英文

    See :ref:`core_exceptions_toplevel` for Core exception classes.


ORM 异常类
---------------------

ORM Exception Classes

.. tab:: 中文

    见 :ref:`orm_exceptions_toplevel` 中的 ORM 异常类.

.. tab:: 英文

    See :ref:`orm_exceptions_toplevel` for ORM exception classes.



旧式异常
-----------------

Legacy Exceptions

.. tab:: 中文

    本节中的异常不是由当前 SQLAlchemy 版本生成的，但在这里提供以适应异常消息超链接。

.. tab:: 英文

    Exceptions in this section are not generated by current SQLAlchemy versions, however are provided here to suit exception message hyperlinks.

.. _error_b8d9:

SQLAlchemy 2.0 中的 <some function> 将不再是 <something>
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The <some function> in SQLAlchemy 2.0 will no longer <something>

.. tab:: 中文

    SQLAlchemy 2.0 是一次对 Core 和 ORM 组件中各种关键使用模式的重大变革。此次发布的目标，是对 SQLAlchemy 自早期以来一些最基础的设计假设进行适度调整，并带来一个全新的、更加简洁的使用模型，使 Core 与 ORM 之间在使用方式上更加一致、更加极简，并且功能更强大。

    如 :ref:`migration_20_toplevel` 所述，SQLAlchemy 2.0 项目在 1.4 系列中引入了一个全面的未来兼容性系统，使得应用程序能够获得清晰、明确、逐步的升级路径，从而迁移至完全兼容 SQLAlchemy 2.0 的模式。该系统的基础是 :class:`.exc.RemovedIn20Warning` 弃用警告，用于指引开发者修改现有代码中将被移除的行为。如何启用该警告的概述见 :ref:`deprecation_20_mode`。

    .. seealso::

        :ref:`migration_20_toplevel`  - 介绍了从 1.x 系列升级的整体流程，以及 SQLAlchemy 2.0 的目标和当前进展。

        :ref:`deprecation_20_mode` - 在 SQLAlchemy 1.4 中启用 “2.0 弃用模式” 的具体指导。

.. tab:: 英文

    SQLAlchemy 2.0 represents a major shift for a wide variety of key
    SQLAlchemy usage patterns in both the Core and ORM components.   The goal
    of the 2.0 release is to make a slight readjustment in some of the most
    fundamental assumptions of SQLAlchemy since its early beginnings, and
    to deliver a newly streamlined usage model that is hoped to be significantly
    more minimalist and consistent between the Core and ORM components, as well as
    more capable.

    Introduced at :ref:`migration_20_toplevel`, the SQLAlchemy 2.0 project includes
    a comprehensive future compatibility system that's integrated into the
    1.4 series of SQLAlchemy, such that applications will have a clear,
    unambiguous, and incremental upgrade path in order to migrate applications to
    being fully 2.0 compatible.   The :class:`.exc.RemovedIn20Warning` deprecation
    warning is at the base of this system to provide guidance on what behaviors in
    an existing codebase will need to be modified.  An overview of how to enable
    this warning is at :ref:`deprecation_20_mode`.

    .. seealso::

        :ref:`migration_20_toplevel`  - An overview of the upgrade process from
        the 1.x series, as well as the current goals and progress of SQLAlchemy
        2.0.


        :ref:`deprecation_20_mode` - specific guidelines on how to use
        "2.0 deprecations mode" in SQLAlchemy 1.4.


.. _error_s9r1:

对象正沿着 backref 级联合并到会话中
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Object is being merged into a Session along the backref cascade

.. tab:: 中文

    此消息与 SQLAlchemy 中的 “反向级联（backref cascade）” 行为有关，该行为已在 2.0 版本中移除。它指的是某个对象因与会话中已存在的另一个对象建立了关联而被自动加入 :class:`_orm.Session` 的行为。由于这一行为被证明在实践中往往令人困惑，因此添加了 :paramref:`_orm.relationship.cascade_backrefs` 和 :paramref:`_orm.backref.cascade_backrefs` 参数，可以设置为 ``False`` 以禁用该行为。在 SQLAlchemy 2.0 中，该行为已被完全移除。

    对于较早版本的 SQLAlchemy，如果某个反向引用使用的是字符串形式的 :paramref:`_orm.relationship.backref` 参数，而希望将 :paramref:`_orm.relationship.cascade_backrefs` 设置为 ``False``，则必须改为使用 :func:`_orm.backref` 函数声明该 backref，以便传入 :paramref:`_orm.backref.cascade_backrefs` 参数。

    作为替代方案，也可以通过将 :class:`_orm.Session` 以 “future” 模式启用，即传入 :paramref:`_orm.Session.future=True`，来全局禁用该行为。

    .. seealso::

        :ref:`change_5150` - SQLAlchemy 2.0 中关于该变更的背景说明。

.. tab:: 英文

    This message refers to the "backref cascade" behavior of SQLAlchemy,
    removed in version 2.0.  This refers to the action of
    an object being added into a :class:`_orm.Session` as a result of another
    object that's already present in that session being associated with it.
    As this behavior has been shown to be more confusing than helpful,
    the :paramref:`_orm.relationship.cascade_backrefs` and
    :paramref:`_orm.backref.cascade_backrefs` parameters were added, which can
    be set to ``False`` to disable it, and in SQLAlchemy 2.0 the "cascade backrefs"
    behavior has been removed entirely.

    For older SQLAlchemy versions, to set
    :paramref:`_orm.relationship.cascade_backrefs` to ``False`` on a backref that
    is currently configured using the :paramref:`_orm.relationship.backref` string
    parameter, the backref must be declared using the :func:`_orm.backref` function
    first so that the :paramref:`_orm.backref.cascade_backrefs` parameter may be
    passed.

    Alternatively, the entire "cascade backrefs" behavior can be turned off
    across the board by using the :class:`_orm.Session` in "future" mode,
    by passing ``True`` for the :paramref:`_orm.Session.future` parameter.

    .. seealso::

        :ref:`change_5150` - background on the change for SQLAlchemy 2.0.


.. _error_c9ae:

select() 构造在“旧版”模式下创建；关键字参数等。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

select() construct created in "legacy" mode; keyword arguments, etc.

.. tab:: 中文

    从 SQLAlchemy 1.4 开始，:func:`_expression.select` 构造函数已更新为支持 SQLAlchemy 2.0 中标准的调用风格。为了与 1.4 系列中的旧代码兼容，该构造函数仍接受 “旧版” 与 “新版” 两种调用方式。

    新版风格要求将列与表表达式仅以位置参数形式传递给 :func:`_expression.select`；其他修饰参数应通过后续方法链式调用添加，例如::

        # 这是推荐的 2.0 风格写法
        stmt = select(table1.c.myid).where(table1.c.myid == table2.c.otherid)

    作为对比，旧版 SQLAlchemy 中（甚至在 :meth:`.Select.where` 方法尚未出现之前）的写法如下::

        # 这是早期 SQLAlchemy 中的文档推荐写法
        stmt = select([table1.c.myid], whereclause=table1.c.myid == table2.c.otherid)

    甚至也可以将 whereclause 直接作为位置参数传入::

        # 也是早期文档中的示例
        stmt = select([table1.c.myid], table1.c.myid == table2.c.otherid)

    过去几年中，像 "whereclause" 这类额外参数已从大多数官方文档中移除，逐渐推广为如下更简洁的形式::

        # 从大约 1.0 版本起官方文档推荐的写法
        stmt = select([table1.c.myid]).where(table1.c.myid == table2.c.otherid)

    :ref:`migration_20_5284` 文档对该变更进行了详尽说明，见 :ref:`2.0 Migration <migration_20_toplevel>`。

    .. seealso::

        :ref:`migration_20_5284`

        :ref:`migration_20_toplevel`

.. tab:: 英文

    The :func:`_expression.select` construct has been updated as of SQLAlchemy
    1.4 to support the newer calling style that is standard in
    SQLAlchemy 2.0.   For backwards compatibility within
    the 1.4 series, the construct accepts arguments in both the "legacy" style as well
    as the "new" style.

    The "new" style features that column and table expressions are passed
    positionally to the :func:`_expression.select` construct only; any other
    modifiers to the object must be passed using subsequent method chaining::

        # this is the way to do it going forward
        stmt = select(table1.c.myid).where(table1.c.myid == table2.c.otherid)

    For comparison, a :func:`_expression.select` in legacy forms of SQLAlchemy,
    before methods like :meth:`.Select.where` were even added, would like::

        # this is how it was documented in original SQLAlchemy versions
        # many years ago
        stmt = select([table1.c.myid], whereclause=table1.c.myid == table2.c.otherid)

    Or even that the "whereclause" would be passed positionally::

        # this is also how it was documented in original SQLAlchemy versions
        # many years ago
        stmt = select([table1.c.myid], table1.c.myid == table2.c.otherid)

    For some years now, the additional "whereclause" and other arguments that are
    accepted have been removed from most narrative documentation, leading to a
    calling style that is most familiar as the list of column arguments passed
    as a list, but no further arguments::

        # this is how it's been documented since around version 1.0 or so
        stmt = select([table1.c.myid]).where(table1.c.myid == table2.c.otherid)

    The document at :ref:`migration_20_5284` describes this change in terms
    of :ref:`2.0 Migration <migration_20_toplevel>`.

    .. seealso::

        :ref:`migration_20_5284`

        :ref:`migration_20_toplevel`

.. _error_c9bf:

通过旧式绑定元数据定位了一个绑定，但由于此会话上设置了 future=True，因此此绑定被忽略。
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A bind was located via legacy bound metadata, but since future=True is set on this Session, this bind is ignored.

.. tab:: 中文

    “绑定元数据（bound metadata）” 的概念存在于 SQLAlchemy 1.4 之前的版本中；在 SQLAlchemy 2.0 中，该功能已被移除。

    该错误指的是 :class:`_schema.MetaData` 对象上的 :paramref:`_schema.MetaData.bind` 参数，它允许将 ORM 的某个映射类通过元数据对象与某个 :class:`_orm.Engine` 关联。在 SQLAlchemy 2.0 中，:class:`_orm.Session` 必须直接绑定到某个 :class:`_orm.Engine`。也就是说，不应再如下方式初始化 :class:`_orm.Session` 或 :class:`_orm.sessionmaker` 而将 Engine 绑定在 MetaData 上::

        engine = create_engine("sqlite://")
        Session = sessionmaker()
        metadata_obj = MetaData(bind=engine)
        Base = declarative_base(metadata=metadata_obj)

        class MyClass(Base): ...

        session = Session()
        session.add(MyClass())
        session.commit()

    相反，必须将 :class:`_engine.Engine` 直接绑定到 :class:`_orm.sessionmaker` 或 :class:`_orm.Session`，并且 :class:`_schema.MetaData` 不再应与任何引擎关联::

        engine = create_engine("sqlite://")
        Session = sessionmaker(engine)
        Base = declarative_base()

        class MyClass(Base): ...

        session = Session()
        session.add(MyClass())
        session.commit()

    在 SQLAlchemy 1.4 中，当在 :class:`_orm.sessionmaker` 或 :class:`_orm.Session` 上设置 :paramref:`_orm.Session.future` 标志时，即启用了该 :term:`2.0 style` 行为。

.. tab:: 英文

    The concept of "bound metadata" is present up until SQLAlchemy 1.4; as
    of SQLAlchemy 2.0 it's been removed.

    This error refers to the :paramref:`_schema.MetaData.bind` parameter on the
    :class:`_schema.MetaData` object that in turn allows objects like the ORM
    :class:`_orm.Session` to associate a particular mapped class with an
    :class:`_orm.Engine`. In SQLAlchemy 2.0, the :class:`_orm.Session` must be
    linked to each :class:`_orm.Engine` directly. That is, instead of instantiating
    the :class:`_orm.Session` or :class:`_orm.sessionmaker` without any arguments,
    and associating the :class:`_engine.Engine` with the
    :class:`_schema.MetaData`::

        engine = create_engine("sqlite://")
        Session = sessionmaker()
        metadata_obj = MetaData(bind=engine)
        Base = declarative_base(metadata=metadata_obj)


        class MyClass(Base): ...


        session = Session()
        session.add(MyClass())
        session.commit()

    The :class:`_engine.Engine` must instead be associated directly with the
    :class:`_orm.sessionmaker` or :class:`_orm.Session`.  The
    :class:`_schema.MetaData` object should no longer be associated with any
    engine::


        engine = create_engine("sqlite://")
        Session = sessionmaker(engine)
        Base = declarative_base()


        class MyClass(Base): ...


        session = Session()
        session.add(MyClass())
        session.commit()

    In SQLAlchemy 1.4, this :term:`2.0 style` behavior is enabled when the
    :paramref:`_orm.Session.future` flag is set on :class:`_orm.sessionmaker`
    or :class:`_orm.Session`.


.. _error_2afi:

此编译对象未绑定到任何引擎或连接
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This Compiled object is not bound to any Engine or Connection

.. tab:: 中文

    这个错误涉及 “绑定元数据（bound metadata）” 的概念，这是 SQLAlchemy 1.x 中存在的一种传统用法模式。该问题通常发生在尝试直接调用 Core 表达式对象上的 :meth:`.Executable.execute` 方法时，而该对象又没有关联任何 :class:`_engine.Engine` 的情况下，例如::

        metadata_obj = MetaData()
        table = Table("t", metadata_obj, Column("q", Integer))

        stmt = select(table)
        result = stmt.execute()  # <--- 会抛出异常

    上述代码中，系统预期 :class:`_schema.MetaData` 对象应当已经 **绑定** 到某个 :class:`_engine.Engine` 实例，例如::

        engine = create_engine("mysql+pymysql://user:pass@host/db")
        metadata_obj = MetaData(bind=engine)

    在这种用法下，任何从该 :class:`_schema.MetaData` 派生出的 :class:`_schema.Table`，其生成的语句将会隐式使用该 :class:`_engine.Engine` 来执行。

    需要注意的是， **SQLAlchemy 2.0 中已不再支持绑定元数据（bound metadata）**。在 2.0 中，执行语句的正确方式是通过 :class:`_engine.Connection` 的 :meth:`_engine.Connection.execute` 方法::

        with engine.connect() as conn:
            result = conn.execute(stmt)

    如果是在 ORM 中使用，也可以通过 :class:`.Session` 对象来执行::

        result = session.execute(stmt)

    .. seealso::

        :ref:`tutorial_statement_execution`

.. tab:: 英文

    This error refers to the concept of "bound metadata", which is a legacy
    SQLAlchemy pattern present only in 1.x versions. The issue occurs when one invokes
    the :meth:`.Executable.execute` method directly off of a Core expression object
    that is not associated with any :class:`_engine.Engine`::

        metadata_obj = MetaData()
        table = Table("t", metadata_obj, Column("q", Integer))

        stmt = select(table)
        result = stmt.execute()  # <--- raises

    What the logic is expecting is that the :class:`_schema.MetaData` object has
    been **bound** to a :class:`_engine.Engine`::

        engine = create_engine("mysql+pymysql://user:pass@host/db")
        metadata_obj = MetaData(bind=engine)

    Where above, any statement that derives from a :class:`_schema.Table` which
    in turn derives from that :class:`_schema.MetaData` will implicitly make use of
    the given :class:`_engine.Engine` in order to invoke the statement.

    Note that the concept of bound metadata is **not present in SQLAlchemy 2.0**.
    The correct way to invoke statements is via
    the :meth:`_engine.Connection.execute` method of a :class:`_engine.Connection`::

        with engine.connect() as conn:
            result = conn.execute(stmt)

    When using the ORM, a similar facility is available via the :class:`.Session`::

        result = session.execute(stmt)

    .. seealso::

        :ref:`tutorial_statement_execution`

.. _error_8s2a:

此连接处于非活动事务中。请完全回滚(rollback)后再继续
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This connection is on an inactive transaction.  Please rollback() fully before proceeding

.. tab:: 中文

    此类错误在 SQLAlchemy 1.4 中被引入，在 SQLAlchemy 2.0 中不再适用。其背后逻辑与事务的嵌套结构有关：当使用 :meth:`_engine.Connection.begin` 创建了一个事务后，如果在此作用域中又开启了另一个 “标记型事务（marker transaction）”，随后对其执行 :meth:`.Transaction.rollback` 或 :meth:`.Transaction.close`，但外部事务仍存在且处于 “非激活” 状态，就会抛出此错误。

    以下是这种情况的示例::

        engine = create_engine(...)

        connection = engine.connect()
        transaction1 = connection.begin()

        # 这是一个 “子事务” 或 “标记事务”，只是逻辑上的嵌套结构，依附于 transaction1
        transaction2 = connection.begin()
        transaction2.rollback()

        # transaction1 仍然存在，但处于非激活状态，此时继续执行将抛出错误
        connection.execute(text("select 1"))

    在上述代码中，``transaction2`` 是一个逻辑上的 “标记事务”，它可以通过 `rollback()` 回滚整个数据库事务，但其 `commit()` 实际上不会提交事务，仅结束其自身的作用域。调用 ``transaction2.rollback()`` 会使得 ``transaction1`` 被 **标记为非激活状态** （实际上数据库级别已经回滚），但从 SQLAlchemy 的角度看，它仍然存在，以维持事务嵌套的结构一致性。

    正确的解决方式是显式回滚外层事务::

        transaction1.rollback()

    这种 “子事务” 模式在 Core 层中并不常用。但在 ORM 中也会遇到类似问题，这通常是 ORM 的 “逻辑事务结构” 所导致，相关说明可参考 FAQ 条目 :ref:`faq_session_rollback`。

    **需要特别指出的是：此类“子事务”模式在 SQLAlchemy 2.0 中已被移除**，因此这一编程模式不再可用，也就不会再产生该错误。

.. tab:: 英文

    This error condition was added to SQLAlchemy as of version 1.4, and does not
    apply to SQLAlchemy 2.0.    The error
    refers to the state where a :class:`_engine.Connection` is placed into a
    transaction using a method like :meth:`_engine.Connection.begin`, and then a
    further "marker" transaction is created within that scope; the "marker"
    transaction is then rolled back using :meth:`.Transaction.rollback` or closed
    using :meth:`.Transaction.close`, however the outer transaction is still
    present in an "inactive" state and must be rolled back.

    The pattern looks like::

        engine = create_engine(...)

        connection = engine.connect()
        transaction1 = connection.begin()

        # this is a "sub" or "marker" transaction, a logical nesting
        # structure based on "real" transaction transaction1
        transaction2 = connection.begin()
        transaction2.rollback()

        # transaction1 is still present and needs explicit rollback,
        # so this will raise
        connection.execute(text("select 1"))

    Above, ``transaction2`` is a "marker" transaction, which indicates a logical
    nesting of transactions within an outer one; while the inner transaction
    can roll back the whole transaction via its rollback() method, its commit()
    method has no effect except to close the scope of the "marker" transaction
    itself.   The call to ``transaction2.rollback()`` has the effect of
    **deactivating** transaction1 which means it is essentially rolled back
    at the database level, however is still present in order to accommodate
    a consistent nesting pattern of transactions.

    The correct resolution is to ensure the outer transaction is also
    rolled back::

        transaction1.rollback()

    This pattern is not commonly used in Core.  Within the ORM, a similar issue can
    occur which is the product of the ORM's "logical" transaction structure; this
    is described in the FAQ entry at :ref:`faq_session_rollback`.

    The "subtransaction" pattern is removed in SQLAlchemy 2.0 so that this
    particular programming pattern is no longer be available, preventing
    this error message.



