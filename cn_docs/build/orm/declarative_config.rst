.. _orm_declarative_mapper_config_toplevel:

=============================================
使用声明式映射器配置
=============================================

Mapper Configuration with Declarative

.. tab:: 中文

    :ref:`orm_mapper_configuration_overview` 部分讨论了 :class:`_orm.Mapper` 构造的一般配置元素，这是定义特定用户定义类如何映射到数据库表或其他SQL构造的结构。以下部分描述了声明式系统如何构建 :class:`_orm.Mapper` 的具体细节。

.. tab:: 英文

    The section :ref:`orm_mapper_configuration_overview` discusses the general
    configurational elements of a :class:`_orm.Mapper` construct, which is the
    structure that defines how a particular user defined class is mapped to a
    database table or other SQL construct.    The following sections describe
    specific details about how the declarative system goes about constructing
    the :class:`_orm.Mapper`.

.. _orm_declarative_properties:

使用声明式定义映射属性
--------------------------------------------

Defining Mapped Properties with Declarative

.. tab:: 中文

    :ref:`orm_declarative_table_config_toplevel` 部分给出的示例展示了使用 :func:`_orm.mapped_column` 构造的表绑定列的映射。除了表绑定列外，还有几种其他类型的ORM映射构造可以配置，最常见的是 :func:`_orm.relationship` 构造。其他类型的属性包括使用 :func:`_orm.column_property` 构造定义的SQL表达式和使用 :func:`_orm.composite` 构造的多列映射。

    虽然 :ref:`命令式映射 <orm_imperative_mapping>` 使用 :ref:`properties <orm_mapping_properties>` 字典来建立所有映射类属性，但在声明式映射中，这些属性都是在类定义中内联指定的，在声明式表映射的情况下，这些属性与将用于生成 :class:`_schema.Table` 对象的 :class:`_schema.Column` 对象一起内联。

    使用 ``User`` 和 ``Address`` 的示例映射，我们可以说明不仅包括 :func:`_orm.mapped_column` 对象，还包括关系和SQL表达式的声明式表映射::

        from typing import List
        from typing import Optional

        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy import Text
        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            firstname: Mapped[str] = mapped_column(String(50))
            lastname: Mapped[str] = mapped_column(String(50))
            fullname: Mapped[str] = column_property(firstname + " " + lastname)

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        class Address(Base):
            __tablename__ = "address"

            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]
            address_statistics: Mapped[Optional[str]] = mapped_column(Text, deferred=True)

            user: Mapped["User"] = relationship(back_populates="addresses")

    上述声明式表映射具有两个表，每个表都有一个引用另一个的 :func:`_orm.relationship`，以及由 :func:`_orm.column_property` 映射的简单SQL表达式和一个指示加载应在 "延迟(deferred)" 基础上进行的额外 :func:`_orm.mapped_column`，由 :paramref:`_orm.mapped_column.deferred` 关键字定义。有关这些特定概念的更多文档，请参见 :ref:`relationship_patterns`、:ref:`mapper_column_property_sql_expressions` 和 :ref:`orm_queryguide_column_deferral`。

    如上所示，可以使用“混合表(hybrid table)”风格在声明式映射中指定属性；直接作为表一部分的 :class:`_schema.Column` 对象移入 :class:`_schema.Table` 定义，但其他所有内容，包括组合SQL表达式，仍将在类定义中内联。需要直接引用 :class:`_schema.Column` 的构造将以 :class:`_schema.Table` 对象的形式引用它。使用混合表样式说明上述映射::

        # 使用声明式和命令式表映射属性
        # 即 __table__

        from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import deferred
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __table__ = Table(
                "user",
                Base.metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String),
                Column("firstname", String(50)),
                Column("lastname", String(50)),
            )

            fullname = column_property(__table__.c.firstname + " " + __table__.c.lastname)

            addresses = relationship("Address", back_populates="user")


        class Address(Base):
            __table__ = Table(
                "address",
                Base.metadata,
                Column("id", Integer, primary_key=True),
                Column("user_id", ForeignKey("user.id")),
                Column("email_address", String),
                Column("address_statistics", Text),
            )

            address_statistics = deferred(__table__.c.address_statistics)

            user = relationship("User", back_populates="addresses")

    上面需要注意的事项：

    * 地址 :class:`_schema.Table` 包含一个名为 ``address_statistics`` 的列，但我们在同一个属性名下重新映射该列，以便由 :func:`_orm.deferred` 构造控制。

    * 对于声明式表和混合表映射，当我们定义 :class:`_schema.ForeignKey` 构造时，我们总是使用 **表名(table name)** 命名目标表，而不是映射类名。

    * 当我们定义 :func:`_orm.relationship` 构造时，由于这些构造在映射类之间建立了链接，其中一个类必然在另一个类之前定义，我们可以使用类名字符串引用远程类。这种功能还扩展到 :func:`_orm.relationship` 上指定的其他参数，如 "主连接(primary join)" 和 "排序(order by)" 参数。有关详细信息，请参见 :ref:`orm_declarative_relationship_eval` 部分。

.. tab:: 英文

    The examples given at :ref:`orm_declarative_table_config_toplevel`
    illustrate mappings against table-bound columns, using the :func:`_orm.mapped_column`
    construct.  There are several other varieties of ORM mapped constructs
    that may be configured besides table-bound columns, the most common being the
    :func:`_orm.relationship` construct.  Other kinds of properties include
    SQL expressions that are defined using the :func:`_orm.column_property`
    construct and multiple-column mappings using the :func:`_orm.composite`
    construct.
    
    While an :ref:`imperative mapping <orm_imperative_mapping>` makes use of
    the :ref:`properties <orm_mapping_properties>` dictionary to establish
    all the mapped class attributes, in the declarative
    mapping, these properties are all specified inline with the class definition,
    which in the case of a declarative table mapping are inline with the
    :class:`_schema.Column` objects that will be used to generate a
    :class:`_schema.Table` object.
    
    Working with the example mapping of ``User`` and ``Address``, we may illustrate
    a declarative table mapping that includes not just :func:`_orm.mapped_column`
    objects but also relationships and SQL expressions::
    
        from typing import List
        from typing import Optional
    
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy import Text
        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
    
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            firstname: Mapped[str] = mapped_column(String(50))
            lastname: Mapped[str] = mapped_column(String(50))
            fullname: Mapped[str] = column_property(firstname + " " + lastname)
    
            addresses: Mapped[List["Address"]] = relationship(back_populates="user")
    
    
        class Address(Base):
            __tablename__ = "address"
    
            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]
            address_statistics: Mapped[Optional[str]] = mapped_column(Text, deferred=True)
    
            user: Mapped["User"] = relationship(back_populates="addresses")
    
    The above declarative table mapping features two tables, each with a
    :func:`_orm.relationship` referring to the other, as well as a simple
    SQL expression mapped by :func:`_orm.column_property`, and an additional
    :func:`_orm.mapped_column` that indicates loading should be on a
    "deferred" basis as defined
    by the :paramref:`_orm.mapped_column.deferred` keyword.    More documentation
    on these particular concepts may be found at :ref:`relationship_patterns`,
    :ref:`mapper_column_property_sql_expressions`, and :ref:`orm_queryguide_column_deferral`.
    
    Properties may be specified with a declarative mapping as above using
    "hybrid table" style as well; the :class:`_schema.Column` objects that
    are directly part of a table move into the :class:`_schema.Table` definition
    but everything else, including composed SQL expressions, would still be
    inline with the class definition.  Constructs that need to refer to a
    :class:`_schema.Column` directly would reference it in terms of the
    :class:`_schema.Table` object.  To illustrate the above mapping using
    hybrid table style::
    
        # mapping attributes using declarative with imperative table
        # i.e. __table__
    
        from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import deferred
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __table__ = Table(
                "user",
                Base.metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String),
                Column("firstname", String(50)),
                Column("lastname", String(50)),
            )
    
            fullname = column_property(__table__.c.firstname + " " + __table__.c.lastname)
    
            addresses = relationship("Address", back_populates="user")
    
    
        class Address(Base):
            __table__ = Table(
                "address",
                Base.metadata,
                Column("id", Integer, primary_key=True),
                Column("user_id", ForeignKey("user.id")),
                Column("email_address", String),
                Column("address_statistics", Text),
            )
    
            address_statistics = deferred(__table__.c.address_statistics)
    
            user = relationship("User", back_populates="addresses")
    
    Things to note above:
    
    * The address :class:`_schema.Table` contains a column called ``address_statistics``,
      however we re-map this column under the same attribute name to be under
      the control of a :func:`_orm.deferred` construct.
    
    * With both declararative table and hybrid table mappings, when we define a
      :class:`_schema.ForeignKey` construct, we always name the target table
      using the **table name**, and not the mapped class name.
    
    * When we define :func:`_orm.relationship` constructs, as these constructs
      create a linkage between two mapped classes where one necessarily is defined
      before the other, we can refer to the remote class using its string name.
      This functionality also extends into the area of other arguments specified
      on the :func:`_orm.relationship` such as the "primary join" and "order by"
      arguments.   See the section :ref:`orm_declarative_relationship_eval` for
      details on this.
    
    
.. _orm_declarative_mapper_options:

使用声明式映射器配置选项
----------------------------------------------

Mapper Configuration Options with Declarative

.. tab:: 中文

    对于所有映射形式，类的映射是通过成为 :class:`_orm.Mapper` 对象一部分的参数配置的。最终接收这些参数的函数是 :class:`_orm.Mapper` 函数，并由定义在 :class:`_orm.registry` 对象上的前端映射函数传递给它。

    对于声明式映射形式，映射参数使用声明式类变量 ``__mapper_args__`` 指定，这是一个作为关键字参数传递给 :class:`_orm.Mapper` 函数的字典。一些示例：

    **映射特定的主键列(Map Specific Primary Key Columns)**

    下面的示例说明了 :paramref:`_orm.Mapper.primary_key` 参数的声明式级别设置，它独立于模式级别的主键约束，建立了ORM应作为类的主键考虑的特定列::

        class GroupUsers(Base):
            __tablename__ = "group_users"

            user_id = mapped_column(String(40))
            group_id = mapped_column(String(40))

            __mapper_args__ = {"primary_key": [user_id, group_id]}

    .. seealso::

        :ref:`mapper_primary_key` - 有关将显式列映射为主键列的ORM映射的更多背景

    **版本ID列(Version ID Column)**

    下面的示例说明了 :paramref:`_orm.Mapper.version_id_col` 和 :paramref:`_orm.Mapper.version_id_generator` 参数的声明式级别设置，这些参数配置了在 :term:`unit of work` 刷新过程中更新和检查的ORM维护的版本计数器::

        from datetime import datetime


        class Widget(Base):
            __tablename__ = "widgets"

            id = mapped_column(Integer, primary_key=True)
            timestamp = mapped_column(DateTime, nullable=False)

            __mapper_args__ = {
                "version_id_col": timestamp,
                "version_id_generator": lambda v: datetime.now(),
            }

    .. seealso::

        :ref:`mapper_version_counter` - 有关ORM版本计数器功能的背景

    **单表继承(Single Table Inheritance)**

    下面的示例说明了 :paramref:`_orm.Mapper.polymorphic_on` 和 :paramref:`_orm.Mapper.polymorphic_identity` 参数的声明式级别设置，这些参数在配置单表继承映射时使用::

        class Person(Base):
            __tablename__ = "person"

            person_id = mapped_column(Integer, primary_key=True)
            type = mapped_column(String, nullable=False)

            __mapper_args__ = dict(
                polymorphic_on=type,
                polymorphic_identity="person",
            )


        class Employee(Person):
            __mapper_args__ = dict(
                polymorphic_identity="employee",
            )

    .. seealso::

        :ref:`single_inheritance` - 有关ORM单表继承映射功能的背景。

.. tab:: 英文

    With all mapping forms, the mapping of the class is configured through
    parameters that become part of the :class:`_orm.Mapper` object.
    The function which ultimately receives these arguments is the
    :class:`_orm.Mapper` function, and are delivered to it from one of
    the front-facing mapping functions defined on the :class:`_orm.registry`
    object.

    For the declarative form of mapping, mapper arguments are specified
    using the ``__mapper_args__`` declarative class variable, which is a dictionary
    that is passed as keyword arguments to the :class:`_orm.Mapper` function.
    Some examples:

    **Map Specific Primary Key Columns**

    The example below illustrates Declarative-level settings for the
    :paramref:`_orm.Mapper.primary_key` parameter, which establishes
    particular columns as part of what the ORM should consider to be a primary
    key for the class, independently of schema-level primary key constraints::

        class GroupUsers(Base):
            __tablename__ = "group_users"

            user_id = mapped_column(String(40))
            group_id = mapped_column(String(40))

            __mapper_args__ = {"primary_key": [user_id, group_id]}

    .. seealso::

        :ref:`mapper_primary_key` - further background on ORM mapping of explicit
        columns as primary key columns

    **Version ID Column**

    The example below illustrates Declarative-level settings for the
    :paramref:`_orm.Mapper.version_id_col` and
    :paramref:`_orm.Mapper.version_id_generator` parameters, which configure
    an ORM-maintained version counter that is updated and checked within the
    :term:`unit of work` flush process::

        from datetime import datetime


        class Widget(Base):
            __tablename__ = "widgets"

            id = mapped_column(Integer, primary_key=True)
            timestamp = mapped_column(DateTime, nullable=False)

            __mapper_args__ = {
                "version_id_col": timestamp,
                "version_id_generator": lambda v: datetime.now(),
            }

    .. seealso::

        :ref:`mapper_version_counter` - background on the ORM version counter feature

    **Single Table Inheritance**

    The example below illustrates Declarative-level settings for the
    :paramref:`_orm.Mapper.polymorphic_on` and
    :paramref:`_orm.Mapper.polymorphic_identity` parameters, which are used when
    configuring a single-table inheritance mapping::

        class Person(Base):
            __tablename__ = "person"

            person_id = mapped_column(Integer, primary_key=True)
            type = mapped_column(String, nullable=False)

            __mapper_args__ = dict(
                polymorphic_on=type,
                polymorphic_identity="person",
            )


        class Employee(Person):
            __mapper_args__ = dict(
                polymorphic_identity="employee",
            )

    .. seealso::

        :ref:`single_inheritance` - background on the ORM single table inheritance mapping feature.

动态构造映射器参数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Constructing mapper arguments dynamically

.. tab:: 中文

    ``__mapper_args__`` 字典可以通过使用 :func:`_orm.declared_attr` 构造从类绑定的描述符方法生成，而不是从固定字典生成。这对于创建从表配置或映射类的其他方面程序生成的映射器参数非常有用。当使用声明式混入或抽象基类时，动态 ``__mapper_args__`` 属性通常很有用。

    例如，为了从映射中省略具有特殊 :attr:`.Column.info` 值的任何列，可以使用 ``__mapper_args__`` 方法从 ``cls.__table__`` 属性扫描这些列并将它们传递给 :paramref:`_orm.Mapper.exclude_properties` 集合::

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import select
        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr


        class ExcludeColsWFlag:
            @declared_attr
            def __mapper_args__(cls):
                return {
                    "exclude_properties": [
                        column.key
                        for column in cls.__table__.c
                        if column.info.get("exclude", False)
                    ]
                }


        class Base(DeclarativeBase):
            pass


        class SomeClass(ExcludeColsWFlag, Base):
            __tablename__ = "some_table"

            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String)
            not_needed = mapped_column(String, info={"exclude": True})

    上面， ``ExcludeColsWFlag`` 混入提供了一个每类的 ``__mapper_args__`` 钩子，
    将扫描包含传递给 :paramref:`.Column.info` 参数的键/值 ``'exclude': True`` 的 :class:`.Column` 对象，然后将它们的字符串“key”名称添加到 :paramref:`_orm.Mapper.exclude_properties` 集合中，从而防止生成的 :class:`.Mapper` 将这些列考虑在任何SQL操作中。

    .. seealso::

        :ref:`orm_mixins_toplevel`

.. tab:: 英文

    The ``__mapper_args__`` dictionary may be generated from a class-bound
    descriptor method rather than from a fixed dictionary by making use of the
    :func:`_orm.declared_attr` construct.    This is useful to create arguments
    for mappers that are programmatically derived from the table configuration
    or other aspects of the mapped class.    A dynamic ``__mapper_args__``
    attribute will typically be useful when using a Declarative Mixin or
    abstract base class.

    For example, to omit from the mapping
    any columns that have a special :attr:`.Column.info` value, a mixin
    can use a ``__mapper_args__`` method that scans for these columns from the
    ``cls.__table__`` attribute and passes them to the :paramref:`_orm.Mapper.exclude_properties`
    collection::

        from sqlalchemy import Column
        from sqlalchemy import Integer
        from sqlalchemy import select
        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr


        class ExcludeColsWFlag:
            @declared_attr
            def __mapper_args__(cls):
                return {
                    "exclude_properties": [
                        column.key
                        for column in cls.__table__.c
                        if column.info.get("exclude", False)
                    ]
                }


        class Base(DeclarativeBase):
            pass


        class SomeClass(ExcludeColsWFlag, Base):
            __tablename__ = "some_table"

            id = mapped_column(Integer, primary_key=True)
            data = mapped_column(String)
            not_needed = mapped_column(String, info={"exclude": True})

    Above, the ``ExcludeColsWFlag`` mixin provides a per-class ``__mapper_args__``
    hook that will scan for :class:`.Column` objects that include the key/value
    ``'exclude': True`` passed to the :paramref:`.Column.info` parameter, and then
    add their string "key" name to the :paramref:`_orm.Mapper.exclude_properties`
    collection which will prevent the resulting :class:`.Mapper` from considering
    these columns for any SQL operations.

    .. seealso::

        :ref:`orm_mixins_toplevel`


其他声明式映射指令
--------------------------------------

Other Declarative Mapping Directives

``__declare_last__()``
~~~~~~~~~~~~~~~~~~~~~~

.. tab:: 中文

    ``__declare_last__()`` 钩子允许定义一个类级别的函数，该函数由 :meth:`.MapperEvents.after_configured` 事件自动调用，该事件在映射假定完成并且“配置(configure)”步骤完成后发生::

        class MyClass(Base):
            @classmethod
            def __declare_last__(cls):
                """ """
                # do something with mappings

.. tab:: 英文

    The ``__declare_last__()`` hook allows definition of
    a class level function that is automatically called by the
    :meth:`.MapperEvents.after_configured` event, which occurs after mappings are
    assumed to be completed and the 'configure' step has finished::

        class MyClass(Base):
            @classmethod
            def __declare_last__(cls):
                """ """
                # do something with mappings

``__declare_first__()``
~~~~~~~~~~~~~~~~~~~~~~~

.. tab:: 中文

    与 ``__declare_last__()`` 类似，但在映射器配置开始时通过 :meth:`.MapperEvents.before_configured` 事件调用::

        class MyClass(Base):
            @classmethod
            def __declare_first__(cls):
                """ """
                # do something before mappings are configured

.. tab:: 英文

    Like ``__declare_last__()``, but is called at the beginning of mapper
    configuration via the :meth:`.MapperEvents.before_configured` event::

        class MyClass(Base):
            @classmethod
            def __declare_first__(cls):
                """ """
                # do something before mappings are configured

.. _declarative_metadata:

``metadata``
~~~~~~~~~~~~

.. tab:: 中文

    :class:`_schema.MetaData` 集合通常用于分配新的 :class:`_schema.Table`，它是与使用中的 :class:`_orm.registry` 对象关联的 :attr:`_orm.registry.metadata` 属性。当使用声明式基类（例如由 :class:`_orm.DeclarativeBase` 超类生成的基类）以及遗留函数（例如 :func:`_orm.declarative_base` 和 :meth:`_orm.registry.generate_base`）时，此 :class:`_schema.MetaData` 通常也是直接在基类上的名为 ``.metadata`` 的属性，因此也通过继承在映射类上。声明式使用此属性（如果存在）来确定目标 :class:`_schema.MetaData` 集合，如果不存在，则使用直接与 :class:`_orm.registry` 关联的 :class:`_schema.MetaData`。

    此属性还可以在每个映射层次结构基础上分配，以影响单个基类和/或 :class:`_orm.registry` 上使用的 :class:`_schema.MetaData` 集合。这无论是使用声明式基类还是直接使用 :meth:`_orm.registry.mapped` 装饰器都有效，从而允许模式，如下一节中的每个抽象基类的元数据示例，:ref:`declarative_abstract` 。可以使用 :meth:`_orm.registry.mapped` 来展示类似的模式，如下所示::

        reg = registry()


        class BaseOne:
            metadata = MetaData()


        class BaseTwo:
            metadata = MetaData()


        @reg.mapped
        class ClassOne:
            __tablename__ = "t1"  # 将使用 reg.metadata

            id = mapped_column(Integer, primary_key=True)


        @reg.mapped
        class ClassTwo(BaseOne):
            __tablename__ = "t1"  # 将使用 BaseOne.metadata

            id = mapped_column(Integer, primary_key=True)


        @reg.mapped
        class ClassThree(BaseTwo):
            __tablename__ = "t1"  # 将使用 BaseTwo.metadata

            id = mapped_column(Integer, primary_key=True)

    .. seealso::

        :ref:`declarative_abstract`

.. tab:: 英文

    The :class:`_schema.MetaData` collection normally used to assign a new
    :class:`_schema.Table` is the :attr:`_orm.registry.metadata` attribute
    associated with the :class:`_orm.registry` object in use. When using a
    declarative base class such as that produced by the
    :class:`_orm.DeclarativeBase` superclass, as well as legacy functions such as
    :func:`_orm.declarative_base` and :meth:`_orm.registry.generate_base`, this
    :class:`_schema.MetaData` is also normally present as an attribute named
    ``.metadata`` that's directly on the base class, and thus also on the mapped
    class via inheritance. Declarative uses this attribute, when present, in order
    to determine the target :class:`_schema.MetaData` collection, or if not
    present, uses the :class:`_schema.MetaData` associated directly with the
    :class:`_orm.registry`.

    This attribute may also be assigned towards in order to affect the
    :class:`_schema.MetaData` collection to be used on a per-mapped-hierarchy basis
    for a single base and/or :class:`_orm.registry`. This takes effect whether a
    declarative base class is used or if the :meth:`_orm.registry.mapped` decorator
    is used directly, thus allowing patterns such as the metadata-per-abstract base
    example in the next section, :ref:`declarative_abstract`. A similar pattern can
    be illustrated using :meth:`_orm.registry.mapped` as follows::

        reg = registry()


        class BaseOne:
            metadata = MetaData()


        class BaseTwo:
            metadata = MetaData()


        @reg.mapped
        class ClassOne:
            __tablename__ = "t1"  # will use reg.metadata

            id = mapped_column(Integer, primary_key=True)


        @reg.mapped
        class ClassTwo(BaseOne):
            __tablename__ = "t1"  # will use BaseOne.metadata

            id = mapped_column(Integer, primary_key=True)


        @reg.mapped
        class ClassThree(BaseTwo):
            __tablename__ = "t1"  # will use BaseTwo.metadata

            id = mapped_column(Integer, primary_key=True)

    .. seealso::

        :ref:`declarative_abstract`

.. _declarative_abstract:

``__abstract__``
~~~~~~~~~~~~~~~~

.. tab:: 中文

    ``__abstract__`` 使声明式完全跳过为类生成表或映射器的过程。可以在层次结构中以与混入相同的方式添加类（见 :ref:`declarative_mixins`），允许子类仅从特殊类扩展::

        class SomeAbstractBase(Base):
            __abstract__ = True

            def some_helpful_method(self):
                """ """

            @declared_attr
            def __mapper_args__(cls):
                return {"helpful mapper arguments": True}


        class MyMappedClass(SomeAbstractBase):
            pass

    ``__abstract__`` 的一种可能用途是为不同的基类使用不同的 :class:`_schema.MetaData`::

        class Base(DeclarativeBase):
            pass


        class DefaultBase(Base):
            __abstract__ = True
            metadata = MetaData()


        class OtherBase(Base):
            __abstract__ = True
            metadata = MetaData()

    如上所示，继承自 ``DefaultBase`` 的类将使用一个 :class:`_schema.MetaData` 作为表的注册表，而继承自 ``OtherBase`` 的类将使用另一个。然后，这些表本身可以在不同的数据库中创建::

        DefaultBase.metadata.create_all(some_engine)
        OtherBase.metadata.create_all(some_other_engine)

    .. seealso::

        :ref:`orm_inheritance_abstract_poly` - 适用于继承层次结构的“抽象(abstract)”映射类的替代形式。

.. tab:: 英文

    ``__abstract__`` causes declarative to skip the production
    of a table or mapper for the class entirely.  A class can be added within a
    hierarchy in the same way as mixin (see :ref:`declarative_mixins`), allowing
    subclasses to extend just from the special class::

        class SomeAbstractBase(Base):
            __abstract__ = True

            def some_helpful_method(self):
                """ """

            @declared_attr
            def __mapper_args__(cls):
                return {"helpful mapper arguments": True}


        class MyMappedClass(SomeAbstractBase):
            pass

    One possible use of ``__abstract__`` is to use a distinct
    :class:`_schema.MetaData` for different bases::

        class Base(DeclarativeBase):
            pass


        class DefaultBase(Base):
            __abstract__ = True
            metadata = MetaData()


        class OtherBase(Base):
            __abstract__ = True
            metadata = MetaData()

    Above, classes which inherit from ``DefaultBase`` will use one
    :class:`_schema.MetaData` as the registry of tables, and those which inherit from
    ``OtherBase`` will use a different one. The tables themselves can then be
    created perhaps within distinct databases::

        DefaultBase.metadata.create_all(some_engine)
        OtherBase.metadata.create_all(some_other_engine)

    .. seealso::

        :ref:`orm_inheritance_abstract_poly` - an alternative form of "abstract"
        mapped class that is appropriate for inheritance hierarchies.

.. _declarative_table_cls:

``__table_cls__``
~~~~~~~~~~~~~~~~~

.. tab:: 中文

    允许用于生成 :class:`_schema.Table` 的可调用对象/类进行自定义。
    这是一个非常开放的钩子，可以允许对这里生成的 :class:`_schema.Table` 进行特殊定制::

        class MyMixin:
            @classmethod
            def __table_cls__(cls, name, metadata_obj, *arg, **kw):
                return Table(f"my_{name}", metadata_obj, *arg, **kw)

    上述混入将导致所有生成的 :class:`_schema.Table` 对象包含前缀 ``"my_"`` ，后跟使用 ``__tablename__`` 属性通常指定的名称。

    ``__table_cls__`` 还支持返回 ``None`` 的情况，这导致类被视为单表继承与其子类。这在某些定制方案中可能有用，以基于表本身的参数确定应进行单表继承，例如，如果没有主键存在，则定义为单继承::

        class AutoTable:
            @declared_attr
            def __tablename__(cls):
                return cls.__name__

            @classmethod
            def __table_cls__(cls, *arg, **kw):
                for obj in arg[1:]:
                    if (isinstance(obj, Column) and obj.primary_key) or isinstance(
                        obj, PrimaryKeyConstraint
                    ):
                        return Table(*arg, **kw)

                return None


        class Person(AutoTable, Base):
            id = mapped_column(Integer, primary_key=True)


        class Employee(Person):
            employee_name = mapped_column(String)

    上述 ``Employee`` 类将被映射为针对 ``Person`` 的单表继承； ``employee_name`` 列将作为 ``Person`` 表的成员添加。

.. tab:: 英文

    Allows the callable / class used to generate a :class:`_schema.Table` to be customized.
    This is a very open-ended hook that can allow special customizations
    to a :class:`_schema.Table` that one generates here::

        class MyMixin:
            @classmethod
            def __table_cls__(cls, name, metadata_obj, *arg, **kw):
                return Table(f"my_{name}", metadata_obj, *arg, **kw)

    The above mixin would cause all :class:`_schema.Table` objects generated to include
    the prefix ``"my_"``, followed by the name normally specified using the
    ``__tablename__`` attribute.

    ``__table_cls__`` also supports the case of returning ``None``, which
    causes the class to be considered as single-table inheritance vs. its subclass.
    This may be useful in some customization schemes to determine that single-table
    inheritance should take place based on the arguments for the table itself,
    such as, define as single-inheritance if there is no primary key present::

        class AutoTable:
            @declared_attr
            def __tablename__(cls):
                return cls.__name__

            @classmethod
            def __table_cls__(cls, *arg, **kw):
                for obj in arg[1:]:
                    if (isinstance(obj, Column) and obj.primary_key) or isinstance(
                        obj, PrimaryKeyConstraint
                    ):
                        return Table(*arg, **kw)

                return None


        class Person(AutoTable, Base):
            id = mapped_column(Integer, primary_key=True)


        class Employee(Person):
            employee_name = mapped_column(String)

    The above ``Employee`` class would be mapped as single-table inheritance
    against ``Person``; the ``employee_name`` column would be added as a member
    of the ``Person`` table.

