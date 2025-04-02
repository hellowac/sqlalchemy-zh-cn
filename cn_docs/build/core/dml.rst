插入,更新,删除
========================

Insert, Updates, Deletes

.. tab:: 中文

   INSERT、UPDATE 和 DELETE 语句建立在以 :class:`.UpdateBase` 为基础的层次结构上。:class:`_expression.Insert` 和 :class:`_expression.Update` 构造基于中间类 :class:`.ValuesBase`。

.. tab:: 英文

   INSERT, UPDATE and DELETE statements build on a hierarchy starting
   with :class:`.UpdateBase`.   The :class:`_expression.Insert` and :class:`_expression.Update`
   constructs build on the intermediary :class:`.ValuesBase`.

.. currentmodule:: sqlalchemy.sql.expression

.. _dml_foundational_consructors:

DML 基础构造函数
--------------------------------------

DML Foundational Constructors

Top level "INSERT", "UPDATE", "DELETE" constructors.

.. autofunction:: delete

.. autofunction:: insert

.. autofunction:: update


DML 类文档构造函数
--------------------------------------

DML Class Documentation Constructors

Class documentation for the constructors listed at
:ref:`dml_foundational_consructors`.

.. autoclass:: Delete
   :members:

   .. automethod:: Delete.where

   .. automethod:: Delete.with_dialect_options

   .. automethod:: Delete.returning

.. autoclass:: Insert
   :members:

   .. automethod:: Insert.with_dialect_options

   .. automethod:: Insert.values

   .. automethod:: Insert.returning

.. autoclass:: Update
   :members:

   .. automethod:: Update.returning

   .. automethod:: Update.where

   .. automethod:: Update.with_dialect_options

   .. automethod:: Update.values

.. autoclass:: sqlalchemy.sql.expression.UpdateBase
   :members:

.. autoclass:: sqlalchemy.sql.expression.ValuesBase
   :members:



