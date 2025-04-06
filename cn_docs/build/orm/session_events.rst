.. _session_events_toplevel:

使用事件跟踪查询、对象和会话更改
=========================================================

Tracking queries, object and Session Changes with Events

.. tab:: 中文

    SQLAlchemy 具有一个广泛的 :ref:`事件监听 <event_toplevel>` 系统，贯穿于 Core 和 ORM。在 ORM 内，有多种事件监听器钩子，在 API 层面上记录在 :ref:`orm_event_toplevel` 。多年来，这些事件集合不断增长，包括许多非常有用的新事件以及一些不再那么相关的旧事件。本节将尝试介绍主要的事件钩子及其可能的使用场景。

.. tab:: 英文

    SQLAlchemy features an extensive :ref:`Event Listening <event_toplevel>`
    system used throughout the Core and ORM.   Within the ORM, there are a
    wide variety of event listener hooks, which are documented at an API
    level at :ref:`orm_event_toplevel`.   This collection of events has
    grown over the years to include lots of very useful new events as well
    as some older events that aren't as relevant as they once were.  This
    section will attempt to introduce the major event hooks and when they
    might be used.

.. _session_execute_events:

执行事件
---------------

Execute Events

.. tab:: 中文

    .. versionadded:: 1.4  
        
        :class:`_orm.Session` 现在新增了一个全面的钩子，用于拦截 ORM 所执行的所有 SELECT 语句，  
        以及批量 UPDATE 和 DELETE 语句。这个钩子取代了之前的 :meth:`_orm.QueryEvents.before_compile`、  
        :meth:`_orm.QueryEvents.before_compile_update` 和 :meth:`_orm.QueryEvents.before_compile_delete` 事件。

    :class:`_orm.Session` 提供了一套完整的机制，允许你拦截并修改所有通过 :meth:`_orm.Session.execute` 方法执行的查询，  
    其中包括所有由 :class:`_orm.Query` 发出的 SELECT 语句，以及在加载列和关系属性时自动发出的 SELECT 语句。  
    该机制使用 :meth:`_orm.SessionEvents.do_orm_execute` 事件钩子和 :class:`_orm.ORMExecuteState` 对象来表示事件状态。

.. tab:: 英文

    .. versionadded:: 1.4  
        
        The :class:`_orm.Session` now features a single comprehensive hook designed to intercept all SELECT statements made on behalf of the ORM as well as bulk UPDATE and DELETE statements. This hook supersedes the previous :meth:`_orm.QueryEvents.before_compile` event as well :meth:`_orm.QueryEvents.before_compile_update` and :meth:`_orm.QueryEvents.before_compile_delete`.

    :class:`_orm.Session` features a comprehensive system by which all queries
    invoked via the :meth:`_orm.Session.execute` method, which includes all
    SELECT statements emitted by :class:`_orm.Query` as well as all SELECT
    statements emitted on behalf of column and relationship loaders, may
    be intercepted and modified.   The system makes use of the
    :meth:`_orm.SessionEvents.do_orm_execute` event hook as well as the
    :class:`_orm.ORMExecuteState` object to represent the event state.


基本查询拦截
^^^^^^^^^^^^^^^^^^^^^^^^^

Basic Query Interception

.. tab:: 中文

    :meth:`_orm.SessionEvents.do_orm_execute` 特别适用于拦截各种查询，包括使用 :term:`1.x style` 的  
    :class:`_orm.Query` 语句，以及在 ORM 启用的上下文中使用 :term:`2.0 style` 构造函数  
    :func:`_sql.select`、:func:`_sql.update` 或 :func:`_sql.delete` 并传递给 :meth:`_orm.Session.execute` 时。

    :class:`_orm.ORMExecuteState` 提供了用于修改语句、参数和执行选项的访问器。例如::

        Session = sessionmaker(engine)


        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if orm_execute_state.is_select:
                # 为所有 SELECT 查询添加 populate_existing 选项
                orm_execute_state.update_execution_options(populate_existing=True)

                # 如果当前 SELECT 针对特定实体，则添加 ORDER BY
                col_descriptions = orm_execute_state.statement.column_descriptions

                if col_descriptions[0]["entity"] is MyEntity:
                    orm_execute_state.statement = statement.order_by(MyEntity.name)

    上述示例演示了如何对 SELECT 查询进行简单的修改。

    在这个层级，:meth:`_orm.SessionEvents.do_orm_execute` 事件钩子的目标是 **替代早期版本中对**  
    :meth:`_orm.QueryEvents.before_compile` **事件的使用**。后者在处理某些类型的加载器时并不总是会被触发，  
    且它只能应用于 :term:`1.x style` 的 :class:`_orm.Query`，而不能用于 :term:`2.0 style` 中的  
    :meth:`_orm.Session.execute` 方式。

.. tab:: 英文

    :meth:`_orm.SessionEvents.do_orm_execute` is firstly useful for any kind of
    interception of a query, which includes those emitted by
    :class:`_orm.Query` with :term:`1.x style` as well as when an ORM-enabled
    :term:`2.0 style` :func:`_sql.select`,
    :func:`_sql.update` or :func:`_sql.delete` construct is delivered to
    :meth:`_orm.Session.execute`.   The :class:`_orm.ORMExecuteState` construct
    provides accessors to allow modifications to statements, parameters, and
    options::

        Session = sessionmaker(engine)


        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if orm_execute_state.is_select:
                # add populate_existing for all SELECT statements

                orm_execute_state.update_execution_options(populate_existing=True)

                # check if the SELECT is against a certain entity and add an
                # ORDER BY if so
                col_descriptions = orm_execute_state.statement.column_descriptions

                if col_descriptions[0]["entity"] is MyEntity:
                    orm_execute_state.statement = statement.order_by(MyEntity.name)

    The above example illustrates some simple modifications to SELECT statements.
    At this level, the :meth:`_orm.SessionEvents.do_orm_execute` event hook intends
    to replace the previous use of the :meth:`_orm.QueryEvents.before_compile` event,
    which was not fired off consistently for various kinds of loaders; additionally,
    the :meth:`_orm.QueryEvents.before_compile` only applies to :term:`1.x style`
    use with :class:`_orm.Query` and not with :term:`2.0 style` use of
    :meth:`_orm.Session.execute`.


.. _do_orm_execute_global_criteria:

添加全局 WHERE / ON 条件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding global WHERE / ON criteria

.. tab:: 中文

    最常被请求的查询扩展功能之一，就是 **为所有查询中的特定实体统一添加 WHERE 条件**。  
    这个功能可以通过 :func:`_orm.with_loader_criteria` 查询选项来实现。它可以独立使用，  
    也可以非常理想地结合 :meth:`_orm.SessionEvents.do_orm_execute` 事件使用::

        from sqlalchemy.orm import with_loader_criteria

        Session = sessionmaker(engine)

        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if (
                orm_execute_state.is_select
                and not orm_execute_state.is_column_load
                and not orm_execute_state.is_relationship_load
            ):
                orm_execute_state.statement = orm_execute_state.statement.options(
                    with_loader_criteria(MyEntity.public == True)
                )

    在上面的例子中，我们为所有对 `MyEntity` 的 SELECT 查询添加了 `public == True` 的过滤条件。  
    该条件会作用于当前查询范围内对该类的 **所有加载操作**。  
    默认情况下，:func:`_orm.with_loader_criteria` 会自动传播到关系加载（relationship loaders），  
    包括懒加载（lazy load）、selectinload 等方式。

    对于一组拥有共同字段结构的类，如果这些类是通过 :ref:`declarative mixin <declarative_mixins>` 混入方式组成，  
    那么也可以通过 :func:`_orm.with_loader_criteria` 搭配 Python 的 lambda 表达式来实现筛选。  
    这个 lambda 表达式会在查询编译阶段、对每个匹配的实体类调用。

    假设我们有一个名为 `HasTimestamp` 的 mixin，用于为多个实体添加时间戳字段::

        import datetime

        class HasTimestamp:
            timestamp = mapped_column(DateTime, default=datetime.datetime.now)

        class SomeEntity(HasTimestamp, Base):
            __tablename__ = "some_entity"
            id = mapped_column(Integer, primary_key=True)

        class SomeOtherEntity(HasTimestamp, Base):
            __tablename__ = "some_entity"
            id = mapped_column(Integer, primary_key=True)

    上述两个类都具有 `timestamp` 字段，其默认值为当前时间。  
    我们可以通过事件钩子拦截所有继承自 `HasTimestamp` 的对象，并筛选出「最近一个月内」的数据::

        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if (
                orm_execute_state.is_select
                and not orm_execute_state.is_column_load
                and not orm_execute_state.is_relationship_load
            ):
                one_month_ago = datetime.datetime.today() - datetime.timedelta(days=30)

                orm_execute_state.statement = orm_execute_state.statement.options(
                    with_loader_criteria(
                        HasTimestamp,
                        lambda cls: cls.timestamp >= one_month_ago,
                        include_aliases=True,
                    )
                )

    .. warning::

        在调用 :func:`_orm.with_loader_criteria` 时使用的 lambda 表达式 **只会针对每个唯一的类调用一次**。  
        不应在 lambda 中调用带有副作用的自定义函数。  
        详见 :ref:`engine_lambda_caching`，这是一个高级特性。

    .. seealso::

        :ref:`examples_session_orm_events` - 包含关于 :func:`_orm.with_loader_criteria` 的完整可运行示例。

.. tab:: 英文

    One of the most requested query-extension features is the ability to add WHERE
    criteria to all occurrences of an entity in all queries.   This is achievable
    by making use of the :func:`_orm.with_loader_criteria` query option, which
    may be used on its own, or is ideally suited to be used within the
    :meth:`_orm.SessionEvents.do_orm_execute` event::

        from sqlalchemy.orm import with_loader_criteria

        Session = sessionmaker(engine)


        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if (
                orm_execute_state.is_select
                and not orm_execute_state.is_column_load
                and not orm_execute_state.is_relationship_load
            ):
                orm_execute_state.statement = orm_execute_state.statement.options(
                    with_loader_criteria(MyEntity.public == True)
                )

    Above, an option is added to all SELECT statements that will limit all queries
    against ``MyEntity`` to filter on ``public == True``.   The criteria
    will be applied to **all** loads of that class within the scope of the
    immediate query.    The :func:`_orm.with_loader_criteria` option by default
    will automatically propagate to relationship loaders as well, which will
    apply to subsequent relationship loads, which includes
    lazy loads, selectinloads, etc.

    For a series of classes that all feature some common column structure,
    if the classes are composed using a :ref:`declarative mixin <declarative_mixins>`,
    the mixin class itself may be used in conjunction with the :func:`_orm.with_loader_criteria`
    option by making use of a Python lambda.  The Python lambda will be invoked at
    query compilation time against the specific entities which match the criteria.
    Given a series of classes based on a mixin called ``HasTimestamp``::

        import datetime


        class HasTimestamp:
            timestamp = mapped_column(DateTime, default=datetime.datetime.now)


        class SomeEntity(HasTimestamp, Base):
            __tablename__ = "some_entity"
            id = mapped_column(Integer, primary_key=True)


        class SomeOtherEntity(HasTimestamp, Base):
            __tablename__ = "some_entity"
            id = mapped_column(Integer, primary_key=True)

    The above classes ``SomeEntity`` and ``SomeOtherEntity`` will each have a column
    ``timestamp`` that defaults to the current date and time.   An event may be used
    to intercept all objects that extend from ``HasTimestamp`` and filter their
    ``timestamp`` column on a date that is no older than one month ago::

        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if (
                orm_execute_state.is_select
                and not orm_execute_state.is_column_load
                and not orm_execute_state.is_relationship_load
            ):
                one_month_ago = datetime.datetime.today() - datetime.timedelta(months=1)

                orm_execute_state.statement = orm_execute_state.statement.options(
                    with_loader_criteria(
                        HasTimestamp,
                        lambda cls: cls.timestamp >= one_month_ago,
                        include_aliases=True,
                    )
                )

    .. warning:: 
        
        The use of a lambda inside of the call to :func:`_orm.with_loader_criteria` is only invoked **once per unique class**. Custom functions should not be invoked within this lambda.   See :ref:`engine_lambda_caching` for an overview of the "lambda SQL" feature, which is for advanced use only.

    .. seealso::

        :ref:`examples_session_orm_events` - includes working examples of the above :func:`_orm.with_loader_criteria` recipes.

.. _do_orm_execute_re_executing:

重新执行语句
^^^^^^^^^^^^^^^^^^^^^^^

Re-Executing Statements

.. tab:: 中文

    .. deepalchemy::

        SQL 语句的重新执行功能涉及到一个稍显复杂的递归过程，  
        其目的是解决「将 SQL 执行路由到其他非 SQL 上下文」这一相对困难的问题。  
        典型的应用包括「dogpile 缓存」和「水平分片（sharding）」，可参考下文提供的示例链接。

    :class:`_orm.ORMExecuteState` 可以控制语句的实际执行过程。  
    你可以选择 **跳过 SQL 执行**，转而返回缓存中的预构建结果，  
    也可以在执行时多次变更状态（如使用多个数据库连接执行相同语句），  
    并在内存中合并多个结果。这些高级用法在 SQLAlchemy 的示例代码中都有实现。

    在 :meth:`_orm.SessionEvents.do_orm_execute` 钩子内部，  
    可以调用 :meth:`_orm.ORMExecuteState.invoke_statement` 方法来执行一次新的、嵌套的  
    :meth:`_orm.Session.execute` 调用。这将 **终止当前语句的默认处理流程** ，直接返回  
    嵌套执行的结果 :class:`_engine.Result` 对象。

    这个嵌套调用会跳过当前钩子上所有已注册的处理器。

    :meth:`_orm.ORMExecuteState.invoke_statement` 会返回一个 :class:`_engine.Result` 对象。  
    该对象支持 **freeze** 成为可缓存格式，并可 **unfreeze** 为新 Result 对象，  
    或与其它 Result 对象合并。

    例如，使用该钩子实现一个缓存机制::

    from sqlalchemy.orm import loading

    cache = {}

    @event.listens_for(Session, "do_orm_execute")
    def _do_orm_execute(orm_execute_state):
        if "my_cache_key" in orm_execute_state.execution_options:
            cache_key = orm_execute_state.execution_options["my_cache_key"]

            if cache_key in cache:
                frozen_result = cache[cache_key]
            else:
                frozen_result = orm_execute_state.invoke_statement().freeze()
                cache[cache_key] = frozen_result

            return loading.merge_frozen_result(
                orm_execute_state.session,
                orm_execute_state.statement,
                frozen_result,
                load=False,
            )

    搭配以上钩子，使用缓存的调用示例如下::

    stmt = (
        select(User).where(User.name == "sandy").execution_options(my_cache_key="key_sandy")
    )

    result = session.execute(stmt)

    这里，通过 :meth:`_sql.Select.execution_options` 设置了一个名为 `"my_cache_key"` 的选项，  
    然后该选项会在钩子中被识别，并与缓存中的 :class:`_engine.FrozenResult` 进行匹配。

    - 若缓存命中，直接使用 `merge_frozen_result` 返回结果；
    - 若未命中，执行查询并将结果 `freeze` 后缓存。

    .. seealso::

        :ref:`examples_caching`

        :ref:`examples_sharding`

.. tab:: 英文

    .. deepalchemy:: 
        
        the statement re-execution feature involves a slightly intricate recursive sequence, and is intended to solve the fairly hard problem of being able to re-route the execution of a SQL statement into various non-SQL contexts.    The twin examples of "dogpile caching" and "horizontal sharding", linked below, should be used as a guide for when this rather advanced feature is appropriate to be used.

    The :class:`_orm.ORMExecuteState` is capable of controlling the execution of
    the given statement; this includes the ability to either not invoke the
    statement at all, allowing a pre-constructed result set retrieved from a cache to
    be returned instead, as well as the ability to invoke the same statement
    repeatedly with different state, such as invoking it against multiple database
    connections and then merging the results together in memory.   Both of these
    advanced patterns are demonstrated in SQLAlchemy's example suite as detailed
    below.

    When inside the :meth:`_orm.SessionEvents.do_orm_execute` event hook, the
    :meth:`_orm.ORMExecuteState.invoke_statement` method may be used to invoke
    the statement using a new nested invocation of :meth:`_orm.Session.execute`,
    which will then preempt the subsequent handling of the current execution
    in progress and instead return the :class:`_engine.Result` returned by the
    inner execution.   The event handlers thus far invoked for the
    :meth:`_orm.SessionEvents.do_orm_execute` hook within this process will
    be skipped within this nested call as well.

    The :meth:`_orm.ORMExecuteState.invoke_statement` method returns a
    :class:`_engine.Result` object; this object then features the ability for it to
    be "frozen" into a cacheable format and "unfrozen" into a new
    :class:`_engine.Result` object, as well as for its data to be merged with
    that of other :class:`_engine.Result` objects.

    E.g., using :meth:`_orm.SessionEvents.do_orm_execute` to implement a cache::

        from sqlalchemy.orm import loading

        cache = {}


        @event.listens_for(Session, "do_orm_execute")
        def _do_orm_execute(orm_execute_state):
            if "my_cache_key" in orm_execute_state.execution_options:
                cache_key = orm_execute_state.execution_options["my_cache_key"]

                if cache_key in cache:
                    frozen_result = cache[cache_key]
                else:
                    frozen_result = orm_execute_state.invoke_statement().freeze()
                    cache[cache_key] = frozen_result

                return loading.merge_frozen_result(
                    orm_execute_state.session,
                    orm_execute_state.statement,
                    frozen_result,
                    load=False,
                )

    With the above hook in place, an example of using the cache would look like::

        stmt = (
            select(User).where(User.name == "sandy").execution_options(my_cache_key="key_sandy")
        )

        result = session.execute(stmt)

    Above, a custom execution option is passed to
    :meth:`_sql.Select.execution_options` in order to establish a "cache key" that
    will then be intercepted by the :meth:`_orm.SessionEvents.do_orm_execute` hook.  This
    cache key is then matched to a :class:`_engine.FrozenResult` object that may be
    present in the cache, and if present, the object is re-used.  The recipe makes
    use of the :meth:`_engine.Result.freeze` method to "freeze" a
    :class:`_engine.Result` object, which above will contain ORM results, such that
    it can be stored in a cache and used multiple times. In order to return a live
    result from the "frozen" result, the :func:`_orm.loading.merge_frozen_result`
    function is used to merge the "frozen" data from the result object into the
    current session.

    The above example is implemented as a complete example in :ref:`examples_caching`.

    The :meth:`_orm.ORMExecuteState.invoke_statement` method may also be called
    multiple times, passing along different information to the
    :paramref:`_orm.ORMExecuteState.invoke_statement.bind_arguments` parameter such
    that the :class:`_orm.Session` will make use of different
    :class:`_engine.Engine` objects each time.  This will return a different
    :class:`_engine.Result` object each time; these results can be merged together
    using the :meth:`_engine.Result.merge` method.  This is the technique employed
    by the :ref:`horizontal_sharding_toplevel` extension; see the source code to
    familiarize.

    .. seealso::

        :ref:`examples_caching`

        :ref:`examples_sharding`




.. _session_persistence_events:

持久性事件
------------------

Persistence Events

.. tab:: 中文

    最常用的一类事件，可能就是与“持久化”相关的事件（persistence events），  
    它们对应于 :ref:`flush 流程 <session_flushing>`。

    所谓 flush，是指对所有挂起的对象变更做出处理决策，并最终以 INSERT、UPDATE 和 DELETE 的 SQL 语句形式发送到数据库。

.. tab:: 英文

    Probably the most widely used series of events are the "persistence" events,
    which correspond to the :ref:`flush process<session_flushing>`.
    The flush is where all the decisions are made about pending changes to
    objects and are then emitted out to the database in the form of INSERT,
    UPDATE, and DELETE statements.

``before_flush()``
^^^^^^^^^^^^^^^^^^

.. tab:: 中文

    在这些事件中，最通用、最有用的是 :meth:`.SessionEvents.before_flush` 钩子。  
    当你希望在 flush 过程中确保对数据库做出额外的持久化更改时，应当使用该钩子。

    :meth:`.SessionEvents.before_flush` 事件可以用来：

    - 对对象的状态进行验证；
    - 在对象被持久化之前，创建额外的对象或设置引用关系。

    在这个事件钩子中， **可以安全地操作 Session 的状态**，也就是说你可以：

    - 将新对象加入 Session；
    - 删除已有对象；
    - 修改对象的属性；

    这些更改都会在钩子执行完成后被自动纳入 flush 流程中。

    一个典型的 :meth:`.SessionEvents.before_flush` 钩子通常会遍历以下集合：

    - :attr:`.Session.new`（新加入的对象）  
    - :attr:`.Session.dirty`（已修改的对象）  
    - :attr:`.Session.deleted`（标记为删除的对象）

    通过扫描这些集合，可以识别出当前有哪些对象将被影响，从而对其进行操作。

    有关 :meth:`.SessionEvents.before_flush` 的使用示例，参见以下文档部分：

    - :ref:`examples_versioned_history`  
    - :ref:`examples_versioned_rows`

.. tab:: 英文

    The :meth:`.SessionEvents.before_flush` hook is by far the most generally
    useful event to use when an application wants to ensure that
    additional persistence changes to the database are made when a flush proceeds.
    Use :meth:`.SessionEvents.before_flush` in order to operate
    upon objects to validate their state as well as to compose additional objects
    and references before they are persisted.   Within this event,
    it is **safe to manipulate the Session's state**, that is, new objects
    can be attached to it, objects can be deleted, and individual attributes
    on objects can be changed freely, and these changes will be pulled into
    the flush process when the event hook completes.

    The typical :meth:`.SessionEvents.before_flush` hook will be tasked with
    scanning the collections :attr:`.Session.new`, :attr:`.Session.dirty` and
    :attr:`.Session.deleted` in order to look for objects
    where something will be happening.

    For illustrations of :meth:`.SessionEvents.before_flush`, see
    examples such as :ref:`examples_versioned_history` and
    :ref:`examples_versioned_rows`.

``after_flush()``
^^^^^^^^^^^^^^^^^

.. tab:: 中文

    :meth:`.SessionEvents.after_flush` 钩子在 flush 流程中 **SQL 语句已被发出之后，但对象状态尚未被修改之前** 被调用。  
    也就是说，在这个阶段你仍然可以访问：

    - :attr:`.Session.new`（新加入的对象）  
    - :attr:`.Session.dirty`（已修改的对象）  
    - :attr:`.Session.deleted`（已删除的对象）

    借此你可以查看刚刚被 flush 的对象。同时也可以结合 :class:`.AttributeState` 提供的变更历史追踪功能，判断哪些更改已被持久化。

    在 :meth:`.SessionEvents.after_flush` 钩子中，可以基于这些观察结果再额外向数据库发出 SQL 语句。

.. tab:: 英文

    The :meth:`.SessionEvents.after_flush` hook is called after the SQL has been emitted for a flush process, but **before** the state of the objects that were flushed has been altered.  That is, you can still inspect the :attr:`.Session.new`, :attr:`.Session.dirty` and :attr:`.Session.deleted` collections to see what was just flushed, and you can also use history tracking features like the ones provided by :class:`.AttributeState` to see what changes were just persisted. In the :meth:`.SessionEvents.after_flush` event, additional SQL can be emitted to the database based on what's observed to have changed.

``after_flush_postexec()``
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. tab:: 中文

    ---

    :meth:`.SessionEvents.after_flush_postexec` 钩子会在 :meth:`.SessionEvents.after_flush` 之后被调用，  
    **但此时对象的状态已经更新，以反映刚才 flush 的结果**。

    此时通常：

    - :attr:`.Session.new`  
    - :attr:`.Session.dirty`  
    - :attr:`.Session.deleted`  

    这三个集合都已经为空。

    在这个钩子中，可以检查 identity map 中的“最终对象状态”，也可以选择再向数据库发出额外 SQL。

    更重要的是，在这个钩子里也允许对对象进行新的更改。这会让 :class:`.Session` 再次变为“脏”状态（dirty）。  
    此时根据不同的上下文，SQLAlchemy 的处理方式如下：

    - 如果 flush 是在 :meth:`.Session.commit` 的上下文中被触发的：  
    
      如果你在这个钩子中做出了新的更改， :class:`.Session` 会自动 **再次** 执行 flush。
    
    - 如果当前并不是在 `commit()` 的上下文中：  
    
      那这些新的更改会被加入到下一次正常 flush 的处理流程中。

    > 🧠 另外，为了防止在钩子中不断添加新状态导致无限循环，SQLAlchemy 设定了一个最大迭代次数为 100 的限制。  
      
      如果在 `commit()` 期间这个钩子每次都导致新状态被加入并反复触发 flush，一旦达到 100 次，将强制中止循环。

.. tab:: 英文

    :meth:`.SessionEvents.after_flush_postexec` is called soon after :meth:`.SessionEvents.after_flush`, but is invoked **after** the state of the objects has been modified to account for the flush that just took place. The :attr:`.Session.new`, :attr:`.Session.dirty` and :attr:`.Session.deleted` collections are normally completely empty here. Use :meth:`.SessionEvents.after_flush_postexec` to inspect the identity map for finalized objects and possibly emit additional SQL.   In this hook, there is the ability to make new changes on objects, which means the :class:`.Session` will again go into a "dirty" state; the mechanics of the :class:`.Session` here will cause it to flush **again** if new changes are detected in this hook if the flush were invoked in the context of :meth:`.Session.commit`; otherwise, the pending changes will be bundled as part of the next normal flush.  When the hook detects new changes within a :meth:`.Session.commit`, a counter ensures that an endless loop in this regard is stopped after 100 iterations, in the case that an :meth:`.SessionEvents.after_flush_postexec` hook continually adds new state to be flushed each time it is called.

.. _session_persistence_mapper:

映射器级刷新事件
^^^^^^^^^^^^^^^^^^^^^^^^^

Mapper-level Flush Events

.. tab:: 中文

    除了 flush 级别的钩子之外，还有一组更细粒度的钩子，它们是按对象级别调用的，并根据 flush 过程中的 INSERT、UPDATE 或 DELETE 进行分类。这些被称为 *mapper 持久化钩子*，同样非常受欢迎。然而，这些事件需要更加谨慎地使用，因为它们在 flush 正在进行的上下文中执行；在此阶段进行许多操作是不安全的。

    这些事件包括：

    * :meth:`.MapperEvents.before_insert`
    * :meth:`.MapperEvents.after_insert`
    * :meth:`.MapperEvents.before_update`
    * :meth:`.MapperEvents.after_update`
    * :meth:`.MapperEvents.before_delete`
    * :meth:`.MapperEvents.after_delete`

    .. note::

        需要注意的是，这些事件 **仅适用于** :ref:`Session flush 操作 <session_flushing>`，而 **不适用于**
        :ref:`ORM 级别的 INSERT/UPDATE/DELETE 功能 <orm_expression_update_delete>`。要拦截 ORM 层的 DML 操作，
        请使用 :meth:`_orm.SessionEvents.do_orm_execute` 事件。

    每个事件都会传入：一个 :class:`_orm.Mapper`，被映射的对象本身，以及正在用于发出 INSERT、UPDATE 或 DELETE 语句的 :class:`_engine.Connection`。  
    这些事件的优势非常明显 —— 如果应用程序希望在特定类型的对象被 INSERT 时附加某些行为，该钩子提供了非常具体的切入点；  
    不同于 :meth:`.SessionEvents.before_flush` 事件，无需遍历 :attr:`.Session.new` 等集合去寻找目标对象。  

    但请注意，这些事件被调用时，flush 计划（即将要发出的所有 INSERT、UPDATE、DELETE 语句的完整列表） **已经确定**，  
    此时不允许再做任何变更。因此，在这些事件中唯一可以修改的，只能是对象当前行（row）中 **本地** 属性。  
    对该对象的其他属性或其他对象进行修改将影响 :class:`.Session` 的状态，并可能导致其无法正常工作。

    在这些 mapper 级持久化事件中 **不被支持的操作** 包括：

    * :meth:`.Session.add`
    * :meth:`.Session.delete`
    * 映射集合的 append、add、remove、delete、discard 等操作
    * 映射关系属性的赋值/删除事件，例如 ``someobject.related = someotherobject``

    传入 :class:`_engine.Connection` 的原因，是鼓励 **直接在这个连接对象上执行简单的 SQL 操作**，  
    比如增加计数器或向日志表插入额外的行。

    还有很多对象级别的操作根本不需要放在 flush 事件中处理。  
    最常见的替代方案是在对象的 ``__init__()`` 方法中直接设置额外的状态，比如创建一些附属于该新对象的其他对象。  
    使用 :ref:`simple_validators` 中描述的验证器机制也是一个替代方式；  
    这些函数可以拦截属性的更改，并据此为目标对象建立额外的状态更改。  

    通过这两种方式，都可以在对象进入 flush 步骤前就已经处于正确状态。


.. tab:: 英文

    In addition to the flush-level hooks, there is also a suite of hooks that are
    more fine-grained, in that they are called on a per-object basis and are broken
    out based on INSERT, UPDATE or DELETE within the flush process. These are the
    mapper persistence hooks, and they too are very popular, however these events
    need to be approached more cautiously, as they proceed within the context of
    the flush process that is already ongoing; many operations are not safe to
    proceed here.

    The events are:

    * :meth:`.MapperEvents.before_insert`
    * :meth:`.MapperEvents.after_insert`
    * :meth:`.MapperEvents.before_update`
    * :meth:`.MapperEvents.after_update`
    * :meth:`.MapperEvents.before_delete`
    * :meth:`.MapperEvents.after_delete`

    .. note::

        It is important to note that these events apply **only** to the
        :ref:`session flush operation <session_flushing>` , and **not** to the
        ORM-level INSERT/UPDATE/DELETE functionality described at
        :ref:`orm_expression_update_delete`. To intercept ORM-level DML, use the
        :meth:`_orm.SessionEvents.do_orm_execute` event.

    Each event is passed the :class:`_orm.Mapper`,
    the mapped object itself, and the :class:`_engine.Connection` which is being
    used to emit an INSERT, UPDATE or DELETE statement.     The appeal of these
    events is clear, in that if an application wants to tie some activity to
    when a specific type of object is persisted with an INSERT, the hook is
    very specific; unlike the :meth:`.SessionEvents.before_flush` event,
    there's no need to search through collections like :attr:`.Session.new`
    in order to find targets.  However, the flush plan which
    represents the full list of every single INSERT, UPDATE, DELETE statement
    to be emitted has *already been decided* when these events are called,
    and no changes may be made at this stage.  Therefore the only changes that are
    even possible to the given objects are upon attributes **local** to the
    object's row.   Any other change to the object or other objects will
    impact the state of the :class:`.Session`, which will fail to function
    properly.

    Operations that are not supported within these mapper-level persistence
    events include:

    * :meth:`.Session.add`
    * :meth:`.Session.delete`
    * Mapped collection append, add, remove, delete, discard, etc.
    * Mapped relationship attribute set/del events,
      i.e. ``someobject.related = someotherobject``

    The reason the :class:`_engine.Connection` is passed is that it is encouraged that
    **simple SQL operations take place here**, directly on the :class:`_engine.Connection`,
    such as incrementing counters or inserting extra rows within log tables.

    There are also many per-object operations that don't need to be handled
    within a flush event at all.   The most common alternative is to simply
    establish additional state along with an object inside its ``__init__()``
    method, such as creating additional objects that are to be associated with
    the new object.  Using validators as described in :ref:`simple_validators` is
    another approach; these functions can intercept changes to attributes and
    establish additional state changes on the target object in response to the
    attribute change.   With both of these approaches, the object is in
    the correct state before it ever gets to the flush step.

.. _session_lifecycle_events:

对象生命周期事件
-----------------------

Object Lifecycle Events

.. tab:: 中文

    另一个事件使用场景是 **追踪对象的生命周期** 。这指的是在 :ref:`session_object_states` 中介绍的那些状态。

    上述所有状态都可以通过事件完整追踪。每个事件都表示一个明确的状态转换，即起始状态和目标状态都是追踪的一部分。  
    除了初始的 transient（瞬态）事件外，所有事件都是基于 :class:`.Session` 对象或类的，  
    这意味着它们既可以与特定的 :class:`.Session` 实例绑定::

        from sqlalchemy import event
        from sqlalchemy.orm import Session

        session = Session()


        @event.listens_for(session, "transient_to_pending")
        def object_is_pending(session, obj):
            print("new pending: %s" % obj)

    也可以与 :class:`.Session` 类本身绑定，或者与某个特定的 :class:`.sessionmaker` 绑定，  
    这通常是最有用的方式::

        from sqlalchemy import event
        from sqlalchemy.orm import sessionmaker

        maker = sessionmaker()


        @event.listens_for(maker, "transient_to_pending")
        def object_is_pending(session, obj):
            print("new pending: %s" % obj)

    监听器当然也可以堆叠在一个函数上，这在实际使用中非常常见。  
    例如，要追踪所有进入 persistent（持久化）状态的对象::

            @event.listens_for(maker, "pending_to_persistent")
            @event.listens_for(maker, "deleted_to_persistent")
            @event.listens_for(maker, "detached_to_persistent")
            @event.listens_for(maker, "loaded_as_persistent")
            def detect_all_persistent(session, instance):
                print("object is now persistent: %s" % instance)


.. tab:: 英文

    Another use case for events is to track the lifecycle of objects.  This
    refers to the states first introduced at :ref:`session_object_states`.

    All the states above can be tracked fully with events.   Each event
    represents a distinct state transition, meaning, the starting state
    and the destination state are both part of what are tracked.   With the
    exception of the initial transient event, all the events are in terms of
    the :class:`.Session` object or class, meaning they can be associated either
    with a specific :class:`.Session` object::

        from sqlalchemy import event
        from sqlalchemy.orm import Session

        session = Session()


        @event.listens_for(session, "transient_to_pending")
        def object_is_pending(session, obj):
            print("new pending: %s" % obj)

    Or with the :class:`.Session` class itself, as well as with a specific
    :class:`.sessionmaker`, which is likely the most useful form::

        from sqlalchemy import event
        from sqlalchemy.orm import sessionmaker

        maker = sessionmaker()


        @event.listens_for(maker, "transient_to_pending")
        def object_is_pending(session, obj):
            print("new pending: %s" % obj)

    The listeners can of course be stacked on top of one function, as is
    likely to be common.   For example, to track all objects that are
    entering the persistent state::

            @event.listens_for(maker, "pending_to_persistent")
            @event.listens_for(maker, "deleted_to_persistent")
            @event.listens_for(maker, "detached_to_persistent")
            @event.listens_for(maker, "loaded_as_persistent")
            def detect_all_persistent(session, instance):
                print("object is now persistent: %s" % instance)

瞬态
^^^^^^^^^

Transient

.. tab:: 中文

    所有被映射的对象在首次构建时都会以 :term:`transient` 状态开始。  
    在此状态下，对象是独立存在的，并没有与任何 :class:`.Session` 关联。  
    对于这个初始状态，不存在特定的“转换”事件，因为还没有 :class:`.Session`；  
    不过如果你想拦截任意一个瞬态对象的创建，:meth:`.InstanceEvents.init` 事件可能是最合适的选择。  
    该事件是绑定在某个特定类或其超类上的。  
    例如，想要拦截特定声明式基类下的所有新建对象，可以这样做::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy import event


        class Base(DeclarativeBase):
            pass


        @event.listens_for(Base, "init", propagate=True)
        def intercept_init(instance, args, kwargs):
            print("new transient: %s" % instance)

.. tab:: 英文

    All mapped objects when first constructed start out as :term:`transient`.
    In this state, the object exists alone and doesn't have an association with
    any :class:`.Session`.   For this initial state, there's no specific
    "transition" event since there is no :class:`.Session`, however if one
    wanted to intercept when any transient object is created, the
    :meth:`.InstanceEvents.init` method is probably the best event.  This
    event is applied to a specific class or superclass.  For example, to
    intercept all new objects for a particular declarative base::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy import event


        class Base(DeclarativeBase):
            pass


        @event.listens_for(Base, "init", propagate=True)
        def intercept_init(instance, args, kwargs):
            print("new transient: %s" % instance)

瞬态到待处理
^^^^^^^^^^^^^^^^^^^^

Transient to Pending

.. tab:: 中文

    当瞬态对象首次通过 :meth:`.Session.add` 或 :meth:`.Session.add_all` 方法与 :class:`.Session` 关联时，它将变为 :term:`pending`（待持久化）状态。  
    对象也可能因为从一个显式添加的引用对象中发生 :ref:`“级联” <unitofwork_cascades>` 而成为 :class:`.Session` 的一部分。  
    这种从瞬态到待持久化的状态转换可以通过 :meth:`.SessionEvents.transient_to_pending` 事件检测到::

        @event.listens_for(sessionmaker, "transient_to_pending")
        def intercept_transient_to_pending(session, object_):
            print("transient to pending: %s" % object_)


.. tab:: 英文

    The transient object becomes :term:`pending` when it is first associated
    with a :class:`.Session` via the :meth:`.Session.add` or :meth:`.Session.add_all`
    method.  An object may also become part of a :class:`.Session` as a result
    of a :ref:`"cascade" <unitofwork_cascades>` from a referencing object that was
    explicitly added.   The transient to pending transition is detectable using
    the :meth:`.SessionEvents.transient_to_pending` event::

        @event.listens_for(sessionmaker, "transient_to_pending")
        def intercept_transient_to_pending(session, object_):
            print("transient to pending: %s" % object_)

待处理到持久
^^^^^^^^^^^^^^^^^^^^^

Pending to Persistent

.. tab:: 中文

    当执行 flush 操作，并对该实例执行 INSERT 语句时，:term:`pending` 对象将变为 :term:`persistent`（持久化）状态。  
    此时对象具有了 identity key（标识键）。  
    可以使用 :meth:`.SessionEvents.pending_to_persistent` 事件来追踪这个从待持久化到持久化的转换::

        @event.listens_for(sessionmaker, "pending_to_persistent")
        def intercept_pending_to_persistent(session, object_):
            print("pending to persistent: %s" % object_)

.. tab:: 英文

    The :term:`pending` object becomes :term:`persistent` when a flush
    proceeds and an INSERT statement takes place for the instance.  The object
    now has an identity key.   Track pending to persistent with the
    :meth:`.SessionEvents.pending_to_persistent` event::

        @event.listens_for(sessionmaker, "pending_to_persistent")
        def intercept_pending_to_persistent(session, object_):
            print("pending to persistent: %s" % object_)

待处理到瞬态
^^^^^^^^^^^^^^^^^^^^

Pending to Transient

.. tab:: 中文

    如果在待持久化对象被 flush 之前调用了 :meth:`.Session.rollback`，  
    或者在被 flush 之前使用了 :meth:`.Session.expunge` 将其移出会话，  
    :term:`pending` 对象就会回到 :term:`transient` 状态。  
    这种转换可以通过 :meth:`.SessionEvents.pending_to_transient` 事件进行追踪::

        @event.listens_for(sessionmaker, "pending_to_transient")
        def intercept_pending_to_transient(session, object_):
            print("transient to pending: %s" % object_)

.. tab:: 英文

    The :term:`pending` object can revert back to :term:`transient` if the
    :meth:`.Session.rollback` method is called before the pending object
    has been flushed, or if the :meth:`.Session.expunge` method is called
    for the object before it is flushed.  Track pending to transient with the
    :meth:`.SessionEvents.pending_to_transient` event::

        @event.listens_for(sessionmaker, "pending_to_transient")
        def intercept_pending_to_transient(session, object_):
            print("transient to pending: %s" % object_)

加载为持久
^^^^^^^^^^^^^^^^^^^^

Loaded as Persistent

.. tab:: 中文

    当对象从数据库加载时，它们可能直接处于 :term:`persistent` 状态。  
    追踪此状态转换等同于追踪对象的加载过程，也等同于使用实例级事件 :meth:`.InstanceEvents.load`。  
    不过，:meth:`.SessionEvents.loaded_as_persistent` 事件提供了一个以会话为中心的钩子，用来拦截通过此路径进入持久化状态的对象::

        @event.listens_for(sessionmaker, "loaded_as_persistent")
        def intercept_loaded_as_persistent(session, object_):
            print("object loaded into persistent state: %s" % object_)

.. tab:: 英文

    Objects can appear in the :class:`.Session` directly in the :term:`persistent`
    state when they are loaded from the database.   Tracking this state transition
    is synonymous with tracking objects as they are loaded, and is synonymous
    with using the :meth:`.InstanceEvents.load` instance-level event.  However, the
    :meth:`.SessionEvents.loaded_as_persistent` event is provided as a
    session-centric hook for intercepting objects as they enter the persistent
    state via this particular avenue::

        @event.listens_for(sessionmaker, "loaded_as_persistent")
        def intercept_loaded_as_persistent(session, object_):
            print("object loaded into persistent state: %s" % object_)

持久到瞬态
^^^^^^^^^^^^^^^^^^^^^^^

Persistent to Transient

.. tab:: 中文

    当 :meth:`.Session.rollback` 被用于一个最初通过 pending 状态添加对象的事务时，  
    持久化（:term:`persistent`）对象可以回到瞬态（:term:`transient`）状态。  
    在 ROLLBACK 的情况下，使该对象进入持久化状态的 INSERT 语句会被回滚，  
    对象也会从 :class:`.Session` 中驱逐，再次变为瞬态。  
    使用 :meth:`.SessionEvents.persistent_to_transient` 事件钩子来追踪从持久化状态回退为瞬态状态的对象::

        @event.listens_for(sessionmaker, "persistent_to_transient")
        def intercept_persistent_to_transient(session, object_):
            print("persistent to transient: %s" % object_)


.. tab:: 英文

    The persistent object can revert to the transient state if the
    :meth:`.Session.rollback` method is called for a transaction where the
    object was first added as pending.   In the case of the ROLLBACK, the
    INSERT statement that made this object persistent is rolled back, and
    the object is evicted from the :class:`.Session` to again become transient.
    Track objects that were reverted to transient from
    persistent using the :meth:`.SessionEvents.persistent_to_transient`
    event hook::

        @event.listens_for(sessionmaker, "persistent_to_transient")
        def intercept_persistent_to_transient(session, object_):
            print("persistent to transient: %s" % object_)

持久到已删除
^^^^^^^^^^^^^^^^^^^^^

Persistent to Deleted

.. tab:: 中文

    当对象在 flush 过程中从数据库中被删除时，  
    持久化（:term:`persistent`）对象会进入 :term:`deleted` 状态。  
    注意，这与调用 :meth:`.Session.delete` 删除目标对象是 **不一样的**。  
    :meth:`.Session.delete` 方法只是将对象 **标记为待删除**；  
    真正的 DELETE 语句直到 flush 执行时才会发出。  
    只有在 flush 之后，目标对象才会进入 "deleted" 状态。

    在 "deleted" 状态下，对象与 :class:`.Session` 的关联非常有限。  
    它不再存在于 identity map 中，也不再存在于表示待删除对象的  
    :attr:`.Session.deleted` 集合中。

    从 "deleted" 状态出发，对象在事务提交后可以变为 detached（:term:`detached`）状态，  
    或者在事务回滚时返回到 persistent 状态。

    通过 :meth:`.SessionEvents.persistent_to_deleted` 事件可以追踪从 persistent 到 deleted 的转换::

        @event.listens_for(sessionmaker, "persistent_to_deleted")
        def intercept_persistent_to_deleted(session, object_):
            print("object was DELETEd, is now in deleted state: %s" % object_)

.. tab:: 英文

    The persistent object enters the :term:`deleted` state when an object
    marked for deletion is deleted from the database within the flush
    process.   Note that this is **not the same** as when the :meth:`.Session.delete`
    method is called for a target object.   The :meth:`.Session.delete`
    method only **marks** the object for deletion; the actual DELETE statement
    is not emitted until the flush proceeds.  It is subsequent to the flush
    that the "deleted" state is present for the target object.

    Within the "deleted" state, the object is only marginally associated
    with the :class:`.Session`.  It is not present in the identity map
    nor is it present in the :attr:`.Session.deleted` collection that refers
    to when it was pending for deletion.

    From the "deleted" state, the object can go either to the detached state
    when the transaction is committed, or back to the persistent state
    if the transaction is instead rolled back.

    Track the persistent to deleted transition with
    :meth:`.SessionEvents.persistent_to_deleted`::

        @event.listens_for(sessionmaker, "persistent_to_deleted")
        def intercept_persistent_to_deleted(session, object_):
            print("object was DELETEd, is now in deleted state: %s" % object_)

已删除到分离
^^^^^^^^^^^^^^^^^^^

Deleted to Detached

.. tab:: 中文

    当会话的事务被提交后，处于 deleted 状态的对象会变为 :term:`detached` 状态。  
    在调用 :meth:`.Session.commit` 方法之后，数据库事务被最终提交，  
    :class:`.Session` 会彻底丢弃该已删除对象，并移除与它的所有关联。  
    使用 :meth:`.SessionEvents.deleted_to_detached` 事件追踪 deleted 到 detached 的转换::

        @event.listens_for(sessionmaker, "deleted_to_detached")
        def intercept_deleted_to_detached(session, object_):
            print("deleted to detached: %s" % object_)

    .. note::

        当对象处于 deleted 状态时，可以使用 ``inspect(object).deleted`` 来访问  
        :attr:`.InstanceState.deleted` 属性，该属性会返回 True。  
        但当对象处于 detached 状态时，:attr:`.InstanceState.deleted` 会再次返回 False。  
        若要检测对象是否曾被删除（无论它当前是否已 detached），可以使用  
        :attr:`.InstanceState.was_deleted` 属性。

.. tab:: 英文

    The deleted object becomes :term:`detached` when the session's transaction
    is committed.  After the :meth:`.Session.commit` method is called, the
    database transaction is final and the :class:`.Session` now fully discards
    the deleted object and removes all associations to it.   Track
    the deleted to detached transition using :meth:`.SessionEvents.deleted_to_detached`::

        @event.listens_for(sessionmaker, "deleted_to_detached")
        def intercept_deleted_to_detached(session, object_):
            print("deleted to detached: %s" % object_)

    .. note::

        While the object is in the deleted state, the :attr:`.InstanceState.deleted`
        attribute, accessible using ``inspect(object).deleted``, returns True.  However
        when the object is detached, :attr:`.InstanceState.deleted` will again
        return False.  To detect that an object was deleted, regardless of whether
        or not it is detached, use the :attr:`.InstanceState.was_deleted`
        accessor.


持久到分离
^^^^^^^^^^^^^^^^^^^^^^

Persistent to Detached

.. tab:: 中文

    当对象通过 :meth:`.Session.expunge`、:meth:`.Session.expunge_all` 或 :meth:`.Session.close` 方法  
    与 :class:`.Session` 解除关联时，持久化对象会变为 :term:`detached` 状态。

    .. note::

        如果对象所属的 :class:`.Session` 被应用程序取消引用并因垃圾回收而被丢弃，  
        对象也可能 **隐式地变为 detached 状态**。此情况下，**不会触发任何事件**。

    使用 :meth:`.SessionEvents.persistent_to_detached` 事件来追踪对象从 persistent 到 detached 的状态转换::

        @event.listens_for(sessionmaker, "persistent_to_detached")
        def intercept_persistent_to_detached(session, object_):
            print("object became detached: %s" % object_)


.. tab:: 英文

    The persistent object becomes :term:`detached` when the object is de-associated
    with the :class:`.Session`, via the :meth:`.Session.expunge`,
    :meth:`.Session.expunge_all`, or :meth:`.Session.close` methods.

    .. note::

        An object may also become **implicitly detached** if its owning
        :class:`.Session` is dereferenced by the application and discarded due to
        garbage collection. In this case, **no event is emitted**.

    Track objects as they move from persistent to detached using the
    :meth:`.SessionEvents.persistent_to_detached` event::

        @event.listens_for(sessionmaker, "persistent_to_detached")
        def intercept_persistent_to_detached(session, object_):
            print("object became detached: %s" % object_)

分离到持久
^^^^^^^^^^^^^^^^^^^^^^

Detached to Persistent

.. tab:: 中文

    当 detached 状态的对象重新通过 :meth:`.Session.add` 或等效方法  
    与某个 session 关联时，它会重新变为 persistent 状态。  
    使用 :meth:`.SessionEvents.detached_to_persistent` 事件来追踪从 detached 返回 persistent 的对象::

        @event.listens_for(sessionmaker, "detached_to_persistent")
        def intercept_detached_to_persistent(session, object_):
            print("object became persistent again: %s" % object_)

.. tab:: 英文

    The detached object becomes persistent when it is re-associated with a
    session using the :meth:`.Session.add` or equivalent method.  Track
    objects moving back to persistent from detached using the
    :meth:`.SessionEvents.detached_to_persistent` event::

        @event.listens_for(sessionmaker, "detached_to_persistent")
        def intercept_detached_to_persistent(session, object_):
            print("object became persistent again: %s" % object_)

已删除到持久
^^^^^^^^^^^^^^^^^^^^^

Deleted to Persistent

.. tab:: 中文

    当对象在某个事务中被 DELETE 后，如果该事务被 :meth:`.Session.rollback` 回滚，  
    则处于 :term:`deleted` 状态的对象可以恢复为 :term:`persistent` 状态。  
    使用 :meth:`.SessionEvents.deleted_to_persistent` 事件来追踪 deleted 状态对象恢复为 persistent 状态::

        @event.listens_for(sessionmaker, "deleted_to_persistent")
        def intercept_deleted_to_persistent(session, object_):
            print("deleted to persistent: %s" % object_)

.. tab:: 英文

    The :term:`deleted` object can be reverted to the :term:`persistent`
    state when the transaction in which it was DELETEd was rolled back
    using the :meth:`.Session.rollback` method.   Track deleted objects
    moving back to the persistent state using the
    :meth:`.SessionEvents.deleted_to_persistent` event::

        @event.listens_for(sessionmaker, "deleted_to_persistent")
        def intercept_deleted_to_persistent(session, object_):
            print("deleted to persistent: %s" % object_)

.. _session_transaction_events:

事务事件
------------------

Transaction Events

.. tab:: 中文

    事务事件允许应用程序在 :class:`.Session` 层面发生事务边界时，以及
    :class:`.Session` 在 :class:`_engine.Connection` 对象上改变事务状态时被通知。
    
    * :meth:`.SessionEvents.after_transaction_create`,
      :meth:`.SessionEvents.after_transaction_end` —— 这些事件用于追踪
      :class:`.Session` 的逻辑事务作用域，其行为不依赖于具体的数据库连接。
      这些事件的设计旨在帮助集成事务追踪系统，例如 ``zope.sqlalchemy``。
      当应用程序需要将某些外部作用域与 :class:`.Session` 的事务作用域对齐时，可以使用这些事件。
      这些钩子会反映 :class:`.Session` 的“嵌套”事务行为，也就是说它们会追踪逻辑上的“子事务”
      以及数据库中的“嵌套”事务（如 SAVEPOINT）。
    
    * :meth:`.SessionEvents.before_commit`, :meth:`.SessionEvents.after_commit`,
      :meth:`.SessionEvents.after_begin`,
      :meth:`.SessionEvents.after_rollback`, :meth:`.SessionEvents.after_soft_rollback` ——  
      这些事件允许从数据库连接的角度追踪事务事件。
      特别是 :meth:`.SessionEvents.after_begin` 是一个 **按连接触发的事件**；
      如果一个 :class:`.Session` 维护了多个连接，那么当这些连接在当前事务中被使用时，
      每个连接都会分别触发该事件。
      回滚和提交事件指的是 DBAPI 连接本身直接接收到回滚或提交指令的时刻。

.. tab:: 英文

    Transaction events allow an application to be notified when transaction
    boundaries occur at the :class:`.Session` level as well as when the
    :class:`.Session` changes the transactional state on :class:`_engine.Connection`
    objects.
    
    * :meth:`.SessionEvents.after_transaction_create`,
      :meth:`.SessionEvents.after_transaction_end` - these events track the
      logical transaction scopes of the :class:`.Session` in a way that is
      not specific to individual database connections.  These events are
      intended to help with integration of transaction-tracking systems such as
      ``zope.sqlalchemy``.  Use these
      events when the application needs to align some external scope with the
      transactional scope of the :class:`.Session`.  These hooks mirror
      the "nested" transactional behavior of the :class:`.Session`, in that they
      track logical "subtransactions" as well as "nested" (e.g. SAVEPOINT)
      transactions.
    
    * :meth:`.SessionEvents.before_commit`, :meth:`.SessionEvents.after_commit`,
      :meth:`.SessionEvents.after_begin`,
      :meth:`.SessionEvents.after_rollback`, :meth:`.SessionEvents.after_soft_rollback` -
      These events allow tracking of transaction events from the perspective
      of database connections.   :meth:`.SessionEvents.after_begin` in particular
      is a per-connection event; a :class:`.Session` that maintains more than
      one connection will emit this event for each connection individually
      as those connections become used within the current transaction.
      The rollback and commit events then refer to when the DBAPI connections
      themselves have received rollback or commit instructions directly.

属性更改事件
-----------------------

Attribute Change Events

.. tab:: 中文

    属性变更事件允许在对象的特定属性被修改时进行拦截。
    这些事件包括 :meth:`.AttributeEvents.set`、:meth:`.AttributeEvents.append` 和
    :meth:`.AttributeEvents.remove`。这些事件非常有用，特别适合用于对单个对象进行验证操作；
    不过，在大多数场景中使用“验证器”钩子（validator hook）会更加方便，
    这些钩子在底层其实就是使用这些属性事件实现的；参见 :ref:`simple_validators`
    了解背景信息。这些属性事件同样也是 backreference（反向引用）机制的实现基础。
    关于属性事件的使用示例，参见 :ref:`examples_instrumentation`。


.. tab:: 英文

    The attribute change events allow interception of when specific attributes
    on an object are modified.  These events include :meth:`.AttributeEvents.set`,
    :meth:`.AttributeEvents.append`, and :meth:`.AttributeEvents.remove`.  These
    events are extremely useful, particularly for per-object validation operations;
    however, it is often much more convenient to use a "validator" hook, which
    uses these hooks behind the scenes; see :ref:`simple_validators` for
    background on this.  The attribute events are also behind the mechanics
    of backreferences.   An example illustrating use of attribute events
    is in :ref:`examples_instrumentation`.




