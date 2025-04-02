.. |tutorial_title| replace:: SQLAlchemy 统一教程
.. |next| replace:: :doc:`engine`

.. footer_topic:: |tutorial_title|

      Next Section: |next|

.. _unified_tutorial:

.. rst-class:: orm_core

============================
SQLAlchemy 统一教程
============================

SQLAlchemy Unified Tutorial

.. tab:: 中文
    
    |

    .. admonition:: 关于本文档

        SQLAlchemy 统一教程集成了 SQLAlchemy 的核心组件和 ORM 组件，作为 SQLAlchemy 的整体介绍。
        对于使用 1.x 系列的 SQLAlchemy 用户，在 `2.0 风格` (:term:`2.0 style`) 的工作中，ORM 使用核心风格的查询，使用 :func:`_sql.select` 构造，核心连接和 ORM 会话之间的事务语义是等效的。
        请注意每个部分的蓝色边框样式，这将告诉您特定主题的 "ORM-ish" 程度！

        已经熟悉 SQLAlchemy 的用户，特别是那些希望将现有应用程序迁移到 SQLAlchemy 2.0 系列中的 1.4 过渡阶段的用户，也应查看 :ref:`migration_20_toplevel` 文档。

        对于新手来说，本文件包含 **很多** 细节，不过到最后他们将被认为是 **Alchemist**。

    SQLAlchemy 以两个不同的 API 形式呈现，一个构建在另一个之上。这些 API 被称为 **Core** 和 **ORM**。

    |

        **SQLAlchemy Core** 是 SQLAlchemy 作为 "数据库工具包" 的基础架构。该库提供了管理与数据库连接、与数据库查询和结果交互以及程序化构建 SQL 语句的工具。

        **主要是 Core-only** 的部分不会涉及 ORM。这些部分使用的 SQLAlchemy 构造将从 ``sqlalchemy`` 命名空间导入。作为主题分类的额外指示，它们还将在右侧包含一个 **深蓝色边框**。
        在使用 ORM 时，这些概念仍然有效，但在用户代码中不太明显。ORM 用户应阅读这些部分，但不应期望直接使用这些 API 进行以 ORM 为中心的代码。

    |

        **SQLAlchemy ORM** 构建在 Core 之上，提供可选的 **对象关系映射** 功能。ORM 提供了一个额外的配置层，允许用户定义的 Python 类 **映射** 到数据库表和其他构造，以及称为 **Session** 的对象持久化机制。
        然后它扩展了 Core 级别的 SQL 表达式语言，以允许 SQL 查询在用户定义的对象的术语中被组合和调用。

        **主要是 ORM-only** 的部分应 **标题包含 "ORM" 一词**，以便明确这是一个与 ORM 相关的主题。这些部分使用的 SQLAlchemy 构造将从 ``sqlalchemy.orm`` 命名空间导入。
        最后，作为主题分类的额外指示，它们还将在左侧包含一个 **浅蓝色边框**。仅使用 Core 的用户可以跳过这些部分。

    |

        **大多数** 本教程中的部分讨论了 **与 ORM 一起显式使用的 Core 概念**。特别是 SQLAlchemy 2.0 在 ORM 中的 Core API 使用集成度更高。

        对于每个这些部分，将有 **介绍性文本** 讨论 ORM 用户应期望使用这些编程模式的程度。这些部分使用的 SQLAlchemy 构造将从 ``sqlalchemy`` 命名空间导入，同时可能使用 ``sqlalchemy.orm`` 构造。
        作为主题分类的额外指示，这些部分还将包含 **左侧较薄的浅边框和右侧较厚的深边框**。Core 和 ORM 用户应同等熟悉这些部分中的概念。

.. tab:: 英文

    |

    .. admonition:: About this document

        The SQLAlchemy Unified Tutorial is integrated between the Core and ORM
        components of SQLAlchemy and serves as a unified introduction to SQLAlchemy
        as a whole. For users of SQLAlchemy within the 1.x series, in the
        :term:`2.0 style` of working, the ORM uses Core-style querying with the
        :func:`_sql.select` construct, and transactional semantics between Core
        connections and ORM sessions are equivalent. Take note of the blue border
        styles for each section, that will tell you how "ORM-ish" a particular
        topic is!

        Users who are already familiar with SQLAlchemy, and especially those
        looking to migrate existing applications to work under the SQLAlchemy 2.0
        series within the 1.4 transitional phase should check out the
        :ref:`migration_20_toplevel` document as well.

        For the newcomer, this document has a **lot** of detail, however by the
        end they will be considered an **Alchemist**.

    SQLAlchemy is presented as two distinct APIs, one building on top of the other.
    These APIs are known as **Core** and **ORM**.

    |

        **SQLAlchemy Core** is the foundational architecture for SQLAlchemy as a
        "database toolkit".  The library provides tools for managing connectivity
        to a database, interacting with database queries and results, and
        programmatic construction of SQL statements.

        Sections that are **primarily Core-only** will not refer to the ORM.
        SQLAlchemy constructs used in these sections will be imported from the
        ``sqlalchemy`` namespace. As an additional indicator of subject
        classification, they will also include a **dark blue border on the right**.
        When using the ORM, these concepts are still in play but are less often
        explicit in user code. ORM users should read these sections, but not expect
        to be using these APIs directly for ORM-centric code.

    |

        **SQLAlchemy ORM** builds upon the Core to provide optional **object
        relational mapping** capabilities.   The ORM provides an additional
        configuration layer allowing user-defined Python classes to be **mapped**
        to database tables and other constructs, as well as an object persistence
        mechanism known as the **Session**.   It then extends the Core-level
        SQL Expression Language to allow SQL queries to be composed and invoked
        in terms of user-defined objects.

        Sections that are **primarily ORM-only** should be **titled to
        include the phrase "ORM"**, so that it's clear this is an ORM related topic.
        SQLAlchemy constructs used in these sections will be imported from the
        ``sqlalchemy.orm`` namespace. Finally, as an additional indicator of
        subject classification, they will also include a **light blue border on the
        left**. Core-only users can skip these.

    |

        **Most** sections in this tutorial discuss **Core concepts that
        are also used explicitly with the ORM**. SQLAlchemy 2.0 in particular
        features a much greater level of integration of Core API use within the
        ORM.

        For each of these sections, there will be **introductory text** discussing the
        degree to which ORM users should expect to be using these programming
        patterns. SQLAlchemy constructs in these sections will be imported from the
        ``sqlalchemy`` namespace with some potential use of ``sqlalchemy.orm``
        constructs at the same time. As an additional indicator of subject
        classification, these sections will also include **both a thinner light
        border on the left, and a thicker dark border on the right**. Core and ORM
        users should familiarize with concepts in these sections equally.


教程概述
---------------

Tutorial Overview

.. tab:: 中文

    本教程将按照应学习的自然顺序介绍这两个概念，首先是以核心为主的方法，然后扩展到更多以 ORM 为中心的概念。

    本教程的主要部分如下：

    .. toctree::
        :hidden:
        :maxdepth: 10

        engine
        dbapi_transactions
        metadata
        data
        orm_data_manipulation
        orm_related_objects
        further_reading

    * :ref:`tutorial_engine` - 所有 SQLAlchemy 应用程序都从一个 :class:`_engine.Engine` 对象开始；这里介绍如何创建它。

    * :ref:`tutorial_working_with_transactions` - 介绍 :class:`_engine.Engine` 及其相关对象 :class:`_engine.Connection` 和 :class:`_result.Result` 的使用 API。 这些内容以核心为主，但 ORM 用户至少要熟悉 :class:`_result.Result` 对象。

    * :ref:`tutorial_working_with_metadata` - SQLAlchemy 的 SQL 抽象以及 ORM 依赖于将数据库模式结构定义为 Python 对象的系统。本节介绍如何从核心和 ORM 的角度进行操作。

    * :ref:`tutorial_working_with_data` - 在这里，我们学习如何在数据库中创建、选择、更新和删除数据。 这里的所谓 :term:`CRUD` 操作是以 SQLAlchemy Core 的形式给出的，并链接到它们的 ORM 对应部分。 在 :ref:`tutorial_selecting_data` 中详细介绍的 SELECT 操作同样适用于 Core 和 ORM。

    * :ref:`tutorial_orm_data_manipulation` 介绍了 ORM 的持久化框架；基本上是插入、更新和删除的 ORM 方法，以及如何处理事务。

    * :ref:`tutorial_orm_related_objects` 介绍了 :func:`_orm.relationship` 构造的概念，并简要概述了如何使用它，提供了更深入文档的链接。

    * :ref:`tutorial_further_reading` 列出了几个主要的顶级文档部分，这些部分全面记录了本教程中介绍的概念。

.. tab:: 英文

    The tutorial will present both concepts in the natural order that they should be learned, first with a mostly-Core-centric approach and then spanning out into more ORM-centric concepts.

    The major sections of this tutorial are as follows:

    * :ref:`tutorial_engine` - all SQLAlchemy applications start with an :class:`_engine.Engine` object; here's how to create one.

    * :ref:`tutorial_working_with_transactions` - the usage API of the :class:`_engine.Engine` and its related objects :class:`_engine.Connection` and :class:`_result.Result` are presented here. This content is Core-centric however ORM users will want to be familiar with at least the :class:`_result.Result` object.

    * :ref:`tutorial_working_with_metadata` - SQLAlchemy's SQL abstractions as well as the ORM rely upon a system of defining database schema constructs as Python objects.   This section introduces how to do that from both a Core and an ORM perspective.

    * :ref:`tutorial_working_with_data` - here we learn how to create, select, update and delete data in the database.   The so-called :term:`CRUD` operations here are given in terms of SQLAlchemy Core with links out towards their ORM counterparts.  The SELECT operation that is introduced in detail at :ref:`tutorial_selecting_data` applies equally well to Core and ORM.

    * :ref:`tutorial_orm_data_manipulation` covers the persistence framework of the ORM; basically the ORM-centric ways to insert, update and delete, as well as how to handle transactions.

    * :ref:`tutorial_orm_related_objects` introduces the concept of the :func:`_orm.relationship` construct and provides a brief overview of how it's used, with links to deeper documentation.

    * :ref:`tutorial_further_reading` lists a series of major top-level documentation sections which fully document the concepts introduced in this tutorial.


.. rst-class:: core-header, orm-dependency

版本检查
-------------

Version Check

.. tab:: 中文

    本教程使用名为 `doctest <https://docs.python.org/3/library/doctest.html>`_ 的系统编写。所有用 ``>>>`` 编写的代码片段实际上都是作为 SQLAlchemy 测试套件的一部分运行的，读者可以在自己的 Python 解释器中实时使用给出的代码示例。

    如果运行示例，建议读者进行快速检查，以验证我们使用的是 **SQLAlchemy 2.1 版**：

    .. sourcecode:: pycon+sql

        >>> import sqlalchemy
        >>> sqlalchemy.__version__  # doctest: +SKIP
        2.1.0

.. tab:: 英文

    This tutorial is written using a system called `doctest
    <https://docs.python.org/3/library/doctest.html>`_. All of the code excerpts
    written with a ``>>>`` are actually run as part of SQLAlchemy's test suite, and
    the reader is invited to work with the code examples given in real time with
    their own Python interpreter.

    If running the examples, it is advised that the reader performs a quick check to
    verify that we are on  **version 2.1** of SQLAlchemy:

    .. sourcecode:: pycon+sql

        >>> import sqlalchemy
        >>> sqlalchemy.__version__  # doctest: +SKIP
        2.1.0





