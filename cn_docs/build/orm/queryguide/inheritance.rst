.. highlight:: pycon+sql
.. |prev| replace:: :doc:`select`
.. |next| replace:: :doc:`dml`

.. include:: queryguide_nav_include.rst

.. doctest-include _inheritance_setup.rst

.. _inheritance_loading_toplevel:


.. currentmodule:: sqlalchemy.orm

.. _loading_joined_inheritance:

为继承映射编写 SELECT 语句
==================================================

Writing SELECT statements for Inheritance Mappings

.. tab:: 中文

    .. admonition:: 关于本文档

        本节使用了配置为 :ref:`ORM 继承 <inheritance_toplevel>` 功能的 ORM 映射，详述在 :ref:`inheritance_toplevel`。重点将放在 :ref:`joined_inheritance` 上，因为这是最复杂的 ORM 查询案例。

        :doc:`查看本页的 ORM 设置 <_inheritance_setup>`。

.. tab:: 英文

    .. admonition:: About this Document

        This section makes use of ORM mappings configured using
        the :ref:`ORM Inheritance <inheritance_toplevel>` feature,
        described at :ref:`inheritance_toplevel`.  The emphasis will be on
        :ref:`joined_inheritance` as this is the most intricate ORM querying
        case.

        :doc:`View the ORM setup for this page <_inheritance_setup>`.

从基类与特定子类中进行选择
------------------------------------------------------

SELECTing from the base class vs. specific sub-classes

.. tab:: 中文

    针对联合继承体系中的某个类构造的 SELECT 语句将查询映射到该类的表以及所有存在的父类表，并使用 JOIN 将它们连接在一起。查询会返回请求类型的对象以及该类型的任何子类型的对象，并通过每一行中的 :term:`discriminator` 值来确定正确的类型。下面的查询针对的是 ``Employee`` 的子类 ``Manager``，因此结果中只包含类型为 ``Manager`` 的对象::

        >>> from sqlalchemy import select
        >>> stmt = select(Manager).order_by(Manager.id)
        >>> managers = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT manager.id, employee.id AS id_1, employee.name, employee.type, employee.company_id, manager.manager_name
        FROM employee JOIN manager ON employee.id = manager.id ORDER BY manager.id
        [...] ()
        {stop}>>> print(managers)
        [Manager('Mr. Krabs')]

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    当 SELECT 语句针对的是继承体系中的基类时，默认行为是仅包含该类的表，不使用 JOIN。和所有情况一样，:term:`discriminator` 列被用于区分请求的不同子类型，因此返回的对象可能是任何子类的实例。返回对象只会填充与基类表对应的属性，而与子类表相关的属性将处于未加载状态，首次访问时会自动加载。子属性的加载方式可以配置为更“积极”的方式，这将在本节稍后部分讨论。

    下面的例子中，我们构造了一个针对 ``Employee`` 父类的查询。这意味着结果集中可能包含 ``Manager``、``Engineer`` 和 ``Employee`` 类型的对象::

        >>> from sqlalchemy import select
        >>> stmt = select(Employee).order_by(Employee.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    如上所示， ``Manager`` 和 ``Engineer`` 的附加表没有包含在 SELECT 中，因此返回的对象尚未包含这些表中的数据，例如 ``Manager`` 类的 ``.manager_name`` 属性和 ``Engineer`` 类的 ``.engineer_info`` 属性。这些属性最初处于 :term:`expired` 状态，在首次访问时会通过 :term:`lazy loading`（延迟加载）自动填充::

        >>> mr_krabs = objects[0]
        >>> print(mr_krabs.manager_name)
        {execsql}SELECT manager.manager_name AS manager_manager_name
        FROM manager
        WHERE ? = manager.id
        [...] (1,)
        {stop}Eugene H. Krabs

    如果加载了大量对象，而应用程序又需要访问子类特有的属性，那么上述延迟加载行为将不可取，因为这属于 :term:`N plus one` 问题的一个例子 —— 每行数据都会触发一条额外的 SQL 查询。这种额外的 SQL 会影响性能，并且与某些方法（如 :ref:`asyncio <asyncio_toplevel>`）不兼容。此外，在我们对 ``Employee`` 对象进行查询时，由于查询仅基于基类表，我们无法在 SQL 中添加与子类 ``Manager`` 或 ``Engineer`` 的特定属性相关的筛选条件。接下来的两个小节将介绍两个构造方式，分别通过不同方式解决上述两个问题，即 :func:`_orm.selectin_polymorphic` 加载选项和 :func:`_orm.with_polymorphic` 实体构造器。


.. tab:: 英文

    A SELECT statement constructed against a class in a joined inheritance hierarchy will query against the table to which the class is mapped, as well as any super-tables present, using JOIN to link them together. The query would then return objects that are of that requested type as well as any sub-types of the requested type,  using the :term:`discriminator` value in each row to determine the correct type. The query below is established against the ``Manager`` subclass of ``Employee``, which then returns a result that will contain only objects of type ``Manager``::

        >>> from sqlalchemy import select
        >>> stmt = select(Manager).order_by(Manager.id)
        >>> managers = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT manager.id, employee.id AS id_1, employee.name, employee.type, employee.company_id, manager.manager_name
        FROM employee JOIN manager ON employee.id = manager.id ORDER BY manager.id
        [...] ()
        {stop}>>> print(managers)
        [Manager('Mr. Krabs')]

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    When the SELECT statement is against the base class in the hierarchy, the default behavior is that only that class' table will be included in the rendered SQL and JOIN will not be used. As in all cases, the :term:`discriminator` column is used to distinguish between different requested sub-types, which then results in objects of any possible sub-type being returned. The objects returned will have attributes corresponding to the base table populated, and attributes corresponding to sub-tables will start in an un-loaded state, loading automatically when accessed. The loading of sub-attributes is configurable to be more "eager" in a variety of ways, discussed later in this section.

    The example below creates a query against the ``Employee`` superclass. This indicates that objects of any type, including ``Manager``, ``Engineer``, and ``Employee``, may be within the result set::

        >>> from sqlalchemy import select
        >>> stmt = select(Employee).order_by(Employee.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    Above, the additional tables for ``Manager`` and ``Engineer`` were not included in the SELECT, which means that the returned objects will not yet contain data represented from those tables, in this example the ``.manager_name`` attribute of the ``Manager`` class as well as the ``.engineer_info`` attribute of the ``Engineer`` class.  These attributes start out in the :term:`expired` state, and will automatically populate themselves when first accessed using :term:`lazy loading`::

        >>> mr_krabs = objects[0]
        >>> print(mr_krabs.manager_name)
        {execsql}SELECT manager.manager_name AS manager_manager_name
        FROM manager
        WHERE ? = manager.id
        [...] (1,)
        {stop}Eugene H. Krabs

    This lazy load behavior is not desirable if a large number of objects have been loaded, in the case that the consuming application will need to be accessing subclass-specific attributes, as this would be an example of the :term:`N plus one` problem that emits additional SQL per row.  This additional SQL can impact performance and also be incompatible with approaches such as using :ref:`asyncio <asyncio_toplevel>`.  Additionally, in our query for ``Employee`` objects, since the query is against the base table only, we did not have a way to add SQL criteria involving subclass-specific attributes in terms of ``Manager`` or ``Engineer``. The next two sections detail two constructs that provide solutions to these two issues in different ways, the :func:`_orm.selectin_polymorphic` loader option and the :func:`_orm.with_polymorphic` entity construct.


.. _polymorphic_selectin:

使用 selectin_polymorphic()
----------------------------

Using selectin_polymorphic()

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    为了解决在访问子类属性时的性能问题，可以使用 :func:`_orm.selectin_polymorphic` 加载策略，在多个对象上预先 :term:`eagerly load`（预加载）这些附加属性。该加载选项的工作方式类似于 :func:`_orm.selectinload` 关系加载策略，它会对继承体系中的每个子表额外发出一条 SELECT 语句，通过 ``IN`` 子句根据主键查询附加行。

    :func:`_orm.selectin_polymorphic` 的参数是被查询的基类实体，后面跟一个该实体子类的序列，用于指定在加载过程中应当加载这些子类的特定属性::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> loader_opt = selectin_polymorphic(Employee, [Manager, Engineer])

    然后将 :func:`_orm.selectin_polymorphic` 作为加载选项传入 :class:`.Select` 的 :meth:`.Select.options` 方法中。以下示例展示了如何使用 :func:`_orm.selectin_polymorphic` 来预加载 ``Manager`` 和 ``Engineer`` 子类本地的列::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> loader_opt = selectin_polymorphic(Employee, [Manager, Engineer])
        >>> stmt = select(Employee).order_by(Employee.id).options(loader_opt)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        SELECT manager.id AS manager_id, employee.id AS employee_id,
        employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id,
        employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    上面的示例展示了为了预加载 ``Engineer.engineer_info`` 和 ``Manager.manager_name`` 这些附加属性而触发的两条额外 SELECT 语句。现在我们可以在不触发额外 SQL 的情况下访问这些已加载对象的子类属性::

        >>> print(objects[0].manager_name)
        Eugene H. Krabs

    .. tip:: 
        
        :func:`_orm.selectin_polymorphic` 加载选项目前尚未对一个优化点进行处理：即在后续的两个“预加载”查询中，其实并不需要包含基类 ``employee`` 表。因此，在上面的示例中我们看到从 ``employee`` 到 ``manager`` 和 ``engineer`` 的 JOIN 操作，即使 ``employee`` 的列已经加载完毕。相比之下，:func:`_orm.selectinload` 关系加载策略在这方面更加智能，能够在不需要的情况下省略 JOIN。

.. tab:: 英文

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    To address the issue of performance when accessing attributes on subclasses, the :func:`_orm.selectin_polymorphic` loader strategy may be used to :term:`eagerly load` these additional attributes up front across many objects at once.  This loader option works in a similar fashion as the :func:`_orm.selectinload` relationship loader strategy to emit an additional SELECT statement against each sub-table for objects loaded in the hierarchy, using ``IN`` to query for additional rows based on primary key.

    :func:`_orm.selectin_polymorphic` accepts as its arguments the base entity that is being queried, followed by a sequence of subclasses of that entity for which their specific attributes should be loaded for incoming rows::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> loader_opt = selectin_polymorphic(Employee, [Manager, Engineer])

    The :func:`_orm.selectin_polymorphic` construct is then used as a loader option, passing it to the :meth:`.Select.options` method of :class:`.Select`. The example illustrates the use of :func:`_orm.selectin_polymorphic` to eagerly load columns local to both the ``Manager`` and ``Engineer`` subclasses::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> loader_opt = selectin_polymorphic(Employee, [Manager, Engineer])
        >>> stmt = select(Employee).order_by(Employee.id).options(loader_opt)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        SELECT manager.id AS manager_id, employee.id AS employee_id,
        employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id,
        employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    The above example illustrates two additional SELECT statements being emitted in order to eagerly fetch additional attributes such as ``Engineer.engineer_info`` as well as ``Manager.manager_name``.   We can now access these sub-attributes on the objects that were loaded without any additional SQL statements being emitted::

        >>> print(objects[0].manager_name)
        Eugene H. Krabs

    .. tip:: 
        
        The :func:`_orm.selectin_polymorphic` loader option does not yet optimize for the fact that the base ``employee`` table does not need to be included in the second two "eager load" queries; hence in the example above we see a JOIN from ``employee`` to ``manager`` and ``engineer``, even though columns from ``employee`` are already loaded.  This is in contrast to the :func:`_orm.selectinload` relationship strategy which is more sophisticated in this regard and can factor out the JOIN when not needed.

.. _polymorphic_selectin_as_loader_option_target:

将 selectin_polymorphic() 应用于现有的即时加载
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Applying selectin_polymorphic() to an existing eager load

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    除了可以将 :func:`_orm.selectin_polymorphic` 作为语句中顶层实体的加载选项，我们也可以在已有加载操作的目标上使用 :func:`_orm.selectin_polymorphic`。在我们的 :doc:`设置 <_inheritance_setup>` 映射中，存在一个父级实体 ``Company``，其 ``Company.employees`` 是指向 ``Employee`` 实体的 :func:`_orm.relationship`。我们可以如下示例那样，对 ``Company`` 实体进行 SELECT 查询，并通过链式加载选项 :meth:`.Load.selectin_polymorphic` 来预加载所有 ``Employee`` 对象及其子类的所有属性。在这种形式下，第一个参数由前一个加载选项（这里是 :func:`_orm.selectinload`）隐式提供，因此我们只需要传入希望加载的子类列表即可::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Company).options(
        ...     selectinload(Company.employees).selectin_polymorphic([Manager, Engineer])
        ... )
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     print(f"employees: {company.employees}")
        {execsql}BEGIN (implicit)
        SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type
        FROM employee
        WHERE employee.company_id IN (?)
        [...] (1,)
        SELECT manager.id AS manager_id, employee.id AS employee_id,
        employee.type AS employee_type,
        manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id,
        employee.type AS employee_type,
        engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}company: Krusty Krab
        employees: [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    .. seealso::

        :ref:`eagerloading_polymorphic_subtypes` - 展示了使用 :func:`_orm.with_polymorphic` 实现上述等效示例的方法


.. tab:: 英文

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    In addition to :func:`_orm.selectin_polymorphic` being specified as an option for a top-level entity loaded by a statement, we may also indicate :func:`_orm.selectin_polymorphic` on the target of an existing load. As our :doc:`setup <_inheritance_setup>` mapping includes a parent ``Company`` entity with a ``Company.employees`` :func:`_orm.relationship` referring to ``Employee`` entities, we may illustrate a SELECT against the ``Company`` entity that eagerly loads all ``Employee`` objects as well as all attributes on their subtypes as follows, by applying :meth:`.Load.selectin_polymorphic` as a chained loader option; in this form, the first argument is implicit from the previous loader option (in this case :func:`_orm.selectinload`), so we only indicate the additional target subclasses we wish to load::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Company).options(
        ...     selectinload(Company.employees).selectin_polymorphic([Manager, Engineer])
        ... )
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     print(f"employees: {company.employees}")
        {execsql}BEGIN (implicit)
        SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type
        FROM employee
        WHERE employee.company_id IN (?)
        [...] (1,)
        SELECT manager.id AS manager_id, employee.id AS employee_id,
        employee.type AS employee_type,
        manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id,
        employee.type AS employee_type,
        engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}company: Krusty Krab
        employees: [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    .. seealso::

        :ref:`eagerloading_polymorphic_subtypes` - illustrates the equivalent example as above using :func:`_orm.with_polymorphic` instead


.. _polymorphic_selectin_w_loader_options:

将加载器选项应用于 selectin_polymorphic 加载的子类
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Applying loader options to the subclasses loaded by selectin_polymorphic

.. tab:: 中文

    :func:`_orm.selectin_polymorphic` 所发出的 SELECT 语句本身也是 ORM 语句，因此我们也可以在其中添加其他加载选项（例如在 :ref:`orm_queryguide_relationship_loaders` 中记录的那些），这些选项可以引用特定的子类。这些选项应当作为 :func:`_orm.selectin_polymorphic` 的 **并列(siblings)** 选项添加，也就是说应在 :meth:`_sql.select.options` 中以逗号分隔列出。

    例如，如果我们假设 ``Manager`` 映射器存在一个到名为 ``Paperwork`` 的实体的 :ref:`一对多关系 <relationship_patterns_o2m>`，我们就可以将 :func:`_orm.selectin_polymorphic` 与 :func:`_orm.selectinload` 结合使用，对所有 ``Manager`` 对象预加载该集合，同时也对 ``Manager`` 对象的子属性进行预加载::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> stmt = (
        ...     select(Employee)
        ...     .order_by(Employee.id)
        ...     .options(
        ...         selectin_polymorphic(Employee, [Manager, Engineer]),
        ...         selectinload(Manager.paperwork),
        ...     )
        ... )
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        SELECT manager.id AS manager_id, employee.id AS employee_id, employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT paperwork.manager_id AS paperwork_manager_id, paperwork.id AS paperwork_id, paperwork.document_name AS paperwork_document_name
        FROM paperwork
        WHERE paperwork.manager_id IN (?)
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id, employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}>>> print(objects[0])
        Manager('Mr. Krabs')
        >>> print(objects[0].paperwork)
        [Paperwork('Secret Recipes'), Paperwork('Krabby Patty Orders')]


.. tab:: 英文

    The SELECT statements emitted by :func:`_orm.selectin_polymorphic` are themselves ORM statements, so we may also add other loader options (such as those documented at :ref:`orm_queryguide_relationship_loaders`) that refer to specific subclasses.   These options should be applied as **siblings** to a :func:`_orm.selectin_polymorphic` option, that is, comma separated within :meth:`_sql.select.options`.

    For example, if we considered that the ``Manager`` mapper had a :ref:`one to many <relationship_patterns_o2m>` relationship to an entity called ``Paperwork``, we could combine the use of :func:`_orm.selectin_polymorphic` and :func:`_orm.selectinload` to eagerly load this collection on all ``Manager`` objects, where the sub-attributes of ``Manager`` objects were also themselves eagerly loaded::

        >>> from sqlalchemy.orm import selectin_polymorphic
        >>> stmt = (
        ...     select(Employee)
        ...     .order_by(Employee.id)
        ...     .options(
        ...         selectin_polymorphic(Employee, [Manager, Engineer]),
        ...         selectinload(Manager.paperwork),
        ...     )
        ... )
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.company_id
        FROM employee ORDER BY employee.id
        [...] ()
        SELECT manager.id AS manager_id, employee.id AS employee_id, employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT paperwork.manager_id AS paperwork_manager_id, paperwork.id AS paperwork_id, paperwork.document_name AS paperwork_document_name
        FROM paperwork
        WHERE paperwork.manager_id IN (?)
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id, employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}>>> print(objects[0])
        Manager('Mr. Krabs')
        >>> print(objects[0].paperwork)
        [Paperwork('Secret Recipes'), Paperwork('Krabby Patty Orders')]

.. _polymorphic_selectin_as_loader_option_target_plus_opts:

当 selectin_polymorphic 本身是子选项时应用加载器选项
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applying loader options when selectin_polymorphic is itself a sub-option

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    .. versionadded:: 2.0.21

    前一节展示了 :func:`_orm.selectin_polymorphic` 与 :func:`_orm.selectinload` 作为 **并列选项** 的用法，它们都在一次对 :meth:`_sql.select.options` 的调用中使用。如果目标实体是通过父关系加载的（如 :ref:`polymorphic_selectin_as_loader_option_target` 中的例子），我们可以通过 :meth:`_orm.Load.options` 方法对该父关系应用子选项，从而实现这一“并列”模式，参见 :ref:`orm_queryguide_relationship_sub_options`。下面我们结合这两个例子，对 ``Company.employees`` 进行加载，同时加载 ``Manager`` 和 ``Engineer`` 类的属性，并对 ``Manager.paperwork`` 属性进行预加载::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Company).options(
        ...     selectinload(Company.employees).options(
        ...         selectin_polymorphic(Employee, [Manager, Engineer]),
        ...         selectinload(Manager.paperwork),
        ...     )
        ... )
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     for employee in company.employees:
        ...         if isinstance(employee, Manager):
        ...             print(f"manager: {employee.name} paperwork: {employee.paperwork}")
        {execsql}BEGIN (implicit)
        SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type
        FROM employee
        WHERE employee.company_id IN (?)
        [...] (1,)
        SELECT manager.id AS manager_id, employee.id AS employee_id, employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT paperwork.manager_id AS paperwork_manager_id, paperwork.id AS paperwork_id, paperwork.document_name AS paperwork_document_name
        FROM paperwork
        WHERE paperwork.manager_id IN (?)
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id, employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}company: Krusty Krab
        manager: Mr. Krabs paperwork: [Paperwork('Secret Recipes'), Paperwork('Krabby Patty Orders')]


.. tab:: 英文

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    .. versionadded:: 2.0.21

    The previous section illustrated :func:`_orm.selectin_polymorphic` and :func:`_orm.selectinload` used as sibling options, both used within a single call to :meth:`_sql.select.options`.   If the target entity is one that is already being loaded from a parent relationship, as in the example at :ref:`polymorphic_selectin_as_loader_option_target`, we can apply this "sibling" pattern using the :meth:`_orm.Load.options` method that applies sub-options to a parent, as illustrated at :ref:`orm_queryguide_relationship_sub_options`.  Below we combine the two examples to load ``Company.employees``, also loading the attributes for the ``Manager`` and ``Engineer`` classes, as well as eagerly loading the ```Manager.paperwork``` attribute::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(Company).options(
        ...     selectinload(Company.employees).options(
        ...         selectin_polymorphic(Employee, [Manager, Engineer]),
        ...         selectinload(Manager.paperwork),
        ...     )
        ... )
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     for employee in company.employees:
        ...         if isinstance(employee, Manager):
        ...             print(f"manager: {employee.name} paperwork: {employee.paperwork}")
        {execsql}BEGIN (implicit)
        SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type
        FROM employee
        WHERE employee.company_id IN (?)
        [...] (1,)
        SELECT manager.id AS manager_id, employee.id AS employee_id, employee.type AS employee_type, manager.manager_name AS manager_manager_name
        FROM employee JOIN manager ON employee.id = manager.id
        WHERE employee.id IN (?) ORDER BY employee.id
        [...] (1,)
        SELECT paperwork.manager_id AS paperwork_manager_id, paperwork.id AS paperwork_id, paperwork.document_name AS paperwork_document_name
        FROM paperwork
        WHERE paperwork.manager_id IN (?)
        [...] (1,)
        SELECT engineer.id AS engineer_id, employee.id AS employee_id, employee.type AS employee_type, engineer.engineer_info AS engineer_engineer_info
        FROM employee JOIN engineer ON employee.id = engineer.id
        WHERE employee.id IN (?, ?) ORDER BY employee.id
        [...] (2, 3)
        {stop}company: Krusty Krab
        manager: Mr. Krabs paperwork: [Paperwork('Secret Recipes'), Paperwork('Krabby Patty Orders')]


在映射器上配置 selectin_polymorphic()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring selectin_polymorphic() on mappers

.. tab:: 中文

    可以在特定的 mapper 上配置 :func:`_orm.selectin_polymorphic` 的行为，使其在默认情况下生效，方法是在每个子类中使用 :paramref:`_orm.Mapper.polymorphic_load` 参数，并将其值设置为 ``"selectin"``。下面的示例演示了如何在 ``Engineer`` 和 ``Manager`` 子类中使用该参数：

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {"polymorphic_identity": "employee", "polymorphic_on": type}


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "selectin",
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "selectin",
                "polymorphic_identity": "manager",
            }

    根据上述映射配置，当针对 ``Employee`` 类执行 SELECT 语句时，将自动使用 ``selectin_polymorphic(Employee, [Engineer, Manager])`` 作为加载选项。


.. tab:: 英文

    The behavior of :func:`_orm.selectin_polymorphic` may be configured on specific mappers so that it takes place by default, by using the :paramref:`_orm.Mapper.polymorphic_load` parameter, using the value ``"selectin"`` on a per-subclass basis.  The example below illustrates the use of this parameter within ``Engineer`` and ``Manager`` subclasses:

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {"polymorphic_identity": "employee", "polymorphic_on": type}


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "selectin",
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "selectin",
                "polymorphic_identity": "manager",
            }

    With the above mapping, SELECT statements against the ``Employee`` class will automatically assume the use of ``selectin_polymorphic(Employee, [Engineer, Manager])`` as a loader option when the statement is emitted.

.. _with_polymorphic:

使用 with_polymorphic()
------------------------

Using with_polymorphic()

.. tab:: 中文

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    与仅影响对象加载的 :func:`_orm.selectin_polymorphic` 不同，:func:`_orm.with_polymorphic` 构造会影响多态结构中 SQL 查询的生成方式，通常表现为对每个子表进行一系列的 LEFT OUTER JOIN。这种连接结构称为 **polymorphic selectable（多态可选项）**。通过提供一个同时包含多个子表的视图，:func:`_orm.with_polymorphic` 允许编写跨多个继承类的 SELECT 语句，并支持基于各个子表添加筛选条件。

    :func:`_orm.with_polymorphic` 本质上是 :func:`_orm.aliased` 构造的一种特殊形式。它接受的参数形式与 :func:`_orm.selectin_polymorphic` 类似：首先是被查询的基类实体，随后是一组希望为其加载具体属性的子类列表::

        >>> from sqlalchemy.orm import with_polymorphic
        >>> employee_poly = with_polymorphic(Employee, [Engineer, Manager])

    为了表示所有子类都应包括在内，:func:`_orm.with_polymorphic` 还接受字符串 ``"*"``，可替代类列表以表示“所有子类”（注意：这一写法尚不被 :func:`_orm.selectin_polymorphic` 支持）::

        >>> employee_poly = with_polymorphic(Employee, "*")

    以下示例演示了与上一节相同的操作，用于一次性加载 ``Manager`` 和 ``Engineer`` 的所有列::

        >>> stmt = select(employee_poly).order_by(employee_poly.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id,
        manager.id AS id_1, manager.manager_name, engineer.id AS id_2, engineer.engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id ORDER BY employee.id
        [...] ()
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    和 :func:`_orm.selectin_polymorphic` 一样，子类的属性在加载时就已完成::

        >>> print(objects[0].manager_name)
        Eugene H. Krabs

    由于 :func:`_orm.with_polymorphic` 默认生成的 selectable 使用的是 LEFT OUTER JOIN，从数据库性能的角度来看，这种方式不如 :func:`_orm.selectin_polymorphic` 那种基于每个子表分别发出简单 JOIN 的 SELECT 查询方式更优化。

.. tab:: 英文

    ..  Setup code, not for display


        >>> session.close()
        ROLLBACK

    In contrast to :func:`_orm.selectin_polymorphic` which affects only the loading of objects, the :func:`_orm.with_polymorphic` construct affects how the SQL query for a polymorphic structure is rendered, most commonly as a series of LEFT OUTER JOINs to each of the included sub-tables. This join structure is known as the **polymorphic selectable**. By providing for a view of several sub-tables at once, :func:`_orm.with_polymorphic` offers a means of writing a SELECT statement across several inherited classes at once with the ability to add filtering criteria based on individual sub-tables.

    :func:`_orm.with_polymorphic` is essentially a special form of the :func:`_orm.aliased` construct. It accepts as its arguments a similar form to that of :func:`_orm.selectin_polymorphic`, which is the base entity that is being queried, followed by a sequence of subclasses of that entity for which their specific attributes should be loaded for incoming rows::

        >>> from sqlalchemy.orm import with_polymorphic
        >>> employee_poly = with_polymorphic(Employee, [Engineer, Manager])

    In order to indicate that all subclasses should be part of the entity, :func:`_orm.with_polymorphic` will also accept the string ``"*"``, which may be passed in place of the sequence of classes to indicate all classes (note this is not yet supported by :func:`_orm.selectin_polymorphic`)::

        >>> employee_poly = with_polymorphic(Employee, "*")

    The example below illustrates the same operation as illustrated in the previous section, to load all columns for ``Manager`` and ``Engineer`` at once::

        >>> stmt = select(employee_poly).order_by(employee_poly.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type, employee.company_id,
        manager.id AS id_1, manager.manager_name, engineer.id AS id_2, engineer.engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id ORDER BY employee.id
        [...] ()
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    As is the case with :func:`_orm.selectin_polymorphic`, attributes on subclasses are already loaded::

        >>> print(objects[0].manager_name)
        Eugene H. Krabs

    As the default selectable produced by :func:`_orm.with_polymorphic` uses LEFT OUTER JOIN, from a database point of view the query is not as well optimized as the approach that :func:`_orm.selectin_polymorphic` takes, with simple SELECT statements using only JOINs emitted on a per-table basis.


.. _with_polymorphic_subclass_attributes:

使用 with_polymorphic() 过滤子类属性
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filtering Subclass Attributes with with_polymorphic()

.. tab:: 中文

    :func:`_orm.with_polymorphic` 构造通过包含子类的命名空间，使我们能够访问这些子类映射器上的属性。前一节中创建的 ``employee_poly`` 构造包含名为 ``.Engineer`` 和 ``.Manager`` 的属性，它们提供了对 ``Engineer`` 和 ``Manager`` 的命名空间引用，用于多态 SELECT 查询中。

    在下面的示例中，我们可以使用 :func:`_sql.or_` 构造来同时对两个子类添加筛选条件::

        >>> from sqlalchemy import or_
        >>> employee_poly = with_polymorphic(Employee, [Engineer, Manager])
        >>> stmt = (
        ...     select(employee_poly)
        ...     .where(
        ...         or_(
        ...             employee_poly.Manager.manager_name == "Eugene H. Krabs",
        ...             employee_poly.Engineer.engineer_info
        ...             == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ...     .order_by(employee_poly.id)
        ... )
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.company_id, manager.id AS id_1,
        manager.manager_name, engineer.id AS id_2, engineer.engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        WHERE manager.manager_name = ? OR engineer.engineer_info = ?
        ORDER BY employee.id
        [...] ('Eugene H. Krabs', 'Senior Customer Engagement Engineer')
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('Squidward')]


.. tab:: 英文

    The :func:`_orm.with_polymorphic` construct makes available the attributes on the included subclass mappers, by including namespaces that allow references to subclasses.   The ``employee_poly`` construct created in the previous section includes attributes named ``.Engineer`` and ``.Manager`` which provide the namespace for ``Engineer`` and ``Manager`` in terms of the polymorphic SELECT.   In the example below, we can use the :func:`_sql.or_` construct to create criteria against both classes at once::

        >>> from sqlalchemy import or_
        >>> employee_poly = with_polymorphic(Employee, [Engineer, Manager])
        >>> stmt = (
        ...     select(employee_poly)
        ...     .where(
        ...         or_(
        ...             employee_poly.Manager.manager_name == "Eugene H. Krabs",
        ...             employee_poly.Engineer.engineer_info
        ...             == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ...     .order_by(employee_poly.id)
        ... )
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.company_id, manager.id AS id_1,
        manager.manager_name, engineer.id AS id_2, engineer.engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        WHERE manager.manager_name = ? OR engineer.engineer_info = ?
        ORDER BY employee.id
        [...] ('Eugene H. Krabs', 'Senior Customer Engagement Engineer')
        {stop}>>> print(objects)
        [Manager('Mr. Krabs'), Engineer('Squidward')]

.. _with_polymorphic_aliasing:

使用 with_polymorphic 进行别名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using aliasing with with_polymorphic

.. tab:: 中文

    :func:`_orm.with_polymorphic` 构造作为 :func:`_orm.aliased` 的一种特殊形式，也提供了 :func:`_orm.aliased` 的基本特性，即对多态查询结构本身进行“别名化（aliasing）”。具体来说，这意味着可以在同一个语句中同时使用两个或更多的 :func:`_orm.with_polymorphic` 实体，它们引用的是同一个类层次结构。

    为了在联合继承（joined inheritance）映射中使用这一特性，我们通常需要传入两个参数，:paramref:`_orm.with_polymorphic.aliased` 以及 :paramref:`_orm.with_polymorphic.flat`。参数 :paramref:`_orm.with_polymorphic.aliased` 表示多态结构应使用唯一的别名来引用；参数 :paramref:`_orm.with_polymorphic.flat` 则是针对默认的 LEFT OUTER JOIN 多态结构而言，它表示语句中应使用更优化的别名处理方式。

    为了演示这一特性，下面的示例生成一个 SELECT 查询，查询两个不同的多态实体：一个是 ``Employee`` 联结 ``Engineer``，另一个是 ``Employee`` 联结 ``Manager``。由于这两个多态实体在其多态结构中都包含基础的 ``employee`` 表，因此必须应用别名以区分这两个不同上下文中的表。两个多态实体被视为两个独立的表，因此通常需要通过某种方式将它们联结在一起。如下所示，我们通过 ``company_id`` 列将它们连接，并在 ``Employee`` / ``Manager`` 实体上施加了附加的限制条件::

        >>> manager_employee = with_polymorphic(Employee, [Manager], aliased=True, flat=True)
        >>> engineer_employee = with_polymorphic(Employee, [Engineer], aliased=True, flat=True)
        >>> stmt = (
        ...     select(manager_employee, engineer_employee)
        ...     .join(
        ...         engineer_employee,
        ...         engineer_employee.company_id == manager_employee.company_id,
        ...     )
        ...     .where(
        ...         or_(
        ...             manager_employee.name == "Mr. Krabs",
        ...             manager_employee.Manager.manager_name == "Eugene H. Krabs",
        ...         )
        ...     )
        ...     .order_by(engineer_employee.name, manager_employee.name)
        ... )
        >>> for manager, engineer in session.execute(stmt):
        ...     print(f"{manager} {engineer}")
        {execsql}SELECT
        employee_1.id, employee_1.name, employee_1.type, employee_1.company_id,
        manager_1.id AS id_1, manager_1.manager_name,
        employee_2.id AS id_2, employee_2.name AS name_1, employee_2.type AS type_1,
        employee_2.company_id AS company_id_1, engineer_1.id AS id_3, engineer_1.engineer_info
        FROM employee AS employee_1
        LEFT OUTER JOIN manager AS manager_1 ON employee_1.id = manager_1.id
        JOIN
        (employee AS employee_2 LEFT OUTER JOIN engineer AS engineer_1 ON employee_2.id = engineer_1.id)
        ON employee_2.company_id = employee_1.company_id
        WHERE employee_1.name = ? OR manager_1.manager_name = ?
        ORDER BY employee_2.name, employee_1.name
        [...] ('Mr. Krabs', 'Eugene H. Krabs')
        {stop}Manager('Mr. Krabs') Manager('Mr. Krabs')
        Manager('Mr. Krabs') Engineer('SpongeBob')
        Manager('Mr. Krabs') Engineer('Squidward')

    在上述示例中，:paramref:`_orm.with_polymorphic.flat` 的行为是：多态结构仍然以 LEFT OUTER JOIN 的形式连接它们各自的表，而这些表被赋予匿名的别名。此外还生成了一个右侧嵌套的 JOIN。

    如果省略 :paramref:`_orm.with_polymorphic.flat` 参数，则默认行为是将每个多态结构包装在子查询中，从而生成更冗长的形式::

        >>> manager_employee = with_polymorphic(Employee, [Manager], aliased=True)
        >>> engineer_employee = with_polymorphic(Employee, [Engineer], aliased=True)
        >>> stmt = (
        ...     select(manager_employee, engineer_employee)
        ...     .join(
        ...         engineer_employee,
        ...         engineer_employee.company_id == manager_employee.company_id,
        ...     )
        ...     .where(
        ...         or_(
        ...             manager_employee.name == "Mr. Krabs",
        ...             manager_employee.Manager.manager_name == "Eugene H. Krabs",
        ...         )
        ...     )
        ...     .order_by(engineer_employee.name, manager_employee.name)
        ... )
        >>> print(stmt)
        {printsql}SELECT anon_1.employee_id, anon_1.employee_name, anon_1.employee_type,
        anon_1.employee_company_id, anon_1.manager_id, anon_1.manager_manager_name, anon_2.employee_id AS employee_id_1,
        anon_2.employee_name AS employee_name_1, anon_2.employee_type AS employee_type_1,
        anon_2.employee_company_id AS employee_company_id_1, anon_2.engineer_id, anon_2.engineer_engineer_info
        FROM
        (SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type,
        employee.company_id AS employee_company_id,
        manager.id AS manager_id, manager.manager_name AS manager_manager_name
        FROM employee LEFT OUTER JOIN manager ON employee.id = manager.id) AS anon_1
        JOIN
        (SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type,
        employee.company_id AS employee_company_id, engineer.id AS engineer_id, engineer.engineer_info AS engineer_engineer_info
        FROM employee LEFT OUTER JOIN engineer ON employee.id = engineer.id) AS anon_2
        ON anon_2.employee_company_id = anon_1.employee_company_id
        WHERE anon_1.employee_name = :employee_name_2 OR anon_1.manager_manager_name = :manager_manager_name_1
        ORDER BY anon_2.employee_name, anon_1.employee_name

    上述形式在历史上对于某些不支持右侧嵌套 JOIN 的数据库后端具有更好的兼容性；此外，当 :func:`_orm.with_polymorphic` 所使用的“多态结构”并不是简单的表间 LEFT OUTER JOIN（例如使用了 :ref:`具体表继承 <concrete_inheritance>` 映射，或者其他替代性多态结构的情况）时，也可能更适合使用这种子查询形式。


.. tab:: 英文

    The :func:`_orm.with_polymorphic` construct, as a special case of :func:`_orm.aliased`, also provides the basic feature that :func:`_orm.aliased` does, which is that of "aliasing" of the polymorphic selectable itself. Specifically this means two or more :func:`_orm.with_polymorphic` entities, referring to the same class hierarchy, can be used at once in a single statement.

    To use this feature with a joined inheritance mapping, we typically want to pass two parameters, :paramref:`_orm.with_polymorphic.aliased` as well as :paramref:`_orm.with_polymorphic.flat`.  The :paramref:`_orm.with_polymorphic.aliased` parameter indicates that the polymorphic selectable should be referenced by an alias name that is unique to this construct.   The :paramref:`_orm.with_polymorphic.flat` parameter is specific to the default LEFT OUTER JOIN polymorphic selectable and indicates that a more optimized form of aliasing should be used in the statement.

    To illustrate this feature, the example below emits a SELECT for two separate polymorphic entities, ``Employee`` joined with ``Engineer``, and ``Employee`` joined with ``Manager``.  Since these two polymorphic entities will both be including the base ``employee`` table in their polymorphic selectable, aliasing must be applied in order to differentiate this table in its two different contexts. The two polymorphic entities are treated like two individual tables, and as such typically need to be joined with each other in some way, as illustrated below where the entities are joined on the ``company_id`` column along with some additional limiting criteria against the ``Employee`` / ``Manager`` entity::

        >>> manager_employee = with_polymorphic(Employee, [Manager], aliased=True, flat=True)
        >>> engineer_employee = with_polymorphic(Employee, [Engineer], aliased=True, flat=True)
        >>> stmt = (
        ...     select(manager_employee, engineer_employee)
        ...     .join(
        ...         engineer_employee,
        ...         engineer_employee.company_id == manager_employee.company_id,
        ...     )
        ...     .where(
        ...         or_(
        ...             manager_employee.name == "Mr. Krabs",
        ...             manager_employee.Manager.manager_name == "Eugene H. Krabs",
        ...         )
        ...     )
        ...     .order_by(engineer_employee.name, manager_employee.name)
        ... )
        >>> for manager, engineer in session.execute(stmt):
        ...     print(f"{manager} {engineer}")
        {execsql}SELECT
        employee_1.id, employee_1.name, employee_1.type, employee_1.company_id,
        manager_1.id AS id_1, manager_1.manager_name,
        employee_2.id AS id_2, employee_2.name AS name_1, employee_2.type AS type_1,
        employee_2.company_id AS company_id_1, engineer_1.id AS id_3, engineer_1.engineer_info
        FROM employee AS employee_1
        LEFT OUTER JOIN manager AS manager_1 ON employee_1.id = manager_1.id
        JOIN
        (employee AS employee_2 LEFT OUTER JOIN engineer AS engineer_1 ON employee_2.id = engineer_1.id)
        ON employee_2.company_id = employee_1.company_id
        WHERE employee_1.name = ? OR manager_1.manager_name = ?
        ORDER BY employee_2.name, employee_1.name
        [...] ('Mr. Krabs', 'Eugene H. Krabs')
        {stop}Manager('Mr. Krabs') Manager('Mr. Krabs')
        Manager('Mr. Krabs') Engineer('SpongeBob')
        Manager('Mr. Krabs') Engineer('Squidward')

    In the above example, the behavior of :paramref:`_orm.with_polymorphic.flat` is that the polymorphic selectables remain as a LEFT OUTER JOIN of their individual tables, which themselves are given anonymous alias names.  There is also a right-nested JOIN produced.

    When omitting the :paramref:`_orm.with_polymorphic.flat` parameter, the usual behavior is that each polymorphic selectable is enclosed within a subquery, producing a more verbose form::

        >>> manager_employee = with_polymorphic(Employee, [Manager], aliased=True)
        >>> engineer_employee = with_polymorphic(Employee, [Engineer], aliased=True)
        >>> stmt = (
        ...     select(manager_employee, engineer_employee)
        ...     .join(
        ...         engineer_employee,
        ...         engineer_employee.company_id == manager_employee.company_id,
        ...     )
        ...     .where(
        ...         or_(
        ...             manager_employee.name == "Mr. Krabs",
        ...             manager_employee.Manager.manager_name == "Eugene H. Krabs",
        ...         )
        ...     )
        ...     .order_by(engineer_employee.name, manager_employee.name)
        ... )
        >>> print(stmt)
        {printsql}SELECT anon_1.employee_id, anon_1.employee_name, anon_1.employee_type,
        anon_1.employee_company_id, anon_1.manager_id, anon_1.manager_manager_name, anon_2.employee_id AS employee_id_1,
        anon_2.employee_name AS employee_name_1, anon_2.employee_type AS employee_type_1,
        anon_2.employee_company_id AS employee_company_id_1, anon_2.engineer_id, anon_2.engineer_engineer_info
        FROM
        (SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type,
        employee.company_id AS employee_company_id,
        manager.id AS manager_id, manager.manager_name AS manager_manager_name
        FROM employee LEFT OUTER JOIN manager ON employee.id = manager.id) AS anon_1
        JOIN
        (SELECT employee.id AS employee_id, employee.name AS employee_name, employee.type AS employee_type,
        employee.company_id AS employee_company_id, engineer.id AS engineer_id, engineer.engineer_info AS engineer_engineer_info
        FROM employee LEFT OUTER JOIN engineer ON employee.id = engineer.id) AS anon_2
        ON anon_2.employee_company_id = anon_1.employee_company_id
        WHERE anon_1.employee_name = :employee_name_2 OR anon_1.manager_manager_name = :manager_manager_name_1
        ORDER BY anon_2.employee_name, anon_1.employee_name

    The above form historically has been more portable to backends that didn't necessarily have support for right-nested JOINs, and it additionally may be appropriate when the "polymorphic selectable" used by :func:`_orm.with_polymorphic` is not a simple LEFT OUTER JOIN of tables, as is the case when using mappings such as :ref:`concrete table inheritance <concrete_inheritance>` mappings as well as when using alternative polymorphic selectables in general.


.. _with_polymorphic_mapper_config:

在映射器上配置 with_polymorphic()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring with_polymorphic() on mappers

.. tab:: 中文

    与 :func:`_orm.selectin_polymorphic` 相似， :func:`_orm.with_polymorphic` 构造也支持映射器配置的版本，可以通过两种不同的方式进行配置：一种是在基类上使用 :paramref:`.mapper.with_polymorphic` 参数，另一种是使用更新版的方式，通过 :paramref:`_orm.Mapper.polymorphic_load` 参数在每个子类上进行配置，传递值 ``"inline"``。

    .. warning::

        对于联合继承（joined inheritance）映射，建议在查询中显式使用 :func:`_orm.with_polymorphic`，或者对于隐式的急切子类加载使用 :paramref:`_orm.Mapper.polymorphic_load` 和 ``"selectin"``，而不是使用本节描述的映射器级别的 :paramref:`.mapper.with_polymorphic` 参数。这个参数调用复杂的启发式方法，旨在重写 SELECT 语句中的 FROM 子句，可能会干扰复杂语句的构建，尤其是那些包含嵌套子查询且涉及同一映射实体的语句。

    例如，我们可以在 ``Employee`` 映射中使用 :paramref:`_orm.Mapper.polymorphic_load` 设置为 ``"inline"``，如下所示：

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {"polymorphic_identity": "employee", "polymorphic_on": type}


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "inline",
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "inline",
                "polymorphic_identity": "manager",
            }

    使用上述映射时，对 ``Employee`` 类的 SELECT 语句将在发出语句时自动假定使用 ``with_polymorphic(Employee, [Engineer, Manager])`` 作为主实体::

        print(select(Employee))
        {printsql}SELECT employee.id, employee.name, employee.type, engineer.id AS id_1,
        engineer.engineer_info, manager.id AS id_2, manager.manager_name
        FROM employee
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        LEFT OUTER JOIN manager ON employee.id = manager.id

    当使用映射器级别的 "with polymorphic" 时，查询也可以直接引用子类实体，这些子类实体隐式代表了多态查询中的联结表。如上所示，我们可以直接引用 ``Manager`` 和 ``Engineer``，并与默认的 ``Employee`` 实体进行配合使用::

        print(
            select(Employee).where(
                or_(Manager.manager_name == "x", Engineer.engineer_info == "y")
            )
        )
        {printsql}SELECT employee.id, employee.name, employee.type, engineer.id AS id_1,
        engineer.engineer_info, manager.id AS id_2, manager.manager_name
        FROM employee
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        LEFT OUTER JOIN manager ON employee.id = manager.id
        WHERE manager.manager_name = :manager_name_1
        OR engineer.engineer_info = :engineer_info_1

    然而，如果我们需要在不同的别名上下文中引用 ``Employee`` 实体或其子实体，我们将再次直接使用 :func:`_orm.with_polymorphic` 来定义这些别名实体，正如在 :ref:`with_polymorphic_aliasing` 中所示。

    为了对多态选择器（polymorphic selectable）进行更集中化的控制，可以使用映射器级别的遗留形式的多态控制，即在基类上配置 :paramref:`_orm.Mapper.with_polymorphic` 参数。此参数接受与 :func:`_orm.with_polymorphic` 构造相似的参数，但通常在联合继承映射中常用的是简单的星号（*），表示所有子表都应被 LEFT OUTER JOIN，如下所示：

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "with_polymorphic": "*",
                "polymorphic_on": type,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

    总体而言， :func:`_orm.with_polymorphic` 以及诸如 :paramref:`_orm.Mapper.with_polymorphic` 等选项所使用的 LEFT OUTER JOIN 格式，从 SQL 和数据库优化器的角度来看可能较为繁琐；对于联合继承映射中子类属性的常规加载，建议优先使用 :func:`_orm.selectin_polymorphic` 方法，或者在映射器级别通过将 :paramref:`_orm.Mapper.polymorphic_load` 设置为 ``"selectin"`` 来进行加载，仅在需要时才在每个查询中使用 :func:`_orm.with_polymorphic`。


.. tab:: 英文

    As is the case with :func:`_orm.selectin_polymorphic`, the :func:`_orm.with_polymorphic` construct also supports a mapper-configured version which may be configured in two different ways, either on the base class using the :paramref:`.mapper.with_polymorphic` parameter, or in a more modern form using the :paramref:`_orm.Mapper.polymorphic_load` parameter on a per-subclass basis, passing the value ``"inline"``.

    .. warning::

        For joined inheritance mappings, prefer explicit use of :func:`_orm.with_polymorphic` within queries, or for implicit eager subclass loading use :paramref:`_orm.Mapper.polymorphic_load` with ``"selectin"``, instead of using the mapper-level :paramref:`.mapper.with_polymorphic` parameter described in this section. This parameter invokes complex heuristics intended to rewrite the FROM clauses within SELECT statements that can interfere with construction of more complex statements, particularly those with nested subqueries that refer to the same mapped entity.

    For example, we may state our ``Employee`` mapping using :paramref:`_orm.Mapper.polymorphic_load` as ``"inline"`` as below:

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {"polymorphic_identity": "employee", "polymorphic_on": type}


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "inline",
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_load": "inline",
                "polymorphic_identity": "manager",
            }

    With the above mapping, SELECT statements against the ``Employee`` class will automatically assume the use of ``with_polymorphic(Employee, [Engineer, Manager])`` as the primary entity when the statement is emitted::

        print(select(Employee))
        {printsql}SELECT employee.id, employee.name, employee.type, engineer.id AS id_1,
        engineer.engineer_info, manager.id AS id_2, manager.manager_name
        FROM employee
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        LEFT OUTER JOIN manager ON employee.id = manager.id

    When using mapper-level "with polymorphic", queries can also refer to the subclass entities directly, where they implicitly represent the joined tables in the polymorphic query.  Above, we can freely refer to ``Manager`` and ``Engineer`` directly against the default ``Employee`` entity::

        print(
            select(Employee).where(
                or_(Manager.manager_name == "x", Engineer.engineer_info == "y")
            )
        )
        {printsql}SELECT employee.id, employee.name, employee.type, engineer.id AS id_1,
        engineer.engineer_info, manager.id AS id_2, manager.manager_name
        FROM employee
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        LEFT OUTER JOIN manager ON employee.id = manager.id
        WHERE manager.manager_name = :manager_name_1
        OR engineer.engineer_info = :engineer_info_1

    However, if we needed to refer to the ``Employee`` entity or its sub entities in separate, aliased contexts, we would again make direct use of :func:`_orm.with_polymorphic` to define these aliased entities as illustrated in :ref:`with_polymorphic_aliasing`.

    For more centralized control over the polymorphic selectable, the more legacy form of mapper-level polymorphic control may be used which is the :paramref:`_orm.Mapper.with_polymorphic` parameter, configured on the base class. This parameter accepts arguments that are comparable to the :func:`_orm.with_polymorphic` construct, however common use with a joined inheritance mapping is the plain asterisk, indicating all sub-tables should be LEFT OUTER JOINED, as in:

    .. sourcecode:: python

        class Employee(Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            type = mapped_column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "with_polymorphic": "*",
                "polymorphic_on": type,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            engineer_info = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, ForeignKey("employee.id"), primary_key=True)
            manager_name = mapped_column(String(30))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

    Overall, the LEFT OUTER JOIN format used by :func:`_orm.with_polymorphic` and by options such as :paramref:`_orm.Mapper.with_polymorphic` may be cumbersome from a SQL and database optimizer point of view; for general loading of subclass attributes in joined inheritance mappings, the :func:`_orm.selectin_polymorphic` approach, or its mapper level equivalent of setting :paramref:`_orm.Mapper.polymorphic_load` to ``"selectin"`` should likely be preferred, making use of :func:`_orm.with_polymorphic` on a per-query basis only as needed.

.. _inheritance_of_type:

连接到特定子类型或 with_polymorphic() 实体
------------------------------------------------------------

Joining to specific sub-types or with_polymorphic() entities

.. tab:: 中文

    由于 :func:`_orm.with_polymorphic` 实体是 :func:`_orm.aliased` 的特例，因此为了将多态实体作为联结的目标，特别是在使用 :func:`_orm.relationship` 构造作为 ON 子句时，我们使用与常规别名相同的技术，详细信息请参见 :ref:`orm_queryguide_joining_relationships_aliased`，最简洁的方法是使用 :meth:`_orm.PropComparator.of_type`。在下面的示例中，我们演示了从父级 ``Company`` 实体通过一对多关系 ``Company.employees`` 进行联结，该关系在 :doc:`setup <_inheritance_setup>` 中配置为链接到 ``Employee`` 对象，并使用 :func:`_orm.with_polymorphic` 实体作为目标::

        >>> employee_plus_engineer = with_polymorphic(Employee, [Engineer])
        >>> stmt = (
        ...     select(Company.name, employee_plus_engineer.name)
        ...     .join(Company.employees.of_type(employee_plus_engineer))
        ...     .where(
        ...         or_(
        ...             employee_plus_engineer.name == "SpongeBob",
        ...             employee_plus_engineer.Engineer.engineer_info
        ...             == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ... )
        >>> for company_name, emp_name in session.execute(stmt):
        ...     print(f"{company_name} {emp_name}")
        {execsql}SELECT company.name, employee.name AS name_1
        FROM company JOIN (employee LEFT OUTER JOIN engineer ON employee.id = engineer.id) ON company.id = employee.company_id
        WHERE employee.name = ? OR engineer.engineer_info = ?
        [...] ('SpongeBob', 'Senior Customer Engagement Engineer')
        {stop}Krusty Krab SpongeBob
        Krusty Krab Squidward

    更直接地， :meth:`_orm.PropComparator.of_type` 也用于任何类型的继承映射，以限制通过 :func:`_orm.relationship` 对象进行的联结，只针对特定的子类型。上述查询可以严格地用 ``Engineer`` 作为目标进行重写，如下所示::

        >>> stmt = (
        ...     select(Company.name, Engineer.name)
        ...     .join(Company.employees.of_type(Engineer))
        ...     .where(
        ...         or_(
        ...             Engineer.name == "SpongeBob",
        ...             Engineer.engineer_info == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ... )
        >>> for company_name, emp_name in session.execute(stmt):
        ...     print(f"{company_name} {emp_name}")
        {execsql}SELECT company.name, employee.name AS name_1
        FROM company JOIN (employee JOIN engineer ON employee.id = engineer.id) ON company.id = employee.company_id
        WHERE employee.name = ? OR engineer.engineer_info = ?
        [...] ('SpongeBob', 'Senior Customer Engagement Engineer')
        {stop}Krusty Krab SpongeBob
        Krusty Krab Squidward

    从上面的示例可以观察到，直接与 ``Engineer`` 目标进行联结，而不是使用 ``with_polymorphic(Employee, [Engineer])`` 的“多态选择器”，具有一个有用的特点，即使用内部联结（inner JOIN）而不是左外联结（LEFT OUTER JOIN），从 SQL 优化器的角度来看，这通常更具性能优势。


.. tab:: 英文

    As a :func:`_orm.with_polymorphic` entity is a special case of :func:`_orm.aliased`, in order to treat a polymorphic entity as the target of a join, specifically when using a :func:`_orm.relationship` construct as the ON clause, we use the same technique for regular aliases as detailed at :ref:`orm_queryguide_joining_relationships_aliased`, most succinctly using :meth:`_orm.PropComparator.of_type`.   In the example below we illustrate a join from the parent ``Company`` entity along the one-to-many relationship ``Company.employees``, which is configured in the :doc:`setup <_inheritance_setup>` to link to ``Employee`` objects, using a :func:`_orm.with_polymorphic` entity as the target::

        >>> employee_plus_engineer = with_polymorphic(Employee, [Engineer])
        >>> stmt = (
        ...     select(Company.name, employee_plus_engineer.name)
        ...     .join(Company.employees.of_type(employee_plus_engineer))
        ...     .where(
        ...         or_(
        ...             employee_plus_engineer.name == "SpongeBob",
        ...             employee_plus_engineer.Engineer.engineer_info
        ...             == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ... )
        >>> for company_name, emp_name in session.execute(stmt):
        ...     print(f"{company_name} {emp_name}")
        {execsql}SELECT company.name, employee.name AS name_1
        FROM company JOIN (employee LEFT OUTER JOIN engineer ON employee.id = engineer.id) ON company.id = employee.company_id
        WHERE employee.name = ? OR engineer.engineer_info = ?
        [...] ('SpongeBob', 'Senior Customer Engagement Engineer')
        {stop}Krusty Krab SpongeBob
        Krusty Krab Squidward

    More directly, :meth:`_orm.PropComparator.of_type` is also used with inheritance mappings of any kind to limit a join along a :func:`_orm.relationship` to a particular sub-type of the :func:`_orm.relationship`'s target.  The above query could be written strictly in terms of ``Engineer`` targets as follows::

        >>> stmt = (
        ...     select(Company.name, Engineer.name)
        ...     .join(Company.employees.of_type(Engineer))
        ...     .where(
        ...         or_(
        ...             Engineer.name == "SpongeBob",
        ...             Engineer.engineer_info == "Senior Customer Engagement Engineer",
        ...         )
        ...     )
        ... )
        >>> for company_name, emp_name in session.execute(stmt):
        ...     print(f"{company_name} {emp_name}")
        {execsql}SELECT company.name, employee.name AS name_1
        FROM company JOIN (employee JOIN engineer ON employee.id = engineer.id) ON company.id = employee.company_id
        WHERE employee.name = ? OR engineer.engineer_info = ?
        [...] ('SpongeBob', 'Senior Customer Engagement Engineer')
        {stop}Krusty Krab SpongeBob
        Krusty Krab Squidward

    It can be observed above that joining to the ``Engineer`` target directly, rather than the "polymorphic selectable" of ``with_polymorphic(Employee, [Engineer])`` has the useful characteristic of using an inner JOIN rather than a LEFT OUTER JOIN, which is generally more performant from a SQL optimizer point of view.

.. _eagerloading_polymorphic_subtypes:

即时加载多态子类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Eager Loading of Polymorphic Subtypes

.. tab:: 中文

    上一节中结合 :meth:`.Select.join` 方法展示的 :meth:`_orm.PropComparator.of_type` 的用法，也可以同样应用于 :ref:`relationship loader options <orm_queryguide_relationship_loaders>`，例如 :func:`_orm.selectinload` 和 :func:`_orm.joinedload`。

    作为一个基本示例，如果我们希望加载 ``Company`` 对象，并额外使用 :func:`_orm.with_polymorphic` 构造对完整的继承层次结构进行急切加载 ``Company.employees`` 的所有元素，我们可以这样写::

        >>> all_employees = with_polymorphic(Employee, "*")
        >>> stmt = select(Company).options(selectinload(Company.employees.of_type(all_employees)))
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     print(f"employees: {company.employees}")
        {execsql}SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type, manager.id AS manager_id,
        manager.manager_name AS manager_manager_name, engineer.id AS engineer_id,
        engineer.engineer_info AS engineer_engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        WHERE employee.company_id IN (?)
        [...] (1,)
        company: Krusty Krab
        employees: [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    上述查询可以直接与前一节 :ref:`polymorphic_selectin_as_loader_option_target` 中使用 :func:`_orm.selectin_polymorphic` 的版本进行对比。

    .. seealso::

        :ref:`polymorphic_selectin_as_loader_option_target` - 演示了与上例等效的、使用 :func:`_orm.selectin_polymorphic` 的方式


.. tab:: 英文

    The use of :meth:`_orm.PropComparator.of_type` illustrated with the :meth:`.Select.join` method in the previous section may also be applied equivalently to :ref:`relationship loader options <orm_queryguide_relationship_loaders>`, such as :func:`_orm.selectinload` and :func:`_orm.joinedload`.

    As a basic example, if we wished to load ``Company`` objects, and additionally eagerly load all elements of ``Company.employees`` using the :func:`_orm.with_polymorphic` construct against the full hierarchy, we may write::

        >>> all_employees = with_polymorphic(Employee, "*")
        >>> stmt = select(Company).options(selectinload(Company.employees.of_type(all_employees)))
        >>> for company in session.scalars(stmt):
        ...     print(f"company: {company.name}")
        ...     print(f"employees: {company.employees}")
        {execsql}SELECT company.id, company.name
        FROM company
        [...] ()
        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type, manager.id AS manager_id,
        manager.manager_name AS manager_manager_name, engineer.id AS engineer_id,
        engineer.engineer_info AS engineer_engineer_info
        FROM employee
        LEFT OUTER JOIN manager ON employee.id = manager.id
        LEFT OUTER JOIN engineer ON employee.id = engineer.id
        WHERE employee.company_id IN (?)
        [...] (1,)
        company: Krusty Krab
        employees: [Manager('Mr. Krabs'), Engineer('SpongeBob'), Engineer('Squidward')]

    The above query may be compared directly to the :func:`_orm.selectin_polymorphic` version illustrated in the previous section :ref:`polymorphic_selectin_as_loader_option_target`.

    .. seealso::

        :ref:`polymorphic_selectin_as_loader_option_target` - illustrates the equivalent example as above using :func:`_orm.selectin_polymorphic` instead


.. _loading_single_inheritance:

单一继承映射的 SELECT 语句
-------------------------------------------------

SELECT Statements for Single Inheritance Mappings

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK
        >>> conn.close()

    .. doctest-include _single_inheritance.rst

    .. admonition:: 单表继承设置（Single Table Inheritance Setup）

        本节讨论单表继承（single table inheritance），详见 :ref:`single_inheritance`，该方式使用一个表来表示继承层级中的多个类。

        :doc:`查看本节的 ORM 设置 <_single_inheritance>`。

    与联合（joined）继承映射不同，单表继承映射的 SELECT 语句构造通常更为简单，因为在一个纯单表继承的层级结构中，只有一张表。

    无论继承层级是否为纯单表继承，还是混合了联合继承与单表继承，对于单表继承的查询来说，区分查询的是基类还是子类是通过在 SELECT 语句中添加额外的 WHERE 条件来实现的。

    例如，对单表继承映射的 ``Employee`` 进行查询，将使用简单的 SELECT 语句从表中加载类型为 ``Manager``、``Engineer`` 和 ``Employee`` 的对象::

        >>> stmt = select(Employee).order_by(Employee.id)
        >>> for obj in session.scalars(stmt):
        ...     print(f"{obj}")
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}Manager('Mr. Krabs')
        Engineer('SpongeBob')
        Engineer('Squidward')

    当对某个具体的子类进行加载时，SQL 语句会附加额外的条件以限制返回的行。如下所示，执行对 ``Engineer`` 实体的 SELECT::

        >>> stmt = select(Engineer).order_by(Engineer.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.engineer_info
        FROM employee
        WHERE employee.type IN (?) ORDER BY employee.id
        [...] ('engineer',)
        {stop}>>> for obj in objects:
        ...     print(f"{obj}")
        Engineer('SpongeBob')
        Engineer('Squidward')


.. tab:: 英文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK
        >>> conn.close()

    .. doctest-include _single_inheritance.rst

    .. admonition:: Single Table Inheritance Setup

        This section discusses single table inheritance, described at :ref:`single_inheritance`, which uses a single table to represent multiple classes in a hierarchy.

        :doc:`View the ORM setup for this section <_single_inheritance>`.

    In contrast to joined inheritance mappings, the construction of SELECT statements for single inheritance mappings tends to be simpler since for an all-single-inheritance hierarchy, there's only one table.

    Regardless of whether or not the inheritance hierarchy is all single-inheritance or has a mixture of joined and single inheritance, SELECT statements for single inheritance differentiate queries against the base class vs. a subclass by limiting the SELECT statement with additional WHERE criteria.

    As an example, a query for the single-inheritance example mapping of ``Employee`` will load objects of type ``Manager``, ``Engineer`` and ``Employee`` using a simple SELECT of the table::

        >>> stmt = select(Employee).order_by(Employee.id)
        >>> for obj in session.scalars(stmt):
        ...     print(f"{obj}")
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}Manager('Mr. Krabs')
        Engineer('SpongeBob')
        Engineer('Squidward')

    When a load is emitted for a specific subclass, additional criteria is added to the SELECT that limits the rows, such as below where a SELECT against the ``Engineer`` entity is performed::

        >>> stmt = select(Engineer).order_by(Engineer.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}SELECT employee.id, employee.name, employee.type, employee.engineer_info
        FROM employee
        WHERE employee.type IN (?) ORDER BY employee.id
        [...] ('engineer',)
        {stop}>>> for obj in objects:
        ...     print(f"{obj}")
        Engineer('SpongeBob')
        Engineer('Squidward')



优化单一继承的属性加载
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Optimizing Attribute Loads for Single Inheritance

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    单表继承映射在对子类属性的 SELECT 行为上与联合继承类似，即默认情况下，子类特有的属性仍会通过额外的 SELECT 语句来获取。下面的示例中，虽然加载的是一个类型为 ``Manager`` 的 ``Employee``，但由于查询的目标类是 ``Employee``，默认情况下并不会加载 ``Manager.manager_name`` 属性，因此当访问该属性时会触发一次额外的 SELECT 操作::

        >>> mr_krabs = session.scalars(select(Employee).where(Employee.name == "Mr. Krabs")).one()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type
        FROM employee
        WHERE employee.name = ?
        [...] ('Mr. Krabs',)
        {stop}>>> mr_krabs.manager_name
        {execsql}SELECT employee.manager_name AS employee_manager_name
        FROM employee
        WHERE employee.id = ? AND employee.type IN (?)
        [...] (1, 'manager')
        {stop}'Eugene H. Krabs'

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    要改变这一行为，可以使用与联合继承中相同的机制来预加载这些子类的额外属性，包括使用 :func:`_orm.selectin_polymorphic` 选项或 :func:`_orm.with_polymorphic` 选项，其中后者通过在主查询中包含额外的列，从 SQL 的角度来看对单表继承映射来说更高效::

        >>> employees = with_polymorphic(Employee, "*")
        >>> stmt = select(employees).order_by(employees.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type,
        employee.manager_name, employee.engineer_info
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}>>> for obj in objects:
        ...     print(f"{obj}")
        Manager('Mr. Krabs')
        Engineer('SpongeBob')
        Engineer('Squidward')
        >>> objects[0].manager_name
        'Eugene H. Krabs'

    由于加载单表继承子类映射的开销通常非常小，因此建议在那些需要频繁访问子类属性的子类上，使用 :paramref:`_orm.Mapper.polymorphic_load` 参数并设置为 ``"inline"``。下面是基于 :doc:`设置示例 <_single_inheritance>` 修改后的示例::

        >>> class Base(DeclarativeBase):
        ...     pass
        >>> class Employee(Base):
        ...     __tablename__ = "employee"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     type: Mapped[str]
        ...
        ...     def __repr__(self):
        ...         return f"{self.__class__.__name__}({self.name!r})"
        ...
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "employee",
        ...         "polymorphic_on": "type",
        ...     }
        >>> class Manager(Employee):
        ...     manager_name: Mapped[str] = mapped_column(nullable=True)
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "manager",
        ...         "polymorphic_load": "inline",
        ...     }
        >>> class Engineer(Employee):
        ...     engineer_info: Mapped[str] = mapped_column(nullable=True)
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "engineer",
        ...         "polymorphic_load": "inline",
        ...     }

    基于上述映射，在针对 ``Employee`` 实体进行 SELECT 查询时，会自动将 ``Manager`` 和 ``Engineer`` 类的列包含在内::

        >>> print(select(Employee))
        {printsql}SELECT employee.id, employee.name, employee.type,
        employee.manager_name, employee.engineer_info
        FROM employee


.. tab:: 英文

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    The default behavior of single inheritance mappings regarding how attributes on subclasses are SELECTed is similar to that of joined inheritance, in that subclass-specific attributes still emit a second SELECT by default.  In the example below, a single ``Employee`` of type ``Manager`` is loaded, however since the requested class is ``Employee``, the ``Manager.manager_name`` attribute is not present by default, and an additional SELECT is emitted when it's accessed::

        >>> mr_krabs = session.scalars(select(Employee).where(Employee.name == "Mr. Krabs")).one()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type
        FROM employee
        WHERE employee.name = ?
        [...] ('Mr. Krabs',)
        {stop}>>> mr_krabs.manager_name
        {execsql}SELECT employee.manager_name AS employee_manager_name
        FROM employee
        WHERE employee.id = ? AND employee.type IN (?)
        [...] (1, 'manager')
        {stop}'Eugene H. Krabs'

    ..  Setup code, not for display

        >>> session.close()
        ROLLBACK

    To alter this behavior, the same general concepts used to eagerly load these additional attributes used in joined inheritance loading apply to single inheritance as well, including use of the :func:`_orm.selectin_polymorphic` option as well as the :func:`_orm.with_polymorphic` option, the latter of which simply includes the additional columns and from a SQL perspective is more efficient for single-inheritance mappers::

        >>> employees = with_polymorphic(Employee, "*")
        >>> stmt = select(employees).order_by(employees.id)
        >>> objects = session.scalars(stmt).all()
        {execsql}BEGIN (implicit)
        SELECT employee.id, employee.name, employee.type,
        employee.manager_name, employee.engineer_info
        FROM employee ORDER BY employee.id
        [...] ()
        {stop}>>> for obj in objects:
        ...     print(f"{obj}")
        Manager('Mr. Krabs')
        Engineer('SpongeBob')
        Engineer('Squidward')
        >>> objects[0].manager_name
        'Eugene H. Krabs'

    Since the overhead of loading single-inheritance subclass mappings is usually minimal, it's therefore recommended that single inheritance mappings include the :paramref:`_orm.Mapper.polymorphic_load` parameter with a setting of ``"inline"`` for those subclasses where loading of their specific subclass attributes is expected to be common.   An example illustrating the :doc:`setup <_single_inheritance>`, modified to include this option, is below::

        >>> class Base(DeclarativeBase):
        ...     pass
        >>> class Employee(Base):
        ...     __tablename__ = "employee"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     type: Mapped[str]
        ...
        ...     def __repr__(self):
        ...         return f"{self.__class__.__name__}({self.name!r})"
        ...
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "employee",
        ...         "polymorphic_on": "type",
        ...     }
        >>> class Manager(Employee):
        ...     manager_name: Mapped[str] = mapped_column(nullable=True)
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "manager",
        ...         "polymorphic_load": "inline",
        ...     }
        >>> class Engineer(Employee):
        ...     engineer_info: Mapped[str] = mapped_column(nullable=True)
        ...     __mapper_args__ = {
        ...         "polymorphic_identity": "engineer",
        ...         "polymorphic_load": "inline",
        ...     }


    With the above mapping, the ``Manager`` and ``Engineer`` classes will have their columns included in SELECT statements against the ``Employee`` entity automatically::

        >>> print(select(Employee))
        {printsql}SELECT employee.id, employee.name, employee.type,
        employee.manager_name, employee.engineer_info
        FROM employee

继承加载 API
-----------------------

Inheritance Loading API

.. tab:: 中文

.. tab:: 英文

.. autofunction:: sqlalchemy.orm.with_polymorphic

.. autofunction:: sqlalchemy.orm.selectin_polymorphic


..  Setup code, not for display

    >>> session.close()
    ROLLBACK
    >>> conn.close()
