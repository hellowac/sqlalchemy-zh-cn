.. _baked_toplevel:

烘焙查询
=============

Baked Queries

.. module:: sqlalchemy.ext.baked

.. tab:: 中文

    ``baked`` 提供了一种替代的创建模式，用于 :class:`~.query.Query` 对象，允许缓存对象的构建和字符串编译步骤。这意味着对于一个特定的 :class:`~.query.Query` 构建场景，如果使用多次，从初始构建到生成 SQL 字符串的所有 Python 函数调用只会发生 **一次** ，而不是每次构建和执行该查询时。

    该系统的基本原理是大大减少在 **发出 SQL 之前** 发生的所有操作的 Python 解释器开销。“baked”系统的缓存 **不会** 以任何方式减少 SQL 调用或缓存从数据库返回的 **结果** 。演示 SQL 调用和结果集本身缓存的技术可以在 :ref:`examples_caching` 中找到。

    .. deprecated:: 1.4  
        
        SQLAlchemy 1.4 和 2.0 引入了全新的直接查询缓存系统，消除了对 :class:`.BakedQuery` 系统的需求。缓存现在对所有 Core 和 ORM 查询透明激活，用户无需采取任何操作，使用的系统描述在 :ref:`sql_caching`。

    .. deepalchemy::

        :mod:`sqlalchemy.ext.baked` 扩展 **不适合初学者** 。正确使用它需要对 SQLAlchemy、数据库驱动程序和后端数据库如何相互作用有很好的高级别理解。此扩展提供了一种非常特定的优化，通常不需要。如上所述，它 **不缓存查询**，仅缓存 SQL 本身的字符串公式。

.. tab:: 英文

    ``baked`` provides an alternative creational pattern for
    :class:`~.query.Query` objects, which allows for caching of the object's
    construction and string-compilation steps.  This means that for a
    particular :class:`~.query.Query` building scenario that is used more than
    once, all of the Python function invocation involved in building the query
    from its initial construction up through generating a SQL string will only
    occur **once**, rather than for each time that query is built up and executed.

    The rationale for this system is to greatly reduce Python interpreter
    overhead for everything that occurs **before the SQL is emitted**.
    The caching of the "baked" system does **not** in any way reduce SQL calls or
    cache the **return results** from the database.  A technique that demonstrates
    the caching of the SQL calls and result sets themselves is available in
    :ref:`examples_caching`.

    .. deprecated:: 1.4  

        SQLAlchemy 1.4 and 2.0 feature an all-new direct query
        caching system that removes the need for the :class:`.BakedQuery` system.
        Caching is now transparently active for all Core and ORM queries with no
        action taken by the user, using the system described at :ref:`sql_caching`.


    .. deepalchemy::

        The :mod:`sqlalchemy.ext.baked` extension is **not for beginners**.  Using
        it correctly requires a good high level understanding of how SQLAlchemy, the
        database driver, and the backend database interact with each other.  This
        extension presents a very specific kind of optimization that is not ordinarily
        needed.  As noted above, it **does not cache queries**, only the string
        formulation of the SQL itself.

概要
--------

Synopsis

.. tab:: 中文

    使用 baked 系统的过程从创建一个所谓的“bakery”开始，
    它表示特定查询对象系列的存储::
    
        from sqlalchemy.ext import baked
    
        bakery = baked.bakery()
    
    上面的“bakery”将数据缓存存储在一个 LRU 缓存中，默认最多保存 200 个元素，
    需要注意的是，一个 ORM 查询通常会包含一个用于表示所调用的 ORM 查询的条目，
    以及一个针对每个数据库方言的 SQL 字符串条目。
    
    bakery 允许我们通过指定一系列 Python 可调用对象来构建一个 :class:`~.query.Query` 对象，
    这些对象通常是 lambda 表达式。为了简便使用，它重载了 ``+=`` 运算符，
    使得典型的查询构建过程看起来像下面这样::
    
        from sqlalchemy import bindparam
    
    
        def search_for_user(session, username, email=None):
            baked_query = bakery(lambda session: session.query(User))
            baked_query += lambda q: q.filter(User.name == bindparam("username"))
    
            baked_query += lambda q: q.order_by(User.id)
    
            if email:
                baked_query += lambda q: q.filter(User.email == bindparam("email"))
    
            result = baked_query(session).params(username=username, email=email).all()
    
            return result
    
    以下是关于上述代码的一些观察：
    
    1. ``baked_query`` 对象是 :class:`.BakedQuery` 的一个实例。这个
       对象本质上是一个用于构建实际 ORM :class:`~.query.Query` 对象的“构建器”，
       但它本身并不是 *实际的* :class:`~.query.Query` 对象。
    
    2. 直到函数的最后，在调用 :meth:`_baked.Result.all` 时，
       实际的 :class:`~.query.Query` 对象才会被构建。
    
    3. 添加到 ``baked_query`` 对象中的步骤都以 Python 函数（通常是 lambda 表达式）表示。
       给 :func:`.bakery` 函数传递的第一个 lambda 接受一个 :class:`.Session` 作为参数。
       其余的 lambda 每个都接受一个 :class:`~.query.Query` 作为参数。
    
    4. 在上面的代码中，尽管我们的应用程序可能多次调用
       ``search_for_user()``，并且每次调用时都会构建一个全新的 :class:`.BakedQuery` 对象，
       *所有的 lambda 表达式仅会被调用一次*。每个 lambda **永远不会** 在该查询缓存于 bakery 时被第二次调用。
    
    5. 缓存是通过存储对 **lambda 对象本身** 的引用来实现的，
       以便构造缓存键；也就是说，Python 解释器为这些函数分配一个 Python 内部标识符，
       这决定了如何在后续执行中识别查询。对于那些调用 ``search_for_user()``
       时指定了 ``email`` 参数的情况，
       可调用的 ``lambda q: q.filter(User.email == bindparam('email'))``
       将成为缓存键的一部分；当 ``email`` 为 ``None`` 时，
       这个可调用对象不在缓存键中。
    
    6. 由于 lambda 表达式仅被调用一次，因此必须确保不在 lambda 内部引用
       可能在多次调用中变化的变量；相反，假设这些是要绑定到 SQL 字符串中的值，
       我们使用 :func:`.bindparam` 构造命名参数，之后使用 :meth:`_baked.Result.params` 应用它们的实际值。

.. tab:: 英文

    Usage of the baked system starts by producing a so-called "bakery", which
    represents storage for a particular series of query objects::
    
        from sqlalchemy.ext import baked
    
        bakery = baked.bakery()
    
    The above "bakery" will store cached data in an LRU cache that defaults
    to 200 elements, noting that an ORM query will typically contain one entry
    for the ORM query as invoked, as well as one entry per database dialect for
    the SQL string.
    
    The bakery allows us to build up a :class:`~.query.Query` object by specifying
    its construction as a series of Python callables, which are typically lambdas.
    For succinct usage, it overrides the ``+=`` operator so that a typical
    query build-up looks like the following::
    
        from sqlalchemy import bindparam
    
    
        def search_for_user(session, username, email=None):
            baked_query = bakery(lambda session: session.query(User))
            baked_query += lambda q: q.filter(User.name == bindparam("username"))
    
            baked_query += lambda q: q.order_by(User.id)
    
            if email:
                baked_query += lambda q: q.filter(User.email == bindparam("email"))
    
            result = baked_query(session).params(username=username, email=email).all()
    
            return result
    
    Following are some observations about the above code:
    
    1. The ``baked_query`` object is an instance of :class:`.BakedQuery`.  This
       object is essentially the "builder" for a real orm :class:`~.query.Query`
       object, but it is not itself the *actual* :class:`~.query.Query`
       object.
    
    2. The actual :class:`~.query.Query` object is not built at all, until the
       very end of the function when :meth:`_baked.Result.all` is called.
    
    3. The steps that are added to the ``baked_query`` object are all expressed
       as Python functions,  typically lambdas.  The first lambda given
       to the :func:`.bakery` function receives a :class:`.Session` as its
       argument.  The remaining lambdas each receive a :class:`~.query.Query`
       as their argument.
    
    4. In the above code, even though our application may call upon
       ``search_for_user()`` many times, and even though within each invocation
       we build up an entirely new :class:`.BakedQuery` object,
       *all of the lambdas are only called once*.   Each lambda is **never** called
       a second time for as long as this query is cached in the bakery.
    
    5. The caching is achieved by storing references to the **lambda objects
       themselves** in order to formulate a cache key; that is, the fact that the
       Python interpreter assigns an in-Python identity to these functions is
       what determines how to identify the query on successive runs. For
       those invocations of ``search_for_user()`` where the ``email`` parameter
       is specified, the callable ``lambda q: q.filter(User.email == bindparam('email'))``
       will be part of the cache key that's retrieved; when ``email`` is
       ``None``, this callable is not part of the cache key.
    
    6. Because the lambdas are all called only once, it is essential that no
       variables which may change across calls are referenced **within** the
       lambdas; instead, assuming these are values to be bound into the
       SQL string, we use :func:`.bindparam` to construct named parameters,
       where we apply their actual values later using :meth:`_baked.Result.params`.


性能
-----------

Performance

.. tab:: 中文

    baked 查询可能看起来有些奇怪、笨拙并且冗长。然而，
    对于一个在应用程序中多次调用的查询，Python 性能的节省是非常显著的。
    在 :ref:`examples_performance` 中演示的 ``short_selects`` 示例套件
    对比了每个仅返回一行的查询，例如以下常规查询::
    
        session = Session(bind=engine)
        for id_ in random.sample(ids, n):
            session.query(Customer).filter(Customer.id == id_).one()
    
    与等效的“baked”查询::
    
        bakery = baked.bakery()
        s = Session(bind=engine)
        for id_ in random.sample(ids, n):
            q = bakery(lambda s: s.query(Customer))
            q += lambda q: q.filter(Customer.id == bindparam("id"))
            q(s).params(id=id_).one()
    
    对于每个代码块迭代 10000 次的 Python 函数调用计数差异如下：
    
    .. sourcecode:: text
    
        test_baked_query : 测试一个完整实体的 baked 查询。
                           （10000 次迭代）；总函数调用 1951294
    
        test_orm_query :   测试一个完整实体的常规 ORM 查询。
                           （10000 次迭代）；总函数调用 7900535
    
    在一台强大的笔记本电脑上的时间（以秒为单位）如下：
    
    .. sourcecode:: text
    
        test_baked_query : 测试一个完整实体的 baked 查询。
                           （10000 次迭代）；总时间 2.174126 秒
    
        test_orm_query :   测试一个完整实体的常规 ORM 查询。
                           （10000 次迭代）；总时间 7.958516 秒
    
    请注意，这个测试故意使用了仅返回一行的查询。
    对于返回多行的查询，baked 查询的性能优势将随着获取行的时间比例减少而减少。
    必须牢记的是， **baked 查询功能仅适用于构建查询本身，而不适用于获取结果**。
    使用 baked 特性并不意味着应用程序会大幅加速；
    它仅对于那些已经通过测量发现受此特定开销影响的应用程序有潜在的帮助。
    
    .. topic:: Measure twice, cut once
    
        关于如何分析 SQLAlchemy 应用程序的背景，请参见
        :ref:`faq_performance` 部分。在尝试提高应用程序性能时，
        使用性能测量技术至关重要。


.. tab:: 英文

    The baked query probably looks a little odd, a little bit awkward and
    a little bit verbose.   However, the savings in
    Python performance for a query which is invoked lots of times in an
    application are very dramatic.   The example suite ``short_selects``
    demonstrated in :ref:`examples_performance` illustrates a comparison
    of queries which each return only one row, such as the following regular
    query::
    
        session = Session(bind=engine)
        for id_ in random.sample(ids, n):
            session.query(Customer).filter(Customer.id == id_).one()
    
    compared to the equivalent "baked" query::
    
        bakery = baked.bakery()
        s = Session(bind=engine)
        for id_ in random.sample(ids, n):
            q = bakery(lambda s: s.query(Customer))
            q += lambda q: q.filter(Customer.id == bindparam("id"))
            q(s).params(id=id_).one()
    
    The difference in Python function call count for an iteration of 10000
    calls to each block are:
    
    .. sourcecode:: text
    
        test_baked_query : test a baked query of the full entity.
                           (10000 iterations); total fn calls 1951294
    
        test_orm_query :   test a straight ORM query of the full entity.
                           (10000 iterations); total fn calls 7900535
    
    In terms of number of seconds on a powerful laptop, this comes out as:
    
    .. sourcecode:: text
    
        test_baked_query : test a baked query of the full entity.
                           (10000 iterations); total time 2.174126 sec
    
        test_orm_query :   test a straight ORM query of the full entity.
                           (10000 iterations); total time 7.958516 sec
    
    Note that this test very intentionally features queries that only return one row.
    For queries that return many rows, the performance advantage of the baked query will have
    less and less of an impact, proportional to the time spent fetching rows.
    It is critical to keep in mind that the **baked query feature only applies to
    building the query itself, not the fetching of results**.  Using the
    baked feature is by no means a guarantee to a much faster application; it is
    only a potentially useful feature for those applications that have been measured
    as being impacted by this particular form of overhead.
    
    .. topic:: Measure twice, cut once
    
        For background on how to profile a SQLAlchemy application, please see
        the section :ref:`faq_performance`.  It is essential that performance
        measurement techniques are used when attempting to improve the performance
        of an application.

原理
---------

Rationale

.. tab:: 中文

    上面的“lambda”方法是一个超集，它扩展了更传统的“参数化”方法。
    假设我们想要构建一个简单的系统，在该系统中，我们只构建一次 :class:`~.query.Query`，
    然后将其存储在字典中以便重用。通过这种方法，我们现在可以直接构建查询，
    并通过调用 ``my_cached_query = query.with_session(None)`` 来移除其 :class:`.Session`::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument):
            if "my_key" not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                my_simple_cache["my_key"] = query.with_session(None)
            else:
                query = my_simple_cache["my_key"].with_session(session)
    
            return query.params(id=id_argument).all()
    
    上述方法给我们带来了非常有限的性能提升。
    通过重用 :class:`~.query.Query`，我们节省了 ``session.query(Model)`` 构造器中的 Python 计算量，
    以及调用 ``filter(Model.id == bindparam('id'))``，这将帮助我们跳过 Core 表达式的构建步骤，并将其传递给 :meth:`_query.Query.filter`。
    然而，这种方法仍然会在每次调用 :meth:`_query.Query.all` 时重新生成完整的 :class:`_expression.Select` 对象，
    并且每次这个新的 :class:`_expression.Select` 都会被传送到字符串编译步骤，
    对于像上面这种简单的情况，这大概占了 70% 的开销。
    
    为了减少额外的开销，我们需要一些更专门的逻辑，
    一种记住选择对象构建和 SQL 构建的方式。在 wiki 上的 `BakedQuery <https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/BakedQuery>`_ 部分有一个相关示例，
    它是此功能的前身，但在那个系统中，我们并没有缓存查询的 *构建* 过程。
    为了消除所有开销，我们需要同时缓存查询的构建和 SQL 的编译。
    假设我们将该示例按以下方式改编，并为自己创建一个方法 ``.bake()``，
    该方法预先编译查询的 SQL，生成一个可以以最小开销调用的新对象。
    我们的示例如下::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument):
            if "my_key" not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                my_simple_cache["my_key"] = query.with_session(None).bake()
            else:
                query = my_simple_cache["my_key"].with_session(session)
    
            return query.params(id=id_argument).all()
    
    在上面，我们已经解决了性能问题，但我们仍然需要处理这个字符串缓存键。
    
    我们可以使用“bakery”方法将上述内容重新框架化，
    使其看起来不那么特殊，并且更像是对简单的“重用查询”方法的改进::
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument):
            def create_model_query(session):
                return session.query(Model).filter(Model.id == bindparam("id"))
    
            parameterized_query = bakery.bake(create_model_query)
            return parameterized_query(session).params(id=id_argument).all()
    
    在上面，我们以与简单的“缓存查询”方法非常相似的方式使用了“baked”系统。
    然而，它减少了两行代码，不需要制造“my_key”这样的缓存键，
    并且还包含了与我们自定义的“bake”函数相同的功能，
    该功能缓存了从查询构造器到 filter 调用，再到 :class:`_expression.Select` 对象的生成，
    再到字符串编译步骤的所有 Python 调用工作。
    
    从上述内容，如果我们问自己，“如果 lookup 需要根据查询结构的不同条件做出决策怎么办？”这时，
    希望能清楚地看出为什么“baked”是目前的方式。
    与通过一个函数构建的参数化查询（这是我们最初认为 baked 会采用的方式）不同，
    我们可以通过 *任意数量* 的函数来构建它。
    考虑我们的简单示例，如果我们需要根据条件在查询中添加一个附加子句::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            if include_frobnizzle:
                cache_key = "my_key_with_frobnizzle"
            else:
                cache_key = "my_key_without_frobnizzle"
    
            if cache_key not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                if include_frobnizzle:
                    query = query.filter(Model.frobnizzle == True)
    
                my_simple_cache[cache_key] = query.with_session(None).bake()
            else:
                query = my_simple_cache[cache_key].with_session(session)
    
            return query.params(id=id_argument).all()
    
    我们的“简单”参数化系统现在必须负责生成缓存键，
    考虑到是否传递了“include_frobnizzle”标志，因为这个标志的存在意味着生成的 SQL 会完全不同。
    应该可以看出，随着查询构建的复杂性增加，缓存这些查询的任务将很快变得繁琐。
    我们可以将上述示例直接转换为使用“bakery”的方式，如下所示::
    
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            def create_model_query(session):
                return session.query(Model).filter(Model.id == bindparam("id"))
    
            parameterized_query = bakery.bake(create_model_query)
    
            if include_frobnizzle:
    
                def include_frobnizzle_in_query(query):
                    return query.filter(Model.frobnizzle == True)
    
                parameterized_query = parameterized_query.with_criteria(
                    include_frobnizzle_in_query
                )
    
            return parameterized_query(session).params(id=id_argument).all()
    
    在上面，我们不仅缓存了查询对象，还缓存了它生成 SQL 所需的所有工作。
    我们也不再需要处理确保生成一个准确考虑了我们所有结构修改的缓存键的问题；
    这一切现在都被自动处理了，并且没有出错的机会。
    
    这个代码示例比简单的示例少了几行代码，消除了处理缓存键的需求，
    并且具有完整的“baked”功能所带来的巨大性能提升。
    但是，它仍然有些冗长！因此，我们将 :meth:`.BakedQuery.add_criteria` 和
    :meth:`.BakedQuery.with_criteria` 方法简化为运算符，
    并鼓励（但绝对不强制！）使用简单的 lambda 表达式，作为减少冗长的一种方式::
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            parameterized_query = bakery.bake(
                lambda s: s.query(Model).filter(Model.id == bindparam("id"))
            )
    
            if include_frobnizzle:
                parameterized_query += lambda q: q.filter(Model.frobnizzle == True)
    
            return parameterized_query(session).params(id=id_argument).all()
    
    在上面，这种方法的实现更加简单，并且代码流更接近于非缓存查询函数的样子，
    因此使得代码更容易移植。
    
    上述描述基本上是从“正常”方法出发，
    解决缓存键构建和管理、移除所有冗余 Python 执行、
    以及构建带有条件的查询时所遇到的额外问题的总结，
    最终导致了目前的“baked”方法。

.. tab:: 英文

    The "lambda" approach above is a superset of what would be a more
    traditional "parameterized" approach.   Suppose we wished to build
    a simple system where we build a :class:`~.query.Query` just once, then
    store it in a dictionary for re-use.   This is possible right now by
    just building up the query, and removing its :class:`.Session` by calling
    ``my_cached_query = query.with_session(None)``::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument):
            if "my_key" not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                my_simple_cache["my_key"] = query.with_session(None)
            else:
                query = my_simple_cache["my_key"].with_session(session)
    
            return query.params(id=id_argument).all()
    
    The above approach gets us a very minimal performance benefit.
    By re-using a :class:`~.query.Query`, we save on the Python work within
    the ``session.query(Model)`` constructor as well as calling upon
    ``filter(Model.id == bindparam('id'))``, which will skip for us the building
    up of the Core expression as well as sending it to :meth:`_query.Query.filter`.
    However, the approach still regenerates the full :class:`_expression.Select`
    object every time when :meth:`_query.Query.all` is called and additionally this
    brand new :class:`_expression.Select` is sent off to the string compilation step every
    time, which for a simple case like the above is probably about 70% of the
    overhead.
    
    To reduce the additional overhead, we need some more specialized logic,
    some way to memoize the construction of the select object and the
    construction of the SQL.  There is an example of this on the wiki
    in the section `BakedQuery <https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/BakedQuery>`_,
    a precursor to this feature, however in that system, we aren't caching
    the *construction* of the query.  In order to remove all the overhead,
    we need to cache both the construction of the query as well as the SQL
    compilation.  Let's assume we adapted the recipe in this way
    and made ourselves a method ``.bake()`` that pre-compiles the SQL for the
    query, producing a new object that can be invoked with minimal overhead.
    Our example becomes::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument):
            if "my_key" not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                my_simple_cache["my_key"] = query.with_session(None).bake()
            else:
                query = my_simple_cache["my_key"].with_session(session)
    
            return query.params(id=id_argument).all()
    
    Above, we've fixed the performance situation, but we still have this
    string cache key to deal with.
    
    We can use the "bakery" approach to re-frame the above in a way that
    looks less unusual than the "building up lambdas" approach, and more like
    a simple improvement upon the simple "reuse a query" approach::
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument):
            def create_model_query(session):
                return session.query(Model).filter(Model.id == bindparam("id"))
    
            parameterized_query = bakery.bake(create_model_query)
            return parameterized_query(session).params(id=id_argument).all()
    
    Above, we use the "baked" system in a manner that is
    very similar to the simplistic "cache a query" system.  However, it
    uses two fewer lines of code, does not need to manufacture a cache key of
    "my_key", and also includes the same feature as our custom "bake" function
    that caches 100% of the Python invocation work from the
    constructor of the query, to the filter call, to the production
    of the :class:`_expression.Select` object, to the string compilation step.
    
    From the above, if we ask ourselves, "what if lookup needs to make conditional decisions
    as to the structure of the query?", this is where hopefully it becomes apparent
    why "baked" is the way it is.   Instead of a parameterized query building
    off from exactly one function (which is how we thought baked might work
    originally), we can build it from *any number* of functions.  Consider
    our naive example, if we needed to have an additional clause in our
    query on a conditional basis::
    
        my_simple_cache = {}
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            if include_frobnizzle:
                cache_key = "my_key_with_frobnizzle"
            else:
                cache_key = "my_key_without_frobnizzle"
    
            if cache_key not in my_simple_cache:
                query = session.query(Model).filter(Model.id == bindparam("id"))
                if include_frobnizzle:
                    query = query.filter(Model.frobnizzle == True)
    
                my_simple_cache[cache_key] = query.with_session(None).bake()
            else:
                query = my_simple_cache[cache_key].with_session(session)
    
            return query.params(id=id_argument).all()
    
    Our "simple" parameterized system must now be tasked with generating
    cache keys which take into account whether or not the "include_frobnizzle"
    flag was passed, as the presence of this flag means that the generated
    SQL would be entirely different.   It should be apparent that as the
    complexity of query building goes up, the task of caching these queries
    becomes burdensome very quickly.   We can convert the above example
    into a direct use of "bakery" as follows::
    
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            def create_model_query(session):
                return session.query(Model).filter(Model.id == bindparam("id"))
    
            parameterized_query = bakery.bake(create_model_query)
    
            if include_frobnizzle:
    
                def include_frobnizzle_in_query(query):
                    return query.filter(Model.frobnizzle == True)
    
                parameterized_query = parameterized_query.with_criteria(
                    include_frobnizzle_in_query
                )
    
            return parameterized_query(session).params(id=id_argument).all()
    
    Above, we again cache not just the query object but all the work it needs
    to do in order to generate SQL.  We also no longer need to deal with
    making sure we generate a cache key that accurately takes into account
    all of the structural modifications we've made; this is now handled
    automatically and without the chance of mistakes.
    
    This code sample is a few lines shorter than the naive example, removes
    the need to deal with cache keys, and has the vast performance benefits
    of the full so-called "baked" feature.  But
    still a little verbose!  Hence we take methods like :meth:`.BakedQuery.add_criteria`
    and :meth:`.BakedQuery.with_criteria` and shorten them into operators, and
    encourage (though certainly not require!) using simple lambdas, only as a
    means to reduce verbosity::
    
        bakery = baked.bakery()
    
    
        def lookup(session, id_argument, include_frobnizzle=False):
            parameterized_query = bakery.bake(
                lambda s: s.query(Model).filter(Model.id == bindparam("id"))
            )
    
            if include_frobnizzle:
                parameterized_query += lambda q: q.filter(Model.frobnizzle == True)
    
            return parameterized_query(session).params(id=id_argument).all()
    
    Where above, the approach is simpler to implement and much more similar
    in code flow to what a non-cached querying function would look like,
    hence making code easier to port.
    
    The above description is essentially a summary of the design process used
    to arrive at the current "baked" approach.   Starting from the
    "normal" approaches, the additional issues of cache key construction and
    management,  removal of all redundant Python execution, and queries built up
    with conditionals needed to be addressed, leading to the final approach.

特殊查询技术
------------------------

Special Query Techniques

.. tab:: 中文

    本节将描述一些针对特定查询情况的技术。

.. tab:: 英文

    This section will describe some techniques for specific query situations.

.. _baked_in:

使用 IN 表达式
^^^^^^^^^^^^^^^^^^^^

Using IN expressions

.. tab:: 中文

SQLAlchemy 中的 :meth:`.ColumnOperators.in_` 方法历史上基于传递给方法的项列表，
渲染一组可变的绑定参数。 由于该列表的长度在不同调用时可能发生变化，
因此对于 baked 查询而言，这种方法不可行。 为了解决这个问题，
:paramref:`.bindparam.expanding` 参数支持一个延迟渲染的 IN 表达式，
该表达式可以安全地缓存到 baked 查询中。 实际的元素列表在语句执行时渲染，而不是在语句编译时::

    bakery = baked.bakery()

    baked_query = bakery(lambda session: session.query(User))
    baked_query += lambda q: q.filter(User.name.in_(bindparam("username", expanding=True)))

    result = baked_query.with_session(session).params(username=["ed", "fred"]).all()

.. seealso::

  :paramref:`.bindparam.expanding`

  :meth:`.ColumnOperators.in_`

.. tab:: 英文

    The :meth:`.ColumnOperators.in_` method in SQLAlchemy historically renders
    a variable set of bound parameters based on the list of items that's passed
    to the method.   This doesn't work for baked queries as the length of that
    list can change on different calls.  To solve this problem, the
    :paramref:`.bindparam.expanding` parameter supports a late-rendered IN
    expression that is safe to be cached inside of baked query.  The actual list
    of elements is rendered at statement execution time, rather than at
    statement compilation time::
    
        bakery = baked.bakery()
    
        baked_query = bakery(lambda session: session.query(User))
        baked_query += lambda q: q.filter(User.name.in_(bindparam("username", expanding=True)))
    
        result = baked_query.with_session(session).params(username=["ed", "fred"]).all()
    
    .. seealso::
    
      :paramref:`.bindparam.expanding`
    
      :meth:`.ColumnOperators.in_`

使用子查询
^^^^^^^^^^^^^^^^

Using Subqueries

.. tab:: 中文

    在使用 :class:`_query.Query` 对象时，通常需要一个 :class:`_query.Query`
    对象用于在另一个查询中生成子查询。 在 :class:`_query.Query` 已经是 baked 形式时，
    可以使用一个临时方法通过 :meth:`.BakedQuery.to_query` 方法检索该 :class:`_query.Query` 对象。
    该方法传递给一个用于生成 baked 查询特定步骤的 lambda 可调用对象的 :class:`.Session` 或 :class:`_query.Query` 对象::
    
        bakery = baked.bakery()
    
        # 一个最终将用作子查询的 baked 查询
        my_subq = bakery(lambda s: s.query(User.id))
        my_subq += lambda q: q.filter(User.id == Address.user_id)
    
        # 在顶部列出选择一个相关的子查询，
        # 我们有“session”参数，将其传递进去
        my_q = bakery(lambda s: s.query(Address.id, my_subq.to_query(s).as_scalar()))
    
        # 在某些标准中使用相关的子查询，我们有“query”参数，将其传递进去。
        my_q += lambda q: q.filter(my_subq.to_query(q).exists())

.. tab:: 英文

    When using :class:`_query.Query` objects, it is often needed that one :class:`_query.Query`
    object is used to generate a subquery within another.   In the case where the
    :class:`_query.Query` is currently in baked form, an interim method may be used to
    retrieve the :class:`_query.Query` object, using the :meth:`.BakedQuery.to_query`
    method.  This method is passed the :class:`.Session` or :class:`_query.Query` that is
    the argument to the lambda callable used to generate a particular step
    of the baked query::
    
        bakery = baked.bakery()
    
        # a baked query that will end up being used as a subquery
        my_subq = bakery(lambda s: s.query(User.id))
        my_subq += lambda q: q.filter(User.id == Address.user_id)
    
        # select a correlated subquery in the top columns list,
        # we have the "session" argument, pass that
        my_q = bakery(lambda s: s.query(Address.id, my_subq.to_query(s).as_scalar()))
    
        # use a correlated subquery in some of the criteria, we have
        # the "query" argument, pass that.
        my_q += lambda q: q.filter(my_subq.to_query(q).exists())

.. _baked_with_before_compile:

使用 before_compile 事件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the before_compile event

.. tab:: 中文

    从 SQLAlchemy 1.3.11 开始，对特定 :class:`_query.Query` 使用 :meth:`.QueryEvents.before_compile` 事件，
    如果事件钩子返回与传递的 :class:`_query.Query` 对象不同的新的 :class:`_query.Query` 对象，
    则会禁止 baked 查询系统缓存该查询。 这样做是为了使 :meth:`.QueryEvents.before_compile`
    钩子可以在每次使用时调用特定的 :class:`_query.Query`，以适应每次修改查询的钩子。
    为了允许 :meth:`.QueryEvents.before_compile` 修改 :meth:`_query.Query` 对象，
    但仍然允许结果被缓存，可以注册事件并传递 ``bake_ok=True`` 标志::
    
        @event.listens_for(Query, "before_compile", retval=True, bake_ok=True)
        def my_event(query):
            for desc in query.column_descriptions:
                if desc["type"] is User:
                    entity = desc["entity"]
                    query = query.filter(entity.deleted == False)
            return query
    
    上述策略适用于每次都会以完全相同的方式修改给定 :class:`_query.Query` 的事件，
    不依赖于特定的参数或外部状态的变化。

.. tab:: 英文

    As of SQLAlchemy 1.3.11, the use of the :meth:`.QueryEvents.before_compile`
    event against a particular :class:`_query.Query` will disallow the baked query
    system from caching the query, if the event hook returns a new :class:`_query.Query`
    object that is different from the one passed in.  This is so that the
    :meth:`.QueryEvents.before_compile` hook may be invoked against a particular
    :class:`_query.Query` every time it is used, to accommodate for hooks that
    alter the query differently each time.    To allow a
    :meth:`.QueryEvents.before_compile` to alter a :meth:`_query.Query` object, but
    still to allow the result to be cached, the event can be registered
    passing the ``bake_ok=True`` flag::
    
        @event.listens_for(Query, "before_compile", retval=True, bake_ok=True)
        def my_event(query):
            for desc in query.column_descriptions:
                if desc["type"] is User:
                    entity = desc["entity"]
                    query = query.filter(entity.deleted == False)
            return query
    
    The above strategy is appropriate for an event that will modify a
    given :class:`_query.Query` in exactly the same way every time, not dependent
    on specific parameters or external state that changes.

在会话范围内禁用烘焙查询
------------------------------------

Disabling Baked Queries Session-wide

.. tab:: 中文

    :paramref:`.Session.enable_baked_queries` 标志可以设置为 False，
    使得在该 :class:`.Session` 中使用的所有 baked 查询都不使用缓存::
    
        session = Session(engine, enable_baked_queries=False)
    
    像所有会话标志一样，它也被工厂对象（如 :class:`.sessionmaker`）和方法（如 :meth:`.sessionmaker.configure`）接受。
    
    此标志的直接原因是，应用程序在遇到可能由于用户定义的 baked 查询或其他 baked 查询问题导致的缓存键冲突时，
    可以关闭该行为，以识别或消除 baked 查询作为问题的根源。

.. tab:: 英文

    The flag :paramref:`.Session.enable_baked_queries` may be set to False,
    causing all baked queries to not use the cache when used against that
    :class:`.Session`::
    
        session = Session(engine, enable_baked_queries=False)
    
    Like all session flags, it is also accepted by factory objects like
    :class:`.sessionmaker` and methods like :meth:`.sessionmaker.configure`.
    
    The immediate rationale for this flag is so that an application
    which is seeing issues potentially due to cache key conflicts from user-defined
    baked queries or other baked query issues can turn the behavior off, in
    order to identify or eliminate baked queries as the cause of an issue.

延迟加载集成
------------------------

Lazy Loading Integration

.. tab:: 中文

    .. versionchanged:: 1.4 
        
        从 SQLAlchemy 1.4 开始，“baked 查询”系统不再是关系加载系统的一部分。 取而代之的是使用 :ref:`native caching <sql_caching>` 系统。
    

.. tab:: 英文

    .. versionchanged:: 1.4 As of SQLAlchemy 1.4, the "baked query" system is no
       longer part of the relationship loading system.
       The :ref:`native caching <sql_caching>` system is used instead.


API 文档
-----------------

API Documentation

.. tab:: 中文

.. tab:: 英文

.. autofunction:: bakery

.. autoclass:: BakedQuery
    :members:

.. autoclass:: Bakery
    :members:

.. autoclass:: Result
    :members:
    :noindex:

