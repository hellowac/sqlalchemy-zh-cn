特殊关系的持久化模式
=========================================

Special Relationship Persistence Patterns

.. tab:: 中文

.. tab:: 英文

.. _post_update:

指向自身的行/相互依赖的行
-------------------------------------------------------

Rows that point to themselves / Mutually Dependent Rows

.. tab:: 中文

    这是一个非常特殊的场景， ``relationship()`` 必须执行一次 ``INSERT`` 和第二次 ``UPDATE``，才能正确地填充一行（以及反过来执行一次 ``UPDATE`` 和 ``DELETE`` ，以避免违反外键约束）。出现这种需求的两种典型情况是：

    * 表中包含一个指向自身的外键，并且某一行的外键值正好指向自身的主键。
    * 两张表分别包含一个外键指向对方，每张表中各有一行互相引用。

    例如：
    
    .. sourcecode:: text
    
                  user
        ---------------------------------
        user_id    name   related_user_id
           1       'ed'          1
    
    或者：
    
    .. sourcecode:: text
    
                     widget                                                  entry
        -------------------------------------------             ---------------------------------
        widget_id     name        favorite_entry_id             entry_id      name      widget_id
           1       'somewidget'          5                         5       'someentry'     1

    在第一种情况下，一行数据指向它自己。从技术上讲，像 PostgreSQL 或 Oracle Database 这类使用序列（sequence）的数据库，可以使用预先生成的值一次性执行 INSERT 操作；但对于依赖自增主键（autoincrement-style primary key）的数据库，则无法做到这一点。:func:`~sqlalchemy.orm.relationship` 在执行 flush 操作时始终假设是“父/子”模型的数据填充方式，因此除非你直接手动填充主键/外键列，:func:`~sqlalchemy.orm.relationship` 就需要使用两条语句来完成插入。

    在第二种情况下，“widget” 行必须先于任何引用它的 “entry” 行插入，但此时 “widget” 行中的 “favorite_entry_id” 列还无法设置，必须等到 “entry” 行创建之后才能设置。因此，在这种情况下，通常无法仅使用两条 INSERT 语句就插入 “widget” 和 “entry” 行；必须执行一次 UPDATE 来满足外键约束。例外情况是外键被配置为“延迟到提交时生效”（deferred until commit，某些数据库支持该特性），并且标识符是手动填充的（这本质上绕过了 :func:`~sqlalchemy.orm.relationship` 的行为）。

    为启用额外的 UPDATE 语句，我们可以在 :func:`_orm.relationship` 中使用 :paramref:`_orm.relationship.post_update` 选项。该选项表示在两行数据都 INSERT 完成后，通过 UPDATE 语句建立它们之间的关联；同时也会在 DELETE 之前，通过 UPDATE 解关联这两行数据。这个标志应该仅设置在其中 *一个* relationship 上，优先设置在多对一（many-to-one）关系的那“一”侧。下面我们展示一个完整的例子，其中包括两个 :class:`_schema.ForeignKey` 构造：

    .. sourcecode:: python

        from sqlalchemy import Integer, ForeignKey, String
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship

        class Base(DeclarativeBase):
            pass

        class Entry(Base):
            __tablename__ = "entry"
            entry_id = mapped_column(Integer, primary_key=True)
            widget_id = mapped_column(Integer, ForeignKey("widget.widget_id"))
            name = mapped_column(String(50))

        class Widget(Base):
            __tablename__ = "widget"

            widget_id = mapped_column(Integer, primary_key=True)
            favorite_entry_id = mapped_column(
                Integer, ForeignKey("entry.entry_id", name="fk_favorite_entry")
            )
            name = mapped_column(String(50))

            entries = relationship(Entry, primaryjoin=widget_id == Entry.widget_id)
            favorite_entry = relationship(
                Entry, primaryjoin=favorite_entry_id == Entry.entry_id, post_update=True
            )

    当使用上述结构进行 `flush` 时，"widget" 行将被插入（但不包含 `favorite_entry_id` 值），然后所有的 "entry" 行会引用它进行插入，最后执行一次 `UPDATE` 更新 `favorite_entry_id` 列的值（当前是一行一行地执行）：

    .. sourcecode:: pycon+sql

        >>> w1 = Widget(name="somewidget")
        >>> e1 = Entry(name="someentry")
        >>> w1.favorite_entry = e1
        >>> w1.entries = [e1]
        >>> session.add_all([w1, e1])
        >>> session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO widget (favorite_entry_id, name) VALUES (?, ?)
        (None, 'somewidget')
        INSERT INTO entry (widget_id, name) VALUES (?, ?)
        (1, 'someentry')
        UPDATE widget SET favorite_entry_id=? WHERE widget.widget_id = ?
        (1, 1)
        COMMIT

    我们还可以添加一个额外配置，指定一个更全面的外键约束，确保 `favorite_entry_id` 总是指向一个归属当前 `Widget` 的 `Entry`。这可以通过 **复合外键** 实现：

    .. sourcecode:: python

        from sqlalchemy import (
            Integer,
            ForeignKey,
            String,
            UniqueConstraint,
            ForeignKeyConstraint,
        )
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship

        class Base(DeclarativeBase):
            pass

        class Entry(Base):
            __tablename__ = "entry"
            entry_id = mapped_column(Integer, primary_key=True)
            widget_id = mapped_column(Integer, ForeignKey("widget.widget_id"))
            name = mapped_column(String(50))
            __table_args__ = (UniqueConstraint("entry_id", "widget_id"),)

        class Widget(Base):
            __tablename__ = "widget"

            widget_id = mapped_column(Integer, autoincrement="ignore_fk", primary_key=True)
            favorite_entry_id = mapped_column(Integer)

            name = mapped_column(String(50))

            __table_args__ = (
                ForeignKeyConstraint(
                    ["widget_id", "favorite_entry_id"],
                    ["entry.widget_id", "entry.entry_id"],
                    name="fk_favorite_entry",
                ),
            )

            entries = relationship(
                Entry, primaryjoin=widget_id == Entry.widget_id, foreign_keys=Entry.widget_id
            )
            favorite_entry = relationship(
                Entry,
                primaryjoin=favorite_entry_id == Entry.entry_id,
                foreign_keys=favorite_entry_id,
                post_update=True,
            )

    上面的映射使用了一个复合 :class:`_schema.ForeignKeyConstraint` 来桥接 `widget_id` 和 `favorite_entry_id` 两列。为了确保 `Widget.widget_id` 仍然是一个“自增主键”，我们在 :class:`_schema.Column` 上设置 :paramref:`_schema.Column.autoincrement="ignore_fk"`，并在每个 :func:`_orm.relationship` 中手动限制哪些列参与外键连接。

.. tab:: 英文

    This is a very specific case where relationship() must perform an INSERT and a
    second UPDATE in order to properly populate a row (and vice versa an UPDATE
    and DELETE in order to delete without violating foreign key constraints). The
    two use cases are:
    
    * A table contains a foreign key to itself, and a single row will
      have a foreign key value pointing to its own primary key.
    * Two tables each contain a foreign key referencing the other
      table, with a row in each table referencing the other.
    
    For example:
    
    .. sourcecode:: text
    
                  user
        ---------------------------------
        user_id    name   related_user_id
           1       'ed'          1
    
    Or:
    
    .. sourcecode:: text
    
                     widget                                                  entry
        -------------------------------------------             ---------------------------------
        widget_id     name        favorite_entry_id             entry_id      name      widget_id
           1       'somewidget'          5                         5       'someentry'     1
    
    In the first case, a row points to itself. Technically, a database that uses sequences such as PostgreSQL or Oracle Database can INSERT the row at once using a previously generated value, but databases which rely upon autoincrement-style primary key identifiers cannot. The :func:`~sqlalchemy.orm.relationship` always assumes a "parent/child" model of row population during flush, so unless you are populating the primary key/foreign key columns directly, :func:`~sqlalchemy.orm.relationship` needs to use two statements.

    In the second case, the "widget" row must be inserted before any referring "entry" rows, but then the "favorite_entry_id" column of that "widget" row cannot be set until the "entry" rows have been generated. In this case, it's typically impossible to insert the "widget" and "entry" rows using just two INSERT statements; an UPDATE must be performed in order to keep foreign key constraints fulfilled. The exception is if the foreign keys are configured as "deferred until commit" (a feature some databases support) and if the identifiers were populated manually (again essentially bypassing :func:`~sqlalchemy.orm.relationship`).

    To enable the usage of a supplementary UPDATE statement, we use the :paramref:`_orm.relationship.post_update` option of :func:`_orm.relationship`.  This specifies that the linkage between the two rows should be created using an UPDATE statement after both rows have been INSERTED; it also causes the rows to be de-associated with each other via UPDATE before a DELETE is emitted.  The flag should be placed on just *one* of the relationships, preferably the many-to-one side.  Below we illustrate a complete example, including two :class:`_schema.ForeignKey` constructs::
    
        from sqlalchemy import Integer, ForeignKey
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class Entry(Base):
            __tablename__ = "entry"
            entry_id = mapped_column(Integer, primary_key=True)
            widget_id = mapped_column(Integer, ForeignKey("widget.widget_id"))
            name = mapped_column(String(50))
    
    
        class Widget(Base):
            __tablename__ = "widget"
    
            widget_id = mapped_column(Integer, primary_key=True)
            favorite_entry_id = mapped_column(
                Integer, ForeignKey("entry.entry_id", name="fk_favorite_entry")
            )
            name = mapped_column(String(50))
    
            entries = relationship(Entry, primaryjoin=widget_id == Entry.widget_id)
            favorite_entry = relationship(
                Entry, primaryjoin=favorite_entry_id == Entry.entry_id, post_update=True
            )
    
    When a structure against the above configuration is flushed, the "widget" row will be
    INSERTed minus the "favorite_entry_id" value, then all the "entry" rows will
    be INSERTed referencing the parent "widget" row, and then an UPDATE statement
    will populate the "favorite_entry_id" column of the "widget" table (it's one
    row at a time for the time being):
    
    .. sourcecode:: pycon+sql
    
        >>> w1 = Widget(name="somewidget")
        >>> e1 = Entry(name="someentry")
        >>> w1.favorite_entry = e1
        >>> w1.entries = [e1]
        >>> session.add_all([w1, e1])
        >>> session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO widget (favorite_entry_id, name) VALUES (?, ?)
        (None, 'somewidget')
        INSERT INTO entry (widget_id, name) VALUES (?, ?)
        (1, 'someentry')
        UPDATE widget SET favorite_entry_id=? WHERE widget.widget_id = ?
        (1, 1)
        COMMIT
    
    An additional configuration we can specify is to supply a more
    comprehensive foreign key constraint on ``Widget``, such that
    it's guaranteed that ``favorite_entry_id`` refers to an ``Entry``
    that also refers to this ``Widget``.  We can use a composite foreign key,
    as illustrated below::
    
        from sqlalchemy import (
            Integer,
            ForeignKey,
            String,
            UniqueConstraint,
            ForeignKeyConstraint,
        )
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class Entry(Base):
            __tablename__ = "entry"
            entry_id = mapped_column(Integer, primary_key=True)
            widget_id = mapped_column(Integer, ForeignKey("widget.widget_id"))
            name = mapped_column(String(50))
            __table_args__ = (UniqueConstraint("entry_id", "widget_id"),)
    
    
        class Widget(Base):
            __tablename__ = "widget"
    
            widget_id = mapped_column(Integer, autoincrement="ignore_fk", primary_key=True)
            favorite_entry_id = mapped_column(Integer)
    
            name = mapped_column(String(50))
    
            __table_args__ = (
                ForeignKeyConstraint(
                    ["widget_id", "favorite_entry_id"],
                    ["entry.widget_id", "entry.entry_id"],
                    name="fk_favorite_entry",
                ),
            )
    
            entries = relationship(
                Entry, primaryjoin=widget_id == Entry.widget_id, foreign_keys=Entry.widget_id
            )
            favorite_entry = relationship(
                Entry,
                primaryjoin=favorite_entry_id == Entry.entry_id,
                foreign_keys=favorite_entry_id,
                post_update=True,
            )
    
    The above mapping features a composite :class:`_schema.ForeignKeyConstraint`
    bridging the ``widget_id`` and ``favorite_entry_id`` columns.  To ensure
    that ``Widget.widget_id`` remains an "autoincrementing" column we specify
    :paramref:`_schema.Column.autoincrement` to the value ``"ignore_fk"``
    on :class:`_schema.Column`, and additionally on each
    :func:`_orm.relationship` we must limit those columns considered as part of
    the foreign key for the purposes of joining and cross-population.

.. _passive_updates:

可变主键/更新级联
--------------------------------------

Mutable Primary Keys / Update Cascades

.. tab:: 中文

    当实体的主键发生变化时，所有引用该主键的关联项也必须同时更新。对于强制执行引用完整性的数据库，最好的策略是使用数据库的 ON UPDATE CASCADE 功能，以便将主键的更改传播到被引用的外键中 —— 除非约束被标记为 "deferrable"（即延迟到事务完成时才强制执行），否则任何时刻这些值都不能处于不同步的状态。

    **强烈建议**：若应用程序希望使用可变的自然主键，应启用数据库的 ``ON UPDATE CASCADE`` 功能。下面是一个说明该用法的映射示例::

        class User(Base):
            __tablename__ = "user"
            __table_args__ = {"mysql_engine": "InnoDB"}

            username = mapped_column(String(50), primary_key=True)
            fullname = mapped_column(String(100))

            addresses = relationship("Address")


        class Address(Base):
            __tablename__ = "address"
            __table_args__ = {"mysql_engine": "InnoDB"}

            email = mapped_column(String(50), primary_key=True)
            username = mapped_column(
                String(50), ForeignKey("user.username", onupdate="cascade")
            )

    上述示例中，我们在 :class:`_schema.ForeignKey` 对象上使用了 ``onupdate="cascade"``，并指定了 ``mysql_engine='InnoDB'`` 设置。该设置确保在使用 MySQL 后端时，会启用支持引用完整性的 ``InnoDB`` 存储引擎。若使用 SQLite，应启用引用完整性支持，配置方法参见 :ref:`sqlite_foreign_keys`。

    .. seealso::

        :ref:`passive_deletes` - 支持关系中 ON DELETE CASCADE 的相关内容

        :paramref:`.orm.mapper.passive_updates` - :class:`_orm.Mapper` 上的类似功能


.. tab:: 英文

    When the primary key of an entity changes, related items
    which reference the primary key must also be updated as
    well. For databases which enforce referential integrity,
    the best strategy is to use the database's ON UPDATE CASCADE
    functionality in order to propagate primary key changes
    to referenced foreign keys - the values cannot be out
    of sync for any moment unless the constraints are marked as "deferrable",
    that is, not enforced until the transaction completes.

    It is **highly recommended** that an application which seeks to employ
    natural primary keys with mutable values to use the ``ON UPDATE CASCADE``
    capabilities of the database.   An example mapping which
    illustrates this is::

        class User(Base):
            __tablename__ = "user"
            __table_args__ = {"mysql_engine": "InnoDB"}

            username = mapped_column(String(50), primary_key=True)
            fullname = mapped_column(String(100))

            addresses = relationship("Address")


        class Address(Base):
            __tablename__ = "address"
            __table_args__ = {"mysql_engine": "InnoDB"}

            email = mapped_column(String(50), primary_key=True)
            username = mapped_column(
                String(50), ForeignKey("user.username", onupdate="cascade")
            )

    Above, we illustrate ``onupdate="cascade"`` on the :class:`_schema.ForeignKey`
    object, and we also illustrate the ``mysql_engine='InnoDB'`` setting
    which, on a MySQL backend, ensures that the ``InnoDB`` engine supporting
    referential integrity is used.  When using SQLite, referential integrity
    should be enabled, using the configuration described at
    :ref:`sqlite_foreign_keys`.

    .. seealso::

        :ref:`passive_deletes` - supporting ON DELETE CASCADE with relationships

        :paramref:`.orm.mapper.passive_updates` - similar feature on :class:`_orm.Mapper`


模拟有限的 ON UPDATE CASCADE 而不支持外键
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Simulating limited ON UPDATE CASCADE without foreign key support

.. tab:: 中文

    在使用 **不支持引用完整性** 的数据库，并且使用了可变值的自然主键的情况下，SQLAlchemy 提供了一项功能，可以在 **有限的范围内** 将主键值的更改传播到已引用该主键的外键列中。这一机制是通过对直接引用主键的外键列发出 UPDATE 语句来实现的。

    主要不支持引用完整性的数据库平台包括：

    - 使用 ``MyISAM`` 存储引擎的 MySQL；
    - 未启用 ``PRAGMA foreign_keys=ON`` 的 SQLite；
    - Oracle 数据库也不支持 ``ON UPDATE CASCADE``，但它仍然强制引用完整性，因此需要将约束设置为 deferrable，SQLAlchemy 才能发出 UPDATE 语句。

    要启用此功能，可以将 :paramref:`_orm.relationship.passive_updates` 标志设置为 ``False``，最好设置在一对多或多对多的 :func:`_orm.relationship` 上。当更新操作不再是“被动”的（passive）时，表示 SQLAlchemy 将为引用发生主键更改的父对象的集合中每个相关对象单独发出 UPDATE 语句。这也意味着，如果集合尚未在本地加载，SQLAlchemy 会强制将其完整加载到内存中。

    之前的映射示例，启用 ``passive_updates=False`` 后如下所示::

        class User(Base):
            __tablename__ = "user"

            username = mapped_column(String(50), primary_key=True)
            fullname = mapped_column(String(100))

            # passive_updates=False 仅在数据库未实现 ON UPDATE CASCADE 时才需要
            addresses = relationship("Address", passive_updates=False)


        class Address(Base):
            __tablename__ = "address"

            email = mapped_column(String(50), primary_key=True)
            username = mapped_column(String(50), ForeignKey("user.username"))

    ``passive_updates=False`` 的主要局限包括：

    * 相比于数据库自身的 ON UPDATE CASCADE 功能，该机制的性能更差。因为它必须使用 SELECT 完整预加载受影响的集合，并对其发出 UPDATE 语句 —— 虽然尝试以“批量”方式进行，但在 DBAPI 层仍然是逐行执行。

    * 此机制无法“级联”超过一层。例如，如果映射 X 的外键引用了映射 Y 的主键，而 Y 的主键又是对映射 Z 的外键，那么 ``passive_updates=False`` 无法将主键更改从 ``Z`` 级联传播到 ``X``。

    * 仅在关系的“多对一”一侧设置 ``passive_updates=False`` 并不能达到完整效果。因为单元工作（unit of work）只会在当前的标识映射（identity map）中查找引用主键发生变化的对象，而不会遍历整个数据库。

    由于除了 Oracle 以外，几乎所有数据库现在都支持 ``ON UPDATE CASCADE``，因此 **强烈建议**：在使用自然且可变主键值的情况下，应优先使用传统的 ``ON UPDATE CASCADE`` 支持。


.. tab:: 英文

    In those cases when a database that does not support referential integrity
    is used, and natural primary keys with mutable values are in play,
    SQLAlchemy offers a feature in order to allow propagation of primary key
    values to already-referenced foreign keys to a **limited** extent,
    by emitting an UPDATE statement against foreign key columns that immediately
    reference a primary key column whose value has changed.
    The primary platforms without referential integrity features are
    MySQL when the ``MyISAM`` storage engine is used, and SQLite when the
    ``PRAGMA foreign_keys=ON`` pragma is not used.  Oracle Database also
    has no support for ``ON UPDATE CASCADE``, but because it still enforces
    referential integrity, needs constraints to be marked as deferrable
    so that SQLAlchemy can emit UPDATE statements.
    
    The feature is enabled by setting the
    :paramref:`_orm.relationship.passive_updates` flag to ``False``,
    most preferably on a one-to-many or
    many-to-many :func:`_orm.relationship`.  When "updates" are no longer
    "passive" this indicates that SQLAlchemy will
    issue UPDATE statements individually for
    objects referenced in the collection referred to by the parent object
    with a changing primary key value.  This also implies that collections
    will be fully loaded into memory if not already locally present.
    
    Our previous mapping using ``passive_updates=False`` looks like::
    
        class User(Base):
            __tablename__ = "user"
    
            username = mapped_column(String(50), primary_key=True)
            fullname = mapped_column(String(100))
    
            # passive_updates=False *only* needed if the database
            # does not implement ON UPDATE CASCADE
            addresses = relationship("Address", passive_updates=False)
    
    
        class Address(Base):
            __tablename__ = "address"
    
            email = mapped_column(String(50), primary_key=True)
            username = mapped_column(String(50), ForeignKey("user.username"))
    
    Key limitations of ``passive_updates=False`` include:
    
    * it performs much more poorly than direct database ON UPDATE CASCADE,
      because it needs to fully pre-load affected collections using SELECT
      and also must emit  UPDATE statements against those values, which it
      will attempt to run  in "batches" but still runs on a per-row basis
      at the DBAPI level.
    
    * the feature cannot "cascade" more than one level.  That is,
      if mapping X has a foreign key which refers to the primary key
      of mapping Y, but then mapping Y's primary key is itself a foreign key
      to mapping Z, ``passive_updates=False`` cannot cascade a change in
      primary key value from ``Z`` to ``X``.
    
    * Configuring ``passive_updates=False`` only on the many-to-one
      side of a relationship will not have a full effect, as the
      unit of work searches only through the current identity
      map for objects that may be referencing the one with a
      mutating primary key, not throughout the database.
    
    As virtually all databases other than Oracle Database now support ``ON UPDATE
    CASCADE``, it is highly recommended that traditional ``ON UPDATE CASCADE``
    support be used in the case that natural and mutable primary key values are in
    use.
