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

.. tab:: 英文

The actual state of any mapped object can be viewed at any time using
the :func:`_sa.inspect` function on a mapped instance; this function will
return the corresponding :class:`.InstanceState` object which manages the
internal ORM state for the object.  :class:`.InstanceState` provides, among
other accessors, boolean attributes indicating the persistence state
of the object, including:

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

  :ref:`orm_mapper_inspection_instancestate` - further examples of
  :class:`.InstanceState`

.. _session_attributes:

会话属性
------------------

Session Attributes

.. tab:: 中文

.. tab:: 英文

The :class:`~sqlalchemy.orm.session.Session` itself acts somewhat like a
set-like collection. All items present may be accessed using the iterator
interface::

    for obj in session:
        print(obj)

And presence may be tested for using regular "contains" semantics::

    if obj in session:
        print("Object is present")

The session is also keeping track of all newly created (i.e. pending) objects,
all objects which have had changes since they were last loaded or saved (i.e.
"dirty"), and everything that's been marked as deleted::

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

(Documentation: :attr:`.Session.new`, :attr:`.Session.dirty`,
:attr:`.Session.deleted`, :attr:`.Session.identity_map`).


.. _session_referencing_behavior:

会话引用行为
----------------------------

Session Referencing Behavior

.. tab:: 中文

.. tab:: 英文

Objects within the session are *weakly referenced*. This
means that when they are dereferenced in the outside application, they fall
out of scope from within the :class:`~sqlalchemy.orm.session.Session` as well
and are subject to garbage collection by the Python interpreter. The
exceptions to this include objects which are pending, objects which are marked
as deleted, or persistent objects which have pending changes on them. After a
full flush, these collections are all empty, and all objects are again weakly
referenced.

To cause objects in the :class:`.Session` to remain strongly
referenced, usually a simple approach is all that's needed.  Examples
of externally managed strong-referencing behavior include loading
objects into a local dictionary keyed to their primary key, or into
lists or sets for the span of time that they need to remain
referenced. These collections can be associated with a
:class:`.Session`, if desired, by placing them into the
:attr:`.Session.info` dictionary.

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

Above, we intercept the :meth:`.SessionEvents.pending_to_persistent`,
:meth:`.SessionEvents.detached_to_persistent`,
:meth:`.SessionEvents.deleted_to_persistent` and
:meth:`.SessionEvents.loaded_as_persistent` event hooks in order to intercept
objects as they enter the :term:`persistent` transition, and the
:meth:`.SessionEvents.persistent_to_detached` and
:meth:`.SessionEvents.persistent_to_deleted` hooks to intercept
objects as they leave the persistent state.

The above function may be called for any :class:`.Session` in order to
provide strong-referencing behavior on a per-:class:`.Session` basis::

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

.. tab:: 英文

:meth:`~.Session.merge` transfers state from an
outside object into a new or already existing instance within a session.   It
also reconciles the incoming data against the state of the
database, producing a history stream which will be applied towards the next
flush, or alternatively can be made to produce a simple "transfer" of
state without producing change history or accessing the database.  Usage is as follows::

    merged_object = session.merge(existing_object)

When given an instance, it follows these steps:

* It examines the primary key of the instance. If it's present, it attempts
  to locate that instance in the local identity map.   If the ``load=True``
  flag is left at its default, it also checks the database for this primary
  key if not located locally.
* If the given instance has no primary key, or if no instance can be found
  with the primary key given, a new instance is created.
* The state of the given instance is then copied onto the located/newly created
  instance. For attribute values which are present on the source instance, the
  value is transferred to the target instance. For attribute values that aren't
  present on the source instance, the corresponding attribute on the target
  instance is :term:`expired` from memory, which discards any locally
  present value from the target instance for that attribute, but no
  direct modification is made to the database-persisted value for that
  attribute.

  If the ``load=True`` flag is left at its default,
  this copy process emits events and will load the target object's
  unloaded collections for each attribute present on the source object,
  so that the incoming state can be reconciled against what's
  present in the database.  If ``load``
  is passed as ``False``, the incoming data is "stamped" directly without
  producing any history.
* The operation is cascaded to related objects and collections, as
  indicated by the ``merge`` cascade (see :ref:`unitofwork_cascades`).
* The new instance is returned.

With :meth:`~.Session.merge`, the given "source"
instance is not modified nor is it associated with the target :class:`.Session`,
and remains available to be merged with any number of other :class:`.Session`
objects.  :meth:`~.Session.merge` is useful for
taking the state of any kind of object structure without regard for its
origins or current session associations and copying its state into a
new session. Here's some examples:

* An application which reads an object structure from a file and wishes to
  save it to the database might parse the file, build up the
  structure, and then use
  :meth:`~.Session.merge` to save it
  to the database, ensuring that the data within the file is
  used to formulate the primary key of each element of the
  structure. Later, when the file has changed, the same
  process can be re-run, producing a slightly different
  object structure, which can then be ``merged`` in again,
  and the :class:`~sqlalchemy.orm.session.Session` will
  automatically update the database to reflect those
  changes, loading each object from the database by primary key and
  then updating its state with the new state given.

* An application is storing objects in an in-memory cache, shared by
  many :class:`.Session` objects simultaneously.   :meth:`~.Session.merge`
  is used each time an object is retrieved from the cache to create
  a local copy of it in each :class:`.Session` which requests it.
  The cached object remains detached; only its state is moved into
  copies of itself that are local to individual :class:`~.Session`
  objects.

  In the caching use case, it's common to use the ``load=False``
  flag to remove the overhead of reconciling the object's state
  with the database.   There's also a "bulk" version of
  :meth:`~.Session.merge` called :meth:`_query.Query.merge_result`
  that was designed to work with cache-extended :class:`_query.Query`
  objects - see the section :ref:`examples_caching`.

* An application wants to transfer the state of a series of objects
  into a :class:`.Session` maintained by a worker thread or other
  concurrent system.  :meth:`~.Session.merge` makes a copy of each object
  to be placed into this new :class:`.Session`.  At the end of the operation,
  the parent thread/process maintains the objects it started with,
  and the thread/worker can proceed with local copies of those objects.

  In the "transfer between threads/processes" use case, the application
  may want to use the ``load=False`` flag as well to avoid overhead and
  redundant SQL queries as the data is transferred.

合并提示
~~~~~~~~~~

Merge Tips

.. tab:: 中文

.. tab:: 英文

:meth:`~.Session.merge` is an extremely useful method for many purposes.  However,
it deals with the intricate border between objects that are transient/detached and
those that are persistent, as well as the automated transference of state.
The wide variety of scenarios that can present themselves here often require a
more careful approach to the state of objects.   Common problems with merge usually involve
some unexpected state regarding the object being passed to :meth:`~.Session.merge`.

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

We now create ``a1``, an object outside the session, which we'd like
to merge on top of the existing ``Address``::

    >>> existing_a1 = u1.addresses[0]
    >>> a1 = Address(id=existing_a1.id)

A surprise would occur if we said this::

    >>> a1.user = u1
    >>> a1 = session.merge(a1)
    >>> session.commit()
    sqlalchemy.orm.exc.FlushError: New instance <Address at 0x1298f50>
    with identity key (<class '__main__.Address'>, (1,)) conflicts with
    persistent instance <Address at 0x12a25d0>

Why is that ?   We weren't careful with our cascades.   The assignment
of ``a1.user`` to a persistent object cascaded to the backref of ``User.addresses``
and made our ``a1`` object pending, as though we had added it.   Now we have
*two* ``Address`` objects in the session::

    >>> a1 = Address()
    >>> a1.user = u1
    >>> a1 in session
    True
    >>> existing_a1 in session
    True
    >>> a1 is existing_a1
    False

Above, our ``a1`` is already pending in the session. The
subsequent :meth:`~.Session.merge` operation essentially
does nothing. Cascade can be configured via the :paramref:`_orm.relationship.cascade`
option on :func:`_orm.relationship`, although in this case it
would mean removing the ``save-update`` cascade from the
``User.addresses`` relationship - and usually, that behavior
is extremely convenient.  The solution here would usually be to not assign
``a1.user`` to an object already persistent in the target
session.

The ``cascade_backrefs=False`` option of :func:`_orm.relationship`
will also prevent the ``Address`` from
being added to the session via the ``a1.user = u1`` assignment.

Further detail on cascade operation is at :ref:`unitofwork_cascades`.

Another example of unexpected state::

    >>> a1 = Address(id=existing_a1.id, user_id=u1.id)
    >>> a1.user = None
    >>> a1 = session.merge(a1)
    >>> session.commit()
    sqlalchemy.exc.IntegrityError: (IntegrityError) address.user_id
    may not be NULL

Above, the assignment of ``user`` takes precedence over the foreign key
assignment of ``user_id``, with the end result that ``None`` is applied
to ``user_id``, causing a failure.

Most :meth:`~.Session.merge` issues can be examined by first checking -
is the object prematurely in the session ?

.. sourcecode:: pycon+sql

    >>> a1 = Address(id=existing_a1, user_id=user.id)
    >>> assert a1 not in session
    >>> a1 = session.merge(a1)

Or is there state on the object that we don't want ?   Examining ``__dict__``
is a quick way to check::

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

.. tab:: 英文

Expunge removes an object from the Session, sending persistent instances to
the detached state, and pending instances to the transient state:

.. sourcecode:: python+sql

    session.expunge(obj1)

To remove all items, call :meth:`~.Session.expunge_all`
(this method was formerly known as ``clear()``).

.. _session_expire:

刷新/过期
---------------------

Refreshing / Expiring

.. tab:: 中文

.. tab:: 英文

:term:`Expiring` means that the database-persisted data held inside a series
of object attributes is erased, in such a way that when those attributes
are next accessed, a SQL query is emitted which will refresh that data from
the database.

When we talk about expiration of data we are usually talking about an object
that is in the :term:`persistent` state.   For example, if we load an object
as follows::

    user = session.scalars(select(User).filter_by(name="user1").limit(1)).first()

The above ``User`` object is persistent, and has a series of attributes
present; if we were to look inside its ``__dict__``, we'd see that state
loaded::

    >>> user.__dict__
    {
      'id': 1, 'name': u'user1',
      '_sa_instance_state': <...>,
    }

where ``id`` and ``name`` refer to those columns in the database.
``_sa_instance_state`` is a non-database-persisted value used by SQLAlchemy
internally (it refers to the :class:`.InstanceState` for the instance.
While not directly relevant to this section, if we want to get at it,
we should use the :func:`_sa.inspect` function to access it).

At this point, the state in our ``User`` object matches that of the loaded
database row.  But upon expiring the object using a method such as
:meth:`.Session.expire`, we see that the state is removed::

    >>> session.expire(user)
    >>> user.__dict__
    {'_sa_instance_state': <...>}

We see that while the internal "state" still hangs around, the values which
correspond to the ``id`` and ``name`` columns are gone.   If we were to access
one of these columns and are watching SQL, we'd see this:

.. sourcecode:: pycon+sql

    >>> print(user.name)
    {execsql}SELECT user.id AS user_id, user.name AS user_name
    FROM user
    WHERE user.id = ?
    (1,)
    {stop}user1

Above, upon accessing the expired attribute ``user.name``, the ORM initiated
a :term:`lazy load` to retrieve the most recent state from the database,
by emitting a SELECT for the user row to which this user refers.  Afterwards,
the ``__dict__`` is again populated::

    >>> user.__dict__
    {
      'id': 1, 'name': u'user1',
      '_sa_instance_state': <...>,
    }

.. note::  While we are peeking inside of ``__dict__`` in order to see a bit
   of what SQLAlchemy does with object attributes, we **should not modify**
   the contents of ``__dict__`` directly, at least as far as those attributes
   which the SQLAlchemy ORM is maintaining (other attributes outside of SQLA's
   realm are fine).  This is because SQLAlchemy uses :term:`descriptors` in
   order to track the changes we make to an object, and when we modify ``__dict__``
   directly, the ORM won't be able to track that we changed something.

Another key behavior of both :meth:`~.Session.expire` and :meth:`~.Session.refresh`
is that all un-flushed changes on an object are discarded.  That is,
if we were to modify an attribute on our ``User``::

    >>> user.name = "user2"

but then we call :meth:`~.Session.expire` without first calling :meth:`~.Session.flush`,
our pending value of ``'user2'`` is discarded::

    >>> session.expire(user)
    >>> user.name
    'user1'

The :meth:`~.Session.expire` method can be used to mark as "expired" all ORM-mapped
attributes for an instance::

    # expire all ORM-mapped attributes on obj1
    session.expire(obj1)

it can also be passed a list of string attribute names, referring to specific
attributes to be marked as expired::

    # expire only attributes obj1.attr1, obj1.attr2
    session.expire(obj1, ["attr1", "attr2"])

The :meth:`.Session.expire_all` method allows us to essentially call
:meth:`.Session.expire` on all objects contained within the :class:`.Session`
at once::

    session.expire_all()

The :meth:`~.Session.refresh` method has a similar interface, but instead
of expiring, it emits an immediate SELECT for the object's row immediately::

    # reload all attributes on obj1
    session.refresh(obj1)

:meth:`~.Session.refresh` also accepts a list of string attribute names,
but unlike :meth:`~.Session.expire`, expects at least one name to
be that of a column-mapped attribute::

    # reload obj1.attr1, obj1.attr2
    session.refresh(obj1, ["attr1", "attr2"])

.. tip::

    An alternative method of refreshing which is often more flexible is to
    use the :ref:`orm_queryguide_populate_existing` feature of the ORM,
    available for :term:`2.0 style` queries with :func:`_sql.select` as well
    as from the :meth:`_orm.Query.populate_existing` method of :class:`_orm.Query`
    within :term:`1.x style` queries.  Using this execution option,
    all of the ORM objects returned in the result set of the statement
    will be refreshed with data from the database::

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

.. tab:: 英文

The SELECT statement that's emitted when an object marked with :meth:`~.Session.expire`
or loaded with :meth:`~.Session.refresh` varies based on several factors, including:

* The load of expired attributes is triggered from **column-mapped attributes only**.
  While any kind of attribute can be marked as expired, including a
  :func:`_orm.relationship` - mapped attribute, accessing an expired :func:`_orm.relationship`
  attribute will emit a load only for that attribute, using standard
  relationship-oriented lazy loading.   Column-oriented attributes, even if
  expired, will not load as part of this operation, and instead will load when
  any column-oriented attribute is accessed.

* :func:`_orm.relationship`- mapped attributes will not load in response to
  expired column-based attributes being accessed.

* Regarding relationships, :meth:`~.Session.refresh` is more restrictive than
  :meth:`.Session.expire` with regards to attributes that aren't column-mapped.
  Calling :meth:`.Session.refresh` and passing a list of names that only includes
  relationship-mapped attributes will actually raise an error.
  In any case, non-eager-loading :func:`_orm.relationship` attributes will not be
  included in any refresh operation.

* :func:`_orm.relationship` attributes configured as "eager loading" via the
  :paramref:`_orm.relationship.lazy` parameter will load in the case of
  :meth:`~.Session.refresh`, if either no attribute names are specified, or
  if their names are included in the list of attributes to be
  refreshed.

* Attributes that are configured as :func:`.deferred` will not normally load,
  during either the expired-attribute load or during a refresh.
  An unloaded attribute that's :func:`.deferred` instead loads on its own when directly
  accessed, or if part of a "group" of deferred attributes where an unloaded
  attribute in that group is accessed.

* For expired attributes that are loaded on access, a joined-inheritance table
  mapping will emit a SELECT that typically only includes those tables for which
  unloaded attributes are present.   The action here is sophisticated enough
  to load only the parent or child table, for example, if the subset of columns
  that were originally expired encompass only one or the other of those tables.

* When :meth:`~.Session.refresh` is used on a joined-inheritance table mapping,
  the SELECT emitted will resemble that of when :meth:`.Session.query` is
  used on the target object's class.  This is typically all those tables that
  are set up as part of the mapping.


何时过期或刷新
~~~~~~~~~~~~~~~~~~~~~~~~~

When to Expire or Refresh

.. tab:: 中文

.. tab:: 英文

The :class:`.Session` uses the expiration feature automatically whenever
the transaction referred to by the session ends.  Meaning, whenever :meth:`.Session.commit`
or :meth:`.Session.rollback` is called, all objects within the :class:`.Session`
are expired, using a feature equivalent to that of the :meth:`.Session.expire_all`
method.   The rationale is that the end of a transaction is a
demarcating point at which there is no more context available in order to know
what the current state of the database is, as any number of other transactions
may be affecting it.  Only when a new transaction starts can we again have access
to the current state of the database, at which point any number of changes
may have occurred.

.. sidebar:: Transaction Isolation

    Of course, most databases are capable of handling
    multiple transactions at once, even involving the same rows of data.   When
    a relational database handles multiple transactions involving the same
    tables or rows, this is when the :term:`isolation` aspect of the database comes
    into play.  The isolation behavior of different databases varies considerably
    and even on a single database can be configured to behave in different ways
    (via the so-called :term:`isolation level` setting).  In that sense, the :class:`.Session`
    can't fully predict when the same SELECT statement, emitted a second time,
    will definitely return the data we already have, or will return new data.
    So as a best guess, it assumes that within the scope of a transaction, unless
    it is known that a SQL expression has been emitted to modify a particular row,
    there's no need to refresh a row unless explicitly told to do so.

The :meth:`.Session.expire` and :meth:`.Session.refresh` methods are used in
those cases when one wants to force an object to re-load its data from the
database, in those cases when it is known that the current state of data
is possibly stale.  Reasons for this might include:

* some SQL has been emitted within the transaction outside of the
  scope of the ORM's object handling, such as if a :meth:`_schema.Table.update` construct
  were emitted using the :meth:`.Session.execute` method;

* if the application
  is attempting to acquire data that is known to have been modified in a
  concurrent transaction, and it is also known that the isolation rules in effect
  allow this data to be visible.

The second bullet has the important caveat that "it is also known that the isolation rules in effect
allow this data to be visible."  This means that it cannot be assumed that an
UPDATE that happened on another database connection will yet be visible here
locally; in many cases, it will not.  This is why if one wishes to use
:meth:`.Session.expire` or :meth:`.Session.refresh` in order to view data between ongoing
transactions, an understanding of the isolation behavior in effect is essential.

.. seealso::

    :meth:`.Session.expire`

    :meth:`.Session.expire_all`

    :meth:`.Session.refresh`

    :ref:`orm_queryguide_populate_existing` - allows any ORM query
    to refresh objects as they would be loaded normally, refreshing
    all matching objects in the identity map against the results of a
    SELECT statement.

    :term:`isolation` - glossary explanation of isolation which includes links
    to Wikipedia.

    `The SQLAlchemy Session In-Depth <https://techspot.zzzeek.org/2012/11/14/pycon-canada-the-sqlalchemy-session-in-depth/>`_ - a video + slides with an in-depth discussion of the object
    lifecycle including the role of data expiration.
