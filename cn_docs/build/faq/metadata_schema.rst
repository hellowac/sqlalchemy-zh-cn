=================
元数据 / Schema
=================

MetaData / Schema

.. contents::
    :local:
    :class: faq
    :backlinks: none



当我说 ``table.drop()`` / ``metadata.drop_all()`` 时，我的程序挂起了
===========================================================================

My program is hanging when I say ``table.drop()`` / ``metadata.drop_all()``

.. tab:: 中文

    这通常对应两个条件：1. 使用的是 PostgreSQL，它对表锁非常严格；2. 存在一个仍然保持打开状态的连接，该连接持有对表的锁，且与用于执行 DROP 语句的连接不同。以下是该模式的最简示例::

        connection = engine.connect()
        result = connection.execute(mytable.select())

        mytable.drop(engine)

    在上述代码中，一个连接池中的连接仍处于被检出状态；此外， `result` 对象也保持着对该连接的引用。如果使用了“隐式执行”，则该 `result` 对象会一直保持连接处于打开状态，直到该对象被关闭或所有结果行被读取完毕。

    对 ``mytable.drop(engine)`` 的调用尝试在另一个从 :class:`_engine.Engine` 获取的连接上执行 DROP TABLE 语句，此时可能会发生锁等待。

    解决方法是在执行 DROP TABLE 之前关闭所有连接::

        connection = engine.connect()
        result = connection.execute(mytable.select())

        # 完全读取结果集
        result.fetchall()

        # 关闭连接
        connection.close()

        # 此时锁已经释放
        mytable.drop(engine)

.. tab:: 英文

    This usually corresponds to two conditions: 1. using PostgreSQL, which is really
    strict about table locks, and 2. you have a connection still open which
    contains locks on the table and is distinct from the connection being used for
    the DROP statement.  Heres the most minimal version of the pattern::

        connection = engine.connect()
        result = connection.execute(mytable.select())

        mytable.drop(engine)

    Above, a connection pool connection is still checked out; furthermore, the
    result object above also maintains a link to this connection.  If
    "implicit execution" is used, the result will hold this connection opened until
    the result object is closed or all rows are exhausted.

    The call to ``mytable.drop(engine)`` attempts to emit DROP TABLE on a second
    connection procured from the :class:`_engine.Engine` which will lock.

    The solution is to close out all connections before emitting DROP TABLE::

        connection = engine.connect()
        result = connection.execute(mytable.select())

        # fully read result sets
        result.fetchall()

        # close connections
        connection.close()

        # now locks are removed
        mytable.drop(engine)

SQLAlchemy 是否支持 ALTER TABLE、CREATE VIEW、CREATE TRIGGER、Schema升级功能？
===============================================================================================

Does SQLAlchemy support ALTER TABLE, CREATE VIEW, CREATE TRIGGER, Schema Upgrade Functionality?

.. tab:: 中文

    SQLAlchemy 本身不直接支持通用的 ALTER 操作。如需在特定场景中执行自定义 DDL，可以使用 :class:`.DDL` 及相关构造器。更多内容请参考 :ref:`metadata_ddl_toplevel` 中的讨论。

    更全面的解决方案是使用模式迁移工具，如 Alembic 或 SQLAlchemy-Migrate；详见 :ref:`schema_migrations` 章节。

.. tab:: 英文


    General ALTER support isn't present in SQLAlchemy directly.  For special DDL
    on an ad-hoc basis, the :class:`.DDL` and related constructs can be used.
    See :ref:`metadata_ddl_toplevel` for a discussion on this subject.

    A more comprehensive option is to use schema migration tools, such as Alembic
    or SQLAlchemy-Migrate; see :ref:`schema_migrations` for discussion on this.



如何按依赖关系对 Table 对象进行排序？
==========================================================

How can I sort Table objects in order of their dependency?

.. tab:: 中文

    你可以通过 :attr:`_schema.MetaData.sorted_tables` 函数获取按依赖顺序排序的表对象::

        metadata_obj = MetaData()
        # ... 向 metadata 添加 Table 对象
        ti = metadata_obj.sorted_tables
        for t in ti:
            print(t)

.. tab:: 英文

    This is available via the :attr:`_schema.MetaData.sorted_tables` function::

        metadata_obj = MetaData()
        # ... add Table objects to metadata
        ti = metadata_obj.sorted_tables
        for t in ti:
            print(t)

.. _faq_ddl_as_string:



如何以字符串形式获取 CREATE TABLE/DROP TABLE 输出？
==============================================================

How can I get the CREATE TABLE/ DROP TABLE output as a string?

.. tab:: 中文

    现代 SQLAlchemy 提供了用于表示 DDL 操作的子句构造器。它们可以像其他 SQL 表达式一样被渲染为字符串::

        from sqlalchemy.schema import CreateTable

        print(CreateTable(mytable))

    若想针对特定引擎获取对应的字符串表示::

        print(CreateTable(mytable).compile(engine))

    还有一种特殊形式的 :class:`_engine.Engine`，可通过 :func:`.create_mock_engine` 获取，它允许将整个 metadata 的创建过程以字符串形式输出。示例如下::

        from sqlalchemy import create_mock_engine


        def dump(sql, *multiparams, **params):
            print(sql.compile(dialect=engine.dialect))


        engine = create_mock_engine("postgresql+psycopg2://", dump)
        metadata_obj.create_all(engine, checkfirst=False)

    `Alembic <https://alembic.sqlalchemy.org>`_ 工具也支持“离线”SQL 生成模式，可将数据库迁移操作渲染为 SQL 脚本。

.. tab:: 英文

    Modern SQLAlchemy has clause constructs which represent DDL operations. These
    can be rendered to strings like any other SQL expression::

        from sqlalchemy.schema import CreateTable

        print(CreateTable(mytable))

    To get the string specific to a certain engine::

        print(CreateTable(mytable).compile(engine))

    There's also a special form of :class:`_engine.Engine` available via
    :func:`.create_mock_engine` that allows one to dump an entire
    metadata creation sequence as a string, using this recipe::

        from sqlalchemy import create_mock_engine


        def dump(sql, *multiparams, **params):
            print(sql.compile(dialect=engine.dialect))


        engine = create_mock_engine("postgresql+psycopg2://", dump)
        metadata_obj.create_all(engine, checkfirst=False)

    The `Alembic <https://alembic.sqlalchemy.org>`_ tool also supports
    an "offline" SQL generation mode that renders database migrations as SQL scripts.

如何对 Table/Column 进行子类化以提供某些行为/配置？
============================================================================

How can I subclass Table/Column to provide certain behaviors/configurations?

.. tab:: 中文

    :class:`_schema.Table` 和 :class:`_schema.Column` 不适合直接进行子类化。但可以通过工厂函数的方式实现构造时的定制行为，以及通过附加事件机制，定义约束命名规则等 schema 对象之间的关联行为。关于这些技术的一个示例，可参见 `Naming Conventions <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/NamingConventions>`_。

.. tab:: 英文

    :class:`_schema.Table` and :class:`_schema.Column` are not good targets for direct subclassing.
    However, there are simple ways to get on-construction behaviors using creation
    functions, and behaviors related to the linkages between schema objects such as
    constraint conventions or naming conventions using attachment events.
    An example of many of these
    techniques can be seen at `Naming Conventions <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/NamingConventions>`_.
