.. |prev| replace:: :doc:`data`
.. |next| replace:: :doc:`orm_related_objects`

.. include:: tutorial_nav_include.rst

.. rst-class:: orm-header

.. _tutorial_orm_data_manipulation:

使用 ORM 进行数据操作
==============================

Data Manipulation with the ORM

.. tab:: 中文

    上一节 :ref:`tutorial_working_with_data` 从核心视角继续关注 SQL 表达式语言，以提供跨主要 SQL 语句构造的连续性。本节将构建 :class:`_orm.Session` 的生命周期及其如何与这些构造交互。

    **前提章节** - 本教程的 ORM 重点部分建立在本文档的两个先前的 ORM 中心章节之上：

    * :ref:`tutorial_executing_orm_session` - 介绍如何创建一个 ORM :class:`_orm.Session` 对象

    * :ref:`tutorial_orm_table_metadata` - 在这里我们设置了 ``User`` 和 ``Address`` 实体的 ORM 映射

    * :ref:`tutorial_selecting_orm_entities` - 一些关于如何为 ``User`` 等实体运行 SELECT 语句的示例

.. tab:: 英文

    The previous section :ref:`tutorial_working_with_data` remained focused on
    the SQL Expression Language from a Core perspective, in order to provide
    continuity across the major SQL statement constructs.  This section will
    then build out the lifecycle of the :class:`_orm.Session` and how it interacts
    with these constructs.

    **Prerequisite Sections** - the ORM focused part of the tutorial builds upon
    two previous ORM-centric sections in this document:

    * :ref:`tutorial_executing_orm_session` - introduces how to make an ORM :class:`_orm.Session` object

    * :ref:`tutorial_orm_table_metadata` - where we set up our ORM mappings of the ``User`` and ``Address`` entities

    * :ref:`tutorial_selecting_orm_entities` - a few examples on how to run SELECT statements for entities like ``User``

.. _tutorial_inserting_orm:

使用 ORM 工作单元模式插入行
-------------------------------------------------

Inserting Rows using the ORM Unit of Work pattern

.. tab:: 中文

    使用 ORM 时，:class:`_orm.Session` 对象负责构造 :class:`_sql.Insert` 构造并在正在进行的事务中将其作为 INSERT 语句发出。我们指示 :class:`_orm.Session` 这样做的方法是 **添加** 对象条目到其中；然后 :class:`_orm.Session` 确保在需要时将这些新条目发出到数据库，使用一种称为 **flush** 的过程。:class:`_orm.Session` 用于持久化对象的整个过程称为 :term:`unit of work` 模式。

.. tab:: 英文

    When using the ORM, the :class:`_orm.Session` object is responsible for
    constructing :class:`_sql.Insert` constructs and emitting them as INSERT
    statements within the ongoing transaction. The way we instruct the
    :class:`_orm.Session` to do so is by **adding** object entries to it; the
    :class:`_orm.Session` then makes sure these new entries will be emitted to the
    database when they are needed, using a process known as a **flush**. The
    overall process used by the :class:`_orm.Session` to persist objects is known
    as the :term:`unit of work` pattern.

类的实例代表行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instances of Classes represent Rows

.. tab:: 中文

    在前面的示例中，我们使用 Python 字典来表示我们想要添加的数据，而在 ORM 中，我们直接使用我们在 :ref:`tutorial_orm_table_metadata` 中定义的自定义 Python 类。在类级别， ``User`` 和 ``Address`` 类作为定义相应数据库表外观的地方。这些类还充当可扩展的数据对象，我们在事务中使用它们来创建和操作行。下面我们将创建两个 ``User`` 对象，每个对象表示一个潜在的要插入的数据库行::

        >>> squidward = User(name="squidward", fullname="Squidward Tentacles")
        >>> krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

    我们可以使用映射列的名称作为构造函数中的关键字参数来构造这些对象。这是可能的，因为 ``User`` 类包含一个由 ORM 映射自动生成的 ``__init__()`` 构造函数，这样我们就可以使用列名作为构造函数中的键来创建每个对象。

    与我们在 :class:`_sql.Insert` 的核心示例中类似，我们没有包括主键（即 ``id`` 列的条目），因为我们希望使用数据库的自动递增主键功能，在这种情况下是 SQLite，ORM 也集成了这一功能。如果我们查看上面对象的 ``id`` 属性，其值显示为 ``None``::

        >>> squidward
        User(id=None, name='squidward', fullname='Squidward Tentacles')

    ``None`` 值由 SQLAlchemy 提供，以表明该属性尚无值。SQLAlchemy 映射的属性始终在 Python 中返回一个值，并且在缺少值时不会引发 ``AttributeError``，当处理尚未分配值的新对象时。

    目前，我们上面的两个对象处于一种称为 :term:`transient` 的状态 - 它们没有与任何数据库状态关联，并且尚未与可以为它们生成 INSERT 语句的 :class:`_orm.Session` 对象关联。

.. tab:: 英文

    Whereas in the previous example we emitted an INSERT using Python dictionaries
    to indicate the data we wanted to add, with the ORM we make direct use of the
    custom Python classes we defined, back at
    :ref:`tutorial_orm_table_metadata`.    At the class level, the ``User`` and
    ``Address`` classes served as a place to define what the corresponding
    database tables should look like.   These classes also serve as extensible
    data objects that we use to create and manipulate rows within a transaction
    as well.  Below we will create two ``User`` objects each representing a
    potential database row to be INSERTed::

        >>> squidward = User(name="squidward", fullname="Squidward Tentacles")
        >>> krabs = User(name="ehkrabs", fullname="Eugene H. Krabs")

    We are able to construct these objects using the names of the mapped columns as
    keyword arguments in the constructor.  This is possible as the ``User`` class
    includes an automatically generated ``__init__()`` constructor that was
    provided by the ORM mapping so that we could create each object using column
    names as keys in the constructor.

    In a similar manner as in our Core examples of :class:`_sql.Insert`, we did not
    include a primary key (i.e. an entry for the ``id`` column), since we would
    like to make use of the auto-incrementing primary key feature of the database,
    SQLite in this case, which the ORM also integrates with.
    The value of the ``id`` attribute on the above
    objects, if we were to view it, displays itself as ``None``::

        >>> squidward
        User(id=None, name='squidward', fullname='Squidward Tentacles')

    The ``None`` value is provided by SQLAlchemy to indicate that the attribute
    has no value as of yet.  SQLAlchemy-mapped attributes always return a value
    in Python and don't raise ``AttributeError`` if they're missing, when
    dealing with a new object that has not had a value assigned.

    At the moment, our two objects above are said to be in a state called
    :term:`transient` - they are not associated with any database state and are yet
    to be associated with a :class:`_orm.Session` object that can generate
    INSERT statements for them.

将对象添加到会话
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding objects to a Session

.. tab:: 中文

    为了逐步说明添加过程，我们将创建一个没有使用上下文管理器的 :class:`_orm.Session` （因此我们必须确保稍后关闭它！）::

        >>> session = Session(engine)

    然后使用 :meth:`_orm.Session.add` 方法将对象添加到 :class:`_orm.Session` 中。当调用此方法时，对象处于一种称为 :term:`pending` 的状态，尚未被插入::

        >>> session.add(squidward)
        >>> session.add(krabs)

    当我们有待处理对象时，可以通过查看 :class:`_orm.Session` 上的一个集合 :attr:`_orm.Session.new` 来看到这种状态::

        >>> session.new
        IdentitySet([User(id=None, name='squidward', fullname='Squidward Tentacles'), User(id=None, name='ehkrabs', fullname='Eugene H. Krabs')])

    上述视图使用了一个名为 :class:`.IdentitySet` 的集合，本质上是一个 Python 集合，在所有情况下都根据对象身份进行哈希（即，使用 Python 内置的 ``id()`` 函数，而不是 Python ``hash()`` 函数）。

.. tab:: 英文

    To illustrate the addition process step by step, we will create a
    :class:`_orm.Session` without using a context manager (and hence we must
    make sure we close it later!)::

        >>> session = Session(engine)

    The objects are then added to the :class:`_orm.Session` using the
    :meth:`_orm.Session.add` method.   When this is called, the objects are in a
    state known as :term:`pending` and have not been inserted yet::

        >>> session.add(squidward)
        >>> session.add(krabs)

    When we have pending objects, we can see this state by looking at a
    collection on the :class:`_orm.Session` called :attr:`_orm.Session.new`::

        >>> session.new
        IdentitySet([User(id=None, name='squidward', fullname='Squidward Tentacles'), User(id=None, name='ehkrabs', fullname='Eugene H. Krabs')])

    The above view is using a collection called :class:`.IdentitySet` that is
    essentially a Python set that hashes on object identity in all cases (i.e.,
    using Python built-in ``id()`` function, rather than the Python ``hash()`` function).

刷新
^^^^^^^^

Flushing

.. tab:: 中文

    :class:`_orm.Session` 使用一种称为 :term:`unit of work` 的模式。这通常意味着它一次积累一个更改，但实际上不会与数据库通信，直到需要时才进行。这使它能够根据一组待处理的更改，更好地决定如何在事务中发出 SQL DML。当它确实向数据库发出 SQL 以推送当前的一组更改时，该过程称为 **flush**。

    我们可以通过调用 :meth:`_orm.Session.flush` 方法手动演示 flush 过程：

    .. sourcecode:: pycon+sql

        >>> session.flush()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('squidward', 'Squidward Tentacles')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 2/2 (ordered; batch not supported)] ('ehkrabs', 'Eugene H. Krabs')

    上面我们观察到 :class:`_orm.Session` 首先被调用以发出 SQL，因此它创建了一个新事务并为这两个对象发出了适当的 INSERT 语句。事务现在 **保持打开(remains open)** 状态，直到我们调用 :class:`_orm.Session` 的 :meth:`_orm.Session.commit`、:meth:`_orm.Session.rollback` 或 :meth:`_orm.Session.close` 方法中的任何一个。

    虽然 :meth:`_orm.Session.flush` 可以用于手动推送当前事务的待处理更改，但通常不需要这样做，因为 :class:`_orm.Session` 具有称为 **autoflush** 的行为，我们将在后面演示。每当调用 :meth:`_orm.Session.commit` 时，它也会刷新更改。

.. tab:: 英文

    The :class:`_orm.Session` makes use of a pattern known as :term:`unit of work`.
    This generally means it accumulates changes one at a time, but does not actually
    communicate them to the database until needed.   This allows it to make
    better decisions about how SQL DML should be emitted in the transaction based
    on a given set of pending changes.   When it does emit SQL to the database
    to push out the current set of changes, the process is known as a **flush**.

    We can illustrate the flush process manually by calling the :meth:`_orm.Session.flush`
    method:

    .. sourcecode:: pycon+sql

        >>> session.flush()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('squidward', 'Squidward Tentacles')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 2/2 (ordered; batch not supported)] ('ehkrabs', 'Eugene H. Krabs')




    Above we observe the :class:`_orm.Session` was first called upon to emit SQL,
    so it created a new transaction and emitted the appropriate INSERT statements
    for the two objects.   The transaction now **remains open** until we call any
    of the :meth:`_orm.Session.commit`, :meth:`_orm.Session.rollback`, or
    :meth:`_orm.Session.close` methods of :class:`_orm.Session`.

    While :meth:`_orm.Session.flush` may be used to manually push out pending
    changes to the current transaction, it is usually unnecessary as the
    :class:`_orm.Session` features a behavior known as **autoflush**, which
    we will illustrate later.   It also flushes out changes whenever
    :meth:`_orm.Session.commit` is called.


自动生成的主键属性
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Autogenerated primary key attributes

.. tab:: 中文

    一旦插入行，我们创建的两个 Python 对象处于一种称为 :term:`persistent` 的状态，它们与添加或加载它们的 :class:`_orm.Session` 对象关联，并具有许多其他行为，这些将在后面介绍。

    发生的 INSERT 的另一个效果是，ORM 已检索每个新对象的新主键标识符；内部它通常使用我们之前介绍的 :attr:`_engine.CursorResult.inserted_primary_key` 访问器。``squidward`` 和 ``krabs`` 对象现在有了这些新的主键标识符，我们可以通过访问 ``id`` 属性查看它们::

        >>> squidward.id
        4
        >>> krabs.id
        5

    .. tip::  
        
        为什么 ORM 在可以使用 :ref:`executemany <tutorial_multiple_parameters>` 时发出了两个单独的 INSERT 语句？正如我们将在下一节中看到的，:class:`_orm.Session` 在刷新对象时总是需要知道新插入对象的主键。如果使用了 SQLite 的自动递增（其他示例包括 PostgreSQL IDENTITY 或 SERIAL，使用序列等），:attr:`_engine.CursorResult.inserted_primary_key` 功能通常要求每个 INSERT 一次发出一行。如果我们事先提供了主键的值，ORM 本来可以更好地优化操作。一些数据库后端（例如 :ref:`psycopg2 <postgresql_psycopg2>`）也可以一次插入多行，同时仍然能够检索主键值。

.. tab:: 英文

    Once the rows are inserted, the two Python objects we've created are in a
    state known as :term:`persistent`, where they are associated with the
    :class:`_orm.Session` object in which they were added or loaded, and feature lots of
    other behaviors that will be covered later.

    Another effect of the INSERT that occurred was that the ORM has retrieved the
    new primary key identifiers for each new object; internally it normally uses
    the same :attr:`_engine.CursorResult.inserted_primary_key` accessor we
    introduced previously.   The ``squidward`` and ``krabs`` objects now have these new
    primary key identifiers associated with them and we can view them by accessing
    the ``id`` attribute::

        >>> squidward.id
        4
        >>> krabs.id
        5

    .. tip::  
        
        Why did the ORM emit two separate INSERT statements when it could have
        used :ref:`executemany <tutorial_multiple_parameters>`?  As we'll see in the
        next section, the
        :class:`_orm.Session` when flushing objects always needs to know the
        primary key of newly inserted objects.  If a feature such as SQLite's autoincrement is used
        (other examples include PostgreSQL IDENTITY or SERIAL, using sequences,
        etc.), the :attr:`_engine.CursorResult.inserted_primary_key` feature
        usually requires that each INSERT is emitted one row at a time.  If we had provided values for the primary keys ahead of
        time, the ORM would have been able to optimize the operation better.  Some
        database backends such as :ref:`psycopg2 <postgresql_psycopg2>` can also
        INSERT many rows at once while still being able to retrieve the primary key
        values.

从身份映射中按主键获取对象
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Getting Objects by Primary Key from the Identity Map

.. tab:: 中文

    对象的主键标识对 :class:`_orm.Session` 很重要，因为这些对象现在使用称为 :term:`identity map` 的功能在内存中链接到此标识。身份映射是一个内存存储，将当前加载在内存中的所有对象链接到它们的主键标识。我们可以通过使用 :meth:`_orm.Session.get` 方法检索上述对象之一来观察这一点，该方法将返回身份映射中的条目（如果本地存在），否则发出 SELECT::

        >>> some_squidward = session.get(User, 4)
        >>> some_squidward
        User(id=4, name='squidward', fullname='Squidward Tentacles')

    关于身份映射的重要一点是，它在特定 :class:`_orm.Session` 对象的范围内，维护特定数据库标识的特定 Python 对象的 **唯一实例(unique instance)**。我们可以观察到 ``some_squidward`` 指的是之前的 ``squidward`` 的 **相同对象(same object)**::

        >>> some_squidward is squidward
        True

    身份映射是一项关键功能，它允许在事务中操作复杂的对象集，而不会出现不同步的情况。

.. tab:: 英文

    The primary key identity of the objects are significant to the :class:`_orm.Session`,
    as the objects are now linked to this identity in memory using a feature
    known as the :term:`identity map`.   The identity map is an in-memory store
    that links all objects currently loaded in memory to their primary key
    identity.   We can observe this by retrieving one of the above objects
    using the :meth:`_orm.Session.get` method, which will return an entry
    from the identity map if locally present, otherwise emitting a SELECT::

        >>> some_squidward = session.get(User, 4)
        >>> some_squidward
        User(id=4, name='squidward', fullname='Squidward Tentacles')

    The important thing to note about the identity map is that it maintains a
    **unique instance** of a particular Python object per a particular database
    identity, within the scope of a particular :class:`_orm.Session` object.  We
    may observe that the ``some_squidward`` refers to the **same object** as that
    of ``squidward`` previously::

        >>> some_squidward is squidward
        True

    The identity map is a critical feature that allows complex sets of objects
    to be manipulated within a transaction without things getting out of sync.


提交
^^^^^^^^^^^

Committing

.. tab:: 中文

    关于 :class:`_orm.Session` 的工作原理还有很多要说的内容，这将在后面进一步讨论。现在我们将提交事务，以便在检查更多 ORM 行为和功能之前，了解如何选择行：

    .. sourcecode:: pycon+sql

        >>> session.commit()
        COMMIT

    上述操作将提交正在进行的事务。我们处理的对象仍然 :term:`attached` 到 :class:`.Session`，这种状态将持续到 :class:`.Session` 关闭（介绍见 :ref:`tutorial_orm_closing`）。

    .. tip::

        需要注意的重要一点是，我们刚刚处理的对象上的属性已被 :term:`expired`，这意味着当我们下一次访问这些属性时，:class:`.Session` 将启动一个新事务并重新加载它们的状态。由于性能原因，这个选项有时会带来问题，或者如果在关闭 :class:`.Session` 后希望使用这些对象（称为 :term:`detached` 状态），因为它们将没有任何状态，并且没有 :class:`.Session` 来加载该状态，导致“分离实例”错误。此行为可以使用称为 :paramref:`.Session.expire_on_commit` 的参数进行控制。更多内容请参见 :ref:`tutorial_orm_closing`。

.. tab:: 英文

    There's much more to say about how the :class:`_orm.Session` works which will
    be discussed further.   For now we will commit the transaction so that
    we can build up knowledge on how to SELECT rows before examining more ORM
    behaviors and features:

    .. sourcecode:: pycon+sql

        >>> session.commit()
        COMMIT

    The above operation will commit the transaction that was in progress.  The
    objects which we've dealt with are still :term:`attached` to the :class:`.Session`,
    which is a state they stay in until the :class:`.Session` is closed
    (which is introduced at :ref:`tutorial_orm_closing`).


    .. tip::

        An important thing to note is that attributes on the objects that we just
        worked with have been :term:`expired`, meaning, when we next access any
        attributes on them, the :class:`.Session` will start a new transaction and
        re-load their state. This option is sometimes problematic for both
        performance reasons, or if one wishes to use the objects after closing the
        :class:`.Session` (which is known as the :term:`detached` state), as they
        will not have any state and will have no :class:`.Session` with which to load
        that state, leading to "detached instance" errors. The behavior is
        controllable using a parameter called :paramref:`.Session.expire_on_commit`.
        More on this is at :ref:`tutorial_orm_closing`.


.. _tutorial_orm_updating:

使用工作单元模式更新 ORM 对象
----------------------------------------------------

Updating ORM Objects using the Unit of Work pattern

.. tab:: 中文

    在前一节 :ref:`tutorial_core_update_delete` 中，我们介绍了表示 SQL UPDATE 语句的 :class:`_sql.Update` 构造。在使用 ORM 时，有两种方式使用该构造。主要方式是它作为 :class:`_orm.Session` 使用的 :term:`unit of work` 过程的一部分自动发出，其中 UPDATE 语句根据具有更改的单个对象对应的主键逐个发出。

    假设我们将用户名为 ``sandy`` 的 ``User`` 对象加载到一个事务中（也展示了 :meth:`_sql.Select.filter_by` 方法以及 :meth:`_engine.Result.scalar_one` 方法）：

    .. sourcecode:: pycon+sql

        >>> sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('sandy',)

    如前所述，Python 对象 ``sandy`` 充当数据库中行的 **代理(proxy)**，更具体地说，是 **当前事务中的(in terms of the
    current transaction)** 数据库行，该行具有 ``2`` 的主键标识::

        >>> sandy
        User(id=2, name='sandy', fullname='Sandy Cheeks')

    如果我们更改此对象的属性，:class:`_orm.Session` 将跟踪此更改::

        >>> sandy.fullname = "Sandy Squirrel"

    该对象出现在名为 :attr:`_orm.Session.dirty` 的集合中，表示该对象是“脏的”::

        >>> sandy in session.dirty
        True

    当 :class:`_orm.Session` 下次发出 flush 时，将发出一个 UPDATE 来更新数据库中的此值。如前所述，flush 会在我们发出任何 SELECT 之前自动发生，使用一种称为 **autoflush** 的行为。我们可以直接查询此行的 ``User.fullname`` 列，并且我们将获得更新的值：

    .. sourcecode:: pycon+sql

        >>> sandy_fullname = session.execute(select(User.fullname).where(User.id == 2)).scalar_one()
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.id = ?
        [...] ('Sandy Squirrel', 2)
        SELECT user_account.fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}
        >>> print(sandy_fullname)
        Sandy Squirrel

    我们可以看到上面我们请求 :class:`_orm.Session` 执行一个 :func:`_sql.select` 语句。然而，发出的 SQL 显示还发出了一个 UPDATE，这是 flush 过程推送待处理更改的结果。``sandy`` Python 对象现在不再被认为是脏的::

        >>> sandy in session.dirty
        False

    但是请注意，我们 **仍然在事务中(still in a transaction)**，我们的更改尚未推送到数据库的永久存储中。由于 Sandy 的姓氏实际上是“Cheeks”而不是“Squirrel”，我们将在稍后回滚事务时修复此错误。但首先我们将进行一些数据更改。

    .. seealso::

        :ref:`session_flushing` - 详细介绍了 flush 过程以及 :paramref:`_orm.Session.autoflush` 设置的相关信息。

.. tab:: 英文

    In the preceding section :ref:`tutorial_core_update_delete`, we introduced the
    :class:`_sql.Update` construct that represents a SQL UPDATE statement. When
    using the ORM, there are two ways in which this construct is used. The primary
    way is that it is emitted automatically as part of the :term:`unit of work`
    process used by the :class:`_orm.Session`, where an UPDATE statement is emitted
    on a per-primary key basis corresponding to individual objects that have
    changes on them.

    Supposing we loaded the ``User`` object for the username ``sandy`` into
    a transaction (also showing off the :meth:`_sql.Select.filter_by` method
    as well as the :meth:`_engine.Result.scalar_one` method):

    .. sourcecode:: pycon+sql

        >>> sandy = session.execute(select(User).filter_by(name="sandy")).scalar_one()
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('sandy',)

    The Python object ``sandy`` as mentioned before acts as a **proxy** for the
    row in the database, more specifically the database row **in terms of the
    current transaction**, that has the primary key identity of ``2``::

        >>> sandy
        User(id=2, name='sandy', fullname='Sandy Cheeks')

    If we alter the attributes of this object, the :class:`_orm.Session` tracks
    this change::

        >>> sandy.fullname = "Sandy Squirrel"

    The object appears in a collection called :attr:`_orm.Session.dirty`, indicating
    the object is "dirty"::

        >>> sandy in session.dirty
        True

    When the :class:`_orm.Session` next emits a flush, an UPDATE will be emitted
    that updates this value in the database.  As mentioned previously, a flush
    occurs automatically before we emit any SELECT, using a behavior known as
    **autoflush**.  We can query directly for the ``User.fullname`` column
    from this row and we will get our updated value back:

    .. sourcecode:: pycon+sql

        >>> sandy_fullname = session.execute(select(User.fullname).where(User.id == 2)).scalar_one()
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.id = ?
        [...] ('Sandy Squirrel', 2)
        SELECT user_account.fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}
        >>> print(sandy_fullname)
        Sandy Squirrel

    We can see above that we requested that the :class:`_orm.Session` execute
    a single :func:`_sql.select` statement.  However the SQL emitted shows
    that an UPDATE were emitted as well, which was the flush process pushing
    out pending changes.  The ``sandy`` Python object is now no longer considered
    dirty::

        >>> sandy in session.dirty
        False

    However note we are **still in a transaction** and our changes have not
    been pushed to the database's permanent storage.   Since Sandy's last name
    is in fact "Cheeks" not "Squirrel", we will repair this mistake later when
    we roll back the transaction.  But first we'll make some more data changes.


    .. seealso::

        :ref:`session_flushing`- details the flush process as well as information
        about the :paramref:`_orm.Session.autoflush` setting.



.. _tutorial_orm_deleting:


使用工作单元模式删除 ORM 对象
----------------------------------------------------

Deleting ORM Objects using the Unit of Work pattern

.. tab:: 中文

    为了完成基本的持久化操作，可以使用 :meth:`_orm.Session.delete` 方法在 :term:`unit of work` 过程中标记单个 ORM 对象以进行删除。让我们从数据库加载 ``patrick``：

    .. sourcecode:: pycon+sql

        >>> patrick = session.get(User, 3)
        {execsql}SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
        user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (3,)

    如果我们将 ``patrick`` 标记为删除，与其他操作一样，实际上不会发生任何事情，直到进行 flush::

        >>> session.delete(patrick)

    当前的 ORM 行为是 ``patrick`` 仍然保留在 :class:`_orm.Session` 中，直到进行 flush，如前所述，如果我们发出查询，则会发生 flush：

    .. sourcecode:: pycon+sql

        >>> session.execute(select(User).where(User.name == "patrick")).first()
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address,
        address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,)
        DELETE FROM user_account WHERE user_account.id = ?
        [...] (3,)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',)

    上面，我们请求发出的 SELECT 之前有一个 DELETE，这表明 ``patrick`` 的待删除操作已进行。还对 ``address`` 表进行了 SELECT，这是由 ORM 查找该表中可能与目标行相关的行引起的；这种行为是 :term:`cascade` 行为的一部分，可以通过允许数据库自动处理 ``address`` 中的相关行来提高效率；部分 :ref:`cascade_delete` 提供了有关此的所有详细信息。

    .. seealso::

        :ref:`cascade_delete` - 介绍如何调整 :meth:`_orm.Session.delete` 的行为，以处理其他表中的相关行。

    此外，现在被删除的 ``patrick`` 对象实例不再被视为 :class:`_orm.Session` 中的持久对象，如包含检查所示：

        >>> patrick in session
        False

    但是，就像我们对 ``sandy`` 对象所做的 UPDATE 一样，我们在此处所做的每一个更改都是本地的持续事务的一部分，如果我们不提交它，它们将不会变为永久的。由于回滚事务实际上更有趣，我们将在下一节中进行回滚。

.. tab:: 英文

    To round out the basic persistence operations, an individual ORM object
    may be marked for deletion within the :term:`unit of work` process
    by using the :meth:`_orm.Session.delete` method.
    Let's load up ``patrick`` from the database:

    .. sourcecode:: pycon+sql

        >>> patrick = session.get(User, 3)
        {execsql}SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
        user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (3,)

    If we mark ``patrick`` for deletion, as is the case with other operations,
    nothing actually happens yet until a flush proceeds::

        >>> session.delete(patrick)

    Current ORM behavior is that ``patrick`` stays in the :class:`_orm.Session`
    until the flush proceeds, which as mentioned before occurs if we emit a query:

    .. sourcecode:: pycon+sql

        >>> session.execute(select(User).where(User.name == "patrick")).first()
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address,
        address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,)
        DELETE FROM user_account WHERE user_account.id = ?
        [...] (3,)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',)

    Above, the SELECT we asked to emit was preceded by a DELETE, which indicated
    the pending deletion for ``patrick`` proceeded.  There was also a ``SELECT``
    against the ``address`` table, which was prompted by the ORM looking for rows
    in this table which may be related to the target row; this behavior is part of
    a behavior known as :term:`cascade`, and can be tailored to work more
    efficiently by allowing the database to handle related rows in ``address``
    automatically; the section :ref:`cascade_delete` has all the detail on this.

    .. seealso::

        :ref:`cascade_delete` - describes how to tune the behavior of
        :meth:`_orm.Session.delete` in terms of how related rows in other tables
        should be handled.

    Beyond that, the ``patrick`` object instance now being deleted is no longer
    considered to be persistent within the :class:`_orm.Session`, as is shown
    by the containment check::

        >>> patrick in session
        False

    However just like the UPDATEs we made to the ``sandy`` object, every change
    we've made here is local to an ongoing transaction, which won't become
    permanent if we don't commit it.  As rolling the transaction back is actually
    more interesting at the moment, we will do that in the next section.

.. _tutorial_orm_bulk:


批量/多行 INSERT、upsert、UPDATE 和 DELETE
---------------------------------------------------

Bulk / Multi Row INSERT, upsert, UPDATE and DELETE

.. tab:: 中文

    :term:`unit of work` 技术旨在结合 :term:`dml` （即 INSERT/UPDATE/DELETE 语句）与 Python 对象机制，通常涉及复杂的相互关联的对象图。一旦使用 :meth:`.Session.add` 将对象添加到 :class:`.Session` 中，unit of work 过程将透明地为我们发出 INSERT/UPDATE/DELETE 语句，因为对象上的属性被创建和修改。

    然而，ORM :class:`.Session` 还具有处理命令的能力，使其能够直接发出 INSERT、UPDATE 和 DELETE 语句，而无需传递任何 ORM 持久化对象，而是传递要 INSERT、UPDATE 或 UPSERT 的值列表，或 WHERE 条件，以便可以调用一次匹配多行的 UPDATE 或 DELETE 语句。这种使用模式在需要影响大量行而无需构造和操作映射对象时尤为重要，对于简化、性能密集的任务（例如大规模批量插入）来说，可能是繁琐且不必要的。

    ORM :class:`_orm.Session` 的批量/多行功能直接使用 :func:`_dml.insert`、:func:`_dml.update` 和 :func:`_dml.delete` 构造，它们的用法类似于 SQLAlchemy Core 的用法（首次在本教程中介绍见 :ref:`tutorial_core_insert` 和 :ref:`tutorial_core_update_delete`）。当在 ORM :class:`_orm.Session` 中使用这些构造而不是简单的 :class:`_engine.Connection` 时，它们的构造、执行和结果处理完全与 ORM 集成。

    有关使用这些功能的背景和示例，请参见 :ref:`queryguide_toplevel` 中的 :ref:`orm_expression_update_delete` 部分。

    .. seealso::

        :ref:`orm_expression_update_delete` - 在 :ref:`queryguide_toplevel` 中

.. tab:: 英文

    The :term:`unit of work` techniques discussed in this section
    are intended to integrate :term:`dml`, or INSERT/UPDATE/DELETE statements,
    with Python object mechanics, often involving complex graphs of
    inter-related objects.  Once objects are added to a :class:`.Session` using
    :meth:`.Session.add`, the unit of work process transparently emits
    INSERT/UPDATE/DELETE on our behalf as attributes on our objects are created
    and modified.

    However, the ORM :class:`.Session` also has the ability to process commands
    that allow it to emit INSERT, UPDATE and DELETE statements directly without
    being passed any ORM-persisted objects, instead being passed lists of values to
    be INSERTed, UPDATEd, or upserted, or WHERE criteria so that an UPDATE or
    DELETE statement that matches many rows at once can be invoked. This mode of
    use is of particular importance when large numbers of rows must be affected
    without the need to construct and manipulate mapped objects, which may be
    cumbersome and unnecessary for simplistic, performance-intensive tasks such as
    large bulk inserts.

    The Bulk / Multi row features of the ORM :class:`_orm.Session` make use of the
    :func:`_dml.insert`, :func:`_dml.update` and :func:`_dml.delete` constructs
    directly, and their usage resembles how they are used with SQLAlchemy Core
    (first introduced in this tutorial at :ref:`tutorial_core_insert` and
    :ref:`tutorial_core_update_delete`).  When using these constructs
    with the ORM :class:`_orm.Session` instead of a plain :class:`_engine.Connection`,
    their construction, execution and result handling is fully integrated with the ORM.

    For background and examples on using these features, see the section
    :ref:`orm_expression_update_delete` in the :ref:`queryguide_toplevel`.

    .. seealso::

        :ref:`orm_expression_update_delete` - in the :ref:`queryguide_toplevel`


回滚
-------------

Rolling Back

.. tab:: 中文

    :class:`_orm.Session` 具有一个 :meth:`_orm.Session.rollback` 方法，该方法如预期的那样在正在进行的 SQL 连接上发出 ROLLBACK。然而，它对当前与 :class:`_orm.Session` 关联的对象也有影响，在我们之前的示例中是 Python 对象 ``sandy``。虽然我们将 ``sandy`` 对象的 ``.fullname`` 更改为 ``"Sandy Squirrel"``，但我们想要回滚此更改。调用 :meth:`_orm.Session.rollback` 不仅会回滚事务，还会 **expire** 当前与此 :class:`_orm.Session` 关联的所有对象，这将使它们在下次访问时使用称为 :term:`lazy loading` 的过程刷新自己：

    .. sourcecode:: pycon+sql

        >>> session.rollback()
        ROLLBACK

    要更仔细地查看“过期”过程，我们可以观察到 Python 对象 ``sandy`` 在其 Python ``__dict__`` 中没有剩余状态，除了一个特殊的 SQLAlchemy 内部状态对象::

        >>> sandy.__dict__
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x...>}

    这是“ :term:`expired` ”状态；再次访问该属性将自动开始一个新事务，并使用当前数据库行刷新 ``sandy``：

    .. sourcecode:: pycon+sql

        >>> sandy.fullname
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
        user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}
        'Sandy Cheeks'

    我们现在可以观察到，整个数据库行也填充到了 ``sandy`` 对象的 ``__dict__`` 中：

        >>> sandy.__dict__  # doctest: +SKIP
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x...>,
        'id': 2, 'name': 'sandy', 'fullname': 'Sandy Cheeks'}

    对于已删除的对象，当我们之前注意到 ``patrick`` 不再在会话中时，该对象的身份也被恢复：

        >>> patrick in session
        True

    当然，数据库数据也会再次存在：

    .. sourcecode:: pycon+sql

        >>> session.execute(select(User).where(User.name == "patrick")).scalar_one() is patrick
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',){stop}
        True

.. tab:: 英文

    The :class:`_orm.Session` has a :meth:`_orm.Session.rollback` method that as
    expected emits a ROLLBACK on the SQL connection in progress.  However, it also
    has an effect on the objects that are currently associated with the
    :class:`_orm.Session`, in our previous example the Python object ``sandy``.
    While we changed the ``.fullname`` of the ``sandy`` object to read ``"Sandy
    Squirrel"``, we want to roll back this change.   Calling
    :meth:`_orm.Session.rollback` will not only roll back the transaction but also
    **expire** all objects currently associated with this :class:`_orm.Session`,
    which will have the effect that they will refresh themselves when next accessed
    using a process known as :term:`lazy loading`:

    .. sourcecode:: pycon+sql

        >>> session.rollback()
        ROLLBACK

    To view the "expiration" process more closely, we may observe that the
    Python object ``sandy`` has no state left within its Python ``__dict__``,
    with the exception of a special SQLAlchemy internal state object::

        >>> sandy.__dict__
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x...>}

    This is the ":term:`expired`" state; accessing the attribute again will autobegin
    a new transaction and refresh ``sandy`` with the current database row:

    .. sourcecode:: pycon+sql

        >>> sandy.fullname
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
        user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}
        'Sandy Cheeks'

    We may now observe that the full database row was also populated into the
    ``__dict__`` of the ``sandy`` object::

        >>> sandy.__dict__  # doctest: +SKIP
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x...>,
        'id': 2, 'name': 'sandy', 'fullname': 'Sandy Cheeks'}

    For deleted objects, when we earlier noted that ``patrick`` was no longer
    in the session, that object's identity is also restored::

        >>> patrick in session
        True

    and of course the database data is present again as well:


    .. sourcecode:: pycon+sql

        >>> session.execute(select(User).where(User.name == "patrick")).scalar_one() is patrick
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',){stop}
        True

.. _tutorial_orm_closing:

关闭会话
------------------

Closing a Session

.. tab:: 中文

    在上述部分中，我们在 Python 上下文管理器之外使用了 :class:`_orm.Session` 对象，即我们没有使用 ``with`` 语句。这没问题，但是如果我们这样做，最好在完成后显式关闭 :class:`_orm.Session`：

    .. sourcecode:: pycon+sql

        >>> session.close()
        {execsql}ROLLBACK

    关闭 :class:`_orm.Session` （在上下文管理器中也会发生）完成以下事情：

    * 它将所有连接资源 :term:`releases` 到连接池，取消（例如回滚）正在进行的任何事务。

      这意味着当我们使用会话执行一些只读任务然后关闭它时，我们不需要显式调用 :meth:`_orm.Session.rollback` 来确保事务已回滚；连接池会处理这些。

    * 它 **expunges** 所有对象从 :class:`_orm.Session` 中。

      这意味着我们为此 :class:`_orm.Session` 加载的所有 Python 对象，如 ``sandy``、``patrick`` 和 ``squidward``，现在处于称为 :term:`detached` 的状态。特别是，我们将注意到仍处于 :term:`expired` 状态的对象，例如由于调用了 :meth:`_orm.Session.commit`，现在无法使用，因为它们不包含当前行的状态，并且不再与任何数据库事务关联以进行刷新::

        # 注意'squidward.name'之前刚刚过期，所以它的值未加载
        >>> squidward.name
        Traceback (most recent call last):
        ...
        sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x...> is not bound to a Session; attribute refresh operation cannot proceed

    可以使用 :meth:`_orm.Session.add` 方法将分离的对象重新关联到相同或新的 :class:`_orm.Session`，这将重新建立它们与特定数据库行的关系：

    .. sourcecode:: pycon+sql

        >>> session.add(squidward)
        >>> squidward.name
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (4,){stop}
        'squidward'

    ..

    .. tip::

        尽量避免在分离状态下使用对象，如果可能的话。当 :class:`_orm.Session` 关闭时，清理对所有以前附加对象的引用。对于需要分离对象的情况，通常是为了刚提交对象的即时显示，例如在视图呈现之前关闭 :class:`_orm.Session` 的 Web 应用程序，为此，将 :paramref:`_orm.Session.expire_on_commit` 标志设置为 ``False``。
    ..

.. tab:: 英文

    Within the above sections we used a :class:`_orm.Session` object outside
    of a Python context manager, that is, we didn't use the ``with`` statement.
    That's fine, however if we are doing things this way, it's best that we explicitly
    close out the :class:`_orm.Session` when we are done with it:

    .. sourcecode:: pycon+sql

        >>> session.close()
        {execsql}ROLLBACK

    Closing the :class:`_orm.Session`, which is what happens when we use it in
    a context manager as well, accomplishes the following things:

    * It :term:`releases` all connection resources to the connection pool, cancelling out (e.g. rolling back) any transactions that were in progress.
        
      This means that when we make use of a session to perform some read-only tasks and then close it, we don't need to explicitly call upon :meth:`_orm.Session.rollback` to make sure the transaction is rolled back; the connection pool handles this.

    * It **expunges** all objects from the :class:`_orm.Session`.

      This means that all the Python objects we had loaded for this :class:`_orm.Session`,
      like ``sandy``, ``patrick`` and ``squidward``, are now in a state known
      as :term:`detached`.  In particular, we will note that objects that were still
      in an :term:`expired` state, for example due to the call to :meth:`_orm.Session.commit`,
      are now non-functional, as they don't contain the state of a current row and
      are no longer associated with any database transaction in which to be
      refreshed::

        # note that 'squidward.name' was just expired previously, so its value is unloaded
        >>> squidward.name
        Traceback (most recent call last):
        ...
        sqlalchemy.orm.exc.DetachedInstanceError: Instance <User at 0x...> is not bound to a Session; attribute refresh operation cannot proceed

    The detached objects can be re-associated with the same, or a new
    :class:`_orm.Session` using the :meth:`_orm.Session.add` method, which
    will re-establish their relationship with their particular database row:

    .. sourcecode:: pycon+sql

        >>> session.add(squidward)
        >>> squidward.name
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (4,){stop}
        'squidward'

    ..

    .. tip::

        Try to avoid using objects in their detached state, if possible. When the
        :class:`_orm.Session` is closed, clean up references to all the
        previously attached objects as well.   For cases where detached objects
        are necessary, typically the immediate display of just-committed objects
        for a web application where the :class:`_orm.Session` is closed before
        the view is rendered, set the :paramref:`_orm.Session.expire_on_commit`
        flag to ``False``.
    ..
