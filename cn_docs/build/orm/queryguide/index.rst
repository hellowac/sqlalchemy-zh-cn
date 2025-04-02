.. highlight:: pycon+sql

.. _queryguide_toplevel:

==================
ORM 查询指南
==================

ORM Querying Guide

.. tab:: 中文

    本节概述了使用 SQLAlchemy ORM 发出查询的 `2.0 风格` (:term:`2.0 style`) 使用方法。

    阅读本节的读者应熟悉 :ref:`unified_tutorial` 中的 SQLAlchemy 概述，特别是这里的大部分内容扩展了 :ref:`tutorial_selecting_data` 中的内容。

    .. admonition:: 对于 SQLAlchemy 1.x 用户

        在 SQLAlchemy 2.x 系列中，ORM 的 SQL SELECT 语句使用与 Core 中相同的 :func:`_sql.select` 构造来构建，然后使用 :class:`_orm.Session` 的 :meth:`_orm.Session.execute` 方法调用（正如现在用于 :ref:`orm_expression_update_delete` 功能的 :func:`_sql.update` 和 :func:`_sql.delete` 构造）。然而，遗留的 :class:`_query.Query` 对象继续作为新系统上的一个薄外观可用，以支持基于 1.x 系列构建的应用程序，无需全面替换所有查询。有关此对象的参考，请参阅 :ref:`query_api_toplevel` 部分。

.. tab:: 英文

    This section provides an overview of emitting queries with the
    SQLAlchemy ORM using :term:`2.0 style` usage.

    Readers of this section should be familiar with the SQLAlchemy overview
    at :ref:`unified_tutorial`, and in particular most of the content here expands
    upon the content at :ref:`tutorial_selecting_data`.

    .. admonition:: For users of SQLAlchemy 1.x

        In the SQLAlchemy 2.x series, SQL SELECT statements for the ORM are
        constructed using the same :func:`_sql.select` construct as is used in
        Core, which is then invoked in terms of a :class:`_orm.Session` using the
        :meth:`_orm.Session.execute` method (as are the :func:`_sql.update` and
        :func:`_sql.delete` constructs now used for the
        :ref:`orm_expression_update_delete` feature). However, the legacy
        :class:`_query.Query` object, which performs these same steps as more of an
        "all-in-one" object, continues to remain available as a thin facade over
        this new system, to support applications that were built on the 1.x series
        without the need for wholesale replacement of all queries. For reference on
        this object, see the section :ref:`query_api_toplevel`.




.. toctree::
    :maxdepth: 3

    select
    inheritance
    dml
    columns
    relationships
    api
    query
