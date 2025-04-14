会话 / 查询
==================

Sessions / Queries

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _faq_session_identity:

我正在使用 Session 重新加载数据，但它没有看到我在其他地方提交的更改
------------------------------------------------------------------------------------------

I'm re-loading data with my Session but it isn't seeing changes that I committed elsewhere

.. tab:: 中文

    关于这种行为的主要问题在于， `session` 的行为就好像事务处于 *serializable* 隔离级别，即使它实际上并不处于这个级别（而且通常并不是）。从实际的角度来看，这意味着在事务范围内，`session` 不会修改它已经读取的任何数据。

    如果你不熟悉“隔离级别”这个术语，你需要先阅读以下链接：

    `隔离级别 <https://en.wikipedia.org/wiki/Isolation_%28database_systems%29>`_

    简而言之， `serializable` 隔离级别通常意味着，一旦你在事务中执行 `SELECT` 操作并获取一系列行，下一次重新执行该 `SELECT` 时，你将获得 *相同的数据*。如果你处于下一个较低的隔离级别“可重复读取（repeatable read）”，你将会看到新添加的行（并且不再看到已删除的行），但对于你 *已经* 加载的行，你不会看到任何变化。只有当你处于更低的隔离级别，例如“已提交读取（read committed）”，才可能看到行数据的值发生变化。

    有关如何在使用 SQLAlchemy ORM 时控制隔离级别的信息，请参见 :ref:`session_transaction_isolation`。

    为了大大简化，:class:`.Session` 本身是以完全隔离的事务为基础的，并且不会覆盖它已经读取的任何映射属性，除非你显式地要求它这么做。尝试在一个正在进行的事务中重新读取你已经加载的数据是一种 *不常见* 的使用场景，在很多情况下没有任何影响，因此这被视为例外，而非常态；为了处理这一例外，提供了几种方法，可以在正在进行的事务上下文中重新加载特定数据。

    要理解我们所说的“事务”，当我们谈到 :class:`.Session` 时，你的 :class:`.Session` 只应该在事务中工作。相关概述请参见 :ref:`unitofwork_transaction`。

    一旦我们确定了隔离级别，并认为我们设置的隔离级别足够低，以便当我们重新 `SELECT` 一行时，我们应该在 :class:`.Session` 中看到新数据，如何查看这些数据呢？

    有三种方式，按常见程度排序：

    1. 我们简单地结束当前事务，并在下一次访问时通过调用 :meth:`.Session.commit` 开始一个新事务（注意，如果 :class:`.Session` 处于较少使用的“自动提交（autocommit）”模式下，还需要调用 :meth:`.Session.begin`）。绝大多数应用程序和用例没有遇到无法“看到”其他事务数据的问题，因为它们遵循这个模式，这是 **短生命周期事务** 最佳实践的核心。参见 :ref:`session_faq_whentocreate`，了解更多关于此的思考。

    2. 我们告诉 :class:`.Session` 重新读取它已经读取的行，无论是通过下一次查询时使用 :meth:`.Session.expire_all` 或 :meth:`.Session.expire`，还是立即对某个对象使用 :class:`.Session.refresh`。有关此的详细信息，请参见 :ref:`session_expire`。

    3. 我们可以执行整个查询，并设置它们在读取行时一定要覆盖已经加载的对象，使用“populate existing”。这是在 :ref:`orm_queryguide_populate_existing` 中描述的一种执行选项。

    但请记住， **如果我们的隔离级别是可重复读取或更高，则 ORM 无法看到行中的更改，除非我们开始一个新事务**。

.. tab:: 英文

    The main issue regarding this behavior is that the session acts as though
    the transaction is in the *serializable* isolation state, even if it's not
    (and it usually is not).   In practical terms, this means that the session
    does not alter any data that it's already read within the scope of a transaction.
    
    If the term "isolation level" is unfamiliar, then you first need to read this link:
    
    `Isolation Level <https://en.wikipedia.org/wiki/Isolation_%28database_systems%29>`_
    
    In short, serializable isolation level generally means
    that once you SELECT a series of rows in a transaction, you will get
    *the identical data* back each time you re-emit that SELECT.   If you are in
    the next-lower isolation level, "repeatable read", you'll
    see newly added rows (and no longer see deleted rows), but for rows that
    you've *already* loaded, you won't see any change.   Only if you are in a
    lower isolation level, e.g. "read committed", does it become possible to
    see a row of data change its value.
    
    For information on controlling the isolation level when using the
    SQLAlchemy ORM, see :ref:`session_transaction_isolation`.
    
    To simplify things dramatically, the :class:`.Session` itself works in
    terms of a completely isolated transaction, and doesn't overwrite any mapped attributes
    it's already read unless you tell it to.  The use case of trying to re-read
    data you've already loaded in an ongoing transaction is an *uncommon* use
    case that in many cases has no effect, so this is considered to be the
    exception, not the norm; to work within this exception, several methods
    are provided to allow specific data to be reloaded within the context
    of an ongoing transaction.
    
    To understand what we mean by "the transaction" when we talk about the
    :class:`.Session`, your :class:`.Session` is intended to only work within
    a transaction.  An overview of this is at :ref:`unitofwork_transaction`.
    
    Once we've figured out what our isolation level is, and we think that
    our isolation level is set at a low enough level so that if we re-SELECT a row,
    we should see new data in our :class:`.Session`, how do we see it?
    
    Three ways, from most common to least:
    
    1. We simply end our transaction and start a new one on next access
       with our :class:`.Session` by calling :meth:`.Session.commit` (note
       that if the :class:`.Session` is in the lesser-used "autocommit"
       mode, there would be a call to :meth:`.Session.begin` as well). The
       vast majority of applications and use cases do not have any issues
       with not being able to "see" data in other transactions because
       they stick to this pattern, which is at the core of the best practice of
       **short lived transactions**.
       See :ref:`session_faq_whentocreate` for some thoughts on this.
    
    2. We tell our :class:`.Session` to re-read rows that it has already read,
       either when we next query for them using :meth:`.Session.expire_all`
       or :meth:`.Session.expire`, or immediately on an object using
       :class:`.Session.refresh`.  See :ref:`session_expire` for detail on this.
    
    3. We can run whole queries while setting them to definitely overwrite
       already-loaded objects as they read rows by using "populate existing".
       This is an execution option described at
       :ref:`orm_queryguide_populate_existing`.
    
    But remember, **the ORM cannot see changes in rows if our isolation
    level is repeatable read or higher, unless we start a new transaction**.

.. _faq_session_rollback:

“由于刷新期间出现先前的异常，此 Session 的事务已被回滚。”（或类似）
---------------------------------------------------------------------------------------------------------

"This Session's transaction has been rolled back due to a previous exception during flush." (or similar)

.. tab:: 中文
    
    当 :meth:`.Session.flush` 引发异常并回滚事务时，如果进一步调用 :class:`.Session` 上的命令而没有显式调用 :meth:`.Session.rollback` 或 :meth:`.Session.close`，则会发生此错误。
    
    通常，这与一个应用程序在 :meth:`.Session.flush` 或 :meth:`.Session.commit` 时捕获异常并没有正确处理异常有关。例如::
    
        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.declarative import declarative_base
    
        Base = declarative_base(create_engine("sqlite://"))
    
    
        class Foo(Base):
            __tablename__ = "foo"
            id = Column(Integer, primary_key=True)
    
    
        Base.metadata.create_all()
    
        session = sessionmaker()()
    
        # 违反约束
        session.add_all([Foo(id=1), Foo(id=1)])
    
        try:
            session.commit()
        except:
            # 忽略错误
            pass
    
        # 在没有回滚的情况下继续使用 session
        session.commit()
    
    :class:`.Session` 的使用应该符合类似于以下结构的方式::
    
        try:
            # <使用 session>
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()  # 可选，取决于用例
    
    除了 flush 操作，许多其他情况也可能导致 try/except 失败。应用程序应确保在 ORM 相关的流程中应用某种“框架”机制，以确保连接和事务资源有明确的边界，并且在出现任何失败条件时，事务能够显式回滚。
    
    这并不意味着应用程序中应当有 try/except 块，这种做法并不是一个可扩展的架构。相反，典型的做法是在首次调用 ORM 相关方法和函数时，调用这些函数的过程会处于一个块中，该块在一系列操作成功完成后提交事务，并在操作失败（包括 flush 失败）时回滚事务。也有通过函数装饰器或上下文管理器实现类似结果的做法。采取何种方法在很大程度上取决于所编写应用程序的类型。
    
    有关如何组织使用 :class:`.Session` 的详细讨论，请参见 :ref:`session_faq_whentocreate`。

.. tab:: 英文

    This is an error that occurs when a :meth:`.Session.flush` raises an exception, rolls back
    the transaction, but further commands upon the :class:`.Session` are called without an
    explicit call to :meth:`.Session.rollback` or :meth:`.Session.close`.

    It usually corresponds to an application that catches an exception
    upon :meth:`.Session.flush` or :meth:`.Session.commit` and
    does not properly handle the exception.    For example::

        from sqlalchemy import create_engine, Column, Integer
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base(create_engine("sqlite://"))


        class Foo(Base):
            __tablename__ = "foo"
            id = Column(Integer, primary_key=True)


        Base.metadata.create_all()

        session = sessionmaker()()

        # constraint violation
        session.add_all([Foo(id=1), Foo(id=1)])

        try:
            session.commit()
        except:
            # ignore error
            pass

        # continue using session without rolling back
        session.commit()

    The usage of the :class:`.Session` should fit within a structure similar to this::

        try:
            # <use session>
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()  # optional, depends on use case

    Many things can cause a failure within the try/except besides flushes.
    Applications should ensure some system of "framing" is applied to ORM-oriented
    processes so that connection and transaction resources have a definitive
    boundary, and so that transactions can be explicitly rolled back if any
    failure conditions occur.

    This does not mean there should be try/except blocks throughout an application,
    which would not be a scalable architecture.  Instead, a typical approach is
    that when ORM-oriented methods and functions are first called, the process
    that's calling the functions from the very top would be within a block that
    commits transactions at the successful completion of a series of operations,
    as well as rolls transactions back if operations fail for any reason,
    including failed flushes.  There are also approaches using function decorators or
    context managers to achieve similar results.   The kind of approach taken
    depends very much on the kind of application being written.

    For a detailed discussion on how to organize usage of the :class:`.Session`,
    please see :ref:`session_faq_whentocreate`.

但为什么 flush() 坚持发出 ROLLBACK？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

But why does flush() insist on issuing a ROLLBACK?

.. tab:: 中文

    如果 :meth:`.Session.flush` 能够部分完成并且不中止回滚，那当然是极好的；然而，它目前尚不具备这样的能力，因为其内部的状态管理机制必须被修改，以便能在任意时刻中断，并确保与已写入数据库的内容完全一致。虽然在理论上这是可能实现的，但此增强功能的实用价值大打折扣，因为许多数据库操作在失败后都强制要求执行 ROLLBACK。特别是 PostgreSQL，一旦某些操作失败，该事务就不能继续执行：

    .. sourcecode:: text

        test=> create table foo(id integer primary key);
        NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "foo_pkey" for table "foo"
        CREATE TABLE
        test=> begin;
        BEGIN
        test=> insert into foo values(1);
        INSERT 0 1
        test=> commit;
        COMMIT
        test=> begin;
        BEGIN
        test=> insert into foo values(1);
        ERROR:  duplicate key value violates unique constraint "foo_pkey"
        test=> insert into foo values(2);
        ERROR:  current transaction is aborted, commands ignored until end of transaction block

    SQLAlchemy 提供的解决方案是通过 :meth:`.Session.begin_nested` 支持 SAVEPOINT。使用 :meth:`.Session.begin_nested`，可以在一个可能失败的操作外部创建一个“嵌套事务”，在操作失败时“回滚”至失败前的状态，同时保留外围事务。

.. tab:: 英文

    It would be great if :meth:`.Session.flush` could partially complete and then
    not roll back, however this is beyond its current capabilities since its
    internal bookkeeping would have to be modified such that it can be halted at
    any time and be exactly consistent with what's been flushed to the database.
    While this is theoretically possible, the usefulness of the enhancement is
    greatly decreased by the fact that many database operations require a ROLLBACK
    in any case. Postgres in particular has operations which, once failed, the
    transaction is not allowed to continue:

    .. sourcecode:: text

        test=> create table foo(id integer primary key);
        NOTICE:  CREATE TABLE / PRIMARY KEY will create implicit index "foo_pkey" for table "foo"
        CREATE TABLE
        test=> begin;
        BEGIN
        test=> insert into foo values(1);
        INSERT 0 1
        test=> commit;
        COMMIT
        test=> begin;
        BEGIN
        test=> insert into foo values(1);
        ERROR:  duplicate key value violates unique constraint "foo_pkey"
        test=> insert into foo values(2);
        ERROR:  current transaction is aborted, commands ignored until end of transaction block

    What SQLAlchemy offers that solves both issues is support of SAVEPOINT, via
    :meth:`.Session.begin_nested`. Using :meth:`.Session.begin_nested`, you can frame an operation that may
    potentially fail within a transaction, and then "roll back" to the point
    before its failure while maintaining the enclosing transaction.

但为什么一次自动调用 ROLLBACK 还不够？为什么我必须再次 ROLLBACK？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

But why isn't the one automatic call to ROLLBACK enough?  Why must I ROLLBACK again?

.. tab:: 中文

    由 ``flush()`` 引发的回滚并不意味着整个事务块的结束；虽然它终结了当前数据库事务，但从 :class:`.Session` 的角度来看，事务仍处于“非活动状态”。

    举例说明如下::

        sess = Session()  # 启动一个逻辑事务
        try:
            sess.flush()

            sess.commit()
        except:
            sess.rollback()

    如上所示，当第一次创建 :class:`.Session` 时（假设未启用“自动提交模式”），会在 :class:`.Session` 内部建立一个逻辑事务。该事务是“逻辑”上的，即在执行 SQL 语句之前不会真正占用数据库资源，此时才会启动连接级别和 DBAPI 级别的事务。然而，无论是否存在数据库级事务，该逻辑事务始终存在，直到通过 :meth:`.Session.commit` 、 :meth:`.Session.rollback` 或 :meth:`.Session.close` 明确终止。

    如果上面的 ``flush()`` 失败，代码仍处于 try/commit/except/rollback 包裹的事务范围内。如果 ``flush()`` 完全回滚逻辑事务，那么等到执行 ``except:`` 块时，:class:`.Session` 将处于一个“干净”的状态，已准备好开启一个全新的事务，此时执行 :meth:`.Session.rollback` 就显得时序错误。尤其是，此时 :class:`.Session` 会已经开始一个新的事务，而 :meth:`.Session.rollback` 会错误地作用在这个新的事务上。为了防止在应当执行回滚的时刻错误地开启新事务，:class:`.Session` 会阻止后续操作，直到显式回滚发生。

    换句话说，调用代码必须 **始终** 使用 :meth:`.Session.commit` 、 :meth:`.Session.rollback` 或 :meth:`.Session.close` 来与当前事务块对应。 ``flush()`` 会使 :class:`.Session` 保持在该事务块中，从而保证上述代码行为的一致性和可预测性。

.. tab:: 英文

    The rollback that's caused by the flush() is not the end of the complete transaction
    block; while it ends the database transaction in play, from the :class:`.Session`
    point of view there is still a transaction that is now in an inactive state.

    Given a block such as::

        sess = Session()  # begins a logical transaction
        try:
            sess.flush()

            sess.commit()
        except:
            sess.rollback()

    Above, when a :class:`.Session` is first created, assuming "autocommit mode"
    isn't used, a logical transaction is established within the :class:`.Session`.
    This transaction is "logical" in that it does not actually use any  database
    resources until a SQL statement is invoked, at which point a connection-level
    and DBAPI-level transaction is started.   However, whether or not
    database-level transactions are part of its state, the logical transaction will
    stay in place until it is ended using :meth:`.Session.commit`,
    :meth:`.Session.rollback`, or :meth:`.Session.close`.

    When the ``flush()`` above fails, the code is still within the transaction
    framed by the try/commit/except/rollback block.   If ``flush()`` were to fully
    roll back the logical transaction, it would mean that when we then reach the
    ``except:`` block the :class:`.Session` would be in a clean state, ready to
    emit new SQL on an all new transaction, and the call to
    :meth:`.Session.rollback` would be out of sequence.  In particular, the
    :class:`.Session` would have begun a new transaction by this point, which the
    :meth:`.Session.rollback` would be acting upon erroneously.  Rather than
    allowing SQL operations to proceed on a new transaction in this place where
    normal usage dictates a rollback is about to take place, the :class:`.Session`
    instead refuses to continue until the explicit rollback actually occurs.

    In other words, it is expected that the calling code will **always** call
    :meth:`.Session.commit`, :meth:`.Session.rollback`, or :meth:`.Session.close`
    to correspond to the current transaction block.  ``flush()`` keeps the
    :class:`.Session` within this transaction block so that the behavior of the
    above code is predictable and consistent.


如何制作始终向每个查询添加特定过滤器的查询？
------------------------------------------------------------------------------------------------

How do I make a Query that always adds a certain filter to every query?

.. tab:: 中文

    请参阅 `FilteredQuery <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/FilteredQuery>`_ 中的配方。

.. tab:: 英文

    See the recipe at `FilteredQuery <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/FilteredQuery>`_.

.. _faq_query_deduplicating:

我的查询没有返回与 query.count() 告诉我的相同数量的对象 - 为什么？
-------------------------------------------------------------------------------------

My Query does not return the same number of objects as query.count() tells me - why?

.. tab:: 中文

    当 :class:`_query.Query` 对象被用来返回 ORM 映射对象的列表时，它会 **基于主键去重对象**。例如，假设我们使用 :ref:`tutorial_orm_table_metadata` 中描述的 ``User`` 映射，执行如下 SQL 查询::

        q = session.query(User).outerjoin(User.addresses).filter(User.name == "jack")

    在上例中，教程中的样例数据在 ``addresses`` 表中有两行对应于 ``users`` 表中名为 ``'jack'`` 的一行数据，其主键为 5。如果我们使用 :meth:`_query.Query.count` 查询数量，将会得到 **2**::

        >>> q.count()
        2

    但如果我们执行 :meth:`_query.Query.all` 或遍历该查询，将只会得到 **一个元素**::

    >>> q.all()
    [User(id=5, name='jack', ...)]

    这是因为 :class:`_query.Query` 返回实体对象时会进行 **去重**。如果我们只请求部分字段，则不会去重::

    >>> session.query(User.id, User.name).outerjoin(User.addresses).filter(
    ...     User.name == "jack"
    ... ).all()
    [(5, 'jack'), (5, 'jack')]

    :class:`_query.Query` 之所以会去重，主要有两个原因：

    * **支持联接预加载（joined eager loading）** — 参见 :ref:`joined_eager_loading`，此功能通过连接相关表的方式加载对象集合，而这些连接查询中的主对象主键是重复的。例如，对于 ``User(id=5)``，多个子项会导致多行重复的主键值。为了正确地将这些行映射为 ``User.addresses`` 集合，必须对主对象进行去重。无论是否启用了 ``joinedload`` 或者设置了 ``lazy='joined'``，出于一致性考虑，都进行去重。预加载的关键理念是加载选项不应影响返回结果的语义。

    * **避免与身份映射（identity map）混淆** — 虽不是最关键的原因，但依然重要。由于 :class:`.Session` 使用 :term:`identity map`，即使结果集中有多条主键为 5 的记录，:class:`.Session` 中只会存在一个唯一的 ``User(id=5)`` 对象。若在结果列表中多次返回同一个对象，从概念上并不合理。事实上，如果结果是一个“有序集合”可能更能代表 :class:`_query.Query` 的意图。

    不过，:class:`_query.Query` 的去重行为仍存在一些争议，主要是因为 :meth:`_query.Query.count` 的行为与实际返回不一致。近年来，联接预加载已逐步被“子查询预加载（subquery eager loading）”策略和“select IN 预加载”策略所取代，这些策略通常更适用于集合加载。随着这些替代策略的发展，SQLAlchemy 未来可能会改变 :class:`_query.Query` 的去重行为，也可能会引入新的 API，以更明确地控制去重，并改进联接预加载的行为，使其具有更一致的使用方式。

.. tab:: 英文

    The :class:`_query.Query` object, when asked to return a list of ORM-mapped objects,
    will **deduplicate the objects based on primary key**.   That is, if we
    for example use the ``User`` mapping described at :ref:`tutorial_orm_table_metadata`,
    and we had a SQL query like the following::
    
        q = session.query(User).outerjoin(User.addresses).filter(User.name == "jack")
    
    Above, the sample data used in the tutorial has two rows in the ``addresses``
    table for the ``users`` row with the name ``'jack'``, primary key value 5.
    If we ask the above query for a :meth:`_query.Query.count`, we will get the answer
    **2**::
    
        >>> q.count()
        2
    
    However, if we run :meth:`_query.Query.all` or iterate over the query, we get back
    **one element**::
    
      >>> q.all()
      [User(id=5, name='jack', ...)]
    
    This is because when the :class:`_query.Query` object returns full entities, they
    are **deduplicated**.    This does not occur if we instead request individual
    columns back::
    
      >>> session.query(User.id, User.name).outerjoin(User.addresses).filter(
      ...     User.name == "jack"
      ... ).all()
      [(5, 'jack'), (5, 'jack')]
    
    There are two main reasons the :class:`_query.Query` will deduplicate:
    
    * **To allow joined eager loading to work correctly** - :ref:`joined_eager_loading`
      works by querying rows using joins against related tables, where it then routes
      rows from those joins into collections upon the lead objects.   In order to do this,
      it has to fetch rows where the lead object primary key is repeated for each
      sub-entry.   This pattern can then continue into further sub-collections such
      that a multiple of rows may be processed for a single lead object, such as
      ``User(id=5)``.   The dedpulication allows us to receive objects in the way they
      were queried, e.g. all the ``User()`` objects whose name is ``'jack'`` which
      for us is one object, with
      the ``User.addresses`` collection eagerly loaded as was indicated either
      by ``lazy='joined'`` on the :func:`_orm.relationship` or via the :func:`_orm.joinedload`
      option.    For consistency, the deduplication is still applied whether or not
      the joinedload is established, as the key philosophy behind eager loading
      is that these options never affect the result.
    
    * **To eliminate confusion regarding the identity map** - this is admittedly
      the less critical reason.  As the :class:`.Session`
      makes use of an :term:`identity map`, even though our SQL result set has two
      rows with primary key 5, there is only one ``User(id=5)`` object inside the :class:`.Session`
      which must be maintained uniquely on its identity, that is, its primary key /
      class combination.   It doesn't actually make much sense, if one is querying for
      ``User()`` objects, to get the same object multiple times in the list.   An
      ordered set would potentially be a better representation of what :class:`_query.Query`
      seeks to return when it returns full objects.
    
    The issue of :class:`_query.Query` deduplication remains problematic, mostly for the
    single reason that the :meth:`_query.Query.count` method is inconsistent, and the
    current status is that joined eager loading has in recent releases been
    superseded first by the "subquery eager loading" strategy and more recently the
    "select IN eager loading" strategy, both of which are generally more
    appropriate for collection eager loading. As this evolution continues,
    SQLAlchemy may alter this behavior on :class:`_query.Query`, which may also involve
    new APIs in order to more directly control this behavior, and may also alter
    the behavior of joined eager loading in order to create a more consistent usage
    pattern.


我已经针对 Outer Join 创建了映射，虽然查询返回行，但没有返回任何对象。为什么不？
------------------------------------------------------------------------------------------------------------------

I've created a mapping against an Outer Join, and while the query returns rows, no objects are returned.  Why not?

.. tab:: 中文

    外连接返回的行中可能包含主键的一部分为 NULL 的情况，因为主键是由两个表的字段组成的复合键。当某行缺乏可接受的主键时，:class:`_query.Query` 对象会忽略这行。是否接受某主键，取决于 :class:`_orm.Mapper` 上的 ``allow_partial_pks`` 标志设置；当此标志启用时，只要主键中至少有一个非 NULL 值，该主键就被接受；否则，则要求所有主键字段均不为 NULL。参见 :class:`_orm.Mapper` 中的 ``allow_partial_pks``。

.. tab:: 英文

    Rows returned by an outer join may contain NULL for part of the primary key,
    as the primary key is the composite of both tables.  The :class:`_query.Query` object ignores incoming rows
    that don't have an acceptable primary key.   Based on the setting of the ``allow_partial_pks``
    flag on :class:`_orm.Mapper`, a primary key is accepted if the value has at least one non-NULL
    value, or alternatively if the value has no NULL values.  See ``allow_partial_pks``
    at :class:`_orm.Mapper`.


我正在使用 ``joinedload()`` 或 ``lazy=False`` 来创建 JOIN/OUTER JOIN，而当我尝试添加 WHERE、ORDER BY、LIMIT 等（依赖于（OUTER）JOIN）时，SQLAlchemy 没有构建正确的查询
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

I'm using ``joinedload()`` or ``lazy=False`` to create a JOIN/OUTER JOIN and SQLAlchemy is not constructing the correct query when I try to add a WHERE, ORDER BY, LIMIT, etc. (which relies upon the (OUTER) JOIN)

.. tab:: 中文

    由联接预加载（joined eager loading）生成的连接语句仅用于完整加载相关集合，它们的设计目的是不影响查询的主要结果。这些连接使用匿名别名，无法被直接引用。

    有关此行为的详细信息，请参阅 :ref:`zen_of_eager_loading`。

.. tab:: 英文

    The joins generated by joined eager loading are only used to fully load related
    collections, and are designed to have no impact on the primary results of the query.
    Since they are anonymously aliased, they cannot be referenced directly.

    For detail on this behavior, see :ref:`zen_of_eager_loading`.

查询没有 ``__len__()``，为什么没有？
------------------------------------

Query has no ``__len__()``, why not?

.. tab:: 中文

    Python 的 ``__len__()`` 魔术方法允许使用内置函数 ``len()`` 来获取集合长度。直观来看，我们可能期望 SQL 查询对象将 ``__len__()`` 关联至 :meth:`_query.Query.count` 方法，从而执行一个 `SELECT COUNT` 查询。但这在 SQLAlchemy 中并不可行，其原因是将查询转换为列表会导致执行两次 SQL 查询，而不是一次，如下所示::

        class Iterates:
            def __len__(self):
                print("LEN!")
                return 5

            def __iter__(self):
                print("ITER!")
                return iter([1, 2, 3, 4, 5])


        list(Iterates())

    输出：

    .. sourcecode:: text

        ITER!
        LEN!

.. tab:: 英文

    The Python ``__len__()`` magic method applied to an object allows the ``len()``
    builtin to be used to determine the length of the collection. It's intuitive
    that a SQL query object would link ``__len__()`` to the :meth:`_query.Query.count`
    method, which emits a `SELECT COUNT`. The reason this is not possible is
    because evaluating the query as a list would incur two SQL calls instead of
    one::

        class Iterates:
            def __len__(self):
                print("LEN!")
                return 5

            def __iter__(self):
                print("ITER!")
                return iter([1, 2, 3, 4, 5])


        list(Iterates())

    output:

    .. sourcecode:: text

        ITER!
        LEN!

如何在 ORM 查询中使用文本 SQL？
------------------------------------------

How Do I use Textual SQL with ORM Queries?

.. tab:: 中文

    见:

    * :ref:`orm_queryguide_selecting_text` - 使用 :class:`_query.Query` 的临时文本块

    * :ref:`session_sql_expressions` - 直接将 :class:`.Session` 与文本 SQL 一起使用。

.. tab:: 英文

    See:

    * :ref:`orm_queryguide_selecting_text` - Ad-hoc textual blocks with :class:`_query.Query`

    * :ref:`session_sql_expressions` - Using :class:`.Session` with textual SQL directly.

我正在调用 ``Session.delete(myobject)``，但它没有从父集合中删除！
------------------------------------------------------------------------------------------

I'm calling ``Session.delete(myobject)`` and it isn't removed from the parent collection!

.. tab:: 中文

    有关此行为的描述，请参阅 :ref:`session_deleting_from_collections`。

.. tab:: 英文

    See :ref:`session_deleting_from_collections` for a description of this behavior.

为什么加载对象时没有调用我的 ``__init__()``？
-------------------------------------------------------

why isn't my ``__init__()`` called when I load objects?

.. tab:: 中文

    有关此行为的描述，请参阅 :ref:`mapped_class_load_events`。

.. tab:: 英文

    See :ref:`mapped_class_load_events` for a description of this behavior.

如何将 ON DELETE CASCADE 与 SA 的 ORM 结合使用？
---------------------------------------------

how do I use ON DELETE CASCADE with SA's ORM?

.. tab:: 中文

    SQLAlchemy 始终会对当前已加载到 :class:`.Session` 中的依赖行执行 UPDATE 或 DELETE 语句。而对于尚未加载的行，默认行为是先执行 SELECT 查询以加载这些行，然后再执行更新或删除操作；换言之，SQLAlchemy 假设未配置 ON DELETE CASCADE。

    如需使 SQLAlchemy 与 ON DELETE CASCADE 配合使用，请参见 :ref:`passive_deletes`。

.. tab:: 英文

    SQLAlchemy will always issue UPDATE or DELETE statements for dependent
    rows which are currently loaded in the :class:`.Session`.  For rows which
    are not loaded, it will by default issue SELECT statements to load
    those rows and update/delete those as well; in other words it assumes
    there is no ON DELETE CASCADE configured.
    To configure SQLAlchemy to cooperate with ON DELETE CASCADE, see
    :ref:`passive_deletes`.

我将实例上的“foo_id”属性设置为“7”，但“foo”属性仍为“None” - 它不应该加载 ID 为 #7 的 Foo 吗？
----------------------------------------------------------------------------------------------------------------------------------------------------

I set the "foo_id" attribute on my instance to "7", but the "foo" attribute is still ``None`` - shouldn't it have loaded Foo with id #7?

.. tab:: 中文

    ORM 的设计并不支持在外键属性发生变化时立即填充关系属性——相反，它是以另一种方式工作的：外键属性由 ORM 在内部处理，最终用户以自然的方式设置对象之间的关系。因此，推荐的设置 ``o.foo`` 的方式就是直接设置它！::

        foo = session.get(Foo, 7)
        o.foo = foo
        Session.commit()

    当然，直接操作外键属性在语法上是完全合法的。然而，目前将外键属性设置为一个新值不会触发其关联的 :func:`_orm.relationship` 的 "expire"（过期）事件。这意味着以下代码序列::

        o = session.scalars(select(SomeClass).limit(1)).first()

        # 假设现有的 o.foo_id 值是 None；
        # 访问 o.foo 会将其解释为 ``None``，但这实际上是一次
        # “加载”操作，加载的是 None 值
        assert o.foo is None

        # 现在设置 foo_id 为某个值，但 o.foo 不会立即反映这一变化
        o.foo_id = 7

    在首次访问时，``o.foo`` 会加载其对应数据库中的有效值（此处为 ``None``）。之后即使设置了 ``o.foo_id = 7``，该值也只是一个挂起（pending）的更改，尚未被 flush，因此 ``o.foo`` 仍然是 ``None``::

        # 属性已被加载为 None，尚未与 o.foo_id = 7 对应起来
        assert o.foo is None

    通常，在提交之后会自然地重新加载 ``o.foo``，此时新的外键值被 flush 且所有状态已过期::

        session.commit()  # 使所有属性过期

        foo_7 = session.get(Foo, 7)

        # o.foo 会再次触发 lazyload，此时会获取到新的对象
        assert o.foo is foo_7

    一种更小范围的操作是单独使该属性过期——这可通过 :meth:`.Session.expire` 对任何 :term:`persistent` 对象执行::

        o = session.scalars(select(SomeClass).limit(1)).first()
        o.foo_id = 7
        Session.expire(o, ["foo"])  # 对象必须是 persistent 状态

        foo_7 = session.get(Foo, 7)

        assert o.foo is foo_7  # 访问时 o.foo 会 lazyload

    请注意，如果对象尚未持久化（persistent）但已存在于 :class:`.Session` 中，它就被称为 :term:`pending`。这表示该对象尚未被 INSERT 到数据库中。对于这类对象，设置 ``foo_id`` 在行尚未插入前没有实际意义，因为还不存在对应的行::

        new_obj = SomeClass()
        new_obj.foo_id = 7

        Session.add(new_obj)

        # 返回 None，但这不是一次 "lazyload"，
        # 因为对象尚未在数据库中持久化，None 值也不属于对象状态的一部分
        assert new_obj.foo is None

        Session.flush()  # 触发 INSERT

        assert new_obj.foo is foo_7  # 现在可以加载了

    .. topic:: 非持久化对象的属性加载

        上述 "pending" 行为的一个变体是，在 :func:`_orm.relationship` 上使用 ``load_on_pending`` 标志。
        设置此标志后，lazy loader 会在 INSERT 执行前为 ``new_obj.foo`` 发起加载；
        另一种变体是使用 :meth:`.Session.enable_relationship_loading` 方法，
        它可以以一种特殊方式将对象“附加”到 :class:`.Session`，
        使得 many-to-one 关系能根据外键属性加载，
        无论对象当前处于何种状态。
        这两种技术 **不推荐在一般情况下使用**；
        它们是为满足某些特殊编程场景而添加的，
        这些场景会重新利用 ORM 的对象状态机制。

    配方 `ExpireRelationshipOnFKChange <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/ExpireRelationshipOnFKChange>`_ 展示了一个使用 SQLAlchemy 事件的示例，
    用于协调设置外键属性与 many-to-one 关系之间的同步。

.. tab:: 英文

    The ORM is not constructed in such a way as to support
    immediate population of relationships driven from foreign
    key attribute changes - instead, it is designed to work the
    other way around - foreign key attributes are handled by the
    ORM behind the scenes, the end user sets up object
    relationships naturally. Therefore, the recommended way to
    set ``o.foo`` is to do just that - set it!::

        foo = session.get(Foo, 7)
        o.foo = foo
        Session.commit()

    Manipulation of foreign key attributes is of course entirely legal.  However,
    setting a foreign-key attribute to a new value currently does not trigger
    an "expire" event of the :func:`_orm.relationship` in which it's involved.  This means
    that for the following sequence::

        o = session.scalars(select(SomeClass).limit(1)).first()

        # assume the existing o.foo_id value is None;
        # accessing o.foo will reconcile this as ``None``, but will effectively
        # "load" the value of None
        assert o.foo is None

        # now set foo_id to something.  o.foo will not be immediately affected
        o.foo_id = 7

    ``o.foo`` is loaded with its effective database value of ``None`` when it
    is first accessed.  Setting
    ``o.foo_id = 7`` will have the value of "7" as a pending change, but no flush
    has occurred - so ``o.foo`` is still ``None``::

        # attribute is already "loaded" as None, has not been
        # reconciled with o.foo_id = 7 yet
        assert o.foo is None

    For ``o.foo`` to load based on the foreign key mutation is usually achieved
    naturally after the commit, which both flushes the new foreign key value
    and expires all state::

        session.commit()  # expires all attributes

        foo_7 = session.get(Foo, 7)

        # o.foo will lazyload again, this time getting the new object
        assert o.foo is foo_7

    A more minimal operation is to expire the attribute individually - this can
    be performed for any :term:`persistent` object using :meth:`.Session.expire`::

        o = session.scalars(select(SomeClass).limit(1)).first()
        o.foo_id = 7
        Session.expire(o, ["foo"])  # object must be persistent for this

        foo_7 = session.get(Foo, 7)

        assert o.foo is foo_7  # o.foo lazyloads on access

    Note that if the object is not persistent but present in the :class:`.Session`,
    it's known as :term:`pending`.   This means the row for the object has not been
    INSERTed into the database yet.  For such an object, setting ``foo_id`` does not
    have meaning until the row is inserted; otherwise there is no row yet::

        new_obj = SomeClass()
        new_obj.foo_id = 7

        Session.add(new_obj)

        # returns None but this is not a "lazyload", as the object is not
        # persistent in the DB yet, and the None value is not part of the
        # object's state
        assert new_obj.foo is None

        Session.flush()  # emits INSERT

        assert new_obj.foo is foo_7  # now it loads

    .. topic:: Attribute loading for non-persistent objects

        One variant on the "pending" behavior above is if we use the flag
        ``load_on_pending`` on :func:`_orm.relationship`.   When this flag is set, the
        lazy loader will emit for ``new_obj.foo`` before the INSERT proceeds; another
        variant of this is to use the :meth:`.Session.enable_relationship_loading`
        method, which can "attach" an object to a :class:`.Session` in such a way that
        many-to-one relationships load as according to foreign key attributes
        regardless of the object being in any particular state.
        Both techniques are **not recommended for general use**; they were added to suit
        specific programming scenarios encountered by users which involve the repurposing
        of the ORM's usual object states.

    The recipe `ExpireRelationshipOnFKChange <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/ExpireRelationshipOnFKChange>`_ features an example using SQLAlchemy events
    in order to coordinate the setting of foreign key attributes with many-to-one
    relationships.

.. _faq_walk_objects:

如何遍历与给定对象相关的所有对象？
-------------------------------------------------------------

How do I walk all objects that are related to a given object?

.. tab:: 中文

    一个对象如果与其他对象有关联，那么它就会涉及到 mappers 之间设置的 :func:`_orm.relationship` 构造。
    下面这段代码将遍历所有相关对象，并修正循环引用::

        from sqlalchemy import inspect


        def walk(obj):
            deque = [obj]

            seen = set()

            while deque:
                obj = deque.pop(0)
                if obj in seen:
                    continue
                else:
                    seen.add(obj)
                    yield obj
                insp = inspect(obj)
                for relationship in insp.mapper.relationships:
                    related = getattr(obj, relationship.key)
                    if relationship.uselist:
                        deque.extend(related)
                    elif related is not None:
                        deque.append(related)

    可以如下演示该函数::

        Base = declarative_base()


        class A(Base):
            __tablename__ = "a"
            id = Column(Integer, primary_key=True)
            bs = relationship("B", backref="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))
            c_id = Column(ForeignKey("c.id"))
            c = relationship("C", backref="bs")


        class C(Base):
            __tablename__ = "c"
            id = Column(Integer, primary_key=True)


        a1 = A(bs=[B(), B(c=C())])


        for obj in walk(a1):
            print(obj)

    输出：

    .. sourcecode:: text

        <__main__.A object at 0x10303b190>
        <__main__.B object at 0x103025210>
        <__main__.B object at 0x10303b0d0>
        <__main__.C object at 0x103025490>

.. tab:: 英文

    An object that has other objects related to it will correspond to the
    :func:`_orm.relationship` constructs set up between mappers.  This code fragment will
    iterate all the objects, correcting for cycles as well::

        from sqlalchemy import inspect


        def walk(obj):
            deque = [obj]

            seen = set()

            while deque:
                obj = deque.pop(0)
                if obj in seen:
                    continue
                else:
                    seen.add(obj)
                    yield obj
                insp = inspect(obj)
                for relationship in insp.mapper.relationships:
                    related = getattr(obj, relationship.key)
                    if relationship.uselist:
                        deque.extend(related)
                    elif related is not None:
                        deque.append(related)

    The function can be demonstrated as follows::

        Base = declarative_base()


        class A(Base):
            __tablename__ = "a"
            id = Column(Integer, primary_key=True)
            bs = relationship("B", backref="a")


        class B(Base):
            __tablename__ = "b"
            id = Column(Integer, primary_key=True)
            a_id = Column(ForeignKey("a.id"))
            c_id = Column(ForeignKey("c.id"))
            c = relationship("C", backref="bs")


        class C(Base):
            __tablename__ = "c"
            id = Column(Integer, primary_key=True)


        a1 = A(bs=[B(), B(c=C())])


        for obj in walk(a1):
            print(obj)

    Output:

    .. sourcecode:: text

        <__main__.A object at 0x10303b190>
        <__main__.B object at 0x103025210>
        <__main__.B object at 0x10303b0d0>
        <__main__.C object at 0x103025490>



有没有办法自动仅拥有唯一的关键字（或其他类型的对象），而无需对关键字进行查询并获取对包含该关键字的行的引用？
---------------------------------------------------------------------------------------------

Is there a way to automagically have only unique keywords (or other kinds of objects) without doing a query for the keyword and getting a reference to the row containing that keyword?

.. tab:: 中文

    读者在阅读文档中的 many-to-many 示例时，会注意到这样一个问题：
    如果你创建了两个相同的 ``Keyword``，它们会被分别插入数据库两次。
    这确实有点不方便。

    为了解决这个问题，可以使用配方 `UniqueObject <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject>`_。

.. tab:: 英文

    When people read the many-to-many example in the docs, they get hit with the
    fact that if you create the same ``Keyword`` twice, it gets put in the DB twice.
    Which is somewhat inconvenient.

    This `UniqueObject <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject>`_ recipe was created to address this issue.

.. _faq_post_update_update:

为什么 post_update 除了第一个 UPDATE 之外还会发出 UPDATE？
-----------------------------------------------------------------

Why does post_update emit UPDATE in addition to the first UPDATE?

.. tab:: 中文

    文档 :ref:`post_update` 中介绍的 post_update 特性，会在某个绑定关系的外键发生变更时，除了常规的 INSERT/UPDATE/DELETE 操作外，还额外发出一个 UPDATE 语句。
    这个 UPDATE 的主要目的是与该行的 INSERT 或 DELETE 配对，
    以便在插入后设置或在删除前清除外键引用，从而打破互相依赖的外键之间的循环引用。
    然而，当前实现还会在目标行本身要被 UPDATE 时，额外产生一条 UPDATE，这通常是 *不必要* 的，并显得冗余。

    不过，研究如何移除这类 “UPDATE / UPDATE” 行为发现，
    这将需要对工作单元（unit of work）机制进行重大修改，
    不仅涉及 post_update 的实现本身，还涉及一些与 post_update 无关的区域；
    这是因为在某些情况下，需要对 UPDATE 的执行顺序进行逆转，
    而这又会影响其他场景，比如正确处理被引用的主键值的更新（详见 :ticket:`1063` 的原型）。

    答案是：post_update 的用途是打破两个互相依赖的外键之间的循环。
    如果我们希望这个打破循环的过程仅限于目标表的 INSERT/DELETE 操作，
    那么这就要求其他 UPDATE 的排序机制更加宽松，
    这又会在其他边缘场景中引发错误。

.. tab:: 英文

    The post_update feature, documented at :ref:`post_update`, involves that an
    UPDATE statement is emitted in response to changes to a particular
    relationship-bound foreign key, in addition to the INSERT/UPDATE/DELETE that
    would normally be emitted for the target row.  While the primary purpose of this
    UPDATE statement is that it pairs up with an INSERT or DELETE of that row, so
    that it can post-set or pre-unset a foreign key reference in order to break a
    cycle with a mutually dependent foreign key, it currently is also bundled as a
    second UPDATE that emits when the target row itself is subject to an UPDATE.
    In this case, the UPDATE emitted by post_update is *usually* unnecessary
    and will often appear wasteful.

    However, some research into trying to remove this "UPDATE / UPDATE" behavior
    reveals that major changes to the unit of work process would need to occur  not
    just throughout the post_update implementation, but also in areas that aren't
    related to post_update for this to work, in that the order of operations would
    need to be reversed on the non-post_update side in some cases, which in turn
    can impact other cases, such as correctly handling an UPDATE of a referenced
    primary key value (see :ticket:`1063` for a proof of concept).

    The answer is that "post_update" is used to break a cycle between two
    mutually dependent foreign keys, and to have this cycle breaking be limited
    to just INSERT/DELETE of the target table implies that the ordering of UPDATE
    statements elsewhere would need to be liberalized, leading to breakage
    in other edge cases.
