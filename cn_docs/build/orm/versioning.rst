.. _mapper_version_counter:

配置版本计数器
=============================

Configuring a Version Counter

.. tab:: 中文

    :class:`_orm.Mapper` 支持管理 :term:`version id column`，这是一个单表列，每次对映射表执行 ``UPDATE`` 时都会递增或以其他方式更新其值。每次 ORM 发出针对该行的 ``UPDATE`` 或 ``DELETE`` 时，都会检查此值，以确保内存中保存的值与数据库值匹配。

    .. warning::

        由于版本控制功能依赖于对象的 **内存中** 记录的比较，该功能仅适用于 :meth:`.Session.flush` 过程，其中 ORM 将单个内存行刷新到数据库。当使用 :meth:`_query.Query.update` 或 :meth:`_query.Query.delete` 方法执行多行 UPDATE 或 DELETE 时，该功能 **不会** 生效，因为这些方法仅发出 UPDATE 或 DELETE 语句，但无法直接访问受影响行的内容。

    该功能的目的是检测两个并发事务在大致相同的时间修改同一行的情况，或者在系统可能重新使用之前事务的数据而不刷新时，提供防止使用“过时”行的保护（例如，如果使用 :class:`.Session` 设置 ``expire_on_commit=False``，则可以重新使用之前事务的数据）。

    .. topic:: 并发事务更新

        在事务中检测并发更新时，通常数据库的事务隔离级别低于 :term:`repeatable read`；否则，事务将不会暴露于与本地更新值冲突的并发更新创建的新行值。在这种情况下，SQLAlchemy 的版本控制功能通常对事务内冲突检测没有用处，尽管它仍然可以用于跨事务的陈旧检测。

        执行可重复读取的数据库通常会锁定目标行以防止并发更新，或者采用某种形式的多版本并发控制，在提交事务时发出错误。SQLAlchemy 的 version_id_col 是一种替代方法，允许在事务内对特定表进行版本跟踪，而该事务可能没有设置此隔离级别。

        .. seealso::

            `可重复读隔离级别(Repeatable Read Isolation Level) <https://www.postgresql.org/docs/current/static/transaction-iso.html#XACT-REPEATABLE-READ>`_ - PostgreSQL 的可重复读取实现，包括错误条件的描述。

.. tab:: 英文

    The :class:`_orm.Mapper` supports management of a :term:`version id column`, which
    is a single table column that increments or otherwise updates its value
    each time an ``UPDATE`` to the mapped table occurs.  This value is checked each
    time the ORM emits an ``UPDATE`` or ``DELETE`` against the row to ensure that
    the value held in memory matches the database value.

    .. warning::

        Because the versioning feature relies upon comparison of the **in memory**
        record of an object, the feature only applies to the :meth:`.Session.flush`
        process, where the ORM flushes individual in-memory rows to the database.
        It does **not** take effect when performing
        a multirow UPDATE or DELETE using :meth:`_query.Query.update` or :meth:`_query.Query.delete`
        methods, as these methods only emit an UPDATE or DELETE statement but otherwise
        do not have direct access to the contents of those rows being affected.

    The purpose of this feature is to detect when two concurrent transactions
    are modifying the same row at roughly the same time, or alternatively to provide
    a guard against the usage of a "stale" row in a system that might be re-using
    data from a previous transaction without refreshing (e.g. if one sets ``expire_on_commit=False``
    with a :class:`.Session`, it is possible to re-use the data from a previous
    transaction).

    .. topic:: Concurrent transaction updates

        When detecting concurrent updates within transactions, it is typically the
        case that the database's transaction isolation level is below the level of
        :term:`repeatable read`; otherwise, the transaction will not be exposed
        to a new row value created by a concurrent update which conflicts with
        the locally updated value.  In this case, the SQLAlchemy versioning
        feature will typically not be useful for in-transaction conflict detection,
        though it still can be used for cross-transaction staleness detection.

        The database that enforces repeatable reads will typically either have locked the
        target row against a concurrent update, or is employing some form
        of multi version concurrency control such that it will emit an error
        when the transaction is committed.  SQLAlchemy's version_id_col is an alternative
        which allows version tracking to occur for specific tables within a transaction
        that otherwise might not have this isolation level set.

        .. seealso::

            `Repeatable Read Isolation Level <https://www.postgresql.org/docs/current/static/transaction-iso.html#XACT-REPEATABLE-READ>`_ - PostgreSQL's implementation of repeatable read, including a description of the error condition.

简单版本计数
-----------------------

Simple Version Counting

.. tab:: 中文

    最简单的版本跟踪方法是向映射表添加一个整数列，然后在映射器选项中将其建立为 ``version_id_col``::

        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_id = mapped_column(Integer, nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {"version_id_col": version_id}

    .. note::  
        
        **强烈建议** 将 ``version_id`` 列设置为 NOT NULL。版本控制功能 **不支持** 版本控制列中的 NULL 值。

    在上面， ``User`` 映射使用 ``version_id`` 列跟踪整数版本。当首次刷新 ``User`` 类型的对象时， ``version_id`` 列将被赋值为 "1"。然后，表的 UPDATE 将始终以类似于以下方式发出：

    .. sourcecode:: sql

        UPDATE user SET version_id=:version_id, name=:name
        WHERE user.id = :user_id AND user.version_id = :user_version_id
        -- {"name": "new name", "version_id": 2, "user_id": 1, "user_version_id": 1}

    上述 UPDATE 语句正在更新不仅匹配 ``user.id = 1`` 的行，还要求 ``user.version_id = 1``，其中 "1" 是我们已知在此对象上使用的最后版本标识符。如果其他事务独立修改了该行，则该版本 ID 将不再匹配，并且 UPDATE 语句将报告没有匹配的行；这是 SQLAlchemy 测试的条件，即我们的 UPDATE（或 DELETE）语句恰好匹配一行。如果没有行匹配，这表明我们的数据版本已过时，并引发 :exc:`.StaleDataError`。

.. tab:: 英文

    The most straightforward way to track versions is to add an integer column
    to the mapped table, then establish it as the ``version_id_col`` within the
    mapper options::

        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_id = mapped_column(Integer, nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {"version_id_col": version_id}

    .. note::  It is **strongly recommended** that the ``version_id`` column
    be made NOT NULL.  The versioning feature **does not support** a NULL
    value in the versioning column.

    Above, the ``User`` mapping tracks integer versions using the column
    ``version_id``.   When an object of type ``User`` is first flushed, the
    ``version_id`` column will be given a value of "1".   Then, an UPDATE
    of the table later on will always be emitted in a manner similar to the
    following:

    .. sourcecode:: sql

        UPDATE user SET version_id=:version_id, name=:name
        WHERE user.id = :user_id AND user.version_id = :user_version_id
        -- {"name": "new name", "version_id": 2, "user_id": 1, "user_version_id": 1}

    The above UPDATE statement is updating the row that not only matches
    ``user.id = 1``, it also is requiring that ``user.version_id = 1``, where "1"
    is the last version identifier we've been known to use on this object.
    If a transaction elsewhere has modified the row independently, this version id
    will no longer match, and the UPDATE statement will report that no rows matched;
    this is the condition that SQLAlchemy tests, that exactly one row matched our
    UPDATE (or DELETE) statement.  If zero rows match, that indicates our version
    of the data is stale, and a :exc:`.StaleDataError` is raised.

.. _custom_version_counter:

自定义版本计数器/类型
-------------------------------

Custom Version Counters / Types

.. tab:: 中文

    其他类型的值或计数器也可以用于版本控制。常见类型包括日期和 GUID。当使用替代类型或计数器方案时，SQLAlchemy 提供了一个钩子，通过 ``version_id_generator`` 参数为此方案提供支持，该参数接受一个版本生成的可调用对象。这个可调用对象会传递当前已知版本的值，并预期返回后续版本。

    例如，如果我们想使用随机生成的 GUID 来跟踪我们的 ``User`` 类的版本控制，可以这样做（注意某些后端支持本地 GUID 类型，但这里我们使用简单的字符串来演示）::

        import uuid


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_uuid = mapped_column(String(32), nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {
                "version_id_col": version_uuid,
                "version_id_generator": lambda version: uuid.uuid4().hex,
            }

    每次 ``User`` 对象进行 INSERT 或 UPDATE 时，持久化引擎都会调用 ``uuid.uuid4()``。在这种情况下，我们的版本生成函数可以忽略传入的 ``version`` 值，因为 ``uuid4()`` 函数生成的标识符无需任何先决值。如果我们使用的是序列化版本控制方案（如数字或特殊字符系统），则可以利用给定的 ``version`` 来帮助确定后续值。

    .. seealso::

        :ref:`custom_guid_type`

.. tab:: 英文

    Other kinds of values or counters can be used for versioning.  Common types include
    dates and GUIDs.   When using an alternate type or counter scheme, SQLAlchemy
    provides a hook for this scheme using the ``version_id_generator`` argument,
    which accepts a version generation callable.  This callable is passed the value of the current
    known version, and is expected to return the subsequent version.

    For example, if we wanted to track the versioning of our ``User`` class
    using a randomly generated GUID, we could do this (note that some backends
    support a native GUID type, but we illustrate here using a simple string)::

        import uuid


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_uuid = mapped_column(String(32), nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {
                "version_id_col": version_uuid,
                "version_id_generator": lambda version: uuid.uuid4().hex,
            }

    The persistence engine will call upon ``uuid.uuid4()`` each time a
    ``User`` object is subject to an INSERT or an UPDATE.  In this case, our
    version generation function can disregard the incoming value of ``version``,
    as the ``uuid4()`` function
    generates identifiers without any prerequisite value.  If we were using
    a sequential versioning scheme such as numeric or a special character system,
    we could make use of the given ``version`` in order to help determine the
    subsequent value.

    .. seealso::

        :ref:`custom_guid_type`

.. _server_side_version_counter:

服务器端版本计数器
----------------------------

Server Side Version Counters

.. tab:: 中文

    ``version_id_generator`` 也可以配置为依赖于由数据库生成的值。在这种情况下，数据库需要某种方式在插入和更新时生成新的标识符。对于更新情况，通常需要一个更新触发器，除非所讨论的数据库支持其他本机版本标识符。特别是 PostgreSQL 数据库支持一个称为 `xmin <https://www.postgresql.org/docs/current/static/ddl-system-columns.html>`_ 的系统列，它提供更新版本控制。我们可以使用 PostgreSQL 的 ``xmin`` 列来对我们的 ``User`` 类进行版本控制，如下所示::

        from sqlalchemy import FetchedValue


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50), nullable=False)
            xmin = mapped_column("xmin", String, system=True, server_default=FetchedValue())

            __mapper_args__ = {"version_id_col": xmin, "version_id_generator": False}

    通过上述映射，ORM 将依赖于 ``xmin`` 列自动提供版本 ID 计数器的新值。

    .. topic:: 创建引用系统列的表

        在上述场景中，由于 ``xmin`` 是 PostgreSQL 提供的系统列，我们使用 ``system=True`` 参数将其标记为系统提供的列，从 ``CREATE TABLE`` 语句中省略。此列的数据类型是一个称为 ``xid`` 的内部 PostgreSQL 类型，主要表现为字符串，因此我们使用 :class:`_types.String` 数据类型。

    ORM 通常在发出 INSERT 或 UPDATE 时不会主动获取数据库生成的值，而是将这些列标记为“已过期”，并在下次访问时获取，除非设置了 ``eager_defaults`` :class:`_orm.Mapper` 标志。然而，当使用服务器端版本列时，ORM 需要主动获取新生成的值。这是为了在任何并发事务可能再次更新之前设置版本计数器。最好在 INSERT 或 UPDATE 语句中同时使用 :term:`RETURNING` 进行此获取，否则如果在之后发出 SELECT 语句，仍然存在一个潜在的竞争条件，即版本计数器可能在获取之前发生变化。

    当目标数据库支持 RETURNING 时，我们的 ``User`` 类的 INSERT 语句将如下所示：

    .. sourcecode:: sql

        INSERT INTO "user" (name) VALUES (%(name)s) RETURNING "user".id, "user".xmin
        -- {'name': 'ed'}

    在上面，ORM 可以在一个语句中获取任何新生成的主键值以及服务器生成的版本标识符。当后端不支持 RETURNING 时，必须为每个 INSERT 和 UPDATE 发出一个额外的 SELECT，这效率低得多，并且还引入了可能错过版本计数器的可能性：

    .. sourcecode:: sql

        INSERT INTO "user" (name) VALUES (%(name)s)
        -- {'name': 'ed'}

        SELECT "user".version_id AS user_version_id FROM "user" where
        "user".id = :param_1
        -- {"param_1": 1}

    *强烈建议* 仅在绝对必要时，并且仅在支持 :term:`RETURNING` 的后端使用服务器端版本计数器，目前支持的后端包括 PostgreSQL、Oracle Database、MariaDB 10.5、SQLite 3.35 和 SQL Server。

.. tab:: 英文

    The ``version_id_generator`` can also be configured to rely upon a value
    that is generated by the database.  In this case, the database would need
    some means of generating new identifiers when a row is subject to an INSERT
    as well as with an UPDATE.   For the UPDATE case, typically an update trigger
    is needed, unless the database in question supports some other native
    version identifier.  The PostgreSQL database in particular supports a system
    column called `xmin <https://www.postgresql.org/docs/current/static/ddl-system-columns.html>`_
    which provides UPDATE versioning.  We can make use
    of the PostgreSQL ``xmin`` column to version our ``User``
    class as follows::

        from sqlalchemy import FetchedValue


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50), nullable=False)
            xmin = mapped_column("xmin", String, system=True, server_default=FetchedValue())

            __mapper_args__ = {"version_id_col": xmin, "version_id_generator": False}

    With the above mapping, the ORM will rely upon the ``xmin`` column for
    automatically providing the new value of the version id counter.

    .. topic:: creating tables that refer to system columns

        In the above scenario, as ``xmin`` is a system column provided by PostgreSQL,
        we use the ``system=True`` argument to mark it as a system-provided
        column, omitted from the ``CREATE TABLE`` statement.   The datatype of this
        column is an internal PostgreSQL type called ``xid`` which acts mostly
        like a string, so we use the :class:`_types.String` datatype.


    The ORM typically does not actively fetch the values of database-generated
    values when it emits an INSERT or UPDATE, instead leaving these columns as
    "expired" and to be fetched when they are next accessed, unless the ``eager_defaults``
    :class:`_orm.Mapper` flag is set.  However, when a
    server side version column is used, the ORM needs to actively fetch the newly
    generated value.  This is so that the version counter is set up *before*
    any concurrent transaction may update it again.   This fetching is also
    best done simultaneously within the INSERT or UPDATE statement using :term:`RETURNING`,
    otherwise if emitting a SELECT statement afterwards, there is still a potential
    race condition where the version counter may change before it can be fetched.

    When the target database supports RETURNING, an INSERT statement for our ``User`` class will look
    like this:

    .. sourcecode:: sql

        INSERT INTO "user" (name) VALUES (%(name)s) RETURNING "user".id, "user".xmin
        -- {'name': 'ed'}

    Where above, the ORM can acquire any newly generated primary key values along
    with server-generated version identifiers in one statement.   When the backend
    does not support RETURNING, an additional SELECT must be emitted for **every**
    INSERT and UPDATE, which is much less efficient, and also introduces the possibility of
    missed version counters:

    .. sourcecode:: sql

        INSERT INTO "user" (name) VALUES (%(name)s)
        -- {'name': 'ed'}

        SELECT "user".version_id AS user_version_id FROM "user" where
        "user".id = :param_1
        -- {"param_1": 1}

    It is *strongly recommended* that server side version counters only be used
    when absolutely necessary and only on backends that support :term:`RETURNING`,
    currently PostgreSQL, Oracle Database, MariaDB 10.5, SQLite 3.35, and SQL
    Server.


编程或条件版本计数器
--------------------------------------------

Programmatic or Conditional Version Counters

.. tab:: 中文

    当 ``version_id_generator`` 设置为 False 时，我们也可以像分配其他映射属性一样以编程方式（和有条件地）设置对象上的版本标识符。例如，如果我们使用我们的 UUID 示例，但将 ``version_id_generator`` 设置为 ``False``，我们可以在选择时设置版本标识符::

        import uuid


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_uuid = mapped_column(String(32), nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {"version_id_col": version_uuid, "version_id_generator": False}


        u1 = User(name="u1", version_uuid=uuid.uuid4().hex)

        session.add(u1)

        session.commit()

        u1.name = "u2"
        u1.version_uuid = uuid.uuid4().hex

        session.commit()

    我们也可以在不增加版本计数器的情况下更新 ``User`` 对象；计数器的值将保持不变，UPDATE 语句仍将检查以前的值。这对于仅对某些类的 UPDATE 敏感于并发问题的方案可能很有用::

        # 将保持 version_uuid 不变
        u1.name = "u3"
        session.commit()

.. tab:: 英文

    When ``version_id_generator`` is set to False, we can also programmatically
    (and conditionally) set the version identifier on our object in the same way
    we assign any other mapped attribute.  Such as if we used our UUID example, but
    set ``version_id_generator`` to ``False``, we can set the version identifier
    at our choosing::

        import uuid


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            version_uuid = mapped_column(String(32), nullable=False)
            name = mapped_column(String(50), nullable=False)

            __mapper_args__ = {"version_id_col": version_uuid, "version_id_generator": False}


        u1 = User(name="u1", version_uuid=uuid.uuid4())

        session.add(u1)

        session.commit()

        u1.name = "u2"
        u1.version_uuid = uuid.uuid4()

        session.commit()

    We can update our ``User`` object without incrementing the version counter
    as well; the value of the counter will remain unchanged, and the UPDATE
    statement will still check against the previous value.  This may be useful
    for schemes where only certain classes of UPDATE are sensitive to concurrency
    issues::

        # will leave version_uuid unchanged
        u1.name = "u3"
        session.commit()
