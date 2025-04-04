.. _relationships_backref:

使用旧版“backref”关系参数
-------------------------------------------------

Using the legacy 'backref' relationship parameter

.. tab:: 中文

    .. note:: 

        :paramref:`_orm.relationship.backref` 关键字应该视为过时，推荐使用 :paramref:`_orm.relationship.back_populates` 配合显式的 :func:`_orm.relationship` 构造。使用单独的 :func:`_orm.relationship` 构造带来了诸多优势，包括：两个 ORM 映射类会在类构建时一开始就包含它们的属性，而不是作为延迟步骤；配置也更加直观，因为所有参数都是显式的。SQLAlchemy 2.0 中的新 :pep:`484` 特性也利用了在源代码中显式出现的属性，而不是使用动态属性生成。

    .. seealso::

        有关双向关系的一般信息，请参阅以下章节：

        :ref:`tutorial_orm_related_objects` - 在 :ref:`unified_tutorial` 中，介绍了使用 :paramref:`_orm.relationship.back_populates` 配置和行为的双向关系概述。

        :ref:`back_populates_cascade` - 讨论了双向 :func:`_orm.relationship` 行为与 :class:`_orm.Session` 级联行为之间的关系。

        :paramref:`_orm.relationship.back_populates`


    :paramref:`_orm.relationship.backref` 关键字参数` 在 :func:`_orm.relationship` 构造中允许自动生成一个新的 :func:`_orm.relationship`，并自动添加到相关类的 ORM 映射中。然后，它将被放入当前正在配置的 :func:`_orm.relationship` 中的 :paramref:`_orm.relationship.back_populates` 配置中，两个 :func:`_orm.relationship` 构造将相互引用。

    以下是一个示例::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship("Address", backref="user")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

    上述配置在 ``User`` 上建立了一个 ``Address`` 对象的集合，名为 ``User.addresses``。它还在 ``Address`` 上建立了一个 ``.user`` 属性，指向父级 ``User`` 对象。 使用 :paramref:`_orm.relationship.back_populates`，它等同于以下配置::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship("Address", back_populates="user")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

            user = relationship("User", back_populates="addresses")

    ``User.addresses`` 和 ``Address.user`` 关系的行为是双向的，这意味着关系一侧的更改会影响另一侧。有关此行为的示例和讨论，请参阅 :ref:`unified_tutorial` 中的 :ref:`tutorial_orm_related_objects`。


.. tab:: 英文

    .. note:: 
        
        The :paramref:`_orm.relationship.backref` keyword should be considered legacy, and use of :paramref:`_orm.relationship.back_populates` with explicit :func:`_orm.relationship` constructs should be preferred.  Using individual :func:`_orm.relationship` constructs provides advantages including that both ORM mapped classes will include their attributes up front as the class is constructed, rather than as a deferred step, and configuration is more straightforward as all arguments are explicit. New :pep:`484` features in SQLAlchemy 2.0 also take advantage of attributes being explicitly present in source code rather than using dynamic attribute generation.

    .. seealso::

        For general information about bidirectional relationships, see the following sections:

        :ref:`tutorial_orm_related_objects` - in the :ref:`unified_tutorial`, presents an overview of bi-directional relationship configuration and behaviors using :paramref:`_orm.relationship.back_populates`

        :ref:`back_populates_cascade` - notes on bi-directional :func:`_orm.relationship` behavior regarding :class:`_orm.Session` cascade behaviors.

        :paramref:`_orm.relationship.back_populates`


    The :paramref:`_orm.relationship.backref` keyword argument on the :func:`_orm.relationship` construct allows the automatic generation of a new :func:`_orm.relationship` that will be automatically be added to the ORM mapping for the related class.  It will then be placed into a :paramref:`_orm.relationship.back_populates` configuration against the current :func:`_orm.relationship` being configured, with both :func:`_orm.relationship` constructs referring to each other.

    Starting with the following example::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship("Address", backref="user")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

    The above configuration establishes a collection of ``Address`` objects on ``User`` called ``User.addresses``.   It also establishes a ``.user`` attribute on ``Address`` which will refer to the parent ``User`` object.   Using :paramref:`_orm.relationship.back_populates` it's equivalent to the following::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship("Address", back_populates="user")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

            user = relationship("User", back_populates="addresses")

    The behavior of the ``User.addresses`` and ``Address.user`` relationships is that they now behave in a **bi-directional** way, indicating that changes on one side of the relationship impact the other.   An example and discussion of this behavior is in the :ref:`unified_tutorial` at :ref:`tutorial_orm_related_objects`.


Backref 默认参数
~~~~~~~~~~~~~~~~~~~~~~~~~

Backref Default Arguments

.. tab:: 中文

    由于 :paramref:`_orm.relationship.backref` 会生成一个全新的 :func:`_orm.relationship`，生成过程默认会尝试在新的 :func:`_orm.relationship` 中包括与原始参数相对应的参数。以下是一个包含 :ref:`自定义连接条件 <relationship_configure_joins>` 的 :func:`_orm.relationship`，其中也包括了 :paramref:`_orm.relationship.backref` 关键字::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship(
                "Address",
                primaryjoin=(
                    "and_(User.id==Address.user_id, Address.email.startswith('tony'))"
                ),
                backref="user",
            )


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

    当生成 "backref" 时， :paramref:`_orm.relationship.primaryjoin` 条件也会复制到新的 :func:`_orm.relationship` 中::

        >>> print(User.addresses.property.primaryjoin)
        "user".id = address.user_id AND address.email LIKE :email_1 || '%%'
        >>>
        >>> print(Address.user.property.primaryjoin)
        "user".id = address.user_id AND address.email LIKE :email_1 || '%%'
        >>>

    其他可转移的参数包括 :paramref:`_orm.relationship.secondary` 参数，它引用了一个多对多关联表，以及 "join" 参数 :paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin`；"backref" 足够智能，知道这两个参数在生成对方关系时也应该被“反向”处理。


.. tab:: 英文

    Since :paramref:`_orm.relationship.backref` generates a whole new :func:`_orm.relationship`, the generation process by default will attempt to include corresponding arguments in the new :func:`_orm.relationship` that correspond to the original arguments. As an example, below is a :func:`_orm.relationship` that includes a :ref:`custom join condition <relationship_configure_joins>` which also includes the :paramref:`_orm.relationship.backref` keyword::

        from sqlalchemy import Column, ForeignKey, Integer, String
        from sqlalchemy.orm import DeclarativeBase, relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship(
                "Address",
                primaryjoin=(
                    "and_(User.id==Address.user_id, Address.email.startswith('tony'))"
                ),
                backref="user",
            )


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

    When the "backref" is generated, the :paramref:`_orm.relationship.primaryjoin` condition is copied to the new :func:`_orm.relationship` as well::

        >>> print(User.addresses.property.primaryjoin)
        "user".id = address.user_id AND address.email LIKE :email_1 || '%%'
        >>>
        >>> print(Address.user.property.primaryjoin)
        "user".id = address.user_id AND address.email LIKE :email_1 || '%%'
        >>>

    Other arguments that are transferrable include the :paramref:`_orm.relationship.secondary` parameter that refers to a many-to-many association table, as well as the "join" arguments :paramref:`_orm.relationship.primaryjoin` and :paramref:`_orm.relationship.secondaryjoin`; "backref" is smart enough to know that these two arguments should also be "reversed" when generating the opposite side.

指定 Backref 参数
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying Backref Arguments

.. tab:: 中文

    许多其他的 "backref" 参数不是隐式的，包括 :paramref:`_orm.relationship.lazy` 、 :paramref:`_orm.relationship.remote_side` 、 :paramref:`_orm.relationship.cascade` 和 :paramref:`_orm.relationship.cascade_backrefs` 等。对于这种情况，我们使用 :func:`.backref` 函数代替字符串；这将存储一组特定的参数，这些参数将在生成时传递给新的 :func:`_orm.relationship`::

        # <other imports>
        from sqlalchemy.orm import backref


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship(
                "Address",
                backref=backref("user", lazy="joined"),
            )

    在上面的例子中，我们仅在 ``Address.user`` 端放置了 ``lazy="joined"`` 指令，这表示当对 ``Address`` 执行查询时，应自动连接到 ``User`` 实体，从而填充每个返回的 ``Address`` 的 ``.user`` 属性。 :func:`.backref` 函数将我们提供的参数格式化成一种形式，这种形式会被接收的 :func:`_orm.relationship` 解释为要应用于它创建的新关系的额外参数。

.. tab:: 英文

    Lots of other arguments for a "backref" are not implicit, and include arguments like :paramref:`_orm.relationship.lazy`, :paramref:`_orm.relationship.remote_side`, :paramref:`_orm.relationship.cascade` and :paramref:`_orm.relationship.cascade_backrefs`.   For this case we use the :func:`.backref` function in place of a string; this will store a specific set of arguments that will be transferred to the new :func:`_orm.relationship` when generated::

        # <other imports>
        from sqlalchemy.orm import backref


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            addresses = relationship(
                "Address",
                backref=backref("user", lazy="joined"),
            )

    Where above, we placed a ``lazy="joined"`` directive only on the ``Address.user`` side, indicating that when a query against ``Address`` is made, a join to the ``User`` entity should be made automatically which will populate the ``.user`` attribute of each returned ``Address``.   The :func:`.backref` function formatted the arguments we gave it into a form that is interpreted by the receiving :func:`_orm.relationship` as additional arguments to be applied to the new relationship it creates.

