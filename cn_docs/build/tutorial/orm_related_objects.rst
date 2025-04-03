.. highlight:: pycon+sql

.. |prev| replace:: :doc:`orm_data_manipulation`
.. |next| replace:: :doc:`further_reading`

.. include:: tutorial_nav_include.rst

.. rst-class:: orm-header

.. _tutorial_orm_related_objects:

使用 ORM 相关对象
================================

Working with ORM Related Objects

.. tab:: 中文

    在本节中，我们将介绍另一个基本的 ORM 概念，即 ORM 如何与引用其他对象的映射类进行交互。在 :ref:`tutorial_declaring_mapped_classes` 部分中，映射类示例使用了一个称为 :func:`_orm.relationship` 的构造。此构造定义了两个不同的映射类之间的链接，或者从映射类到自身的链接，后者称为 **self-referential** 关系。

    为了描述 :func:`_orm.relationship` 的基本思想，首先我们将简要回顾映射，省略 :func:`_orm.mapped_column` 映射和其他指令：

    .. sourcecode:: python

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import relationship

        class User(Base):
            __tablename__ = "user_account"

            # ... mapped_column() mappings

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")

        class Address(Base):
            __tablename__ = "address"

            # ... mapped_column() mappings

            user: Mapped["User"] = relationship(back_populates="addresses")

    上面，``User`` 类现在有一个属性 ``User.addresses``， ``Address`` 类有一个属性 ``Address.user``。 :func:`_orm.relationship` 构造与 :class:`_orm.Mapped` 构造相结合以指示类型行为，将用于检查映射到 ``User`` 和 ``Address`` 类的 :class:`_schema.Table` 对象之间的表关系。由于表示 ``address`` 表的 :class:`_schema.Table` 对象具有引用 ``user_account`` 表的 :class:`_schema.ForeignKeyConstraint`，:func:`_orm.relationship` 可以明确确定从 ``User`` 类到 ``Address`` 类的 :term:`one to many` 关系，沿着 ``User.addresses`` 关系； ``user_account`` 表中的一行可能被 ``address`` 表中的多行引用。

    所有一对多关系自然地对应于相反方向的 :term:`many to one` 关系，在本例中是 ``Address.user`` 所指出的关系。:paramref:`_orm.relationship.back_populates` 参数，如上所述在指向其他名称的两个 :func:`_orm.relationship` 对象上配置，建立了这两个 :func:`_orm.relationship` 构造应被视为互补的；我们将在下一节中看到这如何发挥作用。

.. tab:: 英文

    In this section, we will cover one more essential ORM concept, which is
    how the ORM interacts with mapped classes that refer to other objects. In the
    section :ref:`tutorial_declaring_mapped_classes`, the mapped class examples
    made use of a construct called :func:`_orm.relationship`.  This construct
    defines a linkage between two different mapped classes, or from a mapped class
    to itself, the latter of which is called a **self-referential** relationship.

    To describe the basic idea of :func:`_orm.relationship`, first we'll review
    the mapping in short form, omitting the :func:`_orm.mapped_column` mappings
    and other directives:

    .. sourcecode:: python


        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import relationship


        class User(Base):
            __tablename__ = "user_account"

            # ... mapped_column() mappings

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        class Address(Base):
            __tablename__ = "address"

            # ... mapped_column() mappings

            user: Mapped["User"] = relationship(back_populates="addresses")

    Above, the ``User`` class now has an attribute ``User.addresses`` and the
    ``Address`` class has an attribute ``Address.user``.   The
    :func:`_orm.relationship` construct, in conjunction with the
    :class:`_orm.Mapped` construct to indicate typing behavior, will be used to
    inspect the table relationships between the :class:`_schema.Table` objects that
    are mapped to the ``User`` and ``Address`` classes. As the
    :class:`_schema.Table` object representing the ``address`` table has a
    :class:`_schema.ForeignKeyConstraint` which refers to the ``user_account``
    table, the :func:`_orm.relationship` can determine unambiguously that there is
    a :term:`one to many` relationship from the ``User`` class to the ``Address``
    class, along the ``User.addresses`` relationship; one particular row in the
    ``user_account`` table may be referenced by many rows in the ``address``
    table.

    All one-to-many relationships naturally correspond to a :term:`many to one`
    relationship in the other direction, in this case the one noted by
    ``Address.user``. The :paramref:`_orm.relationship.back_populates` parameter,
    seen above configured on both :func:`_orm.relationship` objects referring to
    the other name, establishes that each of these two :func:`_orm.relationship`
    constructs should be considered to be complimentary to each other; we will see
    how this plays out in the next section.


持久化和加载关系
-------------------------------------

Persisting and Loading Relationships

.. tab:: 中文

    我们可以通过实例化对象来说明 :func:`_orm.relationship` 的作用。如果我们创建一个新的 ``User`` 对象，可以注意到当我们访问 ``.addresses`` 元素时会有一个 Python 列表::

        >>> u1 = User(name="pkrabs", fullname="Pearl Krabs")
        >>> u1.addresses
        []

    这个对象是一个 SQLAlchemy 特定版本的 Python ``list``，具有跟踪和响应对其进行的更改的能力。即使我们从未将其分配给对象，当我们访问属性时，集合也会自动出现。这类似于 :ref:`tutorial_inserting_orm` 中的行为，其中观察到没有明确分配值的基于列的属性也会自动显示为 ``None``，而不是像 Python 的通常行为那样引发 ``AttributeError``。

    由于 ``u1`` 对象仍然是 :term:`transient` 的，并且我们从 ``u1.addresses`` 获得的 ``list`` 尚未发生变化（即附加或扩展），它实际上还没有与对象关联，但随着我们对其进行更改，它将成为 ``User`` 对象状态的一部分。

    该集合特定于 ``Address`` 类，这是唯一可以在其中持久保存的 Python 对象类型。使用 ``list.append()`` 方法，我们可以添加一个 ``Address`` 对象::

        >>> a1 = Address(email_address="pearl.krabs@gmail.com")
        >>> u1.addresses.append(a1)

    此时， ``u1.addresses`` 集合如预期包含新的 ``Address`` 对象::

        >>> u1.addresses
        [Address(id=None, email_address='pearl.krabs@gmail.com')]

    当我们将 ``Address`` 对象与 ``u1`` 实例的 ``User.addresses`` 集合相关联时，发生了另一种行为，即 ``User.addresses`` 关系与 ``Address.user`` 关系同步，这样我们不仅可以从 ``User`` 对象导航到 ``Address`` 对象，还可以从 ``Address`` 对象导航回“父” ``User`` 对象::

        >>> a1.user
        User(id=None, name='pkrabs', fullname='Pearl Krabs')

    这种同步是由于我们在两个 :func:`_orm.relationship` 对象之间使用 :paramref:`_orm.relationship.back_populates` 参数而发生的。此参数指定应进行互补属性分配/列表变更的另一个 :func:`_orm.relationship`。它在另一个方向上也同样有效，即如果我们创建另一个 ``Address`` 对象并将其分配给 ``Address.user`` 属性，该 ``Address`` 将成为该 ``User`` 对象上的 ``User.addresses`` 集合的一部分::

        >>> a2 = Address(email_address="pearl@aol.com", user=u1)
        >>> u1.addresses
        [Address(id=None, email_address='pearl.krabs@gmail.com'), Address(id=None, email_address='pearl@aol.com')]

    实际上，我们在 ``Address`` 构造函数中使用了 ``user`` 参数作为关键字参数，接受它就像在 ``Address`` 类上声明的任何其他映射属性一样。它相当于事实上的 ``Address.user`` 属性的赋值::

        # 等效于 a2 = Address(user=u1)
        >>> a2.user = u1

.. tab:: 英文

    We can start by illustrating what :func:`_orm.relationship` does to instances
    of objects.   If we make a new ``User`` object, we can note that there is a
    Python list when we access the ``.addresses`` element::

        >>> u1 = User(name="pkrabs", fullname="Pearl Krabs")
        >>> u1.addresses
        []

    This object is a SQLAlchemy-specific version of Python ``list`` which
    has the ability to track and respond to changes made to it.  The collection
    also appeared automatically when we accessed the attribute, even though we never assigned it to the object.
    This is similar to the behavior noted at :ref:`tutorial_inserting_orm` where
    it was observed that column-based attributes to which we don't explicitly
    assign a value also display as ``None`` automatically, rather than raising
    an ``AttributeError`` as would be Python's usual behavior.

    As the ``u1`` object is still :term:`transient` and the ``list`` that we got
    from ``u1.addresses`` has not been mutated (i.e. appended or extended), it's
    not actually associated with the object yet, but as we make changes to it,
    it will become part of the state of the ``User`` object.

    The collection is specific to the ``Address`` class which is the only type
    of Python object that may be persisted within it.  Using the ``list.append()``
    method we may add an ``Address`` object::

      >>> a1 = Address(email_address="pearl.krabs@gmail.com")
      >>> u1.addresses.append(a1)

    At this point, the ``u1.addresses`` collection as expected contains the
    new ``Address`` object::

      >>> u1.addresses
      [Address(id=None, email_address='pearl.krabs@gmail.com')]

    As we associated the ``Address`` object with the ``User.addresses`` collection
    of the ``u1`` instance, another behavior also occurred, which is that the
    ``User.addresses`` relationship synchronized itself with the ``Address.user``
    relationship, such that we can navigate not only from the ``User`` object
    to the ``Address`` object, we can also navigate from the ``Address`` object
    back to the "parent" ``User`` object::

      >>> a1.user
      User(id=None, name='pkrabs', fullname='Pearl Krabs')

    This synchronization occurred as a result of our use of the
    :paramref:`_orm.relationship.back_populates` parameter between the two
    :func:`_orm.relationship` objects.  This parameter names another
    :func:`_orm.relationship` for which complementary attribute assignment / list
    mutation should occur.   It will work equally well in the other
    direction, which is that if we create another ``Address`` object and assign
    to its ``Address.user`` attribute, that ``Address`` becomes part of the
    ``User.addresses`` collection on that ``User`` object::

      >>> a2 = Address(email_address="pearl@aol.com", user=u1)
      >>> u1.addresses
      [Address(id=None, email_address='pearl.krabs@gmail.com'), Address(id=None, email_address='pearl@aol.com')]

    We actually made use of the ``user`` parameter as a keyword argument in the
    ``Address`` constructor, which is accepted just like any other mapped attribute
    that was declared on the ``Address`` class.  It is equivalent to assignment
    of the ``Address.user`` attribute after the fact::

      # equivalent effect as a2 = Address(user=u1)
      >>> a2.user = u1


.. _tutorial_orm_cascades:

将对象级联到会话中
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Cascading Objects into the Session

.. tab:: 中文

    我们现在有一个 ``User`` 和两个 ``Address`` 对象，它们在内存中以双向结构关联，但如 :ref:`tutorial_inserting_orm` 中所述，这些对象在与 :class:`_orm.Session` 对象关联之前，处于 :term:`transient` 状态。

    我们使用仍在进行的 :class:`_orm.Session`，并注意到当我们将 :meth:`_orm.Session.add` 方法应用于主要的 ``User`` 对象时，相关的 ``Address`` 对象也会添加到同一个 :class:`_orm.Session` 中::

        >>> session.add(u1)
        >>> u1 in session
        True
        >>> a1 in session
        True
        >>> a2 in session
        True

    上述行为，即 :class:`_orm.Session` 接收到一个 ``User`` 对象，并沿着 ``User.addresses`` 关系找到相关的 ``Address`` 对象，被称为 **自级联更新(save-update cascade)**，在 ORM 参考文档 :ref:`unitofwork_cascades` 中有详细讨论。

    这三个对象现在处于 :term:`pending` 状态；这意味着它们准备好成为 INSERT 操作的主题，但尚未进行；所有三个对象都没有分配主键，此外，``a1`` 和 ``a2`` 对象有一个称为 ``user_id`` 的属性，该属性引用了具有 :class:`_schema.ForeignKeyConstraint` 的 :class:`_schema.Column`，该约束引用了 ``user_account.id`` 列；这些也为 ``None``，因为这些对象尚未与实际数据库行关联::

        >>> print(u1.id)
        None
        >>> print(a1.user_id)
        None

    在这个阶段，我们可以看到 unit of work 过程提供的巨大实用性；回想在 :ref:`tutorial_core_insert_values_clause` 部分中，使用一些复杂的语法将行插入到 ``user_account`` 和 ``address`` 表中，以便自动将 ``address.user_id`` 列与 ``user_account`` 行相关联。此外，有必要首先为 ``user_account`` 行发出 INSERT，然后是 ``address``，因为 ``address`` 中的行 **依赖** ``user_account`` 中的父行来获取其 ``user_id`` 列中的值。

    使用 :class:`_orm.Session` 时，所有这些繁琐的工作都为我们处理了，即使是最顽固的 SQL 纯粹主义者也可以从 INSERT、UPDATE 和 DELETE 语句的自动化中受益。当我们 :meth:`_orm.Session.commit` 事务时，所有步骤都按正确的顺序调用，此外，新生成的 ``user_account`` 行的主键也适当地应用于 ``address.user_id`` 列：

    .. sourcecode:: pycon+sql

        >>> session.commit()
        {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] ('pkrabs', 'Pearl Krabs')
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('pearl.krabs@gmail.com', 6)
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [insertmanyvalues 2/2 (ordered; batch not supported)] ('pearl@aol.com', 6)
        COMMIT

.. tab:: 英文

    We now have a ``User`` and two ``Address`` objects that are associated in a
    bidirectional structure
    in memory, but as noted previously in :ref:`tutorial_inserting_orm` ,
    these objects are said to be in the :term:`transient` state until they
    are associated with a :class:`_orm.Session` object.

    We make use of the :class:`_orm.Session` that's still ongoing, and note that
    when we apply the :meth:`_orm.Session.add` method to the lead ``User`` object,
    the related ``Address`` object also gets added to that same :class:`_orm.Session`::

      >>> session.add(u1)
      >>> u1 in session
      True
      >>> a1 in session
      True
      >>> a2 in session
      True

    The above behavior, where the :class:`_orm.Session` received a ``User`` object,
    and followed along the ``User.addresses`` relationship to locate a related
    ``Address`` object, is known as the **save-update cascade** and is discussed
    in detail in the ORM reference documentation at :ref:`unitofwork_cascades`.

    The three objects are now in the :term:`pending` state; this means they are
    ready to be the subject of an INSERT operation but this has not yet proceeded;
    all three objects have no primary key assigned yet, and in addition, the ``a1``
    and ``a2`` objects have an attribute called ``user_id`` which refers to the
    :class:`_schema.Column` that has a :class:`_schema.ForeignKeyConstraint`
    referring to the ``user_account.id`` column; these are also ``None`` as the
    objects are not yet associated with a real database row::

        >>> print(u1.id)
        None
        >>> print(a1.user_id)
        None

    It's at this stage that we can see the very great utility that the unit of
    work process provides; recall in the section :ref:`tutorial_core_insert_values_clause`,
    rows were inserted into the ``user_account`` and
    ``address`` tables using some elaborate syntaxes in order to automatically
    associate the ``address.user_id`` columns with those of the ``user_account``
    rows.  Additionally, it was necessary that we emit INSERT for ``user_account``
    rows first, before those of ``address``, since rows in ``address`` are
    **dependent** on their parent row in ``user_account`` for a value in their
    ``user_id`` column.

    When using the :class:`_orm.Session`, all this tedium is handled for us and
    even the most die-hard SQL purist can benefit from automation of INSERT,
    UPDATE and DELETE statements.   When we :meth:`_orm.Session.commit` the
    transaction all steps invoke in the correct order, and furthermore the
    newly generated primary key of the ``user_account`` row is applied to the
    ``address.user_id`` column appropriately:

    .. sourcecode:: pycon+sql

      >>> session.commit()
      {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?)
      [...] ('pkrabs', 'Pearl Krabs')
      INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
      [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('pearl.krabs@gmail.com', 6)
      INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
      [insertmanyvalues 2/2 (ordered; batch not supported)] ('pearl@aol.com', 6)
      COMMIT




.. _tutorial_loading_relationships:

加载关系
---------------------

Loading Relationships

.. tab:: 中文

    在最后一步中，我们调用了 :meth:`_orm.Session.commit`，它为事务发出了 COMMIT，然后根据 :paramref:`_orm.Session.commit.expire_on_commit` 使所有对象过期，以便它们在下一个事务中刷新。

    当我们下一次访问这些对象上的属性时，我们将看到为行的主要属性发出的 SELECT，例如当我们查看 ``u1`` 对象的新生成的主键时：

    .. sourcecode:: pycon+sql

      >>> u1.id
      {execsql}BEGIN (implicit)
      SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
      user_account.fullname AS user_account_fullname
      FROM user_account
      WHERE user_account.id = ?
      [...] (6,){stop}
      6

    ``u1`` ``User`` 对象现在有一个持久化集合 ``User.addresses``，我们也可以访问。由于该集合由 ``address`` 表中的另一组行组成，当我们访问该集合时，我们再次看到发出的 :term:`lazy load` 以检索对象：

    .. sourcecode:: pycon+sql

      >>> u1.addresses
      {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address,
      address.user_id AS address_user_id
      FROM address
      WHERE ? = address.user_id
      [...] (6,){stop}
      [Address(id=4, email_address='pearl.krabs@gmail.com'), Address(id=5, email_address='pearl@aol.com')]

    SQLAlchemy ORM 中的集合和相关属性在内存中是持久的；一旦集合或属性填充，SQL 将不再发出，直到该集合或属性 :term:`expired`。我们可以再次访问 ``u1.addresses`` 并添加或删除项目，这不会产生任何新的 SQL 调用::

      >>> u1.addresses
      [Address(id=4, email_address='pearl.krabs@gmail.com'), Address(id=5, email_address='pearl@aol.com')]

    虽然如果我们不采取明确步骤进行优化，lazy loading 发出的加载可能会迅速变得昂贵，但 lazy loading 网络至少经过了相当好的优化，不会执行重复工作；由于 ``u1.addresses`` 集合已刷新，根据 :term:`identity map`，这些实际上是我们已经处理的 ``a1`` 和 ``a2`` 对象的相同 ``Address`` 实例，因此我们完成了此特定对象图中所有属性的加载::

      >>> a1
      Address(id=4, email_address='pearl.krabs@gmail.com')
      >>> a2
      Address(id=5, email_address='pearl@aol.com')

    关系如何加载或不加载的问题本身就是一个完整的主题。对此概念的一些额外介绍将在本节稍后的 :ref:`tutorial_orm_loader_strategies` 中进行。

.. tab:: 英文

    In the last step, we called :meth:`_orm.Session.commit` which emitted a COMMIT
    for the transaction, and then per
    :paramref:`_orm.Session.commit.expire_on_commit` expired all objects so that
    they refresh for the next transaction.

    When we next access an attribute on these objects, we'll see the SELECT
    emitted for the primary attributes of the row, such as when we view the
    newly generated primary key for the ``u1`` object:

    .. sourcecode:: pycon+sql

      >>> u1.id
      {execsql}BEGIN (implicit)
      SELECT user_account.id AS user_account_id, user_account.name AS user_account_name,
      user_account.fullname AS user_account_fullname
      FROM user_account
      WHERE user_account.id = ?
      [...] (6,){stop}
      6

    The ``u1`` ``User`` object now has a persistent collection ``User.addresses``
    that we may also access.   As this collection consists of an additional set
    of rows from the ``address`` table, when we access this collection as well
    we again see a :term:`lazy load` emitted in order to retrieve the objects:

    .. sourcecode:: pycon+sql

      >>> u1.addresses
      {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address,
      address.user_id AS address_user_id
      FROM address
      WHERE ? = address.user_id
      [...] (6,){stop}
      [Address(id=4, email_address='pearl.krabs@gmail.com'), Address(id=5, email_address='pearl@aol.com')]

    Collections and related attributes in the SQLAlchemy ORM are persistent in
    memory; once the collection or attribute is populated, SQL is no longer emitted
    until that collection or attribute is :term:`expired`.    We may access
    ``u1.addresses`` again as well as add or remove items and this will not
    incur any new SQL calls::

      >>> u1.addresses
      [Address(id=4, email_address='pearl.krabs@gmail.com'), Address(id=5, email_address='pearl@aol.com')]

    While the loading emitted by lazy loading can quickly become expensive if
    we don't take explicit steps to optimize it, the network of lazy loading
    at least is fairly well optimized to not perform redundant work; as the
    ``u1.addresses`` collection was refreshed, per the :term:`identity map`
    these are in fact the same
    ``Address`` instances as the ``a1`` and ``a2`` objects we've been dealing with
    already, so we're done loading all attributes in this particular object
    graph::

      >>> a1
      Address(id=4, email_address='pearl.krabs@gmail.com')
      >>> a2
      Address(id=5, email_address='pearl@aol.com')

    The issue of how relationships load, or not, is an entire subject onto
    itself.  Some additional introduction to these concepts is later in this
    section at :ref:`tutorial_orm_loader_strategies`.

.. _tutorial_select_relationships:

在查询中使用关系
------------------------------

Using Relationships in Queries

.. tab:: 中文

    前一节介绍了 :func:`_orm.relationship` 构造在处理 **映射类实例(instances of a mapped class)** 时的行为，如上所示，即 ``User`` 和 ``Address`` 类的 ``u1``、 ``a1`` 和 ``a2`` 实例。在本节中，我们介绍 :func:`_orm.relationship` 在 **映射类的类级行为(class level behavior of a mapped class)** 中的应用，它在多种方式上有助于自动构建 SQL 查询。

.. tab:: 英文

    The previous section introduced the behavior of the :func:`_orm.relationship`
    construct when working with **instances of a mapped class**, above, the
    ``u1``, ``a1`` and ``a2`` instances of the ``User`` and ``Address`` classes.
    In this section, we introduce the behavior of :func:`_orm.relationship` as it
    applies to **class level behavior of a mapped class**, where it serves in
    several ways to help automate the construction of SQL queries.

.. _tutorial_joining_relationships:

使用关系进行连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Relationships to Join

.. tab:: 中文

    部分 :ref:`tutorial_select_join` 和 :ref:`tutorial_select_join_onclause` 介绍了使用 :meth:`_sql.Select.join` 和 :meth:`_sql.Select.join_from` 方法来组成 SQL JOIN 子句。为了描述表之间的连接方式，这些方法要么基于表元数据结构中链接两个表的单个明确的 :class:`_schema.ForeignKeyConstraint` 对象来推断 ON 子句，要么我们可以提供一个显式的 SQL 表达式构造来指示特定的 ON 子句。

    在使用 ORM 实体时，还有一种额外的机制可以帮助我们设置连接的 ON 子句，即使用在我们的用户映射中设置的 :func:`_orm.relationship` 对象，如 :ref:`tutorial_declaring_mapped_classes` 中所示。类绑定的对应于 :func:`_orm.relationship` 的属性可以作为 **单个参数** 传递给 :meth:`_sql.Select.join`，它用来同时表示连接的右侧和 ON 子句::

        >>> print(select(Address.email_address).select_from(User).join(User.addresses))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    如果我们不指定 ON 子句，映射上的 ORM :func:`_orm.relationship` 不会被 :meth:`_sql.Select.join` 或 :meth:`_sql.Select.join_from` 用来推断 ON 子句。这意味着，如果我们在 ``User`` 和 ``Address`` 之间没有 ON 子句的情况下连接，它之所以有效，是因为两个映射的 :class:`_schema.Table` 对象之间的 :class:`_schema.ForeignKeyConstraint`，而不是因为 ``User`` 和 ``Address`` 类上的 :func:`_orm.relationship` 对象::

        >>> print(select(Address.email_address).join_from(User, Address))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    有关如何使用带有 :func:`_orm.relationship` 构造的 :meth:`.Select.join` 和 :meth:`.Select.join_from` 的更多示例，请参见 :ref:`queryguide_toplevel` 中的部分 :ref:`orm_queryguide_joins`。

    .. seealso::

        :ref:`orm_queryguide_joins` in the :ref:`queryguide_toplevel`

.. tab:: 英文

    The sections :ref:`tutorial_select_join` and
    :ref:`tutorial_select_join_onclause` introduced the usage of the
    :meth:`_sql.Select.join` and :meth:`_sql.Select.join_from` methods to compose
    SQL JOIN clauses.   In order to describe how to join between tables, these
    methods either **infer** the ON clause based on the presence of a single
    unambiguous :class:`_schema.ForeignKeyConstraint` object within the table
    metadata structure that links the two tables, or otherwise we may provide an
    explicit SQL Expression construct that indicates a specific ON clause.

    When using ORM entities, an additional mechanism is available to help us set up
    the ON clause of a join, which is to make use of the :func:`_orm.relationship`
    objects that we set up in our user mapping, as was demonstrated at
    :ref:`tutorial_declaring_mapped_classes`. The class-bound attribute
    corresponding to the :func:`_orm.relationship` may be passed as the **single
    argument** to :meth:`_sql.Select.join`, where it serves to indicate both the
    right side of the join as well as the ON clause at once::

        >>> print(select(Address.email_address).select_from(User).join(User.addresses))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    The presence of an ORM :func:`_orm.relationship` on a mapping is not used
    by :meth:`_sql.Select.join` or :meth:`_sql.Select.join_from`
    to infer the ON clause if we don't
    specify it.  This means, if we join from ``User`` to ``Address`` without an
    ON clause, it works because of the :class:`_schema.ForeignKeyConstraint`
    between the two mapped :class:`_schema.Table` objects, not because of the
    :func:`_orm.relationship` objects on the ``User`` and ``Address`` classes::

        >>> print(select(Address.email_address).join_from(User, Address))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    See the section :ref:`orm_queryguide_joins` in the :ref:`queryguide_toplevel`
    for many more examples of how to use :meth:`.Select.join` and :meth:`.Select.join_from`
    with :func:`_orm.relationship` constructs.

    .. seealso::

        :ref:`orm_queryguide_joins` in the :ref:`queryguide_toplevel`

.. _tutorial_relationship_operators:

关系 WHERE 运算符
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Relationship WHERE Operators

.. tab:: 中文

    还有一些与 :func:`_orm.relationship` 一起提供的其他 SQL 生成助手种类，通常在构建语句的 WHERE 子句时很有用。请参阅 :ref:`queryguide_toplevel` 中的部分 :ref:`orm_queryguide_relationship_operators`。

    .. seealso::

        :ref:`queryguide_toplevel` 中的 :ref:`orm_queryguide_relationship_operators`

.. tab:: 英文

    There are some additional varieties of SQL generation helpers that come with
    :func:`_orm.relationship` which are typically useful when building up the
    WHERE clause of a statement.  See the section
    :ref:`orm_queryguide_relationship_operators` in the :ref:`queryguide_toplevel`.

    .. seealso::

        :ref:`orm_queryguide_relationship_operators` in the :ref:`queryguide_toplevel`

.. _tutorial_orm_loader_strategies:

加载器策略
-----------------

Loader Strategies

.. tab:: 中文

    在部分 :ref:`tutorial_loading_relationships` 中，我们介绍了一个概念，即当我们处理映射对象的实例时，访问默认情况下使用 :func:`_orm.relationship` 映射的属性会在集合未填充时发出一个 :term:`lazy load` 以加载应存在于该集合中的对象。

    Lazy loading 是最著名的 ORM 模式之一，也是最具争议的。当内存中的几十个 ORM 对象每个都引用少量未加载的属性时，这些对象的常规操作可能会触发许多额外的查询，最终累积起来（也称为 :term:`N plus one problem`），更糟糕的是，它们是隐式发出的。这些隐式查询可能不会被注意到，可能在尝试后由于不再有可用的数据库事务而导致错误，或者在使用替代并发模式（如 :ref:`asyncio <asyncio_toplevel>`）时，它们实际上根本不起作用。

    与此同时，当它与使用中的并发方法兼容且没有引起其他问题时，lazy loading 是一种非常流行且有用的模式。出于这些原因，SQLAlchemy 的 ORM 非常重视能够控制和优化这种加载行为。

    最重要的是，有效使用 ORM lazy loading 的第一步是 **测试应用程序，打开 SQL 回显，并观察发出的 SQL**。如果似乎有许多看起来可以更高效地合并为一个的冗余 SELECT 语句，如果在从其 :class:`_orm.Session` 中 :term:`detached` 的对象不适当地发生加载，这时就需要考虑使用 **加载器策略(loader strategies)**。

    加载器策略(loader strategies) 表示为对象，可以使用 :meth:`_sql.Select.options` 方法与 SELECT 语句关联，例如：

    .. sourcecode:: python

          for user_obj in session.execute(
              select(User).options(selectinload(User.addresses))
          ).scalars():
              user_obj.addresses  # 访问已经加载的 addresses 集合

    它们还可以使用 :paramref:`_orm.relationship.lazy` 选项作为 :func:`_orm.relationship` 的默认配置，例如：

    .. sourcecode:: python

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import relationship

        class User(Base):
            __tablename__ = "user_account"

            addresses: Mapped[List["Address"]] = relationship(
                back_populates="user", lazy="selectin"
            )

    每个 loader strategy 对象都会向声明中添加一些信息，这些信息将在 :class:`_orm.Session` 决定如何加载和/或访问各种属性时使用。

    下面的部分将介绍一些最常用的 loader strategies。

    .. seealso::

        :ref:`loading_toplevel` 中的两个部分：

        * :ref:`relationship_lazy_option` - 配置 :func:`_orm.relationship` 策略的详细信息

        * :ref:`relationship_loader_options` - 使用查询时 **加载器策略(loader strategies)** 的详细信息

.. tab:: 英文

    In the section :ref:`tutorial_loading_relationships` we introduced the concept
    that when we work with instances of mapped objects, accessing the attributes
    that are mapped using :func:`_orm.relationship` in the default case will emit
    a :term:`lazy load` when the collection is not populated in order to load
    the objects that should be present in this collection.

    Lazy loading is one of the most famous ORM patterns, and is also the one that
    is most controversial.   When several dozen ORM objects in memory each refer to
    a handful of unloaded attributes, routine manipulation of these objects can
    spin off many additional queries that can add up (otherwise known as the
    :term:`N plus one problem`), and to make matters worse they are emitted
    implicitly.    These implicit queries may not be noticed, may cause errors
    when they are attempted after there's no longer a database transaction
    available, or when using alternative concurrency patterns such as :ref:`asyncio
    <asyncio_toplevel>`, they actually won't work at all.

    At the same time, lazy loading is a vastly popular and useful pattern when it
    is compatible with the concurrency approach in use and isn't otherwise causing
    problems.   For these reasons, SQLAlchemy's ORM places a lot of emphasis on
    being able to control and optimize this loading behavior.

    Above all, the first step in using ORM lazy loading effectively is to **test
    the application, turn on SQL echoing, and watch the SQL that is emitted**. If
    there seem to be lots of redundant SELECT statements that look very much like
    they could be rolled into one much more efficiently, if there are loads
    occurring inappropriately for objects that have been :term:`detached` from
    their :class:`_orm.Session`, that's when to look into using **loader
    strategies**.

    Loader strategies are represented as objects that may be associated with a
    SELECT statement using the :meth:`_sql.Select.options` method, e.g.:

    .. sourcecode:: python

          for user_obj in session.execute(
              select(User).options(selectinload(User.addresses))
          ).scalars():
              user_obj.addresses  # access addresses collection already loaded

    They may be also configured as defaults for a :func:`_orm.relationship` using
    the :paramref:`_orm.relationship.lazy` option, e.g.:

    .. sourcecode:: python

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import relationship


        class User(Base):
            __tablename__ = "user_account"

            addresses: Mapped[List["Address"]] = relationship(
                back_populates="user", lazy="selectin"
            )

    Each loader strategy object adds some kind of information to the statement that
    will be used later by the :class:`_orm.Session` when it is deciding how various
    attributes should be loaded and/or behave when they are accessed.

    The sections below will introduce a few of the most prominently used
    loader strategies.

    .. seealso::

        Two sections in :ref:`loading_toplevel`:

        * :ref:`relationship_lazy_option` - details on configuring the strategy on :func:`_orm.relationship`

        * :ref:`relationship_loader_options` - details on using query-time loader strategies

选择加载
^^^^^^^^^^^^^

Selectin Load

.. tab:: 中文

    现代 SQLAlchemy 中最有用的加载器是 :func:`_orm.selectinload` 加载器选项。此选项解决了最常见形式的“N 加 1”问题，即一组对象引用相关集合。:func:`_orm.selectinload` 将确保特定集合针对整个对象系列在前端使用单个查询加载。它通过一种 SELECT 形式来实现这一点，在大多数情况下可以针对相关表单独发出，而无需引入 JOIN 或子查询，并且只查询那些集合尚未加载的父对象。下面我们通过加载所有 ``User`` 对象及其相关的 ``Address`` 对象来说明 :func:`_orm.selectinload`；虽然我们只调用一次 :meth:`_orm.Session.execute`，给定一个 :func:`_sql.select` 构造，但访问数据库时，实际上会发出两个 SELECT 语句，第二个用于获取相关的 ``Address`` 对象：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
        >>> for row in session.execute(stmt):
        ...     print(
        ...         f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
        ...     )
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()
        SELECT address.user_id AS address_user_id, address.id AS address_id,
        address.email_address AS address_email_address
        FROM address
        WHERE address.user_id IN (?, ?, ?, ?, ?, ?)
        [...] (1, 2, 3, 4, 5, 6){stop}
        spongebob  (spongebob@sqlalchemy.org)
        sandy  (sandy@sqlalchemy.org, sandy@squirrelpower.org)
        patrick  ()
        squidward  ()
        ehkrabs  ()
        pkrabs  (pearl.krabs@gmail.com, pearl@aol.com)

    .. seealso::

        :ref:`loading_toplevel` 中的 :ref:`selectin_eager_loading`

.. tab:: 英文

    The most useful loader in modern SQLAlchemy is the
    :func:`_orm.selectinload` loader option.  This option solves the most common
    form of the "N plus one" problem which is that of a set of objects that refer
    to related collections.   :func:`_orm.selectinload` will ensure that a particular
    collection for a full series of objects are loaded up front using a single
    query.   It does this using a SELECT form that in most cases can be emitted
    against the related table alone, without the introduction of JOINs or
    subqueries, and only queries for those parent objects for which the
    collection isn't already loaded.   Below we illustrate :func:`_orm.selectinload`
    by loading all of the ``User`` objects and all of their related ``Address``
    objects; while we invoke :meth:`_orm.Session.execute` only once, given a
    :func:`_sql.select` construct, when the database is accessed, there are
    in fact two SELECT statements emitted, the second one being to fetch the
    related ``Address`` objects:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(User).options(selectinload(User.addresses)).order_by(User.id)
        >>> for row in session.execute(stmt):
        ...     print(
        ...         f"{row.User.name}  ({', '.join(a.email_address for a in row.User.addresses)})"
        ...     )
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()
        SELECT address.user_id AS address_user_id, address.id AS address_id,
        address.email_address AS address_email_address
        FROM address
        WHERE address.user_id IN (?, ?, ?, ?, ?, ?)
        [...] (1, 2, 3, 4, 5, 6){stop}
        spongebob  (spongebob@sqlalchemy.org)
        sandy  (sandy@sqlalchemy.org, sandy@squirrelpower.org)
        patrick  ()
        squidward  ()
        ehkrabs  ()
        pkrabs  (pearl.krabs@gmail.com, pearl@aol.com)

    .. seealso::

        :ref:`selectin_eager_loading` - in :ref:`loading_toplevel`

连接加载
^^^^^^^^^^^

Joined Load

.. tab:: 中文

    :func:`_orm.joinedload` 预加载策略是 SQLAlchemy 中最早的预加载器，它通过向数据库传递的 SELECT 语句添加 JOIN（根据选项可以是外连接或内连接）来加载相关对象。

    :func:`_orm.joinedload` 策略最适合加载相关的多对一对象，因为这只需要将额外的列添加到任何情况下都会获取的主实体行中。为了提高效率，它还接受一个选项 :paramref:`_orm.joinedload.innerjoin`，以便在我们知道所有 ``Address`` 对象都有一个关联的 ``User`` 的情况下，使用内连接而不是外连接：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import joinedload
        >>> stmt = (
        ...     select(Address)
        ...     .options(joinedload(Address.user, innerjoin=True))
        ...     .order_by(Address.id)
        ... )
        >>> for row in session.execute(stmt):
        ...     print(f"{row.Address.email_address} {row.Address.user.name}")
        {execsql}SELECT address.id, address.email_address, address.user_id, user_account_1.id AS id_1,
        user_account_1.name, user_account_1.fullname
        FROM address
        JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        ORDER BY address.id
        [...] (){stop}
        spongebob@sqlalchemy.org spongebob
        sandy@sqlalchemy.org sandy
        sandy@squirrelpower.org sandy
        pearl.krabs@gmail.com pkrabs
        pearl@aol.com pkrabs

    :func:`_orm.joinedload` 也适用于集合，即一对多关系，但它具有按递归方式按相关项目成倍增加主行的效果，这使得对于嵌套集合和/或较大集合，结果集的数据量呈数量级增长，因此应根据具体情况评估其使用与 :func:`_orm.selectinload` 等其他选项的优劣。

    重要的是要注意，包含的 :class:`_sql.Select` 语句的 WHERE 和 ORDER BY 条件 **不会针对 joinedload() 渲染的表**。在上面，可以在 SQL 中看到一个 **匿名别名(anonymous alias)** 应用于 ``user_account`` 表，因此在查询中无法直接寻址。这个概念在部分 :ref:`zen_of_eager_loading` 中有更详细的讨论。

    .. tip::

      重要的是要注意，多对一预加载通常不是必需的，因为在常见情况下，“N 加 1”问题不太普遍。当许多对象都引用同一个相关对象时，例如许多 ``Address`` 对象每个都引用同一个 ``User``，SQL 只会为该 ``User`` 对象发出一次使用正常的 lazy loading。当可能时，lazy load 例程将在当前 :class:`_orm.Session` 中按主键查找相关对象，而不会发出任何 SQL。

    .. seealso::

      :ref:`loading_toplevel` 中的 :ref:`joined_eager_loading`

.. tab:: 英文

    The :func:`_orm.joinedload` eager load strategy is the oldest eager loader in
    SQLAlchemy, which augments the SELECT statement that's being passed to the
    database with a JOIN (which may be an outer or an inner join depending on options),
    which can then load in related objects.

    The :func:`_orm.joinedload` strategy is best suited towards loading
    related many-to-one objects, as this only requires that additional columns
    are added to a primary entity row that would be fetched in any case.
    For greater efficiency, it also accepts an option :paramref:`_orm.joinedload.innerjoin`
    so that an inner join instead of an outer join may be used for a case such
    as below where we know that all ``Address`` objects have an associated
    ``User``:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import joinedload
        >>> stmt = (
        ...     select(Address)
        ...     .options(joinedload(Address.user, innerjoin=True))
        ...     .order_by(Address.id)
        ... )
        >>> for row in session.execute(stmt):
        ...     print(f"{row.Address.email_address} {row.Address.user.name}")
        {execsql}SELECT address.id, address.email_address, address.user_id, user_account_1.id AS id_1,
        user_account_1.name, user_account_1.fullname
        FROM address
        JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        ORDER BY address.id
        [...] (){stop}
        spongebob@sqlalchemy.org spongebob
        sandy@sqlalchemy.org sandy
        sandy@squirrelpower.org sandy
        pearl.krabs@gmail.com pkrabs
        pearl@aol.com pkrabs

    :func:`_orm.joinedload` also works for collections, meaning one-to-many relationships,
    however it has the effect
    of multiplying out primary rows per related item in a recursive way
    that grows the amount of data sent for a result set by orders of magnitude for
    nested collections and/or larger collections, so its use vs. another option
    such as :func:`_orm.selectinload` should be evaluated on a per-case basis.

    It's important to note that the WHERE and ORDER BY criteria of the enclosing
    :class:`_sql.Select` statement **do not target the table rendered by
    joinedload()**.   Above, it can be seen in the SQL that an **anonymous alias**
    is applied to the ``user_account`` table such that is not directly addressable
    in the query.   This concept is discussed in more detail in the section
    :ref:`zen_of_eager_loading`.


    .. tip::

      It's important to note that many-to-one eager loads are often not necessary,
      as the "N plus one" problem is much less prevalent in the common case. When
      many objects all refer to the same related object, such as many ``Address``
      objects that each refer to the same ``User``, SQL will be emitted only once
      for that ``User`` object using normal lazy loading.  The lazy load routine
      will look up the related object by primary key in the current
      :class:`_orm.Session` without emitting any SQL when possible.


    .. seealso::

      :ref:`joined_eager_loading` - in :ref:`loading_toplevel`

.. _tutorial_orm_loader_strategies_contains_eager:

显式连接 + 预加载
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Explicit Join + Eager load

.. tab:: 中文

    如果我们在连接到 ``user_account`` 表时使用诸如 :meth:`_sql.Select.join` 之类的方法来呈现 JOIN，我们还可以利用该 JOIN 来急切加载每个返回的 ``Address`` 对象上的 ``Address.user`` 属性的内容。这本质上是我们使用“连接预加载”但自己呈现 JOIN。通过使用 :func:`_orm.contains_eager` 选项可以实现这种常见的用例。此选项与 :func:`_orm.joinedload` 非常相似，只是它假设我们已经设置好了 JOIN，并且它只指示应将 COLUMNS 子句中的其他列加载到每个返回对象的相关属性中，例如：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import contains_eager
        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "pkrabs")
        ...     .options(contains_eager(Address.user))
        ...     .order_by(Address.id)
        ... )
        >>> for row in session.execute(stmt):
        ...     print(f"{row.Address.email_address} {row.Address.user.name}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.email_address, address.user_id
        FROM address JOIN user_account ON user_account.id = address.user_id
        WHERE user_account.name = ? ORDER BY address.id
        [...] ('pkrabs',){stop}
        pearl.krabs@gmail.com pkrabs
        pearl@aol.com pkrabs

    上面，我们既过滤了 ``user_account.name`` 上的行，还将 ``user_account`` 中的行加载到返回行的 ``Address.user`` 属性中。如果我们分别应用 :func:`_orm.joinedload`，我们会得到一个不必要地连接两次的 SQL 查询：

        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "pkrabs")
        ...     .options(joinedload(Address.user))
        ...     .order_by(Address.id)
        ... )
        >>> print(stmt)  # SELECT 不必要地有一个 JOIN 和 LEFT OUTER JOIN
        {printsql}SELECT address.id, address.email_address, address.user_id,
        user_account_1.id AS id_1, user_account_1.name, user_account_1.fullname
        FROM address JOIN user_account ON user_account.id = address.user_id
        LEFT OUTER JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        WHERE user_account.name = :name_1 ORDER BY address.id

    .. seealso::

        :ref:`loading_toplevel` 中的两个部分：

        * :ref:`zen_of_eager_loading` - 详细描述了上述问题

        * :ref:`contains_eager` - 使用 :func:`.contains_eager`

.. tab:: 英文

    If we were to load ``Address`` rows while joining to the ``user_account`` table
    using a method such as :meth:`_sql.Select.join` to render the JOIN, we could
    also leverage that JOIN in order to eagerly load the contents of the
    ``Address.user`` attribute on each ``Address`` object returned.  This is
    essentially that we are using "joined eager loading" but rendering the JOIN
    ourselves.   This common use case is achieved by using the
    :func:`_orm.contains_eager` option. This option is very similar to
    :func:`_orm.joinedload`, except that it assumes we have set up the JOIN
    ourselves, and it instead only indicates that additional columns in the COLUMNS
    clause should be loaded into related attributes on each returned object, for
    example:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import contains_eager
        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "pkrabs")
        ...     .options(contains_eager(Address.user))
        ...     .order_by(Address.id)
        ... )
        >>> for row in session.execute(stmt):
        ...     print(f"{row.Address.email_address} {row.Address.user.name}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.email_address, address.user_id
        FROM address JOIN user_account ON user_account.id = address.user_id
        WHERE user_account.name = ? ORDER BY address.id
        [...] ('pkrabs',){stop}
        pearl.krabs@gmail.com pkrabs
        pearl@aol.com pkrabs

    Above, we both filtered the rows on ``user_account.name`` and also loaded
    rows from ``user_account`` into the ``Address.user`` attribute of the returned
    rows.   If we had applied :func:`_orm.joinedload` separately, we would get a
    SQL query that unnecessarily joins twice::

        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "pkrabs")
        ...     .options(joinedload(Address.user))
        ...     .order_by(Address.id)
        ... )
        >>> print(stmt)  # SELECT has a JOIN and LEFT OUTER JOIN unnecessarily
        {printsql}SELECT address.id, address.email_address, address.user_id,
        user_account_1.id AS id_1, user_account_1.name, user_account_1.fullname
        FROM address JOIN user_account ON user_account.id = address.user_id
        LEFT OUTER JOIN user_account AS user_account_1 ON user_account_1.id = address.user_id
        WHERE user_account.name = :name_1 ORDER BY address.id

    .. seealso::

        Two sections in :ref:`loading_toplevel`:

        * :ref:`zen_of_eager_loading` - describes the above problem in detail

        * :ref:`contains_eager` - using :func:`.contains_eager`


提升加载
^^^^^^^^^

Raiseload

.. tab:: 中文

    另一个值得一提的加载策略是 :func:`_orm.raiseload`。此选项用于完全阻止应用程序遇到 :term:`N plus one` 问题，通过导致通常会进行的懒加载(lazy load)改为引发错误来实现。它有两个变体，通过 :paramref:`_orm.raiseload.sql_only` 选项控制，分别阻止需要 SQL 的 懒加载(lazy loads) 和所有“加载”操作，包括仅需查询当前 :class:`_orm.Session` 的操作。

    使用 :func:`_orm.raiseload` 的一种方法是将其配置在 :func:`_orm.relationship` 本身上，通过将 :paramref:`_orm.relationship.lazy` 设置为 ``"raise_on_sql"``，使得对于特定映射，某个关系永远不会尝试发出 SQL：

    .. setup code

        >>> class Base(DeclarativeBase):
        ...     pass

    ::

        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import relationship


        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     addresses: Mapped[List["Address"]] = relationship(
        ...         back_populates="user", lazy="raise_on_sql"
        ...     )


        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     user: Mapped["User"] = relationship(back_populates="addresses", lazy="raise_on_sql")

    使用这种映射，应用程序被阻止 lazy loading，表明特定查询需要指定加载策略：

        >>> u1 = session.execute(select(User)).scalars().first()
        {execsql}SELECT user_account.id FROM user_account
        [...] ()
        {stop}>>> u1.addresses
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'User.addresses' is not available due to lazy='raise_on_sql'

    该异常表明应提前加载该集合：

        >>> u1 = (
        ...     session.execute(select(User).options(selectinload(User.addresses)))
        ...     .scalars()
        ...     .first()
        ... )
        {execsql}SELECT user_account.id
        FROM user_account
        [...] ()
        SELECT address.user_id AS address_user_id, address.id AS address_id
        FROM address
        WHERE address.user_id IN (?, ?, ?, ?, ?, ?)
        [...] (1, 2, 3, 4, 5, 6)

    ``lazy="raise_on_sql"`` 选项对于多对一关系也尽量智能化；如上所述，如果 ``Address`` 对象的 ``Address.user`` 属性未加载，但该 ``User`` 对象在同一 :class:`_orm.Session` 中本地存在，“raiseload” 策略不会引发错误。

    .. seealso::

        :ref:`loading_toplevel` 中的 :ref:`prevent_lazy_with_raiseload`

.. tab:: 英文

    One additional loader strategy worth mentioning is :func:`_orm.raiseload`.
    This option is used to completely block an application from having the
    :term:`N plus one` problem at all by causing what would normally be a lazy
    load to raise an error instead.   It has two variants that are controlled via
    the :paramref:`_orm.raiseload.sql_only` option to block either lazy loads
    that require SQL, versus all "load" operations including those which
    only need to consult the current :class:`_orm.Session`.

    One way to use :func:`_orm.raiseload` is to configure it on
    :func:`_orm.relationship` itself, by setting :paramref:`_orm.relationship.lazy`
    to the value ``"raise_on_sql"``, so that for a particular mapping, a certain
    relationship will never try to emit SQL:

    .. setup code

        >>> class Base(DeclarativeBase):
        ...     pass

    ::

        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import relationship


        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     addresses: Mapped[List["Address"]] = relationship(
        ...         back_populates="user", lazy="raise_on_sql"
        ...     )


        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     user: Mapped["User"] = relationship(back_populates="addresses", lazy="raise_on_sql")

    Using such a mapping, the application is blocked from lazy loading,
    indicating that a particular query would need to specify a loader strategy::

        >>> u1 = session.execute(select(User)).scalars().first()
        {execsql}SELECT user_account.id FROM user_account
        [...] ()
        {stop}>>> u1.addresses
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'User.addresses' is not available due to lazy='raise_on_sql'


    The exception would indicate that this collection should be loaded up front
    instead::

        >>> u1 = (
        ...     session.execute(select(User).options(selectinload(User.addresses)))
        ...     .scalars()
        ...     .first()
        ... )
        {execsql}SELECT user_account.id
        FROM user_account
        [...] ()
        SELECT address.user_id AS address_user_id, address.id AS address_id
        FROM address
        WHERE address.user_id IN (?, ?, ?, ?, ?, ?)
        [...] (1, 2, 3, 4, 5, 6)

    The ``lazy="raise_on_sql"`` option tries to be smart about many-to-one
    relationships as well; above, if the ``Address.user`` attribute of an
    ``Address`` object were not loaded, but that ``User`` object were locally
    present in the same :class:`_orm.Session`, the "raiseload" strategy would not
    raise an error.

    .. seealso::

        :ref:`prevent_lazy_with_raiseload` - in :ref:`loading_toplevel`

