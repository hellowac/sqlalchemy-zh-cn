.. _faq_performance:

性能
===========

Performance

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _faq_new_caching:

为什么升级到 1.4 和/或 2.x 后我的应用程序运行缓慢？
--------------------------------------------------------------

Why is my application slow after upgrading to 1.4 and/or 2.x?

.. tab:: 中文

    从 SQLAlchemy 1.4 版本开始，新增了一个 :ref:`SQL 编译缓存功能 <sql_caching>`，该功能允许 Core 和 ORM SQL 构造缓存其字符串形式以及用于从语句中获取结果的其他结构信息，从而跳过相对昂贵的字符串编译过程，当下次使用结构上等效的构造时，避免重复编译。该系统依赖于对所有 SQL 构造实现的功能，包括 :class:`_schema.Column`、:func:`_sql.select` 和 :class:`_types.TypeEngine` 对象，生成一个 **缓存键** ，该键完全表示它们的状态，直到影响 SQL 编译过程的程度。

    该缓存系统使得 SQLAlchemy 1.4 及更高版本在将 SQL 构造重复转换为字符串的时间上，相比 SQLAlchemy 1.3 更加高效。然而，只有在启用了适用于方言和 SQL 构造的缓存时，才会生效；如果没有启用，字符串编译通常与 SQLAlchemy 1.3 的表现类似，在某些情况下可能会略微降低速度。

    然而，有一种情况，如果 SQLAlchemy 的新缓存系统被禁用（原因如下），则 ORM 的性能可能比 1.3 或更早版本差，原因在于 ORM 懒加载器和对象刷新查询缺乏缓存，这些查询在 1.3 及更早版本中使用了现在已废弃的 ``BakedQuery`` 系统。如果应用程序在切换到 1.4 后，出现了显著的性能下降（30% 或更高的操作完成时间增长），这很可能是由于此问题，相关的缓解步骤见下文。

    .. seealso::

        :ref:`sql_caching` - 缓存系统概述

        :ref:`caching_caveats` - 关于未启用缓存的元素的额外信息。

.. tab:: 英文

    SQLAlchemy as of version 1.4 includes a
    :ref:`SQL compilation caching facility <sql_caching>` which will allow
    Core and ORM SQL constructs to cache their stringified form, along with other
    structural information used to fetch results from the statement, allowing the
    relatively expensive string compilation process to be skipped when another
    structurally equivalent construct is next used. This system
    relies upon functionality that is implemented for all SQL constructs, including
    objects such as  :class:`_schema.Column`,
    :func:`_sql.select`, and :class:`_types.TypeEngine` objects, to produce a
    **cache key** which fully represents their state to the degree that it affects
    the SQL compilation process.

    The caching system allows SQLAlchemy 1.4 and above to be more performant than
    SQLAlchemy 1.3 with regards to the time spent converting SQL constructs into
    strings repeatedly.  However, this only works if caching is enabled for the
    dialect and SQL constructs in use; if not, string compilation is usually
    similar to that of SQLAlchemy 1.3, with a slight decrease in speed in some
    cases.

    There is one case however where if SQLAlchemy's new caching system has been
    disabled (for reasons below), performance for the ORM may be in fact
    significantly poorer than that of 1.3 or other prior releases which is due to
    the lack of caching within ORM lazy loaders and object refresh queries, which
    in the 1.3 and earlier releases used the now-legacy ``BakedQuery`` system. If
    an application is seeing significant (30% or higher) degradations in
    performance (measured in time for operations to complete) when switching to
    1.4, this is the likely cause of the issue, with steps to mitigate below.

    .. seealso::

        :ref:`sql_caching` - overview of the caching system

        :ref:`caching_caveats` - additional information regarding the warnings
        generated for elements that don't enable caching.

第一步 - 打开 SQL 日志并确认缓存是否正常工作
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Step one - turn on SQL logging and confirm whether or not caching is working

.. tab:: 中文

    在此，我们希望使用 :ref:`engine logging <sql_caching_logging>` 中描述的技术，查找带有 ``[no key]`` 指示符或甚至 ``[dialect does not support caching]`` 的语句。成功参与缓存系统的 SQL 语句在第一次调用时会显示 ``[generated in Xs]``，而在随后的大多数语句中，则会显示 ``[cached since Xs ago]``。如果对于 SELECT 语句， ``[no key]`` 显示得特别明显，或者由于 ``[dialect does not support caching]`` 完全禁用了缓存，这可能是导致性能显著下降的原因。

    .. seealso::

        :ref:`sql_caching_logging`

.. tab:: 英文

    Here, we want to use the technique described at
    :ref:`engine logging <sql_caching_logging>`, looking for statements with the
    ``[no key]`` indicator or even ``[dialect does not support caching]``.
    The indicators we would see for SQL statements that are successfully participating
    in the caching system would be indicating ``[generated in Xs]`` when
    statements are invoked for the first time and then
    ``[cached since Xs ago]`` for the vast majority of statements subsequent.
    If ``[no key]`` is prevalent in particular for SELECT statements, or
    if caching is disabled entirely due to ``[dialect does not support caching]``,
    this can be the cause of significant performance degradation.

    .. seealso::

        :ref:`sql_caching_logging`


第二步 - 确定哪些结构阻止启用缓存
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Step two - identify what constructs are blocking caching from being enabled

.. tab:: 中文

    假设语句未被缓存，应用程序的日志中应该会早期显示警告（仅限 SQLAlchemy 1.4.28 及以上版本），指示未参与缓存的方言、:class:`.TypeEngine` 对象和 SQL 构造。

    对于用户自定义数据类型（如扩展了 :class:`_types.TypeDecorator` 和 :class:`_types.UserDefinedType` 的类型），警告将如下所示：

    .. sourcecode:: text

        sqlalchemy.ext.SAWarning: MyType 将不会生成缓存键，因为
        ``cache_ok`` 属性未设置为 True。这可能会带来显著的性能影响，
        包括与以前版本的 SQLAlchemy 相比，性能下降。若此类型对象的状态
        可以安全地用于缓存键，请将此属性设置为 True，或设置为 False 以禁用此警告。

    对于自定义和第三方 SQL 元素（如使用 :ref:`sqlalchemy.ext.compiler_toplevel` 中描述的技术构建的元素），这些警告将如下所示：

    .. sourcecode:: text

        sqlalchemy.exc.SAWarning: 类 MyClass 将不会使用 SQL 编译缓存，
        因为它未将 'inherit_cache' 属性设置为 ``True``。这可能会带来显著的
        性能影响，包括与以前版本的 SQLAlchemy 相比，性能下降。如果此对象
        可以使用由超类生成的缓存键，请将此属性设置为 True。或者，您可以
        将此属性设置为 False 来禁用此警告。

    对于使用 :class:`.Dialect` 类层次结构的自定义和第三方方言，这些警告将如下所示：

    .. sourcecode:: text

        sqlalchemy.exc.SAWarning: 方言 database:driver 将不会使用 SQL 编译缓存，
        因为它未将 'supports_statement_cache' 属性设置为 ``True``。这可能会
        带来显著的性能影响，包括与以前版本的 SQLAlchemy 相比，性能下降。
        方言维护者应在适当的开发和测试后，设置此属性为 True，以支持 SQLAlchemy 1.4 缓存。
        否则，您可以将此属性设置为 False 来禁用此警告。

.. tab:: 英文

    Assuming statements are not being cached, there should be warnings emitted
    early in the application's log (SQLAlchemy 1.4.28 and above only) indicating
    dialects, :class:`.TypeEngine` objects, and SQL constructs that are not
    participating in caching.

    For user defined datatypes such as those which extend :class:`_types.TypeDecorator`
    and :class:`_types.UserDefinedType`, the warnings will look like:

    .. sourcecode:: text

        sqlalchemy.ext.SAWarning: MyType will not produce a cache key because the
        ``cache_ok`` attribute is not set to True. This can have significant
        performance implications including some performance degradations in
        comparison to prior SQLAlchemy versions. Set this attribute to True if this
        type object's state is safe to use in a cache key, or False to disable this
        warning.

    For custom and third party SQL elements, such as those constructed using
    the techniques described at :ref:`sqlalchemy.ext.compiler_toplevel`, these
    warnings will look like:

    .. sourcecode:: text

        sqlalchemy.exc.SAWarning: Class MyClass will not make use of SQL
        compilation caching as it does not set the 'inherit_cache' attribute to
        ``True``. This can have significant performance implications including some
        performance degradations in comparison to prior SQLAlchemy versions. Set
        this attribute to True if this object can make use of the cache key
        generated by the superclass. Alternatively, this attribute may be set to
        False which will disable this warning.

    For custom and third party dialects which make use of the :class:`.Dialect`
    class hierarchy, the warnings will look like:

    .. sourcecode:: text

        sqlalchemy.exc.SAWarning: Dialect database:driver will not make use of SQL
        compilation caching as it does not set the 'supports_statement_cache'
        attribute to ``True``. This can have significant performance implications
        including some performance degradations in comparison to prior SQLAlchemy
        versions. Dialect maintainers should seek to set this attribute to True
        after appropriate development and testing for SQLAlchemy 1.4 caching
        support. Alternatively, this attribute may be set to False which will
        disable this warning.


第三步 - 为给定对象启用缓存和/或寻找替代方案
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Step three - enable caching for the given objects and/or seek alternatives

.. tab:: 中文

    解决缺少缓存问题的步骤包括：
    
    * 检查并将 :attr:`.ExternalType.cache_ok` 设置为 ``True``，适用于所有继承自 :class:`_types.TypeDecorator`、:class:`_types.UserDefinedType` 的自定义类型，以及这些类型的子类，例如 :class:`_types.PickleType`。 **仅在** 自定义类型不包含任何额外的状态属性，且这些属性不会影响 SQL 渲染时，设置此选项::
    
            class MyCustomType(TypeDecorator):
                cache_ok = True
                impl = String
    
      如果使用的类型来自第三方库，请与该库的维护者协作，以便进行调整并发布新版。
    
      .. seealso::
    
        :attr:`.ExternalType.cache_ok` - 启用自定义数据类型缓存的要求背景信息。
    
    * 确保第三方方言将 :attr:`.Dialect.supports_statement_cache` 设置为 ``True``。这表明第三方方言的维护者已经确保其方言与 SQLAlchemy 1.4 或更高版本兼容，并且该方言不包含可能干扰缓存的编译特性。由于存在一些常见的编译模式可能会干扰缓存，因此方言维护者需要仔细检查并测试这一点，调整任何与缓存不兼容的遗留模式。
    
      .. seealso::
    
          :ref:`engine_thirdparty_caching` - 第三方方言参与 SQL 语句缓存的背景和示例。
    
    * 自定义 SQL 类，包括使用 :ref:`sqlalchemy.ext.compiler_toplevel` 创建的所有 DQL / DML 构造，以及诸如 :class:`_schema.Column` 或 :class:`_schema.Table` 等对象的临时子类。可以将 :attr:`.HasCacheKey.inherit_cache` 属性设置为 ``True``，适用于那些不包含任何特定于子类的状态信息且不会影响 SQL 编译的简单子类。
    
      .. seealso::
    
        :ref:`compilerext_caching` - 应用 :attr:`.HasCacheKey.inherit_cache` 属性的指南。
    
    .. seealso::
    
        :ref:`sql_caching` - 缓存系统概述
    
        :ref:`caching_caveats` - 当特定构造和/或方言未启用缓存时发出的警告背景信息。

.. tab:: 英文

    Steps to mitigate the lack of caching include:
    
    * Review and set :attr:`.ExternalType.cache_ok` to ``True`` for all custom types
      which extend from :class:`_types.TypeDecorator`,
      :class:`_types.UserDefinedType`, as well as subclasses of these such as
      :class:`_types.PickleType`.  Set this **only** if the custom type does not
      include any additional state attributes which affect how it renders SQL::
    
            class MyCustomType(TypeDecorator):
                cache_ok = True
                impl = String
    
      If the types in use are from a third-party library, consult with the
      maintainers of that library so that it may be adjusted and released.
    
      .. seealso::
    
        :attr:`.ExternalType.cache_ok` - background on requirements to enable
        caching for custom datatypes.
    
    * Make sure third party dialects set :attr:`.Dialect.supports_statement_cache`
      to ``True``. What this indicates is that the maintainers of a third party
      dialect have made sure their dialect works with SQLAlchemy 1.4 or greater,
      and that their dialect doesn't include any compilation features which may get
      in the way of caching. As there are some common compilation patterns which
      can in fact interfere with caching, it's important that dialect maintainers
      check and test this carefully, adjusting for any of the legacy patterns
      which won't work with caching.
    
      .. seealso::
    
          :ref:`engine_thirdparty_caching` - background and examples for third-party
          dialects to participate in SQL statement caching.
    
    * Custom SQL classes, including all DQL / DML constructs one might create
      using the :ref:`sqlalchemy.ext.compiler_toplevel`, as well as ad-hoc
      subclasses of objects such as :class:`_schema.Column` or
      :class:`_schema.Table`.   The :attr:`.HasCacheKey.inherit_cache` attribute
      may be set to ``True`` for trivial subclasses, which do not contain any
      subclass-specific state information which affects the SQL compilation.
    
      .. seealso::
    
        :ref:`compilerext_caching` - guidelines for applying the
        :attr:`.HasCacheKey.inherit_cache` attribute.
    
    
    .. seealso::
    
        :ref:`sql_caching` - caching system overview
    
        :ref:`caching_caveats` - background on warnings emitted when caching
        is not enabled for specific constructs and/or dialects.


.. _faq_how_to_profile:

如何分析 SQLAlchemy 支持的应用程序？
---------------------------------------------------

How can I profile a SQLAlchemy powered application?

.. tab:: 中文

    查找性能问题通常涉及两种策略。一是查询分析，二是代码分析。

.. tab:: 英文

    Looking for performance issues typically involves two strategies.  One is query profiling, and the other is code profiling.

Query Profiling
^^^^^^^^^^^^^^^

.. tab:: 中文

    有时，普通的 SQL 日志记录（通过 Python 的 logging 模块或通过 :func:`_sa.create_engine` 的 ``echo=True`` 参数启用）可以帮助了解操作所需的时间。例如，如果你在 SQL 操作后立即记录日志，你会在日志中看到如下内容：

    .. sourcecode:: text

        17:37:48,325 INFO  [sqlalchemy.engine.base.Engine.0x...048c] SELECT ...
        17:37:48,326 INFO  [sqlalchemy.engine.base.Engine.0x...048c] {<params>}
        17:37:48,660 DEBUG [myapp.somemessage]

    如果你在操作后记录了 ``myapp.somemessage``，你就知道 SQL 部分的操作花费了 334 毫秒。

    SQL 日志记录还可以显示是否发出了几十/上百个查询，这些查询本可以通过更少的查询来组织。当使用 SQLAlchemy ORM 时，提供了“急切加载”（eager loading）功能，用于部分（:func:`.contains_eager()`）或完全（:func:`_orm.joinedload()`、:func:`.subqueryload()`）自动化此活动，但没有使用 ORM 时，“急切加载”通常意味着使用联接（joins），使得跨多个表的结果可以在一个结果集内加载，而不是随着查询深度的增加而增加查询数量（即 ``r + r*r2 + r*r2*r3`` ...）。

    对于更长期的查询性能分析，或实现一个应用程序端的“慢查询”监控器，可以使用事件拦截游标执行，采用以下方法::

        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        import time
        import logging

        logging.basicConfig()
        logger = logging.getLogger("myapp.sqltime")
        logger.setLevel(logging.DEBUG)


        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())
            logger.debug("Start Query: %s", statement)


        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info["query_start_time"].pop(-1)
            logger.debug("Query Complete!")
            logger.debug("Total Time: %f", total)

    在上述代码中，我们使用了 :meth:`_events.ConnectionEvents.before_cursor_execute` 和 :meth:`_events.ConnectionEvents.after_cursor_execute` 事件来建立拦截点，围绕语句执行时机进行操作。我们通过 :class:`._ConnectionRecord.info` 字典将计时器附加到连接上；在此，我们使用堆栈，以应对偶尔发生的游标执行事件可能是嵌套的情况。

.. tab:: 英文

    Sometimes just plain SQL logging (enabled via python's logging module
    or via the ``echo=True`` argument on :func:`_sa.create_engine`) can give an
    idea how long things are taking.  For example, if you log something
    right after a SQL operation, you'd see something like this in your
    log:

    .. sourcecode:: text

        17:37:48,325 INFO  [sqlalchemy.engine.base.Engine.0x...048c] SELECT ...
        17:37:48,326 INFO  [sqlalchemy.engine.base.Engine.0x...048c] {<params>}
        17:37:48,660 DEBUG [myapp.somemessage]

    if you logged ``myapp.somemessage`` right after the operation, you know
    it took 334ms to complete the SQL part of things.

    Logging SQL will also illustrate if dozens/hundreds of queries are
    being issued which could be better organized into much fewer queries.
    When using the SQLAlchemy ORM, the "eager loading"
    feature is provided to partially (:func:`.contains_eager()`) or fully
    (:func:`_orm.joinedload()`, :func:`.subqueryload()`)
    automate this activity, but without
    the ORM "eager loading" typically means to use joins so that results across multiple
    tables can be loaded in one result set instead of multiplying numbers
    of queries as more depth is added (i.e. ``r + r*r2 + r*r2*r3`` ...)

    For more long-term profiling of queries, or to implement an application-side
    "slow query" monitor, events can be used to intercept cursor executions,
    using a recipe like the following::

        from sqlalchemy import event
        from sqlalchemy.engine import Engine
        import time
        import logging

        logging.basicConfig()
        logger = logging.getLogger("myapp.sqltime")
        logger.setLevel(logging.DEBUG)


        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            conn.info.setdefault("query_start_time", []).append(time.time())
            logger.debug("Start Query: %s", statement)


        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
            total = time.time() - conn.info["query_start_time"].pop(-1)
            logger.debug("Query Complete!")
            logger.debug("Total Time: %f", total)

    Above, we use the :meth:`_events.ConnectionEvents.before_cursor_execute` and
    :meth:`_events.ConnectionEvents.after_cursor_execute` events to establish an interception
    point around when a statement is executed.  We attach a timer onto the
    connection using the :class:`._ConnectionRecord.info` dictionary; we use a
    stack here for the occasional case where the cursor execute events may be nested.

.. _faq_code_profiling:

代码分析
^^^^^^^^^^^^^^

Code Profiling

.. tab:: 中文

    如果日志记录显示单个查询的执行时间过长，您需要进一步拆解各个阶段的时间消耗，包括数据库内部处理查询、通过网络发送结果、由 :term:`DBAPI` 处理，最终由 SQLAlchemy 的结果集和/或 ORM 层接收。每个阶段都可能有各自的瓶颈，具体情况取决于细节。

    为此，您需要使用 `Python Profiling Module <https://docs.python.org/2/library/profile.html>`_。下面是一个简单的示例，展示了如何将性能分析集成到上下文管理器中::

        import cProfile
        import io
        import pstats
        import contextlib


        @contextlib.contextmanager
        def profiled():
            pr = cProfile.Profile()
            pr.enable()
            yield
            pr.disable()
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
            ps.print_stats()
            # 取消注释以查看哪些函数被调用
            # ps.print_callers()
            print(s.getvalue())

    要对代码的某一部分进行性能分析，可以按如下方式使用：

        with profiled():
            session.scalars(select(FooClass).where(FooClass.somevalue == 8)).all()

    性能分析的输出可以帮助我们了解时间的消耗在哪里。一部分性能分析输出可能如下所示：

    .. sourcecode:: text

        13726 function calls (13042 primitive calls) in 0.014 seconds

        Ordered by: cumulative time

        ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        222/21    0.001    0.000    0.011    0.001 lib/sqlalchemy/orm/loading.py:26(instances)
        220/20    0.002    0.000    0.010    0.001 lib/sqlalchemy/orm/loading.py:327(_instance)
        220/20    0.000    0.000    0.010    0.000 lib/sqlalchemy/orm/loading.py:284(populate_state)
        20    0.000    0.000    0.010    0.000 lib/sqlalchemy/orm/strategies.py:987(load_collection_from_subq)
        20    0.000    0.000    0.009    0.000 lib/sqlalchemy/orm/strategies.py:935(get)
            1    0.000    0.000    0.009    0.009 lib/sqlalchemy/orm/strategies.py:940(_load)
        21    0.000    0.000    0.008    0.000 lib/sqlalchemy/orm/strategies.py:942(<genexpr>)
            2    0.000    0.000    0.004    0.002 lib/sqlalchemy/orm/query.py:2400(__iter__)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/orm/query.py:2414(_execute_and_instances)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/engine/base.py:659(execute)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/sql/elements.py:321(_execute_on_connection)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/engine/base.py:788(_execute_clauseelement)

        ...

    从上述输出可以看出，SQLAlchemy 的 ``instances()`` 函数被调用了 222 次（递归调用，其中 21 次是外部调用），所有调用的总时间为 0.011 秒。
    
.. tab:: 英文

    If logging reveals that individual queries are taking too long, you'd
    need a breakdown of how much time was spent within the database
    processing the query, sending results over the network, being handled
    by the :term:`DBAPI`, and finally being received by SQLAlchemy's result set
    and/or ORM layer.   Each of these stages can present their own
    individual bottlenecks, depending on specifics.

    For that you need to use the
    `Python Profiling Module <https://docs.python.org/2/library/profile.html>`_.
    Below is a simple recipe which works profiling into a context manager::

        import cProfile
        import io
        import pstats
        import contextlib


        @contextlib.contextmanager
        def profiled():
            pr = cProfile.Profile()
            pr.enable()
            yield
            pr.disable()
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
            ps.print_stats()
            # uncomment this to see who's calling what
            # ps.print_callers()
            print(s.getvalue())

    To profile a section of code::

        with profiled():
            session.scalars(select(FooClass).where(FooClass.somevalue == 8)).all()

    The output of profiling can be used to give an idea where time is
    being spent.   A section of profiling output looks like this:

    .. sourcecode:: text

        13726 function calls (13042 primitive calls) in 0.014 seconds

        Ordered by: cumulative time

        ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        222/21    0.001    0.000    0.011    0.001 lib/sqlalchemy/orm/loading.py:26(instances)
        220/20    0.002    0.000    0.010    0.001 lib/sqlalchemy/orm/loading.py:327(_instance)
        220/20    0.000    0.000    0.010    0.000 lib/sqlalchemy/orm/loading.py:284(populate_state)
        20    0.000    0.000    0.010    0.000 lib/sqlalchemy/orm/strategies.py:987(load_collection_from_subq)
        20    0.000    0.000    0.009    0.000 lib/sqlalchemy/orm/strategies.py:935(get)
            1    0.000    0.000    0.009    0.009 lib/sqlalchemy/orm/strategies.py:940(_load)
        21    0.000    0.000    0.008    0.000 lib/sqlalchemy/orm/strategies.py:942(<genexpr>)
            2    0.000    0.000    0.004    0.002 lib/sqlalchemy/orm/query.py:2400(__iter__)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/orm/query.py:2414(_execute_and_instances)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/engine/base.py:659(execute)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/sql/elements.py:321(_execute_on_connection)
            2    0.000    0.000    0.002    0.001 lib/sqlalchemy/engine/base.py:788(_execute_clauseelement)

        ...

    Above, we can see that the ``instances()`` SQLAlchemy function was called 222
    times (recursively, and 21 times from the outside), taking a total of .011
    seconds for all calls combined.

执行缓慢
^^^^^^^^^^^^^^^^^^

Execution Slowness

.. tab:: 中文

    这些调用的具体情况可以帮助我们了解时间消耗的来源。例如，如果在 ``cursor.execute()`` 中消耗了时间，例如 DBAPI：

    .. sourcecode:: text

        2    0.102    0.102    0.204    0.102 {method 'execute' of 'sqlite3.Cursor' objects}

    这表明数据库在返回结果时花费了较长时间，意味着需要优化查询，可能通过添加索引或重构查询和/或底层架构来实现。为此任务，建议使用数据库后端提供的查询计划分析工具，如 EXPLAIN、SHOW PLAN 等。

.. tab:: 英文

    The specifics of these calls can tell us where the time is being spent.
    If for example, you see time being spent within ``cursor.execute()``,
    e.g. against the DBAPI:

    .. sourcecode:: text

        2    0.102    0.102    0.204    0.102 {method 'execute' of 'sqlite3.Cursor' objects}

    this would indicate that the database is taking a long time to start returning
    results, and it means your query should be optimized, either by adding indexes
    or restructuring the query and/or underlying schema.  For that task,
    analysis of the query plan is warranted, using a system such as EXPLAIN,
    SHOW PLAN, etc. as is provided by the database backend.

结果获取缓慢 - 核心
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Result Fetching Slowness - Core

.. tab:: 中文
    
    另一方面，如果您看到与获取行相关的调用次数极多，或 ``fetchall()`` 调用非常长时间，这可能意味着查询返回了比预期更多的行，或者获取行本身很慢。ORM 本身通常使用 ``fetchall()`` 获取行（如果使用了 :meth:`_query.Query.yield_per` 选项，则使用 ``fetchmany()`` ）。
    
    如果在 DBAPI 层看到 ``fetchall()`` 调用时间异常慢，这可能是因为查询返回的行数过多：
    
    .. sourcecode:: text
    
        2    0.300    0.600    0.300    0.600 {method 'fetchall' of 'sqlite3.Cursor' objects}
    
    即使最终结果看起来没有太多行，意外地多的行数也可能是由笛卡尔积造成的——多个行集被组合在一起，而没有适当地联接表。使用 SQLAlchemy Core 或 ORM 查询时，如果在复杂查询中使用了错误的 :class:`_schema.Column` 对象，就容易产生这种行为，导致额外的 FROM 子句被意外地引入。
    
    另一方面，如果在 DBAPI 层看到 ``fetchall()`` 调用很快，但在 SQLAlchemy 的 :class:`_engine.CursorResult` 执行 ``fetchall()`` 时变得很慢，可能是由于数据类型处理的慢速，比如 Unicode 转换等：
    
    .. sourcecode:: text
    
        # DBAPI 游标执行很快...
        2    0.020    0.040    0.020    0.040 {method 'fetchall' of 'sqlite3.Cursor' objects}
    
        ...
    
        # 但 SQLAlchemy 的结果代理很慢，这是类型级别的处理
        2    0.100    0.200    0.100    0.200 lib/sqlalchemy/engine/result.py:778(fetchall)
    
    在某些情况下，后端可能正在执行不必要的类型级别处理。更具体地说，如果在类型 API 中看到慢速的调用，那通常是更好的指示，下面是当我们使用类似的类型时的表现::
    
        from sqlalchemy import TypeDecorator
        import time
    
    
        class Foo(TypeDecorator):
            impl = String
    
            def process_result_value(self, value, thing):
                # 有意添加延迟以供演示
                time.sleep(0.001)
                return value
    
    这种故意延迟操作的性能分析输出如下所示：
    
    .. sourcecode:: text
    
          200    0.001    0.000    0.237    0.001 lib/sqlalchemy/sql/type_api.py:911(process)
          200    0.001    0.000    0.236    0.001 test.py:28(process_result_value)
          200    0.235    0.001    0.235    0.001 {time.sleep}
    
    在这里，我们看到 ``type_api`` 系统中的许多耗时调用，实际上最消耗时间的是 ``time.sleep()`` 调用。
    
    确保查看 :ref:`Dialect documentation <dialect_toplevel>` 以获取关于在这一层面进行已知性能调优的建议，特别是对于像 Oracle 这样的数据库。可能存在一些与确保数值精度或字符串处理相关的系统，在某些情况下可能并不需要这些处理。
    
    另外，还有一些更低级的地方可能导致行获取性能下降；例如，如果时间消耗集中在类似 ``socket.receive()`` 的调用上，可能表明网络连接本身非常慢，而数据在网络中传输的时间过长。

.. tab:: 英文

    If on the other hand you see many thousands of calls related to fetching rows,
    or very long calls to ``fetchall()``, it may
    mean your query is returning more rows than expected, or that the fetching
    of rows itself is slow.   The ORM itself typically uses ``fetchall()`` to fetch
    rows (or ``fetchmany()`` if the :meth:`_query.Query.yield_per` option is used).

    An inordinately large number of rows would be indicated
    by a very slow call to ``fetchall()`` at the DBAPI level:

    .. sourcecode:: text

        2    0.300    0.600    0.300    0.600 {method 'fetchall' of 'sqlite3.Cursor' objects}

    An unexpectedly large number of rows, even if the ultimate result doesn't seem
    to have many rows, can be the result of a cartesian product - when multiple
    sets of rows are combined together without appropriately joining the tables
    together.   It's often easy to produce this behavior with SQLAlchemy Core or
    ORM query if the wrong :class:`_schema.Column` objects are used in a complex query,
    pulling in additional FROM clauses that are unexpected.

    On the other hand, a fast call to ``fetchall()`` at the DBAPI level, but then
    slowness when SQLAlchemy's :class:`_engine.CursorResult` is asked to do a ``fetchall()``,
    may indicate slowness in processing of datatypes, such as unicode conversions
    and similar:

    .. sourcecode:: text

        # the DBAPI cursor is fast...
        2    0.020    0.040    0.020    0.040 {method 'fetchall' of 'sqlite3.Cursor' objects}

        ...

        # but SQLAlchemy's result proxy is slow, this is type-level processing
        2    0.100    0.200    0.100    0.200 lib/sqlalchemy/engine/result.py:778(fetchall)

    In some cases, a backend might be doing type-level processing that isn't
    needed.   More specifically, seeing calls within the type API that are slow
    are better indicators - below is what it looks like when we use a type like
    this::

        from sqlalchemy import TypeDecorator
        import time


        class Foo(TypeDecorator):
            impl = String

            def process_result_value(self, value, thing):
                # intentionally add slowness for illustration purposes
                time.sleep(0.001)
                return value

    the profiling output of this intentionally slow operation can be seen like this:

    .. sourcecode:: text

        200    0.001    0.000    0.237    0.001 lib/sqlalchemy/sql/type_api.py:911(process)
        200    0.001    0.000    0.236    0.001 test.py:28(process_result_value)
        200    0.235    0.001    0.235    0.001 {time.sleep}

    that is, we see many expensive calls within the ``type_api`` system, and the actual
    time consuming thing is the ``time.sleep()`` call.

    Make sure to check the :ref:`Dialect documentation <dialect_toplevel>`
    for notes on known performance tuning suggestions at this level, especially for
    databases like Oracle.  There may be systems related to ensuring numeric accuracy
    or string processing that may not be needed in all cases.

    There also may be even more low-level points at which row-fetching performance is suffering;
    for example, if time spent seems to focus on a call like ``socket.receive()``,
    that could indicate that everything is fast except for the actual network connection,
    and too much time is spent with data moving over the network.

结果获取缓慢 - ORM
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Result Fetching Slowness - ORM

.. tab:: 中文

    要检测 ORM 在获取行时的慢速（这是最常见的性能瓶颈），如 ``populate_state()`` 和 ``_instance()`` 这样的调用将展示每个 ORM 对象的填充过程：

    .. sourcecode:: text

        # ORM 为每一行加载的对象调用 _instance，
        # 为每一行加载的对象调用 populate_state，以填充对象的属性
        220/20    0.001    0.000    0.010    0.000 lib/sqlalchemy/orm/loading.py:327(_instance)
        220/20    0.000    0.000    0.009    0.000 lib/sqlalchemy/orm/loading.py:284(populate_state)

    ORM 在将行转换为 ORM 映射对象时的慢速，是由于该操作的复杂性与 cPython 的开销相结合的结果。常见的缓解策略包括：

    * 获取单独的列而不是完整的实体，即::

        select(User.id, User.name)

    而不是::

        select(User)

    * 使用 :class:`.Bundle` 对象组织基于列的结果::

        u_b = Bundle("user", User.id, User.name)
        a_b = Bundle("address", Address.id, Address.email)

        for user, address in session.execute(select(u_b, a_b).join(User.addresses)):
            ...

    * 使用结果缓存 - 参见 :ref:`examples_caching` 获取更深入的示例。

    * 考虑使用更快的解释器，如 PyPy。

    性能分析的输出可能看起来有点令人畏惧，但经过一些练习后，它们非常容易读取。

    .. seealso::

        :ref:`examples_performance` - 一系列包含性能分析功能的性能演示。

.. tab:: 英文

    To detect slowness in ORM fetching of rows (which is the most common area
    of performance concern), calls like ``populate_state()`` and ``_instance()`` will
    illustrate individual ORM object populations:

    .. sourcecode:: text

        # the ORM calls _instance for each ORM-loaded row it sees, and
        # populate_state for each ORM-loaded row that results in the population
        # of an object's attributes
        220/20    0.001    0.000    0.010    0.000 lib/sqlalchemy/orm/loading.py:327(_instance)
        220/20    0.000    0.000    0.009    0.000 lib/sqlalchemy/orm/loading.py:284(populate_state)

    The ORM's slowness in turning rows into ORM-mapped objects is a product
    of the complexity of this operation combined with the overhead of cPython.
    Common strategies to mitigate this include:

    * fetch individual columns instead of full entities, that is::

        select(User.id, User.name)

    instead of::

        select(User)

    * Use :class:`.Bundle` objects to organize column-based results::

        u_b = Bundle("user", User.id, User.name)
        a_b = Bundle("address", Address.id, Address.email)

        for user, address in session.execute(select(u_b, a_b).join(User.addresses)):
            ...

    * Use result caching - see :ref:`examples_caching` for an in-depth example
    of this.

    * Consider a faster interpreter like that of PyPy.

    The output of a profile can be a little daunting but after some
    practice they are very easy to read.

    .. seealso::

        :ref:`examples_performance` - a suite of performance demonstrations
        with bundled profiling capabilities.

我正在使用 ORM 插入 400,000 行，它真的很慢！
-------------------------------------------------------------

I'm inserting 400,000 rows with the ORM and it's really slow!

.. tab:: 中文

    ORM 插入的方式已经发生了变化，因为大多数包含的驱动程序从 SQLAlchemy 2.0 开始支持使用 `RETURNING` 和 :ref:`insertmanyvalues <engine_insertmanyvalues>`。有关详细信息，请参见 :ref:`change_6047` 章节。

    总体来说，除了 MySQL 驱动程序外，SQLAlchemy 内置的驱动程序现在应该能够提供非常快速的 ORM 批量插入性能。

    第三方驱动程序也可以通过一些小的代码更改来支持新的批量插入基础设施，前提是它们的后端支持必要的语法。SQLAlchemy 开发者鼓励第三方方言的用户发布与这些驱动相关的问题，以便他们能与 SQLAlchemy 开发者联系以寻求帮助。

.. tab:: 英文

    The nature of ORM inserts has changed, as most included drivers use RETURNING
    with :ref:`insertmanyvalues <engine_insertmanyvalues>` support as of SQLAlchemy
    2.0. See the section :ref:`change_6047` for details.

    Overall, SQLAlchemy built-in drivers other than that of MySQL should now
    offer very fast ORM bulk insert performance.

    Third party drivers can opt in to the new bulk infrastructure as well with some
    small code changes assuming their backends support the necessary syntaxes.
    SQLAlchemy developers would encourage users of third party dialects to post
    issues with these drivers, so that they may contact SQLAlchemy developers for
    assistance.



