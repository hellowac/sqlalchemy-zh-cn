.. _core_inspection_toplevel:
.. _inspection_toplevel:

运行时审查 API
======================

Runtime Inspection API

.. automodule:: sqlalchemy.inspection

.. autofunction:: sqlalchemy.inspect


可用的审查目标
----------------------------

Available Inspection Targets

.. tab:: 中文

    以下是许多最常见的检查目标列表。

    * :class:`.Connectable` （即 :class:`_engine.Engine`，:class:`_engine.Connection`） - 返回 :class:`_reflection.Inspector` 对象。
    * :class:`_expression.ClauseElement` - 所有SQL表达式组件，包括 :class:`_schema.Table` ， :class:`_schema.Column`，作为它们自己的检查对象，这意味着传递给 :func:`_sa.inspect` 的任何这些对象都会返回它们自己。
    * ``object`` - 给定的对象将由ORM检查其映射 - 如果是，则返回表示对象的映射状态的 :class:`.InstanceState`。 :class:`.InstanceState` 还通过 :class:`.AttributeState` 接口提供对每个属性状态的访问，以及通过 :class:`.History` 对象提供任何属性的每次刷新“历史”。

      .. seealso::

          :ref:`orm_mapper_inspection_instancestate`

    * ``type`` （即类） - 给定的类将由ORM检查其映射 - 如果是，则返回该类的 :class:`_orm.Mapper`。

      .. seealso::

          :ref:`orm_mapper_inspection_mapper`

    * 已映射的属性 - 将已映射的属性传递给 :func:`_sa.inspect`，例如 ``inspect(MyClass.some_attribute)``，返回 :class:`.QueryableAttribute` 对象，这是与已映射类关联的 :term:`描述符`。此描述符通过其 :attr:`.QueryableAttribute.property` 属性引用 :class:`.MapperProperty`，通常是 :class:`.ColumnProperty` 或 :class:`.RelationshipProperty` 的实例。
    * :class:`.AliasedClass` - 返回 :class:`.AliasedInsp` 对象。

.. tab:: 英文

    Below is a listing of many of the most common inspection targets.

    * :class:`.Connectable` (i.e. :class:`_engine.Engine`,
      :class:`_engine.Connection`) - returns an :class:`_reflection.Inspector` object.
    * :class:`_expression.ClauseElement` - all SQL expression components, including
      :class:`_schema.Table`, :class:`_schema.Column`, serve as their own inspection objects,
      meaning any of these objects passed to :func:`_sa.inspect` return themselves.
    * ``object`` - an object given will be checked by the ORM for a mapping -
      if so, an :class:`.InstanceState` is returned representing the mapped
      state of the object.  The :class:`.InstanceState` also provides access
      to per attribute state via the :class:`.AttributeState` interface as well
      as the per-flush "history" of any attribute via the :class:`.History`
      object.

      .. seealso::

          :ref:`orm_mapper_inspection_instancestate`

    * ``type`` (i.e. a class) - a class given will be checked by the ORM for a
      mapping - if so, a :class:`_orm.Mapper` for that class is returned.

      .. seealso::

          :ref:`orm_mapper_inspection_mapper`

    * mapped attribute - passing a mapped attribute to :func:`_sa.inspect`, such
      as ``inspect(MyClass.some_attribute)``, returns a :class:`.QueryableAttribute`
      object, which is the :term:`descriptor` associated with a mapped class.
      This descriptor refers to a :class:`.MapperProperty`, which is usually
      an instance of :class:`.ColumnProperty`
      or :class:`.RelationshipProperty`, via its :attr:`.QueryableAttribute.property`
      attribute.
    * :class:`.AliasedClass` - returns an :class:`.AliasedInsp` object.


