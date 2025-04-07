# ext/automap.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

r"""
.. tab:: 中文

    定义一个扩展 :mod:`sqlalchemy.ext.declarative` 系统
    ，该系统可以自动从数据库模式生成映射类和关系，通常但不一定是反射出来的。

    我们希望 :class:`.AutomapBase` 系统提供一个快速且现代化的解决方案，
    来解决著名的 `SQLSoup <https://pypi.org/project/sqlsoup/>`_
    也试图解决的问题，即动态地从现有数据库生成一个快速且基础的对象模型。
    通过严格从映射器配置层面解决这个问题，并与现有的声明式类技术完全集成， :class:`.AutomapBase`
    旨在为快速自动生成临时映射提供一个良好的集成方案。

    .. tip:: :ref:`automap_toplevel` 扩展旨在实现“零声明”方法，
       其中可以从数据库模式动态生成一个完整的 ORM 模型，包括类和预命名的关系。
       对于仍然希望结合表格反射使用显式类声明（包括显式关系定义）的应用，
       :class:`.DeferredReflection` 类（在 :ref:`orm_declarative_reflected_deferred_reflection` 中描述）是更好的选择。


.. tab:: 英文

    Define an extension to the :mod:`sqlalchemy.ext.declarative` system
    which automatically generates mapped classes and relationships from a database
    schema, typically though not necessarily one which is reflected.

    It is hoped that the :class:`.AutomapBase` system provides a quick
    and modernized solution to the problem that the very famous
    `SQLSoup <https://pypi.org/project/sqlsoup/>`_
    also tries to solve, that of generating a quick and rudimentary object
    model from an existing database on the fly.  By addressing the issue strictly
    at the mapper configuration level, and integrating fully with existing
    Declarative class techniques, :class:`.AutomapBase` seeks to provide
    a well-integrated approach to the issue of expediently auto-generating ad-hoc
    mappings.

    .. tip:: The :ref:`automap_toplevel` extension is geared towards a
       "zero declaration" approach, where a complete ORM model including classes
       and pre-named relationships can be generated on the fly from a database
       schema. For applications that still want to use explicit class declarations
       including explicit relationship definitions in conjunction with reflection
       of tables, the :class:`.DeferredReflection` class, described at
       :ref:`orm_declarative_reflected_deferred_reflection`, is a better choice.

.. _automap_basic_use:

基本用法
=========

Basic Use

.. tab:: 中文

    最简单的用法是将现有的数据库反射到一个新的模型中。
    我们通过类似于创建声明式基类的方式，创建一个新的 :class:`.AutomapBase` 类，使用 :func:`.automap_base`。
    然后，我们在结果基类上调用 :meth:`.AutomapBase.prepare` 方法，要求它反射模式并生成映射::

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy.orm import Session
        from sqlalchemy import create_engine

        Base = automap_base()

        # 假设 engine 已经设置了两个表 'user' 和 'address'
        engine = create_engine("sqlite:///mydatabase.db")

        # 反射表格
        Base.prepare(autoload_with=engine)

        # 映射类现在是通过表名自动生成的
        User = Base.classes.user
        Address = Base.classes.address

        session = Session(engine)

        # 基本的关系已生成
        session.add(Address(email_address="foo@bar.com", user=User(name="foo")))
        session.commit()

        # 基于集合的关系默认命名为
        # "<classname>_collection"
        u1 = session.query(User).first()
        print(u1.address_collection)

    在上面的例子中，调用 :meth:`.AutomapBase.prepare` 并传递 :paramref:`.AutomapBase.prepare.reflect` 参数，表示
    将调用此声明基类的 :class:`_schema.MetaData` 集合上的 :meth:`_schema.MetaData.reflect` 方法；
    然后，在 :class:`_schema.MetaData` 中的每个 **可用的** :class:`_schema.Table`
    都会自动生成一个新的映射类。 连接各个表的 :class:`_schema.ForeignKeyConstraint` 对象
    将用于生成类之间新的双向 :func:`_orm.relationship` 对象。
    类和关系遵循一个默认的命名方案，我们可以自定义该方案。 到此为止，
    我们基本的映射由相关的 ``User`` 和 ``Address`` 类组成，已准备好以传统方式使用。

    .. note:: **可用的** 表示一个表要被映射，必须指定主键。
       此外，如果检测到表是两个其他表之间的纯关联表，它将不会直接映射，
       而是作为两个引用表之间的多对多表进行配置。


.. tab:: 英文

    The simplest usage is to reflect an existing database into a new model.
    We create a new :class:`.AutomapBase` class in a similar manner as to how
    we create a declarative base class, using :func:`.automap_base`.
    We then call :meth:`.AutomapBase.prepare` on the resulting base class,
    asking it to reflect the schema and produce mappings::

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy.orm import Session
        from sqlalchemy import create_engine

        Base = automap_base()

        # engine, suppose it has two tables 'user' and 'address' set up
        engine = create_engine("sqlite:///mydatabase.db")

        # reflect the tables
        Base.prepare(autoload_with=engine)

        # mapped classes are now created with names by default
        # matching that of the table name.
        User = Base.classes.user
        Address = Base.classes.address

        session = Session(engine)

        # rudimentary relationships are produced
        session.add(Address(email_address="foo@bar.com", user=User(name="foo")))
        session.commit()

        # collection-based relationships are by default named
        # "<classname>_collection"
        u1 = session.query(User).first()
        print(u1.address_collection)

    Above, calling :meth:`.AutomapBase.prepare` while passing along the
    :paramref:`.AutomapBase.prepare.reflect` parameter indicates that the
    :meth:`_schema.MetaData.reflect`
    method will be called on this declarative base
    classes' :class:`_schema.MetaData` collection; then, each **viable**
    :class:`_schema.Table` within the :class:`_schema.MetaData`
    will get a new mapped class
    generated automatically.  The :class:`_schema.ForeignKeyConstraint`
    objects which
    link the various tables together will be used to produce new, bidirectional
    :func:`_orm.relationship` objects between classes.
    The classes and relationships
    follow along a default naming scheme that we can customize.  At this point,
    our basic mapping consisting of related ``User`` and ``Address`` classes is
    ready to use in the traditional way.

    .. note:: By **viable**, we mean that for a table to be mapped, it must
       specify a primary key.  Additionally, if the table is detected as being
       a pure association table between two other tables, it will not be directly
       mapped and will instead be configured as a many-to-many table between
       the mappings for the two referring tables.

从现有元数据生成用法
=============================================

Generating Mappings from an Existing MetaData

.. tab:: 中文

    我们可以将预先声明的 :class:`_schema.MetaData` 对象传递给 :func:`.automap_base`。
    这个对象可以以任何方式构造，包括通过编程、从序列化文件中或通过
    :meth:`_schema.MetaData.reflect` 反射自身构造。下面我们展示了反射和
    显式表声明的组合::

        from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
        from sqlalchemy.ext.automap import automap_base

        engine = create_engine("sqlite:///mydatabase.db")

        # 创建我们自己的 MetaData 对象
        metadata = MetaData()

        # 我们可以从数据库中反射它，使用选项
        # 比如 'only' 来限制我们查看的表格...
        metadata.reflect(engine, only=["user", "address"])

        # ...或者仅使用它定义我们自己的 Table 对象（或两者结合）
        Table(
            "user_order",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", ForeignKey("user.id")),
        )

        # 然后我们可以从这个 MetaData 中生成一组映射。
        Base = automap_base(metadata=metadata)

        # 调用 prepare() 只是设置映射类和关系。
        Base.prepare()

        # 映射类已准备好
        User = Base.classes.user
        Address = Base.classes.address
        Order = Base.classes.user_order

.. tab:: 英文

    We can pass a pre-declared :class:`_schema.MetaData` object to
    :func:`.automap_base`.
    This object can be constructed in any way, including programmatically, from
    a serialized file, or from itself being reflected using
    :meth:`_schema.MetaData.reflect`.
    Below we illustrate a combination of reflection and
    explicit table declaration::

        from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
        from sqlalchemy.ext.automap import automap_base

        engine = create_engine("sqlite:///mydatabase.db")

        # produce our own MetaData object
        metadata = MetaData()

        # we can reflect it ourselves from a database, using options
        # such as 'only' to limit what tables we look at...
        metadata.reflect(engine, only=["user", "address"])

        # ... or just define our own Table objects with it (or combine both)
        Table(
            "user_order",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("user_id", ForeignKey("user.id")),
        )

        # we can then produce a set of mappings from this MetaData.
        Base = automap_base(metadata=metadata)

        # calling prepare() just sets up mapped classes and relationships.
        Base.prepare()

        # mapped classes are ready
        User = Base.classes.user
        Address = Base.classes.address
        Order = Base.classes.user_order

.. _automap_by_module:

从多个架构生成用法
=========================================

Generating Mappings from Multiple Schemas

.. tab:: 中文

    当与反射一起使用时，:meth:`.AutomapBase.prepare` 方法每次最多只能反射一个模式中的表，
    可以使用 :paramref:`.AutomapBase.prepare.schema` 参数指示要反射的模式名称。
    为了从多个模式中填充 :class:`.AutomapBase`，可以多次调用 :meth:`.AutomapBase.prepare`，
    每次传递不同的名称给 :paramref:`.AutomapBase.prepare.schema` 参数。
    :meth:`.AutomapBase.prepare` 方法会维护一个已映射的 :class:`_schema.Table` 对象的内部列表，
    并且仅会为自上次运行 :meth:`.AutomapBase.prepare` 后新添加的 :class:`_schema.Table` 对象添加新的映射::

        e = create_engine("postgresql://scott:tiger@localhost/test")

        Base.metadata.create_all(e)

        Base = automap_base()

        Base.prepare(e)
        Base.prepare(e, schema="test_schema")
        Base.prepare(e, schema="test_schema_2")

    .. versionadded:: 2.0  :meth:`.AutomapBase.prepare` 方法可以被调用任意次数；
       每次运行时，只有新增的表会被映射。 在版本 1.4 及更早版本中，多次调用会导致错误，
       因为它会尝试重新映射已经映射的类。 之前的解决方法是直接调用
       :meth:`_schema.MetaData.reflect`，此方法仍然可用。

.. tab:: 英文

    The :meth:`.AutomapBase.prepare` method when used with reflection may reflect
    tables from one schema at a time at most, using the
    :paramref:`.AutomapBase.prepare.schema` parameter to indicate the name of a
    schema to be reflected from. In order to populate the :class:`.AutomapBase`
    with tables from multiple schemas, :meth:`.AutomapBase.prepare` may be invoked
    multiple times, each time passing a different name to the
    :paramref:`.AutomapBase.prepare.schema` parameter. The
    :meth:`.AutomapBase.prepare` method keeps an internal list of
    :class:`_schema.Table` objects that have already been mapped, and will add new
    mappings only for those :class:`_schema.Table` objects that are new since the
    last time :meth:`.AutomapBase.prepare` was run::

        e = create_engine("postgresql://scott:tiger@localhost/test")

        Base.metadata.create_all(e)

        Base = automap_base()

        Base.prepare(e)
        Base.prepare(e, schema="test_schema")
        Base.prepare(e, schema="test_schema_2")

    .. versionadded:: 2.0  The :meth:`.AutomapBase.prepare` method may be called
       any number of times; only newly added tables will be mapped
       on each run.   Previously in version 1.4 and earlier, multiple calls would
       cause errors as it would attempt to re-map an already mapped class.
       The previous workaround approach of invoking
       :meth:`_schema.MetaData.reflect` directly remains available as well.

跨多个架构自动映射同用法
-----------------------------------------------------

Automapping same-named tables across multiple schemas

.. tab:: 中文

    对于多模式可能具有同名表的常见情况，因此会生成同名类，可以通过以下方式解决冲突：
    使用 :paramref:`.AutomapBase.prepare.classname_for_table` 钩子在每个模式的基础上应用不同的类名，或者使用
    :paramref:`.AutomapBase.prepare.modulename_for_table` 钩子，通过更改类的有效 ``__module__`` 属性来区分同名类。
    在下面的示例中，使用该钩子为所有类创建一个 ``__module__`` 属性，其形式为 ``mymodule.<schemaname>``，
    如果没有模式，则使用模式名称 ``default``::

        e = create_engine("postgresql://scott:tiger@localhost/test")

        Base.metadata.create_all(e)


        def module_name_for_table(cls, tablename, table):
            if table.schema is not None:
                return f"mymodule.{table.schema}"
            else:
                return f"mymodule.default"


        Base = automap_base()

        Base.prepare(e, modulename_for_table=module_name_for_table)
        Base.prepare(
            e, schema="test_schema", modulename_for_table=module_name_for_table
        )
        Base.prepare(
            e, schema="test_schema_2", modulename_for_table=module_name_for_table
        )

    同名类被组织到一个分层的集合中，可以通过 :attr:`.AutomapBase.by_module` 访问。
    此集合可以使用特定包/模块的点分隔名称来遍历，直到所需的类名。

    .. note:: 当使用 :paramref:`.AutomapBase.prepare.modulename_for_table`
       钩子返回一个新的 ``__module__`` 且不为 ``None`` 时，类将
       **不会** 被放入 :attr:`.AutomapBase.classes` 集合中；只有那些没有显式给定模块名的类
       会放入该集合，因为该集合无法单独表示同名类。

    在上面的示例中，如果数据库中包含一个名为 ``accounts`` 的表，
    并且该表存在于默认模式、``test_schema`` 模式和 ``test_schema_2`` 模式中，
    则将提供三个单独的类，分别为::

        Base.by_module.mymodule.default.accounts
        Base.by_module.mymodule.test_schema.accounts
        Base.by_module.mymodule.test_schema_2.accounts

    为所有 :class:`.AutomapBase` 类生成的默认模块命名空间是
    ``sqlalchemy.ext.automap``。如果没有使用
    :paramref:`.AutomapBase.prepare.modulename_for_table` 钩子，
    则 :attr:`.AutomapBase.by_module` 的内容将完全位于
    ``sqlalchemy.ext.automap`` 命名空间中（例如，
    ``MyBase.by_module.sqlalchemy.ext.automap.<classname>``），
    其中包含与 :attr:`.AutomapBase.classes` 中看到的相同的一系列类。
    因此，通常只有在显式 ``__module__`` 约定存在时，才需要使用 :attr:`.AutomapBase.by_module`。

    .. versionadded:: 2.0

        添加了 :attr:`.AutomapBase.by_module` 集合，该集合根据点分隔的模块名称
        存储类，并且添加了 :paramref:`.Automap.prepare.modulename_for_table` 参数，
        允许为自动映射的类定义自定义的 ``__module__`` 方案。

.. tab:: 英文

    For the common case where multiple schemas may have same-named tables and
    therefore would generate same-named classes, conflicts can be resolved either
    through use of the :paramref:`.AutomapBase.prepare.classname_for_table` hook to
    apply different classnames on a per-schema basis, or by using the
    :paramref:`.AutomapBase.prepare.modulename_for_table` hook, which allows
    disambiguation of same-named classes by changing their effective ``__module__``
    attribute. In the example below, this hook is used to create a ``__module__``
    attribute for all classes that is of the form ``mymodule.<schemaname>``, where
    the schema name ``default`` is used if no schema is present::

        e = create_engine("postgresql://scott:tiger@localhost/test")

        Base.metadata.create_all(e)


        def module_name_for_table(cls, tablename, table):
            if table.schema is not None:
                return f"mymodule.{table.schema}"
            else:
                return f"mymodule.default"


        Base = automap_base()

        Base.prepare(e, modulename_for_table=module_name_for_table)
        Base.prepare(
            e, schema="test_schema", modulename_for_table=module_name_for_table
        )
        Base.prepare(
            e, schema="test_schema_2", modulename_for_table=module_name_for_table
        )

    The same named-classes are organized into a hierarchical collection available
    at :attr:`.AutomapBase.by_module`.  This collection is traversed using the
    dot-separated name of a particular package/module down into the desired
    class name.

    .. note:: When using the :paramref:`.AutomapBase.prepare.modulename_for_table`
       hook to return a new ``__module__`` that is not ``None``, the class is
       **not** placed into the :attr:`.AutomapBase.classes` collection; only
       classes that were not given an explicit modulename are placed here, as the
       collection cannot represent same-named classes individually.

    In the example above, if the database contained a table named ``accounts`` in
    all three of the default schema, the ``test_schema`` schema, and the
    ``test_schema_2`` schema, three separate classes will be available as::

        Base.by_module.mymodule.default.accounts
        Base.by_module.mymodule.test_schema.accounts
        Base.by_module.mymodule.test_schema_2.accounts

    The default module namespace generated for all :class:`.AutomapBase` classes is
    ``sqlalchemy.ext.automap``. If no
    :paramref:`.AutomapBase.prepare.modulename_for_table` hook is used, the
    contents of :attr:`.AutomapBase.by_module` will be entirely within the
    ``sqlalchemy.ext.automap`` namespace (e.g.
    ``MyBase.by_module.sqlalchemy.ext.automap.<classname>``), which would contain
    the same series of classes as what would be seen in
    :attr:`.AutomapBase.classes`. Therefore it's generally only necessary to use
    :attr:`.AutomapBase.by_module` when explicit ``__module__`` conventions are
    present.

    .. versionadded:: 2.0

        Added the :attr:`.AutomapBase.by_module` collection, which stores
        classes within a named hierarchy based on dot-separated module names,
        as well as the :paramref:`.Automap.prepare.modulename_for_table` parameter
        which allows for custom ``__module__`` schemes for automapped
        classes.



明确指用法
=============================

Specifying Classes Explicitly

.. tab:: 中文

    .. tip:: 如果应用程序中预计显式类会占据重要地位，
       考虑改用 :class:`.DeferredReflection`。

    :mod:`.sqlalchemy.ext.automap` 扩展允许显式定义类，
    方式类似于 :class:`.DeferredReflection` 类。
    从 :class:`.AutomapBase` 扩展的类像常规的声明式类一样工作，
    但在构造后不会立即映射，而是在我们调用 :meth:`.AutomapBase.prepare` 时映射。
    :meth:`.AutomapBase.prepare` 方法将利用我们基于表名建立的类。
    如果我们的模式包含表 ``user`` 和 ``address``，
    我们可以定义一个或两个类来使用::

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import create_engine

        # automap base
        Base = automap_base()


        # 为 'user' 表预声明 User 类
        class User(Base):
            __tablename__ = "user"

            # 重写 schema 元素，如列
            user_name = Column("name", String)

            # 也可以重写关系，如有需要
            # 我们必须使用 automap 默认使用的关系名称，
            # 还必须引用 automap 会为 "address" 生成的类名
            address_collection = relationship("address", collection_class=set)


        # 反射
        engine = create_engine("sqlite:///mydatabase.db")
        Base.prepare(autoload_with=engine)

        # 我们仍然有从表名 "address" 生成的 Address 类，
        # 但 User 现在与 Base.classes.User 相同

        Address = Base.classes.address

        u1 = session.query(User).first()
        print(u1.address_collection)

        # backref 仍然存在：
        a1 = session.query(Address).first()
        print(a1.user)

    上述示例中，一个比较复杂的细节是，我们演示了如何覆盖
    automap 本应创建的 :func:`_orm.relationship` 对象。
    为此，我们需要确保名称与 automap 通常生成的名称匹配，
    即关系名称应为 ``User.address_collection``，
    从 automap 角度看，所引用的类名为 ``address``，
    尽管在我们使用此类时，它被称为 ``Address``。


.. tab:: 英文

    .. tip:: If explicit classes are expected to be prominent in an application,
       consider using :class:`.DeferredReflection` instead.

    The :mod:`.sqlalchemy.ext.automap` extension allows classes to be defined
    explicitly, in a way similar to that of the :class:`.DeferredReflection` class.
    Classes that extend from :class:`.AutomapBase` act like regular declarative
    classes, but are not immediately mapped after their construction, and are
    instead mapped when we call :meth:`.AutomapBase.prepare`.  The
    :meth:`.AutomapBase.prepare` method will make use of the classes we've
    established based on the table name we use.  If our schema contains tables
    ``user`` and ``address``, we can define one or both of the classes to be used::

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import create_engine

        # automap base
        Base = automap_base()


        # pre-declare User for the 'user' table
        class User(Base):
            __tablename__ = "user"

            # override schema elements like Columns
            user_name = Column("name", String)

            # override relationships too, if desired.
            # we must use the same name that automap would use for the
            # relationship, and also must refer to the class name that automap will
            # generate for "address"
            address_collection = relationship("address", collection_class=set)


        # reflect
        engine = create_engine("sqlite:///mydatabase.db")
        Base.prepare(autoload_with=engine)

        # we still have Address generated from the tablename "address",
        # but User is the same as Base.classes.User now

        Address = Base.classes.address

        u1 = session.query(User).first()
        print(u1.address_collection)

        # the backref is still there:
        a1 = session.query(Address).first()
        print(a1.user)

    Above, one of the more intricate details is that we illustrated overriding
    one of the :func:`_orm.relationship` objects that automap would have created.
    To do this, we needed to make sure the names match up with what automap
    would normally generate, in that the relationship name would be
    ``User.address_collection`` and the name of the class referred to, from
    automap's perspective, is called ``address``, even though we are referring to
    it as ``Address`` within our usage of this class.

覆盖命名用法
=========================

Overriding Naming Schemes

.. tab:: 中文

    :mod:`.sqlalchemy.ext.automap` 的任务是基于模式生成映射类和关系名称，
    这意味着它在确定这些名称时会有决策点。
    这些决策点是通过函数提供的，可以传递给 :meth:`.AutomapBase.prepare` 方法，
    并且分别称为 :func:`.classname_for_table`、
    :func:`.name_for_scalar_relationship`，
    以及 :func:`.name_for_collection_relationship`。 这些函数中的任何一个或所有都可以提供，
    如下例所示，我们使用“驼峰命名法”方案来命名类名，并使用 `Inflect <https://pypi.org/project/inflect>`_ 包
    为集合名称添加“复数化”功能::

        import re
        import inflect


        def camelize_classname(base, tablename, table):
            "生成一个 '驼峰化' 的类名，例如"
            "'words_and_underscores' -> 'WordsAndUnderscores'"

            return str(
                tablename[0].upper()
                + re.sub(
                    r"_([a-z])",
                    lambda m: m.group(1).upper(),
                    tablename[1:],
                )
            )


        _pluralizer = inflect.engine()


        def pluralize_collection(base, local_cls, referred_cls, constraint):
            "生成一个 '非驼峰化'、'复数化' 的类名，例如"
            "'SomeTerm' -> 'some_terms'"

            referred_name = referred_cls.__name__
            uncamelized = re.sub(
                r"[A-Z]",
                lambda m: "_%s" % m.group(0).lower(),
                referred_name,
            )[1:]
            pluralized = _pluralizer.plural(uncamelized)
            return pluralized


        from sqlalchemy.ext.automap import automap_base

        Base = automap_base()

        engine = create_engine("sqlite:///mydatabase.db")

        Base.prepare(
            autoload_with=engine,
            classname_for_table=camelize_classname,
            name_for_collection_relationship=pluralize_collection,
        )

    从上述映射中，我们现在会有 ``User`` 和 ``Address`` 类，
    其中从 ``User`` 到 ``Address`` 的集合称为 ``User.addresses``::

        User, Address = Base.classes.User, Base.classes.Address

        u1 = User(addresses=[Address(email="foo@bar.com")])

.. tab:: 英文

    :mod:`.sqlalchemy.ext.automap` is tasked with producing mapped classes and
    relationship names based on a schema, which means it has decision points in how
    these names are determined.  These three decision points are provided using
    functions which can be passed to the :meth:`.AutomapBase.prepare` method, and
    are known as :func:`.classname_for_table`,
    :func:`.name_for_scalar_relationship`,
    and :func:`.name_for_collection_relationship`.  Any or all of these
    functions are provided as in the example below, where we use a "camel case"
    scheme for class names and a "pluralizer" for collection names using the
    `Inflect <https://pypi.org/project/inflect>`_ package::

        import re
        import inflect


        def camelize_classname(base, tablename, table):
            "Produce a 'camelized' class name, e.g."
            "'words_and_underscores' -> 'WordsAndUnderscores'"

            return str(
                tablename[0].upper()
                + re.sub(
                    r"_([a-z])",
                    lambda m: m.group(1).upper(),
                    tablename[1:],
                )
            )


        _pluralizer = inflect.engine()


        def pluralize_collection(base, local_cls, referred_cls, constraint):
            "Produce an 'uncamelized', 'pluralized' class name, e.g."
            "'SomeTerm' -> 'some_terms'"

            referred_name = referred_cls.__name__
            uncamelized = re.sub(
                r"[A-Z]",
                lambda m: "_%s" % m.group(0).lower(),
                referred_name,
            )[1:]
            pluralized = _pluralizer.plural(uncamelized)
            return pluralized


        from sqlalchemy.ext.automap import automap_base

        Base = automap_base()

        engine = create_engine("sqlite:///mydatabase.db")

        Base.prepare(
            autoload_with=engine,
            classname_for_table=camelize_classname,
            name_for_collection_relationship=pluralize_collection,
        )

    From the above mapping, we would now have classes ``User`` and ``Address``,
    where the collection from ``User`` to ``Address`` is called
    ``User.addresses``::

        User, Address = Base.classes.User, Base.classes.Address

        u1 = User(addresses=[Address(email="foo@bar.com")])

关系用法
======================

Relationship Detection

.. tab:: 中文

    自动映射完成的大部分工作是基于外键生成 :func:`_orm.relationship` 结构。
    在多对一和一对多关系中，工作机制如下：

    1. 给定的 :class:`_schema.Table`，已知映射到特定类，
       将检查是否存在 :class:`_schema.ForeignKeyConstraint` 对象。

    2. 从每个 :class:`_schema.ForeignKeyConstraint` 中，匹配
       其中的远程 :class:`_schema.Table` 对象，并将其与
       要映射到的类进行匹配，如果没有匹配，则跳过。

    3. 当我们检查的 :class:`_schema.ForeignKeyConstraint`
       对应于来自直接映射类的引用时，关系将设置为多对一，
       指向被引用的类；在被引用的类上将创建一个相应的
       一对多 backref，指向这个类。

    4. 如果 :class:`_schema.ForeignKeyConstraint` 中的任何列
       是不可为空的（例如 ``nullable=False``），
       则会将 :paramref:`_orm.relationship.cascade` 关键字参数
       设置为 ``all, delete-orphan``，并将其传递给关系或 backref。
       如果 :class:`_schema.ForeignKeyConstraint` 报告
       :paramref:`_schema.ForeignKeyConstraint.ondelete`
       被设置为 ``CASCADE`` （对于不可为空的列）或 ``SET NULL`` （对于可为空的列），
       则 :paramref:`_orm.relationship.passive_deletes` 标志会被设置为 ``True``，
       并包含在关系的关键字参数中。
       请注意，并非所有后端都支持反射 ON DELETE。

    5. 关系的名称是通过 :paramref:`.AutomapBase.prepare.name_for_scalar_relationship`
       和 :paramref:`.AutomapBase.prepare.name_for_collection_relationship`
       可调用函数确定的。需要注意的是，默认的关系命名是基于 **实际类名** 进行的。
       如果你为某个类显式指定了名称，或指定了其他类命名方案，
       那么关系名称将会从该名称中派生。

    6. 类会检查是否存在与这些名称匹配的已映射属性。
       如果在一侧检测到映射属性，但另一侧没有，
       :class:`.AutomapBase` 会尝试在缺失的一侧创建关系，
       然后使用 :paramref:`_orm.relationship.back_populates`
       参数指向另一侧的关系。

    7. 在通常情况下，如果两侧都没有关系，
       :meth:`.AutomapBase.prepare` 会在"多对一"的一侧生成 :func:`_orm.relationship`，
       并使用 :paramref:`_orm.relationship.backref` 参数将其匹配到另一侧。

    8. :func:`_orm.relationship` 和可选的 :func:`.backref` 的生成
       会交给 :paramref:`.AutomapBase.prepare.generate_relationship` 函数处理，
       该函数可以由最终用户提供，以增强传递给 :func:`_orm.relationship` 或 :func:`.backref`
       的参数，或使用这些函数的自定义实现。

.. tab:: 英文

    The vast majority of what automap accomplishes is the generation of
    :func:`_orm.relationship` structures based on foreign keys.  The mechanism
    by which this works for many-to-one and one-to-many relationships is as
    follows:

    1. A given :class:`_schema.Table`, known to be mapped to a particular class,
       is examined for :class:`_schema.ForeignKeyConstraint` objects.

    2. From each :class:`_schema.ForeignKeyConstraint`, the remote
       :class:`_schema.Table`
       object present is matched up to the class to which it is to be mapped,
       if any, else it is skipped.

    3. As the :class:`_schema.ForeignKeyConstraint`
       we are examining corresponds to a
       reference from the immediate mapped class,  the relationship will be set up
       as a many-to-one referring to the referred class; a corresponding
       one-to-many backref will be created on the referred class referring
       to this class.

    4. If any of the columns that are part of the
       :class:`_schema.ForeignKeyConstraint`
       are not nullable (e.g. ``nullable=False``), a
       :paramref:`_orm.relationship.cascade` keyword argument
       of ``all, delete-orphan`` will be added to the keyword arguments to
       be passed to the relationship or backref.  If the
       :class:`_schema.ForeignKeyConstraint` reports that
       :paramref:`_schema.ForeignKeyConstraint.ondelete`
       is set to ``CASCADE`` for a not null or ``SET NULL`` for a nullable
       set of columns, the option :paramref:`_orm.relationship.passive_deletes`
       flag is set to ``True`` in the set of relationship keyword arguments.
       Note that not all backends support reflection of ON DELETE.

    5. The names of the relationships are determined using the
       :paramref:`.AutomapBase.prepare.name_for_scalar_relationship` and
       :paramref:`.AutomapBase.prepare.name_for_collection_relationship`
       callable functions.  It is important to note that the default relationship
       naming derives the name from the **the actual class name**.  If you've
       given a particular class an explicit name by declaring it, or specified an
       alternate class naming scheme, that's the name from which the relationship
       name will be derived.

    6. The classes are inspected for an existing mapped property matching these
       names.  If one is detected on one side, but none on the other side,
       :class:`.AutomapBase` attempts to create a relationship on the missing side,
       then uses the :paramref:`_orm.relationship.back_populates`
       parameter in order to
       point the new relationship to the other side.

    7. In the usual case where no relationship is on either side,
       :meth:`.AutomapBase.prepare` produces a :func:`_orm.relationship` on the
       "many-to-one" side and matches it to the other using the
       :paramref:`_orm.relationship.backref` parameter.

    8. Production of the :func:`_orm.relationship` and optionally the
       :func:`.backref`
       is handed off to the :paramref:`.AutomapBase.prepare.generate_relationship`
       function, which can be supplied by the end-user in order to augment
       the arguments passed to :func:`_orm.relationship` or :func:`.backref` or to
       make use of custom implementations of these functions.

自定义关系用法
-----------------------------

Custom Relationship Arguments

.. tab:: 中文

    :paramref:`.AutomapBase.prepare.generate_relationship` 钩子可以用来
    为关系添加参数。对于大多数情况，我们可以使用现有的
    :func:`.automap.generate_relationship` 函数，返回
    对象，并在给定的关键字字典中添加我们的参数。

    下面是一个示例，演示如何将
    :paramref:`_orm.relationship.cascade` 和
    :paramref:`_orm.relationship.passive_deletes`
    选项传递给所有一对多关系::

        from sqlalchemy.ext.automap import generate_relationship
        from sqlalchemy.orm import interfaces


        def _gen_relationship(
            base, direction, return_fn, attrname, local_cls, referred_cls, **kw
        ):
            if direction is interfaces.ONETOMANY:
                kw["cascade"] = "all, delete-orphan"
                kw["passive_deletes"] = True
            # 使用内置函数来实际返回
            # 结果。
            return generate_relationship(
                base, direction, return_fn, attrname, local_cls, referred_cls, **kw
            )


        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import create_engine

        # automap base
        Base = automap_base()

        engine = create_engine("sqlite:///mydatabase.db")
        Base.prepare(autoload_with=engine, generate_relationship=_gen_relationship)

.. tab:: 英文

    The :paramref:`.AutomapBase.prepare.generate_relationship` hook can be used
    to add parameters to relationships.  For most cases, we can make use of the
    existing :func:`.automap.generate_relationship` function to return
    the object, after augmenting the given keyword dictionary with our own
    arguments.

    Below is an illustration of how to send
    :paramref:`_orm.relationship.cascade` and
    :paramref:`_orm.relationship.passive_deletes`
    options along to all one-to-many relationships::

        from sqlalchemy.ext.automap import generate_relationship
        from sqlalchemy.orm import interfaces


        def _gen_relationship(
            base, direction, return_fn, attrname, local_cls, referred_cls, **kw
        ):
            if direction is interfaces.ONETOMANY:
                kw["cascade"] = "all, delete-orphan"
                kw["passive_deletes"] = True
            # make use of the built-in function to actually return
            # the result.
            return generate_relationship(
                base, direction, return_fn, attrname, local_cls, referred_cls, **kw
            )


        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import create_engine

        # automap base
        Base = automap_base()

        engine = create_engine("sqlite:///mydatabase.db")
        Base.prepare(autoload_with=engine, generate_relationship=_gen_relationship)

多对多用法
--------------------------

Many-to-Many relationships

.. tab:: 中文

    :mod:`.sqlalchemy.ext.automap` 将生成多对多关系，例如那些包含 ``secondary`` 参数的关系。生成这些关系的过程如下：

    1. 给定的 :class:`_schema.Table` 会在映射类被分配之前，检查是否存在 :class:`_schema.ForeignKeyConstraint` 对象。

    2. 如果表包含恰好两个 :class:`_schema.ForeignKeyConstraint` 对象，并且表中的所有列都是这两个 :class:`_schema.ForeignKeyConstraint` 对象的一部分，则该表被假定为一个“secondary”表，并且 **不会直接映射**。

    3. 该 :class:`_schema.Table` 所引用的两个（或一个，自引用的情况）外部表会与它们将要映射到的类进行匹配（如果有的话）。

    4. 如果找到两侧的映射类，则会在这两个类之间创建一个多对多的双向 :func:`_orm.relationship` / :func:`.backref` 配对。

    5. 多对多的覆盖逻辑与一对多/多对一的逻辑相同；会调用 :func:`.generate_relationship` 函数来生成结构，并保持现有属性。

.. tab:: 英文

    :mod:`.sqlalchemy.ext.automap` will generate many-to-many relationships, e.g.
    those which contain a ``secondary`` argument.  The process for producing these
    is as follows:

    1. A given :class:`_schema.Table` is examined for
       :class:`_schema.ForeignKeyConstraint`
       objects, before any mapped class has been assigned to it.

    2. If the table contains two and exactly two
       :class:`_schema.ForeignKeyConstraint`
       objects, and all columns within this table are members of these two
       :class:`_schema.ForeignKeyConstraint` objects, the table is assumed to be a
       "secondary" table, and will **not be mapped directly**.

    3. The two (or one, for self-referential) external tables to which the
       :class:`_schema.Table`
       refers to are matched to the classes to which they will be
       mapped, if any.

    4. If mapped classes for both sides are located, a many-to-many bi-directional
       :func:`_orm.relationship` / :func:`.backref`
       pair is created between the two
       classes.

    5. The override logic for many-to-many works the same as that of one-to-many/
       many-to-one; the :func:`.generate_relationship` function is called upon
       to generate the structures and existing attributes will be maintained.

具有继承的用法
------------------------------

Relationships with Inheritance

.. tab:: 中文

    :mod:`.sqlalchemy.ext.automap` 不会在继承关系中的两个类之间生成任何关系。也就是说，给定以下两个类：

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            type = Column(String(50))
            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }

        class Engineer(Employee):
            __tablename__ = "engineer"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    从 ``Engineer`` 到 ``Employee`` 的外键用于建立两者之间的连接继承关系，而不是作为关系使用。

    请注意，这意味着 automap 不会为从子类到父类的外键生成 *任何* 关系。如果映射中有从子类到父类的实际关系，这些关系需要显式声明。以下示例中，由于 ``Engineer`` 到 ``Employee`` 有两个独立的外键，我们需要设置我们希望的关系，并明确指定 ``inherit_condition``，因为这些是 SQLAlchemy 无法自动推断的内容：

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            type = Column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }

        class Engineer(Employee):
            __tablename__ = "engineer"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            favorite_employee_id = Column(Integer, ForeignKey("employee.id"))

            favorite_employee = relationship(
                Employee, foreign_keys=favorite_employee_id
            )

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "inherit_condition": id == Employee.id,
            }

.. tab:: 英文

    :mod:`.sqlalchemy.ext.automap` will not generate any relationships between
    two classes that are in an inheritance relationship.   That is, with two
    classes given as follows::

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            type = Column(String(50))
            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    The foreign key from ``Engineer`` to ``Employee`` is used not for a
    relationship, but to establish joined inheritance between the two classes.

    Note that this means automap will not generate *any* relationships
    for foreign keys that link from a subclass to a superclass.  If a mapping
    has actual relationships from subclass to superclass as well, those
    need to be explicit.  Below, as we have two separate foreign keys
    from ``Engineer`` to ``Employee``, we need to set up both the relationship
    we want as well as the ``inherit_condition``, as these are not things
    SQLAlchemy can guess::

        class Employee(Base):
            __tablename__ = "employee"
            id = Column(Integer, primary_key=True)
            type = Column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": type,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = Column(Integer, ForeignKey("employee.id"), primary_key=True)
            favorite_employee_id = Column(Integer, ForeignKey("employee.id"))

            favorite_employee = relationship(
                Employee, foreign_keys=favorite_employee_id
            )

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "inherit_condition": id == Employee.id,
            }

处理简单命名用法
--------------------------------

Handling Simple Naming Conflicts

.. tab:: 中文

    在映射过程中如果出现命名冲突，可以根据需要覆盖 :func:`.classname_for_table` 、:func:`.name_for_scalar_relationship` 和 :func:`.name_for_collection_relationship`。例如，如果 automap 尝试为多对一关系命名时与现有列名称相同，可以有条件地选择其他命名约定。考虑以下模式：

    .. sourcecode:: sql

        CREATE TABLE table_a (
            id INTEGER PRIMARY KEY
        );

        CREATE TABLE table_b (
            id INTEGER PRIMARY KEY,
            table_a INTEGER,
            FOREIGN KEY(table_a) REFERENCES table_a(id)
        );

    上述模式将首先将 ``table_a`` 表自动映射为名为 ``table_a`` 的类；然后，它会将一个与该类相关的关系映射到 ``table_b`` 类上，关系的名称也为 ``table_a``。这种关系名称与映射列 ``table_b.table_a`` 冲突，因此会在映射时抛出错误。

    我们可以通过使用下划线来解决此冲突，如下所示：

        def name_for_scalar_relationship(
            base, local_cls, referred_cls, constraint
        ):
            name = referred_cls.__name__.lower()
            local_table = local_cls.__table__
            if name in local_table.columns:
                newname = name + "_"
                warnings.warn(
                    "Already detected name %s present.  using %s" % (name, newname)
                )
                return newname
            return name


        Base.prepare(
            autoload_with=engine,
            name_for_scalar_relationship=name_for_scalar_relationship,
        )

    另外，我们可以改变列端的名称。可以使用 :ref:`mapper_column_distinct_names` 中描述的技术，通过显式地为列指定新名称来修改映射的列：

        Base = automap_base()


        class TableB(Base):
            __tablename__ = "table_b"
            _table_a = Column("table_a", ForeignKey("table_a.id"))


        Base.prepare(autoload_with=engine)

.. tab:: 英文

    In the case of naming conflicts during mapping, override any of
    :func:`.classname_for_table`, :func:`.name_for_scalar_relationship`,
    and :func:`.name_for_collection_relationship` as needed.  For example, if
    automap is attempting to name a many-to-one relationship the same as an
    existing column, an alternate convention can be conditionally selected.  Given
    a schema:

    .. sourcecode:: sql

        CREATE TABLE table_a (
            id INTEGER PRIMARY KEY
        );

        CREATE TABLE table_b (
            id INTEGER PRIMARY KEY,
            table_a INTEGER,
            FOREIGN KEY(table_a) REFERENCES table_a(id)
        );

    The above schema will first automap the ``table_a`` table as a class named
    ``table_a``; it will then automap a relationship onto the class for ``table_b``
    with the same name as this related class, e.g. ``table_a``.  This
    relationship name conflicts with the mapping column ``table_b.table_a``,
    and will emit an error on mapping.

    We can resolve this conflict by using an underscore as follows::

        def name_for_scalar_relationship(
            base, local_cls, referred_cls, constraint
        ):
            name = referred_cls.__name__.lower()
            local_table = local_cls.__table__
            if name in local_table.columns:
                newname = name + "_"
                warnings.warn(
                    "Already detected name %s present.  using %s" % (name, newname)
                )
                return newname
            return name


        Base.prepare(
            autoload_with=engine,
            name_for_scalar_relationship=name_for_scalar_relationship,
        )

    Alternatively, we can change the name on the column side.   The columns
    that are mapped can be modified using the technique described at
    :ref:`mapper_column_distinct_names`, by assigning the column explicitly
    to a new name::

        Base = automap_base()


        class TableB(Base):
            __tablename__ = "table_b"
            _table_a = Column("table_a", ForeignKey("table_a.id"))


        Base.prepare(autoload_with=engine)

使用带有明确声明的 Autom用法
========================================

Using Automap with Explicit Declarations

.. tab:: 中文

    如前所述，automap 不依赖于反射，并且可以使用任何 :class:`_schema.Table` 对象集合，这些对象位于 :class:`_schema.MetaData` 集合中。因此，automap 也可以用于在完全定义表元数据的模型基础上，生成缺失的关系：

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import Column, Integer, String, ForeignKey

        Base = automap_base()


        class User(Base):
            __tablename__ = "user"

            id = Column(Integer, primary_key=True)
            name = Column(String)


        class Address(Base):
            __tablename__ = "address"

            id = Column(Integer, primary_key=True)
            email = Column(String)
            user_id = Column(ForeignKey("user.id"))


        # 生成关系
        Base.prepare()

        # 映射完成，生成 "address_collection" 和
        # "user" 关系
        a1 = Address(email="u1")
        a2 = Address(email="u2")
        u1 = User(address_collection=[a1, a2])
        assert a1.user is u1

    上述代码中，给定了基本完整的 ``User`` 和 ``Address`` 映射，定义在 ``Address.user_id`` 上的 :class:`_schema.ForeignKey` 使得在映射类中生成了双向关系对 ``Address.user`` 和 ``User.address_collection``。

    请注意，当继承 :class:`.AutomapBase` 时，必须调用 :meth:`.AutomapBase.prepare` 方法；如果未调用，已声明的类将处于未映射状态。


.. tab:: 英文

    As noted previously, automap has no dependency on reflection, and can make
    use of any collection of :class:`_schema.Table` objects within a
    :class:`_schema.MetaData`
    collection.  From this, it follows that automap can also be used
    generate missing relationships given an otherwise complete model that fully
    defines table metadata::

        from sqlalchemy.ext.automap import automap_base
        from sqlalchemy import Column, Integer, String, ForeignKey

        Base = automap_base()


        class User(Base):
            __tablename__ = "user"

            id = Column(Integer, primary_key=True)
            name = Column(String)


        class Address(Base):
            __tablename__ = "address"

            id = Column(Integer, primary_key=True)
            email = Column(String)
            user_id = Column(ForeignKey("user.id"))


        # produce relationships
        Base.prepare()

        # mapping is complete, with "address_collection" and
        # "user" relationships
        a1 = Address(email="u1")
        a2 = Address(email="u2")
        u1 = User(address_collection=[a1, a2])
        assert a1.user is u1

    Above, given mostly complete ``User`` and ``Address`` mappings, the
    :class:`_schema.ForeignKey` which we defined on ``Address.user_id`` allowed a
    bidirectional relationship pair ``Address.user`` and
    ``User.address_collection`` to be generated on the mapped classes.

    Note that when subclassing :class:`.AutomapBase`,
    the :meth:`.AutomapBase.prepare` method is required; if not called, the classes
    we've declared are in an un-mapped state.


.. _automap_intercepting_columns:

拦截列用法
===============================

Intercepting Column Definitions

.. tab:: 中文

    :class:`_schema.MetaData` 和 :class:`_schema.Table` 对象支持一个事件钩子 :meth:`_events.DDLEvents.column_reflect`，可以在构造 :class:`_schema.Column` 对象之前拦截关于数据库列的信息。例如，如果我们希望使用诸如 ``"attr_<columnname>"`` 的命名约定来映射列，可以使用该事件，如下所示：

        @event.listens_for(Base.metadata, "column_reflect")
        def column_reflect(inspector, table, column_info):
            # 设置列的 key 为 "attr_<小写列名>"
            column_info["key"] = "attr_%s" % column_info["name"].lower()


        # 执行反射
        Base.prepare(autoload_with=engine)

    .. versionadded:: 1.4.0b2 :meth:`_events.DDLEvents.column_reflect` 事件
       可以应用于 :class:`_schema.MetaData` 对象。

    .. seealso::

          :meth:`_events.DDLEvents.column_reflect`

          :ref:`mapper_automated_reflection_schemes` - 在 ORM 映射文档中

.. tab:: 英文

    The :class:`_schema.MetaData` and :class:`_schema.Table` objects support an
    event hook :meth:`_events.DDLEvents.column_reflect` that may be used to intercept
    the information reflected about a database column before the :class:`_schema.Column`
    object is constructed.   For example if we wanted to map columns using a
    naming convention such as ``"attr_<columnname>"``, the event could
    be applied as::

        @event.listens_for(Base.metadata, "column_reflect")
        def column_reflect(inspector, table, column_info):
            # set column.key = "attr_<lower_case_name>"
            column_info["key"] = "attr_%s" % column_info["name"].lower()


        # run reflection
        Base.prepare(autoload_with=engine)

    .. versionadded:: 1.4.0b2 the :meth:`_events.DDLEvents.column_reflect` event
       may be applied to a :class:`_schema.MetaData` object.

    .. seealso::

        :meth:`_events.DDLEvents.column_reflect`

        :ref:`mapper_automated_reflection_schemes` - in the ORM mapping documentation


"""  # noqa

from __future__ import annotations

import dataclasses
from typing import Any
from typing import Callable
from typing import cast
from typing import ClassVar
from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional
from typing import overload
from typing import Protocol
from typing import Set
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

from .. import util
from ..orm import backref
from ..orm import declarative_base as _declarative_base
from ..orm import exc as orm_exc
from ..orm import interfaces
from ..orm import relationship
from ..orm.decl_base import _DeferredMapperConfig
from ..orm.mapper import _CONFIGURE_MUTEX
from ..schema import ForeignKeyConstraint
from ..sql import and_
from ..util import Properties

if TYPE_CHECKING:
    from ..engine.base import Engine
    from ..orm.base import RelationshipDirection
    from ..orm.relationships import ORMBackrefArgument
    from ..orm.relationships import Relationship
    from ..sql.schema import Column
    from ..sql.schema import MetaData
    from ..sql.schema import Table
    from ..util import immutabledict


_KT = TypeVar("_KT", bound=Any)
_VT = TypeVar("_VT", bound=Any)


class PythonNameForTableType(Protocol):
    def __call__(self, base: Type[Any], tablename: str, table: Table) -> str: ...


def classname_for_table(
    base: Type[Any],
    tablename: str,
    table: Table,
) -> str:
    """Return the class name that should be used, given the name
    of a table.

    The default implementation is::

        return str(tablename)

    Alternate implementations can be specified using the
    :paramref:`.AutomapBase.prepare.classname_for_table`
    parameter.

    :param base: the :class:`.AutomapBase` class doing the prepare.

    :param tablename: string name of the :class:`_schema.Table`.

    :param table: the :class:`_schema.Table` object itself.

    :return: a string class name.

     .. note::

        In Python 2, the string used for the class name **must** be a
        non-Unicode object, e.g. a ``str()`` object.  The ``.name`` attribute
        of :class:`_schema.Table` is typically a Python unicode subclass,
        so the
        ``str()`` function should be applied to this name, after accounting for
        any non-ASCII characters.

    """
    return str(tablename)


class NameForScalarRelationshipType(Protocol):
    def __call__(
        self,
        base: Type[Any],
        local_cls: Type[Any],
        referred_cls: Type[Any],
        constraint: ForeignKeyConstraint,
    ) -> str: ...


def name_for_scalar_relationship(
    base: Type[Any],
    local_cls: Type[Any],
    referred_cls: Type[Any],
    constraint: ForeignKeyConstraint,
) -> str:
    """Return the attribute name that should be used to refer from one
    class to another, for a scalar object reference.

    The default implementation is::

        return referred_cls.__name__.lower()

    Alternate implementations can be specified using the
    :paramref:`.AutomapBase.prepare.name_for_scalar_relationship`
    parameter.

    :param base: the :class:`.AutomapBase` class doing the prepare.

    :param local_cls: the class to be mapped on the local side.

    :param referred_cls: the class to be mapped on the referring side.

    :param constraint: the :class:`_schema.ForeignKeyConstraint` that is being
     inspected to produce this relationship.

    """
    return referred_cls.__name__.lower()


class NameForCollectionRelationshipType(Protocol):
    def __call__(
        self,
        base: Type[Any],
        local_cls: Type[Any],
        referred_cls: Type[Any],
        constraint: ForeignKeyConstraint,
    ) -> str: ...


def name_for_collection_relationship(
    base: Type[Any],
    local_cls: Type[Any],
    referred_cls: Type[Any],
    constraint: ForeignKeyConstraint,
) -> str:
    """Return the attribute name that should be used to refer from one
    class to another, for a collection reference.

    The default implementation is::

        return referred_cls.__name__.lower() + "_collection"

    Alternate implementations
    can be specified using the
    :paramref:`.AutomapBase.prepare.name_for_collection_relationship`
    parameter.

    :param base: the :class:`.AutomapBase` class doing the prepare.

    :param local_cls: the class to be mapped on the local side.

    :param referred_cls: the class to be mapped on the referring side.

    :param constraint: the :class:`_schema.ForeignKeyConstraint` that is being
     inspected to produce this relationship.

    """
    return referred_cls.__name__.lower() + "_collection"


class GenerateRelationshipType(Protocol):
    @overload
    def __call__(
        self,
        base: Type[Any],
        direction: RelationshipDirection,
        return_fn: Callable[..., Relationship[Any]],
        attrname: str,
        local_cls: Type[Any],
        referred_cls: Type[Any],
        **kw: Any,
    ) -> Relationship[Any]: ...

    @overload
    def __call__(
        self,
        base: Type[Any],
        direction: RelationshipDirection,
        return_fn: Callable[..., ORMBackrefArgument],
        attrname: str,
        local_cls: Type[Any],
        referred_cls: Type[Any],
        **kw: Any,
    ) -> ORMBackrefArgument: ...

    def __call__(
        self,
        base: Type[Any],
        direction: RelationshipDirection,
        return_fn: Union[
            Callable[..., Relationship[Any]], Callable[..., ORMBackrefArgument]
        ],
        attrname: str,
        local_cls: Type[Any],
        referred_cls: Type[Any],
        **kw: Any,
    ) -> Union[ORMBackrefArgument, Relationship[Any]]: ...


@overload
def generate_relationship(
    base: Type[Any],
    direction: RelationshipDirection,
    return_fn: Callable[..., Relationship[Any]],
    attrname: str,
    local_cls: Type[Any],
    referred_cls: Type[Any],
    **kw: Any,
) -> Relationship[Any]: ...


@overload
def generate_relationship(
    base: Type[Any],
    direction: RelationshipDirection,
    return_fn: Callable[..., ORMBackrefArgument],
    attrname: str,
    local_cls: Type[Any],
    referred_cls: Type[Any],
    **kw: Any,
) -> ORMBackrefArgument: ...


def generate_relationship(
    base: Type[Any],
    direction: RelationshipDirection,
    return_fn: Union[
        Callable[..., Relationship[Any]], Callable[..., ORMBackrefArgument]
    ],
    attrname: str,
    local_cls: Type[Any],
    referred_cls: Type[Any],
    **kw: Any,
) -> Union[Relationship[Any], ORMBackrefArgument]:
    r"""Generate a :func:`_orm.relationship` or :func:`.backref`
    on behalf of two
    mapped classes.

    An alternate implementation of this function can be specified using the
    :paramref:`.AutomapBase.prepare.generate_relationship` parameter.

    The default implementation of this function is as follows::

        if return_fn is backref:
            return return_fn(attrname, **kw)
        elif return_fn is relationship:
            return return_fn(referred_cls, **kw)
        else:
            raise TypeError("Unknown relationship function: %s" % return_fn)

    :param base: the :class:`.AutomapBase` class doing the prepare.

    :param direction: indicate the "direction" of the relationship; this will
     be one of :data:`.ONETOMANY`, :data:`.MANYTOONE`, :data:`.MANYTOMANY`.

    :param return_fn: the function that is used by default to create the
     relationship.  This will be either :func:`_orm.relationship` or
     :func:`.backref`.  The :func:`.backref` function's result will be used to
     produce a new :func:`_orm.relationship` in a second step,
     so it is critical
     that user-defined implementations correctly differentiate between the two
     functions, if a custom relationship function is being used.

    :param attrname: the attribute name to which this relationship is being
     assigned. If the value of :paramref:`.generate_relationship.return_fn` is
     the :func:`.backref` function, then this name is the name that is being
     assigned to the backref.

    :param local_cls: the "local" class to which this relationship or backref
     will be locally present.

    :param referred_cls: the "referred" class to which the relationship or
     backref refers to.

    :param \**kw: all additional keyword arguments are passed along to the
     function.

    :return: a :func:`_orm.relationship` or :func:`.backref` construct,
     as dictated
     by the :paramref:`.generate_relationship.return_fn` parameter.

    """

    if return_fn is backref:
        return return_fn(attrname, **kw)
    elif return_fn is relationship:
        return return_fn(referred_cls, **kw)
    else:
        raise TypeError("Unknown relationship function: %s" % return_fn)


ByModuleProperties = Properties[Union["ByModuleProperties", Type[Any]]]


class AutomapBase:
    """Base class for an "automap" schema.

    The :class:`.AutomapBase` class can be compared to the "declarative base"
    class that is produced by the :func:`.declarative.declarative_base`
    function.  In practice, the :class:`.AutomapBase` class is always used
    as a mixin along with an actual declarative base.

    A new subclassable :class:`.AutomapBase` is typically instantiated
    using the :func:`.automap_base` function.

    .. seealso::

        :ref:`automap_toplevel`

    """

    __abstract__ = True

    classes: ClassVar[Properties[Type[Any]]]
    """An instance of :class:`.util.Properties` containing classes.

    This object behaves much like the ``.c`` collection on a table.  Classes
    are present under the name they were given, e.g.::

        Base = automap_base()
        Base.prepare(autoload_with=some_engine)

        User, Address = Base.classes.User, Base.classes.Address

    For class names that overlap with a method name of
    :class:`.util.Properties`, such as ``items()``, the getitem form
    is also supported::

        Item = Base.classes["items"]

    """

    by_module: ClassVar[ByModuleProperties]
    """An instance of :class:`.util.Properties` containing a hierarchal
    structure of dot-separated module names linked to classes.

    This collection is an alternative to the :attr:`.AutomapBase.classes`
    collection that is useful when making use of the
    :paramref:`.AutomapBase.prepare.modulename_for_table` parameter, which will
    apply distinct ``__module__`` attributes to generated classes.

    The default ``__module__`` an automap-generated class is
    ``sqlalchemy.ext.automap``; to access this namespace using
    :attr:`.AutomapBase.by_module` looks like::

        User = Base.by_module.sqlalchemy.ext.automap.User

    If a class had a ``__module__`` of ``mymodule.account``, accessing
    this namespace looks like::

        MyClass = Base.by_module.mymodule.account.MyClass

    .. versionadded:: 2.0

    .. seealso::

        :ref:`automap_by_module`

    """

    metadata: ClassVar[MetaData]
    """Refers to the :class:`_schema.MetaData` collection that will be used
    for new :class:`_schema.Table` objects.

    .. seealso::

        :ref:`orm_declarative_metadata`

    """

    _sa_automapbase_bookkeeping: ClassVar[_Bookkeeping]

    @classmethod
    @util.deprecated_params(
        engine=(
            "2.0",
            "The :paramref:`_automap.AutomapBase.prepare.engine` parameter "
            "is deprecated and will be removed in a future release.  "
            "Please use the "
            ":paramref:`_automap.AutomapBase.prepare.autoload_with` "
            "parameter.",
        ),
        reflect=(
            "2.0",
            "The :paramref:`_automap.AutomapBase.prepare.reflect` "
            "parameter is deprecated and will be removed in a future "
            "release.  Reflection is enabled when "
            ":paramref:`_automap.AutomapBase.prepare.autoload_with` "
            "is passed.",
        ),
    )
    def prepare(
        cls: Type[AutomapBase],
        autoload_with: Optional[Engine] = None,
        engine: Optional[Any] = None,
        reflect: bool = False,
        schema: Optional[str] = None,
        classname_for_table: Optional[PythonNameForTableType] = None,
        modulename_for_table: Optional[PythonNameForTableType] = None,
        collection_class: Optional[Any] = None,
        name_for_scalar_relationship: Optional[NameForScalarRelationshipType] = None,
        name_for_collection_relationship: Optional[
            NameForCollectionRelationshipType
        ] = None,
        generate_relationship: Optional[GenerateRelationshipType] = None,
        reflection_options: Union[
            Dict[_KT, _VT], immutabledict[_KT, _VT]
        ] = util.EMPTY_DICT,
    ) -> None:
        """Extract mapped classes and relationships from the
        :class:`_schema.MetaData` and perform mappings.

        For full documentation and examples see
        :ref:`automap_basic_use`.

        :param autoload_with: an :class:`_engine.Engine` or
         :class:`_engine.Connection` with which
         to perform schema reflection; when specified, the
         :meth:`_schema.MetaData.reflect` method will be invoked within
         the scope of this method.

        :param engine: legacy; use :paramref:`.AutomapBase.autoload_with`.
         Used to indicate the :class:`_engine.Engine` or
         :class:`_engine.Connection` with which to reflect tables with,
         if :paramref:`.AutomapBase.reflect` is True.

        :param reflect: legacy; use :paramref:`.AutomapBase.autoload_with`.
         Indicates that :meth:`_schema.MetaData.reflect` should be invoked.

        :param classname_for_table: callable function which will be used to
         produce new class names, given a table name.  Defaults to
         :func:`.classname_for_table`.

        :param modulename_for_table: callable function which will be used to
         produce the effective ``__module__`` for an internally generated
         class, to allow for multiple classes of the same name in a single
         automap base which would be in different "modules".

         Defaults to ``None``, which will indicate that ``__module__`` will not
         be set explicitly; the Python runtime will use the value
         ``sqlalchemy.ext.automap`` for these classes.

         When assigning ``__module__`` to generated classes, they can be
         accessed based on dot-separated module names using the
         :attr:`.AutomapBase.by_module` collection.   Classes that have
         an explicit ``__module_`` assigned using this hook do **not** get
         placed into the :attr:`.AutomapBase.classes` collection, only
         into :attr:`.AutomapBase.by_module`.

         .. versionadded:: 2.0

         .. seealso::

            :ref:`automap_by_module`

        :param name_for_scalar_relationship: callable function which will be
         used to produce relationship names for scalar relationships.  Defaults
         to :func:`.name_for_scalar_relationship`.

        :param name_for_collection_relationship: callable function which will
         be used to produce relationship names for collection-oriented
         relationships.  Defaults to :func:`.name_for_collection_relationship`.

        :param generate_relationship: callable function which will be used to
         actually generate :func:`_orm.relationship` and :func:`.backref`
         constructs.  Defaults to :func:`.generate_relationship`.

        :param collection_class: the Python collection class that will be used
         when a new :func:`_orm.relationship`
         object is created that represents a
         collection.  Defaults to ``list``.

        :param schema: Schema name to reflect when reflecting tables using
         the :paramref:`.AutomapBase.prepare.autoload_with` parameter. The name
         is passed to the :paramref:`_schema.MetaData.reflect.schema` parameter
         of :meth:`_schema.MetaData.reflect`. When omitted, the default schema
         in use by the database connection is used.

         .. note:: The :paramref:`.AutomapBase.prepare.schema`
            parameter supports reflection of a single schema at a time.
            In order to include tables from many schemas, use
            multiple calls to :meth:`.AutomapBase.prepare`.

            For an overview of multiple-schema automap including the use
            of additional naming conventions to resolve table name
            conflicts, see the section :ref:`automap_by_module`.

            .. versionadded:: 2.0 :meth:`.AutomapBase.prepare` supports being
               directly invoked any number of times, keeping track of tables
               that have already been processed to avoid processing them
               a second time.

        :param reflection_options: When present, this dictionary of options
         will be passed to :meth:`_schema.MetaData.reflect`
         to supply general reflection-specific options like ``only`` and/or
         dialect-specific options like ``oracle_resolve_synonyms``.

         .. versionadded:: 1.4

        """

        for mr in cls.__mro__:
            if "_sa_automapbase_bookkeeping" in mr.__dict__:
                automap_base = cast("Type[AutomapBase]", mr)
                break
        else:
            assert False, "Can't locate automap base in class hierarchy"

        glbls = globals()
        if classname_for_table is None:
            classname_for_table = glbls["classname_for_table"]
        if name_for_scalar_relationship is None:
            name_for_scalar_relationship = glbls["name_for_scalar_relationship"]
        if name_for_collection_relationship is None:
            name_for_collection_relationship = glbls["name_for_collection_relationship"]
        if generate_relationship is None:
            generate_relationship = glbls["generate_relationship"]
        if collection_class is None:
            collection_class = list

        if autoload_with:
            reflect = True

        if engine:
            autoload_with = engine

        if reflect:
            assert autoload_with
            opts = dict(
                schema=schema,
                extend_existing=True,
                autoload_replace=False,
            )
            if reflection_options:
                opts.update(reflection_options)
            cls.metadata.reflect(autoload_with, **opts)  # type: ignore[arg-type]  # noqa: E501

        with _CONFIGURE_MUTEX:
            table_to_map_config: Union[
                Dict[Optional[Table], _DeferredMapperConfig],
                Dict[Table, _DeferredMapperConfig],
            ] = {
                cast("Table", m.local_table): m
                for m in _DeferredMapperConfig.classes_for_base(cls, sort=False)
            }

            many_to_many: List[Tuple[Table, Table, List[ForeignKeyConstraint], Table]]
            many_to_many = []

            bookkeeping = automap_base._sa_automapbase_bookkeeping
            metadata_tables = cls.metadata.tables

            for table_key in set(metadata_tables).difference(bookkeeping.table_keys):
                table = metadata_tables[table_key]
                bookkeeping.table_keys.add(table_key)

                lcl_m2m, rem_m2m, m2m_const = _is_many_to_many(cls, table)
                if lcl_m2m is not None:
                    assert rem_m2m is not None
                    assert m2m_const is not None
                    many_to_many.append((lcl_m2m, rem_m2m, m2m_const, table))
                elif not table.primary_key:
                    continue
                elif table not in table_to_map_config:
                    clsdict: Dict[str, Any] = {"__table__": table}
                    if modulename_for_table is not None:
                        new_module = modulename_for_table(cls, table.name, table)
                        if new_module is not None:
                            clsdict["__module__"] = new_module
                    else:
                        new_module = None

                    newname = classname_for_table(cls, table.name, table)
                    if new_module is None and newname in cls.classes:
                        util.warn(
                            "Ignoring duplicate class name "
                            f"'{newname}' "
                            "received in automap base for table "
                            f"{table.key} without "
                            "``__module__`` being set; consider using the "
                            "``modulename_for_table`` hook"
                        )
                        continue

                    mapped_cls = type(
                        newname,
                        (automap_base,),
                        clsdict,
                    )
                    map_config = _DeferredMapperConfig.config_for_cls(mapped_cls)
                    assert map_config.cls.__name__ == newname
                    if new_module is None:
                        cls.classes[newname] = mapped_cls

                    by_module_properties: ByModuleProperties = cls.by_module
                    for token in map_config.cls.__module__.split("."):
                        if token not in by_module_properties:
                            by_module_properties[token] = util.Properties({})

                        props = by_module_properties[token]

                        # we can assert this because the clsregistry
                        # module would have raised if there was a mismatch
                        # between modules/classes already.
                        # see test_cls_schema_name_conflict
                        assert isinstance(props, Properties)
                        by_module_properties = props

                    by_module_properties[map_config.cls.__name__] = mapped_cls

                    table_to_map_config[table] = map_config

            for map_config in table_to_map_config.values():
                _relationships_for_fks(
                    automap_base,
                    map_config,
                    table_to_map_config,
                    collection_class,
                    name_for_scalar_relationship,
                    name_for_collection_relationship,
                    generate_relationship,
                )

            for lcl_m2m, rem_m2m, m2m_const, table in many_to_many:
                _m2m_relationship(
                    automap_base,
                    lcl_m2m,
                    rem_m2m,
                    m2m_const,
                    table,
                    table_to_map_config,
                    collection_class,
                    name_for_scalar_relationship,
                    name_for_collection_relationship,
                    generate_relationship,
                )

            for map_config in _DeferredMapperConfig.classes_for_base(automap_base):
                map_config.map()

    _sa_decl_prepare = True
    """Indicate that the mapping of classes should be deferred.

    The presence of this attribute name indicates to declarative
    that the call to mapper() should not occur immediately; instead,
    information about the table and attributes to be mapped are gathered
    into an internal structure called _DeferredMapperConfig.  These
    objects can be collected later using classes_for_base(), additional
    mapping decisions can be made, and then the map() method will actually
    apply the mapping.

    The only real reason this deferral of the whole
    thing is needed is to support primary key columns that aren't reflected
    yet when the class is declared; everything else can theoretically be
    added to the mapper later.  However, the _DeferredMapperConfig is a
    nice interface in any case which exists at that not usually exposed point
    at which declarative has the class and the Table but hasn't called
    mapper() yet.

    """

    @classmethod
    def _sa_raise_deferred_config(cls) -> NoReturn:
        raise orm_exc.UnmappedClassError(
            cls,
            msg="Class %s is a subclass of AutomapBase.  "
            "Mappings are not produced until the .prepare() "
            "method is called on the class hierarchy." % orm_exc._safe_cls_name(cls),
        )


@dataclasses.dataclass
class _Bookkeeping:
    __slots__ = ("table_keys",)

    table_keys: Set[str]


def automap_base(declarative_base: Optional[Type[Any]] = None, **kw: Any) -> Any:
    r"""Produce a declarative automap base.

    This function produces a new base class that is a product of the
    :class:`.AutomapBase` class as well a declarative base produced by
    :func:`.declarative.declarative_base`.

    All parameters other than ``declarative_base`` are keyword arguments
    that are passed directly to the :func:`.declarative.declarative_base`
    function.

    :param declarative_base: an existing class produced by
     :func:`.declarative.declarative_base`.  When this is passed, the function
     no longer invokes :func:`.declarative.declarative_base` itself, and all
     other keyword arguments are ignored.

    :param \**kw: keyword arguments are passed along to
     :func:`.declarative.declarative_base`.

    """
    if declarative_base is None:
        Base = _declarative_base(**kw)
    else:
        Base = declarative_base

    return type(
        Base.__name__,
        (AutomapBase, Base),
        {
            "__abstract__": True,
            "classes": util.Properties({}),
            "by_module": util.Properties({}),
            "_sa_automapbase_bookkeeping": _Bookkeeping(set()),
        },
    )


def _is_many_to_many(
    automap_base: Type[Any], table: Table
) -> Tuple[Optional[Table], Optional[Table], Optional[list[ForeignKeyConstraint]]]:
    fk_constraints = [
        const for const in table.constraints if isinstance(const, ForeignKeyConstraint)
    ]
    if len(fk_constraints) != 2:
        return None, None, None

    cols: List[Column[Any]] = sum(
        [
            [fk.parent for fk in fk_constraint.elements]
            for fk_constraint in fk_constraints
        ],
        [],
    )

    if set(cols) != set(table.c):
        return None, None, None

    return (
        fk_constraints[0].elements[0].column.table,
        fk_constraints[1].elements[0].column.table,
        fk_constraints,
    )


def _relationships_for_fks(
    automap_base: Type[Any],
    map_config: _DeferredMapperConfig,
    table_to_map_config: Union[
        Dict[Optional[Table], _DeferredMapperConfig],
        Dict[Table, _DeferredMapperConfig],
    ],
    collection_class: type,
    name_for_scalar_relationship: NameForScalarRelationshipType,
    name_for_collection_relationship: NameForCollectionRelationshipType,
    generate_relationship: GenerateRelationshipType,
) -> None:
    local_table = cast("Optional[Table]", map_config.local_table)
    local_cls = cast(
        "Optional[Type[Any]]", map_config.cls
    )  # derived from a weakref, may be None

    if local_table is None or local_cls is None:
        return
    for constraint in local_table.constraints:
        if isinstance(constraint, ForeignKeyConstraint):
            fks = constraint.elements
            referred_table = fks[0].column.table
            referred_cfg = table_to_map_config.get(referred_table, None)
            if referred_cfg is None:
                continue
            referred_cls = referred_cfg.cls

            if local_cls is not referred_cls and issubclass(local_cls, referred_cls):
                continue

            relationship_name = name_for_scalar_relationship(
                automap_base, local_cls, referred_cls, constraint
            )
            backref_name = name_for_collection_relationship(
                automap_base, referred_cls, local_cls, constraint
            )

            o2m_kws: Dict[str, Union[str, bool]] = {}
            nullable = False not in {fk.parent.nullable for fk in fks}
            if not nullable:
                o2m_kws["cascade"] = "all, delete-orphan"

                if constraint.ondelete and constraint.ondelete.lower() == "cascade":
                    o2m_kws["passive_deletes"] = True
            else:
                if constraint.ondelete and constraint.ondelete.lower() == "set null":
                    o2m_kws["passive_deletes"] = True

            create_backref = backref_name not in referred_cfg.properties

            if relationship_name not in map_config.properties:
                if create_backref:
                    backref_obj = generate_relationship(
                        automap_base,
                        interfaces.ONETOMANY,
                        backref,
                        backref_name,
                        referred_cls,
                        local_cls,
                        collection_class=collection_class,
                        **o2m_kws,
                    )
                else:
                    backref_obj = None
                rel = generate_relationship(
                    automap_base,
                    interfaces.MANYTOONE,
                    relationship,
                    relationship_name,
                    local_cls,
                    referred_cls,
                    foreign_keys=[fk.parent for fk in constraint.elements],
                    backref=backref_obj,
                    remote_side=[fk.column for fk in constraint.elements],
                )
                if rel is not None:
                    map_config.properties[relationship_name] = rel
                    if not create_backref:
                        referred_cfg.properties[
                            backref_name
                        ].back_populates = relationship_name  # type: ignore[union-attr] # noqa: E501
            elif create_backref:
                rel = generate_relationship(
                    automap_base,
                    interfaces.ONETOMANY,
                    relationship,
                    backref_name,
                    referred_cls,
                    local_cls,
                    foreign_keys=[fk.parent for fk in constraint.elements],
                    back_populates=relationship_name,
                    collection_class=collection_class,
                    **o2m_kws,
                )
                if rel is not None:
                    referred_cfg.properties[backref_name] = rel
                    map_config.properties[
                        relationship_name
                    ].back_populates = backref_name  # type: ignore[union-attr]


def _m2m_relationship(
    automap_base: Type[Any],
    lcl_m2m: Table,
    rem_m2m: Table,
    m2m_const: List[ForeignKeyConstraint],
    table: Table,
    table_to_map_config: Union[
        Dict[Optional[Table], _DeferredMapperConfig],
        Dict[Table, _DeferredMapperConfig],
    ],
    collection_class: type,
    name_for_scalar_relationship: NameForCollectionRelationshipType,
    name_for_collection_relationship: NameForCollectionRelationshipType,
    generate_relationship: GenerateRelationshipType,
) -> None:
    map_config = table_to_map_config.get(lcl_m2m, None)
    referred_cfg = table_to_map_config.get(rem_m2m, None)
    if map_config is None or referred_cfg is None:
        return

    local_cls = map_config.cls
    referred_cls = referred_cfg.cls

    relationship_name = name_for_collection_relationship(
        automap_base, local_cls, referred_cls, m2m_const[0]
    )
    backref_name = name_for_collection_relationship(
        automap_base, referred_cls, local_cls, m2m_const[1]
    )

    create_backref = backref_name not in referred_cfg.properties

    if table in table_to_map_config:
        overlaps = "__*"
    else:
        overlaps = None

    if relationship_name not in map_config.properties:
        if create_backref:
            backref_obj = generate_relationship(
                automap_base,
                interfaces.MANYTOMANY,
                backref,
                backref_name,
                referred_cls,
                local_cls,
                collection_class=collection_class,
                overlaps=overlaps,
            )
        else:
            backref_obj = None

        rel = generate_relationship(
            automap_base,
            interfaces.MANYTOMANY,
            relationship,
            relationship_name,
            local_cls,
            referred_cls,
            overlaps=overlaps,
            secondary=table,
            primaryjoin=and_(fk.column == fk.parent for fk in m2m_const[0].elements),  # type: ignore [arg-type]
            secondaryjoin=and_(fk.column == fk.parent for fk in m2m_const[1].elements),  # type: ignore [arg-type]
            backref=backref_obj,
            collection_class=collection_class,
        )
        if rel is not None:
            map_config.properties[relationship_name] = rel

            if not create_backref:
                referred_cfg.properties[backref_name].back_populates = relationship_name  # type: ignore[union-attr] # noqa: E501
    elif create_backref:
        rel = generate_relationship(
            automap_base,
            interfaces.MANYTOMANY,
            relationship,
            backref_name,
            referred_cls,
            local_cls,
            overlaps=overlaps,
            secondary=table,
            primaryjoin=and_(fk.column == fk.parent for fk in m2m_const[1].elements),  # type: ignore [arg-type]
            secondaryjoin=and_(fk.column == fk.parent for fk in m2m_const[0].elements),  # type: ignore [arg-type]
            back_populates=relationship_name,
            collection_class=collection_class,
        )
        if rel is not None:
            referred_cfg.properties[backref_name] = rel
            map_config.properties[relationship_name].back_populates = backref_name  # type: ignore[union-attr]
