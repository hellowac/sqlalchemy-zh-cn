.. |prev| replace:: :doc:`index`
.. |next| replace:: :doc:`dbapi_transactions`

.. include:: tutorial_nav_include.rst

.. rst-class:: core-header, orm-addin

.. _tutorial_engine:

建立连接 - Engine
==========================================

Establishing Connectivity - the Engine

.. tab:: 中文

    .. admonition:: **欢迎 ORM 和 Core 读者！**

        每个连接到数据库的 SQLAlchemy 应用程序都需要使用 :class:`_engine.Engine`。这一简短的部分适用于所有人。

    任何 SQLAlchemy 应用程序的开始都是一个名为 :class:`_engine.Engine` 的对象。这个对象充当连接特定数据库的中央来源，既提供工厂功能，又提供一个称为 :ref:`连接池 <pooling_toplevel>` 的存储空间用于这些数据库连接。引擎通常是为特定数据库服务器创建的全局对象，并使用一个 URL 字符串进行配置，该字符串将描述它应如何连接到数据库主机或后端。

    在本教程中，我们将使用仅内存的 SQLite 数据库。这是一种无需设置实际预先存在的数据库即可测试的简单方法。:class:`_engine.Engine` 是通过使用 :func:`_sa.create_engine` 函数创建的：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

    :class:`_sa.create_engine` 的主要参数是一个字符串 URL，上面作为字符串 ``"sqlite+pysqlite:///:memory:"`` 传递。这个字符串向 :class:`_engine.Engine` 指示了三个重要事实：

    1. 我们正在与哪种数据库通信？这是上面的 ``sqlite`` 部分，它将 SQLAlchemy 链接到一个称为 :term:`dialect` 的对象。

    2. 我们使用什么 :term:`DBAPI`？Python :term:`DBAPI` 是 SQLAlchemy 用来与特定数据库交互的第三方驱动程序。在这种情况下，我们使用名称 ``pysqlite``，它在现代 Python 使用中是 `sqlite3 <https://docs.python.org/library/sqlite3.html>`_ 标准库接口。如果省略，SQLAlchemy 将使用为所选数据库设置的默认 :term:`DBAPI`。

    3. 我们如何定位数据库？在这种情况下，我们的 URL 包含短语 ``/:memory:``，这是向 ``sqlite3`` 模块指示我们将使用 **仅内存** 数据库。这种数据库非常适合实验，因为它不需要任何服务器，也不需要创建新文件。

    .. admonition:: Lazy Connecting

        :class:`_engine.Engine` 在第一次由 :func:`_sa.create_engine` 返回时实际上还没有尝试连接到数据库；只有在第一次要求它执行数据库任务时才会发生连接。这是一种称为 :term:`lazy initialization` 的软件设计模式。

    我们还指定了一个参数 :paramref:`_sa.create_engine.echo`，它将指示 :class:`_engine.Engine` 将其发出的所有 SQL 记录到一个将写入标准输出的 Python 记录器中。这个标志是一种更正式设置 :ref:`Python 日志记录 <dbengine_logging>` 的简便方法，并且在脚本中进行实验时非常有用。许多 SQL 示例将包含此 SQL 日志记录输出，在 ``[SQL]`` 链接下，当点击时，将显示完整的 SQL 交互内容。

.. tab:: 英文

    .. admonition:: **Welcome ORM and Core readers alike!**

        Every SQLAlchemy application that connects to a database needs to use
        an :class:`_engine.Engine`.  This short section is for everyone.

    The start of any SQLAlchemy application is an object called the
    :class:`_engine.Engine`.   This object acts as a central source of connections
    to a particular database, providing both a factory as well as a holding
    space called a :ref:`connection pool <pooling_toplevel>` for these database
    connections.   The engine is typically a global object created just
    once for a particular database server, and is configured using a URL string
    which will describe how it should connect to the database host or backend.

    For this tutorial we will use an in-memory-only SQLite database. This is an
    easy way to test things without needing to have an actual pre-existing database
    set up.  The :class:`_engine.Engine` is created by using the
    :func:`_sa.create_engine` function:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite+pysqlite:///:memory:", echo=True)

    The main argument to :class:`_sa.create_engine`
    is a string URL, above passed as the string ``"sqlite+pysqlite:///:memory:"``.
    This string indicates to the :class:`_engine.Engine` three important
    facts:

    1. What kind of database are we communicating with?   This is the ``sqlite``
    portion above, which links in SQLAlchemy to an object known as the
    :term:`dialect`.

    2. What :term:`DBAPI` are we using?  The Python :term:`DBAPI` is a third party
    driver that SQLAlchemy uses to interact with a particular database.  In
    this case, we're using the name ``pysqlite``, which in modern Python
    use is the `sqlite3 <https://docs.python.org/library/sqlite3.html>`_ standard
    library interface for SQLite. If omitted, SQLAlchemy will use a default
    :term:`DBAPI` for the particular database selected.

    3. How do we locate the database?   In this case, our URL includes the phrase
    ``/:memory:``, which is an indicator to the ``sqlite3`` module that we
    will be using an **in-memory-only** database.   This kind of database
    is perfect for experimenting as it does not require any server nor does
    it need to create new files.

    .. admonition:: Lazy Connecting

        The :class:`_engine.Engine`, when first returned by :func:`_sa.create_engine`,
        has not actually tried to connect to the database yet; that happens
        only the first time it is asked to perform a task against the database.
        This is a software design pattern known as :term:`lazy initialization`.

    We have also specified a parameter :paramref:`_sa.create_engine.echo`, which
    will instruct the :class:`_engine.Engine` to log all of the SQL it emits to a
    Python logger that will write to standard out.   This flag is a shorthand way
    of setting up
    :ref:`Python logging more formally <dbengine_logging>` and is useful for
    experimentation in scripts.   Many of the SQL examples will include this
    SQL logging output beneath a ``[SQL]`` link that when clicked, will reveal
    the full SQL interaction.

