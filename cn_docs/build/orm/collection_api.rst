.. highlight:: python

.. _custom_collections_toplevel:

.. currentmodule:: sqlalchemy.orm

========================================
集合自定义和 API 详细信息
========================================

Collection Customization and API Details

.. tab:: 中文

    :func:`_orm.relationship` 函数定义了两个类之间的链接。当链接定义为一对多或多对多关系时，加载和操作对象时，它表示为一个 Python 集合。本节介绍了有关集合配置和技术的其他信息。

.. tab:: 英文

    The :func:`_orm.relationship` function defines a linkage between two classes. When the linkage defines a one-to-many or many-to-many relationship, it's represented as a Python collection when objects are loaded and manipulated. This section presents additional information about collection configuration and techniques.



.. _custom_collections:

自定义集合访问
-----------------------------

Customizing Collection Access

.. tab:: 中文

.. tab:: 英文

Mapping a one-to-many or many-to-many relationship results in a collection of
values accessible through an attribute on the parent instance.   The two
common collection types for these are ``list`` and ``set``, which in
:ref:`Declarative <orm_declarative_styles_toplevel>` mappings that use
:class:`_orm.Mapped` is established by using the collection type within
the :class:`_orm.Mapped` container, as demonstrated in the ``Parent.children`` collection
below where ``list`` is used::

    from sqlalchemy import ForeignKey

    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy.orm import Mapped
    from sqlalchemy.orm import mapped_column
    from sqlalchemy.orm import relationship


    class Base(DeclarativeBase):
        pass


    class Parent(Base):
        __tablename__ = "parent"

        parent_id: Mapped[int] = mapped_column(primary_key=True)

        # use a list
        children: Mapped[list["Child"]] = relationship()


    class Child(Base):
        __tablename__ = "child"

        child_id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))

Or for a ``set``, illustrated in the same
``Parent.children`` collection::

    from sqlalchemy import ForeignKey

    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy.orm import Mapped
    from sqlalchemy.orm import mapped_column
    from sqlalchemy.orm import relationship


    class Base(DeclarativeBase):
        pass


    class Parent(Base):
        __tablename__ = "parent"

        parent_id: Mapped[int] = mapped_column(primary_key=True)

        # use a set
        children: Mapped[set["Child"]] = relationship()


    class Child(Base):
        __tablename__ = "child"

        child_id: Mapped[int] = mapped_column(primary_key=True)
        parent_id: Mapped[int] = mapped_column(ForeignKey("parent.id"))

When using mappings without the :class:`_orm.Mapped` annotation, such as when
using :ref:`imperative mappings <orm_imperative_mapping>` or untyped
Python code, as well as in a few special cases, the collection class for a
:func:`_orm.relationship` can always be specified directly using the
:paramref:`_orm.relationship.collection_class` parameter::

    # non-annotated mapping


    class Parent(Base):
        __tablename__ = "parent"

        parent_id = mapped_column(Integer, primary_key=True)

        children = relationship("Child", collection_class=set)


    class Child(Base):
        __tablename__ = "child"

        child_id = mapped_column(Integer, primary_key=True)
        parent_id = mapped_column(ForeignKey("parent.id"))

In the absence of :paramref:`_orm.relationship.collection_class`
or :class:`_orm.Mapped`, the default collection type is ``list``.

Beyond ``list`` and ``set`` builtins, there is also support for two varieties of
dictionary, described below at :ref:`orm_dictionary_collection`. There is also
support for any arbitrary mutable sequence type can be set up as the target
collection, with some additional configuration steps; this is described in the
section :ref:`orm_custom_collection`.


.. _orm_dictionary_collection:

字典集合
~~~~~~~~~~~~~~~~~~~~~~

Dictionary Collections

.. tab:: 中文

    在将字典作为集合使用时，需要额外的一些细节。
    这是因为对象总是以列表的形式从数据库加载，因此必须提供一种键生成策略以正确地填充字典。
    :func:`.attribute_keyed_dict` 函数是实现简单字典集合最常用的方式。
    它会生成一个字典类，该类会将映射类的某个特定属性作为键。
    下面我们映射一个包含以 ``Note.keyword`` 属性为键的 ``Note`` 项字典的 ``Item`` 类。
    当使用 :func:`.attribute_keyed_dict` 时，:class:`_orm.Mapped` 注解可以使用 :class:`_orm.KeyFuncDict` 或普通的 ``dict`` 来标注类型，如下例所示。
    但在此情况下，必须指定 :paramref:`_orm.relationship.collection_class` 参数，以便对 :func:`.attribute_keyed_dict` 进行适当的参数化::

        from typing import Dict
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import attribute_keyed_dict
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=attribute_keyed_dict("keyword"),
                cascade="all, delete-orphan",
            )


        class Note(Base):
            __tablename__ = "note"

            id: Mapped[int] = mapped_column(primary_key=True)
            item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
            keyword: Mapped[str]
            text: Mapped[Optional[str]]

            def __init__(self, keyword: str, text: str):
                self.keyword = keyword
                self.text = text

    ``Item.notes`` 此时就是一个字典::

        >>> item = Item()
        >>> item.notes["a"] = Note("a", "atext")
        >>> item.notes.items()
        {'a': <__main__.Note object at 0x2eaaf0>}

    :func:`.attribute_keyed_dict` 会确保每个 ``Note`` 的 ``.keyword`` 属性与字典中的键保持一致。
    例如，在为 ``Item.notes`` 赋值时，我们提供的字典键必须与实际 ``Note`` 对象的键一致::

        item = Item()
        item.notes = {
            "a": Note("a", "atext"),
            "b": Note("b", "btext"),
        }

    :func:`.attribute_keyed_dict` 用作键的属性甚至可以完全不映射！
    使用普通的 Python ``@property`` 可以允许对象的几乎任何细节或其组合作为键。
    如下例中我们将键定义为 ``Note.keyword`` 与 ``Note.text`` 字段前十个字符组成的元组::

        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=attribute_keyed_dict("note_key"),
                back_populates="item",
                cascade="all, delete-orphan",
            )


        class Note(Base):
            __tablename__ = "note"

            id: Mapped[int] = mapped_column(primary_key=True)
            item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
            keyword: Mapped[str]
            text: Mapped[str]

            item: Mapped["Item"] = relationship()

            @property
            def note_key(self):
                return (self.keyword, self.text[0:10])

            def __init__(self, keyword: str, text: str):
                self.keyword = keyword
                self.text = text

    在上例中，我们添加了一个 ``Note.item`` 关系，并配置为双向的 :paramref:`_orm.relationship.back_populates`。
    当赋值给这个反向关系时，该 ``Note`` 会自动添加到 ``Item.notes`` 字典中，并且键会被自动生成::

        >>> item = Item()
        >>> n1 = Note("a", "atext")
        >>> n1.item = item
        >>> item.notes
        {('a', 'atext'): <__main__.Note object at 0x2eaaf0>}

    其他内置字典类型还包括 :func:`.column_keyed_dict`，它与 :func:`.attribute_keyed_dict` 类似，
    但接收的是 :class:`_schema.Column` 对象::

        from sqlalchemy.orm import column_keyed_dict


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=column_keyed_dict(Note.__table__.c.keyword),
                cascade="all, delete-orphan",
            )

    还有 :func:`.mapped_collection`，它接受任意可调用函数。
    但通常更容易使用 :func:`.attribute_keyed_dict` 搭配 ``@property``，如前所述::

        from sqlalchemy.orm import mapped_collection


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=mapped_collection(lambda note: note.text[0:10]),
                cascade="all, delete-orphan",
            )

    字典映射常与 “关联代理(Association Proxy)” 扩展结合使用，以生成简化的字典视图。
    参见 :ref:`proxying_dictionaries` 和 :ref:`composite_association_proxy` 获取示例。

.. tab:: 英文

    A little extra detail is needed when using a dictionary as a collection.
    This because objects are always loaded from the database as lists, and a key-generation
    strategy must be available to populate the dictionary correctly.  The
    :func:`.attribute_keyed_dict` function is by far the most common way
    to achieve a simple dictionary collection.  It produces a dictionary class that will apply a particular attribute
    of the mapped class as a key.   Below we map an ``Item`` class containing
    a dictionary of ``Note`` items keyed to the ``Note.keyword`` attribute.
    When using :func:`.attribute_keyed_dict`, the :class:`_orm.Mapped`
    annotation may be typed using the :class:`_orm.KeyFuncDict`
    or just plain ``dict`` as illustrated in the following example.   However,
    the :paramref:`_orm.relationship.collection_class` parameter
    is required in this case so that the :func:`.attribute_keyed_dict`
    may be appropriately parametrized::

        from typing import Dict
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import attribute_keyed_dict
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=attribute_keyed_dict("keyword"),
                cascade="all, delete-orphan",
            )


        class Note(Base):
            __tablename__ = "note"

            id: Mapped[int] = mapped_column(primary_key=True)
            item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
            keyword: Mapped[str]
            text: Mapped[Optional[str]]

            def __init__(self, keyword: str, text: str):
                self.keyword = keyword
                self.text = text

    ``Item.notes`` is then a dictionary::

        >>> item = Item()
        >>> item.notes["a"] = Note("a", "atext")
        >>> item.notes.items()
        {'a': <__main__.Note object at 0x2eaaf0>}

    :func:`.attribute_keyed_dict` will ensure that
    the ``.keyword`` attribute of each ``Note`` complies with the key in the
    dictionary.   Such as, when assigning to ``Item.notes``, the dictionary
    key we supply must match that of the actual ``Note`` object::

        item = Item()
        item.notes = {
            "a": Note("a", "atext"),
            "b": Note("b", "btext"),
        }

    The attribute which :func:`.attribute_keyed_dict` uses as a key
    does not need to be mapped at all!  Using a regular Python ``@property`` allows virtually
    any detail or combination of details about the object to be used as the key, as
    below when we establish it as a tuple of ``Note.keyword`` and the first ten letters
    of the ``Note.text`` field::

        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=attribute_keyed_dict("note_key"),
                back_populates="item",
                cascade="all, delete-orphan",
            )


        class Note(Base):
            __tablename__ = "note"

            id: Mapped[int] = mapped_column(primary_key=True)
            item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
            keyword: Mapped[str]
            text: Mapped[str]

            item: Mapped["Item"] = relationship()

            @property
            def note_key(self):
                return (self.keyword, self.text[0:10])

            def __init__(self, keyword: str, text: str):
                self.keyword = keyword
                self.text = text

    Above we added a ``Note.item`` relationship, with a bi-directional
    :paramref:`_orm.relationship.back_populates` configuration.
    Assigning to this reverse relationship, the ``Note``
    is added to the ``Item.notes`` dictionary and the key is generated for us automatically::

        >>> item = Item()
        >>> n1 = Note("a", "atext")
        >>> n1.item = item
        >>> item.notes
        {('a', 'atext'): <__main__.Note object at 0x2eaaf0>}

    Other built-in dictionary types include :func:`.column_keyed_dict`,
    which is almost like :func:`.attribute_keyed_dict` except given the :class:`_schema.Column`
    object directly::

        from sqlalchemy.orm import column_keyed_dict


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=column_keyed_dict(Note.__table__.c.keyword),
                cascade="all, delete-orphan",
            )

    as well as :func:`.mapped_collection` which is passed any callable function.
    Note that it's usually easier to use :func:`.attribute_keyed_dict` along
    with a ``@property`` as mentioned earlier::

        from sqlalchemy.orm import mapped_collection


        class Item(Base):
            __tablename__ = "item"

            id: Mapped[int] = mapped_column(primary_key=True)

            notes: Mapped[Dict[str, "Note"]] = relationship(
                collection_class=mapped_collection(lambda note: note.text[0:10]),
                cascade="all, delete-orphan",
            )

    Dictionary mappings are often combined with the "Association Proxy" extension to produce
    streamlined dictionary views.  See :ref:`proxying_dictionaries` and :ref:`composite_association_proxy`
    for examples.

.. _key_collections_mutations:

处理字典集合的键突变和反向填充
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Dealing with Key Mutations and back-populating for Dictionary collections

.. tab:: 中文

    当使用 :func:`.attribute_keyed_dict` 时，字典的“键”是从目标对象的某个属性中获取的。
    **对此键的更改是不会被追踪的**。这意味着该键必须在首次使用时就被赋值；
    如果之后更改了该键，集合本身不会发生变化。

    一个典型的例子是依赖 backref（反向引用）来填充映射属性集合时可能会出现的问题。
    如下所示::

        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)

            bs: Mapped[Dict[str, "B"]] = relationship(
                collection_class=attribute_keyed_dict("data"),
                back_populates="a",
            )


        class B(Base):
            __tablename__ = "b"

            id: Mapped[int] = mapped_column(primary_key=True)
            a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
            data: Mapped[str]

            a: Mapped["A"] = relationship(back_populates="bs")

    如上，如果我们创建一个引用特定 ``A()`` 的 ``B()`` 实例，back_populates 会将该 ``B()`` 实例添加到 ``A.bs`` 集合中，
    但如果此时 ``B.data`` 的值尚未设置，作为键的值将会是 ``None``::

        >>> a1 = A()
        >>> b1 = B(a=a1)
        >>> a1.bs
        {None: <test3.B object at 0x7f7b1023ef70>}

    事后设置 ``b1.data`` 不会更新集合中的键::

        >>> b1.data = "the key"
        >>> a1.bs
        {None: <test3.B object at 0x7f7b1023ef70>}

    如果尝试在构造函数中初始化 ``B()``，也能观察到这个行为。
    参数的传递顺序会影响结果::

        >>> B(a=a1, data="the key")
        <test3.B object at 0x7f7b10114280>
        >>> a1.bs
        {None: <test3.B object at 0x7f7b10114280>}

    与此相对::

        >>> B(data="the key", a=a1)
        <test3.B object at 0x7f7b10114340>
        >>> a1.bs
        {'the key': <test3.B object at 0x7f7b10114340>}

    如果在使用 backref 的同时存在此类问题，请确保通过 ``__init__`` 方法按照正确顺序初始化属性。

    你也可以使用事件监听器来追踪集合中的变更，例如如下代码::

        from sqlalchemy import event
        from sqlalchemy.orm import attributes


        @event.listens_for(B.data, "set")
        def set_item(obj, value, previous, initiator):
            if obj.a is not None:
                previous = None if previous == attributes.NO_VALUE else previous
                obj.a.bs[value] = obj
                obj.a.bs.pop(previous)


.. tab:: 英文

    When using :func:`.attribute_keyed_dict`, the "key" for the dictionary
    is taken from an attribute on the target object.   **Changes to this key
    are not tracked**.  This means that the key must be assigned towards when
    it is first used, and if the key changes, the collection will not be mutated.
    A typical example where this might be an issue is when relying upon backrefs
    to populate an attribute mapped collection.  Given the following::

        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)

            bs: Mapped[Dict[str, "B"]] = relationship(
                collection_class=attribute_keyed_dict("data"),
                back_populates="a",
            )


        class B(Base):
            __tablename__ = "b"

            id: Mapped[int] = mapped_column(primary_key=True)
            a_id: Mapped[int] = mapped_column(ForeignKey("a.id"))
            data: Mapped[str]

            a: Mapped["A"] = relationship(back_populates="bs")

    Above, if we create a ``B()`` that refers to a specific ``A()``, the back
    populates will then add the ``B()`` to the ``A.bs`` collection, however
    if the value of ``B.data`` is not set yet, the key will be ``None``::

        >>> a1 = A()
        >>> b1 = B(a=a1)
        >>> a1.bs
        {None: <test3.B object at 0x7f7b1023ef70>}


    Setting ``b1.data`` after the fact does not update the collection::

        >>> b1.data = "the key"
        >>> a1.bs
        {None: <test3.B object at 0x7f7b1023ef70>}


    This can also be seen if one attempts to set up ``B()`` in the constructor.
    The order of arguments changes the result::

        >>> B(a=a1, data="the key")
        <test3.B object at 0x7f7b10114280>
        >>> a1.bs
        {None: <test3.B object at 0x7f7b10114280>}

    vs::

        >>> B(data="the key", a=a1)
        <test3.B object at 0x7f7b10114340>
        >>> a1.bs
        {'the key': <test3.B object at 0x7f7b10114340>}

    If backrefs are being used in this way, ensure that attributes are populated
    in the correct order using an ``__init__`` method.

    An event handler such as the following may also be used to track changes in the
    collection as well::

        from sqlalchemy import event
        from sqlalchemy.orm import attributes


        @event.listens_for(B.data, "set")
        def set_item(obj, value, previous, initiator):
            if obj.a is not None:
                previous = None if previous == attributes.NO_VALUE else previous
                obj.a.bs[value] = obj
                obj.a.bs.pop(previous)

.. _orm_custom_collection:

自定义集合实现
---------------------------------

Custom Collection Implementations

.. tab:: 中文

    你也可以使用自定义类型作为集合。在简单场景下，继承自 ``list`` 或 ``set`` 并添加自定义行为就足够了。
    在其他情况下，需要使用特殊的装饰器来告诉 SQLAlchemy 集合是如何运作的。

    .. topic:: 我需要自定义集合实现吗？

        大多数情况下 **完全不需要**！最常见的“自定义”集合使用场景是验证或转换传入的值，
        例如将字符串转换为某个类的实例；或更进一步，在内部以某种方式表示数据，
        然后以另一种形式在外部呈现该数据的“视图”。

        对于第一种场景，:func:`_orm.validates` 装饰器是目前**最简单**的方式，
        它可以在所有情况下拦截传入的值，用于验证和简单的数据转换。参见 :ref:`simple_validators` 查看示例。

        对于第二种场景，:ref:`associationproxy_toplevel` 扩展是一个经过充分测试、被广泛使用的系统，
        它可以根据目标对象上的某个属性，提供集合的读写“视图”。
        由于该目标属性可以是返回任意值的 ``@property``，
        所以只需要几个函数就可以构建出各种“替代”形式的集合视图。
        这种方式不会影响底层的映射集合，同时避免了需要按方法逐一定制集合行为的问题。

        当集合在访问或修改时需要特殊行为，而这些行为无法在集合外部建模时，
        自定义集合就非常有用了。当然，也可以与上述两种方式结合使用。

    SQLAlchemy 中的集合会被透明地 *检测并注入行为（instrumented）*。
    所谓“注入行为”，意味着集合上的普通操作会被追踪，并在刷新（flush）时同步到数据库中。
    此外，集合操作还可以触发 *事件*，表示需要执行某些附加操作。
    附加操作的例子包括：将子项保存到父对象所属的 :class:`~sqlalchemy.orm.session.Session` 中（即 ``save-update`` 级联），
    或同步双向关系的状态（即 :func:`.backref`）。

    `collections` 模块理解 `list`、`set` 和 `dict` 的基本接口，
    并会自动为这些内建类型及其子类添加行为注入。
    如果你实现了一个符合集合接口的自定义类型，也会通过“鸭子类型”进行识别和注入行为：

    .. sourcecode:: python+sql

        class ListLike:
            def __init__(self):
                self.data = []

            def append(self, item):
                self.data.append(item)

            def remove(self, item):
                self.data.remove(item)

            def extend(self, items):
                self.data.extend(items)

            def __iter__(self):
                return iter(self.data)

            def foo(self):
                return "foo"

    ``append``、 ``remove`` 和 ``extend`` 是 ``list`` 的已知成员方法，会自动被注入行为。
    ``__iter__`` 并不是改变集合的方法，因此不会被注入， ``foo`` 也不会。

    当然，“鸭子类型”（也就是猜测）并不总是可靠，所以你可以通过 ``__emulates__`` 类属性明确指定你要模拟的接口类型::

        class SetLike:
            __emulates__ = set

            def __init__(self):
                self.data = set()

            def append(self, item):
                self.data.add(item)

            def remove(self, item):
                self.data.remove(item)

            def __iter__(self):
                return iter(self.data)

    这个类看起来像一个 Python 的 ``list``（因为它有 ``append`` 方法），
    但 ``__emulates__`` 属性强制它被当作 ``set`` 来处理。
    其中的 ``remove`` 是 `set` 接口的已知方法，因此会被注入行为。

    但此类 **尚不能直接使用** ：我们还需要提供一些额外信息来让 SQLAlchemy ORM 正确调用集合方法。
    ORM 需要知道该使用哪些方法来添加、移除、迭代集合中的成员。
    如果你使用的是 ``list`` 或 ``set``，这些方法是已知的，会自动使用。
    但上面的类虽然像 ``set``，却并未提供标准的 ``add`` 方法，
    因此我们需要通过装饰器（如 ``@collection.appender``）告诉 ORM 使用哪个方法来代替 ``add``，
    这将在下一节中演示。


.. tab:: 英文

    You can use your own types for collections as well.  In simple cases,
    inheriting from ``list`` or ``set``, adding custom behavior, is all that's needed.
    In other cases, special decorators are needed to tell SQLAlchemy more detail
    about how the collection operates.

    .. topic:: Do I need a custom collection implementation?

        In most cases not at all!   The most common use cases for a "custom" collection
        is one that validates or marshals incoming values into a new form, such as
        a string that becomes a class instance, or one which goes a
        step beyond and represents the data internally in some fashion, presenting
        a "view" of that data on the outside of a different form.

        For the first use case, the :func:`_orm.validates` decorator is by far
        the simplest way to intercept incoming values in all cases for the purposes
        of validation and simple marshaling.  See :ref:`simple_validators`
        for an example of this.

        For the second use case, the :ref:`associationproxy_toplevel` extension is a
        well-tested, widely used system that provides a read/write "view" of a
        collection in terms of some attribute present on the target object. As the
        target attribute can be a ``@property`` that returns virtually anything, a
        wide array of "alternative" views of a collection can be constructed with
        just a few functions. This approach leaves the underlying mapped collection
        unaffected and avoids the need to carefully tailor collection behavior on a
        method-by-method basis.

        Customized collections are useful when the collection needs to
        have special behaviors upon access or mutation operations that can't
        otherwise be modeled externally to the collection.   They can of course
        be combined with the above two approaches.

    Collections in SQLAlchemy are transparently *instrumented*. Instrumentation
    means that normal operations on the collection are tracked and result in
    changes being written to the database at flush time. Additionally, collection
    operations can fire *events* which indicate some secondary operation must take
    place. Examples of a secondary operation include saving the child item in the
    parent's :class:`~sqlalchemy.orm.session.Session` (i.e. the ``save-update``
    cascade), as well as synchronizing the state of a bi-directional relationship
    (i.e. a :func:`.backref`).

    The collections package understands the basic interface of lists, sets and
    dicts and will automatically apply instrumentation to those built-in types and
    their subclasses. Object-derived types that implement a basic collection
    interface are detected and instrumented via duck-typing:

    .. sourcecode:: python+sql

        class ListLike:
            def __init__(self):
                self.data = []

            def append(self, item):
                self.data.append(item)

            def remove(self, item):
                self.data.remove(item)

            def extend(self, items):
                self.data.extend(items)

            def __iter__(self):
                return iter(self.data)

            def foo(self):
                return "foo"

    ``append``, ``remove``, and ``extend`` are known members of ``list``, and will
    be instrumented automatically. ``__iter__`` is not a mutator method and won't
    be instrumented, and ``foo`` won't be either.

    Duck-typing (i.e. guesswork) isn't rock-solid, of course, so you can be
    explicit about the interface you are implementing by providing an
    ``__emulates__`` class attribute::

        class SetLike:
            __emulates__ = set

            def __init__(self):
                self.data = set()

            def append(self, item):
                self.data.add(item)

            def remove(self, item):
                self.data.remove(item)

            def __iter__(self):
                return iter(self.data)

    This class looks similar to a Python ``list`` (i.e. "list-like") as it has an
    ``append`` method, but the ``__emulates__`` attribute forces it to be treated
    as a ``set``. ``remove`` is known to be part of the set interface and will be
    instrumented.

    But this class won't work quite yet: a little glue is needed to adapt it for
    use by SQLAlchemy. The ORM needs to know which methods to use to append, remove
    and iterate over members of the collection. When using a type like ``list`` or
    ``set``, the appropriate methods are well-known and used automatically when
    present.  However the class above, which only roughly resembles a ``set``, does not
    provide the expected ``add`` method, so we must indicate to the ORM the
    method that will instead take the place of the ``add`` method, in this
    case using a decorator ``@collection.appender``; this is illustrated in the
    next section.

通过装饰器注释自定义集合
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Annotating Custom Collections via Decorators

.. tab:: 中文

    可以使用装饰器来标记 ORM 所需的集合操作方法。
    当你的类不完全符合其容器类型的常规接口，或者你希望使用不同的方法来完成这些操作时，可以使用这些装饰器。

    .. sourcecode:: python

        from sqlalchemy.orm.collections import collection


        class SetLike:
            __emulates__ = set

            def __init__(self):
                self.data = set()

            @collection.appender
            def append(self, item):
                self.data.add(item)

            def remove(self, item):
                self.data.remove(item)

            def __iter__(self):
                return iter(self.data)

    上面的代码就是完成这个例子的全部内容。SQLAlchemy 会通过 ``append`` 方法添加实例。
    ``remove`` 和 ``__iter__`` 是集合（set）的默认方法，会分别用于移除和遍历集合。
    你也可以自定义这些默认方法：

    .. sourcecode:: python+sql

        from sqlalchemy.orm.collections import collection


        class MyList(list):
            @collection.remover
            def zark(self, item):
                # 做一些特别的处理...
                ...

            @collection.iterator
            def hey_use_this_instead_for_iteration(self): ...

    并没有要求类必须“像 list”或“像 set”。
    集合类可以是任何结构，只要为 SQLAlchemy 标注了用于添加、移除和迭代的方法即可。

    添加（append）和移除（remove）方法将接收一个映射实体作为唯一参数；
    而迭代器方法不接受任何参数，并且必须返回一个迭代器。


.. tab:: 英文

    Decorators can be used to tag the individual methods the ORM needs to manage
    collections. Use them when your class doesn't quite meet the regular interface
    for its container type, or when you otherwise would like to use a different method to
    get the job done.

    .. sourcecode:: python

        from sqlalchemy.orm.collections import collection


        class SetLike:
            __emulates__ = set

            def __init__(self):
                self.data = set()

            @collection.appender
            def append(self, item):
                self.data.add(item)

            def remove(self, item):
                self.data.remove(item)

            def __iter__(self):
                return iter(self.data)

    And that's all that's needed to complete the example. SQLAlchemy will add
    instances via the ``append`` method. ``remove`` and ``__iter__`` are the
    default methods for sets and will be used for removing and iteration. Default
    methods can be changed as well:

    .. sourcecode:: python+sql

        from sqlalchemy.orm.collections import collection


        class MyList(list):
            @collection.remover
            def zark(self, item):
                # do something special...
                ...

            @collection.iterator
            def hey_use_this_instead_for_iteration(self): ...

    There is no requirement to be "list-like" or "set-like" at all. Collection classes
    can be any shape, so long as they have the append, remove and iterate
    interface marked for SQLAlchemy's use. Append and remove methods will be
    called with a mapped entity as the single argument, and iterator methods are
    called with no arguments and must return an iterator.

.. _dictionary_collections:

自定义基于字典的集合
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom Dictionary-Based Collections

.. tab:: 中文

    :class:`.KeyFuncDict` 类可以作为自定义类型的基类，或者作为 mix-in 快速为其他类添加 ``dict`` 类型集合的支持。它使用一个键函数（keying function）来将操作委托给 ``__setitem__`` 和 ``__delitem__``：

    .. sourcecode:: python+sql

        from sqlalchemy.orm.collections import KeyFuncDict


        class MyNodeMap(KeyFuncDict):
            """存储 'Node' 对象，以其 'name' 属性作为键。"""

            def __init__(self, *args, **kw):
                super().__init__(keyfunc=lambda node: node.name)
                dict.__init__(self, *args, **kw)

    当你继承 :class:`.KeyFuncDict` 时，如果你自定义了 ``__setitem__()`` 或 ``__delitem__()`` 方法， **并且** 在这些方法中调用了 :class:`.KeyFuncDict` 中对应的同名方法，那么你应当使用 :meth:`.collection.internally_instrumented` 装饰器对其进行装饰。这是因为 :class:`.KeyFuncDict` 中的方法已经被 SQLAlchemy 所“仪器化”，从一个已被仪器化的方法内部再次调用可能导致事件被重复或错误地触发，在某些情况下会引起内部状态损坏::

        from sqlalchemy.orm.collections import KeyFuncDict, collection


        class MyKeyFuncDict(KeyFuncDict):
            """当你在方法中调用已被仪器化的方法时，使用 @internally_instrumented。"""

            @collection.internally_instrumented
            def __setitem__(self, key, value, _sa_initiator=None):
                # 可以在这里处理 key 和 value
                super(MyKeyFuncDict, self).__setitem__(key, value, _sa_initiator)

            @collection.internally_instrumented
            def __delitem__(self, key, _sa_initiator=None):
                # 可以在这里处理 key
                super(MyKeyFuncDict, self).__delitem__(key, _sa_initiator)

    ORM 与列表（list）和集合（set）一样也能识别 ``dict`` 接口，并会自动对你定义的 "dict-like" 方法进行仪器化（instrumentation），如果你选择继承 ``dict`` 或通过 duck-typing 实现 dict 类行为。

    不过你仍需要显式地为添加器（appender）和移除器（remover）方法添加装饰器 —— 因为基本字典接口中并没有默认与 SQLAlchemy 兼容的可识别方法。而迭代操作默认会通过 ``values()`` 实现，除非你使用装饰器进行修改。


.. tab:: 英文

    The :class:`.KeyFuncDict` class can be used as
    a base class for your custom types or as a mix-in to quickly add ``dict``
    collection support to other classes. It uses a keying function to delegate to
    ``__setitem__`` and ``__delitem__``:

    .. sourcecode:: python+sql

        from sqlalchemy.orm.collections import KeyFuncDict


        class MyNodeMap(KeyFuncDict):
            """Holds 'Node' objects, keyed by the 'name' attribute."""

            def __init__(self, *args, **kw):
                super().__init__(keyfunc=lambda node: node.name)
                dict.__init__(self, *args, **kw)

    When subclassing :class:`.KeyFuncDict`, user-defined versions
    of ``__setitem__()`` or ``__delitem__()`` should be decorated
    with :meth:`.collection.internally_instrumented`, **if** they call down
    to those same methods on :class:`.KeyFuncDict`.  This because the methods
    on :class:`.KeyFuncDict` are already instrumented - calling them
    from within an already instrumented call can cause events to be fired off
    repeatedly, or inappropriately, leading to internal state corruption in
    rare cases::

        from sqlalchemy.orm.collections import KeyFuncDict, collection


        class MyKeyFuncDict(KeyFuncDict):
            """Use @internally_instrumented when your methods
            call down to already-instrumented methods.

            """

            @collection.internally_instrumented
            def __setitem__(self, key, value, _sa_initiator=None):
                # do something with key, value
                super(MyKeyFuncDict, self).__setitem__(key, value, _sa_initiator)

            @collection.internally_instrumented
            def __delitem__(self, key, _sa_initiator=None):
                # do something with key
                super(MyKeyFuncDict, self).__delitem__(key, _sa_initiator)

    The ORM understands the ``dict`` interface just like lists and sets, and will
    automatically instrument all "dict-like" methods if you choose to subclass
    ``dict`` or provide dict-like collection behavior in a duck-typed class. You
    must decorate appender and remover methods, however- there are no compatible
    methods in the basic dictionary interface for SQLAlchemy to use by default.
    Iteration will go through ``values()`` unless otherwise decorated.


检测和自定义类型
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instrumentation and Custom Types

.. tab:: 中文

    许多自定义类型和现有的库类可以 **直接** 用作实体集合类型，无需额外处理。然而，需要注意的是， **仪器化（instrumentation）过程会修改该类型，并自动为其方法添加装饰器** 。

    这些装饰是轻量级的，并且在非关系使用场景中是无操作（no-op）的，但如果在其他地方被触发，仍然会带来不必要的性能开销。因此，当你使用某个库类作为集合类型时，采用 **“无实际改动的子类（trivial subclass）”技巧是个不错的做法**，这样可以将 SQLAlchemy 的装饰限制在你定义关系的用例中。例如：

    .. sourcecode:: python+sql

        class MyAwesomeList(some.great.library.AwesomeList):
            pass


        # ... relationship(..., collection_class=MyAwesomeList)

    对于内建类型，ORM 本身也使用了这种方式：当直接使用 ``list``、 ``set`` 或 ``dict`` 时，ORM 会在内部悄悄地用一个无实际改动的子类替代它们。


.. tab:: 英文

    Many custom types and existing library classes can be used as a entity
    collection type as-is without further ado. However, it is important to note
    that the instrumentation process will modify the type, adding decorators
    around methods automatically.

    The decorations are lightweight and no-op outside of relationships, but they
    do add unneeded overhead when triggered elsewhere. When using a library class
    as a collection, it can be good practice to use the "trivial subclass" trick
    to restrict the decorations to just your usage in relationships. For example:

    .. sourcecode:: python+sql

        class MyAwesomeList(some.great.library.AwesomeList):
            pass


        # ... relationship(..., collection_class=MyAwesomeList)

    The ORM uses this approach for built-ins, quietly substituting a trivial
    subclass when a ``list``, ``set`` or ``dict`` is used directly.

集合 API
-----------------------------

Collection API

.. tab:: 中文

.. tab:: 英文

.. currentmodule:: sqlalchemy.orm

.. autofunction:: attribute_keyed_dict

.. autofunction:: column_keyed_dict

.. autofunction:: keyfunc_mapping

.. autodata:: attribute_mapped_collection

.. autodata:: column_mapped_collection

.. autodata:: mapped_collection

.. autoclass:: sqlalchemy.orm.KeyFuncDict
   :members:

.. autodata:: sqlalchemy.orm.MappedCollection


集合内部结构
-----------------------------

Collection Internals

.. tab:: 中文

.. tab:: 英文

.. currentmodule:: sqlalchemy.orm.collections

.. autofunction:: bulk_replace

.. autoclass:: collection
    :members:

.. autodata:: collection_adapter

.. autoclass:: CollectionAdapter

.. autoclass:: InstrumentedDict

.. autoclass:: InstrumentedList

.. autoclass:: InstrumentedSet
