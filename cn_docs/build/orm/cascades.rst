.. _unitofwork_cascades:

级联
========

Cascades

.. tab:: 中文

    Mappers 支持在 :func:`~sqlalchemy.orm.relationship` 构造上配置 :term:`cascade` （级联）行为的概念。  
    这指的是在一个“父”对象上执行的操作应如何相对于某个特定的 :class:`.Session` 传播到该关系引用的项目（例如“子”对象），  
    其行为受 :paramref:`_orm.relationship.cascade` 选项的影响。

    级联的默认行为仅限于所谓的 :ref:`cascade_save_update` 和 :ref:`cascade_merge` 设置。  
    级联的典型“替代”设置是添加 :ref:`cascade_delete` 和 :ref:`cascade_delete_orphan` 选项；  
    这些设置适用于那些只要附属于其父对象就存在，否则就应被删除的相关对象。

    级联行为通过 :func:`~sqlalchemy.orm.relationship` 上的 :paramref:`_orm.relationship.cascade` 选项进行配置::

        class Order(Base):
            __tablename__ = "order"

            items = relationship("Item", cascade="all, delete-orphan")
            customer = relationship("User", cascade="save-update")

    若要在反向引用（backref）上设置级联，同样的标志也可以与 :func:`~.sqlalchemy.orm.backref` 函数一起使用，  
    该函数最终会将其参数传递回 :func:`~sqlalchemy.orm.relationship`::

        class Item(Base):
            __tablename__ = "item"

            order = relationship(
                "Order", backref=backref("items", cascade="all, delete-orphan")
            )

    .. sidebar:: 级联的起源

        SQLAlchemy 中关系的级联行为及其配置选项，主要源自 Hibernate ORM 中的类似特性；  
        Hibernate 在一些地方提到了 “cascade”，比如在 `Example: Parent/Child <https://docs.jboss.org/hibernate/orm/3.3/reference/en-US/html/example-parentchild.html>`_。  
        如果你对级联感到困惑，我们可以引用他们的总结：“我们刚刚讨论的部分可能会有些令人困惑。不过，在实践中，一切都会运转得很顺利。”

    :paramref:`_orm.relationship.cascade` 的默认值是 ``save-update, merge``。  
    此参数的典型替代设置为 ``all``，或者更常见的是 ``all, delete-orphan``。  
    
    符号 ``all`` 是 ``save-update, merge, refresh-expire, expunge, delete`` 的同义词，  
    而将其与 ``delete-orphan`` 一起使用，则表示子对象在所有情况下都应跟随其父对象，  
    并在不再与其父对象关联时被删除。

    .. warning:: 
        
        ``all`` 级联选项隐含了 :ref:`cascade_refresh_expire` 设置，  
        在使用 :ref:`asyncio_toplevel` 扩展时可能不太理想，  
        因为它会比通常在显式 IO 场景中更积极地使相关对象过期。  
        更多背景信息可参见 :ref:`asyncio_orm_avoid_lazyloads` 中的说明。

    :paramref:`_orm.relationship.cascade` 参数可用的取值将在下列小节中介绍。


.. tab:: 英文

    Mappers support the concept of configurable :term:`cascade` behavior on :func:`~sqlalchemy.orm.relationship` constructs.  This refers to how operations performed on a "parent" object relative to a particular :class:`.Session` should be propagated to items referred to by that relationship (e.g. "child" objects), and is affected by the :paramref:`_orm.relationship.cascade` option.

    The default behavior of cascade is limited to cascades of the so-called :ref:`cascade_save_update` and :ref:`cascade_merge` settings. The typical "alternative" setting for cascade is to add the :ref:`cascade_delete` and :ref:`cascade_delete_orphan` options; these settings are appropriate for related objects which only exist as long as they are attached to their parent, and are otherwise deleted.

    Cascade behavior is configured using the :paramref:`_orm.relationship.cascade` option on :func:`~sqlalchemy.orm.relationship`::

        class Order(Base):
            __tablename__ = "order"

            items = relationship("Item", cascade="all, delete-orphan")
            customer = relationship("User", cascade="save-update")

    To set cascades on a backref, the same flag can be used with the :func:`~.sqlalchemy.orm.backref` function, which ultimately feeds its arguments back into :func:`~sqlalchemy.orm.relationship`::

        class Item(Base):
            __tablename__ = "item"

            order = relationship(
                "Order", backref=backref("items", cascade="all, delete-orphan")
            )

    .. sidebar:: The Origins of Cascade

        SQLAlchemy's notion of cascading behavior on relationships, as well as the options to configure them, are primarily derived from the similar feature in the Hibernate ORM; Hibernate refers to "cascade" in a few places such as in `Example: Parent/Child <https://docs.jboss.org/hibernate/orm/3.3/reference/en-US/html/example-parentchild.html>`_. If cascades are confusing, we'll refer to their conclusion, stating "The sections we have just covered can be a bit confusing. However, in practice, it all works out nicely."

    The default value of :paramref:`_orm.relationship.cascade` is ``save-update, merge``. The typical alternative setting for this parameter is either ``all`` or more commonly ``all, delete-orphan``.  The ``all`` symbol is a synonym for ``save-update, merge, refresh-expire, expunge, delete``, and using it in conjunction with ``delete-orphan`` indicates that the child object should follow along with its parent in all cases, and be deleted once it is no longer associated with that parent.

    .. warning:: 
        
        The ``all`` cascade option implies the :ref:`cascade_refresh_expire` cascade setting which may not be desirable when using the :ref:`asyncio_toplevel` extension, as it will expire related objects more aggressively than is typically appropriate in an explicit IO context. See the notes at :ref:`asyncio_orm_avoid_lazyloads` for further background.

    The list of available values which can be specified for the :paramref:`_orm.relationship.cascade` parameter are described in the following subsections.

.. _cascade_save_update:

保存-更新
-----------

save-update

.. tab:: 中文

    ``save-update`` 级联表示，当一个对象被通过 :meth:`.Session.add` 放入 :class:`.Session` 中时，  
    所有通过该 :func:`_orm.relationship` 与之关联的对象也应被添加到同一个 :class:`.Session` 中。  
    假设我们有一个对象 ``user1``，它关联了两个对象 ``address1`` 和 ``address2``::

        >>> user1 = User()
        >>> address1, address2 = Address(), Address()
        >>> user1.addresses = [address1, address2]

    如果我们将 ``user1`` 添加到一个 :class:`.Session` 中，那么 ``address1`` 和 ``address2`` 也会隐式地被添加::

        >>> sess = Session()
        >>> sess.add(user1)
        >>> address1 in sess
        True

    ``save-update`` 级联也会影响已存在于某个 :class:`.Session` 中的对象的属性操作。  
    如果我们将第三个对象 ``address3`` 添加到 ``user1.addresses`` 集合中，它也会成为该 :class:`.Session` 的一部分::

        >>> address3 = Address()
        >>> user1.addresses.append(address3)
        >>> address3 in sess
        True

    当从集合中移除某项或将对象从标量属性中解除关联时，``save-update`` 级联可能会表现出令人惊讶的行为。  
    在某些情况下，被孤立的对象可能仍会被拉入前父对象的 :class:`.Session` 中；这是为了使 flush 过程能够适当地处理该相关对象。  
    这种情况通常只会在某个对象从一个 :class:`.Session` 中移除后又添加到另一个中时发生::

        >>> user1 = sess1.scalars(select(User).filter_by(id=1)).first()
        >>> address1 = user1.addresses[0]
        >>> sess1.close()  # user1 和 address1 不再与 sess1 关联
        >>> user1.addresses.remove(address1)  # address1 不再与 user1 关联
        >>> sess2 = Session()
        >>> sess2.add(user1)  # ... 但 address1 仍会被添加到新会话中，
        >>> address1 in sess2  # 因为它仍然处于“等待 flush”的状态
        True

    ``save-update`` 级联默认启用，通常会被默认接受；它通过允许一次 :meth:`.Session.add` 调用就能将整个对象结构注册到 :class:`.Session` 中，从而简化了代码。  
    虽然它是可以被禁用的，但通常没有必要这样做。

.. tab:: 英文

    ``save-update`` cascade indicates that when an object is placed into a :class:`.Session` via :meth:`.Session.add`, all the objects associated with it via this :func:`_orm.relationship` should also be added to that same :class:`.Session`.  Suppose we have an object ``user1`` with two related objects ``address1``, ``address2``::

        >>> user1 = User()
        >>> address1, address2 = Address(), Address()
        >>> user1.addresses = [address1, address2]

    If we add ``user1`` to a :class:`.Session`, it will also add ``address1``, ``address2`` implicitly::

        >>> sess = Session()
        >>> sess.add(user1)
        >>> address1 in sess
        True

    ``save-update`` cascade also affects attribute operations for objects that are already present in a :class:`.Session`.  If we add a third object, ``address3`` to the ``user1.addresses`` collection, it becomes part of the state of that :class:`.Session`::

        >>> address3 = Address()
        >>> user1.addresses.append(address3)
        >>> address3 in sess
        True

    A ``save-update`` cascade can exhibit surprising behavior when removing an item from a collection or de-associating an object from a scalar attribute. In some cases, the orphaned objects may still be pulled into the ex-parent's :class:`.Session`; this is so that the flush process may handle that related object appropriately. This case usually only arises if an object is removed from one :class:`.Session` and added to another::

        >>> user1 = sess1.scalars(select(User).filter_by(id=1)).first()
        >>> address1 = user1.addresses[0]
        >>> sess1.close()  # user1, address1 no longer associated with sess1
        >>> user1.addresses.remove(address1)  # address1 no longer associated with user1
        >>> sess2 = Session()
        >>> sess2.add(user1)  # ... but it still gets added to the new session,
        >>> address1 in sess2  # because it's still "pending" for flush
        True

    The ``save-update`` cascade is on by default, and is typically taken for granted; it simplifies code by allowing a single call to :meth:`.Session.add` to register an entire structure of objects within that :class:`.Session` at once.   While it can be disabled, there is usually not a need to do so.

.. _back_populates_cascade:

.. _backref_cascade:

具有双向关系的保存-更新级联的行为
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Behavior of save-update cascade with bi-directional relationships

.. tab:: 中文

    在双向关系的上下文中， ``save-update`` 级联是 **单向** 发生的，  
    即当使用 :paramref:`_orm.relationship.back_populates` 或 :paramref:`_orm.relationship.backref` 参数创建两个互相关联的 :func:`_orm.relationship` 对象时。

    如果一个未与 :class:`_orm.Session` 关联的对象被分配给一个已与 :class:`_orm.Session` 关联的父对象的属性或集合，  
    该对象会被自动添加到相同的 :class:`_orm.Session` 中。  
    然而，反过来的操作则不会有这种效果；  
    即当一个已与 :class:`_orm.Session` 关联的子对象被分配给一个未与任何 :class:`_orm.Session` 关联的父对象时，  
    不会导致该父对象自动添加到该 :class:`_orm.Session` 中。  
    此行为被称为“级联反向引用（cascade backrefs）”，  
    该行为在 SQLAlchemy 2.0 中被标准化并发生了变化。

    为了说明这个问题，假设有 ``Order`` 对象和一组 ``Item`` 对象之间的双向关系，  
    通过 ``Order.items`` 和 ``Item.order`` 两个关系字段建立::

        mapper_registry.map_imperatively(
            Order,
            order_table,
            properties={"items": relationship(Item, back_populates="order")},
        )

        mapper_registry.map_imperatively(
            Item,
            item_table,
            properties={"order": relationship(Order, back_populates="items")},
        )

    如果一个 ``Order`` 已与某个 :class:`_orm.Session` 关联，  
    并且随后创建了一个 ``Item`` 对象并将其追加到该 ``Order`` 的 ``items`` 集合中，  
    那么该 ``Item`` 会被自动级联加入到同一个 :class:`_orm.Session` 中::

        >>> o1 = Order()
        >>> session.add(o1)
        >>> o1 in session
        True

        >>> i1 = Item()
        >>> o1.items.append(i1)
        >>> o1 is i1.order
        True
        >>> i1 in session
        True

    如上，由于 ``Order.items`` 和 ``Item.order`` 是双向关系，  
    将对象追加到 ``Order.items`` 也会自动赋值给 ``Item.order``。  
    与此同时，``save-update`` 级联使得该 ``Item`` 对象被加入到 ``Order`` 所属的 :class:`_orm.Session` 中。

    然而，如果上述操作以 **相反方向** 进行，即直接给 ``Item.order`` 赋值而不是添加到 ``Order.items``，  
    那么级联操作将 **不会** 自动发生，  
    即使最终 ``Order.items`` 和 ``Item.order`` 的状态和前例一致::

        >>> o1 = Order()
        >>> session.add(o1)
        >>> o1 in session
        True

        >>> i1 = Item()
        >>> i1.order = o1
        >>> i1 in order.items
        True
        >>> i1 in session
        False

    在上述情况下，在创建 ``Item`` 对象并设置其状态之后，  
    应该显式地将其添加到 :class:`_orm.Session` 中::

        >>> session.add(i1)

    在旧版本的 SQLAlchemy 中， ``save-update`` 级联在所有情况下都会双向发生。  
    随后，引入了名为 ``cascade_backrefs`` 的选项以使其变为可选。  
    最终，在 SQLAlchemy 1.4 中此旧行为被弃用，  
    而在 SQLAlchemy 2.0 中 ``cascade_backrefs`` 选项被彻底移除。  
    其背后的理由是：  
    用户通常不会觉得直观——即为某对象的属性赋值（如 ``i1.order = o1``）竟然会影响对象 ``i1`` 的持久化状态，  
    使得它变成了一个挂起（pending）状态的对象；  
    这在后续过程中容易引发问题，例如在 autoflush 中对象被过早 flush，  
    而此时该对象可能仍在构建中，尚未准备好被 flush。  
    此外，允许选择单向或双向行为的选项也被移除，  
    因为这会导致 ORM 中出现两种略有不同的行为方式，  
    从而增加了学习曲线、文档复杂度以及用户支持的负担。

    .. seealso::

        :ref:`change_5150` - 有关“级联反向引用”行为更改的背景资料


.. tab:: 英文

    The ``save-update`` cascade takes place **uni-directionally** in the context of a bi-directional relationship, i.e. when using the :paramref:`_orm.relationship.back_populates` or :paramref:`_orm.relationship.backref` parameters to create two separate :func:`_orm.relationship` objects which refer to each other.

    An object that's not associated with a :class:`_orm.Session`, when assigned to an attribute or collection on a parent object that is associated with a :class:`_orm.Session`, will be automatically added to that same :class:`_orm.Session`. However, the same operation in reverse will not have this effect; an object that's not associated with a :class:`_orm.Session`, upon which a child object that is associated with a :class:`_orm.Session` is assigned, will not result in an automatic addition of that parent object to the :class:`_orm.Session`.  The overall subject of this behavior is known as "cascade backrefs", and represents a change in behavior that was standardized as of SQLAlchemy 2.0.

    To illustrate, given a mapping of ``Order`` objects which relate bi-directionally to a series of ``Item`` objects via relationships ``Order.items`` and ``Item.order``::

        mapper_registry.map_imperatively(
            Order,
            order_table,
            properties={"items": relationship(Item, back_populates="order")},
        )

        mapper_registry.map_imperatively(
            Item,
            item_table,
            properties={"order": relationship(Order, back_populates="items")},
        )

    If an ``Order`` is already associated with a :class:`_orm.Session`, and an ``Item`` object is then created and appended to the ``Order.items`` collection of that ``Order``, the ``Item`` will be automatically cascaded into that same :class:`_orm.Session`::

        >>> o1 = Order()
        >>> session.add(o1)
        >>> o1 in session
        True

        >>> i1 = Item()
        >>> o1.items.append(i1)
        >>> o1 is i1.order
        True
        >>> i1 in session
        True

    Above, the bidirectional nature of ``Order.items`` and ``Item.order`` means that appending to ``Order.items`` also assigns to ``Item.order``. At the same time, the ``save-update`` cascade allowed for the ``Item`` object to be added to the same :class:`_orm.Session` which the parent ``Order`` was already associated.

    However, if the operation above is performed in the **reverse** direction, where ``Item.order`` is assigned rather than appending directly to ``Order.item``, the cascade operation into the :class:`_orm.Session` will **not** take place automatically, even though the object assignments ``Order.items`` and ``Item.order`` will be in the same state as in the previous example::

        >>> o1 = Order()
        >>> session.add(o1)
        >>> o1 in session
        True

        >>> i1 = Item()
        >>> i1.order = o1
        >>> i1 in order.items
        True
        >>> i1 in session
        False

    In the above case, after the ``Item`` object is created and all the desired state is set upon it, it should then be added to the :class:`_orm.Session` explicitly::

        >>> session.add(i1)

    In older versions of SQLAlchemy, the save-update cascade would occur bidirectionally in all cases. It was then made optional using an option known as ``cascade_backrefs``. Finally, in SQLAlchemy 1.4 the old behavior was deprecated and the ``cascade_backrefs`` option was removed in SQLAlchemy 2.0. The rationale is that users generally do not find it intuitive that assigning to an attribute on an object, illustrated above as the assignment of ``i1.order = o1``, would alter the persistence state of that object ``i1`` such that it's now pending within a :class:`_orm.Session`, and there would frequently be subsequent issues where autoflush would prematurely flush the object and cause errors, in those cases where the given object was still being constructed and wasn't in a ready state to be flushed. The option to select between uni-directional and bi-directional behvaiors was also removed, as this option created two slightly different ways of working, adding to the overall learning curve of the ORM as well as to the documentation and user support burden.

    .. seealso::

        :ref:`change_5150` - background on the change in behavior for "cascade backrefs"

.. _cascade_delete:

删除
------

delete

.. tab:: 中文

    ``delete`` 级联表示，当一个“父”对象被标记为删除时，  
    其关联的“子”对象也应当一并被标记为删除。  
    例如，如果我们在 ``User.addresses`` 关系上配置了 ``delete`` 级联::

        class User(Base):
            # ...

            addresses = relationship("Address", cascade="all, delete")

    在使用上述映射时，我们有一个 ``User`` 对象以及两个关联的 ``Address`` 对象::

        >>> user1 = sess1.scalars(select(User).filter_by(id=1)).first()
        >>> address1, address2 = user1.addresses

    如果我们将 ``user1`` 标记为删除，在执行 flush 操作之后， ``address1`` 和 ``address2`` 也将被删除：

    .. sourcecode:: pycon+sql

        >>> sess.delete(user1)
        >>> sess.commit()
        {execsql}DELETE FROM address WHERE address.id = ?
        ((1,), (2,))
        DELETE FROM user WHERE user.id = ?
        (1,)
        COMMIT

    相反地，如果我们的 ``User.addresses`` 关系 **未** 配置 ``delete`` 级联，  
    SQLAlchemy 的默认行为是将 ``address1`` 和 ``address2`` 与 ``user1`` 解关联，  
    即将它们的外键引用设为 ``NULL``。使用如下映射::

        class User(Base):
            # ...

            addresses = relationship("Address")

    当父级 ``User`` 对象被删除时， ``address`` 表中的行不会被删除，  
    而是与其解关联：

    .. sourcecode:: pycon+sql

        >>> sess.delete(user1)
        >>> sess.commit()
        {execsql}UPDATE address SET user_id=? WHERE address.id = ?
        (None, 1)
        UPDATE address SET user_id=? WHERE address.id = ?
        (None, 2)
        DELETE FROM user WHERE user.id = ?
        (1,)
        COMMIT

    在一对多关系中，:ref:`cascade_delete` 级联通常与 :ref:`cascade_delete_orphan` 级联一起使用。  
    当“子”对象与其父对象解关联时，后者会触发对该行的 DELETE 操作。  
    ``delete`` 和 ``delete-orphan`` 的组合覆盖了 SQLAlchemy 决定是将外键列设置为 NULL，还是彻底删除该行的两种情况。

    该功能默认完全独立于数据库中通过 ``FOREIGN KEY`` 约束所定义的 ``CASCADE`` 行为。  
    为了更高效地与数据库级别的配置集成，应使用 :ref:`passive_deletes` 中描述的附加指令。

    .. warning::

        请注意 ORM 中的 “delete” 和 “delete-orphan” 行为 **仅适用于** 通过 :meth:`_orm.Session.delete` 方法，
        在 :term:`unit of work` 流程中标记要删除的单个 ORM 实例。  
        它 **不适用于** “批量”删除操作，这类操作是通过 :func:`_sql.delete` 构造函数执行的，  
        示例参见 :ref:`orm_queryguide_update_delete_where`。  
        更多信息参见 :ref:`orm_queryguide_update_delete_caveats`。

    .. seealso::

        :ref:`passive_deletes`

        :ref:`cascade_delete_many_to_many`

        :ref:`cascade_delete_orphan`


.. tab:: 英文

    The ``delete`` cascade indicates that when a "parent" object is marked for deletion, its related "child" objects should also be marked for deletion.   If for example we have a relationship ``User.addresses`` with ``delete`` cascade configured::

        class User(Base):
            # ...

            addresses = relationship("Address", cascade="all, delete")

    If using the above mapping, we have a ``User`` object and two related ``Address`` objects::

        >>> user1 = sess1.scalars(select(User).filter_by(id=1)).first()
        >>> address1, address2 = user1.addresses

    If we mark ``user1`` for deletion, after the flush operation proceeds, ``address1`` and ``address2`` will also be deleted:

    .. sourcecode:: pycon+sql

        >>> sess.delete(user1)
        >>> sess.commit()
        {execsql}DELETE FROM address WHERE address.id = ?
        ((1,), (2,))
        DELETE FROM user WHERE user.id = ?
        (1,)
        COMMIT

    Alternatively, if our ``User.addresses`` relationship does *not* have ``delete`` cascade, SQLAlchemy's default behavior is to instead de-associate ``address1`` and ``address2`` from ``user1`` by setting their foreign key reference to ``NULL``.  Using a mapping as follows::

        class User(Base):
            # ...

            addresses = relationship("Address")

    Upon deletion of a parent ``User`` object, the rows in ``address`` are not deleted, but are instead de-associated:

    .. sourcecode:: pycon+sql

        >>> sess.delete(user1)
        >>> sess.commit()
        {execsql}UPDATE address SET user_id=? WHERE address.id = ?
        (None, 1)
        UPDATE address SET user_id=? WHERE address.id = ?
        (None, 2)
        DELETE FROM user WHERE user.id = ?
        (1,)
        COMMIT

    :ref:`cascade_delete` cascade on one-to-many relationships is often combined with :ref:`cascade_delete_orphan` cascade, which will emit a DELETE for the related row if the "child" object is deassociated from the parent.  The combination of ``delete`` and ``delete-orphan`` cascade covers both situations where SQLAlchemy has to decide between setting a foreign key column to NULL versus deleting the row entirely.

    The feature by default works completely independently of database-configured ``FOREIGN KEY`` constraints that may themselves configure ``CASCADE`` behavior. In order to integrate more efficiently with this configuration, additional directives described at :ref:`passive_deletes` should be used.

    .. warning::  
        
        Note that the ORM's "delete" and "delete-orphan" behavior applies **only** to the use of the :meth:`_orm.Session.delete` method to mark individual ORM instances for deletion within the :term:`unit of work` process. It does **not** apply to "bulk" deletes, which would be emitted using the :func:`_sql.delete` construct as illustrated at :ref:`orm_queryguide_update_delete_where`.   See :ref:`orm_queryguide_update_delete_caveats` for additional background.

    .. seealso::

        :ref:`passive_deletes`

        :ref:`cascade_delete_many_to_many`

        :ref:`cascade_delete_orphan`

.. _cascade_delete_many_to_many:

使用具有多对多关系的删除级联
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using delete cascade with many-to-many relationships

.. tab:: 中文

    ``cascade="all, delete"`` 选项同样适用于多对多关系，  
    该关系使用 :paramref:`_orm.relationship.secondary` 参数指示一个关联表。  
    当父对象被删除并因此与其相关对象解除关联时，unit of work 过程通常会从关联表中删除对应的行，  
    但不会删除关联的子对象本身。而当结合使用 ``cascade="all, delete"`` 时，  
    还会额外对子对象本身执行 ``DELETE`` 操作。

    以下示例改编自 :ref:`relationships_many_to_many`，展示如何在关联的 **一方** 使用 ``cascade="all, delete"`` 设置::

        association_table = Table(
            "association",
            Base.metadata,
            Column("left_id", Integer, ForeignKey("left.id")),
            Column("right_id", Integer, ForeignKey("right.id")),
        )


        class Parent(Base):
            __tablename__ = "left"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                secondary=association_table,
                back_populates="parents",
                cascade="all, delete",
            )


        class Child(Base):
            __tablename__ = "right"
            id = mapped_column(Integer, primary_key=True)
            parents = relationship(
                "Parent",
                secondary=association_table,
                back_populates="children",
            )

    在上例中，当一个 ``Parent`` 对象通过 :meth:`_orm.Session.delete` 被标记为删除时，  
    flush 过程会像往常一样从 ``association`` 表中删除对应行，  
    但根据级联规则，也会将所有关联的 ``Child`` 行一并删除。

    .. warning::

        如果上述 ``cascade="all, delete"`` 设置同时配置在 **两个** 关系上，  
        那么级联操作会在所有 ``Parent`` 和 ``Child`` 对象之间不断传递，  
        加载所有遇到的 ``children`` 和 ``parents`` 集合，并删除所有关联的对象。  
        通常 **不建议** 将 "delete" 级联设置为双向。

    .. seealso::

    :ref:`relationships_many_to_many_deletion`

    :ref:`passive_deletes_many_to_many`


.. tab:: 英文

    The ``cascade="all, delete"`` option works equally well with a many-to-many relationship, one that uses :paramref:`_orm.relationship.secondary` to indicate an association table.   When a parent object is deleted, and therefore de-associated with its related objects, the unit of work process will normally delete rows from the association table, but leave the related objects intact. When combined with ``cascade="all, delete"``, additional ``DELETE`` statements will take place for the child rows themselves.

    The following example adapts that of :ref:`relationships_many_to_many` to illustrate the ``cascade="all, delete"`` setting on **one** side of the association::

        association_table = Table(
            "association",
            Base.metadata,
            Column("left_id", Integer, ForeignKey("left.id")),
            Column("right_id", Integer, ForeignKey("right.id")),
        )


        class Parent(Base):
            __tablename__ = "left"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                secondary=association_table,
                back_populates="parents",
                cascade="all, delete",
            )


        class Child(Base):
            __tablename__ = "right"
            id = mapped_column(Integer, primary_key=True)
            parents = relationship(
                "Parent",
                secondary=association_table,
                back_populates="children",
            )

    Above, when a ``Parent`` object is marked for deletion using :meth:`_orm.Session.delete`, the flush process will as usual delete the associated rows from the ``association`` table, however per cascade rules it will also delete all related ``Child`` rows.


    .. warning::

        If the above ``cascade="all, delete"`` setting were configured on **both** relationships, then the cascade action would continue cascading through all ``Parent`` and ``Child`` objects, loading each ``children`` and ``parents`` collection encountered and deleting everything that's connected.   It is typically not desirable for "delete" cascade to be configured bidirectionally.

    .. seealso::

    :ref:`relationships_many_to_many_deletion`

    :ref:`passive_deletes_many_to_many`
    
    .. _passive_deletes:
    
使用具有 ORM 关系的外键 ON DELETE 级联
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using foreign key ON DELETE cascade with ORM relationships

.. tab:: 中文
    
    SQLAlchemy 的 "delete" 级联行为与数据库中 ``FOREIGN KEY`` 约束的 ``ON DELETE`` 功能存在重叠。  
    SQLAlchemy 允许通过 :class:`_schema.ForeignKey` 和 :class:`_schema.ForeignKeyConstraint` 构造配置这些模式级别的 :term:`DDL` 行为；  
    这些对象结合 :class:`_schema.Table` 元数据的使用方式详见 :ref:`on_update_on_delete`。
    
    要在 :func:`_orm.relationship` 中使用 ``ON DELETE`` 外键级联，  
    首先需要注意的是：仍然必须配置 :paramref:`_orm.relationship.cascade` 设置来匹配期望的 "delete" 或 "set null" 行为  
    （即使用 ``delete`` cascade 或保持默认），  
    这样无论由 ORM 还是数据库层级的约束来实际修改数据库中的数据，ORM 都能适当跟踪那些可能被影响的本地对象的状态。
    
    然后还可以在 :func:`_orm.relationship` 上设置一个额外的选项，用以控制 ORM 在多大程度上自己执行相关行的 DELETE/UPDATE 操作，  
    或者依赖数据库端的 FOREIGN KEY 级联处理。  
    这个选项是 :paramref:`_orm.relationship.passive_deletes`，它可以接受 ``False`` （默认）、 ``True`` 和 ``"all"`` 三种值。
    
    最常见的场景是：当父行被删除时，其子行也应该被删除，并且相关的 ``FOREIGN KEY`` 约束也配置了 ``ON DELETE CASCADE``::
    
        class Parent(Base):
            __tablename__ = "parent"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                back_populates="parent",
                cascade="all, delete",
                passive_deletes=True,
            )
    
    
        class Child(Base):
            __tablename__ = "child"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("parent.id", ondelete="CASCADE"))
            parent = relationship("Parent", back_populates="children")
    
    当父行被删除时，以上配置的行为如下：
    
    1. 应用程序调用 ``session.delete(my_parent)``，其中 ``my_parent`` 是一个 ``Parent`` 实例。
    
    2. 当 :class:`_orm.Session` 下一次 flush 数据库时，ORM 会删除 **当前已加载** 的 ``my_parent.children`` 集合中的所有项，即对每个记录发出 ``DELETE`` 语句。
    
    3. 如果 ``my_parent.children`` 集合是 **未加载** 的，则不会发出任何 ``DELETE`` 语句。  
       如果这个 :func:`_orm.relationship` 没有设置 :paramref:`_orm.relationship.passive_deletes`，则 ORM 会为未加载的 ``Child`` 对象发出 ``SELECT`` 查询。
    
    4. 接着会对 ``my_parent`` 所对应的父行发出 ``DELETE`` 语句。
    
    5. 数据库层级的 ``ON DELETE CASCADE`` 设置确保所有在 ``child`` 表中引用该 ``parent`` 行的行也会被删除。
    
    6. 被 ``my_parent`` 所引用的 ``Parent`` 实例，以及所有与其相关联并已 **加载** 的 ``Child`` 实例（即第 2 步中的那些），都会从 :class:`._orm.Session` 中解除关联。
    
    .. note::
    
        要使用 "ON DELETE CASCADE"，底层数据库引擎必须支持并启用 ``FOREIGN KEY`` 约束：
    
        * 在使用 MySQL 时，必须选择支持外键的存储引擎。详见 :ref:`mysql_storage_engines`。
    
        * 在使用 SQLite 时，必须显式启用外键支持。详见 :ref:`sqlite_foreign_keys`。
    
    .. topic:: 有关 Passive Deletes 的说明
    
        有必要理解 ORM 与关系型数据库中 "cascade" 概念的区别，以及它们之间的整合方式：
    
        * 数据库层级的 ``ON DELETE`` 级联是针对关系的 **many-to-one** 方向配置的；也就是说，它是相对于作为“多”端的 ``FOREIGN KEY`` 约束设置的。  
          而在 ORM 层面， **方向是相反的**：SQLAlchemy 是从“父”端来处理“子”对象的删除，  
          因此 ``delete`` 和 ``delete-orphan`` cascade 是配置在 **one-to-many** 方向的关系上。
    
        * 没有配置 ``ON DELETE`` 的数据库外键约束常用于 **阻止** 删除父行，  
          因为这会留下未处理的关联子行。  
          如果在一对多关系中希望实现这种行为，SQLAlchemy 默认将外键设置为 ``NULL`` 的行为可以通过两种方式被捕获：
    
            * 最简单且最常见的方法是在数据库层面将该外键列设置为 ``NOT NULL``。  
              此时 SQLAlchemy 尝试将其设为 NULL 会抛出 NOT NULL 约束异常。
    
            * 另一种更特殊的方式是将 :paramref:`_orm.relationship.passive_deletes` 设置为字符串 ``"all"``。  
              这样会完全禁用 SQLAlchemy 将外键设为 NULL 的行为，  
              删除操作仅对父行发出 DELETE，不会对子行产生任何影响，即使该子对象已存在于内存中。  
              在需要触发数据库层级触发器（如 ``ON DELETE``）的场景中，这种方式可能是理想的选择。
    
        * 数据库层级的 ``ON DELETE`` 级联通常比依赖 SQLAlchemy 的 "cascade" 功能更高效。  
          数据库可以在单个 DELETE 语句中链式地完成多个表的级联删除；  
          例如删除 A 行会自动删除所有关联的 B 行，进而删除所有与 B 相关的 C 行，以此类推。  
          而 SQLAlchemy 若要支持完整的级联删除，必须逐一加载每个相关集合来确保处理所有潜在的关联行，  
          它 **无法** 一次性发出覆盖所有级联目标的 DELETE 语句。
    
        * 不过 SQLAlchemy 并不需要变得如此复杂，  
          因为我们可以通过使用 :paramref:`_orm.relationship.passive_deletes` 选项，  
          配合正确配置的外键约束，来与数据库的 ``ON DELETE`` 功能实现良好集成。  
          在此配置下，SQLAlchemy 仅对当前已加载在 :class:`.Session` 中的行发出 DELETE，  
          而对于未加载的集合，则交由数据库来处理，避免多余的 SELECT 查询。  
          详见 :ref:`passive_deletes` 中的使用示例。
    
        * 虽然数据库层级的 ``ON DELETE`` 功能仅在关系的 "many" 端起作用，  
          但 SQLAlchemy 的 "delete" cascade 也具有在 **反方向** 工作的 **有限能力**。  
          即它也可以配置在 "many" 端，当关系解除时删除 "one" 端的对象。  
          不过这很容易引发约束冲突，尤其是当有多个对象指向这个 "one" 端时，  
          所以通常 **仅适用于真正的一对一关系**。  
          在这种情况下应启用 :paramref:`_orm.relationship.single_parent` 标志以确保 Python 层的唯一性断言。

.. tab:: 英文

    The behavior of SQLAlchemy's "delete" cascade overlaps with the ``ON DELETE`` feature of a database ``FOREIGN KEY`` constraint. SQLAlchemy allows configuration of these schema-level :term:`DDL` behaviors using the :class:`_schema.ForeignKey` and :class:`_schema.ForeignKeyConstraint` constructs; usage of these objects in conjunction with :class:`_schema.Table` metadata is described at :ref:`on_update_on_delete`.
    
    In order to use ``ON DELETE`` foreign key cascades in conjunction with :func:`_orm.relationship`, it's important to note first and foremost that the :paramref:`_orm.relationship.cascade` setting must still be configured to match the desired "delete" or "set null" behavior (using ``delete`` cascade or leaving it omitted), so that whether the ORM or the database level constraints will handle the task of actually modifying the data in the database, the ORM will still be able to appropriately track the state of locally present objects that may be affected.
    
    There is then an additional option on :func:`_orm.relationship` which indicates the degree to which the ORM should try to run DELETE/UPDATE operations on related rows itself, vs. how much it should rely upon expecting the database-side FOREIGN KEY constraint cascade to handle the task; this is the :paramref:`_orm.relationship.passive_deletes` parameter and it accepts options ``False`` (the default), ``True`` and ``"all"``.
    
    The most typical example is that where child rows are to be deleted when parent rows are deleted, and that ``ON DELETE CASCADE`` is configured on the relevant ``FOREIGN KEY`` constraint as well::
    
    
        class Parent(Base):
            __tablename__ = "parent"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                back_populates="parent",
                cascade="all, delete",
                passive_deletes=True,
            )
    
    
        class Child(Base):
            __tablename__ = "child"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("parent.id", ondelete="CASCADE"))
            parent = relationship("Parent", back_populates="children")
    
    The behavior of the above configuration when a parent row is deleted is as follows:
    
    1. The application calls ``session.delete(my_parent)``, where ``my_parent`` is an instance of ``Parent``.
    
    2. When the :class:`_orm.Session` next flushes changes to the database, all of the **currently loaded** items within the ``my_parent.children`` collection are deleted by the ORM, meaning a ``DELETE`` statement is emitted for each record.
    
    3. If the ``my_parent.children`` collection is **unloaded**, then no ``DELETE`` statements are emitted.   If the :paramref:`_orm.relationship.passive_deletes` flag were **not** set on this :func:`_orm.relationship`, then a ``SELECT`` statement for unloaded ``Child`` objects would have been emitted.
    
    4. A ``DELETE`` statement is then emitted for the ``my_parent`` row itself.
    
    5. The database-level ``ON DELETE CASCADE`` setting ensures that all rows in ``child`` which refer to the affected row in ``parent`` are also deleted.
    
    6. The ``Parent`` instance referred to by ``my_parent``, as well as all instances of ``Child`` that were related to this object and were **loaded** (i.e. step 2 above took place), are de-associated from the :class:`._orm.Session`.
    
    .. note::
    
        To use "ON DELETE CASCADE", the underlying database engine must support ``FOREIGN KEY`` constraints and they must be enforcing:
    
        * When using MySQL, an appropriate storage engine must be selected.  See :ref:`mysql_storage_engines` for details.
    
        * When using SQLite, foreign key support must be enabled explicitly. See :ref:`sqlite_foreign_keys` for details.
    
    .. topic:: Notes on Passive Deletes
    
        It is important to note the differences between the ORM and the relational database's notion of "cascade" as well as how they integrate:
    
        * A database level ``ON DELETE`` cascade is configured effectively on the **many-to-one** side of the relationship; that is, we configure it relative to the ``FOREIGN KEY`` constraint that is the "many" side of a relationship.  At the ORM level, **this direction is reversed**. SQLAlchemy handles the deletion of "child" objects relative to a "parent" from the "parent" side, which means that ``delete`` and ``delete-orphan`` cascade are configured on the **one-to-many** side.
    
        * Database level foreign keys with no ``ON DELETE`` setting are often used to **prevent** a parent row from being removed, as it would necessarily leave an unhandled related row present.  If this behavior is desired in a one-to-many relationship, SQLAlchemy's default behavior of setting a foreign key to ``NULL`` can be caught in one of two ways:
    
            * The easiest and most common is just to set the foreign-key-holding column to ``NOT NULL`` at the database schema level.  An attempt by SQLAlchemy to set the column to NULL will fail with a simple NOT NULL constraint exception.
    
            * The other, more special case way is to set the :paramref:`_orm.relationship.passive_deletes` flag to the string ``"all"``.  This has the effect of entirely disabling SQLAlchemy's behavior of setting the foreign key column to NULL, and a DELETE will be emitted for the parent row without any affect on the child row, even if the child row is present in memory. This may be desirable in the case when database-level foreign key triggers, either special ``ON DELETE`` settings or otherwise, need to be activated in all cases when a parent row is deleted.
    
        * Database level ``ON DELETE`` cascade is generally much more efficient than relying upon the "cascade" delete feature of SQLAlchemy.  The database can chain a series of cascade operations across many relationships at once; e.g. if row A is deleted, all the related rows in table B can be deleted, and all the C rows related to each of those B rows, and on and on, all within the scope of a single DELETE statement. SQLAlchemy on the other hand, in order to support the cascading delete operation fully, has to individually load each related collection in order to target all rows that then may have further related collections. That is, SQLAlchemy isn't sophisticated enough to emit a DELETE for all those related rows at once within this context.
    
        * SQLAlchemy doesn't **need** to be this sophisticated, as we instead provide smooth integration with the database's own ``ON DELETE`` functionality, by using the :paramref:`_orm.relationship.passive_deletes` option in conjunction with properly configured foreign key constraints. Under this behavior, SQLAlchemy only emits DELETE for those rows that are already locally present in the :class:`.Session`; for any collections that are unloaded, it leaves them to the database to handle, rather than emitting a SELECT for them.  The section :ref:`passive_deletes` provides an example of this use.
    
        * While database-level ``ON DELETE`` functionality works only on the "many" side of a relationship, SQLAlchemy's "delete" cascade has **limited** ability to operate in the *reverse* direction as well, meaning it can be configured on the "many" side to delete an object on the "one" side when the reference on the "many" side is deleted.  However this can easily result in constraint violations if there are other objects referring to this "one" side from the "many", so it typically is only useful when a relationship is in fact a "one to one".  The :paramref:`_orm.relationship.single_parent` flag should be used to establish an in-Python assertion for this case.
    
.. _passive_deletes_many_to_many:

使用具有多对多关系的外键 ON DELETE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using foreign key ON DELETE with many-to-many relationships

.. tab:: 中文

    如 :ref:`cascade_delete_many_to_many` 中所述，"delete" 级联同样适用于多对多关系。  
    要在多对多关系中结合使用 ``ON DELETE CASCADE`` 外键，  
    需要在关联表（association table）上配置 ``FOREIGN KEY`` 指令。  
    这些指令可以自动删除关联表中的数据，但 **无法自动删除实际的关联对象本身**。

    在这种情况下，:paramref:`_orm.relationship.passive_deletes` 指令可以帮我们节省一部分删除操作过程中的 ``SELECT`` 语句，  
    但 ORM 仍然会加载部分集合，以便正确定位受影响的子对象并进行处理。

    .. note::

        一个设想中的优化方案是：对关联表中所有与父对象关联的行一次性发出 ``DELETE`` 语句，  
        然后使用 ``RETURNING`` 来获取受影响的子对象，但目前这并不是 ORM 工作单元（unit of work）实现的一部分。

    在此配置中，我们在关联表中的两个外键约束上都配置了 ``ON DELETE CASCADE``。  
    我们在从父到子的方向上配置 ``cascade="all, delete"``，  
    然后在双向关系的 **另一侧** 配置 ``passive_deletes=True``，如下所示::

        association_table = Table(
            "association",
            Base.metadata,
            Column("left_id", Integer, ForeignKey("left.id", ondelete="CASCADE")),
            Column("right_id", Integer, ForeignKey("right.id", ondelete="CASCADE")),
        )


        class Parent(Base):
            __tablename__ = "left"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                secondary=association_table,
                back_populates="parents",
                cascade="all, delete",
            )


        class Child(Base):
            __tablename__ = "right"
            id = mapped_column(Integer, primary_key=True)
            parents = relationship(
                "Parent",
                secondary=association_table,
                back_populates="children",
                passive_deletes=True,
            )

    使用上述配置，当删除一个 ``Parent`` 对象时，过程如下：

    1. 使用 :meth:`_orm.Session.delete` 将某个 ``Parent`` 对象标记为待删除。

    2. 当执行 flush 时，如果 ``Parent.children`` 集合尚未加载，ORM 会先发出一条 SELECT 查询，以加载对应的 ``Child`` 对象。

    3. 随后 ORM 会发出 ``DELETE`` 语句，删除关联表 ``association`` 中对应该父对象的所有行。

    4. 对于所有在这次删除中被影响的 ``Child`` 对象，由于配置了 ``passive_deletes=True``，  
    工作单元将 **不会** 对每个 ``Child.parents`` 集合发出 SELECT 查询，  
    因为已假设关联表中的相关行会被删除。

    5. 最后，ORM 会对从 ``Parent.children`` 加载的每个 ``Child`` 对象发出 ``DELETE`` 语句。


.. tab:: 英文

    As described at :ref:`cascade_delete_many_to_many`, "delete" cascade works for many-to-many relationships as well.  To make use of ``ON DELETE CASCADE`` foreign keys in conjunction with many to many, ``FOREIGN KEY`` directives are configured on the association table.   These directives can handle the task of automatically deleting from the association table, but cannot accommodate the automatic deletion of the related objects themselves.

    In this case, the :paramref:`_orm.relationship.passive_deletes` directive can save us some additional ``SELECT`` statements during a delete operation but there are still some collections that the ORM will continue to load, in order to locate affected child objects and handle them correctly.

    .. note::

        Hypothetical optimizations to this could include a single ``DELETE`` statement against all parent-associated rows of the association table at once, then use ``RETURNING`` to locate affected related child rows, however this is not currently part of the ORM unit of work implementation.

    In this configuration, we configure ``ON DELETE CASCADE`` on both foreign key constraints of the association table.  We configure ``cascade="all, delete"`` on the parent->child side of the relationship, and we can then configure ``passive_deletes=True`` on the **other** side of the bidirectional relationship as illustrated below::

        association_table = Table(
            "association",
            Base.metadata,
            Column("left_id", Integer, ForeignKey("left.id", ondelete="CASCADE")),
            Column("right_id", Integer, ForeignKey("right.id", ondelete="CASCADE")),
        )


        class Parent(Base):
            __tablename__ = "left"
            id = mapped_column(Integer, primary_key=True)
            children = relationship(
                "Child",
                secondary=association_table,
                back_populates="parents",
                cascade="all, delete",
            )


        class Child(Base):
            __tablename__ = "right"
            id = mapped_column(Integer, primary_key=True)
            parents = relationship(
                "Parent",
                secondary=association_table,
                back_populates="children",
                passive_deletes=True,
            )

    Using the above configuration, the deletion of a ``Parent`` object proceeds as follows:

    1. A ``Parent`` object is marked for deletion using :meth:`_orm.Session.delete`.

    2. When the flush occurs, if the ``Parent.children`` collection is not loaded, the ORM will first emit a SELECT statement in order to load the ``Child`` objects that correspond to ``Parent.children``.

    3. It will then then emit ``DELETE`` statements for the rows in ``association`` which correspond to that parent row.

    4. for each ``Child`` object affected by this immediate deletion, because ``passive_deletes=True`` is configured, the unit of work will not need to try to emit SELECT statements for each ``Child.parents`` collection as it is assumed the corresponding rows in ``association`` will be deleted.

    5. ``DELETE`` statements are then emitted for each ``Child`` object that was loaded from ``Parent.children``.


.. _cascade_delete_orphan:

删除-孤立
-------------

delete-orphan

.. tab:: 中文

    ``delete-orphan`` 级联是在 ``delete`` 级联基础上的增强，  
    使得子对象在 **与父对象解除关联时** 也会被标记为待删除，而不仅仅是在父对象被标记删除时。  
    当子对象“属于”其父对象，并且外键为 NOT NULL 时，这是一个常见用法，  
    这样当某个子对象从父对象集合中移除时，它就会被删除。

    ``delete-orphan`` 级联隐含了 **每个子对象只能同时拥有一个父对象**。  
    在绝大多数情况下，它 **仅适用于一对多关系**。  
    对于较少见的将其用于多对一或多对多关系的情况，  
    可以通过配置 :paramref:`_orm.relationship.single_parent` 参数来强制“多”的一方在任一时间只能关联一个对象，  
    此参数在 Python 层提供校验，确保对象只与一个父对象关联。  
    但这会 **大幅限制** 多重关系的功能，通常并非我们所期望的行为。

    .. seealso::

        :ref:`error_bbf0` - 有关一个常见的 delete-orphan 级联错误场景的背景介绍。

.. tab:: 英文

    ``delete-orphan`` cascade adds behavior to the ``delete`` cascade, such that a child object will be marked for deletion when it is de-associated from the parent, not just when the parent is marked for deletion.   This is a common feature when dealing with a related object that is "owned" by its parent, with a NOT NULL foreign key, so that removal of the item from the parent collection results in its deletion.

    ``delete-orphan`` cascade implies that each child object can only have one parent at a time, and in the **vast majority of cases is configured only on a one-to-many relationship.**   For the much less common case of setting it on a many-to-one or many-to-many relationship, the "many" side can be forced to allow only a single object at a time by configuring the :paramref:`_orm.relationship.single_parent` argument, which establishes Python-side validation that ensures the object is associated with only one parent at a time, however this greatly limits the functionality of the "many" relationship and is usually not what's desired.

    .. seealso::

        :ref:`error_bbf0` - background on a common error scenario involving delete-orphan cascade.

.. _cascade_merge:

合并
-----

merge

.. tab:: 中文

    ``merge`` 级联表示，当对一个父对象调用 :meth:`.Session.merge` 操作时，该操作会向其引用的对象传播。  
    该级联默认是开启的。

.. tab:: 英文

    ``merge`` cascade indicates that the :meth:`.Session.merge` operation should be propagated from a parent that's the subject of the :meth:`.Session.merge` call down to referred objects. This cascade is also on by default.

.. _cascade_refresh_expire:

刷新-过期
--------------

refresh-expire

.. tab:: 中文

    ``refresh-expire`` 是一个不常用的选项，表示 :meth:`.Session.expire` 操作应当从父对象向其引用对象传播。  
    当使用 :meth:`.Session.refresh` 时，引用对象仅会被标记为过期（expired），但不会真正刷新（refreshed）。

.. tab:: 英文

    ``refresh-expire`` is an uncommon option, indicating that the :meth:`.Session.expire` operation should be propagated from a parent down to referred objects.   When using :meth:`.Session.refresh`, the referred objects are expired only, but not actually refreshed.

.. _cascade_expunge:

删除
-------

expunge

.. tab:: 中文

    ``expunge`` 级联表示，当父对象通过 :meth:`.Session.expunge` 从 :class:`.Session` 中移除时，  
    该操作也会向其引用对象传播。

.. tab:: 英文

    ``expunge`` cascade indicates that when the parent object is removed from the :class:`.Session` using :meth:`.Session.expunge`, the operation should be propagated down to referred objects.


.. _session_deleting_from_collections:

删除注意事项 - 删除从集合和标量关系中引用的对象
----------------------------------------------------------------------------------------

Notes on Delete - Deleting Objects Referenced from Collections and Scalar Relationships

.. tab:: 中文

    一般来说，在 flush 过程中，ORM **不会修改集合或标量关系的内容**。  
    也就是说，如果某个类有一个 :func:`_orm.relationship` 属性，指向一组对象或某个单个对象（如多对一关系），  
    在 flush 发生时，该属性的内容 **不会被修改**。  
    相反，我们预期这个 :class:`.Session` 最终会过期（expire），  
    要么通过 :meth:`.Session.commit` 的自动过期行为，要么通过显式调用 :meth:`.Session.expire`。  
    此时，该 :class:`.Session` 中引用的任何对象或集合都会被清空，并在下次访问时重新加载。

    这种行为常常引发一个误解，特别是在使用 :meth:`~.Session.delete` 方法时。  
    当我们对一个对象调用 :meth:`.Session.delete` 并 flush 时，对应的数据库行会被删除。  
    如果有其他行通过外键引用了这个被删除的行，且这些行是通过 :func:`_orm.relationship` 跟踪的，  
    那么这些引用行的外键会被设置为 null，  
    或者如果设置了删除级联（delete cascade），那么这些相关行也会被删除。  
    但即便如此， **在 flush 范围内，对象间的关系属性或集合在 Python 端仍保持原样**。  
    也就是说，如果被删除的对象属于某个集合，它仍会存在于 Python 的该集合中，直到该集合被标记为过期。  
    同样，如果该对象是通过多对一或一对一的关系被另一个对象引用的，该引用也会继续存在，直到这个对象过期。

    下面的示例演示了，尽管 ``Address`` 对象已被标记为删除并且 flush 了，  
    它仍然存在于父对象 ``User`` 的集合中::

        >>> address = user.addresses[1]
        >>> session.delete(address)
        >>> session.flush()
        >>> address in user.addresses
        True

    当上面的会话被提交时，所有属性将过期。  
    此时再次访问 ``user.addresses`` 时，集合将被重新加载，从而显示出期望的状态::

        >>> session.commit()
        >>> address in user.addresses
        False

    有一种方法可以拦截 :meth:`.Session.delete` 并自动调用过期逻辑，  
    参见 `ExpireRelationshipOnFKChange <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/ExpireRelationshipOnFKChange>`_。  
    但更常见的做法是， **不直接使用** :meth:`~.Session.delete`， **而是借助级联行为在移除子对象时自动触发删除操作**。  
    ``delete-orphan`` 级联正是用于实现这种行为，如下所示::

        class User(Base):
            __tablename__ = "user"

            # ...

            addresses = relationship("Address", cascade="all, delete-orphan")


        # ...

        del user.addresses[1]
        session.flush()

    在上述代码中，当从 ``User.addresses`` 集合中移除某个 ``Address`` 对象时，  
    ``delete-orphan`` 级联会使该对象被标记为删除，效果等同于将其传递给 :meth:`~.Session.delete`。

    ``delete-orphan`` 级联同样可以用于多对一或一对一关系。  
    这时，当一个对象从其父对象中解除关联时，它也会自动被标记为删除。  
    但在多对一或一对一中使用 ``delete-orphan`` 时，需要额外配置一个标志：  
    :paramref:`_orm.relationship.single_parent`，  
    该参数会在 Python 层面断言该对象 **不能同时被多个父对象引用**::

        class User(Base):
            # ...

            preference = relationship(
                "Preference", cascade="all, delete-orphan", single_parent=True
            )

    上面这个例子中，如果某个 ``Preference`` 对象从其所属 ``User`` 中移除，在 flush 时它就会被删除::

        some_user.preference = None
        session.flush()  # 将删除该 Preference 对象

    .. seealso::

        :ref:`unitofwork_cascades` 获取有关级联行为的更多细节。

.. tab:: 英文

    The ORM in general never modifies the contents of a collection or scalar relationship during the flush process.  This means, if your class has a :func:`_orm.relationship` that refers to a collection of objects, or a reference to a single object such as many-to-one, the contents of this attribute will not be modified when the flush process occurs.  Instead, it is expected that the :class:`.Session` would eventually be expired, either through the expire-on-commit behavior of :meth:`.Session.commit` or through explicit use of :meth:`.Session.expire`. At that point, any referenced object or collection associated with that :class:`.Session` will be cleared and will re-load itself upon next access.

    A common confusion that arises regarding this behavior involves the use of the :meth:`~.Session.delete` method.   When :meth:`.Session.delete` is invoked upon an object and the :class:`.Session` is flushed, the row is deleted from the database.  Rows that refer to the target row via  foreign key, assuming they are tracked using a :func:`_orm.relationship` between the two mapped object types, will also see their foreign key attributes UPDATED to null, or if delete cascade is set up, the related rows will be deleted as well. However, even though rows related to the deleted object might be themselves modified as well, **no changes occur to relationship-bound collections or object references on the objects** involved in the operation within the scope of the flush itself.   This means if the object was a member of a related collection, it will still be present on the Python side until that collection is expired.  Similarly, if the object were referenced via many-to-one or one-to-one from another object, that reference will remain present on that object until the object is expired as well.

    Below, we illustrate that after an ``Address`` object is marked for deletion, it's still present in the collection associated with the parent ``User``, even after a flush::

        >>> address = user.addresses[1]
        >>> session.delete(address)
        >>> session.flush()
        >>> address in user.addresses
        True

    When the above session is committed, all attributes are expired.  The next access of ``user.addresses`` will re-load the collection, revealing the desired state::

        >>> session.commit()
        >>> address in user.addresses
        False

    There is a recipe for intercepting :meth:`.Session.delete` and invoking this expiration automatically; see `ExpireRelationshipOnFKChange <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/ExpireRelationshipOnFKChange>`_ for this.  However, the usual practice of deleting items within collections is to forego the usage of :meth:`~.Session.delete` directly, and instead use cascade behavior to automatically invoke the deletion as a result of removing the object from the parent collection.  The ``delete-orphan`` cascade accomplishes this, as illustrated in the example below::

        class User(Base):
            __tablename__ = "user"

            # ...

            addresses = relationship("Address", cascade="all, delete-orphan")


        # ...

        del user.addresses[1]
        session.flush()

    Where above, upon removing the ``Address`` object from the ``User.addresses`` collection, the ``delete-orphan`` cascade has the effect of marking the ``Address`` object for deletion in the same way as passing it to :meth:`~.Session.delete`.

    The ``delete-orphan`` cascade can also be applied to a many-to-one or one-to-one relationship, so that when an object is de-associated from its parent, it is also automatically marked for deletion.   Using ``delete-orphan`` cascade on a many-to-one or one-to-one requires an additional flag :paramref:`_orm.relationship.single_parent` which invokes an assertion that this related object is not to shared with any other parent simultaneously::

        class User(Base):
            # ...

            preference = relationship(
                "Preference", cascade="all, delete-orphan", single_parent=True
            )

    Above, if a hypothetical ``Preference`` object is removed from a ``User``, it will be deleted on flush::

        some_user.preference = None
        session.flush()  # will delete the Preference object

    .. seealso::

        :ref:`unitofwork_cascades` for detail on cascades.

