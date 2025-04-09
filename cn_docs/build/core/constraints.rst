.. _metadata_constraints_toplevel:
.. _metadata_constraints:

.. currentmodule:: sqlalchemy.schema

================================
定义约束和索引
================================

Defining Constraints and Indexes

.. tab:: 中文

    本节将讨论SQL *约束* (:term:`constraints`) 和索引。在SQLAlchemy中，关键类包括 :class:`_schema.ForeignKeyConstraint` 和 :class:`.Index`。

.. tab:: 英文

    This section will discuss SQL :term:`constraints` and indexes.  In SQLAlchemy the key classes include :class:`_schema.ForeignKeyConstraint` and :class:`.Index`.

.. _metadata_foreignkeys:

定义外键
---------------------

Defining Foreign Keys

.. tab:: 中文

    在 SQL 中， *外键* 是一种表级结构，它限制该表中的一个或多个列，仅允许这些列的值出现在另一组列中，通常但不总是在另一个表中。我们称这些被限制的列为 *外键列*，而被它们所引用的列为 *被引用列*。被引用的列几乎总是其所属表的主键，但也有例外。外键是连接具有相互关系的行对的“关节”，SQLAlchemy 在其几乎所有操作中都赋予这一概念极高的重要性。

    在 SQLAlchemy 中，正如在 DDL 中一样，外键约束可以作为表定义中的附加属性来定义，也可以（在单列外键的情况下）选择在单个列的定义中指定。单列外键更为常见，并且可以在列级别通过构造 :class:`~sqlalchemy.schema.ForeignKey` 对象并将其作为 :class:`~sqlalchemy.schema.Column` 对象的参数来指定::

        user_preference = Table(
            "user_preference",
            metadata_obj,
            Column("pref_id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
            Column("pref_name", String(40), nullable=False),
            Column("pref_value", String(100)),
        )

    如上所示，我们定义了一个新表 ``user_preference``，其中每一行的 ``user_id`` 列的值必须存在于 ``user`` 表的 ``user_id`` 列中。

    传递给 :class:`~sqlalchemy.schema.ForeignKey` 的参数通常是形如 *<表名>.<列名>* 的字符串，对于位于远程 schema 或“拥有者”中的表，则使用形如 *<schema名>.<表名>.<列名>* 的格式。它也可以是一个实际的 :class:`~sqlalchemy.schema.Column` 对象，如下所示，它是从已有的 :class:`~sqlalchemy.schema.Table` 对象的 ``c`` 集合中获取的::

        ForeignKey(user.c.user_id)

    使用字符串的好处在于， ``user`` 和 ``user_preference`` 之间的 Python 内部链接仅在首次需要时才会解析，因此表对象可以轻松地分布在多个模块中，并按任意顺序定义。

    外键也可以在表级别使用 :class:`~sqlalchemy.schema.ForeignKeyConstraint` 对象来定义。该对象可以描述单列或多列的外键。多列外键称为 *复合外键*，几乎总是引用具有复合主键的表。下面我们定义一个具有复合主键的表 ``invoice``::

        invoice = Table(
            "invoice",
            metadata_obj,
            Column("invoice_id", Integer, primary_key=True),
            Column("ref_num", Integer, primary_key=True),
            Column("description", String(60), nullable=False),
        )

    然后是一个引用 ``invoice`` 的复合外键表 ``invoice_item``::

        invoice_item = Table(
            "invoice_item",
            metadata_obj,
            Column("item_id", Integer, primary_key=True),
            Column("item_name", String(60), nullable=False),
            Column("invoice_id", Integer, nullable=False),
            Column("ref_num", Integer, nullable=False),
            ForeignKeyConstraint(
                ["invoice_id", "ref_num"], ["invoice.invoice_id", "invoice.ref_num"]
            ),
        )

    需要注意的是，:class:`~sqlalchemy.schema.ForeignKeyConstraint` 是定义复合外键的唯一方式。尽管我们也可以分别在 ``invoice_item.invoice_id`` 和 ``invoice_item.ref_num`` 列上放置单个 :class:`~sqlalchemy.schema.ForeignKey` 对象，但 SQLAlchemy 不会意识到这两个值应该成对匹配——它会被视为两个独立的外键约束，而不是引用两个列的单个复合外键。


.. tab:: 英文

    A *foreign key* in SQL is a table-level construct that constrains one or more
    columns in that table to only allow values that are present in a different set
    of columns, typically but not always located on a different table. We call the
    columns which are constrained the *foreign key* columns and the columns which
    they are constrained towards the *referenced* columns. The referenced columns
    almost always define the primary key for their owning table, though there are
    exceptions to this. The foreign key is the "joint" that connects together
    pairs of rows which have a relationship with each other, and SQLAlchemy
    assigns very deep importance to this concept in virtually every area of its
    operation.

    In SQLAlchemy as well as in DDL, foreign key constraints can be defined as
    additional attributes within the table clause, or for single-column foreign
    keys they may optionally be specified within the definition of a single
    column. The single column foreign key is more common, and at the column level
    is specified by constructing a :class:`~sqlalchemy.schema.ForeignKey` object
    as an argument to a :class:`~sqlalchemy.schema.Column` object::

        user_preference = Table(
            "user_preference",
            metadata_obj,
            Column("pref_id", Integer, primary_key=True),
            Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
            Column("pref_name", String(40), nullable=False),
            Column("pref_value", String(100)),
        )

    Above, we define a new table ``user_preference`` for which each row must
    contain a value in the ``user_id`` column that also exists in the ``user``
    table's ``user_id`` column.

    The argument to :class:`~sqlalchemy.schema.ForeignKey` is most commonly a
    string of the form *<tablename>.<columnname>*, or for a table in a remote
    schema or "owner" of the form *<schemaname>.<tablename>.<columnname>*. It may
    also be an actual :class:`~sqlalchemy.schema.Column` object, which as we'll
    see later is accessed from an existing :class:`~sqlalchemy.schema.Table`
    object via its ``c`` collection::

        ForeignKey(user.c.user_id)

    The advantage to using a string is that the in-python linkage between ``user``
    and ``user_preference`` is resolved only when first needed, so that table
    objects can be easily spread across multiple modules and defined in any order.

    Foreign keys may also be defined at the table level, using the
    :class:`~sqlalchemy.schema.ForeignKeyConstraint` object. This object can
    describe a single- or multi-column foreign key. A multi-column foreign key is
    known as a *composite* foreign key, and almost always references a table that
    has a composite primary key. Below we define a table ``invoice`` which has a
    composite primary key::

        invoice = Table(
            "invoice",
            metadata_obj,
            Column("invoice_id", Integer, primary_key=True),
            Column("ref_num", Integer, primary_key=True),
            Column("description", String(60), nullable=False),
        )

    And then a table ``invoice_item`` with a composite foreign key referencing
    ``invoice``::

        invoice_item = Table(
            "invoice_item",
            metadata_obj,
            Column("item_id", Integer, primary_key=True),
            Column("item_name", String(60), nullable=False),
            Column("invoice_id", Integer, nullable=False),
            Column("ref_num", Integer, nullable=False),
            ForeignKeyConstraint(
                ["invoice_id", "ref_num"], ["invoice.invoice_id", "invoice.ref_num"]
            ),
        )

    It's important to note that the
    :class:`~sqlalchemy.schema.ForeignKeyConstraint` is the only way to define a
    composite foreign key. While we could also have placed individual
    :class:`~sqlalchemy.schema.ForeignKey` objects on both the
    ``invoice_item.invoice_id`` and ``invoice_item.ref_num`` columns, SQLAlchemy
    would not be aware that these two values should be paired together - it would
    be two individual foreign key constraints instead of a single composite
    foreign key referencing two columns.

.. _use_alter:

通过 ALTER 创建/删除外键约束
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating/Dropping Foreign Key Constraints via ALTER

.. tab:: 中文

    我们在教程和其他地方看到的外键与 DDL 的行为表明，约束通常以内联方式呈现在 CREATE TABLE 语句中，例如：

    .. sourcecode:: sql

        CREATE TABLE addresses (
            id INTEGER NOT NULL,
            user_id INTEGER,
            email_address VARCHAR NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT user_id_fk FOREIGN KEY(user_id) REFERENCES users (id)
        )

    ``CONSTRAINT .. FOREIGN KEY`` 指令用于在 CREATE TABLE 定义中以内联方式创建约束。
    :meth:`_schema.MetaData.create_all` 和 :meth:`_schema.MetaData.drop_all` 方法默认采用这种方式，它们会对涉及的所有 :class:`_schema.Table` 对象进行拓扑排序，以按照外键依赖关系的顺序创建和删除表（该排序也可通过 :attr:`_schema.MetaData.sorted_tables` 访问器获得）。

    当涉及两个或多个外键约束且存在“依赖循环”时，这种方式将不起作用，即一组表互相依赖，前提是后端强制执行外键（除 SQLite 和 MySQL/MyISAM 外，其他数据库均是如此）。因此这些方法会将此类循环中的约束拆分为单独的 ALTER 语句，在除 SQLite 以外的所有后端中执行，因为 SQLite 不支持大多数 ALTER 形式。如下所示：

    ::

        node = Table(
            "node",
            metadata_obj,
            Column("node_id", Integer, primary_key=True),
            Column("primary_element", Integer, ForeignKey("element.element_id")),
        )

        element = Table(
            "element",
            metadata_obj,
            Column("element_id", Integer, primary_key=True),
            Column("parent_node_id", Integer),
            ForeignKeyConstraint(
                ["parent_node_id"], ["node.node_id"], name="fk_element_parent_node_id"
            ),
        )

    当我们在 PostgreSQL 后端上调用 :meth:`_schema.MetaData.create_all` 时，
    两个表之间的循环将被解析，约束将被单独创建：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.create_all(conn, checkfirst=False)
        {execsql}CREATE TABLE element (
            element_id SERIAL NOT NULL,
            parent_node_id INTEGER,
            PRIMARY KEY (element_id)
        )

        CREATE TABLE node (
            node_id SERIAL NOT NULL,
            primary_element INTEGER,
            PRIMARY KEY (node_id)
        )

        ALTER TABLE element ADD CONSTRAINT fk_element_parent_node_id
            FOREIGN KEY(parent_node_id) REFERENCES node (node_id)
        ALTER TABLE node ADD FOREIGN KEY(primary_element)
            REFERENCES element (element_id)
        {stop}

    当执行 DROP 操作时也会应用相同的逻辑，不过要注意，在 SQL 中执行 DROP CONSTRAINT 需要该约束具有名称。就上面的 ``'node'`` 表而言，我们并未为该约束命名，因此系统将尝试仅对具名约束执行 DROP：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.drop_all(conn, checkfirst=False)
        {execsql}ALTER TABLE element DROP CONSTRAINT fk_element_parent_node_id
        DROP TABLE node
        DROP TABLE element
        {stop}

    如果循环无法被解析，比如在我们没有为任一约束命名的情况下，则会收到如下错误：

    .. sourcecode:: text

        sqlalchemy.exc.CircularDependencyError: Can't sort tables for DROP;
        an unresolvable foreign key dependency exists between tables:
        element, node.  Please ensure that the ForeignKey and ForeignKeyConstraint
        objects involved in the cycle have names so that they can be dropped
        using DROP CONSTRAINT.

    这个错误只适用于 DROP 情况，因为在 CREATE 情况下可以不指定名称而发出 “ADD CONSTRAINT”；数据库通常会自动分配一个名称。

    :paramref:`_schema.ForeignKeyConstraint.use_alter` 和 :paramref:`_schema.ForeignKey.use_alter` 关键字参数可用于手动解析依赖循环。我们可以只在 ``'element'`` 表中添加该标志，如下所示::

        element = Table(
            "element",
            metadata_obj,
            Column("element_id", Integer, primary_key=True),
            Column("parent_node_id", Integer),
            ForeignKeyConstraint(
                ["parent_node_id"],
                ["node.node_id"],
                use_alter=True,
                name="fk_element_parent_node_id",
            ),
        )

    在我们的 CREATE DDL 中，我们将仅看到此约束的 ALTER 语句，而不是另一个约束：

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.create_all(conn, checkfirst=False)
        {execsql}CREATE TABLE element (
            element_id SERIAL NOT NULL,
            parent_node_id INTEGER,
            PRIMARY KEY (element_id)
        )

        CREATE TABLE node (
            node_id SERIAL NOT NULL,
            primary_element INTEGER,
            PRIMARY KEY (node_id),
            FOREIGN KEY(primary_element) REFERENCES element (element_id)
        )

        ALTER TABLE element ADD CONSTRAINT fk_element_parent_node_id
        FOREIGN KEY(parent_node_id) REFERENCES node (node_id)
        {stop}

    :paramref:`_schema.ForeignKeyConstraint.use_alter` 和 :paramref:`_schema.ForeignKey.use_alter` 与 DROP 操作结合使用时，约束必须具名，否则会引发如下错误：

    .. sourcecode:: text

        sqlalchemy.exc.CompileError: Can't emit DROP CONSTRAINT for constraint
        ForeignKeyConstraint(...); it has no name

    .. seealso::

        :ref:`constraint_naming_conventions`

        :func:`.sort_tables_and_constraints`

.. tab:: 英文

    The behavior we've seen in tutorials and elsewhere involving
    foreign keys with DDL illustrates that the constraints are typically
    rendered "inline" within the CREATE TABLE statement, such as:

    .. sourcecode:: sql

        CREATE TABLE addresses (
            id INTEGER NOT NULL,
            user_id INTEGER,
            email_address VARCHAR NOT NULL,
            PRIMARY KEY (id),
            CONSTRAINT user_id_fk FOREIGN KEY(user_id) REFERENCES users (id)
        )

    The ``CONSTRAINT .. FOREIGN KEY`` directive is used to create the constraint
    in an "inline" fashion within the CREATE TABLE definition.   The
    :meth:`_schema.MetaData.create_all` and :meth:`_schema.MetaData.drop_all` methods do
    this by default, using a topological sort of all the :class:`_schema.Table` objects
    involved such that tables are created and dropped in order of their foreign
    key dependency (this sort is also available via the
    :attr:`_schema.MetaData.sorted_tables` accessor).

    This approach can't work when two or more foreign key constraints are
    involved in a "dependency cycle", where a set of tables
    are mutually dependent on each other, assuming the backend enforces foreign
    keys (always the case except on SQLite, MySQL/MyISAM).   The methods will
    therefore break out constraints in such a cycle into separate ALTER
    statements, on all backends other than SQLite which does not support
    most forms of ALTER.  Given a schema like::

        node = Table(
            "node",
            metadata_obj,
            Column("node_id", Integer, primary_key=True),
            Column("primary_element", Integer, ForeignKey("element.element_id")),
        )

        element = Table(
            "element",
            metadata_obj,
            Column("element_id", Integer, primary_key=True),
            Column("parent_node_id", Integer),
            ForeignKeyConstraint(
                ["parent_node_id"], ["node.node_id"], name="fk_element_parent_node_id"
            ),
        )

    When we call upon :meth:`_schema.MetaData.create_all` on a backend such as the
    PostgreSQL backend, the cycle between these two tables is resolved and the
    constraints are created separately:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.create_all(conn, checkfirst=False)
        {execsql}CREATE TABLE element (
            element_id SERIAL NOT NULL,
            parent_node_id INTEGER,
            PRIMARY KEY (element_id)
        )

        CREATE TABLE node (
            node_id SERIAL NOT NULL,
            primary_element INTEGER,
            PRIMARY KEY (node_id)
        )

        ALTER TABLE element ADD CONSTRAINT fk_element_parent_node_id
            FOREIGN KEY(parent_node_id) REFERENCES node (node_id)
        ALTER TABLE node ADD FOREIGN KEY(primary_element)
            REFERENCES element (element_id)
        {stop}

    In order to emit DROP for these tables, the same logic applies, however
    note here that in SQL, to emit DROP CONSTRAINT requires that the constraint
    has a name.  In the case of the ``'node'`` table above, we haven't named
    this constraint; the system will therefore attempt to emit DROP for only
    those constraints that are named:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.drop_all(conn, checkfirst=False)
        {execsql}ALTER TABLE element DROP CONSTRAINT fk_element_parent_node_id
        DROP TABLE node
        DROP TABLE element
        {stop}


    In the case where the cycle cannot be resolved, such as if we hadn't applied
    a name to either constraint here, we will receive the following error:

    .. sourcecode:: text

        sqlalchemy.exc.CircularDependencyError: Can't sort tables for DROP;
        an unresolvable foreign key dependency exists between tables:
        element, node.  Please ensure that the ForeignKey and ForeignKeyConstraint
        objects involved in the cycle have names so that they can be dropped
        using DROP CONSTRAINT.

    This error only applies to the DROP case as we can emit "ADD CONSTRAINT"
    in the CREATE case without a name; the database typically assigns one
    automatically.

    The :paramref:`_schema.ForeignKeyConstraint.use_alter` and
    :paramref:`_schema.ForeignKey.use_alter` keyword arguments can be used
    to manually resolve dependency cycles.  We can add this flag only to
    the ``'element'`` table as follows::

        element = Table(
            "element",
            metadata_obj,
            Column("element_id", Integer, primary_key=True),
            Column("parent_node_id", Integer),
            ForeignKeyConstraint(
                ["parent_node_id"],
                ["node.node_id"],
                use_alter=True,
                name="fk_element_parent_node_id",
            ),
        )

    in our CREATE DDL we will see the ALTER statement only for this constraint,
    and not the other one:

    .. sourcecode:: pycon+sql

        >>> with engine.connect() as conn:
        ...     metadata_obj.create_all(conn, checkfirst=False)
        {execsql}CREATE TABLE element (
            element_id SERIAL NOT NULL,
            parent_node_id INTEGER,
            PRIMARY KEY (element_id)
        )

        CREATE TABLE node (
            node_id SERIAL NOT NULL,
            primary_element INTEGER,
            PRIMARY KEY (node_id),
            FOREIGN KEY(primary_element) REFERENCES element (element_id)
        )

        ALTER TABLE element ADD CONSTRAINT fk_element_parent_node_id
        FOREIGN KEY(parent_node_id) REFERENCES node (node_id)
        {stop}

    :paramref:`_schema.ForeignKeyConstraint.use_alter` and
    :paramref:`_schema.ForeignKey.use_alter`, when used in conjunction with a drop
    operation, will require that the constraint is named, else an error
    like the following is generated:

    .. sourcecode:: text

        sqlalchemy.exc.CompileError: Can't emit DROP CONSTRAINT for constraint
        ForeignKeyConstraint(...); it has no name

    .. seealso::

        :ref:`constraint_naming_conventions`

        :func:`.sort_tables_and_constraints`

.. _on_update_on_delete:

ON UPDATE 和 ON DELETE
~~~~~~~~~~~~~~~~~~~~~~~

ON UPDATE and ON DELETE

.. tab:: 中文
    
    大多数数据库支持外键值的 *级联* 操作，也就是说，当父行被更新时，新的值会传递到子行中；或者当父行被删除时，所有对应的子行会被设为 null 或一并删除。
    在数据定义语言（DDL）中，这类行为通过像 "ON UPDATE CASCADE"、"ON DELETE CASCADE" 和 "ON DELETE SET NULL" 这样的短语来指定，对应于外键约束。"ON UPDATE" 或 "ON DELETE" 后的短语也可能因所用数据库的不同而有所变化。
    :class:`~sqlalchemy.schema.ForeignKey` 和 :class:`~sqlalchemy.schema.ForeignKeyConstraint` 对象支持通过 ``onupdate`` 和 ``ondelete`` 关键字参数生成这些子句。其值是任意字符串，会被输出在相应的 "ON UPDATE" 或 "ON DELETE" 短语之后::

        child = Table(
            "child",
            metadata_obj,
            Column(
                "id",
                Integer,
                ForeignKey("parent.id", onupdate="CASCADE", ondelete="CASCADE"),
                primary_key=True,
            ),
        )

        composite = Table(
            "composite",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("rev_id", Integer),
            Column("note_id", Integer),
            ForeignKeyConstraint(
                ["rev_id", "note_id"],
                ["revisions.id", "revisions.note_id"],
                onupdate="CASCADE",
                ondelete="SET NULL",
            ),
        )

    请注意，一些数据库后端在级联操作上有特殊要求：

    * MySQL / MariaDB - 应使用 ``InnoDB`` 存储引擎（在现代数据库中通常是默认选项）
    * SQLite - 默认情况下不启用外键约束。   参考 :ref:`sqlite_foreign_keys`

    .. seealso::

        有关将 ``ON DELETE CASCADE`` 与 ORM :func:`_orm.relationship` 构造集成的背景知识，请参见以下章节：

        :ref:`passive_deletes`

        :ref:`passive_deletes_many_to_many`

        :ref:`postgresql_constraint_options` - 指出外键级联操作可用的其他选项，如列列表

        :ref:`sqlite_foreign_keys` - 启用 SQLite 外键支持的背景知识


.. tab:: 英文

    Most databases support *cascading* of foreign key values, that is the when a
    parent row is updated the new value is placed in child rows, or when the
    parent row is deleted all corresponding child rows are set to null or deleted.
    In data definition language these are specified using phrases like "ON UPDATE
    CASCADE", "ON DELETE CASCADE", and "ON DELETE SET NULL", corresponding to
    foreign key constraints. The phrase after "ON UPDATE" or "ON DELETE" may also
    allow other phrases that are specific to the database in use. The
    :class:`~sqlalchemy.schema.ForeignKey` and
    :class:`~sqlalchemy.schema.ForeignKeyConstraint` objects support the
    generation of this clause via the ``onupdate`` and ``ondelete`` keyword
    arguments. The value is any string which will be output after the appropriate
    "ON UPDATE" or "ON DELETE" phrase::
    
        child = Table(
            "child",
            metadata_obj,
            Column(
                "id",
                Integer,
                ForeignKey("parent.id", onupdate="CASCADE", ondelete="CASCADE"),
                primary_key=True,
            ),
        )
    
        composite = Table(
            "composite",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("rev_id", Integer),
            Column("note_id", Integer),
            ForeignKeyConstraint(
                ["rev_id", "note_id"],
                ["revisions.id", "revisions.note_id"],
                onupdate="CASCADE",
                ondelete="SET NULL",
            ),
        )
    
    Note that some backends have special requirements for cascades to function:
    
    * MySQL / MariaDB - the ``InnoDB`` storage engine should be used (this is
      typically the default in modern databases)
    * SQLite - constraints are not enabled by default.
      See :ref:`sqlite_foreign_keys`
    
    .. seealso::
    
        For background on integration of ``ON DELETE CASCADE`` with
        ORM :func:`_orm.relationship` constructs, see the following sections:
    
        :ref:`passive_deletes`
    
        :ref:`passive_deletes_many_to_many`
    
        :ref:`postgresql_constraint_options` - indicates additional options
        available for foreign key cascades such as column lists
    
        :ref:`sqlite_foreign_keys` - background on enabling foreign key support
        with SQLite

.. _schema_unique_constraint:

UNIQUE 约束
-----------------

UNIQUE Constraint

.. tab:: 中文

    唯一约束（Unique Constraint）可以通过在 :class:`~sqlalchemy.schema.Column` 上使用 ``unique`` 关键字以匿名方式创建单列表唯一约束。
    带有显式名称的唯一约束和/或多列表唯一约束通过 :class:`~sqlalchemy.schema.UniqueConstraint` 表级构造来创建。

    .. sourcecode:: python+sql

        from sqlalchemy import UniqueConstraint

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # 每列匿名唯一约束
            Column("col1", Integer, unique=True),
            Column("col2", Integer),
            Column("col3", Integer),
            # 显式/复合唯一约束。'name' 是可选项。
            UniqueConstraint("col2", "col3", name="uix_1"),
        )

.. tab:: 英文

    Unique constraints can be created anonymously on a single column using the
    ``unique`` keyword on :class:`~sqlalchemy.schema.Column`. Explicitly named
    unique constraints and/or those with multiple columns are created via the
    :class:`~sqlalchemy.schema.UniqueConstraint` table-level construct.

    .. sourcecode:: python+sql

        from sqlalchemy import UniqueConstraint

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # per-column anonymous unique constraint
            Column("col1", Integer, unique=True),
            Column("col2", Integer),
            Column("col3", Integer),
            # explicit/composite unique constraint.  'name' is optional.
            UniqueConstraint("col2", "col3", name="uix_1"),
        )

CHECK 约束
----------------

CHECK Constraint

.. tab:: 中文

    检查约束（Check Constraint）可以具名或匿名，并可以在列级或表级使用 :class:`~sqlalchemy.schema.CheckConstraint` 构造进行创建。
    检查约束的文本会直接传递给数据库，因此其“数据库无关性”是有限的。列级检查约束通常只应引用所在的那一列，而表级约束可以引用表中的任意列。

    请注意，一些数据库（如 MySQL 8.0.16 之前的版本）并不真正支持检查约束。

    .. sourcecode:: python+sql

        from sqlalchemy import CheckConstraint

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # 每列 CHECK 约束
            Column("col1", Integer, CheckConstraint("col1>5")),
            Column("col2", Integer),
            Column("col3", Integer),
            # 表级 CHECK 约束。'name' 是可选项。
            CheckConstraint("col2 > col3 + 5", name="check1"),
        )

        mytable.create(engine)
        {execsql}CREATE TABLE mytable (
            col1 INTEGER  CHECK (col1>5),
            col2 INTEGER,
            col3 INTEGER,
            CONSTRAINT check1  CHECK (col2 > col3 + 5)
        ){stop}

.. tab:: 英文

    Check constraints can be named or unnamed and can be created at the Column or
    Table level, using the :class:`~sqlalchemy.schema.CheckConstraint` construct.
    The text of the check constraint is passed directly through to the database,
    so there is limited "database independent" behavior. Column level check
    constraints generally should only refer to the column to which they are
    placed, while table level constraints can refer to any columns in the table.

    Note that some databases do not actively support check constraints such as
    older versions of MySQL (prior to 8.0.16).

    .. sourcecode:: python+sql

        from sqlalchemy import CheckConstraint

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # per-column CHECK constraint
            Column("col1", Integer, CheckConstraint("col1>5")),
            Column("col2", Integer),
            Column("col3", Integer),
            # table level CHECK constraint.  'name' is optional.
            CheckConstraint("col2 > col3 + 5", name="check1"),
        )

        mytable.create(engine)
        {execsql}CREATE TABLE mytable (
            col1 INTEGER  CHECK (col1>5),
            col2 INTEGER,
            col3 INTEGER,
            CONSTRAINT check1  CHECK (col2 > col3 + 5)
        ){stop}

PRIMARY KEY 约束
----------------------

PRIMARY KEY Constraint

.. tab:: 中文

    任何 :class:`_schema.Table` 对象的主键约束是隐式存在的，基于那些设置了 :paramref:`_schema.Column.primary_key` 标志的 :class:`_schema.Column` 对象。
    :class:`.PrimaryKeyConstraint` 对象提供了对该约束的显式访问方式，并允许直接进行配置::

        from sqlalchemy import PrimaryKeyConstraint

        my_table = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer),
            Column("version_id", Integer),
            Column("data", String(50)),
            PrimaryKeyConstraint("id", "version_id", name="mytable_pk"),
        )

    .. seealso::

        :class:`.PrimaryKeyConstraint` - 详细的 API 文档。

.. tab:: 英文

    The primary key constraint of any :class:`_schema.Table` object is implicitly
    present, based on the :class:`_schema.Column` objects that are marked with the
    :paramref:`_schema.Column.primary_key` flag.   The :class:`.PrimaryKeyConstraint`
    object provides explicit access to this constraint, which includes the
    option of being configured directly::

        from sqlalchemy import PrimaryKeyConstraint

        my_table = Table(
            "mytable",
            metadata_obj,
            Column("id", Integer),
            Column("version_id", Integer),
            Column("data", String(50)),
            PrimaryKeyConstraint("id", "version_id", name="mytable_pk"),
        )

    .. seealso::

        :class:`.PrimaryKeyConstraint` - detailed API documentation.

使用声明性 ORM 扩展时设置约束
---------------------------------------------------------------

Setting up Constraints when using the Declarative ORM Extension

.. tab:: 中文

    :class:`_schema.Table` 是 SQLAlchemy Core 中用于定义表元数据的构造，这些元数据除了其他用途外，还可作为 SQLAlchemy ORM 中类映射的目标。:ref:`Declarative <declarative_toplevel>` 扩展允许根据一组 :class:`_schema.Column` 对象的映射自动创建 :class:`_schema.Table` 对象。

    若要将诸如 :class:`_schema.ForeignKeyConstraint` 这样的表级约束对象应用于通过 Declarative 定义的表，可以使用 ``__table_args__`` 属性，详见 :ref:`declarative_table_args`。

.. tab:: 英文

    The :class:`_schema.Table` is the SQLAlchemy Core construct that allows one to define
    table metadata, which among other things can be used by the SQLAlchemy ORM
    as a target to map a class.  The :ref:`Declarative <declarative_toplevel>`
    extension allows the :class:`_schema.Table` object to be created automatically, given
    the contents of the table primarily as a mapping of :class:`_schema.Column` objects.

    To apply table-level constraint objects such as :class:`_schema.ForeignKeyConstraint`
    to a table defined using Declarative, use the ``__table_args__`` attribute,
    described at :ref:`declarative_table_args`.

.. _constraint_naming_conventions:

配置约束命名约定
-----------------------------------------

Configuring Constraint Naming Conventions

.. tab:: 中文

    关系型数据库通常为所有约束和索引分配显式名称。在常见情况下，使用 ``CREATE TABLE`` 创建表时，CHECK、UNIQUE 和 PRIMARY KEY 等约束是在表定义中内联产生的，如果没有指定名称，数据库系统通常会自动为这些约束分配名称。而当使用诸如 ``ALTER TABLE`` 这样的命令修改已有数据库表时，该命令通常需要为新添加的约束显式指定名称，并且能够指定要删除或修改的现有约束的名称。

    可以使用 :paramref:`.Constraint.name` 参数显式地为约束命名，索引使用 :paramref:`.Index.name` 参数。对于约束来说，该参数是可选的。也可以通过 :paramref:`_schema.Column.unique` 和 :paramref:`_schema.Column.index` 参数使用不带显式名称的方式创建 :class:`.UniqueConstraint` 和 :class:`.Index` 对象。

    对已有表和约束进行修改的用例可通过如 `Alembic <https://alembic.sqlalchemy.org/>`_ 等模式迁移工具来处理。然而，Alembic 和 SQLAlchemy 当前都不会为未指定名称的约束对象自动生成名称，因此若要修改现有约束，就需要反向工程分析数据库用于自动命名约束的机制，或是在一开始就小心地为所有约束指定名称。

    与为所有 :class:`.Constraint` 和 :class:`.Index` 对象显式命名的方式相对，使用事件机制可以构建自动命名方案。这种方法的优点是，可以无需在代码中到处指定名称参数，也能为所有约束和索引提供一致的命名方案；而且这种机制同样适用于通过 :paramref:`_schema.Column.unique` 和 :paramref:`_schema.Column.index` 参数产生的约束和索引。从 SQLAlchemy 0.9.2 起，基于事件的此类命名方案已被包含，并可通过 :paramref:`_schema.MetaData.naming_convention` 参数进行配置。


.. tab:: 英文

    Relational databases typically assign explicit names to all constraints and
    indexes.  In the common case that a table is created using ``CREATE TABLE``
    where constraints such as CHECK, UNIQUE, and PRIMARY KEY constraints are
    produced inline with the table definition, the database usually has a system
    in place in which names are automatically assigned to these constraints, if
    a name is not otherwise specified.  When an existing database table is altered
    in a database using a command such as ``ALTER TABLE``, this command typically
    needs to specify explicit names for new constraints as well as be able to
    specify the name of an existing constraint that is to be dropped or modified.

    Constraints can be named explicitly using the :paramref:`.Constraint.name` parameter,
    and for indexes the :paramref:`.Index.name` parameter.  However, in the
    case of constraints this parameter is optional.  There are also the use
    cases of using the :paramref:`_schema.Column.unique` and :paramref:`_schema.Column.index`
    parameters which create :class:`.UniqueConstraint` and :class:`.Index` objects
    without an explicit name being specified.

    The use case of alteration of existing tables and constraints can be handled
    by schema migration tools such as `Alembic <https://alembic.sqlalchemy.org/>`_.
    However, neither Alembic nor SQLAlchemy currently create names for constraint
    objects where the name is otherwise unspecified, leading to the case where
    being able to alter existing constraints means that one must reverse-engineer
    the naming system used by the relational database to auto-assign names,
    or that care must be taken to ensure that all constraints are named.

    In contrast to having to assign explicit names to all :class:`.Constraint`
    and :class:`.Index` objects, automated naming schemes can be constructed
    using events.  This approach has the advantage that constraints will get
    a consistent naming scheme without the need for explicit name parameters
    throughout the code, and also that the convention takes place just as well
    for those constraints and indexes produced by the :paramref:`_schema.Column.unique`
    and :paramref:`_schema.Column.index` parameters.  As of SQLAlchemy 0.9.2 this
    event-based approach is included, and can be configured using the argument
    :paramref:`_schema.MetaData.naming_convention`.

为元数据集合配置命名约定
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring a Naming Convention for a MetaData Collection

.. tab:: 中文

    :paramref:`_schema.MetaData.naming_convention` 是一个字典，其键可以是 :class:`.Index` 类或各个 :class:`.Constraint` 类，也可以是一些字符串代码，如 ``"fk"``、 ``"pk"``、 ``"ix"``、 ``"ck"``、 ``"uq"`` ，分别代表外键、主键、索引、检查和唯一约束。字典中的字符串模板将在约束或索引与该 :class:`_schema.MetaData` 对象关联且未指定名称时使用（包括一个可以进一步装饰已有名称的例外情况）。

    一个适用于基本场景的命名方案示例如下::

        convention = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }

        metadata_obj = MetaData(naming_convention=convention)

    上述命名方案将为目标 :class:`_schema.MetaData` 集合中的所有约束生成名称。
    例如，当我们创建一个未命名的 :class:`.UniqueConstraint` 时，可以看到自动生成的名称::

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30), nullable=False),
        ...     UniqueConstraint("name"),
        ... )
        >>> list(user_table.constraints)[1].name
        'uq_user_name'

    即使我们只是使用 :paramref:`_schema.Column.unique` 标志，该功能也会生效::

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30), nullable=False, unique=True),
        ... )
        >>> list(user_table.constraints)[1].name
        'uq_user_name'

    命名方案方法的一个关键优势在于：名称是在 Python 构建对象时生成的，而不是在发出 DDL 时。这对于使用 Alembic 的 ``--autogenerate`` 功能尤为重要，因为生成的新迁移脚本中将会包含显式的命名::

        def upgrade():
            op.create_unique_constraint("uq_user_name", "user", ["name"])

    上述 ``"uq_user_name"`` 字符串即是从 ``--autogenerate`` 在元数据中定位到的 :class:`.UniqueConstraint` 对象中获取的。

    可用的模板变量包括 ``%(table_name)s``、 ``%(referred_table_name)s``、 ``%(column_0_name)s``、 ``%(column_0_label)s``、 ``%(column_0_key)s``、 ``%(referred_column_0_name)s`` 和 ``%(constraint_name)s``，还包括它们的多列版本，如 ``%(column_0N_name)s``、 ``%(column_0_N_name)s``、 ``%(referred_column_0_N_name)s``，这些变量会以带或不带下划线的方式连接所有列名。
    :paramref:`_schema.MetaData.naming_convention` 的文档中提供了对每个模板变量的更多细节说明。


.. tab:: 英文

    :paramref:`_schema.MetaData.naming_convention` refers to a dictionary which accepts
    the :class:`.Index` class or individual :class:`.Constraint` classes as keys,
    and Python string templates as values.   It also accepts a series of
    string-codes as alternative keys, ``"fk"``, ``"pk"``,
    ``"ix"``, ``"ck"``, ``"uq"`` for foreign key, primary key, index,
    check, and unique constraint, respectively.  The string templates in this
    dictionary are used whenever a constraint or index is associated with this
    :class:`_schema.MetaData` object that does not have an existing name given (including
    one exception case where an existing name can be further embellished).

    An example naming convention that suits basic cases is as follows::

        convention = {
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }

        metadata_obj = MetaData(naming_convention=convention)

    The above convention will establish names for all constraints within
    the target :class:`_schema.MetaData` collection.
    For example, we can observe the name produced when we create an unnamed
    :class:`.UniqueConstraint`::

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30), nullable=False),
        ...     UniqueConstraint("name"),
        ... )
        >>> list(user_table.constraints)[1].name
        'uq_user_name'

    This same feature takes effect even if we just use the :paramref:`_schema.Column.unique`
    flag::

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("name", String(30), nullable=False, unique=True),
        ... )
        >>> list(user_table.constraints)[1].name
        'uq_user_name'

    A key advantage to the naming convention approach is that the names are established
    at Python construction time, rather than at DDL emit time.  The effect this has
    when using Alembic's ``--autogenerate`` feature is that the naming convention
    will be explicit when a new migration script is generated::

        def upgrade():
            op.create_unique_constraint("uq_user_name", "user", ["name"])

    The above ``"uq_user_name"`` string was copied from the :class:`.UniqueConstraint`
    object that ``--autogenerate`` located in our metadata.

    The tokens available include ``%(table_name)s``, ``%(referred_table_name)s``,
    ``%(column_0_name)s``, ``%(column_0_label)s``, ``%(column_0_key)s``,
    ``%(referred_column_0_name)s``, and  ``%(constraint_name)s``, as well as
    multiple-column versions of each including ``%(column_0N_name)s``,
    ``%(column_0_N_name)s``,  ``%(referred_column_0_N_name)s`` which render all
    column names separated with or without an underscore.  The documentation for
    :paramref:`_schema.MetaData.naming_convention` has further detail on each  of these
    conventions.

.. _constraint_default_naming_convention:

默认命名约定
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The Default Naming Convention

.. tab:: 中文

    :paramref:`_schema.MetaData.naming_convention` 的默认值处理了 SQLAlchemy 长期以来的行为，
    即为使用 :paramref:`_schema.Column.index` 参数创建的 :class:`.Index` 对象分配名称::

        >>> from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION
        >>> DEFAULT_NAMING_CONVENTION
        immutabledict({'ix': 'ix_%(column_0_label)s'})

.. tab:: 英文

    The default value for :paramref:`_schema.MetaData.naming_convention` handles
    the long-standing SQLAlchemy behavior of assigning a name to a :class:`.Index`
    object that is created using the :paramref:`_schema.Column.index` parameter::

        >>> from sqlalchemy.sql.schema import DEFAULT_NAMING_CONVENTION
        >>> DEFAULT_NAMING_CONVENTION
        immutabledict({'ix': 'ix_%(column_0_label)s'})

长名称截断
~~~~~~~~~~~~~~~~~~~~~~~~~

Truncation of Long Names

.. tab:: 中文

    当生成的名称（特别是那些使用了多列 token 的名称）超过目标数据库标识符长度限制时
    （例如 PostgreSQL 的限制是 63 个字符），该名称将会被确定性地截断，并追加一个
    基于原始长名称的 md5 哈希值计算出的 4 位后缀。例如，下面的命名规则会由于列名较长
    而生成超长名称::

        metadata_obj = MetaData(
            naming_convention={"uq": "uq_%(table_name)s_%(column_0_N_name)s"}
        )

        long_names = Table(
            "long_names",
            metadata_obj,
            Column("information_channel_code", Integer, key="a"),
            Column("billing_convention_name", Integer, key="b"),
            Column("product_identifier", Integer, key="c"),
            UniqueConstraint("a", "b", "c"),
        )

    在 PostgreSQL 方言中，名称超过 63 个字符时将被如下方式截断：

    .. sourcecode:: sql

        CREATE TABLE long_names (
            information_channel_code INTEGER,
            billing_convention_name INTEGER,
            product_identifier INTEGER,
            CONSTRAINT uq_long_names_information_channel_code_billing_conventi_a79e
            UNIQUE (information_channel_code, billing_convention_name, product_identifier)
        )

    上述后缀 ``a79e`` 是基于长名称的 md5 哈希值得出的，并将在每次生成时保持一致，
    从而为给定的模式生成一致的名称。

.. tab:: 英文

    When a generated name, particularly those that use the multiple-column tokens,
    is too long for the identifier length limit of the target database
    (for example, PostgreSQL has a limit of 63 characters), the name will be
    deterministically truncated using a 4-character suffix based on the md5
    hash of the long name.  For example, the naming convention below will
    generate very long names given the column names in use::

        metadata_obj = MetaData(
            naming_convention={"uq": "uq_%(table_name)s_%(column_0_N_name)s"}
        )

        long_names = Table(
            "long_names",
            metadata_obj,
            Column("information_channel_code", Integer, key="a"),
            Column("billing_convention_name", Integer, key="b"),
            Column("product_identifier", Integer, key="c"),
            UniqueConstraint("a", "b", "c"),
        )

    On the PostgreSQL dialect, names longer than 63 characters will be truncated
    as in the following example:

    .. sourcecode:: sql

        CREATE TABLE long_names (
            information_channel_code INTEGER,
            billing_convention_name INTEGER,
            product_identifier INTEGER,
            CONSTRAINT uq_long_names_information_channel_code_billing_conventi_a79e
            UNIQUE (information_channel_code, billing_convention_name, product_identifier)
        )

    The above suffix ``a79e`` is based on the md5 hash of the long name and will
    generate the same value every time to produce consistent names for a given
    schema.

为命名约定创建自定义标记
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Creating Custom Tokens for Naming Conventions

.. tab:: 中文

    还可以通过在命名约定字典中指定额外的 token 和可调用对象来自定义添加新 token。
    例如，如果我们希望使用 GUID 方案为外键约束命名，可以按如下方式实现::

        import uuid


        def fk_guid(constraint, table):
            str_tokens = (
                [
                    table.name,
                ]
                + [element.parent.name for element in constraint.elements]
                + [element.target_fullname for element in constraint.elements]
            )
            guid = uuid.uuid5(uuid.NAMESPACE_OID, "_".join(str_tokens).encode("ascii"))
            return str(guid)


        convention = {
            "fk_guid": fk_guid,
            "ix": "ix_%(column_0_label)s",
            "fk": "fk_%(fk_guid)s",
        }

    在上例中，当我们创建一个新的 :class:`_schema.ForeignKeyConstraint` 时，
    将获得如下名称::

        >>> metadata_obj = MetaData(naming_convention=convention)

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("version", Integer, primary_key=True),
        ...     Column("data", String(30)),
        ... )
        >>> address_table = Table(
        ...     "address",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("user_id", Integer),
        ...     Column("user_version_id", Integer),
        ... )
        >>> fk = ForeignKeyConstraint(["user_id", "user_version_id"], ["user.id", "user.version"])
        >>> address_table.append_constraint(fk)
        >>> fk.name
        fk_0cd51ab5-8d70-56e8-a83c-86661737766d

    .. seealso::

        :paramref:`_schema.MetaData.naming_convention` - 了解更多用法细节以及可用命名组件的完整列表。

        `命名约束的重要性 <https://alembic.sqlalchemy.org/en/latest/naming.html>`_ - Alembic 文档中的相关说明。


.. tab:: 英文

    New tokens can also be added, by specifying an additional token
    and a callable within the naming_convention dictionary.  For example, if we
    wanted to name our foreign key constraints using a GUID scheme, we could do
    that as follows::

        import uuid


        def fk_guid(constraint, table):
            str_tokens = (
                [
                    table.name,
                ]
                + [element.parent.name for element in constraint.elements]
                + [element.target_fullname for element in constraint.elements]
            )
            guid = uuid.uuid5(uuid.NAMESPACE_OID, "_".join(str_tokens).encode("ascii"))
            return str(guid)


        convention = {
            "fk_guid": fk_guid,
            "ix": "ix_%(column_0_label)s",
            "fk": "fk_%(fk_guid)s",
        }

    Above, when we create a new :class:`_schema.ForeignKeyConstraint`, we will get a
    name as follows::

        >>> metadata_obj = MetaData(naming_convention=convention)

        >>> user_table = Table(
        ...     "user",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("version", Integer, primary_key=True),
        ...     Column("data", String(30)),
        ... )
        >>> address_table = Table(
        ...     "address",
        ...     metadata_obj,
        ...     Column("id", Integer, primary_key=True),
        ...     Column("user_id", Integer),
        ...     Column("user_version_id", Integer),
        ... )
        >>> fk = ForeignKeyConstraint(["user_id", "user_version_id"], ["user.id", "user.version"])
        >>> address_table.append_constraint(fk)
        >>> fk.name
        fk_0cd51ab5-8d70-56e8-a83c-86661737766d

    .. seealso::

        :paramref:`_schema.MetaData.naming_convention` - for additional usage details
        as well as a listing of all available naming components.

        `The Importance of Naming Constraints <https://alembic.sqlalchemy.org/en/latest/naming.html>`_ - in the Alembic documentation.

.. _naming_check_constraints:

命名 CHECK 约束
~~~~~~~~~~~~~~~~~~~~~~~~

Naming CHECK Constraints

.. tab:: 中文

    :class:`.CheckConstraint` 对象配置在任意 SQL 表达式之上，该表达式可以包含任意数量的列，
    而且通常使用原始 SQL 字符串进行配置。因此，对于 :class:`.CheckConstraint`，一种常见的命名约定是：
    假设该对象已有名称，然后再结合其他约定元素进行增强。
    一个典型的约定形式为 ``"ck_%(table_name)s_%(constraint_name)s"``::

        metadata_obj = MetaData(
            naming_convention={"ck": "ck_%(table_name)s_%(constraint_name)s"}
        )

        Table(
            "foo",
            metadata_obj,
            Column("value", Integer),
            CheckConstraint("value > 5", name="value_gt_5"),
        )

    上述表格将生成名称 ``ck_foo_value_gt_5``：

    .. sourcecode:: sql

        CREATE TABLE foo (
            value INTEGER,
            CONSTRAINT ck_foo_value_gt_5 CHECK (value > 5)
        )

    :class:`.CheckConstraint` 也支持 ``%(columns_0_name)s`` token；
    我们可以通过在约束表达式中确保使用 :class:`_schema.Column` 或 :func:`_expression.column` 元素来使用该 token，
    方法可以是将约束与表分离定义::

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        foo = Table("foo", metadata_obj, Column("value", Integer))

        CheckConstraint(foo.c.value > 5)

    也可以通过内联使用 :func:`_expression.column`::

        from sqlalchemy import column

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        foo = Table(
            "foo", metadata_obj, Column("value", Integer), CheckConstraint(column("value") > 5)
        )

    两种方式都会生成名称 ``ck_foo_value``：

    .. sourcecode:: sql

        CREATE TABLE foo (
            value INTEGER,
            CONSTRAINT ck_foo_value CHECK (value > 5)
        )

    “column zero”的名称确定方式是通过扫描表达式中存在的列对象来完成的。
    如果表达式中存在多个列，该扫描会使用确定性的搜索逻辑，
    但具体结构会决定哪一列被视为“column zero”。

.. tab:: 英文

    The :class:`.CheckConstraint` object is configured against an arbitrary
    SQL expression, which can have any number of columns present, and additionally
    is often configured using a raw SQL string.  Therefore a common convention
    to use with :class:`.CheckConstraint` is one where we expect the object
    to have a name already, and we then enhance it with other convention elements.
    A typical convention is ``"ck_%(table_name)s_%(constraint_name)s"``::

        metadata_obj = MetaData(
            naming_convention={"ck": "ck_%(table_name)s_%(constraint_name)s"}
        )

        Table(
            "foo",
            metadata_obj,
            Column("value", Integer),
            CheckConstraint("value > 5", name="value_gt_5"),
        )

    The above table will produce the name ``ck_foo_value_gt_5``:

    .. sourcecode:: sql

        CREATE TABLE foo (
            value INTEGER,
            CONSTRAINT ck_foo_value_gt_5 CHECK (value > 5)
        )

    :class:`.CheckConstraint` also supports the ``%(columns_0_name)s``
    token; we can make use of this by ensuring we use a :class:`_schema.Column` or
    :func:`_expression.column` element within the constraint's expression,
    either by declaring the constraint separate from the table::

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        foo = Table("foo", metadata_obj, Column("value", Integer))

        CheckConstraint(foo.c.value > 5)

    or by using a :func:`_expression.column` inline::

        from sqlalchemy import column

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        foo = Table(
            "foo", metadata_obj, Column("value", Integer), CheckConstraint(column("value") > 5)
        )

    Both will produce the name ``ck_foo_value``:

    .. sourcecode:: sql

        CREATE TABLE foo (
            value INTEGER,
            CONSTRAINT ck_foo_value CHECK (value > 5)
        )

    The determination of the name of "column zero" is performed by scanning
    the given expression for column objects.  If the expression has more than
    one column present, the scan does use a deterministic search, however the
    structure of the expression will determine which column is noted as
    "column zero".

.. _naming_schematypes:

为布尔、枚举和其他架构类型配置命名
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring Naming for Boolean, Enum, and other schema types

.. tab:: 中文

    :class:`.SchemaType` 类指的是如 :class:`.Boolean` 和 :class:`.Enum` 等类型对象，
    它们会为对应的类型生成一个 CHECK 约束。
    此类约束的名称可通过传入 `name` 参数直接指定，例如 :paramref:`.Boolean.name`::

        Table("foo", metadata_obj, Column("flag", Boolean(name="ck_foo_flag")))

    命名约定功能也可以与这些类型结合使用，通常会使用包含 ``%(constraint_name)s`` 的约定，
    并为类型显式指定名称::

        metadata_obj = MetaData(
            naming_convention={"ck": "ck_%(table_name)s_%(constraint_name)s"}
        )

        Table("foo", metadata_obj, Column("flag", Boolean(name="flag_bool")))

    上述表将生成约束名 ``ck_foo_flag_bool``：

    .. sourcecode:: sql

        CREATE TABLE foo (
            flag BOOL,
            CONSTRAINT ck_foo_flag_bool CHECK (flag IN (0, 1))
        )

    :class:`.SchemaType` 类使用了特殊的内部标记机制，使得命名约定仅在 DDL 编译时确定。
    在 PostgreSQL 中，由于存在原生 BOOLEAN 类型，:class:`.Boolean` 的 CHECK 约束并不需要；
    即使为 CHECK 约束配置了命名约定，也可以安全地定义未命名的 :class:`.Boolean` 类型。
    该命名约定仅在运行在不支持原生 BOOLEAN 类型的数据库（如 SQLite 或 MySQL）时才会被启用。

    CHECK 约束也可以使用 ``column_0_name`` token，该 token 与 :class:`.SchemaType` 搭配良好，
    因为这类约束通常只涉及一个列::

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        Table("foo", metadata_obj, Column("flag", Boolean()))

    上述结构将生成：

    .. sourcecode:: sql

        CREATE TABLE foo (
            flag BOOL,
            CONSTRAINT ck_foo_flag CHECK (flag IN (0, 1))
        )

.. tab:: 英文

    The :class:`.SchemaType` class refers to type objects such as :class:`.Boolean`
    and :class:`.Enum` which generate a CHECK constraint accompanying the type.
    The name for the constraint here is most directly set up by sending
    the "name" parameter, e.g. :paramref:`.Boolean.name`::

        Table("foo", metadata_obj, Column("flag", Boolean(name="ck_foo_flag")))

    The naming convention feature may be combined with these types as well,
    normally by using a convention which includes ``%(constraint_name)s``
    and then applying a name to the type::

        metadata_obj = MetaData(
            naming_convention={"ck": "ck_%(table_name)s_%(constraint_name)s"}
        )

        Table("foo", metadata_obj, Column("flag", Boolean(name="flag_bool")))

    The above table will produce the constraint name ``ck_foo_flag_bool``:

    .. sourcecode:: sql

        CREATE TABLE foo (
            flag BOOL,
            CONSTRAINT ck_foo_flag_bool CHECK (flag IN (0, 1))
        )

    The :class:`.SchemaType` classes use special internal symbols so that
    the naming convention is only determined at DDL compile time.  On PostgreSQL,
    there's a native BOOLEAN type, so the CHECK constraint of :class:`.Boolean`
    is not needed; we are safe to set up a :class:`.Boolean` type without a
    name, even though a naming convention is in place for check constraints.
    This convention will only be consulted for the CHECK constraint if we
    run against a database without a native BOOLEAN type like SQLite or
    MySQL.

    The CHECK constraint may also make use of the ``column_0_name`` token,
    which works nicely with :class:`.SchemaType` since these constraints have
    only one column::

        metadata_obj = MetaData(naming_convention={"ck": "ck_%(table_name)s_%(column_0_name)s"})

        Table("foo", metadata_obj, Column("flag", Boolean()))

    The above schema will produce:

    .. sourcecode:: sql

        CREATE TABLE foo (
            flag BOOL,
            CONSTRAINT ck_foo_flag CHECK (flag IN (0, 1))
        )

将命名约定与 ORM 声明性混合使用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using Naming Conventions with ORM Declarative Mixins

.. tab:: 中文

    当在 :ref:`ORM Declarative Mixins <orm_mixins_toplevel>` 中使用命名约定功能时，
    每个实际映射到表的子类必须拥有各自独立的约束对象。
    详见 :ref:`orm_mixins_named_constraints` 部分以获取背景信息和示例。

.. tab:: 英文

    When using the naming convention feature with :ref:`ORM Declarative Mixins
    <orm_mixins_toplevel>`, individual constraint objects must exist for each
    actual table-mapped subclass.  See the section
    :ref:`orm_mixins_named_constraints` for background and examples.

约束 API
---------------

Constraints API

.. autoclass:: Constraint
    :members:
    :inherited-members:

.. autoclass:: ColumnCollectionMixin
    :members:

.. autoclass:: ColumnCollectionConstraint
    :members:
    :inherited-members:

.. autoclass:: CheckConstraint
    :members:
    :inherited-members:

.. autoclass:: ForeignKey
    :members:
    :inherited-members:

.. autoclass:: ForeignKeyConstraint
    :members:
    :inherited-members:

.. autoclass:: HasConditionalDDL
    :members:
    :inherited-members:

.. autoclass:: PrimaryKeyConstraint
    :members:
    :inherited-members:


.. autoclass:: UniqueConstraint
    :members:
    :inherited-members:


.. autofunction:: sqlalchemy.schema.conv

.. _schema_indexes:

索引
-------

Indexes

.. tab:: 中文

    索引可以匿名创建（使用自动生成的名称 ``ix_<column label>``），
    方法是在 :class:`~sqlalchemy.schema.Column` 上使用内联的 ``index`` 关键字，
    这也会修改 ``unique`` 的行为，使其将唯一性应用于索引本身，而不是单独添加一个 UNIQUE 约束。
    对于具有指定名称或包含多个列的索引，请使用需要显式指定名称的
    :class:`~sqlalchemy.schema.Index` 构造。

    下面演示了一个包含多个 :class:`~sqlalchemy.schema.Index` 对象的
    :class:`~sqlalchemy.schema.Table`。
    "CREATE INDEX" 的 DDL 会在表创建语句之后立即发出：

    .. sourcecode:: python+sql

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # 一个带索引的列，索引名为 "ix_mytable_col1"
            Column("col1", Integer, index=True),
            # 一个唯一索引的列，索引名为 "ix_mytable_col2"
            Column("col2", Integer, index=True, unique=True),
            Column("col3", Integer),
            Column("col4", Integer),
            Column("col5", Integer),
            Column("col6", Integer),
        )

        # 在 col3 和 col4 上创建一个索引
        Index("idx_col34", mytable.c.col3, mytable.c.col4)

        # 在 col5 和 col6 上创建一个唯一索引
        Index("myindex", mytable.c.col5, mytable.c.col6, unique=True)

        mytable.create(engine)
        {execsql}CREATE TABLE mytable (
            col1 INTEGER,
            col2 INTEGER,
            col3 INTEGER,
            col4 INTEGER,
            col5 INTEGER,
            col6 INTEGER
        )
        CREATE INDEX ix_mytable_col1 ON mytable (col1)
        CREATE UNIQUE INDEX ix_mytable_col2 ON mytable (col2)
        CREATE UNIQUE INDEX myindex ON mytable (col5, col6)
        CREATE INDEX idx_col34 ON mytable (col3, col4){stop}

    注意，上述示例中 :class:`.Index` 构造是在与其关联的表对象之外定义的，
    直接使用了 :class:`_schema.Column` 对象。
    :class:`.Index` 也支持在 :class:`_schema.Table` 内部进行“内联”定义，
    使用字符串名称来标识列::

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            Column("col1", Integer),
            Column("col2", Integer),
            Column("col3", Integer),
            Column("col4", Integer),
            # 在 col1 和 col2 上创建索引
            Index("idx_col12", "col1", "col2"),
            # 在 col3 和 col4 上创建唯一索引
            Index("idx_col34", "col3", "col4", unique=True),
        )

    :class:`~sqlalchemy.schema.Index` 对象也支持其自身的 ``create()`` 方法：

    .. sourcecode:: python+sql

        i = Index("someindex", mytable.c.col5)
        i.create(engine)
        {execsql}CREATE INDEX someindex ON mytable (col5){stop}


.. tab:: 英文

    Indexes can be created anonymously (using an auto-generated name ``ix_<column
    label>``) for a single column using the inline ``index`` keyword on
    :class:`~sqlalchemy.schema.Column`, which also modifies the usage of
    ``unique`` to apply the uniqueness to the index itself, instead of adding a
    separate UNIQUE constraint. For indexes with specific names or which encompass
    more than one column, use the :class:`~sqlalchemy.schema.Index` construct,
    which requires a name.

    Below we illustrate a :class:`~sqlalchemy.schema.Table` with several
    :class:`~sqlalchemy.schema.Index` objects associated. The DDL for "CREATE
    INDEX" is issued right after the create statements for the table:

    .. sourcecode:: python+sql

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            # an indexed column, with index "ix_mytable_col1"
            Column("col1", Integer, index=True),
            # a uniquely indexed column with index "ix_mytable_col2"
            Column("col2", Integer, index=True, unique=True),
            Column("col3", Integer),
            Column("col4", Integer),
            Column("col5", Integer),
            Column("col6", Integer),
        )

        # place an index on col3, col4
        Index("idx_col34", mytable.c.col3, mytable.c.col4)

        # place a unique index on col5, col6
        Index("myindex", mytable.c.col5, mytable.c.col6, unique=True)

        mytable.create(engine)
        {execsql}CREATE TABLE mytable (
            col1 INTEGER,
            col2 INTEGER,
            col3 INTEGER,
            col4 INTEGER,
            col5 INTEGER,
            col6 INTEGER
        )
        CREATE INDEX ix_mytable_col1 ON mytable (col1)
        CREATE UNIQUE INDEX ix_mytable_col2 ON mytable (col2)
        CREATE UNIQUE INDEX myindex ON mytable (col5, col6)
        CREATE INDEX idx_col34 ON mytable (col3, col4){stop}

    Note in the example above, the :class:`.Index` construct is created
    externally to the table which it corresponds, using :class:`_schema.Column`
    objects directly.  :class:`.Index` also supports
    "inline" definition inside the :class:`_schema.Table`, using string names to
    identify columns::

        metadata_obj = MetaData()
        mytable = Table(
            "mytable",
            metadata_obj,
            Column("col1", Integer),
            Column("col2", Integer),
            Column("col3", Integer),
            Column("col4", Integer),
            # place an index on col1, col2
            Index("idx_col12", "col1", "col2"),
            # place a unique index on col3, col4
            Index("idx_col34", "col3", "col4", unique=True),
        )

    The :class:`~sqlalchemy.schema.Index` object also supports its own ``create()`` method:

    .. sourcecode:: python+sql

        i = Index("someindex", mytable.c.col5)
        i.create(engine)
        {execsql}CREATE INDEX someindex ON mytable (col5){stop}

.. _schema_indexes_functional:

功能索引
~~~~~~~~~~~~~~~~~~

Functional Indexes

.. tab:: 中文

    :class:`.Index` 支持由目标后端支持的 SQL 和函数表达式。
    若要对列的降序值创建索引，可使用 :meth:`_expression.ColumnElement.desc` 修饰符::

        from sqlalchemy import Index

        Index("someindex", mytable.c.somecol.desc())

    或者，在支持函数索引（如 PostgreSQL）的后端中，
    可以使用 ``lower()`` 函数创建“大小写不敏感”索引::

        from sqlalchemy import func, Index

        Index("someindex", func.lower(mytable.c.somecol))

.. tab:: 英文

    :class:`.Index` supports SQL and function expressions, as supported by the
    target backend.  To create an index against a column using a descending
    value, the :meth:`_expression.ColumnElement.desc` modifier may be used::

        from sqlalchemy import Index

        Index("someindex", mytable.c.somecol.desc())

    Or with a backend that supports functional indexes such as PostgreSQL,
    a "case insensitive" index can be created using the ``lower()`` function::

        from sqlalchemy import func, Index

        Index("someindex", func.lower(mytable.c.somecol))

索引 API
---------

Index API

.. tab:: 中文

.. tab:: 英文

.. autoclass:: Index
    :members:
    :inherited-members:
