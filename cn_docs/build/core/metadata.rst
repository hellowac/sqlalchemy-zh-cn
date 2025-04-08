.. _metadata_toplevel:

.. _metadata_describing_toplevel:

.. _metadata_describing:

==================================
使用元数据描述数据库
==================================

Describing Databases with MetaData

.. module:: sqlalchemy.schema

.. tab:: 中文

    本节讨论了基本的 :class:`_schema.Table`， :class:`_schema.Column` 和 :class:`_schema.MetaData` 对象。

    .. seealso::

        :ref:`tutorial_working_with_metadata` - 在 :ref:`unified_tutorial` 中介绍SQLAlchemy数据库元数据概念的教程

    元数据实体的集合存储在一个恰当地命名为:class:`~sqlalchemy.schema.MetaData`的对象中::

        from sqlalchemy import MetaData

        metadata_obj = MetaData()

    :class:`~sqlalchemy.schema.MetaData` 是一个容器对象，它将被描述的数据库（或多个数据库）的许多不同特性保存在一起。

    要表示一个表，使用 :class:`~sqlalchemy.schema.Table` 类。它的两个主要参数是表名，然后是它将关联的 :class:`~sqlalchemy.schema.MetaData` 对象。其余的参数主要是描述每个列的 :class:`~sqlalchemy.schema.Column` 对象::

        from sqlalchemy import Table, Column, Integer, String

        user = Table(
            "user",
            metadata_obj,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(16), nullable=False),
            Column("email_address", String(60)),
            Column("nickname", String(50), nullable=False),
        )

    上面描述了一个名为 ``user`` 的表，其中包含四个列。表的主键由 ``user_id`` 列组成。多个列可以分配 ``primary_key=True`` 标志，这表示一个多列主键，称为 *复合* 主键。

    另请注意，每列使用与通用类型相对应的对象来描述其数据类型，例如 :class:`~sqlalchemy.types.Integer` 和 :class:`~sqlalchemy.types.String`。SQLAlchemy具有几十种不同层次的类型，并且可以创建自定义类型。关于类型系统的文档可以在 :ref:`types_toplevel` 中找到。

.. tab:: 英文

    This section discusses the fundamental :class:`_schema.Table`, :class:`_schema.Column`
    and :class:`_schema.MetaData` objects.

    .. seealso::

        :ref:`tutorial_working_with_metadata` - tutorial introduction to
        SQLAlchemy's database metadata concept in the :ref:`unified_tutorial`

    A collection of metadata entities is stored in an object aptly named
    :class:`~sqlalchemy.schema.MetaData`::

        from sqlalchemy import MetaData

        metadata_obj = MetaData()

    :class:`~sqlalchemy.schema.MetaData` is a container object that keeps together
    many different features of a database (or multiple databases) being described.

    To represent a table, use the :class:`~sqlalchemy.schema.Table` class. Its two
    primary arguments are the table name, then the
    :class:`~sqlalchemy.schema.MetaData` object which it will be associated with.
    The remaining positional arguments are mostly
    :class:`~sqlalchemy.schema.Column` objects describing each column::

        from sqlalchemy import Table, Column, Integer, String

        user = Table(
            "user",
            metadata_obj,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(16), nullable=False),
            Column("email_address", String(60)),
            Column("nickname", String(50), nullable=False),
        )

    Above, a table called ``user`` is described, which contains four columns. The
    primary key of the table consists of the ``user_id`` column. Multiple columns
    may be assigned the ``primary_key=True`` flag which denotes a multi-column
    primary key, known as a *composite* primary key.

    Note also that each column describes its datatype using objects corresponding
    to genericized types, such as :class:`~sqlalchemy.types.Integer` and
    :class:`~sqlalchemy.types.String`. SQLAlchemy features dozens of types of
    varying levels of specificity as well as the ability to create custom types.
    Documentation on the type system can be found at :ref:`types_toplevel`.

.. _metadata_tables_and_columns:

访问表和列
----------------------------

Accessing Tables and Columns


.. tab:: 中文

    :class:`~sqlalchemy.schema.MetaData` 对象包含了与其关联的所有模式构造元素。它支持几种访问这些表对象的方法，例如 ``sorted_tables`` 访问器会按外键依赖顺序返回每个 :class:`~sqlalchemy.schema.Table` 对象的列表（即，每个表之前都会列出它所引用的所有表）::
    
        >>> for t in metadata_obj.sorted_tables:
        ...     print(t.name)
        user
        user_preference
        invoice
        invoice_item
    
    在大多数情况下，单个 :class:`~sqlalchemy.schema.Table` 对象会被显式声明，这些对象通常作为模块级变量直接在应用程序中访问。一旦定义了 :class:`~sqlalchemy.schema.Table`，它就拥有一整套访问器，可以用来检查其属性。下面是一个 :class:`~sqlalchemy.schema.Table` 的定义示例::
    
        employees = Table(
            "employees",
            metadata_obj,
            Column("employee_id", Integer, primary_key=True),
            Column("employee_name", String(60), nullable=False),
            Column("employee_dept", Integer, ForeignKey("departments.department_id")),
        )
    
    请注意该表中使用了 :class:`~sqlalchemy.schema.ForeignKey` 对象 —— 该构造定义了对远程表的引用，完整说明请参见 :ref:`metadata_foreignkeys`。关于如何访问该表信息的方法包括::
    
        # 访问 "employee_id" 列：
        employees.columns.employee_id
    
        # 或者更简洁地
        employees.c.employee_id
    
        # 通过字符串访问
        employees.c["employee_id"]
    
        # 使用多个字符串返回列元组（2.0 新增）
        emp_id, name, type = employees.c["employee_id", "name", "type"]
    
        # 遍历所有列
        for c in employees.c:
            print(c)
    
        # 获取表的主键列
        for primary_key in employees.primary_key:
            print(primary_key)
    
        # 获取表的外键对象：
        for fkey in employees.foreign_keys:
            print(fkey)
    
        # 访问表的 MetaData：
        employees.metadata
    
        # 访问列的名称、类型、是否可为空、是否为主键、外键信息
        employees.c.employee_id.name
        employees.c.employee_id.type
        employees.c.employee_id.nullable
        employees.c.employee_id.primary_key
        employees.c.employee_dept.foreign_keys
    
        # 获取列的 "key"，默认为列名，但可以是任何用户自定义的字符串：
        employees.c.employee_name.key
    
        # 访问列所归属的表：
        employees.c.employee_id.table is employees
    
        # 获取与外键关联的表：
        list(employees.c.employee_dept.foreign_keys)[0].column.table
    
    .. tip::
    
      :attr:`_sql.FromClause.c` 集合（与 :attr:`_sql.FromClause.columns` 同义）是 :class:`_sql.ColumnCollection` 的实例，提供了 **类字典接口** 来访问列集合。通常我们通过属性访问，如 ``employees.c.employee_name``。
      但如果列名中包含空格，或与字典方法名称冲突（例如 :meth:`_sql.ColumnCollection.keys` 或 :meth:`_sql.ColumnCollection.values`），则必须使用索引方式访问，如 ``employees.c['values']`` 或 ``employees.c["some column"]``。详细信息请参见 :class:`_sql.ColumnCollection`。


.. tab:: 英文


    The :class:`~sqlalchemy.schema.MetaData` object contains all of the schema
    constructs we've associated with it. It supports a few methods of accessing
    these table objects, such as the ``sorted_tables`` accessor which returns a
    list of each :class:`~sqlalchemy.schema.Table` object in order of foreign key
    dependency (that is, each table is preceded by all tables which it
    references)::
    
        >>> for t in metadata_obj.sorted_tables:
        ...     print(t.name)
        user
        user_preference
        invoice
        invoice_item
    
    In most cases, individual :class:`~sqlalchemy.schema.Table` objects have been
    explicitly declared, and these objects are typically accessed directly as
    module-level variables in an application. Once a
    :class:`~sqlalchemy.schema.Table` has been defined, it has a full set of
    accessors which allow inspection of its properties. Given the following
    :class:`~sqlalchemy.schema.Table` definition::
    
        employees = Table(
            "employees",
            metadata_obj,
            Column("employee_id", Integer, primary_key=True),
            Column("employee_name", String(60), nullable=False),
            Column("employee_dept", Integer, ForeignKey("departments.department_id")),
        )
    
    Note the :class:`~sqlalchemy.schema.ForeignKey` object used in this table -
    this construct defines a reference to a remote table, and is fully described
    in :ref:`metadata_foreignkeys`. Methods of accessing information about this
    table include::
    
        # access the column "employee_id":
        employees.columns.employee_id
    
        # or just
        employees.c.employee_id
    
        # via string
        employees.c["employee_id"]
    
        # a tuple of columns may be returned using multiple strings
        # (new in 2.0)
        emp_id, name, type = employees.c["employee_id", "name", "type"]
    
        # iterate through all columns
        for c in employees.c:
            print(c)
    
        # get the table's primary key columns
        for primary_key in employees.primary_key:
            print(primary_key)
    
        # get the table's foreign key objects:
        for fkey in employees.foreign_keys:
            print(fkey)
    
        # access the table's MetaData:
        employees.metadata
    
        # access a column's name, type, nullable, primary key, foreign key
        employees.c.employee_id.name
        employees.c.employee_id.type
        employees.c.employee_id.nullable
        employees.c.employee_id.primary_key
        employees.c.employee_dept.foreign_keys
    
        # get the "key" of a column, which defaults to its name, but can
        # be any user-defined string:
        employees.c.employee_name.key
    
        # access a column's table:
        employees.c.employee_id.table is employees
    
        # get the table related by a foreign key
        list(employees.c.employee_dept.foreign_keys)[0].column.table
    
    .. tip::
    
      The :attr:`_sql.FromClause.c` collection, synonymous with the
      :attr:`_sql.FromClause.columns` collection, is an instance of
      :class:`_sql.ColumnCollection`, which provides a **dictionary-like interface**
      to the collection of columns.   Names are ordinarily accessed like
      attribute names, e.g. ``employees.c.employee_name``.  However for special names
      with spaces or those that match the names of dictionary methods such as
      :meth:`_sql.ColumnCollection.keys` or :meth:`_sql.ColumnCollection.values`,
      indexed access must be used, such as ``employees.c['values']`` or
      ``employees.c["some column"]``.  See :class:`_sql.ColumnCollection` for
      further information.


创建和删除数据库表
-------------------------------------

Creating and Dropping Database Tables


.. tab:: 中文
    
    一旦你定义了一些 :class:`~sqlalchemy.schema.Table` 对象，并且假设你正在操作一个全新的数据库，那么你可能希望为这些表及其相关结构生成 CREATE 语句（顺便说一下，如果你已经有偏好的方法，例如数据库自带的工具或已有的脚本系统，也完全可以跳过这个部分 —— SQLAlchemy 并不强制必须通过它来创建表结构）。
    
    通常使用 :func:`~sqlalchemy.schema.MetaData.create_all` 方法对 :class:`~sqlalchemy.schema.MetaData` 对象执行 CREATE 操作。此方法会为每个表先检查是否存在，如果不存在再发出 CREATE 语句：
    
    .. sourcecode:: python+sql
    
        engine = create_engine("sqlite:///:memory:")
    
        metadata_obj = MetaData()
    
        user = Table(
            "user",
            metadata_obj,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(16), nullable=False),
            Column("email_address", String(60), key="email"),
            Column("nickname", String(50), nullable=False),
        )
    
        user_prefs = Table(
            "user_prefs",
            metadata_obj,
            Column("pref_id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
            Column("pref_name", String(40), nullable=False),
            Column("pref_value", String(100)),
        )
    
        metadata_obj.create_all(engine)
        {execsql}PRAGMA table_info(user){}
        CREATE TABLE user(
                user_id INTEGER NOT NULL PRIMARY KEY,
                user_name VARCHAR(16) NOT NULL,
                email_address VARCHAR(60),
                nickname VARCHAR(50) NOT NULL
        )
        PRAGMA table_info(user_prefs){}
        CREATE TABLE user_prefs(
                pref_id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user(user_id),
                pref_name VARCHAR(40) NOT NULL,
                pref_value VARCHAR(100)
        )
    
    :func:`~sqlalchemy.schema.MetaData.create_all` 方法通常会在表定义中直接内联生成外键约束，并且按照依赖顺序生成表结构。该行为可以通过选项修改，从而改为使用 ``ALTER TABLE`` 语句。
    
    删除所有表可使用 :func:`~sqlalchemy.schema.MetaData.drop_all` 方法。该方法与 :func:`~sqlalchemy.schema.MetaData.create_all` 相反 —— 它会先检查每张表是否存在，并按依赖的逆序进行删除。
    
    也可以通过 :class:`~sqlalchemy.schema.Table` 的 ``create()`` 和 ``drop()`` 方法创建或删除单个表。默认情况下这些方法会直接执行 CREATE 或 DROP，无论表是否存在：
    
    .. sourcecode:: python+sql
    
        engine = create_engine("sqlite:///:memory:")
    
        metadata_obj = MetaData()
    
        employees = Table(
            "employees",
            metadata_obj,
            Column("employee_id", Integer, primary_key=True),
            Column("employee_name", String(60), nullable=False, key="name"),
            Column("employee_dept", Integer, ForeignKey("departments.department_id")),
        )
        employees.create(engine)
        {execsql}CREATE TABLE employees(
            employee_id SERIAL NOT NULL PRIMARY KEY,
            employee_name VARCHAR(60) NOT NULL,
            employee_dept INTEGER REFERENCES departments(department_id)
        )
        {}
    
    ``drop()`` 方法：
    
    .. sourcecode:: python+sql
    
        employees.drop(engine)
        {execsql}DROP TABLE employees
        {}
    
    若希望在执行前先检查表是否存在，可以给 ``create()`` 或 ``drop()`` 方法传入 ``checkfirst=True`` 参数::
    
        employees.create(engine, checkfirst=True)
        employees.drop(engine, checkfirst=False)

.. tab:: 英文


    Once you've defined some :class:`~sqlalchemy.schema.Table` objects, assuming
    you're working with a brand new database one thing you might want to do is
    issue CREATE statements for those tables and their related constructs (as an
    aside, it's also quite possible that you *don't* want to do this, if you
    already have some preferred methodology such as tools included with your
    database or an existing scripting system - if that's the case, feel free to
    skip this section - SQLAlchemy has no requirement that it be used to create
    your tables).
    
    The usual way to issue CREATE is to use
    :func:`~sqlalchemy.schema.MetaData.create_all` on the
    :class:`~sqlalchemy.schema.MetaData` object. This method will issue queries
    that first check for the existence of each individual table, and if not found
    will issue the CREATE statements:
    
    .. sourcecode:: python+sql
    
        engine = create_engine("sqlite:///:memory:")
    
        metadata_obj = MetaData()
    
        user = Table(
            "user",
            metadata_obj,
            Column("user_id", Integer, primary_key=True),
            Column("user_name", String(16), nullable=False),
            Column("email_address", String(60), key="email"),
            Column("nickname", String(50), nullable=False),
        )
    
        user_prefs = Table(
            "user_prefs",
            metadata_obj,
            Column("pref_id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
            Column("pref_name", String(40), nullable=False),
            Column("pref_value", String(100)),
        )
    
        metadata_obj.create_all(engine)
        {execsql}PRAGMA table_info(user){}
        CREATE TABLE user(
                user_id INTEGER NOT NULL PRIMARY KEY,
                user_name VARCHAR(16) NOT NULL,
                email_address VARCHAR(60),
                nickname VARCHAR(50) NOT NULL
        )
        PRAGMA table_info(user_prefs){}
        CREATE TABLE user_prefs(
                pref_id INTEGER NOT NULL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES user(user_id),
                pref_name VARCHAR(40) NOT NULL,
                pref_value VARCHAR(100)
        )
    
    :func:`~sqlalchemy.schema.MetaData.create_all` creates foreign key constraints
    between tables usually inline with the table definition itself, and for this
    reason it also generates the tables in order of their dependency. There are
    options to change this behavior such that ``ALTER TABLE`` is used instead.
    
    Dropping all tables is similarly achieved using the
    :func:`~sqlalchemy.schema.MetaData.drop_all` method. This method does the
    exact opposite of :func:`~sqlalchemy.schema.MetaData.create_all` - the
    presence of each table is checked first, and tables are dropped in reverse
    order of dependency.
    
    Creating and dropping individual tables can be done via the ``create()`` and
    ``drop()`` methods of :class:`~sqlalchemy.schema.Table`. These methods by
    default issue the CREATE or DROP regardless of the table being present:
    
    .. sourcecode:: python+sql
    
        engine = create_engine("sqlite:///:memory:")
    
        metadata_obj = MetaData()
    
        employees = Table(
            "employees",
            metadata_obj,
            Column("employee_id", Integer, primary_key=True),
            Column("employee_name", String(60), nullable=False, key="name"),
            Column("employee_dept", Integer, ForeignKey("departments.department_id")),
        )
        employees.create(engine)
        {execsql}CREATE TABLE employees(
            employee_id SERIAL NOT NULL PRIMARY KEY,
            employee_name VARCHAR(60) NOT NULL,
            employee_dept INTEGER REFERENCES departments(department_id)
        )
        {}
    
    ``drop()`` method:
    
    .. sourcecode:: python+sql
    
        employees.drop(engine)
        {execsql}DROP TABLE employees
        {}
    
    To enable the "check first for the table existing" logic, add the
    ``checkfirst=True`` argument to ``create()`` or ``drop()``::
    
        employees.create(engine, checkfirst=True)
        employees.drop(engine, checkfirst=False)

.. _schema_migrations:

通过迁移更改数据库对象
---------------------------------------------

Altering Database Objects through Migrations
    
    
.. tab:: 中文
    
    虽然 SQLAlchemy 直接支持对模式结构发出 CREATE 和 DROP 语句，但修改这些结构（通常通过 ALTER 语句以及其他特定数据库的结构）超出了 SQLAlchemy 本身的范围。尽管通过传递 :func:`_expression.text` 构造给 :meth:`_engine.Connection.execute` 或使用 :class:`.DDL` 构造手动发出 ALTER 语句等操作很简单，但一种常见做法是使用模式迁移工具，将数据库模式的维护自动化，以配合应用程序代码的演进。
    
    SQLAlchemy 项目提供了专门的迁移工具 `Alembic <https://alembic.sqlalchemy.org>`_ 来完成这一目标。Alembic 提供了高度可定制的环境和极简的使用模式，支持如下功能：事务性 DDL、自动生成“候选”迁移、“离线”模式生成 SQL 脚本，以及分支解析支持。
    
    Alembic 替代了原有的 `SQLAlchemy-Migrate <https://github.com/openstack/sqlalchemy-migrate>`_ 项目，该项目是 SQLAlchemy 的第一个迁移工具，现在已被视为遗留方案。

.. tab:: 英文


    While SQLAlchemy directly supports emitting CREATE and DROP statements for
    schema constructs, the ability to alter those constructs, usually via the ALTER
    statement as well as other database-specific constructs, is outside of the
    scope of SQLAlchemy itself.  While it's easy enough to emit ALTER statements
    and similar by hand, such as by passing a :func:`_expression.text` construct to
    :meth:`_engine.Connection.execute` or by using the :class:`.DDL` construct, it's a
    common practice to automate the maintenance of database schemas in relation to
    application code using schema migration tools.

    The SQLAlchemy project offers the  `Alembic <https://alembic.sqlalchemy.org>`_
    migration tool for this purpose.   Alembic features a highly customizable
    environment and a minimalistic usage pattern, supporting such features as
    transactional DDL, automatic generation of "candidate" migrations, an "offline"
    mode which generates SQL scripts, and support for branch resolution.

    Alembic supersedes the `SQLAlchemy-Migrate
    <https://github.com/openstack/sqlalchemy-migrate>`_   project, which is the
    original migration tool for SQLAlchemy and is now  considered legacy.

.. _schema_table_schema_name:

指定架构名称
--------------------------

Specifying the Schema Name


.. tab:: 中文
    
    大多数数据库都支持多个“模式”（schemas）的概念 —— 也就是命名空间，它们指向另一组表和其他结构。服务器端的“模式”结构形式多种多样，包括特定数据库下的“模式”名称（如 PostgreSQL 的 schema）、命名的兄弟数据库（如 MySQL / MariaDB 对同一服务器上其他数据库的访问），还有其他一些机制，如其他用户名所拥有的表（Oracle、SQL Server），甚至是指向其他数据库文件（如 SQLite 的 ATTACH）或远程服务器（如 Oracle Database 的 DBLINK 结合 synonym）。
    
    上述各种机制的共同点（大多数情况下）是它们可以通过一个字符串名称来引用另一组表。SQLAlchemy 将这个名称称为 **schema 名称**。在 SQLAlchemy 中，它只是一个字符串名称，关联到某个 :class:`_schema.Table` 对象，并以适合目标数据库的方式渲染到 SQL 语句中，从而使得表在其远程“schema”中被正确引用 —— 无论这个机制在目标数据库中是怎样实现的。
    
    可以直接使用 :paramref:`_schema.Table.schema` 参数将 “schema” 名称关联到一个 :class:`_schema.Table` 对象；当使用 ORM 的 :ref:`declarative table <orm_declarative_table_config_toplevel>` 配置时，该参数通过 ``__table_args__`` 参数字典传递。
    
    也可以将 “schema” 名称关联到 :class:`_schema.MetaData` 对象上，那么这个 schema 将自动作用于所有没有显式指定 schema 名称的 :class:`_schema.Table` 对象。此外，SQLAlchemy 还支持“动态” schema 名称系统，这在多租户（multi-tenant）应用中非常常见，可以使一组 :class:`_schema.Table` 元数据在每个连接或每条语句基础上引用不同的 schema 名称。
    
    .. topic:: 什么是 “schema”？
    
        SQLAlchemy 对数据库 “schema” 的支持最初是为了支持 PostgreSQL 风格的 schema。该风格中，首先有一个 “数据库”（通常只有一个所有者），在该数据库中可以有任意多个 “schema”，这些 schema 中才包含实际的表对象。
    
        某个 schema 中的表通过 "<schemaname>.<tablename>" 的语法显式引用。与此对比，例如 MySQL 的架构中只有 “数据库”，但 SQL 语句仍然可以通过 "<database>.<tablename>" 的语法引用多个数据库中的表。对于 Oracle 数据库，该语法又代表了另一个概念 —— 表的 “所有者”。无论使用哪种数据库，SQLAlchemy 使用 “schema” 一词来表示 "<限定符>.<tablename>" 语法中的限定符部分。
    
    .. seealso::
    
        :ref:`orm_declarative_table_schema_name` - 使用 ORM 时指定 schema 名称  
        :ref:`declarative table <orm_declarative_table_config_toplevel>` 配置方式
    
    最基本的例子是使用 Core 层 :class:`_schema.Table` 对象时传入 :paramref:`_schema.Table.schema` 参数，如下所示::
    
        metadata_obj = MetaData()
    
        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
            schema="remote_banks",
        )
    
    通过这个 :class:`_schema.Table` 生成的 SQL（如下所示的 SELECT 语句）将使用 schema 名称 ``remote_banks`` 来限定表名 ``financial_info``：
    
    .. sourcecode:: pycon+sql
    
        >>> print(select(financial_info))
        {printsql}SELECT remote_banks.financial_info.id, remote_banks.financial_info.value
        FROM remote_banks.financial_info
    
    当使用显式 schema 名称声明 :class:`_schema.Table` 对象时，它将在内部以 schema 和表名的组合形式存储在 :class:`_schema.MetaData` 的命名空间中。我们可以通过在 :attr:`_schema.MetaData.tables` 集合中查找 ``'remote_banks.financial_info'`` 键来查看它::
    
        >>> metadata_obj.tables["remote_banks.financial_info"]
        Table('financial_info', MetaData(),
        Column('id', Integer(), table=<financial_info>, primary_key=True, nullable=False),
        Column('value', String(length=100), table=<financial_info>, nullable=False),
        schema='remote_banks')
    
    当通过 :class:`_schema.ForeignKey` 或 :class:`_schema.ForeignKeyConstraint` 对象引用该表时，也必须使用这种带点的名称，即使引用表也在同一 schema 中::
    
        customer = Table(
            "customer",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("financial_info_id", ForeignKey("remote_banks.financial_info.id")),
            schema="remote_banks",
        )
    
    在某些方言中，:paramref:`_schema.Table.schema` 参数还可以表示多级标识符路径（例如点分形式的路径）。这在一些数据库中尤为重要，比如 Microsoft SQL Server，通常使用点号分隔的“数据库/所有者”标识符。此时，token 可以直接全部作为 schema 传入，例如::
    
        schema = "dbo.scott"
    
    .. seealso::
    
        :ref:`multipart_schema_names` - 使用 SQL Server 方言时如何使用点分 schema 名称  
        :ref:`metadata_reflection_schemas`

.. tab:: 英文


    Most databases support the concept of multiple "schemas" - namespaces that
    refer to alternate sets of tables and other constructs.  The server-side
    geometry of a "schema" takes many forms, including names of "schemas" under the
    scope of a particular database (e.g. PostgreSQL schemas), named sibling
    databases (e.g. MySQL / MariaDB access to other databases on the same server),
    as well as other concepts like tables owned by other usernames (Oracle
    Database, SQL Server) or even names that refer to alternate database files
    (SQLite ATTACH) or remote servers (Oracle Database DBLINK with synonyms).
    
    What all of the above approaches have (mostly) in common is that there's a way
    of referencing this alternate set of tables using a string name.  SQLAlchemy
    refers to this name as the **schema name**.  Within SQLAlchemy, this is nothing
    more than a string name which is associated with a :class:`_schema.Table`
    object, and is then rendered into SQL statements in a manner appropriate to the
    target database such that the table is referenced in its remote "schema",
    whatever mechanism that is on the target database.
    
    The "schema" name may be associated directly with a :class:`_schema.Table`
    using the :paramref:`_schema.Table.schema` argument; when using the ORM
    with :ref:`declarative table <orm_declarative_table_config_toplevel>` configuration,
    the parameter is passed using the ``__table_args__`` parameter dictionary.
    
    The "schema" name may also be associated with the :class:`_schema.MetaData`
    object where it will take effect automatically for all :class:`_schema.Table`
    objects associated with that :class:`_schema.MetaData` that don't otherwise
    specify their own name.  Finally, SQLAlchemy also supports a "dynamic" schema name
    system that is often used for multi-tenant applications such that a single set
    of :class:`_schema.Table` metadata may refer to a dynamically configured set of
    schema names on a per-connection or per-statement basis.
    
    .. topic::  What's "schema" ?
    
        SQLAlchemy's support for database "schema" was designed with first party
        support for PostgreSQL-style schemas.  In this style, there is first a
        "database" that typically has a single "owner".  Within this database there
        can be any number of "schemas" which then contain the actual table objects.
    
        A table within a specific schema is referenced explicitly using the syntax
        "<schemaname>.<tablename>".  Contrast this to an architecture such as that
        of MySQL, where there are only "databases", however SQL statements can
        refer to multiple databases at once, using the same syntax except it is
        "<database>.<tablename>".  On Oracle Database, this syntax refers to yet
        another concept, the "owner" of a table.  Regardless of which kind of
        database is in use, SQLAlchemy uses the phrase "schema" to refer to the
        qualifying identifier within the general syntax of
        "<qualifier>.<tablename>".
    
    .. seealso::
    
        :ref:`orm_declarative_table_schema_name` - schema name specification when using the ORM
        :ref:`declarative table <orm_declarative_table_config_toplevel>` configuration
    
    
    The most basic example is that of the :paramref:`_schema.Table.schema` argument
    using a Core :class:`_schema.Table` object as follows::
    
        metadata_obj = MetaData()
    
        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
            schema="remote_banks",
        )
    
    SQL that is rendered using this :class:`_schema.Table`, such as the SELECT
    statement below, will explicitly qualify the table name ``financial_info`` with
    the ``remote_banks`` schema name:
    
    .. sourcecode:: pycon+sql
    
        >>> print(select(financial_info))
        {printsql}SELECT remote_banks.financial_info.id, remote_banks.financial_info.value
        FROM remote_banks.financial_info
    
    When a :class:`_schema.Table` object is declared with an explicit schema
    name, it is stored in the internal :class:`_schema.MetaData` namespace
    using the combination of the schema and table name.  We can view this
    in the :attr:`_schema.MetaData.tables` collection by searching for the
    key ``'remote_banks.financial_info'``::
    
        >>> metadata_obj.tables["remote_banks.financial_info"]
        Table('financial_info', MetaData(),
        Column('id', Integer(), table=<financial_info>, primary_key=True, nullable=False),
        Column('value', String(length=100), table=<financial_info>, nullable=False),
        schema='remote_banks')
    
    This dotted name is also what must be used when referring to the table
    for use with the :class:`_schema.ForeignKey` or :class:`_schema.ForeignKeyConstraint`
    objects, even if the referring table is also in that same schema::
    
        customer = Table(
            "customer",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("financial_info_id", ForeignKey("remote_banks.financial_info.id")),
            schema="remote_banks",
        )
    
    The :paramref:`_schema.Table.schema` argument may also be used with certain
    dialects to indicate
    a multiple-token (e.g. dotted) path to a particular table.  This is particularly
    important on a database such as Microsoft SQL Server where there are often
    dotted "database/owner" tokens.  The tokens may be placed directly in the name
    at once, such as::
    
        schema = "dbo.scott"
    
    .. seealso::
    
        :ref:`multipart_schema_names` - describes use of dotted schema names
        with the SQL Server dialect.
    
        :ref:`metadata_reflection_schemas`


.. _schema_metadata_schema_name:

使用元数据指定默认架构名称
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifying a Default Schema Name with MetaData


.. tab:: 中文
    
    也可以在顶层的 :class:`_schema.MetaData` 构造中传入 :paramref:`_schema.MetaData.schema` 参数，为所有 :paramref:`_schema.Table.schema` 参数设置一个显式的默认值::
    
        metadata_obj = MetaData(schema="remote_banks")
    
        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
        )
    
    如上所示，对于所有将 :paramref:`_schema.Table.schema` 参数保留为默认值 ``None`` 的 :class:`_schema.Table` 对象（或直接与该 :class:`_schema.MetaData` 关联的 :class:`_schema.Sequence` 对象），将视为该参数被设置为 ``"remote_banks"``。这包括该 :class:`_schema.Table` 在 :class:`_schema.MetaData` 中是以 schema 限定名形式被收录的，也就是说::
    
        metadata_obj.tables["remote_banks.financial_info"]
    
    当使用 :class:`_schema.ForeignKey` 或 :class:`_schema.ForeignKeyConstraint` 对象引用该表时，可以使用 schema 限定名或非限定名来引用 ``remote_banks.financial_info`` 表::
    
        # 两种方式都可行：
    
        refers_to_financial_info = Table(
            "refers_to_financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("fiid", ForeignKey("financial_info.id")),
        )
    
    
        # 或者
    
        refers_to_financial_info = Table(
            "refers_to_financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("fiid", ForeignKey("remote_banks.financial_info.id")),
        )
    
    当使用带有 :paramref:`_schema.MetaData.schema` 的 :class:`_schema.MetaData` 对象时，如果某个 :class:`_schema.Table` 明确指定它不应使用 schema 限定，可以使用特殊标识符 :data:`_schema.BLANK_SCHEMA`::
    
        from sqlalchemy import BLANK_SCHEMA
    
        metadata_obj = MetaData(schema="remote_banks")
    
        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
            schema=BLANK_SCHEMA,  # 不会使用 "remote_banks"
        )
    
    .. seealso::
    
        :paramref:`_schema.MetaData.schema`

.. tab:: 英文


    The :class:`_schema.MetaData` object may also set up an explicit default
    option for all :paramref:`_schema.Table.schema` parameters by passing the
    :paramref:`_schema.MetaData.schema` argument to the top level :class:`_schema.MetaData`
    construct::

        metadata_obj = MetaData(schema="remote_banks")

        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
        )

    Above, for any :class:`_schema.Table` object (or :class:`_schema.Sequence` object
    directly associated with the :class:`_schema.MetaData`) which leaves the
    :paramref:`_schema.Table.schema` parameter at its default of ``None`` will instead
    act as though the parameter were set to the value ``"remote_banks"``.  This
    includes that the :class:`_schema.Table` is cataloged in the :class:`_schema.MetaData`
    using the schema-qualified name, that is::

        metadata_obj.tables["remote_banks.financial_info"]

    When using the :class:`_schema.ForeignKey` or :class:`_schema.ForeignKeyConstraint`
    objects to refer to this table, either the schema-qualified name or the
    non-schema-qualified name may be used to refer to the ``remote_banks.financial_info``
    table::

        # either will work:

        refers_to_financial_info = Table(
            "refers_to_financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("fiid", ForeignKey("financial_info.id")),
        )


        # or

        refers_to_financial_info = Table(
            "refers_to_financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("fiid", ForeignKey("remote_banks.financial_info.id")),
        )

    When using a :class:`_schema.MetaData` object that sets
    :paramref:`_schema.MetaData.schema`, a :class:`_schema.Table` that wishes
    to specify that it should not be schema qualified may use the special symbol
    :data:`_schema.BLANK_SCHEMA`::

        from sqlalchemy import BLANK_SCHEMA

        metadata_obj = MetaData(schema="remote_banks")

        financial_info = Table(
            "financial_info",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("value", String(100), nullable=False),
            schema=BLANK_SCHEMA,  # will not use "remote_banks"
        )

    .. seealso::

        :paramref:`_schema.MetaData.schema`


.. _schema_dynamic_naming_convention:

应用动态架构命名约定
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applying Dynamic Schema Naming Conventions


.. tab:: 中文
    
    :paramref:`_schema.Table.schema` 参数所使用的名称也可以用于按连接或执行时动态查找的机制。例如在多租户场景中，每次事务或语句执行都可以针对一组会变化的特定 schema 名称。相关特性在 :ref:`schema_translating` 一节中有详细说明。
    
    .. seealso::
    
        :ref:`schema_translating`

.. tab:: 英文


    The names used by the :paramref:`_schema.Table.schema` parameter may also be
    applied against a lookup that is dynamic on a per-connection or per-execution
    basis, so that for example in multi-tenant situations, each transaction
    or statement may be targeted at a specific set of schema names that change.
    The section :ref:`schema_translating` describes how this feature is used.

    .. seealso::

        :ref:`schema_translating`


.. _schema_set_default_connections:

为新连接设置默认架构
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting a Default Schema for New Connections


.. tab:: 中文
    
    上述方法都涉及在 SQL 语句中显式包含 schema 名称。
    实际上，数据库连接具备“默认 schema”的概念，
    即当表名未显式指定 schema 时，所使用的“schema”（或数据库、所有者等）的名称。
    这些名称通常在登录时进行配置，例如连接到 PostgreSQL 数据库时，默认的 "schema" 名为 "public"。
    
    在许多情况下，默认的 "schema" 无法通过登录本身进行设置，而是需要在每次建立连接时进行配置，
    例如在 PostgreSQL 中使用 "SET SEARCH_PATH" 或在 Oracle Database 中使用 "ALTER SESSION"。
    可以通过 :meth:`_pool.PoolEvents.connect` 事件来实现这一点，
    该事件允许在首次创建 DBAPI 连接时进行操作。例如，以下代码将 Oracle Database 的 CURRENT_SCHEMA 设置为一个自定义名称::
    
        from sqlalchemy import event
        from sqlalchemy import create_engine
    
        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )
    
    
        @event.listens_for(engine, "connect", insert=True)
        def set_current_schema(dbapi_connection, connection_record):
            cursor_obj = dbapi_connection.cursor()
            cursor_obj.execute("ALTER SESSION SET CURRENT_SCHEMA=%s" % schema_name)
            cursor_obj.close()
    
    上述代码中，``set_current_schema()`` 事件处理器会在上述 :class:`_engine.Engine` 首次建立连接时立即执行；
    由于事件被“插入”到处理器列表的开头，它还会在方言（dialect）自己的事件处理器运行之前执行，
    尤其包括确定连接的“默认 schema”的那一个处理器。
    
    对于其他数据库，请参考数据库本身和/或其 SQLAlchemy 方言文档，以了解如何设置默认 schema。
    
    .. versionchanged:: 1.4.0b2  

       上述方案现在无需额外注册其它事件处理器即可工作。
    
    .. seealso::
    
        :ref:`postgresql_alternate_search_path` - 位于 :ref:`postgresql_toplevel` 方言文档中。

.. tab:: 英文


    The above approaches all refer to methods of including an explicit schema-name
    within SQL statements.  Database connections in fact feature the concept
    of a "default" schema, which is the name of the "schema" (or database, owner,
    etc.) that takes place if a table name is not explicitly schema-qualified.
    These names are usually configured at the login level, such as when connecting
    to a PostgreSQL database, the default "schema" is called "public".

    There are often cases where the default "schema" cannot be set via the login
    itself and instead would usefully be configured each time a connection is made,
    using a statement such as "SET SEARCH_PATH" on PostgreSQL or "ALTER SESSION" on
    Oracle Database.  These approaches may be achieved by using the
    :meth:`_pool.PoolEvents.connect` event, which allows access to the DBAPI
    connection when it is first created.  For example, to set the Oracle Database
    CURRENT_SCHEMA variable to an alternate name::

        from sqlalchemy import event
        from sqlalchemy import create_engine

        engine = create_engine(
            "oracle+oracledb://scott:tiger@localhost:1521?service_name=freepdb1"
        )


        @event.listens_for(engine, "connect", insert=True)
        def set_current_schema(dbapi_connection, connection_record):
            cursor_obj = dbapi_connection.cursor()
            cursor_obj.execute("ALTER SESSION SET CURRENT_SCHEMA=%s" % schema_name)
            cursor_obj.close()

    Above, the ``set_current_schema()`` event handler will take place immediately
    when the above :class:`_engine.Engine` first connects; as the event is
    "inserted" into the beginning of the handler list, it will also take place
    before the dialect's own event handlers are run, in particular including the
    one that will determine the "default schema" for the connection.

    For other databases, consult the database and/or dialect documentation
    for specific information regarding how default schemas are configured.

    .. versionchanged:: 1.4.0b2  The above recipe now works without the need to
    establish additional event handlers.

    .. seealso::

        :ref:`postgresql_alternate_search_path` - in the :ref:`postgresql_toplevel` dialect documentation.




架构和反射
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Schemas and Reflection


.. tab:: 中文
    
    SQLAlchemy 的 schema 功能会与在 :ref:`metadata_reflection_toplevel` 中介绍的表反射功能交互使用。
    更多细节请参考 :ref:`metadata_reflection_schemas`。

.. tab:: 英文


    The schema feature of SQLAlchemy interacts with the table reflection
    feature introduced at :ref:`metadata_reflection_toplevel`.  See the section
    :ref:`metadata_reflection_schemas` for additional details on how this works.


后端特定选项
------------------------

Backend-Specific Options


.. tab:: 中文
    
    :class:`~sqlalchemy.schema.Table` 支持数据库特定的选项。
    例如，MySQL 支持不同的表存储引擎，包括 "MyISAM" 和 "InnoDB"。
    可以通过 :class:`~sqlalchemy.schema.Table` 的 ``mysql_engine`` 参数表达这一点::
    
        addresses = Table(
            "engine_email_addresses",
            metadata_obj,
            Column("address_id", Integer, primary_key=True),
            Column("remote_user_id", Integer, ForeignKey(users.c.user_id)),
            Column("email_address", String(20)),
            mysql_engine="InnoDB",
        )
    
    其他数据库后端也可能支持表级别的选项 —— 这些内容可在每种方言的独立文档章节中找到说明。

.. tab:: 英文


    :class:`~sqlalchemy.schema.Table` supports database-specific options. For
    example, MySQL has different table backend types, including "MyISAM" and
    "InnoDB". This can be expressed with :class:`~sqlalchemy.schema.Table` using
    ``mysql_engine``::

        addresses = Table(
            "engine_email_addresses",
            metadata_obj,
            Column("address_id", Integer, primary_key=True),
            Column("remote_user_id", Integer, ForeignKey(users.c.user_id)),
            Column("email_address", String(20)),
            mysql_engine="InnoDB",
        )

    Other backends may support table-level options as well - these would be
    described in the individual documentation sections for each dialect.

列、表、元数据 API
---------------------------

Column, Table, MetaData API


.. tab:: 中文

.. tab:: 英文


.. attribute:: sqlalchemy.schema.BLANK_SCHEMA
    :noindex:

    Refers to :attr:`.SchemaConst.BLANK_SCHEMA`.

.. attribute:: sqlalchemy.schema.RETAIN_SCHEMA
    :noindex:

    Refers to :attr:`.SchemaConst.RETAIN_SCHEMA`


.. autoclass:: Column
    :members:
    :inherited-members:


.. autoclass:: MetaData
    :members:

.. autoclass:: SchemaConst
    :members:

.. autoclass:: SchemaItem
    :members:

.. autofunction:: insert_sentinel

.. autoclass:: Table
    :members:
    :inherited-members:
