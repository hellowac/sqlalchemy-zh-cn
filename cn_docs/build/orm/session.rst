.. _session_toplevel:

=================
使用会话
=================

Using the Session

.. module:: sqlalchemy.orm.session

.. tab:: 中文

    声明性基础和 ORM 映射函数（如 :ref:`mapper_config_toplevel` 中所述）是 ORM 的主要配置接口。一旦映射配置完成，持久化操作的主要使用接口是 :class:`.Session`。

.. tab:: 英文

    The declarative base and ORM mapping functions described at
    :ref:`mapper_config_toplevel` are the primary configurational interface for the
    ORM. Once mappings are configured, the primary usage interface for
    persistence operations is the
    :class:`.Session`.

.. toctree::
    :maxdepth: 3

    session_basics
    session_state_management
    cascades
    session_transaction
    persistence_techniques
    contextual
    session_events
    session_api

