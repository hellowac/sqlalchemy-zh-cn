.. _functions_toplevel:
.. _generic_functions:

=========================
SQL 和 范型函数
=========================

SQL and Generic Functions

.. currentmodule:: sqlalchemy.sql.functions

.. tab:: 中文

    SQL 函数通过使用 :data:`_sql.func` 命名空间来调用。有关如何使用 :data:`_sql.func` 对象在语句中呈现 SQL 函数的背景，请参阅 :ref:`tutorial_functions` 中的教程。

    .. seealso::

        :ref:`tutorial_functions` - 在 :ref:`unified_tutorial` 中

.. tab:: 英文

    SQL functions are invoked by using the :data:`_sql.func` namespace.
    See the tutorial at :ref:`tutorial_functions` for background on how to
    use the :data:`_sql.func` object to render SQL functions in statements.

    .. seealso::

        :ref:`tutorial_functions` - in the :ref:`unified_tutorial`

函数 API
------------

Function API

.. tab:: 中文

    SQL 函数的基本 API，提供 :data:`_sql.func` 命名空间以及可用于扩展的类。

.. tab:: 英文

    The base API for SQL functions, which provides for the :data:`_sql.func` namespace as well as classes that may be used for extensibility.

.. autoclass:: AnsiFunction
   :exclude-members: inherit_cache, __new__

.. autoclass:: Function

.. autoclass:: FunctionElement
   :members:
   :exclude-members: inherit_cache, __new__

.. autoclass:: GenericFunction
   :exclude-members: inherit_cache, __new__

.. autofunction:: register_function


选定的“已知”函数
--------------------------

Selected "Known" Functions

.. tab:: 中文

    这些是 :class:`.GenericFunction` 的实现，适用于一组常见的 SQL 函数，自动设置每个函数的预期返回类型。它们以与 :data:`_sql.func` 命名空间的任何其他成员相同的方式调用::

        select(func.count("*")).select_from(some_table)

    请注意，任何 :data:`_sql.func` 未知的名称都会按原样生成函数名称——对可以调用哪些 SQL 函数没有限制，无论是 SQLAlchemy 已知的、内置的还是用户定义的。这里只描述了 SQLAlchemy 已经知道使用的参数和返回类型的那些函数。

.. tab:: 英文

    These are :class:`.GenericFunction` implementations for a selected set of
    common SQL functions that set up the expected return type for each function
    automatically.  The are invoked in the same way as any other member of the
    :data:`_sql.func` namespace::

        select(func.count("*")).select_from(some_table)

    Note that any name not known to :data:`_sql.func` generates the function name
    as is - there is no restriction on what SQL functions can be called, known or
    unknown to SQLAlchemy, built-in or user defined. The section here only
    describes those functions where SQLAlchemy already knows what argument and
    return types are in use.

.. autoclass:: aggregate_strings
    :no-members:

.. autoclass:: array_agg
    :no-members:

.. autoclass:: char_length
    :no-members:

.. autoclass:: coalesce
    :no-members:

.. autoclass:: concat
    :no-members:

.. autoclass:: count
    :no-members:

.. autoclass:: cube
    :no-members:

.. autoclass:: cume_dist
    :no-members:

.. autoclass:: current_date
    :no-members:

.. autoclass:: current_time
    :no-members:

.. autoclass:: current_timestamp
    :no-members:

.. autoclass:: current_user
    :no-members:

.. autoclass:: dense_rank
    :no-members:

.. autoclass:: grouping_sets
    :no-members:

.. autoclass:: localtime
    :no-members:

.. autoclass:: localtimestamp
    :no-members:

.. autoclass:: max
    :no-members:

.. autoclass:: min
    :no-members:

.. autoclass:: mode
    :no-members:

.. autoclass:: next_value
    :no-members:

.. autoclass:: now
    :no-members:

.. autoclass:: percent_rank
    :no-members:

.. autoclass:: percentile_cont
    :no-members:

.. autoclass:: percentile_disc
    :no-members:

.. autoclass:: random
    :no-members:

.. autoclass:: rank
    :no-members:

.. autoclass:: rollup
    :no-members:

.. autoclass:: session_user
    :no-members:

.. autoclass:: sum
    :no-members:

.. autoclass:: sysdate
    :no-members:

.. autoclass:: user
    :no-members:
