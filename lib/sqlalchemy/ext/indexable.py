# ext/indexable.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php
# mypy: ignore-errors

"""
.. tab:: 中文

    在 ORM 映射类上定义具有“索引”属性的属性，这些属性用于具有 :class:`_types.Indexable` 类型的列。

    “索引”意味着该属性关联于某个 :class:`_types.Indexable` 列的某个元素，并使用预定义的索引访问它。
    :class:`_types.Indexable` 类型包括诸如 :class:`_types.ARRAY` 、 :class:`_types.JSON` 和 :class:`_postgresql.HSTORE` 等类型。

    :mod:`~sqlalchemy.ext.indexable` 扩展提供了一个类似 :class:`_schema.Column` 的接口，用于访问任意一个
    :class:`_types.Indexable` 类型列中的元素。在简单情况下，它可以被视为一个映射的 :class:`_schema.Column` 属性。

.. tab:: 英文

    Define attributes on ORM-mapped classes that have "index" attributes for
    columns with :class:`_types.Indexable` types.

    "index" means the attribute is associated with an element of an
    :class:`_types.Indexable` column with the predefined index to access it.
    The :class:`_types.Indexable` types include types such as
    :class:`_types.ARRAY`, :class:`_types.JSON` and
    :class:`_postgresql.HSTORE`.



    The :mod:`~sqlalchemy.ext.indexable` extension provides
    :class:`_schema.Column`-like interface for any element of an
    :class:`_types.Indexable` typed column. In simple cases, it can be
    treated as a :class:`_schema.Column` - mapped attribute.

摘要
========

Synopsis

.. tab:: 中文

    假设有一个 ``Person`` 模型，包含主键和一个 JSON 数据字段。虽然这个字段可以编码任意数量的元素，
    我们希望单独引用其中名为 ``name`` 的元素，并使其表现得像一个独立的列属性::

        from sqlalchemy import Column, JSON, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.indexable import index_property

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            name = index_property("data", "name")

    在上例中，``name`` 属性现在就像一个映射列一样工作。
    我们可以创建一个新的 ``Person`` 实例并为 ``name`` 属性赋值::

        >>> person = Person(name="Alchemist")

    现在可以访问该值::

        >>> person.name
        'Alchemist'

    其底层实现中，JSON 字段被初始化为一个新的空字典，并设置了对应字段::

        >>> person.data
        {'name': 'Alchemist'}

    该字段支持就地修改::

        >>> person.name = "Renamed"
        >>> person.name
        'Renamed'
        >>> person.data
        {'name': 'Renamed'}

    当使用 :class:`.index_property` 时，对索引结构的更改也会自动被跟踪为历史变更；我们无需使用
    :class:`~.mutable.MutableDict` 来为工作单元追踪这些变更。

    删除操作也能正常工作::

        >>> del person.name
        >>> person.data
        {}

    如上所示，删除 ``person.name`` 会从字典中移除该键值对，但不会删除整个字典。

    若访问缺失的键，将抛出 ``AttributeError``::

        >>> person = Person()
        >>> person.name
        AttributeError: 'name'

    除非你为其设置了默认值::

        >>> class Person(Base):
        ...     __tablename__ = "person"
        ...
        ...     id = Column(Integer, primary_key=True)
        ...     data = Column(JSON)
        ...
        ...     name = index_property("data", "name", default=None)  # 设置默认值

        >>> person = Person()
        >>> print(person.name)
        None

    这些属性在类级别同样可用。如下示例展示了如何使用 ``Person.name`` 生成带索引的 SQL 条件::

        >>> from sqlalchemy.orm import Session
        >>> session = Session()
        >>> query = session.query(Person).filter(Person.name == "Alchemist")

    上述查询等效于::

        >>> query = session.query(Person).filter(Person.data["name"] == "Alchemist")

    多个 :class:`.index_property` 对象可以级联使用，以实现多层索引::

        from sqlalchemy import Column, JSON, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.indexable import index_property

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            birthday = index_property("data", "birthday")
            year = index_property("birthday", "year")
            month = index_property("birthday", "month")
            day = index_property("birthday", "day")

    如上所示，以下查询::

        q = session.query(Person).filter(Person.year == "1980")

    在 PostgreSQL 后端中，该查询将被渲染为：

    .. sourcecode:: sql

        SELECT person.id, person.data
        FROM person
        WHERE person.data -> %(data_1)s -> %(param_1)s = %(param_2)s

.. tab:: 英文

    Given ``Person`` as a model with a primary key and JSON data field.
    While this field may have any number of elements encoded within it,
    we would like to refer to the element called ``name`` individually
    as a dedicated attribute which behaves like a standalone column::

        from sqlalchemy import Column, JSON, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.indexable import index_property

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            name = index_property("data", "name")

    Above, the ``name`` attribute now behaves like a mapped column.   We
    can compose a new ``Person`` and set the value of ``name``::

        >>> person = Person(name="Alchemist")

    The value is now accessible::

        >>> person.name
        'Alchemist'

    Behind the scenes, the JSON field was initialized to a new blank dictionary
    and the field was set::

        >>> person.data
        {'name': 'Alchemist'}

    The field is mutable in place::

        >>> person.name = "Renamed"
        >>> person.name
        'Renamed'
        >>> person.data
        {'name': 'Renamed'}

    When using :class:`.index_property`, the change that we make to the indexable
    structure is also automatically tracked as history; we no longer need
    to use :class:`~.mutable.MutableDict` in order to track this change
    for the unit of work.

    Deletions work normally as well::

        >>> del person.name
        >>> person.data
        {}

    Above, deletion of ``person.name`` deletes the value from the dictionary,
    but not the dictionary itself.

    A missing key will produce ``AttributeError``::

        >>> person = Person()
        >>> person.name
        AttributeError: 'name'

    Unless you set a default value::

        >>> class Person(Base):
        ...     __tablename__ = "person"
        ...
        ...     id = Column(Integer, primary_key=True)
        ...     data = Column(JSON)
        ...
        ...     name = index_property("data", "name", default=None)  # See default

        >>> person = Person()
        >>> print(person.name)
        None


    The attributes are also accessible at the class level.
    Below, we illustrate ``Person.name`` used to generate
    an indexed SQL criteria::

        >>> from sqlalchemy.orm import Session
        >>> session = Session()
        >>> query = session.query(Person).filter(Person.name == "Alchemist")

    The above query is equivalent to::

        >>> query = session.query(Person).filter(Person.data["name"] == "Alchemist")

    Multiple :class:`.index_property` objects can be chained to produce
    multiple levels of indexing::

        from sqlalchemy import Column, JSON, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.ext.indexable import index_property

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            birthday = index_property("data", "birthday")
            year = index_property("birthday", "year")
            month = index_property("birthday", "month")
            day = index_property("birthday", "day")

    Above, a query such as::

        q = session.query(Person).filter(Person.year == "1980")

    On a PostgreSQL backend, the above query will render as:

    .. sourcecode:: sql

        SELECT person.id, person.data
        FROM person
        WHERE person.data -> %(data_1)s -> %(param_1)s = %(param_2)s

默认值
==============

Default Values

.. tab:: 中文

    当被索引的数据结构不存在且执行设置操作时，:class:`.index_property` 包含一些特殊行为：

    * 对于传入的是整数索引值的 :class:`.index_property`，默认数据结构将是一个 Python 列表，
      列表中填充 ``None``，其长度至少为索引值加一；然后在该索引位置设置给定值。
      这意味着如果索引值为零，列表会被初始化为 ``[None]``，然后设置该值；
      如果索引值为五，列表会被初始化为 ``[None, None, None, None, None]``，然后设置第五个元素。
      注意：已存在的列表 **不会** 被原地扩展以容纳新的值。

    * 对于传入其他类型索引值（例如通常是字符串）的 :class:`.index_property`，
      默认数据结构将是 Python 字典。

    * 默认数据结构也可以通过 :paramref:`.index_property.datatype` 参数设置为任意 Python 可调用对象，
      此设置会覆盖上述规则。

.. tab:: 英文

    :class:`.index_property` includes special behaviors for when the indexed
    data structure does not exist, and a set operation is called:

    * For an :class:`.index_property` that is given an integer index value,
      the default data structure will be a Python list of ``None`` values,
      at least as long as the index value; the value is then set at its
      place in the list.  This means for an index value of zero, the list
      will be initialized to ``[None]`` before setting the given value,
      and for an index value of five, the list will be initialized to
      ``[None, None, None, None, None]`` before setting the fifth element
      to the given value.   Note that an existing list is **not** extended
      in place to receive a value.

    * for an :class:`.index_property` that is given any other kind of index
      value (e.g. strings usually), a Python dictionary is used as the
      default data structure.

    * The default data structure can be set to any Python callable using the
      :paramref:`.index_property.datatype` parameter, overriding the previous
      rules.


子类化
===========

Subclassing

.. tab:: 中文

    :class:`.index_property` 可以被子类化，尤其适用于需要在访问时自动转换值或 SQL 表达式的常见用例。
    下面是一个用于 PostgreSQL JSON 类型的常见示例，我们希望在访问时自动进行类型转换，并使用 ``astext()``::

        class pg_json_property(index_property):
            def __init__(self, attr_name, index, cast_type):
                super(pg_json_property, self).__init__(attr_name, index)
                self.cast_type = cast_type

            def expr(self, model):
                expr = super(pg_json_property, self).expr(model)
                return expr.astext.cast(self.cast_type)

    上述子类可与 PostgreSQL 专用的 :class:`_postgresql.JSON` 类型一起使用::

        from sqlalchemy import Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.dialects.postgresql import JSON

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            age = pg_json_property("data", "age", Integer)

    ``age`` 属性在实例级别的行为与之前相同；但在生成 SQL 时，
    将使用 PostgreSQL 的 ``->>`` 操作符进行索引访问，而不是常规的 ``->`` 操作符::

        >>> query = session.query(Person).filter(Person.age < 20)

    上述查询将被渲染为：

    .. sourcecode:: sql

        SELECT person.id, person.data
        FROM person
        WHERE CAST(person.data ->> %(data_1)s AS INTEGER) < %(param_1)s

.. tab:: 英文

    :class:`.index_property` can be subclassed, in particular for the common
    use case of providing coercion of values or SQL expressions as they are
    accessed.  Below is a common recipe for use with a PostgreSQL JSON type,
    where we want to also include automatic casting plus ``astext()``::

        class pg_json_property(index_property):
            def __init__(self, attr_name, index, cast_type):
                super(pg_json_property, self).__init__(attr_name, index)
                self.cast_type = cast_type

            def expr(self, model):
                expr = super(pg_json_property, self).expr(model)
                return expr.astext.cast(self.cast_type)

    The above subclass can be used with the PostgreSQL-specific
    version of :class:`_postgresql.JSON`::

        from sqlalchemy import Column, Integer
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.dialects.postgresql import JSON

        Base = declarative_base()


        class Person(Base):
            __tablename__ = "person"

            id = Column(Integer, primary_key=True)
            data = Column(JSON)

            age = pg_json_property("data", "age", Integer)

    The ``age`` attribute at the instance level works as before; however
    when rendering SQL, PostgreSQL's ``->>`` operator will be used
    for indexed access, instead of the usual index operator of ``->``::

        >>> query = session.query(Person).filter(Person.age < 20)

    The above query will render:

    .. sourcecode:: sql

        SELECT person.id, person.data
        FROM person
        WHERE CAST(person.data ->> %(data_1)s AS INTEGER) < %(param_1)s

"""  # noqa

from .. import inspect
from ..ext.hybrid import hybrid_property
from ..orm.attributes import flag_modified


__all__ = ["index_property"]


class index_property(hybrid_property):  # noqa
    """A property generator. The generated property describes an object
    attribute that corresponds to an :class:`_types.Indexable`
    column.

    .. seealso::

        :mod:`sqlalchemy.ext.indexable`

    """

    _NO_DEFAULT_ARGUMENT = object()

    def __init__(
        self,
        attr_name,
        index,
        default=_NO_DEFAULT_ARGUMENT,
        datatype=None,
        mutable=True,
        onebased=True,
    ):
        """Create a new :class:`.index_property`.

        :param attr_name:
            An attribute name of an `Indexable` typed column, or other
            attribute that returns an indexable structure.
        :param index:
            The index to be used for getting and setting this value.  This
            should be the Python-side index value for integers.
        :param default:
            A value which will be returned instead of `AttributeError`
            when there is not a value at given index.
        :param datatype: default datatype to use when the field is empty.
            By default, this is derived from the type of index used; a
            Python list for an integer index, or a Python dictionary for
            any other style of index.   For a list, the list will be
            initialized to a list of None values that is at least
            ``index`` elements long.
        :param mutable: if False, writes and deletes to the attribute will
            be disallowed.
        :param onebased: assume the SQL representation of this value is
            one-based; that is, the first index in SQL is 1, not zero.
        """

        if mutable:
            super().__init__(self.fget, self.fset, self.fdel, self.expr)
        else:
            super().__init__(self.fget, None, None, self.expr)
        self.attr_name = attr_name
        self.index = index
        self.default = default
        is_numeric = isinstance(index, int)
        onebased = is_numeric and onebased

        if datatype is not None:
            self.datatype = datatype
        else:
            if is_numeric:
                self.datatype = lambda: [None for x in range(index + 1)]
            else:
                self.datatype = dict
        self.onebased = onebased

    def _fget_default(self, err=None):
        if self.default == self._NO_DEFAULT_ARGUMENT:
            raise AttributeError(self.attr_name) from err
        else:
            return self.default

    def fget(self, instance):
        attr_name = self.attr_name
        column_value = getattr(instance, attr_name)
        if column_value is None:
            return self._fget_default()
        try:
            value = column_value[self.index]
        except (KeyError, IndexError) as err:
            return self._fget_default(err)
        else:
            return value

    def fset(self, instance, value):
        attr_name = self.attr_name
        column_value = getattr(instance, attr_name, None)
        if column_value is None:
            column_value = self.datatype()
            setattr(instance, attr_name, column_value)
        column_value[self.index] = value
        setattr(instance, attr_name, column_value)
        if attr_name in inspect(instance).mapper.attrs:
            flag_modified(instance, attr_name)

    def fdel(self, instance):
        attr_name = self.attr_name
        column_value = getattr(instance, attr_name)
        if column_value is None:
            raise AttributeError(self.attr_name)
        try:
            del column_value[self.index]
        except KeyError as err:
            raise AttributeError(self.attr_name) from err
        else:
            setattr(instance, attr_name, column_value)
            flag_modified(instance, attr_name)

    def expr(self, model):
        column = getattr(model, self.attr_name)
        index = self.index
        if self.onebased:
            index += 1
        return column[index]
