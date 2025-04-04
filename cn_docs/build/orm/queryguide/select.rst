.. highlight:: pycon+sql
.. |prev| replace:: :doc:`index`
.. |next| replace:: :doc:`inheritance`

.. include:: queryguide_nav_include.rst

为 ORM 映射类编写 SELECT 语句
================================================

Writing SELECT statements for ORM Mapped Classes

.. tab:: 中文

    .. admonition:: 关于本文档

        本节使用了在 :ref:`unified_tutorial` 中首次介绍的 ORM 映射，展示在 :ref:`tutorial_declaring_mapped_classes` 部分。

        :doc:`查看本页的 ORM 设置 <_plain_setup>`。

    SELECT 语句由 :func:`_sql.select` 函数生成，该函数返回一个 :class:`_sql.Select` 对象。要返回的实体和/或 SQL 表达式（即“列”子句）以位置参数传递给函数。从那里，使用其他方法生成完整的语句，例如下面示例中的 :meth:`_sql.Select.where` 方法::

        >>> from sqlalchemy import select
        >>> stmt = select(User).where(User.name == "spongebob")

    给定一个完整的 :class:`_sql.Select` 对象，为了在 ORM 中执行它以返回行，该对象被传递给 :meth:`_orm.Session.execute`，然后返回一个 :class:`.Result` 对象::

        >>> result = session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        >>> for user_obj in result.scalars():
        ...     print(f"{user_obj.name} {user_obj.fullname}")
        spongebob Spongebob Squarepants

.. tab:: 英文

    .. admonition:: About this Document

        This section makes use of ORM mappings first illustrated in the
        :ref:`unified_tutorial`, shown in the section
        :ref:`tutorial_declaring_mapped_classes`.

        :doc:`View the ORM setup for this page <_plain_setup>`.


    SELECT statements are produced by the :func:`_sql.select` function which
    returns a :class:`_sql.Select` object.  The entities and/or SQL expressions
    to return (i.e. the "columns" clause) are passed positionally to the
    function.  From there, additional methods are used to generate the complete
    statement, such as the :meth:`_sql.Select.where` method illustrated below::

        >>> from sqlalchemy import select
        >>> stmt = select(User).where(User.name == "spongebob")

    Given a completed :class:`_sql.Select` object, in order to execute it within
    the ORM to get rows back, the object is passed to
    :meth:`_orm.Session.execute`, where a :class:`.Result` object is then
    returned::

        >>> result = session.execute(stmt)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('spongebob',){stop}
        >>> for user_obj in result.scalars():
        ...     print(f"{user_obj.name} {user_obj.fullname}")
        spongebob Spongebob Squarepants


.. _orm_queryguide_select_columns:

选择 ORM 实体和属性
-------------------------------------

Selecting ORM Entities and Attributes

.. tab:: 中文
    
    :func:`_sql.select` 构造接受 ORM 实体，包括映射类以及表示映射列的类级属性，这些实体在构造时转换为 :term:`ORM 注释的` :class:`_sql.FromClause` 和 :class:`_sql.ColumnElement` 元素。

    包含 ORM 注释实体的 :class:`_sql.Select` 对象通常使用 :class:`_orm.Session` 对象执行，而不是 :class:`_engine.Connection` 对象，以便 ORM 相关功能可以生效，包括可以返回 ORM 映射对象的实例。直接使用 :class:`_engine.Connection` 时，结果行将仅包含列级数据。

.. tab:: 英文

    The :func:`_sql.select` construct accepts ORM entities, including mapped classes as well as class-level attributes representing mapped columns, which are converted into :term:`ORM-annotated` :class:`_sql.FromClause` and :class:`_sql.ColumnElement` elements at construction time.

    A :class:`_sql.Select` object that contains ORM-annotated entities is normally executed using a :class:`_orm.Session` object, and not a :class:`_engine.Connection` object, so that ORM-related features may take effect, including that instances of ORM-mapped objects may be returned.  When using the :class:`_engine.Connection` directly, result rows will only contain column-level data.

.. _orm_queryguide_select_orm_entities:

选择 ORM 实体
^^^^^^^^^^^^^^^^^^^^^^

Selecting ORM Entities

.. tab:: 中文

    下面我们从 ``User`` 实体中进行选择，生成一个 :class:`_sql.Select`，从 ``User`` 映射到的 :class:`_schema.Table` 中进行选择::

        >>> result = session.execute(select(User).order_by(User.id))
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()

    从 ORM 实体中进行选择时，实体本身在结果中作为一行返回，其中包含单个元素，而不是一系列单独的列；例如，:class:`_engine.Result` 返回每行只有一个元素的 :class:`_engine.Row` 对象，该元素保存在 ``User`` 对象上::

        >>> result.all()
        [(User(id=1, name='spongebob', fullname='Spongebob Squarepants'),),
         (User(id=2, name='sandy', fullname='Sandy Cheeks'),),
         (User(id=3, name='patrick', fullname='Patrick Star'),),
         (User(id=4, name='squidward', fullname='Squidward Tentacles'),),
         (User(id=5, name='ehkrabs', fullname='Eugene H. Krabs'),)]

    选择包含 ORM 实体的单元素行列表时，通常会跳过 :class:`_engine.Row` 对象的生成而是直接接收 ORM 实体。最容易实现这一点的方法是使用 :meth:`_orm.Session.scalars` 方法执行，而不是 :meth:`_orm.Session.execute` 方法，这样就会返回一个 :class:`.ScalarResult` 对象，该对象产生单个元素而不是行::

        >>> session.scalars(select(User).order_by(User.id)).all()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()
        {stop}[User(id=1, name='spongebob', fullname='Spongebob Squarepants'),
         User(id=2, name='sandy', fullname='Sandy Cheeks'),
         User(id=3, name='patrick', fullname='Patrick Star'),
         User(id=4, name='squidward', fullname='Squidward Tentacles'),
         User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')]

    调用 :meth:`_orm.Session.scalars` 方法相当于调用 :meth:`_orm.Session.execute` 来接收 :class:`_engine.Result` 对象，然后调用 :meth:`_engine.Result.scalars` 来接收 :class:`_engine.ScalarResult` 对象。

.. tab:: 英文

    Below we select from the ``User`` entity, producing a :class:`_sql.Select` that selects from the mapped :class:`_schema.Table` to which ``User`` is mapped::

        >>> result = session.execute(select(User).order_by(User.id))
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()

    When selecting from ORM entities, the entity itself is returned in the result
    as a row with a single element, as opposed to a series of individual columns; for example above, the :class:`_engine.Result` returns :class:`_engine.Row` objects that have just a single element per row, that element holding onto a ``User`` object::

        >>> result.all()
        [(User(id=1, name='spongebob', fullname='Spongebob Squarepants'),),
         (User(id=2, name='sandy', fullname='Sandy Cheeks'),),
         (User(id=3, name='patrick', fullname='Patrick Star'),),
         (User(id=4, name='squidward', fullname='Squidward Tentacles'),),
         (User(id=5, name='ehkrabs', fullname='Eugene H. Krabs'),)]


    When selecting a list of single-element rows containing ORM entities, it is typical to skip the generation of :class:`_engine.Row` objects and instead receive ORM entities directly.   This is most easily achieved by using the :meth:`_orm.Session.scalars` method to execute, rather than the :meth:`_orm.Session.execute` method, so that a :class:`.ScalarResult` object which yields single elements rather than rows is returned::

        >>> session.scalars(select(User).order_by(User.id)).all()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account ORDER BY user_account.id
        [...] ()
        {stop}[User(id=1, name='spongebob', fullname='Spongebob Squarepants'),
         User(id=2, name='sandy', fullname='Sandy Cheeks'),
         User(id=3, name='patrick', fullname='Patrick Star'),
         User(id=4, name='squidward', fullname='Squidward Tentacles'),
         User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')]

    Calling the :meth:`_orm.Session.scalars` method is the equivalent to calling upon :meth:`_orm.Session.execute` to receive a :class:`_engine.Result` object, then calling upon :meth:`_engine.Result.scalars` to receive a :class:`_engine.ScalarResult` object.


.. _orm_queryguide_select_multiple_entities:

同时选择多个 ORM 实体
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selecting Multiple ORM Entities Simultaneously

.. tab:: 中文

    :func:`_sql.select` 函数可以一次接受多个 ORM 类和/或列表达式，包括可以请求多个 ORM 类。当从多个 ORM 类中进行 SELECT 查询时，结果行中的每个字段将根据其类名进行命名。在下面的示例中，对 ``User`` 和 ``Address`` 的 SELECT 查询的结果行将分别以 ``User`` 和 ``Address`` 命名::

        >>> stmt = select(User, Address).join(User.addresses).order_by(User.id, Address.id)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User.name} {row.Address.email_address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id
        [...] (){stop}
        spongebob spongebob@sqlalchemy.org
        sandy sandy@sqlalchemy.org
        sandy squirrel@squirrelpower.org
        patrick pat999@aol.com
        squidward stentcl@sqlalchemy.org

    如果我们希望在结果行中为这些实体分配不同的名称，可以使用 :func:`_orm.aliased` 构造，配合 :paramref:`_orm.aliased.name` 参数来为它们指定显式别名::

        >>> from sqlalchemy.orm import aliased
        >>> user_cls = aliased(User, name="user_cls")
        >>> email_cls = aliased(Address, name="email")
        >>> stmt = (
        ...     select(user_cls, email_cls)
        ...     .join(user_cls.addresses.of_type(email_cls))
        ...     .order_by(user_cls.id, email_cls.id)
        ... )
        >>> row = session.execute(stmt).first()
        {execsql}SELECT user_cls.id, user_cls.name, user_cls.fullname,
        email.id AS id_1, email.user_id, email.email_address
        FROM user_account AS user_cls JOIN address AS email
        ON user_cls.id = email.user_id ORDER BY user_cls.id, email.id
        [...] ()
        {stop}>>> print(f"{row.user_cls.name} {row.email.email_address}")
        spongebob spongebob@sqlalchemy.org

    上面的别名形式将在 :ref:`orm_queryguide_joining_relationships_aliased` 中进一步讨论。

    现有的 :class:`_sql.Select` 构造也可以通过 :meth:`_sql.Select.add_columns` 方法向其列子句添加 ORM 类和/或列表达式。我们也可以使用这种形式生成与上面相同的语句::

        >>> stmt = (
        ...     select(User).join(User.addresses).add_columns(Address).order_by(User.id, Address.id)
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id


.. tab:: 英文

    The :func:`_sql.select` function accepts any number of ORM classes and/or column expressions at once, including that multiple ORM classes may be requested.   When SELECTing from multiple ORM classes, they are named in each result row based on their class name.   In the example below, the result rows for a SELECT against ``User`` and ``Address`` will refer to them under the names ``User`` and ``Address``::

        >>> stmt = select(User, Address).join(User.addresses).order_by(User.id, Address.id)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User.name} {row.Address.email_address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id
        [...] (){stop}
        spongebob spongebob@sqlalchemy.org
        sandy sandy@sqlalchemy.org
        sandy squirrel@squirrelpower.org
        patrick pat999@aol.com
        squidward stentcl@sqlalchemy.org

    If we wanted to assign different names to these entities in the rows, we would use the :func:`_orm.aliased` construct using the :paramref:`_orm.aliased.name` parameter to alias them with an explicit name::

        >>> from sqlalchemy.orm import aliased
        >>> user_cls = aliased(User, name="user_cls")
        >>> email_cls = aliased(Address, name="email")
        >>> stmt = (
        ...     select(user_cls, email_cls)
        ...     .join(user_cls.addresses.of_type(email_cls))
        ...     .order_by(user_cls.id, email_cls.id)
        ... )
        >>> row = session.execute(stmt).first()
        {execsql}SELECT user_cls.id, user_cls.name, user_cls.fullname,
        email.id AS id_1, email.user_id, email.email_address
        FROM user_account AS user_cls JOIN address AS email
        ON user_cls.id = email.user_id ORDER BY user_cls.id, email.id
        [...] ()
        {stop}>>> print(f"{row.user_cls.name} {row.email.email_address}")
        spongebob spongebob@sqlalchemy.org

    The aliased form above is discussed further at :ref:`orm_queryguide_joining_relationships_aliased`.

    An existing :class:`_sql.Select` construct may also have ORM classes and/or column expressions added to its columns clause using the :meth:`_sql.Select.add_columns` method. We can produce the same statement as above using this form as well::

        >>> stmt = (
        ...     select(User).join(User.addresses).add_columns(Address).order_by(User.id, Address.id)
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname,
        address.id AS id_1, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id


选择单个属性
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selecting Individual Attributes

.. tab:: 中文
    
    映射类上的属性，例如 ``User.name`` 和 ``Address.email_address``，可以像 :class:`_schema.Column` 或其他 SQL 表达式对象一样，在传递给 :func:`_sql.select` 时使用。创建一个针对特定列的 :func:`_sql.select` 查询将返回 :class:`.Row` 对象，而 **不是** 像 ``User`` 或 ``Address`` 这样的实体对象。每个 :class:`.Row` 对象将分别包含每个列::

        >>> result = session.execute(
        ...     select(User.name, Address.email_address)
        ...     .join(User.addresses)
        ...     .order_by(User.id, Address.id)
        ... )
        {execsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id
        [...] (){stop}

    上述语句返回 :class:`.Row` 对象，其中包含 ``name`` 和 ``email_address`` 列，如下所示的运行时演示::

        >>> for row in result:
        ...     print(f"{row.name}  {row.email_address}")
        spongebob  spongebob@sqlalchemy.org
        sandy  sandy@sqlalchemy.org
        sandy  squirrel@squirrelpower.org
        patrick  pat999@aol.com
        squidward  stentcl@sqlalchemy.org


.. tab:: 英文

    The attributes on a mapped class, such as ``User.name`` and ``Address.email_address``, can be used just like :class:`_schema.Column` or other SQL expression objects when passed to :func:`_sql.select`. Creating a :func:`_sql.select` that is against specific columns will return :class:`.Row` objects, and **not** entities like ``User`` or ``Address`` objects. Each :class:`.Row` will have each column represented individually::

        >>> result = session.execute(
        ...     select(User.name, Address.email_address)
        ...     .join(User.addresses)
        ...     .order_by(User.id, Address.id)
        ... )
        {execsql}SELECT user_account.name, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        ORDER BY user_account.id, address.id
        [...] (){stop}

    The above statement returns :class:`.Row` objects with ``name`` and ``email_address`` columns, as illustrated in the runtime demonstration below::

        >>> for row in result:
        ...     print(f"{row.name}  {row.email_address}")
        spongebob  spongebob@sqlalchemy.org
        sandy  sandy@sqlalchemy.org
        sandy  squirrel@squirrelpower.org
        patrick  pat999@aol.com
        squidward  stentcl@sqlalchemy.org

.. _bundles:

使用捆绑包对选定属性进行分组
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Grouping Selected Attributes with Bundles

.. tab:: 中文

    :class:`_orm.Bundle` 构造是一个可扩展的仅限 ORM 的构造，允许将列表达式集成到结果行中::

        >>> from sqlalchemy.orm import Bundle
        >>> stmt = select(
        ...     Bundle("user", User.name, User.fullname),
        ...     Bundle("email", Address.email_address),
        ... ).join_from(User, Address)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.user.name} {row.user.fullname} {row.email.email_address}")
        {execsql}SELECT user_account.name, user_account.fullname, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] (){stop}
        spongebob Spongebob Squarepants spongebob@sqlalchemy.org
        sandy Sandy Cheeks sandy@sqlalchemy.org
        sandy Sandy Cheeks squirrel@squirrelpower.org
        patrick Patrick Star pat999@aol.com
        squidward Squidward Tentacles stentcl@sqlalchemy.org

    :class:`_orm.Bundle` 对于创建轻量级视图和自定义列分组可能非常有用。 :class:`_orm.Bundle` 也可以被子类化，以返回替代数据结构；有关示例，请参见 :meth:`_orm.Bundle.create_row_processor`。

    .. seealso::

        :class:`_orm.Bundle`

        :meth:`_orm.Bundle.create_row_processor`


.. tab:: 英文

    The :class:`_orm.Bundle` construct is an extensible ORM-only construct that allows sets of column expressions to be grouped in result rows::

        >>> from sqlalchemy.orm import Bundle
        >>> stmt = select(
        ...     Bundle("user", User.name, User.fullname),
        ...     Bundle("email", Address.email_address),
        ... ).join_from(User, Address)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.user.name} {row.user.fullname} {row.email.email_address}")
        {execsql}SELECT user_account.name, user_account.fullname, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        [...] (){stop}
        spongebob Spongebob Squarepants spongebob@sqlalchemy.org
        sandy Sandy Cheeks sandy@sqlalchemy.org
        sandy Sandy Cheeks squirrel@squirrelpower.org
        patrick Patrick Star pat999@aol.com
        squidward Squidward Tentacles stentcl@sqlalchemy.org

    The :class:`_orm.Bundle` is potentially useful for creating lightweight views and custom column groupings. :class:`_orm.Bundle` may also be subclassed in order to return alternate data structures; see :meth:`_orm.Bundle.create_row_processor` for an example.

    .. seealso::

        :class:`_orm.Bundle`

        :meth:`_orm.Bundle.create_row_processor`


.. _orm_queryguide_orm_aliases:

选择 ORM 别名
^^^^^^^^^^^^^^^^^^^^^

Selecting ORM Aliases

.. tab:: 中文

    如 :ref:`tutorial_using_aliases` 中的教程所述，要创建 ORM 实体的 SQL 别名，可以使用 :func:`_orm.aliased` 构造来对映射类进行操作::

        >>> from sqlalchemy.orm import aliased
        >>> u1 = aliased(User)
        >>> print(select(u1).order_by(u1.id))
        {printsql}SELECT user_account_1.id, user_account_1.name, user_account_1.fullname
        FROM user_account AS user_account_1 ORDER BY user_account_1.id

    与使用 :meth:`_schema.Table.alias` 时一样，SQL 别名是匿名命名的。如果希望从带有显式名称的行中选择实体，可以传递 :paramref:`_orm.aliased.name` 参数::

        >>> from sqlalchemy.orm import aliased
        >>> u1 = aliased(User, name="u1")
        >>> stmt = select(u1).order_by(u1.id)
        >>> row = session.execute(stmt).first()
        {execsql}SELECT u1.id, u1.name, u1.fullname
        FROM user_account AS u1 ORDER BY u1.id
        [...] (){stop}
        >>> print(f"{row.u1.name}")
        spongebob

    .. seealso::

        :class:`_orm.aliased` 构造在多个用例中是核心概念，包括：

        * 使用 ORM 进行子查询；更多信息请参见 :ref:`orm_queryguide_subqueries` 和 :ref:`orm_queryguide_join_subqueries`。
        * 控制结果集中的实体名称；参见 :ref:`orm_queryguide_select_multiple_entities` 中的示例。
        * 多次连接相同的 ORM 实体；参见 :ref:`orm_queryguide_joining_relationships_aliased` 中的示例。


.. tab:: 英文

    As discussed in the tutorial at :ref:`tutorial_using_aliases`, to create a SQL alias of an ORM entity is achieved using the :func:`_orm.aliased` construct against a mapped class::

        >>> from sqlalchemy.orm import aliased
        >>> u1 = aliased(User)
        >>> print(select(u1).order_by(u1.id))
        {printsql}SELECT user_account_1.id, user_account_1.name, user_account_1.fullname
        FROM user_account AS user_account_1 ORDER BY user_account_1.id

    As is the case when using :meth:`_schema.Table.alias`, the SQL alias is anonymously named.   For the case of selecting the entity from a row with an explicit name, the :paramref:`_orm.aliased.name` parameter may be passed as well::

        >>> from sqlalchemy.orm import aliased
        >>> u1 = aliased(User, name="u1")
        >>> stmt = select(u1).order_by(u1.id)
        >>> row = session.execute(stmt).first()
        {execsql}SELECT u1.id, u1.name, u1.fullname
        FROM user_account AS u1 ORDER BY u1.id
        [...] (){stop}
        >>> print(f"{row.u1.name}")
        spongebob

    .. seealso::


        The :class:`_orm.aliased` construct is central for several use cases,
        including:

        * making use of subqueries with the ORM; the sections :ref:`orm_queryguide_subqueries` and :ref:`orm_queryguide_join_subqueries` discuss this further.
        * Controlling the name of an entity in a result set; see :ref:`orm_queryguide_select_multiple_entities` for an example
        * Joining to the same ORM entity multiple times; see :ref:`orm_queryguide_joining_relationships_aliased` for an example.

.. _orm_queryguide_selecting_text:

从文本语句获取 ORM 结果
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Getting ORM Results from Textual Statements

.. tab:: 中文
    
    ORM 支持从来自其他来源的 SELECT 语句加载实体。典型的用例是文本 SELECT 语句，在 SQLAlchemy 中使用 :func:`_sql.text` 构造表示。可以使用 ORM 映射的列信息来扩展 :func:`_sql.text` 构造；然后可以将这些信息与 ORM 实体本身关联，以便根据此语句加载 ORM 对象。

    给定一个我们想要加载的文本 SQL 语句::

        >>> from sqlalchemy import text
        >>> textual_sql = text("SELECT id, name, fullname FROM user_account ORDER BY id")

    我们可以使用 :meth:`_sql.TextClause.columns` 方法向语句添加列信息；当调用此方法时， :class:`_sql.TextClause` 对象会转换为 :class:`_sql.TextualSelect` 对象，这个对象扮演了与 :class:`_sql.Select` 构造相似的角色。通常传递给 :meth:`_sql.TextClause.columns` 方法的是 :class:`_schema.Column` 对象或其等效对象，在这种情况下，我们可以直接使用 ``User`` 类上的 ORM 映射属性::

        >>> textual_sql = textual_sql.columns(User.id, User.name, User.fullname)

    现在，我们得到了一个 ORM 配置的 SQL 构造，它可以单独加载 "id"、"name" 和 "fullname" 列。为了将此 SELECT 语句用作完整的 ``User`` 实体的来源，我们可以使用 :meth:`_sql.Select.from_statement` 方法将这些列与常规的 ORM 启用的 :class:`_sql.Select` 构造链接::

        >>> orm_sql = select(User).from_statement(textual_sql)
        >>> for user_obj in session.execute(orm_sql).scalars():
        ...     print(user_obj)
        {execsql}SELECT id, name, fullname FROM user_account ORDER BY id
        [...] (){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    同样的 :class:`_sql.TextualSelect` 对象也可以使用 :meth:`_sql.TextualSelect.subquery` 方法转换为子查询，并使用 :func:`_orm.aliased` 构造将其链接到 ``User`` 实体，方法与下面的 :ref:`orm_queryguide_subqueries` 中讨论的相似::

        >>> orm_subquery = aliased(User, textual_sql.subquery())
        >>> stmt = select(orm_subquery)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT id, name, fullname FROM user_account ORDER BY id) AS anon_1
        [...] (){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    使用 :class:`_sql.TextualSelect` 直接与 :meth:`_sql.Select.from_statement` 结合使用与利用 :func:`_sql.aliased` 的区别在于，前者不会在生成的 SQL 中产生子查询。在某些情况下，这可以在性能或复杂性方面带来优势。

.. tab:: 英文

    The ORM supports loading of entities from SELECT statements that come from other sources. The typical use case is that of a textual SELECT statement, which in SQLAlchemy is represented using the :func:`_sql.text` construct. A :func:`_sql.text` construct can be augmented with information about the ORM-mapped columns that the statement would load; this can then be associated with the ORM entity itself so that ORM objects can be loaded based on this statement.

    Given a textual SQL statement we'd like to load from::

        >>> from sqlalchemy import text
        >>> textual_sql = text("SELECT id, name, fullname FROM user_account ORDER BY id")

    We can add column information to the statement by using the :meth:`_sql.TextClause.columns` method; when this method is invoked, the :class:`_sql.TextClause` object is converted into a :class:`_sql.TextualSelect` object, which takes on a role that is comparable to the :class:`_sql.Select` construct.  The :meth:`_sql.TextClause.columns` method is typically passed :class:`_schema.Column` objects or equivalent, and in this case we can make use of the ORM-mapped attributes on the ``User`` class directly::

        >>> textual_sql = textual_sql.columns(User.id, User.name, User.fullname)

    We now have an ORM-configured SQL construct that as given, can load the "id", "name" and "fullname" columns separately.   To use this SELECT statement as a source of complete ``User`` entities instead, we can link these columns to a regular ORM-enabled :class:`_sql.Select` construct using the :meth:`_sql.Select.from_statement` method::

        >>> orm_sql = select(User).from_statement(textual_sql)
        >>> for user_obj in session.execute(orm_sql).scalars():
        ...     print(user_obj)
        {execsql}SELECT id, name, fullname FROM user_account ORDER BY id
        [...] (){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    The same :class:`_sql.TextualSelect` object can also be converted into a subquery using the :meth:`_sql.TextualSelect.subquery` method, and linked to the ``User`` entity to it using the :func:`_orm.aliased` construct, in a similar manner as discussed below in :ref:`orm_queryguide_subqueries`::

        >>> orm_subquery = aliased(User, textual_sql.subquery())
        >>> stmt = select(orm_subquery)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT id, name, fullname FROM user_account ORDER BY id) AS anon_1
        [...] (){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    The difference between using the :class:`_sql.TextualSelect` directly with :meth:`_sql.Select.from_statement` versus making use of :func:`_sql.aliased` is that in the former case, no subquery is produced in the resulting SQL. This can in some scenarios be advantageous from a performance or complexity perspective.

.. _orm_queryguide_subqueries:

从子查询中选择实体
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selecting Entities from Subqueries

.. tab:: 中文
    

    前一节讨论的 :func:`_orm.aliased` 构造可以与任何 :class:`_sql.Subquery` 构造一起使用，该构造来自诸如 :meth:`_sql.Select.subquery` 这样的方法，将 ORM 实体链接到该子查询返回的列；必须在子查询返回的列与实体映射的列之间存在 **列对应关系**，也就是说，子查询需要最终来源于这些实体，如下面的示例所示::

        >>> inner_stmt = select(User).where(User.id < 7).order_by(User.id)
        >>> subq = inner_stmt.subquery()
        >>> aliased_user = aliased(User, subq)
        >>> stmt = select(aliased_user)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql} SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id < ? ORDER BY user_account.id) AS anon_1
        [generated in ...] (7,)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    .. seealso::

        :ref:`tutorial_subqueries_orm_aliased` - 在 :ref:`unified_tutorial` 中

        :ref:`orm_queryguide_join_subqueries`

.. tab:: 英文

    The :func:`_orm.aliased` construct discussed in the previous section can be used with any :class:`_sql.Subquery` construct that comes from a method such as :meth:`_sql.Select.subquery` to link ORM entities to the columns returned by that subquery; there must be a **column correspondence** relationship between the columns delivered by the subquery and the columns to which the entity is mapped, meaning, the subquery needs to be ultimately derived from those entities, such as in the example below::

        >>> inner_stmt = select(User).where(User.id < 7).order_by(User.id)
        >>> subq = inner_stmt.subquery()
        >>> aliased_user = aliased(User, subq)
        >>> stmt = select(aliased_user)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql} SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id < ? ORDER BY user_account.id) AS anon_1
        [generated in ...] (7,)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')
        User(id=3, name='patrick', fullname='Patrick Star')
        User(id=4, name='squidward', fullname='Squidward Tentacles')
        User(id=5, name='ehkrabs', fullname='Eugene H. Krabs')

    .. seealso::

        :ref:`tutorial_subqueries_orm_aliased` - in the :ref:`unified_tutorial`

        :ref:`orm_queryguide_join_subqueries`

.. _orm_queryguide_unions:

从 UNION 和其他集合操作中选择实体
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Selecting Entities from UNIONs and other set operations

.. tab:: 中文
    
    :func:`_sql.union` 和 :func:`_sql.union_all` 函数是最常用的集合操作，除了这两个，还有其他集合操作，如 :func:`_sql.except_`、:func:`_sql.intersect` 等，它们会返回一个被称为 :class:`_sql.CompoundSelect` 的对象，该对象由多个 :class:`_sql.Select` 构造组成，通过集合操作关键字连接。可以使用之前在 :ref:`orm_queryguide_selecting_text` 中演示的 :meth:`_sql.Select.from_statement` 方法，从简单的复合选择中选择 ORM 实体。在这个方法中，UNION 语句是完整的语句，将会被渲染，使用 :meth:`_sql.Select.from_statement` 后，无法再添加额外的条件::

        >>> from sqlalchemy import union_all
        >>> u = union_all(
        ...     select(User).where(User.id < 2), select(User).where(User.id == 3)
        ... ).order_by(User.id)
        >>> stmt = select(User).from_statement(u)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id < ? UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id = ? ORDER BY id
        [generated in ...] (2, 3)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=3, name='patrick', fullname='Patrick Star')

    :class:`_sql.CompoundSelect` 构造可以更灵活地用于查询中，可以通过将其组织为子查询，并使用 :func:`_orm.aliased` 将其与 ORM 实体链接，从而进一步修改查询，如在 :ref:`orm_queryguide_subqueries` 中所示。下面的示例中，我们首先使用 :meth:`_sql.CompoundSelect.subquery` 创建 UNION ALL 语句的子查询，然后将其打包到 :func:`_orm.aliased` 构造中，在该构造中，它可以像任何其他映射实体一样用于 :func:`_sql.select` 构造，包括可以根据导出的列添加过滤和排序条件::

        >>> subq = union_all(
        ...     select(User).where(User.id < 2), select(User).where(User.id == 3)
        ... ).subquery()
        >>> user_alias = aliased(User, subq)
        >>> stmt = select(user_alias).order_by(user_alias.id)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id < ? UNION ALL SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id = ?) AS anon_1 ORDER BY anon_1.id
        [generated in ...] (2, 3)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=3, name='patrick', fullname='Patrick Star')


.. tab:: 英文

    The :func:`_sql.union` and :func:`_sql.union_all` functions are the most common set operations, which along with other set operations such as :func:`_sql.except_`, :func:`_sql.intersect` and others deliver an object known as a :class:`_sql.CompoundSelect`, which is composed of multiple :class:`_sql.Select` constructs joined by a set-operation keyword.   ORM entities may be selected from simple compound selects using the :meth:`_sql.Select.from_statement` method illustrated previously at :ref:`orm_queryguide_selecting_text`.  In this method, the UNION statement is the complete statement that will be rendered, no additional criteria can be added after :meth:`_sql.Select.from_statement` is used::

        >>> from sqlalchemy import union_all
        >>> u = union_all(
        ...     select(User).where(User.id < 2), select(User).where(User.id == 3)
        ... ).order_by(User.id)
        >>> stmt = select(User).from_statement(u)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id < ? UNION ALL SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id = ? ORDER BY id
        [generated in ...] (2, 3)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=3, name='patrick', fullname='Patrick Star')

    A :class:`_sql.CompoundSelect` construct can be more flexibly used within a query that can be further modified by organizing it into a subquery and linking it to an ORM entity using :func:`_orm.aliased`, as illustrated previously at :ref:`orm_queryguide_subqueries`.  In the example below, we first use :meth:`_sql.CompoundSelect.subquery` to create a subquery of the UNION ALL statement, we then package that into the :func:`_orm.aliased` construct where it can be used like any other mapped entity in a :func:`_sql.select` construct, including that we can add filtering and order by criteria based on its exported columns::

        >>> subq = union_all(
        ...     select(User).where(User.id < 2), select(User).where(User.id == 3)
        ... ).subquery()
        >>> user_alias = aliased(User, subq)
        >>> stmt = select(user_alias).order_by(user_alias.id)
        >>> for user_obj in session.execute(stmt).scalars():
        ...     print(user_obj)
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname
        FROM (SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id < ? UNION ALL SELECT user_account.id AS id, user_account.name AS name, user_account.fullname AS fullname
        FROM user_account
        WHERE user_account.id = ?) AS anon_1 ORDER BY anon_1.id
        [generated in ...] (2, 3)
        {stop}User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=3, name='patrick', fullname='Patrick Star')


.. seealso::

    :ref:`tutorial_orm_union` - in the :ref:`unified_tutorial`

.. _orm_queryguide_joins:

连接
-----

Joins

.. tab:: 中文

    :meth:`_sql.Select.join` 和 :meth:`_sql.Select.join_from` 方法用于构造 SQL JOIN 语句，用于 SELECT 语句中。

    本节将详细介绍这些方法在 ORM 中的使用案例。有关从 Core 视角使用这些方法的一般概述，请参见 :ref:`tutorial_select_join`（在 :ref:`unified_tutorial` 中）。

    在 ORM 环境中使用 :meth:`_sql.Select.join` 方法来构建 :term:`2.0 风格`查询，除了遗留用例外，基本上等同于在 :term:`1.x 风格`查询中使用 :meth:`_orm.Query.join` 方法的用法。


.. tab:: 英文

    The :meth:`_sql.Select.join` and :meth:`_sql.Select.join_from` methods are used to construct SQL JOINs against a SELECT statement.

    This section will detail ORM use cases for these methods.  For a general overview of their use from a Core perspective, see :ref:`tutorial_select_join` in the :ref:`unified_tutorial`.

    The usage of :meth:`_sql.Select.join` in an ORM context for :term:`2.0 style` queries is mostly equivalent, minus legacy use cases, to the usage of the :meth:`_orm.Query.join` method in :term:`1.x style` queries.

.. _orm_queryguide_simple_relationship_join:

简单关系连接
^^^^^^^^^^^^^^^^^^^^^^^^^

Simple Relationship Joins

.. tab:: 中文
    
    考虑两个类 ``User`` 和 ``Address`` 之间的映射，其中关系 ``User.addresses`` 表示与每个 ``User`` 相关联的 ``Address`` 对象集合。 :meth:`_sql.Select.join` 最常见的用法是通过该关系创建一个 JOIN，使用 ``User.addresses`` 属性来指示如何进行连接::

        >>> stmt = select(User).join(User.addresses)

    上述对 :meth:`_sql.Select.join` 的调用将会生成 SQL，约等于::

        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    在上面的例子中，我们将 ``User.addresses`` 传递给 :meth:`_sql.Select.join`，它被称为 "on 子句"，即它指示如何构造 JOIN 的 "ON" 部分。

    .. tip::

        请注意，使用 :meth:`_sql.Select.join` 从一个实体连接到另一个实体会影响 SELECT 语句的 FROM 子句，但不会影响列子句；在这个例子中，SELECT 语句仍然只会返回来自 ``User`` 实体的行。若要同时选择 ``User`` 和 ``Address`` 的列 / 实体，必须在 :func:`_sql.select` 函数中同时指定 ``Address`` 实体，或者在之后使用 :meth:`_sql.Select.add_columns` 方法将其添加到 :class:`_sql.Select` 构造中。有关这两种形式的示例，请参见 :ref:`orm_queryguide_select_multiple_entities` 部分。

.. tab:: 英文

    Consider a mapping between two classes ``User`` and ``Address``, with a relationship ``User.addresses`` representing a collection of ``Address`` objects associated with each ``User``.   The most common usage of :meth:`_sql.Select.join` is to create a JOIN along this relationship, using the ``User.addresses`` attribute as an indicator for how this should occur::

        >>> stmt = select(User).join(User.addresses)

    Where above, the call to :meth:`_sql.Select.join` along ``User.addresses`` will result in SQL approximately equivalent to::

        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    In the above example we refer to ``User.addresses`` as passed to :meth:`_sql.Select.join` as the "on clause", that is, it indicates how the "ON" portion of the JOIN should be constructed.

    .. tip::

        Note that using :meth:`_sql.Select.join` to JOIN from one entity to another affects the FROM clause of the SELECT statement, but not the columns clause; the SELECT statement in this example will continue to return rows from only the ``User`` entity.  To SELECT columns / entities from both ``User`` and ``Address`` at the same time, the ``Address`` entity must also be named in the :func:`_sql.select` function, or added to the :class:`_sql.Select` construct afterwards using the :meth:`_sql.Select.add_columns` method.  See the section :ref:`orm_queryguide_select_multiple_entities` for examples of both of these forms.

链接多个连接
^^^^^^^^^^^^^^^^^^^^^^^

Chaining Multiple Joins

.. tab:: 中文
    
    要构建一系列的 JOIN，可以使用多个 :meth:`_sql.Select.join` 调用。绑定到关系的属性同时意味着 JOIN 的左侧和右侧。考虑额外的实体 ``Order`` 和 ``Item``, 其中 ``User.orders`` 关系引用了 ``Order`` 实体， ``Order.items`` 关系通过关联表 ``order_items`` 引用了 ``Item`` 实体。两个 :meth:`_sql.Select.join` 调用将首先从 ``User`` 到 ``Order`` 进行 JOIN，然后再从 ``Order`` 到 ``Item`` 进行 JOIN。然而，由于 ``Order.items`` 是一个 :ref:`多对多 <relationships_many_to_many>` 关系，它将导致两个单独的 JOIN 元素，因此在生成的 SQL 中总共有三个 JOIN 元素::

        >>> stmt = select(User).join(User.orders).join(Order.items)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN user_order ON user_account.id = user_order.user_id
        JOIN order_items AS order_items_1 ON user_order.id = order_items_1.order_id
        JOIN item ON item.id = order_items_1.item_id

    每次调用 :meth:`_sql.Select.join` 方法的顺序仅在于我们希望从哪个 "左" 侧进行 JOIN 之前，需要先确保该侧已经在 FROM 列表中，然后再指定新的目标。例如，如果我们指定 ``select(User).join(Order.items).join(User.orders)``, 则 :meth:`_sql.Select.join` 不会知道如何正确地进行 JOIN 并会抛出错误。在正确的实践中，应该以与我们希望在 SQL 中呈现 JOIN 子句的方式一致的方式调用 :meth:`_sql.Select.join` 方法，每次调用应代表一个明确的链接，从前一个元素到当前的 JOIN。

    我们在 FROM 子句中定位的所有元素仍然可以作为继续连接的潜在点。例如，我们可以继续向上面的 ``User`` 实体连接链中添加其他元素，例如添加 ``User.addresses`` 关系::

        >>> stmt = select(User).join(User.orders).join(Order.items).join(User.addresses)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN user_order ON user_account.id = user_order.user_id
        JOIN order_items AS order_items_1 ON user_order.id = order_items_1.order_id
        JOIN item ON item.id = order_items_1.item_id
        JOIN address ON user_account.id = address.user_id


.. tab:: 英文

    To construct a chain of joins, multiple :meth:`_sql.Select.join` calls may be used.  The relationship-bound attribute implies both the left and right side of the join at once.   Consider additional entities ``Order`` and ``Item``, where the ``User.orders`` relationship refers to the ``Order`` entity, and the ``Order.items`` relationship refers to the ``Item`` entity, via an association table ``order_items``.   Two :meth:`_sql.Select.join` calls will result in a JOIN first from ``User`` to ``Order``, and a second from ``Order`` to ``Item``.  However, since ``Order.items`` is a :ref:`many to many <relationships_many_to_many>` relationship, it results in two separate JOIN elements, for a total of three JOIN elements in the resulting SQL::

        >>> stmt = select(User).join(User.orders).join(Order.items)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN user_order ON user_account.id = user_order.user_id
        JOIN order_items AS order_items_1 ON user_order.id = order_items_1.order_id
        JOIN item ON item.id = order_items_1.item_id

    The order in which each call to the :meth:`_sql.Select.join` method is significant only to the degree that the "left" side of what we would like to join from needs to be present in the list of FROMs before we indicate a new target.   :meth:`_sql.Select.join` would not, for example, know how to join correctly if we were to specify ``select(User).join(Order.items).join(User.orders)``, and would raise an error.  In correct practice, the :meth:`_sql.Select.join` method is invoked in such a way that lines up with how we would want the JOIN clauses in SQL to be rendered, and each call should represent a clear link from what precedes it.

    All of the elements that we target in the FROM clause remain available as potential points to continue joining FROM.    We can continue to add other elements to join FROM the ``User`` entity above, for example adding on the ``User.addresses`` relationship to our chain of joins::

        >>> stmt = select(User).join(User.orders).join(Order.items).join(User.addresses)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN user_order ON user_account.id = user_order.user_id
        JOIN order_items AS order_items_1 ON user_order.id = order_items_1.order_id
        JOIN item ON item.id = order_items_1.item_id
        JOIN address ON user_account.id = address.user_id


连接到目标实体
^^^^^^^^^^^^^^^^^^^^^^^^

Joins to a Target Entity

.. tab:: 中文

    第二种形式的 :meth:`_sql.Select.join` 允许任何映射的实体或核心可选择构造作为目标。在这种用法中，:meth:`_sql.Select.join` 将尝试 **推断(infer)** JOIN 的 ON 子句，使用两个实体之间的自然外键关系::

        >>> stmt = select(User).join(Address)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    在上述调用形式中，调用 :meth:`_sql.Select.join` 时会自动推断 "on 子句"。如果两个映射的 :class:`_schema.Table` 构造之间没有设置 :class:`_schema.ForeignKeyConstraint`，或者它们之间有多个 :class:`_schema.ForeignKeyConstraint` 关系，导致适用的约束不明确，则此调用形式最终会引发错误。

    .. note::

        当使用 :meth:`_sql.Select.join` 或 :meth:`_sql.Select.join_from` 而不指明 ON 子句时，ORM 配置的 :func:`_orm.relationship` 构造 **不会被考虑**。只有在映射的 :class:`_schema.Table` 对象级别之间配置的 :class:`_schema.ForeignKeyConstraint` 关系会在尝试推断 JOIN 的 ON 子句时被查询。


.. tab:: 英文

    A second form of :meth:`_sql.Select.join` allows any mapped entity or core selectable construct as a target.   In this usage, :meth:`_sql.Select.join` will attempt to **infer** the ON clause for the JOIN, using the natural foreign key relationship between two entities::

        >>> stmt = select(User).join(Address)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    In the above calling form, :meth:`_sql.Select.join` is called upon to infer the "on clause" automatically.  This calling form will ultimately raise an error if either there are no :class:`_schema.ForeignKeyConstraint` setup between the two mapped :class:`_schema.Table` constructs, or if there are multiple :class:`_schema.ForeignKeyConstraint` linkages between them such that the appropriate constraint to use is ambiguous.

    .. note:: 
        
        When making use of :meth:`_sql.Select.join` or :meth:`_sql.Select.join_from` without indicating an ON clause, ORM configured :func:`_orm.relationship` constructs are **not taken into account**. Only the configured :class:`_schema.ForeignKeyConstraint` relationships between the entities at the level of the mapped :class:`_schema.Table` objects are consulted when an attempt is made to infer an ON clause for the JOIN.

.. _queryguide_join_onclause:

使用 ON 子句连接到目标
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Joins to a Target with an ON Clause

.. tab:: 中文

    第三种调用形式允许同时显式传递目标实体和 ON 子句。包含 SQL 表达式作为 ON 子句的示例如下::

        >>> stmt = select(User).join(Address, User.id == Address.user_id)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    基于表达式的 ON 子句也可以是绑定到 :func:`_orm.relationship` 的属性，和在 :ref:`orm_queryguide_simple_relationship_join` 中使用的方式相同::

        >>> stmt = select(User).join(Address, User.addresses)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    上述示例看似冗余，因为它以两种不同的方式指示了 ``Address`` 的目标；然而，当与别名实体连接时，这种形式的实用性变得显而易见；有关示例，请参见 :ref:`orm_queryguide_joining_relationships_aliased` 部分。


.. tab:: 英文

    The third calling form allows both the target entity as well as the ON clause to be passed explicitly.    A example that includes a SQL expression as the ON clause is as follows::

        >>> stmt = select(User).join(Address, User.id == Address.user_id)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    The expression-based ON clause may also be a :func:`_orm.relationship`-bound attribute, in the same way it's used in :ref:`orm_queryguide_simple_relationship_join`::

        >>> stmt = select(User).join(Address, User.addresses)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account JOIN address ON user_account.id = address.user_id

    The above example seems redundant in that it indicates the target of ``Address`` in two different ways; however, the utility of this form becomes apparent when joining to aliased entities; see the section :ref:`orm_queryguide_joining_relationships_aliased` for an example.

.. _orm_queryguide_join_relationship_onclause_and:

.. _orm_queryguide_join_on_augmented:

将关系与自定义 ON 条件相结合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combining Relationship with Custom ON Criteria

.. tab:: 中文

    :func:`_orm.relationship` 构造生成的 ON 子句可以通过附加额外的条件来增强。这对于快速限制通过关系路径进行特定连接的范围非常有用，也适用于配置加载策略，如 :func:`_orm.joinedload` 和 :func:`_orm.selectinload` 等场景。 :meth:`_orm.PropComparator.and_` 方法接受一系列 SQL 表达式，按位置将它们通过 AND 连接到 JOIN 的 ON 子句中。例如，如果我们希望从 ``User`` 连接到 ``Address``，但同时将 ON 条件限制为特定的电子邮件地址：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).join(
        ...     User.addresses.and_(Address.email_address == "squirrel@squirrelpower.org")
        ... )
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        JOIN address ON user_account.id = address.user_id AND address.email_address = ?
        [...] ('squirrel@squirrelpower.org',){stop}
        [('Sandy Cheeks',)]

    .. seealso::

        :meth:`_orm.PropComparator.and_` 方法也适用于加载策略，如 :func:`_orm.joinedload` 和 :func:`_orm.selectinload`。请参见 :ref:`loader_option_criteria` 部分。


.. tab:: 英文

    The ON clause generated by the :func:`_orm.relationship` construct may be augmented with additional criteria.  This is useful both for quick ways to limit the scope of a particular join over a relationship path, as well as for cases like configuring loader strategies such as :func:`_orm.joinedload` and :func:`_orm.selectinload`. The :meth:`_orm.PropComparator.and_` method accepts a series of SQL expressions positionally that will be joined to the ON clause of the JOIN via AND.  For example if we wanted to JOIN from ``User`` to ``Address`` but also limit the ON criteria to only certain email addresses：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).join(
        ...     User.addresses.and_(Address.email_address == "squirrel@squirrelpower.org")
        ... )
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        JOIN address ON user_account.id = address.user_id AND address.email_address = ?
        [...] ('squirrel@squirrelpower.org',){stop}
        [('Sandy Cheeks',)]

    .. seealso::

        The :meth:`_orm.PropComparator.and_` method also works with loader strategies such as :func:`_orm.joinedload` and :func:`_orm.selectinload`. See the section :ref:`loader_option_criteria`.

.. _tutorial_joining_relationships_aliased:

.. _orm_queryguide_joining_relationships_aliased:

使用关系在别名目标之间进行连接
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using Relationship to join between aliased targets

.. tab:: 中文
    
    在使用 :func:`_orm.relationship` 绑定的属性构建连接时，用于指示 ON 子句的两参数语法，如 :ref:`queryguide_join_onclause` 所示，可以扩展为与 :func:`_orm.aliased` 构造一起使用，以指示 SQL 别名作为连接的目标，同时仍然使用 :func:`_orm.relationship` 绑定的属性来指示 ON 子句，如下例所示，其中 ``User`` 实体被连接到两个不同的 :func:`_orm.aliased` 构造，与 ``Address`` 实体进行连接::

        >>> address_alias_1 = aliased(Address)
        >>> address_alias_2 = aliased(Address)
        >>> stmt = (
        ...     select(User)
        ...     .join(address_alias_1, User.addresses)
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join(address_alias_2, User.addresses)
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2

    相同的模式可以更简洁地通过修饰符 :meth:`_orm.PropComparator.of_type` 来表达，该修饰符可以应用于 :func:`_orm.relationship` 绑定的属性，传递目标实体，以便一步完成目标指示。下面的示例使用 :meth:`_orm.PropComparator.of_type` 来生成与上面相同的 SQL 语句::

        >>> print(
        ...     select(User)
        ...     .join(User.addresses.of_type(address_alias_1))
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join(User.addresses.of_type(address_alias_2))
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2

    要使用 :func:`_orm.relationship` 从别名实体构建一个连接，可以直接从 :func:`_orm.aliased` 构造中获取该属性::

        >>> user_alias_1 = aliased(User)
        >>> print(select(user_alias_1.name).join(user_alias_1.addresses))
        {printsql}SELECT user_account_1.name
        FROM user_account AS user_account_1
        JOIN address ON user_account_1.id = address.user_id

.. tab:: 英文

    When constructing joins using :func:`_orm.relationship`-bound attributes to indicate the ON clause, the two-argument syntax illustrated in :ref:`queryguide_join_onclause` can be expanded to work with the :func:`_orm.aliased` construct, to indicate a SQL alias as the target of a join while still making use of the :func:`_orm.relationship`-bound attribute to  indicate the ON clause, as in the example below, where the ``User`` entity is joined twice to two different :func:`_orm.aliased` constructs against the ``Address`` entity::

        >>> address_alias_1 = aliased(Address)
        >>> address_alias_2 = aliased(Address)
        >>> stmt = (
        ...     select(User)
        ...     .join(address_alias_1, User.addresses)
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join(address_alias_2, User.addresses)
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2

    The same pattern may be expressed more succinctly using the modifier :meth:`_orm.PropComparator.of_type`, which may be applied to the :func:`_orm.relationship`-bound attribute, passing along the target entity in order to indicate the target in one step.   The example below uses :meth:`_orm.PropComparator.of_type` to produce the same SQL statement as the one just illustrated::

        >>> print(
        ...     select(User)
        ...     .join(User.addresses.of_type(address_alias_1))
        ...     .where(address_alias_1.email_address == "patrick@aol.com")
        ...     .join(User.addresses.of_type(address_alias_2))
        ...     .where(address_alias_2.email_address == "patrick@gmail.com")
        ... )
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN address AS address_1 ON user_account.id = address_1.user_id
        JOIN address AS address_2 ON user_account.id = address_2.user_id
        WHERE address_1.email_address = :email_address_1
        AND address_2.email_address = :email_address_2


    To make use of a :func:`_orm.relationship` to construct a join **from** an aliased entity, the attribute is available from the :func:`_orm.aliased` construct directly::

        >>> user_alias_1 = aliased(User)
        >>> print(select(user_alias_1.name).join(user_alias_1.addresses))
        {printsql}SELECT user_account_1.name
        FROM user_account AS user_account_1
        JOIN address ON user_account_1.id = address.user_id



.. _orm_queryguide_join_subqueries:

连接到子查询
^^^^^^^^^^^^^^^^^^^^^

Joining to Subqueries

.. tab:: 中文

    连接的目标可以是任何“可选择(selectable)”的实体，包括子查询。在使用 ORM 时，通常这些目标会通过 :func:`_orm.aliased` 构造来声明，但这并不是严格要求，特别是在连接的实体不会在结果中返回的情况下。例如，要从 ``User`` 实体连接到 ``Address`` 实体，其中 ``Address`` 实体作为一个行限制子查询表示，我们首先使用 :meth:`_sql.Select.subquery` 构造一个 :class:`_sql.Subquery` 对象，然后将其作为 :meth:`_sql.Select.join` 方法的目标::

        >>> subq = select(Address).where(Address.email_address == "pat999@aol.com").subquery()
        >>> stmt = select(User).join(subq, User.id == subq.c.user_id)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = :email_address_1) AS anon_1
        ON user_account.id = anon_1.user_id{stop}

    当通过 :meth:`_orm.Session.execute` 调用上述 SELECT 语句时，将返回包含 ``User`` 实体的行，但不包含 ``Address`` 实体。为了将 ``Address`` 实体包括到结果集中，我们可以对 ``Address`` 实体和 :class:`.Subquery` 对象构造一个 :func:`_orm.aliased` 对象。我们还可以为 :func:`_orm.aliased` 构造指定一个名称，例如下面使用的 ``"address"``，以便我们可以在结果行中按名称引用它::

        >>> address_subq = aliased(Address, subq, name="address")
        >>> stmt = select(User, address_subq).join(address_subq)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User} {row.address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.user_id, anon_1.email_address
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = ?) AS anon_1 ON user_account.id = anon_1.user_id
        [...] ('pat999@aol.com',){stop}
        User(id=3, name='patrick', fullname='Patrick Star') Address(id=4, email_address='pat999@aol.com')


.. tab:: 英文

    The target of a join may be any "selectable" entity which includes subqueries.   When using the ORM, it is typical that these targets are stated in terms of an :func:`_orm.aliased` construct, but this is not strictly required, particularly if the joined entity is not being returned in the results.  For example, to join from the ``User`` entity to the ``Address`` entity, where the ``Address`` entity is represented as a row limited subquery, we first construct a :class:`_sql.Subquery` object using :meth:`_sql.Select.subquery`, which may then be used as the target of the :meth:`_sql.Select.join` method::

        >>> subq = select(Address).where(Address.email_address == "pat999@aol.com").subquery()
        >>> stmt = select(User).join(subq, User.id == subq.c.user_id)
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = :email_address_1) AS anon_1
        ON user_account.id = anon_1.user_id{stop}

    The above SELECT statement when invoked via :meth:`_orm.Session.execute` will return rows that contain ``User`` entities, but not ``Address`` entities. In order to include ``Address`` entities to the set of entities that would be returned in result sets, we construct an :func:`_orm.aliased` object against the ``Address`` entity and :class:`.Subquery` object. We also may wish to apply a name to the :func:`_orm.aliased` construct, such as ``"address"`` used below, so that we can refer to it by name in the result row::

        >>> address_subq = aliased(Address, subq, name="address")
        >>> stmt = select(User, address_subq).join(address_subq)
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User} {row.address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.user_id, anon_1.email_address
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = ?) AS anon_1 ON user_account.id = anon_1.user_id
        [...] ('pat999@aol.com',){stop}
        User(id=3, name='patrick', fullname='Patrick Star') Address(id=4, email_address='pat999@aol.com')

沿关系路径连接到子查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Joining to Subqueries along Relationship paths

.. tab:: 中文

    上一节中展示的子查询形式可以通过使用 :func:`_orm.relationship` 绑定的属性以更具体的方式表示，使用在 :ref:`orm_queryguide_joining_relationships_aliased` 中指示的某些形式。例如，为了创建相同的连接，同时确保该连接沿着特定的 :func:`_orm.relationship` 进行，我们可以使用 :meth:`_orm.PropComparator.of_type` 方法，传递包含目标连接的 :class:`.Subquery` 对象的 :func:`_orm.aliased` 构造::

        >>> address_subq = aliased(Address, subq, name="address")
        >>> stmt = select(User, address_subq).join(User.addresses.of_type(address_subq))
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User} {row.address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.user_id, anon_1.email_address
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = ?) AS anon_1 ON user_account.id = anon_1.user_id
        [...] ('pat999@aol.com',){stop}
        User(id=3, name='patrick', fullname='Patrick Star') Address(id=4, email_address='pat999@aol.com')


.. tab:: 英文

    The subquery form illustrated in the previous section may be expressed with more specificity using a :func:`_orm.relationship`-bound attribute using one of the forms indicated at :ref:`orm_queryguide_joining_relationships_aliased`. For example, to create the same join while ensuring the join is along that of a particular :func:`_orm.relationship`, we may use the :meth:`_orm.PropComparator.of_type` method, passing the :func:`_orm.aliased` construct containing the :class:`.Subquery` object that's the target of the join::

        >>> address_subq = aliased(Address, subq, name="address")
        >>> stmt = select(User, address_subq).join(User.addresses.of_type(address_subq))
        >>> for row in session.execute(stmt):
        ...     print(f"{row.User} {row.address}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        anon_1.id AS id_1, anon_1.user_id, anon_1.email_address
        FROM user_account
        JOIN (SELECT address.id AS id,
        address.user_id AS user_id, address.email_address AS email_address
        FROM address
        WHERE address.email_address = ?) AS anon_1 ON user_account.id = anon_1.user_id
        [...] ('pat999@aol.com',){stop}
        User(id=3, name='patrick', fullname='Patrick Star') Address(id=4, email_address='pat999@aol.com')

引用多个实体的子查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Subqueries that Refer to Multiple Entities

.. tab:: 中文

    包含跨多个 ORM 实体的列的子查询可以一次应用于多个 :func:`_orm.aliased` 构造，并在同一个 :class:`.Select` 构造中分别按每个实体使用。渲染的 SQL 将继续将所有这些 :func:`_orm.aliased` 构造视为相同的子查询，但从 ORM / Python 的角度来看，可以使用适当的 :func:`_orm.aliased` 构造引用不同的返回值和对象属性。

    例如，给定一个同时引用 ``User`` 和 ``Address`` 的子查询::

        >>> user_address_subq = (
        ...     select(User.id, User.name, User.fullname, Address.id, Address.email_address)
        ...     .join_from(User, Address)
        ...     .where(Address.email_address.in_(["pat999@aol.com", "squirrel@squirrelpower.org"]))
        ...     .subquery()
        ... )

    我们可以创建分别引用相同对象的 ``User`` 和 ``Address`` 的 :func:`_orm.aliased` 构造::

        >>> user_alias = aliased(User, user_address_subq, name="user")
        >>> address_alias = aliased(Address, user_address_subq, name="address")

    一个从这两个实体选择的 :class:`.Select` 构造将只渲染一次子查询，但在结果行的上下文中可以同时返回 ``User`` 和 ``Address`` 类的对象::

        >>> stmt = select(user_alias, address_alias).where(user_alias.name == "sandy")
        >>> for row in session.execute(stmt):
        ...     print(f"{row.user} {row.address}")
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname, anon_1.id_1, anon_1.email_address
        FROM (SELECT user_account.id AS id, user_account.name AS name,
        user_account.fullname AS fullname, address.id AS id_1,
        address.email_address AS email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE address.email_address IN (?, ?)) AS anon_1
        WHERE anon_1.name = ?
        [...] ('pat999@aol.com', 'squirrel@squirrelpower.org', 'sandy'){stop}
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='squirrel@squirrelpower.org')


.. tab:: 英文

    A subquery that contains columns spanning more than one ORM entity may be applied to more than one :func:`_orm.aliased` construct at once, and used in the same :class:`.Select` construct in terms of each entity separately. The rendered SQL will continue to treat all such :func:`_orm.aliased` constructs as the same subquery, however from the ORM / Python perspective the different return values and object attributes can be referenced by using the appropriate :func:`_orm.aliased` construct.

    Given for example a subquery that refers to both ``User`` and ``Address``::

        >>> user_address_subq = (
        ...     select(User.id, User.name, User.fullname, Address.id, Address.email_address)
        ...     .join_from(User, Address)
        ...     .where(Address.email_address.in_(["pat999@aol.com", "squirrel@squirrelpower.org"]))
        ...     .subquery()
        ... )

    We can create :func:`_orm.aliased` constructs against both ``User`` and ``Address`` that each refer to the same object::

        >>> user_alias = aliased(User, user_address_subq, name="user")
        >>> address_alias = aliased(Address, user_address_subq, name="address")

    A :class:`.Select` construct selecting from both entities will render the subquery once, but in a result-row context can return objects of both ``User`` and ``Address`` classes at the same time::

        >>> stmt = select(user_alias, address_alias).where(user_alias.name == "sandy")
        >>> for row in session.execute(stmt):
        ...     print(f"{row.user} {row.address}")
        {execsql}SELECT anon_1.id, anon_1.name, anon_1.fullname, anon_1.id_1, anon_1.email_address
        FROM (SELECT user_account.id AS id, user_account.name AS name,
        user_account.fullname AS fullname, address.id AS id_1,
        address.email_address AS email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE address.email_address IN (?, ?)) AS anon_1
        WHERE anon_1.name = ?
        [...] ('pat999@aol.com', 'squirrel@squirrelpower.org', 'sandy'){stop}
        User(id=2, name='sandy', fullname='Sandy Cheeks') Address(id=3, email_address='squirrel@squirrelpower.org')


.. _orm_queryguide_select_from:

设置连接中最左边的 FROM 子句
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Setting the leftmost FROM clause in a join

.. tab:: 中文
    
    在当前的 :class:`_sql.Select` 状态的左侧与我们想要连接的目标不一致的情况下，可以使用 :meth:`_sql.Select.join_from` 方法::

        >>> stmt = select(Address).join_from(User, User.addresses).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    :meth:`_sql.Select.join_from` 方法接受两个或三个参数，格式可以是 ``(<join from>, <onclause>)`` 或 ``(<join from>, <join to>, [<onclause>])``::

        >>> stmt = select(Address).join_from(User, Address).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    要设置 SELECT 语句的初始 FROM 子句，以便后续可以使用 :meth:`_sql.Select.join`，也可以使用 :meth:`_sql.Select.select_from` 方法::

        >>> stmt = select(Address).select_from(User).join(Address).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    .. tip::

        :meth:`_sql.Select.select_from` 方法并不会实际决定 FROM 子句中表的顺序。如果语句还引用了一个 :class:`_sql.Join` 构造，它引用的表的顺序不同，那么 :class:`_sql.Join` 构造的顺序将优先。在我们使用 :meth:`_sql.Select.join` 和 :meth:`_sql.Select.join_from` 这样的方式时，这些方法最终会创建一个 :class:`_sql.Join` 对象。因此，在像下面这样的情况下，我们可以看到 :meth:`_sql.Select.select_from` 的内容会被覆盖::

            >>> stmt = select(Address).select_from(User).join(Address.user).where(User.name == "sandy")
            >>> print(stmt)
            {printsql}SELECT address.id, address.user_id, address.email_address
            FROM address JOIN user_account ON user_account.id = address.user_id
            WHERE user_account.name = :name_1

        上面我们看到 FROM 子句是 ``address JOIN user_account``，即使我们先声明了 ``select_from(User)``。因为 ``.join(Address.user)`` 方法的调用，最终的语句等效于以下内容::

            >>> from sqlalchemy.sql import join
            >>>
            >>> user_table = User.__table__
            >>> address_table = Address.__table__
            >>>
            >>> j = address_table.join(user_table, user_table.c.id == address_table.c.user_id)
            >>> stmt = (
            ...     select(address_table)
            ...     .select_from(user_table)
            ...     .select_from(j)
            ...     .where(user_table.c.name == "sandy")
            ... )
            >>> print(stmt)
            {printsql}SELECT address.id, address.user_id, address.email_address
            FROM address JOIN user_account ON user_account.id = address.user_id
            WHERE user_account.name = :name_1

        上面的 :class:`_sql.Join` 构造作为 :meth:`_sql.Select.select_from` 列表中的另一个条目被添加，覆盖了之前的条目。


.. tab:: 英文

    In cases where the left side of the current state of :class:`_sql.Select` is not in line with what we want to join from, the :meth:`_sql.Select.join_from` method may be used::

        >>> stmt = select(Address).join_from(User, User.addresses).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    The :meth:`_sql.Select.join_from` method accepts two or three arguments, either in the form ``(<join from>, <onclause>)``, or ``(<join from>, <join to>, [<onclause>])``::

        >>> stmt = select(Address).join_from(User, Address).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    To set up the initial FROM clause for a SELECT such that :meth:`_sql.Select.join` can be used subsequent, the :meth:`_sql.Select.select_from` method may also be used::


        >>> stmt = select(Address).select_from(User).join(Address).where(User.name == "sandy")
        >>> print(stmt)
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM user_account JOIN address ON user_account.id = address.user_id
        WHERE user_account.name = :name_1

    .. tip::

        The :meth:`_sql.Select.select_from` method does not actually have the final say on the order of tables in the FROM clause.    If the statement also refers to a :class:`_sql.Join` construct that refers to existing tables in a different order, the :class:`_sql.Join` construct takes precedence.    When we use methods like :meth:`_sql.Select.join` and :meth:`_sql.Select.join_from`, these methods are ultimately creating such a :class:`_sql.Join` object.   Therefore we can see the contents of :meth:`_sql.Select.select_from` being overridden in a case like this::

            >>> stmt = select(Address).select_from(User).join(Address.user).where(User.name == "sandy")
            >>> print(stmt)
            {printsql}SELECT address.id, address.user_id, address.email_address
            FROM address JOIN user_account ON user_account.id = address.user_id
            WHERE user_account.name = :name_1

        Where above, we see that the FROM clause is ``address JOIN user_account``, even though we stated ``select_from(User)`` first. Because of the ``.join(Address.user)`` method call, the statement is ultimately equivalent to the following::

            >>> from sqlalchemy.sql import join
            >>>
            >>> user_table = User.__table__
            >>> address_table = Address.__table__
            >>>
            >>> j = address_table.join(user_table, user_table.c.id == address_table.c.user_id)
            >>> stmt = (
            ...     select(address_table)
            ...     .select_from(user_table)
            ...     .select_from(j)
            ...     .where(user_table.c.name == "sandy")
            ... )
            >>> print(stmt)
            {printsql}SELECT address.id, address.user_id, address.email_address
            FROM address JOIN user_account ON user_account.id = address.user_id
            WHERE user_account.name = :name_1

        The :class:`_sql.Join` construct above is added as another entry in the :meth:`_sql.Select.select_from` list which supersedes the previous entry.


.. _orm_queryguide_relationship_operators:


关系 WHERE 运算符
----------------------------

Relationship WHERE Operators

.. tab:: 中文

    除了在 :meth:`.Select.join` 和 :meth:`.Select.join_from` 方法中使用 :func:`_orm.relationship` 构造之外，:func:`_orm.relationship` 还可以使用 :meth:`.Select.where` 方法帮助构建通常用于 WHERE 子句的 SQL 表达式。

.. tab:: 英文

    Besides the use of :func:`_orm.relationship` constructs within the :meth:`.Select.join` and :meth:`.Select.join_from` methods, :func:`_orm.relationship` also plays a role in helping to construct SQL expressions that are typically for use in the WHERE clause, using the :meth:`.Select.where` method.


.. _orm_queryguide_relationship_exists:

.. _tutorial_relationship_exists:

EXISTS 形式：has() / any()
^^^^^^^^^^^^^^^^^^^^^^^^^^^

EXISTS forms: has() / any()

.. tab:: 中文

    :class:`_sql.Exists` 构造最早在 :ref:`unified_tutorial` 的 :ref:`tutorial_exists` 部分中介绍。该对象用于与标量子查询一起呈现 SQL EXISTS 关键字。 :func:`_orm.relationship` 构造提供了一些辅助方法，可以用来生成一些常见的 EXISTS 类型查询，这些查询是基于关系的。

    对于像 ``User.addresses`` 这样的“一对多”关系，可以使用 :meth:`_orm.PropComparator.any` 方法生成一个与 ``address`` 表相关联的 EXISTS 查询，该查询通过子查询与 ``user_account`` 表关联。此方法接受一个可选的 WHERE 条件，用于限制子查询匹配的行：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).where(
        ...     User.addresses.any(Address.email_address == "squirrel@squirrelpower.org")
        ... )
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        WHERE EXISTS (SELECT 1
        FROM address
        WHERE user_account.id = address.user_id AND address.email_address = ?)
        [...] ('squirrel@squirrelpower.org',){stop}
        [('Sandy Cheeks',)]

    由于 EXISTS 通常在进行负查找时更高效，因此常见的查询是查找没有相关实体的实体。通过使用 ``~User.addresses.any()`` 这样的表达式，可以选择没有相关 ``Address`` 行的 ``User`` 实体：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).where(~User.addresses.any())
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        WHERE NOT (EXISTS (SELECT 1
        FROM address
        WHERE user_account.id = address.user_id))
        [...] (){stop}
        [('Eugene H. Krabs',)]

    :meth:`_orm.PropComparator.has` 方法与 :meth:`_orm.PropComparator.any` 方法大致相同，区别在于它用于多对一关系，例如，如果我们想查找所有属于 "sandy" 的 ``Address`` 对象，可以使用如下查询：

    .. sourcecode:: pycon+sql

        >>> stmt = select(Address.email_address).where(Address.user.has(User.name == "sandy"))
        >>> session.execute(stmt).all()
        {execsql}SELECT address.email_address
        FROM address
        WHERE EXISTS (SELECT 1
        FROM user_account
        WHERE user_account.id = address.user_id AND user_account.name = ?)
        [...] ('sandy',){stop}
        [('sandy@sqlalchemy.org',), ('squirrel@squirrelpower.org',)]


.. tab:: 英文

    The :class:`_sql.Exists` construct was first introduced in the :ref:`unified_tutorial` in the section :ref:`tutorial_exists`.  This object is used to render the SQL EXISTS keyword in conjunction with a scalar subquery.   The :func:`_orm.relationship` construct provides for some helper methods that may be used to generate some common EXISTS styles of queries in terms of the relationship.

    For a one-to-many relationship such as ``User.addresses``, an EXISTS against the ``address`` table that correlates back to the ``user_account`` table can be produced using :meth:`_orm.PropComparator.any`.  This method accepts an optional WHERE criteria to limit the rows matched by the subquery:

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).where(
        ...     User.addresses.any(Address.email_address == "squirrel@squirrelpower.org")
        ... )
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        WHERE EXISTS (SELECT 1
        FROM address
        WHERE user_account.id = address.user_id AND address.email_address = ?)
        [...] ('squirrel@squirrelpower.org',){stop}
        [('Sandy Cheeks',)]

    As EXISTS tends to be more efficient for negative lookups, a common query is to locate entities where there are no related entities present.  This is succinct using a phrase such as ``~User.addresses.any()``, to select for ``User`` entities that have no related ``Address`` rows:

    .. sourcecode:: pycon+sql

        >>> stmt = select(User.fullname).where(~User.addresses.any())
        >>> session.execute(stmt).all()
        {execsql}SELECT user_account.fullname
        FROM user_account
        WHERE NOT (EXISTS (SELECT 1
        FROM address
        WHERE user_account.id = address.user_id))
        [...] (){stop}
        [('Eugene H. Krabs',)]

    The :meth:`_orm.PropComparator.has` method works in mostly the same way as :meth:`_orm.PropComparator.any`, except that it's used for many-to-one relationships, such as if we wanted to locate all ``Address`` objects which belonged to "sandy":

    .. sourcecode:: pycon+sql

        >>> stmt = select(Address.email_address).where(Address.user.has(User.name == "sandy"))
        >>> session.execute(stmt).all()
        {execsql}SELECT address.email_address
        FROM address
        WHERE EXISTS (SELECT 1
        FROM user_account
        WHERE user_account.id = address.user_id AND user_account.name = ?)
        [...] ('sandy',){stop}
        [('sandy@sqlalchemy.org',), ('squirrel@squirrelpower.org',)]

.. _orm_queryguide_relationship_common_operators:

关系实例比较运算符
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Relationship Instance Comparison Operators

.. tab:: 中文

    .. comment

        >>> session.expunge_all()

    :func:`_orm.relationship` 绑定的属性还提供了一些用于构造 SQL 的实现方式，这些方式旨在基于相关对象的特定实例来过滤该 :func:`_orm.relationship` 绑定的属性，它可以从一个给定的 :term:`persistent`（或在不常见情况下为 :term:`detached`）对象实例中解包出合适的属性值，并据此构造出以目标 :func:`_orm.relationship` 为依据的 WHERE 条件。

    * **多对一关系的等值比较** - 可以将一个具体的对象实例与多对一关系进行比较，以选择那些目标实体的外键值等于给定对象主键值的行::

        >>> user_obj = session.get(User, 1)
        {execsql}SELECT ...{stop}
        >>> print(select(Address).where(Address.user == user_obj))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE :param_1 = address.user_id

    ..

    * **多对一关系的不等值比较** - 同样也可以使用不等运算符::

        >>> print(select(Address).where(Address.user != user_obj))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE address.user_id != :user_id_1 OR address.user_id IS NULL

    ..

    * **对象是否包含在一对多集合中** - 本质上是“一对多”版本的“等值”比较：选择那些主键等于相关对象中外键值的行::

        >>> address_obj = session.get(Address, 1)
        {execsql}SELECT ...{stop}
        >>> print(select(User).where(User.addresses.contains(address_obj)))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id = :param_1

    ..

    * **一个对象是否有特定的父对象（从一对多的角度）** - :func:`_orm.with_parent` 函数会生成一个用于返回那些被指定父对象引用的行的比较条件，这本质上等价于在多对一那侧使用 ``==`` 运算符::

        >>> from sqlalchemy.orm import with_parent
        >>> print(select(Address).where(with_parent(user_obj, User.addresses)))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE :param_1 = address.user_id


.. tab:: 英文

    .. comment

        >>> session.expunge_all()

    The :func:`_orm.relationship`-bound attribute also offers a few SQL construction implementations that are geared towards filtering a :func:`_orm.relationship`-bound attribute in terms of a specific instance of a related object, which can unpack the appropriate attribute values from a given :term:`persistent` (or less commonly a :term:`detached`) object instance and construct WHERE criteria in terms of the target :func:`_orm.relationship`.

    * **many to one equals comparison** - a specific object instance can be compared to many-to-one relationship, to select rows where the foreign key of the target entity matches the primary key value of the object given::

        >>> user_obj = session.get(User, 1)
        {execsql}SELECT ...{stop}
        >>> print(select(Address).where(Address.user == user_obj))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE :param_1 = address.user_id

    ..

    * **many to one not equals comparison** - the not equals operator may also be used::

        >>> print(select(Address).where(Address.user != user_obj))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE address.user_id != :user_id_1 OR address.user_id IS NULL

    ..

    * **object is contained in a one-to-many collection** - this is essentially the one-to-many version of the "equals" comparison, select rows where the primary key equals the value of the foreign key in a related object::

        >>> address_obj = session.get(Address, 1)
        {execsql}SELECT ...{stop}
        >>> print(select(User).where(User.addresses.contains(address_obj)))
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.id = :param_1

    ..

    * **An object has a particular parent from a one-to-many perspective** - the :func:`_orm.with_parent` function produces a comparison that returns rows which are referenced by a given parent, this is essentially the same as using the ``==`` operator with the many-to-one side::

        >>> from sqlalchemy.orm import with_parent
        >>> print(select(Address).where(with_parent(user_obj, User.addresses)))
        {printsql}SELECT address.id, address.user_id, address.email_address
        FROM address
        WHERE :param_1 = address.user_id


