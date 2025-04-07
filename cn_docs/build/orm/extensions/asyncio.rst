.. _asyncio_toplevel:

异步 I/O (asyncio)
==========================

Asynchronous I/O (asyncio)

.. tab:: 中文

    对 Python asyncio 的支持。支持 Core 和 ORM 使用，使用 asyncio 兼容的方言。

    .. versionadded:: 1.4

    .. warning:: 
        
        请阅读 :ref:`asyncio_install` 以获取有关 **所有** 平台的重要安装说明。

    .. seealso::

        :ref:`change_3414` - 初始功能公告

        :ref:`examples_asyncio` - 示例脚本，展示在 asyncio 扩展中使用 Core 和 ORM 的工作示例。

.. tab:: 英文

    Support for Python asyncio.    Support for Core and ORM usage is
    included, using asyncio-compatible dialects.

    .. versionadded:: 1.4

    .. warning:: 
        
        Please read :ref:`asyncio_install` for important platform installation notes on **all** platforms.

    .. seealso::

        :ref:`change_3414` - initial feature announcement

        :ref:`examples_asyncio` - example scripts illustrating working examples
        of Core and ORM use within the asyncio extension.

.. _asyncio_install:

Asyncio 平台安装说明
-----------------------------------

Asyncio Platform Installation Notes

.. tab:: 中文

    asyncio 扩展依赖于 `greenlet <https://pypi.org/project/greenlet/>`_ 库。这个依赖 **默认未安装**。

    要安装 SQLAlchemy 并确保存在 ``greenlet`` 依赖项，可以安装 ``[asyncio]`` `setuptools extra <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-setuptools-extras>`_，如下所示，这还将包括指示 ``pip`` 安装 ``greenlet``：

    .. sourcecode:: text

        pip install sqlalchemy[asyncio]

    注意，在没有预构建 wheel 文件的平台上安装 ``greenlet`` 意味着 ``greenlet`` 将从源代码构建，这要求 Python 的开发库也必须存在。

    .. versionchanged:: 2.1  
        
        ``greenlet`` 不再默认安装；要使用 asyncio 扩展，必须使用 ``sqlalchemy[asyncio]`` 目标。

.. tab:: 英文

    The asyncio extension depends
    upon the `greenlet <https://pypi.org/project/greenlet/>`_ library. This
    dependency is **not installed by default**.

    To install SQLAlchemy while ensuring the ``greenlet`` dependency is present, the
    ``[asyncio]`` `setuptools extra <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-setuptools-extras>`_
    may be installed
    as follows, which will include also instruct ``pip`` to install ``greenlet``:

    .. sourcecode:: text

        pip install sqlalchemy[asyncio]

    Note that installation of ``greenlet`` on platforms that do not have a pre-built
    wheel file means that ``greenlet`` will be built from source, which requires
    that Python's development libraries also be present.

    .. versionchanged:: 2.1  
        
        ``greenlet`` is no longer installed by default; to use the asyncio extension, the ``sqlalchemy[asyncio]`` target must be used.


概要 - Core
---------------

Synopsis - Core

.. tab:: 中文

    对于 Core 使用，:func:`_asyncio.create_async_engine` 函数会创建一个
    :class:`_asyncio.AsyncEngine` 的实例，它提供了传统 :class:`_engine.Engine` API 的异步版本。
    :class:`_asyncio.AsyncEngine` 通过其 :meth:`_asyncio.AsyncEngine.connect` 和
    :meth:`_asyncio.AsyncEngine.begin` 方法提供 :class:`_asyncio.AsyncConnection`，这两个方法
    都是异步上下文管理器。随后 :class:`_asyncio.AsyncConnection` 可使用
    :meth:`_asyncio.AsyncConnection.execute` 方法来执行语句并返回一个缓冲的
    :class:`_engine.Result`，或使用 :meth:`_asyncio.AsyncConnection.stream` 方法返回一个
    服务器端流式的 :class:`_asyncio.AsyncResult`：

    .. sourcecode:: pycon+sql

        >>> import asyncio

        >>> from sqlalchemy import Column
        >>> from sqlalchemy import MetaData
        >>> from sqlalchemy import select
        >>> from sqlalchemy import String
        >>> from sqlalchemy import Table
        >>> from sqlalchemy.ext.asyncio import create_async_engine

        >>> meta = MetaData()
        >>> t1 = Table("t1", meta, Column("name", String(50), primary_key=True))


        >>> async def async_main() -> None:
        ...     engine = create_async_engine("sqlite+aiosqlite://", echo=True)
        ...
        ...     async with engine.begin() as conn:
        ...         await conn.run_sync(meta.drop_all)
        ...         await conn.run_sync(meta.create_all)
        ...
        ...         await conn.execute(
        ...             t1.insert(), [{"name": "some name 1"}, {"name": "some name 2"}]
        ...         )
        ...
        ...     async with engine.connect() as conn:
        ...         # 执行 select 返回一个 Result，将以缓冲方式返回结果
        ...         result = await conn.execute(select(t1).where(t1.c.name == "some name 1"))
        ...
        ...         print(result.fetchall())
        ...
        ...     # 对于在函数作用域中创建的 AsyncEngine，需显式关闭并清理连接池中的连接
        ...     await engine.dispose()


        >>> asyncio.run(async_main())
        {execsql}BEGIN (implicit)
        ...
        CREATE TABLE t1 (
            name VARCHAR(50) NOT NULL,
            PRIMARY KEY (name)
        )
        ...
        INSERT INTO t1 (name) VALUES (?)
        [...] [('some name 1',), ('some name 2',)]
        COMMIT
        BEGIN (implicit)
        SELECT t1.name
        FROM t1
        WHERE t1.name = ?
        [...] ('some name 1',)
        [('some name 1',)]
        ROLLBACK

    如上所示，可以使用 :meth:`_asyncio.AsyncConnection.run_sync` 方法调用特殊的 DDL 函数，
    如 :meth:`_schema.MetaData.create_all`，这类函数没有可等待（awaitable）钩子。

    .. tip:: 
        
        当在一个即将离开上下文并被垃圾回收的作用域中使用 :class:`_asyncio.AsyncEngine` 对象时， 建议使用 ``await`` 调用 :meth:`_asyncio.AsyncEngine.dispose` 方法，如上述示例中的 ``async_main`` 函数所示。 这样可以确保连接池中所有打开的连接能在可等待上下文中正确关闭。 与阻塞式 IO 不同，SQLAlchemy 无法在诸如 ``__del__`` 或 weakref finalizer 这类方法中正确释放这些连接， 因为这些地方无法使用 ``await``。如果未显式处理引擎的释放，当其超出作用域时，可能会在垃圾回收过程中产生类似 ``RuntimeError: Event loop is closed`` 的警告信息。

    :class:`_asyncio.AsyncConnection` 还通过 :meth:`_asyncio.AsyncConnection.stream` 方法提供了
    "流式" API，返回一个 :class:`_asyncio.AsyncResult` 对象。该结果对象使用服务器端游标，并提供 async/await API，
    例如异步迭代器::

        async with engine.connect() as conn:
            async_result = await conn.stream(select(t1))

            async for row in async_result:
                print("row: %s" % (row,))


.. tab:: 英文

    For Core use, the :func:`_asyncio.create_async_engine` function creates an
    instance of :class:`_asyncio.AsyncEngine` which then offers an async version of
    the traditional :class:`_engine.Engine` API.   The
    :class:`_asyncio.AsyncEngine` delivers an :class:`_asyncio.AsyncConnection` via
    its :meth:`_asyncio.AsyncEngine.connect` and :meth:`_asyncio.AsyncEngine.begin`
    methods which both deliver asynchronous context managers.   The
    :class:`_asyncio.AsyncConnection` can then invoke statements using either the
    :meth:`_asyncio.AsyncConnection.execute` method to deliver a buffered
    :class:`_engine.Result`, or the :meth:`_asyncio.AsyncConnection.stream` method
    to deliver a streaming server-side :class:`_asyncio.AsyncResult`:

    .. sourcecode:: pycon+sql

        >>> import asyncio

        >>> from sqlalchemy import Column
        >>> from sqlalchemy import MetaData
        >>> from sqlalchemy import select
        >>> from sqlalchemy import String
        >>> from sqlalchemy import Table
        >>> from sqlalchemy.ext.asyncio import create_async_engine

        >>> meta = MetaData()
        >>> t1 = Table("t1", meta, Column("name", String(50), primary_key=True))


        >>> async def async_main() -> None:
        ...     engine = create_async_engine("sqlite+aiosqlite://", echo=True)
        ...
        ...     async with engine.begin() as conn:
        ...         await conn.run_sync(meta.drop_all)
        ...         await conn.run_sync(meta.create_all)
        ...
        ...         await conn.execute(
        ...             t1.insert(), [{"name": "some name 1"}, {"name": "some name 2"}]
        ...         )
        ...
        ...     async with engine.connect() as conn:
        ...         # select a Result, which will be delivered with buffered
        ...         # results
        ...         result = await conn.execute(select(t1).where(t1.c.name == "some name 1"))
        ...
        ...         print(result.fetchall())
        ...
        ...     # for AsyncEngine created in function scope, close and
        ...     # clean-up pooled connections
        ...     await engine.dispose()


        >>> asyncio.run(async_main())
        {execsql}BEGIN (implicit)
        ...
        CREATE TABLE t1 (
            name VARCHAR(50) NOT NULL,
            PRIMARY KEY (name)
        )
        ...
        INSERT INTO t1 (name) VALUES (?)
        [...] [('some name 1',), ('some name 2',)]
        COMMIT
        BEGIN (implicit)
        SELECT t1.name
        FROM t1
        WHERE t1.name = ?
        [...] ('some name 1',)
        [('some name 1',)]
        ROLLBACK

    Above, the :meth:`_asyncio.AsyncConnection.run_sync` method may be used to
    invoke special DDL functions such as :meth:`_schema.MetaData.create_all` that
    don't include an awaitable hook.

    .. tip:: It's advisable to invoke the :meth:`_asyncio.AsyncEngine.dispose` method
    using ``await`` when using the :class:`_asyncio.AsyncEngine` object in a
    scope that will go out of context and be garbage collected, as illustrated in the
    ``async_main`` function in the above example.  This ensures that any
    connections held open by the connection pool will be properly disposed
    within an awaitable context.   Unlike when using blocking IO, SQLAlchemy
    cannot properly dispose of these connections within methods like ``__del__``
    or weakref finalizers as there is no opportunity to invoke ``await``.
    Failing to explicitly dispose of the engine when it falls out of scope
    may result in warnings emitted to standard out resembling the form
    ``RuntimeError: Event loop is closed`` within garbage collection.

    The :class:`_asyncio.AsyncConnection` also features a "streaming" API via
    the :meth:`_asyncio.AsyncConnection.stream` method that returns an
    :class:`_asyncio.AsyncResult` object.  This result object uses a server-side
    cursor and provides an async/await API, such as an async iterator::

        async with engine.connect() as conn:
            async_result = await conn.stream(select(t1))

            async for row in async_result:
                print("row: %s" % (row,))

.. _asyncio_orm:


概要 - ORM
---------------

Synopsis - ORM

.. tab:: 中文

    使用 :term:`2.0 style` 查询风格时，:class:`_asyncio.AsyncSession` 类提供完整的 ORM 功能。

    在默认的使用模式下，需特别注意避免 :term:`lazy loading` 或其他涉及 ORM 关系和列属性的
    过期属性访问；下一节 :ref:`asyncio_orm_avoid_lazyloads` 将对此进行详细说明。

    .. warning::

        单个 :class:`_asyncio.AsyncSession` 实例在 **多个并发任务中使用并不安全**。
        详见 :ref:`asyncio_concurrency` 和 :ref:`session_faq_threadsafe` 章节了解背景信息。

    以下示例展示了一个完整的例子，包括映射器和会话的配置：

    .. sourcecode:: pycon+sql

        >>> from __future__ import annotations

        >>> import asyncio
        >>> import datetime
        >>> from typing import List

        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import func
        >>> from sqlalchemy import select
        >>> from sqlalchemy.ext.asyncio import AsyncAttrs
        >>> from sqlalchemy.ext.asyncio import async_sessionmaker
        >>> from sqlalchemy.ext.asyncio import AsyncSession
        >>> from sqlalchemy.ext.asyncio import create_async_engine
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship
        >>> from sqlalchemy.orm import selectinload


        >>> class Base(AsyncAttrs, DeclarativeBase):
        ...     pass

        >>> class B(Base):
        ...     __tablename__ = "b"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
        ...     data: Mapped[str]

        >>> class A(Base):
        ...     __tablename__ = "a"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     data: Mapped[str]
        ...     create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
        ...     bs: Mapped[List[B]] = relationship()

        >>> async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
        ...     async with async_session() as session:
        ...         async with session.begin():
        ...             session.add_all(
        ...                 [
        ...                     A(bs=[B(data="b1"), B(data="b2")], data="a1"),
        ...                     A(bs=[], data="a2"),
        ...                     A(bs=[B(data="b3"), B(data="b4")], data="a3"),
        ...                 ]
        ...             )


        >>> async def select_and_update_objects(
        ...     async_session: async_sessionmaker[AsyncSession],
        ... ) -> None:
        ...     async with async_session() as session:
        ...         stmt = select(A).order_by(A.id).options(selectinload(A.bs))
        ...
        ...         result = await session.execute(stmt)
        ...
        ...         for a in result.scalars():
        ...             print(a, a.data)
        ...             print(f"created at: {a.create_date}")
        ...             for b in a.bs:
        ...                 print(b, b.data)
        ...
        ...         result = await session.execute(select(A).order_by(A.id).limit(1))
        ...
        ...         a1 = result.scalars().one()
        ...
        ...         a1.data = "new data"
        ...
        ...         await session.commit()
        ...
        ...         # 提交后访问属性；这正是 expire_on_commit=False 所允许的
        ...         print(a1.data)
        ...
        ...         # 或者，AsyncAttrs 允许将任何属性作为 awaitable 来访问（2.0.13 中新增）
        ...         for b1 in await a1.awaitable_attrs.bs:
        ...             print(b1, b1.data)


        >>> async def async_main() -> None:
        ...     engine = create_async_engine("sqlite+aiosqlite://", echo=True)
        ...
        ...     # async_sessionmaker：用于创建 AsyncSession 对象的工厂。
        ...     # 设置 expire_on_commit=False，避免事务提交后使对象失效
        ...     async_session = async_sessionmaker(engine, expire_on_commit=False)
        ...
        ...     async with engine.begin() as conn:
        ...         await conn.run_sync(Base.metadata.create_all)
        ...
        ...     await insert_objects(async_session)
        ...     await select_and_update_objects(async_session)
        ...
        ...     # 对于在函数作用域中创建的 AsyncEngine，需显式关闭并清理连接池连接
        ...     await engine.dispose()


        >>> asyncio.run(async_main())
        {execsql}BEGIN (implicit)
        ...
        CREATE TABLE a (
            id INTEGER NOT NULL,
            data VARCHAR NOT NULL,
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE b (
            id INTEGER NOT NULL,
            a_id INTEGER NOT NULL,
            data VARCHAR NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(a_id) REFERENCES a (id)
        )
        ...
        COMMIT
        BEGIN (implicit)
        INSERT INTO a (data) VALUES (?) RETURNING id, create_date
        [...] ('a1',)
        ...
        INSERT INTO b (a_id, data) VALUES (?, ?) RETURNING id
        [...] (1, 'b2')
        ...
        COMMIT
        BEGIN (implicit)
        SELECT a.id, a.data, a.create_date
        FROM a ORDER BY a.id
        [...] ()
        SELECT b.a_id AS b_a_id, b.id AS b_id, b.data AS b_data
        FROM b
        WHERE b.a_id IN (?, ?, ?)
        [...] (1, 2, 3)
        <A object at ...> a1
        created at: ...
        <B object at ...> b1
        <B object at ...> b2
        <A object at ...> a2
        created at: ...
        <A object at ...> a3
        created at: ...
        <B object at ...> b3
        <B object at ...> b4
        SELECT a.id, a.data, a.create_date
        FROM a ORDER BY a.id
        LIMIT ? OFFSET ?
        [...] (1, 0)
        UPDATE a SET data=? WHERE a.id = ?
        [...] ('new data', 1)
        COMMIT
        new data
        <B object at ...> b1
        <B object at ...> b2

    在上述示例中，:class:`_asyncio.AsyncSession` 是通过可选的辅助工具
    :class:`_asyncio.async_sessionmaker` 实例化的，它提供了一个创建新的
    :class:`_asyncio.AsyncSession` 对象的工厂，具备一组固定参数，
    其中包括将其绑定到某个特定数据库 URL 的 :class:`_asyncio.AsyncEngine`。
    之后，它被传递给其他方法，并在 Python 异步上下文管理器（即 ``async with:`` 语句）中使用，
    以便在代码块结束时自动关闭；其行为等同于调用 :meth:`_asyncio.AsyncSession.close` 方法。


.. tab:: 英文

    Using :term:`2.0 style` querying, the :class:`_asyncio.AsyncSession` class
    provides full ORM functionality.

    Within the default mode of use, special care must be taken to avoid :term:`lazy
    loading` or other expired-attribute access involving ORM relationships and
    column attributes; the next section :ref:`asyncio_orm_avoid_lazyloads` details
    this.

    .. warning::

        A single instance of :class:`_asyncio.AsyncSession` is **not safe for
        use in multiple, concurrent tasks**.  See the sections
        :ref:`asyncio_concurrency` and :ref:`session_faq_threadsafe` for background.

    The example below illustrates a complete example including mapper and session
    configuration:

    .. sourcecode:: pycon+sql

        >>> from __future__ import annotations

        >>> import asyncio
        >>> import datetime
        >>> from typing import List

        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import func
        >>> from sqlalchemy import select
        >>> from sqlalchemy.ext.asyncio import AsyncAttrs
        >>> from sqlalchemy.ext.asyncio import async_sessionmaker
        >>> from sqlalchemy.ext.asyncio import AsyncSession
        >>> from sqlalchemy.ext.asyncio import create_async_engine
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship
        >>> from sqlalchemy.orm import selectinload


        >>> class Base(AsyncAttrs, DeclarativeBase):
        ...     pass

        >>> class B(Base):
        ...     __tablename__ = "b"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
        ...     data: Mapped[str]

        >>> class A(Base):
        ...     __tablename__ = "a"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     data: Mapped[str]
        ...     create_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
        ...     bs: Mapped[List[B]] = relationship()

        >>> async def insert_objects(async_session: async_sessionmaker[AsyncSession]) -> None:
        ...     async with async_session() as session:
        ...         async with session.begin():
        ...             session.add_all(
        ...                 [
        ...                     A(bs=[B(data="b1"), B(data="b2")], data="a1"),
        ...                     A(bs=[], data="a2"),
        ...                     A(bs=[B(data="b3"), B(data="b4")], data="a3"),
        ...                 ]
        ...             )


        >>> async def select_and_update_objects(
        ...     async_session: async_sessionmaker[AsyncSession],
        ... ) -> None:
        ...     async with async_session() as session:
        ...         stmt = select(A).order_by(A.id).options(selectinload(A.bs))
        ...
        ...         result = await session.execute(stmt)
        ...
        ...         for a in result.scalars():
        ...             print(a, a.data)
        ...             print(f"created at: {a.create_date}")
        ...             for b in a.bs:
        ...                 print(b, b.data)
        ...
        ...         result = await session.execute(select(A).order_by(A.id).limit(1))
        ...
        ...         a1 = result.scalars().one()
        ...
        ...         a1.data = "new data"
        ...
        ...         await session.commit()
        ...
        ...         # access attribute subsequent to commit; this is what
        ...         # expire_on_commit=False allows
        ...         print(a1.data)
        ...
        ...         # alternatively, AsyncAttrs may be used to access any attribute
        ...         # as an awaitable (new in 2.0.13)
        ...         for b1 in await a1.awaitable_attrs.bs:
        ...             print(b1, b1.data)


        >>> async def async_main() -> None:
        ...     engine = create_async_engine("sqlite+aiosqlite://", echo=True)
        ...
        ...     # async_sessionmaker: a factory for new AsyncSession objects.
        ...     # expire_on_commit - don't expire objects after transaction commit
        ...     async_session = async_sessionmaker(engine, expire_on_commit=False)
        ...
        ...     async with engine.begin() as conn:
        ...         await conn.run_sync(Base.metadata.create_all)
        ...
        ...     await insert_objects(async_session)
        ...     await select_and_update_objects(async_session)
        ...
        ...     # for AsyncEngine created in function scope, close and
        ...     # clean-up pooled connections
        ...     await engine.dispose()


        >>> asyncio.run(async_main())
        {execsql}BEGIN (implicit)
        ...
        CREATE TABLE a (
            id INTEGER NOT NULL,
            data VARCHAR NOT NULL,
            create_date DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE b (
            id INTEGER NOT NULL,
            a_id INTEGER NOT NULL,
            data VARCHAR NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(a_id) REFERENCES a (id)
        )
        ...
        COMMIT
        BEGIN (implicit)
        INSERT INTO a (data) VALUES (?) RETURNING id, create_date
        [...] ('a1',)
        ...
        INSERT INTO b (a_id, data) VALUES (?, ?) RETURNING id
        [...] (1, 'b2')
        ...
        COMMIT
        BEGIN (implicit)
        SELECT a.id, a.data, a.create_date
        FROM a ORDER BY a.id
        [...] ()
        SELECT b.a_id AS b_a_id, b.id AS b_id, b.data AS b_data
        FROM b
        WHERE b.a_id IN (?, ?, ?)
        [...] (1, 2, 3)
        <A object at ...> a1
        created at: ...
        <B object at ...> b1
        <B object at ...> b2
        <A object at ...> a2
        created at: ...
        <A object at ...> a3
        created at: ...
        <B object at ...> b3
        <B object at ...> b4
        SELECT a.id, a.data, a.create_date
        FROM a ORDER BY a.id
        LIMIT ? OFFSET ?
        [...] (1, 0)
        UPDATE a SET data=? WHERE a.id = ?
        [...] ('new data', 1)
        COMMIT
        new data
        <B object at ...> b1
        <B object at ...> b2

    In the example above, the :class:`_asyncio.AsyncSession` is instantiated using
    the optional :class:`_asyncio.async_sessionmaker` helper, which provides
    a factory for new :class:`_asyncio.AsyncSession` objects with a fixed set
    of parameters, which here includes associating it with
    an :class:`_asyncio.AsyncEngine` against particular database URL. It is then
    passed to other methods where it may be used in a Python asynchronous context
    manager (i.e. ``async with:`` statement) so that it is automatically closed at
    the end of the block; this is equivalent to calling the
    :meth:`_asyncio.AsyncSession.close` method.


.. _asyncio_concurrency:

将 AsyncSession 与并发任务结合使用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using AsyncSession with Concurrent Tasks

.. tab:: 中文

    :class:`_asyncio.AsyncSession` 对象是一个 **可变的、有状态的对象** ，表示 **单个有状态的数据库事务正在进行** 。使用 asyncio 的并发任务时，例如使用 ``asyncio.gather()`` 之类的 API，每个单独任务应该使用一个 **单独的**  :class:`_asyncio.AsyncSession`。

    有关 :class:`_orm.Session` 和 :class:`_asyncio.AsyncSession` 在并发工作负载中的使用方式的一般说明，请参阅 :ref:`session_faq_threadsafe` 部分。

.. tab:: 英文

    The :class:`_asyncio.AsyncSession` object is a **mutable, stateful object**
    which represents a **single, stateful database transaction in progress**. Using
    concurrent tasks with asyncio, with APIs such as ``asyncio.gather()`` for
    example, should use a **separate** :class:`_asyncio.AsyncSession` **per individual
    task**.

    See the section :ref:`session_faq_threadsafe` for a general description of
    the :class:`_orm.Session` and :class:`_asyncio.AsyncSession` with regards to
    how they should be used with concurrent workloads.

.. _asyncio_orm_avoid_lazyloads:

使用 AsyncSession 时防止隐式 IO
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Preventing Implicit IO when Using AsyncSession

.. tab:: 中文

以下是上述内容的翻译：

---

    使用传统的 asyncio 时，应用程序需要避免在属性访问时隐式触发 IO 的情况。以下是一些可行的技术手段，许多已在前文示例中展示。

    * 对于延迟加载关系、延迟列或表达式，以及在属性过期的情况下访问属性的场景，可以使用 :class:`_asyncio.AsyncAttrs` 混入类。将此混入类添加到具体类，或更通用地添加到声明式 ``Base`` 超类中，即可通过 :attr:`_asyncio.AsyncAttrs.awaitable_attrs` 访问器将任何属性作为可等待对象访问::

        from __future__ import annotations
        from typing import List
        from sqlalchemy.ext.asyncio import AsyncAttrs
        from sqlalchemy.orm import DeclarativeBase, Mapped, relationship

        class Base(AsyncAttrs, DeclarativeBase):
            pass

        class A(Base):
            __tablename__ = "a"
            bs: Mapped[List[B]] = relationship()

        class B(Base):
            __tablename__ = "b"

    当未使用预加载时，访问新加载实例的 ``A.bs`` 集合通常会触发 :term:`lazy loading`，这通常需要执行数据库 IO。在 asyncio 中不允许隐式 IO，因此可以使用 `awaitable_attrs` 前缀以可等待方式访问该属性::

        a1 = (await session.scalars(select(A))).one()
        for b1 in await a1.awaitable_attrs.bs:
            print(b1)

    :class:`_asyncio.AsyncAttrs` 提供了一个简洁的接口，其底层逻辑也被 :meth:`_asyncio.AsyncSession.run_sync` 方法所使用。

    .. versionadded:: 2.0.13

    * 可以使用 **仅写集合（write only collections）** 替代集合属性，这样将永远不会隐式执行 IO。此功能可参考 SQLAlchemy 2.0 中的 :ref:`write_only_relationship`。使用该功能时，集合不会被读取，只能通过显式 SQL 查询。可参考 :ref:`examples_asyncio` 中的 ``async_orm_writeonly.py`` 示例。

    使用仅写集合时，程序行为简单、可预测。但缺点是无法批量加载集合，必须手动处理。因此以下要点仍涉及常规的懒加载关系的处理技巧。

    * 如果不使用 :class:`_asyncio.AsyncAttrs`，可以将关系声明为 ``lazy="raise"``，避免其尝试执行 SQL。此时应改为使用 :term:`eager loading`。

    * 最实用的预加载策略是 :func:`_orm.selectinload`，如前面的例子所示，用于预加载 ``A.bs`` 集合::

        stmt = select(A).options(selectinload(A.bs))

    * 创建新对象时， **集合应总是赋默认值，例如空列表**::

        A(bs=[], data="a2")

    这使得在对象刷新前 ``.bs`` 属性即可读取。否则在刷新时该集合属性会处于未加载状态，访问时将报错。

    * :class:`_asyncio.AsyncSession` 应设置 :paramref:`_orm.Session.expire_on_commit=False`，以便在调用 :meth:`_asyncio.AsyncSession.commit` 后仍可访问对象属性。例如::

        async_session = async_sessionmaker(engine, expire_on_commit=False)

        async with async_session() as session:
            result = await session.execute(select(A).order_by(A.id))
            a1 = result.scalars().first()
            await session.commit()
            print(a1.data)  # commit 后仍可访问

    其他注意事项包括：

    * 应避免使用 :meth:`_asyncio.AsyncSession.expire`，若确实需要可使用 :meth:`_asyncio.AsyncSession.refresh`。一般不建议使用过期机制，通常应将 ``expire_on_commit`` 设为 ``False``。

    * 在 asyncio 下可以显式加载懒加载关系，方法是将属性名传递给 :meth:`_asyncio.AsyncSession.refresh` 的 ``attribute_names`` 参数::

        a_obj = await async_session.get(A, [1])
        await async_session.refresh(a_obj, ["bs"])
        print(f"bs collection: {a_obj.bs}")

    .. versionadded:: 2.0.4 
        
        支持通过 refresh 的 attribute_names 显式加载关系属性。

    * 避免使用 ``all`` 级联选项（详见 :ref:`unitofwork_cascades`），应明确列出所需的级联功能。 ``all`` 包含 :ref:`cascade_refresh_expire`，它会使 :meth:`.AsyncSession.refresh` 使相关对象属性过期，却不一定重新加载这些对象。

    * 对于 :func:`_orm.deferred` 列，应使用合适的加载选项，方式与 :func:`_orm.relationship` 类似。详见 :ref:`orm_queryguide_column_deferral`。

    .. _dynamic_asyncio:

    * 默认情况下，“动态”关系加载器（详见 :ref:`dynamic_relationship`）不兼容 asyncio。可以通过 :meth:`_asyncio.AsyncSession.run_sync` 使用，或使用其 ``.statement`` 属性构造普通 select 查询::

        user = await session.get(User, 42)
        addresses = (await session.scalars(user.addresses.statement)).all()

        stmt = user.addresses.statement.where(Address.email_address.startswith("patrick"))
        addresses_filter = (await session.scalars(stmt)).all()

    SQLAlchemy 2.0 引入的 :ref:`write_only <write_only_relationship>` 技术完全兼容 asyncio，建议优先使用。

    .. seealso::

        :ref:`migration_20_dynamic_loaders` - 迁移到 2.0 风格的注意事项

    * 如果在 asyncio 中使用的数据库（如 MySQL 8）不支持 RETURNING 子句，那么服务器默认值（如自动生成的时间戳）将无法在对象刷新后获得。除非启用 :paramref:`_orm.Mapper.eager_defaults`。在 SQLAlchemy 2.0 中，对于支持 RETURNING 的数据库（如 PostgreSQL、SQLite 和 MariaDB）会自动启用此行为。

.. tab:: 英文

    Using traditional asyncio, the application needs to avoid any points at which
    IO-on-attribute access may occur.   Techniques that can be used to help
    this are below, many of which are illustrated in the preceding example.
    
    * Attributes that are lazy-loading relationships, deferred columns or
      expressions, or are being accessed in expiration scenarios can take advantage
      of the  :class:`_asyncio.AsyncAttrs` mixin.  This mixin, when added to a
      specific class or more generally to the Declarative ``Base`` superclass,
      provides an accessor :attr:`_asyncio.AsyncAttrs.awaitable_attrs`
      which delivers any attribute as an awaitable::
    
        from __future__ import annotations
    
        from typing import List
    
        from sqlalchemy.ext.asyncio import AsyncAttrs
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import relationship
    
    
        class Base(AsyncAttrs, DeclarativeBase):
            pass
    
    
        class A(Base):
            __tablename__ = "a"
    
            # ... rest of mapping ...
    
            bs: Mapped[List[B]] = relationship()
    
    
        class B(Base):
            __tablename__ = "b"
    
            # ... rest of mapping ...
    
      Accessing the ``A.bs`` collection on newly loaded instances of ``A`` when
      eager loading is not in use will normally use :term:`lazy loading`, which in
      order to succeed will usually emit IO to the database, which will fail under
      asyncio as no implicit IO is allowed. To access this attribute directly under
      asyncio without any prior loading operations, the attribute can be accessed
      as an awaitable by indicating the :attr:`_asyncio.AsyncAttrs.awaitable_attrs`
      prefix::
    
        a1 = (await session.scalars(select(A))).one()
        for b1 in await a1.awaitable_attrs.bs:
            print(b1)
    
      The :class:`_asyncio.AsyncAttrs` mixin provides a succinct facade over the
      internal approach that's also used by the
      :meth:`_asyncio.AsyncSession.run_sync` method.
    
    
      .. versionadded:: 2.0.13
    
      .. seealso::
    
          :class:`_asyncio.AsyncAttrs`
    
    
    * Collections can be replaced with **write only collections** that will never
      emit IO implicitly, by using the :ref:`write_only_relationship` feature in
      SQLAlchemy 2.0. Using this feature, collections are never read from, only
      queried using explicit SQL calls.  See the example
      ``async_orm_writeonly.py`` in the :ref:`examples_asyncio` section for
      an example of write-only collections used with asyncio.
    
      When using write only collections, the program's behavior is simple and easy
      to predict regarding collections. However, the downside is that there is not
      any built-in system for loading many of these collections all at once, which
      instead would need to be performed manually.  Therefore, many of the
      bullets below address specific techniques when using traditional lazy-loaded
      relationships with asyncio, which requires more care.
    
    * If not using :class:`_asyncio.AsyncAttrs`, relationships can be declared
      with ``lazy="raise"`` so that by default they will not attempt to emit SQL.
      In order to load collections, :term:`eager loading` would be used instead.
    
    * The most useful eager loading strategy is the
      :func:`_orm.selectinload` eager loader, which is employed in the previous
      example in order to eagerly
      load the ``A.bs`` collection within the scope of the
      ``await session.execute()`` call::
    
          stmt = select(A).options(selectinload(A.bs))
    
    * When constructing new objects, **collections are always assigned a default,
      empty collection**, such as a list in the above example::
    
          A(bs=[], data="a2")
    
      This allows the ``.bs`` collection on the above ``A`` object to be present and
      readable when the ``A`` object is flushed; otherwise, when the ``A`` is
      flushed, ``.bs`` would be unloaded and would raise an error on access.
    
    * The :class:`_asyncio.AsyncSession` is configured using
      :paramref:`_orm.Session.expire_on_commit` set to False, so that we may access
      attributes on an object subsequent to a call to
      :meth:`_asyncio.AsyncSession.commit`, as in the line at the end where we
      access an attribute::
    
          # create AsyncSession with expire_on_commit=False
          async_session = AsyncSession(engine, expire_on_commit=False)
    
          # sessionmaker version
          async_session = async_sessionmaker(engine, expire_on_commit=False)
    
          async with async_session() as session:
              result = await session.execute(select(A).order_by(A.id))
    
              a1 = result.scalars().first()
    
              # commit would normally expire all attributes
              await session.commit()
    
              # access attribute subsequent to commit; this is what
              # expire_on_commit=False allows
              print(a1.data)
    
    Other guidelines include:
    
    * Methods like :meth:`_asyncio.AsyncSession.expire` should be avoided in favor of
      :meth:`_asyncio.AsyncSession.refresh`; **if** expiration is absolutely needed.
      Expiration should generally **not** be needed as
      :paramref:`_orm.Session.expire_on_commit`
      should normally be set to ``False`` when using asyncio.
    
    * A lazy-loaded relationship **can be loaded explicitly under asyncio** using
      :meth:`_asyncio.AsyncSession.refresh`, **if** the desired attribute name
      is passed explicitly to
      :paramref:`_orm.Session.refresh.attribute_names`, e.g.::
    
        # assume a_obj is an A that has lazy loaded A.bs collection
        a_obj = await async_session.get(A, [1])
    
        # force the collection to load by naming it in attribute_names
        await async_session.refresh(a_obj, ["bs"])
    
        # collection is present
        print(f"bs collection: {a_obj.bs}")
    
      It's of course preferable to use eager loading up front in order to have
      collections already set up without the need to lazy-load.
    
      .. versionadded:: 2.0.4 Added support for
         :meth:`_asyncio.AsyncSession.refresh` and the underlying
         :meth:`_orm.Session.refresh` method to force lazy-loaded relationships
         to load, if they are named explicitly in the
         :paramref:`_orm.Session.refresh.attribute_names` parameter.
         In previous versions, the relationship would be silently skipped even
         if named in the parameter.
    
    * Avoid using the ``all`` cascade option documented at :ref:`unitofwork_cascades`
      in favor of listing out the desired cascade features explicitly.   The
      ``all`` cascade option implies among others the :ref:`cascade_refresh_expire`
      setting, which means that the :meth:`.AsyncSession.refresh` method will
      expire the attributes on related objects, but not necessarily refresh those
      related objects assuming eager loading is not configured within the
      :func:`_orm.relationship`, leaving them in an expired state.
    
    * Appropriate loader options should be employed for :func:`_orm.deferred`
      columns, if used at all, in addition to that of :func:`_orm.relationship`
      constructs as noted above.  See :ref:`orm_queryguide_column_deferral` for
      background on deferred column loading.
    
    * The "dynamic" relationship loader strategy described at
      :ref:`dynamic_relationship` is not compatible by default with the asyncio approach.
      It can be used directly only if invoked within the
      :meth:`_asyncio.AsyncSession.run_sync` method described at
      :ref:`session_run_sync`, or by using its ``.statement`` attribute
      to obtain a normal select::
    
          user = await session.get(User, 42)
          addresses = (await session.scalars(user.addresses.statement)).all()
          stmt = user.addresses.statement.where(Address.email_address.startswith("patrick"))
          addresses_filter = (await session.scalars(stmt)).all()
    
      The :ref:`write only <write_only_relationship>` technique, introduced in
      version 2.0 of SQLAlchemy, is fully compatible with asyncio and should be
      preferred.
    
      .. seealso::
    
        :ref:`migration_20_dynamic_loaders` - notes on migration to 2.0 style
    
    * If using asyncio with a database that does not support RETURNING, such as
      MySQL 8, server default values such as generated timestamps will not be
      available on newly flushed objects unless the
      :paramref:`_orm.Mapper.eager_defaults` option is used. In SQLAlchemy 2.0,
      this behavior is applied automatically to backends like PostgreSQL, SQLite
      and MariaDB which use RETURNING to fetch new values when rows are
      INSERTed.

.. _session_run_sync:

在 asyncio 下运行同步方法和函数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Running Synchronous Methods and Functions under asyncio

.. tab:: 中文

    .. deepalchemy::  
        
        这种方式本质上是公开了 SQLAlchemy 用以提供 asyncio 接口的底层机制。 虽然从技术角度看这样做并没有问题，但总体上可以认为该方式较为“有争议”， 因为它违背了 asyncio 编程模型的一些核心理念。asyncio 的基本理念是： 任何可能触发 IO 的编程语句 **必须** 通过 ``await`` 来显式标识，否则程序就无法明确指出在哪一行可能会发生 IO。 这种方法并未改变该理念的本质，只是允许在函数调用范围内，将一系列同步的 IO 指令打包为一个 awaitable， 从而免除该规则的限制。

    作为将传统 SQLAlchemy “懒加载” 集成到 asyncio 事件循环中的一种 **可选** 方法，
    SQLAlchemy 提供了 :meth:`_asyncio.AsyncSession.run_sync`，它可以在 greenlet 中运行任意 Python 函数，
    并在访问数据库驱动时将传统同步编程逻辑自动转换为 ``await``。一个典型做法是，
    asyncio 风格的应用可以将数据库相关的逻辑封装为函数，并通过 :meth:`_asyncio.AsyncSession.run_sync` 来调用它们。

    改写上面的示例，如果我们没有使用 :func:`_orm.selectinload` 来预加载 ``A.bs`` 集合，
    可以将相关的属性访问操作封装在一个单独函数中执行::

        import asyncio

        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


        def fetch_and_update_objects(session):
            """在一个 awaitable 函数中运行传统同步风格的 ORM 代码。"""

            # 此处的 session 是传统 ORM Session。
            # 所有功能都可用，包括旧版 Query 接口。

            stmt = select(A)

            result = session.execute(stmt)
            for a1 in result.scalars():
                print(a1)

                # 懒加载
                for b1 in a1.bs:
                    print(b1)

            # 使用 legacy Query 接口
            a1 = session.query(A).order_by(A.id).first()

            a1.data = "new data"


        async def async_main():
            engine = create_async_engine(
                "postgresql+asyncpg://scott:tiger@localhost/test",
                echo=True,
            )
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)

            async with AsyncSession(engine) as session:
                async with session.begin():
                    session.add_all(
                        [
                            A(bs=[B(), B()], data="a1"),
                            A(bs=[B()], data="a2"),
                            A(bs=[B(), B()], data="a3"),
                        ]
                    )

                await session.run_sync(fetch_and_update_objects)

                await session.commit()

            # 如果在函数作用域中创建了 AsyncEngine，关闭并清理连接池
            await engine.dispose()


        asyncio.run(async_main())

    以上方式通过在 “同步” 运行器中执行某些函数，在某种程度上类似于在基于事件的编程库（如 ``gevent``）之上运行 SQLAlchemy 应用程序。
    不同之处如下：

    1. 与使用 ``gevent`` 不同，我们可以继续使用标准的 Python asyncio 事件循环或任何自定义事件循环，无需集成到 ``gevent`` 的事件循环中。

    2. 完全不涉及 “monkeypatching”。上述示例使用的是原生 asyncio 驱动，底层 SQLAlchemy 连接池也使用 Python 内置的 ``asyncio.Queue`` 进行连接池管理。

    3. 程序可以在 async/await 异步代码与包含同步代码的函数之间自由切换，几乎不会产生性能开销。 这不依赖于线程执行器（thread executor），也没有额外的等待器或同步机制。

    4. 底层网络驱动程序完全使用 Python 的 asyncio 概念， 不使用任何第三方网络库（如 ``gevent`` 和 ``eventlet`` 所提供的网络功能）。


.. tab:: 英文

    .. deepalchemy::  This approach is essentially exposing publicly the
       mechanism by which SQLAlchemy is able to provide the asyncio interface
       in the first place.   While there is no technical issue with doing so, overall
       the approach can probably be considered "controversial" as it works against
       some of the central philosophies of the asyncio programming model, which
       is essentially that any programming statement that can potentially result
       in IO being invoked **must** have an ``await`` call, lest the program
       does not make it explicitly clear every line at which IO may occur.
       This approach does not change that general idea, except that it allows
       a series of synchronous IO instructions to be exempted from this rule
       within the scope of a function call, essentially bundled up into a single
       awaitable.
    
    As an alternative means of integrating traditional SQLAlchemy "lazy loading"
    within an asyncio event loop, an **optional** method known as
    :meth:`_asyncio.AsyncSession.run_sync` is provided which will run any
    Python function inside of a greenlet, where traditional synchronous
    programming concepts will be translated to use ``await`` when they reach the
    database driver.   A hypothetical approach here is an asyncio-oriented
    application can package up database-related methods into functions that are
    invoked using :meth:`_asyncio.AsyncSession.run_sync`.
    
    Altering the above example, if we didn't use :func:`_orm.selectinload`
    for the ``A.bs`` collection, we could accomplish our treatment of these
    attribute accesses within a separate function::
    
        import asyncio
    
        from sqlalchemy import select
        from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    
    
        def fetch_and_update_objects(session):
            """run traditional sync-style ORM code in a function that will be
            invoked within an awaitable.
    
            """
    
            # the session object here is a traditional ORM Session.
            # all features are available here including legacy Query use.
    
            stmt = select(A)
    
            result = session.execute(stmt)
            for a1 in result.scalars():
                print(a1)
    
                # lazy loads
                for b1 in a1.bs:
                    print(b1)
    
            # legacy Query use
            a1 = session.query(A).order_by(A.id).first()
    
            a1.data = "new data"
    
    
        async def async_main():
            engine = create_async_engine(
                "postgresql+asyncpg://scott:tiger@localhost/test",
                echo=True,
            )
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
    
            async with AsyncSession(engine) as session:
                async with session.begin():
                    session.add_all(
                        [
                            A(bs=[B(), B()], data="a1"),
                            A(bs=[B()], data="a2"),
                            A(bs=[B(), B()], data="a3"),
                        ]
                    )
    
                await session.run_sync(fetch_and_update_objects)
    
                await session.commit()
    
            # for AsyncEngine created in function scope, close and
            # clean-up pooled connections
            await engine.dispose()
    
    
        asyncio.run(async_main())
    
    The above approach of running certain functions within a "sync" runner
    has some parallels to an application that runs a SQLAlchemy application
    on top of an event-based programming library such as ``gevent``.  The
    differences are as follows:
    
    1. unlike when using ``gevent``, we can continue to use the standard Python
       asyncio event loop, or any custom event loop, without the need to integrate
       into the ``gevent`` event loop.
    
    2. There is no "monkeypatching" whatsoever.   The above example makes use of
       a real asyncio driver and the underlying SQLAlchemy connection pool is also
       using the Python built-in ``asyncio.Queue`` for pooling connections.
    
    3. The program can freely switch between async/await code and contained
       functions that use sync code with virtually no performance penalty.  There
       is no "thread executor" or any additional waiters or synchronization in use.
    
    4. The underlying network drivers are also using pure Python asyncio
       concepts, no third party networking libraries as ``gevent`` and ``eventlet``
       provides are in use.

.. _asyncio_events:

使用 asyncio 扩展的事件
---------------------------------------

Using events with the asyncio extension

.. tab:: 中文

    SQLAlchemy 的 :ref:`事件系统 <event_toplevel>` 并未被 asyncio 扩展直接暴露，
    这意味着当前还没有 “async” 版本的 SQLAlchemy 事件处理器。
    
    不过，由于 asyncio 扩展是围绕传统同步 SQLAlchemy API 构建的，
    因此仍然可以自由使用常规的 “同步” 风格事件处理器，就像不使用 asyncio 时一样。
    
    如下面详细说明的，当前有两种策略可以在 asyncio 接口中注册事件：
    
    * 可以在实例级别注册事件（例如，某个特定的 :class:`_asyncio.AsyncEngine` 实例），
      方法是将事件绑定到该实例对应的 ``sync`` 属性上，该属性指向被代理的同步对象。
      例如，若要在某个 :class:`_asyncio.AsyncEngine` 实例上注册
      :meth:`_events.PoolEvents.connect` 事件，应使用其
      :attr:`_asyncio.AsyncEngine.sync_engine` 属性作为目标。可用的目标包括：
    
          :attr:`_asyncio.AsyncEngine.sync_engine`
    
          :attr:`_asyncio.AsyncConnection.sync_connection`
    
          :attr:`_asyncio.AsyncConnection.sync_engine`
    
          :attr:`_asyncio.AsyncSession.sync_session`
    
    * 若要在类级别注册事件（即目标是所有该类型的实例，例如所有
      :class:`_asyncio.AsyncSession` 实例），则应使用对应的同步风格类作为目标。
      例如，若要为 :class:`_asyncio.AsyncSession` 类注册
      :meth:`_ormevents.SessionEvents.before_commit` 事件，应使用 :class:`_orm.Session` 类作为目标。
    
    * 若要在 :class:`_orm.sessionmaker` 层级注册事件，可结合使用显式声明的
      :class:`_orm.sessionmaker` 与 :class:`_asyncio.async_sessionmaker`，
      通过 :paramref:`_asyncio.async_sessionmaker.sync_session_class` 参数进行关联，
      并将事件绑定到 :class:`_orm.sessionmaker` 上。
    
    在 asyncio 上下文中使用事件处理器时，诸如 :class:`_engine.Connection` 之类的对象
    仍然以其传统的 “同步” 方式工作，无需使用 ``await`` 或 ``async``；
    当消息最终传递到 asyncio 数据库适配器时，调用方式将被透明地转换为 asyncio 风格的调用。
    对于接收 DBAPI 层连接对象的事件（如 :meth:`_events.PoolEvents.connect`），
    所传入的对象是符合 :term:`pep-249` 标准的 “connection” 对象，
    它将同步风格的调用适配为 asyncio 驱动调用。

.. tab:: 英文

    The SQLAlchemy :ref:`event system <event_toplevel>` is not directly exposed
    by the asyncio extension, meaning there is not yet an "async" version of a
    SQLAlchemy event handler.
    
    However, as the asyncio extension surrounds the usual synchronous SQLAlchemy
    API, regular "synchronous" style event handlers are freely available as they
    would be if asyncio were not used.
    
    As detailed below, there are two current strategies to register events given
    asyncio-facing APIs:
    
    * Events can be registered at the instance level (e.g. a specific
      :class:`_asyncio.AsyncEngine` instance) by associating the event with the
      ``sync`` attribute that refers to the proxied object. For example to register
      the :meth:`_events.PoolEvents.connect` event against an
      :class:`_asyncio.AsyncEngine` instance, use its
      :attr:`_asyncio.AsyncEngine.sync_engine` attribute as target. Targets
      include:
    
          :attr:`_asyncio.AsyncEngine.sync_engine`
    
          :attr:`_asyncio.AsyncConnection.sync_connection`
    
          :attr:`_asyncio.AsyncConnection.sync_engine`
    
          :attr:`_asyncio.AsyncSession.sync_session`
    
    * To register an event at the class level, targeting all instances of the same type (e.g.
      all :class:`_asyncio.AsyncSession` instances), use the corresponding
      sync-style class. For example to register the
      :meth:`_ormevents.SessionEvents.before_commit` event against the
      :class:`_asyncio.AsyncSession` class, use the :class:`_orm.Session` class as
      the target.
    
    * To register at the :class:`_orm.sessionmaker` level, combine an explicit
      :class:`_orm.sessionmaker` with an :class:`_asyncio.async_sessionmaker`
      using :paramref:`_asyncio.async_sessionmaker.sync_session_class`, and
      associate events with the :class:`_orm.sessionmaker`.
    
    When working within an event handler that is within an asyncio context, objects
    like the :class:`_engine.Connection` continue to work in their usual
    "synchronous" way without requiring ``await`` or ``async`` usage; when messages
    are ultimately received by the asyncio database adapter, the calling style is
    transparently adapted back into the asyncio calling style.  For events that
    are passed a DBAPI level connection, such as :meth:`_events.PoolEvents.connect`,
    the object is a :term:`pep-249` compliant "connection" object which will adapt
    sync-style calls into the asyncio driver.

异步引擎/会话/会话生成器的事件监听器示例
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Examples of Event Listeners with Async Engines / Sessions / Sessionmakers

.. tab:: 中文

    下面是一些将同步风格事件处理器与面向异步的 API 构造关联的示例：
    
    * **AsyncEngine 上的 Core 事件**
    
      在此示例中，我们通过 :class:`_asyncio.AsyncEngine` 的
      :attr:`_asyncio.AsyncEngine.sync_engine` 属性，作为
      :class:`.ConnectionEvents` 和 :class:`.PoolEvents` 的目标来访问同步引擎实例::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy import text
        from sqlalchemy.engine import Engine
        from sqlalchemy.ext.asyncio import create_async_engine
    
        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost:5432/test")
    
    
        # 在 Engine 实例上注册 connect 事件
        @event.listens_for(engine.sync_engine, "connect")
        def my_on_connect(dbapi_con, connection_record):
            print("新建 DBAPI 连接：", dbapi_con)
            cursor = dbapi_con.cursor()
    
            # 对适配后的 DBAPI 连接 / 游标使用同步风格 API
            cursor.execute("select 'execute from event'")
            print(cursor.fetchone()[0])
    
    
        # 在所有 Engine 实例上注册 before_execute 事件
        @event.listens_for(Engine, "before_execute")
        def my_before_execute(
            conn,
            clauseelement,
            multiparams,
            params,
            execution_options,
        ):
            print("before execute!")
    
    
        async def go():
            async with engine.connect() as conn:
                await conn.execute(text("select 1"))
            await engine.dispose()
    
    
        asyncio.run(go())
    
      输出结果：
    
      .. sourcecode:: text
    
        新建 DBAPI 连接： <AdaptedConnection <asyncpg.connection.Connection object at 0x7f33f9b16960>>
        execute from event
        before execute!
    
    
    * **AsyncSession 上的 ORM 事件**
    
      在此示例中，我们通过 :attr:`_asyncio.AsyncSession.sync_session` 属性，作为
      :class:`_orm.SessionEvents` 的目标::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.orm import Session
    
        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost:5432/test")
    
        session = AsyncSession(engine)
    
    
        # 在 Session 实例上注册 before_commit 事件
        @event.listens_for(session.sync_session, "before_commit")
        def my_before_commit(session):
            print("before commit!")
    
            # 在 Session 上使用同步风格 API
            connection = session.connection()
    
            # 在 Connection 上使用同步风格 API
            result = connection.execute(text("select 'execute from event'"))
            print(result.first())
    
    
        # 在所有 Session 实例上注册 after_commit 事件
        @event.listens_for(Session, "after_commit")
        def my_after_commit(session):
            print("after commit!")
    
    
        async def go():
            await session.execute(text("select 1"))
            await session.commit()
    
            await session.close()
            await engine.dispose()
    
    
        asyncio.run(go())
    
      输出结果：
    
      .. sourcecode:: text
    
        before commit!
        execute from event
        after commit!
    
    
    * **在 async_sessionmaker 上的 ORM 事件**
    
      在此用例中，我们以 :class:`_orm.sessionmaker` 作为事件目标，
      然后通过 :paramref:`_asyncio.async_sessionmaker.sync_session_class` 参数，
      将其赋值给 :class:`_asyncio.async_sessionmaker`::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy.ext.asyncio import async_sessionmaker
        from sqlalchemy.orm import sessionmaker
    
        sync_maker = sessionmaker()
        maker = async_sessionmaker(sync_session_class=sync_maker)
    
    
        @event.listens_for(sync_maker, "before_commit")
        def before_commit(session):
            print("before commit")
    
    
        async def main():
            async_session = maker()
    
            await async_session.commit()
    
    
        asyncio.run(main())
    
      输出结果：
    
      .. sourcecode:: text
    
        before commit
    
    
    .. topic:: asyncio 与事件，两种对立的模型
    
        SQLAlchemy 的事件本质上发生在特定 SQLAlchemy 流程的**内部**；
        即事件总是在某个 SQLAlchemy API 被用户代码调用 *之后*，
        并在该 API 的某些其他内部处理发生 *之前* 触发。
    
        与此相对的是 asyncio 扩展的架构，它运行在 SQLAlchemy 通常流程的**外部**，
        即从用户 API 到 DBAPI 函数的路径之外。
    
        消息流动的过程可以用以下方式可视化：
    
        .. sourcecode:: text
    
             SQLAlchemy    SQLAlchemy        SQLAlchemy          SQLAlchemy   plain
              asyncio      asyncio           ORM/Core            asyncio      asyncio
              (public      (internal)                            (internal)
              facing)
            -------------|------------|------------------------|-----------|------------
            asyncio API  |            |                        |           |
            call  ->     |            |                        |           |
                         |  ->  ->    |                        |  ->  ->   |
                         |~~~~~~~~~~~~| sync API call ->       |~~~~~~~~~~~|
                         | asyncio    |  event hooks ->        | sync      |
                         | to         |   invoke action ->     | to        |
                         | sync       |    event hooks ->      | asyncio   |
                         | (greenlet) |     dialect ->         | (leave    |
                         |~~~~~~~~~~~~|      event hooks ->    | greenlet) |
                         |  ->  ->    |       sync adapted     |~~~~~~~~~~~|
                         |            |               DBAPI -> |  ->  ->   | asyncio
                         |            |                        |           | driver -> database
    
        如图所示，API 调用总是始于 asyncio，通过同步 API 流转，最终回到 asyncio，
        然后结果再按相反方向传播。在此过程中，消息首先被转换为同步风格的 API 使用，
        然后再转换回异步风格。
    
        事件钩子本质上出现在 “同步风格 API 使用” 的中间。
        因此，在事件钩子中所呈现的 API，处于 asyncio API 请求被转换为同步过程的内部，
        之后发往数据库 API 的消息将被自动转换为异步调用。


.. tab:: 英文

    Some examples of sync style event handlers associated with async-facing API
    constructs are illustrated below:
    
    * **Core Events on AsyncEngine**
    
      In this example, we access the :attr:`_asyncio.AsyncEngine.sync_engine`
      attribute of :class:`_asyncio.AsyncEngine` as the target for
      :class:`.ConnectionEvents` and :class:`.PoolEvents`::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy import text
        from sqlalchemy.engine import Engine
        from sqlalchemy.ext.asyncio import create_async_engine
    
        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost:5432/test")
    
    
        # connect event on instance of Engine
        @event.listens_for(engine.sync_engine, "connect")
        def my_on_connect(dbapi_con, connection_record):
            print("New DBAPI connection:", dbapi_con)
            cursor = dbapi_con.cursor()
    
            # sync style API use for adapted DBAPI connection / cursor
            cursor.execute("select 'execute from event'")
            print(cursor.fetchone()[0])
    
    
        # before_execute event on all Engine instances
        @event.listens_for(Engine, "before_execute")
        def my_before_execute(
            conn,
            clauseelement,
            multiparams,
            params,
            execution_options,
        ):
            print("before execute!")
    
    
        async def go():
            async with engine.connect() as conn:
                await conn.execute(text("select 1"))
            await engine.dispose()
    
    
        asyncio.run(go())
    
      Output:
    
      .. sourcecode:: text
    
        New DBAPI connection: <AdaptedConnection <asyncpg.connection.Connection object at 0x7f33f9b16960>>
        execute from event
        before execute!
    
    
    * **ORM Events on AsyncSession**
    
      In this example, we access :attr:`_asyncio.AsyncSession.sync_session` as the
      target for :class:`_orm.SessionEvents`::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy import text
        from sqlalchemy.ext.asyncio import AsyncSession
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.orm import Session
    
        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost:5432/test")
    
        session = AsyncSession(engine)
    
    
        # before_commit event on instance of Session
        @event.listens_for(session.sync_session, "before_commit")
        def my_before_commit(session):
            print("before commit!")
    
            # sync style API use on Session
            connection = session.connection()
    
            # sync style API use on Connection
            result = connection.execute(text("select 'execute from event'"))
            print(result.first())
    
    
        # after_commit event on all Session instances
        @event.listens_for(Session, "after_commit")
        def my_after_commit(session):
            print("after commit!")
    
    
        async def go():
            await session.execute(text("select 1"))
            await session.commit()
    
            await session.close()
            await engine.dispose()
    
    
        asyncio.run(go())
    
      Output:
    
      .. sourcecode:: text
    
        before commit!
        execute from event
        after commit!
    
    
    * **ORM Events on async_sessionmaker**
    
      For this use case, we make a :class:`_orm.sessionmaker` as the event target,
      then assign it to the :class:`_asyncio.async_sessionmaker` using
      the :paramref:`_asyncio.async_sessionmaker.sync_session_class` parameter::
    
        import asyncio
    
        from sqlalchemy import event
        from sqlalchemy.ext.asyncio import async_sessionmaker
        from sqlalchemy.orm import sessionmaker
    
        sync_maker = sessionmaker()
        maker = async_sessionmaker(sync_session_class=sync_maker)
    
    
        @event.listens_for(sync_maker, "before_commit")
        def before_commit(session):
            print("before commit")
    
    
        async def main():
            async_session = maker()
    
            await async_session.commit()
    
    
        asyncio.run(main())
    
      Output:
    
      .. sourcecode:: text
    
        before commit
    
    
    .. topic:: asyncio and events, two opposites
    
        SQLAlchemy events by their nature take place within the **interior** of a
        particular SQLAlchemy process; that is, an event always occurs *after* some
        particular SQLAlchemy API has been invoked by end-user code, and *before*
        some other internal aspect of that API occurs.
    
        Contrast this to the architecture of the asyncio extension, which takes
        place on the **exterior** of SQLAlchemy's usual flow from end-user API to
        DBAPI function.
    
        The flow of messaging may be visualized as follows:
    
        .. sourcecode:: text
    
             SQLAlchemy    SQLAlchemy        SQLAlchemy          SQLAlchemy   plain
              asyncio      asyncio           ORM/Core            asyncio      asyncio
              (public      (internal)                            (internal)
              facing)
            -------------|------------|------------------------|-----------|------------
            asyncio API  |            |                        |           |
            call  ->     |            |                        |           |
                         |  ->  ->    |                        |  ->  ->   |
                         |~~~~~~~~~~~~| sync API call ->       |~~~~~~~~~~~|
                         | asyncio    |  event hooks ->        | sync      |
                         | to         |   invoke action ->     | to        |
                         | sync       |    event hooks ->      | asyncio   |
                         | (greenlet) |     dialect ->         | (leave    |
                         |~~~~~~~~~~~~|      event hooks ->    | greenlet) |
                         |  ->  ->    |       sync adapted     |~~~~~~~~~~~|
                         |            |               DBAPI -> |  ->  ->   | asyncio
                         |            |                        |           | driver -> database
    
    
        Where above, an API call always starts as asyncio, flows through the
        synchronous API, and ends as asyncio, before results are propagated through
        this same chain in the opposite direction. In between, the message is
        adapted first into sync-style API use, and then back out to async style.
        Event hooks then by their nature occur in the middle of the "sync-style API
        use".  From this it follows that the API presented within event hooks
        occurs inside the process by which asyncio API requests have been adapted
        to sync, and outgoing messages to the database API will be converted
        to asyncio transparently.
    
.. _asyncio_events_run_async:

在连接池和其他事件中使用仅可等待的驱动程序方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using awaitable-only driver methods in connection pool and other events

.. tab:: 中文

    如上节所述，诸如围绕 :class:`.PoolEvents` 的事件处理器会接收到一个同步风格的 “DBAPI” 连接，
    这是 SQLAlchemy asyncio 方言提供的一个包装对象，用于将底层 asyncio “驱动”连接适配为
    SQLAlchemy 内部可以使用的形式。 当用户自定义的事件处理器实现需要直接使用底层驱动连接、
    并调用其仅支持 `await` 的方法时，就会出现一种特殊用例。一个典型的例子是 asyncpg 驱动所提供的 ``.set_type_codec()`` 方法。
    
    为支持这一用例，SQLAlchemy 的 :class:`.AdaptedConnection` 类提供了一个方法
    :meth:`.AdaptedConnection.run_async`，它允许在事件处理器或其他 SQLAlchemy 内部逻辑的
    “同步”上下文中调用一个可等待（awaitable）的函数。该方法的设计与 :meth:`_asyncio.AsyncConnection.run_sync`
    相对应，后者允许在异步上下文中运行同步方法。
    
    :meth:`.AdaptedConnection.run_async` 应当接收一个函数，该函数接受最底层的 “驱动”连接作为唯一参数，
    并返回一个可等待对象。该函数本身不需要声明为 ``async``；完全可以是一个 Python 的 ``lambda`` 表达式，
    因为返回的 awaitable 会在之后被调用::
    
        from sqlalchemy import event
        from sqlalchemy.ext.asyncio import create_async_engine
    
        engine = create_async_engine(...)
    
    
        @event.listens_for(engine.sync_engine, "connect")
        def register_custom_types(dbapi_connection, *args):
            dbapi_connection.run_async(
                lambda connection: connection.set_type_codec(
                    "MyCustomType",
                    encoder,
                    decoder,  # ...
                )
            )
    
    在上述示例中，传递给 ``register_custom_types`` 事件处理器的对象是一个 :class:`.AdaptedConnection` 实例，
    它为底层仅支持异步的驱动级连接对象提供了类 DBAPI 的接口。
    :meth:`.AdaptedConnection.run_async` 方法则提供了一个 awaitable 环境，可对底层驱动连接进行操作。
    
    .. versionadded:: 1.4.30


.. tab:: 英文

    As discussed in the above section, event handlers such as those oriented
    around the :class:`.PoolEvents` event handlers receive a sync-style "DBAPI" connection,
    which is a wrapper object supplied by SQLAlchemy asyncio dialects to adapt
    the underlying asyncio "driver" connection into one that can be used by
    SQLAlchemy's internals.    A special use case arises when the user-defined
    implementation for such an event handler needs to make use of the
    ultimate "driver" connection directly, using awaitable only methods on that
    driver connection.  One such example is the ``.set_type_codec()`` method
    supplied by the asyncpg driver.
    
    To accommodate this use case, SQLAlchemy's :class:`.AdaptedConnection`
    class provides a method :meth:`.AdaptedConnection.run_async` that allows
    an awaitable function to be invoked within the "synchronous" context of
    an event handler or other SQLAlchemy internal.  This method is directly
    analogous to the :meth:`_asyncio.AsyncConnection.run_sync` method that
    allows a sync-style method to run under async.
    
    :meth:`.AdaptedConnection.run_async` should be passed a function that will
    accept the innermost "driver" connection as a single argument, and return
    an awaitable that will be invoked by the :meth:`.AdaptedConnection.run_async`
    method.  The given function itself does not need to be declared as ``async``;
    it's perfectly fine for it to be a Python ``lambda:``, as the return awaitable
    value will be invoked after being returned::
    
        from sqlalchemy import event
        from sqlalchemy.ext.asyncio import create_async_engine
    
        engine = create_async_engine(...)
    
    
        @event.listens_for(engine.sync_engine, "connect")
        def register_custom_types(dbapi_connection, *args):
            dbapi_connection.run_async(
                lambda connection: connection.set_type_codec(
                    "MyCustomType",
                    encoder,
                    decoder,  # ...
                )
            )
    
    Above, the object passed to the ``register_custom_types`` event handler
    is an instance of :class:`.AdaptedConnection`, which provides a DBAPI-like
    interface to an underlying async-only driver-level connection object.
    The :meth:`.AdaptedConnection.run_async` method then provides access to an
    awaitable environment where the underlying driver level connection may be
    acted upon.
    
    .. versionadded:: 1.4.30


使用多个 asyncio 事件循环
----------------------------------

Using multiple asyncio event loops

.. tab:: 中文

    如果一个应用程序使用了多个事件循环（例如在异步编程中不常见地与多线程结合使用），
    在使用默认连接池实现的情况下，不应在不同事件循环之间共享同一个 :class:`_asyncio.AsyncEngine`。
    
    如果需要将 :class:`_asyncio.AsyncEngine` 从一个事件循环传递到另一个，
    则应在重新使用前调用 :meth:`_asyncio.AsyncEngine.dispose()` 方法。
    若未正确处理，可能会导致 ``RuntimeError`` 异常，
    类似于 ``Task <Task pending ...> got Future attached to a different loop``。
    
    如果必须在不同事件循环之间共享同一个引擎，应通过配置 :class:`~sqlalchemy.pool.NullPool`
    禁用连接池，以避免任何连接被重复使用::
    
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import NullPool
    
        engine = create_async_engine(
            "postgresql+asyncpg://user:pass@host/dbname",
            poolclass=NullPool,
        )

.. tab:: 英文

    An application that makes use of multiple event loops, for example in the
    uncommon case of combining asyncio with multithreading, should not share the
    same :class:`_asyncio.AsyncEngine` with different event loops when using the
    default pool implementation.
    
    If an :class:`_asyncio.AsyncEngine` is be passed from one event loop to another,
    the method :meth:`_asyncio.AsyncEngine.dispose()` should be called before it's
    re-used on a new event loop. Failing to do so may lead to a ``RuntimeError``
    along the lines of
    ``Task <Task pending ...> got Future attached to a different loop``
    
    If the same engine must be shared between different loop, it should be configured
    to disable pooling using :class:`~sqlalchemy.pool.NullPool`, preventing the Engine
    from using any connection more than once::
    
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy.pool import NullPool
    
        engine = create_async_engine(
            "postgresql+asyncpg://user:pass@host/dbname",
            poolclass=NullPool,
        )

.. _asyncio_scoped_session:

使用 asyncio 作用域会话
----------------------------

Using asyncio scoped session

.. tab:: 中文
    
    在线程模式的 SQLAlchemy 中所使用的 “scoped session” 模式（通过 :class:`.scoped_session` 对象实现），
    在 asyncio 中也有适配版本，即 :class:`_asyncio.async_scoped_session`。
    
    .. tip::  SQLAlchemy 通常 **不推荐** 在新开发中使用 “scoped” 模式，因为它依赖于可变的全局状态，
       且在每个线程或任务工作完成后还必须显式清理这些状态。
       特别是在使用 asyncio 时，直接将 :class:`_asyncio.AsyncSession` 作为参数传递给需要它的 awaitable 函数通常是更好的做法。
    
    在使用 :class:`_asyncio.async_scoped_session` 时，由于 asyncio 上下文中没有 “线程本地” 的概念，
    必须为其构造函数提供 “scopefunc” 参数。以下示例演示了使用 ``asyncio.current_task()`` 实现此目的::
    
        from asyncio import current_task
    
        from sqlalchemy.ext.asyncio import (
            async_scoped_session,
            async_sessionmaker,
        )
    
        async_session_factory = async_sessionmaker(
            some_async_engine,
            expire_on_commit=False,
        )
        AsyncScopedSession = async_scoped_session(
            async_session_factory,
            scopefunc=current_task,
        )
        some_async_session = AsyncScopedSession()
    
    .. warning:: :class:`_asyncio.async_scoped_session` 所使用的 "scopefunc"
       会在一个任务中 **被多次调用**，每次访问底层 :class:`_asyncio.AsyncSession` 时都会执行一次。
       因此，该函数应具有 **幂等性** 且尽可能轻量，不应尝试创建或修改任何状态（例如建立回调等）。
    
    .. warning:: 使用 ``current_task()`` 作为作用域键时，必须在最外层 awaitable 作用域内调用
       :meth:`_asyncio.async_scoped_session.remove` 方法，以确保任务完成时将作用域键从注册表中移除，
       否则任务句柄和 :class:`_asyncio.AsyncSession` 实例会保留在内存中，导致内存泄漏。
       下面的示例展示了正确使用 :meth:`_asyncio.async_scoped_session.remove` 的方式。
    
    :class:`_asyncio.async_scoped_session` 实现了与 :class:`.scoped_session` 类似的 **代理行为**，
    因此它可以直接被当作 :class:`_asyncio.AsyncSession` 使用，只需注意在调用时添加 ``await``，
    包括调用 :meth:`_asyncio.async_scoped_session.remove` 方法::
    
        async def some_function(some_async_session, some_object):
            # 直接使用 AsyncSession
            some_async_session.add(some_object)
    
            # 通过上下文代理使用 AsyncSession
            await AsyncScopedSession.commit()
    
            # 移除当前上下文代理的 AsyncSession
            await AsyncScopedSession.remove()
    
    .. versionadded:: 1.4.19
    
    .. currentmodule:: sqlalchemy.ext.asyncio

.. tab:: 英文

    The "scoped session" pattern used in threaded SQLAlchemy with the
    :class:`.scoped_session` object is also available in asyncio, using
    an adapted version called :class:`_asyncio.async_scoped_session`.
    
    .. tip::  SQLAlchemy generally does not recommend the "scoped" pattern
       for new development as it relies upon mutable global state that must also be
       explicitly torn down when work within the thread or task is complete.
       Particularly when using asyncio, it's likely a better idea to pass the
       :class:`_asyncio.AsyncSession` directly to the awaitable functions that need
       it.
    
    When using :class:`_asyncio.async_scoped_session`, as there's no "thread-local"
    concept in the asyncio context, the "scopefunc" parameter must be provided to
    the constructor. The example below illustrates using the
    ``asyncio.current_task()`` function for this purpose::
    
        from asyncio import current_task
    
        from sqlalchemy.ext.asyncio import (
            async_scoped_session,
            async_sessionmaker,
        )
    
        async_session_factory = async_sessionmaker(
            some_async_engine,
            expire_on_commit=False,
        )
        AsyncScopedSession = async_scoped_session(
            async_session_factory,
            scopefunc=current_task,
        )
        some_async_session = AsyncScopedSession()
    
    .. warning:: The "scopefunc" used by :class:`_asyncio.async_scoped_session`
       is invoked **an arbitrary number of times** within a task, once for each
       time the underlying :class:`_asyncio.AsyncSession` is accessed. The function
       should therefore be **idempotent** and lightweight, and should not attempt
       to create or mutate any state, such as establishing callbacks, etc.
    
    .. warning:: Using ``current_task()`` for the "key" in the scope requires that
       the :meth:`_asyncio.async_scoped_session.remove` method is called from
       within the outermost awaitable, to ensure the key is removed from the
       registry when the task is complete, otherwise the task handle as well as
       the :class:`_asyncio.AsyncSession` will remain in memory, essentially
       creating a memory leak.  See the following example which illustrates
       the correct use of :meth:`_asyncio.async_scoped_session.remove`.
    
    :class:`_asyncio.async_scoped_session` includes **proxy
    behavior** similar to that of :class:`.scoped_session`, which means it can be
    treated as a :class:`_asyncio.AsyncSession` directly, keeping in mind that
    the usual ``await`` keywords are necessary, including for the
    :meth:`_asyncio.async_scoped_session.remove` method::
    
        async def some_function(some_async_session, some_object):
            # use the AsyncSession directly
            some_async_session.add(some_object)
    
            # use the AsyncSession via the context-local proxy
            await AsyncScopedSession.commit()
    
            # "remove" the current proxied AsyncSession for the local context
            await AsyncScopedSession.remove()
    
    .. versionadded:: 1.4.19
    
    .. currentmodule:: sqlalchemy.ext.asyncio


.. _asyncio_inspector:

使用检查器检查架构对象
---------------------------------------------------

Using the Inspector to inspect schema objects

.. tab:: 中文

    SQLAlchemy 还没有提供 :class:`_reflection.Inspector` （在 :ref:`metadata_reflection_inspector` 中介绍）的 asyncio 版本，
    但是可以通过利用 :class:`_asyncio.AsyncConnection` 的 :meth:`_asyncio.AsyncConnection.run_sync` 方法在 asyncio 上下文中使用现有接口::

        import asyncio

        from sqlalchemy import inspect
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost/test")


        def use_inspector(conn):
            inspector = inspect(conn)
            # use the inspector
            print(inspector.get_view_names())
            # return any value to the caller
            return inspector.get_table_names()


        async def async_main():
            async with engine.connect() as conn:
                tables = await conn.run_sync(use_inspector)


        asyncio.run(async_main())

.. tab:: 英文

    SQLAlchemy does not yet offer an asyncio version of the
    :class:`_reflection.Inspector` (introduced at :ref:`metadata_reflection_inspector`),
    however the existing interface may be used in an asyncio context by
    leveraging the :meth:`_asyncio.AsyncConnection.run_sync` method of
    :class:`_asyncio.AsyncConnection`::

        import asyncio

        from sqlalchemy import inspect
        from sqlalchemy.ext.asyncio import create_async_engine

        engine = create_async_engine("postgresql+asyncpg://scott:tiger@localhost/test")


        def use_inspector(conn):
            inspector = inspect(conn)
            # use the inspector
            print(inspector.get_view_names())
            # return any value to the caller
            return inspector.get_table_names()


        async def async_main():
            async with engine.connect() as conn:
                tables = await conn.run_sync(use_inspector)


        asyncio.run(async_main())

.. seealso::

    :ref:`metadata_reflection`

    :ref:`inspection_toplevel`

引擎 API 文档
-------------------------

Engine API Documentation

.. autofunction:: create_async_engine

.. autofunction:: async_engine_from_config

.. autofunction:: create_async_pool_from_url

.. autoclass:: AsyncEngine
   :members:

.. autoclass:: AsyncConnection
   :members:

.. autoclass:: AsyncTransaction
   :members:

结果集 API 文档
----------------------------------

Result Set API Documentation

.. tab:: 中文

.. tab:: 英文

The :class:`_asyncio.AsyncResult` object is an async-adapted version of the
:class:`_result.Result` object.  It is only returned when using the
:meth:`_asyncio.AsyncConnection.stream` or :meth:`_asyncio.AsyncSession.stream`
methods, which return a result object that is on top of an active database
cursor.

.. autoclass:: AsyncResult
   :members:
   :inherited-members:

.. autoclass:: AsyncScalarResult
   :members:
   :inherited-members:

.. autoclass:: AsyncMappingResult
   :members:
   :inherited-members:

.. autoclass:: AsyncTupleResult

ORM 会话 API 文档
-----------------------------

ORM Session API Documentation

.. autofunction:: async_object_session

.. autofunction:: async_session

.. autofunction:: close_all_sessions

.. autoclass:: async_sessionmaker
   :members:
   :inherited-members:

.. autoclass:: async_scoped_session
   :members:
   :inherited-members:

.. autoclass:: AsyncAttrs
   :members:

.. autoclass:: AsyncSession
   :members:
   :exclude-members: sync_session_class

   .. autoattribute:: sync_session_class

.. autoclass:: AsyncSessionTransaction
   :members:



