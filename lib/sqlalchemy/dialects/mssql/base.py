# dialects/mssql/base.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

"""
.. dialect:: mssql
    :name: Microsoft SQL Server
    :normal_support: 2012+
    :best_effort: 2005+

.. _mssql_external_dialects:

外部方言
-----------------

External Dialects

.. tab:: 中文

    除了上述原生支持 SQLAlchemy 的 DBAPI 层之外，还有其他与 SQL Server 兼容的 DBAPI 层的第三方方言。请参阅:ref:`dialect_toplevel` 页面上的“外部方言”列表。

.. tab:: 英文

    In addition to the above DBAPI layers with native SQLAlchemy support, there are third-party dialects for other DBAPI layers that are compatible with SQL Server. See the "External Dialects" list on the :ref:`dialect_toplevel` page.

.. _mssql_identity:

自动增量行为 / IDENTITY 列
------------------------------------------

Auto Increment Behavior / IDENTITY Columns

.. tab:: 中文

    SQL Server 使用 ``IDENTITY`` 构造提供所谓的“自增”功能，可用于表中的任意单个整数列。
    SQLAlchemy 将 ``IDENTITY`` 视为默认整数主键列的 “autoincrement” 行为的一部分，详见 :paramref:`_schema.Column.autoincrement`。
    这意味着，默认情况下，:class:`_schema.Table` 中的第一个整数主键列将被视为标识列（除非它绑定了一个 :class:`.Sequence`），并将生成如下 DDL::

        from sqlalchemy import Table, MetaData, Column, Integer

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True),
            Column("x", Integer),
        )
        m.create_all(engine)

    上述示例将生成如下 DDL：

    .. sourcecode:: sql

        CREATE TABLE t (
            id INTEGER NOT NULL IDENTITY,
            x INTEGER NULL,
            PRIMARY KEY (id)
        )

    如果不希望默认生成 ``IDENTITY``，可在首个整数主键列上将 :paramref:`_schema.Column.autoincrement` 显式设置为 ``False``::

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("x", Integer),
        )
        m.create_all(engine)

    要将 ``IDENTITY`` 用于非主键列，可在目标 :class:`_schema.Column` 上设置 ``autoincrement=True``，同时确保任何整数主键列的 ``autoincrement`` 设置为 ``False``::

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("x", Integer, autoincrement=True),
        )
        m.create_all(engine)

    .. versionchanged:: 1.4
       在 :class:`_schema.Column` 中新增 :class:`_schema.Identity` 构造，以指定 IDENTITY 的起始值与增量值。此方式取代使用 :class:`.Sequence` 来设置相关参数。

    .. deprecated:: 1.4

       传递给 :class:`_schema.Column` 的 ``mssql_identity_start`` 与 ``mssql_identity_increment`` 参数已弃用，应使用 :class:`_schema.Identity` 对象替代。
       若同时指定两种配置方式将导致编译错误。
       此外，这两个参数也不再出现在 :meth:`_reflection.Inspector.get_columns` 方法返回结果中的 ``dialect_options`` 字段下，应使用 ``identity`` 字段获取相关信息。

    .. versionchanged:: 1.4
       移除了通过 :class:`.Sequence` 对象修改 IDENTITY 特性的能力。:class:`.Sequence` 现在仅用于操作真正的 T-SQL `SEQUENCE` 类型。

    .. note::

        每个表只能存在一个 IDENTITY 列。当通过 ``autoincrement=True`` 启用 IDENTITY 关键字时，SQLAlchemy 不会限制多个列同时指定该选项的行为。
        数据库自身将在执行 ``CREATE TABLE`` 时拒绝这种定义。

    .. note::

        若向标有 IDENTITY 的列插入值，SQL Server 将拒绝该 INSERT 语句。
        若要允许插入值，必须启用会话级的 "SET IDENTITY_INSERT" 选项。
        SQLAlchemy 的 SQL Server 方言在使用核心层的 :class:`_expression.Insert` 构造时会自动启用该选项；
        若执行时明确为 IDENTITY 列提供值，则将在语句执行期间启用 "IDENTITY_INSERT"。
        不过，这种方式性能较低，不应作为常规方案使用。
        若表中的整数主键列并不需要 IDENTITY 行为，应在建表时设置 ``autoincrement=False`` 来禁用该关键字。

.. tab:: 英文

    SQL Server provides so-called "auto incrementing" behavior using the
    ``IDENTITY`` construct, which can be placed on any single integer column in a
    table. SQLAlchemy considers ``IDENTITY`` within its default "autoincrement"
    behavior for an integer primary key column, described at
    :paramref:`_schema.Column.autoincrement`.  This means that by default,
    the first integer primary key column in a :class:`_schema.Table` will be
    considered to be the identity column - unless it is associated with a
    :class:`.Sequence` - and will generate DDL as such::

        from sqlalchemy import Table, MetaData, Column, Integer

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True),
            Column("x", Integer),
        )
        m.create_all(engine)

    The above example will generate DDL as:

    .. sourcecode:: sql

        CREATE TABLE t (
            id INTEGER NOT NULL IDENTITY,
            x INTEGER NULL,
            PRIMARY KEY (id)
        )

    For the case where this default generation of ``IDENTITY`` is not desired,
    specify ``False`` for the :paramref:`_schema.Column.autoincrement` flag,
    on the first integer primary key column::

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("x", Integer),
        )
        m.create_all(engine)

    To add the ``IDENTITY`` keyword to a non-primary key column, specify
    ``True`` for the :paramref:`_schema.Column.autoincrement` flag on the desired
    :class:`_schema.Column` object, and ensure that
    :paramref:`_schema.Column.autoincrement`
    is set to ``False`` on any integer primary key column::

        m = MetaData()
        t = Table(
            "t",
            m,
            Column("id", Integer, primary_key=True, autoincrement=False),
            Column("x", Integer, autoincrement=True),
        )
        m.create_all(engine)

    .. versionchanged::  1.4   Added :class:`_schema.Identity` construct
       in a :class:`_schema.Column` to specify the start and increment
       parameters of an IDENTITY. These replace
       the use of the :class:`.Sequence` object in order to specify these values.

    .. deprecated:: 1.4

       The ``mssql_identity_start`` and ``mssql_identity_increment`` parameters
       to :class:`_schema.Column` are deprecated and should we replaced by
       an :class:`_schema.Identity` object. Specifying both ways of configuring
       an IDENTITY will result in a compile error.
       These options are also no longer returned as part of the
       ``dialect_options`` key in :meth:`_reflection.Inspector.get_columns`.
       Use the information in the ``identity`` key instead.

    .. versionchanged::  1.4   Removed the ability to use a :class:`.Sequence`
       object to modify IDENTITY characteristics. :class:`.Sequence` objects
       now only manipulate true T-SQL SEQUENCE types.

    .. note::

        There can only be one IDENTITY column on the table.  When using
        ``autoincrement=True`` to enable the IDENTITY keyword, SQLAlchemy does not
        guard against multiple columns specifying the option simultaneously.  The
        SQL Server database will instead reject the ``CREATE TABLE`` statement.

    .. note::

        An INSERT statement which attempts to provide a value for a column that is
        marked with IDENTITY will be rejected by SQL Server.   In order for the
        value to be accepted, a session-level option "SET IDENTITY_INSERT" must be
        enabled.   The SQLAlchemy SQL Server dialect will perform this operation
        automatically when using a core :class:`_expression.Insert`
        construct; if the
        execution specifies a value for the IDENTITY column, the "IDENTITY_INSERT"
        option will be enabled for the span of that statement's invocation.However,
        this scenario is not high performing and should not be relied upon for
        normal use.   If a table doesn't actually require IDENTITY behavior in its
        integer primary key column, the keyword should be disabled when creating
        the table by ensuring that ``autoincrement=False`` is set.

控制“起始”和“增量”
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Controlling "Start" and "Increment"

.. tab:: 中文

    要精确控制 ``IDENTITY`` 的起始值与增量值，可将 :class:`_schema.Identity` 传入 :class:`_schema.Column`，并使用其 :paramref:`_schema.Identity.start` 和 :paramref:`_schema.Identity.increment` 参数::

        from sqlalchemy import Table, Integer, Column, Identity

        test = Table(
            "test",
            metadata,
            Column(
                "id", Integer, primary_key=True, Identity(start=100, increment=10)
            ),
            Column("name", String(20)),
        )

    上述 :class:`_schema.Table` 对象将生成如下 CREATE TABLE 语句：

    .. sourcecode:: sql

       CREATE TABLE test (
         id INTEGER NOT NULL IDENTITY(100,10) PRIMARY KEY,
         name VARCHAR(20) NULL,
       )

    .. note::

       :class:`_schema.Identity` 对象除了 ``start`` 与 ``increment`` 外，还支持多个其他参数。
       然而 SQL Server 并不支持这些额外参数，因此它们在生成 DDL 时将被忽略。

.. tab:: 英文

    Specific control over the "start" and "increment" values for
    the ``IDENTITY`` generator are provided using the
    :paramref:`_schema.Identity.start` and :paramref:`_schema.Identity.increment`
    parameters passed to the :class:`_schema.Identity` object::

        from sqlalchemy import Table, Integer, Column, Identity

        test = Table(
            "test",
            metadata,
            Column(
                "id", Integer, primary_key=True, Identity(start=100, increment=10)
            ),
            Column("name", String(20)),
        )

    The CREATE TABLE for the above :class:`_schema.Table` object would be:

    .. sourcecode:: sql

    CREATE TABLE test (
        id INTEGER NOT NULL IDENTITY(100,10) PRIMARY KEY,
        name VARCHAR(20) NULL,
    )

    .. note::

        The :class:`_schema.Identity` object supports many other parameter in
        addition to ``start`` and ``increment``. These are not supported by
        SQL Server and will be ignored when generating the CREATE TABLE ddl.


将 IDENTITY 与非整数数值类型结合使用
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using IDENTITY with Non-Integer numeric types

.. tab:: 中文

    SQL Server 还允许在 ``NUMERIC`` 列上使用 ``IDENTITY``。
    为在 SQLAlchemy 中顺利实现此模式，建议列的主类型仍为 ``Integer``，但可通过 :meth:`.TypeEngine.with_variant` 方法将其在底层数据库中具体实现为 ``Numeric``::

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import Numeric
        from sqlalchemy import String
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base()


        class TestTable(Base):
            __tablename__ = "test"
            id = Column(
                Integer().with_variant(Numeric(10, 0), "mssql"),
                primary_key=True,
                autoincrement=True,
            )
            name = Column(String)

    在上述示例中，使用 ``Integer().with_variant()`` 明确表达了意图。
    关于 ``autoincrement`` 仅适用于 ``Integer`` 类型的限制，是在元数据层面定义的，而非每个方言各自决定的。

    采用上述模式时，插入行所返回的主键标识符（即赋值给 ORM 实例，如上例中的 ``TestTable`` 的 `id`）将是 ``Decimal()`` 实例，而不是 ``int``，因为 SQL Server 返回的数值类型是 ``Numeric``。
    若希望该返回类型为浮点数，可向 :paramref:`_types.Numeric.asdecimal` 传入 ``False``。
    若希望将 ``Numeric(10, 0)`` 类型的值归一化为 Python 的整数类型（在 Python 3 中也支持任意精度长整型），可使用 :class:`_types.TypeDecorator` 进行如下封装::

        from sqlalchemy import TypeDecorator


        class NumericAsInteger(TypeDecorator):
            "将浮点返回值规范化为整数"

            impl = Numeric(10, 0, asdecimal=False)
            cache_ok = True

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = int(value)
                return value


        class TestTable(Base):
            __tablename__ = "test"
            id = Column(
                Integer().with_variant(NumericAsInteger, "mssql"),
                primary_key=True,
                autoincrement=True,
            )
            name = Column(String)

.. tab:: 英文

    SQL Server also allows ``IDENTITY`` to be used with ``NUMERIC`` columns.  To
    implement this pattern smoothly in SQLAlchemy, the primary datatype of the
    column should remain as ``Integer``, however the underlying implementation
    type deployed to the SQL Server database can be specified as ``Numeric`` using
    :meth:`.TypeEngine.with_variant`::

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import Numeric
        from sqlalchemy import String
        from sqlalchemy.ext.declarative import declarative_base

        Base = declarative_base()


        class TestTable(Base):
            __tablename__ = "test"
            id = Column(
                Integer().with_variant(Numeric(10, 0), "mssql"),
                primary_key=True,
                autoincrement=True,
            )
            name = Column(String)

    In the above example, ``Integer().with_variant()`` provides clear usage
    information that accurately describes the intent of the code. The general
    restriction that ``autoincrement`` only applies to ``Integer`` is established
    at the metadata level and not at the per-dialect level.

    When using the above pattern, the primary key identifier that comes back from
    the insertion of a row, which is also the value that would be assigned to an
    ORM object such as ``TestTable`` above, will be an instance of ``Decimal()``
    and not ``int`` when using SQL Server. The numeric return type of the
    :class:`_types.Numeric` type can be changed to return floats by passing False
    to :paramref:`_types.Numeric.asdecimal`. To normalize the return type of the
    above ``Numeric(10, 0)`` to return Python ints (which also support "long"
    integer values in Python 3), use :class:`_types.TypeDecorator` as follows::

        from sqlalchemy import TypeDecorator


        class NumericAsInteger(TypeDecorator):
            "normalize floating point return values into ints"

            impl = Numeric(10, 0, asdecimal=False)
            cache_ok = True

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = int(value)
                return value


        class TestTable(Base):
            __tablename__ = "test"
            id = Column(
                Integer().with_variant(NumericAsInteger, "mssql"),
                primary_key=True,
                autoincrement=True,
            )
            name = Column(String)

.. _mssql_insert_behavior:

INSERT 行为
^^^^^^^^^^^^^^^^

INSERT behavior

.. tab:: 中文

    处理 ``IDENTITY`` 列的插入时间涉及两种关键技术。最常见的做法是能够获取给定 ``IDENTITY`` 列的“最后插入值”，这个过程在许多情况下由 SQLAlchemy 隐式执行，最重要的是在 ORM 中。

    获取此值的过程有几种变体：

    * 在绝大多数情况下，SQL Server 中的 INSERT 语句会与 RETURNING 一起使用，以获取新生成的主键值：

      .. sourcecode:: sql

        INSERT INTO t (x) OUTPUT inserted.id VALUES (?)

      从 SQLAlchemy 2.0 开始，默认情况下也会使用 :ref:`engine_insertmanyvalues` 特性来优化多行 INSERT 语句；对于 SQL Server，这个特性会作用于带有 RETURNING 和不带 RETURNING 的 INSERT 语句。

      .. versionchanged:: 2.0.10
         由于行排序问题，SQLAlchemy 2.0.9 暂时禁用了 SQL Server 的 :ref:`engine_insertmanyvalues` 特性。 从 2.0.10 开始，该特性已重新启用，并针对事务单元要求的 RETURNING 排序进行了特殊处理。

    * 当 RETURNING 不可用或通过 ``implicit_returning=False`` 被禁用时，将使用 ``scope_identity()`` 函数或 ``@@identity`` 变量；行为依据后端不同而有所不同：

      * 在使用 PyODBC 时，会在 INSERT 语句的末尾附加 ``; select scope_identity()``；会获取第二个结果集以接收值。给定如下表：

        t = Table(
            "t",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("x", Integer),
            implicit_returning=False,
        )

        一个 INSERT 语句将如下所示：

        .. sourcecode:: sql

            INSERT INTO t (x) VALUES (?); select scope_identity()

      * 其他方言如 pymssql 会在 INSERT 语句之后调用 ``SELECT scope_identity() AS lastrowid``。如果将 ``use_scope_identity=False`` 传递给 :func:`_sa.create_engine`，则会使用 ``SELECT @@identity AS lastrowid`` 代替。

    包含 ``IDENTITY`` 列的表将禁止显式引用身份列的 INSERT 语句。SQLAlchemy 方言会检测到当通过核心 :func:`_expression.insert` 构造（而非普通字符串 SQL）创建的 INSERT 构造中引用了身份列，并在这种情况下会在执行插入语句前发出 ``SET IDENTITY_INSERT ON``，执行后发出 ``SET IDENTITY_INSERT OFF``。给定如下示例：

        m = MetaData()
        t = Table(
            "t", m, Column("id", Integer, primary_key=True), Column("x", Integer)
        )
        m.create_all(engine)

        with engine.begin() as conn:
            conn.execute(t.insert(), {"id": 1, "x": 1}, {"id": 2, "x": 2})

    上述列将以 IDENTITY 创建，但我们发出的 INSERT 语句指定了显式值。在回显输出中我们可以看到 SQLAlchemy 如何处理：

    .. sourcecode:: sql

        CREATE TABLE t (
            id INTEGER NOT NULL IDENTITY(1,1),
            x INTEGER NULL,
            PRIMARY KEY (id)
        )

        COMMIT
        SET IDENTITY_INSERT t ON
        INSERT INTO t (id, x) VALUES (?, ?)
        ((1, 1), (2, 2))
        SET IDENTITY_INSERT t OFF
        COMMIT

    这是一个适用于测试和批量插入场景的辅助用例。

.. tab:: 英文

    Handling of the ``IDENTITY`` column at INSERT time involves two key
    techniques. The most common is being able to fetch the "last inserted value"
    for a given ``IDENTITY`` column, a process which SQLAlchemy performs
    implicitly in many cases, most importantly within the ORM.

    The process for fetching this value has several variants:

    * In the vast majority of cases, RETURNING is used in conjunction with INSERT
      statements on SQL Server in order to get newly generated primary key values:

      .. sourcecode:: sql

        INSERT INTO t (x) OUTPUT inserted.id VALUES (?)

      As of SQLAlchemy 2.0, the :ref:`engine_insertmanyvalues` feature is also
      used by default to optimize many-row INSERT statements; for SQL Server
      the feature takes place for both RETURNING and-non RETURNING
      INSERT statements.

      .. versionchanged:: 2.0.10 The :ref:`engine_insertmanyvalues` feature for
         SQL Server was temporarily disabled for SQLAlchemy version 2.0.9 due to
         issues with row ordering. As of 2.0.10 the feature is re-enabled, with
         special case handling for the unit of work's requirement for RETURNING to
         be ordered.

    * When RETURNING is not available or has been disabled via
      ``implicit_returning=False``, either the ``scope_identity()`` function or
      the ``@@identity`` variable is used; behavior varies by backend:

      * when using PyODBC, the phrase ``; select scope_identity()`` will be
        appended to the end of the INSERT statement; a second result set will be
        fetched in order to receive the value.  Given a table as::

            t = Table(
                "t",
                metadata,
                Column("id", Integer, primary_key=True),
                Column("x", Integer),
                implicit_returning=False,
            )

        an INSERT will look like:

        .. sourcecode:: sql

            INSERT INTO t (x) VALUES (?); select scope_identity()

      * Other dialects such as pymssql will call upon
        ``SELECT scope_identity() AS lastrowid`` subsequent to an INSERT
        statement. If the flag ``use_scope_identity=False`` is passed to
        :func:`_sa.create_engine`,
        the statement ``SELECT @@identity AS lastrowid``
        is used instead.

    A table that contains an ``IDENTITY`` column will prohibit an INSERT statement
    that refers to the identity column explicitly.  The SQLAlchemy dialect will
    detect when an INSERT construct, created using a core
    :func:`_expression.insert`
    construct (not a plain string SQL), refers to the identity column, and
    in this case will emit ``SET IDENTITY_INSERT ON`` prior to the insert
    statement proceeding, and ``SET IDENTITY_INSERT OFF`` subsequent to the
    execution.  Given this example::

        m = MetaData()
        t = Table(
            "t", m, Column("id", Integer, primary_key=True), Column("x", Integer)
        )
        m.create_all(engine)

        with engine.begin() as conn:
            conn.execute(t.insert(), {"id": 1, "x": 1}, {"id": 2, "x": 2})

    The above column will be created with IDENTITY, however the INSERT statement
    we emit is specifying explicit values.  In the echo output we can see
    how SQLAlchemy handles this:

    .. sourcecode:: sql

        CREATE TABLE t (
            id INTEGER NOT NULL IDENTITY(1,1),
            x INTEGER NULL,
            PRIMARY KEY (id)
        )

        COMMIT
        SET IDENTITY_INSERT t ON
        INSERT INTO t (id, x) VALUES (?, ?)
        ((1, 1), (2, 2))
        SET IDENTITY_INSERT t OFF
        COMMIT



    This is an auxiliary use case suitable for testing and bulk insert scenarios.

SEQUENCE 支持
----------------

SEQUENCE support

.. tab:: 中文

    :class:`.Sequence` 对象创建“真实”序列，即 ``CREATE SEQUENCE``：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import Sequence
        >>> from sqlalchemy.schema import CreateSequence
        >>> from sqlalchemy.dialects import mssql
        >>> print(
        ...     CreateSequence(Sequence("my_seq", start=1)).compile(
        ...         dialect=mssql.dialect()
        ...     )
        ... )
        {printsql}CREATE SEQUENCE my_seq START WITH 1

    对于整数主键生成，SQL Server 的 ``IDENTITY`` 构造通常应优先于序列。

    .. tip::

        T-SQL 的默认起始值是 ``-2**63``，而不是大多数其他 SQL 数据库中的 1。用户应显式将 :paramref:`.Sequence.start` 设置为 1（如果这是期望的默认值）：

            seq = Sequence("my_sequence", start=1)

    .. versionadded:: 1.4 添加了 SQL Server 对 :class:`.Sequence` 的支持

    .. versionchanged:: 2.0
        SQL Server 方言将不再隐式渲染 ``CREATE SEQUENCE`` 中的 "START WITH 1"，这在 1.4 版本中首次实现。

.. tab:: 英文

    The :class:`.Sequence` object creates "real" sequences, i.e.,
    ``CREATE SEQUENCE``:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import Sequence
        >>> from sqlalchemy.schema import CreateSequence
        >>> from sqlalchemy.dialects import mssql
        >>> print(
        ...     CreateSequence(Sequence("my_seq", start=1)).compile(
        ...         dialect=mssql.dialect()
        ...     )
        ... )
        {printsql}CREATE SEQUENCE my_seq START WITH 1

    For integer primary key generation, SQL Server's ``IDENTITY`` construct should
    generally be preferred vs. sequence.

    .. tip::

        The default start value for T-SQL is ``-2**63`` instead of 1 as
        in most other SQL databases. Users should explicitly set the
        :paramref:`.Sequence.start` to 1 if that's the expected default::

            seq = Sequence("my_sequence", start=1)

    .. versionadded:: 1.4 added SQL Server support for :class:`.Sequence`

    .. versionchanged:: 2.0 The SQL Server dialect will no longer implicitly
       render "START WITH 1" for ``CREATE SEQUENCE``, which was the behavior
       first implemented in version 1.4.

VARCHAR / NVARCHAR 上的 MAX
-------------------------

MAX on VARCHAR / NVARCHAR

.. tab:: 中文

    SQL Server 支持在 :class:`_types.VARCHAR` 和 :class:`_types.NVARCHAR` 数据类型中使用特殊字符串 "MAX" 来表示“最大长度”。该方言目前将其作为基本类型中的 "None" 长度处理，而不是提供这些类型的方言特定版本，这样指定如 ``VARCHAR(None)`` 的基本类型可以在多个后端上假设为“无长度”行为，而不使用特定方言的类型。

    要构建一个 SQL Server VARCHAR 或 NVARCHAR 最大长度的列，可以使用 None：

        my_table = Table(
            "my_table",
            metadata,
            Column("my_data", VARCHAR(None)),
            Column("my_n_data", NVARCHAR(None)),
        )

.. tab:: 英文

    SQL Server supports the special string "MAX" within the
    :class:`_types.VARCHAR` and :class:`_types.NVARCHAR` datatypes,
    to indicate "maximum length possible".   The dialect currently handles this as
    a length of "None" in the base type, rather than supplying a
    dialect-specific version of these types, so that a base type
    specified such as ``VARCHAR(None)`` can assume "unlengthed" behavior on
    more than one backend without using dialect-specific types.

    To build a SQL Server VARCHAR or NVARCHAR with MAX length, use None::

        my_table = Table(
            "my_table",
            metadata,
            Column("my_data", VARCHAR(None)),
            Column("my_n_data", NVARCHAR(None)),
        )

排序规则支持
-----------------

Collation Support

.. tab:: 中文

    字符排序规则由基本字符串类型支持，通过字符串参数 "collation" 指定：

        from sqlalchemy import VARCHAR

        Column("login", VARCHAR(32, collation="Latin1_General_CI_AS"))

    当这样的列与 :class:`_schema.Table` 关联时，生成的 CREATE TABLE 语句将如下所示：

    .. sourcecode:: sql

        login VARCHAR(32) COLLATE Latin1_General_CI_AS NULL

.. tab:: 英文

    Character collations are supported by the base string types,
    specified by the string argument "collation"::

        from sqlalchemy import VARCHAR

        Column("login", VARCHAR(32, collation="Latin1_General_CI_AS"))

    When such a column is associated with a :class:`_schema.Table`, the
    CREATE TABLE statement for this column will yield:

    .. sourcecode:: sql

        login VARCHAR(32) COLLATE Latin1_General_CI_AS NULL

LIMIT/OFFSET 支持
--------------------

LIMIT/OFFSET Support

.. tab:: 中文

    自 SQL Server 2012 起，MSSQL 支持通过 "OFFSET n ROWS" 和 "FETCH NEXT n ROWS" 子句添加了对 LIMIT / OFFSET 的支持。如果检测到 SQL Server 2012 或更高版本，SQLAlchemy 会自动支持这些语法。

    .. versionchanged:: 1.4
       添加了对 SQL Server "OFFSET n ROWS" 和 "FETCH NEXT n ROWS" 语法的支持。

    对于只指定 LIMIT 而没有 OFFSET 的语句，所有版本的 SQL Server 都支持 TOP 关键字。此语法在没有 OFFSET 子句的情况下用于所有 SQL Server 版本。像如下的语句：

        select(some_table).limit(5)

    将会转换为类似以下的 SQL：

    .. sourcecode:: sql

        SELECT TOP 5 col1, col2.. FROM table

    对于 SQL Server 2012 之前的版本，使用 LIMIT 和 OFFSET，或者仅使用 OFFSET 的语句将会通过 ``ROW_NUMBER()`` 窗口函数进行转换。像如下的语句：

        select(some_table).order_by(some_table.c.col3).limit(5).offset(10)

    将会转换为类似以下的 SQL：

    .. sourcecode:: sql

        SELECT anon_1.col1, anon_1.col2 FROM (SELECT col1, col2,
        ROW_NUMBER() OVER (ORDER BY col3) AS
        mssql_rn FROM table WHERE t.x = :x_1) AS
        anon_1 WHERE mssql_rn > :param_1 AND mssql_rn <= :param_2 + :param_1

    请注意，在使用 LIMIT 和/或 OFFSET 时，无论使用旧的还是新的 SQL Server 语法，语句都必须包含 ORDER BY，否则将抛出 :class:`.CompileError`。

.. tab:: 英文

    MSSQL has added support for LIMIT / OFFSET as of SQL Server 2012, via the
    "OFFSET n ROWS" and "FETCH NEXT n ROWS" clauses.  SQLAlchemy supports these
    syntaxes automatically if SQL Server 2012 or greater is detected.

    .. versionchanged:: 1.4 support added for SQL Server "OFFSET n ROWS" and
        "FETCH NEXT n ROWS" syntax.

    For statements that specify only LIMIT and no OFFSET, all versions of SQL
    Server support the TOP keyword.   This syntax is used for all SQL Server
    versions when no OFFSET clause is present.  A statement such as::

        select(some_table).limit(5)

    will render similarly to:

    .. sourcecode:: sql

        SELECT TOP 5 col1, col2.. FROM table

    For versions of SQL Server prior to SQL Server 2012, a statement that uses
    LIMIT and OFFSET, or just OFFSET alone, will be rendered using the
    ``ROW_NUMBER()`` window function.   A statement such as::

        select(some_table).order_by(some_table.c.col3).limit(5).offset(10)

    will render similarly to:

    .. sourcecode:: sql

        SELECT anon_1.col1, anon_1.col2 FROM (SELECT col1, col2,
        ROW_NUMBER() OVER (ORDER BY col3) AS
        mssql_rn FROM table WHERE t.x = :x_1) AS
        anon_1 WHERE mssql_rn > :param_1 AND mssql_rn <= :param_2 + :param_1

    Note that when using LIMIT and/or OFFSET, whether using the older
    or newer SQL Server syntaxes, the statement must have an ORDER BY as well,
    else a :class:`.CompileError` is raised.

.. _mssql_comment_support:

DDL 注释支持
--------------------

DDL Comment Support

.. tab:: 中文

    评论支持，包括对 :paramref:`_schema.Table.comment` 和 :paramref:`_schema.Column.comment` 等属性的 DDL 渲染，以及反射这些注释的功能，在使用支持的 SQL Server 版本时得到支持。如果首次连接时检测到不支持的版本（如 Azure Synapse），通过检查 ``fn_listextendedproperty`` SQL 函数的存在，则会禁用评论支持，包括渲染和表注释反射，因为这两个功能依赖于 SQL Server 存储过程和函数，而这些在并非所有后端类型中可用。

    要强制开启或关闭评论支持，可以绕过自动检测，在 :func:`_sa.create_engine` 中设置 ``supports_comments`` 参数：

        e = create_engine("mssql+pyodbc://u:p@dsn", supports_comments=False)

    .. versionadded:: 2.0
       为 SQL Server 方言添加了对表和列注释的支持，包括 DDL 生成和反射。

.. tab:: 英文

    Comment support, which includes DDL rendering for attributes such as
    :paramref:`_schema.Table.comment` and :paramref:`_schema.Column.comment`, as
    well as the ability to reflect these comments, is supported assuming a
    supported version of SQL Server is in use. If a non-supported version such as
    Azure Synapse is detected at first-connect time (based on the presence
    of the ``fn_listextendedproperty`` SQL function), comment support including
    rendering and table-comment reflection is disabled, as both features rely upon
    SQL Server stored procedures and functions that are not available on all
    backend types.

    To force comment support to be on or off, bypassing autodetection, set the
    parameter ``supports_comments`` within :func:`_sa.create_engine`::

        e = create_engine("mssql+pyodbc://u:p@dsn", supports_comments=False)

    .. versionadded:: 2.0 Added support for table and column comments for
        the SQL Server dialect, including DDL generation and reflection.

.. _mssql_isolation_level:

事务隔离级别
---------------------------

Transaction Isolation Level

.. tab:: 中文

    所有 SQL Server 方言都支持通过方言特定的参数 :paramref:`_sa.create_engine.isolation_level` 来设置事务隔离级别，该参数由 :func:`_sa.create_engine` 接受，以及传递给 :meth:`_engine.Connection.execution_options` 的 :paramref:`.Connection.execution_options.isolation_level` 参数。此功能通过为每个新连接发出 ``SET TRANSACTION ISOLATION LEVEL <level>`` 命令来工作。

    使用 :func:`_sa.create_engine` 设置隔离级别：

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@ms_2008", isolation_level="REPEATABLE READ"
        )

    使用每连接执行选项设置：

        connection = engine.connect()
        connection = connection.execution_options(isolation_level="READ COMMITTED")

    ``isolation_level`` 的有效值包括：

    * ``AUTOCOMMIT`` - pyodbc / pymssql 特有
    * ``READ COMMITTED``
    * ``READ UNCOMMITTED``
    * ``REPEATABLE READ``
    * ``SERIALIZABLE``
    * ``SNAPSHOT`` - SQL Server 特有

    隔离级别配置还有更多选项，例如链接到主 :class:`_engine.Engine` 的“子引擎”对象，每个对象应用不同的隔离级别设置。有关背景信息，请参见 :ref:`dbapi_autocommit`。

    .. seealso::

        :ref:`dbapi_autocommit`

.. tab:: 英文

    All SQL Server dialects support setting of transaction isolation level
    both via a dialect-specific parameter
    :paramref:`_sa.create_engine.isolation_level`
    accepted by :func:`_sa.create_engine`,
    as well as the :paramref:`.Connection.execution_options.isolation_level`
    argument as passed to
    :meth:`_engine.Connection.execution_options`.
    This feature works by issuing the
    command ``SET TRANSACTION ISOLATION LEVEL <level>`` for
    each new connection.

    To set isolation level using :func:`_sa.create_engine`::

        engine = create_engine(
            "mssql+pyodbc://scott:tiger@ms_2008", isolation_level="REPEATABLE READ"
        )

    To set using per-connection execution options::

        connection = engine.connect()
        connection = connection.execution_options(isolation_level="READ COMMITTED")

    Valid values for ``isolation_level`` include:

    * ``AUTOCOMMIT`` - pyodbc / pymssql-specific
    * ``READ COMMITTED``
    * ``READ UNCOMMITTED``
    * ``REPEATABLE READ``
    * ``SERIALIZABLE``
    * ``SNAPSHOT`` - specific to SQL Server

    There are also more options for isolation level configurations, such as
    "sub-engine" objects linked to a main :class:`_engine.Engine` which each apply
    different isolation level settings.  See the discussion at
    :ref:`dbapi_autocommit` for background.

    .. seealso::

        :ref:`dbapi_autocommit`

.. _mssql_reset_on_return:

连接池的临时表/资源重置
-------------------------------------------------------

Temporary Table / Resource Reset for Connection Pooling

.. tab:: 中文

    SQLAlchemy :class:`.Engine` 对象使用的 :class:`.QueuePool` 连接池实现包括 :ref:`reset on return <pool_reset_on_return>` 行为，当连接返回到连接池时，会调用 DBAPI 的 ``.rollback()`` 方法。虽然此回滚将清除上一个事务使用的即时状态，但它并不涵盖会话级别的更广泛状态，包括临时表以及其他服务器状态，如预处理语句句柄和语句缓存。已知 SQL Server 有一个未记录的存储过程 ``sp_reset_connection``，它是解决此问题的一个变通方法，可以重置连接上的大部分会话状态，包括临时表。

    要将 ``sp_reset_connection`` 安装为执行 reset-on-return 的方法，可以使用 :meth:`.PoolEvents.reset` 事件钩子，如下例所示。通过将 :paramref:`_sa.create_engine.pool_reset_on_return` 参数设置为 ``None``，以便自定义方案可以完全替代默认行为。自定义钩子实现会在任何情况下调用 ``.rollback()``，因为通常需要确保 DBAPI 自身的提交/回滚跟踪与事务的状态保持一致：

        from sqlalchemy import create_engine
        from sqlalchemy import event

        mssql_engine = create_engine(
            "mssql+pyodbc://scott:tiger^5HHH@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            # 禁用默认的 reset-on-return 方案
            pool_reset_on_return=None,
        )


        @event.listens_for(mssql_engine, "reset")
        def _reset_mssql(dbapi_connection, connection_record, reset_state):
            if not reset_state.terminate_only:
                dbapi_connection.execute("{call sys.sp_reset_connection}")

            # 以便 DBAPI 本身知道连接已被重置
            dbapi_connection.rollback()

    .. versionchanged:: 2.0.0b3
       为 :meth:`.PoolEvents.reset` 事件添加了额外的状态参数，并确保在所有“重置”发生时调用该事件，以便它适合作为自定义“重置”处理程序的地方。以前使用 :meth:`.PoolEvents.checkin` 处理程序的方案仍然可用。

    .. seealso::

        :ref:`pool_reset_on_return` - 参见 :ref:`pooling_toplevel` 文档

.. tab:: 英文

    The :class:`.QueuePool` connection pool implementation used
    by the SQLAlchemy :class:`.Engine` object includes
    :ref:`reset on return <pool_reset_on_return>` behavior that will invoke
    the DBAPI ``.rollback()`` method when connections are returned to the pool.
    While this rollback will clear out the immediate state used by the previous
    transaction, it does not cover a wider range of session-level state, including
    temporary tables as well as other server state such as prepared statement
    handles and statement caches.   An undocumented SQL Server procedure known
    as ``sp_reset_connection`` is known to be a workaround for this issue which
    will reset most of the session state that builds up on a connection, including
    temporary tables.

    To install ``sp_reset_connection`` as the means of performing reset-on-return,
    the :meth:`.PoolEvents.reset` event hook may be used, as demonstrated in the
    example below. The :paramref:`_sa.create_engine.pool_reset_on_return` parameter
    is set to ``None`` so that the custom scheme can replace the default behavior
    completely.   The custom hook implementation calls ``.rollback()`` in any case,
    as it's usually important that the DBAPI's own tracking of commit/rollback
    will remain consistent with the state of the transaction::

        from sqlalchemy import create_engine
        from sqlalchemy import event

        mssql_engine = create_engine(
            "mssql+pyodbc://scott:tiger^5HHH@mssql2017:1433/test?driver=ODBC+Driver+17+for+SQL+Server",
            # disable default reset-on-return scheme
            pool_reset_on_return=None,
        )


        @event.listens_for(mssql_engine, "reset")
        def _reset_mssql(dbapi_connection, connection_record, reset_state):
            if not reset_state.terminate_only:
                dbapi_connection.execute("{call sys.sp_reset_connection}")

            # so that the DBAPI itself knows that the connection has been
            # reset
            dbapi_connection.rollback()

    .. versionchanged:: 2.0.0b3  Added additional state arguments to
       the :meth:`.PoolEvents.reset` event and additionally ensured the event
       is invoked for all "reset" occurrences, so that it's appropriate
       as a place for custom "reset" handlers.   Previous schemes which
       use the :meth:`.PoolEvents.checkin` handler remain usable as well.

    .. seealso::

        :ref:`pool_reset_on_return` - in the :ref:`pooling_toplevel` documentation

可空性
-----------

Nullability

.. tab:: 中文

    MSSQL 支持三种列的空值可用性级别。默认的空值可用性允许空值，并在 CREATE TABLE 语句中明确指定：

    .. sourcecode:: sql

        name VARCHAR(20) NULL

    如果指定 ``nullable=None``，则不做任何指定。换句话说，使用数据库配置的默认值。这将会渲染为：

    .. sourcecode:: sql

        name VARCHAR(20)

    如果 ``nullable`` 为 ``True`` 或 ``False``，则列将分别为 ``NULL`` 或 ``NOT NULL``。

.. tab:: 英文

    MSSQL has support for three levels of column nullability. The default
    nullability allows nulls and is explicit in the CREATE TABLE
    construct:

    .. sourcecode:: sql

        name VARCHAR(20) NULL

    If ``nullable=None`` is specified then no specification is made. In
    other words the database's configured default is used. This will
    render:

    .. sourcecode:: sql

        name VARCHAR(20)

    If ``nullable`` is ``True`` or ``False`` then the column will be
    ``NULL`` or ``NOT NULL`` respectively.

日期/时间处理
--------------------

Date / Time Handling

.. tab:: 中文

    DATE 和 TIME 类型是支持的。绑定参数将根据大多数 MSSQL 驱动程序的要求转换为 `datetime.datetime()` 对象，并且如果需要，结果将从字符串中进行处理。对于 SQL Server 2005 及之前的版本，DATE 和 TIME 类型不可用。如果检测到 2008 以下的服务器版本，这些类型的 DDL 将会作为 DATETIME 类型发出。

.. tab:: 英文

    DATE and TIME are supported.   Bind parameters are converted
    to datetime.datetime() objects as required by most MSSQL drivers,
    and results are processed from strings if needed.
    The DATE and TIME types are not available for MSSQL 2005 and
    previous - if a server version below 2008 is detected, DDL
    for these types will be issued as DATETIME.

.. _mssql_large_type_deprecation:

大型文本/二进制类型弃用
----------------------------------

Large Text/Binary Type Deprecation

.. tab:: 中文

    根据 `SQL Server 2012/2014 文档 <https://technet.microsoft.com/en-us/library/ms187993.aspx>`_，``NTEXT``、``TEXT`` 和 ``IMAGE`` 数据类型将在未来的 SQL Server 版本中被移除。SQLAlchemy 通常将这些类型与 :class:`.UnicodeText`、:class:`_expression.TextClause` 和 :class:`.LargeBinary` 数据类型相关联。

    为了适应这一变化，方言中新增了一个标志 ``deprecate_large_types``，该标志将在首次连接时自动根据使用的服务器版本进行设置，除非用户另行设置。该标志的行为如下：

    * 当该标志为 ``True`` 时，使用 :class:`.UnicodeText`、:class:`_expression.TextClause` 和 :class:`.LargeBinary` 数据类型进行 DDL 渲染时，将分别渲染为 ``NVARCHAR(max)``、``VARCHAR(max)`` 和 ``VARBINARY(max)`` 类型。这是添加该标志后的新行为。

    * 当该标志为 ``False`` 时，使用 :class:`.UnicodeText`、:class:`_expression.TextClause` 和 :class:`.LargeBinary` 数据类型进行 DDL 渲染时，将分别渲染为 ``NTEXT``、``TEXT`` 和 ``IMAGE`` 类型。这是这些类型的长期行为。

    * 在数据库连接建立之前，标志的初始值为 ``None``。如果使用方言渲染 DDL 而未设置该标志，它将被解释为 ``False``。

    * 在首次连接时，方言会检测是否使用了 SQL Server 2012 或更高版本；如果标志仍为 ``None``，则会根据是否检测到 2012 或更高版本，将其设置为 ``True`` 或 ``False``。

    * 在创建方言时，可以将标志设置为 ``True`` 或 ``False``，通常通过 :func:`_sa.create_engine` 完成::

            eng = create_engine(
                "mssql+pymssql://user:pass@host/db", deprecate_large_types=True
            )

    * 通过使用大写类型对象，可以完全控制是否渲染“旧”或“新”类型： :class:`_types.NVARCHAR`、:class:`_types.VARCHAR`、:class:`_types.VARBINARY`、:class:`_types.TEXT`、:class:`_mssql.NTEXT`、:class:`_mssql.IMAGE`，这些类型将始终固定并始终输出精确的类型。

.. tab:: 英文

    Per
    `SQL Server 2012/2014 Documentation <https://technet.microsoft.com/en-us/library/ms187993.aspx>`_,
    the ``NTEXT``, ``TEXT`` and ``IMAGE`` datatypes are to be removed from SQL
    Server in a future release.   SQLAlchemy normally relates these types to the
    :class:`.UnicodeText`, :class:`_expression.TextClause` and
    :class:`.LargeBinary` datatypes.

    In order to accommodate this change, a new flag ``deprecate_large_types``
    is added to the dialect, which will be automatically set based on detection
    of the server version in use, if not otherwise set by the user.  The
    behavior of this flag is as follows:

    * When this flag is ``True``, the :class:`.UnicodeText`,
      :class:`_expression.TextClause` and
      :class:`.LargeBinary` datatypes, when used to render DDL, will render the
      types ``NVARCHAR(max)``, ``VARCHAR(max)``, and ``VARBINARY(max)``,
      respectively.  This is a new behavior as of the addition of this flag.

    * When this flag is ``False``, the :class:`.UnicodeText`,
      :class:`_expression.TextClause` and
      :class:`.LargeBinary` datatypes, when used to render DDL, will render the
      types ``NTEXT``, ``TEXT``, and ``IMAGE``,
      respectively.  This is the long-standing behavior of these types.

    * The flag begins with the value ``None``, before a database connection is
      established.   If the dialect is used to render DDL without the flag being
      set, it is interpreted the same as ``False``.

    * On first connection, the dialect detects if SQL Server version 2012 or
      greater is in use; if the flag is still at ``None``, it sets it to ``True``
      or ``False`` based on whether 2012 or greater is detected.

    * The flag can be set to either ``True`` or ``False`` when the dialect
      is created, typically via :func:`_sa.create_engine`::

            eng = create_engine(
                "mssql+pymssql://user:pass@host/db", deprecate_large_types=True
            )

    * Complete control over whether the "old" or "new" types are rendered is
      available in all SQLAlchemy versions by using the UPPERCASE type objects
      instead: :class:`_types.NVARCHAR`, :class:`_types.VARCHAR`,
      :class:`_types.VARBINARY`, :class:`_types.TEXT`, :class:`_mssql.NTEXT`,
      :class:`_mssql.IMAGE`
      will always remain fixed and always output exactly that
      type.

.. _multipart_schema_names:

多部分架构名称
----------------------

Multipart Schema Names

.. tab:: 中文

    SQL Server 架构有时需要多个部分来组成它们的“架构”限定符，即将数据库名称和所有者名称作为独立的令牌来表示，例如 ``mydatabase.dbo.some_table``。可以使用 :paramref:`_schema.Table.schema` 参数一次性设置这些多部分名称，方法如下::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="mydatabase.dbo",
        )

    在执行如表或组件反射等操作时，包含点的架构参数将被拆分为独立的“数据库”和“所有者”部分，以便正确查询 SQL Server 信息架构表，因为这两个值是分开存储的。此外，在为 DDL 或 SQL 渲染架构名称时，如果名称包含大小写敏感的名称或其他特殊字符，这两个组件将被分别引用。给定如下参数::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="MyDataBase.dbo",
        )

    上述架构将被渲染为 ``[MyDataBase].dbo``，并且在反射时，将使用 "dbo" 作为所有者，"MyDataBase" 作为数据库名称。

    要控制架构名称如何拆分为数据库/所有者，需在名称中指定括号（在 SQL Server 中为引用字符）。如下所示，"所有者" 将被视为 ``MyDataBase.dbo``，而 "数据库" 将为 None::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="[MyDataBase.dbo]",
        )

    要单独指定包含特殊字符或嵌入点的数据库和所有者名称，可以使用两组括号::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="[MyDataBase.Period].[MyOwner.Dot]",
        )

.. tab:: 英文

    SQL Server schemas sometimes require multiple parts to their "schema"
    qualifier, that is, including the database name and owner name as separate
    tokens, such as ``mydatabase.dbo.some_table``. These multipart names can be set
    at once using the :paramref:`_schema.Table.schema` argument of
    :class:`_schema.Table`::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="mydatabase.dbo",
        )

    When performing operations such as table or component reflection, a schema
    argument that contains a dot will be split into separate
    "database" and "owner"  components in order to correctly query the SQL
    Server information schema tables, as these two values are stored separately.
    Additionally, when rendering the schema name for DDL or SQL, the two
    components will be quoted separately for case sensitive names and other
    special characters.   Given an argument as below::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="MyDataBase.dbo",
        )

    The above schema would be rendered as ``[MyDataBase].dbo``, and also in
    reflection, would be reflected using "dbo" as the owner and "MyDataBase"
    as the database name.

    To control how the schema name is broken into database / owner,
    specify brackets (which in SQL Server are quoting characters) in the name.
    Below, the "owner" will be considered as ``MyDataBase.dbo`` and the
    "database" will be None::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="[MyDataBase.dbo]",
        )

    To individually specify both database and owner name with special characters
    or embedded dots, use two sets of brackets::

        Table(
            "some_table",
            metadata,
            Column("q", String(50)),
            schema="[MyDataBase.Period].[MyOwner.Dot]",
        )

.. _legacy_schema_rendering:

传统架构模式
------------------

Legacy Schema Mode

.. tab:: 中文

    MSSQL 方言的早期版本引入了一种行为，使得在 SELECT 语句中使用带有架构限定符的表时，该表会自动被别名；给定一个表如下::

        account_table = Table(
            "account",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("info", String(100)),
            schema="customer_schema",
        )

    这种遗留模式的渲染假设 "customer_schema.account" 并不被 SQL 语句的所有部分接受，如下所示：

    .. sourcecode:: pycon+sql

        >>> eng = create_engine("mssql+pymssql://mydsn", legacy_schema_aliasing=True)
        >>> print(account_table.select().compile(eng))
        {printsql}SELECT account_1.id, account_1.info
        FROM customer_schema.account AS account_1

    目前此行为默认已关闭，因为它似乎没有实际用途；然而，在遗留应用依赖此行为的情况下，仍可通过 `legacy_schema_aliasing` 参数来启用，如上所示。

    .. deprecated:: 1.4

       ``legacy_schema_aliasing`` 标志现在已被弃用，并将在未来的版本中移除。

.. tab:: 英文

    Very old versions of the MSSQL dialect introduced the behavior such that a
    schema-qualified table would be auto-aliased when used in a
    SELECT statement; given a table::

        account_table = Table(
            "account",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("info", String(100)),
            schema="customer_schema",
        )

    this legacy mode of rendering would assume that "customer_schema.account"
    would not be accepted by all parts of the SQL statement, as illustrated
    below:

    .. sourcecode:: pycon+sql

        >>> eng = create_engine("mssql+pymssql://mydsn", legacy_schema_aliasing=True)
        >>> print(account_table.select().compile(eng))
        {printsql}SELECT account_1.id, account_1.info
        FROM customer_schema.account AS account_1

    This mode of behavior is now off by default, as it appears to have served
    no purpose; however in the case that legacy applications rely upon it,
    it is available using the ``legacy_schema_aliasing`` argument to
    :func:`_sa.create_engine` as illustrated above.

    .. deprecated:: 1.4

        The ``legacy_schema_aliasing`` flag is now
        deprecated and will be removed in a future release.

.. _mssql_indexes:

聚集索引支持
-----------------------

Clustered Index Support

.. tab:: 中文

    MSSQL 方言通过 ``mssql_clustered`` 选项支持聚集索引（以及主键）。该选项可用于 :class:`.Index`、:class:`.UniqueConstraint` 和 :class:`.PrimaryKeyConstraint`。对于索引，该选项可与 ``mssql_columnstore`` 选项结合使用，以创建聚集列存储索引。

    要生成聚集索引，使用如下代码::

        Index("my_index", table.c.x, mssql_clustered=True)

    该索引会被渲染为 ``CREATE CLUSTERED INDEX my_index ON table (x)``。

    要生成聚集主键，使用如下代码：

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x", "y", mssql_clustered=True),
        )

    该表将被渲染为如下 SQL 语句：

    .. sourcecode:: sql

      CREATE TABLE my_table (
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        PRIMARY KEY CLUSTERED (x, y)
      )

    同样，我们可以使用以下代码生成聚集唯一约束：

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x"),
            UniqueConstraint("y", mssql_clustered=True),
        )

    要显式请求非聚集主键（例如，当需要单独的聚集索引时），使用如下代码：

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x", "y", mssql_clustered=False),
        )

    该表将被渲染为如下 SQL 语句：

    .. sourcecode:: sql

      CREATE TABLE my_table (
        x INTEGER NOT NULL,
        y INTEGER NOT NULL,
        PRIMARY KEY NONCLUSTERED (x, y)
      )

.. tab:: 英文

    The MSSQL dialect supports clustered indexes (and primary keys) via the
    ``mssql_clustered`` option.  This option is available to :class:`.Index`,
    :class:`.UniqueConstraint`. and :class:`.PrimaryKeyConstraint`.
    For indexes this option can be combined with the ``mssql_columnstore`` one
    to create a clustered columnstore index.

    To generate a clustered index::

        Index("my_index", table.c.x, mssql_clustered=True)

    which renders the index as ``CREATE CLUSTERED INDEX my_index ON table (x)``.

    To generate a clustered primary key use::

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x", "y", mssql_clustered=True),
        )

    which will render the table, for example, as:

    .. sourcecode:: sql

        CREATE TABLE my_table (
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            PRIMARY KEY CLUSTERED (x, y)
        )

    Similarly, we can generate a clustered unique constraint using::

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x"),
            UniqueConstraint("y", mssql_clustered=True),
        )

    To explicitly request a non-clustered primary key (for example, when
    a separate clustered index is desired), use::

        Table(
            "my_table",
            metadata,
            Column("x", ...),
            Column("y", ...),
            PrimaryKeyConstraint("x", "y", mssql_clustered=False),
        )

    which will render the table, for example, as:

    .. sourcecode:: sql

        CREATE TABLE my_table (
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            PRIMARY KEY NONCLUSTERED (x, y)
        )

列存储索引支持
-------------------------

Columnstore Index Support

.. tab:: 中文

    MSSQL 方言通过 ``mssql_columnstore`` 选项支持列存储索引。该选项可用于 :class:`.Index`。它可以与 ``mssql_clustered`` 选项结合使用，以创建聚集列存储索引。

    要生成列存储索引，使用如下代码::

        Index("my_index", table.c.x, mssql_columnstore=True)

    该索引将被渲染为 ``CREATE COLUMNSTORE INDEX my_index ON table (x)``。

    要生成聚集列存储索引，提供空的列定义::

        idx = Index("my_index", mssql_clustered=True, mssql_columnstore=True)
        # 需要将索引与表关联
        table.append_constraint(idx)

    上述代码将会渲染为 ``CREATE CLUSTERED COLUMNSTORE INDEX my_index ON table``。

.. tab:: 英文

    The MSSQL dialect supports columnstore indexes via the ``mssql_columnstore``
    option.  This option is available to :class:`.Index`. It be combined with
    the ``mssql_clustered`` option to create a clustered columnstore index.

    To generate a columnstore index::

        Index("my_index", table.c.x, mssql_columnstore=True)

    which renders the index as ``CREATE COLUMNSTORE INDEX my_index ON table (x)``.

    To generate a clustered columnstore index provide no columns::

        idx = Index("my_index", mssql_clustered=True, mssql_columnstore=True)
        # required to associate the index with the table
        table.append_constraint(idx)

    the above renders the index as
    ``CREATE CLUSTERED COLUMNSTORE INDEX my_index ON table``.

.. versionadded:: 2.0.18

MSSQL 特定索引选项
-----------------------------

MSSQL-Specific Index Options

.. tab:: 中文

    除了集群之外，MSSQL 方言还支持 :class:`.Index` 的其他特殊选项。

.. tab:: 英文

    In addition to clustering, the MSSQL dialect supports other special options for :class:`.Index`.

INCLUDE
^^^^^^^

INCLUDE

.. tab:: 中文

    ``mssql_include`` 选项会将给定字符串名称渲染为 INCLUDE(colname)::

        Index("my_index", table.c.x, mssql_include=["y"])

    会将索引渲染为 ``CREATE INDEX my_index ON table (x) INCLUDE (y)``

.. tab:: 英文

    The ``mssql_include`` option renders INCLUDE(colname) for the given string names::

        Index("my_index", table.c.x, mssql_include=["y"])

    would render the index as ``CREATE INDEX my_index ON table (x) INCLUDE (y)``

.. _mssql_index_where:

筛选索引
^^^^^^^^^^^^^^^^

Filtered Indexes

.. tab:: 中文

    ``mssql_where`` 选项会针对给定的字符串名称渲染 WHERE(condition) 语句::

        Index("my_index", table.c.x, mssql_where=table.c.x > 10)

    会将索引渲染为 ``CREATE INDEX my_index ON table (x) WHERE x > 10``。

.. tab:: 英文

    The ``mssql_where`` option renders WHERE(condition) for the given string names::

        Index("my_index", table.c.x, mssql_where=table.c.x > 10)

    would render the index as ``CREATE INDEX my_index ON table (x) WHERE x > 10``.

索引排序
^^^^^^^^^^^^^^

Index ordering

.. tab:: 中文

    索引排序可以通过函数表达式实现，例如::

        Index("my_index", table.c.x.desc())

    会将索引渲染为 ``CREATE INDEX my_index ON table (x DESC)``

    .. seealso::

        :ref:`schema_indexes_functional`

.. tab:: 英文

    Index ordering is available via functional expressions, such as::

        Index("my_index", table.c.x.desc())

    would render the index as ``CREATE INDEX my_index ON table (x DESC)``

    .. seealso::

        :ref:`schema_indexes_functional`

兼容级别
--------------------

Compatibility Levels

.. tab:: 中文

    MSSQL 支持在数据库级别设置兼容性级别。这允许，例如，在 SQL2005 数据库服务器上运行与 SQL2000 兼容的数据库。``server_version_info`` 始终返回数据库服务器版本信息（在这种情况下为 SQL2005），而不是兼容性级别信息。因此，如果在向后兼容模式下运行，SQLAlchemy 可能会尝试使用数据库服务器无法解析的 T-SQL 语句。

.. tab:: 英文

    MSSQL supports the notion of setting compatibility levels at the
    database level. This allows, for instance, to run a database that
    is compatible with SQL2000 while running on a SQL2005 database
    server. ``server_version_info`` will always return the database
    server version information (in this case SQL2005) and not the
    compatibility level information. Because of this, if running under
    a backwards compatibility mode SQLAlchemy may attempt to use T-SQL
    statements that are unable to be parsed by the database server.

.. _mssql_triggers:

触发器
--------

Triggers

.. tab:: 中文

    默认情况下，SQLAlchemy 使用 `OUTPUT INSERTED` 来获取通过 IDENTITY 列或其他服务器端默认值生成的新主键值。MS-SQL 不允许在具有触发器的表上使用 `OUTPUT INSERTED`。要禁用在每个表级别上使用 `OUTPUT INSERTED`，可以为每个具有触发器的 :class:`_schema.Table` 指定 ``implicit_returning=False``::

        Table(
            "mytable",
            metadata,
            Column("id", Integer, primary_key=True),
            # ...,
            implicit_returning=False,
        )

    声明式形式::

        class MyClass(Base):
            # ...
            __table_args__ = {"implicit_returning": False}

.. tab:: 英文

    SQLAlchemy by default uses OUTPUT INSERTED to get at newly
    generated primary key values via IDENTITY columns or other
    server side defaults.   MS-SQL does not
    allow the usage of OUTPUT INSERTED on tables that have triggers.
    To disable the usage of OUTPUT INSERTED on a per-table basis,
    specify ``implicit_returning=False`` for each :class:`_schema.Table`
    which has triggers::

        Table(
            "mytable",
            metadata,
            Column("id", Integer, primary_key=True),
            # ...,
            implicit_returning=False,
        )

    Declarative form::

        class MyClass(Base):
            # ...
            __table_args__ = {"implicit_returning": False}

.. _mssql_rowcount_versioning:

行数支持/ORM 版本控制
---------------------------------

Rowcount Support / ORM Versioning

.. tab:: 中文

    SQL Server 驱动程序可能在返回 UPDATE 或 DELETE 语句的更新行数方面存在限制。

    截至目前，PyODBC 驱动程序在使用 `OUTPUT INSERTED` 时无法返回行数。因此，SQLAlchemy 的早期版本在依赖准确行数以匹配版本号与匹配行数的功能（如 "ORM 版本控制" 功能）上存在限制。

    SQLAlchemy 2.0 现在通过手动检索这些特定用例的 "rowcount" 来解决这个问题，方法是通过计算 RETURNING 中返回的行数；因此，尽管驱动程序仍然存在此限制，但 ORM 版本控制功能不再受其影响。自 SQLAlchemy 2.0.5 起，pyodbc 驱动程序已完全恢复 ORM 版本控制支持。

    .. versionchanged:: 2.0.5  恢复了对 pyodbc 驱动程序的 ORM 版本控制支持。
       之前，在 ORM 刷新期间会发出警告，指示版本控制不受支持。

.. tab:: 英文

    The SQL Server drivers may have limited ability to return the number
    of rows updated from an UPDATE or DELETE statement.

    As of this writing, the PyODBC driver is not able to return a rowcount when
    OUTPUT INSERTED is used.    Previous versions of SQLAlchemy therefore had
    limitations for features such as the "ORM Versioning" feature that relies upon
    accurate rowcounts in order to match version numbers with matched rows.

    SQLAlchemy 2.0 now retrieves the "rowcount" manually for these particular use
    cases based on counting the rows that arrived back within RETURNING; so while
    the driver still has this limitation, the ORM Versioning feature is no longer
    impacted by it. As of SQLAlchemy 2.0.5, ORM versioning has been fully
    re-enabled for the pyodbc driver.

    .. versionchanged:: 2.0.5  ORM versioning support is restored for the pyodbc
        driver.  Previously, a warning would be emitted during ORM flush that
        versioning was not supported.


启用快照隔离
---------------------------

Enabling Snapshot Isolation

.. tab:: 中文

    SQL Server 有一个默认的事务隔离模式，它会锁定整个表，并导致即使是轻度并发的应用程序也会有长时间持有的锁和频繁的死锁。建议为整个数据库启用快照隔离，以支持现代级别的并发性。这可以通过以下 SQL 提示中的 ALTER DATABASE 命令来实现：

    .. sourcecode:: sql

        ALTER DATABASE MyDatabase SET ALLOW_SNAPSHOT_ISOLATION ON

        ALTER DATABASE MyDatabase SET READ_COMMITTED_SNAPSHOT ON

    有关 SQL Server 快照隔离的背景信息，请参见 https://msdn.microsoft.com/en-us/library/ms175095.aspx。

.. tab:: 英文

    SQL Server has a default transaction
    isolation mode that locks entire tables, and causes even mildly concurrent
    applications to have long held locks and frequent deadlocks.
    Enabling snapshot isolation for the database as a whole is recommended
    for modern levels of concurrency support.  This is accomplished via the
    following ALTER DATABASE commands executed at the SQL prompt:

    .. sourcecode:: sql

        ALTER DATABASE MyDatabase SET ALLOW_SNAPSHOT_ISOLATION ON

        ALTER DATABASE MyDatabase SET READ_COMMITTED_SNAPSHOT ON

    Background on SQL Server snapshot isolation is available at
    https://msdn.microsoft.com/en-us/library/ms175095.aspx.

"""  # noqa

from __future__ import annotations

import codecs
import datetime
import operator
import re
from typing import overload
from typing import TYPE_CHECKING
from uuid import UUID as _python_UUID

from . import information_schema as ischema
from .json import JSON
from .json import JSONIndexType
from .json import JSONPathType
from ... import exc
from ... import Identity
from ... import schema as sa_schema
from ... import Sequence
from ... import sql
from ... import text
from ... import util
from ...engine import cursor as _cursor
from ...engine import default
from ...engine import reflection
from ...engine.reflection import ReflectionDefaults
from ...sql import coercions
from ...sql import compiler
from ...sql import elements
from ...sql import expression
from ...sql import func
from ...sql import quoted_name
from ...sql import roles
from ...sql import sqltypes
from ...sql import try_cast as try_cast  # noqa: F401
from ...sql import util as sql_util
from ...sql._typing import is_sql_compiler
from ...sql.compiler import InsertmanyvaluesSentinelOpts
from ...sql.elements import TryCast as TryCast  # noqa: F401
from ...types import BIGINT
from ...types import BINARY
from ...types import CHAR
from ...types import DATE
from ...types import DATETIME
from ...types import DECIMAL
from ...types import FLOAT
from ...types import INTEGER
from ...types import NCHAR
from ...types import NUMERIC
from ...types import NVARCHAR
from ...types import SMALLINT
from ...types import TEXT
from ...types import VARCHAR
from ...util import update_wrapper
from ...util.typing import Literal

if TYPE_CHECKING:
    from ...sql.dml import DMLState
    from ...sql.selectable import TableClause

# https://sqlserverbuilds.blogspot.com/
MS_2017_VERSION = (14,)
MS_2016_VERSION = (13,)
MS_2014_VERSION = (12,)
MS_2012_VERSION = (11,)
MS_2008_VERSION = (10,)
MS_2005_VERSION = (9,)
MS_2000_VERSION = (8,)

RESERVED_WORDS = {
    "add",
    "all",
    "alter",
    "and",
    "any",
    "as",
    "asc",
    "authorization",
    "backup",
    "begin",
    "between",
    "break",
    "browse",
    "bulk",
    "by",
    "cascade",
    "case",
    "check",
    "checkpoint",
    "close",
    "clustered",
    "coalesce",
    "collate",
    "column",
    "commit",
    "compute",
    "constraint",
    "contains",
    "containstable",
    "continue",
    "convert",
    "create",
    "cross",
    "current",
    "current_date",
    "current_time",
    "current_timestamp",
    "current_user",
    "cursor",
    "database",
    "dbcc",
    "deallocate",
    "declare",
    "default",
    "delete",
    "deny",
    "desc",
    "disk",
    "distinct",
    "distributed",
    "double",
    "drop",
    "dump",
    "else",
    "end",
    "errlvl",
    "escape",
    "except",
    "exec",
    "execute",
    "exists",
    "exit",
    "external",
    "fetch",
    "file",
    "fillfactor",
    "for",
    "foreign",
    "freetext",
    "freetexttable",
    "from",
    "full",
    "function",
    "goto",
    "grant",
    "group",
    "having",
    "holdlock",
    "identity",
    "identity_insert",
    "identitycol",
    "if",
    "in",
    "index",
    "inner",
    "insert",
    "intersect",
    "into",
    "is",
    "join",
    "key",
    "kill",
    "left",
    "like",
    "lineno",
    "load",
    "merge",
    "national",
    "nocheck",
    "nonclustered",
    "not",
    "null",
    "nullif",
    "of",
    "off",
    "offsets",
    "on",
    "open",
    "opendatasource",
    "openquery",
    "openrowset",
    "openxml",
    "option",
    "or",
    "order",
    "outer",
    "over",
    "percent",
    "pivot",
    "plan",
    "precision",
    "primary",
    "print",
    "proc",
    "procedure",
    "public",
    "raiserror",
    "read",
    "readtext",
    "reconfigure",
    "references",
    "replication",
    "restore",
    "restrict",
    "return",
    "revert",
    "revoke",
    "right",
    "rollback",
    "rowcount",
    "rowguidcol",
    "rule",
    "save",
    "schema",
    "securityaudit",
    "select",
    "session_user",
    "set",
    "setuser",
    "shutdown",
    "some",
    "statistics",
    "system_user",
    "table",
    "tablesample",
    "textsize",
    "then",
    "to",
    "top",
    "tran",
    "transaction",
    "trigger",
    "truncate",
    "tsequal",
    "union",
    "unique",
    "unpivot",
    "update",
    "updatetext",
    "use",
    "user",
    "values",
    "varying",
    "view",
    "waitfor",
    "when",
    "where",
    "while",
    "with",
    "writetext",
}


class REAL(sqltypes.REAL):
    """the SQL Server REAL datatype."""

    def __init__(self, **kw):
        # REAL is a synonym for FLOAT(24) on SQL server.
        # it is only accepted as the word "REAL" in DDL, the numeric
        # precision value is not allowed to be present
        kw.setdefault("precision", 24)
        super().__init__(**kw)


class DOUBLE_PRECISION(sqltypes.DOUBLE_PRECISION):
    """the SQL Server DOUBLE PRECISION datatype.

    .. versionadded:: 2.0.11

    """

    def __init__(self, **kw):
        # DOUBLE PRECISION is a synonym for FLOAT(53) on SQL server.
        # it is only accepted as the word "DOUBLE PRECISION" in DDL,
        # the numeric precision value is not allowed to be present
        kw.setdefault("precision", 53)
        super().__init__(**kw)


class TINYINT(sqltypes.Integer):
    __visit_name__ = "TINYINT"


# MSSQL DATE/TIME types have varied behavior, sometimes returning
# strings.  MSDate/TIME check for everything, and always
# filter bind parameters into datetime objects (required by pyodbc,
# not sure about other dialects).


class _MSDate(sqltypes.Date):
    def bind_processor(self, dialect):
        def process(value):
            if type(value) == datetime.date:
                return datetime.datetime(value.year, value.month, value.day)
            else:
                return value

        return process

    _reg = re.compile(r"(\d+)-(\d+)-(\d+)")

    def result_processor(self, dialect, coltype):
        def process(value):
            if isinstance(value, datetime.datetime):
                return value.date()
            elif isinstance(value, str):
                m = self._reg.match(value)
                if not m:
                    raise ValueError("could not parse %r as a date value" % (value,))
                return datetime.date(*[int(x or 0) for x in m.groups()])
            else:
                return value

        return process


class TIME(sqltypes.TIME):
    def __init__(self, precision=None, **kwargs):
        self.precision = precision
        super().__init__()

    __zero_date = datetime.date(1900, 1, 1)

    def bind_processor(self, dialect):
        def process(value):
            if isinstance(value, datetime.datetime):
                value = datetime.datetime.combine(self.__zero_date, value.time())
            elif isinstance(value, datetime.time):
                """issue #5339
                per: https://github.com/mkleehammer/pyodbc/wiki/Tips-and-Tricks-by-Database-Platform#time-columns
                pass TIME value as string
                """  # noqa
                value = str(value)
            return value

        return process

    _reg = re.compile(r"(\d+):(\d+):(\d+)(?:\.(\d{0,6}))?")

    def result_processor(self, dialect, coltype):
        def process(value):
            if isinstance(value, datetime.datetime):
                return value.time()
            elif isinstance(value, str):
                m = self._reg.match(value)
                if not m:
                    raise ValueError("could not parse %r as a time value" % (value,))
                return datetime.time(*[int(x or 0) for x in m.groups()])
            else:
                return value

        return process


_MSTime = TIME


class _BASETIMEIMPL(TIME):
    __visit_name__ = "_BASETIMEIMPL"


class _DateTimeBase:
    def bind_processor(self, dialect):
        def process(value):
            if type(value) == datetime.date:
                return datetime.datetime(value.year, value.month, value.day)
            else:
                return value

        return process


class _MSDateTime(_DateTimeBase, sqltypes.DateTime):
    pass


class SMALLDATETIME(_DateTimeBase, sqltypes.DateTime):
    __visit_name__ = "SMALLDATETIME"


class DATETIME2(_DateTimeBase, sqltypes.DateTime):
    __visit_name__ = "DATETIME2"

    def __init__(self, precision=None, **kw):
        super().__init__(**kw)
        self.precision = precision


class DATETIMEOFFSET(_DateTimeBase, sqltypes.DateTime):
    __visit_name__ = "DATETIMEOFFSET"

    def __init__(self, precision=None, **kw):
        super().__init__(**kw)
        self.precision = precision


class _UnicodeLiteral:
    def literal_processor(self, dialect):
        def process(value):
            value = value.replace("'", "''")

            if dialect.identifier_preparer._double_percents:
                value = value.replace("%", "%%")

            return "N'%s'" % value

        return process


class _MSUnicode(_UnicodeLiteral, sqltypes.Unicode):
    pass


class _MSUnicodeText(_UnicodeLiteral, sqltypes.UnicodeText):
    pass


class TIMESTAMP(sqltypes._Binary):
    """Implement the SQL Server TIMESTAMP type.

    Note this is **completely different** than the SQL Standard
    TIMESTAMP type, which is not supported by SQL Server.  It
    is a read-only datatype that does not support INSERT of values.

    .. seealso::

        :class:`_mssql.ROWVERSION`

    """

    __visit_name__ = "TIMESTAMP"

    # expected by _Binary to be present
    length = None

    def __init__(self, convert_int=False):
        """Construct a TIMESTAMP or ROWVERSION type.

        :param convert_int: if True, binary integer values will
         be converted to integers on read.

        """
        self.convert_int = convert_int

    def result_processor(self, dialect, coltype):
        super_ = super().result_processor(dialect, coltype)
        if self.convert_int:

            def process(value):
                if super_:
                    value = super_(value)
                if value is not None:
                    # https://stackoverflow.com/a/30403242/34549
                    value = int(codecs.encode(value, "hex"), 16)
                return value

            return process
        else:
            return super_


class ROWVERSION(TIMESTAMP):
    """Implement the SQL Server ROWVERSION type.

    The ROWVERSION datatype is a SQL Server synonym for the TIMESTAMP
    datatype, however current SQL Server documentation suggests using
    ROWVERSION for new datatypes going forward.

    The ROWVERSION datatype does **not** reflect (e.g. introspect) from the
    database as itself; the returned datatype will be
    :class:`_mssql.TIMESTAMP`.

    This is a read-only datatype that does not support INSERT of values.

    .. seealso::

        :class:`_mssql.TIMESTAMP`

    """

    __visit_name__ = "ROWVERSION"


class NTEXT(sqltypes.UnicodeText):
    """MSSQL NTEXT type, for variable-length unicode text up to 2^30
    characters."""

    __visit_name__ = "NTEXT"


class VARBINARY(sqltypes.VARBINARY, sqltypes.LargeBinary):
    """The MSSQL VARBINARY type.

    This type adds additional features to the core :class:`_types.VARBINARY`
    type, including "deprecate_large_types" mode where
    either ``VARBINARY(max)`` or IMAGE is rendered, as well as the SQL
    Server ``FILESTREAM`` option.

    .. seealso::

        :ref:`mssql_large_type_deprecation`

    """

    __visit_name__ = "VARBINARY"

    def __init__(self, length=None, filestream=False):
        """
        Construct a VARBINARY type.

        :param length: optional, a length for the column for use in
          DDL statements, for those binary types that accept a length,
          such as the MySQL BLOB type.

        :param filestream=False: if True, renders the ``FILESTREAM`` keyword
          in the table definition. In this case ``length`` must be ``None``
          or ``'max'``.

          .. versionadded:: 1.4.31

        """

        self.filestream = filestream
        if self.filestream and length not in (None, "max"):
            raise ValueError("length must be None or 'max' when setting filestream")
        super().__init__(length=length)


class IMAGE(sqltypes.LargeBinary):
    __visit_name__ = "IMAGE"


class XML(sqltypes.Text):
    """MSSQL XML type.

    This is a placeholder type for reflection purposes that does not include
    any Python-side datatype support.   It also does not currently support
    additional arguments, such as "CONTENT", "DOCUMENT",
    "xml_schema_collection".

    """

    __visit_name__ = "XML"


class BIT(sqltypes.Boolean):
    """MSSQL BIT type.

    Both pyodbc and pymssql return values from BIT columns as
    Python <class 'bool'> so just subclass Boolean.

    """

    __visit_name__ = "BIT"


class MONEY(sqltypes.TypeEngine):
    __visit_name__ = "MONEY"


class SMALLMONEY(sqltypes.TypeEngine):
    __visit_name__ = "SMALLMONEY"


class MSUUid(sqltypes.Uuid):
    def bind_processor(self, dialect):
        if self.native_uuid:
            # this is currently assuming pyodbc; might not work for
            # some other mssql driver
            return None
        else:
            if self.as_uuid:

                def process(value):
                    if value is not None:
                        value = value.hex
                    return value

                return process
            else:

                def process(value):
                    if value is not None:
                        value = value.replace("-", "").replace("''", "'")
                    return value

                return process

    def literal_processor(self, dialect):
        if self.native_uuid:

            def process(value):
                return f"""'{str(value).replace("''", "'")}'"""

            return process
        else:
            if self.as_uuid:

                def process(value):
                    return f"""'{value.hex}'"""

                return process
            else:

                def process(value):
                    return f"""'{value.replace("-", "").replace("'", "''")}'"""

                return process


class UNIQUEIDENTIFIER(sqltypes.Uuid[sqltypes._UUID_RETURN]):
    __visit_name__ = "UNIQUEIDENTIFIER"

    @overload
    def __init__(
        self: UNIQUEIDENTIFIER[_python_UUID], as_uuid: Literal[True] = ...
    ): ...

    @overload
    def __init__(self: UNIQUEIDENTIFIER[str], as_uuid: Literal[False] = ...): ...

    def __init__(self, as_uuid: bool = True):
        """Construct a :class:`_mssql.UNIQUEIDENTIFIER` type.


        :param as_uuid=True: if True, values will be interpreted
         as Python uuid objects, converting to/from string via the
         DBAPI.

         .. versionchanged:: 2.0 Added direct "uuid" support to the
            :class:`_mssql.UNIQUEIDENTIFIER` datatype; uuid interpretation
            defaults to ``True``.

        """
        self.as_uuid = as_uuid
        self.native_uuid = True


class SQL_VARIANT(sqltypes.TypeEngine):
    __visit_name__ = "SQL_VARIANT"


# old names.
MSDateTime = _MSDateTime
MSDate = _MSDate
MSReal = REAL
MSTinyInteger = TINYINT
MSTime = TIME
MSSmallDateTime = SMALLDATETIME
MSDateTime2 = DATETIME2
MSDateTimeOffset = DATETIMEOFFSET
MSText = TEXT
MSNText = NTEXT
MSString = VARCHAR
MSNVarchar = NVARCHAR
MSChar = CHAR
MSNChar = NCHAR
MSBinary = BINARY
MSVarBinary = VARBINARY
MSImage = IMAGE
MSBit = BIT
MSMoney = MONEY
MSSmallMoney = SMALLMONEY
MSUniqueIdentifier = UNIQUEIDENTIFIER
MSVariant = SQL_VARIANT

ischema_names = {
    "int": INTEGER,
    "bigint": BIGINT,
    "smallint": SMALLINT,
    "tinyint": TINYINT,
    "varchar": VARCHAR,
    "nvarchar": NVARCHAR,
    "char": CHAR,
    "nchar": NCHAR,
    "text": TEXT,
    "ntext": NTEXT,
    "decimal": DECIMAL,
    "numeric": NUMERIC,
    "float": FLOAT,
    "datetime": DATETIME,
    "datetime2": DATETIME2,
    "datetimeoffset": DATETIMEOFFSET,
    "date": DATE,
    "time": TIME,
    "smalldatetime": SMALLDATETIME,
    "binary": BINARY,
    "varbinary": VARBINARY,
    "bit": BIT,
    "real": REAL,
    "double precision": DOUBLE_PRECISION,
    "image": IMAGE,
    "xml": XML,
    "timestamp": TIMESTAMP,
    "money": MONEY,
    "smallmoney": SMALLMONEY,
    "uniqueidentifier": UNIQUEIDENTIFIER,
    "sql_variant": SQL_VARIANT,
}


class MSTypeCompiler(compiler.GenericTypeCompiler):
    def _extend(self, spec, type_, length=None):
        """Extend a string-type declaration with standard SQL
        COLLATE annotations.

        """

        if getattr(type_, "collation", None):
            collation = "COLLATE %s" % type_.collation
        else:
            collation = None

        if not length:
            length = type_.length

        if length:
            spec = spec + "(%s)" % length

        return " ".join([c for c in (spec, collation) if c is not None])

    def visit_double(self, type_, **kw):
        return self.visit_DOUBLE_PRECISION(type_, **kw)

    def visit_FLOAT(self, type_, **kw):
        precision = getattr(type_, "precision", None)
        if precision is None:
            return "FLOAT"
        else:
            return "FLOAT(%(precision)s)" % {"precision": precision}

    def visit_TINYINT(self, type_, **kw):
        return "TINYINT"

    def visit_TIME(self, type_, **kw):
        precision = getattr(type_, "precision", None)
        if precision is not None:
            return "TIME(%s)" % precision
        else:
            return "TIME"

    def visit_TIMESTAMP(self, type_, **kw):
        return "TIMESTAMP"

    def visit_ROWVERSION(self, type_, **kw):
        return "ROWVERSION"

    def visit_datetime(self, type_, **kw):
        if type_.timezone:
            return self.visit_DATETIMEOFFSET(type_, **kw)
        else:
            return self.visit_DATETIME(type_, **kw)

    def visit_DATETIMEOFFSET(self, type_, **kw):
        precision = getattr(type_, "precision", None)
        if precision is not None:
            return "DATETIMEOFFSET(%s)" % type_.precision
        else:
            return "DATETIMEOFFSET"

    def visit_DATETIME2(self, type_, **kw):
        precision = getattr(type_, "precision", None)
        if precision is not None:
            return "DATETIME2(%s)" % precision
        else:
            return "DATETIME2"

    def visit_SMALLDATETIME(self, type_, **kw):
        return "SMALLDATETIME"

    def visit_unicode(self, type_, **kw):
        return self.visit_NVARCHAR(type_, **kw)

    def visit_text(self, type_, **kw):
        if self.dialect.deprecate_large_types:
            return self.visit_VARCHAR(type_, **kw)
        else:
            return self.visit_TEXT(type_, **kw)

    def visit_unicode_text(self, type_, **kw):
        if self.dialect.deprecate_large_types:
            return self.visit_NVARCHAR(type_, **kw)
        else:
            return self.visit_NTEXT(type_, **kw)

    def visit_NTEXT(self, type_, **kw):
        return self._extend("NTEXT", type_)

    def visit_TEXT(self, type_, **kw):
        return self._extend("TEXT", type_)

    def visit_VARCHAR(self, type_, **kw):
        return self._extend("VARCHAR", type_, length=type_.length or "max")

    def visit_CHAR(self, type_, **kw):
        return self._extend("CHAR", type_)

    def visit_NCHAR(self, type_, **kw):
        return self._extend("NCHAR", type_)

    def visit_NVARCHAR(self, type_, **kw):
        return self._extend("NVARCHAR", type_, length=type_.length or "max")

    def visit_date(self, type_, **kw):
        if self.dialect.server_version_info < MS_2008_VERSION:
            return self.visit_DATETIME(type_, **kw)
        else:
            return self.visit_DATE(type_, **kw)

    def visit__BASETIMEIMPL(self, type_, **kw):
        return self.visit_time(type_, **kw)

    def visit_time(self, type_, **kw):
        if self.dialect.server_version_info < MS_2008_VERSION:
            return self.visit_DATETIME(type_, **kw)
        else:
            return self.visit_TIME(type_, **kw)

    def visit_large_binary(self, type_, **kw):
        if self.dialect.deprecate_large_types:
            return self.visit_VARBINARY(type_, **kw)
        else:
            return self.visit_IMAGE(type_, **kw)

    def visit_IMAGE(self, type_, **kw):
        return "IMAGE"

    def visit_XML(self, type_, **kw):
        return "XML"

    def visit_VARBINARY(self, type_, **kw):
        text = self._extend("VARBINARY", type_, length=type_.length or "max")
        if getattr(type_, "filestream", False):
            text += " FILESTREAM"
        return text

    def visit_boolean(self, type_, **kw):
        return self.visit_BIT(type_)

    def visit_BIT(self, type_, **kw):
        return "BIT"

    def visit_JSON(self, type_, **kw):
        # this is a bit of a break with SQLAlchemy's convention of
        # "UPPERCASE name goes to UPPERCASE type name with no modification"
        return self._extend("NVARCHAR", type_, length="max")

    def visit_MONEY(self, type_, **kw):
        return "MONEY"

    def visit_SMALLMONEY(self, type_, **kw):
        return "SMALLMONEY"

    def visit_uuid(self, type_, **kw):
        if type_.native_uuid:
            return self.visit_UNIQUEIDENTIFIER(type_, **kw)
        else:
            return super().visit_uuid(type_, **kw)

    def visit_UNIQUEIDENTIFIER(self, type_, **kw):
        return "UNIQUEIDENTIFIER"

    def visit_SQL_VARIANT(self, type_, **kw):
        return "SQL_VARIANT"


class MSExecutionContext(default.DefaultExecutionContext):
    _enable_identity_insert = False
    _select_lastrowid = False
    _lastrowid = None

    dialect: MSDialect

    def _opt_encode(self, statement):
        if self.compiled and self.compiled.schema_translate_map:
            rst = self.compiled.preparer._render_schema_translates
            statement = rst(statement, self.compiled.schema_translate_map)

        return statement

    def pre_exec(self):
        """Activate IDENTITY_INSERT if needed."""

        if self.isinsert:
            if TYPE_CHECKING:
                assert is_sql_compiler(self.compiled)
                assert isinstance(self.compiled.compile_state, DMLState)
                assert isinstance(self.compiled.compile_state.dml_table, TableClause)

            tbl = self.compiled.compile_state.dml_table
            id_column = tbl._autoincrement_column

            if id_column is not None and (not isinstance(id_column.default, Sequence)):
                insert_has_identity = True
                compile_state = self.compiled.dml_compile_state
                self._enable_identity_insert = (
                    id_column.key in self.compiled_parameters[0]
                ) or (
                    compile_state._dict_parameters
                    and (id_column.key in compile_state._insert_col_keys)
                )

            else:
                insert_has_identity = False
                self._enable_identity_insert = False

            self._select_lastrowid = (
                not self.compiled.inline
                and insert_has_identity
                and not self.compiled.effective_returning
                and not self._enable_identity_insert
                and not self.executemany
            )

            if self._enable_identity_insert:
                self.root_connection._cursor_execute(
                    self.cursor,
                    self._opt_encode(
                        "SET IDENTITY_INSERT %s ON"
                        % self.identifier_preparer.format_table(tbl)
                    ),
                    (),
                    self,
                )

    def post_exec(self):
        """Disable IDENTITY_INSERT if enabled."""

        conn = self.root_connection

        if self.isinsert or self.isupdate or self.isdelete:
            self._rowcount = self.cursor.rowcount

        if self._select_lastrowid:
            if self.dialect.use_scope_identity:
                conn._cursor_execute(
                    self.cursor,
                    "SELECT scope_identity() AS lastrowid",
                    (),
                    self,
                )
            else:
                conn._cursor_execute(
                    self.cursor, "SELECT @@identity AS lastrowid", (), self
                )
            # fetchall() ensures the cursor is consumed without closing it
            row = self.cursor.fetchall()[0]
            self._lastrowid = int(row[0])

            self.cursor_fetch_strategy = _cursor._NO_CURSOR_DML
        elif (
            self.compiled is not None
            and is_sql_compiler(self.compiled)
            and self.compiled.effective_returning
        ):
            self.cursor_fetch_strategy = _cursor.FullyBufferedCursorFetchStrategy(
                self.cursor,
                self.cursor.description,
                self.cursor.fetchall(),
            )

        if self._enable_identity_insert:
            if TYPE_CHECKING:
                assert is_sql_compiler(self.compiled)
                assert isinstance(self.compiled.compile_state, DMLState)
                assert isinstance(self.compiled.compile_state.dml_table, TableClause)
            conn._cursor_execute(
                self.cursor,
                self._opt_encode(
                    "SET IDENTITY_INSERT %s OFF"
                    % self.identifier_preparer.format_table(
                        self.compiled.compile_state.dml_table
                    )
                ),
                (),
                self,
            )

    def get_lastrowid(self):
        return self._lastrowid

    def handle_dbapi_exception(self, e):
        if self._enable_identity_insert:
            try:
                self.cursor.execute(
                    self._opt_encode(
                        "SET IDENTITY_INSERT %s OFF"
                        % self.identifier_preparer.format_table(
                            self.compiled.compile_state.dml_table
                        )
                    )
                )
            except Exception:
                pass

    def fire_sequence(self, seq, type_):
        return self._execute_scalar(
            (
                "SELECT NEXT VALUE FOR %s"
                % self.identifier_preparer.format_sequence(seq)
            ),
            type_,
        )

    def get_insert_default(self, column):
        if (
            isinstance(column, sa_schema.Column)
            and column is column.table._autoincrement_column
            and isinstance(column.default, sa_schema.Sequence)
            and column.default.optional
        ):
            return None
        return super().get_insert_default(column)


class MSSQLCompiler(compiler.SQLCompiler):
    returning_precedes_values = True

    extract_map = util.update_copy(
        compiler.SQLCompiler.extract_map,
        {
            "doy": "dayofyear",
            "dow": "weekday",
            "milliseconds": "millisecond",
            "microseconds": "microsecond",
        },
    )

    def __init__(self, *args, **kwargs):
        self.tablealiases = {}
        super().__init__(*args, **kwargs)

    def visit_frame_clause(self, frameclause, **kw):
        kw["literal_execute"] = True
        return super().visit_frame_clause(frameclause, **kw)

    def _with_legacy_schema_aliasing(fn):
        def decorate(self, *arg, **kw):
            if self.dialect.legacy_schema_aliasing:
                return fn(self, *arg, **kw)
            else:
                super_ = getattr(super(MSSQLCompiler, self), fn.__name__)
                return super_(*arg, **kw)

        return decorate

    def visit_now_func(self, fn, **kw):
        return "CURRENT_TIMESTAMP"

    def visit_current_date_func(self, fn, **kw):
        return "GETDATE()"

    def visit_length_func(self, fn, **kw):
        return "LEN%s" % self.function_argspec(fn, **kw)

    def visit_char_length_func(self, fn, **kw):
        return "LEN%s" % self.function_argspec(fn, **kw)

    def visit_aggregate_strings_func(self, fn, **kw):
        expr = fn.clauses.clauses[0]._compiler_dispatch(self, **kw)
        kw["literal_execute"] = True
        delimeter = fn.clauses.clauses[1]._compiler_dispatch(self, **kw)
        return f"string_agg({expr}, {delimeter})"

    def visit_concat_op_expression_clauselist(self, clauselist, operator, **kw):
        return " + ".join(self.process(elem, **kw) for elem in clauselist)

    def visit_concat_op_binary(self, binary, operator, **kw):
        return "%s + %s" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def visit_true(self, expr, **kw):
        return "1"

    def visit_false(self, expr, **kw):
        return "0"

    def visit_match_op_binary(self, binary, operator, **kw):
        return "CONTAINS (%s, %s)" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def get_select_precolumns(self, select, **kw):
        """MS-SQL puts TOP, it's version of LIMIT here"""

        s = super().get_select_precolumns(select, **kw)

        if select._has_row_limiting_clause and self._use_top(select):
            # ODBC drivers and possibly others
            # don't support bind params in the SELECT clause on SQL Server.
            # so have to use literal here.
            kw["literal_execute"] = True
            s += "TOP %s " % self.process(self._get_limit_or_fetch(select), **kw)
            if select._fetch_clause is not None:
                if select._fetch_clause_options["percent"]:
                    s += "PERCENT "
                if select._fetch_clause_options["with_ties"]:
                    s += "WITH TIES "

        return s

    def get_from_hint_text(self, table, text):
        return text

    def get_crud_hint_text(self, table, text):
        return text

    def _get_limit_or_fetch(self, select):
        if select._fetch_clause is None:
            return select._limit_clause
        else:
            return select._fetch_clause

    def _use_top(self, select):
        return (select._offset_clause is None) and (
            select._simple_int_clause(select._limit_clause)
            or (
                # limit can use TOP with is by itself. fetch only uses TOP
                # when it needs to because of PERCENT and/or WITH TIES
                # TODO: Why?  shouldn't we use TOP always ?
                select._simple_int_clause(select._fetch_clause)
                and (
                    select._fetch_clause_options["percent"]
                    or select._fetch_clause_options["with_ties"]
                )
            )
        )

    def limit_clause(self, cs, **kwargs):
        return ""

    def _check_can_use_fetch_limit(self, select):
        # to use ROW_NUMBER(), an ORDER BY is required.
        # OFFSET are FETCH are options of the ORDER BY clause
        if not select._order_by_clause.clauses:
            raise exc.CompileError(
                "MSSQL requires an order_by when "
                "using an OFFSET or a non-simple "
                "LIMIT clause"
            )

        if select._fetch_clause_options is not None and (
            select._fetch_clause_options["percent"]
            or select._fetch_clause_options["with_ties"]
        ):
            raise exc.CompileError(
                "MSSQL needs TOP to use PERCENT and/or WITH TIES. "
                "Only simple fetch without offset can be used."
            )

    def _row_limit_clause(self, select, **kw):
        """MSSQL 2012 supports OFFSET/FETCH operators
        Use it instead subquery with row_number

        """

        if self.dialect._supports_offset_fetch and not self._use_top(select):
            self._check_can_use_fetch_limit(select)

            return self.fetch_clause(
                select,
                fetch_clause=self._get_limit_or_fetch(select),
                require_offset=True,
                **kw,
            )

        else:
            return ""

    def visit_try_cast(self, element, **kw):
        return "TRY_CAST (%s AS %s)" % (
            self.process(element.clause, **kw),
            self.process(element.typeclause, **kw),
        )

    def translate_select_structure(self, select_stmt, **kwargs):
        """Look for ``LIMIT`` and OFFSET in a select statement, and if
        so tries to wrap it in a subquery with ``row_number()`` criterion.
        MSSQL 2012 and above are excluded

        """
        select = select_stmt

        if (
            select._has_row_limiting_clause
            and not self.dialect._supports_offset_fetch
            and not self._use_top(select)
            and not getattr(select, "_mssql_visit", None)
        ):
            self._check_can_use_fetch_limit(select)

            _order_by_clauses = [
                sql_util.unwrap_label_reference(elem)
                for elem in select._order_by_clause.clauses
            ]

            limit_clause = self._get_limit_or_fetch(select)
            offset_clause = select._offset_clause

            select = select._generate()
            select._mssql_visit = True
            select = (
                select.add_columns(
                    sql.func.ROW_NUMBER()
                    .over(order_by=_order_by_clauses)
                    .label("mssql_rn")
                )
                .order_by(None)
                .alias()
            )

            mssql_rn = sql.column("mssql_rn")
            limitselect = sql.select(*[c for c in select.c if c.key != "mssql_rn"])
            if offset_clause is not None:
                limitselect = limitselect.where(mssql_rn > offset_clause)
                if limit_clause is not None:
                    limitselect = limitselect.where(
                        mssql_rn <= (limit_clause + offset_clause)
                    )
            else:
                limitselect = limitselect.where(mssql_rn <= (limit_clause))
            return limitselect
        else:
            return select

    @_with_legacy_schema_aliasing
    def visit_table(self, table, mssql_aliased=False, iscrud=False, **kwargs):
        if mssql_aliased is table or iscrud:
            return super().visit_table(table, **kwargs)

        # alias schema-qualified tables
        alias = self._schema_aliased_table(table)
        if alias is not None:
            return self.process(alias, mssql_aliased=table, **kwargs)
        else:
            return super().visit_table(table, **kwargs)

    @_with_legacy_schema_aliasing
    def visit_alias(self, alias, **kw):
        # translate for schema-qualified table aliases
        kw["mssql_aliased"] = alias.element
        return super().visit_alias(alias, **kw)

    @_with_legacy_schema_aliasing
    def visit_column(self, column, add_to_result_map=None, **kw):
        if (
            column.table is not None
            and (not self.isupdate and not self.isdelete)
            or self.is_subquery()
        ):
            # translate for schema-qualified table aliases
            t = self._schema_aliased_table(column.table)
            if t is not None:
                converted = elements._corresponding_column_or_error(t, column)
                if add_to_result_map is not None:
                    add_to_result_map(
                        column.name,
                        column.name,
                        (column, column.name, column.key),
                        column.type,
                    )

                return super().visit_column(converted, **kw)

        return super().visit_column(column, add_to_result_map=add_to_result_map, **kw)

    def _schema_aliased_table(self, table):
        if getattr(table, "schema", None) is not None:
            if table not in self.tablealiases:
                self.tablealiases[table] = table.alias()
            return self.tablealiases[table]
        else:
            return None

    def visit_extract(self, extract, **kw):
        field = self.extract_map.get(extract.field, extract.field)
        return "DATEPART(%s, %s)" % (field, self.process(extract.expr, **kw))

    def visit_savepoint(self, savepoint_stmt, **kw):
        return "SAVE TRANSACTION %s" % self.preparer.format_savepoint(savepoint_stmt)

    def visit_rollback_to_savepoint(self, savepoint_stmt, **kw):
        return "ROLLBACK TRANSACTION %s" % self.preparer.format_savepoint(
            savepoint_stmt
        )

    def visit_binary(self, binary, **kwargs):
        """Move bind parameters to the right-hand side of an operator, where
        possible.

        """
        if (
            isinstance(binary.left, expression.BindParameter)
            and binary.operator == operator.eq
            and not isinstance(binary.right, expression.BindParameter)
        ):
            return self.process(
                expression.BinaryExpression(binary.right, binary.left, binary.operator),
                **kwargs,
            )
        return super().visit_binary(binary, **kwargs)

    def returning_clause(self, stmt, returning_cols, *, populate_result_map, **kw):
        # SQL server returning clause requires that the columns refer to
        # the virtual table names "inserted" or "deleted".   Here, we make
        # a simple alias of our table with that name, and then adapt the
        # columns we have from the list of RETURNING columns to that new name
        # so that they render as "inserted.<colname>" / "deleted.<colname>".

        if stmt.is_insert or stmt.is_update:
            target = stmt.table.alias("inserted")
        elif stmt.is_delete:
            target = stmt.table.alias("deleted")
        else:
            assert False, "expected Insert, Update or Delete statement"

        adapter = sql_util.ClauseAdapter(target)

        # adapter.traverse() takes a column from our target table and returns
        # the one that is linked to the "inserted" / "deleted" tables.  So  in
        # order to retrieve these values back from the result  (e.g. like
        # row[column]), tell the compiler to also add the original unadapted
        # column to the result map.   Before #4877, these were  (unknowingly)
        # falling back using string name matching in the result set which
        # necessarily used an expensive KeyError in order to match.

        columns = [
            self._label_returning_column(
                stmt,
                adapter.traverse(column),
                populate_result_map,
                {"result_map_targets": (column,)},
                fallback_label_name=fallback_label_name,
                column_is_repeated=repeated,
                name=name,
                proxy_name=proxy_name,
                **kw,
            )
            for (
                name,
                proxy_name,
                fallback_label_name,
                column,
                repeated,
            ) in stmt._generate_columns_plus_names(
                True, cols=expression._select_iterables(returning_cols)
            )
        ]

        return "OUTPUT " + ", ".join(columns)

    def get_cte_preamble(self, recursive):
        # SQL Server finds it too inconvenient to accept
        # an entirely optional, SQL standard specified,
        # "RECURSIVE" word with their "WITH",
        # so here we go
        return "WITH"

    def label_select_column(self, select, column, asfrom):
        if isinstance(column, expression.Function):
            return column.label(None)
        else:
            return super().label_select_column(select, column, asfrom)

    def for_update_clause(self, select, **kw):
        # "FOR UPDATE" is only allowed on "DECLARE CURSOR" which
        # SQLAlchemy doesn't use
        return ""

    def order_by_clause(self, select, **kw):
        # MSSQL only allows ORDER BY in subqueries if there is a LIMIT:
        # "The ORDER BY clause is invalid in views, inline functions,
        # derived tables, subqueries, and common table expressions,
        # unless TOP, OFFSET or FOR XML is also specified."
        if (
            self.is_subquery()
            and not self._use_top(select)
            and (select._offset is None or not self.dialect._supports_offset_fetch)
        ):
            # avoid processing the order by clause if we won't end up
            # using it, because we don't want all the bind params tacked
            # onto the positional list if that is what the dbapi requires
            return ""

        order_by = self.process(select._order_by_clause, **kw)

        if order_by:
            return " ORDER BY " + order_by
        else:
            return ""

    def update_from_clause(
        self, update_stmt, from_table, extra_froms, from_hints, **kw
    ):
        """Render the UPDATE..FROM clause specific to MSSQL.

        In MSSQL, if the UPDATE statement involves an alias of the table to
        be updated, then the table itself must be added to the FROM list as
        well. Otherwise, it is optional. Here, we add it regardless.

        """
        return "FROM " + ", ".join(
            t._compiler_dispatch(self, asfrom=True, fromhints=from_hints, **kw)
            for t in [from_table] + extra_froms
        )

    def delete_table_clause(self, delete_stmt, from_table, extra_froms, **kw):
        """If we have extra froms make sure we render any alias as hint."""
        ashint = False
        if extra_froms:
            ashint = True
        return from_table._compiler_dispatch(
            self, asfrom=True, iscrud=True, ashint=ashint, **kw
        )

    def delete_extra_from_clause(
        self, delete_stmt, from_table, extra_froms, from_hints, **kw
    ):
        """Render the DELETE .. FROM clause specific to MSSQL.

        Yes, it has the FROM keyword twice.

        """
        return "FROM " + ", ".join(
            t._compiler_dispatch(self, asfrom=True, fromhints=from_hints, **kw)
            for t in [from_table] + extra_froms
        )

    def visit_empty_set_expr(self, type_, **kw):
        return "SELECT 1 WHERE 1!=1"

    def visit_is_distinct_from_binary(self, binary, operator, **kw):
        return "NOT EXISTS (SELECT %s INTERSECT SELECT %s)" % (
            self.process(binary.left),
            self.process(binary.right),
        )

    def visit_is_not_distinct_from_binary(self, binary, operator, **kw):
        return "EXISTS (SELECT %s INTERSECT SELECT %s)" % (
            self.process(binary.left),
            self.process(binary.right),
        )

    def _render_json_extract_from_binary(self, binary, operator, **kw):
        # note we are intentionally calling upon the process() calls in the
        # order in which they appear in the SQL String as this is used
        # by positional parameter rendering

        if binary.type._type_affinity is sqltypes.JSON:
            return "JSON_QUERY(%s, %s)" % (
                self.process(binary.left, **kw),
                self.process(binary.right, **kw),
            )

        # as with other dialects, start with an explicit test for NULL
        case_expression = "CASE JSON_VALUE(%s, %s) WHEN NULL THEN NULL" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

        if binary.type._type_affinity is sqltypes.Integer:
            type_expression = "ELSE CAST(JSON_VALUE(%s, %s) AS INTEGER)" % (
                self.process(binary.left, **kw),
                self.process(binary.right, **kw),
            )
        elif binary.type._type_affinity in (sqltypes.Numeric, sqltypes.Float):
            type_expression = "ELSE CAST(JSON_VALUE(%s, %s) AS %s)" % (
                self.process(binary.left, **kw),
                self.process(binary.right, **kw),
                (
                    "FLOAT"
                    if isinstance(binary.type, sqltypes.Float)
                    else "NUMERIC(%s, %s)" % (binary.type.precision, binary.type.scale)
                ),
            )
        elif binary.type._type_affinity is sqltypes.Boolean:
            # the NULL handling is particularly weird with boolean, so
            # explicitly return numeric (BIT) constants
            type_expression = "WHEN 'true' THEN 1 WHEN 'false' THEN 0 ELSE NULL"
        elif binary.type._type_affinity is sqltypes.String:
            # TODO: does this comment (from mysql) apply to here, too?
            #       this fails with a JSON value that's a four byte unicode
            #       string.  SQLite has the same problem at the moment
            type_expression = "ELSE JSON_VALUE(%s, %s)" % (
                self.process(binary.left, **kw),
                self.process(binary.right, **kw),
            )
        else:
            # other affinity....this is not expected right now
            type_expression = "ELSE JSON_QUERY(%s, %s)" % (
                self.process(binary.left, **kw),
                self.process(binary.right, **kw),
            )

        return case_expression + " " + type_expression + " END"

    def visit_json_getitem_op_binary(self, binary, operator, **kw):
        return self._render_json_extract_from_binary(binary, operator, **kw)

    def visit_json_path_getitem_op_binary(self, binary, operator, **kw):
        return self._render_json_extract_from_binary(binary, operator, **kw)

    def visit_sequence(self, seq, **kw):
        return "NEXT VALUE FOR %s" % self.preparer.format_sequence(seq)


class MSSQLStrictCompiler(MSSQLCompiler):
    """A subclass of MSSQLCompiler which disables the usage of bind
    parameters where not allowed natively by MS-SQL.

    A dialect may use this compiler on a platform where native
    binds are used.

    """

    ansi_bind_rules = True

    def visit_in_op_binary(self, binary, operator, **kw):
        kw["literal_execute"] = True
        return "%s IN %s" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def visit_not_in_op_binary(self, binary, operator, **kw):
        kw["literal_execute"] = True
        return "%s NOT IN %s" % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def render_literal_value(self, value, type_):
        """
        For date and datetime values, convert to a string
        format acceptable to MSSQL. That seems to be the
        so-called ODBC canonical date format which looks
        like this:

            yyyy-mm-dd hh:mi:ss.mmm(24h)

        For other data types, call the base class implementation.
        """
        # datetime and date are both subclasses of datetime.date
        if issubclass(type(value), datetime.date):
            # SQL Server wants single quotes around the date string.
            return "'" + str(value) + "'"
        else:
            return super().render_literal_value(value, type_)


class MSDDLCompiler(compiler.DDLCompiler):
    def get_column_specification(self, column, **kwargs):
        colspec = self.preparer.format_column(column)

        # type is not accepted in a computed column
        if column.computed is not None:
            colspec += " " + self.process(column.computed)
        else:
            colspec += " " + self.dialect.type_compiler_instance.process(
                column.type, type_expression=column
            )

        if column.nullable is not None:
            if (
                not column.nullable
                or column.primary_key
                or isinstance(column.default, sa_schema.Sequence)
                or column.autoincrement is True
                or column.identity
            ):
                colspec += " NOT NULL"
            elif column.computed is None:
                # don't specify "NULL" for computed columns
                colspec += " NULL"

        if column.table is None:
            raise exc.CompileError(
                "mssql requires Table-bound columns in order to generate DDL"
            )

        d_opt = column.dialect_options["mssql"]
        start = d_opt["identity_start"]
        increment = d_opt["identity_increment"]
        if start is not None or increment is not None:
            if column.identity:
                raise exc.CompileError(
                    "Cannot specify options 'mssql_identity_start' and/or "
                    "'mssql_identity_increment' while also using the "
                    "'Identity' construct."
                )
            util.warn_deprecated(
                "The dialect options 'mssql_identity_start' and "
                "'mssql_identity_increment' are deprecated. "
                "Use the 'Identity' object instead.",
                "1.4",
            )

        if column.identity:
            colspec += self.process(column.identity, **kwargs)
        elif (
            column is column.table._autoincrement_column or column.autoincrement is True
        ) and (not isinstance(column.default, Sequence) or column.default.optional):
            colspec += self.process(Identity(start=start, increment=increment))
        else:
            default = self.get_column_default_string(column)
            if default is not None:
                colspec += " DEFAULT " + default

        return colspec

    def visit_create_index(self, create, include_schema=False, **kw):
        index = create.element
        self._verify_index_table(index)
        preparer = self.preparer
        text = "CREATE "
        if index.unique:
            text += "UNIQUE "

        # handle clustering option
        clustered = index.dialect_options["mssql"]["clustered"]
        if clustered is not None:
            if clustered:
                text += "CLUSTERED "
            else:
                text += "NONCLUSTERED "

        # handle columnstore option (has no negative value)
        columnstore = index.dialect_options["mssql"]["columnstore"]
        if columnstore:
            text += "COLUMNSTORE "

        text += "INDEX %s ON %s" % (
            self._prepared_index_name(index, include_schema=include_schema),
            preparer.format_table(index.table),
        )

        # in some case mssql allows indexes with no columns defined
        if len(index.expressions) > 0:
            text += " (%s)" % ", ".join(
                self.sql_compiler.process(expr, include_table=False, literal_binds=True)
                for expr in index.expressions
            )

        # handle other included columns
        if index.dialect_options["mssql"]["include"]:
            inclusions = [
                index.table.c[col] if isinstance(col, str) else col
                for col in index.dialect_options["mssql"]["include"]
            ]

            text += " INCLUDE (%s)" % ", ".join(
                [preparer.quote(c.name) for c in inclusions]
            )

        whereclause = index.dialect_options["mssql"]["where"]

        if whereclause is not None:
            whereclause = coercions.expect(roles.DDLExpressionRole, whereclause)

            where_compiled = self.sql_compiler.process(
                whereclause, include_table=False, literal_binds=True
            )
            text += " WHERE " + where_compiled

        return text

    def visit_drop_index(self, drop, **kw):
        return "\nDROP INDEX %s ON %s" % (
            self._prepared_index_name(drop.element, include_schema=False),
            self.preparer.format_table(drop.element.table),
        )

    def visit_primary_key_constraint(self, constraint, **kw):
        if len(constraint) == 0:
            return ""
        text = ""
        if constraint.name is not None:
            text += "CONSTRAINT %s " % self.preparer.format_constraint(constraint)
        text += "PRIMARY KEY "

        clustered = constraint.dialect_options["mssql"]["clustered"]
        if clustered is not None:
            if clustered:
                text += "CLUSTERED "
            else:
                text += "NONCLUSTERED "

        text += "(%s)" % ", ".join(self.preparer.quote(c.name) for c in constraint)
        text += self.define_constraint_deferrability(constraint)
        return text

    def visit_unique_constraint(self, constraint, **kw):
        if len(constraint) == 0:
            return ""
        text = ""
        if constraint.name is not None:
            formatted_name = self.preparer.format_constraint(constraint)
            if formatted_name is not None:
                text += "CONSTRAINT %s " % formatted_name
        text += "UNIQUE %s" % self.define_unique_constraint_distinct(constraint, **kw)
        clustered = constraint.dialect_options["mssql"]["clustered"]
        if clustered is not None:
            if clustered:
                text += "CLUSTERED "
            else:
                text += "NONCLUSTERED "

        text += "(%s)" % ", ".join(self.preparer.quote(c.name) for c in constraint)
        text += self.define_constraint_deferrability(constraint)
        return text

    def visit_computed_column(self, generated, **kw):
        text = "AS (%s)" % self.sql_compiler.process(
            generated.sqltext, include_table=False, literal_binds=True
        )
        # explicitly check for True|False since None means server default
        if generated.persisted is True:
            text += " PERSISTED"
        return text

    def visit_set_table_comment(self, create, **kw):
        schema = self.preparer.schema_for_object(create.element)
        schema_name = schema if schema else self.dialect.default_schema_name
        return (
            "execute sp_addextendedproperty 'MS_Description', "
            "{}, 'schema', {}, 'table', {}".format(
                self.sql_compiler.render_literal_value(
                    create.element.comment, sqltypes.NVARCHAR()
                ),
                self.preparer.quote_schema(schema_name),
                self.preparer.format_table(create.element, use_schema=False),
            )
        )

    def visit_drop_table_comment(self, drop, **kw):
        schema = self.preparer.schema_for_object(drop.element)
        schema_name = schema if schema else self.dialect.default_schema_name
        return (
            "execute sp_dropextendedproperty 'MS_Description', 'schema', "
            "{}, 'table', {}".format(
                self.preparer.quote_schema(schema_name),
                self.preparer.format_table(drop.element, use_schema=False),
            )
        )

    def visit_set_column_comment(self, create, **kw):
        schema = self.preparer.schema_for_object(create.element.table)
        schema_name = schema if schema else self.dialect.default_schema_name
        return (
            "execute sp_addextendedproperty 'MS_Description', "
            "{}, 'schema', {}, 'table', {}, 'column', {}".format(
                self.sql_compiler.render_literal_value(
                    create.element.comment, sqltypes.NVARCHAR()
                ),
                self.preparer.quote_schema(schema_name),
                self.preparer.format_table(create.element.table, use_schema=False),
                self.preparer.format_column(create.element),
            )
        )

    def visit_drop_column_comment(self, drop, **kw):
        schema = self.preparer.schema_for_object(drop.element.table)
        schema_name = schema if schema else self.dialect.default_schema_name
        return (
            "execute sp_dropextendedproperty 'MS_Description', 'schema', "
            "{}, 'table', {}, 'column', {}".format(
                self.preparer.quote_schema(schema_name),
                self.preparer.format_table(drop.element.table, use_schema=False),
                self.preparer.format_column(drop.element),
            )
        )

    def visit_create_sequence(self, create, **kw):
        prefix = None
        if create.element.data_type is not None:
            data_type = create.element.data_type
            prefix = " AS %s" % self.type_compiler.process(data_type)
        return super().visit_create_sequence(create, prefix=prefix, **kw)

    def visit_identity_column(self, identity, **kw):
        text = " IDENTITY"
        if identity.start is not None or identity.increment is not None:
            start = 1 if identity.start is None else identity.start
            increment = 1 if identity.increment is None else identity.increment
            text += "(%s,%s)" % (start, increment)
        return text


class MSIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = RESERVED_WORDS

    def __init__(self, dialect):
        super().__init__(
            dialect,
            initial_quote="[",
            final_quote="]",
            quote_case_sensitive_collations=False,
        )

    def _escape_identifier(self, value):
        return value.replace("]", "]]")

    def _unescape_identifier(self, value):
        return value.replace("]]", "]")

    def quote_schema(self, schema):
        """Prepare a quoted table and schema name."""

        dbname, owner = _schema_elements(schema)
        if dbname:
            result = "%s.%s" % (self.quote(dbname), self.quote(owner))
        elif owner:
            result = self.quote(owner)
        else:
            result = ""
        return result


def _db_plus_owner_listing(fn):
    def wrap(dialect, connection, schema=None, **kw):
        dbname, owner = _owner_plus_db(dialect, schema)
        return _switch_db(
            dbname,
            connection,
            fn,
            dialect,
            connection,
            dbname,
            owner,
            schema,
            **kw,
        )

    return update_wrapper(wrap, fn)


def _db_plus_owner(fn):
    def wrap(dialect, connection, tablename, schema=None, **kw):
        dbname, owner = _owner_plus_db(dialect, schema)
        return _switch_db(
            dbname,
            connection,
            fn,
            dialect,
            connection,
            tablename,
            dbname,
            owner,
            schema,
            **kw,
        )

    return update_wrapper(wrap, fn)


def _switch_db(dbname, connection, fn, *arg, **kw):
    if dbname:
        current_db = connection.exec_driver_sql("select db_name()").scalar()
        if current_db != dbname:
            connection.exec_driver_sql(
                "use %s" % connection.dialect.identifier_preparer.quote(dbname)
            )
    try:
        return fn(*arg, **kw)
    finally:
        if dbname and current_db != dbname:
            connection.exec_driver_sql(
                "use %s" % connection.dialect.identifier_preparer.quote(current_db)
            )


def _owner_plus_db(dialect, schema):
    if not schema:
        return None, dialect.default_schema_name
    else:
        return _schema_elements(schema)


_memoized_schema = util.LRUCache()


def _schema_elements(schema):
    if isinstance(schema, quoted_name) and schema.quote:
        return None, schema

    if schema in _memoized_schema:
        return _memoized_schema[schema]

    # tests for this function are in:
    # test/dialect/mssql/test_reflection.py ->
    #           OwnerPlusDBTest.test_owner_database_pairs
    # test/dialect/mssql/test_compiler.py -> test_force_schema_*
    # test/dialect/mssql/test_compiler.py -> test_schema_many_tokens_*
    #

    if schema.startswith("__[SCHEMA_"):
        return None, schema

    push = []
    symbol = ""
    bracket = False
    has_brackets = False
    for token in re.split(r"(\[|\]|\.)", schema):
        if not token:
            continue
        if token == "[":
            bracket = True
            has_brackets = True
        elif token == "]":
            bracket = False
        elif not bracket and token == ".":
            if has_brackets:
                push.append("[%s]" % symbol)
            else:
                push.append(symbol)
            symbol = ""
            has_brackets = False
        else:
            symbol += token
    if symbol:
        push.append(symbol)
    if len(push) > 1:
        dbname, owner = ".".join(push[0:-1]), push[-1]

        # test for internal brackets
        if re.match(r".*\].*\[.*", dbname[1:-1]):
            dbname = quoted_name(dbname, quote=False)
        else:
            dbname = dbname.lstrip("[").rstrip("]")

    elif len(push):
        dbname, owner = None, push[0]
    else:
        dbname, owner = None, None

    _memoized_schema[schema] = dbname, owner
    return dbname, owner


class MSDialect(default.DefaultDialect):
    # will assume it's at least mssql2005
    name = "mssql"
    supports_statement_cache = True
    supports_default_values = True
    supports_empty_insert = False
    favor_returning_over_lastrowid = True

    returns_native_bytes = True

    supports_comments = True
    supports_default_metavalue = False
    """dialect supports INSERT... VALUES (DEFAULT) syntax -
    SQL Server **does** support this, but **not** for the IDENTITY column,
    so we can't turn this on.

    """

    # supports_native_uuid is partial here, so we implement our
    # own impl type

    execution_ctx_cls = MSExecutionContext
    use_scope_identity = True
    max_identifier_length = 128
    schema_name = "dbo"

    insert_returning = True
    update_returning = True
    delete_returning = True
    update_returning_multifrom = True
    delete_returning_multifrom = True

    colspecs = {
        sqltypes.DateTime: _MSDateTime,
        sqltypes.Date: _MSDate,
        sqltypes.JSON: JSON,
        sqltypes.JSON.JSONIndexType: JSONIndexType,
        sqltypes.JSON.JSONPathType: JSONPathType,
        sqltypes.Time: _BASETIMEIMPL,
        sqltypes.Unicode: _MSUnicode,
        sqltypes.UnicodeText: _MSUnicodeText,
        DATETIMEOFFSET: DATETIMEOFFSET,
        DATETIME2: DATETIME2,
        SMALLDATETIME: SMALLDATETIME,
        DATETIME: DATETIME,
        sqltypes.Uuid: MSUUid,
    }

    engine_config_types = default.DefaultDialect.engine_config_types.union(
        {"legacy_schema_aliasing": util.asbool}
    )

    ischema_names = ischema_names

    supports_sequences = True
    sequences_optional = True
    # This is actually used for autoincrement, where itentity is used that
    # starts with 1.
    # for sequences T-SQL's actual default is -9223372036854775808
    default_sequence_base = 1

    supports_native_boolean = False
    non_native_boolean_check_constraint = False
    supports_unicode_binds = True
    postfetch_lastrowid = True

    # may be changed at server inspection time for older SQL server versions
    supports_multivalues_insert = True

    use_insertmanyvalues = True

    # note pyodbc will set this to False if fast_executemany is set,
    # as of SQLAlchemy 2.0.9
    use_insertmanyvalues_wo_returning = True

    insertmanyvalues_implicit_sentinel = (
        InsertmanyvaluesSentinelOpts.AUTOINCREMENT
        | InsertmanyvaluesSentinelOpts.IDENTITY
        | InsertmanyvaluesSentinelOpts.USE_INSERT_FROM_SELECT
    )

    # "The incoming request has too many parameters. The server supports a "
    # "maximum of 2100 parameters."
    # in fact you can have 2099 parameters.
    insertmanyvalues_max_parameters = 2099

    _supports_offset_fetch = False
    _supports_nvarchar_max = False

    legacy_schema_aliasing = False

    server_version_info = ()

    statement_compiler = MSSQLCompiler
    ddl_compiler = MSDDLCompiler
    type_compiler_cls = MSTypeCompiler
    preparer = MSIdentifierPreparer

    construct_arguments = [
        (sa_schema.PrimaryKeyConstraint, {"clustered": None}),
        (sa_schema.UniqueConstraint, {"clustered": None}),
        (
            sa_schema.Index,
            {
                "clustered": None,
                "include": None,
                "where": None,
                "columnstore": None,
            },
        ),
        (
            sa_schema.Column,
            {"identity_start": None, "identity_increment": None},
        ),
    ]

    def __init__(
        self,
        query_timeout=None,
        use_scope_identity=True,
        schema_name="dbo",
        deprecate_large_types=None,
        supports_comments=None,
        json_serializer=None,
        json_deserializer=None,
        legacy_schema_aliasing=None,
        ignore_no_transaction_on_rollback=False,
        **opts,
    ):
        self.query_timeout = int(query_timeout or 0)
        self.schema_name = schema_name

        self.use_scope_identity = use_scope_identity
        self.deprecate_large_types = deprecate_large_types
        self.ignore_no_transaction_on_rollback = ignore_no_transaction_on_rollback
        self._user_defined_supports_comments = uds = supports_comments
        if uds is not None:
            self.supports_comments = uds

        if legacy_schema_aliasing is not None:
            util.warn_deprecated(
                "The legacy_schema_aliasing parameter is "
                "deprecated and will be removed in a future release.",
                "1.4",
            )
            self.legacy_schema_aliasing = legacy_schema_aliasing

        super().__init__(**opts)

        self._json_serializer = json_serializer
        self._json_deserializer = json_deserializer

    def do_savepoint(self, connection, name):
        # give the DBAPI a push
        connection.exec_driver_sql("IF @@TRANCOUNT = 0 BEGIN TRANSACTION")
        super().do_savepoint(connection, name)

    def do_release_savepoint(self, connection, name):
        # SQL Server does not support RELEASE SAVEPOINT
        pass

    def do_rollback(self, dbapi_connection):
        try:
            super().do_rollback(dbapi_connection)
        except self.dbapi.ProgrammingError as e:
            if self.ignore_no_transaction_on_rollback and re.match(
                r".*\b111214\b", str(e)
            ):
                util.warn(
                    "ProgrammingError 111214 "
                    "'No corresponding transaction found.' "
                    "has been suppressed via "
                    "ignore_no_transaction_on_rollback=True"
                )
            else:
                raise

    _isolation_lookup = {
        "SERIALIZABLE",
        "READ UNCOMMITTED",
        "READ COMMITTED",
        "REPEATABLE READ",
        "SNAPSHOT",
    }

    def get_isolation_level_values(self, dbapi_connection):
        return list(self._isolation_lookup)

    def set_isolation_level(self, dbapi_connection, level):
        cursor = dbapi_connection.cursor()
        cursor.execute(f"SET TRANSACTION ISOLATION LEVEL {level}")
        cursor.close()
        if level == "SNAPSHOT":
            dbapi_connection.commit()

    def get_isolation_level(self, dbapi_connection):
        cursor = dbapi_connection.cursor()
        view_name = "sys.system_views"
        try:
            cursor.execute(
                (
                    "SELECT name FROM {} WHERE name IN "
                    "('dm_exec_sessions', 'dm_pdw_nodes_exec_sessions')"
                ).format(view_name)
            )
            row = cursor.fetchone()
            if not row:
                raise NotImplementedError(
                    "Can't fetch isolation level on this particular SQL Server version."
                )

            view_name = f"sys.{row[0]}"

            cursor.execute(
                """
                    SELECT CASE transaction_isolation_level
                    WHEN 0 THEN NULL
                    WHEN 1 THEN 'READ UNCOMMITTED'
                    WHEN 2 THEN 'READ COMMITTED'
                    WHEN 3 THEN 'REPEATABLE READ'
                    WHEN 4 THEN 'SERIALIZABLE'
                    WHEN 5 THEN 'SNAPSHOT' END
                    AS TRANSACTION_ISOLATION_LEVEL
                    FROM {}
                    where session_id = @@SPID
                """.format(view_name)
            )
        except self.dbapi.Error as err:
            raise NotImplementedError(
                "Can't fetch isolation level;  encountered error {} when "
                'attempting to query the "{}" view.'.format(err, view_name)
            ) from err
        else:
            row = cursor.fetchone()
            return row[0].upper()
        finally:
            cursor.close()

    def initialize(self, connection):
        super().initialize(connection)
        self._setup_version_attributes()
        self._setup_supports_nvarchar_max(connection)
        self._setup_supports_comments(connection)

    def _setup_version_attributes(self):
        if self.server_version_info[0] not in list(range(8, 17)):
            util.warn(
                "Unrecognized server version info '%s'.  Some SQL Server "
                "features may not function properly."
                % ".".join(str(x) for x in self.server_version_info)
            )

        if self.server_version_info >= MS_2008_VERSION:
            self.supports_multivalues_insert = True
        else:
            self.supports_multivalues_insert = False

        if self.deprecate_large_types is None:
            self.deprecate_large_types = self.server_version_info >= MS_2012_VERSION

        self._supports_offset_fetch = (
            self.server_version_info and self.server_version_info[0] >= 11
        )

    def _setup_supports_nvarchar_max(self, connection):
        try:
            connection.scalar(
                sql.text("SELECT CAST('test max support' AS NVARCHAR(max))")
            )
        except exc.DBAPIError:
            self._supports_nvarchar_max = False
        else:
            self._supports_nvarchar_max = True

    def _setup_supports_comments(self, connection):
        if self._user_defined_supports_comments is not None:
            return

        try:
            connection.scalar(
                sql.text(
                    "SELECT 1 FROM fn_listextendedproperty"
                    "(default, default, default, default, "
                    "default, default, default)"
                )
            )
        except exc.DBAPIError:
            self.supports_comments = False
        else:
            self.supports_comments = True

    def _get_default_schema_name(self, connection):
        query = sql.text("SELECT schema_name()")
        default_schema_name = connection.scalar(query)
        if default_schema_name is not None:
            # guard against the case where the default_schema_name is being
            # fed back into a table reflection function.
            return quoted_name(default_schema_name, quote=True)
        else:
            return self.schema_name

    @_db_plus_owner
    def has_table(self, connection, tablename, dbname, owner, schema, **kw):
        self._ensure_has_table_connection(connection)

        return self._internal_has_table(connection, tablename, owner, **kw)

    @reflection.cache
    @_db_plus_owner
    def has_sequence(self, connection, sequencename, dbname, owner, schema, **kw):
        sequences = ischema.sequences

        s = sql.select(sequences.c.sequence_name).where(
            sequences.c.sequence_name == sequencename
        )

        if owner:
            s = s.where(sequences.c.sequence_schema == owner)

        c = connection.execute(s)

        return c.first() is not None

    @reflection.cache
    @_db_plus_owner_listing
    def get_sequence_names(self, connection, dbname, owner, schema, **kw):
        sequences = ischema.sequences

        s = sql.select(sequences.c.sequence_name)
        if owner:
            s = s.where(sequences.c.sequence_schema == owner)

        c = connection.execute(s)

        return [row[0] for row in c]

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        s = sql.select(ischema.schemata.c.schema_name).order_by(
            ischema.schemata.c.schema_name
        )
        schema_names = [r[0] for r in connection.execute(s)]
        return schema_names

    @reflection.cache
    @_db_plus_owner_listing
    def get_table_names(self, connection, dbname, owner, schema, **kw):
        tables = ischema.tables
        s = (
            sql.select(tables.c.table_name)
            .where(
                sql.and_(
                    tables.c.table_schema == owner,
                    tables.c.table_type == "BASE TABLE",
                )
            )
            .order_by(tables.c.table_name)
        )
        table_names = [r[0] for r in connection.execute(s)]
        return table_names

    @reflection.cache
    @_db_plus_owner_listing
    def get_view_names(self, connection, dbname, owner, schema, **kw):
        tables = ischema.tables
        s = (
            sql.select(tables.c.table_name)
            .where(
                sql.and_(
                    tables.c.table_schema == owner,
                    tables.c.table_type == "VIEW",
                )
            )
            .order_by(tables.c.table_name)
        )
        view_names = [r[0] for r in connection.execute(s)]
        return view_names

    @reflection.cache
    def _internal_has_table(self, connection, tablename, owner, **kw):
        if tablename.startswith("#"):  # temporary table
            # mssql does not support temporary views
            # SQL Error [4103] [S0001]: "#v": Temporary views are not allowed
            return bool(
                connection.scalar(
                    # U filters on user tables only.
                    text("SELECT object_id(:table_name, 'U')"),
                    {"table_name": f"tempdb.dbo.[{tablename}]"},
                )
            )
        else:
            tables = ischema.tables

            s = sql.select(tables.c.table_name).where(
                sql.and_(
                    sql.or_(
                        tables.c.table_type == "BASE TABLE",
                        tables.c.table_type == "VIEW",
                    ),
                    tables.c.table_name == tablename,
                )
            )

            if owner:
                s = s.where(tables.c.table_schema == owner)

            c = connection.execute(s)

            return c.first() is not None

    def _default_or_error(self, connection, tablename, owner, method, **kw):
        # TODO: try to avoid having to run a separate query here
        if self._internal_has_table(connection, tablename, owner, **kw):
            return method()
        else:
            raise exc.NoSuchTableError(f"{owner}.{tablename}")

    @reflection.cache
    @_db_plus_owner
    def get_indexes(self, connection, tablename, dbname, owner, schema, **kw):
        filter_definition = (
            "ind.filter_definition"
            if self.server_version_info >= MS_2008_VERSION
            else "NULL as filter_definition"
        )
        rp = connection.execution_options(future_result=True).execute(
            sql.text(
                f"""
select
    ind.index_id,
    ind.is_unique,
    ind.name,
    ind.type,
    {filter_definition}
from
    sys.indexes as ind
join sys.tables as tab on
    ind.object_id = tab.object_id
join sys.schemas as sch on
    sch.schema_id = tab.schema_id
where
    tab.name = :tabname
    and sch.name = :schname
    and ind.is_primary_key = 0
    and ind.type != 0
order by
    ind.name
                """
            )
            .bindparams(
                sql.bindparam("tabname", tablename, ischema.CoerceUnicode()),
                sql.bindparam("schname", owner, ischema.CoerceUnicode()),
            )
            .columns(name=sqltypes.Unicode())
        )
        indexes = {}
        for row in rp.mappings():
            indexes[row["index_id"]] = current = {
                "name": row["name"],
                "unique": row["is_unique"] == 1,
                "column_names": [],
                "include_columns": [],
                "dialect_options": {},
            }

            do = current["dialect_options"]
            index_type = row["type"]
            if index_type in {1, 2}:
                do["mssql_clustered"] = index_type == 1
            if index_type in {5, 6}:
                do["mssql_clustered"] = index_type == 5
                do["mssql_columnstore"] = True
            if row["filter_definition"] is not None:
                do["mssql_where"] = row["filter_definition"]

        rp = connection.execution_options(future_result=True).execute(
            sql.text(
                """
select
    ind_col.index_id,
    col.name,
    ind_col.is_included_column
from
    sys.columns as col
join sys.tables as tab on
    tab.object_id = col.object_id
join sys.index_columns as ind_col on
    ind_col.column_id = col.column_id
    and ind_col.object_id = tab.object_id
join sys.schemas as sch on
    sch.schema_id = tab.schema_id
where
    tab.name = :tabname
    and sch.name = :schname
            """
            )
            .bindparams(
                sql.bindparam("tabname", tablename, ischema.CoerceUnicode()),
                sql.bindparam("schname", owner, ischema.CoerceUnicode()),
            )
            .columns(name=sqltypes.Unicode())
        )
        for row in rp.mappings():
            if row["index_id"] not in indexes:
                continue
            index_def = indexes[row["index_id"]]
            is_colstore = index_def["dialect_options"].get("mssql_columnstore")
            is_clustered = index_def["dialect_options"].get("mssql_clustered")
            if not (is_colstore and is_clustered):
                # a clustered columnstore index includes all columns but does
                # not want them in the index definition
                if row["is_included_column"] and not is_colstore:
                    # a noncludsted columnstore index reports that includes
                    # columns but requires that are listed as normal columns
                    index_def["include_columns"].append(row["name"])
                else:
                    index_def["column_names"].append(row["name"])
        for index_info in indexes.values():
            # NOTE: "root level" include_columns is legacy, now part of
            #       dialect_options (issue #7382)
            index_info["dialect_options"]["mssql_include"] = index_info[
                "include_columns"
            ]

        if indexes:
            return list(indexes.values())
        else:
            return self._default_or_error(
                connection, tablename, owner, ReflectionDefaults.indexes, **kw
            )

    @reflection.cache
    @_db_plus_owner
    def get_view_definition(self, connection, viewname, dbname, owner, schema, **kw):
        view_def = connection.execute(
            sql.text(
                "select mod.definition "
                "from sys.sql_modules as mod "
                "join sys.views as views on mod.object_id = views.object_id "
                "join sys.schemas as sch on views.schema_id = sch.schema_id "
                "where views.name=:viewname and sch.name=:schname"
            ).bindparams(
                sql.bindparam("viewname", viewname, ischema.CoerceUnicode()),
                sql.bindparam("schname", owner, ischema.CoerceUnicode()),
            )
        ).scalar()
        if view_def:
            return view_def
        else:
            raise exc.NoSuchTableError(f"{owner}.{viewname}")

    @reflection.cache
    def get_table_comment(self, connection, table_name, schema=None, **kw):
        if not self.supports_comments:
            raise NotImplementedError(
                "Can't get table comments on current SQL Server version in use"
            )

        schema_name = schema if schema else self.default_schema_name
        COMMENT_SQL = """
            SELECT cast(com.value as nvarchar(max))
            FROM fn_listextendedproperty('MS_Description',
                'schema', :schema, 'table', :table, NULL, NULL
            ) as com;
        """

        comment = connection.execute(
            sql.text(COMMENT_SQL).bindparams(
                sql.bindparam("schema", schema_name, ischema.CoerceUnicode()),
                sql.bindparam("table", table_name, ischema.CoerceUnicode()),
            )
        ).scalar()
        if comment:
            return {"text": comment}
        else:
            return self._default_or_error(
                connection,
                table_name,
                None,
                ReflectionDefaults.table_comment,
                **kw,
            )

    def _temp_table_name_like_pattern(self, tablename):
        # LIKE uses '%' to match zero or more characters and '_' to match any
        # single character. We want to match literal underscores, so T-SQL
        # requires that we enclose them in square brackets.
        return tablename + (("[_][_][_]%") if not tablename.startswith("##") else "")

    def _get_internal_temp_table_name(self, connection, tablename):
        # it's likely that schema is always "dbo", but since we can
        # get it here, let's get it.
        # see https://stackoverflow.com/questions/8311959/
        # specifying-schema-for-temporary-tables

        try:
            return connection.execute(
                sql.text(
                    "select table_schema, table_name "
                    "from tempdb.information_schema.tables "
                    "where table_name like :p1"
                ),
                {"p1": self._temp_table_name_like_pattern(tablename)},
            ).one()
        except exc.MultipleResultsFound as me:
            raise exc.UnreflectableTableError(
                "Found more than one temporary table named '%s' in tempdb "
                "at this time. Cannot reliably resolve that name to its "
                "internal table name." % tablename
            ) from me
        except exc.NoResultFound as ne:
            raise exc.NoSuchTableError(
                "Unable to find a temporary table named '%s' in tempdb." % tablename
            ) from ne

    @reflection.cache
    @_db_plus_owner
    def get_columns(self, connection, tablename, dbname, owner, schema, **kw):
        is_temp_table = tablename.startswith("#")
        if is_temp_table:
            owner, tablename = self._get_internal_temp_table_name(connection, tablename)

            columns = ischema.mssql_temp_table_columns
        else:
            columns = ischema.columns

        computed_cols = ischema.computed_columns
        identity_cols = ischema.identity_columns
        if owner:
            whereclause = sql.and_(
                columns.c.table_name == tablename,
                columns.c.table_schema == owner,
            )
            full_name = columns.c.table_schema + "." + columns.c.table_name
        else:
            whereclause = columns.c.table_name == tablename
            full_name = columns.c.table_name

        if self._supports_nvarchar_max:
            computed_definition = computed_cols.c.definition
        else:
            # tds_version 4.2 does not support NVARCHAR(MAX)
            computed_definition = sql.cast(computed_cols.c.definition, NVARCHAR(4000))

        object_id = func.object_id(full_name)

        s = (
            sql.select(
                columns.c.column_name,
                columns.c.data_type,
                columns.c.is_nullable,
                columns.c.character_maximum_length,
                columns.c.numeric_precision,
                columns.c.numeric_scale,
                columns.c.column_default,
                columns.c.collation_name,
                computed_definition,
                computed_cols.c.is_persisted,
                identity_cols.c.is_identity,
                identity_cols.c.seed_value,
                identity_cols.c.increment_value,
                ischema.extended_properties.c.value.label("comment"),
            )
            .select_from(columns)
            .outerjoin(
                computed_cols,
                onclause=sql.and_(
                    computed_cols.c.object_id == object_id,
                    computed_cols.c.name
                    == columns.c.column_name.collate("DATABASE_DEFAULT"),
                ),
            )
            .outerjoin(
                identity_cols,
                onclause=sql.and_(
                    identity_cols.c.object_id == object_id,
                    identity_cols.c.name
                    == columns.c.column_name.collate("DATABASE_DEFAULT"),
                ),
            )
            .outerjoin(
                ischema.extended_properties,
                onclause=sql.and_(
                    ischema.extended_properties.c["class"] == 1,
                    ischema.extended_properties.c.major_id == object_id,
                    ischema.extended_properties.c.minor_id
                    == columns.c.ordinal_position,
                    ischema.extended_properties.c.name == "MS_Description",
                ),
            )
            .where(whereclause)
            .order_by(columns.c.ordinal_position)
        )

        c = connection.execution_options(future_result=True).execute(s)

        cols = []
        for row in c.mappings():
            name = row[columns.c.column_name]
            type_ = row[columns.c.data_type]
            nullable = row[columns.c.is_nullable] == "YES"
            charlen = row[columns.c.character_maximum_length]
            numericprec = row[columns.c.numeric_precision]
            numericscale = row[columns.c.numeric_scale]
            default = row[columns.c.column_default]
            collation = row[columns.c.collation_name]
            definition = row[computed_definition]
            is_persisted = row[computed_cols.c.is_persisted]
            is_identity = row[identity_cols.c.is_identity]
            identity_start = row[identity_cols.c.seed_value]
            identity_increment = row[identity_cols.c.increment_value]
            comment = row[ischema.extended_properties.c.value]

            coltype = self.ischema_names.get(type_, None)

            kwargs = {}
            if coltype in (
                MSString,
                MSChar,
                MSNVarchar,
                MSNChar,
                MSText,
                MSNText,
                MSBinary,
                MSVarBinary,
                sqltypes.LargeBinary,
            ):
                if charlen == -1:
                    charlen = None
                kwargs["length"] = charlen
                if collation:
                    kwargs["collation"] = collation

            if coltype is None:
                util.warn("Did not recognize type '%s' of column '%s'" % (type_, name))
                coltype = sqltypes.NULLTYPE
            else:
                if issubclass(coltype, sqltypes.NumericCommon):
                    kwargs["precision"] = numericprec

                    if not issubclass(coltype, sqltypes.Float):
                        kwargs["scale"] = numericscale

                coltype = coltype(**kwargs)
            cdict = {
                "name": name,
                "type": coltype,
                "nullable": nullable,
                "default": default,
                "autoincrement": is_identity is not None,
                "comment": comment,
            }

            if definition is not None and is_persisted is not None:
                cdict["computed"] = {
                    "sqltext": definition,
                    "persisted": is_persisted,
                }

            if is_identity is not None:
                # identity_start and identity_increment are Decimal or None
                if identity_start is None or identity_increment is None:
                    cdict["identity"] = {}
                else:
                    if isinstance(coltype, sqltypes.BigInteger):
                        start = int(identity_start)
                        increment = int(identity_increment)
                    elif isinstance(coltype, sqltypes.Integer):
                        start = int(identity_start)
                        increment = int(identity_increment)
                    else:
                        start = identity_start
                        increment = identity_increment

                    cdict["identity"] = {
                        "start": start,
                        "increment": increment,
                    }

            cols.append(cdict)

        if cols:
            return cols
        else:
            return self._default_or_error(
                connection, tablename, owner, ReflectionDefaults.columns, **kw
            )

    @reflection.cache
    @_db_plus_owner
    def get_pk_constraint(self, connection, tablename, dbname, owner, schema, **kw):
        pkeys = []
        TC = ischema.constraints
        C = ischema.key_constraints.alias("C")

        # Primary key constraints
        s = (
            sql.select(
                C.c.column_name,
                TC.c.constraint_type,
                C.c.constraint_name,
                func.objectproperty(
                    func.object_id(C.c.table_schema + "." + C.c.constraint_name),
                    "CnstIsClustKey",
                ).label("is_clustered"),
            )
            .where(
                sql.and_(
                    TC.c.constraint_name == C.c.constraint_name,
                    TC.c.table_schema == C.c.table_schema,
                    C.c.table_name == tablename,
                    C.c.table_schema == owner,
                ),
            )
            .order_by(TC.c.constraint_name, C.c.ordinal_position)
        )
        c = connection.execution_options(future_result=True).execute(s)
        constraint_name = None
        is_clustered = None
        for row in c.mappings():
            if "PRIMARY" in row[TC.c.constraint_type.name]:
                pkeys.append(row["COLUMN_NAME"])
                if constraint_name is None:
                    constraint_name = row[C.c.constraint_name.name]
                if is_clustered is None:
                    is_clustered = row["is_clustered"]
        if pkeys:
            return {
                "constrained_columns": pkeys,
                "name": constraint_name,
                "dialect_options": {"mssql_clustered": is_clustered},
            }
        else:
            return self._default_or_error(
                connection,
                tablename,
                owner,
                ReflectionDefaults.pk_constraint,
                **kw,
            )

    @reflection.cache
    @_db_plus_owner
    def get_foreign_keys(self, connection, tablename, dbname, owner, schema, **kw):
        # Foreign key constraints
        s = (
            text(
                """\
WITH fk_info AS (
    SELECT
        ischema_ref_con.constraint_schema,
        ischema_ref_con.constraint_name,
        ischema_key_col.ordinal_position,
        ischema_key_col.table_schema,
        ischema_key_col.table_name,
        ischema_ref_con.unique_constraint_schema,
        ischema_ref_con.unique_constraint_name,
        ischema_ref_con.match_option,
        ischema_ref_con.update_rule,
        ischema_ref_con.delete_rule,
        ischema_key_col.column_name AS constrained_column
    FROM
        INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS ischema_ref_con
        INNER JOIN
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE ischema_key_col ON
            ischema_key_col.table_schema = ischema_ref_con.constraint_schema
            AND ischema_key_col.constraint_name =
            ischema_ref_con.constraint_name
    WHERE ischema_key_col.table_name = :tablename
        AND ischema_key_col.table_schema = :owner
),
constraint_info AS (
    SELECT
        ischema_key_col.constraint_schema,
        ischema_key_col.constraint_name,
        ischema_key_col.ordinal_position,
        ischema_key_col.table_schema,
        ischema_key_col.table_name,
        ischema_key_col.column_name
    FROM
        INFORMATION_SCHEMA.KEY_COLUMN_USAGE ischema_key_col
),
index_info AS (
    SELECT
        sys.schemas.name AS index_schema,
        sys.indexes.name AS index_name,
        sys.index_columns.key_ordinal AS ordinal_position,
        sys.schemas.name AS table_schema,
        sys.objects.name AS table_name,
        sys.columns.name AS column_name
    FROM
        sys.indexes
        INNER JOIN
        sys.objects ON
            sys.objects.object_id = sys.indexes.object_id
        INNER JOIN
        sys.schemas ON
            sys.schemas.schema_id = sys.objects.schema_id
        INNER JOIN
        sys.index_columns ON
            sys.index_columns.object_id = sys.objects.object_id
            AND sys.index_columns.index_id = sys.indexes.index_id
        INNER JOIN
        sys.columns ON
            sys.columns.object_id = sys.indexes.object_id
            AND sys.columns.column_id = sys.index_columns.column_id
)
    SELECT
        fk_info.constraint_schema,
        fk_info.constraint_name,
        fk_info.ordinal_position,
        fk_info.constrained_column,
        constraint_info.table_schema AS referred_table_schema,
        constraint_info.table_name AS referred_table_name,
        constraint_info.column_name AS referred_column,
        fk_info.match_option,
        fk_info.update_rule,
        fk_info.delete_rule
    FROM
        fk_info INNER JOIN constraint_info ON
            constraint_info.constraint_schema =
                fk_info.unique_constraint_schema
            AND constraint_info.constraint_name =
                fk_info.unique_constraint_name
            AND constraint_info.ordinal_position = fk_info.ordinal_position
    UNION
    SELECT
        fk_info.constraint_schema,
        fk_info.constraint_name,
        fk_info.ordinal_position,
        fk_info.constrained_column,
        index_info.table_schema AS referred_table_schema,
        index_info.table_name AS referred_table_name,
        index_info.column_name AS referred_column,
        fk_info.match_option,
        fk_info.update_rule,
        fk_info.delete_rule
    FROM
        fk_info INNER JOIN index_info ON
            index_info.index_schema = fk_info.unique_constraint_schema
            AND index_info.index_name = fk_info.unique_constraint_name
            AND index_info.ordinal_position = fk_info.ordinal_position

    ORDER BY fk_info.constraint_schema, fk_info.constraint_name,
        fk_info.ordinal_position
"""
            )
            .bindparams(
                sql.bindparam("tablename", tablename, ischema.CoerceUnicode()),
                sql.bindparam("owner", owner, ischema.CoerceUnicode()),
            )
            .columns(
                constraint_schema=sqltypes.Unicode(),
                constraint_name=sqltypes.Unicode(),
                table_schema=sqltypes.Unicode(),
                table_name=sqltypes.Unicode(),
                constrained_column=sqltypes.Unicode(),
                referred_table_schema=sqltypes.Unicode(),
                referred_table_name=sqltypes.Unicode(),
                referred_column=sqltypes.Unicode(),
            )
        )

        # group rows by constraint ID, to handle multi-column FKs
        fkeys = []

        def fkey_rec():
            return {
                "name": None,
                "constrained_columns": [],
                "referred_schema": None,
                "referred_table": None,
                "referred_columns": [],
                "options": {},
            }

        fkeys = util.defaultdict(fkey_rec)

        for r in connection.execute(s).all():
            (
                _,  # constraint schema
                rfknm,
                _,  # ordinal position
                scol,
                rschema,
                rtbl,
                rcol,
                # TODO: we support match=<keyword> for foreign keys so
                # we can support this also, PG has match=FULL for example
                # but this seems to not be a valid value for SQL Server
                _,  # match rule
                fkuprule,
                fkdelrule,
            ) = r

            rec = fkeys[rfknm]
            rec["name"] = rfknm

            if fkuprule != "NO ACTION":
                rec["options"]["onupdate"] = fkuprule

            if fkdelrule != "NO ACTION":
                rec["options"]["ondelete"] = fkdelrule

            if not rec["referred_table"]:
                rec["referred_table"] = rtbl
                if schema is not None or owner != rschema:
                    if dbname:
                        rschema = dbname + "." + rschema
                    rec["referred_schema"] = rschema

            local_cols, remote_cols = (
                rec["constrained_columns"],
                rec["referred_columns"],
            )

            local_cols.append(scol)
            remote_cols.append(rcol)

        if fkeys:
            return list(fkeys.values())
        else:
            return self._default_or_error(
                connection,
                tablename,
                owner,
                ReflectionDefaults.foreign_keys,
                **kw,
            )
