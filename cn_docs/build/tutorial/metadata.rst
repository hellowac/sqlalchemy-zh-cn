.. |prev| replace:: :doc:`dbapi_transactions`
.. |next| replace:: :doc:`data`

.. include:: tutorial_nav_include.rst

.. _tutorial_working_with_metadata:

使用数据库元数据
==============================

Working with Database Metadata

.. tab:: 中文

    随着引擎和 SQL 执行的完成，我们准备开始一些 Alchemy。SQLAlchemy Core 和 ORM 的核心元素是 SQL 表达式语言，它允许流畅、可组合地构建 SQL 查询。这些查询的基础是表示数据库概念（如表和列）的 Python 对象。这些对象统称为 :term:`database metadata`。

    SQLAlchemy 中最常见的数据库元数据基础对象是 :class:`_schema.MetaData`、:class:`_schema.Table` 和 :class:`_schema.Column`。下面的部分将说明这些对象在 Core 导向风格和 ORM 导向风格中的使用。

    .. container:: orm-header

        **ORM 读者，请继续关注！**

        与其他部分一样，Core 用户可以跳过 ORM 部分，但 ORM 用户最好从这两个角度熟悉这些对象。这里讨论的 :class:`.Table` 对象在使用 ORM 时以更间接（并且完全是 Python 类型）的方式声明，但在 ORM 的配置中仍然存在一个 :class:`.Table` 对象。

.. tab:: 英文

    With engines and SQL execution down, we are ready to begin some Alchemy.
    The central element of both SQLAlchemy Core and ORM is the SQL Expression
    Language which allows for fluent, composable construction of SQL queries.
    The foundation for these queries are Python objects that represent database
    concepts like tables and columns.   These objects are known collectively
    as :term:`database metadata`.

    The most common foundational objects for database metadata in SQLAlchemy are
    known as  :class:`_schema.MetaData`, :class:`_schema.Table`, and :class:`_schema.Column`.
    The sections below will illustrate how these objects are used in both a
    Core-oriented style as well as an ORM-oriented style.

    .. container:: orm-header

        **ORM readers, stay with us!**

        As with other sections, Core users can skip the ORM sections, but ORM users
        would best be familiar with these objects from both perspectives.
        The :class:`.Table` object discussed here is declared in a more indirect
        (and also fully Python-typed) way when using the ORM, however there is still
        a :class:`.Table` object within the ORM's configuration.


.. rst-class:: core-header, orm-dependency


.. _tutorial_core_metadata:

使用表对象设置元数据
---------------------------------------

Setting up MetaData with Table objects

.. tab:: 中文

    当我们使用关系数据库时，数据库中我们查询的基本数据保持结构称为 **表(table)**。
    在 SQLAlchemy 中，数据库“表”最终由一个名为 :class:`_schema.Table` 的 Python 对象表示。

    要开始使用 SQLAlchemy 表达式语言，我们需要构建表示我们感兴趣的所有数据库表的 :class:`_schema.Table` 对象。:class:`_schema.Table` 是通过编程构建的，可以直接使用 :class:`_schema.Table` 构造函数，或间接使用 ORM 映射类（在 :ref:`tutorial_orm_table_metadata` 中描述）。还可以选择从现有数据库加载部分或全部表信息，这称为 :term:`reflection` 。

    无论使用哪种方法，我们总是从一个集合开始，这个集合是我们放置表的地方，称为 :class:`_schema.MetaData` 对象。该对象本质上是围绕 Python 字典的 :term:`facade`，存储一系列键为字符串名称的 :class:`_schema.Table` 对象。虽然 ORM 提供了一些获取此集合的选项，但我们始终可以选择直接创建一个集合，如下所示：

        >>> from sqlalchemy import MetaData
        >>> metadata_obj = MetaData()

    一旦我们有了 :class:`_schema.MetaData` 对象，我们就可以声明一些 :class:`_schema.Table` 对象。本教程将从经典的 SQLAlchemy 教程模型开始，其中有一个名为 ``user_account`` 的表，用于存储例如网站用户的表，以及一个相关的表 ``address``，用于存储与 ``user_account`` 表中的行关联的电子邮件地址。当完全不使用 ORM 声明模型时，我们直接构建每个 :class:`_schema.Table` 对象，通常将每个对象分配给一个变量，这将是我们在应用代码中引用表的方式：

        >>> from sqlalchemy import Table, Column, Integer, String
        >>> user_table = Table(
        ...     "user_account",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30)),
        ...     Column("fullname", String),
        ... )

    在上面的示例中，当我们希望编写引用数据库中 ``user_account`` 表的代码时，我们将使用 ``user_table`` Python 变量来引用它。

    .. topic:: 我在程序中何时创建 ``MetaData`` 对象？

       为整个应用程序创建一个 :class:`_schema.MetaData` 对象是最常见的情况，通常在应用程序的单个位置作为模块级变量表示，通常在“models”或“dbschema”类型的包中。通常通过 ORM 中心的 :class:`_orm.registry` 或 :ref:`Declarative Base <tutorial_orm_declarative_base>` 基类访问 :class:`_schema.MetaData`，以便在 ORM 和 Core 声明的 :class:`_schema.Table` 对象之间共享同一个 :class:`_schema.MetaData`。

       也可以有多个 :class:`_schema.MetaData` 集合；:class:`_schema.Table` 对象可以在没有限制的情况下引用其他集合中的 :class:`_schema.Table` 对象。然而，对于彼此相关的 :class:`_schema.Table` 对象组，从声明它们的角度以及从 DDL（即 CREATE 和 DROP）语句按正确顺序发出的角度来看，在单个 :class:`_schema.MetaData` 集合中设置它们实际上要简单得多。

.. tab:: 英文

    When we work with a relational database, the basic data-holding structure
    in the database which we query from is known as a **table**.
    In SQLAlchemy, the database "table" is ultimately represented
    by a Python object similarly named :class:`_schema.Table`.

    To start using the SQLAlchemy Expression Language, we will want to have
    :class:`_schema.Table` objects constructed that represent all of the database
    tables we are interested in working with. The :class:`_schema.Table` is
    constructed programmatically, either directly by using the
    :class:`_schema.Table` constructor, or indirectly by using ORM Mapped classes
    (described later at :ref:`tutorial_orm_table_metadata`).  There is also the
    option to load some or all table information from an existing database,
    called :term:`reflection`.

    .. comment:  the word "simply" is used below.  While I dont like this word, I am
       using it here to stress that creating the MetaData directly will not
       introduce complexity (as long as one knows to associate it w/ declarative
       base)

    Whichever kind of approach is used, we always start out with a collection
    that will be where we place our tables known as the :class:`_schema.MetaData`
    object.  This object is essentially a :term:`facade` around a Python dictionary
    that stores a series of :class:`_schema.Table` objects keyed to their string
    name.   While the ORM provides some options on where to get this collection,
    we always have the option to simply make one directly, which looks like::

        >>> from sqlalchemy import MetaData
        >>> metadata_obj = MetaData()

    Once we have a :class:`_schema.MetaData` object, we can declare some
    :class:`_schema.Table` objects. This tutorial will start with the classic
    SQLAlchemy tutorial model, which has a table called ``user_account`` that
    stores, for example, the users of a website, and a related table ``address``,
    which stores email addresses associated with rows in the ``user_account``
    table. When not using ORM Declarative models at all, we construct each
    :class:`_schema.Table` object directly, typically assigning each to a variable
    that will be how we will refer to the table in application code::

        >>> from sqlalchemy import Table, Column, Integer, String
        >>> user_table = Table(
        ...     "user_account",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30)),
        ...     Column("fullname", String),
        ... )

    With the above example, when we wish to write code that refers to the
    ``user_account`` table in the database, we will use the ``user_table``
    Python variable to refer to it.

    .. topic:: When do I make a ``MetaData`` object in my program?

       Having a single :class:`_schema.MetaData` object for an entire application is
       the most common case, represented as a module-level variable in a single place
       in an application, often in a "models" or "dbschema" type of package. It is
       also very common that the :class:`_schema.MetaData` is accessed via an
       ORM-centric :class:`_orm.registry` or
       :ref:`Declarative Base <tutorial_orm_declarative_base>` base class, so that
       this same :class:`_schema.MetaData` is shared among ORM- and Core-declared
       :class:`_schema.Table` objects.

       There can be multiple :class:`_schema.MetaData` collections as well;
       :class:`_schema.Table` objects can refer to :class:`_schema.Table` objects
       in other collections without restrictions. However, for groups of
       :class:`_schema.Table` objects that are related to each other, it is in
       practice much more straightforward to have them set up within a single
       :class:`_schema.MetaData` collection, both from the perspective of declaring
       them, as well as from the perspective of DDL (i.e. CREATE and DROP) statements
       being emitted in the correct order.


``Table`` 的组件
^^^^^^^^^^^^^^^^^^^^^^^

Components of ``Table``

.. tab:: 中文

    我们可以看到，Python 中编写的 :class:`_schema.Table` 结构类似于 SQL 的 CREATE TABLE 语句；从表名开始，然后列出每一列，每一列都有一个名称和数据类型。我们上面使用的对象是：

    * :class:`_schema.Table` - 表示一个数据库表，并将其分配给 :class:`_schema.MetaData` 集合。

    * :class:`_schema.Column` - 表示数据库表中的一列，并将其分配给 :class:`_schema.Table` 对象。:class:`_schema.Column` 通常包括一个字符串名称和一个类型对象。在父类 :class:`_schema.Table` 中，:class:`_schema.Column` 对象的集合通常通过位于 :attr:`_schema.Table.c` 的关联数组访问：

        >>> user_table.c.name
        Column('name', String(length=30), table=<user_account>)

        >>> user_table.c.keys()
        ['id', 'name', 'fullname']

    * :class:`_types.Integer`, :class:`_types.String` - 这些类表示 SQL 数据类型，可以实例化或不实例化传递给 :class:`_schema.Column`。在上面，我们希望将“name”列的长度设置为“30”，因此实例化了 ``String(30)``。但对于“id”和“fullname”，我们没有指定这些，因此我们可以传递类本身。

    .. seealso::

        :class:`_schema.MetaData`、:class:`_schema.Table` 和 :class:`_schema.Column` 的参考和 API 文档在 :ref:`metadata_toplevel`。
        数据类型的参考文档在 :ref:`types_toplevel`。

    在接下来的部分中，我们将说明 :class:`_schema.Table` 的基本功能之一，即在特定数据库连接上生成 :term:`DDL`。但首先我们将声明第二个 :class:`_schema.Table`。

.. tab:: 英文

    We can observe that the :class:`_schema.Table` construct as written in Python
    has a resemblance to a SQL CREATE TABLE statement; starting with the table
    name, then listing out each column, where each column has a name and a
    datatype. The objects we use above are:

    * :class:`_schema.Table` - represents a database table and assigns itself to a :class:`_schema.MetaData` collection.

    * :class:`_schema.Column` - represents a column in a database table, and
      assigns itself to a :class:`_schema.Table` object.   The :class:`_schema.Column`
      usually includes a string name and a type object.   The collection of
      :class:`_schema.Column` objects in terms of the parent :class:`_schema.Table`
      are typically accessed via an associative array located at :attr:`_schema.Table.c`::

        >>> user_table.c.name
        Column('name', String(length=30), table=<user_account>)

        >>> user_table.c.keys()
        ['id', 'name', 'fullname']

    * :class:`_types.Integer`, :class:`_types.String` - these classes represent
      SQL datatypes and can be passed to a :class:`_schema.Column` with or without
      necessarily being instantiated.  Above, we want to give a length of "30" to
      the "name" column, so we instantiated ``String(30)``.  But for "id" and
      "fullname" we did not specify these, so we can send the class itself.

    .. seealso::

        The reference and API documentation for :class:`_schema.MetaData`,
        :class:`_schema.Table` and :class:`_schema.Column` is at :ref:`metadata_toplevel`.
        The reference documentation for datatypes is at :ref:`types_toplevel`.

    In an upcoming section, we will illustrate one of the fundamental
    functions of :class:`_schema.Table` which
    is to generate :term:`DDL` on a particular database connection.  But first
    we will declare a second :class:`_schema.Table`.

声明简单约束
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Declaring Simple Constraints

.. tab:: 中文

    示例 ``user_table`` 中的第一个 :class:`_schema.Column` 包含 :paramref:`_schema.Column.primary_key` 参数，这是一个指示该 :class:`_schema.Column` 应成为此表主键的一部分的简便方法。主键本身通常是隐式声明的，并由 :class:`_schema.PrimaryKeyConstraint` 构造表示，我们可以在 :class:`_schema.Table` 对象上的 :attr:`_schema.Table.primary_key` 属性上看到：

        >>> user_table.primary_key
        PrimaryKeyConstraint(Column('id', Integer(), table=<user_account>, primary_key=True, nullable=False))

    最常显式声明的约束是对应于数据库 :term:`foreign key constraint` 的 :class:`_schema.ForeignKeyConstraint` 对象。当我们声明彼此相关的表时，SQLAlchemy 使用这些外键约束声明的存在，不仅在 CREATE 语句中向数据库发出它们，还帮助构建 SQL 表达式。

    仅涉及目标表上的单列的 :class:`_schema.ForeignKeyConstraint` 通常使用列级简写符号通过 :class:`_schema.ForeignKey` 对象声明。下面我们声明一个第二个表 ``address``，它将具有一个引用 ``user`` 表的外键约束：

        >>> from sqlalchemy import ForeignKey
        >>> address_table = Table(
        ...     "address",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("user_id", ForeignKey("user_account.id"), nullable=False),
        ...     Column("email_address", String, nullable=False),
        ... )

    上表还具有第三种约束，即 SQL 中的 "NOT NULL" 约束，上面使用 :paramref:`_schema.Column.nullable` 参数指示。

    .. tip:: 
      
      在 :class:`_schema.Column` 定义中使用 :class:`_schema.ForeignKey` 对象时，我们可以省略该 :class:`_schema.Column` 的数据类型；它会自动从相关列的数据类型推断出来，在上面的示例中是 ``user_account.id`` 列的 :class:`_types.Integer` 数据类型。

    在下一节中，我们将发出 ``user`` 和 ``address`` 表的完整 DDL 以查看完成的结果。

.. tab:: 英文

    The first :class:`_schema.Column` in the example ``user_table`` includes the
    :paramref:`_schema.Column.primary_key` parameter which is a shorthand technique
    of indicating that this :class:`_schema.Column` should be part of the primary
    key for this table.  The primary key itself is normally declared implicitly
    and is represented by the :class:`_schema.PrimaryKeyConstraint` construct,
    which we can see on the :attr:`_schema.Table.primary_key`
    attribute on the :class:`_schema.Table` object::

        >>> user_table.primary_key
        PrimaryKeyConstraint(Column('id', Integer(), table=<user_account>, primary_key=True, nullable=False))

    The constraint that is most typically declared explicitly is the
    :class:`_schema.ForeignKeyConstraint` object that corresponds to a database
    :term:`foreign key constraint`.  When we declare tables that are related to
    each other, SQLAlchemy uses the presence of these foreign key constraint
    declarations not only so that they are emitted within CREATE statements to
    the database, but also to assist in constructing SQL expressions.

    A :class:`_schema.ForeignKeyConstraint` that involves only a single column
    on the target table is typically declared using a column-level shorthand notation
    via the :class:`_schema.ForeignKey` object.  Below we declare a second table
    ``address`` that will have a foreign key constraint referring to the ``user``
    table::

        >>> from sqlalchemy import ForeignKey
        >>> address_table = Table(
        ...     "address",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("user_id", ForeignKey("user_account.id"), nullable=False),
        ...     Column("email_address", String, nullable=False),
        ... )

    The table above also features a third kind of constraint, which in SQL is the
    "NOT NULL" constraint, indicated above using the :paramref:`_schema.Column.nullable`
    parameter.

    .. tip:: When using the :class:`_schema.ForeignKey` object within a
       :class:`_schema.Column` definition, we can omit the datatype for that
       :class:`_schema.Column`; it is automatically inferred from that of the
       related column, in the above example the :class:`_types.Integer` datatype
       of the ``user_account.id`` column.

    In the next section we will emit the completed DDL for the ``user`` and
    ``address`` table to see the completed result.

.. _tutorial_emitting_ddl:

向数据库发送 DDL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Emitting DDL to the Database

.. tab:: 中文

    我们已经构建了一个对象结构，表示数据库中的两个表，从根 :class:`_schema.MetaData` 对象开始，然后是两个 :class:`_schema.Table` 对象，每个对象都包含一组 :class:`_schema.Column` 和 :class:`_schema.Constraint` 对象。这种对象结构将成为我们在 Core 和 ORM 中执行大多数操作的核心。

    我们可以使用这个结构做的第一件有用的事情是向我们的 SQLite 数据库发出 CREATE TABLE 语句，或 :term:`DDL`，以便我们可以插入和查询数据。我们已经拥有执行此操作所需的所有工具，通过在我们的 :class:`_schema.MetaData` 上调用 :meth:`_schema.MetaData.create_all` 方法，并向其发送指向目标数据库的 :class:`_engine.Engine`：

    .. sourcecode:: pycon+sql

        >>> metadata_obj.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        CREATE TABLE user_account (
            id INTEGER NOT NULL,
            name VARCHAR(30),
            fullname VARCHAR,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE address (
            id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            email_address VARCHAR NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES user_account (id)
        )
        ...
        COMMIT

    上面的 DDL 创建过程包括一些特定于 SQLite 的 PRAGMA 语句，这些语句在发出 CREATE 之前测试每个表的存在。完整的步骤系列也包含在 BEGIN/COMMIT 对中以适应事务性 DDL。

    创建过程还负责按正确的顺序发出 CREATE 语句；上面，FOREIGN KEY 约束依赖于 ``user`` 表的存在，因此 ``address`` 表是第二个创建的。在更复杂的依赖场景中，FOREIGN KEY 约束也可以在事实发生后使用 ALTER 应用于表。

    :class:`_schema.MetaData` 对象还具有 :meth:`_schema.MetaData.drop_all` 方法，该方法将按照发出 CREATE 的相反顺序发出 DROP 语句以删除模式元素。

    .. topic:: 迁移工具通常是合适的

        总体而言，:class:`_schema.MetaData` 的 CREATE / DROP 功能对于测试套件、小型和/或新应用程序以及使用短期数据库的应用程序很有用。然而，对于长期管理应用程序数据库架构，构建在 SQLAlchemy 之上的架构管理工具（如 `Alembic <https://alembic.sqlalchemy.org>`_ ）可能是更好的选择，因为它可以在应用程序设计变化时逐步更改固定的数据库架构并协调这一过程。

.. tab:: 英文

    We've constructed an object structure that represents
    two database tables in a database, starting at the root :class:`_schema.MetaData`
    object, then into two :class:`_schema.Table` objects, each of which hold
    onto a collection of :class:`_schema.Column` and :class:`_schema.Constraint`
    objects.   This object structure will be at the center of most operations
    we perform with both Core and ORM going forward.

    The first useful thing we can do with this structure will be to emit CREATE
    TABLE statements, or :term:`DDL`, to our SQLite database so that we can insert
    and query data from them.   We have already all the tools needed to do so, by
    invoking the
    :meth:`_schema.MetaData.create_all` method on our :class:`_schema.MetaData`,
    sending it the :class:`_engine.Engine` that refers to the target database:

    .. sourcecode:: pycon+sql

        >>> metadata_obj.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        CREATE TABLE user_account (
            id INTEGER NOT NULL,
            name VARCHAR(30),
            fullname VARCHAR,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE address (
            id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            email_address VARCHAR NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES user_account (id)
        )
        ...
        COMMIT

    The DDL create process above includes some SQLite-specific PRAGMA statements
    that test for the existence of each table before emitting a CREATE.   The full
    series of steps are also included within a BEGIN/COMMIT pair to accommodate
    for transactional DDL.

    The create process also takes care of emitting CREATE statements in the correct
    order; above, the FOREIGN KEY constraint is dependent on the ``user`` table
    existing, so the ``address`` table is created second.   In more complicated
    dependency scenarios the FOREIGN KEY constraints may also be applied to tables
    after the fact using ALTER.

    The :class:`_schema.MetaData` object also features a
    :meth:`_schema.MetaData.drop_all` method that will emit DROP statements in the
    reverse order as it would emit CREATE in order to drop schema elements.

    .. topic:: Migration tools are usually appropriate

        Overall, the CREATE / DROP feature of :class:`_schema.MetaData` is useful
        for test suites, small and/or new applications, and applications that use
        short-lived databases.  For management of an application database schema
        over the long term however, a schema management tool such as `Alembic
        <https://alembic.sqlalchemy.org>`_, which builds upon SQLAlchemy, is likely
        a better choice, as it can manage and orchestrate the process of
        incrementally altering a fixed database schema over time as the design of
        the application changes.


.. rst-class:: orm-header

.. _tutorial_orm_table_metadata:

使用 ORM 声明形式定义表元数据
----------------------------------------------------

Using ORM Declarative Forms to Define Table Metadata

.. tab:: 中文

    .. topic:: 另一种创建 Table 对象的方法？

      前面的示例说明了直接使用 :class:`_schema.Table` 对象，这在构建 SQL 表达式时是 SQLAlchemy 最终引用数据库表的方式。如前所述，SQLAlchemy ORM 提供了一个围绕 :class:`_schema.Table` 声明过程的 facade，称为 **声明式表(Declarative Table)**。声明式表过程实现了与我们在上一节中相同的目标，即构建 :class:`_schema.Table` 对象，但在此过程中还为我们提供了称为 :term:`ORM mapped class` 的东西，或简称为“映射类”。映射类是使用 ORM 时 SQL 最常见的基础单元，在现代 SQLAlchemy 中也可以与 Core 中心的使用非常有效地结合。

      使用声明式表的一些好处包括：

      * 设置列定义的方式更加简洁和符合 Python 风格，其中可以使用 Python 类型来表示数据库中使用的 SQL 类型

      * 生成的映射类可以用于形成 SQL 表达式，在许多情况下可以维护 :pep:`484` 类型信息，这些信息被静态分析工具如 Mypy 和 IDE 类型检查器拾取

      * 允许一次性声明表元数据和用于持久化 / 对象加载操作的 ORM 映射类。

      本节将说明使用声明式表构建前几节中的相同 :class:`_schema.Table` 元数据。

    使用 ORM 时，我们声明 :class:`_schema.Table` 元数据的过程通常与声明 :term:`mapped` 类的过程相结合。映射类是我们希望创建的任何 Python 类，它将在其上具有将链接到数据库表中列的属性。虽然有几种实现方式，但最常见的样式称为 :ref:`declarative <orm_declarative_mapper_config_toplevel>`，它允许我们同时声明用户定义的类和 :class:`_schema.Table` 元数据。

.. tab:: 英文

    .. topic:: Another way to make Table objects?

      The preceding examples illustrated direct use of the :class:`_schema.Table`
      object, which underlies how SQLAlchemy ultimately refers to database tables
      when constructing SQL expressions. As mentioned, the SQLAlchemy ORM provides
      for a facade around the :class:`_schema.Table` declaration process referred
      towards as **Declarative Table**.   The Declarative Table process accomplishes
      the same goal as we had in the previous section, that of building
      :class:`_schema.Table` objects, but also within that process gives us
      something else called an :term:`ORM mapped class`, or just "mapped class".
      The mapped class is the
      most common foundational unit of SQL when using the ORM, and in modern
      SQLAlchemy can also be used quite effectively with Core-centric
      use as well.

      Some benefits of using Declarative Table include:

      * A more succinct and Pythonic style of setting up column definitions, where
        Python types may be used to represent SQL types to be used in the
        database

      * The resulting mapped class can be
        used to form SQL expressions that in many cases maintain :pep:`484` typing
        information that's picked up by static analysis tools such as
        Mypy and IDE type checkers

      * Allows declaration of table metadata and the ORM mapped class used in
        persistence / object loading operations all at once.

      This section will illustrate the same :class:`_schema.Table` metadata
      of the previous section(s) being constructed using Declarative Table.

    When using the ORM, the process by which we declare :class:`_schema.Table` metadata
    is usually combined with the process of declaring :term:`mapped` classes.
    The mapped class is any Python class we'd like to create, which will then
    have attributes on it that will be linked to the columns in a database table.
    While there are a few varieties of how this is achieved, the most common
    style is known as
    :ref:`declarative <orm_declarative_mapper_config_toplevel>`, and allows us
    to declare our user-defined classes and :class:`_schema.Table` metadata
    at once.

.. _tutorial_orm_declarative_base:

建立声明基类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Establishing a Declarative Base

.. tab:: 中文

    当使用 ORM 时，:class:`_schema.MetaData` 集合仍然存在，但它本身与一个仅限 ORM 的构造相关，通常称为 **声明基类(Declarative Base)**。获取新的声明基类最便捷的方法是创建一个继承自 SQLAlchemy :class:`_orm.DeclarativeBase` 类的新类：

        >>> from sqlalchemy.orm import DeclarativeBase
        >>> class Base(DeclarativeBase):
        ...     pass

    上面的 ``Base`` 类就是我们所说的声明基类。当我们创建继承自 ``Base`` 的新类，并结合适当的类级指令时，它们将在类创建时分别被建立为新的 **ORM 映射类**，每个类通常（但不排除其他情况）引用特定的 :class:`_schema.Table` 对象。

    声明基类引用为我们自动创建的 :class:`_schema.MetaData` 集合，假设我们没有从外部提供一个。此 :class:`.MetaData` 集合可以通过 :attr:`_orm.DeclarativeBase.metadata` 类级属性访问。当我们创建新的映射类时，它们每个将引用此 :class:`.MetaData` 集合中的一个 :class:`.Table`：

        >>> Base.metadata
        MetaData()

    声明基类还引用一个称为 :class:`_orm.registry` 的集合，这是 SQLAlchemy ORM 中的中央“映射配置”单元。虽然很少直接访问此对象，但它是映射配置过程的核心，因为一组 ORM 映射类将通过此注册表相互协调。与 :class:`.MetaData` 的情况一样，我们的声明基类也为我们创建了一个 :class:`_orm.registry` （同样可以选择传递我们自己的 :class:`_orm.registry`），我们可以通过 :attr:`_orm.DeclarativeBase.registry` 类变量访问：

        >>> Base.registry
        <sqlalchemy.orm.decl_api.registry object at 0x...>

    .. topic::  使用 ``registry`` 进行其他映射的方法

      :class:`_orm.DeclarativeBase` 并不是映射类的唯一方法，只是最常见的方法。:class:`_orm.registry` 还提供其他映射配置模式，包括面向装饰器和命令式的映射类方法。还有完全支持在映射时创建 Python 数据类。参考文档在 :ref:`mapper_config_toplevel` 中有详细介绍。

.. tab:: 英文

    When using the ORM, the :class:`_schema.MetaData` collection remains present,
    however it itself is associated with an ORM-only construct commonly referred
    towards as the **Declarative Base**.   The most expedient way to acquire
    a new Declarative Base is to create a new class that subclasses the
    SQLAlchemy :class:`_orm.DeclarativeBase` class::

        >>> from sqlalchemy.orm import DeclarativeBase
        >>> class Base(DeclarativeBase):
        ...     pass

    Above, the ``Base`` class is what we'll call the Declarative Base.
    When we make new classes that are subclasses of ``Base``, combined with
    appropriate class-level directives, they will each be established as a new
    **ORM mapped class** at class creation time, each one typically (but not
    exclusively) referring to a particular :class:`_schema.Table` object.

    The Declarative Base refers to a :class:`_schema.MetaData` collection that is
    created for us automatically, assuming we didn't provide one from the outside.
    This :class:`.MetaData` collection is accessible via the
    :attr:`_orm.DeclarativeBase.metadata` class-level attribute. As we create new
    mapped classes, they each will reference a :class:`.Table` within this
    :class:`.MetaData` collection::

        >>> Base.metadata
        MetaData()

    The Declarative Base also refers to a collection called :class:`_orm.registry`, which
    is the central "mapper configuration" unit in the SQLAlchemy ORM.  While
    seldom accessed directly, this object is central to the mapper configuration
    process, as a set of ORM mapped classes will coordinate with each other via
    this registry.   As was the case with :class:`.MetaData`, our Declarative
    Base also created a :class:`_orm.registry` for us (again with options to
    pass our own :class:`_orm.registry`), which we can access
    via the :attr:`_orm.DeclarativeBase.registry` class variable::

        >>> Base.registry
        <sqlalchemy.orm.decl_api.registry object at 0x...>

    .. topic::  Other ways to map with the ``registry``

      :class:`_orm.DeclarativeBase` is not the only way to map classes, only the
      most common.  :class:`_orm.registry` also provides other mapper
      configurational patterns, including decorator-oriented and imperative ways
      to map classes.  There's also full support for creating Python dataclasses
      while mapping.  The reference documentation at :ref:`mapper_config_toplevel`
      has it all.


.. _tutorial_declaring_mapped_classes:

声明映射类
^^^^^^^^^^^^^^^^^^^^^^^^

Declaring Mapped Classes

.. tab:: 中文

    在建立了 ``Base`` 类后，我们现在可以定义 ``user_account`` 和 ``address`` 表的 ORM 映射类，即新的 ``User`` 和 ``Address`` 类。下面我们展示最现代的声明形式，它使用 :pep:`484` 类型注释，并通过一个特殊类型 :class:`.Mapped` 来指示属性应映射为特定类型：

        >>> from typing import List
        >>> from typing import Optional
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship

        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str] = mapped_column(String(30))
        ...     fullname: Mapped[Optional[str]]
        ...
        ...     addresses: Mapped[List["Address"]] = relationship(back_populates="user")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     email_address: Mapped[str]
        ...     user_id = mapped_column(ForeignKey("user_account.id"))
        ...
        ...     user: Mapped[User] = relationship(back_populates="addresses")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Address(id={self.id!r}, email_address={self.email_address!r})"

    上面的两个类 ``User`` 和 ``Address`` 现在称为 **ORM 映射类**，可用于后续介绍的 ORM 持久化和查询操作。这些类的细节包括：

    * 每个类引用在声明映射过程中生成的 :class:`_schema.Table` 对象，通过将字符串分配给 :attr:`_orm.DeclarativeBase.__tablename__` 属性命名。一旦类创建，这个生成的 :class:`_schema.Table` 可以通过 :attr:`_orm.DeclarativeBase.__table__` 属性获取。

    * 如前所述，这种形式称为 :ref:`orm_declarative_table_configuration`。另一种声明样式是直接构建 :class:`_schema.Table` 对象，并直接将其分配给 :attr:`_orm.DeclarativeBase.__table__`。这种样式称为 :ref:`Declarative with Imperative Table <orm_imperative_table_configuration>`。

    * 为了在 :class:`_schema.Table` 中指示列，我们使用 :func:`_orm.mapped_column` 构造，并结合基于 :class:`_orm.Mapped` 类型的类型注释。这个对象将生成应用于构建 :class:`_schema.Table` 的 :class:`_schema.Column` 对象。

    * 对于具有简单数据类型且没有其他选项的列，我们可以单独使用 :class:`_orm.Mapped` 类型注释，使用简单的 Python 类型如 ``int`` 和 ``str`` 表示 :class:`.Integer` 和 :class:`.String`。在声明映射过程中，如何解释 Python 类型的自定义非常开放；请参阅章节 :ref:`orm_declarative_mapped_column` 和 :ref:`orm_declarative_mapped_column_type_map` 以了解背景。

    * 可以根据 ``Optional[<typ>]`` 类型注释（或其等效形式 ``<typ> | None`` 或 ``Union[<typ>, None]``）来声明列为“可为空”或“不可为空”。也可以显式使用 :paramref:`_orm.mapped_column.nullable` 参数（不必与注释的可选性匹配）。

    * 使用显式类型注释是 **完全可选的** 。我们也可以在没有注释的情况下使用 :func:`_orm.mapped_column`。使用这种形式时，我们将在每个 :func:`_orm.mapped_column` 构造中使用更显式的类型对象如 :class:`.Integer` 和 :class:`.String` 以及 ``nullable=False`` 根据需要。

    * 另外两个属性 ``User.addresses`` 和 ``Address.user`` 定义了称为 :func:`_orm.relationship` 的不同类型的属性，具有如图所示的类似注释感知配置样式。:func:`_orm.relationship` 构造在 :ref:`tutorial_orm_related_objects` 中有更详细的讨论。

    * 如果我们不声明自己的 ``__init__()`` 方法，类会自动获得一个 ``__init__()`` 方法。此方法的默认形式接受所有属性名称作为可选的关键字参数：

        >>> sandy = User(name="sandy", fullname="Sandy Cheeks")

      要自动生成一个提供位置参数以及具有默认关键字值参数的完善 ``__init__()`` 方法，可以使用在 :ref:`orm_declarative_native_dataclasses` 中介绍的数据类功能。当然，也总是可以选择使用显式 ``__init__()`` 方法。

    * 添加 ``__repr__()`` 方法以便我们获得可读的字符串输出；这些方法没有必须存在的要求。与 ``__init__()`` 的情况一样，可以使用 :ref:`dataclasses <orm_declarative_native_dataclasses>` 功能自动生成 ``__repr__()`` 方法。

    .. topic:: 旧 Declarative 去哪里了？

        使用 SQLAlchemy 1.4 或以前版本的用户会注意到，上述映射使用了与以前截然不同的形式；不仅在声明映射中使用了 :func:`_orm.mapped_column` 而不是 :class:`.Column`，还使用了 Python 类型注释来派生列信息。

        为了为“旧”方式的用户提供背景信息，声明映射仍然可以像以前一样使用 :class:`.Column` 对象（以及使用 :func:`_orm.declarative_base` 函数创建基类），这些形式将继续支持，没有计划取消支持。这两种工具被新构造取代的主要原因首先是为了与 :pep:`484` 工具（包括 VSCode 等 IDE 和 Mypy 和 Pyright 等类型检查器）无缝集成，而无需插件。其次，从类型注释派生声明是 SQLAlchemy 与 Python 数据类集成的一部分，现在可以从映射中 :ref:`natively generated <orm_declarative_native_dataclasses>`。

        对于喜欢“旧”方式但仍希望他们的 IDE 不会错误地报告声明映射的类型错误的用户，:func:`_orm.mapped_column` 构造是 ORM 声明映射中 :class:`.Column` 的直接替代品（注意 :func:`_orm.mapped_column` 仅适用于 ORM 声明映射；不能在 :class:`.Table` 构造中使用），类型注释是可选的。我们的上面映射可以不带注释写成：

            class User(Base):
                __tablename__ = "user_account"

                id = mapped_column(Integer, primary_key=True)
                name = mapped_column(String(30), nullable=False)
                fullname = mapped_column(String)

                addresses = relationship("Address", back_populates="user")

                # ... 定义继续

        上面的类相比使用 :class:`.Column` 直接的类有一个优势，即 ``User`` 类以及 ``User`` 的实例将在不使用插件的情况下向类型工具指示正确的类型信息。:func:`_orm.mapped_column` 还允许额外的 ORM 特定参数来配置行为，如延迟列加载，以前需要使用单独的 :func:`_orm.deferred` 函数与 :class:`_schema.Column` 一起使用。

        有一个示例显示如何将旧样式的声明类转换为新样式，可以在 :ref:`whatsnew_20_orm_declarative_typing` 中的 :ref:`whatsnew_20_toplevel` 指南中看到。

    .. seealso::

        :ref:`orm_mapping_styles` - 不同 ORM 配置样式的完整背景。

        :ref:`orm_declarative_mapping` - 声明类映射概述

        :ref:`orm_declarative_table` - 如何使用 :func:`_orm.mapped_column` 和 :class:`_orm.Mapped` 定义在使用声明时要映射的 :class:`_schema.Table` 中的列的详细信息。

.. tab:: 英文

    With the ``Base`` class established, we can now define ORM mapped classes
    for the ``user_account`` and ``address`` tables in terms of new classes ``User`` and
    ``Address``.  We illustrate below the most modern form of Declarative, which
    is driven from :pep:`484` type annotations using a special type
    :class:`.Mapped`, which indicates attributes to be mapped as particular
    types::

        >>> from typing import List
        >>> from typing import Optional
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship

        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str] = mapped_column(String(30))
        ...     fullname: Mapped[Optional[str]]
        ...
        ...     addresses: Mapped[List["Address"]] = relationship(back_populates="user")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     email_address: Mapped[str]
        ...     user_id = mapped_column(ForeignKey("user_account.id"))
        ...
        ...     user: Mapped[User] = relationship(back_populates="addresses")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Address(id={self.id!r}, email_address={self.email_address!r})"

    The two classes above, ``User`` and ``Address``, are now called
    as **ORM Mapped Classes**, and are available for use in
    ORM persistence and query operations, which will be described later.  Details
    about these classes include:

    * Each class refers to a :class:`_schema.Table` object that was generated as
      part of the declarative mapping process, which is named by assigning
      a string to the :attr:`_orm.DeclarativeBase.__tablename__` attribute.
      Once the class is created, this generated :class:`_schema.Table` is available
      from the :attr:`_orm.DeclarativeBase.__table__` attribute.

    * As mentioned previously, this form
      is known as :ref:`orm_declarative_table_configuration`.  One
      of several alternative declaration styles would instead have us
      build the :class:`_schema.Table` object directly, and **assign** it
      directly to :attr:`_orm.DeclarativeBase.__table__`.  This style
      is known as :ref:`Declarative with Imperative Table <orm_imperative_table_configuration>`.

    * To indicate columns in the :class:`_schema.Table`, we use the
      :func:`_orm.mapped_column` construct, in combination with
      typing annotations based on the :class:`_orm.Mapped` type.  This object
      will generate :class:`_schema.Column` objects that are applied to the
      construction of the :class:`_schema.Table`.

    * For columns with simple datatypes and no other options, we can indicate a
      :class:`_orm.Mapped` type annotation alone, using simple Python types like
      ``int`` and ``str`` to mean :class:`.Integer` and :class:`.String`.
      Customization of how Python types are interpreted within the Declarative
      mapping process is very open ended; see the sections
      :ref:`orm_declarative_mapped_column` and
      :ref:`orm_declarative_mapped_column_type_map` for background.

    * A column can be declared as "nullable" or "not null" based on the
      presence of the ``Optional[<typ>]`` type annotation (or its equivalents,
      ``<typ> | None`` or ``Union[<typ>, None]``).  The
      :paramref:`_orm.mapped_column.nullable` parameter may also be used explicitly
      (and does not have to match the annotation's optionality).

    * Use of explicit typing annotations is **completely
      optional**.  We can also use :func:`_orm.mapped_column` without annotations.
      When using this form, we would use more explicit type objects like
      :class:`.Integer` and :class:`.String` as well as ``nullable=False``
      as needed within each :func:`_orm.mapped_column` construct.

    * Two additional attributes, ``User.addresses`` and ``Address.user``, define
      a different kind of attribute called :func:`_orm.relationship`, which
      features similar annotation-aware configuration styles as shown.  The
      :func:`_orm.relationship` construct is discussed more fully at
      :ref:`tutorial_orm_related_objects`.

    * The classes are automatically given an ``__init__()`` method if we don't
      declare one of our own.  The default form of this method accepts all
      attribute names as optional keyword arguments::

        >>> sandy = User(name="sandy", fullname="Sandy Cheeks")

      To automatically generate a full-featured ``__init__()`` method which
      provides for positional arguments as well as arguments with default keyword
      values, the dataclasses feature introduced at
      :ref:`orm_declarative_native_dataclasses` may be used.  It's of course
      always an option to use an explicit ``__init__()`` method as well.

    * The ``__repr__()`` methods are added so that we get a readable string output;
      there's no requirement for these methods to be here.  As is the case
      with ``__init__()``, a ``__repr__()`` method
      can be generated automatically by using the
      :ref:`dataclasses <orm_declarative_native_dataclasses>` feature.

    .. topic::  Where'd the old Declarative go?

        Users of SQLAlchemy 1.4 or previous will note that the above mapping
        uses a dramatically different form than before; not only does it use
        :func:`_orm.mapped_column` instead of :class:`.Column` in the Declarative
        mapping, it also uses Python type annotations to derive column information.

        To provide context for users of the "old" way, Declarative mappings can
        still be made using :class:`.Column` objects (as well as using the
        :func:`_orm.declarative_base` function to create the base class) as before,
        and these forms will continue to be supported with no plans to
        remove support.  The reason these two facilities
        are superseded by new constructs is first and foremost to integrate
        smoothly with :pep:`484` tools, including IDEs such as VSCode and type
        checkers such as Mypy and Pyright, without the need for plugins. Secondly,
        deriving the declarations from type annotations is part of SQLAlchemy's
        integration with Python dataclasses, which can now be
        :ref:`generated natively <orm_declarative_native_dataclasses>` from mappings.

        For users who like the "old" way, but still desire their IDEs to not
        mistakenly report typing errors for their declarative mappings, the
        :func:`_orm.mapped_column` construct is a drop-in replacement for
        :class:`.Column` in an ORM Declarative mapping (note that
        :func:`_orm.mapped_column` is for ORM Declarative mappings only; it can't
        be used within a :class:`.Table` construct), and the type annotations are
        optional. Our mapping above can be written without annotations as::

            class User(Base):
                __tablename__ = "user_account"

                id = mapped_column(Integer, primary_key=True)
                name = mapped_column(String(30), nullable=False)
                fullname = mapped_column(String)

                addresses = relationship("Address", back_populates="user")

                # ... definition continues

        The above class has an advantage over one that uses :class:`.Column`
        directly, in that the ``User`` class as well as instances of ``User``
        will indicate the correct typing information to typing tools, without
        the use of plugins.  :func:`_orm.mapped_column` also allows for additional
        ORM-specific parameters to configure behaviors such as deferred column loading,
        which previously needed a separate :func:`_orm.deferred` function to be
        used with :class:`_schema.Column`.

        There's also an example of converting an old-style Declarative class
        to the new style, which can be seen at :ref:`whatsnew_20_orm_declarative_typing`
        in the :ref:`whatsnew_20_toplevel` guide.

    .. seealso::

        :ref:`orm_mapping_styles` - full background on different ORM configurational
        styles.

        :ref:`orm_declarative_mapping` - overview of Declarative class mapping

        :ref:`orm_declarative_table` - detail on how to use
        :func:`_orm.mapped_column` and :class:`_orm.Mapped` to define the columns
        within a :class:`_schema.Table` to be mapped when using Declarative.


从 ORM 映射向数据库发送 DDL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Emitting DDL to the database from an ORM mapping

.. tab:: 中文

    由于我们的 ORM 映射类引用了包含在 :class:`_schema.MetaData` 集合中的 :class:`_schema.Table` 对象，因此发出 DDL 的过程与前面在 :ref:`tutorial_emitting_ddl` 中描述的过程相同。在我们的例子中，我们已经在我们的 SQLite 数据库中生成了 ``user`` 和 ``address`` 表。如果我们还没有这样做，我们可以自由地使用与我们的 ORM 声明基类关联的 :class:`_schema.MetaData` 来执行此操作，通过从 :attr:`_orm.DeclarativeBase.metadata` 属性访问集合，然后像以前一样使用 :meth:`_schema.MetaData.create_all`。在这种情况下，运行 PRAGMA 语句，但由于发现已经存在这些表，因此不会生成新表：

    .. sourcecode:: pycon+sql

        >>> Base.metadata.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        COMMIT

.. tab:: 英文

    As our ORM mapped classes refer to :class:`_schema.Table` objects contained
    within a :class:`_schema.MetaData` collection, emitting DDL given the
    Declarative Base uses the same process as that described previously at
    :ref:`tutorial_emitting_ddl`. In our case, we have already generated the
    ``user`` and ``address`` tables in our SQLite database. If we had not done so
    already, we would be free to make use of the :class:`_schema.MetaData`
    associated with our ORM Declarative Base class in order to do so, by accessing
    the collection from the :attr:`_orm.DeclarativeBase.metadata` attribute and
    then using :meth:`_schema.MetaData.create_all` as before.  In this case,
    PRAGMA statements are run, but no new tables are generated since they
    are found to be present already:

    .. sourcecode:: pycon+sql

        >>> Base.metadata.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        COMMIT


.. rst-class:: core-header, orm-addin

.. _tutorial_table_reflection:

表反射
-------------------------------

Table Reflection

.. tab:: 中文

    .. topic:: 可选部分

        本节只是 **表反射(table reflection)** 相关主题的简要介绍，或如何从现有数据库自动生成 :class:`_schema.Table` 对象。希望继续编写查询的教程读者可以随意跳过本节。

    为了完善处理表元数据的部分，我们将说明在本节开始时提到的另一项操作，即 **表反射(table reflection)** 。表反射是指通过读取数据库的当前状态生成 :class:`_schema.Table` 和相关对象的过程。而在前面的章节中，我们在 Python 中声明了 :class:`_schema.Table` 对象，然后可以选择向数据库发出 DDL 以生成这样一个模式，反射过程则反其道而行之，从现有数据库开始生成用于表示该数据库中模式的 Python 数据结构。

    .. tip::  
      
      使用 SQLAlchemy 与现有数据库时没有必须使用反射的要求。通常情况下，SQLAlchemy 应用程序在 Python 中显式声明所有元数据，使其结构与现有数据库对应。元数据结构也不需要包括预先存在的数据库中不需要用于本地应用程序功能的表、列或其他约束和构造。

    作为反射的示例，我们将创建一个新的 :class:`_schema.Table` 对象，该对象表示我们在本文档前面部分手动创建的 ``some_table`` 对象。再次说明，有几种实现方式，但最基本的是构建一个 :class:`_schema.Table` 对象，给定表的名称和它将所属的 :class:`_schema.MetaData` 集合，然后不是指示单个 :class:`_schema.Column` 和 :class:`_schema.Constraint` 对象，而是使用 :paramref:`_schema.Table.autoload_with` 参数传递目标 :class:`_engine.Engine`：

    .. sourcecode:: pycon+sql

        >>> some_table = Table("some_table", metadata_obj, autoload_with=engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("some_table")
        [raw sql] ()
        SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
        [raw sql] ('some_table',)
        PRAGMA main.foreign_key_list("some_table")
        ...
        PRAGMA main.index_list("some_table")
        ...
        ROLLBACK{stop}

    在此过程结束时，``some_table`` 对象现在包含有关表中存在的 :class:`_schema.Column` 对象的信息，并且该对象的使用方式与我们显式声明的 :class:`_schema.Table` 完全相同：

        >>> some_table
        Table('some_table', MetaData(),
            Column('x', INTEGER(), table=<some_table>),
            Column('y', INTEGER(), table=<some_table>),
            schema=None)

    .. seealso::

        在 :ref:`metadata_reflection_toplevel` 阅读更多关于表和模式反射的信息。

        有关表反射的 ORM 相关变体，部分 :ref:`orm_declarative_reflected` 包括可用选项的概述。

.. tab:: 英文

    .. topic:: Optional Section

        This section is just a brief introduction to the related subject of
        **table reflection**, or how to generate :class:`_schema.Table`
        objects automatically from an existing database.  Tutorial readers who
        want to get on with writing queries can feel free to skip this section.

    To round out the section on working with table metadata, we will illustrate
    another operation that was mentioned at the beginning of the section,
    that of **table reflection**.   Table reflection refers to the process of
    generating :class:`_schema.Table` and related objects by reading the current
    state of a database.   Whereas in the previous sections we've been declaring
    :class:`_schema.Table` objects in Python, where we then have the option
    to emit DDL to the database to generate such a schema, the reflection process
    does these two steps in reverse, starting from an existing database
    and generating in-Python data structures to represent the schemas within
    that database.

    .. tip::  There is no requirement that reflection must be used in order to
      use SQLAlchemy with a pre-existing database.  It is entirely typical that
      the SQLAlchemy application declares all metadata explicitly in Python,
      such that its structure corresponds to that the existing database.
      The metadata structure also need not include tables, columns, or other
      constraints and constructs in the pre-existing database that are not needed
      for the local application to function.

    As an example of reflection, we will create a new :class:`_schema.Table`
    object which represents the ``some_table`` object we created manually in
    the earlier sections of this document.  There are again some varieties of
    how this is performed, however the most basic is to construct a
    :class:`_schema.Table` object, given the name of the table and a
    :class:`_schema.MetaData` collection to which it will belong, then
    instead of indicating individual :class:`_schema.Column` and
    :class:`_schema.Constraint` objects, pass it the target :class:`_engine.Engine`
    using the :paramref:`_schema.Table.autoload_with` parameter:

    .. sourcecode:: pycon+sql

        >>> some_table = Table("some_table", metadata_obj, autoload_with=engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("some_table")
        [raw sql] ()
        SELECT sql FROM  (SELECT * FROM sqlite_master UNION ALL   SELECT * FROM sqlite_temp_master) WHERE name = ? AND type in ('table', 'view')
        [raw sql] ('some_table',)
        PRAGMA main.foreign_key_list("some_table")
        ...
        PRAGMA main.index_list("some_table")
        ...
        ROLLBACK{stop}

    At the end of the process, the ``some_table`` object now contains the
    information about the :class:`_schema.Column` objects present in the table, and
    the object is usable in exactly the same way as a :class:`_schema.Table` that
    we declared explicitly::

        >>> some_table
        Table('some_table', MetaData(),
            Column('x', INTEGER(), table=<some_table>),
            Column('y', INTEGER(), table=<some_table>),
            schema=None)

    .. seealso::

        Read more about table and schema reflection at :ref:`metadata_reflection_toplevel`.

        For ORM-related variants of table reflection, the section
        :ref:`orm_declarative_reflected` includes an overview of the available
        options.

后续步骤
----------

Next Steps

.. tab:: 中文

    我们现在已经准备好了一个包含两个表的 SQLite 数据库，以及可以通过 :class:`_engine.Connection` 和/或 ORM :class:`_orm.Session` 与这些表交互的 Core 和 ORM 表导向构造。在接下来的章节中，我们将说明如何使用这些结构来创建、操作和选择数据。

.. tab:: 英文

    We now have a SQLite database ready to go with two tables present, and
    Core and ORM table-oriented constructs that we can use to interact with
    these tables via a :class:`_engine.Connection` and/or ORM
    :class:`_orm.Session`.  In the following sections, we will illustrate
    how to create, manipulate, and select data using these structures.
