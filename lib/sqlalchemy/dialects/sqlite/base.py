# dialects/sqlite/base.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors


r'''
.. dialect:: sqlite
    :name: SQLite
    :normal_support: 3.12+
    :best_effort: 3.7.16+

.. _sqlite_datetime:

日期和时间类型
-------------------

Date and Time Types

.. tab:: 中文

    SQLite 不具备内建的 DATE、TIME 或 DATETIME 类型，pysqlite 也不提供开箱即用的功能来在 Python 的 `datetime` 对象与 SQLite 支持的格式之间进行转换。
    SQLAlchemy 提供的 :class:`~sqlalchemy.types.DateTime` 及相关类型在使用 SQLite 时，提供了日期格式化与解析的功能。其具体实现类为 :class:`_sqlite.DATETIME`、:class:`_sqlite.DATE` 与 :class:`_sqlite.TIME`。
    这些类型会将日期和时间表示为 ISO 格式的字符串，这种格式在排序时也表现良好。此机制不依赖于传统的 "libc" 内部函数，因此历史日期也能被完全支持。

.. tab:: 英文

    SQLite does not have built-in DATE, TIME, or DATETIME types, and pysqlite does
    not provide out of the box functionality for translating values between Python
    `datetime` objects and a SQLite-supported format. SQLAlchemy's own
    :class:`~sqlalchemy.types.DateTime` and related types provide date formatting
    and parsing functionality when SQLite is used. The implementation classes are
    :class:`_sqlite.DATETIME`, :class:`_sqlite.DATE` and :class:`_sqlite.TIME`.
    These types represent dates and times as ISO formatted strings, which also
    nicely support ordering. There's no reliance on typical "libc" internals for
    these functions so historical dates are fully supported.

确保文本关联性
^^^^^^^^^^^^^^^^^^^^^^

Ensuring Text affinity

.. tab:: 中文

    这些类型在生成 DDL 时会使用标准的 ``DATE``、``TIME`` 和 ``DATETIME`` 类型标识。然而，也可以为这些类型应用自定义的存储格式。
    当检测到存储格式中不含有字母字符时，这些类型的 DDL 会被渲染为 ``DATE_CHAR``、``TIME_CHAR`` 和 ``DATETIME_CHAR``，
    以确保列依然具有文本关联性（textual affinity）。

    .. seealso::

        `类型关联性（Type Affinity） <https://www.sqlite.org/datatype3.html#affinity>`_ - SQLite 文档中的相关说明

.. tab:: 英文

    The DDL rendered for these types is the standard ``DATE``, ``TIME``
    and ``DATETIME`` indicators.    However, custom storage formats can also be
    applied to these types.   When the
    storage format is detected as containing no alpha characters, the DDL for
    these types is rendered as ``DATE_CHAR``, ``TIME_CHAR``, and ``DATETIME_CHAR``,
    so that the column continues to have textual affinity.

    .. seealso::

        `Type Affinity <https://www.sqlite.org/datatype3.html#affinity>`_ -
        in the SQLite documentation

.. _sqlite_autoincrement:

SQLite 自动递增行为
----------------------------------

SQLite Auto Incrementing Behavior

.. tab:: 中文

    关于 SQLite 自增主键的背景资料参见： https://sqlite.org/autoinc.html

    关键概念：

    * SQLite 拥有一种隐式的 “自动增长” 特性，当某个非复合主键列被定义为 `"INTEGER PRIMARY KEY"` 时，该特性即被启用。

    * SQLite 同时也支持显式的 "AUTOINCREMENT" 关键字，但该关键字 **并不等同于** 上述隐式自动增长机制。
      此关键字通常 **不推荐使用** 。除非使用了 SQLite 特定的参数，SQLAlchemy 默认不会生成该关键字（见下文）。
      但无论如何，若要使用该关键字，仍然要求列的数据类型名称必须是 "INTEGER"。

.. tab:: 英文

    Background on SQLite's autoincrement is at: https://sqlite.org/autoinc.html

    Key concepts:

    * SQLite has an implicit "auto increment" feature that takes place for any
      non-composite primary-key column that is specifically created using
      "INTEGER PRIMARY KEY" for the type + primary key.

    * SQLite also has an explicit "AUTOINCREMENT" keyword, that is **not**
      equivalent to the implicit autoincrement feature; this keyword is not
      recommended for general use.  SQLAlchemy does not render this keyword
      unless a special SQLite-specific directive is used (see below).  However,
      it still requires that the column's type is named "INTEGER".

使用 AUTOINCREMENT 关键字
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the AUTOINCREMENT Keyword

.. tab:: 中文

    若要在生成 DDL 时在主键列上显式添加 AUTOINCREMENT 关键字，可以在 :class:`.Table` 构造中添加 ``sqlite_autoincrement=True`` 标志::

        Table(
            "sometable",
            metadata,
            Column("id", Integer, primary_key=True),
            sqlite_autoincrement=True,
        )

.. tab:: 英文

    To specifically render the AUTOINCREMENT keyword on the primary key column
    when rendering DDL, add the flag ``sqlite_autoincrement=True`` to the Table
    construct::

        Table(
            "sometable",
            metadata,
            Column("id", Integer, primary_key=True),
            sqlite_autoincrement=True,
        )

允许 SQLAlchemy 中除 Integer/INTEGER 之外的其他类型的自动递增行为
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Allowing autoincrement behavior SQLAlchemy types other than Integer/INTEGER

.. tab:: 中文

    SQLite 的类型模型基于命名约定。这意味着，任何包含 ``"INT"`` 子字符串的类型名称都将被认为具有 “integer 关联性”。
    例如，类型 ``"BIGINT"``、``"SPECIAL_INT"``，甚至 ``"XYZINTQPR"``，在 SQLite 中都会被视为 "integer" 关联性类型。
    但需特别注意： **无论使用显式还是隐式的 autoincrement 特性，SQLite 都要求列类型的名称必须** 严格为 ``"INTEGER"``。
    因此，如果应用中主键使用了 :class:`.BigInteger` 类型，在 SQLite 中，为了启用自增功能，该类型在生成 ``CREATE TABLE`` 语句时必须渲染为 ``"INTEGER"``。

    一种实现方式是仅在 SQLite 上使用 :class:`.Integer`，并借助 :meth:`.TypeEngine.with_variant`::

        table = Table(
            "my_table",
            metadata,
            Column(
                "id",
                BigInteger().with_variant(Integer, "sqlite"),
                primary_key=True,
            ),
        )

    另一种方式是自定义一个继承自 :class:`.BigInteger` 的子类，当其针对 SQLite 编译时将类型名称重写为 ``INTEGER``::

        from sqlalchemy import BigInteger
        from sqlalchemy.ext.compiler import compiles


        class SLBigInteger(BigInteger):
            pass


        @compiles(SLBigInteger, "sqlite")
        def bi_c(element, compiler, **kw):
            return "INTEGER"


        @compiles(SLBigInteger)
        def bi_c(element, compiler, **kw):
            return compiler.visit_BIGINT(element, **kw)


        table = Table(
            "my_table", metadata, Column("id", SLBigInteger(), primary_key=True)
        )

    .. seealso::

        :meth:`.TypeEngine.with_variant`

        :ref:`sqlalchemy.ext.compiler_toplevel`

        `SQLite 3 中的数据类型 <https://sqlite.org/datatype3.html>`_

.. tab:: 英文

    SQLite's typing model is based on naming conventions.  Among other things, this
    means that any type name which contains the substring ``"INT"`` will be
    determined to be of "integer affinity".  A type named ``"BIGINT"``,
    ``"SPECIAL_INT"`` or even ``"XYZINTQPR"``, will be considered by SQLite to be
    of "integer" affinity.  However, **the SQLite autoincrement feature, whether
    implicitly or explicitly enabled, requires that the name of the column's type
    is exactly the string "INTEGER"**.  Therefore, if an application uses a type
    like :class:`.BigInteger` for a primary key, on SQLite this type will need to
    be rendered as the name ``"INTEGER"`` when emitting the initial ``CREATE
    TABLE`` statement in order for the autoincrement behavior to be available.

    One approach to achieve this is to use :class:`.Integer` on SQLite
    only using :meth:`.TypeEngine.with_variant`::

        table = Table(
            "my_table",
            metadata,
            Column(
                "id",
                BigInteger().with_variant(Integer, "sqlite"),
                primary_key=True,
            ),
        )

    Another is to use a subclass of :class:`.BigInteger` that overrides its DDL
    name to be ``INTEGER`` when compiled against SQLite::

        from sqlalchemy import BigInteger
        from sqlalchemy.ext.compiler import compiles


        class SLBigInteger(BigInteger):
            pass


        @compiles(SLBigInteger, "sqlite")
        def bi_c(element, compiler, **kw):
            return "INTEGER"


        @compiles(SLBigInteger)
        def bi_c(element, compiler, **kw):
            return compiler.visit_BIGINT(element, **kw)


        table = Table(
            "my_table", metadata, Column("id", SLBigInteger(), primary_key=True)
        )

    .. seealso::

        :meth:`.TypeEngine.with_variant`

        :ref:`sqlalchemy.ext.compiler_toplevel`

        `Datatypes In SQLite Version 3 <https://sqlite.org/datatype3.html>`_

.. _sqlite_concurrency:

数据库锁定行为/并发性
---------------------------------------

Database Locking Behavior / Concurrency

.. tab:: 中文

    SQLite 并非为高并发写操作而设计。由于数据库本质上是一个文件，在事务中的写操作会将该文件完全锁定，意味着在写期间，只有一个 “连接”（本质上是一个文件句柄）拥有对数据库的独占访问权限 ——
    所有其他“连接”在此期间都会被阻塞。

    Python 的 DBAPI 规范也定义了一种始终处于事务中的连接模型；它没有 ``connection.begin()`` 方法，
    只有 ``connection.commit()`` 与 ``connection.rollback()``，调用这些方法后应立即开始一个新事务。
    这似乎暗示 SQLite 驱动理论上在任意时间只允许一个文件句柄访问某个数据库文件；
    但实际上，在 SQLite 自身以及 pysqlite 驱动的多方面因素影响下，这一限制已大大放宽。

    然而，无论采用哪种锁定模式，一旦事务开始并至少执行了一条 DML 语句（如 INSERT、UPDATE、DELETE），SQLite 仍会锁定整个数据库文件，
    此时其他事务在试图执行 DML 时也会被阻塞。默认情况下，该阻塞时间非常短，超时后会报错。

    在配合 SQLAlchemy ORM 使用时，这一行为尤为关键。
    SQLAlchemy 的 :class:`.Session` 对象默认运行在一个事务中，且在启用了自动刷新（autoflush）模式时，可能在任意 SELECT 语句之前就会发出 DML。
    这可能会导致数据库比预期更快地进入锁定状态。虽然可以在一定程度上调整 SQLite 及其 pysqlite 驱动的锁定模式，
    但需注意的是，在 SQLite 中尝试实现高写入并发本就是一场败战。

    如需了解更多关于 SQLite 在设计上不具备写入并发的资料，请参阅官方文档末尾部分：
    `哪些场景下应考虑其他关系型数据库 —— 高并发需求 <https://www.sqlite.org/whentouse.html>`_

    以下各小节将介绍 SQLite 的文件架构所影响的领域，这些领域在使用 pysqlite 驱动时通常需要特殊处理或绕过方案。

.. tab:: 英文

    SQLite is not designed for a high level of write concurrency. The database
    itself, being a file, is locked completely during write operations within
    transactions, meaning exactly one "connection" (in reality a file handle)
    has exclusive access to the database during this period - all other
    "connections" will be blocked during this time.

    The Python DBAPI specification also calls for a connection model that is
    always in a transaction; there is no ``connection.begin()`` method,
    only ``connection.commit()`` and ``connection.rollback()``, upon which a
    new transaction is to be begun immediately.  This may seem to imply
    that the SQLite driver would in theory allow only a single filehandle on a
    particular database file at any time; however, there are several
    factors both within SQLite itself as well as within the pysqlite driver
    which loosen this restriction significantly.

    However, no matter what locking modes are used, SQLite will still always
    lock the database file once a transaction is started and DML (e.g. INSERT,
    UPDATE, DELETE) has at least been emitted, and this will block
    other transactions at least at the point that they also attempt to emit DML.
    By default, the length of time on this block is very short before it times out
    with an error.

    This behavior becomes more critical when used in conjunction with the
    SQLAlchemy ORM.  SQLAlchemy's :class:`.Session` object by default runs
    within a transaction, and with its autoflush model, may emit DML preceding
    any SELECT statement.   This may lead to a SQLite database that locks
    more quickly than is expected.   The locking mode of SQLite and the pysqlite
    driver can be manipulated to some degree, however it should be noted that
    achieving a high degree of write-concurrency with SQLite is a losing battle.

    For more information on SQLite's lack of write concurrency by design, please
    see
    `Situations Where Another RDBMS May Work Better - High Concurrency
    <https://www.sqlite.org/whentouse.html>`_ near the bottom of the page.

    The following subsections introduce areas that are impacted by SQLite's
    file-based architecture and additionally will usually require workarounds to
    work when using the pysqlite driver.

.. _sqlite_isolation_level:

事务隔离级别/自动提交
----------------------------------------

Transaction Isolation Level / Autocommit

.. tab:: 中文

    SQLite 以一种非标准的方式支持“事务隔离”，主要体现在两个方面。其一是
    `PRAGMA read_uncommitted <https://www.sqlite.org/pragma.html#pragma_read_uncommitted>`_
    指令。此设置可在 SQLite 的默认 ``SERIALIZABLE`` 隔离级别与一种通常称为
    ``READ UNCOMMITTED`` 的“脏读”隔离模式之间切换。

    SQLAlchemy 通过 :func:`_sa.create_engine` 的 :paramref:`_sa.create_engine.isolation_level`
    参数与该 PRAGMA 指令集成。与 SQLite 一起使用时，该参数的有效值为 ``"SERIALIZABLE"``
    与 ``"READ UNCOMMITTED"``，它们分别对应的 SQLite PRAGMA 值为 0 与 1。SQLite 默认值为
    ``SERIALIZABLE``，但其行为也受 pysqlite 驱动器默认行为的影响。

    在使用 pysqlite 驱动时，还可用 ``"AUTOCOMMIT"`` 隔离级别，它会通过 DBAPI 连接的
    ``.isolation_level`` 属性将其设置为 None，从而修改 pysqlite 的连接行为，在该设置期间启用自动提交。

    SQLite 的事务锁定行为受 ``BEGIN`` 语句的形式影响。该语句有三种模式：“deferred”、“immediate”
    与 “exclusive”，详见
    `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_。简单的 ``BEGIN`` 语句使用的是
    “deferred” 模式，在此模式下，直到第一次读写操作执行前，数据库文件不会被锁定；读操作在第一次写入前
    对其他事务仍是开放的。但需要特别注意的是，pysqlite 驱动会干扰此行为，它 **甚至不会在第一次写入前发出 BEGIN** 。

    .. warning::

        SQLite 的事务范围受到 pysqlite 驱动中未解决问题的影响，后者将 BEGIN 语句推迟到了不可接受的程度。
        请参阅 :ref:`pysqlite_serializable` 或 :ref:`aiosqlite_serializable` 部分，了解应对该行为的技巧。

    .. seealso::

        :ref:`dbapi_autocommit`

.. tab:: 英文

    SQLite supports "transaction isolation" in a non-standard way, along two
    axes.  One is that of the
    `PRAGMA read_uncommitted <https://www.sqlite.org/pragma.html#pragma_read_uncommitted>`_
    instruction.   This setting can essentially switch SQLite between its
    default mode of ``SERIALIZABLE`` isolation, and a "dirty read" isolation
    mode normally referred to as ``READ UNCOMMITTED``.

    SQLAlchemy ties into this PRAGMA statement using the
    :paramref:`_sa.create_engine.isolation_level` parameter of
    :func:`_sa.create_engine`.
    Valid values for this parameter when used with SQLite are ``"SERIALIZABLE"``
    and ``"READ UNCOMMITTED"`` corresponding to a value of 0 and 1, respectively.
    SQLite defaults to ``SERIALIZABLE``, however its behavior is impacted by
    the pysqlite driver's default behavior.

    When using the pysqlite driver, the ``"AUTOCOMMIT"`` isolation level is also
    available, which will alter the pysqlite connection using the ``.isolation_level``
    attribute on the DBAPI connection and set it to None for the duration
    of the setting.

    The other axis along which SQLite's transactional locking is impacted is
    via the nature of the ``BEGIN`` statement used.   The three varieties
    are "deferred", "immediate", and "exclusive", as described at
    `BEGIN TRANSACTION <https://sqlite.org/lang_transaction.html>`_.   A straight
    ``BEGIN`` statement uses the "deferred" mode, where the database file is
    not locked until the first read or write operation, and read access remains
    open to other transactions until the first write operation.  But again,
    it is critical to note that the pysqlite driver interferes with this behavior
    by *not even emitting BEGIN* until the first write operation.

    .. warning::

        SQLite's transactional scope is impacted by unresolved
        issues in the pysqlite driver, which defers BEGIN statements to a greater
        degree than is often feasible. See the section :ref:`pysqlite_serializable`
        or :ref:`aiosqlite_serializable` for techniques to work around this behavior.

    .. seealso::

        :ref:`dbapi_autocommit`

INSERT/UPDATE/DELETE...RETURNING
---------------------------------

INSERT/UPDATE/DELETE...RETURNING

.. tab:: 中文

    SQLite 方言支持 SQLite 3.35 引入的 ``INSERT|UPDATE|DELETE..RETURNING`` 语法。
    在某些场景下，可能会自动使用 ``INSERT..RETURNING`` 来获取新生成的标识符，
    替代传统的 ``cursor.lastrowid`` 方法；不过，在简单的单语句情况下，出于性能考虑，仍优先使用 ``cursor.lastrowid``。

    要显式指定 ``RETURNING`` 子句，请在每个语句上使用 :meth:`._UpdateBase.returning` 方法::

        # INSERT..RETURNING
        result = connection.execute(
            table.insert().values(name="foo").returning(table.c.col1, table.c.col2)
        )
        print(result.all())

        # UPDATE..RETURNING
        result = connection.execute(
            table.update()
            .where(table.c.name == "foo")
            .values(name="bar")
            .returning(table.c.col1, table.c.col2)
        )
        print(result.all())

        # DELETE..RETURNING
        result = connection.execute(
            table.delete()
            .where(table.c.name == "foo")
            .returning(table.c.col1, table.c.col2)
        )
        print(result.all())

    .. versionadded:: 2.0
        增加对 SQLite RETURNING 的支持

.. tab:: 英文

    The SQLite dialect supports SQLite 3.35's  ``INSERT|UPDATE|DELETE..RETURNING``
    syntax.   ``INSERT..RETURNING`` may be used
    automatically in some cases in order to fetch newly generated identifiers in
    place of the traditional approach of using ``cursor.lastrowid``, however
    ``cursor.lastrowid`` is currently still preferred for simple single-statement
    cases for its better performance.

    To specify an explicit ``RETURNING`` clause, use the
    :meth:`._UpdateBase.returning` method on a per-statement basis::

        # INSERT..RETURNING
        result = connection.execute(
            table.insert().values(name="foo").returning(table.c.col1, table.c.col2)
        )
        print(result.all())

        # UPDATE..RETURNING
        result = connection.execute(
            table.update()
            .where(table.c.name == "foo")
            .values(name="bar")
            .returning(table.c.col1, table.c.col2)
        )
        print(result.all())

        # DELETE..RETURNING
        result = connection.execute(
            table.delete()
            .where(table.c.name == "foo")
            .returning(table.c.col1, table.c.col2)
        )
        print(result.all())

    .. versionadded:: 2.0  Added support for SQLite RETURNING

SAVEPOINT 支持
----------------------------

SAVEPOINT Support

.. tab:: 中文

    SQLite 支持 SAVEPOINT（保存点），但仅在事务已开始后才生效。
    SQLAlchemy 通过 Core 层的 :meth:`_engine.Connection.begin_nested` 方法以及 ORM 层的 :meth:`.Session.begin_nested` 方法提供保存点支持。
    然而，除非使用某些变通方案，否则在使用 pysqlite 驱动时 SAVEPOINT 将无法正常工作。

    .. warning::

        SQLite 的 SAVEPOINT 功能受 pysqlite 和 aiosqlite 驱动中的未解决问题影响，
        它们将 BEGIN 语句的触发推迟到了通常无法接受的程度。
        请参阅 :ref:`pysqlite_serializable` 与 :ref:`aiosqlite_serializable`，了解应对技巧。

.. tab:: 英文

    SQLite supports SAVEPOINTs, which only function once a transaction is
    begun.   SQLAlchemy's SAVEPOINT support is available using the
    :meth:`_engine.Connection.begin_nested` method at the Core level, and
    :meth:`.Session.begin_nested` at the ORM level.   However, SAVEPOINTs
    won't work at all with pysqlite unless workarounds are taken.

    .. warning::

        SQLite's SAVEPOINT feature is impacted by unresolved
        issues in the pysqlite and aiosqlite drivers, which defer BEGIN statements
        to a greater degree than is often feasible. See the sections
        :ref:`pysqlite_serializable` and :ref:`aiosqlite_serializable`
        for techniques to work around this behavior.

事务性 DDL
----------------------------

Transactional DDL

.. tab:: 中文

    SQLite 数据库支持事务性的 :term:`DDL` 操作。
    在这种情况下，pysqlite 驱动不仅未能自动开启事务，
    还在检测到 DDL 时结束了任何已有事务，因此也需要特殊处理。

    .. warning::

        SQLite 的事务性 DDL 操作受到 pysqlite 驱动中未解决问题的影响，
        它既不发出 BEGIN，也会在遇到 DDL 时强制 COMMIT，取消已有事务。
        请参阅 :ref:`pysqlite_serializable`，了解应对技巧。

.. tab:: 英文

    The SQLite database supports transactional :term:`DDL` as well.
    In this case, the pysqlite driver is not only failing to start transactions,
    it also is ending any existing transaction when DDL is detected, so again,
    workarounds are required.

    .. warning::

        SQLite's transactional DDL is impacted by unresolved issues
        in the pysqlite driver, which fails to emit BEGIN and additionally
        forces a COMMIT to cancel any transaction when DDL is encountered.
        See the section :ref:`pysqlite_serializable`
        for techniques to work around this behavior.

.. _sqlite_foreign_keys:

外键支持
-------------------

Foreign Key Support

.. tab:: 中文

    SQLite 支持在表的 CREATE 语句中使用 FOREIGN KEY 语法，
    但默认情况下，这些约束 **对表的行为没有实际影响**。

    要使 SQLite 中的外键约束生效，需要满足以下三个前提：

    * 必须使用 SQLite 版本 3.6.19 或更高版本；
    * SQLite 库在编译时 **不能启用** SQLITE_OMIT_FOREIGN_KEY 或 SQLITE_OMIT_TRIGGER 宏；
    * 在所有连接使用前必须显式发出 ``PRAGMA foreign_keys = ON`` 语句，包括调用 :meth:`sqlalchemy.schema.MetaData.create_all` 之前。

    SQLAlchemy 可通过事件机制在新连接建立时自动发出 ``PRAGMA`` 语句::

        from sqlalchemy.engine import Engine
        from sqlalchemy import event


        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    .. warning::

        启用 SQLite 外键后，**无法** 对包含相互依赖外键约束的表执行 CREATE 或 DROP 操作；
        若要为这类表发出 DDL，必须使用 ALTER TABLE 单独创建或删除这些约束，
        但 SQLite 并 **不支持** 此类操作。

    .. seealso::

        `SQLite Foreign Key Support <https://www.sqlite.org/foreignkeys.html>`_
        - SQLite 官方网站上的相关说明。

        :ref:`event_toplevel` - SQLAlchemy 的事件 API。

        :ref:`use_alter` - 了解 SQLAlchemy 如何处理相互依赖的外键约束的更多信息。

.. tab:: 英文

    SQLite supports FOREIGN KEY syntax when emitting CREATE statements for tables,
    however by default these constraints have no effect on the operation of the
    table.

    Constraint checking on SQLite has three prerequisites:

    * At least version 3.6.19 of SQLite must be in use
    * The SQLite library must be compiled *without* the SQLITE_OMIT_FOREIGN_KEY
      or SQLITE_OMIT_TRIGGER symbols enabled.
    * The ``PRAGMA foreign_keys = ON`` statement must be emitted on all
      connections before use -- including the initial call to
      :meth:`sqlalchemy.schema.MetaData.create_all`.

    SQLAlchemy allows for the ``PRAGMA`` statement to be emitted automatically for
    new connections through the usage of events::

        from sqlalchemy.engine import Engine
        from sqlalchemy import event


        @event.listens_for(Engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    .. warning::

        When SQLite foreign keys are enabled, it is **not possible**
        to emit CREATE or DROP statements for tables that contain
        mutually-dependent foreign key constraints;
        to emit the DDL for these tables requires that ALTER TABLE be used to
        create or drop these constraints separately, for which SQLite has
        no support.

    .. seealso::

        `SQLite Foreign Key Support <https://www.sqlite.org/foreignkeys.html>`_
        - on the SQLite web site.

        :ref:`event_toplevel` - SQLAlchemy event API.

        :ref:`use_alter` - more information on SQLAlchemy's facilities for handling
         mutually-dependent foreign key constraints.

.. _sqlite_on_conflict_ddl:

ON CONFLICT 约束支持
-----------------------------------

ON CONFLICT support for constraints

.. tab:: 中文

    .. seealso:: 本节描述了 SQLite 中出现在 CREATE TABLE 语句中的 :term:`DDL` 版本的 "ON CONFLICT"。关于适用于 INSERT 语句的 "ON CONFLICT"，请参阅 :ref:`sqlite_on_conflict_insert`。

    SQLite 支持一种非标准的 DDL 子句 ON CONFLICT，可应用于主键、唯一性、检查以及非空约束。在 DDL 中，该子句可以出现在 "CONSTRAINT" 子句中，或直接出现在列定义内，具体取决于目标约束的位置。要在 DDL 中渲染该子句，可以在 :class:`.PrimaryKeyConstraint`、:class:`.UniqueConstraint`、:class:`.CheckConstraint` 对象中指定扩展参数 ``sqlite_on_conflict`` 并传入冲突解决算法的字符串形式。在 :class:`_schema.Column` 对象中，则可以使用 ``sqlite_on_conflict_not_null``、``sqlite_on_conflict_primary_key``、``sqlite_on_conflict_unique`` 等参数，分别对应三种列级约束类型。

    .. seealso::

        `ON CONFLICT <https://www.sqlite.org/lang_conflict.html>`_ - SQLite 官方文档

    ``sqlite_on_conflict`` 参数接受一个字符串，表示选择的冲突解决算法，其值可以是 SQLite 支持的 ROLLBACK、ABORT、FAIL、IGNORE 或 REPLACE。例如，添加一个指定使用 IGNORE 算法的 UNIQUE 约束::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", Integer),
            UniqueConstraint("id", "data", sqlite_on_conflict="IGNORE"),
        )

    上述代码生成的 CREATE TABLE DDL 如下：

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER,
            PRIMARY KEY (id),
            UNIQUE (id, data) ON CONFLICT IGNORE
        )

    使用 :paramref:`_schema.Column.unique` 标志为单个列添加 UNIQUE 约束时，也可以通过 ``sqlite_on_conflict_unique`` 参数指定冲突策略，该参数将会添加到生成的 UNIQUE 约束中::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "data", Integer, unique=True, sqlite_on_conflict_unique="IGNORE"
            ),
        )

    生成的 SQL 如下：

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER,
            PRIMARY KEY (id),
            UNIQUE (data) ON CONFLICT IGNORE
        )

    要为 NOT NULL 约束指定 FAIL 算法，可使用 ``sqlite_on_conflict_not_null``::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "data", Integer, nullable=False, sqlite_on_conflict_not_null="FAIL"
            ),
        )

    生成的列定义中会包含 inline 的 ON CONFLICT 子句：

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER NOT NULL ON CONFLICT FAIL,
            PRIMARY KEY (id)
        )

    类似地，若要为 inline 主键指定冲突算法，可使用 ``sqlite_on_conflict_primary_key``::

        some_table = Table(
            "some_table",
            metadata,
            Column(
                "id",
                Integer,
                primary_key=True,
                sqlite_on_conflict_primary_key="FAIL",
            ),
        )

    由于 SQLAlchemy 会单独渲染 PRIMARY KEY 约束，因此冲突解决算法会应用在约束上：

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            PRIMARY KEY (id) ON CONFLICT FAIL
        )

.. tab:: 英文

    .. seealso:: This section describes the :term:`DDL` version of "ON CONFLICT" for
       SQLite, which occurs within a CREATE TABLE statement.  For "ON CONFLICT" as
       applied to an INSERT statement, see :ref:`sqlite_on_conflict_insert`.

    SQLite supports a non-standard DDL clause known as ON CONFLICT which can be applied
    to primary key, unique, check, and not null constraints.   In DDL, it is
    rendered either within the "CONSTRAINT" clause or within the column definition
    itself depending on the location of the target constraint.    To render this
    clause within DDL, the extension parameter ``sqlite_on_conflict`` can be
    specified with a string conflict resolution algorithm within the
    :class:`.PrimaryKeyConstraint`, :class:`.UniqueConstraint`,
    :class:`.CheckConstraint` objects.  Within the :class:`_schema.Column` object,
    there
    are individual parameters ``sqlite_on_conflict_not_null``,
    ``sqlite_on_conflict_primary_key``, ``sqlite_on_conflict_unique`` which each
    correspond to the three types of relevant constraint types that can be
    indicated from a :class:`_schema.Column` object.

    .. seealso::

        `ON CONFLICT <https://www.sqlite.org/lang_conflict.html>`_ - in the SQLite
        documentation

    The ``sqlite_on_conflict`` parameters accept a  string argument which is just
    the resolution name to be chosen, which on SQLite can be one of ROLLBACK,
    ABORT, FAIL, IGNORE, and REPLACE.   For example, to add a UNIQUE constraint
    that specifies the IGNORE algorithm::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", Integer),
            UniqueConstraint("id", "data", sqlite_on_conflict="IGNORE"),
        )

    The above renders CREATE TABLE DDL as:

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER,
            PRIMARY KEY (id),
            UNIQUE (id, data) ON CONFLICT IGNORE
        )


    When using the :paramref:`_schema.Column.unique`
    flag to add a UNIQUE constraint
    to a single column, the ``sqlite_on_conflict_unique`` parameter can
    be added to the :class:`_schema.Column` as well, which will be added to the
    UNIQUE constraint in the DDL::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "data", Integer, unique=True, sqlite_on_conflict_unique="IGNORE"
            ),
        )

    rendering:

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER,
            PRIMARY KEY (id),
            UNIQUE (data) ON CONFLICT IGNORE
        )

    To apply the FAIL algorithm for a NOT NULL constraint,
    ``sqlite_on_conflict_not_null`` is used::

        some_table = Table(
            "some_table",
            metadata,
            Column("id", Integer, primary_key=True),
            Column(
                "data", Integer, nullable=False, sqlite_on_conflict_not_null="FAIL"
            ),
        )

    this renders the column inline ON CONFLICT phrase:

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            data INTEGER NOT NULL ON CONFLICT FAIL,
            PRIMARY KEY (id)
        )


    Similarly, for an inline primary key, use ``sqlite_on_conflict_primary_key``::

        some_table = Table(
            "some_table",
            metadata,
            Column(
                "id",
                Integer,
                primary_key=True,
                sqlite_on_conflict_primary_key="FAIL",
            ),
        )

    SQLAlchemy renders the PRIMARY KEY constraint separately, so the conflict
    resolution algorithm is applied to the constraint itself:

    .. sourcecode:: sql

        CREATE TABLE some_table (
            id INTEGER NOT NULL,
            PRIMARY KEY (id) ON CONFLICT FAIL
        )

.. _sqlite_on_conflict_insert:

INSERT...ON CONFLICT（更新插入）
-----------------------------

INSERT...ON CONFLICT (Upsert)

.. tab:: 中文

    .. seealso:: 本节描述了 SQLite 中出现在 INSERT 语句中的 :term:`DML` 版本的 "ON CONFLICT"。关于适用于 CREATE TABLE 语句的版本，请参阅 :ref:`sqlite_on_conflict_ddl`。

    自 SQLite 3.24.0 版本起，支持通过 ``INSERT`` 语句中的 ``ON CONFLICT`` 子句实现“upsert”（插入或更新）功能。候选行只有在不违反任何唯一或主键约束的情况下才会被插入。若违反唯一性约束，则可以采取两种方式处理：其一是 "DO UPDATE"，表示应更新目标行中的数据；其二是 "DO NOTHING"，表示跳过该行。

    冲突的判断基于表中现有的唯一约束或唯一索引。这些约束通过显式声明其包含的列和条件来识别。

    SQLAlchemy 提供了 SQLite 特有的 :func:`_sqlite.insert()` 函数以支持 ``ON CONFLICT``，并配套提供了生成式方法 :meth:`_sqlite.Insert.on_conflict_do_update` 和 :meth:`_sqlite.Insert.on_conflict_do_nothing`：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.dialects.sqlite import insert

        >>> insert_stmt = insert(my_table).values(
        ...     id="some_existing_id", data="inserted value"
        ... )

        >>> do_update_stmt = insert_stmt.on_conflict_do_update(
        ...     index_elements=["id"], set_=dict(data="updated value")
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?{stop}

        >>> do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["id"])

        >>> print(do_nothing_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO NOTHING

    .. versionadded:: 1.4

    .. seealso::

        `Upsert
        <https://sqlite.org/lang_UPSERT.html>`_
        - SQLite 官方文档

.. tab:: 英文

    .. seealso:: This section describes the :term:`DML` version of "ON CONFLICT" for
       SQLite, which occurs within an INSERT statement.  For "ON CONFLICT" as
       applied to a CREATE TABLE statement, see :ref:`sqlite_on_conflict_ddl`.

    From version 3.24.0 onwards, SQLite supports "upserts" (update or insert)
    of rows into a table via the ``ON CONFLICT`` clause of the ``INSERT``
    statement. A candidate row will only be inserted if that row does not violate
    any unique or primary key constraints. In the case of a unique constraint violation, a
    secondary action can occur which can be either "DO UPDATE", indicating that
    the data in the target row should be updated, or "DO NOTHING", which indicates
    to silently skip this row.

    Conflicts are determined using columns that are part of existing unique
    constraints and indexes.  These constraints are identified by stating the
    columns and conditions that comprise the indexes.

    SQLAlchemy provides ``ON CONFLICT`` support via the SQLite-specific
    :func:`_sqlite.insert()` function, which provides
    the generative methods :meth:`_sqlite.Insert.on_conflict_do_update`
    and :meth:`_sqlite.Insert.on_conflict_do_nothing`:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.dialects.sqlite import insert

        >>> insert_stmt = insert(my_table).values(
        ...     id="some_existing_id", data="inserted value"
        ... )

        >>> do_update_stmt = insert_stmt.on_conflict_do_update(
        ...     index_elements=["id"], set_=dict(data="updated value")
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?{stop}

        >>> do_nothing_stmt = insert_stmt.on_conflict_do_nothing(index_elements=["id"])

        >>> print(do_nothing_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO NOTHING

    .. versionadded:: 1.4

    .. seealso::

        `Upsert <https://sqlite.org/lang_UPSERT.html>`_ - in the SQLite documentation.


指定目标
^^^^^^^^^^^^^^^^^^^^^

Specifying the Target

.. tab:: 中文

    这两个方法都通过列推断方式指定冲突目标：

    * 参数 :paramref:`_sqlite.Insert.on_conflict_do_update.index_elements` 接受一个序列，可包含字符串形式的列名、:class:`_schema.Column` 对象，或 SQL 表达式，用于标识唯一索引或约束。

    * 使用 :paramref:`_sqlite.Insert.on_conflict_do_update.index_elements` 推断索引时，可结合 :paramref:`_sqlite.Insert.on_conflict_do_update.index_where` 参数推断部分索引：

      .. sourcecode:: pycon+sql

            >>> stmt = insert(my_table).values(user_email="a@b.com", data="inserted data")

            >>> do_update_stmt = stmt.on_conflict_do_update(
            ...     index_elements=[my_table.c.user_email],
            ...     index_where=my_table.c.user_email.like("%@gmail.com"),
            ...     set_=dict(data=stmt.excluded.data),
            ... )

            >>> print(do_update_stmt)
            {printsql}INSERT INTO my_table (data, user_email) VALUES (?, ?)
            ON CONFLICT (user_email)
            WHERE user_email LIKE '%@gmail.com'
            DO UPDATE SET data = excluded.data

.. tab:: 英文

    Both methods supply the "target" of the conflict using column inference:

    * The :paramref:`_sqlite.Insert.on_conflict_do_update.index_elements` argument
      specifies a sequence containing string column names, :class:`_schema.Column`
      objects, and/or SQL expression elements, which would identify a unique index
      or unique constraint.

    * When using :paramref:`_sqlite.Insert.on_conflict_do_update.index_elements`
      to infer an index, a partial index can be inferred by also specifying the
      :paramref:`_sqlite.Insert.on_conflict_do_update.index_where` parameter:

      .. sourcecode:: pycon+sql

            >>> stmt = insert(my_table).values(user_email="a@b.com", data="inserted data")

            >>> do_update_stmt = stmt.on_conflict_do_update(
            ...     index_elements=[my_table.c.user_email],
            ...     index_where=my_table.c.user_email.like("%@gmail.com"),
            ...     set_=dict(data=stmt.excluded.data),
            ... )

            >>> print(do_update_stmt)
            {printsql}INSERT INTO my_table (data, user_email) VALUES (?, ?)
            ON CONFLICT (user_email)
            WHERE user_email LIKE '%@gmail.com'
            DO UPDATE SET data = excluded.data

SET 子句
^^^^^^^^^^^^^^^

The SET Clause

.. tab:: 中文

    ``ON CONFLICT...DO UPDATE`` 用于在已存在行的情况下执行更新操作，该更新可以结合插入操作中提供的新值以及其他值。这些更新值通过参数 :paramref:`_sqlite.Insert.on_conflict_do_update.set_` 指定。该参数接受一个字典，字典中的内容将直接用于 UPDATE：

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")

        >>> do_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"], set_=dict(data="updated value")
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?

    .. warning::

        方法 :meth:`_sqlite.Insert.on_conflict_do_update` **不会** 考虑 Python 端指定的默认 UPDATE 值或生成函数，例如通过 :paramref:`_schema.Column.onupdate` 指定的那些值。若希望在 ON CONFLICT 风格的 UPDATE 中应用这些值，必须显式地包含在 :paramref:`_sqlite.Insert.on_conflict_do_update.set_` 字典中。

.. tab:: 英文

    ``ON CONFLICT...DO UPDATE`` is used to perform an update of the already
    existing row, using any combination of new values as well as values
    from the proposed insertion. These values are specified using the
    :paramref:`_sqlite.Insert.on_conflict_do_update.set_` parameter.  This
    parameter accepts a dictionary which consists of direct values
    for UPDATE:

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")

        >>> do_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"], set_=dict(data="updated value")
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?

    .. warning::

        The :meth:`_sqlite.Insert.on_conflict_do_update` method does **not** take
        into account Python-side default UPDATE values or generation functions,
        e.g. those specified using :paramref:`_schema.Column.onupdate`. These
        values will not be exercised for an ON CONFLICT style of UPDATE, unless
        they are manually specified in the
        :paramref:`_sqlite.Insert.on_conflict_do_update.set_` dictionary.

使用排除的 INSERT 值进行更新
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Updating using the Excluded INSERT Values

.. tab:: 中文

    若要引用拟插入的行，可以使用特殊别名 :attr:`~.sqlite.Insert.excluded`，该别名可作为 :class:`_sqlite.Insert` 对象的一个属性使用。它会在列名前加上 "excluded." 前缀，告知 DO UPDATE 使用原本会被插入的值来更新现有行（假如没有冲突）：

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(
        ...     id="some_id", data="inserted value", author="jlh"
        ... )

        >>> do_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"],
        ...     set_=dict(data="updated value", author=stmt.excluded.author),
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data, author) VALUES (?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?, author = excluded.author

.. tab:: 英文

    In order to refer to the proposed insertion row, the special alias
    :attr:`~.sqlite.Insert.excluded` is available as an attribute on
    the :class:`_sqlite.Insert` object; this object creates an "excluded." prefix
    on a column, that informs the DO UPDATE to update the row with the value that
    would have been inserted had the constraint not failed:

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(
        ...     id="some_id", data="inserted value", author="jlh"
        ... )

        >>> do_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"],
        ...     set_=dict(data="updated value", author=stmt.excluded.author),
        ... )

        >>> print(do_update_stmt)
        {printsql}INSERT INTO my_table (id, data, author) VALUES (?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?, author = excluded.author

其他 WHERE 条件
^^^^^^^^^^^^^^^^^^^^^^^^^

Additional WHERE Criteria

.. tab:: 中文

    方法 :meth:`_sqlite.Insert.on_conflict_do_update` 还接受一个 WHERE 子句，通过参数 :paramref:`_sqlite.Insert.on_conflict_do_update.where` 指定，用于限制执行 UPDATE 的行范围：

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(
        ...     id="some_id", data="inserted value", author="jlh"
        ... )

        >>> on_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"],
        ...     set_=dict(data="updated value", author=stmt.excluded.author),
        ...     where=(my_table.c.status == 2),
        ... )
        >>> print(on_update_stmt)
        {printsql}INSERT INTO my_table (id, data, author) VALUES (?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?, author = excluded.author
        WHERE my_table.status = ?

.. tab:: 英文

    The :meth:`_sqlite.Insert.on_conflict_do_update` method also accepts
    a WHERE clause using the :paramref:`_sqlite.Insert.on_conflict_do_update.where`
    parameter, which will limit those rows which receive an UPDATE:

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(
        ...     id="some_id", data="inserted value", author="jlh"
        ... )

        >>> on_update_stmt = stmt.on_conflict_do_update(
        ...     index_elements=["id"],
        ...     set_=dict(data="updated value", author=stmt.excluded.author),
        ...     where=(my_table.c.status == 2),
        ... )
        >>> print(on_update_stmt)
        {printsql}INSERT INTO my_table (id, data, author) VALUES (?, ?, ?)
        ON CONFLICT (id) DO UPDATE SET data = ?, author = excluded.author
        WHERE my_table.status = ?


使用 DO NOTHING 跳过行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Skipping Rows with DO NOTHING

.. tab:: 中文

    使用 ``ON CONFLICT`` 也可以完全跳过插入操作，当遇到唯一性约束冲突时直接忽略该行的插入。以下示例展示了如何通过方法 :meth:`_sqlite.Insert.on_conflict_do_nothing` 实现这一功能：

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")
        >>> stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        >>> print(stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?) ON CONFLICT (id) DO NOTHING

    若在 ``DO NOTHING`` 中未指定任何列或约束，则该语句将忽略所有发生唯一性冲突的插入：

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")
        >>> stmt = stmt.on_conflict_do_nothing()
        >>> print(stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?) ON CONFLICT DO NOTHING

.. tab:: 英文

    ``ON CONFLICT`` may be used to skip inserting a row entirely
    if any conflict with a unique constraint occurs; below this is illustrated
    using the :meth:`_sqlite.Insert.on_conflict_do_nothing` method:

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")
        >>> stmt = stmt.on_conflict_do_nothing(index_elements=["id"])
        >>> print(stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?) ON CONFLICT (id) DO NOTHING


    If ``DO NOTHING`` is used without specifying any columns or constraint,
    it has the effect of skipping the INSERT for any unique violation which
    occurs:

    .. sourcecode:: pycon+sql

        >>> stmt = insert(my_table).values(id="some_id", data="inserted value")
        >>> stmt = stmt.on_conflict_do_nothing()
        >>> print(stmt)
        {printsql}INSERT INTO my_table (id, data) VALUES (?, ?) ON CONFLICT DO NOTHING

.. _sqlite_type_reflection:

类型反射
---------------

Type Reflection

.. tab:: 中文

    SQLite 的类型系统不同于大多数其他数据库后端，其类型字符串名称通常并不一一对应于某种具体的“类型”。相反，SQLite 使用所谓的五种“类型亲和性”（type affinities）机制，通过字符串匹配方式为每一列确定类型行为。

    SQLAlchemy 在执行类型反射时，会使用一个简单的查找表将返回的关键字映射为 SQLAlchemy 提供的类型。这个查找表在 SQLite 方言中与其他方言类似。但是，SQLite 方言在找不到特定类型名的匹配项时，使用一种不同的“回退”策略：它实现了 SQLite 在官方文档 https://www.sqlite.org/datatype3.html 第 2.1 节中描述的“类型亲和性”规则。

    此查找表会直接将以下类型名与对应的 SQLAlchemy 类型进行一一匹配：

    :class:`_types.BIGINT`、:class:`_types.BLOB`、
    :class:`_types.BOOLEAN`、:class:`_types.BOOLEAN`、
    :class:`_types.CHAR`、:class:`_types.DATE`、
    :class:`_types.DATETIME`、:class:`_types.FLOAT`、
    :class:`_types.DECIMAL`、:class:`_types.FLOAT`、
    :class:`_types.INTEGER`、:class:`_types.INTEGER`、
    :class:`_types.NUMERIC`、:class:`_types.REAL`、
    :class:`_types.SMALLINT`、:class:`_types.TEXT`、
    :class:`_types.TIME`、:class:`_types.TIMESTAMP`、
    :class:`_types.VARCHAR`、:class:`_types.NVARCHAR`、
    :class:`_types.NCHAR`

    当类型名称未匹配上述任何项时，将采用“类型亲和性”规则进行推断：

    * 若类型名包含字符串 ``INT``，则返回 :class:`_types.INTEGER`
    * 若类型名包含字符串 ``CHAR``、``CLOB`` 或 ``TEXT``，则返回 :class:`_types.TEXT`
    * 若类型名包含字符串 ``BLOB``，则返回 :class:`_types.NullType`
    * 若类型名包含字符串 ``REAL``、``FLOA`` 或 ``DOUB``，则返回 :class:`_types.REAL`
    * 否则，使用 :class:`*

.. tab:: 英文

    SQLite types are unlike those of most other database backends, in that
    the string name of the type usually does not correspond to a "type" in a
    one-to-one fashion.  Instead, SQLite links per-column typing behavior
    to one of five so-called "type affinities" based on a string matching
    pattern for the type.

    SQLAlchemy's reflection process, when inspecting types, uses a simple
    lookup table to link the keywords returned to provided SQLAlchemy types.
    This lookup table is present within the SQLite dialect as it is for all
    other dialects.  However, the SQLite dialect has a different "fallback"
    routine for when a particular type name is not located in the lookup map;
    it instead implements the SQLite "type affinity" scheme located at
    https://www.sqlite.org/datatype3.html section 2.1.

    The provided typemap will make direct associations from an exact string
    name match for the following types:

    :class:`_types.BIGINT`, :class:`_types.BLOB`,
    :class:`_types.BOOLEAN`, :class:`_types.BOOLEAN`,
    :class:`_types.CHAR`, :class:`_types.DATE`,
    :class:`_types.DATETIME`, :class:`_types.FLOAT`,
    :class:`_types.DECIMAL`, :class:`_types.FLOAT`,
    :class:`_types.INTEGER`, :class:`_types.INTEGER`,
    :class:`_types.NUMERIC`, :class:`_types.REAL`,
    :class:`_types.SMALLINT`, :class:`_types.TEXT`,
    :class:`_types.TIME`, :class:`_types.TIMESTAMP`,
    :class:`_types.VARCHAR`, :class:`_types.NVARCHAR`,
    :class:`_types.NCHAR`

    When a type name does not match one of the above types, the "type affinity"
    lookup is used instead:

    * :class:`_types.INTEGER` is returned if the type name includes the
      string ``INT``
    * :class:`_types.TEXT` is returned if the type name includes the
      string ``CHAR``, ``CLOB`` or ``TEXT``
    * :class:`_types.NullType` is returned if the type name includes the
      string ``BLOB``
    * :class:`_types.REAL` is returned if the type name includes the string
      ``REAL``, ``FLOA`` or ``DOUB``.
    * Otherwise, the :class:`_types.NUMERIC` type is used.

.. _sqlite_partial_index:

部分索引
---------------

Partial Indexes

.. tab:: 中文

    可以通过 DDL 系统中的 ``sqlite_where`` 参数来定义一个 **部分索引** （例如带有 WHERE 子句的索引）::

        tbl = Table("testtbl", m, Column("data", Integer))
        idx = Index(
            "test_idx1",
            tbl.c.data,
            sqlite_where=and_(tbl.c.data > 5, tbl.c.data < 10),
        )

    该索引在创建时将被渲染为：

    .. sourcecode:: sql

        CREATE INDEX test_idx1 ON testtbl (data)
        WHERE data > 5 AND data < 10

.. tab:: 英文

    A partial index, e.g. one which uses a WHERE clause, can be specified
    with the DDL system using the argument ``sqlite_where``::

        tbl = Table("testtbl", m, Column("data", Integer))
        idx = Index(
            "test_idx1",
            tbl.c.data,
            sqlite_where=and_(tbl.c.data > 5, tbl.c.data < 10),
        )

    The index will be rendered at create time as:

    .. sourcecode:: sql

        CREATE INDEX test_idx1 ON testtbl (data)
        WHERE data > 5 AND data < 10

.. _sqlite_dotted_column_names:

点分列名
-------------------

Dotted Column Names

.. tab:: 中文

    **不推荐** 使用显式包含句点（`.`）的表名或列名。尽管在关系型数据库中这是一个通用的糟糕做法，因为点号是一个具有语法意义的字符，但在 SQLite 驱动中，直到 **3.10.0** 版本之前存在一个 bug，使得 SQLAlchemy 必须在结果集中过滤掉这些点号。

    这个完全由 SQLite 引擎外部引起的 bug 可以如下重现::

        import sqlite3

        assert sqlite3.sqlite_version_info < (
            3,
            10,
            0,
        ), "bug 在该版本中已修复"

        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("create table x (a integer, b integer)")
        cursor.execute("insert into x (a, b) values (1, 1)")
        cursor.execute("insert into x (a, b) values (2, 2)")

        cursor.execute("select x.a, x.b from x")
        assert [c[0] for c in cursor.description] == ["a", "b"]

        cursor.execute(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert [c[0] for c in cursor.description] == ["a", "b"], [
            c[0] for c in cursor.description
        ]

    第二个断言将会失败：

    .. sourcecode:: text

        Traceback (most recent call last):
          File "test.py", line 19, in <module>
            [c[0] for c in cursor.description]
        AssertionError: ['x.a', 'x.b']

    如上所示，驱动错误地将列名报告为包含表名的形式，这与没有使用 UNION 时的行为完全不一致。

    SQLAlchemy 依赖于列名在与原始语句匹配时的可预测性，因此 SQLite 方言别无选择，只能过滤掉这些点号::

        from sqlalchemy import create_engine

        eng = create_engine("sqlite://")
        conn = eng.connect()

        conn.exec_driver_sql("create table x (a integer, b integer)")
        conn.exec_driver_sql("insert into x (a, b) values (1, 1)")
        conn.exec_driver_sql("insert into x (a, b) values (2, 2)")

        result = conn.exec_driver_sql("select x.a, x.b from x")
        assert result.keys() == ["a", "b"]

        result = conn.exec_driver_sql(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert result.keys() == ["a", "b"]

    注意，尽管 SQLAlchemy 过滤掉了点号，*仍然可以通过带点的形式访问这些列名*::

        >>> row = result.first()
        >>> row["a"]
        1
        >>> row["x.a"]
        1
        >>> row["b"]
        1
        >>> row["x.b"]
        1

    因此，SQLAlchemy 所采取的回避策略仅影响公共 API 中的 :meth:`_engine.CursorResult.keys` 与 :meth:`.Row.keys()`。在某些特定场景中，若应用确实 **必须** 使用包含点号的列名，并且需要通过 :meth:`_engine.CursorResult.keys` 或 :meth:`.Row.keys()` 返回这些 **未经修改的原始列名** ，则可以使用 ``sqlite_raw_colnames`` 执行选项来启用这一行为，可在每个 :class:`_engine.Connection` 实例中设置::

        result = conn.execution_options(sqlite_raw_colnames=True).exec_driver_sql(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert result.keys() == ["x.a", "x.b"]

    也可在每个 :class:`_engine.Engine` 实例上设置::

        engine = create_engine(
            "sqlite://", execution_options={"sqlite_raw_colnames": True}
        )

    使用引擎级别的执行选项时，请注意： **基于 Core 或 ORM 的 UNION 查询可能无法正常工作**。

.. tab:: 英文

    Using table or column names that explicitly have periods in them is
    **not recommended**.   While this is generally a bad idea for relational
    databases in general, as the dot is a syntactically significant character,
    the SQLite driver up until version **3.10.0** of SQLite has a bug which
    requires that SQLAlchemy filter out these dots in result sets.

    The bug, entirely outside of SQLAlchemy, can be illustrated thusly::

        import sqlite3

        assert sqlite3.sqlite_version_info < (
            3,
            10,
            0,
        ), "bug is fixed in this version"

        conn = sqlite3.connect(":memory:")
        cursor = conn.cursor()

        cursor.execute("create table x (a integer, b integer)")
        cursor.execute("insert into x (a, b) values (1, 1)")
        cursor.execute("insert into x (a, b) values (2, 2)")

        cursor.execute("select x.a, x.b from x")
        assert [c[0] for c in cursor.description] == ["a", "b"]

        cursor.execute(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert [c[0] for c in cursor.description] == ["a", "b"], [
            c[0] for c in cursor.description
        ]

    The second assertion fails:

    .. sourcecode:: text

        Traceback (most recent call last):
          File "test.py", line 19, in <module>
            [c[0] for c in cursor.description]
        AssertionError: ['x.a', 'x.b']

    Where above, the driver incorrectly reports the names of the columns
    including the name of the table, which is entirely inconsistent vs.
    when the UNION is not present.

    SQLAlchemy relies upon column names being predictable in how they match
    to the original statement, so the SQLAlchemy dialect has no choice but
    to filter these out::


        from sqlalchemy import create_engine

        eng = create_engine("sqlite://")
        conn = eng.connect()

        conn.exec_driver_sql("create table x (a integer, b integer)")
        conn.exec_driver_sql("insert into x (a, b) values (1, 1)")
        conn.exec_driver_sql("insert into x (a, b) values (2, 2)")

        result = conn.exec_driver_sql("select x.a, x.b from x")
        assert result.keys() == ["a", "b"]

        result = conn.exec_driver_sql(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert result.keys() == ["a", "b"]

    Note that above, even though SQLAlchemy filters out the dots, *both
    names are still addressable*::

        >>> row = result.first()
        >>> row["a"]
        1
        >>> row["x.a"]
        1
        >>> row["b"]
        1
        >>> row["x.b"]
        1

    Therefore, the workaround applied by SQLAlchemy only impacts
    :meth:`_engine.CursorResult.keys` and :meth:`.Row.keys()` in the public API. In
    the very specific case where an application is forced to use column names that
    contain dots, and the functionality of :meth:`_engine.CursorResult.keys` and
    :meth:`.Row.keys()` is required to return these dotted names unmodified,
    the ``sqlite_raw_colnames`` execution option may be provided, either on a
    per-:class:`_engine.Connection` basis::

        result = conn.execution_options(sqlite_raw_colnames=True).exec_driver_sql(
            """
            select x.a, x.b from x where a=1
            union
            select x.a, x.b from x where a=2
            """
        )
        assert result.keys() == ["x.a", "x.b"]

    or on a per-:class:`_engine.Engine` basis::

        engine = create_engine(
            "sqlite://", execution_options={"sqlite_raw_colnames": True}
        )

    When using the per-:class:`_engine.Engine` execution option, note that
    **Core and ORM queries that use UNION may not function properly**.

SQLite 特定表选项
-----------------------------

SQLite-specific table options

.. tab:: 中文

    SQLite 方言支持与 :class:`_schema.Table` 构造配合使用的 `CREATE TABLE` 选项如下：

    * ``WITHOUT ROWID``::

        Table("some_table", metadata, ..., sqlite_with_rowid=False)

    *
      ``STRICT``::

        Table("some_table", metadata, ..., sqlite_strict=True)

      .. versionadded:: 2.0.37

    .. seealso::

        `SQLite CREATE TABLE options
        <https://www.sqlite.org/lang_createtable.html>`_

.. tab:: 英文

    One option for CREATE TABLE is supported directly by the SQLite
    dialect in conjunction with the :class:`_schema.Table` construct:

    * ``WITHOUT ROWID``::

        Table("some_table", metadata, ..., sqlite_with_rowid=False)

    *
      ``STRICT``::

        Table("some_table", metadata, ..., sqlite_strict=True)

      .. versionadded:: 2.0.37

    .. seealso::

        `SQLite CREATE TABLE options
        <https://www.sqlite.org/lang_createtable.html>`_

.. _sqlite_include_internal:

反射内部模式表
----------------------------------

Reflecting internal schema tables

.. tab:: 中文

    返回表名列表的反射方法会排除所谓的 "SQLite 内部模式对象（internal schema object）"，SQLite 认为这些是名称以 ``sqlite_`` 为前缀的对象。例如使用 ``AUTOINCREMENT`` 列参数时自动生成的 ``sqlite_sequence`` 表。若希望返回这些对象，可以向 :meth:`_schema.MetaData.reflect` 或 :meth:`.Inspector.get_table_names` 等方法传递参数 ``sqlite_include_internal=True``。

    .. versionadded:: 2.0

        增加了 ``sqlite_include_internal=True`` 参数。此前，SQLAlchemy 反射方法并不会忽略这些表。

    .. note::

        参数 ``sqlite_include_internal`` 并不作用于存在于 ``sqlite_master`` 等模式中的 “系统” 表。

    .. seealso::

        `SQLite Internal Schema Objects <https://www.sqlite.org/fileformat2.html#intschema>`_ - SQLite 官方文档中的介绍。

.. tab:: 英文

    Reflection methods that return lists of tables will omit so-called
    "SQLite internal schema object" names, which are considered by SQLite
    as any object name that is prefixed with ``sqlite_``.  An example of
    such an object is the ``sqlite_sequence`` table that's generated when
    the ``AUTOINCREMENT`` column parameter is used.   In order to return
    these objects, the parameter ``sqlite_include_internal=True`` may be
    passed to methods such as :meth:`_schema.MetaData.reflect` or
    :meth:`.Inspector.get_table_names`.

    .. versionadded:: 2.0  Added the ``sqlite_include_internal=True`` parameter.
       Previously, these tables were not ignored by SQLAlchemy reflection
       methods.

    .. note::

        The ``sqlite_include_internal`` parameter does not refer to the
        "system" tables that are present in schemas such as ``sqlite_master``.

    .. seealso::

        `SQLite Internal Schema Objects <https://www.sqlite.org/fileformat2.html#intschema>`_ - in the SQLite documentation.

'''  # noqa

from __future__ import annotations

import datetime
import numbers
import re
from typing import Optional

from .json import JSON
from .json import JSONIndexType
from .json import JSONPathType
from ... import exc
from ... import schema as sa_schema
from ... import sql
from ... import text
from ... import types as sqltypes
from ... import util
from ...engine import default
from ...engine import processors
from ...engine import reflection
from ...engine.reflection import ReflectionDefaults
from ...sql import coercions
from ...sql import compiler
from ...sql import elements
from ...sql import roles
from ...sql import schema
from ...types import BLOB  # noqa
from ...types import BOOLEAN  # noqa
from ...types import CHAR  # noqa
from ...types import DECIMAL  # noqa
from ...types import FLOAT  # noqa
from ...types import INTEGER  # noqa
from ...types import NUMERIC  # noqa
from ...types import REAL  # noqa
from ...types import SMALLINT  # noqa
from ...types import TEXT  # noqa
from ...types import TIMESTAMP  # noqa
from ...types import VARCHAR  # noqa


class _SQliteJson(JSON):
    def result_processor(self, dialect, coltype):
        default_processor = super().result_processor(dialect, coltype)

        def process(value):
            try:
                return default_processor(value)
            except TypeError:
                if isinstance(value, numbers.Number):
                    return value
                else:
                    raise

        return process


class _DateTimeMixin:
    _reg = None
    _storage_format = None

    def __init__(self, storage_format=None, regexp=None, **kw):
        super().__init__(**kw)
        if regexp is not None:
            self._reg = re.compile(regexp)
        if storage_format is not None:
            self._storage_format = storage_format

    @property
    def format_is_text_affinity(self):
        """return True if the storage format will automatically imply
        a TEXT affinity.

        If the storage format contains no non-numeric characters,
        it will imply a NUMERIC storage format on SQLite; in this case,
        the type will generate its DDL as DATE_CHAR, DATETIME_CHAR,
        TIME_CHAR.

        """
        spec = self._storage_format % {
            "year": 0,
            "month": 0,
            "day": 0,
            "hour": 0,
            "minute": 0,
            "second": 0,
            "microsecond": 0,
        }
        return bool(re.search(r"[^0-9]", spec))

    def adapt(self, cls, **kw):
        if issubclass(cls, _DateTimeMixin):
            if self._storage_format:
                kw["storage_format"] = self._storage_format
            if self._reg:
                kw["regexp"] = self._reg
        return super().adapt(cls, **kw)

    def literal_processor(self, dialect):
        bp = self.bind_processor(dialect)

        def process(value):
            return "'%s'" % bp(value)

        return process


class DATETIME(_DateTimeMixin, sqltypes.DateTime):
    r"""Represent a Python datetime object in SQLite using a string.

    The default string storage format is::

        "%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d.%(microsecond)06d"

    e.g.:

    .. sourcecode:: text

        2021-03-15 12:05:57.105542

    The incoming storage format is by default parsed using the
    Python ``datetime.fromisoformat()`` function.

    .. versionchanged:: 2.0  ``datetime.fromisoformat()`` is used for default
       datetime string parsing.

    The storage format can be customized to some degree using the
    ``storage_format`` and ``regexp`` parameters, such as::

        import re
        from sqlalchemy.dialects.sqlite import DATETIME

        dt = DATETIME(
            storage_format=(
                "%(year)04d/%(month)02d/%(day)02d %(hour)02d:%(minute)02d:%(second)02d"
            ),
            regexp=r"(\d+)/(\d+)/(\d+) (\d+)-(\d+)-(\d+)",
        )

    :param truncate_microseconds: when ``True`` microseconds will be truncated
     from the datetime. Can't be specified together with ``storage_format``
     or ``regexp``.

    :param storage_format: format string which will be applied to the dict
     with keys year, month, day, hour, minute, second, and microsecond.

    :param regexp: regular expression which will be applied to incoming result
     rows, replacing the use of ``datetime.fromisoformat()`` to parse incoming
     strings. If the regexp contains named groups, the resulting match dict is
     applied to the Python datetime() constructor as keyword arguments.
     Otherwise, if positional groups are used, the datetime() constructor
     is called with positional arguments via
     ``*map(int, match_obj.groups(0))``.

    """  # noqa

    _storage_format = (
        "%(year)04d-%(month)02d-%(day)02d "
        "%(hour)02d:%(minute)02d:%(second)02d.%(microsecond)06d"
    )

    def __init__(self, *args, **kwargs):
        truncate_microseconds = kwargs.pop("truncate_microseconds", False)
        super().__init__(*args, **kwargs)
        if truncate_microseconds:
            assert "storage_format" not in kwargs, (
                "You can specify only one of truncate_microseconds or storage_format."
            )
            assert "regexp" not in kwargs, (
                "You can specify only one of truncate_microseconds or regexp."
            )
            self._storage_format = (
                "%(year)04d-%(month)02d-%(day)02d %(hour)02d:%(minute)02d:%(second)02d"
            )

    def bind_processor(self, dialect):
        datetime_datetime = datetime.datetime
        datetime_date = datetime.date
        format_ = self._storage_format

        def process(value):
            if value is None:
                return None
            elif isinstance(value, datetime_datetime):
                return format_ % {
                    "year": value.year,
                    "month": value.month,
                    "day": value.day,
                    "hour": value.hour,
                    "minute": value.minute,
                    "second": value.second,
                    "microsecond": value.microsecond,
                }
            elif isinstance(value, datetime_date):
                return format_ % {
                    "year": value.year,
                    "month": value.month,
                    "day": value.day,
                    "hour": 0,
                    "minute": 0,
                    "second": 0,
                    "microsecond": 0,
                }
            else:
                raise TypeError(
                    "SQLite DateTime type only accepts Python "
                    "datetime and date objects as input."
                )

        return process

    def result_processor(self, dialect, coltype):
        if self._reg:
            return processors.str_to_datetime_processor_factory(
                self._reg, datetime.datetime
            )
        else:
            return processors.str_to_datetime


class DATE(_DateTimeMixin, sqltypes.Date):
    r"""Represent a Python date object in SQLite using a string.

    The default string storage format is::

        "%(year)04d-%(month)02d-%(day)02d"

    e.g.:

    .. sourcecode:: text

        2011-03-15

    The incoming storage format is by default parsed using the
    Python ``date.fromisoformat()`` function.

    .. versionchanged:: 2.0  ``date.fromisoformat()`` is used for default
       date string parsing.


    The storage format can be customized to some degree using the
    ``storage_format`` and ``regexp`` parameters, such as::

        import re
        from sqlalchemy.dialects.sqlite import DATE

        d = DATE(
            storage_format="%(month)02d/%(day)02d/%(year)04d",
            regexp=re.compile("(?P<month>\d+)/(?P<day>\d+)/(?P<year>\d+)"),
        )

    :param storage_format: format string which will be applied to the
     dict with keys year, month, and day.

    :param regexp: regular expression which will be applied to
     incoming result rows, replacing the use of ``date.fromisoformat()`` to
     parse incoming strings. If the regexp contains named groups, the resulting
     match dict is applied to the Python date() constructor as keyword
     arguments. Otherwise, if positional groups are used, the date()
     constructor is called with positional arguments via
     ``*map(int, match_obj.groups(0))``.

    """

    _storage_format = "%(year)04d-%(month)02d-%(day)02d"

    def bind_processor(self, dialect):
        datetime_date = datetime.date
        format_ = self._storage_format

        def process(value):
            if value is None:
                return None
            elif isinstance(value, datetime_date):
                return format_ % {
                    "year": value.year,
                    "month": value.month,
                    "day": value.day,
                }
            else:
                raise TypeError(
                    "SQLite Date type only accepts Python date objects as input."
                )

        return process

    def result_processor(self, dialect, coltype):
        if self._reg:
            return processors.str_to_datetime_processor_factory(
                self._reg, datetime.date
            )
        else:
            return processors.str_to_date


class TIME(_DateTimeMixin, sqltypes.Time):
    r"""Represent a Python time object in SQLite using a string.

    The default string storage format is::

        "%(hour)02d:%(minute)02d:%(second)02d.%(microsecond)06d"

    e.g.:

    .. sourcecode:: text

        12:05:57.10558

    The incoming storage format is by default parsed using the
    Python ``time.fromisoformat()`` function.

    .. versionchanged:: 2.0  ``time.fromisoformat()`` is used for default
       time string parsing.

    The storage format can be customized to some degree using the
    ``storage_format`` and ``regexp`` parameters, such as::

        import re
        from sqlalchemy.dialects.sqlite import TIME

        t = TIME(
            storage_format="%(hour)02d-%(minute)02d-%(second)02d-%(microsecond)06d",
            regexp=re.compile("(\d+)-(\d+)-(\d+)-(?:-(\d+))?"),
        )

    :param truncate_microseconds: when ``True`` microseconds will be truncated
     from the time. Can't be specified together with ``storage_format``
     or ``regexp``.

    :param storage_format: format string which will be applied to the dict
     with keys hour, minute, second, and microsecond.

    :param regexp: regular expression which will be applied to incoming result
     rows, replacing the use of ``datetime.fromisoformat()`` to parse incoming
     strings. If the regexp contains named groups, the resulting match dict is
     applied to the Python time() constructor as keyword arguments. Otherwise,
     if positional groups are used, the time() constructor is called with
     positional arguments via ``*map(int, match_obj.groups(0))``.

    """

    _storage_format = "%(hour)02d:%(minute)02d:%(second)02d.%(microsecond)06d"

    def __init__(self, *args, **kwargs):
        truncate_microseconds = kwargs.pop("truncate_microseconds", False)
        super().__init__(*args, **kwargs)
        if truncate_microseconds:
            assert "storage_format" not in kwargs, (
                "You can specify only one of truncate_microseconds or storage_format."
            )
            assert "regexp" not in kwargs, (
                "You can specify only one of truncate_microseconds or regexp."
            )
            self._storage_format = "%(hour)02d:%(minute)02d:%(second)02d"

    def bind_processor(self, dialect):
        datetime_time = datetime.time
        format_ = self._storage_format

        def process(value):
            if value is None:
                return None
            elif isinstance(value, datetime_time):
                return format_ % {
                    "hour": value.hour,
                    "minute": value.minute,
                    "second": value.second,
                    "microsecond": value.microsecond,
                }
            else:
                raise TypeError(
                    "SQLite Time type only accepts Python time objects as input."
                )

        return process

    def result_processor(self, dialect, coltype):
        if self._reg:
            return processors.str_to_datetime_processor_factory(
                self._reg, datetime.time
            )
        else:
            return processors.str_to_time


colspecs = {
    sqltypes.Date: DATE,
    sqltypes.DateTime: DATETIME,
    sqltypes.JSON: _SQliteJson,
    sqltypes.JSON.JSONIndexType: JSONIndexType,
    sqltypes.JSON.JSONPathType: JSONPathType,
    sqltypes.Time: TIME,
}

ischema_names = {
    "BIGINT": sqltypes.BIGINT,
    "BLOB": sqltypes.BLOB,
    "BOOL": sqltypes.BOOLEAN,
    "BOOLEAN": sqltypes.BOOLEAN,
    "CHAR": sqltypes.CHAR,
    "DATE": sqltypes.DATE,
    "DATE_CHAR": sqltypes.DATE,
    "DATETIME": sqltypes.DATETIME,
    "DATETIME_CHAR": sqltypes.DATETIME,
    "DOUBLE": sqltypes.DOUBLE,
    "DECIMAL": sqltypes.DECIMAL,
    "FLOAT": sqltypes.FLOAT,
    "INT": sqltypes.INTEGER,
    "INTEGER": sqltypes.INTEGER,
    "JSON": JSON,
    "NUMERIC": sqltypes.NUMERIC,
    "REAL": sqltypes.REAL,
    "SMALLINT": sqltypes.SMALLINT,
    "TEXT": sqltypes.TEXT,
    "TIME": sqltypes.TIME,
    "TIME_CHAR": sqltypes.TIME,
    "TIMESTAMP": sqltypes.TIMESTAMP,
    "VARCHAR": sqltypes.VARCHAR,
    "NVARCHAR": sqltypes.NVARCHAR,
    "NCHAR": sqltypes.NCHAR,
}


class SQLiteCompiler(compiler.SQLCompiler):
    extract_map = util.update_copy(
        compiler.SQLCompiler.extract_map,
        {
            "month": "%m",
            "day": "%d",
            "year": "%Y",
            "second": "%S",
            "hour": "%H",
            "doy": "%j",
            "minute": "%M",
            "epoch": "%s",
            "dow": "%w",
            "week": "%W",
        },
    )

    def visit_truediv_binary(self, binary, operator, **kw):
        return (
            self.process(binary.left, **kw)
            + " / "
            + "(%s + 0.0)" % self.process(binary.right, **kw)
        )

    def visit_now_func(self, fn, **kw):
        return "CURRENT_TIMESTAMP"

    def visit_localtimestamp_func(self, func, **kw):
        return 'DATETIME(CURRENT_TIMESTAMP, "localtime")'

    def visit_true(self, expr, **kw):
        return "1"

    def visit_false(self, expr, **kw):
        return "0"

    def visit_char_length_func(self, fn, **kw):
        return "length%s" % self.function_argspec(fn)

    def visit_aggregate_strings_func(self, fn, **kw):
        return "group_concat%s" % self.function_argspec(fn)

    def visit_cast(self, cast, **kwargs):
        if self.dialect.supports_cast:
            return super().visit_cast(cast, **kwargs)
        else:
            return self.process(cast.clause, **kwargs)

    def visit_extract(self, extract, **kw):
        try:
            return "CAST(STRFTIME('%s', %s) AS INTEGER)" % (
                self.extract_map[extract.field],
                self.process(extract.expr, **kw),
            )
        except KeyError as err:
            raise exc.CompileError(
                "%s is not a valid extract argument." % extract.field
            ) from err

    def returning_clause(
        self,
        stmt,
        returning_cols,
        *,
        populate_result_map,
        **kw,
    ):
        kw["include_table"] = False
        return super().returning_clause(
            stmt, returning_cols, populate_result_map=populate_result_map, **kw
        )

    def limit_clause(self, select, **kw):
        text = ""
        if select._limit_clause is not None:
            text += "\n LIMIT " + self.process(select._limit_clause, **kw)
        if select._offset_clause is not None:
            if select._limit_clause is None:
                text += "\n LIMIT " + self.process(sql.literal(-1))
            text += " OFFSET " + self.process(select._offset_clause, **kw)
        else:
            text += " OFFSET " + self.process(sql.literal(0), **kw)
        return text

    def for_update_clause(self, select, **kw):
        # sqlite has no "FOR UPDATE" AFAICT
        return ""

    def update_from_clause(
        self, update_stmt, from_table, extra_froms, from_hints, **kw
    ):
        kw["asfrom"] = True
        return "FROM " + ", ".join(
            t._compiler_dispatch(self, fromhints=from_hints, **kw) for t in extra_froms
        )

    def visit_is_distinct_from_binary(self, binary, operator, **kw):
        return "%s IS NOT %s" % (
            self.process(binary.left),
            self.process(binary.right),
        )

    def visit_is_not_distinct_from_binary(self, binary, operator, **kw):
        return "%s IS %s" % (
            self.process(binary.left),
            self.process(binary.right),
        )

    def visit_json_getitem_op_binary(self, binary, operator, **kw):
        if binary.type._type_affinity is sqltypes.JSON:
            expr = "JSON_QUOTE(JSON_EXTRACT(%s, %s))"
        else:
            expr = "JSON_EXTRACT(%s, %s)"

        return expr % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def visit_json_path_getitem_op_binary(self, binary, operator, **kw):
        if binary.type._type_affinity is sqltypes.JSON:
            expr = "JSON_QUOTE(JSON_EXTRACT(%s, %s))"
        else:
            expr = "JSON_EXTRACT(%s, %s)"

        return expr % (
            self.process(binary.left, **kw),
            self.process(binary.right, **kw),
        )

    def visit_empty_set_op_expr(self, type_, expand_op, **kw):
        # slightly old SQLite versions don't seem to be able to handle
        # the empty set impl
        return self.visit_empty_set_expr(type_)

    def visit_empty_set_expr(self, element_types, **kw):
        return "SELECT %s FROM (SELECT %s) WHERE 1!=1" % (
            ", ".join("1" for type_ in element_types or [INTEGER()]),
            ", ".join("1" for type_ in element_types or [INTEGER()]),
        )

    def visit_regexp_match_op_binary(self, binary, operator, **kw):
        return self._generate_generic_binary(binary, " REGEXP ", **kw)

    def visit_not_regexp_match_op_binary(self, binary, operator, **kw):
        return self._generate_generic_binary(binary, " NOT REGEXP ", **kw)

    def _on_conflict_target(self, clause, **kw):
        if clause.inferred_target_elements is not None:
            target_text = "(%s)" % ", ".join(
                (
                    self.preparer.quote(c)
                    if isinstance(c, str)
                    else self.process(c, include_table=False, use_schema=False)
                )
                for c in clause.inferred_target_elements
            )
            if clause.inferred_target_whereclause is not None:
                target_text += " WHERE %s" % self.process(
                    clause.inferred_target_whereclause,
                    include_table=False,
                    use_schema=False,
                    literal_execute=True,
                )

        else:
            target_text = ""

        return target_text

    def visit_on_conflict_do_nothing(self, on_conflict, **kw):
        target_text = self._on_conflict_target(on_conflict, **kw)

        if target_text:
            return "ON CONFLICT %s DO NOTHING" % target_text
        else:
            return "ON CONFLICT DO NOTHING"

    def visit_on_conflict_do_update(self, on_conflict, **kw):
        clause = on_conflict

        target_text = self._on_conflict_target(on_conflict, **kw)

        action_set_ops = []

        set_parameters = dict(clause.update_values_to_set)
        # create a list of column assignment clauses as tuples

        insert_statement = self.stack[-1]["selectable"]
        cols = insert_statement.table.c
        for c in cols:
            col_key = c.key

            if col_key in set_parameters:
                value = set_parameters.pop(col_key)
            elif c in set_parameters:
                value = set_parameters.pop(c)
            else:
                continue

            if isinstance(value, elements.BindParameter) and value.type._isnull:
                value = value._with_binary_element_type(c.type)
            value_text = self.process(value.self_group(), use_schema=False)

            key_text = self.preparer.quote(c.name)
            action_set_ops.append("%s = %s" % (key_text, value_text))

        # check for names that don't match columns
        if set_parameters:
            util.warn(
                "Additional column names not matching "
                "any column keys in table '%s': %s"
                % (
                    self.current_executable.table.name,
                    (", ".join("'%s'" % c for c in set_parameters)),
                )
            )
            for k, v in set_parameters.items():
                key_text = (
                    self.preparer.quote(k)
                    if isinstance(k, str)
                    else self.process(k, use_schema=False)
                )
                value_text = self.process(
                    coercions.expect(roles.ExpressionElementRole, v),
                    use_schema=False,
                )
                action_set_ops.append("%s = %s" % (key_text, value_text))

        action_text = ", ".join(action_set_ops)
        if clause.update_whereclause is not None:
            action_text += " WHERE %s" % self.process(
                clause.update_whereclause, include_table=True, use_schema=False
            )

        return "ON CONFLICT %s DO UPDATE SET %s" % (target_text, action_text)

    def visit_bitwise_xor_op_binary(self, binary, operator, **kw):
        # sqlite has no xor. Use "a XOR b" = "(a | b) - (a & b)".
        kw["eager_grouping"] = True
        or_ = self._generate_generic_binary(binary, " | ", **kw)
        and_ = self._generate_generic_binary(binary, " & ", **kw)
        return f"({or_} - {and_})"


class SQLiteDDLCompiler(compiler.DDLCompiler):
    def get_column_specification(self, column, **kwargs):
        coltype = self.dialect.type_compiler_instance.process(
            column.type, type_expression=column
        )
        colspec = self.preparer.format_column(column) + " " + coltype
        default = self.get_column_default_string(column)
        if default is not None:
            if not re.match(r"""^\s*[\'\"\(]""", default) and re.match(
                r".*\W.*", default
            ):
                colspec += f" DEFAULT ({default})"
            else:
                colspec += f" DEFAULT {default}"

        if not column.nullable:
            colspec += " NOT NULL"

            on_conflict_clause = column.dialect_options["sqlite"][
                "on_conflict_not_null"
            ]
            if on_conflict_clause is not None:
                colspec += " ON CONFLICT " + on_conflict_clause

        if column.primary_key:
            if (
                column.autoincrement is True
                and len(column.table.primary_key.columns) != 1
            ):
                raise exc.CompileError(
                    "SQLite does not support autoincrement for composite primary keys"
                )

            if (
                column.table.dialect_options["sqlite"]["autoincrement"]
                and len(column.table.primary_key.columns) == 1
                and issubclass(column.type._type_affinity, sqltypes.Integer)
                and not column.foreign_keys
            ):
                colspec += " PRIMARY KEY"

                on_conflict_clause = column.dialect_options["sqlite"][
                    "on_conflict_primary_key"
                ]
                if on_conflict_clause is not None:
                    colspec += " ON CONFLICT " + on_conflict_clause

                colspec += " AUTOINCREMENT"

        if column.computed is not None:
            colspec += " " + self.process(column.computed)

        return colspec

    def visit_primary_key_constraint(self, constraint, **kw):
        # for columns with sqlite_autoincrement=True,
        # the PRIMARY KEY constraint can only be inline
        # with the column itself.
        if len(constraint.columns) == 1:
            c = list(constraint)[0]
            if (
                c.primary_key
                and c.table.dialect_options["sqlite"]["autoincrement"]
                and issubclass(c.type._type_affinity, sqltypes.Integer)
                and not c.foreign_keys
            ):
                return None

        text = super().visit_primary_key_constraint(constraint)

        on_conflict_clause = constraint.dialect_options["sqlite"]["on_conflict"]
        if on_conflict_clause is None and len(constraint.columns) == 1:
            on_conflict_clause = list(constraint)[0].dialect_options["sqlite"][
                "on_conflict_primary_key"
            ]

        if on_conflict_clause is not None:
            text += " ON CONFLICT " + on_conflict_clause

        return text

    def visit_unique_constraint(self, constraint, **kw):
        text = super().visit_unique_constraint(constraint)

        on_conflict_clause = constraint.dialect_options["sqlite"]["on_conflict"]
        if on_conflict_clause is None and len(constraint.columns) == 1:
            col1 = list(constraint)[0]
            if isinstance(col1, schema.SchemaItem):
                on_conflict_clause = list(constraint)[0].dialect_options["sqlite"][
                    "on_conflict_unique"
                ]

        if on_conflict_clause is not None:
            text += " ON CONFLICT " + on_conflict_clause

        return text

    def visit_check_constraint(self, constraint, **kw):
        text = super().visit_check_constraint(constraint)

        on_conflict_clause = constraint.dialect_options["sqlite"]["on_conflict"]

        if on_conflict_clause is not None:
            text += " ON CONFLICT " + on_conflict_clause

        return text

    def visit_column_check_constraint(self, constraint, **kw):
        text = super().visit_column_check_constraint(constraint)

        if constraint.dialect_options["sqlite"]["on_conflict"] is not None:
            raise exc.CompileError(
                "SQLite does not support on conflict clause for column check constraint"
            )

        return text

    def visit_foreign_key_constraint(self, constraint, **kw):
        local_table = constraint.elements[0].parent.table
        remote_table = constraint.elements[0].column.table

        if local_table.schema != remote_table.schema:
            return None
        else:
            return super().visit_foreign_key_constraint(constraint)

    def define_constraint_remote_table(self, constraint, table, preparer):
        """Format the remote table clause of a CREATE CONSTRAINT clause."""

        return preparer.format_table(table, use_schema=False)

    def visit_create_index(
        self, create, include_schema=False, include_table_schema=True, **kw
    ):
        index = create.element
        self._verify_index_table(index)
        preparer = self.preparer
        text = "CREATE "
        if index.unique:
            text += "UNIQUE "

        text += "INDEX "

        if create.if_not_exists:
            text += "IF NOT EXISTS "

        text += "%s ON %s (%s)" % (
            self._prepared_index_name(index, include_schema=True),
            preparer.format_table(index.table, use_schema=False),
            ", ".join(
                self.sql_compiler.process(expr, include_table=False, literal_binds=True)
                for expr in index.expressions
            ),
        )

        whereclause = index.dialect_options["sqlite"]["where"]
        if whereclause is not None:
            where_compiled = self.sql_compiler.process(
                whereclause, include_table=False, literal_binds=True
            )
            text += " WHERE " + where_compiled

        return text

    def post_create_table(self, table):
        table_options = []

        if not table.dialect_options["sqlite"]["with_rowid"]:
            table_options.append("WITHOUT ROWID")

        if table.dialect_options["sqlite"]["strict"]:
            table_options.append("STRICT")

        if table_options:
            return "\n " + ",\n ".join(table_options)
        else:
            return ""


class SQLiteTypeCompiler(compiler.GenericTypeCompiler):
    def visit_large_binary(self, type_, **kw):
        return self.visit_BLOB(type_)

    def visit_DATETIME(self, type_, **kw):
        if not isinstance(type_, _DateTimeMixin) or type_.format_is_text_affinity:
            return super().visit_DATETIME(type_)
        else:
            return "DATETIME_CHAR"

    def visit_DATE(self, type_, **kw):
        if not isinstance(type_, _DateTimeMixin) or type_.format_is_text_affinity:
            return super().visit_DATE(type_)
        else:
            return "DATE_CHAR"

    def visit_TIME(self, type_, **kw):
        if not isinstance(type_, _DateTimeMixin) or type_.format_is_text_affinity:
            return super().visit_TIME(type_)
        else:
            return "TIME_CHAR"

    def visit_JSON(self, type_, **kw):
        # note this name provides NUMERIC affinity, not TEXT.
        # should not be an issue unless the JSON value consists of a single
        # numeric value.   JSONTEXT can be used if this case is required.
        return "JSON"


class SQLiteIdentifierPreparer(compiler.IdentifierPreparer):
    reserved_words = {
        "add",
        "after",
        "all",
        "alter",
        "analyze",
        "and",
        "as",
        "asc",
        "attach",
        "autoincrement",
        "before",
        "begin",
        "between",
        "by",
        "cascade",
        "case",
        "cast",
        "check",
        "collate",
        "column",
        "commit",
        "conflict",
        "constraint",
        "create",
        "cross",
        "current_date",
        "current_time",
        "current_timestamp",
        "database",
        "default",
        "deferrable",
        "deferred",
        "delete",
        "desc",
        "detach",
        "distinct",
        "drop",
        "each",
        "else",
        "end",
        "escape",
        "except",
        "exclusive",
        "exists",
        "explain",
        "false",
        "fail",
        "for",
        "foreign",
        "from",
        "full",
        "glob",
        "group",
        "having",
        "if",
        "ignore",
        "immediate",
        "in",
        "index",
        "indexed",
        "initially",
        "inner",
        "insert",
        "instead",
        "intersect",
        "into",
        "is",
        "isnull",
        "join",
        "key",
        "left",
        "like",
        "limit",
        "match",
        "natural",
        "not",
        "notnull",
        "null",
        "of",
        "offset",
        "on",
        "or",
        "order",
        "outer",
        "plan",
        "pragma",
        "primary",
        "query",
        "raise",
        "references",
        "reindex",
        "rename",
        "replace",
        "restrict",
        "right",
        "rollback",
        "row",
        "select",
        "set",
        "table",
        "temp",
        "temporary",
        "then",
        "to",
        "transaction",
        "trigger",
        "true",
        "union",
        "unique",
        "update",
        "using",
        "vacuum",
        "values",
        "view",
        "virtual",
        "when",
        "where",
    }


class SQLiteExecutionContext(default.DefaultExecutionContext):
    @util.memoized_property
    def _preserve_raw_colnames(self):
        return not self.dialect._broken_dotted_colnames or self.execution_options.get(
            "sqlite_raw_colnames", False
        )

    def _translate_colname(self, colname):
        # TODO: detect SQLite version 3.10.0 or greater;
        # see [ticket:3633]

        # adjust for dotted column names.  SQLite
        # in the case of UNION may store col names as
        # "tablename.colname", or if using an attached database,
        # "database.tablename.colname", in cursor.description
        if not self._preserve_raw_colnames and "." in colname:
            return colname.split(".")[-1], colname
        else:
            return colname, None


class SQLiteDialect(default.DefaultDialect):
    name = "sqlite"
    supports_alter = False

    # SQlite supports "DEFAULT VALUES" but *does not* support
    # "VALUES (DEFAULT)"
    supports_default_values = True
    supports_default_metavalue = False

    # sqlite issue:
    # https://github.com/python/cpython/issues/93421
    # note this parameter is no longer used by the ORM or default dialect
    # see #9414
    supports_sane_rowcount_returning = False

    supports_empty_insert = False
    supports_cast = True
    supports_multivalues_insert = True
    use_insertmanyvalues = True
    tuple_in_values = True
    supports_statement_cache = True
    insert_null_pk_still_autoincrements = True
    insert_returning = True
    update_returning = True
    update_returning_multifrom = True
    delete_returning = True
    update_returning_multifrom = True

    supports_default_metavalue = True
    """dialect supports INSERT... VALUES (DEFAULT) syntax"""

    default_metavalue_token = "NULL"
    """for INSERT... VALUES (DEFAULT) syntax, the token to put in the
    parenthesis."""

    default_paramstyle = "qmark"
    execution_ctx_cls = SQLiteExecutionContext
    statement_compiler = SQLiteCompiler
    ddl_compiler = SQLiteDDLCompiler
    type_compiler_cls = SQLiteTypeCompiler
    preparer = SQLiteIdentifierPreparer
    ischema_names = ischema_names
    colspecs = colspecs

    construct_arguments = [
        (
            sa_schema.Table,
            {
                "autoincrement": False,
                "with_rowid": True,
                "strict": False,
            },
        ),
        (sa_schema.Index, {"where": None}),
        (
            sa_schema.Column,
            {
                "on_conflict_primary_key": None,
                "on_conflict_not_null": None,
                "on_conflict_unique": None,
            },
        ),
        (sa_schema.Constraint, {"on_conflict": None}),
    ]

    _broken_fk_pragma_quotes = False
    _broken_dotted_colnames = False

    def __init__(
        self,
        native_datetime=False,
        json_serializer=None,
        json_deserializer=None,
        **kwargs,
    ):
        default.DefaultDialect.__init__(self, **kwargs)

        self._json_serializer = json_serializer
        self._json_deserializer = json_deserializer

        # this flag used by pysqlite dialect, and perhaps others in the
        # future, to indicate the driver is handling date/timestamp
        # conversions (and perhaps datetime/time as well on some hypothetical
        # driver ?)
        self.native_datetime = native_datetime

        if self.dbapi is not None:
            if self.dbapi.sqlite_version_info < (3, 7, 16):
                util.warn(
                    "SQLite version %s is older than 3.7.16, and will not "
                    "support right nested joins, as are sometimes used in "
                    "more complex ORM scenarios.  SQLAlchemy 1.4 and above "
                    "no longer tries to rewrite these joins."
                    % (self.dbapi.sqlite_version_info,)
                )

            # NOTE: python 3.7 on fedora for me has SQLite 3.34.1.  These
            # version checks are getting very stale.
            self._broken_dotted_colnames = self.dbapi.sqlite_version_info < (
                3,
                10,
                0,
            )
            self.supports_default_values = self.dbapi.sqlite_version_info >= (
                3,
                3,
                8,
            )
            self.supports_cast = self.dbapi.sqlite_version_info >= (3, 2, 3)
            self.supports_multivalues_insert = (
                # https://www.sqlite.org/releaselog/3_7_11.html
                self.dbapi.sqlite_version_info >= (3, 7, 11)
            )
            # see https://www.sqlalchemy.org/trac/ticket/2568
            # as well as https://www.sqlite.org/src/info/600482d161
            self._broken_fk_pragma_quotes = self.dbapi.sqlite_version_info < (
                3,
                6,
                14,
            )

            if self.dbapi.sqlite_version_info < (3, 35) or util.pypy:
                self.update_returning = self.delete_returning = (
                    self.insert_returning
                ) = False

            if self.dbapi.sqlite_version_info < (3, 32, 0):
                # https://www.sqlite.org/limits.html
                self.insertmanyvalues_max_parameters = 999

    _isolation_lookup = util.immutabledict({"READ UNCOMMITTED": 1, "SERIALIZABLE": 0})

    def get_isolation_level_values(self, dbapi_connection):
        return list(self._isolation_lookup)

    def set_isolation_level(self, dbapi_connection, level):
        isolation_level = self._isolation_lookup[level]

        cursor = dbapi_connection.cursor()
        cursor.execute(f"PRAGMA read_uncommitted = {isolation_level}")
        cursor.close()

    def get_isolation_level(self, dbapi_connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA read_uncommitted")
        res = cursor.fetchone()
        if res:
            value = res[0]
        else:
            # https://www.sqlite.org/changes.html#version_3_3_3
            # "Optional READ UNCOMMITTED isolation (instead of the
            # default isolation level of SERIALIZABLE) and
            # table level locking when database connections
            # share a common cache.""
            # pre-SQLite 3.3.0 default to 0
            value = 0
        cursor.close()
        if value == 0:
            return "SERIALIZABLE"
        elif value == 1:
            return "READ UNCOMMITTED"
        else:
            assert False, "Unknown isolation level %s" % value

    @reflection.cache
    def get_schema_names(self, connection, **kw):
        s = "PRAGMA database_list"
        dl = connection.exec_driver_sql(s)

        return [db[1] for db in dl if db[1] != "temp"]

    def _format_schema(self, schema, table_name):
        if schema is not None:
            qschema = self.identifier_preparer.quote_identifier(schema)
            name = f"{qschema}.{table_name}"
        else:
            name = table_name
        return name

    def _sqlite_main_query(
        self,
        table: str,
        type_: str,
        schema: Optional[str],
        sqlite_include_internal: bool,
    ):
        main = self._format_schema(schema, table)
        if not sqlite_include_internal:
            filter_table = " AND name NOT LIKE 'sqlite~_%' ESCAPE '~'"
        else:
            filter_table = ""
        query = (
            f"SELECT name FROM {main} WHERE type='{type_}'{filter_table} ORDER BY name"
        )
        return query

    @reflection.cache
    def get_table_names(
        self, connection, schema=None, sqlite_include_internal=False, **kw
    ):
        query = self._sqlite_main_query(
            "sqlite_master", "table", schema, sqlite_include_internal
        )
        names = connection.exec_driver_sql(query).scalars().all()
        return names

    @reflection.cache
    def get_temp_table_names(self, connection, sqlite_include_internal=False, **kw):
        query = self._sqlite_main_query(
            "sqlite_temp_master", "table", None, sqlite_include_internal
        )
        names = connection.exec_driver_sql(query).scalars().all()
        return names

    @reflection.cache
    def get_temp_view_names(self, connection, sqlite_include_internal=False, **kw):
        query = self._sqlite_main_query(
            "sqlite_temp_master", "view", None, sqlite_include_internal
        )
        names = connection.exec_driver_sql(query).scalars().all()
        return names

    @reflection.cache
    def has_table(self, connection, table_name, schema=None, **kw):
        self._ensure_has_table_connection(connection)

        if schema is not None and schema not in self.get_schema_names(connection, **kw):
            return False

        info = self._get_table_pragma(
            connection, "table_info", table_name, schema=schema
        )
        return bool(info)

    def _get_default_schema_name(self, connection):
        return "main"

    @reflection.cache
    def get_view_names(
        self, connection, schema=None, sqlite_include_internal=False, **kw
    ):
        query = self._sqlite_main_query(
            "sqlite_master", "view", schema, sqlite_include_internal
        )
        names = connection.exec_driver_sql(query).scalars().all()
        return names

    @reflection.cache
    def get_view_definition(self, connection, view_name, schema=None, **kw):
        if schema is not None:
            qschema = self.identifier_preparer.quote_identifier(schema)
            master = f"{qschema}.sqlite_master"
            s = ("SELECT sql FROM %s WHERE name = ? AND type='view'") % (master,)
            rs = connection.exec_driver_sql(s, (view_name,))
        else:
            try:
                s = (
                    "SELECT sql FROM "
                    " (SELECT * FROM sqlite_master UNION ALL "
                    "  SELECT * FROM sqlite_temp_master) "
                    "WHERE name = ? "
                    "AND type='view'"
                )
                rs = connection.exec_driver_sql(s, (view_name,))
            except exc.DBAPIError:
                s = "SELECT sql FROM sqlite_master WHERE name = ? AND type='view'"
                rs = connection.exec_driver_sql(s, (view_name,))

        result = rs.fetchall()
        if result:
            return result[0].sql
        else:
            raise exc.NoSuchTableError(f"{schema}.{view_name}" if schema else view_name)

    @reflection.cache
    def get_columns(self, connection, table_name, schema=None, **kw):
        pragma = "table_info"
        # computed columns are threaded as hidden, they require table_xinfo
        if self.server_version_info >= (3, 31):
            pragma = "table_xinfo"
        info = self._get_table_pragma(connection, pragma, table_name, schema=schema)
        columns = []
        tablesql = None
        for row in info:
            name = row[1]
            type_ = row[2].upper()
            nullable = not row[3]
            default = row[4]
            primary_key = row[5]
            hidden = row[6] if pragma == "table_xinfo" else 0

            # hidden has value 0 for normal columns, 1 for hidden columns,
            # 2 for computed virtual columns and 3 for computed stored columns
            # https://www.sqlite.org/src/info/069351b85f9a706f60d3e98fbc8aaf40c374356b967c0464aede30ead3d9d18b
            if hidden == 1:
                continue

            generated = bool(hidden)
            persisted = hidden == 3

            if tablesql is None and generated:
                tablesql = self._get_table_sql(connection, table_name, schema, **kw)
                # remove create table
                match = re.match(
                    r"create table .*?\((.*)\)$",
                    tablesql.strip(),
                    re.DOTALL | re.IGNORECASE,
                )
                assert match, f"create table not found in {tablesql}"
                tablesql = match.group(1).strip()

            columns.append(
                self._get_column_info(
                    name,
                    type_,
                    nullable,
                    default,
                    primary_key,
                    generated,
                    persisted,
                    tablesql,
                )
            )
        if columns:
            return columns
        elif not self.has_table(connection, table_name, schema):
            raise exc.NoSuchTableError(
                f"{schema}.{table_name}" if schema else table_name
            )
        else:
            return ReflectionDefaults.columns()

    def _get_column_info(
        self,
        name,
        type_,
        nullable,
        default,
        primary_key,
        generated,
        persisted,
        tablesql,
    ):
        if generated:
            # the type of a column "cc INTEGER GENERATED ALWAYS AS (1 + 42)"
            # somehow is "INTEGER GENERATED ALWAYS"
            type_ = re.sub("generated", "", type_, flags=re.IGNORECASE)
            type_ = re.sub("always", "", type_, flags=re.IGNORECASE).strip()

        coltype = self._resolve_type_affinity(type_)

        if default is not None:
            default = str(default)

        colspec = {
            "name": name,
            "type": coltype,
            "nullable": nullable,
            "default": default,
            "primary_key": primary_key,
        }
        if generated:
            sqltext = ""
            if tablesql:
                pattern = (
                    r"[^,]*\s+GENERATED\s+ALWAYS\s+AS"
                    r"\s+\((.*)\)\s*(?:virtual|stored)?"
                )
                match = re.search(re.escape(name) + pattern, tablesql, re.IGNORECASE)
                if match:
                    sqltext = match.group(1)
            colspec["computed"] = {"sqltext": sqltext, "persisted": persisted}
        return colspec

    def _resolve_type_affinity(self, type_):
        """Return a data type from a reflected column, using affinity rules.

        SQLite's goal for universal compatibility introduces some complexity
        during reflection, as a column's defined type might not actually be a
        type that SQLite understands - or indeed, my not be defined *at all*.
        Internally, SQLite handles this with a 'data type affinity' for each
        column definition, mapping to one of 'TEXT', 'NUMERIC', 'INTEGER',
        'REAL', or 'NONE' (raw bits). The algorithm that determines this is
        listed in https://www.sqlite.org/datatype3.html section 2.1.

        This method allows SQLAlchemy to support that algorithm, while still
        providing access to smarter reflection utilities by recognizing
        column definitions that SQLite only supports through affinity (like
        DATE and DOUBLE).

        """
        match = re.match(r"([\w ]+)(\(.*?\))?", type_)
        if match:
            coltype = match.group(1)
            args = match.group(2)
        else:
            coltype = ""
            args = ""

        if coltype in self.ischema_names:
            coltype = self.ischema_names[coltype]
        elif "INT" in coltype:
            coltype = sqltypes.INTEGER
        elif "CHAR" in coltype or "CLOB" in coltype or "TEXT" in coltype:
            coltype = sqltypes.TEXT
        elif "BLOB" in coltype or not coltype:
            coltype = sqltypes.NullType
        elif "REAL" in coltype or "FLOA" in coltype or "DOUB" in coltype:
            coltype = sqltypes.REAL
        else:
            coltype = sqltypes.NUMERIC

        if args is not None:
            args = re.findall(r"(\d+)", args)
            try:
                coltype = coltype(*[int(a) for a in args])
            except TypeError:
                util.warn(
                    "Could not instantiate type %s with "
                    "reflected arguments %s; using no arguments." % (coltype, args)
                )
                coltype = coltype()
        else:
            coltype = coltype()

        return coltype

    @reflection.cache
    def get_pk_constraint(self, connection, table_name, schema=None, **kw):
        constraint_name = None
        table_data = self._get_table_sql(connection, table_name, schema=schema)
        if table_data:
            PK_PATTERN = r"CONSTRAINT (\w+) PRIMARY KEY"
            result = re.search(PK_PATTERN, table_data, re.I)
            constraint_name = result.group(1) if result else None

        cols = self.get_columns(connection, table_name, schema, **kw)
        # consider only pk columns. This also avoids sorting the cached
        # value returned by get_columns
        cols = [col for col in cols if col.get("primary_key", 0) > 0]
        cols.sort(key=lambda col: col.get("primary_key"))
        pkeys = [col["name"] for col in cols]

        if pkeys:
            return {"constrained_columns": pkeys, "name": constraint_name}
        else:
            return ReflectionDefaults.pk_constraint()

    @reflection.cache
    def get_foreign_keys(self, connection, table_name, schema=None, **kw):
        # sqlite makes this *extremely difficult*.
        # First, use the pragma to get the actual FKs.
        pragma_fks = self._get_table_pragma(
            connection, "foreign_key_list", table_name, schema=schema
        )

        fks = {}

        for row in pragma_fks:
            (numerical_id, rtbl, lcol, rcol) = (row[0], row[2], row[3], row[4])

            if not rcol:
                # no referred column, which means it was not named in the
                # original DDL.  The referred columns of the foreign key
                # constraint are therefore the primary key of the referred
                # table.
                try:
                    referred_pk = self.get_pk_constraint(
                        connection, rtbl, schema=schema, **kw
                    )
                    referred_columns = referred_pk["constrained_columns"]
                except exc.NoSuchTableError:
                    # ignore not existing parents
                    referred_columns = []
            else:
                # note we use this list only if this is the first column
                # in the constraint.  for subsequent columns we ignore the
                # list and append "rcol" if present.
                referred_columns = []

            if self._broken_fk_pragma_quotes:
                rtbl = re.sub(r"^[\"\[`\']|[\"\]`\']$", "", rtbl)

            if numerical_id in fks:
                fk = fks[numerical_id]
            else:
                fk = fks[numerical_id] = {
                    "name": None,
                    "constrained_columns": [],
                    "referred_schema": schema,
                    "referred_table": rtbl,
                    "referred_columns": referred_columns,
                    "options": {},
                }
                fks[numerical_id] = fk

            fk["constrained_columns"].append(lcol)

            if rcol:
                fk["referred_columns"].append(rcol)

        def fk_sig(constrained_columns, referred_table, referred_columns):
            return (
                tuple(constrained_columns) + (referred_table,) + tuple(referred_columns)
            )

        # then, parse the actual SQL and attempt to find DDL that matches
        # the names as well.   SQLite saves the DDL in whatever format
        # it was typed in as, so need to be liberal here.

        keys_by_signature = {
            fk_sig(
                fk["constrained_columns"],
                fk["referred_table"],
                fk["referred_columns"],
            ): fk
            for fk in fks.values()
        }

        table_data = self._get_table_sql(connection, table_name, schema=schema)

        def parse_fks():
            if table_data is None:
                # system tables, etc.
                return

            # note that we already have the FKs from PRAGMA above.  This whole
            # regexp thing is trying to locate additional detail about the
            # FKs, namely the name of the constraint and other options.
            # so parsing the columns is really about matching it up to what
            # we already have.
            FK_PATTERN = (
                r"(?:CONSTRAINT (\w+) +)?"
                r"FOREIGN KEY *\( *(.+?) *\) +"
                r'REFERENCES +(?:(?:"(.+?)")|([a-z0-9_]+)) *\( *((?:(?:"[^"]+"|[a-z0-9_]+) *(?:, *)?)+)\) *'  # noqa: E501
                r"((?:ON (?:DELETE|UPDATE) "
                r"(?:SET NULL|SET DEFAULT|CASCADE|RESTRICT|NO ACTION) *)*)"
                r"((?:NOT +)?DEFERRABLE)?"
                r"(?: +INITIALLY +(DEFERRED|IMMEDIATE))?"
            )
            for match in re.finditer(FK_PATTERN, table_data, re.I):
                (
                    constraint_name,
                    constrained_columns,
                    referred_quoted_name,
                    referred_name,
                    referred_columns,
                    onupdatedelete,
                    deferrable,
                    initially,
                ) = match.group(1, 2, 3, 4, 5, 6, 7, 8)
                constrained_columns = list(self._find_cols_in_sig(constrained_columns))
                if not referred_columns:
                    referred_columns = constrained_columns
                else:
                    referred_columns = list(self._find_cols_in_sig(referred_columns))
                referred_name = referred_quoted_name or referred_name
                options = {}

                for token in re.split(r" *\bON\b *", onupdatedelete.upper()):
                    if token.startswith("DELETE"):
                        ondelete = token[6:].strip()
                        if ondelete and ondelete != "NO ACTION":
                            options["ondelete"] = ondelete
                    elif token.startswith("UPDATE"):
                        onupdate = token[6:].strip()
                        if onupdate and onupdate != "NO ACTION":
                            options["onupdate"] = onupdate

                if deferrable:
                    options["deferrable"] = "NOT" not in deferrable.upper()
                if initially:
                    options["initially"] = initially.upper()

                yield (
                    constraint_name,
                    constrained_columns,
                    referred_name,
                    referred_columns,
                    options,
                )

        fkeys = []

        for (
            constraint_name,
            constrained_columns,
            referred_name,
            referred_columns,
            options,
        ) in parse_fks():
            sig = fk_sig(constrained_columns, referred_name, referred_columns)
            if sig not in keys_by_signature:
                util.warn(
                    "WARNING: SQL-parsed foreign key constraint "
                    "'%s' could not be located in PRAGMA "
                    "foreign_keys for table %s" % (sig, table_name)
                )
                continue
            key = keys_by_signature.pop(sig)
            key["name"] = constraint_name
            key["options"] = options
            fkeys.append(key)
        # assume the remainders are the unnamed, inline constraints, just
        # use them as is as it's extremely difficult to parse inline
        # constraints
        fkeys.extend(keys_by_signature.values())
        if fkeys:
            return fkeys
        else:
            return ReflectionDefaults.foreign_keys()

    def _find_cols_in_sig(self, sig):
        for match in re.finditer(r'(?:"(.+?)")|([a-z0-9_]+)', sig, re.I):
            yield match.group(1) or match.group(2)

    @reflection.cache
    def get_unique_constraints(self, connection, table_name, schema=None, **kw):
        auto_index_by_sig = {}
        for idx in self.get_indexes(
            connection,
            table_name,
            schema=schema,
            include_auto_indexes=True,
            **kw,
        ):
            if not idx["name"].startswith("sqlite_autoindex"):
                continue
            sig = tuple(idx["column_names"])
            auto_index_by_sig[sig] = idx

        table_data = self._get_table_sql(connection, table_name, schema=schema, **kw)
        unique_constraints = []

        def parse_uqs():
            if table_data is None:
                return
            UNIQUE_PATTERN = r'(?:CONSTRAINT "?(.+?)"? +)?UNIQUE *\((.+?)\)'
            INLINE_UNIQUE_PATTERN = (
                r'(?:(".+?")|(?:[\[`])?([a-z0-9_]+)(?:[\]`])?)[\t ]'
                r"+[a-z0-9_ ]+?[\t ]+UNIQUE"
            )

            for match in re.finditer(UNIQUE_PATTERN, table_data, re.I):
                name, cols = match.group(1, 2)
                yield name, list(self._find_cols_in_sig(cols))

            # we need to match inlines as well, as we seek to differentiate
            # a UNIQUE constraint from a UNIQUE INDEX, even though these
            # are kind of the same thing :)
            for match in re.finditer(INLINE_UNIQUE_PATTERN, table_data, re.I):
                cols = list(self._find_cols_in_sig(match.group(1) or match.group(2)))
                yield None, cols

        for name, cols in parse_uqs():
            sig = tuple(cols)
            if sig in auto_index_by_sig:
                auto_index_by_sig.pop(sig)
                parsed_constraint = {"name": name, "column_names": cols}
                unique_constraints.append(parsed_constraint)
        # NOTE: auto_index_by_sig might not be empty here,
        # the PRIMARY KEY may have an entry.
        if unique_constraints:
            return unique_constraints
        else:
            return ReflectionDefaults.unique_constraints()

    @reflection.cache
    def get_check_constraints(self, connection, table_name, schema=None, **kw):
        table_data = self._get_table_sql(connection, table_name, schema=schema, **kw)

        # NOTE NOTE NOTE
        # DO NOT CHANGE THIS REGULAR EXPRESSION.   There is no known way
        # to parse CHECK constraints that contain newlines themselves using
        # regular expressions, and the approach here relies upon each
        # individual
        # CHECK constraint being on a single line by itself.   This
        # necessarily makes assumptions as to how the CREATE TABLE
        # was emitted.   A more comprehensive DDL parsing solution would be
        # needed to improve upon the current situation. See #11840 for
        # background
        CHECK_PATTERN = r"(?:CONSTRAINT (.+) +)?CHECK *\( *(.+) *\),? *"
        cks = []

        for match in re.finditer(CHECK_PATTERN, table_data or "", re.I):
            name = match.group(1)

            if name:
                name = re.sub(r'^"|"$', "", name)

            cks.append({"sqltext": match.group(2), "name": name})
        cks.sort(key=lambda d: d["name"] or "~")  # sort None as last
        if cks:
            return cks
        else:
            return ReflectionDefaults.check_constraints()

    @reflection.cache
    def get_indexes(self, connection, table_name, schema=None, **kw):
        pragma_indexes = self._get_table_pragma(
            connection, "index_list", table_name, schema=schema
        )
        indexes = []

        # regular expression to extract the filter predicate of a partial
        # index. this could fail to extract the predicate correctly on
        # indexes created like
        #   CREATE INDEX i ON t (col || ') where') WHERE col <> ''
        # but as this function does not support expression-based indexes
        # this case does not occur.
        partial_pred_re = re.compile(r"\)\s+where\s+(.+)", re.IGNORECASE)

        if schema:
            schema_expr = "%s." % self.identifier_preparer.quote_identifier(schema)
        else:
            schema_expr = ""

        include_auto_indexes = kw.pop("include_auto_indexes", False)
        for row in pragma_indexes:
            # ignore implicit primary key index.
            # https://www.mail-archive.com/sqlite-users@sqlite.org/msg30517.html
            if not include_auto_indexes and row[1].startswith("sqlite_autoindex"):
                continue
            indexes.append(
                dict(
                    name=row[1],
                    column_names=[],
                    unique=row[2],
                    dialect_options={},
                )
            )

            # check partial indexes
            if len(row) >= 5 and row[4]:
                s = (
                    "SELECT sql FROM %(schema)ssqlite_master "
                    "WHERE name = ? "
                    "AND type = 'index'" % {"schema": schema_expr}
                )
                rs = connection.exec_driver_sql(s, (row[1],))
                index_sql = rs.scalar()
                predicate_match = partial_pred_re.search(index_sql)
                if predicate_match is None:
                    # unless the regex is broken this case shouldn't happen
                    # because we know this is a partial index, so the
                    # definition sql should match the regex
                    util.warn(
                        "Failed to look up filter predicate of "
                        "partial index %s" % row[1]
                    )
                else:
                    predicate = predicate_match.group(1)
                    indexes[-1]["dialect_options"]["sqlite_where"] = text(predicate)

        # loop thru unique indexes to get the column names.
        for idx in list(indexes):
            pragma_index = self._get_table_pragma(
                connection, "index_info", idx["name"], schema=schema
            )

            for row in pragma_index:
                if row[2] is None:
                    util.warn(
                        "Skipped unsupported reflection of "
                        "expression-based index %s" % idx["name"]
                    )
                    indexes.remove(idx)
                    break
                else:
                    idx["column_names"].append(row[2])

        indexes.sort(key=lambda d: d["name"] or "~")  # sort None as last
        if indexes:
            return indexes
        elif not self.has_table(connection, table_name, schema):
            raise exc.NoSuchTableError(
                f"{schema}.{table_name}" if schema else table_name
            )
        else:
            return ReflectionDefaults.indexes()

    def _is_sys_table(self, table_name):
        return table_name in {
            "sqlite_schema",
            "sqlite_master",
            "sqlite_temp_schema",
            "sqlite_temp_master",
        }

    @reflection.cache
    def _get_table_sql(self, connection, table_name, schema=None, **kw):
        if schema:
            schema_expr = "%s." % (self.identifier_preparer.quote_identifier(schema))
        else:
            schema_expr = ""
        try:
            s = (
                "SELECT sql FROM "
                " (SELECT * FROM %(schema)ssqlite_master UNION ALL "
                "  SELECT * FROM %(schema)ssqlite_temp_master) "
                "WHERE name = ? "
                "AND type in ('table', 'view')" % {"schema": schema_expr}
            )
            rs = connection.exec_driver_sql(s, (table_name,))
        except exc.DBAPIError:
            s = (
                "SELECT sql FROM %(schema)ssqlite_master "
                "WHERE name = ? "
                "AND type in ('table', 'view')" % {"schema": schema_expr}
            )
            rs = connection.exec_driver_sql(s, (table_name,))
        value = rs.scalar()
        if value is None and not self._is_sys_table(table_name):
            raise exc.NoSuchTableError(f"{schema_expr}{table_name}")
        return value

    def _get_table_pragma(self, connection, pragma, table_name, schema=None):
        quote = self.identifier_preparer.quote_identifier
        if schema is not None:
            statements = [f"PRAGMA {quote(schema)}."]
        else:
            # because PRAGMA looks in all attached databases if no schema
            # given, need to specify "main" schema, however since we want
            # 'temp' tables in the same namespace as 'main', need to run
            # the PRAGMA twice
            statements = ["PRAGMA main.", "PRAGMA temp."]

        qtable = quote(table_name)
        for statement in statements:
            statement = f"{statement}{pragma}({qtable})"
            cursor = connection.exec_driver_sql(statement)
            if not cursor._soft_closed:
                # work around SQLite issue whereby cursor.description
                # is blank when PRAGMA returns no rows:
                # https://www.sqlite.org/cvstrac/tktview?tn=1884
                result = cursor.fetchall()
            else:
                result = []
            if result:
                return result
        else:
            return []
