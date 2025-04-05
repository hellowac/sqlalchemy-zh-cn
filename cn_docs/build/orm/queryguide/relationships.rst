.. |prev| replace:: :doc:`columns`
.. |next| replace:: :doc:`api`

.. include:: queryguide_nav_include.rst

.. _orm_queryguide_relationship_loaders:

.. _loading_toplevel:

.. currentmodule:: sqlalchemy.orm

关系加载技术
===============================

Relationship Loading Techniques

.. tab:: 中文

    .. admonition:: 关于本文档

        本节深入介绍了如何加载相关对象。读者应熟悉 :ref:`relationship_config_toplevel` 和基本用法。

        大多数示例假定类似于 :doc:`选择的设置 <_plain_setup>` 中说明的 "用户/地址" 映射设置。

    SQLAlchemy 的一个重要部分是提供广泛的控制，以在查询时加载相关对象。所谓“相关对象”是指使用 :func:`_orm.relationship` 在映射器上配置的集合或标量关联。这种行为可以在映射器构造时使用 :func:`_orm.relationship` 函数的 :paramref:`_orm.relationship.lazy` 参数进行配置，也可以通过使用 **ORM 加载选项** 与 :class:`_sql.Select` 构造一起配置。

    关系的加载分为三类： **延迟(lazy)** 加载、 **急切(eager)** 加载和 **不(no)** 加载。延迟加载是指从查询返回的对象最初没有加载相关对象。当在特定对象上首次访问给定集合或引用时，将发出一个额外的 SELECT 语句，以便加载请求的集合。

    急切加载是指从查询返回的对象已经预先加载了相关的集合或标量引用。ORM 要么通过增强通常会发出的 SELECT 语句与 JOIN 一起加载相关行，要么通过在主语句之后发出额外的 SELECT 语句一次性加载集合或标量引用来实现这一点。

    “不”加载是指禁用给定关系的加载，即属性为空并且从不加载，或者在访问时引发错误，以防止不必要的延迟加载。

.. tab:: 英文

    .. admonition:: About this Document

        This section presents an in-depth view of how to load related
        objects.   Readers should be familiar with
        :ref:`relationship_config_toplevel` and basic use.

        Most examples here assume the "User/Address" mapping setup similar
        to the one illustrated at :doc:`setup for selects <_plain_setup>`.

    A big part of SQLAlchemy is providing a wide range of control over how related
    objects get loaded when querying.   By "related objects" we refer to collections
    or scalar associations configured on a mapper using :func:`_orm.relationship`.
    This behavior can be configured at mapper construction time using the
    :paramref:`_orm.relationship.lazy` parameter to the :func:`_orm.relationship`
    function, as well as by using **ORM loader options** with
    the :class:`_sql.Select` construct.

    The loading of relationships falls into three categories; **lazy** loading,
    **eager** loading, and **no** loading. Lazy loading refers to objects that are returned
    from a query without the related
    objects loaded at first.  When the given collection or reference is
    first accessed on a particular object, an additional SELECT statement
    is emitted such that the requested collection is loaded.

    Eager loading refers to objects returned from a query with the related
    collection or scalar reference already loaded up front.  The ORM
    achieves this either by augmenting the SELECT statement it would normally
    emit with a JOIN to load in related rows simultaneously, or by emitting
    additional SELECT statements after the primary one to load collections
    or scalar references at once.

    "No" loading refers to the disabling of loading on a given relationship, either
    that the attribute is empty and is just never loaded, or that it raises
    an error when it is accessed, in order to guard against unwanted lazy loads.

关系加载样式摘要
--------------------------------------

Summary of Relationship Loading Styles

.. tab:: 中文

    主要的关系加载方式有：

    * **懒加载 (lazy loading)** - 可通过 ``lazy='select'`` 或 :func:`.lazyload` 选项实现，这种加载方式会在访问属性时发出一个 SELECT 语句，懒加载每次仅加载一个对象的关联引用。懒加载是所有没有特别指示 :paramref:`_orm.relationship.lazy` 选项的 :func:`_orm.relationship` 构造的 **默认加载方式**。懒加载的详细信息参见 :ref:`lazy_loading`。

    * **select IN 加载 (select IN loading)** - 可通过 ``lazy='selectin'`` 或 :func:`.selectinload` 选项实现，这种加载方式会发出第二个（或更多）SELECT 语句，将父对象的主键标识符组装到 IN 子句中，从而一次性加载所有相关集合或标量引用。select IN 加载的详细信息参见 :ref:`selectin_eager_loading`。

    * **连接加载 (joined loading)** - 可通过 ``lazy='joined'`` 或 :func:`_orm.joinedload` 选项实现，这种加载方式会对给定的 SELECT 语句应用 JOIN，以便将相关行加载到同一结果集中。连接急加载的详细信息参见 :ref:`joined_eager_loading`。

    * **异常加载 (raise loading)** - 可通过 ``lazy='raise'``、``lazy='raise_on_sql'`` 或 :func:`.raiseload` 选项实现，这种加载方式会在通常进行懒加载时触发，但会抛出 ORM 异常，以防止应用程序进行不希望的懒加载。异常加载的介绍参见 :ref:`prevent_lazy_with_raiseload`。

    * **子查询加载 (subquery loading)** - 可通过 ``lazy='subquery'`` 或 :func:`.subqueryload` 选项实现，这种加载方式会发出第二个 SELECT 语句，该语句在子查询中重新声明原始查询，然后将该子查询与相关表连接，以便一次性加载所有相关集合或标量引用。子查询急加载的详细信息参见 :ref:`subquery_eager_loading`。

    * **仅写加载 (write only loading)** - 可通过 ``lazy='write_only'`` 或使用 :class:`_orm.WriteOnlyMapped` 注解来标注 :class:`_orm.Relationship` 对象的左侧。这种仅集合的加载方式生成一种替代的属性仪器，它永远不会隐式地从数据库加载记录，而是仅允许使用 :meth:`.WriteOnlyCollection.add`、:meth:`.WriteOnlyCollection.add_all` 和 :meth:`.WriteOnlyCollection.remove` 方法。查询集合是通过调用 :meth:`.WriteOnlyCollection.select` 方法来执行构建的 SELECT 语句。仅写加载的详细信息参见 :ref:`write_only_relationship`。

    * **动态加载 (dynamic loading)** - 可通过 ``lazy='dynamic'`` 或使用 :class:`_orm.DynamicMapped` 注解来标注 :class:`_orm.Relationship` 对象的左侧。这是一个旧版的仅集合加载方式，它在访问集合时生成 :class:`_orm.Query` 对象，从而允许对集合内容发出自定义 SQL。然而，动态加载器在某些情况下会隐式地迭代底层集合，这使得它们在管理真正的大集合时不太有用。动态加载器被 :ref:`"write only" <write_only_relationship>` 集合所取代，这将防止在任何情况下隐式加载底层集合。动态加载器的详细信息参见 :ref:`dynamic_relationship`。

.. tab:: 英文

    The primary forms of relationship loading are:

    * **lazy loading** - available via ``lazy='select'`` or the :func:`.lazyload` option, this is the form of loading that emits a SELECT statement at attribute access time to lazily load a related reference on a single object at a time.  Lazy loading is the **default loading style** for all :func:`_orm.relationship` constructs that don't otherwise indicate the :paramref:`_orm.relationship.lazy` option.  Lazy loading is detailed at :ref:`lazy_loading`.

    * **select IN loading** - available via ``lazy='selectin'`` or the :func:`.selectinload` option, this form of loading emits a second (or more) SELECT statement which assembles the primary key identifiers of the parent objects into an IN clause, so that all members of related collections / scalar references are loaded at once by primary key.  Select IN loading is detailed at :ref:`selectin_eager_loading`.

    * **joined loading** - available via ``lazy='joined'`` or the :func:`_orm.joinedload` option, this form of loading applies a JOIN to the given SELECT statement so that related rows are loaded in the same result set.   Joined eager loading is detailed at :ref:`joined_eager_loading`.

    * **raise loading** - available via ``lazy='raise'``, ``lazy='raise_on_sql'``, or the :func:`.raiseload` option, this form of loading is triggered at the same time a lazy load would normally occur, except it raises an ORM exception in order to guard against the application making unwanted lazy loads. An introduction to raise loading is at :ref:`prevent_lazy_with_raiseload`.

    * **subquery loading** - available via ``lazy='subquery'`` or the :func:`.subqueryload` option, this form of loading emits a second SELECT statement which re-states the original query embedded inside of a subquery, then JOINs that subquery to the related table to be loaded to load all members of related collections / scalar references at once.  Subquery eager loading is detailed at :ref:`subquery_eager_loading`.

    * **write only loading** - available via ``lazy='write_only'``, or by annotating the left side of the :class:`_orm.Relationship` object using the :class:`_orm.WriteOnlyMapped` annotation.   This collection-only loader style produces an alternative attribute instrumentation that never implicitly loads records from the database, instead only allowing :meth:`.WriteOnlyCollection.add`, :meth:`.WriteOnlyCollection.add_all` and :meth:`.WriteOnlyCollection.remove` methods.  Querying the collection is performed by invoking a SELECT statement which is constructed using the :meth:`.WriteOnlyCollection.select` method.    Write only loading is discussed at :ref:`write_only_relationship`.

    * **dynamic loading** - available via ``lazy='dynamic'``, or by annotating the left side of the :class:`_orm.Relationship` object using the :class:`_orm.DynamicMapped` annotation. This is a legacy collection-only loader style which produces a :class:`_orm.Query` object when the collection is accessed, allowing custom SQL to be emitted against the collection's contents. However, dynamic loaders will implicitly iterate the underlying collection in various circumstances which makes them less useful for managing truly large collections. Dynamic loaders are superseded by :ref:`"write only" <write_only_relationship>` collections, which will prevent the underlying collection from being implicitly loaded under any circumstances. Dynamic loaders are discussed at :ref:`dynamic_relationship`.


.. _relationship_lazy_option:

在映射时配置加载器策略
---------------------------------------------

Configuring Loader Strategies at Mapping Time

.. tab:: 中文

    可以在映射时配置某个关系的加载策略，使其在加载映射类型的对象时始终生效，前提是查询级别没有修改它的选项。这可以通过 :paramref:`_orm.relationship.lazy` 参数配置到 :func:`_orm.relationship` 中；该参数的常见值包括 ``select``、``selectin`` 和 ``joined``。

    下面的示例说明了 :ref:`relationship_patterns_o2m` 中的关系示例，将 ``Parent.children`` 关系配置为在发出 ``Parent`` 对象的 SELECT 语句时使用 :ref:`selectin_eager_loading`：

        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Parent(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(lazy="selectin")


        class Child(Base):
            __tablename__ = "child"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))

    在上述示例中，每当加载 ``Parent`` 对象的集合时，每个 ``Parent`` 对象的 ``children`` 集合也将被填充，并使用 ``"selectin"`` 加载策略发出第二个查询。

    :paramref:`_orm.relationship.lazy` 参数的默认值是 ``"select"`` ，这表示使用 :ref:`lazy_loading`。


.. tab:: 英文

    The loader strategy for a particular relationship can be configured at mapping time to take place in all cases where an object of the mapped type is loaded, in the absence of any query-level options that modify it. This is configured using the :paramref:`_orm.relationship.lazy` parameter to :func:`_orm.relationship`; common values for this parameter include ``select``, ``selectin`` and ``joined``.

    The example below illustrates the relationship example at :ref:`relationship_patterns_o2m`, configuring the ``Parent.children`` relationship to use :ref:`selectin_eager_loading` when a SELECT statement for ``Parent`` objects is emitted::

        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Parent(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(lazy="selectin")


        class Child(Base):
            __tablename__ = "child"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))

    Above, whenever a collection of ``Parent`` objects are loaded, each ``Parent`` will also have its ``children`` collection populated, using the ``"selectin"`` loader strategy that emits a second query.

    The default value of the :paramref:`_orm.relationship.lazy` argument is ``"select"``, which indicates :ref:`lazy_loading`.

.. _relationship_loader_options:

使用加载器选项进行关系加载
----------------------------------------

Relationship Loading with Loader Options

.. tab:: 中文

    另一种可能更常见的配置加载策略的方式是，通过 :meth:`_sql.Select.options` 方法在每个查询基础上为特定属性设置加载策略。使用加载器选项可以对关系加载进行非常详细的控制；最常用的加载器选项有 :func:`_orm.joinedload` 、:func:`_orm.selectinload` 和 :func:`_orm.lazyload`。该选项接受一个类绑定的属性，指向应该被加载的特定类/属性：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        # 将 children 设置为懒加载
        stmt = select(Parent).options(lazyload(Parent.children))

        from sqlalchemy.orm import joinedload

        # 将 children 设置为通过 JOIN 来急加载
        stmt = select(Parent).options(joinedload(Parent.children))

    加载器选项还可以通过 **方法链式调用** 来进一步指定加载应如何发生在更深层级的属性上：

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload

        stmt = select(Parent).options(
            joinedload(Parent.children).subqueryload(Child.subelements)
        )

    可以对 "懒加载" 集合应用链式加载器选项。这意味着当某个集合或关联在访问时被懒加载时，指定的选项会生效：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(Parent).options(lazyload(Parent.children).subqueryload(Child.subelements))

    如上所示，该查询将返回不包含 ``children`` 集合的 ``Parent`` 对象。当特定 ``Parent`` 对象的 ``children`` 集合首次被访问时，它将懒加载相关对象，但还会对每个 ``children`` 成员的 ``subelements`` 集合应用急加载。

.. tab:: 英文

    The other, and possibly more common way to configure loading strategies is to set them up on a per-query basis against specific attributes using the :meth:`_sql.Select.options` method.  Very detailed control over relationship loading is available using loader options; the most common are :func:`_orm.joinedload`, :func:`_orm.selectinload` and :func:`_orm.lazyload`.   The option accepts a class-bound attribute referring to the specific class/attribute that should be targeted::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        # set children to load lazily
        stmt = select(Parent).options(lazyload(Parent.children))

        from sqlalchemy.orm import joinedload

        # set children to load eagerly with a join
        stmt = select(Parent).options(joinedload(Parent.children))

    The loader options can also be "chained" using **method chaining** to specify how loading should occur further levels deep::

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload

        stmt = select(Parent).options(
            joinedload(Parent.children).subqueryload(Child.subelements)
        )

    Chained loader options can be applied against a "lazy" loaded collection. This means that when a collection or association is lazily loaded upon access, the specified option will then take effect::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(Parent).options(lazyload(Parent.children).subqueryload(Child.subelements))

    Above, the query will return ``Parent`` objects without the ``children`` collections loaded.  When the ``children`` collection on a particular ``Parent`` object is first accessed, it will lazy load the related objects, but additionally apply eager loading to the ``subelements`` collection on each member of ``children``.


.. _loader_option_criteria:

向加载器选项添加条件
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding Criteria to loader options

.. tab:: 中文

    用于指示加载器选项的关系属性包括能够将额外的过滤条件添加到创建的连接的 ON 子句中，或者添加到相关的 WHERE 条件中，这取决于加载策略。可以通过 :meth:`.PropComparator.and_` 方法来实现，该方法会将一个选项传递过去，从而将加载结果限制为给定的过滤条件：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(A).options(lazyload(A.bs.and_(B.id > 5)))

    使用限制条件时，如果某个集合已经加载，它将不会被刷新；为了确保新条件生效，可以应用 :ref:`orm_queryguide_populate_existing` 执行选项：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = (
            select(A)
            .options(lazyload(A.bs.and_(B.id > 5)))
            .execution_options(populate_existing=True)
        )

    如果希望将过滤条件添加到查询中的所有实体实例中，而不管加载策略是什么，也不管它出现在加载过程的哪个阶段，可以参见 :func:`_orm.with_loader_criteria` 函数。

    .. versionadded:: 1.4


.. tab:: 英文

    The relationship attributes used to indicate loader options include the ability to add additional filtering criteria to the ON clause of the join that's created, or to the WHERE criteria involved, depending on the loader strategy.  This can be achieved using the :meth:`.PropComparator.and_` method which will pass through an option such that loaded results are limited to the given filter criteria::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(A).options(lazyload(A.bs.and_(B.id > 5)))

    When using limiting criteria, if a particular collection is already loaded it won't be refreshed; to ensure the new criteria takes place, apply the :ref:`orm_queryguide_populate_existing` execution option::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = (
            select(A)
            .options(lazyload(A.bs.and_(B.id > 5)))
            .execution_options(populate_existing=True)
        )

    In order to add filtering criteria to all occurrences of an entity throughout a query, regardless of loader strategy or where it occurs in the loading process, see the :func:`_orm.with_loader_criteria` function.

    .. versionadded:: 1.4

.. _orm_queryguide_relationship_sub_options:

使用 Load.options() 指定子选项
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Specifying Sub-Options with Load.options()

.. tab:: 中文

    通过方法链式调用，每个路径链接的加载器样式都被明确指定。为了在不改变特定属性的现有加载器样式的情况下沿路径导航，可以使用 :func:`.defaultload` 方法/函数：

        from sqlalchemy import select
        from sqlalchemy.orm import defaultload

        stmt = select(A).options(defaultload(A.atob).joinedload(B.btoc))

    也可以使用类似的方法一次性指定多个子选项，通过 :meth:`_orm.Load.options` 方法：

        from sqlalchemy import select
        from sqlalchemy.orm import defaultload
        from sqlalchemy.orm import joinedload

        stmt = select(A).options(
            defaultload(A.atob).options(joinedload(B.btoc), joinedload(B.btod))
        )

    .. seealso::

        :ref:`orm_queryguide_load_only_related` - 说明了如何结合关系和面向列的加载器选项的示例。

    .. note::  

        应用于对象懒加载集合的加载器选项是 **“粘性”(sticky)** 的，意味着它们会持续存在于由特定对象加载的集合中，只要该对象仍然存在于内存中。例如，给定以下示例：

            stmt = select(Parent).options(lazyload(Parent.children).subqueryload(Child.subelements))

    如果通过上述查询加载的 ``Parent`` 对象的 ``children`` 集合过期（例如，当 :class:`.Session` 对象的事务被提交或回滚，或使用了 :meth:`.Session.expire_all`），下次访问 ``Parent.children`` 集合并重新加载时，``Child.subelements`` 集合将再次使用子查询急加载。这种情况即使在后续查询中访问该 ``Parent`` 对象，并指定不同的选项时依然成立。要在不清除并重新加载对象的情况下更改现有对象的选项，必须通过联合使用 :ref:`orm_queryguide_populate_existing` 执行选项明确设置：

            # 更改已经加载的 Parent 对象的选项
            stmt = (
                select(Parent)
                .execution_options(populate_existing=True)
                .options(lazyload(Parent.children).lazyload(Child.subelements))
                .all()
            )

    如果上面加载的对象已经完全从 :class:`.Session` 中清除（例如，垃圾回收，或者使用了 :meth:`.Session.expunge_all`），那么 "粘性(sticky)" 选项也会消失，重新创建的对象在重新加载时将使用新的选项。

    未来的 SQLAlchemy 版本可能会添加更多替代方法，用于操作已经加载的对象的加载器选项。

.. tab:: 英文

    Using method chaining, the loader style of each link in the path is explicitly stated.  To navigate along a path without changing the existing loader style of a particular attribute, the :func:`.defaultload` method/function may be used::

        from sqlalchemy import select
        from sqlalchemy.orm import defaultload

        stmt = select(A).options(defaultload(A.atob).joinedload(B.btoc))

    A similar approach can be used to specify multiple sub-options at once, using the :meth:`_orm.Load.options` method::

        from sqlalchemy import select
        from sqlalchemy.orm import defaultload
        from sqlalchemy.orm import joinedload

        stmt = select(A).options(
            defaultload(A.atob).options(joinedload(B.btoc), joinedload(B.btod))
        )

    .. seealso::

        :ref:`orm_queryguide_load_only_related` - illustrates examples of combining relationship and column-oriented loader options.


    .. note::  
        
        The loader options applied to an object's lazy-loaded collections are **"sticky"** to specific object instances, meaning they will persist upon collections loaded by that specific object for as long as it exists in memory.  For example, given the previous example::

            stmt = select(Parent).options(lazyload(Parent.children).subqueryload(Child.subelements))

    if the ``children`` collection on a particular ``Parent`` object loaded by the above query is expired (such as when a :class:`.Session` object's transaction is committed or rolled back, or :meth:`.Session.expire_all` is used), when the ``Parent.children`` collection is next accessed in order to re-load it, the ``Child.subelements`` collection will again be loaded using subquery eager loading. This stays the case even if the above ``Parent`` object is accessed from a subsequent query that specifies a different set of options. To change the options on an existing object without expunging it and re-loading, they must be set explicitly in conjunction using the
    :ref:`orm_queryguide_populate_existing` execution option::

            # change the options on Parent objects that were already loaded
            stmt = (
                select(Parent)
                .execution_options(populate_existing=True)
                .options(lazyload(Parent.children).lazyload(Child.subelements))
                .all()
            )

    If the objects loaded above are fully cleared from the :class:`.Session`, such as due to garbage collection or that :meth:`.Session.expunge_all` were used, the "sticky" options will also be gone and the newly created objects will make use of new options if loaded again.

    A future SQLAlchemy release may add more alternatives to manipulating the loader options on already-loaded objects.


.. _lazy_loading:

延迟加载
------------

Lazy Loading

.. tab:: 中文

    默认情况下，所有对象间的关系都是 **懒加载**。与 :func:`_orm.relationship` 相关的标量或集合属性包含一个触发器，该触发器在第一次访问该属性时触发。这个触发器通常会在访问时发出 SQL 调用，以加载相关对象或对象集合：

    .. sourcecode:: pycon+sql

        >>> spongebob.addresses
        {execsql}SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
        FROM addresses
        WHERE ? = addresses.user_id
        [5]
        {stop}[<Address(u'spongebob@google.com')>, <Address(u'j25@yahoo.com')>]

    唯一不发出 SQL 的情况是简单的多对一关系，当相关对象仅通过其主键就能识别，并且该对象已经存在于当前 :class:`.Session` 中。因此，虽然懒加载对于相关集合可能开销较大，但在加载大量对象且与相对较小的一组目标对象具有简单多对一关系的情况下，懒加载可以本地引用这些对象，而不需要像有多少个父对象就发出多少个 SELECT 语句。

    这种“按属性访问时加载”的默认行为被称为“懒加载”或“select”加载 —— “select” 这个名字是因为在第一次访问属性时通常会发出一个 "SELECT" 语句。

    可以通过 :func:`.lazyload` 加载器选项为正常配置为其他方式的属性启用懒加载：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        # 强制懒加载一个通常以其他方式加载的属性
        stmt = select(User).options(lazyload(User.addresses))


.. tab:: 英文

    By default, all inter-object relationships are **lazy loading**. The scalar or collection attribute associated with a :func:`_orm.relationship` contains a trigger which fires the first time the attribute is accessed.  This trigger typically issues a SQL call at the point of access in order to load the related object or objects:

    .. sourcecode:: pycon+sql

        >>> spongebob.addresses
        {execsql}SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
        FROM addresses
        WHERE ? = addresses.user_id
        [5]
        {stop}[<Address(u'spongebob@google.com')>, <Address(u'j25@yahoo.com')>]

    The one case where SQL is not emitted is for a simple many-to-one relationship, when the related object can be identified by its primary key alone and that object is already present in the current :class:`.Session`.  For this reason, while lazy loading can be expensive for related collections, in the case that one is loading lots of objects with simple many-to-ones against a relatively small set of possible target objects, lazy loading may be able to refer to these objects locally without emitting as many SELECT statements as there are parent objects.

    This default behavior of "load upon attribute access" is known as "lazy" or "select" loading - the name "select" because a "SELECT" statement is typically emitted when the attribute is first accessed.

    Lazy loading can be enabled for a given attribute that is normally configured in some other way using the :func:`.lazyload` loader option::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        # force lazy loading for an attribute that is set to
        # load some other way normally
        stmt = select(User).options(lazyload(User.addresses))

.. _prevent_lazy_with_raiseload:

使用 raiseload 防止不必要的延迟加载
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Preventing unwanted lazy loads using raiseload

.. tab:: 中文

    :func:`.lazyload` 策略会产生在对象关系映射中最常见的问题之一；即 :term:`N+1 问题`，该问题指出，对于任何 N 个加载的对象，访问它们的懒加载属性将导致发出 N+1 个 SELECT 语句。在 SQLAlchemy 中，通常解决 N+1 问题的方法是利用其非常强大的急加载系统。然而，急加载要求提前在 :class:`_sql.Select` 中指定要加载的属性。对于代码可能访问那些没有急加载的属性，而又不希望进行懒加载的情况，可以使用 :func:`.raiseload` 策略来解决；此加载器策略将懒加载的行为替换为抛出信息性错误：

        from sqlalchemy import select
        from sqlalchemy.orm import raiseload

        stmt = select(User).options(raiseload(User.addresses))

    上述代码中，使用此查询加载的 ``User`` 对象将不会加载 ``.addresses`` 集合；如果稍后某些代码尝试访问此属性，将引发 ORM 异常。

    :func:`.raiseload` 可以与所谓的“通配符”说明符一起使用，表示所有关系都应该使用此策略。例如，设置仅一个属性为急加载，而其余属性都为 raise：

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        from sqlalchemy.orm import raiseload

        stmt = select(Order).options(joinedload(Order.items), raiseload("*"))

    上述通配符将应用于 **所有** 关系，不仅仅是 ``Order`` 上的 ``items``，而且还包括 ``Item`` 对象上的所有关系。要仅对 ``Order`` 对象设置 :func:`.raiseload`，可以使用 :class:`_orm.Load` 指定完整路径：

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        from sqlalchemy.orm import Load

        stmt = select(Order).options(joinedload(Order.items), Load(Order).raiseload("*"))

    相反，要仅对 ``Item`` 对象设置 raise：

        stmt = select(Order).options(joinedload(Order.items).raiseload("*"))

    :func:`.raiseload` 选项仅适用于关系属性。对于面向列的属性，:func:`.defer` 选项支持 :paramref:`.orm.defer.raiseload` 选项，功能与此相同。

    .. tip:: 
        
        "raiseload" 策略 **不适用于** :term:`工作单元` 刷新过程。这意味着，如果 :meth:`_orm.Session.flush` 过程需要加载集合以完成其工作，它将在绕过任何 :func:`_orm.raiseload` 指令的情况下进行。

    .. seealso::

        :ref:`wildcard_loader_strategies`

        :ref:`orm_queryguide_deferred_raiseload`


.. tab:: 英文

    The :func:`.lazyload` strategy produces an effect that is one of the most common issues referred to in object relational mapping; the :term:`N plus one problem`, which states that for any N objects loaded, accessing their lazy-loaded attributes means there will be N+1 SELECT statements emitted.  In SQLAlchemy, the usual mitigation for the N+1 problem is to make use of its very capable eager load system.  However, eager loading requires that the attributes which are to be loaded be specified with the :class:`_sql.Select` up front.  The problem of code that may access other attributes that were not eagerly loaded, where lazy loading is not desired, may be addressed using the :func:`.raiseload` strategy; this loader strategy replaces the behavior of lazy loading with an informative error being raised::

        from sqlalchemy import select
        from sqlalchemy.orm import raiseload

        stmt = select(User).options(raiseload(User.addresses))

    Above, a ``User`` object loaded from the above query will not have the ``.addresses`` collection loaded; if some code later on attempts to access this attribute, an ORM exception is raised.

    :func:`.raiseload` may be used with a so-called "wildcard" specifier to indicate that all relationships should use this strategy.  For example, to set up only one attribute as eager loading, and all the rest as raise::

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        from sqlalchemy.orm import raiseload

        stmt = select(Order).options(joinedload(Order.items), raiseload("*"))

    The above wildcard will apply to **all** relationships not just on ``Order`` besides ``items``, but all those on the ``Item`` objects as well.  To set up :func:`.raiseload` for only the ``Order`` objects, specify a full path with :class:`_orm.Load`::

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        from sqlalchemy.orm import Load

        stmt = select(Order).options(joinedload(Order.items), Load(Order).raiseload("*"))

    Conversely, to set up the raise for just the ``Item`` objects::

        stmt = select(Order).options(joinedload(Order.items).raiseload("*"))

    The :func:`.raiseload` option applies only to relationship attributes.  For column-oriented attributes, the :func:`.defer` option supports the :paramref:`.orm.defer.raiseload` option which works in the same way.

    .. tip:: 
        
        The "raiseload" strategies **do not apply** within the :term:`unit of work` flush process.   That means if the :meth:`_orm.Session.flush` process needs to load a collection in order to finish its work, it will do so while bypassing any :func:`_orm.raiseload` directives.

    .. seealso::

        :ref:`wildcard_loader_strategies`

        :ref:`orm_queryguide_deferred_raiseload`

.. _joined_eager_loading:

连接预/急加载
--------------------

Joined Eager Loading

.. tab:: 中文

    连接急加载(Joined eager loading)是 SQLAlchemy ORM 中最早的急加载方式。它通过在发出的 SELECT 语句中连接一个 JOIN（默认是 LEFT OUTER JOIN），并从与父对象相同的结果集中填充目标标量/集合。

    在映射层，这看起来像：

        class Address(Base):
            # ...

            user: Mapped[User] = relationship(lazy="joined")

    连接急加载(Joined eager loading)通常作为查询选项应用，而不是作为映射上的默认加载选项，特别是在用于集合而不是多对一引用时。可以使用 :func:`_orm.joinedload` 加载器选项来实现：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = select(User).options(joinedload(User.addresses)).filter_by(name="spongebob")
        >>> spongebob = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ['spongebob']

    .. tip::

        当在多对一或多对多集合的引用中使用 :func:`_orm.joinedload` 时，必须对返回的结果应用 :meth:`_result.Result.unique` 方法，该方法会根据主键去重，由于连接操作，返回的行数可能会被乘以。若未使用此方法，ORM 会引发错误。

        这在现代 SQLAlchemy 中并不自动进行，因为它改变了结果集的行为，使得返回的 ORM 对象数量比查询通常返回的行数要少。因此，SQLAlchemy 将 :meth:`_result.Result.unique` 的使用明确化，以避免对返回对象在主键上去重的含糊不清。

    默认发出的 JOIN 是 LEFT OUTER JOIN，以便允许存在不引用相关行的主对象。对于一个保证有元素的属性，比如一个多对一引用到相关对象，并且外键是 NOT NULL 的情况，可以通过使用内连接来提高查询效率；在映射层通过 :paramref:`_orm.relationship.innerjoin` 标志实现：

        class Address(Base):
            # ...

            user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
            user: Mapped[User] = relationship(lazy="joined", innerjoin=True)

    在查询选项层，可以通过 :paramref:`_orm.joinedload.innerjoin` 标志实现：

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload

        stmt = select(Address).options(joinedload(Address.user, innerjoin=True))

    当在一个包含外连接的链中应用时，JOIN 会进行右嵌套：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = select(User).options(
        ...     joinedload(User.addresses).joinedload(Address.widgets, innerjoin=True)
        ... )
        >>> results = session.scalars(stmt).unique().all()
        {execsql}SELECT
            widgets_1.id AS widgets_1_id,
            widgets_1.name AS widgets_1_name,
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN (
            addresses AS addresses_1 JOIN widgets AS widgets_1 ON
            addresses_1.widget_id = widgets_1.id
        ) ON users.id = addresses_1.user_id

    .. tip:: 
        
        如果在发出 SELECT 时使用了数据库行锁定技术（即使用 :meth:`_sql.Select.with_for_update` 方法发出 SELECT..FOR UPDATE），则连接表也可能会被锁定，具体取决于所使用的后端行为。由于这个原因，不推荐在使用 SELECT..FOR UPDATE 时同时使用连接急加载。


.. tab:: 英文

    Joined eager loading is the oldest style of eager loading included with the SQLAlchemy ORM.  It works by connecting a JOIN (by default a LEFT OUTER join) to the SELECT statement emitted, and populates the target scalar/collection from the same result set as that of the parent.

    At the mapping level, this looks like::

        class Address(Base):
            # ...

            user: Mapped[User] = relationship(lazy="joined")

    Joined eager loading is usually applied as an option to a query, rather than as a default loading option on the mapping, in particular when used for collections rather than many-to-one-references.   This is achieved using the :func:`_orm.joinedload` loader option:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = select(User).options(joinedload(User.addresses)).filter_by(name="spongebob")
        >>> spongebob = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ['spongebob']


    .. tip::

        When including :func:`_orm.joinedload` in reference to a one-to-many or many-to-many collection, the :meth:`_result.Result.unique` method must be applied to the returned result, which will uniquify the incoming rows by primary key that otherwise are multiplied out by the join. The ORM will raise an error if this is not present.

        This is not automatic in modern SQLAlchemy, as it changes the behavior of the result set to return fewer ORM objects than the statement would normally return in terms of number of rows.  Therefore SQLAlchemy keeps the use of :meth:`_result.Result.unique` explicit, so there's no ambiguity that the returned objects are being uniqified on primary key.

    The JOIN emitted by default is a LEFT OUTER JOIN, to allow for a lead object that does not refer to a related row.  For an attribute that is guaranteed to have an element, such as a many-to-one reference to a related object where the referencing foreign key is NOT NULL, the query can be made more efficient by using an inner join; this is available at the mapping level via the :paramref:`_orm.relationship.innerjoin` flag::

        class Address(Base):
            # ...

            user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
            user: Mapped[User] = relationship(lazy="joined", innerjoin=True)

    At the query option level, via the :paramref:`_orm.joinedload.innerjoin` flag::

        from sqlalchemy import select
        from sqlalchemy.orm import joinedload

        stmt = select(Address).options(joinedload(Address.user, innerjoin=True))

    The JOIN will right-nest itself when applied in a chain that includes an OUTER JOIN:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = select(User).options(
        ...     joinedload(User.addresses).joinedload(Address.widgets, innerjoin=True)
        ... )
        >>> results = session.scalars(stmt).unique().all()
        {execsql}SELECT
            widgets_1.id AS widgets_1_id,
            widgets_1.name AS widgets_1_name,
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN (
            addresses AS addresses_1 JOIN widgets AS widgets_1 ON
            addresses_1.widget_id = widgets_1.id
        ) ON users.id = addresses_1.user_id


    .. tip:: 
        
        If using database row locking techniques when emitting the SELECT, meaning the :meth:`_sql.Select.with_for_update` method is being used to emit SELECT..FOR UPDATE, the joined table may be locked as well, depending on the behavior of the backend in use.   It's not recommended to use joined eager loading at the same time as SELECT..FOR UPDATE for this reason.



.. NOTE:  wow, this section. super long. it's not really reference material
   either it's conceptual

.. _zen_of_eager_loading:

连接预加载的禅宗
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Zen of Joined Eager Loading

.. tab:: 中文

    由于连接急加载与 :meth:`_sql.Select.join` 的使用有许多相似之处，因此在何时以及如何使用它时常会产生困惑。理解两者的区别至关重要：虽然 :meth:`_sql.Select.join` 用于改变查询的结果， :func:`_orm.joinedload` 则努力 **不** 改变查询的结果，而是隐藏连接的效果，只允许相关对象存在。

    加载器策略背后的哲学是，任何一组加载方案都可以应用于特定的查询，并且 *结果不会改变* —— 只会改变完全加载相关对象和集合所需的 SQL 语句的数量。一个特定的查询可能最初使用所有的延迟加载（lazy loads）。在使用它的过程中，可能会发现某些属性或集合总是被访问，改为为这些属性或集合使用急加载（eager loading）会更高效。加载策略可以在不修改查询的情况下进行更改，结果保持不变，但发出的 SQL 语句会减少。从理论上讲（并且在实践中几乎如此），对 :class:`_sql.Select` 所做的任何操作都不会基于加载策略的变化加载不同的主对象或相关对象集。

    具体来说， :func:`joinedload` 是如何实现这一点的呢？它通过创建一个匿名别名来添加到查询中的 JOIN，因此这些 JOIN 不能被查询的其他部分引用。例如，下面的查询使用 :func:`_orm.joinedload` 来创建一个从 ``users`` 到 ``addresses`` 的 LEFT OUTER JOIN，但是对 ``Address.email_address`` 添加的 ``ORDER BY`` 是无效的——因为在查询中没有命名 ``Address`` 实体：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = (
        ...     select(User)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address   <-- 这个部分是错的！
        ['spongebob']

    上面， ``ORDER BY addresses.email_address`` 是无效的，因为 ``addresses`` 没有出现在 FROM 列表中。正确的加载 ``User`` 记录并按电子邮件地址排序的方法是使用 :meth:`_sql.Select.join`：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}
        SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        JOIN addresses ON users.id = addresses.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address
        ['spongebob']

    上述语句与之前的语句不同，因为 ``addresses`` 的列没有被包含在结果中。我们可以将 :func:`_orm.joinedload` 加回来，这样就有两个连接——一个是我们排序的连接，另一个是用于匿名加载 ``User.addresses`` 集合的连接：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users JOIN addresses
            ON users.id = addresses.user_id
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address
        ['spongebob']

    从上面可以看到，我们使用 :meth:`_sql.Select.join` 来提供我们希望在后续查询标准中使用的 JOIN 子句，而使用 :func:`_orm.joinedload` 仅关注加载每个 ``User`` 结果的 ``User.addresses`` 集合。在这种情况下，两个连接看起来可能是多余的——确实是多余的。如果我们只想使用一个 JOIN 来同时加载集合和进行排序，我们可以使用 :func:`.contains_eager` 选项，稍后在 :ref:`contains_eager` 中介绍。但为了理解 :func:`joinedload` 的工作原理，考虑一下我们是否在 **过滤** 某个特定的 ``Address``：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .filter(Address.email_address == "someaddress@foo.com")
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users JOIN addresses
            ON users.id = addresses.user_id
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ? AND addresses.email_address = ?
        ['spongebob', 'someaddress@foo.com']

    上面，我们可以看到这两个 JOIN 的角色非常不同。一个将精确匹配一行，即连接 ``User`` 和 ``Address``，其中 ``Address.email_address=='someaddress@foo.com'``。另一个 LEFT OUTER JOIN 将匹配 *所有* 与 ``User`` 相关的 ``Address`` 行，仅用于填充那些返回的 ``User.addresses`` 集合。

    通过将 :func:`_orm.joinedload` 更改为另一种加载方式，我们可以完全独立地改变集合的加载方式，而不会影响检索实际 ``User`` 行所使用的 SQL。下面我们将 :func:`_orm.joinedload` 更改为 :func:`.selectinload`：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(selectinload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .filter(Address.email_address == "someaddress@foo.com")
        ... )
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        JOIN addresses ON users.id = addresses.user_id
        WHERE
            users.name = ?
            AND addresses.email_address = ?
        ['spongebob', 'someaddress@foo.com']
        # ... selectinload() 会发出一个 SELECT 语句
        # 来加载所有的地址记录 ...


    在使用连接急加载时，如果查询包含影响外部行的修饰符（例如使用 DISTINCT、LIMIT、OFFSET 或等效操作符），完成的语句会首先被包装在一个子查询中，专门用于连接急加载的 JOIN 将应用到该子查询中。SQLAlchemy 的连接急加载不遗余力地确保它不会影响查询的最终结果，只会改变集合和相关对象的加载方式，无论查询的格式如何。

    .. seealso::

        :ref:`contains_eager` - 使用 :func:`.contains_eager`


.. tab:: 英文

    Since joined eager loading seems to have many resemblances to the use of :meth:`_sql.Select.join`, it often produces confusion as to when and how it should be used.   It is critical to understand the distinction that while :meth:`_sql.Select.join` is used to alter the results of a query, :func:`_orm.joinedload` goes through great lengths to **not** alter the results of the query, and instead hide the effects of the rendered join to only allow for related objects to be present.

    The philosophy behind loader strategies is that any set of loading schemes can be applied to a particular query, and *the results don't change* - only the number of SQL statements required to fully load related objects and collections changes. A particular query might start out using all lazy loads.   After using it in context, it might be revealed that particular attributes or collections are always accessed, and that it would be more efficient to change the loader strategy for these.   The strategy can be changed with no other modifications to the query, the results will remain identical, but fewer SQL statements would be emitted. In theory (and pretty much in practice), nothing you can do to the :class:`_sql.Select` would make it load a different set of primary or related objects based on a change in loader strategy.

    How :func:`joinedload` in particular achieves this result of not impacting entity rows returned in any way is that it creates an anonymous alias of the joins it adds to your query, so that they can't be referenced by other parts of the query.   For example, the query below uses :func:`_orm.joinedload` to create a LEFT OUTER JOIN from ``users`` to ``addresses``, however the ``ORDER BY`` added against ``Address.email_address`` is not valid - the ``Address`` entity is not named in the query:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import joinedload
        >>> stmt = (
        ...     select(User)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address   <-- this part is wrong !
        ['spongebob']

    Above, ``ORDER BY addresses.email_address`` is not valid since ``addresses`` is not in the FROM list.   The correct way to load the ``User`` records and order by email address is to use :meth:`_sql.Select.join`:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}
        SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        JOIN addresses ON users.id = addresses.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address
        ['spongebob']

    The statement above is of course not the same as the previous one, in that the columns from ``addresses`` are not included in the result at all.   We can add :func:`_orm.joinedload` back in, so that there are two joins - one is that which we are ordering on, the other is used anonymously to load the contents of the ``User.addresses`` collection:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .order_by(Address.email_address)
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users JOIN addresses
            ON users.id = addresses.user_id
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ?
        ORDER BY addresses.email_address
        ['spongebob']

    What we see above is that our usage of :meth:`_sql.Select.join` is to supply JOIN clauses we'd like to use in subsequent query criterion, whereas our usage of :func:`_orm.joinedload` only concerns itself with the loading of the ``User.addresses`` collection, for each ``User`` in the result. In this case, the two joins most probably appear redundant - which they are.  If we wanted to use just one JOIN for collection loading as well as ordering, we use the :func:`.contains_eager` option, described in :ref:`contains_eager` below.   But to see why :func:`joinedload` does what it does, consider if we were **filtering** on a particular ``Address``:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(joinedload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .filter(Address.email_address == "someaddress@foo.com")
        ... )
        >>> result = session.scalars(stmt).unique().all()
        {execsql}SELECT
            addresses_1.id AS addresses_1_id,
            addresses_1.email_address AS addresses_1_email_address,
            addresses_1.user_id AS addresses_1_user_id,
            users.id AS users_id, users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users JOIN addresses
            ON users.id = addresses.user_id
        LEFT OUTER JOIN addresses AS addresses_1
            ON users.id = addresses_1.user_id
        WHERE users.name = ? AND addresses.email_address = ?
        ['spongebob', 'someaddress@foo.com']

    Above, we can see that the two JOINs have very different roles.  One will match exactly one row, that of the join of ``User`` and ``Address`` where ``Address.email_address=='someaddress@foo.com'``. The other LEFT OUTER JOIN will match *all* ``Address`` rows related to ``User``, and is only used to populate the ``User.addresses`` collection, for those ``User`` objects that are returned.

    By changing the usage of :func:`_orm.joinedload` to another style of loading, we can change how the collection is loaded completely independently of SQL used to retrieve the actual ``User`` rows we want.  Below we change :func:`_orm.joinedload` into :func:`.selectinload`:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(User)
        ...     .join(User.addresses)
        ...     .options(selectinload(User.addresses))
        ...     .filter(User.name == "spongebob")
        ...     .filter(Address.email_address == "someaddress@foo.com")
        ... )
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        JOIN addresses ON users.id = addresses.user_id
        WHERE
            users.name = ?
            AND addresses.email_address = ?
        ['spongebob', 'someaddress@foo.com']
        # ... selectinload() emits a SELECT in order
        # to load all address records ...


    When using joined eager loading, if the query contains a modifier that impacts the rows returned externally to the joins, such as when using DISTINCT, LIMIT, OFFSET or equivalent, the completed statement is first wrapped inside a subquery, and the joins used specifically for joined eager loading are applied to the subquery.   SQLAlchemy's joined eager loading goes the extra mile, and then ten miles further, to absolutely ensure that it does not affect the end result of the query, only the way collections and related objects are loaded, no matter what the format of the query is.

    .. seealso::

        :ref:`contains_eager` - using :func:`.contains_eager`

.. _selectin_eager_loading:

选择 IN 加载
-----------------

Select IN loading

.. tab:: 中文

    在大多数情况下，选择 IN 加载是急加载对象集合的最简单和高效的方式。选择 IN 急加载不可行的唯一情况是，当模型使用复合主键，并且后端数据库不支持使用 IN 的元组时，目前包括 SQL Server 在内的数据库就不支持此功能。

    "Select IN" 急加载通过向 :paramref:`_orm.relationship.lazy` 传递 ``"selectin"`` 参数或使用 :func:`.selectinload` 加载器选项来提供。这种加载方式会发出一个 SELECT 语句，引用父对象的主键值，或者在多对一关系的情况下，引用子对象的主键值，放入 IN 子句中，以加载相关的关联对象：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import selectinload
        >>> stmt = (
        ...     select(User)
        ...     .options(selectinload(User.addresses))
        ...     .filter(or_(User.name == "spongebob", User.name == "ed"))
        ... )
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.name = ? OR users.name = ?
        ('spongebob', 'ed')
        SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
        FROM addresses
        WHERE addresses.user_id IN (?, ?)
        (5, 7)

    上面，第二个 SELECT 语句引用了 ``addresses.user_id IN (5, 7)`` ，其中的 "5" 和 "7" 是之前加载的两个 ``User`` 对象的主键值；在一批对象完全加载后，它们的主键值被注入到第二个 SELECT 的 ``IN`` 子句中。由于 ``User`` 和 ``Address`` 之间的关系具有简单的主连接条件，并且 ``User`` 的主键值可以从 ``Address.user_id`` 中派生，因此语句中没有任何连接或子查询。

    对于简单的多对一加载，也不需要 JOIN，因为使用了父对象的外键值：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Address).options(selectinload(Address.user))
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
            FROM addresses
        SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.id IN (?, ?)
        (1, 2)

    .. tip::

        这里的 "简单" 指的是 :paramref:`_orm.relationship.primaryjoin` 条件表示 "一" 方主键与 "多" 方的外键之间的等值比较，没有其他附加的条件。

    选择 IN 加载也支持多对多关系，目前它会连接三个表，匹配两边的行。

    关于这种加载方式，需要注意的几点包括：

    * 该策略会为最多 500 个父主键值发出一个 SELECT 语句，因为主键被渲染到 SQL 语句中的一个大的 IN 表达式中。一些数据库（如 Oracle 数据库）对 IN 表达式的大小有硬性限制，总的来说，SQL 字符串的大小不应过大。

    * 由于 "selectin" 加载依赖于 IN，因此对于使用复合主键的映射，它必须使用 IN 的 "元组" 形式，即 ``WHERE (table.column_a, table.column_b) IN ((?, ?), (?, ?), (?, ?))``。SQL Server 当前不支持这种语法，而 SQLite 至少需要版本 3.15 才能支持。SQLAlchemy 并没有特殊逻辑来提前检查哪些平台支持此语法；如果在不支持的平台上运行，数据库会立即返回错误。SQLAlchemy 直接执行 SQL 并让其失败的一个优点是，如果某个数据库开始支持此语法，它将无需对 SQLAlchemy 进行任何更改（正如 SQLite 的情况一样）。


.. tab:: 英文

    In most cases, selectin loading is the most simple and efficient way to eagerly load collections of objects.  The only scenario in which selectin eager loading is not feasible is when the model is using composite primary keys, and the backend database does not support tuples with IN, which currently includes SQL Server.

    "Select IN" eager loading is provided using the ``"selectin"`` argument to :paramref:`_orm.relationship.lazy` or by using the :func:`.selectinload` loader option.   This style of loading emits a SELECT that refers to the primary key values of the parent object, or in the case of a many-to-one relationship to the those of the child objects, inside of an IN clause, in order to load related associations:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import selectinload
        >>> stmt = (
        ...     select(User)
        ...     .options(selectinload(User.addresses))
        ...     .filter(or_(User.name == "spongebob", User.name == "ed"))
        ... )
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.name = ? OR users.name = ?
        ('spongebob', 'ed')
        SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
        FROM addresses
        WHERE addresses.user_id IN (?, ?)
        (5, 7)

    Above, the second SELECT refers to ``addresses.user_id IN (5, 7)``, where the "5" and "7" are the primary key values for the previous two ``User`` objects loaded; after a batch of objects are completely loaded, their primary key values are injected into the ``IN`` clause for the second SELECT. Because the relationship between ``User`` and ``Address`` has a simple primary join condition and provides that the primary key values for ``User`` can be derived from ``Address.user_id``, the statement has no joins or subqueries at all.

    For simple many-to-one loads, a JOIN is also not needed as the foreign key value from the parent object is used:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Address).options(selectinload(Address.user))
        >>> result = session.scalars(stmt).all()
        {execsql}SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id
            FROM addresses
        SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.id IN (?, ?)
        (1, 2)

    .. tip::

        by "simple" we mean that the :paramref:`_orm.relationship.primaryjoin` condition expresses an equality comparison between the primary key of the "one" side and a straight foreign key of the "many" side, without any additional criteria.

    Select IN loading also supports many-to-many relationships, where it currently will JOIN across all three tables to match rows from one side to the other.

    Things to know about this kind of loading include:

    * The strategy emits a SELECT for up to 500 parent primary key values at a time, as the primary keys are rendered into a large IN expression in the SQL statement.  Some databases like Oracle Database have a hard limit on how large an IN expression can be, and overall the size of the SQL string shouldn't be arbitrarily large.

    * As "selectin" loading relies upon IN, for a mapping with composite primary keys, it must use the "tuple" form of IN, which looks like ``WHERE (table.column_a, table.column_b) IN ((?, ?), (?, ?), (?, ?))``. This syntax is not currently supported on SQL Server and for SQLite requires at least version 3.15.  There is no special logic in SQLAlchemy to check ahead of time which platforms support this syntax or not; if run against a non-supporting platform, the database will return an error immediately.   An advantage to SQLAlchemy just running the SQL out for it to fail is that if a particular database does start supporting this syntax, it will work without any changes to SQLAlchemy (as was the case with SQLite).


.. _subquery_eager_loading:

子查询预/急加载
----------------------

Subquery Eager Loading

.. tab:: 中文

    .. legacy:: 

        :func:`_orm.subqueryload` 急加载器目前大多已经过时，已经被 :func:`_orm.selectinload` 策略取代，后者设计更加简洁，功能更灵活，支持如 :ref:`Yield Per <orm_queryguide_yield_per>` 等特性，并且在大多数情况下发出的 SQL 语句更为高效。由于 :func:`_orm.subqueryload` 依赖于重新解释原始的 SELECT 语句，因此在处理非常复杂的源查询时，它可能无法高效地工作。

        :func:`_orm.subqueryload` 仍然可能对于某些特定场景有用，尤其是在急加载包含复合主键的集合对象时，特别是在 Microsoft SQL Server 后端，后者目前仍不支持 "tuple IN" 语法。

    子查询加载与选择 IN 急加载相似，然而发出的 SELECT 语句是从原始语句派生的，其查询结构比选择 IN 急加载更复杂。

    子查询急加载通过向 :paramref:`_orm.relationship.lazy` 传递 ``"subquery"`` 参数或使用 :func:`.subqueryload` 加载器选项来提供。

    子查询急加载的操作是针对每个要加载的关系发出一个第二个 SELECT 语句，这个 SELECT 语句涉及所有结果对象一次性加载。此 SELECT 语句引用了原始的 SELECT 语句，原始查询被包装在一个子查询中，以便我们检索到主对象返回的主键列表，然后将其与所有集合成员链接，以一次性加载它们：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import subqueryload
        >>> stmt = select(User).options(subqueryload(User.addresses)).filter_by(name="spongebob")
        >>> results = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.name = ?
        ('spongebob',)
        SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (
            SELECT users.id AS users_id
            FROM users
            WHERE users.name = ?) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id, addresses.id
        ('spongebob',)

    关于这种加载方式需要了解的几点包括：

    * "subquery" 加载策略发出的 SELECT 语句，与 "selectin" 不同，需要使用子查询，并且会继承原始查询中存在的性能限制。子查询本身也可能会因为使用的数据库具体情况而产生性能问题。

    * "subquery" 加载要求一些特殊的排序规则才能正确工作。使用 :func:`.subqueryload` 并且查询包含限制性修饰符（如 :meth:`_sql.Select.limit` 或 :meth:`_sql.Select.offset`）时， **应始终** 使用 :meth:`_sql.Select.order_by` 对唯一的列（例如主键）进行排序，以确保 :func:`.subqueryload` 发出的附加查询与父查询使用相同的排序。否则，内查询可能返回错误的行：

        # 错误，没有 ORDER BY
        stmt = select(User).options(subqueryload(User.addresses).limit(1))

        # 错误，如果 User.name 不是唯一的
        stmt = select(User).options(subqueryload(User.addresses)).order_by(User.name).limit(1)

        # 正确
        stmt = (
            select(User)
            .options(subqueryload(User.addresses))
            .order_by(User.name, User.id)
            .limit(1)
        )

    .. seealso::

        :ref:`faq_subqueryload_limit_sort` - 详细示例

    * "subquery" 加载在用于多层次深度的急加载时会遇到额外的性能/复杂性问题，因为子查询会被重复嵌套。

    * "subquery" 加载与 :ref:`Yield Per <orm_queryguide_yield_per>` 提供的 "批处理" 加载不兼容，无论是对于集合关系还是标量关系。

    由于以上原因，应该优先选择 "selectin" 策略，而不是 "subquery"。

    .. seealso::

        :ref:`selectin_eager_loading`


.. tab:: 英文

    .. legacy:: 
        
        The :func:`_orm.subqueryload` eager loader is mostly legacy at this point, superseded by the :func:`_orm.selectinload` strategy which is of much simpler design, more flexible with features such as :ref:`Yield Per <orm_queryguide_yield_per>`, and emits more efficient SQL statements in most cases.   As :func:`_orm.subqueryload` relies upon re-interpreting the original SELECT statement, it may fail to work efficiently when given very complex source queries.

        :func:`_orm.subqueryload` may continue to be useful for the specific case of an eager loaded collection for objects that use composite primary keys, on the Microsoft SQL Server backend that continues to not have support for the "tuple IN" syntax.

    Subquery loading is similar in operation to selectin eager loading, however the SELECT statement which is emitted is derived from the original statement, and has a more complex query structure as that of selectin eager loading.

    Subquery eager loading is provided using the ``"subquery"`` argument to :paramref:`_orm.relationship.lazy` or by using the :func:`.subqueryload` loader option.

    The operation of subquery eager loading is to emit a second SELECT statement for each relationship to be loaded, across all result objects at once. This SELECT statement refers to the original SELECT statement, wrapped inside of a subquery, so that we retrieve the same list of primary keys for the primary object being returned, then link that to the sum of all the collection members to load them at once:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import subqueryload
        >>> stmt = select(User).options(subqueryload(User.addresses)).filter_by(name="spongebob")
        >>> results = session.scalars(stmt).all()
        {execsql}SELECT
            users.id AS users_id,
            users.name AS users_name,
            users.fullname AS users_fullname,
            users.nickname AS users_nickname
        FROM users
        WHERE users.name = ?
        ('spongebob',)
        SELECT
            addresses.id AS addresses_id,
            addresses.email_address AS addresses_email_address,
            addresses.user_id AS addresses_user_id,
            anon_1.users_id AS anon_1_users_id
        FROM (
            SELECT users.id AS users_id
            FROM users
            WHERE users.name = ?) AS anon_1
        JOIN addresses ON anon_1.users_id = addresses.user_id
        ORDER BY anon_1.users_id, addresses.id
        ('spongebob',)


    Things to know about this kind of loading include:

    * The SELECT statement emitted by the "subquery" loader strategy, unlike that of "selectin", requires a subquery, and will inherit whatever performance limitations are present in the original query.  The subquery itself may also incur performance penalties based on the specifics of the database in use.

    * "subquery" loading imposes some special ordering requirements in order to work correctly.  A query which makes use of :func:`.subqueryload` in conjunction with a limiting modifier such as :meth:`_sql.Select.limit`, or :meth:`_sql.Select.offset` should **always** include :meth:`_sql.Select.order_by` against unique column(s) such as the primary key, so that the additional queries emitted by :func:`.subqueryload` include the same ordering as used by the parent query.  Without it, there is a chance that the inner query could return the wrong rows::

        # incorrect, no ORDER BY
        stmt = select(User).options(subqueryload(User.addresses).limit(1))

        # incorrect if User.name is not unique
        stmt = select(User).options(subqueryload(User.addresses)).order_by(User.name).limit(1)

        # correct
        stmt = (
            select(User)
            .options(subqueryload(User.addresses))
            .order_by(User.name, User.id)
            .limit(1)
        )

    .. seealso::

        :ref:`faq_subqueryload_limit_sort` - detailed example


    * "subquery" loading also incurs additional performance / complexity issues when used on a many-levels-deep eager load, as subqueries will be nested repeatedly.

    * "subquery" loading is not compatible with the "batched" loading supplied by :ref:`Yield Per <orm_queryguide_yield_per>`, both for collection and scalar relationships.

    For the above reasons, the "selectin" strategy should be preferred over "subquery".

    .. seealso::

        :ref:`selectin_eager_loading`




.. _what_kind_of_loading:

使用哪种加载？
-----------------------------

What Kind of Loading to Use ?

.. tab:: 中文

    通常，选择使用哪种加载方式取决于优化 SQL 执行次数、SQL 复杂度和获取数据量之间的权衡。

    **一对多 / 多对多 集合** - :func:`_orm.selectinload` 通常是最佳的加载策略。它发出一个额外的 SELECT 语句，尽量减少使用的表数，保持原始语句不受影响，并且对任何类型的源查询都非常灵活。它的主要限制是在使用复合主键的表时，后端不支持 "tuple IN" 语法，当前包括 SQL Server 和非常旧的 SQLite 版本；所有其他支持的后端都支持该语法。

    **多对一** - :func:`_orm.joinedload` 策略是最通用的策略。在特殊情况下，如果相关值的数量非常少，:func:`_orm.immediateload` 策略也可能有用，因为该策略会从本地 :class:`_orm.Session` 获取对象，而不发出任何 SQL 查询，前提是相关对象已经存在。

.. tab:: 英文

    Which type of loading to use typically comes down to optimizing the tradeoff between number of SQL executions, complexity of SQL emitted, and amount of data fetched.


    **One to Many / Many to Many Collection** - The :func:`_orm.selectinload` is generally the best loading strategy to use.  It emits an additional SELECT that uses as few tables as possible, leaving the original statement unaffected, and is most flexible for any kind of originating query.   Its only major limitation is when using a table with composite primary keys on a backend that does not support "tuple IN", which currently includes SQL Server and very old SQLite versions; all other included backends support it.

    **Many to One** - The :func:`_orm.joinedload` strategy is the most general purpose strategy. In special cases, the :func:`_orm.immediateload` strategy may also be useful, if there are a very small number of potential related values, as this strategy will fetch the object from the local :class:`_orm.Session` without emitting any SQL if the related object is already present.



多态预加载
-------------------------

Polymorphic Eager Loading

.. tab:: 中文

    可以按急加载的每个基础指定多态选项。有关此方法的示例，请参阅 :ref:`eagerloading_polymorphic_subtypes` 部分，介绍了 :meth:`.PropComparator.of_type` 方法与 :func:`_orm.with_polymorphic` 函数的结合使用。

.. tab:: 英文

    Specification of polymorphic options on a per-eager-load basis is supported. See the section :ref:`eagerloading_polymorphic_subtypes` for examples of the :meth:`.PropComparator.of_type` method in conjunction with the :func:`_orm.with_polymorphic` function.

.. _wildcard_loader_strategies:

通配符加载策略
---------------------------

Wildcard Loading Strategies

.. tab:: 中文

    每个 :func:`_orm.joinedload`、:func:`.subqueryload`、:func:`.lazyload`、:func:`.selectinload` 和 :func:`.raiseload` 都可以用于设置特定查询的默认 :func:`_orm.relationship` 加载样式，影响所有未在语句中另行指定的 :func:`_orm.relationship` 映射属性。可以通过将字符串 ``'*'`` 作为参数传递给这些选项来启用此功能：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(MyClass).options(lazyload("*"))

    上述代码中的 ``lazyload('*')`` 选项将会覆盖查询中所有 :func:`_orm.relationship` 构造的 ``lazy`` 设置，除非这些构造使用了 ``lazy='write_only'`` 或 ``lazy='dynamic'``。

    如果某些关系指定了 ``lazy='joined'`` 或 ``lazy='selectin'``，例如，使用 ``lazyload('*')`` 会强制所有这些关系使用 ``'select'`` 加载，即当每个属性被访问时发出一个 SELECT 语句。

    此选项不会覆盖查询中声明的加载器选项，如 :func:`.joinedload`、:func:`.selectinload` 等。下面的查询仍然会对 ``widget`` 关系使用连接加载（joined loading）：

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload
        from sqlalchemy.orm import joinedload

        stmt = select(MyClass).options(lazyload("*"), joinedload(MyClass.widget))

    虽然上述对 :func:`.joinedload` 的指令无论是在 :func:`.lazyload` 选项之前还是之后出现，都会生效，但如果多个选项中都包含了 ``"*"``，则最后一个选项将生效。


.. tab:: 英文

    Each of :func:`_orm.joinedload`, :func:`.subqueryload`, :func:`.lazyload`, :func:`.selectinload`, and :func:`.raiseload` can be used to set the default style of :func:`_orm.relationship` loading for a particular query, affecting all :func:`_orm.relationship` -mapped attributes not otherwise specified in the statement.   This feature is available by passing the string ``'*'`` as the argument to any of these options::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload

        stmt = select(MyClass).options(lazyload("*"))

    Above, the ``lazyload('*')`` option will supersede the ``lazy`` setting of all :func:`_orm.relationship` constructs in use for that query, with the exception of those that use ``lazy='write_only'`` or ``lazy='dynamic'``.

    If some relationships specify ``lazy='joined'`` or ``lazy='selectin'``, for example, using ``lazyload('*')`` will unilaterally cause all those relationships to use ``'select'`` loading, e.g. emit a SELECT statement when each attribute is accessed.

    The option does not supersede loader options stated in the query, such as :func:`.joinedload`, :func:`.selectinload`, etc.  The query below will still use joined loading for the ``widget`` relationship::

        from sqlalchemy import select
        from sqlalchemy.orm import lazyload
        from sqlalchemy.orm import joinedload

        stmt = select(MyClass).options(lazyload("*"), joinedload(MyClass.widget))

    While the instruction for :func:`.joinedload` above will take place regardless of whether it appears before or after the :func:`.lazyload` option, if multiple options that each included ``"*"`` were passed, the last one will take effect.

.. _orm_queryguide_relationship_per_entity_wildcard:

每个实体通配符加载策略
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Per-Entity Wildcard Loading Strategies

.. tab:: 中文

    通配符加载策略的一个变种是能够在每个实体基础上设置加载策略。例如，如果查询 ``User`` 和 ``Address``，我们可以通过首先应用 :class:`_orm.Load` 对象，然后指定 ``*`` 作为链式选项，来指示 ``Address`` 上的所有关系使用懒加载，同时不影响 ``User`` 的加载策略：

        from sqlalchemy import select
        from sqlalchemy.orm import Load

        stmt = select(User, Address).options(Load(Address).lazyload("*"))

    上述代码中，``Address`` 上的所有关系将被设置为懒加载。

.. tab:: 英文

    A variant of the wildcard loader strategy is the ability to set the strategy on a per-entity basis.  For example, if querying for ``User`` and ``Address``, we can instruct all relationships on ``Address`` to use lazy loading, while leaving the loader strategies for ``User`` unaffected, by first applying the :class:`_orm.Load` object, then specifying the ``*`` as a chained option::

        from sqlalchemy import select
        from sqlalchemy.orm import Load

        stmt = select(User, Address).options(Load(Address).lazyload("*"))

    Above, all relationships on ``Address`` will be set to a lazy load.

.. _joinedload_and_join:

.. _contains_eager:

将显式连接/语句路由到预加载的集合
-----------------------------------------------------------------

Routing Explicit Joins/Statements into Eagerly Loaded Collections

.. tab:: 中文

    :func:`_orm.joinedload()` 的行为是自动创建连接，使用匿名别名作为目标，结果会被路由到加载对象的集合和标量引用中。通常情况下，查询已经包含了表示特定集合或标量引用的必要连接，而 ``joinedload`` 特性所添加的连接是多余的——但你仍然希望这些集合/引用被填充。

    为此，SQLAlchemy 提供了 :func:`_orm.contains_eager` 选项。该选项的使用方式与 :func:`_orm.joinedload()` 相同，只不过它假定 :class:`_sql.Select` 对象将显式地包含适当的连接，通常使用类似 :meth:`_sql.Select.join` 的方法。下面，我们指定了 ``User`` 和 ``Address`` 之间的连接，并额外将其作为 ``User.addresses`` 的急加载基础：

        from sqlalchemy.orm import contains_eager

        stmt = select(User).join(User.addresses).options(contains_eager(User.addresses))

    如果 "急加载" 部分的语句是 "别名" 的，那么路径应该使用 :meth:`.PropComparator.of_type` 来指定，这样就可以传递具体的 :func:`_orm.aliased` 构造：

    .. sourcecode:: python+sql

        # 使用 Address 实体的别名
        adalias = aliased(Address)

        # 构建一个预期 "addresses" 结果的语句

        stmt = (
            select(User)
            .outerjoin(User.addresses.of_type(adalias))
            .options(contains_eager(User.addresses.of_type(adalias)))
        )

        # 正常获取结果
        r = session.scalars(stmt).unique().all()
        {execsql}SELECT
            users.user_id AS users_user_id,
            users.user_name AS users_user_name,
            adalias.address_id AS adalias_address_id,
            adalias.user_id AS adalias_user_id,
            adalias.email_address AS adalias_email_address,
            (...其他列...)
        FROM users
        LEFT OUTER JOIN email_addresses AS email_addresses_1
        ON users.user_id = email_addresses_1.user_id

    作为 :func:`.contains_eager` 参数传递的路径需要是从起始实体开始的完整路径。例如，如果我们正在加载 ``Users->orders->Order->items->Item``，则该选项的使用方式如下：

        stmt = select(User).options(contains_eager(User.orders).contains_eager(Order.items))


.. tab:: 英文

    The behavior of :func:`_orm.joinedload()` is such that joins are created automatically, using anonymous aliases as targets, the results of which are routed into collections and scalar references on loaded objects. It is often the case that a query already includes the necessary joins which represent a particular collection or scalar reference, and the joins added by the joinedload feature are redundant - yet you'd still like the collections/references to be populated.

    For this SQLAlchemy supplies the :func:`_orm.contains_eager` option. This option is used in the same manner as the :func:`_orm.joinedload()` option except it is assumed that the :class:`_sql.Select` object will explicitly include the appropriate joins, typically using methods like :meth:`_sql.Select.join`. Below, we specify a join between ``User`` and ``Address`` and additionally establish this as the basis for eager loading of ``User.addresses``::

        from sqlalchemy.orm import contains_eager

        stmt = select(User).join(User.addresses).options(contains_eager(User.addresses))

    If the "eager" portion of the statement is "aliased", the path should be specified using :meth:`.PropComparator.of_type`, which allows the specific :func:`_orm.aliased` construct to be passed:

    .. sourcecode:: python+sql

        # use an alias of the Address entity
        adalias = aliased(Address)

        # construct a statement which expects the "addresses" results

        stmt = (
            select(User)
            .outerjoin(User.addresses.of_type(adalias))
            .options(contains_eager(User.addresses.of_type(adalias)))
        )

        # get results normally
        r = session.scalars(stmt).unique().all()
        {execsql}SELECT
            users.user_id AS users_user_id,
            users.user_name AS users_user_name,
            adalias.address_id AS adalias_address_id,
            adalias.user_id AS adalias_user_id,
            adalias.email_address AS adalias_email_address,
            (...other columns...)
        FROM users
        LEFT OUTER JOIN email_addresses AS email_addresses_1
        ON users.user_id = email_addresses_1.user_id

    The path given as the argument to :func:`.contains_eager` needs to be a full path from the starting entity. For example if we were loading ``Users->orders->Order->items->Item``, the option would be used as::

        stmt = select(User).options(contains_eager(User.orders).contains_eager(Order.items))

使用 contains_eager() 加载自定义过滤的集合结果
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using contains_eager() to load a custom-filtered collection result

.. tab:: 中文

    当我们使用 :func:`.contains_eager` 时， *我们* 自行构建用于填充集合的 SQL。由此自然可以推导出，我们可以选择 **修改** 集合预期存储的值，方法是编写 SQL 来加载集合或标量属性的子集。

    .. tip::  

        SQLAlchemy 现在有一种 **更简单的方式来做到这一点**，通过允许将 WHERE 条件直接添加到加载器选项中，如 :func:`_orm.joinedload` 和 :func:`_orm.selectinload`，使用 :meth:`.PropComparator.and_`。有关示例，请参见 :ref:`loader_option_criteria` 部分。

        如果相关集合需要使用比简单 WHERE 子句更复杂的 SQL 条件或修饰符进行查询，那么这里描述的技术仍然适用。

    例如，我们可以加载一个 ``User`` 对象，并仅将特定的地址急加载到它的 ``.addresses`` 集合中，通过过滤联接数据并使用 :func:`_orm.contains_eager` 路由，同时使用 :ref:`orm_queryguide_populate_existing` 来确保任何已经加载的集合会被覆盖：

        stmt = (
            select(User)
            .join(User.addresses)
            .filter(Address.email_address.like("%@aol.com"))
            .options(contains_eager(User.addresses))
            .execution_options(populate_existing=True)
        )

    上述查询将仅加载包含至少一个 ``Address`` 对象（该对象的 ``email`` 字段包含子字符串 ``'aol.com'``）的 ``User`` 对象； ``User.addresses`` 集合将 **仅** 包含这些 ``Address`` 条目，而 **不** 包含实际上与集合关联的其他 ``Address`` 条目。

    .. tip::  

        在所有情况下，SQLAlchemy ORM **不会覆盖已加载的属性和集合**，除非明确告诉它这么做。由于存在 :term:`identity map`，通常情况下，ORM 查询返回的对象实际上已经存在并已加载到内存中。因此，在使用 :func:`_orm.contains_eager` 以替代方式填充集合时，通常最好使用 :ref:`orm_queryguide_populate_existing`，如上所示，以便用新数据刷新已加载的集合。``populate_existing`` 选项将重置 **所有** 已存在的属性，包括待处理的更改，因此在使用它之前，确保所有数据已刷新。使用默认行为的 :class:`_orm.Session`（包括 :ref:`autoflush <session_flushing>`）已足够。

    .. note::  

        我们使用 :func:`_orm.contains_eager` 加载的自定义集合不是“粘性的”；也就是说，下次加载该集合时，它将使用其通常的默认内容。如果对象已过期（默认会话设置下，当调用 :meth:`.Session.commit`、:meth:`.Session.rollback` 方法时，或者使用 :meth:`.Session.expire_all` 或 :meth:`.Session.expire` 方法时），该集合将被重新加载。

    .. seealso::

        :ref:`loader_option_criteria` - 现代 API，允许直接在任何关系加载器选项中使用 WHERE 条件


.. tab:: 英文

    When we use :func:`.contains_eager`, *we* are constructing ourselves the SQL that will be used to populate collections.  From this, it naturally follows that we can opt to **modify** what values the collection is intended to store, by writing our SQL to load a subset of elements for collections or scalar attributes.

    .. tip::  
        
        SQLAlchemy now has a **much simpler way to do this**, by allowing WHERE criteria to be added directly to loader options such as :func:`_orm.joinedload` and :func:`_orm.selectinload` using :meth:`.PropComparator.and_`.  See the section :ref:`loader_option_criteria` for examples.

        The techniques described here still apply if the related collection is to be queried using SQL criteria or modifiers more complex than a simple WHERE clause.


    As an example, we can load a ``User`` object and eagerly load only particular addresses into its ``.addresses`` collection by filtering the joined data, routing it using :func:`_orm.contains_eager`, also using :ref:`orm_queryguide_populate_existing` to ensure any already-loaded collections are overwritten::

        stmt = (
            select(User)
            .join(User.addresses)
            .filter(Address.email_address.like("%@aol.com"))
            .options(contains_eager(User.addresses))
            .execution_options(populate_existing=True)
        )

    The above query will load only ``User`` objects which contain at least ``Address`` object that contains the substring ``'aol.com'`` in its ``email`` field; the ``User.addresses`` collection will contain **only** these ``Address`` entries, and *not* any other ``Address`` entries that are in fact associated with the collection.

    .. tip::  
        
        In all cases, the SQLAlchemy ORM does **not overwrite already loaded attributes and collections** unless told to do so.   As there is an :term:`identity map` in use, it is often the case that an ORM query is returning objects that were in fact already present and loaded in memory. Therefore, when using :func:`_orm.contains_eager` to populate a collection in an alternate way, it is usually a good idea to use :ref:`orm_queryguide_populate_existing` as illustrated above so that an already-loaded collection is refreshed with the new data. The ``populate_existing`` option will reset **all** attributes that were already present, including pending changes, so make sure all data is flushed before using it.   Using the :class:`_orm.Session` with its default behavior of :ref:`autoflush <session_flushing>` is sufficient.

    .. note::   
        
        The customized collection we load using :func:`_orm.contains_eager` is not "sticky"; that is, the next time this collection is loaded, it will be loaded with its usual default contents.   The collection is subject to being reloaded if the object is expired, which occurs whenever the :meth:`.Session.commit`, :meth:`.Session.rollback` methods are used assuming default session settings, or the :meth:`.Session.expire_all` or :meth:`.Session.expire` methods are used.

    .. seealso::

        :ref:`loader_option_criteria` - modern API allowing WHERE criteria directly within any relationship loader option


关系加载器 API
-----------------------

Relationship Loader API

.. tab:: 中文

.. tab:: 英文

.. autofunction:: contains_eager

.. autofunction:: defaultload

.. autofunction:: immediateload

.. autofunction:: joinedload

.. autofunction:: lazyload

.. autoclass:: sqlalchemy.orm.Load
    :members:
    :inherited-members: Generative

.. autofunction:: noload

.. autofunction:: raiseload

.. autofunction:: selectinload

.. autofunction:: subqueryload
