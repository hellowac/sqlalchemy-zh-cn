SQL 表达式
===============

SQL Expressions

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _faq_sql_expression_string:

如何将 SQL 表达式呈现为字符串，可能内联绑定参数？
------------------------------------------------------------------------------------

How do I render SQL expressions as strings, possibly with bound parameters inlined?

.. tab:: 中文

    SQLAlchemy Core 语句对象或表达式片段的“字符串化”，以及 ORM :class:`_query.Query` 对象，在大多数简单场景下，只需使用 Python 内建的 ``str()`` 函数即可，如下例所示（注意 Python 的 ``print`` 函数会自动调用 ``str()``，即便没有显式使用）：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import table, column, select
        >>> t = table("my_table", column("x"))
        >>> statement = select(t)
        >>> print(str(statement))
        {printsql}SELECT my_table.x
        FROM my_table

    可以对 ORM 的 :class:`_query.Query` 对象、:func:`_expression.select` 、:func:`_expression.insert` 等语句，以及任意表达式片段使用 ``str()`` 函数或等效方式，例如：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import column
        >>> print(column("x") == "some value")
        {printsql}x = :x_1

.. tab:: 英文

    The "stringification" of a SQLAlchemy Core statement object or
    expression fragment, as well as that of an ORM :class:`_query.Query` object,
    in the majority of simple cases is as simple as using
    the ``str()`` builtin function, as below when use it with the ``print``
    function (note the Python ``print`` function also calls ``str()`` automatically
    if we don't use it explicitly):

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import table, column, select
        >>> t = table("my_table", column("x"))
        >>> statement = select(t)
        >>> print(str(statement))
        {printsql}SELECT my_table.x
        FROM my_table

    The ``str()`` builtin, or an equivalent, can be invoked on ORM
    :class:`_query.Query`  object as well as any statement such as that of
    :func:`_expression.select`, :func:`_expression.insert` etc. and also any expression fragment, such
    as:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import column
        >>> print(column("x") == "some value")
        {printsql}x = :x_1

针对特定数据库进行字符串化
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Stringifying for Specific Databases

.. tab:: 中文

    当语句或片段中包含某些具有特定数据库方言格式的元素，或包含仅在特定数据库中才支持的元素时，字符串化可能会生成非目标数据库语法的 SQL，甚至可能抛出 :class:`.UnsupportedCompilationError` 异常。此时需要使用 :meth:`_expression.ClauseElement.compile` 方法，并传入一个表示目标数据库的 :class:`_engine.Engine` 或 :class:`.Dialect` 对象。如下例，如果我们有一个 MySQL 的引擎，可以按 MySQL 方言进行字符串化：

    .. sourcecode:: python

        from sqlalchemy import create_engine

        engine = create_engine("mysql+pymysql://scott:tiger@localhost/test")
        print(statement.compile(engine))

    也可以直接实例化一个 :class:`.Dialect` 对象，无需构建 :class:`_engine.Engine`，例如使用 PostgreSQL 方言：

    .. sourcecode:: python

        from sqlalchemy.dialects import postgresql

        print(statement.compile(dialect=postgresql.dialect()))

    需要注意，任意方言都可以通过 :func:`_sa.create_engine` 创建一个虚拟 URL 的引擎，并访问其 :attr:`_engine.Engine.dialect` 属性获得：

    .. sourcecode:: python

        e = create_engine("postgresql+psycopg2://")
        psycopg2_dialect = e.dialect

    若使用 ORM 的 :class:`~.orm.query.Query` 对象，需要先访问其 :attr:`~.orm.query.Query.statement` 属性，再进行字符串化：

    .. sourcecode:: python

        statement = query.statement
        print(statement.compile(someengine))

.. tab:: 英文

    A complication arises when the statement or fragment we are stringifying
    contains elements that have a database-specific string format, or when it
    contains elements that are only available within a certain kind of database.
    In these cases, we might get a stringified statement that is not in the correct
    syntax for the database we are targeting, or the operation may raise a
    :class:`.UnsupportedCompilationError` exception.   In these cases, it is
    necessary that we stringify the statement using the
    :meth:`_expression.ClauseElement.compile` method, while passing along an :class:`_engine.Engine`
    or :class:`.Dialect` object that represents the target database.  Such as
    below, if we have a MySQL database engine, we can stringify a statement in
    terms of the MySQL dialect::

        from sqlalchemy import create_engine

        engine = create_engine("mysql+pymysql://scott:tiger@localhost/test")
        print(statement.compile(engine))

    More directly, without building up an :class:`_engine.Engine` object we can
    instantiate a :class:`.Dialect` object directly, as below where we
    use a PostgreSQL dialect::

        from sqlalchemy.dialects import postgresql

        print(statement.compile(dialect=postgresql.dialect()))

    Note that any dialect can be assembled using :func:`_sa.create_engine` itself
    with a dummy URL and then accessing the :attr:`_engine.Engine.dialect` attribute,
    such as if we wanted a dialect object for psycopg2::

        e = create_engine("postgresql+psycopg2://")
        psycopg2_dialect = e.dialect

    When given an ORM :class:`~.orm.query.Query` object, in order to get at the
    :meth:`_expression.ClauseElement.compile`
    method we only need access the :attr:`~.orm.query.Query.statement`
    accessor first::

        statement = query.statement
        print(statement.compile(someengine))

内联呈现绑定参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rendering Bound Parameters Inline

.. tab:: 中文

    .. warning:: 
        
        **绝不要** 对来自不可信输入（例如 Web 表单或用户提交内容）的字符串使用上述技术。
       SQLAlchemy 将 Python 值转换为 SQL 字符串的功能 **并不安全，且不会验证传入数据的类型**。
       编写非 DDL 类型 SQL 时应始终使用绑定参数。
    
    上述方式会生成传给 Python :term:`DBAPI` 的 SQL 字符串，其中绑定参数不会被内联。SQLAlchemy 默认不会将绑定参数字符串化，这应由 DBAPI 处理，且跳过绑定参数正是现代 Web 应用中最常见的安全漏洞之一。只有在特定场景（如发出 DDL）中，SQLAlchemy 才会有限支持该操作。此功能可以通过向 ``compile_kwargs`` 传入 ``literal_binds`` 标志开启：
    
    .. sourcecode:: python
    
        from sqlalchemy.sql import table, column, select
    
        t = table("t", column("x"))
    
        s = select(t).where(t.c.x == 5)
    
        # **不要**用于不可信输入！
        print(s.compile(compile_kwargs={"literal_binds": True}))
    
        # 为特定方言渲染
        print(s.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    
        # 或传入引擎作为第一个参数
        print(s.compile(some_engine, compile_kwargs={"literal_binds": True}))
    
    该功能主要用于日志记录或调试目的，当需要查询的原始 SQL 字符串时非常有用。
    
    需要注意，该功能仅支持基础类型，如 int 与 str，且若使用了未设置值的 :func:`.bindparam`，则无法完成字符串化。下文将介绍如何无条件字符串化所有参数。
    
    .. tip::
    
       SQLAlchemy 不支持完整的字面量值字符串化，主要基于以下三点原因：
    
       1. DBAPI 本身已支持该功能，若使用正常方式即可调用。
          若 SQLAlchemy 还需复制每种 DBAPI 的字面量渲染逻辑，将造成冗余且高昂的维护成本。
    
       2. 对绑定参数进行字符串化的场景常被误用于直接执行这些字符串 SQL，这不仅没必要，而且不安全，SQLAlchemy 并不鼓励这种用法。
    
       3. 字面量值渲染是最容易引发安全漏洞的区域。SQLAlchemy 希望将参数字符串化的安全问题尽可能交由各 DBAPI 处理。
    
    鉴于 SQLAlchemy 并不完全支持字面量字符串化，以下是若干在特定调试场景下可用的技巧。以下示例使用 PostgreSQL 的 :class:`_postgresql.UUID` 数据类型：
    
    .. sourcecode:: python
    
        import uuid
    
        from sqlalchemy import Column, create_engine, Integer, select
        from sqlalchemy.dialects.postgresql import UUID
        from sqlalchemy.orm import declarative_base
    
        Base = declarative_base()
    
        class A(Base):
            __tablename__ = "a"
            id = Column(Integer, primary_key=True)
            data = Column(UUID)
    
        stmt = select(A).where(A.data == uuid.uuid4())
    
    给定上述模型和语句，将 UUID 值内联字符串化的方式包括：
    
    * 使用某些 DBAPI（如 psycopg2）的辅助函数，例如 `mogrify() <https://www.psycopg.org/docs/cursor.html#cursor.mogrify>`_ 提供字面量渲染功能。先获取 SQL 字符串，再通过 :attr:`.SQLCompiler.params` 获取参数：
    
      .. sourcecode:: python
    
          e = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")
    
          with e.connect() as conn:
              cursor = conn.connection.cursor()
              compiled = stmt.compile(e)
              print(cursor.mogrify(str(compiled), compiled.params))
    
      上述代码将输出 psycopg2 的原始字节串：
    
      .. sourcecode:: sql
    
          b"SELECT a.id, a.data \nFROM a \nWHERE a.data = 'a511b0fc-76da-4c47-a4b4-716a8189b7ac'::uuid"
    
    * 直接将 :attr:`.SQLCompiler.params` 渲染进 SQL 字符串中，注意使用目标 DBAPI 的 `paramstyle <https://www.python.org/dev/peps/pep-0249/#paramstyle>`_。如 psycopg2 使用命名风格 ``pyformat``。注意 ``render_postcompile`` 的含义将在下文讨论。 **警告：不适用于不可信输入！**
    
      .. sourcecode:: python
    
        e = create_engine("postgresql+psycopg2://")
        compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
        print(str(compiled) % compiled.params)
    
      该方式会生成非可执行但适合调试的字符串：
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = 9eec1209-50b4-4253-b74b-f82461ed80c1
    
      若使用位置参数风格如 ``qmark``，可以结合 :attr:`.SQLCompiler.positiontup` 获取参数顺序，与 :attr:`.SQLCompiler.params` 搭配使用，如在 SQLite 上渲染：
    
      .. sourcecode:: python
    
        import re
        e = create_engine("sqlite+pysqlite://")
        compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
        params = (repr(compiled.params[name]) for name in compiled.positiontup)
        print(re.sub(r"\?", lambda m: next(params), str(compiled)))
    
      输出示例：
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('1bd70375-db17-4d8c-94f1-fc2ef3aada26')
    
    * 使用 :ref:`sqlalchemy.ext.compiler_toplevel` 扩展，在存在用户自定义标志时，自定义渲染 :class:`_sql.BindParameter` 对象：
    
      .. sourcecode:: python
    
        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.sql.expression import BindParameter
    
        @compiles(BindParameter)
        def _render_literal_bindparam(element, compiler, use_my_literal_recipe=False, **kw):
            if not use_my_literal_recipe:
                return compiler.visit_bindparam(element, **kw)
            return repr(element.value)
    
        e = create_engine("postgresql+psycopg2://")
        print(stmt.compile(e, compile_kwargs={"use_my_literal_recipe": True}))
    
      上述代码将输出：
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('47b154cd-36b2-42ae-9718-888629ab9857')
    
    * 若要为特定数据类型实现内建字符串化行为，可继承 :class:`_types.TypeDecorator`，并通过 :meth:`.TypeDecorator.process_literal_param` 提供自定义渲染：
    
      .. sourcecode:: python
    
        from sqlalchemy import TypeDecorator
    
        class UUIDStringify(TypeDecorator):
            impl = UUID
    
            def process_literal_param(self, value, dialect):
                return repr(value)
    
      然后在模型中使用该类型，或使用 :func:`_sql.type_coerce` 临时应用：
    
      .. sourcecode:: python
    
        from sqlalchemy import type_coerce
    
        stmt = select(A).where(type_coerce(A.data, UUIDStringify) == uuid.uuid4())
        print(stmt.compile(e, compile_kwargs={"literal_binds": True}))
    
      输出将再次是：
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('47b154cd-36b2-42ae-9718-888629ab9857')

.. tab:: 英文

    .. warning:: **Never** use these techniques with string content received from
       untrusted input, such as from web forms or other user-input applications.
       SQLAlchemy's facilities to  coerce Python values into direct SQL string
       values are **not secure against untrusted input and do not validate the type
       of data being passed**. Always use bound parameters when programmatically
       invoking non-DDL SQL statements against a relational database.
    
    The above forms will render the SQL statement as it is passed to the Python
    :term:`DBAPI`, which includes that bound parameters are not rendered inline.
    SQLAlchemy normally does not stringify bound parameters, as this is handled
    appropriately by the Python DBAPI, not to mention bypassing bound
    parameters is probably the most widely exploited security hole in
    modern web applications.   SQLAlchemy has limited ability to do this
    stringification in certain circumstances such as that of emitting DDL.
    In order to access this functionality one can use the ``literal_binds``
    flag, passed to ``compile_kwargs``::
    
        from sqlalchemy.sql import table, column, select
    
        t = table("t", column("x"))
    
        s = select(t).where(t.c.x == 5)
    
        # **do not use** with untrusted input!!!
        print(s.compile(compile_kwargs={"literal_binds": True}))
    
        # to render for a specific dialect
        print(s.compile(dialect=dialect, compile_kwargs={"literal_binds": True}))
    
        # or if you have an Engine, pass as first argument
        print(s.compile(some_engine, compile_kwargs={"literal_binds": True}))
    
    This functionality is provided mainly for logging or debugging purposes, where
    having the raw sql string of a query may prove useful.
    
    The above approach has the caveats that it is only supported for basic types,
    such as ints and strings, and furthermore if a :func:`.bindparam` without a
    pre-set value is used directly, it won't be able to stringify that either.
    Methods of stringifying all parameters unconditionally are detailed below.
    
    .. tip::
    
       The reason SQLAlchemy does not support full stringification of all
       datatypes is threefold:
    
       1. This is a functionality that is already supported by the DBAPI in use
          when the DBAPI is used normally.   The SQLAlchemy project cannot be
          tasked with duplicating this functionality for every datatype for
          all backends, as this is redundant work which also incurs significant
          testing and ongoing support overhead.
    
       2. Stringifying with bound parameters inlined for specific databases
          suggests a usage that is actually passing these fully stringified
          statements onto the database for execution. This is unnecessary and
          insecure, and SQLAlchemy does not want to encourage this use in any
          way.
    
       3. The area of rendering literal values is the most likely area for
          security issues to be reported.  SQLAlchemy tries to keep the area of
          safe parameter stringification an issue for the DBAPI drivers as much
          as possible where the specifics for each DBAPI can be handled
          appropriately and securely.
    
    As SQLAlchemy intentionally does not support full stringification of literal
    values, techniques to do so within specific debugging scenarios include the
    following. As an example, we will use the PostgreSQL :class:`_postgresql.UUID`
    datatype::
    
        import uuid
    
        from sqlalchemy import Column
        from sqlalchemy import create_engine
        from sqlalchemy import Integer
        from sqlalchemy import select
        from sqlalchemy.dialects.postgresql import UUID
        from sqlalchemy.orm import declarative_base
    
    
        Base = declarative_base()
    
    
        class A(Base):
            __tablename__ = "a"
    
            id = Column(Integer, primary_key=True)
            data = Column(UUID)
    
    
        stmt = select(A).where(A.data == uuid.uuid4())
    
    Given the above model and statement which will compare a column to a single
    UUID value, options for stringifying this statement with inline values
    include:
    
    * Some DBAPIs such as psycopg2 support helper functions like
      `mogrify() <https://www.psycopg.org/docs/cursor.html#cursor.mogrify>`_ which
      provide access to their literal-rendering functionality.   To use such
      features, render the SQL string without using ``literal_binds`` and pass
      the parameters separately via the :attr:`.SQLCompiler.params` accessor::
    
          e = create_engine("postgresql+psycopg2://scott:tiger@localhost/test")
    
          with e.connect() as conn:
              cursor = conn.connection.cursor()
              compiled = stmt.compile(e)
    
              print(cursor.mogrify(str(compiled), compiled.params))
    
      The above code will produce psycopg2's raw bytestring:
    
      .. sourcecode:: sql
    
          b"SELECT a.id, a.data \nFROM a \nWHERE a.data = 'a511b0fc-76da-4c47-a4b4-716a8189b7ac'::uuid"
    
    * Render the :attr:`.SQLCompiler.params` directly into the statement, using
      the appropriate `paramstyle <https://www.python.org/dev/peps/pep-0249/#paramstyle>`_
      of the target DBAPI.  For example, the psycopg2 DBAPI uses the named ``pyformat``
      style.  The meaning of ``render_postcompile`` will be discussed in the next
      section.   **WARNING this is NOT secure, do NOT use untrusted input**::
    
        e = create_engine("postgresql+psycopg2://")
    
        # will use pyformat style, i.e. %(paramname)s for param
        compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
    
        print(str(compiled) % compiled.params)
    
      This will produce a non-working string, that nonetheless is suitable for
      debugging:
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = 9eec1209-50b4-4253-b74b-f82461ed80c1
    
      Another example using a positional paramstyle such as ``qmark``, we can render
      our above statement in terms of SQLite by also using the
      :attr:`.SQLCompiler.positiontup` collection in conjunction with
      :attr:`.SQLCompiler.params`, in order to retrieve the parameters in
      their positional order for the statement as compiled::
    
        import re
    
        e = create_engine("sqlite+pysqlite://")
    
        # will use qmark style, i.e. ? for param
        compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
    
        # params in positional order
        params = (repr(compiled.params[name]) for name in compiled.positiontup)
    
        print(re.sub(r"\?", lambda m: next(params), str(compiled)))
    
      The above snippet prints:
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('1bd70375-db17-4d8c-94f1-fc2ef3aada26')
    
    * Use the :ref:`sqlalchemy.ext.compiler_toplevel` extension to render
      :class:`_sql.BindParameter` objects in a custom way when a user-defined
      flag is present.  This flag is sent through the ``compile_kwargs``
      dictionary like any other flag::
    
        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.sql.expression import BindParameter
    
    
        @compiles(BindParameter)
        def _render_literal_bindparam(element, compiler, use_my_literal_recipe=False, **kw):
            if not use_my_literal_recipe:
                # use normal bindparam processing
                return compiler.visit_bindparam(element, **kw)
    
            # if use_my_literal_recipe was passed to compiler_kwargs,
            # render the value directly
            return repr(element.value)
    
    
        e = create_engine("postgresql+psycopg2://")
        print(stmt.compile(e, compile_kwargs={"use_my_literal_recipe": True}))
    
      The above recipe will print:
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('47b154cd-36b2-42ae-9718-888629ab9857')
    
    * For type-specific stringification that's built into a model or a statement, the
      :class:`_types.TypeDecorator` class may be used to provide custom stringification
      of any datatype using the :meth:`.TypeDecorator.process_literal_param` method::
    
        from sqlalchemy import TypeDecorator
    
    
        class UUIDStringify(TypeDecorator):
            impl = UUID
    
            def process_literal_param(self, value, dialect):
                return repr(value)
    
      The above datatype needs to be used either explicitly within the model
      or locally within the statement using :func:`_sql.type_coerce`, such as ::
    
        from sqlalchemy import type_coerce
    
        stmt = select(A).where(type_coerce(A.data, UUIDStringify) == uuid.uuid4())
    
        print(stmt.compile(e, compile_kwargs={"literal_binds": True}))
    
      Again printing the same form:
    
      .. sourcecode:: sql
    
        SELECT a.id, a.data
        FROM a
        WHERE a.data = UUID('47b154cd-36b2-42ae-9718-888629ab9857')
    
将“POSTCOMPILE”参数呈现为绑定参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Rendering "POSTCOMPILE" Parameters as Bound Parameters

.. tab:: 中文
    
    SQLAlchemy 提供了一种称为 :paramref:`_sql.BindParameter.expanding` 的绑定参数变体，它是一种“延迟求值”的参数类型：在编译 SQL 结构时会以中间状态渲染，在语句执行时再根据传入的实际值进一步处理。  
    该“扩展”参数被默认用于 :meth:`_sql.ColumnOperators.in_` 表达式，以便生成的 SQL 字符串可以被安全地缓存，而不依赖每次调用 :meth:`_sql.ColumnOperators.in_` 时传入的值列表::
    
      >>> stmt = select(A).where(A.id.in_([1, 2, 3]))
    
    若要将 IN 子句渲染为真实的绑定参数符号，可在调用 :meth:`_sql.ClauseElement.compile` 时使用 ``render_postcompile=True`` 标志：
    
    .. sourcecode:: pycon+sql
    
      >>> e = create_engine("postgresql+psycopg2://")
      >>> print(stmt.compile(e, compile_kwargs={"render_postcompile": True}))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.id IN (%(id_1_1)s, %(id_1_2)s, %(id_1_3)s)
    
    前文关于绑定参数渲染所介绍的 ``literal_binds`` 标志，会自动将 ``render_postcompile`` 设置为 True，因此对于包含简单整数或字符串的语句，可以直接进行字符串化：
    
    .. sourcecode:: pycon+sql
    
      # literal_binds 会隐式启用 render_postcompile
      >>> print(stmt.compile(e, compile_kwargs={"literal_binds": True}))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.id IN (1, 2, 3)
    
    :attr:`.SQLCompiler.params` 与 :attr:`.SQLCompiler.positiontup` 也与 ``render_postcompile`` 兼容，因此可继续使用之前渲染内联绑定参数的方式，如 SQLite 的位置参数风格：
    
    .. sourcecode:: pycon+sql
    
      >>> u1, u2, u3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
      >>> stmt = select(A).where(A.data.in_([u1, u2, u3]))
    
      >>> import re
      >>> e = create_engine("sqlite+pysqlite://")
      >>> compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
      >>> params = (repr(compiled.params[name]) for name in compiled.positiontup)
      >>> print(re.sub(r"\?", lambda m: next(params), str(compiled)))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.data IN (UUID('aa1944d6-9a5a-45d5-b8da-0ba1ef0a4f38'), UUID('a81920e6-15e2-4392-8a3c-d775ffa9ccd2'), UUID('b5574cdb-ff9b-49a3-be52-dbc89f087bfa'))
    
    .. warning::
    
        请注意，**以上所有将字面量值字符串化的代码示例**，都绕过了使用绑定参数的方式将语句发送给数据库，因此 **仅可用于以下情况**：
    
        1. **仅用于调试目的**
    
        2. 该字符串 **不会被传递给生产数据库执行**
    
        3. 仅处理 **本地、可信输入**
    
        上述字符串化技巧 **在安全性方面毫无保障，绝不可用于连接生产环境数据库**。

.. tab:: 英文

    SQLAlchemy includes a variant on a bound parameter known as
    :paramref:`_sql.BindParameter.expanding`, which is a "late evaluated" parameter
    that is rendered in an intermediary state when a SQL construct is compiled,
    which is then further processed at statement execution time when the actual
    known values are passed.   "Expanding" parameters are used for
    :meth:`_sql.ColumnOperators.in_` expressions by default so that the SQL
    string can be safely cached independently of the actual lists of values
    being passed to a particular invocation of :meth:`_sql.ColumnOperators.in_`::
    
      >>> stmt = select(A).where(A.id.in_([1, 2, 3]))
    
    To render the IN clause with real bound parameter symbols, use the
    ``render_postcompile=True`` flag with :meth:`_sql.ClauseElement.compile`:
    
    .. sourcecode:: pycon+sql
    
      >>> e = create_engine("postgresql+psycopg2://")
      >>> print(stmt.compile(e, compile_kwargs={"render_postcompile": True}))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.id IN (%(id_1_1)s, %(id_1_2)s, %(id_1_3)s)
    
    The ``literal_binds`` flag, described in the previous section regarding
    rendering of bound parameters, automatically sets ``render_postcompile`` to
    True, so for a statement with simple ints/strings, these can be stringified
    directly:
    
    .. sourcecode:: pycon+sql
    
      # render_postcompile is implied by literal_binds
      >>> print(stmt.compile(e, compile_kwargs={"literal_binds": True}))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.id IN (1, 2, 3)
    
    The :attr:`.SQLCompiler.params` and :attr:`.SQLCompiler.positiontup` are
    also compatible with ``render_postcompile``, so that
    the previous recipes for rendering inline bound parameters will work here
    in the same way, such as SQLite's positional form:
    
    .. sourcecode:: pycon+sql
    
      >>> u1, u2, u3 = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
      >>> stmt = select(A).where(A.data.in_([u1, u2, u3]))
    
      >>> import re
      >>> e = create_engine("sqlite+pysqlite://")
      >>> compiled = stmt.compile(e, compile_kwargs={"render_postcompile": True})
      >>> params = (repr(compiled.params[name]) for name in compiled.positiontup)
      >>> print(re.sub(r"\?", lambda m: next(params), str(compiled)))
      {printsql}SELECT a.id, a.data
      FROM a
      WHERE a.data IN (UUID('aa1944d6-9a5a-45d5-b8da-0ba1ef0a4f38'), UUID('a81920e6-15e2-4392-8a3c-d775ffa9ccd2'), UUID('b5574cdb-ff9b-49a3-be52-dbc89f087bfa'))
    
    .. warning::
    
        Remember, **all** of the above code recipes which stringify literal
        values, bypassing the use of bound parameters when sending statements
        to the database, are **only to be used when**:
    
        1. the use is **debugging purposes only**
    
        2. the string **is not to be passed to a live production database**
    
        3. only with **local, trusted input**
    
        The above recipes for stringification of literal values are **not secure in
        any way and should never be used against production databases**.

.. _faq_sql_expression_percent_signs:

为什么在对 SQL 语句进行字符串化时百分号会加倍？
------------------------------------------------------------------------

Why are percent signs being doubled up when stringifying SQL statements?

.. tab:: 中文
    
    许多 :term:`DBAPI` 实现采用 ``pyformat`` 或 ``format`` 风格的 `paramstyle <https://www.python.org/dev/peps/pep-0249/#paramstyle>`_，这类风格在语法中会使用百分号 (%)。  
    大多数采用该风格的 DBAPI 要求语句中其他用途的百分号必须成对出现（即进行转义），如：
    
    .. sourcecode:: sql
    
        SELECT a, b FROM some_table WHERE a = %s AND c = %s AND num %% modulus = 0
    
    当 SQLAlchemy 将 SQL 语句传递给底层 DBAPI 时，绑定参数的替换方式与 Python 的字符串插值运算符 ``%`` 相同，且许多 DBAPI 实际上也直接使用了该运算符。  
    如上述语句，绑定参数替换后应如下所示：
    
    .. sourcecode:: sql
    
        SELECT a, b FROM some_table WHERE a = 5 AND c = 10 AND num % modulus = 0
    
    对于 PostgreSQL（默认 DBAPI 为 psycopg2）和 MySQL（默认 DBAPI 为 mysqlclient）等数据库的默认编译器，会自动进行百分号转义处理：
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import table, column
        >>> from sqlalchemy.dialects import postgresql
        >>> t = table("my_table", column("value % one"), column("value % two"))
        >>> print(t.select().compile(dialect=postgresql.dialect()))
        {printsql}SELECT my_table."value %% one", my_table."value %% two"
        FROM my_table
    
    若使用此类方言，但希望生成不包含绑定参数符号的非 DBAPI 语句，可以使用一种简便方式：直接通过 Python 的 ``%`` 运算符替换空参数集来去除百分号转义：
    
    .. sourcecode:: pycon+sql
    
        >>> strstmt = str(t.select().compile(dialect=postgresql.dialect()))
        >>> print(strstmt % ())
        {printsql}SELECT my_table."value % one", my_table."value % two"
        FROM my_table
    
    另一种方法是为使用的方言设置不同的参数风格；所有 :class:`.Dialect` 实现均接受 ``paramstyle`` 参数，它会影响该方言的编译器使用指定的参数风格。  
    如下示例，将常见的 ``named`` 参数风格应用到 PostgreSQL 方言中，以禁用 SQL 编译过程中的百分号转义：
    
    .. sourcecode:: pycon+sql
    
        >>> print(t.select().compile(dialect=postgresql.dialect(paramstyle="named")))
        {printsql}SELECT my_table."value % one", my_table."value % two"
        FROM my_table

.. tab:: 英文

    Many :term:`DBAPI` implementations make use of the ``pyformat`` or ``format``
    `paramstyle <https://www.python.org/dev/peps/pep-0249/#paramstyle>`_, which
    necessarily involve percent signs in their syntax.  Most DBAPIs that do this
    expect percent signs used for other reasons to be doubled up (i.e. escaped) in
    the string form of the statements used, e.g.:

    .. sourcecode:: sql

        SELECT a, b FROM some_table WHERE a = %s AND c = %s AND num %% modulus = 0

    When SQL statements are passed to the underlying DBAPI by SQLAlchemy,
    substitution of bound parameters works in the same way as the Python string
    interpolation operator ``%``, and in many cases the DBAPI actually uses this
    operator directly.  Above, the substitution of bound parameters would then look
    like:

    .. sourcecode:: sql

        SELECT a, b FROM some_table WHERE a = 5 AND c = 10 AND num % modulus = 0

    The default compilers for databases like PostgreSQL (default DBAPI is psycopg2)
    and MySQL (default DBAPI is mysqlclient) will have this percent sign
    escaping behavior:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import table, column
        >>> from sqlalchemy.dialects import postgresql
        >>> t = table("my_table", column("value % one"), column("value % two"))
        >>> print(t.select().compile(dialect=postgresql.dialect()))
        {printsql}SELECT my_table."value %% one", my_table."value %% two"
        FROM my_table

    When such a dialect is being used, if non-DBAPI statements are desired that
    don't include bound parameter symbols, one quick way to remove the percent
    signs is to simply substitute in an empty set of parameters using Python's
    ``%`` operator directly:

    .. sourcecode:: pycon+sql

        >>> strstmt = str(t.select().compile(dialect=postgresql.dialect()))
        >>> print(strstmt % ())
        {printsql}SELECT my_table."value % one", my_table."value % two"
        FROM my_table

    The other is to set a different parameter style on the dialect being used; all
    :class:`.Dialect` implementations accept a parameter
    ``paramstyle`` which will cause the compiler for that
    dialect to use the given parameter style.  Below, the very common ``named``
    parameter style is set within the dialect used for the compilation so that
    percent signs are no longer significant in the compiled form of SQL, and will
    no longer be escaped:

    .. sourcecode:: pycon+sql

        >>> print(t.select().compile(dialect=postgresql.dialect(paramstyle="named")))
        {printsql}SELECT my_table."value % one", my_table."value % two"
        FROM my_table


.. _faq_sql_expression_op_parenthesis:

我正在使用 op() 生成自定义运算符，但我的括号无法正确显示
---------------------------------------------------------------------------------------------

I'm using op() to generate a custom operator and my parenthesis are not coming out correctly

.. tab:: 中文

    :meth:`.Operators.op` 方法允许创建一个 SQLAlchemy 未知的自定义数据库运算符：

    .. sourcecode:: pycon+sql

        >>> print(column("q").op("->")(column("p")))
        {printsql}q -> p

    然而，当该方法用于复合表达式的右侧时，其生成的 SQL 可能不会按照预期加上括号：

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).op("->")(column("p")))
        {printsql}q1 + q2 -> p

    上述代码中，我们更可能期望的输出是 ``(q1 + q2) -> p``。

    要解决此类问题，可以通过设置 :paramref:`.Operators.op.precedence` 参数来指定该运算符的优先级，设为一个较高的数值（最大为 100）。目前 SQLAlchemy 中使用的最高运算符优先级为 15：

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).op("->", precedence=100)(column("p")))
        {printsql}(q1 + q2) -> p

    我们也可以通过 :meth:`_expression.ColumnElement.self_group` 方法强制对二元表达式（即具有左右操作数与运算符的表达式）加括号：

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).self_group().op("->")(column("p")))
        {printsql}(q1 + q2) -> p

.. tab:: 英文

    The :meth:`.Operators.op` method allows one to create a custom database operator
    otherwise not known by SQLAlchemy:

    .. sourcecode:: pycon+sql

        >>> print(column("q").op("->")(column("p")))
        {printsql}q -> p

    However, when using it on the right side of a compound expression, it doesn't
    generate parenthesis as we expect:

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).op("->")(column("p")))
        {printsql}q1 + q2 -> p

    Where above, we probably want ``(q1 + q2) -> p``.

    The solution to this case is to set the precedence of the operator, using
    the :paramref:`.Operators.op.precedence` parameter, to a high
    number, where 100 is the maximum value, and the highest number used by any
    SQLAlchemy operator is currently 15:

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).op("->", precedence=100)(column("p")))
        {printsql}(q1 + q2) -> p

    We can also usually force parenthesization around a binary expression (e.g.
    an expression that has left/right operands and an operator) using the
    :meth:`_expression.ColumnElement.self_group` method:

    .. sourcecode:: pycon+sql

        >>> print((column("q1") + column("q2")).self_group().op("->")(column("p")))
        {printsql}(q1 + q2) -> p

为什么括号规则是这样的？
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Why are the parentheses rules like this?

.. tab:: 中文

    许多数据库在遇到过多括号或括号出现在不符合语法预期的位置时会报错，因此 SQLAlchemy 并不会基于表达式的组合方式（grouping）来盲目生成括号，而是依赖运算符优先级和结合性，仅在必要时生成最少的括号。否则像下面这样的表达式::

        column("a") & column("b") & column("c") & column("d")

    会被生成为：

    .. sourcecode:: sql

        (((a AND b) AND c) AND d)

    虽然语法上没问题，但这可能会让人烦恼（并可能被报告为 bug）。在其他场景中，这种处理甚至会导致更容易让数据库混淆的问题，例如::

        column("q", ARRAY(Integer, dimensions=2))[5][6]

    会被生成为：

    .. sourcecode:: sql

        ((q[5])[6])

    还有一些边缘情况，比如我们会得到 ``"(x) = 7"`` 这种形式，而许多数据库对这种写法也不太友好。因此，SQLAlchemy 的括号处理逻辑不会一味地包裹括号，而是通过运算符的优先级与结合性来判断是否应当生成括号。

    对于 :meth:`.Operators.op` 方法，其默认的优先级（precedence）为 0。

    如果我们将 :paramref:`.Operators.op.precedence` 的默认值设为 100（即最高），会发生什么？  
    这会导致生成的表达式中增加更多括号，但语义上依然是正确的。也就是说，下面两个表达式是等价的：

    .. sourcecode:: pycon+sql

        >>> print((column("q") - column("y")).op("+", precedence=100)(column("z")))
        {printsql}(q - y) + z{stop}
        >>> print((column("q") - column("y")).op("+")(column("z")))
        {printsql}q - y + z{stop}

    但以下两个则不等价：

    .. sourcecode:: pycon+sql

        >>> print(column("q") - column("y").op("+", precedence=100)(column("z")))
        {printsql}q - y + z{stop}
        >>> print(column("q") - column("y").op("+")(column("z")))
        {printsql}q - (y + z){stop}

    目前来看，既然括号的处理方式是基于运算符优先级与结合性，就不太可能在所有情况下都为一个没有指定优先级的通用自定义运算符自动地生成理想的括号结构。因为有时我们希望自定义运算符的优先级低于其他运算符，有时又希望它更高。

    或许在未来，我们可以让上述“二元”表达式在调用 ``op()`` 时自动强制使用 ``self_group()`` 方法，即假设左侧的复合表达式总是可以安全地加上括号。  
    也许这种更改以后可以引入，但目前来看，保持内部括号处理规则的一致性仍是更稳妥的选择。

.. tab:: 英文

    A lot of databases barf when there are excessive parenthesis or when
    parenthesis are in unusual places they doesn't expect, so SQLAlchemy does not
    generate parenthesis based on groupings, it uses operator precedence and if the
    operator is known to be associative, so that parenthesis are generated
    minimally. Otherwise, an expression like::

        column("a") & column("b") & column("c") & column("d")

    would produce:

    .. sourcecode:: sql

        (((a AND b) AND c) AND d)

    which is fine but would probably annoy people (and be reported as a bug). In
    other cases, it leads to things that are more likely to confuse databases or at
    the very least readability, such as::

        column("q", ARRAY(Integer, dimensions=2))[5][6]

    would produce:

    .. sourcecode:: sql

        ((q[5])[6])

    There are also some edge cases where we get things like ``"(x) = 7"`` and databases
    really don't like that either.  So parenthesization doesn't naively
    parenthesize, it uses operator precedence and associativity to determine
    groupings.

    For :meth:`.Operators.op`, the value of precedence defaults to zero.

    What if we defaulted the value of :paramref:`.Operators.op.precedence` to 100,
    e.g. the highest?  Then this expression makes more parenthesis, but is
    otherwise OK, that is, these two are equivalent:

    .. sourcecode:: pycon+sql

        >>> print((column("q") - column("y")).op("+", precedence=100)(column("z")))
        {printsql}(q - y) + z{stop}
        >>> print((column("q") - column("y")).op("+")(column("z")))
        {printsql}q - y + z{stop}

    but these two are not:

    .. sourcecode:: pycon+sql

        >>> print(column("q") - column("y").op("+", precedence=100)(column("z")))
        {printsql}q - y + z{stop}
        >>> print(column("q") - column("y").op("+")(column("z")))
        {printsql}q - (y + z){stop}

    For now, it's not clear that as long as we are doing parenthesization based on
    operator precedence and associativity, if there is really a way to parenthesize
    automatically for a generic operator with no precedence given that is going to
    work in all cases, because sometimes you want a custom op to have a lower
    precedence than the other operators and sometimes you want it to be higher.

    It is possible that maybe if the "binary" expression above forced the use of
    the ``self_group()`` method when ``op()`` is called, making the assumption that
    a compound expression on the left side can always be parenthesized harmlessly.
    Perhaps this change can be made at some point, however for the time being
    keeping the parenthesization rules more internally consistent seems to be
    the safer approach.

