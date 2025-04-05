.. highlight:: pycon+sql

.. |prev| replace:: :doc:`dml`
.. |next| replace:: :doc:`relationships`

.. include:: queryguide_nav_include.rst


.. doctest-include _deferred_setup.rst

.. currentmodule:: sqlalchemy.orm

.. _loading_columns:

======================
列加载选项
======================

Column Loading Options

.. tab:: 中文

    .. admonition:: 关于本文档

        本节介绍了有关加载列的其他选项。使用的映射包括存储大字符串值的列，我们可能希望限制它们的加载时间。

        :doc:`查看本页的 ORM 设置 <_deferred_setup>`。下面的一些示例将重新定义 ``Book`` 映射器以修改一些列定义。

.. tab:: 英文

    .. admonition:: About this Document

        This section presents additional options regarding the loading of
        columns.  The mappings used include columns that would store
        large string values for which we may want to limit when they
        are loaded.

        :doc:`View the ORM setup for this page <_deferred_setup>`.  Some
        of the examples below will redefine the ``Book`` mapper to modify
        some of the column definitions.

.. _orm_queryguide_column_deferral:

使用【列延迟】限制加载哪些列
------------------------------------------------

Limiting which Columns Load with Column Deferral

.. tab:: 中文

    **列延迟加载（Column deferral）** 指的是在查询某类对象时，从 SELECT 语句中省略 ORM 映射的某些列。这种做法通常是出于性能考虑，适用于那些表中存在不常使用且可能包含大量数据的列的情况，因为在每次查询时完全加载这些列可能会非常耗时或占用大量内存。SQLAlchemy ORM 提供了多种方式来控制实体加载时列的加载方式。

    本节中的大多数示例展示的是 **ORM 加载选项（ORM loader options）** 。这些是一些小型构造体，被传递给 :class:`_sql.Select` 对象的 :meth:`_sql.Select.options` 方法，在对象被编译为 SQL 字符串时由 ORM 使用。


.. tab:: 英文

    **Column deferral** refers to ORM mapped columns that are omitted from a SELECT statement when objects of that type are queried. The general rationale here is performance, in cases where tables have seldom-used columns with potentially large data values, as fully loading these columns on every query may be time and/or memory intensive. SQLAlchemy ORM offers a variety of ways to control the loading of columns when entities are loaded.

    Most examples in this section are illustrating **ORM loader options**. These are small constructs that are passed to the :meth:`_sql.Select.options` method of the :class:`_sql.Select` object, which are then consumed by the ORM when the object is compiled into a SQL string.

.. _orm_queryguide_load_only:

使用 ``load_only()`` 减少加载的列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``load_only()`` to reduce loaded columns

.. tab:: 中文

    :func:`_orm.load_only` 加载选项是在已知只会访问少量列时，加载对象最便捷的方式。该选项接受多个类绑定的属性对象作为参数，用于指示应加载哪些列映射的属性，除了主键以外的其他列映射属性将不会被包含在获取的列中。在下面的示例中， ``Book`` 类包含 ``.title``、 ``.summary`` 和 ``.cover_photo`` 三个列。使用 :func:`_orm.load_only` 我们可以指示 ORM 仅预加载 ``.title`` 和 ``.summary`` 列::

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import load_only
        >>> stmt = select(Book).options(load_only(Book.title, Book.summary))
        >>> books = session.scalars(stmt).all()
        {execsql}SELECT book.id, book.title, book.summary
        FROM book
        [...] ()
        {stop}>>> for book in books:
        ...     print(f"{book.title}  {book.summary}")
        100 Years of Krabby Patties  some long summary
        Sea Catch 22  another long summary
        The Sea Grapes of Wrath  yet another summary
        A Nut Like No Other  some long summary
        Geodesic Domes: A Retrospective  another long summary
        Rocketry for Squirrels  yet another summary

    如上所示，SELECT 语句省略了 ``.cover_photo`` 列，仅包含 ``.title`` 和 ``.summary``，以及主键列 ``.id``；ORM 通常会始终获取主键列，因为这些列用于建立该行的身份标识。

    一旦对象加载完成，对于尚未加载的属性，通常会应用 :term:`lazy loading`（延迟加载）行为，也就是说，当首次访问这些属性时，会在当前事务中发出一条 SQL 语句以加载该值。如下所示，访问 ``.cover_photo`` 会触发一条 SELECT 语句来加载其值::

        >>> img_data = books[0].cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (1,)

    延迟加载始终使用对象当前处于 :term:`persistent`（持久）状态所绑定的 :class:`_orm.Session` 来执行。如果该对象已与任何 :class:`_orm.Session` 分离（即处于 :term:`detached` 状态），该操作会失败并引发异常。

    作为访问时延迟加载的替代方案，还可以将延迟列配置为在访问时始终抛出具有提示信息的异常，而不管其是否已绑定 Session。在使用 :func:`_orm.load_only` 构造时，可以通过 :paramref:`_orm.load_only.raiseload` 参数来启用此行为。参见 :ref:`orm_queryguide_deferred_raiseload` 章节以了解背景和示例。

    .. tip::  

        如其他地方所述，在使用 :ref:`asyncio_toplevel` 时不支持延迟加载。


.. tab:: 英文

    The :func:`_orm.load_only` loader option is the most expedient option to use when loading objects where it is known that only a small handful of columns will be accessed. This option accepts a variable number of class-bound attribute objects indicating those column-mapped attributes that should be loaded, where all other column-mapped attributes outside of the primary key will not be part of the columns fetched . In the example below, the ``Book`` class contains columns ``.title``, ``.summary`` and ``.cover_photo``. Using :func:`_orm.load_only` we can instruct the ORM to only load the ``.title`` and ``.summary`` columns up front::

        >>> from sqlalchemy import select
        >>> from sqlalchemy.orm import load_only
        >>> stmt = select(Book).options(load_only(Book.title, Book.summary))
        >>> books = session.scalars(stmt).all()
        {execsql}SELECT book.id, book.title, book.summary
        FROM book
        [...] ()
        {stop}>>> for book in books:
        ...     print(f"{book.title}  {book.summary}")
        100 Years of Krabby Patties  some long summary
        Sea Catch 22  another long summary
        The Sea Grapes of Wrath  yet another summary
        A Nut Like No Other  some long summary
        Geodesic Domes: A Retrospective  another long summary
        Rocketry for Squirrels  yet another summary

    Above, the SELECT statement has omitted the ``.cover_photo`` column and included only ``.title`` and ``.summary``, as well as the primary key column ``.id``; the ORM will typically always fetch the primary key columns as these are required to establish the identity for the row.

    Once loaded, the object will normally have :term:`lazy loading` behavior applied to the remaining unloaded attributes, meaning that when any are first accessed, a SQL statement will be emitted within the current transaction in order to load the value.  Below, accessing ``.cover_photo`` emits a SELECT statement to load its value::

        >>> img_data = books[0].cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (1,)

    Lazy loads are always emitted using the :class:`_orm.Session` to which the object is in the :term:`persistent` state.  If the object is :term:`detached` from any :class:`_orm.Session`, the operation fails, raising an exception.

    As an alternative to lazy loading on access, deferred columns may also be configured to raise an informative exception when accessed, regardless of their attachment state.  When using the :func:`_orm.load_only` construct, this may be indicated using the :paramref:`_orm.load_only.raiseload` parameter. See the section :ref:`orm_queryguide_deferred_raiseload` for background and examples.

    .. tip::  
        
        as noted elsewhere, lazy loading is not available when using :ref:`asyncio_toplevel`.

使用 ``load_only()`` 处理多个实体
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``load_only()`` with multiple entities

.. tab:: 中文

    :func:`_orm.load_only` 的作用范围仅限于其属性列表中所指向的单个实体（当前不允许传入跨多个实体的属性列表）。在下面的示例中，给定的 :func:`_orm.load_only` 选项仅应用于 ``Book`` 实体。被同时查询的 ``User`` 实体不受影响；在生成的 SELECT 语句中， ``user_account`` 表的所有列都会被包含，而 ``book`` 表中仅包含 ``book.id`` 和 ``book.title``::

        >>> stmt = select(User, Book).join_from(User, Book).options(load_only(Book.title))
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname,
        book.id AS id_1, book.title
        FROM user_account JOIN book ON user_account.id = book.owner_id

    如果我们希望同时对 ``User`` 和 ``Book`` 应用 :func:`_orm.load_only` 选项，则需要分别为它们设置两个独立的选项::

        >>> stmt = (
        ...     select(User, Book)
        ...     .join_from(User, Book)
        ...     .options(load_only(User.name), load_only(Book.title))
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, book.id AS id_1, book.title
        FROM user_account JOIN book ON user_account.id = book.owner_id

.. tab:: 英文

    :func:`_orm.load_only` limits itself to the single entity that is referred towards in its list of attributes (passing a list of attributes that span more than a single entity is currently disallowed). In the example below, the given :func:`_orm.load_only` option applies only to the ``Book`` entity. The ``User`` entity that's also selected is not affected; within the resulting SELECT statement, all columns for ``user_account`` are present, whereas only ``book.id`` and ``book.title`` are present for the ``book`` table::

        >>> stmt = select(User, Book).join_from(User, Book).options(load_only(Book.title))
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, user_account.fullname,
        book.id AS id_1, book.title
        FROM user_account JOIN book ON user_account.id = book.owner_id

    If we wanted to apply :func:`_orm.load_only` options to both ``User`` and ``Book``, we would make use of two separate options::

        >>> stmt = (
        ...     select(User, Book)
        ...     .join_from(User, Book)
        ...     .options(load_only(User.name), load_only(Book.title))
        ... )
        >>> print(stmt)
        {printsql}SELECT user_account.id, user_account.name, book.id AS id_1, book.title
        FROM user_account JOIN book ON user_account.id = book.owner_id

.. _orm_queryguide_load_only_related:

使用 ``load_only()`` 处理相关对象和集合
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``load_only()`` on related objects and collections

.. tab:: 中文

    在使用 :ref:`relationship loaders <loading_toplevel>` 控制关联对象加载时，可以使用关系加载器的 :meth:`.Load.load_only` 方法，对子实体的列应用 :func:`_orm.load_only` 规则。下面的示例中，使用 :func:`_orm.selectinload` 加载每个 ``User`` 对象关联的 ``books`` 集合。通过将 :meth:`.Load.load_only` 应用于选项对象，当关系对象被加载时，生成的 SELECT 语句只会包含 ``title`` 列以及主键列::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(User).options(selectinload(User.books).load_only(Book.title))
        >>> for user in session.scalars(stmt):
        ...     print(f"{user.fullname}   {[b.title for b in user.books]}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        SELECT book.owner_id AS book_owner_id, book.id AS book_id, book.title AS book_title
        FROM book
        WHERE book.owner_id IN (?, ?)
        [...] (1, 2)
        {stop}Spongebob Squarepants   ['100 Years of Krabby Patties', 'Sea Catch 22', 'The Sea Grapes of Wrath']
        Sandy Cheeks   ['A Nut Like No Other', 'Geodesic Domes: A Retrospective', 'Rocketry for Squirrels']

    .. comment

        >>> session.expunge_all()

    :func:`_orm.load_only` 也可以应用于子实体，而无需显式指定用于该关系的加载方式。如果我们不希望改变 ``User.books`` 的默认加载策略，但仍希望对 ``Book`` 应用 load only 规则，可以使用 :func:`_orm.defaultload` 选项，它会保留关系的默认加载方式（此处为 ``"lazy"``），并对每个 ``User.books`` 集合所发出的 SELECT 语句应用我们自定义的 :func:`_orm.load_only` 规则::

        >>> from sqlalchemy.orm import defaultload
        >>> stmt = select(User).options(defaultload(User.books).load_only(Book.title))
        >>> for user in session.scalars(stmt):
        ...     print(f"{user.fullname}   {[b.title for b in user.books]}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        SELECT book.id AS book_id, book.title AS book_title
        FROM book
        WHERE ? = book.owner_id
        [...] (1,)
        {stop}Spongebob Squarepants   ['100 Years of Krabby Patties', 'Sea Catch 22', 'The Sea Grapes of Wrath']
        {execsql}SELECT book.id AS book_id, book.title AS book_title
        FROM book
        WHERE ? = book.owner_id
        [...] (2,)
        {stop}Sandy Cheeks   ['A Nut Like No Other', 'Geodesic Domes: A Retrospective', 'Rocketry for Squirrels']


.. tab:: 英文

    When using :ref:`relationship loaders <loading_toplevel>` to control the loading of related objects, the :meth:`.Load.load_only` method of any relationship loader may be used to apply :func:`_orm.load_only` rules to columns on the sub-entity.  In the example below, :func:`_orm.selectinload` is used to load the related ``books`` collection on each ``User`` object.   By applying :meth:`.Load.load_only` to the resulting option object, when objects are loaded for the relationship, the SELECT emitted will only refer to the ``title`` column in addition to primary key column::

        >>> from sqlalchemy.orm import selectinload
        >>> stmt = select(User).options(selectinload(User.books).load_only(Book.title))
        >>> for user in session.scalars(stmt):
        ...     print(f"{user.fullname}   {[b.title for b in user.books]}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        SELECT book.owner_id AS book_owner_id, book.id AS book_id, book.title AS book_title
        FROM book
        WHERE book.owner_id IN (?, ?)
        [...] (1, 2)
        {stop}Spongebob Squarepants   ['100 Years of Krabby Patties', 'Sea Catch 22', 'The Sea Grapes of Wrath']
        Sandy Cheeks   ['A Nut Like No Other', 'Geodesic Domes: A Retrospective', 'Rocketry for Squirrels']


    .. comment

        >>> session.expunge_all()

    :func:`_orm.load_only` may also be applied to sub-entities without needing to state the style of loading to use for the relationship itself.  If we didn't want to change the default loading style of ``User.books`` but still apply load only rules to ``Book``, we would link using the :func:`_orm.defaultload` option, which in this case will retain the default relationship loading style of ``"lazy"``, and applying our custom :func:`_orm.load_only` rule to the SELECT statement emitted for each ``User.books`` collection::

        >>> from sqlalchemy.orm import defaultload
        >>> stmt = select(User).options(defaultload(User.books).load_only(Book.title))
        >>> for user in session.scalars(stmt):
        ...     print(f"{user.fullname}   {[b.title for b in user.books]}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname
        FROM user_account
        [...] ()
        SELECT book.id AS book_id, book.title AS book_title
        FROM book
        WHERE ? = book.owner_id
        [...] (1,)
        {stop}Spongebob Squarepants   ['100 Years of Krabby Patties', 'Sea Catch 22', 'The Sea Grapes of Wrath']
        {execsql}SELECT book.id AS book_id, book.title AS book_title
        FROM book
        WHERE ? = book.owner_id
        [...] (2,)
        {stop}Sandy Cheeks   ['A Nut Like No Other', 'Geodesic Domes: A Retrospective', 'Rocketry for Squirrels']

.. _orm_queryguide_defer:

使用 ``defer()`` 忽略特定列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``defer()`` to omit specific columns

.. tab:: 中文

    :func:`_orm.defer` 加载选项是一个比 :func:`_orm.load_only` 更加细粒度的替代方案，它允许将某个特定列标记为“不要加载”。在下面的示例中，:func:`_orm.defer` 被直接应用于 ``.cover_photo`` 列，而其他列的行为保持不变::

        >>> from sqlalchemy.orm import defer
        >>> stmt = select(Book).where(Book.owner_id == 2).options(defer(Book.cover_photo))
        >>> books = session.scalars(stmt).all()
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.owner_id = ?
        [...] (2,)
        {stop}>>> for book in books:
        ...     print(f"{book.title}: {book.summary}")
        A Nut Like No Other: some long summary
        Geodesic Domes: A Retrospective: another long summary
        Rocketry for Squirrels: yet another summary

    与 :func:`_orm.load_only` 一样，未加载的列默认在访问时将通过 :term:`lazy loading`（延迟加载）方式加载::

        >>> img_data = books[0].cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (4,)

    可以在一个语句中使用多个 :func:`_orm.defer` 选项来标记多个列为延迟加载。

    同样地，:func:`_orm.defer` 选项也支持使被延迟加载的属性在访问时抛出异常，而不是执行延迟加载。这一点在 :ref:`orm_queryguide_deferred_raiseload` 一节中有说明。

.. tab:: 英文

    The :func:`_orm.defer` loader option is a more fine grained alternative to :func:`_orm.load_only`, which allows a single specific column to be marked as "dont load".  In the example below, :func:`_orm.defer` is applied directly to the ``.cover_photo`` column, leaving the behavior of all other columns unchanged::

        >>> from sqlalchemy.orm import defer
        >>> stmt = select(Book).where(Book.owner_id == 2).options(defer(Book.cover_photo))
        >>> books = session.scalars(stmt).all()
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.owner_id = ?
        [...] (2,)
        {stop}>>> for book in books:
        ...     print(f"{book.title}: {book.summary}")
        A Nut Like No Other: some long summary
        Geodesic Domes: A Retrospective: another long summary
        Rocketry for Squirrels: yet another summary

    As is the case with :func:`_orm.load_only`, unloaded columns by default will load themselves when accessed using :term:`lazy loading`::

        >>> img_data = books[0].cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (4,)

    Multiple :func:`_orm.defer` options may be used in one statement in order to mark several columns as deferred.

    As is the case with :func:`_orm.load_only`, the :func:`_orm.defer` option also includes the ability to have a deferred attribute raise an exception on access rather than lazy loading.  This is illustrated in the section :ref:`orm_queryguide_deferred_raiseload`.

.. _orm_queryguide_deferred_raiseload:

使用 raiseload 防止延迟列加载
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using raiseload to prevent deferred column loads

.. tab:: 中文

    .. comment

    >>> session.expunge_all()

    当使用 :func:`_orm.load_only` 或 :func:`_orm.defer` 加载选项时，被标记为延迟加载的属性在对象中默认会在首次访问时，在当前事务中发出 SELECT 语句以加载其值。通常我们希望避免这种加载发生，而是在访问属性时直接抛出异常，以表明该列不应被访问。这种情况在以下场景中很常见：某个操作已提前加载了所有需要的列，并将对象传递给视图层，如果视图层中再次访问数据库列，将会暴露出加载缺失的问题，从而可用于回退并修复预加载逻辑。

    对于这种用途，:func:`_orm.defer` 和 :func:`_orm.load_only` 加载选项都包含一个布尔参数 :paramref:`_orm.defer.raiseload`，当设置为 ``True`` 时，将使相关属性在访问时抛出异常。下面的示例中，被延迟的 ``.cover_photo`` 列在访问时将被禁止::

        >>> book = session.scalar(
        ...     select(Book).options(defer(Book.cover_photo, raiseload=True)).where(Book.id == 4)
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.id = ?
        [...] (4,)
        {stop}>>> book.cover_photo
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.cover_photo' is not available due to raiseload=True

    当使用 :func:`_orm.load_only` 指定一组需要加载的非延迟列时，可使用 :paramref:`_orm.load_only.raiseload` 参数来对其余未加载列启用 ``raiseload`` 行为，它将应用于所有被延迟的属性::

        >>> session.expunge_all()
        >>> book = session.scalar(
        ...     select(Book).options(load_only(Book.title, raiseload=True)).where(Book.id == 5)
        ... )
        {execsql}SELECT book.id, book.title
        FROM book
        WHERE book.id = ?
        [...] (5,)
        {stop}>>> book.summary
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.summary' is not available due to raiseload=True

    .. note::

        当前尚不支持在同一语句中混用 :func:`_orm.load_only` 和 :func:`_orm.defer` 来改变同一实体中某些属性的 ``raiseload`` 行为；这样做会产生未定义的属性加载行为。

    .. seealso::

        :paramref:`_orm.defer.raiseload` 功能是关系型 “raiseload” 功能在列级别的版本。关于关系的 "raiseload"，请参见本指南的 :ref:`loading_toplevel` 部分中的 :ref:`prevent_lazy_with_raiseload`。


.. tab:: 英文

    .. comment

    >>> session.expunge_all()

    When using the :func:`_orm.load_only` or :func:`_orm.defer` loader options, attributes marked as deferred on an object have the default behavior that when first accessed, a SELECT statement will be emitted within the current transaction in order to load their value. It is often necessary to prevent this load from occurring, and instead raise an exception when the attribute is accessed, indicating that the need to query the database for this column was not expected. A typical scenario is an operation where objects are loaded with all the columns that are known to be required for the operation to proceed, which are then passed onto a view layer. Any further SQL operations that emit within the view layer should be caught, so that the up-front loading operation can be adjusted to accommodate for that additional data up front, rather than incurring additional lazy loading.

    For this use case the :func:`_orm.defer` and :func:`_orm.load_only` options include a boolean parameter :paramref:`_orm.defer.raiseload`, which when set to ``True`` will cause the affected attributes to raise on access.  In the example below, the deferred column ``.cover_photo`` will disallow attribute access::

        >>> book = session.scalar(
        ...     select(Book).options(defer(Book.cover_photo, raiseload=True)).where(Book.id == 4)
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.id = ?
        [...] (4,)
        {stop}>>> book.cover_photo
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.cover_photo' is not available due to raiseload=True

    When using :func:`_orm.load_only` to name a specific set of non-deferred columns, ``raiseload`` behavior may be applied to the remaining columns using the :paramref:`_orm.load_only.raiseload` parameter, which will be applied to all deferred attributes::

        >>> session.expunge_all()
        >>> book = session.scalar(
        ...     select(Book).options(load_only(Book.title, raiseload=True)).where(Book.id == 5)
        ... )
        {execsql}SELECT book.id, book.title
        FROM book
        WHERE book.id = ?
        [...] (5,)
        {stop}>>> book.summary
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.summary' is not available due to raiseload=True

    .. note::

        It is not yet possible to mix :func:`_orm.load_only` and :func:`_orm.defer` options which refer to the same entity together in one statement in order to change the ``raiseload`` behavior of certain attributes; currently, doing so will produce undefined loading behavior of attributes.

    .. seealso::

        The :paramref:`_orm.defer.raiseload` feature is the column-level version of the same "raiseload" feature that's available for relationships. For "raiseload" with relationships, see :ref:`prevent_lazy_with_raiseload` in the :ref:`loading_toplevel` section of this guide.



.. _orm_queryguide_deferred_declarative:

在映射上配置列延迟
---------------------------------------

Configuring Column Deferral on Mappings

.. tab:: 中文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    :func:`_orm.defer` 的功能也可以作为映射列的默认行为启用，这对于那些不应该在每次查询中无条件加载的列来说非常合适。要进行配置，可使用 :func:`_orm.mapped_column` 的参数 :paramref:`_orm.mapped_column.deferred`。以下示例展示了对 ``Book`` 类的映射，其中 ``summary`` 和 ``cover_photo`` 列被设置为默认延迟加载::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text, deferred=True)
        ...     cover_photo: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    使用上述映射后，针对 ``Book`` 的查询将自动省略 ``summary`` 和 ``cover_photo`` 列::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)

    如所有延迟加载行为一样，当首次访问已加载对象上的延迟属性时，其默认行为是 :term:`lazy load` 其值::

        >>> img_data = book.cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)

    与 :func:`_orm.defer` 和 :func:`_orm.load_only` 加载选项类似，映射器级别的延迟加载同样支持 ``raiseload`` 行为。此行为意味着如果语句中未提供其他加载选项，则不会懒加载这些列，而是在访问时抛出异常。这样可以配置映射，使得某些列默认不会加载，并且在没有显式加载指令的情况下也永远不会懒加载。关于如何配置和使用此行为，请参见 :ref:`orm_queryguide_mapper_deferred_raiseload` 一节。

.. tab:: 英文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    The functionality of :func:`_orm.defer` is available as a default behavior for mapped columns, as may be appropriate for columns that should not be loaded unconditionally on every query. To configure, use the :paramref:`_orm.mapped_column.deferred` parameter of :func:`_orm.mapped_column`. The example below illustrates a mapping for ``Book`` which applies default column deferral to the ``summary`` and ``cover_photo`` columns::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text, deferred=True)
        ...     cover_photo: Mapped[bytes] = mapped_column(LargeBinary, deferred=True)
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    Using the above mapping, queries against ``Book`` will automatically not include the ``summary`` and ``cover_photo`` columns::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)

    As is the case with all deferral, the default behavior when deferred attributes on the loaded object are first accessed is that they will :term:`lazy load` their value::

        >>> img_data = book.cover_photo
        {execsql}SELECT book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)

    As is the case with the :func:`_orm.defer` and :func:`_orm.load_only` loader options, mapper level deferral also includes an option for ``raiseload`` behavior to occur, rather than lazy loading, when no other options are present in a statement.  This allows a mapping where certain columns will not load by default and will also never load lazily without explicit directives used in a statement.   See the section :ref:`orm_queryguide_mapper_deferred_raiseload` for background on how to configure and use this behavior.

.. _orm_queryguide_deferred_imperative:

对命令式映射器、映射 SQL 表达式使用 ``deferred()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``deferred()`` for imperative mappers, mapped SQL expressions

.. tab:: 中文

    :func:`_orm.deferred` 是早期版本中使用的、功能更通用的“延迟列”映射指令，早于 SQLAlchemy 中 :func:`_orm.mapped_column` 构造的引入。

    :func:`_orm.deferred` 在配置 ORM 映射器时使用，它接受任意 SQL 表达式或 :class:`_schema.Column` 对象。因此它适用于非声明式的 :ref:`命令式映射 <orm_imperative_mapping>`，可通过 :paramref:`_orm.registry.map_imperatively.properties` 字典传入：

    .. sourcecode:: python

        from sqlalchemy import Blob
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Text
        from sqlalchemy.orm import registry

        mapper_registry = registry()

        book_table = Table(
            "book",
            mapper_registry.metadata,
            Column("id", Integer, primary_key=True),
            Column("title", String(50)),
            Column("summary", Text),
            Column("cover_image", Blob),
        )


        class Book:
            pass


        mapper_registry.map_imperatively(
            Book,
            book_table,
            properties={
                "summary": deferred(book_table.c.summary),
                "cover_image": deferred(book_table.c.cover_image),
            },
        )

    当映射的 SQL 表达式应以延迟方式加载时，也可以使用 :func:`_orm.deferred` 替代 :func:`_orm.column_property`：

    .. sourcecode:: python

        from sqlalchemy.orm import deferred


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            firstname: Mapped[str] = mapped_column()
            lastname: Mapped[str] = mapped_column()
            fullname: Mapped[str] = deferred(firstname + " " + lastname)

    .. seealso::

        :ref:`mapper_column_property_sql_expressions` - 位于 :ref:`mapper_sql_expressions` 章节

        :ref:`orm_imperative_table_column_options` - 位于 :ref:`orm_declarative_table_config_toplevel` 章节


.. tab:: 英文

    The :func:`_orm.deferred` function is the earlier, more general purpose "deferred column" mapping directive that precedes the introduction of the :func:`_orm.mapped_column` construct in SQLAlchemy.

    :func:`_orm.deferred` is used when configuring ORM mappers, and accepts arbitrary SQL expressions or :class:`_schema.Column` objects. As such it's suitable to be used with non-declarative :ref:`imperative mappings <orm_imperative_mapping>`, passing it to the :paramref:`_orm.registry.map_imperatively.properties` dictionary:

    .. sourcecode:: python

        from sqlalchemy import Blob
        from sqlalchemy import Column
        from sqlalchemy import ForeignKey
        from sqlalchemy import Integer
        from sqlalchemy import String
        from sqlalchemy import Table
        from sqlalchemy import Text
        from sqlalchemy.orm import registry

        mapper_registry = registry()

        book_table = Table(
            "book",
            mapper_registry.metadata,
            Column("id", Integer, primary_key=True),
            Column("title", String(50)),
            Column("summary", Text),
            Column("cover_image", Blob),
        )


        class Book:
            pass


        mapper_registry.map_imperatively(
            Book,
            book_table,
            properties={
                "summary": deferred(book_table.c.summary),
                "cover_image": deferred(book_table.c.cover_image),
            },
        )

    :func:`_orm.deferred` may also be used in place of :func:`_orm.column_property` when mapped SQL expressions should be loaded on a deferred basis:

    .. sourcecode:: python

        from sqlalchemy.orm import deferred


        class User(Base):
            __tablename__ = "user"

            id: Mapped[int] = mapped_column(primary_key=True)
            firstname: Mapped[str] = mapped_column()
            lastname: Mapped[str] = mapped_column()
            fullname: Mapped[str] = deferred(firstname + " " + lastname)

    .. seealso::

        :ref:`mapper_column_property_sql_expressions` - in the section :ref:`mapper_sql_expressions`

        :ref:`orm_imperative_table_column_options` - in the section :ref:`orm_declarative_table_config_toplevel`

使用 ``undefer()`` “急切地” 加载延迟列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``undefer()`` to "eagerly" load deferred columns

.. tab:: 中文

    对于在映射中配置为默认延迟加载的列，:func:`_orm.undefer` 选项可以使这些通常被延迟加载的列被“取消延迟”，也就是说，这些列将与映射中的其他列一起被立即加载。例如，我们可以对 ``Book.summary`` 列应用 :func:`_orm.undefer`，该列在前面的映射中被标记为了延迟加载::

        >>> from sqlalchemy.orm import undefer
        >>> book = session.scalar(select(Book).where(Book.id == 2).options(undefer(Book.summary)))
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.id = ?
        [...] (2,)

    此时 ``Book.summary`` 列已被预加载，可以在不发出额外 SQL 的情况下访问其内容::

        >>> print(book.summary)
        another long summary


.. tab:: 英文

    With columns configured on mappings to defer by default, the :func:`_orm.undefer` option will cause any column that is normally deferred to be undeferred, that is, to load up front with all the other columns of the mapping.   For example we may apply :func:`_orm.undefer` to the ``Book.summary`` column, which is indicated in the previous mapping as deferred::

        >>> from sqlalchemy.orm import undefer
        >>> book = session.scalar(select(Book).where(Book.id == 2).options(undefer(Book.summary)))
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary
        FROM book
        WHERE book.id = ?
        [...] (2,)

    The ``Book.summary`` column was now eagerly loaded, and may be accessed without additional SQL being emitted::

        >>> print(book.summary)
        another long summary

.. _orm_queryguide_deferred_group:

按组加载延迟列
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Loading deferred columns in groups

.. tab:: 中文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    通常情况下，当某列通过 ``mapped_column(deferred=True)`` 进行映射时，当对象访问该延迟加载的属性时，将会发出一条 SQL 语句来仅加载该特定列，而不会加载其他列，即使该映射中还有其他也被标记为延迟加载的列。在常见情况下，如果该延迟属性属于一组应当一次性加载的属性，而不是为每个属性分别发出 SQL，则可以使用 :paramref:`_orm.mapped_column.deferred_group` 参数。该参数接受一个任意字符串，用于定义一个共同的列组，这些列将在访问其中任何一个时一并取消延迟加载::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(
        ...         Text, deferred=True, deferred_group="book_attrs"
        ...     )
        ...     cover_photo: Mapped[bytes] = mapped_column(
        ...         LargeBinary, deferred=True, deferred_group="book_attrs"
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    使用上述映射，当访问 ``summary`` 或 ``cover_photo`` 任一属性时，两者将通过一条 SELECT 语句一并加载::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> img_data, summary = book.cover_photo, book.summary
        {execsql}SELECT book.summary AS book_summary, book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)


.. tab:: 英文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    Normally when a column is mapped with ``mapped_column(deferred=True)``, when the deferred attribute is accessed on an object, SQL will be emitted to load only that specific column and no others, even if the mapping has other columns that are also marked as deferred. In the common case that the deferred attribute is part of a group of attributes that should all load at once, rather than emitting SQL for each attribute individually, the :paramref:`_orm.mapped_column.deferred_group` parameter may be used, which accepts an arbitrary string which will define a common group of columns to be undeferred::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(
        ...         Text, deferred=True, deferred_group="book_attrs"
        ...     )
        ...     cover_photo: Mapped[bytes] = mapped_column(
        ...         LargeBinary, deferred=True, deferred_group="book_attrs"
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    Using the above mapping, accessing either ``summary`` or ``cover_photo`` will load both columns at once using just one SELECT statement::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> img_data, summary = book.cover_photo, book.summary
        {execsql}SELECT book.summary AS book_summary, book.cover_photo AS book_cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)


使用 ``undefer_group()`` 按组取消延迟
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Undeferring by group with ``undefer_group()``

.. tab:: 中文

    如果延迟加载的列使用 :paramref:`_orm.mapped_column.deferred_group` 参数进行了配置，如前一节所介绍的那样，那么可以使用 :func:`_orm.undefer_group` 选项，通过传入该组的字符串名称，实现整组列的预加载（即非延迟加载）::

        >>> from sqlalchemy.orm import undefer_group
        >>> book = session.scalar(
        ...     select(Book).where(Book.id == 2).options(undefer_group("book_attrs"))
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)

    此时 ``summary`` 和 ``cover_photo`` 两列都已加载，无需额外的数据库访问::

        >>> img_data, summary = book.cover_photo, book.summary

.. tab:: 英文

    If deferred columns are configured with :paramref:`_orm.mapped_column.deferred_group` as introduced in the preceding section, the entire group may be indicated to load eagerly using the :func:`_orm.undefer_group` option, passing the string name of the group to be eagerly loaded::

        >>> from sqlalchemy.orm import undefer_group
        >>> book = session.scalar(
        ...     select(Book).where(Book.id == 2).options(undefer_group("book_attrs"))
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)

    Both ``summary`` and ``cover_photo`` are available without additional loads::

        >>> img_data, summary = book.cover_photo, book.summary

对通配符取消延迟
^^^^^^^^^^^^^^^^^^^^^^^^

Undeferring on wildcards

.. tab:: 中文

    大多数 ORM 加载选项都接受通配表达式 ``"*"``，表示该选项应应用于所有相关属性。如果某个映射包含一系列延迟加载的列，那么可以通过使用通配符一次性取消所有列的延迟加载，无需使用组名::

        >>> book = session.scalar(select(Book).where(Book.id == 3).options(undefer("*")))
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (3,)

.. tab:: 英文

    Most ORM loader options accept a wildcard expression, indicated by ``"*"``, which indicates that the option should be applied to all relevant attributes.   If a mapping has a series of deferred columns, all such columns can be undeferred at once, without using a group name, by indicating a wildcard::

        >>> book = session.scalar(select(Book).where(Book.id == 3).options(undefer("*")))
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (3,)

.. _orm_queryguide_mapper_deferred_raiseload:

配置映射器级“raiseload”行为
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Configuring mapper-level "raiseload" behavior

.. tab:: 中文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    在 :ref:`orm_queryguide_deferred_raiseload` 中首次介绍的 "raiseload" 行为，也可以作为默认的 mapper 级别行为使用，方法是使用 :paramref:`_orm.mapped_column.deferred_raiseload` 参数配置 :func:`_orm.mapped_column`。启用该参数后，相关列在任何情况下访问都会抛出异常，除非在查询时通过 :func:`_orm.undefer` 或 :func:`_orm.load_only` 显式取消延迟加载::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text, deferred=True, deferred_raiseload=True)
        ...     cover_photo: Mapped[bytes] = mapped_column(
        ...         LargeBinary, deferred=True, deferred_raiseload=True
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    在上述映射中，``.summary`` 和 ``.cover_photo`` 两列默认是不可访问的::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> book.summary
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.summary' is not available due to raiseload=True

    只有在查询时通过 :func:`_orm.undefer` 或 :func:`_orm.undefer_group`，或较不常见的 :func:`_orm.defer` 显式指定，才能加载这些属性。以下示例中，使用 ``undefer('*')`` 取消所有列的延迟加载，同时通过 :ref:`orm_queryguide_populate_existing` 强制刷新已加载对象的加载策略::

        >>> book = session.scalar(
        ...     select(Book)
        ...     .where(Book.id == 2)
        ...     .options(undefer("*"))
        ...     .execution_options(populate_existing=True)
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> book.summary
        'another long summary'


.. tab:: 英文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass

    The "raiseload" behavior first introduced at :ref:`orm_queryguide_deferred_raiseload` may also be applied as a default mapper-level behavior, using the :paramref:`_orm.mapped_column.deferred_raiseload` parameter of :func:`_orm.mapped_column`.  When using this parameter, the affected columns will raise on access in all cases unless explicitly "undeferred" using :func:`_orm.undefer` or :func:`_orm.load_only` at query time::

        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text, deferred=True, deferred_raiseload=True)
        ...     cover_photo: Mapped[bytes] = mapped_column(
        ...         LargeBinary, deferred=True, deferred_raiseload=True
        ...     )
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"

    Using the above mapping, the ``.summary`` and ``.cover_photo`` columns are by default not loadable::

        >>> book = session.scalar(select(Book).where(Book.id == 2))
        {execsql}SELECT book.id, book.owner_id, book.title
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> book.summary
        Traceback (most recent call last):
        ...
        sqlalchemy.exc.InvalidRequestError: 'Book.summary' is not available due to raiseload=True

    Only by overriding their behavior at query time, typically using :func:`_orm.undefer` or :func:`_orm.undefer_group`, or less commonly :func:`_orm.defer`, may the attributes be loaded.  The example below applies ``undefer('*')`` to undefer all attributes, also making use of :ref:`orm_queryguide_populate_existing` to refresh the already-loaded object's loader options::

        >>> book = session.scalar(
        ...     select(Book)
        ...     .where(Book.id == 2)
        ...     .options(undefer("*"))
        ...     .execution_options(populate_existing=True)
        ... )
        {execsql}SELECT book.id, book.owner_id, book.title, book.summary, book.cover_photo
        FROM book
        WHERE book.id = ?
        [...] (2,)
        {stop}>>> book.summary
        'another long summary'



.. _orm_queryguide_with_expression:

将任意 SQL 表达式加载到对象上
-----------------------------------------------

Loading Arbitrary SQL Expressions onto Objects

.. tab:: 中文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass
        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     fullname: Mapped[Optional[str]]
        ...     books: Mapped[List["Book"]] = relationship(back_populates="owner")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text)
        ...     cover_photo: Mapped[bytes] = mapped_column(LargeBinary)
        ...     owner: Mapped["User"] = relationship(back_populates="books")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"
    
    如在 :ref:`orm_queryguide_select_columns` 以及其他部分所讨论的，:func:`.select` 构造可用于在结果集中加载任意 SQL 表达式。例如，如果我们想发出一个查询，加载 ``User`` 对象的同时，还统计每位 ``User`` 拥有多少本书，我们可以使用 ``func.count(Book.id)`` 将一个“计数”列添加到查询中，同时包括对 ``Book`` 的 JOIN 以及按所有者 ID 进行的 GROUP BY。这样将会返回 :class:`.Row` 对象，每行包含两个条目，一个是 ``User``，另一个是 ``func.count(Book.id)``::
    
        >>> from sqlalchemy import func
        >>> stmt = select(User, func.count(Book.id)).join_from(User, Book).group_by(Book.owner_id)
        >>> for user, book_count in session.execute(stmt):
        ...     print(f"Username: {user.name}  Number of books: {book_count}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        count(book.id) AS count_1
        FROM user_account JOIN book ON user_account.id = book.owner_id
        GROUP BY book.owner_id
        [...] ()
        {stop}Username: spongebob  Number of books: 3
        Username: sandy  Number of books: 3
    
    在上述示例中， ``User`` 实体和“图书数量”SQL 表达式是分别返回的。但一种常见用例是构造一个只返回 ``User`` 对象的查询，例如可以用 :meth:`_orm.Session.scalars` 来遍历，并将 ``func.count(Book.id)`` 的结果 *动态地* 应用于每个 ``User`` 实例。最终结果类似于将任意 SQL 表达式映射到类上的 :func:`_orm.column_property` 的效果，不同的是表达式可以在查询时动态设置。SQLAlchemy 为这种用例提供了 :func:`_orm.with_expression` 加载选项，配合映射级别的 :func:`_orm.query_expression` 指令即可实现此功能。
    
    要在查询中使用 :func:`_orm.with_expression`，被映射的类必须预先使用 :func:`_orm.query_expression` 指令配置一个 ORM 映射属性；该指令将在类上生成一个适合接收查询时 SQL 表达式的属性。以下我们向 ``User`` 添加一个新属性 ``User.book_count``。该属性是只读的，没有默认值；如果未填充值，在加载实例上访问时通常为 ``None``::
    
        >>> from sqlalchemy.orm import query_expression
        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     fullname: Mapped[Optional[str]]
        ...     book_count: Mapped[int] = query_expression()
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
    
    在映射中配置好 ``User.book_count`` 属性之后，我们就可以使用 :func:`_orm.with_expression` 加载选项，将一个 SQL 表达式应用到每个 ``User`` 实例上::
    
        >>> from sqlalchemy.orm import with_expression
        >>> stmt = (
        ...     select(User)
        ...     .join_from(User, Book)
        ...     .group_by(Book.owner_id)
        ...     .options(with_expression(User.book_count, func.count(Book.id)))
        ... )
        >>> for user in session.scalars(stmt):
        ...     print(f"Username: {user.name}  Number of books: {user.book_count}")
        {execsql}SELECT count(book.id) AS count_1, user_account.id, user_account.name,
        user_account.fullname
        FROM user_account JOIN book ON user_account.id = book.owner_id
        GROUP BY book.owner_id
        [...] ()
        {stop}Username: spongebob  Number of books: 3
        Username: sandy  Number of books: 3
    
    在上述示例中，我们将 ``func.count(Book.id)`` 表达式从 :func:`_sql.select` 的列参数中移除，转而放入 :func:`_orm.with_expression` 加载选项中。ORM 会将其视为一种特殊的列加载选项，动态应用于查询语句。
    
    关于 :func:`.query_expression` 映射有以下注意事项：
    
    * 如果某个对象没有通过 :func:`_orm.with_expression` 填充该属性，那么该属性的值将是 ``None``，除非在映射中设置了 :paramref:`_orm.query_expression.default_expr` 来指定默认 SQL 表达式。
    
    * :func:`_orm.with_expression` 的值 **不会填充已加载的对象**，除非使用 :ref:`orm_queryguide_populate_existing`。下面的示例是 **无效** 的，因为对象 ``A`` 已经被加载：
    
      .. sourcecode:: python
    
            # 加载第一个 A
            obj = session.scalars(select(A).order_by(A.id)).first()
    
            # 使用加载选项再次加载同一个 A；表达式不会被应用
            obj = session.scalars(select(A).options(with_expression(A.expr, some_expr))).first()
    
      若想在已加载对象上重新填充值，需要使用 :ref:`orm_queryguide_populate_existing` 执行选项确保所有列都被重新加载：
    
      .. sourcecode:: python
    
            obj = session.scalars(
                select(A)
                .options(with_expression(A.expr, some_expr))
                .execution_options(populate_existing=True)
            ).first()
    
    * 一旦对象过期（通过 :meth:`.Session.expire` 或 :meth:`.Session.commit` 的 `expire_on_commit` 行为），:func:`_orm.with_expression` 表达式 **将失效**。表达式与其值不再与属性绑定，之后访问会返回 ``None``。
    
    * :func:`_orm.with_expression` 作为对象加载选项，仅在 **最外层查询** 中生效，仅适用于完整实体的查询，不适用于任意列选择、子查询或复合语句（如 UNION）的子元素。参见下一节 :ref:`orm_queryguide_with_expression_unions` 示例。
    
    * 被映射的属性 **不能** 用于查询中的其他部分，例如 WHERE 子句或 ORDER BY 子句中引用临时表达式；如下写法 **无效**：
    
      .. sourcecode:: python
    
            # 无法在查询中引用 A.expr
            stmt = (
                select(A)
                .options(with_expression(A.expr, A.x + A.y))
                .filter(A.expr > 5)
                .order_by(A.expr)
            )
    
      上述 WHERE 和 ORDER BY 子句中的 ``A.expr`` 表达式将解析为 NULL。若要在查询中多处使用该表达式，应提前赋值为变量，然后引用变量：
    
      .. sourcecode:: python
    
            # 提前定义所需表达式，在查询中引用
            a_expr = A.x + A.y
            stmt = (
                select(A)
                .options(with_expression(A.expr, a_expr))
                .filter(a_expr > 5)
                .order_by(a_expr)
            )
    
    .. seealso::
    
        :func:`_orm.with_expression` 是一个特殊选项，用于在查询时将 SQL 表达式动态应用于映射类。若要将固定 SQL 表达式配置在映射上，请参见 :ref:`mapper_sql_expressions`。
    

.. tab:: 英文

    .. comment

        >>> class Base(DeclarativeBase):
        ...     pass
        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     fullname: Mapped[Optional[str]]
        ...     books: Mapped[List["Book"]] = relationship(back_populates="owner")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text)
        ...     cover_photo: Mapped[bytes] = mapped_column(LargeBinary)
        ...     owner: Mapped["User"] = relationship(back_populates="books")
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"


    As discussed :ref:`orm_queryguide_select_columns` and elsewhere, the :func:`.select` construct may be used to load arbitrary SQL expressions in a result set.  Such as if we wanted to issue a query that loads ``User`` objects, but also includes a count of how many books each ``User`` owned, we could use ``func.count(Book.id)`` to add a "count" column to a query which includes a JOIN to ``Book`` as well as a GROUP BY owner id.  This will yield :class:`.Row` objects that each contain two entries, one for ``User`` and one for ``func.count(Book.id)``::
    
        >>> from sqlalchemy import func
        >>> stmt = select(User, func.count(Book.id)).join_from(User, Book).group_by(Book.owner_id)
        >>> for user, book_count in session.execute(stmt):
        ...     print(f"Username: {user.name}  Number of books: {book_count}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname,
        count(book.id) AS count_1
        FROM user_account JOIN book ON user_account.id = book.owner_id
        GROUP BY book.owner_id
        [...] ()
        {stop}Username: spongebob  Number of books: 3
        Username: sandy  Number of books: 3
    
    In the above example, the ``User`` entity and the "book count" SQL expression are returned separately. However, a popular use case is to produce a query that will yield ``User`` objects alone, which can be iterated for example using :meth:`_orm.Session.scalars`, where the result of the ``func.count(Book.id)`` SQL expression is applied *dynamically* to each ``User`` entity. The end result would be similar to the case where an arbitrary SQL expression were mapped to the class using :func:`_orm.column_property`, except that the SQL expression can be modified at query time. For this use case SQLAlchemy provides the :func:`_orm.with_expression` loader option, which when combined with the mapper level :func:`_orm.query_expression` directive may produce this result.
    
    .. comment
    
        >>> class Base(DeclarativeBase):
        ...     pass
        >>> class Book(Base):
        ...     __tablename__ = "book"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     owner_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"))
        ...     title: Mapped[str]
        ...     summary: Mapped[str] = mapped_column(Text)
        ...     cover_photo: Mapped[bytes] = mapped_column(LargeBinary)
        ...
        ...     def __repr__(self) -> str:
        ...         return f"Book(id={self.id!r}, title={self.title!r})"
    
    
    To apply :func:`_orm.with_expression` to a query, the mapped class must have pre-configured an ORM mapped attribute using the :func:`_orm.query_expression` directive; this directive will produce an attribute on the mapped class that is suitable for receiving query-time SQL expressions.  Below we add a new attribute ``User.book_count`` to ``User``.  This ORM mapped attribute is read-only and has no default value; accessing it on a loaded instance will normally produce ``None``::
    
        >>> from sqlalchemy.orm import query_expression
        >>> class User(Base):
        ...     __tablename__ = "user_account"
        ...     id: Mapped[int] = mapped_column(primary_key=True)
        ...     name: Mapped[str]
        ...     fullname: Mapped[Optional[str]]
        ...     book_count: Mapped[int] = query_expression()
        ...
        ...     def __repr__(self) -> str:
        ...         return f"User(id={self.id!r}, name={self.name!r}, fullname={self.fullname!r})"
    
    With the ``User.book_count`` attribute configured in our mapping, we may populate it with data from a SQL expression using the :func:`_orm.with_expression` loader option to apply a custom SQL expression to each ``User`` object as it's loaded::
    
        >>> from sqlalchemy.orm import with_expression
        >>> stmt = (
        ...     select(User)
        ...     .join_from(User, Book)
        ...     .group_by(Book.owner_id)
        ...     .options(with_expression(User.book_count, func.count(Book.id)))
        ... )
        >>> for user in session.scalars(stmt):
        ...     print(f"Username: {user.name}  Number of books: {user.book_count}")
        {execsql}SELECT count(book.id) AS count_1, user_account.id, user_account.name,
        user_account.fullname
        FROM user_account JOIN book ON user_account.id = book.owner_id
        GROUP BY book.owner_id
        [...] ()
        {stop}Username: spongebob  Number of books: 3
        Username: sandy  Number of books: 3
    
    Above, we moved our ``func.count(Book.id)`` expression out of the columns argument of the :func:`_sql.select` construct and into the :func:`_orm.with_expression` loader option.  The ORM then considers this to be a special column load option that's applied dynamically to the statement.
    
    The :func:`.query_expression` mapping has these caveats:
    
    * On an object where :func:`_orm.with_expression` were not used to populate the attribute, the attribute on an object instance will have the value ``None``, unless on the mapping the :paramref:`_orm.query_expression.default_expr` parameter is set to a default SQL expression.
    
    * The :func:`_orm.with_expression` value **does not populate on an object that is already loaded**, unless :ref:`orm_queryguide_populate_existing` is used. The example below will **not work**, as the ``A`` object is already loaded:
    
      .. sourcecode:: python
    
            # load the first A
            obj = session.scalars(select(A).order_by(A.id)).first()
    
            # load the same A with an option; expression will **not** be applied
            # to the already-loaded object
            obj = session.scalars(select(A).options(with_expression(A.expr, some_expr))).first()
    
      To ensure the attribute is re-loaded on an existing object, use the :ref:`orm_queryguide_populate_existing` execution option to ensure all columns are re-populated:
    
      .. sourcecode:: python
    
            obj = session.scalars(
                select(A)
                .options(with_expression(A.expr, some_expr))
                .execution_options(populate_existing=True)
            ).first()
    
    * The :func:`_orm.with_expression` SQL expression **is lost when the object is expired**.  Once the object is expired, either via :meth:`.Session.expire` or via the expire_on_commit behavior of :meth:`.Session.commit`, the SQL expression and its value is no longer associated with the attribute and will return ``None`` on subsequent access.
    
    * :func:`_orm.with_expression`, as an object loading option, only takes effect on the **outermost part of a query** and only for a query against a full entity, and not for arbitrary column selects, within subqueries, or the elements of a compound statement such as a UNION.  See the next section :ref:`orm_queryguide_with_expression_unions` for an example.
    
    * The mapped attribute **cannot** be applied to other parts of the query, such as the WHERE clause, the ORDER BY clause, and make use of the ad-hoc expression; that is, this won't work:
    
      .. sourcecode:: python
    
            # can't refer to A.expr elsewhere in the query
            stmt = (
                select(A)
                .options(with_expression(A.expr, A.x + A.y))
                .filter(A.expr > 5)
                .order_by(A.expr)
            )
    
      The ``A.expr`` expression will resolve to NULL in the above WHERE clause and ORDER BY clause. To use the expression throughout the query, assign to a variable and use that:
    
      .. sourcecode:: python
    
            # assign desired expression up front, then refer to that in
            # the query
            a_expr = A.x + A.y
            stmt = (
                select(A)
                .options(with_expression(A.expr, a_expr))
                .filter(a_expr > 5)
                .order_by(a_expr)
            )
    
    .. seealso::
    
        The :func:`_orm.with_expression` option is a special option used to apply SQL expressions to mapped classes dynamically at query time. For ordinary fixed SQL expressions configured on mappers, see the section :ref:`mapper_sql_expressions`.

.. _orm_queryguide_with_expression_unions:

使用 ``with_expression()`` 处理 UNION 和其他子查询
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ``with_expression()`` with UNIONs, other subqueries

.. tab:: 中文

    .. comment

    >>> session.close()

    :func:`_orm.with_expression` 构造是一个 ORM 加载选项，因此 **只能应用于 SELECT 语句的最外层**，即用于加载特定 ORM 实体的查询。  
    如果它被用于 :func:`_sql.select` 语句中，而该语句随后会作为子查询或复合语句（如 UNION）中的元素，则该选项不会生效。

    若要在子查询中使用任意 SQL 表达式，应使用常规 Core 风格的方法添加表达式。  
    要将子查询派生的表达式赋值给 ORM 实体的 :func:`_orm.query_expression` 属性，应在 ORM 对象加载的最外层使用 :func:`_orm.with_expression`，并引用子查询中的 SQL 表达式。

    在以下示例中，两个 :func:`_sql.select` 构造分别用于 ORM 实体 ``A``，并在其中添加了一个 SQL 表达式并标记为 ``expr``，两者通过 :func:`_sql.union_all` 组合。然后，在最外层使用 :ref:`orm_queryguide_unions` 中描述的查询技术，从该 UNION 中选择 ``A`` 实体，并使用 :func:`_orm.with_expression` 选项，将 SQL 表达式提取到新加载的 ``A`` 实例上::

        >>> from sqlalchemy import union_all
        >>> s1 = (
        ...     select(User, func.count(Book.id).label("book_count"))
        ...     .join_from(User, Book)
        ...     .where(User.name == "spongebob")
        ... )
        >>> s2 = (
        ...     select(User, func.count(Book.id).label("book_count"))
        ...     .join_from(User, Book)
        ...     .where(User.name == "sandy")
        ... )
        >>> union_stmt = union_all(s1, s2)
        >>> orm_stmt = (
        ...     select(User)
        ...     .from_statement(union_stmt)
        ...     .options(with_expression(User.book_count, union_stmt.selected_columns.book_count))
        ... )
        >>> for user in session.scalars(orm_stmt):
        ...     print(f"Username: {user.name}  Number of books: {user.book_count}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname, count(book.id) AS book_count
        FROM user_account JOIN book ON user_account.id = book.owner_id
        WHERE user_account.name = ?
        UNION ALL
        SELECT user_account.id, user_account.name, user_account.fullname, count(book.id) AS book_count
        FROM user_account JOIN book ON user_account.id = book.owner_id
        WHERE user_account.name = ?
        [...] ('spongebob', 'sandy'){stop}
        Username: spongebob  Number of books: 3  
        Username: sandy  Number of books: 3


.. tab:: 英文

    .. comment

    >>> session.close()

    The :func:`_orm.with_expression` construct is an ORM loader option, and as such may only be applied to the outermost level of a SELECT statement which is to load a particular ORM entity.   It does not have any effect if used inside of a :func:`_sql.select` that will then be used as a subquery or as an element within a compound statement such as a UNION.

    In order to use arbitrary SQL expressions in subqueries, normal Core-style means of adding expressions should be used. To assemble a subquery-derived expression onto the ORM entity's :func:`_orm.query_expression` attributes, :func:`_orm.with_expression` is used at the top layer of ORM object loading, referencing the SQL expression within the subquery.

    In the example below, two :func:`_sql.select` constructs are used against the ORM entity ``A`` with an additional SQL expression labeled in ``expr``, and combined using :func:`_sql.union_all`.  Then, at the topmost layer, the ``A`` entity is SELECTed from this UNION, using the querying technique described at :ref:`orm_queryguide_unions`, adding an option with :func:`_orm.with_expression` to extract this SQL expression onto newly loaded instances of ``A``::

        >>> from sqlalchemy import union_all
        >>> s1 = (
        ...     select(User, func.count(Book.id).label("book_count"))
        ...     .join_from(User, Book)
        ...     .where(User.name == "spongebob")
        ... )
        >>> s2 = (
        ...     select(User, func.count(Book.id).label("book_count"))
        ...     .join_from(User, Book)
        ...     .where(User.name == "sandy")
        ... )
        >>> union_stmt = union_all(s1, s2)
        >>> orm_stmt = (
        ...     select(User)
        ...     .from_statement(union_stmt)
        ...     .options(with_expression(User.book_count, union_stmt.selected_columns.book_count))
        ... )
        >>> for user in session.scalars(orm_stmt):
        ...     print(f"Username: {user.name}  Number of books: {user.book_count}")
        {execsql}SELECT user_account.id, user_account.name, user_account.fullname, count(book.id) AS book_count
        FROM user_account JOIN book ON user_account.id = book.owner_id
        WHERE user_account.name = ?
        UNION ALL
        SELECT user_account.id, user_account.name, user_account.fullname, count(book.id) AS book_count
        FROM user_account JOIN book ON user_account.id = book.owner_id
        WHERE user_account.name = ?
        [...] ('spongebob', 'sandy'){stop}
        Username: spongebob  Number of books: 3
        Username: sandy  Number of books: 3



列加载 API
-------------------

Column Loading API

.. tab:: 中文

.. tab:: 英文

.. autofunction:: defer

.. autofunction:: deferred

.. autofunction:: query_expression

.. autofunction:: load_only

.. autofunction:: undefer

.. autofunction:: undefer_group

.. autofunction:: with_expression

.. comment

  >>> session.close()
  >>> conn.close()
  ROLLBACK...
