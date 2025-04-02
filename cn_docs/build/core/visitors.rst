访问者和遍历实用程序
================================

Visitor and Traversal Utilities

.. tab:: 中文

   :mod:`sqlalchemy.sql.visitors` 模块由类和函数组成，其目的是通用地 **遍历** 核心 SQL 表达式结构。这与 Python 的 ``ast`` 模块类似，它提供了一个系统，使程序可以对 SQL 表达式的每个组件进行操作。常见的用途包括定位各种元素，如 :class:`_schema.Table` 或 :class:`.BindParameter` 对象，以及更改结构的状态，例如用其他 FROM 子句替换某些 FROM 子句。

   .. note:: 
      
      :mod:`sqlalchemy.sql.visitors` 模块是一个内部 API，并不是完全公开的。它可能会发生变化，并且可能在未考虑到 SQLAlchemy 自身内部的使用模式下无法按预期工作。

   :mod:`sqlalchemy.sql.visitors` 模块是 SQLAlchemy **内部** 的一部分，通常不会被调用的应用程序代码使用。然而，它在某些边缘情况下使用，例如构建缓存例程时，以及使用 :ref:`自定义 SQL 构造和编译扩展 <sqlalchemy.ext.compiler_toplevel>` 构建自定义 SQL 表达式时。

.. tab:: 英文

   The :mod:`sqlalchemy.sql.visitors` module consists of classes and functions
   that serve the purpose of generically **traversing** a Core SQL expression
   structure.   This is not unlike the Python ``ast`` module in that is presents
   a system by which a program can operate upon each component of a SQL
   expression.   Common purposes this serves are locating various kinds of
   elements such as :class:`_schema.Table` or :class:`.BindParameter` objects,
   as well as altering the state of the structure such as replacing certain FROM
   clauses with others.

   .. note:: the :mod:`sqlalchemy.sql.visitors` module is an internal API and
      is not fully public.    It is subject to change and may additionally not
      function as expected for use patterns that aren't considered within
      SQLAlchemy's own internals.

   The :mod:`sqlalchemy.sql.visitors` module is part of the **internals** of
   SQLAlchemy and it is not usually used by calling application code.  It is
   however used in certain edge cases such as when constructing caching routines
   as well as when building out custom SQL expressions using the
   :ref:`Custom SQL Constructs and Compilation Extension <sqlalchemy.ext.compiler_toplevel>`.

.. automodule:: sqlalchemy.sql.visitors
   :members:
   :private-members:

