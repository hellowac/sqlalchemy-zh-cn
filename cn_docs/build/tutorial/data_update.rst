.. highlight:: pycon+sql

.. |prev| replace:: :doc:`data_select`
.. |next| replace:: :doc:`orm_data_manipulation`

.. include:: tutorial_nav_include.rst


.. rst-class:: core-header, orm-addin

.. _tutorial_core_update_delete:

使用 UPDATE 和 DELETE 语句
-------------------------------------

Using UPDATE and DELETE Statements

.. tab:: 中文

    到目前为止，我们已经介绍了 :class:`_sql.Insert`，以便我们可以将一些数据插入数据库，然后花了很多时间在 :class:`_sql.Select` 上，该类处理从数据库检索数据的广泛使用模式。在本节中，我们将介绍 :class:`_sql.Update` 和 :class:`_sql.Delete` 构造，这些构造用于修改现有行以及删除现有行。本节将从核心视角介绍这些构造。

    .. container:: orm-header

        **ORM 读者** - 正如在 :ref:`tutorial_core_insert` 中提到的情况一样，当与 ORM 一起使用时，:class:`_sql.Update` 和 :class:`_sql.Delete` 操作通常在 :class:`_orm.Session` 对象内部作为 :term:`unit of work` 过程的一部分调用。

        然而，与 :class:`_sql.Insert` 不同，:class:`_sql.Update` 和 :class:`_sql.Delete` 构造也可以直接与 ORM 一起使用，使用一种称为“ORM 启用的更新和删除”的模式；因此，熟悉这些构造对 ORM 的使用是有用的。这两种使用风格在 :ref:`tutorial_orm_updating` 和 :ref:`tutorial_orm_deleting` 部分中讨论。

.. tab:: 英文

    So far we've covered :class:`_sql.Insert`, so that we can get some data into
    our database, and then spent a lot of time on :class:`_sql.Select` which
    handles the broad range of usage patterns used for retrieving data from the
    database.   In this section we will cover the :class:`_sql.Update` and
    :class:`_sql.Delete` constructs, which are used to modify existing rows
    as well as delete existing rows.    This section will cover these constructs
    from a Core-centric perspective.


    .. container:: orm-header

        **ORM Readers** - As was the case mentioned at :ref:`tutorial_core_insert`,
        the :class:`_sql.Update` and :class:`_sql.Delete` operations when used with
        the ORM are usually invoked internally from the :class:`_orm.Session`
        object as part of the :term:`unit of work` process.

        However, unlike :class:`_sql.Insert`, the :class:`_sql.Update` and
        :class:`_sql.Delete` constructs can also be used directly with the ORM,
        using a pattern known as "ORM-enabled update and delete"; for this reason,
        familiarity with these constructs is useful for ORM use.  Both styles of
        use are discussed in the sections :ref:`tutorial_orm_updating` and
        :ref:`tutorial_orm_deleting`.

.. _tutorial_core_update:

update() SQL 表达式构造
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The update() SQL Expression Construct

.. tab:: 中文

    :func:`_sql.update` 函数生成一个新的 :class:`_sql.Update` 实例，表示 SQL 中的 UPDATE 语句，它将更新表中的现有数据。

    与 :func:`_sql.insert` 构造类似，:func:`_sql.update` 也有一种“传统”形式，它一次对单个表发出 UPDATE 并且不返回任何行。然而，一些后端支持一个 UPDATE 语句可以一次修改多个表，并且 UPDATE 语句还支持 RETURNING，这样包含在匹配行中的列可以在结果集中返回。

    一个基本的 UPDATE 看起来像这样::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .values(fullname="Patrick the Star")
        ... )
        >>> print(stmt)
        {printsql}UPDATE user_account SET fullname=:fullname WHERE user_account.name = :name_1

    :meth:`_sql.Update.values` 方法控制 UPDATE 语句的 SET 元素的内容。这是 :class:`_sql.Insert` 构造共享的方法。参数通常可以使用列名作为关键字参数传递。

    UPDATE 支持所有主要的 SQL 形式的 UPDATE，包括针对表达式的更新，我们可以使用 :class:`_schema.Column` 表达式::

        >>> stmt = update(user_table).values(fullname="Username: " + user_table.c.name)
        >>> print(stmt)
        {printsql}UPDATE user_account SET fullname=(:name_1 || user_account.name)

    为了支持在“executemany”上下文中进行 UPDATE，其中许多参数集将针对同一语句调用，可以使用 :func:`_sql.bindparam` 构造来设置绑定参数；这些参数将替换通常放置文字值的位置：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import bindparam
        >>> stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == bindparam("oldname"))
        ...     .values(name=bindparam("newname"))
        ... )
        >>> with engine.begin() as conn:
        ...     conn.execute(
        ...         stmt,
        ...         [
        ...             {"oldname": "jack", "newname": "ed"},
        ...             {"oldname": "wendy", "newname": "mary"},
        ...             {"oldname": "jim", "newname": "jake"},
        ...         ],
        ...     )
        {execsql}BEGIN (implicit)
        UPDATE user_account SET name=? WHERE user_account.name = ?
        [...] [('ed', 'jack'), ('mary', 'wendy'), ('jake', 'jim')]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT{stop}

    其他可以应用于 UPDATE 的技术包括：

.. tab:: 英文

    The :func:`_sql.update` function generates a new instance of
    :class:`_sql.Update` which represents an UPDATE statement in SQL, that will
    update existing data in a table.

    Like the :func:`_sql.insert` construct, there is a "traditional" form of
    :func:`_sql.update`, which emits UPDATE against a single table at a time and
    does not return any rows.   However some backends support an UPDATE statement
    that may modify multiple tables at once, and the UPDATE statement also
    supports RETURNING such that columns contained in matched rows may be returned
    in the result set.

    A basic UPDATE looks like::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .values(fullname="Patrick the Star")
        ... )
        >>> print(stmt)
        {printsql}UPDATE user_account SET fullname=:fullname WHERE user_account.name = :name_1

    The :meth:`_sql.Update.values` method controls the contents of the SET elements
    of the UPDATE statement.  This is the same method shared by the :class:`_sql.Insert`
    construct.   Parameters can normally be passed using the column names as
    keyword arguments.

    UPDATE supports all the major SQL forms of UPDATE, including updates against expressions,
    where we can make use of :class:`_schema.Column` expressions::

        >>> stmt = update(user_table).values(fullname="Username: " + user_table.c.name)
        >>> print(stmt)
        {printsql}UPDATE user_account SET fullname=(:name_1 || user_account.name)

    To support UPDATE in an "executemany" context, where many parameter sets will
    be invoked against the same statement, the :func:`_sql.bindparam`
    construct may be used to set up bound parameters; these replace the places
    that literal values would normally go:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import bindparam
        >>> stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == bindparam("oldname"))
        ...     .values(name=bindparam("newname"))
        ... )
        >>> with engine.begin() as conn:
        ...     conn.execute(
        ...         stmt,
        ...         [
        ...             {"oldname": "jack", "newname": "ed"},
        ...             {"oldname": "wendy", "newname": "mary"},
        ...             {"oldname": "jim", "newname": "jake"},
        ...         ],
        ...     )
        {execsql}BEGIN (implicit)
        UPDATE user_account SET name=? WHERE user_account.name = ?
        [...] [('ed', 'jack'), ('mary', 'wendy'), ('jake', 'jim')]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT{stop}


    Other techniques which may be applied to UPDATE include:

.. _tutorial_correlated_updates:

相关更新
~~~~~~~~~~~~~~~~~~

Correlated Updates

.. tab:: 中文

    UPDATE 语句可以通过使用 :ref:`相关子查询 <tutorial_scalar_subquery>` 来利用其他表中的行。子查询可以在任何可以放置列表达式的地方使用::

      >>> scalar_subq = (
      ...     select(address_table.c.email_address)
      ...     .where(address_table.c.user_id == user_table.c.id)
      ...     .order_by(address_table.c.id)
      ...     .limit(1)
      ...     .scalar_subquery()
      ... )
      >>> update_stmt = update(user_table).values(fullname=scalar_subq)
      >>> print(update_stmt)
      {printsql}UPDATE user_account SET fullname=(SELECT address.email_address
      FROM address
      WHERE address.user_id = user_account.id ORDER BY address.id
      LIMIT :param_1)

.. tab:: 英文

    An UPDATE statement can make use of rows in other tables by using a
    :ref:`correlated subquery <tutorial_scalar_subquery>`.  A subquery may be used
    anywhere a column expression might be placed::

      >>> scalar_subq = (
      ...     select(address_table.c.email_address)
      ...     .where(address_table.c.user_id == user_table.c.id)
      ...     .order_by(address_table.c.id)
      ...     .limit(1)
      ...     .scalar_subquery()
      ... )
      >>> update_stmt = update(user_table).values(fullname=scalar_subq)
      >>> print(update_stmt)
      {printsql}UPDATE user_account SET fullname=(SELECT address.email_address
      FROM address
      WHERE address.user_id = user_account.id ORDER BY address.id
      LIMIT :param_1)

.. _tutorial_update_from:

UPDATE..FROM
~~~~~~~~~~~~~

UPDATE..FROM

.. tab:: 中文

    某些数据库（如 PostgreSQL 和 MySQL）支持 “UPDATE FROM” 语法，其中可以在一个特殊的 FROM 子句中直接声明其他表。当在语句的 WHERE 子句中找到其他表时，将隐式生成此语法::

    >>> update_stmt = (
    ...     update(user_table)
    ...     .where(user_table.c.id == address_table.c.user_id)
    ...     .where(address_table.c.email_address == "patrick@aol.com")
    ...     .values(fullname="Pat")
    ... )
    >>> print(update_stmt)
    {printsql}UPDATE user_account SET fullname=:fullname FROM address
    WHERE user_account.id = address.user_id AND address.email_address = :email_address_1


    MySQL 还有一种特定语法，可以更新多个表。这要求我们在 VALUES 子句中引用 :class:`_schema.Table` 对象，以便引用其他表::

    >>> update_stmt = (
    ...     update(user_table)
    ...     .where(user_table.c.id == address_table.c.user_id)
    ...     .where(address_table.c.email_address == "patrick@aol.com")
    ...     .values(
    ...         {
    ...             user_table.c.fullname: "Pat",
    ...             address_table.c.email_address: "pat@aol.com",
    ...         }
    ...     )
    ... )
    >>> from sqlalchemy.dialects import mysql
    >>> print(update_stmt.compile(dialect=mysql.dialect()))
    {printsql}UPDATE user_account, address
    SET address.email_address=%s, user_account.fullname=%s
    WHERE user_account.id = address.user_id AND address.email_address = %s

.. tab:: 英文

    Some databases such as PostgreSQL and MySQL support a syntax "UPDATE FROM"
    where additional tables may be stated directly in a special FROM clause. This
    syntax will be generated implicitly when additional tables are located in the
    WHERE clause of the statement::

      >>> update_stmt = (
      ...     update(user_table)
      ...     .where(user_table.c.id == address_table.c.user_id)
      ...     .where(address_table.c.email_address == "patrick@aol.com")
      ...     .values(fullname="Pat")
      ... )
      >>> print(update_stmt)
      {printsql}UPDATE user_account SET fullname=:fullname FROM address
      WHERE user_account.id = address.user_id AND address.email_address = :email_address_1


    There is also a MySQL specific syntax that can UPDATE multiple tables. This
    requires we refer to :class:`_schema.Table` objects in the VALUES clause in
    order to refer to additional tables::

      >>> update_stmt = (
      ...     update(user_table)
      ...     .where(user_table.c.id == address_table.c.user_id)
      ...     .where(address_table.c.email_address == "patrick@aol.com")
      ...     .values(
      ...         {
      ...             user_table.c.fullname: "Pat",
      ...             address_table.c.email_address: "pat@aol.com",
      ...         }
      ...     )
      ... )
      >>> from sqlalchemy.dialects import mysql
      >>> print(update_stmt.compile(dialect=mysql.dialect()))
      {printsql}UPDATE user_account, address
      SET address.email_address=%s, user_account.fullname=%s
      WHERE user_account.id = address.user_id AND address.email_address = %s

.. _tutorial_parameter_ordered_updates:

参数有序更新
~~~~~~~~~~~~~~~~~~~~~~~~~~

Parameter Ordered Updates

.. tab:: 中文

    另一种 MySQL 特有的行为是，UPDATE 的 SET 子句中参数的顺序实际上会影响每个表达式的评估。对于这种用例，:meth:`_sql.Update.ordered_values` 方法接受一个元组序列，以便可以控制此顺序 [1]_::

      >>> update_stmt = update(some_table).ordered_values(
      ...     (some_table.c.y, 20), (some_table.c.x, some_table.c.y + 10)
      ... )
      >>> print(update_stmt)
      {printsql}UPDATE some_table SET y=:y, x=(some_table.y + :y_1)


    .. [1] 虽然 Python 字典在 Python 3.7 及以后版本中
      `保证按插入顺序排列
      <https://mail.python.org/pipermail/python-dev/2017-December/151283.html>`_，
      但 :meth:`_sql.Update.ordered_values` 方法仍然提供了额外的意图明确性，
      当 MySQL UPDATE 语句的 SET 子句需要按特定方式进行时尤为重要。

.. tab:: 英文

    Another MySQL-only behavior is that the order of parameters in the SET clause
    of an UPDATE actually impacts the evaluation of each expression.   For this use
    case, the :meth:`_sql.Update.ordered_values` method accepts a sequence of
    tuples so that this order may be controlled [2]_::

      >>> update_stmt = update(some_table).ordered_values(
      ...     (some_table.c.y, 20), (some_table.c.x, some_table.c.y + 10)
      ... )
      >>> print(update_stmt)
      {printsql}UPDATE some_table SET y=:y, x=(some_table.y + :y_1)


    .. [2] While Python dictionaries are
      `guaranteed to be insert ordered
      <https://mail.python.org/pipermail/python-dev/2017-December/151283.html>`_
      as of Python 3.7, the
      :meth:`_sql.Update.ordered_values` method still provides an additional
      measure of clarity of intent when it is essential that the SET clause
      of a MySQL UPDATE statement proceed in a specific way.

.. _tutorial_deletes:

delete() SQL 表达式构造
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The delete() SQL Expression Construct

.. tab:: 中文

    :func:`_sql.delete` 函数生成一个新的 :class:`_sql.Delete` 实例，表示 SQL 中的 DELETE 语句，它将从表中删除行。

    从 API 角度来看，:func:`_sql.delete` 语句与 :func:`_sql.update` 构造非常相似，传统上不返回任何行，但允许在某些数据库后端上使用 RETURNING 变体。

    ::

        >>> from sqlalchemy import delete
        >>> stmt = delete(user_table).where(user_table.c.name == "patrick")
        >>> print(stmt)
        {printsql}DELETE FROM user_account WHERE user_account.name = :name_1

.. tab:: 英文

    The :func:`_sql.delete` function generates a new instance of
    :class:`_sql.Delete` which represents a DELETE statement in SQL, that will
    delete rows from a table.

    The :func:`_sql.delete` statement from an API perspective is very similar to
    that of the :func:`_sql.update` construct, traditionally returning no rows but
    allowing for a RETURNING variant on some database backends.

    ::

        >>> from sqlalchemy import delete
        >>> stmt = delete(user_table).where(user_table.c.name == "patrick")
        >>> print(stmt)
        {printsql}DELETE FROM user_account WHERE user_account.name = :name_1


.. _tutorial_multi_table_deletes:

多表删除
~~~~~~~~~~~~~~~~~~~~~~

Multiple Table Deletes

.. tab:: 中文

    与 :class:`_sql.Update` 类似，:class:`_sql.Delete` 支持在 WHERE 子句中使用相关子查询以及特定于后端的多表语法，例如 MySQL 上的 ``DELETE FROM..USING``::

      >>> delete_stmt = (
      ...     delete(user_table)
      ...     .where(user_table.c.id == address_table.c.user_id)
      ...     .where(address_table.c.email_address == "patrick@aol.com")
      ... )
      >>> from sqlalchemy.dialects import mysql
      >>> print(delete_stmt.compile(dialect=mysql.dialect()))
      {printsql}DELETE FROM user_account USING user_account, address
      WHERE user_account.id = address.user_id AND address.email_address = %s

.. tab:: 英文

    Like :class:`_sql.Update`, :class:`_sql.Delete` supports the use of correlated
    subqueries in the WHERE clause as well as backend-specific multiple table
    syntaxes, such as ``DELETE FROM..USING`` on MySQL::

      >>> delete_stmt = (
      ...     delete(user_table)
      ...     .where(user_table.c.id == address_table.c.user_id)
      ...     .where(address_table.c.email_address == "patrick@aol.com")
      ... )
      >>> from sqlalchemy.dialects import mysql
      >>> print(delete_stmt.compile(dialect=mysql.dialect()))
      {printsql}DELETE FROM user_account USING user_account, address
      WHERE user_account.id = address.user_id AND address.email_address = %s

.. _tutorial_update_delete_rowcount:

从 UPDATE、DELETE 获取受影响的行数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Getting Affected Row Count from UPDATE, DELETE

.. tab:: 中文

    :class:`_sql.Update` 和 :class:`_sql.Delete` 都支持在语句执行后返回匹配的行数，适用于使用 Core :class:`_engine.Connection` 调用的语句，即 :meth:`_engine.Connection.execute`。根据下面提到的注意事项，该值可以从 :attr:`_engine.CursorResult.rowcount` 属性中获取：

    .. sourcecode:: pycon+sql

        >>> with engine.begin() as conn:
        ...     result = conn.execute(
        ...         update(user_table)
        ...         .values(fullname="Patrick McStar")
        ...         .where(user_table.c.name == "patrick")
        ...     )
        ...     print(result.rowcount)
        {execsql}BEGIN (implicit)
        UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Patrick McStar', 'patrick'){stop}
        1
        {execsql}COMMIT{stop}

    .. tip::

        :class:`_engine.CursorResult` 类是 :class:`_engine.Result` 的子类，包含特定于 DBAPI ``cursor`` 对象的附加属性。当通过 :meth:`_engine.Connection.execute` 方法调用语句时，将返回此子类的实例。当使用 ORM 时，:meth:`_orm.Session.execute` 方法为所有 INSERT、UPDATE 和 DELETE 语句返回此类型的对象。

    关于 :attr:`_engine.CursorResult.rowcount` 的一些事实：

    * 返回的值是语句 WHERE 子句 **匹配(matched)** 的行数。无论行是否实际修改都无关紧要。

    * 对于使用 RETURNING 的 UPDATE 或 DELETE 语句，或使用 :ref:`executemany <tutorial_multiple_parameters>` 执行的语句，:attr:`_engine.CursorResult.rowcount` 不一定可用。这取决于所使用的 DBAPI 模块。

    * 在任何 DBAPI 不确定某种语句的 rowcount 的情况下，返回的值为 ``-1``。

    * SQLAlchemy 在游标关闭之前预先记忆 DBAPIs 的 ``cursor.rowcount`` 值，因为一些 DBAPIs 不支持事后访问此属性。为了对非 UPDATE 或 DELETE 的语句（例如 INSERT 或 SELECT）预先记忆 ``cursor.rowcount``，可以使用 :paramref:`_engine.Connection.execution_options.preserve_rowcount` 执行选项。

    * 某些驱动程序，特别是针对非关系型数据库的第三方方言，可能根本不支持 :attr:`_engine.CursorResult.rowcount`。:attr:`_engine.CursorResult.supports_sane_rowcount` 游标属性将指示这一点。

    * “rowcount” 由 ORM :term:`unit of work` 过程使用，以验证 UPDATE 或 DELETE 语句匹配预期的行数，并且对于文档中 :ref:`mapper_version_counter` 的 ORM 版本控制功能也至关重要。

.. tab:: 英文

    Both :class:`_sql.Update` and :class:`_sql.Delete` support the ability to
    return the number of rows matched after the statement proceeds, for statements
    that are invoked using Core :class:`_engine.Connection`, i.e.
    :meth:`_engine.Connection.execute`. Per the caveats mentioned below, this value
    is available from the :attr:`_engine.CursorResult.rowcount` attribute:

    .. sourcecode:: pycon+sql

        >>> with engine.begin() as conn:
        ...     result = conn.execute(
        ...         update(user_table)
        ...         .values(fullname="Patrick McStar")
        ...         .where(user_table.c.name == "patrick")
        ...     )
        ...     print(result.rowcount)
        {execsql}BEGIN (implicit)
        UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Patrick McStar', 'patrick'){stop}
        1
        {execsql}COMMIT{stop}

    .. tip::

        The :class:`_engine.CursorResult` class is a subclass of
        :class:`_engine.Result` which contains additional attributes that are
        specific to the DBAPI ``cursor`` object.  An instance of this subclass is
        returned when a statement is invoked via the
        :meth:`_engine.Connection.execute` method. When using the ORM, the
        :meth:`_orm.Session.execute` method returns an object of this type for
        all INSERT, UPDATE, and DELETE statements.

    Facts about :attr:`_engine.CursorResult.rowcount`:

    * The value returned is the number of rows **matched** by the WHERE clause of
      the statement.   It does not matter if the row were actually modified or not.

    * :attr:`_engine.CursorResult.rowcount` is not necessarily available for an UPDATE
      or DELETE statement that uses RETURNING, or for one that uses an
      :ref:`executemany <tutorial_multiple_parameters>` execution.   The availability
      depends on the DBAPI module in use.

    * In any case where the DBAPI does not determine the rowcount for some type
      of statement, the returned value will be ``-1``.

    * SQLAlchemy pre-memoizes the DBAPIs ``cursor.rowcount`` value before the cursor
      is closed, as some DBAPIs don't support accessing this attribute after the
      fact.  In order to pre-memoize ``cursor.rowcount`` for a statement that is
      not UPDATE or DELETE, such as INSERT or SELECT, the
      :paramref:`_engine.Connection.execution_options.preserve_rowcount` execution
      option may be used.

    * Some drivers, particularly third party dialects for non-relational databases,
      may not support :attr:`_engine.CursorResult.rowcount` at all.   The
      :attr:`_engine.CursorResult.supports_sane_rowcount` cursor attribute will
      indicate this.

    * "rowcount" is used by the ORM :term:`unit of work` process to validate that
      an UPDATE or DELETE statement matched the expected number of rows, and is
      also essential for the ORM versioning feature documented at
      :ref:`mapper_version_counter`.

将 RETURNING 与 UPDATE、DELETE 结合使用
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using RETURNING with UPDATE, DELETE

.. tab:: 中文

    与 :class:`_sql.Insert` 构造类似，:class:`_sql.Update` 和 :class:`_sql.Delete` 也支持 RETURNING 子句，使用 :meth:`_sql.Update.returning` 和 :meth:`_sql.Delete.returning` 方法添加。当这些方法在支持 RETURNING 的后端上使用时，符合语句 WHERE 条件的所有行的选定列将作为行返回到 :class:`_engine.Result` 对象中，可以进行迭代::

        >>> update_stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .values(fullname="Patrick the Star")
        ...     .returning(user_table.c.id, user_table.c.name)
        ... )
        >>> print(update_stmt)
        {printsql}UPDATE user_account SET fullname=:fullname
        WHERE user_account.name = :name_1
        RETURNING user_account.id, user_account.name{stop}

        >>> delete_stmt = (
        ...     delete(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .returning(user_table.c.id, user_table.c.name)
        ... )
        >>> print(delete_stmt)
        {printsql}DELETE FROM user_account
        WHERE user_account.name = :name_1
        RETURNING user_account.id, user_account.name{stop}

.. tab:: 英文

    Like the :class:`_sql.Insert` construct, :class:`_sql.Update` and :class:`_sql.Delete`
    also support the RETURNING clause which is added by using the
    :meth:`_sql.Update.returning` and :meth:`_sql.Delete.returning` methods.
    When these methods are used on a backend that supports RETURNING, selected
    columns from all rows that match the WHERE criteria of the statement
    will be returned in the :class:`_engine.Result` object as rows that can
    be iterated::


        >>> update_stmt = (
        ...     update(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .values(fullname="Patrick the Star")
        ...     .returning(user_table.c.id, user_table.c.name)
        ... )
        >>> print(update_stmt)
        {printsql}UPDATE user_account SET fullname=:fullname
        WHERE user_account.name = :name_1
        RETURNING user_account.id, user_account.name{stop}

        >>> delete_stmt = (
        ...     delete(user_table)
        ...     .where(user_table.c.name == "patrick")
        ...     .returning(user_table.c.id, user_table.c.name)
        ... )
        >>> print(delete_stmt)
        {printsql}DELETE FROM user_account
        WHERE user_account.name = :name_1
        RETURNING user_account.id, user_account.name{stop}

有关 UPDATE、DELETE 的进一步阅读
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Further Reading for UPDATE, DELETE

.. tab:: 中文

    .. seealso::

        UPDATE / DELETE 的API文档:

        * :class:`_sql.Update`

        * :class:`_sql.Delete`

        基于 ORM 的 UPDATE 和 DELETE:

        :ref:`queryguide_toplevel` 中的 :ref:`orm_expression_update_delete`

.. tab:: 英文

    .. seealso::

        API documentation for UPDATE / DELETE:

        * :class:`_sql.Update`

        * :class:`_sql.Delete`

        ORM-enabled UPDATE and DELETE:

        :ref:`orm_expression_update_delete` - in the :ref:`queryguide_toplevel`


