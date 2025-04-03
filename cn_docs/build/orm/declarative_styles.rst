.. _orm_declarative_styles_toplevel:

==========================
声明式映射风格
==========================

Declarative Mapping Styles

.. tab:: 中文

    正如在 :ref:`orm_declarative_mapping` 中介绍的那样， **声明式映射** 是现代 SQLAlchemy 中构建映射的典型方式。本节将概述可用于声明式映射器配置的形式。

.. tab:: 英文

    As introduced at :ref:`orm_declarative_mapping`, the **Declarative Mapping** is
    the typical way that mappings are constructed in modern SQLAlchemy.   This
    section will provide an overview of forms that may be used for Declarative
    mapper configuration.


.. _orm_explicit_declarative_base:

.. _orm_declarative_generated_base_class:

使用声明性基类
-------------------------------

Using a Declarative Base Class

.. tab:: 中文

    最常见的方法是通过继承 :class:`_orm.DeclarativeBase` 超类生成“声明式基类”::

        from sqlalchemy.orm import DeclarativeBase


        # 声明式基类
        class Base(DeclarativeBase):
            pass

    声明式基类也可以通过将现有的 :class:`_orm.registry` 分配为名为 ``registry`` 的类变量来创建::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import registry

        reg = registry()


        # 声明式基类
        class Base(DeclarativeBase):
            registry = reg

    .. versionchanged:: 2.0 
        
        The :class:`_orm.DeclarativeBase` 超类取代了 :func:`_orm.declarative_base` 函数和 :meth:`_orm.registry.generate_base` 方法的使用；超类方法与 :pep:`484` 工具集成，无需使用插件。有关迁移说明，请参见 :ref:`whatsnew_20_orm_declarative_typing`。

    使用声明式基类，可以将新映射类声明为基类的子类::

        from datetime import datetime
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[Optional[str]]
            nickname: Mapped[Optional[str]] = mapped_column(String(64))
            create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        class Address(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]

            user: Mapped["User"] = relationship(back_populates="addresses")

    以上， ``Base`` 类作为要映射的新类的基础，如上所述，构造了新映射类 ``User`` 和 ``Address`` 。

    对于构造的每个子类，类的主体遵循声明式映射方法，该方法在幕后定义了 :class:`_schema.Table` 和 :class:`_orm.Mapper` 对象，组成完整的映射。

    .. seealso::

        :ref:`orm_declarative_table_config_toplevel` - 描述了如何指定要生成的映射 :class:`_schema.Table` 的组件，包括关于 :func:`_orm.mapped_column` 构造的使用及其如何与 :class:`_orm.Mapped` 注释类型交互的说明和选项

        :ref:`orm_declarative_mapper_config_toplevel` - 描述了声明式中ORM映射器配置的所有其他方面，包括 :func:`_orm.relationship` 配置、SQL表达式和 :class:`_orm.Mapper` 参数

.. tab:: 英文

    The most common approach is to generate a "Declarative Base" class by
    subclassing the :class:`_orm.DeclarativeBase` superclass::

        from sqlalchemy.orm import DeclarativeBase


        # declarative base class
        class Base(DeclarativeBase):
            pass

    The Declarative Base class may also be created given an existing
    :class:`_orm.registry` by assigning it as a class variable named
    ``registry``::

        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import registry

        reg = registry()


        # declarative base class
        class Base(DeclarativeBase):
            registry = reg

    .. versionchanged:: 2.0 The :class:`_orm.DeclarativeBase` superclass supersedes
    the use of the :func:`_orm.declarative_base` function and
    :meth:`_orm.registry.generate_base` methods; the superclass approach
    integrates with :pep:`484` tools without the use of plugins.
    See :ref:`whatsnew_20_orm_declarative_typing` for migration notes.

    With the declarative base class, new mapped classes are declared as subclasses
    of the base::

        from datetime import datetime
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy.orm import DeclarativeBase
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import relationship


        class Base(DeclarativeBase):
            pass


        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[Optional[str]]
            nickname: Mapped[Optional[str]] = mapped_column(String(64))
            create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        class Address(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]

            user: Mapped["User"] = relationship(back_populates="addresses")

    Above, the ``Base`` class serves as a base for new classes that are to be
    mapped, as above new mapped classes ``User`` and ``Address`` are constructed.

    For each subclass constructed, the body of the class then follows the
    declarative mapping approach which defines both a :class:`_schema.Table` as
    well as a :class:`_orm.Mapper` object behind the scenes which comprise a full
    mapping.

    .. seealso::

        :ref:`orm_declarative_table_config_toplevel` - describes how to specify
        the components of the mapped :class:`_schema.Table` to be generated,
        including notes and options on the use of the :func:`_orm.mapped_column`
        construct and how it interacts with the :class:`_orm.Mapped` annotation
        type

        :ref:`orm_declarative_mapper_config_toplevel` - describes all other
        aspects of ORM mapper configuration within Declarative including
        :func:`_orm.relationship` configuration, SQL expressions and
        :class:`_orm.Mapper` parameters


.. _orm_declarative_decorator:

使用装饰器进行声明性映射（无声明性基类）
------------------------------------------------------------

Declarative Mapping using a Decorator (no declarative base)

.. tab:: 中文

    作为使用 “声明式基类” 的替代方法，可以使用类似于 “经典” 映射的命令式技术，或更简洁地使用装饰器，将声明式映射显式应用于类。:meth:`_orm.registry.mapped` 函数是一个类装饰器，可以应用于没有层次结构的任何Python类。Python类在其他方面通常以声明式风格配置。

    下面的示例使用 :meth:`_orm.registry.mapped` 装饰器而不是 :class:`_orm.DeclarativeBase` 超类设置了与上一节中相同的映射::

        from datetime import datetime
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        class User:
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[Optional[str]]
            nickname: Mapped[Optional[str]] = mapped_column(String(64))
            create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        @mapper_registry.mapped
        class Address:
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]

            user: Mapped["User"] = relationship(back_populates="addresses")

    使用上述风格时，特定类的映射将**仅**在装饰器直接应用于该类时进行。对于继承映射（在 :ref:`inheritance_toplevel` 中详细描述），应将装饰器应用于要映射的每个子类::

        from sqlalchemy.orm import registry

        mapper_registry = registry()


        @mapper_registry.mapped
        class Person:
            __tablename__ = "person"

            person_id = mapped_column(Integer, primary_key=True)
            type = mapped_column(String, nullable=False)

            __mapper_args__ = {
                "polymorphic_on": type,
                "polymorphic_identity": "person",
            }


        @mapper_registry.mapped
        class Employee(Person):
            __tablename__ = "employee"

            person_id = mapped_column(ForeignKey("person.person_id"), primary_key=True)

            __mapper_args__ = {
                "polymorphic_identity": "employee",
            }

    声明式表配置风格 :ref:`declarative table <orm_declarative_table>` 和命令式表配置风格 :ref:`imperative table <orm_imperative_table_configuration>` 都可以与声明式基类或装饰器风格的声明式映射一起使用。

    装饰器形式的映射在将SQLAlchemy声明式映射与其他类仪器系统（例如 dataclasses_ 和 attrs_ ）结合使用时很有用，但请注意，SQLAlchemy 2.0现在也具有与声明式基类的dataclasses集成。

.. tab:: 英文

    As an alternative to using the "declarative base" class is to apply
    declarative mapping to a class explicitly, using either an imperative technique
    similar to that of a "classical" mapping, or more succinctly by using
    a decorator.  The :meth:`_orm.registry.mapped` function is a class decorator
    that can be applied to any Python class with no hierarchy in place.  The
    Python class otherwise is configured in declarative style normally.

    The example below sets up the identical mapping as seen in the
    previous section, using the :meth:`_orm.registry.mapped`
    decorator rather than using the :class:`_orm.DeclarativeBase` superclass::

        from datetime import datetime
        from typing import List
        from typing import Optional

        from sqlalchemy import ForeignKey
        from sqlalchemy import func
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy.orm import Mapped
        from sqlalchemy.orm import mapped_column
        from sqlalchemy.orm import registry
        from sqlalchemy.orm import relationship

        mapper_registry = registry()


        @mapper_registry.mapped
        class User:
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name: Mapped[str]
            fullname: Mapped[Optional[str]]
            nickname: Mapped[Optional[str]] = mapped_column(String(64))
            create_date: Mapped[datetime] = mapped_column(insert_default=func.now())

            addresses: Mapped[List["Address"]] = relationship(back_populates="user")


        @mapper_registry.mapped
        class Address:
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            user_id = mapped_column(ForeignKey("user.id"))
            email_address: Mapped[str]

            user: Mapped["User"] = relationship(back_populates="addresses")

    When using the above style, the mapping of a particular class will **only**
    proceed if the decorator is applied to that class directly. For inheritance
    mappings (described in detail at :ref:`inheritance_toplevel`), the decorator
    should be applied to each subclass that is to be mapped::

        from sqlalchemy.orm import registry

        mapper_registry = registry()


        @mapper_registry.mapped
        class Person:
            __tablename__ = "person"

            person_id = mapped_column(Integer, primary_key=True)
            type = mapped_column(String, nullable=False)

            __mapper_args__ = {
                "polymorphic_on": type,
                "polymorphic_identity": "person",
            }


        @mapper_registry.mapped
        class Employee(Person):
            __tablename__ = "employee"

            person_id = mapped_column(ForeignKey("person.person_id"), primary_key=True)

            __mapper_args__ = {
                "polymorphic_identity": "employee",
            }

    Both the :ref:`declarative table <orm_declarative_table>` and
    :ref:`imperative table <orm_imperative_table_configuration>`
    table configuration styles may be used with either the Declarative Base
    or decorator styles of Declarative mapping.

    The decorator form of mapping is useful when combining a
    SQLAlchemy declarative mapping with other class instrumentation systems
    such as dataclasses_ and attrs_, though note that SQLAlchemy 2.0 now features
    dataclasses integration with Declarative Base classes as well.


.. _dataclass: https://docs.python.org/3/library/dataclasses.html
.. _dataclasses: https://docs.python.org/3/library/dataclasses.html
.. _attrs: https://pypi.org/project/attrs/
