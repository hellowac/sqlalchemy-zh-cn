第三方包集成问题
===============================

Third Party Integration Issues

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _numpy_int64:

我收到与 “numpy.int64”、 “numpy.bool_” 等相关的错误。
------------------------------------------------------------------------

I'm getting errors related to "``numpy.int64``", "``numpy.bool_``", etc.

.. tab:: 中文

    numpy_ 包拥有一套扩展自 Python 数值类型的专有数值数据类型，但这些类型在某些情况下表现出的行为可能与 SQLAlchemy 的行为不兼容，有时甚至无法与所使用的底层 DBAPI 驱动兼容。

    可能出现的两类典型错误包括：

    - ``ProgrammingError: can't adapt type 'numpy.int64'`` （在 psycopg2 等后端中出现）；
    - ``ArgumentError: SQL expression object expected, got object of type <class 'numpy.bool_'> instead``；

    在较新版本的 SQLAlchemy 中，后者的报错信息可能为：

    - ``ArgumentError: SQL expression for WHERE/HAVING role expected, got True``。

    第一类错误的原因在于 psycopg2 等驱动缺少对 ``int64`` 类型的适配支持——这种类型不能直接作为参数传入查询中。例如下面的代码会触发该问题：

    .. sourcecode:: python

        import numpy


        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)
            data = Column(Integer)


        # .. 稍后
        session.add(A(data=numpy.int64(10)))
        session.commit()

    第二类错误则是因为 ``numpy.int64`` 类型重写了其 ``__eq__()`` 方法，并强制返回 ``numpy.True`` 或 ``numpy.False``，这会破坏 SQLAlchemy 表达式语言的行为。SQLAlchemy 期望从 Python 的等值比较中返回 :class:`_sql.ColumnElement` 类型的表达式：

    .. sourcecode:: pycon+sql

        >>> import numpy
        >>> from sqlalchemy import column, Integer
        >>> print(column("x", Integer) == numpy.int64(10))  # 正常
        {printsql}x = :x_1{stop}
        >>> print(numpy.int64(10) == column("x", Integer))  # 出错
        False

    上述两类问题的解决方式是一样的：应将特殊的 numpy 数据类型转换为标准 Python 值。常见的转换方式包括对 ``numpy.int32`` 和 ``numpy.int64`` 使用 Python 内建的 ``int()`` 函数，对 ``numpy.float32`` 使用 ``float()`` 函数：

    .. sourcecode:: python

        data = numpy.int64(10)

        session.add(A(data=int(data)))

        result = session.execute(select(A.data).where(int(data) == A.data))

        session.commit()

.. tab:: 英文

    The numpy_ package has its own numeric datatypes that extend from Python's
    numeric types, but contain some behaviors that in some cases make them impossible
    to reconcile with some of SQLAlchemy's behaviors, as well as in some cases
    with those of the underlying DBAPI driver in use.

    Two errors which can occur are ``ProgrammingError: can't adapt type 'numpy.int64'``
    on a backend such as psycopg2, and ``ArgumentError: SQL expression object
    expected, got object of type <class 'numpy.bool_'> instead``; in
    more recent versions of SQLAlchemy this may be ``ArgumentError: SQL expression
    for WHERE/HAVING role expected, got True``.

    In the first case, the issue is due to psycopg2 not having an appropriate
    lookup entry for the ``int64`` datatype such that it is not accepted directly
    by queries.   This may be illustrated from code based on the following::

        import numpy


        class A(Base):
            __tablename__ = "a"

            id = Column(Integer, primary_key=True)
            data = Column(Integer)


        # .. later
        session.add(A(data=numpy.int64(10)))
        session.commit()

    In the latter case, the issue is due to the ``numpy.int64`` datatype overriding
    the ``__eq__()`` method and enforcing that the return type of an expression is
    ``numpy.True`` or ``numpy.False``, which breaks SQLAlchemy's expression
    language behavior that expects to return :class:`_sql.ColumnElement`
    expressions from Python equality comparisons:

    .. sourcecode:: pycon+sql

        >>> import numpy
        >>> from sqlalchemy import column, Integer
        >>> print(column("x", Integer) == numpy.int64(10))  # works
        {printsql}x = :x_1{stop}
        >>> print(numpy.int64(10) == column("x", Integer))  # breaks
        False

    These errors are both solved in the same way, which is that special numpy
    datatypes need to be replaced with regular Python values.  Examples include
    applying the Python ``int()`` function to types like ``numpy.int32`` and
    ``numpy.int64`` and the Python ``float()`` function to ``numpy.float32``::

        data = numpy.int64(10)

        session.add(A(data=int(data)))

        result = session.execute(select(A.data).where(int(data) == A.data))

        session.commit()

.. _numpy: https://numpy.org

预期 WHERE/HAVING 角色的 SQL 表达式为 True
-------------------------------------------------------

SQL expression for WHERE/HAVING role expected, got True

.. tab:: 中文

    见 :ref:`numpy_int64`.

.. tab:: 英文

    See :ref:`numpy_int64`.
