# ext/hybrid.py
# Copyright (C) 2005-2025 the SQLAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of SQLAlchemy and is released under
# the MIT License: https://www.opensource.org/licenses/mit-license.php

r"""
.. tab:: 中文

    定义具有“混合”行为的 ORM 映射类属性。

    “混合”意味着属性在类级别和实例级别具有不同的行为。

    :mod:`~sqlalchemy.ext.hybrid` 扩展提供了一种特殊形式的方法装饰器，并且对 SQLAlchemy 其余部分的依赖最小化。其基本操作理论可以与任何基于描述符的表达式系统一起工作。

    考虑一个映射 ``Interval``，表示整数的 ``start`` 和 ``end`` 值。我们可以在映射类上定义更高层次的函数，这些函数在类级别生成 SQL 表达式，在实例级别进行 Python 表达式求值。下面，使用 :class:`.hybrid_method` 或 :class:`.hybrid_property` 装饰的每个函数可以接收 ``self`` 作为类的实例，或者根据上下文直接接收类本身::

        from __future__ import annotations

        from sqlalchemy.ext.hybrid import hybrid_method
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Interval(Base):
            __tablename__ = "interval"

            id: Mapped[int] = mapped_column(primary_key=True)
            start: Mapped[int]
            end: Mapped[int]

            def __init__(self, start: int, end: int):
                self.start = start
                self.end = end

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @hybrid_method
            def contains(self, point: int) -> bool:
                return (self.start <= point) & (point <= self.end)

            @hybrid_method
            def intersects(self, other: Interval) -> bool:
                return self.contains(other.start) | self.contains(other.end)

    上面的 ``length`` 属性返回 ``end`` 和 ``start`` 属性之间的差值。对于 ``Interval`` 实例，这个减法操作在 Python 中进行，使用常规的 Python 描述符机制::

        >>> i1 = Interval(5, 10)
        >>> i1.length
        5

    当处理 ``Interval`` 类本身时，:class:`.hybrid_property` 描述符根据 ``Interval`` 类作为参数来求值函数体，当使用 SQLAlchemy 表达式机制求值时，返回一个新的 SQL 表达式：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Interval.length))
        {printsql}SELECT interval."end" - interval.start AS length
        FROM interval{stop}


        >>> print(select(Interval).filter(Interval.length > 10))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval."end" - interval.start > :param_1

    使用混合属性时，像 :meth:`.Select.filter_by` 这样的过滤方法也得到了支持：

    .. sourcecode:: pycon+sql

        >>> print(select(Interval).filter_by(length=5))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval."end" - interval.start = :param_1

    ``Interval`` 类示例还展示了两个方法，``contains()`` 和 ``intersects()``，它们都使用 :class:`.hybrid_method` 装饰器。这个装饰器将同样的思想应用于方法，正如 :class:`.hybrid_property` 对属性所做的那样。这些方法返回布尔值，并利用 Python 的 ``|`` 和 ``&`` 位运算符来生成等效的实例级和 SQL 表达式级布尔行为：

    .. sourcecode:: pycon+sql

        >>> i1.contains(6)
        True
        >>> i1.contains(15)
        False
        >>> i1.intersects(Interval(7, 18))
        True
        >>> i1.intersects(Interval(25, 29))
        False

        >>> print(select(Interval).filter(Interval.contains(15)))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval.start <= :start_1 AND interval."end" > :end_1{stop}

        >>> ia = aliased(Interval)
        >>> print(select(Interval, ia).filter(Interval.intersects(ia)))
        {printsql}SELECT interval.id, interval.start,
        interval."end", interval_1.id AS interval_1_id,
        interval_1.start AS interval_1_start, interval_1."end" AS interval_1_end
        FROM interval, interval AS interval_1
        WHERE interval.start <= interval_1.start
            AND interval."end" > interval_1.start
            OR interval.start <= interval_1."end"
            AND interval."end" > interval_1."end"{stop}

.. tab:: 英文

    Define attributes on ORM-mapped classes that have "hybrid" behavior.

    "hybrid" means the attribute has distinct behaviors defined at the
    class level and at the instance level.

    The :mod:`~sqlalchemy.ext.hybrid` extension provides a special form of
    method decorator and has minimal dependencies on the rest of SQLAlchemy.
    Its basic theory of operation can work with any descriptor-based expression
    system.

    Consider a mapping ``Interval``, representing integer ``start`` and ``end``
    values. We can define higher level functions on mapped classes that produce SQL
    expressions at the class level, and Python expression evaluation at the
    instance level.  Below, each function decorated with :class:`.hybrid_method` or
    :class:`.hybrid_property` may receive ``self`` as an instance of the class, or
    may receive the class directly, depending on context::

        from __future__ import annotations

        from sqlalchemy.ext.hybrid import hybrid_method
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Interval(Base):
            __tablename__ = "interval"

            id: Mapped[int] = mapped_column(primary_key=True)
            start: Mapped[int]
            end: Mapped[int]

            def __init__(self, start: int, end: int):
                self.start = start
                self.end = end

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @hybrid_method
            def contains(self, point: int) -> bool:
                return (self.start <= point) & (point <= self.end)

            @hybrid_method
            def intersects(self, other: Interval) -> bool:
                return self.contains(other.start) | self.contains(other.end)

    Above, the ``length`` property returns the difference between the
    ``end`` and ``start`` attributes.  With an instance of ``Interval``,
    this subtraction occurs in Python, using normal Python descriptor
    mechanics::

        >>> i1 = Interval(5, 10)
        >>> i1.length
        5

    When dealing with the ``Interval`` class itself, the :class:`.hybrid_property`
    descriptor evaluates the function body given the ``Interval`` class as
    the argument, which when evaluated with SQLAlchemy expression mechanics
    returns a new SQL expression:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Interval.length))
        {printsql}SELECT interval."end" - interval.start AS length
        FROM interval{stop}


        >>> print(select(Interval).filter(Interval.length > 10))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval."end" - interval.start > :param_1

    Filtering methods such as :meth:`.Select.filter_by` are supported
    with hybrid attributes as well:

    .. sourcecode:: pycon+sql

        >>> print(select(Interval).filter_by(length=5))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval."end" - interval.start = :param_1

    The ``Interval`` class example also illustrates two methods,
    ``contains()`` and ``intersects()``, decorated with
    :class:`.hybrid_method`. This decorator applies the same idea to
    methods that :class:`.hybrid_property` applies to attributes.   The
    methods return boolean values, and take advantage of the Python ``|``
    and ``&`` bitwise operators to produce equivalent instance-level and
    SQL expression-level boolean behavior:

    .. sourcecode:: pycon+sql

        >>> i1.contains(6)
        True
        >>> i1.contains(15)
        False
        >>> i1.intersects(Interval(7, 18))
        True
        >>> i1.intersects(Interval(25, 29))
        False

        >>> print(select(Interval).filter(Interval.contains(15)))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE interval.start <= :start_1 AND interval."end" > :end_1{stop}

        >>> ia = aliased(Interval)
        >>> print(select(Interval, ia).filter(Interval.intersects(ia)))
        {printsql}SELECT interval.id, interval.start,
        interval."end", interval_1.id AS interval_1_id,
        interval_1.start AS interval_1_start, interval_1."end" AS interval_1_end
        FROM interval, interval AS interval_1
        WHERE interval.start <= interval_1.start
            AND interval."end" > interval_1.start
            OR interval.start <= interval_1."end"
            AND interval."end" > interval_1."end"{stop}

.. _hybrid_distinct_expression:

定义不同于属性行为的表达式行为
--------------------------------------------------------------

Defining Expression Behavior Distinct from Attribute Behavior

.. tab:: 中文

    在前一节中，我们在 ``Interval.contains`` 和 ``Interval.intersects`` 方法中使用 ``&`` 和 ``|`` 位运算符时是幸运的，因为我们的函数操作的是两个布尔值，并返回一个新的布尔值。在许多情况下，Python 函数和 SQLAlchemy SQL 表达式的构造之间有足够的差异，因此应该定义两个独立的 Python 表达式。:mod:`~sqlalchemy.ext.hybrid` 装饰器定义了一个 **修饰符** :meth:`.hybrid_property.expression` 用于此目的。作为示例，我们将定义区间的半径，这需要使用绝对值函数::

        from sqlalchemy import ColumnElement
        from sqlalchemy import Float
        from sqlalchemy import func
        from sqlalchemy import type_coerce


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self) -> float:
                return abs(self.length) / 2

            @radius.inplace.expression
            @classmethod
            def _radius_expression(cls) -> ColumnElement[float]:
                return type_coerce(func.abs(cls.length) / 2, Float)

    在上面的示例中，首先将 :class:`.hybrid_property` 分配给 ``Interval.radius``，然后通过名为 ``Interval._radius_expression`` 的后续方法进行修改，该方法使用装饰器 ``@radius.inplace.expression``，将两个修饰符 :attr:`.hybrid_property.inplace` 和 :attr:`.hybrid_property.expression` 链接在一起。使用 :attr:`.hybrid_property.inplace` 表明 :meth:`.hybrid_property.expression` 修饰符应直接修改现有的混合对象 ``Interval.radius``，而不是创建一个新对象。关于这个修饰符及其原因的讨论将在下一节 :ref:`hybrid_pep484_naming` 中讨论。使用 ``@classmethod`` 是可选的，严格来说，它只是为了给类型工具一个提示，表明 ``cls`` 在这种情况下应该是 ``Interval`` 类，而不是 ``Interval`` 的实例。

    .. note::

        :attr:`.hybrid_property.inplace` 以及为正确的类型支持而使用 ``@classmethod``，自 SQLAlchemy 2.0.4 起可用，早期版本不支持。

    现在，``Interval.radius`` 包含了一个表达式元素，当在类级别访问 ``Interval.radius`` 时，SQL 函数 ``ABS()`` 被返回：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Interval).filter(Interval.radius > 5))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE abs(interval."end" - interval.start) / :abs_1 > :param_1

.. tab:: 英文

    In the previous section, our usage of the ``&`` and ``|`` bitwise operators
    within the ``Interval.contains`` and ``Interval.intersects`` methods was
    fortunate, considering our functions operated on two boolean values to return a
    new one. In many cases, the construction of an in-Python function and a
    SQLAlchemy SQL expression have enough differences that two separate Python
    expressions should be defined. The :mod:`~sqlalchemy.ext.hybrid` decorator
    defines a **modifier** :meth:`.hybrid_property.expression` for this purpose. As an
    example we'll define the radius of the interval, which requires the usage of
    the absolute value function::

        from sqlalchemy import ColumnElement
        from sqlalchemy import Float
        from sqlalchemy import func
        from sqlalchemy import type_coerce


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self) -> float:
                return abs(self.length) / 2

            @radius.inplace.expression
            @classmethod
            def _radius_expression(cls) -> ColumnElement[float]:
                return type_coerce(func.abs(cls.length) / 2, Float)

    In the above example, the :class:`.hybrid_property` first assigned to the
    name ``Interval.radius`` is amended by a subsequent method called
    ``Interval._radius_expression``, using the decorator
    ``@radius.inplace.expression``, which chains together two modifiers
    :attr:`.hybrid_property.inplace` and :attr:`.hybrid_property.expression`.
    The use of :attr:`.hybrid_property.inplace` indicates that the
    :meth:`.hybrid_property.expression` modifier should mutate the
    existing hybrid object at ``Interval.radius`` in place, without creating a
    new object.   Notes on this modifier and its
    rationale are discussed in the next section :ref:`hybrid_pep484_naming`.
    The use of ``@classmethod`` is optional, and is strictly to give typing
    tools a hint that ``cls`` in this case is expected to be the ``Interval``
    class, and not an instance of ``Interval``.

    .. note:: :attr:`.hybrid_property.inplace` as well as the use of ``@classmethod``
       for proper typing support are available as of SQLAlchemy 2.0.4, and will
       not work in earlier versions.

    With ``Interval.radius`` now including an expression element, the SQL
    function ``ABS()`` is returned when accessing ``Interval.radius``
    at the class level:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(Interval).filter(Interval.radius > 5))
        {printsql}SELECT interval.id, interval.start, interval."end"
        FROM interval
        WHERE abs(interval."end" - interval.start) / :abs_1 > :param_1


.. _hybrid_pep484_naming:

使用“inplace”创建符合 pep-484 的混合属性
---------------------------------------------------------------

Using ``inplace`` to create pep-484 compliant hybrid properties

.. tab:: 中文

    在前一节中，展示了一个 :class:`.hybrid_property` 装饰器，其中包括两个独立的方法级函数，它们都被装饰以生成一个名为 ``Interval.radius`` 的单一对象属性。实际上，我们可以为 :class:`.hybrid_property` 使用几种不同的修饰符，包括 :meth:`.hybrid_property.expression`、:meth:`.hybrid_property.setter` 和 :meth:`.hybrid_property.update_expression`。

    SQLAlchemy 的 :class:`.hybrid_property` 装饰器的设计目的是，像 Python 内建的 ``@property`` 装饰器一样，可以重复定义属性，每次使用 **相同的属性名**，就像下面的示例展示了如何使用 :meth:`.hybrid_property.setter` 和 :meth:`.hybrid_property.expression` 来修饰 ``Interval.radius`` 描述符::

        # 正确使用，但不被 pep-484 工具接受


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self):
                return abs(self.length) / 2

            @radius.setter
            def radius(self, value):
                self.length = value * 2

            @radius.expression
            def radius(cls):
                return type_coerce(func.abs(cls.length) / 2, Float)

    如上所示，存在三个 ``Interval.radius`` 方法，但由于每个方法都被装饰，首先使用 :class:`.hybrid_property` 装饰器，然后使用 ``@radius`` 名称本身，最终效果是 ``Interval.radius`` 是一个包含三个不同功能的单一属性。此使用风格源自 Python 文档中的 ``@property`` 用法
    <https://docs.python.org/3/library/functions.html#property>_。
    需要注意的是，由于 ``@property`` 和 :class:`.hybrid_property` 的工作原理，每次都会 **创建描述符的副本** 。也就是说，每次调用 ``@radius.expression``、``@radius.setter`` 等时，都会完全创建一个新对象。这使得可以在子类中重新定义属性，而不会出现问题（有关如何使用此方法，请参见本节后面的 :ref:`hybrid_reuse_subclass`）。

    然而，上述方法与类型工具（如 mypy 和 pyright）不兼容。Python 自己的 ``@property`` 装饰器没有这个限制，仅仅因为
    `这些工具硬编码了 @property 的行为
    <https://github.com/python/typing/discussions/1102>`_，这意味着 SQLAlchemy 在 :pep:`484` 合规性下无法使用此语法。

    为了在保持类型合规的同时生成合理的语法，:attr:`.hybrid_property.inplace` 装饰器允许使用不同的方法名称重新使用相同的装饰器，同时仍然生成一个单一的装饰器::

        # 正确使用，且被 pep-484 工具接受


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self) -> float:
                return abs(self.length) / 2

            @radius.inplace.setter
            def _radius_setter(self, value: float) -> None:
                # 仅为示例
                self.length = value * 2

            @radius.inplace.expression
            @classmethod
            def _radius_expression(cls) -> ColumnElement[float]:
                return type_coerce(func.abs(cls.length) / 2, Float)

    使用 :attr:`.hybrid_property.inplace` 进一步限定了装饰器的使用，即不应创建新副本，从而保持 ``Interval.radius`` 名称，同时允许 ``Interval._radius_setter`` 和 ``Interval._radius_expression`` 使用不同的名称。

    .. versionadded:: 2.0.4 增加了 :attr:`.hybrid_property.inplace`，允许更简洁地构建复合的 :class:`.hybrid_property` 对象，而无需重复使用方法名称。同时，允许在 :attr:`.hybrid_property.expression`、:attr:`.hybrid_property.update_expression` 和 :attr:`.hybrid_property.comparator` 中使用 ``@classmethod``，使得类型工具能够在方法签名中识别 ``cls`` 为类而非实例。

.. tab:: 英文

    In the previous section, a :class:`.hybrid_property` decorator is illustrated
    which includes two separate method-level functions being decorated, both
    to produce a single object attribute referenced as ``Interval.radius``.
    There are actually several different modifiers we can use for
    :class:`.hybrid_property` including :meth:`.hybrid_property.expression`,
    :meth:`.hybrid_property.setter` and :meth:`.hybrid_property.update_expression`.

    SQLAlchemy's :class:`.hybrid_property` decorator intends that adding on these
    methods may be done in the identical manner as Python's built-in
    ``@property`` decorator, where idiomatic use is to continue to redefine the
    attribute repeatedly, using the **same attribute name** each time, as in the
    example below that illustrates the use of :meth:`.hybrid_property.setter` and
    :meth:`.hybrid_property.expression` for the ``Interval.radius`` descriptor::

        # correct use, however is not accepted by pep-484 tooling


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self):
                return abs(self.length) / 2

            @radius.setter
            def radius(self, value):
                self.length = value * 2

            @radius.expression
            def radius(cls):
                return type_coerce(func.abs(cls.length) / 2, Float)

    Above, there are three ``Interval.radius`` methods, but as each are decorated,
    first by the :class:`.hybrid_property` decorator and then by the
    ``@radius`` name itself, the end effect is that ``Interval.radius`` is
    a single attribute with three different functions contained within it.
    This style of use is taken from `Python's documented use of @property
    <https://docs.python.org/3/library/functions.html#property>`_.
    It is important to note that the way both ``@property`` as well as
    :class:`.hybrid_property` work, a **copy of the descriptor is made each time**.
    That is, each call to ``@radius.expression``, ``@radius.setter`` etc.
    make a new object entirely.  This allows the attribute to be re-defined in
    subclasses without issue (see :ref:`hybrid_reuse_subclass` later in this
    section for how this is used).

    However, the above approach is not compatible with typing tools such as
    mypy and pyright.  Python's own ``@property`` decorator does not have this
    limitation only because
    `these tools hardcode the behavior of @property
    <https://github.com/python/typing/discussions/1102>`_, meaning this syntax
    is not available to SQLAlchemy under :pep:`484` compliance.

    In order to produce a reasonable syntax while remaining typing compliant,
    the :attr:`.hybrid_property.inplace` decorator allows the same
    decorator to be re-used with different method names, while still producing
    a single decorator under one name::

        # correct use which is also accepted by pep-484 tooling


        class Interval(Base):
            # ...

            @hybrid_property
            def radius(self) -> float:
                return abs(self.length) / 2

            @radius.inplace.setter
            def _radius_setter(self, value: float) -> None:
                # for example only
                self.length = value * 2

            @radius.inplace.expression
            @classmethod
            def _radius_expression(cls) -> ColumnElement[float]:
                return type_coerce(func.abs(cls.length) / 2, Float)

    Using :attr:`.hybrid_property.inplace` further qualifies the use of the
    decorator that a new copy should not be made, thereby maintaining the
    ``Interval.radius`` name while allowing additional methods
    ``Interval._radius_setter`` and ``Interval._radius_expression`` to be
    differently named.


    .. versionadded:: 2.0.4 Added :attr:`.hybrid_property.inplace` to allow
       less verbose construction of composite :class:`.hybrid_property` objects
       while not having to use repeated method names.   Additionally allowed the
       use of ``@classmethod`` within :attr:`.hybrid_property.expression`,
       :attr:`.hybrid_property.update_expression`, and
       :attr:`.hybrid_property.comparator` to allow typing tools to identify
       ``cls`` as a class and not an instance in the method signature.

定义 Setter
----------------

Defining Setters

.. tab:: 中文

    :meth:`.hybrid_property.setter` 修饰符允许构建自定义的 setter 方法，用于修改对象上的值::

        class Interval(Base):
            # ...

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @length.inplace.setter
            def _length_setter(self, value: int) -> None:
                self.end = self.start + value

    现在，当设置属性时，会调用 ``length(self, value)`` 方法::

        >>> i1 = Interval(5, 10)
        >>> i1.length
        5
        >>> i1.length = 12
        >>> i1.end
        17

.. tab:: 英文

    The :meth:`.hybrid_property.setter` modifier allows the construction of a
    custom setter method, that can modify values on the object::

        class Interval(Base):
            # ...

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @length.inplace.setter
            def _length_setter(self, value: int) -> None:
                self.end = self.start + value

    The ``length(self, value)`` method is now called upon set::

        >>> i1 = Interval(5, 10)
        >>> i1.length
        5
        >>> i1.length = 12
        >>> i1.end
        17

.. _hybrid_bulk_update:

允许批量 ORM 更新
------------------------

Allowing Bulk ORM Update

.. tab:: 中文

    混合属性可以定义一个用于 ORM 启用的更新操作的自定义 “UPDATE” 处理器，从而允许混合属性在更新语句的 SET 子句中使用。

    通常，当混合属性与 :func:`_sql.update` 一起使用时，其 SQL 表达式会作为 SET 子句中目标列的替代。如果我们的 ``Interval`` 类中有一个名为 ``start_point`` 的混合属性，关联到 ``Interval.start``，那么它可以被直接替代使用::

        from sqlalchemy import update

        stmt = update(Interval).values({Interval.start_point: 10})

    然而，当使用像 ``Interval.length`` 这样的复合混合属性时，该混合属性代表多个列。我们可以设置一个处理器来处理传入 VALUES 表达式中的值，该值会影响这些列，这可以通过 :meth:`.hybrid_property.update_expression` 装饰器来实现。一个与我们 setter 类似的处理器可以这样定义::

        from typing import List, Tuple, Any


        class Interval(Base):
            # ...

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @length.inplace.setter
            def _length_setter(self, value: int) -> None:
                self.end = self.start + value

            @length.inplace.update_expression
            def _length_update_expression(
                cls, value: Any
            ) -> List[Tuple[Any, Any]]:
                return [(cls.end, cls.start + value)]

    如上所示，如果我们在 UPDATE 表达式中使用 ``Interval.length``，我们会得到一个混合的 SET 表达式：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import update
        >>> print(update(Interval).values({Interval.length: 25}))
        {printsql}UPDATE interval SET "end"=(interval.start + :start_1)

    这个 SET 表达式会被 ORM 自动处理。

    .. seealso::

        :ref:`orm_expression_update_delete` - 包含关于 ORM 启用的 UPDATE 语句的背景信息

.. tab:: 英文

    A hybrid can define a custom "UPDATE" handler for when using
    ORM-enabled updates, allowing the hybrid to be used in the
    SET clause of the update.

    Normally, when using a hybrid with :func:`_sql.update`, the SQL
    expression is used as the column that's the target of the SET.  If our
    ``Interval`` class had a hybrid ``start_point`` that linked to
    ``Interval.start``, this could be substituted directly::

        from sqlalchemy import update

        stmt = update(Interval).values({Interval.start_point: 10})

    However, when using a composite hybrid like ``Interval.length``, this
    hybrid represents more than one column.   We can set up a handler that will
    accommodate a value passed in the VALUES expression which can affect
    this, using the :meth:`.hybrid_property.update_expression` decorator.
    A handler that works similarly to our setter would be::

        from typing import List, Tuple, Any


        class Interval(Base):
            # ...

            @hybrid_property
            def length(self) -> int:
                return self.end - self.start

            @length.inplace.setter
            def _length_setter(self, value: int) -> None:
                self.end = self.start + value

            @length.inplace.update_expression
            def _length_update_expression(
                cls, value: Any
            ) -> List[Tuple[Any, Any]]:
                return [(cls.end, cls.start + value)]

    Above, if we use ``Interval.length`` in an UPDATE expression, we get
    a hybrid SET expression:

    .. sourcecode:: pycon+sql


        >>> from sqlalchemy import update
        >>> print(update(Interval).values({Interval.length: 25}))
        {printsql}UPDATE interval SET "end"=(interval.start + :start_1)

    This SET expression is accommodated by the ORM automatically.

    .. seealso::

        :ref:`orm_expression_update_delete` - includes background on ORM-enabled
        UPDATE statements


使用关系
--------------------------

Working with Relationships

.. tab:: 中文

    在创建适用于关联对象的混合属性时，与基于列的数据相比，没有本质的区别。不过，对于这些混合属性，通常更需要使用不同的表达式。我们将说明的两种变体是“依赖连接（join-dependent）”的混合属性和“相关子查询（correlated subquery）”的混合属性。

.. tab:: 英文

    There's no essential difference when creating hybrids that work with
    related objects as opposed to column-based data. The need for distinct
    expressions tends to be greater.  The two variants we'll illustrate
    are the "join-dependent" hybrid, and the "correlated subquery" hybrid.

连接依赖关系混合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Join-Dependent Relationship Hybrid

.. tab:: 中文

    来看如下的声明式映射，它将 ``User`` 和 ``SavingsAccount`` 关联起来::

        from __future__ import annotations

        from decimal import Decimal
        from typing import cast
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Numeric
        from sqlalchemy import String
        from sqlalchemy import SQLColumnExpression
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class SavingsAccount(Base):
            __tablename__ = "account"
            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            balance: Mapped[Decimal] = mapped_column(Numeric(15, 5))

            owner: Mapped[User] = relationship(back_populates="accounts")


        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

            accounts: Mapped[List[SavingsAccount]] = relationship(
                back_populates="owner", lazy="selectin"
            )

            @hybrid_property
            def balance(self) -> Optional[Decimal]:
                if self.accounts:
                    return self.accounts[0].balance
                else:
                    return None

            @balance.inplace.setter
            def _balance_setter(self, value: Optional[Decimal]) -> None:
                assert value is not None

                if not self.accounts:
                    account = SavingsAccount(owner=self)
                else:
                    account = self.accounts[0]
                account.balance = value

            @balance.inplace.expression
            @classmethod
            def _balance_expression(cls) -> SQLColumnExpression[Optional[Decimal]]:
                return cast(
                    "SQLColumnExpression[Optional[Decimal]]",
                    SavingsAccount.balance,
                )

    上述混合属性 ``balance`` 处理的是该用户账户列表中的第一个 ``SavingsAccount`` 条目。
    在 Python 层的 getter/setter 方法中，可以将 ``accounts`` 当作存在于 ``self`` 上的 Python 列表来操作。

    .. tip:: 上例中的 ``User.balance`` getter 会访问 ``self.accounts`` 集合，而该集合通常通过在 ``User.balance`` 上配置的 :func:`_orm.relationship` 使用 :func:`.selectinload` 加载策略来加载。如果在 :func:`_orm.relationship` 上未显式指定加载策略，默认策略为 :func:`.lazyload`，它会按需发出 SQL 查询。在使用 asyncio 时，不支持按需加载器（如 :func:`.lazyload`），因此在使用 asyncio 时应注意确保该混合访问器可以访问 ``self.accounts`` 集合。

    在表达式层面，期望 ``User`` 类在使用时有合适的上下文，即会存在与 ``SavingsAccount`` 的合适连接：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(
        ...     select(User, User.balance)
        ...     .join(User.accounts)
        ...     .filter(User.balance > 5000)
        ... )
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name,
        account.balance AS account_balance
        FROM "user" JOIN account ON "user".id = account.user_id
        WHERE account.balance > :balance_1

    但需要注意的是，虽然在实例层级的访问器中需要担心 ``self.accounts`` 是否存在，而在 SQL 表达式层中，这一问题以另一种方式体现，即我们通常会使用外连接：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy import or_
        >>> print(
        ...     select(User, User.balance)
        ...     .outerjoin(User.accounts)
        ...     .filter(or_(User.balance < 5000, User.balance == None))
        ... )
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name,
        account.balance AS account_balance
        FROM "user" LEFT OUTER JOIN account ON "user".id = account.user_id
        WHERE account.balance <  :balance_1 OR account.balance IS NULL


.. tab:: 英文

    Consider the following declarative
    mapping which relates a ``User`` to a ``SavingsAccount``::

        from __future__ import annotations

        from decimal import Decimal
        from typing import cast
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import Numeric
        from sqlalchemy import String
        from sqlalchemy import SQLColumnExpression
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class SavingsAccount(Base):
            __tablename__ = "account"
            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            balance: Mapped[Decimal] = mapped_column(Numeric(15, 5))

            owner: Mapped[User] = relationship(back_populates="accounts")


        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

            accounts: Mapped[List[SavingsAccount]] = relationship(
                back_populates="owner", lazy="selectin"
            )

            @hybrid_property
            def balance(self) -> Optional[Decimal]:
                if self.accounts:
                    return self.accounts[0].balance
                else:
                    return None

            @balance.inplace.setter
            def _balance_setter(self, value: Optional[Decimal]) -> None:
                assert value is not None

                if not self.accounts:
                    account = SavingsAccount(owner=self)
                else:
                    account = self.accounts[0]
                account.balance = value

            @balance.inplace.expression
            @classmethod
            def _balance_expression(cls) -> SQLColumnExpression[Optional[Decimal]]:
                return cast(
                    "SQLColumnExpression[Optional[Decimal]]",
                    SavingsAccount.balance,
                )

    The above hybrid property ``balance`` works with the first
    ``SavingsAccount`` entry in the list of accounts for this user.   The
    in-Python getter/setter methods can treat ``accounts`` as a Python
    list available on ``self``.

    .. tip:: The ``User.balance`` getter in the above example accesses the
       ``self.acccounts`` collection, which will normally be loaded via the
       :func:`.selectinload` loader strategy configured on the ``User.balance``
       :func:`_orm.relationship`. The default loader strategy when not otherwise
       stated on :func:`_orm.relationship` is :func:`.lazyload`, which emits SQL on
       demand. When using asyncio, on-demand loaders such as :func:`.lazyload` are
       not supported, so care should be taken to ensure the ``self.accounts``
       collection is accessible to this hybrid accessor when using asyncio.

    At the expression level, it's expected that the ``User`` class will
    be used in an appropriate context such that an appropriate join to
    ``SavingsAccount`` will be present:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(
        ...     select(User, User.balance)
        ...     .join(User.accounts)
        ...     .filter(User.balance > 5000)
        ... )
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name,
        account.balance AS account_balance
        FROM "user" JOIN account ON "user".id = account.user_id
        WHERE account.balance > :balance_1

    Note however, that while the instance level accessors need to worry
    about whether ``self.accounts`` is even present, this issue expresses
    itself differently at the SQL expression level, where we basically
    would use an outer join:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> from sqlalchemy import or_
        >>> print(
        ...     select(User, User.balance)
        ...     .outerjoin(User.accounts)
        ...     .filter(or_(User.balance < 5000, User.balance == None))
        ... )
        {printsql}SELECT "user".id AS user_id, "user".name AS user_name,
        account.balance AS account_balance
        FROM "user" LEFT OUTER JOIN account ON "user".id = account.user_id
        WHERE account.balance <  :balance_1 OR account.balance IS NULL

相关子查询关系混合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Correlated Subquery Relationship Hybrid

.. tab:: 中文

    当然，我们也可以选择不依赖外部查询中的连接用法，而是使用相关子查询，它可以更便捷地封装进单个列表达式中。相关子查询更具可移植性，但在 SQL 层通常性能较差。借助 :ref:`mapper_column_property_sql_expressions` 中展示的技术，我们可以调整 ``SavingsAccount`` 示例，使其聚合 *所有* 账户的余额，并为列表达式使用相关子查询::

        from __future__ import annotations

        from decimal import Decimal
        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Numeric
        from sqlalchemy import select
        from sqlalchemy import SQLColumnExpression
        from sqlalchemy import String
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class SavingsAccount(Base):
            __tablename__ = "account"
            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            balance: Mapped[Decimal] = mapped_column(Numeric(15, 5))

            owner: Mapped[User] = relationship(back_populates="accounts")


        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

            accounts: Mapped[List[SavingsAccount]] = relationship(
                back_populates="owner", lazy="selectin"
            )

            @hybrid_property
            def balance(self) -> Decimal:
                return sum(
                    (acc.balance for acc in self.accounts), start=Decimal("0")
                )

            @balance.inplace.expression
            @classmethod
            def _balance_expression(cls) -> SQLColumnExpression[Decimal]:
                return (
                    select(func.sum(SavingsAccount.balance))
                    .where(SavingsAccount.user_id == cls.id)
                    .label("total_balance")
                )

    上述方法会为我们生成 ``balance`` 列，该列渲染为一个相关 SELECT 子查询：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(User).filter(User.balance > 400))
        {printsql}SELECT "user".id, "user".name
        FROM "user"
        WHERE (
            SELECT sum(account.balance) AS sum_1 FROM account
            WHERE account.user_id = "user".id
        ) > :param_1

.. tab:: 英文

    We can, of course, forego being dependent on the enclosing query's usage
    of joins in favor of the correlated subquery, which can portably be packed
    into a single column expression. A correlated subquery is more portable, but
    often performs more poorly at the SQL level. Using the same technique
    illustrated at :ref:`mapper_column_property_sql_expressions`,
    we can adjust our ``SavingsAccount`` example to aggregate the balances for
    *all* accounts, and use a correlated subquery for the column expression::

        from __future__ import annotations

        from decimal import Decimal
        from typing import List

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Numeric
        from sqlalchemy import select
        from sqlalchemy import SQLColumnExpression
        from sqlalchemy import String
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class SavingsAccount(Base):
            __tablename__ = "account"
            id: Mapped[int] = mapped_column(primary_key=True)
            user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
            balance: Mapped[Decimal] = mapped_column(Numeric(15, 5))

            owner: Mapped[User] = relationship(back_populates="accounts")


        class User(Base):
            __tablename__ = "user"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str] = mapped_column(String(100))

            accounts: Mapped[List[SavingsAccount]] = relationship(
                back_populates="owner", lazy="selectin"
            )

            @hybrid_property
            def balance(self) -> Decimal:
                return sum(
                    (acc.balance for acc in self.accounts), start=Decimal("0")
                )

            @balance.inplace.expression
            @classmethod
            def _balance_expression(cls) -> SQLColumnExpression[Decimal]:
                return (
                    select(func.sum(SavingsAccount.balance))
                    .where(SavingsAccount.user_id == cls.id)
                    .label("total_balance")
                )

    The above recipe will give us the ``balance`` column which renders
    a correlated SELECT:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(User).filter(User.balance > 400))
        {printsql}SELECT "user".id, "user".name
        FROM "user"
        WHERE (
            SELECT sum(account.balance) AS sum_1 FROM account
            WHERE account.user_id = "user".id
        ) > :param_1


.. _hybrid_custom_comparators:

构建自定义比较器
---------------------------

Building Custom Comparators

.. tab:: 中文

    混合属性还包括一个辅助功能，允许构建自定义比较器（comparator）。比较器对象允许对每一个 SQLAlchemy 表达式操作符的行为进行单独定制。它们在创建在 SQL 端具有高度特殊行为的自定义类型时非常有用。

    .. note:: 本节引入的 :meth:`.hybrid_property.comparator` 装饰器 **替代** 了
       :meth:`.hybrid_property.expression` 装饰器。两者不能同时使用。

    下面的示例类允许对名为 ``word_insensitive`` 的属性进行不区分大小写的比较::

        from __future__ import annotations

        from typing import Any

        from sqlalchemy import ColumnElement
        from sqlalchemy import func
        from sqlalchemy.ext.hybrid import Comparator
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class CaseInsensitiveComparator(Comparator[str]):
            def __eq__(self, other: Any) -> ColumnElement[bool]:  # type: ignore[override]  # noqa: E501
                return func.lower(self.__clause_element__()) == func.lower(other)


        class SearchWord(Base):
            __tablename__ = "searchword"

            id: Mapped[int] = mapped_column(primary_key=True)
            word: Mapped[str]

            @hybrid_property
            def word_insensitive(self) -> str:
                return self.word.lower()

            @word_insensitive.inplace.comparator
            @classmethod
            def _word_insensitive_comparator(cls) -> CaseInsensitiveComparator:
                return CaseInsensitiveComparator(cls.word)

    如上所示，针对 ``word_insensitive`` 的 SQL 表达式将在两边应用 ``LOWER()`` SQL 函数：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(SearchWord).filter_by(word_insensitive="Trucks"))
        {printsql}SELECT searchword.id, searchword.word
        FROM searchword
        WHERE lower(searchword.word) = lower(:lower_1)

    上面的 ``CaseInsensitiveComparator`` 实现了部分 :class:`.ColumnOperators` 接口。可以使用 :meth:`.Operators.operate` 对所有比较操作（如 ``eq``、``lt``、``gt`` 等）统一应用小写转换操作::

        class CaseInsensitiveComparator(Comparator):
            def operate(self, op, other, **kwargs):
                return op(
                    func.lower(self.__clause_element__()),
                    func.lower(other),
                    **kwargs,
                )

.. tab:: 英文

    The hybrid property also includes a helper that allows construction of
    custom comparators. A comparator object allows one to customize the
    behavior of each SQLAlchemy expression operator individually.  They
    are useful when creating custom types that have some highly
    idiosyncratic behavior on the SQL side.

    .. note::  The :meth:`.hybrid_property.comparator` decorator introduced
       in this section **replaces** the use of the
       :meth:`.hybrid_property.expression` decorator.
       They cannot be used together.

    The example class below allows case-insensitive comparisons on the attribute
    named ``word_insensitive``::

        from __future__ import annotations

        from typing import Any

        from sqlalchemy import ColumnElement
        from sqlalchemy import func
        from sqlalchemy.ext.hybrid import Comparator
        from sqlalchemy.ext.hybrid import hybrid_property
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class CaseInsensitiveComparator(Comparator[str]):
            def __eq__(self, other: Any) -> ColumnElement[bool]:  # type: ignore[override]  # noqa: E501
                return func.lower(self.__clause_element__()) == func.lower(other)


        class SearchWord(Base):
            __tablename__ = "searchword"

            id: Mapped[int] = mapped_column(primary_key=True)
            word: Mapped[str]

            @hybrid_property
            def word_insensitive(self) -> str:
                return self.word.lower()

            @word_insensitive.inplace.comparator
            @classmethod
            def _word_insensitive_comparator(cls) -> CaseInsensitiveComparator:
                return CaseInsensitiveComparator(cls.word)

    Above, SQL expressions against ``word_insensitive`` will apply the ``LOWER()``
    SQL function to both sides:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy import select
        >>> print(select(SearchWord).filter_by(word_insensitive="Trucks"))
        {printsql}SELECT searchword.id, searchword.word
        FROM searchword
        WHERE lower(searchword.word) = lower(:lower_1)


    The ``CaseInsensitiveComparator`` above implements part of the
    :class:`.ColumnOperators` interface.   A "coercion" operation like
    lowercasing can be applied to all comparison operations (i.e. ``eq``,
    ``lt``, ``gt``, etc.) using :meth:`.Operators.operate`::

        class CaseInsensitiveComparator(Comparator):
            def operate(self, op, other, **kwargs):
                return op(
                    func.lower(self.__clause_element__()),
                    func.lower(other),
                    **kwargs,
                )

.. _hybrid_reuse_subclass:

跨子类重用混合属性
-------------------------------------------

Reusing Hybrid Properties across Subclasses

.. tab:: 中文

    混合属性可以从超类中引用，从而允许通过 :meth:`.hybrid_property.getter`、:meth:`.hybrid_property.setter` 等方法在子类中重新定义这些方法。这类似于 Python 标准的 ``@property`` 对象的工作方式::

        class FirstNameOnly(Base):
            # ...

            first_name: Mapped[str]

            @hybrid_property
            def name(self) -> str:
                return self.first_name

            @name.inplace.setter
            def _name_setter(self, value: str) -> None:
                self.first_name = value


        class FirstNameLastName(FirstNameOnly):
            # ...

            last_name: Mapped[str]

            # 这里没有使用 'inplace'；调用 getter 创建了 FirstNameOnly.name 的副本，
            # 该副本仅属于 FirstNameLastName
            @FirstNameOnly.name.getter
            def name(self) -> str:
                return self.first_name + " " + self.last_name

            @name.inplace.setter
            def _name_setter(self, value: str) -> None:
                self.first_name, self.last_name = value.split(" ", 1)

    如上所示，``FirstNameLastName`` 类引用 ``FirstNameOnly.name`` 混合属性，以重用其 getter 和 setter 方法。

    当仅重写 :meth:`.hybrid_property.expression` 和 :meth:`.hybrid_property.comparator` 且首次引用的是超类时，这些名称会与类级的 :class:`.QueryableAttribute` 对象中的同名访问器发生冲突。要在直接引用父类描述符时重写这些方法，需要添加特殊限定符 :attr:`.hybrid_property.overrides`，该限定符会将已注入的属性反引用为混合对象::

        class FirstNameLastName(FirstNameOnly):
            # ...

            last_name: Mapped[str]

            @FirstNameOnly.name.overrides.expression
            @classmethod
            def name(cls):
                return func.concat(cls.first_name, " ", cls.last_name)

.. tab:: 英文

    A hybrid can be referred to from a superclass, to allow modifying
    methods like :meth:`.hybrid_property.getter`, :meth:`.hybrid_property.setter`
    to be used to redefine those methods on a subclass.  This is similar to
    how the standard Python ``@property`` object works::

        class FirstNameOnly(Base):
            # ...

            first_name: Mapped[str]

            @hybrid_property
            def name(self) -> str:
                return self.first_name

            @name.inplace.setter
            def _name_setter(self, value: str) -> None:
                self.first_name = value


        class FirstNameLastName(FirstNameOnly):
            # ...

            last_name: Mapped[str]

            # 'inplace' is not used here; calling getter creates a copy
            # of FirstNameOnly.name that is local to FirstNameLastName
            @FirstNameOnly.name.getter
            def name(self) -> str:
                return self.first_name + " " + self.last_name

            @name.inplace.setter
            def _name_setter(self, value: str) -> None:
                self.first_name, self.last_name = value.split(" ", 1)

    Above, the ``FirstNameLastName`` class refers to the hybrid from
    ``FirstNameOnly.name`` to repurpose its getter and setter for the subclass.

    When overriding :meth:`.hybrid_property.expression` and
    :meth:`.hybrid_property.comparator` alone as the first reference to the
    superclass, these names conflict with the same-named accessors on the class-
    level :class:`.QueryableAttribute` object returned at the class level.  To
    override these methods when referring directly to the parent class descriptor,
    add the special qualifier :attr:`.hybrid_property.overrides`, which will de-
    reference the instrumented attribute back to the hybrid object::

        class FirstNameLastName(FirstNameOnly):
            # ...

            last_name: Mapped[str]

            @FirstNameOnly.name.overrides.expression
            @classmethod
            def name(cls):
                return func.concat(cls.first_name, " ", cls.last_name)

混合值对象
--------------------

Hybrid Value Objects

.. tab:: 中文

    注意在前面的例子中，如果我们将 ``SearchWord`` 实例的 ``word_insensitive`` 属性与普通 Python 字符串进行比较，普通字符串不会被转换为小写 —— 我们构建的 ``CaseInsensitiveComparator`` 只应用于 SQL 层，因为它是由 ``@word_insensitive.comparator`` 返回的。

    更全面的自定义比较器形式是构建一个 *混合值对象（Hybrid Value Object）*。这种技术将目标值或表达式应用于一个值对象，并在所有情况下由访问器返回该对象。值对象可以控制值上的所有操作，以及比较值的处理方式，无论是在 SQL 表达式端还是 Python 值端。以下使用新的 ``CaseInsensitiveWord`` 类替换之前的 ``CaseInsensitiveComparator`` 类::

        class CaseInsensitiveWord(Comparator):
            "混合值，表示单词的小写表示形式。"

            def __init__(self, word):
                if isinstance(word, basestring):
                    self.word = word.lower()
                elif isinstance(word, CaseInsensitiveWord):
                    self.word = word.word
                else:
                    self.word = func.lower(word)

            def operate(self, op, other, **kwargs):
                if not isinstance(other, CaseInsensitiveWord):
                    other = CaseInsensitiveWord(other)
                return op(self.word, other.word, **kwargs)

            def __clause_element__(self):
                return self.word

            def __str__(self):
                return self.word

            key = "word"
            "应用于 Query 元组结果的标签"

    如上所示，``CaseInsensitiveWord`` 对象表示 ``self.word``，该值可能是一个 SQL 函数，也可能是一个原生 Python 值。通过重写 ``operate()`` 和 ``__clause_element__()`` 来处理 ``self.word``，可以使所有比较操作适用于转换后的 ``word``，无论是在 SQL 端还是 Python 端。我们的 ``SearchWord`` 类现在可以始终通过一个混合调用无条件地返回 ``CaseInsensitiveWord`` 对象::

        class SearchWord(Base):
            __tablename__ = "searchword"
            id: Mapped[int] = mapped_column(primary_key=True)
            word: Mapped[str]

            @hybrid_property
            def word_insensitive(self) -> CaseInsensitiveWord:
                return CaseInsensitiveWord(self.word)

    现在， ``word_insensitive`` 属性具有统一的不区分大小写比较行为，包括 SQL 表达式与 Python 表达式之间的比较（注意此处 Python 值已在 Python 层被转换为小写）：

    .. sourcecode:: pycon+sql

        >>> print(select(SearchWord).filter_by(word_insensitive="Trucks"))
        {printsql}SELECT searchword.id AS searchword_id, searchword.word AS searchword_word
        FROM searchword
        WHERE lower(searchword.word) = :lower_1

    SQL 表达式对 SQL 表达式：

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import aliased
        >>> sw1 = aliased(SearchWord)
        >>> sw2 = aliased(SearchWord)
        >>> print(
        ...     select(sw1.word_insensitive, sw2.word_insensitive).filter(
        ...         sw1.word_insensitive > sw2.word_insensitive
        ...     )
        ... )
        {printsql}SELECT lower(searchword_1.word) AS lower_1,
        lower(searchword_2.word) AS lower_2
        FROM searchword AS searchword_1, searchword AS searchword_2
        WHERE lower(searchword_1.word) > lower(searchword_2.word)

    仅 Python 表达式::

        >>> ws1 = SearchWord(word="SomeWord")
        >>> ws1.word_insensitive == "sOmEwOrD"
        True
        >>> ws1.word_insensitive == "XOmEwOrX"
        False
        >>> print(ws1.word_insensitive)
        someword

    混合值模式对任何可能具有多种表示形式的值都非常有用，比如时间戳、时间差、度量单位、货币和加密密码等。

    .. seealso::

        `Hybrids and Value Agnostic Types
        <https://techspot.zzzeek.org/2011/10/21/hybrids-and-value-agnostic-types/>`_
        - 见 techspot.zzzeek.org 博客

        `Value Agnostic Types, Part II
        <https://techspot.zzzeek.org/2011/10/29/value-agnostic-types-part-ii/>`_ -
        见 techspot.zzzeek.org 博客

.. tab:: 英文

    Note in our previous example, if we were to compare the ``word_insensitive``
    attribute of a ``SearchWord`` instance to a plain Python string, the plain
    Python string would not be coerced to lower case - the
    ``CaseInsensitiveComparator`` we built, being returned by
    ``@word_insensitive.comparator``, only applies to the SQL side.

    A more comprehensive form of the custom comparator is to construct a *Hybrid
    Value Object*. This technique applies the target value or expression to a value
    object which is then returned by the accessor in all cases.   The value object
    allows control of all operations upon the value as well as how compared values
    are treated, both on the SQL expression side as well as the Python value side.
    Replacing the previous ``CaseInsensitiveComparator`` class with a new
    ``CaseInsensitiveWord`` class::

        class CaseInsensitiveWord(Comparator):
            "Hybrid value representing a lower case representation of a word."

            def __init__(self, word):
                if isinstance(word, basestring):
                    self.word = word.lower()
                elif isinstance(word, CaseInsensitiveWord):
                    self.word = word.word
                else:
                    self.word = func.lower(word)

            def operate(self, op, other, **kwargs):
                if not isinstance(other, CaseInsensitiveWord):
                    other = CaseInsensitiveWord(other)
                return op(self.word, other.word, **kwargs)

            def __clause_element__(self):
                return self.word

            def __str__(self):
                return self.word

            key = "word"
            "Label to apply to Query tuple results"

    Above, the ``CaseInsensitiveWord`` object represents ``self.word``, which may
    be a SQL function, or may be a Python native.   By overriding ``operate()`` and
    ``__clause_element__()`` to work in terms of ``self.word``, all comparison
    operations will work against the "converted" form of ``word``, whether it be
    SQL side or Python side. Our ``SearchWord`` class can now deliver the
    ``CaseInsensitiveWord`` object unconditionally from a single hybrid call::

        class SearchWord(Base):
            __tablename__ = "searchword"
            id: Mapped[int] = mapped_column(primary_key=True)
            word: Mapped[str]

            @hybrid_property
            def word_insensitive(self) -> CaseInsensitiveWord:
                return CaseInsensitiveWord(self.word)

    The ``word_insensitive`` attribute now has case-insensitive comparison behavior
    universally, including SQL expression vs. Python expression (note the Python
    value is converted to lower case on the Python side here):

    .. sourcecode:: pycon+sql

        >>> print(select(SearchWord).filter_by(word_insensitive="Trucks"))
        {printsql}SELECT searchword.id AS searchword_id, searchword.word AS searchword_word
        FROM searchword
        WHERE lower(searchword.word) = :lower_1

    SQL expression versus SQL expression:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.orm import aliased
        >>> sw1 = aliased(SearchWord)
        >>> sw2 = aliased(SearchWord)
        >>> print(
        ...     select(sw1.word_insensitive, sw2.word_insensitive).filter(
        ...         sw1.word_insensitive > sw2.word_insensitive
        ...     )
        ... )
        {printsql}SELECT lower(searchword_1.word) AS lower_1,
        lower(searchword_2.word) AS lower_2
        FROM searchword AS searchword_1, searchword AS searchword_2
        WHERE lower(searchword_1.word) > lower(searchword_2.word)

    Python only expression::

        >>> ws1 = SearchWord(word="SomeWord")
        >>> ws1.word_insensitive == "sOmEwOrD"
        True
        >>> ws1.word_insensitive == "XOmEwOrX"
        False
        >>> print(ws1.word_insensitive)
        someword

    The Hybrid Value pattern is very useful for any kind of value that may have
    multiple representations, such as timestamps, time deltas, units of
    measurement, currencies and encrypted passwords.

    .. seealso::

        `Hybrids and Value Agnostic Types
        <https://techspot.zzzeek.org/2011/10/21/hybrids-and-value-agnostic-types/>`_
        - on the techspot.zzzeek.org blog

        `Value Agnostic Types, Part II
        <https://techspot.zzzeek.org/2011/10/29/value-agnostic-types-part-ii/>`_ -
        on the techspot.zzzeek.org blog


"""  # noqa

from __future__ import annotations

from typing import Any
from typing import Callable
from typing import cast
from typing import Generic
from typing import List
from typing import Optional
from typing import overload
from typing import Protocol
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

from .. import util
from ..orm import attributes
from ..orm import InspectionAttrExtensionType
from ..orm import interfaces
from ..orm import ORMDescriptor
from ..orm.attributes import QueryableAttribute
from ..sql import roles
from ..sql._typing import is_has_clause_element
from ..sql.elements import ColumnElement
from ..sql.elements import SQLCoreOperations
from ..util.typing import Concatenate
from ..util.typing import Literal
from ..util.typing import ParamSpec
from ..util.typing import Self

if TYPE_CHECKING:
    from ..orm.interfaces import MapperProperty
    from ..orm.util import AliasedInsp
    from ..sql import SQLColumnExpression
    from ..sql._typing import _ColumnExpressionArgument
    from ..sql._typing import _DMLColumnArgument
    from ..sql._typing import _HasClauseElement
    from ..sql._typing import _InfoType
    from ..sql.operators import OperatorType

_P = ParamSpec("_P")
_R = TypeVar("_R")
_T = TypeVar("_T", bound=Any)
_TE = TypeVar("_TE", bound=Any)
_T_co = TypeVar("_T_co", bound=Any, covariant=True)
_T_con = TypeVar("_T_con", bound=Any, contravariant=True)


class HybridExtensionType(InspectionAttrExtensionType):
    HYBRID_METHOD = "HYBRID_METHOD"
    """Symbol indicating an :class:`InspectionAttr` that's
    of type :class:`.hybrid_method`.

    Is assigned to the :attr:`.InspectionAttr.extension_type`
    attribute.

    .. seealso::

        :attr:`_orm.Mapper.all_orm_attributes`

    """

    HYBRID_PROPERTY = "HYBRID_PROPERTY"
    """Symbol indicating an :class:`InspectionAttr` that's
        of type :class:`.hybrid_method`.

    Is assigned to the :attr:`.InspectionAttr.extension_type`
    attribute.

    .. seealso::

        :attr:`_orm.Mapper.all_orm_attributes`

    """


class _HybridGetterType(Protocol[_T_co]):
    def __call__(s, self: Any) -> _T_co: ...


class _HybridSetterType(Protocol[_T_con]):
    def __call__(s, self: Any, value: _T_con) -> None: ...


class _HybridUpdaterType(Protocol[_T_con]):
    def __call__(
        s,
        cls: Any,
        value: Union[_T_con, _ColumnExpressionArgument[_T_con]],
    ) -> List[Tuple[_DMLColumnArgument, Any]]: ...


class _HybridDeleterType(Protocol[_T_co]):
    def __call__(s, self: Any) -> None: ...


class _HybridExprCallableType(Protocol[_T_co]):
    def __call__(
        s, cls: Any
    ) -> Union[_HasClauseElement[_T_co], SQLColumnExpression[_T_co]]: ...


class _HybridComparatorCallableType(Protocol[_T]):
    def __call__(self, cls: Any) -> Comparator[_T]: ...


class _HybridClassLevelAccessor(QueryableAttribute[_T]):
    """Describe the object returned by a hybrid_property() when
    called as a class-level descriptor.

    """

    if TYPE_CHECKING:

        def getter(self, fget: _HybridGetterType[_T]) -> hybrid_property[_T]: ...

        def setter(self, fset: _HybridSetterType[_T]) -> hybrid_property[_T]: ...

        def deleter(self, fdel: _HybridDeleterType[_T]) -> hybrid_property[_T]: ...

        @property
        def overrides(self) -> hybrid_property[_T]: ...

        def update_expression(
            self, meth: _HybridUpdaterType[_T]
        ) -> hybrid_property[_T]: ...


class hybrid_method(interfaces.InspectionAttrInfo, Generic[_P, _R]):
    """A decorator which allows definition of a Python object method with both
    instance-level and class-level behavior.

    """

    is_attribute = True
    extension_type = HybridExtensionType.HYBRID_METHOD

    def __init__(
        self,
        func: Callable[Concatenate[Any, _P], _R],
        expr: Optional[Callable[Concatenate[Any, _P], SQLCoreOperations[_R]]] = None,
    ):
        """Create a new :class:`.hybrid_method`.

        Usage is typically via decorator::

            from sqlalchemy.ext.hybrid import hybrid_method


            class SomeClass:
                @hybrid_method
                def value(self, x, y):
                    return self._value + x + y

                @value.expression
                @classmethod
                def value(cls, x, y):
                    return func.some_function(cls._value, x, y)

        """
        self.func = func
        if expr is not None:
            self.expression(expr)
        else:
            self.expression(func)  # type: ignore

    @property
    def inplace(self) -> Self:
        """Return the inplace mutator for this :class:`.hybrid_method`.

        The :class:`.hybrid_method` class already performs "in place" mutation
        when the :meth:`.hybrid_method.expression` decorator is called,
        so this attribute returns Self.

        .. versionadded:: 2.0.4

        .. seealso::

            :ref:`hybrid_pep484_naming`

        """
        return self

    @overload
    def __get__(
        self, instance: Literal[None], owner: Type[object]
    ) -> Callable[_P, SQLCoreOperations[_R]]: ...

    @overload
    def __get__(self, instance: object, owner: Type[object]) -> Callable[_P, _R]: ...

    def __get__(
        self, instance: Optional[object], owner: Type[object]
    ) -> Union[Callable[_P, _R], Callable[_P, SQLCoreOperations[_R]]]:
        if instance is None:
            return self.expr.__get__(owner, owner)  # type: ignore
        else:
            return self.func.__get__(instance, owner)  # type: ignore

    def expression(
        self, expr: Callable[Concatenate[Any, _P], SQLCoreOperations[_R]]
    ) -> hybrid_method[_P, _R]:
        """Provide a modifying decorator that defines a
        SQL-expression producing method."""

        self.expr = expr
        if not self.expr.__doc__:
            self.expr.__doc__ = self.func.__doc__
        return self


def _unwrap_classmethod(meth: _T) -> _T:
    if isinstance(meth, classmethod):
        return meth.__func__  # type: ignore
    else:
        return meth


class hybrid_property(interfaces.InspectionAttrInfo, ORMDescriptor[_T]):
    """A decorator which allows definition of a Python descriptor with both
    instance-level and class-level behavior.

    """

    is_attribute = True
    extension_type = HybridExtensionType.HYBRID_PROPERTY

    __name__: str

    def __init__(
        self,
        fget: _HybridGetterType[_T],
        fset: Optional[_HybridSetterType[_T]] = None,
        fdel: Optional[_HybridDeleterType[_T]] = None,
        expr: Optional[_HybridExprCallableType[_T]] = None,
        custom_comparator: Optional[Comparator[_T]] = None,
        update_expr: Optional[_HybridUpdaterType[_T]] = None,
    ):
        """Create a new :class:`.hybrid_property`.

        Usage is typically via decorator::

            from sqlalchemy.ext.hybrid import hybrid_property


            class SomeClass:
                @hybrid_property
                def value(self):
                    return self._value

                @value.setter
                def value(self, value):
                    self._value = value

        """
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.expr = _unwrap_classmethod(expr)
        self.custom_comparator = _unwrap_classmethod(custom_comparator)
        self.update_expr = _unwrap_classmethod(update_expr)
        util.update_wrapper(self, fget)  # type: ignore[arg-type]

    @overload
    def __get__(self, instance: Any, owner: Literal[None]) -> Self: ...

    @overload
    def __get__(
        self, instance: Literal[None], owner: Type[object]
    ) -> _HybridClassLevelAccessor[_T]: ...

    @overload
    def __get__(self, instance: object, owner: Type[object]) -> _T: ...

    def __get__(
        self, instance: Optional[object], owner: Optional[Type[object]]
    ) -> Union[hybrid_property[_T], _HybridClassLevelAccessor[_T], _T]:
        if owner is None:
            return self
        elif instance is None:
            return self._expr_comparator(owner)
        else:
            return self.fget(instance)

    def __set__(self, instance: object, value: Any) -> None:
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance: object) -> None:
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def _copy(self, **kw: Any) -> hybrid_property[_T]:
        defaults = {
            key: value
            for key, value in self.__dict__.items()
            if not key.startswith("_")
        }
        defaults.update(**kw)
        return type(self)(**defaults)

    @property
    def overrides(self) -> Self:
        """Prefix for a method that is overriding an existing attribute.

        The :attr:`.hybrid_property.overrides` accessor just returns
        this hybrid object, which when called at the class level from
        a parent class, will de-reference the "instrumented attribute"
        normally returned at this level, and allow modifying decorators
        like :meth:`.hybrid_property.expression` and
        :meth:`.hybrid_property.comparator`
        to be used without conflicting with the same-named attributes
        normally present on the :class:`.QueryableAttribute`::

            class SuperClass:
                # ...

                @hybrid_property
                def foobar(self):
                    return self._foobar


            class SubClass(SuperClass):
                # ...

                @SuperClass.foobar.overrides.expression
                def foobar(cls):
                    return func.subfoobar(self._foobar)

        .. seealso::

            :ref:`hybrid_reuse_subclass`

        """
        return self

    class _InPlace(Generic[_TE]):
        """A builder helper for .hybrid_property.

        .. versionadded:: 2.0.4

        """

        __slots__ = ("attr",)

        def __init__(self, attr: hybrid_property[_TE]):
            self.attr = attr

        def _set(self, **kw: Any) -> hybrid_property[_TE]:
            for k, v in kw.items():
                setattr(self.attr, k, _unwrap_classmethod(v))
            return self.attr

        def getter(self, fget: _HybridGetterType[_TE]) -> hybrid_property[_TE]:
            return self._set(fget=fget)

        def setter(self, fset: _HybridSetterType[_TE]) -> hybrid_property[_TE]:
            return self._set(fset=fset)

        def deleter(self, fdel: _HybridDeleterType[_TE]) -> hybrid_property[_TE]:
            return self._set(fdel=fdel)

        def expression(
            self, expr: _HybridExprCallableType[_TE]
        ) -> hybrid_property[_TE]:
            return self._set(expr=expr)

        def comparator(
            self, comparator: _HybridComparatorCallableType[_TE]
        ) -> hybrid_property[_TE]:
            return self._set(custom_comparator=comparator)

        def update_expression(
            self, meth: _HybridUpdaterType[_TE]
        ) -> hybrid_property[_TE]:
            return self._set(update_expr=meth)

    @property
    def inplace(self) -> _InPlace[_T]:
        """Return the inplace mutator for this :class:`.hybrid_property`.

        This is to allow in-place mutation of the hybrid, allowing the first
        hybrid method of a certain name to be re-used in order to add
        more methods without having to name those methods the same, e.g.::

            class Interval(Base):
                # ...

                @hybrid_property
                def radius(self) -> float:
                    return abs(self.length) / 2

                @radius.inplace.setter
                def _radius_setter(self, value: float) -> None:
                    self.length = value * 2

                @radius.inplace.expression
                def _radius_expression(cls) -> ColumnElement[float]:
                    return type_coerce(func.abs(cls.length) / 2, Float)

        .. versionadded:: 2.0.4

        .. seealso::

            :ref:`hybrid_pep484_naming`

        """
        return hybrid_property._InPlace(self)

    def getter(self, fget: _HybridGetterType[_T]) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines a getter method."""

        return self._copy(fget=fget)

    def setter(self, fset: _HybridSetterType[_T]) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines a setter method."""

        return self._copy(fset=fset)

    def deleter(self, fdel: _HybridDeleterType[_T]) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines a deletion method."""

        return self._copy(fdel=fdel)

    def expression(self, expr: _HybridExprCallableType[_T]) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines a SQL-expression
        producing method.

        When a hybrid is invoked at the class level, the SQL expression given
        here is wrapped inside of a specialized :class:`.QueryableAttribute`,
        which is the same kind of object used by the ORM to represent other
        mapped attributes.   The reason for this is so that other class-level
        attributes such as docstrings and a reference to the hybrid itself may
        be maintained within the structure that's returned, without any
        modifications to the original SQL expression passed in.

        .. note::

           When referring to a hybrid property  from an owning class (e.g.
           ``SomeClass.some_hybrid``), an instance of
           :class:`.QueryableAttribute` is returned, representing the
           expression or comparator object as well as this  hybrid object.
           However, that object itself has accessors called ``expression`` and
           ``comparator``; so when attempting to override these decorators on a
           subclass, it may be necessary to qualify it using the
           :attr:`.hybrid_property.overrides` modifier first.  See that
           modifier for details.

        .. seealso::

            :ref:`hybrid_distinct_expression`

        """

        return self._copy(expr=expr)

    def comparator(
        self, comparator: _HybridComparatorCallableType[_T]
    ) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines a custom
        comparator producing method.

        The return value of the decorated method should be an instance of
        :class:`~.hybrid.Comparator`.

        .. note::  The :meth:`.hybrid_property.comparator` decorator
           **replaces** the use of the :meth:`.hybrid_property.expression`
           decorator.  They cannot be used together.

        When a hybrid is invoked at the class level, the
        :class:`~.hybrid.Comparator` object given here is wrapped inside of a
        specialized :class:`.QueryableAttribute`, which is the same kind of
        object used by the ORM to represent other mapped attributes.   The
        reason for this is so that other class-level attributes such as
        docstrings and a reference to the hybrid itself may be maintained
        within the structure that's returned, without any modifications to the
        original comparator object passed in.

        .. note::

           When referring to a hybrid property  from an owning class (e.g.
           ``SomeClass.some_hybrid``), an instance of
           :class:`.QueryableAttribute` is returned, representing the
           expression or comparator object as this  hybrid object.  However,
           that object itself has accessors called ``expression`` and
           ``comparator``; so when attempting to override these decorators on a
           subclass, it may be necessary to qualify it using the
           :attr:`.hybrid_property.overrides` modifier first.  See that
           modifier for details.

        """
        return self._copy(custom_comparator=comparator)

    def update_expression(self, meth: _HybridUpdaterType[_T]) -> hybrid_property[_T]:
        """Provide a modifying decorator that defines an UPDATE tuple
        producing method.

        The method accepts a single value, which is the value to be
        rendered into the SET clause of an UPDATE statement.  The method
        should then process this value into individual column expressions
        that fit into the ultimate SET clause, and return them as a
        sequence of 2-tuples.  Each tuple
        contains a column expression as the key and a value to be rendered.

        E.g.::

            class Person(Base):
                # ...

                first_name = Column(String)
                last_name = Column(String)

                @hybrid_property
                def fullname(self):
                    return first_name + " " + last_name

                @fullname.update_expression
                def fullname(cls, value):
                    fname, lname = value.split(" ", 1)
                    return [(cls.first_name, fname), (cls.last_name, lname)]

        """
        return self._copy(update_expr=meth)

    @util.memoized_property
    def _expr_comparator(
        self,
    ) -> Callable[[Any], _HybridClassLevelAccessor[_T]]:
        if self.custom_comparator is not None:
            return self._get_comparator(self.custom_comparator)
        elif self.expr is not None:
            return self._get_expr(self.expr)
        else:
            return self._get_expr(cast(_HybridExprCallableType[_T], self.fget))

    def _get_expr(
        self, expr: _HybridExprCallableType[_T]
    ) -> Callable[[Any], _HybridClassLevelAccessor[_T]]:
        def _expr(cls: Any) -> ExprComparator[_T]:
            return ExprComparator(cls, expr(cls), self)

        util.update_wrapper(_expr, expr)

        return self._get_comparator(_expr)

    def _get_comparator(
        self, comparator: Any
    ) -> Callable[[Any], _HybridClassLevelAccessor[_T]]:
        proxy_attr = attributes._create_proxied_attribute(self)

        def expr_comparator(
            owner: Type[object],
        ) -> _HybridClassLevelAccessor[_T]:
            # because this is the descriptor protocol, we don't really know
            # what our attribute name is.  so search for it through the
            # MRO.
            for lookup in owner.__mro__:
                if self.__name__ in lookup.__dict__:
                    if lookup.__dict__[self.__name__] is self:
                        name = self.__name__
                        break
            else:
                name = attributes._UNKNOWN_ATTR_KEY  # type: ignore[assignment]

            return cast(
                "_HybridClassLevelAccessor[_T]",
                proxy_attr(
                    owner,
                    name,
                    self,
                    comparator(owner),
                    doc=comparator.__doc__ or self.__doc__,
                ),
            )

        return expr_comparator


class Comparator(interfaces.PropComparator[_T]):
    """A helper class that allows easy construction of custom
    :class:`~.orm.interfaces.PropComparator`
    classes for usage with hybrids."""

    def __init__(
        self, expression: Union[_HasClauseElement[_T], SQLColumnExpression[_T]]
    ):
        self.expression = expression

    def __clause_element__(self) -> roles.ColumnsClauseRole:
        expr = self.expression
        if is_has_clause_element(expr):
            ret_expr = expr.__clause_element__()
        else:
            if TYPE_CHECKING:
                assert isinstance(expr, ColumnElement)
            ret_expr = expr

        if TYPE_CHECKING:
            # see test_hybrid->test_expression_isnt_clause_element
            # that exercises the usual place this is caught if not
            # true
            assert isinstance(ret_expr, ColumnElement)
        return ret_expr

    @util.non_memoized_property
    def property(self) -> interfaces.MapperProperty[_T]:
        raise NotImplementedError()

    def adapt_to_entity(self, adapt_to_entity: AliasedInsp[Any]) -> Comparator[_T]:
        # interesting....
        return self


class ExprComparator(Comparator[_T]):
    def __init__(
        self,
        cls: Type[Any],
        expression: Union[_HasClauseElement[_T], SQLColumnExpression[_T]],
        hybrid: hybrid_property[_T],
    ):
        self.cls = cls
        self.expression = expression
        self.hybrid = hybrid

    def __getattr__(self, key: str) -> Any:
        return getattr(self.expression, key)

    @util.ro_non_memoized_property
    def info(self) -> _InfoType:
        return self.hybrid.info

    def _bulk_update_tuples(
        self, value: Any
    ) -> Sequence[Tuple[_DMLColumnArgument, Any]]:
        if isinstance(self.expression, attributes.QueryableAttribute):
            return self.expression._bulk_update_tuples(value)
        elif self.hybrid.update_expr is not None:
            return self.hybrid.update_expr(self.cls, value)
        else:
            return [(self.expression, value)]

    @util.non_memoized_property
    def property(self) -> MapperProperty[_T]:
        # this accessor is not normally used, however is accessed by things
        # like ORM synonyms if the hybrid is used in this context; the
        # .property attribute is not necessarily accessible
        return self.expression.property  # type: ignore

    def operate(
        self, op: OperatorType, *other: Any, **kwargs: Any
    ) -> ColumnElement[Any]:
        return op(self.expression, *other, **kwargs)

    def reverse_operate(
        self, op: OperatorType, other: Any, **kwargs: Any
    ) -> ColumnElement[Any]:
        return op(other, self.expression, **kwargs)  # type: ignore
