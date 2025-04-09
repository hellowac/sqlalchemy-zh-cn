.. _metadata_ddl_toplevel:
.. _metadata_ddl:
.. currentmodule:: sqlalchemy.schema

自定义 DDL
===============

Customizing DDL

.. tab:: 中文

    在前面的章节中，我们讨论了各种模式构造，包括 :class:`~sqlalchemy.schema.Table`，:class:`~sqlalchemy.schema.ForeignKeyConstraint`，:class:`~sqlalchemy.schema.CheckConstraint` 和 :class:`~sqlalchemy.schema.Sequence`。在整个过程中，我们依赖于 :class:`~sqlalchemy.schema.Table` 和 :class:`~sqlalchemy.schema.MetaData` 的 ``create()`` 和 :func:`~sqlalchemy.schema.MetaData.create_all` 方法来发出所有构造的数据定义语言（DDL）。当发出时，会调用预定的操作顺序，并无条件地创建每个表的DDL，包括与其相关的所有约束和其他对象。对于需要数据库特定DDL的更复杂场景，SQLAlchemy提供了两种技术，可以根据任何条件添加任何DDL，无论是伴随标准的表生成还是单独生成。

.. tab:: 英文

    In the preceding sections we've discussed a variety of schema constructs
    including :class:`~sqlalchemy.schema.Table`,
    :class:`~sqlalchemy.schema.ForeignKeyConstraint`,
    :class:`~sqlalchemy.schema.CheckConstraint`, and
    :class:`~sqlalchemy.schema.Sequence`. Throughout, we've relied upon the
    ``create()`` and :func:`~sqlalchemy.schema.MetaData.create_all` methods of
    :class:`~sqlalchemy.schema.Table` and :class:`~sqlalchemy.schema.MetaData` in
    order to issue data definition language (DDL) for all constructs. When issued,
    a pre-determined order of operations is invoked, and DDL to create each table
    is created unconditionally including all constraints and other objects
    associated with it. For more complex scenarios where database-specific DDL is
    required, SQLAlchemy offers two techniques which can be used to add any DDL
    based on any condition, either accompanying the standard generation of tables
    or by itself.

自定义 DDL
----------

Custom DDL

.. tab:: 中文

    自定义 DDL 语句可以最方便地通过 :class:`~sqlalchemy.schema.DDL` 构造实现。
    该构造与其他所有 DDL 元素类似，只不过它接受一个字符串作为要执行的文本：

    .. sourcecode:: python+sql

        event.listen(
            metadata,
            "after_create",
            DDL(
                "ALTER TABLE users ADD CONSTRAINT "
                "cst_user_name_length "
                " CHECK (length(user_name) >= 8)"
            ),
        )

    一种更全面的方式是使用自定义编译机制来创建 DDL 构造的库——详见
    :ref:`sqlalchemy.ext.compiler_toplevel`。

.. tab:: 英文

    Custom DDL phrases are most easily achieved using the
    :class:`~sqlalchemy.schema.DDL` construct. This construct works like all the
    other DDL elements except it accepts a string which is the text to be emitted:

    .. sourcecode:: python+sql

        event.listen(
            metadata,
            "after_create",
            DDL(
                "ALTER TABLE users ADD CONSTRAINT "
                "cst_user_name_length "
                " CHECK (length(user_name) >= 8)"
            ),
        )

    A more comprehensive method of creating libraries of DDL constructs is to use
    custom compilation - see :ref:`sqlalchemy.ext.compiler_toplevel` for
    details.


.. _schema_ddl_sequences:

控制 DDL 序列
-------------------------

Controlling DDL Sequences

.. tab:: 中文

    前面提到的 :class:`_schema.DDL` 构造还可以根据数据库的检查结果有条件地执行。
    该功能可通过 :meth:`.ExecutableDDLElement.execute_if` 方法实现。
    例如，如果我们只想在 PostgreSQL 后端创建触发器，可以这样调用::

        mytable = Table(
            "mytable",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", String(50)),
        )

        func = DDL(
            "CREATE FUNCTION my_func() "
            "RETURNS TRIGGER AS $$ "
            "BEGIN "
            "NEW.data := 'ins'; "
            "RETURN NEW; "
            "END; $$ LANGUAGE PLPGSQL"
        )

        trigger = DDL(
            "CREATE TRIGGER dt_ins BEFORE INSERT ON mytable "
            "FOR EACH ROW EXECUTE PROCEDURE my_func();"
        )

        event.listen(mytable, "after_create", func.execute_if(dialect="postgresql"))

        event.listen(mytable, "after_create", trigger.execute_if(dialect="postgresql"))

    :paramref:`.ExecutableDDLElement.execute_if.dialect` 关键字也接受一个由字符串组成的元组，表示多个方言名称::

        event.listen(
            mytable, "after_create", trigger.execute_if(dialect=("postgresql", "mysql"))
        )
        event.listen(
            mytable, "before_drop", trigger.execute_if(dialect=("postgresql", "mysql"))
        )

    :meth:`.ExecutableDDLElement.execute_if` 方法也可以使用一个可调用对象，
    该对象会接收当前使用的数据库连接。
    在下面的示例中，我们通过先查询 PostgreSQL 的系统目录，
    判断 CHECK 约束是否已存在，来有条件地创建该约束：

    .. sourcecode:: python+sql

        def should_create(ddl, target, connection, **kw):
            row = connection.execute(
                "select conname from pg_constraint where conname='%s'" % ddl.element.name
            ).scalar()
            return not bool(row)


        def should_drop(ddl, target, connection, **kw):
            return not should_create(ddl, target, connection, **kw)


        event.listen(
            users,
            "after_create",
            DDL(
                "ALTER TABLE users ADD CONSTRAINT "
                "cst_user_name_length CHECK (length(user_name) >= 8)"
            ).execute_if(callable_=should_create),
        )
        event.listen(
            users,
            "before_drop",
            DDL("ALTER TABLE users DROP CONSTRAINT cst_user_name_length").execute_if(
                callable_=should_drop
            ),
        )

        users.create(engine)
        {execsql}CREATE TABLE users (
            user_id SERIAL NOT NULL,
            user_name VARCHAR(40) NOT NULL,
            PRIMARY KEY (user_id)
        )

        SELECT conname FROM pg_constraint WHERE conname='cst_user_name_length'
        ALTER TABLE users ADD CONSTRAINT cst_user_name_length  CHECK (length(user_name) >= 8)
        {stop}

        users.drop(engine)
        {execsql}SELECT conname FROM pg_constraint WHERE conname='cst_user_name_length'
        ALTER TABLE users DROP CONSTRAINT cst_user_name_length
        DROP TABLE users{stop}

.. tab:: 英文

    The :class:`_schema.DDL` construct introduced previously also has the
    ability to be invoked conditionally based on inspection of the
    database.  This feature is available using the :meth:`.ExecutableDDLElement.execute_if`
    method.  For example, if we wanted to create a trigger but only on
    the PostgreSQL backend, we could invoke this as::

        mytable = Table(
            "mytable",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", String(50)),
        )

        func = DDL(
            "CREATE FUNCTION my_func() "
            "RETURNS TRIGGER AS $$ "
            "BEGIN "
            "NEW.data := 'ins'; "
            "RETURN NEW; "
            "END; $$ LANGUAGE PLPGSQL"
        )

        trigger = DDL(
            "CREATE TRIGGER dt_ins BEFORE INSERT ON mytable "
            "FOR EACH ROW EXECUTE PROCEDURE my_func();"
        )

        event.listen(mytable, "after_create", func.execute_if(dialect="postgresql"))

        event.listen(mytable, "after_create", trigger.execute_if(dialect="postgresql"))

    The :paramref:`.ExecutableDDLElement.execute_if.dialect` keyword also accepts a tuple
    of string dialect names::

        event.listen(
            mytable, "after_create", trigger.execute_if(dialect=("postgresql", "mysql"))
        )
        event.listen(
            mytable, "before_drop", trigger.execute_if(dialect=("postgresql", "mysql"))
        )

    The :meth:`.ExecutableDDLElement.execute_if` method can also work against a callable
    function that will receive the database connection in use.  In the
    example below, we use this to conditionally create a CHECK constraint,
    first looking within the PostgreSQL catalogs to see if it exists:

    .. sourcecode:: python+sql

        def should_create(ddl, target, connection, **kw):
            row = connection.execute(
                "select conname from pg_constraint where conname='%s'" % ddl.element.name
            ).scalar()
            return not bool(row)


        def should_drop(ddl, target, connection, **kw):
            return not should_create(ddl, target, connection, **kw)


        event.listen(
            users,
            "after_create",
            DDL(
                "ALTER TABLE users ADD CONSTRAINT "
                "cst_user_name_length CHECK (length(user_name) >= 8)"
            ).execute_if(callable_=should_create),
        )
        event.listen(
            users,
            "before_drop",
            DDL("ALTER TABLE users DROP CONSTRAINT cst_user_name_length").execute_if(
                callable_=should_drop
            ),
        )

        users.create(engine)
        {execsql}CREATE TABLE users (
            user_id SERIAL NOT NULL,
            user_name VARCHAR(40) NOT NULL,
            PRIMARY KEY (user_id)
        )

        SELECT conname FROM pg_constraint WHERE conname='cst_user_name_length'
        ALTER TABLE users ADD CONSTRAINT cst_user_name_length  CHECK (length(user_name) >= 8)
        {stop}

        users.drop(engine)
        {execsql}SELECT conname FROM pg_constraint WHERE conname='cst_user_name_length'
        ALTER TABLE users DROP CONSTRAINT cst_user_name_length
        DROP TABLE users{stop}

使用内置 DDLElement 类
-------------------------------------

Using the built-in DDLElement Classes

.. tab:: 中文

    ``sqlalchemy.schema`` 包含了一些 SQL 表达式构造，用于生成 DDL 表达式，
    它们都继承自通用的基类 :class:`.ExecutableDDLElement`。
    例如，要生成一个 ``CREATE TABLE`` 语句，可以使用 :class:`.CreateTable` 构造：

    .. sourcecode:: python+sql

        from sqlalchemy.schema import CreateTable

        with engine.connect() as conn:
            conn.execute(CreateTable(mytable))
        {execsql}CREATE TABLE mytable (
            col1 INTEGER,
            col2 INTEGER,
            col3 INTEGER,
            col4 INTEGER,
            col5 INTEGER,
            col6 INTEGER
        ){stop}

    如上所示，:class:`~sqlalchemy.schema.CreateTable` 构造的工作方式类似于其他表达式构造（如 ``select()``、 ``table.insert()`` 等）。
    SQLAlchemy 中所有与 DDL 相关的构造都是 :class:`.ExecutableDDLElement` 的子类；
    这个基类对应所有的 CREATE、DROP 以及 ALTER 操作对象，
    不仅适用于 SQLAlchemy，也适用于 Alembic Migrations。
    可用构造的完整参考请参见 :ref:`schema_api_ddl`。

    用户也可以自定义继承自 :class:`.ExecutableDDLElement` 的类，以创建自己的 DDL 构造。
    文档 :ref:`sqlalchemy.ext.compiler_toplevel` 中包含了多个示例。

.. tab:: 英文

    The ``sqlalchemy.schema`` package contains SQL expression constructs that
    provide DDL expressions, all of which extend from the common base
    :class:`.ExecutableDDLElement`. For example, to produce a ``CREATE TABLE`` statement,
    one can use the :class:`.CreateTable` construct:

    .. sourcecode:: python+sql

        from sqlalchemy.schema import CreateTable

        with engine.connect() as conn:
            conn.execute(CreateTable(mytable))
        {execsql}CREATE TABLE mytable (
            col1 INTEGER,
            col2 INTEGER,
            col3 INTEGER,
            col4 INTEGER,
            col5 INTEGER,
            col6 INTEGER
        ){stop}

    Above, the :class:`~sqlalchemy.schema.CreateTable` construct works like any
    other expression construct (such as ``select()``, ``table.insert()``, etc.).
    All of SQLAlchemy's DDL oriented constructs are subclasses of
    the :class:`.ExecutableDDLElement` base class; this is the base of all the
    objects corresponding to CREATE and DROP as well as ALTER,
    not only in SQLAlchemy but in Alembic Migrations as well.
    A full reference of available constructs is in :ref:`schema_api_ddl`.

    User-defined DDL constructs may also be created as subclasses of
    :class:`.ExecutableDDLElement` itself.   The documentation in
    :ref:`sqlalchemy.ext.compiler_toplevel` has several examples of this.

.. _schema_ddl_ddl_if:

控制 DDL 约束和索引的生成
-----------------------------------------------------

Controlling DDL Generation of Constraints and Indexes

.. versionadded:: 2.0

.. tab:: 中文

    前面提到的 :meth:`.ExecutableDDLElement.execute_if` 方法在需要有条件执行自定义 :class:`.DDL` 类时非常有用，
    但对于通常与特定 :class:`.Table` 相关的元素（如约束和索引），也常常有类似的“条件”需求。
    例如，一个索引可能包含某些特定于 PostgreSQL 或 SQL Server 后端的特性。
    针对这种用例，可以使用 :meth:`.Constraint.ddl_if` 和 :meth:`.Index.ddl_if` 方法，
    它们可以用于 :class:`.CheckConstraint`、:class:`.UniqueConstraint` 和 :class:`.Index` 等构造，
    并接受与 :meth:`.ExecutableDDLElement.execute_if` 方法相同的参数，以控制这些对象的 DDL 是否会在其所属的
    :class:`.Table` 上下文中被执行。这些方法可以在定义 :class:`.Table` 时内联使用
    （或者同样地，在 ORM 声明式映射中通过 ``__table_args__`` 集合使用），如下所示::

        from sqlalchemy import CheckConstraint, Index
        from sqlalchemy import MetaData, Table, Column
        from sqlalchemy import Integer, String

        meta = MetaData()

        my_table = Table(
            "my_table",
            meta,
            Column("id", Integer, primary_key=True),
            Column("num", Integer),
            Column("data", String),
            Index("my_pg_index", "data").ddl_if(dialect="postgresql"),
            CheckConstraint("num > 5").ddl_if(dialect="postgresql"),
        )

    在上面的示例中，:class:`.Table` 构造包含一个 :class:`.Index` 和一个 :class:`.CheckConstraint` 构造，
    它们都通过 ``.ddl_if(dialect="postgresql")`` 指定仅在 PostgreSQL 方言下生效，
    因此它们只会在生成 PostgreSQL 的 CREATE TABLE 语句时被包含。
    例如，如果我们对 SQLite 方言执行 ``meta.create_all()``，两个构造都不会被包含：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> sqlite_engine = create_engine("sqlite+pysqlite://", echo=True)
        >>> meta.create_all(sqlite_engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_info("my_table")
        [raw sql] ()
        PRAGMA temp.table_info("my_table")
        [raw sql] ()

        CREATE TABLE my_table (
            id INTEGER NOT NULL,
            num INTEGER,
            data VARCHAR,
            PRIMARY KEY (id)
        )

    然而，如果我们在 PostgreSQL 数据库上运行相同命令，将会看到针对 CHECK 约束的内联 DDL，
    以及为索引单独生成的 CREATE 语句：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> postgresql_engine = create_engine(
        ...     "postgresql+psycopg2://scott:tiger@localhost/test", echo=True
        ... )
        >>> meta.create_all(postgresql_engine)
        {execsql}BEGIN (implicit)
        select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
        [generated in 0.00009s] {'name': 'my_table'}

        CREATE TABLE my_table (
            id SERIAL NOT NULL,
            num INTEGER,
            data VARCHAR,
            PRIMARY KEY (id),
            CHECK (num > 5)
        )
        [no key 0.00007s] {}
        CREATE INDEX my_pg_index ON my_table (data)
        [no key 0.00013s] {}
        COMMIT

    :meth:`.Constraint.ddl_if` 和 :meth:`.Index.ddl_if` 方法所创建的事件钩子不仅可以在 DDL 执行时被调用，
    还会在 SQL 编译阶段参与处理，比如在 :class:`.CreateTable` 对象渲染 ``CHECK (num > 5)`` 语句时。
    因此，通过 :meth:`.Constraint.ddl_if.callable_` 参数所接收的事件钩子会包含更丰富的参数，
    比如 ``dialect`` 关键字参数，以及 ``compiler`` 参数，该参数是 :class:`.DDLCompiler` 的一个实例，
    用于处理 CREATE TABLE 语句中内联渲染的部分。
    需要注意的是，当事件在 :class:`.DDLCompiler` 阶段触发时， **不会** 提供 ``bind`` 参数。
    因此，如果希望检测数据库版本信息，推荐使用传入的 :class:`.Dialect` 对象。
    比如，要检测 PostgreSQL 14 及以上版本，可以这样编写：

    .. sourcecode:: python+sql

        def only_pg_14(ddl_element, target, bind, dialect, **kw):
            return dialect.name == "postgresql" and dialect.server_version_info >= (14,)


        my_table = Table(
            "my_table",
            meta,
            Column("id", Integer, primary_key=True),
            Column("num", Integer),
            Column("data", String),
            Index("my_pg_index", "data").ddl_if(callable_=only_pg_14),
        )

    .. seealso::

        :meth:`.Constraint.ddl_if`

        :meth:`.Index.ddl_if`


.. tab:: 英文

    While the previously mentioned :meth:`.ExecutableDDLElement.execute_if` method is
    useful for custom :class:`.DDL` classes which need to invoke conditionally,
    there is also a common need for elements that are typically related to a
    particular :class:`.Table`, namely constraints and indexes, to also be
    subject to "conditional" rules, such as an index that includes features
    that are specific to a particular backend such as PostgreSQL or SQL Server.
    For this use case, the :meth:`.Constraint.ddl_if` and :meth:`.Index.ddl_if`
    methods may be used against constructs such as :class:`.CheckConstraint`,
    :class:`.UniqueConstraint` and :class:`.Index`, accepting the same
    arguments as the :meth:`.ExecutableDDLElement.execute_if` method in order to control
    whether or not their DDL will be emitted in terms of their parent
    :class:`.Table` object.  These methods may be used inline when
    creating the definition for a :class:`.Table`
    (or similarly, when using the ``__table_args__`` collection in an ORM
    declarative mapping), such as::

        from sqlalchemy import CheckConstraint, Index
        from sqlalchemy import MetaData, Table, Column
        from sqlalchemy import Integer, String

        meta = MetaData()

        my_table = Table(
            "my_table",
            meta,
            Column("id", Integer, primary_key=True),
            Column("num", Integer),
            Column("data", String),
            Index("my_pg_index", "data").ddl_if(dialect="postgresql"),
            CheckConstraint("num > 5").ddl_if(dialect="postgresql"),
        )

    In the above example, the :class:`.Table` construct refers to both an
    :class:`.Index` and a :class:`.CheckConstraint` construct, both which
    indicate ``.ddl_if(dialect="postgresql")``, which indicates that these
    elements will be included in the CREATE TABLE sequence only against the
    PostgreSQL dialect.  If we run ``meta.create_all()`` against the SQLite
    dialect, for example, neither construct will be included:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> sqlite_engine = create_engine("sqlite+pysqlite://", echo=True)
        >>> meta.create_all(sqlite_engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_info("my_table")
        [raw sql] ()
        PRAGMA temp.table_info("my_table")
        [raw sql] ()

        CREATE TABLE my_table (
            id INTEGER NOT NULL,
            num INTEGER,
            data VARCHAR,
            PRIMARY KEY (id)
        )

    However, if we run the same commands against a PostgreSQL database, we will
    see inline DDL for the CHECK constraint as well as a separate CREATE
    statement emitted for the index:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> postgresql_engine = create_engine(
        ...     "postgresql+psycopg2://scott:tiger@localhost/test", echo=True
        ... )
        >>> meta.create_all(postgresql_engine)
        {execsql}BEGIN (implicit)
        select relname from pg_class c join pg_namespace n on n.oid=c.relnamespace where pg_catalog.pg_table_is_visible(c.oid) and relname=%(name)s
        [generated in 0.00009s] {'name': 'my_table'}

        CREATE TABLE my_table (
            id SERIAL NOT NULL,
            num INTEGER,
            data VARCHAR,
            PRIMARY KEY (id),
            CHECK (num > 5)
        )
        [no key 0.00007s] {}
        CREATE INDEX my_pg_index ON my_table (data)
        [no key 0.00013s] {}
        COMMIT

    The :meth:`.Constraint.ddl_if` and :meth:`.Index.ddl_if` methods create
    an event hook that may be consulted not just at DDL execution time, as is the
    behavior with :meth:`.ExecutableDDLElement.execute_if`, but also within the SQL compilation
    phase of the :class:`.CreateTable` object, which is responsible for rendering
    the ``CHECK (num > 5)`` DDL inline within the CREATE TABLE statement.
    As such, the event hook that is received by the :meth:`.Constraint.ddl_if.callable_`
    parameter has a richer argument set present, including that there is
    a ``dialect`` keyword argument passed, as well as an instance of :class:`.DDLCompiler`
    via the ``compiler`` keyword argument for the "inline rendering" portion of the
    sequence.  The ``bind`` argument is **not** present when the event is triggered
    within the :class:`.DDLCompiler` sequence, so a modern event hook that wishes
    to inspect the database versioning information would best use the given
    :class:`.Dialect` object, such as to test PostgreSQL versioning:

    .. sourcecode:: python+sql

        def only_pg_14(ddl_element, target, bind, dialect, **kw):
            return dialect.name == "postgresql" and dialect.server_version_info >= (14,)


        my_table = Table(
            "my_table",
            meta,
            Column("id", Integer, primary_key=True),
            Column("num", Integer),
            Column("data", String),
            Index("my_pg_index", "data").ddl_if(callable_=only_pg_14),
        )

    .. seealso::

        :meth:`.Constraint.ddl_if`

        :meth:`.Index.ddl_if`



.. _schema_api_ddl:

DDL 表达式构造 API
-----------------------------

DDL Expression Constructs API

.. tab:: 中文

.. tab:: 英文

.. autofunction:: sort_tables

.. autofunction:: sort_tables_and_constraints

.. autoclass:: BaseDDLElement
    :members:

.. autoclass:: ExecutableDDLElement
    :members:

.. autoclass:: DDL
    :members:

.. autoclass:: _CreateDropBase

.. autoclass:: CreateTable
    :members:


.. autoclass:: DropTable
    :members:


.. autoclass:: CreateColumn
    :members:


.. autoclass:: CreateSequence
    :members:


.. autoclass:: DropSequence
    :members:


.. autoclass:: CreateIndex
    :members:


.. autoclass:: DropIndex
    :members:


.. autoclass:: AddConstraint
    :members:


.. autoclass:: DropConstraint
    :members:


.. autoclass:: CreateSchema
    :members:


.. autoclass:: DropSchema
    :members:
