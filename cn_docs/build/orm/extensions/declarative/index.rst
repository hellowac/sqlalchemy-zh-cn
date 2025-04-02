.. _declarative_toplevel:

.. currentmodule:: sqlalchemy.ext.declarative

======================
声明式扩展
======================

Declarative Extensions

.. tab:: 中文

   特定于 :ref:`Declarative <orm_declarative_mapping>` 映射 API 的扩展。

   .. versionchanged:: 1.4  
      
      Declarative 扩展的绝大部分现已集成到 SQLAlchemy ORM 中，并可从 ``sqlalchemy.orm`` 命名空间导入。有关新文档，请参阅 :ref:`orm_declarative_mapping` 文档。 有关更改的概述，请参阅 :ref:`change_5508`。

.. tab:: 英文

   Extensions specific to the :ref:`Declarative <orm_declarative_mapping>`
   mapping API.

   .. versionchanged:: 1.4  The vast majority of the Declarative extension is now
      integrated into the SQLAlchemy ORM and is importable from the
      ``sqlalchemy.orm`` namespace.  See the documentation at
      :ref:`orm_declarative_mapping` for new documentation.
      For an overview of the change, see :ref:`change_5508`.

.. autoclass:: AbstractConcreteBase

.. autoclass:: ConcreteBase

.. autoclass:: DeferredReflection
   :members:

