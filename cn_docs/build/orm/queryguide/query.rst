.. highlight:: pycon+sql
.. |prev| replace:: :doc:`api`

.. |tutorial_title| replace:: ORM Querying Guide

.. topic:: |tutorial_title|

      This page is part of the :doc:`index`.

      Previous: |prev|


.. currentmodule:: sqlalchemy.orm

.. _query_api_toplevel:

================
旧式查询 API
================

Legacy Query API

.. tab:: 中文

    .. admonition:: 关于遗留查询 API

        本页包含用于 :class:`_query.Query` 构造的 Python 生成文档，多年来，这是使用 SQLAlchemy ORM 时的唯一 SQL 接口。从 2.0 版本开始，一种全新的工作方式成为了标准方法，同样的 :func:`_sql.select` 构造在 Core 和 ORM 中都能很好地工作，提供了一致的查询构建接口。

        对于基于 2.0 API 之前的 SQLAlchemy ORM 构建的任何应用程序，:class:`_query.Query` API 通常代表应用程序中绝大多数的数据库访问代码，因此 :class:`_query.Query` API 的大多数内容 **不会从 SQLAlchemy 中移除** 。:class:`_query.Query` 对象在后台执行时现在会将自身转换为 2.0 风格的 :func:`_sql.select` 对象，因此现在只是一个非常薄的适配器 API。

        有关将基于 :class:`_query.Query` 的应用程序迁移到 2.0 风格的指南，请参阅 :ref:`migration_20_query_usage`。

        有关 2.0 风格的 ORM 对象 SQL 编写简介，请参阅 :ref:`unified_tutorial`。2.0 风格查询的其他参考资料见 :ref:`queryguide_toplevel`。

.. tab:: 英文

    .. admonition:: About the Legacy Query API


        This page contains the Python generated documentation for the
        :class:`_query.Query` construct, which for many years was the sole SQL
        interface when working with the SQLAlchemy ORM.  As of version 2.0, an all
        new way of working is now the standard approach, where the same
        :func:`_sql.select` construct that works for Core works just as well for the
        ORM, providing a consistent interface for building queries.

        For any application that is built on the SQLAlchemy ORM prior to the
        2.0 API, the :class:`_query.Query` API will usually represents the vast
        majority of database access code within an application, and as such the
        majority of the :class:`_query.Query` API is
        **not being removed from SQLAlchemy**.  The :class:`_query.Query` object
        behind the scenes now translates itself into a 2.0 style :func:`_sql.select`
        object when the :class:`_query.Query` object is executed, so it now is
        just a very thin adapter API.

        For a guide to migrating an application based on :class:`_query.Query`
        to 2.0 style, see :ref:`migration_20_query_usage`.

        For an introduction to writing SQL for ORM objects in the 2.0 style,
        start with the :ref:`unified_tutorial`.  Additional reference for 2.0 style
        querying is at :ref:`queryguide_toplevel`.

查询对象
================

The Query Object

.. tab:: 中文

    :class:`_query.Query` 是通过给定的 :class:`~.Session` 使用 :meth:`~.Session.query` 方法生成的::

        q = session.query(SomeMappedClass)

    以下是 :class:`_query.Query` 对象的完整接口。

.. tab:: 英文

    :class:`_query.Query` is produced in terms of a given :class:`~.Session`, using the :meth:`~.Session.query` method::

        q = session.query(SomeMappedClass)

    Following is the full interface for the :class:`_query.Query` object.

.. autoclass:: sqlalchemy.orm.Query
   :members:
   :inherited-members:

ORM 特定的查询构造
=============================

ORM-Specific Query Constructs

.. tab:: 中文

    本节已移至 :ref:`queryguide_additional`。

.. tab:: 英文

    This section has moved to :ref:`queryguide_additional`.
