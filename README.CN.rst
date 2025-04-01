SQLAlchemy
==========

|PyPI| |Python| |Downloads|

.. |PyPI| image:: https://img.shields.io/pypi/v/sqlalchemy
    :target: https://pypi.org/project/sqlalchemy
    :alt: PyPI

.. |Python| image:: https://img.shields.io/pypi/pyversions/sqlalchemy
    :target: https://pypi.org/project/sqlalchemy
    :alt: PyPI - Python Version

.. |Downloads| image:: https://static.pepy.tech/badge/sqlalchemy/month
    :target: https://pepy.tech/project/sqlalchemy
    :alt: PyPI - Downloads


Python SQL 工具包和对象关系映射器

介绍
-------------

SQLAlchemy 是 Python SQL 工具包和对象关系映射器，它为应用程序开发人员提供了 SQL 的全部功能和灵活性。SQLAlchemy 提供了一整套众所周知的企业级持久性模式，旨在实现高效、高性能的数据库访问，并改编为一种简单且 Pythonic 的域语言。

SQLAlchemy 的主要功能包括：

* 一个工业级的 ORM，从核心构建在身份映射、工作单元和数据映射模式上。这些模式允许使用声明式配置系统透明地持久化对象。领域模型可以自然地构造和操作，更改会自动与当前事务同步。
* 一个面向关系的查询系统，明确地展示了 SQL 功能的全部范围，包括连接、子查询、关联和几乎所有其他功能，在对象模型的术语中。使用 ORM 编写查询使用了与编写 SQL 时相同的关系组成技术。虽然你可以随时使用字面 SQL，但几乎从不需要。
* 一个全面且灵活的急加载系统，用于相关集合和对象。集合在会话中缓存，可以在单个访问时加载，也可以使用连接一次性加载，或者通过集合查询跨整个结果集加载。
* 一个核心 SQL 构建系统和 DBAPI 交互层。SQLAlchemy Core 独立于 ORM，是一个完整的数据库抽象层，包括一个可扩展的基于 Python 的 SQL 表达式语言、模式元数据、连接池、类型强制和自定义类型。
* 所有的主键和外键约束都假定是复合的和自然的。当然，代理整数主键仍然是常态，但 SQLAlchemy 从不假定或硬编码这种模型。
* 数据库内省和生成。数据库模式可以一步“反映”到表示数据库元数据的 Python 结构中；这些相同的结构可以生成 CREATE 语句——所有这些都在 Core 内部，独立于 ORM。

SQLAlchemy 的哲学：

* 随着大小和性能的重要性越来越高，SQL 数据库越来越不像对象集合；随着抽象的重要性越来越高，对象集合越来越不像表和行。SQLAlchemy 旨在兼顾这两个原则。
* ORM 不需要隐藏“R”。关系数据库提供丰富的基于集合的功能，应该完全展示。SQLAlchemy 的 ORM 提供了一套开放式的模式，允许开发人员在领域模型和关系模式之间构建自定义的中介层，使所谓的“对象关系阻抗”问题成为遥远的记忆。
* 在所有情况下，开发人员都做出关于对象模型和关系模式的设计、结构和命名约定的所有决策。SQLAlchemy 只提供自动执行这些决策的手段。
* 使用 SQLAlchemy 时，不存在“ORM 生成了一个错误的查询”——你完全控制查询的结构，包括如何组织连接、如何使用子查询和关联、请求哪些列。SQLAlchemy 所做的一切最终都是开发人员启动的决策的结果。
* 如果问题不需要 ORM，不要使用 ORM。SQLAlchemy 包含一个 Core 和单独的 ORM 组件。Core 提供了一个完整的 SQL 表达语言，允许 Python 式构建直接渲染为目标数据库的 SQL 字符串的 SQL 构造，返回的结果集本质上是增强的 DBAPI 游标。
* 事务应该是常态。使用 SQLAlchemy 的 ORM，直到调用 commit() 之前，什么都不会永久存储。SQLAlchemy 鼓励应用程序创建一致的方法来划定一系列操作的开始和结束。
* 永远不要在 SQL 语句中渲染文字值。尽可能使用绑定参数，允许查询优化器有效缓存查询计划，并使 SQL 注入攻击成为非问题。

文档
-------------

最新文档在：

https://www.sqlalchemy.org/docs/

安装 / 要求
---------------------------

有关安装的完整文档在
`Installation <https://www.sqlalchemy.org/docs/intro.html#installation>`_。

获取帮助 / 开发 / 错误报告
------------------------------------------

请参阅 `SQLAlchemy Community Guide <https://www.sqlalchemy.org/support.html>`_。

行为准则
---------------

最重要的是，SQLAlchemy 非常重视用户和开发人员之间的礼貌、周到和建设性沟通。
请参阅我们当前的行为准则
`Code of Conduct <https://www.sqlalchemy.org/codeofconduct.html>`_。

许可证
-------

SQLAlchemy 根据 `MIT 许可证
<https://www.opensource.org/licenses/mit-license.php>`_ 进行分发。

