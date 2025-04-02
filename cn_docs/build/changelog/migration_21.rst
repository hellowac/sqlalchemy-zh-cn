.. _whatsnew_21_toplevel:

=============================
SQLAlchemy 2.1 有什么新功能？
=============================

What's New in SQLAlchemy 2.1?

.. tab:: 中文

    .. admonition:: 关于此文档

        本文档描述了 SQLAlchemy 2.0 版和 2.1 版之间的变化。

.. tab:: 英文

    .. admonition:: About this Document

        This document describes changes between SQLAlchemy version 2.0 and
        version 2.1.


.. _change_10635:

``Row`` 现在直接表示单个列类型，无需 ``Tuple``
--------------------------------------------------------------------------

``Row`` now represents individual column types directly without ``Tuple``

.. tab:: 中文

    SQLAlchemy 2.0 在所有组件中实现了广泛的 :pep:`484` 类型，包括新的功能，即行返回语句（如 :func:`_sql.select`）能够跟踪各个列的类型，然后将其传递到执行阶段，再传递到 :class:`_engine.Result` 对象，然后传递到各个 :class:`_engine.Row` 对象。在 :ref:`change_result_typing_20` 中描述，这种方法解决了语句 / 行类型的几个问题，但有些问题仍然无法解决。在 2.1 中，其中一个问题，即各个列类型需要打包成一个 ``typing.Tuple``，现在通过新的 :pep:`646` 集成解决了，这允许类似元组的类型实际上不被类型化为 ``Tuple``。

    在 SQLAlchemy 2.0 中，类似于以下的语句::

        stmt = select(column("x", Integer), column("y", String))

    将被类型化为::

        Select[Tuple[int, str]]

    在 2.1 中，现在被类型化为::

        Select[int, str]

    执行 ``stmt`` 时，:class:`_engine.Result` 和 :class:`_engine.Row` 对象将分别被类型化为 ``Result[int, str]`` 和 ``Row[int, str]``。不再需要使用 :attr:`_engine.Row._t` 将其类型化为真正的 ``Tuple``，项目可以迁移离开这种模式。

    Mypy 用户需要使用 **Mypy 1.7 或更高版本** 才能使用 pep-646 集成。

.. tab:: 英文

    SQLAlchemy 2.0 implemented a broad array of :pep:`484` typing throughout
    all components, including a new ability for row-returning statements such
    as :func:`_sql.select` to maintain track of individual column types, which
    were then passed through the execution phase onto the :class:`_engine.Result`
    object and then to the individual :class:`_engine.Row` objects.   Described
    at :ref:`change_result_typing_20`, this approach solved several issues
    with statement / row typing, but some remained unsolvable.  In 2.1, one
    of those issues, that the individual column types needed to be packaged
    into a ``typing.Tuple``, is now resolved using new :pep:`646` integration,
    which allows for tuple-like types that are not actually typed as ``Tuple``.

    In SQLAlchemy 2.0, a statement such as::

        stmt = select(column("x", Integer), column("y", String))

    Would be typed as::

        Select[Tuple[int, str]]

    In 2.1, it's now typed as::

        Select[int, str]

    When executing ``stmt``, the :class:`_engine.Result` and :class:`_engine.Row`
    objects will be typed as ``Result[int, str]`` and ``Row[int, str]``, respectively.
    The prior workaround using :attr:`_engine.Row._t` to type as a real ``Tuple``
    is no longer needed and projects can migrate off this pattern.

    Mypy users will need to make use of **Mypy 1.7 or greater** for pep-646
    integration to be available.

限制
^^^^^^^^^^^

Limitations

.. tab:: 中文

    尚未通过 pep-646 或任何其他 pep 解决的问题是，将 :class:`_sql.Select` 等类中的任意数量的表达式映射到行对象，而无需在类型注释中明确说明每个参数的位置。为了解决这个问题，SQLAlchemy 使用自动 "stub 生成" 工具来生成不同数量的位置参数到类似 :func:`_sql.select` 的构造的硬编码映射，以解析为单个 ``Unpack[]`` 表达式（在 SQLAlchemy 2.0 中，这种生成产生了 ``Tuple[]`` 注释）。这意味着在 :class:`_engine.Row` 对象中将有任意数量的特定列表达式进行类型化，而不会将剩余表达式恢复为 ``Any``；对于 :func:`_sql.select`，当前是十个表达式，对于使用 :meth:`_dml.Insert.returning` 的 DML 表达式（如 :func:`_dml.insert`），是八个表达式。如果提出了一个提供 ``Map`` 操作符给 pep-646 的新 pep，这个限制可以被解除。[1]_ 最初，错误地认为这个限制完全阻止了 pep-646 的使用，然而，``Unpack`` 构造实际上取代了在 2.0 中使用 ``Tuple`` 所做的一切。

    一个额外的限制是没有提出解决方案，即 :class:`_engine.Row` 上的基于名称的属性无法自动进行类型化，因此这些属性继续被类型化为 ``Any`` （例如，对于上述示例中的 ``row.x`` 和 ``row.y``）。使用当前的语言特性，这只能通过一个显式的基于类的构造来解决，该构造允许在前面组合一个具有显式字段的显式 :class:`_engine.Row`，这将是冗长且非自动的。

.. tab:: 英文

    Not yet solved by pep-646 or any other pep is the ability for an arbitrary
    number of expressions within :class:`_sql.Select` and others to be mapped to
    row objects, without stating each argument position explicitly within typing
    annotations.   To work around this issue, SQLAlchemy makes use of automated
    "stub generation" tools to generate hardcoded mappings of different numbers of
    positional arguments to constructs like :func:`_sql.select` to resolve to
    individual ``Unpack[]`` expressions (in SQLAlchemy 2.0, this generation
    produced ``Tuple[]`` annotations instead).  This means that there are arbitrary
    limits on how many specific column expressions will be typed within the
    :class:`_engine.Row` object, without restoring to ``Any`` for remaining
    expressions; for :func:`_sql.select`, it's currently ten expressions, and
    for DML expressions like :func:`_dml.insert` that use :meth:`_dml.Insert.returning`,
    it's eight.    If and when a new pep that provides a ``Map`` operator
    to pep-646 is proposed, this limitation can be lifted. [1]_  Originally, it was
    mistakenly assumed that this limitation prevented pep-646 from being usable at all,
    however, the ``Unpack`` construct does in fact replace everything that
    was done using ``Tuple`` in 2.0.

    An additional limitation for which there is no proposed solution is that
    there's no way for the name-based attributes on :class:`_engine.Row` to be
    automatically typed, so these continue to be typed as ``Any`` (e.g. ``row.x``
    and ``row.y`` for the above example).   With current language features,
    this could only be fixed by having an explicit class-based construct that
    allows one to compose an explicit :class:`_engine.Row` with explicit fields
    up front, which would be verbose and not automatic.

.. [1] https://github.com/python/typing/discussions/1001#discussioncomment-1897813

:ticket:`10635`


.. _change_10197:

Asyncio“greenlet”依赖项不再默认安装
------------------------------------------------------------

Asyncio "greenlet" dependency no longer installs by default

.. tab:: 中文

    SQLAlchemy 1.4 和 2.0 使用一个复杂的表达式来确定 ``greenlet`` 依赖项是否可以从 pypi 使用预构建的 wheel 安装，而不是从源代码构建。这是因为在某些平台上，从源代码构建 ``greenlet`` 并不总是简单的。

    这种方法的缺点包括：SQLAlchemy 需要准确跟踪在 pypi 上发布的 ``greenlet`` 版本；设置表达式导致了一些包管理工具（如 ``poetry``）的问题；即使不使用 asyncio 扩展，也无法 **不** 安装 ``greenlet``，尽管这完全可行。

    通过将 ``greenlet`` 完全放在 ``[asyncio]`` 目标中，这些问题都得到了解决。唯一的缺点是 asyncio 扩展的用户需要注意这个额外的安装依赖项。

.. tab:: 英文

    SQLAlchemy 1.4 and 2.0 used a complex expression to determine if the
    ``greenlet`` dependency, needed by the :ref:`asyncio <asyncio_toplevel>`
    extension, could be installed from pypi using a pre-built wheel instead
    of having to build from source.   This because the source build of ``greenlet``
    is not always trivial on some platforms.

    Disadvantages to this approach included that SQLAlchemy needed to track
    exactly which versions of ``greenlet`` were published as wheels on pypi;
    the setup expression led to problems with some package management tools
    such as ``poetry``; it was not possible to install SQLAlchemy **without**
    ``greenlet`` being installed, even though this is completely feasible
    if the asyncio extension is not used.

    These problems are all solved by keeping ``greenlet`` entirely within the
    ``[asyncio]`` target.  The only downside is that users of the asyncio extension
    need to be aware of this extra installation dependency.

:ticket:`10197`


.. _change_10050:

ORM 关系允许调用 back_populates
---------------------------------------------------

ORM Relationship allows callable for back_populates

.. tab:: 中文

    为了帮助生成更符合 IDE 级别的 linting 和类型检查的代码，:paramref:`_orm.relationship.back_populates` 参数现在接受直接引用类绑定属性以及执行相同操作的 lambdas::

        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)

            # 使用 lambda: 直接链接到 B.a
            bs: Mapped[list[B]] = relationship(back_populates=lambda: B.a)


        class B(Base):
            __tablename__ = "b"
            id: Mapped[int] = mapped_column(primary_key=True)
            a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))

            # A.bs 已经存在，因此可以直接链接
            a: Mapped[A] = relationship(back_populates=A.bs)

.. tab:: 英文

    To help produce code that is more amenable to IDE-level linting and type
    checking, the :paramref:`_orm.relationship.back_populates` parameter now
    accepts both direct references to a class-bound attribute as well as
    lambdas which do the same::

        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)

            # use a lambda: to link to B.a directly when it exists
            bs: Mapped[list[B]] = relationship(back_populates=lambda: B.a)


        class B(Base):
            __tablename__ = "b"
            id: Mapped[int] = mapped_column(primary_key=True)
            a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))

            # A.bs already exists, so can link directly
            a: Mapped[A] = relationship(back_populates=A.bs)

:ticket:`10050`

.. _change_12168:

ORM 映射数据类不再在 ``__dict__`` 中填充隐式 ``default``
------------------------------------------------------------------------------

ORM Mapped Dataclasses no longer populate implicit ``default`` in ``__dict__``

.. tab:: 中文

    此行为更改解决了在 2.0 版本中引入的 SQLAlchemy 的 :ref:`orm_declarative_native_dataclasses` 功能的广泛报告的问题。SQLAlchemy ORM 一直具有一种行为，即 ORM 映射类上的特定属性将具有不同的行为，具体取决于它是否具有已设置的值，包括该值是否为 ``None``，与该属性根本没有设置的情况不同。当引入声明数据类映射时，:paramref:`_orm.mapped_column.default` 参数引入了一种新功能，即在生成的 ``__init__`` 方法中设置数据类级别的默认值。这不幸地破坏了各种流行的工作流程，其中最突出的是使用外键值创建 ORM 对象来代替多对一引用::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class Parent(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

            related_id: Mapped[int | None] = mapped_column(ForeignKey("child.id"), default=None)
            related: Mapped[Child | None] = relationship(default=None)


        class Child(Base):
            __tablename__ = "child"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

    在上述映射中，为 ``Parent`` 生成的 ``__init__`` 方法在 Python 代码中看起来像这样::


        def __init__(self, related_id=None, related=None): ...

    这意味着仅使用 ``related_id`` 创建新的 ``Parent`` 将在 ``__dict__`` 中填充 ``related_id`` 和 ``related``::

        # 2.0 行为；由于存在 related=None，将为 related_id 插入 NULL
        >>> p1 = Parent(related_id=5)
        >>> p1.__dict__
        {'related_id': 5, 'related': None, '_sa_instance_state': ...}

    ``related`` 的 ``None`` 值意味着 SQLAlchemy 更倾向于不存在的相关 ``Child`` 而不是 ``related_id`` 的现有值，该值将被丢弃，并且将为 ``related_id`` 插入 ``NULL``。

    在新的行为中， ``__init__`` 方法如下例所示，使用一个特殊的常量 ``DONT_SET`` 表示应忽略 ``related`` 的不存在值。这使类的行为更接近于 SQLAlchemy ORM 映射类的传统操作方式::

        def __init__(self, related_id=DONT_SET, related=DONT_SET): ...

    然后我们得到一个 ``__dict__`` 设置，它将遵循预期的行为，省略 ``related`` 并稍后运行一个 INSERT，带有 ``related_id=5``::

        # 2.1 行为；将为 related_id 插入 5
        >>> p1 = Parent(related_id=5)
        >>> p1.__dict__
        {'related_id': 5, '_sa_instance_state': ...}

.. tab:: 英文

    This behavioral change addresses a widely reported issue with SQLAlchemy's
    :ref:`orm_declarative_native_dataclasses` feature that was introduced in 2.0.
    SQLAlchemy ORM has always featured a behavior where a particular attribute on
    an ORM mapped class will have different behaviors depending on if it has an
    actively set value, including if that value is ``None``, versus if the
    attribute is not set at all.  When Declarative Dataclass Mapping was introduced, the
    :paramref:`_orm.mapped_column.default` parameter introduced a new capability
    which is to set up a dataclass-level default to be present in the generated
    ``__init__`` method. This had the unfortunate side effect of breaking various
    popular workflows, the most prominent of which is creating an ORM object with
    the foreign key value in lieu of a many-to-one reference::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class Parent(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

            related_id: Mapped[int | None] = mapped_column(ForeignKey("child.id"), default=None)
            related: Mapped[Child | None] = relationship(default=None)


        class Child(Base):
            __tablename__ = "child"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

    In the above mapping, the ``__init__`` method generated for ``Parent``
    would in Python code look like this::


        def __init__(self, related_id=None, related=None): ...

    This means that creating a new ``Parent`` with ``related_id`` only would populate
    both ``related_id`` and ``related`` in ``__dict__``::

        # 2.0 behavior; will INSERT NULL for related_id due to the presence
        # of related=None
        >>> p1 = Parent(related_id=5)
        >>> p1.__dict__
        {'related_id': 5, 'related': None, '_sa_instance_state': ...}

    The ``None`` value for ``'related'`` means that SQLAlchemy favors the non-present
    related ``Child`` over the present value for ``'related_id'``, which would be
    discarded, and ``NULL`` would be inserted for ``'related_id'`` instead.

    In the new behavior, the ``__init__`` method instead looks like the example below,
    using a special constant ``DONT_SET`` indicating a non-present value for ``'related'``
    should be ignored.  This allows the class to behave more closely to how
    SQLAlchemy ORM mapped classes traditionally operate::

        def __init__(self, related_id=DONT_SET, related=DONT_SET): ...

    We then get a ``__dict__`` setup that will follow the expected behavior of
    omitting ``related`` from ``__dict__`` and later running an INSERT with
    ``related_id=5``::

        # 2.1 behavior; will INSERT 5 for related_id
        >>> p1 = Parent(related_id=5)
        >>> p1.__dict__
        {'related_id': 5, '_sa_instance_state': ...}

数据类默认值通过描述符而不是 __dict__ 传递
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dataclass defaults are delivered via descriptor instead of __dict__

.. tab:: 中文

    上述行为更进一步，即为了支持除 ``None`` 之外的默认值，数据类级别默认值（即使用 :paramref:`_orm.mapped_column.default`、:paramref:`_orm.column_property.default` 或 :paramref:`_orm.deferred.default` 参数设置的默认值）通过 SQLAlchemy 的属性系统中的机制在 Python :term:`descriptor` 级别传递，通常情况下这些机制会为未填充的列返回 ``None``，因此即使默认值未填充到 ``__dict__`` 中，当访问该属性时仍会传递默认值。这种行为基于 Python 数据类本身在为包含 ``init=False`` 的字段指示默认值时的操作。

    在下面的示例中，一个不可变默认值 ``"default_status"`` 被应用于名为 ``status`` 的列::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class SomeObject(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

            status: Mapped[str] = mapped_column(default="default_status")

    在上述映射中，不带参数构造 ``SomeObject`` 将不会在 ``__dict__`` 中传递任何值，但会通过描述符传递默认值::

        # 对象构造时没有 ``status`` 的值
        >>> s1 = SomeObject()

        # 默认值不会放在 ``__dict__`` 中
        >>> s1.__dict__
        {'_sa_instance_state': ...}

        # 但默认值通过描述符在对象级别传递
        >>> s1.status
        'default_status'

        # 值仍然未填充到 ``__dict__`` 中
        >>> s1.__dict__
        {'_sa_instance_state': ...}

    传递给 :paramref:`_orm.mapped_column.default` 的值也会像以前一样分配给底层 :class:`_schema.Column` 的 :paramref:`_schema.Column.default` 参数，在那里它作为 INSERT 语句的 Python 级默认值。因此，尽管 ``__dict__`` 中从未填充对象的默认值，但 INSERT 仍然在参数集中包含该值。这本质上修改了声明数据类映射系统，使其更像传统的 ORM 映射类，其中“默认值”仅表示列级默认值。

.. tab:: 英文

    The above behavior goes a step further, which is that in order to
    honor default values that are something other than ``None``, the value of the
    dataclass-level default (i.e. set using any of the
    :paramref:`_orm.mapped_column.default`,
    :paramref:`_orm.column_property.default`, or :paramref:`_orm.deferred.default`
    parameters) is directed to be delivered at the
    Python :term:`descriptor` level using mechanisms in SQLAlchemy's attribute
    system that normally return ``None`` for un-popualted columns, so that even though the default is not
    populated into ``__dict__``, it's still delivered when the attribute is
    accessed.  This behavior is based on what Python dataclasses itself does
    when a default is indicated for a field that also includes ``init=False``.

    In the example below, an immutable default ``"default_status"``
    is applied to a column called ``status``::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class SomeObject(Base):
            __tablename__ = "parent"

            id: Mapped[int] = mapped_column(primary_key=True, init=False)

            status: Mapped[str] = mapped_column(default="default_status")

    In the above mapping, constructing ``SomeObject`` with no parameters will
    deliver no values inside of ``__dict__``, but will deliver the default
    value via descriptor::

        # object is constructed with no value for ``status``
        >>> s1 = SomeObject()

        # the default value is not placed in ``__dict__``
        >>> s1.__dict__
        {'_sa_instance_state': ...}

        # but the default value is delivered at the object level via descriptor
        >>> s1.status
        'default_status'

        # the value still remains unpopulated in ``__dict__``
        >>> s1.__dict__
        {'_sa_instance_state': ...}

    The value passed
    as :paramref:`_orm.mapped_column.default` is also assigned as was the
    case before to the :paramref:`_schema.Column.default` parameter of the
    underlying :class:`_schema.Column`, where it takes
    place as a Python-level default for INSERT statements.  So while ``__dict__``
    is never populated with the default value on the object, the INSERT
    still includes the value in the parameter set.  This essentially modifies
    the Declarative Dataclass Mapping system to work more like traditional
    ORM mapped classes, where a "default" means just that, a column level
    default.

即使没有 init，也可以在对象上访问数据类默认值
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dataclass defaults are accessible on objects even without init

.. tab:: 中文

    由于新行为以类似于 Python 数据类在 ``init=False`` 时的方式使用描述符，因此新功能也实现了这种行为。这是一种全新的行为，其中 ORM 映射类可以为字段提供默认值，即使它们根本不是 ``__init__()`` 方法的一部分。在下面的映射中， ``status`` 字段配置为 ``init=False``，这意味着它根本不是构造函数的一部分::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class SomeObject(Base):
            __tablename__ = "parent"
            id: Mapped[int] = mapped_column(primary_key=True, init=False)
            status: Mapped[str] = mapped_column(default="default_status", init=False)

    当我们不带参数构造 ``SomeObject()`` 时，默认值可以通过描述符访问实例::

        >>> so = SomeObject()
        >>> so.status
        default_status

.. tab:: 英文


    As the new behavior makes use of descriptors in a similar way as Python
    dataclasses do themselves when ``init=False``, the new feature implements
    this behavior as well.   This is an all new behavior where an ORM mapped
    class can deliver a default value for fields even if they are not part of
    the ``__init__()`` method at all.  In the mapping below, the ``status``
    field is configured with ``init=False``, meaning it's not part of the
    constructor at all::

        class Base(MappedAsDataclass, DeclarativeBase):
            pass


        class SomeObject(Base):
            __tablename__ = "parent"
            id: Mapped[int] = mapped_column(primary_key=True, init=False)
            status: Mapped[str] = mapped_column(default="default_status", init=False)

    When we construct ``SomeObject()`` with no arguments, the default is accessible
    on the instance, delivered via descriptor::

        >>> so = SomeObject()
        >>> so.status
        default_status

相关更改
^^^^^^^^^^^^^^^

Related Changes

.. tab:: 中文

    此更改包括以下 API 变更：

    * 当存在 :paramref:`_orm.relationship.default` 参数时，仅接受值 ``None``，并且仅在关系最终是多对一关系或建立 :paramref:`_orm.relationship.uselist` 为 ``False`` 时才被接受。
    * :paramref:`_orm.mapped_column.default` 和 :paramref:`_orm.mapped_column.insert_default` 参数是互斥的，一次只能传递一个。这两个参数在 :class:`_schema.Column` 级别的行为是等效的，但在声明数据类映射级别，只有 :paramref:`_orm.mapped_column.default` 实际上通过描述符访问设置数据类级别的默认值；使用 :paramref:`_orm.mapped_column.insert_default` 将使对象属性在实例上默认值为 ``None``，直到插入发生，这与传统 ORM 映射类的工作方式相同。

.. tab:: 英文


    This change includes the following API changes:

    * The :paramref:`_orm.relationship.default` parameter, when present, only
      accepts a value of ``None``, and is only accepted when the relationship is
      ultimately a many-to-one relationship or one that establishes
      :paramref:`_orm.relationship.uselist` as ``False``.
    * The :paramref:`_orm.mapped_column.default` and :paramref:`_orm.mapped_column.insert_default`
      parameters are mutually exclusive, and only one may be passed at a time.
      The behavior of the two parameters is equivalent at the :class:`_schema.Column`
      level, however at the Declarative Dataclass Mapping level, only
      :paramref:`_orm.mapped_column.default` actually sets the dataclass-level
      default with descriptor access; using :paramref:`_orm.mapped_column.insert_default`
      will have the effect of the object attribute defaulting to ``None`` on the
      instance until the INSERT takes place, in the same way it works on traditional
      ORM mapped classes.

:ticket:`12168`


.. _change_11234:

URL stringify 和 parse 现在支持“数据库”部分的 URL 转义
----------------------------------------------------------------------------

URL stringify and parse now supports URL escaping for the "database" portion

.. tab:: 中文

    包含 URL 转义字符的数据库部分的 URL 现在将解析这些转义字符::

        >>> from sqlalchemy import make_url
        >>> u = make_url("driver://user:pass@host/database%3Fname")
        >>> u.database
        'database?name'

    以前，这些字符不会被解码::

        >>> # pre-2.1 行为
        >>> from sqlalchemy import make_url
        >>> u = make_url("driver://user:pass@host/database%3Fname")
        >>> u.database
        'database%3Fname'

    此更改也适用于字符串化部分；数据库名称中的大多数特殊字符将被 URL 转义，忽略一些如加号和斜杠的字符::

        >>> from sqlalchemy import URL
        >>> u = URL.create("driver", database="a?b=c")
        >>> str(u)
        'driver:///a%3Fb%3Dc'

    上述 URL 正确地回环到自身::

        >>> make_url(str(u))
        driver:///a%3Fb%3Dc
        >>> make_url(str(u)).database == u.database
        True

    以前，程序化应用的特殊字符不会在结果中被转义，导致 URL 不代表原始的数据库部分。下面，`b=c` 是查询字符串的一部分而不是数据库部分::

        >>> from sqlalchemy import URL
        >>> u = URL.create("driver", database="a?b=c")
        >>> str(u)
        'driver:///a?b=c'

.. tab:: 英文

    A URL that includes URL-escaped characters in the database portion will
    now parse with conversion of those escaped characters::

        >>> from sqlalchemy import make_url
        >>> u = make_url("driver://user:pass@host/database%3Fname")
        >>> u.database
        'database?name'

    Previously, such characters would not be unescaped::

        >>> # pre-2.1 behavior
        >>> from sqlalchemy import make_url
        >>> u = make_url("driver://user:pass@host/database%3Fname")
        >>> u.database
        'database%3Fname'

    This change also applies to the stringify side; most special characters in
    the database name will be URL escaped, omitting a few such as plus signs and
    slashes::

        >>> from sqlalchemy import URL
        >>> u = URL.create("driver", database="a?b=c")
        >>> str(u)
        'driver:///a%3Fb%3Dc'

    Where the above URL correctly round-trips to itself::

        >>> make_url(str(u))
        driver:///a%3Fb%3Dc
        >>> make_url(str(u)).database == u.database
        True


    Whereas previously, special characters applied programmatically would not
    be escaped in the result, leading to a URL that does not represent the
    original database portion.  Below, `b=c` is part of the query string and
    not the database portion::

        >>> from sqlalchemy import URL
        >>> u = URL.create("driver", database="a?b=c")
        >>> str(u)
        'driver:///a?b=c'

:ticket:`11234`

.. _change_11250:

对 mssql+pyodbc 的 odbc_connect= 处理的潜在重大更改
--------------------------------------------------------------------

Potential breaking change to odbc_connect= handling for mssql+pyodbc

.. tab:: 中文

    修复了一个 mssql+pyodbc 问题，其中在未引用的 ``odbc_connect=``（原始 DBAPI）连接字符串中有效的加号被替换为空格。

    之前，pyodbc 连接器总是将 odbc_connect 值传递给 unquote_plus()，即使不需要也是如此。因此，如果（未引用的）odbc_connect 值包含 ``PWD=pass+word``，它将被更改为 ``PWD=pass word``，并且登录将失败。一种解决方法是仅引用加号 — ``PWD=pass%2Bword`` — 然后它将被解码为 ``PWD=pass+word``。

    使用上述解决方法通过 :meth:`_engine.URL.create` 在 odbc_connect 字符串的 ``PWD=`` 参数中指定加号的实现将不得不移除解决方法，只需传递 ``PWD=`` 值，像在有效的 ODBC 连接字符串中一样出现（即，如果直接使用 ``pyodbc.connect()`` 连接字符串，则需要相同）。

.. tab:: 英文


    Fixed a mssql+pyodbc issue where valid plus signs in an already-unquoted
    ``odbc_connect=`` (raw DBAPI) connection string were replaced with spaces.

    Previously, the pyodbc connector would always pass the odbc_connect value
    to unquote_plus(), even if it was not required. So, if the (unquoted)
    odbc_connect value contained ``PWD=pass+word`` that would get changed to
    ``PWD=pass word``, and the login would fail. One workaround was to quote
    just the plus sign — ``PWD=pass%2Bword`` — which would then get unquoted
    to ``PWD=pass+word``.

    Implementations using the above workaround with :meth:`_engine.URL.create`
    to specify a plus sign in the ``PWD=`` argument of an odbc_connect string
    will have to remove the workaround and just pass the ``PWD=`` value as it
    would appear in a valid ODBC connection string (i.e., the same as would be
    required if using the connection string directly with ``pyodbc.connect()``).

:ticket:`11250`
