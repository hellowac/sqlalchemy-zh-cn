.. highlight:: pycon+sql

.. |prev| replace:: :doc:`data_insert`
.. |next| replace:: :doc:`data_update`

.. include:: tutorial_nav_include.rst

.. _tutorial_selecting_data:

.. rst-class:: core-header, orm-dependency

使用 SELECT 语句
-----------------------

Using SELECT Statements

.. tab:: 中文

    对于 Core 和 ORM，:func:`_sql.select` 函数生成一个 :class:`_sql.Select` 构造，用于所有 SELECT 查询。
    在 Core 中传递给 :meth:`_engine.Connection.execute` 方法，在 ORM 中传递给 :meth:`_orm.Session.execute` 方法，在当前事务中发出一个 SELECT 语句，并通过返回的 :class:`_engine.Result` 对象获取结果行。

    .. container:: orm-header

        **ORM 读者** - 这里的内容同样适用于 Core 和 ORM 的使用，并且提到了基本的 ORM 变体用例。然而，还有更多特定于 ORM 的功能；这些记录在 :ref:`queryguide_toplevel`。

.. tab:: 英文

    For both Core and ORM, the :func:`_sql.select` function generates a
    :class:`_sql.Select` construct which is used for all SELECT queries.
    Passed to methods like :meth:`_engine.Connection.execute` in Core and
    :meth:`_orm.Session.execute` in ORM, a SELECT statement is emitted in the
    current transaction and the result rows available via the returned
    :class:`_engine.Result` object.

    .. container:: orm-header

        **ORM Readers** - the content here applies equally well to both Core and ORM
        use and basic ORM variant use cases are mentioned here.  However there are
        a lot more ORM-specific features available as well; these are documented
        at :ref:`queryguide_toplevel`.


select() SQL 表达式构造
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The select() SQL Expression Construct

.. tab:: 中文

    :func:`_sql.select` 构造的语句构建方式与 :func:`_sql.insert` 类似，使用 :term:`generative` 方法，其中每个方法在对象上构建更多状态。与其他 SQL 构造一样，它可以直接字符串化::

        >>> from sqlalchemy import select
        >>> stmt = select(user_table).where(user_table.c.name == "spongebob")
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1

    与所有其他语句级 SQL 构造相同，要实际运行该语句，我们将其传递给执行方法。由于 SELECT 语句返回行，我们始终可以迭代结果对象以获取 :class:`_engine.Row` 对象：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     for row in conn.execute(stmt):
        ...         print(row)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        (1, 'spongebob', 'Spongebob Squarepants')
        {execsql}ROLLBACK{stop}

    使用 ORM 时，特别是对于针对 ORM 实体构建的 :func:`_sql.select` 构造，我们需要使用 :class:`_orm.Session` 上的 :meth:`_orm.Session.execute` 方法来执行它；使用这种方法，我们继续从结果中获取 :class:`_engine.Row` 对象，但是这些行现在能够包括完整的实体，例如 ``User`` 类的实例，作为每行中的单个元素：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User).where(User.name == "spongebob")
        >>> with Session(engine) as session:
        ...     for row in session.execute(stmt):
        ...         print(row)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)
        {execsql}ROLLBACK{stop}

    .. topic:: select() from a Table vs. ORM class

        尽管这些示例中生成的 SQL 看起来相同，无论我们调用 ``select(user_table)`` 还是 ``select(User)``，但在更一般的情况下，它们不一定渲染相同的内容，因为 ORM 映射类可能映射到表之外的其他类型的“可选对象”。针对 ORM 实体的 ``select()`` 还表明结果中应返回 ORM 映射实例，而从 :class:`_schema.Table` 对象中 SELECT 时则不然。

    以下部分将更详细地讨论 SELECT 构造。

.. tab:: 英文

    The :func:`_sql.select` construct builds up a statement in the same way
    as that of :func:`_sql.insert`, using a :term:`generative` approach where
    each method builds more state onto the object.  Like the other SQL constructs,
    it can be stringified in place::

        >>> from sqlalchemy import select
        >>> stmt = select(user_table).where(user_table.c.name == "spongebob")
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1

    Also in the same manner as all other statement-level SQL constructs, to
    actually run the statement we pass it to an execution method.
    Since a SELECT statement returns
    rows we can always iterate the result object to get :class:`_engine.Row`
    objects back:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     for row in conn.execute(stmt):
        ...         print(row)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        (1, 'spongebob', 'Spongebob Squarepants')
        {execsql}ROLLBACK{stop}

    When using the ORM, particularly with a :func:`_sql.select` construct that's
    composed against ORM entities, we will want to execute it using the
    :meth:`_orm.Session.execute` method on the :class:`_orm.Session`; using
    this approach, we continue to get :class:`_engine.Row` objects from the
    result, however these rows are now capable of including
    complete entities, such as instances of the ``User`` class, as individual
    elements within each row:

    .. sourcecode:: pycon+sql

        >>> stmt = select(User).where(User.name == "spongebob")
        >>> with Session(engine) as session:
        ...     for row in session.execute(stmt):
        ...         print(row)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)
        {execsql}ROLLBACK{stop}

    .. topic:: select() from a Table vs. ORM class

        While the SQL generated in these examples looks the same whether we invoke
        ``select(user_table)`` or ``select(User)``, in the more general case
        they do not necessarily render the same thing, as an ORM-mapped class
        may be mapped to other kinds of "selectables" besides tables.  The
        ``select()`` that's against an ORM entity also indicates that ORM-mapped
        instances should be returned in a result, which is not the case when
        SELECTing from a :class:`_schema.Table` object.

    The following sections will discuss the SELECT construct in more detail.

.. _tutorial_selecting_columns:

设置 COLUMNS 和 FROM 子句
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting the COLUMNS and FROM clause

.. tab:: 中文

    :func:`_sql.select` 函数接受表示任意数量的 :class:`_schema.Column` 和/或 :class:`_schema.Table` 表达式的位置元素，以及广泛的兼容对象，这些对象被解析为要从中 SELECT 的 SQL 表达式列表，这些表达式将作为结果集中返回的列。这些元素在更简单的情况下也用于创建 FROM 子句，该子句是从传递的列和类似表的表达式推断出来的::

        >>> print(select(user_table))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account

    要使用 Core 方法从单个列 SELECT，:class:`_schema.Column` 对象从 :attr:`_schema.Table.c` 访问器访问并可以直接发送；FROM 子句将被推断为那些列所代表的所有 :class:`_schema.Table` 和其他 :class:`_sql.FromClause` 对象的集合::

        >>> print(select(user_table.c.name, user_table.c.fullname))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    或者，当使用任何 :class:`.FromClause` （如 :class:`.Table`）的 :attr:`.FromClause.c` 集合时，可以通过使用字符串名称的元组为 :func:`_sql.select` 指定多个列::

        >>> print(select(user_table.c["name", "fullname"]))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    .. versionadded:: 2.0 
        
        为 :attr:`.FromClause.c` 集合添加了元组访问器功能

.. tab:: 英文

    The :func:`_sql.select` function accepts positional elements representing any
    number of :class:`_schema.Column` and/or :class:`_schema.Table` expressions, as
    well as a wide range of compatible objects, which are resolved into a list of SQL
    expressions to be SELECTed from that will be returned as columns in the result
    set.  These elements also serve in simpler cases to create the FROM clause,
    which is inferred from the columns and table-like expressions passed::

        >>> print(select(user_table))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account

    To SELECT from individual columns using a Core approach,
    :class:`_schema.Column` objects are accessed from the :attr:`_schema.Table.c`
    accessor and can be sent directly; the FROM clause will be inferred as the set
    of all :class:`_schema.Table` and other :class:`_sql.FromClause` objects that
    are represented by those columns::

        >>> print(select(user_table.c.name, user_table.c.fullname))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    Alternatively, when using the :attr:`.FromClause.c` collection of any
    :class:`.FromClause` such as :class:`.Table`, multiple columns may be specified
    for a :func:`_sql.select` by using a tuple of string names::

        >>> print(select(user_table.c["name", "fullname"]))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    .. versionadded:: 2.0 
        
        Added tuple-accessor capability to the :attr:`.FromClause.c` collection


.. _tutorial_selecting_orm_entities:

选择 ORM 实体和列
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selecting ORM Entities and Columns

.. tab:: 中文

    ORM 实体，如我们的 ``User`` 类以及它上面映射到列的属性如 ``User.name``，也参与表示表和列的 SQL 表达式语言系统。下面展示了一个从 ``User`` 实体中 SELECT 的示例，最终呈现的方式与我们直接使用 ``user_table`` 一样：

        >>> print(select(User))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account

    当使用 ORM :meth:`_orm.Session.execute` 方法执行如上语句时，与从 ``user_table`` 中 SELECT 相比，有一个重要的区别，即 **实体本身作为每行中的单个元素返回**。也就是说，当我们从上述语句中获取行时，由于要获取的内容列表中只有 ``User`` 实体，我们返回的 :class:`_engine.Row` 对象只有一个元素，其中包含 ``User`` 类的实例：

        >>> row = session.execute(select(User)).first()
        {execsql}BEGIN...
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> row
        (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)

    上述 :class:`_engine.Row` 只有一个元素，表示 ``User`` 实体：

        >>> row[0]
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')

    一种强烈推荐的实现上述相同结果的便捷方法是直接使用 :meth:`_orm.Session.scalars` 方法执行语句；该方法将返回一个 :class:`_result.ScalarResult` 对象，该对象一次提供每行的第一个“列”，在这种情况下，是 ``User`` 类的实例：

        >>> user = session.scalars(select(User)).first()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> user
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')


    或者，我们可以选择 ORM 实体的单个列作为结果行中的独立元素，通过使用类绑定的属性；当这些属性传递给诸如 :func:`_sql.select` 之类的构造时，它们将解析为每个属性表示的 :class:`_schema.Column` 或其他 SQL 表达式：

        >>> print(select(User.name, User.fullname))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    当我们使用 :meth:`_orm.Session.execute` 调用*这个*语句时，我们现在收到的行对于每个值都有单独的元素，每个元素对应一个单独的列或其他 SQL 表达式：

        >>> row = session.execute(select(User.name, User.fullname)).first()
        {execsql}SELECT user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> row
        ('spongebob', 'Spongebob Squarepants')

    这些方法也可以混合使用，如下所示，我们将 ``User`` 实体的 ``name`` 属性作为行的第一个元素，并将完整的 ``Address`` 实体作为第二个元素：

        >>> session.execute(
        ...     select(User.name, Address).where(User.id == Address.user_id).order_by(Address.id)
        ... ).all()
        {execsql}SELECT user_account.name, address.id, address.email_address, address.user_id
        FROM user_account, address
        WHERE user_account.id = address.user_id ORDER BY address.id
        [...] (){stop}
        [('spongebob', Address(id=1, email_address='spongebob@sqlalchemy.org')),
        ('sandy', Address(id=2, email_address='sandy@sqlalchemy.org')),
        ('sandy', Address(id=3, email_address='sandy@squirrelpower.org'))]

    选择 ORM 实体和列的方法以及将行转换为常见方法将在 :ref:`orm_queryguide_select_columns` 中进一步讨论。

    .. seealso::

        :ref:`orm_queryguide_select_columns` - 在 :ref:`queryguide_toplevel` 中

.. tab:: 英文

    ORM entities, such our ``User`` class as well as the column-mapped
    attributes upon it such as ``User.name``, also participate in the SQL Expression
    Language system representing tables and columns.    Below illustrates an
    example of SELECTing from the ``User`` entity, which ultimately renders
    in the same way as if we had used ``user_table`` directly::

        >>> print(select(User))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account

    When executing a statement like the above using the ORM :meth:`_orm.Session.execute`
    method, there is an important difference when we select from a full entity
    such as ``User``, as opposed to ``user_table``, which is that the **entity
    itself is returned as a single element within each row**.  That is, when we fetch rows from
    the above statement, as there is only the ``User`` entity in the list of
    things to fetch, we get back :class:`_engine.Row` objects that have only one element, which contain
    instances of the ``User`` class::

        >>> row = session.execute(select(User)).first()
        {execsql}BEGIN...
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> row
        (User(id=1, name='spongebob', fullname='Spongebob Squarepants'),)

    The above :class:`_engine.Row` has just one element, representing the ``User`` entity::

        >>> row[0]
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')

    A highly recommended convenience method of achieving the same result as above
    is to use the :meth:`_orm.Session.scalars` method to execute the statement
    directly; this method will return a :class:`_result.ScalarResult` object
    that delivers the first "column" of each row at once, in this case,
    instances of the ``User`` class::

        >>> user = session.scalars(select(User)).first()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> user
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')


    Alternatively, we can select individual columns of an ORM entity as distinct
    elements within result rows, by using the class-bound attributes; when these
    are passed to a construct such as :func:`_sql.select`, they are resolved into
    the :class:`_schema.Column` or other SQL expression represented by each
    attribute::

        >>> print(select(User.name, User.fullname))
        {printsql}SELECT user_account.name, user_account.fullname
        FROM user_account

    When we invoke *this* statement using :meth:`_orm.Session.execute`, we now
    receive rows that have individual elements per value, each corresponding
    to a separate column or other SQL expression::

        >>> row = session.execute(select(User.name, User.fullname)).first()
        {execsql}SELECT user_account.name, user_account.fullname
        FROM user_account
        [...] (){stop}
        >>> row
        ('spongebob', 'Spongebob Squarepants')

    The approaches can also be mixed, as below where we SELECT the ``name``
    attribute of the ``User`` entity as the first element of the row, and combine
    it with full ``Address`` entities in the second element::

        >>> session.execute(
        ...     select(User.name, Address).where(User.id == Address.user_id).order_by(Address.id)
        ... ).all()
        {execsql}SELECT user_account.name, address.id, address.email_address, address.user_id
        FROM user_account, address
        WHERE user_account.id = address.user_id ORDER BY address.id
        [...] (){stop}
        [('spongebob', Address(id=1, email_address='spongebob@sqlalchemy.org')),
        ('sandy', Address(id=2, email_address='sandy@sqlalchemy.org')),
        ('sandy', Address(id=3, email_address='sandy@squirrelpower.org'))]

    Approaches towards selecting ORM entities and columns as well as common methods
    for converting rows are discussed further at :ref:`orm_queryguide_select_columns`.

    .. seealso::

        :ref:`orm_queryguide_select_columns` - in the :ref:`queryguide_toplevel`

从带标签的 SQL 表达式中选择
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selecting from Labeled SQL Expressions

.. tab:: 中文

    :meth:`_sql.ColumnElement.label` 方法以及 ORM 属性上相同名称的方法提供了列或表达式的 SQL 标签，使其在结果集中具有特定名称。这在按名称引用结果行中的任意 SQL 表达式时非常有用：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import func, cast
        >>> stmt = select(
        ...     ("Username: " + user_table.c.name).label("username"),
        ... ).order_by(user_table.c.name)
        >>> with engine.connect() as conn:
        ...     for row in conn.execute(stmt):
        ...         print(f"{row.username}")
        {execsql}BEGIN (implicit)
        SELECT ? || user_account.name AS username
        FROM user_account ORDER BY user_account.name
        [...] ('Username: ',){stop}
        Username: patrick
        Username: sandy
        Username: spongebob
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`tutorial_order_by_label` - 我们创建的标签名称也可以在 :class:`_sql.Select` 的 ORDER BY 或 GROUP BY 子句中引用。

.. tab:: 英文

    The :meth:`_sql.ColumnElement.label` method as well as the same-named method
    available on ORM attributes provides a SQL label of a column or expression,
    allowing it to have a specific name in a result set.  This can be helpful
    when referring to arbitrary SQL expressions in a result row by name:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import func, cast
        >>> stmt = select(
        ...     ("Username: " + user_table.c.name).label("username"),
        ... ).order_by(user_table.c.name)
        >>> with engine.connect() as conn:
        ...     for row in conn.execute(stmt):
        ...         print(f"{row.username}")
        {execsql}BEGIN (implicit)
        SELECT ? || user_account.name AS username
        FROM user_account ORDER BY user_account.name
        [...] ('Username: ',){stop}
        Username: patrick
        Username: sandy
        Username: spongebob
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`tutorial_order_by_label` - the label names we create may also be
        referenced in the ORDER BY or GROUP BY clause of the :class:`_sql.Select`.

.. _tutorial_select_arbitrary_text:

使用文本列表达式进行选择
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selecting with Textual Column Expressions

.. tab:: 中文

    当我们使用 :func:`_sql.select` 函数构造 :class:`_sql.Select` 对象时，通常会传递一系列使用 :ref:`table metadata <tutorial_working_with_metadata>` 定义的 :class:`_schema.Table` 和 :class:`_schema.Column` 对象，或者在使用 ORM 时，我们可能会发送表示表列的 ORM 映射属性。然而，有时也需要在语句中制造任意 SQL 块，例如常量字符串表达式，或者只是一些更快地直接编写的任意 SQL。

    在 :ref:`tutorial_working_with_transactions` 中介绍的 :func:`_sql.text` 构造实际上可以直接嵌入到 :class:`_sql.Select` 构造中，例如下面我们制造一个硬编码字符串字面量 ``'some phrase'`` 并将其嵌入到 SELECT 语句中::

    >>> from sqlalchemy import text
    >>> stmt = select(text("'some phrase'"), user_table.c.name).order_by(user_table.c.name)
    >>> with engine.connect() as conn:
    ...     print(conn.execute(stmt).all())
    {execsql}BEGIN (implicit)
    SELECT 'some phrase', user_account.name
    FROM user_account ORDER BY user_account.name
    [generated in ...] ()
    {stop}[('some phrase', 'patrick'), ('some phrase', 'sandy'), ('some phrase', 'spongebob')]
    {execsql}ROLLBACK{stop}

    虽然 :func:`_sql.text` 构造可以在大多数地方用于注入字面 SQL 短语，但更多时候我们实际上在处理每个表示单个列表达式的文本单元。在这种常见情况下，我们可以使用 :func:`_sql.literal_column` 构造从我们的文本片段中获得更多功能。此对象类似于 :func:`_sql.text`，但它明确表示单个“列”，然后可以在子查询和其他表达式中标记和引用::

    >>> from sqlalchemy import literal_column
    >>> stmt = select(literal_column("'some phrase'").label("p"), user_table.c.name).order_by(
    ...     user_table.c.name
    ... )
    >>> with engine.connect() as conn:
    ...     for row in conn.execute(stmt):
    ...         print(f"{row.p}, {row.name}")
    {execsql}BEGIN (implicit)
    SELECT 'some phrase' AS p, user_account.name
    FROM user_account ORDER BY user_account.name
    [generated in ...] ()
    {stop}some phrase, patrick
    some phrase, sandy
    some phrase, spongebob
    {execsql}ROLLBACK{stop}

    请注意，在两种情况下，当使用 :func:`_sql.text` 或 :func:`_sql.literal_column` 时，我们正在编写一个语法 SQL 表达式，而不是一个字面值。因此，我们必须包括所需的任何引用或语法以呈现我们希望看到的 SQL。

.. tab:: 英文

    When we construct a :class:`_sql.Select` object using the :func:`_sql.select`
    function, we are normally passing to it a series of :class:`_schema.Table`
    and :class:`_schema.Column` objects that were defined using
    :ref:`table metadata <tutorial_working_with_metadata>`, or when using the ORM we may be
    sending ORM-mapped attributes that represent table columns.   However,
    sometimes there is also the need to manufacture arbitrary SQL blocks inside
    of statements, such as constant string expressions, or just some arbitrary
    SQL that's quicker to write literally.

    The :func:`_sql.text` construct introduced at
    :ref:`tutorial_working_with_transactions` can in fact be embedded into a
    :class:`_sql.Select` construct directly, such as below where we manufacture
    a hardcoded string literal ``'some phrase'`` and embed it within the
    SELECT statement::

    >>> from sqlalchemy import text
    >>> stmt = select(text("'some phrase'"), user_table.c.name).order_by(user_table.c.name)
    >>> with engine.connect() as conn:
    ...     print(conn.execute(stmt).all())
    {execsql}BEGIN (implicit)
    SELECT 'some phrase', user_account.name
    FROM user_account ORDER BY user_account.name
    [generated in ...] ()
    {stop}[('some phrase', 'patrick'), ('some phrase', 'sandy'), ('some phrase', 'spongebob')]
    {execsql}ROLLBACK{stop}

    While the :func:`_sql.text` construct can be used in most places to inject
    literal SQL phrases, more often than not we are actually dealing with textual
    units that each represent an individual
    column expression.  In this common case we can get more functionality out of
    our textual fragment using the :func:`_sql.literal_column`
    construct instead.  This object is similar to :func:`_sql.text` except that
    instead of representing arbitrary SQL of any form,
    it explicitly represents a single "column" and can then be labeled and referred
    towards in subqueries and other expressions::


    >>> from sqlalchemy import literal_column
    >>> stmt = select(literal_column("'some phrase'").label("p"), user_table.c.name).order_by(
    ...     user_table.c.name
    ... )
    >>> with engine.connect() as conn:
    ...     for row in conn.execute(stmt):
    ...         print(f"{row.p}, {row.name}")
    {execsql}BEGIN (implicit)
    SELECT 'some phrase' AS p, user_account.name
    FROM user_account ORDER BY user_account.name
    [generated in ...] ()
    {stop}some phrase, patrick
    some phrase, sandy
    some phrase, spongebob
    {execsql}ROLLBACK{stop}


    Note that in both cases, when using :func:`_sql.text` or
    :func:`_sql.literal_column`, we are writing a syntactical SQL expression, and
    not a literal value. We therefore have to include whatever quoting or syntaxes
    are necessary for the SQL we want to see rendered.

.. _tutorial_select_where_clause:

WHERE 子句
^^^^^^^^^^^^^^^^

The WHERE clause

.. tab:: 中文

    SQLAlchemy 允许我们通过使用标准的 Python 运算符与 :class:`_schema.Column` 和类似对象结合来组合 SQL 表达式，例如 ``name = 'squidward'`` 或 ``user_id > 10`` 。对于布尔表达式，大多数 Python 运算符如 ``==``、 ``!=``、 ``<``、 ``>=`` 等生成新的 SQL 表达式对象，而不是普通的布尔 ``True`` / ``False`` 值::

        >>> print(user_table.c.name == "squidward")
        user_account.name = :name_1

        >>> print(address_table.c.user_id > 10)
        address.user_id > :user_id_1


    我们可以使用这些表达式通过将结果对象传递给 :meth:`_sql.Select.where` 方法来生成 WHERE 子句::

        >>> print(select(user_table).where(user_table.c.name == "squidward"))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1


    要生成由 AND 连接的多个表达式，可以多次调用 :meth:`_sql.Select.where` 方法::

        >>> print(
        ...     select(address_table.c.email_address)
        ...     .where(user_table.c.name == "squidward")
        ...     .where(address_table.c.user_id == user_table.c.id)
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id

    对 :meth:`_sql.Select.where` 的单次调用也接受多个表达式，效果相同::

        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         user_table.c.name == "squidward",
        ...         address_table.c.user_id == user_table.c.id,
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id

    "AND" 和 "OR" 连接可以直接使用 :func:`_sql.and_` 和 :func:`_sql.or_` 函数，如下所示，以 ORM 实体为例::

        >>> from sqlalchemy import and_, or_
        >>> print(
        ...     select(Address.email_address).where(
        ...         and_(
        ...             or_(User.name == "squidward", User.name == "sandy"),
        ...             Address.user_id == User.id,
        ...         )
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE (user_account.name = :name_1 OR user_account.name = :name_2)
        AND address.user_id = user_account.id

    对于针对单个实体的简单“相等”比较，还有一种流行的方法称为 :meth:`_sql.Select.filter_by`，它接受与列键或 ORM 属性名称匹配的关键字参数。它将过滤最左侧的 FROM 子句或最后一个连接的实体::

        >>> print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1 AND user_account.fullname = :fullname_1


    .. seealso::

        :doc:`/core/operators` - SQLAlchemy 中大多数 SQL 运算符函数的描述

.. tab:: 英文

    SQLAlchemy allows us to compose SQL expressions, such as ``name = 'squidward'``
    or ``user_id > 10``, by making use of standard Python operators in
    conjunction with
    :class:`_schema.Column` and similar objects.   For boolean expressions, most
    Python operators such as ``==``, ``!=``, ``<``, ``>=`` etc. generate new
    SQL Expression objects, rather than plain boolean ``True``/``False`` values::

        >>> print(user_table.c.name == "squidward")
        user_account.name = :name_1

        >>> print(address_table.c.user_id > 10)
        address.user_id > :user_id_1


    We can use expressions like these to generate the WHERE clause by passing
    the resulting objects to the :meth:`_sql.Select.where` method::

        >>> print(select(user_table).where(user_table.c.name == "squidward"))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1


    To produce multiple expressions joined by AND, the :meth:`_sql.Select.where`
    method may be invoked any number of times::

        >>> print(
        ...     select(address_table.c.email_address)
        ...     .where(user_table.c.name == "squidward")
        ...     .where(address_table.c.user_id == user_table.c.id)
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id

    A single call to :meth:`_sql.Select.where` also accepts multiple expressions
    with the same effect::

        >>> print(
        ...     select(address_table.c.email_address).where(
        ...         user_table.c.name == "squidward",
        ...         address_table.c.user_id == user_table.c.id,
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE user_account.name = :name_1 AND address.user_id = user_account.id

    "AND" and "OR" conjunctions are both available directly using the
    :func:`_sql.and_` and :func:`_sql.or_` functions, illustrated below in terms
    of ORM entities::

        >>> from sqlalchemy import and_, or_
        >>> print(
        ...     select(Address.email_address).where(
        ...         and_(
        ...             or_(User.name == "squidward", User.name == "sandy"),
        ...             Address.user_id == User.id,
        ...         )
        ...     )
        ... )
        {printsql}SELECT address.email_address
        FROM address, user_account
        WHERE (user_account.name = :name_1 OR user_account.name = :name_2)
        AND address.user_id = user_account.id

    For simple "equality" comparisons against a single entity, there's also a
    popular method known as :meth:`_sql.Select.filter_by` which accepts keyword
    arguments that match to column keys or ORM attribute names.  It will filter
    against the leftmost FROM clause or the last entity joined::

        >>> print(select(User).filter_by(name="spongebob", fullname="Spongebob Squarepants"))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = :name_1 AND user_account.fullname = :fullname_1


    .. seealso::


        :doc:`/core/operators` - descriptions of most SQL operator functions in SQLAlchemy


.. _tutorial_select_join:

显式 FROM 子句和 JOIN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Explicit FROM clauses and JOINs

.. tab:: 中文

    正如前面提到的，FROM 子句通常是根据我们在列子句中设置的表达式以及 :class:`_sql.Select` 的其他元素推断出来的。

    如果我们在 COLUMNS 子句中设置了某个 :class:`_schema.Table` 的单列，它也会将该 :class:`_schema.Table` 放入 FROM 子句中::

        >>> print(select(user_table.c.name))
        {printsql}SELECT user_account.name
        FROM user_account

    如果我们将两个表的列放在一起，那么我们会得到一个逗号分隔的 FROM 子句::

        >>> print(select(user_table.c.name, address_table.c.email_address))
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account, address

    为了将这两个表连接在一起，我们通常使用 :class:`_sql.Select` 上的两种方法之一。第一种是 :meth:`_sql.Select.join_from` 方法，它允许我们明确表示 JOIN 的左侧和右侧::

        >>> print(
        ...     select(user_table.c.name, address_table.c.email_address).join_from(
        ...         user_table, address_table
        ...     )
        ... )
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id


    另一种是 :meth:`_sql.Select.join` 方法，它只表示 JOIN 的右侧，左侧是推断出来的::

        >>> print(select(user_table.c.name, address_table.c.email_address).join(address_table))
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    .. sidebar:: ON 子句是推断出来的

        使用 :meth:`_sql.Select.join_from` 或 :meth:`_sql.Select.join` 时，我们可能会注意到在简单的外键情况下，JOIN 的 ON 子句也是为我们推断出来的。更多内容将在下一节中介绍。

    我们也可以选择显式地将元素添加到 FROM 子句中，如果它不是我们希望从列子句中推断出来的那样。我们使用 :meth:`_sql.Select.select_from` 方法来实现这一点，如下所示，我们将 ``user_table`` 作为 FROM 子句中的第一个元素，并使用 :meth:`_sql.Select.join` 将 ``address_table`` 作为第二个元素::

        >>> print(select(address_table.c.email_address).select_from(user_table).join(address_table))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    另一个我们可能希望使用 :meth:`_sql.Select.select_from` 的示例是，如果我们的列子句没有足够的信息来提供 FROM 子句。例如，要从常见的 SQL 表达式 ``count(*)`` 中 SELECT，我们使用一个称为 :attr:`_sql.func` 的 SQLAlchemy 元素来生成 SQL ``count()`` 函数::

        >>> from sqlalchemy import func
        >>> print(select(func.count("*")).select_from(user_table))
        {printsql}SELECT count(:count_2) AS count_1
        FROM user_account

    .. seealso::

        :ref:`orm_queryguide_select_from` - 在 :ref:`queryguide_toplevel` 中 -
        包含更多示例和注释，讨论 :meth:`_sql.Select.select_from` 和
        :meth:`_sql.Select.join` 的交互。

.. tab:: 英文

    As mentioned previously, the FROM clause is usually **inferred**
    based on the expressions that we are setting in the columns
    clause as well as other elements of the :class:`_sql.Select`.

    If we set a single column from a particular :class:`_schema.Table`
    in the COLUMNS clause, it puts that :class:`_schema.Table` in the FROM
    clause as well::

        >>> print(select(user_table.c.name))
        {printsql}SELECT user_account.name
        FROM user_account

    If we were to put columns from two tables, then we get a comma-separated FROM
    clause::

        >>> print(select(user_table.c.name, address_table.c.email_address))
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account, address

    In order to JOIN these two tables together, we typically use one of two methods
    on :class:`_sql.Select`.  The first is the :meth:`_sql.Select.join_from`
    method, which allows us to indicate the left and right side of the JOIN
    explicitly::

        >>> print(
        ...     select(user_table.c.name, address_table.c.email_address).join_from(
        ...         user_table, address_table
        ...     )
        ... )
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id


    The other is the :meth:`_sql.Select.join` method, which indicates only the
    right side of the JOIN, the left hand-side is inferred::

        >>> print(select(user_table.c.name, address_table.c.email_address).join(address_table))
        {printsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    .. sidebar::  The ON Clause is inferred

        When using :meth:`_sql.Select.join_from` or :meth:`_sql.Select.join`, we may
        observe that the ON clause of the join is also inferred for us in simple
        foreign key cases. More on that in the next section.

    We also have the option to add elements to the FROM clause explicitly, if it is not
    inferred the way we want from the columns clause.  We use the
    :meth:`_sql.Select.select_from` method to achieve this, as below
    where we establish ``user_table`` as the first element in the FROM
    clause and :meth:`_sql.Select.join` to establish ``address_table`` as
    the second::

        >>> print(select(address_table.c.email_address).select_from(user_table).join(address_table))
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    Another example where we might want to use :meth:`_sql.Select.select_from`
    is if our columns clause doesn't have enough information to provide for a
    FROM clause.  For example, to SELECT from the common SQL expression
    ``count(*)``, we use a SQLAlchemy element known as :attr:`_sql.func` to
    produce the SQL ``count()`` function::

        >>> from sqlalchemy import func
        >>> print(select(func.count("*")).select_from(user_table))
        {printsql}SELECT count(:count_2) AS count_1
        FROM user_account

    .. seealso::

        :ref:`orm_queryguide_select_from` - in the :ref:`queryguide_toplevel` -
        contains additional examples and notes
        regarding the interaction of :meth:`_sql.Select.select_from` and
        :meth:`_sql.Select.join`.

.. _tutorial_select_join_onclause:

设置 ON 子句
~~~~~~~~~~~~~~~~~~~~~

Setting the ON Clause

.. tab:: 中文

    前面的 JOIN 示例说明了 :class:`_sql.Select` 构造可以在两个表之间进行连接并自动生成 ON 子句。这些示例中发生这种情况是因为 ``user_table`` 和 ``address_table`` :class:`_sql.Table` 对象包含一个用于形成此 ON 子句的 :class:`_schema.ForeignKeyConstraint` 定义。

    如果连接的左右目标没有这样的约束，或者存在多个约束，我们需要直接指定 ON 子句。:meth:`_sql.Select.join` 和 :meth:`_sql.Select.join_from` 都接受一个附加参数用于 ON 子句，该子句使用与 :ref:`tutorial_select_where_clause` 中相同的 SQL 表达机制来声明::

        >>> print(
        ...     select(address_table.c.email_address)
        ...     .select_from(user_table)
        ...     .join(address_table, user_table.c.id == address_table.c.user_id)
        ... )
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    .. container:: orm-header

        **ORM 提示** - 使用 :func:`_orm.relationship` 构造的 ORM 实体时，还有另一种生成 ON 子句的方法，例如在上一节 :ref:`tutorial_declaring_mapped_classes` 中设置的映射。
        这是一个完整的话题，在 :ref:`tutorial_joining_relationships` 中有详细介绍。

.. tab:: 英文

    The previous examples of JOIN illustrated that the :class:`_sql.Select` construct
    can join between two tables and produce the ON clause automatically.  This
    occurs in those examples because the ``user_table`` and ``address_table``
    :class:`_sql.Table` objects include a single :class:`_schema.ForeignKeyConstraint`
    definition which is used to form this ON clause.

    If the left and right targets of the join do not have such a constraint, or
    there are multiple constraints in place, we need to specify the ON clause
    directly.   Both :meth:`_sql.Select.join` and :meth:`_sql.Select.join_from`
    accept an additional argument for the ON clause, which is stated using the
    same SQL Expression mechanics as we saw about in :ref:`tutorial_select_where_clause`::

        >>> print(
        ...     select(address_table.c.email_address)
        ...     .select_from(user_table)
        ...     .join(address_table, user_table.c.id == address_table.c.user_id)
        ... )
        {printsql}SELECT address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id

    .. container:: orm-header

        **ORM Tip** - there's another way to generate the ON clause when using
        ORM entities that make use of the :func:`_orm.relationship` construct,
        like the mapping set up in the previous section at
        :ref:`tutorial_declaring_mapped_classes`.
        This is a whole subject onto itself, which is introduced at length
        at :ref:`tutorial_joining_relationships`.

OUTER 和 FULL 连接
~~~~~~~~~~~~~~~~~~~

OUTER and FULL join

.. tab:: 中文

    :meth:`_sql.Select.join` 和 :meth:`_sql.Select.join_from` 方法都接受关键字参数 :paramref:`_sql.Select.join.isouter` 和 :paramref:`_sql.Select.join.full`，分别渲染 LEFT OUTER JOIN 和 FULL OUTER JOIN::

        >>> print(select(user_table).join(address_table, isouter=True))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account LEFT OUTER JOIN address ON user_account.id = address.user_id{stop}

        >>> print(select(user_table).join(address_table, full=True))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account FULL OUTER JOIN address ON user_account.id = address.user_id{stop}

    还有一个方法 :meth:`_sql.Select.outerjoin` 等效于使用 ``.join(..., isouter=True)``。

    .. tip::

        SQL 还有一个 "RIGHT OUTER JOIN"。SQLAlchemy 不会直接渲染这个；而是反转表的顺序并使用 "LEFT OUTER JOIN"。

.. tab:: 英文

    Both the :meth:`_sql.Select.join` and :meth:`_sql.Select.join_from` methods
    accept keyword arguments :paramref:`_sql.Select.join.isouter` and
    :paramref:`_sql.Select.join.full` which will render LEFT OUTER JOIN
    and FULL OUTER JOIN, respectively::

        >>> print(select(user_table).join(address_table, isouter=True))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account LEFT OUTER JOIN address ON user_account.id = address.user_id{stop}

        >>> print(select(user_table).join(address_table, full=True))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account FULL OUTER JOIN address ON user_account.id = address.user_id{stop}

    There is also a method :meth:`_sql.Select.outerjoin` that is equivalent to
    using ``.join(..., isouter=True)``.

    .. tip::

        SQL also has a "RIGHT OUTER JOIN".  SQLAlchemy doesn't render this directly;
        instead, reverse the order of the tables and use "LEFT OUTER JOIN".

.. _tutorial_order_by_group_by_having:

ORDER BY、GROUP BY、HAVING
^^^^^^^^^^^^^^^^^^^^^^^^^^^

ORDER BY, GROUP BY, HAVING

.. tab:: 中文

    SELECT SQL 语句包含一个名为 ORDER BY 的子句，用于在给定的排序中返回选定的行。

    GROUP BY 子句的构造类似于 ORDER BY 子句，其目的是将选定的行细分为特定的组，可以在这些组上调用聚合函数。HAVING 子句通常与 GROUP BY 一起使用，其形式类似于 WHERE 子句，只不过它应用于组内使用的聚合函数。

.. tab:: 英文

    The SELECT SQL statement includes a clause called ORDER BY which is used to
    return the selected rows within a given ordering.

    The GROUP BY clause is constructed similarly to the ORDER BY clause, and has
    the purpose of sub-dividing the selected rows into specific groups upon which
    aggregate functions may be invoked. The HAVING clause is usually used with
    GROUP BY and is of a similar form to the WHERE clause, except that it's applied
    to the aggregated functions used within groups.

.. _tutorial_order_by:

ORDER BY
~~~~~~~~

ORDER BY

.. tab:: 中文

    ORDER BY 子句是根据通常基于 :class:`_schema.Column` 或类似对象的 SQL 表达式构造的。:meth:`_sql.Select.order_by` 方法按位置接受一个或多个这些表达式::

        >>> print(select(user_table).order_by(user_table.c.name))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.name

    升序 / 降序可以通过 :meth:`_sql.ColumnElement.asc` 和 :meth:`_sql.ColumnElement.desc` 修饰符实现，这些修饰符也存在于 ORM 绑定属性中::

        >>> print(select(User).order_by(User.fullname.desc()))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.fullname DESC

    上述语句将生成按 ``user_account.fullname`` 列降序排序的行。

.. tab:: 英文

    The ORDER BY clause is constructed in terms
    of SQL Expression constructs typically based on :class:`_schema.Column` or
    similar objects.  The :meth:`_sql.Select.order_by` method accepts one or
    more of these expressions positionally::

        >>> print(select(user_table).order_by(user_table.c.name))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.name

    Ascending / descending is available from the :meth:`_sql.ColumnElement.asc`
    and :meth:`_sql.ColumnElement.desc` modifiers, which are present
    from ORM-bound attributes as well::

        >>> print(select(User).order_by(User.fullname.desc()))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.fullname DESC

    The above statement will yield rows that are sorted by the
    ``user_account.fullname`` column in descending order.

.. _tutorial_group_by_w_aggregates:

使用 GROUP BY / HAVING 的聚合函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Aggregate functions with GROUP BY / HAVING

.. tab:: 中文

    在 SQL 中，聚合函数允许跨多行的列表达式聚合在一起以生成单个结果。示例包括计数、计算平均值以及在一组值中查找最大值或最小值。

    SQLAlchemy 通过一个称为 :data:`_sql.func` 的命名空间以开放的方式提供 SQL 函数。这是一个特殊的构造对象，当给定特定 SQL 函数的名称时，它将创建 :class:`_functions.Function` 的新实例，该名称可以是任何名称，并且可以传递零个或多个参数给函数，这些参数与所有其他情况一样，都是 SQL 表达式构造。例如，要对 ``user_account.id`` 列呈现 SQL COUNT() 函数，我们调用 ``count()`` 名称::

        >>> from sqlalchemy import func
        >>> count_fn = func.count(user_table.c.id)
        >>> print(count_fn)
        {printsql}count(user_account.id)

    SQL 函数在本教程的后面部分 :ref:`tutorial_functions` 中有更详细的描述。

    在 SQL 中使用聚合函数时，GROUP BY 子句是必不可少的，因为它允许将行划分为组，每个组将单独应用聚合函数。当在 SELECT 语句的 COLUMNS 子句中请求非聚合列时，SQL 要求这些列都要受到 GROUP BY 子句的约束，无论是直接的还是基于主键关联的间接的。HAVING 子句的使用方式与 WHERE 子句类似，不同之处在于它根据聚合值而不是直接行内容过滤出行。

    SQLAlchemy 通过 :meth:`_sql.Select.group_by` 和 :meth:`_sql.Select.having` 方法提供这两个子句。下面我们展示选择用户名字段以及地址计数，对于那些有多个地址的用户：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         select(User.name, func.count(Address.id).label("count"))
        ...         .join(Address)
        ...         .group_by(User.name)
        ...         .having(func.count(Address.id) > 1)
        ...     )
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name, count(address.id) AS count
        FROM user_account JOIN address ON user_account.id = address.user_id GROUP BY user_account.name
        HAVING count(address.id) > ?
        [...] (1,){stop}
        [('sandy', 2)]
        {execsql}ROLLBACK{stop}

.. tab:: 英文

    In SQL, aggregate functions allow column expressions across multiple rows
    to be aggregated together to produce a single result.  Examples include
    counting, computing averages, as well as locating the maximum or minimum
    value in a set of values.

    SQLAlchemy provides for SQL functions in an open-ended way using a namespace
    known as :data:`_sql.func`.  This is a special constructor object which
    will create new instances of :class:`_functions.Function` when given the name
    of a particular SQL function, which can have any name, as well as zero or
    more arguments to pass to the function, which are, like in all other cases,
    SQL Expression constructs.   For example, to
    render the SQL COUNT() function against the ``user_account.id`` column,
    we call upon the ``count()`` name::

        >>> from sqlalchemy import func
        >>> count_fn = func.count(user_table.c.id)
        >>> print(count_fn)
        {printsql}count(user_account.id)

    SQL functions are described in more detail later in this tutorial at
    :ref:`tutorial_functions`.

    When using aggregate functions in SQL, the GROUP BY clause is essential in that
    it allows rows to be partitioned into groups where aggregate functions will
    be applied to each group individually.  When requesting non-aggregated columns
    in the COLUMNS clause of a SELECT statement, SQL requires that these columns
    all be subject to a GROUP BY clause, either directly or indirectly based on
    a primary key association.    The HAVING clause is then used in a similar
    manner as the WHERE clause, except that it filters out rows based on aggregated
    values rather than direct row contents.

    SQLAlchemy provides for these two clauses using the :meth:`_sql.Select.group_by`
    and :meth:`_sql.Select.having` methods.   Below we illustrate selecting
    user name fields as well as count of addresses, for those users that have more
    than one address:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         select(User.name, func.count(Address.id).label("count"))
        ...         .join(Address)
        ...         .group_by(User.name)
        ...         .having(func.count(Address.id) > 1)
        ...     )
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name, count(address.id) AS count
        FROM user_account JOIN address ON user_account.id = address.user_id GROUP BY user_account.name
        HAVING count(address.id) > ?
        [...] (1,){stop}
        [('sandy', 2)]
        {execsql}ROLLBACK{stop}

.. _tutorial_order_by_label:

按标签排序或分组
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ordering or Grouping by a Label

.. tab:: 中文

    一个重要的技术，尤其是在某些数据库后端，是能够对已经在列子句中声明的表达式进行 ORDER BY 或 GROUP BY，而无需在 ORDER BY 或 GROUP BY 子句中重新声明表达式，而是使用列子句中的列名或标签名。通过将名称的字符串文本传递给 :meth:`_sql.Select.order_by` 或 :meth:`_sql.Select.group_by` 方法，可以实现这种形式。传递的文本 **不会直接渲染(not rendered directly)** ；相反，列子句中给表达式的名称在上下文中渲染为该表达式的名称，如果没有找到匹配项，则会引发错误。单一修饰符 :func:`.asc` 和 :func:`.desc` 也可以以这种形式使用：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import func, desc
        >>> stmt = (
        ...     select(Address.user_id, func.count(Address.id).label("num_addresses"))
        ...     .group_by("user_id")
        ...     .order_by("user_id", desc("num_addresses"))
        ... )
        >>> print(stmt)
        {printsql}SELECT address.user_id, count(address.id) AS num_addresses
        FROM address GROUP BY address.user_id ORDER BY address.user_id, num_addresses DESC

.. tab:: 英文

    An important technique, in particular on some database backends, is the ability
    to ORDER BY or GROUP BY an expression that is already stated in the columns
    clause, without re-stating the expression in the ORDER BY or GROUP BY clause
    and instead using the column name or labeled name from the COLUMNS clause.
    This form is available by passing the string text of the name to the
    :meth:`_sql.Select.order_by` or :meth:`_sql.Select.group_by` method.  The text
    passed is **not rendered directly**; instead, the name given to an expression
    in the columns clause and rendered as that expression name in context, raising an
    error if no match is found.   The unary modifiers
    :func:`.asc` and :func:`.desc` may also be used in this form:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import func, desc
        >>> stmt = (
        ...     select(Address.user_id, func.count(Address.id).label("num_addresses"))
        ...     .group_by("user_id")
        ...     .order_by("user_id", desc("num_addresses"))
        ... )
        >>> print(stmt)
        {printsql}SELECT address.user_id, count(address.id) AS num_addresses
        FROM address GROUP BY address.user_id ORDER BY address.user_id, num_addresses DESC

.. _tutorial_using_aliases:

使用别名
^^^^^^^^^^^^^

Using Aliases

.. tab:: 中文

    现在我们从多个表中选择并使用连接时，很快就会遇到需要在语句的 FROM 子句中多次引用同一个表的情况。我们使用 SQL **别名(aliases)** 来完成这项工作，这是一种为表或子查询提供替代名称的语法，可以在语句中引用它。

    在 SQLAlchemy 表达式语言中，这些“名称”由称为 :class:`_sql.Alias` 构造的 :class:`_sql.FromClause` 对象表示，在 Core 中使用 :meth:`_sql.FromClause.alias` 方法构造。:class:`_sql.Alias` 构造就像 :class:`_sql.Table` 构造一样，它在 :attr:`_sql.Alias.c` 集合中也包含一个 :class:`_schema.Column` 对象的命名空间。例如，下面的 SELECT 语句返回所有唯一的用户名对::

        >>> user_alias_1 = user_table.alias()
        >>> user_alias_2 = user_table.alias()
        >>> print(
        ...     select(user_alias_1.c.name, user_alias_2.c.name).join_from(
        ...         user_alias_1, user_alias_2, user_alias_1.c.id > user_alias_2.c.id
        ...     )
        ... )
        {printsql}SELECT user_account_1.name, user_account_2.name AS name_1
        FROM user_account AS user_account_1
        JOIN user_account AS user_account_2 ON user_account_1.id > user_account_2.id

.. tab:: 英文

    Now that we are selecting from multiple tables and using joins, we quickly
    run into the case where we need to refer to the same table multiple times
    in the FROM clause of a statement.  We accomplish this using SQL **aliases**,
    which are a syntax that supplies an alternative name to a table or subquery
    from which it can be referenced in the statement.

    In the SQLAlchemy Expression Language, these "names" are instead represented by
    :class:`_sql.FromClause` objects known as the :class:`_sql.Alias` construct,
    which is constructed in Core using the :meth:`_sql.FromClause.alias`
    method. An :class:`_sql.Alias` construct is just like a :class:`_sql.Table`
    construct in that it also has a namespace of :class:`_schema.Column`
    objects within the :attr:`_sql.Alias.c` collection.  The SELECT statement
    below for example returns all unique pairs of user names::

        >>> user_alias_1 = user_table.alias()
        >>> user_alias_2 = user_table.alias()
        >>> print(
        ...     select(user_alias_1.c.name, user_alias_2.c.name).join_from(
        ...         user_alias_1, user_alias_2, user_alias_1.c.id > user_alias_2.c.id
        ...     )
        ... )
        {printsql}SELECT user_account_1.name, user_account_2.name AS name_1
        FROM user_account AS user_account_1
        JOIN user_account AS user_account_2 ON user_account_1.id > user_account_2.id

.. _tutorial_orm_entity_aliases:

ORM 实体别名
~~~~~~~~~~~~~~~~~~

ORM Entity Aliases

.. tab:: 中文

    ORM 等效于 :meth:`_sql.FromClause.alias` 方法的是 ORM :func:`_orm.aliased` 函数，可以应用于 ``User`` 和 ``Address`` 等实体。这会在内部生成一个针对原始映射 :class:`_schema.Table` 对象的 :class:`_sql.Alias` 对象，同时保持 ORM 功能。下面的 SELECT 语句从 ``User`` 实体中选择包含两个特定电子邮件地址的所有对象::

        >>> from sqlalchemy.orm import aliased
        >>> address_alias_1 = aliased(Address)
        >>> address_alias_2 = aliased(Address)
        >>> print(
        ...     select(User)
        ...     .join_from(User, address_alias_1)
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join_from(User, address_alias_2)
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2

    .. tip::

        如 :ref:`tutorial_select_join_onclause` 中所述，ORM 提供了另一种使用 :func:`_orm.relationship` 构造进行连接的方法。
        上述使用别名的示例在 :ref:`tutorial_joining_relationships_aliased` 中使用 :func:`_orm.relationship` 进行演示。

.. tab:: 英文

    The ORM equivalent of the :meth:`_sql.FromClause.alias` method is the
    ORM :func:`_orm.aliased` function, which may be applied to an entity
    such as ``User`` and ``Address``.  This produces a :class:`_sql.Alias` object
    internally that's against the original mapped :class:`_schema.Table` object,
    while maintaining ORM functionality.  The SELECT below selects from the
    ``User`` entity all objects that include two particular email addresses::

        >>> from sqlalchemy.orm import aliased
        >>> address_alias_1 = aliased(Address)
        >>> address_alias_2 = aliased(Address)
        >>> print(
        ...     select(User)
        ...     .join_from(User, address_alias_1)
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join_from(User, address_alias_2)
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2

    .. tip::

        As mentioned in :ref:`tutorial_select_join_onclause`, the ORM provides
        for another way to join using the :func:`_orm.relationship` construct.
        The above example using aliases is demonstrated using :func:`_orm.relationship`
        at :ref:`tutorial_joining_relationships_aliased`.


.. _tutorial_subqueries_ctes:

子查询和 CTE
^^^^^^^^^^^^^^^^^^^^

Subqueries and CTEs

.. tab:: 中文

    SQL 中的子查询是一个在括号内呈现的 SELECT 语句，并放置在封闭语句的上下文中，通常是 SELECT 语句，但不一定是。

    本节将介绍所谓的“非标量”子查询，通常放在封闭 SELECT 的 FROM 子句中。我们还将介绍公共表表达式（CTE），它的用法与子查询类似，但包含额外的功能。

    SQLAlchemy 使用 :class:`_sql.Subquery` 对象来表示子查询，使用 :class:`_sql.CTE` 来表示 CTE，通常分别从 :meth:`_sql.Select.subquery` 和 :meth:`_sql.Select.cte` 方法中获得。任何一个对象都可以作为较大的 :func:`_sql.select` 构造中的 FROM 元素使用。

    我们可以构造一个 :class:`_sql.Subquery` 来选择 ``address`` 表中的行的聚合计数（聚合函数和 GROUP BY 在 :ref:`tutorial_group_by_w_aggregates` 中已介绍）：

        >>> subq = (
        ...     select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .subquery()
        ... )

    单独将子查询字符串化，而不是嵌入另一个 :class:`_sql.Select` 或其他语句中，会生成没有任何括号的普通 SELECT 语句::

        >>> print(subq)
        {printsql}SELECT count(address.id) AS count, address.user_id
        FROM address GROUP BY address.user_id

    :class:`_sql.Subquery` 对象的行为类似于任何其他 FROM 对象，如 :class:`_schema.Table`，尤其是它包含一个选中列的 :attr:`_sql.Subquery.c` 命名空间。我们可以使用这个命名空间来引用 ``user_id`` 列以及我们自定义标签的 ``count`` 表达式::

        >>> print(select(subq.c.user_id, subq.c.count))
        {printsql}SELECT anon_1.user_id, anon_1.count
        FROM (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id) AS anon_1

    在 ``subq`` 对象中包含的行选择中，我们可以将对象应用于更大的 :class:`_sql.Select`，将数据连接到 ``user_account`` 表中::

        >>> stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        ...     user_table, subq
        ... )

        >>> print(stmt)
        {printsql}SELECT user_account.name, user_account.fullname, anon_1.count
        FROM user_account JOIN (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id) AS anon_1 ON user_account.id = anon_1.user_id

    为了从 ``user_account`` 连接到 ``address``，我们使用了 :meth:`_sql.Select.join_from` 方法。如前所述，此连接的 ON 子句再次基于外键约束 **推断(inferred)** 。尽管 SQL 子查询本身没有任何约束，SQLAlchemy 可以通过确定 ``subq.c.user_id`` 列是从 ``address_table.c.user_id`` 列 **派生(derived)** 的来作用于表示在列上的约束，该列确实表达了指回 ``user_table.c.id`` 列的外键关系，然后用于生成 ON 子句。

.. tab:: 英文

    A subquery in SQL is a SELECT statement that is rendered within parenthesis and
    placed within the context of an enclosing statement, typically a SELECT
    statement but not necessarily.

    This section will cover a so-called "non-scalar" subquery, which is typically
    placed in the FROM clause of an enclosing SELECT.   We will also cover the
    Common Table Expression or CTE, which is used in a similar way as a subquery,
    but includes additional features.

    SQLAlchemy uses the :class:`_sql.Subquery` object to represent a subquery and
    the :class:`_sql.CTE` to represent a CTE, usually obtained from the
    :meth:`_sql.Select.subquery` and :meth:`_sql.Select.cte` methods, respectively.
    Either object can be used as a FROM element inside of a larger
    :func:`_sql.select` construct.

    We can construct a :class:`_sql.Subquery` that will select an aggregate count
    of rows from the ``address`` table (aggregate functions and GROUP BY were
    introduced previously at :ref:`tutorial_group_by_w_aggregates`):

        >>> subq = (
        ...     select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .subquery()
        ... )

    Stringifying the subquery by itself without it being embedded inside of another
    :class:`_sql.Select` or other statement produces the plain SELECT statement
    without any enclosing parenthesis::

        >>> print(subq)
        {printsql}SELECT count(address.id) AS count, address.user_id
        FROM address GROUP BY address.user_id


    The :class:`_sql.Subquery` object behaves like any other FROM object such
    as a :class:`_schema.Table`, notably that it includes a :attr:`_sql.Subquery.c`
    namespace of the columns which it selects.  We can use this namespace to
    refer to both the ``user_id`` column as well as our custom labeled
    ``count`` expression::

        >>> print(select(subq.c.user_id, subq.c.count))
        {printsql}SELECT anon_1.user_id, anon_1.count
        FROM (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id) AS anon_1

    With a selection of rows contained within the ``subq`` object, we can apply
    the object to a larger :class:`_sql.Select` that will join the data to
    the ``user_account`` table::

        >>> stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        ...     user_table, subq
        ... )

        >>> print(stmt)
        {printsql}SELECT user_account.name, user_account.fullname, anon_1.count
        FROM user_account JOIN (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id) AS anon_1 ON user_account.id = anon_1.user_id

    In order to join from ``user_account`` to ``address``, we made use of the
    :meth:`_sql.Select.join_from` method.   As has been illustrated previously, the
    ON clause of this join was again **inferred** based on foreign key constraints.
    Even though a SQL subquery does not itself have any constraints, SQLAlchemy can
    act upon constraints represented on the columns by determining that the
    ``subq.c.user_id`` column is **derived** from the ``address_table.c.user_id``
    column, which does express a foreign key relationship back to the
    ``user_table.c.id`` column which is then used to generate the ON clause.

通用表表达式 (CTE)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Common Table Expressions (CTEs)

.. tab:: 中文

    在 SQLAlchemy 中，:class:`_sql.CTE` 构造的用法与 :class:`_sql.Subquery` 构造几乎相同。通过将 :meth:`_sql.Select.subquery` 方法的调用更改为使用 :meth:`_sql.Select.cte`，我们可以以相同的方式使用生成的对象作为 FROM 元素，但渲染的 SQL 是非常不同的公共表表达式语法::

        >>> subq = (
        ...     select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .cte()
        ... )

        >>> stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        ...     user_table, subq
        ... )

        >>> print(stmt)
        {printsql}WITH anon_1 AS
        (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id)
        SELECT user_account.name, user_account.fullname, anon_1.count
        FROM user_account JOIN anon_1 ON user_account.id = anon_1.user_id

    :class:`_sql.CTE` 构造还具有以“递归”样式使用的能力，并且在更复杂的情况下可以从 INSERT、UPDATE 或 DELETE 语句的 RETURNING 子句中组成。:class:`_sql.CTE` 的文档字符串中包含有关这些附加模式的详细信息。

    在这两种情况下，子查询和 CTE 在 SQL 级别使用“匿名”名称命名。在 Python 代码中，我们根本不需要提供这些名称。:class:`_sql.Subquery` 或 :class:`_sql.CTE` 实例的对象标识在渲染时作为对象的语法标识。如果传递名称作为 :meth:`_sql.Select.subquery` 或 :meth:`_sql.Select.cte` 方法的第一个参数，则可以在 SQL 中渲染该名称。

    .. seealso::

        :meth:`_sql.Select.subquery` - 有关子查询的更多详细信息

        :meth:`_sql.Select.cte` - 包括如何使用 RECURSIVE 以及面向 DML 的 CTE 的示例

.. tab:: 英文

    Usage of the :class:`_sql.CTE` construct in SQLAlchemy is virtually
    the same as how the :class:`_sql.Subquery` construct is used.  By changing
    the invocation of the :meth:`_sql.Select.subquery` method to use
    :meth:`_sql.Select.cte` instead, we can use the resulting object as a FROM
    element in the same way, but the SQL rendered is the very different common
    table expression syntax::

        >>> subq = (
        ...     select(func.count(address_table.c.id).label("count"), address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .cte()
        ... )

        >>> stmt = select(user_table.c.name, user_table.c.fullname, subq.c.count).join_from(
        ...     user_table, subq
        ... )

        >>> print(stmt)
        {printsql}WITH anon_1 AS
        (SELECT count(address.id) AS count, address.user_id AS user_id
        FROM address GROUP BY address.user_id)
        SELECT user_account.name, user_account.fullname, anon_1.count
        FROM user_account JOIN anon_1 ON user_account.id = anon_1.user_id

    The :class:`_sql.CTE` construct also features the ability to be used
    in a "recursive" style, and may in more elaborate cases be composed from the
    RETURNING clause of an INSERT, UPDATE or DELETE statement.  The docstring
    for :class:`_sql.CTE` includes details on these additional patterns.

    In both cases, the subquery and CTE were named at the SQL level using an
    "anonymous" name.  In the Python code, we don't need to provide these names
    at all.  The object identity of the :class:`_sql.Subquery` or :class:`_sql.CTE`
    instances serves as the syntactical identity of the object when rendered.
    A name that will be rendered in the SQL can be provided by passing it as the
    first argument of the :meth:`_sql.Select.subquery` or :meth:`_sql.Select.cte` methods.

    .. seealso::

        :meth:`_sql.Select.subquery` - further detail on subqueries

        :meth:`_sql.Select.cte` - examples for CTE including how to use RECURSIVE as well as DML-oriented CTEs

.. _tutorial_subqueries_orm_aliased:

ORM 实体子查询/CTE
~~~~~~~~~~~~~~~~~~~~~~~~~~

ORM Entity Subqueries/CTEs

.. tab:: 中文

    在 ORM 中，:func:`_orm.aliased` 构造可用于将 ORM 实体（例如我们的 ``User`` 或 ``Address`` 类）与表示行源的任何 :class:`_sql.FromClause` 概念关联。前一节 :ref:`tutorial_orm_entity_aliases` 说明了使用 :func:`_orm.aliased` 将映射类与其映射的 :class:`_schema.Table` 的 :class:`_sql.Alias` 关联。在这里，我们说明 :func:`_orm.aliased` 对 :class:`_sql.Subquery` 和 :class:`_sql.CTE` 的应用，这些都是针对 :class:`_sql.Select` 构造生成的，最终派生自相同的映射 :class:`_schema.Table`。

    下面是将 :func:`_orm.aliased` 应用于 :class:`_sql.Subquery` 构造的示例，以便从其行中提取 ORM 实体。结果显示了一系列 ``User`` 和 ``Address`` 对象，其中每个 ``Address`` 对象的数据最终来自对 ``address`` 表的子查询，而不是直接来自该表：

    .. sourcecode:: pycon+sql

        >>> subq = select(Address).where(~Address.email_address.like("%@aol.com")).subquery()
        >>> address_subq = aliased(Address, subq)
        >>> stmt = (
        ...     select(User, address_subq)
        ...     .join_from(User, address_subq)
        ...     .order_by(User.id, address_subq.id)
        ... )
        >>> with Session(engine) as session:
        ...     for user, address in session.execute(stmt):
        ...         print(f"{user} {address}")
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
        FROM user_account JOIN
        (SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE ?) AS anon_1 ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.id
        [...] ('%@aol.com',){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants') Address(id=1, email_address='spongebob@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=2, email_address='sandy@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='sandy@squirrelpower.org')
        {execsql}ROLLBACK{stop}

    下面是一个相同的示例，只是它使用 :class:`_sql.CTE` 构造：

    .. sourcecode:: pycon+sql

        >>> cte_obj = select(Address).where(~Address.email_address.like("%@aol.com")).cte()
        >>> address_cte = aliased(Address, cte_obj)
        >>> stmt = (
        ...     select(User, address_cte)
        ...     .join_from(User, address_cte)
        ...     .order_by(User.id, address_cte.id)
        ... )
        >>> with Session(engine) as session:
        ...     for user, address in session.execute(stmt):
        ...         print(f"{user} {address}")
        {execsql}BEGIN (implicit)
        WITH anon_1 AS
        (SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE ?)
        SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
        FROM user_account
        JOIN anon_1 ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.id
        [...] ('%@aol.com',){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants') Address(id=1, email_address='spongebob@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=2, email_address='sandy@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='sandy@squirrelpower.org')
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`orm_queryguide_subqueries` - 在 :ref:`queryguide_toplevel` 中

.. tab:: 英文

    In the ORM, the :func:`_orm.aliased` construct may be used to associate an ORM
    entity, such as our ``User`` or ``Address`` class, with any :class:`_sql.FromClause`
    concept that represents a source of rows.  The preceding section
    :ref:`tutorial_orm_entity_aliases` illustrates using :func:`_orm.aliased`
    to associate the mapped class with an :class:`_sql.Alias` of its
    mapped :class:`_schema.Table`.   Here we illustrate :func:`_orm.aliased` doing the same
    thing against both a :class:`_sql.Subquery` as well as a :class:`_sql.CTE`
    generated against a :class:`_sql.Select` construct, that ultimately derives
    from that same mapped :class:`_schema.Table`.

    Below is an example of applying :func:`_orm.aliased` to the :class:`_sql.Subquery`
    construct, so that ORM entities can be extracted from its rows.  The result
    shows a series of ``User`` and ``Address`` objects, where the data for
    each ``Address`` object ultimately came from a subquery against the
    ``address`` table rather than that table directly:

    .. sourcecode:: pycon+sql

        >>> subq = select(Address).where(~Address.email_address.like("%@aol.com")).subquery()
        >>> address_subq = aliased(Address, subq)
        >>> stmt = (
        ...     select(User, address_subq)
        ...     .join_from(User, address_subq)
        ...     .order_by(User.id, address_subq.id)
        ... )
        >>> with Session(engine) as session:
        ...     for user, address in session.execute(stmt):
        ...         print(f"{user} {address}")
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
        FROM user_account JOIN
        (SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE ?) AS anon_1 ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.id
        [...] ('%@aol.com',){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants') Address(id=1, email_address='spongebob@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=2, email_address='sandy@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='sandy@squirrelpower.org')
        {execsql}ROLLBACK{stop}

    Another example follows, which is exactly the same except it makes use of the
    :class:`_sql.CTE` construct instead:

    .. sourcecode:: pycon+sql

        >>> cte_obj = select(Address).where(~Address.email_address.like("%@aol.com")).cte()
        >>> address_cte = aliased(Address, cte_obj)
        >>> stmt = (
        ...     select(User, address_cte)
        ...     .join_from(User, address_cte)
        ...     .order_by(User.id, address_cte.id)
        ... )
        >>> with Session(engine) as session:
        ...     for user, address in session.execute(stmt):
        ...         print(f"{user} {address}")
        {execsql}BEGIN (implicit)
        WITH anon_1 AS
        (SELECT address.id AS id, address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE address.email_address NOT LIKE ?)
        SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.email_address, anon_1.user_id
        FROM user_account
        JOIN anon_1 ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.id
        [...] ('%@aol.com',){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants') Address(id=1, email_address='spongebob@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=2, email_address='sandy@sqlalchemy.org')
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='sandy@squirrelpower.org')
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`orm_queryguide_subqueries` - in the :ref:`queryguide_toplevel`

.. _tutorial_scalar_subquery:

标量和相关子查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Scalar and Correlated Subqueries

.. tab:: 中文

    标量子查询是一个返回零或一行且仅包含一列的子查询。然后，该子查询在封闭的 SELECT 语句的 COLUMNS 或 WHERE 子句中使用，与常规子查询不同，它不在 FROM 子句中使用。:term:`相关子查询` 是一个标量子查询，它引用封闭 SELECT 语句中的表。

    SQLAlchemy 使用 :class:`_sql.ScalarSelect` 构造来表示标量子查询，它是 :class:`_sql.ColumnElement` 表达式层次结构的一部分，而常规子查询由 :class:`_sql.Subquery` 构造表示，它属于 :class:`_sql.FromClause` 层次结构。

    标量子查询通常（但不一定）与聚合函数一起使用，前面在 :ref:`tutorial_group_by_w_aggregates` 中介绍过。通过使用 :meth:`_sql.Select.scalar_subquery` 方法明确指示标量子查询，如下所示。其默认字符串形式在单独字符串化时呈现为从两个表中选择的普通 SELECT 语句::

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .scalar_subquery()
        ... )
        >>> print(subq)
        {printsql}(SELECT count(address.id) AS count_1
        FROM address, user_account
        WHERE user_account.id = address.user_id)

    上述 ``subq`` 对象现在位于 :class:`_sql.ColumnElement` SQL 表达式层次结构中，可以像任何其他列表达式一样使用::

        >>> print(subq == 5)
        {printsql}(SELECT count(address.id) AS count_1
        FROM address, user_account
        WHERE user_account.id = address.user_id) = :param_1

    尽管标量子查询本身在字符串化时会在其 FROM 子句中呈现 ``user_account`` 和 ``address``，但当将其嵌入到处理 ``user_account`` 表的封闭 :func:`_sql.select` 构造中时，``user_account`` 表会自动 **关联(correlated)** ，这意味着它不会在子查询的 FROM 子句中呈现::

        >>> stmt = select(user_table.c.name, subq.label("address_count"))
        >>> print(stmt)
        {printsql}SELECT user_account.name, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
        FROM user_account

    简单的相关子查询通常会做出所需的正确操作。然而，在关联不明确的情况下，SQLAlchemy 会让我们知道需要更多的清晰度::

        >>> stmt = (
        ...     select(
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...         subq.label("address_count"),
        ...     )
        ...     .join_from(user_table, address_table)
        ...     .order_by(user_table.c.id, address_table.c.id)
        ... )
        >>> print(stmt)
        Traceback (most recent call last):
        ...
        InvalidRequestError: Select statement '<... Select object at ...>' returned
        no FROM clauses due to auto-correlation; specify correlate(<tables>) to
        control correlation manually.

    要指定我们希望关联的表是 ``user_table``，我们可以使用 :meth:`_sql.ScalarSelect.correlate` 或 :meth:`_sql.ScalarSelect.correlate_except` 方法::

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .scalar_subquery()
        ...     .correlate(user_table)
        ... )

    然后，该语句可以像任何其他列一样返回此列的数据：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         select(
        ...             user_table.c.name,
        ...             address_table.c.email_address,
        ...             subq.label("address_count"),
        ...         )
        ...         .join_from(user_table, address_table)
        ...         .order_by(user_table.c.id, address_table.c.id)
        ...     )
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name, address.email_address, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
        FROM user_account JOIN address ON user_account.id = address.user_id ORDER BY user_account.id, address.id
        [...] (){stop}
        [('spongebob', 'spongebob@sqlalchemy.org', 1), ('sandy', 'sandy@sqlalchemy.org', 2),
        ('sandy', 'sandy@squirrelpower.org', 2)]
        {execsql}ROLLBACK{stop}

.. tab:: 英文

    A scalar subquery is a subquery that returns exactly zero or one row and
    exactly one column.  The subquery is then used in the COLUMNS or WHERE clause
    of an enclosing SELECT statement and is different than a regular subquery in
    that it is not used in the FROM clause.   A :term:`correlated subquery` is a
    scalar subquery that refers to a table in the enclosing SELECT statement.

    SQLAlchemy represents the scalar subquery using the
    :class:`_sql.ScalarSelect` construct, which is part of the
    :class:`_sql.ColumnElement` expression hierarchy, in contrast to the regular
    subquery which is represented by the :class:`_sql.Subquery` construct, which is
    in the :class:`_sql.FromClause` hierarchy.

    Scalar subqueries are often, but not necessarily, used with aggregate functions,
    introduced previously at :ref:`tutorial_group_by_w_aggregates`.   A scalar
    subquery is indicated explicitly by making use of the :meth:`_sql.Select.scalar_subquery`
    method as below.  It's default string form when stringified by itself
    renders as an ordinary SELECT statement that is selecting from two tables::

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .scalar_subquery()
        ... )
        >>> print(subq)
        {printsql}(SELECT count(address.id) AS count_1
        FROM address, user_account
        WHERE user_account.id = address.user_id)

    The above ``subq`` object now falls within the :class:`_sql.ColumnElement`
    SQL expression hierarchy, in that it may be used like any other column
    expression::

        >>> print(subq == 5)
        {printsql}(SELECT count(address.id) AS count_1
        FROM address, user_account
        WHERE user_account.id = address.user_id) = :param_1


    Although the scalar subquery by itself renders both ``user_account`` and
    ``address`` in its FROM clause when stringified by itself, when embedding it
    into an enclosing :func:`_sql.select` construct that deals with the
    ``user_account`` table, the ``user_account`` table is automatically
    **correlated**, meaning it does not render in the FROM clause of the subquery::

        >>> stmt = select(user_table.c.name, subq.label("address_count"))
        >>> print(stmt)
        {printsql}SELECT user_account.name, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
        FROM user_account

    Simple correlated subqueries will usually do the right thing that's desired.
    However, in the case where the correlation is ambiguous, SQLAlchemy will let
    us know that more clarity is needed::

        >>> stmt = (
        ...     select(
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...         subq.label("address_count"),
        ...     )
        ...     .join_from(user_table, address_table)
        ...     .order_by(user_table.c.id, address_table.c.id)
        ... )
        >>> print(stmt)
        Traceback (most recent call last):
        ...
        InvalidRequestError: Select statement '<... Select object at ...>' returned
        no FROM clauses due to auto-correlation; specify correlate(<tables>) to
        control correlation manually.

    To specify that the ``user_table`` is the one we seek to correlate we specify
    this using the :meth:`_sql.ScalarSelect.correlate` or
    :meth:`_sql.ScalarSelect.correlate_except` methods::

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .scalar_subquery()
        ...     .correlate(user_table)
        ... )

    The statement then can return the data for this column like any other:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         select(
        ...             user_table.c.name,
        ...             address_table.c.email_address,
        ...             subq.label("address_count"),
        ...         )
        ...         .join_from(user_table, address_table)
        ...         .order_by(user_table.c.id, address_table.c.id)
        ...     )
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name, address.email_address, (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id) AS address_count
        FROM user_account JOIN address ON user_account.id = address.user_id ORDER BY user_account.id, address.id
        [...] (){stop}
        [('spongebob', 'spongebob@sqlalchemy.org', 1), ('sandy', 'sandy@sqlalchemy.org', 2),
        ('sandy', 'sandy@squirrelpower.org', 2)]
        {execsql}ROLLBACK{stop}


.. _tutorial_lateral_correlation:

LATERAL 相关
~~~~~~~~~~~~~~~~~~~

LATERAL correlation

.. tab:: 中文

    LATERAL 关联是 SQL 关联的一个特殊子类别，允许选择单元在单个 FROM 子句中引用另一个选择单元。这是一个非常特殊的用例，虽然是 SQL 标准的一部分，但已知只有 PostgreSQL 的最新版本支持。

    通常，如果 SELECT 语句在其 FROM 子句中引用 ``table1 JOIN (SELECT ...) AS subquery``，则右侧的子查询可能不会引用左侧的 "table1" 表达式；关联可能只引用完全封闭此 SELECT 的另一个 SELECT 的表。LATERAL 关键字允许我们改变这种行为，并允许从右侧 JOIN 进行关联。

    SQLAlchemy 使用 :meth:`_expression.Select.lateral` 方法支持此功能，该方法创建一个称为 :class:`.Lateral` 的对象。:class:`.Lateral` 属于与 :class:`.Subquery` 和 :class:`.Alias` 相同的家族，但在将构造添加到封闭 SELECT 的 FROM 子句时，也包括关联行为。以下示例说明了一个使用 LATERAL 的 SQL 查询，选择“用户账户 / 电子邮件地址计数”数据，如前一节所述::

        >>> subq = (
        ...     select(
        ...         func.count(address_table.c.id).label("address_count"),
        ...         address_table.c.email_address,
        ...         address_table.c.user_id,
        ...     )
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .lateral()
        ... )
        >>> stmt = (
        ...     select(user_table.c.name, subq.c.address_count, subq.c.email_address)
        ...     .join_from(user_table, subq)
        ...     .order_by(user_table.c.id, subq.c.email_address)
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.name, anon_1.address_count, anon_1.email_address
        FROM user_account
        JOIN LATERAL (SELECT count(address.id) AS address_count,
        address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE user_account.id = address.user_id) AS anon_1
        ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.email_address

    上述示例中，JOIN 的右侧是一个关联到 JOIN 左侧 ``user_account`` 表的子查询。

    使用 :meth:`_expression.Select.lateral` 时，:meth:`_expression.Select.correlate` 和 :meth:`_expression.Select.correlate_except` 方法的行为也适用于 :class:`.Lateral` 构造。

    .. seealso::

        :class:`_expression.Lateral`

        :meth:`_expression.Select.lateral`

.. tab:: 英文

    LATERAL correlation is a special sub-category of SQL correlation which
    allows a selectable unit to refer to another selectable unit within a
    single FROM clause.  This is an extremely special use case which, while
    part of the SQL standard, is only known to be supported by recent
    versions of PostgreSQL.

    Normally, if a SELECT statement refers to
    ``table1 JOIN (SELECT ...) AS subquery`` in its FROM clause, the subquery
    on the right side may not refer to the "table1" expression from the left side;
    correlation may only refer to a table that is part of another SELECT that
    entirely encloses this SELECT.  The LATERAL keyword allows us to turn this
    behavior around and allow correlation from the right side JOIN.

    SQLAlchemy supports this feature using the :meth:`_expression.Select.lateral`
    method, which creates an object known as :class:`.Lateral`. :class:`.Lateral`
    is in the same family as :class:`.Subquery` and :class:`.Alias`, but also
    includes correlation behavior when the construct is added to the FROM clause of
    an enclosing SELECT. The following example illustrates a SQL query that makes
    use of LATERAL, selecting the "user account / count of email address" data as
    was discussed in the previous section::

        >>> subq = (
        ...     select(
        ...         func.count(address_table.c.id).label("address_count"),
        ...         address_table.c.email_address,
        ...         address_table.c.user_id,
        ...     )
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .lateral()
        ... )
        >>> stmt = (
        ...     select(user_table.c.name, subq.c.address_count, subq.c.email_address)
        ...     .join_from(user_table, subq)
        ...     .order_by(user_table.c.id, subq.c.email_address)
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.name, anon_1.address_count, anon_1.email_address
        FROM user_account
        JOIN LATERAL (SELECT count(address.id) AS address_count,
        address.email_address AS email_address, address.user_id AS user_id
        FROM address
        WHERE user_account.id = address.user_id) AS anon_1
        ON user_account.id = anon_1.user_id
        ORDER BY user_account.id, anon_1.email_address

    Above, the right side of the JOIN is a subquery that correlates to the
    ``user_account`` table that's on the left side of the join.

    When using :meth:`_expression.Select.lateral`, the behavior of
    :meth:`_expression.Select.correlate` and
    :meth:`_expression.Select.correlate_except` methods is applied to the
    :class:`.Lateral` construct as well.

    .. seealso::

        :class:`_expression.Lateral`

        :meth:`_expression.Select.lateral`



.. _tutorial_union:

UNION、UNION ALL 和其他集合操作
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

UNION, UNION ALL and other set operations

.. tab:: 中文

    在 SQL 中，SELECT 语句可以使用 UNION 或 UNION ALL SQL 操作合并在一起，从而生成一个或多个语句共同生成的所有行的集合。其他集合操作如 INTERSECT [ALL] 和 EXCEPT [ALL] 也是可能的。

    SQLAlchemy 的 :class:`_sql.Select` 构造通过函数如 :func:`_sql.union`、:func:`_sql.intersect` 和 :func:`_sql.except_` 以及它们的“all”对应物 :func:`_sql.union_all`、:func:`_sql.intersect_all` 和 :func:`_sql.except_all` 支持这种性质的组合。这些函数都接受任意数量的子选择项，通常是 :class:`_sql.Select` 构造，但也可以是现有的组合。

    这些函数生成的构造是 :class:`_sql.CompoundSelect`，其使用方式与 :class:`_sql.Select` 构造相同，只是它的方法较少。例如，由 :func:`_sql.union_all` 生成的 :class:`_sql.CompoundSelect` 可以直接使用 :meth:`_engine.Connection.execute` 调用::

        >>> from sqlalchemy import union_all
        >>> stmt1 = select(user_table).where(user_table.c.name == "sandy")
        >>> stmt2 = select(user_table).where(user_table.c.name == "spongebob")
        >>> u = union_all(stmt1, stmt2)
        >>> with engine.connect() as conn:
        ...     result = conn.execute(u)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [generated in ...] ('sandy', 'spongebob')
        {stop}[(2, 'sandy', 'Sandy Cheeks'), (1, 'spongebob', 'Spongebob Squarepants')]
        {execsql}ROLLBACK{stop}

    要将 :class:`_sql.CompoundSelect` 用作子查询，就像 :class:`_sql.Select` 一样，它提供了一个 :meth:`_sql.SelectBase.subquery` 方法，该方法将生成一个 :class:`_sql.Subquery` 对象，并带有一个可以在封闭的 :func:`_sql.select` 中引用的 :attr:`_sql.FromClause.c` 集合::

        >>> u_subq = u.subquery()
        >>> stmt = (
        ...     select(u_subq.c.name, address_table.c.email_address)
        ...     .join_from(address_table, u_subq)
        ...     .order_by(u_subq.c.name, address_table.c.email_address)
        ... )
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT anon_1.name, address.email_address
        FROM address JOIN
        (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?
        UNION ALL
        SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?)
        AS anon_1 ON anon_1.id = address.user_id
        ORDER BY anon_1.name, address.email_address
        [generated in ...] ('sandy', 'spongebob')
        {stop}[('sandy', 'sandy@sqlalchemy.org'), ('sandy', 'sandy@squirrelpower.org'), ('spongebob', 'spongebob@sqlalchemy.org')]
        {execsql}ROLLBACK{stop}

.. tab:: 英文

    In SQL, SELECT statements can be merged together using the UNION or UNION ALL
    SQL operation, which produces the set of all rows produced by one or more
    statements together.  Other set operations such as INTERSECT [ALL] and
    EXCEPT [ALL] are also possible.

    SQLAlchemy's :class:`_sql.Select` construct supports compositions of this
    nature using functions like :func:`_sql.union`, :func:`_sql.intersect` and
    :func:`_sql.except_`, and the "all" counterparts :func:`_sql.union_all`,
    :func:`_sql.intersect_all` and :func:`_sql.except_all`. These functions all
    accept an arbitrary number of sub-selectables, which are typically
    :class:`_sql.Select` constructs but may also be an existing composition.

    The construct produced by these functions is the :class:`_sql.CompoundSelect`,
    which is used in the same manner as the :class:`_sql.Select` construct, except
    that it has fewer methods.   The :class:`_sql.CompoundSelect` produced by
    :func:`_sql.union_all` for example may be invoked directly using
    :meth:`_engine.Connection.execute`::

        >>> from sqlalchemy import union_all
        >>> stmt1 = select(user_table).where(user_table.c.name == "sandy")
        >>> stmt2 = select(user_table).where(user_table.c.name == "spongebob")
        >>> u = union_all(stmt1, stmt2)
        >>> with engine.connect() as conn:
        ...     result = conn.execute(u)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [generated in ...] ('sandy', 'spongebob')
        {stop}[(2, 'sandy', 'Sandy Cheeks'), (1, 'spongebob', 'Spongebob Squarepants')]
        {execsql}ROLLBACK{stop}

    To use a :class:`_sql.CompoundSelect` as a subquery, just like :class:`_sql.Select`
    it provides a :meth:`_sql.SelectBase.subquery` method which will produce a
    :class:`_sql.Subquery` object with a :attr:`_sql.FromClause.c`
    collection that may be referenced in an enclosing :func:`_sql.select`::

        >>> u_subq = u.subquery()
        >>> stmt = (
        ...     select(u_subq.c.name, address_table.c.email_address)
        ...     .join_from(address_table, u_subq)
        ...     .order_by(u_subq.c.name, address_table.c.email_address)
        ... )
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT anon_1.name, address.email_address
        FROM address JOIN
        (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?
        UNION ALL
        SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?)
        AS anon_1 ON anon_1.id = address.user_id
        ORDER BY anon_1.name, address.email_address
        [generated in ...] ('sandy', 'spongebob')
        {stop}[('sandy', 'sandy@sqlalchemy.org'), ('sandy', 'sandy@squirrelpower.org'), ('spongebob', 'spongebob@sqlalchemy.org')]
        {execsql}ROLLBACK{stop}

.. _tutorial_orm_union:

从联合中选择 ORM 实体
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selecting ORM Entities from Unions

.. tab:: 中文

    前面的示例说明了如何构造给定两个 :class:`_schema.Table` 对象的 UNION，以返回数据库行。如果我们想使用 UNION 或其他集合操作选择行，然后作为 ORM 对象接收它们，有两种方法可以使用。在这两种情况下，我们首先构造一个表示我们要执行的 SELECT / UNION / 等语句的 :func:`_sql.select` 或 :class:`_sql.CompoundSelect` 对象；该语句应针对目标 ORM 实体或其底层映射的 :class:`_schema.Table` 对象组成::

        >>> stmt1 = select(User).where(User.name == "sandy")
        >>> stmt2 = select(User).where(User.name == "spongebob")
        >>> u = union_all(stmt1, stmt2)

    对于未嵌套在子查询内的简单 SELECT with UNION，通常可以使用 :meth:`_sql.Select.from_statement` 方法在 ORM 对象获取上下文中使用它们。通过这种方法，UNION 语句表示整个查询；在使用 :meth:`_sql.Select.from_statement` 后不能添加其他条件::

        >>> orm_stmt = select(User).from_statement(u)
        >>> with Session(engine) as session:
        ...     for obj in session.execute(orm_stmt).scalars():
        ...         print(obj)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ? UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [generated in ...] ('sandy', 'spongebob')
        {stop}User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        {execsql}ROLLBACK{stop}

    要以更灵活的方式使用 UNION 或其他集合相关构造作为实体相关组件，可以使用 :meth:`_sql.CompoundSelect.subquery` 方法将 :class:`_sql.CompoundSelect` 构造组织成子查询，然后使用 :func:`_orm.aliased` 函数链接到 ORM 对象。这与 :ref:`tutorial_subqueries_orm_aliased` 中介绍的方式相同，首先创建我们所需实体到子查询的临时“映射”，然后像选择其他映射类一样从该新实体中选择。在下面的示例中，我们可以在 UNION 本身之外添加其他条件（如 ORDER BY），因为我们可以过滤或按子查询导出的列排序::

        >>> user_alias = aliased(User, u.subquery())
        >>> orm_stmt = select(user_alias).order_by(user_alias.id)
        >>> with Session(engine) as session:
        ...     for obj in session.execute(orm_stmt).scalars():
        ...         print(obj)
        {execsql}BEGIN (implicit)
        SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ? UNION ALL SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?) AS anon_1 ORDER BY anon_1.id
        [generated in ...] ('sandy', 'spongebob')
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`orm_queryguide_unions` - 在 :ref:`queryguide_toplevel`

.. tab:: 英文

    The preceding examples illustrated how to construct a UNION given two
    :class:`_schema.Table` objects, to then return database rows.  If we wanted
    to use a UNION or other set operation to select rows that we then receive
    as ORM objects, there are two approaches that may be used.  In both cases,
    we first construct a :func:`_sql.select` or :class:`_sql.CompoundSelect`
    object that represents the SELECT / UNION / etc statement we want to
    execute; this statement should be composed against the target
    ORM entities or their underlying mapped :class:`_schema.Table` objects::

        >>> stmt1 = select(User).where(User.name == "sandy")
        >>> stmt2 = select(User).where(User.name == "spongebob")
        >>> u = union_all(stmt1, stmt2)

    For a simple SELECT with UNION that is not already nested inside of a
    subquery, these
    can often be used in an ORM object fetching context by using the
    :meth:`_sql.Select.from_statement` method.  With this approach, the UNION
    statement represents the entire query; no additional
    criteria can be added after :meth:`_sql.Select.from_statement` is used::

        >>> orm_stmt = select(User).from_statement(u)
        >>> with Session(engine) as session:
        ...     for obj in session.execute(orm_stmt).scalars():
        ...         print(obj)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ? UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [generated in ...] ('sandy', 'spongebob')
        {stop}User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        {execsql}ROLLBACK{stop}

    To use a UNION or other set-related construct as an entity-related component in
    in a more flexible manner, the :class:`_sql.CompoundSelect` construct may be
    organized into a subquery using :meth:`_sql.CompoundSelect.subquery`, which
    then links to ORM objects using the :func:`_orm.aliased` function. This works
    in the same way introduced at :ref:`tutorial_subqueries_orm_aliased`, to first
    create an ad-hoc "mapping" of our desired entity to the subquery, then
    selecting from that new entity as though it were any other mapped class.
    In the example below, we are able to add additional criteria such as ORDER BY
    outside of the UNION itself, as we can filter or order by the columns exported
    by the subquery::

        >>> user_alias = aliased(User, u.subquery())
        >>> orm_stmt = select(user_alias).order_by(user_alias.id)
        >>> with Session(engine) as session:
        ...     for obj in session.execute(orm_stmt).scalars():
        ...         print(obj)
        {execsql}BEGIN (implicit)
        SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ? UNION ALL SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.name = ?) AS anon_1 ORDER BY anon_1.id
        [generated in ...] ('sandy', 'spongebob')
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        {execsql}ROLLBACK{stop}

    .. seealso::

        :ref:`orm_queryguide_unions` - in the :ref:`queryguide_toplevel`

.. _tutorial_exists:

EXISTS 子查询
^^^^^^^^^^^^^^^^^^

EXISTS subqueries

.. tab:: 中文

    SQL EXISTS 关键字是一个运算符，用于 :ref:`标量子查询 <tutorial_scalar_subquery>`，根据 SELECT 语句是否返回行来返回布尔值 true 或 false。SQLAlchemy 包含 :class:`_sql.ScalarSelect` 对象的变体，称为 :class:`_sql.Exists`，它将生成一个 EXISTS 子查询，并且最方便的是使用 :meth:`_sql.SelectBase.exists` 方法生成。下面我们生成一个 EXISTS，以便返回在 ``address`` 中有多于一行相关行的 ``user_account`` 行：

    .. sourcecode:: pycon+sql

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .having(func.count(address_table.c.id) > 1)
        ... ).exists()
        >>> with engine.connect() as conn:
        ...     result = conn.execute(select(user_table.c.name).where(subq))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name
        FROM user_account
        WHERE EXISTS (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id GROUP BY address.user_id
        HAVING count(address.id) > ?)
        [...] (1,){stop}
        [('sandy',)]
        {execsql}ROLLBACK{stop}

    EXISTS 构造更多地用作否定，例如 NOT EXISTS，因为它提供了一种 SQL 高效形式，用于查找相关表没有行的行。下面我们选择没有电子邮件地址的用户名；请注意在第二个 WHERE 子句中使用的二元否定运算符（ ``~`` ）：

    .. sourcecode:: pycon+sql

        >>> subq = (
        ...     select(address_table.c.id).where(user_table.c.id == address_table.c.user_id)
        ... ).exists()
        >>> with engine.connect() as conn:
        ...     result = conn.execute(select(user_table.c.name).where(~subq))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name
        FROM user_account
        WHERE NOT (EXISTS (SELECT address.id
        FROM address
        WHERE user_account.id = address.user_id))
        [...] (){stop}
        [('patrick',)]
        {execsql}ROLLBACK{stop}

.. tab:: 英文

    The SQL EXISTS keyword is an operator that is used with :ref:`scalar subqueries
    <tutorial_scalar_subquery>` to return a boolean true or false depending on if
    the SELECT statement would return a row.  SQLAlchemy includes a variant of the
    :class:`_sql.ScalarSelect` object called :class:`_sql.Exists`, which will
    generate an EXISTS subquery and is most conveniently generated using the
    :meth:`_sql.SelectBase.exists` method.  Below we produce an EXISTS so that we
    can return ``user_account`` rows that have more than one related row in
    ``address``:

    .. sourcecode:: pycon+sql

        >>> subq = (
        ...     select(func.count(address_table.c.id))
        ...     .where(user_table.c.id == address_table.c.user_id)
        ...     .group_by(address_table.c.user_id)
        ...     .having(func.count(address_table.c.id) > 1)
        ... ).exists()
        >>> with engine.connect() as conn:
        ...     result = conn.execute(select(user_table.c.name).where(subq))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name
        FROM user_account
        WHERE EXISTS (SELECT count(address.id) AS count_1
        FROM address
        WHERE user_account.id = address.user_id GROUP BY address.user_id
        HAVING count(address.id) > ?)
        [...] (1,){stop}
        [('sandy',)]
        {execsql}ROLLBACK{stop}

    The EXISTS construct is more often than not used as a negation, e.g. NOT EXISTS,
    as it provides a SQL-efficient form of locating rows for which a related
    table has no rows.  Below we select user names that have no email addresses;
    note the binary negation operator (``~``) used inside the second WHERE
    clause:

    .. sourcecode:: pycon+sql

        >>> subq = (
        ...     select(address_table.c.id).where(user_table.c.id == address_table.c.user_id)
        ... ).exists()
        >>> with engine.connect() as conn:
        ...     result = conn.execute(select(user_table.c.name).where(~subq))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT user_account.name
        FROM user_account
        WHERE NOT (EXISTS (SELECT address.id
        FROM address
        WHERE user_account.id = address.user_id))
        [...] (){stop}
        [('patrick',)]
        {execsql}ROLLBACK{stop}


.. _tutorial_functions:

使用 SQL 函数
^^^^^^^^^^^^^^^^^^^^^^^^^^

Working with SQL Functions

.. tab:: 中文

    在本节前面首次介绍的 :ref:`tutorial_group_by_w_aggregates`，:data:`_sql.func` 对象用作创建新的 :class:`_functions.Function` 对象的工厂，当在 :func:`_sql.select` 之类的构造中使用时，会生成一个 SQL 函数显示，通常由一个名称、一对括号（虽然不总是如此）和可能一些参数组成。典型的 SQL 函数示例如下：

    * ``count()`` 函数，一个聚合函数，用于计算返回的行数：

    .. sourcecode:: pycon+sql

        >>> print(select(func.count()).select_from(user_table))
        {printsql}SELECT count(*) AS count_1
        FROM user_account

    ..

    * ``lower()`` 函数，一个字符串函数，用于将字符串转换为小写：

    .. sourcecode:: pycon+sql

        >>> print(select(func.lower("A String With Much UPPERCASE")))
        {printsql}SELECT lower(:lower_2) AS lower_1

    ..

    * ``now()`` 函数，提供当前日期和时间；由于这是一个常见函数，SQLAlchemy 知道如何为每个后端以不同方式呈现，在 SQLite 的情况下使用 CURRENT_TIMESTAMP 函数：

    .. sourcecode:: pycon+sql

        >>> stmt = select(func.now())
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT CURRENT_TIMESTAMP AS now_1
        [...] ()
        [(datetime.datetime(...),)]
        ROLLBACK

    ..

    由于大多数数据库后端具有数十甚至数百种不同的 SQL 函数，:data:`_sql.func` 尽可能宽松地接受任何从该命名空间访问的名称都被自动视为一个 SQL 函数，这些函数将以通用方式呈现::

        >>> print(select(func.some_crazy_function(user_table.c.name, 17)))
        {printsql}SELECT some_crazy_function(user_account.name, :some_crazy_function_2) AS some_crazy_function_1
        FROM user_account

    同时，一小部分极为常见的 SQL 函数如 :class:`_functions.count`、:class:`_functions.now`、:class:`_functions.max`、:class:`_functions.concat` 包含预打包版本，提供适当的类型信息，并在某些情况下生成特定于后端的 SQL。下面的示例对比了 PostgreSQL 方言和 Oracle 数据库方言的 :class:`_functions.now` 函数的 SQL 生成：

        >>> from sqlalchemy.dialects import postgresql
        >>> print(select(func.now()).compile(dialect=postgresql.dialect()))
        {printsql}SELECT now() AS now_1{stop}
        >>> from sqlalchemy.dialects import oracle
        >>> print(select(func.now()).compile(dialect=oracle.dialect()))
        {printsql}SELECT CURRENT_TIMESTAMP AS now_1 FROM DUAL{stop}

.. tab:: 英文

    First introduced earlier in this section at
    :ref:`tutorial_group_by_w_aggregates`, the :data:`_sql.func` object serves as a
    factory for creating new :class:`_functions.Function` objects, which when used
    in a construct like :func:`_sql.select`, produce a SQL function display,
    typically consisting of a name, some parenthesis (although not always), and
    possibly some arguments. Examples of typical SQL functions include:

    * the ``count()`` function, an aggregate function which counts how many rows are returned:

    .. sourcecode:: pycon+sql

        >>> print(select(func.count()).select_from(user_table))
        {printsql}SELECT count(*) AS count_1
        FROM user_account

    ..

    * the ``lower()`` function, a string function that converts a string to lower case:

    .. sourcecode:: pycon+sql

        >>> print(select(func.lower("A String With Much UPPERCASE")))
        {printsql}SELECT lower(:lower_2) AS lower_1

    ..

    * the ``now()`` function, which provides for the current date and time; as this is a common function, SQLAlchemy knows how to render this differently for each backend, in the case of SQLite using the CURRENT_TIMESTAMP function:

    .. sourcecode:: pycon+sql

        >>> stmt = select(func.now())
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT CURRENT_TIMESTAMP AS now_1
        [...] ()
        [(datetime.datetime(...),)]
        ROLLBACK

    ..

    As most database backends feature dozens if not hundreds of different SQL
    functions, :data:`_sql.func` tries to be as liberal as possible in what it
    accepts. Any name that is accessed from this namespace is automatically
    considered to be a SQL function that will render in a generic way::

        >>> print(select(func.some_crazy_function(user_table.c.name, 17)))
        {printsql}SELECT some_crazy_function(user_account.name, :some_crazy_function_2) AS some_crazy_function_1
        FROM user_account

    At the same time, a relatively small set of extremely common SQL functions such
    as :class:`_functions.count`, :class:`_functions.now`, :class:`_functions.max`,
    :class:`_functions.concat` include pre-packaged versions of themselves which
    provide for proper typing information as well as backend-specific SQL
    generation in some cases.  The example below contrasts the SQL generation that
    occurs for the PostgreSQL dialect compared to the Oracle Database dialect for
    the :class:`_functions.now` function::

        >>> from sqlalchemy.dialects import postgresql
        >>> print(select(func.now()).compile(dialect=postgresql.dialect()))
        {printsql}SELECT now() AS now_1{stop}
        >>> from sqlalchemy.dialects import oracle
        >>> print(select(func.now()).compile(dialect=oracle.dialect()))
        {printsql}SELECT CURRENT_TIMESTAMP AS now_1 FROM DUAL{stop}

函数具有返回类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Functions Have Return Types

.. tab:: 中文

    函数是列表达式，因此它们也具有描述生成的 SQL 表达式的数据类型的 SQL :ref:`数据类型 <types_toplevel>`。我们在这里将这些类型称为“SQL 返回类型”，指的是函数在数据库端 SQL 表达式上下文中返回的 SQL 值的类型，而不是 Python 函数的“返回类型”。

    可以通过引用 :attr:`_functions.Function.type` 属性来访问任何 SQL 函数的 SQL 返回类型，通常用于调试目的；对于一些非常常见的 SQL 函数，此属性将预先配置，但对于大多数 SQL 函数，如果未另行指定，则为“null”数据类型::

        >>> # 预先配置的 SQL 函数（只有几十个）
        >>> func.now().type
        DateTime()

        >>> # 任意 SQL 函数（所有其他 SQL 函数）
        >>> func.run_some_calculation().type
        NullType()

    当在更大的表达式上下文中使用函数表达式时，这些 SQL 返回类型是重要的；也就是说，当表达式的数据类型是 :class:`_types.Integer` 或 :class:`_types.Numeric` 时，数学运算符将工作得更好，JSON 访问器需要使用 :class:`_types.JSON` 类型才能工作。某些类别的函数返回整个行而不是列值，需要引用特定列；这些函数称为 :ref:`表值函数 <tutorial_functions_table_valued>`。

    在执行语句并获取行时，函数的 SQL 返回类型也可能很重要，对于这些情况，SQLAlchemy 必须应用结果集处理。一个典型的例子是 SQLite 上的日期相关函数，其中 SQLAlchemy 的 :class:`_types.DateTime` 和相关数据类型在接收结果行时负责从字符串值转换为 Python ``datetime()`` 对象。

    要将特定类型应用于我们正在创建的函数，我们使用 :paramref:`_functions.Function.type_` 参数传递它；类型参数可以是 :class:`_types.TypeEngine` 类或实例。在下面的示例中，我们传递 :class:`_types.JSON` 类以生成 PostgreSQL ``json_object()`` 函数，注意到 SQL 返回类型将是 JSON 类型::

        >>> from sqlalchemy import JSON
        >>> function_expr = func.json_object('{a, 1, b, "def", c, 3.5}', type_=JSON)

    通过使用 :class:`_types.JSON` 数据类型创建我们的 JSON 函数，SQL 表达式对象具有 JSON 相关功能，例如访问元素::

        >>> stmt = select(function_expr["def"])
        >>> print(stmt)
        {printsql}SELECT json_object(:json_object_1)[:json_object_2] AS anon_1

.. tab:: 英文

    As functions are column expressions, they also have
    SQL :ref:`datatypes <types_toplevel>` that describe the data type of
    a generated SQL expression.  We refer to these types here as "SQL return types",
    in reference to the type of SQL value that is returned by the function
    in the context of a database-side SQL expression,
    as opposed to the "return type" of a Python function.

    The SQL return type of any SQL function may be accessed, typically for
    debugging purposes, by referring to the :attr:`_functions.Function.type`
    attribute; this will be pre-configured for a **select few** of extremely
    common SQL functions, but for most SQL functions is the "null" datatype
    if not otherwise specified::

        >>> # pre-configured SQL function (only a few dozen of these)
        >>> func.now().type
        DateTime()

        >>> # arbitrary SQL function (all other SQL functions)
        >>> func.run_some_calculation().type
        NullType()

    These SQL return types are significant when making
    use of the function expression in the context of a larger expression; that is,
    math operators will work better when the datatype of the expression is
    something like :class:`_types.Integer` or :class:`_types.Numeric`, JSON
    accessors in order to work need to be using a type such as
    :class:`_types.JSON`.  Certain classes of functions return entire rows
    instead of column values, where there is a need to refer to specific columns;
    such functions are known
    as :ref:`table valued functions <tutorial_functions_table_valued>`.

    The SQL return type of the function may also be significant when executing a
    statement and getting rows back, for those cases where SQLAlchemy has to apply
    result-set processing. A prime example of this are date-related functions on
    SQLite, where SQLAlchemy's :class:`_types.DateTime` and related datatypes take
    on the role of converting from string values to Python ``datetime()`` objects
    as result rows are received.

    To apply a specific type to a function we're creating, we pass it using the
    :paramref:`_functions.Function.type_` parameter; the type argument may be
    either a :class:`_types.TypeEngine` class or an instance.  In the example
    below we pass the :class:`_types.JSON` class to generate the PostgreSQL
    ``json_object()`` function, noting that the SQL return type will be of
    type JSON::

        >>> from sqlalchemy import JSON
        >>> function_expr = func.json_object('{a, 1, b, "def", c, 3.5}', type_=JSON)

    By creating our JSON function with the :class:`_types.JSON` datatype, the
    SQL expression object takes on JSON-related features, such as that of accessing
    elements::

        >>> stmt = select(function_expr["def"])
        >>> print(stmt)
        {printsql}SELECT json_object(:json_object_1)[:json_object_2] AS anon_1

内置函数具有预配置的返回类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Built-in Functions Have Pre-Configured Return Types

.. tab:: 中文

    对于常见的聚合函数如 :class:`_functions.count`、:class:`_functions.max`、:class:`_functions.min` 以及少量日期函数如 :class:`_functions.now` 和字符串函数如 :class:`_functions.concat`，SQL 返回类型已适当设置，有时基于使用情况。:class:`_functions.max` 函数和类似的聚合过滤函数将根据给定的参数设置 SQL 返回类型::

        >>> m1 = func.max(Column("some_int", Integer))
        >>> m1.type
        Integer()

        >>> m2 = func.max(Column("some_str", String))
        >>> m2.type
        String()

    日期和时间函数通常对应于由 :class:`_types.DateTime`、:class:`_types.Date` 或 :class:`_types.Time` 描述的 SQL 表达式::

        >>> func.now().type
        DateTime()
        >>> func.current_date().type
        Date()

    已知的字符串函数如 :class:`_functions.concat` 会知道 SQL 表达式的类型为 :class:`_types.String`::

        >>> func.concat("x", "y").type
        String()

    然而，对于绝大多数 SQL 函数，SQLAlchemy 并未在其非常小的已知函数列表中明确列出。例如，虽然通常没有问题使用 SQL 函数 ``func.lower()`` 和 ``func.upper()`` 转换字符串的大小写，但 SQLAlchemy 实际上并不知道这些函数，因此它们具有“null” SQL 返回类型::

        >>> func.upper("lowercase").type
        NullType()

    对于简单的函数如 ``upper`` 和 ``lower``，这个问题通常并不显著，因为字符串值可以从数据库中接收而无需 SQLAlchemy 端的任何特殊类型处理，SQLAlchemy 的类型转换规则通常也能正确猜测意图；例如，Python 的 ``+`` 运算符将根据表达式两边的内容正确解释为字符串连接运算符::

        >>> print(select(func.upper("lowercase") + " suffix"))
        {printsql}SELECT upper(:upper_1) || :upper_2 AS anon_1

    总体而言，可能需要 :paramref:`_functions.Function.type_` 参数的情景是：

    1. 该函数不是 SQLAlchemy 内置函数；这一点可以通过创建该函数并观察 :attr:`_functions.Function.type` 属性来证明，即::

        >>> func.count().type
        Integer()

    ..

    vs.::

        >>> func.json_object('{"a", "b"}').type
        NullType()

    2. 需要函数感知的表达式支持；这通常指与数据类型如 :class:`_types.JSON` 或 :class:`_types.ARRAY` 相关的特殊运算符

    3. 需要结果值处理，这可能包括类型如 :class:`_functions.DateTime`、:class:`_types.Boolean`、:class:`_types.Enum`，或再次是特殊数据类型如 :class:`_types.JSON`、:class:`_types.ARRAY`。

.. tab:: 英文

    For common aggregate functions like :class:`_functions.count`,
    :class:`_functions.max`, :class:`_functions.min` as well as a very small number
    of date functions like :class:`_functions.now` and string functions like
    :class:`_functions.concat`, the SQL return type is set up appropriately,
    sometimes based on usage. The :class:`_functions.max` function and similar
    aggregate filtering functions will set up the SQL return type based on the
    argument given::

        >>> m1 = func.max(Column("some_int", Integer))
        >>> m1.type
        Integer()

        >>> m2 = func.max(Column("some_str", String))
        >>> m2.type
        String()

    Date and time functions typically correspond to SQL expressions described by
    :class:`_types.DateTime`, :class:`_types.Date` or :class:`_types.Time`::

        >>> func.now().type
        DateTime()
        >>> func.current_date().type
        Date()

    A known string function such as :class:`_functions.concat`
    will know that a SQL expression would be of type :class:`_types.String`::

        >>> func.concat("x", "y").type
        String()

    However, for the vast majority of SQL functions, SQLAlchemy does not have them
    explicitly present in its very small list of known functions.  For example,
    while there is typically no issue using SQL functions ``func.lower()``
    and ``func.upper()`` to convert the casing of strings, SQLAlchemy doesn't
    actually know about these functions, so they have a "null" SQL return type::

        >>> func.upper("lowercase").type
        NullType()

    For simple functions like ``upper`` and ``lower``, the issue is not usually
    significant, as string values may be received from the database without any
    special type handling on the SQLAlchemy side, and SQLAlchemy's type
    coercion rules can often correctly guess intent as well; the Python ``+``
    operator for example will be correctly interpreted as the string concatenation
    operator based on looking at both sides of the expression::

        >>> print(select(func.upper("lowercase") + " suffix"))
        {printsql}SELECT upper(:upper_1) || :upper_2 AS anon_1

    Overall, the scenario where the
    :paramref:`_functions.Function.type_` parameter is likely necessary is:

    1. the function is not already a SQLAlchemy built-in function; this can be
    evidenced by creating the function and observing the :attr:`_functions.Function.type`
    attribute, that is::

        >>> func.count().type
        Integer()

    ..

    vs.::

        >>> func.json_object('{"a", "b"}').type
        NullType()

    2. Function-aware expression support is needed; this most typically refers to
    special operators related to datatypes such as :class:`_types.JSON` or
    :class:`_types.ARRAY`

    3. Result value processing is needed, which may include types such as
    :class:`_functions.DateTime`, :class:`_types.Boolean`, :class:`_types.Enum`,
    or again special datatypes such as :class:`_types.JSON`,
    :class:`_types.ARRAY`.

高级 SQL 函数技术
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Advanced SQL Function Techniques

.. tab:: 中文

    以下小节说明了更多可以用 SQL 函数完成的操作。虽然这些技术比基本的 SQL 函数使用更不常见且更高级，但它们仍然非常流行，主要是因为 PostgreSQL 强调更复杂的函数形式，包括表值和列值形式，这些形式在 JSON 数据中很受欢迎。

.. tab:: 英文

    The following subsections illustrate more things that can be done with
    SQL functions.  While these techniques are less common and more advanced than
    basic SQL function use, they nonetheless are extremely popular, largely
    as a result of PostgreSQL's emphasis on more complex function forms, including
    table- and column-valued forms that are popular with JSON data.

.. _tutorial_window_functions:

使用窗口函数
######################

Using Window Functions

.. tab:: 中文

    窗口函数是 SQL 聚合函数的一种特殊用法，它在处理各个结果行时计算在一个组内返回的行的聚合值。与 ``MAX()`` 这样的函数不同，后者会给出一组行中某列的最大值，而作为“窗口函数”使用的同一函数将为每一行提供 *该行* 的最大值。

    在 SQL 中，窗口函数允许指定应用函数的行，“分区”值考虑不同子集的窗口，以及“order by”表达式，重要的是它指示应用聚合函数的行顺序。

    在 SQLAlchemy 中，由 :data:`_sql.func` 命名空间生成的所有 SQL 函数都包含一个方法 :meth:`_functions.FunctionElement.over`，该方法授予窗口函数或“OVER”语法；生成的构造是 :class:`_sql.Over` 构造。

    一个常用的窗口函数是 ``row_number()`` 函数，它简单地对行进行计数。我们可以将此行计数分区到用户名，以对各个用户的电子邮件地址进行编号：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(
        ...         func.row_number().over(partition_by=user_table.c.name),
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT row_number() OVER (PARTITION BY user_account.name) AS anon_1,
        user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ()
        {stop}[(1, 'sandy', 'sandy@sqlalchemy.org'), (2, 'sandy', 'sandy@squirrelpower.org'), (1, 'spongebob', 'spongebob@sqlalchemy.org')]
        {printsql}ROLLBACK{stop}

    上面，:paramref:`_functions.FunctionElement.over.partition_by` 参数用于在 OVER 子句中呈现 ``PARTITION BY`` 子句。我们还可以使用 :paramref:`_functions.FunctionElement.over.order_by` 使用 ``ORDER BY`` 子句：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(
        ...         func.count().over(order_by=user_table.c.name),
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT count(*) OVER (ORDER BY user_account.name) AS anon_1,
        user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ()
        {stop}[(2, 'sandy', 'sandy@sql.org'), (2, 'sandy', 'sandy@squirrelpower.org'), (3, 'spongebob', 'spongebob@sqlalchemy.org')]
        {printsql}ROLLBACK{stop}

    窗口函数的更多选项包括范围的使用；有关更多示例，请参见 :func:`_expression.over`。

    .. tip::

        重要的是要注意 :meth:`_functions.FunctionElement.over` 方法仅适用于实际是聚合函数的 SQL 函数；虽然 :class:`_sql.Over` 构造将愉快地为给定的任何 SQL 函数呈现自己，但如果函数本身不是 SQL 聚合函数，数据库将拒绝该表达式。

.. tab:: 英文

    A window function is a special use of a SQL aggregate function which calculates
    the aggregate value over the rows being returned in a group as the individual
    result rows are processed.  Whereas a function like ``MAX()`` will give you
    the highest value of a column within a set of rows, using the same function
    as a "window function" will given you the highest value for each row,
    *as of that row*.

    In SQL, window functions allow one to specify the rows over which the
    function should be applied, a "partition" value which considers the window
    over different sub-sets of rows, and an "order by" expression which importantly
    indicates the order in which rows should be applied to the aggregate function.

    In SQLAlchemy, all SQL functions generated by the :data:`_sql.func` namespace
    include a method :meth:`_functions.FunctionElement.over` which
    grants the window function, or "OVER", syntax; the construct produced
    is the :class:`_sql.Over` construct.

    A common function used with window functions is the ``row_number()`` function
    which simply counts rows. We may partition this row count against user name to
    number the email addresses of individual users:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(
        ...         func.row_number().over(partition_by=user_table.c.name),
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT row_number() OVER (PARTITION BY user_account.name) AS anon_1,
        user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ()
        {stop}[(1, 'sandy', 'sandy@sqlalchemy.org'), (2, 'sandy', 'sandy@squirrelpower.org'), (1, 'spongebob', 'spongebob@sqlalchemy.org')]
        {printsql}ROLLBACK{stop}

    Above, the :paramref:`_functions.FunctionElement.over.partition_by` parameter
    is used so that the ``PARTITION BY`` clause is rendered within the OVER clause.
    We also may make use of the ``ORDER BY`` clause using :paramref:`_functions.FunctionElement.over.order_by`:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(
        ...         func.count().over(order_by=user_table.c.name),
        ...         user_table.c.name,
        ...         address_table.c.email_address,
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT count(*) OVER (ORDER BY user_account.name) AS anon_1,
        user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ()
        {stop}[(2, 'sandy', 'sandy@sqlalchemy.org'), (2, 'sandy', 'sandy@squirrelpower.org'), (3, 'spongebob', 'spongebob@sqlalchemy.org')]
        {printsql}ROLLBACK{stop}

    Further options for window functions include usage of ranges; see
    :func:`_expression.over` for more examples.

    .. tip::

        It's important to note that the :meth:`_functions.FunctionElement.over`
        method only applies to those SQL functions which are in fact aggregate
        functions; while the :class:`_sql.Over` construct will happily render itself
        for any SQL function given, the database will reject the expression if the
        function itself is not a SQL aggregate function.

.. _tutorial_functions_within_group:

特殊修饰符 WITHIN GROUP、FILTER
######################################

Special Modifiers WITHIN GROUP, FILTER

.. tab:: 中文

    “WITHIN GROUP” SQL 语法与“有序集合”或“假设集合”聚合函数结合使用。常见的“有序集合”函数包括 ``percentile_cont()`` 和 ``rank()``。SQLAlchemy 包括内置实现 :class:`_functions.rank`、:class:`_functions.dense_rank`、:class:`_functions.mode`、:class:`_functions.percentile_cont` 和 :class:`_functions.percentile_disc`，这些实现包括 :meth:`_functions.FunctionElement.within_group` 方法::

        >>> print(
        ...     func.unnest(
        ...         func.percentile_disc([0.25, 0.5, 0.75, 1]).within_group(user_table.c.name)
        ...     )
        ... )
        {printsql}unnest(percentile_disc(:percentile_disc_1) WITHIN GROUP (ORDER BY user_account.name))

    某些后端支持“FILTER”，与返回的总行范围相比，限制聚合函数的范围到特定子集行，可使用 :meth:`_functions.FunctionElement.filter` 方法获得::

        >>> stmt = (
        ...     select(
        ...         func.count(address_table.c.email_address).filter(user_table.c.name == "sandy"),
        ...         func.count(address_table.c.email_address).filter(
        ...             user_table.c.name == "spongebob"
        ...         ),
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT count(address.email_address) FILTER (WHERE user_account.name = ?) AS anon_1,
        count(address.email_address) FILTER (WHERE user_account.name = ?) AS anon_2
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ('sandy', 'spongebob')
        {stop}[(2, 1)]
        {execsql}ROLLBACK

.. tab:: 英文

    The "WITHIN GROUP" SQL syntax is used in conjunction with an "ordered set"
    or a "hypothetical set" aggregate
    function.  Common "ordered set" functions include ``percentile_cont()``
    and ``rank()``.  SQLAlchemy includes built in implementations
    :class:`_functions.rank`, :class:`_functions.dense_rank`,
    :class:`_functions.mode`, :class:`_functions.percentile_cont` and
    :class:`_functions.percentile_disc` which include a :meth:`_functions.FunctionElement.within_group`
    method::

        >>> print(
        ...     func.unnest(
        ...         func.percentile_disc([0.25, 0.5, 0.75, 1]).within_group(user_table.c.name)
        ...     )
        ... )
        {printsql}unnest(percentile_disc(:percentile_disc_1) WITHIN GROUP (ORDER BY user_account.name))

    "FILTER" is supported by some backends to limit the range of an aggregate function to a
    particular subset of rows compared to the total range of rows returned, available
    using the :meth:`_functions.FunctionElement.filter` method::

        >>> stmt = (
        ...     select(
        ...         func.count(address_table.c.email_address).filter(user_table.c.name == "sandy"),
        ...         func.count(address_table.c.email_address).filter(
        ...             user_table.c.name == "spongebob"
        ...         ),
        ...     )
        ...     .select_from(user_table)
        ...     .join(address_table)
        ... )
        >>> with engine.connect() as conn:  # doctest:+SKIP
        ...     result = conn.execute(stmt)
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        SELECT count(address.email_address) FILTER (WHERE user_account.name = ?) AS anon_1,
        count(address.email_address) FILTER (WHERE user_account.name = ?) AS anon_2
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] ('sandy', 'spongebob')
        {stop}[(2, 1)]
        {execsql}ROLLBACK

.. _tutorial_functions_table_valued:

表值函数
#######################

Table-Valued Functions

.. tab:: 中文

    表值 SQL 函数支持包含命名子元素的标量表示。通常用于 JSON 和 ARRAY 相关函数以及诸如 ``generate_series()`` 之类的函数，表值函数在 FROM 子句中指定，然后作为表或有时甚至作为列引用。这种形式的函数在 PostgreSQL 数据库中很突出，但 SQLite、Oracle 数据库和 SQL Server 也支持某些形式的表值函数。

    .. seealso::

        :ref:`postgresql_table_valued_overview` - 在 :ref:`postgresql_toplevel` 文档中。

        尽管许多数据库支持表值和其他特殊形式，但 PostgreSQL 是对这些功能需求最大的地方。请参阅本节，了解 PostgreSQL 语法的其他示例以及其他功能。

    SQLAlchemy 提供了 :meth:`_functions.FunctionElement.table_valued` 方法作为基本的“表值函数”构造，它将 :data:`_sql.func` 对象转换为包含一系列命名列的 FROM 子句，基于位置传递的字符串名称。它返回一个 :class:`_sql.TableValuedAlias` 对象，这是一个功能启用的 :class:`_sql.Alias` 构造，可以像 :ref:`tutorial_using_aliases` 中介绍的任何其他 FROM 子句一样使用。下面我们说明了 ``json_each()`` 函数，尽管它在 PostgreSQL 上很常见，但现代版本的 SQLite 也支持::

        >>> onetwothree = func.json_each('["one", "two", "three"]').table_valued("value")
        >>> stmt = select(onetwothree).where(onetwothree.c.value.in_(["two", "three"]))
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     result.all()
        {execsql}BEGIN (implicit)
        SELECT anon_1.value
        FROM json_each(?) AS anon_1
        WHERE anon_1.value IN (?, ?)
        [...] ('["one", "two", "three"]', 'two', 'three')
        {stop}[('two',), ('three',)]
        {execsql}ROLLBACK{stop}

    上面，我们使用了 SQLite 和 PostgreSQL 支持的 ``json_each()`` JSON 函数生成一个包含单列的表值表达式，该列称为 ``value``，然后选择了它的三行中的两行。

    .. seealso::

        :ref:`postgresql_table_valued` - 在 :ref:`postgresql_toplevel` 文档中 -
        本节将详细介绍其他语法，例如特殊列推导和已知在 PostgreSQL 上有效的“WITH ORDINALITY”。

.. tab:: 英文

    Table-valued SQL functions support a scalar representation that contains named
    sub-elements. Often used for JSON and ARRAY-oriented functions as well as
    functions like ``generate_series()``, the table-valued function is specified in
    the FROM clause, and is then referenced as a table, or sometimes even as a
    column. Functions of this form are prominent within the PostgreSQL database,
    however some forms of table valued functions are also supported by SQLite,
    Oracle Database, and SQL Server.

    .. seealso::

        :ref:`postgresql_table_valued_overview` - in the :ref:`postgresql_toplevel` documentation.

        While many databases support table valued and other special
        forms, PostgreSQL tends to be where there is the most demand for these
        features.   See this section for additional examples of PostgreSQL
        syntaxes as well as additional features.

    SQLAlchemy provides the :meth:`_functions.FunctionElement.table_valued` method
    as the basic "table valued function" construct, which will convert a
    :data:`_sql.func` object into a FROM clause containing a series of named
    columns, based on string names passed positionally. This returns a
    :class:`_sql.TableValuedAlias` object, which is a function-enabled
    :class:`_sql.Alias` construct that may be used as any other FROM clause as
    introduced at :ref:`tutorial_using_aliases`. Below we illustrate the
    ``json_each()`` function, which while common on PostgreSQL is also supported by
    modern versions of SQLite::

        >>> onetwothree = func.json_each('["one", "two", "three"]').table_valued("value")
        >>> stmt = select(onetwothree).where(onetwothree.c.value.in_(["two", "three"]))
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     result.all()
        {execsql}BEGIN (implicit)
        SELECT anon_1.value
        FROM json_each(?) AS anon_1
        WHERE anon_1.value IN (?, ?)
        [...] ('["one", "two", "three"]', 'two', 'three')
        {stop}[('two',), ('three',)]
        {execsql}ROLLBACK{stop}

    Above, we used the ``json_each()`` JSON function supported by SQLite and
    PostgreSQL to generate a table valued expression with a single column referred
    towards as ``value``, and then selected two of its three rows.

    .. seealso::

        :ref:`postgresql_table_valued` - in the :ref:`postgresql_toplevel` documentation -
        this section will detail additional syntaxes such as special column derivations
        and "WITH ORDINALITY" that are known to work with PostgreSQL.

.. _tutorial_functions_column_valued:

列值函数 - 表值函数作为标量列
##################################################################

Column Valued Functions - Table Valued Function as a Scalar Column

.. tab:: 中文

    PostgreSQL 和 Oracle 数据库支持的一种特殊语法是指在 FROM 子句中引用一个函数，然后在 SELECT 语句或其他列表达式上下文的列子句中将其作为单列交付。PostgreSQL 对这种语法的广泛使用包括 ``json_array_elements()``、``json_object_keys()``、``json_each_text()``、``json_each()`` 等函数。

    SQLAlchemy 将这种语法称为“列值”函数，可以通过将 :meth:`_functions.FunctionElement.column_valued` 修饰符应用于 :class:`_functions.Function` 构造来实现::

        >>> from sqlalchemy import select, func
        >>> stmt = select(func.json_array_elements('["one", "two"]').column_valued("x"))
        >>> print(stmt)
        {printsql}SELECT x
        FROM json_array_elements(:json_array_elements_1) AS x

    “列值”形式也受到 Oracle 数据库方言的支持，可用于自定义 SQL 函数::

        >>> from sqlalchemy.dialects import oracle
        >>> stmt = select(func.scalar_strings(5).column_valued("s"))
        >>> print(stmt.compile(dialect=oracle.dialect()))
        {printsql}SELECT s.COLUMN_VALUE
        FROM TABLE (scalar_strings(:scalar_strings_1)) s


    .. seealso::

        :ref:`postgresql_column_valued` - 在 :ref:`postgresql_toplevel` 文档中。

.. tab:: 英文

    A special syntax supported by PostgreSQL and Oracle Database is that of
    referring towards a function in the FROM clause, which then delivers itself as
    a single column in the columns clause of a SELECT statement or other column
    expression context.  PostgreSQL makes great use of this syntax for such
    functions as ``json_array_elements()``, ``json_object_keys()``,
    ``json_each_text()``, ``json_each()``, etc.

    SQLAlchemy refers to this as a "column valued" function and is available
    by applying the :meth:`_functions.FunctionElement.column_valued` modifier
    to a :class:`_functions.Function` construct::

        >>> from sqlalchemy import select, func
        >>> stmt = select(func.json_array_elements('["one", "two"]').column_valued("x"))
        >>> print(stmt)
        {printsql}SELECT x
        FROM json_array_elements(:json_array_elements_1) AS x

    The "column valued" form is also supported by the Oracle Database dialects,
    where it is usable for custom SQL functions::

        >>> from sqlalchemy.dialects import oracle
        >>> stmt = select(func.scalar_strings(5).column_valued("s"))
        >>> print(stmt.compile(dialect=oracle.dialect()))
        {printsql}SELECT s.COLUMN_VALUE
        FROM TABLE (scalar_strings(:scalar_strings_1)) s


    .. seealso::

        :ref:`postgresql_column_valued` - in the :ref:`postgresql_toplevel` documentation.

.. _tutorial_casts:

数据强制转换和类型强制转换
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data Casts and Type Coercion

.. tab:: 中文

    在 SQL 中，我们经常需要显式地指示表达式的数据类型，或者告诉数据库在一个模糊的表达式中预期的数据类型，或者在某些情况下，我们想将 SQL 表达式的隐含数据类型转换为其他类型。SQL CAST 关键字用于此任务，在 SQLAlchemy 中由 :func:`.cast` 函数提供。此函数接受列表达式和数据类型对象作为参数，如下所示，我们从 ``user_table.c.id`` 列对象生成 SQL 表达式 ``CAST(user_account.id AS VARCHAR)``::

        >>> from sqlalchemy import cast
        >>> stmt = select(cast(user_table.c.id, String))
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     result.all()
        {execsql}BEGIN (implicit)
        SELECT CAST(user_account.id AS VARCHAR) AS id
        FROM user_account
        [...] ()
        {stop}[('1',), ('2',), ('3',)]
        {execsql}ROLLBACK{stop}

    :func:`.cast` 函数不仅呈现 SQL CAST 语法，还生成一个 SQLAlchemy 列表达式，该表达式在 Python 端也将作为给定的数据类型。例如，一个被 :func:`.cast` 为 :class:`_sqltypes.JSON` 的字符串表达式将获得 JSON 下标和比较运算符::

        >>> from sqlalchemy import JSON
        >>> print(cast("{'a': 'b'}", JSON)["a"])
        {printsql}CAST(:param_1 AS JSON)[:param_2]

.. tab:: 英文

    In SQL, we often need to indicate the datatype of an expression explicitly,
    either to tell the database what type is expected in an otherwise ambiguous
    expression, or in some cases when we want to convert the implied datatype
    of a SQL expression into something else.   The SQL CAST keyword is used for
    this task, which in SQLAlchemy is provided by the :func:`.cast` function.
    This function accepts a column expression and a data type
    object as arguments, as demonstrated below where we produce a SQL expression
    ``CAST(user_account.id AS VARCHAR)`` from the ``user_table.c.id`` column
    object::

        >>> from sqlalchemy import cast
        >>> stmt = select(cast(user_table.c.id, String))
        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     result.all()
        {execsql}BEGIN (implicit)
        SELECT CAST(user_account.id AS VARCHAR) AS id
        FROM user_account
        [...] ()
        {stop}[('1',), ('2',), ('3',)]
        {execsql}ROLLBACK{stop}

    The :func:`.cast` function not only renders the SQL CAST syntax, it also
    produces a SQLAlchemy column expression that will act as the given datatype on
    the Python side as well. A string expression that is :func:`.cast` to
    :class:`_sqltypes.JSON` will gain JSON subscript and comparison operators, for example::

        >>> from sqlalchemy import JSON
        >>> print(cast("{'a': 'b'}", JSON)["a"])
        {printsql}CAST(:param_1 AS JSON)[:param_2]


type_coerce() - 仅限 Python 的“强制转换”
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

type_coerce() - a Python-only "cast"

.. tab:: 中文

    有时需要让 SQLAlchemy 知道表达式的数据类型，出于上述所有原因，但不要在 SQL 端呈现 CAST 表达式，因为它可能会干扰已经可以正常工作的 SQL 操作。对于这种相当常见的用例，有另一个函数 :func:`.type_coerce` 与 :func:`.cast` 密切相关，因为它将 Python 表达式设置为具有特定的 SQL 数据库类型，但不会在数据库端呈现 ``CAST`` 关键字或数据类型。:func:`.type_coerce` 在处理 :class:`_types.JSON` 数据类型时特别重要，因为它通常与不同平台上的字符串导向数据类型有着复杂的关系，甚至可能不是显式的数据类型，如在 SQLite 和 MariaDB 上。下面，我们使用 :func:`.type_coerce` 将 Python 结构作为 JSON 字符串传递到 MySQL 的一个 JSON 函数中：

    .. sourcecode:: pycon+sql

        >>> import json
        >>> from sqlalchemy import JSON
        >>> from sqlalchemy import type_coerce
        >>> from sqlalchemy.dialects import mysql
        >>> s = select(type_coerce({"some_key": {"foo": "bar"}}, JSON)["some_key"])
        >>> print(s.compile(dialect=mysql.dialect()))
        {printsql}SELECT JSON_EXTRACT(%s, %s) AS anon_1

    上面，MySQL 的 ``JSON_EXTRACT`` SQL 函数被调用，因为我们使用 :func:`.type_coerce` 指示我们的 Python 字典应被视为 :class:`_types.JSON`。Python 的 ``__getitem__`` 运算符，在本例中为 ``['some_key']``，因此可用并允许呈现 ``JSON_EXTRACT`` 路径表达式（未显示，但在本例中最终将是 ``'$."some_key"'``）。

.. tab:: 英文

    Sometimes there is the need to have SQLAlchemy know the datatype of an
    expression, for all the reasons mentioned above, but to not render the CAST
    expression itself on the SQL side, where it may interfere with a SQL operation
    that already works without it.  For this fairly common use case there is
    another function :func:`.type_coerce` which is closely related to
    :func:`.cast`, in that it sets up a Python expression as having a specific SQL
    database type, but does not render the ``CAST`` keyword or datatype on the
    database side.    :func:`.type_coerce` is particularly important when dealing
    with the :class:`_types.JSON` datatype, which typically has an intricate
    relationship with string-oriented datatypes on different platforms and
    may not even be an explicit datatype, such as on SQLite and MariaDB.
    Below, we use :func:`.type_coerce` to deliver a Python structure as a JSON
    string into one of MySQL's JSON functions:

    .. sourcecode:: pycon+sql

        >>> import json
        >>> from sqlalchemy import JSON
        >>> from sqlalchemy import type_coerce
        >>> from sqlalchemy.dialects import mysql
        >>> s = select(type_coerce({"some_key": {"foo": "bar"}}, JSON)["some_key"])
        >>> print(s.compile(dialect=mysql.dialect()))
        {printsql}SELECT JSON_EXTRACT(%s, %s) AS anon_1

    Above, MySQL's ``JSON_EXTRACT`` SQL function was invoked
    because we used :func:`.type_coerce` to indicate that our Python dictionary
    should be treated as :class:`_types.JSON`.  The Python ``__getitem__``
    operator, ``['some_key']`` in this case, became available as a result and
    allowed a ``JSON_EXTRACT`` path expression (not shown, however in this
    case it would ultimately be ``'$."some_key"'``) to be rendered.
