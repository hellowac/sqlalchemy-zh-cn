.. _orm_event_toplevel:

ORM 事件
==========

ORM Events

.. tab:: 中文

   ORM 包括多种可供订阅的钩子。

   有关最常用 ORM 事件的介绍，请参阅 :ref:`session_events_toplevel` 部分。事件系统的一般讨论见 :ref:`event_toplevel`。非 ORM 事件，例如那些关于连接和低级语句执行的事件，描述在 :ref:`core_event_toplevel`。

.. tab:: 英文

   The ORM includes a wide variety of hooks available for subscription.

   For an introduction to the most commonly used ORM events, see the section
   :ref:`session_events_toplevel`.   The event system in general is discussed
   at :ref:`event_toplevel`.  Non-ORM events such as those regarding connections
   and low-level statement execution are described in :ref:`core_event_toplevel`.

会话事件
--------------

Session Events

.. tab:: 中文

   最基本的事件钩子可在 ORM :class:`_orm.Session` 对象级别使用。这里拦截的内容类型包括：

   * **持久化操作** - 发送更改到数据库的 ORM 刷新过程可以使用在不同刷新部分触发的事件进行扩展，以增加或修改发送到数据库的数据，或在持久化发生时允许其他事情发生。有关持久化事件的详细信息，请参阅 :ref:`session_persistence_events`。

   * **对象生命周期事件** - 当对象被添加、持久化、从会话中删除时的钩子。有关这些内容的更多信息，请参阅 :ref:`session_lifecycle_events`。

   * **执行事件** - 作为 :term:`2.0 风格` 执行模型的一部分，针对 ORM 实体发出的所有 SELECT 语句以及刷新过程之外的批量 UPDATE 和 DELETE 语句均通过 :meth:`_orm.Session.execute` 方法使用 :meth:`_orm.SessionEvents.do_orm_execute` 方法拦截。有关此事件的更多信息，请参阅 :ref:`session_execute_events`。

   请务必阅读 :ref:`session_events_toplevel` 章节以了解这些事件的上下文。

.. tab:: 英文

   The most basic event hooks are available at the level of the ORM
   :class:`_orm.Session` object.   The types of things that are intercepted
   here include:

   * **Persistence Operations** - the ORM flush process that sends changes to the
     database can be extended using events that fire off at different parts of the
     flush, to augment or modify the data being sent to the database or to allow
     other things to happen when persistence occurs.   Read more about persistence
     events at :ref:`session_persistence_events`.

   * **Object lifecycle events** - hooks when objects are added, persisted,
     deleted from sessions.   Read more about these at
     :ref:`session_lifecycle_events`.

   * **Execution Events** - Part of the :term:`2.0 style` execution model, all
     SELECT statements against ORM entities emitted, as well as bulk UPDATE
     and DELETE statements outside of the flush process, are intercepted
     from the :meth:`_orm.Session.execute` method using the
     :meth:`_orm.SessionEvents.do_orm_execute` method.  Read more about this
     event at :ref:`session_execute_events`.

   Be sure to read the :ref:`session_events_toplevel` chapter for context
   on these events.

.. autoclass:: sqlalchemy.orm.SessionEvents
   :members:

映射器事件
-------------

Mapper Events

.. tab:: 中文

   映射器事件钩子涵盖了与单个或多个 :class:`_orm.Mapper` 对象相关的事件，这些对象是将用户定义类映射到 :class:`_schema.Table` 对象的中心配置对象。在 :class:`_orm.Mapper` 级别发生的事情类型包括：

   * **按对象的持久化操作** - 最受欢迎的映射器钩子是单元工作钩子，例如 :meth:`_orm.MapperEvents.before_insert`、:meth:`_orm.MapperEvents.after_update` 等。这些事件与更粗粒度的会话级事件（如 :meth:`_orm.SessionEvents.before_flush`）相比，它们在刷新过程中按对象发生；尽管对象上的细粒度活动更为直接，但 :class:`_orm.Session` 功能的可用性有限。

   * **映射器配置事件** - 另一类主要的映射器钩子是在类被映射时、映射器被最终确定时以及成组的映射器被配置为相互引用时发生的那些事件。这些事件包括在单个 :class:`_orm.Mapper` 级别的 :meth:`_orm.MapperEvents.instrument_class`、:meth:`_orm.MapperEvents.before_mapper_configured` 和 :meth:`_orm.MapperEvents.mapper_configured`，以及在成组 :class:`_orm.Mapper` 对象级别的 :meth:`_orm.MapperEvents.before_configured` 和 :meth:`_orm.MapperEvents.after_configured`。

.. tab:: 英文

   Mapper event hooks encompass things that happen as related to individual
   or multiple :class:`_orm.Mapper` objects, which are the central configurational
   object that maps a user-defined class to a :class:`_schema.Table` object.
   Types of things which occur at the :class:`_orm.Mapper` level include:

   * **Per-object persistence operations** - the most popular mapper hooks are the
     unit-of-work hooks such as :meth:`_orm.MapperEvents.before_insert`,
     :meth:`_orm.MapperEvents.after_update`, etc.  These events are contrasted to
     the more coarse grained session-level events such as
     :meth:`_orm.SessionEvents.before_flush` in that they occur within the flush
     process on a per-object basis; while finer grained activity on an object is
     more straightforward, availability of :class:`_orm.Session` features is
     limited.

   * **Mapper configuration events** - the other major class of mapper hooks are
     those which occur as a class is mapped, as a mapper is finalized, and when
     sets of mappers are configured to refer to each other.  These events include
     :meth:`_orm.MapperEvents.instrument_class`,
     :meth:`_orm.MapperEvents.before_mapper_configured` and
     :meth:`_orm.MapperEvents.mapper_configured` at the individual
     :class:`_orm.Mapper` level, and  :meth:`_orm.MapperEvents.before_configured`
     and :meth:`_orm.MapperEvents.after_configured` at the level of collections of
     :class:`_orm.Mapper` objects.

.. autoclass:: sqlalchemy.orm.MapperEvents
   :members:

实例事件
---------------

Instance Events

.. tab:: 中文

   实例事件专注于 ORM 映射实例的构造，包括当它们被实例化为 :term:`transient` 对象时，当它们从数据库加载并成为 :term:`persistent` 对象时，以及当数据库刷新或过期操作发生在对象上时。

.. tab:: 英文

   Instance events are focused on the construction of ORM mapped instances,
   including when they are instantiated as :term:`transient` objects,
   when they are loaded from the database and become :term:`persistent` objects,
   as well as when database refresh or expiration operations occur on the object.

.. autoclass:: sqlalchemy.orm.InstanceEvents
   :members:



.. _orm_attribute_events:

属性事件
----------------

Attribute Events

.. tab:: 中文

   属性事件在 ORM 映射对象的各个属性上发生变化时触发。这些事件构成了诸如 :ref:`自定义验证函数 <simple_validators>` 以及 :ref:`反向引用处理程序 <relationships_backref>` 等功能的基础。

.. tab:: 英文

   Attribute events are triggered as things occur on individual attributes of
   ORM mapped objects.  These events form the basis for things like
   :ref:`custom validation functions <simple_validators>` as well as
   :ref:`backref handlers <relationships_backref>`.

.. seealso::

  :ref:`mapping_attributes_toplevel`

.. autoclass:: sqlalchemy.orm.AttributeEvents
   :members:


查询事件
------------

Query Events

.. autoclass:: sqlalchemy.orm.QueryEvents
   :members:

仪表事件
----------------------

Instrumentation Events

.. automodule:: sqlalchemy.orm.instrumentation

.. autoclass:: sqlalchemy.orm.InstrumentationEvents
   :members:

