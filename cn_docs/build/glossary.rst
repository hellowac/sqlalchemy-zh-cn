:orphan:

.. _glossary:

========
术语
========

Glossary

.. glossary::
    :sorted:

    1.x 风格
    2.0 风格
    1.x-风格
    2.0-风格
    1.x style
    2.0 style
    1.x-style
    2.0-style
        .. tab:: 中文

            这些术语在 SQLAlchemy 1.4 中是新的，并且与 SQLAlchemy 1.4->2.0 过渡计划有关，详见 :ref:`migration_20_toplevel`。术语“1.x 风格”指在整个 SQLAlchemy 1.x 系列及更早版本（如 1.3、1.2 等）中记录的 API 使用方式，而术语“2.0 风格”指 API 在 2.0 版本中的使用方式。版本 1.4 实现了几乎所有 2.0 的 API，称为“过渡模式”，而版本 2.0 仍保留了遗留的 :class:`_orm.Query` 对象，以允许遗留代码在很大程度上与 2.0 兼容。

        .. tab:: 英文
        
            These terms are new in SQLAlchemy 1.4 and refer to the SQLAlchemy 1.4->
            2.0 transition plan, described at :ref:`migration_20_toplevel`.  The
            term "1.x style" refers to an API used in the way it's been documented
            throughout the 1.x series of SQLAlchemy and earlier (e.g. 1.3, 1.2, etc)
            and the term "2.0 style" refers to the way an API will look in version
            2.0.   Version 1.4 implements nearly all of 2.0's API in so-called
            "transition mode", while version 2.0 still maintains the legacy
            :class:`_orm.Query` object to allow legacy code to remain largely
            2.0 compatible.

        .. seealso::

            :ref:`migration_20_toplevel`

    哨兵
    插入哨兵
    sentinel
    insert sentinel
        .. tab:: 中文

            这是一个 SQLAlchemy 特定术语，指的是一个 :class:`_schema.Column`，可以用于批量 :term:`insertmanyvalues` 操作，以通过 RETURNING 或类似方式跟踪插入的数据记录。这样的列配置在以下情况下是必要的：当 :term:`insertmanyvalues` 功能为许多行执行优化的 INSERT..RETURNING 语句时，仍然能够保证返回的行的顺序与输入数据匹配。

            对于典型用例，SQLAlchemy SQL 编译器可以自动使用代理整数主键列作为“插入哨兵”，不需要用户配置。对于其他种类的服务器生成的主键值的较少见情况，可以在 :term:`table metadata` 中可选地配置明确的“插入哨兵”列，以优化一次插入多行的 INSERT 语句。

            .. seealso::

                :ref:`engine_insertmanyvalues_returning_order` - 在 :ref:`engine_insertmanyvalues` 部分中

        .. tab:: 英文

            This is a SQLAlchemy-specific term that refers to a
            :class:`_schema.Column` which can be used for a bulk
            :term:`insertmanyvalues` operation to track INSERTed data records
            against rows passed back using RETURNING or similar.   Such a
            column configuration is necessary for those cases when the
            :term:`insertmanyvalues` feature does an optimized INSERT..RETURNING
            statement for many rows at once while still being able to guarantee the
            order of returned rows matches the input data.

            For typical use cases, the SQLAlchemy SQL compiler can automatically
            make use of surrogate integer primary key columns as "insert
            sentinels", and no user-configuration is required.  For less common
            cases with other varieties of server-generated primary key values,
            explicit "insert sentinel" columns may be optionally configured within
            :term:`table metadata` in order to optimize INSERT statements that
            are inserting many rows at once.

            .. seealso::

                :ref:`engine_insertmanyvalues_returning_order` - in the section
                :ref:`engine_insertmanyvalues`

    insertmanyvalues
        .. tab:: 中文

            这是一个 SQLAlchemy 特定功能，允许 INSERT 语句在单个语句中发出数千行新行，同时允许使用 RETURNING 或类似方式从语句中内联返回服务器生成的值，以进行性能优化。该功能旨在为选定的后端透明地提供，但确实提供了一些配置选项。有关此功能的完整描述，请参阅 :ref:`engine_insertmanyvalues` 部分。

            .. seealso::

                :ref:`engine_insertmanyvalues`

        .. tab:: 英文

            This refers to a SQLAlchemy-specific feature which allows INSERT
            statements to emit thousands of new rows within a single statement
            while at the same time allowing server generated values to be returned
            inline from the statement using RETURNING or similar, for performance
            optimization purposes. The feature is intended to be transparently
            available for selected backends, but does offer some configurational
            options. See the section :ref:`engine_insertmanyvalues` for a full
            description of this feature.

            .. seealso::

                :ref:`engine_insertmanyvalues`

    混合类
    mixin class
    mixin classes
        .. tab:: 中文

            一种常见的面向对象模式，其中一个类包含供其他类使用的方法或属性，而不必成为这些其他类的父类。

            .. seealso::

                `Mixin (via Wikipedia) <https://en.wikipedia.org/wiki/Mixin>`_

        .. tab:: 英文

            A common object-oriented pattern where a class that contains methods or
            attributes for use by other classes without having to be the parent class
            of those other classes.

            .. seealso::

                `Mixin (via Wikipedia) <https://en.wikipedia.org/wiki/Mixin>`_


    反射
    reflection
    reflected
        .. tab:: 中文

            在 SQLAlchemy 中，这个术语指的是查询数据库架构目录的功能，以加载有关现有表、列、约束和其他结构的信息。SQLAlchemy 包含的功能既可以提供这些信息的原始数据，也可以从数据库架构目录中自动构建可用的 Core/ORM :class:`.Table` 对象。

            .. seealso::

                :ref:`metadata_reflection_toplevel` - 关于数据库反射的完整背景。

                :ref:`orm_declarative_reflected` - 关于将 ORM 映射与反射表集成的背景。

        .. tab:: 英文

            In SQLAlchemy, this term refers to the feature of querying a database's
            schema catalogs in order to load information about existing tables,
            columns, constraints, and other constructs.   SQLAlchemy includes
            features that can both provide raw data for this information, as well
            as that it can construct Core/ORM usable :class:`.Table` objects
            from database schema catalogs automatically.

            .. seealso::

                :ref:`metadata_reflection_toplevel` - complete background on database reflection.

                :ref:`orm_declarative_reflected` - background on integrating ORM mappings with reflected tables.


    指令式
    imperative
    声明式
    declarative
        .. tab:: 中文

            在 SQLAlchemy ORM 中，这些术语指的是将 Python 类映射到数据库表的两种不同风格。

            .. seealso::

                :ref:`orm_declarative_mapping`

                :ref:`orm_imperative_mapping`

        .. tab:: 英文


            In the SQLAlchemy ORM, these terms refer to two different styles of
            mapping Python classes to database tables.

            .. seealso::

                :ref:`orm_declarative_mapping`

                :ref:`orm_imperative_mapping`

    表面
    facade
        .. tab:: 中文

            一个作为前端接口的对象，掩盖了更复杂的底层或结构代码。

            .. seealso::

                `Facade pattern (via Wikipedia) <https://en.wikipedia.org/wiki/Facade_pattern>`_

        .. tab:: 英文


            An object that serves as a front-facing interface masking more complex
            underlying or structural code.

            .. seealso::

                `Facade pattern (via Wikipedia) <https://en.wikipedia.org/wiki/Facade_pattern>`_

    关系
    relational
    关系代数
    relational algebra
        .. tab:: 中文

            由 Edgar F. Codd 开发的一种代数系统，用于建模和查询存储在关系数据库中的数据。

            .. seealso::

                `Relational Algebra (via Wikipedia) <https://zh.wikipedia.org/wiki/关系代数_(数据库)>`_

        .. tab:: 英文


            An algebraic system developed by Edgar F. Codd that is used for
            modelling and querying the data stored in relational databases.

            .. seealso::

                `Relational Algebra (via Wikipedia) <https://en.wikipedia.org/wiki/Relational_algebra>`_

    笛卡尔积
    cartesian product
        .. tab:: 中文

            给定两个集合 A 和 B，笛卡尔积是所有有序对 (a, b) 的集合，其中 a 在 A 中，b 在 B 中。

            在 SQL 数据库中，当我们从两个或多个表（或其他子查询）中选择时未在一个表的行与另一个表的行之间建立任何标准（直接或间接）时，就会发生笛卡尔积。如果我们同时从表 A 和表 B 中选择，我们会得到表 A 的每一行与表 B 的第一行匹配，然后表 A 的每一行与表 B 的第二行匹配，依此类推，直到表 A 的每一行都与表 B 的每一行配对。

            笛卡尔积会生成巨大的结果集，如果不加以防止，可能会轻易导致客户端应用程序崩溃。

            .. seealso::

                `Cartesian Product (via Wikipedia) <https://en.wikipedia.org/wiki/Cartesian_product>`_

        .. tab:: 英文

            Given two sets A and B, the cartesian product is the set of all ordered pairs (a, b)
            where a is in A and b is in B.

            In terms of SQL databases, a cartesian product occurs when we select from two
            or more tables (or other subqueries) without establishing any kind of criteria
            between the rows of one table to another (directly or indirectly).  If we
            SELECT from table A and table B at the same time, we get every row of A matched
            to the first row of B, then every row of A matched to the second row of B, and
            so on until every row from A has been paired with every row of B.

            Cartesian products cause enormous result sets to be generated and can easily
            crash a client application if not prevented.

            .. seealso::

                `Cartesian Product (via Wikipedia) <https://en.wikipedia.org/wiki/Cartesian_product>`_

    循环复杂度
    cyclomatic complexity
        .. tab:: 中文

            一种基于程序源代码中可能路径数量的代码复杂度度量。

            .. seealso::

                `Cyclomatic Complexity <https://zh.wikipedia.org/wiki/循环复杂度>`_

        .. tab:: 英文
            A measure of code complexity based on the number of possible paths
            through a program's source code.

            .. seealso::

                `Cyclomatic Complexity <https://en.wikipedia.org/wiki/Cyclomatic_complexity>`_

    绑定参数
    bound parameter
    bound parameters
    bind parameter
    bind parameters
        .. tab:: 中文

            绑定参数是将数据传递给 :term:`DBAPI` 数据库驱动程序的主要方式。虽然要调用的操作基于 SQL 语句字符串，但数据值本身是单独传递的，驱动程序包含的逻辑将安全地处理这些字符串并将它们传递给后端数据库服务器，这可能包括将参数格式化到 SQL 字符串本身，或使用单独的协议将它们传递给数据库。

            数据库驱动程序执行此操作的具体系统对调用者来说应该无关紧要；关键是从外部看，数据应该 **始终** 单独传递，而不是作为 SQL 字符串的一部分传递。这对于防止 SQL 注入的安全性以及允许驱动程序具有最佳性能都是不可或缺的。

            .. seealso::

                `Prepared Statement <https://zh.wikipedia.org/wiki/参数化查询>`_ - 在 Wikipedia

                `bind parameters <https://use-the-index-luke.com/sql/where-clause/bind-parameters>`_ - 在 Use The Index, Luke!

                :ref:`tutorial_sending_parameters` - 在 :ref:`unified_tutorial`

        .. tab:: 英文

            Bound parameters are the primary means in which data is passed to the
            :term:`DBAPI` database driver.    While the operation to be invoked is
            based on the SQL statement string, the data values themselves are
            passed separately, where the driver contains logic that will safely
            process these strings and pass them to the backend database server,
            which may either involve formatting the parameters into the SQL string
            itself, or passing them to the database using separate protocols.

            The specific system by which the database driver does this should not
            matter to the caller; the point is that on the outside, data should
            **always** be passed separately and not as part of the SQL string
            itself.  This is integral both to having adequate security against
            SQL injections as well as allowing the driver to have the best
            performance.

            .. seealso::

                `Prepared Statement <https://en.wikipedia.org/wiki/Prepared_statement>`_ - at Wikipedia

                `bind parameters <https://use-the-index-luke.com/sql/where-clause/bind-parameters>`_ - at Use The Index, Luke!

                :ref:`tutorial_sending_parameters` - in the :ref:`unified_tutorial`

    可选择的
    selectable
        .. tab:: 中文

            一个用在 SQLAlchemy 中的术语，用于描述表示一组行的 SQL 结构。它与 :term:`relational algebra` 中的“关系”概念非常相似。在 SQLAlchemy 中，子类化 :class:`_expression.Selectable` 类的对象在使用 SQLAlchemy Core 时被认为是可用作“selectables”。最常见的两个结构是 :class:`_schema.Table` 和 :class:`_expression.Select` 语句。

            .. seealso::

                `Relational Algebra (via Wikipedia) <https://zh.wikipedia.org/wiki/关系代数_(数据库)>`_

        .. tab:: 英文

            A term used in SQLAlchemy to describe a SQL construct that represents
            a collection of rows.   It's largely similar to the concept of a
            "relation" in :term:`relational algebra`.  In SQLAlchemy, objects
            that subclass the :class:`_expression.Selectable` class are considered to be
            usable as "selectables" when using SQLAlchemy Core.  The two most
            common constructs are that of the :class:`_schema.Table` and that of the
            :class:`_expression.Select` statement.

    ORM-注解
    ORM-annotated
    annotations
        .. tab:: 中文

            术语“ORM-annotated”指的是 SQLAlchemy 的一个内部方面，其中一个核心对象（例如 :class:`_schema.Column` 对象）可以携带额外的运行时信息，该信息标记它属于特定的 ORM 映射。这个术语不应与常用短语“类型注释”混淆，后者指的是用于静态类型的 Python 源代码“类型提示”，如 :pep:`484` 中介绍的那样。

            SQLAlchemy 的大多数文档代码示例都格式化为一个关于“Annotated Example”或“Non-annotated Example”的小注释。这是指示例是否为 :pep:`484` 注释，与 SQLAlchemy 的“ORM-annotated”概念无关。

            当文档中出现“ORM-annotated”一词时，它指的是核心 SQL 表达式对象，如 :class:`.Table`、 :class:`.Column` 和 :class:`.Select` 对象，这些对象源自或指向源自一个或多个 ORM 映射的子元素，因此在传递给 ORM 方法（例如 :meth:`_orm.Session.execute`）时将具有 ORM 特定的解释和/或行为。例如，当我们从 ORM 映射构建 :class:`.Select` 对象时，如 :ref:`ORM Tutorial <tutorial_declaring_mapped_classes>` 中说明的 ``User`` 类 ::

                >>> stmt = select(User)

            上面的 :class:`.Select` 的内部状态引用了 ``User`` 映射到的 :class:`.Table`。``User`` 类本身并未立即引用。这就是 :class:`.Select` 构造与核心级别过程兼容的方式（请注意，:class:`.Select` 的 ``._raw_columns`` 成员是私有的，不应由最终用户代码访问）::

                >>> stmt._raw_columns
                [Table('user_account', MetaData(), Column('id', Integer(), ...)]

            然而，当我们将 :class:`.Select` 传递给 ORM :class:`.Session` 时，与对象间接关联的 ORM 实体用于在 ORM 上下文中解释此 :class:`.Select`。实际的“ORM 注释”可以在另一个私有变量 ``._annotations`` 中看到::

                >>> stmt._raw_columns[0]._annotations
                immutabledict({
                'entity_namespace': <Mapper at 0x7f4dd8098c10; User>,
                'parententity': <Mapper at 0x7f4dd8098c10; User>,
                'parentmapper': <Mapper at 0x7f4dd8098c10; User>
                })

            因此我们将 ``stmt`` 称为 **ORM-annotated select()** 对象。这是一个 :class:`.Select` 语句，包含额外的信息，当传递给诸如 :meth:`_orm.Session.execute` 之类的方法时，这些信息将使其在 ORM 特定的方式中进行解释。

        .. tab:: 英文


            The phrase "ORM-annotated" refers to an internal aspect of SQLAlchemy,
            where a Core object such as a :class:`_schema.Column` object can carry along
            additional runtime information that marks it as belonging to a particular
            ORM mapping.   The term should not be confused with the common phrase
            "type annotation", which refers to Python source code "type hints" used
            for static typing as introduced at :pep:`484`.

            Most of SQLAlchemy's documented code examples are formatted with a
            small note regarding "Annotated Example" or "Non-annotated Example".
            This refers to whether or not the example is :pep:`484` annotated,
            and is not related to the SQLAlchemy concept of "ORM-annotated".

            When the phrase "ORM-annotated" appears in documentation, it is
            referring to Core SQL expression objects such as :class:`.Table`,
            :class:`.Column`, and :class:`.Select` objects, which originate from,
            or refer to sub-elements that originate from, one or more ORM mappings,
            and therefore will have ORM-specific interpretations and/or behaviors
            when passed to ORM methods such as :meth:`_orm.Session.execute`.
            For example, when we construct a :class:`.Select` object from an ORM
            mapping, such as the ``User`` class illustrated in the
            :ref:`ORM Tutorial <tutorial_declaring_mapped_classes>`::

                >>> stmt = select(User)

            The internal state of the above :class:`.Select` refers to the
            :class:`.Table` to which ``User`` is mapped.   The ``User`` class
            itself is not immediately referenced.  This is how the :class:`.Select`
            construct remains compatible with Core-level processes (note that
            the ``._raw_columns`` member of :class:`.Select` is private and
            should not be accessed by end-user code)::

                >>> stmt._raw_columns
                [Table('user_account', MetaData(), Column('id', Integer(), ...)]

            However, when our :class:`.Select` is passed along to an ORM
            :class:`.Session`, the ORM entities that are indirectly associated
            with the object are used to interpret this :class:`.Select` in an
            ORM context.  The actual "ORM annotations" can be seen in another
            private variable ``._annotations``::

                >>> stmt._raw_columns[0]._annotations
                immutabledict({
                'entity_namespace': <Mapper at 0x7f4dd8098c10; User>,
                'parententity': <Mapper at 0x7f4dd8098c10; User>,
                'parentmapper': <Mapper at 0x7f4dd8098c10; User>
                })

            Therefore we refer to ``stmt`` as an **ORM-annotated select()** object.
            It's a :class:`.Select` statement that contains additional information
            that will cause it to be interpreted in an ORM-specific way when passed
            to methods like :meth:`_orm.Session.execute`.


    plugin
    plugin-enabled
    plugin-specific
        .. tab:: 中文

            “plugin-enabled” 或 “plugin-specific” 通常表示 SQLAlchemy Core 中的一个函数或方法在 ORM 上下文中使用时会表现得不同。

            SQLAlchemy 允许核心构造（例如 :class:`_sql.Select` 对象）参与“插件”系统，该系统可以向对象注入默认情况下不存在的其他行为和功能。

            具体来说，主要的“插件”是“orm”插件，它是 SQLAlchemy ORM 利用核心构造来组成和执行返回 ORM 结果的 SQL 查询的系统基础。

            .. seealso::

                :ref:`migration_20_unify_select`

        .. tab:: 英文

            "plugin-enabled" or "plugin-specific" generally indicates a function or method in
            SQLAlchemy Core which will behave differently when used in an ORM
            context.

            SQLAlchemy allows Core constructs such as :class:`_sql.Select` objects
            to participate in a "plugin" system, which can inject additional
            behaviors and features into the object that are not present by default.

            Specifically, the primary "plugin" is the "orm" plugin, which is
            at the base of the system that the SQLAlchemy ORM makes use of
            Core constructs in order to compose and execute SQL queries that
            return ORM results.

            .. seealso::

                :ref:`migration_20_unify_select`

    crud
    CRUD
        .. tab:: 中文

            一个首字母缩略词，意思是“创建、更新、删除”。在 SQL 中，该术语指创建、修改和删除数据库中的数据的操作集，也称为 :term:`DML`，通常指 ``INSERT``、 ``UPDATE`` 和 ``DELETE`` 语句。

        .. tab:: 英文

            An acronym meaning "Create, Update, Delete".  The term in SQL refers to the
            set of operations that create, modify and delete data from the database,
            also known as :term:`DML`, and typically refers to the ``INSERT``,
            ``UPDATE``, and ``DELETE`` statements.

    executemany
        .. tab:: 中文

            这个术语指的是 :pep:`249` DBAPI 规范的一部分，表示可以对数据库连接调用单个 SQL 语句，并使用多个参数集。具体方法称为 `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_，它与用于单语句调用的 `cursor.execute() <https://peps.python.org/pep-0249/#execute>`_ 方法有许多行为上的不同。“executemany” 方法多次执行给定的 SQL 语句，每次使用传递的一组参数。使用 executemany 的一般理由是提高性能，其中 DBAPI 可以使用诸如预先准备语句一次的技术，或以其他方式优化多次调用相同的语句。

            当 :meth:`_engine.Connection.execute` 方法被使用并传递了一个参数字典列表时，SQLAlchemy 通常会自动使用 ``cursor.executemany()`` 方法；这向 SQLAlchemy Core 表明，SQL 语句和处理后的参数集应传递给 ``cursor.executemany()``，驱动程序将为每个参数字典单独调用该语句。

            ``cursor.executemany()`` 方法的一个关键限制是，当使用此方法时， ``cursor`` 未配置为返回行。对于 **大多数** 后端（一个显着的例外是 python-oracledb / cx_Oracle DBAPIs），这意味着像 ``INSERT..RETURNING`` 这样的语句通常不能直接与 ``cursor.executemany()`` 一起使用，因为 DBAPIs 通常不会将每次 INSERT 执行的单行聚合在一起。

            为克服此限制，SQLAlchemy 从 2.0 系列开始实现了一种称为 :ref:`engine_insertmanyvalues` 的替代形式的“executemany”。此功能使用 ``cursor.execute()`` 调用一个 INSERT 语句，该语句将在一次往返中处理多个参数集，从而产生与使用 ``cursor.executemany()`` 相同的效果，同时仍然支持 RETURNING。

            .. seealso::

                :ref:`tutorial_multiple_parameters` - 对“executemany”的教程介绍

                :ref:`engine_insertmanyvalues` - 允许在“executemany”中使用 RETURNING 的 SQLAlchemy 功能

        .. tab:: 英文

            This term refers to a part of the :pep:`249` DBAPI specification
            indicating a single SQL statement that may be invoked against a
            database connection with multiple parameter sets.   The specific
            method is known as
            `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_,
            and it has many behavioral differences in comparison to the
            `cursor.execute() <https://peps.python.org/pep-0249/#execute>`_
            method which is used for single-statement invocation.   The "executemany"
            method executes the given SQL statement multiple times, once for
            each set of parameters passed.  The general rationale for using
            executemany is that of improved performance, wherein the DBAPI may
            use techniques such as preparing the statement just once beforehand,
            or otherwise optimizing for invoking the same statement many times.

            SQLAlchemy typically makes use of the ``cursor.executemany()`` method
            automatically when the :meth:`_engine.Connection.execute` method is
            used where a list of parameter dictionaries were passed; this indicates
            to SQLAlchemy Core that the SQL statement and processed parameter sets
            should be passed to ``cursor.executemany()``, where the statement will
            be invoked by the driver for each parameter dictionary individually.

            A key limitation of the ``cursor.executemany()`` method as used with
            all known DBAPIs is that the ``cursor`` is not configured to return
            rows when this method is used.  For **most** backends (a notable
            exception being the python-oracledb / cx_Oracle DBAPIs), this means that
            statements like ``INSERT..RETURNING`` typically cannot be used with
            ``cursor.executemany()`` directly, since DBAPIs typically do not
            aggregate the single row from each INSERT execution together.

            To overcome this limitation, SQLAlchemy as of the 2.0 series implements
            an alternative form of "executemany" which is known as
            :ref:`engine_insertmanyvalues`. This feature makes use of
            ``cursor.execute()`` to invoke an INSERT statement that will proceed
            with multiple parameter sets in one round trip, thus producing the same
            effect as using ``cursor.executemany()`` while still supporting
            RETURNING.

            .. seealso::

                :ref:`tutorial_multiple_parameters` - tutorial introduction to
                "executemany"

                :ref:`engine_insertmanyvalues` - SQLAlchemy feature which allows
                RETURNING to be used with "executemany"

    marshalling
    数据编组
    data marshalling
        .. tab:: 中文

            将对象的内存表示转换为适合存储或传输到系统另一部分的数据格式的过程，当数据必须在计算机程序的不同部分之间或从一个程序移动到另一个程序时。就 SQLAlchemy 而言，我们通常需要将数据“编组”成适合传递到关系数据库的格式。

            .. seealso::

                `Marshalling (via Wikipedia) <https://zh.wikipedia.org/wiki/Marshalling_(计算机科学)>`_

                :ref:`types_typedecorator` - SQLAlchemy 的 :class:`.TypeDecorator` 通常用于将数据发送到数据库进行 INSERT 和 UPDATE 语句时的数据编组，以及使用 SELECT 语句检索数据时的“解组”。

        .. tab:: 英文

            The process of transforming the memory representation of an object to
            a data format suitable for storage or transmission to another part of
            a system, when data must be moved between different parts of a
            computer program or from one program to another.   In terms of
            SQLAlchemy, we often need to "marshal" data into a format appropriate
            for passing into the relational database.

            .. seealso::

                `Marshalling (via Wikipedia) <https://en.wikipedia.org/wiki/Marshalling_(computer_science)>`_

                :ref:`types_typedecorator` - SQLAlchemy's :class:`.TypeDecorator`
                is commonly used for data marshalling as data is sent into the
                database for INSERT and UPDATE statements, and "unmarshalling"
                data as it is retrieved using SELECT statements.

    descriptor
    描述符
    descriptors
        .. tab:: 中文

            在 Python 中，描述符是具有“绑定行为”的对象属性，其属性访问被 `描述符协议 <https://docs.python.org/howto/descriptor.html>`_ 中的方法覆盖。 这些方法是 ``__get__()``、 ``__set__()`` 和 ``__delete__()``。 如果为对象定义了这些方法中的任何一个，它就被称为描述符。

            在 SQLAlchemy 中，描述符被大量使用，以提供映射类的属性行为。当类被映射时，例如::

                class MyClass(Base):
                    __tablename__ = "foo"

                    id = Column(Integer, primary_key=True)
                    data = Column(String)

            当 ``MyClass`` 类的定义完成时，该类将被 :term:`mapped`，此时，最初作为 :class:`_schema.Column` 对象的 ``id`` 和 ``data`` 属性将被 :term:`instrumentation` 系统替换为 :class:`.InstrumentedAttribute` 的实例，这些实例是提供上述 ``__get__()``、``__set__()`` 和 ``__delete__()`` 方法的描述符。 :class:`.InstrumentedAttribute` 在类级别使用时会生成一个 SQL 表达式：

            .. sourcecode:: pycon+sql

                >>> print(MyClass.data == 5)
                {printsql}data = :data_1

            在实例级别，它会跟踪值的变化，并且还会从数据库 :term:`lazy loads` 未加载的属性：

                >>> m1 = MyClass()
                >>> m1.id = 5
                >>> m1.data = "some data"

                >>> from sqlalchemy import inspect
                >>> inspect(m1).attrs.data.history.added
                "some data"

        .. tab:: 英文


            In Python, a descriptor is an object attribute with “binding behavior”,
            one whose attribute access has been overridden by methods in the
            `descriptor protocol <https://docs.python.org/howto/descriptor.html>`_.
            Those methods are ``__get__()``, ``__set__()``, and ``__delete__()``.
            If any of those methods are defined for an object, it is said to be a
            descriptor.

            In SQLAlchemy, descriptors are used heavily in order to provide attribute behavior
            on mapped classes.   When a class is mapped as such::

                class MyClass(Base):
                    __tablename__ = "foo"

                    id = Column(Integer, primary_key=True)
                    data = Column(String)

            The ``MyClass`` class will be :term:`mapped` when its definition
            is complete, at which point the ``id`` and ``data`` attributes,
            starting out as :class:`_schema.Column` objects, will be replaced
            by the :term:`instrumentation` system with instances
            of :class:`.InstrumentedAttribute`, which are descriptors that
            provide the above mentioned ``__get__()``, ``__set__()`` and
            ``__delete__()`` methods.   The :class:`.InstrumentedAttribute`
            will generate a SQL expression when used at the class level:

            .. sourcecode:: pycon+sql

                >>> print(MyClass.data == 5)
                {printsql}data = :data_1

            and at the instance level, keeps track of changes to values,
            and also :term:`lazy loads` unloaded attributes
            from the database::

                >>> m1 = MyClass()
                >>> m1.id = 5
                >>> m1.data = "some data"

                >>> from sqlalchemy import inspect
                >>> inspect(m1).attrs.data.history.added
                "some data"

    DDL
        .. tab:: 中文

            一个 **数据定义语言** 的缩写。DDL 是 SQL 的子集，关系数据库使用它来配置表、约束和数据库模式中的其他永久对象。SQLAlchemy 提供了一个丰富的 API 用于构建和发出 DDL 表达式。

            .. seealso::

                :ref:`metadata_toplevel`

                `DDL (via Wikipedia) <https://zh.wikipedia.org/wiki/资料定义语言>`_

                :term:`DML`

                :term:`DQL`

        .. tab:: 英文

            An acronym for **Data Definition Language**.  DDL is the subset
            of SQL that relational databases use to configure tables, constraints,
            and other permanent objects within a database schema.  SQLAlchemy
            provides a rich API for constructing and emitting DDL expressions.

            .. seealso::

                :ref:`metadata_toplevel`

                `DDL (via Wikipedia) <https://en.wikipedia.org/wiki/Data_definition_language>`_

                :term:`DML`

                :term:`DQL`

    DML
        .. tab:: 中文

            一个 **数据操作语言** 的缩写。DML 是 SQL 的子集，关系数据库使用它来 *修改* 表中的数据。DML 通常指三个广为人知的语句：INSERT、UPDATE 和 DELETE，也称为 :term:`CRUD` （“创建、读取、更新、删除”的缩写）。

            .. seealso::

                `DML (via Wikipedia) <https://zh.wikipedia.org/wiki/数据操纵语言>`_

                :term:`DDL`

                :term:`DQL`

        .. tab:: 英文

            An acronym for **Data Manipulation Language**.  DML is the subset of
            SQL that relational databases use to *modify* the data in tables. DML
            typically refers to the three widely familiar statements of INSERT,
            UPDATE and  DELETE, otherwise known as :term:`CRUD` (acronym for "Create,
            Read, Update, Delete").

            .. seealso::

                `DML (via Wikipedia) <https://en.wikipedia.org/wiki/Data_manipulation_language>`_

                :term:`DDL`

                :term:`DQL`

    DQL
        .. tab:: 中文

            一个 **数据查询语言** 的缩写。DQL 是 SQL 的子集，关系数据库使用它来 *读取* 表中的数据。DQL 几乎完全指 SQL SELECT 结构作为使用的顶级 SQL 语句。

            .. seealso::

                `DQL (via Wikipedia) <https://en.wikipedia.org/wiki/Data_query_language>`_

                :term:`DML`

                :term:`DDL`

        .. tab:: 英文

            An acronym for **Data Query Language**.  DQL is the subset of
            SQL that relational databases use to *read* the data in tables.
            DQL almost exclusively refers to the SQL SELECT construct as the
            top level SQL statement in use.

            .. seealso::

                `DQL (via Wikipedia) <https://en.wikipedia.org/wiki/Data_query_language>`_

                :term:`DML`

                :term:`DDL`

    metadata
    元数据
    database metadata
    数据库元数据
    table metadata
    表元数据
        .. tab:: 中文

            术语 “元数据” 通常指“ 描述数据的数据”；本身代表某种其他数据格式和/或结构的数据。在 SQLAlchemy 中，术语 “元数据” 通常指 :class:`_schema.MetaData` 构造，它是关于表、列、约束和其他可能存在于特定数据库中的 :term:`DDL` 对象的信息集合。

            .. seealso::

                `Metadata Mapping (via Martin Fowler) <https://www.martinfowler.com/eaaCatalog/metadataMapping.html>`_

                :ref:`tutorial_working_with_metadata`  - 在 :ref:`unified_tutorial` 中

        .. tab:: 英文

            The term "metadata" generally refers to "data that describes data";
            data that itself represents the format and/or structure of some other
            kind of data.  In SQLAlchemy, the term "metadata" typically refers  to
            the :class:`_schema.MetaData` construct, which is a collection of information
            about the tables, columns, constraints, and other :term:`DDL` objects
            that may exist in a particular database.

            .. seealso::

                `Metadata Mapping (via Martin Fowler) <https://www.martinfowler.com/eaaCatalog/metadataMapping.html>`_

                :ref:`tutorial_working_with_metadata`  - in the :ref:`unified_tutorial`

    version id column
    版本ID列
        .. tab:: 中文

            在 SQLAlchemy 中，这指的是使用特定的表列来跟踪特定行的“版本”，随着行的值发生变化。虽然有不同类型的关系模式以不同的方式使用“版本 ID 列”，但 SQLAlchemy 的 ORM 包括一个特定功能，允许将此类列配置为在使用新信息更新行时测试陈旧数据的一种手段。如果我们尝试将新数据放入行时该列的最后已知“版本”与该行的版本不匹配，我们就知道我们正在处理陈旧信息。

            在数据库中存储“版本化”行还有其他方法，通常称为“时间”数据。除了 SQLAlchemy 的版本控制功能外，文档中还提供了一些示例，见下文链接。

            .. seealso::

                :ref:`mapper_version_counter` - SQLAlchemy 的内置版本 ID 功能。

                :ref:`examples_versioning` - 其他时间版本行的映射示例。

        .. tab:: 英文

            In SQLAlchemy, this refers to the use of a particular table column that
            tracks the "version" of a particular row, as the row changes values.   While
            there are different kinds of relational patterns that make use of a
            "version id column" in different ways, SQLAlchemy's ORM includes a particular
            feature that allows for such a column to be configured as a means of
            testing for stale data when a row is being UPDATEd with new information.
            If the last known "version" of this column does not match that of the
            row when we try to put new data into the row, we know that we are
            acting on stale information.

            There are also other ways of storing "versioned" rows in a database,
            often referred to as "temporal" data.  In addition to SQLAlchemy's
            versioning feature, a few more examples are also present in the
            documentation, see the links below.

            .. seealso::

                :ref:`mapper_version_counter` - SQLAlchemy's built-in version id feature.

                :ref:`examples_versioning` - other examples of mappings that version rows temporally.

    registry
    注册
        .. tab:: 中文

            一个对象，通常是全局可访问的，包含一些程序状态的长期信息，这些信息通常对程序的许多部分都很有用。

            .. seealso::

                `Registry (via Martin Fowler) <https://martinfowler.com/eaaCatalog/registry.html>`_

        .. tab:: 英文

            An object, typically globally accessible, that contains long-lived
            information about some program state that is generally useful to many
            parts of a program.

            .. seealso::

                `Registry (via Martin Fowler) <https://martinfowler.com/eaaCatalog/registry.html>`_

    cascade
    级联
        .. tab:: 中文

            一个术语，用于描述在 SQLAlchemy 中，针对特定对象执行的 ORM 持久化操作如何扩展到与该对象直接关联的其他对象。在 SQLAlchemy 中，这些对象关联是使用 :func:`_orm.relationship` 构造配置的。 :func:`_orm.relationship` 包含一个称为 :paramref:`_orm.relationship.cascade` 的参数，该参数提供有关某些持久化操作如何级联的选项。

            “级联”一词以及该系统在 SQLAlchemy 中的一般架构，无论好坏，都是从 Hibernate ORM 借用的。

            .. seealso::

                :ref:`unitofwork_cascades`

        .. tab:: 英文

            A term used in SQLAlchemy to describe how an ORM persistence action that
            takes place on a particular object would extend into other objects
            which are directly associated with that object.  In SQLAlchemy, these
            object associations are configured using the :func:`_orm.relationship`
            construct.   :func:`_orm.relationship` contains a parameter called
            :paramref:`_orm.relationship.cascade` which provides options on how certain
            persistence operations may cascade.

            The term "cascades" as well as the general architecture of this system
            in SQLAlchemy was borrowed, for better or worse, from the Hibernate
            ORM.

            .. seealso::

                :ref:`unitofwork_cascades`

    dialect
    方言
        .. tab:: 中文

            在 SQLAlchemy 中，“方言”是一个 Python 对象，表示允许在特定类型的数据库后端和该数据库的特定类型的 Python 驱动程序（或 :term:`DBAPI`）上进行数据库操作的信息和方法。SQLAlchemy 方言是 :class:`.Dialect` 类的子类。

            .. seealso::

                :ref:`engines_toplevel`

        .. tab:: 英文

            In SQLAlchemy, the "dialect" is a Python object that represents information
            and methods that allow database operations to proceed on a particular
            kind of database backend and a particular kind of Python driver (or
            :term:`DBAPI`) for that database.   SQLAlchemy dialects are subclasses
            of the :class:`.Dialect` class.

            .. seealso::

                :ref:`engines_toplevel`

    discriminator
    鉴别器
        .. tab:: 中文

            一个结果集列，在 :term:`polymorphic` 加载期间用于确定应将哪种映射类应用于特定的传入结果行。

            .. seealso::

                :ref:`inheritance_toplevel`

        .. tab:: 英文

            A result-set column which is used during :term:`polymorphic` loading
            to determine what kind of mapped class should be applied to a particular
            incoming result row.

            .. seealso::

                :ref:`inheritance_toplevel`

    instrumentation
    instrumented
    instrumenting
        .. tab:: 中文

            Instrumentation 是指增强特定类的功能和属性集的过程。理想情况下，类的行为应保持接近普通类，只是提供了额外的行为和功能。SQLAlchemy 的 :term:`mapping` 过程除了其他功能外，还会向映射类添加数据库启用的 :term:`descriptors`，每个描述符代表一个特定的数据库列或与相关类的关系。

        .. tab:: 英文

            Instrumentation refers to the process of augmenting the functionality
            and attribute set of a particular class.   Ideally, the
            behavior of the class should remain close to a regular
            class, except that additional behaviors and features are
            made available.  The SQLAlchemy :term:`mapping` process,
            among other things, adds database-enabled :term:`descriptors`
            to a mapped
            class each of which represents a particular database column
            or relationship to a related class.

    identity key
    身份密钥
        .. tab:: 中文

            一个与 ORM 映射对象关联的键，用于标识它们在数据库中的主键标识，以及它们在 :class:`_orm.Session` :term:`identity map` 中的唯一标识。

            在 SQLAlchemy 中，您可以使用 :func:`_sa.inspect` API 查看 ORM 对象的标识键，以返回 :class:`_orm.InstanceState` 跟踪对象，然后查看 :attr:`_orm.InstanceState.key` 属性::

                >>> from sqlalchemy import inspect
                >>> inspect(some_object).key
                (<class '__main__.MyTable'>, (1,), None)

            .. seealso::

                :term:`identity map`

        .. tab:: 英文

            A key associated with ORM-mapped objects that identifies their
            primary key identity within the database, as well as their unique
            identity within a :class:`_orm.Session` :term:`identity map`.

            In SQLAlchemy, you can view the identity key for an ORM object
            using the :func:`_sa.inspect` API to return the :class:`_orm.InstanceState`
            tracking object, then looking at the :attr:`_orm.InstanceState.key`
            attribute::

                >>> from sqlalchemy import inspect
                >>> inspect(some_object).key
                (<class '__main__.MyTable'>, (1,), None)

            .. seealso::

                :term:`identity map`

    identity map
    身份映射
        .. tab:: 中文

            Python 对象及其数据库标识之间的映射。身份映射是与 ORM :term:`Session` 对象关联的集合，并维护每个数据库对象的单个实例，该实例以其标识为键。这种模式的优点是，针对特定数据库标识进行的所有操作都透明地协调到单个对象实例上。当将身份映射与 :term:`isolated` 事务结合使用时，具有特定主键的对象引用在实际操作中可以视为实际数据库行的代理。

            .. seealso::

                `Identity Map (via Martin Fowler) <https://martinfowler.com/eaaCatalog/identityMap.html>`_

                :ref:`session_get` - 如何通过主键在身份映射中查找对象

        .. tab:: 英文

            A mapping between Python objects and their database identities.
            The identity map is a collection that's associated with an
            ORM :term:`Session` object, and maintains a single instance
            of every database object keyed to its identity.   The advantage
            to this pattern is that all operations which occur for a particular
            database identity are transparently coordinated onto a single
            object instance.  When using an identity map in conjunction with
            an :term:`isolated` transaction, having a reference
            to an object that's known to have a particular primary key can
            be considered from a practical standpoint to be a
            proxy to the actual database row.

            .. seealso::

                `Identity Map (via Martin Fowler) <https://martinfowler.com/eaaCatalog/identityMap.html>`_

                :ref:`session_get` - how to look up an object in the identity map
                by primary key

    lazy initialization
    延迟初始化
        .. tab:: 中文

            一种延迟某些初始化操作的策略，例如创建对象、填充数据或建立与其他服务的连接，直到需要这些资源时才进行。

            .. seealso::

                `Lazy initialization (via Wikipedia) <https://en.wikipedia.org/wiki/Lazy_initialization>`_

        .. tab:: 英文

            A tactic of delaying some initialization action, such as creating objects,
            populating data, or establishing connectivity to other services, until
            those resources are required.

            .. seealso::

                `Lazy initialization (via Wikipedia) <https://en.wikipedia.org/wiki/Lazy_initialization>`_

    lazy load
    lazy loads
    lazy loaded
    lazy loading
    延迟加载
        .. tab:: 中文

            在对象关系映射中，“延迟加载”指的是在某段时间内（通常是对象首次加载时）属性不包含其数据库端的值。相反，属性会接收到一个 *memoization*，使其在首次使用时访问数据库并加载数据。使用这种模式，有时可以减少对象获取的复杂性和时间，因为不需要立即处理相关表的属性。

            延迟加载是 :term:`eager loading` 的对立面。

            在 SQLAlchemy 中，延迟加载是 ORM 的一个关键特性，适用于用户定义类上 :term:`mapped` 的属性。当访问引用数据库列或相关对象的属性时，如果没有加载值，ORM 将使用当前对象所关联的 :class:`_orm.Session` 在 :term:`persistent` 状态下，并在当前事务上发出一个 SELECT 语句，如果没有进行中的事务，则启动一个新事务。如果对象处于 :term:`detached` 状态且未与任何 :class:`_orm.Session` 关联，这被视为错误状态并引发 :ref:`informative exception <error_bhk3>`。

            .. seealso::

                `Lazy Load (via Martin Fowler) <https://martinfowler.com/eaaCatalog/lazyLoad.html>`_

                :term:`N plus one problem`

                :ref:`loading_columns` - 包含有关 ORM 映射列的延迟加载信息

                :doc:`orm/queryguide/relationships` - 包含有关 ORM 相关对象的延迟加载信息

                :ref:`asyncio_orm_avoid_lazyloads` - 在使用 :ref:`asyncio_toplevel` 扩展时避免延迟加载的提示

        .. tab:: 英文

            In object relational mapping, a "lazy load" refers to an
            attribute that does not contain its database-side value
            for some period of time, typically when the object is
            first loaded.  Instead, the attribute receives a
            *memoization* that causes it to go out to the database
            and load its data when it's first used.   Using this pattern,
            the complexity and time spent within object fetches can
            sometimes be reduced, in that
            attributes for related tables don't need to be addressed
            immediately.

            Lazy loading is the opposite of :term:`eager loading`.

            Within SQLAlchemy, lazy loading is a key feature of the ORM, and
            applies to attributes which are :term:`mapped` on a user-defined class.
            When attributes that refer to database columns or related objects
            are accessed, for which no loaded value is present, the ORM makes
            use of the :class:`_orm.Session` for which the current object is
            associated with in the :term:`persistent` state, and emits a SELECT
            statement on the current transaction, starting a new transaction if
            one was not in progress.   If the object is in the :term:`detached`
            state and not associated with any :class:`_orm.Session`, this is
            considered to be an error state and an
            :ref:`informative exception <error_bhk3>` is raised.

            .. seealso::

                `Lazy Load (via Martin Fowler) <https://martinfowler.com/eaaCatalog/lazyLoad.html>`_

                :term:`N plus one problem`

                :ref:`loading_columns` - includes information on lazy loading of
                ORM mapped columns

                :doc:`orm/queryguide/relationships` - includes information on lazy
                loading of ORM related objects

                :ref:`asyncio_orm_avoid_lazyloads` - tips on avoiding lazy loading
                when using the :ref:`asyncio_toplevel` extension

    eager load
    eager loads
    eager loaded
    eager loading
    eagerly load
    预加载
        .. tab:: 中文

            在对象关系映射中，“预加载”指的是在对象本身从数据库加载时，属性也会被填充其数据库端的值。在 SQLAlchemy 中，"预加载" 通常指的是使用 :func:`_orm.relationship` 构造在映射之间链接的相关集合和对象实例，但也可以指加载其他列属性，通常是从与正在查询的特定表相关的其他表中加载，例如使用 :ref:`inheritance <inheritance_toplevel>` 映射时。

            预加载是 :term:`lazy loading` 的对立面。

            .. seealso::

                :doc:`orm/queryguide/relationships`

        .. tab:: 英文

            In object relational mapping, an "eager load" refers to an attribute
            that is populated with its database-side value at the same time as when
            the object itself is loaded from the database. In SQLAlchemy, the term
            "eager loading" usually refers to related collections and instances of
            objects that are linked between mappings using the
            :func:`_orm.relationship` construct, but can also refer to additional
            column attributes being loaded, often from other tables related to a
            particular table being queried, such as when using
            :ref:`inheritance <inheritance_toplevel>` mappings.

            Eager loading is the opposite of :term:`lazy loading`.

            .. seealso::

                :doc:`orm/queryguide/relationships`


    mapping
    mapped
    mapped class
    ORM mapped class
    映射类
    ORM映射类
        .. tab:: 中文

            我们说一个类是“映射的”，当它与 :class:`_orm.Mapper` 类的实例关联时。这个过程将类与数据库表或其他 :term:`selectable` 构造关联在一起，以便可以使用 :class:`.Session` 持久化和加载它的实例。

            .. seealso::

                :ref:`orm_mapping_classes_toplevel`

        .. tab:: 英文

            We say a class is "mapped" when it has been associated with an
            instance of the :class:`_orm.Mapper` class. This process associates
            the class with a database table or other :term:`selectable` construct,
            so that instances of it can be persisted and loaded using a
            :class:`.Session`.

            .. seealso::

                :ref:`orm_mapping_classes_toplevel`

    N plus one problem
    N plus one
        .. tab:: 中文

            N+1 问题是 :term:`lazy load` 模式的一个常见副作用，其中应用程序希望遍历对象结果集中每个成员的相关属性或集合，而该属性或集合设置为通过延迟加载模式进行加载。最终结果是发出一个 SELECT 语句来加载父对象的初始结果集；然后，当应用程序遍历每个成员时，会为每个成员发出一个额外的 SELECT 语句，以加载该成员的相关属性或集合。最终结果是，对于 N 个父对象的结果集，将发出 N+1 个 SELECT 语句。

            N+1 问题可以通过 :term:`eager loading` 来缓解。

            .. seealso::

                :ref:`tutorial_orm_loader_strategies`

                :doc:`orm/queryguide/relationships`

        .. tab:: 英文

            The N plus one problem is a common side effect of the
            :term:`lazy load` pattern, whereby an application wishes
            to iterate through a related attribute or collection on
            each member of a result set of objects, where that
            attribute or collection is set to be loaded via the lazy
            load pattern.   The net result is that a SELECT statement
            is emitted to load the initial result set of parent objects;
            then, as the application iterates through each member,
            an additional SELECT statement is emitted for each member
            in order to load the related attribute or collection for
            that member.  The end result is that for a result set of
            N parent objects, there will be N + 1 SELECT statements emitted.

            The N plus one problem is alleviated using :term:`eager loading`.

            .. seealso::

                :ref:`tutorial_orm_loader_strategies`

                :doc:`orm/queryguide/relationships`

    polymorphic
    polymorphically
    多态的
        .. tab:: 中文

            指的是一次处理多种类型的函数。在 SQLAlchemy 中，该术语通常应用于 ORM 映射类的概念，其中查询操作将根据结果集中信息返回不同的子类，通常通过检查结果中称为 :term:`discriminator` 的特定列的值来实现。

            在 SQLAlchemy 中，多态加载意味着使用三种不同方案中的一种或组合来映射类的层次结构：“joined”、“single”和“concrete”。部分 :ref:`inheritance_toplevel` 完整描述了继承映射。

        .. tab:: 英文

            Refers to a function that handles several types at once.  In SQLAlchemy,
            the term is usually applied to the concept of an ORM mapped class
            whereby a query operation will return different subclasses
            based on information in the result set, typically by checking the
            value of a particular column in the result known as the :term:`discriminator`.

            Polymorphic loading in SQLAlchemy implies that a one or a
            combination of three different schemes are used to map a hierarchy
            of classes; "joined", "single", and "concrete".   The section
            :ref:`inheritance_toplevel` describes inheritance mapping fully.

    method chaining
    方法链
    generative
    生成式
        .. tab:: 中文

            “方法链”，在 SQLAlchemy 文档中称为“生成式”，是一种面向对象的技术，通过在对象上调用方法来构建对象的状态。对象具有任意数量的方法，每个方法返回一个具有附加状态的新对象（或在某些情况下相同的对象）。

            在 SQLAlchemy 中，最常使用方法链的两个对象是 :class:`_expression.Select` 对象和 :class:`.orm.query.Query` 对象。例如，可以通过调用 :meth:`_expression.Select.where` 和 :meth:`_expression.Select.order_by` 方法，为 :class:`_expression.Select` 对象的 WHERE 子句分配两个表达式以及一个 ORDER BY 子句::

                stmt = (
                    select(user.c.name)
                    .where(user.c.id > 5)
                    .where(user.c.name.like("e%"))
                    .order_by(user.c.name)
                )

            上述每个方法调用都会返回原始 :class:`_expression.Select` 对象的副本，并添加附加的限定符。

        .. tab:: 英文

            "Method chaining", referred to within SQLAlchemy documentation as
            "generative", is an object-oriented technique whereby the state of an
            object is constructed by calling methods on the object. The object
            features any number of methods, each of which return a new object (or
            in some cases the same object) with additional state added to the
            object.

            The two SQLAlchemy objects that make the most use of
            method chaining are the :class:`_expression.Select`
            object and the :class:`.orm.query.Query` object.
            For example, a :class:`_expression.Select` object can
            be assigned two expressions to its WHERE clause as well
            as an ORDER BY clause by calling upon the :meth:`_expression.Select.where`
            and :meth:`_expression.Select.order_by` methods::

                stmt = (
                    select(user.c.name)
                    .where(user.c.id > 5)
                    .where(user.c.name.like("e%"))
                    .order_by(user.c.name)
                )

            Each method call above returns a copy of the original
            :class:`_expression.Select` object with additional qualifiers
            added.

    release
    releases
    released
    释放
        .. tab:: 中文

            在 SQLAlchemy 中，术语“释放”是指结束特定数据库连接的使用过程。SQLAlchemy 具有连接池的使用功能，可以配置数据库连接的生命周期。当使用池化连接时，“关闭”它的过程，即调用 ``connection.close()`` 语句，可能会将连接返回到现有池中，也可能会关闭该连接所引用的底层 TCP/IP 连接——哪种情况发生取决于配置以及池的当前状态。因此，我们使用术语 *released*，意为“在我们使用完连接后，做任何你做的事情”。

            该术语有时会在短语“释放事务资源”中使用，以更明确地表示我们实际上“释放”的是连接上已累积的任何事务状态。在大多数情况下，从表中选择、发出更新等过程会在该连接上获取 :term:`isolated` 状态以及潜在的行或表锁。这种状态都是特定事务的本地状态，当我们发出回滚时会被释放。连接池的一个重要特性是，当我们将连接返回到池中时，也会调用 DBAPI 的 ``connection.rollback()`` 方法，因此当连接被设置为再次使用时，它处于“干净”的状态，不再引用之前的一系列操作。

            .. seealso::

                :ref:`pooling_toplevel`

        .. tab:: 英文

            In the context of SQLAlchemy, the term "released"
            refers to the process of ending the usage of a particular
            database connection.    SQLAlchemy features the usage
            of connection pools, which allows configurability as to
            the lifespan of database connections.   When using a pooled
            connection, the process of "closing" it, i.e. invoking
            a statement like ``connection.close()``, may have the effect
            of the connection being returned to an existing pool,
            or it may have the effect of actually shutting down the
            underlying TCP/IP connection referred to by that connection -
            which one takes place depends on configuration as well
            as the current state of the pool.  So we used the term
            *released* instead, to mean "do whatever it is you do
            with connections when we're done using them".

            The term will sometimes be used in the phrase, "release
            transactional resources", to indicate more explicitly that
            what we are actually "releasing" is any transactional
            state which as accumulated upon the connection.  In most
            situations, the process of selecting from tables, emitting
            updates, etc. acquires :term:`isolated` state upon
            that connection as well as potential row or table locks.
            This state is all local to a particular transaction
            on the connection, and is released when we emit a rollback.
            An important feature of the connection pool is that when
            we return a connection to the pool, the ``connection.rollback()``
            method of the DBAPI is called as well, so that as the
            connection is set up to be used again, it's in a "clean"
            state with no references held to the previous series
            of operations.

            .. seealso::

                :ref:`pooling_toplevel`

    DBAPI
    pep-249
        .. tab:: 中文

            DBAPI 是“Python 数据库 API 规范”（Python Database API Specification）的缩写。这是在 Python 中广泛使用的规范，用于定义所有数据库连接包的常见使用模式。DBAPI 是一个“低级”API，通常是 Python 应用程序中用于与数据库通信的最低级系统。SQLAlchemy 的 :term:`dialect` 系统围绕 DBAPI 的操作构建，提供服务于特定数据库引擎的特定 DBAPI 的单个方言类；例如，:func:`_sa.create_engine` URL ``postgresql+psycopg2://@localhost/test`` 指的是 :mod:`psycopg2 <.postgresql.psycopg2>` DBAPI/方言组合，而 URL ``mysql+mysqldb://@localhost/test`` 指的是 :mod:`MySQL for Python <.mysql.mysqldb>` DBAPI/方言组合。

            .. seealso::

                `PEP 249 - Python Database API Specification v2.0 <https://www.python.org/dev/peps/pep-0249/>`_

        .. tab:: 英文

            DBAPI is shorthand for the phrase "Python Database API
            Specification".  This is a widely used specification
            within Python to define common usage patterns for all
            database connection packages.   The DBAPI is a "low level"
            API which is typically the lowest level system used
            in a Python application to talk to a database.  SQLAlchemy's
            :term:`dialect` system is constructed around the
            operation of the DBAPI, providing individual dialect
            classes which service a specific DBAPI on top of a
            specific database engine; for example, the :func:`_sa.create_engine`
            URL ``postgresql+psycopg2://@localhost/test``
            refers to the :mod:`psycopg2 <.postgresql.psycopg2>`
            DBAPI/dialect combination, whereas the URL ``mysql+mysqldb://@localhost/test``
            refers to the :mod:`MySQL for Python <.mysql.mysqldb>`
            DBAPI/dialect combination.

            .. seealso::

                `PEP 249 - Python Database API Specification v2.0 <https://www.python.org/dev/peps/pep-0249/>`_

    domain model
    领域模型
        .. tab:: 中文

            领域模型在问题解决和软件工程中是与特定问题相关的所有主题的概念模型。它描述了各种实体、它们的属性、角色和关系，以及支配问题领域的约束。

            （via Wikipedia）

            .. seealso::

                `Domain Model (via Wikipedia) <https://en.wikipedia.org/wiki/Domain_model>`_

        .. tab:: 英文


            A domain model in problem solving and software engineering is a conceptual model of all the topics related to a specific problem. It describes the various entities, their attributes, roles, and relationships, plus the constraints that govern the problem domain.

            (via Wikipedia)

            .. seealso::

                `Domain Model (via Wikipedia) <https://en.wikipedia.org/wiki/Domain_model>`_

    unit of work
    工作单元
        .. tab:: 中文

            一种软件架构，其中持久化系统（如对象关系映射器）维护对一系列对象所做更改的列表，并定期将所有这些待处理的更改刷新到数据库。

            SQLAlchemy 的 :class:`_orm.Session` 实现了工作单元模式，其中使用 :meth:`_orm.Session.add` 方法添加到 :class:`_orm.Session` 的对象将参与工作单元风格的持久化。

            要了解 SQLAlchemy 中工作单元持久化的样子，请从 :ref:`unified_tutorial` 中的 :ref:`tutorial_orm_data_manipulation` 部分开始。然后，详细信息参见一般参考文档中的 :ref:`session_basics`。

            .. seealso::

                `Unit of Work (via Martin Fowler) <https://martinfowler.com/eaaCatalog/unitOfWork.html>`_

                :ref:`tutorial_orm_data_manipulation`

                :ref:`session_basics`

        .. tab:: 英文

            A software architecture where a persistence system such as an object
            relational mapper maintains a list of changes made to a series of
            objects, and periodically flushes all those pending changes out to the
            database.

            SQLAlchemy's :class:`_orm.Session` implements the unit of work pattern,
            where objects that are added to the :class:`_orm.Session` using methods
            like :meth:`_orm.Session.add` will then participate in unit-of-work
            style persistence.

            For a walk-through of what unit of work persistence looks like in
            SQLAlchemy, start with the section :ref:`tutorial_orm_data_manipulation`
            in the :ref:`unified_tutorial`.    Then for more detail, see
            :ref:`session_basics` in the general reference documentation.

            .. seealso::

                `Unit of Work (via Martin Fowler) <https://martinfowler.com/eaaCatalog/unitOfWork.html>`_

                :ref:`tutorial_orm_data_manipulation`

                :ref:`session_basics`

    flush
    flushing
    flushed
        .. tab:: 中文

            这指的是 :term:`unit of work` 用于向数据库发出更改的实际过程。在 SQLAlchemy 中，这个过程通过 :class:`_orm.Session` 对象发生，通常是自动的，但也可以手动控制。

            .. seealso::

                :ref:`session_flushing`

        .. tab:: 英文

            This refers to the actual process used by the :term:`unit of work`
            to emit changes to a database.  In SQLAlchemy this process occurs
            via the :class:`_orm.Session` object and is usually automatic, but
            can also be controlled manually.

            .. seealso::

                :ref:`session_flushing`

    expire
    expired
    expires
    expiring
    Expiring
    过期
        .. tab:: 中文

            在 SQLAlchemy ORM 中，指的是当 :term:`persistent` 或有时是 :term:`detached` 对象中的数据被清除时，下次访问对象的属性时，将发出一个 :term:`lazy load` SQL 查询，以便刷新当前正在进行的事务中存储的该对象的数据。

            .. seealso::

                :ref:`session_expire`

        .. tab:: 英文

            In the SQLAlchemy ORM, refers to when the data in a :term:`persistent`
            or sometimes :term:`detached` object is erased, such that when
            the object's attributes are next accessed, a :term:`lazy load` SQL
            query will be emitted in order to refresh the data for this object
            as stored in the current ongoing transaction.

            .. seealso::

                :ref:`session_expire`

    Session
        .. tab:: 中文

            ORM 数据库操作的容器或范围。会话从数据库加载实例，跟踪映射实例的更改，并在刷新时在一个工作单元中持久化更改。

            .. seealso::

                :doc:`orm/session`

        .. tab:: 英文

            The container or scope for ORM database operations. Sessions
            load instances from the database, track changes to mapped
            instances and persist changes in a single unit of work when
            flushed.

            .. seealso::

                :doc:`orm/session`

    columns clause
        .. tab:: 中文

            ``SELECT`` 语句中枚举将在结果集中返回的 SQL 表达式的部分。表达式直接跟在 ``SELECT`` 关键字后面，是一个用逗号分隔的单个表达式列表。

            例如：

            .. sourcecode:: sql

                SELECT user_account.name, user_account.email
                FROM user_account WHERE user_account.name = 'fred'

            上面，列 ``user_account.name`` 和 ``user_account.email`` 是 ``SELECT`` 语句的列子句。

        .. tab:: 英文

            The portion of the ``SELECT`` statement which enumerates the
            SQL expressions to be returned in the result set.  The expressions
            follow the ``SELECT`` keyword directly and are a comma-separated
            list of individual expressions.

            E.g.:

            .. sourcecode:: sql

                SELECT user_account.name, user_account.email
                FROM user_account WHERE user_account.name = 'fred'

            Above, the list of columns ``user_acount.name``,
            ``user_account.email`` is the columns clause of the ``SELECT``.

    WHERE clause
        .. tab:: 中文

            ``SELECT`` 语句中指示按哪些条件过滤行的部分。它是跟在 ``WHERE`` 关键字后面的一个 SQL 表达式。

            .. sourcecode:: sql

                SELECT user_account.name, user_account.email
                FROM user_account
                WHERE user_account.name = 'fred' AND user_account.status = 'E'

            上面，短语 ``WHERE user_account.name = 'fred' AND user_account.status = 'E'`` 构成了 ``SELECT`` 的 WHERE 子句。

        .. tab:: 英文

            The portion of the ``SELECT`` statement which indicates criteria
            by which rows should be filtered.   It is a single SQL expression
            which follows the keyword ``WHERE``.

            .. sourcecode:: sql

                SELECT user_account.name, user_account.email
                FROM user_account
                WHERE user_account.name = 'fred' AND user_account.status = 'E'

            Above, the phrase ``WHERE user_account.name = 'fred' AND user_account.status = 'E'``
            comprises the WHERE clause of the ``SELECT``.

    FROM clause
        .. tab:: 中文

            ``SELECT`` 语句中指示行的初始来源的部分。

            一个简单的 ``SELECT`` 将在其 FROM 子句中包含一个或多个表名。多个来源用逗号分隔：

            .. sourcecode:: sql

                SELECT user.name, address.email_address
                FROM user, address
                WHERE user.id=address.user_id

            FROM 子句也是指定显式连接的地方。我们可以使用一个包含两个表的 ``JOIN`` 的单个 ``FROM`` 元素重写上述 ``SELECT``：

            .. sourcecode:: sql

                SELECT user.name, address.email_address
                FROM user JOIN address ON user.id=address.user_id

        .. tab:: 英文

            The portion of the ``SELECT`` statement which indicates the initial
            source of rows.

            A simple ``SELECT`` will feature one or more table names in its
            FROM clause.  Multiple sources are separated by a comma:

            .. sourcecode:: sql

                SELECT user.name, address.email_address
                FROM user, address
                WHERE user.id=address.user_id

            The FROM clause is also where explicit joins are specified.  We can
            rewrite the above ``SELECT`` using a single ``FROM`` element which consists
            of a ``JOIN`` of the two tables:

            .. sourcecode:: sql

                SELECT user.name, address.email_address
                FROM user JOIN address ON user.id=address.user_id


    subquery
    子查询
    scalar subquery
    标量子查询
        .. tab:: 中文

            指嵌入在封闭的 ``SELECT`` 语句中的 ``SELECT`` 语句。

            子查询有两种一般形式，一种称为“标量选择”，它必须返回一行和一列，另一种形式作为“派生表”并用作另一个选择的 FROM 子句的行来源。标量选择可以放在封闭选择的 :term:`WHERE clause`、:term:`columns clause`、ORDER BY 子句或 HAVING 子句中，而派生表形式可以放在封闭 ``SELECT`` 的 FROM 子句中。

            示例：

            1. 放在封闭 ``SELECT`` 的 :term:`columns clause` 中的标量子查询。在此示例中，子查询是 :term:`correlated subquery`，因为它选择的部分行是通过封闭语句给出的。

                .. sourcecode:: sql

                SELECT id, (SELECT name FROM address WHERE address.user_id=user.id)
                FROM user

            2. 放在封闭 ``SELECT`` 的 :term:`WHERE clause` 中的标量子查询。在此示例中，该子查询未关联，因为它选择了一个固定结果。

                .. sourcecode:: sql

                SELECT id, name FROM user
                WHERE status=(SELECT status_id FROM status_code WHERE code='C')

            3. 放在封闭 ``SELECT`` 的 :term:`FROM clause` 中的派生表子查询。此类子查询几乎总是给出别名。

                .. sourcecode:: sql

                SELECT user.id, user.name, ad_subq.email_address
                FROM
                    user JOIN
                    (select user_id, email_address FROM address WHERE address_type='Q') AS ad_subq
                    ON user.id = ad_subq.user_id

        .. tab:: 英文

            Refers to a ``SELECT`` statement that is embedded within an enclosing
            ``SELECT``.

            A subquery comes in two general flavors, one known as a "scalar select"
            which specifically must return exactly one row and one column, and the
            other form which acts as a "derived table" and serves as a source of
            rows for the FROM clause of another select.  A scalar select is eligible
            to be placed in the :term:`WHERE clause`, :term:`columns clause`,
            ORDER BY clause or HAVING clause of the enclosing select, whereas the
            derived table form is eligible to be placed in the FROM clause of the
            enclosing ``SELECT``.

            Examples:

            1. a scalar subquery placed in the :term:`columns clause` of an enclosing
                ``SELECT``.  The subquery in this example is a :term:`correlated subquery` because part
                of the rows which it selects from are given via the enclosing statement.

                .. sourcecode:: sql

                SELECT id, (SELECT name FROM address WHERE address.user_id=user.id)
                FROM user

            2. a scalar subquery placed in the :term:`WHERE clause` of an enclosing
                ``SELECT``.  This subquery in this example is not correlated as it selects a fixed result.

                .. sourcecode:: sql

                SELECT id, name FROM user
                WHERE status=(SELECT status_id FROM status_code WHERE code='C')

            3. a derived table subquery placed in the :term:`FROM clause` of an enclosing
                ``SELECT``.   Such a subquery is almost always given an alias name.

                .. sourcecode:: sql

                SELECT user.id, user.name, ad_subq.email_address
                FROM
                    user JOIN
                    (select user_id, email_address FROM address WHERE address_type='Q') AS ad_subq
                    ON user.id = ad_subq.user_id

    correlates
    correlated subquery
    相关子查询
    correlated subqueries
        .. tab:: 中文

            如果 :term:`subquery` 依赖于封闭 ``SELECT`` 中的数据，则它是相关的。

            下面，一个子查询从 ``email_address`` 表中选择聚合值 ``MIN(a.id)``，使其针对 ``email_address.user_account_id`` 列关联 ``user_account.id`` 列的值：

            .. sourcecode:: sql

                SELECT user_account.name, email_address.email
                    FROM user_account
                    JOIN email_address ON user_account.id=email_address.user_account_id
                    WHERE email_address.id = (
                    SELECT MIN(a.id) FROM email_address AS a
                    WHERE a.user_account_id=user_account.id
                    )

            上面的子查询指的是 ``user_account`` 表，该表本身不在这个嵌套查询的 ``FROM`` 子句中。相反， ``user_account`` 表是从封闭查询接收的，其中从 ``user_account`` 中选择的每一行都会导致子查询的不同执行。

            在大多数情况下，相关子查询出现在直接封闭 ``SELECT`` 语句的 :term:`WHERE clause` 或 :term:`columns clause` 中，以及 ORDER BY 或 HAVING 子句中。

            在不太常见的情况下，相关子查询可能出现在封闭 ``SELECT`` 的 :term:`FROM clause` 中；在这些情况下，相关性通常是由于封闭的 ``SELECT`` 本身被封闭在另一个 ``SELECT`` 的 WHERE、ORDER BY、columns 或 HAVING 子句中，例如：

            .. sourcecode:: sql

                SELECT parent.id FROM parent
                WHERE EXISTS (
                    SELECT * FROM (
                        SELECT child.id AS id, child.parent_id AS parent_id, child.pos AS pos
                        FROM child
                        WHERE child.parent_id = parent.id ORDER BY child.pos
                    LIMIT 3)
                WHERE id = 7)

            不能通过 ``FROM`` 子句直接将一个 ``SELECT`` 的相关性关联到封闭查询，因为只有当封闭语句的 FROM 子句中的原始源行可用时，相关性才能进行。

        .. tab:: 英文

            A :term:`subquery` is correlated if it depends on data in the
            enclosing ``SELECT``.

            Below, a subquery selects the aggregate value ``MIN(a.id)``
            from the ``email_address`` table, such that
            it will be invoked for each value of ``user_account.id``, correlating
            the value of this column against the ``email_address.user_account_id``
            column:

            .. sourcecode:: sql

                SELECT user_account.name, email_address.email
                    FROM user_account
                    JOIN email_address ON user_account.id=email_address.user_account_id
                    WHERE email_address.id = (
                    SELECT MIN(a.id) FROM email_address AS a
                    WHERE a.user_account_id=user_account.id
                    )

            The above subquery refers to the ``user_account`` table, which is not itself
            in the ``FROM`` clause of this nested query.   Instead, the ``user_account``
            table is received from the enclosing query, where each row selected from
            ``user_account`` results in a distinct execution of the subquery.

            A correlated subquery is in most cases present in the :term:`WHERE clause`
            or :term:`columns clause` of the immediately enclosing ``SELECT``
            statement, as well as in the ORDER BY or HAVING clause.

            In less common cases, a correlated subquery may be present in the
            :term:`FROM clause` of an enclosing ``SELECT``; in these cases the
            correlation is typically due to the enclosing ``SELECT`` itself being
            enclosed in the WHERE,
            ORDER BY, columns or HAVING clause of another ``SELECT``, such as:

            .. sourcecode:: sql

                SELECT parent.id FROM parent
                WHERE EXISTS (
                    SELECT * FROM (
                        SELECT child.id AS id, child.parent_id AS parent_id, child.pos AS pos
                        FROM child
                        WHERE child.parent_id = parent.id ORDER BY child.pos
                    LIMIT 3)
                WHERE id = 7)

            Correlation from one ``SELECT`` directly to one which encloses the correlated
            query via its ``FROM``
            clause is not possible, because the correlation can only proceed once the
            original source rows from the enclosing statement's FROM clause are available.


    ACID
    ACID model
        .. tab:: 中文

            “原子性、一致性、隔离性、持久性”的首字母缩写；一组保证数据库事务可靠处理的属性。
            （via Wikipedia）

            .. seealso::

                :term:`atomicity`

                :term:`consistency`

                :term:`isolation`

                :term:`durability`

                `ACID Model (via Wikipedia) <https://en.wikipedia.org/wiki/ACID_Model>`_

        .. tab:: 英文

            An acronym for "Atomicity, Consistency, Isolation,
            Durability"; a set of properties that guarantee that
            database transactions are processed reliably.
            (via Wikipedia)

            .. seealso::

                :term:`atomicity`

                :term:`consistency`

                :term:`isolation`

                :term:`durability`

                `ACID Model (via Wikipedia) <https://en.wikipedia.org/wiki/ACID_Model>`_

    atomicity
    原子性
        .. tab:: 中文

            原子性是 :term:`ACID` 模型的组成部分之一，要求每个事务是“全有或全无”的：如果事务的一部分失败，则整个事务失败，数据库状态保持不变。原子系统必须在每种情况下都保证原子性，包括停电、错误和崩溃。（via Wikipedia）

            .. seealso::

                :term:`ACID`

                `Atomicity (via Wikipedia) <https://en.wikipedia.org/wiki/Atomicity_(database_systems)>`_

        .. tab:: 英文

            Atomicity is one of the components of the :term:`ACID` model,
            and requires that each transaction is "all or nothing":
            if one part of the transaction fails, the entire transaction
            fails, and the database state is left unchanged. An atomic
            system must guarantee atomicity in each and every situation,
            including power failures, errors, and crashes.
            (via Wikipedia)

            .. seealso::

                :term:`ACID`

                `Atomicity (via Wikipedia) <https://en.wikipedia.org/wiki/Atomicity_(database_systems)>`_

    consistency
    一致性
        .. tab:: 中文

            一致性是 :term:`ACID` 模型的组成部分之一，确保任何事务都将数据库从一个有效状态带到另一个有效状态。写入数据库的任何数据都必须符合所有定义的规则，包括但不限于 :term:`constraints`、级联、触发器及其任何组合。（via Wikipedia）

            .. seealso::

                :term:`ACID`

                `Consistency (via Wikipedia) <https://en.wikipedia.org/wiki/Consistency_(database_systems)>`_

        .. tab:: 英文

            Consistency is one of the components of the :term:`ACID` model,
            and ensures that any transaction will
            bring the database from one valid state to another. Any data
            written to the database must be valid according to all defined
            rules, including but not limited to :term:`constraints`, cascades,
            triggers, and any combination thereof.
            (via Wikipedia)

            .. seealso::

                :term:`ACID`

                `Consistency (via Wikipedia) <https://en.wikipedia.org/wiki/Consistency_(database_systems)>`_

    isolation
    isolated
    isolation level
    隔离级别
        .. tab:: 中文

            隔离性是 :term:`ACID` 模型的组成部分之一，确保事务的并发执行结果是一个系统状态，该状态将是事务按顺序执行时获得的状态，即一个接一个地执行。每个事务必须在完全隔离的情况下执行，即如果 T1 和 T2 并发执行，则每个事务应保持独立。（via Wikipedia）

            .. seealso::

                :term:`ACID`

                `Isolation (via Wikipedia) <https://en.wikipedia.org/wiki/Isolation_(database_systems)>`_

                :term:`read uncommitted`

                :term:`read committed`

                :term:`repeatable read`

                :term:`serializable`

        .. tab:: 英文

            The isolation property of the :term:`ACID` model
            ensures that the concurrent execution
            of transactions results in a system state that would be
            obtained if transactions were executed serially, i.e. one
            after the other. Each transaction must execute in total
            isolation i.e. if T1 and T2 execute concurrently then each
            should remain independent of the other.
            (via Wikipedia)

            .. seealso::

                :term:`ACID`

                `Isolation (via Wikipedia) <https://en.wikipedia.org/wiki/Isolation_(database_systems)>`_

                :term:`read uncommitted`

                :term:`read committed`

                :term:`repeatable read`

                :term:`serializable`

    repeatable read
    可重复读
        .. tab:: 中文

            四种数据库 :term:`isolation` 级别之一，repeatable read 具有 :term:`read committed` 的所有隔离特性，此外，还具有在事务中读取的任何特定行在该事务期间保证不受任何后续外部更改（即来自其他并发 UPDATE 语句）的影响。

        .. tab:: 英文

            One of the four database :term:`isolation` levels, repeatable read
            features all of the isolation of :term:`read committed`, and
            additionally features that any particular row that is read within a
            transaction is guaranteed from that point to not have any subsequent
            external changes in value (i.e. from other concurrent UPDATE
            statements) for the duration of that transaction.

    read committed
    读已提交
        .. tab:: 中文

            四种数据库 :term:`isolation` 级别之一，read committed 确保事务不会暴露给其他并发事务中尚未提交的任何数据，从而防止所谓的“脏读”。然而，在 read committed 下可能会有不可重复读，这意味着如果另一个事务已提交更改，则第二次读取行中的数据可能会更改。

        .. tab:: 英文

            One of the four database :term:`isolation` levels, read committed
            features that the transaction will not be exposed to any data from
            other concurrent transactions that has not been committed yet,
            preventing so-called "dirty reads".  However, under read committed
            there can be non-repeatable reads, meaning data in a row may change
            when read a second time if another transaction has committed changes.

    read uncommitted
    读取未提交
        .. tab:: 中文

            四种数据库 :term:`isolation` 级别之一，read uncommitted 的特性是事务中的数据更改在事务提交之前不会永久生效。然而，在 read uncommitted 中，可能在另一个事务的范围内查看未在其他事务中提交的数据；这些被称为“脏读”。

        .. tab:: 英文

            One of the four database :term:`isolation` levels, read uncommitted
            features that changes made to database data within a transaction will
            not become permanent until the transaction is committed.   However,
            within read uncommitted, it may be possible for data that is not
            committed in other transactions to be viewable within the scope of
            another transaction; these are known as "dirty reads".

    serializable
    可序列化
        .. tab:: 中文

            四种数据库 :term:`isolation` 级别之一，serializable 具有 :term:`repeatable read` 的所有隔离特性，并且在基于锁的方法中保证不会发生所谓的“幻读”；这意味着在其他事务范围内 INSERT 或 DELETE 的行在此事务中将不可检测。在此事务中读取的行保证继续存在，而不存在的行保证不会因另一个事务的插入而出现。

            Serializable 隔离通常依赖于行或行范围的锁定来实现此效果，这可能会增加死锁的可能性并降低性能。还有一些非锁定的方案，但这些方案必然依赖于在检测到写冲突时拒绝事务。

        .. tab:: 英文

            One of the four database :term:`isolation` levels, serializable
            features all of the isolation of :term:`repeatable read`, and
            additionally within a lock-based approach guarantees that so-called
            "phantom reads" cannot occur; this means that rows which are INSERTed
            or DELETEd within the scope of other transactions will not be
            detectable within this transaction.   A row that is read within this
            transaction is guaranteed to continue existing, and a row that does not
            exist is guaranteed that it cannot appear of inserted from another
            transaction.

            Serializable isolation typically relies upon locking of rows or ranges
            of rows in order to achieve this effect and can increase the chance of
            deadlocks and degrade performance.   There are also non-lock based
            schemes however these necessarily rely upon rejecting transactions if
            write collisions are detected.


    durability
    耐久性
        .. tab:: 中文

            持久性是 :term:`ACID` 模型的一个属性，意味着一旦事务被提交，即使在断电、崩溃或错误的情况下，它也将保持提交状态。例如，在关系数据库中，一旦一组 SQL 语句执行完毕，结果需要永久存储（即使数据库在此后立即崩溃）。
            （via Wikipedia）

            .. seealso::

                :term:`ACID`

                `Durability (via Wikipedia) <https://en.wikipedia.org/wiki/Durability_(database_systems)>`_

        .. tab:: 英文

            Durability is a property of the :term:`ACID` model
            which means that once a transaction has been committed,
            it will remain so, even in the event of power loss, crashes,
            or errors. In a relational database, for instance, once a
            group of SQL statements execute, the results need to be stored
            permanently (even if the database crashes immediately
            thereafter).
            (via Wikipedia)

            .. seealso::

                :term:`ACID`

                `Durability (via Wikipedia) <https://en.wikipedia.org/wiki/Durability_(database_systems)>`_

    RETURNING
        .. tab:: 中文

            这是某些后端以各种形式提供的非SQL标准子句，提供在执行 INSERT、UPDATE 或 DELETE 语句时返回结果集的服务。可以返回匹配行的任何列集，就像它们是由 SELECT 语句生成的一样。

            RETURNING 子句为常见的更新/选择场景提供了显著的性能提升，包括在创建时检索内联或默认生成的主键值和默认值，以及以原子方式获取服务器生成的默认值。

            PostgreSQL 中的 RETURNING 示例如下所示：

            .. sourcecode:: sql

                INSERT INTO user_account (name) VALUES ('new name') RETURNING id, timestamp

            如上所述，INSERT 语句在执行时将提供一个结果集，其中包括列 ``user_account.id`` 和 ``user_account.timestamp`` 的值，上述值应作为默认值生成，因为它们未包含在其他地方（但请注意，任何列或 SQL 表达式序列都可以放入 RETURNING 中，而不仅仅是默认值列）。

            当前支持 RETURNING 或类似构造的后端有 PostgreSQL、SQL Server、Oracle Database 和 Firebird。PostgreSQL 和 Firebird 的实现通常是全功能的，而 SQL Server 和 Oracle Database 的实现有一些注意事项。在 SQL Server 上，该子句在 INSERT 和 UPDATE 语句中称为"OUTPUT INSERTED"，在 DELETE 语句中称为"OUTPUT DELETED"；关键注意事项是触发器与此关键字不支持。在 Oracle Database 中，它被称为"RETURNING...INTO"，并且要求将值放入 OUT 参数中，这不仅使语法笨拙，而且一次只能用于一行。

            SQLAlchemy 的 :meth:`.UpdateBase.returning` 系统在这些后端的 RETURNING 系统之上提供了一个抽象层，以提供一致的列返回接口。ORM 还包括许多在可用时使用 RETURNING 的优化。

        .. tab:: 英文

            This is a non-SQL standard clause provided in various forms by
            certain backends, which provides the service of returning a result
            set upon execution of an INSERT, UPDATE or DELETE statement.  Any set
            of columns from the matched rows can be returned, as though they were
            produced from a SELECT statement.

            The RETURNING clause provides both a dramatic performance boost to
            common update/select scenarios, including retrieval of inline- or
            default- generated primary key values and defaults at the moment they
            were created, as well as a way to get at server-generated
            default values in an atomic way.

            An example of RETURNING, idiomatic to PostgreSQL, looks like:

            .. sourcecode:: sql

                INSERT INTO user_account (name) VALUES ('new name') RETURNING id, timestamp

            Above, the INSERT statement will provide upon execution a result set
            which includes the values of the columns ``user_account.id`` and
            ``user_account.timestamp``, which above should have been generated as default
            values as they are not included otherwise (but note any series of columns
            or SQL expressions can be placed into RETURNING, not just default-value columns).

            The backends that currently support RETURNING or a similar construct
            are PostgreSQL, SQL Server, Oracle Database, and Firebird.  The
            PostgreSQL and Firebird implementations are generally full featured,
            whereas the implementations of SQL Server and Oracle Database have
            caveats. On SQL Server, the clause is known as "OUTPUT INSERTED" for
            INSERT and UPDATE statements and "OUTPUT DELETED" for DELETE
            statements; the key caveat is that triggers are not supported in
            conjunction with this keyword.  In Oracle Database, it is known as
            "RETURNING...INTO", and requires that the value be placed into an OUT
            parameter, meaning not only is the syntax awkward, but it can also only
            be used for one row at a time.

            SQLAlchemy's :meth:`.UpdateBase.returning` system provides a layer of abstraction
            on top of the RETURNING systems of these backends to provide a consistent
            interface for returning columns.  The ORM also includes many optimizations
            that make use of RETURNING when available.

    one to many
    一对多
        .. tab:: 中文

            一种 :func:`~sqlalchemy.orm.relationship` 样式，它将父映射器表的主键链接到相关表的外键。每个唯一的父对象可以引用零个或多个唯一的相关对象。

            相关对象反过来将与其父对象有隐式或显式的 :term:`many to one` 关系。

            一个一对多模式的示例（请注意，这与 :term:`many to one` 模式相同）：

            .. sourcecode:: sql

                CREATE TABLE department (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30),
                    dep_id INTEGER REFERENCES department(id)
                )

            ``department`` 到 ``employee`` 的关系是一对多，因为许多员工记录可以与一个部门关联。一个 SQLAlchemy 映射可能如下所示::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    employees = relationship("Employee")


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))

            .. seealso::

                :term:`relationship`

                :term:`many to one`

                :term:`backref`

        .. tab:: 英文

            A style of :func:`~sqlalchemy.orm.relationship` which links
            the primary key of the parent mapper's table to the foreign
            key of a related table.   Each unique parent object can
            then refer to zero or more unique related objects.

            The related objects in turn will have an implicit or
            explicit :term:`many to one` relationship to their parent
            object.

            An example one to many schema (which, note, is identical
            to the :term:`many to one` schema):

            .. sourcecode:: sql

                CREATE TABLE department (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30),
                    dep_id INTEGER REFERENCES department(id)
                )

            The relationship from ``department`` to ``employee`` is
            one to many, since many employee records can be associated with a
            single department.  A SQLAlchemy mapping might look like::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    employees = relationship("Employee")


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))

            .. seealso::

                :term:`relationship`

                :term:`many to one`

                :term:`backref`

    many to one
    多对一
        .. tab:: 中文

            一种 :func:`~sqlalchemy.orm.relationship` 样式，它将父映射器表中的外键链接到相关表的主键。每个父对象可以引用零个或一个相关对象。

            相关对象反过来将与引用它们的任意数量的父对象具有隐式或显式的 :term:`one to many` 关系。

            一个多对一模式的示例（请注意，这与 :term:`one to many` 模式相同）：

            .. sourcecode:: sql

                CREATE TABLE department (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30),
                    dep_id INTEGER REFERENCES department(id)
                )

            ``employee`` 到 ``department`` 的关系是多对一，因为许多员工记录可以与一个部门关联。一个 SQLAlchemy 映射可能如下所示::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))
                    department = relationship("Department")

            .. seealso::

                :term:`relationship`

                :term:`one to many`

                :term:`backref`

        .. tab:: 英文

            A style of :func:`~sqlalchemy.orm.relationship` which links
            a foreign key in the parent mapper's table to the primary
            key of a related table.   Each parent object can
            then refer to exactly zero or one related object.

            The related objects in turn will have an implicit or
            explicit :term:`one to many` relationship to any number
            of parent objects that refer to them.

            An example many to one schema (which, note, is identical
            to the :term:`one to many` schema):

            .. sourcecode:: sql

                CREATE TABLE department (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30),
                    dep_id INTEGER REFERENCES department(id)
                )


            The relationship from ``employee`` to ``department`` is
            many to one, since many employee records can be associated with a
            single department.  A SQLAlchemy mapping might look like::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))
                    department = relationship("Department")

            .. seealso::

                :term:`relationship`

                :term:`one to many`

                :term:`backref`

    backref
    bidirectional relationship
    双向关系
        .. tab:: 中文

            对 :term:`relationship` 系统的扩展，其中两个不同的 :func:`~sqlalchemy.orm.relationship` 对象可以相互关联，以便在任一方发生变化时在内存中协调。这两个关系最常见的构建方式是显式使用 :func:`~sqlalchemy.orm.relationship` 函数为一方指定 ``backref`` 关键字，以便另一方的 :func:`~sqlalchemy.orm.relationship` 自动创建。我们可以使用 :term:`one to many` 中的示例来说明这一点::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    employees = relationship("Employee", backref="department")


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))

            backref 可以应用于任何关系，包括一对多、多对一和 :term:`many to many`。

            .. seealso::

                :term:`relationship`

                :term:`one to many`

                :term:`many to one`

                :term:`many to many`

        .. tab:: 英文

            An extension to the :term:`relationship` system whereby two
            distinct :func:`~sqlalchemy.orm.relationship` objects can be
            mutually associated with each other, such that they coordinate
            in memory as changes occur to either side.   The most common
            way these two relationships are constructed is by using
            the :func:`~sqlalchemy.orm.relationship` function explicitly
            for one side and specifying the ``backref`` keyword to it so that
            the other :func:`~sqlalchemy.orm.relationship` is created
            automatically.  We can illustrate this against the example we've
            used in :term:`one to many` as follows::

                class Department(Base):
                    __tablename__ = "department"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    employees = relationship("Employee", backref="department")


                class Employee(Base):
                    __tablename__ = "employee"
                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))
                    dep_id = Column(Integer, ForeignKey("department.id"))

            A backref can be applied to any relationship, including one to many,
            many to one, and :term:`many to many`.

            .. seealso::

                :term:`relationship`

                :term:`one to many`

                :term:`many to one`

                :term:`many to many`

    many to many
    多对多
        .. tab:: 中文

            一种 :func:`sqlalchemy.orm.relationship` 样式，通过中间表将两个表链接在一起。使用此配置，左侧的任意数量的行可以引用右侧的任意数量的行，反之亦然。

            一个将员工与项目关联的模式：

            .. sourcecode:: sql

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE project (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee_project (
                    employee_id INTEGER PRIMARY KEY,
                    project_id INTEGER PRIMARY KEY,
                    FOREIGN KEY (employee_id) REFERENCES employee(id),
                    FOREIGN KEY (project_id) REFERENCES project(id)
                )

            如上所述， ``employee_project`` 表是多对多表，自然形成由每个相关表的主键组成的复合主键。

            在 SQLAlchemy 中，:func:`sqlalchemy.orm.relationship` 函数可以以大多数透明的方式表示这种关系，其中多对多表使用简单的表元数据指定::

                class Employee(Base):
                    __tablename__ = "employee"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))

                    projects = relationship(
                        "Project",
                        secondary=Table(
                            "employee_project",
                            Base.metadata,
                            Column("employee_id", Integer, ForeignKey("employee.id"), primary_key=True),
                            Column("project_id", Integer, ForeignKey("project.id"), primary_key=True),
                        ),
                        backref="employees",
                    )


                class Project(Base):
                    __tablename__ = "project"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))

            如上所述，定义了 ``Employee.projects`` 和反向引用的 ``Project.employees`` 集合::

                proj = Project(name="Client A")

                emp1 = Employee(name="emp1")
                emp2 = Employee(name="emp2")

                proj.employees.extend([emp1, emp2])

            .. seealso::

                :term:`association relationship`

                :term:`relationship`

                :term:`one to many`

                :term:`many to one`

        .. tab:: 英文

            A style of :func:`sqlalchemy.orm.relationship` which links two tables together
            via an intermediary table in the middle.   Using this configuration,
            any number of rows on the left side may refer to any number of
            rows on the right, and vice versa.

            A schema where employees can be associated with projects:

            .. sourcecode:: sql

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE project (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee_project (
                    employee_id INTEGER PRIMARY KEY,
                    project_id INTEGER PRIMARY KEY,
                    FOREIGN KEY employee_id REFERENCES employee(id),
                    FOREIGN KEY project_id REFERENCES project(id)
                )

            Above, the ``employee_project`` table is the many-to-many table,
            which naturally forms a composite primary key consisting
            of the primary key from each related table.

            In SQLAlchemy, the :func:`sqlalchemy.orm.relationship` function
            can represent this style of relationship in a mostly
            transparent fashion, where the many-to-many table is
            specified using plain table metadata::

                class Employee(Base):
                    __tablename__ = "employee"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))

                    projects = relationship(
                        "Project",
                        secondary=Table(
                            "employee_project",
                            Base.metadata,
                            Column("employee_id", Integer, ForeignKey("employee.id"), primary_key=True),
                            Column("project_id", Integer, ForeignKey("project.id"), primary_key=True),
                        ),
                        backref="employees",
                    )


                class Project(Base):
                    __tablename__ = "project"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))

            Above, the ``Employee.projects`` and back-referencing ``Project.employees``
            collections are defined::

                proj = Project(name="Client A")

                emp1 = Employee(name="emp1")
                emp2 = Employee(name="emp2")

                proj.employees.extend([emp1, emp2])

            .. seealso::

                :term:`association relationship`

                :term:`relationship`

                :term:`one to many`

                :term:`many to one`

    relationship
    relationships
        .. tab:: 中文

            两个映射类之间的连接单元，对应于数据库中两个表之间的某种关系。

            该关系使用 SQLAlchemy 函数 :func:`~sqlalchemy.orm.relationship` 定义。一旦创建，SQLAlchemy 会检查涉及的参数和底层映射，以将关系分类为以下三种类型之一：:term:`one to many`、:term:`many to one` 或 :term:`many to many`。通过这种分类，关系结构处理数据库中适当链接的持久化任务，以响应内存中的对象关联，以及根据数据库中的当前链接将对象引用和集合加载到内存中的任务。

            .. seealso::

                :ref:`relationship_config_toplevel`

        .. tab:: 英文

            A connecting unit between two mapped classes, corresponding
            to some relationship between the two tables in the database.

            The relationship is defined using the SQLAlchemy function
            :func:`~sqlalchemy.orm.relationship`.   Once created, SQLAlchemy
            inspects the arguments and underlying mappings involved
            in order to classify the relationship as one of three types:
            :term:`one to many`, :term:`many to one`, or :term:`many to many`.
            With this classification, the relationship construct
            handles the task of persisting the appropriate linkages
            in the database in response to in-memory object associations,
            as well as the job of loading object references and collections
            into memory based on the current linkages in the
            database.

            .. seealso::

                :ref:`relationship_config_toplevel`

    cursor
    游标
        .. tab:: 中文

            一种控制结构，使得能够遍历数据库中的记录。
            在 Python DBAPI 中，cursor 对象实际上是语句执行的起点，也是用于获取结果的接口。

            .. seealso::

                `Cursor Objects (in pep-249) <https://www.python.org/dev/peps/pep-0249/#cursor-objects>`_

                `Cursor (via Wikipedia) <https://en.wikipedia.org/wiki/Cursor_(databases)>`_

        .. tab:: 英文

            A control structure that enables traversal over the records in a database.
            In the Python DBAPI, the cursor object is in fact the starting point
            for statement execution as well as the interface used for fetching
            results.

            .. seealso::

                `Cursor Objects (in pep-249) <https://www.python.org/dev/peps/pep-0249/#cursor-objects>`_

                `Cursor (via Wikipedia) <https://en.wikipedia.org/wiki/Cursor_(databases)>`_


    association relationship
    关联关系
        .. tab:: 中文

            一种两级的 :term:`relationship`，使用中间的关联表将两个表连接在一起。关联关系不同于 :term:`many to many` 关系，因为多对多表由一个完整的类映射，而不是像多对多那样由 :func:`sqlalchemy.orm.relationship` 构造隐式处理，这样可以显式地使用附加属性。

            例如，如果我们想将员工与项目关联起来，同时存储该员工在项目中的具体角色，关系模式可能如下所示：

            .. sourcecode:: sql

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE project (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee_project (
                    employee_id INTEGER PRIMARY KEY,
                    project_id INTEGER PRIMARY KEY,
                    role_name VARCHAR(30),
                    FOREIGN KEY (employee_id) REFERENCES employee(id),
                    FOREIGN KEY (project_id) REFERENCES project(id)
                )

            上述的 SQLAlchemy 声明映射可能如下所示::

                class Employee(Base):
                    __tablename__ = "employee"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class Project(Base):
                    __tablename__ = "project"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class EmployeeProject(Base):
                    __tablename__ = "employee_project"

                    employee_id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
                    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
                    role_name = Column(String(30))

                    project = relationship("Project", backref="project_employees")
                    employee = relationship("Employee", backref="employee_projects")

            可以为项目添加员工并指定角色名称::

                proj = Project(name="Client A")

                emp1 = Employee(name="emp1")
                emp2 = Employee(name="emp2")

                proj.project_employees.extend(
                    [
                        EmployeeProject(employee=emp1, role_name="tech lead"),
                        EmployeeProject(employee=emp2, role_name="account executive"),
                    ]
                )

            .. seealso::

                :term:`many to many`

        .. tab:: 英文

            A two-tiered :term:`relationship` which links two tables
            together using an association table in the middle.  The
            association relationship differs from a :term:`many to many`
            relationship in that the many-to-many table is mapped
            by a full class, rather than invisibly handled by the
            :func:`sqlalchemy.orm.relationship` construct as in the case
            with many-to-many, so that additional attributes are
            explicitly available.

            For example, if we wanted to associate employees with
            projects, also storing the specific role for that employee
            with the project, the relational schema might look like:

            .. sourcecode:: sql

                CREATE TABLE employee (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE project (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(30)
                )

                CREATE TABLE employee_project (
                    employee_id INTEGER PRIMARY KEY,
                    project_id INTEGER PRIMARY KEY,
                    role_name VARCHAR(30),
                    FOREIGN KEY employee_id REFERENCES employee(id),
                    FOREIGN KEY project_id REFERENCES project(id)
                )

            A SQLAlchemy declarative mapping for the above might look like::

                class Employee(Base):
                    __tablename__ = "employee"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class Project(Base):
                    __tablename__ = "project"

                    id = Column(Integer, primary_key=True)
                    name = Column(String(30))


                class EmployeeProject(Base):
                    __tablename__ = "employee_project"

                    employee_id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
                    project_id = Column(Integer, ForeignKey("project.id"), primary_key=True)
                    role_name = Column(String(30))

                    project = relationship("Project", backref="project_employees")
                    employee = relationship("Employee", backref="employee_projects")

            Employees can be added to a project given a role name::

                proj = Project(name="Client A")

                emp1 = Employee(name="emp1")
                emp2 = Employee(name="emp2")

                proj.project_employees.extend(
                    [
                        EmployeeProject(employee=emp1, role_name="tech lead"),
                        EmployeeProject(employee=emp2, role_name="account executive"),
                    ]
                )

            .. seealso::

                :term:`many to many`

    constraint
    constraints
    constrained
    约束
        .. tab:: 中文

            在关系数据库中建立的规则，确保数据的有效性和一致性。常见的约束形式包括 :term:`primary key constraint`、:term:`foreign key constraint` 和 :term:`check constraint`。

        .. tab:: 英文

            Rules established within a relational database that ensure
            the validity and consistency of data.   Common forms
            of constraint include :term:`primary key constraint`,
            :term:`foreign key constraint`, and :term:`check constraint`.

    candidate key
    候选键
        .. tab:: 中文

            一个 :term:`relational algebra` 术语，指的是形成行的唯一标识键的属性或属性集。一个行可以有多个候选键，每个候选键都适合作为该行的主键。表的主键始终是候选键。

            .. seealso::

                :term:`primary key`

                `Candidate key (via Wikipedia) <https://en.wikipedia.org/wiki/Candidate_key>`_

                https://www.databasestar.com/database-keys/

        .. tab:: 英文


            A :term:`relational algebra` term referring to an attribute or set
            of attributes that form a uniquely identifying key for a
            row.  A row may have more than one candidate key, each of which
            is suitable for use as the primary key of that row.
            The primary key of a table is always a candidate key.

            .. seealso::

                :term:`primary key`

                `Candidate key (via Wikipedia) <https://en.wikipedia.org/wiki/Candidate_key>`_

                https://www.databasestar.com/database-keys/

    primary key
    主键
    primary key constraint
    主键约束
        .. tab:: 中文

            一种 :term:`constraint`，唯一定义表中每行的特征。主键必须由任何其他行都不能复制的特征组成。主键可以由单个属性或多个属性组合而成。
            (via Wikipedia)

            表的主键通常（但并非总是）在 ``CREATE TABLE`` :term:`DDL` 中定义：

            .. sourcecode:: sql

                CREATE TABLE employee (
                        emp_id INTEGER,
                        emp_name VARCHAR(30),
                        dep_id INTEGER,
                        PRIMARY KEY (emp_id)
                )

            .. seealso::

                :term:`composite primary key`

                `Primary key (via Wikipedia) <https://en.wikipedia.org/wiki/Primary_Key>`_

        .. tab:: 英文

            A :term:`constraint` that uniquely defines the characteristics
            of each row in a table. The primary key has to consist of
            characteristics that cannot be duplicated by any other row.
            The primary key may consist of a single attribute or
            multiple attributes in combination.
            (via Wikipedia)

            The primary key of a table is typically, though not always,
            defined within the ``CREATE TABLE`` :term:`DDL`:

            .. sourcecode:: sql

                CREATE TABLE employee (
                        emp_id INTEGER,
                        emp_name VARCHAR(30),
                        dep_id INTEGER,
                        PRIMARY KEY (emp_id)
                )

            .. seealso::

                :term:`composite primary key`

                `Primary key (via Wikipedia) <https://en.wikipedia.org/wiki/Primary_Key>`_

    composite primary key
    复合主键
        .. tab:: 中文

            一个 :term:`primary key`，包含多个列。特定的数据库行基于两个或多个列而不是单个值唯一。

            .. seealso::

                :term:`primary key`

        .. tab:: 英文

            A :term:`primary key` that has more than one column.   A particular
            database row is unique based on two or more columns rather than just
            a single value.

            .. seealso::

                :term:`primary key`

    foreign key constraint
    外键约束
        .. tab:: 中文

            一个表之间的参照约束。外键是关系表中的一个字段或一组字段，与另一个表的 :term:`candidate key` 匹配。外键可用于交叉引用表。
            (via Wikipedia)

            可以使用标准 SQL 中的 :term:`DDL` 向表添加外键约束，如下所示：

            .. sourcecode:: sql

                ALTER TABLE employee ADD CONSTRAINT dep_id_fk
                FOREIGN KEY (employee) REFERENCES department (dep_id)

            .. seealso::

                `Foreign Key Constraint (via Wikipedia) <https://en.wikipedia.org/wiki/Foreign_key_constraint>`_

        .. tab:: 英文

            A referential constraint between two tables.  A foreign key is a field or set of fields in a
            relational table that matches a :term:`candidate key` of another table.
            The foreign key can be used to cross-reference tables.
            (via Wikipedia)

            A foreign key constraint can be added to a table in standard
            SQL using :term:`DDL` like the following:

            .. sourcecode:: sql

                ALTER TABLE employee ADD CONSTRAINT dep_id_fk
                FOREIGN KEY (employee) REFERENCES department (dep_id)

            .. seealso::

                `Foreign Key Constraint (via Wikipedia) <https://en.wikipedia.org/wiki/Foreign_key_constraint>`_

    check constraint
    检查约束
        .. tab:: 中文

            一个检查约束是一个条件，用于定义在关系数据库的表中添加或更新条目时的有效数据。检查约束适用于表中的每一行。

            (via Wikipedia)

            可以使用标准 SQL 中的 :term:`DDL` 向表添加检查约束，如下所示：

            .. sourcecode:: sql

                ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);

            .. seealso::

                `CHECK constraint (via Wikipedia) <https://en.wikipedia.org/wiki/Check_constraint>`_

        .. tab:: 英文

            A check constraint is a
            condition that defines valid data when adding or updating an
            entry in a table of a relational database. A check constraint
            is applied to each row in the table.

            (via Wikipedia)

            A check constraint can be added to a table in standard
            SQL using :term:`DDL` like the following:

            .. sourcecode:: sql

                ALTER TABLE distributors ADD CONSTRAINT zipchk CHECK (char_length(zipcode) = 5);

            .. seealso::

                `CHECK constraint (via Wikipedia) <https://en.wikipedia.org/wiki/Check_constraint>`_

    unique constraint
    唯一约束
    unique key index
    唯一键索引
        .. tab:: 中文

            唯一键索引可以唯一标识数据库表中的每一行数据值。唯一键索引由单个列或单个数据库表中的一组列组成。如果不使用 NULL 值，则数据库表中的两行或数据记录不能在这些唯一键索引列中具有相同的数据值（或数据值组合）。根据其设计，数据库表可以有多个唯一键索引，但最多只能有一个主键索引。

            (via Wikipedia)

            .. seealso::

                `Unique key (via Wikipedia) <https://en.wikipedia.org/wiki/Unique_key#Defining_unique_keys>`_

        .. tab:: 英文

            A unique key index can uniquely identify each row of data
            values in a database table. A unique key index comprises a
            single column or a set of columns in a single database table.
            No two distinct rows or data records in a database table can
            have the same data value (or combination of data values) in
            those unique key index columns if NULL values are not used.
            Depending on its design, a database table may have many unique
            key indexes but at most one primary key index.

            (via Wikipedia)

            .. seealso::

                `Unique key (via Wikipedia) <https://en.wikipedia.org/wiki/Unique_key#Defining_unique_keys>`_

    transient
    瞬态
        .. tab:: 中文

            这描述了对象在 :term:`Session` 中可以具有的主要对象状态之一；一个瞬态对象是一个没有任何数据库标识的新对象，并且尚未与会话关联。当对象被添加到会话中时，它会移动到 :term:`pending` 状态。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            This describes one of the major object states which
            an object can have within a :term:`Session`; a transient object
            is a new object that doesn't have any database identity
            and has not been associated with a session yet.  When the
            object is added to the session, it moves to the
            :term:`pending` state.

            .. seealso::

                :ref:`session_object_states`

    pending
    待办的
        .. tab:: 中文

            这描述了对象在 :term:`Session` 中可以具有的主要对象状态之一；一个挂起对象是一个没有任何数据库标识的新对象，但最近已与会话关联。当会话发出刷新并插入行时，对象会移动到 :term:`persistent` 状态。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            This describes one of the major object states which
            an object can have within a :term:`Session`; a pending object
            is a new object that doesn't have any database identity,
            but has been recently associated with a session.   When
            the session emits a flush and the row is inserted, the
            object moves to the :term:`persistent` state.

            .. seealso::

                :ref:`session_object_states`

    deleted
    删除的
        .. tab:: 中文

            这描述了对象在 :term:`Session` 中可以具有的主要对象状态之一；一个已删除对象是一个以前是持久的对象，并且在刷新到数据库中发出 DELETE 语句以删除其行。对象将在会话事务提交后移动到 :term:`detached` 状态；或者，如果会话事务被回滚，DELETE 将被还原，对象将返回到 :term:`persistent` 状态。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            This describes one of the major object states which
            an object can have within a :term:`Session`; a deleted object
            is an object that was formerly persistent and has had a
            DELETE statement emitted to the database within a flush
            to delete its row.  The object will move to the :term:`detached`
            state once the session's transaction is committed; alternatively,
            if the session's transaction is rolled back, the DELETE is
            reverted and the object moves back to the :term:`persistent`
            state.

            .. seealso::

                :ref:`session_object_states`

    persistent
    持久的
        .. tab:: 中文

            这描述了对象在 :term:`Session` 中可以具有的主要对象状态之一；一个持久对象是具有数据库标识（即主键）并且当前与会话关联的对象。任何先前处于 :term:`pending` 状态并且现在已插入的对象，以及任何由会话从数据库加载的对象，都是处于持久状态。当一个持久对象从会话中移除时，它被称为 :term:`detached`。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            This describes one of the major object states which
            an object can have within a :term:`Session`; a persistent object
            is an object that has a database identity (i.e. a primary key)
            and is currently associated with a session.   Any object
            that was previously :term:`pending` and has now been inserted
            is in the persistent state, as is any object that's
            been loaded by the session from the database.   When a
            persistent object is removed from a session, it is known
            as :term:`detached`.

            .. seealso::

                :ref:`session_object_states`

    detached
    分离的
        .. tab:: 中文

            这描述了对象在 :term:`Session` 中可以具有的主要对象状态之一；一个分离对象是具有数据库标识（即主键）但未与任何会话关联的对象。以前处于 :term:`persistent` 状态并被移出其会话的对象，无论是因为被删除还是拥有会话被关闭，都会移到分离状态。分离状态通常在对象在会话之间移动或在与外部对象缓存之间移动时使用。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            This describes one of the major object states which
            an object can have within a :term:`Session`; a detached object
            is an object that has a database identity (i.e. a primary key)
            but is not associated with any session.  An object that
            was previously :term:`persistent` and was removed from its
            session either because it was expunged, or the owning
            session was closed, moves into the detached state.
            The detached state is generally used when objects are being
            moved between sessions or when being moved to/from an external
            object cache.

            .. seealso::

                :ref:`session_object_states`

    attached
    随附的
        .. tab:: 中文

            表示当前与特定 :term:`Session` 关联的 ORM 对象。

            .. seealso::

                :ref:`session_object_states`

        .. tab:: 英文

            Indicates an ORM object that is presently associated with a specific
            :term:`Session`.

            .. seealso::

                :ref:`session_object_states`
