========================
非传统映射
========================

Non-Traditional Mappings

.. _orm_mapping_joins:

.. _maptojoin:

将一个类映射到多个表
=======================================

Mapping a Class against Multiple Tables

.. tab:: 中文

    映射器可以针对除普通表之外的任意关系单元（称为 *selectables* ）构造。例如，:func:`_expression.join` 函数创建一个由多个表组成的可选择单元，具有其自己的复合主键，可以像 :class:`_schema.Table` 一样进行映射::

        from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import column_property

        metadata_obj = MetaData()

        # 定义两个 Table 对象
        user_table = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String),
        )

        address_table = Table(
            "address",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.id")),
            Column("email_address", String),
        )

        # 定义它们之间的连接
        user_address_join = join(user_table, address_table)


        class Base(DeclarativeBase):
            metadata = metadata_obj


        # 映射到它
        class AddressUser(Base):
            __table__ = user_address_join

            id = column_property(user_table.c.id, address_table.c.user_id)
            address_id = address_table.c.id

    在上面的示例中，连接表示了 ``user`` 和 ``address`` 表的列。 ``user.id`` 和 ``address.user_id`` 列通过外键等同，因此在映射中它们被定义为一个属性 ``AddressUser.id``，使用 :func:`.column_property` 来指示专门的列映射。基于这个配置部分，在刷新时映射将把新的主键值从 ``user.id`` 复制到 ``address.user_id`` 列。

    此外， ``address.id`` 列被明确映射到名为 ``address_id`` 的属性。这是为了 **消除歧义**，即将 ``address.id`` 列的映射与同名的 ``AddressUser.id`` 属性区分开来，这里已被分配为引用 ``user`` 表和 ``address.user_id`` 外键组合的列。

    上述映射的自然主键是 ``(user.id, address.id)`` 的复合键，因为这些是 ``user`` 和 ``address`` 表组合在一起的主键列。 ``AddressUser`` 对象的标识将以这两个值表示，并通过 ``AddressUser`` 对象表示为 ``(AddressUser.id, AddressUser.address_id)``。

    在引用 ``AddressUser.id`` 列时，大多数 SQL 表达式将仅使用映射列列表中的第一列，因为这两列是同义的。然而，对于特殊用例，例如 GROUP BY 表达式，必须同时引用两列并使用适当的上下文，例如处理别名等，可以使用访问器 :attr:`.ColumnProperty.Comparator.expressions`::

        stmt = select(AddressUser).group_by(*AddressUser.id.expressions)

    .. note::

        如上所示的针对多个表的映射支持持久性，即在目标表中插入、更新和删除行。然而，它不支持同时对一个记录执行 UPDATE 一个表并对其他表执行 INSERT 或 DELETE 的操作。也就是说，如果记录 PtoQ 映射到表“p”和“q”，并且它基于“p”和“q”的 LEFT OUTER JOIN 有一行，如果进行的 UPDATE 是要更改现有记录中“q”表的数据，则“q”表中的行必须存在；如果主键标识已存在，它不会发出 INSERT。如果行不存在，对于大多数支持报告 UPDATE 影响的行数的 DBAPI 驱动程序，ORM 将无法检测到更新的行并引发错误；否则，数据将被默默忽略。

        一个允许动态“插入”相关行的配方可能使用 :attr:`.MapperEvents.before_update` 事件，如下所示::

            from sqlalchemy import event


            @event.listens_for(PtoQ, "before_update")
            def receive_before_update(mapper, connection, target):
                if target.some_required_attr_on_q is None:
                    connection.execute(q_table.insert(), {"id": target.id})

        在上面，通过使用 :meth:`_schema.Table.insert` 创建 INSERT 构造并使用用于发出刷新过程其他 SQL 的 :class:`_engine.Connection` 来执行它，向 ``q_table`` 表插入了一行。用户提供的逻辑必须检测到从“p”到“q”的 LEFT OUTER JOIN 在“q”端没有条目。

.. tab:: 英文

    Mappers can be constructed against arbitrary relational units (called
    *selectables*) in addition to plain tables. For example, the :func:`_expression.join`
    function creates a selectable unit comprised of
    multiple tables, complete with its own composite primary key, which can be
    mapped in the same way as a :class:`_schema.Table`::

        from sqlalchemy import Table, Column, Integer, String, MetaData, join, ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import column_property

        metadata_obj = MetaData()

        # define two Table objects
        user_table = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String),
        )

        address_table = Table(
            "address",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.id")),
            Column("email_address", String),
        )

        # define a join between them.  This
        # takes place across the user.id and address.user_id
        # columns.
        user_address_join = join(user_table, address_table)


        class Base(DeclarativeBase):
            metadata = metadata_obj


        # map to it
        class AddressUser(Base):
            __table__ = user_address_join

            id = column_property(user_table.c.id, address_table.c.user_id)
            address_id = address_table.c.id

    In the example above, the join expresses columns for both the
    ``user`` and the ``address`` table.  The ``user.id`` and ``address.user_id``
    columns are equated by foreign key, so in the mapping they are defined
    as one attribute, ``AddressUser.id``, using :func:`.column_property` to
    indicate a specialized column mapping.   Based on this part of the
    configuration, the mapping will copy
    new primary key values from ``user.id`` into the ``address.user_id`` column
    when a flush occurs.

    Additionally, the ``address.id`` column is mapped explicitly to
    an attribute named ``address_id``.   This is to **disambiguate** the
    mapping of the ``address.id`` column from the same-named ``AddressUser.id``
    attribute, which here has been assigned to refer to the ``user`` table
    combined with the ``address.user_id`` foreign key.

    The natural primary key of the above mapping is the composite of
    ``(user.id, address.id)``, as these are the primary key columns of the
    ``user`` and ``address`` table combined together.  The identity of an
    ``AddressUser`` object will be in terms of these two values, and
    is represented from an ``AddressUser`` object as
    ``(AddressUser.id, AddressUser.address_id)``.

    When referring to the ``AddressUser.id`` column, most SQL expressions will
    make use of only the first column in the list of columns mapped, as the
    two columns are synonymous.  However, for the special use case such as
    a GROUP BY expression where both columns must be referenced at the same
    time while making use of the proper context, that is, accommodating for
    aliases and similar, the accessor :attr:`.ColumnProperty.Comparator.expressions`
    may be used::

        stmt = select(AddressUser).group_by(*AddressUser.id.expressions)

    .. note::

        A mapping against multiple tables as illustrated above supports
        persistence, that is, INSERT, UPDATE and DELETE of rows within the targeted
        tables. However, it does not support an operation that would UPDATE one
        table and perform INSERT or DELETE on others at the same time for one
        record. That is, if a record PtoQ is mapped to tables “p” and “q”, where it
        has a row based on a LEFT OUTER JOIN of “p” and “q”, if an UPDATE proceeds
        that is to alter data in the “q” table in an existing record, the row in
        “q” must exist; it won’t emit an INSERT if the primary key identity is
        already present.  If the row does not exist, for most DBAPI drivers which
        support reporting the number of rows affected by an UPDATE, the ORM will
        fail to detect an updated row and raise an error; otherwise, the data
        would be silently ignored.

        A recipe to allow for an on-the-fly “insert” of the related row might make
        use of the :attr:`.MapperEvents.before_update` event and look like::

            from sqlalchemy import event


            @event.listens_for(PtoQ, "before_update")
            def receive_before_update(mapper, connection, target):
                if target.some_required_attr_on_q is None:
                    connection.execute(q_table.insert(), {"id": target.id})

        where above, a row is INSERTed into the ``q_table`` table by creating an
        INSERT construct with :meth:`_schema.Table.insert`, then executing it  using the
        given :class:`_engine.Connection` which is the same one being used to emit other
        SQL for the flush process.   The user-supplied logic would have to detect
        that the LEFT OUTER JOIN from "p" to "q" does not have an entry for the "q"
        side.

.. _orm_mapping_arbitrary_subqueries:

将一个类映射到任意子查询
============================================

Mapping a Class against Arbitrary Subqueries

.. tab:: 中文

    类似于针对连接的映射，也可以使用 :func:`_expression.select` 对象进行映射。下面的示例片段展示了将名为 ``Customer`` 的类映射到包含连接到子查询的 :func:`_expression.select`::

        from sqlalchemy import select, func

        subq = (
            select(
                func.count(orders.c.id).label("order_count"),
                func.max(orders.c.price).label("highest_order"),
                orders.c.customer_id,
            )
            .group_by(orders.c.customer_id)
            .subquery()
        )

        customer_select = (
            select(customers, subq)
            .join_from(customers, subq, customers.c.id == subq.c.customer_id)
            .subquery()
        )


        class Customer(Base):
            __table__ = customer_select

    在上面，由 ``customer_select`` 表示的完整行将是 ``customers`` 表的所有列，此外还有 ``subq`` 子查询公开的列，这些列是 ``order_count``、 ``highest_order`` 和 ``customer_id``。将 ``Customer`` 类映射到这个可选项然后创建一个包含这些属性的类。

    当 ORM 持久化 ``Customer`` 的新实例时，只有 ``customers`` 表实际上会接收一个 INSERT。这是因为 ``orders`` 表的主键未在映射中表示；ORM 只会向其映射了主键的表发出 INSERT。

    .. note::

        映射到任意 SELECT 语句，尤其是上述复杂语句的做法几乎从未需要；它必然会产生复杂的查询，这些查询通常不如直接查询构造高效。这种做法在一定程度上基于 SQLAlchemy 的早期历史，当时 :class:`_orm.Mapper` 构造被认为是主要的查询接口；在现代用法中，可以使用 :class:`_query.Query` 对象构造几乎任何 SELECT 语句，包括复杂的复合语句，应该优先于“映射到可选项”方法。

.. tab:: 英文

    Similar to mapping against a join, a plain :func:`_expression.select` object
    can be used with a mapper as well.  The example fragment below illustrates
    mapping a class called ``Customer`` to a :func:`_expression.select` which
    includes a join to a subquery::

        from sqlalchemy import select, func

        subq = (
            select(
                func.count(orders.c.id).label("order_count"),
                func.max(orders.c.price).label("highest_order"),
                orders.c.customer_id,
            )
            .group_by(orders.c.customer_id)
            .subquery()
        )

        customer_select = (
            select(customers, subq)
            .join_from(customers, subq, customers.c.id == subq.c.customer_id)
            .subquery()
        )


        class Customer(Base):
            __table__ = customer_select

    Above, the full row represented by ``customer_select`` will be all the
    columns of the ``customers`` table, in addition to those columns
    exposed by the ``subq`` subquery, which are ``order_count``,
    ``highest_order``, and ``customer_id``.  Mapping the ``Customer``
    class to this selectable then creates a class which will contain
    those attributes.

    When the ORM persists new instances of ``Customer``, only the
    ``customers`` table will actually receive an INSERT.  This is because the
    primary key of the ``orders`` table is not represented in the mapping;  the ORM
    will only emit an INSERT into a table for which it has mapped the primary
    key.

    .. note::

        The practice of mapping to arbitrary SELECT statements, especially
        complex ones as above, is
        almost never needed; it necessarily tends to produce complex queries
        which are often less efficient than that which would be produced
        by direct query construction.   The practice is to some degree
        based on the very early history of SQLAlchemy where the :class:`_orm.Mapper`
        construct was meant to represent the primary querying interface;
        in modern usage, the :class:`_query.Query` object can be used to construct
        virtually any SELECT statement, including complex composites, and should
        be favored over the "map-to-selectable" approach.

一个类的多个映射器
==============================

Multiple Mappers for One Class

.. tab:: 中文

    在现代 SQLAlchemy 中，一个特定类一次只能由一个所谓的 **primary** 映射器映射。这个映射器涉及三个主要功能领域：查询、持久化和映射类的仪器化。primary 映射器的基本原理与 :class:`_orm.Mapper` 修改类本身的事实有关，不仅将其持久化到特定的 :class:`_schema.Table`，还在类上 :term:`instrumenting` 属性，这些属性根据表元数据专门结构化。由于只有一个映射器可以实际对类进行仪器化，因此不可能有多个映射器以相同的程度与一个类关联。

    “非 primary” 映射器的概念在 SQLAlchemy 的许多版本中存在，但从 1.3 版本开始，这个功能被弃用了。唯一有用的情况是构造一个关系，以针对备用可选项的类。这个用例现在适合使用 :class:`.aliased` 构造，并在 :ref:`relationship_aliased_class` 中进行了描述。

    至于一个类可以在不同情况下完全持久化到不同表的用例，早期版本的 SQLAlchemy 提供了从 Hibernate 适配的功能，称为“实体名称”功能。然而，一旦映射类本身成为 SQL 表达式构造的来源，这个用例在 SQLAlchemy 中变得不可行；也就是说，类的属性本身直接链接到映射的表列。该功能被删除并替换为一种简单的配方导向方法来完成这项任务，而没有任何仪器化的歧义 - 创建新的子类，每个子类单独映射。这种模式现在作为一个配方在 `Entity Name <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/EntityName>`_ 中提供。

.. tab:: 英文

    In modern SQLAlchemy, a particular class is mapped by only one so-called
    **primary** mapper at a time.   This mapper is involved in three main areas of
    functionality: querying, persistence, and instrumentation of the mapped class.
    The rationale of the primary mapper relates to the fact that the
    :class:`_orm.Mapper` modifies the class itself, not only persisting it towards a
    particular :class:`_schema.Table`, but also :term:`instrumenting` attributes upon the
    class which are structured specifically according to the table metadata.   It's
    not possible for more than one mapper to be associated with a class in equal
    measure, since only one mapper can actually instrument the class.

    The concept of a "non-primary" mapper had existed for many versions of
    SQLAlchemy however as of version 1.3 this feature is deprecated.   The
    one case where such a non-primary mapper is useful is when constructing
    a relationship to a class against an alternative selectable.   This
    use case is now suited using the :class:`.aliased` construct and is described
    at :ref:`relationship_aliased_class`.

    As far as the use case of a class that can actually be fully persisted
    to different tables under different scenarios, very early versions of
    SQLAlchemy offered a feature for this adapted from Hibernate, known
    as the "entity name" feature.  However, this use case became infeasible
    within SQLAlchemy once the mapped class itself became the source of SQL
    expression construction; that is, the class' attributes themselves link
    directly to mapped table columns.   The feature was removed and replaced
    with a simple recipe-oriented approach to accomplishing this task
    without any ambiguity of instrumentation - to create new subclasses, each
    mapped individually.  This pattern is now available as a recipe at `Entity Name
    <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/EntityName>`_.

