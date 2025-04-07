"""
.. tab:: 中文

    这些配方说明了 :meth:`_orm.Session.execute` 使用的 ORM SELECT 行为的增强，以及 :term:`2.0 样式` 的 :func:`_sql.select` 以及 :term:`1.x 样式` :class:`_orm.Query` 对象。

    示例包括 :func:`_orm.with_loader_criteria` 选项以及 :meth:`_orm.SessionEvents.do_orm_execute` 钩子的演示。

    从 SQLAlchemy 1.4 开始，:class:`_orm.Query` 构造与 :class:`_expression.Select` 构造统一，因此这两个对象大致相同。

.. tab:: 英文

    Recipes which illustrate augmentation of ORM SELECT behavior as used by
    :meth:`_orm.Session.execute` with :term:`2.0 style` use of
    :func:`_sql.select`, as well as the :term:`1.x style` :class:`_orm.Query`
    object.

    Examples include demonstrations of the :func:`_orm.with_loader_criteria`
    option as well as the :meth:`_orm.SessionEvents.do_orm_execute` hook.

    As of SQLAlchemy 1.4, the :class:`_orm.Query` construct is unified
    with the :class:`_expression.Select` construct, so that these two objects
    are mostly the same.


.. autosource::

"""  # noqa
