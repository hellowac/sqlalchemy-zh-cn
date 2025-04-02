列元素和表达式
===============================

Column Elements and Expressions

.. currentmodule:: sqlalchemy.sql.expression

.. tab:: 中文

   表达式 API 由一系列类组成，每个类代表 SQL 字符串中的特定词法元素。将它们组合成一个更大的结构，它们形成一个可以 *编译* 成字符串表示的语句构造，可以传递给数据库。这些类被组织成一个以最基础的 :class:`.ClauseElement` 类开始的层次结构。关键子类包括 :class:`.ColumnElement`，它表示 SQL 语句中任何基于列的表达式的角色，例如在列子句、WHERE 子句和 ORDER BY 子句中；以及 :class:`.FromClause`，它表示在 SELECT 语句的 FROM 子句中放置的标记的角色。

.. tab:: 英文

   The expression API consists of a series of classes each of which represents a
   specific lexical element within a SQL string.  Composed together
   into a larger structure, they form a statement construct that may
   be *compiled* into a string representation that can be passed to a database.
   The classes are organized into a hierarchy that begins at the basemost
   :class:`.ClauseElement` class. Key subclasses include :class:`.ColumnElement`,
   which represents the role of any column-based expression
   in a SQL statement, such as in the columns clause, WHERE clause, and ORDER BY
   clause, and :class:`.FromClause`, which represents the role of a token that
   is placed in the FROM clause of a SELECT statement.

.. _sqlelement_foundational_constructors:

列元素基础构造函数
-----------------------------------------

Column Element Foundational Constructors

.. tab:: 中文

.. tab:: 英文

Standalone functions imported from the ``sqlalchemy`` namespace which are
used when building up SQLAlchemy Expression Language constructs.

.. autofunction:: and_

.. autofunction:: bindparam

.. autofunction:: bitwise_not

.. autofunction:: case

.. autofunction:: cast

.. autofunction:: column

.. autoclass:: custom_op
   :members:

.. autofunction:: distinct

.. autofunction:: extract

.. autofunction:: false

.. autodata:: func

.. autofunction:: lambda_stmt

.. autofunction:: literal

.. autofunction:: literal_column

.. autofunction:: not_

.. autofunction:: null

.. autofunction:: or_

.. autofunction:: outparam

.. autofunction:: text

.. autofunction:: true

.. autofunction:: try_cast

.. autofunction:: tuple_

.. autofunction:: type_coerce

.. autoclass:: quoted_name

   .. attribute:: quote

      whether the string should be unconditionally quoted


.. _sqlelement_modifier_constructors:

列元素修饰符构造函数
-------------------------------------

Column Element Modifier Constructors

.. tab:: 中文

.. tab:: 英文

Functions listed here are more commonly available as methods from any
:class:`_sql.ColumnElement` construct, for example, the
:func:`_sql.label` function is usually invoked via the
:meth:`_sql.ColumnElement.label` method.

.. autofunction:: all_

.. autofunction:: any_

.. autofunction:: asc

.. autofunction:: between

.. autofunction:: collate

.. autofunction:: desc

.. autofunction:: funcfilter

.. autofunction:: label

.. autofunction:: nulls_first

.. function:: nullsfirst

   Synonym for the :func:`_sql.nulls_first` function.

   .. versionchanged:: 2.0.5 restored missing legacy symbol :func:`.nullsfirst`.

.. autofunction:: nulls_last

.. function:: nullslast

   Legacy synonym for the :func:`_sql.nulls_last` function.

   .. versionchanged:: 2.0.5 restored missing legacy symbol :func:`.nullslast`.

.. autofunction:: over

.. autofunction:: within_group

列元素类文档
-----------------------------------

Column Element Class Documentation

.. tab:: 中文

.. tab:: 英文

The classes here are generated using the constructors listed at
:ref:`sqlelement_foundational_constructors` and
:ref:`sqlelement_modifier_constructors`.


.. autoclass:: BinaryExpression
   :members:

.. autoclass:: BindParameter
   :members:

.. autoclass:: Case
   :members:

.. autoclass:: Cast
   :members:

.. autoclass:: ClauseList
   :members:


.. autoclass:: ColumnClause
   :members:

.. autoclass:: ColumnCollection
   :members:

.. autoclass:: ColumnElement
   :members:
   :inherited-members:
   :undoc-members:

.. data:: ColumnExpressionArgument

   General purpose "column expression" argument.

   .. versionadded:: 2.0.13

   This type is used for "column" kinds of expressions that typically represent
   a single SQL column expression, including :class:`_sql.ColumnElement`, as
   well as ORM-mapped attributes that will have a ``__clause_element__()``
   method.


.. autoclass:: ColumnOperators
   :members:
   :special-members:
   :inherited-members:


.. autoclass:: Extract
   :members:

.. autoclass:: False_
   :members:

.. autoclass:: FunctionFilter
   :members:

.. autoclass:: Label
   :members:

.. autoclass:: Null
   :members:

.. autoclass:: Operators
   :members:
   :special-members:

.. autoclass:: Over
   :members:

.. autoclass:: SQLColumnExpression

.. autoclass:: TextClause
   :members:

.. autoclass:: TryCast
   :members:

.. autoclass:: Tuple
   :members:

.. autoclass:: WithinGroup
   :members:

.. autoclass:: sqlalchemy.sql.elements.WrapsColumnExpression
   :members:

.. autoclass:: True_
   :members:

.. autoclass:: TypeCoerce
   :members:

.. autoclass:: UnaryExpression
   :members:

列元素类型实用程序
-------------------------------

Column Element Typing Utilities

.. tab:: 中文

.. tab:: 英文

Standalone utility functions imported from the ``sqlalchemy`` namespace
to improve support by type checkers.


.. autofunction:: sqlalchemy.NotNullable

.. autofunction:: sqlalchemy.Nullable
