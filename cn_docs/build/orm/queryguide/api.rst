.. highlight:: pycon+sql

.. |prev| replace:: :doc:`relationships`
.. |next| replace:: :doc:`query`

.. include:: queryguide_nav_include.rst


=============================
用于查询的 ORM API 功能
=============================

ORM API Features for Querying

ORM 加载器选项
------------------

ORM Loader Options

.. tab:: 中文

    加载器选项是对象，当它们传递给 :meth:`_sql.Select.options` 方法时，作用于 :class:`.Select` 对象或类似 SQL 结构，影响列属性和关系属性的加载。大多数加载器选项都源自 :class:`_orm.Load` 层次结构。有关使用加载器选项的完整概述，请参阅下面的链接部分。

    .. seealso::

        * :ref:`loading_columns` - 详细说明影响列和 SQL 表达式映射属性加载的映射器和加载选项

        * :ref:`loading_toplevel` - 详细说明影响 :func:`_orm.relationship` 映射属性加载的关系和加载选项
    
.. tab:: 英文

    Loader options are objects which, when passed to the :meth:`_sql.Select.options` method of a :class:`.Select` object or similar SQL construct, affect the loading of both column and relationship-oriented attributes. The majority of loader options descend from the :class:`_orm.Load` hierarchy. For a complete overview of using loader options, see the linked sections below.

    .. seealso::

        * :ref:`loading_columns` - details mapper and loading options that affect how column and SQL-expression mapped attributes are loaded

        * :ref:`loading_toplevel` - details relationship and loading options that affect how :func:`_orm.relationship` mapped attributes are loaded

.. _orm_queryguide_execution_options:


ORM 执行选项
---------------------

ORM Execution Options

.. tab:: 中文

    ORM 层级的执行选项是关键字选项，它们可以通过 :paramref:`_orm.Session.execute.execution_options` 参数与语句执行相关联，这是一个字典参数，接受 :class:`_orm.Session` 方法，如 :meth:`_orm.Session.execute` 和 :meth:`_orm.Session.scalars`，或者通过直接与将要调用的语句本身关联，使用 :meth:`_sql.Executable.execution_options` 方法，该方法接受任意关键字参数。

    ORM 层级选项与 Core 层级的执行选项不同，后者在 :meth:`_engine.Connection.execution_options` 中有文档说明。需要注意的是，下文讨论的 ORM 选项与 Core 层级的方法 :meth:`_engine.Connection.execution_options` 或 :meth:`_engine.Engine.execution_options` **不兼容**；即使 :class:`.Engine` 或 :class:`.Connection` 与正在使用的 :class:`_orm.Session` 关联，这些选项也会被忽略。

    在本节中，将使用 ``_sql.Executable.execution_options`` 方法样式进行示例说明。

.. tab:: 英文

    ORM-level execution options are keyword options that may be associated with a statement execution using either the :paramref:`_orm.Session.execute.execution_options` parameter, which is a dictionary argument accepted by :class:`_orm.Session` methods such as :meth:`_orm.Session.execute` and :meth:`_orm.Session.scalars`, or by associating them directly with the statement to be invoked itself using the :meth:`_sql.Executable.execution_options` method, which accepts them as arbitrary keyword arguments.

    ORM-level options are distinct from the Core level execution options documented at :meth:`_engine.Connection.execution_options`. It's important to note that the ORM options discussed below are **not** compatible with Core level methods :meth:`_engine.Connection.execution_options` or :meth:`_engine.Engine.execution_options`; the options are ignored at this level, even if the :class:`.Engine` or :class:`.Connection` is associated with the :class:`_orm.Session` in use.

    Within this section, the :meth:`_sql.Executable.execution_options` method style will be illustrated for examples.

.. _orm_queryguide_populate_existing:

填充现有
^^^^^^^^^^^^^^^^^

Populate Existing

.. tab:: 中文

    ``populate_existing`` 执行选项确保，对于所有加载的行，对应的 :class:`_orm.Session` 中的实例将被完全刷新——擦除对象中现有的任何数据（包括待处理的更改），并用从结果加载的数据替换。

    使用示例如下：

        >>> stmt = select(User).execution_options(populate_existing=True)
        >>> result = session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        ...

    通常，ORM 对象只会加载一次，如果它们与后续结果行的主键匹配，则不会将该行应用于对象。这是为了保留对象上的待处理未刷新的更改，并避免刷新已存在数据的开销和复杂性。 :class:`_orm.Session` 假定使用高度隔离的事务模型，且在事务内期望发生变化的数据（超出本地更改）将通过显式步骤来处理，如此方法所示。

    使用 ``populate_existing``，可以刷新与查询匹配的任何对象集，并且它还允许控制关系加载器选项。例如，要刷新一个实例，同时刷新相关的对象集：

    .. sourcecode:: python

        stmt = (
            select(User)
            .where(User.name.in_(names))
            .execution_options(populate_existing=True)
            .options(selectinload(User.addresses))
        )
        # 将刷新所有匹配的 User 对象以及相关的
        # Address 对象
        users = session.execute(stmt).scalars().all()

    ``populate_existing`` 的另一个使用案例是支持各种属性加载功能，这些功能可以在每个查询基础上更改属性的加载方式。适用的选项包括：

    * :func:`_orm.with_expression` 选项

    * :meth:`_orm.PropComparator.and_` 方法，可修改加载器策略加载的内容

    * :func:`_orm.contains_eager` 选项

    * :func:`_orm.with_loader_criteria` 选项

    * :func:`_orm.load_only` 选项，用于选择要刷新的属性

    ``populate_existing`` 执行选项等同于 :meth:`_orm.Query.populate_existing` 方法，适用于 :term:`1.x style` ORM 查询。

    .. seealso::

        :ref:`faq_session_identity` - 在 :doc:`/faq/index` 中

        :ref:`session_expire` - 在 ORM :class:`_orm.Session` 文档中


.. tab:: 英文^

    The ``populate_existing`` execution option ensures that, for all rows loaded, the corresponding instances in the :class:`_orm.Session` will be fully refreshed – erasing any existing data within the objects (including pending changes) and replacing with the data loaded from the result.

    Example use looks like::

        >>> stmt = select(User).execution_options(populate_existing=True)
        >>> result = session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        ...

    Normally, ORM objects are only loaded once, and if they are matched up to the primary key in a subsequent result row, the row is not applied to the object.  This is both to preserve pending, unflushed changes on the object as well as to avoid the overhead and complexity of refreshing data which is already there.   The :class:`_orm.Session` assumes a default working model of a highly isolated transaction, and to the degree that data is expected to change within the transaction outside of the local changes being made, those use cases would be handled using explicit steps such as this method.

    Using ``populate_existing``, any set of objects that matches a query can be refreshed, and it also allows control over relationship loader options. E.g. to refresh an instance while also refreshing a related set of objects:

    .. sourcecode:: python

        stmt = (
            select(User)
            .where(User.name.in_(names))
            .execution_options(populate_existing=True)
            .options(selectinload(User.addresses))
        )
        # will refresh all matching User objects as well as the related
        # Address objects
        users = session.execute(stmt).scalars().all()

    Another use case for ``populate_existing`` is in support of various attribute loading features that can change how an attribute is loaded on a per-query basis.   Options for which this apply include:

    * The :func:`_orm.with_expression` option

    * The :meth:`_orm.PropComparator.and_` method that can modify what a loader strategy loads

    * The :func:`_orm.contains_eager` option

    * The :func:`_orm.with_loader_criteria` option

    * The :func:`_orm.load_only` option to select what attributes to refresh

    The ``populate_existing`` execution option is equvialent to the :meth:`_orm.Query.populate_existing` method in :term:`1.x style` ORM queries.

    .. seealso::

        :ref:`faq_session_identity` - in :doc:`/faq/index`

        :ref:`session_expire` - in the ORM :class:`_orm.Session` documentation

.. _orm_queryguide_autoflush:

自动刷新
^^^^^^^^^

Autoflush

.. tab:: 中文
    
    此选项在设置为 ``False`` 时，将导致 :class:`_orm.Session` 不调用 "autoflush" 步骤。它相当于使用 :attr:`_orm.Session.no_autoflush` 上下文管理器来禁用 autoflush：

        >>> stmt = select(User).execution_options(autoflush=False)
        >>> session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        ...

    此选项也适用于启用了 ORM 的 :class:`_sql.Update` 和 :class:`_sql.Delete` 查询。

    ``autoflush`` 执行选项相当于 :meth:`_orm.Query.autoflush` 方法，在 :term:`1.x style` ORM 查询中。

    .. seealso::

        :ref:`session_flushing`

.. tab:: 英文

    This option, when passed as ``False``, will cause the :class:`_orm.Session` to not invoke the "autoflush" step.  It is equivalent to using the :attr:`_orm.Session.no_autoflush` context manager to disable autoflush::

        >>> stmt = select(User).execution_options(autoflush=False)
        >>> session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        ...

    This option will also work on ORM-enabled :class:`_sql.Update` and :class:`_sql.Delete` queries.

    The ``autoflush`` execution option is equvialent to the :meth:`_orm.Query.autoflush` method in :term:`1.x style` ORM queries.

    .. seealso::

        :ref:`session_flushing`

.. _orm_queryguide_yield_per:

使用 Yield Per 获取大量结果集
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fetching Large Result Sets with Yield Per

.. tab:: 中文

    ``yield_per`` 执行选项是一个整数值，它将导致 :class:`_engine.Result` 一次只缓冲有限数量的行和/或 ORM 对象，然后再将数据提供给客户端。

    通常，ORM 会立即获取 **所有** 行，为每一行构建 ORM 对象，并将这些对象组装成一个单一的缓冲区，然后将这个缓冲区传递给 :class:`_engine.Result` 对象，作为返回的行的来源。这样做的理由是确保如联合急加载、结果去重和依赖身份映射保持一致状态的结果处理逻辑能够正确工作。

    ``yield_per`` 选项的目的是改变这种行为，使 ORM 结果集优化用于通过非常大的结果集（例如 > 10K 行）进行迭代的场景，在这种情况下，用户已确定上述模式不适用。当使用 ``yield_per`` 时，ORM 会将 ORM 结果批量为子集合，并在迭代 :class:`_engine.Result` 对象时逐个从每个子集合中返回行，以便 Python 解释器无需声明非常大的内存区域，这既耗时又会导致过度的内存使用。该选项会影响数据库游标的使用方式，以及 ORM 构建行和对象并传递给 :class:`_engine.Result` 的方式。

    .. tip::

        从上面可以得出结论， :class:`_engine.Result` 必须以可迭代的方式消费，也就是说，使用迭代方式，例如 ``for row in result`` 或使用部分行方法，如 :meth:`_engine.Result.fetchmany` 或 :meth:`_engine.Result.partitions`。调用 :meth:`_engine.Result.all` 会违背使用 ``yield_per`` 的目的。

    使用 ``yield_per`` 相当于同时使用 :paramref:`_engine.Connection.execution_options.stream_results` 执行选项，这会选择使用服务器端游标（如果数据库支持的话），以及在返回的 :class:`_engine.Result` 对象上使用 :meth:`_engine.Result.yield_per` 方法，后者建立了固定的行大小，并且限制了每次构建的 ORM 对象数量。

    .. tip::

        ``yield_per`` 现在也可以作为 Core 执行选项使用，详细说明请参阅 :ref:`engine_stream_results`。本节详细说明了将 ``yield_per`` 作为执行选项与 ORM :class:`_orm.Session` 配合使用。在这两种上下文中，该选项的行为尽可能相似。

    在与 ORM 一起使用时， ``yield_per`` 必须通过在给定语句上使用 :meth:`.Executable.execution_options` 方法，或通过将其传递给 :paramref:`_orm.Session.execute.execution_options` 参数（例如 :meth:`_orm.Session.execute` 或其他类似的 :class:`_orm.Session` 方法，如 :meth:`_orm.Session.scalars`）。以下是获取 ORM 对象的典型用法示例：

        >>> stmt = select(User).execution_options(yield_per=10)
        >>> for user_obj in session.scalars(stmt):
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... 行继续 ...

    上面的代码等同于以下示例，后者在 Core 层级执行选项中使用了 :paramref:`_engine.Connection.execution_options.stream_results` 和 :paramref:`_engine.Connection.execution_options.max_row_buffer`，并结合了 :meth:`_engine.Result.yield_per` 方法：

        # 等效代码
        >>> stmt = select(User).execution_options(stream_results=True, max_row_buffer=10)
        >>> for user_obj in session.scalars(stmt).yield_per(10):
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... 行继续 ...

    ``yield_per`` 也通常与 :meth:`_engine.Result.partitions` 方法结合使用，该方法将按分组的分区迭代行。每个分区的大小默认为传递给 ``yield_per`` 的整数值，如下所示：

        >>> stmt = select(User).execution_options(yield_per=10)
        >>> for partition in session.scalars(stmt).partitions():
        ...     for user_obj in partition:
        ...         print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... 行继续 ...

    ``yield_per`` 执行选项与使用集合的 :ref:`"subquery" eager loading <subquery_eager_loading>` 或 :ref:`"joined" eager loading <joined_eager_loading>` 加载不兼容。当使用 :ref:`"select in" eager loading <selectin_eager_loading>` 时，如果数据库驱动程序支持多个独立游标，它是可能兼容的。

    此外， ``yield_per`` 执行选项与 :meth:`_engine.Result.unique` 方法不兼容；因为该方法依赖于存储所有行的完整身份集，它会必然违背使用 ``yield_per`` 的目的，后者是为了处理任意大量的行。

    .. versionchanged:: 1.4.6  

        当从使用 :meth:`_engine.Result.unique` 过滤的 :class:`_engine.Result` 对象中获取 ORM 行时，如果同时使用了 ``yield_per`` 执行选项，将会引发异常。

    当使用遗留的 :class:`_orm.Query` 对象并采用 :term:`1.x style` ORM 使用时， :meth:`_orm.Query.yield_per` 方法的结果与 ``yield_per`` 执行选项相同。


.. tab:: 英文^

    The ``yield_per`` execution option is an integer value which will cause the :class:`_engine.Result` to buffer only a limited number of rows and/or ORM objects at a time, before making data available to the client.

    Normally, the ORM will fetch **all** rows immediately, constructing ORM objects for each and assembling those objects into a single buffer, before passing this buffer to the :class:`_engine.Result` object as a source of rows to be returned. The rationale for this behavior is to allow correct behavior for features such as joined eager loading, uniquifying of results, and the general case of result handling logic that relies upon the identity map maintaining a consistent state for every object in a result set as it is fetched.

    The purpose of the ``yield_per`` option is to change this behavior so that the ORM result set is optimized for iteration through very large result sets (e.g. > 10K rows), where the user has determined that the above patterns don't apply. When ``yield_per`` is used, the ORM will instead batch ORM results into sub-collections and yield rows from each sub-collection individually as the :class:`_engine.Result` object is iterated, so that the Python interpreter doesn't need to declare very large areas of memory which is both time consuming and leads to excessive memory use. The option affects both the way the database cursor is used as well as how the ORM constructs rows and objects to be passed to the :class:`_engine.Result`.

    .. tip::

        From the above, it follows that the :class:`_engine.Result` must be consumed in an iterable fashion, that is, using iteration such as ``for row in result`` or using partial row methods such as :meth:`_engine.Result.fetchmany` or :meth:`_engine.Result.partitions`. Calling :meth:`_engine.Result.all` will defeat the purpose of using ``yield_per``.

    Using ``yield_per`` is equivalent to making use of both the :paramref:`_engine.Connection.execution_options.stream_results` execution option, which selects for server side cursors to be used by the backend if supported, and the :meth:`_engine.Result.yield_per` method on the returned :class:`_engine.Result` object, which establishes a fixed size of rows to be fetched as well as a corresponding limit to how many ORM objects will be constructed at once.

    .. tip::

        ``yield_per`` is now available as a Core execution option as well, described in detail at :ref:`engine_stream_results`.  This section details the use of ``yield_per`` as an execution option with an ORM :class:`_orm.Session`.  The option behaves as similarly as possible in both contexts.

    When used with the ORM, ``yield_per`` must be established either via the :meth:`.Executable.execution_options` method on the given statement or by passing it to the :paramref:`_orm.Session.execute.execution_options` parameter of :meth:`_orm.Session.execute` or other similar :class:`_orm.Session` method such as :meth:`_orm.Session.scalars`.  Typical use for fetching ORM objects is illustrated below::

        >>> stmt = select(User).execution_options(yield_per=10)
        >>> for user_obj in session.scalars(stmt):
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... rows continue ...

    The above code is equivalent to the example below, which uses :paramref:`_engine.Connection.execution_options.stream_results` and :paramref:`_engine.Connection.execution_options.max_row_buffer` Core-level execution options in conjunction with the :meth:`_engine.Result.yield_per` method of :class:`_engine.Result`::

        # equivalent code
        >>> stmt = select(User).execution_options(stream_results=True, max_row_buffer=10)
        >>> for user_obj in session.scalars(stmt).yield_per(10):
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... rows continue ...

    ``yield_per`` is also commonly used in combination with the :meth:`_engine.Result.partitions` method, which will iterate rows in grouped partitions. The size of each partition defaults to the integer value passed to ``yield_per``, as in the below example::

        >>> stmt = select(User).execution_options(yield_per=10)
        >>> for partition in session.scalars(stmt).partitions():
        ...     for user_obj in partition:
        ...         print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        ...
        >>> # ... rows continue ...


    The ``yield_per`` execution option **is not compatible** with :ref:`"subquery" eager loading <subquery_eager_loading>` loading or :ref:`"joined" eager loading <joined_eager_loading>` when using collections. It is potentially compatible with :ref:`"select in" eager loading <selectin_eager_loading>` , provided the database driver supports multiple, independent cursors.

    Additionally, the ``yield_per`` execution option is not compatible with the :meth:`_engine.Result.unique` method; as this method relies upon storing a complete set of identities for all rows, it would necessarily defeat the purpose of using ``yield_per`` which is to handle an arbitrarily large number of rows.

    .. versionchanged:: 1.4.6  
        
        An exception is raised when ORM rows are fetched from a :class:`_engine.Result` object that makes use of the :meth:`_engine.Result.unique` filter, at the same time as the ``yield_per`` execution option is used.

    When using the legacy :class:`_orm.Query` object with :term:`1.x style` ORM use, the :meth:`_orm.Query.yield_per` method will have the same result as that of the ``yield_per`` execution option.


.. seealso::

    :ref:`engine_stream_results`

.. _queryguide_identity_token:

身份令牌
^^^^^^^^^^^^^^

Identity Token

.. doctest-disable:

.. tab:: 中文

    .. deepalchemy::

        此选项是一个高级功能，主要用于 :ref:`horizontal_sharding_toplevel` 扩展。在典型场景中，如果需要从不同的“分片”或分区中加载具有相同主键的对象，建议优先为每个分片使用单独的 :class:`_orm.Session` 对象。

    “identity token”（身份标记）是一个可以与新加载对象的 :term:`identity key` 关联的任意值。该元素首先是为了支持进行每行“分片”的扩展而存在，在这些扩展中，对象可能从某一数据库表的多个副本中加载，这些副本之间存在主键重叠的情况。该“identity token”的主要使用者是 :ref:`horizontal_sharding_toplevel` 扩展，它提供了一个通用框架，用于在一个特定数据库表的多个“分片”之间持久化对象。

    ``identity_token`` 执行选项可以在每个查询的基础上使用，从而直接影响此标记。通过直接使用该选项，可以将多个具有相同主键和源表、但“身份”不同的对象实例载入同一个 :class:`_orm.Session` 中。

    一个使用场景是，通过 :ref:`schema_translating` 功能，将来自不同 schema 的同名表中的对象加入到 :class:`_orm.Session` 中。以下是一个映射示例：

    .. sourcecode:: python

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class MyTable(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    上述类的默认 “schema” 名称为 ``None``，意味着不会在 SQL 语句中写入 schema 限定名。然而，如果我们使用 :paramref:`_engine.Connection.execution_options.schema_translate_map` 并将 ``None`` 映射为其他 schema，则可以将 ``MyTable`` 的实例分别放入两个不同的 schema 中：

    .. sourcecode:: python

        engine = create_engine(
            "postgresql+psycopg://scott:tiger@localhost/test",
        )

        with Session(
            engine.execution_options(schema_translate_map={None: "test_schema"})
        ) as sess:
            sess.add(MyTable(name="this is schema one"))
            sess.commit()

        with Session(
            engine.execution_options(schema_translate_map={None: "test_schema_2"})
        ) as sess:
            sess.add(MyTable(name="this is schema two"))
            sess.commit()

    上面两个代码块分别创建了一个带有不同 schema translate map 的 :class:`_orm.Session` 对象，一个 ``MyTable`` 实例分别被持久化到了 ``test_schema.my_table`` 和 ``test_schema_2.my_table`` 表中。

    上述两个 :class:`_orm.Session` 对象是彼此独立的。如果我们希望在一次事务中持久化这两个对象，则需要使用 :ref:`horizontal_sharding_toplevel` 扩展来实现。

    然而，我们可以如下所示，在一个 session 中查询这些对象：

    .. sourcecode:: python

        with Session(engine) as sess:
            obj1 = sess.scalar(
                select(MyTable)
                .where(MyTable.id == 1)
                .execution_options(
                    schema_translate_map={None: "test_schema"},
                    identity_token="test_schema",
                )
            )
            obj2 = sess.scalar(
                select(MyTable)
                .where(MyTable.id == 1)
                .execution_options(
                    schema_translate_map={None: "test_schema_2"},
                    identity_token="test_schema_2",
                )
            )

    ``obj1`` 和 ``obj2`` 是彼此独立的。然而，它们都引用了 ``MyTable`` 类的主键 id 1，但却是不同的对象。这就是 ``identity_token`` 的作用，可以通过检查每个对象的 :attr:`_orm.InstanceState.key` 来观察这两个不同的标识：

        >>> from sqlalchemy import inspect
        >>> inspect(obj1).key
        (<class '__main__.MyTable'>, (1,), 'test_schema')
        >>> inspect(obj2).key
        (<class '__main__.MyTable'>, (1,), 'test_schema_2')

    以上逻辑在使用 :ref:`horizontal_sharding_toplevel` 扩展时会自动处理。

    .. versionadded:: 2.0.0rc1 

        - 新增了 ``identity_token`` ORM 层级执行选项。

    .. seealso::

        :ref:`examples_sharding` - 位于 :ref:`examples_toplevel` 部分。示例脚本 ``separate_schema_translates.py`` 展示了上述使用场景的完整分片 API 实现。


.. tab:: 英文

    .. deepalchemy::   
        
        This option is an advanced-use feature mostly intended to be used with the :ref:`horizontal_sharding_toplevel` extension. For typical cases of loading objects with identical primary keys from different "shards" or partitions, consider using individual :class:`_orm.Session` objects per shard first.


    The "identity token" is an arbitrary value that can be associated within the :term:`identity key` of newly loaded objects.   This element exists first and foremost to support extensions which perform per-row "sharding", where objects may be loaded from any number of replicas of a particular database table that nonetheless have overlapping primary key values. The primary consumer of "identity token" is the :ref:`horizontal_sharding_toplevel` extension, which supplies a general framework for persisting objects among multiple "shards" of a particular database table.

    The ``identity_token`` execution option may be used on a per-query basis to directly affect this token.   Using it directly, one can populate a :class:`_orm.Session` with multiple instances of an object that have the same primary key and source table, but different "identities".

    One such example is to populate a :class:`_orm.Session` with objects that come from same-named tables in different schemas, using the :ref:`schema_translating` feature which can affect the choice of schema within the scope of queries.  Given a mapping as:

    .. sourcecode:: python

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class MyTable(Base):
            __tablename__ = "my_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    The default "schema" name for the class above is ``None``, meaning, no schema qualification will be written into SQL statements.  However, if we make use of :paramref:`_engine.Connection.execution_options.schema_translate_map`, mapping ``None`` to an alternate schema, we can place instances of ``MyTable`` into two different schemas:

    .. sourcecode:: python

        engine = create_engine(
            "postgresql+psycopg://scott:tiger@localhost/test",
        )

        with Session(
            engine.execution_options(schema_translate_map={None: "test_schema"})
        ) as sess:
            sess.add(MyTable(name="this is schema one"))
            sess.commit()

        with Session(
            engine.execution_options(schema_translate_map={None: "test_schema_2"})
        ) as sess:
            sess.add(MyTable(name="this is schema two"))
            sess.commit()

    The above two blocks create a :class:`_orm.Session` object linked to a different schema translate map each time, and an instance of ``MyTable`` is persisted into both ``test_schema.my_table`` as well as ``test_schema_2.my_table``.

    The :class:`_orm.Session` objects above are independent.  If we wanted to persist both objects in one transaction, we would need to use the :ref:`horizontal_sharding_toplevel` extension to do this.

    However, we can illustrate querying for these objects in one session as follows:

    .. sourcecode:: python

        with Session(engine) as sess:
            obj1 = sess.scalar(
                select(MyTable)
                .where(MyTable.id == 1)
                .execution_options(
                    schema_translate_map={None: "test_schema"},
                    identity_token="test_schema",
                )
            )
            obj2 = sess.scalar(
                select(MyTable)
                .where(MyTable.id == 1)
                .execution_options(
                    schema_translate_map={None: "test_schema_2"},
                    identity_token="test_schema_2",
                )
            )

    Both ``obj1`` and ``obj2`` are distinct from each other.  However, they both refer to primary key id 1 for the ``MyTable`` class, yet are distinct. This is how the ``identity_token`` comes into play, which we can see in the inspection of each object, where we look at :attr:`_orm.InstanceState.key` to view the two distinct identity tokens::

        >>> from sqlalchemy import inspect
        >>> inspect(obj1).key
        (<class '__main__.MyTable'>, (1,), 'test_schema')
        >>> inspect(obj2).key
        (<class '__main__.MyTable'>, (1,), 'test_schema_2')


    The above logic takes place automatically when using the :ref:`horizontal_sharding_toplevel` extension.

    .. versionadded:: 2.0.0rc1 
        
        - added the ``identity_token`` ORM level execution option.

    .. seealso::

        :ref:`examples_sharding` - in the :ref:`examples_toplevel` section. See the script ``separate_schema_translates.py`` for a demonstration of the above use case using the full sharding API.


.. doctest-enable:

.. _queryguide_inspection:

检查启用 ORM 的 SELECT 和 DML 语句中的实体和列
==========================================================================

Inspecting entities and columns from ORM-enabled SELECT and DML statements

.. tab:: 中文

    :func:`_sql.select` 构造函数，以及 :func:`_sql.insert`、:func:`_sql.update` 和 :func:`_sql.delete` 构造函数（对于后者 DML 构造，自 SQLAlchemy 1.4.33 起），都支持对创建这些语句所引用的实体进行检查，并能获取结果集中将返回的列和数据类型等信息。

    对于一个 :class:`.Select` 对象，这些信息可通过其 :attr:`.Select.column_descriptions` 属性获得。该属性的行为方式与传统的 :attr:`.Query.column_descriptions` 属性相同。返回格式为一个字典列表，如下所示::

        >>> from pprint import pprint
        >>> user_alias = aliased(User, name="user2")
        >>> stmt = select(User, User.id, user_alias)
        >>> pprint(stmt.column_descriptions)
        [{'aliased': False,
        'entity': <class 'User'>,
        'expr': <class 'User'>,
        'name': 'User',
        'type': <class 'User'>},
        {'aliased': False,
        'entity': <class 'User'>,
        'expr': <....InstrumentedAttribute object at ...>,
        'name': 'id',
        'type': Integer()},
        {'aliased': True,
        'entity': <AliasedClass ...; User>,
        'expr': <AliasedClass ...; User>,
        'name': 'user2',
        'type': <class 'User'>}]

    当 :attr:`.Select.column_descriptions` 与非 ORM 对象（如普通的 :class:`.Table` 或 :class:`.Column` 对象）一起使用时，返回的条目将始终包含有关返回列的基础信息::

        >>> stmt = select(user_table, address_table.c.id)
        >>> pprint(stmt.column_descriptions)
        [{'expr': Column('id', Integer(), table=<user_account>, primary_key=True, nullable=False),
        'name': 'id',
        'type': Integer()},
        {'expr': Column('name', String(), table=<user_account>, nullable=False),
        'name': 'name',
        'type': String()},
        {'expr': Column('fullname', String(), table=<user_account>),
        'name': 'fullname',
        'type': String()},
        {'expr': Column('id', Integer(), table=<address>, primary_key=True, nullable=False),
        'name': 'id_1',
        'type': Integer()}]

    .. versionchanged:: 1.4.33

        当使用在非 ORM 启用的 :class:`.Select` 对象上时，:attr:`.Select.column_descriptions` 属性现在会返回值；此前会抛出 ``NotImplementedError``。

    对于 :func:`_sql.insert`、:func:`.update` 和 :func:`.delete` 构造函数，有两个独立的属性可用。其一是 :attr:`.UpdateBase.entity_description`，该属性返回有关主 ORM 实体及该 DML 语句将影响的数据库表的信息::

        >>> from sqlalchemy import update
        >>> stmt = update(User).values(name="somename").returning(User.id)
        >>> pprint(stmt.entity_description)
        {'entity': <class 'User'>,
        'expr': <class 'User'>,
        'name': 'User',
        'table': Table('user_account', ...),
        'type': <class 'User'>}

    .. tip::

        :attr:`.UpdateBase.entity_description` 中包含的 ``"table"`` 条目表示 **语句将插入、更新或删除的实际数据表**，这通常 **并不等同于** 该类所映射的 SQL “selectable” 对象。例如，在连接表继承（joined-table inheritance）的场景中，``"table"`` 将指代该实体对应的局部数据表。

    另一个属性是 :attr:`.UpdateBase.returning_column_descriptions`，它以与 :attr:`.Select.column_descriptions` 类似的方式提供 RETURNING 子句中各列的信息::

        >>> pprint(stmt.returning_column_descriptions)
        [{'aliased': False,
        'entity': <class 'User'>,
        'expr': <sqlalchemy.orm.attributes.InstrumentedAttribute ...>,
        'name': 'id',
        'type': Integer()}]

    .. versionadded:: 1.4.33

        新增了 :attr:`.UpdateBase.entity_description` 和 :attr:`.UpdateBase.returning_column_descriptions` 属性。

.. tab:: 英文

    The :func:`_sql.select` construct, as well as the :func:`_sql.insert`, :func:`_sql.update` and :func:`_sql.delete` constructs (for the latter DML constructs, as of SQLAlchemy 1.4.33), all support the ability to inspect the entities in which these statements are created against, as well as the columns and datatypes that would be returned in a result set.

    For a :class:`.Select` object, this information is available from the :attr:`.Select.column_descriptions` attribute. This attribute operates in the same way as the legacy :attr:`.Query.column_descriptions` attribute. The format returned is a list of dictionaries::

        >>> from pprint import pprint
        >>> user_alias = aliased(User, name="user2")
        >>> stmt = select(User, User.id, user_alias)
        >>> pprint(stmt.column_descriptions)
        [{'aliased': False,
        'entity': <class 'User'>,
        'expr': <class 'User'>,
        'name': 'User',
        'type': <class 'User'>},
        {'aliased': False,
        'entity': <class 'User'>,
        'expr': <....InstrumentedAttribute object at ...>,
        'name': 'id',
        'type': Integer()},
        {'aliased': True,
        'entity': <AliasedClass ...; User>,
        'expr': <AliasedClass ...; User>,
        'name': 'user2',
        'type': <class 'User'>}]


    When :attr:`.Select.column_descriptions` is used with non-ORM objects such as plain :class:`.Table` or :class:`.Column` objects, the entries will contain basic information about individual columns returned in all cases::

        >>> stmt = select(user_table, address_table.c.id)
        >>> pprint(stmt.column_descriptions)
        [{'expr': Column('id', Integer(), table=<user_account>, primary_key=True, nullable=False),
        'name': 'id',
        'type': Integer()},
        {'expr': Column('name', String(), table=<user_account>, nullable=False),
        'name': 'name',
        'type': String()},
        {'expr': Column('fullname', String(), table=<user_account>),
        'name': 'fullname',
        'type': String()},
        {'expr': Column('id', Integer(), table=<address>, primary_key=True, nullable=False),
        'name': 'id_1',
        'type': Integer()}]

    .. versionchanged:: 1.4.33 
        
        The :attr:`.Select.column_descriptions` attribute now returns a value when used against a :class:`.Select` that is not ORM-enabled.  Previously, this would raise ``NotImplementedError``.


    For :func:`_sql.insert`, :func:`.update` and :func:`.delete` constructs, there are two separate attributes. One is :attr:`.UpdateBase.entity_description` which returns information about the primary ORM entity and database table which the DML construct would be affecting::

        >>> from sqlalchemy import update
        >>> stmt = update(User).values(name="somename").returning(User.id)
        >>> pprint(stmt.entity_description)
        {'entity': <class 'User'>,
        'expr': <class 'User'>,
        'name': 'User',
        'table': Table('user_account', ...),
        'type': <class 'User'>}

    .. tip::  
        
        The :attr:`.UpdateBase.entity_description` includes an entry ``"table"`` which is actually the **table to be inserted, updated or deleted** by the statement, which is **not** always the same as the SQL "selectable" to which the class may be mapped. For example, in a joined-table inheritance scenario, ``"table"`` will refer to the local table for the given entity.

    The other is :attr:`.UpdateBase.returning_column_descriptions` which delivers information about the columns present in the RETURNING collection in a manner roughly similar to that of :attr:`.Select.column_descriptions`::

        >>> pprint(stmt.returning_column_descriptions)
        [{'aliased': False,
        'entity': <class 'User'>,
        'expr': <sqlalchemy.orm.attributes.InstrumentedAttribute ...>,
        'name': 'id',
        'type': Integer()}]

    .. versionadded:: 1.4.33 
        
        Added the :attr:`.UpdateBase.entity_description` and :attr:`.UpdateBase.returning_column_descriptions` attributes.


.. _queryguide_additional:

其他 ORM API 构造
=============================

Additional ORM API Constructs

.. tab:: 中文

.. tab:: 英文


.. autofunction:: sqlalchemy.orm.aliased

.. autoclass:: sqlalchemy.orm.util.AliasedClass

.. autoclass:: sqlalchemy.orm.util.AliasedInsp

.. autoclass:: sqlalchemy.orm.Bundle
    :members:

.. autofunction:: sqlalchemy.orm.with_loader_criteria

.. autofunction:: sqlalchemy.orm.join

.. autofunction:: sqlalchemy.orm.outerjoin

.. autofunction:: sqlalchemy.orm.with_parent


..  Setup code, not for display

    >>> session.close()
    >>> conn.close()
    ROLLBACK
