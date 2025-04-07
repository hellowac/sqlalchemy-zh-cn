.. _associationproxy_toplevel:

关联代理
=================

Association Proxy

.. module:: sqlalchemy.ext.associationproxy

.. tab:: 中文

    ``associationproxy`` 用于创建跨关系的目标属性的读/写视图。它本质上隐藏了两个端点之间的“中间”属性的使用，可以用于从一组相关对象或标量关系中挑选字段，或减少使用关联对象模式的冗长。
    通过创造性地应用，association proxy 允许构建几乎任何几何形状的复杂集合和字典视图，使用标准的、透明配置的关系模式持久化到数据库中。

.. tab:: 英文

    ``associationproxy`` is used to create a read/write view of a
    target attribute across a relationship.  It essentially conceals
    the usage of a "middle" attribute between two endpoints, and
    can be used to cherry-pick fields from both a collection of
    related objects or scalar relationship. or to reduce the verbosity
    of using the association object pattern.
    Applied creatively, the association proxy allows
    the construction of sophisticated collections and dictionary
    views of virtually any geometry, persisted to the database using
    standard, transparently configured relational patterns.

.. _associationproxy_scalar_collections:

简化标量集合
------------------------------

Simplifying Scalar Collections

.. tab:: 中文

    设想在两个类 ``User`` 和 ``Keyword`` 之间存在一个多对多的映射关系。
    每个 ``User`` 可以拥有任意数量的 ``Keyword`` 对象，反之亦然
    （多对多关系模式详见 :ref:`relationships_many_to_many`）。
    下面的示例展示了该模式的实现方式，与标准用法的唯一区别是，
    在 ``User`` 类中额外添加了一个属性 ``User.keywords``::
    
        from __future__ import annotations
    
        from typing import Final
        from typing import List
    
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
            kw: Mapped[List[Keyword]] = relationship(secondary=lambda: user_keyword_table)
    
            def __init__(self, name: str):
                self.name = name
    
            # 从 'kw' 关系中代理 'keyword' 属性
            keywords: AssociationProxy[List[str]] = association_proxy("kw", "keyword")
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
    
        user_keyword_table: Final[Table] = Table(
            "user_keyword",
            Base.metadata,
            Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
            Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
        )
    
    在上述示例中，:func:`.association_proxy` 应用于 ``User`` 类，用于构建一个基于 ``kw`` 关系的“视图”，
    此视图可以直接访问与每个 ``Keyword`` 对象关联的 ``.keyword`` 字符串值。
    当将字符串添加到该集合时，也会自动创建新的 ``Keyword`` 对象::
    
        >>> user = User("jek")
        >>> user.keywords.append("cheese-inspector")
        >>> user.keywords.append("snack-ninja")
        >>> print(user.keywords)
        ['cheese-inspector', 'snack-ninja']
    
    要理解其工作机制，先看不使用 ``.keywords`` 代理时 ``User`` 与 ``Keyword`` 的行为。
    通常，若要读取或操作与 ``User`` 关联的“keyword”字符串集合，
    就需要遍历每个集合元素并访问其 ``.keyword`` 属性，这种方式较为繁琐。
    下面的例子演示了不使用代理时进行相同操作的写法::
    
        >>> # 不使用 association_proxy 时的等效操作
        >>> user = User("jek")
        >>> user.kw.append(Keyword("cheese-inspector"))
        >>> user.kw.append(Keyword("snack-ninja"))
        >>> print([keyword.keyword for keyword in user.kw])
        ['cheese-inspector', 'snack-ninja']
    
    由 :func:`.association_proxy` 函数创建的 :class:`.AssociationProxy` 对象是一个
    `Python 描述符 <https://docs.python.org/howto/descriptor.html>`_ 实例，
    并不会被 :class:`.Mapper` 认为是“映射”属性。
    因此，它总是直接内联在映射类的类定义中，无论使用的是声明式还是命令式映射方式。
    
    代理通过操作底层已映射的属性或集合来实现功能，
    通过代理进行的更改会立即反映到被映射的属性中，反之亦然。
    底层属性仍然可以正常访问。
    
    在首次访问时，association proxy 会对目标集合进行反射操作，
    以确保其行为与底层集合一致。它会考虑代理的本地属性是集合还是标量引用，
    以及集合是类似 set、list 还是 dict，从而使代理行为与底层属性保持一致。


.. tab:: 英文
    
    Consider a many-to-many mapping between two classes, ``User`` and ``Keyword``.
    Each ``User`` can have any number of ``Keyword`` objects, and vice-versa
    (the many-to-many pattern is described at :ref:`relationships_many_to_many`).
    The example below illustrates this pattern in the same way, with the
    exception of an extra attribute added to the ``User`` class called
    ``User.keywords``::
    
        from __future__ import annotations
    
        from typing import Final
        from typing import List
    
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
            kw: Mapped[List[Keyword]] = relationship(secondary=lambda: user_keyword_table)
    
            def __init__(self, name: str):
                self.name = name
    
            # proxy the 'keyword' attribute from the 'kw' relationship
            keywords: AssociationProxy[List[str]] = association_proxy("kw", "keyword")
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
    
        user_keyword_table: Final[Table] = Table(
            "user_keyword",
            Base.metadata,
            Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
            Column("keyword_id", Integer, ForeignKey("keyword.id"), primary_key=True),
        )
    
    In the above example, :func:`.association_proxy` is applied to the ``User``
    class to produce a "view" of the ``kw`` relationship, which exposes the string
    value of ``.keyword`` associated with each ``Keyword`` object.  It also
    creates new ``Keyword`` objects transparently when strings are added to the
    collection::
    
        >>> user = User("jek")
        >>> user.keywords.append("cheese-inspector")
        >>> user.keywords.append("snack-ninja")
        >>> print(user.keywords)
        ['cheese-inspector', 'snack-ninja']
    
    To understand the mechanics of this, first review the behavior of
    ``User`` and ``Keyword`` without using the ``.keywords`` association proxy.
    Normally, reading and manipulating the collection of "keyword" strings associated
    with ``User`` requires traversal from each collection element to the ``.keyword``
    attribute, which can be awkward.  The example below illustrates the identical
    series of operations applied without using the association proxy::
    
        >>> # identical operations without using the association proxy
        >>> user = User("jek")
        >>> user.kw.append(Keyword("cheese-inspector"))
        >>> user.kw.append(Keyword("snack-ninja"))
        >>> print([keyword.keyword for keyword in user.kw])
        ['cheese-inspector', 'snack-ninja']
    
    The :class:`.AssociationProxy` object produced by the :func:`.association_proxy` function
    is an instance of a `Python descriptor <https://docs.python.org/howto/descriptor.html>`_,
    and is not considered to be "mapped" by the :class:`.Mapper` in any way.  Therefore,
    it's always indicated inline within the class definition of the mapped class,
    regardless of whether Declarative or Imperative mappings are used.
    
    The proxy functions by operating upon the underlying mapped attribute
    or collection in response to operations, and changes made via the proxy are immediately
    apparent in the mapped attribute, as well as vice versa.   The underlying
    attribute remains fully accessible.
    
    When first accessed, the association proxy performs introspection
    operations on the target collection so that its behavior corresponds correctly.
    Details such as if the locally proxied attribute is a collection (as is typical)
    or a scalar reference, as well as if the collection acts like a set, list,
    or dictionary is taken into account, so that the proxy should act just like
    the underlying collection or attribute does.

.. _associationproxy_creator:

创建新值
^^^^^^^^^^^^^^^^^^^^^^

Creation of New Values

.. tab:: 中文

    当 association proxy 拦截到一个列表的 ``append()`` 操作（或 set 的 ``add()``、
    dict 的 ``__setitem__()``，或标量赋值操作）时，
    它会使用中介对象的构造器创建一个新实例，并将所给值作为唯一参数传递。
    在上面的例子中，像这样的操作::
    
        user.keywords.append("cheese-inspector")
    
    会被 association proxy 转换为如下操作::
    
        user.kw.append(Keyword("cheese-inspector"))
    
    这个例子之所以有效，是因为我们将 ``Keyword`` 的构造函数设计为接受一个位置参数 ``keyword``。
    如果不能使用单参数构造器，可以使用 association proxy 的 :paramref:`.association_proxy.creator`
    参数自定义对象创建逻辑。它接受一个可调用对象（如 Python 函数），用于根据传入参数创建新对象。
    下面的示例展示了使用常见的 lambda 函数::
    
        class User(Base):
            ...
    
            # 在 append() 操作中使用 Keyword(keyword=kw)
            keywords: AssociationProxy[List[str]] = association_proxy(
                "kw", "keyword", creator=lambda kw: Keyword(keyword=kw)
            )
    
    ``creator`` 函数在 list 或 set 类型集合中接受一个参数，在标量属性中也是如此；
    而在 dict 类型集合中，它会接收两个参数，即 “key” 和 “value”。
    一个使用该形式的例子可见于 :ref:`proxying_dictionaries`。

.. tab:: 英文

    When a list ``append()`` event (or set ``add()``, dictionary ``__setitem__()``,
    or scalar assignment event) is intercepted by the association proxy, it
    instantiates a new instance of the "intermediary" object using its constructor,
    passing as a single argument the given value. In our example above, an
    operation like::
    
        user.keywords.append("cheese-inspector")
    
    Is translated by the association proxy into the operation::
    
        user.kw.append(Keyword("cheese-inspector"))
    
    The example works here because we have designed the constructor for ``Keyword``
    to accept a single positional argument, ``keyword``. For those cases where a
    single-argument constructor isn't feasible, the association proxy's creational
    behavior can be customized using the :paramref:`.association_proxy.creator`
    argument, which references a callable (i.e. Python function) that will produce
    a new object instance given the singular argument. Below we illustrate this
    using a lambda as is typical::
    
        class User(Base):
            ...
    
            # use Keyword(keyword=kw) on append() events
            keywords: AssociationProxy[List[str]] = association_proxy(
                "kw", "keyword", creator=lambda kw: Keyword(keyword=kw)
            )
    
    The ``creator`` function accepts a single argument in the case of a list-
    or set- based collection, or a scalar attribute.  In the case of a dictionary-based
    collection, it accepts two arguments, "key" and "value".   An example
    of this is below in :ref:`proxying_dictionaries`.

简化关联对象
-------------------------------

Simplifying Association Objects

.. tab:: 中文

    “关联对象”模式是多对多关系的一种扩展形式，相关内容详见 :ref:`association_pattern`。
    在日常使用中，association proxy（关联代理）可以用于屏蔽“关联对象”的存在，让使用更简洁。
    
    假设我们上面定义的 ``user_keyword`` 表中还有其他列需要显式映射，
    但在大多数情况下我们并不需要直接访问这些额外属性。
    下面我们演示一个新的映射方式，引入 ``UserKeywordAssociation`` 类，
    它被映射到前面提到的 ``user_keyword`` 表。
    该类增加了一个额外列 ``special_key``，它是一个我们偶尔会访问的值，但并非默认使用情形。
    我们在 ``User`` 类上创建了一个名为 ``keywords`` 的 association proxy，
    它将 ``user_keyword_associations`` 集合中的 ``UserKeywordAssociation`` 实例
    与其对应的 ``.keyword`` 属性进行桥接::
    
        from __future__ import annotations
    
        from typing import List
        from typing import Optional
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
    
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[List[UserKeywordAssociation]] = relationship(
                back_populates="user",
                cascade="all, delete-orphan",
            )
    
            # 将 "user_keyword_associations" 集合代理到其内部的 "keyword" 属性
            keywords: AssociationProxy[List[Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[Optional[str]] = mapped_column(String(50))
    
            user: Mapped[User] = relationship(back_populates="user_keyword_associations")
    
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column("keyword", String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
            def __repr__(self) -> str:
                return f"Keyword({self.keyword!r})"
    
    通过上述配置，我们可以操作每个 ``User`` 对象的 ``.keywords`` 集合，
    它提供了一个包含 ``Keyword`` 对象的集合，这些对象是通过底层的 ``UserKeywordAssociation`` 实例获取的::
    
        >>> user = User("log")
        >>> for kw in (Keyword("new_from_blammo"), Keyword("its_big")):
        ...     user.keywords.append(kw)
        >>> print(user.keywords)
        [Keyword('new_from_blammo'), Keyword('its_big')]
    
    这个例子与前面 :ref:`associationproxy_scalar_collections` 中的示例形成对比，
    在那里 association proxy 暴露的是字符串集合，而这里是一个组合对象的集合。
    在这种情况下，每次调用 ``.keywords.append()`` 实际等效于::
    
        >>> user.user_keyword_associations.append(
        ...     UserKeywordAssociation(keyword=Keyword("its_heavy"))
        ... )
    
    ``UserKeywordAssociation`` 对象拥有两个在 association proxy 的 ``append()`` 操作中同时赋值的属性：
    ``.keyword``，指向关联的 ``Keyword`` 对象；
    以及 ``.user``，指向当前的 ``User`` 对象。
    首先为 ``.keyword`` 赋值，因为 association proxy 会响应 ``.append()`` 操作创建一个新的 ``UserKeywordAssociation`` 实例，
    并将传入的 ``Keyword`` 实例赋给其 ``.keyword`` 属性。
    随后该 ``UserKeywordAssociation`` 实例被添加到 ``User.user_keyword_associations`` 集合中，
    此时，由于我们在 ``UserKeywordAssociation.user`` 上配置了 ``back_populates``，
    该属性会自动被赋值为当前执行 ``append`` 的父 ``User`` 实例。
    而 ``special_key`` 参数则保持默认值 ``None``。
    
    如果在某些情况下我们希望为 ``special_key`` 设置一个特定值，
    可以显式创建 ``UserKeywordAssociation`` 对象。下面的例子中我们为所有三个属性赋值。
    其中在构造过程中为 ``.user`` 赋值的同时，也将该对象添加到了 ``User.user_keyword_associations`` 集合中（通过关系实现）::
    
        >>> UserKeywordAssociation(
        ...     keyword=Keyword("its_wood"), user=user, special_key="my special key"
        ... )
    
    最终，association proxy 返回的是所有这些操作所代表的 ``Keyword`` 对象的集合::
    
        >>> print(user.keywords)
        [Keyword('new_from_blammo'), Keyword('its_big'), Keyword('its_heavy'), Keyword('its_wood')]


.. tab:: 英文

    The "association object" pattern is an extended form of a many-to-many
    relationship, and is described at :ref:`association_pattern`. Association
    proxies are useful for keeping "association objects" out of the way during
    regular use.
    
    Suppose our ``user_keyword`` table above had additional columns
    which we'd like to map explicitly, but in most cases we don't
    require direct access to these attributes.  Below, we illustrate
    a new mapping which introduces the ``UserKeywordAssociation`` class, which
    is mapped to the ``user_keyword`` table illustrated earlier.
    This class adds an additional column ``special_key``, a value which
    we occasionally want to access, but not in the usual case.   We
    create an association proxy on the ``User`` class called
    ``keywords``, which will bridge the gap from the ``user_keyword_associations``
    collection of ``User`` to the ``.keyword`` attribute present on each
    ``UserKeywordAssociation``::
    
        from __future__ import annotations
    
        from typing import List
        from typing import Optional
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
    
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[List[UserKeywordAssociation]] = relationship(
                back_populates="user",
                cascade="all, delete-orphan",
            )
    
            # association proxy of "user_keyword_associations" collection
            # to "keyword" attribute
            keywords: AssociationProxy[List[Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda keyword_obj: UserKeywordAssociation(keyword=keyword_obj),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[Optional[str]] = mapped_column(String(50))
    
            user: Mapped[User] = relationship(back_populates="user_keyword_associations")
    
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column("keyword", String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
            def __repr__(self) -> str:
                return f"Keyword({self.keyword!r})"
    
    With the above configuration, we can operate upon the ``.keywords`` collection
    of each ``User`` object, each of which exposes a collection of ``Keyword``
    objects that are obtained from the underlying ``UserKeywordAssociation`` elements::
    
        >>> user = User("log")
        >>> for kw in (Keyword("new_from_blammo"), Keyword("its_big")):
        ...     user.keywords.append(kw)
        >>> print(user.keywords)
        [Keyword('new_from_blammo'), Keyword('its_big')]
    
    This example is in contrast to the example illustrated previously at
    :ref:`associationproxy_scalar_collections`, where the association proxy exposed
    a collection of strings, rather than a collection of composed objects.
    In this case, each ``.keywords.append()`` operation is equivalent to::
    
        >>> user.user_keyword_associations.append(
        ...     UserKeywordAssociation(keyword=Keyword("its_heavy"))
        ... )
    
    The ``UserKeywordAssociation`` object has two attributes that are both
    populated within the scope of the ``append()`` operation of the association
    proxy; ``.keyword``, which refers to the
    ``Keyword`` object, and ``.user``, which refers to the ``User`` object.
    The ``.keyword`` attribute is populated first, as the association proxy
    generates a new ``UserKeywordAssociation`` object in response to the ``.append()``
    operation, assigning the given ``Keyword`` instance to the ``.keyword``
    attribute. Then, as the ``UserKeywordAssociation`` object is appended to the
    ``User.user_keyword_associations`` collection, the ``UserKeywordAssociation.user`` attribute,
    configured as ``back_populates`` for ``User.user_keyword_associations``, is initialized
    upon the given ``UserKeywordAssociation`` instance to refer to the parent ``User``
    receiving the append operation.  The ``special_key``
    argument above is left at its default value of ``None``.
    
    For those cases where we do want ``special_key`` to have a value, we
    create the ``UserKeywordAssociation`` object explicitly.  Below we assign all
    three attributes, wherein the assignment of ``.user`` during
    construction, has the effect of appending the new ``UserKeywordAssociation`` to
    the ``User.user_keyword_associations`` collection (via the relationship)::
    
        >>> UserKeywordAssociation(
        ...     keyword=Keyword("its_wood"), user=user, special_key="my special key"
        ... )
    
    The association proxy returns to us a collection of ``Keyword`` objects represented
    by all these operations::
    
        >>> print(user.keywords)
        [Keyword('new_from_blammo'), Keyword('its_big'), Keyword('its_heavy'), Keyword('its_wood')]

.. _proxying_dictionaries:

代理到基于字典的集合
----------------------------------------

Proxying to Dictionary Based Collections

.. tab:: 中文

    association proxy（关联代理）同样可以代理到基于字典的集合上。  
    在 SQLAlchemy 映射中，通常使用 :func:`.attribute_keyed_dict` 集合类型来创建字典集合，  
    并且还可以使用 :ref:`dictionary_collections` 中描述的扩展技术。
    
    当 association proxy 检测到目标是基于字典的集合时，它会自动调整自身的行为。
    当新值被添加到字典中时，association proxy 会在实例化中间对象时向创建函数传递两个参数（键和值），而不是一个参数。
    这个创建函数默认是中间类的构造器，也可以通过 ``creator`` 参数进行自定义。
    
    下面我们修改前面的 ``UserKeywordAssociation`` 示例，
    将 ``User.user_keyword_associations`` 集合映射为一个字典，  
    该字典以 ``UserKeywordAssociation.special_key`` 字段作为键。
    同时我们在 ``User.keywords`` proxy 上应用了一个 ``creator`` 参数，
    以便在添加新元素到字典时，值可以正确赋值::
    
        from __future__ import annotations
        from typing import Dict
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            # user/user_keyword_associations 关系，使用字典映射，
            # 以 "special_key" 为字典中的键。
            user_keyword_associations: Mapped[Dict[str, UserKeywordAssociation]] = relationship(
                back_populates="user",
                collection_class=attribute_keyed_dict("special_key"),
                cascade="all, delete-orphan",
            )
            # proxy 到 'user_keyword_associations'，在创建过程中实例化
            # UserKeywordAssociation，并将键赋给 'special_key'，值赋给 'keyword'。
            keywords: AssociationProxy[Dict[str, Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda k, v: UserKeywordAssociation(special_key=k, keyword=v),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str]
    
            user: Mapped[User] = relationship(
                back_populates="user_keyword_associations",
            )
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
            def __repr__(self) -> str:
                return f"Keyword({self.keyword!r})"
    
    我们可以将 ``.keywords`` 集合表现为一个字典，
    其中将 ``UserKeywordAssociation.special_key`` 的值映射为 ``Keyword`` 对象::
    
        >>> user = User("log")
    
        >>> user.keywords["sk1"] = Keyword("kw1")
        >>> user.keywords["sk2"] = Keyword("kw2")
    
        >>> print(user.keywords)
        {'sk1': Keyword('kw1'), 'sk2': Keyword('kw2')}


.. tab:: 英文

    The association proxy can proxy to dictionary based collections as well.   SQLAlchemy
    mappings usually use the :func:`.attribute_keyed_dict` collection type to
    create dictionary collections, as well as the extended techniques described in
    :ref:`dictionary_collections`.
    
    The association proxy adjusts its behavior when it detects the usage of a
    dictionary-based collection. When new values are added to the dictionary, the
    association proxy instantiates the intermediary object by passing two
    arguments to the creation function instead of one, the key and the value. As
    always, this creation function defaults to the constructor of the intermediary
    class, and can be customized using the ``creator`` argument.
    
    Below, we modify our ``UserKeywordAssociation`` example such that the ``User.user_keyword_associations``
    collection will now be mapped using a dictionary, where the ``UserKeywordAssociation.special_key``
    argument will be used as the key for the dictionary.   We also apply a ``creator``
    argument to the ``User.keywords`` proxy so that these values are assigned appropriately
    when new elements are added to the dictionary::
    
        from __future__ import annotations
        from typing import Dict
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            # user/user_keyword_associations relationship, mapping
            # user_keyword_associations with a dictionary against "special_key" as key.
            user_keyword_associations: Mapped[Dict[str, UserKeywordAssociation]] = relationship(
                back_populates="user",
                collection_class=attribute_keyed_dict("special_key"),
                cascade="all, delete-orphan",
            )
            # proxy to 'user_keyword_associations', instantiating
            # UserKeywordAssociation assigning the new key to 'special_key',
            # values to 'keyword'.
            keywords: AssociationProxy[Dict[str, Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda k, v: UserKeywordAssociation(special_key=k, keyword=v),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str]
    
            user: Mapped[User] = relationship(
                back_populates="user_keyword_associations",
            )
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
            def __repr__(self) -> str:
                return f"Keyword({self.keyword!r})"
    
    We illustrate the ``.keywords`` collection as a dictionary, mapping the
    ``UserKeywordAssociation.special_key`` value to ``Keyword`` objects::
    
        >>> user = User("log")
    
        >>> user.keywords["sk1"] = Keyword("kw1")
        >>> user.keywords["sk2"] = Keyword("kw2")
    
        >>> print(user.keywords)
        {'sk1': Keyword('kw1'), 'sk2': Keyword('kw2')}

.. _composite_association_proxy:

复合关联代理
-----------------------------

Composite Association Proxies

.. tab:: 中文

    考虑到我们之前关于从关系到标量属性的代理、跨关联对象的代理以及字典代理的示例，
    我们可以将这三种技术结合起来，为 ``User`` 提供一个 ``keywords`` 字典，
    该字典严格处理将 ``special_key`` 的字符串值映射到字符串 ``keyword``。
    ``UserKeywordAssociation`` 和 ``Keyword`` 类完全被隐藏。
    这是通过在 ``User`` 上构建一个关联代理来实现的，该代理指向
    ``UserKeywordAssociation`` 上的一个关联代理::
    
        from __future__ import annotations
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[Dict[str, UserKeywordAssociation]] = relationship(
                back_populates="user",
                collection_class=attribute_keyed_dict("special_key"),
                cascade="all, delete-orphan",
            )
            # 与基本字典示例中的 'user_keyword_associations'->'keyword' 相同的代理。
            keywords: AssociationProxy[Dict[str, str]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda k, v: UserKeywordAssociation(special_key=k, keyword=v),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str] = mapped_column(String(64))
            user: Mapped[User] = relationship(
                back_populates="user_keyword_associations",
            )
    
            # 与 Keyword 的关系现在称为 'kw'
            kw: Mapped[Keyword] = relationship()
    
            # 'keyword' 现在是指向 'Keyword' 中 'keyword' 属性的代理
            keyword: AssociationProxy[Dict[str, str]] = association_proxy("kw", "keyword")
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
    ``User.keywords`` 现在是一个从字符串到字符串的字典，
    其中 ``UserKeywordAssociation`` 和 ``Keyword`` 对象会通过关联代理透明地创建和删除。
    在下面的示例中，我们展示了赋值操作符的用法，该操作符也由关联代理适当处理，
    以一次将字典值应用到集合中::
    
        >>> user = User("log")
        >>> user.keywords = {"sk1": "kw1", "sk2": "kw2"}
        >>> print(user.keywords)
        {'sk1': 'kw1', 'sk2': 'kw2'}
    
        >>> user.keywords["sk3"] = "kw3"
        >>> del user.keywords["sk2"]
        >>> print(user.keywords)
        {'sk1': 'kw1', 'sk3': 'kw3'}
    
        >>> # 展示非代理使用
        ... print(user.user_keyword_associations["sk3"].kw)
        <__main__.Keyword object at 0x12ceb90>
    
    我们上面示例的一个警告是，因为 ``Keyword`` 对象是在每次字典设置操作时创建的，
    该示例未能保持 ``Keyword`` 对象在其字符串名称上的唯一性，这是此类标记场景中的典型要求。
    对于这种用例，推荐使用 `UniqueObject <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject>`_ 配方，或者
    类似的创建策略，这将对 ``Keyword`` 类的构造函数应用 "先查找，后创建" 策略，
    以便在给定名称已存在时返回已经存在的 ``Keyword`` 对象。


.. tab:: 英文

    Given our previous examples of proxying from relationship to scalar
    attribute, proxying across an association object, and proxying dictionaries,
    we can combine all three techniques together to give ``User``
    a ``keywords`` dictionary that deals strictly with the string value
    of ``special_key`` mapped to the string ``keyword``.  Both the ``UserKeywordAssociation``
    and ``Keyword`` classes are entirely concealed.  This is achieved by building
    an association proxy on ``User`` that refers to an association proxy
    present on ``UserKeywordAssociation``::
    
        from __future__ import annotations
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[Dict[str, UserKeywordAssociation]] = relationship(
                back_populates="user",
                collection_class=attribute_keyed_dict("special_key"),
                cascade="all, delete-orphan",
            )
            # the same 'user_keyword_associations'->'keyword' proxy as in
            # the basic dictionary example.
            keywords: AssociationProxy[Dict[str, str]] = association_proxy(
                "user_keyword_associations",
                "keyword",
                creator=lambda k, v: UserKeywordAssociation(special_key=k, keyword=v),
            )
    
            def __init__(self, name: str):
                self.name = name
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str] = mapped_column(String(64))
            user: Mapped[User] = relationship(
                back_populates="user_keyword_associations",
            )
    
            # the relationship to Keyword is now called
            # 'kw'
            kw: Mapped[Keyword] = relationship()
    
            # 'keyword' is changed to be a proxy to the
            # 'keyword' attribute of 'Keyword'
            keyword: AssociationProxy[Dict[str, str]] = association_proxy("kw", "keyword")
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
            def __init__(self, keyword: str):
                self.keyword = keyword
    
    ``User.keywords`` is now a dictionary of string to string, where
    ``UserKeywordAssociation`` and ``Keyword`` objects are created and removed for us
    transparently using the association proxy. In the example below, we illustrate
    usage of the assignment operator, also appropriately handled by the
    association proxy, to apply a dictionary value to the collection at once::
    
        >>> user = User("log")
        >>> user.keywords = {"sk1": "kw1", "sk2": "kw2"}
        >>> print(user.keywords)
        {'sk1': 'kw1', 'sk2': 'kw2'}
    
        >>> user.keywords["sk3"] = "kw3"
        >>> del user.keywords["sk2"]
        >>> print(user.keywords)
        {'sk1': 'kw1', 'sk3': 'kw3'}
    
        >>> # illustrate un-proxied usage
        ... print(user.user_keyword_associations["sk3"].kw)
        <__main__.Keyword object at 0x12ceb90>
    
    One caveat with our example above is that because ``Keyword`` objects are created
    for each dictionary set operation, the example fails to maintain uniqueness for
    the ``Keyword`` objects on their string name, which is a typical requirement for
    a tagging scenario such as this one.  For this use case the recipe
    `UniqueObject <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/UniqueObject>`_, or
    a comparable creational strategy, is
    recommended, which will apply a "lookup first, then create" strategy to the constructor
    of the ``Keyword`` class, so that an already existing ``Keyword`` is returned if the
    given name is already present.

使用关联代理进行查询
---------------------------------

Querying with Association Proxies

.. tab:: 中文

    `:class: .AssociationProxy` 提供了简单的 SQL 构建功能，
    这些功能在类级别工作，与其他 ORM 映射的属性类似，
    并提供了主要基于 SQL ``EXISTS`` 关键字的基本过滤支持。
    
    .. note:: 关联代理扩展的主要目的是允许
       改进对已经加载的映射对象实例的持久化和对象访问模式。
       类绑定的查询功能用途有限，不会替代在构建包含 JOIN、预加载
       选项等 SQL 查询时引用底层属性的需求。
    
    在本节中，假设一个类既有指向列的关联代理，也有指向相关对象的关联代理，
    如下方的示例映射所示::
    
        from __future__ import annotations
        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
        from sqlalchemy.orm import DeclarativeBase, relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
        from sqlalchemy.orm.collections import Mapped
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[UserKeywordAssociation] = relationship(
                cascade="all, delete-orphan",
            )
    
            # 面向对象的关联代理
            keywords: AssociationProxy[List[Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
            )
    
            # 面向列的关联代理
            special_keys: AssociationProxy[List[str]] = association_proxy(
                "user_keyword_associations", "special_key"
            )
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str] = mapped_column(String(64))
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
    生成的 SQL 采用与 ``EXISTS`` SQL 操作符相关的子查询形式，
    因此可以在 WHERE 子句中使用，而无需对封闭查询进行额外的修改。
    如果关联代理的直接目标是 **映射列表达式**，
    可以使用标准的列操作符，这些操作符将嵌入子查询中。
    例如，直接的等式操作符：
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.special_keys == "jek")))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND user_keyword.special_key = :special_key_1)
    
    LIKE 操作符：
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.special_keys.like("%jek"))))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND user_keyword.special_key LIKE :special_key_1)
    
    对于关联代理，其中直接目标是 **相关对象或集合，
    或相关对象上的另一个关联代理或属性**，可以使用面向关系的操作符，
    如 :meth:`_orm.PropComparator.has` 和 :meth:`_orm.PropComparator.any`。
    ``User.keywords`` 属性实际上是两个关联代理的链接，
    因此在使用此代理生成 SQL 语句时，我们得到两个层次的 EXISTS 子查询：
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.keywords.any(Keyword.keyword == "jek"))))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND (EXISTS (SELECT 1
        FROM keyword
        WHERE keyword.id = user_keyword.keyword_id AND keyword.keyword = :keyword_1)))
    
    这不是最有效的 SQL 形式，因此虽然关联代理在快速生成 WHERE 条件时非常方便，
    但应该检查 SQL 结果，并在最佳使用时将其 "展开" 为显式的 JOIN 条件，
    特别是在将多个关联代理串联在一起时。

.. tab:: 英文

    The :class:`.AssociationProxy` features simple SQL construction capabilities
    which work at the class level in a similar way as other ORM-mapped attributes,
    and provide rudimentary filtering support primarily based on the
    SQL ``EXISTS`` keyword.
    
    
    .. note:: The primary purpose of the association proxy extension is to allow
       for improved persistence and object-access patterns with mapped object
       instances that are already loaded.  The class-bound querying feature
       is of limited use and will not replace the need to refer to the underlying
       attributes when constructing SQL queries with JOINs, eager loading
       options, etc.
    
    For this section, assume a class with both an association proxy
    that refers to a column, as well as an association proxy that refers
    to a related object, as in the example mapping below::
    
        from __future__ import annotations
        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
        from sqlalchemy.orm import DeclarativeBase, relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
        from sqlalchemy.orm.collections import Mapped
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            user_keyword_associations: Mapped[UserKeywordAssociation] = relationship(
                cascade="all, delete-orphan",
            )
    
            # object-targeted association proxy
            keywords: AssociationProxy[List[Keyword]] = association_proxy(
                "user_keyword_associations",
                "keyword",
            )
    
            # column-targeted association proxy
            special_keys: AssociationProxy[List[str]] = association_proxy(
                "user_keyword_associations", "special_key"
            )
    
    
        class UserKeywordAssociation(Base):
            __tablename__ = "user_keyword"
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
            keyword_id: Mapped[int] = mapped_column(ForeignKey("keyword.id"), primary_key=True)
            special_key: Mapped[str] = mapped_column(String(64))
            keyword: Mapped[Keyword] = relationship()
    
    
        class Keyword(Base):
            __tablename__ = "keyword"
            id: Mapped[int] = mapped_column(primary_key=True)
            keyword: Mapped[str] = mapped_column(String(64))
    
    The SQL generated takes the form of a correlated subquery against
    the EXISTS SQL operator so that it can be used in a WHERE clause without
    the need for additional modifications to the enclosing query.  If the
    immediate target of an association proxy is a **mapped column expression**,
    standard column operators can be used which will be embedded in the subquery.
    For example a straight equality operator:
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.special_keys == "jek")))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND user_keyword.special_key = :special_key_1)
    
    a LIKE operator:
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.special_keys.like("%jek"))))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND user_keyword.special_key LIKE :special_key_1)
    
    For association proxies where the immediate target is a **related object or collection,
    or another association proxy or attribute on the related object**, relationship-oriented
    operators can be used instead, such as :meth:`_orm.PropComparator.has` and
    :meth:`_orm.PropComparator.any`.   The ``User.keywords`` attribute is in fact
    two association proxies linked together, so when using this proxy for generating
    SQL phrases, we get two levels of EXISTS subqueries:
    
    .. sourcecode:: pycon+sql
    
        >>> print(session.scalars(select(User).where(User.keywords.any(Keyword.keyword == "jek"))))
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name
        FROM "user"
        WHERE EXISTS (SELECT 1
        FROM user_keyword
        WHERE "user".id = user_keyword.user_id AND (EXISTS (SELECT 1
        FROM keyword
        WHERE keyword.id = user_keyword.keyword_id AND keyword.keyword = :keyword_1)))
    
    This is not the most efficient form of SQL, so while association proxies can be
    convenient for generating WHERE criteria quickly, SQL results should be
    inspected and "unrolled" into explicit JOIN criteria for best use, especially
    when chaining association proxies together.

.. _cascade_scalar_deletes:

级联标量删除
------------------------

Cascading Scalar Deletes

.. tab:: 中文

    给定如下映射::
    
        from __future__ import annotations
        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
        from sqlalchemy.orm import DeclarativeBase, relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
        from sqlalchemy.orm.collections import Mapped
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class A(Base):
            __tablename__ = "test_a"
            id: Mapped[int] = mapped_column(primary_key=True)
            ab: Mapped[AB] = relationship(uselist=False)
            b: AssociationProxy[B] = association_proxy(
                "ab", "b", creator=lambda b: AB(b=b), cascade_scalar_deletes=True
            )
    
    
        class B(Base):
            __tablename__ = "test_b"
            id: Mapped[int] = mapped_column(primary_key=True)
    
    
        class AB(Base):
            __tablename__ = "test_ab"
            a_id: Mapped[int] = mapped_column(ForeignKey(A.id), primary_key=True)
            b_id: Mapped[int] = mapped_column(ForeignKey(B.id), primary_key=True)
    
            b: Mapped[B] = relationship()
    
    对 ``A.b`` 进行赋值将生成一个 ``AB`` 对象::
    
        a.b = B()
    
    ``A.b`` 关联是标量的，并且使用了参数
    :paramref:`.AssociationProxy.cascade_scalar_deletes`。当启用此参数时，
    将 ``A.b`` 设置为 ``None`` 也会删除 ``A.ab``::
    
        a.b = None
        assert a.ab is None
    
    当未设置 :paramref:`.AssociationProxy.cascade_scalar_deletes` 时，
    上述的关联对象 ``a.ab`` 将保持不变。
    
    请注意，这不是面向集合的关联代理的行为；
    在这种情况下，当代理集合中的成员被移除时，
    中介关联对象始终会被删除。是否删除行取决于关系的级联设置。
    
    .. seealso::
    
        :ref:`unitofwork_cascades`

.. tab:: 英文

    Given a mapping as::
    
        from __future__ import annotations
        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.ext.associationproxy import association_proxy, AssociationProxy
        from sqlalchemy.orm import DeclarativeBase, relationship
        from sqlalchemy.orm.collections import attribute_keyed_dict
        from sqlalchemy.orm.collections import Mapped
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class A(Base):
            __tablename__ = "test_a"
            id: Mapped[int] = mapped_column(primary_key=True)
            ab: Mapped[AB] = relationship(uselist=False)
            b: AssociationProxy[B] = association_proxy(
                "ab", "b", creator=lambda b: AB(b=b), cascade_scalar_deletes=True
            )
    
    
        class B(Base):
            __tablename__ = "test_b"
            id: Mapped[int] = mapped_column(primary_key=True)
    
    
        class AB(Base):
            __tablename__ = "test_ab"
            a_id: Mapped[int] = mapped_column(ForeignKey(A.id), primary_key=True)
            b_id: Mapped[int] = mapped_column(ForeignKey(B.id), primary_key=True)
    
            b: Mapped[B] = relationship()
    
    An assignment to ``A.b`` will generate an ``AB`` object::
    
        a.b = B()
    
    The ``A.b`` association is scalar, and includes use of the parameter
    :paramref:`.AssociationProxy.cascade_scalar_deletes`.  When this parameter
    is enabled, setting ``A.b``
    to ``None`` will remove ``A.ab`` as well::
    
        a.b = None
        assert a.ab is None
    
    When :paramref:`.AssociationProxy.cascade_scalar_deletes` is not set,
    the association object ``a.ab`` above would remain in place.
    
    Note that this is not the behavior for collection-based association proxies;
    in that case, the intermediary association object is always removed when
    members of the proxied collection are removed.  Whether or not the row is
    deleted depends on the relationship cascade setting.
    
    .. seealso::
    
        :ref:`unitofwork_cascades`

标量关系
--------------------

Scalar Relationships

.. tab:: 中文

    下面的示例演示了在一对多关系的多方使用关联代理，
    访问标量对象的属性::
    
        from __future__ import annotations
    
        from typing import List
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class Recipe(Base):
            __tablename__ = "recipe"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            steps: Mapped[List[Step]] = relationship(back_populates="recipe")
            step_descriptions: AssociationProxy[List[str]] = association_proxy(
                "steps", "description"
            )
    
    
        class Step(Base):
            __tablename__ = "step"
            id: Mapped[int] = mapped_column(primary_key=True)
            description: Mapped[str]
            recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
            recipe: Mapped[Recipe] = relationship(back_populates="steps")
    
            recipe_name: AssociationProxy[str] = association_proxy("recipe", "name")
    
            def __init__(self, description: str) -> None:
                self.description = description
    
    
        my_snack = Recipe(
            name="afternoon snack",
            step_descriptions=[
                "slice bread",
                "spread peanut butted",
                "eat sandwich",
            ],
        )
    
    可以使用以下方式打印 ``my_snack`` 的步骤总结::
    
        >>> for i, step in enumerate(my_snack.steps, 1):
        ...     print(f"Step {i} of {step.recipe_name!r}: {step.description}")
        Step 1 of 'afternoon snack': slice bread
        Step 2 of 'afternoon snack': spread peanut butted
        Step 3 of 'afternoon snack': eat sandwich


.. tab:: 英文

    The example below illustrates the use of the association proxy on the many
    side of of a one-to-many relationship, accessing attributes of a scalar
    object::
    
        from __future__ import annotations
    
        from typing import List
    
        from sqlalchemy import ForeignKey
        from sqlalchemy import String
        from sqlalchemy.ext.associationproxy import association_proxy
        from sqlalchemy.ext.associationproxy import AssociationProxy
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class Recipe(Base):
            __tablename__ = "recipe"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(64))
    
            steps: Mapped[List[Step]] = relationship(back_populates="recipe")
            step_descriptions: AssociationProxy[List[str]] = association_proxy(
                "steps", "description"
            )
    
    
        class Step(Base):
            __tablename__ = "step"
            id: Mapped[int] = mapped_column(primary_key=True)
            description: Mapped[str]
            recipe_id: Mapped[int] = mapped_column(ForeignKey("recipe.id"))
            recipe: Mapped[Recipe] = relationship(back_populates="steps")
    
            recipe_name: AssociationProxy[str] = association_proxy("recipe", "name")
    
            def __init__(self, description: str) -> None:
                self.description = description
    
    
        my_snack = Recipe(
            name="afternoon snack",
            step_descriptions=[
                "slice bread",
                "spread peanut butted",
                "eat sandwich",
            ],
        )
    
    A summary of the steps of ``my_snack`` can be printed using::
    
        >>> for i, step in enumerate(my_snack.steps, 1):
        ...     print(f"Step {i} of {step.recipe_name!r}: {step.description}")
        Step 1 of 'afternoon snack': slice bread
        Step 2 of 'afternoon snack': spread peanut butted
        Step 3 of 'afternoon snack': eat sandwich

API 文档
-----------------

API Documentation

.. tab:: 中文

.. tab:: 英文

.. autofunction:: association_proxy

.. autoclass:: AssociationProxy
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: AssociationProxyInstance
   :members:
   :undoc-members:
   :inherited-members:

.. autoclass:: ObjectAssociationProxyInstance
   :members:
   :inherited-members:

.. autoclass:: ColumnAssociationProxyInstance
   :members:
   :inherited-members:

.. autoclass:: AssociationProxyExtensionType
   :members:
