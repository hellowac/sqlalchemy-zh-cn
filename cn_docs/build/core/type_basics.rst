类型层次结构
=====================

The Type Hierarchy

.. module:: sqlalchemy.types

.. tab:: 中文

    SQLAlchemy提供了大多数常见数据库数据类型的抽象，以及几种自定义数据类型的技术。

    数据库类型使用Python类表示，所有这些类最终都从称为 :class:`_types.TypeEngine` 的基本类型类扩展而来。有两类通用的数据类型，每类在类型层次结构中的表达方式不同。可以根据两种不同的命名约定来识别单个数据类型类使用的类别，分别是“CamelCase”和“大写字母”。

    .. seealso::

        :ref:`tutorial_core_metadata` - 在 :ref:`unified_tutorial` 中。说明了使用 :class:`_types.TypeEngine` 类型对象定义 :class:`_schema.Table` 元数据的最基础用法，并以教程形式介绍了类型对象的概念。

.. tab:: 英文

    SQLAlchemy provides abstractions for most common database data types,
    as well as several techniques for customization of datatypes.

    Database types are represented using Python classes, all of which ultimately
    extend from the base type class known as :class:`_types.TypeEngine`. There are
    two general categories of datatypes, each of which express themselves within
    the typing hierarchy in different ways. The category used by an individual
    datatype class can be identified based on the use of two different naming
    conventions, which are "CamelCase" and "UPPERCASE".

    .. seealso::

        :ref:`tutorial_core_metadata` - in the :ref:`unified_tutorial`.  Illustrates
        the most rudimental use of :class:`_types.TypeEngine` type objects to
        define :class:`_schema.Table` metadata and introduces the concept
        of type objects in tutorial form.

“驼峰式”数据类型
-------------------------

The "CamelCase" datatypes

.. tab:: 中文

    基础类型采用“驼峰命名（CamelCase）”的类名，例如 :class:`_types.String`、
    :class:`_types.Numeric`、:class:`_types.Integer` 和 :class:`_types.DateTime`。
    所有直接继承自 :class:`_types.TypeEngine` 的子类都是“驼峰命名”类型。
    这些“驼峰命名”类型在最大程度上是 **与数据库无关的**，这意味着它们可以在任何数据库后端中使用，
    并会根据目标后端的特性做出相应行为，以实现预期效果。

    一个简单直观的“驼峰命名”数据类型示例是 :class:`_types.String`。
    在大多数后端中，在 :ref:`表结构定义 <metadata_describing>` 中使用此数据类型
    通常会映射为目标数据库中的 ``VARCHAR`` 类型，用于在数据库与应用之间传递字符串值，
    如下所示的示例::

        from sqlalchemy import MetaData
        from sqlalchemy import Table, Column, Integer, String

        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("user_name", String, primary_key=True),
            Column("email_address", String(60)),
        )

    当在 :class:`_schema.Table` 定义或任意 SQL 表达式中使用某个 :class:`_types.TypeEngine` 类型时，
    如果该类型不需要任何参数，可以直接使用类名（即无需使用 ``()`` 实例化）。
    如果需要传参，比如上例中 ``"email_address"`` 列指定了长度参数 60，则需要实例化该类型。

    另一个体现更多后端特性行为的“驼峰命名”数据类型是 :class:`_types.Boolean`。
    不同于 :class:`_types.String`，后者代表的是所有数据库都支持的字符串类型，
    并非所有数据库都具备真正的“布尔”类型；
    有些使用整数或 BIT 值 0 和 1，有些支持布尔字面值 ``true`` 和 ``false``，而另一些则不支持。
    对于该类型，:class:`_types.Boolean` 在 PostgreSQL 上可能会渲染为 ``BOOLEAN``，
    在 MySQL 上可能为 ``BIT``，在 Oracle 上可能为 ``SMALLINT``。
    当通过该类型向数据库传递或接收数据时，会根据所用方言将 Python 的布尔值或数值进行解释。

    在大多数情况下，典型的 SQLAlchemy 应用会优先使用这些“驼峰命名”类型，
    因为它们通常具备更好的默认行为，并且能够自动适配各种数据库后端。

    “驼峰命名”数据类型的通用参考列表见下方链接：
    :ref:`types_generic`。


.. tab:: 英文

    The rudimental types have "CamelCase" names such as :class:`_types.String`,
    :class:`_types.Numeric`, :class:`_types.Integer`, and :class:`_types.DateTime`.
    All of the immediate subclasses of :class:`_types.TypeEngine` are
    "CamelCase" types. The "CamelCase" types are to the greatest degree possible
    **database agnostic**, meaning they can all be used on any database backend
    where they will behave in such a way as appropriate to that backend in order to
    produce the desired behavior.

    An example of a straightforward "CamelCase" datatype is :class:`_types.String`.
    On most backends, using this datatype in a
    :ref:`table specification <metadata_describing>` will correspond to the
    ``VARCHAR`` database type being used on the target backend, delivering string
    values to and from the database, as in the example below::

        from sqlalchemy import MetaData
        from sqlalchemy import Table, Column, Integer, String

        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("user_name", String, primary_key=True),
            Column("email_address", String(60)),
        )

    When using a particular :class:`_types.TypeEngine` class in a
    :class:`_schema.Table` definition or in any SQL expression overall, if no
    arguments are required it may be passed as the class itself, that is, without
    instantiating it with ``()``. If arguments are needed, such as the length
    argument of 60 in the ``"email_address"`` column above, the type may be
    instantiated.

    Another "CamelCase" datatype that expresses more backend-specific behavior
    is the :class:`_types.Boolean` datatype. Unlike :class:`_types.String`,
    which represents a string datatype that all databases have,
    not every backend has a real "boolean" datatype; some make use of integers
    or BIT values 0 and 1, some have boolean literal constants ``true`` and
    ``false`` while others dont.   For this datatype, :class:`_types.Boolean`
    may render ``BOOLEAN`` on a backend such as PostgreSQL, ``BIT`` on the
    MySQL backend and ``SMALLINT`` on Oracle Database.  As data is sent and
    received from the database using this type, based on the dialect in use it
    may be interpreting Python numeric or boolean values.

    The typical SQLAlchemy application will likely wish to use primarily
    "CamelCase" types in the general case, as they will generally provide the best
    basic behavior and be automatically portable to all backends.

    Reference for the general set of "CamelCase" datatypes is below at
    :ref:`types_generic`.

“大写”数据类型
-------------------------

The "UPPERCASE" datatypes

.. tab:: 中文

    与“驼峰命名”类型相对的是“全大写（UPPERCASE）”数据类型。
    这些类型总是从某个特定的“驼峰命名”类型继承而来，并始终表示一个 **精确** 的数据库类型。
    使用“全大写”类型时，其类型名称会被 **原样** 渲染，
    不考虑当前后端是否支持该类型。因此，在 SQLAlchemy 应用中使用“全大写”类型表明：
    该应用要求使用特定的数据库类型，这也意味着该应用（如果没有做额外处理）
    通常只能运行在那些支持该精确类型的后端上。
    例如， :class:`_types.VARCHAR`、 :class:`_types.NUMERIC`、 :class:`_types.INTEGER` 和
    :class:`_types.TIMESTAMP` 就是“全大写”类型，分别继承自前面提到的
    :class:`_types.String`、 :class:`_types.Numeric`、 :class:`_types.Integer` 和 :class:`_types.DateTime`。

    ``sqlalchemy.types`` 中包含的“全大写”类型是常见的 SQL 类型，通常至少在两个以上的数据库后端中可用。

    “全大写”数据类型的通用参考列表见下方链接：
    :ref:`types_sqlstandard`。

.. tab:: 英文

    In contrast to the "CamelCase" types are the "UPPERCASE" datatypes. These
    datatypes are always inherited from a particular "CamelCase" datatype, and
    always represent an **exact** datatype.   When using an "UPPERCASE" datatype,
    the name of the type is always rendered exactly as given, without regard for
    whether or not the current backend supports it.   Therefore the use
    of "UPPERCASE" types in a SQLAlchemy application indicates that specific
    datatypes are required, which then implies that the application would normally,
    without additional steps taken,
    be limited to those backends which use the type exactly as given.   Examples
    of UPPERCASE types include :class:`_types.VARCHAR`, :class:`_types.NUMERIC`,
    :class:`_types.INTEGER`, and :class:`_types.TIMESTAMP`, which inherit directly
    from the previously mentioned "CamelCase" types
    :class:`_types.String`,
    :class:`_types.Numeric`, :class:`_types.Integer`, and :class:`_types.DateTime`,
    respectively.

    The "UPPERCASE" datatypes that are part of ``sqlalchemy.types`` are common
    SQL types that typically expect to be available on at least two backends
    if not more.

    Reference for the general set of "UPPERCASE" datatypes is below at
    :ref:`types_sqlstandard`.



.. _types_vendor:

后端特定的“大写”数据类型
--------------------------------------

Backend-specific "UPPERCASE" datatypes

.. tab:: 中文

    大多数数据库还提供了其专有的数据类型，这些类型可能完全是数据库特有的，
    或者支持数据库特定的附加参数。
    对于这类类型，SQLAlchemy 的特定方言会提供 **后端专属** 的“全大写”数据类型，
    用于描述在其他后端中没有对应类型的 SQL 类型。
    例如，PostgreSQL 的 :class:`_postgresql.JSONB`、SQL Server 的 :class:`_mssql.IMAGE`，
    以及 MySQL 的 :class:`_mysql.TINYTEXT` 就是这样的类型。

    此外，某些特定后端还可能提供“全大写”类型的变种，这些变种在 ``sqlalchemy.types`` 中也有对应，
    但扩展了后端专用的参数。
    例如，在创建 MySQL 的字符串类型时，可以指定 ``charset`` 或 ``national`` 等 MySQL 专用参数，
    它们可以通过 MySQL 版本的 :class:`_mysql.VARCHAR` 来传入，
    这些参数分别对应于 :paramref:`_mysql.VARCHAR.charset` 和 :paramref:`_mysql.VARCHAR.national`。

    后端专用类型的 API 文档请参考各方言的文档，参见：
    :ref:`dialect_toplevel`。

.. tab:: 英文

    Most databases also have their own datatypes that
    are either fully specific to those databases, or add additional arguments
    that are specific to those databases.   For these datatypes, specific
    SQLAlchemy dialects provide **backend-specific** "UPPERCASE" datatypes, for a
    SQL type that has no analogue on other backends.  Examples of backend-specific
    uppercase datatypes include PostgreSQL's :class:`_postgresql.JSONB`, SQL Server's
    :class:`_mssql.IMAGE` and MySQL's :class:`_mysql.TINYTEXT`.

    Specific backends may also include "UPPERCASE" datatypes that extend the
    arguments available from that same "UPPERCASE" datatype as found in the
    ``sqlalchemy.types`` module. An example is when creating a MySQL string
    datatype, one might want to specify MySQL-specific arguments such as ``charset``
    or ``national``, which are available from the MySQL version
    of :class:`_mysql.VARCHAR` as the MySQL-only parameters
    :paramref:`_mysql.VARCHAR.charset` and :paramref:`_mysql.VARCHAR.national`.

    API documentation for backend-specific types are in the dialect-specific
    documentation, listed at :ref:`dialect_toplevel`.


.. _types_with_variant:

对多个后端使用“大写”和后端特定的类型
------------------------------------------------------------------

Using "UPPERCASE" and Backend-specific types for multiple backends

.. tab:: 中文

    回顾“全大写（UPPERCASE）”和“驼峰命名（CamelCase）”类型的存在，引出了一个自然的使用场景：
    如何仅在目标后端处于启用状态时，使用具有后端特定选项的“全大写”数据类型。
    为将与数据库无关的“驼峰命名”系统与后端特定的“全大写”系统结合起来，
    可以使用 :meth:`_types.TypeEngine.with_variant` 方法，将多个类型 **组合** 起来，
    以在特定后端上实现特定行为。

    例如，我们希望使用 :class:`_types.String` 数据类型，
    但在运行于 MySQL 或 MariaDB 上时，希望使用 MySQL 的 :class:`_mysql.VARCHAR` 类型，
    并指定其 :paramref:`_mysql.VARCHAR.charset` 参数，
    则可以通过 :meth:`_types.TypeEngine.with_variant` 实现如下::

        from sqlalchemy import MetaData
        from sqlalchemy import Table, Column, Integer, String
        from sqlalchemy.dialects.mysql import VARCHAR

        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("user_name", String(100), primary_key=True),
            Column(
                "bio",
                String(255).with_variant(VARCHAR(255, charset="utf8"), "mysql", "mariadb"),
            ),
        )

    在上述表结构定义中，``"bio"`` 列在所有后端中都会具备字符串行为。
    在大多数后端中，它将在 DDL 中被渲染为 ``VARCHAR``；
    但在 MySQL 与 MariaDB 中（即数据库 URL 以 ``mysql`` 或 ``mariadb`` 开头时），
    该列将被渲染为 ``VARCHAR(255) CHARACTER SET utf8``。

    .. seealso::

        :meth:`_types.TypeEngine.with_variant` - 更多用法示例与说明

.. tab:: 英文

    Reviewing the presence of "UPPERCASE" and "CamelCase" types leads to the natural
    use case of how to make use of "UPPERCASE" datatypes for backend-specific
    options, but only when that backend is in use.   To tie together the
    database-agnostic "CamelCase" and backend-specific "UPPERCASE" systems, one
    makes use of the :meth:`_types.TypeEngine.with_variant` method in order to
    **compose** types together to work with specific behaviors on specific backends.

    Such as, to use the :class:`_types.String` datatype, but when running on MySQL
    to make use of the :paramref:`_mysql.VARCHAR.charset` parameter of
    :class:`_mysql.VARCHAR` when the table is created on MySQL or MariaDB,
    :meth:`_types.TypeEngine.with_variant` may be used as below::

        from sqlalchemy import MetaData
        from sqlalchemy import Table, Column, Integer, String
        from sqlalchemy.dialects.mysql import VARCHAR

        metadata_obj = MetaData()

        user = Table(
            "user",
            metadata_obj,
            Column("user_name", String(100), primary_key=True),
            Column(
                "bio",
                String(255).with_variant(VARCHAR(255, charset="utf8"), "mysql", "mariadb"),
            ),
        )

    In the above table definition, the ``"bio"`` column will have string-behaviors
    on all backends. On most backends it will render in DDL as ``VARCHAR``. However
    on MySQL and MariaDB (indicated by database URLs that start with ``mysql`` or
    ``mariadb``), it will render as ``VARCHAR(255) CHARACTER SET utf8``.

    .. seealso::

        :meth:`_types.TypeEngine.with_variant` - additional usage examples and notes

.. _types_generic:

通用“驼峰式”类型
-------------------------

Generic "CamelCase" Types

.. tab:: 中文

    通用类型（Generic types）用于定义可以读取、写入并存储某种特定 Python 数据类型的列。
    当发出 ``CREATE TABLE`` 语句时，SQLAlchemy 会根据目标数据库选择最合适的列类型。
    如果希望完全控制在 ``CREATE TABLE`` 中发出的列类型（例如 ``VARCHAR``），
    请参阅 :ref:`types_sqlstandard` 以及本章的其他相关章节。

.. tab:: 英文

    Generic types specify a column that can read, write and store a
    particular type of Python data.  SQLAlchemy will choose the best
    database column type available on the target database when issuing a
    ``CREATE TABLE`` statement.  For complete control over which column
    type is emitted in ``CREATE TABLE``, such as ``VARCHAR`` see
    :ref:`types_sqlstandard` and the other sections of this chapter.

.. autoclass:: BigInteger
   :members:

.. autoclass:: Boolean
   :members:

.. autoclass:: Date
   :members:

.. autoclass:: DateTime
   :members:

.. autoclass:: Enum
  :members: __init__, create, drop

.. autoclass:: Double
   :members:

.. autoclass:: Float
  :members:

.. autoclass:: Integer
  :members:

.. autoclass:: Interval
  :members:

.. autoclass:: LargeBinary
  :members:

.. autoclass:: MatchType
  :members:

.. autoclass:: Numeric
  :members:

.. autoclass:: NumericCommon
  :members:

.. autoclass:: PickleType
  :members:

.. autoclass:: SchemaType
  :members:
  :undoc-members:

.. autoclass:: SmallInteger
  :members:

.. autoclass:: String
   :members:

.. autoclass:: Text
   :members:

.. autoclass:: Time
  :members:

.. autoclass:: Unicode
  :members:

.. autoclass:: UnicodeText
   :members:

.. autoclass:: Uuid
  :members:

.. _types_sqlstandard:

SQL 标准和多个供应商“大写”类型
--------------------------------------------------

SQL Standard and Multiple Vendor "UPPERCASE" Types

.. tab:: 中文

    这一类类型包括 SQL 标准中定义的类型，或那些可能在某些数据库后端中存在的类型。
    与“通用”类型不同的是，SQL 标准/多厂商类型 **不保证** 能在所有数据库后端上工作，
    它们只能在那些明确支持该类型名称的后端上生效。
    也就是说，当发出 ``CREATE TABLE`` 时，此类类型将始终原样输出其名称。

.. tab:: 英文

    This category of types refers to types that are either part of the
    SQL standard, or are potentially found within a subset of database backends.
    Unlike the "generic" types, the SQL standard/multi-vendor types have **no**
    guarantee of working on all backends, and will only work on those backends
    that explicitly support them by name.  That is, the type will always emit
    its exact name in DDL with ``CREATE TABLE`` is issued.


.. autoclass:: ARRAY
    :members: __init__, Comparator
    :member-order: bysource


.. autoclass:: BIGINT


.. autoclass:: BINARY


.. autoclass:: BLOB


.. autoclass:: BOOLEAN


.. autoclass:: CHAR


.. autoclass:: CLOB


.. autoclass:: DATE


.. autoclass:: DATETIME


.. autoclass:: DECIMAL

.. autoclass:: DOUBLE

.. autoclass:: DOUBLE_PRECISION

.. autoclass:: FLOAT


.. autoclass:: INT

.. autoclass:: JSON
    :members:


.. autoclass:: sqlalchemy.types.INTEGER


.. autoclass:: NCHAR


.. autoclass:: NVARCHAR


.. autoclass:: NUMERIC


.. autoclass:: REAL


.. autoclass:: SMALLINT


.. autoclass:: TEXT


.. autoclass:: TIME


.. autoclass:: TIMESTAMP
    :members:


.. autoclass:: UUID

.. autoclass:: VARBINARY


.. autoclass:: VARCHAR
