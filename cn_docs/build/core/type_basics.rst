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
