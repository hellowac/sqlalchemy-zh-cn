"""
.. tab:: 中文

    使用 SQLAlchemy 分片（Sharding）API 的基础示例。  
    分片指的是在多个数据库之间横向扩展数据的能力。
    
    “分片”映射的基本组成部分包括：
    
    * 多个 :class:`_engine.Engine` 实例，每个实例分配一个“分片 ID”（shard id）。
      这些 :class:`_engine.Engine` 实例可以指向不同的数据库，
      或是同一数据库中不同的 schema / accounts，甚至也可以仅通过一些选项加以区分，
      使其在使用时访问不同的 schema 或表。
    
    * 一个函数，它接收一个待保存的实例并返回一个分片 ID；
      这个函数被称为 "shard_chooser"。
    
    * 一个函数，它接收一个实例标识符，并返回一个适用的分片 ID 列表；
      这个函数称为 "id_chooser"。如果该函数返回所有分片 ID，则表示将搜索所有分片。
    
    * 一个函数，它接收一个查询对象并返回一个要尝试的分片 ID 列表；
      这个函数称为 "query_chooser"。如果返回所有分片 ID，则表示将对所有分片进行查询，
      并将结果合并。
    
    在这些示例中，我们对相同的基础模型使用了不同类型的分片方式，
    该模型用于按大陆存储天气数据。我们提供了示例性的 shard_chooser、id_chooser 和
    query_chooser 函数。其中 query_chooser 展示了如何通过检查 SQL 表达式元素，
    尝试推断出所请求的唯一分片。
    
    构建通用的分片操作是一种富有挑战性的方式，目的是为多个数据库之间的实例组织问题提供解决方案。
    作为一种更简单直白的替代方式，“独立实体（distinct entity）”方法可以显式地将对象分配到不同的表
    （并可能是不同的数据库节点）中 —— 该方法在 Wiki 页面中有描述，
    参见 `EntityName <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/EntityName>`_。


.. tab:: 英文

    A basic example of using the SQLAlchemy Sharding API.
    Sharding refers to horizontally scaling data across multiple
    databases.
    
    The basic components of a "sharded" mapping are:
    
    * multiple :class:`_engine.Engine` instances, each assigned a "shard id".
      These :class:`_engine.Engine` instances may refer to different databases,
      or different schemas / accounts within the same database, or they can
      even be differentiated only by options that will cause them to access
      different schemas or tables when used.
    
    * a function which can return a single shard id, given an instance
      to be saved; this is called "shard_chooser"
    
    * a function which can return a list of shard ids which apply to a particular
      instance identifier; this is called "id_chooser".If it returns all shard ids,
      all shards will be searched.
    
    * a function which can return a list of shard ids to try, given a particular
      Query ("query_chooser").  If it returns all shard ids, all shards will be
      queried and the results joined together.
    
    In these examples, different kinds of shards are used against the same basic
    example which accommodates weather data on a per-continent basis. We provide
    example shard_chooser, id_chooser and query_chooser functions. The
    query_chooser illustrates inspection of the SQL expression element in order to
    attempt to determine a single shard being requested.
    
    The construction of generic sharding routines is an ambitious approach
    to the issue of organizing instances among multiple databases.   For a
    more plain-spoken alternative, the "distinct entity" approach
    is a simple method of assigning objects to different tables (and potentially
    database nodes) in an explicit way - described on the wiki at
    `EntityName <https://www.sqlalchemy.org/trac/wiki/UsageRecipes/EntityName>`_.

.. autosource::

"""
