"""
.. tab:: 中文

    展示了一个扩展，它为实体创建版本表，并在每次变更时存储记录。
    该扩展会生成一个匿名的“历史”类，用于表示目标对象的历史版本。
    
    可与 :ref:`examples_versioned_rows` 示例进行对比，后者是在同一张表中将更新作为新行写入，
    而不是使用单独的历史表。
    
    通过一个单元测试模块 ``test_versioning.py`` 来演示用法，该模块使用 SQLAlchemy 的内部 pytest 插件运行::
    
        $ pytest test/base/test_examples.py
    
    以下是一个使用声明式（declarative）进行示例操作的片段::
    
        from history_meta import Versioned, versioned_session
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class SomeClass(Versioned, Base):
            __tablename__ = "sometable"
    
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
    
            def __eq__(self, other):
                assert type(other) is SomeClass and other.id == self.id
    
    
        Session = sessionmaker(bind=engine)
        versioned_session(Session)
    
        sess = Session()
        sc = SomeClass(name="sc1")
        sess.add(sc)
        sess.commit()
    
        sc.name = "sc1modified"
        sess.commit()
    
        assert sc.version == 2
    
        SomeClassHistory = SomeClass.__history_mapper__.class_
    
        assert sess.query(SomeClassHistory).filter(
            SomeClassHistory.version == 1
        ).all() == [SomeClassHistory(version=1, name="sc1")]
    
    ``Versioned`` mixin 设计用于配合声明式使用。
    若要在经典映射（classical mapper）中使用该扩展，可使用 ``_history_mapper`` 函数::
    
        from history_meta import _history_mapper
    
        m = mapper(SomeClass, sometable)
        _history_mapper(m)
    
        SomeHistoryClass = SomeClass.__history_mapper__.class_
    
    该版本控制示例还可与 ORM 的乐观并发控制特性集成，相关文档见 :ref:`mapper_version_counter`。
    若要启用该功能，可将 ``Versioned.use_mapper_versioning`` 设置为 True::
    
        class SomeClass(Versioned, Base):
            __tablename__ = "sometable"
    
            use_mapper_versioning = True
    
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
    
            def __eq__(self, other):
                assert type(other) is SomeClass and other.id == self.id
    
    如上所示，若两个具有相同版本标识符的 ``SomeClass`` 实例同时更新并提交到数据库，
    而数据库的隔离级别允许两个 UPDATE 语句同时进行，
    那么其中一个将会失败，因为它已不再基于最新的版本标识符进行操作。

.. tab:: 英文


    Illustrates an extension which creates version tables for entities and stores
    records for each change. The given extensions generate an anonymous "history"
    class which represents historical versions of the target object.
    
    Compare to the :ref:`examples_versioned_rows` examples which write updates
    as new rows in the same table, without using a separate history table.
    
    Usage is illustrated via a unit test module ``test_versioning.py``, which is
    run using SQLAlchemy's internal pytest plugin::
    
        $ pytest test/base/test_examples.py
    
    
    A fragment of example usage, using declarative::
    
        from history_meta import Versioned, versioned_session
    
    
        class Base(DeclarativeBase):
            pass
    
    
        class SomeClass(Versioned, Base):
            __tablename__ = "sometable"
    
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
    
            def __eq__(self, other):
                assert type(other) is SomeClass and other.id == self.id
    
    
        Session = sessionmaker(bind=engine)
        versioned_session(Session)
    
        sess = Session()
        sc = SomeClass(name="sc1")
        sess.add(sc)
        sess.commit()
    
        sc.name = "sc1modified"
        sess.commit()
    
        assert sc.version == 2
    
        SomeClassHistory = SomeClass.__history_mapper__.class_
    
        assert sess.query(SomeClassHistory).filter(
            SomeClassHistory.version == 1
        ).all() == [SomeClassHistory(version=1, name="sc1")]
    
    The ``Versioned`` mixin is designed to work with declarative.  To use
    the extension with classical mappers, the ``_history_mapper`` function
    can be applied::
    
        from history_meta import _history_mapper
    
        m = mapper(SomeClass, sometable)
        _history_mapper(m)
    
        SomeHistoryClass = SomeClass.__history_mapper__.class_
    
    The versioning example also integrates with the ORM optimistic concurrency
    feature documented at :ref:`mapper_version_counter`.   To enable this feature,
    set the flag ``Versioned.use_mapper_versioning`` to True::
    
        class SomeClass(Versioned, Base):
            __tablename__ = "sometable"
    
            use_mapper_versioning = True
    
            id = Column(Integer, primary_key=True)
            name = Column(String(50))
    
            def __eq__(self, other):
                assert type(other) is SomeClass and other.id == self.id
    
    Above, if two instance of ``SomeClass`` with the same version identifier
    are updated and sent to the database for UPDATE concurrently, if the database
    isolation level allows the two UPDATE statements to proceed, one will fail
    because it no longer is against the last known version identifier.

.. autosource::

"""
