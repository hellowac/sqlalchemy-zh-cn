.. currentmodule:: sqlalchemy.orm

.. _mapper_sql_expressions:

SQL 表达式作为映射属性
====================================

SQL Expressions as Mapped Attributes

.. tab:: 中文

    映射类上的属性可以链接到 SQL 表达式，可用于查询。

.. tab:: 英文

    Attributes on a mapped class can be linked to SQL expressions, which can be used in queries.

使用混合
--------------

Using a Hybrid

.. tab:: 中文

    将相对简单的 SQL 表达式链接到类的最简单和最灵活的方法是使用所谓的“混合属性”，在 :ref:`hybrids_toplevel` 部分进行了描述。混合属性提供了一种在 Python 层面和 SQL 表达式层面都可以工作的表达方式。例如，下面我们映射一个包含 ``firstname`` 和 ``lastname`` 属性的 ``User`` 类，并包含一个混合属性，为我们提供 ``fullname``，即两个字符串的连接::

        from sqlalchemy.ext.hybrid import hybrid_property


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @hybrid_property
            def fullname(self):
                return self.firstname + " " + self.lastname

    在上面， ``fullname`` 属性在实例和类级别都被解释，因此它可以从实例中获得::

        some_user = session.scalars(select(User).limit(1)).first()
        print(some_user.fullname)

    也可以在查询中使用::

        some_user = session.scalars(
            select(User).where(User.fullname == "John Smith").limit(1)
        ).first()

    字符串连接示例是一个简单的例子，其中 Python 表达式可以在实例和类级别上双重使用。通常，SQL 表达式必须与 Python 表达式区分开来，这可以使用 :meth:`.hybrid_property.expression` 实现。下面我们展示了在混合属性中需要使用条件的情况，在 Python 中使用 ``if`` 语句，在 SQL 表达式中使用 :func:`_expression.case` 构造::

        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.sql import case


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @hybrid_property
            def fullname(self):
                if self.firstname is not None:
                    return self.firstname + " " + self.lastname
                else:
                    return self.lastname

            @fullname.expression
            def fullname(cls):
                return case(
                    (cls.firstname != None, cls.firstname + " " + cls.lastname),
                    else_=cls.lastname,
                )

.. tab:: 英文

    The easiest and most flexible way to link relatively simple SQL expressions to a class is to use a so-called
    "hybrid attribute",
    described in the section :ref:`hybrids_toplevel`.  The hybrid provides
    for an expression that works at both the Python level as well as at the
    SQL expression level.  For example, below we map a class ``User``,
    containing attributes ``firstname`` and ``lastname``, and include a hybrid that
    will provide for us the ``fullname``, which is the string concatenation of the two::

        from sqlalchemy.ext.hybrid import hybrid_property


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @hybrid_property
            def fullname(self):
                return self.firstname + " " + self.lastname

    Above, the ``fullname`` attribute is interpreted at both the instance and
    class level, so that it is available from an instance::

        some_user = session.scalars(select(User).limit(1)).first()
        print(some_user.fullname)

    as well as usable within queries::

        some_user = session.scalars(
            select(User).where(User.fullname == "John Smith").limit(1)
        ).first()

    The string concatenation example is a simple one, where the Python expression
    can be dual purposed at the instance and class level.  Often, the SQL expression
    must be distinguished from the Python expression, which can be achieved using
    :meth:`.hybrid_property.expression`.  Below we illustrate the case where a conditional
    needs to be present inside the hybrid, using the ``if`` statement in Python and the
    :func:`_expression.case` construct for SQL expressions::

        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.sql import case


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @hybrid_property
            def fullname(self):
                if self.firstname is not None:
                    return self.firstname + " " + self.lastname
                else:
                    return self.lastname

            @fullname.expression
            def fullname(cls):
                return case(
                    (cls.firstname != None, cls.firstname + " " + cls.lastname),
                    else_=cls.lastname,
                )

.. _mapper_column_property_sql_expressions:

使用 column_property
---------------------

Using column_property

.. tab:: 中文

    :func:`_orm.column_property` 函数可以用来映射 SQL 表达式，类似于常规映射的 :class:`_schema.Column`。通过这种技术，属性会与加载时的所有其他列映射属性一起加载。在某些情况下，这比使用混合属性更有优势，因为该值可以在加载对象的父行时一并加载，特别是如果表达式链接到其他表（通常作为相关子查询）以访问通常在已加载对象上不可用的数据。

    使用 :func:`_orm.column_property` 进行 SQL 表达式的缺点包括表达式必须与为类整体发出的 SELECT 语句兼容，并且从声明性 mixin 使用 :func:`_orm.column_property` 时也可能会出现一些配置上的怪癖。

    我们的 “fullname” 示例可以使用 :func:`_orm.column_property` 表达，如下所示::

        from sqlalchemy.orm import column_property


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))
            fullname = column_property(firstname + " " + lastname)

    相关子查询也可以使用。下面我们使用 :func:`_expression.select` 构造创建一个 :class:`_sql.ScalarSelect`，它表示一个面向列的 SELECT 语句，将特定 ``User`` 可用的 ``Address`` 对象的计数链接在一起::

        from sqlalchemy.orm import column_property
        from sqlalchemy import select, func
        from sqlalchemy import Column, Integer, String, ForeignKey

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(Integer, ForeignKey("user.id"))


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            address_count = column_property(
                select(func.count(Address.id))
                .where(Address.user_id == id)
                .correlate_except(Address)
                .scalar_subquery()
            )

    在上述示例中，我们定义了一个 :func:`_expression.ScalarSelect` 构造，如下所示::

        stmt = (
            select(func.count(Address.id))
            .where(Address.user_id == id)
            .correlate_except(Address)
            .scalar_subquery()
        )

    在上面，我们首先使用 :func:`_sql.select` 创建一个 :class:`_sql.Select` 构造，然后我们使用 :meth:`_sql.Select.scalar_subquery` 方法将其转换为 :term:`scalar subquery`，表明我们打算在列表达式上下文中使用此 :class:`_sql.Select` 语句。

    在 :class:`_sql.Select` 本身中，我们选择 ``Address.id`` 行的计数，其中 ``Address.user_id`` 列等于 ``id``，在 ``User`` 类的上下文中，这是名为 ``id`` 的 :class:`_schema.Column` （请注意， ``id`` 也是一个 Python 内置函数的名称，这里我们不想使用它 - 如果我们在 ``User`` 类定义之外，我们会使用 ``User.id``）。

    :meth:`_sql.Select.correlate_except` 方法表明，此 :func:`_expression.select` 的 FROM 子句中的每个元素都可以从 FROM 列表中省略（即，与 ``User`` 的外部 SELECT 语句相关） ，除了对应于 ``Address`` 的 ▋

.. tab:: 英文

    The :func:`_orm.column_property` function can be used to map a SQL
    expression in a manner similar to a regularly mapped :class:`_schema.Column`.
    With this technique, the attribute is loaded
    along with all other column-mapped attributes at load time.  This is in some
    cases an advantage over the usage of hybrids, as the value can be loaded
    up front at the same time as the parent row of the object, particularly if
    the expression is one which links to other tables (typically as a correlated
    subquery) to access data that wouldn't normally be
    available on an already loaded object.

    Disadvantages to using :func:`_orm.column_property` for SQL expressions include that
    the expression must be compatible with the SELECT statement emitted for the class
    as a whole, and there are also some configurational quirks which can occur
    when using :func:`_orm.column_property` from declarative mixins.

    Our "fullname" example can be expressed using :func:`_orm.column_property` as
    follows::

        from sqlalchemy.orm import column_property


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))
            fullname = column_property(firstname + " " + lastname)

    Correlated subqueries may be used as well. Below we use the
    :func:`_expression.select` construct to create a :class:`_sql.ScalarSelect`,
    representing a column-oriented SELECT statement, that links together the count
    of ``Address`` objects available for a particular ``User``::

        from sqlalchemy.orm import column_property
        from sqlalchemy import select, func
        from sqlalchemy import Column, Integer, String, ForeignKey

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Address(Base):
            __tablename__ = "address"
            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(Integer, ForeignKey("user.id"))


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            address_count = column_property(
                select(func.count(Address.id))
                .where(Address.user_id == id)
                .correlate_except(Address)
                .scalar_subquery()
            )

    In the above example, we define a :func:`_expression.ScalarSelect` construct like the following::

        stmt = (
            select(func.count(Address.id))
            .where(Address.user_id == id)
            .correlate_except(Address)
            .scalar_subquery()
        )

    Above, we first use :func:`_sql.select` to create a :class:`_sql.Select`
    construct, which we then convert into a :term:`scalar subquery` using the
    :meth:`_sql.Select.scalar_subquery` method, indicating our intent to use this
    :class:`_sql.Select` statement in a column expression context.

    Within the :class:`_sql.Select` itself, we select the count of ``Address.id`` rows
    where the ``Address.user_id`` column is equated to ``id``, which in the context
    of the ``User`` class is the :class:`_schema.Column` named ``id`` (note that ``id`` is
    also the name of a Python built in function, which is not what we want to use
    here - if we were outside of the ``User`` class definition, we'd use ``User.id``).

    The :meth:`_sql.Select.correlate_except` method indicates that each element in the
    FROM clause of this :func:`_expression.select` may be omitted from the FROM list (that is, correlated
    to the enclosing SELECT statement against ``User``) except for the one corresponding
    to ``Address``.  This isn't strictly necessary, but prevents ``Address`` from
    being inadvertently omitted from the FROM list in the case of a long string
    of joins between ``User`` and ``Address`` tables where SELECT statements against
    ``Address`` are nested.

    For a :func:`.column_property` that refers to columns linked from a
    many-to-many relationship, use :func:`.and_` to join the fields of the
    association table to both tables in a relationship::

        from sqlalchemy import and_


        class Author(Base):
            # ...

            book_count = column_property(
                select(func.count(books.c.id))
                .where(
                    and_(
                        book_authors.c.author_id == authors.c.id,
                        book_authors.c.book_id == books.c.id,
                    )
                )
                .scalar_subquery()
            )

将 column_property() 添加到现有的声明式映射类
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding column_property() to an existing Declarative mapped class

.. tab:: 中文

    如果导入问题阻止 :func:`.column_property` 与类内联定义，则可以在配置后将其分配给类。使用声明基类（即由 :class:`_orm.DeclarativeBase` 超类或遗留函数如 :func:`_orm.declarative_base` 生成）的映射时，此属性分配会调用 :meth:`_orm.Mapper.add_property` 以在事实发生后添加额外的属性::

        # 仅当使用声明基类时有效
        User.address_count = column_property(
            select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
        )

    使用不使用声明基类的映射样式时，例如 :meth:`_orm.registry.mapped` 装饰器，可以在底层 :class:`_orm.Mapper` 对象上显式调用 :meth:`_orm.Mapper.add_property` 方法，该对象可以使用 :func:`_sa.inspect` 获得::

        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped
        class User:
            __tablename__ = "user"

            # ... additional mapping directives


        # 后续操作 ...

        # 适用于任何类型的映射
        from sqlalchemy import inspect

        inspect(User).add_property(
            column_property(
                select(func.count(Address.id))
                .where(Address.user_id == User.id)
                .scalar_subquery()
            )
        )

    .. seealso::

    :ref:`orm_declarative_table_adding_columns`

.. tab:: 英文

    If import issues prevent the :func:`.column_property` from being defined
    inline with the class, it can be assigned to the class after both
    are configured.   When using mappings that make use of a Declarative
    base class (i.e. produced by the :class:`_orm.DeclarativeBase` superclass
    or legacy functions such as :func:`_orm.declarative_base`),
    this attribute assignment has the effect of calling :meth:`_orm.Mapper.add_property`
    to add an additional property after the fact::

        # only works if a declarative base class is in use
        User.address_count = column_property(
            select(func.count(Address.id)).where(Address.user_id == User.id).scalar_subquery()
        )

    When using mapping styles that don't use Declarative base classes
    such as the :meth:`_orm.registry.mapped` decorator, the :meth:`_orm.Mapper.add_property`
    method may be invoked explicitly on the underlying :class:`_orm.Mapper` object,
    which can be obtained using :func:`_sa.inspect`::

        from sqlalchemy.orm import registry

        reg = registry()


        @reg.mapped
        class User:
            __tablename__ = "user"

            # ... additional mapping directives


        # later ...

        # works for any kind of mapping
        from sqlalchemy import inspect

        inspect(User).add_property(
            column_property(
                select(func.count(Address.id))
                .where(Address.user_id == User.id)
                .scalar_subquery()
            )
        )

    .. seealso::

    :ref:`orm_declarative_table_adding_columns`


.. _mapper_column_property_sql_expressions_composed:

在映射时从列属性组合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Composing from Column Properties at Mapping Time

.. tab:: 中文

    可以创建组合多个 :class:`.ColumnProperty` 对象的映射。当 :class:`.ColumnProperty` 在核心表达式上下文中使用时，它将被解释为 SQL 表达式，前提是它由现有的表达式对象作为目标；这是通过核心检测对象具有返回 SQL 表达式的 ``__clause_element__()`` 方法来实现的。然而，如果 :class:`.ColumnProperty` 在没有其他核心 SQL 表达式对象作为目标的表达式中用作主对象，则 :attr:`.ColumnProperty.expression` 属性将返回底层 SQL 表达式，以便可以一致地用于构建 SQL 表达式。下面， ``File`` 类包含一个属性 ``File.path``，它将字符串令牌连接到 ``File.filename`` 属性，该属性本身是一个 :class:`.ColumnProperty`::

        class File(Base):
            __tablename__ = "file"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(64))
            extension = mapped_column(String(8))
            filename = column_property(name + "." + extension)
            path = column_property("C:/" + filename.expression)

    当 ``File`` 类正常用于表达式时，分配给 ``filename`` 和 ``path`` 的属性可以直接使用。仅在映射定义中直接使用 :class:`.ColumnProperty` 时才需要使用 :attr:`.ColumnProperty.expression` 属性::

        stmt = select(File.path).where(File.filename == "foo.txt")

.. tab:: 英文

    It is possible to create mappings that combine multiple
    :class:`.ColumnProperty` objects together.  The :class:`.ColumnProperty` will
    be interpreted as a SQL expression when used in a Core expression context,
    provided that it is targeted by an existing expression object; this works by
    the Core detecting that the object has a ``__clause_element__()`` method which
    returns a SQL expression.   However, if the :class:`.ColumnProperty` is used as
    a lead object in an expression where there is no other Core SQL expression
    object to target it, the :attr:`.ColumnProperty.expression` attribute will
    return the underlying SQL expression so that it can be used to build SQL
    expressions consistently.  Below, the ``File`` class contains an attribute
    ``File.path`` that concatenates a string token to the ``File.filename``
    attribute, which is itself a :class:`.ColumnProperty`::


        class File(Base):
            __tablename__ = "file"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(64))
            extension = mapped_column(String(8))
            filename = column_property(name + "." + extension)
            path = column_property("C:/" + filename.expression)

    When the ``File`` class is used in expressions normally, the attributes
    assigned to ``filename`` and ``path`` are usable directly.  The use of the
    :attr:`.ColumnProperty.expression` attribute is only necessary when using
    the :class:`.ColumnProperty` directly within the mapping definition::

        stmt = select(File.path).where(File.filename == "foo.txt")

使用带有 ``column_property()`` 的列延迟
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Column Deferral with ``column_property()``

.. tab:: 中文

    在 :ref:`queryguide_toplevel` 的 :ref:`orm_queryguide_column_deferral` 中介绍的列延迟特性可以在映射时应用于由 :func:`_orm.column_property` 映射的 SQL 表达式，通过使用 :func:`_orm.deferred` 函数代替 :func:`_orm.column_property`::

        from sqlalchemy.orm import deferred


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            firstname: Mapped[str] = mapped_column()
            lastname: Mapped[str] = mapped_column()
            fullname: Mapped[str] = deferred(firstname + " " + lastname)

    .. seealso::

        :ref:`orm_queryguide_deferred_imperative`

.. tab:: 英文

    The column deferral feature introduced in the :ref:`queryguide_toplevel`
    at :ref:`orm_queryguide_column_deferral` may be applied at mapping time
    to a SQL expression mapped by :func:`_orm.column_property` by using the
    :func:`_orm.deferred` function in place of :func:`_orm.column_property`::

        from sqlalchemy.orm import deferred


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            firstname: Mapped[str] = mapped_column()
            lastname: Mapped[str] = mapped_column()
            fullname: Mapped[str] = deferred(firstname + " " + lastname)

    .. seealso::

        :ref:`orm_queryguide_deferred_imperative`



使用普通描述符
------------------------

Using a plain descriptor

.. tab:: 中文

    在必须发出比 :func:`_orm.column_property` 或 :class:`.hybrid_property` 提供的 SQL 查询更复杂的情况下，可以使用作为属性访问的常规 Python 函数，前提是表达式只需要在已经加载的实例上可用。假设表达式只需在已加载的实例上可用。该函数使用 Python 自身的 ``@property`` 装饰器进行装饰，将其标记为只读属性。在函数中，使用 :func:`.object_session` 定位对应于当前对象的 :class:`.Session`，然后使用该会话发出查询::

        from sqlalchemy.orm import object_session
        from sqlalchemy import select, func


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @property
            def address_count(self):
                return object_session(self).scalar(
                    select(func.count(Address.id)).where(Address.user_id == self.id)
                )

    普通描述符方法作为最后手段是有用的，但在通常情况下，其性能不如混合属性和列属性方法，因为它需要在每次访问时发出 SQL 查询。

.. tab:: 英文

    In cases where a SQL query more elaborate than what :func:`_orm.column_property`
    or :class:`.hybrid_property` can provide must be emitted, a regular Python
    function accessed as an attribute can be used, assuming the expression
    only needs to be available on an already-loaded instance.   The function
    is decorated with Python's own ``@property`` decorator to mark it as a read-only
    attribute.   Within the function, :func:`.object_session`
    is used to locate the :class:`.Session` corresponding to the current object,
    which is then used to emit a query::

        from sqlalchemy.orm import object_session
        from sqlalchemy import select, func


        class User(Base):
            __tablename__ = "user"
            id = mapped_column(Integer, primary_key=True)
            firstname = mapped_column(String(50))
            lastname = mapped_column(String(50))

            @property
            def address_count(self):
                return object_session(self).scalar(
                    select(func.count(Address.id)).where(Address.user_id == self.id)
                )

    The plain descriptor approach is useful as a last resort, but is less performant
    in the usual case than both the hybrid and column property approaches, in that
    it needs to emit a SQL query upon each access.

.. _mapper_querytime_expression:

查询时 SQL 表达式作为映射属性
-----------------------------------------------

Query-time SQL expressions as mapped attributes

.. tab:: 中文

    除了能够在映射类上配置固定的 SQL 表达式之外，SQLAlchemy ORM 还包括一个功能，即可以将对象加载为在查询时设置为其状态一部分的任意 SQL 表达式的结果。这种行为可以通过使用 :func:`_orm.query_expression` 配置 ORM 映射属性，然后在查询时使用 :func:`_orm.with_expression` 加载选项来实现。有关示例映射和用法，请参见 :ref:`orm_queryguide_with_expression` 部分。

.. tab:: 英文

    In addition to being able to configure fixed SQL expressions on mapped classes,
    the SQLAlchemy ORM also includes a feature wherein objects may be loaded
    with the results of arbitrary SQL expressions which are set up at query time as part
    of their state.  This behavior is available by configuring an ORM mapped
    attribute using :func:`_orm.query_expression` and then using the
    :func:`_orm.with_expression` loader option at query time.  See the section
    :ref:`orm_queryguide_with_expression` for an example mapping and usage.

