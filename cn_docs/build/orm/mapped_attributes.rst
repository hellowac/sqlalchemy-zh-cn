.. _mapping_attributes_toplevel:

.. currentmodule:: sqlalchemy.orm

更改Attribute的行为
===========================

Changing Attribute Behavior

.. tab:: 中文

    本节将讨论用于修改 ORM 映射属性行为的特性和技术，包括使用 :func:`_orm.mapped_column` 、:func:`_orm.relationship` 和其他映射的属性。

.. tab:: 英文

    This section will discuss features and techniques used to modify the behavior of ORM mapped attributes, including those mapped with :func:`_orm.mapped_column`, :func:`_orm.relationship`, and others.

.. _simple_validators:

简单验证器
-----------------

Simple Validators

.. tab:: 中文

    快速为属性添加“验证”例程的方法是使用 :func:`~sqlalchemy.orm.validates` 装饰器。属性验证器可以引发异常，停止更改属性值的过程，或者可以将给定的值更改为不同的值。验证器和所有属性扩展一样，只会被正常的用户代码调用；当 ORM 填充对象时不会被调用::

        from sqlalchemy.orm import validates


        class EmailAddress(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)

            @validates("email")
            def validate_email(self, key, address):
                if "@" not in address:
                    raise ValueError("failed simple email validation")
                return address

    验证器还会接收集合添加事件，当项目添加到集合中时::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address")

            @validates("addresses")
            def validate_address(self, key, address):
                if "@" not in address.email:
                    raise ValueError("failed simplified email validation")
                return address

    默认情况下，验证函数不会为集合删除事件发出，因为通常预期丢弃的值不需要验证。但是，:func:`.validates` 通过向装饰器指定 ``include_removes=True`` 来支持接收这些事件。当设置此标志时，验证函数必须接收一个附加的布尔参数，如果为 ``True`` 表示操作是删除::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address")

            @validates("addresses", include_removes=True)
            def validate_address(self, key, address, is_remove):
                if is_remove:
                    raise ValueError("not allowed to remove items from the collection")
                else:
                    if "@" not in address.email:
                        raise ValueError("failed simplified email validation")
                    return address

    通过 backref 链接的相互依赖的验证器的情况也可以通过使用 ``include_backrefs=False`` 选项进行调整；当此选项设置为 ``False`` 时，如果事件是由于 backref 发生的，则会阻止验证函数发出::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address", backref="user")

            @validates("addresses", include_backrefs=False)
            def validate_address(self, key, address):
                if "@" not in address:
                    raise ValueError("failed simplified email validation")
                return address

    上述代码中，如果我们将 ``Address.user`` 分配为 ``some_address.user = some_user``，即使 ``some_user.addresses`` 发生了添加，``validate_address()`` 函数也*不会*发出，因为事件是由 backref 引起的。

    请注意，:func:`~.validates` 装饰器是基于属性事件构建的便捷功能。需要更多控制属性更改行为配置的应用程序可以使用此系统，如 :class:`~.AttributeEvents` 中所述。

.. tab:: 英文

    A quick way to add a "validation" routine to an attribute is to use the
    :func:`~sqlalchemy.orm.validates` decorator. An attribute validator can raise
    an exception, halting the process of mutating the attribute's value, or can
    change the given value into something different. Validators, like all
    attribute extensions, are only called by normal userland code; they are not
    issued when the ORM is populating the object::

        from sqlalchemy.orm import validates


        class EmailAddress(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            email = mapped_column(String)

            @validates("email")
            def validate_email(self, key, address):
                if "@" not in address:
                    raise ValueError("failed simple email validation")
                return address

    Validators also receive collection append events, when items are added to a
    collection::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address")

            @validates("addresses")
            def validate_address(self, key, address):
                if "@" not in address.email:
                    raise ValueError("failed simplified email validation")
                return address

    The validation function by default does not get emitted for collection
    remove events, as the typical expectation is that a value being discarded
    doesn't require validation.  However, :func:`.validates` supports reception
    of these events by specifying ``include_removes=True`` to the decorator.  When
    this flag is set, the validation function must receive an additional boolean
    argument which if ``True`` indicates that the operation is a removal::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address")

            @validates("addresses", include_removes=True)
            def validate_address(self, key, address, is_remove):
                if is_remove:
                    raise ValueError("not allowed to remove items from the collection")
                else:
                    if "@" not in address.email:
                        raise ValueError("failed simplified email validation")
                    return address

    The case where mutually dependent validators are linked via a backref
    can also be tailored, using the ``include_backrefs=False`` option; this option,
    when set to ``False``, prevents a validation function from emitting if the
    event occurs as a result of a backref::

        from sqlalchemy.orm import validates


        class User(Base):
            # ...

            addresses = relationship("Address", backref="user")

            @validates("addresses", include_backrefs=False)
            def validate_address(self, key, address):
                if "@" not in address:
                    raise ValueError("failed simplified email validation")
                return address

    Above, if we were to assign to ``Address.user`` as in ``some_address.user = some_user``,
    the ``validate_address()`` function would *not* be emitted, even though an append
    occurs to ``some_user.addresses`` - the event is caused by a backref.

    Note that the :func:`~.validates` decorator is a convenience function built on
    top of attribute events.   An application that requires more control over
    configuration of attribute change behavior can make use of this system,
    described at :class:`~.AttributeEvents`.

.. autofunction:: validates

在核心级别使用自定义数据类型
----------------------------------------

Using Custom Datatypes at the Core Level

.. tab:: 中文
    
    一种非ORM的方式，通过自定义数据类型来影响列的值，以适应数据在Python中和在数据库中表示方式之间的转换，可以应用于映射的 :class:`_schema.Table` 元数据。在一些需要在数据存入数据库和返回时进行编码/解码的情况下，这种方式更为常见；在核心文档的 :ref:`types_typedecorator` 部分可以阅读更多相关内容。

.. tab:: 英文

    A non-ORM means of affecting the value of a column in a way that suits
    converting data between how it is represented in Python, vs. how it is
    represented in the database, can be achieved by using a custom datatype that is
    applied to the mapped :class:`_schema.Table` metadata.     This is more common in the
    case of some style of encoding / decoding that occurs both as data goes to the
    database and as it is returned; read more about this in the Core documentation
    at :ref:`types_typedecorator`.


.. _mapper_hybrids:

使用描述符和混合
-----------------------------

Using Descriptors and Hybrids

.. tab:: 中文

    一种更全面的方法来为属性生成修改后的行为是使用 :term:`descriptors`。这些通常在Python中使用 ``property()`` 函数。SQLAlchemy的标准描述符技术是创建一个普通描述符，并让它从一个具有不同名称的映射属性中读取/写入。下面我们用Python 2.6风格的属性来说明这一点::

        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            # 使用下划线命名属性，
            # 与列名不同
            _email = mapped_column("email", String)

            # 然后创建一个 ".email" 属性
            # 来获取/设置 "._email"
            @property
            def email(self):
                return self._email

            @email.setter
            def email(self, email):
                self._email = email

    上面的方法可以工作，但我们可以添加更多内容。虽然我们的 ``EmailAddress`` 对象将通过 ``email`` 描述符和 ``_email`` 映射属性传递值，但类级别的 ``EmailAddress.email`` 属性没有通常的表达语义，无法与 :class:`_sql.Select` 一起使用。为了提供这些，我们可以使用 :mod:`~sqlalchemy.ext.hybrid` 扩展，如下所示::

        from sqlalchemy.ext.hybrid import hybrid_property


        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            _email = mapped_column("email", String)

            @hybrid_property
            def email(self):
                return self._email

            @email.setter
            def email(self, email):
                self._email = email

    ``email`` 属性，除了在我们有 ``EmailAddress`` 实例时提供 getter/setter 行为外，当在类级别使用时也提供 SQL 表达式，也就是说，直接从 ``EmailAddress`` 类使用:

    .. sourcecode:: python+sql

        from sqlalchemy.orm import Session
        from sqlalchemy import select

        session = Session()

        address = session.scalars(
            select(EmailAddress).where(EmailAddress.email == "address@example.com")
        ).one()
        {execsql}SELECT address.email AS address_email, address.id AS address_id
        FROM address
        WHERE address.email = ?
        ('address@example.com',)
        {stop}

        address.email = "otheraddress@example.com"
        session.commit()
        {execsql}UPDATE address SET email=? WHERE address.id = ?
        ('otheraddress@example.com', 1)
        COMMIT
        {stop}

    :class:`~.hybrid_property` 还允许我们更改属性的行为，包括定义在实例级别访问属性和在类/表达式级别访问属性时的不同行为，使用 :meth:`.hybrid_property.expression` 修饰符。例如，如果我们想自动添加主机名，我们可以定义两组字符串操作逻辑::

        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            _email = mapped_column("email", String)

            @hybrid_property
            def email(self):
                """返回 _email 的值，直到最后十二个字符。"""
                return self._email[:-12]

            @email.setter
            def email(self, email):
                """设置 _email 的值，附加上十二个字符的值 @example.com。"""
                self._email = email + "@example.com"

            @email.expression
            def email(cls):
                """生成一个表示 _email 列值的 SQL 表达式，减去最后十二个字符。"""
                return func.substr(cls._email, 0, func.length(cls._email) - 12)

    在上面，访问 ``EmailAddress`` 实例的 ``email`` 属性将返回 ``_email`` 属性的值，从值中移除或添加主机名 ``@example.com``。当我们查询 ``email`` 属性时，会渲染一个 SQL 函数，产生相同的效果:

    .. sourcecode:: python+sql

        address = session.scalars(
            select(EmailAddress).where(EmailAddress.email == "address")
        ).one()
        {execsql}SELECT address.email AS address_email, address.id AS address_id
        FROM address
        WHERE substr(address.email, ?, length(address.email) - ?) = ?
        (0, 12, 'address')
        {stop}

    更多关于 Hybrids 的内容，请参阅 :ref:`hybrids_toplevel`。

.. tab:: 英文

    A more comprehensive way to produce modified behavior for an attribute is to
    use :term:`descriptors`.  These are commonly used in Python using the ``property()``
    function. The standard SQLAlchemy technique for descriptors is to create a
    plain descriptor, and to have it read/write from a mapped attribute with a
    different name. Below we illustrate this using Python 2.6-style properties::

        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            # name the attribute with an underscore,
            # different from the column name
            _email = mapped_column("email", String)

            # then create an ".email" attribute
            # to get/set "._email"
            @property
            def email(self):
                return self._email

            @email.setter
            def email(self, email):
                self._email = email

    The approach above will work, but there's more we can add. While our
    ``EmailAddress`` object will shuttle the value through the ``email``
    descriptor and into the ``_email`` mapped attribute, the class level
    ``EmailAddress.email`` attribute does not have the usual expression semantics
    usable with :class:`_sql.Select`. To provide these, we instead use the
    :mod:`~sqlalchemy.ext.hybrid` extension as follows::

        from sqlalchemy.ext.hybrid import hybrid_property


        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            _email = mapped_column("email", String)

            @hybrid_property
            def email(self):
                return self._email

            @email.setter
            def email(self, email):
                self._email = email

    The ``.email`` attribute, in addition to providing getter/setter behavior when we have an
    instance of ``EmailAddress``, also provides a SQL expression when used at the class level,
    that is, from the ``EmailAddress`` class directly:

    .. sourcecode:: python+sql

        from sqlalchemy.orm import Session
        from sqlalchemy import select

        session = Session()

        address = session.scalars(
            select(EmailAddress).where(EmailAddress.email == "address@example.com")
        ).one()
        {execsql}SELECT address.email AS address_email, address.id AS address_id
        FROM address
        WHERE address.email = ?
        ('address@example.com',)
        {stop}

        address.email = "otheraddress@example.com"
        session.commit()
        {execsql}UPDATE address SET email=? WHERE address.id = ?
        ('otheraddress@example.com', 1)
        COMMIT
        {stop}

    The :class:`~.hybrid_property` also allows us to change the behavior of the
    attribute, including defining separate behaviors when the attribute is
    accessed at the instance level versus at the class/expression level, using the
    :meth:`.hybrid_property.expression` modifier. Such as, if we wanted to add a
    host name automatically, we might define two sets of string manipulation
    logic::

        class EmailAddress(Base):
            __tablename__ = "email_address"

            id = mapped_column(Integer, primary_key=True)

            _email = mapped_column("email", String)

            @hybrid_property
            def email(self):
                """Return the value of _email up until the last twelve
                characters."""

                return self._email[:-12]

            @email.setter
            def email(self, email):
                """Set the value of _email, tacking on the twelve character
                value @example.com."""

                self._email = email + "@example.com"

            @email.expression
            def email(cls):
                """Produce a SQL expression that represents the value
                of the _email column, minus the last twelve characters."""

                return func.substr(cls._email, 0, func.length(cls._email) - 12)

    Above, accessing the ``email`` property of an instance of ``EmailAddress``
    will return the value of the ``_email`` attribute, removing or adding the
    hostname ``@example.com`` from the value. When we query against the ``email``
    attribute, a SQL function is rendered which produces the same effect:

    .. sourcecode:: python+sql

        address = session.scalars(
            select(EmailAddress).where(EmailAddress.email == "address")
        ).one()
        {execsql}SELECT address.email AS address_email, address.id AS address_id
        FROM address
        WHERE substr(address.email, ?, length(address.email) - ?) = ?
        (0, 12, 'address')
        {stop}

    Read more about Hybrids at :ref:`hybrids_toplevel`.

.. _synonyms:

同义词
--------

Synonyms

.. tab:: 中文

    同义词是一种映射器级别的结构，允许类上的任何属性“镜像”另一个被映射的属性。

    在最基本的意义上，同义词是一种通过额外的名称使某个属性可用的简便方法::

        from sqlalchemy.orm import synonym


        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            job_status = mapped_column(String(50))

            status = synonym("job_status")

    上述类 ``MyClass`` 有两个属性， ``.job_status`` 和 ``.status``，它们在表达式级别上会表现为一个属性:

    .. sourcecode:: pycon+sql

        >>> print(MyClass.job_status == "some_status")
        {printsql}my_table.job_status = :job_status_1{stop}

        >>> print(MyClass.status == "some_status")
        {printsql}my_table.job_status = :job_status_1{stop}

    并且在实例级别::

        >>> m1 = MyClass(status="x")
        >>> m1.status, m1.job_status
        ('x', 'x')

        >>> m1.job_status = "y"
        >>> m1.status, m1.job_status
        ('y', 'y')

    :func:`.synonym` 可以用于任何类型的映射属性，这些属性继承自 :class:`.MapperProperty`，包括映射列和关系，以及它们本身的同义词。

    除了简单的镜像，:func:`.synonym` 还可以引用用户定义的 :term:`descriptor`。我们可以给 ``status`` 同义词提供一个 ``@property``::

        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            status = mapped_column(String(50))

            @property
            def job_status(self):
                return "Status: " + self.status

            job_status = synonym("status", descriptor=job_status)

    当使用声明式时，上述模式可以更简洁地表示，使用 :func:`.synonym_for` 装饰器::

        from sqlalchemy.ext.declarative import synonym_for


        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            status = mapped_column(String(50))

            @synonym_for("status")
            @property
            def job_status(self):
                return "Status: " + self.status

    虽然 :func:`.synonym` 对于简单的镜像非常有用，但在现代用法中，通过描述符增强属性行为的用例更适合使用 :ref:`hybrid attribute <mapper_hybrids>` 功能，它更面向Python描述符。技术上来说，:func:`.synonym` 可以做任何 :class:`.hybrid_property` 能做的事情，因为它也支持自定义SQL功能的注入，但在复杂情况下，hybrid 更加直接易用。

.. tab:: 英文

    Synonyms are a mapper-level construct that allow any attribute on a class
    to "mirror" another attribute that is mapped.

    In the most basic sense, the synonym is an easy way to make a certain
    attribute available by an additional name::

        from sqlalchemy.orm import synonym


        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            job_status = mapped_column(String(50))

            status = synonym("job_status")

    The above class ``MyClass`` has two attributes, ``.job_status`` and
    ``.status`` that will behave as one attribute, both at the expression
    level:

    .. sourcecode:: pycon+sql

        >>> print(MyClass.job_status == "some_status")
        {printsql}my_table.job_status = :job_status_1{stop}

        >>> print(MyClass.status == "some_status")
        {printsql}my_table.job_status = :job_status_1{stop}

    and at the instance level::

        >>> m1 = MyClass(status="x")
        >>> m1.status, m1.job_status
        ('x', 'x')

        >>> m1.job_status = "y"
        >>> m1.status, m1.job_status
        ('y', 'y')

    The :func:`.synonym` can be used for any kind of mapped attribute that
    subclasses :class:`.MapperProperty`, including mapped columns and relationships,
    as well as synonyms themselves.

    Beyond a simple mirror, :func:`.synonym` can also be made to reference
    a user-defined :term:`descriptor`.  We can supply our
    ``status`` synonym with a ``@property``::

        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            status = mapped_column(String(50))

            @property
            def job_status(self):
                return "Status: " + self.status

            job_status = synonym("status", descriptor=job_status)

    When using Declarative, the above pattern can be expressed more succinctly
    using the :func:`.synonym_for` decorator::

        from sqlalchemy.ext.declarative import synonym_for


        class MyClass(Base):
            __tablename__ = "my_table"

            id = mapped_column(Integer, primary_key=True)
            status = mapped_column(String(50))

            @synonym_for("status")
            @property
            def job_status(self):
                return "Status: " + self.status

    While the :func:`.synonym` is useful for simple mirroring, the use case
    of augmenting attribute behavior with descriptors is better handled in modern
    usage using the :ref:`hybrid attribute <mapper_hybrids>` feature, which
    is more oriented towards Python descriptors.   Technically, a :func:`.synonym`
    can do everything that a :class:`.hybrid_property` can do, as it also supports
    injection of custom SQL capabilities, but the hybrid is more straightforward
    to use in more complex situations.

.. autofunction:: synonym

.. _custom_comparators:

运算符自定义
----------------------

Operator Customization

.. tab:: 中文

    SQLAlchemy ORM 和核心表达式语言使用的“操作符”是完全可定制的。例如，比较表达式 ``User.name == 'ed'`` 使用了一个内置于 Python 本身的操作符，称为 ``operator.eq`` - 可以修改 SQLAlchemy 与此类操作符关联的实际 SQL 构造。新的操作也可以与列表达式相关联。列表达式的操作符最直接在类型级别重新定义 - 请参阅 :ref:`types_operators` 部分了解描述。

    ORM 级别的函数如 :func:`.column_property`、:func:`_orm.relationship` 和 :func:`.composite` 也通过将 :class:`.PropComparator` 子类传递给每个函数的 ``comparator_factory`` 参数来提供在 ORM 级别重新定义操作符的功能。在此级别自定义操作符的用例较为罕见。有关概述，请参阅 :class:`.PropComparator` 的文档。

.. tab:: 英文

    The "operators" used by the SQLAlchemy ORM and Core expression language
    are fully customizable.  For example, the comparison expression
    ``User.name == 'ed'`` makes usage of an operator built into Python
    itself called ``operator.eq`` - the actual SQL construct which SQLAlchemy
    associates with such an operator can be modified.  New
    operations can be associated with column expressions as well.   The operators
    which take place for column expressions are most directly redefined at the
    type level -  see the
    section :ref:`types_operators` for a description.

    ORM level functions like :func:`.column_property`, :func:`_orm.relationship`,
    and :func:`.composite` also provide for operator redefinition at the ORM
    level, by passing a :class:`.PropComparator` subclass to the ``comparator_factory``
    argument of each function.  Customization of operators at this level is a
    rare use case.  See the documentation at :class:`.PropComparator`
    for an overview.

