.. _relationship_configure_joins:

配置关系连接方式
----------------------------------

Configuring how Relationship Joins

.. tab:: 中文

    :func:`_orm.relationship` 通常会通过检查两个表之间的外键关系来确定应比较哪些列来创建两个表之间的连接。在各种情况下，此行为都需要定制。

.. tab:: 英文

    :func:`_orm.relationship` will normally create a join between two tables by examining the foreign key relationship between the two tables to determine which columns should be compared.  There are a variety of situations where this behavior needs to be customized.

.. _relationship_foreign_keys:

处理多个连接路径
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Handling Multiple Join Paths

.. tab:: 中文

    最常见的情况之一是两个表之间有多个外键路径。

    考虑一个 ``Customer`` 类，其中包含两个指向 ``Address`` 类的外键::

        from sqlalchemy import Integer, ForeignKey, String, Column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Customer(Base):
            __tablename__ = "customer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            billing_address_id = mapped_column(Integer, ForeignKey("address.id"))
            shipping_address_id = mapped_column(Integer, ForeignKey("address.id"))

            billing_address = relationship("Address")
            shipping_address = relationship("Address")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            street = mapped_column(String)
            city = mapped_column(String)
            state = mapped_column(String)
            zip = mapped_column(String)

    上述映射，当我们尝试使用它时，会产生错误：

    .. sourcecode:: text

        sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join
        condition between parent/child tables on relationship
        Customer.billing_address - there are multiple foreign key
        paths linking the tables.  Specify the 'foreign_keys' argument,
        providing a list of those columns which should be
        counted as containing a foreign key reference to the parent table.

    上述消息相当长。:func:`_orm.relationship` 可以返回许多潜在的消息，这些消息经过精心定制以检测各种常见的配置问题；大多数情况下会建议解决歧义或其他缺失信息所需的额外配置。

    在这种情况下，消息希望我们通过为每个 :func:`_orm.relationship` 指定应考虑的外键列来限定每个 :func:`_orm.relationship`，适当的形式如下::

        class Customer(Base):
            __tablename__ = "customer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            billing_address_id = mapped_column(Integer, ForeignKey("address.id"))
            shipping_address_id = mapped_column(Integer, ForeignKey("address.id"))

            billing_address = relationship("Address", foreign_keys=[billing_address_id])
            shipping_address = relationship("Address", foreign_keys=[shipping_address_id])

    在上面，我们指定了 ``foreign_keys`` 参数，这是一个 :class:`_schema.Column` 或 :class:`_schema.Column` 对象列表，用于指示应被视为“外键”的列，换句话说，即包含引用父表值的列。从 ``Customer`` 对象加载 ``Customer.billing_address`` 关系将使用 ``billing_address_id`` 中存在的值来标识要加载的 ``Address`` 中的行；类似地， ``shipping_address_id`` 用于 ``shipping_address`` 关系。这两个列的链接在持久化期间也起作用；在刷新期间，刚插入的 ``Address`` 对象的新生成主键将被复制到关联的 ``Customer`` 对象的适当外键列中。

    在使用声明式指定 ``foreign_keys`` 时，我们也可以使用字符串名称来指定，但重要的是，如果使用列表， **列表是字符串的一部分**::

            billing_address = relationship("Address", foreign_keys="[Customer.billing_address_id]")

    在这个特定示例中，列表在任何情况下都是不必要的，因为我们只需要一个 :class:`_schema.Column`::

            billing_address = relationship("Address", foreign_keys="Customer.billing_address_id")

    .. warning:: 
        
        作为 Python 可评估字符串传递时，:paramref:`_orm.relationship.foreign_keys` 参数使用 Python 的 ``eval()`` 函数进行解释。 **不要将不受信任的输入传递给此字符串**。有关声明式评估 :func:`_orm.relationship` 参数的详细信息，请参见 :ref:`declarative_relationship_eval`。

.. tab:: 英文

    One of the most common situations to deal with is when
    there are more than one foreign key path between two tables.

    Consider a ``Customer`` class that contains two foreign keys to an ``Address``
    class::

        from sqlalchemy import Integer, ForeignKey, String, Column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class Customer(Base):
            __tablename__ = "customer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            billing_address_id = mapped_column(Integer, ForeignKey("address.id"))
            shipping_address_id = mapped_column(Integer, ForeignKey("address.id"))

            billing_address = relationship("Address")
            shipping_address = relationship("Address")


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            street = mapped_column(String)
            city = mapped_column(String)
            state = mapped_column(String)
            zip = mapped_column(String)

    The above mapping, when we attempt to use it, will produce the error:

    .. sourcecode:: text

        sqlalchemy.exc.AmbiguousForeignKeysError: Could not determine join
        condition between parent/child tables on relationship
        Customer.billing_address - there are multiple foreign key
        paths linking the tables.  Specify the 'foreign_keys' argument,
        providing a list of those columns which should be
        counted as containing a foreign key reference to the parent table.

    The above message is pretty long.  There are many potential messages
    that :func:`_orm.relationship` can return, which have been carefully tailored
    to detect a variety of common configurational issues; most will suggest
    the additional configuration that's needed to resolve the ambiguity
    or other missing information.

    In this case, the message wants us to qualify each :func:`_orm.relationship`
    by instructing for each one which foreign key column should be considered, and
    the appropriate form is as follows::

        class Customer(Base):
            __tablename__ = "customer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)

            billing_address_id = mapped_column(Integer, ForeignKey("address.id"))
            shipping_address_id = mapped_column(Integer, ForeignKey("address.id"))

            billing_address = relationship("Address", foreign_keys=[billing_address_id])
            shipping_address = relationship("Address", foreign_keys=[shipping_address_id])

    Above, we specify the ``foreign_keys`` argument, which is a :class:`_schema.Column` or list
    of :class:`_schema.Column` objects which indicate those columns to be considered "foreign",
    or in other words, the columns that contain a value referring to a parent table.
    Loading the ``Customer.billing_address`` relationship from a ``Customer``
    object will use the value present in ``billing_address_id`` in order to
    identify the row in ``Address`` to be loaded; similarly, ``shipping_address_id``
    is used for the ``shipping_address`` relationship.   The linkage of the two
    columns also plays a role during persistence; the newly generated primary key
    of a just-inserted ``Address`` object will be copied into the appropriate
    foreign key column of an associated ``Customer`` object during a flush.

    When specifying ``foreign_keys`` with Declarative, we can also use string
    names to specify, however it is important that if using a list, the **list
    is part of the string**::

            billing_address = relationship("Address", foreign_keys="[Customer.billing_address_id]")

    In this specific example, the list is not necessary in any case as there's only
    one :class:`_schema.Column` we need::

            billing_address = relationship("Address", foreign_keys="Customer.billing_address_id")

    .. warning:: 
        
        When passed as a Python-evaluable string, the
        :paramref:`_orm.relationship.foreign_keys` argument is interpreted using Python's
        ``eval()`` function. **DO NOT PASS UNTRUSTED INPUT TO THIS STRING**. See
        :ref:`declarative_relationship_eval` for details on declarative
        evaluation of :func:`_orm.relationship` arguments.


.. _relationship_primaryjoin:

指定备用连接条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specifying Alternate Join Conditions

.. tab:: 中文

    :func:`_orm.relationship` 在构建连接时的默认行为是将一侧主键列的值等同于另一侧引用外键的列的值。我们可以使用 :paramref:`_orm.relationship.primaryjoin` 参数（以及在使用“secondary”表时使用的 :paramref:`_orm.relationship.secondaryjoin` 参数）将此标准更改为我们想要的任何内容。

    在下面的示例中，使用 ``User`` 类以及存储街道地址的 ``Address`` 类，我们创建一个关系 ``boston_addresses``，它只加载那些指定城市为“Boston”的 ``Address`` 对象::

        from sqlalchemy import Integer, ForeignKey, String, Column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)
            boston_addresses = relationship(
                "Address",
                primaryjoin="and_(User.id==Address.user_id, Address.city=='Boston')",
            )


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

            street = mapped_column(String)
            city = mapped_column(String)
            state = mapped_column(String)
            zip = mapped_column(String)

    在这个字符串 SQL 表达式中，我们使用了 :func:`.and_` 连接构造来建立两个不同的连接条件谓词 - 将 ``User.id`` 和 ``Address.user_id`` 列连接到一起，并将 ``Address`` 中的行限制为仅 ``city='Boston'``。在使用声明式时，基本的 SQL 函数如 :func:`.and_` 在字符串 :func:`_orm.relationship` 参数的评估命名空间中自动可用。

    .. warning:: 
        
        当作为 Python 可评估字符串传递时，:paramref:`_orm.relationship.primaryjoin` 参数使用 Python 的 ``eval()`` 函数进行解释。 **不要将不受信任的输入传递给此字符串**。有关声明式评估 :func:`_orm.relationship` 参数的详细信息，请参见 :ref:`declarative_relationship_eval`。

    我们在 :paramref:`_orm.relationship.primaryjoin` 中使用的自定义条件通常仅在 SQLAlchemy 渲染 SQL 以加载或表示此关系时才重要。也就是说，它用于发出 SQL 语句以执行每个属性的延迟加载，或在查询时构建连接时使用，例如通过 :meth:`Select.join`，或通过“joined”或“subquery”风格的预加载。当正在操作内存中的对象时，我们可以将任何我们想要的 ``Address`` 对象放入 ``boston_addresses`` 集合中，而不管 ``.city`` 属性的值是什么。对象将保持在集合中，直到属性过期并从数据库中重新加载应用的条件。当发生刷新时， ``boston_addresses`` 内的对象将无条件刷新，将主键 ``user.id`` 列的值分配到每行的持有外键的 ``address.user_id`` 列中。 ``city`` 条件在这里没有效果，因为刷新过程只关心将主键值同步到引用的外键值中。

.. tab:: 英文

    The default behavior of :func:`_orm.relationship` when constructing a join
    is that it equates the value of primary key columns
    on one side to that of foreign-key-referring columns on the other.
    We can change this criterion to be anything we'd like using the
    :paramref:`_orm.relationship.primaryjoin`
    argument, as well as the :paramref:`_orm.relationship.secondaryjoin`
    argument in the case when a "secondary" table is used.

    In the example below, using the ``User`` class
    as well as an ``Address`` class which stores a street address,  we
    create a relationship ``boston_addresses`` which will only
    load those ``Address`` objects which specify a city of "Boston"::

        from sqlalchemy import Integer, ForeignKey, String, Column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String)
            boston_addresses = relationship(
                "Address",
                primaryjoin="and_(User.id==Address.user_id, Address.city=='Boston')",
            )


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(Integer, ForeignKey("user.id"))

            street = mapped_column(String)
            city = mapped_column(String)
            state = mapped_column(String)
            zip = mapped_column(String)

    Within this string SQL expression, we made use of the :func:`.and_` conjunction
    construct to establish two distinct predicates for the join condition - joining
    both the ``User.id`` and ``Address.user_id`` columns to each other, as well as
    limiting rows in ``Address`` to just ``city='Boston'``.   When using
    Declarative, rudimentary SQL functions like :func:`.and_` are automatically
    available in the evaluated namespace of a string :func:`_orm.relationship`
    argument.

    .. warning:: 
        
        When passed as a Python-evaluable string, the
        :paramref:`_orm.relationship.primaryjoin` argument is interpreted using
        Python's
        ``eval()`` function. **DO NOT PASS UNTRUSTED INPUT TO THIS STRING**. See
        :ref:`declarative_relationship_eval` for details on declarative
        evaluation of :func:`_orm.relationship` arguments.


    The custom criteria we use in a :paramref:`_orm.relationship.primaryjoin`
    is generally only significant when SQLAlchemy is rendering SQL in
    order to load or represent this relationship. That is, it's used in
    the SQL statement that's emitted in order to perform a per-attribute
    lazy load, or when a join is constructed at query time, such as via
    :meth:`Select.join`, or via the eager "joined" or "subquery" styles of
    loading.   When in-memory objects are being manipulated, we can place
    any ``Address`` object we'd like into the ``boston_addresses``
    collection, regardless of what the value of the ``.city`` attribute
    is.   The objects will remain present in the collection until the
    attribute is expired and re-loaded from the database where the
    criterion is applied.   When a flush occurs, the objects inside of
    ``boston_addresses`` will be flushed unconditionally, assigning value
    of the primary key ``user.id`` column onto the foreign-key-holding
    ``address.user_id`` column for each row.  The ``city`` criteria has no
    effect here, as the flush process only cares about synchronizing
    primary key values into referencing foreign key values.

.. _relationship_custom_foreign:

创建自定义外部条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating Custom Foreign Conditions

.. tab:: 中文

    主连接条件的另一个元素是如何确定那些被认为是“外键”的列。通常，某些 :class:`_schema.Column` 对象将指定 :class:`_schema.ForeignKey`，或者是与连接条件相关的 :class:`_schema.ForeignKeyConstraint` 的一部分。:func:`_orm.relationship` 会查看这种外键状态，因为它决定了如何为此关系加载和持久化数据。然而，:paramref:`_orm.relationship.primaryjoin` 参数可以用来创建不涉及任何“schema”级别外键的连接条件。我们可以结合使用 :paramref:`_orm.relationship.primaryjoin` 以及 :paramref:`_orm.relationship.foreign_keys` 和 :paramref:`_orm.relationship.remote_side` 显式地建立这样的连接。

    在下面的示例中，一个类 ``HostEntry`` 自引用连接，将字符串 ``content`` 列等同于 ``ip_address`` 列，这是一个名为 ``INET`` 的 PostgreSQL 类型。我们需要使用 :func:`.cast` 将连接的一侧强制转换为另一侧的类型::

        from sqlalchemy import cast, String, Column, Integer
        from sqlalchemy.orm import relationship
        from sqlalchemy.dialects.postgresql import INET

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class HostEntry(Base):
            __tablename__ = "host_entry"

            id = mapped_column(Integer, primary_key=True)
            ip_address = mapped_column(INET)
            content = mapped_column(String(50))

            # relationship() 使用显式 foreign_keys 和 remote_side
            parent_host = relationship(
                "HostEntry",
                primaryjoin=ip_address == cast(content, INET),
                foreign_keys=content,
                remote_side=ip_address,
            )

    上述关系将产生如下连接：

    .. sourcecode:: sql

        SELECT host_entry.id, host_entry.ip_address, host_entry.content
        FROM host_entry JOIN host_entry AS host_entry_1
        ON host_entry_1.ip_address = CAST(host_entry.content AS INET)

    上述的另一种语法是在线使用 :func:`.foreign` 和 :func:`.remote` :term:`annotations`，在 :paramref:`_orm.relationship.primaryjoin` 表达式中。这种语法表示 :func:`_orm.relationship` 通常自行应用于连接条件的注释，给定 :paramref:`_orm.relationship.foreign_keys` 和 :paramref:`_orm.relationship.remote_side` 参数。当存在显式连接条件时，这些函数可能更简洁，并且还标记了“外键”或“远程”的确切列，而不管该列是否多次声明或在复杂 SQL 表达式中::

        from sqlalchemy.orm import foreign, remote


        class HostEntry(Base):
            __tablename__ = "host_entry"

            id = mapped_column(Integer, primary_key=True)
            ip_address = mapped_column(INET)
            content = mapped_column(String(50))

            # relationship() 使用显式 foreign() 和 remote() 注释
            # 代替单独的参数
            parent_host = relationship(
                "HostEntry",
                primaryjoin=remote(ip_address) == cast(foreign(content), INET),
            )

.. tab:: 英文

    Another element of the primary join condition is how those columns
    considered "foreign" are determined.  Usually, some subset
    of :class:`_schema.Column` objects will specify :class:`_schema.ForeignKey`, or otherwise
    be part of a :class:`_schema.ForeignKeyConstraint` that's relevant to the join condition.
    :func:`_orm.relationship` looks to this foreign key status as it decides
    how it should load and persist data for this relationship.   However, the
    :paramref:`_orm.relationship.primaryjoin` argument can be used to create a join condition that
    doesn't involve any "schema" level foreign keys.  We can combine :paramref:`_orm.relationship.primaryjoin`
    along with :paramref:`_orm.relationship.foreign_keys` and :paramref:`_orm.relationship.remote_side` explicitly in order to
    establish such a join.

    Below, a class ``HostEntry`` joins to itself, equating the string ``content``
    column to the ``ip_address`` column, which is a PostgreSQL type called ``INET``.
    We need to use :func:`.cast` in order to cast one side of the join to the
    type of the other::

        from sqlalchemy import cast, String, Column, Integer
        from sqlalchemy.orm import relationship
        from sqlalchemy.dialects.postgresql import INET

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class HostEntry(Base):
            __tablename__ = "host_entry"

            id = mapped_column(Integer, primary_key=True)
            ip_address = mapped_column(INET)
            content = mapped_column(String(50))

            # relationship() using explicit foreign_keys, remote_side
            parent_host = relationship(
                "HostEntry",
                primaryjoin=ip_address == cast(content, INET),
                foreign_keys=content,
                remote_side=ip_address,
            )

    The above relationship will produce a join like:

    .. sourcecode:: sql

        SELECT host_entry.id, host_entry.ip_address, host_entry.content
        FROM host_entry JOIN host_entry AS host_entry_1
        ON host_entry_1.ip_address = CAST(host_entry.content AS INET)

    An alternative syntax to the above is to use the :func:`.foreign` and
    :func:`.remote` :term:`annotations`,
    inline within the :paramref:`_orm.relationship.primaryjoin` expression.
    This syntax represents the annotations that :func:`_orm.relationship` normally
    applies by itself to the join condition given the :paramref:`_orm.relationship.foreign_keys` and
    :paramref:`_orm.relationship.remote_side` arguments.  These functions may
    be more succinct when an explicit join condition is present, and additionally
    serve to mark exactly the column that is "foreign" or "remote" independent
    of whether that column is stated multiple times or within complex
    SQL expressions::

        from sqlalchemy.orm import foreign, remote


        class HostEntry(Base):
            __tablename__ = "host_entry"

            id = mapped_column(Integer, primary_key=True)
            ip_address = mapped_column(INET)
            content = mapped_column(String(50))

            # relationship() using explicit foreign() and remote() annotations
            # in lieu of separate arguments
            parent_host = relationship(
                "HostEntry",
                primaryjoin=remote(ip_address) == cast(foreign(content), INET),
            )

.. _relationship_custom_operator:

在连接条件中使用自定义运算符
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using custom operators in join conditions

.. tab:: 中文

    关系的另一个用例是使用自定义运算符，例如在与 :class:`_postgresql.INET` 和 :class:`_postgresql.CIDR` 类型连接时使用 PostgreSQL 的“包含于” ``<<`` 运算符。对于自定义布尔运算符，我们使用 :meth:`.Operators.bool_op` 函数::

        inet_column.bool_op("<<")(cidr_column)

    如上所述的比较可以直接与 :paramref:`_orm.relationship.primaryjoin` 一起使用，当构建 :func:`_orm.relationship` 时::

        class IPA(Base):
            __tablename__ = "ip_address"

            id = mapped_column(Integer, primary_key=True)
            v4address = mapped_column(INET)

            network = relationship(
                "Network",
                primaryjoin="IPA.v4address.bool_op('<<')(foreign(Network.v4representation))",
                viewonly=True,
            )


        class Network(Base):
            __tablename__ = "network"

            id = mapped_column(Integer, primary_key=True)
            v4representation = mapped_column(CIDR)

    如上所述的查询::

        select(IPA).join(IPA.network)

    将渲染为：

    .. sourcecode:: sql

        SELECT ip_address.id AS ip_address_id, ip_address.v4address AS ip_address_v4address
        FROM ip_address JOIN network ON ip_address.v4address << network.v4representation

.. tab:: 英文

    Another use case for relationships is the use of custom operators, such
    as PostgreSQL's "is contained within" ``<<`` operator when joining with
    types such as :class:`_postgresql.INET` and :class:`_postgresql.CIDR`.
    For custom boolean operators we use the :meth:`.Operators.bool_op` function::

        inet_column.bool_op("<<")(cidr_column)

    A comparison like the above may be used directly with
    :paramref:`_orm.relationship.primaryjoin` when constructing
    a :func:`_orm.relationship`::

        class IPA(Base):
            __tablename__ = "ip_address"

            id = mapped_column(Integer, primary_key=True)
            v4address = mapped_column(INET)

            network = relationship(
                "Network",
                primaryjoin="IPA.v4address.bool_op('<<')(foreign(Network.v4representation))",
                viewonly=True,
            )


        class Network(Base):
            __tablename__ = "network"

            id = mapped_column(Integer, primary_key=True)
            v4representation = mapped_column(CIDR)

    Above, a query such as::

        select(IPA).join(IPA.network)

    Will render as:

    .. sourcecode:: sql

        SELECT ip_address.id AS ip_address_id, ip_address.v4address AS ip_address_v4address
        FROM ip_address JOIN network ON ip_address.v4address << network.v4representation

.. _relationship_custom_operator_sql_function:

基于 SQL 函数的自定义运算符
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Custom operators based on SQL functions

.. tab:: 中文

    :param:`~.Operators.op.is_comparison` 的用例变体是当我们不使用运算符，而是使用 SQL 函数时。此用例的典型示例是 PostgreSQL PostGIS 函数，但任何解析为二进制条件的数据库上的任何 SQL 函数都可以应用。为了适应这种用例，:meth:`.FunctionElement.as_comparison` 方法可以修改任何 SQL 函数，例如从 :data:`.func` 命名空间调用的那些，以向 ORM 表明函数生成两个表达式的比较。下面的示例使用了 `Geoalchemy2 <https://geoalchemy-2.readthedocs.io/>`_ 库::

        from geoalchemy2 import Geometry
        from sqlalchemy import Column, Integer, func
        from sqlalchemy.orm import relationship, foreign


        class Polygon(Base):
            __tablename__ = "polygon"
            id = mapped_column(Integer, primary_key=True)
            geom = mapped_column(Geometry("POLYGON", srid=4326))
            points = relationship(
                "Point",
                primaryjoin="func.ST_Contains(foreign(Polygon.geom), Point.geom).as_comparison(1, 2)",
                viewonly=True,
            )


        class Point(Base):
            __tablename__ = "point"
            id = mapped_column(Integer, primary_key=True)
            geom = mapped_column(Geometry("POINT", srid=4326))

    上面，:meth:`.FunctionElement.as_comparison` 表示 ``func.ST_Contains()`` SQL 函数正在比较 ``Polygon.geom`` 和 ``Point.geom`` 表达式。:func:`.foreign` 注释另外指出在此特定关系中哪个列承担“外键”角色。

.. tab:: 英文

    A variant to the use case for :paramref:`~.Operators.op.is_comparison` is
    when we aren't using an operator, but a SQL function.   The typical example
    of this use case is the PostgreSQL PostGIS functions however any SQL
    function on any database that resolves to a binary condition may apply.
    To suit this use case, the :meth:`.FunctionElement.as_comparison` method
    can modify any SQL function, such as those invoked from the :data:`.func`
    namespace, to indicate to the ORM that the function produces a comparison of
    two expressions.  The below example illustrates this with the
    `Geoalchemy2 <https://geoalchemy-2.readthedocs.io/>`_ library::

        from geoalchemy2 import Geometry
        from sqlalchemy import Column, Integer, func
        from sqlalchemy.orm import relationship, foreign


        class Polygon(Base):
            __tablename__ = "polygon"
            id = mapped_column(Integer, primary_key=True)
            geom = mapped_column(Geometry("POLYGON", srid=4326))
            points = relationship(
                "Point",
                primaryjoin="func.ST_Contains(foreign(Polygon.geom), Point.geom).as_comparison(1, 2)",
                viewonly=True,
            )


        class Point(Base):
            __tablename__ = "point"
            id = mapped_column(Integer, primary_key=True)
            geom = mapped_column(Geometry("POINT", srid=4326))

    Above, the :meth:`.FunctionElement.as_comparison` indicates that the
    ``func.ST_Contains()`` SQL function is comparing the ``Polygon.geom`` and
    ``Point.geom`` expressions. The :func:`.foreign` annotation additionally notes
    which column takes on the "foreign key" role in this particular relationship.

.. _relationship_overlapping_foreignkeys:

重叠外键
~~~~~~~~~~~~~~~~~~~~~~~~

Overlapping Foreign Keys

.. tab:: 中文

    在使用复合外键时可能会出现一种罕见的情况，即单个列可能是通过外键约束引用的多个列的主题。

    考虑一个（确实复杂的）映射，例如 ``Magazine`` 对象，通过复合主键方案由 ``Writer`` 对象和 ``Article`` 对象引用，两者都包括 ``magazine_id``；然后为了使 ``Article`` 也引用 ``Writer``， ``Article.magazine_id`` 参与了两个单独的关系； ``Article.magazine`` 和 ``Article.writer``::

        class Magazine(Base):
            __tablename__ = "magazine"

            id = mapped_column(Integer, primary_key=True)


        class Article(Base):
            __tablename__ = "article"

            article_id = mapped_column(Integer)
            magazine_id = mapped_column(ForeignKey("magazine.id"))
            writer_id = mapped_column()

            magazine = relationship("Magazine")
            writer = relationship("Writer")

            __table_args__ = (
                PrimaryKeyConstraint("article_id", "magazine_id"),
                ForeignKeyConstraint(
                    ["writer_id", "magazine_id"], ["writer.id", "writer.magazine_id"]
                ),
            )


        class Writer(Base):
            __tablename__ = "writer"

            id = mapped_column(Integer, primary_key=True)
            magazine_id = mapped_column(ForeignKey("magazine.id"), primary_key=True)
            magazine = relationship("Magazine")

    配置上述映射时，我们会看到发出的警告：

    .. sourcecode:: text

        SAWarning: relationship 'Article.writer' will copy column
        writer.magazine_id to column article.magazine_id,
        which conflicts with relationship(s): 'Article.magazine'
        (copies magazine.id to article.magazine_id). Consider applying
        viewonly=True to read-only relationships, or provide a primaryjoin
        condition marking writable columns with the foreign() annotation.

    这源于这样一个事实，即 ``Article.magazine_id`` 是两个不同外键约束的主题；它直接作为源列引用 ``Magazine.id``，但在引用 ``Writer`` 的复合键的上下文中也作为源列引用 ``Writer.magazine_id``。如果我们将一个 ``Article`` 与一个特定的 ``Magazine`` 关联起来，但随后将 ``Article`` 与一个与 *不同* 的 ``Magazine`` 关联的 ``Writer`` 关联，那么 ORM 将以非确定性的方式覆盖 ``Article.magazine_id``，静默地更改我们引用的杂志；如果我们将 ``Writer`` 与 ``Article`` 取消关联，它也可能尝试将 NULL 放入此列中。警告让我们知道这是事实。

    为了解决这个问题，我们需要将 ``Article`` 的行为分解为包括以下三个特性：

    1. ``Article`` 首先根据仅在 ``Article.magazine`` 关系中持久化的数据写入 ``Article.magazine_id``，即从 ``Magazine.id`` 复制的值。

    2. ``Article`` 可以代表在 ``Article.writer`` 关系中持久化的数据写入 ``Article.writer_id``，但仅写入 ``Writer.id`` 列；``Writer.magazine_id`` 列不应该写入 ``Article.magazine_id``，因为它最终来自 ``Magazine.id``。

    3. ``Article`` 在加载 ``Article.writer`` 时会考虑 ``Article.magazine_id``，尽管它*不会*代表此关系写入它。

    为了实现 #1 和 #2，我们可以仅将 ``Article.writer_id`` 指定为 ``Article.writer`` 的“外键”::

        class Article(Base):
            # ...

            writer = relationship("Writer", foreign_keys="Article.writer_id")

    然而，这样做的效果是 ``Article.writer`` 在查询 ``Writer`` 时不考虑 ``Article.magazine_id``:

    .. sourcecode:: sql

        SELECT article.article_id AS article_article_id,
            article.magazine_id AS article_magazine_id,
            article.writer_id AS article_writer_id
        FROM article
        JOIN writer ON writer.id = article.writer_id

    因此，为了实现 #1、#2 和 #3，我们可以通过完全表达连接条件以及要写入的列来实现，结合使用 :paramref:`_orm.relationship.primaryjoin`，以及 :paramref:`_orm.relationship.foreign_keys` 参数，或者更简洁地通过注释 :func:`_orm.foreign`::

        class Article(Base):
            # ...

            writer = relationship(
                "Writer",
                primaryjoin="and_(Writer.id == foreign(Article.writer_id), "
                "Writer.magazine_id == Article.magazine_id)",
            )

.. tab:: 英文

    A rare scenario can arise when composite foreign keys are used, such that
    a single column may be the subject of more than one column
    referred to via foreign key constraint.
    
    Consider an (admittedly complex) mapping such as the ``Magazine`` object,
    referred to both by the ``Writer`` object and the ``Article`` object
    using a composite primary key scheme that includes ``magazine_id``
    for both; then to make ``Article`` refer to ``Writer`` as well,
    ``Article.magazine_id`` is involved in two separate relationships;
    ``Article.magazine`` and ``Article.writer``::
    
        class Magazine(Base):
            __tablename__ = "magazine"
    
            id = mapped_column(Integer, primary_key=True)
    
    
        class Article(Base):
            __tablename__ = "article"
    
            article_id = mapped_column(Integer)
            magazine_id = mapped_column(ForeignKey("magazine.id"))
            writer_id = mapped_column()
    
            magazine = relationship("Magazine")
            writer = relationship("Writer")
    
            __table_args__ = (
                PrimaryKeyConstraint("article_id", "magazine_id"),
                ForeignKeyConstraint(
                    ["writer_id", "magazine_id"], ["writer.id", "writer.magazine_id"]
                ),
            )
    
    
        class Writer(Base):
            __tablename__ = "writer"
    
            id = mapped_column(Integer, primary_key=True)
            magazine_id = mapped_column(ForeignKey("magazine.id"), primary_key=True)
            magazine = relationship("Magazine")
    
    When the above mapping is configured, we will see this warning emitted:
    
    .. sourcecode:: text
    
        SAWarning: relationship 'Article.writer' will copy column
        writer.magazine_id to column article.magazine_id,
        which conflicts with relationship(s): 'Article.magazine'
        (copies magazine.id to article.magazine_id). Consider applying
        viewonly=True to read-only relationships, or provide a primaryjoin
        condition marking writable columns with the foreign() annotation.
    
    What this refers to originates from the fact that ``Article.magazine_id`` is
    the subject of two different foreign key constraints; it refers to
    ``Magazine.id`` directly as a source column, but also refers to
    ``Writer.magazine_id`` as a source column in the context of the
    composite key to ``Writer``.   If we associate an ``Article`` with a
    particular ``Magazine``, but then associate the ``Article`` with a
    ``Writer`` that's  associated  with a *different* ``Magazine``, the ORM
    will overwrite ``Article.magazine_id`` non-deterministically, silently
    changing which magazine to which we refer; it may
    also attempt to place NULL into this column if we de-associate a
    ``Writer`` from an ``Article``.  The warning lets us know this is the case.
    
    To solve this, we need to break out the behavior of ``Article`` to include
    all three of the following features:
    
    1. ``Article`` first and foremost writes to
       ``Article.magazine_id`` based on data persisted in the ``Article.magazine``
       relationship only, that is a value copied from ``Magazine.id``.
    
    2. ``Article`` can write to ``Article.writer_id`` on behalf of data
       persisted in the  ``Article.writer`` relationship, but only the
       ``Writer.id`` column; the ``Writer.magazine_id`` column should not
       be written into ``Article.magazine_id`` as it ultimately is sourced
       from ``Magazine.id``.
    
    3. ``Article`` takes ``Article.magazine_id`` into account when loading
       ``Article.writer``, even though it *doesn't* write to it on behalf
       of this relationship.
    
    To get just #1 and #2, we could specify only ``Article.writer_id`` as the
    "foreign keys" for ``Article.writer``::
    
        class Article(Base):
            # ...
    
            writer = relationship("Writer", foreign_keys="Article.writer_id")
    
    However, this has the effect of ``Article.writer`` not taking
    ``Article.magazine_id`` into account when querying against ``Writer``:
    
    .. sourcecode:: sql
    
        SELECT article.article_id AS article_article_id,
            article.magazine_id AS article_magazine_id,
            article.writer_id AS article_writer_id
        FROM article
        JOIN writer ON writer.id = article.writer_id
    
    Therefore, to get at all of #1, #2, and #3, we express the join condition
    as well as which columns to be written by combining
    :paramref:`_orm.relationship.primaryjoin` fully, along with either the
    :paramref:`_orm.relationship.foreign_keys` argument, or more succinctly by
    annotating with :func:`_orm.foreign`::
    
        class Article(Base):
            # ...
    
            writer = relationship(
                "Writer",
                primaryjoin="and_(Writer.id == foreign(Article.writer_id), "
                "Writer.magazine_id == Article.magazine_id)",
            )

非关系比较/物化路径
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Non-relational Comparisons / Materialized Path

.. tab:: 中文

    .. warning::  本节详细介绍了一个实验性功能。

    使用自定义表达式意味着我们可以生成不遵循通常主键/外键模型的不正统连接条件。一个这样的例子是物化路径模式，我们比较字符串以获得重叠的路径标记，从而生成树结构。

    通过谨慎使用 :func:`.foreign` 和 :func:`.remote`，我们可以构建一个有效地生成基本物化路径系统的关系。本质上，当 :func:`.foreign` 和 :func:`.remote` 在比较表达式的*同一*侧时，关系被认为是“一对多”；当它们在 *不同* 侧时，关系被认为是“多对一”。对于这里使用的比较，我们将处理集合，因此我们将其配置为“一对多”：

        class Element(Base):
            __tablename__ = "element"

            path = mapped_column(String, primary_key=True)

            descendants = relationship(
                "Element",
                primaryjoin=remote(foreign(path)).like(path.concat("/%")),
                viewonly=True,
                order_by=path,
            )

    上面，如果给定一个路径属性为 ``"/foo/bar2"`` 的 ``Element`` 对象，我们希望加载 ``Element.descendants`` 看起来像：

    .. sourcecode:: sql

        SELECT element.path AS element_path
        FROM element
        WHERE element.path LIKE ('/foo/bar2' || '/%') ORDER BY element.path

.. tab:: 英文

    .. warning::  this section details an experimental feature.

    Using custom expressions means we can produce unorthodox join conditions that
    don't obey the usual primary/foreign key model.  One such example is the
    materialized path pattern, where we compare strings for overlapping path tokens
    in order to produce a tree structure.

    Through careful use of :func:`.foreign` and :func:`.remote`, we can build
    a relationship that effectively produces a rudimentary materialized path
    system.   Essentially, when :func:`.foreign` and :func:`.remote` are
    on the *same* side of the comparison expression, the relationship is considered
    to be "one to many"; when they are on *different* sides, the relationship
    is considered to be "many to one".   For the comparison we'll use here,
    we'll be dealing with collections so we keep things configured as "one to many"::

        class Element(Base):
            __tablename__ = "element"

            path = mapped_column(String, primary_key=True)

            descendants = relationship(
                "Element",
                primaryjoin=remote(foreign(path)).like(path.concat("/%")),
                viewonly=True,
                order_by=path,
            )

    Above, if given an ``Element`` object with a path attribute of ``"/foo/bar2"``,
    we seek for a load of ``Element.descendants`` to look like:

    .. sourcecode:: sql

        SELECT element.path AS element_path
        FROM element
        WHERE element.path LIKE ('/foo/bar2' || '/%') ORDER BY element.path

.. _self_referential_many_to_many:

自引用多对多关系
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Self-Referential Many-to-Many Relationship

.. tab:: 中文

    .. seealso::

        本节记录了“邻接列表”模式的两表变体，该模式记录在 :ref:`self_referential` 中。请务必查看子部分中的自引用查询模式
        :ref:`self_referential_query` 和 :ref:`self_referential_eager_loading`，这些模式同样适用于此处讨论的映射模式。

    多对多关系可以通过 :paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 之一或两者进行定制 - 后者对于使用 :paramref:`_orm.relationship.secondary` 参数指定多对多引用的关系非常重要。
    一种涉及使用 :paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 的常见情况是建立一个从类到自身的多对多关系，如下所示::

        from typing import List

        from sqlalchemy import Integer, ForeignKey, Column, Table
        from sqlalchemy.orm import DeclarativeBase, Mapped
        from sqlalchemy.orm import mapped_column, relationship


        class Base(DeclarativeBase):
            pass


        node_to_node = Table(
            "node_to_node",
            Base.metadata,
            Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
            Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
        )


        class Node(Base):
            __tablename__ = "node"
            id: Mapped[int] = mapped_column(primary_key=True)
            label: Mapped[str]
            right_nodes: Mapped[List["Node"]] = relationship(
                "Node",
                secondary=node_to_node,
                primaryjoin=id == node_to_node.c.left_node_id,
                secondaryjoin=id == node_to_node.c.right_node_id,
                back_populates="left_nodes",
            )
            left_nodes: Mapped[List["Node"]] = relationship(
                "Node",
                secondary=node_to_node,
                primaryjoin=id == node_to_node.c.right_node_id,
                secondaryjoin=id == node_to_node.c.left_node_id,
                back_populates="right_nodes",
            )

    如上所示，SQLAlchemy 无法自动知道哪些列应该连接到 ``right_nodes`` 和 ``left_nodes`` 关系。:paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 参数建立了我们希望如何连接到关联表。
    在上面的声明形式中，由于我们在与 ``Node`` 类对应的 Python 块中声明了这些条件，所以 ``id`` 变量可以直接作为我们希望连接的 :class:`_schema.Column` 对象使用。

    或者，我们可以使用字符串定义 :paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 参数，这在我们的配置中尚未提供 ``Node.id`` 列对象或 ``node_to_node`` 表可能尚未可用的情况下是合适的。
    当在声明字符串中引用普通的 :class:`_schema.Table` 对象时，我们使用表在 :class:`_schema.MetaData` 中的字符串名称::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            label = mapped_column(String)
            right_nodes = relationship(
                "Node",
                secondary="node_to_node",
                primaryjoin="Node.id==node_to_node.c.left_node_id",
                secondaryjoin="Node.id==node_to_node.c.right_node_id",
                backref="left_nodes",
            )

    .. warning:: 
        
        当作为 Python 可评估字符串传递时，:paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 参数使用 Python 的 ``eval()`` 函数进行解释。 **不要将不受信任的输入传递给这些字符串**。有关声明式评估 :func:`_orm.relationship` 参数的详细信息，请参见 :ref:`declarative_relationship_eval`。


    这里的经典映射情况类似，其中 ``node_to_node`` 可以连接到 ``node.c.id``::

        from sqlalchemy import Integer, ForeignKey, String, Column, Table, MetaData
        from sqlalchemy.orm import relationship, registry

        metadata_obj = MetaData()
        mapper_registry = registry()

        node_to_node = Table(
            "node_to_node",
            metadata_obj,
            Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
            Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
        )

        node = Table(
            "node",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("label", String),
        )


        class Node:
            pass


        mapper_registry.map_imperatively(
            Node,
            node,
            properties={
                "right_nodes": relationship(
                    Node,
                    secondary=node_to_node,
                    primaryjoin=node.c.id == node_to_node.c.left_node_id,
                    secondaryjoin=node.c.id == node_to_node.c.right_node_id,
                    backref="left_nodes",
                )
            },
        )

    请注意，在这两个示例中，:paramref:`_orm.relationship.backref` 关键字指定了一个 ``left_nodes`` 反向引用 - 当 :func:`_orm.relationship` 以相反方向创建第二个关系时，它足够智能地反转 :paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin` 参数。

    .. seealso::

    * :ref:`self_referential` - 单表版本
    * :ref:`self_referential_query` - 自引用映射查询提示
    * :ref:`self_referential_eager_loading` - 自引用映射预加载提示

.. tab:: 英文

    .. seealso::
    
        This section documents a two-table variant of the "adjacency list" pattern,
        which is documented at :ref:`self_referential`.  Be sure to review the
        self-referential querying patterns in subsections
        :ref:`self_referential_query` and :ref:`self_referential_eager_loading`
        which apply equally well to the mapping pattern discussed here.
    
    Many to many relationships can be customized by one or both of :paramref:`_orm.relationship.primaryjoin`
    and :paramref:`_orm.relationship.secondaryjoin` - the latter is significant for a relationship that
    specifies a many-to-many reference using the :paramref:`_orm.relationship.secondary` argument.
    A common situation which involves the usage of :paramref:`_orm.relationship.primaryjoin` and :paramref:`_orm.relationship.secondaryjoin`
    is when establishing a many-to-many relationship from a class to itself, as shown below::
    
        from typing import List
    
        from sqlalchemy import Integer, ForeignKey, Column, Table
        from sqlalchemy.orm import DeclarativeBase, Mapped
        from sqlalchemy.orm import mapped_column, relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        node_to_node = Table(
            "node_to_node",
            Base.metadata,
            Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
            Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
        )
    
    
        class Node(Base):
            __tablename__ = "node"
            id: Mapped[int] = mapped_column(primary_key=True)
            label: Mapped[str]
            right_nodes: Mapped[List["Node"]] = relationship(
                "Node",
                secondary=node_to_node,
                primaryjoin=id == node_to_node.c.left_node_id,
                secondaryjoin=id == node_to_node.c.right_node_id,
                back_populates="left_nodes",
            )
            left_nodes: Mapped[List["Node"]] = relationship(
                "Node",
                secondary=node_to_node,
                primaryjoin=id == node_to_node.c.right_node_id,
                secondaryjoin=id == node_to_node.c.left_node_id,
                back_populates="right_nodes",
            )
    
    Where above, SQLAlchemy can't know automatically which columns should connect
    to which for the ``right_nodes`` and ``left_nodes`` relationships.   The :paramref:`_orm.relationship.primaryjoin`
    and :paramref:`_orm.relationship.secondaryjoin` arguments establish how we'd like to join to the association table.
    In the Declarative form above, as we are declaring these conditions within the Python
    block that corresponds to the ``Node`` class, the ``id`` variable is available directly
    as the :class:`_schema.Column` object we wish to join with.
    
    Alternatively, we can define the :paramref:`_orm.relationship.primaryjoin`
    and :paramref:`_orm.relationship.secondaryjoin` arguments using strings, which is suitable
    in the case that our configuration does not have either the ``Node.id`` column
    object available yet or the ``node_to_node`` table perhaps isn't yet available.
    When referring to a plain :class:`_schema.Table` object in a declarative string, we
    use the string name of the table as it is present in the :class:`_schema.MetaData`::
    
        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            label = mapped_column(String)
            right_nodes = relationship(
                "Node",
                secondary="node_to_node",
                primaryjoin="Node.id==node_to_node.c.left_node_id",
                secondaryjoin="Node.id==node_to_node.c.right_node_id",
                backref="left_nodes",
            )
    
    .. warning:: When passed as a Python-evaluable string, the
        :paramref:`_orm.relationship.primaryjoin` and
        :paramref:`_orm.relationship.secondaryjoin` arguments are interpreted using
        Python's ``eval()`` function. **DO NOT PASS UNTRUSTED INPUT TO THESE
        STRINGS**. See :ref:`declarative_relationship_eval` for details on
        declarative evaluation of :func:`_orm.relationship` arguments.
    
    
    A classical mapping situation here is similar, where ``node_to_node`` can be joined
    to ``node.c.id``::
    
        from sqlalchemy import Integer, ForeignKey, String, Column, Table, MetaData
        from sqlalchemy.orm import relationship, registry
    
        metadata_obj = MetaData()
        mapper_registry = registry()
    
        node_to_node = Table(
            "node_to_node",
            metadata_obj,
            Column("left_node_id", Integer, ForeignKey("node.id"), primary_key=True),
            Column("right_node_id", Integer, ForeignKey("node.id"), primary_key=True),
        )
    
        node = Table(
            "node",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("label", String),
        )
    
    
        class Node:
            pass
    
    
        mapper_registry.map_imperatively(
            Node,
            node,
            properties={
                "right_nodes": relationship(
                    Node,
                    secondary=node_to_node,
                    primaryjoin=node.c.id == node_to_node.c.left_node_id,
                    secondaryjoin=node.c.id == node_to_node.c.right_node_id,
                    backref="left_nodes",
                )
            },
        )
    
    Note that in both examples, the :paramref:`_orm.relationship.backref`
    keyword specifies a ``left_nodes`` backref - when
    :func:`_orm.relationship` creates the second relationship in the reverse
    direction, it's smart enough to reverse the
    :paramref:`_orm.relationship.primaryjoin` and
    :paramref:`_orm.relationship.secondaryjoin` arguments.
    
    .. seealso::
    
      * :ref:`self_referential` - single table version
      * :ref:`self_referential_query` - tips on querying with self-referential
        mappings
      * :ref:`self_referential_eager_loading` - tips on eager loading with self-
        referential mapping

.. _composite_secondary_join:

复合“次要”连接
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Composite "Secondary" Joins

.. tab:: 中文

    .. note::

        本节介绍了 SQLAlchemy 支持的一些极端情况，但建议尽可能通过使用合理的关系布局和/或 :ref:`in-Python attributes <mapper_hybrids>` 以更简单的方式解决这些问题。

    有时，当需要在两个表之间建立 :func:`_orm.relationship` 时，需要涉及两个或三个以上的表才能将它们连接起来。这是一个 :func:`_orm.relationship` 的领域，试图突破可能的界限，许多这些特殊用例的最终解决方案通常需要在 SQLAlchemy 邮件列表中讨论。

    在较新的 SQLAlchemy 版本中，可以在某些情况下使用 :paramref:`_orm.relationship.secondary` 参数来提供由多个表组成的复合目标。以下是这样的连接条件的示例（要求至少版本 0.9.2 才能按原样运行）::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))

            d = relationship(
                "D",
                secondary="join(B, D, B.d_id == D.id).join(C, C.d_id == D.id)",
                primaryjoin="and_(A.b_id == B.id, A.id == C.a_id)",
                secondaryjoin="D.id == B.d_id",
                uselist=False,
                viewonly=True,
            )


        class B(Base):
            __tablename__ = "b"

            id = mapped_column(Integer, primary_key=True)
            d_id = mapped_column(ForeignKey("d.id"))


        class C(Base):
            __tablename__ = "c"

            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))
            d_id = mapped_column(ForeignKey("d.id"))


        class D(Base):
            __tablename__ = "d"

            id = mapped_column(Integer, primary_key=True)

    在上面的示例中，我们以声明方式提供了 :paramref:`_orm.relationship.secondary`、:paramref:`_orm.relationship.primaryjoin` 和 :paramref:`_orm.relationship.secondaryjoin`，直接引用命名表 ``a``、 ``b``、 ``c``、 ``d``。从 ``A`` 到 ``D`` 的查询如下所示：

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.d)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (
            b AS b_1 JOIN d AS d_1 ON b_1.d_id = d_1.id
                JOIN c AS c_1 ON c_1.d_id = d_1.id)
            ON a.b_id = b_1.id AND a.id = c_1.a_id JOIN d ON d.id = b_1.d_id

    在上面的示例中，我们利用能够将多个表放入“secondary”容器的优势，以便我们可以跨多个表进行连接，同时保持 :func:`_orm.relationship` 的“简单性”，因为在“左侧”和“右侧”都有“一个”表；复杂性保持在中间。

    .. warning:: 
        
        像上面这样的关系通常标记为 ``viewonly=True``，使用 :paramref:`_orm.relationship.viewonly`，并应被视为只读。尽管有时可以使这样的关系可写，但这通常很复杂且容易出错。

    .. seealso::

        :ref:`relationship_viewonly_notes`

.. tab:: 英文

    .. note::

        This section features far edge cases that are somewhat supported
        by SQLAlchemy, however it is recommended to solve problems like these
        in simpler ways whenever possible, by using reasonable relational
        layouts and / or :ref:`in-Python attributes <mapper_hybrids>`.

    Sometimes, when one seeks to build a :func:`_orm.relationship` between two tables
    there is a need for more than just two or three tables to be involved in
    order to join them.  This is an area of :func:`_orm.relationship` where one seeks
    to push the boundaries of what's possible, and often the ultimate solution to
    many of these exotic use cases needs to be hammered out on the SQLAlchemy mailing
    list.

    In more recent versions of SQLAlchemy, the :paramref:`_orm.relationship.secondary`
    parameter can be used in some of these cases in order to provide a composite
    target consisting of multiple tables.   Below is an example of such a
    join condition (requires version 0.9.2 at least to function as is)::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))

            d = relationship(
                "D",
                secondary="join(B, D, B.d_id == D.id).join(C, C.d_id == D.id)",
                primaryjoin="and_(A.b_id == B.id, A.id == C.a_id)",
                secondaryjoin="D.id == B.d_id",
                uselist=False,
                viewonly=True,
            )


        class B(Base):
            __tablename__ = "b"

            id = mapped_column(Integer, primary_key=True)
            d_id = mapped_column(ForeignKey("d.id"))


        class C(Base):
            __tablename__ = "c"

            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))
            d_id = mapped_column(ForeignKey("d.id"))


        class D(Base):
            __tablename__ = "d"

            id = mapped_column(Integer, primary_key=True)

    In the above example, we provide all three of :paramref:`_orm.relationship.secondary`,
    :paramref:`_orm.relationship.primaryjoin`, and :paramref:`_orm.relationship.secondaryjoin`,
    in the declarative style referring to the named tables ``a``, ``b``, ``c``, ``d``
    directly.  A query from ``A`` to ``D`` looks like:

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.d)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (
            b AS b_1 JOIN d AS d_1 ON b_1.d_id = d_1.id
                JOIN c AS c_1 ON c_1.d_id = d_1.id)
            ON a.b_id = b_1.id AND a.id = c_1.a_id JOIN d ON d.id = b_1.d_id

    In the above example, we take advantage of being able to stuff multiple
    tables into a "secondary" container, so that we can join across many
    tables while still keeping things "simple" for :func:`_orm.relationship`, in that
    there's just "one" table on both the "left" and the "right" side; the
    complexity is kept within the middle.

    .. warning:: 
        
        A relationship like the above is typically marked as ``viewonly=True``, using :paramref:`_orm.relationship.viewonly`, and should be considered as read-only.  While there are sometimes ways to make relationships like the above writable, this is generally complicated and error prone.

    .. seealso::

        :ref:`relationship_viewonly_notes`



.. _relationship_non_primary_mapper:

.. _relationship_aliased_class:

与别名类的关系
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Relationship to Aliased Class

.. tab:: 中文

    在上一节中，我们展示了一种技术，其中使用 :paramref:`_orm.relationship.secondary` 将附加表放入连接条件中。有一种复杂的连接情况，即使这种技术也不足以解决；当我们希望从 ``A`` 连接到 ``B`` 时，使用任意数量的中间表 ``C``、``D`` 等，但在 ``A`` 和 ``B`` 之间也有直接的连接条件。在这种情况下，从 ``A`` 到 ``B`` 的连接可能很难仅通过复杂的 :paramref:`_orm.relationship.primaryjoin` 条件来表达，因为中间表可能需要特殊处理，并且不能通过 :paramref:`_orm.relationship.secondary` 对象来表达，因为 ``A->secondary->B`` 模式不支持在 ``A`` 和 ``B`` 之间的任何直接引用。当遇到这种 **极其高级** 情况时，我们可以求助于创建第二个映射作为关系的目标。这就是我们使用 :class:`.AliasedClass` 来映射一个包含我们需要的所有附加表的类。为了产生这个类的“替代”映射，我们使用 :func:`.aliased` 函数生成新的构造，然后对该对象使用 :func:`_orm.relationship` ，就像它是一个普通的映射类一样。

    下面展示了一个简单的从 ``A`` 到 ``B`` 的 :func:`_orm.relationship` 连接，但是 primaryjoin 条件通过两个附加实体 ``C`` 和 ``D`` 得到了增强，这些实体的行也必须同时与 ``A`` 和 ``B`` 的行对齐::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))


        class B(Base):
            __tablename__ = "b"

            id = mapped_column(Integer, primary_key=True)


        class C(Base):
            __tablename__ = "c"

            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))

            some_c_value = mapped_column(String)


        class D(Base):
            __tablename__ = "d"

            id = mapped_column(Integer, primary_key=True)
            c_id = mapped_column(ForeignKey("c.id"))
            b_id = mapped_column(ForeignKey("b.id"))

            some_d_value = mapped_column(String)


        # 1. 将 join() 设置为一个变量，以便我们可以在映射中多次引用它。
        j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)

        # 2. 创建一个 AliasedClass 到 B
        B_viacd = aliased(B, j, flat=True)

        A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)

    通过上述映射，一个简单的连接如下所示：

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.b)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) ON a.b_id = b.id

.. tab:: 英文

    In the previous section, we illustrated a technique where we used
    :paramref:`_orm.relationship.secondary` in order to place additional
    tables within a join condition.   There is one complex join case where
    even this technique is not sufficient; when we seek to join from ``A``
    to ``B``, making use of any number of ``C``, ``D``, etc. in between,
    however there are also join conditions between ``A`` and ``B``
    *directly*.  In this case, the join from ``A`` to ``B`` may be
    difficult to express with just a complex
    :paramref:`_orm.relationship.primaryjoin` condition, as the intermediary
    tables may need special handling, and it is also not expressible with
    a :paramref:`_orm.relationship.secondary` object, since the
    ``A->secondary->B`` pattern does not support any references between
    ``A`` and ``B`` directly.  When this **extremely advanced** case
    arises, we can resort to creating a second mapping as a target for the
    relationship.  This is where we use :class:`.AliasedClass` in order to make a
    mapping to a class that includes all the additional tables we need for
    this join. In order to produce this mapper as an "alternative" mapping
    for our class, we use the :func:`.aliased` function to produce the new
    construct, then use :func:`_orm.relationship` against the object as though it
    were a plain mapped class.

    Below illustrates a :func:`_orm.relationship` with a simple join from ``A`` to
    ``B``, however the primaryjoin condition is augmented with two additional
    entities ``C`` and ``D``, which also must have rows that line up with
    the rows in both ``A`` and ``B`` simultaneously::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))


        class B(Base):
            __tablename__ = "b"

            id = mapped_column(Integer, primary_key=True)


        class C(Base):
            __tablename__ = "c"

            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))

            some_c_value = mapped_column(String)


        class D(Base):
            __tablename__ = "d"

            id = mapped_column(Integer, primary_key=True)
            c_id = mapped_column(ForeignKey("c.id"))
            b_id = mapped_column(ForeignKey("b.id"))

            some_d_value = mapped_column(String)


        # 1. set up the join() as a variable, so we can refer
        # to it in the mapping multiple times.
        j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)

        # 2. Create an AliasedClass to B
        B_viacd = aliased(B, j, flat=True)

        A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)

    With the above mapping, a simple join looks like:

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.b)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) ON a.b_id = b.id

将 AliasedClass 映射与类型集成并避免早期映射器配置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Integrating AliasedClass Mappings with Typing and Avoiding Early Mapper Configuration

.. tab:: 中文

    创建 :func:`_orm.aliased` 构造针对映射类会强制 :func:`_orm.configure_mappers` 步骤进行，这将解析所有当前类及其关系。如果当前映射所需的无关映射类尚未声明，或者关系本身的配置需要访问尚未声明的类，这可能会有问题。此外，SQLAlchemy 的声明模式在关系声明在前时与 Python 类型最有效地协作。

    要组织关系的构造以解决这些问题，可以使用配置级事件钩子，如 :meth:`.MapperEvents.before_mapper_configured`，它将在所有映射准备好配置时调用配置代码::

        from sqlalchemy import event


        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))


        @event.listens_for(A, "before_mapper_configured")
        def _configure_ab_relationship(mapper, cls):
            # 在配置钩子中进行上述配置

            j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)
            B_viacd = aliased(B, j, flat=True)
            A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)

    如上所述，函数 ``_configure_ab_relationship()`` 仅在请求完全配置的 ``A`` 版本时调用，此时类 ``B``、``D`` 和 ``C`` 将可用。

    对于与内联类型集成的方法，可以使用类似的技术有效地生成用于别名类的“单例”创建模式，其中它作为全局变量进行延迟初始化，然后可以在关系内联中使用::

        from typing import Any

        B_viacd: Any = None
        b_viacd_join: Any = None


        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)
            b_id: Mapped[int] = mapped_column(ForeignKey("b.id"))

            # 1. 使用 lambdas 声明关系，允许其解析为延迟配置的目标
            b: Mapped[B] = relationship(
                lambda: B_viacd, primaryjoin=lambda: A.b_id == b_viacd_join.c.b_id
            )


        # 2. 使用 before_mapper_configured 钩子配置关系的目标。
        @event.listens_for(A, "before_mapper_configured")
        def _configure_ab_relationship(mapper, cls):
            # 3. 在配置钩子中将 join() 和 AliasedClass 设置为全局变量。

            global B_viacd, b_viacd_join

            b_viacd_join = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)
            B_viacd = aliased(B, b_viacd_join, flat=True)

.. tab:: 英文

    The creation of the :func:`_orm.aliased` construct against a mapped class
    forces the :func:`_orm.configure_mappers` step to proceed, which will resolve
    all current classes and their relationships.  This may be problematic if
    unrelated mapped classes needed by the current mappings have not yet been
    declared, or if the configuration of the relationship itself needs access
    to as-yet undeclared classes.  Additionally, SQLAlchemy's Declarative pattern
    works with Python typing most effectively when relationships are declared
    up front.

    To organize the construction of the relationship to work with these issues, a
    configure level event hook like :meth:`.MapperEvents.before_mapper_configured`
    may be used, which will invoke the configuration code only when all mappings
    are ready for configuration::

        from sqlalchemy import event


        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)
            b_id = mapped_column(ForeignKey("b.id"))


        @event.listens_for(A, "before_mapper_configured")
        def _configure_ab_relationship(mapper, cls):
            # do the above configuration in a configuration hook

            j = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)
            B_viacd = aliased(B, j, flat=True)
            A.b = relationship(B_viacd, primaryjoin=A.b_id == j.c.b_id)

    Above, the function ``_configure_ab_relationship()`` will be invoked only
    when a fully configured version of ``A`` is requested, at which point the
    classes ``B``, ``D`` and ``C`` would be available.

    For an approach that integrates with inline typing, a similar technique can be
    used to effectively generate a "singleton" creation pattern for the aliased
    class where it is late-initialized as a global variable, which can then be used
    in the relationship inline::

        from typing import Any

        B_viacd: Any = None
        b_viacd_join: Any = None


        class A(Base):
            __tablename__ = "a"

            id: Mapped[int] = mapped_column(primary_key=True)
            b_id: Mapped[int] = mapped_column(ForeignKey("b.id"))

            # 1. the relationship can be declared using lambdas, allowing it to resolve
            #    to targets that are late-configured
            b: Mapped[B] = relationship(
                lambda: B_viacd, primaryjoin=lambda: A.b_id == b_viacd_join.c.b_id
            )


        # 2. configure the targets of the relationship using a before_mapper_configured
        #    hook.
        @event.listens_for(A, "before_mapper_configured")
        def _configure_ab_relationship(mapper, cls):
            # 3. set up the join() and AliasedClass as globals from within
            #    the configuration hook.

            global B_viacd, b_viacd_join

            b_viacd_join = join(B, D, D.b_id == B.id).join(C, C.id == D.c_id)
            B_viacd = aliased(B, b_viacd_join, flat=True)

在查询中使用 AliasedClass 目标
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the AliasedClass target in Queries

.. tab:: 中文

    在前面的示例中， ``A.b`` 关系引用 ``B_viacd`` 实体作为目标，而 **不是** 直接引用 ``B`` 类。要添加涉及 ``A.b`` 关系的附加条件，通常需要直接引用 ``B_viacd``，而不是使用 ``B``，特别是在 ``A.b`` 的目标实体要转换为别名或子查询的情况下。下面展示了使用子查询而不是连接的相同关系::

        subq = select(B).join(D, D.b_id == B.id).join(C, C.id == D.c_id).subquery()

        B_viacd_subquery = aliased(B, subq)

        A.b = relationship(B_viacd_subquery, primaryjoin=A.b_id == subq.c.id)

    使用上述 ``A.b`` 关系的查询将呈现一个子查询：

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.b)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
        FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id

    如果我们想添加基于 ``A.b`` 连接的附加条件，必须以 ``B_viacd_subquery`` 而不是直接 ``B`` 的形式进行：

    .. sourcecode:: python+sql

        sess.scalars(
            select(A)
            .join(A.b)
            .where(B_viacd_subquery.some_b_column == "some b")
            .order_by(B_viacd_subquery.id)
        ).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
        FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id
        WHERE anon_1.some_b_column = ? ORDER BY anon_1.id

.. tab:: 英文

    In the previous example, the ``A.b`` relationship refers to the ``B_viacd``
    entity as the target, and **not** the ``B`` class directly. To add additional
    criteria involving the ``A.b`` relationship, it's typically necessary to
    reference the ``B_viacd`` directly rather than using ``B``, especially in a
    case where the target entity of ``A.b`` is to be transformed into an alias or a
    subquery. Below illustrates the same relationship using a subquery, rather than
    a join::

        subq = select(B).join(D, D.b_id == B.id).join(C, C.id == D.c_id).subquery()

        B_viacd_subquery = aliased(B, subq)

        A.b = relationship(B_viacd_subquery, primaryjoin=A.b_id == subq.c.id)

    A query using the above ``A.b`` relationship will render a subquery:

    .. sourcecode:: python+sql

        sess.scalars(select(A).join(A.b)).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
        FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id

    If we want to add additional criteria based on the ``A.b`` join, we must do
    so in terms of ``B_viacd_subquery`` rather than ``B`` directly:

    .. sourcecode:: python+sql

        sess.scalars(
            select(A)
            .join(A.b)
            .where(B_viacd_subquery.some_b_column == "some b")
            .order_by(B_viacd_subquery.id)
        ).all()

        {execsql}SELECT a.id AS a_id, a.b_id AS a_b_id
        FROM a JOIN (SELECT b.id AS id, b.some_b_column AS some_b_column
        FROM b JOIN d ON d.b_id = b.id JOIN c ON c.id = d.c_id) AS anon_1 ON a.b_id = anon_1.id
        WHERE anon_1.some_b_column = ? ORDER BY anon_1.id

.. _relationship_to_window_function:

使用窗口函数的行限制关系
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Row-Limited Relationships with Window Functions

.. tab:: 中文

    另一个有趣的用例是将关系应用到 :class:`.AliasedClass` 对象的情况，其中关系需要连接到任何形式的特殊 SELECT。一个场景是需要使用窗口函数，例如限制关系应该返回多少行。下面的示例展示了一个非主映射器关系，它将为每个集合加载前十个项目::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)


        class B(Base):
            __tablename__ = "b"
            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))


        partition = select(
            B, func.row_number().over(order_by=B.id, partition_by=B.a_id).label("index")
        ).alias()

        partitioned_b = aliased(B, partition)

        A.partitioned_bs = relationship(
            partitioned_b, primaryjoin=and_(partitioned_b.a_id == A.id, partition.c.index < 10)
        )

    我们可以在大多数加载器策略中使用上述 ``partitioned_bs`` 关系，例如 :func:`.selectinload`::

        for a1 in session.scalars(select(A).options(selectinload(A.partitioned_bs))):
            print(a1.partitioned_bs)  # <-- 最多不超过十个对象

    上述“selectinload”查询如下所示：

    .. sourcecode:: sql

        SELECT
            a_1.id AS a_1_id, anon_1.id AS anon_1_id, anon_1.a_id AS anon_1_a_id,
            anon_1.data AS anon_1_data, anon_1.index AS anon_1_index
        FROM a AS a_1
        JOIN (
            SELECT b.id AS id, b.a_id AS a_id, b.data AS data,
            row_number() OVER (PARTITION BY b.a_id ORDER BY b.id) AS index
            FROM b) AS anon_1
        ON anon_1.a_id = a_1.id AND anon_1.index < %(index_1)s
        WHERE a_1.id IN ( ... primary key collection ...)
        ORDER BY a_1.id

    如上所述，对于“a”中的每个匹配主键，我们将按“b.id”顺序获取前十个“bs”。通过在“a_id”上分区，我们确保每个“行号”都是特定于父“a_id”的。

    这样的映射通常还包括从“A”到“B”的“普通”关系，用于持久化操作以及需要每个“A”的完整“B”对象集时。

.. tab:: 英文

    Another interesting use case for relationships to :class:`.AliasedClass`
    objects are situations where
    the relationship needs to join to a specialized SELECT of any form.   One
    scenario is when the use of a window function is desired, such as to limit
    how many rows should be returned for a relationship.  The example below
    illustrates a non-primary mapper relationship that will load the first
    ten items for each collection::

        class A(Base):
            __tablename__ = "a"

            id = mapped_column(Integer, primary_key=True)


        class B(Base):
            __tablename__ = "b"
            id = mapped_column(Integer, primary_key=True)
            a_id = mapped_column(ForeignKey("a.id"))


        partition = select(
            B, func.row_number().over(order_by=B.id, partition_by=B.a_id).label("index")
        ).alias()

        partitioned_b = aliased(B, partition)

        A.partitioned_bs = relationship(
            partitioned_b, primaryjoin=and_(partitioned_b.a_id == A.id, partition.c.index < 10)
        )

    We can use the above ``partitioned_bs`` relationship with most of the loader
    strategies, such as :func:`.selectinload`::

        for a1 in session.scalars(select(A).options(selectinload(A.partitioned_bs))):
            print(a1.partitioned_bs)  # <-- will be no more than ten objects

    Where above, the "selectinload" query looks like:

    .. sourcecode:: sql

        SELECT
            a_1.id AS a_1_id, anon_1.id AS anon_1_id, anon_1.a_id AS anon_1_a_id,
            anon_1.data AS anon_1_data, anon_1.index AS anon_1_index
        FROM a AS a_1
        JOIN (
            SELECT b.id AS id, b.a_id AS a_id, b.data AS data,
            row_number() OVER (PARTITION BY b.a_id ORDER BY b.id) AS index
            FROM b) AS anon_1
        ON anon_1.a_id = a_1.id AND anon_1.index < %(index_1)s
        WHERE a_1.id IN ( ... primary key collection ...)
        ORDER BY a_1.id

    Above, for each matching primary key in "a", we will get the first ten
    "bs" as ordered by "b.id".   By partitioning on "a_id" we ensure that each
    "row number" is local to the parent "a_id".

    Such a mapping would ordinarily also include a "plain" relationship
    from "A" to "B", for persistence operations as well as when the full
    set of "B" objects per "A" is desired.

.. _query_enabled_properties:

构建启用查询的属性
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Building Query-Enabled Properties

.. tab:: 中文

    非常复杂的自定义连接条件可能无法直接持久化，在某些情况下甚至可能无法正确加载。要移除持久化部分，可以在 :func:`~sqlalchemy.orm.relationship` 上使用 :paramref:`_orm.relationship.viewonly` 标志，将其设为只读属性（写入集合的数据将在刷新时被忽略）。但是，在极端情况下，可以考虑将常规 Python 属性与 :class:`_query.Query` 结合使用，如下所示：

    .. sourcecode:: python

        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)

            @property
            def addresses(self):
                return object_session(self).query(Address).with_parent(self).filter(...).all()

    在其他情况下，描述符可以构建为利用现有的 Python 数据。有关特殊 Python 属性的更多讨论，请参见 :ref:`mapper_hybrids` 部分。

    .. seealso::

        :ref:`mapper_hybrids`

.. tab:: 英文

    Very ambitious custom join conditions may fail to be directly persistable, and
    in some cases may not even load correctly. To remove the persistence part of
    the equation, use the flag :paramref:`_orm.relationship.viewonly` on the
    :func:`~sqlalchemy.orm.relationship`, which establishes it as a read-only
    attribute (data written to the collection will be ignored on flush()).
    However, in extreme cases, consider using a regular Python property in
    conjunction with :class:`_query.Query` as follows:

    .. sourcecode:: python

        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)

            @property
            def addresses(self):
                return object_session(self).query(Address).with_parent(self).filter(...).all()

    In other cases, the descriptor can be built to make use of existing in-Python
    data.  See the section on :ref:`mapper_hybrids` for more general discussion
    of special Python attributes.

    .. seealso::

        :ref:`mapper_hybrids`

.. _relationship_viewonly_notes:

使用 viewonly 关系参数的注意事项
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Notes on using the viewonly relationship parameter

.. tab:: 中文

    :paramref:`_orm.relationship.viewonly` 参数应用于 :func:`_orm.relationship` 构造时，表示该 :func:`_orm.relationship` 不会参与任何 ORM :term:`unit of work` 操作，此外，该属性不期望参与其表示的集合的 Python 内部变异。这意味着虽然 viewonly 关系可能引用可变的 Python 集合（如列表或集合），但在映射实例上对该列表或集合进行更改对 ORM 刷新过程 **没有影响**。

    要探索此场景，请考虑以下映射::

        from __future__ import annotations

        import datetime

        from sqlalchemy import and_
        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None]

            all_tasks: Mapped[list[Task]] = relationship()

            current_week_tasks: Mapped[list[Task]] = relationship(
                primaryjoin=lambda: and_(
                    User.id == Task.user_account_id,
                    # 该表达式适用于 PostgreSQL，但可能不支持其他数据库引擎
                    Task.task_date >= func.now() - datetime.timedelta(days=7),
                ),
                viewonly=True,
            )


        class Task(Base):
            __tablename__ = "task"

            id: Mapped[int] = mapped_column(primary_key=True)
            user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
            description: Mapped[str | None]
            task_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

            user: Mapped[User] = relationship(back_populates="current_week_tasks")

    以下部分将指出此配置的不同方面。

.. tab:: 英文

    The :paramref:`_orm.relationship.viewonly` parameter when applied to a
    :func:`_orm.relationship` construct indicates that this :func:`_orm.relationship`
    will not take part in any ORM :term:`unit of work` operations, and additionally
    that the attribute does not expect to participate within in-Python mutations
    of its represented collection.  This means
    that while the viewonly relationship may refer to a mutable Python collection
    like a list or set, making changes to that list or set as present on a
    mapped instance will have **no effect** on the ORM flush process.

    To explore this scenario consider this mapping::

        from __future__ import annotations

        import datetime

        from sqlalchemy import and_
        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None]

            all_tasks: Mapped[list[Task]] = relationship()

            current_week_tasks: Mapped[list[Task]] = relationship(
                primaryjoin=lambda: and_(
                    User.id == Task.user_account_id,
                    # this expression works on PostgreSQL but may not be supported
                    # by other database engines
                    Task.task_date >= func.now() - datetime.timedelta(days=7),
                ),
                viewonly=True,
            )


        class Task(Base):
            __tablename__ = "task"

            id: Mapped[int] = mapped_column(primary_key=True)
            user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
            description: Mapped[str | None]
            task_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

            user: Mapped[User] = relationship(back_populates="current_week_tasks")

    The following sections will note different aspects of this configuration.

在 Python 中，包括 backref 的突变不适用于 viewonly=True
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In-Python mutations including backrefs are not appropriate with viewonly=True

.. tab:: 中文

    上面的映射将 ``User.current_week_tasks`` 视为 ``Task.user`` 属性的 :term:`backref` 目标。SQLAlchemy 的 ORM 配置过程目前不会对此进行标记，但这实际上是一个配置错误。更改 ``Task`` 上的 ``.user`` 属性不会影响 ``.current_week_tasks`` 属性::

        >>> u1 = User()
        >>> t1 = Task(task_date=datetime.datetime.now())
        >>> t1.user = u1
        >>> u1.current_week_tasks
        []

    这里有另一个名为 :paramref:`_orm.relationship.sync_backrefs` 的参数，可以打开它以允许在这种情况下更改 ``.current_week_tasks``，但这不被认为是 viewonly 关系的最佳实践，viewonly 关系不应该依赖于 Python 内部变异。

    在此映射中，可以在 ``User.all_tasks`` 和 ``Task.user`` 之间配置 backrefs，因为它们都不是 viewonly 并且将正常同步。

    除了 viewonly 关系禁用 backref 变异的问题外，Python 中对 ``User.all_tasks`` 集合的简单更改在将更改刷新到数据库之前，也不会反映在 ``User.current_week_tasks`` 集合中。

    总体而言，对于需要自定义集合立即响应 Python 内部变异的用例，viewonly 关系通常不合适。更好的方法是使用 SQLAlchemy 的 :ref:`hybrids_toplevel` 功能，或对于仅实例的情况使用 Python ``@property``，其中可以实现基于当前 Python 实例生成的用户定义集合。要更改我们的示例以这种方式工作，我们修复 ``Task.user`` 上的 :paramref:`_orm.relationship.back_populates` 参数以引用 ``User.all_tasks``，然后展示一个简单的 ``@property``，该属性将根据即时的 ``User.all_tasks`` 集合提供结果::

        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None]

            all_tasks: Mapped[list[Task]] = relationship(back_populates="user")

            @property
            def current_week_tasks(self) -> list[Task]:
                past_seven_days = datetime.datetime.now() - datetime.timedelta(days=7)
                return [t for t in self.all_tasks if t.task_date >= past_seven_days]


        class Task(Base):
            __tablename__ = "task"

            id: Mapped[int] = mapped_column(primary_key=True)
            user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
            description: Mapped[str | None]
            task_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

            user: Mapped[User] = relationship(back_populates="all_tasks")

    使用每次动态计算的 Python 集合，我们可以保证始终获得正确的答案，而无需使用数据库::

        >>> u1 = User()
        >>> t1 = Task(task_date=datetime.datetime.now())
        >>> t1.user = u1
        >>> u1.current_week_tasks
        [<__main__.Task object at 0x7f3d699523c0>]

.. tab:: 英文

    The above mapping targets the ``User.current_week_tasks`` viewonly relationship
    as the :term:`backref` target of the ``Task.user`` attribute.  This is not
    currently flagged by SQLAlchemy's ORM configuration process, however is a
    configuration error.   Changing the ``.user`` attribute on a ``Task`` will not
    affect the ``.current_week_tasks`` attribute::

        >>> u1 = User()
        >>> t1 = Task(task_date=datetime.datetime.now())
        >>> t1.user = u1
        >>> u1.current_week_tasks
        []

    There is another parameter called :paramref:`_orm.relationship.sync_backrefs`
    which can be turned on here to allow ``.current_week_tasks`` to be mutated in this
    case, however this is not considered to be a best practice with a viewonly
    relationship, which instead should not be relied upon for in-Python mutations.

    In this mapping, backrefs can be configured between ``User.all_tasks`` and
    ``Task.user``, as these are both not viewonly and will synchronize normally.

    Beyond the issue of backref mutations being disabled for viewonly relationships,
    plain changes to the ``User.all_tasks`` collection in Python
    are also not reflected in the ``User.current_week_tasks`` collection until
    changes have been flushed to the database.

    Overall, for a use case where a custom collection should respond immediately to
    in-Python mutations, the viewonly relationship is generally not appropriate.  A
    better approach is to use the :ref:`hybrids_toplevel` feature of SQLAlchemy, or
    for instance-only cases to use a Python ``@property``, where a user-defined
    collection that is generated in terms of the current Python instance can be
    implemented.  To change our example to work this way, we repair the
    :paramref:`_orm.relationship.back_populates` parameter on ``Task.user`` to
    reference ``User.all_tasks``, and
    then illustrate a simple ``@property`` that will deliver results in terms of
    the immediate ``User.all_tasks`` collection::

        class User(Base):
            __tablename__ = "user_account"

            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str | None]

            all_tasks: Mapped[list[Task]] = relationship(back_populates="user")

            @property
            def current_week_tasks(self) -> list[Task]:
                past_seven_days = datetime.datetime.now() - datetime.timedelta(days=7)
                return [t for t in self.all_tasks if t.task_date >= past_seven_days]


        class Task(Base):
            __tablename__ = "task"

            id: Mapped[int] = mapped_column(primary_key=True)
            user_account_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
            description: Mapped[str | None]
            task_date: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

            user: Mapped[User] = relationship(back_populates="all_tasks")

    Using an in-Python collection calculated on the fly each time, we are guaranteed
    to have the correct answer at all times, without the need to use a database
    at all::

        >>> u1 = User()
        >>> t1 = Task(task_date=datetime.datetime.now())
        >>> t1.user = u1
        >>> u1.current_week_tasks
        [<__main__.Task object at 0x7f3d699523c0>]


viewonly=True 集合/属性在过期之前不会被重新查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

viewonly=True collections / attributes do not get re-queried until expired

.. tab:: 中文

    继续使用原始的 viewonly 属性，如果我们确实对 :term:`persistent` 对象上的 ``User.all_tasks`` 集合进行更改，那么 viewonly 集合只能在发生 **两** 件事后显示此更改的净结果。首先是对 ``User.all_tasks`` 的更改被 :term:`flushed`，以便新数据至少在本地事务范围内在数据库中可用。其次是 ``User.current_week_tasks`` 属性被 :term:`expired` 并通过新的 SQL 查询重新加载到数据库中。

    为了支持此要求，最简单的流程是仅在主要是只读的操作中使用 viewonly 关系。例如，如果我们从数据库中重新检索一个 ``User``，集合将是最新的：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f8711b906b0>]

    当我们对 ``u1.all_tasks`` 进行修改时，如果我们希望这些更改反映在 ``u1.current_week_tasks`` viewonly 关系中，这些更改需要被刷新，并且 ``u1.current_week_tasks`` 属性需要被过期，以便在下一次访问时 :term:`lazy load`。最简单的方法是使用 :meth:`_orm.Session.commit`，保持 :paramref:`_orm.Session.expire_on_commit` 参数设置为默认值 ``True``：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.commit()
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f8711b90ec0>, <__main__.Task object at 0x7f8711b90a10>]

    如上所述，调用 :meth:`_orm.Session.commit` 将 ``u1.all_tasks`` 的更改刷新到数据库，然后使所有对象过期，因此当我们访问 ``u1.current_week_tasks`` 时，发生了 :term:`lazy load`，从数据库中重新获取此属性的内容。

    要拦截操作而不实际提交事务，需要先显式使属性 :term:`expired` 。一种简单的方法是直接调用它。在下面的示例中，:meth:`_orm.Session.flush` 将待处理的更改发送到数据库，然后使用 :meth:`_orm.Session.expire` 使 ``u1.current_week_tasks`` 集合过期，以便在下一次访问时重新获取：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.flush()
        ...     sess.expire(u1, ["current_week_tasks"])
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7fd95a4c8c50>, <__main__.Task object at 0x7fd95a4c8c80>]

    我们实际上可以跳过调用 :meth:`_orm.Session.flush`，假设 :class:`_orm.Session` 保持 :paramref:`_orm.Session.autoflush` 为默认值 ``True``，因为过期的 ``current_week_tasks`` 属性将在过期后访问时触发自动刷新：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.expire(u1, ["current_week_tasks"])
        ...     print(u1.current_week_tasks)  # 触发查询前的自动刷新
        [<__main__.Task object at 0x7fd95a4c8c50>, <__main__.Task object at 0x7fd95a4c8c80>]

    继续上述方法更复杂一点，我们可以在相关的 ``User.all_tasks`` 集合更改时使用 :ref:`event hooks <event_toplevel>` 程序化地应用过期。这是一种 **高级技术**，首先应该考虑更简单的架构，如 ``@property`` 或坚持只读用例。在我们的简单示例中，这将配置为：

        from sqlalchemy import event, inspect


        @event.listens_for(User.all_tasks, "append")
        @event.listens_for(User.all_tasks, "remove")
        @event.listens_for(User.all_tasks, "bulk_replace")
        def _expire_User_current_week_tasks(target, value, initiator):
            inspect(target).session.expire(target, ["current_week_tasks"])

    通过上述钩子，变异操作会被拦截，并导致 ``User.current_week_tasks`` 集合自动过期：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f66d093ccb0>, <__main__.Task object at 0x7f66d093cce0>]

    上述 :class:`_orm.AttributeEvents` 事件钩子也会被 backref 变异触发，因此通过上述钩子对 ``Task.user`` 的更改也会被拦截：

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     t1 = Task(task_date=datetime.datetime.now())
        ...     t1.user = u1
        ...     sess.add(t1)
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f3b0c070d10>, <__main__.Task object at 0x7f3b0c057d10>]

.. tab:: 英文

    Continuing with the original viewonly attribute, if we do in fact make changes
    to the ``User.all_tasks`` collection on a :term:`persistent` object, the
    viewonly collection can only show the net result of this change after **two**
    things occur.  The first is that the change to ``User.all_tasks`` is
    :term:`flushed`, so that the new data is available in the database, at least
    within the scope of the local transaction.  The second is that the ``User.current_week_tasks``
    attribute is :term:`expired` and reloaded via a new SQL query to the database.

    To support this requirement, the simplest flow to use is one where the
    **viewonly relationship is consumed only in operations that are primarily read
    only to start with**.   Such as below, if we retrieve a ``User`` fresh from
    the database, the collection will be current::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f8711b906b0>]


    When we make modifications to ``u1.all_tasks``, if we want to see these changes
    reflected in the ``u1.current_week_tasks`` viewonly relationship, these changes need to be flushed
    and the ``u1.current_week_tasks`` attribute needs to be expired, so that
    it will :term:`lazy load` on next access.  The simplest approach to this is
    to use :meth:`_orm.Session.commit`, keeping the :paramref:`_orm.Session.expire_on_commit`
    parameter set at its default of ``True``::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.commit()
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f8711b90ec0>, <__main__.Task object at 0x7f8711b90a10>]

    Above, the call to :meth:`_orm.Session.commit` flushed the changes to ``u1.all_tasks``
    to the database, then expired all objects, so that when we accessed ``u1.current_week_tasks``,
    a :term:` lazy load` occurred which fetched the contents for this attribute
    freshly from the database.

    To intercept operations without actually committing the transaction,
    the attribute needs to be explicitly :term:`expired`
    first.   A simplistic way to do this is to just call it directly.  In
    the example below, :meth:`_orm.Session.flush` sends pending changes to the
    database, then :meth:`_orm.Session.expire` is used to expire the ``u1.current_week_tasks``
    collection so that it re-fetches on next access::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.flush()
        ...     sess.expire(u1, ["current_week_tasks"])
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7fd95a4c8c50>, <__main__.Task object at 0x7fd95a4c8c80>]

    We can in fact skip the call to :meth:`_orm.Session.flush`, assuming a
    :class:`_orm.Session` that keeps :paramref:`_orm.Session.autoflush` at its
    default value of ``True``, as the expired ``current_week_tasks`` attribute will
    trigger autoflush when accessed after expiration::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     sess.expire(u1, ["current_week_tasks"])
        ...     print(u1.current_week_tasks)  # triggers autoflush before querying
        [<__main__.Task object at 0x7fd95a4c8c50>, <__main__.Task object at 0x7fd95a4c8c80>]

    Continuing with the above approach to something more elaborate, we can apply
    the expiration programmatically when the related ``User.all_tasks`` collection
    changes, using :ref:`event hooks <event_toplevel>`.   This an **advanced
    technique**, where simpler architectures like ``@property`` or sticking to
    read-only use cases should be examined first.  In our simple example, this
    would be configured as::

        from sqlalchemy import event, inspect


        @event.listens_for(User.all_tasks, "append")
        @event.listens_for(User.all_tasks, "remove")
        @event.listens_for(User.all_tasks, "bulk_replace")
        def _expire_User_current_week_tasks(target, value, initiator):
            inspect(target).session.expire(target, ["current_week_tasks"])

    With the above hooks, mutation operations are intercepted and result in
    the ``User.current_week_tasks`` collection to be expired automatically::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     u1.all_tasks.append(Task(task_date=datetime.datetime.now()))
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f66d093ccb0>, <__main__.Task object at 0x7f66d093cce0>]

    The :class:`_orm.AttributeEvents` event hooks used above are also triggered
    by backref mutations, so with the above hooks a change to ``Task.user`` is
    also intercepted::

        >>> with Session(e) as sess:
        ...     u1 = sess.scalar(select(User).where(User.id == 1))
        ...     t1 = Task(task_date=datetime.datetime.now())
        ...     t1.user = u1
        ...     sess.add(t1)
        ...     print(u1.current_week_tasks)
        [<__main__.Task object at 0x7f3b0c070d10>, <__main__.Task object at 0x7f3b0c057d10>]

