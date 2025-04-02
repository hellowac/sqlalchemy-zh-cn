.. _postgresql_toplevel:

PostgreSQL
==========

PostgreSQL

.. automodule:: sqlalchemy.dialects.postgresql.base

ARRAY 类型
-----------

ARRAY Types

.. tab:: 中文

    PostgreSQL方言支持数组，既可以作为多维列类型，也可以作为数组文字：

    * :class:`_postgresql.ARRAY` - ARRAY数据类型

    * :class:`_postgresql.array` - 数组文字

    * :func:`_postgresql.array_agg` - ARRAY_AGG SQL函数

    * :class:`_postgresql.aggregate_order_by` - PG的ORDER BY聚合函数语法的助手类。

.. tab:: 英文

    The PostgreSQL dialect supports arrays, both as multidimensional column types
    as well as array literals:

    * :class:`_postgresql.ARRAY` - ARRAY datatype

    * :class:`_postgresql.array` - array literal

    * :func:`_postgresql.array_agg` - ARRAY_AGG SQL function

    * :class:`_postgresql.aggregate_order_by` - helper for PG's ORDER BY aggregate function syntax.

.. _postgresql_json_types:

JSON 类型
----------

JSON Types

.. tab:: 中文

    PostgreSQL方言支持JSON和JSONB数据类型，包括psycopg2的原生支持以及所有PostgreSQL特殊运算符的支持：

.. tab:: 英文

    The PostgreSQL dialect supports both JSON and JSONB datatypes, including
    psycopg2's native support and support for all of PostgreSQL's special
    operators:

* :class:`_postgresql.JSON`

* :class:`_postgresql.JSONB`

* :class:`_postgresql.JSONPATH`

HSTORE 类型
-----------

HSTORE Type

.. tab:: 中文

    PostgreSQL的HSTORE类型以及hstore文字都受到支持：

    * :class:`_postgresql.HSTORE` - HSTORE数据类型

    * :class:`_postgresql.hstore` - hstore文字

.. tab:: 英文

    The PostgreSQL HSTORE type as well as hstore literals are supported:

    * :class:`_postgresql.HSTORE` - HSTORE datatype

    * :class:`_postgresql.hstore` - hstore literal

ENUM 类型
----------

ENUM Types

.. tab:: 中文

    PostgreSQL具有一个独立创建的TYPE结构，用于实现枚举类型。这种方法在SQLAlchemy方面引入了在何时应该创建和删除此类型的显著复杂性。类型对象也是一个独立的可反映实体。应参考以下章节：

    * :class:`_postgresql.ENUM` - ENUM的DDL和类型支持。

    * :meth:`.PGInspector.get_enums` - 检索当前ENUM类型的列表

    * :meth:`.postgresql.ENUM.create` , :meth:`.postgresql.ENUM.drop` - ENUM的单独CREATE和DROP命令。

.. tab:: 英文

    PostgreSQL has an independently creatable TYPE structure which is used
    to implement an enumerated type.   This approach introduces significant
    complexity on the SQLAlchemy side in terms of when this type should be
    CREATED and DROPPED.   The type object is also an independently reflectable
    entity.   The following sections should be consulted:

    * :class:`_postgresql.ENUM` - DDL and typing support for ENUM.

    * :meth:`.PGInspector.get_enums` - retrieve a listing of current ENUM types

    * :meth:`.postgresql.ENUM.create` , :meth:`.postgresql.ENUM.drop` - individual CREATE and DROP commands for ENUM.

.. _postgresql_array_of_enum:

将 ENUM 与 ARRAY 结合使用
^^^^^^^^^^^^^^^^^^^^^

Using ENUM with ARRAY

.. tab:: 中文

    ENUM和ARRAY的组合目前不直接受后端DBAPI的支持。在SQLAlchemy 1.3.17之前，需要一个特殊的解决方法来允许这种组合工作，如下所述。

    .. sourcecode:: python

        from sqlalchemy import TypeDecorator
        from sqlalchemy.dialects.postgresql import ARRAY


        class ArrayOfEnum(TypeDecorator):
            impl = ARRAY

            def bind_expression(self, bindvalue):
                return sa.cast(bindvalue, self)

            def result_processor(self, dialect, coltype):
                super_rp = super(ArrayOfEnum, self).result_processor(dialect, coltype)

                def handle_raw_string(value):
                    inner = re.match(r"^{(.*)}$", value).group(1)
                    return inner.split(",") if inner else []

                def process(value):
                    if value is None:
                        return None
                    return super_rp(handle_raw_string(value))

                return process

    例如::

        Table(
            "mydata",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", ArrayOfEnum(ENUM("a", "b", "c", name="myenum"))),
        )

    这种类型不包含为内置类型，因为它与在新版本中突然决定直接支持ENUM的ARRAY的DBAPI不兼容。

.. tab:: 英文

    The combination of ENUM and ARRAY is not directly supported by backend
    DBAPIs at this time.   Prior to SQLAlchemy 1.3.17, a special workaround
    was needed in order to allow this combination to work, described below.

    .. sourcecode:: python

        from sqlalchemy import TypeDecorator
        from sqlalchemy.dialects.postgresql import ARRAY


        class ArrayOfEnum(TypeDecorator):
            impl = ARRAY

            def bind_expression(self, bindvalue):
                return sa.cast(bindvalue, self)

            def result_processor(self, dialect, coltype):
                super_rp = super(ArrayOfEnum, self).result_processor(dialect, coltype)

                def handle_raw_string(value):
                    inner = re.match(r"^{(.*)}$", value).group(1)
                    return inner.split(",") if inner else []

                def process(value):
                    if value is None:
                        return None
                    return super_rp(handle_raw_string(value))

                return process

    E.g.::

        Table(
            "mydata",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", ArrayOfEnum(ENUM("a", "b", "c", name="myenum"))),
        )

    This type is not included as a built-in type as it would be incompatible
    with a DBAPI that suddenly decides to support ARRAY of ENUM directly in
    a new version.

.. _postgresql_array_of_json:

将 JSON/JSONB 与 ARRAY 结合使用
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using JSON/JSONB with ARRAY

.. tab:: 中文

    类似于使用ENUM，在SQLAlchemy 1.3.17之前，对于JSON/JSONB的ARRAY，我们需要渲染适当的CAST。当前的psycopg2驱动程序正确处理结果集，无需任何特殊步骤。

    .. sourcecode:: python

        class CastingArray(ARRAY):
            def bind_expression(self, bindvalue):
                return sa.cast(bindvalue, self)

    例如::

        Table(
            "mydata",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", CastingArray(JSONB)),
        )

.. tab:: 英文

    Similar to using ENUM, prior to SQLAlchemy 1.3.17, for an ARRAY of JSON/JSONB
    we need to render the appropriate CAST.   Current psycopg2 drivers accommodate
    the result set correctly without any special steps.

    .. sourcecode:: python

        class CastingArray(ARRAY):
            def bind_expression(self, bindvalue):
                return sa.cast(bindvalue, self)

    E.g.::

        Table(
            "mydata",
            metadata,
            Column("id", Integer, primary_key=True),
            Column("data", CastingArray(JSONB)),
        )

.. _postgresql_ranges:

范围和多范围类型
--------------------------

Range and Multirange Types

.. tab:: 中文

    PostgreSQL范围和多范围类型支持psycopg、pg8000和asyncpg方言；psycopg2方言仅支持范围类型。

    .. versionadded:: 2.0.17 
        
        为pg8000方言添加了范围和多范围支持。需要pg8000 1.29.8或更高版本。

    传递到数据库的数据值可以作为字符串值传递，也可以使用 :class:`_postgresql.Range` 数据对象传递。

    .. versionadded:: 2.0 
        
        添加了用于指示范围的后端无关的 :class:`_postgresql.Range` 对象。不再公开特定于``psycopg2``的范围类，仅由该特定方言内部使用。

    例如，使用 :class:`_postgresql.TSRANGE` 数据类型的完全类型化模型示例::

        from datetime import datetime

        from sqlalchemy.dialects.postgresql import Range
        from sqlalchemy.dialects.postgresql import TSRANGE
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class RoomBooking(Base):
            __tablename__ = "room_booking"

            id: Mapped[int] = mapped_column(primary_key=True)
            room: Mapped[str]
            during: Mapped[Range[datetime]] = mapped_column(TSRANGE)

    要表示上述``during``列的数据，:class:`_postgresql.Range` 类型是一个简单的数据类，将表示范围的边界。下面说明了如何将一行插入到上述``room_booking``表中::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        engine = create_engine("postgresql+psycopg://scott:tiger@pg14/dbname")

        Base.metadata.create_all(engine)

        with Session(engine) as session:
            booking = RoomBooking(
                room="101", during=Range(datetime(2013, 3, 23), datetime(2013, 3, 25))
            )
            session.add(booking)
            session.commit()

    从任何范围列中选择也将返回 :class:`_postgresql.Range` 对象，如下所示::

        from sqlalchemy import select

        with Session(engine) as session:
            for row in session.execute(select(RoomBooking.during)):
                print(row)

    可用的范围数据类型如下：

.. tab:: 英文

    PostgreSQL range and multirange types are supported for the
    psycopg, pg8000 and asyncpg dialects; the psycopg2 dialect supports the
    range types only.

    .. versionadded:: 2.0.17 Added range and multirange support for the pg8000
    dialect.  pg8000 1.29.8 or greater is required.

    Data values being passed to the database may be passed as string
    values or by using the :class:`_postgresql.Range` data object.

    .. versionadded:: 2.0  Added the backend-agnostic :class:`_postgresql.Range`
    object used to indicate ranges.  The ``psycopg2``-specific range classes
    are no longer exposed and are only used internally by that particular
    dialect.

    E.g. an example of a fully typed model using the
    :class:`_postgresql.TSRANGE` datatype::

        from datetime import datetime

        from sqlalchemy.dialects.postgresql import Range
        from sqlalchemy.dialects.postgresql import TSRANGE
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class RoomBooking(Base):
            __tablename__ = "room_booking"

            id: Mapped[int] = mapped_column(primary_key=True)
            room: Mapped[str]
            during: Mapped[Range[datetime]] = mapped_column(TSRANGE)

    To represent data for the ``during`` column above, the :class:`_postgresql.Range`
    type is a simple dataclass that will represent the bounds of the range.
    Below illustrates an INSERT of a row into the above ``room_booking`` table::

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session

        engine = create_engine("postgresql+psycopg://scott:tiger@pg14/dbname")

        Base.metadata.create_all(engine)

        with Session(engine) as session:
            booking = RoomBooking(
                room="101", during=Range(datetime(2013, 3, 23), datetime(2013, 3, 25))
            )
            session.add(booking)
            session.commit()

    Selecting from any range column will also return :class:`_postgresql.Range`
    objects as indicated::

        from sqlalchemy import select

        with Session(engine) as session:
            for row in session.execute(select(RoomBooking.during)):
                print(row)

    The available range datatypes are as follows:

* :class:`_postgresql.INT4RANGE`
* :class:`_postgresql.INT8RANGE`
* :class:`_postgresql.NUMRANGE`
* :class:`_postgresql.DATERANGE`
* :class:`_postgresql.TSRANGE`
* :class:`_postgresql.TSTZRANGE`

.. autoclass:: sqlalchemy.dialects.postgresql.Range
    :members:

多范围
^^^^^^^^^^^

Multiranges

.. tab:: 中文

    Multiranges在PostgreSQL 14及以上版本中受支持。SQLAlchemy的多范围数据类型处理 :class:`_postgresql.Range` 类型的列表。

    Multiranges仅支持psycopg、asyncpg和pg8000方言。SQLAlchemy的默认 ``postgresql`` 方言psycopg2不支持多范围数据类型。

    .. versionadded:: 2.0 
        
        添加了对MULTIRANGE数据类型的支持。SQLAlchemy将多范围值表示为 :class:`_postgresql.Range` 对象的列表。

    .. versionadded:: 2.0.17 
        
        为pg8000方言添加了多范围支持。需要pg8000 1.29.8或更高版本。

    .. versionadded:: 2.0.26 
        
        添加了 :class:`_postgresql.MultiRange` 序列。

    下面的示例说明了 :class:`_postgresql.TSMULTIRANGE` 数据类型的使用::

        from datetime import datetime
        from typing import List

        from sqlalchemy.dialects.postgresql import Range
        from sqlalchemy.dialects.postgresql import TSMULTIRANGE
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class EventCalendar(Base):
            __tablename__ = "event_calendar"

            id: Mapped[int] = mapped_column(primary_key=True)
            event_name: Mapped[str]
            added: Mapped[datetime]
            in_session_periods: Mapped[List[Range[datetime]]] = mapped_column(TSMULTIRANGE)

    说明插入和选择记录::

        from sqlalchemy import create_engine
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        engine = create_engine("postgresql+psycopg://scott:tiger@pg14/test")

        Base.metadata.create_all(engine)

        with Session(engine) as session:
            calendar = EventCalendar(
                event_name="SQLAlchemy Tutorial Sessions",
                in_session_periods=[
                    Range(datetime(2013, 3, 23), datetime(2013, 3, 25)),
                    Range(datetime(2013, 4, 12), datetime(2013, 4, 15)),
                    Range(datetime(2013, 5, 9), datetime(2013, 5, 12)),
                ],
            )
            session.add(calendar)
            session.commit()

            for multirange in session.scalars(select(EventCalendar.in_session_periods)):
                for range_ in multirange:
                    print(f"Start: {range_.lower}  End: {range_.upper}")

    .. note:: 
        
        在上述示例中，ORM处理的 :class:`_postgresql.Range` 类型列表不会自动检测特定列表值的原地更改；要使用ORM更新列表值，可以重新分配一个新列表给该属性，或者使用 :class:`.MutableList` 类型修改器。有关背景信息，请参见章节 :ref:`mutable_toplevel`。

.. tab:: 英文

    Multiranges are supported by PostgreSQL 14 and above.  SQLAlchemy's
    multirange datatypes deal in lists of :class:`_postgresql.Range` types.

    Multiranges are supported on the psycopg, asyncpg, and pg8000 dialects
    **only**.  The psycopg2 dialect, which is SQLAlchemy's default ``postgresql``
    dialect, **does not** support multirange datatypes.

    .. versionadded:: 2.0 
        
        Added support for MULTIRANGE datatypes. SQLAlchemy represents a multirange value as a list of :class:`_postgresql.Range` objects.

    .. versionadded:: 2.0.17 
        
        Added multirange support for the pg8000 dialect. pg8000 1.29.8 or greater is required.

    .. versionadded:: 2.0.26 
        
        :class:`_postgresql.MultiRange` sequence added.

    The example below illustrates use of the :class:`_postgresql.TSMULTIRANGE`
    datatype::

        from datetime import datetime
        from typing import List

        from sqlalchemy.dialects.postgresql import Range
        from sqlalchemy.dialects.postgresql import TSMULTIRANGE
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class EventCalendar(Base):
            __tablename__ = "event_calendar"

            id: Mapped[int] = mapped_column(primary_key=True)
            event_name: Mapped[str]
            added: Mapped[datetime]
            in_session_periods: Mapped[List[Range[datetime]]] = mapped_column(TSMULTIRANGE)

    Illustrating insertion and selecting of a record::

        from sqlalchemy import create_engine
        from sqlalchemy import select
        from sqlalchemy.orm import Session

        engine = create_engine("postgresql+psycopg://scott:tiger@pg14/test")

        Base.metadata.create_all(engine)

        with Session(engine) as session:
            calendar = EventCalendar(
                event_name="SQLAlchemy Tutorial Sessions",
                in_session_periods=[
                    Range(datetime(2013, 3, 23), datetime(2013, 3, 25)),
                    Range(datetime(2013, 4, 12), datetime(2013, 4, 15)),
                    Range(datetime(2013, 5, 9), datetime(2013, 5, 12)),
                ],
            )
            session.add(calendar)
            session.commit()

            for multirange in session.scalars(select(EventCalendar.in_session_periods)):
                for range_ in multirange:
                    print(f"Start: {range_.lower}  End: {range_.upper}")

    .. note:: 
        
        In the above example, the list of :class:`_postgresql.Range` types
        as handled by the ORM will not automatically detect in-place changes to
        a particular list value; to update list values with the ORM, either re-assign
        a new list to the attribute, or use the :class:`.MutableList`
        type modifier.  See the section :ref:`mutable_toplevel` for background.

.. _postgresql_multirange_list_use:

使用多范围序列推断多范围类型
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Use of a MultiRange sequence to infer the multirange type

.. tab:: 中文

    在不指定类型的情况下使用多范围作为文字时，可以使用实用程序 :class:`_postgresql.MultiRange` 序列::

        from sqlalchemy import literal
        from sqlalchemy.dialects.postgresql import MultiRange

        with Session(engine) as session:
            stmt = select(EventCalendar).where(
                EventCalendar.added.op("<@")(
                    MultiRange(
                        [
                            Range(datetime(2023, 1, 1), datetime(2023, 3, 31)),
                            Range(datetime(2023, 7, 1), datetime(2023, 9, 30)),
                        ]
                    )
                )
            )
            in_range = session.execute(stmt).all()

        with engine.connect() as conn:
            row = conn.scalar(select(literal(MultiRange([Range(2, 4)]))))
            print(f"{row.lower} -> {row.upper}")

    使用简单的 ``list`` 而不是 :class:`_postgresql.MultiRange` 将需要手动将文字值的类型设置为适当的多范围类型。

    .. versionadded:: 2.0.26 :class:`_postgresql.MultiRange` 序列添加。

    可用的多范围数据类型如下：

    * :class:`_postgresql.INT4MULTIRANGE`
    * :class:`_postgresql.INT8MULTIRANGE`
    * :class:`_postgresql.NUMMULTIRANGE`
    * :class:`_postgresql.DATEMULTIRANGE`
    * :class:`_postgresql.TSMULTIRANGE`
    * :class:`_postgresql.TSTZMULTIRANGE`

.. tab:: 英文

    When using a multirange as a literal without specifying the type
    the utility :class:`_postgresql.MultiRange` sequence can be used::

        from sqlalchemy import literal
        from sqlalchemy.dialects.postgresql import MultiRange

        with Session(engine) as session:
            stmt = select(EventCalendar).where(
                EventCalendar.added.op("<@")(
                    MultiRange(
                        [
                            Range(datetime(2023, 1, 1), datetime(2013, 3, 31)),
                            Range(datetime(2023, 7, 1), datetime(2013, 9, 30)),
                        ]
                    )
                )
            )
            in_range = session.execute(stmt).all()

        with engine.connect() as conn:
            row = conn.scalar(select(literal(MultiRange([Range(2, 4)]))))
            print(f"{row.lower} -> {row.upper}")

    Using a simple ``list`` instead of :class:`_postgresql.MultiRange` would require
    manually setting the type of the literal value to the appropriate multirange type.

    .. versionadded:: 2.0.26 :class:`_postgresql.MultiRange` sequence added.

    The available multirange datatypes are as follows:

    * :class:`_postgresql.INT4MULTIRANGE`
    * :class:`_postgresql.INT8MULTIRANGE`
    * :class:`_postgresql.NUMMULTIRANGE`
    * :class:`_postgresql.DATEMULTIRANGE`
    * :class:`_postgresql.TSMULTIRANGE`
    * :class:`_postgresql.TSTZMULTIRANGE`

.. _postgresql_network_datatypes:

网络数据类型
------------------

Network Data Types

.. tab:: 中文

    包含的网络数据类型有 :class:`_postgresql.INET`，:class:`_postgresql.CIDR`，:class:`_postgresql.MACADDR`。

    对于 :class:`_postgresql.INET` 和 :class:`_postgresql.CIDR` 数据类型，有条件支持这些数据类型发送和检索Python ``ipaddress`` 对象，包括 ``ipaddress.IPv4Network``， ``ipaddress.IPv6Network`` ， ``ipaddress.IPv4Address`` ， ``ipaddress.IPv6Address`` 。此支持目前是 **DBAPI本身的默认行为，并且因DBAPI而异。SQLAlchemy尚未实现自己的网络地址转换逻辑**。

    * :ref:`postgresql_psycopg` 和 :ref:`postgresql_asyncpg` 完全支持这些数据类型；默认情况下，来自 ``ipaddress`` 系列的对象会在行中返回。
    * :ref:`postgresql_psycopg2` 方言仅发送和接收字符串。
    * :ref:`postgresql_pg8000` 方言支持 :class:`_postgresql.INET` 数据类型的 ``ipaddress.IPv4Address`` 和 ``ipaddress.IPv6Address`` 对象，但对 :class:`_postgresql.CIDR` 类型使用字符串。

    要 **将所有上述DBAPI标准化为只返回字符串**，请使用 ``native_inet_types`` 参数，并传递值 ``False`` ::

        e = create_engine(
            "postgresql+psycopg://scott:tiger@host/dbname", native_inet_types=False
        )

    使用上述参数， ``psycopg``、 ``asyncpg`` 和 ``pg8000`` 方言将禁用DBAPI对这些类型的适配，并仅返回字符串，匹配旧的 ``psycopg2`` 方言的行为。

    该参数也可以设置为 ``True`` ，此时对于那些不支持或尚未完全支持将行转换为Python ``ipaddress`` 数据类型的后端（目前是psycopg2和pg8000），将引发 ``NotImplementedError`` 。

.. tab:: 英文

    The included networking datatypes are :class:`_postgresql.INET`,
    :class:`_postgresql.CIDR`, :class:`_postgresql.MACADDR`.

    For :class:`_postgresql.INET` and :class:`_postgresql.CIDR` datatypes,
    conditional support is available for these datatypes to send and retrieve
    Python ``ipaddress`` objects including ``ipaddress.IPv4Network``,
    ``ipaddress.IPv6Network``, ``ipaddress.IPv4Address``,
    ``ipaddress.IPv6Address``.  This support is currently **the default behavior of
    the DBAPI itself, and varies per DBAPI.  SQLAlchemy does not yet implement its
    own network address conversion logic**.

    * The :ref:`postgresql_psycopg` and :ref:`postgresql_asyncpg` support these
    datatypes fully; objects from the ``ipaddress`` family are returned in rows
    by default.
    * The :ref:`postgresql_psycopg2` dialect only sends and receives strings.
    * The :ref:`postgresql_pg8000` dialect supports ``ipaddress.IPv4Address`` and
    ``ipaddress.IPv6Address`` objects for the :class:`_postgresql.INET` datatype,
    but uses strings for :class:`_postgresql.CIDR` types.

    To **normalize all the above DBAPIs to only return strings**, use the
    ``native_inet_types`` parameter, passing a value of ``False``::

        e = create_engine(
            "postgresql+psycopg://scott:tiger@host/dbname", native_inet_types=False
        )

    With the above parameter, the ``psycopg``, ``asyncpg`` and ``pg8000`` dialects
    will disable the DBAPI's adaptation of these types and will return only strings,
    matching the behavior of the older ``psycopg2`` dialect.

    The parameter may also be set to ``True``, where it will have the effect of
    raising ``NotImplementedError`` for those backends that don't support, or
    don't yet fully support, conversion of rows to Python ``ipaddress`` datatypes
    (currently psycopg2 and pg8000).

.. versionadded:: 2.0.18 - added the ``native_inet_types`` parameter.

PostgreSQL 数据类型
---------------------

PostgreSQL Data Types

.. tab:: 中文

    与所有SQLAlchemy方言一样，所有已知对PostgreSQL有效的UPPERCASE类型都可以从顶级方言中导入，无论它们是来自 :mod:`sqlalchemy.types` 还是来自本地方言::

        from sqlalchemy.dialects.postgresql import (
            ARRAY,
            BIGINT,
            BIT,
            BOOLEAN,
            BYTEA,
            CHAR,
            CIDR,
            CITEXT,
            DATE,
            DATEMULTIRANGE,
            DATERANGE,
            DOMAIN,
            DOUBLE_PRECISION,
            ENUM,
            FLOAT,
            HSTORE,
            INET,
            INT4MULTIRANGE,
            INT4RANGE,
            INT8MULTIRANGE,
            INT8RANGE,
            INTEGER,
            INTERVAL,
            JSON,
            JSONB,
            JSONPATH,
            MACADDR,
            MACADDR8,
            MONEY,
            NUMERIC,
            NUMMULTIRANGE,
            NUMRANGE,
            OID,
            REAL,
            REGCLASS,
            REGCONFIG,
            SMALLINT,
            TEXT,
            TIME,
            TIMESTAMP,
            TSMULTIRANGE,
            TSQUERY,
            TSRANGE,
            TSTZMULTIRANGE,
            TSTZRANGE,
            TSVECTOR,
            UUID,
            VARCHAR,
        )

    特定于PostgreSQL或具有PostgreSQL特定构造参数的类型如下：

.. tab:: 英文

    As with all SQLAlchemy dialects, all UPPERCASE types that are known to be
    valid with PostgreSQL are importable from the top level dialect, whether
    they originate from :mod:`sqlalchemy.types` or from the local dialect::

        from sqlalchemy.dialects.postgresql import (
            ARRAY,
            BIGINT,
            BIT,
            BOOLEAN,
            BYTEA,
            CHAR,
            CIDR,
            CITEXT,
            DATE,
            DATEMULTIRANGE,
            DATERANGE,
            DOMAIN,
            DOUBLE_PRECISION,
            ENUM,
            FLOAT,
            HSTORE,
            INET,
            INT4MULTIRANGE,
            INT4RANGE,
            INT8MULTIRANGE,
            INT8RANGE,
            INTEGER,
            INTERVAL,
            JSON,
            JSONB,
            JSONPATH,
            MACADDR,
            MACADDR8,
            MONEY,
            NUMERIC,
            NUMMULTIRANGE,
            NUMRANGE,
            OID,
            REAL,
            REGCLASS,
            REGCONFIG,
            SMALLINT,
            TEXT,
            TIME,
            TIMESTAMP,
            TSMULTIRANGE,
            TSQUERY,
            TSRANGE,
            TSTZMULTIRANGE,
            TSTZRANGE,
            TSVECTOR,
            UUID,
            VARCHAR,
        )

    Types which are specific to PostgreSQL, or have PostgreSQL-specific
    construction arguments, are as follows:

.. note: where :noindex: is used, indicates a type that is not redefined
   in the dialect module, just imported from sqltypes.  this avoids warnings
   in the sphinx build

.. currentmodule:: sqlalchemy.dialects.postgresql

.. autoclass:: sqlalchemy.dialects.postgresql.AbstractRange
    :members: comparator_factory

.. autoclass:: sqlalchemy.dialects.postgresql.AbstractSingleRange

.. autoclass:: sqlalchemy.dialects.postgresql.AbstractMultiRange


.. autoclass:: ARRAY
    :members: __init__, Comparator
    :member-order: bysource

.. autoclass:: BIT

.. autoclass:: BYTEA
    :members: __init__

.. autoclass:: CIDR

.. autoclass:: CITEXT

.. autoclass:: DOMAIN
    :members: __init__, create, drop

.. autoclass:: DOUBLE_PRECISION
    :members: __init__
    :noindex:


.. autoclass:: ENUM
    :members: __init__, create, drop


.. autoclass:: HSTORE
    :members:


.. autoclass:: INET

.. autoclass:: INTERVAL
    :members: __init__

.. autoclass:: JSON
    :members:

.. autoclass:: JSONB
    :members:

.. autoclass:: JSONPATH

.. autoclass:: MACADDR

.. autoclass:: MACADDR8

.. autoclass:: MONEY

.. autoclass:: OID

.. autoclass:: REAL
    :members: __init__
    :noindex:


.. autoclass:: REGCONFIG

.. autoclass:: REGCLASS

.. autoclass:: TIMESTAMP
    :members: __init__

.. autoclass:: TIME
    :members: __init__

.. autoclass:: TSQUERY

.. autoclass:: TSVECTOR

.. autoclass:: UUID
    :members: __init__
    :noindex:


.. autoclass:: INT4RANGE


.. autoclass:: INT8RANGE


.. autoclass:: NUMRANGE


.. autoclass:: DATERANGE


.. autoclass:: TSRANGE


.. autoclass:: TSTZRANGE


.. autoclass:: INT4MULTIRANGE


.. autoclass:: INT8MULTIRANGE


.. autoclass:: NUMMULTIRANGE


.. autoclass:: DATEMULTIRANGE


.. autoclass:: TSMULTIRANGE


.. autoclass:: TSTZMULTIRANGE


.. autoclass:: MultiRange


PostgreSQL SQL 元素和函数
--------------------------------------

PostgreSQL SQL Elements and Functions

.. autoclass:: aggregate_order_by

.. autoclass:: array

.. autofunction:: array_agg

.. autofunction:: Any

.. autofunction:: All

.. autoclass:: hstore
    :members:

.. autoclass:: to_tsvector

.. autoclass:: to_tsquery

.. autoclass:: plainto_tsquery

.. autoclass:: phraseto_tsquery

.. autoclass:: websearch_to_tsquery

.. autoclass:: ts_headline

.. autofunction:: distinct_on

PostgreSQL 约束类型
---------------------------

PostgreSQL Constraint Types

.. tab:: 中文

    SQLAlchemy通过 :class:`ExcludeConstraint` 类支持PostgreSQL EXCLUDE约束：

    .. autoclass:: ExcludeConstraint
        :members: __init__

    例如::

        from sqlalchemy.dialects.postgresql import ExcludeConstraint, TSRANGE


        class RoomBooking(Base):
            __tablename__ = "room_booking"

            room = Column(Integer(), primary_key=True)
            during = Column(TSRANGE())

            __table_args__ = (ExcludeConstraint(("room", "="), ("during", "&&")),)

.. tab:: 英文

    SQLAlchemy supports PostgreSQL EXCLUDE constraints via the
    :class:`ExcludeConstraint` class:

    .. autoclass:: ExcludeConstraint
        :no-index:
        :members: __init__

    For example::

        from sqlalchemy.dialects.postgresql import ExcludeConstraint, TSRANGE


        class RoomBooking(Base):
            __tablename__ = "room_booking"

            room = Column(Integer(), primary_key=True)
            during = Column(TSRANGE())

            __table_args__ = (ExcludeConstraint(("room", "="), ("during", "&&")),)

PostgreSQL DML 构造
-------------------------

PostgreSQL DML Constructs

.. autofunction:: sqlalchemy.dialects.postgresql.insert

.. autoclass:: sqlalchemy.dialects.postgresql.Insert
  :members:

.. _postgresql_psycopg2:

psycopg2
--------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg2

.. _postgresql_psycopg:

psycopg
--------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg

.. _postgresql_pg8000:

pg8000
------

.. automodule:: sqlalchemy.dialects.postgresql.pg8000

.. _dialect-postgresql-asyncpg:

.. _postgresql_asyncpg:

asyncpg
-------

.. automodule:: sqlalchemy.dialects.postgresql.asyncpg

psycopg2cffi
------------

.. automodule:: sqlalchemy.dialects.postgresql.psycopg2cffi
