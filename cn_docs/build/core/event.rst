.. _event_toplevel:

事件
======

Events

.. tab:: 中文

    SQLAlchemy 包含一个事件 API，它将各种各样的钩子发布到 SQLAlchemy Core 和 ORM 的内部。

.. tab:: 英文

    SQLAlchemy includes an event API which publishes a wide variety of hooks into the internals of both SQLAlchemy Core and ORM.

事件注册
------------------

Event Registration

.. tab:: 中文

    订阅事件是通过一个统一的 API 实现的，即 :func:`.listen` 函数，或可选地通过 :func:`.listens_for` 装饰器来完成。这些函数接受一个目标对象、一个用于标识要拦截事件的字符串标识符，以及一个用户定义的监听函数。这两个函数还可以接受额外的位置参数和关键字参数，具体支持哪些参数取决于事件的类型，这些事件类型可能会定义替代的接口形式，或基于目标对象说明次级事件目标的处理方式。

    事件的名称及其对应监听函数的参数签名来自绑定于某个类的规范方法，该类作为标记类在文档中进行了说明。例如，:meth:`_events.PoolEvents.connect` 的文档中指出，事件名称为 ``"connect"``，并且用户定义的监听函数应当接收两个位置参数::

        from sqlalchemy.event import listen
        from sqlalchemy.pool import Pool


        def my_on_connect(dbapi_con, connection_record):
            print("New DBAPI connection:", dbapi_con)


        listen(Pool, "connect", my_on_connect)

    使用装饰器 :func:`.listens_for` 订阅事件的形式如下::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect")
        def my_on_connect(dbapi_con, connection_record):
            print("New DBAPI connection:", dbapi_con)

.. tab:: 英文

    Subscribing to an event occurs through a single API point, the :func:`.listen` function,
    or alternatively the :func:`.listens_for` decorator.   These functions accept a
    target, a string identifier which identifies the event to be intercepted, and
    a user-defined listening function.  Additional positional and keyword arguments to these
    two functions may be supported by
    specific types of events, which may specify alternate interfaces for the given event function, or provide
    instructions regarding secondary event targets based on the given target.

    The name of an event and the argument signature of a corresponding listener function is derived from
    a class bound specification method, which exists bound to a marker class that's described in the documentation.
    For example, the documentation for :meth:`_events.PoolEvents.connect` indicates that the event name is ``"connect"``
    and that a user-defined listener function should receive two positional arguments::

        from sqlalchemy.event import listen
        from sqlalchemy.pool import Pool


        def my_on_connect(dbapi_con, connection_record):
            print("New DBAPI connection:", dbapi_con)


        listen(Pool, "connect", my_on_connect)

    To listen with the :func:`.listens_for` decorator looks like::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect")
        def my_on_connect(dbapi_con, connection_record):
            print("New DBAPI connection:", dbapi_con)

.. _event_named_argument_styles:

命名参数样式
---------------------

Named Argument Styles

.. tab:: 中文

    某些类型的事件监听函数可以接受不同风格的参数。以 :meth:`_events.PoolEvents.connect` 为例，该事件会传入 ``dbapi_connection`` 和 ``connection_record`` 两个参数。我们可以选择使用具名参数的方式接收这些参数，即编写一个接受 ``**keyword`` 参数的监听函数，并向 :func:`.listen` 或 :func:`.listens_for` 传递 ``named=True`` 参数::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect", named=True)
        def my_on_connect(**kw):
            print("New DBAPI connection:", kw["dbapi_connection"])

    在使用具名参数时，监听函数将以字典方式接收所有事件参数，其键名对应函数签名中指定的参数名。

    具名参数模式会将所有参数按名称传入监听函数，因此监听函数中可以直接列出部分参数，只要名称对应即可，其余参数通过 ``**kw`` 捕获::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect", named=True)
        def my_on_connect(dbapi_connection, **kw):
            print("New DBAPI connection:", dbapi_connection)
            print("Connection record:", kw["connection_record"])

    如上所示，监听函数中出现 ``**kw`` 是向 :func:`.listens_for` 表明应该使用具名方式传参，而非按位置传参。

.. tab:: 英文

    There are some varieties of argument styles which can be accepted by listener
    functions.  Taking the example of :meth:`_events.PoolEvents.connect`, this function
    is documented as receiving ``dbapi_connection`` and ``connection_record`` arguments.
    We can opt to receive these arguments by name, by establishing a listener function
    that accepts ``**keyword`` arguments, by passing ``named=True`` to either
    :func:`.listen` or :func:`.listens_for`::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect", named=True)
        def my_on_connect(**kw):
            print("New DBAPI connection:", kw["dbapi_connection"])

    When using named argument passing, the names listed in the function argument
    specification will be used as keys in the dictionary.

    Named style passes all arguments by name regardless of the function
    signature, so specific arguments may be listed as well, in any order,
    as long as the names match up::

        from sqlalchemy.event import listens_for
        from sqlalchemy.pool import Pool


        @listens_for(Pool, "connect", named=True)
        def my_on_connect(dbapi_connection, **kw):
            print("New DBAPI connection:", dbapi_connection)
            print("Connection record:", kw["connection_record"])

    Above, the presence of ``**kw`` tells :func:`.listens_for` that
    arguments should be passed to the function by name, rather than positionally.

目标
-------

Targets

.. tab:: 中文

    :func:`.listen` 函数在监听目标的选择上非常灵活。它通常可以接受类、这些类的实例，或者与之相关的类或对象，这些对象中能够派生出适当的监听目标。例如，前文提到的 ``"connect"`` 事件可以接受 :class:`_engine.Engine` 类或其实例，也可以接受 :class:`_pool.Pool` 类或其实例::

        from sqlalchemy.event import listen
        from sqlalchemy.pool import Pool, QueuePool
        from sqlalchemy import create_engine
        from sqlalchemy.engine import Engine
        import psycopg2


        def connect():
            return psycopg2.connect(user="ed", host="127.0.0.1", dbname="test")


        my_pool = QueuePool(connect)
        my_engine = create_engine("postgresql+psycopg2://ed@localhost/test")

        # 为所有 Pool 实例添加监听器
        listen(Pool, "connect", my_on_connect)

        # 通过 Engine 类为所有 Pool 实例添加监听器
        listen(Engine, "connect", my_on_connect)

        # 为 my_pool 添加监听器
        listen(my_pool, "connect", my_on_connect)

        # 为 my_engine.pool 添加监听器
        listen(my_engine, "connect", my_on_connect)

.. tab:: 英文

    The :func:`.listen` function is very flexible regarding targets.  It
    generally accepts classes, instances of those classes, and related
    classes or objects from which the appropriate target can be derived.
    For example, the above mentioned ``"connect"`` event accepts
    :class:`_engine.Engine` classes and objects as well as :class:`_pool.Pool` classes
    and objects::

        from sqlalchemy.event import listen
        from sqlalchemy.pool import Pool, QueuePool
        from sqlalchemy import create_engine
        from sqlalchemy.engine import Engine
        import psycopg2


        def connect():
            return psycopg2.connect(user="ed", host="127.0.0.1", dbname="test")


        my_pool = QueuePool(connect)
        my_engine = create_engine("postgresql+psycopg2://ed@localhost/test")

        # associate listener with all instances of Pool
        listen(Pool, "connect", my_on_connect)

        # associate listener with all instances of Pool
        # via the Engine class
        listen(Engine, "connect", my_on_connect)

        # associate listener with my_pool
        listen(my_pool, "connect", my_on_connect)

        # associate listener with my_engine.pool
        listen(my_engine, "connect", my_on_connect)

.. _event_modifiers:

修饰符
---------

Modifiers

.. tab:: 中文

    某些事件监听器允许通过 :func:`.listen` 传入修饰符参数。这些修饰符有时可以改变监听器的调用签名。例如，在 ORM 事件中，某些监听器可以返回值来影响后续处理。默认情况下，监听函数不需要返回值，但通过传入 ``retval=True`` 参数，可以启用返回值的支持::

        def validate_phone(target, value, oldvalue, initiator):
            """去除电话号码中的非数字字符"""

            return re.sub(r"\D", "", value)


        # 在 UserContact.phone 属性上设置监听器，启用返回值处理
        listen(UserContact.phone, "set", validate_phone, retval=True)

.. tab:: 英文

    Some listeners allow modifiers to be passed to :func:`.listen`.  These
    modifiers sometimes provide alternate calling signatures for
    listeners.  Such as with ORM events, some event listeners can have a
    return value which modifies the subsequent handling.   By default, no
    listener ever requires a return value, but by passing ``retval=True``
    this value can be supported::

        def validate_phone(target, value, oldvalue, initiator):
            """Strip non-numeric characters from a phone number"""

            return re.sub(r"\D", "", value)


        # setup listener on UserContact.phone attribute, instructing
        # it to use the return value
        listen(UserContact.phone, "set", validate_phone, retval=True)

事件和多处理
--------------------------

Events and Multiprocessing

.. tab:: 中文

    SQLAlchemy 的事件钩子是通过 Python 函数与对象实现的，因此事件的传播是以 Python 函数调用的方式进行的。Python 的多进程模型遵循操作系统多进程的通用理念，例如父进程派生出子进程，因此我们可以用同样的模型来描述 SQLAlchemy 事件系统在多进程环境中的行为。

    在父进程中注册的事件钩子，在其之后派生出来的子进程中也会存在，因为子进程启动时会复制父进程中所有已存在的 Python 结构。相反，如果子进程早于事件钩子的注册而存在，那么这些子进程将不会继承新注册的事件钩子。也就是说，父进程对 Python 结构所做的更改不会传播至已经存在的子进程。

    至于事件本身，它们是 Python 函数调用，在进程之间无法传播。SQLAlchemy 的事件系统并不实现任何形式的进程间通信。不过，用户可以自行实现支持 Python 多进程消息通信的事件钩子逻辑，但这部分功能需由用户自定义。

.. tab:: 英文

    SQLAlchemy's event hooks are implemented with Python functions and objects,
    so events propagate via Python function calls.
    Python multiprocessing follows the
    same way we think about OS multiprocessing,
    such as a parent process forking a child process,
    thus we can describe the SQLAlchemy event system's behavior using the same model.

    Event hooks registered in a parent process
    will be present in new child processes
    that are forked from that parent after the hooks have been registered,
    since the child process starts with
    a copy of all existing Python structures from the parent when spawned.
    Child processes that already exist before the hooks are registered
    will not receive those new event hooks,
    as changes made to Python structures in a parent process
    do not propagate to child processes.

    For the events themselves, these are Python function calls,
    which do not have any ability to propagate between processes.
    SQLAlchemy's event system does not implement any inter-process communication.
    It is possible to implement event hooks
    that use Python inter-process messaging within them,
    however this would need to be implemented by the user.

事件参考
---------------

Event Reference

.. tab:: 中文

    SQLAlchemy Core 与 SQLAlchemy ORM 都支持丰富的事件钩子：

    * **Core 事件** - 详见 :ref:`core_event_toplevel`，涵盖连接池生命周期、SQL 语句执行、事务生命周期、模式的创建与销毁等相关的事件钩子。

    * **ORM 事件** - 详见 :ref:`orm_event_toplevel`，涵盖类与属性的检测钩子、对象初始化钩子、属性变更钩子、会话状态、刷新与提交钩子、映射器初始化、对象/结果填充，以及针对单个对象的持久化钩子等内容。

.. tab:: 英文

    Both SQLAlchemy Core and SQLAlchemy ORM feature a wide variety of event hooks:
    
    * **Core Events** - these are described in
      :ref:`core_event_toplevel` and include event hooks specific to
      connection pool lifecycle, SQL statement execution,
      transaction lifecycle, and schema creation and teardown.
    
    * **ORM Events** - these are described in
      :ref:`orm_event_toplevel`, and include event hooks specific to
      class and attribute instrumentation, object initialization
      hooks, attribute on-change hooks, session state, flush, and
      commit hooks, mapper initialization, object/result population,
      and per-instance persistence hooks.

API 参考
-------------

API Reference

.. tab:: 中文

.. tab:: 英文

.. autofunction:: sqlalchemy.event.listen

.. autofunction:: sqlalchemy.event.listens_for

.. autofunction:: sqlalchemy.event.remove

.. autofunction:: sqlalchemy.event.contains
