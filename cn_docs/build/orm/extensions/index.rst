.. _plugins:
.. _sqlalchemy.ext:

ORM 扩展
==============

ORM Extensions

.. tab:: 中文

    SQLAlchemy 提供了多种 ORM 扩展，增加了核心行为的附加功能。

    这些扩展几乎完全建立在公共核心和 ORM API 之上，用户应被鼓励阅读其源代码以进一步了解其行为。特别是“水平分片”、“混合属性”和“变异跟踪”扩展非常简洁。

.. tab:: 英文

    SQLAlchemy has a variety of ORM extensions available, which add additional
    functionality to the core behavior.

    The extensions build almost entirely on public core and ORM APIs and users should
    be encouraged to read their source code to further their understanding of their
    behavior.   In particular the "Horizontal Sharding", "Hybrid Attributes", and
    "Mutation Tracking" extensions are very succinct.

.. toctree::
    :maxdepth: 1

    asyncio
    associationproxy
    automap
    baked
    declarative/index
    mutable
    orderinglist
    horizontal_shard
    hybrid
    indexable
    instrumentation

