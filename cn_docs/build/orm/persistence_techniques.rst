=================================
其他的持久化技术
=================================

Additional Persistence Techniques

.. _flush_embedded_sql_expressions:

将 SQL 插入/更新表达式嵌入到刷新中
====================================================

Embedding SQL Insert/Update Expressions into a Flush

.. tab:: 中文

    此功能允许数据库列的值被设置为 SQL 表达式，而不是字面量值。它对于原子更新、调用存储过程等特别有用。您只需将表达式赋值给属性::

        class SomeClass(Base):
            __tablename__ = "some_table"

            # ...

            value = mapped_column(Integer)

        someobject = session.get(SomeClass, 5)

        # 将 'value' 属性设置为增加 1 的 SQL 表达式
        someobject.value = SomeClass.value + 1

        # 发出 "UPDATE some_table SET value=value+1"
        session.commit()

    该技术适用于 INSERT 和 UPDATE 语句。执行 flush/commit 操作后，上述 `someobject` 上的 ``value`` 属性会被过期，
    因此在下次访问时，新的值会从数据库中加载。

    此功能还具有条件支持，可以与主键列一起使用。对于支持 RETURNING 的数据库（包括 Oracle 数据库、SQL Server、MariaDB 10.5、SQLite 3.35），
    也可以将 SQL 表达式赋值给主键列。这不仅可以评估 SQL 表达式，还允许成功通过 ORM 获取由服务器端触发器修改主键值的情况::

        class Foo(Base):
            __tablename__ = "foo"
            pk = mapped_column(Integer, primary_key=True)
            bar = mapped_column(Integer)

        e = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        Base.metadata.create_all(e)

        session = Session(e)

        foo = Foo(pk=sql.select(sql.func.coalesce(sql.func.max(Foo.pk) + 1, 1)))
        session.add(foo)
        session.commit()

    在 PostgreSQL 上，上述 :class:`.Session` 将发出以下 INSERT：

    .. sourcecode:: sql

        INSERT INTO foo (foopk, bar) VALUES
        ((SELECT coalesce(max(foo.foopk) + %(max_1)s, %(coalesce_2)s) AS coalesce_1
        FROM foo), %(bar)s) RETURNING foo.foopk

.. tab:: 英文

    This feature allows the value of a database column to be set to a SQL
    expression instead of a literal value. It's especially useful for atomic
    updates, calling stored procedures, etc. All you do is assign an expression to
    an attribute::

        class SomeClass(Base):
            __tablename__ = "some_table"

            # ...

            value = mapped_column(Integer)


        someobject = session.get(SomeClass, 5)

        # set 'value' attribute to a SQL expression adding one
        someobject.value = SomeClass.value + 1

        # issues "UPDATE some_table SET value=value+1"
        session.commit()

    This technique works both for INSERT and UPDATE statements. After the
    flush/commit operation, the ``value`` attribute on ``someobject`` above is
    expired, so that when next accessed the newly generated value will be loaded
    from the database.

    The feature also has conditional support to work in conjunction with
    primary key columns.  For backends that have RETURNING support
    (including Oracle Database, SQL Server, MariaDB 10.5, SQLite 3.35) a
    SQL expression may be assigned to a primary key column as well.  This allows
    both the SQL expression to be evaluated, as well as allows any server side
    triggers that modify the primary key value on INSERT, to be successfully
    retrieved by the ORM as part of the object's primary key::


        class Foo(Base):
            __tablename__ = "foo"
            pk = mapped_column(Integer, primary_key=True)
            bar = mapped_column(Integer)


        e = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        Base.metadata.create_all(e)

        session = Session(e)

        foo = Foo(pk=sql.select(sql.func.coalesce(sql.func.max(Foo.pk) + 1, 1)))
        session.add(foo)
        session.commit()

    On PostgreSQL, the above :class:`.Session` will emit the following INSERT:

    .. sourcecode:: sql

        INSERT INTO foo (foopk, bar) VALUES
        ((SELECT coalesce(max(foo.foopk) + %(max_1)s, %(coalesce_2)s) AS coalesce_1
        FROM foo), %(bar)s) RETURNING foo.foopk

.. _session_sql_expressions:

将 SQL 表达式与会话结合使用
===================================

Using SQL Expressions with Sessions

.. tab:: 中文

    SQL 表达式和字符串可以通过 :class:`~sqlalchemy.orm.session.Session` 在其事务上下文中执行。  
    最简单的方法是使用 :meth:`~.Session.execute` 方法，它返回一个 :class:`~sqlalchemy.engine.CursorResult`，  
    与 :class:`~sqlalchemy.engine.Engine` 或 :class:`~sqlalchemy.engine.Connection` 返回的结果相同::

        Session = sessionmaker(bind=engine)
        session = Session()

        # 执行字符串语句
        result = session.execute(text("select * from table where id=:id"), {"id": 7})

        # 执行 SQL 表达式构造
        result = session.execute(select(mytable).where(mytable.c.id == 7))

    当前 :class:`~sqlalchemy.engine.Connection` 可通过 :meth:`~.Session.connection` 方法访问：

        connection = session.connection()

    上述示例涉及一个绑定到单个 :class:`_engine.Engine` 或 :class:`_engine.Connection` 的 :class:`_orm.Session`。
    要使用一个绑定到多个引擎或没有引擎的 :class:`_orm.Session`（即依赖绑定的元数据），  
    :meth:`_orm.Session.execute` 和 :meth:`_orm.Session.connection` 方法接受一个绑定参数字典 :paramref:`_orm.Session.execute.bind_arguments`，
    该字典可以包含 "mapper"，其值是一个映射类或 :class:`_orm.Mapper` 实例，用于定位所需引擎的上下文::

        Session = sessionmaker()
        session = Session()

        # 执行时需要指定 mapper 或类
        result = session.execute(
            text("select * from table where id=:id"),
            {"id": 7},
            bind_arguments={"mapper": MyMappedClass},
        )

        result = session.execute(
            select(mytable).where(mytable.c.id == 7), bind_arguments={"mapper": MyMappedClass}
        )

        connection = session.connection(MyMappedClass)

    .. versionchanged:: 1.4 
        
        ``mapper`` 和 ``clause`` 参数现在作为字典的一部分传递给 :meth:`_orm.Session.execute`，  
        这个字典被作为 :paramref:`_orm.Session.execute.bind_arguments` 参数传递。  
        以前的参数仍然被接受，但此用法已被弃用。


.. tab:: 英文

    SQL expressions and strings can be executed via the
    :class:`~sqlalchemy.orm.session.Session` within its transactional context.
    This is most easily accomplished using the
    :meth:`~.Session.execute` method, which returns a
    :class:`~sqlalchemy.engine.CursorResult` in the same manner as an
    :class:`~sqlalchemy.engine.Engine` or
    :class:`~sqlalchemy.engine.Connection`::

        Session = sessionmaker(bind=engine)
        session = Session()

        # execute a string statement
        result = session.execute(text("select * from table where id=:id"), {"id": 7})

        # execute a SQL expression construct
        result = session.execute(select(mytable).where(mytable.c.id == 7))

    The current :class:`~sqlalchemy.engine.Connection` held by the
    :class:`~sqlalchemy.orm.session.Session` is accessible using the
    :meth:`~.Session.connection` method::

        connection = session.connection()

    The examples above deal with a :class:`_orm.Session` that's
    bound to a single :class:`_engine.Engine` or
    :class:`_engine.Connection`. To execute statements using a
    :class:`_orm.Session` which is bound either to multiple
    engines, or none at all (i.e. relies upon bound metadata), both
    :meth:`_orm.Session.execute` and
    :meth:`_orm.Session.connection` accept a dictionary of bind arguments
    :paramref:`_orm.Session.execute.bind_arguments` which may include "mapper"
    which is passed a mapped class or
    :class:`_orm.Mapper` instance, which is used to locate the
    proper context for the desired engine::

        Session = sessionmaker()
        session = Session()

        # need to specify mapper or class when executing
        result = session.execute(
            text("select * from table where id=:id"),
            {"id": 7},
            bind_arguments={"mapper": MyMappedClass},
        )

        result = session.execute(
            select(mytable).where(mytable.c.id == 7), bind_arguments={"mapper": MyMappedClass}
        )

        connection = session.connection(MyMappedClass)

    .. versionchanged:: 1.4 
        
        the ``mapper`` and ``clause`` arguments to :meth:`_orm.Session.execute` are now passed as part of a dictionary sent as the :paramref:`_orm.Session.execute.bind_arguments` parameter. The previous arguments are still accepted however this usage is deprecated.

.. _session_forcing_null:

在具有默认值的列上强制为 NULL
=======================================

Forcing NULL on a column with a default

.. tab:: 中文

    ORM 将任何从未设置的属性视为“默认”情况；该属性将被省略在 INSERT 语句中::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True)

        obj = MyObject(id=1)
        session.add(obj)
        session.commit()  # INSERT 时省略 'data' 列；数据库
        # 会将其持久化为 NULL 值

    省略列的 INSERT 意味着该列将被设置为 NULL 值， *除非* 该列已设置默认值，  
    在这种情况下，默认值将被持久化。无论是纯 SQL 角度（服务器端默认值），  
    还是 SQLAlchemy 的插入行为（包括客户端和服务器端默认值）都遵循此行为::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True, server_default="default")

        obj = MyObject(id=1)
        session.add(obj)
        session.commit()  # INSERT 时省略 'data' 列；数据库
        # 会将其持久化为 'default' 值

    然而，在 ORM 中，即使显式地将 Python 值 `None` 赋值给对象，这也会被视为 **与未赋值相同**::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True, server_default="default")

        obj = MyObject(id=1, data=None)
        session.add(obj)
        session.commit()  # INSERT 时将 'data' 列显式设置为 None；
        # ORM 仍然将其从语句中省略，数据库仍会将其持久化为 'default'

    上述操作将把 `data` 列持久化为服务器默认值 `"default"`，而不是 SQL NULL，  
    即使传递了 `None`；这是 ORM 的长期行为，许多应用程序都将其作为假设。

    那么，如果我们实际上想要将 NULL 存入该列，即使该列有默认值怎么办？  
    有两种方法。第一种是在每个实例级别，使用 :obj:`_expression.null` SQL 构造赋值给属性::

        from sqlalchemy import null

        obj = MyObject(id=1, data=null())
        session.add(obj)
        session.commit()  # INSERT 时将 'data' 列显式设置为 null；
        # ORM 直接使用此值，绕过所有客户端和服务器端的默认值，
        # 数据库将其持久化为 NULL 值

    :obj:`_expression.null` SQL 构造总是会直接将 SQL NULL 值插入目标 INSERT 语句中。

    如果我们希望能够使用 Python 值 `None`，并且希望它尽管列有默认值时也能持久化为 NULL，  
    我们可以使用 Core 层修饰符 :meth:`.TypeEngine.evaluates_none` 来为 ORM 配置此行为，  
    该修饰符指示 ORM 应将 `None` 视为与其他任何值相同并传递它，而不是将其视为“缺失”值并省略::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(
                String(50).evaluates_none(),  # 指示 None 始终传递
                nullable=True,
                server_default="default",
            )

        obj = MyObject(id=1, data=None)
        session.add(obj)
        session.commit()  # INSERT 时将 'data' 列显式设置为 None；
        # ORM 直接使用此值，绕过所有客户端和服务器端的默认值，
        # 数据库将其持久化为 NULL 值

    .. topic:: Evaluating None

        :meth:`.TypeEngine.evaluates_none` 修饰符主要用于指示类型，  
        其中 Python 值 "None" 有特殊意义，最典型的例子是 JSON 类型，  
        它可能希望将 JSON 中的 `null` 值持久化，而不是 SQL NULL。  
        在这里，我们稍微重用了这个修饰符，用于指示 ORM 在遇到 `None` 时传递它，  
        即使没有为其分配特殊的类型级行为。


.. tab:: 英文

    The ORM considers any attribute that was never set on an object as a
    "default" case; the attribute will be omitted from the INSERT statement::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True)


        obj = MyObject(id=1)
        session.add(obj)
        session.commit()  # INSERT with the 'data' column omitted; the database
        # itself will persist this as the NULL value

    Omitting a column from the INSERT means that the column will
    have the NULL value set, *unless* the column has a default set up,
    in which case the default value will be persisted.   This holds true
    both from a pure SQL perspective with server-side defaults, as well as the
    behavior of SQLAlchemy's insert behavior with both client-side and server-side
    defaults::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True, server_default="default")


        obj = MyObject(id=1)
        session.add(obj)
        session.commit()  # INSERT with the 'data' column omitted; the database
        # itself will persist this as the value 'default'

    However, in the ORM, even if one assigns the Python value ``None`` explicitly
    to the object, this is treated the **same** as though the value were never
    assigned::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String(50), nullable=True, server_default="default")


        obj = MyObject(id=1, data=None)
        session.add(obj)
        session.commit()  # INSERT with the 'data' column explicitly set to None;
        # the ORM still omits it from the statement and the
        # database will still persist this as the value 'default'

    The above operation will persist into the ``data`` column the
    server default value of ``"default"`` and not SQL NULL, even though ``None``
    was passed; this is a long-standing behavior of the ORM that many applications
    hold as an assumption.

    So what if we want to actually put NULL into this column, even though the
    column has a default value?  There are two approaches.  One is that
    on a per-instance level, we assign the attribute using the
    :obj:`_expression.null` SQL construct::

        from sqlalchemy import null

        obj = MyObject(id=1, data=null())
        session.add(obj)
        session.commit()  # INSERT with the 'data' column explicitly set as null();
        # the ORM uses this directly, bypassing all client-
        # and server-side defaults, and the database will
        # persist this as the NULL value

    The :obj:`_expression.null` SQL construct always translates into the SQL
    NULL value being directly present in the target INSERT statement.

    If we'd like to be able to use the Python value ``None`` and have this
    also be persisted as NULL despite the presence of column defaults,
    we can configure this for the ORM using a Core-level modifier
    :meth:`.TypeEngine.evaluates_none`, which indicates
    a type where the ORM should treat the value ``None`` the same as any other
    value and pass it through, rather than omitting it as a "missing" value::

        class MyObject(Base):
            __tablename__ = "my_table"
            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(
                String(50).evaluates_none(),  # indicate that None should always be passed
                nullable=True,
                server_default="default",
            )


        obj = MyObject(id=1, data=None)
        session.add(obj)
        session.commit()  # INSERT with the 'data' column explicitly set to None;
        # the ORM uses this directly, bypassing all client-
        # and server-side defaults, and the database will
        # persist this as the NULL value

    .. topic:: Evaluating None

        The :meth:`.TypeEngine.evaluates_none` modifier is primarily intended to
        signal a type where the Python value "None" is significant, the primary
        example being a JSON type which may want to persist the JSON ``null`` value
        rather than SQL NULL.  We are slightly repurposing it here in order to
        signal to the ORM that we'd like ``None`` to be passed into the type whenever
        present, even though no special type-level behaviors are assigned to it.

.. _orm_server_defaults:

获取服务器生成的默认值
===================================

Fetching Server-Generated Defaults

.. tab:: 中文

    正如在 :ref:`server_defaults` 和 :ref:`triggered_columns` 部分中介绍的那样，  
    Core 支持数据库列的概念，其中数据库本身在 INSERT 语句执行时生成一个值，  
    在某些较少见的情况下，甚至在 UPDATE 语句时生成该值。  
    ORM 对这些列也提供支持，能够在刷新时获取这些新生成的值。  
    对于由服务器生成的主键列，这是必需的，因为 ORM 必须在对象持久化后获取其主键值。

    在绝大多数情况下，数据库自动生成值的主键列是简单的整数列，这些列通常由数据库作为“自动递增”列，  
    或者通过与该列关联的序列来实现。SQLAlchemy Core 中的每个数据库方言都支持一种检索这些主键值的方法，  
    这种方法通常是 Python DBAPI 原生支持的，通常这个过程是自动进行的。  
    有关此更多的文档，请参见 :paramref:`_schema.Column.autoincrement`。

    对于那些不是主键列或不是简单的自动递增整数列的服务器生成列，  
    ORM 要求这些列被标记为适当的 ``server_default`` 指令，以便 ORM 能够检索这些值。  
    然而，并非所有方法都在所有后端上都支持，因此必须小心使用适当的方法。  
    需要回答的两个问题是：1. 该列是否是主键的一部分？2. 数据库是否支持 RETURNING 或等效的语句，比如“OUTPUT inserted”？  
    这些 SQL 语句会在执行 INSERT 或 UPDATE 语句时返回服务器生成的值。  
    RETURNING 目前由 PostgreSQL、Oracle 数据库、MariaDB 10.5、SQLite 3.35 和 SQL Server 支持。

.. tab:: 英文

    As introduced in the sections :ref:`server_defaults` and :ref:`triggered_columns`,
    the Core supports the notion of database columns for which the database
    itself generates a value upon INSERT and in less common cases upon UPDATE
    statements.  The ORM features support for such columns regarding being
    able to fetch these newly generated values upon flush.   This behavior is
    required in the case of primary key columns that are generated by the server,
    since the ORM has to know the primary key of an object once it is persisted.

    In the vast majority of cases, primary key columns that have their value
    generated automatically by the database are  simple integer columns, which are
    implemented by the database as either a so-called "autoincrement" column, or
    from a sequence associated with the column.   Every database dialect within
    SQLAlchemy Core supports a method of retrieving these primary key values which
    is often native to the Python DBAPI, and in general this process is automatic.
    There is more documentation regarding this at
    :paramref:`_schema.Column.autoincrement`.

    For server-generating columns that are not primary key columns or that are not
    simple autoincrementing integer columns, the ORM requires that these columns
    are marked with an appropriate ``server_default`` directive that allows the ORM to
    retrieve this value.   Not all methods are supported on all backends, however,
    so care must be taken to use the appropriate method. The two questions to be
    answered are, 1. is this column part of the primary key or not, and 2. does the
    database support RETURNING or an equivalent, such as "OUTPUT inserted"; these
    are SQL phrases which return a server-generated value at the same time as the
    INSERT or UPDATE statement is invoked.   RETURNING is currently supported
    by PostgreSQL, Oracle Database, MariaDB 10.5, SQLite 3.35, and SQL Server.

情况 1：支持非主键、RETURNING 或等效项
-------------------------------------------------------------

Case 1: non primary key, RETURNING or equivalent is supported

.. tab:: 中文

    在这种情况下，列应该标记为 :class:`.FetchedValue` 或者显式使用 :paramref:`_schema.Column.server_default`。  
    当执行 INSERT 语句时，如果 :paramref:`_orm.Mapper.eager_defaults` 参数设置为 ``True``，或者默认设置为 ``"auto"``，  
    则 ORM 会自动将这些列添加到 RETURNING 子句中，这样它们可以立即获取。对于支持 RETURNING 和 :ref:`insertmanyvalues <engine_insertmanyvalues>` 的方言::

        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)

            # 服务器端 SQL 日期函数生成新的时间戳
            timestamp = mapped_column(DateTime(), server_default=func.now())

            # 其他服务器端函数（如触发器）在 INSERT 时将值填充到此列
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

            # 设置 eager_defaults 为 True。通常这是可选的，因为如果后端支持 RETURNING 和 insertmanyvalues，
            # 则在 INSERT 时无论如何都会执行 eager defaults
            __mapper_args__ = {"eager_defaults": True}

    在上述示例中，如果 INSERT 语句没有显式指定客户端端的 "timestamp" 或 "special_identifier" 列的值，  
    那么 INSERT 语句会将 "timestamp" 和 "special_identifier" 列包含在 RETURNING 子句中，这样它们会立即获取。  
    在 PostgreSQL 数据库中，以上表的 INSERT 语句如下所示：

    .. sourcecode:: sql

        INSERT INTO my_table DEFAULT VALUES RETURNING my_table.id, my_table.timestamp, my_table.special_identifier

    .. versionchanged:: 2.0.0rc1 
        
        :paramref:`_orm.Mapper.eager_defaults` 参数现在默认设置为新的 ``"auto"``，  
        如果后端数据库同时支持 RETURNING 和 :ref:`insertmanyvalues <engine_insertmanyvalues>`，  
        它将自动使用 RETURNING 来获取服务器生成的默认值。

    .. note:: 
        
        :paramref:`_orm.Mapper.eager_defaults` 的 ``"auto"`` 值仅适用于 INSERT 语句。  
        即使 UPDATE 语句支持 RETURNING，更新语句也不会使用 RETURNING，除非 :paramref:`_orm.Mapper.eager_defaults` 设置为 ``True``。  
        这是因为 UPDATE 语句没有等效的 "insertmanyvalues" 功能，因此 UPDATE RETURNING 将要求每个更新的行分别发出 UPDATE 语句。


.. tab:: 英文

    In this case, columns should be marked as :class:`.FetchedValue` or with an
    explicit :paramref:`_schema.Column.server_default`.   The ORM will
    automatically add these columns to the RETURNING clause when performing
    INSERT statements, assuming the
    :paramref:`_orm.Mapper.eager_defaults` parameter is set to ``True``, or
    if left at its default setting of ``"auto"``, for dialects that support
    both RETURNING as well as :ref:`insertmanyvalues <engine_insertmanyvalues>`::


        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)

            # server-side SQL date function generates a new timestamp
            timestamp = mapped_column(DateTime(), server_default=func.now())

            # some other server-side function not named here, such as a trigger,
            # populates a value into this column during INSERT
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

            # set eager defaults to True.  This is usually optional, as if the
            # backend supports RETURNING + insertmanyvalues, eager defaults
            # will take place regardless on INSERT
            __mapper_args__ = {"eager_defaults": True}

    Above, an INSERT statement that does not specify explicit values for
    "timestamp" or "special_identifier" from the client side will include the
    "timestamp" and "special_identifier" columns within the RETURNING clause so
    they are available immediately. On the PostgreSQL database, an INSERT for the
    above table will look like:

    .. sourcecode:: sql

        INSERT INTO my_table DEFAULT VALUES RETURNING my_table.id, my_table.timestamp, my_table.special_identifier

    .. versionchanged:: 2.0.0rc1 
        
        The :paramref:`_orm.Mapper.eager_defaults` parameter now defaults to a new setting ``"auto"``, which will automatically make use of RETURNING to fetch server-generated default values on INSERT if the backing database supports both RETURNING as well as :ref:`insertmanyvalues <engine_insertmanyvalues>`.

    .. note:: 
        
        The ``"auto"`` value for :paramref:`_orm.Mapper.eager_defaults` only applies to INSERT statements.  UPDATE statements will not use RETURNING, even if available, unless :paramref:`_orm.Mapper.eager_defaults` is set to ``True``.  This is because there is no equivalent "insertmanyvalues" feature for UPDATE, so UPDATE RETURNING will require that UPDATE statements are emitted individually for each row being UPDATEd.

情况 2：表包含与 RETURNING 不兼容的触发器生成的值
----------------------------------------------------------------------------------------

Case 2: Table includes trigger-generated values which are not compatible with RETURNING

.. tab:: 中文

    ``"auto"`` 设置的 :paramref:`_orm.Mapper.eager_defaults` 表示，支持 RETURNING 的后端通常会在 INSERT 语句中使用 RETURNING 来检索新生成的默认值。
    然而，对于使用触发器生成的服务器端值，有一些限制，导致无法使用 RETURNING：

    * SQL Server 不允许在 INSERT 语句中使用 RETURNING 来检索触发器生成的值；该语句会失败。

    * SQLite 在将 RETURNING 与触发器结合使用时存在一些限制，因此 RETURNING 子句无法获取插入的值。

    * 其他后端在与触发器或其他类型的服务器生成值一起使用 RETURNING 时可能存在限制。

    要禁用对于此类值（不仅仅是服务器生成的默认值）使用 RETURNING，并确保 ORM 永远不会使用 RETURNING 进行某个表的操作，可以在映射的 :class:`.Table` 中指定 :paramref:`_schema.Table.implicit_returning` 为 ``False``。  
    使用声明式映射时，这看起来像这样::

        class MyModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

            # 假设一个数据库触发器在 INSERT 时填充这个列
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

            # 禁用该表所有使用 RETURNING 的行为
            __table_args__ = {"implicit_returning": False}

    在使用 pyodbc 驱动程序的 SQL Server 上，上述表的 INSERT 语句将不会使用 RETURNING，而是使用 SQL Server 的 ``scope_identity()`` 函数来检索新生成的主键值：

    .. sourcecode:: sql

        INSERT INTO my_table (data) VALUES (?); select scope_identity()

    .. seealso::

        :ref:`mssql_insert_behavior` - 有关 SQL Server 方言方法获取新生成主键值的背景知识


.. tab:: 英文

    The ``"auto"`` setting of :paramref:`_orm.Mapper.eager_defaults` means that
    a backend that supports RETURNING will usually make use of RETURNING with
    INSERT statements in order to retrieve newly generated default values.
    However there are limitations of server-generated values that are generated
    using triggers, such that RETURNING can't be used:

    * SQL Server does not allow RETURNING to be used in an INSERT statement to retrieve a trigger-generated value; the statement will fail.

    * SQLite has limitations in combining the use of RETURNING with triggers, such that the RETURNING clause will not have the INSERTed value available

    * Other backends may have limitations with RETURNING in conjunction with triggers, or other kinds of server-generated values.

    To disable the use of RETURNING for such values, including not just for
    server generated default values but also to ensure that the ORM will never
    use RETURNING with a particular table, specify
    :paramref:`_schema.Table.implicit_returning`
    as ``False`` for the mapped :class:`.Table`.  Using a Declarative mapping
    this looks like::

        class MyModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

            # assume a database trigger populates a value into this column
            # during INSERT
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

            # disable all use of RETURNING for the table
            __table_args__ = {"implicit_returning": False}

    On SQL Server with the pyodbc driver, an INSERT for the above table will
    not use RETURNING and will use the SQL Server ``scope_identity()`` function
    to retrieve the newly generated primary key value:

    .. sourcecode:: sql

        INSERT INTO my_table (data) VALUES (?); select scope_identity()

    .. seealso::

        :ref:`mssql_insert_behavior` - background on the SQL Server dialect's
        methods of fetching newly generated primary key values

情况 3：不支持或不需要非主键、RETURNING 或等效项
--------------------------------------------------------------------------------

Case 3: non primary key, RETURNING or equivalent is not supported or not needed

.. tab:: 中文

    这是与上述第 1 种情况相同的情况，唯一的区别是通常我们不希望使用 :paramref:`.orm.Mapper.eager_defaults`，  
    因为当前实现中，在没有 RETURNING 支持的情况下，它会为每行发出一个 SELECT，这样的做法性能较差。  
    因此，以下映射中省略了该参数::

        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            timestamp = mapped_column(DateTime(), server_default=func.now())

            # 假设数据库触发器在 INSERT 时填充这个列
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

    在没有 RETURNING 或 "insertmanyvalues" 支持的后端上插入上述映射的记录后，  
    "timestamp" 和 "special_identifier" 列将保持为空，并且将在首次访问它们时通过第二个 SELECT 语句进行获取，也就是说，它们会被标记为“过期”。

    如果显式为 :paramref:`.orm.Mapper.eager_defaults` 提供了 ``True`` 的值，并且后端数据库不支持 RETURNING 或等效功能，  
    则 ORM 将在 INSERT 语句后立即发出一个 SELECT 语句来获取新生成的值；  
    当前，ORM 还不能批量选择许多新插入的行，如果没有 RETURNING 的支持，这个操作通常是不可取的，因为它会为刷新过程添加额外的 SELECT 语句。  
    在 MySQL（而不是 MariaDB）上使用上述映射并将 :paramref:`.orm.Mapper.eager_defaults` 标记为 True 时，刷新时会生成如下 SQL：

    .. sourcecode:: sql

        INSERT INTO my_table () VALUES ()

        -- 使用 eager_defaults **时**，但不支持 RETURNING
        SELECT my_table.timestamp AS my_table_timestamp, my_table.special_identifier AS my_table_special_identifier
        FROM my_table WHERE my_table.id = %s

    SQLAlchemy 在未来的版本中可能会改进在没有 RETURNING 支持的情况下的 eager defaults 性能，  
    使其能够批量选择许多行并在一个 SELECT 语句中处理。

.. tab:: 英文

    This case is the same as case 1 above, except we typically don't want to
    use :paramref:`.orm.Mapper.eager_defaults`, as its current implementation
    in the absence of RETURNING support is to emit a SELECT-per-row, which
    is not performant.  Therefore the parameter is omitted in the mapping below::

        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            timestamp = mapped_column(DateTime(), server_default=func.now())

            # assume a database trigger populates a value into this column
            # during INSERT
            special_identifier = mapped_column(String(50), server_default=FetchedValue())

    After a record with the above mapping is INSERTed on a backend that does not
    include RETURNING or "insertmanyvalues" support, the "timestamp" and
    "special_identifier" columns will remain empty, and will be fetched via a
    second SELECT statement when they are first accessed after the flush, e.g. they
    are marked as "expired".

    If the :paramref:`.orm.Mapper.eager_defaults` is explicitly provided with a
    value of ``True``, and the backend database does not support RETURNING or an
    equivalent, the ORM will emit a SELECT statement immediately following the
    INSERT statement in order to fetch newly generated values; the ORM does not
    currently have the ability to SELECT many newly inserted rows in batch if
    RETURNING was not available. This is usually undesirable as it adds additional
    SELECT statements to the flush process that may not be needed. Using the above
    mapping with the :paramref:`.orm.Mapper.eager_defaults` flag set to True
    against MySQL (not MariaDB) results in SQL like this upon flush:

    .. sourcecode:: sql

        INSERT INTO my_table () VALUES ()

        -- when eager_defaults **is** used, but RETURNING is not supported
        SELECT my_table.timestamp AS my_table_timestamp, my_table.special_identifier AS my_table_special_identifier
        FROM my_table WHERE my_table.id = %s

    A future release of SQLAlchemy may seek to improve the efficiency of
    eager defaults in the abcense of RETURNING to batch many rows within a
    single SELECT statement.

情况 4：支持主键、RETURNING 或等效项
----------------------------------------------------------

Case 4: primary key, RETURNING or equivalent is supported

.. tab:: 中文

    具有服务器生成值的主键列必须在 INSERT 时立即获取；ORM 只能访问具有主键值的行，因此，如果主键是由服务器生成的，ORM 需要一种方法在 INSERT 后立即检索该新值。

    如前所述，对于整数的“自增”列，以及标记为 :class:`.Identity` 和类似 PostgreSQL SERIAL 的特殊构造，这些类型会被 Core 自动处理；如果不支持 RETURNING，数据库会包括获取“最后插入的 ID”的函数，而如果支持 RETURNING，SQLAlchemy 将使用它。

    例如，使用 Oracle 数据库并标记为 :class:`.Identity` 的列，RETURNING 会自动用于获取新的主键值::

        class MyOracleModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(Identity(), primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

    上面模型在 Oracle 数据库上的 INSERT 语句如下：

    .. sourcecode:: sql

        INSERT INTO my_table (data) VALUES (:data) RETURNING my_table.id INTO :ret_0

    SQLAlchemy 为 "data" 字段渲染了一个 INSERT 语句，但仅在 RETURNING 子句中包括 "id"，  
    这样就可以让服务器端生成 "id" 并立即返回新值。

    对于由服务器端函数或触发器生成的非整数值，以及来自表格外部构造的整数值（包括显式序列和触发器），  
    必须在表的元数据中标明服务器默认生成。再次以 Oracle 数据库为例，我们可以使用 :class:`.Sequence` 构造来为显式序列命名，如下所示::

        class MyOracleModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(Sequence("my_oracle_seq"), primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

    这个版本模型在 Oracle 数据库上的 INSERT 语句如下：

    .. sourcecode:: sql

        INSERT INTO my_table (id, data) VALUES (my_oracle_seq.nextval, :data) RETURNING my_table.id INTO :ret_0

    上面，SQLAlchemy 为主键列渲染了 ``my_oracle_seq.nextval``，  
    这样它就会用于新的主键生成，并且还使用 RETURNING 立即获取新值。

    如果数据来源不是简单的 SQL 函数或 :class:`.Sequence`，例如使用触发器或数据库特定的数据类型生成新值，  
    则可以通过在列定义中使用 :class:`.FetchedValue` 来指示值生成的默认值。下面是一个使用 SQL Server TIMESTAMP 列作为主键的模型示例；  
    在 SQL Server 中，该数据类型会自动生成新值，因此在表的元数据中，使用 :class:`.FetchedValue` 来指示 :paramref:`.Column.server_default` 参数::

        class MySQLServerModel(Base):
            __tablename__ = "my_table"

            timestamp: Mapped[datetime.datetime] = mapped_column(
                TIMESTAMP(), server_default=FetchedValue(), primary_key=True
            )
            data: Mapped[str] = mapped_column(String(50))

    在 SQL Server 上插入上述表格时，SQL 语句如下：

    .. sourcecode:: sql

        INSERT INTO my_table (data) OUTPUT inserted.timestamp VALUES (?)


.. tab:: 英文

    A primary key column with a server-generated value must be fetched immediately
    upon INSERT; the ORM can only access rows for which it has a primary key value,
    so if the primary key is generated by the server, the ORM needs a way
    to retrieve that new value immediately upon INSERT.

    As mentioned above, for integer "autoincrement" columns, as well as
    columns marked with :class:`.Identity` and special constructs such as
    PostgreSQL SERIAL, these types are handled automatically by the Core; databases
    include functions for fetching the "last inserted id" where RETURNING
    is not supported, and where RETURNING is supported SQLAlchemy will use that.

    For example, using Oracle Database with a column marked as :class:`.Identity`,
    RETURNING is used automatically to fetch the new primary key value::

        class MyOracleModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(Identity(), primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

    The INSERT for a model as above on Oracle Database looks like:

    .. sourcecode:: sql

        INSERT INTO my_table (data) VALUES (:data) RETURNING my_table.id INTO :ret_0

    SQLAlchemy renders an INSERT for the "data" field, but only includes "id" in
    the RETURNING clause, so that server-side generation for "id" will take
    place and the new value will be returned immediately.

    For non-integer values generated by server side functions or triggers, as well
    as for integer values that come from constructs outside the table itself,
    including explicit sequences and triggers, the server default generation must
    be marked in the table metadata. Using Oracle Database as the example again, we can
    illustrate a similar table as above naming an explicit sequence using the
    :class:`.Sequence` construct::

        class MyOracleModel(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(Sequence("my_oracle_seq"), primary_key=True)
            data: Mapped[str] = mapped_column(String(50))

    An INSERT for this version of the model on Oracle Database would look like:

    .. sourcecode:: sql

        INSERT INTO my_table (id, data) VALUES (my_oracle_seq.nextval, :data) RETURNING my_table.id INTO :ret_0

    Where above, SQLAlchemy renders ``my_sequence.nextval`` for the primary key
    column so that it is used for new primary key generation, and also uses
    RETURNING to get the new value back immediately.

    If the source of data is not represented by a simple SQL function or
    :class:`.Sequence`, such as when using triggers or database-specific datatypes
    that produce new values, the presence of a value-generating default may be
    indicated by using :class:`.FetchedValue` within the column definition. Below
    is a model that uses a SQL Server TIMESTAMP column as the primary key; on SQL
    Server, this datatype generates new values automatically, so this is indicated
    in the table metadata by indicating :class:`.FetchedValue` for the
    :paramref:`.Column.server_default` parameter::

        class MySQLServerModel(Base):
            __tablename__ = "my_table"

            timestamp: Mapped[datetime.datetime] = mapped_column(
                TIMESTAMP(), server_default=FetchedValue(), primary_key=True
            )
            data: Mapped[str] = mapped_column(String(50))

    An INSERT for the above table on SQL Server looks like:

    .. sourcecode:: sql

        INSERT INTO my_table (data) OUTPUT inserted.timestamp VALUES (?)

情况 5：不支持主键、RETURNING 或等效项
--------------------------------------------------------------

Case 5: primary key, RETURNING or equivalent is not supported

.. tab:: 中文

    在这里，我们生成了适用于 MySQL 等数据库的行，这些数据库使用某种方式在服务器端生成默认值，但并非使用数据库的常规自增机制。  
    在这种情况下，我们必须确保 SQLAlchemy 可以“预执行”默认值，这意味着它必须是一个显式的 SQL 表达式。

    .. note:: 
        
        本节将展示多个涉及 MySQL 中 datetime 值的示例，因为该后端的 datetime 数据类型有额外的特殊要求，这些要求非常有用。然而，请记住，MySQL 要求为除常见的单列自增整数主键之外的任何自动生成的数据类型使用显式的“预执行”默认生成器。

.. tab:: 英文

    In this area we are generating rows for a database such as MySQL
    where some means of generating a default is occurring on the server, but is
    outside of the database's usual autoincrement routine. In this case, we have to
    make sure SQLAlchemy can "pre-execute" the default, which means it has to be an
    explicit SQL expression.

    .. note::  
        
        This section will illustrate multiple recipes involving datetime values for MySQL, since the datetime datatypes on this backend has additional idiosyncratic requirements that are useful to illustrate.  Keep in mind however that MySQL requires an explicit "pre-executed" default generator for *any* auto-generated datatype used as the primary key other than the usual single-column autoincrementing integer value.

带有 DateTime 主键的 MySQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MySQL with DateTime primary key

.. tab:: 中文

    以 MySQL 中的 :class:`.DateTime` 列为例，我们使用 "NOW()" SQL 函数添加一个显式的预执行支持的默认值::

        class MyModel(Base):
            __tablename__ = "my_table"

            timestamp = mapped_column(DateTime(), default=func.now(), primary_key=True)

    在上述代码中，我们选择了 "NOW()" 函数来为列提供一个 datetime 值。生成的 SQL 如下所示：

    .. sourcecode:: sql

        SELECT now() AS anon_1
        INSERT INTO my_table (timestamp) VALUES (%s)
        ('2018-08-09 13:08:46',)


.. tab:: 英文

    Using the example of a :class:`.DateTime` column for MySQL, we add an explicit
    pre-execute-supported default using the "NOW()" SQL function::

        class MyModel(Base):
            __tablename__ = "my_table"

            timestamp = mapped_column(DateTime(), default=func.now(), primary_key=True)

    Where above, we select the "NOW()" function to deliver a datetime value
    to the column.  The SQL generated by the above is:

    .. sourcecode:: sql

        SELECT now() AS anon_1
        INSERT INTO my_table (timestamp) VALUES (%s)
        ('2018-08-09 13:08:46',)

带有 TIMESTAMP 主键的 MySQL
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

MySQL with TIMESTAMP primary key

.. tab:: 中文

    当使用 :class:`_types.TIMESTAMP` 数据类型与 MySQL 时，MySQL 通常会自动为此数据类型关联一个服务器端默认值。  
    然而，当我们将其用作主键时，Core 无法检索新生成的值，除非我们自己执行该函数。  
    由于 :class:`_types.TIMESTAMP` 在 MySQL 中实际存储的是二进制值，因此我们需要在使用 "NOW()" 时添加额外的 "CAST" 语句，以便检索可以持久化到列中的二进制值::

        from sqlalchemy import cast, Binary


        class MyModel(Base):
            __tablename__ = "my_table"

            timestamp = mapped_column(
                TIMESTAMP(), default=cast(func.now(), Binary), primary_key=True
            )

    在上面的代码中，除了选择 "NOW()" 函数外，我们还使用了 :class:`.Binary` 数据类型，并结合 :func:`.cast`，  
    以便返回值为二进制形式。上述 INSERT 语句生成的 SQL 如下：

    .. sourcecode:: sql

        SELECT CAST(now() AS BINARY) AS anon_1
        INSERT INTO my_table (timestamp) VALUES (%s)
        (b'2018-08-09 13:08:46',)

    .. seealso::

        :ref:`metadata_defaults_toplevel`

.. tab:: 英文

    When using the :class:`_types.TIMESTAMP` datatype with MySQL, MySQL ordinarily
    associates a server-side default with this datatype automatically.  However
    when we use one as a primary key, the Core cannot retrieve the newly generated
    value unless we execute the function ourselves.  As :class:`_types.TIMESTAMP` on
    MySQL actually stores a binary value, we need to add an additional "CAST" to our
    usage of "NOW()" so that we retrieve a binary value that can be persisted
    into the column::

        from sqlalchemy import cast, Binary


        class MyModel(Base):
            __tablename__ = "my_table"

            timestamp = mapped_column(
                TIMESTAMP(), default=cast(func.now(), Binary), primary_key=True
            )

    Above, in addition to selecting the "NOW()" function, we additionally make
    use of the :class:`.Binary` datatype in conjunction with :func:`.cast` so that
    the returned value is binary.  SQL rendered from the above within an
    INSERT looks like:

    .. sourcecode:: sql

        SELECT CAST(now() AS BINARY) AS anon_1
        INSERT INTO my_table (timestamp) VALUES (%s)
        (b'2018-08-09 13:08:46',)

    .. seealso::

        :ref:`metadata_defaults_toplevel`

关于急切获取用于 INSERT 或 UPDATE 的客户端调用 SQL 表达式的说明
-----------------------------------------------------------------------------------

Notes on eagerly fetching client invoked SQL expressions used for INSERT or UPDATE

.. tab:: 中文

    前面的示例展示了如何使用 :paramref:`_schema.Column.server_default` 在 DDL 中创建包括默认生成函数的表。

    SQLAlchemy 还支持非 DDL 服务器端默认值，正如 :ref:`defaults_client_invoked_sql` 所述；这些“客户端调用的 SQL 表达式”  
    是通过 :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 参数来设置的。

    这些 SQL 表达式目前与真实的服务器端默认值在 ORM 中的使用存在相同的限制；当 :paramref:`_orm.Mapper.eager_defaults` 设置为  
    ``"auto"`` 或 ``True`` 时，它们不会通过 RETURNING 被提前获取，除非 :class:`.FetchedValue` 指令与 :class:`_schema.Column` 关联，  
    即使这些表达式不是 DDL 服务器默认值，而是由 SQLAlchemy 本身主动渲染的。这一限制可能会在未来的 SQLAlchemy 版本中得到解决。

    可以将 :class:`.FetchedValue` 构造应用于 :paramref:`_schema.Column.server_default` 或  
    :paramref:`_schema.Column.server_onupdate`，同时使用 :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 设置 SQL 表达式，  
    例如下面的示例中， ``func.now()`` 构造用于 :paramref:`_schema.Column.default` 和 :paramref:`_schema.Column.onupdate` 的客户端调用 SQL 表达式。  
    为了使 :paramref:`_orm.Mapper.eager_defaults` 行为包括在有 RETURNING 可用时获取这些值，  
    需要将 :paramref:`_schema.Column.server_default` 和 :paramref:`_schema.Column.server_onupdate` 与 :class:`.FetchedValue` 一起使用，以确保提取发生::

        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)

            created = mapped_column(
                DateTime(), default=func.now(), server_default=FetchedValue()
            )
            updated = mapped_column(
                DateTime(),
                onupdate=func.now(),
                server_default=FetchedValue(),
                server_onupdate=FetchedValue(),
            )

            __mapper_args__ = {"eager_defaults": True}

    对于上面的映射，ORM 渲染的 SQL 对于 INSERT 和 UPDATE 将在 RETURNING 子句中包含 ``created`` 和 ``updated``：

    .. sourcecode:: sql

        INSERT INTO my_table (created) VALUES (now()) RETURNING my_table.id, my_table.created, my_table.updated

        UPDATE my_table SET updated=now() WHERE my_table.id = %(my_table_id)s RETURNING my_table.updated


.. tab:: 英文

    The preceding examples indicate the use of :paramref:`_schema.Column.server_default`
    to create tables that include default-generation functions within their
    DDL.

    SQLAlchemy also supports non-DDL server side defaults, as documented at
    :ref:`defaults_client_invoked_sql`; these "client invoked SQL expressions"
    are set up using the :paramref:`_schema.Column.default` and
    :paramref:`_schema.Column.onupdate` parameters.

    These SQL expressions currently are subject to the same limitations within the
    ORM as occurs for true server-side defaults; they won't be eagerly fetched with
    RETURNING when :paramref:`_orm.Mapper.eager_defaults` is set to ``"auto"`` or
    ``True`` unless the :class:`.FetchedValue` directive is associated with the
    :class:`_schema.Column`, even though these expressions are not DDL server
    defaults and are actively rendered by SQLAlchemy itself. This limitation may be
    addressed in future SQLAlchemy releases.

    The :class:`.FetchedValue` construct can be applied to
    :paramref:`_schema.Column.server_default` or
    :paramref:`_schema.Column.server_onupdate` at the same time that a SQL
    expression is used with :paramref:`_schema.Column.default` and
    :paramref:`_schema.Column.onupdate`, such as in the example below where the
    ``func.now()`` construct is used as a client-invoked SQL expression
    for :paramref:`_schema.Column.default` and
    :paramref:`_schema.Column.onupdate`.  In order for the behavior of
    :paramref:`_orm.Mapper.eager_defaults` to include that it fetches these
    values using RETURNING when available, :paramref:`_schema.Column.server_default` and
    :paramref:`_schema.Column.server_onupdate` are used with :class:`.FetchedValue`
    to ensure that the fetch occurs::

        class MyModel(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)

            created = mapped_column(
                DateTime(), default=func.now(), server_default=FetchedValue()
            )
            updated = mapped_column(
                DateTime(),
                onupdate=func.now(),
                server_default=FetchedValue(),
                server_onupdate=FetchedValue(),
            )

            __mapper_args__ = {"eager_defaults": True}

    With a mapping similar to the above, the SQL rendered by the ORM for
    INSERT and UPDATE will include ``created`` and ``updated`` in the RETURNING
    clause:

    .. sourcecode:: sql

        INSERT INTO my_table (created) VALUES (now()) RETURNING my_table.id, my_table.created, my_table.updated

        UPDATE my_table SET updated=now() WHERE my_table.id = %(my_table_id)s RETURNING my_table.updated



.. _orm_dml_returning_objects:


使用 INSERT、UPDATE 和 ON CONFLICT（即 upsert）返回 ORM 对象
==========================================================================

Using INSERT, UPDATE and ON CONFLICT (i.e. upsert) to return ORM Objects

.. tab:: 中文

    SQLAlchemy 2.0 提供了增强的功能，可以发出多种类型的 ORM 启用的 INSERT、UPDATE 和 upsert 语句。  
    有关 upsert 的详细信息，请参阅 :ref:`orm_queryguide_upsert`。

.. tab:: 英文

    SQLAlchemy 2.0 includes enhanced capabilities for emitting several varieties of ORM-enabled INSERT, UPDATE, and upsert statements.  See the document at :doc:`queryguide/dml` for documentation.  For upsert, see :ref:`orm_queryguide_upsert`.

使用 PostgreSQL ON CONFLICT 和 RETURNING 返回更新的 ORM对象
---------------------------------------------------------------------------

Using PostgreSQL ON CONFLICT with RETURNING to return upserted ORM objects

.. tab:: 中文

    本节已移至 :ref:`orm_queryguide_upsert`。

.. tab:: 英文

    This section has moved to :ref:`orm_queryguide_upsert`.


.. _session_partitioning:

分区策略（例如每个会话有多个数据库后端）
=====================================================================

Partitioning Strategies (e.g. multiple database backends per Session)

.. tab:: 中文

.. tab:: 英文

简单垂直分区
----------------------------

Simple Vertical Partitioning

.. tab:: 中文

    垂直分区将不同的类、类层次结构或映射的表分配到多个数据库中，  
    通过使用 :class:`.Session` 配置 :paramref:`.Session.binds` 参数来实现。  
    该参数接收一个字典，其中包含 ORM 映射的类、映射层次结构中的任意类（例如声明性基类或混入类）、  
    :class:`_schema.Table` 对象和 :class:`_orm.Mapper` 对象作为键，这些键通常会引用 :class:`_engine.Engine` 或  
    较不常见的 :class:`_engine.Connection` 对象作为目标。  
    每当 :class:`.Session` 需要代表特定类型的映射类发出 SQL 时，该字典会被查询以定位适当的数据库连接源::

        engine1 = create_engine("postgresql+psycopg2://db1")
        engine2 = create_engine("postgresql+psycopg2://db2")

        Session = sessionmaker()

        # 将 User 操作绑定到 engine 1，将 Account 操作绑定到 engine 2
        Session.configure(binds={User: engine1, Account: engine2})

        session = Session()

    在上面的示例中，对任意类的 SQL 操作将使用与该类绑定的 :class:`_engine.Engine`。  
    这种功能涵盖了读取和写入操作；针对映射到 ``engine1`` 的实体的 :class:`_query.Query` （通过查看请求的项目列表中的第一个实体确定）  
    将使用 ``engine1`` 来运行查询。提交操作将针对每个类使用 **两个** 引擎，当它提交 ``User`` 和 ``Account`` 类型的对象时。

    在更常见的情况下，通常会使用基类或混入类来区分不同数据库连接的操作。  
    :paramref:`.Session.binds` 参数可以接受任何任意的 Python 类作为键，如果该类在特定映射类的 ``__mro__`` （Python 方法解析顺序）中找到，则会使用该类。  
    假设有两个声明性基类表示两个不同的数据库连接::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Session

        class BaseA(DeclarativeBase):
            pass

        class BaseB(DeclarativeBase):
            pass

        class User(BaseA): ...

        class Address(BaseA): ...

        class GameInfo(BaseB): ...

        class GameStats(BaseB): ...

        Session = sessionmaker()

        # 所有 User/Address 操作将使用 engine 1，所有 Game 操作将使用 engine 2
        Session.configure(binds={BaseA: engine1, BaseB: engine2})

    在上面的示例中，派生自 ``BaseA`` 和 ``BaseB`` 的类将根据它们的超类，  
    将其 SQL 操作路由到其中一个引擎。如果某个类同时继承多个“绑定”超类，则会选择目标类层次结构中位于最顶部的超类来决定使用哪个引擎。

    .. seealso::

        :paramref:`.Session.binds`


.. tab:: 英文

    Vertical partitioning places different classes, class hierarchies,
    or mapped tables, across multiple databases, by configuring the
    :class:`.Session` with the :paramref:`.Session.binds` argument. This
    argument receives a dictionary that contains any combination of
    ORM-mapped classes, arbitrary classes within a mapped hierarchy (such
    as declarative base classes or mixins), :class:`_schema.Table` objects,
    and :class:`_orm.Mapper` objects as keys, which then refer typically to
    :class:`_engine.Engine` or less typically :class:`_engine.Connection` objects as targets.
    The dictionary is consulted whenever the :class:`.Session` needs to
    emit SQL on behalf of a particular kind of mapped class in order to locate
    the appropriate source of database connectivity::

        engine1 = create_engine("postgresql+psycopg2://db1")
        engine2 = create_engine("postgresql+psycopg2://db2")

        Session = sessionmaker()

        # bind User operations to engine 1, Account operations to engine 2
        Session.configure(binds={User: engine1, Account: engine2})

        session = Session()

    Above, SQL operations against either class will make usage of the :class:`_engine.Engine`
    linked to that class.     The functionality is comprehensive across both
    read and write operations; a :class:`_query.Query` that is against entities
    mapped to ``engine1`` (determined by looking at the first entity in the
    list of items requested) will make use of ``engine1`` to run the query.   A
    flush operation will make use of **both** engines on a per-class basis as it
    flushes objects of type ``User`` and ``Account``.

    In the more common case, there are typically base or mixin classes that  can be
    used to distinguish between operations that are destined for different database
    connections.  The :paramref:`.Session.binds` argument can accommodate any
    arbitrary Python class as a key, which will be used if it is found to be in the
    ``__mro__`` (Python method resolution order) for a particular  mapped class.
    Supposing two declarative bases are representing two different database
    connections::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Session


        class BaseA(DeclarativeBase):
            pass


        class BaseB(DeclarativeBase):
            pass


        class User(BaseA): ...


        class Address(BaseA): ...


        class GameInfo(BaseB): ...


        class GameStats(BaseB): ...


        Session = sessionmaker()

        # all User/Address operations will be on engine 1, all
        # Game operations will be on engine 2
        Session.configure(binds={BaseA: engine1, BaseB: engine2})

    Above, classes which descend from ``BaseA`` and ``BaseB`` will have their
    SQL operations routed to one of two engines based on which superclass
    they descend from, if any.   In the case of a class that descends from more
    than one "bound" superclass, the superclass that is highest in the target
    class' hierarchy will be chosen to represent which engine should be used.

    .. seealso::

        :paramref:`.Session.binds`


多引擎会话的事务协调
----------------------------------------------------------

Coordination of Transactions for a multiple-engine Session

.. tab:: 中文

    使用多个绑定引擎时有一个注意事项，即在一个后端的提交操作成功后，另一个后端的提交操作可能会失败。  
    这是一个一致性问题，在关系型数据库中通常通过“二阶段事务”来解决，该事务在提交序列中增加了一个“准备”步骤，  
    允许多个数据库在实际完成事务之前同意提交。

    由于 DBAPI 的支持有限，SQLAlchemy 对跨后端的二阶段事务支持有限。  
    通常已知与 PostgreSQL 后端兼容得较好，与 MySQL 后端的兼容性较差。  
    然而，当后端支持时，:class:`.Session` 完全能够利用二阶段事务功能，方法是通过在 :class:`.sessionmaker` 或  
    :class:`.Session` 中设置 :paramref:`.Session.use_twophase` 标志。  
    有关示例，请参见 :ref:`session_twophase`。

.. tab:: 英文

    One caveat to using multiple bound engines is in the case where a commit
    operation may fail on one backend after the commit has succeeded on another.
    This is an inconsistency problem that in relational databases is solved
    using a "two phase transaction", which adds an additional "prepare" step
    to the commit sequence that allows for multiple databases to agree to commit
    before actually completing the transaction.

    Due to limited support within DBAPIs,  SQLAlchemy has limited support for two-
    phase transactions across backends.  Most typically, it is known to work well
    with the PostgreSQL backend and to  a lesser extent with the MySQL backend.
    However, the :class:`.Session` is fully capable of taking advantage of the two
    phase transaction feature when the backend supports it, by setting the
    :paramref:`.Session.use_twophase` flag within :class:`.sessionmaker` or
    :class:`.Session`.  See :ref:`session_twophase` for an example.


.. _session_custom_partitioning:

自定义垂直分区
----------------------------

Custom Vertical Partitioning

.. tab:: 中文

    通过覆盖 :meth:`.Session.get_bind` 方法，可以构建更全面的基于规则的类级分区。  
    下面我们展示了一个自定义的 :class:`.Session`，它实现了以下规则：

    1. Flush 操作，以及批量的 "update" 和 "delete" 操作，被交付到名为 ``leader`` 的引擎。

    2. 所有继承自 ``MyOtherClass`` 的对象操作，都将在 ``other`` 引擎上执行。

    3. 所有其他类的读操作，将随机选择 ``follower1`` 或 ``follower2`` 数据库。

    ::

        engines = {
            "leader": create_engine("sqlite:///leader.db"),
            "other": create_engine("sqlite:///other.db"),
            "follower1": create_engine("sqlite:///follower1.db"),
            "follower2": create_engine("sqlite:///follower2.db"),
        }

        from sqlalchemy.sql import Update, Delete
        from sqlalchemy.orm import Session, sessionmaker
        import random


        class RoutingSession(Session):
            def get_bind(self, mapper=None, clause=None):
                if mapper and issubclass(mapper.class_, MyOtherClass):
                    return engines["other"]
                elif self._flushing or isinstance(clause, (Update, Delete)):
                    # 注：这是为了示例，然而在实践中，读写分离通常会通过在
                    # 顶层使用两个不同的 Session 来实现。
                    # 请参阅下面的注释
                    return engines["leader"]
                else:
                    return engines[random.choice(["follower1", "follower2"])]

    上述 :class:`.Session` 类通过 ``class_`` 参数传递给 :class:`.sessionmaker` 使用::

        Session = sessionmaker(class_=RoutingSession)

    这种方法可以与多个 :class:`_schema.MetaData` 对象结合使用，  
    方法之一是使用声明性 ``__abstract__`` 关键字，详细说明见 :ref:`declarative_abstract`。

    .. note::

        上面的示例说明了如何根据 SQL 语句是否需要写入数据来路由到所谓的“leader”或“follower”数据库。  
        然而，这种方法可能不是一个实用的方式，因为它会导致读写操作之间的不协调事务行为。  
        在实践中，最好在开始时将 :class:`_orm.Session` 构建为“读取”或“写入”会话，  
        依据整体操作或事务的性质来决定。这样，写入数据的操作也会在同一事务范围内执行读取查询。  
        参见 :ref:`session_transaction_isolation_enginewide` 中的示例，  
        该示例设置了一个“只读”操作的 :class:`_orm.sessionmaker`，使用自动提交连接，  
        另一个则用于“写入”操作，其中将包含 DML / COMMIT。

    .. seealso::

        `Django风格的数据库路由器在SQLAlchemy中的实现 <https://techspot.zzzeek.org/2012/01/11/django-style-database-routers-in-sqlalchemy/>`_  
        - 一篇关于 :meth:`.Session.get_bind` 更全面示例的博客文章


.. tab:: 英文

    More comprehensive rule-based class-level partitioning can be built by
    overriding the :meth:`.Session.get_bind` method.   Below we illustrate
    a custom :class:`.Session` which delivers the following rules:

    1. Flush operations, as well as bulk "update" and "delete" operations, are delivered to the engine named ``leader``.

    2. Operations on objects that subclass ``MyOtherClass`` all occur on the ``other`` engine.

    3. Read operations for all other classes occur on a random choice of the ``follower1`` or ``follower2`` database.

    ::

        engines = {
            "leader": create_engine("sqlite:///leader.db"),
            "other": create_engine("sqlite:///other.db"),
            "follower1": create_engine("sqlite:///follower1.db"),
            "follower2": create_engine("sqlite:///follower2.db"),
        }

        from sqlalchemy.sql import Update, Delete
        from sqlalchemy.orm import Session, sessionmaker
        import random


        class RoutingSession(Session):
            def get_bind(self, mapper=None, clause=None):
                if mapper and issubclass(mapper.class_, MyOtherClass):
                    return engines["other"]
                elif self._flushing or isinstance(clause, (Update, Delete)):
                    # NOTE: this is for example, however in practice reader/writer
                    # splits are likely more straightforward by using two distinct
                    # Sessions at the top of a "reader" or "writer" operation.
                    # See note below
                    return engines["leader"]
                else:
                    return engines[random.choice(["follower1", "follower2"])]

    The above :class:`.Session` class is plugged in using the ``class_``
    argument to :class:`.sessionmaker`::

        Session = sessionmaker(class_=RoutingSession)

    This approach can be combined with multiple :class:`_schema.MetaData` objects,
    using an approach such as that of using the declarative ``__abstract__``
    keyword, described at :ref:`declarative_abstract`.

    .. note:: 
        
        While the above example illustrates routing of specific SQL statements to a so-called "leader" or "follower" database based on whether or not the statement expects to write data, this is likely not a practical approach, as it leads to uncoordinated transaction behavior between reading and writing within the same operation.  In practice, it's likely best to construct the :class:`_orm.Session` up front as a "reader" or "writer" session, based on the overall operation / transaction that's proceeding. That way, an operation that will be writing data will also emit its read-queries within the same transaction scope.  See the example at :ref:`session_transaction_isolation_enginewide` for a recipe that sets up one :class:`_orm.sessionmaker` for "read only" operations using autocommit connections, and another for "write" operations which will include DML / COMMIT.

    .. seealso::

        `Django-style Database Routers in SQLAlchemy <https://techspot.zzzeek.org/2012/01/11/django-style-database-routers-in-sqlalchemy/>`_  - blog post on a more comprehensive example of :meth:`.Session.get_bind`

水平分区
-----------------------

Horizontal Partitioning

.. tab:: 中文

    水平分区将单个表（或一组表）的行分配到多个数据库中。  
    SQLAlchemy 的 :class:`.Session` 支持这个概念，然而要完全利用它，  
    需要使用 :class:`.Session` 和 :class:`_query.Query` 子类。  
    这些子类的基础版本可在 :ref:`horizontal_sharding_toplevel` ORM 扩展中找到。  
    使用示例可以参考 :ref:`examples_sharding`。

.. tab:: 英文

    Horizontal partitioning partitions the rows of a single table (or a set of
    tables) across multiple databases.    The SQLAlchemy :class:`.Session`
    contains support for this concept, however to use it fully requires that
    :class:`.Session` and :class:`_query.Query` subclasses are used.  A basic version
    of these subclasses are available in the :ref:`horizontal_sharding_toplevel`
    ORM extension.   An example of use is at: :ref:`examples_sharding`.

.. _bulk_operations:

批量操作
===============

Bulk Operations

.. tab:: 中文

    .. legacy::

        SQLAlchemy 2.0 已将 :class:`_orm.Session` 的“批量插入”和  
        “批量更新”功能集成到 2.0 风格的 :meth:`_orm.Session.execute` 方法中，  
        该方法直接使用 :class:`_dml.Insert` 和 :class:`_dml.Update` 构造。  
        请参见文档 :doc:`queryguide/dml`，其中包括 :ref:`orm_queryguide_legacy_bulk_insert`，  
        说明了如何从旧方法迁移到新方法。

.. tab:: 英文

    .. legacy::

        SQLAlchemy 2.0 has integrated the :class:`_orm.Session` "bulk insert" and
        "bulk update" capabilities into 2.0 style :meth:`_orm.Session.execute`
        method, making direct use of :class:`_dml.Insert` and :class:`_dml.Update`
        constructs. See the document at :doc:`queryguide/dml` for documentation,
        including :ref:`orm_queryguide_legacy_bulk_insert` which illustrates migration
        from the older methods to the new methods.
