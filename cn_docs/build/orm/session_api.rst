.. currentmodule:: sqlalchemy.orm

会话 API
===========

Session API

Session 和 sessionmaker()
--------------------------

Session and sessionmaker()

.. autoclass:: sessionmaker
    :members:
    :inherited-members:

.. autoclass:: ORMExecuteState
    :members:

.. autoclass:: Session
   :members:
   :inherited-members:

.. autoclass:: SessionTransaction
   :members:

.. autoclass:: SessionTransactionOrigin
   :members:

会话实用程序
-----------------

Session Utilities

.. tab:: 中文


.. tab:: 英文

.. autofunction:: close_all_sessions

.. autofunction:: make_transient

.. autofunction:: make_transient_to_detached

.. autofunction:: object_session

.. autofunction:: sqlalchemy.orm.util.was_deleted

属性和状态管理实用程序
----------------------------------------

Attribute and State Management Utilities

.. tab:: 中文

    这些函数由 SQLAlchemy 属性检测 API 提供，以提供处理实例、属性值和历史记录的详细接口。在构建事件监听器函数时，其中一些非常有用，例如 :doc:`/orm/events` 中描述的那些。

.. tab:: 英文

    These functions are provided by the SQLAlchemy attribute
    instrumentation API to provide a detailed interface for dealing
    with instances, attribute values, and history.  Some of them
    are useful when constructing event listener functions, such as
    those described in :doc:`/orm/events`.

.. currentmodule:: sqlalchemy.orm.util

.. autofunction:: object_state

.. currentmodule:: sqlalchemy.orm.attributes

.. autofunction:: del_attribute

.. autofunction:: get_attribute

.. autofunction:: get_history

.. autofunction:: init_collection

.. autofunction:: flag_modified

.. autofunction:: flag_dirty

.. function:: instance_state

    Return the :class:`.InstanceState` for a given
    mapped object.

    This function is the internal version
    of :func:`.object_state`.   The
    :func:`.object_state` and/or the
    :func:`_sa.inspect` function is preferred here
    as they each emit an informative exception
    if the given object is not mapped.

.. autofunction:: sqlalchemy.orm.instrumentation.is_instrumented

.. autofunction:: set_attribute

.. autofunction:: set_committed_value

.. autoclass:: History
    :members:

