.. _self_referential:

邻接表关系
----------------------------

Adjacency List Relationships

.. tab:: 中文

    **邻接列表** 模式是一种常见的关系模式，其中一个表包含对自身的外键引用，换句话说就是一个 **自引用关系** 。这是在平面表中表示层次数据的最常见方法。其他方法包括 **嵌套集合** ，有时称为“修改的先序”，以及 **物化路径** 。尽管修改的先序在SQL查询中的流畅性上具有吸引力，但由于并发性、降低复杂性以及修改的先序对于能够完全加载子树到应用空间的应用程序没有太大优势的原因，邻接列表模型可能是大多数层次存储需求中最合适的模式。

    .. seealso::

        本节详细介绍了单表版本的自引用关系。有关使用第二个表作为关联表的自引用关系，请参阅
        :ref:`self_referential_many_to_many` 部分。

    在本例中，我们将使用一个名为 ``Node`` 的映射类来表示树结构::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node")

    使用这种结构，一个如下的图：

    .. sourcecode:: text

        root --+---> child1
               +---> child2 --+--> subchild1
               |              +--> subchild2
               +---> child3

    将表示为如下数据：

    .. sourcecode:: text

        id       parent_id     data
        ---      -------       ----
        1        NULL          root
        2        1             child1
        3        1             child2
        4        3             subchild1
        5        3             subchild2
        6        1             child3

    这里的 :func:`_orm.relationship` 配置与“普通”一对多关系的工作方式相同，唯一的例外是“方向”，即关系是一对多还是多对一，默认情况下假定为一对多。要建立多对一关系，需要添加一个额外的指令，称为 :paramref:`_orm.relationship.remote_side`，它是一个 :class:`_schema.Column` 或一组 :class:`_schema.Column` 对象，指示那些应被视为“远程”的列::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            parent = relationship("Node", remote_side=[id])

    在上面的代码中， ``id`` 列被应用为 ``parent`` :func:`_orm.relationship` 的 :paramref:`_orm.relationship.remote_side`，从而将 ``parent_id`` 确立为“本地”端，关系然后表现为多对一。

    一如既往，可以使用两个由 :paramref:`_orm.relationship.back_populates` 连接的 :func:`_orm.relationship` 构造将两个方向组合成双向关系::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node", back_populates="parent")
            parent = relationship("Node", back_populates="children", remote_side=[id])

    .. seealso::

        :ref:`examples_adjacencylist` - 更新后的 SQLAlchemy 2.0 实例

.. tab:: 英文

    The **adjacency list** pattern is a common relational pattern whereby a table
    contains a foreign key reference to itself, in other words is a
    **self referential relationship**. This is the most common
    way to represent hierarchical data in flat tables.  Other methods
    include **nested sets**, sometimes called "modified preorder",
    as well as **materialized path**.  Despite the appeal that modified preorder
    has when evaluated for its fluency within SQL queries, the adjacency list model is
    probably the most appropriate pattern for the large majority of hierarchical
    storage needs, for reasons of concurrency, reduced complexity, and that
    modified preorder has little advantage over an application which can fully
    load subtrees into the application space.

    .. seealso::

        This section details the single-table version of a self-referential
        relationship. For a self-referential relationship that uses a second table
        as an association table, see the section
        :ref:`self_referential_many_to_many`.

    In this example, we'll work with a single mapped
    class called ``Node``, representing a tree structure::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node")

    With this structure, a graph such as the following:

    .. sourcecode:: text

        root --+---> child1
            +---> child2 --+--> subchild1
            |              +--> subchild2
            +---> child3

    Would be represented with data such as:

    .. sourcecode:: text

        id       parent_id     data
        ---      -------       ----
        1        NULL          root
        2        1             child1
        3        1             child2
        4        3             subchild1
        5        3             subchild2
        6        1             child3

    The :func:`_orm.relationship` configuration here works in the
    same way as a "normal" one-to-many relationship, with the
    exception that the "direction", i.e. whether the relationship
    is one-to-many or many-to-one, is assumed by default to
    be one-to-many.   To establish the relationship as many-to-one,
    an extra directive is added known as :paramref:`_orm.relationship.remote_side`, which
    is a :class:`_schema.Column` or collection of :class:`_schema.Column` objects
    that indicate those which should be considered to be "remote"::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            parent = relationship("Node", remote_side=[id])

    Where above, the ``id`` column is applied as the :paramref:`_orm.relationship.remote_side`
    of the ``parent`` :func:`_orm.relationship`, thus establishing
    ``parent_id`` as the "local" side, and the relationship
    then behaves as a many-to-one.

    As always, both directions can be combined into a bidirectional
    relationship using two :func:`_orm.relationship` constructs linked by
    :paramref:`_orm.relationship.back_populates`::

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node", back_populates="parent")
            parent = relationship("Node", back_populates="children", remote_side=[id])

    .. seealso::

        :ref:`examples_adjacencylist` - working example, updated for SQLAlchemy 2.0

复合邻接表
~~~~~~~~~~~~~~~~~~~~~~~~~

Composite Adjacency Lists

.. tab:: 中文

    邻接列表关系的一个子类别是一个罕见的情况，其中一个特定列在连接条件的“本地(local)”和“远程(remote)”两侧都存在。下面的 ``Folder`` 类是一个示例；使用复合主键， ``account_id`` 列指向自身，以指示与父文件夹属于同一帐户的子文件夹；而 ``folder_id`` 则指向该帐户中的特定文件夹::

        class Folder(Base):
            __tablename__ = "folder"
            __table_args__ = (
                ForeignKeyConstraint(
                    ["account_id", "parent_id"], ["folder.account_id", "folder.folder_id"]
                ),
            )

            account_id = mapped_column(Integer, primary_key=True)
            folder_id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer)
            name = mapped_column(String)

            parent_folder = relationship(
                "Folder", back_populates="child_folders", remote_side=[account_id, folder_id]
            )

            child_folders = relationship("Folder", back_populates="parent_folder")

    在上面的代码中，我们将 ``account_id`` 传递到 :paramref:`_orm.relationship.remote_side` 列表中。:func:`_orm.relationship` 识别出这里的 ``account_id`` 列在两侧都有，并将“远程”列与 ``folder_id`` 列对齐，后者被识别为仅存在于“远程”一侧。

.. tab:: 英文

    A sub-category of the adjacency list relationship is the rare
    case where a particular column is present on both the "local" and
    "remote" side of the join condition.  An example is the ``Folder``
    class below; using a composite primary key, the ``account_id``
    column refers to itself, to indicate sub folders which are within
    the same account as that of the parent; while ``folder_id`` refers
    to a specific folder within that account::

        class Folder(Base):
            __tablename__ = "folder"
            __table_args__ = (
                ForeignKeyConstraint(
                    ["account_id", "parent_id"], ["folder.account_id", "folder.folder_id"]
                ),
            )

            account_id = mapped_column(Integer, primary_key=True)
            folder_id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer)
            name = mapped_column(String)

            parent_folder = relationship(
                "Folder", back_populates="child_folders", remote_side=[account_id, folder_id]
            )

            child_folders = relationship("Folder", back_populates="parent_folder")

    Above, we pass ``account_id`` into the :paramref:`_orm.relationship.remote_side` list.
    :func:`_orm.relationship` recognizes that the ``account_id`` column here
    is on both sides, and aligns the "remote" column along with the
    ``folder_id`` column, which it recognizes as uniquely present on
    the "remote" side.

.. _self_referential_query:

自引用查询策略
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Self-Referential Query Strategies

.. tab:: 中文

    自引用结构的查询与其他查询一样工作::

        # 获取所有名为 'child2' 的节点
        session.scalars(select(Node).where(Node.data == "child2"))

    但是，当尝试沿着树的一个级别到下一个级别的外键进行连接时，需要特别注意。在 SQL 中，从一个表到自身的连接要求表达式的至少一侧被“别名化(aliased)”，以便可以明确引用它。

    回想一下 ORM 教程中的 :ref:`orm_queryguide_orm_aliases` ， :func:`_orm.aliased` 构造通常用于提供 ORM 实体的“别名”。使用这种技术从 ``Node`` 到自身的连接如下所示：

    .. sourcecode:: python+sql

        from sqlalchemy.orm import aliased

        nodealias = aliased(Node)
        session.scalars(
            select(Node)
            .where(Node.data == "subchild1")
            .join(Node.parent.of_type(nodealias))
            .where(nodealias.data == "child2")
        ).all()
        {execsql}SELECT node.id AS node_id,
                node.parent_id AS node_parent_id,
                node.data AS node_data
        FROM node JOIN node AS node_1
            ON node.parent_id = node_1.id
        WHERE node.data = ?
            AND node_1.data = ?
        ['subchild1', 'child2']

.. tab:: 英文

    Querying of self-referential structures works like any other query::

        # get all nodes named 'child2'
        session.scalars(select(Node).where(Node.data == "child2"))

    However extra care is needed when attempting to join along
    the foreign key from one level of the tree to the next.  In SQL,
    a join from a table to itself requires that at least one side of the
    expression be "aliased" so that it can be unambiguously referred to.

    Recall from :ref:`orm_queryguide_orm_aliases` in the ORM tutorial that the
    :func:`_orm.aliased` construct is normally used to provide an "alias" of
    an ORM entity.  Joining from ``Node`` to itself using this technique
    looks like:

    .. sourcecode:: python+sql

        from sqlalchemy.orm import aliased

        nodealias = aliased(Node)
        session.scalars(
            select(Node)
            .where(Node.data == "subchild1")
            .join(Node.parent.of_type(nodealias))
            .where(nodealias.data == "child2")
        ).all()
        {execsql}SELECT node.id AS node_id,
                node.parent_id AS node_parent_id,
                node.data AS node_data
        FROM node JOIN node AS node_1
            ON node.parent_id = node_1.id
        WHERE node.data = ?
            AND node_1.data = ?
        ['subchild1', 'child2']


.. _self_referential_eager_loading:

配置自引用预加载
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuring Self-Referential Eager Loading

.. tab:: 中文

    在正常查询操作期间，关系的预加载（eager loading）使用从父表到子表的连接或外连接进行，这样父表及其直接子集合或引用可以从单个 SQL 语句中填充，或通过第二个语句填充所有直接子集合。SQLAlchemy 的连接和子查询预加载在连接到相关项时始终使用别名表，因此与自引用连接兼容。然而，要对自引用关系使用预加载，SQLAlchemy 需要知道应该连接和/或查询多深的层次；否则，根本不会进行预加载。此深度设置通过 :paramref:`~.relationships.join_depth` 配置：

    .. sourcecode:: python+sql

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node", lazy="joined", join_depth=2)


        session.scalars(select(Node)).all()
        {execsql}SELECT node_1.id AS node_1_id,
                node_1.parent_id AS node_1_parent_id,
                node_1.data AS node_1_data,
                node_2.id AS node_2_id,
                node_2.parent_id AS node_2_parent_id,
                node_2.data AS node_2_data,
                node.id AS node_id,
                node.parent_id AS node_parent_id,
                node.data AS node_data
        FROM node
            LEFT OUTER JOIN node AS node_2
                ON node.id = node_2.parent_id
            LEFT OUTER JOIN node AS node_1
                ON node_2.id = node_1.parent_id
        []

.. tab:: 英文

    Eager loading of relationships occurs using joins or outerjoins from parent to
    child table during a normal query operation, such that the parent and its
    immediate child collection or reference can be populated from a single SQL
    statement, or a second statement for all immediate child collections.
    SQLAlchemy's joined and subquery eager loading use aliased tables in all cases
    when joining to related items, so are compatible with self-referential
    joining. However, to use eager loading with a self-referential relationship,
    SQLAlchemy needs to be told how many levels deep it should join and/or query;
    otherwise the eager load will not take place at all. This depth setting is
    configured via :paramref:`~.relationships.join_depth`:

    .. sourcecode:: python+sql

        class Node(Base):
            __tablename__ = "node"
            id = mapped_column(Integer, primary_key=True)
            parent_id = mapped_column(Integer, ForeignKey("node.id"))
            data = mapped_column(String(50))
            children = relationship("Node", lazy="joined", join_depth=2)


        session.scalars(select(Node)).all()
        {execsql}SELECT node_1.id AS node_1_id,
                node_1.parent_id AS node_1_parent_id,
                node_1.data AS node_1_data,
                node_2.id AS node_2_id,
                node_2.parent_id AS node_2_parent_id,
                node_2.data AS node_2_data,
                node.id AS node_id,
                node.parent_id AS node_parent_id,
                node.data AS node_data
        FROM node
            LEFT OUTER JOIN node AS node_2
                ON node.id = node_2.parent_id
            LEFT OUTER JOIN node AS node_1
                ON node_2.id = node_1.parent_id
        []

