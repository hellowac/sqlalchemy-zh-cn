连接 / 引擎
=====================

Connections / Engines

.. contents::
    :local:
    :class: faq
    :backlinks: none


如何配置日志记录？
---------------------------

How do I configure logging?

See :ref:`dbengine_logging`.

如何池化数据库连接？我的连接是否已池化？
----------------------------------------------------------------

How do I pool database connections?   Are my connections pooled?

.. tab:: 中文

    SQLAlchemy在大多数情况下自动执行应用程序级别的连接池。对于所有包含的方言（使用 "memory" 数据库的SQLite除外）， :class:`_engine.Engine` 对象指的是一个 :class:`.QueuePool` 作为连接源。

    有关更多详细信息，请参见 :ref:`engines_toplevel` 和 :ref:`pooling_toplevel`。

.. tab:: 英文

    SQLAlchemy performs application-level connection pooling automatically
    in most cases.  For all included dialects (except SQLite when using a 
    "memory" database), a :class:`_engine.Engine` object refers to a 
    :class:`.QueuePool` as a source of connectivity.

    For more detail, see :ref:`engines_toplevel` and :ref:`pooling_toplevel`.

如何将自定义连接参数传递给我的数据库 API？
----------------------------------------------------------

How do I pass custom connect arguments to my database API?

.. tab:: 中文

    :func:`_sa.create_engine` 调用可以通过 ``connect_args`` 关键字参数直接接受附加参数::
    
        e = create_engine(
            "mysql+mysqldb://scott:tiger@localhost/test", connect_args={"encoding": "utf8"}
        )
    
    或者，对于基本的字符串和整数类型参数，也通常可以通过 URL 的查询字符串指定::
    
        e = create_engine("mysql+mysqldb://scott:tiger@localhost/test?encoding=utf8")

.. tab:: 英文

    The :func:`_sa.create_engine` call accepts additional arguments either directly via the ``connect_args`` keyword argument::

        e = create_engine(
            "mysql+mysqldb://scott:tiger@localhost/test", connect_args={"encoding": "utf8"}
        )

    Or for basic string and integer arguments, they can usually be specified in the query string of the URL::

        e = create_engine("mysql+mysqldb://scott:tiger@localhost/test?encoding=utf8")

.. seealso::

    :ref:`custom_dbapi_args`

“MySQL 服务器已消失”
----------------------------

"MySQL Server has gone away"

.. tab:: 中文
    
    此类错误的主要原因是 MySQL 连接已超时，并被服务器关闭。MySQL 服务器会关闭空闲超过一定时间的连接，默认时间为八小时。为了应对这种情况，可以立即启用 :paramref:`_sa.create_engine.pool_recycle` 设置。该设置可以确保当连接使用时，如果其存在时间已超过设定的秒数，就会被丢弃并替换为一个新连接。
    
    为了应对数据库重启以及因网络问题导致的其他临时连接丢失的情况，连接池中的连接也可能会在更通用的断开检测技术作用下被回收。:ref:`pool_disconnects` 小节介绍了“悲观”（例如 pre-ping）和“乐观”（例如优雅恢复）技术的背景。现代 SQLAlchemy 更倾向于使用“悲观”方式。
    
    .. seealso::
    
        :ref:`pool_disconnects`

.. tab:: 英文

    The primary cause of this error is that the MySQL connection has timed out
    and has been closed by the server.   The MySQL server closes connections
    which have been idle a period of time which defaults to eight hours.
    To accommodate this, the immediate setting is to enable the
    :paramref:`_sa.create_engine.pool_recycle` setting, which will ensure that a
    connection which is older than a set amount of seconds will be discarded
    and replaced with a new connection when it is next checked out.

    For the more general case of accommodating database restarts and other
    temporary loss of connectivity due to network issues, connections that
    are in the pool may be recycled in response to more generalized disconnect
    detection techniques.  The section :ref:`pool_disconnects` provides
    background on both "pessimistic" (e.g. pre-ping) and "optimistic"
    (e.g. graceful recovery) techniques.   Modern SQLAlchemy tends to favor
    the "pessimistic" approach.

    .. seealso::

        :ref:`pool_disconnects`

.. _mysql_sync_errors:

“命令不同步；您现在无法运行此命令”/“此结果对象不返回行。它已自动关闭”
------------------------------------------------------------------------------------------------------------------------------------

"Commands out of sync; you can't run this command now" / "This result object does not return rows. It has been closed automatically"

.. tab:: 中文
    
    MySQL 驱动程序存在一类较为广泛的故障模式，在这些模式下，与服务器的连接处于无效状态。通常当连接再次被使用时，会出现以下两类错误消息中的一种。原因在于服务器的状态已被更改为客户端库未预期的状态，导致客户端库在连接上发出新语句时，服务器无法做出预期响应。
    
    在 SQLAlchemy 中，由于数据库连接是被池化管理的，连接消息不同步的问题变得更加严重。因为如果操作失败，而连接本身处于不可用状态，该连接被返回连接池后，在下一次使用时就会出现故障。为解决这一问题，当检测到这类故障时，连接会被 **标记为失效**，从而底层与 MySQL 的连接会被丢弃。这种失效机制在很多已知的故障模式中会自动触发，也可以通过调用 :meth:`_engine.Connection.invalidate` 方法显式触发。
    
    此外，在这类故障模式中还有另一类情况，即使用像 ``with session.begin_nested():`` 这样的上下文管理器在发生错误时尝试“回滚”事务；然而，在某些连接故障模式下，回滚操作（例如 RELEASE SAVEPOINT 操作）本身也会失败，从而导致误导性的堆栈跟踪。
    
    最初，这类错误的原因相对简单，即多线程程序在多个线程中对同一个连接发出命令。这主要发生在最初广泛使用的原生 C 编写的“MySQLdb”驱动中。然而，随着 PyMySQL、MySQL-connector-Python 等纯 Python 驱动的出现，以及 gevent/eventlet、multiprocessing（如与 Celery 一起使用）等工具的广泛使用，导致此类问题的因素大幅增加。其中一些问题已在 SQLAlchemy 的多个版本中得到改进，但也存在一些无法避免的情况：
    
    * **在线程之间共享连接** —— 这是最早导致此类错误的原因。程序在两个或多个线程中同时使用同一个连接，导致多个消息集合在连接上混合，从而将服务器端的会话状态搞乱，客户端不再知道如何解释当前状态。不过，如今其他原因更为常见。
    
    * **在进程之间共享连接的文件句柄** —— 这通常发生在程序使用 ``os.fork()`` 创建新进程时，父进程中的 TCP 连接会被共享到一个或多个子进程中。由于多个进程在向同一个文件句柄发送消息，服务器接收到交错的消息，导致连接状态混乱。
    
      这种情况在程序使用 Python 的 “multiprocessing” 模块并在父进程中创建了 :class:`_engine.Engine` 实例时很容易发生。使用 Celery 等工具时也常见这种模式。正确做法是在子进程启动时创建新的 :class:`_engine.Engine` 实例，丢弃父进程传下来的实例；或者调用 :meth:`_engine.Engine.dispose` 以释放继承自父进程的 :class:`_engine.Engine` 实例所持有的内部连接池。
    
    * **使用 Greenlet Monkeypatching 后发生退出** —— 使用 gevent 或 eventlet 等库对 Python 网络 API 进行 monkeypatching 后，像 PyMySQL 这类库即使未专门为异步模式设计，也会以异步方式运行。一个常见的问题是 greenthread 被中断，通常是由于应用程序中的超时逻辑。此时会抛出 ``GreenletExit`` 异常，中断 PyMySQL 正在执行的操作（例如正在接收服务器响应或重置连接状态）。异常中断后，客户端和服务器之间的通信步调被打乱，连接后续的使用可能失败。自 SQLAlchemy 1.1.0 版本起，当数据库操作被“退出类异常”中断（如 ``GreenletExit``，或任何继承自 Python ``BaseException`` 但不继承自 ``Exception`` 的异常）时，连接会被标记为失效。
    
    * **回滚 / SAVEPOINT 释放失败** —— 某些类型的错误会导致连接在事务上下文中不可用，也会影响 “SAVEPOINT” 块中的操作。在这种情况下，连接上的错误会使得任何 SAVEPOINT 实际上已不存在，而当 SQLAlchemy 或应用程序尝试回滚该 SAVEPOINT 时，“RELEASE SAVEPOINT” 操作会失败，通常会返回“savepoint does not exist”这样的消息。在 Python 3 中，将会输出异常链，其中包含导致错误的根本“原因”；而在 Python 2 中，由于没有异常链，SQLAlchemy 的新版本会尝试发出一个警告，说明原始的失败原因，同时仍然抛出导致回滚失败的直接错误。


.. tab:: 英文
    
    The MySQL drivers have a fairly wide class of failure modes whereby the state of
    the connection to the server is in an invalid state.  Typically, when the connection
    is used again, one of these two error messages will occur.    The reason is because
    the state of the server has been changed to one in which the client library
    does not expect, such that when the client library emits a new statement
    on the connection, the server does not respond as expected.
    
    In SQLAlchemy, because database connections are pooled, the issue of the messaging
    being out of sync on a connection becomes more important, since when an operation
    fails, if the connection itself is in an unusable state, if it goes back into the
    connection pool, it will malfunction when checked out again.  The mitigation
    for this issue is that the connection is **invalidated** when such a failure
    mode occurs so that the underlying database connection to MySQL is discarded.
    This invalidation occurs automatically for many known failure modes and can
    also be called explicitly via the :meth:`_engine.Connection.invalidate` method.
    
    There is also a second class of failure modes within this category where a context manager
    such as ``with session.begin_nested():`` wants to "roll back" the transaction
    when an error occurs; however within some failure modes of the connection, the
    rollback itself (which can also be a RELEASE SAVEPOINT operation) also
    fails, causing misleading stack traces.
    
    Originally, the cause of this error used to be fairly simple, it meant that
    a multithreaded program was invoking commands on a single connection from more
    than one thread.   This applied to the original "MySQLdb" native-C driver that was
    pretty much the only driver in use.   However, with the introduction of pure Python
    drivers like PyMySQL and MySQL-connector-Python, as well as increased use of
    tools such as gevent/eventlet, multiprocessing (often with Celery), and others,
    there is a whole series of factors that has been known to cause this problem, some of
    which have been improved across SQLAlchemy versions but others which are unavoidable:
    
    * **Sharing a connection among threads** - This is the original reason these kinds
      of errors occurred.  A program used the same connection in two or more threads at
      the same time, meaning multiple sets of messages got mixed up on the connection,
      putting the server-side session into a state that the client no longer knows how
      to interpret.   However, other causes are usually more likely today.
    
    * **Sharing the filehandle for the connection among processes** - This usually occurs
      when a program uses ``os.fork()`` to spawn a new process, and a TCP connection
      that is present in th parent process gets shared into one or more child processes.
      As multiple processes are now emitting messages to essentially the same filehandle,
      the server receives interleaved messages and breaks the state of the connection.
    
      This scenario can occur very easily if a program uses Python's "multiprocessing"
      module and makes use of an :class:`_engine.Engine` that was created in the parent
      process.  It's common that "multiprocessing" is in use when using tools like
      Celery.  The correct approach should be either that a new :class:`_engine.Engine`
      is produced when a child process first starts, discarding any :class:`_engine.Engine`
      that came down from the parent process; or, the :class:`_engine.Engine` that's inherited
      from the parent process can have it's internal pool of connections disposed by
      calling :meth:`_engine.Engine.dispose`.
    
    * **Greenlet Monkeypatching w/ Exits** - When using a library like gevent or eventlet
      that monkeypatches the Python networking API, libraries like PyMySQL are now
      working in an asynchronous mode of operation, even though they are not developed
      explicitly against this model.  A common issue is that a greenthread is interrupted,
      often due to timeout logic in the application.  This results in the ``GreenletExit``
      exception being raised, and the pure-Python MySQL driver is interrupted from
      its work, which may have been that it was receiving a response from the server
      or preparing to otherwise reset the state of the connection.   When the exception
      cuts all that work short, the conversation between client and server is now
      out of sync and subsequent usage of the connection may fail.   SQLAlchemy
      as of version 1.1.0 knows how to guard against this, as if a database operation
      is interrupted by a so-called "exit exception", which includes ``GreenletExit``
      and any other subclass of Python ``BaseException`` that is not also a subclass
      of ``Exception``, the connection is invalidated.
    
    * **Rollbacks / SAVEPOINT releases failing** - Some classes of error cause
      the connection to be unusable within the context of a transaction, as well
      as when operating in a "SAVEPOINT" block.  In these cases, the failure
      on the connection has rendered any SAVEPOINT as no longer existing, yet
      when SQLAlchemy, or the application, attempts to "roll back" this savepoint,
      the "RELEASE SAVEPOINT" operation fails, typically with a message like
      "savepoint does not exist".   In this case, under Python 3 there will be
      a chain of exceptions output, where the ultimate "cause" of the error
      will be displayed as well.  Under Python 2, there are no "chained" exceptions,
      however recent versions of SQLAlchemy will attempt to emit a warning
      illustrating the original failure cause, while still throwing the
      immediate error which is the failure of the ROLLBACK.
    
.. _faq_execute_retry:

如何自动“重试”语句执行？
-------------------------------------------------------

How Do I "Retry" a Statement Execution Automatically?
    
.. tab:: 中文

    文档章节 :ref:`pool_disconnects` 讨论了在连接池中的连接自上次检出后已断开的情况下可用的策略。此方面最现代的功能是 :paramref:`_sa.create_engine.pre_ping` 参数，它允许在从连接池获取数据库连接时发出一个“ping”，如果当前连接已断开，则自动重连。

    需要注意的是，这个“ping”仅在连接被实际使用 **之前** 发出。一旦连接交付给调用者，根据 Python :term:`DBAPI` 规范，它现在将会触发一次 **自动开启事务** （autobegin）操作，这意味着该连接在首次使用时会自动开始一个新事务，并在后续语句中保持该事务，直到显式调用 DBAPI 层的 ``connection.commit()`` 或 ``connection.rollback()`` 方法。

    在现代 SQLAlchemy 的使用中，总是一系列 SQL 语句在此事务状态下被执行，假设未启用 :ref:`DBAPI 自动提交模式 <dbapi_autocommit>`（下一节将详细介绍），也就意味着不会有任何语句被自动提交；如果操作失败，则当前事务中所有语句的效果都会丢失。

    这对于“重试”语句的含义是：在默认情况下，当连接丢失时， **整个事务也会丢失** 。此时无法“重新连接并重试”后继续事务的剩余操作，因为数据已经丢失。因此，SQLAlchemy 并不提供一种透明的“重连”机制来应对事务中断的情况，即数据库连接在使用中被断开。处理事务中断断开的标准方法是： **从事务的起点重新执行整个操作** ，通常是通过一个 Python 自定义装饰器，在函数失败时重试数次直到成功，或者将应用架构设计成能够容忍事务丢失并相应地处理操作失败。

    另外也存在一种扩展的设想，即记录事务中的所有语句，然后在一个新事务中重放这些语句以近似“重试”操作。SQLAlchemy 的 :ref:`事件系统 <core_event_toplevel>` 允许构建这样的系统，但这类方案在实践中并不常见，因为无法保证这些 :term:`DML` 语句在新事务中的执行环境和原事务相同，一旦事务结束，数据库状态可能已发生变化。因此，在事务开始和提交的点显式设计“重试”机制仍然是更可靠的方式，因为应用层的事务方法最清楚该如何重新执行它们的步骤。

    否则，如果 SQLAlchemy 提供了一个在事务中途透明且静默“重连”的功能，其结果很可能是悄无声息地丢失数据。试图隐藏这个问题只会使情况更加严重。

    然而，如果我们 **没有使用事务** ，那么就有更多的可能性，如下一节所述。

.. tab:: 英文

    The documentation section :ref:`pool_disconnects` discusses the strategies
    available for pooled connections that have been disconnected since the last
    time a particular connection was checked out.   The most modern feature
    in this regard is the :paramref:`_sa.create_engine.pre_ping` parameter, which
    allows that a "ping" is emitted on a database connection when it's retrieved
    from the pool, reconnecting if the current connection has been disconnected.

    It's important to note that this "ping" is only emitted **before** the
    connection is actually used for an operation.   Once the connection is
    delivered to the caller, per the Python :term:`DBAPI` specification it is now
    subject to an **autobegin** operation, which means it will automatically BEGIN
    a new transaction when it is first used that remains in effect for subsequent
    statements, until the DBAPI-level ``connection.commit()`` or
    ``connection.rollback()`` method is invoked.

    In modern use of SQLAlchemy, a series of SQL statements are always invoked
    within this transactional state, assuming
    :ref:`DBAPI autocommit mode <dbapi_autocommit>` is not enabled (more on that in
    the next section), meaning that no single statement is automatically committed;
    if an operation fails, the effects of all statements within the current
    transaction will be lost.

    The implication that this has for the notion of "retrying" a statement is that
    in the default case, when a connection is lost, **the entire transaction is
    lost**. There is no useful way that the database can "reconnect and retry" and
    continue where it left off, since data is already lost.   For this reason,
    SQLAlchemy does not have a transparent "reconnection" feature that works
    mid-transaction, for the case when the database connection has disconnected
    while being used. The canonical approach to dealing with mid-operation
    disconnects is to **retry the entire operation from the start of the
    transaction**, often by using a custom Python decorator that will
    "retry" a particular function several times until it succeeds, or to otherwise
    architect the application in such a way that it is resilient against
    transactions that are dropped that then cause operations to fail.

    There is also the notion of extensions that can keep track of all of the
    statements that have proceeded within a transaction and then replay them all in
    a new transaction in order to approximate a "retry" operation.  SQLAlchemy's
    :ref:`event system <core_event_toplevel>` does allow such a system to be
    constructed, however this approach is also not generally useful as there is
    no way to guarantee that those
    :term:`DML` statements will be working against the same state, as once a
    transaction has ended the state of the database in a new transaction may be
    totally different.   Architecting "retry" explicitly into the application
    at the points at which transactional operations begin and commit remains
    the better approach since the application-level transactional methods are
    the ones that know best how to re-run their steps.

    Otherwise, if SQLAlchemy were to provide a feature that transparently and
    silently "reconnected" a connection mid-transaction, the effect would be that
    data is silently lost.   By trying to hide the problem, SQLAlchemy would make
    the situation much worse.

    However, if we are **not** using transactions, then there are more options
    available, as the next section describes.

.. _faq_execute_retry_autocommit:

使用 DBAPI 自动提交允许只读版本的透明重新连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using DBAPI Autocommit Allows for a Readonly Version of Transparent Reconnect

.. tab:: 中文
    
    在说明不提供透明重连机制的理由后，以上讨论建立在应用程序确实使用了 DBAPI 层事务的前提上。由于大多数 DBAPI 现在支持 :ref:`原生“自动提交”设置 <dbapi_autocommit>`，我们可以利用这些特性，为 **只读的、自动提交的操作** 提供有限的透明重连机制。一个透明的语句重试可以应用于 DBAPI 的 ``cursor.execute()`` 方法；但对于 ``cursor.executemany()``，仍不安全使用该机制，因为语句可能已经消耗了部分传入参数。
    
    .. warning:: 
        
        以下方案 **不应** 用于写入数据的操作。使用者应仔细阅读并理解该方案的工作方式，并针对目标 DBAPI 驱动在各种故障模式下进行充分测试后，方可在生产环境中使用。此重试机制不能保证在所有情况下防止连接断开错误。
    
    通过使用 :meth:`_events.DialectEvents.do_execute` 和 :meth:`_events.DialectEvents.do_execute_no_params` 钩子，可以对 DBAPI 层的 ``cursor.execute()`` 方法应用一个简单的重试机制，从而在语句执行时拦截断开连接的情况。 **注意**：此机制 **不会** 拦截在结果集提取阶段的连接失败（针对那些不会完全缓存结果集的 DBAPI）。此方案要求数据库支持 DBAPI 层的自动提交，并且并非对所有数据库后端都 **有保障**。以下提供了一个函数 ``reconnecting_engine()``，它将事件钩子应用于指定的 :class:`_engine.Engine` 对象，返回一个始终启用 DBAPI 自动提交的版本，并可在单参数或无参数的语句执行中自动透明重连::
    
        import time
    
        from sqlalchemy import event
    
    
        def reconnecting_engine(engine, num_retries, retry_interval):
            def _run_with_retries(fn, context, cursor_obj, statement, *arg, **kw):
                for retry in range(num_retries + 1):
                    try:
                        fn(cursor_obj, statement, context=context, *arg)
                    except engine.dialect.dbapi.Error as raw_dbapi_err:
                        connection = context.root_connection
                        if engine.dialect.is_disconnect(raw_dbapi_err, connection, cursor_obj):
                            engine.logger.error(
                                "disconnection error, attempt %d/%d",
                                retry + 1,
                                num_retries + 1,
                                exc_info=True,
                            )
                            connection.invalidate()
    
                            # 使用 SQLAlchemy 2.0 API（如可用）
                            if hasattr(connection, "rollback"):
                                connection.rollback()
                            else:
                                trans = connection.get_transaction()
                                if trans:
                                    trans.rollback()
    
                            if retry == num_retries:
                                raise
    
                            time.sleep(retry_interval)
                            context.cursor = cursor_obj = connection.connection.cursor()
                        else:
                            raise
                    else:
                        return True
    
            e = engine.execution_options(isolation_level="AUTOCOMMIT")
    
            @event.listens_for(e, "do_execute_no_params")
            def do_execute_no_params(cursor_obj, statement, context):
                return _run_with_retries(
                    context.dialect.do_execute_no_params, context, cursor_obj, statement
                )
    
            @event.listens_for(e, "do_execute")
            def do_execute(cursor_obj, statement, parameters, context):
                return _run_with_retries(
                    context.dialect.do_execute, context, cursor_obj, statement, parameters
                )
    
            return e
    
    根据上述方案，可以使用以下示例脚本来演示事务中途的重连操作。运行该脚本后，每五秒会向数据库发出一次 ``SELECT 1`` 语句::
    
        from sqlalchemy import create_engine
        from sqlalchemy import select
    
        if __name__ == "__main__":
            engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test", echo_pool=True)
    
            def do_a_thing(engine):
                with engine.begin() as conn:
                    while True:
                        print("ping: %s" % conn.execute(select([1])).scalar())
                        time.sleep(5)
    
            e = reconnecting_engine(
                create_engine("mysql+mysqldb://scott:tiger@localhost/test", echo_pool=True),
                num_retries=5,
                retry_interval=2,
            )
    
            do_a_thing(e)
    
    在脚本运行期间重启数据库，可以观察到透明重连效果：
    
    .. sourcecode:: text
    
        $ python reconnect_test.py
        ping: 1
        ping: 1
        disconnection error, retrying operation
        Traceback (most recent call last):
          ...
        MySQLdb._exceptions.OperationalError: (2006, 'MySQL server has gone away')
        2020-10-19 16:16:22,624 INFO sqlalchemy.pool.impl.QueuePool Invalidate connection <_mysql.connection open to 'localhost' at 0xf59240>
        ping: 1
        ping: 1
        ...
    
    .. versionadded:: 1.4  上述方案依赖于 SQLAlchemy 1.4 的特定行为，无法在更早版本中按此方式工作。

.. tab:: 英文

    With the rationale for not having a transparent reconnection mechanism stated,
    the preceding section rests upon the assumption that the application is in
    fact using DBAPI-level transactions.  As most DBAPIs now offer :ref:`native
    "autocommit" settings <dbapi_autocommit>`, we can make use of these features to
    provide a limited form of transparent reconnect for **read only,
    autocommit only operations**.  A transparent statement retry may be applied to
    the ``cursor.execute()`` method of the DBAPI, however it is still not safe to
    apply to the ``cursor.executemany()`` method of the DBAPI, as the statement may
    have consumed any portion of the arguments given.
    
    .. warning:: The following recipe should **not** be used for operations that
       write data.   Users should carefully read and understand how the recipe
       works and test failure modes very carefully against the specifically
       targeted DBAPI driver before making production use of this recipe.
       The retry mechanism does not guarantee prevention of disconnection errors
       in all cases.
    
    A simple retry mechanism may be applied to the DBAPI level ``cursor.execute()``
    method by making use of the :meth:`_events.DialectEvents.do_execute` and
    :meth:`_events.DialectEvents.do_execute_no_params` hooks, which will be able to
    intercept disconnections during statement executions.   It will **not**
    intercept connection failures during result set fetch operations, for those
    DBAPIs that don't fully buffer result sets.  The recipe requires that the
    database support DBAPI level autocommit and is **not guaranteed** for
    particular backends.  A single function ``reconnecting_engine()`` is presented
    which applies the event hooks to a given :class:`_engine.Engine` object,
    returning an always-autocommit version that enables DBAPI-level autocommit.
    A connection will transparently reconnect for single-parameter and no-parameter
    statement executions::
    
    
        import time
    
        from sqlalchemy import event
    
    
        def reconnecting_engine(engine, num_retries, retry_interval):
            def _run_with_retries(fn, context, cursor_obj, statement, *arg, **kw):
                for retry in range(num_retries + 1):
                    try:
                        fn(cursor_obj, statement, context=context, *arg)
                    except engine.dialect.dbapi.Error as raw_dbapi_err:
                        connection = context.root_connection
                        if engine.dialect.is_disconnect(raw_dbapi_err, connection, cursor_obj):
                            engine.logger.error(
                                "disconnection error, attempt %d/%d",
                                retry + 1,
                                num_retries + 1,
                                exc_info=True,
                            )
                            connection.invalidate()
    
                            # use SQLAlchemy 2.0 API if available
                            if hasattr(connection, "rollback"):
                                connection.rollback()
                            else:
                                trans = connection.get_transaction()
                                if trans:
                                    trans.rollback()
    
                            if retry == num_retries:
                                raise
    
                            time.sleep(retry_interval)
                            context.cursor = cursor_obj = connection.connection.cursor()
                        else:
                            raise
                    else:
                        return True
    
            e = engine.execution_options(isolation_level="AUTOCOMMIT")
    
            @event.listens_for(e, "do_execute_no_params")
            def do_execute_no_params(cursor_obj, statement, context):
                return _run_with_retries(
                    context.dialect.do_execute_no_params, context, cursor_obj, statement
                )
    
            @event.listens_for(e, "do_execute")
            def do_execute(cursor_obj, statement, parameters, context):
                return _run_with_retries(
                    context.dialect.do_execute, context, cursor_obj, statement, parameters
                )
    
            return e
    
    Given the above recipe, a reconnection mid-transaction may be demonstrated
    using the following proof of concept script.  Once run, it will emit a
    ``SELECT 1`` statement to the database every five seconds::
    
        from sqlalchemy import create_engine
        from sqlalchemy import select
    
        if __name__ == "__main__":
            engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test", echo_pool=True)
    
            def do_a_thing(engine):
                with engine.begin() as conn:
                    while True:
                        print("ping: %s" % conn.execute(select([1])).scalar())
                        time.sleep(5)
    
            e = reconnecting_engine(
                create_engine("mysql+mysqldb://scott:tiger@localhost/test", echo_pool=True),
                num_retries=5,
                retry_interval=2,
            )
    
            do_a_thing(e)
    
    Restart the database while the script runs to demonstrate the transparent
    reconnect operation:
    
    .. sourcecode:: text
    
        $ python reconnect_test.py
        ping: 1
        ping: 1
        disconnection error, retrying operation
        Traceback (most recent call last):
          ...
        MySQLdb._exceptions.OperationalError: (2006, 'MySQL server has gone away')
        2020-10-19 16:16:22,624 INFO sqlalchemy.pool.impl.QueuePool Invalidate connection <_mysql.connection open to 'localhost' at 0xf59240>
        ping: 1
        ping: 1
        ...
    
    .. versionadded:: 1.4  the above recipe makes use of 1.4-specific behaviors and will
       not work as given on previous SQLAlchemy versions.
    
    The above recipe is tested for SQLAlchemy 1.4.



为什么 SQLAlchemy 发出如此多的 ROLLBACK？
--------------------------------------------

Why does SQLAlchemy issue so many ROLLBACKs?

.. tab:: 中文

    SQLAlchemy 目前假定 DBAPI 连接处于“非自动提交”模式——这是 Python 数据库 API 的默认行为，这意味着必须假定事务始终在进行中。连接返回时，连接池会发出 ``connection.rollback()``。这样做是为了释放连接上剩余的所有事务资源。在像 PostgreSQL 或 MSSQL 这样表资源被严格锁定的数据库中，这一点至关重要，这样行和表就不会在不再使用的连接中保持锁定状态。否则应用程序可能会挂起。然而，这不仅仅适用于锁，对于任何具有事务隔离类型的数据库（包括带有 InnoDB 的 MySQL）来说，它都同样重要。任何仍在旧事务中的连接，如果已经在隔离状态下在该连接上查询过该数据，都将返回过时的数据。有关即使在 MySQL 上也可能会看到过时数据的背景信息，请参阅 https://dev.mysql.com/doc/refman/5.1/en/innodb-transaction-model.html

.. tab:: 英文

    SQLAlchemy currently assumes DBAPI connections are in "non-autocommit" mode - this is the default behavior of the Python database API, meaning it must be assumed that a transaction is always in progress. The connection pool issues ``connection.rollback()`` when a connection is returned. This is so that any transactional resources remaining on the connection are released. On a database like PostgreSQL or MSSQL where table resources are aggressively locked, this is critical so that rows and tables don't remain locked within connections that are no longer in use. An application can otherwise hang. It's not just for locks, however, and is equally critical on any database that has any kind of transaction isolation, including MySQL with InnoDB. Any connection that is still inside an old transaction will return stale data, if that data was already queried on that connection within isolation. For background on why you might see stale data even on MySQL, see https://dev.mysql.com/doc/refman/5.1/en/innodb-transaction-model.html

我在使用 MyISAM - 我如何关闭它？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I'm on MyISAM - how do I turn it off?

.. tab:: 中文

    连接池中连接的返回行为可以通过 ``reset_on_return`` 参数进行配置::

        from sqlalchemy import create_engine
        from sqlalchemy.pool import QueuePool

        engine = create_engine(
            "mysql+mysqldb://scott:tiger@localhost/myisam_database",
            pool=QueuePool(reset_on_return=False),
        )

.. tab:: 英文

    The behavior of the connection pool's connection return behavior can be
    configured using ``reset_on_return``::

        from sqlalchemy import create_engine
        from sqlalchemy.pool import QueuePool

        engine = create_engine(
            "mysql+mysqldb://scott:tiger@localhost/myisam_database",
            pool=QueuePool(reset_on_return=False),
        )

我在使用 SQL Server - 我如何将这些 ROLLBACK 转换为 COMMIT？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

I'm on SQL Server - how do I turn those ROLLBACKs into COMMITs?

.. tab:: 中文

    ``reset_on_return`` 参数接受 ``commit``、``rollback``，以及 ``True``、``False`` 和 ``None`` 作为取值。设置为 ``commit`` 时，任何连接在返回连接池时都会执行一次 COMMIT 操作::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@mydsn", pool=QueuePool(reset_on_return="commit")
        )

.. tab:: 英文

    ``reset_on_return`` accepts the values ``commit``, ``rollback`` in addition
    to ``True``, ``False``, and ``None``.   Setting to ``commit`` will cause
    a COMMIT as any connection is returned to the pool::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@mydsn", pool=QueuePool(reset_on_return="commit")
        )

我正在使用与 SQLite 数据库的多个连接（通常用于测试事务操作），并且我的测试程序无法正常工作！
----------------------------------------------------------------------------------------------------------------------------------------------------------

I am using multiple connections with a SQLite database (typically to test transaction operation), and my test program is not working!

.. tab:: 中文

    如果使用 SQLite 的 ``:memory:`` 数据库，默认的连接池是 :class:`.SingletonThreadPool`，该连接池会为每个线程维护一个 SQLite 连接。因此，在同一个线程中使用两个连接实际上会获得同一个 SQLite 连接。请确保不使用内存数据库，以便引擎能够使用 :class:`.QueuePool`（当前 SQLAlchemy 版本中非内存数据库的默认连接池）。

    .. seealso::

        :ref:`pysqlite_threading_pooling` - 有关 PySQLite 行为的更多信息。

.. tab:: 英文

    If using a SQLite ``:memory:`` database the default connection pool is the 
    :class:`.SingletonThreadPool`, which maintains exactly one SQLite connection
    per thread.  So two connections in use in the same thread will actually be 
    the same SQLite connection.  Make sure you're not using a :memory: database
    so that the engine will use :class:`.QueuePool` (the default for non-memory 
    databases in current SQLAlchemy versions).

    .. seealso::

        :ref:`pysqlite_threading_pooling` - info on PySQLite's behavior.

.. _faq_dbapi_connection:

使用引擎时如何获取原始 DBAPI 连接？
--------------------------------------------------------------

How do I get at the raw DBAPI connection when using an Engine?

.. tab:: 中文
    
    对于常规的 SQLAlchemy 引擎级连接对象，可以通过 :class:`_engine.Connection` 的 :attr:`_engine.Connection.connection` 属性访问一个经过连接池代理的 DBAPI 连接版本；而要获取真实的 DBAPI 连接对象，可以访问该对象的 :attr:`.PoolProxiedConnection.dbapi_connection` 属性。对于同步驱动程序，通常不需要直接访问未经过代理的 DBAPI 连接，因为所有方法都已通过代理进行了转发::
    
        engine = create_engine(...)
        conn = engine.connect()
    
        # pep-249 风格的 PoolProxiedConnection（历史上称为 "connection fairy"）
        connection_fairy = conn.connection
    
        # 通常可从该对象获取 cursor() 来执行语句
        cursor_obj = connection_fairy.cursor()
        # ... 与 cursor_obj 交互
    
        # 若需绕过 "connection_fairy"，例如设置未代理的 pep-249 DBAPI 连接的属性，可使用 .dbapi_connection
        raw_dbapi_connection = connection_fairy.dbapi_connection
    
        # 也可以通过 .driver_connection 获取真实的底层连接（下一节将详述）
        also_raw_dbapi_connection = connection_fairy.driver_connection
    
    .. versionchanged:: 1.4.24  
       新增 :attr:`.PoolProxiedConnection.dbapi_connection` 属性，取代先前的
       :attr:`.PoolProxiedConnection.connection` 属性（该属性仍可用）；
       新属性始终提供 pep-249 同步风格的连接对象。
       同时新增 :attr:`.PoolProxiedConnection.driver_connection` 属性，
       无论底层 API 如何实现，该属性总是指向真实的驱动级连接。

.. tab:: 英文

    With a regular SA engine-level Connection, you can get at a pool-proxied
    version of the DBAPI connection via the :attr:`_engine.Connection.connection` attribute on
    :class:`_engine.Connection`, and for the really-real DBAPI connection you can call the
    :attr:`.PoolProxiedConnection.dbapi_connection` attribute on that.  On regular sync drivers
    there is usually no need to access the non-pool-proxied DBAPI connection,
    as all methods are proxied through::
    
        engine = create_engine(...)
        conn = engine.connect()
    
        # pep-249 style PoolProxiedConnection (historically called a "connection fairy")
        connection_fairy = conn.connection
    
        # typically to run statements one would get a cursor() from this
        # object
        cursor_obj = connection_fairy.cursor()
        # ... work with cursor_obj
    
        # to bypass "connection_fairy", such as to set attributes on the
        # unproxied pep-249 DBAPI connection, use .dbapi_connection
        raw_dbapi_connection = connection_fairy.dbapi_connection
    
        # the same thing is available as .driver_connection (more on this
        # in the next section)
        also_raw_dbapi_connection = connection_fairy.driver_connection
    
    .. versionchanged:: 1.4.24  Added the
       :attr:`.PoolProxiedConnection.dbapi_connection` attribute,
       which supersedes the previous
       :attr:`.PoolProxiedConnection.connection` attribute which still remains
       available; this attribute always provides a pep-249 synchronous style
       connection object.  The :attr:`.PoolProxiedConnection.driver_connection`
       attribute is also added which will always refer to the real driver-level
       connection regardless of what API it presents.

访问 asyncio 驱动程序的底层连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Accessing the underlying connection for an asyncio driver

.. tab:: 中文
    
    当使用 asyncio 驱动时，以上方案有两个变化。首先是当使用 :class:`_asyncio.AsyncConnection` 时，必须通过可 await 的方法 :meth:`_asyncio.AsyncConnection.get_raw_connection` 来获取 :class:`.PoolProxiedConnection`。此时返回的 :class:`.PoolProxiedConnection` 保持 pep-249 同步使用模式，:attr:`.PoolProxiedConnection.dbapi_connection` 属性指向的是一个 SQLAlchemy 适配的连接对象，该对象将 asyncio 连接适配为 pep-249 风格的同步 API。换句话说，当使用 asyncio 驱动时，实际上存在 *两层* 代理。而真正的 asyncio 连接可通过 :class:`.PoolProxiedConnection.driver_connection` 属性访问。上例改写为 asyncio 风格如下::
    
        async def main():
            engine = create_async_engine(...)
            conn = await engine.connect()
    
            # pep-249 风格的 ConnectionFairy 连接池代理对象，呈现同步接口
            connection_fairy = await conn.get_raw_connection()
    
            # 此代理下还有第二层代理，适配 asyncio 驱动为 pep-249 接口，通过 .dbapi_connection 访问
            sqla_sync_conn = connection_fairy.dbapi_connection
    
            # 最真实的底层 asyncio 驱动连接可通过 .driver_connection 获取
            raw_asyncio_connection = connection_fairy.driver_connection
    
            # 可使用底层 asyncio 连接进行操作
            result = await raw_asyncio_connection.execute(...)
    
    .. versionchanged:: 1.4.24  
       新增 :attr:`.PoolProxiedConnection.dbapi_connection` 与 
       :attr:`.PoolProxiedConnection.driver_connection` 属性，允许通过统一接口访问
       pep-249 连接、适配层和底层驱动连接。
    
    当使用 asyncio 驱动时，前述“DBAPI”连接实际上是一个由 SQLAlchemy 适配的连接对象，它提供同步风格的 pep-249 API。要访问实际的 asyncio 驱动连接（即驱动提供的原始 asyncio API 接口），可通过 :class:`.PoolProxiedConnection` 的 :attr:`.PoolProxiedConnection.driver_connection` 属性访问。
    对于标准 pep-249 驱动，:attr:`.PoolProxiedConnection.dbapi_connection` 与 :attr:`.PoolProxiedConnection.driver_connection` 是等价的。
    
    你必须确保在将连接返回连接池前，复原任何隔离级别设置或其他操作相关的设置。
    
    作为替代方式，也可以在 :class:`_engine.Connection` 或其代理连接上调用 :meth:`_engine.Connection.detach` 方法，将连接从连接池中解除绑定。这样，当调用 :meth:`_engine.Connection.close` 时，该连接将被真正关闭并从池中移除:
    
    .. sourcecode:: text

        conn = engine.connect()
        conn.detach()  # 将 DBAPI 连接从连接池中解绑
        conn.connection.<go nuts>
        conn.close()  # 连接被真正关闭，连接池将创建新连接替代

.. tab:: 英文

    When an asyncio driver is in use, there are two changes to the above
    scheme.  The first is that when using an :class:`_asyncio.AsyncConnection`,
    the :class:`.PoolProxiedConnection` must be accessed using the awaitable method
    :meth:`_asyncio.AsyncConnection.get_raw_connection`.   The
    returned :class:`.PoolProxiedConnection` in this case retains a sync-style
    pep-249 usage pattern, and the :attr:`.PoolProxiedConnection.dbapi_connection`
    attribute refers to a
    a SQLAlchemy-adapted connection object which adapts the asyncio
    connection to a sync style pep-249 API, in other words there are *two* levels
    of proxying going on when using an asyncio driver.   The actual asyncio connection
    is available from the :class:`.PoolProxiedConnection.driver_connection` attribute.
    To restate the previous example in terms of asyncio looks like::
    
        async def main():
            engine = create_async_engine(...)
            conn = await engine.connect()
    
            # pep-249 style ConnectionFairy connection pool proxy object
            # presents a sync interface
            connection_fairy = await conn.get_raw_connection()
    
            # beneath that proxy is a second proxy which adapts the
            # asyncio driver into a pep-249 connection object, accessible
            # via .dbapi_connection as is the same with a sync API
            sqla_sync_conn = connection_fairy.dbapi_connection
    
            # the really-real innermost driver connection is available
            # from the .driver_connection attribute
            raw_asyncio_connection = connection_fairy.driver_connection
    
            # work with raw asyncio connection
            result = await raw_asyncio_connection.execute(...)
    
    .. versionchanged:: 1.4.24  Added the
       :attr:`.PoolProxiedConnection.dbapi_connection`
       and :attr:`.PoolProxiedConnection.driver_connection` attributes to allow access
       to pep-249 connections, pep-249 adaption layers, and underlying driver
       connections using a consistent interface.
    
    When using asyncio drivers, the above "DBAPI" connection is actually a
    SQLAlchemy-adapted form of connection which presents a synchronous-style
    pep-249 style API.  To access the actual
    asyncio driver connection, which will present the original asyncio API
    of the driver in use, this can be accessed via the
    :attr:`.PoolProxiedConnection.driver_connection` attribute of
    :class:`.PoolProxiedConnection`.
    For a standard pep-249 driver, :attr:`.PoolProxiedConnection.dbapi_connection`
    and :attr:`.PoolProxiedConnection.driver_connection` are synonymous.
    
    You must ensure that you revert any isolation level settings or other
    operation-specific settings on the connection back to normal before returning
    it to the pool.
    
    As an alternative to reverting settings, you can call the
    :meth:`_engine.Connection.detach` method on either :class:`_engine.Connection`
    or the proxied connection, which will de-associate the connection from the pool
    such that it will be closed and discarded when :meth:`_engine.Connection.close`
    is called:
    
    .. sourcecode:: text
    
        conn = engine.connect()
        conn.detach()  # detaches the DBAPI connection from the connection pool
        conn.connection.<go nuts>
        conn.close()  # connection is closed for real, the pool replaces it with a new connection

如何将引擎/连接/会话与 Python 多处理或 os.fork() 结合使用？
----------------------------------------------------------------------------------------

How do I use engines / connections / sessions with Python multiprocessing, or os.fork()?

.. tab:: 中文

    这部分内容在 :ref:`pooling_multiprocessing` 部分中有介绍。

.. tab:: 英文

    This is covered in the section :ref:`pooling_multiprocessing`.

