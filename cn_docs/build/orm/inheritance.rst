.. _inheritance_toplevel:

映射类继承层次结构
=====================================

Mapping Class Inheritance Hierarchies

.. tab:: 中文

    SQLAlchemy 支持三种形式的继承：

    * **单表继承** – 多种类型的类由一个表表示；

    * **具体表继承** – 每种类型的类由独立的表表示；

    * **连接表继承** – 类层次结构被拆分为依赖表。每个类由其自己的表表示，该表仅包括该类本地的那些属性。

    最常见的继承形式是单表和连接表，而具体继承在配置上带来更多的挑战。

    当映射器在继承关系中配置时，SQLAlchemy 能够 :term:`多态地` 加载元素，这意味着单个查询可以返回多种类型的对象。

    .. seealso::

        :ref:`loading_joined_inheritance` - 在 :ref:`queryguide_toplevel` 中

        :ref:`examples_inheritance` - 完整的连接、单表和具体继承示例

.. tab:: 英文

    SQLAlchemy supports three forms of inheritance:

    * **single table inheritance** – several types of classes are represented by a single table;

    * **concrete table inheritance** – each type of class is represented by independent tables;

    * **joined table inheritance** – the class hierarchy is broken up among dependent tables. Each class represented by its own table that only includes those attributes local to that class.

    The most common forms of inheritance are single and joined table, while
    concrete inheritance presents more configurational challenges.

    When mappers are configured in an inheritance relationship, SQLAlchemy has the
    ability to load elements :term:`polymorphically`, meaning that a single query can
    return objects of multiple types.

    .. seealso::

        :ref:`loading_joined_inheritance` - in the :ref:`queryguide_toplevel`

        :ref:`examples_inheritance` - complete examples of joined, single and concrete inheritance

.. _joined_inheritance:

连接表继承
------------------------

Joined Table Inheritance

.. tab:: 中文

    在连接表继承中，类层次结构中的每个类由一个独特的表表示。查询层次结构中的特定子类将呈现为其继承路径中所有表的 SQL JOIN。如果查询的类是基类，则查询基表，同时可以选择包括其他表或允许子表特定属性稍后加载。

    在所有情况下，确定给定行要实例化的最终类是通过在基类上定义的 :term:`discriminator` 列或 SQL 表达式，该列或表达式将产生一个标量值，该值与特定子类相关联。

    在连接继承层次结构中，基类配置了指示多态鉴别列的附加参数，以及可选的基类本身的多态标识符::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }

            def __repr__(self):
                return f"{self.__class__.__name__}({self.name!r})"

    在上面的示例中，鉴别器是 ``type`` 列，它是使用 :paramref:`_orm.Mapper.polymorphic_on` 参数配置的。此参数接受列导向的表达式，可以是要使用的映射属性的字符串名称，也可以是列表达式对象，例如 :class:`_schema.Column` 或 :func:`_orm.mapped_column` 构造。

    鉴别列将存储一个值，该值指示行中表示的对象类型。该列可以是任何数据类型，但字符串和整数是最常见的。为数据库中特定行应用此列的实际数据值是使用 :paramref:`_orm.Mapper.polymorphic_identity` 参数指定的，如下所述。

    虽然多态鉴别表达式不是严格必要的，但如果需要多态加载，则是必需的。在基表上建立列是实现这一目标的最简单方法，但是非常复杂的继承映射可以使用 SQL 表达式，例如 CASE 表达式，作为多态鉴别器。

    .. note::

        目前，**整个继承层次结构只能配置一个鉴别列或 SQL 表达式**，通常在层次结构中的最基类上。不支持“级联”多态鉴别表达式。

    接下来我们定义 ``Employee`` 的 ``Engineer`` 和 ``Manager`` 子类。每个子类包含表示其代表的子类特有属性的列。每个表还必须包含一个主键列（或列），以及到父表的外键引用::

        class Engineer(Employee):
            __tablename__ = "engineer"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            engineer_name: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            manager_name: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

    在上面的示例中，每个映射在其映射参数中指定 :paramref:`_orm.Mapper.polymorphic_identity` 参数。此值填充由基映射器中建立的 :paramref:`_orm.Mapper.polymorphic_on` 参数指定的列。:paramref:`_orm.Mapper.polymorphic_identity` 参数在整个层次结构中的每个映射类中应该是唯一的，并且每个映射类只能有一个“标识”；如上所述，不支持某些子类引入第二个标识的“级联”标识。

    ORM 使用 :paramref:`_orm.Mapper.polymorphic_identity` 设置的值来确定在多态加载行时一行属于哪个类。在上面的示例中，表示 ``Employee`` 的每一行将在其 ``type`` 列中具有值 ``'employee'``；同样，每个 ``Engineer`` 将获得值 ``'engineer'``，每个 ``Manager`` 将获得值 ``'manager'``。无论继承映射是像连接表继承那样使用不同的连接表，还是像单表继承那样使用一个表，都希望此值被持久化并在查询时可供 ORM 使用。:paramref:`_orm.Mapper.polymorphic_identity` 参数也适用于具体表继承，但实际上不会持久化；有关详细信息，请参阅 :ref:`concrete_inheritance` 后面的部分。

    在多态设置中，最常见的是在主键本身的同一列或列上建立外键约束，但这不是必需的；可以使与主键不同的列通过外键引用父级。从基表到子类的 JOIN 的构造方式也是直接可定制的，但这很少是必要的。

    .. topic:: 连接继承主键

        连接表继承配置的一个自然结果是，任何映射对象的标识可以完全从基表中的行确定。这显然有优势，因此 SQLAlchemy 始终认为连接继承类的主键列仅是基表的列。换句话说， ``engineer`` 和 ``manager`` 表的 ``id`` 列不用于定位 ``Engineer`` 或 ``Manager`` 对象 - 只考虑 ``employee.id`` 中的值。当然，一旦在语句中确定了父行，``engineer.id`` 和 ``manager.id`` 仍然是定位连接行的关键。

    完成连接继承映射后，针对 ``Employee`` 的查询将返回 ``Employee``、``Engineer`` 和 ``Manager`` 对象的组合。新保存的 ``Engineer``、``Manager`` 和 ``Employee`` 对象将自动使用正确的“鉴别”值填充 ``employee.type`` 列，在这种情况下为 ``"engineer"``、``"manager"`` 或 ``"employee"``，视情况而定。

.. tab:: 英文

    In joined table inheritance, each class along a hierarchy of classes
    is represented by a distinct table.  Querying for a particular subclass
    in the hierarchy will render as a SQL JOIN along all tables in its
    inheritance path. If the queried class is the base class, the base table
    is queried instead, with options to include other tables at the same time
    or to allow attributes specific to sub-tables to load later.

    In all cases, the ultimate class to instantiate for a given row is determined
    by a :term:`discriminator` column or SQL expression, defined on the base class,
    which will yield a scalar value that is associated with a particular subclass.


    The base class in a joined inheritance hierarchy is configured with
    additional arguments that will indicate to the polymorphic discriminator
    column, and optionally a polymorphic identifier for the base class itself::

        from sqlalchemy import ForeignKey
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column


        class Base(DeclarativeBase):
            pass


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }

            def __repr__(self):
                return f"{self.__class__.__name__}({self.name!r})"

    In the above example, the discriminator is the ``type`` column, whichever is
    configured using the :paramref:`_orm.Mapper.polymorphic_on` parameter. This
    parameter accepts a column-oriented expression, specified either as a string
    name of the mapped attribute to use or as a column expression object such as
    :class:`_schema.Column` or :func:`_orm.mapped_column` construct.

    The discriminator column will store a value which indicates the type of object
    represented within the row. The column may be of any datatype, though string
    and integer are the most common.  The actual data value to be applied to this
    column for a particular row in the database is specified using the
    :paramref:`_orm.Mapper.polymorphic_identity` parameter, described below.

    While a polymorphic discriminator expression is not strictly necessary, it is
    required if polymorphic loading is desired.   Establishing a column on
    the base table is the easiest way to achieve this, however very sophisticated
    inheritance mappings may make use of SQL expressions, such as a CASE
    expression, as the polymorphic discriminator.

    .. note::

        Currently, **only one discriminator column or SQL expression may be
        configured for the entire inheritance hierarchy**, typically on the base-
        most class in the hierarchy. "Cascading" polymorphic discriminator
        expressions are not yet supported.

    We next define ``Engineer`` and ``Manager`` subclasses of ``Employee``.
    Each contains columns that represent the attributes unique to the subclass
    they represent. Each table also must contain a primary key column (or
    columns), as well as a foreign key reference to the parent table::

        class Engineer(Employee):
            __tablename__ = "engineer"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            engineer_name: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            manager_name: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

    In the above example, each mapping specifies the
    :paramref:`_orm.Mapper.polymorphic_identity` parameter within its mapper arguments.
    This value populates the column designated by the
    :paramref:`_orm.Mapper.polymorphic_on` parameter established on the base  mapper.
    The :paramref:`_orm.Mapper.polymorphic_identity`  parameter should be unique to
    each mapped class across the whole hierarchy, and there should only be one
    "identity" per mapped class; as noted above,  "cascading" identities where some
    subclasses introduce a second identity are not supported.

    The ORM uses the value set up by :paramref:`_orm.Mapper.polymorphic_identity` in
    order to determine which class a row belongs towards when loading rows
    polymorphically.  In the example above, every row which represents an
    ``Employee`` will have the value ``'employee'`` in its ``type`` column; similarly,
    every ``Engineer`` will get the value ``'engineer'``, and each ``Manager`` will
    get the value ``'manager'``. Regardless of whether the inheritance mapping uses
    distinct joined tables for subclasses as in joined table inheritance, or all
    one table as in single table inheritance, this value is expected to be
    persisted and available to the ORM when querying. The
    :paramref:`_orm.Mapper.polymorphic_identity` parameter also applies to concrete
    table inheritance, but is not actually persisted; see the later section at
    :ref:`concrete_inheritance` for details.

    In a polymorphic setup, it is most common that the foreign key constraint is
    established on the same column or columns as the primary key itself, however
    this is not required; a column distinct from the primary key may also be made
    to refer to the parent via foreign key.  The way that a JOIN is constructed
    from the base table to subclasses is also directly customizable, however this
    is rarely necessary.

    .. topic:: Joined inheritance primary keys

        One natural effect of the joined table inheritance configuration is that
        the identity of any mapped object can be determined entirely from rows  in
        the base table alone. This has obvious advantages, so SQLAlchemy always
        considers the primary key columns of a joined inheritance class to be those
        of the base table only. In other words, the ``id`` columns of both the
        ``engineer`` and ``manager`` tables are not used to locate ``Engineer`` or
        ``Manager`` objects - only the value in ``employee.id`` is considered.
        ``engineer.id`` and ``manager.id`` are still of course critical to the
        proper operation of the pattern overall as they are used to locate the
        joined row, once the parent row has been determined within a statement.

    With the joined inheritance mapping complete, querying against ``Employee``
    will return a combination of ``Employee``, ``Engineer`` and ``Manager``
    objects. Newly saved ``Engineer``, ``Manager``, and ``Employee`` objects will
    automatically populate the ``employee.type`` column with the correct
    "discriminator" value in this case ``"engineer"``,
    ``"manager"``, or ``"employee"``, as appropriate.

具有连接继承的关系
+++++++++++++++++++++++++++++++++++++

Relationships with Joined Inheritance

.. tab:: 中文

    完全支持连接表继承的关系。涉及连接继承类的关系应针对与外键约束对应的层次结构中的类；如下所示，由于 ``employee`` 表有一个指向 ``company`` 表的外键约束，因此关系在 ``Company`` 和 ``Employee`` 之间设置::

        from __future__ import annotations

        from sqlalchemy.orm import relationship


        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            employees: Mapped[List[Employee]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee): ...


        class Engineer(Employee): ...

    如果外键约束在对应于子类的表上，则关系应针对该子类。 在以下示例中，从 ``manager`` 到 ``company`` 有一个外键约束，因此关系在 ``Manager`` 和 ``Company`` 类之间建立::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            managers: Mapped[List[Manager]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            manager_name: Mapped[str]

            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="managers")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee): ...

    在上面， ``Manager`` 类将具有 ``Manager.company`` 属性；``Company`` 将具有 ``Company.managers`` 属性，该属性始终加载针对 ``employee`` 和 ``manager`` 表的连接。

.. tab:: 英文

    Relationships are fully supported with joined table inheritance.   The
    relationship involving a joined-inheritance class should target the class
    in the hierarchy that also corresponds to the foreign key constraint;
    below, as the ``employee`` table has a foreign key constraint back to
    the ``company`` table, the relationships are set up between ``Company``
    and ``Employee``::

        from __future__ import annotations

        from sqlalchemy.orm import relationship


        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            employees: Mapped[List[Employee]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee): ...


        class Engineer(Employee): ...

    If the foreign key constraint is on a table corresponding to a subclass,
    the relationship should target that subclass instead.  In the example
    below, there is a foreign
    key constraint from ``manager`` to ``company``, so the relationships are
    established between the ``Manager`` and ``Company`` classes::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            managers: Mapped[List[Manager]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id: Mapped[int] = mapped_column(ForeignKey("employee.id"), primary_key=True)
            manager_name: Mapped[str]

            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="managers")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee): ...

    Above, the ``Manager`` class will have a ``Manager.company`` attribute;
    ``Company`` will have a ``Company.managers`` attribute that always
    loads against a join of the ``employee`` and ``manager`` tables together.

加载连接继承映射
+++++++++++++++++++++++++++++++++++

Loading Joined Inheritance Mappings

.. tab:: 中文

    有关继承加载技术的背景知识，请参阅部分 :ref:`inheritance_loading_toplevel`，包括在映射器配置时和查询时要查询的表的配置。

.. tab:: 英文

    See the section :ref:`inheritance_loading_toplevel` for background on inheritance loading techniques, including configuration of tables to be queried both at mapper configuration time as well as query time.

.. _single_inheritance:

单表继承
------------------------

Single Table Inheritance

.. tab:: 中文

    单表继承在单个表中表示所有子类的所有属性。特定子类具有该类独有的属性时，将其保存在表中的列中，如果行指的是其他类型的对象，这些列将为空。

    查询层次结构中的特定子类将呈现为对基表的 SELECT，其中包括一个 WHERE 子句，该子句将行限制为在鉴别列或表达式中具有特定值的行。

    与连接表继承相比，单表继承具有简单的优点；查询效率更高，因为只需要一个表即可加载所有表示的类的对象。

    单表继承配置看起来很像连接表继承，除了只有基类指定 ``__tablename__``。基表上还需要一个鉴别列，以便类可以相互区分。

    即使子类共享其所有属性的基表，在使用声明式时，:class:`_orm.mapped_column` 对象仍可以在子类上指定，表明该列仅映射到该子类；:class:`_orm.mapped_column` 将应用于相同的基 :class:`_schema.Table` 对象::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Manager(Employee):
            manager_data: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    注意，派生类 Manager 和 Engineer 的映射器省略了 ``__tablename__``，表明它们没有自己的映射表。此外，包含了带有 ``nullable=True`` 的 :func:`_orm.mapped_column` 指令；由于为这些类声明的 Python 类型不包括 ``Optional[]``，因此该列通常将映射为 ``NOT NULL``，这对于只期望为对应于该特定子类的行填充的列不合适。

.. tab:: 英文

    Single table inheritance represents all attributes of all subclasses
    within a single table.  A particular subclass that has attributes unique
    to that class will persist them within columns in the table that are otherwise
    NULL if the row refers to a different kind of object.

    Querying for a particular subclass
    in the hierarchy will render as a SELECT against the base table, which
    will include a WHERE clause that limits rows to those with a particular
    value or values present in the discriminator column or expression.

    Single table inheritance has the advantage of simplicity compared to
    joined table inheritance; queries are much more efficient as only one table
    needs to be involved in order to load objects of every represented class.

    Single-table inheritance configuration looks much like joined-table
    inheritance, except only the base class specifies ``__tablename__``. A
    discriminator column is also required on the base table so that classes can be
    differentiated from each other.

    Even though subclasses share the base table for all of their attributes, when
    using Declarative, :class:`_orm.mapped_column` objects may still be specified
    on subclasses, indicating that the column is to be mapped only to that
    subclass; the :class:`_orm.mapped_column` will be applied to the same base
    :class:`_schema.Table` object::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Manager(Employee):
            manager_data: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    Note that the mappers for the derived classes Manager and Engineer omit the
    ``__tablename__``, indicating they do not have a mapped table of
    their own.  Additionally, a :func:`_orm.mapped_column` directive with
    ``nullable=True`` is included; as the Python types declared for these classes
    do not include ``Optional[]``, the column would normally be mapped as
    ``NOT NULL``, which would not be appropriate as this column only expects to
    be populated for those rows that correspond to that particular subclass.

.. _orm_inheritance_column_conflicts:

使用 ``use_existing_column`` 解决列冲突
+++++++++++++++++++++++++++++++++++++++++++++++++++++++

Resolving Column Conflicts with ``use_existing_column``

.. tab:: 中文

    请注意，在上一节中，由于在没有自己表的子类上声明， ``manager_name`` 和 ``engineer_info`` 列已被“上移(moved up)”以应用于 ``Employee.__table__``。当两个子类要指定相同的列时，会出现一个棘手的情况，如下所示::

        from datetime import datetime


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }
            start_date: Mapped[datetime] = mapped_column(nullable=True)


        class Manager(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }
            start_date: Mapped[datetime] = mapped_column(nullable=True)

    在上面， ``Engineer`` 和 ``Manager`` 上声明的 ``start_date`` 列将导致一个错误：

    .. sourcecode:: text

        sqlalchemy.exc.ArgumentError: Column 'start_date' on class Manager conflicts
        with existing column 'employee.start_date'.  If using Declarative,
        consider using the use_existing_column parameter of mapped_column() to
        resolve conflicts.

    上述场景为声明式映射系统带来了一个模棱两可的问题，可以通过在 :func:`_orm.mapped_column` 上使用 :paramref:`_orm.mapped_column.use_existing_column` 参数来解决，该参数指示 :func:`_orm.mapped_column` 查看继承的超类并使用已经映射的列（如果存在），否则映射一个新列::

        from sqlalchemy import DateTime


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )


        class Manager(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )

    在上面，当 ``Manager`` 被映射时， ``start_date`` 列已经存在于 ``Employee`` 类上，因为它已经由 ``Engineer`` 映射提供。:paramref:`_orm.mapped_column.use_existing_column` 参数指示 :func:`_orm.mapped_column` 它应该首先在 ``Employee`` 的映射 :class:`.Table` 上查找请求的 :class:`_schema.Column` ，如果存在，则保持现有映射。如果不存在，:func:`_orm.mapped_column` 将正常映射该列，将其添加为 ``Employee`` 超类引用的 :class:`.Table` 的列之一。

    .. versionadded:: 2.0.0b4 
        
        - 添加 :paramref:`_orm.mapped_column.use_existing_column`，提供了一种 2.0 兼容的方法，用于有条件地映射继承子类上的列。之前的方法结合了 :class:`.declared_attr` 和对父类 ``.__table__`` 的查找，仍然可以正常工作，但缺乏 :pep:`484` 的类型支持。

    类似的概念可以与混入类（参见 :ref:`orm_mixins_toplevel`）一起使用，以定义特定系列的列和/或来自可重用混入类的其他映射属性::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": type,
                "polymorphic_identity": "employee",
            }


        class HasStartDate:
            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )


        class Engineer(HasStartDate, Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(HasStartDate, Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

.. tab:: 英文

    Note in the previous section that the ``manager_name`` and ``engineer_info`` columns
    are "moved up" to be applied to ``Employee.__table__``, as a result of their
    declaration on a subclass that has no table of its own.   A tricky case
    comes up when two subclasses want to specify *the same* column, as below::

        from datetime import datetime


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }
            start_date: Mapped[datetime] = mapped_column(nullable=True)


        class Manager(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }
            start_date: Mapped[datetime] = mapped_column(nullable=True)

    Above, the ``start_date`` column declared on both ``Engineer`` and ``Manager``
    will result in an error:

    .. sourcecode:: text


        sqlalchemy.exc.ArgumentError: Column 'start_date' on class Manager conflicts
        with existing column 'employee.start_date'.  If using Declarative,
        consider using the use_existing_column parameter of mapped_column() to
        resolve conflicts.

    The above scenario presents an ambiguity to the Declarative mapping system that
    may be resolved by using the :paramref:`_orm.mapped_column.use_existing_column`
    parameter on :func:`_orm.mapped_column`, which instructs :func:`_orm.mapped_column`
    to look on the inheriting superclass present and use the column that's already
    mapped, if already present, else to map a new column::


        from sqlalchemy import DateTime


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )


        class Manager(Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )

    Above, when ``Manager`` is mapped, the ``start_date`` column is
    already present on the ``Employee`` class, having been provided by the
    ``Engineer`` mapping already.   The :paramref:`_orm.mapped_column.use_existing_column`
    parameter indicates to :func:`_orm.mapped_column` that it should look for the
    requested :class:`_schema.Column` on the mapped :class:`.Table` for
    ``Employee`` first, and if present, maintain that existing mapping.  If not
    present, :func:`_orm.mapped_column` will map the column normally, adding it
    as one of the columns in the :class:`.Table` referenced by the
    ``Employee`` superclass.


    .. versionadded:: 2.0.0b4 - Added :paramref:`_orm.mapped_column.use_existing_column`,
    which provides a 2.0-compatible means of mapping a column on an inheriting
    subclass conditionally.  The previous approach which combines
    :class:`.declared_attr` with a lookup on the parent ``.__table__``
    continues to function as well, but lacks :pep:`484` typing support.


    A similar concept can be used with mixin classes (see :ref:`orm_mixins_toplevel`)
    to define a particular series of columns and/or other mapped attributes
    from a reusable mixin class::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": type,
                "polymorphic_identity": "employee",
            }


        class HasStartDate:
            start_date: Mapped[datetime] = mapped_column(
                nullable=True, use_existing_column=True
            )


        class Engineer(HasStartDate, Employee):
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }


        class Manager(HasStartDate, Employee):
            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }

具有单表继承的关系
+++++++++++++++++++++++++++++++++++++++++++

Relationships with Single Table Inheritance

.. tab:: 中文

    单表继承的关系完全支持。其配置方式与连接继承的相同；外键属性应位于关系的“外键(foreign)”端的同一个类上::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            employees: Mapped[List[Employee]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            manager_data: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    同样，如连接继承的情况一样，我们可以创建涉及特定子类的关系。查询时，SELECT 语句将包括一个 WHERE 子句，该子句将类选择限制为该子类或子类::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            managers: Mapped[List[Manager]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            manager_name: Mapped[str] = mapped_column(nullable=True)

            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="managers")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    在上面， ``Manager`` 类将具有 ``Manager.company`` 属性； ``Company`` 将具有 ``Company.managers`` 属性，该属性始终加载 ``employee`` 并带有附加的 WHERE 子句，将行限制为 ``type = 'manager'`` 的那些行。

.. tab:: 英文

    Relationships are fully supported with single table inheritance.   Configuration
    is done in the same manner as that of joined inheritance; a foreign key
    attribute should be on the same class that's the "foreign" side of the
    relationship::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            employees: Mapped[List[Employee]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            manager_data: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    Also, like the case of joined inheritance, we can create relationships
    that involve a specific subclass.   When queried, the SELECT statement will
    include a WHERE clause that limits the class selection to that subclass
    or subclasses::

        class Company(Base):
            __tablename__ = "company"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            managers: Mapped[List[Manager]] = relationship(back_populates="company")


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Manager(Employee):
            manager_name: Mapped[str] = mapped_column(nullable=True)

            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))
            company: Mapped[Company] = relationship(back_populates="managers")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
            }


        class Engineer(Employee):
            engineer_info: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
            }

    Above, the ``Manager`` class will have a ``Manager.company`` attribute;
    ``Company`` will have a ``Company.managers`` attribute that always
    loads against the ``employee`` with an additional WHERE clause that
    limits rows to those with ``type = 'manager'``.

.. _orm_inheritance_abstract_poly:

使用 ``polymorphic_abstract`` 构建更深层次的层次结构
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Building Deeper Hierarchies with ``polymorphic_abstract``

.. tab:: 中文

    .. versionadded:: 2.0

    在构建任何类型的继承层次结构时，映射类可以包含 :paramref:`_orm.Mapper.polymorphic_abstract` 参数设置为 ``True``，这表明该类应正常映射，但不期望直接实例化，并且不包括 :paramref:`_orm.Mapper.polymorphic_identity`。然后可以将子类声明为该映射类的子类，这些子类本身可以包含 :paramref:`_orm.Mapper.polymorphic_identity`，因此可以正常使用。这允许通过一个在层次结构中被认为是“抽象”的公共基类一次引用一系列子类，在查询以及在 :func:`_orm.relationship` 声明中都是如此。这种用法与在声明式中使用 :ref:`declarative_abstract` 属性不同，后者将目标类完全取消映射，因此不能作为映射类本身使用。:paramref:`_orm.Mapper.polymorphic_abstract` 可以应用于层次结构中的任何类或类，包括一次在多个层次上。

    例如，假设 ``Manager`` 和 ``Principal`` 都被归类到超类 ``Executive``，而 ``Engineer`` 和 ``Sysadmin`` 被归类到超类 ``Technologist``。 ``Executive`` 或 ``Technologist`` 都不会被实例化，因此没有 :paramref:`_orm.Mapper.polymorphic_identity`。这些类可以使用 :paramref:`_orm.Mapper.polymorphic_abstract` 配置如下::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Executive(Employee):
            """公司的高管"""

            executive_background: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {"polymorphic_abstract": True}


        class Technologist(Employee):
            """从事技术工作的员工"""

            competencies: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {"polymorphic_abstract": True}


        class Manager(Executive):
            """经理"""

            __mapper_args__ = {"polymorphic_identity": "manager"}


        class Principal(Executive):
            """公司的负责人"""

            __mapper_args__ = {"polymorphic_identity": "principal"}


        class Engineer(Technologist):
            """工程师"""

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class SysAdmin(Technologist):
            """系统管理员"""

            __mapper_args__ = {"polymorphic_identity": "sysadmin"}

    在上面的示例中，新的类 ``Technologist`` 和 ``Executive`` 是普通的映射类，并且还指示添加到超类的新列 ``executive_background`` 和 ``competencies``。但是，它们都没有设置 :paramref:`_orm.Mapper.polymorphic_identity`；这是因为不期望直接实例化 ``Technologist`` 或 ``Executive``；我们总是会有 ``Manager``、 ``Principal``、 ``Engineer`` 或 ``SysAdmin`` 中的一个。但是，我们可以查询 ``Principal`` 和 ``Technologist`` 角色，并且可以将它们作为 :func:`_orm.relationship` 的目标。下面的示例演示了针对 ``Technologist`` 对象的 SELECT 语句：

    .. sourcecode:: python+sql

        session.scalars(select(Technologist)).all()
        {execsql}
        SELECT employee.id, employee.name, employee.type, employee.competencies
        FROM employee
        WHERE employee.type IN (?, ?)
        [...] ('engineer', 'sysadmin')

    ``Technologist`` 和 ``Executive`` 抽象映射类也可以作为 :func:`_orm.relationship` 映射的目标，像任何其他映射类一样。我们可以扩展上面的示例以包含 ``Company``，具有单独的集合 ``Company.technologists`` 和 ``Company.principals``::

        class Company(Base):
            __tablename__ = "company"
            id = Column(Integer, primary_key=True)

            executives: Mapped[List[Executive]] = relationship()
            technologists: Mapped[List[Technologist]] = relationship()


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)

            # 外键到 "company.id" 被添加
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))

            # 映射的其余部分相同
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
            }


        # 之前示例中的 Executive、Technologist、Manager、Principal、Engineer、SysAdmin 类在此不变

    使用上述映射，我们可以分别跨 ``Company.technologists`` 和 ``Company.executives`` 使用连接和关系加载技术：

    .. sourcecode:: python+sql

        session.scalars(
            select(Company)
            .join(Company.technologists)
            .where(Technologist.competency.ilike("%java%"))
            .options(selectinload(Company.executives))
        ).all()
        {execsql}
        SELECT company.id
        FROM company JOIN employee ON company.id = employee.company_id AND employee.type IN (?, ?)
        WHERE lower(employee.competencies) LIKE lower(?)
        [...] ('engineer', 'sysadmin', '%java%')

        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type,
        employee.executive_background AS employee_executive_background
        FROM employee
        WHERE employee.company_id IN (?) AND employee.type IN (?, ?)
        [...] (1, 'manager', 'principal')

    .. seealso::

        :ref:`declarative_abstract` - 声明式参数，允许声明式类在层次结构中完全取消映射，同时仍然从映射超类扩展。

.. tab:: 英文

    .. versionadded:: 2.0

    When building any kind of inheritance hierarchy, a mapped class may include the
    :paramref:`_orm.Mapper.polymorphic_abstract` parameter set to ``True``, which
    indicates that the class should be mapped normally, however would not expect to
    be instantiated directly and would not include a
    :paramref:`_orm.Mapper.polymorphic_identity`. Subclasses may then be declared
    as subclasses of this mapped class, which themselves can include a
    :paramref:`_orm.Mapper.polymorphic_identity` and therefore be used normally.
    This allows a series of subclasses to be referenced at once by a common base
    class which is considered to be "abstract" within the hierarchy, both in
    queries as well as in :func:`_orm.relationship` declarations. This use differs
    from the use of the :ref:`declarative_abstract` attribute with Declarative,
    which leaves the target class entirely unmapped and thus not usable as a mapped
    class by itself. :paramref:`_orm.Mapper.polymorphic_abstract` may be applied to
    any class or classes at any level in the hierarchy, including on multiple
    levels at once.

    As an example, suppose ``Manager`` and ``Principal`` were both to be classified
    against a superclass ``Executive``, and ``Engineer`` and ``Sysadmin`` were
    classified against a superclass ``Technologist``. Neither ``Executive`` or
    ``Technologist`` is ever instantiated, therefore have no
    :paramref:`_orm.Mapper.polymorphic_identity`. These classes can be configured
    using :paramref:`_orm.Mapper.polymorphic_abstract` as follows::

        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "polymorphic_on": "type",
            }


        class Executive(Employee):
            """An executive of the company"""

            executive_background: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {"polymorphic_abstract": True}


        class Technologist(Employee):
            """An employee who works with technology"""

            competencies: Mapped[str] = mapped_column(nullable=True)

            __mapper_args__ = {"polymorphic_abstract": True}


        class Manager(Executive):
            """a manager"""

            __mapper_args__ = {"polymorphic_identity": "manager"}


        class Principal(Executive):
            """a principal of the company"""

            __mapper_args__ = {"polymorphic_identity": "principal"}


        class Engineer(Technologist):
            """an engineer"""

            __mapper_args__ = {"polymorphic_identity": "engineer"}


        class SysAdmin(Technologist):
            """a systems administrator"""

            __mapper_args__ = {"polymorphic_identity": "sysadmin"}

    In the above example, the new classes ``Technologist`` and ``Executive``
    are ordinary mapped classes, and also indicate new columns to be added to the
    superclass called ``executive_background`` and ``competencies``.   However,
    they both lack a setting for :paramref:`_orm.Mapper.polymorphic_identity`;
    this is because it's not expected that ``Technologist`` or ``Executive`` would
    ever be instantiated directly; we'd always have one of ``Manager``, ``Principal``,
    ``Engineer`` or ``SysAdmin``.   We can however query for
    ``Principal`` and ``Technologist`` roles, as well as have them be targets
    of :func:`_orm.relationship`.  The example below demonstrates a SELECT
    statement for ``Technologist`` objects:


    .. sourcecode:: python+sql

        session.scalars(select(Technologist)).all()
        {execsql}
        SELECT employee.id, employee.name, employee.type, employee.competencies
        FROM employee
        WHERE employee.type IN (?, ?)
        [...] ('engineer', 'sysadmin')

    The ``Technologist`` and ``Executive`` abstract mapped classes may also be
    made the targets of :func:`_orm.relationship` mappings, like any other
    mapped class.  We can extend the above example to include ``Company``,
    with separate collections ``Company.technologists`` and ``Company.principals``::

        class Company(Base):
            __tablename__ = "company"
            id = Column(Integer, primary_key=True)

            executives: Mapped[List[Executive]] = relationship()
            technologists: Mapped[List[Technologist]] = relationship()


        class Employee(Base):
            __tablename__ = "employee"
            id: Mapped[int] = mapped_column(primary_key=True)

            # foreign key to "company.id" is added
            company_id: Mapped[int] = mapped_column(ForeignKey("company.id"))

            # rest of mapping is the same
            name: Mapped[str]
            type: Mapped[str]

            __mapper_args__ = {
                "polymorphic_on": "type",
            }


        # Executive, Technologist, Manager, Principal, Engineer, SysAdmin
        # classes from previous example would follow here unchanged

    Using the above mapping we can use joins and relationship loading techniques
    across ``Company.technologists`` and ``Company.executives`` individually:

    .. sourcecode:: python+sql

        session.scalars(
            select(Company)
            .join(Company.technologists)
            .where(Technologist.competency.ilike("%java%"))
            .options(selectinload(Company.executives))
        ).all()
        {execsql}
        SELECT company.id
        FROM company JOIN employee ON company.id = employee.company_id AND employee.type IN (?, ?)
        WHERE lower(employee.competencies) LIKE lower(?)
        [...] ('engineer', 'sysadmin', '%java%')

        SELECT employee.company_id AS employee_company_id, employee.id AS employee_id,
        employee.name AS employee_name, employee.type AS employee_type,
        employee.executive_background AS employee_executive_background
        FROM employee
        WHERE employee.company_id IN (?) AND employee.type IN (?, ?)
        [...] (1, 'manager', 'principal')



    .. seealso::

        :ref:`declarative_abstract` - Declarative parameter which allows a
        Declarative class to be completely un-mapped within a hierarchy, while
        still extending from a mapped superclass.


加载单继承映射
+++++++++++++++++++++++++++++++++++

Loading Single Inheritance Mappings

.. tab:: 中文

    单表继承的加载技术与连接表继承的加载技术几乎相同，并且在这两种映射类型之间提供了高度的抽象，使得在它们之间切换以及在单个层次结构中将它们混合变得容易（只需省略单继承子类的 ``__tablename__``）。有关继承加载技术的文档，请参阅 :ref:`inheritance_loading_toplevel` 和 :ref:`loading_single_inheritance` 部分，包括在映射器配置时以及查询时配置类进行查询。

.. tab:: 英文

    The loading techniques for single-table inheritance are mostly identical to
    those used for joined-table inheritance, and a high degree of abstraction is
    provided between these two mapping types such that it is easy to switch between
    them as well as to intermix them in a single hierarchy (just omit
    ``__tablename__`` from whichever subclasses are to be single-inheriting). See
    the sections :ref:`inheritance_loading_toplevel` and
    :ref:`loading_single_inheritance` for documentation on inheritance loading
    techniques, including configuration of classes to be queried both at mapper
    configuration time as well as query time.

.. _concrete_inheritance:

具体表继承
--------------------------

Concrete Table Inheritance

.. tab:: 中文

    具体继承将每个子类映射到其自己的独立表，每个表包含生成该类实例所需的所有列。默认情况下，具体继承配置非多态查询；查询特定类将仅查询该类的表并仅返回该类的实例。通过在映射器中配置一个特殊的 SELECT 来启用具体类的多态加载，该 SELECT 通常由所有表的 UNION 生成。

    .. warning::

        具体表继承比连接表继承或单表继承 **复杂得多**，并且在功能上 **受限得多**，特别是涉及与关系、急切加载和多态加载一起使用时。当以多态方式使用时，它会生成 **非常大的查询**，使用 UNIONS 其性能不如简单的连接。如果需要关系加载和多态加载的灵活性，强烈建议尽可能使用连接表继承或单表继承。如果不需要多态加载，那么如果每个类完全引用自己的表，则可以使用普通的非继承映射。

    尽管连接和单表继承在“多态(polymorphic)”加载方面很流畅，但在具体继承中则更加尴尬。因此，当 **不需要多态加载** 时，具体继承更为合适。建立涉及具体继承类的关系也更加尴尬。

    要将类设置为使用具体继承，请在 ``__mapper_args__`` 中添加 :paramref:`_orm.Mapper.concrete` 参数。这表明声明式以及映射，超类表不应被视为映射的一部分::

        class Employee(Base):
            __tablename__ = "employee"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))


        class Manager(Employee):
            __tablename__ = "manager"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(50))

            __mapper_args__ = {
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(50))

            __mapper_args__ = {
                "concrete": True,
            }

    需要注意两个关键点：

    * 我们必须在每个子类上 **显式定义所有列**，即使是同名列。诸如 ``Employee.name`` 之类的列 **不会** 自动复制到 ``Manager`` 或 ``Engineer`` 映射的表中。

    * 虽然 ``Engineer`` 和 ``Manager`` 类在与 ``Employee`` 的继承关系中映射，但它们仍然 **不包括多态加载**。这意味着，如果我们查询 ``Employee`` 对象，则根本不会查询 ``manager`` 和 ``engineer`` 表。

.. tab:: 英文

    Concrete inheritance maps each subclass to its own distinct table, each
    of which contains all columns necessary to produce an instance of that class.
    A concrete inheritance configuration by default queries non-polymorphically;
    a query for a particular class will only query that class' table
    and only return instances of that class.  Polymorphic loading of concrete
    classes is enabled by configuring within the mapper
    a special SELECT that typically is produced as a UNION of all the tables.

    .. warning::

        Concrete table inheritance is **much more complicated** than joined
        or single table inheritance, and is **much more limited in functionality**
        especially pertaining to using it with relationships, eager loading,
        and polymorphic loading.  When used polymorphically it produces
        **very large queries** with UNIONS that won't perform as well as simple
        joins.  It is strongly advised that if flexibility in relationship loading
        and polymorphic loading is required, that joined or single table inheritance
        be used if at all possible.   If polymorphic loading isn't required, then
        plain non-inheriting mappings can be used if each class refers to its
        own table completely.

    Whereas joined and single table inheritance are fluent in "polymorphic"
    loading, it is a more awkward affair in concrete inheritance.  For this
    reason, concrete inheritance is more appropriate when **polymorphic loading
    is not required**.   Establishing relationships that involve concrete inheritance
    classes is also more awkward.

    To establish a class as using concrete inheritance, add the
    :paramref:`_orm.Mapper.concrete` parameter within the ``__mapper_args__``.
    This indicates to Declarative as well as the mapping that the superclass
    table should not be considered as part of the mapping::

        class Employee(Base):
            __tablename__ = "employee"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))


        class Manager(Employee):
            __tablename__ = "manager"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(50))

            __mapper_args__ = {
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(50))

            __mapper_args__ = {
                "concrete": True,
            }

    Two critical points should be noted:

    * We must **define all columns explicitly** on each subclass, even those of
      the same name.  A column such as
      ``Employee.name`` here is **not** copied out to the tables mapped
      by ``Manager`` or ``Engineer`` for us.

    * while the ``Engineer`` and ``Manager`` classes are
      mapped in an inheritance relationship with ``Employee``, they still **do not
      include polymorphic loading**.  Meaning, if we query for ``Employee``
      objects, the ``manager`` and ``engineer`` tables are not queried at all.

.. _concrete_polymorphic:

具体多态加载配置
++++++++++++++++++++++++++++++++++++++++++

Concrete Polymorphic Loading Configuration

.. tab:: 中文

    使用具体继承进行多态加载需要针对每个应该具有多态加载的基类配置一个特殊的 SELECT。这个 SELECT 需要能够单独访问所有映射的表，通常是一个使用 SQLAlchemy 辅助函数 :func:`.polymorphic_union` 构造的 UNION 语句。

    如 :ref:`inheritance_loading_toplevel` 中讨论的，任何类型的映射继承配置都可以配置为默认从特殊的可选项加载，使用 :paramref:`_orm.Mapper.with_polymorphic` 参数。当前的公共 API 要求在首次构建 :class:`_orm.Mapper` 时设置此参数。

    然而，在声明式的情况下，映射器和映射的 :class:`_schema.Table` 是在定义映射类时同时创建的。这意味着 :paramref:`_orm.Mapper.with_polymorphic` 参数还不能提供，因为与子类对应的 :class:`_schema.Table` 对象尚未定义。

    有几种策略可以解决这个循环问题，但是声明式提供了辅助类 :class:`.ConcreteBase` 和 :class:`.AbstractConcreteBase`，它们在幕后处理这个问题。

    使用 :class:`.ConcreteBase`，我们可以几乎以与其他形式的继承映射相同的方式设置我们的具体映射::

        from sqlalchemy.ext.declarative import ConcreteBase
        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    在上面，声明式在映射器“初始化”时为 ``Employee`` 类设置多态可选项；这是解析其他依赖映射器的映射器后期配置步骤。:class:`.ConcreteBase` 辅助类使用 :func:`.polymorphic_union` 函数在设置所有其他类后创建所有具体映射表的 UNION，然后使用已经存在的基类映射器配置这个语句。

    在选择时，多态联合生成如下查询：

    .. sourcecode:: python+sql

        session.scalars(select(Employee)).all()
        {execsql}
        SELECT
            pjoin.id,
            pjoin.name,
            pjoin.type,
            pjoin.manager_data,
            pjoin.engineer_info
        FROM (
            SELECT
                employee.id AS id,
                employee.name AS name,
                CAST(NULL AS VARCHAR(40)) AS manager_data,
                CAST(NULL AS VARCHAR(40)) AS engineer_info,
                'employee' AS type
            FROM employee
            UNION ALL
            SELECT
                manager.id AS id,
                manager.name AS name,
                manager.manager_data AS manager_data,
                CAST(NULL AS VARCHAR(40)) AS engineer_info,
                'manager' AS type
            FROM manager
            UNION ALL
            SELECT
                engineer.id AS id,
                engineer.name AS name,
                CAST(NULL AS VARCHAR(40)) AS manager_data,
                engineer.engineer_info AS engineer_info,
                'engineer' AS type
            FROM engineer
        ) AS pjoin

    上述 UNION 查询需要为每个子表制造“NULL”列，以适应那些不属于特定子类的列。

    .. seealso::

        :class:`.ConcreteBase`

.. tab:: 英文

    Polymorphic loading with concrete inheritance requires that a specialized
    SELECT is configured against each base class that should have polymorphic
    loading.  This SELECT needs to be capable of accessing all the
    mapped tables individually, and is typically a UNION statement that is
    constructed using a SQLAlchemy helper :func:`.polymorphic_union`.

    As discussed in :ref:`inheritance_loading_toplevel`, mapper inheritance
    configurations of any type can be configured to load from a special selectable
    by default using the :paramref:`_orm.Mapper.with_polymorphic` argument.  Current
    public API requires that this argument is set on a :class:`_orm.Mapper` when
    it is first constructed.

    However, in the case of Declarative, both the mapper and the :class:`_schema.Table`
    that is mapped are created at once, the moment the mapped class is defined.
    This means that the :paramref:`_orm.Mapper.with_polymorphic` argument cannot
    be provided yet, since the :class:`_schema.Table` objects that correspond to the
    subclasses haven't yet been defined.

    There are a few strategies available to resolve this cycle, however
    Declarative provides helper classes :class:`.ConcreteBase` and
    :class:`.AbstractConcreteBase` which handle this issue behind the scenes.

    Using :class:`.ConcreteBase`, we can set up our concrete mapping in
    almost the same way as we do other forms of inheritance mappings::

        from sqlalchemy.ext.declarative import ConcreteBase
        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    Above, Declarative sets up the polymorphic selectable for the
    ``Employee`` class at mapper "initialization" time; this is the late-configuration
    step for mappers that resolves other dependent mappers.  The :class:`.ConcreteBase`
    helper uses the
    :func:`.polymorphic_union` function to create a UNION of all concrete-mapped
    tables after all the other classes are set up, and then configures this statement
    with the already existing base-class mapper.

    Upon select, the polymorphic union produces a query like this:

    .. sourcecode:: python+sql

        session.scalars(select(Employee)).all()
        {execsql}
        SELECT
            pjoin.id,
            pjoin.name,
            pjoin.type,
            pjoin.manager_data,
            pjoin.engineer_info
        FROM (
            SELECT
                employee.id AS id,
                employee.name AS name,
                CAST(NULL AS VARCHAR(40)) AS manager_data,
                CAST(NULL AS VARCHAR(40)) AS engineer_info,
                'employee' AS type
            FROM employee
            UNION ALL
            SELECT
                manager.id AS id,
                manager.name AS name,
                manager.manager_data AS manager_data,
                CAST(NULL AS VARCHAR(40)) AS engineer_info,
                'manager' AS type
            FROM manager
            UNION ALL
            SELECT
                engineer.id AS id,
                engineer.name AS name,
                CAST(NULL AS VARCHAR(40)) AS manager_data,
                engineer.engineer_info AS engineer_info,
                'engineer' AS type
            FROM engineer
        ) AS pjoin

    The above UNION query needs to manufacture "NULL" columns for each subtable
    in order to accommodate for those columns that aren't members of that
    particular subclass.

    .. seealso::

        :class:`.ConcreteBase`

.. _abstract_concrete_base:

抽象具体类
+++++++++++++++++++++++++

Abstract Concrete Classes

.. tab:: 中文

    目前为止展示的具体映射显示了子类和基类映射到单独的表中。在具体继承的用例中，基类通常不在数据库中表示，只有子类。换句话说，基类是“抽象”的。

    通常，当我们想将两个不同的子类映射到单独的表，并将基类保留为未映射时，这可以非常容易地实现。在使用声明式时，只需使用 ``__abstract__`` 指示符声明基类::

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(Base):
            __abstract__ = True


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

    在上面，我们实际上没有使用 SQLAlchemy 的继承映射功能；我们可以正常加载和持久化 ``Manager`` 和 ``Engineer`` 实例。然而，当我们需要 **多态查询(query polymorphically)** 时，即我们想发出 ``select(Employee)`` 并返回 ``Manager`` 和 ``Engineer`` 实例的集合时，情况发生了变化。这将我们带回具体继承的领域，我们必须针对 ``Employee`` 构建一个特殊的映射器才能实现这一点。

    要修改我们的具体继承示例以说明能够进行多态加载的“抽象”基类，我们将只有一个 ``engineer`` 和一个 ``manager`` 表，没有 ``employee`` 表，但是 ``Employee`` 映射器将直接映射到“多态联合”，而不是在 :paramref:`_orm.Mapper.with_polymorphic` 参数中本地指定。

    为此，声明式提供了一个 :class:`.ConcreteBase` 类的变体，称为 :class:`.AbstractConcreteBase`，它在幕后自动实现这一点::

        from sqlalchemy.ext.declarative import AbstractConcreteBase
        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(AbstractConcreteBase, Base):
            strict_attrs = True

            name = mapped_column(String(50))


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        Base.registry.configure()

    在上面，调用 :meth:`_orm.registry.configure` 方法，这将触发 ``Employee`` 类实际映射；在配置步骤之前，该类没有映射，因为它将查询的子表尚未定义。这个过程比 :class:`.ConcreteBase` 更复杂，因为必须延迟基类的整个映射，直到声明了所有子类。使用上述映射，只能持久化 ``Manager`` 和 ``Engineer`` 的实例；针对 ``Employee`` 类的查询将始终生成 ``Manager`` 和 ``Engineer`` 对象。

    使用上述映射，可以根据 ``Employee`` 类和在其上本地声明的任何属性生成查询，例如 ``Employee.name``：

    .. sourcecode:: pycon+sql

        >>> stmt = select(Employee).where(Employee.name == "n1")
        >>> print(stmt)
        {printsql}SELECT pjoin.id, pjoin.name, pjoin.type, pjoin.manager_data, pjoin.engineer_info
        FROM (
        SELECT engineer.id AS id, engineer.name AS name, engineer.engineer_info AS engineer_info,
        CAST(NULL AS VARCHAR(40)) AS manager_data, 'engineer' AS type
        FROM engineer
        UNION ALL
        SELECT manager.id AS id, manager.name AS name, CAST(NULL AS VARCHAR(40)) AS engineer_info,
        manager.manager_data AS manager_data, 'manager' AS type
        FROM manager
        ) AS pjoin
        WHERE pjoin.name = :name_1

    :param:`.AbstractConcreteBase.strict_attrs` 参数表明 ``Employee`` 类应直接映射仅属于 ``Employee`` 类的那些属性，在本例中是 ``Employee.name`` 属性。其他属性如 ``Manager.manager_data`` 和 ``Engineer.engineer_info`` 仅存在于其对应的子类上。当 :paramref:`.AbstractConcreteBase.strict_attrs` 未设置时，所有子类属性如 ``Manager.manager_data`` 和 ``Engineer.engineer_info`` 都会映射到基 ``Employee`` 类上。这是一个遗留的使用模式，可能在查询时更方便，但会导致所有子类共享整个层次结构的完整属性集；在上面的示例中，不使用 :paramref:`.AbstractConcreteBase.strict_attrs` 会导致生成无用的 ``Engineer.manager_name`` 和 ``Manager.engineer_info`` 属性。

    .. versionadded:: 2.0  
        
        添加了 :paramref:`.AbstractConcreteBase.strict_attrs` 参数到 :class:`.AbstractConcreteBase`，它生成更清晰的映射；默认值为 False，以允许遗留映射继续按 1.x 版本的方式工作。

.. tab:: 英文

    The concrete mappings illustrated thus far show both the subclasses as well
    as the base class mapped to individual tables.   In the concrete inheritance
    use case, it is common that the base class is not represented within the
    database, only the subclasses.  In other words, the base class is
    "abstract".

    Normally, when one would like to map two different subclasses to individual
    tables, and leave the base class unmapped, this can be achieved very easily.
    When using Declarative, just declare the
    base class with the ``__abstract__`` indicator::

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(Base):
            __abstract__ = True


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

    Above, we are not actually making use of SQLAlchemy's inheritance mapping
    facilities; we can load and persist instances of ``Manager`` and ``Engineer``
    normally.   The situation changes however when we need to **query polymorphically**,
    that is, we'd like to emit ``select(Employee)`` and get back a collection
    of ``Manager`` and ``Engineer`` instances.    This brings us back into the
    domain of concrete inheritance, and we must build a special mapper against
    ``Employee`` in order to achieve this.

    To modify our concrete inheritance example to illustrate an "abstract" base
    that is capable of polymorphic loading,
    we will have only an ``engineer`` and a ``manager`` table and no ``employee``
    table, however the ``Employee`` mapper will be mapped directly to the
    "polymorphic union", rather than specifying it locally to the
    :paramref:`_orm.Mapper.with_polymorphic` parameter.

    To help with this, Declarative offers a variant of the :class:`.ConcreteBase`
    class called :class:`.AbstractConcreteBase` which achieves this automatically::

        from sqlalchemy.ext.declarative import AbstractConcreteBase
        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass


        class Employee(AbstractConcreteBase, Base):
            strict_attrs = True

            name = mapped_column(String(50))


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        Base.registry.configure()

    Above, the :meth:`_orm.registry.configure` method is invoked, which will
    trigger the ``Employee`` class to be actually mapped; before the configuration
    step, the class has no mapping as the sub-tables which it will query from
    have not yet been defined.   This process is more complex than that of
    :class:`.ConcreteBase`, in that the entire mapping
    of the base class must be delayed until all the subclasses have been declared.
    With a mapping like the above, only instances of ``Manager`` and ``Engineer``
    may be persisted; querying against the ``Employee`` class will always produce
    ``Manager`` and ``Engineer`` objects.

    Using the above mapping, queries can be produced in terms of the ``Employee``
    class and any attributes that are locally declared upon it, such as the
    ``Employee.name``:

    .. sourcecode:: pycon+sql

        >>> stmt = select(Employee).where(Employee.name == "n1")
        >>> print(stmt)
        {printsql}SELECT pjoin.id, pjoin.name, pjoin.type, pjoin.manager_data, pjoin.engineer_info
        FROM (
        SELECT engineer.id AS id, engineer.name AS name, engineer.engineer_info AS engineer_info,
        CAST(NULL AS VARCHAR(40)) AS manager_data, 'engineer' AS type
        FROM engineer
        UNION ALL
        SELECT manager.id AS id, manager.name AS name, CAST(NULL AS VARCHAR(40)) AS engineer_info,
        manager.manager_data AS manager_data, 'manager' AS type
        FROM manager
        ) AS pjoin
        WHERE pjoin.name = :name_1

    The :paramref:`.AbstractConcreteBase.strict_attrs` parameter indicates that the
    ``Employee`` class should directly map only those attributes which are local to
    the ``Employee`` class, in this case the ``Employee.name`` attribute. Other
    attributes such as ``Manager.manager_data`` and ``Engineer.engineer_info`` are
    present only on their corresponding subclass.
    When :paramref:`.AbstractConcreteBase.strict_attrs`
    is not set, then all subclass attributes such as ``Manager.manager_data`` and
    ``Engineer.engineer_info`` get mapped onto the base ``Employee`` class.  This
    is a legacy mode of use which may be more convenient for querying but has the
    effect that all subclasses share the
    full set of attributes for the whole hierarchy; in the above example, not
    using :paramref:`.AbstractConcreteBase.strict_attrs` would have the effect
    of generating non-useful ``Engineer.manager_name`` and ``Manager.engineer_info``
    attributes.

    .. versionadded:: 2.0  
        
        Added :paramref:`.AbstractConcreteBase.strict_attrs`
        parameter to :class:`.AbstractConcreteBase` which produces a cleaner
        mapping; the default is False to allow legacy mappings to continue working
        as they did in 1.x versions.



.. seealso::

    :class:`.AbstractConcreteBase`


经典和半经典具体多态配置
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Classical and Semi-Classical Concrete Polymorphic Configuration

.. tab:: 中文

    声明式配置中展示的 :class:`.ConcreteBase` 和 :class:`.AbstractConcreteBase` 等价于两种其他形式的配置，它们显式地使用 :func:`.polymorphic_union`。这些配置形式显式使用 :class:`_schema.Table` 对象，以便首先创建“多态联合(polymorphic union)”，然后应用于映射。这里展示这些配置形式以澄清 :func:`.polymorphic_union` 函数在映射中的作用。

    例如， **半经典映射(semi-classical mapping)** 使用声明式，但单独建立 :class:`_schema.Table` 对象::

        metadata_obj = Base.metadata

        employees_table = Table(
            "employee",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )

        managers_table = Table(
            "manager",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("manager_data", String(50)),
        )

        engineers_table = Table(
            "engineer",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("engineer_info", String(50)),
        )

    接下来，使用 :func:`.polymorphic_union` 生成 UNION::

        from sqlalchemy.orm import polymorphic_union

        pjoin = polymorphic_union(
            {
                "employee": employees_table,
                "manager": managers_table,
                "engineer": engineers_table,
            },
            "type",
            "pjoin",
        )

    使用上述 :class:`_schema.Table` 对象，可以使用“半经典”风格生成映射，其中我们将声明式与 ``__table__`` 参数结合使用；我们通过 ``__mapper_args__`` 将上述多态联合传递给 :paramref:`_orm.Mapper.with_polymorphic` 参数::

        class Employee(Base):
            __table__ = employees_table
            __mapper_args__ = {
                "polymorphic_on": pjoin.c.type,
                "with_polymorphic": ("*", pjoin),
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __table__ = engineers_table
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        class Manager(Employee):
            __table__ = managers_table
            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }

    或者，可以在完全“经典”风格中使用相同的 :class:`_schema.Table` 对象，而不使用声明式。一个类似于由声明式提供的构造函数如下所示::

        class Employee:
            def __init__(self, **kw):
                for k in kw:
                    setattr(self, k, kw[k])


        class Manager(Employee):
            pass


        class Engineer(Employee):
            pass


        employee_mapper = mapper_registry.map_imperatively(
            Employee,
            pjoin,
            with_polymorphic=("*", pjoin),
            polymorphic_on=pjoin.c.type,
        )
        manager_mapper = mapper_registry.map_imperatively(
            Manager,
            managers_table,
            inherits=employee_mapper,
            concrete=True,
            polymorphic_identity="manager",
        )
        engineer_mapper = mapper_registry.map_imperatively(
            Engineer,
            engineers_table,
            inherits=employee_mapper,
            concrete=True,
            polymorphic_identity="engineer",
        )

    “抽象”示例也可以使用“半经典”或“经典”风格进行映射。不同之处在于，我们将“多态联合”直接应用为基映射器上的映射可选项，而不是将其应用于 :paramref:`_orm.Mapper.with_polymorphic` 参数。本节展示了“半经典”映射::

        from sqlalchemy.orm import polymorphic_union

        pjoin = polymorphic_union(
            {
                "manager": managers_table,
                "engineer": engineers_table,
            },
            "type",
            "pjoin",
        )


        class Employee(Base):
            __table__ = pjoin
            __mapper_args__ = {
                "polymorphic_on": pjoin.c.type,
                "with_polymorphic": "*",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __table__ = engineers_table
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        class Manager(Employee):
            __table__ = managers_tables
            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }

    在上面，我们以与之前相同的方式使用 :func:`.polymorphic_union`，只是省略了 ``employee`` 表。

    .. seealso::

        :ref:`orm_imperative_mapping` - 关于命令式或“经典”映射的背景信息

.. tab:: 英文

    The Declarative configurations illustrated with :class:`.ConcreteBase`
    and :class:`.AbstractConcreteBase` are equivalent to two other forms
    of configuration that make use of :func:`.polymorphic_union` explicitly.
    These configurational forms make use of the :class:`_schema.Table` object explicitly
    so that the "polymorphic union" can be created first, then applied
    to the mappings.   These are illustrated here to clarify the role
    of the :func:`.polymorphic_union` function in terms of mapping.

    A **semi-classical mapping** for example makes use of Declarative, but
    establishes the :class:`_schema.Table` objects separately::

        metadata_obj = Base.metadata

        employees_table = Table(
            "employee",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
        )

        managers_table = Table(
            "manager",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("manager_data", String(50)),
        )

        engineers_table = Table(
            "engineer",
            metadata_obj,
            Column("id", Integer, primary_key=True),
            Column("name", String(50)),
            Column("engineer_info", String(50)),
        )

    Next, the UNION is produced using :func:`.polymorphic_union`::

        from sqlalchemy.orm import polymorphic_union

        pjoin = polymorphic_union(
            {
                "employee": employees_table,
                "manager": managers_table,
                "engineer": engineers_table,
            },
            "type",
            "pjoin",
        )

    With the above :class:`_schema.Table` objects, the mappings can be produced using "semi-classical" style,
    where we use Declarative in conjunction with the ``__table__`` argument;
    our polymorphic union above is passed via ``__mapper_args__`` to
    the :paramref:`_orm.Mapper.with_polymorphic` parameter::

        class Employee(Base):
            __table__ = employee_table
            __mapper_args__ = {
                "polymorphic_on": pjoin.c.type,
                "with_polymorphic": ("*", pjoin),
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __table__ = engineer_table
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        class Manager(Employee):
            __table__ = manager_table
            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }

    Alternatively, the same :class:`_schema.Table` objects can be used in
    fully "classical" style, without using Declarative at all.
    A constructor similar to that supplied by Declarative is illustrated::

        class Employee:
            def __init__(self, **kw):
                for k in kw:
                    setattr(self, k, kw[k])


        class Manager(Employee):
            pass


        class Engineer(Employee):
            pass


        employee_mapper = mapper_registry.map_imperatively(
            Employee,
            pjoin,
            with_polymorphic=("*", pjoin),
            polymorphic_on=pjoin.c.type,
        )
        manager_mapper = mapper_registry.map_imperatively(
            Manager,
            managers_table,
            inherits=employee_mapper,
            concrete=True,
            polymorphic_identity="manager",
        )
        engineer_mapper = mapper_registry.map_imperatively(
            Engineer,
            engineers_table,
            inherits=employee_mapper,
            concrete=True,
            polymorphic_identity="engineer",
        )

    The "abstract" example can also be mapped using "semi-classical" or "classical"
    style.  The difference is that instead of applying the "polymorphic union"
    to the :paramref:`_orm.Mapper.with_polymorphic` parameter, we apply it directly
    as the mapped selectable on our basemost mapper.  The semi-classical
    mapping is illustrated below::

        from sqlalchemy.orm import polymorphic_union

        pjoin = polymorphic_union(
            {
                "manager": managers_table,
                "engineer": engineers_table,
            },
            "type",
            "pjoin",
        )


        class Employee(Base):
            __table__ = pjoin
            __mapper_args__ = {
                "polymorphic_on": pjoin.c.type,
                "with_polymorphic": "*",
                "polymorphic_identity": "employee",
            }


        class Engineer(Employee):
            __table__ = engineer_table
            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }


        class Manager(Employee):
            __table__ = manager_table
            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }

    Above, we use :func:`.polymorphic_union` in the same manner as before, except
    that we omit the ``employee`` table.

    .. seealso::

        :ref:`orm_imperative_mapping` - background information on imperative, or "classical" mappings



具有具体继承的关系
+++++++++++++++++++++++++++++++++++++++

Relationships with Concrete Inheritance

.. tab:: 中文

    在具体继承场景中，映射关系是具有挑战性的，因为不同的类不共享一个表。如果关系仅涉及特定类，例如我们之前示例中的 ``Company`` 和 ``Manager`` 之间的关系，则不需要特殊步骤，因为这只是两个相关的表。

    然而，如果 ``Company`` 需要与 ``Employee`` 形成一对多关系，这意味着集合中可能包含 ``Engineer`` 和 ``Manager`` 对象，这意味着 ``Employee`` 必须具有多态加载功能，并且每个相关的表必须具有指向 ``company`` 表的外键。这样的配置示例如下::

        from sqlalchemy.ext.declarative import ConcreteBase


        class Company(Base):
            __tablename__ = "company"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            employees = relationship("Employee")


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    具体继承和关系的下一个复杂性涉及当我们希望 ``Employee``、 ``Manager`` 和 ``Engineer`` 中的一个或全部本身引用 ``Company`` 时。对于这种情况，SQLAlchemy 有特殊行为，即放置在 ``Employee`` 上的 :func:`_orm.relationship` 链接到 ``Company`` **在实例级别不起作用**，对于 ``Manager`` 和 ``Engineer`` 类也是如此。相反，必须在每个类上应用一个单独的 :func:`_orm.relationship`。为了在三个单独的关系中实现双向行为，这些关系作为 ``Company.employees`` 的对立面，使用 :paramref:`_orm.relationship.back_populates` 参数在每个关系之间::

        from sqlalchemy.ext.declarative import ConcreteBase


        class Company(Base):
            __tablename__ = "company"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            employees = relationship("Employee", back_populates="company")


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    上述限制与当前实现相关，包括具体继承类不共享超类的任何属性，因此需要设置不同的关系。

.. tab:: 英文

    In a concrete inheritance scenario, mapping relationships is challenging
    since the distinct classes do not share a table.    If the relationships
    only involve specific classes, such as a relationship between ``Company`` in
    our previous examples and ``Manager``, special steps aren't needed as these
    are just two related tables.

    However, if ``Company`` is to have a one-to-many relationship
    to ``Employee``, indicating that the collection may include both
    ``Engineer`` and ``Manager`` objects, that implies that ``Employee`` must
    have polymorphic loading capabilities and also that each table to be related
    must have a foreign key back to the ``company`` table.  An example of
    such a configuration is as follows::

        from sqlalchemy.ext.declarative import ConcreteBase


        class Company(Base):
            __tablename__ = "company"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            employees = relationship("Employee")


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    The next complexity with concrete inheritance and relationships involves
    when we'd like one or all of ``Employee``, ``Manager`` and ``Engineer`` to
    themselves refer back to ``Company``.   For this case, SQLAlchemy has
    special behavior in that a :func:`_orm.relationship` placed on ``Employee``
    which links to ``Company`` **does not work**
    against the ``Manager`` and ``Engineer`` classes, when exercised at the
    instance level.  Instead, a distinct
    :func:`_orm.relationship` must be applied to each class.   In order to achieve
    bi-directional behavior in terms of three separate relationships which
    serve as the opposite of ``Company.employees``, the
    :paramref:`_orm.relationship.back_populates` parameter is used between
    each of the relationships::

        from sqlalchemy.ext.declarative import ConcreteBase


        class Company(Base):
            __tablename__ = "company"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            employees = relationship("Employee", back_populates="company")


        class Employee(ConcreteBase, Base):
            __tablename__ = "employee"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "employee",
                "concrete": True,
            }


        class Manager(Employee):
            __tablename__ = "manager"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            manager_data = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "manager",
                "concrete": True,
            }


        class Engineer(Employee):
            __tablename__ = "engineer"
            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50))
            engineer_info = mapped_column(String(40))
            company_id = mapped_column(ForeignKey("company.id"))
            company = relationship("Company", back_populates="employees")

            __mapper_args__ = {
                "polymorphic_identity": "engineer",
                "concrete": True,
            }

    The above limitation is related to the current implementation, including
    that concrete inheriting classes do not share any of the attributes of
    the superclass and therefore need distinct relationships to be set up.

加载具体继承映射
+++++++++++++++++++++++++++++++++++++

Loading Concrete Inheritance Mappings

.. tab:: 中文

    使用具体继承进行加载的选项是有限的；通常，如果在映射器上使用声明式具体混入配置了多态加载，则在当前的 SQLAlchemy 版本中无法在查询时进行修改。通常，:func:`_orm.with_polymorphic` 函数可以覆盖具体加载的样式，但由于当前的限制，这尚不支持。

.. tab:: 英文

    The options for loading with concrete inheritance are limited; generally,
    if polymorphic loading is configured on the mapper using one of the
    declarative concrete mixins, it can't be modified at query time
    in current SQLAlchemy versions.   Normally, the :func:`_orm.with_polymorphic`
    function would be able to override the style of loading used by concrete,
    however due to current limitations this is not yet supported.

