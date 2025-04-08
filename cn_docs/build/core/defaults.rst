.. currentmodule:: sqlalchemy.schema

.. _metadata_defaults_toplevel:

.. _metadata_defaults:

列 INSERT/UPDATE 默认值
=============================

Column INSERT/UPDATE Defaults

.. tab:: 中文

    列的INSERT和UPDATE默认值指的是在对某行执行INSERT或UPDATE语句时，如果 **没有为该列提供值** ，则为该行的特定列创建 **默认值** 的函数。也就是说，如果一个表有一个名为“timestamp”的列，并且一个INSERT语句没有包含该列的值，则INSERT默认值会创建一个新值，例如当前时间，该值将用作插入“timestamp”列的值。如果语句 *确实* 包含该列的值，那么默认值则 *不会* 生效。

    列默认值可以是服务器端函数或常量值，这些值与模式一起在 :term:`DDL` 中定义，或者作为SQL表达式直接在由SQLAlchemy发出的INSERT或UPDATE语句中呈现；它们也可以是客户端Python函数或常量值，这些值在数据传递到数据库之前由SQLAlchemy调用。

    .. note::

        列默认值处理程序不应与拦截和修改INSERT和UPDATE语句的传入值的构造混淆，这些值 *确实* 在语句调用时提供。这被称为 *数据编组* (:term:`data marshalling`) ，即应用程序在将列值发送到数据库之前以某种方式修改列值。SQLAlchemy提供了一些实现此目的的方法，包括使用 :ref:`自定义数据类型 <types_typedecorator>` ， :ref:`SQL执行事件 <core_sql_events>` 以及在ORM中使用 :ref:`自定义验证器 <simple_validators>` 和 :ref:`属性事件 <orm_attribute_events>` 。列默认值仅在SQL :term:`DML` 语句中 **没有值存在** 时调用。

    SQLAlchemy提供了一系列关于默认值生成函数的功能，这些函数在INSERT和UPDATE语句期间针对不存在的值执行。选项包括：

    * 在INSERT和UPDATE操作期间使用的标量值作为默认值
    * 在INSERT和UPDATE操作期间执行的Python函数
    * 嵌入在INSERT语句中的SQL表达式（或在某些情况下提前执行）
    * 嵌入在UPDATE语句中的SQL表达式
    * 在INSERT期间使用的服务器端默认值
    * 在UPDATE期间使用的服务器端触发器标记

    所有插入/更新默认值的一般规则是，如果没有为特定列传递值作为 ``execute()`` 参数，则默认值生效；否则，使用给定的值。

.. tab:: 英文

    Column INSERT and UPDATE defaults refer to functions that create a **default
    value** for a particular column in a row as an INSERT or UPDATE statement is
    proceeding against that row, in the case where **no value was provided to the
    INSERT or UPDATE statement for that column**.  That is, if a table has a column
    called "timestamp", and an INSERT statement proceeds which does not include a
    value for this column, an INSERT default would create a new value, such as
    the current time, that is used as the value to be INSERTed into the "timestamp"
    column.  If the statement *does* include a value  for this column, then the
    default does *not* take place.

    Column defaults can be server-side functions or constant values which are
    defined in the database along with the schema in :term:`DDL`, or as SQL
    expressions which are rendered directly within an INSERT or UPDATE statement
    emitted by SQLAlchemy; they may also be client-side Python functions or
    constant values which are invoked by SQLAlchemy before data is passed to the
    database.

    .. note::

        A column default handler should not be confused with a construct that
        intercepts and modifies incoming values for INSERT and UPDATE statements
        which *are* provided to the statement as it is invoked.  This is known
        as :term:`data marshalling`, where a column value is modified in some way
        by the application before being sent to the database.  SQLAlchemy provides
        a few means of achieving this which include using :ref:`custom datatypes
        <types_typedecorator>`, :ref:`SQL execution events <core_sql_events>` and
        in the ORM :ref:`custom  validators <simple_validators>` as well as
        :ref:`attribute events <orm_attribute_events>`.    Column defaults are only
        invoked when there is **no value present** for a column in a SQL
        :term:`DML` statement.


    SQLAlchemy provides an array of features regarding default generation
    functions which take place for non-present values during INSERT and UPDATE
    statements. Options include:

    * Scalar values used as defaults during INSERT and UPDATE operations
    * Python functions which execute upon INSERT and UPDATE operations
    * SQL expressions which are embedded in INSERT statements (or in some cases execute beforehand)
    * SQL expressions which are embedded in UPDATE statements
    * Server side default values used during INSERT
    * Markers for server-side triggers used during UPDATE

    The general rule for all insert/update defaults is that they only take effect
    if no value for a particular column is passed as an ``execute()`` parameter;
    otherwise, the given value is used.

标量默认值
---------------

Scalar Defaults

.. tab:: 中文

    最简单的默认值类型是用于列的默认值的标量值::

        Table("mytable", metadata_obj, Column("somecolumn", Integer, default=12))

    如上所示，值 "12" 将在插入时作为列的值绑定，如果没有提供其他值。

    标量值也可以与 UPDATE 语句相关联，尽管这并不常见（因为 UPDATE 语句通常需要动态的默认值）::

        Table("mytable", metadata_obj, Column("somecolumn", Integer, onupdate=25))

.. tab:: 英文

    The simplest kind of default is a scalar value used as the default value of a column::

        Table("mytable", metadata_obj, Column("somecolumn", Integer, default=12))

    Above, the value "12" will be bound as the column value during an INSERT if no
    other value is supplied.

    A scalar value may also be associated with an UPDATE statement, though this is
    not very common (as UPDATE statements are usually looking for dynamic
    defaults)::

        Table("mytable", metadata_obj, Column("somecolumn", Integer, onupdate=25))

Python 执行函数
-------------------------

Python-Executed Functions

.. tab:: 中文

    :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 关键字参数也接受 Python 函数。
    当没有为该列提供其他值时，这些函数将在插入或更新时调用，并且返回的值将用作列的值。
    下面演示了一个粗略的“序列”，它将一个递增的计数器分配给主键列::

        # 一个递增的函数
        i = 0

        def mydefault():
            global i
            i += 1
            return i

        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True, default=mydefault),
        )

    需要注意的是，对于真正的“递增序列”行为，通常应该使用数据库的内置功能，
    这些功能可能包括序列对象或其他自增能力。对于主键列，SQLAlchemy 通常会自动使用这些能力。
    有关详细信息，请参见 :class:`~sqlalchemy.schema.Column` 的 API 文档，包括 :paramref:`_schema.Column.autoincrement` 标志，
    以及本章后面关于 :class:`~sqlalchemy.schema.Sequence` 部分的标准主键生成技术。

    为了演示 `onupdate`，我们将 Python 的 ``datetime`` 函数 ``now`` 分配给 :paramref:`_schema.Column.onupdate` 属性::

        import datetime

        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            # 定义 'last_updated' 为 datetime.now() 填充
            Column("last_updated", DateTime, onupdate=datetime.datetime.now),
        )

.. tab:: 英文

    The :paramref:`_schema.Column.default` and :paramref:`_schema.Column.onupdate` keyword arguments also accept Python
    functions. These functions are invoked at the time of insert or update if no
    other value for that column is supplied, and the value returned is used for
    the column's value. Below illustrates a crude "sequence" that assigns an
    incrementing counter to a primary key column::

        # a function which counts upwards
        i = 0


        def mydefault():
            global i
            i += 1
            return i


        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True, default=mydefault),
        )

    It should be noted that for real "incrementing sequence" behavior, the
    built-in capabilities of the database should normally be used, which may
    include sequence objects or other autoincrementing capabilities. For primary
    key columns, SQLAlchemy will in most cases use these capabilities
    automatically. See the API documentation for
    :class:`~sqlalchemy.schema.Column` including the :paramref:`_schema.Column.autoincrement` flag, as
    well as the section on :class:`~sqlalchemy.schema.Sequence` later in this
    chapter for background on standard primary key generation techniques.

    To illustrate onupdate, we assign the Python ``datetime`` function ``now`` to
    the :paramref:`_schema.Column.onupdate` attribute::

        import datetime

        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            # define 'last_updated' to be populated with datetime.now()
            Column("last_updated", DateTime, onupdate=datetime.datetime.now),
        )

    When an update statement executes and no value is passed for ``last_updated``,
    the ``datetime.datetime.now()`` Python function is executed and its return
    value used as the value for ``last_updated``. Notice that we provide ``now``
    as the function itself without calling it (i.e. there are no parenthesis
    following) - SQLAlchemy will execute the function at the time the statement
    executes.

.. _context_default_functions:

上下文敏感默认函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Context-Sensitive Default Functions

.. tab:: 中文

    当执行更新语句且没有为 ``last_updated`` 提供值时，
    ``datetime.datetime.now()`` Python 函数将被执行，并且其返回值将作为 ``last_updated`` 的值。
    请注意，我们提供的是函数本身，而不是调用它（即后面没有括号）——SQLAlchemy 将在语句执行时调用该函数。

    :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 使用的 Python 函数
    也可以利用当前语句的上下文来确定一个值。语句的 `context` 是一个内部 SQLAlchemy 对象，
    它包含关于正在执行的语句的所有信息，包括其源表达式、与其关联的参数以及游标。
    在默认值生成方面，典型的使用案例是访问行上正在插入或更新的其他值。
    要访问上下文，请提供一个接受单个 ``context`` 参数的函数::

        def mydefault(context):
            return context.get_current_parameters()["counter"] + 12

        t = Table(
            "mytable",
            metadata_obj,
            Column("counter", Integer),
            Column("counter_plus_twelve", Integer, default=mydefault, onupdate=mydefault),
        )

    上述默认值生成函数会在所有没有提供 ``counter_plus_twelve`` 值的 INSERT 和 UPDATE 语句中执行，
    并且该值将是执行中 ``counter`` 列的值加上数字 12。

    对于使用“executemany”样式执行的单个语句，例如通过 :meth:`_engine.Connection.execute` 传递多个参数集，
    用户定义的函数将为每个参数集调用一次。对于多值 :class:`_expression.Insert` 构造（例如，通过
    :meth:`_expression.Insert.values` 方法设置多个 VALUES 子句），用户定义的函数也将为每个参数集调用一次。

    当调用该函数时，可以从上下文对象（:class:`.DefaultExecutionContext` 的子类）中访问特殊方法
    :meth:`.DefaultExecutionContext.get_current_parameters`。该方法返回一个列键到值的字典，表示
    INSERT 或 UPDATE 语句的完整参数集。在多值 INSERT 构造的情况下，与单独的 VALUES 子句对应的
    参数子集将从完整的参数字典中隔离并单独返回。


.. tab:: 英文

    The Python functions used by :paramref:`_schema.Column.default` and
    :paramref:`_schema.Column.onupdate` may also make use of the current statement's
    context in order to determine a value. The `context` of a statement is an
    internal SQLAlchemy object which contains all information about the statement
    being executed, including its source expression, the parameters associated with
    it and the cursor. The typical use case for this context with regards to
    default generation is to have access to the other values being inserted or
    updated on the row. To access the context, provide a function that accepts a
    single ``context`` argument::

        def mydefault(context):
            return context.get_current_parameters()["counter"] + 12


        t = Table(
            "mytable",
            metadata_obj,
            Column("counter", Integer),
            Column("counter_plus_twelve", Integer, default=mydefault, onupdate=mydefault),
        )

    The above default generation function is applied so that it will execute for
    all INSERT and UPDATE statements where a value for ``counter_plus_twelve`` was
    otherwise not provided, and the value will be that of whatever value is present
    in the execution for the ``counter`` column, plus the number 12.

    For a single statement that is being executed using "executemany" style, e.g.
    with multiple parameter sets passed to :meth:`_engine.Connection.execute`, the
    user-defined function is called once for each set of parameters. For the use case of
    a multi-valued :class:`_expression.Insert` construct (e.g. with more than one VALUES
    clause set up via the :meth:`_expression.Insert.values` method), the user-defined function
    is also called once for each set of parameters.

    When the function is invoked, the special method
    :meth:`.DefaultExecutionContext.get_current_parameters` is available from
    the context object (an subclass of :class:`.DefaultExecutionContext`).  This
    method returns a dictionary of column-key to values that represents the
    full set of values for the INSERT or UPDATE statement.   In the case of a
    multi-valued INSERT construct, the subset of parameters that corresponds to
    the individual VALUES clause is isolated from the full parameter dictionary
    and returned alone.

.. _defaults_client_invoked_sql:

客户端调用的 SQL 表达式
------------------------------

Client-Invoked SQL Expressions

.. tab:: 中文

    :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 关键字也可以
    传递 SQL 表达式，在大多数情况下，这些表达式会以内联方式呈现在 INSERT 或 UPDATE 语句中::

        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            # 定义 'create_date' 默认值为 now()
            Column("create_date", DateTime, default=func.now()),
            # 定义 'key' 从 'keyvalues' 表中提取默认值
            Column(
                "key",
                String(20),
                default=select(keyvalues.c.key).where(keyvalues.c.type="type1"),
            ),
            # 定义 'last_modified' 在更新时使用 current_timestamp SQL 函数
            Column("last_modified", DateTime, onupdate=func.utc_timestamp()),
        )

    如上所示， ``create_date`` 列将在插入时使用 ``now()`` SQL 函数的结果填充（根据后台数据库，通常编译为 ``NOW()`` 或 ``CURRENT_TIMESTAMP``），
    ``key`` 列将使用来自另一个表的 SELECT 子查询的结果填充。``last_modified`` 列将在该表执行 UPDATE 语句时
    使用 SQL ``UTC_TIMESTAMP()`` MySQL 函数的值填充。

    .. note::

        使用 SQL 函数时，使用 :attr:`.func` 构造，我们“调用”命名的函数，例如像 ``func.now()`` 这样的括号。这不同于当我们指定一个 Python 可调用对象作为默认值
        （如 ``datetime.datetime``）时，我们传递函数本身，但不调用它。在 SQL 函数的情况下，调用 ``func.now()`` 返回 SQL 表达式对象，
        它将把“NOW”函数呈现为 SQL 中的内容。

    由 :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 指定的默认值和更新 SQL 表达式
    在 INSERT 或 UPDATE 语句执行时由 SQLAlchemy 显式调用，通常会以内联方式呈现在 DML 语句中，除了某些特殊情况，具体情况见下文。
    这与“服务器端”默认值不同，后者是表的 DDL 定义的一部分，例如作为 "CREATE TABLE" 语句的一部分，这些值可能更常见。
    有关服务器端默认值，请参见下一节 :ref:`server_defaults`。

    当 :paramref:`_schema.Column.default` 指定的 SQL 表达式用于主键列时，在某些情况下，SQLAlchemy 必须“预执行”
    默认生成的 SQL 函数，这意味着它会在一个单独的 SELECT 语句中调用该函数，然后将生成的值作为参数传递给 INSERT。
    这仅发生在 INSERT 语句的主键列需要返回该主键值的情况下，其中 RETURNING 或 ``cursor.lastrowid`` 可能不能使用。
    指定 :paramref:`~.expression.insert.inline` 标志的 :class:`_expression.Insert` 构造将始终以内联方式呈现默认表达式。

    当语句使用单个参数集执行时（即它不是“executemany”风格的执行），返回的
    :class:`~sqlalchemy.engine.CursorResult` 将包含一个集合，可以通过 :meth:`_engine.CursorResult.postfetch_cols` 访问，
    该集合包含所有使用内联执行默认值的 :class:`~sqlalchemy.schema.Column` 对象。
    类似地，所有绑定到语句的参数，包括所有预执行的 Python 和 SQL 表达式，都包含在
    :attr:`_engine.CursorResult.last_inserted_params` 或 :attr:`_engine.CursorResult.last_updated_params` 集合中。
    :attr:`_engine.CursorResult.inserted_primary_key` 集合包含插入行的主键值列表（一个列表，使得单列和复合列主键在同一格式下表示）。

.. tab:: 英文

    The :paramref:`_schema.Column.default` and :paramref:`_schema.Column.onupdate` keywords may
    also be passed SQL expressions, which are in most cases rendered inline within the
    INSERT or UPDATE statement::

        t = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            # define 'create_date' to default to now()
            Column("create_date", DateTime, default=func.now()),
            # define 'key' to pull its default from the 'keyvalues' table
            Column(
                "key",
                String(20),
                default=select(keyvalues.c.key).where(keyvalues.c.type="type1"),
            ),
            # define 'last_modified' to use the current_timestamp SQL function on update
            Column("last_modified", DateTime, onupdate=func.utc_timestamp()),
        )

    Above, the ``create_date`` column will be populated with the result of the
    ``now()`` SQL function (which, depending on backend, compiles into ``NOW()``
    or ``CURRENT_TIMESTAMP`` in most cases) during an INSERT statement, and the
    ``key`` column with the result of a SELECT subquery from another table. The
    ``last_modified`` column will be populated with the value of
    the SQL ``UTC_TIMESTAMP()`` MySQL function when an UPDATE statement is
    emitted for this table.

    .. note::

        When using SQL functions with the :attr:`.func` construct, we "call" the
        named function, e.g. with parenthesis as in ``func.now()``.   This differs
        from when we specify a Python callable as a default such as
        ``datetime.datetime``, where we pass the function itself, but we don't
        invoke it ourselves.   In the case of a SQL function, invoking
        ``func.now()`` returns the SQL expression object that will render the
        "NOW" function into the SQL being emitted.

    Default and update SQL expressions specified by :paramref:`_schema.Column.default` and
    :paramref:`_schema.Column.onupdate` are invoked explicitly by SQLAlchemy when an
    INSERT or UPDATE statement occurs, typically rendered inline within the DML
    statement except in certain cases listed below.   This is different than a
    "server side" default, which is part of the table's DDL definition, e.g. as
    part of the "CREATE TABLE" statement, which are likely more common.   For
    server side defaults, see the next section :ref:`server_defaults`.

    When a SQL expression indicated by :paramref:`_schema.Column.default` is used with
    primary key columns, there are some cases where SQLAlchemy must "pre-execute"
    the default generation SQL function, meaning it is invoked in a separate SELECT
    statement, and the resulting value is passed as a parameter to the INSERT.
    This only occurs for primary key columns for an INSERT statement that is being
    asked to return this primary key value, where RETURNING or ``cursor.lastrowid``
    may not be used.   An :class:`_expression.Insert` construct that specifies the
    :paramref:`~.expression.insert.inline` flag will always render default expressions
    inline.

    When the statement is executed with a single set of parameters (that is, it is
    not an "executemany" style execution), the returned
    :class:`~sqlalchemy.engine.CursorResult` will contain a collection accessible
    via :meth:`_engine.CursorResult.postfetch_cols` which contains a list of all
    :class:`~sqlalchemy.schema.Column` objects which had an inline-executed
    default. Similarly, all parameters which were bound to the statement, including
    all Python and SQL expressions which were pre-executed, are present in the
    :meth:`_engine.CursorResult.last_inserted_params` or
    :meth:`_engine.CursorResult.last_updated_params` collections on
    :class:`~sqlalchemy.engine.CursorResult`. The
    :attr:`_engine.CursorResult.inserted_primary_key` collection contains a list of primary
    key values for the row inserted (a list so that single-column and
    composite-column primary keys are represented in the same format).

.. _server_defaults:

服务器调用的 DDL 显式默认表达式
-----------------------------------------------

Server-invoked DDL-Explicit Default Expressions

.. tab:: 中文

    SQL 表达式默认值的一种变体是 :paramref:`_schema.Column.server_default`，它会在 :meth:`_schema.Table.create` 操作期间
    放置在 CREATE TABLE 语句中：

    .. sourcecode:: python+sql

        t = Table(
            "test",
            metadata_obj,
            Column("abc", String(20), server_default="abc"),
            Column("created_at", DateTime, server_default=func.sysdate()),
            Column("index_value", Integer, server_default=text("0")),
        )

    上述表的创建调用将生成：

    .. sourcecode:: sql

        CREATE TABLE test (
            abc varchar(20) default 'abc',
            created_at datetime default sysdate,
            index_value integer default 0
        )

    上面的示例演示了 :paramref:`_schema.Column.server_default` 的两种典型用法，
    即 SQL 函数（上述示例中的 SYSDATE）以及服务器端常量值（上述示例中的整数“0”）。建议使用
    :func:`_expression.text` 构造来处理任何字面 SQL 值，而不是传递原始值，因为 SQLAlchemy 通常不会对这些值执行任何引用或转义。

    像客户端生成的表达式一样，:paramref:`_schema.Column.server_default` 通常可以容纳 SQL 表达式，
    但是预计这些表达式通常是简单的函数和表达式，而不是嵌入式 SELECT 之类的复杂情况。


.. tab:: 英文

    A variant on the SQL expression default is the :paramref:`_schema.Column.server_default`, which gets
    placed in the CREATE TABLE statement during a :meth:`_schema.Table.create` operation:

    .. sourcecode:: python+sql

        t = Table(
            "test",
            metadata_obj,
            Column("abc", String(20), server_default="abc"),
            Column("created_at", DateTime, server_default=func.sysdate()),
            Column("index_value", Integer, server_default=text("0")),
        )

    A create call for the above table will produce:

    .. sourcecode:: sql

        CREATE TABLE test (
            abc varchar(20) default 'abc',
            created_at datetime default sysdate,
            index_value integer default 0
        )

    The above example illustrates the two typical use cases for :paramref:`_schema.Column.server_default`,
    that of the SQL function (SYSDATE in the above example) as well as a server-side constant
    value (the integer "0" in the above example).  It is advisable to use the
    :func:`_expression.text` construct for any literal SQL values as opposed to passing the
    raw value, as SQLAlchemy does not typically perform any quoting or escaping on
    these values.

    Like client-generated expressions, :paramref:`_schema.Column.server_default` can accommodate
    SQL expressions in general, however it is expected that these will usually be simple
    functions and expressions, and not the more complex cases like an embedded SELECT.


.. _triggered_columns:

标记隐式生成的值、时间戳和触发的列
----------------------------------------------------------------------

Marking Implicitly Generated Values, timestamps, and Triggered Columns

.. tab:: 中文

    根据其他服务器端数据库机制生成新值的列，例如在某些平台上看到的 TIMESTAMP 列中的数据库特定自动生成行为，
    以及在 INSERT 或 UPDATE 时调用的自定义触发器生成新值，可以使用 :class:`.FetchedValue` 作为标记进行标识::

        from sqlalchemy.schema import FetchedValue

        t = Table(
            "test",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("abc", TIMESTAMP, server_default=FetchedValue()),
            Column("def", String(20), server_onupdate=FetchedValue()),
        )

    `:class:`.FetchedValue` 标记不会影响 CREATE TABLE 的渲染 DDL。
    它标记该列为将在 INSERT 或 UPDATE 语句过程中由数据库填充的新值，对于支持的数据库，
    它可用于指示该列应作为语句的 RETURNING 或 OUTPUT 子句的一部分。
    SQLAlchemy ORM 等工具随后使用此标记，以便在此类操作之后知道如何获取该列的值。
    特别地，`:meth:`.ValuesBase.return_defaults` 方法可以与 :class:`_expression.Insert` 或 :class:`_expression.Update`
    构造一起使用，指示这些值应返回。

    有关在 ORM 中使用 :class:`.FetchedValue` 的详细信息，请参见 :ref:`orm_server_defaults`。

    .. warning:: 
        :paramref:`_schema.Column.server_onupdate` 指令 **当前** 不会生成 MySQL 的 "ON UPDATE CURRENT_TIMESTAMP()" 子句。 请参见 :ref:`mysql_timestamp_onupdate` 了解如何生成此子句的背景信息。

    .. seealso::

        :ref:`orm_server_defaults`

.. tab:: 英文

    Columns which generate a new value on INSERT or UPDATE based on other
    server-side database mechanisms, such as database-specific auto-generating
    behaviors such as seen with TIMESTAMP columns on some platforms, as well as
    custom triggers that invoke upon INSERT or UPDATE to generate a new value,
    may be called out using :class:`.FetchedValue` as a marker::

        from sqlalchemy.schema import FetchedValue

        t = Table(
            "test",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("abc", TIMESTAMP, server_default=FetchedValue()),
            Column("def", String(20), server_onupdate=FetchedValue()),
        )

    The :class:`.FetchedValue` indicator does not affect the rendered DDL for the
    CREATE TABLE.  Instead, it marks the column as one that will have a new value
    populated by the database during the process of an INSERT or UPDATE statement,
    and for supporting  databases may be used to indicate that the column should be
    part of a RETURNING or OUTPUT clause for the statement.    Tools such as the
    SQLAlchemy ORM then make use of this marker in order to know how to get at the
    value of the column after such an operation.   In particular, the
    :meth:`.ValuesBase.return_defaults` method can be used with an :class:`_expression.Insert`
    or :class:`_expression.Update` construct to indicate that these values should be
    returned.

    For details on using :class:`.FetchedValue` with the ORM, see
    :ref:`orm_server_defaults`.

    .. warning:: The :paramref:`_schema.Column.server_onupdate` directive
        **does not** currently produce MySQL's
        "ON UPDATE CURRENT_TIMESTAMP()" clause.  See
        :ref:`mysql_timestamp_onupdate` for background on how to produce
        this clause.


    .. seealso::

        :ref:`orm_server_defaults`

.. _defaults_sequences:

定义序列
------------------

Defining Sequences

.. tab:: 中文

    SQLAlchemy 使用 :class:`~sqlalchemy.schema.Sequence` 对象表示数据库序列，
    这被视为“列默认值”的特例。它仅对那些明确支持序列的数据库有效，
    在 SQLAlchemy 所包括的方言中，包括 PostgreSQL、Oracle 数据库、MS SQL Server 和 MariaDB。
    :class:`~sqlalchemy.schema.Sequence` 对象在其他情况下会被忽略。
    
    .. tip::
    
        在较新的数据库引擎中，生成整数主键值时，应该优先使用 :class:`.Identity` 构造，而非 :class:`.Sequence`。
        请参见 :ref:`identity_ddl` 部分了解有关此构造的背景信息。
    
    :class:`~sqlalchemy.schema.Sequence` 可以作为任何列的“默认”生成器，在 INSERT 操作期间使用，并且可以
    配置为在 UPDATE 操作期间触发（如果需要）。它通常与单个整数主键列一起使用::
    
        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                Sequence("cart_id_seq", start=1),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )
    
    如上所示，``cartitems`` 表与名为 ``cart_id_seq`` 的序列关联。
    执行 :meth:`.MetaData.create_all` 将生成：
    
    .. sourcecode:: sql
    
        CREATE SEQUENCE cart_id_seq START WITH 1
    
        CREATE TABLE cartitems (
          cart_id INTEGER NOT NULL,
          description VARCHAR(40),
          createdate TIMESTAMP WITHOUT TIME ZONE,
          PRIMARY KEY (cart_id)
        )
    
    .. tip::
    
      使用具有显式架构名称的表时（详细信息请参见 :ref:`schema_table_schema_name`），
      :class:`.Table` 配置的架构 **不会** 自动传递给嵌入的 :class:`.Sequence`，
      而是需要指定 :paramref:`.Sequence.schema`::
    
        Sequence("cart_id_seq", start=1, schema="some_schema")
    
      :class:`.Sequence` 也可以配置为自动使用当前使用的 :paramref:`.MetaData.schema` 设置；
      有关背景信息，请参见 :ref:`sequence_metadata`。
    
    当 :class:`_dml.Insert` DML 构造应用于 ``cartitems`` 表时，若未显式传递 ``cart_id`` 列的值，
    则会使用 ``cart_id_seq`` 序列在参与的数据库中生成一个值。通常，序列函数会嵌入在 INSERT 语句中，
    并与 RETURNING 一起使用，以便将新生成的值返回给 Python 进程：
    
    .. sourcecode:: sql
    
        INSERT INTO cartitems (cart_id, description, createdate)
        VALUES (next_val(cart_id_seq), 'some description', '2015-10-15 12:00:15')
        RETURNING cart_id
    
    当使用 :meth:`.Connection.execute` 调用 :class:`_dml.Insert` 构造时，
    新生成的主键标识符，包括但不限于使用 :class:`.Sequence` 生成的主键，
    可以从 :class:`.CursorResult` 构造中通过 :attr:`.CursorResult.inserted_primary_key` 属性访问。
    
    当 :class:`~sqlalchemy.schema.Sequence` 与 :class:`_schema.Column` 作为 **Python 端** 默认生成器关联时，
    该 :class:`.Sequence` 也会在类似 DDL 为拥有的 :class:`_schema.Table` 生成时
    受到 "CREATE SEQUENCE" 和 "DROP SEQUENCE" DDL 的影响，
    例如在使用 :meth:`.MetaData.create_all` 生成多个表的 DDL 时。
    
    :class:`.Sequence` 还可以直接与 :class:`.MetaData` 构造关联。
    这允许 :class:`.Sequence` 在多个 :class:`.Table` 中使用，并且允许继承 :paramref:`.MetaData.schema` 参数。
    有关背景信息，请参见 :ref:`sequence_metadata`。


.. tab:: 英文

    SQLAlchemy represents database sequences using the
    :class:`~sqlalchemy.schema.Sequence` object, which is considered to be a
    special case of "column default". It only has an effect on databases which have
    explicit support for sequences, which among SQLAlchemy's included dialects
    includes PostgreSQL, Oracle Database, MS SQL Server, and MariaDB.  The
    :class:`~sqlalchemy.schema.Sequence` object is otherwise ignored.
    
    .. tip::
    
        In newer database engines, the :class:`.Identity` construct should likely
        be preferred vs. :class:`.Sequence` for generation of integer primary key
        values. See the section :ref:`identity_ddl` for background on this
        construct.
    
    The :class:`~sqlalchemy.schema.Sequence` may be placed on any column as a
    "default" generator to be used during INSERT operations, and can also be
    configured to fire off during UPDATE operations if desired. It is most
    commonly used in conjunction with a single integer primary key column::
    
        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                Sequence("cart_id_seq", start=1),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )
    
    Where above, the table ``cartitems`` is associated with a sequence named
    ``cart_id_seq``.   Emitting :meth:`.MetaData.create_all` for the above
    table will include:
    
    .. sourcecode:: sql
    
        CREATE SEQUENCE cart_id_seq START WITH 1
    
        CREATE TABLE cartitems (
          cart_id INTEGER NOT NULL,
          description VARCHAR(40),
          createdate TIMESTAMP WITHOUT TIME ZONE,
          PRIMARY KEY (cart_id)
        )
    
    .. tip::
    
      When using tables with explicit schema names (detailed at
      :ref:`schema_table_schema_name`), the configured schema of the :class:`.Table`
      is **not** automatically shared by an embedded :class:`.Sequence`, instead,
      specify :paramref:`.Sequence.schema`::
    
        Sequence("cart_id_seq", start=1, schema="some_schema")
    
      The :class:`.Sequence` may also be made to automatically make use of the
      :paramref:`.MetaData.schema` setting on the :class:`.MetaData` in use;
      see :ref:`sequence_metadata` for background.
    
    When :class:`_dml.Insert` DML constructs are invoked against the ``cartitems``
    table, without an explicit value passed for the ``cart_id`` column, the
    ``cart_id_seq`` sequence will be used to generate a value on participating
    backends. Typically, the sequence function is embedded in the INSERT statement,
    which is combined with RETURNING so that the newly generated value can be
    returned to the Python process:
    
    .. sourcecode:: sql
    
        INSERT INTO cartitems (cart_id, description, createdate)
        VALUES (next_val(cart_id_seq), 'some description', '2015-10-15 12:00:15')
        RETURNING cart_id
    
    When using :meth:`.Connection.execute` to invoke an :class:`_dml.Insert` construct,
    newly generated primary key identifiers, including but not limited to those
    generated using :class:`.Sequence`, are available from the :class:`.CursorResult`
    construct using the :attr:`.CursorResult.inserted_primary_key` attribute.
    
    When the :class:`~sqlalchemy.schema.Sequence` is associated with a
    :class:`_schema.Column` as its **Python-side** default generator, the
    :class:`.Sequence` will also be subject to "CREATE SEQUENCE" and "DROP
    SEQUENCE" DDL when similar DDL is emitted for the owning :class:`_schema.Table`,
    such as when using :meth:`.MetaData.create_all` to generate DDL for a series
    of tables.
    
    The :class:`.Sequence` may also be associated with a
    :class:`.MetaData` construct directly.  This allows the :class:`.Sequence`
    to be used in more than one :class:`.Table` at a time and also allows the
    :paramref:`.MetaData.schema` parameter to be inherited.  See the section
    :ref:`sequence_metadata` for background.

将序列与 SERIAL 列关联
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Associating a Sequence on a SERIAL column

.. tab:: 中文

    PostgreSQL 的 SERIAL 数据类型是一个自动递增的类型，在发出 CREATE TABLE 时隐式创建 PostgreSQL 序列。
    当 :class:`.Sequence` 构造用于 :class:`_schema.Column` 时，可以通过为 :paramref:`.Sequence.optional` 参数指定 ``True`` 来指示
    在此特定情况下不使用它。
    这允许在没有其他主键生成系统的后端使用给定的 :class:`.Sequence`，但对于 PostgreSQL 等将自动为特定列生成序列的后端则忽略它::

        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                # 在可用时使用显式的 Sequence，但在 PostgreSQL 上不使用，
                # 因为 SERIAL 会被使用
                Sequence("cart_id_seq", start=1, optional=True),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )

    在上面的示例中，PostgreSQL 的 ``CREATE TABLE`` 将对 ``cart_id`` 列使用 ``SERIAL`` 数据类型，
    而 ``cart_id_seq`` 序列将被忽略。但是在 Oracle 数据库上，``cart_id_seq`` 序列将被显式创建。

    .. tip::

        SERIAL 和 SEQUENCE 的这种特定交互是相当传统的做法，和其他情况一样，使用 :class:`.Identity` 替代它会简化操作，
        仅在所有支持的后端上使用 ``IDENTITY``。

.. tab:: 英文

    PostgreSQL's SERIAL datatype is an auto-incrementing type that implies
    the implicit creation of a PostgreSQL sequence when CREATE TABLE is emitted.
    The :class:`.Sequence` construct, when indicated for a :class:`_schema.Column`,
    may indicate that it should not be used in this specific case by specifying
    a value of ``True`` for the :paramref:`.Sequence.optional` parameter.
    This allows the given :class:`.Sequence` to be used for backends that have no
    alternative primary key generation system but to ignore it for backends
    such as PostgreSQL which will automatically generate a sequence for a particular
    column::

        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                # use an explicit Sequence where available, but not on
                # PostgreSQL where SERIAL will be used
                Sequence("cart_id_seq", start=1, optional=True),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )

    In the above example, ``CREATE TABLE`` for PostgreSQL will make use of the
    ``SERIAL`` datatype for the ``cart_id`` column, and the ``cart_id_seq``
    sequence will be ignored.  However on Oracle Database, the ``cart_id_seq``
    sequence will be created explicitly.

    .. tip::

        This particular interaction of SERIAL and SEQUENCE is fairly legacy, and
        as in other cases, using :class:`.Identity` instead will simplify the
        operation to simply use ``IDENTITY`` on all supported backends.


独立执行序列
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Executing a Sequence Standalone

.. tab:: 中文


    SEQUENCE 是 SQL 中的一个一类模式对象，可以独立地在数据库中生成值。如果你有一个 :class:`.Sequence`
    对象，可以通过将其直接传递给 SQL 执行方法来调用它的“下一个值”指令::

        with my_engine.connect() as conn:
            seq = Sequence("some_sequence", start=1)
            nextid = conn.execute(seq)

    为了在 SQL 语句（如 SELECT 或 INSERT）中嵌入 :class:`.Sequence` 的“下一个值”函数，
    可以使用 :meth:`.Sequence.next_value` 方法，它将在语句编译时渲染出一个适合目标后端的 SQL 函数：

    .. sourcecode:: pycon+sql

        >>> my_seq = Sequence("some_sequence", start=1)
        >>> stmt = select(my_seq.next_value())
        >>> print(stmt.compile(dialect=postgresql.dialect()))
        {printsql}SELECT nextval('some_sequence') AS next_value_1

.. tab:: 英文

    A SEQUENCE is a first class schema object in SQL and can be used to generate
    values independently in the database.   If you have a :class:`.Sequence`
    object, it can be invoked with its "next value" instruction by
    passing it directly to a SQL execution method::

        with my_engine.connect() as conn:
            seq = Sequence("some_sequence", start=1)
            nextid = conn.execute(seq)

    In order to embed the "next value" function of a :class:`.Sequence`
    inside of a SQL statement like a SELECT or INSERT, use the :meth:`.Sequence.next_value`
    method, which will render at statement compilation time a SQL function that is
    appropriate for the target backend:

    .. sourcecode:: pycon+sql

        >>> my_seq = Sequence("some_sequence", start=1)
        >>> stmt = select(my_seq.next_value())
        >>> print(stmt.compile(dialect=postgresql.dialect()))
        {printsql}SELECT nextval('some_sequence') AS next_value_1

.. _sequence_metadata:

将序列与元数据关联
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Associating a Sequence with the MetaData

.. tab:: 中文


    对于要与任意 :class:`.Table` 对象关联的 :class:`.Sequence`，
    可以通过 :paramref:`.Sequence.metadata` 参数将其与特定的 :class:`_schema.MetaData` 关联::
    
        seq = Sequence("my_general_seq", metadata=metadata_obj, start=1)
    
    然后，可以像平常一样将该序列与列关联起来::
    
        table = Table(
            "cartitems",
            metadata_obj,
            seq,
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )
    
    在上面的示例中， :class:`.Sequence` 对象被视为一个独立的模式构造，可以独立存在或在表之间共享。
    
    显式将 :class:`.Sequence` 与 :class:`_schema.MetaData` 关联会带来以下行为：
    
    * :class:`.Sequence` 将继承目标 :class:`_schema.MetaData` 中指定的 :paramref:`_schema.MetaData.schema` 参数，
      该参数影响 CREATE / DROP DDL 的生成，以及如何在 SQL 语句中渲染 :meth:`.Sequence.next_value` 函数。
    
    * :meth:`_schema.MetaData.create_all` 和 :meth:`_schema.MetaData.drop_all` 方法将为该 :class:`.Sequence`
      发出 CREATE / DROP，即使该 :class:`.Sequence` 未与任何属于该 :class:`_schema.MetaData` 的
      :class:`_schema.Table` / :class:`_schema.Column` 关联。

.. tab:: 英文

    For a :class:`.Sequence` that is to be associated with arbitrary
    :class:`.Table` objects, the :class:`.Sequence` may be associated with
    a particular :class:`_schema.MetaData`, using the
    :paramref:`.Sequence.metadata` parameter::
    
        seq = Sequence("my_general_seq", metadata=metadata_obj, start=1)
    
    Such a sequence can then be associated with columns in the usual way::
    
        table = Table(
            "cartitems",
            metadata_obj,
            seq,
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )
    
    In the above example, the :class:`.Sequence` object is treated as an
    independent schema construct that can exist on its own or be shared among
    tables.
    
    Explicitly associating the :class:`.Sequence` with :class:`_schema.MetaData`
    allows for the following behaviors:
    
    * The :class:`.Sequence` will inherit the :paramref:`_schema.MetaData.schema`
      parameter specified to the target :class:`_schema.MetaData`, which
      affects the production of CREATE / DROP DDL as well as how the
      :meth:`.Sequence.next_value` function is rendered in SQL statements.
    
    * The :meth:`_schema.MetaData.create_all` and :meth:`_schema.MetaData.drop_all`
      methods will emit CREATE / DROP for this :class:`.Sequence`,
      even if the :class:`.Sequence` is not associated with any
      :class:`_schema.Table` / :class:`_schema.Column` that's a member of this
      :class:`_schema.MetaData`.

将序列关联为服务器端默认值
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Associating a Sequence as the Server Side Default

.. tab:: 中文

    .. note:: 以下技术仅在 PostgreSQL 数据库中有效。它不适用于 Oracle 数据库。

    前面的章节展示了如何将 :class:`.Sequence` 与 :class:`_schema.Column` 关联，作为 **Python 端默认生成器**::

        Column(
            "cart_id",
            Integer,
            Sequence("cart_id_seq", metadata=metadata_obj, start=1),
            primary_key=True,
        )

    在上述情况下， :class:`.Sequence` 将自动在相关的 :class:`_schema.Table` 发出 CREATE / DROP 时受到 CREATE SEQUENCE / DROP SEQUENCE DDL 的影响。
    然而，当发出 CREATE TABLE 时，序列 **不会** 作为列的服务器端默认值出现。

    如果我们希望序列作为服务器端默认值使用，
    即使我们从 SQL 命令行发出 INSERT 命令到表中，它也会生效，我们可以使用 :paramref:`_schema.Column.server_default`
    参数与序列的值生成函数结合使用，该函数可以通过 :meth:`.Sequence.next_value` 方法获取。下面我们展示了同一个 :class:`.Sequence`
    同时作为 Python 端默认生成器和服务器端默认生成器与 :class:`_schema.Column` 关联::

        cart_id_seq = Sequence("cart_id_seq", metadata=metadata_obj, start=1)
        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                cart_id_seq,
                server_default=cart_id_seq.next_value(),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )

    或者在 ORM 中使用::

        class CartItem(Base):
            __tablename__ = "cartitems"

            cart_id_seq = Sequence("cart_id_seq", metadata=Base.metadata, start=1)
            cart_id = Column(
                Integer, cart_id_seq, server_default=cart_id_seq.next_value(), primary_key=True
            )
            description = Column(String(40))
            createdate = Column(DateTime)

    当发出 "CREATE TABLE" 语句时，在 PostgreSQL 上会发出如下语句：

    .. sourcecode:: sql

        CREATE TABLE cartitems (
            cart_id INTEGER DEFAULT nextval('cart_id_seq') NOT NULL,
            description VARCHAR(40),
            createdate TIMESTAMP WITHOUT TIME ZONE,
            PRIMARY KEY (cart_id)
        )

    将 :class:`.Sequence` 同时放置在 Python 端和服务器端默认生成上下文中，确保了“主键获取”逻辑在所有情况下都能正常工作。
    通常，启用序列的数据库也支持 INSERT 语句的 RETURNING，这是 SQLAlchemy 在发出该语句时自动使用的功能。
    然而，如果某个特定插入没有使用 RETURNING，那么 SQLAlchemy 会倾向于在 INSERT 语句之外“预执行”序列，
    这仅在序列作为 Python 端默认生成器函数时有效。

    该示例还将 :class:`.Sequence` 直接与包含的 :class:`_schema.MetaData` 关联，
    这再次确保了 :class:`.Sequence` 完全与 :class:`_schema.MetaData` 集合的参数相关联，包括默认模式（如果有的话）。

    .. seealso::

        :ref:`postgresql_sequences` - 在 PostgreSQL 方言文档中

        :ref:`oracle_returning` - 在 Oracle 数据库方言文档中

.. tab:: 英文

    .. note:: The following technique is known to work only with the PostgreSQL
       database.  It does not work with Oracle Database.
    
    The preceding sections illustrate how to associate a :class:`.Sequence` with a
    :class:`_schema.Column` as the **Python side default generator**::
    
        Column(
            "cart_id",
            Integer,
            Sequence("cart_id_seq", metadata=metadata_obj, start=1),
            primary_key=True,
        )
    
    In the above case, the :class:`.Sequence` will automatically be subject
    to CREATE SEQUENCE / DROP SEQUENCE DDL when the related :class:`_schema.Table`
    is subject to CREATE / DROP.  However, the sequence will **not** be present
    as the server-side default for the column when CREATE TABLE is emitted.
    
    If we want the sequence to be used as a server-side default,
    meaning it takes place even if we emit INSERT commands to the table from
    the SQL command line, we can use the :paramref:`_schema.Column.server_default`
    parameter in conjunction with the value-generation function of the
    sequence, available from the :meth:`.Sequence.next_value` method.  Below
    we illustrate the same :class:`.Sequence` being associated with the
    :class:`_schema.Column` both as the Python-side default generator as well as
    the server-side default generator::
    
        cart_id_seq = Sequence("cart_id_seq", metadata=metadata_obj, start=1)
        table = Table(
            "cartitems",
            metadata_obj,
            Column(
                "cart_id",
                Integer,
                cart_id_seq,
                server_default=cart_id_seq.next_value(),
                primary_key=True,
            ),
            Column("description", String(40)),
            Column("createdate", DateTime()),
        )
    
    or with the ORM::
    
        class CartItem(Base):
            __tablename__ = "cartitems"
    
            cart_id_seq = Sequence("cart_id_seq", metadata=Base.metadata, start=1)
            cart_id = Column(
                Integer, cart_id_seq, server_default=cart_id_seq.next_value(), primary_key=True
            )
            description = Column(String(40))
            createdate = Column(DateTime)
    
    When the "CREATE TABLE" statement is emitted, on PostgreSQL it would be
    emitted as:
    
    .. sourcecode:: sql
    
        CREATE TABLE cartitems (
            cart_id INTEGER DEFAULT nextval('cart_id_seq') NOT NULL,
            description VARCHAR(40),
            createdate TIMESTAMP WITHOUT TIME ZONE,
            PRIMARY KEY (cart_id)
        )
    
    Placement of the :class:`.Sequence` in both the Python-side and server-side
    default generation contexts ensures that the "primary key fetch" logic
    works in all cases.  Typically, sequence-enabled databases also support
    RETURNING for INSERT statements, which is used automatically by SQLAlchemy
    when emitting this statement.  However if RETURNING is not used for a particular
    insert, then SQLAlchemy would prefer to "pre-execute" the sequence outside
    of the INSERT statement itself, which only works if the sequence is
    included as the Python-side default generator function.
    
    The example also associates the :class:`.Sequence` with the enclosing
    :class:`_schema.MetaData` directly, which again ensures that the :class:`.Sequence`
    is fully associated with the parameters of the :class:`_schema.MetaData` collection
    including the default schema, if any.
    
    .. seealso::
    
        :ref:`postgresql_sequences` - in the PostgreSQL dialect documentation
    
        :ref:`oracle_returning` - in the Oracle Database dialect documentation

.. _computed_ddl:

计算列 (GENERATED ALWAYS AS)
--------------------------------------

Computed Columns (GENERATED ALWAYS AS)

.. tab:: 中文

    :class:`.Computed` 构造允许 :class:`_schema.Column` 在 DDL 中声明为“GENERATED ALWAYS AS”列，
    即其值由数据库服务器计算得出。该构造接受一个 SQL 表达式，通常通过字符串或 :func:`_expression.text` 构造文本声明，
    类似于 :class:`.CheckConstraint`。然后，SQL 表达式由数据库服务器解释，以确定该列在一行中的值。

    示例::

        from sqlalchemy import Table, Column, MetaData, Integer, Computed

        metadata_obj = MetaData()

        square = Table(
            "square",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("side", Integer),
            Column("area", Integer, Computed("side * side")),
            Column("perimeter", Integer, Computed("4 * side")),
        )

    当在 PostgreSQL 12 后端运行时，``square`` 表的 DDL 将如下所示：

    .. sourcecode:: sql

        CREATE TABLE square (
            id SERIAL NOT NULL,
            side INTEGER,
            area INTEGER GENERATED ALWAYS AS (side * side) STORED,
            perimeter INTEGER GENERATED ALWAYS AS (4 * side) STORED,
            PRIMARY KEY (id)
        )

    无论该值是在 INSERT 和 UPDATE 时持久化，还是在查询时计算，都是数据库的实现细节；
    前者称为“存储”，后者称为“虚拟”。一些数据库实现支持两者，但有些只支持其中之一。
    可以通过可选的 :paramref:`.Computed.persisted` 标志指定为 ``True`` 或 ``False``，
    以指示是否应在 DDL 中渲染“STORED”或“VIRTUAL”关键字，
    但如果目标后端不支持该关键字，则会引发错误；如果未设置该标志，将使用目标后端的有效默认值。

    :class:`.Computed` 构造是 :class:`.FetchedValue` 对象的子类，
    它将自身设置为目标 :class:`_schema.Column` 的“服务器默认值”和“服务器更新时默认值”生成器，
    这意味着在生成 INSERT 和 UPDATE 语句时，它将被视为默认生成列，
    同时，在使用 ORM 时，它将作为生成列被提取。
    这包括它将成为数据库 RETURNING 子句的一部分，
    对于支持 RETURNING 且生成的值需要被立即提取的数据库。

    .. note:: 使用 :class:`.Computed` 构造定义的 :class:`_schema.Column` 不能存储任何超出服务器应用于该列的值；
       当前，当向这样的列传递一个值以在 INSERT 或 UPDATE 中写入时，SQLAlchemy 的行为是该值将被忽略。

    “GENERATED ALWAYS AS”当前已知被以下数据库支持：

    * MySQL 5.7 及更高版本

    * MariaDB 10.x 系列及更高版本

    * PostgreSQL 从版本 12 开始

    * Oracle 数据库 - 需要注意的是 RETURNING 在 UPDATE 中无法正确工作（如果包含计算列的 UPDATE..RETURNING 被渲染时，会发出警告）

    * Microsoft SQL Server

    * SQLite 从版本 3.31 开始

    当 :class:`.Computed` 与不支持的后端一起使用时，如果目标方言不支持它，则在尝试渲染该构造时会引发 :class:`.CompileError`。
    否则，如果方言支持它，但使用的特定数据库服务器版本不支持它，则在发出 DDL 到数据库时会引发 :class:`.DBAPIError` 的子类，通常是 :class:`.OperationalError`。

    .. seealso::

        :class:`.Computed`

.. tab:: 英文

    The :class:`.Computed` construct allows a :class:`_schema.Column` to be declared in
    DDL as a "GENERATED ALWAYS AS" column, that is, one which has a value that is
    computed by the database server.    The construct accepts a SQL expression
    typically declared textually using a string or the :func:`_expression.text` construct, in
    a similar manner as that of :class:`.CheckConstraint`.   The SQL expression is
    then interpreted by the database server in order to determine the value for the
    column within a row.
    
    Example::
    
        from sqlalchemy import Table, Column, MetaData, Integer, Computed
    
        metadata_obj = MetaData()
    
        square = Table(
            "square",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("side", Integer),
            Column("area", Integer, Computed("side * side")),
            Column("perimeter", Integer, Computed("4 * side")),
        )
    
    The DDL for the ``square`` table when run on a PostgreSQL 12 backend will look
    like:
    
    .. sourcecode:: sql
    
        CREATE TABLE square (
            id SERIAL NOT NULL,
            side INTEGER,
            area INTEGER GENERATED ALWAYS AS (side * side) STORED,
            perimeter INTEGER GENERATED ALWAYS AS (4 * side) STORED,
            PRIMARY KEY (id)
        )
    
    Whether the value is persisted upon INSERT and UPDATE, or if it is calculated
    on fetch, is an implementation detail of the database; the former is known as
    "stored" and the latter is known as "virtual".  Some database implementations
    support both, but some only support one or the other.  The optional
    :paramref:`.Computed.persisted` flag may be specified as ``True`` or ``False``
    to indicate if the "STORED" or "VIRTUAL" keyword should be rendered in DDL,
    however this will raise an error if the keyword is not supported by the target
    backend; leaving it unset will use  a working default for the target backend.
    
    The :class:`.Computed` construct is a subclass of the :class:`.FetchedValue`
    object, and will set itself up as both the "server default" and "server
    onupdate" generator for the target :class:`_schema.Column`, meaning it will be treated
    as a default generating column when INSERT and UPDATE statements are generated,
    as well as that it will be fetched as a generating column when using the ORM.
    This includes that it will be part of the RETURNING clause of the database
    for databases which support RETURNING and the generated values are to be
    eagerly fetched.
    
    .. note:: A :class:`_schema.Column` that is defined with the :class:`.Computed`
       construct may not store any value outside of that which the server applies
       to it;  SQLAlchemy's behavior when a value is passed for such a column
       to be written in INSERT or UPDATE is currently that the value will be
       ignored.
    
    "GENERATED ALWAYS AS" is currently known to be supported by:
    
    * MySQL version 5.7 and onwards
    
    * MariaDB 10.x series and onwards
    
    * PostgreSQL as of version 12
    
    * Oracle Database - with the caveat that RETURNING does not work correctly with
      UPDATE (a warning will be emitted to this effect when the UPDATE..RETURNING
      that includes a computed column is rendered)
    
    * Microsoft SQL Server
    
    * SQLite as of version 3.31
    
    When :class:`.Computed` is used with an unsupported backend, if the target
    dialect does not support it, a :class:`.CompileError` is raised when attempting
    to render the construct.  Otherwise, if the dialect supports it but the
    particular database server version in use does not, then a subclass of
    :class:`.DBAPIError`, usually :class:`.OperationalError`, is raised when the
    DDL is emitted to the database.
    
    .. seealso::
    
        :class:`.Computed`

.. _identity_ddl:

标识列 (GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY)
-----------------------------------------------------------------

Identity Columns (GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY)

.. versionadded:: 1.4

.. tab:: 中文

    :class:`.Identity` 构造允许 :class:`_schema.Column` 声明为身份列，并在 DDL 中呈现为 "GENERATED { ALWAYS | BY DEFAULT } AS IDENTITY"。
    身份列的值由数据库服务器自动生成，使用递增（或递减）序列。该构造与 :class:`.Sequence` 大多数选项共享，用于控制数据库行为。

    示例::

        from sqlalchemy import Table, Column, MetaData, Integer, Identity, String

        metadata_obj = MetaData()

        data = Table(
            "data",
            metadata_obj,
            Column("id", Integer, Identity(start=42, cycle=True), primary_key=True),
            Column("data", String),
        )

    在 PostgreSQL 12 后端运行时，``data`` 表的 DDL 将如下所示：

    .. sourcecode:: sql

        CREATE TABLE data (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 42 CYCLE) NOT NULL,
            data VARCHAR,
            PRIMARY KEY (id)
        )

    如果语句中没有为 ``id`` 列提供值，数据库将在插入时自动为 ``id`` 列生成一个值，从 ``42`` 开始。
    身份列还可以要求数据库生成该列的值，忽略语句中传递的值或根据后端抛出错误。要激活此模式，可以在 :class:`.Identity` 构造中将 :paramref:`_schema.Identity.always` 参数设置为 ``True``。更新前面的示例以包含此参数将生成以下 DDL：

    .. sourcecode:: sql

        CREATE TABLE data (
            id INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 42 CYCLE) NOT NULL,
            data VARCHAR,
            PRIMARY KEY (id)
        )

    :class:`.Identity` 构造是 :class:`.FetchedValue` 对象的子类，
    并将其设置为目标 :class:`_schema.Column` 的“服务器默认值”生成器，
    这意味着在生成 INSERT 语句时，它将作为默认生成列，
    并且在使用 ORM 时，它将作为生成列被提取。
    这包括它将成为数据库 RETURNING 子句的一部分，
    对于支持 RETURNING 且生成的值需要被立即提取的数据库。

    :class:`.Identity` 构造当前已知被以下数据库支持：

    * PostgreSQL 从版本 10 开始。

    * Oracle 数据库从版本 12 开始。它还支持传递 ``always=None`` 启用默认生成模式，并且支持参数 ``on_null=True``， 用于指定与 "BY DEFAULT" 身份列一起使用的 "ON NULL"。

    * Microsoft SQL Server。 MSSQL 使用自定义语法，仅支持 ``start`` 和 ``increment`` 参数，忽略所有其他参数。

    当 :class:`.Identity` 与不支持的后端一起使用时，它将被忽略，使用默认的 SQLAlchemy 自动递增列逻辑。

    当 :class:`_schema.Column` 同时指定 :class:`.Identity` 和将 :paramref:`_schema.Column.autoincrement` 设置为 ``False`` 时，将引发错误。

    .. seealso::

        :class:`.Identity`


.. tab:: 英文

    The :class:`.Identity` construct allows a :class:`_schema.Column` to be declared
    as an identity column and rendered in DDL as "GENERATED { ALWAYS | BY DEFAULT }
    AS IDENTITY".  An identity column has its value automatically generated by the
    database server using an incrementing (or decrementing) sequence. The construct
    shares most of its option to control the database behaviour with
    :class:`.Sequence`.
    
    Example::
    
        from sqlalchemy import Table, Column, MetaData, Integer, Identity, String
    
        metadata_obj = MetaData()
    
        data = Table(
            "data",
            metadata_obj,
            Column("id", Integer, Identity(start=42, cycle=True), primary_key=True),
            Column("data", String),
        )
    
    The DDL for the ``data`` table when run on a PostgreSQL 12 backend will look
    like:
    
    .. sourcecode:: sql
    
        CREATE TABLE data (
            id INTEGER GENERATED BY DEFAULT AS IDENTITY (START WITH 42 CYCLE) NOT NULL,
            data VARCHAR,
            PRIMARY KEY (id)
        )
    
    The database will generate a value for the ``id`` column upon insert,
    starting from ``42``, if the statement did not already contain a value for
    the ``id`` column.
    An identity column can also require that the database generates the value
    of the column, ignoring the value passed with the statement or raising an
    error, depending on the backend. To activate this mode, set the parameter
    :paramref:`_schema.Identity.always` to ``True`` in the
    :class:`.Identity` construct. Updating the previous
    example to include this parameter will generate the following DDL:
    
    .. sourcecode:: sql
    
        CREATE TABLE data (
            id INTEGER GENERATED ALWAYS AS IDENTITY (START WITH 42 CYCLE) NOT NULL,
            data VARCHAR,
            PRIMARY KEY (id)
        )
    
    The :class:`.Identity` construct is a subclass of the :class:`.FetchedValue`
    object, and will set itself up as the "server default" generator for the
    target :class:`_schema.Column`, meaning it will be treated
    as a default generating column when INSERT statements are generated,
    as well as that it will be fetched as a generating column when using the ORM.
    This includes that it will be part of the RETURNING clause of the database
    for databases which support RETURNING and the generated values are to be
    eagerly fetched.
    
    The :class:`.Identity` construct is currently known to be supported by:
    
    * PostgreSQL as of version 10.
    
    * Oracle Database as of version 12. It also supports passing ``always=None`` to
      enable the default generated mode and the parameter ``on_null=True`` to
      specify "ON NULL" in conjunction with a "BY DEFAULT" identity column.
    
    * Microsoft SQL Server. MSSQL uses a custom syntax that only supports the
      ``start`` and ``increment`` parameters, and ignores all other.
    
    When :class:`.Identity` is used with an unsupported backend, it is ignored,
    and the default SQLAlchemy logic for autoincrementing columns is used.
    
    An error is raised when a :class:`_schema.Column` specifies both an
    :class:`.Identity` and also sets :paramref:`_schema.Column.autoincrement`
    to ``False``.
    
    .. seealso::
    
        :class:`.Identity`


默认对象 API
-------------------

Default Objects API

.. autoclass:: Computed
    :members:


.. autoclass:: ColumnDefault


.. autoclass:: DefaultClause


.. autoclass:: DefaultGenerator


.. autoclass:: FetchedValue


.. autoclass:: Sequence
    :members:


.. autoclass:: Identity
    :members:
