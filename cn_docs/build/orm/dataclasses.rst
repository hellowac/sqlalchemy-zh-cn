.. _orm_dataclasses_toplevel:

======================================
与dataclass和attrs的集成
======================================

Integration with dataclasses and attrs

.. tab:: 中文

    SQLAlchemy 自 2.0 版本起，支持“原生数据类”集成，通过在映射类中添加一个混入或装饰器，可以将 :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 映射转换为 Python 数据类_。

    .. versionadded:: 2.0 
        
        与 ORM 声明类集成的数据类创建

    还有一些模式允许映射现有的数据类，以及映射由 attrs_ 第三方集成库注入的类。

.. tab:: 英文

    SQLAlchemy as of version 2.0 features "native dataclass" integration where
    an :ref:`Annotated Declarative Table <orm_declarative_mapped_column>`
    mapping may be turned into a Python dataclass_ by adding a single mixin
    or decorator to mapped classes.

    .. versionadded:: 2.0 Integrated dataclass creation with ORM Declarative classes

    There are also patterns available that allow existing dataclasses to be
    mapped, as well as to map classes instrumented by the
    attrs_ third party integration library.

.. _orm_declarative_native_dataclasses:

声明式Dataclass映射
-----------------------------

Declarative Dataclass Mapping

.. tab:: 中文

    SQLAlchemy :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 映射可以通过额外的混入类或装饰器指令进行增强，这将在映射完成后为声明式过程添加一个额外步骤，该步骤将在完成映射过程之前将映射类 **就地(in-place)** 转换为 Python 数据类_，然后应用 ORM 特定的 :term:`instrumentation` 到类中。这种增强提供的最显著的行为是生成一个具有位置参数和关键字参数的细粒度控制的 ``__init__()`` 方法，无论是否有默认值，以及生成像 ``__repr__()`` 和 ``__eq__()`` 这样的方法。

    从 :pep:`484` 类型注释的角度来看，该类被认为具有数据类特定的行为，最显著的是利用 :pep:`681` “数据类转换”，这允许类型工具将该类视为使用 ``@dataclasses.dataclass`` 装饰器显式装饰的类。

    .. note::  
        
        截至 **2023年4月4日**，类型工具对 :pep:`681` 的支持有限，目前已知 Pyright_ 以及 Mypy_ 从 **1.2 版本** 开始支持。请注意，Mypy 1.1.1 引入了 :pep:`681` 支持，但没有正确适应 Python 描述符，这会在使用 SQLAlchemy 的 ORM 映射方案时导致错误。

    .. seealso::

        https://peps.python.org/pep-0681/#the-dataclass-transform-decorator - 有关像 SQLAlchemy 这样的库如何实现 :pep:`681` 支持的背景信息


    数据类转换可以通过添加 :class:`_orm.MappedAsDataclass` 混入到 :class:`_orm.DeclarativeBase` 类层次结构中，或通过使用 :meth:`_orm.registry.mapped_as_dataclass` 类装饰器进行装饰映射。

    :class:`_orm.MappedAsDataclass` 混入可以应用于声明式 ``Base`` 类或任何超类，如下例所示::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(MappedAsDataclass, DeclarativeBase):
            """子类将转换为数据类"""


        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    也可以直接应用于从声明式基类扩展的类::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(DeclarativeBase):
            pass


        class User(MappedAsDataclass, Base):
            """User 类将转换为数据类"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    使用装饰器形式时，仅支持 :meth:`_orm.registry.mapped_as_dataclass` 装饰器::

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry


        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

.. tab:: 英文

    SQLAlchemy :ref:`Annotated Declarative Table <orm_declarative_mapped_column>`
    mappings may be augmented with an additional
    mixin class or decorator directive, which will add an additional step to
    the Declarative process after the mapping is complete that will convert
    the mapped class **in-place** into a Python dataclass_, before completing
    the mapping process which applies ORM-specific :term:`instrumentation`
    to the class.   The most prominent behavioral addition this provides is
    generation of an ``__init__()`` method with fine-grained control over
    positional and keyword arguments with or without defaults, as well as
    generation of methods like ``__repr__()`` and ``__eq__()``.

    From a :pep:`484` typing perspective, the class is recognized
    as having Dataclass-specific behaviors, most notably  by taking advantage of :pep:`681`
    "Dataclass Transforms", which allows typing tools to consider the class
    as though it were explicitly decorated using the ``@dataclasses.dataclass``
    decorator.

    .. note::  Support for :pep:`681` in typing tools as of **April 4, 2023** is
    limited and is currently known to be supported by Pyright_ as well
    as Mypy_ as of **version 1.2**.  Note that Mypy 1.1.1 introduced
    :pep:`681` support but did not correctly accommodate Python descriptors
    which will lead to errors when using SQLAlchemy's ORM mapping scheme.

    .. seealso::

        https://peps.python.org/pep-0681/#the-dataclass-transform-decorator - background
        on how libraries like SQLAlchemy enable :pep:`681` support


    Dataclass conversion may be added to any Declarative class either by adding the
    :class:`_orm.MappedAsDataclass` mixin to a :class:`_orm.DeclarativeBase` class
    hierarchy, or for decorator mapping by using the
    :meth:`_orm.registry.mapped_as_dataclass` class decorator.

    The :class:`_orm.MappedAsDataclass` mixin may be applied either
    to the Declarative ``Base`` class or any superclass, as in the example
    below::


        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(MappedAsDataclass, DeclarativeBase):
            """subclasses will be converted to dataclasses"""


        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    Or may be applied directly to classes that extend from the Declarative base::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(DeclarativeBase):
            pass


        class User(MappedAsDataclass, Base):
            """User class will be converted to a dataclass"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    When using the decorator form, only the :meth:`_orm.registry.mapped_as_dataclass`
    decorator is supported::

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry


        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

类级功能配置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Class level feature configuration

.. tab:: 中文

    对数据类功能的支持是部分的。目前 **支持** 的功能包括 ``init``、 ``repr``、 ``eq``、 ``order`` 和 ``unsafe_hash``，在 Python 3.10+ 上还支持 ``match_args`` 和 ``kw_only``。当前 **不支持** 的功能包括 ``frozen`` 和 ``slots``。

    当使用 :class:`_orm.MappedAsDataclass` 混入类形式时，类配置参数作为类级参数传递::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(DeclarativeBase):
            pass


        class User(MappedAsDataclass, Base, repr=False, unsafe_hash=True):
            """User 类将转换为数据类"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    当使用 :meth:`_orm.registry.mapped_as_dataclass` 装饰器形式时，类配置参数直接传递给装饰器::

        from sqlalchemy.orm import registry
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        reg = registry()


        @reg.mapped_as_dataclass(unsafe_hash=True)
        class User:
            """User 类将转换为数据类"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    有关数据类类选项的背景信息，请参阅 dataclasses_ 文档
    在 `@dataclasses.dataclass <https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass>`_。

.. tab:: 英文

    Support for dataclasses features is partial.  Currently **supported** are
    the ``init``, ``repr``, ``eq``, ``order`` and ``unsafe_hash`` features,
    ``match_args`` and ``kw_only`` are supported on Python 3.10+.
    Currently **not supported** are the ``frozen`` and ``slots`` features.

    When using the mixin class form with :class:`_orm.MappedAsDataclass`,
    class configuration arguments are passed as class-level parameters::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass


        class Base(DeclarativeBase):
            pass


        class User(MappedAsDataclass, Base, repr=False, unsafe_hash=True):
            """User class will be converted to a dataclass"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    When using the decorator form with :meth:`_orm.registry.mapped_as_dataclass`,
    class configuration arguments are passed to the decorator directly::

        from sqlalchemy.orm import registry
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        reg = registry()


        @reg.mapped_as_dataclass(unsafe_hash=True)
        class User:
            """User class will be converted to a dataclass"""

            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

    For background on dataclass class options, see the dataclasses_ documentation
    at `@dataclasses.dataclass <https://docs.python.org/3/library/dataclasses.html#dataclasses.dataclass>`_.

属性配置
^^^^^^^^^^^^^^^^^^^^^^^

Attribute Configuration

.. tab:: 中文

    SQLAlchemy 原生数据类与普通数据类不同，映射的属性在所有情况下都使用 :class:`_orm.Mapped` 泛型注解容器描述。映射遵循 :ref:`orm_declarative_table` 中记录的相同形式，并且支持 :func:`_orm.mapped_column` 和 :class:`_orm.Mapped` 的所有功能。

    此外，ORM 属性配置结构包括 :func:`_orm.mapped_column`、:func:`_orm.relationship` 和 :func:`_orm.composite` 支持 **每个属性字段选项** ，包括 ``init``、 ``default``、 ``default_factory`` 和 ``repr``。这些参数的名称如 :pep:`681` 中规定的那样是固定的。功能等同于数据类：

    * ``init``，如 :paramref:`_orm.mapped_column.init`， :paramref:`_orm.relationship.init`，如果为 False 表示该字段不应成为 ``__init__()`` 方法的一部分
    * ``default``，如 :paramref:`_orm.mapped_column.default`， :paramref:`_orm.relationship.default` 表示该字段在 ``__init__()`` 方法中作为关键字参数的默认值。
    * ``default_factory``，如 :paramref:`_orm.mapped_column.default_factory`， :paramref:`_orm.relationship.default_factory`，表示一个可调用函数，如果在 ``__init__()`` 方法中没有显式传递参数，将调用该函数生成一个新的默认值。
    * ``repr`` 默认为 True，表示该字段应成为生成的 ``__repr__()`` 方法的一部分

    另一个与数据类的关键区别是属性的默认值 **必须** 使用 ORM 结构的 ``default`` 参数配置，例如 ``mapped_column(default=None)``。不支持类似数据类语法的接受简单 Python 值作为默认值的语法，而无需使用 ``@dataclasses.field()``。

    以下使用 :func:`_orm.mapped_column` 的示例将生成一个 ``__init__()`` 方法，该方法仅接受字段 ``name`` 和 ``fullname``，其中 ``name`` 是必需的，可以按位置传递，而 ``fullname`` 是可选的。我们期望由数据库生成的 ``id`` 字段完全不在构造函数中::

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str] = mapped_column(default=None)


        # 'fullname' 是可选的关键字参数
        u1 = User("name")

.. tab:: 英文

    SQLAlchemy native dataclasses differ from normal dataclasses in that
    attributes to be mapped are described using the :class:`_orm.Mapped`
    generic annotation container in all cases.    Mappings follow the same
    forms as those documented at :ref:`orm_declarative_table`, and all
    features of :func:`_orm.mapped_column` and :class:`_orm.Mapped` are supported.

    Additionally, ORM attribute configuration constructs including
    :func:`_orm.mapped_column`, :func:`_orm.relationship` and :func:`_orm.composite`
    support **per-attribute field options**, including ``init``, ``default``,
    ``default_factory`` and ``repr``.  The names of these arguments is fixed
    as specified in :pep:`681`.   Functionality is equivalent to dataclasses:

    * ``init``, as in :paramref:`_orm.mapped_column.init`,
    :paramref:`_orm.relationship.init`, if False indicates the field should
    not be part of the ``__init__()`` method
    * ``default``, as in :paramref:`_orm.mapped_column.default`,
    :paramref:`_orm.relationship.default`
    indicates a default value for the field as given as a keyword argument
    in the ``__init__()`` method.
    * ``default_factory``, as in :paramref:`_orm.mapped_column.default_factory`,
    :paramref:`_orm.relationship.default_factory`, indicates a callable function
    that will be invoked to generate a new default value for a parameter
    if not passed explicitly to the ``__init__()`` method.
    * ``repr`` True by default, indicates the field should be part of the generated
    ``__repr__()`` method


    Another key difference from dataclasses is that default values for attributes
    **must** be configured using the ``default`` parameter of the ORM construct,
    such as ``mapped_column(default=None)``.   A syntax that resembles dataclass
    syntax which accepts simple Python values as defaults without using
    ``@dataclases.field()`` is not supported.

    As an example using :func:`_orm.mapped_column`, the mapping below will
    produce an ``__init__()`` method that accepts only the fields ``name`` and
    ``fullname``, where ``name`` is required and may be passed positionally,
    and ``fullname`` is optional.  The ``id`` field, which we expect to be
    database-generated, is not part of the constructor at all::

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[str] = mapped_column(default=None)


        # 'fullname' is optional keyword argument
        u1 = User("name")

列默认值
~~~~~~~~~~~~~~~

Column Defaults

.. tab:: 中文

    为了适应 ``default`` 参数与 :class:`_schema.Column` 结构的现有 :paramref:`_schema.Column.default` 参数的名称重叠，:func:`_orm.mapped_column` 结构通过添加一个新参数 :paramref:`_orm.mapped_column.insert_default` 来消除两者的歧义，该参数将直接填充到 :class:`_schema.Column` 的 :paramref:`_schema.Column.default` 参数中，而不管在 :paramref:`_orm.mapped_column.default` 上设置了什么值，:paramref:`_orm.mapped_column.default` 始终用于数据类配置。例如，配置一个 datetime 列，其 :paramref:`_schema.Column.default` 设置为 ``func.utc_timestamp()`` SQL 函数，但该参数在构造函数中是可选的::

        from datetime import datetime

        from sqlalchemy import func
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            created_at: Mapped[datetime] = mapped_column(
                insert_default=func.utc_timestamp(), default=None
            )

    在上述映射中，如果在创建新的 ``User`` 对象时没有传递 ``created_at`` 参数，``INSERT`` 将按以下方式进行：

    .. sourcecode:: pycon+sql

        >>> with Session(e) as session:
        ...     session.add(User())
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (created_at) VALUES (utc_timestamp())
        [generated in 0.00010s] ()
        COMMIT

.. tab:: 英文

    In order to accommodate the name overlap of the ``default`` argument with
    the existing :paramref:`_schema.Column.default` parameter of the  :class:`_schema.Column`
    construct, the :func:`_orm.mapped_column` construct disambiguates the two
    names by adding a new parameter :paramref:`_orm.mapped_column.insert_default`,
    which will be populated directly into the
    :paramref:`_schema.Column.default` parameter of  :class:`_schema.Column`,
    independently of what may be set on
    :paramref:`_orm.mapped_column.default`, which is always used for the
    dataclasses configuration.  For example, to configure a datetime column with
    a :paramref:`_schema.Column.default` set to the ``func.utc_timestamp()`` SQL function,
    but where the parameter is optional in the constructor::

        from datetime import datetime

        from sqlalchemy import func
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            created_at: Mapped[datetime] = mapped_column(
                insert_default=func.utc_timestamp(), default=None
            )

    With the above mapping, an ``INSERT`` for a new ``User`` object where no
    parameter for ``created_at`` were passed proceeds as:

    .. sourcecode:: pycon+sql

        >>> with Session(e) as session:
        ...     session.add(User())
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (created_at) VALUES (utc_timestamp())
        [generated in 0.00010s] ()
        COMMIT



与注解集成
~~~~~~~~~~~~~~~~~~~~~~~~~~

Integration with Annotated

.. tab:: 中文

    在 :ref:`orm_declarative_mapped_column_pep593` 中介绍的方法展示了如何使用 :pep:`593` ``Annotated`` 对象来打包整个 :func:`_orm.mapped_column` 结构以便重用。虽然 ``Annotated`` 对象可以与数据类一起使用，但 **不幸的是，数据类特定的关键字参数不能在 Annotated 结构中使用** 。这些包括 :pep:`681` 特定的参数 ``init``、 ``default``、 ``repr`` 和 ``default_factory``，它们 **必须** 出现在与类属性内联的 :func:`_orm.mapped_column` 或类似结构中。

    .. versionchanged:: 2.0.14/2.0.22  
        
        当 ``Annotated`` 结构与像 :func:`_orm.mapped_column` 这样的 ORM 结构一起使用时，不能容纳数据类字段参数如 ``init`` 和 ``repr`` - 这种用法违反了 Python 数据类的设计，并且不受 :pep:`681` 支持，因此在运行时也被 SQLAlchemy ORM 拒绝。现在发出弃用警告，并且该属性将被忽略。

    例如，下面的 ``init=False`` 参数将被忽略并另外发出弃用警告::

        from typing import Annotated

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        # 类型工具以及 SQLAlchemy 将忽略此处的 init=False
        intpk = Annotated[int, mapped_column(init=False, primary_key=True)]

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"
            id: Mapped[intpk]


        # 类型错误以及运行时错误：缺少参数 "id"
        u1 = User()

    相反，:func:`_orm.mapped_column` 必须在右侧显式设置 :paramref:`_orm.mapped_column.init`；其他参数可以保留在 ``Annotated`` 结构中::

        from typing import Annotated

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        intpk = Annotated[int, mapped_column(primary_key=True)]

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            # init=False 和其他 pep-681 参数必须内联
            id: Mapped[intpk] = mapped_column(init=False)


        u1 = User()

.. tab:: 英文

    The approach introduced at :ref:`orm_declarative_mapped_column_pep593`
    illustrates how to use :pep:`593` ``Annotated`` objects to package whole
    :func:`_orm.mapped_column` constructs for re-use.  While ``Annotated`` objects
    can be combined with the use of dataclasses, **dataclass-specific keyword
    arguments unfortunately cannot be used within the Annotated construct**.  This
    includes :pep:`681`-specific arguments ``init``, ``default``, ``repr``, and
    ``default_factory``, which **must** be present in a :func:`_orm.mapped_column`
    or similar construct inline with the class attribute.
    
    .. versionchanged:: 2.0.14/2.0.22  the ``Annotated`` construct when used with
       an ORM construct like :func:`_orm.mapped_column` cannot accommodate dataclass
       field parameters such as ``init`` and ``repr`` - this use goes against the
       design of Python dataclasses and is not supported by :pep:`681`, and therefore
       is also rejected by the SQLAlchemy ORM at runtime.   A deprecation warning
       is now emitted and the attribute will be ignored.
    
    As an example, the ``init=False`` parameter below will be ignored and additionally
    emit a deprecation warning::
    
        from typing import Annotated
    
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
    
        # typing tools as well as SQLAlchemy will ignore init=False here
        intpk = Annotated[int, mapped_column(init=False, primary_key=True)]
    
        reg = registry()
    
    
        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"
            id: Mapped[intpk]
    
    
        # typing error as well as runtime error: Argument missing for parameter "id"
        u1 = User()
    
    Instead, :func:`_orm.mapped_column` must be present on the right side
    as well with an explicit setting for :paramref:`_orm.mapped_column.init`;
    the other arguments can remain within the ``Annotated`` construct::
    
        from typing import Annotated
    
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
    
        intpk = Annotated[int, mapped_column(primary_key=True)]
    
        reg = registry()
    
    
        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"
    
            # init=False and other pep-681 arguments must be inline
            id: Mapped[intpk] = mapped_column(init=False)
    
    
        u1 = User()

.. _orm_declarative_dc_mixins:

使用混合和抽象超类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using mixins and abstract superclasses

.. tab:: 中文

    任何在 :class:`_orm.MappedAsDataclass` 映射类中使用的混入或基类，如果包含 :class:`_orm.Mapped` 属性，则它们本身必须是 :class:`_orm.MappedAsDataclass` 层次结构的一部分，例如在下面的示例中使用混入::

        class Mixin(MappedAsDataclass):
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)


        class Base(DeclarativeBase, MappedAsDataclass):
            pass


        class User(Base, Mixin):
            __tablename__ = "sys_user"

            uid: Mapped[str] = mapped_column(
                String(50), init=False, default_factory=uuid4, primary_key=True
            )
            username: Mapped[str] = mapped_column()
            email: Mapped[str] = mapped_column()

    支持 :pep:`681` 的 Python 类型检查器否则不会将非数据类混入的属性视为数据类的一部分。

    .. deprecated:: 2.0.8 
        
        在 :class:`_orm.MappedAsDataclass` 或 :meth:`_orm.registry.mapped_as_dataclass` 层次结构中使用混入和抽象基类，如果它们本身不是数据类，则已弃用，因为这些字段不被 :pep:`681` 视为属于数据类。在这种情况下会发出警告，后来将成为错误。

    .. seealso::

        :ref:`error_dcmx` - 有关原因的背景

.. tab:: 英文

    Any mixins or base classes that are used in a :class:`_orm.MappedAsDataclass`
    mapped class which include :class:`_orm.Mapped` attributes must themselves be
    part of a :class:`_orm.MappedAsDataclass`
    hierarchy, such as in the example below using a mixin::


        class Mixin(MappedAsDataclass):
            create_user: Mapped[int] = mapped_column()
            update_user: Mapped[Optional[int]] = mapped_column(default=None, init=False)


        class Base(DeclarativeBase, MappedAsDataclass):
            pass


        class User(Base, Mixin):
            __tablename__ = "sys_user"

            uid: Mapped[str] = mapped_column(
                String(50), init=False, default_factory=uuid4, primary_key=True
            )
            username: Mapped[str] = mapped_column()
            email: Mapped[str] = mapped_column()

    Python type checkers which support :pep:`681` will otherwise not consider
    attributes from non-dataclass mixins to be part of the dataclass.

    .. deprecated:: 2.0.8  
        
        Using mixins and abstract bases within :class:`_orm.MappedAsDataclass` or :meth:`_orm.registry.mapped_as_dataclass` hierarchies which are not themselves dataclasses is deprecated, as these fields are not supported by :pep:`681` as belonging to the dataclass.  A warning is emitted for this case which will later be an error.

    .. seealso::

        :ref:`error_dcmx` - background on rationale




关系配置
^^^^^^^^^^^^^^^^^^^^^^^^^^

Relationship Configuration

.. tab:: 中文

    :class:`_orm.Mapped` 注解与 :func:`_orm.relationship` 结合使用的方式与 :ref:`relationship_patterns` 中描述的相同。当将基于集合的 :func:`_orm.relationship` 指定为可选关键字参数时，必须传递 :paramref:`_orm.relationship.default_factory` 参数，并且它必须引用要使用的集合类。如果默认值为 ``None``，多对一和标量对象引用可以使用 :paramref:`_orm.relationship.default`::

        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        reg = registry()


        @reg.mapped_as_dataclass
        class Parent:
            __tablename__ = "parent"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(
                default_factory=list, back_populates="parent"
            )


        @reg.mapped_as_dataclass
        class Child:
            __tablename__ = "child"
            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
            parent: Mapped["Parent"] = relationship(default=None)

    上述映射将在没有传递 ``children`` 的情况下构造新的 ``Parent()`` 对象时为 ``Parent.children`` 生成一个空列表，并且在没有传递 ``parent`` 的情况下构造新的 ``Child()`` 对象时为 ``Child.parent`` 生成一个 ``None`` 值。

    虽然 :func:`_orm.relationship` 本身的给定集合类可以自动派生 :paramref:`_orm.relationship.default_factory`，但这会破坏与数据类的兼容性，因为 :paramref:`_orm.relationship.default_factory` 或 :paramref:`_orm.relationship.default` 的存在决定了参数在渲染到 ``__init__()`` 方法时是否必须或可选。

.. tab:: 英文

    The :class:`_orm.Mapped` annotation in combination with
    :func:`_orm.relationship` is used in the same way as described at
    :ref:`relationship_patterns`.    When specifying a collection-based
    :func:`_orm.relationship` as an optional keyword argument, the
    :paramref:`_orm.relationship.default_factory` parameter must be passed and it
    must refer to the collection class that's to be used.  Many-to-one and
    scalar object references may make use of
    :paramref:`_orm.relationship.default` if the default value is to be ``None``::

        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        reg = registry()


        @reg.mapped_as_dataclass
        class Parent:
            __tablename__ = "parent"
            id: Mapped[int] = mapped_column(primary_key=True)
            children: Mapped[List["Child"]] = relationship(
                default_factory=list, back_populates="parent"
            )


        @reg.mapped_as_dataclass
        class Child:
            __tablename__ = "child"
            id: Mapped[int] = mapped_column(primary_key=True)
            parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))
            parent: Mapped["Parent"] = relationship(default=None)

    The above mapping will generate an empty list for ``Parent.children`` when a
    new ``Parent()`` object is constructed without passing ``children``, and
    similarly a ``None`` value for ``Child.parent`` when a new ``Child()`` object
    is constructed without passing ``parent``.

    While the :paramref:`_orm.relationship.default_factory` can be automatically
    derived from the given collection class of the :func:`_orm.relationship`
    itself, this would break compatibility with dataclasses, as the presence
    of :paramref:`_orm.relationship.default_factory` or
    :paramref:`_orm.relationship.default` is what determines if the parameter is
    to be required or optional when rendered into the ``__init__()`` method.

.. _orm_declarative_native_dataclasses_non_mapped_fields:

使用非映射数据类字段
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Non-Mapped Dataclass Fields

.. tab:: 中文

    在使用声明式数据类时，非映射字段也可以在类中使用，它们将成为数据类构造过程的一部分，但不会被映射。任何不使用 :class:`.Mapped` 的字段都将被映射过程忽略。如下例所示，字段 ``ctrl_one`` 和 ``ctrl_two`` 将成为对象的实例级状态的一部分，但不会被 ORM 持久化::

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class Data:
            __tablename__ = "data"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            status: Mapped[str]

            ctrl_one: Optional[str] = None
            ctrl_two: Optional[str] = None

    上面的 ``Data`` 实例可以创建为::

        d1 = Data(status="s1", ctrl_one="ctrl1", ctrl_two="ctrl2")

    一个更现实的例子可能是结合 ``__post_init__()`` 功能使用 Dataclasses 的 ``InitVar`` 功能来接收仅初始化字段，这些字段可用于组合持久化数据。如下例所示， ``User`` 类使用 ``id``、``name`` 和 ``password_hash`` 作为映射特性，但使用仅初始化的 ``password`` 和 ``repeat_password`` 字段来表示用户创建过程 (注意：要运行此示例，请将函数 ``your_crypt_function_here()`` 替换为第三方加密函数，如 `bcrypt <https://pypi.org/project/bcrypt/>`_ 或 `argon2-cffi <https://pypi.org/project/argon2-cffi/>`_)::

        from dataclasses import InitVar
        from typing import Optional

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

            password: InitVar[str]
            repeat_password: InitVar[str]

            password_hash: Mapped[str] = mapped_column(init=False, nullable=False)

            def __post_init__(self, password: str, repeat_password: str):
                if password != repeat_password:
                    raise ValueError("passwords do not match")

                self.password_hash = your_crypt_function_here(password)

    上述对象使用参数 ``password`` 和 ``repeat_password`` 创建，这些参数会被提前消耗，以便生成 ``password_hash`` 变量::

        >>> u1 = User(name="some_user", password="xyz", repeat_password="xyz")
        >>> u1.password_hash
        '$6$9ppc... (example crypted string....)'

    .. versionchanged:: 2.0.0rc1  
        
        使用 :meth:`_orm.registry.mapped_as_dataclass` 或 :class:`.MappedAsDataclass` 时，可以包含不包括 :class:`.Mapped` 注解的字段，这些字段将被视为生成的数据类的一部分，但不会被映射，而无需同时指示 ``__allow_unmapped__`` 类属性。以前的 2.0 测试版需要显式存在此属性，尽管此属性的目的是仅允许旧版 ORM 类型映射继续运行。

.. tab:: 英文

    When using Declarative dataclasses, non-mapped fields may be used on the
    class as well, which will be part of the dataclass construction process but
    will not be mapped.   Any field that does not use :class:`.Mapped` will
    be ignored by the mapping process.   In the example below, the fields
    ``ctrl_one`` and ``ctrl_two`` will be part of the instance-level state
    of the object, but will not be persisted by the ORM::


        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class Data:
            __tablename__ = "data"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            status: Mapped[str]

            ctrl_one: Optional[str] = None
            ctrl_two: Optional[str] = None

    Instance of ``Data`` above can be created as::

        d1 = Data(status="s1", ctrl_one="ctrl1", ctrl_two="ctrl2")

    A more real world example might be to make use of the Dataclasses
    ``InitVar`` feature in conjunction with the ``__post_init__()`` feature to
    receive init-only fields that can be used to compose persisted data.
    In the example below, the ``User``
    class is declared using ``id``, ``name`` and ``password_hash`` as mapped features,
    but makes use of init-only ``password`` and ``repeat_password`` fields to
    represent the user creation process (note: to run this example, replace
    the function ``your_crypt_function_here()`` with a third party crypt
    function, such as `bcrypt <https://pypi.org/project/bcrypt/>`_ or
    `argon2-cffi <https://pypi.org/project/argon2-cffi/>`_)::

        from dataclasses import InitVar
        from typing import Optional

        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped_as_dataclass
        class User:
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(init=False, primary_key=True)
            name: Mapped[str]

            password: InitVar[str]
            repeat_password: InitVar[str]

            password_hash: Mapped[str] = mapped_column(init=False, nullable=False)

            def __post_init__(self, password: str, repeat_password: str):
                if password != repeat_password:
                    raise ValueError("passwords do not match")

                self.password_hash = your_crypt_function_here(password)

    The above object is created with parameters ``password`` and
    ``repeat_password``, which are consumed up front so that the ``password_hash``
    variable may be generated::

        >>> u1 = User(name="some_user", password="xyz", repeat_password="xyz")
        >>> u1.password_hash
        '$6$9ppc... (example crypted string....)'

    .. versionchanged:: 2.0.0rc1  
        
        When using :meth:`_orm.registry.mapped_as_dataclass` or :class:`.MappedAsDataclass`, fields that do not include the :class:`.Mapped` annotation may be included, which will be treated as part of the resulting dataclass but not be mapped, without the need to also indicate the ``__allow_unmapped__`` class attribute.  Previous 2.0 beta releases would require this attribute to be explicitly present, even though the purpose of this attribute was only to allow legacy ORM typed mappings to continue to function.

.. _dataclasses_pydantic:

与 Pydantic 等备用数据类提供程序集成
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integrating with Alternate Dataclass Providers such as Pydantic

.. tab:: 中文

    .. warning::

        Pydantic 的数据类层与 SQLAlchemy 的类检测 **不完全兼容**，需要额外的内部更改，许多功能（如相关集合）可能无法正常工作。

        对于 Pydantic 兼容性，请考虑 `SQLModel <https://sqlmodel.tiangolo.com>`_ ORM，它是基于 SQLAlchemy ORM 构建的 Pydantic，包含专门的实现细节， **明确解决** 了这些不兼容性。

    SQLAlchemy 的 :class:`_orm.MappedAsDataclass` 类和 :meth:`_orm.registry.mapped_as_dataclass` 方法在对类应用声明式映射过程后，直接调用 Python 标准库 ``dataclasses.dataclass`` 类装饰器。可以使用 :class:`_orm.MappedAsDataclass` 作为类关键字参数以及 :meth:`_orm.registry.mapped_as_dataclass` 接受的 ``dataclass_callable`` 参数交换此函数调用，以替代其他数据类提供者，例如 Pydantic 的数据类::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass
        from sqlalchemy.orm import registry


        class Base(
            MappedAsDataclass,
            DeclarativeBase,
            dataclass_callable=pydantic.dataclasses.dataclass,
        ):
            pass


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    上述 ``User`` 类将被应用为数据类，使用 Pydantic 的 ``pydantic.dataclasses.dataclasses`` 可调用对象。该过程适用于映射类以及从 :class:`_orm.MappedAsDataclass` 扩展的混入类或直接应用了 :meth:`_orm.registry.mapped_as_dataclass` 的类。

    .. versionadded:: 2.0.4 
        
        添加了 :class:`_orm.MappedAsDataclass` 和 :meth:`_orm.registry.mapped_as_dataclass` 的 ``dataclass_callable`` 类和方法参数，并调整了一些数据类内部结构以适应更严格的数据类函数，例如 Pydantic 的数据类。

.. tab:: 英文

    .. warning::

        The dataclass layer of Pydantic is **not fully compatible** with
        SQLAlchemy's class instrumentation without additional internal changes,
        and many features such as related collections may not work correctly.

        For Pydantic compatibility, please consider the
        `SQLModel <https://sqlmodel.tiangolo.com>`_ ORM which is built with
        Pydantic on top of SQLAlchemy ORM, which includes special implementation
        details which **explicitly resolve** these incompatibilities.

    SQLAlchemy's :class:`_orm.MappedAsDataclass` class
    and :meth:`_orm.registry.mapped_as_dataclass` method call directly into
    the Python standard library ``dataclasses.dataclass`` class decorator, after
    the declarative mapping process has been applied to the class.  This
    function call may be swapped out for alternateive dataclasses providers,
    such as that of Pydantic, using the ``dataclass_callable`` parameter
    accepted by :class:`_orm.MappedAsDataclass` as a class keyword argument
    as well as by :meth:`_orm.registry.mapped_as_dataclass`::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import MappedAsDataclass
        from sqlalchemy.orm import registry


        class Base(
            MappedAsDataclass,
            DeclarativeBase,
            dataclass_callable=pydantic.dataclasses.dataclass,
        ):
            pass


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]

    The above ``User`` class will be applied as a dataclass, using Pydantic's
    ``pydantic.dataclasses.dataclasses`` callable.     The process is available
    both for mapped classes as well as mixins that extend from
    :class:`_orm.MappedAsDataclass` or which have
    :meth:`_orm.registry.mapped_as_dataclass` applied directly.

    .. versionadded:: 2.0.4 
        
        Added the ``dataclass_callable`` class and method parameters for :class:`_orm.MappedAsDataclass` and :meth:`_orm.registry.mapped_as_dataclass`, and adjusted some of the dataclass internals to accommodate more strict dataclass functions such as that of Pydantic.


.. _orm_declarative_dataclasses:

将 ORM 映射应用于现有数据类（旧式数据类使用）
---------------------------------------------------------------------

Applying ORM Mappings to an existing dataclass (legacy dataclass use)

.. tab:: 中文

    .. legacy::

    此处描述的方法已被 2.0 系列 SQLAlchemy 中的新特性 :ref:`orm_declarative_native_dataclasses` 取代。此新版本功能建立在 1.4 版本中首次添加的数据类支持之上，本节描述了该支持。

    要映射现有的数据类，SQLAlchemy 的“内联”声明性指令不能直接使用；ORM 指令使用以下三种技术之一进行分配：

    * 使用“声明性与命令性表(Declarative with Imperative Table)”定义要映射的表/列，使用分配给类的 ``__table__`` 属性的 :class:`_schema.Table` 对象；关系在 ``__mapper_args__`` 字典内定义。类使用 :meth:`_orm.registry.mapped` 装饰器映射。示例如下：:ref:`orm_declarative_dataclasses_imperative_table`。

    * 使用完整的“声明性(Declarative)”，声明性解释的指令如 :class:`_schema.Column`、:func:`_orm.relationship` 被添加到 ``dataclasses.field()`` 结构的 ``.metadata`` 字典中，由声明性过程使用。类再次使用 :meth:`_orm.registry.mapped` 装饰器映射。参见下面的示例：:ref:`orm_declarative_dataclasses_declarative_table`。

    * 可以使用 :meth:`_orm.registry.map_imperatively` 方法将“命令性(Imperative)”映射应用于现有数据类，以完全相同的方式生成映射，如 :ref:`orm_imperative_mapping` 中描述。如下面的示例所示：:ref:`orm_imperative_dataclasses`。

    SQLAlchemy 将映射应用于数据类的总体过程与普通类相同，但还包括 SQLAlchemy 将检测在数据类声明过程中作为类级属性的属性，并在运行时将其替换为通常的 SQLAlchemy ORM 映射属性。dataclasses 生成的 ``__init__`` 方法保持不变，dataclasses 生成的所有其他方法如 ``__eq__()``、 ``__repr__()`` 等也是如此。

.. tab:: 英文

    .. legacy::

        The approaches described here are superseded by the :ref:`orm_declarative_native_dataclasses` feature new in the 2.0 series of SQLAlchemy.  This newer version of the feature builds upon the dataclass support first added in version 1.4, which is described in this section.

    To map an existing dataclass, SQLAlchemy's "inline" declarative directives
    cannot be used directly; ORM directives are assigned using one of three
    techniques:

    * Using "Declarative with Imperative Table", the table / column to be mapped is defined using a :class:`_schema.Table` object assigned to the ``__table__`` attribute of the class; relationships are defined within ``__mapper_args__`` dictionary.  The class is mapped using the :meth:`_orm.registry.mapped` decorator.   An example is below at :ref:`orm_declarative_dataclasses_imperative_table`.

    * Using full "Declarative", the Declarative-interpreted directives such as :class:`_schema.Column`, :func:`_orm.relationship` are added to the ``.metadata`` dictionary of the ``dataclasses.field()`` construct, where they are consumed by the declarative process.  The class is again mapped using the :meth:`_orm.registry.mapped` decorator.  See the example below at :ref:`orm_declarative_dataclasses_declarative_table`.

    * An "Imperative" mapping can be applied to an existing dataclass using the :meth:`_orm.registry.map_imperatively` method to produce the mapping in exactly the same way as described at :ref:`orm_imperative_mapping`. This is illustrated below at :ref:`orm_imperative_dataclasses`.

    The general process by which SQLAlchemy applies mappings to a dataclass
    is the same as that of an ordinary class, but also includes that
    SQLAlchemy will detect class-level attributes that were part of the
    dataclasses declaration process and replace them at runtime with
    the usual SQLAlchemy ORM mapped attributes.   The ``__init__`` method that
    would have been generated by dataclasses is left intact, as is the same
    for all the other methods that dataclasses generates such as
    ``__eq__()``, ``__repr__()``, etc.

.. _orm_declarative_dataclasses_imperative_table:

使用声明式和命令式表映射预先存在的数据类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mapping pre-existing dataclasses using Declarative With Imperative Table

.. tab:: 中文

    下面是一个使用 ``@dataclass`` 和 :ref:`orm_imperative_table_configuration` 的映射示例。一个完整的 :class:`_schema.Table` 对象被显式构建并分配给 ``__table__`` 属性。实例字段使用正常的数据类语法定义。其他 :class:`.MapperProperty` 定义，例如 :func:`.relationship`，放置在类级字典 :ref:`__mapper_args__ <orm_declarative_mapper_options>` 下的 ``properties`` 键中，对应于 :paramref:`_orm.Mapper.properties` 参数::

        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import List, Optional

        from sqlalchemy import Column, ForeignKey, Integer, String, Table
        from sqlalchemy.orm import registry, relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        @dataclass
        class User:
            __table__ = Table(
                "user",
                mapper_registry.metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String(50)),
                Column("fullname", String(50)),
                Column("nickname", String(12)),
            )
            id: int = field(init=False)
            name: Optional[str] = None
            fullname: Optional[str] = None
            nickname: Optional[str] = None
            addresses: List[Address] = field(default_factory=list)

            __mapper_args__ = {  # type: ignore
                "properties": {
                    "addresses": relationship("Address"),
                }
            }


        @mapper_registry.mapped
        @dataclass
        class Address:
            __table__ = Table(
                "address",
                mapper_registry.metadata,
                Column("id", Integer, primary_key=True),
                Column("user_id", Integer, ForeignKey("user.id")),
                Column("email_address", String(50)),
            )
            id: int = field(init=False)
            user_id: int = field(init=False)
            email_address: Optional[str] = None

    在上述示例中， ``User.id``、 ``Address.id`` 和 ``Address.user_id`` 属性被定义为 ``field(init=False)``。这意味着这些参数不会被添加到 ``__init__()`` 方法中，但 :class:`.Session` 在从自增或其他默认值生成器刷新值后仍然能够设置它们。为了允许在构造函数中显式指定它们，它们将被赋予 ``None`` 的默认值。

    要单独声明 :func:`_orm.relationship`，需要直接在 :paramref:`_orm.Mapper.properties` 字典中指定，该字典本身在 ``__mapper_args__`` 字典中指定，以便传递给 :class:`_orm.Mapper` 的构造函数。此方法的替代方法在下一个示例中。

    .. warning::
        
        声明一个数据类 ``field()`` 设置 ``default`` 与 ``init=False`` 一起使用时，将不会如纯数据类那样工作，因为 SQLAlchemy 类检测将替换数据类创建过程在类上设置的默认值。请改用 ``default_factory``。在使用 :ref:`orm_declarative_native_dataclasses` 时会自动进行此调整。

.. tab:: 英文

    An example of a mapping using ``@dataclass`` using
    :ref:`orm_imperative_table_configuration` is below. A complete
    :class:`_schema.Table` object is constructed explicitly and assigned to the
    ``__table__`` attribute. Instance fields are defined using normal dataclass
    syntaxes. Additional :class:`.MapperProperty`
    definitions such as :func:`.relationship`, are placed in the
    :ref:`__mapper_args__ <orm_declarative_mapper_options>` class-level
    dictionary underneath the ``properties`` key, corresponding to the
    :paramref:`_orm.Mapper.properties` parameter::

        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import List, Optional

        from sqlalchemy import Column, ForeignKey, Integer, String, Table
        from sqlalchemy.orm import registry, relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        @dataclass
        class User:
            __table__ = Table(
                "user",
                mapper_registry.metadata,
                Column("id", Integer, primary_key=True),
                Column("name", String(50)),
                Column("fullname", String(50)),
                Column("nickname", String(12)),
            )
            id: int = field(init=False)
            name: Optional[str] = None
            fullname: Optional[str] = None
            nickname: Optional[str] = None
            addresses: List[Address] = field(default_factory=list)

            __mapper_args__ = {  # type: ignore
                "properties": {
                    "addresses": relationship("Address"),
                }
            }


        @mapper_registry.mapped
        @dataclass
        class Address:
            __table__ = Table(
                "address",
                mapper_registry.metadata,
                Column("id", Integer, primary_key=True),
                Column("user_id", Integer, ForeignKey("user.id")),
                Column("email_address", String(50)),
            )
            id: int = field(init=False)
            user_id: int = field(init=False)
            email_address: Optional[str] = None

    In the above example, the ``User.id``, ``Address.id``, and ``Address.user_id``
    attributes are defined as ``field(init=False)``. This means that parameters for
    these won't be added to ``__init__()`` methods, but
    :class:`.Session` will still be able to set them after getting their values
    during flush from autoincrement or other default value generator.   To
    allow them to be specified in the constructor explicitly, they would instead
    be given a default value of ``None``.

    For a :func:`_orm.relationship` to be declared separately, it needs to be
    specified directly within the :paramref:`_orm.Mapper.properties` dictionary
    which itself is specified within the ``__mapper_args__`` dictionary, so that it
    is passed to the constructor for :class:`_orm.Mapper`. An alternative to this
    approach is in the next example.


    .. warning::
        
        Declaring a dataclass ``field()`` setting a ``default`` together with ``init=False``
        will not work as would be expected with a totally plain dataclass,
        since the SQLAlchemy class instrumentation will replace
        the default value set on the class by the dataclass creation process.
        Use ``default_factory`` instead. This adaptation is done automatically when
        making use of :ref:`orm_declarative_native_dataclasses`.

.. _orm_declarative_dataclasses_declarative_table:

使用声明式样式字段映射预先存在的数据类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mapping pre-existing dataclasses using Declarative-style fields

.. tab:: 中文

    .. legacy:: 
        
        此声明数据类映射方法应被视为遗留方法。它将继续受支持，但与 :ref:`orm_declarative_native_dataclasses` 中详细介绍的新方法相比，不太可能提供任何优势。

    请注意， **mapped_column() 不支持此用法**；
    应继续使用 :class:`_schema.Column` 结构在 ``dataclasses.field()`` 的 ``metadata`` 字段中声明表元数据。

    完全声明性方法要求将 :class:`_schema.Column` 对象声明为类属性，而使用数据类时会与数据类级属性冲突。将两者结合在一起的方法是使用 ``dataclass.field`` 对象上的 ``metadata`` 属性，其中可以提供特定于 SQLAlchemy 的映射信息。当类指定属性 ``__sa_dataclass_metadata_key__`` 时，声明性支持提取这些参数。这还提供了一种更简洁的方法来表示 :func:`_orm.relationship` 关联::

        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import List

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import registry, relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        @dataclass
        class User:
            __tablename__ = "user"

            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            name: str = field(default=None, metadata={"sa": Column(String(50))})
            fullname: str = field(default=None, metadata={"sa": Column(String(50))})
            nickname: str = field(default=None, metadata={"sa": Column(String(12))})
            addresses: List[Address] = field(
                default_factory=list, metadata={"sa": relationship("Address")}
            )


        @mapper_registry.mapped
        @dataclass
        class Address:
            __tablename__ = "address"
            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            user_id: int = field(init=False, metadata={"sa": Column(ForeignKey("user.id"))})
            email_address: str = field(default=None, metadata={"sa": Column(String(50))})

.. tab:: 英文

    .. legacy:: 
        
        This approach to Declarative mapping with dataclasses should be considered as legacy.  It will remain supported however is unlikely to offer any advantages against the new approach detailed at :ref:`orm_declarative_native_dataclasses`.

        Note that **mapped_column() is not supported with this use**; the :class:`_schema.Column` construct should continue to be used to declare table metadata within the ``metadata`` field of ``dataclasses.field()``.

    The fully declarative approach requires that :class:`_schema.Column` objects
    are declared as class attributes, which when using dataclasses would conflict
    with the dataclass-level attributes.  An approach to combine these together
    is to make use of the ``metadata`` attribute on the ``dataclass.field``
    object, where SQLAlchemy-specific mapping information may be supplied.
    Declarative supports extraction of these parameters when the class
    specifies the attribute ``__sa_dataclass_metadata_key__``.  This also
    provides a more succinct method of indicating the :func:`_orm.relationship`
    association::


        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import List

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import registry, relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        @dataclass
        class User:
            __tablename__ = "user"

            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            name: str = field(default=None, metadata={"sa": Column(String(50))})
            fullname: str = field(default=None, metadata={"sa": Column(String(50))})
            nickname: str = field(default=None, metadata={"sa": Column(String(12))})
            addresses: List[Address] = field(
                default_factory=list, metadata={"sa": relationship("Address")}
            )


        @mapper_registry.mapped
        @dataclass
        class Address:
            __tablename__ = "address"
            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            user_id: int = field(init=False, metadata={"sa": Column(ForeignKey("user.id"))})
            email_address: str = field(default=None, metadata={"sa": Column(String(50))})

.. _orm_declarative_dataclasses_mixin:

将声明式混合与预先存在的数据类结合使用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Declarative Mixins with pre-existing dataclasses

.. tab:: 中文

    在 :ref:`orm_mixins_toplevel` 部分中，引入了声明性 Mixin 类。声明性 mixin 的一个要求是，某些无法轻松复制的结构必须使用 :class:`_orm.declared_attr` 装饰器以可调用方式提供，例如在 :ref:`orm_declarative_mixins_relationships` 示例中::

        class RefTargetMixin:
            @declared_attr
            def target_id(cls) -> Mapped[int]:
                return mapped_column("target_id", ForeignKey("target.id"))

            @declared_attr
            def target(cls):
                return relationship("Target")

    在 Dataclasses ``field()`` 对象中，通过使用 lambda 表示 ``field()`` 内的 SQLAlchemy 结构来支持此形式。使用 :func:`_orm.declared_attr` 包围 lambda 是可选的。如果我们想生成上述 ORM 字段来自 mixin 且 mixin 本身为数据类的 ``User`` 类，形式如下::

        @dataclass
        class UserMixin:
            __tablename__ = "user"

            __sa_dataclass_metadata_key__ = "sa"

            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})

            addresses: List[Address] = field(
                default_factory=list, metadata={"sa": lambda: relationship("Address")}
            )


        @dataclass
        class AddressMixin:
            __tablename__ = "address"
            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            user_id: int = field(
                init=False, metadata={"sa": lambda: Column(ForeignKey("user.id"))}
            )
            email_address: str = field(default=None, metadata={"sa": Column(String(50))})


        @mapper_registry.mapped
        class User(UserMixin):
            pass


        @mapper_registry.mapped
        class Address(AddressMixin):
            pass

    .. versionadded:: 1.4.2  
        
        添加对“声明属性(declared attr)”风格的 mixin 属性的支持，即 :func:`_orm.relationship` 结构以及带有外键声明的 :class:`_schema.Column` 对象，以用于“带声明表的数据类(Dataclasses with Declarative Table)”样式映射中。

.. tab:: 英文

    In the section :ref:`orm_mixins_toplevel`, Declarative Mixin classes
    are introduced.  One requirement of declarative mixins is that certain
    constructs that can't be easily duplicated must be given as callables,
    using the :class:`_orm.declared_attr` decorator, such as in the
    example at :ref:`orm_declarative_mixins_relationships`::

        class RefTargetMixin:
            @declared_attr
            def target_id(cls) -> Mapped[int]:
                return mapped_column("target_id", ForeignKey("target.id"))

            @declared_attr
            def target(cls):
                return relationship("Target")

    This form is supported within the Dataclasses ``field()`` object by using
    a lambda to indicate the SQLAlchemy construct inside the ``field()``.
    Using :func:`_orm.declared_attr` to surround the lambda is optional.
    If we wanted to produce our ``User`` class above where the ORM fields
    came from a mixin that is itself a dataclass, the form would be::

        @dataclass
        class UserMixin:
            __tablename__ = "user"

            __sa_dataclass_metadata_key__ = "sa"

            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})

            addresses: List[Address] = field(
                default_factory=list, metadata={"sa": lambda: relationship("Address")}
            )


        @dataclass
        class AddressMixin:
            __tablename__ = "address"
            __sa_dataclass_metadata_key__ = "sa"
            id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})
            user_id: int = field(
                init=False, metadata={"sa": lambda: Column(ForeignKey("user.id"))}
            )
            email_address: str = field(default=None, metadata={"sa": Column(String(50))})


        @mapper_registry.mapped
        class User(UserMixin):
            pass


        @mapper_registry.mapped
        class Address(AddressMixin):
            pass

    .. versionadded:: 1.4.2  
        
        Added support for "declared attr" style mixin attributes, namely :func:`_orm.relationship` constructs as well as :class:`_schema.Column` objects with foreign key declarations, to be used within "Dataclasses with Declarative Table" style mappings.



.. _orm_imperative_dataclasses:

使用命令式映射映射预先存在的数据类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mapping pre-existing dataclasses using Imperative Mapping

.. tab:: 中文

    如前所述，使用 ``@dataclass`` 装饰器设置为数据类的类可以进一步使用 :meth:`_orm.registry.mapped` 装饰器进行装饰，以便将声明式样式映射应用于该类。作为使用 :meth:`_orm.registry.mapped` 装饰器的替代方法，我们还可以通过 :meth:`_orm.registry.map_imperatively` 方法传递该类，从而可以将所有 :class:`_schema.Table` 和 :class:`_orm.Mapper` 配置命令式传递给函数，而不是将它们作为类变量定义在类本身上::

        from __future__ import annotations

        from dataclasses import dataclass
        from dataclasses import field
        from typing import List

        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import MetaData
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @dataclass
        class User:
            id: int = field(init=False)
            name: str = None
            fullname: str = None
            nickname: str = None
            addresses: List[Address] = field(default_factory=list)


        @dataclass
        class Address:
            id: int = field(init=False)
            user_id: int = field(init=False)
            email_address: str = None


        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("fullname", String(50)),
            Column("nickname", String(12)),
        )

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
                "addresses": relationship(Address, backref="user", order_by=address.c.id),
            },
        )

        mapper_registry.map_imperatively(Address, address)

    与使用此映射样式时，:ref:`orm_declarative_dataclasses_imperative_table` 中提到的相同警告适用。

.. tab:: 英文

    As described previously, a class which is set up as a dataclass using the
    ``@dataclass`` decorator can then be further decorated using the
    :meth:`_orm.registry.mapped` decorator in order to apply declarative-style
    mapping to the class. As an alternative to using the
    :meth:`_orm.registry.mapped` decorator, we may also pass the class through the
    :meth:`_orm.registry.map_imperatively` method instead, so that we may pass all
    :class:`_schema.Table` and :class:`_orm.Mapper` configuration imperatively to
    the function rather than having them defined on the class itself as class
    variables::

        from __future__ import annotations

        from dataclasses import dataclass
        from dataclasses import field
        from typing import List

        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import MetaData
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @dataclass
        class User:
            id: int = field(init=False)
            name: str = None
            fullname: str = None
            nickname: str = None
            addresses: List[Address] = field(default_factory=list)


        @dataclass
        class Address:
            id: int = field(init=False)
            user_id: int = field(init=False)
            email_address: str = None


        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("fullname", String(50)),
            Column("nickname", String(12)),
        )

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
                "addresses": relationship(Address, backref="user", order_by=address.c.id),
            },
        )

        mapper_registry.map_imperatively(Address, address)

    The same warning mentioned in :ref:`orm_declarative_dataclasses_imperative_table`
    applies when using this mapping style.

.. _orm_declarative_attrs_imperative_table:

将 ORM 映射应用于现有属性类
-------------------------------------------------

Applying ORM mappings to an existing attrs class

.. tab:: 中文

    .. warning:: 
        
        ``attrs`` 库不是 SQLAlchemy 的持续集成测试的一部分，由于任何一方引入的不兼容性，可能会在没有通知的情况下更改与该库的兼容性。

    attrs_ 库是一个流行的第三方库，提供与数据类相似的功能，并提供许多普通数据类中没有的额外功能。

    使用 attrs_ 增强的类使用 ``@define`` 装饰器。此装饰器启动一个过程，扫描定义类行为的类属性，然后用于生成方法、文档和注释。

    SQLAlchemy ORM 支持使用 **命令式** 映射映射 attrs_ 类。这种风格的通用形式等同于使用数据类的 :ref:`orm_imperative_dataclasses` 映射形式，其中类构造仅使用 ``attrs``，ORM 映射在类构造之后应用，而不进行任何类属性扫描。

    attrs_ 的 ``@define`` 装饰器默认情况下会用一个新的基于 __slots__ 的类替换注解类，这是不支持的。使用旧样式注解 ``@attr.s`` 或使用 ``define(slots=False)`` 时，类不会被替换。此外， ``attrs`` 在装饰器运行后会删除其自己的类绑定属性，以便 SQLAlchemy 的映射过程可以接管这些属性而不会出现任何问题。这两个装饰器 ``@attr.s`` 和 ``@define(slots=False)`` 均适用于 SQLAlchemy。

    .. versionchanged:: 2.0  
        
        SQLAlchemy 与 ``attrs`` 的集成仅适用于命令式映射风格，即不使用声明性。引入的 ORM 注解声明风格与 ``attrs`` 不兼容。

    首先构建 ``attrs`` 类。SQLAlchemy ORM 映射可以在之后应用，使用 :meth:`_orm.registry.map_imperatively`::

        from __future__ import annotations

        from typing import List

        from attrs import define
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import MetaData
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @define(slots=False)
        class User:
            id: int
            name: str
            fullname: str
            nickname: str
            addresses: List[Address]


        @define(slots=False)
        class Address:
            id: int
            user_id: int
            email_address: Optional[str]


        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("fullname", String(50)),
            Column("nickname", String(12)),
        )

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
                "addresses": relationship(Address, backref="user", order_by=address.c.id),
            },
        )

        mapper_registry.map_imperatively(Address, address)

.. tab:: 英文

    .. warning:: 
        
        The ``attrs`` library is not part of SQLAlchemy's continuous integration testing, and compatibility with this library may change without notice due to incompatibilities introduced by either side.


    The attrs_ library is a popular third party library that provides similar
    features as dataclasses, with many additional features provided not
    found in ordinary dataclasses.

    A class augmented with attrs_ uses the ``@define`` decorator. This decorator
    initiates a process to scan the class for attributes that define the class'
    behavior, which are then used to generate methods, documentation, and
    annotations.

    The SQLAlchemy ORM supports mapping an attrs_ class using **Imperative** mapping.
    The general form of this style is equivalent to the
    :ref:`orm_imperative_dataclasses` mapping form used with
    dataclasses, where the class construction uses ``attrs`` alone, with ORM mappings
    applied after the fact without any class attribute scanning.

    The ``@define`` decorator of attrs_ by default replaces the annotated class
    with a new __slots__ based class, which is not supported. When using the old
    style annotation ``@attr.s`` or using ``define(slots=False)``, the class
    does not get replaced. Furthermore ``attrs`` removes its own class-bound attributes
    after the decorator runs, so that SQLAlchemy's mapping process takes over these
    attributes without any issue. Both decorators, ``@attr.s`` and ``@define(slots=False)``
    work with SQLAlchemy.

    .. versionchanged:: 2.0  
        
        SQLAlchemy integration with ``attrs`` works only with imperative mapping style, that is, not using Declarative. The introduction of ORM Annotated Declarative style is not cross-compatible with ``attrs``.

    The ``attrs`` class is built first.  The SQLAlchemy ORM mapping can be
    applied after the fact using :meth:`_orm.registry.map_imperatively`::

        from __future__ import annotations

        from typing import List

        from attrs import define
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import MetaData
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @define(slots=False)
        class User:
            id: int
            name: str
            fullname: str
            nickname: str
            addresses: List[Address]


        @define(slots=False)
        class Address:
            id: int
            user_id: int
            email_address: Optional[str]


        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("fullname", String(50)),
            Column("nickname", String(12)),
        )

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
                "addresses": relationship(Address, backref="user", order_by=address.c.id),
            },
        )

        mapper_registry.map_imperatively(Address, address)

.. _dataclass: https://docs.python.org/3/library/dataclasses.html
.. _dataclasses: https://docs.python.org/3/library/dataclasses.html
.. _attrs: https://pypi.org/project/attrs/
.. _mypy: https://mypy.readthedocs.io/en/stable/
.. _pyright: https://github.com/microsoft/pyright
