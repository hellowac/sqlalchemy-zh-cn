.. _relationship_patterns:

基本关系模式
---------------------------

Basic Relationship Patterns

.. tab:: 中文

    快速演练基础关系模式，在本节中使用基于 :class:`_orm.Mapped` 注解类型的 :ref:`声明式 <orm_explicit_declarative_base>` 风格映射进行说明。

    以下各节的设置如下::

        from __future__ import annotations
        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass

.. tab:: 英文

    A quick walkthrough of the basic relational patterns, which in this section are illustrated
    using :ref:`Declarative <orm_explicit_declarative_base>` style mappings
    based on the use of the :class:`_orm.Mapped` annotation type.

    The setup for each of the following sections is as follows::

        from __future__ import annotations
        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass

声明式与命令式形式
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Declarative vs. Imperative Forms

.. tab:: 中文

    随着 SQLAlchemy 的发展，不同的 ORM 配置风格已经出现。
    对于本节和其他使用带注释的 :ref:`Declarative <orm_explicit_declarative_base>` 映射和 :class:`_orm.Mapped` 的示例，相应的非注释形式应使用所需的类或字符串类名作为传递给 :func:`_orm.relationship` 的第一个参数。下面的示例展示了本文档中使用的形式，这是一个使用 :pep:`484` 注释的完全声明式示例，其中 :func:`_orm.relationship` 构造也从 :class:`_orm.Mapped` 注释中派生目标类和集合类型，这是 SQLAlchemy 声明式映射的最新形式::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="children")

    相比之下，使用 **不带注释** 的声明式映射是更“经典”的映射形式，其中 :func:`_orm.relationship` 需要直接传递所有参数，如下例所示::

        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            children = relationship("Child", back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(ForeignKey("parent_table.id"))
            parent = relationship("Parent", back_populates="children")

    最后，使用 :ref:`Imperative Mapping <orm_imperative_mapping>`，这是 SQLAlchemy 在声明式之前的原始映射形式（尽管如此，仍然受到一部分用户的青睐），上述配置如下::

        registry.map_imperatively(
            Parent,
            parent_table,
            properties={"children": relationship("Child", back_populates="parent")},
        )

        registry.map_imperatively(
            Child,
            child_table,
            properties={"parent": relationship("Parent", back_populates="children")},
        )

    此外，非注释映射的默认集合样式是 ``list``。要使用 ``set`` 或其他集合而不使用注释，请使用 :paramref:`_orm.relationship.collection_class` 参数指示::

        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            children = relationship("Child", collection_class=set, ...)

    有关 :func:`_orm.relationship` 的集合配置的详细信息，请参见 :ref:`custom_collections`。

    根据需要将注意到带注释和不带注释/命令式风格之间的其他差异。

.. tab:: 英文

    As SQLAlchemy has evolved, different ORM configurational styles have emerged.
    For examples in this section and others that use annotated
    :ref:`Declarative <orm_explicit_declarative_base>` mappings with
    :class:`_orm.Mapped`, the corresponding non-annotated form should use the
    desired class, or string class name, as the first argument passed to
    :func:`_orm.relationship`.  The example below illustrates the form used in
    this document, which is a fully Declarative example using :pep:`484` annotations,
    where the :func:`_orm.relationship` construct is also deriving the target
    class and collection type from the :class:`_orm.Mapped` annotation,
    which is the most modern form of SQLAlchemy Declarative mapping::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="children")

    In contrast, using a Declarative mapping **without** annotations is
    the more "classic" form of mapping, where :func:`_orm.relationship`
    requires all parameters passed to it directly, as in the example below::

        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            children = relationship("Child", back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(ForeignKey("parent_table.id"))
            parent = relationship("Parent", back_populates="children")

    Finally, using :ref:`Imperative Mapping <orm_imperative_mapping>`, which
    is SQLAlchemy's original mapping form before Declarative was made (which
    nonetheless remains preferred by a vocal minority of users), the above
    configuration looks like::

        registry.map_imperatively(
            Parent,
            parent_table,
            properties={"children": relationship("Child", back_populates="parent")},
        )

        registry.map_imperatively(
            Child,
            child_table,
            properties={"parent": relationship("Parent", back_populates="children")},
        )

    Additionally, the default collection style for non-annotated mappings is
    ``list``.  To use a ``set`` or other collection without annotations, indicate
    it using the :paramref:`_orm.relationship.collection_class` parameter::

        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            children = relationship("Child", collection_class=set, ...)

    Detail on collection configuration for :func:`_orm.relationship` is at
    :ref:`custom_collections`.

    Additional differences between annotated and non-annotated / imperative
    styles will be noted as needed.

.. _relationship_patterns_o2m:

一对多
~~~~~~~~~~~

One To Many

.. tab:: 中文

    一对多关系在子表上放置一个引用父表的外键。然后在父表上指定 :func:`_orm.relationship`，引用由子表表示的项目集合::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship()


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))

    要在一对多关系中建立双向关系，其中“反向(reverse)”端是多对一，指定一个额外的 :func:`_orm.relationship` 并使用 :paramref:`_orm.relationship.back_populates` 参数连接两者，使用每个 :func:`_orm.relationship` 的属性名称作为另一个的 :paramref:`_orm.relationship.back_populates` 的值::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="children")

    ``Child`` 将获得具有多对一语义的 ``parent`` 属性。

.. tab:: 英文

    A one to many relationship places a foreign key on the child table referencing
    the parent.  :func:`_orm.relationship` is then specified on the parent, as referencing
    a collection of items represented by the child::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship()


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))

    To establish a bidirectional relationship in one-to-many, where the "reverse"
    side is a many to one, specify an additional :func:`_orm.relationship` and connect
    the two using the :paramref:`_orm.relationship.back_populates` parameter,
    using the attribute name of each :func:`_orm.relationship`
    as the value for :paramref:`_orm.relationship.back_populates` on the other::


        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="children")

    ``Child`` will get a ``parent`` attribute with many-to-one semantics.

.. _relationship_patterns_o2m_collection:

使用集合、列表或其他集合类型实现一对多
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Sets, Lists, or other Collection Types for One To Many

.. tab:: 中文

    使用带注释的声明式映射时，:func:`_orm.relationship` 使用的集合类型是从传递给 :class:`_orm.Mapped` 容器类型的集合类型派生的。上一节的示例可以写成使用 ``set`` 而不是 ``list`` 作为 ``Parent.children`` 集合，使用 ``Mapped[Set["Child"]]``::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[Set["Child"]] = relationship(back_populates="parent")

    当使用非注释形式（包括命令式映射）时，可以使用 :paramref:`_orm.relationship.collection_class` 参数传递作为集合使用的 Python 类。

    .. seealso::

        :ref:`custom_collections` - 包含有关集合配置的更多详细信息，包括一些将 :func:`_orm.relationship` 映射到字典的技术。

.. tab:: 英文

    Using annotated Declarative mappings, the type of collection used for the
    :func:`_orm.relationship` is derived from the collection type passed to the
    :class:`_orm.Mapped` container type.  The example from the previous section
    may be written to use a ``set`` rather than a ``list`` for the
    ``Parent.children`` collection using ``Mapped[Set["Child"]]``::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[Set["Child"]] = relationship(back_populates="parent")

    When using non-annotated forms including imperative mappings, the Python
    class to use as a collection may be passed using the
    :paramref:`_orm.relationship.collection_class` parameter.

    .. seealso::

        :ref:`custom_collections` - contains further detail on collection
        configuration including some techniques to map :func:`_orm.relationship`
        to dictionaries.


配置一对多的删除行为
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuring Delete Behavior for One to Many

.. tab:: 中文

    通常情况下，当删除其所属的 ``Parent`` 时，所有 ``Child`` 对象也应该被删除。要配置此行为，使用在 :ref:`cascade_delete` 中描述的 ``delete`` 级联选项。还有一个额外的选项，即当 ``Child`` 对象与其父对象解除关联时，该对象本身也可以被删除。此行为在 :ref:`cascade_delete_orphan` 中描述。

    .. seealso::

        :ref:`cascade_delete`

        :ref:`passive_deletes`

        :ref:`cascade_delete_orphan`

.. tab:: 英文

    It is often the case that all ``Child`` objects should be deleted
    when their owning ``Parent`` is deleted.  To configure this behavior,
    the ``delete`` cascade option described at :ref:`cascade_delete` is used.
    An additional option is that a ``Child`` object can itself be deleted when
    it is deassociated from its parent.  This behavior is described at
    :ref:`cascade_delete_orphan`.

    .. seealso::

        :ref:`cascade_delete`

        :ref:`passive_deletes`

        :ref:`cascade_delete_orphan`


.. _relationship_patterns_m2o:

多对一
~~~~~~~~~~~

Many To One

.. tab:: 中文

    多对一关系在父表中放置一个引用子表的外键。在父表上声明 :func:`_orm.relationship`，将创建一个新的标量持有属性::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped["Child"] = relationship()


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)

    上述示例显示了一个假设非空行为的多对一关系；下一节，:ref:`relationship_patterns_nullable_m2o`，演示了一个可空版本。

    通过添加第二个 :func:`_orm.relationship` 并在两个方向上应用 :paramref:`_orm.relationship.back_populates` 参数来实现双向行为，使用每个 :func:`_orm.relationship` 的属性名称作为另一个的 :paramref:`_orm.relationship.back_populates` 的值::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped["Child"] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Parent"]] = relationship(back_populates="child")

.. tab:: 英文

    Many to one places a foreign key in the parent table referencing the child.
    :func:`_orm.relationship` is declared on the parent, where a new scalar-holding
    attribute will be created::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped["Child"] = relationship()


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)

    The above example shows a many-to-one relationship that assumes non-nullable
    behavior; the next section, :ref:`relationship_patterns_nullable_m2o`,
    illustrates a nullable version.

    Bidirectional behavior is achieved by adding a second :func:`_orm.relationship`
    and applying the :paramref:`_orm.relationship.back_populates` parameter
    in both directions, using the attribute name of each :func:`_orm.relationship`
    as the value for :paramref:`_orm.relationship.back_populates` on the other::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped["Child"] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Parent"]] = relationship(back_populates="child")

.. _relationship_patterns_nullable_m2o:

可空多对一
^^^^^^^^^^^^^^^^^^^^

Nullable Many-to-One

.. tab:: 中文

    在前面的示例中， ``Parent.child`` 关系未被标记为允许 ``None``；这源于 ``Parent.child_id`` 列本身不可为空，因为它被标记为 ``Mapped[int]``。如果我们希望 ``Parent.child`` 是一个 **可为空** 的多对一关系，我们可以将 ``Parent.child_id`` 和 ``Parent.child`` 都设置为 ``Optional[]``，这种情况下配置如下所示::

        from typing import Optional


        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[Optional[int]] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped[Optional["Child"]] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Parent"]] = relationship(back_populates="child")

    上面， ``Parent.child_id`` 的列将在 DDL 中创建为允许 ``NULL`` 值。当使用 :func:`_orm.mapped_column` 进行显式类型声明时，指定 ``child_id: Mapped[Optional[int]]`` 相当于在 :class:`_schema.Column` 上将 :paramref:`_schema.Column.nullable` 设置为 ``True``，而 ``child_id: Mapped[int]`` 相当于将其设置为 ``False``。有关此行为的背景，请参见 :ref:`orm_declarative_mapped_column_nullability`。

    .. tip::

    如果使用 Python 3.10 或更高版本，:pep:`604` 语法更方便，用 ``| None`` 表示可选类型，当与 :pep:`563` 延迟注释评估结合使用时，不再需要字符串引号类型，如下所示::

        from __future__ import annotations


        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int | None] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped[Child | None] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List[Parent]] = relationship(back_populates="child")

.. tab:: 英文

    In the preceding example, the ``Parent.child`` relationship is not typed as
    allowing ``None``; this follows from the ``Parent.child_id`` column itself
    not being nullable, as it is typed with ``Mapped[int]``.    If we wanted
    ``Parent.child`` to be a **nullable** many-to-one, we can set both
    ``Parent.child_id`` and ``Parent.child`` to be ``Optional[]``, in which
    case the configuration would look like::

        from typing import Optional


        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[Optional[int]] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped[Optional["Child"]] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Parent"]] = relationship(back_populates="child")

    Above, the column for ``Parent.child_id`` will be created in DDL to allow
    ``NULL`` values. When using :func:`_orm.mapped_column` with explicit typing
    declarations, the specification of ``child_id: Mapped[Optional[int]]`` is
    equivalent to setting :paramref:`_schema.Column.nullable` to ``True`` on the
    :class:`_schema.Column`, whereas ``child_id: Mapped[int]`` is equivalent to
    setting it to ``False``. See :ref:`orm_declarative_mapped_column_nullability`
    for background on this behavior.

    .. tip::

    If using Python 3.10 or greater, :pep:`604` syntax is more convenient
    to indicate optional types using ``| None``, which when combined with
    :pep:`563` postponed annotation evaluation so that string-quoted types aren't
    required, would look like::

        from __future__ import annotations


        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child_id: Mapped[int | None] = mapped_column(ForeignKey("child_table.id"))
            child: Mapped[Child | None] = relationship(back_populates="parents")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List[Parent]] = relationship(back_populates="child")

.. _relationships_one_to_one:

一对一
~~~~~~~~~~

One To One

.. tab:: 中文

    一对一关系本质上是从外键的角度来看是一种 :ref:`relationship_patterns_o2m` 关系，但表示任何时候只会有一行引用特定的父行。

    当使用带注释的映射和 :class:`_orm.Mapped` 时，“一对一”约定是通过在关系的两边应用非集合类型的 :class:`_orm.Mapped` 注释来实现的，这将向 ORM 表明两边都不应使用集合，如下例所示::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child: Mapped["Child"] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="child")

    如上所示，当我们加载一个 ``Parent`` 对象时， ``Parent.child`` 属性将引用一个单一的 ``Child`` 对象，而不是一个集合。如果我们用一个新的 ``Child`` 对象替换 ``Parent.child`` 的值，ORM 的工作单元过程将用新的对象替换先前的 ``Child`` 行，默认情况下将先前的 ``child.parent_id`` 列设置为 NULL，除非有特定的 :ref:`cascade <unitofwork_cascades>` 行为设置。

    .. tip::

        如前所述，ORM 将“一对一”模式视为一种约定，它假设当它在 ``Parent`` 对象上加载 ``Parent.child`` 属性时，只会返回一行。如果返回多行，ORM 将发出警告。

        然而，上述关系中的 ``Child.parent`` 方面仍然是“多对一”关系。单独使用时，它不会检测到分配超过一个 ``Child``，除非设置了 :paramref:`_orm.relationship.single_parent` 参数，这可能很有用::

            class Child(Base):
                __tablename__ = "child_table"

                id: Mapped[int] = mapped_column(primary_key=True)
                parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
                parent: Mapped["Parent"] = relationship(back_populates="child", single_parent=True)

        除了设置此参数，“一对多”方面（这里按约定是一对一）也不会可靠地检测到是否有多个 ``Child`` 与单个 ``Parent`` 关联，例如在多个 ``Child`` 对象待处理且未持久化到数据库的情况下。

        无论是否使用 :paramref:`_orm.relationship.single_parent`，建议数据库模式包括 :ref:`unique constraint <schema_unique_constraint>`，以指示 ``Child.parent_id`` 列应是唯一的，以确保在数据库级别一个 ``Child`` 行只能在任何时候引用一个特定的 ``Parent`` 行（有关 ``__table_args__`` 元组语法的背景，请参见 :ref:`orm_declarative_table_configuration`）::

            from sqlalchemy import UniqueConstraint


            class Child(Base):
                __tablename__ = "child_table"

                id: Mapped[int] = mapped_column(primary_key=True)
                parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
                parent: Mapped["Parent"] = relationship(back_populates="child")

                __table_args__ = (UniqueConstraint("parent_id"),)

    .. versionadded:: 2.0  
        
        :func:`_orm.relationship` 构造可以从给定的 :class:`_orm.Mapped` 注释中推导出 :paramref:`_orm.relationship.uselist` 参数的有效值。

.. tab:: 英文

    One To One is essentially a :ref:`relationship_patterns_o2m`
    relationship from a foreign key perspective, but indicates that there will
    only be one row at any time that refers to a particular parent row.

    When using annotated mappings with :class:`_orm.Mapped`, the "one-to-one"
    convention is achieved by applying a non-collection type to the
    :class:`_orm.Mapped` annotation on both sides of the relationship, which will
    imply to the ORM that a collection should not be used on either side, as in the
    example below::

        class Parent(Base):
            __tablename__ = "parent_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            child: Mapped["Child"] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
            parent: Mapped["Parent"] = relationship(back_populates="child")

    Above, when we load a ``Parent`` object, the ``Parent.child`` attribute
    will refer to a single ``Child`` object rather than a collection.  If we
    replace the value of ``Parent.child`` with a new ``Child`` object, the ORM's
    unit of work process will replace the previous ``Child`` row with the new one,
    setting the previous ``child.parent_id`` column to NULL by default unless there
    are specific :ref:`cascade <unitofwork_cascades>` behaviors set up.

    .. tip::

        As mentioned previously, the ORM considers the "one-to-one" pattern as a
        convention, where it makes the assumption that when it loads the
        ``Parent.child`` attribute on a ``Parent`` object, it will get only one
        row back.  If more than one row is returned, the ORM will emit a warning.

        However, the ``Child.parent`` side of the above relationship remains as a
        "many-to-one" relationship.  By itself, it will not detect assignment
        of more than one ``Child``, unless the :paramref:`_orm.relationship.single_parent`
        parameter is set, which may be useful::

            class Child(Base):
                __tablename__ = "child_table"

                id: Mapped[int] = mapped_column(primary_key=True)
                parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
                parent: Mapped["Parent"] = relationship(back_populates="child", single_parent=True)

        Outside of setting this parameter, the "one-to-many" side (which here is
        one-to-one by convention) will also not reliably detect if more than one
        ``Child`` is associated with a single ``Parent``, such as in the case where
        the multiple ``Child`` objects are pending and not database-persistent.

        Whether or not :paramref:`_orm.relationship.single_parent` is used, it is
        recommended that the database schema include a :ref:`unique constraint
        <schema_unique_constraint>` to indicate that the ``Child.parent_id`` column
        should be unique, to ensure at the database level that only one ``Child`` row may refer
        to a particular ``Parent`` row at a time (see :ref:`orm_declarative_table_configuration`
        for background on the ``__table_args__`` tuple syntax)::

            from sqlalchemy import UniqueConstraint


            class Child(Base):
                __tablename__ = "child_table"

                id: Mapped[int] = mapped_column(primary_key=True)
                parent_id: Mapped[int] = mapped_column(ForeignKey("parent_table.id"))
                parent: Mapped["Parent"] = relationship(back_populates="child")

                __table_args__ = (UniqueConstraint("parent_id"),)

    .. versionadded:: 2.0  
        
        The :func:`_orm.relationship` construct can derive
        the effective value of the :paramref:`_orm.relationship.uselist`
        parameter from a given :class:`_orm.Mapped` annotation.

为非注释配置设置 uselist=False
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting uselist=False for non-annotated configurations

.. tab:: 中文

    当使用 :func:`_orm.relationship` 而没有 :class:`_orm.Mapped` 注释的好处时，可以通过在通常为“多”端的位置设置 :paramref:`_orm.relationship.uselist` 参数为 ``False`` 来启用一对一模式，如下所示的非注释声明式配置::

        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            child = relationship("Child", uselist=False, back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(ForeignKey("parent_table.id"))
            parent = relationship("Parent", back_populates="child")

.. tab:: 英文

    When using :func:`_orm.relationship` without the benefit of :class:`_orm.Mapped`
    annotations, the one-to-one pattern can be enabled using the
    :paramref:`_orm.relationship.uselist` parameter set to ``False`` on what
    would normally be the "many" side, illustrated in a non-annotated
    Declarative configuration below::


        class Parent(Base):
            __tablename__ = "parent_table"

            id = mapped_column(Integer, primary_key=True)
            child = relationship("Child", uselist=False, back_populates="parent")


        class Child(Base):
            __tablename__ = "child_table"

            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(ForeignKey("parent_table.id"))
            parent = relationship("Parent", back_populates="child")

.. _relationships_many_to_many:

多对多
~~~~~~~~~~~~

Many To Many

.. tab:: 中文

    多对多关系在两个类之间添加一个关联表。关联表几乎总是作为一个核心 :class:`_schema.Table` 对象或其他核心可选对象（如 :class:`_sql.Join` 对象）给出，并通过 :func:`_orm.relationship` 的 :paramref:`_orm.relationship.secondary` 参数指示。通常，:class:`_schema.Table` 使用与声明基类相关联的 :class:`_schema.MetaData` 对象，以便 :class:`_schema.ForeignKey` 指令可以定位要链接的远程表::

        from __future__ import annotations

        from sqlalchemy import Column
        from sqlalchemy import Table
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        # 注意对于核心表，我们使用 sqlalchemy.Column 构造，
        # 而不是 sqlalchemy.orm.mapped_column
        association_table = Table(
            "association_table",
            Base.metadata,
            Column("left_id", ForeignKey("left_table.id")),
            Column("right_id", ForeignKey("right_table.id")),
        )


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List[Child]] = relationship(secondary=association_table)


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

    .. tip::

        上面的“关联表”建立了外键约束，指向关系两侧的两个实体表。通常省略 ``association.left_id`` 和 ``association.right_id`` 的数据类型，因为它们是从引用表中推断出来的。虽然 SQLAlchemy 并未强制要求，但 **建议** 将引用两个实体表的列设置在 **唯一约束** 或更常见的 **主键约束** 中；这确保了无论应用程序端的问题如何，重复行都不会被持久化到表中::

            association_table = Table(
                "association_table",
                Base.metadata,
                Column("left_id", ForeignKey("left_table.id"), primary_key=True),
                Column("right_id", ForeignKey("right_table.id"), primary_key=True),
            )

.. tab:: 英文

    Many to Many adds an association table between two classes. The association
    table is nearly always given as a Core :class:`_schema.Table` object or
    other Core selectable such as a :class:`_sql.Join` object, and is
    indicated by the :paramref:`_orm.relationship.secondary` argument to
    :func:`_orm.relationship`. Usually, the :class:`_schema.Table` uses the
    :class:`_schema.MetaData` object associated with the declarative base class, so
    that the :class:`_schema.ForeignKey` directives can locate the remote tables
    with which to link::

        from __future__ import annotations

        from sqlalchemy import Column
        from sqlalchemy import Table
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        # note for a Core table, we use the sqlalchemy.Column construct,
        # not sqlalchemy.orm.mapped_column
        association_table = Table(
            "association_table",
            Base.metadata,
            Column("left_id", ForeignKey("left_table.id")),
            Column("right_id", ForeignKey("right_table.id")),
        )


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List[Child]] = relationship(secondary=association_table)


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

    .. tip::

        The "association table" above has foreign key constraints established that
        refer to the two entity tables on either side of the relationship.  The data
        type of each of ``association.left_id`` and ``association.right_id`` is
        normally inferred from that of the referenced table and may be omitted.
        It is also **recommended**, though not in any way required by SQLAlchemy,
        that the columns which refer to the two entity tables are established within
        either a **unique constraint** or more commonly as the **primary key constraint**;
        this ensures that duplicate rows won't be persisted within the table regardless
        of issues on the application side::

            association_table = Table(
                "association_table",
                Base.metadata,
                Column("left_id", ForeignKey("left_table.id"), primary_key=True),
                Column("right_id", ForeignKey("right_table.id"), primary_key=True),
            )

设置双向多对多
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting Bi-Directional Many-to-many

.. tab:: 中文

    对于双向关系，关系的两边都包含一个集合。使用 :paramref:`_orm.relationship.back_populates` 指定，并为每个 :func:`_orm.relationship` 指定公共关联表::

        from __future__ import annotations

        from sqlalchemy import Column
        from sqlalchemy import Table
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        association_table = Table(
            "association_table",
            Base.metadata,
            Column("left_id", ForeignKey("left_table.id"), primary_key=True),
            Column("right_id", ForeignKey("right_table.id"), primary_key=True),
        )


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List[Child]] = relationship(
                secondary=association_table, back_populates="parents"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List[Parent]] = relationship(
                secondary=association_table, back_populates="children"
            )

.. tab:: 英文

    For a bidirectional relationship, both sides of the relationship contain a
    collection.  Specify using :paramref:`_orm.relationship.back_populates`, and
    for each :func:`_orm.relationship` specify the common association table::

        from __future__ import annotations

        from sqlalchemy import Column
        from sqlalchemy import Table
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        association_table = Table(
            "association_table",
            Base.metadata,
            Column("left_id", ForeignKey("left_table.id"), primary_key=True),
            Column("right_id", ForeignKey("right_table.id"), primary_key=True),
        )


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List[Child]] = relationship(
                secondary=association_table, back_populates="parents"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List[Parent]] = relationship(
                secondary=association_table, back_populates="children"
            )

使用后期评估形式作为“次要”参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using a late-evaluated form for the "secondary" argument

.. tab:: 中文

    :paramref:`_orm.relationship.secondary` 参数的 :func:`_orm.relationship` 还接受两种不同的“延迟评估(late evaluated)”形式，包括字符串表名和 lambda 可调用对象。有关背景和示例，请参见 :ref:`orm_declarative_relationship_secondary_eval`。

.. tab:: 英文

    The :paramref:`_orm.relationship.secondary` parameter of
    :func:`_orm.relationship` also accepts two different "late evaluated" forms,
    including string table name as well as lambda callable.   See the section
    :ref:`orm_declarative_relationship_secondary_eval` for background and
    examples.


使用集合、列表或其他集合类型实现多对多
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Sets, Lists, or other Collection Types for Many To Many

.. tab:: 中文

    多对多关系的集合配置与 :ref:`relationship_patterns_o2m` 完全相同，如 :ref:`relationship_patterns_o2m_collection` 中所述。对于使用 :class:`_orm.Mapped` 的带注释映射，可以通过在 :class:`_orm.Mapped` 泛型类中使用的集合类型来指示集合，例如 ``set``::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[Set["Child"]] = relationship(secondary=association_table)

    当使用非注释形式（包括命令式映射）时，与一对多关系一样，可以使用 :paramref:`_orm.relationship.collection_class` 参数传递要用作集合的 Python 类。

    .. seealso::

        :ref:`custom_collections` - 包含有关集合配置的更多详细信息，包括将 :func:`_orm.relationship` 映射到字典的一些技术。

.. tab:: 英文

    Configuration of collections for a Many to Many relationship is identical
    to that of :ref:`relationship_patterns_o2m`, as described at
    :ref:`relationship_patterns_o2m_collection`.    For an annotated mapping
    using :class:`_orm.Mapped`, the collection can be indicated by the
    type of collection used within the :class:`_orm.Mapped` generic class,
    such as ``set``::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[Set["Child"]] = relationship(secondary=association_table)

    When using non-annotated forms including imperative mappings, as is
    the case with one-to-many, the Python
    class to use as a collection may be passed using the
    :paramref:`_orm.relationship.collection_class` parameter.

    .. seealso::

        :ref:`custom_collections` - contains further detail on collection
        configuration including some techniques to map :func:`_orm.relationship`
        to dictionaries.

.. _relationships_many_to_many_deletion:

从多对多表中删除行
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deleting Rows from the Many to Many Table

.. tab:: 中文

    :param:`_orm.relationship.secondary` 参数的 :func:`_orm.relationship` 独有的一个行为是，这里指定的 :class:`_schema.Table` 会自动进行 INSERT 和 DELETE 语句操作，因为对象会从集合中添加或移除。 **无需手动从此表中删除** 。从集合中移除记录的行为将在刷新时删除该行::

        # 行将自动从 "secondary" 表中删除
        myparent.children.remove(somechild)

    一个常见的问题是，当子对象直接传递给 :meth:`.Session.delete` 时，如何删除 "secondary" 表中的行::

        session.delete(somechild)

    这里有几种可能性：

    * 如果存在从 ``Parent`` 到 ``Child`` 的 :func:`_orm.relationship`，但没有将特定 ``Child`` 链接到每个 ``Parent`` 的反向关系，SQLAlchemy 将不会意识到在删除这个特定 ``Child`` 对象时，需要维护链接到 ``Parent`` 的 "secondary" 表。不会删除 "secondary" 表。
    * 如果存在将特定 ``Child`` 链接到每个 ``Parent`` 的关系，假设它被称为 ``Child.parents``，默认情况下，SQLAlchemy 将加载 ``Child.parents`` 集合以定位所有 ``Parent`` 对象，并删除所有在 "secondary" 表中建立此链接的行。请注意，此关系不需要是双向的；SQLAlchemy 仅严格查看与被删除的 ``Child`` 对象相关的每个 :func:`_orm.relationship`。
    * 一个更高性能的选项是使用数据库使用的外键上的 ON DELETE CASCADE 指令。假设数据库支持此功能，数据库本身可以在 "child" 中的引用行被删除时自动删除 "secondary" 表中的行。在这种情况下，SQLAlchemy 可以使用 :paramref:`_orm.relationship.passive_deletes` 指令在 :func:`_orm.relationship` 上指示跳过主动加载 ``Child.parents`` 集合；有关更多详细信息，请参见 :ref:`passive_deletes`。

    再次注意，这些行为*仅*与 :func:`_orm.relationship` 中使用的 :paramref:`_orm.relationship.secondary` 选项相关。如果处理的是显式映射的关联表，并且 *不* 存在于相关 :func:`_orm.relationship` 的 :paramref:`_orm.relationship.secondary` 选项中，可以改用级联规则自动删除相关实体 - 有关此功能的信息，请参见 :ref:`unitofwork_cascades`。

    .. seealso::

        :ref:`cascade_delete_many_to_many`

        :ref:`passive_deletes_many_to_many`

.. tab:: 英文

    A behavior which is unique to the :paramref:`_orm.relationship.secondary`
    argument to :func:`_orm.relationship` is that the :class:`_schema.Table` which
    is specified here is automatically subject to INSERT and DELETE statements, as
    objects are added or removed from the collection. There is **no need to delete
    from this table manually**.   The act of removing a record from the collection
    will have the effect of the row being deleted on flush::
    
        # row will be deleted from the "secondary" table
        # automatically
        myparent.children.remove(somechild)
    
    A question which often arises is how the row in the "secondary" table can be deleted
    when the child object is handed directly to :meth:`.Session.delete`::
    
        session.delete(somechild)
    
    There are several possibilities here:
    
    * If there is a :func:`_orm.relationship` from ``Parent`` to ``Child``, but there is
      **not** a reverse-relationship that links a particular ``Child`` to each ``Parent``,
      SQLAlchemy will not have any awareness that when deleting this particular
      ``Child`` object, it needs to maintain the "secondary" table that links it to
      the ``Parent``.  No delete of the "secondary" table will occur.
    * If there is a relationship that links a particular ``Child`` to each ``Parent``,
      suppose it's called ``Child.parents``, SQLAlchemy by default will load in
      the ``Child.parents`` collection to locate all ``Parent`` objects, and remove
      each row from the "secondary" table which establishes this link.  Note that
      this relationship does not need to be bidirectional; SQLAlchemy is strictly
      looking at every :func:`_orm.relationship` associated with the ``Child`` object
      being deleted.
    * A higher performing option here is to use ON DELETE CASCADE directives
      with the foreign keys used by the database.   Assuming the database supports
      this feature, the database itself can be made to automatically delete rows in the
      "secondary" table as referencing rows in "child" are deleted.   SQLAlchemy
      can be instructed to forego actively loading in the ``Child.parents``
      collection in this case using the :paramref:`_orm.relationship.passive_deletes`
      directive on :func:`_orm.relationship`; see :ref:`passive_deletes` for more details
      on this.
    
    Note again, these behaviors are *only* relevant to the
    :paramref:`_orm.relationship.secondary` option used with
    :func:`_orm.relationship`.   If dealing with association tables that are mapped
    explicitly and are *not* present in the :paramref:`_orm.relationship.secondary`
    option of a relevant :func:`_orm.relationship`, cascade rules can be used
    instead to automatically delete entities in reaction to a related entity being
    deleted - see :ref:`unitofwork_cascades` for information on this feature.
    
    .. seealso::
    
        :ref:`cascade_delete_many_to_many`
    
        :ref:`passive_deletes_many_to_many`


.. _association_pattern:

关联对象
~~~~~~~~~~~~~~~~~~

Association Object

.. tab:: 中文

    关联对象模式是多对多关系的一种变体：它用于当关联表包含超出那些作为父表和子表（或左表和右表）外键的其他列时，这些列最理想地映射到它们自己的 ORM 映射类。这个映射类映射到 :class:`.Table`，该表在使用多对多模式时通常会作为 :paramref:`_orm.relationship.secondary` 指定。

    在关联对象模式中，不使用 :paramref:`_orm.relationship.secondary` 参数；相反，一个类直接映射到关联表。两个单独的 :func:`_orm.relationship` 构造首先将父侧链接到通过一对多映射的关联类，然后将映射的关联类通过多对一链接到子侧，从而形成从父到关联到子的单向关联对象关系。对于双向关系，使用四个 :func:`_orm.relationship` 构造将映射的关联类在两个方向上链接到父和子。

    下面的示例说明了一个新的类 ``Association`` 映射到名为 ``association`` 的 :class:`.Table`；该表现在包括一个名为 ``extra_data`` 的附加列，这是一个字符串值，存储在 ``Parent`` 和 ``Child`` 之间的每个关联中。通过将该表映射到一个显式类，从 ``Parent`` 到 ``Child`` 的基本访问显式使用 ``Association``::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"
            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]
            child: Mapped["Child"] = relationship()


        class Parent(Base):
            __tablename__ = "left_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Association"]] = relationship()


        class Child(Base):
            __tablename__ = "right_table"
            id: Mapped[int] = mapped_column(primary_key=True)

    为了说明双向版本，我们添加了两个更多的 :func:`_orm.relationship` 构造，使用 :paramref:`_orm.relationship.back_populates` 链接到现有的关系::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"
            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]
            child: Mapped["Child"] = relationship(back_populates="parents")
            parent: Mapped["Parent"] = relationship(back_populates="children")


        class Parent(Base):
            __tablename__ = "left_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Association"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "right_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Association"]] = relationship(back_populates="child")

    使用直接形式的关联模式需要在将子对象附加到父对象之前，将子对象与关联实例关联；同样，从父到子的访问通过关联对象进行::

        # 创建父对象，通过关联附加子对象
        p = Parent()
        a = Association(extra_data="some data")
        a.child = Child()
        p.children.append(a)

        # 通过关联迭代子对象，包括关联属性
        for assoc in p.children:
            print(assoc.extra_data)
            print(assoc.child)

    为了增强关联对象模式，使得直接访问 ``Association`` 对象是可选的，SQLAlchemy 提供了 :ref:`associationproxy_toplevel` 扩展。该扩展允许配置属性，以便通过单次访问进行两次“跳跃”，一次“跳跃”到关联对象，第二次跳跃到目标属性。

    .. seealso::

        :ref:`associationproxy_toplevel` - 允许在三类关联对象映射中实现父和子之间的直接“多对多”风格访问。

    .. warning::

        避免将关联对象模式与直接的 :ref:`many-to-many <relationships_many_to_many>` 模式混合使用，因为这会产生在没有特殊步骤的情况下数据可能被不一致地读写的情况；通常使用 :ref:`association proxy <associationproxy_toplevel>` 提供更简洁的访问。有关这种组合引入的警告的详细背景，请参见下一节 :ref:`association_pattern_w_m2m`。

.. tab:: 英文

    The association object pattern is a variant on many-to-many: it's used when an
    association table contains additional columns beyond those which are foreign
    keys to the parent and child (or left and right) tables, columns which are most
    ideally mapped to their own ORM mapped class. This mapped class is mapped
    against the :class:`.Table` that would otherwise be noted as
    :paramref:`_orm.relationship.secondary` when using the many-to-many pattern.

    In the association object pattern, the :paramref:`_orm.relationship.secondary`
    parameter is not used; instead, a class is mapped directly to the association
    table. Two individual :func:`_orm.relationship` constructs then link first the
    parent side to the mapped association class via one to many, and then the
    mapped association class to the child side via many-to-one, to form a
    uni-directional association object relationship from parent, to association, to
    child. For a bi-directional relationship, four :func:`_orm.relationship`
    constructs are used to link the mapped association class to both parent and
    child in both directions.

    The example below illustrates a new class ``Association`` which maps
    to the :class:`.Table` named ``association``; this table now includes
    an additional column called ``extra_data``, which is a string value that
    is stored along with each association between ``Parent`` and
    ``Child``.   By mapping the table to an explicit class, rudimental access
    from ``Parent`` to ``Child`` makes explicit use of ``Association``::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"
            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]
            child: Mapped["Child"] = relationship()


        class Parent(Base):
            __tablename__ = "left_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Association"]] = relationship()


        class Child(Base):
            __tablename__ = "right_table"
            id: Mapped[int] = mapped_column(primary_key=True)

    To illustrate the bi-directional version, we add two more :func:`_orm.relationship`
    constructs, linked to the existing ones using :paramref:`_orm.relationship.back_populates`::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"
            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]
            child: Mapped["Child"] = relationship(back_populates="parents")
            parent: Mapped["Parent"] = relationship(back_populates="children")


        class Parent(Base):
            __tablename__ = "left_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Association"]] = relationship(back_populates="parent")


        class Child(Base):
            __tablename__ = "right_table"
            id: Mapped[int] = mapped_column(primary_key=True)
            parents: Mapped[List["Association"]] = relationship(back_populates="child")

    Working with the association pattern in its direct form requires that child
    objects are associated with an association instance before being appended to
    the parent; similarly, access from parent to child goes through the
    association object::

        # create parent, append a child via association
        p = Parent()
        a = Association(extra_data="some data")
        a.child = Child()
        p.children.append(a)

        # iterate through child objects via association, including association
        # attributes
        for assoc in p.children:
            print(assoc.extra_data)
            print(assoc.child)

    To enhance the association object pattern such that direct
    access to the ``Association`` object is optional, SQLAlchemy
    provides the :ref:`associationproxy_toplevel` extension. This
    extension allows the configuration of attributes which will
    access two "hops" with a single access, one "hop" to the
    associated object, and a second to a target attribute.

    .. seealso::

        :ref:`associationproxy_toplevel` - allows direct "many to many" style
        access between parent and child for a three-class association object mapping.

    .. warning::

        Avoid mixing the association object pattern with the :ref:`many-to-many <relationships_many_to_many>`
        pattern directly, as this produces conditions where data may be read
        and written in an inconsistent fashion without special steps;
        the :ref:`association proxy <associationproxy_toplevel>` is typically
        used to provide more succinct access.  For more detailed background
        on the caveats introduced by this combination, see the next section
        :ref:`association_pattern_w_m2m`.

.. _association_pattern_w_m2m:

将关联对象与多对多访问模式相结合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combining Association Object with Many-to-Many Access Patterns

.. tab:: 中文

    正如前一节提到的，关联对象模式不会自动与同时针对相同表/列使用的多对多模式集成。因此，读取操作可能会返回冲突的数据，写入操作也可能会尝试刷新冲突的更改，导致完整性错误或意外的插入或删除。

    为了说明，下面的示例配置了 ``Parent`` 和 ``Child`` 之间通过 ``Parent.children`` 和 ``Child.parents`` 的双向多对多关系。同时，还配置了一个关联对象关系，通过 ``Parent.child_associations -> Association.child`` 和 ``Child.parent_associations -> Association.parent`` 进行关联::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"

            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]

            # 关联对象 -> 子对象
            child: Mapped["Child"] = relationship(back_populates="parent_associations")

            # 关联对象 -> 父对象
            parent: Mapped["Parent"] = relationship(back_populates="child_associations")


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # 多对多关系到子对象，绕过 `Association` 类
            children: Mapped[List["Child"]] = relationship(
                secondary="association_table", back_populates="parents"
            )

            # 父对象 -> 关联对象 -> 子对象
            child_associations: Mapped[List["Association"]] = relationship(
                back_populates="parent"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # 多对多关系到父对象，绕过 `Association` 类
            parents: Mapped[List["Parent"]] = relationship(
                secondary="association_table", back_populates="children"
            )

            # 子对象 -> 关联对象 -> 父对象
            parent_associations: Mapped[List["Association"]] = relationship(
                back_populates="child"
            )

    使用该 ORM 模型进行更改时，对 ``Parent.children`` 的更改不会与对 ``Parent.child_associations`` 或 ``Child.parent_associations`` 的更改在 Python 中协调；虽然所有这些关系本身将继续正常运行，但一个上的更改在另一个上不会显示，直到 :class:`.Session` 过期，这通常会在 :meth:`.Session.commit` 之后自动发生。

    此外，如果进行了冲突的更改，例如添加一个新的 ``Association`` 对象，同时将相同的相关 ``Child`` 附加到 ``Parent.children``，当工作单元刷新过程进行时，这将引发完整性错误，如下面的示例所示::

        p1 = Parent()
        c1 = Child()
        p1.children.append(c1)

        # 冗余，将在 Association 上导致重复插入
        p1.child_associations.append(Association(child=c1))

    直接将 ``Child`` 附加到 ``Parent.children`` 也意味着在 ``association`` 表中创建行，而不指示 ``association.extra_data`` 列的任何值，该列将接收 ``NULL`` 作为其值。

    如果你知道自己在做什么，使用上述映射是可以的；在不频繁使用“关联对象”模式的情况下，使用多对多关系可能是有理由的，因为沿着单个多对多关系加载关系更容易，这也可以稍微优化 SQL 语句中“secondary”表的使用方式，而不是使用两个单独的关系到显式关联类。至少可以使用 :paramref:`_orm.relationship.viewonly` 参数应用于“secondary”关系，以避免发生冲突的更改，同时防止将 ``NULL`` 写入附加的关联列，如下所示::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # 多对多关系到子对象，绕过 `Association` 类
            children: Mapped[List["Child"]] = relationship(
                secondary="association_table", back_populates="parents", viewonly=True
            )

            # 父对象 -> 关联对象 -> 子对象
            child_associations: Mapped[List["Association"]] = relationship(
                back_populates="parent"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # 多对多关系到父对象，绕过 `Association` 类
            parents: Mapped[List["Parent"]] = relationship(
                secondary="association_table", back_populates="children", viewonly=True
            )

            # 子对象 -> 关联对象 -> 父对象
            parent_associations: Mapped[List["Association"]] = relationship(
                back_populates="child"
            )

    上述映射不会将对 ``Parent.children`` 或 ``Child.parents`` 的任何更改写入数据库，从而防止冲突的写入。然而，如果在与读取 viewonly 集合的同一个事务或 :class:`.Session` 中对这些集合进行更改，则 ``Parent.children`` 或 ``Child.parents`` 的读取数据不一定与从 ``Parent.child_associations`` 或 ``Child.parent_associations`` 读取的数据匹配。如果关联对象关系的使用不频繁，并且与访问多对多集合的代码仔细组织以避免陈旧读取（在极端情况下，直接使用 :meth:`_orm.Session.expire` 在当前事务中刷新集合），这种模式可能是可行的。

    上述模式的一个流行替代方案是，用一个扩展替换直接多对多的 ``Parent.children`` 和 ``Child.parents`` 关系，该扩展将透明地通过 ``Association`` 类代理，同时保持 ORM 的观点一致。该扩展称为 :ref:`Association Proxy <associationproxy_toplevel>`。

    .. seealso::

        :ref:`associationproxy_toplevel` - 允许在三类关联对象映射中实现父和子之间的直接“多对多”风格访问。

.. tab:: 英文

    As mentioned in the previous section, the association object pattern does not
    automatically integrate with usage of the many-to-many pattern against the same
    tables/columns at the same time.  From this it follows that read operations
    may return conflicting data and write operations may also attempt to flush
    conflicting changes, causing either integrity errors or unexpected
    inserts or deletes.

    To illustrate, the example below configures a bidirectional many-to-many relationship
    between ``Parent`` and ``Child`` via ``Parent.children`` and ``Child.parents``.
    At the same time, an association object relationship is also configured,
    between ``Parent.child_associations -> Association.child``
    and ``Child.parent_associations -> Association.parent``::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Association(Base):
            __tablename__ = "association_table"

            left_id: Mapped[int] = mapped_column(ForeignKey("left_table.id"), primary_key=True)
            right_id: Mapped[int] = mapped_column(
                ForeignKey("right_table.id"), primary_key=True
            )
            extra_data: Mapped[Optional[str]]

            # association between Assocation -> Child
            child: Mapped["Child"] = relationship(back_populates="parent_associations")

            # association between Assocation -> Parent
            parent: Mapped["Parent"] = relationship(back_populates="child_associations")


        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # many-to-many relationship to Child, bypassing the `Association` class
            children: Mapped[List["Child"]] = relationship(
                secondary="association_table", back_populates="parents"
            )

            # association between Parent -> Association -> Child
            child_associations: Mapped[List["Association"]] = relationship(
                back_populates="parent"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # many-to-many relationship to Parent, bypassing the `Association` class
            parents: Mapped[List["Parent"]] = relationship(
                secondary="association_table", back_populates="children"
            )

            # association between Child -> Association -> Parent
            parent_associations: Mapped[List["Association"]] = relationship(
                back_populates="child"
            )

    When using this ORM model to make changes, changes made to
    ``Parent.children`` will not be coordinated with changes made to
    ``Parent.child_associations`` or ``Child.parent_associations`` in Python;
    while all of these relationships will continue to function normally by
    themselves, changes on one will not show up in another until the
    :class:`.Session` is expired, which normally occurs automatically after
    :meth:`.Session.commit`.

    Additionally, if conflicting changes are made,
    such as adding a new ``Association`` object while also appending the same
    related ``Child`` to ``Parent.children``, this will raise integrity
    errors when the unit of work flush process proceeds, as in the
    example below::

        p1 = Parent()
        c1 = Child()
        p1.children.append(c1)

        # redundant, will cause a duplicate INSERT on Association
        p1.child_associations.append(Association(child=c1))

    Appending ``Child`` to ``Parent.children`` directly also implies the
    creation of rows in the ``association`` table without indicating any
    value for the ``association.extra_data`` column, which will receive
    ``NULL`` for its value.

    It's fine to use a mapping like the above if you know what you're doing; there
    may be good reason to use many-to-many relationships in the case where use
    of the "association object" pattern is infrequent, which is that it's easier to
    load relationships along a single many-to-many relationship, which can also
    optimize slightly better how the "secondary" table is used in SQL statements,
    compared to how two separate relationships to an explicit association class is
    used.   It's at least a good idea to apply the
    :paramref:`_orm.relationship.viewonly` parameter
    to the "secondary" relationship to avoid the issue of conflicting
    changes occurring, as well as preventing ``NULL`` being written to the
    additional association columns, as below::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # many-to-many relationship to Child, bypassing the `Association` class
            children: Mapped[List["Child"]] = relationship(
                secondary="association_table", back_populates="parents", viewonly=True
            )

            # association between Parent -> Association -> Child
            child_associations: Mapped[List["Association"]] = relationship(
                back_populates="parent"
            )


        class Child(Base):
            __tablename__ = "right_table"

            id: Mapped[int] = mapped_column(primary_key=True)

            # many-to-many relationship to Parent, bypassing the `Association` class
            parents: Mapped[List["Parent"]] = relationship(
                secondary="association_table", back_populates="children", viewonly=True
            )

            # association between Child -> Association -> Parent
            parent_associations: Mapped[List["Association"]] = relationship(
                back_populates="child"
            )

    The above mapping will not write any changes to ``Parent.children`` or
    ``Child.parents`` to the database, preventing conflicting writes.  However, reads
    of ``Parent.children`` or ``Child.parents`` will not necessarily match the data
    that's read from ``Parent.child_associations`` or ``Child.parent_associations``,
    if changes are being made to these collections within the same transaction
    or :class:`.Session` as where the viewonly collections are being read.  If
    use of the association object relationships is infrequent and is carefully
    organized against code that accesses the many-to-many collections to avoid
    stale reads (in extreme cases, making direct use of :meth:`_orm.Session.expire`
    to cause collections to be refreshed within the current transaction), the pattern may be feasible.

    A popular alternative to the above pattern is one where the direct many-to-many
    ``Parent.children`` and ``Child.parents`` relationships are replaced with
    an extension that will transparently proxy through the ``Association``
    class, while keeping everything consistent from the ORM's point of
    view.  This extension is known as the :ref:`Association Proxy <associationproxy_toplevel>`.

    .. seealso::

        :ref:`associationproxy_toplevel` - allows direct "many to many" style
        access between parent and child for a three-class association object mapping.

.. _orm_declarative_relationship_eval:

关系参数的后期评估
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Late-Evaluation of Relationship Arguments

.. tab:: 中文

    正如前几节所述，大多数示例中映射的各种 :func:`_orm.relationship` 构造使用字符串名称引用其目标类，而不是类本身，例如在使用 :class:`_orm.Mapped` 时，将生成仅在运行时作为字符串存在的前向引用::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            # ...

            parent: Mapped["Parent"] = relationship(back_populates="children")

    类似地，在使用非注释形式（如非注释声明式或命令式映射）时，:func:`_orm.relationship` 构造也直接支持字符串名称::

        registry.map_imperatively(
            Parent,
            parent_table,
            properties={"children": relationship("Child", back_populates="parent")},
        )

        registry.map_imperatively(
            Child,
            child_table,
            properties={"parent": relationship("Parent", back_populates="children")},
        )

    这些字符串名称在映射解析阶段解析为类，这是一个内部过程，通常在定义所有映射之后触发，通常在首次使用映射本身时触发。:class:`_orm.registry` 对象是存储这些名称并解析为它们引用的映射类的容器。

    除了 :func:`_orm.relationship` 的主要类参数外，还可以将依赖于尚未定义的类上的列的其他参数指定为 Python 函数，或更常见地指定为字符串。对于这些参数中的大多数，除主要参数外，字符串输入将作为 Python 表达式使用 Python 的内置 eval() 函数进行评估，因为它们旨在接收完整的 SQL 表达式。

    .. warning:: 
        
        由于使用 Python ``eval()`` 函数解释传递给 :func:`_orm.relationship` 映射配置构造的延迟评估字符串参数，这些参数不应重新用于接收不受信任的用户输入； ``eval()`` 对不受信任的用户输入 **不安全**。

    在此评估中可用的完整命名空间包括为此声明基础映射的所有类，以及 ``sqlalchemy`` 包的内容，包括表达式函数如 :func:`_sql.desc` 和 :attr:`_functions.func`::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                order_by="desc(Child.email_address)",
                primaryjoin="Parent.id == Child.parent_id",
            )

    对于多个模块包含同名类的情况，字符串类名称也可以在任何这些字符串表达式中指定为模块限定路径::

        class Parent(Base):
            # ...

            children: Mapped[List["myapp.mymodel.Child"]] = relationship(
                order_by="desc(myapp.mymodel.Child.email_address)",
                primaryjoin="myapp.mymodel.Parent.id == myapp.mymodel.Child.parent_id",
            )

    在上述示例中，传递给 :class:`_orm.Mapped` 的字符串可以通过直接传递类位置字符串到 :paramref:`_orm.relationship.argument` 进行消歧。下面说明了 ``Child`` 的仅类型导入，结合将在 :class:`_orm.registry` 中搜索正确名称的运行时说明符::

        import typing

        if typing.TYPE_CHECKING:
            from myapp.mymodel import Child


        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                "myapp.mymodel.Child",
                order_by="desc(myapp.mymodel.Child.email_address)",
                primaryjoin="myapp.mymodel.Parent.id == myapp.mymodel.Child.parent_id",
            )

    限定路径可以是消除名称歧义的任何部分路径。例如，要在 ``myapp.model1.Child`` 和 ``myapp.model2.Child`` 之间消除歧义，可以指定 ``model1.Child`` 或 ``model2.Child``::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                "model1.Child",
                order_by="desc(mymodel1.Child.email_address)",
                primaryjoin="Parent.id == model1.Child.parent_id",
            )

    :func:`_orm.relationship` 构造还接受 Python 函数或 lambda 作为输入。这种 Python 功能方法可能如下所示::

        import typing

        from sqlalchemy import desc

        if typing.TYPE_CHECKING:
            from myapplication import Child


        def _resolve_child_model():
            from myapplication import Child

            return Child


        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                _resolve_child_model,
                order_by=lambda: desc(_resolve_child_model().email_address),
                primaryjoin=lambda: Parent.id == _resolve_child_model().parent_id,
            )

    接受 Python 函数/lambda 或字符串并传递给 ``eval()`` 的参数的完整列表包括：

    * :paramref:`_orm.relationship.order_by`

    * :paramref:`_orm.relationship.primaryjoin`

    * :paramref:`_orm.relationship.secondaryjoin`

    * :paramref:`_orm.relationship.secondary`

    * :paramref:`_orm.relationship.remote_side`

    * :paramref:`_orm.relationship.foreign_keys`

    * :paramref:`_orm.relationship._user_defined_foreign_keys`

    .. warning::

        如前所述，传递给 :func:`_orm.relationship` 的上述参数将作为 Python 代码表达式使用 eval() 进行评估。 **不要将不受信任的输入传递给这些参数。**

.. tab:: 英文

    Most of the examples in the preceding sections illustrate mappings
    where the various :func:`_orm.relationship` constructs refer to their target
    classes using a string name, rather than the class itself, such as when
    using :class:`_orm.Mapped`, a forward reference is generated that exists
    at runtime only as a string::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(back_populates="parent")


        class Child(Base):
            # ...

            parent: Mapped["Parent"] = relationship(back_populates="children")

    Similarly, when using non-annotated forms such as non-annotated Declarative
    or Imperative mappings, a string name is also supported directly by
    the :func:`_orm.relationship` construct::

        registry.map_imperatively(
            Parent,
            parent_table,
            properties={"children": relationship("Child", back_populates="parent")},
        )

        registry.map_imperatively(
            Child,
            child_table,
            properties={"parent": relationship("Parent", back_populates="children")},
        )

    These string names are resolved into classes in the mapper resolution stage,
    which is an internal process that occurs typically after all mappings have been
    defined and is normally triggered by the first usage of the mappings
    themselves.  The :class:`_orm.registry` object is the container where these
    names are stored and resolved to the mapped classes to which they refer.

    In addition to the main class argument for :func:`_orm.relationship`,
    other arguments which depend upon the columns present on an as-yet
    undefined class may also be specified either as Python functions, or more
    commonly as strings.   For most of these
    arguments except that of the main argument, string inputs are
    **evaluated as Python expressions using Python's built-in eval() function**,
    as they are intended to receive complete SQL expressions.

    .. warning:: As the Python ``eval()`` function is used to interpret the
    late-evaluated string arguments passed to :func:`_orm.relationship` mapper
    configuration construct, these arguments should **not** be repurposed
    such that they would receive untrusted user input; ``eval()`` is
    **not secure** against untrusted user input.

    The full namespace available within this evaluation includes all classes mapped
    for this declarative base, as well as the contents of the ``sqlalchemy``
    package, including expression functions like :func:`_sql.desc` and
    :attr:`_functions.func`::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                order_by="desc(Child.email_address)",
                primaryjoin="Parent.id == Child.parent_id",
            )

    For the case where more than one module contains a class of the same name,
    string class names can also be specified as module-qualified paths
    within any of these string expressions::

        class Parent(Base):
            # ...

            children: Mapped[List["myapp.mymodel.Child"]] = relationship(
                order_by="desc(myapp.mymodel.Child.email_address)",
                primaryjoin="myapp.mymodel.Parent.id == myapp.mymodel.Child.parent_id",
            )

    In an example like the above, the string passed to :class:`_orm.Mapped`
    can be disambiguated from a specific class argument by passing the class
    location string directly to :paramref:`_orm.relationship.argument` as well.
    Below illustrates a typing-only import for ``Child``, combined with a
    runtime specifier for the target class that will search for the correct
    name within the :class:`_orm.registry`::

        import typing

        if typing.TYPE_CHECKING:
            from myapp.mymodel import Child


        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                "myapp.mymodel.Child",
                order_by="desc(myapp.mymodel.Child.email_address)",
                primaryjoin="myapp.mymodel.Parent.id == myapp.mymodel.Child.parent_id",
            )

    The qualified path can be any partial path that removes ambiguity between
    the names.  For example, to disambiguate between
    ``myapp.model1.Child`` and ``myapp.model2.Child``,
    we can specify ``model1.Child`` or ``model2.Child``::

        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                "model1.Child",
                order_by="desc(mymodel1.Child.email_address)",
                primaryjoin="Parent.id == model1.Child.parent_id",
            )

    The :func:`_orm.relationship` construct also accepts Python functions or
    lambdas as input for these arguments.  A Python functional approach might look
    like the following::

        import typing

        from sqlalchemy import desc

        if typing.TYPE_CHECKING:
            from myapplication import Child


        def _resolve_child_model():
            from myapplication import Child

            return Child


        class Parent(Base):
            # ...

            children: Mapped[List["Child"]] = relationship(
                _resolve_child_model,
                order_by=lambda: desc(_resolve_child_model().email_address),
                primaryjoin=lambda: Parent.id == _resolve_child_model().parent_id,
            )

    The full list of parameters which accept Python functions/lambdas or strings
    that will be passed to ``eval()`` are:

    * :paramref:`_orm.relationship.order_by`

    * :paramref:`_orm.relationship.primaryjoin`

    * :paramref:`_orm.relationship.secondaryjoin`

    * :paramref:`_orm.relationship.secondary`

    * :paramref:`_orm.relationship.remote_side`

    * :paramref:`_orm.relationship.foreign_keys`

    * :paramref:`_orm.relationship._user_defined_foreign_keys`

    .. warning::

        As stated previously, the above parameters to :func:`_orm.relationship`
        are **evaluated as Python code expressions using eval().  DO NOT PASS
        UNTRUSTED INPUT TO THESE ARGUMENTS.**

.. _orm_declarative_table_adding_relationship:

在声明后向映射类添加关系
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding Relationships to Mapped Classes After Declaration

.. tab:: 中文

    还需要注意的是，与 :ref:`orm_declarative_table_adding_columns` 中描述的类似，任何 :class:`_orm.MapperProperty` 构造都可以随时添加到声明式基类映射中（注意在这种情况下不支持带注释的形式）。如果我们想在 ``Address`` 类可用后实现此 :func:`_orm.relationship`，我们也可以在之后应用它::

        # 首先，模块 A，其中 Child 尚未创建，
        # 我们创建一个对 Child 一无所知的 Parent 类


        class Parent(Base): ...


        # ... 稍后，在模块 B 中，该模块在模块 A 之后导入：


        class Child(Base): ...


        from module_a import Parent

        # 将 User.addresses 关系分配为类变量。
        # 声明式基类将拦截此操作并映射关系。
        Parent.children = relationship(Child, primaryjoin=Child.parent_id == Parent.id)

    与 ORM 映射列的情况一样，:class:`_orm.Mapped` 注释类型无法参与此操作；因此，相关类必须直接在 :func:`_orm.relationship` 构造中指定，可以是类本身、类的字符串名称或返回目标类引用的可调用函数。

    .. note:: 
        
        与 ORM 映射列的情况一样，将映射属性分配给已映射的类仅在使用“声明式基类”类时才会正确运行，这意味着用户定义的 :class:`_orm.DeclarativeBase` 子类或 :func:`_orm.declarative_base` 或 :meth:`_orm.registry.generate_base` 返回的动态生成类。此“基类”包括一个 Python 元类，该元类实现了一个特殊的 ``__setattr__()`` 方法来拦截这些操作。

        如果类使用装饰器（如 :meth:`_orm.registry.mapped`）或命令式函数（如 :meth:`_orm.registry.map_imperatively`）进行映射，则运行时将类映射属性分配给映射类将 **不起作用**。

.. tab:: 英文

    It should also be noted that in a similar way as described at
    :ref:`orm_declarative_table_adding_columns`, any :class:`_orm.MapperProperty`
    construct can be added to a declarative base mapping at any time
    (noting that annotated forms are not supported in this context).  If
    we wanted to implement this :func:`_orm.relationship` after the ``Address``
    class were available, we could also apply it afterwards::

        # first, module A, where Child has not been created yet,
        # we create a Parent class which knows nothing about Child


        class Parent(Base): ...


        # ... later, in Module B, which is imported after module A:


        class Child(Base): ...


        from module_a import Parent

        # assign the User.addresses relationship as a class variable.  The
        # declarative base class will intercept this and map the relationship.
        Parent.children = relationship(Child, primaryjoin=Child.parent_id == Parent.id)

    As is the case for ORM mapped columns, there's no capability for
    the :class:`_orm.Mapped` annotation type to take part in this operation;
    therefore, the related class must be specified directly within the
    :func:`_orm.relationship` construct, either as the class itself, the string
    name of the class, or a callable function that returns a reference to
    the target class.

    .. note:: 
        
        As is the case for ORM mapped columns, assignment of mapped
        properties to an already mapped class will only
        function correctly if the "declarative base" class is used, meaning
        the user-defined subclass of :class:`_orm.DeclarativeBase` or the
        dynamically generated class returned by :func:`_orm.declarative_base`
        or :meth:`_orm.registry.generate_base`.   This "base" class includes
        a Python metaclass which implements a special ``__setattr__()`` method
        that intercepts these operations.

        Runtime assignment of class-mapped attributes to a mapped class will **not** work
        if the class is mapped using decorators like :meth:`_orm.registry.mapped`
        or imperative functions like :meth:`_orm.registry.map_imperatively`.


.. _orm_declarative_relationship_secondary_eval:

使用后期评估形式作为多对多的“次要”参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using a late-evaluated form for the "secondary" argument of many-to-many

.. tab:: 中文

    多对多关系使用 :paramref:`_orm.relationship.secondary` 参数，通常表示对通常未映射的 :class:`_schema.Table` 对象或其他核心可选对象的引用。使用 lambda 可调用对象进行延迟评估是典型的做法。

    对于 :ref:`relationships_many_to_many` 中给出的示例，如果我们假设 ``association_table`` :class:`.Table` 对象将在模块中映射类本身之后的某个时间点定义，我们可以使用 lambda 编写 :func:`_orm.relationship` 如下::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(
                "Child", secondary=lambda: association_table
            )

    对于作为 **有效 Python 标识符** 的表名的快捷方式，:paramref:`_orm.relationship.secondary` 参数也可以作为字符串传递，其中解析通过将字符串作为 Python 表达式评估来工作，简单的标识符名称链接到当前 :class:`_orm.registry` 引用的相同名称的 :class:`_schema.Table` 对象。

    在下面的示例中，表达式 ``"association_table"`` 作为名为“association_table”的变量进行评估，该变量根据 :class:`.MetaData` 集合中的表名解析::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(secondary="association_table")

    .. note:: 
        
        作为字符串传递时，传递给 :paramref:`_orm.relationship.secondary` 的名称 **必须是有效的 Python 标识符** ，以字母开头并且仅包含字母数字字符或下划线。其他字符（如破折号等）将被解释为 Python 操作符，这将无法解析为给定名称。请考虑使用 lambda 表达式而不是字符串以提高清晰度。

    .. warning:: 
        
        作为字符串传递时，:paramref:`_orm.relationship.secondary` 参数使用 Python 的 ``eval()`` 函数进行解释，即使它通常是表的名称。 **不要将不受信任的输入传递给此字符串**。

.. tab:: 英文

    Many-to-many relationships make use of the
    :paramref:`_orm.relationship.secondary` parameter, which ordinarily
    indicates a reference to a typically non-mapped :class:`_schema.Table`
    object or other Core selectable object.  Late evaluation
    using a lambda callable is typical.

    For the example given at :ref:`relationships_many_to_many`, if we assumed
    that the ``association_table`` :class:`.Table` object would be defined at a point later on in the
    module than the mapped class itself, we may write the :func:`_orm.relationship`
    using a lambda as::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(
                "Child", secondary=lambda: association_table
            )

    As a shortcut for table names that are also **valid Python identifiers**, the
    :paramref:`_orm.relationship.secondary` parameter may also be passed as a
    string, where resolution works by evaluation of the string as a Python
    expression, with simple identifier names linked to same-named
    :class:`_schema.Table` objects that are present in the same
    :class:`_schema.MetaData` collection referenced by the current
    :class:`_orm.registry`.

    In the example below, the expression
    ``"association_table"`` is evaluated as a variable
    named "association_table" that is resolved against the table names within
    the :class:`.MetaData` collection::

        class Parent(Base):
            __tablename__ = "left_table"

            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(secondary="association_table")

    .. note:: 
        
        When passed as a string, the name passed to
        :paramref:`_orm.relationship.secondary` **must be a valid Python identifier**
        starting with a letter and containing only alphanumeric characters or
        underscores.   Other characters such as dashes etc. will be interpreted
        as Python operators which will not resolve to the name given.  Please consider
        using lambda expressions rather than strings for improved clarity.

    .. warning:: 
        
        When passed as a string,
        :paramref:`_orm.relationship.secondary` argument is interpreted using Python's
        ``eval()`` function, even though it's typically the name of a table.
        **DO NOT PASS UNTRUSTED INPUT TO THIS STRING**.



