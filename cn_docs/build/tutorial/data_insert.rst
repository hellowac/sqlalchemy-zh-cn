.. highlight:: pycon+sql

.. |prev| replace:: :doc:`data`
.. |next| replace:: :doc:`data_select`

.. include:: tutorial_nav_include.rst

.. rst-class:: core-header, orm-addin

.. _tutorial_core_insert:

使用 INSERT 语句
-----------------------

Using INSERT Statements

.. tab:: 中文

    使用 Core 以及在进行批量操作时使用 ORM 时，直接使用 :func:`_sql.insert` 函数生成 SQL INSERT 语句 - 该函数生成一个新的 :class:`_sql.Insert` 实例，表示 SQL 中的 INSERT 语句，用于向表中添加新数据。

    .. container:: orm-header

        **ORM 读者** -

        本节详细介绍了 Core 生成单个 SQL INSERT 语句以向表中添加新行的方式。使用 ORM 时，我们通常使用另一个工具，即 :term:`unit of work`，它将自动生成多个 INSERT 语句。然而，即使在 ORM 为我们运行时，了解 Core 如何处理数据创建和操作也非常有用。此外，ORM 支持直接使用 INSERT，使用称为 :ref:`tutorial_orm_bulk` 的功能。

        要直接跳到如何使用正常的工作单元模式使用 ORM 插入行，请参阅 :ref:`tutorial_inserting_orm`。

.. tab:: 英文

    When using Core as well as when using the ORM for bulk operations, a SQL INSERT
    statement is generated directly using the :func:`_sql.insert` function - this
    function generates a new instance of :class:`_sql.Insert` which represents an
    INSERT statement in SQL, that adds new data into a table.

    .. container:: orm-header

        **ORM Readers** -

        This section details the Core means of generating an individual SQL INSERT
        statement in order to add new rows to a table. When using the ORM, we
        normally use another tool that rides on top of this called the
        :term:`unit of work`, which will automate the production of many INSERT
        statements at once. However, understanding how the Core handles data
        creation and manipulation is very useful even when the ORM is running
        it for us.  Additionally, the ORM supports direct use of INSERT
        using a feature called :ref:`tutorial_orm_bulk`.

        To skip directly to how to INSERT rows with the ORM using normal
        unit of work patterns, see :ref:`tutorial_inserting_orm`.


insert() SQL 表达式构造
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The insert() SQL Expression Construct

.. tab:: 中文

    一个简单的 :class:`_sql.Insert` 示例，展示目标表和 VALUES 子句::

        >>> from sqlalchemy import insert
        >>> stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")

    上面的 ``stmt`` 变量是 :class:`_sql.Insert` 的一个实例。大多数 SQL 表达式可以直接字符串化，以查看生成的内容的一般形式::

        >>> print(stmt)
        {printsql}INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)

    字符串化形式是通过生成对象的 :class:`_engine.Compiled` 形式创建的，其中包括语句的数据库特定字符串 SQL 表示；我们可以使用 :meth:`_sql.ClauseElement.compile` 方法直接获取此对象::

        >>> compiled = stmt.compile()

    我们的 :class:`_sql.Insert` 构造是一个“参数化”构造的示例，之前在 :ref:`tutorial_sending_parameters` 中说明；要查看 ``name`` 和 ``fullname`` :term:`bound parameters`，这些也可以从 :class:`_engine.Compiled` 构造中获取::

        >>> compiled.params
        {'name': 'spongebob', 'fullname': 'Spongebob Squarepants'}

.. tab:: 英文

    A simple example of :class:`_sql.Insert` illustrating the target table
    and the VALUES clause at once::

        >>> from sqlalchemy import insert
        >>> stmt = insert(user_table).values(name="spongebob", fullname="Spongebob Squarepants")

    The above ``stmt`` variable is an instance of :class:`_sql.Insert`.  Most
    SQL expressions can be stringified in place as a means to see the general
    form of what's being produced::

        >>> print(stmt)
        {printsql}INSERT INTO user_account (name, fullname) VALUES (:name, :fullname)

    The stringified form is created by producing a :class:`_engine.Compiled` form
    of the object which includes a database-specific string SQL representation of
    the statement; we can acquire this object directly using the
    :meth:`_sql.ClauseElement.compile` method::

        >>> compiled = stmt.compile()

    Our :class:`_sql.Insert` construct is an example of a "parameterized"
    construct, illustrated previously at :ref:`tutorial_sending_parameters`; to
    view the ``name`` and ``fullname`` :term:`bound parameters`, these are
    available from the :class:`_engine.Compiled` construct as well::

        >>> compiled.params
        {'name': 'spongebob', 'fullname': 'Spongebob Squarepants'}


执行语句
^^^^^^^^^^^^^^^^^^^^^^^

Executing the Statement

.. tab:: 中文

    通过执行该语句，我们可以在 ``user_table`` 中插入一行。
    INSERT SQL 以及捆绑的参数可以在 SQL 日志中看到：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] ('spongebob', 'Spongebob Squarepants')
        COMMIT

    在上面的简单形式中，INSERT 语句不返回任何行，如果仅插入一行，通常会包括返回在插入该行期间生成的列级默认值信息的功能，最常见的是整数主键值。在上述情况下，SQLite 数据库中的第一行通常会返回第一个整数主键值 ``1``，我们可以使用 :attr:`_engine.CursorResult.inserted_primary_key` 访问器获取：

    .. sourcecode:: pycon+sql

        >>> result.inserted_primary_key
        (1,)

    .. tip:: 
        
        :attr:`_engine.CursorResult.inserted_primary_key` 返回一个元组，因为主键可能包含多个列。这被称为 :term:`composite primary key`。:attr:`_engine.CursorResult.inserted_primary_key` 旨在始终包含刚插入记录的完整主键，而不仅仅是“cursor.lastrowid”类型的值，并且无论是否使用“自增”，都旨在填充，因此为了表达完整的主键，它是一个元组。

    .. versionchanged:: 1.4.8 
        
        由 :attr:`_engine.CursorResult.inserted_primary_key` 返回的元组现在是一个命名元组，通过将其返回为 :class:`_result.Row` 对象来实现。

.. tab:: 英文

    Invoking the statement we can INSERT a row into ``user_table``.
    The INSERT SQL as well as the bundled parameters can be seen in the
    SQL logging:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(stmt)
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] ('spongebob', 'Spongebob Squarepants')
        COMMIT

    In its simple form above, the INSERT statement does not return any rows, and if
    only a single row is inserted, it will usually include the ability to return
    information about column-level default values that were generated during the
    INSERT of that row, most commonly an integer primary key value.  In the above
    case the first row in a SQLite database will normally return ``1`` for the
    first integer primary key value, which we can acquire using the
    :attr:`_engine.CursorResult.inserted_primary_key` accessor:

    .. sourcecode:: pycon+sql

        >>> result.inserted_primary_key
        (1,)

    .. tip:: :attr:`_engine.CursorResult.inserted_primary_key` returns a tuple
    because a primary key may contain multiple columns.  This is known as
    a :term:`composite primary key`.  The :attr:`_engine.CursorResult.inserted_primary_key`
    is intended to always contain the complete primary key of the record just
    inserted, not just a "cursor.lastrowid" kind of value, and is also intended
    to be populated regardless of whether or not "autoincrement" were used, hence
    to express a complete primary key it's a tuple.

    .. versionchanged:: 1.4.8 the tuple returned by
    :attr:`_engine.CursorResult.inserted_primary_key` is now a named tuple
    fulfilled by returning it as a :class:`_result.Row` object.

.. _tutorial_core_insert_values_clause:

INSERT 通常会自动生成“values”子句
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

INSERT usually generates the "values" clause automatically

.. tab:: 中文

    示例中使用了 :meth:`_sql.Insert.values` 方法来显式创建 SQL INSERT 语句的 VALUES 子句。如果我们不实际使用 :meth:`_sql.Insert.values` 并仅打印出一个“空”语句，我们会得到一个包含表中每一列的 INSERT::

        >>> print(insert(user_table))
        {printsql}INSERT INTO user_account (id, name, fullname) VALUES (:id, :name, :fullname)

    如果我们使用尚未调用 :meth:`_sql.Insert.values` 的 :class:`_sql.Insert` 构造并执行它而不是打印它，该语句将基于我们传递给 :meth:`_engine.Connection.execute` 方法的参数编译为字符串，并仅包括与传递的参数相关的列。这实际上是使用 :class:`_sql.Insert` 插入行的常用方法，无需键入显式 VALUES 子句。下面的示例说明了一个带有一组参数的两列 INSERT 语句的执行：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         insert(user_table),
        ...         [
        ...             {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...             {"name": "patrick", "fullname": "Patrick Star"},
        ...         ],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] [('sandy', 'Sandy Cheeks'), ('patrick', 'Patrick Star')]
        COMMIT{stop}

    上面的执行采用了在 :ref:`tutorial_multiple_parameters` 中首次介绍的“executemany”形式，但与使用 :func:`_sql.text` 构造不同，我们不需要拼出任何 SQL。通过将字典或字典列表传递给与 :class:`_sql.Insert` 构造结合使用的 :meth:`_engine.Connection.execute` 方法，:class:`_engine.Connection` 确保传递的列名将自动在 :class:`_sql.Insert` 构造的 VALUES 子句中表示。

    .. deepalchemy::

        嗨，欢迎来到 **深度炼金术(Deep Alchemy)** 的第一版。左边的人被称为 **炼金术士(The Alchemist)** ，你会注意到他们 **不是** 巫师，因为尖顶帽子没有向上翘。炼金术士来解释通常 **更高级和/或复杂(more advanced and/or tricky)** 且 **通常不需要(not usually needed)** 的内容，但无论出于何种原因，他们认为你应该了解 SQLAlchemy 能做的这个事情。

        在本版中，为了在 ``address_table`` 中也有一些有趣的数据，下面是一个更高级的示例，说明如何在同时包括从参数生成的附加 VALUES 的情况下显式使用 :meth:`_sql.Insert.values` 方法。构造了一个 :term:`scalar subquery`，使用了在下一节中介绍的 :func:`_sql.select` 构造，子查询中使用的参数使用 :func:`_sql.bindparam` 构造显式设置绑定参数名称。

        这是一些稍微 **更深(deeper)** 的炼金术，我们可以添加相关的行而不需要将 ``user_table`` 操作的主键标识符获取到应用程序中。大多数炼金术士将简单地使用 ORM，它会为我们处理类似的事情。

        .. sourcecode:: pycon+sql

            >>> from sqlalchemy import select, bindparam
            >>> scalar_subq = (
            ...     select(user_table.c.id)
            ...     .where(user_table.c.name == bindparam("username"))
            ...     .scalar_subquery()
            ... )

            >>> with engine.connect() as conn:
            ...     result = conn.execute(
            ...         insert(address_table).values(user_id=scalar_subq),
            ...         [
            ...             {
            ...                 "username": "spongebob",
            ...                 "email_address": "spongebob@sqlalchemy.org",
            ...             },
            ...             {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
            ...             {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
            ...         ],
            ...     )
            ...     conn.commit()
            {execsql}BEGIN (implicit)
            INSERT INTO address (user_id, email_address) VALUES ((SELECT user_account.id
            FROM user_account
            WHERE user_account.name = ?), ?)
            [...] [('spongebob', 'spongebob@sqlalchemy.org'), ('sandy', 'sandy@sqlalchemy.org'),
            ('sandy', 'sandy@squirrelpower.org')]
            COMMIT{stop}

        有了这些，我们的表中有了一些更有趣的数据，我们将在接下来的部分中使用这些数据。

    .. tip:: 
        
        如果我们指示 :meth:`_sql.Insert.values` 不带任何参数，则生成一个真正的“空” INSERT，它仅插入表的“默认值”而不包含任何显式值；并非每个数据库后端都支持此功能，但这是 SQLite 生成的内容::

        >>> print(insert(user_table).values().compile(engine))
        {printsql}INSERT INTO user_account DEFAULT VALUES

.. tab:: 英文

    The example above made use of the :meth:`_sql.Insert.values` method to
    explicitly create the VALUES clause of the SQL INSERT statement.   If
    we don't actually use :meth:`_sql.Insert.values` and just print out an "empty"
    statement, we get an INSERT for every column in the table::

        >>> print(insert(user_table))
        {printsql}INSERT INTO user_account (id, name, fullname) VALUES (:id, :name, :fullname)

    If we take an :class:`_sql.Insert` construct that has not had
    :meth:`_sql.Insert.values` called upon it and execute it
    rather than print it, the statement will be compiled to a string based
    on the parameters that we passed to the :meth:`_engine.Connection.execute`
    method, and only include columns relevant to the parameters that were
    passed.   This is actually the usual way that
    :class:`_sql.Insert` is used to insert rows without having to type out
    an explicit VALUES clause.   The example below illustrates a two-column
    INSERT statement being executed with a list of parameters at once:


    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(
        ...         insert(user_table),
        ...         [
        ...             {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...             {"name": "patrick", "fullname": "Patrick Star"},
        ...         ],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] [('sandy', 'Sandy Cheeks'), ('patrick', 'Patrick Star')]
        COMMIT{stop}

    The execution above features "executemany" form first illustrated at
    :ref:`tutorial_multiple_parameters`, however unlike when using the
    :func:`_sql.text` construct, we didn't have to spell out any SQL.
    By passing a dictionary or list of dictionaries to the :meth:`_engine.Connection.execute`
    method in conjunction with the :class:`_sql.Insert` construct, the
    :class:`_engine.Connection` ensures that the column names which are passed
    will be expressed in the VALUES clause of the :class:`_sql.Insert`
    construct automatically.

    .. deepalchemy::

        Hi, welcome to the first edition of **Deep Alchemy**.   The person on the
        left is known as **The Alchemist**, and you'll note they are **not** a wizard,
        as the pointy hat is not sticking upwards.   The Alchemist comes around to
        describe things that are generally **more advanced and/or tricky** and
        additionally **not usually needed**, but for whatever reason they feel you
        should know about this thing that SQLAlchemy can do.

        In this edition, towards the goal of having some interesting data in the
        ``address_table`` as well, below is a more advanced example illustrating
        how the :meth:`_sql.Insert.values` method may be used explicitly while at
        the same time including for additional VALUES generated from the
        parameters.    A :term:`scalar subquery` is constructed, making use of the
        :func:`_sql.select` construct introduced in the next section, and the
        parameters used in the subquery are set up using an explicit bound
        parameter name, established using the :func:`_sql.bindparam` construct.

        This is some slightly **deeper** alchemy just so that we can add related
        rows without fetching the primary key identifiers from the ``user_table``
        operation into the application.   Most Alchemists will simply use the ORM
        which takes care of things like this for us.

        .. sourcecode:: pycon+sql

            >>> from sqlalchemy import select, bindparam
            >>> scalar_subq = (
            ...     select(user_table.c.id)
            ...     .where(user_table.c.name == bindparam("username"))
            ...     .scalar_subquery()
            ... )

            >>> with engine.connect() as conn:
            ...     result = conn.execute(
            ...         insert(address_table).values(user_id=scalar_subq),
            ...         [
            ...             {
            ...                 "username": "spongebob",
            ...                 "email_address": "spongebob@sqlalchemy.org",
            ...             },
            ...             {"username": "sandy", "email_address": "sandy@sqlalchemy.org"},
            ...             {"username": "sandy", "email_address": "sandy@squirrelpower.org"},
            ...         ],
            ...     )
            ...     conn.commit()
            {execsql}BEGIN (implicit)
            INSERT INTO address (user_id, email_address) VALUES ((SELECT user_account.id
            FROM user_account
            WHERE user_account.name = ?), ?)
            [...] [('spongebob', 'spongebob@sqlalchemy.org'), ('sandy', 'sandy@sqlalchemy.org'),
            ('sandy', 'sandy@squirrelpower.org')]
            COMMIT{stop}

        With that, we have some more interesting data in our tables that we will
        make use of in the upcoming sections.

    .. tip:: 
        
        A true "empty" INSERT that inserts only the "defaults" for a table without including any explicit values at all is generated if we indicate :meth:`_sql.Insert.values` with no arguments; not every database backend supports this, but here's what SQLite produces::

        >>> print(insert(user_table).values().compile(engine))
        {printsql}INSERT INTO user_account DEFAULT VALUES


.. _tutorial_insert_returning:

INSERT...RETURNING
^^^^^^^^^^^^^^^^^^^^^

.. tab:: 中文

    对于支持的后端，RETURNING 子句会自动使用以检索最后插入的主键值以及服务器默认值。然而，也可以使用 :meth:`_sql.Insert.returning` 方法显式指定 RETURNING 子句；在这种情况下，执行语句时返回的 :class:`_engine.Result` 对象包含可以获取的行::

        >>> insert_stmt = insert(address_table).returning(
        ...     address_table.c.id, address_table.c.email_address
        ... )
        >>> print(insert_stmt)
        {printsql}INSERT INTO address (id, user_id, email_address)
        VALUES (:id, :user_id, :email_address)
        RETURNING address.id, address.email_address

    它还可以与 :meth:`_sql.Insert.from_select` 结合使用，如下面的示例所示，构建在 :ref:`tutorial_insert_from_select` 中提到的示例之上::

        >>> select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
        >>> insert_stmt = insert(address_table).from_select(
        ...     ["user_id", "email_address"], select_stmt
        ... )
        >>> print(insert_stmt.returning(address_table.c.id, address_table.c.email_address))
        {printsql}INSERT INTO address (user_id, email_address)
        SELECT user_account.id, user_account.name || :name_1 AS anon_1
        FROM user_account RETURNING address.id, address.email_address

    .. tip::

        RETURNING 功能还支持 UPDATE 和 DELETE 语句，这将在本教程的后面介绍。

        对于 INSERT 语句，RETURNING 功能可用于单行语句以及一次插入多行的语句。支持 RETURNING 的多行 INSERT 是特定于方言的，但对于支持 RETURNING 的所有 SQLAlchemy 包含的方言均支持此功能。有关此功能的背景信息，请参阅部分 :ref:`engine_insertmanyvalues`。

    .. seealso::

        ORM 也支持带或不带 RETURNING 的批量 INSERT。参考文档请参阅 :ref:`orm_queryguide_bulk_insert`。

.. tab:: 英文

    The RETURNING clause for supported backends is used
    automatically in order to retrieve the last inserted primary key value
    as well as the values for server defaults.   However the RETURNING clause
    may also be specified explicitly using the :meth:`_sql.Insert.returning`
    method; in this case, the :class:`_engine.Result`
    object that's returned when the statement is executed has rows which
    can be fetched::

        >>> insert_stmt = insert(address_table).returning(
        ...     address_table.c.id, address_table.c.email_address
        ... )
        >>> print(insert_stmt)
        {printsql}INSERT INTO address (id, user_id, email_address)
        VALUES (:id, :user_id, :email_address)
        RETURNING address.id, address.email_address

    It can also be combined with :meth:`_sql.Insert.from_select`,
    as in the example below that builds upon the example stated in
    :ref:`tutorial_insert_from_select`::

        >>> select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
        >>> insert_stmt = insert(address_table).from_select(
        ...     ["user_id", "email_address"], select_stmt
        ... )
        >>> print(insert_stmt.returning(address_table.c.id, address_table.c.email_address))
        {printsql}INSERT INTO address (user_id, email_address)
        SELECT user_account.id, user_account.name || :name_1 AS anon_1
        FROM user_account RETURNING address.id, address.email_address

    .. tip::

        The RETURNING feature is also supported by UPDATE and DELETE statements,
        which will be introduced later in this tutorial.

        For INSERT statements, the RETURNING feature may be used
        both for single-row statements as well as for statements that INSERT
        multiple rows at once.  Support for multiple-row INSERT with RETURNING
        is dialect specific, however is supported for all the dialects
        that are included in SQLAlchemy which support RETURNING.  See the section
        :ref:`engine_insertmanyvalues` for background on this feature.

    .. seealso::

        Bulk INSERT with or without RETURNING is also supported by the ORM.  See
        :ref:`orm_queryguide_bulk_insert` for reference documentation.



.. _tutorial_insert_from_select:

INSERT...FROM SELECT
^^^^^^^^^^^^^^^^^^^^^

.. tab:: 中文

    一个较少使用但为完整性考虑而存在的 :class:`_sql.Insert` 特性是，:class:`_sql.Insert` 构造可以通过 :meth:`_sql.Insert.from_select` 方法直接从 SELECT 获取行来组成 INSERT。这种方法接受一个 :func:`_sql.select` 构造和一列列名列表，目标是实际 INSERT 中的列。在下面的示例中，行被添加到 ``address`` 表中，这些行是从 ``user_account`` 表中派生的，给每个用户一个免费的 ``aol.com`` 电子邮件地址::

        >>> select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
        >>> insert_stmt = insert(address_table).from_select(
        ...     ["user_id", "email_address"], select_stmt
        ... )
        >>> print(insert_stmt)
        {printsql}INSERT INTO address (user_id, email_address)
        SELECT user_account.id, user_account.name || :name_1 AS anon_1
        FROM user_account

    这种构造用于当希望将数据从数据库的某些其他部分直接复制到一组新行中，而无需实际从客户端获取和重新发送数据时。

    .. seealso::

        :class:`_sql.Insert` - 在 SQL 表达式 API 文档中

.. tab:: 英文

    A less used feature of :class:`_sql.Insert`, but here for completeness, the
    :class:`_sql.Insert` construct can compose an INSERT that gets rows directly
    from a SELECT using the :meth:`_sql.Insert.from_select` method.
    This method accepts a :func:`_sql.select` construct, which is discussed in the
    next section, along with a list of column names to be targeted in the
    actual INSERT.  In the example below, rows are added to the ``address``
    table which are derived from rows in the ``user_account`` table, giving each
    user a free email address at ``aol.com``::

        >>> select_stmt = select(user_table.c.id, user_table.c.name + "@aol.com")
        >>> insert_stmt = insert(address_table).from_select(
        ...     ["user_id", "email_address"], select_stmt
        ... )
        >>> print(insert_stmt)
        {printsql}INSERT INTO address (user_id, email_address)
        SELECT user_account.id, user_account.name || :name_1 AS anon_1
        FROM user_account

    This construct is used when one wants to copy data from
    some other part of the database directly into a new set of rows, without
    actually fetching and re-sending the data from the client.


    .. seealso::

        :class:`_sql.Insert` - in the SQL Expression API documentation

