.. highlight:: pycon+sql

操作符参考
===============================

Operator Reference

..  Setup code, not for display

    >>> from sqlalchemy import column, select
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)
    >>> from sqlalchemy import MetaData, Table, Column, Integer, String, Numeric
    >>> metadata_obj = MetaData()
    >>> user_table = Table(
    ...     "user_account",
    ...     metadata_obj,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("name", String(30)),
    ...     Column("fullname", String),
    ... )
    >>> from sqlalchemy import ForeignKey
    >>> address_table = Table(
    ...     "address",
    ...     metadata_obj,
    ...     Column("id", Integer, primary_key=True),
    ...     Column("user_id", None, ForeignKey("user_account.id")),
    ...     Column("email_address", String, nullable=False),
    ... )
    >>> metadata_obj.create_all(engine)
    BEGIN (implicit)
    ...
    >>> from sqlalchemy.orm import declarative_base
    >>> Base = declarative_base()
    >>> from sqlalchemy.orm import relationship
    >>> class User(Base):
    ...     __tablename__ = "user_account"
    ...
    ...     id = Column(Integer, primary_key=True)
    ...     name = Column(String(30))
    ...     fullname = Column(String)
    ...
    ...     addresses = relationship("Address", back_populates="user")
    ...
    ...     def __repr__(self):
    ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

    >>> class Address(Base):
    ...     __tablename__ = "address"
    ...
    ...     id = Column(Integer, primary_key=True)
    ...     email_address = Column(String, nullable=False)
    ...     user_id = Column(Integer, ForeignKey("user_account.id"))
    ...
    ...     user = relationship("User", back_populates="addresses")
    ...
    ...     def __repr__(self):
    ...         return f"Address(id={self.id!r}, email_address={self.email_address!r})"
    >>> conn = engine.connect()
    >>> from sqlalchemy.orm import Session
    >>> session = Session(conn)
    >>> session.add_all(
    ...     [
    ...         User(
    ...             name="spongebob",
    ...             fullname="Spongebob Squarepants",
    ...             addresses=[Address(email_address="spongebob@sqlalchemy.org")],
    ...         ),
    ...         User(
    ...             name="sandy",
    ...             fullname="Sandy Cheeks",
    ...             addresses=[
    ...                 Address(email_address="sandy@sqlalchemy.org"),
    ...                 Address(email_address="squirrel@squirrelpower.org"),
    ...             ],
    ...         ),
    ...         User(
    ...             name="patrick",
    ...             fullname="Patrick Star",
    ...             addresses=[Address(email_address="pat999@aol.com")],
    ...         ),
    ...         User(
    ...             name="squidward",
    ...             fullname="Squidward Tentacles",
    ...             addresses=[Address(email_address="stentcl@sqlalchemy.org")],
    ...         ),
    ...         User(name="ehkrabs", fullname="Eugene H. Krabs"),
    ...     ]
    ... )
    >>> session.commit()
    BEGIN ...
    >>> conn.begin()
    BEGIN ...

.. tab:: 中文

    本节详细介绍了可用于构建 SQL 表达式的运算符的用法。

    这些方法是根据 :class:`_sql.Operators` 和 :class:`_sql.ColumnOperators` 基类呈现的。这些方法可以在这些类的派生类中使用，包括：

    * :class:`_schema.Column` 对象

    * 更广泛地说，:class:`_sql.ColumnElement` 对象，它们是所有核心 SQL 表达式语言列级表达式的根

    * :class:`_orm.InstrumentedAttribute` 对象，它们是 ORM 级别的映射属性。

    这些运算符首先在教程部分进行介绍，包括：

    * :doc:`/tutorial/index` - :term:`2.0 风格` 的统一教程

    * :doc:`/orm/tutorial` - :term:`1.x 风格` 的 ORM 教程

    * :doc:`/core/tutorial` - :term:`1.x 风格` 的 Core 教程

.. tab:: 英文

    This section details usage of the operators that are available
    to construct SQL expressions.

    These methods are presented in terms of the :class:`_sql.Operators`
    and :class:`_sql.ColumnOperators` base classes.   The methods are then
    available on descendants of these classes, including:

    * :class:`_schema.Column` objects

    * :class:`_sql.ColumnElement` objects more generally, which are the root
      of all Core SQL Expression language column-level expressions

    * :class:`_orm.InstrumentedAttribute` objects, which are ORM
      level mapped attributes.

    The operators are first introduced in the tutorial sections, including:

    * :doc:`/tutorial/index` - unified tutorial in :term:`2.0 style`

    * :doc:`/orm/tutorial` - ORM tutorial in :term:`1.x style`

    * :doc:`/core/tutorial` - Core tutorial in :term:`1.x style`

比较运算符
^^^^^^^^^^^^^^^^^^^^

Comparison Operators

.. tab:: 中文

    适用于多种数据类型的基本比较，包括数字、字符串、日期和许多其他类型：

.. tab:: 英文

    Basic comparisons which apply to many datatypes, including numerics, strings, dates, and many others:

* :meth:`_sql.ColumnOperators.__eq__` (Python "``==``" operator)::

    >>> print(column("x") == 5)
    {printsql}x = :x_1

  ..

* :meth:`_sql.ColumnOperators.__ne__` (Python "``!=``" operator)::

    >>> print(column("x") != 5)
    {printsql}x != :x_1

  ..

* :meth:`_sql.ColumnOperators.__gt__` (Python "``>``" operator)::

    >>> print(column("x") > 5)
    {printsql}x > :x_1

  ..

* :meth:`_sql.ColumnOperators.__lt__` (Python "``<``" operator)::

    >>> print(column("x") < 5)
    {printsql}x < :x_1

  ..

* :meth:`_sql.ColumnOperators.__ge__` (Python "``>=``" operator)::

    >>> print(column("x") >= 5)
    {printsql}x >= :x_1

  ..

* :meth:`_sql.ColumnOperators.__le__` (Python "``<=``" operator)::

    >>> print(column("x") <= 5)
    {printsql}x <= :x_1

  ..

* :meth:`_sql.ColumnOperators.between`::

    >>> print(column("x").between(5, 10))
    {printsql}x BETWEEN :x_1 AND :x_2

  ..

IN 比较
^^^^^^^^^^^^^^

IN Comparisons

.. tab:: 中文

    SQL IN 运算符是 SQLAlchemy 中的一个独立主题。由于 IN 运算符通常用于固定值列表，因此 SQLAlchemy 的绑定参数强制功能利用了一种特殊的 SQL 编译形式，该形式会呈现一个临时 SQL 字符串以供编译，该字符串在第二步中形成最终的绑定参数列表。换句话说，“它就是有效”。

.. tab:: 英文

    The SQL IN operator is a subject all its own in SQLAlchemy.   As the IN operator is usually used against a list of fixed values, SQLAlchemy's feature of bound parameter coercion makes use of a special form of SQL compilation that renders an interim SQL string for compilation that's formed into the final list of bound parameters in a second step.   In other words, "it just works".

IN 与值列表
~~~~~~~~~~~~~~~~~~~~~~~~~~~

IN against a list of values

.. tab:: 中文

    IN 通常通过将值列表传递给 :meth:`_sql.ColumnOperators.in_` 方法来实现：

        >>> print(column("x").in_([1, 2, 3]))
        {printsql}x IN (__[POSTCOMPILE_x_1])

    特殊绑定形式 ``__[POSTCOMPILE`` 在执行时被呈现为单独的参数，如下所示：

        >>> stmt = select(User.id).where(User.id.in_([1, 2, 3]))
        >>> result = conn.execute(stmt)
        {execsql}SELECT user_account.id
        FROM user_account
        WHERE user_account.id IN (?, ?, ?)
        [...] (1, 2, 3){stop}

.. tab:: 英文

    IN is available most typically by passing a list of
    values to the :meth:`_sql.ColumnOperators.in_` method::

        >>> print(column("x").in_([1, 2, 3]))
        {printsql}x IN (__[POSTCOMPILE_x_1])

    The special bound form ``__[POSTCOMPILE`` is rendered into individual parameters
    at execution time, illustrated below::

        >>> stmt = select(User.id).where(User.id.in_([1, 2, 3]))
        >>> result = conn.execute(stmt)
        {execsql}SELECT user_account.id
        FROM user_account
        WHERE user_account.id IN (?, ?, ?)
        [...] (1, 2, 3){stop}

空 IN 表达式
~~~~~~~~~~~~~~~~~~~~

Empty IN Expressions

.. tab:: 中文

    SQLAlchemy 通过呈现不返回任何行的后端特定子查询，为空 IN 表达式生成数学上有效的结果。换句话说，“它就是有效”::

        >>> stmt = select(User.id).where(User.id.in_([]))
        >>> result = conn.execute(stmt)
        {execsql}SELECT user_account.id
        FROM user_account
        WHERE user_account.id IN (SELECT 1 FROM (SELECT 1) WHERE 1!=1)
        [...] ()

    上面的“空集”子查询正确概括，并且还根据保留的 IN 运算符进行呈现。

.. tab:: 英文

    SQLAlchemy produces a mathematically valid result for an empty IN expression
    by rendering a backend-specific subquery that returns no rows.   Again
    in other words, "it just works"::

        >>> stmt = select(User.id).where(User.id.in_([]))
        >>> result = conn.execute(stmt)
        {execsql}SELECT user_account.id
        FROM user_account
        WHERE user_account.id IN (SELECT 1 FROM (SELECT 1) WHERE 1!=1)
        [...] ()

    The "empty set" subquery above generalizes correctly and is also rendered
    in terms of the IN operator which remains in place.


NOT IN
~~~~~~~

NOT IN

.. tab:: 中文

    “NOT IN” 可通过 :meth:`_sql.ColumnOperators.not_in` 运算符获得::

        >>> print(column("x").not_in([1, 2, 3]))
        {printsql}(x NOT IN (__[POSTCOMPILE_x_1]))

    这通常更容易通过使用 ``~`` 运算符取反来获得::

        >>> print(~column("x").in_([1, 2, 3]))
        {printsql}(x NOT IN (__[POSTCOMPILE_x_1]))

.. tab:: 英文

    "NOT IN" is available via the :meth:`_sql.ColumnOperators.not_in` operator::

        >>> print(column("x").not_in([1, 2, 3]))
        {printsql}(x NOT IN (__[POSTCOMPILE_x_1]))

    This is typically more easily available by negating with the ``~`` operator::

        >>> print(~column("x").in_([1, 2, 3]))
        {printsql}(x NOT IN (__[POSTCOMPILE_x_1]))

元组 IN 表达式
~~~~~~~~~~~~~~~~~~~~

Tuple IN Expressions

.. tab:: 中文

    元组与元组的比较在 IN 中很常见，因为在其他用例中，它适用于将行与一组潜在的复合主键值进行匹配的情况。:func:`_sql.tuple_` 构造为元组比较提供了基本构建块。然后，:meth:`_sql.Tuple.in_` 操作符接收一个元组列表::

        >>> from sqlalchemy import tuple_
        >>> tup = tuple_(column("x", Integer), column("y", Integer))
        >>> expr = tup.in_([(1, 2), (3, 4)])
        >>> print(expr)
        {printsql}(x, y) IN (__[POSTCOMPILE_param_1])

    为了说明所呈现的参数::

        >>> tup = tuple_(User.id, Address.id)
        >>> stmt = select(User.name).join(Address).where(tup.in_([(1, 1), (2, 2)]))
        >>> conn.execute(stmt).all()
        {execsql}SELECT user_account.name
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE (user_account.id, address.id) IN (VALUES (?, ?), (?, ?))
        [...] (1, 1, 2, 2){stop}
        [('spongebob',), ('sandy',)]

.. tab:: 英文

    Comparison of tuples to tuples is common with IN, as among other use cases accommodates for the case when matching rows to a set of potential composite primary key values.  The :func:`_sql.tuple_` construct provides the basic building block for tuple comparisons.  The :meth:`_sql.Tuple.in_` operator then receives a list of tuples::

        >>> from sqlalchemy import tuple_
        >>> tup = tuple_(column("x", Integer), column("y", Integer))
        >>> expr = tup.in_([(1, 2), (3, 4)])
        >>> print(expr)
        {printsql}(x, y) IN (__[POSTCOMPILE_param_1])

    To illustrate the parameters rendered::

        >>> tup = tuple_(User.id, Address.id)
        >>> stmt = select(User.name).join(Address).where(tup.in_([(1, 1), (2, 2)]))
        >>> conn.execute(stmt).all()
        {execsql}SELECT user_account.name
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE (user_account.id, address.id) IN (VALUES (?, ?), (?, ?))
        [...] (1, 1, 2, 2){stop}
        [('spongebob',), ('sandy',)]

子查询 IN
~~~~~~~~~~~

Subquery IN

.. tab:: 中文

    最后，:meth:`_sql.ColumnOperators.in_` 和 :meth:`_sql.ColumnOperators.not_in` 运算符与子查询一起使用。该表单规定直接传入 :class:`_sql.Select` 构造，而无需显式转换为命名子查询::

        >>> print(column("x").in_(select(user_table.c.id)))
        {printsql}x IN (SELECT user_account.id
        FROM user_account)

    元组按预期工作::

        >>> print(
        ... tuple_(column("x"), column("y")).in_(
        ... select(user_table.c.id, address_table.c.id).join(address_table)
        ... )
        ... )
        {printsql}(x, y) IN (SELECT user_account.id, address.id
        FROM user_account JOIN address ON user_account.id = address.user_id)

.. tab:: 英文

    Finally, the :meth:`_sql.ColumnOperators.in_` and :meth:`_sql.ColumnOperators.not_in` operators work with subqueries.   The form provides that a :class:`_sql.Select` construct is passed in directly, without any explicit conversion to a named subquery::

        >>> print(column("x").in_(select(user_table.c.id)))
        {printsql}x IN (SELECT user_account.id
        FROM user_account)

    Tuples work as expected::

        >>> print(
        ...     tuple_(column("x"), column("y")).in_(
        ...         select(user_table.c.id, address_table.c.id).join(address_table)
        ...     )
        ... )
        {printsql}(x, y) IN (SELECT user_account.id, address.id
        FROM user_account JOIN address ON user_account.id = address.user_id)

身份比较
^^^^^^^^^^^^^^^^^^^^

Identity Comparisons

.. tab:: 中文
    
    这些运算符用于测试特殊的 SQL 值，例如 ``NULL``，以及某些数据库支持的布尔常量 ``true`` 或 ``false``：
    
    * :meth:`_sql.ColumnOperators.is_`：
    
      此运算符会生成精确的 SQL 表达式 "x IS y"，最常见的形式是 "<expr> IS NULL"。可使用普通的 Python 值 ``None`` 来获得 ``NULL`` 常量::
    
        >>> print(column("x").is_(None))
        {printsql}x IS NULL
    
      如果需要，也可以显式地使用 :func:`_sql.null` 构造函数来获取 SQL NULL::
    
        >>> from sqlalchemy import null
        >>> print(column("x").is_(null()))
        {printsql}x IS NULL
    
      当使用重载的 :meth:`_sql.ColumnOperators.__eq__` 运算符（即 ``==``）并结合 ``None`` 或 :func:`_sql.null` 值时，会自动调用 :meth:`_sql.ColumnOperators.is_` 运算符。因此，通常不需要显式使用 :meth:`_sql.ColumnOperators.is_`，尤其是用于动态值的情况下::
    
        >>> a = None
        >>> print(column("x") == a)
        {printsql}x IS NULL
    
      注意，Python 中的 ``is`` 运算符 **不可重载**。尽管 Python 提供了重载 ``==`` 和 ``!=`` 等运算符的机制，但并 **不** 支持重定义 ``is``。
    
    * :meth:`_sql.ColumnOperators.is_not`：
    
      类似于 :meth:`_sql.ColumnOperators.is_`，该运算符生成 "IS NOT"::
    
        >>> print(column("x").is_not(None))
        {printsql}x IS NOT NULL
    
      与 ``!= None`` 等价::
    
        >>> print(column("x") != None)
        {printsql}x IS NOT NULL
    
    * :meth:`_sql.ColumnOperators.is_distinct_from`：
    
      生成 SQL 的 IS DISTINCT FROM::
    
        >>> print(column("x").is_distinct_from("some value"))
        {printsql}x IS DISTINCT FROM :x_1
    
    * :meth:`_sql.ColumnOperators.isnot_distinct_from`：
    
      生成 SQL 的 IS NOT DISTINCT FROM::
    
        >>> print(column("x").isnot_distinct_from("some value"))
        {printsql}x IS NOT DISTINCT FROM :x_1


.. tab:: 英文

    These operators involve testing for special SQL values such as
    ``NULL``, boolean constants such as ``true`` or ``false`` which some
    databases support:
    
    * :meth:`_sql.ColumnOperators.is_`:
    
      This operator will provide exactly the SQL for "x IS y", most often seen
      as "<expr> IS NULL".   The ``NULL`` constant is most easily acquired
      using regular Python ``None``::
    
        >>> print(column("x").is_(None))
        {printsql}x IS NULL
    
      SQL NULL is also explicitly available, if needed, using the
      :func:`_sql.null` construct::
    
        >>> from sqlalchemy import null
        >>> print(column("x").is_(null()))
        {printsql}x IS NULL
    
      The :meth:`_sql.ColumnOperators.is_` operator is automatically invoked when
      using the :meth:`_sql.ColumnOperators.__eq__` overloaded operator, i.e.
      ``==``, in conjunction with the ``None`` or :func:`_sql.null` value. In this
      way, there's typically not a need to use :meth:`_sql.ColumnOperators.is_`
      explicitly, particularly when used with a dynamic value::
    
        >>> a = None
        >>> print(column("x") == a)
        {printsql}x IS NULL
    
      Note that the Python ``is`` operator is **not overloaded**.  Even though
      Python provides hooks to overload operators such as ``==`` and ``!=``,
      it does **not** provide any way to redefine ``is``.
    
    * :meth:`_sql.ColumnOperators.is_not`:
    
      Similar to :meth:`_sql.ColumnOperators.is_`, produces "IS NOT"::
    
        >>> print(column("x").is_not(None))
        {printsql}x IS NOT NULL
    
      Is similarly equivalent to ``!= None``::
    
        >>> print(column("x") != None)
        {printsql}x IS NOT NULL
    
    * :meth:`_sql.ColumnOperators.is_distinct_from`:
    
      Produces SQL IS DISTINCT FROM::
    
        >>> print(column("x").is_distinct_from("some value"))
        {printsql}x IS DISTINCT FROM :x_1
    
    * :meth:`_sql.ColumnOperators.isnot_distinct_from`:
    
      Produces SQL IS NOT DISTINCT FROM::
    
        >>> print(column("x").isnot_distinct_from("some value"))
        {printsql}x IS NOT DISTINCT FROM :x_1

字符串比较
^^^^^^^^^^^^^^^^^^

String Comparisons

.. tab:: 中文

    * :meth:`_sql.ColumnOperators.like`::
    
        >>> print(column("x").like("word"))
        {printsql}x LIKE :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.ilike`：
    
      不区分大小写的 LIKE 查询，在通用后端中使用 SQL 的 ``lower()`` 函数。在 PostgreSQL 后端中会使用 ``ILIKE``::
    
        >>> print(column("x").ilike("word"))
        {printsql}lower(x) LIKE lower(:x_1)
    
      ..
    
    * :meth:`_sql.ColumnOperators.notlike`::
    
        >>> print(column("x").notlike("word"))
        {printsql}x NOT LIKE :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.notilike`::
    
        >>> print(column("x").notilike("word"))
        {printsql}lower(x) NOT LIKE lower(:x_1)

.. tab:: 英文

    * :meth:`_sql.ColumnOperators.like`::
    
        >>> print(column("x").like("word"))
        {printsql}x LIKE :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.ilike`:
    
      Case insensitive LIKE makes use of the SQL ``lower()`` function on a
      generic backend.  On the PostgreSQL backend it will use ``ILIKE``::
    
        >>> print(column("x").ilike("word"))
        {printsql}lower(x) LIKE lower(:x_1)
    
      ..
    
    * :meth:`_sql.ColumnOperators.notlike`::
    
        >>> print(column("x").notlike("word"))
        {printsql}x NOT LIKE :x_1
    
      ..
    
    
    * :meth:`_sql.ColumnOperators.notilike`::
    
        >>> print(column("x").notilike("word"))
        {printsql}lower(x) NOT LIKE lower(:x_1)


字符串包含
^^^^^^^^^^^^^^^^^^^

String Containment

.. tab:: 中文
    
    字符串包含运算符基本上是通过 LIKE 和字符串拼接运算符组合而成的，该拼接运算符在大多数后端中为 ``||``，或者有时是函数如 ``concat()``：
    
    * :meth:`_sql.ColumnOperators.startswith`::
    
        >>> print(column("x").startswith("word"))
        {printsql}x LIKE :x_1 || '%'
    
      ..
    
    * :meth:`_sql.ColumnOperators.endswith`::
    
        >>> print(column("x").endswith("word"))
        {printsql}x LIKE '%' || :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.contains`::
    
        >>> print(column("x").contains("word"))
        {printsql}x LIKE '%' || :x_1 || '%'

.. tab:: 英文

    String containment operators are basically built as a combination of
    LIKE and the string concatenation operator, which is ``||`` on most
    backends or sometimes a function like ``concat()``:
    
    * :meth:`_sql.ColumnOperators.startswith`::
    
        >>> print(column("x").startswith("word"))
        {printsql}x LIKE :x_1 || '%'
    
      ..
    
    * :meth:`_sql.ColumnOperators.endswith`::
    
        >>> print(column("x").endswith("word"))
        {printsql}x LIKE '%' || :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.contains`::
    
        >>> print(column("x").contains("word"))
        {printsql}x LIKE '%' || :x_1 || '%'


字符串匹配
^^^^^^^^^^^^^^^^

String matching

.. tab:: 中文
    
    匹配运算符始终是后端特定的，在不同的数据库上可能会有不同的行为和结果：
    
    * :meth:`_sql.ColumnOperators.match`：
    
      这是一个方言相关的运算符，利用底层数据库提供的 MATCH 特性（如果可用）::
    
        >>> print(column("x").match("word"))
        {printsql}x MATCH :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.regexp_match`：
    
      此运算符是方言特定的。以下以 PostgreSQL 方言为例进行说明::
    
        >>> from sqlalchemy.dialects import postgresql
        >>> print(column("x").regexp_match("word").compile(dialect=postgresql.dialect()))
        {printsql}x ~ %(x_1)s
    
      或在 MySQL 中::
    
        >>> from sqlalchemy.dialects import mysql
        >>> print(column("x").regexp_match("word").compile(dialect=mysql.dialect()))
        {printsql}x REGEXP %s

.. tab:: 英文

    Matching operators are always backend-specific and may provide different
    behaviors and results on different databases:
    
    * :meth:`_sql.ColumnOperators.match`:
    
      This is a dialect-specific operator that makes use of the MATCH
      feature of the underlying database, if available::
    
        >>> print(column("x").match("word"))
        {printsql}x MATCH :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.regexp_match`:
    
      This operator is dialect specific.  We can illustrate it in terms of
      for example the PostgreSQL dialect::
    
        >>> from sqlalchemy.dialects import postgresql
        >>> print(column("x").regexp_match("word").compile(dialect=postgresql.dialect()))
        {printsql}x ~ %(x_1)s
    
      Or MySQL::
    
        >>> from sqlalchemy.dialects import mysql
        >>> print(column("x").regexp_match("word").compile(dialect=mysql.dialect()))
        {printsql}x REGEXP %s


.. _queryguide_operators_concat_op:

字符串更改
^^^^^^^^^^^^^^^^^

String Alteration

.. tab:: 中文
    
    * :meth:`_sql.ColumnOperators.concat`：
    
      字符串拼接::
    
        >>> print(column("x").concat("some string"))
        {printsql}x || :x_1
    
      当与一个继承自 :class:`_types.String` 的列表达式一起使用时，也可通过 :meth:`_sql.ColumnOperators.__add__` （即 Python 的 ``+`` 运算符）来使用此操作符::
    
        >>> print(column("x", String) + "some string")
        {printsql}x || :x_1
    
      此运算符会生成合适的、数据库特定的 SQL 表达式，例如在 MySQL 中传统上使用的是 ``concat()`` 函数::
    
        >>> print((column("x", String) + "some string").compile(dialect=mysql.dialect()))
        {printsql}concat(x, %s)
    
      ..
    
    * :meth:`_sql.ColumnOperators.regexp_replace`：
    
      此运算符是 :meth:`_sql.ColumnOperators.regexp` 的补充，在支持的后端上生成等价的 REGEXP REPLACE::
    
        >>> print(column("x").regexp_replace("foo", "bar").compile(dialect=postgresql.dialect()))
        {printsql}REGEXP_REPLACE(x, %(x_1)s, %(x_2)s)
    
      ..
    
    * :meth:`_sql.ColumnOperators.collate`：
    
      生成 SQL 的 COLLATE 运算符，用于在表达式中指定特定的排序规则::
    
        >>> print(
        ...     (column("x").collate("latin1_german2_ci") == "Müller").compile(
        ...         dialect=mysql.dialect()
        ...     )
        ... )
        {printsql}(x COLLATE latin1_german2_ci) = %s
    
      如果想对字面值使用 COLLATE，可以使用 :func:`_sql.literal` 构造函数::
    
        >>> from sqlalchemy import literal
        >>> print(
        ...     (literal("Müller").collate("latin1_german2_ci") == column("x")).compile(
        ...         dialect=mysql.dialect()
        ...     )
        ... )
        {printsql}(%s COLLATE latin1_german2_ci) = x

.. tab:: 英文

    * :meth:`_sql.ColumnOperators.concat`:
    
      String concatenation::
    
        >>> print(column("x").concat("some string"))
        {printsql}x || :x_1
    
      This operator is available via :meth:`_sql.ColumnOperators.__add__`, that
      is, the Python ``+`` operator, when working with a column expression that
      derives from :class:`_types.String`::
    
        >>> print(column("x", String) + "some string")
        {printsql}x || :x_1
    
      The operator will produce the appropriate database-specific construct,
      such as on MySQL it's historically been the ``concat()`` SQL function::
    
        >>> print((column("x", String) + "some string").compile(dialect=mysql.dialect()))
        {printsql}concat(x, %s)
    
      ..
    
    * :meth:`_sql.ColumnOperators.regexp_replace`:
    
      Complementary to :meth:`_sql.ColumnOperators.regexp` this produces REGEXP
      REPLACE equivalent for the backends which support it::
    
        >>> print(column("x").regexp_replace("foo", "bar").compile(dialect=postgresql.dialect()))
        {printsql}REGEXP_REPLACE(x, %(x_1)s, %(x_2)s)
    
      ..
    
    * :meth:`_sql.ColumnOperators.collate`:
    
      Produces the COLLATE SQL operator which provides for specific collations
      at expression time::
    
        >>> print(
        ...     (column("x").collate("latin1_german2_ci") == "Müller").compile(
        ...         dialect=mysql.dialect()
        ...     )
        ... )
        {printsql}(x COLLATE latin1_german2_ci) = %s
    
    
      To use COLLATE against a literal value, use the :func:`_sql.literal` construct::
    
    
        >>> from sqlalchemy import literal
        >>> print(
        ...     (literal("Müller").collate("latin1_german2_ci") == column("x")).compile(
        ...         dialect=mysql.dialect()
        ...     )
        ... )
        {printsql}(%s COLLATE latin1_german2_ci) = x

  ..

算术运算符
^^^^^^^^^^^^^^^^^^^^

Arithmetic Operators

.. tab:: 中文

    * :meth:`_sql.ColumnOperators.__add__`, :meth:`_sql.ColumnOperators.__radd__` （Python "``+``" 运算符）::
    
        >>> print(column("x") + 5)
        {printsql}x + :x_1{stop}
    
        >>> print(5 + column("x"))
        {printsql}:x_1 + x{stop}
    
      ..
    
      注意：当表达式的数据类型是 :class:`_types.String` 或类似类型时，
      :meth:`_sql.ColumnOperators.__add__` 运算符将产生 :ref:`字符串拼接 <queryguide_operators_concat_op>` 的效果。
    
    * :meth:`_sql.ColumnOperators.__sub__`, :meth:`_sql.ColumnOperators.__rsub__` （Python "``-``" 运算符）::
    
        >>> print(column("x") - 5)
        {printsql}x - :x_1{stop}
    
        >>> print(5 - column("x"))
        {printsql}:x_1 - x{stop}
    
      ..
    
    * :meth:`_sql.ColumnOperators.__mul__`, :meth:`_sql.ColumnOperators.__rmul__` （Python "``*``" 运算符）::
    
        >>> print(column("x") * 5)
        {printsql}x * :x_1{stop}
    
        >>> print(5 * column("x"))
        {printsql}:x_1 * x{stop}
    
      ..
    
    * :meth:`_sql.ColumnOperators.__truediv__`, :meth:`_sql.ColumnOperators.__rtruediv__` （Python "``/``" 运算符）。
      这是 Python 的 ``truediv`` 运算符，确保进行真除法::
    
        >>> print(column("x") / 5)
        {printsql}x / CAST(:x_1 AS NUMERIC){stop}
        >>> print(5 / column("x"))
        {printsql}:x_1 / CAST(x AS NUMERIC){stop}
    
      .. versionchanged:: 2.0  Python 的 ``/`` 运算符现在确保执行整数真除法
    
      ..
    
    * :meth:`_sql.ColumnOperators.__floordiv__`, :meth:`_sql.ColumnOperators.__rfloordiv__` （Python "``//``" 运算符）。
      这是 Python 的 ``floordiv`` 运算符，确保进行地板除法。
      对于默认后端以及如 PostgreSQL 等后端，SQL 中的 ``/`` 运算符在处理整数值时通常表现为地板除法::
    
        >>> print(column("x") // 5)
        {printsql}x / :x_1{stop}
        >>> print(5 // column("x", Integer))
        {printsql}:x_1 / x{stop}
    
      对于默认不使用地板除法的后端，或当使用数值类型时，将使用 FLOOR() 函数来确保进行地板除法::
    
        >>> print(column("x") // 5.5)
        {printsql}FLOOR(x / :x_1){stop}
        >>> print(5 // column("x", Numeric))
        {printsql}FLOOR(:x_1 / x){stop}
    
      .. versionadded:: 2.0  添加对 FLOOR 除法的支持
    
      ..
    
    * :meth:`_sql.ColumnOperators.__mod__`, :meth:`_sql.ColumnOperators.__rmod__` （Python "``%``" 运算符）::
    
        >>> print(column("x") % 5)
        {printsql}x % :x_1{stop}
        >>> print(5 % column("x"))
        {printsql}:x_1 % x{stop}


.. tab:: 英文

    * :meth:`_sql.ColumnOperators.__add__`, :meth:`_sql.ColumnOperators.__radd__` (Python "``+``" operator)::
    
        >>> print(column("x") + 5)
        {printsql}x + :x_1{stop}
    
        >>> print(5 + column("x"))
        {printsql}:x_1 + x{stop}
    
      ..
    
    
      Note that when the datatype of the expression is :class:`_types.String`
      or similar, the :meth:`_sql.ColumnOperators.__add__` operator instead produces
      :ref:`string concatenation <queryguide_operators_concat_op>`.
    
    
    * :meth:`_sql.ColumnOperators.__sub__`, :meth:`_sql.ColumnOperators.__rsub__` (Python "``-``" operator)::
    
        >>> print(column("x") - 5)
        {printsql}x - :x_1{stop}
    
        >>> print(5 - column("x"))
        {printsql}:x_1 - x{stop}
    
      ..
    
    
    * :meth:`_sql.ColumnOperators.__mul__`, :meth:`_sql.ColumnOperators.__rmul__` (Python "``*``" operator)::
    
        >>> print(column("x") * 5)
        {printsql}x * :x_1{stop}
    
        >>> print(5 * column("x"))
        {printsql}:x_1 * x{stop}
    
      ..
    
    * :meth:`_sql.ColumnOperators.__truediv__`, :meth:`_sql.ColumnOperators.__rtruediv__` (Python "``/``" operator).
      This is the Python ``truediv`` operator, which will ensure integer true division occurs::
    
        >>> print(column("x") / 5)
        {printsql}x / CAST(:x_1 AS NUMERIC){stop}
        >>> print(5 / column("x"))
        {printsql}:x_1 / CAST(x AS NUMERIC){stop}
    
      .. versionchanged:: 2.0  The Python ``/`` operator now ensures integer true division takes place
    
      ..
    
    * :meth:`_sql.ColumnOperators.__floordiv__`, :meth:`_sql.ColumnOperators.__rfloordiv__` (Python "``//``" operator).
      This is the Python ``floordiv`` operator, which will ensure floor division occurs.
      For the default backend as well as backends such as PostgreSQL, the SQL ``/`` operator normally
      behaves this way for integer values::
    
        >>> print(column("x") // 5)
        {printsql}x / :x_1{stop}
        >>> print(5 // column("x", Integer))
        {printsql}:x_1 / x{stop}
    
      For backends that don't use floor division by default, or when used with numeric values,
      the FLOOR() function is used to ensure floor division::
    
        >>> print(column("x") // 5.5)
        {printsql}FLOOR(x / :x_1){stop}
        >>> print(5 // column("x", Numeric))
        {printsql}FLOOR(:x_1 / x){stop}
    
      .. versionadded:: 2.0  Support for FLOOR division
    
      ..
    
    
    * :meth:`_sql.ColumnOperators.__mod__`, :meth:`_sql.ColumnOperators.__rmod__` (Python "``%``" operator)::
    
        >>> print(column("x") % 5)
        {printsql}x % :x_1{stop}
        >>> print(5 % column("x"))
        {printsql}:x_1 % x{stop}

  ..

.. _operators_bitwise:

按位运算符
^^^^^^^^^^^^^^^^^

Bitwise Operators

.. tab:: 中文
    
    位运算符函数为不同后端提供了一致的位运算操作支持，通常用于兼容的值类型，如整数或位串（例如 PostgreSQL 中的
    :class:`_postgresql.BIT` 类型）。请注意，这些并不是通用的布尔运算符。
    
    .. versionadded:: 2.0.2 添加了专用的位运算符支持。
    
    * :meth:`_sql.ColumnOperators.bitwise_not`, :func:`_sql.bitwise_not`。
      可作为列级方法使用，对父对象生成位反（NOT）表达式::
    
        >>> print(column("x").bitwise_not())
        ~x
    
      此运算符也可作为表达式级方法使用，对单个表达式应用位反操作::
    
        >>> from sqlalchemy import bitwise_not
        >>> print(bitwise_not(column("x")))
        ~x
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_and` 生成位与（AND）操作::
    
        >>> print(column("x").bitwise_and(5))
        x & :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_or` 生成位或（OR）操作::
    
        >>> print(column("x").bitwise_or(5))
        x | :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_xor` 生成位异或（XOR）操作::
    
        >>> print(column("x").bitwise_xor(5))
        x ^ :x_1
    
      对于 PostgreSQL 方言，"#" 被用来表示位异或；使用该后端时会自动生成::
    
        >>> from sqlalchemy.dialects import postgresql
        >>> print(column("x").bitwise_xor(5).compile(dialect=postgresql.dialect()))
        x # %(x_1)s
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_rshift`, :meth:`_sql.ColumnOperators.bitwise_lshift`
      生成位右移和左移运算符::
    
        >>> print(column("x").bitwise_rshift(5))
        x >> :x_1
        >>> print(column("x").bitwise_lshift(5))
        x << :x_1

.. tab:: 英文

    Bitwise operator functions provide uniform access to bitwise operators across
    different backends, which are expected to operate on compatible
    values such as integers and bit-strings (e.g. PostgreSQL
    :class:`_postgresql.BIT` and similar). Note that these are **not** general
    boolean operators.
    
    .. versionadded:: 2.0.2 Added dedicated operators for bitwise operations.
    
    * :meth:`_sql.ColumnOperators.bitwise_not`, :func:`_sql.bitwise_not`.
      Available as a column-level method, producing a bitwise NOT clause against a
      parent object::
    
        >>> print(column("x").bitwise_not())
        ~x
    
      This operator is also available as a column-expression-level method, applying
      bitwise NOT to an individual column expression::
    
        >>> from sqlalchemy import bitwise_not
        >>> print(bitwise_not(column("x")))
        ~x
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_and` produces bitwise AND::
    
        >>> print(column("x").bitwise_and(5))
        x & :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_or` produces bitwise OR::
    
        >>> print(column("x").bitwise_or(5))
        x | :x_1
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_xor` produces bitwise XOR::
    
        >>> print(column("x").bitwise_xor(5))
        x ^ :x_1
    
      For PostgreSQL dialects, "#" is used to represent bitwise XOR; this emits
      automatically when using one of these backends::
    
        >>> from sqlalchemy.dialects import postgresql
        >>> print(column("x").bitwise_xor(5).compile(dialect=postgresql.dialect()))
        x # %(x_1)s
    
      ..
    
    * :meth:`_sql.ColumnOperators.bitwise_rshift`, :meth:`_sql.ColumnOperators.bitwise_lshift`
      produce bitwise shift operators::
    
        >>> print(column("x").bitwise_rshift(5))
        x >> :x_1
        >>> print(column("x").bitwise_lshift(5))
        x << :x_1

  ..


使用连接和否定
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Conjunctions and Negations

.. tab:: 中文

    最常见的连接词 "AND" 会在多次调用 :meth:`_sql.Select.where` 方法时自动应用，
    同样适用于类似的方法，如 :meth:`_sql.Update.where` 和 :meth:`_sql.Delete.where`::
    
        >>> print(
        ...     select(address_table.c.email_address)
        ...     .where(user_table.c.name == "squidward")
        ...     .where(address_table.c.user_id == user_table.c.id)
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id
    
    :meth:`_sql.Select.where`、:meth:`_sql.Update.where` 和 :meth:`_sql.Delete.where`
    也支持传入多个表达式参数，并具有相同的效果::
    
        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         user_table.c.name == "squidward",
        ...         address_table.c.user_id == user_table.c.id,
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id
    
    连接词 "AND" 及其搭档 "OR" 都可以通过 :func:`_sql.and_` 和 :func:`_sql.or_` 函数直接使用::
    
        >>> from sqlalchemy import and_, or_
        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         and_(
        ...             or_(user_table.c.name == "squidward", user_table.c.name == "sandy"),
        ...             address_table.c.user_id == user_table.c.id,
        ...         )
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE (user_account.name = :name_1 OR user_account.name = :name_2)
        AND address.user_id = user_account.id
    
    可以使用 :func:`_sql.not_` 函数进行逻辑非（否定）操作。该函数通常会反转布尔表达式中的运算符::
    
        >>> from sqlalchemy import not_
        >>> print(not_(column("x") == 5))
        {printsql}x != :x_1
    
    在合适的情况下，它也可能应用 ``NOT`` 关键字::
    
        >>> from sqlalchemy import Boolean
        >>> print(not_(column("x", Boolean)))
        {printsql}NOT x

.. tab:: 英文

    The most common conjunction, "AND", is automatically applied if we make repeated use of the :meth:`_sql.Select.where` method, as well as similar methods such as
    :meth:`_sql.Update.where` and :meth:`_sql.Delete.where`::
    
        >>> print(
        ...     select(address_table.c.email_address)
        ...     .where(user_table.c.name == "squidward")
        ...     .where(address_table.c.user_id == user_table.c.id)
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id
    
    :meth:`_sql.Select.where`, :meth:`_sql.Update.where` and :meth:`_sql.Delete.where` also accept multiple expressions with the same effect::
    
        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         user_table.c.name == "squidward",
        ...         address_table.c.user_id == user_table.c.id,
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id
    
    The "AND" conjunction, as well as its partner "OR", are both available directly using the :func:`_sql.and_` and :func:`_sql.or_` functions::
    
    
        >>> from sqlalchemy import and_, or_
        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         and_(
        ...             or_(user_table.c.name == "squidward", user_table.c.name == "sandy"),
        ...             address_table.c.user_id == user_table.c.id,
        ...         )
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE (user_account.name = :name_1 OR user_account.name = :name_2)
        AND address.user_id = user_account.id
    
    A negation is available using the :func:`_sql.not_` function.  This will
    typically invert the operator in a boolean expression::
    
        >>> from sqlalchemy import not_
        >>> print(not_(column("x") == 5))
        {printsql}x != :x_1
    
    It also may apply a keyword such as ``NOT`` when appropriate::
    
        >>> from sqlalchemy import Boolean
        >>> print(not_(column("x", Boolean)))
        {printsql}NOT x


连接运算符
^^^^^^^^^^^^^^^^^^^^^^

Conjunction Operators

.. tab:: 中文
    
    上述连接函数 :func:`_sql.and_`、:func:`_sql.or_` 和 :func:`_sql.not_` 也可以通过 Python 的运算符重载形式使用：
    
    .. note:: Python 中的 ``&`` 、 ``|`` 和 ``~`` 运算符具有较高的优先级；
       因此，对于包含表达式的操作数，通常需要添加括号，如下方示例所示。
    
    * :meth:`_sql.Operators.__and__` （Python "``&``" 运算符）：
    
      Python 的 ``&`` 运算符被重载，行为等同于 :func:`_sql.and_` （注意操作数使用括号）::
    
         >>> print((column("x") == 5) & (column("y") == 10))
         {printsql}x = :x_1 AND y = :y_1
    
      ..
    
    * :meth:`_sql.Operators.__or__` （Python "``|``" 运算符）：
    
      Python 的 ``|`` 运算符被重载，行为等同于 :func:`_sql.or_` （注意操作数使用括号）::
    
        >>> print((column("x") == 5) | (column("y") == 10))
        {printsql}x = :x_1 OR y = :y_1
    
      ..
    
    * :meth:`_sql.Operators.__invert__` （Python "``~``" 运算符）：
    
      Python 的 ``~`` 运算符被重载，行为等同于 :func:`_sql.not_`，可以反转已有运算符，
      或对整个表达式应用 ``NOT`` 关键字::
    
        >>> print(~(column("x") == 5))
        {printsql}x != :x_1{stop}
    
        >>> from sqlalchemy import Boolean
        >>> print(~column("x", Boolean))
        {printsql}NOT x{stop}
    
      ..
    
    ..  初始化代码，仅用于设置，不作展示
    
        >>> conn.close()
        ROLLBACK

.. tab:: 英文

    The above conjunction functions :func:`_sql.and_`, :func:`_sql.or_`,
    :func:`_sql.not_` are also available as overloaded Python operators:
    
    .. note:: The Python ``&``, ``|`` and ``~`` operators take high precedence
       in the language; as a result, parenthesis must usually be applied
       for operands that themselves contain expressions, as indicated in the
       examples below.
    
    * :meth:`_sql.Operators.__and__` (Python "``&``" operator):
    
      The Python binary ``&`` operator is overloaded to behave the same
      as :func:`_sql.and_` (note parenthesis around the two operands)::
    
         >>> print((column("x") == 5) & (column("y") == 10))
         {printsql}x = :x_1 AND y = :y_1
    
      ..
    
    
    * :meth:`_sql.Operators.__or__` (Python "``|``" operator):
    
      The Python binary ``|`` operator is overloaded to behave the same
      as :func:`_sql.or_` (note parenthesis around the two operands)::
    
        >>> print((column("x") == 5) | (column("y") == 10))
        {printsql}x = :x_1 OR y = :y_1
    
      ..
    
    
    * :meth:`_sql.Operators.__invert__` (Python "``~``" operator):
    
      The Python binary ``~`` operator is overloaded to behave the same
      as :func:`_sql.not_`, either inverting the existing operator, or
      applying the ``NOT`` keyword to the expression as a whole::
    
        >>> print(~(column("x") == 5))
        {printsql}x != :x_1{stop}
    
        >>> from sqlalchemy import Boolean
        >>> print(~column("x", Boolean))
        {printsql}NOT x{stop}
    
      ..
    
    ..  Setup code, not for display
    
        >>> conn.close()
        ROLLBACK
