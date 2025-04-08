.. currentmodule:: sqlalchemy.schema

.. _metadata_reflection_toplevel:
.. _metadata_reflection:


反射数据库对象
===========================

Reflecting Database Objects

.. tab:: 中文

    可以指示 :class:`~sqlalchemy.schema.Table` 对象从数据库中已经存在的对应数据库模式对象中加载信息。这个过程称为 *反射(reflection)* 。在最简单的情况下，您只需要指定表名、一个 :class:`~sqlalchemy.schema.MetaData` 对象和 ``autoload_with`` 参数::

        >>> messages = Table("messages", metadata_obj, autoload_with=engine)
        >>> [c.name for c in messages.columns]
        ['message_id', 'message_name', 'date']

    上述操作将使用给定的引擎查询数据库中的 ``messages`` 表的信息，然后将生成与这些信息对应的 :class:`~sqlalchemy.schema.Column`、:class:`~sqlalchemy.schema.ForeignKey` 和其他对象，就像 :class:`~sqlalchemy.schema.Table` 对象是在Python中手工构造的一样。

    当表被反射时，如果一个给定的表通过外键引用另一个表，一个代表连接的第二个 :class:`~sqlalchemy.schema.Table` 对象将在 :class:`~sqlalchemy.schema.MetaData` 对象中创建。下面，假设表 ``shopping_cart_items`` 引用了一个名为 ``shopping_carts`` 的表。反射 ``shopping_cart_items`` 表的效果是使 ``shopping_carts`` 表也会被加载::

        >>> shopping_cart_items = Table("shopping_cart_items", metadata_obj, autoload_with=engine)
        >>> "shopping_carts" in metadata_obj.tables
        True

    :class:`~sqlalchemy.schema.MetaData` 具有有趣的“单例”行为，即如果您分别请求两个表，:class:`~sqlalchemy.schema.MetaData` 将确保每个不同的表名只创建一个 :class:`~sqlalchemy.schema.Table` 对象。如果一个给定名称的 :class:`~sqlalchemy.schema.Table` 对象已经存在，:class:`~sqlalchemy.schema.Table` 构造函数实际上会返回已经存在的 :class:`~sqlalchemy.schema.Table` 对象。例如，下面我们可以通过命名它来访问已经生成的 ``shopping_carts`` 表::

        shopping_carts = Table("shopping_carts", metadata_obj)

    当然，无论如何，使用 ``autoload_with=engine`` 是一个好主意。这是为了确保如果表的属性尚未加载，则将加载它们。反射操作仅在表尚未加载时发生；一旦加载，对具有相同名称的新调用将不会重新发出任何反射查询。

.. tab:: 英文

    A :class:`~sqlalchemy.schema.Table` object can be instructed to load
    information about itself from the corresponding database schema object already
    existing within the database. This process is called *reflection*. In the
    most simple case you need only specify the table name, a :class:`~sqlalchemy.schema.MetaData`
    object, and the ``autoload_with`` argument::

        >>> messages = Table("messages", metadata_obj, autoload_with=engine)
        >>> [c.name for c in messages.columns]
        ['message_id', 'message_name', 'date']

    The above operation will use the given engine to query the database for
    information about the ``messages`` table, and will then generate
    :class:`~sqlalchemy.schema.Column`, :class:`~sqlalchemy.schema.ForeignKey`,
    and other objects corresponding to this information as though the
    :class:`~sqlalchemy.schema.Table` object were hand-constructed in Python.

    When tables are reflected, if a given table references another one via foreign
    key, a second :class:`~sqlalchemy.schema.Table` object is created within the
    :class:`~sqlalchemy.schema.MetaData` object representing the connection.
    Below, assume the table ``shopping_cart_items`` references a table named
    ``shopping_carts``. Reflecting the ``shopping_cart_items`` table has the
    effect such that the ``shopping_carts`` table will also be loaded::

        >>> shopping_cart_items = Table("shopping_cart_items", metadata_obj, autoload_with=engine)
        >>> "shopping_carts" in metadata_obj.tables
        True

    The :class:`~sqlalchemy.schema.MetaData` has an interesting "singleton-like"
    behavior such that if you requested both tables individually,
    :class:`~sqlalchemy.schema.MetaData` will ensure that exactly one
    :class:`~sqlalchemy.schema.Table` object is created for each distinct table
    name. The :class:`~sqlalchemy.schema.Table` constructor actually returns to
    you the already-existing :class:`~sqlalchemy.schema.Table` object if one
    already exists with the given name. Such as below, we can access the already
    generated ``shopping_carts`` table just by naming it::

        shopping_carts = Table("shopping_carts", metadata_obj)

    Of course, it's a good idea to use ``autoload_with=engine`` with the above table
    regardless. This is so that the table's attributes will be loaded if they have
    not been already. The autoload operation only occurs for the table if it
    hasn't already been loaded; once loaded, new calls to
    :class:`~sqlalchemy.schema.Table` with the same name will not re-issue any
    reflection queries.

.. _reflection_overriding_columns:

覆盖反射列
----------------------------

Overriding Reflected Columns

.. tab:: 中文

    在反射表时，可以为各个列显式指定值以进行覆盖；
    这对于指定自定义数据类型、在数据库中未配置的主键约束等情况非常有用::

        >>> mytable = Table(
        ...     "mytable",
        ...     metadata_obj,
        ...     Column(
        ...         "id", Integer, primary_key=True
        ...     ),  # 将反射出的 'id' 列覆盖为主键
        ...     Column("mydata", Unicode(50)),  # 将反射出的 'mydata' 列覆盖为 Unicode 类型
        ...     # 其他无需更改的列正常反射
        ...     autoload_with=some_engine,
        ... )

    .. seealso::

        :ref:`custom_and_decorated_types_reflection` - 展示了上述列覆盖技术如何与
        使用自定义数据类型和表反射相结合。

.. tab:: 英文

    Individual columns can be overridden with explicit values when reflecting
    tables; this is handy for specifying custom datatypes, constraints such as
    primary keys that may not be configured within the database, etc.::

        >>> mytable = Table(
        ...     "mytable",
        ...     metadata_obj,
        ...     Column(
        ...         "id", Integer, primary_key=True
        ...     ),  # override reflected 'id' to have primary key
        ...     Column("mydata", Unicode(50)),  # override reflected 'mydata' to be Unicode
        ...     # additional Column objects which require no change are reflected normally
        ...     autoload_with=some_engine,
        ... )

    .. seealso::

        :ref:`custom_and_decorated_types_reflection` - illustrates how the above
        column override technique applies to the use of custom datatypes with
        table reflection.

反射视图
----------------

Reflecting Views

.. tab:: 中文

    反射系统也支持视图（views）的反射。基本用法与表相同::

        my_view = Table("some_view", metadata, autoload_with=engine)

    上述代码中，``my_view`` 是一个 :class:`~sqlalchemy.schema.Table` 对象，
    其包含的 :class:`~sqlalchemy.schema.Column` 对象代表视图 "some_view" 中每列的名称和类型。

    通常我们希望在反射视图时至少包含主键约束（如果可能，还包括外键约束）。
    但视图反射不会自动推断这些约束。

    可以使用“覆盖”技术，显式指定那些作为主键或具有外键约束的列::

        my_view = Table(
            "some_view",
            metadata,
            Column("view_id", Integer, primary_key=True),
            Column("related_thing", Integer, ForeignKey("othertable.thing_id")),
            autoload_with=engine,
        )

.. tab:: 英文

    The reflection system can also reflect views. Basic usage is the same as that
    of a table::

        my_view = Table("some_view", metadata, autoload_with=engine)

    Above, ``my_view`` is a :class:`~sqlalchemy.schema.Table` object with
    :class:`~sqlalchemy.schema.Column` objects representing the names and types of
    each column within the view "some_view".

    Usually, it's desired to have at least a primary key constraint when
    reflecting a view, if not foreign keys as well. View reflection doesn't
    extrapolate these constraints.

    Use the "override" technique for this, specifying explicitly those columns
    which are part of the primary key or have foreign key constraints::

        my_view = Table(
            "some_view",
            metadata,
            Column("view_id", Integer, primary_key=True),
            Column("related_thing", Integer, ForeignKey("othertable.thing_id")),
            autoload_with=engine,
        )

一次反射所有表
-----------------------------

Reflecting All Tables at Once

.. tab:: 中文

    :class:`~sqlalchemy.schema.MetaData` 对象也可以列出所有表并进行完整反射。
    可以通过调用 :func:`~sqlalchemy.schema.MetaData.reflect` 方法来实现。
    调用后，所有被找到的表都会出现在该 :class:`~sqlalchemy.schema.MetaData` 对象的表字典中::

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=someengine)
        users_table = metadata_obj.tables["users"]
        addresses_table = metadata_obj.tables["addresses"]

    ``metadata.reflect()`` 也可以用于清空或删除数据库中所有表的所有行::

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=someengine)
        with someengine.begin() as conn:
            for table in reversed(metadata_obj.sorted_tables):
                conn.execute(table.delete())

.. tab:: 英文

    The :class:`~sqlalchemy.schema.MetaData` object can also get a listing of
    tables and reflect the full set. This is achieved by using the
    :func:`~sqlalchemy.schema.MetaData.reflect` method. After calling it, all
    located tables are present within the :class:`~sqlalchemy.schema.MetaData`
    object's dictionary of tables::

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=someengine)
        users_table = metadata_obj.tables["users"]
        addresses_table = metadata_obj.tables["addresses"]

    ``metadata.reflect()`` also provides a handy way to clear or delete all the rows in a database::

        metadata_obj = MetaData()
        metadata_obj.reflect(bind=someengine)
        with someengine.begin() as conn:
            for table in reversed(metadata_obj.sorted_tables):
                conn.execute(table.delete())

.. _metadata_reflection_schemas:

反射来自其他架构的表
------------------------------------

Reflecting Tables from Other Schemas

.. tab:: 中文

    章节 :ref:`schema_table_schema_name` 引入了“schema”的概念，
    即数据库中的命名空间，包含表和其他对象，
    这些 schema 可以显式指定。
    :class:`_schema.Table` 对象的 "schema"，
    以及视图、索引和序列等其他对象的 schema，
    可以通过 :paramref:`_schema.Table.schema` 参数设置；
    也可以通过 :paramref:`_schema.MetaData.schema` 参数设置为整个 :class:`_schema.MetaData` 对象的默认 schema。

    schema 参数的使用会直接影响反射功能查找对象的位置。
    例如，给定一个通过其 :paramref:`_schema.MetaData.schema` 参数配置了默认 schema 为 "project" 的 :class:`_schema.MetaData` 对象::

        >>> metadata_obj = MetaData(schema="project")

    :meth:`.MetaData.reflect` 方法将使用配置好的 ``.schema`` 进行反射::

        >>> # 使用 metadata_obj 中配置的 `schema`
        >>> metadata_obj.reflect(someengine)

    最终结果是，来自 "project" schema 的 :class:`_schema.Table` 对象将被反射，
    并带有该 schema 名称作为限定名::

        >>> metadata_obj.tables["project.messages"]
        Table('messages', MetaData(), Column('message_id', INTEGER(), table=<messages>), schema='project')

    类似地，单独的 :class:`_schema.Table` 对象若提供了 :paramref:`_schema.Table.schema` 参数，
    也将从该 schema 中进行反射，优先于其所属的 :class:`_schema.MetaData` 对象中配置的默认 schema::

        >>> messages = Table("messages", metadata_obj, schema="project", autoload_with=someengine)
        >>> messages
        Table('messages', MetaData(), Column('message_id', INTEGER(), table=<messages>), schema='project')

    最后，:meth:`_schema.MetaData.reflect` 方法本身也支持传入
    :paramref:`_schema.MetaData.reflect.schema` 参数，
    这使得我们可以从 "project" schema 中加载表，即使 :class:`_schema.MetaData` 对象未设置默认 schema::

        >>> metadata_obj = MetaData()
        >>> metadata_obj.reflect(someengine, schema="project")

    我们可以多次调用 :meth:`_schema.MetaData.reflect`，传入不同的
    :paramref:`_schema.MetaData.schema` 参数（或不传）来继续为 :class:`_schema.MetaData` 对象添加更多对象::

        >>> # 添加来自 "customer" schema 的表
        >>> metadata_obj.reflect(someengine, schema="customer")
        >>> # 添加来自默认 schema 的表
        >>> metadata_obj.reflect(someengine)

.. tab:: 英文

    The section :ref:`schema_table_schema_name` introduces the concept of table
    schemas, which are namespaces within a database that contain tables and other
    objects, and which can be specified explicitly. The "schema" for a
    :class:`_schema.Table` object, as well as for other objects like views, indexes and
    sequences, can be set up using the :paramref:`_schema.Table.schema` parameter,
    and also as the default schema for a :class:`_schema.MetaData` object using the
    :paramref:`_schema.MetaData.schema` parameter.

    The use of this schema parameter directly affects where the table reflection
    feature will look when it is asked to reflect objects.  For example, given
    a :class:`_schema.MetaData` object configured with a default schema name
    "project" via its :paramref:`_schema.MetaData.schema` parameter::

        >>> metadata_obj = MetaData(schema="project")

    The :meth:`.MetaData.reflect` will then utilize that configured ``.schema``
    for reflection::

        >>> # uses `schema` configured in metadata_obj
        >>> metadata_obj.reflect(someengine)

    The end result is that :class:`_schema.Table` objects from the "project"
    schema will be reflected, and they will be populated as schema-qualified
    with that name::

        >>> metadata_obj.tables["project.messages"]
        Table('messages', MetaData(), Column('message_id', INTEGER(), table=<messages>), schema='project')

    Similarly, an individual :class:`_schema.Table` object that includes the
    :paramref:`_schema.Table.schema` parameter will also be reflected from that
    database schema, overriding any default schema that may have been configured on the
    owning :class:`_schema.MetaData` collection::

        >>> messages = Table("messages", metadata_obj, schema="project", autoload_with=someengine)
        >>> messages
        Table('messages', MetaData(), Column('message_id', INTEGER(), table=<messages>), schema='project')

    Finally, the :meth:`_schema.MetaData.reflect` method itself also allows a
    :paramref:`_schema.MetaData.reflect.schema` parameter to be passed, so we
    could also load tables from the "project" schema for a default configured
    :class:`_schema.MetaData` object::

        >>> metadata_obj = MetaData()
        >>> metadata_obj.reflect(someengine, schema="project")

    We can call :meth:`_schema.MetaData.reflect` any number of times with different
    :paramref:`_schema.MetaData.schema` arguments (or none at all) to continue
    populating the :class:`_schema.MetaData` object with more objects::

        >>> # add tables from the "customer" schema
        >>> metadata_obj.reflect(someengine, schema="customer")
        >>> # add tables from the default schema
        >>> metadata_obj.reflect(someengine)

.. _reflection_schema_qualified_interaction:

架构限定反射与默认架构的交互
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interaction of Schema-qualified Reflection with the Default Schema

.. tab:: 中文

    .. admonition:: 小节最佳实践总结
    
       本节讨论了 SQLAlchemy 在处理数据库会话中“默认 schema”下可见的表时的反射行为，
       以及这些表如何与包含显式 schema 的 SQLAlchemy 指令交互。最佳实践是：
       确保数据库的“默认” schema 仅是一个单独的名称，而不是多个名称组成的列表；
       对于那些属于该“默认” schema，且在 DDL 和 SQL 中可以不加限定名直接引用的表，
       应将相应的 :paramref:`_schema.Table.schema` 及类似的 schema 参数保留为默认值 ``None``。
    
    如 :ref:`schema_metadata_schema_name` 中所述，具有 schema 概念的数据库通常也包含“默认 schema”的概念。
    这是因为，在常见情况下引用表对象时不写 schema 名，
    但支持 schema 的数据库仍然会认为该表存在于某个 schema 中。
    例如，PostgreSQL 更进一步引入了
    `schema 搜索路径
    <https://www.postgresql.org/docs/current/static/ddl-schemas.html#DDL-SCHEMAS-PATH>`_
    的概念，在一个数据库会话中，可以有多个 schema 被视为“隐式”的；
    此时引用这些 schema 中的表名时不需要指定 schema 名（当然，指定了 schema 名也完全可以接受）。
    
    由于大多数关系型数据库都支持一种表对象既可以使用 schema 限定名，也可以以“隐式”方式（无 schema）引用，
    这就为 SQLAlchemy 的反射功能带来了复杂性。
    在以 schema 限定方式反射一个表时，
    会将其 :attr:`_schema.Table.schema` 属性设置为相应的 schema，
    并以 schema 限定方式存储在 :attr:`_schema.MetaData.tables` 集合中；
    而以非 schema 限定方式反射同一个表，则会以未限定 schema 的方式存储在该集合中。
    最终结果是：在同一个 :class:`_schema.MetaData` 集合中，会存在两个表示数据库中同一张表的 :class:`_schema.Table` 对象。
    
    为了说明这一问题的影响，考虑前例中的 "project" schema 中的表，
    假设该 schema 是数据库连接的默认 schema，
    或者在 PostgreSQL 中，假设 "project" 已被设置到 PostgreSQL 的 ``search_path`` 中。
    这样一来，数据库会接受以下两个 SQL 语句作为等价的：
    
    .. sourcecode:: sql
    
        -- 带 schema 限定
        SELECT message_id FROM project.messages
    
        -- 无 schema 限定
        SELECT message_id FROM messages
    
    在数据库中，这不是问题，因为表可以通过这两种方式找到。
    但在 SQLAlchemy 中，SQL 语句的语义取决于 :class:`_schema.Table` 对象的“标识”。
    根据 SQLAlchemy 当前的决策，如果我们同时以 schema 限定方式和非限定方式反射同一张 "messages" 表，
    将会得到两个 **不会** 被视为语义等价的 :class:`_schema.Table` 对象::
    
        >>> # 以非 schema 限定方式反射
        >>> messages_table_1 = Table("messages", metadata_obj, autoload_with=someengine)
        >>> # 以 schema 限定方式反射
        >>> messages_table_2 = Table(
        ...     "messages", metadata_obj, schema="project", autoload_with=someengine
        ... )
        >>> # 两个不同的对象
        >>> messages_table_1 is messages_table_2
        False
        >>> # 分别存储在不同位置
        >>> metadata.tables["messages"] is messages_table_1
        True
        >>> metadata.tables["project.messages"] is messages_table_2
        True
    
    当被反射的表包含对其他表的外键引用时，上述问题将更加复杂。
    假设 "messages" 表有一个 "project_id" 列引用了同一 schema 下的另一张表 "projects"，
    这意味着在 "messages" 表的定义中存在一个 :class:`_schema.ForeignKeyConstraint` 约束对象。
    
    此时，我们可能在一个 :class:`_schema.MetaData` 集合中拥有多达四个 :class:`_schema.Table` 对象来表示数据库中的这两张表，
    其中一部分可能是反射过程中自动生成的；
    这是因为反射过程中遇到外键时会自动反射被引用的表。
    在为该被引用表分配 schema 时，SQLAlchemy 的逻辑是：
    如果外键所属的 :class:`_schema.Table` 对象未指定 schema，
    且被引用表与当前表在同一个 schema 中，则反射的 :class:`_schema.ForeignKeyConstraint` 对象将 **省略 schema**；
    否则将 **包含 schema**。
    
    最常见的情况是：以 schema 限定方式反射某张表后，
    其关联表也会以 schema 限定方式被反射::
    
        >>> # 以 schema 限定方式反射 "messages"
        >>> messages_table_1 = Table(
        ...     "messages", metadata_obj, schema="project", autoload_with=someengine
        ... )
    
    上述 ``messages_table_1`` 中的 ``projects`` 表也将以 schema 限定方式被引用。
    该 "projects" 表会因为 "messages" 引用了它而被自动反射::
    
        >>> messages_table_1.c.project_id
        Column('project_id', INTEGER(), ForeignKey('project.projects.project_id'), table=<messages>)
    
    如果代码的其他部分又以非 schema 限定方式反射了 "projects" 表，
    就会存在两个不相同的 "projects" 表对象：
    
        >>> # 以非 schema 限定方式反射 "projects"
        >>> projects_table_1 = Table("projects", metadata_obj, autoload_with=someengine)
    
        >>> # messages_table_1 并不引用 projects_table_1
        >>> messages_table_1.c.project_id.references(projects_table_1.c.project_id)
        False
    
        >>> # 它引用的是这个
        >>> projects_table_2 = metadata_obj.tables["project.projects"]
        >>> messages_table_1.c.project_id.references(projects_table_2.c.project_id)
        True
    
        >>> # 它们是不同的对象，一个有 schema，一个没有
        >>> projects_table_1 is projects_table_2
        False
    
    这种混乱会给依赖反射加载应用级 :class:`_schema.Table` 对象的程序带来问题，
    尤其是在数据库迁移场景中，例如使用 Alembic Migrations 检测新表和外键约束时。
    
    要避免上述行为带来的问题，只需遵循以下简单规则：
    
    * 对于期望存在于数据库 **默认 schema** 中的 :class:`_schema.Table`，
      不要为其指定 :paramref:`_schema.Table.schema` 参数。
    
    对于 PostgreSQL 及其他支持 schema “搜索路径”的数据库，还需遵循以下规则：
    
    * 将“搜索路径”限制为仅包含一个 schema，即默认 schema。
    
    .. seealso::
    
        :ref:`postgresql_schema_reflection` - 有关该行为在 PostgreSQL 数据库中的更多细节。


.. tab:: 英文

    .. admonition:: Section Best Practices Summarized
    
       In this section, we discuss SQLAlchemy's reflection behavior regarding
       tables that are visible in the "default schema" of a database session,
       and how these interact with SQLAlchemy directives that include the schema
       explicitly.  As a best practice, ensure the "default" schema for a database
       is just a single name, and not a list of names; for tables that are
       part of this "default" schema and can be named without schema qualification
       in DDL and SQL, leave corresponding :paramref:`_schema.Table.schema` and
       similar schema parameters set to their default of ``None``.
    
    As described at :ref:`schema_metadata_schema_name`, databases that have
    the concept of schemas usually also include the concept of a "default" schema.
    The reason for this is naturally that when one refers to table objects without
    a schema as is common, a schema-capable database will still consider that
    table to be in a "schema" somewhere.   Some databases such as PostgreSQL
    take this concept further into the notion of a
    `schema search path
    <https://www.postgresql.org/docs/current/static/ddl-schemas.html#DDL-SCHEMAS-PATH>`_
    where *multiple* schema names can be considered in a particular database
    session to be "implicit"; referring to a table name that it's any of those
    schemas will not require that the schema name be present (while at the same time
    it's also perfectly fine if the schema name *is* present).
    
    Since most relational databases therefore have the concept of a particular
    table object which can be referenced both in a schema-qualified way, as
    well as an "implicit" way where no schema is present, this presents a
    complexity for SQLAlchemy's reflection
    feature.  Reflecting a table in
    a schema-qualified manner will always populate its :attr:`_schema.Table.schema`
    attribute and additionally affect how this :class:`_schema.Table` is organized
    into the :attr:`_schema.MetaData.tables` collection, that is, in a schema
    qualified manner.  Conversely, reflecting the **same** table in a non-schema
    qualified manner will organize it into the :attr:`_schema.MetaData.tables`
    collection **without** being schema qualified.  The end result is that there
    would be two separate :class:`_schema.Table` objects in the single
    :class:`_schema.MetaData` collection representing the same table in the
    actual database.
    
    To illustrate the ramifications of this issue, consider tables from the
    "project" schema in the previous example, and suppose also that the "project"
    schema is the default schema of our database connection, or if using a database
    such as PostgreSQL suppose the "project" schema is set up in the PostgreSQL
    ``search_path``.  This would mean that the database accepts the following
    two SQL statements as equivalent:
    
    .. sourcecode:: sql
    
        -- schema qualified
        SELECT message_id FROM project.messages
    
        -- non-schema qualified
        SELECT message_id FROM messages
    
    This is not a problem as the table can be found in both ways.  However
    in SQLAlchemy, it's the **identity** of the :class:`_schema.Table` object
    that determines its semantic role within a SQL statement.  Based on the current
    decisions within SQLAlchemy, this means that if we reflect the same "messages" table in
    both a schema-qualified as well as a non-schema qualified manner, we get
    **two** :class:`_schema.Table` objects that will **not** be treated as
    semantically equivalent::
    
        >>> # reflect in non-schema qualified fashion
        >>> messages_table_1 = Table("messages", metadata_obj, autoload_with=someengine)
        >>> # reflect in schema qualified fashion
        >>> messages_table_2 = Table(
        ...     "messages", metadata_obj, schema="project", autoload_with=someengine
        ... )
        >>> # two different objects
        >>> messages_table_1 is messages_table_2
        False
        >>> # stored in two different ways
        >>> metadata.tables["messages"] is messages_table_1
        True
        >>> metadata.tables["project.messages"] is messages_table_2
        True
    
    The above issue becomes more complicated when the tables being reflected contain
    foreign key references to other tables.  Suppose "messages" has a "project_id"
    column which refers to rows in another schema-local table "projects", meaning
    there is a :class:`_schema.ForeignKeyConstraint` object that is part of the
    definition of the "messages" table.
    
    We can find ourselves in a situation where one :class:`_schema.MetaData`
    collection may contain as many as four :class:`_schema.Table` objects
    representing these two database tables, where one or two of the additional
    tables were generated by the reflection process; this is because when
    the reflection process encounters a foreign key constraint on a table
    being reflected, it branches out to reflect that referenced table as well.
    The decision making it uses to assign the schema to this referenced
    table is that SQLAlchemy will **omit a default schema** from the reflected
    :class:`_schema.ForeignKeyConstraint` object if the owning
    :class:`_schema.Table` also omits its schema name and also that these two objects
    are in the same schema, but will **include** it if
    it were not omitted.
    
    The common scenario is when the reflection of a table in a schema qualified
    fashion then loads a related table that will also be performed in a schema
    qualified fashion::
    
        >>> # reflect "messages" in a schema qualified fashion
        >>> messages_table_1 = Table(
        ...     "messages", metadata_obj, schema="project", autoload_with=someengine
        ... )
    
    The above ``messages_table_1`` will refer to ``projects`` also in a schema
    qualified fashion.  This "projects" table will be reflected automatically by
    the fact that "messages" refers to it::
    
        >>> messages_table_1.c.project_id
        Column('project_id', INTEGER(), ForeignKey('project.projects.project_id'), table=<messages>)
    
    if some other part of the code reflects "projects" in a non-schema qualified
    fashion, there are now two projects tables that are not the same:
    
        >>> # reflect "projects" in a non-schema qualified fashion
        >>> projects_table_1 = Table("projects", metadata_obj, autoload_with=someengine)
    
        >>> # messages does not refer to projects_table_1 above
        >>> messages_table_1.c.project_id.references(projects_table_1.c.project_id)
        False
    
        >>> # it refers to this one
        >>> projects_table_2 = metadata_obj.tables["project.projects"]
        >>> messages_table_1.c.project_id.references(projects_table_2.c.project_id)
        True
    
        >>> # they're different, as one non-schema qualified and the other one is
        >>> projects_table_1 is projects_table_2
        False
    
    The above confusion can cause problems within applications that use table
    reflection to load up application-level :class:`_schema.Table` objects, as
    well as within migration scenarios, in particular such as when using Alembic
    Migrations to detect new tables and foreign key constraints.
    
    The above behavior can be remedied by sticking to one simple practice:
    
    * Don't include the :paramref:`_schema.Table.schema` parameter for any
      :class:`_schema.Table` that expects to be located in the **default** schema
      of the database.
    
    For PostgreSQL and other databases that support a "search" path for schemas,
    add the following additional practice:
    
    * Keep the "search path" narrowed down to **one schema only, which is the
      default schema**.
    
    
    .. seealso::
    
        :ref:`postgresql_schema_reflection` - additional details of this behavior
        as regards the PostgreSQL database.
    

.. _metadata_reflection_inspector:

使用检查器的细粒度反射
--------------------------------------

Fine Grained Reflection with Inspector

.. tab:: 中文

    还提供一个低级接口，它提供了一个与后端无关的系统，用于从给定的数据库加载架构、表、列和约束描述列表。这被称为“检查器(Inspector)”::

        from sqlalchemy import create_engine
        from sqlalchemy import inspect

        engine = create_engine("...")
        insp = inspect(engine)
        print(insp.get_table_names())

.. tab:: 英文

    A low level interface which provides a backend-agnostic system of loading
    lists of schema, table, column, and constraint descriptions from a given
    database is also available. This is known as the "Inspector"::

        from sqlalchemy import create_engine
        from sqlalchemy import inspect

        engine = create_engine("...")
        insp = inspect(engine)
        print(insp.get_table_names())

.. autoclass:: sqlalchemy.engine.reflection.Inspector
    :members:
    :undoc-members:

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedColumn
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedComputed
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedCheckConstraint
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedForeignKeyConstraint
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedIdentity
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedIndex
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedPrimaryKeyConstraint
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedUniqueConstraint
    :members:
    :inherited-members: dict

.. autoclass:: sqlalchemy.engine.interfaces.ReflectedTableComment
    :members:
    :inherited-members: dict


.. _metadata_reflection_dbagnostic_types:

使用与数据库无关的类型进行反射
---------------------------------------

Reflecting with Database-Agnostic Types

.. tab:: 中文

    当反射表的列时，无论是使用 :paramref:`_schema.Table.autoload_with` 参数
    还是使用 :meth:`_reflection.Inspector.get_columns` 方法，
    数据类型将尽可能具体地与目标数据库匹配。
    这意味着，如果从 MySQL 数据库中反射出一个“integer”数据类型，
    该类型将由 :class:`sqlalchemy.dialects.mysql.INTEGER` 类表示，
    该类包含 MySQL 特有的属性，如 "display_width"。
    在 PostgreSQL 中，可能会返回 PostgreSQL 特有的数据类型，如
    :class:`sqlalchemy.dialects.postgresql.INTERVAL` 或
    :class:`sqlalchemy.dialects.postgresql.ENUM`。
    
    有一种反射的使用场景是：将给定的 :class:`_schema.Table` 转移到另一个供应商的数据库。
    为了适应这种场景，可以使用一种技术，将这些供应商特有的数据类型
    动态转换为 SQLAlchemy 后端无关的数据类型实例，例如上述的 :class:`_types.Integer`、:class:`_types.Interval` 和 :class:`_types.Enum`。
    这可以通过在列反射时拦截 :meth:`_events.DDLEvents.column_reflect` 事件，并结合
    :meth:`_types.TypeEngine.as_generic` 方法来实现。
    
    考虑一个 MySQL 中的表（选择 MySQL 是因为它有很多供应商特有的数据类型和选项）：
    
    .. sourcecode:: sql
    
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            data1 VARCHAR(50) CHARACTER SET latin1,
            data2 MEDIUMINT(4),
            data3 TINYINT(2)
        )
    
    上述表包含了 MySQL 特有的整数类型 ``MEDIUMINT`` 和 ``TINYINT``
    以及包含 MySQL 特有的 ``CHARACTER SET`` 选项的 ``VARCHAR``。
    如果我们正常反射该表，它会生成一个 :class:`_schema.Table` 对象，
    该对象将包含这些 MySQL 特有的数据类型和选项：
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import MetaData, Table, create_engine
        >>> mysql_engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test")
        >>> metadata_obj = MetaData()
        >>> my_mysql_table = Table("my_table", metadata_obj, autoload_with=mysql_engine)
    
    上述示例将表架构反射到一个新的 :class:`_schema.Table` 对象中。
    然后，我们可以为了演示目的，使用 :class:`_schema.CreateTable` 构造体打印出 MySQL 特有的
    "CREATE TABLE" 语句：
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy.schema import CreateTable
        >>> print(CreateTable(my_mysql_table).compile(mysql_engine))
        {printsql}CREATE TABLE my_table (
        id INTEGER(11) NOT NULL AUTO_INCREMENT,
        data1 VARCHAR(50) CHARACTER SET latin1,
        data2 MEDIUMINT(4),
        data3 TINYINT(2),
        PRIMARY KEY (id)
        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    
    上面，MySQL 特有的数据类型和选项被保留了。如果我们想要一个
    可以干净地转移到另一个数据库供应商的 :class:`_schema.Table`，
    并将特有的数据类型 :class:`sqlalchemy.dialects.mysql.MEDIUMINT` 和
    :class:`sqlalchemy.dialects.mysql.TINYINT` 替换为 :class:`_types.Integer`，
    我们可以选择将该表的数据类型“通用化”，或以任何我们想要的方式修改它们，
    通过使用 :meth:`_events.DDLEvents.column_reflect` 事件建立一个处理程序。
    该自定义处理程序将使用 :meth:`_types.TypeEngine.as_generic` 方法，
    通过替换传递给事件处理程序的列字典中的 ``"type"`` 项，
    将上述 MySQL 特有的类型对象转换为通用类型。
    该字典的格式可以在 :meth:`_reflection.Inspector.get_columns` 中找到：
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import event
        >>> metadata_obj = MetaData()
    
        >>> @event.listens_for(metadata_obj, "column_reflect")
        ... def genericize_datatypes(inspector, tablename, column_dict):
        ...     column_dict["type"] = column_dict["type"].as_generic()
    
        >>> my_generic_table = Table("my_table", metadata_obj, autoload_with=mysql_engine)
    
    现在，我们得到一个新的通用 :class:`_schema.Table`，它使用 :class:`_types.Integer` 来表示这些数据类型。
    我们现在可以为 PostgreSQL 数据库发出一个 "CREATE TABLE" 语句，例如：
    
    .. sourcecode:: pycon+sql
    
        >>> pg_engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        >>> my_generic_table.create(pg_engine)
        {execsql}CREATE TABLE my_table (
            id SERIAL NOT NULL,
            data1 VARCHAR(50),
            data2 INTEGER,
            data3 INTEGER,
            PRIMARY KEY (id)
        )
    
    上面也可以注意到，SQLAlchemy 通常会为其他行为做出合理的猜测，
    例如 MySQL 的 ``AUTO_INCREMENT`` 指令在 PostgreSQL 中最接近的是 ``SERIAL`` 自增数据类型。
    
    .. versionadded:: 1.4 添加了 :meth:`_types.TypeEngine.as_generic` 方法，
       并改进了 :meth:`_events.DDLEvents.column_reflect` 事件的使用，
       使其可以方便地应用于 :class:`_schema.MetaData` 对象。


.. tab:: 英文

    When the columns of a table are reflected, using either the
    :paramref:`_schema.Table.autoload_with` parameter of :class:`_schema.Table` or
    the :meth:`_reflection.Inspector.get_columns` method of
    :class:`_reflection.Inspector`, the datatypes will be as specific as possible
    to the target database.   This means that if an "integer" datatype is reflected
    from a MySQL database, the type will be represented by the
    :class:`sqlalchemy.dialects.mysql.INTEGER` class, which includes MySQL-specific
    attributes such as "display_width".   Or on PostgreSQL, a PostgreSQL-specific
    datatype such as :class:`sqlalchemy.dialects.postgresql.INTERVAL` or
    :class:`sqlalchemy.dialects.postgresql.ENUM` may be returned.
    
    There is a use case for reflection which is that a given :class:`_schema.Table`
    is to be transferred to a different vendor database.   To suit this use case,
    there is a technique by which these vendor-specific datatypes can be converted
    on the fly to be instance of SQLAlchemy backend-agnostic datatypes, for
    the examples above types such as :class:`_types.Integer`, :class:`_types.Interval`
    and :class:`_types.Enum`.   This may be achieved by intercepting the
    column reflection using the :meth:`_events.DDLEvents.column_reflect` event
    in conjunction with the :meth:`_types.TypeEngine.as_generic` method.
    
    Given a table in MySQL (chosen because MySQL has a lot of vendor-specific
    datatypes and options):
    
    .. sourcecode:: sql
    
        CREATE TABLE IF NOT EXISTS my_table (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            data1 VARCHAR(50) CHARACTER SET latin1,
            data2 MEDIUMINT(4),
            data3 TINYINT(2)
        )
    
    The above table includes MySQL-only integer types ``MEDIUMINT`` and
    ``TINYINT`` as well as a ``VARCHAR`` that includes the MySQL-only ``CHARACTER
    SET`` option.   If we reflect this table normally, it produces a
    :class:`_schema.Table` object that will contain those MySQL-specific datatypes
    and options:
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import MetaData, Table, create_engine
        >>> mysql_engine = create_engine("mysql+mysqldb://scott:tiger@localhost/test")
        >>> metadata_obj = MetaData()
        >>> my_mysql_table = Table("my_table", metadata_obj, autoload_with=mysql_engine)
    
    The above example reflects the above table schema into a new :class:`_schema.Table`
    object.  We can then, for demonstration purposes, print out the MySQL-specific
    "CREATE TABLE" statement using the :class:`_schema.CreateTable` construct:
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy.schema import CreateTable
        >>> print(CreateTable(my_mysql_table).compile(mysql_engine))
        {printsql}CREATE TABLE my_table (
        id INTEGER(11) NOT NULL AUTO_INCREMENT,
        data1 VARCHAR(50) CHARACTER SET latin1,
        data2 MEDIUMINT(4),
        data3 TINYINT(2),
        PRIMARY KEY (id)
        )ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
    
    
    Above, the MySQL-specific datatypes and options were maintained.   If we wanted
    a :class:`_schema.Table` that we could instead transfer cleanly to another
    database vendor, replacing the special datatypes
    :class:`sqlalchemy.dialects.mysql.MEDIUMINT` and
    :class:`sqlalchemy.dialects.mysql.TINYINT` with :class:`_types.Integer`, we can
    choose instead to "genericize" the datatypes on this table, or otherwise change
    them in any way we'd like, by establishing a handler using the
    :meth:`_events.DDLEvents.column_reflect` event.  The custom handler will make use
    of the :meth:`_types.TypeEngine.as_generic` method to convert the above
    MySQL-specific type objects into generic ones, by replacing the ``"type"``
    entry within the column dictionary entry that is passed to the event handler.
    The format of this dictionary is described at :meth:`_reflection.Inspector.get_columns`:
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import event
        >>> metadata_obj = MetaData()
    
        >>> @event.listens_for(metadata_obj, "column_reflect")
        ... def genericize_datatypes(inspector, tablename, column_dict):
        ...     column_dict["type"] = column_dict["type"].as_generic()
    
        >>> my_generic_table = Table("my_table", metadata_obj, autoload_with=mysql_engine)
    
    We now get a new :class:`_schema.Table` that is generic and uses
    :class:`_types.Integer` for those datatypes.  We can now emit a
    "CREATE TABLE" statement for example on a PostgreSQL database:
    
    .. sourcecode:: pycon+sql
    
        >>> pg_engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        >>> my_generic_table.create(pg_engine)
        {execsql}CREATE TABLE my_table (
            id SERIAL NOT NULL,
            data1 VARCHAR(50),
            data2 INTEGER,
            data3 INTEGER,
            PRIMARY KEY (id)
        )
    
    Noting above also that SQLAlchemy will usually make a decent guess for other
    behaviors, such as that the MySQL ``AUTO_INCREMENT`` directive is represented
    in PostgreSQL most closely using the ``SERIAL`` auto-incrementing datatype.
    
    .. versionadded:: 1.4 Added the :meth:`_types.TypeEngine.as_generic` method
       and additionally improved the use of the :meth:`_events.DDLEvents.column_reflect`
       event such that it may be applied to a :class:`_schema.MetaData` object
       for convenience.


反射的局限性
-------------------------

Limitations of Reflection

.. tab:: 中文
    
    需要注意的是，反射过程仅使用数据库中表示的信息来重新创建 :class:`_schema.Table` 元数据。
    根据定义，这个过程无法恢复数据库中未实际存储的 schema 方面的信息。
    反射过程中无法恢复的状态包括但不限于：
    
    * 客户端默认值，既可以是 Python 函数，也可以是使用 :class:`_schema.Column` 的 ``default`` 关键字定义的 SQL 表达式
      （注意，这与 ``server_default`` 是分开的，后者是反射时可以获取的内容）。
    
    * 列信息，例如可能已放入 :attr:`_schema.Column.info` 字典的数据
    
    * :class:`_schema.Column` 或 :class:`_schema.Table` 的 ``.quote`` 设置的值
    
    * 特定 :class:`.Sequence` 与给定 :class:`_schema.Column` 的关联
    
    在许多情况下，关系型数据库报告的表元数据格式与 SQLAlchemy 中指定的格式不同。
    反射返回的 :class:`_schema.Table` 对象不能总是可靠地生成与原始 Python 定义的 :class:`_schema.Table` 对象相同的 DDL。
    发生这种情况的领域包括服务器默认值、列相关序列以及与约束和数据类型有关的各种特殊情况。
    服务器端默认值可能会与强制转换指令一起返回（通常 PostgreSQL 会包括 ``::<type>`` 强制转换）
    或与最初指定的引号模式不同。
    
    另一个限制类别包括反射仅部分定义或尚未定义的 schema 结构。
    最近对反射的改进允许反射视图、索引和外键选项等内容。
    截至本文写作时，像 CHECK 约束、表注释和触发器等结构尚未反射。

.. tab:: 英文

    It's important to note that the reflection process recreates :class:`_schema.Table`
    metadata using only information which is represented in the relational database.
    This process by definition cannot restore aspects of a schema that aren't
    actually stored in the database.   State which is not available from reflection
    includes but is not limited to:
    
    * Client side defaults, either Python functions or SQL expressions defined using
      the ``default`` keyword of :class:`_schema.Column` (note this is separate from ``server_default``,
      which specifically is what's available via reflection).
    
    * Column information, e.g. data that might have been placed into the
      :attr:`_schema.Column.info` dictionary
    
    * The value of the ``.quote`` setting for :class:`_schema.Column` or :class:`_schema.Table`
    
    * The association of a particular :class:`.Sequence` with a given :class:`_schema.Column`
    
    The relational database also in many cases reports on table metadata in a
    different format than what was specified in SQLAlchemy.   The :class:`_schema.Table`
    objects returned from reflection cannot be always relied upon to produce the identical
    DDL as the original Python-defined :class:`_schema.Table` objects.   Areas where
    this occurs includes server defaults, column-associated sequences and various
    idiosyncrasies regarding constraints and datatypes.   Server side defaults may
    be returned with cast directives (typically PostgreSQL will include a ``::<type>``
    cast) or different quoting patterns than originally specified.
    
    Another category of limitation includes schema structures for which reflection
    is only partially or not yet defined.  Recent improvements to reflection allow
    things like views, indexes and foreign key options to be reflected.  As of this
    writing, structures like CHECK constraints, table comments, and triggers are
    not reflected.

