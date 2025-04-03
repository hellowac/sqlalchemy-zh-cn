.. _orm_mixins_toplevel:

使用 Mixins 组合映射层次结构
========================================

Composing Mapped Hierarchies with Mixins

.. tab:: 中文

    在使用 :ref:`Declarative <orm_declarative_mapping>` 风格映射类时，一个常见的需求是共享通用功能，例如特定列、表或映射器选项、命名方案或其他映射属性，跨多个类。使用声明式映射时，这种习惯用法通过使用 :term:`mixin classes` 以及通过增强声明式基类本身来支持。

    .. tip:: 
        
        除了混入类，共同的列选项还可以通过使用 :pep:`593` ``Annotated`` 类型在多个类之间共享；有关这些SQLAlchemy 2.0功能的背景，请参阅 :ref:`orm_declarative_mapped_column_type_map_pep593` 和 :ref:`orm_declarative_mapped_column_pep593`。

    下面是一些常见混入习惯用法的示例::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class CommonMixin:
            """定义一系列可以通过将这个类作为混入类应用于映射类的常用元素。"""

            @declared_attr.directive
            def __tablename__(cls) -> str:
                return cls.__name__.lower()

            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}

            id: Mapped[int] = mapped_column(primary_key=True)


        class HasLogRecord:
            """标记与 ``LogRecord`` 类有多对一关系的类。"""

            log_record_id: Mapped[int] = mapped_column(ForeignKey("logrecord.id"))

            @declared_attr
            def log_record(self) -> Mapped["LogRecord"]:
                return relationship("LogRecord")


        class LogRecord(CommonMixin, Base):
            log_info: Mapped[str]


        class MyModel(CommonMixin, HasLogRecord, Base):
            name: Mapped[str]

    上面的示例说明了一个类 ``MyModel`` ，它在其基类中包含了两个混入 ``CommonMixin`` 和 ``HasLogRecord`` ，以及一个补充类 ``LogRecord`` ，该类也包含了 ``CommonMixin`` ，展示了在混入和基类上支持的各种构造，包括：

    * 使用 :func:`_orm.mapped_column`、:class:`_orm.Mapped` 或 :class:`_schema.Column` 声明的列从混入或基类复制到目标类进行映射；上面通过列属性 ``CommonMixin.id`` 和 ``HasLogRecord.log_record_id`` 说明了这一点。
    * 声明式指令如 ``__table_args__`` 和 ``__mapper_args__`` 可以分配给混入或基类，它们将自动对继承混入或基类的任何类生效。上面的示例通过 ``__table_args__`` 和 ``__mapper_args__`` 属性说明了这一点。
    * 所有声明式指令，包括所有 ``__tablename__`` 、 ``__table__`` 、 ``__table_args__`` 和 ``__mapper_args__`` ，可以使用用户定义的类方法实现，这些方法使用 :class:`_orm.declared_attr` 装饰器（特别是 :attr:`_orm.declared_attr.directive` 子成员，稍后会详细介绍）。上面，通过生成一个动态生成 :class:`.Table` 名称的 ``def __tablename__(cls)`` 类方法来说明这一点；当应用于 ``MyModel`` 类时，表名将生成为 ``"mymodel"`` ，当应用于 ``LogRecord`` 类时，表名将生成为 ``"logrecord"`` 。
    * 其他ORM属性如 :func:`_orm.relationship` 可以使用同样用 :class:`_orm.declared_attr` 装饰的用户定义类方法在目标类上生成进行映射。上面，通过生成一个多对一 :func:`_orm.relationship` 到一个名为 ``LogRecord`` 的映射对象来说明这一点。

    上面的功能可以通过一个 :func:`_sql.select` 示例进行演示：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(MyModel).join(MyModel.log_record))
        {printsql}SELECT mymodel.name, mymodel.id, mymodel.log_record_id
        FROM mymodel JOIN logrecord ON logrecord.id = mymodel.log_record_id

    .. tip:: 
        
        :class:`_orm.declared_attr` 的示例将尝试说明每个方法示例的正确 :pep:`484` 注解。使用带有 :class:`_orm.declared_attr` 函数的注解是 **完全可选的** ，声明式不会使用这些注解；然而，这些注解对于通过Mypy ``--strict`` 类型检查是必要的。

    另外，上面说明的 :attr:`_orm.declared_attr.directive` 子成员也是可选的，只对 :pep:`484` 类型工具有意义，因为它在创建覆盖声明指令如 ``__tablename__`` 、 ``__mapper_args__`` 和 ``__table_args__`` 的方法时调整预期的返回类型。

    .. versionadded:: 2.0  
        
        作为SQLAlchemy ORM的 :pep:`484` 类型支持的一部分，向 :class:`_orm.declared_attr` 添加了 :attr:`_orm.declared_attr.directive` 以区分 :class:`_orm.Mapped` 属性和声明式配置属性

    对于混入和基类的顺序没有固定的约定。正常的Python方法解析规则适用，上面的示例也同样适用于::

        class MyModel(Base, HasLogRecord, CommonMixin):
            name: Mapped[str] = mapped_column()

    这是因为 ``Base`` 在这里没有定义 ``CommonMixin`` 或 ``HasLogRecord`` 定义的任何变量，即 ``__tablename__``、 ``__table_args__``、 ``id`` 等。如果 ``Base`` 确实定义了相同名称的属性，则放在继承列表中第一个的类将确定在新定义的类上使用哪个属性。

    .. tip:: 
        
        虽然上面的示例使用基于 :class:`_orm.Mapped` 注解类的 :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 形式，混入类也可以完美地与非注解和遗留的声明式形式一起工作，例如直接使用 :class:`_schema.Column` 而不是 :func:`_orm.mapped_column`。

    .. versionchanged:: 2.0 
        
        对于使用SQLAlchemy 1.4系列的用户，他们可能使用了 ``mypy plugin``，不再需要使用 :func:`_orm.declarative_mixin` 类装饰器来标记声明式混入，假设不再使用mypy插件。

.. tab:: 英文

    A common need when mapping classes using the :ref:`Declarative
    <orm_declarative_mapping>` style is to share common functionality, such as
    particular columns, table or mapper options, naming schemes, or other mapped
    properties, across many classes.  When using declarative mappings, this idiom
    is supported via the use of :term:`mixin classes`, as well as via augmenting the declarative base
    class itself.
    
    .. tip::  In addition to mixin classes, common column options may also be
       shared among many classes using :pep:`593` ``Annotated`` types; see
       :ref:`orm_declarative_mapped_column_type_map_pep593` and
       :ref:`orm_declarative_mapped_column_pep593` for background on these
       SQLAlchemy 2.0 features.
    
    An example of some commonly mixed-in idioms is below::
    
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class CommonMixin:
            """define a series of common elements that may be applied to mapped
            classes using this class as a mixin class."""
    
            @declared_attr.directive
            def __tablename__(cls) -> str:
                return cls.__name__.lower()
    
            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}
    
            id: Mapped[int] = mapped_column(primary_key=True)
    
    
        class HasLogRecord:
            """mark classes that have a many-to-one relationship to the
            ``LogRecord`` class."""
    
            log_record_id: Mapped[int] = mapped_column(ForeignKey("logrecord.id"))
    
            @declared_attr
            def log_record(self) -> Mapped["LogRecord"]:
                return relationship("LogRecord")
    
    
        class LogRecord(CommonMixin, Base):
            log_info: Mapped[str]
    
    
        class MyModel(CommonMixin, HasLogRecord, Base):
            name: Mapped[str]
    
    The above example illustrates a class ``MyModel`` which includes two mixins
    ``CommonMixin`` and ``HasLogRecord`` in its bases, as well as a supplementary
    class ``LogRecord`` which also includes ``CommonMixin``, demonstrating a
    variety of constructs that are supported on mixins and base classes, including:
    
    * columns declared using :func:`_orm.mapped_column`, :class:`_orm.Mapped`
      or :class:`_schema.Column` are copied from mixins or base classes onto
      the target class to be mapped; above this is illustrated via the
      column attributes ``CommonMixin.id`` and ``HasLogRecord.log_record_id``.
    * Declarative directives such as ``__table_args__`` and ``__mapper_args__``
      can be assigned to a mixin or base class, where they will take effect
      automatically for any classes which inherit from the mixin or base.
      The above example illustrates this using
      the ``__table_args__`` and ``__mapper_args__`` attributes.
    * All Declarative directives, including all of ``__tablename__``, ``__table__``,
      ``__table_args__`` and ``__mapper_args__``,  may be implemented using
      user-defined class methods, which are decorated with the
      :class:`_orm.declared_attr` decorator (specifically the
      :attr:`_orm.declared_attr.directive` sub-member, more on that in a moment).
      Above, this is illustrated using a ``def __tablename__(cls)`` classmethod that
      generates a :class:`.Table` name dynamically; when applied to the
      ``MyModel`` class, the table name will be generated as ``"mymodel"``, and
      when applied to the ``LogRecord`` class, the table name will be generated
      as ``"logrecord"``.
    * Other ORM properties such as :func:`_orm.relationship` can be generated
      on the target class to be mapped using user-defined class methods also
      decorated with the :class:`_orm.declared_attr` decorator.  Above, this is
      illustrated by generating a many-to-one :func:`_orm.relationship` to a mapped
      object called ``LogRecord``.
    
    The features above may all be demonstrated using a :func:`_sql.select`
    example:
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import select
        >>> print(select(MyModel).join(MyModel.log_record))
        {printsql}SELECT mymodel.name, mymodel.id, mymodel.log_record_id
        FROM mymodel JOIN logrecord ON logrecord.id = mymodel.log_record_id
    
    .. tip:: The examples of :class:`_orm.declared_attr` will attempt to illustrate
       the correct :pep:`484` annotations for each method example.  The use of annotations with
       :class:`_orm.declared_attr` functions are **completely optional**, and
       are not
       consumed by Declarative; however, these annotations are required in order
       to pass Mypy ``--strict`` type checking.
    
       Additionally, the :attr:`_orm.declared_attr.directive` sub-member
       illustrated above is optional as well, and is only significant for
       :pep:`484` typing tools, as it adjusts for the expected return type when
       creating methods to override Declarative directives such as
       ``__tablename__``, ``__mapper_args__`` and ``__table_args__``.
    
       .. versionadded:: 2.0  As part of :pep:`484` typing support for the
          SQLAlchemy ORM, added the :attr:`_orm.declared_attr.directive` to
          :class:`_orm.declared_attr` to distinguish between :class:`_orm.Mapped`
          attributes and Declarative configurational attributes
    
    There's no fixed convention for the order of mixins and base classes.
    Normal Python method resolution rules apply, and
    the above example would work just as well with::
    
        class MyModel(Base, HasLogRecord, CommonMixin):
            name: Mapped[str] = mapped_column()
    
    This works because ``Base`` here doesn't define any of the variables that
    ``CommonMixin`` or ``HasLogRecord`` defines, i.e. ``__tablename__``,
    ``__table_args__``, ``id``, etc. If the ``Base`` did define an attribute of the
    same name, the class placed first in the inherits list would determine which
    attribute is used on the newly defined class.
    
    .. tip::  While the above example is using
       :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` form
       based on the :class:`_orm.Mapped` annotation class, mixin classes also work
       perfectly well with non-annotated and legacy Declarative forms, such as when
       using :class:`_schema.Column` directly instead of
       :func:`_orm.mapped_column`.
    
    .. versionchanged:: 2.0 For users coming from the 1.4 series of SQLAlchemy
       who may have been using the ``mypy plugin``, the
       :func:`_orm.declarative_mixin` class decorator is no longer needed
       to mark declarative mixins, assuming the mypy plugin is no longer in use.


增强Base基类
~~~~~~~~~~~~~~~~~~~

Augmenting the Base

.. tab:: 中文

    除了使用纯混入外，本节中的大多数技术还可以直接应用于基类，以便将模式应用于从特定基类派生的所有类。下面的示例说明了上一节的一些示例，关于 ``Base`` 类::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            """定义一系列可以通过将这个类作为基类应用于映射类的常用元素。"""

            @declared_attr.directive
            def __tablename__(cls) -> str:
                return cls.__name__.lower()

            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}

            id: Mapped[int] = mapped_column(primary_key=True)


        class HasLogRecord:
            """标记与 ``LogRecord`` 类有多对一关系的类。"""

            log_record_id: Mapped[int] = mapped_column(ForeignKey("logrecord.id"))

            @declared_attr
            def log_record(self) -> Mapped["LogRecord"]:
                return relationship("LogRecord")


        class LogRecord(Base):
            log_info: Mapped[str]


        class MyModel(HasLogRecord, Base):
            name: Mapped[str]

    上面， ``MyModel`` 和 ``LogRecord`` 在继承 ``Base`` 时，将会从类名派生其表名，一个名为 ``id`` 的主键列，以及由 ``Base.__table_args__`` 和 ``Base.__mapper_args__`` 定义的表和映射器参数。

    使用遗留 :func:`_orm.declarative_base` 或 :meth:`_orm.registry.generate_base` 时，可以如下使用 :paramref:`_orm.declarative_base.cls` 参数来生成等效效果，如下面的非注解示例所示::

        # 遗留 declarative_base() 的使用

        from sqlalchemy import Integer, String
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import declarative_base
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base:
            """定义一系列可以通过将这个类作为基类应用于映射类的常用元素。"""

            @declared_attr.directive
            def __tablename__(cls):
                return cls.__name__.lower()

            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}

            id = mapped_column(Integer, primary_key=True)


        Base = declarative_base(cls=Base)


        class HasLogRecord:
            """标记与``LogRecord``类有多对一关系的类。"""

            log_record_id = mapped_column(ForeignKey("logrecord.id"))

            @declared_attr
            def log_record(self):
                return relationship("LogRecord")


        class LogRecord(Base):
            log_info = mapped_column(String)


        class MyModel(HasLogRecord, Base):
            name = mapped_column(String)

.. tab:: 英文

    In addition to using a pure mixin, most of the techniques in this
    section can also be applied to the base class directly, for patterns that
    should apply to all classes derived from a particular base.  The example
    below illustrates some of the previous section's example in terms of the
    ``Base`` class::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            """define a series of common elements that may be applied to mapped
            classes using this class as a base class."""

            @declared_attr.directive
            def __tablename__(cls) -> str:
                return cls.__name__.lower()

            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}

            id: Mapped[int] = mapped_column(primary_key=True)


        class HasLogRecord:
            """mark classes that have a many-to-one relationship to the
            ``LogRecord`` class."""

            log_record_id: Mapped[int] = mapped_column(ForeignKey("logrecord.id"))

            @declared_attr
            def log_record(self) -> Mapped["LogRecord"]:
                return relationship("LogRecord")


        class LogRecord(Base):
            log_info: Mapped[str]


        class MyModel(HasLogRecord, Base):
            name: Mapped[str]

    Where above, ``MyModel`` as well as ``LogRecord``, in deriving from
    ``Base``, will both have their table name derived from their class name,
    a primary key column named ``id``, as well as the above table and mapper
    arguments defined by ``Base.__table_args__`` and ``Base.__mapper_args__``.

    When using legacy :func:`_orm.declarative_base` or :meth:`_orm.registry.generate_base`,
    the :paramref:`_orm.declarative_base.cls` parameter may be used as follows
    to generate an equivalent effect, as illustrated in the non-annotated
    example below::

        # legacy declarative_base() use

        from sqlalchemy import Integer, String
        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import declarative_base
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base:
            """define a series of common elements that may be applied to mapped
            classes using this class as a base class."""

            @declared_attr.directive
            def __tablename__(cls):
                return cls.__name__.lower()

            __table_args__ = {"mysql_engine": "InnoDB"}
            __mapper_args__ = {"eager_defaults": True}

            id = mapped_column(Integer, primary_key=True)


        Base = declarative_base(cls=Base)


        class HasLogRecord:
            """mark classes that have a many-to-one relationship to the
            ``LogRecord`` class."""

            log_record_id = mapped_column(ForeignKey("logrecord.id"))

            @declared_attr
            def log_record(self):
                return relationship("LogRecord")


        class LogRecord(Base):
            log_info = mapped_column(String)


        class MyModel(HasLogRecord, Base):
            name = mapped_column(String)

混合列
~~~~~~~~~~~~~~~~~

Mixing in Columns

.. tab:: 中文

    列可以在混入中表示，假设使用 :ref:`Declarative table <orm_declarative_table>` 风格的配置（而不是 :ref:`imperative table <orm_imperative_table_configuration>` 配置），这样在混入中声明的列可以被复制为声明过程生成的 :class:`_schema.Table` 的一部分。:func:`_orm.mapped_column` 、 :class:`_orm.Mapped` 和 :class:`_schema.Column` 三种构造都可以在声明式混入中内联声明::

        class TimestampMixin:
            created_at: Mapped[datetime] = mapped_column(default=func.now())
            updated_at: Mapped[datetime]


        class MyModel(TimestampMixin, Base):
            __tablename__ = "test"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    如上所示，所有在其类基中包含 ``TimestampMixin`` 的声明式类将自动包含一个 ``created_at`` 列，该列将时间戳应用于所有行插入，以及一个 ``updated_at`` 列，出于示例目的，该列没有默认值（如果有，我们将使用 :paramref:`_schema.Column.onupdate` 参数，该参数由 :func:`_orm.mapped_column` 接受）。这些列构造总是 **从原始混入或基类中复制(copied from the originating mixin or base class)**，这样相同的混入/基类可以应用于任意数量的目标类，每个目标类将有自己的列构造。

    所有声明式列形式都被混入支持，包括：

    * **注解属性(Annotated attributes)** - 是否存在 :func:`_orm.mapped_column`::

        class TimestampMixin:
            created_at: Mapped[datetime] = mapped_column(default=func.now())
            updated_at: Mapped[datetime]

    * **mapped_column** - 是否存在 :class:`_orm.Mapped`::

        class TimestampMixin:
            created_at = mapped_column(default=func.now())
            updated_at: Mapped[datetime] = mapped_column()

    * **Column** - 传统声明式形式::

        class TimestampMixin:
            created_at = Column(DateTime, default=func.now())
            updated_at = Column(DateTime)

    在上述每种形式中，声明式处理混入类上的基于列的属性，通过创建构造的 **副本** ，然后将其应用于目标类。

    .. versionchanged:: 2.0 
        
        声明式API现在可以适应 :class:`_schema.Column` 对象以及在使用混入时的任何形式的 :func:`_orm.mapped_column` 构造，而无需使用 :func:`_orm.declared_attr`。先前限制了带有 :class:`_schema.ForeignKey` 元素的列无法直接在混入中使用的限制已被移除。

.. tab:: 英文

    Columns can be indicated in mixins assuming the
    :ref:`Declarative table <orm_declarative_table>` style of configuration
    is in use (as opposed to
    :ref:`imperative table <orm_imperative_table_configuration>` configuration),
    so that columns declared on the mixin can then be copied to be
    part of the :class:`_schema.Table` that the Declarative process generates.
    All three of the :func:`_orm.mapped_column`, :class:`_orm.Mapped`,
    and :class:`_schema.Column` constructs may be declared inline in a
    declarative mixin::

        class TimestampMixin:
            created_at: Mapped[datetime] = mapped_column(default=func.now())
            updated_at: Mapped[datetime]


        class MyModel(TimestampMixin, Base):
            __tablename__ = "test"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    Where above, all declarative classes that include ``TimestampMixin``
    in their class bases will automatically include a column ``created_at``
    that applies a timestamp to all row insertions, as well as an ``updated_at``
    column, which does not include a default for the purposes of the example
    (if it did, we would use the :paramref:`_schema.Column.onupdate` parameter
    which is accepted by :func:`_orm.mapped_column`).  These column constructs
    are always **copied from the originating mixin or base class**, so that the
    same mixin/base class may be applied to any number of target classes
    which will each have their own column constructs.

    All Declarative column forms are supported by mixins, including:

    * **Annotated attributes**  - with or without :func:`_orm.mapped_column` present::

        class TimestampMixin:
            created_at: Mapped[datetime] = mapped_column(default=func.now())
            updated_at: Mapped[datetime]

    * **mapped_column** - with or without :class:`_orm.Mapped` present::

        class TimestampMixin:
            created_at = mapped_column(default=func.now())
            updated_at: Mapped[datetime] = mapped_column()

    * **Column** - legacy Declarative form::

        class TimestampMixin:
            created_at = Column(DateTime, default=func.now())
            updated_at = Column(DateTime)

    In each of the above forms, Declarative handles the column-based attributes
    on the mixin class by creating a **copy** of the construct, which is then
    applied to the target class.

    .. versionchanged:: 2.0 The declarative API can now accommodate
    :class:`_schema.Column` objects as well as :func:`_orm.mapped_column`
    constructs of any form when using mixins without the need to use
    :func:`_orm.declared_attr`.  Previous limitations which prevented columns
    with :class:`_schema.ForeignKey` elements from being used directly
    in mixins have been removed.


.. _orm_declarative_mixins_relationships:

混合关系
~~~~~~~~~~~~~~~~~~~~~~~

Mixing in Relationships

.. tab:: 中文

    由 :func:`~sqlalchemy.orm.relationship` 创建的关系仅使用 :class:`_orm.declared_attr` 方法提供给声明式混入类，消除了复制关系及其可能的列绑定内容时可能出现的任何歧义。下面的示例结合了一个外键列和关系，以便两个类 ``Foo`` 和 ``Bar`` 都可以配置为通过多对一引用一个公共目标类::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class RefTargetMixin:
            target_id: Mapped[int] = mapped_column(ForeignKey("target.id"))

            @declared_attr
            def target(cls) -> Mapped["Target"]:
                return relationship("Target")


        class Foo(RefTargetMixin, Base):
            __tablename__ = "foo"
            id: Mapped[int] = mapped_column(primary_key=True)


        class Bar(RefTargetMixin, Base):
            __tablename__ = "bar"
            id: Mapped[int] = mapped_column(primary_key=True)


        class Target(Base):
            __tablename__ = "target"
            id: Mapped[int] = mapped_column(primary_key=True)

    通过上述映射， ``Foo`` 和 ``Bar`` 中的每一个都包含一个访问 ``Target`` 的关系，通过 ``.target`` 属性访问：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Foo).join(Foo.target))
        {printsql}SELECT foo.id, foo.target_id
        FROM foo JOIN target ON target.id = foo.target_id{stop}
        >>> print(select(Bar).join(Bar.target))
        {printsql}SELECT bar.id, bar.target_id
        FROM bar JOIN target ON target.id = bar.target_id{stop}

    特殊参数如 :paramref:`_orm.relationship.primaryjoin` 也可以在混入的类方法中使用，这些类方法通常需要引用正在映射的类。对于需要引用本地映射列的方案，在普通情况下，这些列由声明式作为映射类上的属性提供，该类作为 ``cls`` 参数传递给装饰的类方法。使用此功能，我们可以例如使用明确的 primaryjoin 重写 ``RefTargetMixin.target`` 方法，该方法引用 ``Target`` 和 ``cls`` 上的待映射列::

        class Target(Base):
            __tablename__ = "target"
            id: Mapped[int] = mapped_column(primary_key=True)


        class RefTargetMixin:
            target_id: Mapped[int] = mapped_column(ForeignKey("target.id"))

            @declared_attr
            def target(cls) -> Mapped["Target"]:
                # 说明明确的 'primaryjoin' 参数
                return relationship("Target", primaryjoin=Target.id == cls.target_id)

.. tab:: 英文

    Relationships created by :func:`~sqlalchemy.orm.relationship` are provided
    with declarative mixin classes exclusively using the
    :class:`_orm.declared_attr` approach, eliminating any ambiguity
    which could arise when copying a relationship and its possibly column-bound
    contents. Below is an example which combines a foreign key column and a
    relationship so that two classes ``Foo`` and ``Bar`` can both be configured to
    reference a common target class via many-to-one::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class RefTargetMixin:
            target_id: Mapped[int] = mapped_column(ForeignKey("target.id"))

            @declared_attr
            def target(cls) -> Mapped["Target"]:
                return relationship("Target")


        class Foo(RefTargetMixin, Base):
            __tablename__ = "foo"
            id: Mapped[int] = mapped_column(primary_key=True)


        class Bar(RefTargetMixin, Base):
            __tablename__ = "bar"
            id: Mapped[int] = mapped_column(primary_key=True)


        class Target(Base):
            __tablename__ = "target"
            id: Mapped[int] = mapped_column(primary_key=True)

    With the above mapping, each of ``Foo`` and ``Bar`` contain a relationship
    to ``Target`` accessed along the ``.target`` attribute:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Foo).join(Foo.target))
        {printsql}SELECT foo.id, foo.target_id
        FROM foo JOIN target ON target.id = foo.target_id{stop}
        >>> print(select(Bar).join(Bar.target))
        {printsql}SELECT bar.id, bar.target_id
        FROM bar JOIN target ON target.id = bar.target_id{stop}

    Special arguments such as :paramref:`_orm.relationship.primaryjoin` may also
    be used within mixed-in classmethods, which often need to refer to the class
    that's being mapped.  For schemes that need to refer to locally mapped columns, in
    ordinary cases these columns are made available by Declarative as attributes
    on the mapped class which is passed as the ``cls`` argument to the
    decorated classmethod.  Using this feature, we could for
    example rewrite the ``RefTargetMixin.target`` method using an
    explicit primaryjoin which refers to pending mapped columns on both
    ``Target`` and ``cls``::

        class Target(Base):
            __tablename__ = "target"
            id: Mapped[int] = mapped_column(primary_key=True)


        class RefTargetMixin:
            target_id: Mapped[int] = mapped_column(ForeignKey("target.id"))

            @declared_attr
            def target(cls) -> Mapped["Target"]:
                # illustrates explicit 'primaryjoin' argument
                return relationship("Target", primaryjoin=Target.id == cls.target_id)

.. _orm_declarative_mixins_mapperproperty:

混合 :func:`_orm.column_property` 和其他 :class:`_orm.MapperProperty` 类
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mixing in :func:`_orm.column_property` and other :class:`_orm.MapperProperty` classes

.. tab:: 中文

    像 :func:`_orm.relationship` 一样，其他 :class:`_orm.MapperProperty` 子类如 :func:`_orm.column_property` 在混入中使用时也需要生成类本地副本，因此也在使用 :class:`_orm.declared_attr` 装饰的函数中声明。在函数内，用 :func:`_orm.mapped_column`、:class:`_orm.Mapped` 或 :class:`_schema.Column` 声明的其他普通映射列将从 ``cls`` 参数中提供，以便它们可以用于组成新属性，如以下示例中将两列相加::

        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class SomethingMixin:
            x: Mapped[int]
            y: Mapped[int]

            @declared_attr
            def x_plus_y(cls) -> Mapped[int]:
                return column_property(cls.x + cls.y)


        class Something(SomethingMixin, Base):
            __tablename__ = "something"

            id: Mapped[int] = mapped_column(primary_key=True)

    如上所示，我们可以在语句中使用 ``Something.x_plus_y`` ，其生成完整的表达式：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Something.x_plus_y))
        {printsql}SELECT something.x + something.y AS anon_1
        FROM something

    .. tip::  
        
        :class:`_orm.declared_attr` 装饰器使被装饰的可调用对象完全像类方法一样运行。然而，像 Pylance_ 这样的类型工具可能无法识别这一点，这有时会导致它对函数体内访问 ``cls`` 变量发出警告。要解决此问题，可以直接将 ``@classmethod`` 装饰器与 :class:`_orm.declared_attr` 结合使用，如::

        class SomethingMixin:
            x: Mapped[int]
            y: Mapped[int]

            @declared_attr
            @classmethod
            def x_plus_y(cls) -> Mapped[int]:
                return column_property(cls.x + cls.y)

    .. versionadded:: 2.0 
        
        - :class:`_orm.declared_attr` 可以适应用 ``@classmethod`` 装饰的函数，以帮助 :pep:`484` 集成在需要时。

.. tab:: 英文

    Like :func:`_orm.relationship`, other
    :class:`_orm.MapperProperty` subclasses such as
    :func:`_orm.column_property` also need to have class-local copies generated
    when used by mixins, so are also declared within functions that are
    decorated by :class:`_orm.declared_attr`.   Within the function,
    other ordinary mapped columns that were declared with :func:`_orm.mapped_column`,
    :class:`_orm.Mapped`, or :class:`_schema.Column` will be made available from the ``cls`` argument
    so that they may be used to compose new attributes, as in the example below which adds two
    columns together::

        from sqlalchemy.orm import column_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class SomethingMixin:
            x: Mapped[int]
            y: Mapped[int]

            @declared_attr
            def x_plus_y(cls) -> Mapped[int]:
                return column_property(cls.x + cls.y)


        class Something(SomethingMixin, Base):
            __tablename__ = "something"

            id: Mapped[int] = mapped_column(primary_key=True)

    Above, we may make use of ``Something.x_plus_y`` in a statement where
    it produces the full expression:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Something.x_plus_y))
        {printsql}SELECT something.x + something.y AS anon_1
        FROM something

    .. tip::  The :class:`_orm.declared_attr` decorator causes the decorated callable
    to behave exactly as a classmethod.  However, typing tools like Pylance_
    may not be able to recognize this, which can sometimes cause it to complain
    about access to the ``cls`` variable inside the body of the function.  To
    resolve this issue when it occurs, the ``@classmethod`` decorator may be
    combined directly with :class:`_orm.declared_attr` as::


        class SomethingMixin:
            x: Mapped[int]
            y: Mapped[int]

            @declared_attr
            @classmethod
            def x_plus_y(cls) -> Mapped[int]:
                return column_property(cls.x + cls.y)

    .. versionadded:: 2.0 - :class:`_orm.declared_attr` can accommodate a
        function decorated with ``@classmethod`` to help with :pep:`484`
        integration where needed.


.. _decl_mixin_inheritance:

使用 Mixins 和基类以及映射继承模式
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Mixins and Base Classes with Mapped Inheritance Patterns

.. tab:: 中文

    在处理映射器继承模式时，如文档 :ref:`inheritance_toplevel` 所述，使用 :class:`_orm.declared_attr` 以及混入类或增强类层次结构中映射和未映射的超类时，会有一些额外的功能。

    在混入类或基类上定义使用 :class:`_orm.declared_attr` 装饰的函数，以便在映射继承层次结构中的子类中解释时，对于生成由声明式使用的特殊名称（如 ``__tablename__`` 、 ``__mapper_args__`` ）的函数与生成普通映射属性（如 :func:`_orm.mapped_column` 和 :func:`_orm.relationship`）的函数之间，有一个重要的区别。定义 **声明式指令(Declarative directives)** 的函数 **针对层次结构中的每个子类调用** ，而生成 **映射属性(mapped attributes)** 的函数 **仅针对层次结构中的第一个映射超类调用** 。

    这种行为差异的理由是基于以下事实：映射属性已经可以被类继承，例如超类的映射表上的特定列不应也复制到子类中，而特定于特定类或其映射表的元素是不可继承的，例如本地映射的表的名称。

    以下两节演示了这两种用例之间的行为差异。

.. tab:: 英文

    When dealing with mapper inheritance patterns as documented at
    :ref:`inheritance_toplevel`, some additional capabilities are present
    when using :class:`_orm.declared_attr` either with mixin classes, or when
    augmenting both mapped and un-mapped superclasses in a class hierarchy.

    When defining functions decorated by :class:`_orm.declared_attr` on mixins or
    base classes to be interpreted by subclasses in a mapped inheritance hierarchy,
    there is an important distinction
    made between functions that generate the special names used by Declarative such
    as ``__tablename__``, ``__mapper_args__`` vs. those that may generate ordinary
    mapped attributes such as :func:`_orm.mapped_column` and
    :func:`_orm.relationship`.  Functions that define **Declarative directives** are
    **invoked for each subclass in a hierarchy**, whereas functions that
    generate **mapped attributes** are **invoked only for the first mapped
    superclass in a hierarchy**.

    The rationale for this difference in behavior is based on the fact that
    mapped properties are already inheritable by classes, such as a particular
    column on a superclass' mapped table should not be duplicated to that of a
    subclass as well, whereas elements that are specific to a particular
    class or its mapped table are not inheritable, such as the name of the
    table that is locally mapped.

    The difference in behavior between these two use cases is demonstrated
    in the following two sections.

使用 :func:`_orm.declared_attr` 继承 :class:`.Table` 和 :class:`.Mapper` 参数
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using :func:`_orm.declared_attr` with inheriting :class:`.Table` and :class:`.Mapper` arguments

.. tab:: 中文

    一个常见的混入用法是创建一个 ``def __tablename__(cls)`` 函数，动态生成映射的 :class:`.Table` 名称。

    这个用法可以用于生成继承映射层次结构中的表名，如下面的示例所示，该示例创建了一个混入，使每个类都具有基于类名的简单表名。下面的示例展示了为映射类 ``Person`` 和 ``Person`` 的子类 ``Engineer`` 生成表名，但不为 ``Person`` 的子类 ``Manager`` 生成表名::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Tablename:
            @declared_attr.directive
            def __tablename__(cls) -> Optional[str]:
                return cls.__name__.lower()


        class Person(Tablename, Base):
            id: Mapped[int] = mapped_column(primary_key=True)
            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)

            primary_language: Mapped[str]

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class Manager(Person):
            @declared_attr.directive
            def __tablename__(cls) -> Optional[str]:
                """覆盖 __tablename__ 使 Manager 为单继承到 Person"""

                return None

            __mapper_args__ = {"polymorphic_identity": "manager"}

    在上面的示例中， ``Person`` 基类和 ``Engineer`` 类，由于它们是生成新表名的 ``Tablename`` 混入类的子类，将具有生成的 ``__tablename__`` 属性，这表示每个类都应该有自己的 :class:`.Table` 生成并映射到它。对于 ``Engineer`` 子类，应用的继承风格是 :ref:`joined table inheritance <joined_inheritance>`，因为它将映射到一个连接到基础 ``person`` 表的 ``engineer`` 表。继承自 ``Person`` 的任何其他子类也将默认应用此继承风格（在此特定示例中，还需要每个子类指定一个主键列；更多内容将在下一节中介绍）。

    相比之下， ``Person`` 的子类 ``Manager`` **覆盖** ``__tablename__`` 类方法以返回 ``None``。这表示声明式不应生成 :class:`.Table`，而是将只使用 ``Person`` 映射到的基础 :class:`.Table`。对于 ``Manager`` 子类，应用的继承风格是 :ref:`single table inheritance <single_inheritance>`。

    上面的示例说明了声明式指令如 ``__tablename__`` 必须 **单独应用于每个子类** ，因为每个映射类都需要声明它将映射到哪个 :class:`.Table`，或者是否将自己映射到继承的超类的 :class:`.Table`。

    如果我们希望 **反转** 上面展示的默认表方案，使单表继承为默认模式，并且只有在提供了 ``__tablename__`` 指令以覆盖它时才定义连接表继承，我们可以在最顶层的 ``__tablename__()`` 方法中使用声明式助手，在这种情况下，这个助手称为 :func:`.has_inherited_table`。如果超类已经映射到 :class:`.Table`，此函数将返回 ``True`` 。我们可以在基类的 ``__tablename__()`` 类方法中使用此助手，以便如果已经存在表，则 **有条件地** 返回 ``None`` 作为表名，从而默认情况下为继承子类指示单表继承::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import has_inherited_table
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Tablename:
            @declared_attr.directive
            def __tablename__(cls):
                if has_inherited_table(cls):
                    return None
                return cls.__name__.lower()


        class Person(Tablename, Base):
            id: Mapped[int] = mapped_column(primary_key=True)
            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            @declared_attr.directive
            def __tablename__(cls):
                """覆盖 __tablename__ 使 Engineer 为连接继承到 Person"""

                return cls.__name__.lower()

            id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)

            primary_language: Mapped[str]

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class Manager(Person):
            __mapper_args__ = {"polymorphic_identity": "manager"}

.. tab:: 英文

    A common recipe with mixins is to create a ``def __tablename__(cls)``
    function that generates a name for the mapped :class:`.Table` dynamically.

    This recipe can be used to generate table names for an inheriting mapper
    hierarchy as in the example below which creates a mixin that gives every class a simple table
    name based on class name.  The recipe is illustrated below where a table name
    is generated for the ``Person`` mapped class and the ``Engineer`` subclass
    of ``Person``, but not for the ``Manager`` subclass of ``Person``::

        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Tablename:
            @declared_attr.directive
            def __tablename__(cls) -> Optional[str]:
                return cls.__name__.lower()


        class Person(Tablename, Base):
            id: Mapped[int] = mapped_column(primary_key=True)
            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)

            primary_language: Mapped[str]

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class Manager(Person):
            @declared_attr.directive
            def __tablename__(cls) -> Optional[str]:
                """override __tablename__ so that Manager is single-inheritance to Person"""

                return None

            __mapper_args__ = {"polymorphic_identity": "manager"}

    In the above example, both the ``Person`` base class as well as the
    ``Engineer`` class, being subclasses of the ``Tablename`` mixin class which
    generates new table names, will have a generated ``__tablename__``
    attribute, which to
    Declarative indicates that each class should have its own :class:`.Table`
    generated to which it will be mapped.   For the ``Engineer`` subclass, the style of inheritance
    applied is :ref:`joined table inheritance <joined_inheritance>`, as it
    will be mapped to a table ``engineer`` that joins to the base ``person``
    table.  Any other subclasses that inherit from ``Person`` will also have
    this style of inheritance applied by default (and within this particular example, would need to
    each specify a primary key column; more on that in the next section).

    By contrast, the ``Manager`` subclass of ``Person`` **overrides** the
    ``__tablename__`` classmethod to return ``None``.   This indicates to
    Declarative that this class should **not** have a :class:`.Table` generated,
    and will instead make use exclusively of the base :class:`.Table` to which
    ``Person`` is mapped.  For the ``Manager`` subclass, the style of inheritance
    applied is :ref:`single table inheritance <single_inheritance>`.

    The example above illustrates that Declarative directives like
    ``__tablename__`` are necessarily **applied to each subclass** individually,
    as each mapped class needs to state which :class:`.Table` it will be mapped
    towards, or if it will map itself to the inheriting superclass' :class:`.Table`.

    If we instead wanted to **reverse** the default table scheme illustrated
    above, so that
    single table inheritance were the default and joined table inheritance
    could be defined only when a ``__tablename__`` directive were supplied to
    override it, we can make use of
    Declarative helpers within the top-most ``__tablename__()`` method, in this
    case a helper called :func:`.has_inherited_table`.  This function will
    return ``True`` if a superclass is already mapped to a :class:`.Table`.
    We may use this helper within the base-most ``__tablename__()`` classmethod
    so that we may **conditionally** return ``None`` for the table name,
    if a table is already present, thus indicating single-table inheritance
    for inheriting subclasses by default::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import has_inherited_table
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Tablename:
            @declared_attr.directive
            def __tablename__(cls):
                if has_inherited_table(cls):
                    return None
                return cls.__name__.lower()


        class Person(Tablename, Base):
            id: Mapped[int] = mapped_column(primary_key=True)
            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            @declared_attr.directive
            def __tablename__(cls):
                """override __tablename__ so that Engineer is joined-inheritance to Person"""

                return cls.__name__.lower()

            id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)

            primary_language: Mapped[str]

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class Manager(Person):
            __mapper_args__ = {"polymorphic_identity": "manager"}

.. _mixin_inheritance_columns:

使用 :func:`_orm.declared_attr` 生成特定于表的继承列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using :func:`_orm.declared_attr` to generate table-specific inheriting columns

.. tab:: 中文

    与使用 :class:`_orm.declared_attr` 处理 ``__tablename__`` 和其他特殊名称的方式相反，当我们混入列和属性（例如关系、列属性等）时，除非将 :class:`_orm.declared_attr` 指令与 :attr:`_orm.declared_attr.cascading` 子指令结合使用，否则该函数仅对层次结构中的 **基类** 调用。如下所示，只有 ``Person`` 类会收到名为 ``id`` 的列；映射将在 ``Engineer`` 上失败，因为没有为其提供主键::

        class HasId:
            id: Mapped[int] = mapped_column(primary_key=True)


        class Person(HasId, Base):
            __tablename__ = "person"

            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        # 此映射将失败，因为没有主键
        class Engineer(Person):
            __tablename__ = "engineer"

            primary_language: Mapped[str]
            __mapper_args__ = {"polymorphic_identity": "engineer"}

    在连接表继承中，我们通常希望在每个子类上命名不同的列。然而，在这种情况下，我们可能希望在每个表上都有一个 ``id`` 列，并通过外键相互引用。我们可以通过使用 :attr:`.declared_attr.cascading` 修饰符来实现这一点，该修饰符指示该函数应该对层次结构中的 **每个类** 调用，几乎（见下文警告）与 ``__tablename__`` 的方式相同::

        class HasIdMixin:
            @declared_attr.cascading
            def id(cls) -> Mapped[int]:
                if has_inherited_table(cls):
                    return mapped_column(ForeignKey("person.id"), primary_key=True)
                else:
                    return mapped_column(Integer, primary_key=True)


        class Person(HasIdMixin, Base):
            __tablename__ = "person"

            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            __tablename__ = "engineer"

            primary_language: Mapped[str]
            __mapper_args__ = {"polymorphic_identity": "engineer"}

    .. warning::

        :attr:`.declared_attr.cascading` 功能当前 **不** 允许子类用不同的函数或值重写属性。这是 ``@declared_attr`` 解析机制中的当前限制，如果检测到这种情况，则会发出警告。此限制仅适用于ORM映射列、关系和其他 :class:`.MapperProperty` 类型的属性。它 **不** 适用于声明式指令，如 ``__tablename__``、 ``__mapper_args__`` 等，这些指令在内部的解析方式与 :attr:`.declared_attr.cascading` 不同。

.. tab:: 英文

    In contrast to how ``__tablename__`` and other special names are handled when
    used with :class:`_orm.declared_attr`, when we mix in columns and properties (e.g.
    relationships, column properties, etc.), the function is
    invoked for the **base class only** in the hierarchy, unless the
    :class:`_orm.declared_attr` directive is used in combination with the
    :attr:`_orm.declared_attr.cascading` sub-directive.  Below, only the
    ``Person`` class will receive a column
    called ``id``; the mapping will fail on ``Engineer``, which is not given
    a primary key::

        class HasId:
            id: Mapped[int] = mapped_column(primary_key=True)


        class Person(HasId, Base):
            __tablename__ = "person"

            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        # this mapping will fail, as there's no primary key
        class Engineer(Person):
            __tablename__ = "engineer"

            primary_language: Mapped[str]
            __mapper_args__ = {"polymorphic_identity": "engineer"}

    It is usually the case in joined-table inheritance that we want distinctly
    named columns on each subclass.  However in this case, we may want to have
    an ``id`` column on every table, and have them refer to each other via
    foreign key.  We can achieve this as a mixin by using the
    :attr:`.declared_attr.cascading` modifier, which indicates that the
    function should be invoked **for each class in the hierarchy**, in *almost*
    (see warning below) the same way as it does for ``__tablename__``::

        class HasIdMixin:
            @declared_attr.cascading
            def id(cls) -> Mapped[int]:
                if has_inherited_table(cls):
                    return mapped_column(ForeignKey("person.id"), primary_key=True)
                else:
                    return mapped_column(Integer, primary_key=True)


        class Person(HasIdMixin, Base):
            __tablename__ = "person"

            discriminator: Mapped[str]
            __mapper_args__ = {"polymorphic_on": "discriminator"}


        class Engineer(Person):
            __tablename__ = "engineer"

            primary_language: Mapped[str]
            __mapper_args__ = {"polymorphic_identity": "engineer"}

    .. warning::

        The :attr:`.declared_attr.cascading` feature currently does
        **not** allow for a subclass to override the attribute with a different
        function or value.  This is a current limitation in the mechanics of
        how ``@declared_attr`` is resolved, and a warning is emitted if
        this condition is detected.   This limitation only applies to
        ORM mapped columns, relationships, and other :class:`.MapperProperty`
        styles of attribute.  It does **not** apply to Declarative directives
        such as ``__tablename__``, ``__mapper_args__``, etc., which
        resolve in a different way internally than that of
        :attr:`.declared_attr.cascading`.


组合来自多个 Mixins 的表/映射器参数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Combining Table/Mapper Arguments from Multiple Mixins

.. tab:: 中文

    在使用声明式混入指定 ``__table_args__`` 或 ``__mapper_args__`` 的情况下，您可能希望将多个混入的某些参数与您希望在类本身上定义的参数合并。这里可以使用 :class:`_orm.declared_attr` 装饰器来创建用户定义的整理例程，从多个集合中提取参数::

        from sqlalchemy.orm import declarative_mixin, declared_attr


        class MySQLSettings:
            __table_args__ = {"mysql_engine": "InnoDB"}


        class MyOtherMixin:
            __table_args__ = {"info": "foo"}


        class MyModel(MySQLSettings, MyOtherMixin, Base):
            __tablename__ = "my_model"

            @declared_attr.directive
            def __table_args__(cls):
                args = dict()
                args.update(MySQLSettings.__table_args__)
                args.update(MyOtherMixin.__table_args__)
                return args

            id = mapped_column(Integer, primary_key=True)

.. tab:: 英文

    In the case of ``__table_args__`` or ``__mapper_args__``
    specified with declarative mixins, you may want to combine
    some parameters from several mixins with those you wish to
    define on the class itself. The
    :class:`_orm.declared_attr` decorator can be used
    here to create user-defined collation routines that pull
    from multiple collections::

        from sqlalchemy.orm import declarative_mixin, declared_attr


        class MySQLSettings:
            __table_args__ = {"mysql_engine": "InnoDB"}


        class MyOtherMixin:
            __table_args__ = {"info": "foo"}


        class MyModel(MySQLSettings, MyOtherMixin, Base):
            __tablename__ = "my_model"

            @declared_attr.directive
            def __table_args__(cls):
                args = dict()
                args.update(MySQLSettings.__table_args__)
                args.update(MyOtherMixin.__table_args__)
                return args

            id = mapped_column(Integer, primary_key=True)

.. _orm_mixins_named_constraints:

使用 Mixins 上的命名约定创建索引和约束
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating Indexes and Constraints with Naming Conventions on Mixins

.. tab:: 中文

    使用命名约束（如 :class:`.Index` 、 :class:`.UniqueConstraint` 、 :class:`.CheckConstraint` ），其中每个对象对于从混入派生的特定表都是唯一的，这需要为每个实际映射的类创建每个对象的单独实例。

    一个简单的示例，定义一个命名的、可能是多列的 :class:`.Index`，适用于从混入派生的所有表，使用 :class:`.Index` 的“内联”形式并将其作为 ``__table_args__`` 的一部分建立，使用 :class:`.declared_attr` 将 ``__table_args__()`` 设为一个类方法，该方法将为每个子类调用::

        class MyMixin:
            a = mapped_column(Integer)
            b = mapped_column(Integer)

            @declared_attr.directive
            def __table_args__(cls):
                return (Index(f"test_idx_{cls.__tablename__}", "a", "b"),)


        class MyModelA(MyMixin, Base):
            __tablename__ = "table_a"
            id = mapped_column(Integer, primary_key=True)


        class MyModelB(MyMixin, Base):
            __tablename__ = "table_b"
            id = mapped_column(Integer, primary_key=True)

    上面的示例将生成两个表 ``"table_a"`` 和 ``"table_b"`` ，索引为 ``"test_idx_table_a"`` 和 ``"test_idx_table_b"`` 。

    通常，在现代SQLAlchemy中我们会使用命名约定，如文档 :ref:`constraint_naming_conventions` 所述。尽管命名约定在创建新的 :class:`.Constraint` 对象时会自动应用，因这种约定在对象构造时基于特定 :class:`.Constraint` 的父 :class:`.Table` 应用，因此需要为每个继承子类创建一个独特的 :class:`.Constraint` 对象，其自身具有 :class:`.Table`，再次使用 :class:`.declared_attr` 和 ``__table_args__()``，如下所示，使用一个抽象映射基类::

        from uuid import UUID

        from sqlalchemy import CheckConstraint
        from sqlalchemy import create_engine
        from sqlalchemy import MetaData
        from sqlalchemy import UniqueConstraint
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column

        constraint_naming_conventions = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }


        class Base(DeclarativeBase):
            metadata = MetaData(naming_convention=constraint_naming_conventions)


        class MyAbstractBase(Base):
            __abstract__ = True

            @declared_attr.directive
            def __table_args__(cls):
                return (
                    UniqueConstraint("uuid"),
                    CheckConstraint("x > 0 OR y < 100", name="xy_chk"),
                )

            id: Mapped[int] = mapped_column(primary_key=True)
            uuid: Mapped[UUID]
            x: Mapped[int]
            y: Mapped[int]


        class ModelAlpha(MyAbstractBase):
            __tablename__ = "alpha"


        class ModelBeta(MyAbstractBase):
            __tablename__ = "beta"

    上面的映射将生成包括表特定名称的所有约束的DDL，包括主键、CHECK约束、唯一约束：

    .. sourcecode:: sql

        CREATE TABLE alpha (
            id INTEGER NOT NULL,
            uuid CHAR(32) NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            CONSTRAINT pk_alpha PRIMARY KEY (id),
            CONSTRAINT uq_alpha_uuid UNIQUE (uuid),
            CONSTRAINT ck_alpha_xy_chk CHECK (x > 0 OR y < 100)
        )


        CREATE TABLE beta (
            id INTEGER NOT NULL,
            uuid CHAR(32) NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            CONSTRAINT pk_beta PRIMARY KEY (id),
            CONSTRAINT uq_beta_uuid UNIQUE (uuid),
            CONSTRAINT ck_beta_xy_chk CHECK (x > 0 OR y < 100)
        )

.. tab:: 英文

    Using named constraints such as :class:`.Index`, :class:`.UniqueConstraint`,
    :class:`.CheckConstraint`, where each object is to be unique to a specific
    table descending from a mixin, requires that an individual instance of each
    object is created per actual mapped class.

    As a simple example, to define a named, potentially multicolumn :class:`.Index`
    that applies to all tables derived from a mixin, use the "inline" form of
    :class:`.Index` and establish it as part of ``__table_args__``, using
    :class:`.declared_attr` to establish ``__table_args__()`` as a class method
    that will be invoked for each subclass::

        class MyMixin:
            a = mapped_column(Integer)
            b = mapped_column(Integer)

            @declared_attr.directive
            def __table_args__(cls):
                return (Index(f"test_idx_{cls.__tablename__}", "a", "b"),)


        class MyModelA(MyMixin, Base):
            __tablename__ = "table_a"
            id = mapped_column(Integer, primary_key=True)


        class MyModelB(MyMixin, Base):
            __tablename__ = "table_b"
            id = mapped_column(Integer, primary_key=True)

    The above example would generate two tables ``"table_a"`` and ``"table_b"``, with
    indexes ``"test_idx_table_a"`` and ``"test_idx_table_b"``

    Typically, in modern SQLAlchemy we would use a naming convention,
    as documented at :ref:`constraint_naming_conventions`.   While naming conventions
    take place automatically using the :paramref:`_schema.MetaData.naming_convention`
    as new :class:`.Constraint` objects are created, as this convention is applied
    at object construction time based on the parent :class:`.Table` for a particular
    :class:`.Constraint`, a distinct :class:`.Constraint` object needs to be created
    for each inheriting subclass with its own :class:`.Table`, again using
    :class:`.declared_attr` with ``__table_args__()``, below illustrated using
    an abstract mapped base::

        from uuid import UUID

        from sqlalchemy import CheckConstraint
        from sqlalchemy import create_engine
        from sqlalchemy import MetaData
        from sqlalchemy import UniqueConstraint
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import declared_attr
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column

        constraint_naming_conventions = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }


        class Base(DeclarativeBase):
            metadata = MetaData(naming_convention=constraint_naming_conventions)


        class MyAbstractBase(Base):
            __abstract__ = True

            @declared_attr.directive
            def __table_args__(cls):
                return (
                    UniqueConstraint("uuid"),
                    CheckConstraint("x > 0 OR y < 100", name="xy_chk"),
                )

            id: Mapped[int] = mapped_column(primary_key=True)
            uuid: Mapped[UUID]
            x: Mapped[int]
            y: Mapped[int]


        class ModelAlpha(MyAbstractBase):
            __tablename__ = "alpha"


        class ModelBeta(MyAbstractBase):
            __tablename__ = "beta"

    The above mapping will generate DDL that includes table-specific names
    for all constraints, including primary key, CHECK constraint, unique
    constraint:

    .. sourcecode:: sql

        CREATE TABLE alpha (
            id INTEGER NOT NULL,
            uuid CHAR(32) NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            CONSTRAINT pk_alpha PRIMARY KEY (id),
            CONSTRAINT uq_alpha_uuid UNIQUE (uuid),
            CONSTRAINT ck_alpha_xy_chk CHECK (x > 0 OR y < 100)
        )


        CREATE TABLE beta (
            id INTEGER NOT NULL,
            uuid CHAR(32) NOT NULL,
            x INTEGER NOT NULL,
            y INTEGER NOT NULL,
            CONSTRAINT pk_beta PRIMARY KEY (id),
            CONSTRAINT uq_beta_uuid UNIQUE (uuid),
            CONSTRAINT ck_beta_xy_chk CHECK (x > 0 OR y < 100)
        )



.. _Pylance: https://github.com/microsoft/pylance-release

