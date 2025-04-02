.. _core_event_toplevel:

核心事件
===========

Core Events

.. tab:: 中文

    本节描述了SQLAlchemy Core中提供的事件接口。有关事件监听API的介绍，请参见 :ref:`event_toplevel` 。ORM事件在 :ref:`orm_event_toplevel` 中描述。

.. tab:: 英文

    This section describes the event interfaces provided in
    SQLAlchemy Core.
    For an introduction to the event listening API, see :ref:`event_toplevel`.
    ORM events are described in :ref:`orm_event_toplevel`.

.. autoclass:: sqlalchemy.event.base.Events
   :members:

连接池事件
----------------------

Connection Pool Events

.. autoclass:: sqlalchemy.events.PoolEvents
   :members:

.. autoclass:: sqlalchemy.events.PoolResetState
   :members:

.. _core_sql_events:

SQL 执行和连接事件
-----------------------------------

SQL Execution and Connection Events

.. autoclass:: sqlalchemy.events.ConnectionEvents
    :members:

.. autoclass:: sqlalchemy.events.DialectEvents
    :members:

架构事件
-------------

Schema Events

.. autoclass:: sqlalchemy.events.DDLEvents
    :members:

.. autoclass:: sqlalchemy.events.SchemaEventTarget
    :members:

