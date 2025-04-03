.. _orm_mapping_classes_toplevel:

==========================
ORM 映射类概述
==========================

ORM Mapped Class Overview

.. tab:: 中文

    ORM类映射配置概述。

    对于SQLAlchemy ORM和/或Python新手来说，建议浏览
    :ref:`orm_quickstart`，最好是通读
    :ref:`unified_tutorial`，其中在 :ref:`tutorial_orm_table_metadata` 首次介绍了ORM配置。

.. tab:: 英文

    Overview of ORM class mapping configuration.

    For readers new to the SQLAlchemy ORM and/or new to Python in general,
    it's recommended to browse through the
    :ref:`orm_quickstart` and preferably to work through the
    :ref:`unified_tutorial`, where ORM configuration is first introduced at
    :ref:`tutorial_orm_table_metadata`.

.. _orm_mapping_styles:

ORM 映射风格
==================

ORM Mapping Styles

.. tab:: 中文

    SQLAlchemy具有两种截然不同的映射配置风格，这些风格又进一步细分为不同的设置选项。映射风格的多样性是为了适应各种开发者的偏好，包括用户定义类与其映射到关系模式表和列的抽象程度、使用的类层次结构类型（包括是否存在自定义元类方案），以及是否存在其他类仪器化方法，例如是否同时使用Python数据类。

    在现代SQLAlchemy中，这些风格之间的差异主要是表面的；当使用特定的SQLAlchemy配置风格来表示映射类的意图时，映射类的内部过程在每种情况下大致相同，其最终结果总是一个用户定义的类，该类具有一个配置为可选择单元的 :class:`_orm.Mapper`，通常由 :class:`_schema.Table` 对象表示，类本身已被 :term:`仪器化` (instrumented) 以包括与关系操作相关的行为，无论是在类的级别还是在该类的实例上。由于过程在所有情况下基本相同，因此从不同风格映射的类始终可以完全互操作。协议 :class:`_orm.MappedClassProtocol` 可用于在使用类型检查器（如mypy）时指示映射类。

    最初的映射API通常被称为“经典”风格，而更自动化的映射风格称为“声明式”风格。SQLAlchemy现在将这两种映射风格称为 **命令式映射(imperative mapping)** 和 **声明式映射(declarative mapping)** 。

    无论使用何种映射风格，自SQLAlchemy 1.4起，所有ORM映射都源自一个名为 :class:`_orm.registry` 的单一对象，这是一个映射类的注册表。使用此注册表，可以作为一个组来最终确定一组映射器配置，并且特定注册表中的类可以在配置过程中按名称相互引用。

    .. versionchanged:: 1.4  
      
        声明式映射和经典映射现在被称为“声明式(declarative)”和“命令式(imperative)”映射，并在内部统一，所有映射都源自表示相关映射集合的 :class:`_orm.registry` 构造。

.. tab:: 英文

    SQLAlchemy features two distinct styles of mapper configuration, which then
    feature further sub-options for how they are set up.   The variability in mapper
    styles is present to suit a varied list of developer preferences, including
    the degree of abstraction of a user-defined class from how it is to be
    mapped to relational schema tables and columns, what kinds of class hierarchies
    are in use, including whether or not custom metaclass schemes are present,
    and finally if there are other class-instrumentation approaches present such
    as if Python dataclasses_ are in use simultaneously.

    In modern SQLAlchemy, the difference between these styles is mostly
    superficial; when a particular SQLAlchemy configurational style is used to
    express the intent to map a class, the internal process of mapping the class
    proceeds in mostly the same way for each, where the end result is always a
    user-defined class that has a :class:`_orm.Mapper` configured against a
    selectable unit, typically represented by a :class:`_schema.Table` object, and
    the class itself has been :term:`instrumented` to include behaviors linked to
    relational operations both at the level of the class as well as on instances of
    that class. As the process is basically the same in all cases, classes mapped
    from different styles are always fully interoperable with each other.
    The protocol :class:`_orm.MappedClassProtocol` can be used to indicate a mapped
    class when using type checkers such as mypy.

    The original mapping API is commonly referred to as "classical" style,
    whereas the more automated style of mapping is known as "declarative" style.
    SQLAlchemy now refers to these two mapping styles as **imperative mapping**
    and **declarative mapping**.

    Regardless of what style of mapping used, all ORM mappings as of SQLAlchemy 1.4
    originate from a single object known as :class:`_orm.registry`, which is a
    registry of mapped classes. Using this registry, a set of mapper configurations
    can be finalized as a group, and classes within a particular registry may refer
    to each other by name within the configurational process.

    .. versionchanged:: 1.4  
      
        Declarative and classical mapping are now referred
        to as "declarative" and "imperative" mapping, and are unified internally,
        all originating from the :class:`_orm.registry` construct that represents
        a collection of related mappings.

.. _orm_declarative_mapping:

声明式映射
-------------------

Declarative Mapping

.. tab:: 中文

    **声明式映射** 是现代SQLAlchemy中构建映射的典型方式。最常见的模式是首先使用 :class:`_orm.DeclarativeBase` 超类构造一个基类。当子类化时，生成的基类将对派生自它的所有子类应用声明式映射过程，默认情况下，相对于特定的 :class:`_orm.registry` 是本地的。下面的示例说明了使用声明式基类然后在声明式表映射中的使用::

        from sqlalchemy import Integer, String, ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        # 声明基类
        class Base(DeclarativeBase):
            pass


        # 使用基类的示例映射
        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str] = mapped_column(String(30))
            nickname: Mapped[Optional[str]]

    在上面，使用 :class:`_orm.DeclarativeBase` 类生成一个新的基类（在SQLAlchemy的文档中通常称为 ``Base`` ，但可以具有任何所需的名称），新映射类可以继承该基类，如上所示，构造了一个新的映射类 ``User`` 。

    .. versionchanged:: 2.0

       :class:`_orm.DeclarativeBase` 超类取代了 :func:`_orm.declarative_base` 函数和 :meth:`_orm.registry.generate_base` 方法的使用；超类方法无需插件即可与 :pep:`484` 工具集成。
       参见 :ref:`whatsnew_20_orm_declarative_typing` 了解迁移说明。

    基类指的是一个 :class:`_orm.registry` 对象，该对象维护一组相关的映射类集合，以及一个保留类映射到的 :class:`_schema.Table` 对象集合的 :class:`_schema.MetaData` 对象。

    主要的声明式映射风格在以下部分中有进一步详细介绍：

    * :ref:`orm_declarative_generated_base_class` - 使用基类的声明式映射。

    * :ref:`orm_declarative_decorator` - 使用装饰器而不是基类的声明式映射。

    在声明式映射类的范围内，也有两种声明 :class:`_schema.Table` 元数据的方式。这些包括：

    * :ref:`orm_declarative_table` - 使用 :func:`_orm.mapped_column` 指令在映射类中内联声明表列（或在遗留形式中，直接使用 :class:`_schema.Column` 对象）。 :func:`_orm.mapped_column` 指令还可以选择性地与使用 :class:`_orm.Mapped` 类的类型注释结合使用，以直接提供有关映射列的一些详细信息。列指令与 ``__tablename__`` 和可选的 ``__table_args__`` 类级别指令结合使用，将允许声明式映射过程构建一个要映射的 :class:`_schema.Table` 对象。

    * :ref:`orm_imperative_table_configuration` - 不单独指定表名和属性，而是将一个显式构造的 :class:`_schema.Table` 对象与一个其他方面声明式映射的类关联。这种映射风格是“声明式”和“命令式”映射的混合体，适用于将类映射到 :term:`反射的` :class:`_schema.Table` 对象以及将类映射到现有Core构造（如连接和子查询）的技术。

    声明式映射的文档在 :ref:`declarative_config_toplevel` 继续。

.. tab:: 英文

    The **Declarative Mapping** is the typical way that mappings are constructed in
    modern SQLAlchemy. The most common pattern is to first construct a base class
    using the :class:`_orm.DeclarativeBase` superclass. The resulting base class,
    when subclassed will apply the declarative mapping process to all subclasses
    that derive from it, relative to a particular :class:`_orm.registry` that
    is local to the new base by default. The example below illustrates
    the use of a declarative base which is then used in a declarative table mapping::

        from sqlalchemy import Integer, String, ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        # declarative base class
        class Base(DeclarativeBase):
            pass


        # an example mapping using the base
        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str] = mapped_column(String(30))
            nickname: Mapped[Optional[str]]

    Above, the :class:`_orm.DeclarativeBase` class is used to generate a new
    base class (within SQLAlchemy's documentation it's typically referred to
    as ``Base``, however can have any desired name) from
    which new classes to be mapped may inherit from, as above a new mapped
    class ``User`` is constructed.

    .. versionchanged:: 2.0 The :class:`_orm.DeclarativeBase` superclass supersedes
      the use of the :func:`_orm.declarative_base` function and
      :meth:`_orm.registry.generate_base` methods; the superclass approach
      integrates with :pep:`484` tools without the use of plugins.
      See :ref:`whatsnew_20_orm_declarative_typing` for migration notes.

    The base class refers to a :class:`_orm.registry` object that maintains a
    collection of related mapped classes. as well as to a :class:`_schema.MetaData`
    object that retains a collection of :class:`_schema.Table` objects to which
    the classes are mapped.

    The major Declarative mapping styles are further detailed in the following
    sections:

    * :ref:`orm_declarative_generated_base_class` - declarative mapping using a
      base class.

    * :ref:`orm_declarative_decorator` - declarative mapping using a decorator,
      rather than a base class.

    Within the scope of a Declarative mapped class, there are also two varieties
    of how the :class:`_schema.Table` metadata may be declared.  These include:

    * :ref:`orm_declarative_table` - table columns are declared inline
      within the mapped class using the :func:`_orm.mapped_column` directive
      (or in legacy form, using the :class:`_schema.Column` object directly).
      The :func:`_orm.mapped_column` directive may also be optionally combined with
      type annotations using the :class:`_orm.Mapped` class which can provide
      some details about the mapped columns directly.  The column
      directives, in combination with the ``__tablename__`` and optional
      ``__table_args__`` class level directives will allow the
      Declarative mapping process to construct a :class:`_schema.Table` object to
      be mapped.

    * :ref:`orm_imperative_table_configuration` - Instead of specifying table name
      and attributes separately, an explicitly constructed :class:`_schema.Table` object
      is associated with a class that is otherwise mapped declaratively.  This
      style of mapping is a hybrid of "declarative" and "imperative" mapping,
      and applies to techniques such as mapping classes to :term:`reflected`
      :class:`_schema.Table` objects, as well as mapping classes to existing
      Core constructs such as joins and subqueries.


    Documentation for Declarative mapping continues at :ref:`declarative_config_toplevel`.

.. _classical_mapping:
.. _orm_imperative_mapping:

命令式映射
-------------------

Imperative Mapping

.. tab:: 中文

  **命令式** 或 **经典** 映射指的是使用 :meth:`_orm.registry.map_imperatively` 方法配置映射类，其中目标类不包含任何声明式类属性。

  .. tip:: 
    
      命令式映射形式是一种较少使用的映射形式，起源于2006年SQLAlchemy的最早版本。它本质上是一种绕过声明系统的方法，提供了一种更“简陋”的映射系统，并且不提供现代功能，如 :pep:`484` 支持。因此，大多数文档示例使用声明式形式，建议新用户从 :ref:`Declarative Table <orm_declarative_table_config_toplevel>` 配置开始。

  .. versionchanged:: 2.0
    
      现在使用 :meth:`_orm.registry.map_imperatively` 方法创建经典映射。独立函数 ``sqlalchemy.orm.mapper()`` 已有效移除。

  在“经典”形式中，表元数据是使用 :class:`_schema.Table` 构造单独创建的，然后通过 :meth:`_orm.registry.map_imperatively` 方法与 ``User`` 类关联，在建立 :class:`_orm.registry` 实例后。通常，共享的 :class:`_orm.registry` 实例用于所有相关的映射类::

      from sqlalchemy import Table, Column, Integer, String, ForeignKey
      from sqlalchemy.orm import registry

      mapper_registry = registry()

      user_table = Table(
          "user",
          mapper_registry.metadata,
          Column("id", Integer, primary_key=True),
          Column("name", String(50)),
          Column("fullname", String(50)),
          Column("nickname", String(12)),
      )


      class User:
          pass


      mapper_registry.map_imperatively(User, user_table)

  有关映射属性的信息，例如与其他类的关系，通过 ``properties`` 字典提供。下面的示例说明了第二个 :class:`_schema.Table` 对象，映射到一个名为 ``Address`` 的类，然后通过 :func:`_orm.relationship` 链接到 ``User`` ::

      address = Table(
          "address",
          metadata_obj,
          Column("id", Integer, primary_key=True),
          Column("user_id", Integer, ForeignKey("user.id")),
          Column("email_address", String(50)),
      )

      mapper_registry.map_imperatively(
          User,
          user,
          properties={
              "addresses": relationship(Address, backref="user", order_by=address.c.id)
          },
      )

      mapper_registry.map_imperatively(Address, address)

  注意，使用命令式方法映射的类与声明式方法映射的类是 **完全可互换(fully interchangeable)** 的。两种系统最终创建相同的配置，包括一个 :class:`_schema.Table`，用户定义的类，与 :class:`_orm.Mapper` 对象链接在一起。当我们谈论 :class:`_orm.Mapper` 的行为时，这也包括使用声明式系统时——它仍然在使用，只是在幕后进行。

.. tab:: 英文

    An **imperative** or **classical** mapping refers to the configuration of a
    mapped class using the :meth:`_orm.registry.map_imperatively` method,
    where the target class does not include any declarative class attributes.

    .. tip:: 
      
       The imperative mapping form is a lesser-used form of mapping that
       originates from the very first releases of SQLAlchemy in 2006.  It's
       essentially a means of bypassing the Declarative system to provide a
       more "barebones" system of mapping, and does not offer modern features
       such as :pep:`484` support.  As such, most documentation examples
       use Declarative forms, and it's recommended that new users start
       with :ref:`Declarative Table <orm_declarative_table_config_toplevel>`
       configuration.

    .. versionchanged:: 2.0  
      
       The :meth:`_orm.registry.map_imperatively` method
       is now used to create classical mappings.  The ``sqlalchemy.orm.mapper()``
       standalone function is effectively removed.

    In "classical" form, the table metadata is created separately with the
    :class:`_schema.Table` construct, then associated with the ``User`` class via
    the :meth:`_orm.registry.map_imperatively` method, after establishing
    a :class:`_orm.registry` instance.  Normally, a single instance of
    :class:`_orm.registry`
    shared for all mapped classes that are related to each other::

        from sqlalchemy import Table, Column, Integer, String, ForeignKey
        from sqlalchemy.orm import registry

        mapper_registry = registry()

        user_table = Table(
            "user",
            mapper_registry.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("fullname", String(50)),
            Column("nickname", String(12)),
        )


        class User:
            pass


        mapper_registry.map_imperatively(User, user_table)

    Information about mapped attributes, such as relationships to other classes, are provided
    via the ``properties`` dictionary.  The example below illustrates a second :class:`_schema.Table`
    object, mapped to a class called ``Address``, then linked to ``User`` via :func:`_orm.relationship`::

        address = Table(
            "address",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.id")),
            Column("email_address", String(50)),
        )

        mapper_registry.map_imperatively(
            User,
            user,
            properties={
                "addresses": relationship(Address, backref="user", order_by=address.c.id)
            },
        )

        mapper_registry.map_imperatively(Address, address)

    Note that classes which are mapped with the Imperative approach are **fully
    interchangeable** with those mapped with the Declarative approach. Both systems
    ultimately create the same configuration, consisting of a
    :class:`_schema.Table`, user-defined class, linked together with a
    :class:`_orm.Mapper` object. When we talk about "the behavior of
    :class:`_orm.Mapper`", this includes when using the Declarative system as well
    - it's still used, just behind the scenes.


.. _orm_mapper_configuration_overview:

映射类基本组件
==================================

Mapped Class Essential Components

.. tab:: 中文

    在所有映射形式中，通过传递构造参数可以以多种方式配置类的映射，这些参数最终成为 :class:`_orm.Mapper` 对象的一部分，通过其构造函数传递。传递给 :class:`_orm.Mapper` 的参数源自给定的映射形式，包括传递给命令式映射的 :meth:`_orm.registry.map_imperatively` 的参数，或者在使用声明式系统时，来自表列、SQL表达式和映射关系以及诸如 :ref:`__mapper_args__ <orm_declarative_mapper_options>` 之类的属性的组合。

    :class:`_orm.Mapper` 类寻找四类通用的配置信息：

.. tab:: 英文

    With all mapping forms, the mapping of the class can be configured in many ways
    by passing construction arguments that ultimately become part of the :class:`_orm.Mapper`
    object via its constructor.  The parameters that are delivered to
    :class:`_orm.Mapper` originate from the given mapping form, including
    parameters passed to :meth:`_orm.registry.map_imperatively` for an Imperative
    mapping, or when using the Declarative system, from a combination
    of the table columns, SQL expressions and
    relationships being mapped along with that of attributes such as
    :ref:`__mapper_args__ <orm_declarative_mapper_options>`.

    There are four general classes of configuration information that the
    :class:`_orm.Mapper` class looks for:

要映射的类
----------------------

The class to be mapped

.. tab:: 中文

    这是我们在应用程序中构建的一个类。
    通常对该类的结构没有限制。 [1]_
    当一个Python类被映射时，该类只能有 **一个** :class:`_orm.Mapper` 对象。 [2]_

    使用 :ref:`声明式 <orm_declarative_mapping>` 映射风格进行映射时，要映射的类要么是声明基类的子类，要么由装饰器或函数（如 :meth:`_orm.registry.mapped` ）处理。

    使用 :ref:`命令式 <orm_imperative_mapping>` 风格进行映射时，该类直接作为 :paramref:`_orm.registry.map_imperatively.class_` 参数传递。

.. tab:: 英文

    This is a class that we construct in our application.
    There are generally no restrictions on the structure of this class. [3]_
    When a Python class is mapped, there can only be **one** :class:`_orm.Mapper`
    object for the class. [4]_

    When mapping with the :ref:`declarative <orm_declarative_mapping>` mapping
    style, the class to be mapped is either a subclass of the declarative base class,
    or is handled by a decorator or function such as :meth:`_orm.registry.mapped`.

    When mapping with the :ref:`imperative <orm_imperative_mapping>` style, the
    class is passed directly as the
    :paramref:`_orm.registry.map_imperatively.class_` argument.

表或其他 from 子句对象
--------------------------------------

The table, or other from clause object

.. tab:: 中文

    在绝大多数常见情况下，这是 :class:`_schema.Table` 的一个实例。对于更高级的用例，它也可以引用任何类型的 :class:`_sql.FromClause` 对象，最常见的替代对象是 :class:`_sql.Subquery` 和 :class:`_sql.Join` 对象。

    使用 :ref:`声明式 <orm_declarative_mapping>` 映射风格进行映射时，目标表要么由声明系统基于 ``__tablename__`` 属性和呈现的 :class:`_schema.Column` 对象生成，要么通过 ``__table__`` 属性建立。这两种配置风格在 :ref:`orm_declarative_table` 和 :ref:`orm_imperative_table_configuration` 中介绍。

    使用 :ref:`命令式 <orm_imperative_mapping>` 风格进行映射时，目标表作为 :paramref:`_orm.registry.map_imperatively.local_table` 参数按位置传递。

    与映射类的“每个类一个映射器”要求相反，作为映射对象的 :class:`_schema.Table` 或其他 :class:`_sql.FromClause` 对象可以与任意数量的映射关联。:class:`_orm.Mapper` 直接对用户定义的类进行修改，但不会以任何方式修改给定的 :class:`_schema.Table` 或其他 :class:`_sql.FromClause`。

.. tab:: 英文

    In the vast majority of common cases this is an instance of
    :class:`_schema.Table`.  For more advanced use cases, it may also refer
    to any kind of :class:`_sql.FromClause` object, the most common
    alternative objects being the :class:`_sql.Subquery` and :class:`_sql.Join`
    object.

    When mapping with the :ref:`declarative <orm_declarative_mapping>` mapping
    style, the subject table is either generated by the declarative system based
    on the ``__tablename__`` attribute and the :class:`_schema.Column` objects
    presented, or it is established via the ``__table__`` attribute.  These
    two styles of configuration are presented at
    :ref:`orm_declarative_table` and :ref:`orm_imperative_table_configuration`.

    When mapping with the :ref:`imperative <orm_imperative_mapping>` style, the
    subject table is passed positionally as the
    :paramref:`_orm.registry.map_imperatively.local_table` argument.

    In contrast to the "one mapper per class" requirement of a mapped class,
    the :class:`_schema.Table` or other :class:`_sql.FromClause` object that
    is the subject of the mapping may be associated with any number of mappings.
    The :class:`_orm.Mapper` applies modifications directly to the user-defined
    class, but does not modify the given :class:`_schema.Table` or other
    :class:`_sql.FromClause` in any way.

.. _orm_mapping_properties:

属性字典
-------------------------

The properties dictionary

.. tab:: 中文

    这是将与映射类关联的所有属性的字典。默认情况下，:class:`_orm.Mapper` 生成从给定 :class:`_schema.Table` 派生的字典条目，以 :class:`_orm.ColumnProperty` 对象的形式，每个对象引用映射表的单个 :class:`_schema.Column`。属性字典还将包含所有其他类型的 :class:`_orm.MapperProperty` 对象，最常见的是由 :func:`_orm.relationship` 构造生成的实例。

    使用 :ref:`声明式 <orm_declarative_mapping>` 映射风格进行映射时，属性字典由声明系统通过扫描要映射的类以查找适当的属性生成。有关此过程的说明，请参见 :ref:`orm_declarative_properties` 部分。

    使用 :ref:`命令式 <orm_imperative_mapping>` 风格进行映射时，属性字典直接作为 ``properties`` 参数传递给 :meth:`_orm.registry.map_imperatively`，后者将其传递给 :paramref:`_orm.Mapper.properties` 参数。

.. tab:: 英文

    This is a dictionary of all of the attributes
    that will be associated with the mapped class.    By default, the
    :class:`_orm.Mapper` generates entries for this dictionary derived from the
    given :class:`_schema.Table`, in the form of :class:`_orm.ColumnProperty`
    objects which each refer to an individual :class:`_schema.Column` of the
    mapped table.  The properties dictionary will also contain all the other
    kinds of :class:`_orm.MapperProperty` objects to be configured, most
    commonly instances generated by the :func:`_orm.relationship` construct.

    When mapping with the :ref:`declarative <orm_declarative_mapping>` mapping
    style, the properties dictionary is generated by the declarative system
    by scanning the class to be mapped for appropriate attributes.  See
    the section :ref:`orm_declarative_properties` for notes on this process.

    When mapping with the :ref:`imperative <orm_imperative_mapping>` style, the
    properties dictionary is passed directly as the
    ``properties`` parameter
    to :meth:`_orm.registry.map_imperatively`, which will pass it along to the
    :paramref:`_orm.Mapper.properties` parameter.

其他映射器配置参数
-------------------------------------

Other mapper configuration parameters

.. tab:: 中文

    使用 :ref:`声明式 <orm_declarative_mapping>` 映射风格进行映射时，通过 ``__mapper_args__`` 类属性配置其他映射器配置参数。使用示例可参见 :ref:`orm_declarative_mapper_options`。

    使用 :ref:`命令式 <orm_imperative_mapping>` 风格进行映射时，关键字参数传递给 :meth:`_orm.registry.map_imperatively` 方法，该方法将它们传递给 :class:`_orm.Mapper` 类。

    接受的全部参数范围记录在 :class:`_orm.Mapper` 中。

.. tab:: 英文

    When mapping with the :ref:`declarative <orm_declarative_mapping>` mapping
    style, additional mapper configuration arguments are configured via the
    ``__mapper_args__`` class attribute.   Examples of use are available
    at :ref:`orm_declarative_mapper_options`.

    When mapping with the :ref:`imperative <orm_imperative_mapping>` style,
    keyword arguments are passed to the to :meth:`_orm.registry.map_imperatively`
    method which passes them along to the :class:`_orm.Mapper` class.

    The full range of parameters accepted are documented at  :class:`_orm.Mapper`.


.. _orm_mapped_class_behavior:


映射类行为
=====================

Mapped Class Behavior

.. tab:: 中文

    在使用 :class:`_orm.registry` 对象的所有映射样式中，以下行为很常见：

.. tab:: 英文

    Across all styles of mapping using the :class:`_orm.registry` object, the following behaviors are common:

.. _mapped_class_default_constructor:

默认构造函数
-------------------

Default Constructor

.. tab:: 中文

    :class:`_orm.registry` 对所有没有显式 ``__init__`` 方法的映射类应用一个默认构造函数，即 ``__init__`` 方法。此方法的行为是提供一个方便的关键字构造函数，接受所有命名属性作为可选关键字参数。例如::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str]

    上面的 ``User`` 类型对象将具有一个构造函数，允许创建 ``User`` 对象，如::

        u1 = User(name="some name", fullname="some fullname")

    .. tip::

        :ref:`orm_declarative_native_dataclasses` 功能通过使用Python数据类提供了一种生成默认 ``__init__()`` 方法的替代方法，并允许高度可配置的构造函数形式。

    .. warning::

        类的 ``__init__()`` 方法仅在对象在Python代码中构造时调用， **而不是在从数据库加载或刷新对象时调用** 。有关如何在加载对象时调用特殊逻辑的入门知识，请参见下一节 :ref:`mapped_class_load_events`。

    包含显式 ``__init__()`` 方法的类将保留该方法，并且不会应用默认构造函数。

    要更改使用的默认构造函数，可以将用户定义的Python可调用对象提供给 :paramref:`_orm.registry.constructor` 参数，该参数将用作默认构造函数。

    构造函数还适用于命令式映射::

        from sqlalchemy.orm import registry

        mapper_registry = registry()

        user_table = Table(
            "user",
            mapper_registry.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )


        class User:
            pass


        mapper_registry.map_imperatively(User, user_table)

    如 :ref:`orm_imperative_mapping` 中所述，以上类以命令式映射，将具有与 :class:`_orm.registry` 关联的默认构造函数。

    .. versionadded:: 1.4  
      
      经典映射现在支持标准配置级构造函数，当它们通过 :meth:`_orm.registry.map_imperatively` 方法映射时。

.. tab:: 英文

    The :class:`_orm.registry` applies a default constructor, i.e. ``__init__``
    method, to all mapped classes that don't explicitly have their own
    ``__init__`` method.   The behavior of this method is such that it provides
    a convenient keyword constructor that will accept as optional keyword arguments
    all the attributes that are named.   E.g.::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str]

    An object of type ``User`` above will have a constructor which allows
    ``User`` objects to be created as::

        u1 = User(name="some name", fullname="some fullname")

    .. tip::

        The :ref:`orm_declarative_native_dataclasses` feature provides an alternate
        means of generating a default ``__init__()`` method by using
        Python dataclasses, and allows for a highly configurable constructor
        form.

    .. warning::

        The ``__init__()`` method of the class is called only when the object is
        constructed in Python code, and **not when an object is loaded or refreshed
        from the database**.  See the next section :ref:`mapped_class_load_events`
        for a primer on how to invoke special logic when objects are loaded.

    A class that includes an explicit ``__init__()`` method will maintain
    that method, and no default constructor will be applied.

    To change the default constructor used, a user-defined Python callable may be
    provided to the :paramref:`_orm.registry.constructor` parameter which will be
    used as the default constructor.

    The constructor also applies to imperative mappings::

        from sqlalchemy.orm import registry

        mapper_registry = registry()

        user_table = Table(
            "user",
            mapper_registry.metadata,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )


        class User:
            pass


        mapper_registry.map_imperatively(User, user_table)

    The above class, mapped imperatively as described at :ref:`orm_imperative_mapping`,
    will also feature the default constructor associated with the :class:`_orm.registry`.

    .. versionadded:: 1.4  
      
        classical mappings now support a standard configuration-level
        constructor when they are mapped via the :meth:`_orm.registry.map_imperatively`
        method.

.. _mapped_class_load_events:

在加载过程中维护非映射状态
------------------------------------------

Maintaining Non-Mapped State Across Loads

.. tab:: 中文

    当映射类的``__init__()``方法在Python代码中直接构造对象时调用::

        u1 = User(name="some name", fullname="some fullname")

    但是，当使用ORM :class:`_orm.Session`加载对象时， ``__init__()`` 方法 **不会** 被调用::

        u1 = session.scalars(select(User).where(User.name == "some name")).first()

    这是因为从数据库加载时，用于构造对象的操作（在上述示例中为 ``User`` ）更类似于 **反序列化** ，例如解包，而不是初始构造。对象的大多数重要状态不是第一次组装，而是从数据库行重新加载。

    因此，为了在对象内维护不属于存储到数据库的数据的状态，使得在加载和构造对象时都存在这种状态，下面详细介绍了两种通用方法。

    1. 使用Python描述符如 ``@property`` ，而不是状态，按需动态计算属性。

       对于简单属性，这是最简单且最不易出错的方法。例如，如果对象 ``Point`` 具有 ``Point.x`` 和 ``Point.y`` ，并希望具有这些属性的和的属性::

          class Point(Base):
              __tablename__ = "point"
              id: Mapped[int] = mapped_column(primary_key=True)
              x: Mapped[int]
              y: Mapped[int]

              @property
              def x_plus_y(self):
                  return self.x + self.y

       使用动态描述符的优点是每次都计算值，这意味着它保持正确的值，因为基础属性（在这种情况下为 ``x`` 和 ``y`` ）可能会更改。

       以上模式的其他形式包括Python标准库
       `cached_property <https://docs.python.org/3/library/functools.html#functools.cached_property>`_
       装饰器（它是缓存的，并且每次都不重新计算），以及SQLAlchemy的 :class:`.hybrid_property` 装饰器，允许可以用于SQL查询的属性。

    2. 使用 :meth:`.InstanceEvents.load` 建立加载状态，并可选地使用补充方法 :meth:`.InstanceEvents.refresh` 和 :meth:`.InstanceEvents.refresh_flush`。

      这些是每当从数据库加载对象或在过期后刷新对象时调用的事件钩子。通常只需要 :meth:`.InstanceEvents.load`，因为非映射的本地对象状态不受过期操作的影响。修改上述 ``Point`` 示例如下::

          from sqlalchemy import event


          class Point(Base):
              __tablename__ = "point"
              id: Mapped[int] = mapped_column(primary_key=True)
              x: Mapped[int]
              y: Mapped[int]

              def __init__(self, x, y, **kw):
                  super().__init__(x=x, y=y, **kw)
                  self.x_plus_y = x + y


          @event.listens_for(Point, "load")
          def receive_load(target, context):
              target.x_plus_y = target.x + target.y

      如果还使用刷新事件，可以根据需要将事件钩子堆叠在一个可调用对象之上，如::

          @event.listens_for(Point, "load")
          @event.listens_for(Point, "refresh")
          @event.listens_for(Point, "refresh_flush")
          def receive_load(target, context, attrs=None):
              target.x_plus_y = target.x + target.y

      上面， ``attrs`` 属性将出现在 ``refresh`` 和 ``refresh_flush`` 事件中，并指示正在刷新的属性名称列表。

.. tab:: 英文

    The ``__init__()`` method of the mapped class is invoked when the object
    is constructed directly in Python code::

        u1 = User(name="some name", fullname="some fullname")

    However, when an object is loaded using the ORM :class:`_orm.Session`,
    the ``__init__()`` method is **not** called::

        u1 = session.scalars(select(User).where(User.name == "some name")).first()

    The reason for this is that when loaded from the database, the operation
    used to construct the object, in the above example the ``User``, is more
    analogous to **deserialization**, such as unpickling, rather than initial
    construction.  The majority of the object's important state is not being
    assembled for the first time, it's being re-loaded from database rows.

    Therefore to maintain state within the object that is not part of the data
    that's stored to the database, such that this state is present when objects
    are loaded as well as constructed, there are two general approaches detailed
    below.

    1. Use Python descriptors like ``@property``, rather than state, to dynamically
       compute attributes as needed.
    
       For simple attributes, this is the simplest approach and the least error prone.
       For example if an object ``Point`` with ``Point.x`` and ``Point.y`` wanted
       an attribute with the sum of these attributes::
    
          class Point(Base):
              __tablename__ = "point"
              id: Mapped[int] = mapped_column(primary_key=True)
              x: Mapped[int]
              y: Mapped[int]
    
              @property
              def x_plus_y(self):
                  return self.x + self.y
    
       An advantage of using dynamic descriptors is that the value is computed
       every time, meaning it maintains the correct value as the underlying
       attributes (``x`` and ``y`` in this case) might change.
    
       Other forms of the above pattern include Python standard library
       `cached_property <https://docs.python.org/3/library/functools.html#functools.cached_property>`_
       decorator (which is cached, and not re-computed each time), as well as SQLAlchemy's :class:`.hybrid_property` decorator which
       allows for attributes that can work for SQL querying as well.


    2. Establish state on-load using :meth:`.InstanceEvents.load`, and optionally
       supplemental methods :meth:`.InstanceEvents.refresh` and :meth:`.InstanceEvents.refresh_flush`.
    
       These are event hooks that are invoked whenever the object is loaded
       from the database, or when it is refreshed after being expired.   Typically
       only the :meth:`.InstanceEvents.load` is needed, since non-mapped local object
       state is not affected by expiration operations.   To revise the ``Point``
       example above looks like::
    
          from sqlalchemy import event
    
    
          class Point(Base):
              __tablename__ = "point"
              id: Mapped[int] = mapped_column(primary_key=True)
              x: Mapped[int]
              y: Mapped[int]
    
              def __init__(self, x, y, **kw):
                  super().__init__(x=x, y=y, **kw)
                  self.x_plus_y = x + y
    
    
          @event.listens_for(Point, "load")
          def receive_load(target, context):
              target.x_plus_y = target.x + target.y
    
       If using the refresh events as well, the event hooks can be stacked on
       top of one callable if needed, as::
    
          @event.listens_for(Point, "load")
          @event.listens_for(Point, "refresh")
          @event.listens_for(Point, "refresh_flush")
          def receive_load(target, context, attrs=None):
              target.x_plus_y = target.x + target.y
    
       Above, the ``attrs`` attribute will be present for the ``refresh`` and
       ``refresh_flush`` events and indicate a list of attribute names that are
       being refreshed.

.. _orm_mapper_inspection:

映射类、实例和映射器的运行时自检
---------------------------------------------------------------

Runtime Introspection of Mapped classes, Instances and Mappers

.. tab:: 中文

    使用 :class:`_orm.registry` 映射的类还将具有一些所有映射常见的属性：

    * ``__mapper__`` 属性将引用与类关联的 :class:`_orm.Mapper`::

        mapper = User.__mapper__

      此 :class:`_orm.Mapper` 也是使用 :func:`_sa.inspect` 函数针对映射类时返回的内容::

        from sqlalchemy import inspect

        mapper = inspect(User)

      ..

    * ``__table__`` 属性将引用与类映射的 :class:`_schema.Table` ，或更一般地引用 :class:`.FromClause` 对象
        
        ::

        table = User.__table__

      此 :class:`.FromClause` 也是使用 :attr:`_orm.Mapper.local_table` 属性时返回的内容::

        table = inspect(User).local_table

      对于单表继承映射，其中类是没有自己表的子类，:attr:`_orm.Mapper.local_table` 属性以及 ``.__table__`` 属性将为 ``None`` 。要检索在查询此类时实际选择的“可选择对象”，可以通过 :attr:`_orm.Mapper.selectable` 属性获得::

        table = inspect(User).selectable

.. tab:: 英文

    A class that is mapped using :class:`_orm.registry` will also feature a few
    attributes that are common to all mappings:
    
    * The ``__mapper__`` attribute will refer to the :class:`_orm.Mapper` that
      is associated with the class::
    
        mapper = User.__mapper__
    
      This :class:`_orm.Mapper` is also what's returned when using the
      :func:`_sa.inspect` function against the mapped class::
    
        from sqlalchemy import inspect
    
        mapper = inspect(User)
    
      ..
    
    * The ``__table__`` attribute will refer to the :class:`_schema.Table`, or
      more generically to the :class:`.FromClause` object, to which the
      class is mapped::
    
        table = User.__table__
    
      This :class:`.FromClause` is also what's returned when using the
      :attr:`_orm.Mapper.local_table` attribute of the :class:`_orm.Mapper`::
    
        table = inspect(User).local_table
    
      For a single-table inheritance mapping, where the class is a subclass that
      does not have a table of its own, the :attr:`_orm.Mapper.local_table` attribute as well
      as the ``.__table__`` attribute will be ``None``.   To retrieve the
      "selectable" that is actually selected from during a query for this class,
      this is available via the :attr:`_orm.Mapper.selectable` attribute::
    
        table = inspect(User).selectable

  ..

.. _orm_mapper_inspection_mapper:

映射器对象的检查
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inspection of Mapper objects

.. tab:: 中文

    如前一节所述，可以使用 :ref:`core_inspection_toplevel` 系统从任何映射类（无论方法如何）获取 :class:`_orm.Mapper` 对象。使用 :func:`_sa.inspect` 函数，可以从映射类中获取 :class:`_orm.Mapper`::

        >>> from sqlalchemy import inspect
        >>> insp = inspect(User)

    提供了详细信息，包括 :attr:`_orm.Mapper.columns`::

        >>> insp.columns
        <sqlalchemy.util._collections.OrderedProperties object at 0x102f407f8>

    这是一个可以以列表格式查看或通过单个名称查看的命名空间::

        >>> list(insp.columns)
        [Column('id', Integer(), table=<user>, primary_key=True, nullable=False), Column('name', String(length=50), table=<user>), Column('fullname', String(length=50), table=<user>), Column('nickname', String(length=50), table=<user>)]
        >>> insp.columns.name
        Column('name', String(length=50), table=<user>)

    其他命名空间包括 :attr:`_orm.Mapper.all_orm_descriptors`，其中包括所有映射属性以及混合属性、关联代理::

        >>> insp.all_orm_descriptors
        <sqlalchemy.util._collections.ImmutableProperties object at 0x1040e2c68>
        >>> insp.all_orm_descriptors.keys()
        ['fullname', 'nickname', 'name', 'id']

    以及 :attr:`_orm.Mapper.column_attrs`::

        >>> list(insp.column_attrs)
        [<ColumnProperty at 0x10403fde0; id>, <ColumnProperty at 0x10403fce8; name>, <ColumnProperty at 0x1040e9050; fullname>, <ColumnProperty at 0x1040e9148; nickname>]
        >>> insp.column_attrs.name
        <ColumnProperty at 0x10403fce8; name>
        >>> insp.column_attrs.name.expression
        Column('name', String(length=50), table=<user>)

    .. seealso::

        :class:`.Mapper`

.. tab:: 英文

    As illustrated in the previous section, the :class:`_orm.Mapper` object is
    available from any mapped class, regardless of method, using the
    :ref:`core_inspection_toplevel` system.  Using the
    :func:`_sa.inspect` function, one can acquire the :class:`_orm.Mapper` from a
    mapped class::
    
        >>> from sqlalchemy import inspect
        >>> insp = inspect(User)
    
    Detailed information is available including :attr:`_orm.Mapper.columns`::
    
        >>> insp.columns
        <sqlalchemy.util._collections.OrderedProperties object at 0x102f407f8>
    
    This is a namespace that can be viewed in a list format or
    via individual names::
    
        >>> list(insp.columns)
        [Column('id', Integer(), table=<user>, primary_key=True, nullable=False), Column('name', String(length=50), table=<user>), Column('fullname', String(length=50), table=<user>), Column('nickname', String(length=50), table=<user>)]
        >>> insp.columns.name
        Column('name', String(length=50), table=<user>)
    
    Other namespaces include :attr:`_orm.Mapper.all_orm_descriptors`, which includes all mapped
    attributes as well as hybrids, association proxies::
    
        >>> insp.all_orm_descriptors
        <sqlalchemy.util._collections.ImmutableProperties object at 0x1040e2c68>
        >>> insp.all_orm_descriptors.keys()
        ['fullname', 'nickname', 'name', 'id']
    
    As well as :attr:`_orm.Mapper.column_attrs`::
    
        >>> list(insp.column_attrs)
        [<ColumnProperty at 0x10403fde0; id>, <ColumnProperty at 0x10403fce8; name>, <ColumnProperty at 0x1040e9050; fullname>, <ColumnProperty at 0x1040e9148; nickname>]
        >>> insp.column_attrs.name
        <ColumnProperty at 0x10403fce8; name>
        >>> insp.column_attrs.name.expression
        Column('name', String(length=50), table=<user>)
    
    .. seealso::
    
        :class:`.Mapper`

.. _orm_mapper_inspection_instancestate:

映射实例的检查
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inspection of Mapped Instances

.. tab:: 中文

    :func:`_sa.inspect` 函数还提供了有关映射类实例的信息。当应用于映射类的实例而不是类本身时，返回的对象称为 :class:`.InstanceState`，它不仅提供类使用的 :class:`.Mapper` 的链接，还提供详细的接口，提供有关实例中各个属性状态的信息，包括它们的当前值以及与其数据库加载值的关系。

    给定从数据库加载的 ``User`` 类的一个实例::

      >>> u1 = session.scalars(select(User)).first()

    :func:`_sa.inspect` 函数将返回一个 :class:`.InstanceState` 对象::

      >>> insp = inspect(u1)
      >>> insp
      <sqlalchemy.orm.state.InstanceState object at 0x7f07e5fec2e0>

    通过这个对象，我们可以看到如 :class:`.Mapper` 之类的元素::

      >>> insp.mapper
      <Mapper at 0x7f07e614ef50; User>

    对象所 :term:`attached` 的 :class:`_orm.Session`，如果有的话::

      >>> insp.session
      <sqlalchemy.orm.session.Session object at 0x7f07e614f160>

    有关对象当前 :ref:`persistence state <session_object_states>` 的信息::

      >>> insp.persistent
      True
      >>> insp.pending
      False

    属性状态信息，如尚未加载或 :term:`lazy loaded` 的属性（假设 ``addresses`` 指的是映射类上与相关类的 :func:`_orm.relationship`）::

      >>> insp.unloaded
      {'addresses'}

    有关属性当前在Python中的状态的信息，例如自上次刷新以来未修改的属性::

      >>> insp.unmodified
      {'nickname', 'name', 'fullname', 'id'}

    以及自上次刷新以来对属性的修改的具体历史::

      >>> insp.attrs.nickname.value
      'nickname'
      >>> u1.nickname = "new nickname"
      >>> insp.attrs.nickname.history
      History(added=['new nickname'], unchanged=(), deleted=['nickname'])

    .. seealso::

        :class:`.InstanceState`

        :attr:`.InstanceState.attrs`

        :class:`.AttributeState`

.. tab:: 英文

    The :func:`_sa.inspect` function also provides information about instances
    of a mapped class.  When applied to an instance of a mapped class, rather
    than the class itself, the object returned is known as :class:`.InstanceState`,
    which will provide links to not only the :class:`.Mapper` in use by the
    class, but also a detailed interface that provides information on the state
    of individual attributes within the instance including their current value
    and how this relates to what their database-loaded value is.
    
    Given an instance of the ``User`` class loaded from the database::
    
      >>> u1 = session.scalars(select(User)).first()
    
    The :func:`_sa.inspect` function will return to us an :class:`.InstanceState`
    object::
    
      >>> insp = inspect(u1)
      >>> insp
      <sqlalchemy.orm.state.InstanceState object at 0x7f07e5fec2e0>
    
    With this object we can see elements such as the :class:`.Mapper`::
    
      >>> insp.mapper
      <Mapper at 0x7f07e614ef50; User>
    
    The :class:`_orm.Session` to which the object is :term:`attached`, if any::
    
      >>> insp.session
      <sqlalchemy.orm.session.Session object at 0x7f07e614f160>
    
    Information about the current :ref:`persistence state <session_object_states>`
    for the object::
    
      >>> insp.persistent
      True
      >>> insp.pending
      False
    
    Attribute state information such as attributes that have not been loaded or
    :term:`lazy loaded` (assume ``addresses`` refers to a :func:`_orm.relationship`
    on the mapped class to a related class)::
    
      >>> insp.unloaded
      {'addresses'}
    
    Information regarding the current in-Python status of attributes, such as
    attributes that have not been modified since the last flush::
    
      >>> insp.unmodified
      {'nickname', 'name', 'fullname', 'id'}
    
    as well as specific history on modifications to attributes since the last flush::
    
      >>> insp.attrs.nickname.value
      'nickname'
      >>> u1.nickname = "new nickname"
      >>> insp.attrs.nickname.history
      History(added=['new nickname'], unchanged=(), deleted=['nickname'])
    
    .. seealso::
    
        :class:`.InstanceState`
    
        :attr:`.InstanceState.attrs`
    
        :class:`.AttributeState`


.. _dataclasses: https://docs.python.org/3/library/dataclasses.html

.. [1] 在Python 2下运行时，Python 2的“旧风格”类是唯一不兼容的类。在Python 2上运行代码时，所有类都必须从Python ``object`` 类继承。在Python 3下，这种情况始终如此。

.. [2] 有一个遗留功能称为“非主映射器”，其中可以将其他 :class:`_orm.Mapper` 对象与已经映射的类相关联，但它们不会对类应用仪器。此功能自SQLAlchemy 1.3起已弃用。

.. [3] When running under Python 2, a Python 2 "old style" class is the only
       kind of class that isn't compatible.    When running code on Python 2,
       all classes must extend from the Python ``object`` class.  Under
       Python 3 this is always the case.

.. [4] There is a legacy feature known as a "non primary mapper", where
       additional :class:`_orm.Mapper` objects may be associated with a class
       that's already mapped, however they don't apply instrumentation
       to the class.  This feature is deprecated as of SQLAlchemy 1.3.

