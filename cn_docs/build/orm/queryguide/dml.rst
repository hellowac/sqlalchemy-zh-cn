.. highlight:: pycon+sql
.. |prev| replace:: :doc:`inheritance`
.. |next| replace:: :doc:`columns`

.. include:: queryguide_nav_include.rst

.. doctest-include _dml_setup.rst

.. _orm_expression_update_delete:

启用 ORM 的 INSERT、UPDATE 和 DELETE 语句
=================================================

ORM-Enabled INSERT, UPDATE, and DELETE statements

.. tab:: 中文

    .. admonition:: 关于本文档

        本节使用了在 :ref:`unified_tutorial` 中首次介绍的 ORM 映射，展示在 :ref:`tutorial_declaring_mapped_classes` 部分，以及在 :ref:`inheritance_toplevel` 部分展示的继承映射。

        :doc:`查看本页的 ORM 设置 <_dml_setup>`。

    :meth:`_orm.Session.execute` 方法除了处理启用 ORM 的 :class:`_sql.Select` 对象外，还可以以各种方式处理启用 ORM 的 :class:`_sql.Insert`、:class:`_sql.Update` 和 :class:`_sql.Delete` 对象，这些方式都用于一次性 INSERT、UPDATE 或 DELETE 多个数据库行。还支持方言特定的启用 ORM 的 "upserts"，即自动使用 UPDATE 的 INSERT 语句，用于已存在的行。

    下表总结了本文档中讨论的调用形式：

    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================
    ORM 用例                                                使用的 DML                                   数据通过  ... 传递                                                              支持     RETURNING?                                       支持多表映射?                  
    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================
    :ref:`orm_queryguide_bulk_insert`                       :func:`_dml.insert`                          List of dictionaries to :paramref:`_orm.Session.execute.params`              :ref:`yes <orm_queryguide_bulk_insert_returning>`         :ref:`yes <orm_queryguide_insert_joined_table_inheritance>`
    :ref:`orm_queryguide_bulk_insert_w_sql`                 :func:`_dml.insert`                          :paramref:`_orm.Session.execute.params` with :meth:`_dml.Insert.values`      :ref:`yes <orm_queryguide_bulk_insert_w_sql>`             :ref:`yes <orm_queryguide_insert_joined_table_inheritance>`
    :ref:`orm_queryguide_insert_values`                     :func:`_dml.insert`                          List of dictionaries to :meth:`_dml.Insert.values`                           :ref:`yes <orm_queryguide_insert_values>`                 no
    :ref:`orm_queryguide_upsert`                            :func:`_dml.insert`                          List of dictionaries to :meth:`_dml.Insert.values`                           :ref:`yes <orm_queryguide_upsert_returning>`              no
    :ref:`orm_queryguide_bulk_update`                       :func:`_dml.update`                          List of dictionaries to :paramref:`_orm.Session.execute.params`              no                                                        :ref:`yes <orm_queryguide_bulk_update_joined_inh>`
    :ref:`orm_queryguide_update_delete_where`               :func:`_dml.update`, :func:`_dml.delete`     keywords to :meth:`_dml.Update.values`                                       :ref:`yes <orm_queryguide_update_delete_where_returning>` :ref:`部分，采用手动步骤 <orm_queryguide_update_delete_joined_inh>`
    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================

.. tab:: 英文

    .. admonition:: About this Document

        This section makes use of ORM mappings first illustrated in the
        :ref:`unified_tutorial`, shown in the section
        :ref:`tutorial_declaring_mapped_classes`, as well as inheritance
        mappings shown in the section :ref:`inheritance_toplevel`.

        :doc:`View the ORM setup for this page <_dml_setup>`.

    The :meth:`_orm.Session.execute` method, in addition to handling ORM-enabled
    :class:`_sql.Select` objects, can also accommodate ORM-enabled
    :class:`_sql.Insert`, :class:`_sql.Update` and :class:`_sql.Delete` objects,
    in various ways which are each used to INSERT, UPDATE, or DELETE
    many database rows at once.  There is also dialect-specific support
    for ORM-enabled "upserts", which are INSERT statements that automatically
    make use of UPDATE for rows that already exist.

    The following table summarizes the calling forms that are discussed in this
    document:

    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================
    ORM Use Case                                            DML Construct Used                           Data is passed using ...                                                     Supports RETURNING?                                       Supports Multi-Table Mappings?
    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================
    :ref:`orm_queryguide_bulk_insert`                       :func:`_dml.insert`                          List of dictionaries to :paramref:`_orm.Session.execute.params`              :ref:`yes <orm_queryguide_bulk_insert_returning>`         :ref:`yes <orm_queryguide_insert_joined_table_inheritance>`
    :ref:`orm_queryguide_bulk_insert_w_sql`                 :func:`_dml.insert`                          :paramref:`_orm.Session.execute.params` with :meth:`_dml.Insert.values`      :ref:`yes <orm_queryguide_bulk_insert_w_sql>`             :ref:`yes <orm_queryguide_insert_joined_table_inheritance>`
    :ref:`orm_queryguide_insert_values`                     :func:`_dml.insert`                          List of dictionaries to :meth:`_dml.Insert.values`                           :ref:`yes <orm_queryguide_insert_values>`                 no
    :ref:`orm_queryguide_upsert`                            :func:`_dml.insert`                          List of dictionaries to :meth:`_dml.Insert.values`                           :ref:`yes <orm_queryguide_upsert_returning>`              no
    :ref:`orm_queryguide_bulk_update`                       :func:`_dml.update`                          List of dictionaries to :paramref:`_orm.Session.execute.params`              no                                                        :ref:`yes <orm_queryguide_bulk_update_joined_inh>`
    :ref:`orm_queryguide_update_delete_where`               :func:`_dml.update`, :func:`_dml.delete`     keywords to :meth:`_dml.Update.values`                                       :ref:`yes <orm_queryguide_update_delete_where_returning>` :ref:`partial, with manual steps <orm_queryguide_update_delete_joined_inh>`
    =====================================================   ==========================================   ========================================================================     ========================================================= ============================================================================



.. _orm_queryguide_bulk_insert:

ORM 批量 INSERT 语句
--------------------------

ORM Bulk INSERT Statements

.. tab:: 中文

    可以使用一个以 ORM 类为基础构造的 :func:`_dml.insert` 构造，并将其传递给 :meth:`_orm.Session.execute` 方法。如果将参数字典列表作为 :paramref:`_orm.Session.execute.params` 参数传入（该参数独立于 :class:`_dml.Insert` 对象本身），则该语句将启用 **批量插入模式**，即尽可能对多行插入进行优化::

        >>> from sqlalchemy import insert
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] [('spongebob', 'Spongebob Squarepants'), ('sandy', 'Sandy Cheeks'), ('patrick', 'Patrick Star'),
        ('squidward', 'Squidward Tentacles'), ('ehkrabs', 'Eugene H. Krabs')]
        {stop}<...>

    参数字典包含的键值对应于 ORM 映射的属性，它们应与映射的 :class:`._schema.Column` 或 :func:`_orm.mapped_column` 声明一致，也可以对应于 :ref:`composite <mapper_composite>` 声明。键应使用 **ORM 映射属性的名称**，而不是数据库中实际列的名称（如果两者不同的话）。

    .. versionchanged:: 2.0

        将一个 :class:`_dml.Insert` 构造传递给 :meth:`_orm.Session.execute` 方法时，现在会启用“批量插入”模式，该模式使用了与旧版 :meth:`_orm.Session.bulk_insert_mappings` 方法相同的机制。这一行为相比 1.x 版本有所变更：在旧版中，:class:`_dml.Insert` 会以 Core 方式解释，使用列名作为键；而现在则接受 ORM 属性名作为键。如需使用 Core 风格的功能，可在调用 :meth:`_orm.Session.execute` 时，通过 :paramref:`_orm.Session.execution_options` 参数传入执行选项 ``{"dml_strategy":"raw"}`` 。


.. tab:: 英文

    A :func:`_dml.insert` construct can be constructed in terms of an ORM class and passed to the :meth:`_orm.Session.execute` method.   A list of parameter dictionaries sent to the :paramref:`_orm.Session.execute.params` parameter, separate from the :class:`_dml.Insert` object itself, will invoke **bulk INSERT mode** for the statement, which essentially means the operation will optimize as much as possible for many rows::

        >>> from sqlalchemy import insert
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] [('spongebob', 'Spongebob Squarepants'), ('sandy', 'Sandy Cheeks'), ('patrick', 'Patrick Star'),
        ('squidward', 'Squidward Tentacles'), ('ehkrabs', 'Eugene H. Krabs')]
        {stop}<...>

    The parameter dictionaries contain key/value pairs which may correspond to ORM mapped attributes that line up with mapped :class:`._schema.Column` or :func:`_orm.mapped_column` declarations, as well as with :ref:`composite <mapper_composite>` declarations.   The keys should match the **ORM mapped attribute name** and **not** the actual database column name, if these two names happen to be different.

    .. versionchanged:: 2.0  
        
        Passing an :class:`_dml.Insert` construct to the :meth:`_orm.Session.execute` method now invokes a "bulk insert", which makes use of the same functionality as the legacy :meth:`_orm.Session.bulk_insert_mappings` method.  This is a behavior change compared to the 1.x series where the :class:`_dml.Insert` would be interpreted in a Core-centric way, using column names for value keys; ORM attribute keys are now accepted.   Core-style functionality is available by passing the execution option ``{"dml_strategy":"raw"}`` to the :paramref:`_orm.Session.execution_options` parameter of :meth:`_orm.Session.execute`.

.. _orm_queryguide_bulk_insert_returning:

使用 RETURNING 获取新对象
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting new objects with RETURNING

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    批量 ORM 插入功能支持在部分后端使用 INSERT..RETURNING，这种形式可以返回一个 :class:`.Result` 对象，该对象既可以返回单独的列值，也可以返回与新插入记录对应的完整 ORM 实体对象。INSERT..RETURNING 要求所用的数据库后端支持 SQL RETURNING 语法，并支持在 :term:`executemany` 模式下使用 RETURNING；这个功能适用于所有 :ref:`SQLAlchemy 内置 <included_dialects>` 的数据库后端， **但不包括 MySQL（MariaDB 是支持的）**。

    举个例子，我们可以运行与之前相同的语句，不过这次加入对 :meth:`.UpdateBase.returning` 方法的调用，并传入完整的 ``User`` 实体以指定希望返回什么。使用 :meth:`_orm.Session.scalars` 可以按 ORM 对象的方式遍历结果::

        >>> users = session.scalars(
        ...     insert(User).returning(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        RETURNING id, name, fullname, species
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}>>> print(users.all())
        [User(name='spongebob', fullname='Spongebob Squarepants'),
        User(name='sandy', fullname='Sandy Cheeks'),
        User(name='patrick', fullname='Patrick Star'),
        User(name='squidward', fullname='Squidward Tentacles'),
        User(name='ehkrabs', fullname='Eugene H. Krabs')]

    在上面的例子中，所生成的 SQL 使用了 SQLite 后端请求的 :ref:`insertmanyvalues <engine_insertmanyvalues>` 特性形式，也就是将多个参数字典内联到一个单独的 INSERT 语句中，从而实现 RETURNING 支持。

    .. versionchanged:: 2.0

        ORM 的 :class:`.Session` 现在可以在 ORM 上下文中解析 :class:`_dml.Insert`、:class:`_dml.Update`，甚至是 :class:`_dml.Delete` 构造中的 RETURNING 子句。这意味着可以将列表达式与 ORM 映射实体混合传递给 :meth:`_dml.Insert.returning` 方法，ORM 将以与 :class:`_sql.Select` 等构造返回 ORM 结果的方式来交付结果，其中映射实体会作为 ORM 映射对象返回。该特性还有限支持 ORM 的加载选项，比如 :func:`_orm.load_only` 和 :func:`_orm.selectinload`。


.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    The bulk ORM insert feature supports INSERT..RETURNING for selected backends, which can return a :class:`.Result` object that may yield individual columns back as well as fully constructed ORM objects corresponding to the newly generated records.    INSERT..RETURNING requires the use of a backend that supports SQL RETURNING syntax as well as support for :term:`executemany` with RETURNING; this feature is available with all :ref:`SQLAlchemy-included <included_dialects>` backends with the exception of MySQL (MariaDB is included).

    As an example, we can run the same statement as before, adding use of the :meth:`.UpdateBase.returning` method, passing the full ``User`` entity as what we'd like to return.  :meth:`_orm.Session.scalars` is used to allow iteration of ``User`` objects::

        >>> users = session.scalars(
        ...     insert(User).returning(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        RETURNING id, name, fullname, species
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}>>> print(users.all())
        [User(name='spongebob', fullname='Spongebob Squarepants'),
        User(name='sandy', fullname='Sandy Cheeks'),
        User(name='patrick', fullname='Patrick Star'),
        User(name='squidward', fullname='Squidward Tentacles'),
        User(name='ehkrabs', fullname='Eugene H. Krabs')]

    In the above example, the rendered SQL takes on the form used by the :ref:`insertmanyvalues <engine_insertmanyvalues>` feature as requested by the SQLite backend, where individual parameter dictionaries are inlined into a single INSERT statement so that RETURNING may be used.

    .. versionchanged:: 2.0  
        
        The ORM :class:`.Session` now interprets RETURNING clauses from :class:`_dml.Insert`, :class:`_dml.Update`, and even :class:`_dml.Delete` constructs in an ORM context, meaning a mixture of column expressions and ORM mapped entities may be passed to the :meth:`_dml.Insert.returning` method which will then be delivered in the way that ORM results are delivered from constructs such as :class:`_sql.Select`, including that mapped entities will be delivered in the result as ORM mapped objects.  Limited support for ORM loader options such as :func:`_orm.load_only` and :func:`_orm.selectinload` is also present.

.. _orm_queryguide_bulk_insert_returning_ordered:

将 RETURNING 记录与输入数据顺序关联
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Correlating RETURNING records with input data order

.. tab:: 中文

    在使用带 RETURNING 的批量 INSERT 时，需要注意大多数数据库后端 **不保证** RETURNING 返回结果的记录顺序，包括其顺序是否与输入记录相对应。在某些应用场景中，如果需要确保 RETURNING 返回的记录能与输入数据正确对应，可以使用额外的参数 :paramref:`_dml.Insert.returning.sort_by_parameter_order`。这个参数在一些数据库后端下会启用特殊的 INSERT 语法，该语法会使用令牌来正确重排返回的记录；或者在某些情况下，例如下面以 SQLite 为例的场景中，操作会以 **逐行插入** 的方式执行::

        >>> data = [
        ...     {"name": "pearl", "fullname": "Pearl Krabs"},
        ...     {"name": "plankton", "fullname": "Plankton"},
        ...     {"name": "gary", "fullname": "Gary"},
        ... ]
        >>> user_ids = session.scalars(
        ...     insert(User).returning(User.id, sort_by_parameter_order=True), data
        ... )
        {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [... (insertmanyvalues) 1/3 (ordered; batch not supported)] ('pearl', 'Pearl Krabs')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 2/3 (ordered; batch not supported)] ('plankton', 'Plankton')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 3/3 (ordered; batch not supported)] ('gary', 'Gary')
        {stop}>>> for user_id, input_record in zip(user_ids, data):
        ...     input_record["id"] = user_id
        >>> print(data)
        [{'name': 'pearl', 'fullname': 'Pearl Krabs', 'id': 6},
        {'name': 'plankton', 'fullname': 'Plankton', 'id': 7},
        {'name': 'gary', 'fullname': 'Gary', 'id': 8}]

    .. versionadded:: 2.0.10

        添加了 :paramref:`_dml.Insert.returning.sort_by_parameter_order`，该参数在 :term:`insertmanyvalues` 架构中实现。

    .. seealso::

        :ref:`engine_insertmanyvalues_returning_order` - 关于在不显著降低性能的前提下，确保输入数据与结果行一一对应的方法背景说明


.. tab:: 英文

    When using bulk INSERT with RETURNING, it's important to note that most database backends provide no formal guarantee of the order in which the records from RETURNING are returned, including that there is no guarantee that their order will correspond to that of the input records.  For applications that need to ensure RETURNING records can be correlated with input data, the additional parameter :paramref:`_dml.Insert.returning.sort_by_parameter_order` may be specified, which depending on backend may use special INSERT forms that maintain a token which is used to reorder the returned rows appropriately, or in some cases, such as in the example below using the SQLite backend, the operation will INSERT one row at a time::

        >>> data = [
        ...     {"name": "pearl", "fullname": "Pearl Krabs"},
        ...     {"name": "plankton", "fullname": "Plankton"},
        ...     {"name": "gary", "fullname": "Gary"},
        ... ]
        >>> user_ids = session.scalars(
        ...     insert(User).returning(User.id, sort_by_parameter_order=True), data
        ... )
        {execsql}INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [... (insertmanyvalues) 1/3 (ordered; batch not supported)] ('pearl', 'Pearl Krabs')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 2/3 (ordered; batch not supported)] ('plankton', 'Plankton')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [insertmanyvalues 3/3 (ordered; batch not supported)] ('gary', 'Gary')
        {stop}>>> for user_id, input_record in zip(user_ids, data):
        ...     input_record["id"] = user_id
        >>> print(data)
        [{'name': 'pearl', 'fullname': 'Pearl Krabs', 'id': 6},
        {'name': 'plankton', 'fullname': 'Plankton', 'id': 7},
        {'name': 'gary', 'fullname': 'Gary', 'id': 8}]

    .. versionadded:: 2.0.10 
        
        Added :paramref:`_dml.Insert.returning.sort_by_parameter_order` which is implemented within the :term:`insertmanyvalues` architecture.

    .. seealso::

        :ref:`engine_insertmanyvalues_returning_order` - background on approaches taken to guarantee correspondence between input data and result rows without significant loss of performance


.. _orm_queryguide_insert_heterogeneous_params:

使用异构参数字典
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Heterogeneous Parameter Dictionaries

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    ORM 的批量插入功能支持所谓“ **异构** ”的参数字典列表，这意味着—— **每个字典可以拥有不同的键** 。当 ORM 检测到这种情况时，会将这些参数字典按键的组合进行分组，然后分别批量生成不同的 INSERT 语句::

        >>> users = session.scalars(
        ...     insert(User).returning(User),
        ...     [
        ...         {
        ...             "name": "spongebob",
        ...             "fullname": "Spongebob Squarepants",
        ...             "species": "Sea Sponge",
        ...         },
        ...         {"name": "sandy", "fullname": "Sandy Cheeks", "species": "Squirrel"},
        ...         {"name": "patrick", "species": "Starfish"},
        ...         {
        ...             "name": "squidward",
        ...             "fullname": "Squidward Tentacles",
        ...             "species": "Squid",
        ...         },
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs", "species": "Crab"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species)
        VALUES (?, ?, ?), (?, ?, ?) RETURNING id, name, fullname, species
        [... (insertmanyvalues) 1/1 (unordered)] ('spongebob', 'Spongebob Squarepants', 'Sea Sponge',
        'sandy', 'Sandy Cheeks', 'Squirrel')
        INSERT INTO user_account (name, species)
        VALUES (?, ?) RETURNING id, name, fullname, species
        [...] ('patrick', 'Starfish')
        INSERT INTO user_account (name, fullname, species)
        VALUES (?, ?, ?), (?, ?, ?) RETURNING id, name, fullname, species
        [... (insertmanyvalues) 1/1 (unordered)] ('squidward', 'Squidward Tentacles',
        'Squid', 'ehkrabs', 'Eugene H. Krabs', 'Crab')

    在上面的例子中，传入的五个参数字典被转换为了三个 INSERT 语句，这些语句是基于字典中键的组合方式分组生成的，同时仍保持了 **行的顺序**，即： ``("name", "fullname", "species")`` 、 ``("name", "species")`` 、 ``("name","fullname", "species")``。

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    The ORM bulk insert feature supports lists of parameter dictionaries that are "heterogeneous", which basically means "individual dictionaries can have different keys".   When this condition is detected, the ORM will break up the parameter dictionaries into groups corresponding to each set of keys and batch accordingly into separate INSERT statements::

        >>> users = session.scalars(
        ...     insert(User).returning(User),
        ...     [
        ...         {
        ...             "name": "spongebob",
        ...             "fullname": "Spongebob Squarepants",
        ...             "species": "Sea Sponge",
        ...         },
        ...         {"name": "sandy", "fullname": "Sandy Cheeks", "species": "Squirrel"},
        ...         {"name": "patrick", "species": "Starfish"},
        ...         {
        ...             "name": "squidward",
        ...             "fullname": "Squidward Tentacles",
        ...             "species": "Squid",
        ...         },
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs", "species": "Crab"},
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species)
        VALUES (?, ?, ?), (?, ?, ?) RETURNING id, name, fullname, species
        [... (insertmanyvalues) 1/1 (unordered)] ('spongebob', 'Spongebob Squarepants', 'Sea Sponge',
        'sandy', 'Sandy Cheeks', 'Squirrel')
        INSERT INTO user_account (name, species)
        VALUES (?, ?) RETURNING id, name, fullname, species
        [...] ('patrick', 'Starfish')
        INSERT INTO user_account (name, fullname, species)
        VALUES (?, ?, ?), (?, ?, ?) RETURNING id, name, fullname, species
        [... (insertmanyvalues) 1/1 (unordered)] ('squidward', 'Squidward Tentacles',
        'Squid', 'ehkrabs', 'Eugene H. Krabs', 'Crab')



    In the above example, the five parameter dictionaries passed translated into three INSERT statements, grouped along the specific sets of keys in each dictionary while still maintaining row order, i.e. ``("name", "fullname", "species")``, ``("name", "species")``, ``("name","fullname", "species")``.

.. _orm_queryguide_insert_null_params:

在 ORM 批量 INSERT 语句中发送 NULL 值
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sending NULL values in ORM bulk INSERT statements

.. tab:: 中文
    
    ORM 的批量插入功能依赖于一种行为，这种行为在旧版的 "bulk" 插入机制中也存在，并且在 ORM 的整体工作单元（unit of work）中同样适用，即： **当某一行包含 NULL 值时，该行会使用一个不引用这些列的 INSERT 语句来插入** ；这样做的理由是，为了让数据库后端及其架构中存在的服务端 INSERT 默认值（这些默认值可能对“是 NULL”与“未提供值”有区别）能够按预期工作。该默认行为会导致批量插入的批次被拆分为多个较小的批次::

        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {
        ...             "name": "name_a",
        ...             "fullname": "Employee A",
        ...             "species": "Squid",
        ...         },
        ...         {
        ...             "name": "name_b",
        ...             "fullname": "Employee B",
        ...             "species": "Squirrel",
        ...         },
        ...         {
        ...             "name": "name_c",
        ...             "fullname": "Employee C",
        ...             "species": None,
        ...         },
        ...         {
        ...             "name": "name_d",
        ...             "fullname": "Employee D",
        ...             "species": "Bluefish",
        ...         },
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] [('name_a', 'Employee A', 'Squid'), ('name_b', 'Employee B', 'Squirrel')]
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] ('name_c', 'Employee C')
        INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] ('name_d', 'Employee D', 'Bluefish')
        ...

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    如上所示，对四行数据的批量 INSERT 被拆分为了三个独立语句，其中第二个语句被格式化为不引用包含 ``None`` 值的列。  
    当数据集中包含大量随机 NULL 值时，这种默认行为可能是 **不理想的**，因为这会导致 `executemany` 操作被拆分为更多更小的操作；尤其当依赖 :ref:`insertmanyvalues <engine_insertmanyvalues>` 功能来减少语句总数时，性能影响可能更大。

    若希望禁用上述 NULL 值的特殊处理行为，可传递执行选项 ``render_nulls=True``；这样所有参数字典会被视为具有相同的键集合，从而统一批处理::

        >>> session.execute(
        ...     insert(User).execution_options(render_nulls=True),
        ...     [
        ...         {
        ...             "name": "name_a",
        ...             "fullname": "Employee A",
        ...             "species": "Squid",
        ...         },
        ...         {
        ...             "name": "name_b",
        ...             "fullname": "Employee B",
        ...             "species": "Squirrel",
        ...         },
        ...         {
        ...             "name": "name_c",
        ...             "fullname": "Employee C",
        ...             "species": None,
        ...         },
        ...         {
        ...             "name": "name_d",
        ...             "fullname": "Employee D",
        ...             "species": "Bluefish",
        ...         },
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] [('name_a', 'Employee A', 'Squid'), ('name_b', 'Employee B', 'Squirrel'), ('name_c', 'Employee C', None), ('name_d', 'Employee D', 'Bluefish')]
        ...

    在上述代码中，所有的参数字典被统一为单个 INSERT 批次发送，包括第三个字典中包含的 ``None`` 值。

    .. versionadded:: 2.0.23  
        
        添加了 ``render_nulls`` 执行选项，它与旧版 :paramref:`_orm.Session.bulk_insert_mappings.render_nulls` 参数行为一致。

.. tab:: 英文

    The bulk ORM insert feature draws upon a behavior that is also present in the legacy "bulk" insert behavior, as well as in the ORM unit of work overall, which is that rows which contain NULL values are INSERTed using a statement that does not refer to those columns; the rationale here is so that backends and schemas which contain server-side INSERT defaults that may be sensitive to the presence of a NULL value vs. no value present will produce a server side value as expected.  This default behavior has the effect of breaking up the bulk inserted batches into more batches of fewer rows::

        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {
        ...             "name": "name_a",
        ...             "fullname": "Employee A",
        ...             "species": "Squid",
        ...         },
        ...         {
        ...             "name": "name_b",
        ...             "fullname": "Employee B",
        ...             "species": "Squirrel",
        ...         },
        ...         {
        ...             "name": "name_c",
        ...             "fullname": "Employee C",
        ...             "species": None,
        ...         },
        ...         {
        ...             "name": "name_d",
        ...             "fullname": "Employee D",
        ...             "species": "Bluefish",
        ...         },
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] [('name_a', 'Employee A', 'Squid'), ('name_b', 'Employee B', 'Squirrel')]
        INSERT INTO user_account (name, fullname) VALUES (?, ?)
        [...] ('name_c', 'Employee C')
        INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] ('name_d', 'Employee D', 'Bluefish')
        ...

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    Above, the bulk INSERT of four rows is broken into three separate statements, the second statement reformatted to not refer to the NULL column for the single parameter dictionary that contains a ``None`` value.    This default behavior may be undesirable when many rows in the dataset contain random NULL values, as it causes the "executemany" operation to be broken into a larger number of smaller operations; particularly when relying upon :ref:`insertmanyvalues <engine_insertmanyvalues>` to reduce the overall number of statements, this can have a bigger performance impact.

    To disable the handling of ``None`` values in the parameters into separate batches, pass the execution option ``render_nulls=True``; this will cause all parameter dictionaries to be treated equivalently, assuming the same set of keys in each dictionary::

        >>> session.execute(
        ...     insert(User).execution_options(render_nulls=True),
        ...     [
        ...         {
        ...             "name": "name_a",
        ...             "fullname": "Employee A",
        ...             "species": "Squid",
        ...         },
        ...         {
        ...             "name": "name_b",
        ...             "fullname": "Employee B",
        ...             "species": "Squirrel",
        ...         },
        ...         {
        ...             "name": "name_c",
        ...             "fullname": "Employee C",
        ...             "species": None,
        ...         },
        ...         {
        ...             "name": "name_d",
        ...             "fullname": "Employee D",
        ...             "species": "Bluefish",
        ...         },
        ...     ],
        ... )
        {execsql}INSERT INTO user_account (name, fullname, species) VALUES (?, ?, ?)
        [...] [('name_a', 'Employee A', 'Squid'), ('name_b', 'Employee B', 'Squirrel'), ('name_c', 'Employee C', None), ('name_d', 'Employee D', 'Bluefish')]
        ...

    Above, all parameter dictionaries are sent in a single INSERT batch, including the ``None`` value present in the third parameter dictionary.

    .. versionadded:: 2.0.23  
        
        Added the ``render_nulls`` execution option which mirrors the behavior of the legacy :paramref:`_orm.Session.bulk_insert_mappings.render_nulls` parameter.

.. _orm_queryguide_insert_joined_table_inheritance:

用于连接表继承的批量 INSERT
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bulk INSERT for Joined Table Inheritance

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.connection()
        BEGIN...

    ORM 批量插入功能构建在传统 :term:`unit of work` 系统所使用的内部机制之上，用于生成 INSERT 语句。  
    这意味着对于一个映射到多个表的 ORM 实体（通常是使用 :ref:`joined table inheritance <joined_inheritance>` 方式映射的实体）， **批量 INSERT 操作会为映射中涉及的每一个表分别生成 INSERT 语句** ，并正确地将服务端生成的主键值传递给依赖这些主键的行。  
    此场景下也支持 RETURNING 功能，ORM 会为每个执行的 INSERT 语句接收一个 :class:`.Result` 对象，之后再将这些结果“水平拼接（horizontally splice）”在一起，使得最终返回的行包含所有被插入的列的值::

        >>> managers = session.scalars(
        ...     insert(Manager).returning(Manager),
        ...     [
        ...         {"name": "sandy", "manager_name": "Sandy Cheeks"},
        ...         {"name": "ehkrabs", "manager_name": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO employee (name, type) VALUES (?, ?) RETURNING id, name, type
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('sandy', 'manager')
        INSERT INTO employee (name, type) VALUES (?, ?) RETURNING id, name, type
        [insertmanyvalues 2/2 (ordered; batch not supported)] ('ehkrabs', 'manager')
        INSERT INTO manager (id, manager_name) VALUES (?, ?), (?, ?) RETURNING id, manager_name, id AS id__1
        [... (insertmanyvalues) 1/1 (ordered)] (1, 'Sandy Cheeks', 2, 'Eugene H. Krabs')

    .. tip:: 
        
        对使用 joined inheritance 映射的类进行批量 INSERT 时，ORM **内部必须使用** :paramref:`_dml.Insert.returning.sort_by_parameter_order` 参数，以便能够将基类表中 RETURNING 返回的主键值与用于插入子表的参数集合进行匹配。
        
        这也是为什么在上例中，SQLite 后端会自动降级为非批处理（non-batched）语句的原因。  
        关于此机制的背景可参见 :ref:`engine_insertmanyvalues_returning_order`。

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.connection()
        BEGIN...

    ORM bulk insert builds upon the internal system that is used by the traditional :term:`unit of work` system in order to emit INSERT statements.  This means that for an ORM entity that is mapped to multiple tables, typically one which is mapped using :ref:`joined table inheritance <joined_inheritance>`, the bulk INSERT operation will emit an INSERT statement for each table represented by the mapping, correctly transferring server-generated primary key values to the table rows that depend upon them.  The RETURNING feature is also supported here, where the ORM will receive :class:`.Result` objects for each INSERT statement executed, and will then "horizontally splice" them together so that the returned rows include values for all columns inserted::

        >>> managers = session.scalars(
        ...     insert(Manager).returning(Manager),
        ...     [
        ...         {"name": "sandy", "manager_name": "Sandy Cheeks"},
        ...         {"name": "ehkrabs", "manager_name": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}INSERT INTO employee (name, type) VALUES (?, ?) RETURNING id, name, type
        [... (insertmanyvalues) 1/2 (ordered; batch not supported)] ('sandy', 'manager')
        INSERT INTO employee (name, type) VALUES (?, ?) RETURNING id, name, type
        [insertmanyvalues 2/2 (ordered; batch not supported)] ('ehkrabs', 'manager')
        INSERT INTO manager (id, manager_name) VALUES (?, ?), (?, ?) RETURNING id, manager_name, id AS id__1
        [... (insertmanyvalues) 1/1 (ordered)] (1, 'Sandy Cheeks', 2, 'Eugene H. Krabs')

    .. tip:: 
        
        Bulk INSERT of joined inheritance mappings requires that the ORM make use of the :paramref:`_dml.Insert.returning.sort_by_parameter_order` parameter internally, so that it can correlate primary key values from RETURNING rows from the base table into the parameter sets being used to INSERT into the "sub" table, which is why the SQLite backend illustrated above transparently degrades to using non-batched statements. Background on this feature is at :ref:`engine_insertmanyvalues_returning_order`.


.. _orm_queryguide_bulk_insert_w_sql:

使用 SQL 表达式的 ORM 批量插入
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

ORM Bulk Insert with SQL Expressions

.. tab:: 中文

    ORM 的批量插入功能支持添加一组 **固定参数** ，这些参数可以包括要应用于每一行的 SQL 表达式。  
    实现方式是结合使用 :meth:`_dml.Insert.values` 方法传入一个将应用于所有行的参数字典，同时在调用 :meth:`_orm.Session.execute` 时以通常的“批量”方式传入单独行的参数字典列表。

    例如，假设有一个 ORM 映射包含一个 "timestamp" 时间戳列：

    .. sourcecode:: python

        import datetime


        class LogRecord(Base):
            __tablename__ = "log_record"
            id: Mapped[int] = mapped_column(primary_key=True)
            message: Mapped[str]
            code: Mapped[str]
            timestamp: Mapped[datetime.datetime]

    如果我们想要插入一系列具有唯一 ``message`` 字段的 ``LogRecord`` 元素，并希望对所有行应用 SQL 函数 ``now()``，那么可以通过 :meth:`_dml.Insert.values` 指定 ``timestamp``，然后以批量模式传入各个记录的值::

        >>> from sqlalchemy import func
        >>> log_record_result = session.scalars(
        ...     insert(LogRecord).values(code="SQLA", timestamp=func.now()).returning(LogRecord),
        ...     [
        ...         {"message": "log message #1"},
        ...         {"message": "log message #2"},
        ...         {"message": "log message #3"},
        ...         {"message": "log message #4"},
        ...     ],
        ... )
        {execsql}INSERT INTO log_record (message, code, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP), (?, ?, CURRENT_TIMESTAMP),
        (?, ?, CURRENT_TIMESTAMP), (?, ?, CURRENT_TIMESTAMP)
        RETURNING id, message, code, timestamp
        [... (insertmanyvalues) 1/1 (unordered)] ('log message #1', 'SQLA', 'log message #2',
        'SQLA', 'log message #3', 'SQLA', 'log message #4', 'SQLA')


        {stop}>>> print(log_record_result.all())
        [LogRecord('log message #1', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #2', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #3', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #4', 'SQLA', datetime.datetime(...))]

.. tab:: 英文

    The ORM bulk insert feature supports the addition of a fixed set of parameters which may include SQL expressions to be applied to every target row. To achieve this, combine the use of the :meth:`_dml.Insert.values` method, passing a dictionary of parameters that will be applied to all rows, with the usual bulk calling form by including a list of parameter dictionaries that contain individual row values when invoking :meth:`_orm.Session.execute`.

    As an example, given an ORM mapping that includes a "timestamp" column:

    .. sourcecode:: python

        import datetime


        class LogRecord(Base):
            __tablename__ = "log_record"
            id: Mapped[int] = mapped_column(primary_key=True)
            message: Mapped[str]
            code: Mapped[str]
            timestamp: Mapped[datetime.datetime]

    If we wanted to INSERT a series of ``LogRecord`` elements, each with a unique ``message`` field, however we would like to apply the SQL function ``now()`` to all rows, we can pass ``timestamp`` within :meth:`_dml.Insert.values` and then pass the additional records using "bulk" mode::

        >>> from sqlalchemy import func
        >>> log_record_result = session.scalars(
        ...     insert(LogRecord).values(code="SQLA", timestamp=func.now()).returning(LogRecord),
        ...     [
        ...         {"message": "log message #1"},
        ...         {"message": "log message #2"},
        ...         {"message": "log message #3"},
        ...         {"message": "log message #4"},
        ...     ],
        ... )
        {execsql}INSERT INTO log_record (message, code, timestamp)
        VALUES (?, ?, CURRENT_TIMESTAMP), (?, ?, CURRENT_TIMESTAMP),
        (?, ?, CURRENT_TIMESTAMP), (?, ?, CURRENT_TIMESTAMP)
        RETURNING id, message, code, timestamp
        [... (insertmanyvalues) 1/1 (unordered)] ('log message #1', 'SQLA', 'log message #2',
        'SQLA', 'log message #3', 'SQLA', 'log message #4', 'SQLA')


        {stop}>>> print(log_record_result.all())
        [LogRecord('log message #1', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #2', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #3', 'SQLA', datetime.datetime(...)),
        LogRecord('log message #4', 'SQLA', datetime.datetime(...))]


.. _orm_queryguide_insert_values:

使用每行 SQL 表达式的 ORM 批量插入
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

ORM Bulk Insert with Per Row SQL Expressions

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {
        ...             "name": "spongebob",
        ...             "fullname": "Spongebob Squarepants",
        ...             "species": "Sea Sponge",
        ...         },
        ...         {"name": "sandy", "fullname": "Sandy Cheeks", "species": "Squirrel"},
        ...         {"name": "patrick", "species": "Starfish"},
        ...         {
        ...             "name": "squidward",
        ...             "fullname": "Squidward Tentacles",
        ...             "species": "Squid",
        ...         },
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs", "species": "Crab"},
        ...     ],
        ... )
        BEGIN...

    `:meth:_dml.Insert.values` 方法本身直接支持一个参数字典的列表。当以这种方式使用 :class:`_dml.Insert` 构造函数时，如果没有将任何参数字典列表传递给 :paramref:`_orm.Session.execute.params` 参数，则不会使用批量 ORM 插入模式，而是将 INSERT 语句按给定形式渲染，并仅执行一次。这种操作模式对于按行传递 SQL 表达式的情况非常有用，也可用于 ORM 中的 "upsert" 语句，后者将在本章稍后介绍 :ref:`orm_queryguide_upsert`。

    下面是一个例子，演示了嵌入每行 SQL 表达式的 INSERT，同时展示了这种形式的 :meth:`_dml.Insert.returning`::

        >>> from sqlalchemy import select
        >>> address_result = session.scalars(
        ...     insert(Address)
        ...     .values(
        ...         [
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "sandy"),
        ...                 "email_address": "sandy@company.com",
        ...             },
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "spongebob"),
        ...                 "email_address": "spongebob@company.com",
        ...             },
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "patrick"),
        ...                 "email_address": "patrick@company.com",
        ...             },
        ...         ]
        ...     )
        ...     .returning(Address),
        ... )
        {execsql}INSERT INTO address (user_id, email_address) VALUES
        ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?), ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?), ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?) RETURNING id, user_id, email_address
        [...] ('sandy', 'sandy@company.com', 'spongebob', 'spongebob@company.com',
        'patrick', 'patrick@company.com')
        {stop}>>> print(address_result.all())
        [Address(email_address='sandy@company.com'),
        Address(email_address='spongebob@company.com'),
        Address(email_address='patrick@company.com')]

    由于上面没有使用批量 ORM 插入模式，因此以下特性没有被启用：

    * :ref:`联合表继承 <orm_queryguide_insert_joined_table_inheritance>` 或其他多表映射不受支持，因为这需要多个 INSERT 语句。

    * :ref:`异构参数集 <orm_queryguide_insert_heterogeneous_params>` 不受支持 - 每个 VALUES 集中的元素必须包含相同的列。

    * 核心级别的优化（例如由 :ref:`insertmanyvalues <engine_insertmanyvalues>` 提供的批处理）不可用；语句需要确保总参数数不超过数据库的限制。

    由于上述原因，通常不建议在 ORM INSERT 语句中使用多个参数集与 :meth:`_dml.Insert.values`，除非有明确的理由，即正在使用 "upsert" 或者需要在每个参数集内嵌入按行的 SQL 表达式。

    .. seealso::

        :ref:`orm_queryguide_upsert`

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {
        ...             "name": "spongebob",
        ...             "fullname": "Spongebob Squarepants",
        ...             "species": "Sea Sponge",
        ...         },
        ...         {"name": "sandy", "fullname": "Sandy Cheeks", "species": "Squirrel"},
        ...         {"name": "patrick", "species": "Starfish"},
        ...         {
        ...             "name": "squidward",
        ...             "fullname": "Squidward Tentacles",
        ...             "species": "Squid",
        ...         },
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs", "species": "Crab"},
        ...     ],
        ... )
        BEGIN...

    The :meth:`_dml.Insert.values` method itself accommodates a list of parameter dictionaries directly. When using the :class:`_dml.Insert` construct in this way, without passing any list of parameter dictionaries to the :paramref:`_orm.Session.execute.params` parameter, bulk ORM insert mode is not used, and instead the INSERT statement is rendered exactly as given and invoked exactly once. This mode of operation may be useful both for the case of passing SQL expressions on a per-row basis, and is also used when using "upsert" statements with the ORM, documented later in this chapter at :ref:`orm_queryguide_upsert`.

    A contrived example of an INSERT that embeds per-row SQL expressions, and also demonstrates :meth:`_dml.Insert.returning` in this form, is below::

        >>> from sqlalchemy import select
        >>> address_result = session.scalars(
        ...     insert(Address)
        ...     .values(
        ...         [
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "sandy"),
        ...                 "email_address": "sandy@company.com",
        ...             },
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "spongebob"),
        ...                 "email_address": "spongebob@company.com",
        ...             },
        ...             {
        ...                 "user_id": select(User.id).where(User.name == "patrick"),
        ...                 "email_address": "patrick@company.com",
        ...             },
        ...         ]
        ...     )
        ...     .returning(Address),
        ... )
        {execsql}INSERT INTO address (user_id, email_address) VALUES
        ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?), ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?), ((SELECT user_account.id
        FROM user_account
        WHERE user_account.name = ?), ?) RETURNING id, user_id, email_address
        [...] ('sandy', 'sandy@company.com', 'spongebob', 'spongebob@company.com',
        'patrick', 'patrick@company.com')
        {stop}>>> print(address_result.all())
        [Address(email_address='sandy@company.com'),
        Address(email_address='spongebob@company.com'),
        Address(email_address='patrick@company.com')]

    Because bulk ORM insert mode is not used above, the following features are not present:

    * :ref:`Joined table inheritance <orm_queryguide_insert_joined_table_inheritance>` or other multi-table mappings are not supported, since that would require multiple INSERT statements.

    * :ref:`Heterogeneous parameter sets <orm_queryguide_insert_heterogeneous_params>` are not supported - each element in the VALUES set must have the same columns.

    * Core-level scale optimizations such as the batching provided by :ref:`insertmanyvalues <engine_insertmanyvalues>` are not available; statements will need to ensure the total number of parameters does not exceed limits imposed by the backing database.

    For the above reasons, it is generally not recommended to use multiple parameter sets with :meth:`_dml.Insert.values` with ORM INSERT statements unless there is a clear rationale, which is either that "upsert" is being used or there is a need to embed per-row SQL expressions in each parameter set.

    .. seealso::

        :ref:`orm_queryguide_upsert`


.. _orm_queryguide_legacy_bulk_insert:

旧会话批量 INSERT 方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Legacy Session Bulk INSERT Methods

.. tab:: 中文

    `:class:_orm.Session` 包含用于执行 "批量" INSERT 和 UPDATE 语句的遗留方法。这些方法与 SQLAlchemy 2.0 版本中的相应特性共享实现，具体描述见 :ref:`orm_queryguide_bulk_insert` 和 :ref:`orm_queryguide_bulk_update`，但缺少许多功能，特别是缺乏 RETURNING 支持以及对会话同步的支持。

    例如，使用 :meth:`.Session.bulk_insert_mappings` 的代码可以按如下方式迁移，首先是这个映射示例::

        session.bulk_insert_mappings(User, [{"name": "u1"}, {"name": "u2"}, {"name": "u3"}])

    上述代码使用新的 API 表达为::

        from sqlalchemy import insert

        session.execute(insert(User), [{"name": "u1"}, {"name": "u2"}, {"name": "u3"}])

    .. seealso::

        :ref:`orm_queryguide_legacy_bulk_update`

.. tab:: 英文

    The :class:`_orm.Session` includes legacy methods for performing "bulk" INSERT and UPDATE statements.  These methods share implementations with the SQLAlchemy 2.0 versions of these features, described at :ref:`orm_queryguide_bulk_insert` and :ref:`orm_queryguide_bulk_update`, however lack many features, namely RETURNING support as well as support for session-synchronization.

    Code which makes use of :meth:`.Session.bulk_insert_mappings` for example can port code as follows, starting with this mappings example::

        session.bulk_insert_mappings(User, [{"name": "u1"}, {"name": "u2"}, {"name": "u3"}])

    The above is expressed using the new API as::

        from sqlalchemy import insert

        session.execute(insert(User), [{"name": "u1"}, {"name": "u2"}, {"name": "u3"}])

    .. seealso::

        :ref:`orm_queryguide_legacy_bulk_update`


.. _orm_queryguide_upsert:

ORM“upsert”语句
~~~~~~~~~~~~~~~~~~~~~~~

ORM "upsert" Statements

.. tab:: 中文

    SQLAlchemy 中的选定后端可能包含特定于方言的 :class:`_dml.Insert` 构造函数，这些构造函数额外具备执行 "upsert"（或插入现有行，并将其转化为近似 UPDATE 语句）功能。所谓的 "现有行"，可能是指具有相同主键值的行，或者是指其他被认为是唯一的索引列；这一点取决于所使用的后端的能力。

    SQLAlchemy 中包含特定于方言的 "upsert" API 功能的方言有：

    * SQLite - 使用 :class:`_sqlite.Insert`，具体文档见 :ref:`sqlite_on_conflict_insert`
    * PostgreSQL - 使用 :class:`_postgresql.Insert`，具体文档见 :ref:`postgresql_insert_on_conflict`
    * MySQL/MariaDB - 使用 :class:`_mysql.Insert`，具体文档见 :ref:`mysql_insert_on_duplicate_key_update`

    用户应查看上述章节，了解如何正确构造这些对象；特别是，"upsert" 方法通常需要引用原始语句，因此该语句通常需要分两步构造。

    如 :ref:`external_toplevel` 中提到的第三方后端也可能具有类似的构造。

    虽然 SQLAlchemy 目前尚未提供一个与后端无关的 upsert 构造，但上述 :class:`_dml.Insert` 变体仍然是 ORM 兼容的，意味着它们可以像文档中描述的 :class:`_dml.Insert` 构造那样使用，具体见 :ref:`orm_queryguide_insert_values`，即通过将要插入的行嵌入到 :meth:`_dml.Insert.values` 方法中。以下示例中，使用 SQLite 的 :func:`_sqlite.insert` 函数生成一个支持 "ON CONFLICT DO UPDATE" 的 :class:`_sqlite.Insert` 构造。然后该语句被传递给 :meth:`_orm.Session.execute`，正常执行，唯一的不同是，传递给 :meth:`_dml.Insert.values` 的参数字典被解释为 ORM 映射的属性键，而不是列名：

    .. 设置代码，不用于展示

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User).values(
        ...         [
        ...             dict(name="sandy"),
        ...             dict(name="spongebob", fullname="Spongebob Squarepants"),
        ...         ]
        ...     )
        ... )
        BEGIN...

    ::

        >>> from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
        >>> stmt = sqlite_upsert(User).values(
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ]
        ... )
        >>> stmt = stmt.on_conflict_do_update(
        ...     index_elements=[User.name], set_=dict(fullname=stmt.excluded.fullname)
        ... )
        >>> session.execute(stmt)
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        ON CONFLICT (name) DO UPDATE SET fullname = excluded.fullname
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}<...>

.. tab:: 英文

    Selected backends with SQLAlchemy may include dialect-specific :class:`_dml.Insert` constructs which additionally have the ability to perform "upserts", or INSERTs where an existing row in the parameter set is turned into an approximation of an UPDATE statement instead. By "existing row" , this may mean rows which share the same primary key value, or may refer to other indexed columns within the row that are considered to be unique; this is dependent on the capabilities of the backend in use.

    The dialects included with SQLAlchemy that include dialect-specific "upsert" API features are:

    * SQLite - using :class:`_sqlite.Insert` documented at :ref:`sqlite_on_conflict_insert`
    * PostgreSQL - using :class:`_postgresql.Insert` documented at :ref:`postgresql_insert_on_conflict`
    * MySQL/MariaDB - using :class:`_mysql.Insert` documented at :ref:`mysql_insert_on_duplicate_key_update`

    Users should review the above sections for background on proper construction of these objects; in particular, the "upsert" method typically needs to refer back to the original statement, so the statement is usually constructed in two separate steps.

    Third party backends such as those mentioned at :ref:`external_toplevel` may
    also feature similar constructs.

    While SQLAlchemy does not yet have a backend-agnostic upsert construct, the above :class:`_dml.Insert` variants are nonetheless ORM compatible in that they may be used in the same way as the :class:`_dml.Insert` construct itself as documented at :ref:`orm_queryguide_insert_values`, that is, by embedding the desired rows to INSERT within the :meth:`_dml.Insert.values` method.   In the example below, the SQLite :func:`_sqlite.insert` function is used to generate an :class:`_sqlite.Insert` construct that includes "ON CONFLICT DO UPDATE" support.   The statement is then passed to :meth:`_orm.Session.execute` where it proceeds normally, with the additional characteristic that the parameter dictionaries passed to :meth:`_dml.Insert.values` are interpreted as ORM mapped attribute keys, rather than column names:

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User).values(
        ...         [
        ...             dict(name="sandy"),
        ...             dict(name="spongebob", fullname="Spongebob Squarepants"),
        ...         ]
        ...     )
        ... )
        BEGIN...

    ::

        >>> from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
        >>> stmt = sqlite_upsert(User).values(
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ]
        ... )
        >>> stmt = stmt.on_conflict_do_update(
        ...     index_elements=[User.name], set_=dict(fullname=stmt.excluded.fullname)
        ... )
        >>> session.execute(stmt)
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        ON CONFLICT (name) DO UPDATE SET fullname = excluded.fullname
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}<...>

.. _orm_queryguide_upsert_returning:

将 RETURNING 与 upsert 语句结合使用
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using RETURNING with upsert statements

.. tab:: 中文

    从 SQLAlchemy ORM 的角度来看，upsert 语句与常规的 :class:`_dml.Insert` 构造类似，这意味着 :meth:`_dml.Insert.returning` 在 upsert 语句中也能正常工作，就像在 :ref:`orm_queryguide_insert_values` 中演示的那样，因此可以传递任何列表达式或相关的 ORM 实体类。继续上一节的示例::

        >>> result = session.scalars(
        ...     stmt.returning(User), execution_options={"populate_existing": True}
        ... )
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        ON CONFLICT (name) DO UPDATE SET fullname = excluded.fullname
        RETURNING id, name, fullname, species
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}>>> print(result.all())
        [User(name='spongebob', fullname='Spongebob Squarepants'),
        User(name='sandy', fullname='Sandy Cheeks'),
        User(name='patrick', fullname='Patrick Star'),
        User(name='squidward', fullname='Squidward Tentacles'),
        User(name='ehkrabs', fullname='Eugene H. Krabs')]

    上面的示例使用了 RETURNING 来返回每一行插入或 upsert 的 ORM 对象。该示例还使用了 :ref:`orm_queryguide_populate_existing` 执行选项。此选项表示对于已经存在的行（在 :class:`_orm.Session` 中已经有的 ``User`` 对象），应该使用新行中的数据进行 **刷新**。对于纯粹的 :class:`_dml.Insert` 语句，此选项并不重要，因为每一行生成的都是全新的主键身份。然而，当 :class:`_dml.Insert` 语句也包含 "upsert" 选项时，它可能会返回已经存在的行的结果，因此这些行可能已经在 :class:`_orm.Session` 对象的 :term:`身份映射` 中有主键身份表示。

    .. seealso::

        :ref:`orm_queryguide_populate_existing`

.. tab:: 英文

    From the SQLAlchemy ORM's point of view, upsert statements look like regular :class:`_dml.Insert` constructs, which includes that :meth:`_dml.Insert.returning` works with upsert statements in the same way as was demonstrated at :ref:`orm_queryguide_insert_values`, so that any column expression or relevant ORM entity class may be passed.  Continuing from the example in the previous section::

        >>> result = session.scalars(
        ...     stmt.returning(User), execution_options={"populate_existing": True}
        ... )
        {execsql}INSERT INTO user_account (name, fullname)
        VALUES (?, ?), (?, ?), (?, ?), (?, ?), (?, ?)
        ON CONFLICT (name) DO UPDATE SET fullname = excluded.fullname
        RETURNING id, name, fullname, species
        [...] ('spongebob', 'Spongebob Squarepants', 'sandy', 'Sandy Cheeks',
        'patrick', 'Patrick Star', 'squidward', 'Squidward Tentacles',
        'ehkrabs', 'Eugene H. Krabs')
        {stop}>>> print(result.all())
        [User(name='spongebob', fullname='Spongebob Squarepants'),
        User(name='sandy', fullname='Sandy Cheeks'),
        User(name='patrick', fullname='Patrick Star'),
        User(name='squidward', fullname='Squidward Tentacles'),
        User(name='ehkrabs', fullname='Eugene H. Krabs')]

    The example above uses RETURNING to return ORM objects for each row inserted or upserted by the statement. The example also adds use of the :ref:`orm_queryguide_populate_existing` execution option. This option indicates that ``User`` objects which are already present in the :class:`_orm.Session` for rows that already exist should be **refreshed** with the data from the new row. For a pure :class:`_dml.Insert` statement, this option is not significant, because every row produced is a brand new primary key identity. However when the :class:`_dml.Insert` also includes "upsert" options, it may also be yielding results from rows that already exist and therefore may already have a primary key identity represented in the :class:`_orm.Session` object's :term:`identity map`.

    .. seealso::

        :ref:`orm_queryguide_populate_existing`


.. _orm_queryguide_bulk_update:

ORM 按主键批量 UPDATE
------------------------------

ORM Bulk UPDATE by Primary Key

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        BEGIN ...
        >>> session.commit()
        COMMIT...
        >>> session.connection()
        BEGIN ...

    :class:`_dml.Update` 构造可以像 :class:`_dml.Insert` 语句那样与 :meth:`_orm.Session.execute` 一起使用，传递多个参数字典的列表，每个字典表示一个对应单个主键值的行。需要注意的是，这种用法不应与使用显式 WHERE 子句的更常见的 :class:`_dml.Update` 语句用法混淆，这种用法在 :ref:`orm_queryguide_update_delete_where` 中有详细说明。

    对于“批量”版本的 UPDATE，首先创建一个基于 ORM 类的 :func:`_dml.update` 构造，并将其传递给 :meth:`_orm.Session.execute` 方法；生成的 :class:`_dml.Update` 对象通常 **不包含值，并且通常不包含 WHERE 条件** ，也就是说，通常不使用 :meth:`_dml.Update.values` 方法，且 :meth:`_dml.Update.where` **通常不使用**，但在某些特殊情况下可以使用，以添加额外的过滤条件。

    传递 :class:`_dml.Update` 构造及其参数字典列表（每个字典包含完整的主键值）将启动 **按主键批量更新模式**，为每一行生成相应的 WHERE 条件，并使用 :term:`executemany` 将每个参数集应用于 UPDATE 语句::

        >>> from sqlalchemy import update
        >>> session.execute(
        ...     update(User),
        ...     [
        ...         {"id": 1, "fullname": "Spongebob Squarepants"},
        ...         {"id": 3, "fullname": "Patrick Star"},
        ...         {"id": 5, "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.id = ?
        [...] [('Spongebob Squarepants', 1), ('Patrick Star', 3), ('Eugene H. Krabs', 5)]
        {stop}<...>

    请注意，每个参数字典 **必须包含每条记录的完整主键**，否则会引发错误。

    与批量 INSERT 功能类似，这里也支持异构参数列表，其中参数将被分成 UPDATE 运行的子批次。

    .. versionchanged:: 2.0.11

        通过使用 :meth:`_dml.Update.where` 方法添加额外的条件，可以将额外的 WHERE 条件与 :ref:`orm_queryguide_bulk_update` 结合使用。然而，这些条件始终是与已经存在的 WHERE 条件一起使用的，后者包括主键值。

    当使用“按主键批量更新”功能时，RETURNING 功能不可用；多个参数字典的列表必然使用 DBAPI :term:`executemany`，而通常这种形式不支持返回结果行。

    .. versionchanged:: 2.0

        将 :class:`_dml.Update` 构造传递给 :meth:`_orm.Session.execute` 方法，并与参数字典列表一起使用时，现在会调用“批量更新”，其功能与旧版的 :meth:`_orm.Session.bulk_update_mappings` 方法相同。这与 1.x 系列的行为有所不同，1.x 系列中 :class:`_dml.Update` 仅支持显式的 WHERE 条件和内联 VALUES。

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK
        >>> session.execute(
        ...     insert(User),
        ...     [
        ...         {"name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"name": "sandy", "fullname": "Sandy Cheeks"},
        ...         {"name": "patrick", "fullname": "Patrick Star"},
        ...         {"name": "squidward", "fullname": "Squidward Tentacles"},
        ...         {"name": "ehkrabs", "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        BEGIN ...
        >>> session.commit()
        COMMIT...
        >>> session.connection()
        BEGIN ...

    The :class:`_dml.Update` construct may be used with :meth:`_orm.Session.execute` in a similar way as the :class:`_dml.Insert` statement is used as described at :ref:`orm_queryguide_bulk_insert`, passing a list of many parameter dictionaries, each dictionary representing an individual row that corresponds to a single primary key value. This use should not be confused with a more common way to use :class:`_dml.Update` statements with the ORM, using an explicit WHERE clause, which is documented at :ref:`orm_queryguide_update_delete_where`.

    For the "bulk" version of UPDATE, a :func:`_dml.update` construct is made in terms of an ORM class and passed to the :meth:`_orm.Session.execute` method; the resulting :class:`_dml.Update` object should have **no values and typically no WHERE criteria**, that is, the :meth:`_dml.Update.values` method is not used, and the :meth:`_dml.Update.where` is **usually** not used, but may be used in the unusual case that additional filtering criteria would be added.

    Passing the :class:`_dml.Update` construct along with a list of parameter dictionaries which each include a full primary key value will invoke **bulk UPDATE by primary key mode** for the statement, generating the appropriate WHERE criteria to match each row by primary key, and using :term:`executemany` to run each parameter set against the UPDATE statement::

        >>> from sqlalchemy import update
        >>> session.execute(
        ...     update(User),
        ...     [
        ...         {"id": 1, "fullname": "Spongebob Squarepants"},
        ...         {"id": 3, "fullname": "Patrick Star"},
        ...         {"id": 5, "fullname": "Eugene H. Krabs"},
        ...     ],
        ... )
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.id = ?
        [...] [('Spongebob Squarepants', 1), ('Patrick Star', 3), ('Eugene H. Krabs', 5)]
        {stop}<...>

    Note that each parameter dictionary **must include a full primary key for each record**, else an error is raised.

    Like the bulk INSERT feature, heterogeneous parameter lists are supported here as well, where the parameters will be grouped into sub-batches of UPDATE runs.

    .. versionchanged:: 2.0.11  
        
        Additional WHERE criteria can be combined with :ref:`orm_queryguide_bulk_update` by using the :meth:`_dml.Update.where` method to add additional criteria.  However this criteria is always in addition to the WHERE criteria that's already made present which includes primary key values.

    The RETURNING feature is not available when using the "bulk UPDATE by primary key" feature; the list of multiple parameter dictionaries necessarily makes use of DBAPI :term:`executemany`, which in its usual form does not typically support result rows.


    .. versionchanged:: 2.0  
        
        Passing an :class:`_dml.Update` construct to the :meth:`_orm.Session.execute` method along with a list of parameter dictionaries now invokes a "bulk update", which makes use of the same functionality as the legacy :meth:`_orm.Session.bulk_update_mappings` method.  This is a behavior change compared to the 1.x series where the :class:`_dml.Update` would only be supported with explicit WHERE criteria and inline VALUES.

.. _orm_queryguide_bulk_update_disabling:

禁用具有多个参数集的 UPDATE 语句的按主键批量 ORM 更新
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Disabling Bulk ORM Update by Primary Key for an UPDATE statement with multiple parameter sets

.. tab:: 中文

    ORM 按主键批量更新功能会针对每条记录运行一个 UPDATE 语句，并为每个主键值添加 WHERE 条件，当满足以下条件时会自动启用此功能：

    1. 给定的 UPDATE 语句是针对 ORM 实体的
    2. 使用 :class:`_orm.Session` 执行语句，而不是 Core 的 :class:`_engine.Connection`
    3. 传递的参数是一个 **字典列表**。

    若要在不使用“ORM 按主键批量更新”的情况下调用 UPDATE 语句，可以直接通过 :meth:`_orm.Session.connection` 方法获取当前的 :class:`_engine.Connection`，然后在事务中执行该语句::

        >>> from sqlalchemy import bindparam
        >>> session.connection().execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] [('Spongebob Squarepants', 'spongebob'), ('Patrick Star', 'patrick')]
        {stop}<...>

    .. seealso::

        :ref:`error_bupq`

.. tab:: 英文

    The ORM Bulk Update by Primary Key feature, which runs an UPDATE statement per record which includes WHERE criteria for each primary key value, is automatically used when:

    1. the UPDATE statement given is against an ORM entity
    2. the :class:`_orm.Session` is used to execute the statement, and not a Core :class:`_engine.Connection`
    3. The parameters passed are a **list of dictionaries**.

    In order to invoke an UPDATE statement without using "ORM Bulk Update by Primary Key", invoke the statement against the :class:`_engine.Connection` directly using the :meth:`_orm.Session.connection` method to acquire the current :class:`_engine.Connection` for the transaction::


        >>> from sqlalchemy import bindparam
        >>> session.connection().execute(
        ...     update(User).where(User.name == bindparam("u_name")),
        ...     [
        ...         {"u_name": "spongebob", "fullname": "Spongebob Squarepants"},
        ...         {"u_name": "patrick", "fullname": "Patrick Star"},
        ...     ],
        ... )
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] [('Spongebob Squarepants', 'spongebob'), ('Patrick Star', 'patrick')]
        {stop}<...>

    .. seealso::

        :ref:`error_bupq`

.. _orm_queryguide_bulk_update_joined_inh:

用于连接表继承的按主键批量 UPDATE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Bulk UPDATE by Primary Key for Joined Table Inheritance

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.execute(
        ...     insert(Manager).returning(Manager),
        ...     [
        ...         {"name": "sandy", "manager_name": "Sandy Cheeks"},
        ...         {"name": "ehkrabs", "manager_name": "Eugene H. Krabs"},
        ...     ],
        ... )
        INSERT...
        >>> session.commit()
        COMMIT...
        >>> session.connection()
        BEGIN (implicit)...

    ORM 批量更新在使用带有联合表继承的映射时，行为与 ORM 批量插入类似；如 :ref:`orm_queryguide_insert_joined_table_inheritance` 中所述，批量 UPDATE 操作会为映射中每个表发出一个 UPDATE 语句，其中给定的参数包括需要更新的值（未受影响的表会被跳过）。

    示例::

        >>> session.execute(
        ...     update(Manager),
        ...     [
        ...         {
        ...             "id": 1,
        ...             "name": "scheeks",
        ...             "manager_name": "Sandy Cheeks, President",
        ...         },
        ...         {
        ...             "id": 2,
        ...             "name": "eugene",
        ...             "manager_name": "Eugene H. Krabs, VP Marketing",
        ...         },
        ...     ],
        ... )
        {execsql}UPDATE employee SET name=? WHERE employee.id = ?
        [...] [('scheeks', 1), ('eugene', 2)]
        UPDATE manager SET manager_name=? WHERE manager.id = ?
        [...] [('Sandy Cheeks, President', 1), ('Eugene H. Krabs, VP Marketing', 2)]
        {stop}<...>

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.execute(
        ...     insert(Manager).returning(Manager),
        ...     [
        ...         {"name": "sandy", "manager_name": "Sandy Cheeks"},
        ...         {"name": "ehkrabs", "manager_name": "Eugene H. Krabs"},
        ...     ],
        ... )
        INSERT...
        >>> session.commit()
        COMMIT...
        >>> session.connection()
        BEGIN (implicit)...

    ORM bulk update has similar behavior to ORM bulk insert when using mappings with joined table inheritance; as described at :ref:`orm_queryguide_insert_joined_table_inheritance`, the bulk UPDATE operation will emit an UPDATE statement for each table represented in the mapping, for which the given parameters include values to be updated (non-affected tables are skipped).

    Example::

        >>> session.execute(
        ...     update(Manager),
        ...     [
        ...         {
        ...             "id": 1,
        ...             "name": "scheeks",
        ...             "manager_name": "Sandy Cheeks, President",
        ...         },
        ...         {
        ...             "id": 2,
        ...             "name": "eugene",
        ...             "manager_name": "Eugene H. Krabs, VP Marketing",
        ...         },
        ...     ],
        ... )
        {execsql}UPDATE employee SET name=? WHERE employee.id = ?
        [...] [('scheeks', 1), ('eugene', 2)]
        UPDATE manager SET manager_name=? WHERE manager.id = ?
        [...] [('Sandy Cheeks, President', 1), ('Eugene H. Krabs, VP Marketing', 2)]
        {stop}<...>

.. _orm_queryguide_legacy_bulk_update:

旧会话批量 UPDATE 方法
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Legacy Session Bulk UPDATE Methods

.. tab:: 中文

    如 :ref:`orm_queryguide_legacy_bulk_insert` 中所述，`:meth:`_orm.Session.bulk_update_mappings` 方法是 :class:`_orm.Session` 的遗留批量更新形式，ORM 在解释带有主键参数的 :func:`_sql.update` 语句时会在内部使用该方法；然而，在使用遗留版本时，诸如会话同步支持等功能是不可用的。

    下面的示例：

        session.bulk_update_mappings(
            User,
            [
                {"id": 1, "name": "scheeks", "manager_name": "Sandy Cheeks, President"},
                {"id": 2, "name": "eugene", "manager_name": "Eugene H. Krabs, VP Marketing"},
            ],
        )

    使用新 API 表示如下：

        from sqlalchemy import update

        session.execute(
            update(User),
            [
                {"id": 1, "name": "scheeks", "manager_name": "Sandy Cheeks, President"},
                {"id": 2, "name": "eugene", "manager_name": "Eugene H. Krabs, VP Marketing"},
            ],
        )

    .. seealso::

        :ref:`orm_queryguide_legacy_bulk_insert`

.. tab:: 英文

    As discussed at :ref:`orm_queryguide_legacy_bulk_insert`, the :meth:`_orm.Session.bulk_update_mappings` method of :class:`_orm.Session` is the legacy form of bulk update, which the ORM makes use of internally when interpreting a :func:`_sql.update` statement with primary key parameters given; however, when using the legacy version, features such as support for session-synchronization are not included.

    The example below::

        session.bulk_update_mappings(
            User,
            [
                {"id": 1, "name": "scheeks", "manager_name": "Sandy Cheeks, President"},
                {"id": 2, "name": "eugene", "manager_name": "Eugene H. Krabs, VP Marketing"},
            ],
        )

    Is expressed using the new API as::

        from sqlalchemy import update

        session.execute(
            update(User),
            [
                {"id": 1, "name": "scheeks", "manager_name": "Sandy Cheeks, President"},
                {"id": 2, "name": "eugene", "manager_name": "Eugene H. Krabs, VP Marketing"},
            ],
        )

    .. seealso::

        :ref:`orm_queryguide_legacy_bulk_insert`



.. _orm_queryguide_update_delete_where:

使用自定义 WHERE 条件的 ORM UPDATE 和 DELETE
------------------------------------------------

ORM UPDATE and DELETE with Custom WHERE Criteria

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    :class:`_dml.Update` 和 :class:`_dml.Delete` 构造体在使用自定义 WHERE 条件（即使用 :meth:`_dml.Update.where` 和 :meth:`_dml.Delete.where` 方法）时，可以通过将其传递给 :meth:`_orm.Session.execute` 来在 ORM 环境中调用，而无需使用 :paramref:`_orm.Session.execute.params` 参数。对于 :class:`_dml.Update`，要更新的值应通过 :meth:`_dml.Update.values` 传递。

    这种用法与之前在 :ref:`orm_queryguide_bulk_update` 中描述的功能不同，因为 ORM 使用给定的 WHERE 子句，而不是将 WHERE 子句固定为主键。这意味着单个 UPDATE 或 DELETE 语句可以一次影响多行数据。

    以下是一个示例，演示了一个 UPDATE 操作影响多个行的 "fullname" 字段::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name.in_(["squidward", "sandy"]))
        ...     .values(fullname="Name starts with S")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name IN (?, ?)
        [...] ('Name starts with S', 'squidward', 'sandy')
        {stop}<...>

    对于 DELETE，下面是基于条件删除行的示例::

        >>> from sqlalchemy import delete
        >>> stmt = delete(User).where(User.name.in_(["squidward", "sandy"]))
        >>> session.execute(stmt)
        {execsql}DELETE FROM user_account WHERE user_account.name IN (?, ?)
        [...] ('squidward', 'sandy')
        {stop}<...>

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    .. warning::

        请阅读以下章节 :ref:`orm_queryguide_update_delete_caveats`，以了解关于 ORM 启用的 UPDATE 和 DELETE 如何与 ORM :term:`工作单元` 特性（如使用 :meth:`_orm.Session.delete` 方法删除单个对象）有所不同的相关重要说明。

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    The :class:`_dml.Update` and :class:`_dml.Delete` constructs, when constructed with custom WHERE criteria (that is, using the :meth:`_dml.Update.where` and :meth:`_dml.Delete.where` methods), may be invoked in an ORM context by passing them to :meth:`_orm.Session.execute`, without using the :paramref:`_orm.Session.execute.params` parameter. For :class:`_dml.Update`, the values to be updated should be passed using :meth:`_dml.Update.values`.

    This mode of use differs from the feature described previously at :ref:`orm_queryguide_bulk_update` in that the ORM uses the given WHERE clause as is, rather than fixing the WHERE clause to be by primary key.   This means that the single UPDATE or DELETE statement can affect many rows at once.

    As an example, below an UPDATE is emitted that affects the "fullname" field of multiple rows::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name.in_(["squidward", "sandy"]))
        ...     .values(fullname="Name starts with S")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name IN (?, ?)
        [...] ('Name starts with S', 'squidward', 'sandy')
        {stop}<...>


    For a DELETE, an example of deleting rows based on criteria::

        >>> from sqlalchemy import delete
        >>> stmt = delete(User).where(User.name.in_(["squidward", "sandy"]))
        >>> session.execute(stmt)
        {execsql}DELETE FROM user_account WHERE user_account.name IN (?, ?)
        [...] ('squidward', 'sandy')
        {stop}<...>

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    .. warning:: 
        
        Please read the following section :ref:`orm_queryguide_update_delete_caveats` for important notes regarding how the functionality of ORM-Enabled UPDATE and DELETE diverges from that of ORM :term:`unit of work` features, such as using the :meth:`_orm.Session.delete` method to delete individual objects.


.. _orm_queryguide_update_delete_caveats:

启用 ORM 的更新和删除的重要说明和注意事项
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Important Notes and Caveats for ORM-Enabled Update and Delete

.. tab:: 中文

    ORM 启用的 UPDATE 和 DELETE 特性绕过了 ORM :term:`工作单元` 自动化，而是能够发出单个 UPDATE 或 DELETE 语句，这样可以一次匹配多个行且不增加复杂性。

    * 这些操作不提供 Python 内部的关系级联操作 - 假设对于需要的外键引用，已经配置了 ON UPDATE CASCADE 和/或 ON DELETE CASCADE，否则如果外键约束被强制执行，数据库可能会发出完整性违反的错误。有关示例，请参阅 :ref:`passive_deletes`。

    * 在 UPDATE 或 DELETE 后，受 ON UPDATE CASCADE 或 ON DELETE CASCADE 影响的、与相关表格相关的依赖对象，尤其是那些指向已删除行的对象，可能仍然引用这些对象。 这个问题在 :class:`.Session` 过期后得到解决，通常是在 :meth:`.Session.commit` 时发生，或者通过使用 :meth:`.Session.expire_all` 强制过期。

    * ORM 启用的 UPDATE 和 DELETE 不会自动处理连接表继承。有关如何处理连接继承映射的说明，请参阅 :ref:`orm_queryguide_update_delete_joined_inh`。

    * 为了将多态性身份限制为特定子类，单表继承映射中所需的 WHERE 条件 **会自动包含**。这仅适用于没有自己表的子类映射器。

    * :func:`_orm.with_loader_criteria` 选项 **被支持** 用于 ORM 更新和删除操作；在这里的条件将添加到要发出的 UPDATE 或 DELETE 语句中，并在 "同步" 过程中被考虑。

    * 要拦截 ORM 启用的 UPDATE 和 DELETE 操作并使用事件处理程序，请使用 :meth:`_orm.SessionEvents.do_orm_execute` 事件。

.. tab:: 英文

    The ORM-enabled UPDATE and DELETE features bypass ORM :term:`unit of work` automation in favor of being able to emit a single UPDATE or DELETE statement that matches multiple rows at once without complexity.

    * The operations do not offer in-Python cascading of relationships - it is assumed that ON UPDATE CASCADE and/or ON DELETE CASCADE is configured for any foreign key references which require it, otherwise the database may emit an integrity violation if foreign key references are being enforced. See the notes at :ref:`passive_deletes` for some examples.

    * After the UPDATE or DELETE, dependent objects in the :class:`.Session` which were impacted by an ON UPDATE CASCADE or ON DELETE CASCADE on related tables, particularly objects that refer to rows that have now been deleted, may still reference those objects.  This issue is resolved once the :class:`.Session` is expired, which normally occurs upon :meth:`.Session.commit` or can be forced by using :meth:`.Session.expire_all`.

    * ORM-enabled UPDATEs and DELETEs do not handle joined table inheritance automatically.   See the section :ref:`orm_queryguide_update_delete_joined_inh` for notes on how to work with joined-inheritance mappings.

    * The WHERE criteria needed in order to limit the polymorphic identity to specific subclasses for single-table-inheritance mappings **is included automatically** .   This only applies to a subclass mapper that has no table of its own.

    * The :func:`_orm.with_loader_criteria` option **is supported** by ORM update and delete operations; criteria here will be added to that of the UPDATE or DELETE statement being emitted, as well as taken into account during the "synchronize" process.

    * In order to intercept ORM-enabled UPDATE and DELETE operations with event handlers, use the :meth:`_orm.SessionEvents.do_orm_execute` event.


.. _orm_queryguide_update_delete_sync:


选择同步策略
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Selecting a Synchronization Strategy

.. tab:: 中文

    当使用 :func:`_dml.update` 或 :func:`_dml.delete` 配合通过 :meth:`_orm.Session.execute` 执行时，SQLAlchemy 提供了额外的 ORM 特定功能，能够 **同步** 由语句更改的状态与当前 :class:`_orm.Session` 中的对象状态。这里的“同步”是指：UPDATE 的属性将被刷新为新值，或者至少被 **过期**，以便下次访问时重新填充新值；而被 DELETE 的对象将被标记为已删除状态。

    同步行为可以通过 "同步策略" 来控制，该策略作为字符串 ORM 执行选项传递，通常通过使用 :paramref:`_orm.Session.execute.execution_options` 字典::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User).where(User.name == "squidward").values(fullname="Squidward Tentacles")
        ... )
        >>> session.execute(stmt, execution_options={"synchronize_session": False})
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Squidward Tentacles', 'squidward')
        {stop}<...>

    执行选项也可以通过 :meth:`_sql.Executable.execution_options` 方法与语句一起传递::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name == "squidward")
        ...     .values(fullname="Squidward Tentacles")
        ...     .execution_options(synchronize_session=False)
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Squidward Tentacles', 'squidward')
        {stop}<...>

    ``synchronize_session`` 支持以下值：

    * ``'auto'`` - 默认值。若后端支持 RETURNING（包括除 MySQL 之外的所有 SQLAlchemy 原生驱动程序），则使用 ``"fetch"`` 策略。如果不支持 RETURNING，则使用 `evaluate` 策略。

    * ``'fetch'`` - 通过执行 SELECT 语句或使用数据库支持的 RETURNING 来检索受影响行的主键，以便在内存中的对象能够刷新更新的值（更新操作）或从 :class:`_orm.Session` 中移除已删除的对象（删除操作）。即使给定的 :func:`_dml.update` 或 :func:`_dml.delete` 语句显式指定了返回值或列，也可以使用此同步策略。

      .. versionchanged:: 2.0 
        
      在使用带有 WHERE 条件的 ORM 启用的 UPDATE 和 DELETE 时，显式使用 :meth:`_dml.UpdateBase.returning` 可以与 ``"fetch"`` 同步策略结合使用。实际语句将包含 `fetch` 策略所需的列与请求的列的联合。

    * ``'evaluate'`` - 该策略指示在 Python 中评估 UPDATE 或 DELETE 语句中的 WHERE 条件，以在 :class:`_orm.Session` 中找到匹配的对象。此方法不会增加 SQL 的往返次数，并且在没有 RETURNING 支持时可能更高效。但对于复杂的 UPDATE 或 DELETE 条件，`'evaluate'` 策略可能无法在 Python 中评估表达式，从而抛出错误。如果发生此情况，建议使用 ``"fetch"`` 策略。

      .. tip::

            如果 SQL 表达式使用了自定义操作符（使用 :meth:`_sql.Operators.op` 或 :class:`_sql.custom_op` 特性），则可以通过 :paramref:`_sql.Operators.op.python_impl` 参数指定一个 Python 函数，该函数将在 ``"evaluate"`` 同步策略中使用。

            .. versionadded:: 2.0

            .. warning::

                如果 UPDATE 操作要在一个已过期许多对象的 :class:`_orm.Session` 上运行，建议避免使用 ``"evaluate"`` 策略，因为它必须刷新对象以测试其是否符合给定的 WHERE 条件，这将导致为每个对象发出一个 SELECT。在这种情况下，尤其是后端支持 RETURNING 时，应该更倾向于使用 ``"fetch"`` 策略。

    * ``False`` - 不同步会话。对于不支持 RETURNING 的后端，如果 ``"evaluate"`` 策略无法使用，则此选项非常有用。在这种情况下，`_orm.Session` 中的对象状态不会自动与发出的 UPDATE 或 DELETE 语句对应，如果存在那些本应对应匹配行的对象，状态将保持不变。

.. tab:: 英文

    When making use of :func:`_dml.update` or :func:`_dml.delete` in conjunction with ORM-enabled execution using :meth:`_orm.Session.execute`, additional ORM-specific functionality is present which will **synchronize** the state being changed by the statement with that of the objects that are currently present within the :term:`identity map` of the :class:`_orm.Session`. By "synchronize" we mean that UPDATEd attributes will be refreshed with the new value, or at the very least :term:`expired` so that they will re-populate with their new value on next access, and DELETEd objects will be moved into the :term:`deleted` state.
    
    This synchronization is controllable as the "synchronization strategy", which is passed as an string ORM execution option, typically by using the :paramref:`_orm.Session.execute.execution_options` dictionary::
    
        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User).where(User.name == "squidward").values(fullname="Squidward Tentacles")
        ... )
        >>> session.execute(stmt, execution_options={"synchronize_session": False})
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Squidward Tentacles', 'squidward')
        {stop}<...>
    
    The execution option may also be bundled with the statement itself using the :meth:`_sql.Executable.execution_options` method::
    
        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name == "squidward")
        ...     .values(fullname="Squidward Tentacles")
        ...     .execution_options(synchronize_session=False)
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        [...] ('Squidward Tentacles', 'squidward')
        {stop}<...>
    
    The following values for ``synchronize_session`` are supported:
    
    * ``'auto'`` - this is the default.   The ``'fetch'`` strategy will be used on backends that support RETURNING, which includes all SQLAlchemy-native drivers except for MySQL.   If RETURNING is not supported, the ``'evaluate'`` strategy will be used instead.
    
    * ``'fetch'`` - Retrieves the primary key identity of affected rows by either performing a SELECT before the UPDATE or DELETE, or by using RETURNING if the database supports it, so that in-memory objects which are affected by the operation can be refreshed with new values (updates) or expunged from the :class:`_orm.Session` (deletes). This synchronization strategy may be used even if the given :func:`_dml.update` or :func:`_dml.delete` construct explicitly specifies entities or columns using :meth:`_dml.UpdateBase.returning`.
    
      .. versionchanged:: 2.0 
        
        Explicit :meth:`_dml.UpdateBase.returning` may be combined with the ``'fetch'`` synchronization strategy when using ORM-enabled UPDATE and DELETE with WHERE criteria.  The actual statement will contain the union of columns between that which the ``'fetch'`` strategy requires and those which were requested.
    
    * ``'evaluate'`` - This indicates to evaluate the WHERE criteria given in the UPDATE or DELETE statement in Python, to locate matching objects within the :class:`_orm.Session`. This approach does not add any SQL round trips to the operation, and in the absence of RETURNING support, may be more efficient. For UPDATE or DELETE statements with complex criteria, the ``'evaluate'`` strategy may not be able to evaluate the expression in Python and will raise an error. If this occurs, use the ``'fetch'`` strategy for the operation instead.
    
      .. tip::
    
        If a SQL expression makes use of custom operators using the :meth:`_sql.Operators.op` or :class:`_sql.custom_op` feature, the :paramref:`_sql.Operators.op.python_impl` parameter may be used to indicate a Python function that will be used by the ``"evaluate"`` synchronization strategy.
    
        .. versionadded:: 2.0
    
      .. warning::
    
        The ``"evaluate"`` strategy should be avoided if an UPDATE operation is to run on a :class:`_orm.Session` that has many objects which have been expired, because it will necessarily need to refresh objects in order to test them against the given WHERE criteria, which will emit a SELECT for each one.   In this case, and particularly if the backend supports RETURNING, the ``"fetch"`` strategy should be preferred.
    
    * ``False`` - don't synchronize the session. This option may be useful for backends that don't support RETURNING where the ``"evaluate"`` strategy is not able to be used.  In this case, the state of objects in the :class:`_orm.Session` is unchanged and will not automatically correspond to the UPDATE or DELETE statement that was emitted, if such objects that would normally correspond to the rows matched are present.


.. _orm_queryguide_update_delete_where_returning:

使用 RETURNING 和 UPDATE/DELETE 以及自定义 WHERE 条件
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using RETURNING with UPDATE/DELETE and Custom WHERE Criteria

.. tab:: 中文

    `:meth:`.UpdateBase.returning` 方法与带有 WHERE 条件的 ORM 启用的 UPDATE 和 DELETE 操作完全兼容。可以指定完整的 ORM 对象和/或列进行 RETURNING 操作::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name == "squidward")
        ...     .values(fullname="Squidward Tentacles")
        ...     .returning(User)
        ... )
        >>> result = session.scalars(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        RETURNING id, name, fullname, species
        [...] ('Squidward Tentacles', 'squidward')
        {stop}>>> print(result.all())
        [User(name='squidward', fullname='Squidward Tentacles')]

    RETURNING 的支持与 ``fetch`` 同步策略兼容，后者也使用 RETURNING。ORM 会适当地组织 RETURNING 中的列，以确保同步过程顺利进行，同时返回的 :class:`.Result` 将包含按请求顺序排列的实体和 SQL 列。

    .. versionadded:: 2.0  

        :meth:`.UpdateBase.returning` 可用于 ORM 启用的 UPDATE 和 DELETE，同时仍然与 ``fetch`` 同步策略完全兼容。

.. tab:: 英文

    The :meth:`.UpdateBase.returning` method is fully compatible with ORM-enabled UPDATE and DELETE with WHERE criteria.   Full ORM objects and/or columns may be indicated for RETURNING::

        >>> from sqlalchemy import update
        >>> stmt = (
        ...     update(User)
        ...     .where(User.name == "squidward")
        ...     .values(fullname="Squidward Tentacles")
        ...     .returning(User)
        ... )
        >>> result = session.scalars(stmt)
        {execsql}UPDATE user_account SET fullname=? WHERE user_account.name = ?
        RETURNING id, name, fullname, species
        [...] ('Squidward Tentacles', 'squidward')
        {stop}>>> print(result.all())
        [User(name='squidward', fullname='Squidward Tentacles')]

    The support for RETURNING is also compatible with the ``fetch`` synchronization strategy, which also uses RETURNING.  The ORM will organize the columns in RETURNING appropriately so that the synchronization proceeds as well as that the returned :class:`.Result` will contain the requested entities and SQL columns in their requested order.

    .. versionadded:: 2.0  
        
        :meth:`.UpdateBase.returning` may be used for ORM enabled UPDATE and DELETE while still retaining full compatibility with the ``fetch`` synchronization strategy.

.. _orm_queryguide_update_delete_joined_inh:

使用 UPDATE/DELETE 和自定义 WHERE 条件进行连接表继承
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

UPDATE/DELETE with Custom WHERE Criteria for Joined Table Inheritance

.. tab:: 中文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    UPDATE/DELETE 语句与 WHERE 条件的特性，与 :ref:`orm_queryguide_bulk_update` 不同，每次调用 :meth:`_orm.Session.execute` 时只会发出单个 UPDATE 或 DELETE 语句。这意味着，当对多表映射（例如，连接表继承映射中的子类）运行 :func:`_dml.update` 或 :func:`_dml.delete` 语句时，必须遵循后端当前的能力，这可能包括后端不支持涉及多个表的 UPDATE 或 DELETE 语句，或者仅有限支持。这意味着对于像连接继承子类这样的映射，ORM 版本的 UPDATE/DELETE 语句在使用 WHERE 条件时只能在一定程度上使用，或者完全不能使用，具体取决于后端的特性。

    对于连接表继承子类，发出多行 UPDATE 语句的最直接方法是仅引用子表。这意味着 :func:`_dml.Update` 构造应仅引用本地子类表中的属性，如下所示::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(Manager.id == 1)
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? WHERE manager.id = ?
        [...] ('Sandy Cheeks, President', 1)
        <...>

    对于上述形式，一种基本的方法是使用子查询来引用基础表，以便在任何 SQL 后端上工作::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(
        ...         Manager.id
        ...         == select(Employee.id).where(Employee.name == "sandy").scalar_subquery()
        ...     )
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? WHERE manager.id = (SELECT employee.id
        FROM employee
        WHERE employee.name = ?) RETURNING id
        [...] ('Sandy Cheeks, President', 'sandy')
        {stop}<...>

    对于支持 `UPDATE...FROM` 的后端，子查询可以作为额外的简单 WHERE 条件表示，然而两个表之间的条件必须明确声明::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(Manager.id == Employee.id, Employee.name == "sandy")
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? FROM employee
        WHERE manager.id = employee.id AND employee.name = ?
        [...] ('Sandy Cheeks, President', 'sandy')
        {stop}<...>

    对于 DELETE，预计基础表和子表中的行会同时被删除。为了 **不使用** 外键级联删除多个连接继承对象的行，应单独为每个表发出 DELETE 语句::

        >>> from sqlalchemy import delete
        >>> session.execute(delete(Manager).where(Manager.id == 1))
        {execsql}DELETE FROM manager WHERE manager.id = ?
        [...] (1,)
        {stop}<...>
        >>> session.execute(delete(Employee).where(Employee.id == 1))
        {execsql}DELETE FROM employee WHERE employee.id = ?
        [...] (1,)
        {stop}<...>

    总体而言，正常的 :term:`unit of work` 过程应 **优先** 用于更新和删除连接继承和其他多表映射中的行，除非有使用自定义 WHERE 条件的性能理由。

.. tab:: 英文

    ..  Setup code, not for display

        >>> session.rollback()
        ROLLBACK...
        >>> session.connection()
        BEGIN (implicit)...

    The UPDATE/DELETE with WHERE criteria feature, unlike the :ref:`orm_queryguide_bulk_update`, only emits a single UPDATE or DELETE statement per call to :meth:`_orm.Session.execute`. This means that when running an :func:`_dml.update` or :func:`_dml.delete` statement against a multi-table mapping, such as a subclass in a joined-table inheritance mapping, the statement must conform to the backend's current capabilities, which may include that the backend does not support an UPDATE or DELETE statement that refers to multiple tables, or may have only limited support for this. This means that for mappings such as joined inheritance subclasses, the ORM version of the UPDATE/DELETE with WHERE criteria feature can only be used to a limited extent or not at all, depending on specifics.

    The most straightforward way to emit a multi-row UPDATE statement for a joined-table subclass is to refer to the sub-table alone. This means the :func:`_dml.Update` construct should only refer to attributes that are local to the subclass table, as in the example below::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(Manager.id == 1)
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? WHERE manager.id = ?
        [...] ('Sandy Cheeks, President', 1)
        <...>

    With the above form, a rudimentary way to refer to the base table in order to locate rows which will work on any SQL backend is so use a subquery::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(
        ...         Manager.id
        ...         == select(Employee.id).where(Employee.name == "sandy").scalar_subquery()
        ...     )
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? WHERE manager.id = (SELECT employee.id
        FROM employee
        WHERE employee.name = ?) RETURNING id
        [...] ('Sandy Cheeks, President', 'sandy')
        {stop}<...>

    For backends that support UPDATE...FROM, the subquery may be stated instead as additional plain WHERE criteria, however the criteria between the two tables must be stated explicitly in some way::

        >>> stmt = (
        ...     update(Manager)
        ...     .where(Manager.id == Employee.id, Employee.name == "sandy")
        ...     .values(manager_name="Sandy Cheeks, President")
        ... )
        >>> session.execute(stmt)
        {execsql}UPDATE manager SET manager_name=? FROM employee
        WHERE manager.id = employee.id AND employee.name = ?
        [...] ('Sandy Cheeks, President', 'sandy')
        {stop}<...>


    For a DELETE, it's expected that rows in both the base table and the sub-table would be DELETEd at the same time.   To DELETE many rows of joined inheritance objects **without** using cascading foreign keys, emit DELETE for each table individually::

        >>> from sqlalchemy import delete
        >>> session.execute(delete(Manager).where(Manager.id == 1))
        {execsql}DELETE FROM manager WHERE manager.id = ?
        [...] (1,)
        {stop}<...>
        >>> session.execute(delete(Employee).where(Employee.id == 1))
        {execsql}DELETE FROM employee WHERE employee.id = ?
        [...] (1,)
        {stop}<...>

    Overall, normal :term:`unit of work` processes should be **preferred** for updating and deleting rows for joined inheritance and other multi-table mappings, unless there is a performance rationale for using custom WHERE criteria.


旧式查询方法
~~~~~~~~~~~~~~~~~~~~

Legacy Query Methods

.. tab:: 中文

    ORM 启用的 UPDATE/DELETE 与 WHERE 条件的特性最初是 :class:`.Query` 对象的一部分，位于 :meth:`_orm.Query.update` 和 :meth:`_orm.Query.delete` 方法中。这些方法仍然可用，并提供了与 :ref:`orm_queryguide_update_delete_where` 中描述的功能相同的子集。主要的区别是，遗留方法不支持显式的 RETURNING 功能。

    .. seealso::

        :meth:`_orm.Query.update`

        :meth:`_orm.Query.delete`

.. tab:: 英文

    The ORM enabled UPDATE/DELETE with WHERE feature was originally part of the now-legacy :class:`.Query` object, in the :meth:`_orm.Query.update` and :meth:`_orm.Query.delete` methods.  These methods remain available and provide a subset of the same functionality as that described at :ref:`orm_queryguide_update_delete_where`.  The primary difference is that the legacy methods don't provide for explicit RETURNING support.

    .. seealso::

        :meth:`_orm.Query.update`

        :meth:`_orm.Query.delete`

..  Setup code, not for display

    >>> session.close()
    ROLLBACK...
    >>> conn.close()
