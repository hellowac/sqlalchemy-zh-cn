
.. currentmodule:: sqlalchemy.orm

类映射 API
=================

Class Mapping API

.. autoclass:: registry
    :members:

.. autofunction:: add_mapped_attribute

.. autofunction:: column_property

.. autofunction:: declarative_base

.. autofunction:: declarative_mixin

.. autofunction:: as_declarative

.. autofunction:: mapped_column

.. autoclass:: declared_attr

    .. attribute:: cascading

        .. tab:: 中文

            将 :class:`.declared_attr` 标记为级联。

            这是一个特殊用途的修饰符，表示在映射继承方案中，基于列或 MapperProperty 的声明属性应在每个映射子类中分别配置。

            .. warning::

                :attr:`.declared_attr.cascading` 修饰符有几个限制：

                * 该标志 **仅** 适用于在声明式混入类和 ``__abstract__`` 类中使用 :class:`.declared_attr`；目前直接在映射类上使用时无效。

                * 该标志 **仅** 适用于正常命名的属性，例如，不适用于任何特殊的下划线属性，如 ``__tablename__``。在这些属性上无效。

                * 该标志当前 **不允许** 在类层次结构中进一步覆盖；如果子类尝试覆盖该属性，将发出警告并跳过覆盖的属性。这是一个希望在某个时候解决的限制。

            如下所示，MyClass 和 MySubClass 都会建立一个独特的 ``id`` 列对象::

                class HasIdMixin:
                    @declared_attr.cascading
                    def id(cls) -> Mapped[int]:
                        if has_inherited_table(cls):
                            return mapped_column(ForeignKey("myclass.id"), primary_key=True)
                        else:
                            return mapped_column(Integer, primary_key=True)


                class MyClass(HasIdMixin, Base):
                    __tablename__ = "myclass"
                    # ...


                class MySubClass(MyClass):
                    """ """

                    # ...

            上述配置的行为是 ``MySubClass`` 将引用其自身的 ``id`` 列以及 ``MyClass`` 下的同名属性 ``some_id``。

            .. seealso::

                :ref:`declarative_inheritance`

                :ref:`mixin_inheritance_columns`

        .. tab:: 英文

            Mark a :class:`.declared_attr` as cascading.
    
            This is a special-use modifier which indicates that a column
            or MapperProperty-based declared attribute should be configured
            distinctly per mapped subclass, within a mapped-inheritance scenario.
    
            .. warning::
    
                The :attr:`.declared_attr.cascading` modifier has several
                limitations:
    
                * The flag **only** applies to the use of :class:`.declared_attr`
                  on declarative mixin classes and ``__abstract__`` classes; it
                  currently has no effect when used on a mapped class directly.
    
                * The flag **only** applies to normally-named attributes, e.g.
                  not any special underscore attributes such as ``__tablename__``.
                  On these attributes it has **no** effect.
    
                * The flag currently **does not allow further overrides** down
                  the class hierarchy; if a subclass tries to override the
                  attribute, a warning is emitted and the overridden attribute
                  is skipped.  This is a limitation that it is hoped will be
                  resolved at some point.
    
            Below, both MyClass as well as MySubClass will have a distinct
            ``id`` Column object established::
    
                class HasIdMixin:
                    @declared_attr.cascading
                    def id(cls) -> Mapped[int]:
                        if has_inherited_table(cls):
                            return mapped_column(ForeignKey("myclass.id"), primary_key=True)
                        else:
                            return mapped_column(Integer, primary_key=True)
    
    
                class MyClass(HasIdMixin, Base):
                    __tablename__ = "myclass"
                    # ...
    
    
                class MySubClass(MyClass):
                    """ """
    
                    # ...
    
            The behavior of the above configuration is that ``MySubClass``
            will refer to both its own ``id`` column as well as that of
            ``MyClass`` underneath the attribute named ``some_id``.
    
            .. seealso::
    
                :ref:`declarative_inheritance`
    
                :ref:`mixin_inheritance_columns`

    .. attribute:: directive

        .. tab:: 中文

            将 :class:`.declared_attr` 标记为装饰声明式指令，如 ``__tablename__`` 或 ``__mapper_args__``。

            :attr:`.declared_attr.directive` 的目的是严格支持 :pep:`484` 类型工具，允许装饰的函数具有 **不** 使用 :class:`_orm.Mapped` 泛型类的返回类型，这通常在 :class:`.declared_attr` 用于列和映射属性时是这样的。在运行时，:attr:`.declared_attr.directive` 返回未修改的 :class:`.declared_attr` 类。

            例如::

                class CreateTableName:
                    @declared_attr.directive
                    def __tablename__(cls) -> str:
                        return cls.__name__.lower()

            .. versionadded:: 2.0

            .. seealso::

                :ref:`orm_mixins_toplevel`

                :class:`_orm.declared_attr`

        .. tab:: 英文

            Mark a :class:`.declared_attr` as decorating a Declarative
            directive such as ``__tablename__`` or ``__mapper_args__``.

            The purpose of :attr:`.declared_attr.directive` is strictly to
            support :pep:`484` typing tools, by allowing the decorated function
            to have a return type that is **not** using the :class:`_orm.Mapped`
            generic class, as would normally be the case when :class:`.declared_attr`
            is used for columns and mapped properties.  At
            runtime, the :attr:`.declared_attr.directive` returns the
            :class:`.declared_attr` class unmodified.

            E.g.::

                class CreateTableName:
                    @declared_attr.directive
                    def __tablename__(cls) -> str:
                        return cls.__name__.lower()

            .. versionadded:: 2.0

            .. seealso::

                :ref:`orm_mixins_toplevel`

                :class:`_orm.declared_attr`


.. autoclass:: DeclarativeBase
    :members:
    :special-members: __table__, __mapper__, __mapper_args__, __tablename__, __table_args__

.. autoclass:: DeclarativeBaseNoMeta
    :members:
    :special-members: __table__, __mapper__, __mapper_args__, __tablename__, __table_args__

.. autofunction:: has_inherited_table

.. autofunction:: synonym_for

.. autofunction:: object_mapper

.. autofunction:: class_mapper

.. autofunction:: configure_mappers

.. autofunction:: clear_mappers

.. autofunction:: sqlalchemy.orm.util.identity_key

.. autofunction:: polymorphic_union

.. autofunction:: orm_insert_sentinel

.. autofunction:: reconstructor

.. autoclass:: Mapper
   :members:

.. autoclass:: MappedAsDataclass
    :members:

.. autoclass:: MappedClassProtocol
    :no-members:
