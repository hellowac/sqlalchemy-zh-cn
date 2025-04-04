.. currentmodule:: sqlalchemy.orm

.. _mapper_composite:

复合列类型
======================

Composite Column Types

.. tab:: 中文

    成组的列可以与单个用户定义的数据类型关联，在现代使用中通常是一个Python dataclass_。ORM 提供了一个代表您提供的列组的单一属性。

    一个简单的例子将成对的 :class:`_types.Integer` 列表示为一个 ``Point`` 对象，具有 ``.x`` 和 ``.y`` 属性。使用 dataclass，这些属性使用相应的 ``int`` Python 类型定义::

        import dataclasses


        @dataclasses.dataclass
        class Point:
            x: int
            y: int

    非dataclass形式也被接受，但需要实现额外的方法。有关使用非dataclass类的示例，请参见 :ref:`composite_legacy_no_dataclass` 部分。

    .. versionadded:: 2.0 :func:`_orm.composite` 结构完全支持Python dataclass，包括从组合类派生映射列数据类型的能力。

    我们将创建一个映射到表 ``vertices`` 的映射，表示为 ``x1/y1`` 和 ``x2/y2`` 的两个点。使用 :func:`_orm.composite` 结构将 ``Point`` 类与映射列相关联。

    下面的示例说明了使用完整的 :ref:`Annotated Declarative Table <orm_declarative_mapped_column>` 配置的最现代形式的 :func:`_orm.composite`。表示每列的 :func:`_orm.mapped_column` 结构直接传递给 :func:`_orm.composite`，指示要生成的列的零个或多个方面，在这种情况下是名称; :func:`_orm.composite` 结构直接从 dataclass 派生列类型（在这种情况下为 ``int``，对应于 :class:`_types.Integer`）::

        from sqlalchemy.orm import DeclarativeBase, Mapped
        from sqlalchemy.orm import composite, mapped_column


        class Base(DeclarativeBase):
            pass


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)

            start: Mapped[Point] = composite(mapped_column("x1"), mapped_column("y1"))
            end: Mapped[Point] = composite(mapped_column("x2"), mapped_column("y2"))

            def __repr__(self):
                return f"Vertex(start={self.start}, end={self.end})"

    .. tip:: 
        
        在上面的示例中，表示组合的列（ ``x1`` ， ``y1`` ，等）也可以在类上访问，但类型检查器无法正确理解。如果访问单个列很重要，它们可以显式声明，如 :ref:`composite_with_typing` 中所示。

    上述映射将对应于一个 CREATE TABLE 语句，如下所示:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.schema import CreateTable
        >>> print(CreateTable(Vertex.__table__))
        {printsql}CREATE TABLE vertices (
        id INTEGER NOT NULL,
        x1 INTEGER NOT NULL,
        y1 INTEGER NOT NULL,
        x2 INTEGER NOT NULL,
        y2 INTEGER NOT NULL,
        PRIMARY KEY (id)
        )

.. tab:: 英文

    Sets of columns can be associated with a single user-defined datatype,
    which in modern use is normally a Python dataclass_. The ORM
    provides a single attribute which represents the group of columns using the
    class you provide.

    A simple example represents pairs of :class:`_types.Integer` columns as a
    ``Point`` object, with attributes ``.x`` and ``.y``.   Using a
    dataclass, these attributes are defined with the corresponding ``int``
    Python type::

        import dataclasses


        @dataclasses.dataclass
        class Point:
            x: int
            y: int

    Non-dataclass forms are also accepted, but require additional methods
    to be implemented.  For an example using a non-dataclass class, see the section
    :ref:`composite_legacy_no_dataclass`.

    .. versionadded:: 2.0 The :func:`_orm.composite` construct fully supports
    Python dataclasses including the ability to derive mapped column datatypes
    from the composite class.

    We will create a mapping to a table ``vertices``, which represents two points
    as ``x1/y1`` and ``x2/y2``.   The ``Point`` class is associated with
    the mapped columns using the :func:`_orm.composite` construct.

    The example below illustrates the most modern form of :func:`_orm.composite` as
    used with a fully
    :ref:`Annotated Declarative Table <orm_declarative_mapped_column>`
    configuration. :func:`_orm.mapped_column` constructs representing each column
    are passed directly to :func:`_orm.composite`, indicating zero or more aspects
    of the columns to be generated, in this case the names; the
    :func:`_orm.composite` construct derives the column types (in this case
    ``int``, corresponding to :class:`_types.Integer`) from the dataclass directly::

        from sqlalchemy.orm import DeclarativeBase, Mapped
        from sqlalchemy.orm import composite, mapped_column


        class Base(DeclarativeBase):
            pass


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)

            start: Mapped[Point] = composite(mapped_column("x1"), mapped_column("y1"))
            end: Mapped[Point] = composite(mapped_column("x2"), mapped_column("y2"))

            def __repr__(self):
                return f"Vertex(start={self.start}, end={self.end})"

    .. tip:: In the example above the columns that represent the composites
        (``x1``, ``y1``, etc.) are also accessible on the class but are not
        correctly understood by type checkers.
        If accessing the single columns is important they can be explicitly declared,
        as shown in :ref:`composite_with_typing`.

    The above mapping would correspond to a CREATE TABLE statement as:

    .. sourcecode:: pycon+sql

        >>> from sqlalchemy.schema import CreateTable
        >>> print(CreateTable(Vertex.__table__))
        {printsql}CREATE TABLE vertices (
        id INTEGER NOT NULL,
        x1 INTEGER NOT NULL,
        y1 INTEGER NOT NULL,
        x2 INTEGER NOT NULL,
        y2 INTEGER NOT NULL,
        PRIMARY KEY (id)
        )


使用映射复合列类型
-------------------------------------------

Working with Mapped Composite Column Types

.. tab:: 中文

    通过如上所示的映射，我们可以使用 ``Vertex`` 类，其中 ``.start`` 和 ``.end`` 属性将透明地引用 ``Point`` 类引用的列，以及 ``Vertex`` 类的实例，其中 ``.start`` 和 ``.end`` 属性将引用 ``Point`` 类的实例。 ``x1``、 ``y1``、 ``x2`` 和 ``y2`` 列透明地处理:

    * **持久化 Point 对象**

      我们可以创建一个 ``Vertex`` 对象，分配 ``Point`` 对象作为成员，并且它们将按预期持久化:

      .. sourcecode:: pycon+sql
  
          >>> v = Vertex(start=Point(3, 4), end=Point(5, 6))
          >>> session.add(v)
          >>> session.commit()
          {execsql}BEGIN (implicit)
          INSERT INTO vertices (x1, y1, x2, y2) VALUES (?, ?, ?, ?)
          [generated in ...] (3, 4, 5, 6)
          COMMIT

    * **选择 Point 对象作为列**

      :func:`_orm.composite` 将允许 ``Vertex.start`` 和 ``Vertex.end`` 属性在使用 ORM :class:`_orm.Session`（包括遗留的 :class:`_orm.Query` 对象）选择 ``Point`` 对象时尽可能地表现为单个 SQL 表达式:

      .. sourcecode:: pycon+sql

            >>> stmt = select(Vertex.start, Vertex.end)
            >>> session.execute(stmt).all()
            {execsql}SELECT vertices.x1, vertices.y1, vertices.x2, vertices.y2
            FROM vertices
            [...] ()
            {stop}[(Point(x=3, y=4), Point(x=5, y=6))]

    * **在 SQL 表达式中比较 Point 对象**

      ``Vertex.start`` 和 ``Vertex.end`` 属性可以在 WHERE 条件和类似的地方使用，使用临时的 ``Point`` 对象进行比较:

      .. sourcecode:: pycon+sql

            >>> stmt = select(Vertex).where(Vertex.start == Point(3, 4)).where(Vertex.end < Point(7, 8))
            >>> session.scalars(stmt).all()
            {execsql}SELECT vertices.id, vertices.x1, vertices.y1, vertices.x2, vertices.y2
            FROM vertices
            WHERE vertices.x1 = ? AND vertices.y1 = ? AND vertices.x2 < ? AND vertices.y2 < ?
            [...] (3, 4, 7, 8)
            {stop}[Vertex(Point(x=3, y=4), Point(x=5, y=6))]

      .. versionadded:: 2.0  
         
            :func:`_orm.composite` 构造现在支持“排序”比较，如 ``<``、 ``>=`` 和类似的，除了已经存在的支持 ``==``、 ``!=``。

      .. tip:: 
        
            上述使用“小于”操作符（ ``<`` ）的“排序”比较以及使用 ``==`` 的“等式”比较，在生成 SQL 表达式时，由 :class:`_orm.Composite.Comparator` 类实现，而不使用组合类本身的比较方法，例如 ``__lt__()`` 或 ``__eq__()`` 方法。因此，上述 ``Point`` dataclass 也不需要实现 dataclasses ``order=True`` 参数以使上述 SQL 操作工作。有关如何自定义比较操作的背景，请参阅 :ref:`composite_operations`。

    * **更新 Vertex 实例上的 Point 对象**

    默认情况下，**必须用新对象替换** ``Point`` 对象，以检测到更改:

    .. sourcecode:: pycon+sql

        >>> v1 = session.scalars(select(Vertex)).one()
            {execsql}SELECT vertices.id, vertices.x1, vertices.y1, vertices.x2, vertices.y2
            FROM vertices
            [...] ()
            {stop}
    
            >>> v1.end = Point(x=10, y=14)
            >>> session.commit()
            {execsql}UPDATE vertices SET x2=?, y2=? WHERE vertices.id = ?
            [...] (10, 14, 1)
            COMMIT
    
        为了在组合对象上允许就地更改，必须使用 :ref:`mutable_toplevel` 扩展。有关示例，请参阅 :ref:`mutable_composites` 部分。
    
.. tab:: 英文
    
    With a mapping as illustrated in the top section, we can work with the
    ``Vertex`` class, where the ``.start`` and ``.end`` attributes will
    transparently refer to the columns referenced by the ``Point`` class, as
    well as with instances of the ``Vertex`` class, where the ``.start`` and
    ``.end`` attributes will refer to instances of the ``Point`` class. The ``x1``,
    ``y1``, ``x2``, and ``y2`` columns are handled transparently:
    
    * **Persisting Point objects**
    
      We can create a ``Vertex`` object, assign ``Point`` objects as members,
      and they will be persisted as expected:
    
      .. sourcecode:: pycon+sql
    
        >>> v = Vertex(start=Point(3, 4), end=Point(5, 6))
        >>> session.add(v)
        >>> session.commit()
        {execsql}BEGIN (implicit)
        INSERT INTO vertices (x1, y1, x2, y2) VALUES (?, ?, ?, ?)
        [generated in ...] (3, 4, 5, 6)
        COMMIT
    
    * **Selecting Point objects as columns**
    
      :func:`_orm.composite` will allow the ``Vertex.start`` and ``Vertex.end``
      attributes to behave like a single SQL expression to as much an extent
      as possible when using the ORM :class:`_orm.Session` (including the legacy
      :class:`_orm.Query` object) to select ``Point`` objects:
    
      .. sourcecode:: pycon+sql
    
        >>> stmt = select(Vertex.start, Vertex.end)
        >>> session.execute(stmt).all()
        {execsql}SELECT vertices.x1, vertices.y1, vertices.x2, vertices.y2
        FROM vertices
        [...] ()
        {stop}[(Point(x=3, y=4), Point(x=5, y=6))]
    
    * **Comparing Point objects in SQL expressions**
    
      The ``Vertex.start`` and ``Vertex.end`` attributes may be used in
      WHERE criteria and similar, using ad-hoc ``Point`` objects for comparisons:
    
      .. sourcecode:: pycon+sql
    
        >>> stmt = select(Vertex).where(Vertex.start == Point(3, 4)).where(Vertex.end < Point(7, 8))
        >>> session.scalars(stmt).all()
        {execsql}SELECT vertices.id, vertices.x1, vertices.y1, vertices.x2, vertices.y2
        FROM vertices
        WHERE vertices.x1 = ? AND vertices.y1 = ? AND vertices.x2 < ? AND vertices.y2 < ?
        [...] (3, 4, 7, 8)
        {stop}[Vertex(Point(x=3, y=4), Point(x=5, y=6))]
    
      .. versionadded:: 2.0  :func:`_orm.composite` constructs now support
         "ordering" comparisons such as ``<``, ``>=``, and similar, in addition
         to the already-present support for ``==``, ``!=``.
    
      .. tip::  The "ordering" comparison above using the "less than" operator (``<``)
         as well as the "equality" comparison using ``==``, when used to generate
         SQL expressions, are implemented by the :class:`_orm.Composite.Comparator`
         class, and don't make use of the comparison methods on the composite class
         itself, e.g. the ``__lt__()`` or ``__eq__()`` methods. From this it
         follows that the ``Point`` dataclass above also need not implement the
         dataclasses ``order=True`` parameter for the above SQL operations to work.
         The section :ref:`composite_operations` contains background on how
         to customize the comparison operations.
    
    * **Updating Point objects on Vertex Instances**
    
      By default, the ``Point`` object **must be replaced by a new object** for
      changes to be detected:
    
      .. sourcecode:: pycon+sql
    
        >>> v1 = session.scalars(select(Vertex)).one()
        {execsql}SELECT vertices.id, vertices.x1, vertices.y1, vertices.x2, vertices.y2
        FROM vertices
        [...] ()
        {stop}
    
        >>> v1.end = Point(x=10, y=14)
        >>> session.commit()
        {execsql}UPDATE vertices SET x2=?, y2=? WHERE vertices.id = ?
        [...] (10, 14, 1)
        COMMIT
    
      In order to allow in place changes on the composite object, the
      :ref:`mutable_toplevel` extension must be used.  See the section
      :ref:`mutable_composites` for examples.



.. _orm_composite_other_forms:

复合的其他映射形式
----------------------------------

Other mapping forms for composites

.. tab:: 中文

    :func:`_orm.composite` 构造可以使用 :func:`_orm.mapped_column` 构造、:class:`_schema.Column` 或现有映射列的字符串名称传递相关列。以下示例说明了与上述主要部分等效的映射。

.. tab:: 英文

    The :func:`_orm.composite` construct may be passed the relevant columns
    using a :func:`_orm.mapped_column` construct, a :class:`_schema.Column`,
    or the string name of an existing mapped column.   The following examples
    illustrate an equivalent mapping as that of the main section above.

直接映射列，然后传递给 composite
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Map columns directly, then pass to composite

.. tab:: 中文

    在这里，我们将现有的 :func:`_orm.mapped_column` 实例传递给 :func:`_orm.composite` 构造，如下面的非注释示例中，我们还将 ``Point`` 类作为第一个参数传递给 :func:`_orm.composite`::

        from sqlalchemy import Integer
        from sqlalchemy.orm import mapped_column, composite


        class Vertex(Base):
            __tablename__ = "vertices"

            id = mapped_column(Integer, primary_key=True)
            x1 = mapped_column(Integer)
            y1 = mapped_column(Integer)
            x2 = mapped_column(Integer)
            y2 = mapped_column(Integer)

            start = composite(Point, x1, y1)
            end = composite(Point, x2, y2)

.. tab:: 英文

    Here we pass the existing :func:`_orm.mapped_column` instances to the
    :func:`_orm.composite` construct, as in the non-annotated example below
    where we also pass the ``Point`` class as the first argument to
    :func:`_orm.composite`::

        from sqlalchemy import Integer
        from sqlalchemy.orm import mapped_column, composite


        class Vertex(Base):
            __tablename__ = "vertices"

            id = mapped_column(Integer, primary_key=True)
            x1 = mapped_column(Integer)
            y1 = mapped_column(Integer)
            x2 = mapped_column(Integer)
            y2 = mapped_column(Integer)

            start = composite(Point, x1, y1)
            end = composite(Point, x2, y2)

.. _composite_with_typing:

直接映射列，将属性名称传递给复合
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Map columns directly, pass attribute names to composite

.. tab:: 中文

    我们可以使用更多带注释的形式编写上述相同的示例，其中我们可以选择将属性名称传递给 :func:`_orm.composite` 而不是完整的列构造::

        from sqlalchemy.orm import mapped_column, composite, Mapped


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)
            x1: Mapped[int]
            y1: Mapped[int]
            x2: Mapped[int]
            y2: Mapped[int]

            start: Mapped[Point] = composite("x1", "y1")
            end: Mapped[Point] = composite("x2", "y2")

.. tab:: 英文

    We can write the same example above using more annotated forms where we have
    the option to pass attribute names to :func:`_orm.composite` instead of
    full column constructs::

        from sqlalchemy.orm import mapped_column, composite, Mapped


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)
            x1: Mapped[int]
            y1: Mapped[int]
            x2: Mapped[int]
            y2: Mapped[int]

            start: Mapped[Point] = composite("x1", "y1")
            end: Mapped[Point] = composite("x2", "y2")

命令式映射和命令式表
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Imperative mapping and imperative table

.. tab:: 中文

    当使用 :ref:`imperative table <orm_imperative_table_configuration>` 或完全 :ref:`imperative <orm_imperative_mapping>` 映射时，我们可以直接访问 :class:`_schema.Column` 对象。这些对象也可以传递给 :func:`_orm.composite`，如下述命令式示例所示::

        mapper_registry.map_imperatively(
            Vertex,
            vertices_table,
            properties={
                "start": composite(Point, vertices_table.c.x1, vertices_table.c.y1),
                "end": composite(Point, vertices_table.c.x2, vertices_table.c.y2),
            },
        )

.. tab:: 英文

    When using :ref:`imperative table <orm_imperative_table_configuration>` or
    fully :ref:`imperative <orm_imperative_mapping>` mappings, we have access
    to :class:`_schema.Column` objects directly.  These may be passed to
    :func:`_orm.composite` as well, as in the imperative example below::

        mapper_registry.map_imperatively(
            Vertex,
            vertices_table,
            properties={
                "start": composite(Point, vertices_table.c.x1, vertices_table.c.y1),
                "end": composite(Point, vertices_table.c.x2, vertices_table.c.y2),
            },
        )

.. _composite_legacy_no_dataclass:

使用旧式非数据类
----------------------------

Using Legacy Non-Dataclasses

.. tab:: 中文

    如果不使用 dataclass，自定义数据类型类的要求是它有一个接受与其列格式对应的位置参数的构造函数，并且还提供一个 ``__composite_values__()`` 方法，该方法按其基于列的属性顺序返回对象的状态，作为列表或元组。它还应提供适当的 ``__eq__()`` 和 ``__ne__()`` 方法来测试两个实例的相等性。

    为了说明不使用 dataclass 的主部分中的等效 ``Point`` 类::

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __composite_values__(self):
                return self.x, self.y

            def __repr__(self):
                return f"Point(x={self.x!r}, y={self.y!r})"

            def __eq__(self, other):
                return isinstance(other, Point) and other.x == self.x and other.y == self.y

            def __ne__(self, other):
                return not self.__eq__(other)

    然后使用 :func:`_orm.composite`，其中必须使用 :ref:`orm_composite_other_forms` 中的一种形式显式声明与 ``Point`` 类关联的列。

.. tab:: 英文

    If not using a dataclass, the requirements for the custom datatype class are
    that it have a constructor
    which accepts positional arguments corresponding to its column format, and
    also provides a method ``__composite_values__()`` which returns the state of
    the object as a list or tuple, in order of its column-based attributes. It
    also should supply adequate ``__eq__()`` and ``__ne__()`` methods which test
    the equality of two instances.

    To illustrate the equivalent ``Point`` class from the main section
    not using a dataclass::

        class Point:
            def __init__(self, x, y):
                self.x = x
                self.y = y

            def __composite_values__(self):
                return self.x, self.y

            def __repr__(self):
                return f"Point(x={self.x!r}, y={self.y!r})"

            def __eq__(self, other):
                return isinstance(other, Point) and other.x == self.x and other.y == self.y

            def __ne__(self, other):
                return not self.__eq__(other)

    Usage with :func:`_orm.composite` then proceeds where the columns to be
    associated with the ``Point`` class must also be declared with explicit
    types, using one of the forms at :ref:`orm_composite_other_forms`.


跟踪复合上的就地突变
-----------------------------------------

Tracking In-Place Mutations on Composites

.. tab:: 中文

    现有组合值的就地更改不会自动跟踪。相反，组合类需要显式地向其父对象提供事件。通过使用 :class:`.MutableComposite` 混入类，这项任务在很大程度上是自动化的，该类使用事件将每个用户定义的组合对象与所有父关联关联起来。请参阅 :ref:`mutable_composites` 中的示例。

.. tab:: 英文

    In-place changes to an existing composite value are
    not tracked automatically.  Instead, the composite class needs to provide
    events to its parent object explicitly.   This task is largely automated
    via the usage of the :class:`.MutableComposite` mixin, which uses events
    to associate each user-defined composite object with all parent associations.
    Please see the example in :ref:`mutable_composites`.

.. _composite_operations:

重新定义复合的比较操作
-----------------------------------------------

Redefining Comparison Operations for Composites

.. tab:: 中文

    默认情况下，“等于”比较操作会生成所有相应列相互等价的 AND。这可以使用 :func:`.composite` 的 ``comparator_factory`` 参数更改，我们在其中指定一个自定义的 :class:`.CompositeProperty.Comparator` 类来定义现有或新操作。下面我们说明了“大于”操作符，实现了与基本“大于”操作相同的表达式::

        import dataclasses

        from sqlalchemy.orm import composite
        from sqlalchemy.orm import CompositeProperty
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.sql import and_


        @dataclasses.dataclass
        class Point:
            x: int
            y: int


        class PointComparator(CompositeProperty.Comparator):
            def __gt__(self, other):
                """重新定义“大于”操作"""

                return and_(
                    *[
                        a > b
                        for a, b in zip(
                            self.__clause_element__().clauses,
                            dataclasses.astuple(other),
                        )
                    ]
                )


        class Base(DeclarativeBase):
            pass


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)

            start: Mapped[Point] = composite(
                mapped_column("x1"), mapped_column("y1"), comparator_factory=PointComparator
            )
            end: Mapped[Point] = composite(
                mapped_column("x2"), mapped_column("y2"), comparator_factory=PointComparator
            )

    由于 ``Point`` 是一个dataclass，我们可以使用 ``dataclasses.astuple()`` 获取 ``Point`` 实例的元组形式。

    然后自定义比较器返回适当的SQL表达式:

    .. sourcecode:: pycon+sql

        >>> print(Vertex.start > Point(5, 6))
        {printsql}vertices.x1 > :x1_1 AND vertices.y1 > :y1_1

.. tab:: 英文

    The "equals" comparison operation by default produces an AND of all
    corresponding columns equated to one another. This can be changed using
    the ``comparator_factory`` argument to :func:`.composite`, where we
    specify a custom :class:`.CompositeProperty.Comparator` class
    to define existing or new operations.
    Below we illustrate the "greater than" operator, implementing
    the same expression that the base "greater than" does::

        import dataclasses

        from sqlalchemy.orm import composite
        from sqlalchemy.orm import CompositeProperty
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.sql import and_


        @dataclasses.dataclass
        class Point:
            x: int
            y: int


        class PointComparator(CompositeProperty.Comparator):
            def __gt__(self, other):
                """redefine the 'greater than' operation"""

                return and_(
                    *[
                        a > b
                        for a, b in zip(
                            self.__clause_element__().clauses,
                            dataclasses.astuple(other),
                        )
                    ]
                )


        class Base(DeclarativeBase):
            pass


        class Vertex(Base):
            __tablename__ = "vertices"

            id: Mapped[int] = mapped_column(primary_key=True)

            start: Mapped[Point] = composite(
                mapped_column("x1"), mapped_column("y1"), comparator_factory=PointComparator
            )
            end: Mapped[Point] = composite(
                mapped_column("x2"), mapped_column("y2"), comparator_factory=PointComparator
            )

    Since ``Point`` is a dataclass, we may make use of
    ``dataclasses.astuple()`` to get a tuple form of ``Point`` instances.

    The custom comparator then returns the appropriate SQL expression:

    .. sourcecode:: pycon+sql

        >>> print(Vertex.start > Point(5, 6))
        {printsql}vertices.x1 > :x1_1 AND vertices.y1 > :y1_1


嵌套复合
-------------------

Nesting Composites

.. tab:: 中文

    组合对象可以定义为在简单的嵌套方案中工作，通过在组合类中重新定义行为以按预期工作，然后通常将组合类映射到单个列的完整长度。这要求定义在“嵌套(nested)”和“平面(flat)”形式之间移动的附加方法。

    下面我们将 ``Vertex`` 类重新组织为本身是一个引用 ``Point`` 对象的组合对象。 ``Vertex`` 和 ``Point`` 可以是 dataclass，不过我们将为 ``Vertex`` 添加一个自定义构造方法，该方法可以用来根据四个列值创建新的 ``Vertex`` 对象，我们将任意命名为 ``_generate()`` 并定义为类方法，以便我们可以通过将值传递给 ``Vertex._generate()`` 方法来创建新的 ``Vertex`` 对象。

    我们还将实现 ``__composite_values__()`` 方法，这是一个由 :func:`_orm.composite` 构造（之前在 :ref:`composite_legacy_no_dataclass` 中介绍）识别的固定名称，表示以平面列值元组接收对象的标准方式，在这种情况下将取代通常的 dataclass 方法。

    有了自定义的 ``_generate()`` 构造函数和 ``__composite_values__()`` 序列化方法，我们现在可以在平面列元组和包含 ``Point`` 实例的 ``Vertex`` 对象之间移动。 ``Vertex._generate`` 方法作为第一个参数传递给 :func:`_orm.composite` 构造作为新 ``Vertex`` 实例的来源，``__composite_values__()`` 方法将由 :func:`_orm.composite` 隐式使用。

    为了示例的目的，``Vertex`` 组合然后映射到一个称为 ``HasVertex`` 的类，这是包含四个源列的 :class:`.Table` 最终所在的地方::

        from __future__ import annotations

        import dataclasses
        from typing import Any
        from typing import Tuple

        from sqlalchemy.orm import composite
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        @dataclasses.dataclass
        class Point:
            x: int
            y: int


        @dataclasses.dataclass
        class Vertex:
            start: Point
            end: Point

            @classmethod
            def _generate(cls, x1: int, y1: int, x2: int, y2: int) -> Vertex:
                """从行生成 Vertex"""
                return Vertex(Point(x1, y1), Point(x2, y2))

            def __composite_values__(self) -> Tuple[Any, ...]:
                """从 Vertex 生成一行"""
                return dataclasses.astuple(self.start) + dataclasses.astuple(self.end)


        class Base(DeclarativeBase):
            pass


        class HasVertex(Base):
            __tablename__ = "has_vertex"
            id: Mapped[int] = mapped_column(primary_key=True)
            x1: Mapped[int]
            y1: Mapped[int]
            x2: Mapped[int]
            y2: Mapped[int]

            vertex: Mapped[Vertex] = composite(Vertex._generate, "x1", "y1", "x2", "y2")

    上述映射可以在 ``HasVertex``、``Vertex`` 和 ``Point`` 方面使用::

        hv = HasVertex(vertex=Vertex(Point(1, 2), Point(3, 4)))

        session.add(hv)
        session.commit()

        stmt = select(HasVertex).where(HasVertex.vertex == Vertex(Point(1, 2), Point(3, 4)))

        hv = session.scalars(stmt).first()
        print(hv.vertex.start)
        print(hv.vertex.end)

.. tab:: 英文

    Composite objects can be defined to work in simple nested schemes, by
    redefining behaviors within the composite class to work as desired, then
    mapping the composite class to the full length of individual columns normally.
    This requires that additional methods to move between the "nested" and
    "flat" forms are defined.

    Below we reorganize the ``Vertex`` class to itself be a composite object which
    refers to ``Point`` objects. ``Vertex`` and ``Point`` can be dataclasses,
    however we will add a custom construction method to ``Vertex`` that can be used
    to create new ``Vertex`` objects given four column values, which will will
    arbitrarily name ``_generate()`` and define as a classmethod so that we can
    make new ``Vertex`` objects by passing values to the ``Vertex._generate()``
    method.

    We will also implement the ``__composite_values__()`` method, which is a fixed
    name recognized by the :func:`_orm.composite` construct (introduced previously
    at :ref:`composite_legacy_no_dataclass`) that indicates a standard way of
    receiving the object as a flat tuple of column values, which in this case will
    supersede the usual dataclass-oriented methodology.

    With our custom ``_generate()`` constructor and
    ``__composite_values__()`` serializer method, we can now move between
    a flat tuple of columns and ``Vertex`` objects that contain ``Point``
    instances.   The ``Vertex._generate`` method is passed as the
    first argument to the :func:`_orm.composite` construct as the source of new
    ``Vertex`` instances, and the ``__composite_values__()`` method will be
    used implicitly by :func:`_orm.composite`.

    For the purposes of the example, the ``Vertex`` composite is then mapped to a
    class called ``HasVertex``, which is where the :class:`.Table` containing the
    four source columns ultimately resides::

        from __future__ import annotations

        import dataclasses
        from typing import Any
        from typing import Tuple

        from sqlalchemy.orm import composite
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        @dataclasses.dataclass
        class Point:
            x: int
            y: int


        @dataclasses.dataclass
        class Vertex:
            start: Point
            end: Point

            @classmethod
            def _generate(cls, x1: int, y1: int, x2: int, y2: int) -> Vertex:
                """generate a Vertex from a row"""
                return Vertex(Point(x1, y1), Point(x2, y2))

            def __composite_values__(self) -> Tuple[Any, ...]:
                """generate a row from a Vertex"""
                return dataclasses.astuple(self.start) + dataclasses.astuple(self.end)


        class Base(DeclarativeBase):
            pass


        class HasVertex(Base):
            __tablename__ = "has_vertex"
            id: Mapped[int] = mapped_column(primary_key=True)
            x1: Mapped[int]
            y1: Mapped[int]
            x2: Mapped[int]
            y2: Mapped[int]

            vertex: Mapped[Vertex] = composite(Vertex._generate, "x1", "y1", "x2", "y2")

    The above mapping can then be used in terms of ``HasVertex``, ``Vertex``, and
    ``Point``::

        hv = HasVertex(vertex=Vertex(Point(1, 2), Point(3, 4)))

        session.add(hv)
        session.commit()

        stmt = select(HasVertex).where(HasVertex.vertex == Vertex(Point(1, 2), Point(3, 4)))

        hv = session.scalars(stmt).first()
        print(hv.vertex.start)
        print(hv.vertex.end)

.. _dataclass: https://docs.python.org/3/library/dataclasses.html

复合 API
-------------

Composite API

.. autofunction:: composite

