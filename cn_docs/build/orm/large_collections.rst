.. highlight:: pycon+sql
.. doctest-enable

.. currentmodule:: sqlalchemy.orm

.. _largecollections:

使用大型集合
==============================

Working with Large Collections

.. tab:: 中文

    :func:`_orm.relationship` 的默认行为是根据配置的 :ref:`加载策略 <orm_queryguide_relationship_loaders>` 将集合的内容完全加载到内存中，该策略控制何时以及如何从数据库加载这些内容。相关集合不仅可以在访问时加载到内存中，或提前加载，但在大多数情况下，当集合本身发生变化时，以及在工作单元系统要删除所属对象时，也需要填充。

    当相关集合可能非常大时，在任何情况下都可能不适合将这样的集合填充到内存中，因为该操作可能会过度消耗时间、网络和内存资源。

    本节包括旨在允许 :func:`_orm.relationship` 与大型集合一起使用的 API 功能，同时保持足够的性能。

.. tab:: 英文

    The default behavior of :func:`_orm.relationship` is to fully load
    the contents of collections into memory, based on a configured
    :ref:`loader strategy <orm_queryguide_relationship_loaders>` that controls
    when and how these contents are loaded from the database.  Related collections
    may be loaded into memory not just when they are accessed, or eagerly loaded,
    but in most cases will require population when the collection
    itself is mutated, as well as in cases where the owning object is to be
    deleted by the unit of work system.

    When a related collection is potentially very large, it may not be feasible
    for such a collection to be populated into memory under any circumstances,
    as the operation may be overly consuming of time, network and memory
    resources.

    This section includes API features intended to allow :func:`_orm.relationship`
    to be used with large collections while maintaining adequate performance.


.. _write_only_relationship:

只写关系
------------------------

Write Only Relationships

.. tab:: 中文

    **仅写** 加载策略是配置 :func:`_orm.relationship` 的主要手段，该关系将保持可写，但不会将其内容加载到内存中。以下是现代类型注释声明形式中仅写 ORM 配置的示例：

    .. sourcecode:: python

        >>> from decimal import Decimal
        >>> from datetime import datetime

        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import func
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship
        >>> from sqlalchemy.orm import Session
        >>> from sqlalchemy.orm import WriteOnlyMapped

        >>> class Base(DeclarativeBase):
        ...     pass

        >>> class Account(Base):
        ...     __tablename__ = "account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     identifier: Mapped[str]
        ...
        ...     account_transactions: WriteOnlyMapped["AccountTransaction"] = relationship(
        ...         cascade="all, delete-orphan",
        ...         passive_deletes=True,
        ...         order_by="AccountTransaction.timestamp",
        ...     )
        ...
        ...     def __repr__(self):
        ...         return f"Account(identifier={self.identifier!r})"

        >>> class AccountTransaction(Base):
        ...     __tablename__ = "account_transaction"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     account_id: Mapped[int] = mapped_column(
        ...         ForeignKey("account.id", ondelete="cascade")
        ...     )
        ...     description: Mapped[str]
        ...     amount: Mapped[Decimal]
        ...     timestamp: Mapped[datetime] = mapped_column(default=func.now())
        ...
        ...     def __repr__(self):
        ...         return (
        ...             f"AccountTransaction(amount={self.amount:.2f}, "
        ...             f"timestamp={self.timestamp.isoformat()!r})"
        ...         )
        ...
        ...     __mapper_args__ = {"eager_defaults": True}


    .. setup code not for display

        >>> from sqlalchemy import create_engine
        >>> from sqlalchemy import event
        >>> engine = create_engine("sqlite://", echo=True)
        >>> @event.listens_for(engine, "connect")
        ... def set_sqlite_pragma(dbapi_connection, connection_record):
        ...     cursor = dbapi_connection.cursor()
        ...     cursor.execute("PRAGMA foreign_keys=ON")
        ...     cursor.close()

        >>> Base.metadata.create_all(engine)
        BEGIN...


    如上所述， ``account_transactions`` 关系不是使用普通的 :class:`.Mapped` 注释进行配置，而是使用 :class:`.WriteOnlyMapped` 类型注释，在运行时将 :ref:`loader strategy <orm_queryguide_relationship_loaders>` 分配为 ``lazy="write_only"`` 给目标 :func:`_orm.relationship`。
    :class:`.WriteOnlyMapped` 注释是 :class:`_orm.Mapped` 注释的替代形式，表示在对象实例上使用 :class:`_orm.WriteOnlyCollection` 集合类型。

    上述 :func:`_orm.relationship` 配置还包括几个特定于删除 ``Account`` 对象以及从 ``account_transactions`` 集合中删除 ``AccountTransaction`` 对象时要采取的操作的元素。这些元素是：

    * ``passive_deletes=True`` - 允许 :term:`unit of work` 在删除 ``Account`` 时无需加载集合；请参阅 :ref:`passive_deletes`。
    * 在 :class:`.ForeignKey` 约束上配置的 ``ondelete="cascade"``。这也详见 :ref:`passive_deletes`。
    * ``cascade="all, delete-orphan"`` - 指示 :term:`unit of work` 在从集合中删除 ``AccountTransaction`` 对象时将其删除。请参阅 :ref:`cascade_delete_orphan` 在 :ref:`unitofwork_cascades` 文档中。

    .. versionadded:: 2.0  添加了“仅写”关系加载器。

.. tab:: 英文

    The **write only** loader strategy is the primary means of configuring a
    :func:`_orm.relationship` that will remain writeable, but will not load
    its contents into memory.  A write-only ORM configuration in modern
    type-annotated Declarative form is illustrated below:
    
    .. sourcecode:: python
    
        >>> from decimal import Decimal
        >>> from datetime import datetime
    
        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import func
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship
        >>> from sqlalchemy.orm import Session
        >>> from sqlalchemy.orm import WriteOnlyMapped
    
        >>> class Base(DeclarativeBase):
        ...     pass
    
        >>> class Account(Base):
        ...     __tablename__ = "account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     identifier: Mapped[str]
        ...
        ...     account_transactions: WriteOnlyMapped["AccountTransaction"] = relationship(
        ...         cascade="all, delete-orphan",
        ...         passive_deletes=True,
        ...         order_by="AccountTransaction.timestamp",
        ...     )
        ...
        ...     def __repr__(self):
        ...         return f"Account(identifier={self.identifier!r})"
    
        >>> class AccountTransaction(Base):
        ...     __tablename__ = "account_transaction"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     account_id: Mapped[int] = mapped_column(
        ...         ForeignKey("account.id", ondelete="cascade")
        ...     )
        ...     description: Mapped[str]
        ...     amount: Mapped[Decimal]
        ...     timestamp: Mapped[datetime] = mapped_column(default=func.now())
        ...
        ...     def __repr__(self):
        ...         return (
        ...             f"AccountTransaction(amount={self.amount:.2f}, "
        ...             f"timestamp={self.timestamp.isoformat()!r})"
        ...         )
        ...
        ...     __mapper_args__ = {"eager_defaults": True}
    
    
    .. setup code not for display
    
        >>> from sqlalchemy import create_engine
        >>> from sqlalchemy import event
        >>> engine = create_engine("sqlite://", echo=True)
        >>> @event.listens_for(engine, "connect")
        ... def set_sqlite_pragma(dbapi_connection, connection_record):
        ...     cursor = dbapi_connection.cursor()
        ...     cursor.execute("PRAGMA foreign_keys=ON")
        ...     cursor.close()
    
        >>> Base.metadata.create_all(engine)
        BEGIN...
    
    
    Above, the ``account_transactions`` relationship is configured not using the
    ordinary :class:`.Mapped` annotation, but instead
    using the :class:`.WriteOnlyMapped` type annotation, which at runtime will
    assign the :ref:`loader strategy <orm_queryguide_relationship_loaders>` of
    ``lazy="write_only"`` to the target :func:`_orm.relationship`.
    The :class:`.WriteOnlyMapped` annotation is an
    alternative form of the :class:`_orm.Mapped` annotation which indicate the use
    of the :class:`_orm.WriteOnlyCollection` collection type on instances of the
    object.
    
    The above :func:`_orm.relationship` configuration also includes several
    elements that are specific to what action to take when ``Account`` objects
    are deleted, as well as when ``AccountTransaction`` objects are removed from the
    ``account_transactions`` collection.  These elements are:
    
    * ``passive_deletes=True`` - allows the :term:`unit of work` to forego having
      to load the collection when ``Account`` is deleted; see
      :ref:`passive_deletes`.
    * ``ondelete="cascade"`` configured on the :class:`.ForeignKey` constraint.
      This is also detailed at :ref:`passive_deletes`.
    * ``cascade="all, delete-orphan"`` - instructs the :term:`unit of work` to
      delete ``AccountTransaction`` objects when they are removed from the
      collection.  See :ref:`cascade_delete_orphan` in the :ref:`unitofwork_cascades`
      document.
    
    .. versionadded:: 2.0  Added "Write only" relationship loaders.


创建和保存新的只写集合
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating and Persisting New Write Only Collections

.. tab:: 中文

    仅写集合仅允许对 :term:`transient` 或 :term:`pending` 对象直接赋值集合。使用上述映射，这意味着我们可以创建一个新的 ``Account`` 对象，并添加一系列 ``AccountTransaction`` 对象到 :class:`_orm.Session` 中。可以使用任何 Python 可迭代对象作为开始的对象源，下面我们使用 Python ``list``::

        >>> new_account = Account(
        ...     identifier="account_01",
        ...     account_transactions=[
        ...         AccountTransaction(description="initial deposit", amount=Decimal("500.00")),
        ...         AccountTransaction(description="transfer", amount=Decimal("1000.00")),
        ...         AccountTransaction(description="withdrawal", amount=Decimal("-29.50")),
        ...     ],
        ... )

        >>> with Session(engine) as session:
        ...     session.add(new_account)
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO account (identifier) VALUES (?)
        [...] ('account_01',)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [... (insertmanyvalues) 1/3 (ordered; batch not supported)] (1, 'initial deposit', 500.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 2/3 (ordered; batch not supported)] (1, 'transfer', 1000.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 3/3 (ordered; batch not supported)] (1, 'withdrawal', -29.5)
        COMMIT


    一旦对象被持久化到数据库（即处于 :term:`persistent` 或 :term:`detached` 状态），集合可以通过新项目进行扩展，也可以删除单个项目。然而，集合 **不能再通过完全替换集合进行重新赋值** ，因为这样的操作需要将以前的集合完全加载到内存中，以便将旧条目与新条目进行对比::

        >>> new_account.account_transactions = [
        ...     AccountTransaction(description="some transaction", amount=Decimal("10.00"))
        ... ]
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: Collection "Account.account_transactions" does not
        support implicit iteration; collection replacement operations can't be used

.. tab:: 英文

    The write-only collection allows for direct assignment of the collection
    as a whole **only** for :term:`transient` or :term:`pending` objects.
    With our above mapping, this indicates we can create a new ``Account``
    object with a sequence of ``AccountTransaction`` objects to be added
    to a :class:`_orm.Session`.   Any Python iterable may be used as the
    source of objects to start, where below we use a Python ``list``::

        >>> new_account = Account(
        ...     identifier="account_01",
        ...     account_transactions=[
        ...         AccountTransaction(description="initial deposit", amount=Decimal("500.00")),
        ...         AccountTransaction(description="transfer", amount=Decimal("1000.00")),
        ...         AccountTransaction(description="withdrawal", amount=Decimal("-29.50")),
        ...     ],
        ... )

        >>> with Session(engine) as session:
        ...     session.add(new_account)
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO account (identifier) VALUES (?)
        [...] ('account_01',)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [... (insertmanyvalues) 1/3 (ordered; batch not supported)] (1, 'initial deposit', 500.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 2/3 (ordered; batch not supported)] (1, 'transfer', 1000.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 3/3 (ordered; batch not supported)] (1, 'withdrawal', -29.5)
        COMMIT


    Once an object is database-persisted (i.e. in the :term:`persistent` or
    :term:`detached` state), the collection has the ability to be extended with new
    items as well as the ability for individual items to be removed. However, the
    collection may **no longer be re-assigned with a full replacement collection**,
    as such an operation requires that the previous collection is fully
    loaded into memory in order to reconcile the old entries with the new ones::

        >>> new_account.account_transactions = [
        ...     AccountTransaction(description="some transaction", amount=Decimal("10.00"))
        ... ]
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: Collection "Account.account_transactions" does not
        support implicit iteration; collection replacement operations can't be used

向现有集合添加新项目
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adding New Items to an Existing Collection

.. tab:: 中文

    对于持久对象的仅写集合，
    使用 :term:`unit of work` 进程修改集合只能通过使用 :meth:`.WriteOnlyCollection.add`、
    :meth:`.WriteOnlyCollection.add_all` 和 :meth:`.WriteOnlyCollection.remove` 方法进行::

        >>> from sqlalchemy import select
        >>> session = Session(engine, expire_on_commit=False)
        >>> existing_account = session.scalar(select(Account).filter_by(identifier="account_01"))
        {execsql}BEGIN (implicit)
        SELECT account.id, account.identifier
        FROM account
        WHERE account.identifier = ?
        [...] ('account_01',)
        {stop}
        >>> existing_account.account_transactions.add_all(
        ...     [
        ...         AccountTransaction(description="paycheck", amount=Decimal("2000.00")),
        ...         AccountTransaction(description="rent", amount=Decimal("-800.00")),
        ...     ]
        ... )
        >>> session.commit()
        {execsql}INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] (1, 'paycheck', 2000.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 2/2 (ordered; batch not supported)] (1, 'rent', -800.0)
        COMMIT


    上面添加的项目保存在 :class:`_orm.Session` 的待处理队列中，直到下一次刷新，
    此时它们将被插入到数据库中，前提是添加的对象之前是 :term:`transient` 的。

.. tab:: 英文

    For write-only collections of persistent objects,
    modifications to the collection using :term:`unit of work` processes may proceed
    only by using the :meth:`.WriteOnlyCollection.add`,
    :meth:`.WriteOnlyCollection.add_all` and :meth:`.WriteOnlyCollection.remove`
    methods::

        >>> from sqlalchemy import select
        >>> session = Session(engine, expire_on_commit=False)
        >>> existing_account = session.scalar(select(Account).filter_by(identifier="account_01"))
        {execsql}BEGIN (implicit)
        SELECT account.id, account.identifier
        FROM account
        WHERE account.identifier = ?
        [...] ('account_01',)
        {stop}
        >>> existing_account.account_transactions.add_all(
        ...     [
        ...         AccountTransaction(description="paycheck", amount=Decimal("2000.00")),
        ...         AccountTransaction(description="rent", amount=Decimal("-800.00")),
        ...     ]
        ... )
        >>> session.commit()
        {execsql}INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] (1, 'paycheck', 2000.0)
        INSERT INTO account_transaction (account_id, description, amount, timestamp)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP) RETURNING id, timestamp
        [insertmanyvalues 2/2 (ordered; batch not supported)] (1, 'rent', -800.0)
        COMMIT


    The items added above are held in a pending queue within the
    :class:`_orm.Session` until the next flush, at which point they are INSERTed
    into the database, assuming the added objects were previously :term:`transient`.

查询项目
~~~~~~~~~~~~~~

Querying Items

.. tab:: 中文

    :class:`_orm.WriteOnlyCollection` 不在任何时候存储对集合当前内容的引用，也不会有任何行为直接向数据库发出 SELECT 以加载它们；其主要假设是集合可能包含成千上万或数百万行，不应作为任何其他操作的副作用完全加载到内存中。

    相反，:class:`_orm.WriteOnlyCollection` 包含生成 SQL 的助手方法，如 :meth:`_orm.WriteOnlyCollection.select`，该方法将生成一个 :class:`.Select` 构造，该构造预先配置了当前父行的正确 WHERE / FROM 条件，然后可以进一步修改以选择所需的任何行范围，并可以使用 :ref:`server side cursors <orm_queryguide_yield_per>` 等功能调用，以便希望以内存高效的方式遍历整个集合的进程。

    生成的语句如下所示。请注意，它还包括在示例映射中由 :func:`_orm.relationship` 的 :paramref:`_orm.relationship.order_by` 参数指示的 ORDER BY 条件；如果未配置该参数，则会省略此条件::

        >>> print(existing_account.account_transactions.select())
        {printsql}SELECT account_transaction.id, account_transaction.account_id, account_transaction.description,
        account_transaction.amount, account_transaction.timestamp
        FROM account_transaction
        WHERE :param_1 = account_transaction.account_id ORDER BY account_transaction.timestamp

    我们可以将此 :class:`.Select` 构造与 :class:`_orm.Session` 结合使用，以查询 ``AccountTransaction`` 对象，最简单的方法是使用 :meth:`_orm.Session.scalars` 方法，该方法将返回一个 :class:`.Result`，直接生成 ORM 对象。通常，但不是必须的，:class:`.Select` 会进一步修改以限制返回的记录；在下面的示例中，添加了额外的 WHERE 条件以仅加载“借记”账户交易，并添加了“LIMIT 10”以仅检索前十行::

        >>> account_transactions = session.scalars(
        ...     existing_account.account_transactions.select()
        ...     .where(AccountTransaction.amount < 0)
        ...     .limit(10)
        ... ).all()
        {execsql}BEGIN (implicit)
        SELECT account_transaction.id, account_transaction.account_id, account_transaction.description,
        account_transaction.amount, account_transaction.timestamp
        FROM account_transaction
        WHERE ? = account_transaction.account_id AND account_transaction.amount < ?
        ORDER BY account_transaction.timestamp  LIMIT ? OFFSET ?
        [...] (1, 0, 10, 0)
        {stop}>>> print(account_transactions)
        [AccountTransaction(amount=-29.50, timestamp='...'), AccountTransaction(amount=-800.00, timestamp='...')]

.. tab:: 英文

    The :class:`_orm.WriteOnlyCollection` does not at any point store a reference
    to the current contents of the collection, nor does it have any behavior where
    it would directly emit a SELECT to the database in order to load them; the
    overriding assumption is that the collection may contain many thousands or
    millions of rows, and should never be fully loaded into memory as a side effect
    of any other operation.

    Instead, the :class:`_orm.WriteOnlyCollection` includes SQL-generating helpers
    such as :meth:`_orm.WriteOnlyCollection.select`, which will generate
    a :class:`.Select` construct pre-configured with the correct WHERE / FROM
    criteria for the current parent row, which can then be further modified in
    order to SELECT any range of rows desired, as well as invoked using features
    like :ref:`server side cursors <orm_queryguide_yield_per>` for processes that
    wish to iterate through the full collection in a memory-efficient manner.

    The statement generated is illustrated below. Note it also includes ORDER BY
    criteria, indicated in the example mapping by the
    :paramref:`_orm.relationship.order_by` parameter of :func:`_orm.relationship`;
    this criteria would be omitted if the parameter were not configured::

        >>> print(existing_account.account_transactions.select())
        {printsql}SELECT account_transaction.id, account_transaction.account_id, account_transaction.description,
        account_transaction.amount, account_transaction.timestamp
        FROM account_transaction
        WHERE :param_1 = account_transaction.account_id ORDER BY account_transaction.timestamp

    We may use this :class:`.Select` construct along with the :class:`_orm.Session`
    in order to query for ``AccountTransaction`` objects, most easily using the
    :meth:`_orm.Session.scalars` method that will return a :class:`.Result` that
    yields ORM objects directly. It's typical, though not required, that the
    :class:`.Select` would be modified further to limit the records returned; in
    the example below, additional WHERE criteria to load only "debit" account
    transactions is added, along with "LIMIT 10" to retrieve only the first ten
    rows::

        >>> account_transactions = session.scalars(
        ...     existing_account.account_transactions.select()
        ...     .where(AccountTransaction.amount < 0)
        ...     .limit(10)
        ... ).all()
        {execsql}BEGIN (implicit)
        SELECT account_transaction.id, account_transaction.account_id, account_transaction.description,
        account_transaction.amount, account_transaction.timestamp
        FROM account_transaction
        WHERE ? = account_transaction.account_id AND account_transaction.amount < ?
        ORDER BY account_transaction.timestamp  LIMIT ? OFFSET ?
        [...] (1, 0, 10, 0)
        {stop}>>> print(account_transactions)
        [AccountTransaction(amount=-29.50, timestamp='...'), AccountTransaction(amount=-800.00, timestamp='...')]


删除项目
~~~~~~~~~~~~~~

Removing Items

.. tab:: 中文

    在当前 :class:`_orm.Session` 中处于 :term:`persistent` 状态的单个项目可以使用 :meth:`.WriteOnlyCollection.remove` 方法标记为从集合中移除。刷新过程将隐式地认为对象已经是集合的一部分。下面的示例演示了移除单个 ``AccountTransaction`` 项目，根据 :ref:`cascade <unitofwork_cascades>` 设置，这将导致该行的 DELETE：

        >>> existing_transaction = account_transactions[0]
        >>> existing_account.account_transactions.remove(existing_transaction)
        >>> session.commit()
        {execsql}DELETE FROM account_transaction WHERE account_transaction.id = ?
        [...] (3,)
        COMMIT

    与任何 ORM 映射的集合一样，对象移除可以继续进行，将对象从集合中取消关联，同时将对象保留在数据库中，或者根据 :func:`_orm.relationship` 的 :ref:`cascade_delete_orphan` 配置为其行发出 DELETE。

    不删除的集合移除涉及为 :ref:`one-to-many <relationship_patterns_o2m>` 关系将外键列设置为 NULL，或者为 :ref:`many-to-many <relationships_many_to_many>` 关系删除相应的关联行。

.. tab:: 英文

    Individual items that are loaded in the :term:`persistent`
    state against the current :class:`_orm.Session` may be marked for removal
    from the collection using the :meth:`.WriteOnlyCollection.remove` method.
    The flush process will implicitly consider the object to be already part
    of the collection when the operation proceeds.   The example below
    illustrates removal of an individual ``AccountTransaction`` item,
    which per :ref:`cascade <unitofwork_cascades>` settings results in a
    DELETE of that row::

    >>> existing_transaction = account_transactions[0]
    >>> existing_account.account_transactions.remove(existing_transaction)
    >>> session.commit()
    {execsql}DELETE FROM account_transaction WHERE account_transaction.id = ?
    [...] (3,)
    COMMIT

    As with any ORM-mapped collection, object removal may proceed either to
    de-associate the object from the collection while leaving the object present in
    the database, or may issue a DELETE for its row, based on the
    :ref:`cascade_delete_orphan` configuration of the :func:`_orm.relationship`.

    Collection removal without deletion involves setting foreign key columns to
    NULL for a :ref:`one-to-many <relationship_patterns_o2m>` relationship, or
    deleting the corresponding association row for a
    :ref:`many-to-many <relationships_many_to_many>` relationship.



批量插入新项目
~~~~~~~~~~~~~~~~~~~~~~~~

Bulk INSERT of New Items

.. tab:: 中文

    :class:`.WriteOnlyCollection` 可以生成 DML 构造，如 :class:`_dml.Insert` 对象，可以在 ORM 上下文中用于产生批量插入行为。请参阅 :ref:`orm_queryguide_bulk_insert` 部分，了解 ORM 批量插入的概述。

.. tab:: 英文

    The :class:`.WriteOnlyCollection` can generate DML constructs such as
    :class:`_dml.Insert` objects, which may be used in an ORM context to
    produce bulk insert behavior.  See the section
    :ref:`orm_queryguide_bulk_insert` for an overview of ORM bulk inserts.

一对多集合
^^^^^^^^^^^

One to Many Collections

.. tab:: 中文

    对于 **仅常规一对多集合**，:meth:`.WriteOnlyCollection.insert` 方法将生成一个 :class:`_dml.Insert` 构造，该构造预先建立了与父对象对应的 VALUES 条件。由于这个 VALUES 条件完全针对相关表，因此该语句可用于插入新行，并同时成为相关集合中的新记录::

        >>> session.execute(
        ...     existing_account.account_transactions.insert(),
        ...     [
        ...         {"description": "transaction 1", "amount": Decimal("47.50")},
        ...         {"description": "transaction 2", "amount": Decimal("-501.25")},
        ...         {"description": "transaction 3", "amount": Decimal("1800.00")},
        ...         {"description": "transaction 4", "amount": Decimal("-300.00")},
        ...     ],
        ... )
        {execsql}BEGIN (implicit)
        INSERT INTO account_transaction (account_id, description, amount, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        [...] [(1, 'transaction 1', 47.5), (1, 'transaction 2', -501.25), (1, 'transaction 3', 1800.0), (1, 'transaction 4', -300.0)]
        <...>
        {stop}
        >>> session.commit()
        COMMIT

    .. seealso::

        :ref:`orm_queryguide_bulk_insert` - 在 :ref:`queryguide_toplevel`

        :ref:`relationship_patterns_o2m` - 在 :ref:`relationship_patterns`

.. tab:: 英文

    For a **regular one to many collection only**, the :meth:`.WriteOnlyCollection.insert`
    method will produce an :class:`_dml.Insert` construct which is pre-established with
    VALUES criteria corresponding to the parent object.  As this VALUES criteria
    is entirely against the related table, the statement can be used to
    INSERT new rows that will at the same time become new records in the
    related collection::

        >>> session.execute(
        ...     existing_account.account_transactions.insert(),
        ...     [
        ...         {"description": "transaction 1", "amount": Decimal("47.50")},
        ...         {"description": "transaction 2", "amount": Decimal("-501.25")},
        ...         {"description": "transaction 3", "amount": Decimal("1800.00")},
        ...         {"description": "transaction 4", "amount": Decimal("-300.00")},
        ...     ],
        ... )
        {execsql}BEGIN (implicit)
        INSERT INTO account_transaction (account_id, description, amount, timestamp) VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        [...] [(1, 'transaction 1', 47.5), (1, 'transaction 2', -501.25), (1, 'transaction 3', 1800.0), (1, 'transaction 4', -300.0)]
        <...>
        {stop}
        >>> session.commit()
        COMMIT

    .. seealso::

        :ref:`orm_queryguide_bulk_insert` - in the :ref:`queryguide_toplevel`

        :ref:`relationship_patterns_o2m` - at :ref:`relationship_patterns`


多对多集合
^^^^^^^^^^^^^^^^^^^^^^^^

Many to Many Collections

.. tab:: 中文

    对于 **多对多集合**，两个类之间的关系涉及一个使用 :class:`_orm.relationship` 的 :paramref:`_orm.relationship.secondary` 参数配置的第三个表。要使用 :class:`.WriteOnlyCollection` 将行批量插入到此类型的集合中，可以先单独批量插入新记录，使用 RETURNING 检索这些记录，然后将这些记录传递给 :meth:`.WriteOnlyCollection.add_all` 方法，其中工作单元进程将继续将它们作为集合的一部分进行持久化。

    假设一个 ``BankAudit`` 类引用了许多使用多对多表的 ``AccountTransaction`` 记录::

        >>> from sqlalchemy import Table, Column
        >>> audit_to_transaction = Table(
        ...     "audit_transaction",
        ...     Base.metadata,
        ...     Column("audit_id", ForeignKey("audit.id", ondelete="CASCADE"), primary_key=True),
        ...     Column(
        ...         "transaction_id",
        ...         ForeignKey("account_transaction.id", ondelete="CASCADE"),
        ...         primary_key=True,
        ...     ),
        ... )
        >>> class BankAudit(Base):
        ...     __tablename__ = "audit"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     account_transactions: WriteOnlyMapped["AccountTransaction"] = relationship(
        ...         secondary=audit_to_transaction, passive_deletes=True
        ...     )

    .. setup code not for display

        >>> Base.metadata.create_all(engine)
        BEGIN...

    为了说明这两个操作，我们使用批量插入添加更多 ``AccountTransaction`` 对象，通过在批量 INSERT 语句中添加 ``returning(AccountTransaction)`` 使用 RETURNING 检索它们（请注意，我们也可以同样轻松地使用现有的 ``AccountTransaction`` 对象）::

        >>> new_transactions = session.scalars(
        ...     existing_account.account_transactions.insert().returning(AccountTransaction),
        ...     [
        ...         {"description": "odd trans 1", "amount": Decimal("50000.00")},
        ...         {"description": "odd trans 2", "amount": Decimal("25000.00")},
        ...         {"description": "odd trans 3", "amount": Decimal("45.00")},
        ...     ],
        ... ).all()
        {execsql}BEGIN (implicit)
        INSERT INTO account_transaction (account_id, description, amount, timestamp) VALUES
        (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP)
        RETURNING id, account_id, description, amount, timestamp
        [...] (1, 'odd trans 1', 50000.0, 1, 'odd trans 2', 25000.0, 1, 'odd trans 3', 45.0)
        {stop}

    准备好一系列 ``AccountTransaction`` 对象后，使用 :meth:`_orm.WriteOnlyCollection.add_all` 方法一次关联多行到新的 ``BankAudit`` 对象::

        >>> bank_audit = BankAudit()
        >>> session.add(bank_audit)
        >>> bank_audit.account_transactions.add_all(new_transactions)
        >>> session.commit()
        {execsql}INSERT INTO audit DEFAULT VALUES
        [...] ()
        INSERT INTO audit_transaction (audit_id, transaction_id) VALUES (?, ?)
        [...] [(1, 10), (1, 11), (1, 12)]
        COMMIT

    .. seealso::

        :ref:`orm_queryguide_bulk_insert` - 在 :ref:`queryguide_toplevel`

        :ref:`relationships_many_to_many` - 在 :ref:`relationship_patterns`

.. tab:: 英文

    For a **many to many collection**, the relationship between two classes
    involves a third table that is configured using the
    :paramref:`_orm.relationship.secondary` parameter of :class:`_orm.relationship`.
    To bulk insert rows into a collection of this type using
    :class:`.WriteOnlyCollection`, the new records may be bulk-inserted separately
    first, retrieved using RETURNING, and those records then passed to the
    :meth:`.WriteOnlyCollection.add_all` method where the unit of work process
    will proceed to persist them as part of the collection.

    Supposing a class ``BankAudit`` referred to many ``AccountTransaction``
    records using a many-to-many table::

        >>> from sqlalchemy import Table, Column
        >>> audit_to_transaction = Table(
        ...     "audit_transaction",
        ...     Base.metadata,
        ...     Column("audit_id", ForeignKey("audit.id", ondelete="CASCADE"), primary_key=True),
        ...     Column(
        ...         "transaction_id",
        ...         ForeignKey("account_transaction.id", ondelete="CASCADE"),
        ...         primary_key=True,
        ...     ),
        ... )
        >>> class BankAudit(Base):
        ...     __tablename__ = "audit"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     account_transactions: WriteOnlyMapped["AccountTransaction"] = relationship(
        ...         secondary=audit_to_transaction, passive_deletes=True
        ...     )

    .. setup code not for display

        >>> Base.metadata.create_all(engine)
        BEGIN...

    To illustrate the two operations, we add more ``AccountTransaction`` objects
    using bulk insert, which we retrieve using RETURNING by adding
    ``returning(AccountTransaction)`` to the bulk INSERT statement (note that
    we could just as easily use existing ``AccountTransaction`` objects as well)::

    >>> new_transactions = session.scalars(
    ...     existing_account.account_transactions.insert().returning(AccountTransaction),
    ...     [
    ...         {"description": "odd trans 1", "amount": Decimal("50000.00")},
    ...         {"description": "odd trans 2", "amount": Decimal("25000.00")},
    ...         {"description": "odd trans 3", "amount": Decimal("45.00")},
    ...     ],
    ... ).all()
    {execsql}BEGIN (implicit)
    INSERT INTO account_transaction (account_id, description, amount, timestamp) VALUES
    (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP), (?, ?, ?, CURRENT_TIMESTAMP)
    RETURNING id, account_id, description, amount, timestamp
    [...] (1, 'odd trans 1', 50000.0, 1, 'odd trans 2', 25000.0, 1, 'odd trans 3', 45.0)
    {stop}

    With a list of ``AccountTransaction`` objects ready, the
    :meth:`_orm.WriteOnlyCollection.add_all` method is used to associate many rows
    at once with a new ``BankAudit`` object::

    >>> bank_audit = BankAudit()
    >>> session.add(bank_audit)
    >>> bank_audit.account_transactions.add_all(new_transactions)
    >>> session.commit()
    {execsql}INSERT INTO audit DEFAULT VALUES
    [...] ()
    INSERT INTO audit_transaction (audit_id, transaction_id) VALUES (?, ?)
    [...] [(1, 10), (1, 11), (1, 12)]
    COMMIT

    .. seealso::

        :ref:`orm_queryguide_bulk_insert` - in the :ref:`queryguide_toplevel`

        :ref:`relationships_many_to_many` - at :ref:`relationship_patterns`


批量更新和删除项目
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bulk UPDATE and DELETE of Items

.. tab:: 中文

    类似于 :class:`.WriteOnlyCollection` 可以生成带有预先建立的 WHERE 条件的 :class:`.Select` 构造，它也可以生成带有相同 WHERE 条件的 :class:`.Update` 和 :class:`.Delete` 构造，以允许针对大集合中的元素进行条件更新和删除语句。

.. tab:: 英文

    In a similar way in which :class:`.WriteOnlyCollection` can generate
    :class:`.Select` constructs with WHERE criteria pre-established, it can
    also generate :class:`.Update` and :class:`.Delete` constructs with that
    same WHERE criteria, to allow criteria-oriented UPDATE and DELETE statements
    against the elements in a large collection.

一对多集合
^^^^^^^^^^^^^^^^^^^^^^^

One To Many Collections

.. tab:: 中文

    正如 INSERT 的情况一样，这个功能对于 **一对多集合** 最为简单。

    在下面的示例中，使用 :meth:`.WriteOnlyCollection.update` 方法对集合中的元素生成一个 UPDATE 语句，定位“amount”等于 ``-800`` 的行，并将金额增加 ``200``::

        >>> session.execute(
        ...     existing_account.account_transactions.update()
        ...     .values(amount=AccountTransaction.amount + 200)
        ...     .where(AccountTransaction.amount == -800),
        ... )
        {execsql}BEGIN (implicit)
        UPDATE account_transaction SET amount=(account_transaction.amount + ?)
        WHERE ? = account_transaction.account_id AND account_transaction.amount = ?
        [...] (200, 1, -800)
        {stop}<...>

    以类似的方式，:meth:`.WriteOnlyCollection.delete` 将生成一个 DELETE 语句并以相同的方式调用::

        >>> session.execute(
        ...     existing_account.account_transactions.delete().where(
        ...         AccountTransaction.amount.between(0, 30)
        ...     ),
        ... )
        {execsql}DELETE FROM account_transaction WHERE ? = account_transaction.account_id
        AND account_transaction.amount BETWEEN ? AND ? RETURNING id
        [...] (1, 0, 30)
        <...>
        {stop}

.. tab:: 英文

    As is the case with INSERT, this feature is most straightforward with **one
    to many collections**.

    In the example below, the :meth:`.WriteOnlyCollection.update` method is used
    to generate an UPDATE statement is emitted against the elements
    in the collection, locating rows where the "amount" is equal to ``-800`` and
    adding the amount of ``200`` to them::

        >>> session.execute(
        ...     existing_account.account_transactions.update()
        ...     .values(amount=AccountTransaction.amount + 200)
        ...     .where(AccountTransaction.amount == -800),
        ... )
        {execsql}BEGIN (implicit)
        UPDATE account_transaction SET amount=(account_transaction.amount + ?)
        WHERE ? = account_transaction.account_id AND account_transaction.amount = ?
        [...] (200, 1, -800)
        {stop}<...>

    In a similar way, :meth:`.WriteOnlyCollection.delete` will produce a
    DELETE statement that is invoked in the same way::

        >>> session.execute(
        ...     existing_account.account_transactions.delete().where(
        ...         AccountTransaction.amount.between(0, 30)
        ...     ),
        ... )
        {execsql}DELETE FROM account_transaction WHERE ? = account_transaction.account_id
        AND account_transaction.amount BETWEEN ? AND ? RETURNING id
        [...] (1, 0, 30)
        <...>
        {stop}

多对多集合
^^^^^^^^^^^^^^^^^^^^^^^^

Many to Many Collections

.. tab:: 中文

    .. tip::

        这里的技术涉及多表 UPDATE 表达式，这稍微高级一些。

    对于 **多对多集合** 的批量 UPDATE 和 DELETE，为了使 UPDATE 或 DELETE 语句与父对象的主键相关，必须显式地将关联表作为 UPDATE/DELETE 语句的一部分，这需要后端支持非标准 SQL 语法，或者在构造 UPDATE 或 DELETE 语句时采取额外的显式步骤。

    对于支持多表版本的 UPDATE 的后端，:meth:`.WriteOnlyCollection.update` 方法对于多对多集合应该可以在没有额外步骤的情况下工作，如下面的示例中，对多对多 ``BankAudit.account_transactions`` 集合中的 ``AccountTransaction`` 对象进行 UPDATE 操作::

        >>> session.execute(
        ...     bank_audit.account_transactions.update().values(
        ...         description=AccountTransaction.description + " (audited)"
        ...     )
        ... )
        {execsql}UPDATE account_transaction SET description=(account_transaction.description || ?)
        FROM audit_transaction WHERE ? = audit_transaction.audit_id
        AND account_transaction.id = audit_transaction.transaction_id RETURNING id
        [...] (' (audited)', 1)
        {stop}<...>

    上述语句自动使用了“UPDATE..FROM”语法，SQLite 和其他后端支持这种语法，以在 WHERE 子句中命名额外的 ``audit_transaction`` 表。

    对于不支持多表语法的多对多集合的 UPDATE 或 DELETE，可以将多对多条件移动到 SELECT 中，例如可以与 IN 结合以匹配行。这里 :class:`.WriteOnlyCollection` 仍然能帮助我们，因为我们使用 :meth:`.WriteOnlyCollection.select` 方法为我们生成这个 SELECT，使用 :meth:`_sql.Select.with_only_columns` 方法生成一个 :term:`scalar subquery`::

        >>> from sqlalchemy import update
        >>> subq = bank_audit.account_transactions.select().with_only_columns(AccountTransaction.id)
        >>> session.execute(
        ...     update(AccountTransaction)
        ...     .values(description=AccountTransaction.description + " (audited)")
        ...     .where(AccountTransaction.id.in_(subq))
        ... )
        {execsql}UPDATE account_transaction SET description=(account_transaction.description || ?)
        WHERE account_transaction.id IN (SELECT account_transaction.id
        FROM audit_transaction
        WHERE ? = audit_transaction.audit_id AND account_transaction.id = audit_transaction.transaction_id)
        RETURNING id
        [...] (' (audited)', 1)
        <...>

.. tab:: 英文

    .. tip::

        The techniques here involve multi-table UPDATE expressions, which are
        slightly more advanced.

    For bulk UPDATE and DELETE of **many to many collections**, in order for
    an UPDATE or DELETE statement to relate to the primary key of the
    parent object, the association table must be explicitly part of the
    UPDATE/DELETE statement, which requires
    either that the backend includes supports for non-standard SQL syntaxes,
    or extra explicit steps when constructing the UPDATE or DELETE statement.

    For backends that support multi-table versions of UPDATE, the
    :meth:`.WriteOnlyCollection.update` method should work without extra steps
    for a many-to-many collection, as in the example below where an UPDATE
    is emitted against ``AccountTransaction`` objects in terms of the
    many-to-many ``BankAudit.account_transactions`` collection::

        >>> session.execute(
        ...     bank_audit.account_transactions.update().values(
        ...         description=AccountTransaction.description + " (audited)"
        ...     )
        ... )
        {execsql}UPDATE account_transaction SET description=(account_transaction.description || ?)
        FROM audit_transaction WHERE ? = audit_transaction.audit_id
        AND account_transaction.id = audit_transaction.transaction_id RETURNING id
        [...] (' (audited)', 1)
        {stop}<...>

    The above statement automatically makes use of "UPDATE..FROM" syntax,
    supported by SQLite and others, to name the additional ``audit_transaction``
    table in the WHERE clause.

    To UPDATE or DELETE a many-to-many collection where multi-table syntax is
    not available, the many-to-many criteria may be moved into SELECT that
    for example may be combined with IN to match rows.
    The :class:`.WriteOnlyCollection` still helps us here, as we use the
    :meth:`.WriteOnlyCollection.select` method to generate this SELECT for
    us, making use of the :meth:`_sql.Select.with_only_columns` method to
    produce a :term:`scalar subquery`::

        >>> from sqlalchemy import update
        >>> subq = bank_audit.account_transactions.select().with_only_columns(AccountTransaction.id)
        >>> session.execute(
        ...     update(AccountTransaction)
        ...     .values(description=AccountTransaction.description + " (audited)")
        ...     .where(AccountTransaction.id.in_(subq))
        ... )
        {execsql}UPDATE account_transaction SET description=(account_transaction.description || ?)
        WHERE account_transaction.id IN (SELECT account_transaction.id
        FROM audit_transaction
        WHERE ? = audit_transaction.audit_id AND account_transaction.id = audit_transaction.transaction_id)
        RETURNING id
        [...] (' (audited)', 1)
        <...>

只写集合 - API 文档
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Write Only Collections - API Documentation

.. autoclass:: sqlalchemy.orm.WriteOnlyCollection
    :members:
    :inherited-members:

.. autoclass:: sqlalchemy.orm.WriteOnlyMapped
    :members:

.. highlight:: python
.. doctest-disable

.. _dynamic_relationship:

动态关系加载器
----------------------------

Dynamic Relationship Loaders

.. tab:: 中文

    .. legacy::
        
        "dynamic" 懒加载策略是现在 "write_only" 策略的旧形式，详见
        :ref:`write_only_relationship` 部分。

        "dynamic" 策略从相关集合生成一个旧的 :class:`_orm.Query` 对象。
        然而，"dynamic" 关系的一个主要缺点是，有几种情况下集合会完全迭代，
        其中一些情况并不明显，只能通过逐个案例进行仔细编程和测试来防止。
        因此，对于真正的大集合管理，应优先使用 :class:`_orm.WriteOnlyCollection`。

        动态加载器也不兼容 :ref:`asyncio_toplevel` 扩展。它可以在某些限制下使用，
        如 :ref:`Asyncio dynamic guidelines <dynamic_asyncio>` 中所示，
        但再次推荐使用完全兼容 asyncio 的 :class:`_orm.WriteOnlyCollection`。

    动态关系策略允许配置一个 :func:`_orm.relationship`，当在一个实例上访问时，
    将返回一个旧的 :class:`_orm.Query` 对象代替集合。
    然后可以进一步修改 :class:`_orm.Query` 以便根据过滤条件迭代数据库集合。
    返回的 :class:`_orm.Query` 对象是 :class:`_orm.AppenderQuery` 的实例，
    它结合了 :class:`_orm.Query` 的加载和迭代行为以及基本的集合变异方法，
    如 :meth:`_orm.AppenderQuery.append` 和 :meth:`_orm.AppenderQuery.remove`。

    动态加载策略可以使用 :class:`_orm.DynamicMapped` 注释类以类型注释声明形式进行配置::

        from sqlalchemy.orm import DynamicMapped


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            posts: DynamicMapped[Post] = relationship()

    如上所述，单个 ``User`` 对象上的 ``User.posts`` 集合将返回 :class:`_orm.AppenderQuery` 对象，
    这是 :class:`_orm.Query` 的子类，还支持基本的集合变异操作::


        jack = session.get(User, id)

        # 过滤 Jack 的博客文章
        posts = jack.posts.filter(Post.headline == "this is a post")

        # 应用数组切片
        posts = jack.posts[5:20]

    动态关系支持有限的写操作，通过 :meth:`_orm.AppenderQuery.append` 和 :meth:`_orm.AppenderQuery.remove` 方法::

        oldpost = jack.posts.filter(Post.headline == "old post").one()
        jack.posts.remove(oldpost)

        jack.posts.append(Post("new post"))

    由于动态关系的读取端始终查询数据库，
    因此对底层集合的更改在数据刷新之前不会可见。
    然而，只要正在使用的 :class:`.Session` 上启用了 "autoflush"，
    这将在每次集合即将发出查询时自动发生。

.. tab:: 英文

    .. legacy::  
        
        The "dynamic" lazy loader strategy is the legacy form of what is
        now the "write_only" strategy described in the section
        :ref:`write_only_relationship`.

        The "dynamic" strategy produces a legacy :class:`_orm.Query` object from the
        related collection. However, a major drawback of "dynamic" relationships is
        that there are several cases where the collection will fully iterate, some
        of which are non-obvious, which can only be prevented with careful
        programming and testing on a case-by-case basis. Therefore, for truly large
        collection management, the :class:`_orm.WriteOnlyCollection` should be
        preferred.

        The dynamic loader is also not compatible with the :ref:`asyncio_toplevel`
        extension. It can be used with some limitations, as indicated in
        :ref:`Asyncio dynamic guidelines <dynamic_asyncio>`, but again the
        :class:`_orm.WriteOnlyCollection`, which is fully compatible with asyncio,
        should be preferred.

    The dynamic relationship strategy allows configuration of a
    :func:`_orm.relationship` which when accessed on an instance will return a
    legacy :class:`_orm.Query` object in place of the collection. The
    :class:`_orm.Query` can then be modified further so that the database
    collection may be iterated based on filtering criteria. The returned
    :class:`_orm.Query` object is an instance of :class:`_orm.AppenderQuery`, which
    combines the loading and iteration behavior of :class:`_orm.Query` along with
    rudimentary collection mutation methods such as
    :meth:`_orm.AppenderQuery.append` and :meth:`_orm.AppenderQuery.remove`.

    The "dynamic" loader strategy may be configured with
    type-annotated Declarative form using the :class:`_orm.DynamicMapped`
    annotation class::

        from sqlalchemy.orm import DynamicMapped


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            posts: DynamicMapped[Post] = relationship()

    Above, the ``User.posts`` collection on an individual ``User`` object
    will return the :class:`_orm.AppenderQuery` object, which is a subclass
    of :class:`_orm.Query` that also supports basic collection mutation
    operations::


        jack = session.get(User, id)

        # filter Jack's blog posts
        posts = jack.posts.filter(Post.headline == "this is a post")

        # apply array slices
        posts = jack.posts[5:20]

    The dynamic relationship supports limited write operations, via the
    :meth:`_orm.AppenderQuery.append` and :meth:`_orm.AppenderQuery.remove` methods::

        oldpost = jack.posts.filter(Post.headline == "old post").one()
        jack.posts.remove(oldpost)

        jack.posts.append(Post("new post"))

    Since the read side of the dynamic relationship always queries the
    database, changes to the underlying collection will not be visible
    until the data has been flushed.  However, as long as "autoflush" is
    enabled on the :class:`.Session` in use, this will occur
    automatically each time the collection is about to emit a
    query.


动态关系加载器 - API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dynamic Relationship Loaders - API

.. tab:: 中文

.. tab:: 英文

.. autoclass:: sqlalchemy.orm.AppenderQuery
    :members:
    :inherited-members: Query

.. autoclass:: sqlalchemy.orm.DynamicMapped
    :members:

.. _collections_raiseload:

设置 RaiseLoad
-----------------

Setting RaiseLoad

.. tab:: 中文

    "raise"-加载关系将在属性通常会发出延迟加载的位置引发 :exc:`~sqlalchemy.exc.InvalidRequestError`::

        class MyClass(Base):
            __tablename__ = "some_table"

            # ...

            children: Mapped[List[MyRelatedClass]] = relationship(lazy="raise")

    如上所述，如果 ``children`` 集合尚未填充，访问该属性将引发异常。 这包括读取访问，但对于集合，也会影响写入访问，因为在加载集合之前无法对其进行修改。 其原理是确保应用程序在某个上下文中不会发出任何意外的延迟加载。 不必通过读取 SQL 日志来确定是否所有必要的属性都已急切加载，“raise”策略将导致未加载的属性在访问时立即引发异常。 该 raise 策略还可使用 :func:`_orm.raiseload` 加载选项在查询选项基础上使用。

    .. seealso::

        :ref:`prevent_lazy_with_raiseload`

.. tab:: 英文

    A "raise"-loaded relationship will raise an
    :exc:`~sqlalchemy.exc.InvalidRequestError` where the attribute would normally
    emit a lazy load::

        class MyClass(Base):
            __tablename__ = "some_table"

            # ...

            children: Mapped[List[MyRelatedClass]] = relationship(lazy="raise")

    Above, attribute access on the ``children`` collection will raise an exception
    if it was not previously populated.  This includes read access but for
    collections will also affect write access, as collections can't be mutated
    without first loading them.  The rationale for this is to ensure that an
    application is not emitting any unexpected lazy loads within a certain context.
    Rather than having to read through SQL logs to determine that all necessary
    attributes were eager loaded, the "raise" strategy will cause unloaded
    attributes to raise immediately if accessed.  The raise strategy is
    also available on a query option basis using the :func:`_orm.raiseload`
    loader option.

    .. seealso::

        :ref:`prevent_lazy_with_raiseload`

使用被动删除
---------------------

Using Passive Deletes

.. tab:: 中文

    在 SQLAlchemy 中，集合管理的一个重要方面是，当引用集合的对象被删除时，SQLAlchemy 需要考虑在此集合中的对象。这些对象将需要与父对象取消关联，对于一对多集合，这意味着外键列将被设置为 NULL，或者根据 :ref:`cascade <unitofwork_cascades>` 设置，可能会发出 DELETE 以删除这些行。

    :term:`unit of work` 进程仅逐行考虑对象，这意味着 DELETE 操作意味着集合中的所有行必须在刷新过程中完全加载到内存中。这对于大集合来说是不可行的，因此我们寻求依赖数据库自身的能力，使用外键 ON DELETE 规则自动更新或删除这些行，指示工作单元无需实际加载这些行即可处理它们。可以通过在 :func:`_orm.relationship` 构造上配置 :paramref:`_orm.relationship.passive_deletes` 来指示工作单元以这种方式工作；使用的外键约束也必须正确配置。

    有关完整“被动删除”配置的更多详细信息，请参见 :ref:`passive_deletes` 部分。

.. tab:: 英文

    An important aspect of collection management in SQLAlchemy is that when an
    object that refers to a collection is deleted, SQLAlchemy needs to consider the
    objects that are inside this collection. Those objects will need to be
    de-associated from the parent, which for a one-to-many collection would mean
    that foreign key columns are set to NULL, or based on
    :ref:`cascade <unitofwork_cascades>` settings, may instead want to emit a
    DELETE for these rows.

    The :term:`unit of work` process only considers objects on a row-by-row basis,
    meaning a DELETE operation implies that all rows within a collection must be
    fully loaded into memory inside the flush process. This is not feasible for
    large collections, so we instead seek to rely upon the database's own
    capability to update or delete the rows automatically using foreign key ON
    DELETE rules, instructing the unit of work to forego actually needing to load
    these rows in order to handle them. The unit of work can be instructed to work
    in this manner by configuring :paramref:`_orm.relationship.passive_deletes` on
    the :func:`_orm.relationship` construct; the foreign key constraints in use
    must also be correctly configured.

    For further detail on a complete "passive delete" configuration, see the
    section :ref:`passive_deletes`.



