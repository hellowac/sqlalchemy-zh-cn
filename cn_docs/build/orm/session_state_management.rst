状态管理
================

State Management

.. _session_object_states:

对象状态简介
------------------------------

Quickie Intro to Object States

.. tab:: 中文

    了解实例在会话中的可能状态是很有帮助的：

    * **Transient（临时状态）** - 一个不在会话中且未保存到数据库的实例；即它没有数据库身份。此类对象与 ORM 的唯一关系是其类关联了一个 :class:`_orm.Mapper`。

    * **Pending（待处理状态）** - 当你使用 :meth:`~.Session.add` 添加一个临时实例时，它变为待处理状态。它尚未真正刷新到数据库，但会在下次刷新时进行。

    * **Persistent（持久状态）** - 一个存在于会话中且在数据库中有记录的实例。你可以通过刷新使待处理实例变为持久实例，或通过查询数据库获取现有实例（或将其他会话中的持久实例移动到你的本地会话中）来获得持久实例。

    * **Deleted（删除状态）** - 一个在刷新内被删除的实例，但事务尚未完成。处于此状态的对象本质上处于“待处理”状态的相反状态；当会话的事务提交时，该对象将移动到分离状态。或者，当会话的事务回滚时，已删除的对象将 *返回* 到持久状态。

    * **Detached（分离状态）** - 一个对应或先前对应于数据库记录但当前不在任何会话中的实例。分离对象将包含一个数据库身份标记，但由于它不关联任何会话，因此无法确定此数据库身份是否实际存在于目标数据库中。分离对象通常是安全的，但它们无法加载未加载的属性或先前标记为“已过期”的属性。

    有关所有可能状态转换的深入了解，请参阅 :ref:`session_lifecycle_events` 部分，该部分描述了每个转换以及如何以编程方式跟踪每个转换。

.. tab:: 英文

    It's helpful to know the states which an instance can have within a session:

    * **Transient** - an instance that's not in a session, and is not saved to the
      database; i.e. it has no database identity. The only relationship such an
      object has to the ORM is that its class has a :class:`_orm.Mapper` associated
      with it.

    * **Pending** - when you :meth:`~.Session.add` a transient
      instance, it becomes pending. It still wasn't actually flushed to the
      database yet, but it will be when the next flush occurs.

    * **Persistent** - An instance which is present in the session and has a record
      in the database. You get persistent instances by either flushing so that the
      pending instances become persistent, or by querying the database for
      existing instances (or moving persistent instances from other sessions into
      your local session).

    * **Deleted** - An instance which has been deleted within a flush, but
      the transaction has not yet completed.  Objects in this state are essentially
      in the opposite of "pending" state; when the session's transaction is committed,
      the object will move to the detached state.  Alternatively, when
      the session's transaction is rolled back, a deleted object moves
      *back* to the persistent state.

    * **Detached** - an instance which corresponds, or previously corresponded,
      to a record in the database, but is not currently in any session.
      The detached object will contain a database identity marker, however
      because it is not associated with a session, it is unknown whether or not
      this database identity actually exists in a target database.  Detached
      objects are safe to use normally, except that they have no ability to
      load unloaded attributes or attributes that were previously marked
      as "expired".

    For a deeper dive into all possible state transitions, see the
    section :ref:`session_lifecycle_events` which describes each transition
    as well as how to programmatically track each one.

获取对象的当前状态
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Getting the Current State of an Object

.. tab:: 中文

  可以在任何时候使用映射实例上的 :func:`_sa.inspect` 函数查看任意已映射对象的实际状态；该函数将返回对应的 :class:`.InstanceState` 对象，该对象管理该实例的内部 ORM 状态。:class:`.InstanceState` 提供了若干访问器属性，其中包括一些布尔属性，用于指示对象的持久化状态，包括：

  * :attr:`.InstanceState.transient`
  * :attr:`.InstanceState.pending`
  * :attr:`.InstanceState.persistent`
  * :attr:`.InstanceState.deleted`
  * :attr:`.InstanceState.detached`

  例如::

      >>> from sqlalchemy import inspect
      >>> insp = inspect(my_object)
      >>> insp.persistent
      True

  .. seealso::

      :ref:`orm_mapper_inspection_instancestate` - 更多关于 :class:`.InstanceState` 的示例

.. tab:: 英文

    The actual state of any mapped object can be viewed at any time using the :func:`_sa.inspect` function on a mapped instance; this function will return the corresponding :class:`.InstanceState` object which manages the internal ORM state for the object.  :class:`.InstanceState` provides, among other accessors, boolean attributes indicating the persistence state of the object, including:

    * :attr:`.InstanceState.transient`
    * :attr:`.InstanceState.pending`
    * :attr:`.InstanceState.persistent`
    * :attr:`.InstanceState.deleted`
    * :attr:`.InstanceState.detached`

    E.g.::

        >>> from sqlalchemy import inspect
        >>> insp = inspect(my_object)
        >>> insp.persistent
        True

    .. seealso::

        :ref:`orm_mapper_inspection_instancestate` - further examples of :class:`.InstanceState`

.. _session_attributes:

会话属性
------------------

Session Attributes

.. tab:: 中文

    :class:`~sqlalchemy.orm.session.Session` 本身在行为上有些类似于集合（set）类型。可以通过迭代器接口访问其中的所有项::

        for obj in session:
            print(obj)

    也可以使用常规的 “包含” 语义来测试某个对象是否存在于会话中::

        if obj in session:
            print("Object is present")

    Session 同时还会跟踪所有新创建的对象（即 pending 状态的对象）、所有自上次加载或保存后发生更改的对象（即 “dirty” 状态的对象），以及所有被标记为已删除的对象::

        # 最近添加到 Session 中的 pending 对象
        session.new

        # 当前检测到已更改的持久化对象
        # （此集合现在在每次访问该属性时动态生成）
        session.dirty

        # 通过 session.delete(obj) 标记为删除的持久化对象
        session.deleted

        # 所有持久化对象的字典，以其标识键作为键
        session.identity_map

    （文档参考：:attr:`.Session.new` 、 :attr:`.Session.dirty` 、 :attr:`.Session.deleted` 、:attr:`.Session.identity_map` ）。

.. tab:: 英文

    The :class:`~sqlalchemy.orm.session.Session` itself acts somewhat like a set-like collection. All items present may be accessed using the iterator interface::

        for obj in session:
            print(obj)

    And presence may be tested for using regular "contains" semantics::

        if obj in session:
            print("Object is present")

    The session is also keeping track of all newly created (i.e. pending) objects, all objects which have had changes since they were last loaded or saved (i.e. "dirty"), and everything that's been marked as deleted::

        # pending objects recently added to the Session
        session.new

        # persistent objects which currently have changes detected
        # (this collection is now created on the fly each time the property is called)
        session.dirty

        # persistent objects that have been marked as deleted via session.delete(obj)
        session.deleted

        # dictionary of all persistent objects, keyed on their
        # identity key
        session.identity_map

    (Documentation: :attr:`.Session.new`, :attr:`.Session.dirty`, :attr:`.Session.deleted`, :attr:`.Session.identity_map`).


.. _session_referencing_behavior:

会话引用行为
----------------------------

Session Referencing Behavior

.. tab:: 中文

    Session 中的对象是 *弱引用* 的。这意味着当对象在外部应用中不再被引用时，它们也会从 :class:`~sqlalchemy.orm.session.Session` 的作用域中消失，并被 Python 解释器进行垃圾回收。例外情况包括：处于 pending 状态的对象、被标记为已删除的对象，或者是具有未提交更改的持久化对象。在一次完整的 flush 操作之后，这些集合会被清空，所有对象将再次以弱引用形式存在。

    若希望 Session 中的对象保持 *强引用*，通常只需要一个简单的方法。例如，可以将对象加载到一个以主键为键的本地字典中，或者放入列表或集合中，在需要维持引用的那段时间内保留它们。这些集合也可以关联到一个 :class:`.Session`，方法是将它们放入 :attr:`.Session.info` 字典中。

    也可以使用基于事件的方式来实现。以下是一个简单的配方，为所有处于 :term:`persistent` 状态的对象提供“强引用”行为::

        from sqlalchemy import event


        def strong_reference_session(session):
            @event.listens_for(session, "pending_to_persistent")
            @event.listens_for(session, "deleted_to_persistent")
            @event.listens_for(session, "detached_to_persistent")
            @event.listens_for(session, "loaded_as_persistent")
            def strong_ref_object(sess, instance):
                if "refs" not in sess.info:
                    sess.info["refs"] = refs = set()
                else:
                    refs = sess.info["refs"]

                refs.add(instance)

            @event.listens_for(session, "persistent_to_detached")
            @event.listens_for(session, "persistent_to_deleted")
            @event.listens_for(session, "persistent_to_transient")
            def deref_object(sess, instance):
                sess.info["refs"].discard(instance)

    在上述代码中，我们拦截了 :meth:`.SessionEvents.pending_to_persistent` 、 :meth:`.SessionEvents.detached_to_persistent` 、 :meth:`.SessionEvents.deleted_to_persistent` 和 :meth:`.SessionEvents.loaded_as_persistent` 事件钩子，以便在对象进入 :term:`persistent` 状态时进行拦截；同时也拦截了 :meth:`.SessionEvents.persistent_to_detached` 和 :meth:`.SessionEvents.persistent_to_deleted` 事件，以便在对象离开 persistent 状态时移除引用。

    可以将上述函数用于任意一个 :class:`.Session` 实例，从而在每个 :class:`.Session` 范围内提供强引用行为::

        from sqlalchemy.orm import Session

        my_session = Session()
        strong_reference_session(my_session)

    也可以应用于任意一个 :class:`.sessionmaker` 实例::

        from sqlalchemy.orm import sessionmaker

        maker = sessionmaker()
        strong_reference_session(maker)

.. tab:: 英文

    Objects within the session are *weakly referenced*. This means that when they are dereferenced in the outside application, they fall out of scope from within the :class:`~sqlalchemy.orm.session.Session` as well and are subject to garbage collection by the Python interpreter. The exceptions to this include objects which are pending, objects which are marked as deleted, or persistent objects which have pending changes on them. After a full flush, these collections are all empty, and all objects are again weakly referenced.

    To cause objects in the :class:`.Session` to remain strongly referenced, usually a simple approach is all that's needed.  Examples of externally managed strong-referencing behavior include loading objects into a local dictionary keyed to their primary key, or into lists or sets for the span of time that they need to remain referenced. These collections can be associated with a :class:`.Session`, if desired, by placing them into the :attr:`.Session.info` dictionary.

    An event based approach is also feasible.  A simple recipe that provides
    "strong referencing" behavior for all objects as they remain within
    the :term:`persistent` state is as follows::

        from sqlalchemy import event


        def strong_reference_session(session):
            @event.listens_for(session, "pending_to_persistent")
            @event.listens_for(session, "deleted_to_persistent")
            @event.listens_for(session, "detached_to_persistent")
            @event.listens_for(session, "loaded_as_persistent")
            def strong_ref_object(sess, instance):
                if "refs" not in sess.info:
                    sess.info["refs"] = refs = set()
                else:
                    refs = sess.info["refs"]

                refs.add(instance)

            @event.listens_for(session, "persistent_to_detached")
            @event.listens_for(session, "persistent_to_deleted")
            @event.listens_for(session, "persistent_to_transient")
            def deref_object(sess, instance):
                sess.info["refs"].discard(instance)

    Above, we intercept the :meth:`.SessionEvents.pending_to_persistent`, :meth:`.SessionEvents.detached_to_persistent`, :meth:`.SessionEvents.deleted_to_persistent` and :meth:`.SessionEvents.loaded_as_persistent` event hooks in order to intercept objects as they enter the :term:`persistent` transition, and the :meth:`.SessionEvents.persistent_to_detached` and :meth:`.SessionEvents.persistent_to_deleted` hooks to intercept objects as they leave the persistent state.

    The above function may be called for any :class:`.Session` in order to provide strong-referencing behavior on a per-:class:`.Session` basis::

        from sqlalchemy.orm import Session

        my_session = Session()
        strong_reference_session(my_session)

    It may also be called for any :class:`.sessionmaker`::

        from sqlalchemy.orm import sessionmaker

        maker = sessionmaker()
        strong_reference_session(maker)

.. _unitofwork_merging:

合并
-------

Merging

.. tab:: 中文

    :meth:`~.Session.merge` 会将外部对象的状态转移到 Session 中的新实例或已存在实例中。它还会将传入数据与数据库状态进行对比，从而生成将在下次 flush 中应用的变更历史；也可以选择不生成历史记录，也不访问数据库，仅执行简单的状态“转移”。用法如下::

        merged_object = session.merge(existing_object)

    当传入一个实例时，其行为如下：

    * 首先检查该实例的主键。如果主键存在，尝试在本地 identity map 中查找该实例。若 ``load=True`` （默认值），当本地未找到时还会访问数据库查找对应主键的实例。
    * 如果传入的实例没有主键，或者根据主键找不到任何实例，则会创建一个新实例。
    * 然后将传入实例的状态复制到找到/新建的目标实例上。对于源实例中存在的属性值，会将其复制到目标实例中；而对于源实例中未提供的属性值，则目标实例中的对应属性会被从内存中 :term:`expired`，即清除当前值，但不会修改数据库中已持久化的值。

      若保持 ``load=True`` （默认），该复制过程会触发事件，并会加载目标对象上尚未加载的集合属性，以便将传入状态与数据库中的状态进行比对。若传入 ``load=False``，则会直接“盖章”式地复制状态，不产生任何历史记录。
    * 此操作会级联到相关的对象和集合，依据 ``merge`` 级联设置（参见 :ref:`unitofwork_cascades`）。
    * 最终返回新的实例。

    使用 :meth:`~.Session.merge` 时，提供的“源”实例不会被修改，也不会关联到目标 :class:`.Session`，仍可被多次合并到其他不同的 :class:`.Session` 中。:meth:`~.Session.merge` 非常适用于将某些对象结构的状态拷贝到新的 Session 中，而无需关注其来源或当前是否已关联 Session。以下是几个典型示例：

    * 一个应用程序从文件中读取一个对象结构，并希望将其保存到数据库。它可以先解析文件，构建对象结构，然后使用 :meth:`~.Session.merge` 将其保存到数据库中，确保文件中的数据用于决定结构中每个元素的主键。以后若文件发生更改，应用可重新执行相同过程，生成略有不同的对象结构，再次使用 ``merge`` 操作，:class:`~sqlalchemy.orm.session.Session` 将自动更新数据库：通过主键加载各对象，并将其状态更新为新传入的状态。

    * 一个应用将对象存储在内存缓存中，并被多个 :class:`.Session` 实例共享。每次从缓存中取出对象时，都会使用 :meth:`~.Session.merge` 为请求的 :class:`.Session` 创建一个本地副本。缓存中的对象保持“分离”状态；只有它的状态被拷贝到各 Session 中本地的新副本。

      在这种缓存场景中，通常会使用 ``load=False`` 标志来省略与数据库状态比对的开销。此外，还有一个 :meth:`~.Session.merge` 的“批量”版本，称为 :meth:`_query.Query.merge_result`，专为支持缓存增强的 :class:`_query.Query` 对象设计 —— 详见 :ref:`examples_caching` 章节。

    * 一个应用希望将一批对象的状态转移到由工作线程或其他并发系统管理的 :class:`.Session` 中。:meth:`~.Session.merge` 会为每个对象创建一份拷贝放入新的 Session 中。操作结束后，父线程/进程仍保留原始对象，而子线程/工作单元则可以使用这些对象的本地副本继续操作。

      在“跨线程/进程转移”的场景中，应用也可能选择使用 ``load=False``，以避免额外开销和重复的 SQL 查询。

.. tab:: 英文

    :meth:`~.Session.merge` transfers state from an outside object into a new or already existing instance within a session.   It also reconciles the incoming data against the state of the database, producing a history stream which will be applied towards the next flush, or alternatively can be made to produce a simple "transfer" of state without producing change history or accessing the database.  Usage is as follows::

        merged_object = session.merge(existing_object)

    When given an instance, it follows these steps:

    * It examines the primary key of the instance. If it's present, it attempts to locate that instance in the local identity map.   If the ``load=True`` flag is left at its default, it also checks the database for this primary key if not located locally.
    * If the given instance has no primary key, or if no instance can be found with the primary key given, a new instance is created.
    * The state of the given instance is then copied onto the located/newly created instance. For attribute values which are present on the source instance, the value is transferred to the target instance. For attribute values that aren't present on the source instance, the corresponding attribute on the target instance is :term:`expired` from memory, which discards any locally present value from the target instance for that attribute, but no direct modification is made to the database-persisted value for that attribute.

      If the ``load=True`` flag is left at its default, this copy process emits events and will load the target object's unloaded collections for each attribute present on the source object, so that the incoming state can be reconciled against what's present in the database.  If ``load`` is passed as ``False``, the incoming data is "stamped" directly without producing any history.
    * The operation is cascaded to related objects and collections, as indicated by the ``merge`` cascade (see :ref:`unitofwork_cascades`).
    * The new instance is returned.

    With :meth:`~.Session.merge`, the given "source" instance is not modified nor is it associated with the target :class:`.Session`, and remains available to be merged with any number of other :class:`.Session` objects.  :meth:`~.Session.merge` is useful for taking the state of any kind of object structure without regard for its origins or current session associations and copying its state into a new session. Here's some examples:

    * An application which reads an object structure from a file and wishes to save it to the database might parse the file, build up the structure, and then use :meth:`~.Session.merge` to save it to the database, ensuring that the data within the file is used to formulate the primary key of each element of the structure. Later, when the file has changed, the same process can be re-run, producing a slightly different object structure, which can then be ``merged`` in again, and the :class:`~sqlalchemy.orm.session.Session` will automatically update the database to reflect those changes, loading each object from the database by primary key and then updating its state with the new state given.

    * An application is storing objects in an in-memory cache, shared by many :class:`.Session` objects simultaneously.   :meth:`~.Session.merge` is used each time an object is retrieved from the cache to create a local copy of it in each :class:`.Session` which requests it. The cached object remains detached; only its state is moved into copies of itself that are local to individual :class:`~.Session` objects.

      In the caching use case, it's common to use the ``load=False`` flag to remove the overhead of reconciling the object's state with the database.   There's also a "bulk" version of :meth:`~.Session.merge` called :meth:`_query.Query.merge_result` that was designed to work with cache-extended :class:`_query.Query` objects - see the section :ref:`examples_caching`.

    * An application wants to transfer the state of a series of objects into a :class:`.Session` maintained by a worker thread or other concurrent system.  :meth:`~.Session.merge` makes a copy of each object to be placed into this new :class:`.Session`.  At the end of the operation, the parent thread/process maintains the objects it started with, and the thread/worker can proceed with local copies of those objects.

      In the "transfer between threads/processes" use case, the application may want to use the ``load=False`` flag as well to avoid overhead and redundant SQL queries as the data is transferred.

合并提示
~~~~~~~~~~

Merge Tips

.. tab:: 中文

    :meth:`~.Session.merge` 是一个在多种场景下都极为有用的方法。然而，它涉及到瞬态/分离对象与持久对象之间的细致边界处理，以及状态的自动传递。在这些场景中，可能会遇到各种情况，因此通常需要更加小心地处理对象的状态。使用 :meth:`~.Session.merge` 时常见的问题，通常是传入的对象具有某种未预期的状态。

    我们来看一个经典的 `User` 和 `Address` 对象示例::

        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50), nullable=False)
            addresses = relationship("Address", backref="user")


        class Address(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            email_address = mapped_column(String(50), nullable=False)
            user_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    假设我们已有一个持久化的 ``User`` 对象和一个关联的 ``Address``::

        >>> u1 = User(name="ed", addresses=[Address(email_address="ed@ed.com")])
        >>> session.add(u1)
        >>> session.commit()

    现在我们创建一个会被合并的对象 ``a1``，其数据将覆盖已有的 ``Address``::

        >>> existing_a1 = u1.addresses[0]
        >>> a1 = Address(id=existing_a1.id)

    如果我们这么做，就会遇到一个意外::

        >>> a1.user = u1
        >>> a1 = session.merge(a1)
        >>> session.commit()
        sqlalchemy.orm.exc.FlushError: New instance <Address at 0x1298f50>
        with identity key (<class '__main__.Address'>, (1,)) conflicts with
        persistent instance <Address at 0x12a25d0>

    为什么会这样？因为我们在处理级联时不够小心。将 ``a1.user`` 设置为一个持久对象时，级联作用传递到了 ``User.addresses`` 的反向引用上，导致 ``a1`` 变成了待处理对象（pending），就像我们刚刚添加了它一样。现在 Session 中存在 *两个* ``Address`` 实例::

        >>> a1 = Address()
        >>> a1.user = u1
        >>> a1 in session
        True
        >>> existing_a1 in session
        True
        >>> a1 is existing_a1
        False

    上面的例子中，``a1`` 已经是待处理状态。随后调用的 :meth:`~.Session.merge` 实际上没有起作用。级联行为可以通过 :func:`_orm.relationship` 中的 :paramref:`_orm.relationship.cascade` 参数进行配置，不过在这个场景下就需要去掉 ``User.addresses`` 中的 ``save-update`` 级联 —— 但通常这个行为是非常有用的。本例中更好的解决方式是不要将 ``a1.user`` 设置为目标 Session 中已存在的持久对象。

    另一种选择是，在 :func:`_orm.relationship` 中设置 ``cascade_backrefs=False``，这样通过 ``a1.user = u1`` 赋值就不会导致 ``Address`` 被添加进 Session。

    有关级联行为的更多细节可参见 :ref:`unitofwork_cascades`。

    另一个状态意外的例子::

        >>> a1 = Address(id=existing_a1.id, user_id=u1.id)
        >>> a1.user = None
        >>> a1 = session.merge(a1)
        >>> session.commit()
        sqlalchemy.exc.IntegrityError: (IntegrityError) address.user_id
        may not be NULL

    上面代码中， ``user`` 的赋值优先于外键 ``user_id``，最终 ``None`` 被应用到了 ``user_id``，从而引发了错误。

    大多数与 :meth:`~.Session.merge` 相关的问题都可以通过检查以下几点来定位：

    对象是否过早地被加入到了 Session 中？

    .. sourcecode:: pycon+sql

        >>> a1 = Address(id=existing_a1, user_id=user.id)
        >>> assert a1 not in session
        >>> a1 = session.merge(a1)

    或者，对象是否包含了一些我们不希望存在的状态？检查 ``__dict__`` 是一种快速的方法::

        >>> a1 = Address(id=existing_a1, user_id=user.id)
        >>> a1.user
        >>> a1.__dict__
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x1298d10>,
            'user_id': 1,
            'id': 1,
            'user': None}
        >>> # 我们不希望将 user=None 合并进去，删除它
        >>> del a1.user
        >>> a1 = session.merge(a1)
        >>> # 成功
        >>> session.commit()

.. tab:: 英文

    :meth:`~.Session.merge` is an extremely useful method for many purposes.  However, it deals with the intricate border between objects that are transient/detached and those that are persistent, as well as the automated transference of state. The wide variety of scenarios that can present themselves here often require a more careful approach to the state of objects.   Common problems with merge usually involve some unexpected state regarding the object being passed to :meth:`~.Session.merge`.

    Lets use the canonical example of the User and Address objects::

        class User(Base):
            __tablename__ = "user"

            id = mapped_column(Integer, primary_key=True)
            name = mapped_column(String(50), nullable=False)
            addresses = relationship("Address", backref="user")


        class Address(Base):
            __tablename__ = "address"

            id = mapped_column(Integer, primary_key=True)
            email_address = mapped_column(String(50), nullable=False)
            user_id = mapped_column(Integer, ForeignKey("user.id"), nullable=False)

    Assume a ``User`` object with one ``Address``, already persistent::

        >>> u1 = User(name="ed", addresses=[Address(email_address="ed@ed.com")])
        >>> session.add(u1)
        >>> session.commit()

    We now create ``a1``, an object outside the session, which we'd like to merge on top of the existing ``Address``::

        >>> existing_a1 = u1.addresses[0]
        >>> a1 = Address(id=existing_a1.id)

    A surprise would occur if we said this::

        >>> a1.user = u1
        >>> a1 = session.merge(a1)
        >>> session.commit()
        sqlalchemy.orm.exc.FlushError: New instance <Address at 0x1298f50>
        with identity key (<class '__main__.Address'>, (1,)) conflicts with
        persistent instance <Address at 0x12a25d0>

    Why is that ?   We weren't careful with our cascades.   The assignment of ``a1.user`` to a persistent object cascaded to the backref of ``User.addresses`` and made our ``a1`` object pending, as though we had added it.   Now we have *two* ``Address`` objects in the session::

        >>> a1 = Address()
        >>> a1.user = u1
        >>> a1 in session
        True
        >>> existing_a1 in session
        True
        >>> a1 is existing_a1
        False

    Above, our ``a1`` is already pending in the session. The subsequent :meth:`~.Session.merge` operation essentially does nothing. Cascade can be configured via the :paramref:`_orm.relationship.cascade` option on :func:`_orm.relationship`, although in this case it would mean removing the ``save-update`` cascade from the ``User.addresses`` relationship - and usually, that behavior is extremely convenient.  The solution here would usually be to not assign ``a1.user`` to an object already persistent in the target session.

    The ``cascade_backrefs=False`` option of :func:`_orm.relationship` will also prevent the ``Address`` from being added to the session via the ``a1.user = u1`` assignment.

    Further detail on cascade operation is at :ref:`unitofwork_cascades`.

    Another example of unexpected state::

        >>> a1 = Address(id=existing_a1.id, user_id=u1.id)
        >>> a1.user = None
        >>> a1 = session.merge(a1)
        >>> session.commit()
        sqlalchemy.exc.IntegrityError: (IntegrityError) address.user_id
        may not be NULL

    Above, the assignment of ``user`` takes precedence over the foreign key assignment of ``user_id``, with the end result that ``None`` is applied to ``user_id``, causing a failure.

    Most :meth:`~.Session.merge` issues can be examined by first checking - is the object prematurely in the session ?

    .. sourcecode:: pycon+sql

        >>> a1 = Address(id=existing_a1, user_id=user.id)
        >>> assert a1 not in session
        >>> a1 = session.merge(a1)

    Or is there state on the object that we don't want ?   Examining ``__dict__`` is a quick way to check::

        >>> a1 = Address(id=existing_a1, user_id=user.id)
        >>> a1.user
        >>> a1.__dict__
        {'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x1298d10>,
            'user_id': 1,
            'id': 1,
            'user': None}
        >>> # we don't want user=None merged, remove it
        >>> del a1.user
        >>> a1 = session.merge(a1)
        >>> # success
        >>> session.commit()

清除
---------

Expunging

.. tab:: 中文

    `expunge` 会将对象从 Session 中移除：如果该对象原本是 *持久* 状态（persistent），它会变为 *分离* 状态（detached）；如果原本是 *待处理* 状态（pending），它会变为 *瞬态* 状态（transient）：

    .. sourcecode:: python+sql

        session.expunge(obj1)

    如果要移除所有对象，可调用 :meth:`~.Session.expunge_all` （该方法以前叫做 ``clear()`` ）。

.. tab:: 英文

    Expunge removes an object from the Session, sending persistent instances to the detached state, and pending instances to the transient state:

    .. sourcecode:: python+sql

        session.expunge(obj1)

    To remove all items, call :meth:`~.Session.expunge_all` (this method was formerly known as ``clear()``).

.. _session_expire:

刷新/过期
---------------------

Refreshing / Expiring

.. tab:: 中文

    :term:`过期 <expiring>` 意味着对象属性中持有的数据库持久化数据会被清除。当这些属性下次被访问时，将会发出 SQL 查询，以从数据库中重新加载这些数据。

    当我们讨论“过期”数据时，通常指的是处于 :term:`持久 <persistent>` 状态的对象。例如，若我们如下加载一个对象::

        user = session.scalars(select(User).filter_by(name="user1").limit(1)).first()

    上述 ``User`` 对象处于持久状态，并拥有一系列已加载的属性；若查看其 ``__dict__``，我们可以看到这些状态已加载::

        >>> user.__dict__
        {
          'id': 1, 'name': u'user1',
          '_sa_instance_state': <...>,
        }

    其中 ``id`` 和 ``name`` 对应数据库中的列。而 ``_sa_instance_state`` 是 SQLAlchemy 内部使用的非数据库持久化值（它对应该实例的 :class:`.InstanceState`。虽然这在本节中不是重点，但若我们想访问它，推荐使用 :func:`_sa.inspect` 来获取）。

    此时，我们的 ``User`` 对象中的状态与数据库行一致。但是，当我们通过 :meth:`.Session.expire` 方法让该对象过期时，其状态将被清除::

        >>> session.expire(user)
        >>> user.__dict__
        {'_sa_instance_state': <...>}

    可以看到，虽然内部“状态”依旧存在，但 ``id`` 和 ``name`` 两个列的值已经不见了。如果我们访问其中某个属性，并观察 SQL，会看到以下内容：

    .. sourcecode:: pycon+sql

        >>> print(user.name)
        {execsql}SELECT user.id AS user_id, user.name AS user_name
        FROM user
        WHERE user.id = ?
        (1,)
        {stop}user1

    上面，当访问已过期的属性 ``user.name`` 时，ORM 启动了一次 :term:`懒加载 <lazy load>` 操作，以从数据库中获取该用户的最新状态。之后，``__dict__`` 再次被填充::

        >>> user.__dict__
        {
          'id': 1, 'name': u'user1',
          '_sa_instance_state': <...>,
        }

    .. note::

        虽然我们此处查看了 ``__dict__`` 以便观察 SQLAlchemy 如何处理对象属性，但我们 **不应直接修改** ``__dict__`` 中的内容，至少对于那些由 SQLAlchemy ORM 管理的属性不应如此（对于 SQLAlchemy 不涉及的其它属性则可以）。这是因为 SQLAlchemy 使用 :term:`描述符 <descriptor>` 来追踪对象的变更，而直接修改 ``__dict__`` 会绕过这种机制，从而导致 ORM 无法追踪更改。

    :meth:`~.Session.expire` 和 :meth:`~.Session.refresh` 方法的另一个关键行为是：**所有未刷新的更改都会被丢弃**。也就是说，如果我们修改了某个属性::

        >>> user.name = "user2"

    但随后调用 :meth:`~.Session.expire` 而没有先调用 :meth:`~.Session.flush`，则我们尚未提交的 ``'user2'`` 值会被丢弃::

        >>> session.expire(user)
        >>> user.name
        'user1'

    :meth:`~.Session.expire` 方法可以用来标记某个实例上的所有 ORM 映射属性为“过期”::

        # 让 obj1 的所有 ORM 映射属性过期
        session.expire(obj1)

    它也可以接受一个字符串属性名的列表，用于标记指定的属性为过期::

        # 仅让 obj1.attr1, obj1.attr2 过期
        session.expire(obj1, ["attr1", "attr2"])

    :meth:`.Session.expire_all` 方法则是将 :meth:`.Session.expire` 应用于该 Session 中的所有对象::

        session.expire_all()

    :meth:`~.Session.refresh` 方法的接口与之类似，但它不会将属性标记为过期，而是立即发出 SELECT 查询以加载对象数据::

        # 重新加载 obj1 的所有属性
        session.refresh(obj1)

    :meth:`~.Session.refresh` 同样接受属性名称列表，但与 :meth:`~.Session.expire` 不同的是，它至少要求一个属性是列映射属性::

        # 重新加载 obj1.attr1, obj1.attr2
        session.refresh(obj1, ["attr1", "attr2"])

    .. tip::

        一种更灵活的刷新方式是使用 ORM 的 :ref:`orm_queryguide_populate_existing` 功能。此功能适用于 :term:`2.0 风格 <2.0 style>` 的查询（使用 :func:`_sql.select`），也适用于 :term:`1.x 风格 <1.x style>` 查询中 :class:`_orm.Query` 的 :meth:`_orm.Query.populate_existing` 方法。使用此执行选项，查询结果中的所有 ORM 对象都会用数据库中的最新数据刷新::

            stmt = (
                select(User)
                .execution_options(populate_existing=True)
                .where((User.name.in_(["a", "b", "c"])))
            )
            for user in session.execute(stmt).scalars():
                print(user)  # 查询结果中的对象会被刷新

        详见 :ref:`orm_queryguide_populate_existing`。

.. tab:: 英文

    :term:`Expiring` means that the database-persisted data held inside a series of object attributes is erased, in such a way that when those attributes are next accessed, a SQL query is emitted which will refresh that data from the database.

    When we talk about expiration of data we are usually talking about an object that is in the :term:`persistent` state.   For example, if we load an object as follows::

        user = session.scalars(select(User).filter_by(name="user1").limit(1)).first()

    The above ``User`` object is persistent, and has a series of attributes present; if we were to look inside its ``__dict__``, we'd see that state loaded::

        >>> user.__dict__
        {
          'id': 1, 'name': u'user1',
          '_sa_instance_state': <...>,
        }

    where ``id`` and ``name`` refer to those columns in the database. ``_sa_instance_state`` is a non-database-persisted value used by SQLAlchemy internally (it refers to the :class:`.InstanceState` for the instance. While not directly relevant to this section, if we want to get at it, we should use the :func:`_sa.inspect` function to access it).

    At this point, the state in our ``User`` object matches that of the loaded database row.  But upon expiring the object using a method such as :meth:`.Session.expire`, we see that the state is removed::

        >>> session.expire(user)
        >>> user.__dict__
        {'_sa_instance_state': <...>}

    We see that while the internal "state" still hangs around, the values which correspond to the ``id`` and ``name`` columns are gone.   If we were to access one of these columns and are watching SQL, we'd see this:

    .. sourcecode:: pycon+sql

        >>> print(user.name)
        {execsql}SELECT user.id AS user_id, user.name AS user_name
        FROM user
        WHERE user.id = ?
        (1,)
        {stop}user1

    Above, upon accessing the expired attribute ``user.name``, the ORM initiated a :term:`lazy load` to retrieve the most recent state from the database, by emitting a SELECT for the user row to which this user refers.  Afterwards, the ``__dict__`` is again populated::

        >>> user.__dict__
        {
          'id': 1, 'name': u'user1',
          '_sa_instance_state': <...>,
        }

    .. note::  
      
        While we are peeking inside of ``__dict__`` in order to see a bit of what SQLAlchemy does with object attributes, we **should not modify** the contents of ``__dict__`` directly, at least as far as those attributes which the SQLAlchemy ORM is maintaining (other attributes outside of SQLA's realm are fine).  This is because SQLAlchemy uses :term:`descriptors` in order to track the changes we make to an object, and when we modify ``__dict__`` directly, the ORM won't be able to track that we changed something.

    Another key behavior of both :meth:`~.Session.expire` and :meth:`~.Session.refresh` is that all un-flushed changes on an object are discarded.  That is, if we were to modify an attribute on our ``User``::

        >>> user.name = "user2"

    but then we call :meth:`~.Session.expire` without first calling :meth:`~.Session.flush`, our pending value of ``'user2'`` is discarded::

        >>> session.expire(user)
        >>> user.name
        'user1'

    The :meth:`~.Session.expire` method can be used to mark as "expired" all ORM-mapped attributes for an instance::

        # expire all ORM-mapped attributes on obj1
        session.expire(obj1)

    it can also be passed a list of string attribute names, referring to specific attributes to be marked as expired::

        # expire only attributes obj1.attr1, obj1.attr2
        session.expire(obj1, ["attr1", "attr2"])

    The :meth:`.Session.expire_all` method allows us to essentially call :meth:`.Session.expire` on all objects contained within the :class:`.Session` at once::

        session.expire_all()

    The :meth:`~.Session.refresh` method has a similar interface, but instead of expiring, it emits an immediate SELECT for the object's row immediately::

        # reload all attributes on obj1
        session.refresh(obj1)

    :meth:`~.Session.refresh` also accepts a list of string attribute names, but unlike :meth:`~.Session.expire`, expects at least one name to be that of a column-mapped attribute::

        # reload obj1.attr1, obj1.attr2
        session.refresh(obj1, ["attr1", "attr2"])

    .. tip::

        An alternative method of refreshing which is often more flexible is to use the :ref:`orm_queryguide_populate_existing` feature of the ORM, available for :term:`2.0 style` queries with :func:`_sql.select` as well as from the :meth:`_orm.Query.populate_existing` method of :class:`_orm.Query` within :term:`1.x style` queries.  Using this execution option, all of the ORM objects returned in the result set of the statement will be refreshed with data from the database::

            stmt = (
                select(User)
                .execution_options(populate_existing=True)
                .where((User.name.in_(["a", "b", "c"])))
            )
            for user in session.execute(stmt).scalars():
                print(user)  # will be refreshed for those columns that came back from the query

        See :ref:`orm_queryguide_populate_existing` for further detail.


实际加载的内容
~~~~~~~~~~~~~~~~~~~

What Actually Loads

.. tab:: 中文

    当对象被标记为 :meth:`~.Session.expire` 或通过 :meth:`~.Session.refresh` 加载时，所发出的 SELECT 查询语句会根据多个因素而有所不同，包括：

    * **只有列映射的属性（column-mapped attributes）** 才会触发对过期属性的加载。虽然任何属性（包括通过 :func:`_orm.relationship` 映射的属性）都可以被标记为过期，但访问一个过期的 :func:`_orm.relationship` 属性时，仅会针对该属性本身进行加载，使用的是标准的关系延迟加载（lazy loading）。  
      列属性即使被标记为过期，也不会在访问关系属性时被加载，它们仅会在自身被访问时触发加载。

    * 访问过期的列属性不会导致其关联的 :func:`_orm.relationship` 属性被加载。

    * 关于关系属性，:meth:`~.Session.refresh` 相较于 :meth:`.Session.expire` 对“非列映射属性”的处理更加严格。  
      如果你调用 :meth:`.Session.refresh` 并传入的属性名称列表中 **只包含** 映射为关系的属性名，那么将会引发一个错误。  
      总之，**非 eager loading** 的 :func:`_orm.relationship` 属性不会被包含在 refresh 操作中。

    * 若某个 :func:`_orm.relationship` 属性通过 :paramref:`_orm.relationship.lazy` 参数配置为了“eager loading”，那么在以下两种情况下，:meth:`~.Session.refresh` 会加载它们：
      - 没有指定任何属性名时；
      - 指定的属性名列表中包含了这些属性名。

    * 被配置为 :func:`.deferred` 的属性在过期加载或 refresh 操作中 **通常不会被加载**。  
      此类延迟属性（deferred attributes）只有在被直接访问时，或作为某个“属性组（group）”中的成员之一被访问时，才会单独触发加载。

    * 对于通过 joined-inheritance（联合继承）表结构映射的对象，在访问过期属性时所发出的 SELECT 查询只会涉及那些属性实际未加载的表。  
      例如，如果被标记为过期的列只属于父表或子表的一部分，那么所发出的查询仅会涉及相应的表，加载过程足够智能以仅选择相关表。

    * 如果在 joined-inheritance 的表结构中使用了 :meth:`~.Session.refresh`，则所发出的 SELECT 查询会类似于针对该对象类使用 :meth:`.Session.query` 所发出的查询。  
      通常，这表示会包括映射中配置的所有表。

.. tab:: 英文

    The SELECT statement that's emitted when an object marked with :meth:`~.Session.expire` or loaded with :meth:`~.Session.refresh` varies based on several factors, including:

    * The load of expired attributes is triggered from **column-mapped attributes only**. While any kind of attribute can be marked as expired, including a :func:`_orm.relationship` - mapped attribute, accessing an expired :func:`_orm.relationship` attribute will emit a load only for that attribute, using standard relationship-oriented lazy loading.   Column-oriented attributes, even if expired, will not load as part of this operation, and instead will load when any column-oriented attribute is accessed.

    * :func:`_orm.relationship`- mapped attributes will not load in response to expired column-based attributes being accessed.

    * Regarding relationships, :meth:`~.Session.refresh` is more restrictive than
      :meth:`.Session.expire` with regards to attributes that aren't column-mapped.
      Calling :meth:`.Session.refresh` and passing a list of names that only includes relationship-mapped attributes will actually raise an error. In any case, non-eager-loading :func:`_orm.relationship` attributes will not be included in any refresh operation.

    * :func:`_orm.relationship` attributes configured as "eager loading" via the :paramref:`_orm.relationship.lazy` parameter will load in the case of :meth:`~.Session.refresh`, if either no attribute names are specified, or if their names are included in the list of attributes to be refreshed.

    * Attributes that are configured as :func:`.deferred` will not normally load, during either the expired-attribute load or during a refresh. An unloaded attribute that's :func:`.deferred` instead loads on its own when directly accessed, or if part of a "group" of deferred attributes where an unloaded attribute in that group is accessed.

    * For expired attributes that are loaded on access, a joined-inheritance table mapping will emit a SELECT that typically only includes those tables for which unloaded attributes are present.   The action here is sophisticated enough to load only the parent or child table, for example, if the subset of columns that were originally expired encompass only one or the other of those tables.

    * When :meth:`~.Session.refresh` is used on a joined-inheritance table mapping, the SELECT emitted will resemble that of when :meth:`.Session.query` is used on the target object's class.  This is typically all those tables that are set up as part of the mapping.


何时过期或刷新
~~~~~~~~~~~~~~~~~~~~~~~~~

When to Expire or Refresh

.. tab:: 中文

    :class:`.Session` 会在事务结束时 **自动启用“过期”机制（expiration feature）**。  
    也就是说，每当调用 :meth:`.Session.commit` 或 :meth:`.Session.rollback` 时，当前 :class:`.Session` 中的所有对象都会被标记为过期，其效果等同于调用 :meth:`.Session.expire_all` 方法。

    这么做的原因在于：事务的结束代表着数据库状态的一个“分界点”，此时我们已无法确定数据库中的状态是否仍是我们所了解的状态，因为此时可能有任意数量的其他事务对数据库进行了更改。只有在开启新的事务之后，我们才能重新获得当前数据库的“真实状态”，此时数据库中可能已经发生了多处更改。

    .. admonition:: 事务隔离（Transaction Isolation）

         当然，大多数数据库都支持同时处理多个事务，即使它们涉及相同的数据行。在这种情况下，关系型数据库中的 **隔离（isolation）**机制就会发挥作用。  
        不同数据库对隔离的实现方式差异较大，甚至同一数据库也可以通过所谓的“隔离级别（isolation level）”配置成不同行为模式。  

        因此，:class:`.Session` 并不能完全预测——当我们第二次发出同一个 SELECT 语句时，返回的结果是否仍是我们之前拥有的那一份，或是否已经是新的数据。  

        基于这个限制，Session 的默认行为是： **在同一个事务范围内，除非明确知道某个行被修改了，否则不会主动刷新已有数据，除非你明确要求刷新。**

    :meth:`.Session.expire` 和 :meth:`.Session.refresh` 方法用于在 **明确知道数据可能已过时** 的情况下，强制对象从数据库中重新加载其数据。常见的使用场景包括：

    * 在事务内执行了 **不属于 ORM 的 SQL 语句** ，比如通过 :meth:`.Session.execute` 执行了 :meth:`_schema.Table.update` 语句；

    * 应用程序尝试获取 **在并发事务中已知被更改** 的数据，同时也明确知道当前隔离级别允许我们看到这部分数据。

    第二种情况有一个非常关键的前提：“也 **必须明确知道** 当前的隔离规则允许这些更改的数据对当前连接是可见的”。  
    换句话说， **不能默认认为其他连接中发生的 UPDATE 已经在当前连接中可见** ；在许多数据库隔离级别下，这种更新 **不可见** 。  

    因此，如果你打算使用 :meth:`.Session.expire` 或 :meth:`.Session.refresh` 来查看多个事务间的数据状态， **理解当前数据库的隔离级别行为至关重要** 。

    .. seealso::

        * :meth:`.Session.expire`

        * :meth:`.Session.expire_all`

        * :meth:`.Session.refresh`

        * :ref:`orm_queryguide_populate_existing`  
          - 允许任何 ORM 查询像正常加载对象那样重新加载数据，会将 Identity Map 中所有匹配的对象与 SELECT 结果进行刷新。

        * :term:`isolation`  
          - 关于数据库事务隔离的术语解释，并附带维基百科等进一步阅读链接。

        * `The SQLAlchemy Session In-Depth <https://techspot.zzzeek.org/2012/11/14/pycon-canada-the-sqlalchemy-session-in-depth/>`_  
          - 一场关于 SQLAlchemy 中 Session 生命周期的深入讲解，包括数据过期机制的视频与幻灯片资源。

.. tab:: 英文

    The :class:`.Session` uses the expiration feature automatically whenever the transaction referred to by the session ends.  Meaning, whenever :meth:`.Session.commit` or :meth:`.Session.rollback` is called, all objects within the :class:`.Session` are expired, using a feature equivalent to that of the :meth:`.Session.expire_all` method.   The rationale is that the end of a transaction is a demarcating point at which there is no more context available in order to know what the current state of the database is, as any number of other transactions may be affecting it.  Only when a new transaction starts can we again have access to the current state of the database, at which point any number of changes may have occurred.

    .. sidebar:: Transaction Isolation

        Of course, most databases are capable of handling multiple transactions at once, even involving the same rows of data.   When a relational database handles multiple transactions involving the same tables or rows, this is when the :term:`isolation` aspect of the database comes into play.  The isolation behavior of different databases varies considerably and even on a single database can be configured to behave in different ways (via the so-called :term:`isolation level` setting).  In that sense, the :class:`.Session` can't fully predict when the same SELECT statement, emitted a second time, will definitely return the data we already have, or will return new data. So as a best guess, it assumes that within the scope of a transaction, unless it is known that a SQL expression has been emitted to modify a particular row, there's no need to refresh a row unless explicitly told to do so.

    The :meth:`.Session.expire` and :meth:`.Session.refresh` methods are used in those cases when one wants to force an object to re-load its data from the database, in those cases when it is known that the current state of data is possibly stale.  Reasons for this might include:

    * some SQL has been emitted within the transaction outside of the scope of the ORM's object handling, such as if a :meth:`_schema.Table.update` construct were emitted using the :meth:`.Session.execute` method;

    * if the application is attempting to acquire data that is known to have been modified in a concurrent transaction, and it is also known that the isolation rules in effect allow this data to be visible.

    The second bullet has the important caveat that "it is also known that the isolation rules in effec allow this data to be visible."  This means that it cannot be assumed that a UPDATE that happened on another database connection will yet be visible her locally; in many cases, it will not.  This is why if one wishes to us :meth:`.Session.expire` or :meth:`.Session.refresh` in order to view data between ongoin transactions, an understanding of the isolation behavior in effect is essential.

    .. seealso::

        :meth:`.Session.expire`

        :meth:`.Session.expire_all`

        :meth:`.Session.refresh`

        :ref:`orm_queryguide_populate_existing` - allows any ORM query to refresh objects as they would be loaded normally, refreshing all matching objects in the identity map against the results of a SELECT statement.

        :term:`isolation` - glossary explanation of isolation which includes links to Wikipedia.

        `The SQLAlchemy Session In-Depth <https://techspot.zzzeek.org/2012/11/14/pycon-canada-the-sqlalchemy-session-in-depth/>`_ a video + slides with an in-depth discussion of the object lifecycle including the role of data expiration.
