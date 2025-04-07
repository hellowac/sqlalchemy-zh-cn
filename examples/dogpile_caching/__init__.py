"""
.. tab:: 中文

    演示了如何将 `dogpile.cache <https://dogpilecache.sqlalchemy.org/>`_ 的功能
    嵌入到 ORM 查询中，从而实现对缓存的全面控制，以及从长期缓存中获取
    “惰性加载”（lazy loaded）属性的能力。
    
    在本演示中，涵盖了以下技术：
    
    * 使用 :meth:`_orm.SessionEvents.do_orm_execute` 事件钩子
    * 利用基本技术绕过 :meth:`_orm.Session.execute`，从自定义缓存源中获取数据，
      而不是从数据库中查询。
    * 使用 dogpile.cache 进行基础缓存，借助“区域”（regions）机制对一组固定配置进行全局控制。
    * 使用自定义的 :class:`.UserDefinedOption` 对象，在语句对象中配置选项。
    
    .. seealso::
    
        :ref:`do_orm_execute_re_executing` - 包含一个展示此处技术的一般性示例。
    
    示例代码如下::
    
        # 查询 Person 对象，并指定使用缓存
        stmt = select(Person).options(FromCache("default"))
    
        # 指定每个 Person 的 "addresses" 集合也来自缓存
        stmt = stmt.options(RelationshipCache(Person.addresses, "default"))
    
        # 执行语句并获取结果
        result = session.execute(stmt)
    
        print(result.scalars().all())
    
    运行该示例前，需要确保 SQLAlchemy 和 dogpile.cache 都已安装，
    或已位于当前 PYTHONPATH 中。该演示将创建一个本地目录用于存放数据文件，
    插入初始数据并运行。第二次运行该演示时将利用已存在的缓存文件，
    整个过程只会对两个表执行一条 SQL 语句——但所展示的结果
    将会通过缓存执行数十次惰性加载操作。
    
    演示脚本本身按复杂度排序，并作为 Python 模块运行以确保相对导入正常工作::
    
       $ python -m examples.dogpile_caching.helloworld
    
       $ python -m examples.dogpile_caching.relationship_caching
    
       $ python -m examples.dogpile_caching.advanced
    
       $ python -m examples.dogpile_caching.local_session_caching


.. tab:: 英文

    Illustrates how to embed
    `dogpile.cache <https://dogpilecache.sqlalchemy.org/>`_
    functionality with ORM queries, allowing full cache control
    as well as the ability to pull "lazy loaded" attributes from long term cache.
    
    In this demo, the following techniques are illustrated:
    
    * Using the :meth:`_orm.SessionEvents.do_orm_execute` event hook
    * Basic technique of circumventing :meth:`_orm.Session.execute` to pull from a
      custom cache source instead of the database.
    * Rudimental caching with dogpile.cache, using "regions" which allow
      global control over a fixed set of configurations.
    * Using custom :class:`.UserDefinedOption` objects to configure options in
      a statement object.
    
    .. seealso::
    
        :ref:`do_orm_execute_re_executing` - includes a general example of the
        technique presented here.
    
    E.g.::
    
        # query for Person objects, specifying cache
        stmt = select(Person).options(FromCache("default"))
    
        # specify that each Person's "addresses" collection comes from
        # cache too
        stmt = stmt.options(RelationshipCache(Person.addresses, "default"))
    
        # execute and results
        result = session.execute(stmt)
    
        print(result.scalars().all())
    
    To run, both SQLAlchemy and dogpile.cache must be
    installed or on the current PYTHONPATH. The demo will create a local
    directory for datafiles, insert initial data, and run. Running the
    demo a second time will utilize the cache files already present, and
    exactly one SQL statement against two tables will be emitted - the
    displayed result however will utilize dozens of lazyloads that all
    pull from cache.
    
    The demo scripts themselves, in order of complexity, are run as Python
    modules so that relative imports work::
    
       $ python -m examples.dogpile_caching.helloworld
    
       $ python -m examples.dogpile_caching.relationship_caching
    
       $ python -m examples.dogpile_caching.advanced
    
       $ python -m examples.dogpile_caching.local_session_caching

.. autosource::
    :files: environment.py, caching_query.py, model.py, fixture_data.py, \
          helloworld.py, relationship_caching.py, advanced.py, \
          local_session_caching.py

"""
