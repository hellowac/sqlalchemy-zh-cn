======================================
事务和连接管理
======================================

Transactions and Connection Management

.. _unitofwork_transaction:

管理事务
=====================

Managing Transactions

.. tab:: 中文

    .. versionchanged:: 1.4 

        Session 的事务管理逻辑已被重新设计，使其更加清晰和易于使用。特别是现在引入了 “autobegin” 操作，意味着可以控制事务的开始点，而无需依赖传统的 “autocommit” 模式。

    :class:`_orm.Session` 一次只追踪一个“虚拟”事务（virtual transaction）的状态，  
    它使用一个名为 :class:`_orm.SessionTransaction` 的对象来实现这一点。  
    该对象会在需要时通过底层的 :class:`_engine.Engine` 或绑定到 :class:`_orm.Session` 的多个 engine，  
    来使用 :class:`_engine.Connection` 启动真正的连接级事务。

    这个“虚拟”事务会在需要时自动创建，  
    也可以通过显式调用 :meth:`_orm.Session.begin` 方法来启动。  
    在尽可能的范围内，Python 的上下文管理器语法可用于创建 :class:`_orm.Session` 对象，  
    也可以用于维持 :class:`_orm.SessionTransaction` 的作用域。

    以下是一个基本的 :class:`_orm.Session` 使用示例::

        from sqlalchemy.orm import Session

        session = Session(engine)

    我们可以使用上下文管理器语法，在明确的事务作用域中执行操作::

        with session.begin():
            session.add(some_object())
            session.add(some_other_object())
        # 上下文结束时提交事务；如果有异常抛出则会回滚事务

    在上述代码块结束时，如果没有异常抛出，任何待处理的对象都会被 flush 到数据库中，  
    随后数据库事务会被提交；若代码块中抛出了异常，则事务会被回滚。  
    无论是哪种情况，该 :class:`_orm.Session` 在离开代码块之后都可以继续用于下一个事务。

    :meth:`_orm.Session.begin` 方法是可选的，  
    也可以采用“边执行边提交”的模式来使用 :class:`_orm.Session`，  
    这种模式下事务会按需自动开启；用户只需在合适的时机进行提交或回滚::

        session = Session(engine)

        session.add(some_object())
        session.add(some_other_object())

        session.commit()  # 提交事务

        # 会自动重新开始新事务
        result = session.execute(text("< some select statement >"))
        session.add_all([more_objects, ...])
        session.commit()  # 再次提交

        session.add(still_another_object)
        session.flush()  # flush still_another_object
        session.rollback()  # 回滚 still_another_object 的更改

    :class:`_orm.Session` 本身提供了一个 :meth:`_orm.Session.close` 方法。  
    如果此时仍处于一个尚未提交或回滚的事务中，调用该方法将取消（即回滚）该事务，  
    并从该 :class:`_orm.Session` 的状态中移除所有对象。  
    如果 :class:`_orm.Session` 的使用方式不能保证一定会调用 :meth:`_orm.Session.commit` 或 :meth:`_orm.Session.rollback`（例如没有在上下文管理器中使用），  
    可以通过调用 :meth:`_orm.Session.close` 来确保所有资源被正确释放::

        # 清除所有对象、无条件回滚事务并释放连接资源
        session.close()

    最后，Session 的创建和关闭过程本身也可以使用上下文管理器语法管理。  
    这是确保 :class:`_orm.Session` 使用范围受控的最佳方式。  
    首先通过 :class:`_orm.Session` 构造器来演示::

        with Session(engine) as session:
            session.add(some_object())
            session.add(some_other_object())

            session.commit()  # 提交事务

            session.add(still_another_object)
            session.flush()  # flush still_another_object

            session.commit()  # 再次提交

            result = session.execute(text("<some SELECT statement>"))

        # 上述 execute() 调用产生的剩余事务状态将被丢弃

    同样，:class:`_orm.sessionmaker` 也可以以相同方式使用::

        Session = sessionmaker(engine)

        with Session() as session:
            with session.begin():
                session.add(some_object)
            # 提交事务

        # 关闭 Session

    :class:`_orm.sessionmaker` 本身也包含一个 :meth:`_orm.sessionmaker.begin` 方法，  
    用于一次性执行创建和开启事务两个操作::

        with Session.begin() as session:
            session.add(some_object)


.. tab:: 英文

    .. versionchanged:: 1.4 
        
        Session transaction management has been revised to be clearer and easier to use.  In particular, it now features "autobegin" operation, which means the point at which a transaction begins may be controlled, without using the legacy "autocommit" mode.

    The :class:`_orm.Session` tracks the state of a single "virtual" transaction at a time, using an object called :class:`_orm.SessionTransaction`.   This object then makes use of the underlying :class:`_engine.Engine` or engines to which the :class:`_orm.Session` object is bound in order to start real connection-level transactions using the :class:`_engine.Connection` object as needed.

    This "virtual" transaction is created automatically when needed, or can alternatively be started using the :meth:`_orm.Session.begin` method.  To as great a degree as possible, Python context manager use is supported both at the level of creating :class:`_orm.Session` objects as well as to maintain the scope of the :class:`_orm.SessionTransaction`.

    Below, assume we start with a :class:`_orm.Session`::

        from sqlalchemy.orm import Session

        session = Session(engine)

    We can now run operations within a demarcated transaction using a context manager::

        with session.begin():
            session.add(some_object())
            session.add(some_other_object())
        # commits transaction at the end, or rolls back if there
        # was an exception raised

    At the end of the above context, assuming no exceptions were raised, any pending objects will be flushed to the database and the database transaction will be committed. If an exception was raised within the above block, then the transaction would be rolled back.  In both cases, the above :class:`_orm.Session` subsequent to exiting the block is ready to be used in subsequent transactions.

    The :meth:`_orm.Session.begin` method is optional, and the :class:`_orm.Session` may also be used in a commit-as-you-go approach, where it will begin transactions automatically as needed; these only need be committed or rolled back::

        session = Session(engine)

        session.add(some_object())
        session.add(some_other_object())

        session.commit()  # commits

        # will automatically begin again
        result = session.execute(text("< some select statement >"))
        session.add_all([more_objects, ...])
        session.commit()  # commits

        session.add(still_another_object)
        session.flush()  # flush still_another_object
        session.rollback()  # rolls back still_another_object

    The :class:`_orm.Session` itself features a :meth:`_orm.Session.close` method.  If the :class:`_orm.Session` is begun within a transaction that has not yet been committed or rolled back, this method will cancel (i.e. rollback) that transaction, and also expunge all objects contained within the :class:`_orm.Session` object's state.   If the :class:`_orm.Session` is being used in such a way that a call to :meth:`_orm.Session.commit` or :meth:`_orm.Session.rollback` is not guaranteed (e.g. not within a context manager or similar), the :class:`_orm.Session.close` method may be used to ensure all resources are released::

        # expunges all objects, releases all transactions unconditionally
        # (with rollback), releases all database connections back to their
        # engines
        session.close()

    Finally, the session construction / close process can itself be run via context manager.  This is the best way to ensure that the scope of a :class:`_orm.Session` object's use is scoped within a fixed block. Illustrated via the :class:`_orm.Session` constructor first::

        with Session(engine) as session:
            session.add(some_object())
            session.add(some_other_object())

            session.commit()  # commits

            session.add(still_another_object)
            session.flush()  # flush still_another_object

            session.commit()  # commits

            result = session.execute(text("<some SELECT statement>"))

        # remaining transactional state from the .execute() call is
        # discarded

    Similarly, the :class:`_orm.sessionmaker` can be used in the same way::

        Session = sessionmaker(engine)

        with Session() as session:
            with session.begin():
                session.add(some_object)
            # commits

        # closes the Session

    :class:`_orm.sessionmaker` itself includes a :meth:`_orm.sessionmaker.begin` method to allow both operations to take place at once::

        with Session.begin() as session:
            session.add(some_object)

.. _session_begin_nested:

使用 SAVEPOINT
---------------

Using SAVEPOINT

.. tab:: 中文

    如果底层数据库引擎支持 `SAVEPOINT` 事务，则可以使用 :meth:`~.Session.begin_nested` 方法来划定一个保存点（SAVEPOINT）::

        Session = sessionmaker()

        with Session.begin() as session:
            session.add(u1)
            session.add(u2)

            nested = session.begin_nested()  # 创建一个保存点
            session.add(u3)
            nested.rollback()  # 回滚 u3，保留 u1 和 u2

        # 提交 u1 和 u2

    每次调用 :meth:`_orm.Session.begin_nested` 时，都会向数据库发出一个新的 “BEGIN SAVEPOINT” 命令（如果尚未处于事务中，则会先开始一个事务），  
    并返回一个 :class:`_orm.SessionTransaction` 类型的对象，作为该保存点的句柄。  
    调用该对象的 ``.commit()`` 方法将向数据库发出 “RELEASE SAVEPOINT” 命令；  
    而调用 ``.rollback()`` 方法则发出 “ROLLBACK TO SAVEPOINT” 命令。  
    外层数据库事务将继续保持进行中状态。

    :meth:`_orm.Session.begin_nested` 通常结合上下文管理器一起使用，  
    可用于捕捉每个记录级别的错误并针对当前事务的一部分状态进行回滚，  
    而不影响整个事务，例如::

        for record in records:
            try:
                with session.begin_nested():
                    session.merge(record)
            except:
                print("Skipped record %s" % record)
        session.commit()

    当 :meth:`_orm.Session.begin_nested` 所返回的上下文管理器退出时，  
    该保存点将被“提交”，并执行常规的 flush 行为以同步所有挂起状态。  
    如果在上下文块中抛出异常，该保存点将被回滚，  
    同时与此次嵌套事务有关的 :class:`_orm.Session` 中的对象状态将被过期（expired）。

    这种模式非常适用于如 PostgreSQL 场景下捕捉 :class:`.IntegrityError` 异常来检测主键冲突；  
    PostgreSQL 默认在遇到此类错误时会中止整个事务，  
    但使用 SAVEPOINT 机制时，外层事务可以保持继续进行。  
    下面的示例中，一组数据将尝试写入数据库，对于偶尔出现的“主键重复”记录将跳过，  
    而不影响整个操作::

        from sqlalchemy import exc

        with session.begin():
            for record in records:
                try:
                    with session.begin_nested():
                        obj = SomeRecord(id=record["identifier"], name=record["name"])
                        session.add(obj)
                except exc.IntegrityError:
                    print(f"Skipped record {record} - row already exists")

    调用 :meth:`~.Session.begin_nested` 时，:class:`_orm.Session` 会首先将当前所有挂起状态 flush 到数据库中；  
    这个行为是无条件的，即使指定了 :paramref:`_orm.Session.autoflush=False` 也不会跳过。  
    其设计目的是：当嵌套事务回滚时，能够明确识别并过期掉保存点范围内所修改的内存对象状态，  
    同时确保这些对象在刷新时能从数据库重新加载其在保存点开始前的状态。

    在 SQLAlchemy 的现代版本中，当使用 :meth:`_orm.Session.begin_nested` 创建的保存点被回滚时，  
    自该保存点起被修改过的内存对象状态将被标记为过期（expired），  
    而未被更改的对象状态则会保留，  
    这样后续操作可以继续使用这些未受影响的数据，而无需重新从数据库加载。

    .. seealso::

        :meth:`_engine.Connection.begin_nested` -  Core 层级的 SAVEPOINT 接口


.. tab:: 英文

    SAVEPOINT transactions, if supported by the underlying engine, may be delineated using the :meth:`~.Session.begin_nested` method::


        Session = sessionmaker()

        with Session.begin() as session:
            session.add(u1)
            session.add(u2)

            nested = session.begin_nested()  # establish a savepoint
            session.add(u3)
            nested.rollback()  # rolls back u3, keeps u1 and u2

        # commits u1 and u2

    Each time :meth:`_orm.Session.begin_nested` is called, a new "BEGIN SAVEPOINT" command is emitted to the database within the scope of the current database transaction (starting one if not already in progress), and an object of type :class:`_orm.SessionTransaction` is returned, which represents a handle to this SAVEPOINT.  When the ``.commit()`` method on this object is called, "RELEASE SAVEPOINT" is emitted to the database, and if instead the ``.rollback()`` method is called, "ROLLBACK TO SAVEPOINT" is emitted.  The enclosing database transaction remains in progress.

    :meth:`_orm.Session.begin_nested` is typically used as a context manager where specific per-instance errors may be caught, in conjunction with a rollback emitted for that portion of the transaction's state, without rolling back the whole transaction, as in the example below::

        for record in records:
            try:
                with session.begin_nested():
                    session.merge(record)
            except:
                print("Skipped record %s" % record)
        session.commit()

    When the context manager yielded by :meth:`_orm.Session.begin_nested` completes, it "commits" the savepoint, which includes the usual behavior of flushing all pending state.  When an error is raised, the savepoint is rolled back and the state of the :class:`_orm.Session` local to the objects that were changed is expired.

    This pattern is ideal for situations such as using PostgreSQL and catching :class:`.IntegrityError` to detect duplicate rows; PostgreSQL normally aborts the entire transaction when such an error is raised, however when using SAVEPOINT, the outer transaction is maintained.   In the example below a list of data is persisted into the database, with the occasional "duplicate primary key" record skipped, without rolling back the entire operation::

        from sqlalchemy import exc

        with session.begin():
            for record in records:
                try:
                    with session.begin_nested():
                        obj = SomeRecord(id=record["identifier"], name=record["name"])
                        session.add(obj)
                except exc.IntegrityError:
                    print(f"Skipped record {record} - row already exists")

    When :meth:`~.Session.begin_nested` is called, the :class:`_orm.Session` first flushes all currently pending state to the database; this occurs unconditionally, regardless of the value of the :paramref:`_orm.Session.autoflush` parameter which normally may be used to disable automatic flush.  The rationale for this behavior is so that when a rollback on this nested transaction occurs, the :class:`_orm.Session` may expire any in-memory state that was created within the scope of the SAVEPOINT, while ensuring that when those expired objects are refreshed, the state of the object graph prior to the beginning of the SAVEPOINT will be available to re-load from the database.

    In modern versions of SQLAlchemy, when a SAVEPOINT initiated by :meth:`_orm.Session.begin_nested` is rolled back, in-memory object state that was modified since the SAVEPOINT was created is expired, however other object state that was not altered since the SAVEPOINT began is maintained.  This is so that subsequent operations can continue to make use of the otherwise unaffected data without the need for refreshing it from the database.

    .. seealso::

        :meth:`_engine.Connection.begin_nested` -  Core SAVEPOINT API

.. _orm_session_vs_engine:

会话级与引擎级事务控制
--------------------------------------------------

Session-level vs. Engine level transaction control

.. tab:: 中文

    :class:`_engine.Connection`（Core）与 :class:`_session.Session`（ORM）在事务语义方面是等价的，  
    无论是在 :class:`_orm.sessionmaker` 与 :class:`_engine.Engine` 的层级，  
    还是 :class:`_orm.Session` 与 :class:`_engine.Connection` 的层级。  
    以下章节将根据如下对照表详细说明这些场景：

    .. sourcecode:: text

        ORM                                           Core
        -----------------------------------------     -----------------------------------
        sessionmaker                                  Engine
        Session                                       Connection
        sessionmaker.begin()                          Engine.begin()
        some_session.commit()                         some_connection.commit()
        with some_sessionmaker() as session:          with some_engine.connect() as conn:
        with some_sessionmaker.begin() as session:    with some_engine.begin() as conn:
        with some_session.begin_nested() as sp:       with some_connection.begin_nested() as sp:


.. tab:: 英文

    The :class:`_engine.Connection` in Core and :class:`_session.Session` in ORM feature equivalent transactional semantics, both at the level of the :class:`_orm.sessionmaker` vs. the :class:`_engine.Engine`, as well as the :class:`_orm.Session` vs. the :class:`_engine.Connection`.  The following sections detail these scenarios based on the following scheme:

    .. sourcecode:: text

        ORM                                           Core
        -----------------------------------------     -----------------------------------
        sessionmaker                                  Engine
        Session                                       Connection
        sessionmaker.begin()                          Engine.begin()
        some_session.commit()                         some_connection.commit()
        with some_sessionmaker() as session:          with some_engine.connect() as conn:
        with some_sessionmaker.begin() as session:    with some_engine.begin() as conn:
        with some_session.begin_nested() as sp:       with some_connection.begin_nested() as sp:

随时提交
~~~~~~~~~~~~~~~~

Commit as you go

.. tab:: 中文

    :class:`_orm.Session` 与 :class:`_engine.Connection` 都提供了 :meth:`_engine.Connection.commit` 和 :meth:`_engine.Connection.rollback` 方法。  
    在 SQLAlchemy 2.0 风格的操作中，这些方法始终作用于 **最外层事务**。  
    对于 :class:`_orm.Session`，假定 :paramref:`_orm.Session.autobegin` 参数保留默认值 ``True``。

    :class:`_engine.Engine` 示例::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.connect() as conn:
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
            conn.commit()

    :class:`_orm.Session` 示例::

        Session = sessionmaker(engine)

        with Session() as session:
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
            session.commit()

.. tab:: 英文

    Both :class:`_orm.Session` and :class:`_engine.Connection` feature :meth:`_engine.Connection.commit` and :meth:`_engine.Connection.rollback` methods.   Using SQLAlchemy 2.0-style operation, these methods affect the **outermost** transaction in all cases.   For the :class:`_orm.Session`, it is assumed that :paramref:`_orm.Session.autobegin` is left at its default value of ``True``.

    :class:`_engine.Engine`::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.connect() as conn:
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
            conn.commit()

    :class:`_orm.Session`::

        Session = sessionmaker(engine)

        with Session() as session:
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
            session.commit()

开始一次
~~~~~~~~~~

Begin Once

.. tab:: 中文

    :class:`_orm.sessionmaker` 与 :class:`_engine.Engine` 都提供了 :meth:`_engine.Engine.begin` 方法，  
    用于创建一个新的 SQL 执行对象（ORM 中为 :class:`_orm.Session`，Core 中为 :class:`_engine.Connection`），  
    并返回一个上下文管理器，用于封装该对象的事务处理（开始、提交或回滚）。

    Engine 示例::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.begin() as conn:
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
        # 自动提交并关闭连接

    Session 示例::

        Session = sessionmaker(engine)

        with Session.begin() as session:
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
        # 自动提交并关闭会话

.. tab:: 英文

    Both :class:`_orm.sessionmaker` and :class:`_engine.Engine` feature a :meth:`_engine.Engine.begin` method that will both procure a new object with which to execute SQL statements (the :class:`_orm.Session` and :class:`_engine.Connection`, respectively) and then return a context manager that will maintain a begin/commit/rollback context for that object.

    Engine::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.begin() as conn:
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
        # commits and closes automatically

    Session::

        Session = sessionmaker(engine)

        with Session.begin() as session:
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
        # commits and closes automatically

嵌套事务
~~~~~~~~~~~~~~~~~~~~

Nested Transaction

.. tab:: 中文

    当使用 :meth:`_orm.Session.begin_nested` 或 :meth:`_engine.Connection.begin_nested` 方法时，返回的事务对象必须用于提交或回滚该 SAVEPOINT。  
    调用 :meth:`_orm.Session.commit` 或 :meth:`_engine.Connection.commit` 方法将始终提交 **最外层** 事务；这是 SQLAlchemy 2.0 特有的行为，与 1.x 版本系列相反。

    Engine 示例::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.begin() as conn:
            savepoint = conn.begin_nested()
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
            savepoint.commit()  # 或者回滚

        # 自动提交

    Session 示例::

        Session = sessionmaker(engine)

        with Session.begin() as session:
            savepoint = session.begin_nested()
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
            savepoint.commit()  # 或者回滚
        # 自动提交


.. tab:: 英文

    When using a SAVEPOINT via the :meth:`_orm.Session.begin_nested` or :meth:`_engine.Connection.begin_nested` methods, the transaction object returned must be used to commit or rollback the SAVEPOINT.  Calling the :meth:`_orm.Session.commit` or :meth:`_engine.Connection.commit` methods will always commit the **outermost** transaction; this is a SQLAlchemy 2.0 specific behavior that is reversed from the 1.x series.

    Engine::

        engine = create_engine("postgresql+psycopg2://user:pass@host/dbname")

        with engine.begin() as conn:
            savepoint = conn.begin_nested()
            conn.execute(
                some_table.insert(),
                [
                    {"data": "some data one"},
                    {"data": "some data two"},
                    {"data": "some data three"},
                ],
            )
            savepoint.commit()  # or rollback

        # commits automatically

    Session::

        Session = sessionmaker(engine)

        with Session.begin() as session:
            savepoint = session.begin_nested()
            session.add_all(
                [
                    SomeClass(data="some data one"),
                    SomeClass(data="some data two"),
                    SomeClass(data="some data three"),
                ]
            )
            savepoint.commit()  # or rollback
        # commits automatically

.. _session_explicit_begin:

显式开始
---------------

Explicit Begin

.. tab:: 中文

    :class:`_orm.Session` 具有 "autobegin" 行为，意味着一旦开始执行操作，它会确保有一个 :class:`_orm.SessionTransaction` 用来追踪正在进行的操作。  
    该事务会在调用 :meth:`_orm.Session.commit` 时完成。

    在框架集成中，通常希望控制“开始”操作的时机。为此， :class:`_orm.Session` 使用了一个 "autobegin" 策略，使得即使是尚未开始事务的 :class:`_orm.Session`，  
    也可以直接调用 :meth:`_orm.Session.begin` 方法::

        Session = sessionmaker(bind=engine)
        session = Session()
        session.begin()
        try:
            item1 = session.get(Item, 1)
            item2 = session.get(Item, 2)
            item1.foo = "bar"
            item2.bar = "foo"
            session.commit()
        except:
            session.rollback()
            raise

    上述模式通常通过上下文管理器以更符合惯例的方式调用::

        Session = sessionmaker(bind=engine)
        session = Session()
        with session.begin():
            item1 = session.get(Item, 1)
            item2 = session.get(Item, 2)
            item1.foo = "bar"
            item2.bar = "foo"

    :meth:`_orm.Session.begin` 方法和会话的 "autobegin" 过程使用相同的步骤来启动事务。  
    这包括在启动事务时会调用 :meth:`_orm.SessionEvents.after_transaction_create` 事件；该钩子允许框架在 ORM :class:`_orm.Session` 的事务处理流程中集成其自定义的事务处理过程。

.. tab:: 英文

    The :class:`_orm.Session` features "autobegin" behavior, meaning that as soon as operations begin to take place, it ensures a :class:`_orm.SessionTransaction` is present to track ongoing operations.   This transaction is completed when :meth:`_orm.Session.commit` is called.

    It is often desirable, particularly in framework integrations, to control the point at which the "begin" operation occurs.  To suit this, the :class:`_orm.Session` uses an "autobegin" strategy, such that the :meth:`_orm.Session.begin` method may be called directly for a :class:`_orm.Session` that has not already had a transaction begun::

        Session = sessionmaker(bind=engine)
        session = Session()
        session.begin()
        try:
            item1 = session.get(Item, 1)
            item2 = session.get(Item, 2)
            item1.foo = "bar"
            item2.bar = "foo"
            session.commit()
        except:
            session.rollback()
            raise

    The above pattern is more idiomatically invoked using a context manager::

        Session = sessionmaker(bind=engine)
        session = Session()
        with session.begin():
            item1 = session.get(Item, 1)
            item2 = session.get(Item, 2)
            item1.foo = "bar"
            item2.bar = "foo"

    The :meth:`_orm.Session.begin` method and the session's "autobegin" process use the same sequence of steps to begin the transaction.   This includes that the :meth:`_orm.SessionEvents.after_transaction_create` event is invoked when it occurs; this hook is used by frameworks in order to integrate their own transactional processes with that of the ORM :class:`_orm.Session`.



.. _session_twophase:

启用两阶段提交
-------------------------

Enabling Two-Phase Commit

.. tab:: 中文

    对于支持两阶段操作的后端（目前为 MySQL 和 PostgreSQL），可以指示会话使用两阶段提交语义。这将协调跨数据库的事务提交，以确保事务在所有数据库中要么提交，要么回滚。你还可以通过 :meth:`_orm.Session.prepare` 方法准备会话与 SQLAlchemy 未管理的事务进行交互。要使用两阶段事务，在会话中设置标志 ``twophase=True``::

        engine1 = create_engine("postgresql+psycopg2://db1")
        engine2 = create_engine("postgresql+psycopg2://db2")

        Session = sessionmaker(twophase=True)

        # 将 User 操作绑定到 engine 1，将 Account 操作绑定到 engine 2
        Session.configure(binds={User: engine1, Account: engine2})

        session = Session()

        # .... 处理账户和用户

        # 提交。会话将向所有数据库发出刷新，并对所有数据库执行准备步骤，
        # 然后提交两个事务
        session.commit()


.. tab:: 英文

    For backends which support two-phase operation (currently MySQL and PostgreSQL), the session can be instructed to use two-phase commit semantics. This will coordinate the committing of transactions across databases so that the transaction is either committed or rolled back in all databases. You can also :meth:`_orm.Session.prepare` the session for interacting with transactions not managed by SQLAlchemy. To use two phase transactions set the flag ``twophase=True`` on the session::

        engine1 = create_engine("postgresql+psycopg2://db1")
        engine2 = create_engine("postgresql+psycopg2://db2")

        Session = sessionmaker(twophase=True)

        # bind User operations to engine 1, Account operations to engine 2
        Session.configure(binds={User: engine1, Account: engine2})

        session = Session()

        # .... work with accounts and users

        # commit.  session will issue a flush to all DBs, and a prepare step to all DBs,
        # before committing both transactions
        session.commit()

.. _session_transaction_isolation:

设置事务隔离级别/DBAPI AUTOCOMMIT
-------------------------------------------------------

Setting Transaction Isolation Levels / DBAPI AUTOCOMMIT

.. tab:: 中文

    大多数 DBAPI 支持可配置的事务隔离级别。传统上有四个级别：“READ UNCOMMITTED”（读未提交）、“READ COMMITTED”（读已提交）、“REPEATABLE READ”（可重复读）和“SERIALIZABLE”（可串行化）。  
    这些通常在 DBAPI 连接开始新事务之前应用，注意大多数 DBAPI 在首次发出 SQL 语句时会隐式开始该事务。

    支持隔离级别的 DBAPI 通常还支持真正的“自动提交”概念，这意味着 DBAPI 连接将被置于非事务性自动提交模式。  
    这通常意味着 DBAPI 的典型行为（自动发出 "BEGIN" 语句到数据库）不再发生，但也可能包括其他指令。  
    在使用此模式时， **DBAPI 在任何情况下都不使用事务**。像 ``.begin()``, ``.commit()`` 和 ``.rollback()`` 等 SQLAlchemy 方法将默默通过，不做任何操作。

    SQLAlchemy 的方言支持在每个 :class:`_engine.Engine` 或 :class:`_engine.Connection` 上设置隔离模式，  
    通过在 :func:`_sa.create_engine` 和 :meth:`_engine.Connection.execution_options` 级别上的标志进行配置。

    当使用 ORM :class:`.Session` 时，它作为引擎和连接的 *外观*，但不会直接暴露事务隔离。  
    因此，为了影响事务隔离级别，我们需要根据需要操作 :class:`_engine.Engine` 或 :class:`_engine.Connection`。

    .. seealso::

        :ref:`dbapi_autocommit` - 请确保查看 SQLAlchemy :class:`_engine.Connection` 对象级别的隔离级别如何工作。

.. tab:: 英文

    Most DBAPIs support the concept of configurable transaction :term:`isolation` levels. These are traditionally the four levels "READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ" and "SERIALIZABLE".  These are usually applied to a DBAPI connection before it begins a new transaction, noting that most DBAPIs will begin this transaction implicitly when SQL statements are first emitted.

    DBAPIs that support isolation levels also usually support the concept of true "autocommit", which means that the DBAPI connection itself will be placed into a non-transactional autocommit mode.   This usually means that the typical DBAPI behavior of emitting "BEGIN" to the database automatically no longer occurs, but it may also include other directives.   When using this mode, **the DBAPI does not use a transaction under any circumstances**.  SQLAlchemy methods like ``.begin()``, ``.commit()`` and ``.rollback()`` pass silently.

    SQLAlchemy's dialects support settable isolation modes on a per-:class:`_engine.Engine` or per-:class:`_engine.Connection` basis, using flags at both the :func:`_sa.create_engine` level as well as at the :meth:`_engine.Connection.execution_options` level.

    When using the ORM :class:`.Session`, it acts as a *facade* for engines and connections, but does not expose transaction isolation directly.  So in order to affect transaction isolation level, we need to act upon the :class:`_engine.Engine` or :class:`_engine.Connection` as appropriate.

    .. seealso::

        :ref:`dbapi_autocommit` - be sure to review how isolation levels work at the level of the SQLAlchemy :class:`_engine.Connection` object as well.

.. _session_transaction_isolation_enginewide:

为 Sessionmaker/引擎范围设置隔离
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting Isolation For A Sessionmaker / Engine Wide

.. tab:: 中文

    要全局设置特定隔离级别的 :class:`.Session` 或 :class:`.sessionmaker`，第一种方法是，可以通过在所有情况下构造一个具有特定隔离级别的 :class:`_engine.Engine`，然后将其用作 :class:`_orm.Session` 和/或 :class:`_orm.sessionmaker` 的连接源::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        eng = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test",
            isolation_level="REPEATABLE READ",
        )

        Session = sessionmaker(eng)

    另一种方法，适用于同时有两个不同隔离级别的引擎，是使用 :meth:`_engine.Engine.execution_options` 方法，它将生成原始 :class:`_engine.Engine` 的浅拷贝，并共享与父引擎相同的连接池。  
    当操作被分成“事务性”和“自动提交”操作时，这种方法通常更合适::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        eng = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = eng.execution_options(isolation_level="AUTOCOMMIT")

        transactional_session = sessionmaker(eng)
        autocommit_session = sessionmaker(autocommit_engine)

    如上所示，"``eng``" 和 "``autocommit_engine``" 共享相同的方言和连接池。  
    然而，当从 ``autocommit_engine`` 获取连接时，将设置“AUTOCOMMIT”模式。  
    这两个 :class:`_orm.sessionmaker` 对象 "``transactional_session``" 和 "``autocommit_session``" 在与数据库连接交互时，将继承这些特性。

    "``autocommit_session``" **仍然具有事务语义**，包括 :meth:`_orm.Session.commit` 和 :meth:`_orm.Session.rollback` 仍然将自己视为“提交”和“回滚”对象，  
    但是事务将默默缺失。正因为如此， **通常（尽管不是严格要求）建议使用 AUTOCOMMIT 隔离级别的会话时以只读方式使用**，即::

        with autocommit_session() as session:
            some_objects = session.execute(text("<statement>"))
            some_other_objects = session.execute(text("<statement>"))

        # 连接关闭


.. tab:: 英文

    To set up a :class:`.Session` or :class:`.sessionmaker` with a specific isolation level globally, the first technique is that an :class:`_engine.Engine` can be constructed against a specific isolation level in all cases, which is then used as the source of connectivity for a :class:`_orm.Session` and/or :class:`_orm.sessionmaker`::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        eng = create_engine(
            "postgresql+psycopg2://scott:tiger@localhost/test",
            isolation_level="REPEATABLE READ",
        )

        Session = sessionmaker(eng)

    Another option, useful if there are to be two engines with different isolation levels at once, is to use the :meth:`_engine.Engine.execution_options` method, which will produce a shallow copy of the original :class:`_engine.Engine` which shares the same connection pool as the parent engine.  This is often preferable when operations will be separated into "transactional" and "autocommit" operations::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        eng = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = eng.execution_options(isolation_level="AUTOCOMMIT")

        transactional_session = sessionmaker(eng)
        autocommit_session = sessionmaker(autocommit_engine)

    Above, both "``eng``" and ``"autocommit_engine"`` share the same dialect and connection pool.  However the "AUTOCOMMIT" mode will be set upon connections when they are acquired from the ``autocommit_engine``.  The two :class:`_orm.sessionmaker` objects "``transactional_session``" and "``autocommit_session"`` then inherit these characteristics when they work with database connections.


    The "``autocommit_session``" **continues to have transactional semantics**, including that :meth:`_orm.Session.commit` and :meth:`_orm.Session.rollback` still consider themselves to be "committing" and "rolling back" objects, however the transaction will be silently absent.  For this reason, **it is typical, though not strictly required, that a Session with AUTOCOMMIT isolation be used in a read-only fashion**, that is::


        with autocommit_session() as session:
            some_objects = session.execute(text("<statement>"))
            some_other_objects = session.execute(text("<statement>"))

        # closes connection

为单个会话设置隔离
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting Isolation for Individual Sessions

.. tab:: 中文

    当我们创建新的 :class:`.Session` 时，既可以直接使用构造函数，也可以使用 :class:`.sessionmaker` 生成的可调用对象，我们可以直接传递 ``bind`` 参数，覆盖预先存在的绑定。  
    例如，我们可以从默认的 :class:`.sessionmaker` 创建 :class:`_orm.Session`，并传递设置为自动提交的引擎::

        plain_engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = plain_engine.execution_options(isolation_level="AUTOCOMMIT")

        # 通常使用 plain_engine
        Session = sessionmaker(plain_engine)

        # 创建一个特定的会话，将使用 "autocommit" 引擎
        with Session(bind=autocommit_engine) as session:
            # 与会话一起工作
            ...

    如果 :class:`.Session` 或 :class:`.sessionmaker` 配置了多个“bind”，我们可以完全重新指定 ``binds`` 参数，  
    或者如果我们只想替换特定的绑定，可以使用 :meth:`.Session.bind_mapper` 或 :meth:`.Session.bind_table` 方法::

        with Session() as session:
            session.bind_mapper(User, autocommit_engine)

.. tab:: 英文

    When we make a new :class:`.Session`, either using the constructor directly or when we call upon the callable produced by a :class:`.sessionmaker`, we can pass the ``bind`` argument directly, overriding the pre-existing bind. We can for example create our :class:`_orm.Session` from a default :class:`.sessionmaker` and pass an engine set for autocommit::

        plain_engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")

        autocommit_engine = plain_engine.execution_options(isolation_level="AUTOCOMMIT")

        # will normally use plain_engine
        Session = sessionmaker(plain_engine)

        # make a specific Session that will use the "autocommit" engine
        with Session(bind=autocommit_engine) as session:
            # work with session
            ...

    For the case where the :class:`.Session` or :class:`.sessionmaker` is configured with multiple "binds", we can either re-specify the ``binds`` argument fully, or if we want to only replace specific binds, we can use the :meth:`.Session.bind_mapper` or :meth:`.Session.bind_table` methods::

        with Session() as session:
            session.bind_mapper(User, autocommit_engine)

为单个事务设置隔离
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Setting Isolation for Individual Transactions

.. tab:: 中文

    关于隔离级别的一个关键注意事项是，不能安全地在已经启动事务的 :class:`_engine.Connection` 上修改隔离级别。  
    数据库不能更改正在进行的事务的隔离级别，并且某些 DBAPIs 和 SQLAlchemy 方言在这方面的行为不一致。

    因此，最好使用一个预先绑定到所需隔离级别的 :class:`_orm.Session`。  
    但是，可以通过在事务开始时使用 :meth:`_orm.Session.connection` 方法来在每个连接级别上影响隔离级别::

        from sqlalchemy.orm import Session

        # 假设会话刚刚构建
        sess = Session(bind=engine)

        # 在任何其他操作之前调用 connection() 并设置选项
        # 这将从绑定的引擎中获取一个新连接并开始一个真实的数据库事务。
        sess.connection(execution_options={"isolation_level": "SERIALIZABLE"})

        # ... 在 SERIALIZABLE 隔离级别下与会话一起工作...

        # 提交事务。连接将被释放
        # 并恢复到先前的隔离级别。
        sess.commit()

        # 在上面的 commit() 之后，可以根据需要开始新的事务，
        # 该事务将继续使用先前的默认隔离级别，除非再次设置。
        
    如上所示，我们首先通过构造函数或 :class:`.sessionmaker` 创建一个 :class:`.Session`。  
    然后，我们显式地通过调用 :meth:`.Session.connection` 设置数据库级别事务的开始，该方法提供的执行选项将在数据库级事务开始之前传递给连接。  
    该事务以选定的隔离级别继续进行。当事务完成后，连接的隔离级别将被重置为其默认值，然后返回到连接池。

    同样，也可以使用 :meth:`_orm.Session.begin` 方法开始 :class:`_orm.Session` 级别的事务；  
    在此调用之后调用 :meth:`_orm.Session.connection` 可以用于设置每个连接事务的隔离级别::

        sess = Session(bind=engine)

        with sess.begin():
            # 在任何其他操作之前调用 connection() 并设置选项
            # 这将从绑定的引擎中获取一个新连接并开始一个真实的数据库事务。
            sess.connection(execution_options={"isolation_level": "SERIALIZABLE"})

            # ... 在 SERIALIZABLE 隔离级别下与会话一起工作...

        # 在块外，事务已提交。连接被释放，并恢复到先前的隔离级别。

.. tab:: 英文

    A key caveat regarding isolation level is that the setting cannot be safely modified on a :class:`_engine.Connection` where a transaction has already started.  Databases cannot change the isolation level of a transaction in progress, and some DBAPIs and SQLAlchemy dialects have inconsistent behaviors in this area.

    Therefore it is preferable to use a :class:`_orm.Session` that is up front bound to an engine with the desired isolation level.  However, the isolation level on a per-connection basis can be affected by using the :meth:`_orm.Session.connection` method at the start of a transaction::

        from sqlalchemy.orm import Session

        # assume session just constructed
        sess = Session(bind=engine)

        # call connection() with options before any other operations proceed.
        # this will procure a new connection from the bound engine and begin a real
        # database transaction.
        sess.connection(execution_options={"isolation_level": "SERIALIZABLE"})

        # ... work with session in SERIALIZABLE isolation level...

        # commit transaction.  the connection is released
        # and reverted to its previous isolation level.
        sess.commit()

        # subsequent to commit() above, a new transaction may be begun if desired,
        # which will proceed with the previous default isolation level unless
        # it is set again.

    Above, we first produce a :class:`.Session` using either the constructor or a :class:`.sessionmaker`. Then we explicitly set up the start of a database-level transaction by calling upon :meth:`.Session.connection`, which provides for execution options that will be passed to the connection before the database-level transaction is begun.  The transaction proceeds with this selected isolation level.   When the transaction completes, the isolation level is reset on the connection to its default before the connection is returned to the connection pool.

    The :meth:`_orm.Session.begin` method may also be used to begin the :class:`_orm.Session` level transaction; calling upon :meth:`_orm.Session.connection` subsequent to that call may be used to set up the per-connection-transaction isolation level::

        sess = Session(bind=engine)

        with sess.begin():
            # call connection() with options before any other operations proceed.
            # this will procure a new connection from the bound engine and begin a
            # real database transaction.
            sess.connection(execution_options={"isolation_level": "SERIALIZABLE"})

            # ... work with session in SERIALIZABLE isolation level...

        # outside the block, the transaction has been committed.  the connection is
        # released and reverted to its previous isolation level.

使用事件跟踪事务状态
--------------------------------------

Tracking Transaction State with Events

.. tab:: 中文

    请参阅 :ref:`session_transaction_events` 一节，了解会话事务状态改变的可用事件挂钩的概述。

.. tab:: 英文

    See the section :ref:`session_transaction_events` for an overview of the available event hooks for session transaction state changes.

.. _session_external_transaction:

将会话加入外部事务（例如测试套件）
========================================================================

Joining a Session into an External Transaction (such as for test suites)

.. tab:: 中文

    如果正在使用的 :class:`_engine.Connection` 已经处于事务状态（即已经建立了 :class:`.Transaction`），  
    可以通过将 :class:`.Session` 绑定到该 :class:`_engine.Connection` 来让 :class:`.Session` 参与该事务。  
    这种做法通常适用于测试套件，允许 ORM 代码自由地使用 :class:`.Session`，包括能够调用 :meth:`.Session.commit`，  
    然后将整个数据库交互回滚。

    .. versionchanged:: 2.0 
        
        "加入外部事务" 的方法在 2.0 中得到了改进；不再需要事件处理程序来“重置”嵌套事务。

    该方法的工作原理是：首先在事务中建立一个 :class:`_engine.Connection`，并可选地创建一个 SAVEPOINT，然后将其传递给 :class:`_orm.Session` 作为“绑定”；  
    将 :paramref:`_orm.Session.join_transaction_mode` 参数设置为 ``"create_savepoint"``，这表示在 :class:`_orm.Session` 中应创建新的 SAVEPOINT，以便实现 BEGIN/COMMIT/ROLLBACK，  
    并确保外部事务保持原样。

    当测试结束时，外部事务将被回滚，因此测试期间的所有数据更改都会被恢复::

        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        from unittest import TestCase

        # 全局应用范围。创建 Session 类和引擎
        Session = sessionmaker()

        engine = create_engine("postgresql+psycopg2://...")


        class SomeTest(TestCase):
            def setUp(self):
                # 连接到数据库
                self.connection = engine.connect()

                # 开始一个非 ORM 事务
                self.trans = self.connection.begin()

                # 将个别 Session 绑定到连接，选择 "create_savepoint" join_transaction_mode
                self.session = Session(
                    bind=self.connection, join_transaction_mode="create_savepoint"
                )

            def test_something(self):
                # 在测试中使用会话。

                self.session.add(Foo())
                self.session.commit()

            def test_something_with_rollbacks(self):
                self.session.add(Bar())
                self.session.flush()
                self.session.rollback()

                self.session.add(Foo())
                self.session.commit()

            def tearDown(self):
                self.session.close()

                # 回滚 - 上面使用 Session 所做的所有操作（包括调用 commit()）将被回滚。
                self.trans.rollback()

                # 将连接返回给引擎
                self.connection.close()

    上述方法是 SQLAlchemy 自身 CI 的一部分，用于确保其按预期工作。


.. tab:: 英文

    If a :class:`_engine.Connection` is being used which is already in a transactional state (i.e. has a :class:`.Transaction` established), a :class:`.Session` can be made to participate within that transaction by just binding the :class:`.Session` to that :class:`_engine.Connection`. The usual rationale for this is a test suite that allows ORM code to work freely with a :class:`.Session`, including the ability to call :meth:`.Session.commit`, where afterwards the entire database interaction is rolled back.

    .. versionchanged:: 2.0 
        
        The "join into an external transaction" recipe is newly improved again in 2.0; event handlers to "reset" the nested transaction are no longer required.

    The recipe works by establishing a :class:`_engine.Connection` within a transaction and optionally a SAVEPOINT, then passing it to a :class:`_orm.Session` as the "bind"; the :paramref:`_orm.Session.join_transaction_mode` parameter is passed with the setting ``"create_savepoint"``, which indicates that new SAVEPOINTs should be created in order to implement BEGIN/COMMIT/ROLLBACK for the :class:`_orm.Session`, which will leave the external transaction in the same state in which it was passed.

    When the test tears down, the external transaction is rolled back so that any data changes throughout the test are reverted::

        from sqlalchemy.orm import sessionmaker
        from sqlalchemy import create_engine
        from unittest import TestCase

        # global application scope.  create Session class, engine
        Session = sessionmaker()

        engine = create_engine("postgresql+psycopg2://...")


        class SomeTest(TestCase):
            def setUp(self):
                # connect to the database
                self.connection = engine.connect()

                # begin a non-ORM transaction
                self.trans = self.connection.begin()

                # bind an individual Session to the connection, selecting
                # "create_savepoint" join_transaction_mode
                self.session = Session(
                    bind=self.connection, join_transaction_mode="create_savepoint"
                )

            def test_something(self):
                # use the session in tests.

                self.session.add(Foo())
                self.session.commit()

            def test_something_with_rollbacks(self):
                self.session.add(Bar())
                self.session.flush()
                self.session.rollback()

                self.session.add(Foo())
                self.session.commit()

            def tearDown(self):
                self.session.close()

                # rollback - everything that happened with the
                # Session above (including calls to commit())
                # is rolled back.
                self.trans.rollback()

                # return connection to the Engine
                self.connection.close()

    The above recipe is part of SQLAlchemy's own CI to ensure that it remains working as expected.

