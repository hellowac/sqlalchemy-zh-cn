==============
会话基础知识
==============

Session Basics

会话有什么用？
--------------------------

What does the Session do ?

.. tab:: 中文

    从最一般的意义上说，:class:`~.Session` 建立了与数据库的所有对话，并且代表了在其生命周期内加载或关联的所有对象的“保持区”。它提供了进行 SELECT 和其他查询的接口，这些查询将返回和修改 ORM 映射对象。ORM 对象本身保存在 :class:`.Session` 中，位于称为 :term:`identity map` 的结构中——一个维护每个对象唯一副本的数据结构，其中“唯一”意味着“具有特定主键的唯一对象”。

    在其最常见的使用模式中，:class:`.Session` 以一种大多无状态的形式开始。一旦发出查询或其他对象与其持久化，它将从与 :class:`.Session` 关联的 :class:`_engine.Engine` 请求连接资源，然后在该连接上建立事务。该事务将持续有效，直到 :class:`.Session` 被指示提交或回滚事务。当事务结束时，与 :class:`_engine.Engine` 关联的连接资源将释放(:term:`released`) 到由引擎管理的连接池中。然后，一个新的事务将以新的连接签出开始。

    由 :class:`_orm.Session` 维护的 ORM 对象是 :term:`instrumented` 的，这样每当在 Python 程序中修改属性或集合时，都会生成一个变更事件，该事件由 :class:`_orm.Session` 记录。每当即将查询数据库或即将提交事务时，:class:`_orm.Session` 会首先将内存中存储的所有待处理更改 **刷新** 到数据库。这称为 :term:`unit of work` 模式。

    使用 :class:`.Session` 时，考虑它维护的 ORM 映射对象作为 **代理对象** 到数据库行是有用的，这些对象是本地于 :class:`.Session` 持有的事务的。为了保持对象状态与数据库中的实际内容匹配，有多种事件会导致对象重新访问数据库以保持同步。可以将对象从 :class:`.Session` 中“分离”并继续使用它们，尽管这种做法有其警告。通常情况下，当你想再次使用它们时，你会将分离的对象重新关联到另一个 :class:`.Session`，以便它们可以恢复表示数据库状态的正常任务。

.. tab:: 英文

    In the most general sense, the :class:`~.Session` establishes all conversations
    with the database and represents a "holding zone" for all the objects which
    you've loaded or associated with it during its lifespan. It provides the
    interface where SELECT and other queries are made that will return and modify
    ORM-mapped objects.  The ORM objects themselves are maintained inside the
    :class:`.Session`, inside a structure called the :term:`identity map` - a data
    structure that maintains unique copies of each object, where "unique" means
    "only one object with a particular primary key".

    The :class:`.Session` in its most common pattern of use begins in a mostly
    stateless form. Once queries are issued or other objects are persisted with it,
    it requests a connection resource from an :class:`_engine.Engine` that is
    associated with the :class:`.Session`, and then establishes a transaction on
    that connection. This transaction remains in effect until the :class:`.Session`
    is instructed to commit or roll back the transaction.   When the transaction
    ends, the connection resource associated with the :class:`_engine.Engine`
    is :term:`released` to the connection pool managed by the engine.   A new
    transaction then starts with a new connection checkout.

    The ORM objects maintained by a :class:`_orm.Session` are :term:`instrumented`
    such that whenever an attribute or a collection is modified in the Python
    program, a change event is generated which is recorded by the
    :class:`_orm.Session`.  Whenever the database is about to be queried, or when
    the transaction is about to be committed, the :class:`_orm.Session` first
    **flushes** all pending changes stored in memory to the database. This is
    known as the :term:`unit of work` pattern.

    When using a :class:`.Session`, it's useful to consider the ORM mapped objects
    that it maintains as **proxy objects** to database rows, which are local to the
    transaction being held by the :class:`.Session`.    In order to maintain the
    state on the objects as matching what's actually in the database, there are a
    variety of events that will cause objects to re-access the database in order to
    keep synchronized.   It is possible to "detach" objects from a
    :class:`.Session`, and to continue using them, though this practice has its
    caveats.  It's intended that usually, you'd re-associate detached objects with
    another :class:`.Session` when you want to work with them again, so that they
    can resume their normal task of representing database state.

.. _session_basics:

使用会话的基础知识
-------------------------

Basics of Using a Session

.. tab:: 中文

    这里介绍了最基本的 :class:`.Session` 使用模式。

.. tab:: 英文

    The most basic :class:`.Session` use patterns are presented here.

.. _session_getting:

打开和关闭会话
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Opening and Closing a Session

.. tab:: 中文

    :class:`_orm.Session` 可以单独构造，也可以通过 :class:`_orm.sessionmaker` 类来构造。它通常在初始化时传入一个 :class:`_engine.Engine` 作为连接资源的来源。一个典型的用法如下所示::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        # 一个 Engine，Session 将使用它进行连接
        # 资源管理
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # 创建 session 并添加对象
        with Session(engine) as session:
            session.add(some_object)
            session.add(some_other_object)
            session.commit()

    在上述代码中，:class:`_orm.Session` 是通过一个与特定数据库 URL 相关联的 :class:`_engine.Engine` 实例化的。随后它被用在一个 Python 上下文管理器中（即 ``with:`` 语句），这样在代码块结束时它会自动关闭；这等效于调用 :meth:`_orm.Session.close` 方法。

    对 :meth:`_orm.Session.commit` 的调用是可选的，只有当我们使用 :class:`_orm.Session` 执行了需要持久化到数据库的新数据操作时才需要调用。如果我们只进行了 SELECT 查询而没有写入任何更改，那么就不需要调用 :meth:`_orm.Session.commit`。

    .. note::

        请注意，在调用 :meth:`_orm.Session.commit`（无论是显式调用还是在使用上下文管理器时隐式调用）之后，所有与 :class:`.Session` 相关联的对象都会被 :term:`expired`，也就是说它们的内容会被清除，并在下一次事务中重新加载。如果这些对象被 :term:`detached`，它们将失去功能，直到重新与一个新的 :class:`.Session` 相关联，除非使用了 :paramref:`.Session.expire_on_commit` 参数来禁用这一行为。详见 :ref:`session_committing` 一节。

.. tab:: 英文

    The :class:`_orm.Session` may be constructed on its own or by using the :class:`_orm.sessionmaker` class.    It typically is passed a single :class:`_engine.Engine` as a source of connectivity up front.  A typical use may look like::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        # an Engine, which the Session will use for connection
        # resources
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # create session and add objects
        with Session(engine) as session:
            session.add(some_object)
            session.add(some_other_object)
            session.commit()

    Above, the :class:`_orm.Session` is instantiated with an :class:`_engine.Engine` associated with a particular database URL.   It is then used in a Python context manager (i.e. ``with:`` statement) so that it is automatically closed at the end of the block; this is equivalent to calling the :meth:`_orm.Session.close` method.

    The call to :meth:`_orm.Session.commit` is optional, and is only needed if the work we've done with the :class:`_orm.Session` includes new data to be persisted to the database.  If we were only issuing SELECT calls and did not need to write any changes, then the call to :meth:`_orm.Session.commit` would be unnecessary.

    .. note::

        Note that after :meth:`_orm.Session.commit` is called, either explicitly or when using a context manager, all objects associated with the :class:`.Session` are :term:`expired`, meaning their contents are erased to be re-loaded within the next transaction. If these objects are instead :term:`detached`, they will be non-functional until re-associated with a new :class:`.Session`, unless the :paramref:`.Session.expire_on_commit` parameter is used to disable this behavior. See the section :ref:`session_committing` for more detail.


.. _session_begin_commit_rollback_block:

构建开始/提交/回滚块
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Framing out a begin / commit / rollback block

.. tab:: 中文

    我们还可以在上下文管理器中包裹对 :meth:`_orm.Session.commit` 的调用，以及事务的整体“框架”，适用于那些需要将数据提交到数据库的场景。所谓“框架”是指：如果所有操作都成功执行，则调用 :meth:`_orm.Session.commit` 方法；如果抛出任何异常，则调用 :meth:`_orm.Session.rollback` 方法以立即回滚事务，然后将异常继续抛出。在 Python 中，这通常使用 ``try: / except: / else:`` 结构表达，如下所示::

        # 展示上下文管理器内部实际做的事情的详细版本
        with Session(engine) as session:
            session.begin()
            try:
                session.add(some_object)
                session.add(some_other_object)
            except:
                session.rollback()
                raise
            else:
                session.commit()

    上面的长格式操作序列，可以更简洁地通过 :meth:`_orm.Session.begin` 方法返回的 :class:`_orm.SessionTransaction` 对象来实现，该对象提供了相同操作序列的上下文管理器接口::

        # 创建 session 并添加对象
        with Session(engine) as session:
            with session.begin():
                session.add(some_object)
                session.add(some_other_object)
            # 如果没有异常，内部上下文会调用 session.commit()
        # 外部上下文会调用 session.close()

    更进一步地，也可以将这两个上下文合并::

        # 创建 session 并添加对象
        with Session(engine) as session, session.begin():
            session.add(some_object)
            session.add(some_other_object)
        # 如果没有异常，内部上下文会调用 session.commit()
        # 外部上下文会调用 session.close()

.. tab:: 英文

    We may also enclose the :meth:`_orm.Session.commit` call and the overall "framing" of the transaction within a context manager for those cases where we will be committing data to the database.  By "framing" we mean that if all operations succeed, the :meth:`_orm.Session.commit` method will be called, but if any exceptions are raised, the :meth:`_orm.Session.rollback` method will be called so that the transaction is rolled back immediately, before propagating the exception outward.   In Python this is most fundamentally expressed using a ``try: / except: / else:`` block such as::

        # verbose version of what a context manager will do
        with Session(engine) as session:
            session.begin()
            try:
                session.add(some_object)
                session.add(some_other_object)
            except:
                session.rollback()
                raise
            else:
                session.commit()

    The long-form sequence of operations illustrated above can be achieved more succinctly by making use of the :class:`_orm.SessionTransaction` object returned by the :meth:`_orm.Session.begin` method, which provides a context manager interface for the same sequence of operations::

        # create session and add objects
        with Session(engine) as session:
            with session.begin():
                session.add(some_object)
                session.add(some_other_object)
            # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()

    More succinctly, the two contexts may be combined::

        # create session and add objects
        with Session(engine) as session, session.begin():
            session.add(some_object)
            session.add(some_other_object)
        # inner context calls session.commit(), if there were no exceptions
        # outer context calls session.close()

使用 sessionmaker
~~~~~~~~~~~~~~~~~~~~

Using a sessionmaker

.. tab:: 中文

    :class:`_orm.sessionmaker` 的目的是提供一个具有固定配置的 :class:`_orm.Session` 对象工厂。由于应用程序通常会在模块作用域中定义一个 :class:`_engine.Engine` 对象，:class:`_orm.sessionmaker` 可以提供一个基于该 engine 构造 :class:`_orm.Session` 对象的工厂::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # 一个 Engine，Session 将使用它进行连接资源的管理，通常在模块作用域中定义
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # 一个 sessionmaker()，通常也在与 engine 相同的作用域中定义
        Session = sessionmaker(engine)

        # 现在我们可以直接构造 Session()，无需每次都传入 engine
        with Session() as session:
            session.add(some_object)
            session.add(some_other_object)
            session.commit()
        # 自动关闭 session

    :class:`_orm.sessionmaker` 类似于 :class:`_engine.Engine`，都是在模块级作用域中作为函数级连接 / 会话的工厂使用。因此它也拥有自己的 :meth:`_orm.sessionmaker.begin` 方法，类似于 :meth:`_engine.Engine.begin`，该方法会返回一个 :class:`_orm.Session` 对象，并同时管理一个 begin/commit/rollback 块::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # 一个 Engine，Session 将使用它进行连接资源的管理
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # 一个 sessionmaker()，通常也在与 engine 相同的作用域中定义
        Session = sessionmaker(engine)

        # 我们现在可以构造一个 Session() 并一次性包含 begin()/commit()/rollback()
        with Session.begin() as session:
            session.add(some_object)
            session.add(some_other_object)
        # 提交事务并关闭 session

    在上述代码中，当 ``with:`` 块结束时，:class:`_orm.Session` 会自动提交其事务，并关闭该 :class:`_orm.Session` 实例。

    在实际应用中，:class:`.sessionmaker` 工厂应与通过 :func:`_sa.create_engine` 创建的 :class:`_engine.Engine` 对象处于相同作用域，通常是在模块级或全局作用域。由于它们都是工厂对象，因此可以同时被多个函数和线程安全地使用。

    .. seealso::

        :class:`_orm.sessionmaker`

        :class:`_orm.Session`

.. tab:: 英文

    The purpose of :class:`_orm.sessionmaker` is to provide a factory for :class:`_orm.Session` objects with a fixed configuration.   As it is typical that an application will have an :class:`_engine.Engine` object in module scope, the :class:`_orm.sessionmaker` can provide a factory for :class:`_orm.Session` objects that are constructed against this engine::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # an Engine, which the Session will use for connection
        # resources, typically in module scope
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # a sessionmaker(), also in the same scope as the engine
        Session = sessionmaker(engine)

        # we can now construct a Session() without needing to pass the
        # engine each time
        with Session() as session:
            session.add(some_object)
            session.add(some_other_object)
            session.commit()
        # closes the session

    The :class:`_orm.sessionmaker` is analogous to the :class:`_engine.Engine` as a module-level factory for function-level sessions / connections.   As such it also has its own :meth:`_orm.sessionmaker.begin` method, analogous to :meth:`_engine.Engine.begin`, which returns a :class:`_orm.Session` object and also maintains a begin/commit/rollback block::


        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker

        # an Engine, which the Session will use for connection
        # resources
        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/")

        # a sessionmaker(), also in the same scope as the engine
        Session = sessionmaker(engine)

        # we can now construct a Session() and include begin()/commit()/rollback()
        # at once
        with Session.begin() as session:
            session.add(some_object)
            session.add(some_other_object)
        # commits the transaction, closes the session

    Where above, the :class:`_orm.Session` will both have its transaction committed as well as that the :class:`_orm.Session` will be closed, when the above ``with:`` block ends.

    When you write your application, the :class:`.sessionmaker` factory should be scoped the same as the :class:`_engine.Engine` object created by :func:`_sa.create_engine`, which is typically at module-level or global scope.  As these objects are both factories, they can be used by any number of functions and threads simultaneously.

    .. seealso::

        :class:`_orm.sessionmaker`

        :class:`_orm.Session`


.. _session_querying_20:

查询
~~~~~~~~

Querying

.. tab:: 中文

    进行查询的主要方式是使用 :func:`_sql.select` 构造函数来创建一个 :class:`_sql.Select` 对象，然后使用 :meth:`_orm.Session.execute` 和 :meth:`_orm.Session.scalars` 等方法执行该对象以返回结果。结果以 :class:`_result.Result` 对象的形式返回，包括像 :class:`_result.ScalarResult` 这样的子类型。

    SQLAlchemy ORM 查询的完整指南详见 :ref:`queryguide_toplevel`。以下是一些简要示例::

        from sqlalchemy import select
        from sqlalchemy.orm import Session

        with Session(engine) as session:
            # 查询 ``User`` 对象
            statement = select(User).filter_by(name="ed")

            # ``User`` 对象列表
            user_obj = session.scalars(statement).all()

            # 查询单独的列
            statement = select(User.name, User.fullname)

            # Row 对象的列表
            rows = session.execute(statement).all()

    .. versionchanged:: 2.0

        "2.0" 风格的查询方式现在是标准方式。关于从 1.x 系列迁移的说明请参阅 :ref:`migration_20_query_usage`。

    .. seealso::

      :ref:`queryguide_toplevel`

.. tab:: 英文

    The primary means of querying is to make use of the :func:`_sql.select` construct to create a :class:`_sql.Select` object, which is then executed to return a result using methods such as :meth:`_orm.Session.execute` and :meth:`_orm.Session.scalars`.  Results are then returned in terms of :class:`_result.Result` objects, including sub-variants such as :class:`_result.ScalarResult`.

    A complete guide to SQLAlchemy ORM querying can be found at :ref:`queryguide_toplevel`.   Some brief examples follow::

        from sqlalchemy import select
        from sqlalchemy.orm import Session

        with Session(engine) as session:
            # query for ``User`` objects
            statement = select(User).filter_by(name="ed")

            # list of ``User`` objects
            user_obj = session.scalars(statement).all()

            # query for individual columns
            statement = select(User.name, User.fullname)

            # list of Row objects
            rows = session.execute(statement).all()

    .. versionchanged:: 2.0

        "2.0" style querying is now standard.  See :ref:`migration_20_query_usage` for migration notes from the 1.x series.

    .. seealso::

      :ref:`queryguide_toplevel`

.. _session_adding:


添加新项目或现有项目
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding New or Existing Items

.. tab:: 中文

    :meth:`~.Session.add` 用于将实例放入会话中。对于 :term:`transient`（即全新创建的）实例，这将在下一个 flush 时触发 INSERT 操作。对于已经是 :term:`persistent`（即由当前会话加载的）实例，它们已在会话中，无需再添加。对于 :term:`detached`（即已从会话中移除的）实例，可以使用此方法重新关联到会话中::

        user1 = User(name="user1")
        user2 = User(name="user2")
        session.add(user1)
        session.add(user2)

        session.commit()  # 将更改写入数据库

    要一次性将多个对象添加到会话中，可以使用 :meth:`~.Session.add_all` 方法::

        session.add_all([item1, item2, item3])

    :meth:`~.Session.add` 操作会 **级联传播（cascade）**，沿着 ``save-update`` 级联路径传播。详细内容见章节 :ref:`unitofwork_cascades`。

.. tab:: 英文

    :meth:`~.Session.add` is used to place instances in the session. For :term:`transient` (i.e. brand new) instances, this will have the effect of an INSERT taking place for those instances upon the next flush. For instances which are :term:`persistent` (i.e. were loaded by this session), they are already present and do not need to be added. Instances which are :term:`detached` (i.e. have been removed from a session) may be re-associated with a session using this method::

        user1 = User(name="user1")
        user2 = User(name="user2")
        session.add(user1)
        session.add(user2)

        session.commit()  # write changes to the database

    To add a list of items to the session at once, use :meth:`~.Session.add_all`::

        session.add_all([item1, item2, item3])

    The :meth:`~.Session.add` operation **cascades** along the ``save-update`` cascade. For more details see the section :ref:`unitofwork_cascades`.

.. _session_deleting:

删除
~~~~~~~~

Deleting

.. tab:: 中文

    :meth:`~.Session.delete` 方法会将实例放入会话中标记为“待删除”的对象列表中::

        # 标记两个对象为待删除
        session.delete(obj1)
        session.delete(obj2)

        # 提交（或 flush）
        session.commit()

    :meth:`_orm.Session.delete` 会标记某个对象为删除状态，从而会针对每个受影响的主键发出 DELETE 语句。在删除操作 flush 之前，被标记为删除的对象会出现在 :attr:`_orm.Session.deleted` 集合中。删除执行后，这些对象会从 :class:`_orm.Session` 中清除，在事务提交后这一清除操作将变为永久性。

    关于 :meth:`_orm.Session.delete` 操作存在一些重要行为，尤其是与该对象存在关系的其他对象或集合的处理方式。更多内容可见 :ref:`unitofwork_cascades` 章节，但一般规则如下：

    * 默认情况下，通过 :func:`_orm.relationship` 指令与被删除对象有关联的映射对象对应的行 **不会被删除**。如果这些对象具有指向被删除行的外键约束，这些外键列将被设置为 NULL。如果这些列是非空约束，则会导致约束冲突。

    * 若要将 "SET NULL" 行为改为删除相关对象的行，请在 :func:`_orm.relationship` 中使用 :ref:`cascade_delete` 级联配置。

    * 若是通过 :paramref:`_orm.relationship.secondary` 参数连接的 "多对多" 中间表，**始终** 会在被引用对象被删除时清除相关行。

    * 当关联对象具有指向被删除对象的外键约束，且这些相关集合当前未加载到内存中，工作单元（unit of work）会发出 SELECT 查询以加载所有相关行，从而获取其主键用于执行 UPDATE 或 DELETE 操作。这样，即使在 Core 层的 :class:`_schema.ForeignKeyConstraint` 中配置了 ON DELETE CASCADE，ORM 也能在无需进一步指令的情况下完成相同的功能。

    * 可通过设置 :paramref:`_orm.relationship.passive_deletes` 参数来优化此行为，并更自然地依赖 ON DELETE CASCADE。当设置为 `True` 时，不再执行上述 SELECT 查询，但本地存在的行仍会被显式地 SET NULL 或 DELETE。若将 :paramref:`_orm.relationship.passive_deletes` 设置为字符串 ``"all"``，则会禁用 **所有** 与关联对象相关的更新/删除。

    * 当某对象被标记为删除并实际执行 DELETE 操作时，该对象 **不会** 自动从引用它的集合或对象中移除。当 :class:`_orm.Session` 过期后，这些集合可能会重新加载，此时该对象将不再存在。然而，更推荐的做法是，不使用 :meth:`_orm.Session.delete` 删除这些对象，而是先将对象从集合中移除，再使用 :ref:`cascade_delete_orphan` 实现因集合变更而触发的删除行为。相关示例见 :ref:`session_deleting_from_collections`。

    .. seealso::

        :ref:`cascade_delete` - 描述 "删除级联"，当主对象被删除时标记其关联对象也应被删除。

        :ref:`cascade_delete_orphan` - 描述 "孤儿删除级联"，当关联对象从主对象中解除关联时被删除。

        :ref:`session_deleting_from_collections` - 关于 :meth:`_orm.Session.delete` 如何与关系刷新机制交互的背景说明。

.. tab:: 英文

    The :meth:`~.Session.delete` method places an instance into the Session's list of objects to be marked as deleted::

        # mark two objects to be deleted
        session.delete(obj1)
        session.delete(obj2)

        # commit (or flush)
        session.commit()

    :meth:`_orm.Session.delete` marks an object for deletion, which will result in a DELETE statement emitted for each primary key affected. Before the pending deletes are flushed, objects marked by "delete" are present in the :attr:`_orm.Session.deleted` collection.  After the DELETE, they are expunged from the :class:`_orm.Session`, which becomes permanent after the transaction is committed.

    There are various important behaviors related to the :meth:`_orm.Session.delete` operation, particularly in how relationships to other objects and collections are handled.    There's more information on how this works in the section :ref:`unitofwork_cascades`, but in general the rules are:

    * Rows that correspond to mapped objects that are related to a deleted object via the :func:`_orm.relationship` directive are **not deleted by default**.  If those objects have a foreign key constraint back to the row being deleted, those columns are set to NULL.   This will cause a constraint violation if the columns are non-nullable.

    * To change the "SET NULL" into a DELETE of a related object's row, use the :ref:`cascade_delete` cascade on the :func:`_orm.relationship`.

    * Rows that are in tables linked as "many-to-many" tables, via the :paramref:`_orm.relationship.secondary` parameter, **are** deleted in all cases when the object they refer to is deleted.

    * When related objects include a foreign key constraint back to the object being deleted, and the related collections to which they belong are not currently loaded into memory, the unit of work will emit a SELECT to fetch all related rows, so that their primary key values can be used to emit either UPDATE or DELETE statements on those related rows.  In this way, the ORM without further instruction will perform the function of ON DELETE CASCADE, even if this is configured on Core :class:`_schema.ForeignKeyConstraint` objects.

    * The :paramref:`_orm.relationship.passive_deletes` parameter can be used to tune this behavior and rely upon "ON DELETE CASCADE" more naturally; when set to True, this SELECT operation will no longer take place, however rows that are locally present will still be subject to explicit SET NULL or DELETE.   Setting :paramref:`_orm.relationship.passive_deletes` to the string ``"all"`` will disable **all** related object update/delete.

    * When the DELETE occurs for an object marked for deletion, the object
      is not automatically removed from collections or object references that
      refer to it.   When the :class:`_orm.Session` is expired, these collections
      may be loaded again so that the object is no longer present.  However, it is preferable that instead of using :meth:`_orm.Session.delete` for these objects, the object should instead be removed from its collection and then :ref:`cascade_delete_orphan` should be used so that it is deleted as a secondary effect of that collection removal.   See the section :ref:`session_deleting_from_collections` for an example of this.

    .. seealso::

        :ref:`cascade_delete` - describes "delete cascade", which marks related objects for deletion when a lead object is deleted.

        :ref:`cascade_delete_orphan` - describes "delete orphan cascade", which marks related objects for deletion when they are de-associated from their lead object.

        :ref:`session_deleting_from_collections` - important background on :meth:`_orm.Session.delete` as involves relationships being refreshed in memory.

.. _session_flushing:

刷新
~~~~~~~~

Flushing

.. tab:: 中文

    当使用 :class:`~sqlalchemy.orm.session.Session` 的默认配置时，flush（刷新）步骤几乎总是自动完成的。具体来说，当因调用 :class:`_query.Query` 或术语中所说的 :term:`2.0-style` 方法 :meth:`_orm.Session.execute` 而将要发出某个 SQL 语句时，flush 会在其之前发生；同样，在调用 :meth:`~.Session.commit` 以提交事务之前也会自动发生 flush；另外，在使用 :meth:`~.Session.begin_nested` 发出 SAVEPOINT 之前，也会发生 flush。

    你可以在任何时候手动调用 :meth:`~.Session.flush` 来强制进行一次刷新操作::

        session.flush()

    某些方法范围内自动发生的刷新称为 **自动刷新（autoflush）**。Autoflush 是一个可配置的自动刷新机制，通常发生在以下方法开始执行时：

    * 调用 :meth:`_orm.Session.execute` 以及其他执行 SQL 的方法，并且目标是启用了 ORM 的 SQL 构造（如指向 ORM 实体或 ORM 映射属性的 :func:`_sql.select` 对象）时；
    * 通过 :class:`_query.Query` 发送 SQL 到数据库时；
    * 在调用 :meth:`.Session.merge` 方法、并查询数据库之前；
    * 对象被 :ref:`刷新 <session_expiring>` 时；
    * 对尚未加载的对象属性触发 ORM 的 :term:`lazy load`（延迟加载）操作时。

    同时，也有一些刷新是 **无条件发生** 的，这些情况包括关键事务边界内的操作：

    * 在 :meth:`.Session.commit` 方法执行过程中；
    * 调用 :meth:`.Session.begin_nested` 时；
    * 使用 :meth:`.Session.prepare`（两阶段提交）方法时。

    **Autoflush** 行为在上述情形中可以通过在构造 :class:`.Session` 或 :class:`.sessionmaker` 时传入 :paramref:`.Session.autoflush=False` 来禁用::

        Session = sessionmaker(autoflush=False)

    此外，还可以在使用某个 :class:`.Session` 时临时禁用 autoflush，通过使用 :attr:`.Session.no_autoflush` 上下文管理器实现::

        with mysession.no_autoflush:
            mysession.add(some_object)
            mysession.flush()

    **重申一遍：** 无论设置是否启用 autoflush，在调用诸如 :meth:`.Session.commit` 和 :meth:`.Session.begin_nested` 等事务性方法时，如果会话中仍存在待处理更改，flush **始终会发生**。

    由于 :class:`.Session` 仅会在 :term:`DBAPI` 事务上下文中对数据库执行 SQL，所有的 "flush" 操作也都必须在数据库事务中执行（具体受数据库事务的 :ref:`隔离级别 <session_transaction_isolation>` 影响），前提是 DBAPI 并未启用 :ref:`驱动级自动提交 <dbapi_autocommit>` 模式。这意味着，如果数据库连接在其事务设置中保证了 :term:`原子性`，那么 flush 中的任意 DML 语句失败时，整个操作将会被回滚。

    当 flush 过程中发生失败时，为了继续使用当前 :class:`_orm.Session`，必须显式调用 :meth:`~.Session.rollback` 来回滚，即便底层事务已经被回滚（即使数据库驱动启用了驱动级自动提交）。这样做的目的是维护所谓“子事务（subtransaction）”的嵌套模式一致性。FAQ 部分 :ref:`faq_session_rollback` 中对此行为有更详细的说明。

    .. seealso::

        :ref:`faq_session_rollback` - 更深入地解释了为什么在 flush 失败后必须调用 :meth:`_orm.Session.rollback`。

.. tab:: 英文

    When the :class:`~sqlalchemy.orm.session.Session` is used with its default configuration, the flush step is nearly always done transparently. Specifically, the flush occurs before any individual SQL statement is issued as a result of a :class:`_query.Query` or a :term:`2.0-style` :meth:`_orm.Session.execute` call, as well as within the :meth:`~.Session.commit` call before the transaction is committed. It also occurs before a SAVEPOINT is issued when :meth:`~.Session.begin_nested` is used.

    A :class:`.Session` flush can be forced at any time by calling the :meth:`~.Session.flush` method::

        session.flush()

    The flush which occurs automatically within the scope of certain methods is known as **autoflush**.  Autoflush is defined as a configurable, automatic flush call which occurs at the beginning of methods including:

    * :meth:`_orm.Session.execute` and other SQL-executing methods, when used against ORM-enabled SQL constructs, such as :func:`_sql.select` objects that refer to ORM entities and/or ORM-mapped attributes
    * When a :class:`_query.Query` is invoked to send SQL to the database
    * Within the :meth:`.Session.merge` method before querying the database
    * When objects are :ref:`refreshed <session_expiring>`
    * When ORM :term:`lazy load` operations occur against unloaded object attributes.

    There are also points at which flushes occur **unconditionally**; these points are within key transactional boundaries which include:

    * Within the process of the :meth:`.Session.commit` method
    * When :meth:`.Session.begin_nested` is called
    * When the :meth:`.Session.prepare` 2PC method is used.

    The **autoflush** behavior, as applied to the previous list of items, can be disabled by constructing a :class:`.Session` or :class:`.sessionmaker` passing the :paramref:`.Session.autoflush` parameter as ``False``::

        Session = sessionmaker(autoflush=False)

    Additionally, autoflush can be temporarily disabled within the flow of using a :class:`.Session` using the :attr:`.Session.no_autoflush` context manager::

        with mysession.no_autoflush:
            mysession.add(some_object)
            mysession.flush()

    **To reiterate:** The flush process **always occurs** when transactional methods such as :meth:`.Session.commit` and :meth:`.Session.begin_nested` are called, regardless of any "autoflush" settings, when the :class:`.Session` has remaining pending changes to process.

    As the :class:`.Session` only invokes SQL to the database within the context of a :term:`DBAPI` transaction, all "flush" operations themselves only occur within a database transaction (subject to the :ref:`isolation level <session_transaction_isolation>` of the database transaction), provided that the DBAPI is not in :ref:`driver level autocommit <dbapi_autocommit>` mode. This means that assuming the database connection is providing for :term:`atomicity` within its transactional settings, if any individual DML statement inside the flush fails, the entire operation will be rolled back.

    When a failure occurs within a flush, in order to continue using that same :class:`_orm.Session`, an explicit call to :meth:`~.Session.rollback` is required after a flush fails, even though the underlying transaction will have been rolled back already (even if the database driver is technically in driver-level autocommit mode).  This is so that the overall nesting pattern of so-called "subtransactions" is consistently maintained. The FAQ section :ref:`faq_session_rollback` contains a more detailed description of this behavior.

    .. seealso::

        :ref:`faq_session_rollback` - further background on why :meth:`_orm.Session.rollback` must be called when a flush fails.

.. _session_get:

通过主键获取
~~~~~~~~~~~~~~~~~~

Get by Primary Key

.. tab:: 中文

    由于 :class:`_orm.Session` 使用了一个 :term:`标识图（identity map）` 来通过主键引用当前内存中的对象，提供了 :meth:`_orm.Session.get` 方法用于根据主键定位对象。该方法首先会在当前标识图中查找，如果未命中才会查询数据库。例如，查找主键为 ``(5,)`` 的 ``User`` 实体::

        my_user = session.get(User, 5)

    :meth:`_orm.Session.get` 同时也支持复合主键的形式，可以使用元组或字典传入，并支持附加参数以控制加载方式和执行选项。完整参数说明详见 :meth:`_orm.Session.get`。

    .. seealso::

        :meth:`_orm.Session.get`

.. tab:: 英文

    As the :class:`_orm.Session` makes use of an :term:`identity map` which refers to current in-memory objects by primary key, the :meth:`_orm.Session.get` method is provided as a means of locating objects by primary key, first looking within the current identity map and then querying the database for non present values.  Such as, to locate a ``User`` entity with primary key identity ``(5, )``::

        my_user = session.get(User, 5)

    The :meth:`_orm.Session.get` also includes calling forms for composite primary key values, which may be passed as tuples or dictionaries, as well as additional parameters which allow for specific loader and execution options. See :meth:`_orm.Session.get` for the complete parameter list.

    .. seealso::

        :meth:`_orm.Session.get`

.. _session_expiring:

过期/刷新
~~~~~~~~~~~~~~~~~~~~~

Expiring / Refreshing

.. tab:: 中文

    在使用 :class:`_orm.Session` 时，一个非常重要且经常遇到的考虑因素是：如何处理那些已经从数据库加载到对象中的状态，尤其是在事务当前状态变化时保持同步的问题。SQLAlchemy ORM 是基于 :term:`标识图（identity map）` 的概念建立的，这意味着当某个对象从 SQL 查询中被“加载”时，系统会维持一个唯一的 Python 对象实例，与特定的数据库标识对应。这意味着如果我们发出两个独立的查询，虽然查询的是相同行，但返回的映射对象将是同一个 Python 对象::

      >>> u1 = session.scalars(select(User).where(User.id == 5)).one()
      >>> u2 = session.scalars(select(User).where(User.id == 5)).one()
      >>> u1 is u2
      True

    由此出发，当 ORM 从查询中获得行数据时，**如果某对象已经被加载过，它将跳过属性的填充**。其设计假设是事务在一个完美隔离的环境中运行；如果事务不具备这样的隔离性，应用程序可以根据需要采取额外措施，从数据库事务中刷新对象状态。详见 FAQ 条目 :ref:`faq_session_identity`。

    当一个 ORM 映射对象被加载到内存中后，可以通过以下三种方式将其内容刷新为当前事务中的最新数据：

    * **`expire()` 方法** 
      - :meth:`_orm.Session.expire` 方法会清除对象中选定或全部属性的内容，使得当这些属性下次被访问时，
        会自动从数据库中加载，例如通过 :term:`延迟加载（lazy loading）` 机制::

        session.expire(u1)
        u1.some_attribute  # <-- 访问时将从事务中延迟加载

      ..

    * **`refresh()` 方法** - 与之密切相关的是 :meth:`_orm.Session.refresh` 方法，它执行与 `expire()` 相同的操作，但会立即发出一个或多个 SQL 查询，从而实际刷新对象的内容::

        session.refresh(u1)  # <-- 立即发出 SQL 查询
        u1.some_attribute  # <-- 从事务中刷新后的值

      ..

    * **`populate_existing()` 方法或执行选项** - 现在作为一个执行选项记录在 :ref:`orm_queryguide_populate_existing` 中；在旧版本中，它是 :class:`_orm.Query` 对象上的 :meth:`_orm.Query.populate_existing` 方法。该操作表示从查询中返回的对象应无条件地使用数据库中的内容重新填充::

        u2 = session.scalars(
            select(User).where(User.id == 5).execution_options(populate_existing=True)
        ).one()

      ..

    关于 refresh / expire 概念的更多讨论，请参见 :ref:`session_expire`。

    .. seealso::

      :ref:`session_expire`

      :ref:`faq_session_identity`

.. tab:: 英文

    An important consideration that will often come up when using the :class:`_orm.Session` is that of dealing with the state that is present on objects that have been loaded from the database, in terms of keeping them synchronized with the current state of the transaction.   The SQLAlchemy ORM is based around the concept of an :term:`identity map` such that when an object is "loaded" from a SQL query, there will be a unique Python object instance maintained corresponding to a particular database identity. This means if we emit two separate queries, each for the same row, and get a mapped object back, the two queries will have returned the same Python object::

        >>> u1 = session.scalars(select(User).where(User.id == 5)).one()
        >>> u2 = session.scalars(select(User).where(User.id == 5)).one()
        >>> u1 is u2
        True

    Following from this, when the ORM gets rows back from a query, it will **skip the population of attributes** for an object that's already loaded. The design assumption here is to assume a transaction that's perfectly isolated, and then to the degree that the transaction isn't isolated, the application can take steps on an as-needed basis to refresh objects from the database transaction.  The FAQ entry at :ref:`faq_session_identity` discusses this concept in more detail.

    When an ORM mapped object is loaded into memory, there are three general ways to refresh its contents with new data from the current transaction:

    * **the expire() method** - the :meth:`_orm.Session.expire` method will erase the contents of selected or all attributes of an object, such that they will be loaded from the database when they are next accessed, e.g. using a :term:`lazy loading` pattern::

        session.expire(u1)
        u1.some_attribute  # <-- lazy loads from the transaction

      ..

    * **the refresh() method** - closely related is the :meth:`_orm.Session.refresh` method, which does everything the :meth:`_orm.Session.expire` method does but also emits one or more SQL queries immediately to actually refresh the contents of the object::

        session.refresh(u1)  # <-- emits a SQL query
        u1.some_attribute  # <-- is refreshed from the transaction

        ..

    * **the populate_existing() method or execution option** - This is now an execution option documented at :ref:`orm_queryguide_populate_existing`; in legacy form it's found on the :class:`_orm.Query` object as the :meth:`_orm.Query.populate_existing` method. This operation in either form indicates that objects being returned from a query should be unconditionally re-populated from their contents in the database::

        u2 = session.scalars(
            select(User).where(User.id == 5).execution_options(populate_existing=True)
        ).one()

      ..

    Further discussion on the refresh / expire concept can be found at :ref:`session_expire`.

    .. seealso::

      :ref:`session_expire`

      :ref:`faq_session_identity`



使用任意 WHERE 子句进行更新和删除
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UPDATE and DELETE with arbitrary WHERE clause

.. tab:: 中文

    SQLAlchemy 2.0 引入了更强大的能力，支持多种基于 ORM 的 INSERT、UPDATE 和 DELETE 语句的发出方式。详见文档 :doc:`queryguide/dml`。

    .. seealso::

        :doc:`queryguide/dml`

        :ref:`orm_queryguide_update_delete_where`

.. tab:: 英文

    SQLAlchemy 2.0 includes enhanced capabilities for emitting several varieties of ORM-enabled INSERT, UPDATE and DELETE statements.  See the document at :doc:`queryguide/dml` for documentation.

    .. seealso::

        :doc:`queryguide/dml`

        :ref:`orm_queryguide_update_delete_where`


.. _session_autobegin:

自动开始
~~~~~~~~~~

Auto Begin

.. tab:: 中文

    :class:`_orm.Session` 对象具有一种称为 **autobegin** （自动开始）的行为。这意味着，一旦对 :class:`_orm.Session` 执行了任何操作——无论是涉及对象状态变化的内部状态修改，还是需要数据库连接的操作——该 :class:`_orm.Session` 会自动将自己视为处于“事务性”状态中。

    当 :class:`_orm.Session` 首次构造时，其内部并不包含任何事务状态。事务状态会在以下情况中自动开始：调用了例如 :meth:`_orm.Session.add` 或 :meth:`_orm.Session.execute` 等方法，执行了某个 :class:`_orm.Query` 以返回结果（该操作最终也会调用 :meth:`_orm.Session.execute`），或对某个 :term:`persistent`（持久化）对象的属性进行了修改。

    可以通过访问 :meth:`_orm.Session.in_transaction` 方法来检查当前是否处于事务状态，该方法返回布尔值 ``True`` 或 ``False``，指示 "autobegin" 步骤是否已经发生。虽然通常不需要，但也可以通过 :meth:`_orm.Session.get_transaction` 方法获取表示当前事务状态的实际 :class:`_orm.SessionTransaction` 对象。

    此外，也可以显式地通过调用 :meth:`_orm.Session.begin` 方法来开始事务状态。调用此方法时，:class:`_orm.Session` 会无条件地进入“事务性”状态。:meth:`_orm.Session.begin` 可以作为上下文管理器使用，详细说明请见 :ref:`session_begin_commit_rollback_block`。

.. tab:: 英文

    The :class:`_orm.Session` object features a behavior known as **autobegin**. This indicates that the :class:`_orm.Session` will internally consider itself to be in a "transactional" state as soon as any work is performed with the :class:`_orm.Session`, either involving modifications to the internal state of the :class:`_orm.Session` with regards to object state changes, or with operations that require database connectivity.

    When the :class:`_orm.Session` is first constructed, there's no transactional state present.   The transactional state is begun automatically, when a method such as :meth:`_orm.Session.add` or :meth:`_orm.Session.execute` is invoked, or similarly if a :class:`_orm.Query` is executed to return results (which ultimately uses :meth:`_orm.Session.execute`), or if an attribute is modified on a :term:`persistent` object.

    The transactional state can be checked by accessing the :meth:`_orm.Session.in_transaction` method, which returns ``True`` or ``False`` indicating if the "autobegin" step has proceeded. While not normally needed, the :meth:`_orm.Session.get_transaction` method will return the actual :class:`_orm.SessionTransaction` object that represents this transactional state.

    The transactional state of the :class:`_orm.Session` may also be started explicitly, by invoking the :meth:`_orm.Session.begin` method.   When this method is called, the :class:`_orm.Session` is placed into the "transactional" state unconditionally.   :meth:`_orm.Session.begin` may be used as a context manager as described at :ref:`session_begin_commit_rollback_block`.

.. _session_autobegin_disable:

禁用自动开始以防止隐式事务
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Disabling Autobegin to Prevent Implicit Transactions

.. tab:: 中文

    可以通过将参数 :paramref:`_orm.Session.autobegin` 设置为 ``False`` 来禁用 "autobegin" 行为。设置此参数后，:class:`_orm.Session` 将要求用户显式调用 :meth:`_orm.Session.begin` 方法以启动事务。在创建会话对象之后，或调用了 :meth:`_orm.Session.rollback`、:meth:`_orm.Session.commit` 或 :meth:`_orm.Session.close` 方法之后，该 :class:`_orm.Session` 将不会自动开启新事务，如果之后尝试使用该对象而未显式调用 :meth:`_orm.Session.begin`，将会抛出错误::

        with Session(engine, autobegin=False) as session:
            session.begin()  # <-- 必须调用，否则下次操作将抛出 InvalidRequestError

            session.add(User(name="u1"))
            session.commit()

            session.begin()  # <-- 必须调用，否则下次操作将抛出 InvalidRequestError

            u1 = session.scalar(select(User).filter_by(name="u1"))

    .. versionadded:: 2.0

        新增 :paramref:`_orm.Session.autobegin` 参数，允许禁用 "autobegin" 行为

.. tab:: 英文

    The "autobegin" behavior may be disabled using the :paramref:`_orm.Session.autobegin` parameter set to ``False``. By using this parameter, a :class:`_orm.Session` will require that the :meth:`_orm.Session.begin` method is called explicitly. Upon construction, as well as after any of the :meth:`_orm.Session.rollback`, :meth:`_orm.Session.commit`, or :meth:`_orm.Session.close` methods are called, the :class:`_orm.Session` won't implicitly begin any new transactions and will raise an error if an attempt to use the :class:`_orm.Session` is made without first calling :meth:`_orm.Session.begin`::

        with Session(engine, autobegin=False) as session:
            session.begin()  # <-- required, else InvalidRequestError raised on next call

            session.add(User(name="u1"))
            session.commit()

            session.begin()  # <-- required, else InvalidRequestError raised on next call

            u1 = session.scalar(select(User).filter_by(name="u1"))

    .. versionadded:: 2.0 
      
        Added :paramref:`_orm.Session.autobegin`, allowing "autobegin" behavior to be disabled

.. _session_committing:

提交
~~~~~~~~~~

Committing

.. tab:: 中文

    :meth:`~.Session.commit` 用于提交当前事务。其核心行为是在所有当前处于事务状态的数据库连接上发出 ``COMMIT`` 命令；从 :term:`DBAPI` 的角度来看，这意味着在每个 DBAPI 连接上调用 ``connection.commit()`` 方法。

    如果 :class:`.Session` 当前没有处于事务状态（表示自上次调用 :meth:`.Session.commit` 后未执行任何操作），该方法将启动并提交一个仅限内部使用的“逻辑事务”。此事务通常不会对数据库产生实际影响，除非检测到有待刷新的变更，但仍会触发事件处理器与对象过期机制。

    :meth:`_orm.Session.commit` 操作会在对相关数据库连接发出 COMMIT 前 **无条件** 调用 :meth:`~.Session.flush` 方法。如果没有检测到待处理的变更，则不会向数据库发送任何 SQL。这一行为不可配置，也不会受到 :paramref:`.Session.autoflush` 参数的影响。

    随后，假设 :class:`_orm.Session` 绑定到了某个 :class:`_engine.Engine`，则 :meth:`_orm.Session.commit` 会对已开始的实际数据库事务执行 COMMIT。提交完成后，与该事务关联的 :class:`_engine.Connection` 对象会被关闭，其底层的 DBAPI 连接也会被 :term:`释放` 回连接池，该连接池隶属于绑定的 :class:`_engine.Engine`。

    对于绑定到多个引擎的 :class:`_orm.Session`（例如见 :ref:`分区策略 <session_partitioning>`），提交的逻辑事务中每个涉及的 :class:`_engine.Engine` / :class:`_engine.Connection` 都将进行上述相同的 COMMIT 操作。除非启用了 :ref:`两阶段提交 <session_twophase>`，否则这些数据库事务之间是 **不协调** 的。

    也可以将 :class:`_orm.Session` 绑定到某个 :class:`_engine.Connection` 上来使用其他的连接交互模式；在这种模式下，假定存在一个 **外部管理的事务**，此时将不会自动执行 COMMIT。详见 :ref:`session_external_transaction` 章节了解此模式的背景。

    最后，在事务结束后，:class:`_orm.Session` 中的所有对象都将被 :term:`过期`。这样可以确保当这些实例再次被访问（无论是通过属性访问还是出现在 SELECT 查询结果中）时，它们将获得最新状态。此行为可通过 :paramref:`_orm.Session.expire_on_commit` 标志进行控制；若该行为不希望发生，可将其设置为 ``False``。

    .. seealso::

      :ref:`session_autobegin`

---

如果你还需要我继续翻译其他部分，或者想要对这段内容进行更深入的解释，也可以随时告诉我！

.. tab:: 英文

    :meth:`~.Session.commit` is used to commit the current transaction.   At its core this indicates that it emits ``COMMIT`` on all current database connections that have a transaction in progress; from a :term:`DBAPI` perspective this means the ``connection.commit()`` DBAPI method is invoked on each DBAPI connection.

    When there is no transaction in place for the :class:`.Session`, indicating that no operations were invoked on this :class:`.Session` since the previous call to :meth:`.Session.commit`, the method will begin and commit an internal-only "logical" transaction, that does not normally affect the database unless pending flush changes were detected, but will still invoke event handlers and object expiration rules.

    The :meth:`_orm.Session.commit` operation unconditionally issues :meth:`~.Session.flush` before emitting COMMIT on relevant database connections. If no pending changes are detected, then no SQL is emitted to the database. This behavior is not configurable and is not affected by the :paramref:`.Session.autoflush` parameter.

    Subsequent to that, assuming the :class:`_orm.Session` is bound to an :class:`_engine.Engine`, :meth:`_orm.Session.commit` will then COMMIT the actual database transaction that is in place, if one was started.   After the commit, the :class:`_engine.Connection` object associated with that transaction is closed, causing its underlying DBAPI connection to be :term:`released` back to the connection pool associated with the :class:`_engine.Engine` to which the :class:`_orm.Session` is bound.

    For a :class:`_orm.Session` that's bound to multiple engines (e.g. as described at :ref:`Partitioning Strategies <session_partitioning>`), the same COMMIT steps will proceed for each :class:`_engine.Engine` / :class:`_engine.Connection` that is in play within the "logical" transaction being committed.  These database transactions are uncoordinated with each other unless :ref:`two-phase features <session_twophase>` are enabled.

    Other connection-interaction patterns are available as well, by binding the :class:`_orm.Session` to a :class:`_engine.Connection` directly; in this case, it's assumed that an externally-managed transaction is present, and a real COMMIT will not be emitted automatically in this case; see the section :ref:`session_external_transaction` for background on this pattern.

    Finally, all objects within the :class:`_orm.Session` are :term:`expired` as the transaction is closed out. This is so that when the instances are next accessed, either through attribute access or by them being present in the result of a SELECT, they receive the most recent state. This behavior may be controlled by the :paramref:`_orm.Session.expire_on_commit` flag, which may be set to ``False`` when this behavior is undesirable.

    .. seealso::

        :ref:`session_autobegin`

.. _session_rollback:

回滚
~~~~~~~~~~~~

Rolling Back

.. tab:: 中文

    :meth:`~.Session.rollback` 方法用于回滚当前事务（若存在）。若当前没有事务，该方法将 **静默通过**，不会引发异常。

    在默认配置的会话中，若事务是通过 :ref:`自动开始 <session_autobegin>` 或显式调用 :meth:`_orm.Session.begin` 方法开启的，在回滚之后会处于如下状态：

    * 数据库事务会被回滚。对于绑定到单个 :class:`_engine.Engine` 的 :class:`_orm.Session`，这意味着最多只会对一个 :class:`_engine.Connection` 发出 ROLLBACK。若绑定到多个 :class:`_engine.Engine`，则所有被检出的 :class:`_engine.Connection` 都会进行 ROLLBACK。
    * 数据库连接被 :term:`释放`。其行为与 :ref:`session_committing` 中描述的连接释放机制一致：从 :class:`_engine.Engine` 获取的 :class:`_engine.Connection` 被关闭，从而将底层 DBAPI 连接释放回该引擎的连接池。若之后开始新的事务，将重新从引擎中检出连接。
    * 若会话绑定的是一个 :class:`_engine.Connection`（参见 :ref:`session_external_transaction`），其回滚行为将根据 :paramref:`_orm.Session.join_transaction_mode` 参数决定，可能涉及回滚保存点（savepoints）或发出实际的 ROLLBACK。
    * 所有在事务期间处于 :term:`pending` 状态（即刚添加到会话中的）对象将被驱逐（expunged），对应的 INSERT 操作也被回滚，但其属性状态仍然保留。
    * 所有在事务期间被标记为 :term:`deleted` 的对象将被提升回 :term:`persistent` 状态，表示其 DELETE 操作被回滚。注意，如果该对象最初在事务中是 :term:`pending` 状态，那么“pending”操作优先生效。
    * 所有未被驱逐的对象都将被完全过期——这一点 **不受** :paramref:`_orm.Session.expire_on_commit` 设置的影响。

    理解上述状态后，:class:`_orm.Session` 可在回滚后安全地继续使用。

    .. versionchanged:: 1.4

        :class:`_orm.Session` 现在具有延迟“开始事务”的行为，详见 :ref:`自动开始 <session_autobegin>`。如果事务未开始，则调用 :meth:`_orm.Session.commit` 和 :meth:`_orm.Session.rollback` 不会有任何效果。在 1.4 之前版本中，由于非自动提交（autocommit）模式下总是隐式存在事务，因此不会出现该行为。

    当 :meth:`_orm.Session.flush` 失败（通常因为主键、外键或“非空”约束违反等原因）时，会自动执行 ROLLBACK（目前 flush 无法在部分失败后继续执行）。但此时 :class:`_orm.Session` 会进入一种称为“非活动”（inactive）的状态，此时调用方必须 **显式调用** :meth:`_orm.Session.rollback` 方法，使会话恢复为可用状态（也可以直接关闭并丢弃该会话）。详见 FAQ 条目 :ref:`faq_session_rollback` 获取更多说明。

    .. seealso::

      :ref:`session_autobegin`

.. tab:: 英文

    :meth:`~.Session.rollback` rolls back the current transaction, if any. When there is no transaction in place, the method passes silently.

    With a default configured session, the post-rollback state of the session, subsequent to a transaction having been begun either via :ref:`autobegin <session_autobegin>` or by calling the :meth:`_orm.Session.begin` method explicitly, is as follows:

      * Database transactions are rolled back.  For a :class:`_orm.Session` bound to a single :class:`_engine.Engine`, this means ROLLBACK is emitted for at most a single :class:`_engine.Connection` that's currently in use. For :class:`_orm.Session` objects bound to multiple :class:`_engine.Engine` objects, ROLLBACK is emitted for all :class:`_engine.Connection` objects that were checked out.
      * Database connections are :term:`released`.  This follows the same connection-related behavior noted in :ref:`session_committing`, where :class:`_engine.Connection` objects obtained from :class:`_engine.Engine` objects are closed, causing the DBAPI connections to be :term:`released` to the connection pool within the :class:`_engine.Engine`.   New connections are checked out from the :class:`_engine.Engine` if and when a new transaction begins.
      * For a :class:`_orm.Session` that's bound directly to a :class:`_engine.Connection` as described at :ref:`session_external_transaction`, rollback behavior on this :class:`_engine.Connection` would follow the behavior specified by the :paramref:`_orm.Session.join_transaction_mode` parameter, which could involve rolling back savepoints or emitting a real ROLLBACK.
      * Objects which were initially in the :term:`pending` state when they were added to the :class:`~sqlalchemy.orm.session.Session` within the lifespan of the transaction are expunged, corresponding to their INSERT statement being rolled back. The state of their attributes remains unchanged.
      * Objects which were marked as :term:`deleted` within the lifespan of the transaction are promoted back to the :term:`persistent` state, corresponding to their DELETE statement being rolled back. Note that if those objects were first :term:`pending` within the transaction, that operation takes precedence instead.
      * All objects not expunged are fully expired - this is regardless of the :paramref:`_orm.Session.expire_on_commit` setting.

    With that state understood, the :class:`_orm.Session` may safely continue usage after a rollback occurs.

    .. versionchanged:: 1.4

        The :class:`_orm.Session` object now features deferred "begin" behavior, as described in :ref:`autobegin <session_autobegin>`. If no transaction is begun, methods like :meth:`_orm.Session.commit` and :meth:`_orm.Session.rollback` have no effect.  This behavior would not have been observed prior to 1.4 as under non-autocommit mode, a transaction would always be implicitly present.

    When a :meth:`_orm.Session.flush` fails, typically for reasons like primary key, foreign key, or "not nullable" constraint violations, a ROLLBACK is issued automatically (it's currently not possible for a flush to continue after a partial failure). However, the :class:`_orm.Session` goes into a state known as "inactive" at this point, and the calling application must always call the :meth:`_orm.Session.rollback` method explicitly so that the :class:`_orm.Session` can go back into a usable state (it can also be simply closed and discarded). See the FAQ entry at :ref:`faq_session_rollback` for further discussion.

    .. seealso::

      :ref:`session_autobegin`

.. _session_closing:

关闭
~~~~~~~

Closing

.. tab:: 中文

    :meth:`~.Session.close` 方法会调用 :meth:`~.Session.expunge_all`，将所有 ORM 映射的对象从会话中移除，并且 :term:`释放` 所绑定的 :class:`_engine.Engine` 对象上的事务/连接资源。当连接被返回到连接池时，其事务状态也将被回滚。

    默认情况下，当 :class:`_orm.Session` 被关闭时，其状态与刚创建时本质上相同，并且 **可以再次使用** 。从这个意义上说，:meth:`_orm.Session.close` 更像是一次“重置”（reset）操作，而不是传统意义上的“关闭数据库连接”操作。在这种使用模式下，方法 :meth:`_orm.Session.reset` 实际上是 :meth:`_orm.Session.close` 的别名，行为完全一致。

    :meth:`_orm.Session.close` 的默认行为可以通过将参数 :paramref:`_orm.Session.close_resets_only` 设置为 ``False`` 来更改，表示在调用 :meth:`_orm.Session.close` 之后，该 :class:`_orm.Session` 不能再被重复使用。在此模式下，:meth:`_orm.Session.reset` 方法则可用于多次“重置”会话，其行为类似于在 :paramref:`_orm.Session.close_resets_only` 设置为 ``True`` 时的 :meth:`_orm.Session.close`。

    .. versionadded:: 2.0.22

    推荐在使用 :class:`_orm.Session` 后总是调用 :meth:`_orm.Session.close` 限定其作用范围，尤其是在未使用 :meth:`_orm.Session.commit` 或 :meth:`_orm.Session.rollback` 的情况下。可以通过上下文管理器使用 :class:`_orm.Session` 来确保会自动调用 :meth:`_orm.Session.close` 方法，例如::

        with Session(engine) as session:
            result = session.execute(select(User))

        # 会话在此自动关闭

    .. versionchanged:: 1.4

        :class:`_orm.Session` 对象现在采用延迟“开始事务”机制，详见 :ref:`自动开始 <session_autobegin>`。调用 :meth:`_orm.Session.close` 后不再立即开启新的事务。

.. tab:: 英文

    The :meth:`~.Session.close` method issues a :meth:`~.Session.expunge_all` which removes all ORM-mapped objects from the session, and :term:`releases` any transactional/connection resources from the :class:`_engine.Engine` object(s) to which it is bound.   When connections are returned to the connection pool, transactional state is rolled back as well.

    By default, when the :class:`_orm.Session` is closed, it is essentially in the original state as when it was first constructed, and **may be used again**. In this sense, the :meth:`_orm.Session.close` method is more like a "reset" back to the clean state and not as much like a "database close" method. In this mode of operation the method :meth:`_orm.Session.reset` is an alias to :meth:`_orm.Session.close` and behaves in the same way.

    The default behavior of :meth:`_orm.Session.close` can be changed by setting the parameter :paramref:`_orm.Session.close_resets_only` to ``False``, indicating that the :class:`_orm.Session` cannot be reused after the method :meth:`_orm.Session.close` has been called. In this mode of operation the :meth:`_orm.Session.reset` method will allow multiple "reset" of the session, behaving like :meth:`_orm.Session.close` when :paramref:`_orm.Session.close_resets_only` is set to ``True``.

    .. versionadded:: 2.0.22

    It's recommended that the scope of a :class:`_orm.Session` be limited by a call to :meth:`_orm.Session.close` at the end, especially if the :meth:`_orm.Session.commit` or :meth:`_orm.Session.rollback` methods are not used.    The :class:`_orm.Session` may be used as a context manager to ensure that :meth:`_orm.Session.close` is called::

        with Session(engine) as session:
            result = session.execute(select(User))

        # closes session automatically

    .. versionchanged:: 1.4

        The :class:`_orm.Session` object features deferred "begin" behavior, as described in :ref:`autobegin <session_autobegin>`. no longer immediately begins a new transaction after the :meth:`_orm.Session.close` method is called.

.. _session_faq:

会话常见问题
----------------------------------

Session Frequently Asked Questions

.. tab:: 中文

    此时，大多数用户通常已经对会话对象有了一些疑问。以下是一个简要的“迷你 FAQ”部分（请注意，我们也有一个更完整的 :doc:`常见问题解答 </faq/index>`），列出了使用 :class:`.Session` 时最常见的问题。

.. tab:: 英文

    By this point, many users already have questions about sessions. This section presents a mini-FAQ (note that we have also a :doc:`real FAQ </faq/index>`) of the most basic issues one is presented with when using a :class:`.Session`.

我什么时候创建 :class:`.sessionmaker`？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When do I make a :class:`.sessionmaker`?

.. tab:: 中文

    **Q：我应该在哪里创建 sessionmaker？**

    A：只需在你的应用程序的全局作用域中创建一次即可。你可以把它看作应用程序配置的一部分。例如，如果你的应用有三个 `.py` 文件组成的包，你可以把 :class:`.sessionmaker` 放在 ``__init__.py`` 文件中。这样其他模块只需执行 `from mypackage import Session`。其他人就只需使用 :class:`.Session()`，其配置由那个中心点控制。

    **Q：如果我在应用启动时还不知道将连接到哪个数据库怎么办？**

    A：你可以稍后在“类级别”通过 :meth:`.sessionmaker.configure` 将引擎绑定到 :class:`.Session`。

    在本节的示例中，我们经常会在调用 :class:`.Session` 的代码上方直接创建 :class:`.sessionmaker` ，但这仅是为了简化示例！在实际应用中，:class:`.sessionmaker` 通常会定义在模块级别，而实际实例化 :class:`.Session` 的调用则应放在开始数据库操作的地方。

.. tab:: 英文

    Just one time, somewhere in your application's global scope. It should be looked upon as part of your application's configuration. If your application has three .py files in a package, you could, for example, place the :class:`.sessionmaker` line in your ``__init__.py`` file; from that point on your other modules say "from mypackage import Session". That way, everyone else just uses :class:`.Session()`, and the configuration of that session is controlled by that central point.

    If your application starts up, does imports, but does not know what database it's going to be connecting to, you can bind the :class:`.Session` at the "class" level to the engine later on, using :meth:`.sessionmaker.configure`.

    In the examples in this section, we will frequently show the :class:`.sessionmaker` being created right above the line where we actually invoke :class:`.Session`. But that's just for example's sake!  In reality, the :class:`.sessionmaker` would be somewhere at the module level.   The calls to instantiate :class:`.Session` would then be placed at the point in the application where database conversations begin.

.. _session_faq_whentocreate:

我什么时候构造 :class:`.Session`，什么时候提交它，什么时候关闭它？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When do I construct a :class:`.Session`, when do I commit it, and when do I close it?

.. tab:: 中文

    .. topic:: 简明总结

        1. 通常建议将会话的生命周期与访问和/或操作数据库数据的函数和对象 **分离**，且 **放在外部控制**。这将极大地帮助你实现可预测且一致的事务范围（transactional scope）。

        2. 明确事务何时开始与结束，并确保事务保持 **简短**。也就是说，事务应在一组操作完成后结束，而不是无限期地保持开启状态。

    :class:`.Session` 通常在一个逻辑操作开始时构建，此时可能会涉及数据库访问。

    每当 :class:`.Session` 与数据库进行交互时，它会立即开启一个数据库事务。该事务会持续进行，直到显式调用 :class:`.Session` 的 rollback、commit 或 close 方法。当上一个事务结束后，如果再次使用该会话，则会开启一个新的事务。因此，:class:`.Session` 支持跨多个事务存在（但同一时间仅有一个事务处于活动状态）。我们将这两个概念称为 **事务范围（transaction scope）** 与 **会话范围（session scope）**。

    尽管应用架构可能千差万别，但确定 :class:`.Session` 开始与结束的范围通常并不困难。

    以下是一些常见示例场景：

    * **Web 应用**：此类应用通常使用 Web 框架所提供的 SQLAlchemy 集成功能。基本模式是：在请求开始时创建 :class:`_orm.Session`，在处理 POST、PUT 或 DELETE 请求后调用 :meth:`_orm.Session.commit`，最后在请求结束时关闭会话。建议将 :paramref:`_orm.Session.expire_on_commit` 设置为 `False`，以便在事务提交后访问对象时不再触发新的 SQL 查询。

    * **后台守护进程**：如果后台服务会生成子进程（fork），应在每个子进程中本地创建一个 :class:`.Session`，在该子进程所处理的“任务”生命周期中使用该会话，并在任务完成后销毁它。

    * **命令行脚本**：在此场景下，应用程序会在程序开始执行任务时创建一个全局 :class:`.Session`，并在任务完成时进行提交。

    * **GUI 驱动应用**：对于图形界面驱动的程序，会话的作用范围可能对应一个用户触发的事件（如点击按钮），也可能对应用户操作的一个周期（如用户“打开”一批记录并“保存”它们）。

    总的原则是， **应用应在函数之外管理会话的生命周期**。这是关注点分离（separation of concerns）的关键做法，确保数据操作逻辑不依赖于会话的上下文。

    例如， **不要这样做**::

        ### 这是错误的做法 ###

        class ThingOne:
            def go(self):
                session = Session()
                try:
                    session.execute(update(FooBar).values(x=5))
                    session.commit()
                except:
                    session.rollback()
                    raise

        class ThingTwo:
            def go(self):
                session = Session()
                try:
                    session.execute(update(Widget).values(q=18))
                    session.commit()
                except:
                    session.rollback()
                    raise

        def run_my_program():
            ThingOne().go()
            ThingTwo().go()

    相反，应该 **将会话（通常也包括事务）生命周期放在外部控制**。下面是一个改进后的示例，并使用 Python 上下文管理器（ ``with:`` 语法）来自动管理 :class:`_orm.Session` 与其事务的作用范围::

        ### 这是更好的做法（但不是唯一的方式）###

        class ThingOne:
            def go(self, session):
                session.execute(update(FooBar).values(x=5))

        class ThingTwo:
            def go(self, session):
                session.execute(update(Widget).values(q=18))

        def run_my_program():
            with Session() as session:
                with session.begin():
                    ThingOne().go(session)
                    ThingTwo().go(session)

    .. versionchanged:: 1.4

        :class:`_orm.Session` 现在可以作为上下文管理器使用，而无需外部辅助函数。

.. tab:: 英文

    .. topic:: tl;dr;

        1. As a general rule, keep the lifecycle of the session **separate and external** from functions and objects that access and/or manipulate database data.  This will greatly help with achieving a predictable and consistent transactional scope.

        2. Make sure you have a clear notion of where transactions begin and end, and keep transactions **short**, meaning, they end at the series of a sequence of operations, instead of being held open indefinitely.

    A :class:`.Session` is typically constructed at the beginning of a logical operation where database access is potentially anticipated.

    The :class:`.Session`, whenever it is used to talk to the database, begins a database transaction as soon as it starts communicating. This transaction remains in progress until the :class:`.Session` is rolled back, committed, or closed.   The :class:`.Session` will begin a new transaction if it is used again, subsequent to the previous transaction ending; from this it follows that the :class:`.Session` is capable of having a lifespan across many transactions, though only one at a time.   We refer to these two concepts as **transaction scope** and **session scope**.

    It's usually not very hard to determine the best points at which to begin and end the scope of a :class:`.Session`, though the wide variety of application architectures possible can introduce challenging situations.

    Some sample scenarios include:

    * Web applications.  In this case, it's best to make use of the SQLAlchemy integrations provided by the web framework in use.  Or otherwise, the basic pattern is create a :class:`_orm.Session` at the start of a web request, call the :meth:`_orm.Session.commit` method at the end of web requests that do POST, PUT, or DELETE, and then close the session at the end of web request.  It's also usually a good idea to set :paramref:`_orm.Session.expire_on_commit` to False so that subsequent access to objects that came from a :class:`_orm.Session` within the view layer do not need to emit new SQL queries to refresh the objects, if the transaction has been committed already.

    * A background daemon which spawns off child forks would want to create a :class:`.Session` local to each child process, work with that :class:`.Session` through the life of the "job" that the fork is handling, then tear it down when the job is completed.

    * For a command-line script, the application would create a single, global :class:`.Session` that is established when the program begins to do its work, and commits it right as the program is completing its task.

    * For a GUI interface-driven application, the scope of the :class:`.Session` may best be within the scope of a user-generated event, such as a button push.  Or, the scope may correspond to explicit user interaction, such as the user "opening" a series of records, then "saving" them.

    As a general rule, the application should manage the lifecycle of the session *externally* to functions that deal with specific data.  This is a fundamental separation of concerns which keeps data-specific operations agnostic of the context in which they access and manipulate that data.

    E.g. **don't do this**::

        ### this is the **wrong way to do it** ###


        class ThingOne:
            def go(self):
                session = Session()
                try:
                    session.execute(update(FooBar).values(x=5))
                    session.commit()
                except:
                    session.rollback()
                    raise


        class ThingTwo:
            def go(self):
                session = Session()
                try:
                    session.execute(update(Widget).values(q=18))
                    session.commit()
                except:
                    session.rollback()
                    raise


        def run_my_program():
            ThingOne().go()
            ThingTwo().go()

    Keep the lifecycle of the session (and usually the transaction) **separate and external**.  The example below illustrates how this might look, and additionally makes use of a Python context manager (i.e. the ``with:`` keyword) in order to manage the scope of the :class:`_orm.Session` and its transaction automatically::

        ### this is a **better** (but not the only) way to do it ###


        class ThingOne:
            def go(self, session):
                session.execute(update(FooBar).values(x=5))


        class ThingTwo:
            def go(self, session):
                session.execute(update(Widget).values(q=18))


        def run_my_program():
            with Session() as session:
                with session.begin():
                    ThingOne().go(session)
                    ThingTwo().go(session)

    .. versionchanged:: 1.4 
      
        The :class:`_orm.Session` may be used as a context manager without the use of external helper functions.

会话是缓存吗？
~~~~~~~~~~~~~~~~~~~~~~~

Is the Session a cache?

.. tab:: 中文

    呃……不完全是。虽然会话（Session） **在某种程度上** 可以被看作是一个缓存，因为它实现了 :term:`identity map` 模式，并以主键为键存储对象，但它 **并不会进行任何形式的查询缓存** 。

    这意味着，即便你执行 `session.scalars(select(Foo).filter_by(name='bar'))` 时，内存中确实已经有一个 `Foo(name='bar')` 的对象存在于 identity map 中，会话对象对此也一无所知。它仍然会向数据库发出 SQL 查询，获取数据行，然后当它识别出行中的主键时， **这时** 它才会去 identity map 中查找是否已有对应对象。如果存在，就重用它。

    只有当你执行 `query.get({some primary key})` 时，:class:`~sqlalchemy.orm.session.Session` 才不会向数据库发起查询请求。

    此外，会话默认使用 **弱引用（weak reference）** 来存储对象实例。这也进一步限制了将会话作为缓存使用的可行性。

    :class:`.Session` 并 **不是设计为全局对象** ，不能作为全局“注册表”被所有地方查阅使用。真正适合做这件事的是所谓的 **二级缓存（second level cache）** 。

    SQLAlchemy 提供了一种基于 [`dogpile.cache`](https://dogpilecache.readthedocs.io/) 的二级缓存实现模式，可参考文档中的 :ref:`examples_caching` 示例。

.. tab:: 英文

    Yeee...no. It's somewhat used as a cache, in that it implements the :term:`identity map` pattern, and stores objects keyed to their primary key. However, it doesn't do any kind of query caching. This means, if you say ``session.scalars(select(Foo).filter_by(name='bar'))``, even if ``Foo(name='bar')`` is right there, in the identity map, the session has no idea about that. It has to issue SQL to the database, get the rows back, and then when it sees the primary key in the row, *then* it can look in the local identity map and see that the object is already there. It's only when you say ``query.get({some primary key})`` that the :class:`~sqlalchemy.orm.session.Session` doesn't have to issue a query.

    Additionally, the Session stores object instances using a weak reference by default. This also defeats the purpose of using the Session as a cache.

    The :class:`.Session` is not designed to be a global object from which everyone consults as a "registry" of objects. That's more the job of a **second level cache**.   SQLAlchemy provides a pattern for implementing second level caching using `dogpile.cache <https://dogpilecache.readthedocs.io/>`_, via the :ref:`examples_caching` example.

如何获取某个对象的 :class:`~sqlalchemy.orm.session.Session`？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

How can I get the :class:`~sqlalchemy.orm.session.Session` for a certain object?

.. tab:: 中文

    你可以使用 :meth:`~.Session.object_session` 类方法来获取某个对象所属的会话实例::

        session = Session.object_session(someobject)

    也可以使用较新的 :ref:`core_inspection_toplevel` 检查系统::

        from sqlalchemy import inspect

        session = inspect(someobject).session

.. tab:: 英文

    Use the :meth:`~.Session.object_session` classmethod available on :class:`~sqlalchemy.orm.session.Session`::

        session = Session.object_session(someobject)

    The newer :ref:`core_inspection_toplevel` system can also be used::

        from sqlalchemy import inspect

        session = inspect(someobject).session

.. _session_faq_threadsafe:

会话是线程安全的吗？AsyncSession 在并发任务中共享是否安全？
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Is the Session thread-safe?  Is AsyncSession safe to share in concurrent tasks?

.. tab:: 中文

    :class:`.Session` 是一个 **可变的、有状态的** 对象，表示 **单个数据库事务**。因此，:class:`.Session` 的实例 **不能在并发的线程或 asyncio 任务之间共享，除非进行仔细的同步**。:class:`.Session` 设计为 **非并发** 使用，也就是说，一个特定的 :class:`.Session` 实例应该仅在一个线程或任务中使用一次。

    当使用 SQLAlchemy 的 :ref:`asyncio <asyncio_toplevel>` 扩展中的 :class:`_asyncio.AsyncSession` 对象时，该对象仅是 :class:`_orm.Session` 上的一个薄代理，并且适用相同的规则；它是一个 **无同步的、可变的、有状态的对象**，因此 **不能** 在多个 asyncio 任务中同时使用同一个 :class:`_asyncio.AsyncSession` 实例。

    :class:`.Session` 或 :class:`_asyncio.AsyncSession` 的实例表示单个逻辑数据库事务，只引用绑定到该对象的特定 :class:`_engine.Connection`（注意：这些对象都支持同时绑定多个引擎，但在事务范围内，每个引擎只有一个连接在起作用）。

    在事务中的数据库连接也是一个有状态的对象，设计上用于按顺序、非并发地操作。命令会按顺序在连接上发出，由数据库服务器按发出的顺序处理这些命令。随着 :class:`_orm.Session` 在该连接上发出命令并接收结果，:class:`_orm.Session` 本身经历了与该连接上的命令和数据状态一致的内部状态变化；这些状态包括事务是否已开始、已提交或已回滚，是否有 SAVEPOINT（保存点）等，以及数据库行与本地 ORM 映射对象之间的状态同步。

    在设计数据库并发应用程序时，适当的模型是每个并发任务或线程都使用自己的数据库事务。这就是为什么在讨论数据库并发时，标准术语通常是 **多个并发事务**。在传统的关系型数据库管理系统（RDBMS）中，没有一个类比可以对应一个正在接收和处理多个命令的单个数据库事务。

    因此，SQLAlchemy 的 :class:`_orm.Session` 和 :class:`_asyncio.AsyncSession` 的并发模型是 **每个线程一个 Session，每个任务一个 AsyncSession**。如果应用程序使用多个线程，或者在 asyncio 中使用多个任务（例如通过 ``asyncio.gather()``），就需要确保每个线程有自己的 :class:`_orm.Session`，每个 asyncio 任务有自己的 :class:`_asyncio.AsyncSession`。

    为了确保这种使用，最好的方式是在线程或任务的顶级 Python 函数内使用 :ref:`标准上下文管理器模式 <session_getting>`，这将确保 :class:`_orm.Session` 或 :class:`_asyncio.AsyncSession` 的生命周期保持在本地作用域内。

    对于需要一个“全局” :class:`.Session` 的应用程序，如果不能将 :class:`.Session` 对象传递给需要它的特定函数和方法，可以使用 :class:`.scoped_session` 方式提供一个“线程本地”的 :class:`.Session` 对象；有关背景，请参见 :ref:`unitofwork_contextual`。在 asyncio 上下文中，:class:`.async_scoped_session` 对象是 :class:`.scoped_session` 的 asyncio 类比，但它配置起来更具挑战性，因为它需要一个自定义的“上下文”函数。

.. tab:: 英文

    The :class:`.Session` is a **mutable, stateful** object that represents a **single database transaction**.   An instance of :class:`.Session` therefore **cannot be shared among concurrent threads or asyncio tasks without careful synchronization**. The :class:`.Session` is intended to be used in a **non-concurrent** fashion, that is, a particular instance of :class:`.Session` should be used in only one thread or task at a time.

    When using the :class:`_asyncio.AsyncSession` object from SQLAlchemy's :ref:`asyncio <asyncio_toplevel>` extension, this object is only a thin proxy on top of a :class:`_orm.Session`, and the same rules apply; it is an **unsynchronized, mutable, stateful object**, so it is **not** safe to use a single instance of :class:`_asyncio.AsyncSession` in multiple asyncio tasks at once.

    An instance of :class:`.Session` or :class:`_asyncio.AsyncSession` represents a single logical database transaction, referencing only a single :class:`_engine.Connection` at a time for a particular :class:`.Engine` or :class:`.AsyncEngine` to which the object is bound (note that these objects both support being bound to multiple engines at once, however in this case there will still be only one connection per engine in play within the scope of a transaction).

    A database connection within a transaction is also a stateful object that is intended to be operated upon in a non-concurrent, sequential fashion. Commands are issued on the connection in a sequence, which are handled by the database server in the exact order in which they are emitted.   As the :class:`_orm.Session` emits commands upon this connection and receives results, the :class:`_orm.Session` itself is transitioning through internal state changes that align with the state of commands and data present on this connection; states which include if a transaction were begun, committed, or rolled back, what SAVEPOINTs if any are in play, as well as fine-grained synchronization of the state of individual database rows with local ORM-mapped objects.

    When designing database applications for concurrency, the appropriate model is that each concurrent task / thread works with its own database transaction. This is why when discussing the issue of database concurrency, the standard terminology used is **multiple, concurrent transactions**.   Within traditional RDMS there is no analogue for a single database transaction that is receiving and processing multiple commands concurrently.

    The concurrency model for SQLAlchemy's :class:`_orm.Session` and :class:`_asyncio.AsyncSession` is therefore **Session per thread, AsyncSession per task**.  An application that uses multiple threads, or multiple tasks in asyncio such as when using an API like ``asyncio.gather()`` would want to ensure that each thread has its own :class:`_orm.Session`, each asyncio task has its own :class:`_asyncio.AsyncSession`.

    The best way to ensure this use is by using the :ref:`standard context manager pattern <session_getting>`  locally within the top level Python function that is inside the thread or task, which will ensure the lifespan of the :class:`_orm.Session` or :class:`_asyncio.AsyncSession` is maintained within a local scope.

    For applications that benefit from having a "global" :class:`.Session` where it's not an option to pass the :class:`.Session` object to specific functions and methods which require it, the :class:`.scoped_session` approach can provide for a "thread local" :class:`.Session` object; see the section :ref:`unitofwork_contextual` for background.   Within the asyncio context, the :class:`.async_scoped_session` object is the asyncio analogue for :class:`.scoped_session`, however is more challenging to configure as it requires a custom "context" function.

