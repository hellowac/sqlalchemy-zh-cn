ORM 配置
=================

ORM Configuration

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _faq_mapper_primary_key:

如何映射没有主键的表？
---------------------------------------------

How do I map a table that has no primary key?

.. tab:: 中文
    
    为了将 ORM 映射到某个特定的数据表，SQLAlchemy 需要至少有一列被标记为主键列；当然，也完全支持多列组成的复合主键。这些列 **不必** 在数据库中实际被定义为主键列，尽管建议这样做。关键在于这些列的行为 *表现得* 像主键，比如它们是唯一且不可为空的，用于标识某一行数据。
    
    大多数 ORM 框架都要求定义某种形式的主键，因为内存中的对象必须能够对应到数据库表中的唯一一行；至少，这使得我们可以使用 UPDATE 和 DELETE 语句仅针对该对象所对应的行操作，不影响其他行。然而，主键的重要性远不止于此。在 SQLAlchemy 中，所有 ORM 映射对象在任何时候都通过一种称为 :term:`identity map` 的模式在 :class:`.Session` 中唯一地与它们对应的数据库行关联。这种模式是 SQLAlchemy 所采用的工作单元（unit of work）机制的核心，同时也是 ORM 使用中常见（或不那么常见）用法的基础。
    
    .. note::
    
        需要注意的是，这里讨论的仅是 SQLAlchemy ORM；如果应用是基于 Core 构建的，仅使用 :class:`_schema.Table` 对象、:func:`_expression.select` 构造等内容， **则不需要** 表中存在或关联任何主键（尽管在 SQL 层面上，所有表 **都应该** 定义某种主键，否则你将无法安全地更新或删除特定行）。
    
    几乎在所有情况下，一个表都会拥有所谓的 :term:`候选键 <candidate key>`，即一列或多列能唯一标识某一行。如果表真的没有这样的列，并且存在完全重复的行，那么它就不符合“第一范式”（ `first normal form <https://en.wikipedia.org/wiki/First_normal_form>`_ ），此时是无法进行 ORM 映射的。否则，可以将构成最佳候选键的列直接应用到映射器中::
    
        class SomeClass(Base):
            __table__ = some_table_with_no_pk
            __mapper_args__ = {
                "primary_key": [some_table_with_no_pk.c.uid, some_table_with_no_pk.c.bar]
            }
    
    更好的方式是在完整声明表元数据时，使用 ``primary_key=True`` 标志：
    
        class SomeClass(Base):
            __tablename__ = "some_table_with_no_pk"
    
            uid = Column(Integer, primary_key=True)
            bar = Column(String, primary_key=True)
    
    所有关系型数据库中的表都应有主键。即便是多对多关联表，其主键通常由两列外键组成的复合键构成：
    
    .. sourcecode:: sql
    
        CREATE TABLE my_association (
          user_id INTEGER REFERENCES user(id),
          account_id INTEGER REFERENCES account(id),
          PRIMARY KEY (user_id, account_id)
        )

.. tab:: 英文

    The SQLAlchemy ORM, in order to map to a particular table, needs there to be
    at least one column denoted as a primary key column; multiple-column,
    i.e. composite, primary keys are of course entirely feasible as well.  These
    columns do **not** need to be actually known to the database as primary key
    columns, though it's a good idea that they are.  It's only necessary that the columns
    *behave* as a primary key does, e.g. as a unique and not nullable identifier
    for a row.

    Most ORMs require that objects have some kind of primary key defined
    because the object in memory must correspond to a uniquely identifiable
    row in the database table; at the very least, this allows the
    object can be targeted for UPDATE and DELETE statements which will affect only
    that object's row and no other.   However, the importance of the primary key
    goes far beyond that.  In SQLAlchemy, all ORM-mapped objects are at all times
    linked uniquely within a :class:`.Session`
    to their specific database row using a pattern called the :term:`identity map`,
    a pattern that's central to the unit of work system employed by SQLAlchemy,
    and is also key to the most common (and not-so-common) patterns of ORM usage.


    .. note::

        It's important to note that we're only talking about the SQLAlchemy ORM; an
        application which builds on Core and deals only with :class:`_schema.Table` objects,
        :func:`_expression.select` constructs and the like, **does not** need any primary key
        to be present on or associated with a table in any way (though again, in SQL, all tables
        should really have some kind of primary key, lest you need to actually
        update or delete specific rows).

    In almost all cases, a table does have a so-called :term:`candidate key`, which is a column or series
    of columns that uniquely identify a row.  If a table truly doesn't have this, and has actual
    fully duplicate rows, the table is not corresponding to `first normal form <https://en.wikipedia.org/wiki/First_normal_form>`_ and cannot be mapped.   Otherwise, whatever columns comprise the best candidate key can be
    applied directly to the mapper::

        class SomeClass(Base):
            __table__ = some_table_with_no_pk
            __mapper_args__ = {
                "primary_key": [some_table_with_no_pk.c.uid, some_table_with_no_pk.c.bar]
            }

    Better yet is when using fully declared table metadata, use the ``primary_key=True``
    flag on those columns::

        class SomeClass(Base):
            __tablename__ = "some_table_with_no_pk"

            uid = Column(Integer, primary_key=True)
            bar = Column(String, primary_key=True)

    All tables in a relational database should have primary keys.   Even a many-to-many
    association table - the primary key would be the composite of the two association
    columns:

    .. sourcecode:: sql

        CREATE TABLE my_association (
        user_id INTEGER REFERENCES user(id),
        account_id INTEGER REFERENCES account(id),
        PRIMARY KEY (user_id, account_id)
        )


如何配置 Python 保留字或类似字的列？
----------------------------------------------------------------------

How do I configure a Column that is a Python reserved word or similar?

.. tab:: 中文

    基于列的属性可以在映射中指定任何所需的名称。请参阅:ref:`mapper_column_distinct_names`。

.. tab:: 英文

    Column-based attributes can be given any name desired in the mapping. See :ref:`mapper_column_distinct_names`.

给定映射类，如何获取所有列、关系、映射属性等的列表？
-------------------------------------------------------------------------------------------------

How do I get a list of all columns, relationships, mapped attributes, etc. given a mapped class?

.. tab:: 中文

    这些信息都可以通过 :class:`_orm.Mapper` 对象获取。
    
    若要获取某个已映射类的 :class:`_orm.Mapper`，可以对该类调用 :func:`_sa.inspect` 函数::
    
        from sqlalchemy import inspect
    
        mapper = inspect(MyClass)
    
    然后，可以通过以下属性访问该类的所有映射信息：
    
    * :attr:`_orm.Mapper.attrs` —— 所有映射属性的命名空间。这些属性本身是 :class:`.MapperProperty` 的实例，其中包含进一步指向已映射 SQL 表达式或列的属性（如果适用）。
    
    * :attr:`_orm.Mapper.column_attrs` —— 仅包含列与 SQL 表达式属性的命名空间。你也可以使用 :attr:`_orm.Mapper.columns` 直接访问 :class:`_schema.Column` 对象。
    
    * :attr:`_orm.Mapper.relationships` —— 所有 :class:`.RelationshipProperty` 属性的命名空间。
    
    * :attr:`_orm.Mapper.all_orm_descriptors` —— 所有映射属性的命名空间，同时包含通过 :class:`.hybrid_property`、:class:`.AssociationProxy` 等系统定义的用户自定义属性。
    
    * :attr:`_orm.Mapper.columns` —— 包含 :class:`_schema.Column` 对象和其他与该映射关联的命名 SQL 表达式的命名空间。
    
    * :attr:`_orm.Mapper.persist_selectable` —— 当前映射器映射到的 :class:`_schema.Table` 或其他可选对象。
    
    * :attr:`_orm.Mapper.local_table` —— 对该映射器“本地”的 :class:`_schema.Table`；在使用继承映射到一个组合 selectables 时，它与 :attr:`_orm.Mapper.persist_selectable` 不同。

.. tab:: 英文
    
    This information is all available from the :class:`_orm.Mapper` object.
    
    To get at the :class:`_orm.Mapper` for a particular mapped class, call the
    :func:`_sa.inspect` function on it::
    
        from sqlalchemy import inspect
    
        mapper = inspect(MyClass)
    
    From there, all information about the class can be accessed through properties
    such as:
    
    * :attr:`_orm.Mapper.attrs` - a namespace of all mapped attributes.  The attributes
      themselves are instances of :class:`.MapperProperty`, which contain additional
      attributes that can lead to the mapped SQL expression or column, if applicable.
    
    * :attr:`_orm.Mapper.column_attrs` - the mapped attribute namespace
      limited to column and SQL expression attributes.   You might want to use
      :attr:`_orm.Mapper.columns` to get at the :class:`_schema.Column` objects directly.
    
    * :attr:`_orm.Mapper.relationships` - namespace of all :class:`.RelationshipProperty` attributes.
    
    * :attr:`_orm.Mapper.all_orm_descriptors` - namespace of all mapped attributes, plus user-defined
      attributes defined using systems such as :class:`.hybrid_property`, :class:`.AssociationProxy` and others.
    
    * :attr:`_orm.Mapper.columns` - A namespace of :class:`_schema.Column` objects and other named
      SQL expressions associated with the mapping.
    
    * :attr:`_orm.Mapper.persist_selectable` - The :class:`_schema.Table` or other selectable to which
      this mapper is mapped.
    
    * :attr:`_orm.Mapper.local_table` - The :class:`_schema.Table` that is "local" to this mapper;
      this differs from :attr:`_orm.Mapper.persist_selectable` in the case of a mapper mapped
      using inheritance to a composed selectable.

.. _faq_combining_columns:

我收到有关“在属性 Y 下隐式组合列 X”的警告或错误
--------------------------------------------------------------------------------------

I'm getting a warning or error about "Implicitly combining column X under attribute Y"

.. tab:: 中文

    以下情况指的是，当映射中包含两个列因名称相同而映射到了同一属性名上，但又没有明确表明这是有意为之的。这种情况下，映射类需要为每一个要存储独立值的属性显式地命名；当两个列具有相同名称但未被区分时，它们会落在同一属性下，结果是某一列的值会被 **复制** 到另一列中，取决于哪一列最先被分配到该属性。

    当这两个列通过外键关系在继承映射中连接时，这种行为通常是期望的，并且不会发出警告。但当系统发出警告或异常时，可以通过将两个列分配给不同的属性名来解决该问题；或者，如果你确实希望合并它们，则应使用 :func:`.column_property` 来显式表示此意图。

    考虑以下示例::

        from sqlalchemy import Integer, Column, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base()


        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)


        class B(A):
            __tablename__ = "b"

            id = Column(Integer, primary_key=True)
            a_id = Column(Integer, ForeignKey("a.id"))

    从 SQLAlchemy 0.9.5 版本开始，上述情况会被检测到，并警告 ``A`` 与 ``B`` 的 ``id`` 列被合并到了同名属性 ``id`` 下。这个问题非常严重，因为它意味着 ``B`` 对象的主键总是会镜像其 ``A`` 的主键。

    一种可解决该问题的方式如下::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)


        class B(A):
            __tablename__ = "b"

            b_id = Column("id", Integer, primary_key=True)
            a_id = Column(Integer, ForeignKey("a.id"))

    假设我们确实希望 ``A.id`` 与 ``B.id`` 是互为镜像的，尽管 ``B.a_id`` 实际上才是与 ``A.id`` 建立外键关系的列。那么我们可以使用 :func:`.column_property` 将它们合并为一个属性::

        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)


        class B(A):
            __tablename__ = "b"

            # 可能并不是你真正想要的，但此处作为演示
            id = column_property(Column(Integer, primary_key=True), A.id)
            a_id = Column(Integer, ForeignKey("a.id"))

.. tab:: 英文

    This condition refers to when a mapping contains two columns that are being
    mapped under the same attribute name due to their name, but there's no indication
    that this is intentional.  A mapped class needs to have explicit names for
    every attribute that is to store an independent value; when two columns have the
    same name and aren't disambiguated, they fall under the same attribute and
    the effect is that the value from one column is **copied** into the other, based
    on which column was assigned to the attribute first.
    
    This behavior is often desirable and is allowed without warning in the case
    where the two columns are linked together via a foreign key relationship
    within an inheritance mapping.   When the warning or exception occurs, the
    issue can be resolved by either assigning the columns to differently-named
    attributes, or if combining them together is desired, by using
    :func:`.column_property` to make this explicit.
    
    Given the example as follows::
    
        from sqlalchemy import Integer, Column, ForeignKey
        from sqlalchemy.ext.declarative import declarative_base
    
        Base = declarative_base()
    
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
    
    
        class B(A):
            __tablename__ = "b"
    
            id = Column(Integer, primary_key=True)
            a_id = Column(Integer, ForeignKey("a.id"))
    
    As of SQLAlchemy version 0.9.5, the above condition is detected, and will
    warn that the ``id`` column of ``A`` and ``B`` is being combined under
    the same-named attribute ``id``, which above is a serious issue since it means
    that a ``B`` object's primary key will always mirror that of its ``A``.
    
    A mapping which resolves this is as follows::
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
    
    
        class B(A):
            __tablename__ = "b"
    
            b_id = Column("id", Integer, primary_key=True)
            a_id = Column(Integer, ForeignKey("a.id"))
    
    Suppose we did want ``A.id`` and ``B.id`` to be mirrors of each other, despite
    the fact that ``B.a_id`` is where ``A.id`` is related.  We could combine
    them together using :func:`.column_property`::
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
    
    
        class B(A):
            __tablename__ = "b"
    
            # probably not what you want, but this is a demonstration
            id = column_property(Column(Integer, primary_key=True), A.id)
            a_id = Column(Integer, ForeignKey("a.id"))

我正在使用 Declarative 并使用 ``and_()`` 或 ``or_()`` 设置 primaryjoin/secondaryjoin，并且收到有关外键的错误消息。
------------------------------------------------------------------------------------------------------------------------------------------------------------------

I'm using Declarative and setting primaryjoin/secondaryjoin using an ``and_()`` or ``or_()``, and I am getting an error message about foreign keys.

.. tab:: 中文

    你是这样做的吗？::

        class MyClass(Base):
            # ....

            foo = relationship(
                "Dest", primaryjoin=and_("MyClass.id==Dest.foo_id", "MyClass.foo==Dest.bar")
            )

    这是一个由两个字符串表达式组成的 ``and_()``，SQLAlchemy 无法对其进行任何映射处理。声明式（Declarative）允许将 :func:`_orm.relationship` 的参数写成字符串，这些字符串会通过 ``eval()`` 被转换为表达式对象。但这种转换不会发生在 ``and_()`` 表达式的内部 —— 这是声明式仅对传给 primaryjoin 或其他参数的 *整个* 字符串应用的特殊操作::

        class MyClass(Base):
            # ....

            foo = relationship(
                "Dest", primaryjoin="and_(MyClass.id==Dest.foo_id, MyClass.foo==Dest.bar)"
            )

    或者，如果你要使用的对象已在作用域中，直接跳过字符串::

        class MyClass(Base):
            # ....

            foo = relationship(
                Dest, primaryjoin=and_(MyClass.id == Dest.foo_id, MyClass.foo == Dest.bar)
            )

    同样的规则适用于其他参数，例如 ``foreign_keys``::

        # 错误的写法！
        foo = relationship(Dest, foreign_keys=["Dest.foo_id", "Dest.bar_id"])

        # 正确的写法！
        foo = relationship(Dest, foreign_keys="[Dest.foo_id, Dest.bar_id]")

        # 也是正确的写法！
        foo = relationship(Dest, foreign_keys=[Dest.foo_id, Dest.bar_id])


        # 如果你引用的是当前类中的列，直接使用列对象就行！
        class MyClass(Base):
            foo_id = Column(...)
            bar_id = Column(...)
            # ...

            foo = relationship(Dest, foreign_keys=[foo_id, bar_id])

.. tab:: 英文

    Are you doing this?::

        class MyClass(Base):
            # ....

            foo = relationship(
                "Dest", primaryjoin=and_("MyClass.id==Dest.foo_id", "MyClass.foo==Dest.bar")
            )

    That's an ``and_()`` of two string expressions, which SQLAlchemy cannot apply any mapping towards.  Declarative allows :func:`_orm.relationship` arguments to be specified as strings, which are converted into expression objects using ``eval()``.   But this doesn't occur inside of an ``and_()`` expression - it's a special operation declarative applies only to the *entirety* of what's passed to primaryjoin or other arguments as a string::

        class MyClass(Base):
            # ....

            foo = relationship(
                "Dest", primaryjoin="and_(MyClass.id==Dest.foo_id, MyClass.foo==Dest.bar)"
            )

    Or if the objects you need are already available, skip the strings::

        class MyClass(Base):
            # ....

            foo = relationship(
                Dest, primaryjoin=and_(MyClass.id == Dest.foo_id, MyClass.foo == Dest.bar)
            )

    The same idea applies to all the other arguments, such as ``foreign_keys``::

        # wrong !
        foo = relationship(Dest, foreign_keys=["Dest.foo_id", "Dest.bar_id"])

        # correct !
        foo = relationship(Dest, foreign_keys="[Dest.foo_id, Dest.bar_id]")

        # also correct !
        foo = relationship(Dest, foreign_keys=[Dest.foo_id, Dest.bar_id])


        # if you're using columns from the class that you're inside of, just use the column objects !
        class MyClass(Base):
            foo_id = Column(...)
            bar_id = Column(...)
            # ...

            foo = relationship(Dest, foreign_keys=[foo_id, bar_id])

.. _faq_subqueryload_limit_sort:

为什么建议将 ``ORDER BY`` 与 ``LIMIT`` 一起使用（尤其是与 ``subqueryload()`` 一起使用）？
------------------------------------------------------------------------------------

Why is ``ORDER BY`` recommended with ``LIMIT`` (especially with ``subqueryload()``)?

.. tab:: 中文

    当一个 SELECT 查询没有使用 ORDER BY 子句时，关系型数据库可以以任意顺序返回匹配的行。虽然这种顺序通常会对应于表中记录的自然顺序，但这并不适用于所有数据库和所有查询。因此，当你使用 ``LIMIT`` 或 ``OFFSET`` 来限制返回的行数，或仅仅是选取结果集的第一行时，返回的是哪一行其实是不可预测的（前提是有多于一行匹配该查询）。

    虽然在一些通常返回自然顺序的数据库上，我们可能不会注意到这个问题，但当我们结合使用 :func:`_orm.subqueryload` 来加载关联集合时，这种不确定性就可能导致集合加载不如预期。

    SQLAlchemy 使用 :func:`_orm.subqueryload` 的方式是发出一个独立的查询，然后将其结果与第一个查询的结果进行匹配。我们会看到两条查询语句像这样被发出：

    .. sourcecode:: pycon+sql

        >>> session.scalars(select(User).options(subqueryload(User.addresses))).all()
        {execsql}-- “主”查询
        SELECT users.id AS users_id
        FROM users
        {stop}
        {execsql}-- subqueryload 发出的“加载”查询
        SELECT addresses.id AS addresses_id,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (SELECT users.id AS users_id FROM users) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id

    第二条查询将第一条查询嵌入为行来源。
    当内部查询使用 ``OFFSET`` 和/或 ``LIMIT`` 且未指定排序时，两条查询可能返回不一致的结果：

    .. sourcecode:: pycon+sql

        >>> user = session.scalars(
        ...     select(User).options(subqueryload(User.addresses)).limit(1)
        ... ).first()
        {execsql}-- “主”查询
        SELECT users.id AS users_id
        FROM users
        LIMIT 1
        {stop}
        {execsql}-- subqueryload 发出的“加载”查询
        SELECT addresses.id AS addresses_id,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (SELECT users.id AS users_id FROM users LIMIT 1) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id

    根据数据库的具体实现，我们可能会得到如下两个查询的结果：

    .. sourcecode:: text

        -- 查询 #1
        +--------+
        |users_id|
        +--------+
        |       1|
        +--------+

        -- 查询 #2
        +------------+-----------------+---------------+
        |addresses_id|addresses_user_id|anon_1_users_id|
        +------------+-----------------+---------------+
        |           3|                2|              2|
        +------------+-----------------+---------------+
        |           4|                2|              2|
        +------------+-----------------+---------------+

    如上所示，我们收到了两个属于 ``user.id = 2`` 的 ``addresses`` 行，但 ``1`` 的却没有返回。我们浪费了两个行结果，而且实际上并未正确加载集合。这个错误非常隐蔽，因为如果不查看 SQL 和实际结果，ORM 不会表现出任何异常；当我们访问 ``User`` 的 ``addresses`` 时，它只会触发一次惰性加载，掩盖了真正的问题。

    这个问题的解决方法是始终指定一个确定性的排序顺序，以保证主查询始终返回相同的一组行。这通常意味着你应该在查询中使用 :meth:`_sql.Select.order_by`，基于表中的某个唯一列排序。主键列通常是一个理想的选择::

        session.scalars(
            select(User).options(subqueryload(User.addresses)).order_by(User.id).limit(1)
        ).first()

    需要注意的是，:func:`_orm.joinedload` 预加载策略不会遇到这个问题，因为它只发出一条查询语句，所以加载查询不可能与主查询不一致。同样，:func:`.selectinload` 预加载策略也不会有这个问题，它直接使用刚加载的主键值来链接集合加载。

    .. seealso::

        :ref:`subquery_eager_loading`

.. tab:: 英文

    When ORDER BY is not used for a SELECT statement that returns rows, the
    relational database is free to returned matched rows in any arbitrary
    order.  While this ordering very often corresponds to the natural
    order of rows within a table, this is not the case for all databases and all
    queries. The consequence of this is that any query that limits rows using
    ``LIMIT`` or ``OFFSET``, or which merely selects the first row of the result,
    discarding the rest, will not be deterministic in terms of what result row is
    returned, assuming there's more than one row that matches the query's criteria.

    While we may not notice this for simple queries on databases that usually
    returns rows in their natural order, it becomes more of an issue if we
    also use :func:`_orm.subqueryload` to load related collections, and we may not
    be loading the collections as intended.

    SQLAlchemy implements :func:`_orm.subqueryload` by issuing a separate query,
    the results of which are matched up to the results from the first query.
    We see two queries emitted like this:

    .. sourcecode:: pycon+sql

        >>> session.scalars(select(User).options(subqueryload(User.addresses))).all()
        {execsql}-- the "main" query
        SELECT users.id AS users_id
        FROM users
        {stop}
        {execsql}-- the "load" query issued by subqueryload
        SELECT addresses.id AS addresses_id,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (SELECT users.id AS users_id FROM users) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id

    The second query embeds the first query as a source of rows.
    When the inner query uses ``OFFSET`` and/or ``LIMIT`` without ordering,
    the two queries may not see the same results:

    .. sourcecode:: pycon+sql

        >>> user = session.scalars(
        ...     select(User).options(subqueryload(User.addresses)).limit(1)
        ... ).first()
        {execsql}-- the "main" query
        SELECT users.id AS users_id
        FROM users
        LIMIT 1
        {stop}
        {execsql}-- the "load" query issued by subqueryload
        SELECT addresses.id AS addresses_id,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (SELECT users.id AS users_id FROM users LIMIT 1) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id

    Depending on database specifics, there is
    a chance we may get a result like the following for the two queries:

    .. sourcecode:: text

        -- query #1
        +--------+
        |users_id|
        +--------+
        |       1|
        +--------+

        -- query #2
        +------------+-----------------+---------------+
        |addresses_id|addresses_user_id|anon_1_users_id|
        +------------+-----------------+---------------+
        |           3|                2|              2|
        +------------+-----------------+---------------+
        |           4|                2|              2|
        +------------+-----------------+---------------+

    Above, we receive two ``addresses`` rows for ``user.id`` of 2, and none for
    1.  We've wasted two rows and failed to actually load the collection.  This
    is an insidious error because without looking at the SQL and the results, the
    ORM will not show that there's any issue; if we access the ``addresses``
    for the ``User`` we have, it will emit a lazy load for the collection and we
    won't see that anything actually went wrong.

    The solution to this problem is to always specify a deterministic sort order,
    so that the main query always returns the same set of rows. This generally
    means that you should :meth:`_sql.Select.order_by` on a unique column on the table.
    The primary key is a good choice for this::

        session.scalars(
            select(User).options(subqueryload(User.addresses)).order_by(User.id).limit(1)
        ).first()

    Note that the :func:`_orm.joinedload` eager loader strategy does not suffer from
    the same problem because only one query is ever issued, so the load query
    cannot be different from the main query.  Similarly, the :func:`.selectinload`
    eager loader strategy also does not have this issue as it links its collection
    loads directly to primary key values just loaded.

    .. seealso::

        :ref:`subquery_eager_loading`

.. _defaults_default_factory_insert_default:

什么是 ``default``、``default_factory`` 和 ``insert_default``，我应该使用哪个？
---------------------------------------------------------------------------------------

What are ``default``, ``default_factory`` and ``insert_default`` and what should I use?

.. tab:: 中文

    由于引入了 PEP-681 数据类转换，SQLAlchemy 的 API 在此处出现了一些冲突，该规范对命名约定较为严格。当你使用 :class:`_orm.MappedAsDataclass` 时，PEP-681 就会生效，相关内容见 :ref:`orm_declarative_native_dataclasses`。如果你没有使用 MappedAsDataclass，则 PEP-681 并不适用。

.. tab:: 英文

    There's a bit of a clash in SQLAlchemy's API here due to the addition of PEP-681
    dataclass transforms, which is strict about its naming conventions. PEP-681 comes
    into play if you are using :class:`_orm.MappedAsDataclass` as shown in :ref:`orm_declarative_native_dataclasses`.
    If you are not using MappedAsDataclass, then it does not apply.

第一部分 - 不使用数据类的经典 SQLAlchemy
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Part One - Classic SQLAlchemy that is not using dataclasses

.. tab:: 中文

    在 **未使用** :class:`_orm.MappedAsDataclass` 的情况下（这是 SQLAlchemy 多年来一贯的使用方式），:func:`_orm.mapped_column`（以及 :class:`_schema.Column`）构造函数支持参数 :paramref:`_orm.mapped_column.default`。该参数表示一个 Python 端的默认值（区别于数据库模式中定义的服务端默认值），将在发出 ``INSERT`` 语句时生效。该默认值可以是一个静态的 Python 值（如字符串）、一个 Python 可调用对象， **或** 一个 SQLAlchemy SQL 构造。完整文档参见 :ref:`defaults_client_invoked_sql`。

    当你在未使用 :class:`_orm.MappedAsDataclass` 的 ORM 映射中使用 :paramref:`_orm.mapped_column.default` 时，此默认值 / 可调用对象 **不会在你构造对象时立即体现**。它只会在 SQLAlchemy 构造 ``INSERT`` 语句时生效。

    需要特别注意的是，当你使用 :func:`_orm.mapped_column`（以及 :class:`_schema.Column`）时，传统的 :paramref:`_orm.mapped_column.default` 参数也可以使用一个新名称：:paramref:`_orm.mapped_column.insert_default`。如果你构造了一个 :func:`_orm.mapped_column` 且 **未使用** :class:`_orm.MappedAsDataclass`，那么 :paramref:`_orm.mapped_column.default` 和 :paramref:`_orm.mapped_column.insert_default` 是 **等价** 的。

.. tab:: 英文

    When **not** using :class:`_orm.MappedAsDataclass`, as has been the case for many years
    in SQLAlchemy, the :func:`_orm.mapped_column` (and :class:`_schema.Column`)
    construct supports a parameter :paramref:`_orm.mapped_column.default`.
    This indicates a Python-side default (as opposed to a server side default that
    would be part of your database's schema definition) that will take place when
    an ``INSERT`` statement is emitted. This default can be **any** of a static Python value
    like a string, **or** a Python callable function, **or** a SQLAlchemy SQL construct.
    Full documentation for :paramref:`_orm.mapped_column.default` is at
    :ref:`defaults_client_invoked_sql`.

    When using :paramref:`_orm.mapped_column.default` with an ORM mapping that is **not**
    using :class:`_orm.MappedAsDataclass`, this default value /callable **does not show
    up on your object when you first construct it**. It only takes place when SQLAlchemy
    works up an ``INSERT`` statement for your object.

    A very important thing to note is that when using :func:`_orm.mapped_column`
    (and :class:`_schema.Column`), the classic :paramref:`_orm.mapped_column.default`
    parameter is also available under a new name, called
    :paramref:`_orm.mapped_column.insert_default`. If you build a
    :func:`_orm.mapped_column` and you are **not** using :class:`_orm.MappedAsDataclass`, the
    :paramref:`_orm.mapped_column.default` and :paramref:`_orm.mapped_column.insert_default`
    parameters are **synonymous**.

第二部分 - 使用 MappedAsDataclass 的数据类支持
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Part Two - Using Dataclasses support with MappedAsDataclass

.. tab:: 中文
    
    .. versionchanged:: 2.1  
       当使用数据类时，列级默认值的行为发生了变化：通过类级描述符提供类行为，同时结合 Core 层的列默认值以实现正确的 INSERT 行为。参见 :ref:`change_12168` 获取背景说明。
    
    当你 **使用** :class:`_orm.MappedAsDataclass`，即使用 :ref:`orm_declarative_native_dataclasses` 中所示的特定映射形式时，:paramref:`_orm.mapped_column.default` 关键字的含义就发生了变化。我们意识到该名称行为的变化并不理想，但由于 PEP-681 的要求，:paramref:`_orm.mapped_column.default` 必须具备这种含义。
    
    当使用数据类时，:paramref:`_orm.mapped_column.default` 参数必须按照 `Python Dataclasses <https://docs.python.org/3/library/dataclasses.html>`_ 中的描述来使用——它指的是一个常量值，如字符串或数字，并且 **在对象构造后立即可用**。从 SQLAlchemy 2.1 开始，即使该值未传入构造函数，它也会通过描述符提供，而不会直接出现在 ``__dict__`` 中。
    
    用于 :paramref:`_orm.mapped_column.default` 的值也会被应用于 :class:`_schema.Column` 的 :paramref:`_schema.Column.default` 参数。这是为了确保作为数据类默认值使用的值，也能在 ORM 发出 INSERT 语句时应用于映射对象中未显式传值的列。使用该参数与 :paramref:`_schema.Column.insert_default` 是 **互斥的**，不能同时使用两者。
    
    :paramref:`_orm.mapped_column.default` 和 :paramref:`_orm.mapped_column.insert_default` 参数也可用于 SQLAlchemy 映射的数据类字段，或整个数据类中标记为 ``init=False`` 的字段。在此用法中，如果使用了 :paramref:`_orm.mapped_column.default`，默认值将会在构造对象时立即可用，同时用于 INSERT 语句；若使用了 :paramref:`_orm.mapped_column.insert_default`，则对象上的属性值为 ``None``，但 INSERT 语句中仍会使用该默认值。
    
    若要为数据类生成可调用默认值（将在对象构造时填充至 ``__dict__`` 中），可使用 :paramref:`_orm.mapped_column.default_factory`。
    
    .. list-table:: 总结表
       :header-rows: 1
    
       * - 构造形式
         - 是否支持数据类？
         - 是否支持非数据类？
         - 是否接受标量？
         - 是否接受可调用对象？
         - 构造对象后是否立即可用？
       * - :paramref:`_orm.mapped_column.default`
         - ✔
         - ✔
         - ✔
         - 仅当未使用数据类时
         - 仅当使用数据类时
       * - :paramref:`_orm.mapped_column.insert_default`
         - ✔（仅当未使用 ``default``）
         - ✔
         - ✔
         - ✔
         - ✖
       * - :paramref:`_orm.mapped_column.default_factory`
         - ✔
         - ✖
         - ✖
         - ✔
         - 仅当使用数据类时

.. tab:: 英文

    .. versionchanged:: 2.1 The behavior of column level defaults when using
       dataclasses has changed to use an approach that uses class-level descriptors
       to provide class behavior, in conjunction with Core-level column defaults
       to provide the correct INSERT behavior. See :ref:`change_12168` for
       background.
    
    When you **are** using :class:`_orm.MappedAsDataclass`, that is, the specific form
    of mapping used at :ref:`orm_declarative_native_dataclasses`, the meaning of the
    :paramref:`_orm.mapped_column.default` keyword changes. We recognize that it's not
    ideal that this name changes its behavior, however there was no alternative as
    PEP-681 requires :paramref:`_orm.mapped_column.default` to take on this meaning.
    
    When dataclasses are used, the :paramref:`_orm.mapped_column.default` parameter
    must be used the way it's described at `Python Dataclasses
    <https://docs.python.org/3/library/dataclasses.html>`_ - it refers to a
    constant value like a string or a number, and **is available on your object
    immediately when constructed**.  As of SQLAlchemy 2.1, the value is delivered
    using a descriptor if not otherwise set, without the value actually being
    placed in ``__dict__`` unless it were passed to the constructor explicitly.
    
    The value used for :paramref:`_orm.mapped_column.default` is also applied to the
    :paramref:`_schema.Column.default` parameter of :class:`_schema.Column`.
    This is so that the value used as the dataclass default is also applied in
    an ORM INSERT statement for a mapped object where the value was not
    explicitly passed.  Using this parameter is **mutually exclusive** against the
    :paramref:`_schema.Column.insert_default` parameter, meaning that both cannot
    be used at the same time.
    
    The :paramref:`_orm.mapped_column.default` and
    :paramref:`_orm.mapped_column.insert_default` parameters may also be used
    (one or the other, not both)
    for a SQLAlchemy-mapped dataclass field, or for a dataclass overall,
    that indicates ``init=False``.
    In this usage, if :paramref:`_orm.mapped_column.default` is used, the default
    value will be available on the constructed object immediately as well as
    used within the INSERT statement.  If :paramref:`_orm.mapped_column.insert_default`
    is used, the constructed object will return ``None`` for the attribute value,
    but the default value will still be used for the INSERT statement.
    
    To use a callable to generate defaults for the dataclass, which would be
    applied to the object when constructed by populating it into ``__dict__``,
    :paramref:`_orm.mapped_column.default_factory` may be used instead.
    
    .. list-table:: Summary Chart
       :header-rows: 1
    
       * - Construct
         - Works with dataclasses?
         - Works without dataclasses?
         - Accepts scalar?
         - Accepts callable?
         - Available on object immediately?
       * - :paramref:`_orm.mapped_column.default`
         - ✔
         - ✔
         - ✔
         - Only if no dataclasses
         - Only if dataclasses
       * - :paramref:`_orm.mapped_column.insert_default`
         - ✔ (only if no ``default``)
         - ✔
         - ✔
         - ✔
         - ✖
       * - :paramref:`_orm.mapped_column.default_factory`
         - ✔
         - ✖
         - ✖
         - ✔
         - Only if dataclasses
