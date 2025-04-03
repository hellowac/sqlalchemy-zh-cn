.. |prev| replace:: :doc:`engine`
.. |next| replace:: :doc:`metadata`

.. include:: tutorial_nav_include.rst


.. _tutorial_working_with_transactions:

使用事务和DBAPI
========================================

Working with Transactions and the DBAPI

.. tab:: 中文

    在配置好 :class:`_engine.Engine` 对象后，我们可以深入了解 :class:`_engine.Engine` 及其主要端点 :class:`_engine.Connection` 和 :class:`_engine.Result` 的基本操作。我们还将介绍 ORM 的 :term:`facade` 对这些对象的封装，即 :class:`_orm.Session`。

    .. admonition:: **给 ORM 读者的注意事项**

        在使用 ORM 时，:class:`_engine.Engine` 由 :class:`_orm.Session` 管理。现代 SQLAlchemy 中的 :class:`_orm.Session` 强调的事务和 SQL 执行模式在很大程度上与下面讨论的 :class:`_engine.Connection` 相同，因此虽然本小节以核心为中心，但这里的所有概念也与 ORM 使用相关，推荐所有 ORM 学习者阅读。在本节的末尾，我们将把 :class:`_engine.Connection` 使用的执行模式与 :class:`_orm.Session` 进行比较。

    由于我们还没有介绍 SQLAlchemy 表达式语言，这是 SQLAlchemy 的主要特性，因此我们将使用此包中的一个简单构造 :func:`_sql.text` 来编写 SQL 语句作为**文本 SQL**。请放心，文本 SQL 在日常 SQLAlchemy 使用中是例外而非规则，但它始终可用。

.. tab:: 英文

    With the :class:`_engine.Engine` object ready to go, we can
    dive into the basic operation of an :class:`_engine.Engine` and
    its primary endpoints, the :class:`_engine.Connection` and
    :class:`_engine.Result`. We'll also introduce the ORM's :term:`facade`
    for these objects, known as the :class:`_orm.Session`.

    .. admonition:: **Note to ORM readers**

        When using the ORM, the :class:`_engine.Engine` is managed by the
        :class:`_orm.Session`.  The :class:`_orm.Session` in modern SQLAlchemy
        emphasizes a transactional and SQL execution pattern that is largely
        identical to that of the :class:`_engine.Connection` discussed below,
        so while this subsection is Core-centric, all of the concepts here
        are relevant to ORM use as well and is recommended for all ORM
        learners.   The execution pattern used by the :class:`_engine.Connection`
        will be compared to the :class:`_orm.Session` at the end
        of this section.

    As we have yet to introduce the SQLAlchemy Expression Language that is the
    primary feature of SQLAlchemy, we'll use a simple construct within
    this package called the :func:`_sql.text` construct, to write
    SQL statements as **textual SQL**.   Rest assured that textual SQL is the 
    exception rather than the rule in day-to-day SQLAlchemy use, but it's
    always available.

.. rst-class:: core-header

.. _tutorial_getting_connection:

获取连接
---------------------

Getting a Connection

.. tab:: 中文

    :class:`_engine.Engine` 的目的是通过提供 :class:`_engine.Connection` 对象来连接数据库。在直接使用 Core 时，所有与数据库的交互都是通过 :class:`_engine.Connection` 对象完成的。由于 :class:`_engine.Connection` 会创建一个针对数据库的开放资源，我们希望将此对象的使用限制在特定上下文中。最好的方法是使用 Python 上下文管理器，也称为 `with 语句 <https://docs.python.org/3/reference/compound_stmts.html#with>`_。下面我们使用一个文本 SQL 语句来显示“Hello World”。文本 SQL 是通过一个称为 :func:`_sql.text` 的构造创建的，稍后我们将详细讨论：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import text

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("select 'hello world'"))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        select 'hello world'
        [...] ()
        {stop}[('hello world',)]
        {execsql}ROLLBACK{stop}

    在上面的示例中，上下文管理器创建了一个数据库连接并在事务中执行了操作。Python DBAPI 的默认行为是始终有一个事务在进行中；当连接被 :term:`released` 时，会发出 ROLLBACK 以结束事务。事务 **不会自动提交** ；如果我们想提交数据，需要调用 :meth:`_engine.Connection.commit`，我们将在下一节中看到。

    .. tip:: 
        
        “自动提交(autocommit)” 模式适用于特殊情况。有关这一点的讨论，请参阅 :ref:`dbapi_autocommit`。

    我们 SELECT 操作的结果返回在一个名为 :class:`_engine.Result` 的对象中，稍后将讨论。目前我们要补充的是，最好在“连接”块内使用此对象，而不要在连接范围之外使用它。

.. tab:: 英文

    The purpose of the :class:`_engine.Engine` is to connect to the database by
    providing a :class:`_engine.Connection` object.   When working with the Core
    directly, the :class:`_engine.Connection` object is how all interaction with the
    database is done.   Because the :class:`_engine.Connection` creates an open
    resource against the database, we want to limit our use of this object to a
    specific context. The best way to do that is with a Python context manager, also
    known as `the with statement <https://docs.python.org/3/reference/compound_stmts.html#with>`_.
    Below we use a textual SQL statement to show "Hello World".  Textual SQL is
    created with a construct called :func:`_sql.text` which we'll discuss
    in more detail later:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import text

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("select 'hello world'"))
        ...     print(result.all())
        {execsql}BEGIN (implicit)
        select 'hello world'
        [...] ()
        {stop}[('hello world',)]
        {execsql}ROLLBACK{stop}

    In the example above, the context manager creates a database connection
    and executes the operation in a transaction. The default behavior of
    the Python DBAPI is that a transaction is always in progress; when the
    connection is :term:`released`, a ROLLBACK is emitted to end the
    transaction.   The transaction is **not committed automatically**; if we want
    to commit data we need to call :meth:`_engine.Connection.commit`
    as we'll see in the next section.

    .. tip::  "autocommit" mode is available for special cases.  The section
    :ref:`dbapi_autocommit` discusses this.

    The result of our SELECT was returned in an object called
    :class:`_engine.Result` that will be discussed later. For the moment
    we'll add that it's best to use this object within the "connect" block,
    and to not use it outside of the scope of our connection.

.. rst-class:: core-header

.. _tutorial_committing_data:

提交更改
------------------

Committing Changes

.. tab:: 中文

    我们刚刚了解到 DBAPI 连接不会自动提交数据。
    如果我们想提交一些数据呢？我们可以修改上面的示例来创建一个表，插入一些数据，然后使用 :meth:`_engine.Connection.commit` 方法提交事务， **在** 我们拥有 :class:`_engine.Connection` 对象的块内：

    .. sourcecode:: pycon+sql

        # "commit as you go"
        >>> with engine.connect() as conn:
        ...     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        CREATE TABLE some_table (x int, y int)
        [...] ()
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(1, 1), (2, 4)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    在上面的示例中，我们执行了两个 SQL 语句，一个是 "CREATE TABLE" 语句 [1]_，另一个是参数化的 "INSERT" 语句（我们稍后在 :ref:`tutorial_multiple_parameters` 中讨论参数化语法）。
    为了提交我们在块中所做的工作，我们调用 :meth:`_engine.Connection.commit` 方法来提交事务。之后，我们可以继续运行更多的 SQL 语句，并为这些语句再次调用 :meth:`_engine.Connection.commit`。SQLAlchemy 将这种风格称为 **commit as you go**。

    还有另一种提交数据的方式。我们可以在前面声明我们的 "connect" 块是一个事务块。为此，我们使用 :meth:`_engine.Engine.begin` 方法来获取连接，而不是 :meth:`_engine.Engine.connect` 方法。此方法将管理 :class:`_engine.Connection` 的范围，并在事务块成功结束时执行 COMMIT，如果引发异常则执行 ROLLBACK。这种风格称为 **begin once**：

    .. sourcecode:: pycon+sql

        # "begin once"
        >>> with engine.begin() as conn:
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
        ...     )
        {execsql}BEGIN (implicit)
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(6, 8), (9, 10)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    您应该主要偏向使用 "begin once" 风格，因为它更短，并且在前面显示了整个块的意图。然而，在本教程中，我们将使用 "commit as you go" 风格，因为它在演示目的上更灵活。

    .. topic::  什么是 "BEGIN (implicit)"?

        您可能已经注意到在事务块开始时有日志行 "BEGIN (implicit)"。这里的 "implicit" 意味着 SQLAlchemy **实际上并没有发送任何命令** 到数据库；它只是将此视为 DBAPI 隐式事务的开始。您可以注册 :ref:`事件钩子 <core_sql_events>` 来拦截此事件，例如。

    .. [1] :term:`DDL` 指的是指示数据库创建、修改或删除模式级构造（如表）的 SQL 子集。DDL（如 "CREATE TABLE"）应位于以 COMMIT 结束的事务块中，因为许多数据库使用事务性 DDL，这样模式更改在提交事务之前不会生效。然而，正如我们稍后将看到的，我们通常让 SQLAlchemy 作为更高级操作的一部分为我们运行 DDL 序列，因此我们通常不需要担心 COMMIT。

.. tab:: 英文

    We just learned that the DBAPI connection doesn't commit automatically.
    What if we want to commit some data?   We can change our example above to create a
    table, insert some data and then commit the transaction using
    the :meth:`_engine.Connection.commit` method, **inside** the block
    where we have the :class:`_engine.Connection` object:

    .. sourcecode:: pycon+sql

        # "commit as you go"
        >>> with engine.connect() as conn:
        ...     conn.execute(text("CREATE TABLE some_table (x int, y int)"))
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        CREATE TABLE some_table (x int, y int)
        [...] ()
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(1, 1), (2, 4)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    Above, we execute two SQL statements, a "CREATE TABLE" statement [2]_
    and an "INSERT" statement that's parameterized (we discuss the parameterization syntax
    later in :ref:`tutorial_multiple_parameters`).
    To commit the work we've done in our block, we call the
    :meth:`_engine.Connection.commit` method which commits the transaction. After
    this, we can continue to run more SQL statements and call :meth:`_engine.Connection.commit`
    again for those statements.  SQLAlchemy refers to this style as **commit as
    you go**.

    There's also another style to commit data. We can declare
    our "connect" block to be a transaction block up front.   To do this, we use the
    :meth:`_engine.Engine.begin` method to get the connection, rather than the
    :meth:`_engine.Engine.connect` method.  This method
    will manage the scope of the :class:`_engine.Connection` and also
    enclose everything inside of a transaction with either a COMMIT at the end 
    if the block was successful, or a ROLLBACK if an exception was raised.  This style
    is known as **begin once**:

    .. sourcecode:: pycon+sql

        # "begin once"
        >>> with engine.begin() as conn:
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 6, "y": 8}, {"x": 9, "y": 10}],
        ...     )
        {execsql}BEGIN (implicit)
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(6, 8), (9, 10)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    You should mostly prefer the "begin once" style because it's shorter and shows the
    intention of the entire block up front.   However, in this tutorial we'll
    use "commit as you go" style as it's more flexible for demonstration
    purposes.

    .. topic::  What's "BEGIN (implicit)"?

        You might have noticed the log line "BEGIN (implicit)" at the start of a
        transaction block.  "implicit" here means that SQLAlchemy **did not
        actually send any command** to the database; it just considers this to be
        the start of the DBAPI's implicit transaction.   You can register
        :ref:`event hooks <core_sql_events>` to intercept this event, for example.


    .. [2] :term:`DDL` refers to the subset of SQL that instructs the database
       to create, modify, or remove schema-level constructs such as tables. DDL
       such as "CREATE TABLE" should be in a transaction block that
       ends with COMMIT, as many databases use transactional DDL such that the
       schema changes don't take place until the transaction is committed. However,
       as we'll see later, we usually let SQLAlchemy run DDL sequences for us as
       part of a higher level operation where we don't generally need to worry
       about the COMMIT.


.. rst-class:: core-header

.. _tutorial_statement_execution:

语句执行基础知识
-----------------------------

Basics of Statement Execution

.. tab:: 中文

    我们已经看到了几个针对数据库运行 SQL 语句的示例，这些示例使用了一个称为 :meth:`_engine.Connection.execute` 的方法，结合一个称为 :func:`_sql.text` 的对象，并返回一个称为 :class:`_engine.Result` 的对象。在本节中，我们将更详细地说明这些组件的机制和交互。

    .. container:: orm-header

    本节中的大多数内容同样适用于现代 ORM 使用中的 :meth:`_orm.Session.execute` 方法，该方法的工作方式与 :meth:`_engine.Connection.execute` 非常相似，包括 ORM 结果行也是使用与 Core 相同的 :class:`_engine.Result` 接口提供的。

.. tab:: 英文

    We have seen a few examples that run SQL statements against a database, making
    use of a method called :meth:`_engine.Connection.execute`, in conjunction with
    an object called :func:`_sql.text`, and returning an object called
    :class:`_engine.Result`.  In this section we'll illustrate more closely the
    mechanics and interactions of these components.

    .. container:: orm-header

    Most of the content in this section applies equally well to modern ORM
    use when using the :meth:`_orm.Session.execute` method, which works
    very similarly to that of :meth:`_engine.Connection.execute`, including that
    ORM result rows are delivered using the same :class:`_engine.Result`
    interface used by Core.

.. rst-class:: orm-addin

.. _tutorial_fetching_rows:

获取行
^^^^^^^^^^^^^

Fetching Rows

.. tab:: 中文

    我们将首先通过使用之前插入的行，在我们创建的表上运行一个文本 SELECT 语句，更详细地说明 :class:`_engine.Result` 对象：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT x, y FROM some_table"))
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table
        [...] ()
        {stop}x: 1  y: 1
        x: 2  y: 4
        x: 6  y: 8
        x: 9  y: 10
        {execsql}ROLLBACK{stop}

    在上面，我们执行的 "SELECT" 语句选择了表中的所有行。
    返回的对象称为 :class:`_engine.Result`，它表示结果行的可迭代对象。

    :class:`_engine.Result` 有许多方法用于获取和转换行，例如前面说明的 :meth:`_engine.Result.all` 方法，它返回所有 :class:`_engine.Row` 对象的列表。它还实现了 Python 的迭代器接口，因此我们可以直接迭代 :class:`_engine.Row` 对象的集合。

    :class:`_engine.Row` 对象本身旨在像 Python 的 `named tuples <https://docs.python.org/3/library/collections.html#collections.namedtuple>`_。下面我们说明了访问行的各种方式。

    * **元组分配** - 这是最符合 Python 习惯的风格，即按位置将变量分配给每一行：

    ::

        result = conn.execute(text("select x, y from some_table"))

        for x, y in result:
            ...

    * **整数索引** - 元组是 Python 序列，因此也可以使用常规整数访问：

    ::

        result = conn.execute(text("select x, y from some_table"))

        for row in result:
            x = row[0]

    * **属性名称** - 由于这些是 Python named tuples，元组具有与每列名称匹配的动态属性名称。这些名称通常是 SQL 语句为每行列指定的名称。虽然它们通常是可以预测的，并且可以通过标签进行控制，但在定义较少的情况下，它们可能会受到特定数据库行为的影响：

    ::
        result = conn.execute(text("select x, y from some_table"))

        for row in result:
            y = row.y

            # 使用 Python f-strings 说明
            print(f"Row: {row.x} {y}")

    ..

    * **映射访问** - 要将行接收为 Python **映射** 对象，这本质上是 Python 的常见 ``dict`` 对象的只读版本，:class:`_engine.Result` 可以通过 :meth:`_engine.Result.mappings` 修饰符 **转换** 为 :class:`_engine.MappingResult` 对象；这是一个结果对象，生成类似字典的 :class:`_engine.RowMapping` 对象，而不是 :class:`_engine.Row` 对象：
    
    ::

        result = conn.execute(text("select x, y from some_table"))

        for dict_row in result.mappings():
            x = dict_row["x"]
            y = dict_row["y"]

.. tab:: 英文

    We'll first illustrate the :class:`_engine.Result` object more closely by
    making use of the rows we've inserted previously, running a textual SELECT
    statement on the table we've created:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT x, y FROM some_table"))
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table
        [...] ()
        {stop}x: 1  y: 1
        x: 2  y: 4
        x: 6  y: 8
        x: 9  y: 10
        {execsql}ROLLBACK{stop}

    Above, the "SELECT" string we executed selected all rows from our table.
    The object returned is called :class:`_engine.Result` and represents an
    iterable object of result rows.

    :class:`_engine.Result` has lots of methods for
    fetching and transforming rows, such as the :meth:`_engine.Result.all`
    method illustrated previously, which returns a list of all :class:`_engine.Row`
    objects.   It also implements the Python iterator interface so that we can
    iterate over the collection of :class:`_engine.Row` objects directly.

    The :class:`_engine.Row` objects themselves are intended to act like Python
    `named tuples
    <https://docs.python.org/3/library/collections.html#collections.namedtuple>`_.
    Below we illustrate a variety of ways to access rows.

    * **Tuple Assignment** - This is the most Python-idiomatic style, which is to assign variables
    to each row positionally as they are received:

    ::

        result = conn.execute(text("select x, y from some_table"))

        for x, y in result:
            ...

    * **Integer Index** - Tuples are Python sequences, so regular integer access is available too:

    ::

        result = conn.execute(text("select x, y from some_table"))

        for row in result:
            x = row[0]

    * **Attribute Name** - As these are Python named tuples, the tuples have dynamic attribute names
    matching the names of each column.  These names are normally the names that the
    SQL statement assigns to the columns in each row.  While they are usually
    fairly predictable and can also be controlled by labels, in less defined cases
    they may be subject to database-specific behaviors::

        result = conn.execute(text("select x, y from some_table"))

        for row in result:
            y = row.y

            # illustrate use with Python f-strings
            print(f"Row: {row.x} {y}")

    ..

    * **Mapping Access** - To receive rows as Python **mapping** objects, which is
    essentially a read-only version of Python's interface to the common ``dict``
    object, the :class:`_engine.Result` may be **transformed** into a
    :class:`_engine.MappingResult` object using the
    :meth:`_engine.Result.mappings` modifier; this is a result object that yields
    dictionary-like :class:`_engine.RowMapping` objects rather than
    :class:`_engine.Row` objects::

        result = conn.execute(text("select x, y from some_table"))

        for dict_row in result.mappings():
            x = dict_row["x"]
            y = dict_row["y"]

  ..

.. rst-class:: orm-addin

.. _tutorial_sending_parameters:

发送参数
^^^^^^^^^^^^^^^^^^

Sending Parameters

.. tab:: 中文

    SQL 语句通常会附带要与语句本身一起传递的数据，正如我们在之前的 INSERT 示例中看到的那样。因此，:meth:`_engine.Connection.execute` 方法也接受参数，这些参数被称为 :term:`bound parameters`。一个基本示例可能是，如果我们只想将 SELECT 语句限制为满足某个条件的行，例如 "y" 值大于传递给函数的某个值的行。

    为了实现这一点，使 SQL 语句保持固定并且驱动程序可以正确地清理该值，我们在语句中添加一个 WHERE 条件，该条件命名了一个名为 "y" 的新参数；:func:`_sql.text` 构造接受这些参数，使用冒号格式“ ``:y`` ”。实际的“ ``:y`` ”值作为字典的形式传递给 :meth:`_engine.Connection.execute` 的第二个参数：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {"y": 2})
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table WHERE y > ?
        [...] (2,)
        {stop}x: 2  y: 4
        x: 6  y: 8
        x: 9  y: 10
        {execsql}ROLLBACK{stop}

    在记录的 SQL 输出中，我们可以看到绑定参数 ``:y`` 在发送到 SQLite 数据库时被转换为问号。这是因为 SQLite 数据库驱动程序使用一种称为“qmark 参数样式”的格式，这是 DBAPI 规范允许的六种不同格式之一。SQLAlchemy 将这些格式抽象为只有一种，即使用冒号的“named”格式。

    .. topic:: 始终使用绑定参数

        正如本节开头提到的，文本 SQL 不是我们使用 SQLAlchemy 的通常方式。然而，在使用文本 SQL 时，Python 字面值，即使是非字符串的整数或日期，也 **不应直接字符串化为 SQL 字符串** ；应 **始终** 使用参数。这是众所周知的避免 SQL 注入攻击的方法，当数据不受信任时尤其如此。然而，它还允许 SQLAlchemy 方言和/或 DBAPI 正确处理后端的传入输入。在纯文本 SQL 用例之外，SQLAlchemy 的 Core 表达式 API 还确保在适当的情况下将 Python 字面值作为绑定参数传递。

.. tab:: 英文

    SQL statements are usually accompanied by data that is to be passed with the
    statement itself, as we saw in the INSERT example previously. The
    :meth:`_engine.Connection.execute` method therefore also accepts parameters,
    which are known as :term:`bound parameters`.  A rudimentary example
    might be if we wanted to limit our SELECT statement only to rows that meet a
    certain criteria, such as rows where the "y" value were greater than a certain
    value that is passed in to a function.

    In order to achieve this such that the SQL statement can remain fixed and
    that the driver can properly sanitize the value, we add a WHERE criteria to
    our statement that names a new parameter called "y"; the :func:`_sql.text`
    construct accepts these using a colon format "``:y``".   The actual value for
    "``:y``" is then passed as the second argument to
    :meth:`_engine.Connection.execute` in the form of a dictionary:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     result = conn.execute(text("SELECT x, y FROM some_table WHERE y > :y"), {"y": 2})
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table WHERE y > ?
        [...] (2,)
        {stop}x: 2  y: 4
        x: 6  y: 8
        x: 9  y: 10
        {execsql}ROLLBACK{stop}


    In the logged SQL output, we can see that the bound parameter ``:y`` was
    converted into a question mark when it was sent to the SQLite database.
    This is because the SQLite database driver uses a format called "qmark parameter style",
    which is one of six different formats allowed by the DBAPI specification.
    SQLAlchemy abstracts these formats into just one, which is the "named" format
    using a colon.

    .. topic:: Always use bound parameters

        As mentioned at the beginning of this section, textual SQL is not the usual
        way we work with SQLAlchemy.  However, when using textual SQL, a Python
        literal value, even non-strings like integers or dates, should **never be
        stringified into SQL string directly**; a parameter should **always** be
        used.  This is most famously known as how to avoid SQL injection attacks
        when the data is untrusted.  However it also allows the SQLAlchemy dialects
        and/or DBAPI to correctly handle the incoming input for the backend.
        Outside of plain textual SQL use cases, SQLAlchemy's Core Expression API
        otherwise ensures that Python literal values are passed as bound parameters
        where appropriate.

.. _tutorial_multiple_parameters:

发送多个参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sending Multiple Parameters

.. tab:: 中文

    在 :ref:`tutorial_committing_data` 示例中，我们执行了一个 INSERT 语句，其中我们似乎能够一次向数据库插入多行。对于 "INSERT"、"UPDATE" 和 "DELETE" 等 :term:`DML` 语句，我们可以通过传递字典列表而不是单个字典，将 **多个参数集** 发送到 :meth:`_engine.Connection.execute` 方法，这表示应该对每个参数集多次调用单个 SQL 语句。这种执行风格被称为 :term:`executemany`：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(11, 12), (13, 14)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    上述操作相当于为每个参数集运行一次给定的 INSERT 语句，但该操作将针对许多行进行优化以提高性能。

    "execute" 和 "executemany" 之间的一个关键行为差异是，后者不支持返回结果行，即使语句包含 RETURNING 子句。唯一的例外是使用 Core :func:`_sql.insert` 构造时，本教程稍后在 :ref:`tutorial_core_insert` 中引入，该构造还使用 :meth:`_sql.Insert.returning` 方法指示 RETURNING。在这种情况下，SQLAlchemy 使用特殊逻辑重新组织 INSERT 语句，以便它可以针对许多行调用，同时仍然支持 RETURNING。

    .. seealso::

    :term:`executemany` - 在 :doc:`Glossary </glossary>` 中，描述了用于大多数 "executemany" 执行的 DBAPI 级别 `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_ 方法。

    :ref:`engine_insertmanyvalues` - 在 :ref:`connections_toplevel` 中，描述了 :meth:`_sql.Insert.returning` 使用的专门逻辑，以在 "executemany" 执行中提供结果集。

.. tab:: 英文

    In the example at :ref:`tutorial_committing_data`, we executed an INSERT
    statement where it appeared that we were able to INSERT multiple rows into the
    database at once.  For :term:`DML` statements such as "INSERT",
    "UPDATE" and "DELETE", we can send **multiple parameter sets** to the
    :meth:`_engine.Connection.execute` method by passing a list of dictionaries
    instead of a single dictionary, which indicates that the single SQL statement
    should be invoked multiple times, once for each parameter set.  This style
    of execution is known as :term:`executemany`:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     conn.execute(
        ...         text("INSERT INTO some_table (x, y) VALUES (:x, :y)"),
        ...         [{"x": 11, "y": 12}, {"x": 13, "y": 14}],
        ...     )
        ...     conn.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO some_table (x, y) VALUES (?, ?)
        [...] [(11, 12), (13, 14)]
        <sqlalchemy.engine.cursor.CursorResult object at 0x...>
        COMMIT

    The above operation is equivalent to running the given INSERT statement once
    for each parameter set, except that the operation will be optimized for
    better performance across many rows.

    A key behavioral difference between "execute" and "executemany" is that the
    latter doesn't support returning of result rows, even if the statement includes
    the RETURNING clause. The one exception to this is when using a Core
    :func:`_sql.insert` construct, introduced later in this tutorial at
    :ref:`tutorial_core_insert`, which also indicates RETURNING using the
    :meth:`_sql.Insert.returning` method.  In that case, SQLAlchemy makes use of
    special logic to reorganize the INSERT statement so that it can be invoked
    for many rows while still supporting RETURNING.

    .. seealso::

    :term:`executemany` - in the :doc:`Glossary </glossary>`, describes the
    DBAPI-level
    `cursor.executemany() <https://peps.python.org/pep-0249/#executemany>`_
    method that's used for most "executemany" executions.

    :ref:`engine_insertmanyvalues` - in :ref:`connections_toplevel`, describes
    the specialized logic used by :meth:`_sql.Insert.returning` to deliver
    result sets with "executemany" executions.


.. rst-class:: orm-header

.. _tutorial_executing_orm_session:

使用 ORM 会话执行
-----------------------------

Executing with an ORM Session

.. tab:: 中文

    如前所述，上述的大多数模式和示例也适用于 ORM 的使用，因此在这里我们将介绍这种用法，以便在教程继续进行时，我们能够说明 Core 和 ORM 使用模式的结合。

    使用 ORM 时，基本的事务 / 数据库交互对象称为 :class:`_orm.Session`。在现代 SQLAlchemy 中，该对象的使用方式与 :class:`_engine.Connection` 非常相似，实际上，当使用 :class:`_orm.Session` 时，它会在内部引用一个 :class:`_engine.Connection` 来发出 SQL。

    当 :class:`_orm.Session` 与非 ORM 构造一起使用时，它会传递我们给它的 SQL 语句，并且通常不会与 :class:`_engine.Connection` 直接执行的操作有太大不同，因此我们可以在这里通过我们已经学习的简单文本 SQL 操作来说明它。

    :class:`_orm.Session` 有几种不同的创建模式，但在这里我们将说明最基本的一种模式，该模式与使用 :class:`_engine.Connection` 的方式完全一致，即在上下文管理器中构造它：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import Session

        >>> stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
        >>> with Session(engine) as session:
        ...     result = session.execute(stmt, {"y": 6})
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table WHERE y > ? ORDER BY x, y
        [...] (6,){stop}
        x: 6  y: 8
        x: 9  y: 10
        x: 11  y: 12
        x: 13  y: 14
        {execsql}ROLLBACK{stop}

    上面的示例可以与前一节中的 :ref:`tutorial_sending_parameters` 示例进行比较 - 我们直接将 ``with engine.connect() as conn`` 替换为 ``with Session(engine) as session``，然后像使用 :meth:`_engine.Connection.execute` 方法一样使用 :meth:`_orm.Session.execute` 方法。

    同样地，像 :class:`_engine.Connection` 一样，:class:`_orm.Session` 具有使用 :meth:`_orm.Session.commit` 方法的“随用随 commit”行为，下面通过一个文本 UPDATE 语句来修改我们的一些数据：

    .. sourcecode:: pycon+sql

        >>> with Session(engine) as session:
        ...     result = session.execute(
        ...         text("UPDATE some_table SET y=:y WHERE x=:x"),
        ...         [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
        ...     )
        ...     session.commit()
        {execsql}BEGIN (implicit)
        UPDATE some_table SET y=? WHERE x=?
        [...] [(11, 9), (15, 13)]
        COMMIT{stop}

    上面，我们使用引入于 :ref:`tutorial_multiple_parameters` 的绑定参数 “executemany” 执行风格调用了一个 UPDATE 语句，以“随用随 commit”提交结束块。

    .. tip:: :class:`_orm.Session` 在结束事务后实际上不会保持 :class:`_engine.Connection` 对象。它在下次需要对数据库执行 SQL 时从 :class:`_engine.Engine` 获取一个新的 :class:`_engine.Connection`。

    显然，:class:`_orm.Session` 还有很多其他的技巧，但理解它有一个 :meth:`_orm.Session.execute` 方法，其用法与 :meth:`_engine.Connection.execute` 相同，将帮助我们开始后续的示例。

    .. seealso::

        :ref:`session_basics` - 提供了 :class:`_orm.Session` 对象的基本创建和使用模式。

.. tab:: 英文

    As mentioned previously, most of the patterns and examples above apply to
    use with the ORM as well, so here we will introduce this usage so that
    as the tutorial proceeds, we will be able to illustrate each pattern in
    terms of Core and ORM use together.

    The fundamental transactional / database interactive object when using the
    ORM is called the :class:`_orm.Session`.  In modern SQLAlchemy, this object
    is used in a manner very similar to that of the :class:`_engine.Connection`,
    and in fact as the :class:`_orm.Session` is used, it refers to a
    :class:`_engine.Connection` internally which it uses to emit SQL.

    When the :class:`_orm.Session` is used with non-ORM constructs, it
    passes through the SQL statements we give it and does not generally do things
    much differently from how the :class:`_engine.Connection` does directly, so
    we can illustrate it here in terms of the simple textual SQL
    operations we've already learned.

    The :class:`_orm.Session` has a few different creational patterns, but
    here we will illustrate the most basic one that tracks exactly with how
    the :class:`_engine.Connection` is used which is to construct it within
    a context manager:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import Session

        >>> stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
        >>> with Session(engine) as session:
        ...     result = session.execute(stmt, {"y": 6})
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
        {execsql}BEGIN (implicit)
        SELECT x, y FROM some_table WHERE y > ? ORDER BY x, y
        [...] (6,){stop}
        x: 6  y: 8
        x: 9  y: 10
        x: 11  y: 12
        x: 13  y: 14
        {execsql}ROLLBACK{stop}

    The example above can be compared to the example in the preceding section
    in :ref:`tutorial_sending_parameters` - we directly replace the call to
    ``with engine.connect() as conn`` with ``with Session(engine) as session``,
    and then make use of the :meth:`_orm.Session.execute` method just like we
    do with the :meth:`_engine.Connection.execute` method.

    Also, like the :class:`_engine.Connection`, the :class:`_orm.Session` features
    "commit as you go" behavior using the :meth:`_orm.Session.commit` method,
    illustrated below using a textual UPDATE statement to alter some of
    our data:

    .. sourcecode:: pycon+sql

        >>> with Session(engine) as session:
        ...     result = session.execute(
        ...         text("UPDATE some_table SET y=:y WHERE x=:x"),
        ...         [{"x": 9, "y": 11}, {"x": 13, "y": 15}],
        ...     )
        ...     session.commit()
        {execsql}BEGIN (implicit)
        UPDATE some_table SET y=? WHERE x=?
        [...] [(11, 9), (15, 13)]
        COMMIT{stop}

    Above, we invoked an UPDATE statement using the bound-parameter, "executemany"
    style of execution introduced at :ref:`tutorial_multiple_parameters`, ending
    the block with a "commit as you go" commit.

    .. tip:: The :class:`_orm.Session` doesn't actually hold onto the
    :class:`_engine.Connection` object after it ends the transaction.  It
    gets a new :class:`_engine.Connection` from the :class:`_engine.Engine`
    the next time it needs to execute SQL against the database.

    The :class:`_orm.Session` obviously has a lot more tricks up its sleeve
    than that, however understanding that it has a :meth:`_orm.Session.execute`
    method that's used the same way as :meth:`_engine.Connection.execute` will
    get us started with the examples that follow later.

    .. seealso::

        :ref:`session_basics` - presents basic creational and usage patterns with
        the :class:`_orm.Session` object.





