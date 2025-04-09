.. currentmodule:: sqlalchemy.types

.. _types_custom:

自定义类型
============

Custom Types

.. tab:: 中文

    存在多种方法可以重新定义现有类型的行为以及提供新的类型的行为。

.. tab:: 英文

    A variety of methods exist to redefine the behavior of existing types as well as to provide new ones.

重写类型编译
---------------------------

Overriding Type Compilation

.. tab:: 中文

    一个常见的需求是强制类型的“字符串”版本发生改变，也就是说，
    强制其在 CREATE TABLE 语句或其他 SQL 函数（如 CAST）中渲染的文本。
    例如，一个应用可能希望在所有平台上都渲染为 ``BINARY``，
    但在某一个平台上则希望渲染为 ``BLOB``。
    对于大多数使用场景，推荐使用现有的通用类型，如 :class:`.LargeBinary`。
    但如果需要更精确地控制类型，可以为任意类型设置一个与方言相关的编译指令，如下::

        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.types import BINARY


        @compiles(BINARY, "sqlite")
        def compile_binary_sqlite(type_, compiler, **kw):
            return "BLOB"

    上述代码允许我们使用 :class:`_types.BINARY`，
    它在所有后端上都会生成 ``BINARY``，除了 SQLite，
    在 SQLite 上会生成 ``BLOB``。

    更多示例请参阅章节 :ref:`type_compilation_extension`，
    该章节属于 :ref:`sqlalchemy.ext.compiler_toplevel` 的子章节。

.. tab:: 英文

    A frequent need is to force the "string" version of a type, that is
    the one rendered in a CREATE TABLE statement or other SQL function
    like CAST, to be changed.   For example, an application may want
    to force the rendering of ``BINARY`` for all platforms
    except for one, in which is wants ``BLOB`` to be rendered.  Usage
    of an existing generic type, in this case :class:`.LargeBinary`, is
    preferred for most use cases.  But to control
    types more accurately, a compilation directive that is per-dialect
    can be associated with any type::

        from sqlalchemy.ext.compiler import compiles
        from sqlalchemy.types import BINARY


        @compiles(BINARY, "sqlite")
        def compile_binary_sqlite(type_, compiler, **kw):
            return "BLOB"

    The above code allows the usage of :class:`_types.BINARY`, which
    will produce the string ``BINARY`` against all backends except SQLite,
    in which case it will produce ``BLOB``.

    See the section :ref:`type_compilation_extension`, a subsection of
    :ref:`sqlalchemy.ext.compiler_toplevel`, for additional examples.

.. _types_typedecorator:

增强现有类型
-------------------------

Augmenting Existing Types

.. tab:: 中文

    :class:`.TypeDecorator` 类允许我们基于现有类型对象创建自定义类型，
    这些类型可添加绑定参数（bind-parameter）处理和结果处理（result-processing）行为。
    当数据在 Python 与数据库之间传输时需要额外的转换处理（即术语 :term:`marshalling`）时，
    可使用此类。

    .. note::

    :class:`.TypeDecorator` 的绑定与结果处理是 **附加于** 所托管类型
    已经执行的处理逻辑之上的。
    SQLAlchemy 针对每种 DBAPI 都自定义了这些基础类型的处理逻辑，
    并已涵盖该 DBAPI 所需的全部转换。
    虽然可以通过子类化来替换这些底层处理行为，但实际中并无必要，
    且 SQLAlchemy 已不再将其作为公开支持的使用方式。

    .. topic:: ORM 提示

    :class:`.TypeDecorator` 可用于在数据写入和读取数据库时，
    提供一致的值转换方式。
    在 ORM 使用中，若要将用户输入的数据从任意格式转换为模型所需格式，
    可使用 :func:`.validates` 装饰器实现类似的效果。
    当转换逻辑依赖于具体的业务需求，且并非一种通用数据类型时，
    使用验证器装饰器可能更合适。

    .. autoclass:: TypeDecorator
       :members:

    .. autoattribute:: cache_ok

.. tab:: 英文

    The :class:`.TypeDecorator` allows the creation of custom types which
    add bind-parameter and result-processing behavior to an existing
    type object.  It is used when additional in-Python :term:`marshalling` of data
    to and/or from the database is required.

    .. note::

    The bind- and result-processing of :class:`.TypeDecorator`
    is **in addition** to the processing already performed by the hosted
    type, which is customized by SQLAlchemy on a per-DBAPI basis to perform
    processing specific to that DBAPI.  While it is possible to replace this
    handling for a given type through direct subclassing, it is never needed in
    practice and SQLAlchemy no longer supports this as a public use case.

    .. topic:: ORM Tip

    The :class:`.TypeDecorator` can be used to provide a consistent means of
    converting some type of value as it is passed into and out of the database.
    When using the ORM, a similar technique exists for converting user data
    from arbitrary formats which is to use the :func:`.validates` decorator.
    This technique may be more appropriate when data coming into an ORM model
    needs to be normalized in some way that is specific to the business case
    and isn't as generic as a datatype.

    .. autoclass:: TypeDecorator
       :members:

    .. autoattribute:: cache_ok

TypeDecorator 配方
---------------------

TypeDecorator Recipes

.. tab:: 中文

    以下是一些关键的 :class:`.TypeDecorator` 配方。

.. tab:: 英文

    A few key :class:`.TypeDecorator` recipes follow.

.. _coerce_to_unicode:

将编码字符串强制转换为 Unicode
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Coercing Encoded Strings to Unicode

.. tab:: 中文

    关于 :class:`.Unicode` 类型，一个常见的困惑是它 **仅** 用于处理 Python 中的 ``unicode`` 对象，
    也就是说，传给该类型的绑定参数在 Python 2 中必须是 ``u'some string'`` 的形式，
    而不是普通的字符串对象（bytestring）。
    它所执行的编码/解码函数只是为了适应所使用的 DBAPI 的要求，
    这些函数本质上是 SQLAlchemy 的内部实现细节。

    如果需要一个可以安全接收 Python 字节串（即包含非 ASCII 字符的字符串，
    在 Python 2 中不是 ``u''`` 对象），可以通过定义一个 :class:`.TypeDecorator` 类型，
    根据需要进行类型转换来实现此功能::

        from sqlalchemy.types import TypeDecorator, Unicode


        class CoerceUTF8(TypeDecorator):
            """在传入数据库之前，将 Python 字节串安全转换为 Unicode。"""

            impl = Unicode

            def process_bind_param(self, value, dialect):
                if isinstance(value, str):
                    value = value.decode("utf-8")
                return value

.. tab:: 英文

    A common source of confusion regarding the :class:`.Unicode` type
    is that it is intended to deal *only* with Python ``unicode`` objects
    on the Python side, meaning values passed to it as bind parameters
    must be of the form ``u'some string'`` if using Python 2 and not 3.
    The encoding/decoding functions it performs are only to suit what the
    DBAPI in use requires, and are primarily a private implementation detail.

    The use case of a type that can safely receive Python bytestrings,
    that is strings that contain non-ASCII characters and are not ``u''``
    objects in Python 2, can be achieved using a :class:`.TypeDecorator`
    which coerces as needed::

        from sqlalchemy.types import TypeDecorator, Unicode


        class CoerceUTF8(TypeDecorator):
            """Safely coerce Python bytestrings to Unicode
            before passing off to the database."""

            impl = Unicode

            def process_bind_param(self, value, dialect):
                if isinstance(value, str):
                    value = value.decode("utf-8")
                return value

四舍五入数字
^^^^^^^^^^^^^^^^^

Rounding Numerics

.. tab:: 中文

    某些数据库连接器（如 SQL Server 的连接器）在接收到包含过多小数位的 Decimal 时会出错。
    以下是一个用于向下舍入的示例方案::

        from sqlalchemy.types import TypeDecorator, Numeric
        from decimal import Decimal


        class SafeNumeric(TypeDecorator):
            """为 Numeric 添加量化处理。"""

            impl = Numeric

            def __init__(self, *arg, **kw):
                TypeDecorator.__init__(self, *arg, **kw)
                self.quantize_int = -self.impl.scale
                self.quantize = Decimal(10) ** self.quantize_int

            def process_bind_param(self, value, dialect):
                if isinstance(value, Decimal) and value.as_tuple()[2] < self.quantize_int:
                    value = value.quantize(self.quantize)
                return value

.. tab:: 英文

    Some database connectors like those of SQL Server choke if a Decimal is passed with too
    many decimal places.   Here's a recipe that rounds them down::

        from sqlalchemy.types import TypeDecorator, Numeric
        from decimal import Decimal


        class SafeNumeric(TypeDecorator):
            """Adds quantization to Numeric."""

            impl = Numeric

            def __init__(self, *arg, **kw):
                TypeDecorator.__init__(self, *arg, **kw)
                self.quantize_int = -self.impl.scale
                self.quantize = Decimal(10) ** self.quantize_int

            def process_bind_param(self, value, dialect):
                if isinstance(value, Decimal) and value.as_tuple()[2] < self.quantize_int:
                    value = value.quantize(self.quantize)
                return value

将时区感知时间戳存储为时区简单 UTC
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Store Timezone Aware Timestamps as Timezone Naive UTC

.. tab:: 中文

    数据库中的时间戳应始终以与时区无关的方式存储。
    对大多数数据库而言，这意味着应首先将时间戳转换为 UTC 时区，
    然后再作为无时区（即不附带任何时区信息，假定 UTC 为“隐式”时区）存储。
    当然，也可以使用数据库特定的类型（如 PostgreSQL 的 “TIMESTAMP WITH TIMEZONE”），
    因其功能更为丰富而常被优先选择；
    但将时间戳以 UTC 格式进行普通存储可适用于所有数据库和驱动。
    当不适用或不希望使用时区感知的数据库类型时，
    可以通过 :class:`.TypeDecorator` 创建一个数据类型，
    用于在存储前将带时区时间戳转换为无时区时间戳，并在读取时转换回带时区。
    下面示例使用 Python 内置的 ``datetime.timezone.utc`` 来完成标准化与反标准化::

        import datetime


        class TZDateTime(TypeDecorator):
            impl = DateTime
            cache_ok = True

            def process_bind_param(self, value, dialect):
                if value is not None:
                    if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                        raise TypeError("tzinfo is required")
                    value = value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = value.replace(tzinfo=datetime.timezone.utc)
                return value

    .. note:: 自 2.0 版本起，建议优先使用内置的 :class:`_types.Uuid` 类型，
        它具有类似的行为。此示例主要用于演示一个接收和返回 Python 对象的类型装饰器写法。

.. tab:: 英文

    Timestamps in databases should always be stored in a timezone-agnostic way. For
    most databases, this means ensuring a timestamp is first in the UTC timezone
    before it is stored, then storing it as timezone-naive (that is, without any
    timezone associated with it; UTC is assumed to be the "implicit" timezone).
    Alternatively,  database-specific types like PostgreSQLs "TIMESTAMP WITH
    TIMEZONE" are often preferred for their richer functionality; however, storing
    as plain UTC will work on all databases and drivers.   When a
    timezone-intelligent database type is not an option or is not preferred,  the
    :class:`.TypeDecorator` can be used to create a datatype that convert timezone
    aware timestamps into timezone naive and back again.   Below, Python's
    built-in ``datetime.timezone.utc`` timezone is used to normalize and
    denormalize::

        import datetime


        class TZDateTime(TypeDecorator):
            impl = DateTime
            cache_ok = True

            def process_bind_param(self, value, dialect):
                if value is not None:
                    if not value.tzinfo or value.tzinfo.utcoffset(value) is None:
                        raise TypeError("tzinfo is required")
                    value = value.astimezone(datetime.timezone.utc).replace(tzinfo=None)
                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = value.replace(tzinfo=datetime.timezone.utc)
                return value

.. _custom_guid_type:

后端无关的 GUID 类型
^^^^^^^^^^^^^^^^^^^^^^^^^^

Backend-agnostic GUID Type

.. tab:: 中文

    此类型接收并返回 Python 的 uuid() 对象。
    在 PostgreSQL 中使用 PG 的 UUID 类型，在 MSSQL 中使用 UNIQUEIDENTIFIER，
    而在其他后端中使用 CHAR(32)，并将其以字符串形式存储。
    其变体 ``GUIDHyphens`` 使用 CHAR(36) 类型并带有连字符的 uuid 格式字符串::

        from operator import attrgetter
        from sqlalchemy.types import TypeDecorator, CHAR
        from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
        from sqlalchemy.dialects.postgresql import UUID
        import uuid


        class GUID(TypeDecorator):
            """平台无关的 GUID 类型。

            PostgreSQL 中使用 UUID 类型，MSSQL 中使用 UNIQUEIDENTIFIER，
            否则使用 CHAR(32)，以十六进制字符串形式存储。

            """

            impl = CHAR
            cache_ok = True

            _default_type = CHAR(32)
            _uuid_as_str = attrgetter("hex")

            def load_dialect_impl(self, dialect):
                if dialect.name == "postgresql":
                    return dialect.type_descriptor(UUID())
                elif dialect.name == "mssql":
                    return dialect.type_descriptor(UNIQUEIDENTIFIER())
                else:
                    return dialect.type_descriptor(self._default_type)

            def process_bind_param(self, value, dialect):
                if value is None or dialect.name in ("postgresql", "mssql"):
                    return value
                else:
                    if not isinstance(value, uuid.UUID):
                        value = uuid.UUID(value)
                    return self._uuid_as_str(value)

            def process_result_value(self, value, dialect):
                if value is None:
                    return value
                else:
                    if not isinstance(value, uuid.UUID):
                        value = uuid.UUID(value)
                    return value


        class GUIDHyphens(GUID):
            """平台无关的 GUID 类型。

            PostgreSQL 中使用 UUID 类型，MSSQL 中使用 UNIQUEIDENTIFIER，
            否则使用 CHAR(36)，以带连字符的 uuid 字符串形式存储。

            """

            _default_type = CHAR(36)
            _uuid_as_str = str


.. tab:: 英文

    .. note:: Since version 2.0 the built-in :class:`_types.Uuid` type that
        behaves similarly should be preferred. This example is presented
        just as an example of a type decorator that receives and returns
        python objects.

    Receives and returns Python uuid() objects.  
    Uses the PG UUID type when using PostgreSQL, UNIQUEIDENTIFIER when using MSSQL,
    CHAR(32) on other backends, storing them in stringified format.
    The ``GUIDHyphens`` version stores the value with hyphens instead of just the hex
    string, using a CHAR(36) type::

        from operator import attrgetter
        from sqlalchemy.types import TypeDecorator, CHAR
        from sqlalchemy.dialects.mssql import UNIQUEIDENTIFIER
        from sqlalchemy.dialects.postgresql import UUID
        import uuid


        class GUID(TypeDecorator):
            """Platform-independent GUID type.

            Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
            otherwise uses CHAR(32), storing as stringified hex values.

            """

            impl = CHAR
            cache_ok = True

            _default_type = CHAR(32)
            _uuid_as_str = attrgetter("hex")

            def load_dialect_impl(self, dialect):
                if dialect.name == "postgresql":
                    return dialect.type_descriptor(UUID())
                elif dialect.name == "mssql":
                    return dialect.type_descriptor(UNIQUEIDENTIFIER())
                else:
                    return dialect.type_descriptor(self._default_type)

            def process_bind_param(self, value, dialect):
                if value is None or dialect.name in ("postgresql", "mssql"):
                    return value
                else:
                    if not isinstance(value, uuid.UUID):
                        value = uuid.UUID(value)
                    return self._uuid_as_str(value)

            def process_result_value(self, value, dialect):
                if value is None:
                    return value
                else:
                    if not isinstance(value, uuid.UUID):
                        value = uuid.UUID(value)
                    return value


        class GUIDHyphens(GUID):
            """Platform-independent GUID type.

            Uses PostgreSQL's UUID type or MSSQL's UNIQUEIDENTIFIER,
            otherwise uses CHAR(36), storing as stringified uuid values.

            """

            _default_type = CHAR(36)
            _uuid_as_str = str

将 Python ``uuid.UUID`` 链接到自定义类型以进行 ORM 映射
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Linking Python ``uuid.UUID`` to the Custom Type for ORM mappings

.. tab:: 中文

    当使用 :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 映射声明 ORM 映射时，
    可以通过将上文定义的自定义 ``GUID`` 类型添加到
    :ref:`type annotation map <orm_declarative_mapped_column_type_map>` 中，
    将其与 Python 的 ``uuid.UUID`` 数据类型关联。
    该映射通常定义在 :class:`_orm.DeclarativeBase` 类中::

        import uuid
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


        class Base(DeclarativeBase):
            type_annotation_map = {
                uuid.UUID: GUID,
            }

    通过上述配置，继承自 ``Base`` 的 ORM 映射类可以在类型注解中使用 Python 的 ``uuid.UUID``，
    并自动使用 ``GUID`` 类型::

        class MyModel(Base):
            __tablename__ = "my_table"

            id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    .. seealso::

        :ref:`orm_declarative_mapped_column_type_map`

.. tab:: 英文

    When declaring ORM mappings using :ref:`Annotated Declarative Table <orm_declarative_mapped_column>`
    mappings, the custom ``GUID`` type defined above may be associated with
    the Python ``uuid.UUID`` datatype by adding it to the
    :ref:`type annotation map <orm_declarative_mapped_column_type_map>`,
    which is typically defined on the :class:`_orm.DeclarativeBase` class::

        import uuid
        from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


        class Base(DeclarativeBase):
            type_annotation_map = {
                uuid.UUID: GUID,
            }

    With the above configuration, ORM mapped classes which extend from
    ``Base`` may refer to Python ``uuid.UUID`` in annotations which will make use
    of ``GUID`` automatically::

        class MyModel(Base):
            __tablename__ = "my_table"

            id: Mapped[uuid.UUID] = mapped_column(primary_key=True)

    .. seealso::

        :ref:`orm_declarative_mapped_column_type_map`

编组 JSON 字符串
^^^^^^^^^^^^^^^^^^^^

Marshal JSON Strings

.. tab:: 中文

    该类型使用 ``simplejson`` （或可修改为 Python 内置的 json 编码器）将 Python 数据结构
    序列化/反序列化为 JSON::

        from sqlalchemy.types import TypeDecorator, VARCHAR
        import json


        class JSONEncodedDict(TypeDecorator):
            """将不可变结构表示为 JSON 编码字符串。

            用法示例：

                JSONEncodedDict(255)

            """

            impl = VARCHAR

            cache_ok = True

            def process_bind_param(self, value, dialect):
                if value is not None:
                    value = json.dumps(value)

                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = json.loads(value)
                return value

.. tab:: 英文

    This type uses ``simplejson`` to marshal Python data structures
    to/from JSON.   Can be modified to use Python's builtin json encoder::

        from sqlalchemy.types import TypeDecorator, VARCHAR
        import json


        class JSONEncodedDict(TypeDecorator):
            """Represents an immutable structure as a json-encoded string.

            Usage:

                JSONEncodedDict(255)

            """

            impl = VARCHAR

            cache_ok = True

            def process_bind_param(self, value, dialect):
                if value is not None:
                    value = json.dumps(value)

                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = json.loads(value)
                return value

添加可变性
~~~~~~~~~~~~~~~~~

Adding Mutability

.. tab:: 中文

    ORM 默认不会检测此类类型的“可变性” —— 也就是说，对值的就地修改不会被检测到，也不会被刷新::

        obj.json_value["key"] = "value"  # ORM *不会* 检测到变更

        obj.json_value = {"key": "value"}  # ORM *会* 检测到变更

    上述限制对许多应用而言可能是可以接受的，因为这些值在创建后可能无需修改。
    但对于确实需要支持可变性的场景，推荐使用 ``sqlalchemy.ext.mutable`` 扩展。
    对于基于字典的 JSON 结构，可以这样应用::

        json_type = MutableDict.as_mutable(JSONEncodedDict)


        class MyClass(Base):
            #  ...

            json_data = Column(json_type)

    .. seealso::

        :ref:`mutable_toplevel`

.. tab:: 英文

    The ORM by default will not detect "mutability" on such a type as above -
    meaning, in-place changes to values will not be detected and will not be
    flushed.   Without further steps, you instead would need to replace the existing
    value with a new one on each parent object to detect changes::

        obj.json_value["key"] = "value"  # will *not* be detected by the ORM

        obj.json_value = {"key": "value"}  # *will* be detected by the ORM

    The above limitation may be
    fine, as many applications may not require that the values are ever mutated
    once created.  For those which do have this requirement, support for mutability
    is best applied using the ``sqlalchemy.ext.mutable`` extension.  For a
    dictionary-oriented JSON structure, we can apply this as::

        json_type = MutableDict.as_mutable(JSONEncodedDict)


        class MyClass(Base):
            #  ...

            json_data = Column(json_type)

    .. seealso::

        :ref:`mutable_toplevel`

处理比较操作
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dealing with Comparison Operations

.. tab:: 中文

    :class:`.TypeDecorator` 的默认行为是将任何表达式的“右侧值”强制转换为相同的类型。
    对于 JSON 类型，这意味着使用的任何操作符都必须在 JSON 上有意义。
    但在某些情况下，用户可能希望该类型在某些情况下像 JSON，
    在另一些情况下像普通文本。例如，如果我们希望在 JSON 类型上使用 LIKE 操作符。
    LIKE 对 JSON 结构并无意义，但对其底层字符串表示则有意义。
    若要在像 ``JSONEncodedDict`` 这样的类型中使用该操作符，我们需要先通过
    :func:`.cast` 或 :func:`.type_coerce` 将列强制转换为字符串类型::

        from sqlalchemy import type_coerce, String

        stmt = select(my_table).where(type_coerce(my_table.c.json_data, String).like("%foo%"))

    :class:`.TypeDecorator` 提供了一个内置机制，可基于操作符进行类型转换。
    如果我们希望频繁使用 LIKE 操作符，并将 JSON 对象作为字符串解释，
    则可以通过重写 :meth:`.TypeDecorator.coerce_compared_value` 方法将其内建到类型中::

        from sqlalchemy.sql import operators
        from sqlalchemy import String


        class JSONEncodedDict(TypeDecorator):
            impl = VARCHAR

            cache_ok = True

            def coerce_compared_value(self, op, value):
                if op in (operators.like_op, operators.not_like_op):
                    return String()
                else:
                    return self

            def process_bind_param(self, value, dialect):
                if value is not None:
                    value = json.dumps(value)

                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = json.loads(value)
                return value

    以上仅是处理 LIKE 操作符的一种方式。
    在其他应用中，若操作符（如 LIKE）对 JSON 对象无意义，
    也可以选择抛出 ``NotImplementedError``，而不是自动转换为文本类型。


.. tab:: 英文

    The default behavior of :class:`.TypeDecorator` is to coerce the "right hand side"
    of any expression into the same type.  For a type like JSON, this means that
    any operator used must make sense in terms of JSON.    For some cases,
    users may wish for the type to behave like JSON in some circumstances, and
    as plain text in others.  One example is if one wanted to handle the
    LIKE operator for the JSON type.  LIKE makes no sense against a JSON structure,
    but it does make sense against the underlying textual representation.  To
    get at this with a type like ``JSONEncodedDict``, we need to
    **coerce** the column to a textual form using :func:`.cast` or
    :func:`.type_coerce` before attempting to use this operator::

        from sqlalchemy import type_coerce, String

        stmt = select(my_table).where(type_coerce(my_table.c.json_data, String).like("%foo%"))

    :class:`.TypeDecorator` provides a built-in system for working up type
    translations like these based on operators.  If we wanted to frequently use the
    LIKE operator with our JSON object interpreted as a string, we can build it
    into the type by overriding the :meth:`.TypeDecorator.coerce_compared_value`
    method::

        from sqlalchemy.sql import operators
        from sqlalchemy import String


        class JSONEncodedDict(TypeDecorator):
            impl = VARCHAR

            cache_ok = True

            def coerce_compared_value(self, op, value):
                if op in (operators.like_op, operators.not_like_op):
                    return String()
                else:
                    return self

            def process_bind_param(self, value, dialect):
                if value is not None:
                    value = json.dumps(value)

                return value

            def process_result_value(self, value, dialect):
                if value is not None:
                    value = json.loads(value)
                return value

    Above is just one approach to handling an operator like "LIKE".  Other
    applications may wish to raise ``NotImplementedError`` for operators that
    have no meaning with a JSON object such as "LIKE", rather than automatically
    coercing to text.


.. _types_sql_value_processing:

应用 SQL 级绑定/结果处理
-----------------------------------------

Applying SQL-level Bind/Result Processing

.. tab:: 中文

    如在 :ref:`types_typedecorator` 小节中所示，
    SQLAlchemy 允许在将参数发送到语句时，以及从数据库加载结果行时，调用 Python 函数，
    以便在数据发送到数据库或从数据库读取时应用转换。
    同时也可以定义 **SQL 层级** 的转换操作。
    这种设计的动机是：某些转换操作仅在关系型数据库中提供，
    以用于在应用程序与持久化格式之间转换数据。
    例如使用数据库定义的加密/解密函数，或用于处理地理数据的存储过程等。

    任何 :class:`.TypeEngine`、:class:`.UserDefinedType` 或 :class:`.TypeDecorator` 的子类
    都可以实现 :meth:`.TypeEngine.bind_expression` 和/或 :meth:`.TypeEngine.column_expression` 方法。
    当这些方法返回非 ``None`` 值时，它们应返回一个 :class:`_expression.ColumnElement` 表达式，
    用于注入 SQL 语句，包裹绑定参数或列表达式。
    例如，为了创建一个 ``Geometry`` 类型，在所有写入操作中使用 PostGIS 函数 ``ST_GeomFromText``，
    在所有读取操作中使用 ``ST_AsText``，我们可以创建一个自定义的 :class:`.UserDefinedType` 子类，
    并结合 :data:`~.sqlalchemy.sql.expression.func` 提供这些方法::

        from sqlalchemy import func
        from sqlalchemy.types import UserDefinedType


        class Geometry(UserDefinedType):
            def get_col_spec(self):
                return "GEOMETRY"

            def bind_expression(self, bindvalue):
                return func.ST_GeomFromText(bindvalue, type_=self)

            def column_expression(self, col):
                return func.ST_AsText(col, type_=self)

    我们可以将 ``Geometry`` 类型用于 :class:`_schema.Table` 元数据中，
    并在 :func:`_expression.select` 语句中使用::

        geometry = Table(
            "geometry",
            metadata,
            Column("geom_id", Integer, primary_key=True),
            Column("geom_data", Geometry),
        )

        print(
            select(geometry).where(
                geometry.c.geom_data == "LINESTRING(189412 252431,189631 259122)"
            )
        )

    生成的 SQL 会按需插入这两个函数。
    ``ST_AsText`` 应用于列子句中，使返回值在进入结果集前经过函数处理，
    而 ``ST_GeomFromText`` 应用于绑定参数，转换传入值：

    .. sourcecode:: sql

        SELECT geometry.geom_id, ST_AsText(geometry.geom_data) AS geom_data_1
        FROM geometry
        WHERE geometry.geom_data = ST_GeomFromText(:geom_data_2)

    :meth:`.TypeEngine.column_expression` 方法与编译器机制协作，
    确保 SQL 表达式不会干扰包装表达式的标签。
    例如，当我们对表达式使用 :func:`.label` 并执行 :func:`_expression.select` 时，
    标签会被渲染在最外层::

        print(select(geometry.c.geom_data.label("my_data")))

    输出结果：

    .. sourcecode:: sql

        SELECT ST_AsText(geometry.geom_data) AS my_data
        FROM geometry

    另一个示例是对 :class:`_postgresql.BYTEA` 进行修饰，
    实现 ``PGPString`` 类型，使用 PostgreSQL 的 ``pgcrypto`` 扩展，
    以透明方式加密/解密数据::

        from sqlalchemy import (
            create_engine,
            String,
            select,
            func,
            MetaData,
            Table,
            Column,
            type_coerce,
            TypeDecorator,
        )

        from sqlalchemy.dialects.postgresql import BYTEA


        class PGPString(TypeDecorator):
            impl = BYTEA

            cache_ok = True

            def __init__(self, passphrase):
                super(PGPString, self).__init__()

                self.passphrase = passphrase

            def bind_expression(self, bindvalue):
                # 将绑定值从 PGPString 转换为 String，
                # 以便原样传递给 psycopg2，而不会被 dbapi.Binary 包裹
                bindvalue = type_coerce(bindvalue, String)
                return func.pgp_sym_encrypt(bindvalue, self.passphrase)

            def column_expression(self, col):
                return func.pgp_sym_decrypt(col, self.passphrase)


        metadata_obj = MetaData()
        message = Table(
            "message",
            metadata_obj,
            Column("username", String(50)),
            Column("message", PGPString("this is my passphrase")),
        )

        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        with engine.begin() as conn:
            metadata_obj.create_all(conn)

            conn.execute(
                message.insert(),
                {"username": "some user", "message": "this is my message"},
            )

            print(
                conn.scalar(select(message.c.message).where(message.c.username == "some user"))
            )

    ``pgp_sym_encrypt`` 和 ``pgp_sym_decrypt`` 函数分别被应用于 INSERT 和 SELECT 语句：

    .. sourcecode:: sql

        INSERT INTO message (username, message)
            VALUES (%(username)s, pgp_sym_encrypt(%(message)s, %(pgp_sym_encrypt_1)s))
            -- {'username': 'some user', 'message': 'this is my message',
            --  'pgp_sym_encrypt_1': 'this is my passphrase'}

        SELECT pgp_sym_decrypt(message.message, %(pgp_sym_decrypt_1)s) AS message_1
            FROM message
            WHERE message.username = %(username_1)s
            -- {'pgp_sym_decrypt_1': 'this is my passphrase', 'username_1': 'some user'}


.. tab:: 英文

    As seen in the section :ref:`types_typedecorator`,
    SQLAlchemy allows Python functions to be invoked both when parameters are sent
    to a statement, as well as when result rows are loaded from the database, to apply
    transformations to the values as they are sent to or from the database.   It is also
    possible to define SQL-level transformations as well.  The rationale here is when
    only the relational database contains a particular series of functions that are necessary
    to coerce incoming and outgoing data between an application and persistence format.
    Examples include using database-defined encryption/decryption functions, as well
    as stored procedures that handle geographic data.

    Any :class:`.TypeEngine`, :class:`.UserDefinedType` or :class:`.TypeDecorator` subclass
    can include implementations of
    :meth:`.TypeEngine.bind_expression` and/or :meth:`.TypeEngine.column_expression`, which
    when defined to return a non-``None`` value should return a :class:`_expression.ColumnElement`
    expression to be injected into the SQL statement, either surrounding
    bound parameters or a column expression.  For example, to build a ``Geometry``
    type which will apply the PostGIS function ``ST_GeomFromText`` to all outgoing
    values and the function ``ST_AsText`` to all incoming data, we can create
    our own subclass of :class:`.UserDefinedType` which provides these methods
    in conjunction with :data:`~.sqlalchemy.sql.expression.func`::

        from sqlalchemy import func
        from sqlalchemy.types import UserDefinedType


        class Geometry(UserDefinedType):
            def get_col_spec(self):
                return "GEOMETRY"

            def bind_expression(self, bindvalue):
                return func.ST_GeomFromText(bindvalue, type_=self)

            def column_expression(self, col):
                return func.ST_AsText(col, type_=self)

    We can apply the ``Geometry`` type into :class:`_schema.Table` metadata
    and use it in a :func:`_expression.select` construct::

        geometry = Table(
            "geometry",
            metadata,
            Column("geom_id", Integer, primary_key=True),
            Column("geom_data", Geometry),
        )

        print(
            select(geometry).where(
                geometry.c.geom_data == "LINESTRING(189412 252431,189631 259122)"
            )
        )

    The resulting SQL embeds both functions as appropriate.   ``ST_AsText``
    is applied to the columns clause so that the return value is run through
    the function before passing into a result set, and ``ST_GeomFromText``
    is run on the bound parameter so that the passed-in value is converted:

    .. sourcecode:: sql

        SELECT geometry.geom_id, ST_AsText(geometry.geom_data) AS geom_data_1
        FROM geometry
        WHERE geometry.geom_data = ST_GeomFromText(:geom_data_2)

    The :meth:`.TypeEngine.column_expression` method interacts with the
    mechanics of the compiler such that the SQL expression does not interfere
    with the labeling of the wrapped expression.   Such as, if we rendered
    a :func:`_expression.select` against a :func:`.label` of our expression, the string
    label is moved to the outside of the wrapped expression::

        print(select(geometry.c.geom_data.label("my_data")))

    Output:

    .. sourcecode:: sql

        SELECT ST_AsText(geometry.geom_data) AS my_data
        FROM geometry

    Another example is we decorate
    :class:`_postgresql.BYTEA` to provide a ``PGPString``, which will make use of the
    PostgreSQL ``pgcrypto`` extension to encrypt/decrypt values
    transparently::

        from sqlalchemy import (
            create_engine,
            String,
            select,
            func,
            MetaData,
            Table,
            Column,
            type_coerce,
            TypeDecorator,
        )

        from sqlalchemy.dialects.postgresql import BYTEA


        class PGPString(TypeDecorator):
            impl = BYTEA

            cache_ok = True

            def __init__(self, passphrase):
                super(PGPString, self).__init__()

                self.passphrase = passphrase

            def bind_expression(self, bindvalue):
                # convert the bind's type from PGPString to
                # String, so that it's passed to psycopg2 as is without
                # a dbapi.Binary wrapper
                bindvalue = type_coerce(bindvalue, String)
                return func.pgp_sym_encrypt(bindvalue, self.passphrase)

            def column_expression(self, col):
                return func.pgp_sym_decrypt(col, self.passphrase)


        metadata_obj = MetaData()
        message = Table(
            "message",
            metadata_obj,
            Column("username", String(50)),
            Column("message", PGPString("this is my passphrase")),
        )

        engine = create_engine("postgresql+psycopg2://scott:tiger@localhost/test", echo=True)
        with engine.begin() as conn:
            metadata_obj.create_all(conn)

            conn.execute(
                message.insert(),
                {"username": "some user", "message": "this is my message"},
            )

            print(
                conn.scalar(select(message.c.message).where(message.c.username == "some user"))
            )

    The ``pgp_sym_encrypt`` and ``pgp_sym_decrypt`` functions are applied
    to the INSERT and SELECT statements:

    .. sourcecode:: sql

        INSERT INTO message (username, message)
            VALUES (%(username)s, pgp_sym_encrypt(%(message)s, %(pgp_sym_encrypt_1)s))
            -- {'username': 'some user', 'message': 'this is my message',
            --  'pgp_sym_encrypt_1': 'this is my passphrase'}

        SELECT pgp_sym_decrypt(message.message, %(pgp_sym_decrypt_1)s) AS message_1
            FROM message
            WHERE message.username = %(username_1)s
            -- {'pgp_sym_decrypt_1': 'this is my passphrase', 'username_1': 'some user'}



.. _types_operators:

重新定义和创建新运算符
-------------------------------------

Redefining and Creating New Operators

.. tab:: 中文

    SQLAlchemy Core 定义了一组固定的表达式操作符，可用于所有的列表达式。
    其中一些操作符具有重载 Python 内建操作符的效果；
    此类操作符的示例包括：
    :meth:`.ColumnOperators.__eq__` （ ``table.c.somecolumn == 'foo'`` ），
    :meth:`.ColumnOperators.__invert__` （ ``~table.c.flag`` ），
    以及 :meth:`.ColumnOperators.__add__` （ ``table.c.x + table.c.y`` ）。
    其他操作符则通过列表达式上的显式方法暴露出来，例如
    :meth:`.ColumnOperators.in_` （ ``table.c.value.in_(['x', 'y'])`` ）和 :meth:`.ColumnOperators.like`
    （ ``table.c.value.like('%ed%')`` ）。

    当需要使用某个 SQL 操作符，而上述方法并未直接支持时，
    最简便的方式是使用任何 SQL 表达式对象的 :meth:`_sql.Operators.op` 方法；
    该方法接受一个表示 SQL 操作符的字符串，并返回一个可调用对象（Python callable），
    该对象接受任意右侧表达式作为参数：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import column
        >>> expr = column("x").op(">>")(column("y"))
        >>> print(expr)
        {printsql}x >> y

    当使用自定义 SQL 类型时，也可以像上述一样实现自定义操作符，
    使其自动出现在使用该列类型的任何列表达式上，无需每次手动调用 :meth:`_sql.Operators.op`。

    为实现此功能，SQL 表达式构造会查找与之关联的 :class:`_types.TypeEngine` 对象，
    以确定内建操作符的行为，并查找是否有自定义方法被调用。
    :class:`.TypeEngine` 定义了一个由 :class:`.TypeEngine.Comparator` 类实现的 “comparison” 对象，
    用于提供 SQL 操作符的基础行为。
    许多特定类型都会提供该类的子类实现。
    用户自定义的 :class:`.TypeEngine.Comparator` 实现可直接构建在某个类型的子类中，
    以便覆盖或定义新的操作。
    下面我们创建一个 :class:`.Integer` 的子类，重写 :meth:`.ColumnOperators.__add__` 操作符，
    它内部使用 :meth:`_sql.Operators.op` 来生成自定义 SQL::

        from sqlalchemy import Integer


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def __add__(self, other):
                    return self.op("goofy")(other)

    上述配置创建了一个新类 ``MyInt``，
    并将其 :attr:`.TypeEngine.comparator_factory` 属性设定为
    一个新的类，该类继承自与 :class:`.Integer` 类型相关的 :class:`.TypeEngine.Comparator` 类。

    用法示例：

    .. sourcecode:: pycon+sql

        >>> sometable = Table("sometable", metadata, Column("data", MyInt))
        >>> print(sometable.c.data + 5)
        {printsql}sometable.data goofy :data_1

    :meth:`.ColumnOperators.__add__` 的实现会被 SQL 表达式本体调用，
    它通过将自身作为 ``expr`` 属性来实例化 :class:`.TypeEngine.Comparator`。
    该属性可在实现中用于直接引用原始的 :class:`_sql.ColumnElement` 对象::

        from sqlalchemy import Integer


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def __add__(self, other):
                    return func.special_addition(self.expr, other)

    添加到 :class:`.TypeEngine.Comparator` 的新方法会通过动态查找机制暴露在
    所属的 SQL 表达式对象上，从而使这些方法成为 :class:`_expression.ColumnElement`
    表达式构造的一部分。
    例如，向整数类型添加一个 ``log()`` 函数::

        from sqlalchemy import Integer, func


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def log(self, other):
                    return func.log(self.expr, other)

    使用上述类型：

    .. sourcecode:: pycon+sql

        >>> print(sometable.c.data.log(5))
        {printsql}log(:log_1, :log_2)

    当使用 :meth:`.Operators.op` 进行返回布尔结果的比较操作时，
    应设置 :paramref:`.Operators.op.is_comparison` 标志为 ``True``::

        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def is_frobnozzled(self, other):
                    return self.op("--is_frobnozzled->", is_comparison=True)(other)

    还可以定义一元操作符。
    例如，要添加 PostgreSQL 阶乘操作符的实现，
    我们可以结合使用 :class:`.UnaryExpression` 构造与 :class:`.custom_op`，
    以生成阶乘表达式::

        from sqlalchemy import Integer
        from sqlalchemy.sql.expression import UnaryExpression
        from sqlalchemy.sql import operators


        class MyInteger(Integer):
            class comparator_factory(Integer.Comparator):
                def factorial(self):
                    return UnaryExpression(
                        self.expr, modifier=operators.custom_op("!"), type_=MyInteger
                    )

    使用该类型：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.sql import column
        >>> print(column("x", MyInteger).factorial())
        {printsql}x !

    .. seealso::

        :meth:`.Operators.op`

        :attr:`.TypeEngine.comparator_factory`


.. tab:: 英文

    SQLAlchemy Core defines a fixed set of expression operators available to all column expressions.
    Some of these operations have the effect of overloading Python's built-in operators;
    examples of such operators include
    :meth:`.ColumnOperators.__eq__` (``table.c.somecolumn == 'foo'``),
    :meth:`.ColumnOperators.__invert__` (``~table.c.flag``),
    and :meth:`.ColumnOperators.__add__` (``table.c.x + table.c.y``).  Other operators are exposed as
    explicit methods on column expressions, such as
    :meth:`.ColumnOperators.in_` (``table.c.value.in_(['x', 'y'])``) and :meth:`.ColumnOperators.like`
    (``table.c.value.like('%ed%')``).

    When the need arises for a SQL operator that isn't directly supported by the
    already supplied methods above, the most expedient way to produce this operator is
    to use the :meth:`_sql.Operators.op` method on any SQL expression object; this method
    is given a string representing the SQL operator to render, and the return value
    is a Python callable that accepts any arbitrary right-hand side expression:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import column
        >>> expr = column("x").op(">>")(column("y"))
        >>> print(expr)
        {printsql}x >> y

    When making use of custom SQL types, there is also a means of implementing
    custom operators as above that are automatically present upon any column
    expression that makes use of that column type, without the need to directly
    call :meth:`_sql.Operators.op` each time the operator is to be used.

    To achieve this, a SQL
    expression construct consults the :class:`_types.TypeEngine` object associated
    with the construct in order to determine the behavior of the built-in
    operators as well as to look for new methods that may have been invoked.
    :class:`.TypeEngine` defines a
    "comparison" object implemented by the :class:`.TypeEngine.Comparator` class to provide the base
    behavior for SQL operators, and many specific types provide their own
    sub-implementations of this class. User-defined :class:`.TypeEngine.Comparator`
    implementations can be built directly into a simple subclass of a particular
    type in order to override or define new operations. Below, we create a
    :class:`.Integer` subclass which overrides the :meth:`.ColumnOperators.__add__`
    operator, which in turn uses :meth:`_sql.Operators.op` to produce the custom
    SQL itself::

        from sqlalchemy import Integer


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def __add__(self, other):
                    return self.op("goofy")(other)

    The above configuration creates a new class ``MyInt``, which
    establishes the :attr:`.TypeEngine.comparator_factory` attribute as
    referring to a new class, subclassing the :class:`.TypeEngine.Comparator` class
    associated with the :class:`.Integer` type.

    Usage:

    .. sourcecode:: pycon+sql

        >>> sometable = Table("sometable", metadata, Column("data", MyInt))
        >>> print(sometable.c.data + 5)
        {printsql}sometable.data goofy :data_1

    The implementation for :meth:`.ColumnOperators.__add__` is consulted
    by an owning SQL expression, by instantiating the :class:`.TypeEngine.Comparator` with
    itself as the ``expr`` attribute.  This attribute may be used when the
    implementation needs to refer to the originating :class:`_sql.ColumnElement`
    object directly::

        from sqlalchemy import Integer


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def __add__(self, other):
                    return func.special_addition(self.expr, other)

    New methods added to a :class:`.TypeEngine.Comparator` are exposed on an
    owning SQL expression object using a dynamic lookup scheme, which exposes methods added to
    :class:`.TypeEngine.Comparator` onto the owning :class:`_expression.ColumnElement`
    expression construct.  For example, to add a ``log()`` function
    to integers::

        from sqlalchemy import Integer, func


        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def log(self, other):
                    return func.log(self.expr, other)

    Using the above type:

    .. sourcecode:: pycon+sql

        >>> print(sometable.c.data.log(5))
        {printsql}log(:log_1, :log_2)

    When using :meth:`.Operators.op` for comparison operations that return a
    boolean result, the :paramref:`.Operators.op.is_comparison` flag should be
    set to ``True``::

        class MyInt(Integer):
            class comparator_factory(Integer.Comparator):
                def is_frobnozzled(self, other):
                    return self.op("--is_frobnozzled->", is_comparison=True)(other)

    Unary operations
    are also possible.  For example, to add an implementation of the
    PostgreSQL factorial operator, we combine the :class:`.UnaryExpression` construct
    along with a :class:`.custom_op` to produce the factorial expression::

        from sqlalchemy import Integer
        from sqlalchemy.sql.expression import UnaryExpression
        from sqlalchemy.sql import operators


        class MyInteger(Integer):
            class comparator_factory(Integer.Comparator):
                def factorial(self):
                    return UnaryExpression(
                        self.expr, modifier=operators.custom_op("!"), type_=MyInteger
                    )

    Using the above type:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.sql import column
        >>> print(column("x", MyInteger).factorial())
        {printsql}x !

    .. seealso::

        :meth:`.Operators.op`

        :attr:`.TypeEngine.comparator_factory`



创建新类型
------------------

Creating New Types

.. tab:: 中文

    :class:`.UserDefinedType` 类是一个简单的基类，用于定义全新的数据库类型。使用它来表示 SQLAlchemy 不支持的原生数据库类型。如果只需要 Python 翻译行为，请使用 :class:`.TypeDecorator`。

    .. autoclass:: UserDefinedType
       :members:
    
       .. autoattribute:: cache_ok

.. tab:: 英文

    The :class:`.UserDefinedType` class is provided as a simple base class for defining entirely new database types.   Use this to represent native database types not known by SQLAlchemy.   If only Python translation behavior is needed, use :class:`.TypeDecorator` instead.

    .. autoclass:: UserDefinedType
       :members:
    
       .. autoattribute:: cache_ok

.. _custom_and_decorated_types_reflection:

使用自定义类型和反射
-----------------------------------------

Working with Custom Types and Reflection

.. tab:: 中文

    需要注意的是，那些被修改以在 Python 中具有附加行为的数据库类型（包括基于
    :class:`.TypeDecorator` 的类型以及其他用户定义的数据类型子类），在数据库架构中并没有任何表示形式。
    当使用 :ref:`metadata_reflection` 中描述的数据库自省功能时，
    SQLAlchemy 使用的是一组固定的映射，用于将数据库服务器返回的数据类型信息
    关联到 SQLAlchemy 的数据类型对象上。
    例如，当我们查看 PostgreSQL 架构中某个数据库列的定义时，可能会得到字符串 ``"VARCHAR"``。
    SQLAlchemy 的 PostgreSQL 方言包含一个硬编码的映射，它将字符串 ``"VARCHAR"``
    关联到 SQLAlchemy 的 :class:`.VARCHAR` 类。
    因此，当我们执行类似 ``Table('my_table', m, autoload_with=engine)`` 的语句时，
    其中的 :class:`_schema.Column` 对象会包含一个 :class:`.VARCHAR` 实例。

    这意味着，如果一个 :class:`_schema.Table` 对象使用了与数据库原生类型名称不直接对应的类型对象，
    那么当我们在其他地方针对该数据库表、并通过反射创建一个新的 :class:`_schema.Table` 对象时，
    它将不会包含该自定义类型。例如：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import (
        ...     Table,
        ...     Column,
        ...     MetaData,
        ...     create_engine,
        ...     PickleType,
        ...     Integer,
        ... )
        >>> metadata = MetaData()
        >>> my_table = Table(
        ...     "my_table", metadata, Column("id", Integer), Column("data", PickleType)
        ... )
        >>> engine = create_engine("sqlite://", echo="debug")
        >>> my_table.create(engine)
        {execsql}INFO sqlalchemy.engine.base.Engine
        CREATE TABLE my_table (
            id INTEGER,
            data BLOB
        )

    上述代码中，我们使用了 :class:`.PickleType`，它是一个基于 :class:`.LargeBinary` 类型的 :class:`.TypeDecorator`，
    而在 SQLite 中该类型对应于数据库类型 ``BLOB`` 。
    在 CREATE TABLE 语句中，我们看到使用的是 ``BLOB`` 类型。
    SQLite 数据库对我们所用的 :class:`.PickleType` 一无所知。

    如果我们查看 ``my_table.c.data.type`` 的数据类型，由于这是我们直接创建的 Python 对象，
    它的类型是 :class:`.PickleType`::

        >>> my_table.c.data.type
        PickleType()

    然而，如果我们使用反射来创建另一个 :class:`_schema.Table` 实例，
    由于我们创建的 SQLite 数据库中并未保存 :class:`.PickleType` 的信息，
    因此得到的是 :class:`.BLOB`：

    .. sourcecode:: pycon+sql

        >>> metadata_two = MetaData()
        >>> my_reflected_table = Table("my_table", metadata_two, autoload_with=engine)
        {execsql}INFO sqlalchemy.engine.base.Engine PRAGMA main.table_info("my_table")
        INFO sqlalchemy.engine.base.Engine ()
        DEBUG sqlalchemy.engine.base.Engine Col ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk')
        DEBUG sqlalchemy.engine.base.Engine Row (0, 'id', 'INTEGER', 0, None, 0)
        DEBUG sqlalchemy.engine.base.Engine Row (1, 'data', 'BLOB', 0, None, 0)

        >>> my_reflected_table.c.data.type
        BLOB()

    通常情况下，当应用程序定义了带有自定义类型的显式 :class:`_schema.Table` 元数据时，
    就不需要使用表反射，因为所有必要的 :class:`_schema.Table` 元数据已经存在。
    然而，在某些情况下，应用程序（或多个应用程序）需要同时使用包含自定义 Python 类型的显式
    :class:`_schema.Table` 元数据和通过数据库反射生成的 :class:`_schema.Table` 对象，
    并希望后者仍然具备自定义数据类型的 Python 行为，此时就需要采取额外步骤。

    最直接的方式是覆盖某些列，如 :ref:`reflection_overriding_columns` 中所述。
    这种技术结合了反射和显式的 :class:`_schema.Column` 对象，用于那些需要使用自定义或装饰类型的列::

        >>> metadata_three = MetaData()
        >>> my_reflected_table = Table(
        ...     "my_table",
        ...     metadata_three,
        ...     Column("data", PickleType),
        ...     autoload_with=engine,
        ... )

    上述 ``my_reflected_table`` 对象是通过反射加载的，
    它会从 SQLite 数据库中加载 "id" 列的定义。
    但对于 "data" 列，我们通过显式的 :class:`_schema.Column` 定义进行了覆盖，
    其中包含了我们期望的 Python 数据类型 :class:`.PickleType`。
    反射过程会保留这个 :class:`_schema.Column` 对象不变::

        >>> my_reflected_table.c.data.type
        PickleType()

    另一种更复杂的方法是使用 :meth:`.DDLEvents.column_reflect` 事件处理器，
    用于将数据库原生类型对象转换为自定义数据类型。
    例如，如果我们希望所有的 :class:`.BLOB` 数据类型都使用 :class:`.PickleType`，
    可以设置一条全局规则::

        from sqlalchemy import BLOB
        from sqlalchemy import event
        from sqlalchemy import PickleType
        from sqlalchemy import Table


        @event.listens_for(Table, "column_reflect")
        def _setup_pickletype(inspector, table, column_info):
            if isinstance(column_info["type"], BLOB):
                column_info["type"] = PickleType()

    当上述代码在任何表反射发生 *之前* 被调用时（注意它应该在应用程序中 **只调用一次**，因为它是全局规则），
    对于任何包含 :class:`.BLOB` 数据类型的 :class:`_schema.Table`，反射过程中得到的类型
    将会在 :class:`_schema.Column` 对象中被存储为 :class:`.PickleType`。

    在实际使用中，上述基于事件的方法通常会包含额外的规则，
    以仅影响那些确实需要转换数据类型的列，例如使用一个包含表名或列名的查找表，
    或使用其他启发式逻辑，以更准确地确定哪些列应该设定为 Python 数据类型。

.. tab:: 英文

    It is important to note that database types which are modified to have
    additional in-Python behaviors, including types based on
    :class:`.TypeDecorator` as well as other user-defined subclasses of datatypes,
    do not have any representation within a database schema.    When using database
    the introspection features described at :ref:`metadata_reflection`, SQLAlchemy
    makes use of a fixed mapping which links the datatype information reported by a
    database server to a SQLAlchemy datatype object.   For example, if we look
    inside of a PostgreSQL schema at the definition for a particular database
    column, we might receive back the string ``"VARCHAR"``.  SQLAlchemy's
    PostgreSQL dialect has a hardcoded mapping which links the string name
    ``"VARCHAR"`` to the SQLAlchemy :class:`.VARCHAR` class, and that's how when we
    emit a statement like ``Table('my_table', m, autoload_with=engine)``, the
    :class:`_schema.Column` object within it would have an instance of :class:`.VARCHAR`
    present inside of it.
    
    The implication of this is that if a :class:`_schema.Table` object makes use of type
    objects that don't correspond directly to the database-native type name, if we
    create a new :class:`_schema.Table` object against a new :class:`_schema.MetaData` collection
    for this database table elsewhere using reflection, it will not have this
    datatype. For example:
    
    .. sourcecode:: pycon+sql
    
        >>> from sqlalchemy import (
        ...     Table,
        ...     Column,
        ...     MetaData,
        ...     create_engine,
        ...     PickleType,
        ...     Integer,
        ... )
        >>> metadata = MetaData()
        >>> my_table = Table(
        ...     "my_table", metadata, Column("id", Integer), Column("data", PickleType)
        ... )
        >>> engine = create_engine("sqlite://", echo="debug")
        >>> my_table.create(engine)
        {execsql}INFO sqlalchemy.engine.base.Engine
        CREATE TABLE my_table (
            id INTEGER,
            data BLOB
        )
    
    Above, we made use of :class:`.PickleType`, which is a :class:`.TypeDecorator`
    that works on top of the :class:`.LargeBinary` datatype, which on SQLite
    corresponds to the database type ``BLOB``.  In the CREATE TABLE, we see that
    the ``BLOB`` datatype is used.   The SQLite database knows nothing about the
    :class:`.PickleType` we've used.
    
    If we look at the datatype of ``my_table.c.data.type``, as this is a Python
    object that was created by us directly, it is :class:`.PickleType`::
    
        >>> my_table.c.data.type
        PickleType()
    
    However, if we create another instance of :class:`_schema.Table` using reflection,
    the use of :class:`.PickleType` is not represented in the SQLite database we've
    created; we instead get back :class:`.BLOB`:
    
    .. sourcecode:: pycon+sql
    
        >>> metadata_two = MetaData()
        >>> my_reflected_table = Table("my_table", metadata_two, autoload_with=engine)
        {execsql}INFO sqlalchemy.engine.base.Engine PRAGMA main.table_info("my_table")
        INFO sqlalchemy.engine.base.Engine ()
        DEBUG sqlalchemy.engine.base.Engine Col ('cid', 'name', 'type', 'notnull', 'dflt_value', 'pk')
        DEBUG sqlalchemy.engine.base.Engine Row (0, 'id', 'INTEGER', 0, None, 0)
        DEBUG sqlalchemy.engine.base.Engine Row (1, 'data', 'BLOB', 0, None, 0)
    
        >>> my_reflected_table.c.data.type
        BLOB()
    
    Typically, when an application defines explicit :class:`_schema.Table` metadata with
    custom types, there is no need to use table reflection because the necessary
    :class:`_schema.Table` metadata is already present.  However, for the case where an
    application, or a combination of them, need to make use of both explicit
    :class:`_schema.Table` metadata which includes custom, Python-level datatypes, as well
    as :class:`_schema.Table` objects which set up their :class:`_schema.Column` objects as
    reflected from the database, which nevertheless still need to exhibit the
    additional Python behaviors of the custom datatypes, additional steps must be
    taken to allow this.
    
    The most straightforward is to override specific columns as described at
    :ref:`reflection_overriding_columns`.  In this technique, we simply
    use reflection in combination with explicit :class:`_schema.Column` objects for those
    columns for which we want to use a custom or decorated datatype::
    
        >>> metadata_three = MetaData()
        >>> my_reflected_table = Table(
        ...     "my_table",
        ...     metadata_three,
        ...     Column("data", PickleType),
        ...     autoload_with=engine,
        ... )
    
    The ``my_reflected_table`` object above is reflected, and will load the
    definition of the "id" column from the SQLite database.  But for the "data"
    column, we've overridden the reflected object with an explicit :class:`_schema.Column`
    definition that includes our desired in-Python datatype, the
    :class:`.PickleType`. The reflection process will leave this :class:`_schema.Column`
    object intact::
    
        >>> my_reflected_table.c.data.type
        PickleType()
    
    A more elaborate way to convert from database-native type objects to custom
    datatypes is to use the :meth:`.DDLEvents.column_reflect` event handler.   If
    for example we knew that we wanted all :class:`.BLOB` datatypes to in fact be
    :class:`.PickleType`, we could set up a rule across the board::
    
    
        from sqlalchemy import BLOB
        from sqlalchemy import event
        from sqlalchemy import PickleType
        from sqlalchemy import Table
    
    
        @event.listens_for(Table, "column_reflect")
        def _setup_pickletype(inspector, table, column_info):
            if isinstance(column_info["type"], BLOB):
                column_info["type"] = PickleType()
    
    When the above code is invoked *before* any table reflection occurs (note also
    it should be invoked **only once** in the application, as it is a global rule),
    upon reflecting any :class:`_schema.Table` that includes a column with a :class:`.BLOB`
    datatype, the resulting datatype will be stored in the :class:`_schema.Column` object
    as :class:`.PickleType`.
    
    In practice, the above event-based approach would likely have additional rules
    in order to affect only those columns where the datatype is important, such as
    a lookup table of table names and possibly column names, or other heuristics
    in order to accurately determine which columns should be established with an
    in Python datatype.
    