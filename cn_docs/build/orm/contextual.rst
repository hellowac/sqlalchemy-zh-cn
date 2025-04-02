.. _unitofwork_contextual:

上下文/线程本地会话
================================

Contextual/Thread-local Sessions

.. tab:: 中文

    回顾 :ref:`session_faq_whentocreate` 部分，介绍了“会话范围”的概念，重点是 Web 应用程序和将 :class:`.Session` 的范围链接到 Web 请求的做法。大多数现代 Web 框架都包含集成工具，以便可以自动管理 :class:`.Session` 的范围，应在可用时使用这些工具。

    SQLAlchemy 包括自己的帮助对象，它有助于建立用户定义的 :class:`.Session` 范围。第三方集成系统也使用它来帮助构建其集成方案。

    该对象是 :class:`.scoped_session` 对象，代表 :class:`.Session` 对象的 **注册表** 。如果你不熟悉注册表模式，可以在 `企业架构模式 <https://martinfowler.com/eaaCatalog/registry.html>`_ 中找到一个很好的介绍。

    .. warning::

        :class:`.scoped_session` 注册表默认使用 Python 的 ``threading.local()``
        来跟踪 :class:`_orm.Session` 实例。 **这不一定与所有应用服务器兼容** ，特别是那些使用 greenlets 或其他替代形式的并发控制的应用服务器，在中高并发场景中使用时可能会导致竞争条件（例如随机发生的失败）。
        请阅读 :ref:`unitofwork_contextual_threadlocal` 和
        :ref:`session_lifespan` 以更全面地了解使用 ``threading.local()`` 跟踪 :class:`_orm.Session` 对象的影响，并在使用基于非传统线程的应用服务器时考虑更明确的范围划分方法。

    .. note::

        :class:`.scoped_session` 对象是许多 SQLAlchemy 应用程序使用的非常流行和有用的对象。然而，重要的是要注意，它仅仅是 :class:`.Session` 管理问题的一种方法。如果你是 SQLAlchemy 的新手，特别是如果“线程本地变量”这个术语对你来说很陌生，我们建议你首先熟悉一个现成的集成系统，例如 `Flask-SQLAlchemy <https://pypi.org/project/Flask-SQLAlchemy/>`_ 或 `zope.sqlalchemy <https://pypi.org/project/zope.sqlalchemy>`_。

    通过调用 :class:`.scoped_session` 并传递一个可以创建新的 :class:`.Session` 对象的 **工厂** 来构建 :class:`.scoped_session`。工厂只是某个被调用时会生成新对象的东西，对于 :class:`.Session`，最常见的工厂是本节前面介绍的 :class:`.sessionmaker`。下面我们展示这种用法::

        >>> from sqlalchemy.orm import scoped_session
        >>> from sqlalchemy.orm import sessionmaker

        >>> session_factory = sessionmaker(bind=some_engine)
        >>> Session = scoped_session(session_factory)

    我们创建的 :class:`.scoped_session` 对象现在将调用 :class:`.sessionmaker` 当我们“调用”注册表时::

        >>> some_session = Session()

    上面的 ``some_session`` 是 :class:`.Session` 的一个实例，我们现在可以用它来与数据库对话。同样的 :class:`.Session` 也存在于我们创建的 :class:`.scoped_session` 注册表中。如果我们第二次调用注册表，我们会得到 **相同** 的 :class:`.Session`::

        >>> some_other_session = Session()
        >>> some_session is some_other_session
        True

    这种模式允许应用程序的不同部分调用全局 :class:`.scoped_session`，以便所有这些区域可以共享同一个会话，而不需要显式传递它。我们在注册表中建立的 :class:`.Session` 将保持存在，直到我们显式告诉注册表处理它，通过调用 :meth:`.scoped_session.remove`::

        >>> Session.remove()

    :meth:`.scoped_session.remove` 方法首先调用当前 :class:`.Session` 上的 :meth:`.Session.close`，其效果是首先释放 :class:`.Session` 拥有的任何连接/事务性资源，然后丢弃 :class:`.Session` 本身。“释放”在这里意味着连接返回到其连接池，任何事务状态都回滚，最终使用底层 DBAPI 连接的 ``rollback()`` 方法。

    此时，:class:`.scoped_session` 对象是“空”的，并将在再次调用时创建一个 **新的** :class:`.Session`。如下所示，这不是我们之前拥有的同一个 :class:`.Session`::

        >>> new_session = Session()
        >>> new_session is some_session
        False

    上面的步骤系列简要说明了“注册表”模式的概念。掌握这一基本概念后，我们可以讨论此模式的一些细节。

.. tab:: 英文

    Recall from the section :ref:`session_faq_whentocreate`, the concept of
    "session scopes" was introduced, with an emphasis on web applications
    and the practice of linking the scope of a :class:`.Session` with that
    of a web request.   Most modern web frameworks include integration tools
    so that the scope of the :class:`.Session` can be managed automatically,
    and these tools should be used as they are available.

    SQLAlchemy includes its own helper object, which helps with the establishment
    of user-defined :class:`.Session` scopes.  It is also used by third-party
    integration systems to help construct their integration schemes.

    The object is the :class:`.scoped_session` object, and it represents a
    **registry** of :class:`.Session` objects.  If you're not familiar with the
    registry pattern, a good introduction can be found in `Patterns of Enterprise
    Architecture <https://martinfowler.com/eaaCatalog/registry.html>`_.

    .. warning::

        The :class:`.scoped_session` registry by default uses a Python
        ``threading.local()``
        in order to track :class:`_orm.Session` instances.   **This is not
        necessarily compatible with all application servers**, particularly those
        which make use of greenlets or other alternative forms of concurrency
        control, which may lead to race conditions (e.g. randomly occurring
        failures) when used in moderate to high concurrency scenarios.
        Please read :ref:`unitofwork_contextual_threadlocal` and
        :ref:`session_lifespan` below to more fully understand the implications
        of using ``threading.local()`` to track :class:`_orm.Session` objects
        and consider more explicit means of scoping when using application servers
        which are not based on traditional threads.

    .. note::

        The :class:`.scoped_session` object is a very popular and useful object
        used by many SQLAlchemy applications.  However, it is important to note
        that it presents **only one approach** to the issue of :class:`.Session`
        management.  If you're new to SQLAlchemy, and especially if the
        term "thread-local variable" seems strange to you, we recommend that
        if possible you familiarize first with an off-the-shelf integration
        system such as `Flask-SQLAlchemy <https://pypi.org/project/Flask-SQLAlchemy/>`_
        or `zope.sqlalchemy <https://pypi.org/project/zope.sqlalchemy>`_.

    A :class:`.scoped_session` is constructed by calling it, passing it a
    **factory** which can create new :class:`.Session` objects.   A factory
    is just something that produces a new object when called, and in the
    case of :class:`.Session`, the most common factory is the :class:`.sessionmaker`,
    introduced earlier in this section.  Below we illustrate this usage::

        >>> from sqlalchemy.orm import scoped_session
        >>> from sqlalchemy.orm import sessionmaker

        >>> session_factory = sessionmaker(bind=some_engine)
        >>> Session = scoped_session(session_factory)

    The :class:`.scoped_session` object we've created will now call upon the
    :class:`.sessionmaker` when we "call" the registry::

        >>> some_session = Session()

    Above, ``some_session`` is an instance of :class:`.Session`, which we
    can now use to talk to the database.   This same :class:`.Session` is also
    present within the :class:`.scoped_session` registry we've created.   If
    we call upon the registry a second time, we get back the **same** :class:`.Session`::

        >>> some_other_session = Session()
        >>> some_session is some_other_session
        True

    This pattern allows disparate sections of the application to call upon a global
    :class:`.scoped_session`, so that all those areas may share the same session
    without the need to pass it explicitly.   The :class:`.Session` we've established
    in our registry will remain, until we explicitly tell our registry to dispose of it,
    by calling :meth:`.scoped_session.remove`::

        >>> Session.remove()

    The :meth:`.scoped_session.remove` method first calls :meth:`.Session.close` on
    the current :class:`.Session`, which has the effect of releasing any connection/transactional
    resources owned by the :class:`.Session` first, then discarding the :class:`.Session`
    itself.  "Releasing" here means that connections are returned to their connection pool and any transactional state is rolled back, ultimately using the ``rollback()`` method of the underlying DBAPI connection.

    At this point, the :class:`.scoped_session` object is "empty", and will create
    a **new** :class:`.Session` when called again.  As illustrated below, this
    is not the same :class:`.Session` we had before::

        >>> new_session = Session()
        >>> new_session is some_session
        False

    The above series of steps illustrates the idea of the "registry" pattern in a
    nutshell.  With that basic idea in hand, we can discuss some of the details
    of how this pattern proceeds.

隐式方法访问
----------------------

Implicit Method Access

.. tab:: 中文

.. tab:: 英文

The job of the :class:`.scoped_session` is simple; hold onto a :class:`.Session`
for all who ask for it.  As a means of producing more transparent access to this
:class:`.Session`, the :class:`.scoped_session` also includes **proxy behavior**,
meaning that the registry itself can be treated just like a :class:`.Session`
directly; when methods are called on this object, they are **proxied** to the
underlying :class:`.Session` being maintained by the registry::

    Session = scoped_session(some_factory)

    # equivalent to:
    #
    # session = Session()
    # print(session.scalars(select(MyClass)).all())
    #
    print(Session.scalars(select(MyClass)).all())

The above code accomplishes the same task as that of acquiring the current
:class:`.Session` by calling upon the registry, then using that :class:`.Session`.

.. _unitofwork_contextual_threadlocal:

线程本地范围
------------------

Thread-Local Scope

.. tab:: 中文

.. tab:: 英文

Users who are familiar with multithreaded programming will note that representing
anything as a global variable is usually a bad idea, as it implies that the
global object will be accessed by many threads concurrently.   The :class:`.Session`
object is entirely designed to be used in a **non-concurrent** fashion, which
in terms of multithreading means "only in one thread at a time".   So our
above example of :class:`.scoped_session` usage, where the same :class:`.Session`
object is maintained across multiple calls, suggests that some process needs
to be in place such that multiple calls across many threads don't actually get
a handle to the same session.   We call this notion **thread local storage**,
which means, a special object is used that will maintain a distinct object
per each application thread.   Python provides this via the
`threading.local() <https://docs.python.org/library/threading.html#threading.local>`_
construct.  The :class:`.scoped_session` object by default uses this object
as storage, so that a single :class:`.Session` is maintained for all who call
upon the :class:`.scoped_session` registry, but only within the scope of a single
thread.   Callers who call upon the registry in a different thread get a
:class:`.Session` instance that is local to that other thread.

Using this technique, the :class:`.scoped_session` provides a quick and relatively
simple (if one is familiar with thread-local storage) way of providing
a single, global object in an application that is safe to be called upon
from multiple threads.

The :meth:`.scoped_session.remove` method, as always, removes the current
:class:`.Session` associated with the thread, if any.  However, one advantage of the
``threading.local()`` object is that if the application thread itself ends, the
"storage" for that thread is also garbage collected.  So it is in fact "safe" to
use thread local scope with an application that spawns and tears down threads,
without the need to call :meth:`.scoped_session.remove`.  However, the scope
of transactions themselves, i.e. ending them via :meth:`.Session.commit` or
:meth:`.Session.rollback`, will usually still be something that must be explicitly
arranged for at the appropriate time, unless the application actually ties the
lifespan of a thread to the lifespan of a transaction.

.. _session_lifespan:

在 Web 应用程序中使用线程本地范围
----------------------------------------------

Using Thread-Local Scope with Web Applications

.. tab:: 中文

.. tab:: 英文

As discussed in the section :ref:`session_faq_whentocreate`, a web application
is architected around the concept of a **web request**, and integrating
such an application with the :class:`.Session` usually implies that the :class:`.Session`
will be associated with that request.  As it turns out, most Python web frameworks,
with notable exceptions such as the asynchronous frameworks Twisted and
Tornado, use threads in a simple way, such that a particular web request is received,
processed, and completed within the scope of a single *worker thread*.  When
the request ends, the worker thread is released to a pool of workers where it
is available to handle another request.

This simple correspondence of web request and thread means that to associate a
:class:`.Session` with a thread implies it is also associated with the web request
running within that thread, and vice versa, provided that the :class:`.Session` is
created only after the web request begins and torn down just before the web request ends.
So it is a common practice to use :class:`.scoped_session` as a quick way
to integrate the :class:`.Session` with a web application.  The sequence
diagram below illustrates this flow:

.. sourcecode:: text

    Web Server          Web Framework        SQLAlchemy ORM Code
    --------------      --------------       ------------------------------
    startup        ->   Web framework        # Session registry is established
                        initializes          Session = scoped_session(sessionmaker())

    incoming
    web request    ->   web request     ->   # The registry is *optionally*
                        starts               # called upon explicitly to create
                                             # a Session local to the thread and/or request
                                             Session()

                                             # the Session registry can otherwise
                                             # be used at any time, creating the
                                             # request-local Session() if not present,
                                             # or returning the existing one
                                             Session.execute(select(MyClass)) # ...

                                             Session.add(some_object) # ...

                                             # if data was modified, commit the
                                             # transaction
                                             Session.commit()

                        web request ends  -> # the registry is instructed to
                                             # remove the Session
                                             Session.remove()

                        sends output      <-
    outgoing web    <-
    response

Using the above flow, the process of integrating the :class:`.Session` with the
web application has exactly two requirements:

1. Create a single :class:`.scoped_session` registry when the web application
   first starts, ensuring that this object is accessible by the rest of the
   application.
2. Ensure that :meth:`.scoped_session.remove` is called when the web request ends,
   usually by integrating with the web framework's event system to establish
   an "on request end" event.

As noted earlier, the above pattern is **just one potential way** to integrate a :class:`.Session`
with a web framework, one which in particular makes the significant assumption
that the **web framework associates web requests with application threads**.  It is
however **strongly recommended that the integration tools provided with the web framework
itself be used, if available**, instead of :class:`.scoped_session`.

In particular, while using a thread local can be convenient, it is preferable that the :class:`.Session` be
associated **directly with the request**, rather than with
the current thread.   The next section on custom scopes details a more advanced configuration
which can combine the usage of :class:`.scoped_session` with direct request based scope, or
any kind of scope.

使用自定义创建的范围
---------------------------

Using Custom Created Scopes

.. tab:: 中文

.. tab:: 英文

The :class:`.scoped_session` object's default behavior of "thread local" scope is only
one of many options on how to "scope" a :class:`.Session`.   A custom scope can be defined
based on any existing system of getting at "the current thing we are working with".

Suppose a web framework defines a library function ``get_current_request()``.  An application
built using this framework can call this function at any time, and the result will be
some kind of ``Request`` object that represents the current request being processed.
If the ``Request`` object is hashable, then this function can be easily integrated with
:class:`.scoped_session` to associate the :class:`.Session` with the request.  Below we illustrate
this in conjunction with a hypothetical event marker provided by the web framework
``on_request_end``, which allows code to be invoked whenever a request ends::

    from my_web_framework import get_current_request, on_request_end
    from sqlalchemy.orm import scoped_session, sessionmaker

    Session = scoped_session(sessionmaker(bind=some_engine), scopefunc=get_current_request)


    @on_request_end
    def remove_session(req):
        Session.remove()

Above, we instantiate :class:`.scoped_session` in the usual way, except that we pass
our request-returning function as the "scopefunc".  This instructs :class:`.scoped_session`
to use this function to generate a dictionary key whenever the registry is called upon
to return the current :class:`.Session`.   In this case it is particularly important
that we ensure a reliable "remove" system is implemented, as this dictionary is not
otherwise self-managed.


上下文会话 API
----------------------

Contextual Session API

.. tab:: 中文

.. tab:: 英文

.. autoclass:: sqlalchemy.orm.scoped_session
    :members:
    :inherited-members:

.. autoclass:: sqlalchemy.util.ScopedRegistry
    :members:

.. autoclass:: sqlalchemy.util.ThreadLocalRegistry

.. autoclass:: sqlalchemy.orm.QueryPropertyDescriptor
