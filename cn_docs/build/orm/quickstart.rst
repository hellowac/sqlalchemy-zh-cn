.. _orm_quickstart:


ORM 快速入门
===============

ORM Quick Start

.. tab:: 中文

    对于想快速了解基本 ORM 使用的新用户，这里是 :ref:`unified_tutorial` 中使用的映射和示例的简短形式。此处的代码可以从一个干净的命令行完全运行。

    由于本节中的描述故意 **非常简短(very short)**，请继续阅读完整的 :ref:`unified_tutorial` 以获取每个概念的更深入描述。

    .. versionchanged:: 2.0
        
        ORM 快速入门已更新为最新的 :pep:`484` 感知功能，使用了包括 :func:`_orm.mapped_column` 在内的新构造。有关迁移信息，请参阅部分 :ref:`whatsnew_20_orm_declarative_typing`。

.. tab:: 英文

    For new users who want to quickly see what basic ORM use looks like, here's an
    abbreviated form of the mappings and examples used in the
    :ref:`unified_tutorial`. The code here is fully runnable from a clean command
    line.

    As the descriptions in this section are intentionally **very short**, please
    proceed to the full :ref:`unified_tutorial` for a much more in-depth
    description of each of the concepts being illustrated here.

    .. versionchanged:: 2.0  
        
        The ORM Quickstart is updated for the latest
        :pep:`484`-aware features using new constructs including
        :func:`_orm.mapped_column`.   See the section
        :ref:`whatsnew_20_orm_declarative_typing` for migration information.

声明模型
---------------

Declare Models

.. tab:: 中文

    在这里，我们定义了模块级别的结构，这些结构将形成我们从数据库中查询的内容。这种结构称为 :ref:`声明性映射 <orm_declarative_mapping>`，它同时定义了一个Python对象模型，以及描述实际存在或将存在于特定数据库中的SQL表的 :term:`数据库元数据` ::

        >>> from typing import List
        >>> from typing import Optional
        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import String
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship

        >>> class Base(DeclarativeBase):
        ...     pass

        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str] = mapped_column(String(30))
        ...     fullname: Mapped[Optional[str]]
        ...
        ...     addresses: Mapped[List["Address"]] = relationship(
        ...         back_populates="user", cascade="all, delete-orphan"
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     email_address: Mapped[str]
        ...     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...
        ...     user: Mapped["User"] = relationship(back_populates="addresses")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Address(id={self.id!r}, email_address={self.email_address!r})"

    映射从一个基类开始，上面的例子中称为``Base``，它是通过简单地对:class:`_orm.DeclarativeBase`类进行子类化创建的。

    然后，通过创建 ``Base`` 的子类来创建单个映射类。映射类通常指一个特定的数据库表，其名称通过使用 ``__tablename__`` 类级别属性来指示。

    接下来，通过添加包含称为 :class:`_orm.Mapped` 的特殊类型注释的属性，声明表的一部分的列。每个属性的名称对应于要成为数据库表一部分的列的名称。每列的数据类型首先从与每个 :class:`_orm.Mapped` 注释关联的Python数据类型中获取； ``int`` 对应 ``INTEGER`` ， ``str`` 对应 ``VARCHAR`` 等。可为空性来自于是否使用了 ``Optional[]`` 类型修饰符。可以在右侧 :func:`_orm.mapped_column` 指令中使用SQLAlchemy类型对象来指示更具体的类型信息，例如在 ``User.name`` 列中使用的 :class:`.String` 数据类型。可以使用 :ref:`类型注释映射 <orm_declarative_mapped_column_type_map>` 自定义Python类型和SQL类型之间的关联。

    :func:`_orm.mapped_column` 指令用于所有需要更具体定制的基于列的属性。除了类型信息外，该指令还接受广泛的参数，用于指示有关数据库列的具体细节，包括服务器默认值和约束信息，例如主键和外键的成员资格。 :func:`_orm.mapped_column` 指令接受SQLAlchemy :class:`_schema.Column` 类接受的参数的超集，SQLAlchemy Core使用该类表示数据库列。

    所有ORM映射类都需要至少一个列声明为主键的一部分，通常通过在应成为主键一部分的那些 :func:`_orm.mapped_column` 对象上使用 :paramref:`_schema.Column.primary_key` 参数。在上面的例子中， ``User.id`` 和 ``Address.id`` 列被标记为主键。

    总体而言，字符串表名称和列声明列表的组合在SQLAlchemy中称为 :term:`表元数据` 。在 :ref:`统一教程 <unified_tutorial>` 的:ref:`tutorial_working_with_metadata` 中介绍了使用Core和ORM方法设置表元数据。上面的映射是称为 :ref:`注释声明性表 <orm_declarative_mapped_column>` 配置的示例。

    还有其他变体的 :class:`_orm.Mapped` 可用，最常见的是上面指示的 :func:`_orm.relationship` 构造。与基于列的属性相反， :func:`_orm.relationship` 表示两个ORM类之间的链接。在上面的例子中， ``User.addresses`` 将 ``User`` 链接到` `Address``，而 ``Address.user`` 将 ``Address`` 链接到 ``User`` 。在 :ref:`统一教程 <unified_tutorial>` 的 :ref:`tutorial_orm_related_objects` 中介绍了 :func:`_orm.relationship` 构造。

    最后，上面的示例类包括一个 ``__repr__()`` 方法，这不是必需的，但对调试很有用。可以使用数据类自动生成类似 ``__repr__()`` 的方法来创建映射类。有关数据类映射的更多信息，请参见 :ref:`orm_declarative_native_dataclasses` 。

.. tab:: 英文

    Here, we define module-level constructs that will form the structures
    which we will be querying from the database.  This structure, known as a
    :ref:`Declarative Mapping <orm_declarative_mapping>`, defines at once both a
    Python object model, as well as :term:`database metadata` that describes
    real SQL tables that exist, or will exist, in a particular database::

        >>> from typing import List
        >>> from typing import Optional
        >>> from sqlalchemy import ForeignKey
        >>> from sqlalchemy import String
        >>> from sqlalchemy.orm import DeclarativeBase
        >>> from sqlalchemy.orm import Mapped
        >>> from sqlalchemy.orm import mapped_column
        >>> from sqlalchemy.orm import relationship

        >>> class Base(DeclarativeBase):
        ...     pass

        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str] = mapped_column(String(30))
        ...     fullname: Mapped[Optional[str]]
        ...
        ...     addresses: Mapped[List["Address"]] = relationship(
        ...         back_populates="user", cascade="all, delete-orphan"
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"

        >>> class Address(Base):
        ...     __tablename__ = "address"
        ...
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     email_address: Mapped[str]
        ...     user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...
        ...     user: Mapped["User"] = relationship(back_populates="addresses")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Address(id={self.id!r}, email_address={self.email_address!r})"

    The mapping starts with a base class, which above is called ``Base``, and is
    created by making a simple subclass against the :class:`_orm.DeclarativeBase`
    class.

    Individual mapped classes are then created by making subclasses of ``Base``.
    A mapped class typically refers to a single particular database table,
    the name of which is indicated by using the ``__tablename__`` class-level
    attribute.

    Next, columns that are part of the table are declared, by adding attributes
    that include a special typing annotation called :class:`_orm.Mapped`. The name
    of each attribute corresponds to the column that is to be part of the database
    table. The datatype of each column is taken first from the Python datatype
    that's associated with each :class:`_orm.Mapped` annotation; ``int`` for
    ``INTEGER``, ``str`` for ``VARCHAR``, etc. Nullability derives from whether or
    not the ``Optional[]`` type modifier is used. More specific typing information
    may be indicated using SQLAlchemy type objects in the right side
    :func:`_orm.mapped_column` directive, such as the :class:`.String` datatype
    used above in the ``User.name`` column. The association between Python types
    and SQL types can be customized using the
    :ref:`type annotation map <orm_declarative_mapped_column_type_map>`.

    The :func:`_orm.mapped_column` directive is used for all column-based
    attributes that require more specific customization. Besides typing
    information, this directive accepts a wide variety of arguments that indicate
    specific details about a database column, including server defaults and
    constraint information, such as membership within the primary key and foreign
    keys. The :func:`_orm.mapped_column` directive accepts a superset of arguments
    that are accepted by the SQLAlchemy :class:`_schema.Column` class, which is
    used by SQLAlchemy Core to represent database columns.

    All ORM mapped classes require at least one column be declared as part of the
    primary key, typically by using the :paramref:`_schema.Column.primary_key`
    parameter on those :func:`_orm.mapped_column` objects that should be part
    of the key.  In the above example, the ``User.id`` and ``Address.id``
    columns are marked as primary key.

    Taken together, the combination of a string table name as well as a list
    of column declarations is known in SQLAlchemy as :term:`table metadata`.
    Setting up table metadata using both Core and ORM approaches is introduced
    in the :ref:`unified_tutorial` at :ref:`tutorial_working_with_metadata`.
    The above mapping is an example of what's known as
    :ref:`Annotated Declarative Table <orm_declarative_mapped_column>`
    configuration.

    Other variants of :class:`_orm.Mapped` are available, most commonly
    the :func:`_orm.relationship` construct indicated above.  In contrast
    to the column-based attributes, :func:`_orm.relationship` denotes a linkage
    between two ORM classes.  In the above example, ``User.addresses`` links
    ``User`` to ``Address``, and ``Address.user`` links ``Address`` to ``User``.
    The :func:`_orm.relationship` construct is introduced in the
    :ref:`unified_tutorial` at :ref:`tutorial_orm_related_objects`.

    Finally, the above example classes include a ``__repr__()`` method, which is
    not required but is useful for debugging. Mapped classes can be created with
    methods such as ``__repr__()`` generated automatically, using dataclasses. More
    on dataclass mapping at :ref:`orm_declarative_native_dataclasses`.


创建引擎
------------------

Create an Engine

.. tab:: 中文

    :class:`_engine.Engine` 是一个 **工厂(factory)**，可以为我们创建新的数据库连接，同时还将连接保存在
    :ref:`连接池 <pooling_toplevel>` 中以便快速重用。为了学习目的，我们通常使用一个方便的
    :ref:`SQLite <sqlite_toplevel>` 内存数据库::

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite://", echo=True)

    .. tip::

        ``echo=True`` 参数指示连接发出的SQL语句将被记录到标准输出。

    有关 :class:`_engine.Engine` 的完整介绍请参见 :ref:`tutorial_engine` 。

.. tab:: 英文

    The :class:`_engine.Engine` is a **factory** that can create new
    database connections for us, which also holds onto connections inside
    of a :ref:`Connection Pool <pooling_toplevel>` for fast reuse.  For learning
    purposes, we normally use a :ref:`SQLite <sqlite_toplevel>` memory-only database
    for convenience::

        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("sqlite://", echo=True)

    .. tip::

        The ``echo=True`` parameter indicates that SQL emitted by connections will
        be logged to standard out.

    A full intro to the :class:`_engine.Engine` starts at :ref:`tutorial_engine`.

发出 CREATE TABLE DDL
----------------------

Emit CREATE TABLE DDL

.. tab:: 中文

    使用我们的表元数据和引擎，我们可以使用称为 :meth:`_schema.MetaData.create_all` 的方法在目标SQLite数据库中一次性生成我们的模式：

    .. sourcecode:: pycon+sql

        >>> Base.metadata.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        CREATE TABLE user_account (
            id INTEGER NOT NULL,
            name VARCHAR(30) NOT NULL,
            fullname VARCHAR,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE address (
            id INTEGER NOT NULL,
            email_address VARCHAR NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES user_account (id)
        )
        ...
        COMMIT

    从我们编写的这段Python代码中发生了很多事情。有关表元数据的完整概述，请继续阅读教程 :ref:`tutorial_working_with_metadata`。

.. tab:: 英文

    Using our table metadata and our engine, we can generate our schema at once
    in our target SQLite database, using a method called :meth:`_schema.MetaData.create_all`:

    .. sourcecode:: pycon+sql

        >>> Base.metadata.create_all(engine)
        {execsql}BEGIN (implicit)
        PRAGMA main.table_...info("user_account")
        ...
        PRAGMA main.table_...info("address")
        ...
        CREATE TABLE user_account (
            id INTEGER NOT NULL,
            name VARCHAR(30) NOT NULL,
            fullname VARCHAR,
            PRIMARY KEY (id)
        )
        ...
        CREATE TABLE address (
            id INTEGER NOT NULL,
            email_address VARCHAR NOT NULL,
            user_id INTEGER NOT NULL,
            PRIMARY KEY (id),
            FOREIGN KEY(user_id) REFERENCES user_account (id)
        )
        ...
        COMMIT

    A lot just happened from that bit of Python code we wrote.  For a complete
    overview of what's going on on with Table metadata, proceed in the
    Tutorial at :ref:`tutorial_working_with_metadata`.

创建对象并持久化
---------------------------

Create Objects and Persist

.. tab:: 中文

    现在我们已经准备好向数据库插入数据了。我们通过创建具有已由声明性映射过程自动建立的 ``__init__()`` 方法的 ``User`` 和 ``Address`` 类的实例来完成此操作。然后，我们使用一个称为 :ref:`Session <tutorial_executing_orm_session>` 的对象将它们传递到数据库，该对象利用 :class:`_engine.Engine` 与数据库交互。这里使用 :meth:`_orm.Session.add_all` 方法一次添加多个对象，并使用 :meth:`_orm.Session.commit` 方法来 :ref:`刷新 <session_flushing>` 任何待处理的更改到数据库，然后 :ref:`提交 <session_committing>` 当前的数据库事务，只要使用 :class:`_orm.Session`，该事务就始终在进行中：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import Session

        >>> with Session(engine) as session:
        ...     spongebob = User(
        ...         name="spongebob",
        ...         fullname="Spongebob Squarepants",
        ...         addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        ...     )
        ...     sandy = User(
        ...         name="sandy",
        ...         fullname="Sandy Cheeks",
        ...         addresses=[
        ...             Address(email_address="sandy@sqlalchemy.org"),
        ...             Address(email_address="sandy@squirrelpower.org"),
        ...         ],
        ...     )
        ...     patrick = User(name="patrick", fullname="Patrick Star")
        ...
        ...     session.add_all([spongebob, sandy, patrick])
        ...
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('spongebob', 'Spongebob Squarepants')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('sandy', 'Sandy Cheeks')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('patrick', 'Patrick Star')
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('spongebob@sqlalchemy.org', 1)
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('sandy@sqlalchemy.org', 2)
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('sandy@squirrelpower.org', 2)
        COMMIT


    .. tip::

        建议以上述方式在上下文管理器样式中使用 :class:`_orm.Session`，即使用Python ``with:`` 语句。
        :class:`_orm.Session` 对象表示活动的数据库资源，因此在完成一系列操作后，确保关闭它是很好的。在下一节中，我们将保持 :class:`_orm.Session` 打开只是为了说明。

    创建 :class:`_orm.Session` 的基础知识在 :ref:`tutorial_executing_orm_session`，更多内容在 :ref:`session_basics`。

    然后，在 :ref:`tutorial_inserting_orm` 中介绍了一些基本持久化操作的变体。

.. tab:: 英文

    We are now ready to insert data in the database.  We accomplish this by
    creating instances of ``User`` and ``Address`` classes, which have
    an ``__init__()`` method already as established automatically by the
    declarative mapping process.  We then pass them
    to the database using an object called a :ref:`Session <tutorial_executing_orm_session>`,
    which makes use of the :class:`_engine.Engine` to interact with the
    database.  The :meth:`_orm.Session.add_all` method is used here to add
    multiple objects at once, and the :meth:`_orm.Session.commit` method
    will be used to :ref:`flush <session_flushing>` any pending changes to the
    database and then :ref:`commit <session_committing>` the current database
    transaction, which is always in progress whenever the :class:`_orm.Session`
    is used:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import Session

        >>> with Session(engine) as session:
        ...     spongebob = User(
        ...         name="spongebob",
        ...         fullname="Spongebob Squarepants",
        ...         addresses=[Address(email_address="spongebob@sqlalchemy.org")],
        ...     )
        ...     sandy = User(
        ...         name="sandy",
        ...         fullname="Sandy Cheeks",
        ...         addresses=[
        ...             Address(email_address="sandy@sqlalchemy.org"),
        ...             Address(email_address="sandy@squirrelpower.org"),
        ...         ],
        ...     )
        ...     patrick = User(name="patrick", fullname="Patrick Star")
        ...
        ...     session.add_all([spongebob, sandy, patrick])
        ...
        ...     session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('spongebob', 'Spongebob Squarepants')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('sandy', 'Sandy Cheeks')
        INSERT INTO user_account (name, fullname) VALUES (?, ?) RETURNING id
        [...] ('patrick', 'Patrick Star')
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('spongebob@sqlalchemy.org', 1)
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('sandy@sqlalchemy.org', 2)
        INSERT INTO address (email_address, user_id) VALUES (?, ?) RETURNING id
        [...] ('sandy@squirrelpower.org', 2)
        COMMIT


    .. tip::

        It's recommended that the :class:`_orm.Session` be used in context
        manager style as above, that is, using the Python ``with:`` statement.
        The :class:`_orm.Session` object represents active database resources
        so it's good to make sure it's closed out when a series of operations
        are completed.  In the next section, we'll keep a :class:`_orm.Session`
        opened just for illustration purposes.

    Basics on creating a :class:`_orm.Session` are at
    :ref:`tutorial_executing_orm_session` and more at :ref:`session_basics`.

    Then, some varieties of basic persistence operations are introduced
    at :ref:`tutorial_inserting_orm`.

简单 SELECT
--------------

Simple SELECT

.. tab:: 中文

    在数据库中有一些行后，这里是发出SELECT语句以加载一些对象的最简单形式。要创建SELECT语句，我们使用 :func:`_sql.select` 函数创建一个新的 :class:`_sql.Select` 对象，然后使用 :class:`_orm.Session` 调用它。在查询ORM对象时，经常有用的方法是 :meth:`_orm.Session.scalars` 方法，它将返回一个 :class:`_result.ScalarResult` 对象，该对象将迭代我们选择的ORM对象：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select

        >>> session = Session(engine)

        >>> stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))

        >>> for user in session.scalars(stmt):
        ...     print(user)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name IN (?, ?)
        [...] ('spongebob', 'sandy'){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')


    上面的查询还使用了 :meth:`_sql.Select.where` 方法来添加WHERE条件，并且还使用了所有SQLAlchemy列类构造的一部分 :meth:`_sql.ColumnOperators.in_` 方法来使用SQL IN操作符。

    有关如何选择对象和单个列的更多详细信息，请参见 :ref:`tutorial_selecting_orm_entities` 。

.. tab:: 英文

    With some rows in the database, here's the simplest form of emitting a SELECT
    statement to load some objects. To create SELECT statements, we use the
    :func:`_sql.select` function to create a new :class:`_sql.Select` object, which
    we then invoke using a :class:`_orm.Session`. The method that is often useful
    when querying for ORM objects is the :meth:`_orm.Session.scalars` method, which
    will return a :class:`_result.ScalarResult` object that will iterate through
    the ORM objects we've selected:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select

        >>> session = Session(engine)

        >>> stmt = select(User).where(User.name.in_(["spongebob", "sandy"]))

        >>> for user in session.scalars(stmt):
        ...     print(user)
        {execsql}BEGIN (implicit)
        SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name IN (?, ?)
        [...] ('spongebob', 'sandy'){stop}
        User(id=1, name='spongebob', fullname='Spongebob Squarepants')
        User(id=2, name='sandy', fullname='Sandy Cheeks')


    The above query also made use of the :meth:`_sql.Select.where` method
    to add WHERE criteria, and also used the :meth:`_sql.ColumnOperators.in_`
    method that's part of all SQLAlchemy column-like constructs to use the
    SQL IN operator.

    More detail on how to select objects and individual columns is at
    :ref:`tutorial_selecting_orm_entities`.

使用 JOIN 进行 SELECT
-----------------

SELECT with JOIN

.. tab:: 中文

    在SQL中，JOIN关键字是同时查询多个表的主要方式。:class:`_sql.Select`构造使用 :meth:`_sql.Select.join` 方法来创建连接：

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "sandy")
        ...     .where(Address.email_address == "sandy@sqlalchemy.org")
        ... )
        >>> sandy_address = session.scalars(stmt).one()
        {execsql}SELECT address.id, address.email_address, address.user_id
        FROM address JOIN user_account ON user_account.id = address.user_id
        WHERE user_account.name = ? AND address.email_address = ?
        [...] ('sandy', 'sandy@sqlalchemy.org')
        {stop}
        >>> sandy_address
        Address(id=2, email_address='sandy@sqlalchemy.org')

    上面的查询说明了多个WHERE条件如何自动用AND链接在一起，以及如何使用SQLAlchemy类列对象来创建“等式”比较，这使用了重载的Python方法 :meth:`_sql.ColumnOperators.__eq__` 来生成SQL条件对象。

    有关上述概念的更多背景信息，请参见 :ref:`tutorial_select_where_clause` 和 :ref:`tutorial_select_join`。

.. tab:: 英文

    It's very common to query amongst multiple tables at once, and in SQL
    the JOIN keyword is the primary way this happens.   The :class:`_sql.Select`
    construct creates joins using the :meth:`_sql.Select.join` method:

    .. sourcecode:: pycon+sql

        >>> stmt = (
        ...     select(Address)
        ...     .join(Address.user)
        ...     .where(User.name == "sandy")
        ...     .where(Address.email_address == "sandy@sqlalchemy.org")
        ... )
        >>> sandy_address = session.scalars(stmt).one()
        {execsql}SELECT address.id, address.email_address, address.user_id
        FROM address JOIN user_account ON user_account.id = address.user_id
        WHERE user_account.name = ? AND address.email_address = ?
        [...] ('sandy', 'sandy@sqlalchemy.org')
        {stop}
        >>> sandy_address
        Address(id=2, email_address='sandy@sqlalchemy.org')

    The above query illustrates multiple WHERE criteria which are automatically
    chained together using AND, as well as how to use SQLAlchemy column-like
    objects to create "equality" comparisons, which uses the overridden Python
    method :meth:`_sql.ColumnOperators.__eq__` to produce a SQL criteria object.

    Some more background on the concepts above are at
    :ref:`tutorial_select_where_clause` and :ref:`tutorial_select_join`.

进行更改
------------

Make Changes

.. tab:: 中文

    :class:`_orm.Session` 对象与我们的ORM映射类 ``User`` 和 ``Address`` 一起，自动跟踪对对象所做的更改，这些更改会在下次 :class:`_orm.Session` 刷新时发出SQL语句。下面，我们更改了与“sandy”关联的一个电子邮件地址，并向“patrick”添加了一个新电子邮件地址，在发出SELECT语句以检索“patrick”的行之后：

    .. sourcecode:: pycon+sql

        >>> stmt = select(User).where(User.name == "patrick")
        >>> patrick = session.scalars(stmt).one()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',)
        {stop}

        >>> patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,){stop}

        >>> sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

        >>> session.commit()
        {execsql}UPDATE address SET email_address=? WHERE address.id = ?
        [...] ('sandy_cheeks@sqlalchemy.org', 2)
        INSERT INTO address (email_address, user_id) VALUES (?, ?)
        [...] ('patrickstar@sqlalchemy.org', 3)
        COMMIT
        {stop}

    注意当我们访问 ``patrick.addresses`` 时，发出了一个SELECT语句。这被称为 :term:`延迟加载` 。关于使用更多或更少SQL访问相关项目的不同方式的背景信息，请参见 :ref:`tutorial_orm_loader_strategies`。

    有关ORM数据操作的详细演练，请参见 :ref:`tutorial_orm_data_manipulation`。

.. tab:: 英文

    The :class:`_orm.Session` object, in conjunction with our ORM-mapped classes
    ``User`` and ``Address``, automatically track changes to the objects as they
    are made, which result in SQL statements that will be emitted the next
    time the :class:`_orm.Session` flushes.   Below, we change one email
    address associated with "sandy", and also add a new email address to
    "patrick", after emitting a SELECT to retrieve the row for "patrick":

    .. sourcecode:: pycon+sql

        >>> stmt = select(User).where(User.name == "patrick")
        >>> patrick = session.scalars(stmt).one()
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        WHERE user_account.name = ?
        [...] ('patrick',)
        {stop}

        >>> patrick.addresses.append(Address(email_address="patrickstar@sqlalchemy.org"))
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,){stop}

        >>> sandy_address.email_address = "sandy_cheeks@sqlalchemy.org"

        >>> session.commit()
        {execsql}UPDATE address SET email_address=? WHERE address.id = ?
        [...] ('sandy_cheeks@sqlalchemy.org', 2)
        INSERT INTO address (email_address, user_id) VALUES (?, ?)
        [...] ('patrickstar@sqlalchemy.org', 3)
        COMMIT
        {stop}

    Notice when we accessed ``patrick.addresses``, a SELECT was emitted.  This is
    called a :term:`lazy load`.   Background on different ways to access related
    items using more or less SQL is introduced at :ref:`tutorial_orm_loader_strategies`.

    A detailed walkthrough on ORM data manipulation starts at
    :ref:`tutorial_orm_data_manipulation`.

进行一些删除
------------

Some Deletes

.. tab:: 中文

    所有事物都必须结束，就像我们的一些数据库行一样——这里是两种不同形式删除操作的快速演示，根据具体的用例，这两种形式都很重要。

    首先，我们将删除“sandy”用户的一个 ``Address`` 对象。当 :class:`_orm.Session` 下一次刷新时，这将导致行被删除。这种行为是我们在映射中配置的，称为 :ref:`级联删除 <cascade_delete>`。我们可以使用 :meth:`_orm.Session.get` 按主键获取 ``sandy`` 对象，然后处理该对象：

    .. sourcecode:: pycon+sql

        >>> sandy = session.get(User, 2)
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}

        >>> sandy.addresses.remove(sandy_address)
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (2,)

    上面的最后一个SELECT语句是 :term:`延迟加载` 操作，以便加载 ``sandy.addresses`` 集合，以便我们可以移除 ``sandy_address`` 成员。还有其他方法可以进行这一系列操作，不会发出这么多SQL。

    我们可以选择使用 :meth:`_orm.Session.flush` 方法发出DELETE SQL语句，而不提交事务：

    .. sourcecode:: pycon+sql

        >>> session.flush()
        {execsql}DELETE FROM address WHERE address.id = ?
        [...] (2,)

    接下来，我们将完全删除“patrick”用户。对于对象本身的顶级删除，我们使用 :meth:`_orm.Session.delete` 方法；此方法实际上并不执行删除，而是设置对象在下一次刷新时被删除。该操作还会根据我们配置的级联选项 :term:`级联` 到相关对象，在本例中为相关的``Address``对象：

    .. sourcecode:: pycon+sql

        >>> session.delete(patrick)
        {execsql}SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (3,)
        SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,)

    在这种特殊情况下，:meth:`_orm.Session.delete` 方法发出了两个SELECT语句，尽管它没有发出DELETE语句，这可能看起来令人惊讶。这是因为当方法检查对象时，发现 ``patrick`` 对象已经 :term:`过期` ，这是当我们上次调用 :meth:`_orm.Session.commit` 时发生的，发出的SQL是为了从新事务中重新加载行。这种过期是可选的，在正常使用中，我们通常会在不适用的情况下将其关闭。

    为了说明行被删除，下面是提交操作：

    .. sourcecode:: pycon+sql

        >>> session.commit()
        {execsql}DELETE FROM address WHERE address.id = ?
        [...] (4,)
        DELETE FROM user_account WHERE user_account.id = ?
        [...] (3,)
        COMMIT
        {stop}

    教程在 :ref:`tutorial_orm_deleting` 中讨论了ORM删除操作。对象过期的背景信息在 :ref:`session_expiring`；级联在 :ref:`unitofwork_cascades` 中有详细讨论。

.. tab:: 英文

    All things must come to an end, as is the case for some of our database
    rows - here's a quick demonstration of two different forms of deletion, both
    of which are important based on the specific use case.

    First we will remove one of the ``Address`` objects from the "sandy" user.
    When the :class:`_orm.Session` next flushes, this will result in the
    row being deleted.   This behavior is something that we configured in our
    mapping called the :ref:`delete cascade <cascade_delete>`.  We can get a handle to the ``sandy``
    object by primary key using :meth:`_orm.Session.get`, then work with the object:

    .. sourcecode:: pycon+sql

        >>> sandy = session.get(User, 2)
        {execsql}BEGIN (implicit)
        SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (2,){stop}

        >>> sandy.addresses.remove(sandy_address)
        {execsql}SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (2,)

    The last SELECT above was the :term:`lazy load` operation proceeding so that
    the ``sandy.addresses`` collection could be loaded, so that we could remove the
    ``sandy_address`` member.  There are other ways to go about this series
    of operations that won't emit as much SQL.

    We can choose to emit the DELETE SQL for what's set to be changed so far, without
    committing the transaction, using the
    :meth:`_orm.Session.flush` method:

    .. sourcecode:: pycon+sql

        >>> session.flush()
        {execsql}DELETE FROM address WHERE address.id = ?
        [...] (2,)

    Next, we will delete the "patrick" user entirely.  For a top-level delete of
    an object by itself, we use the :meth:`_orm.Session.delete` method; this
    method doesn't actually perform the deletion, but sets up the object
    to be deleted on the next flush.  The
    operation will also :term:`cascade` to related objects based on the cascade
    options that we configured, in this case, onto the related ``Address`` objects:

    .. sourcecode:: pycon+sql

        >>> session.delete(patrick)
        {execsql}SELECT user_account.id AS user_account_id, user_account.name AS user_account_name, user_account.fullname AS user_account_fullname
        FROM user_account
        WHERE user_account.id = ?
        [...] (3,)
        SELECT address.id AS address_id, address.email_address AS address_email_address, address.user_id AS address_user_id
        FROM address
        WHERE ? = address.user_id
        [...] (3,)

    The :meth:`_orm.Session.delete` method in this particular case emitted two
    SELECT statements, even though it didn't emit a DELETE, which might seem surprising.
    This is because when the method went to inspect the object, it turns out the
    ``patrick`` object was :term:`expired`, which happened when we last called upon
    :meth:`_orm.Session.commit`, and the SQL emitted was to re-load the rows
    from the new transaction.   This expiration is optional, and in normal
    use we will often be turning it off for situations where it doesn't apply well.

    To illustrate the rows being deleted, here's the commit:

    .. sourcecode:: pycon+sql

        >>> session.commit()
        {execsql}DELETE FROM address WHERE address.id = ?
        [...] (4,)
        DELETE FROM user_account WHERE user_account.id = ?
        [...] (3,)
        COMMIT
        {stop}

    The Tutorial discusses ORM deletion at :ref:`tutorial_orm_deleting`.
    Background on object expiration is at :ref:`session_expiring`; cascades
    are discussed in depth at :ref:`unitofwork_cascades`.

深入了解上述概念
---------------------------------

Learn the above concepts in depth

.. tab:: 中文

    对于新用户来说，上面的部分可能是一次旋风之旅。每一步中都有很多重要的概念没有涵盖。在快速了解事物外观之后，建议通读 :ref:`unified_tutorial`，以深入了解上面的内容。祝你好运！

.. tab:: 英文

    For a new user, the above sections were likely a whirlwind tour.   There's a
    lot of important concepts in each step above that weren't covered.   With a
    quick overview of what things look like, it's recommended to work through
    the :ref:`unified_tutorial` to gain a solid working knowledge of what's
    really going on above.  Good luck!





