:orphan:

.. _index_toplevel:

========================
SQLAlchemy 文档
========================

SQLAlchemy Documentation

入门
---------------------

Getting Started

.. tab:: 中文

    第一次使用 SQLAlchemy?   从这开始:

    * **对于 Python 初学者:** :ref:`安装指南 <installation>` - 使用 pip 和类似工具进行安装的基本指导

    * **对于 Python 老手来说:** :doc:`SQLAlchemy Overview <intro>` - SQLAlchemy 的简要架构概述

.. tab:: 英文

    New to SQLAlchemy?   Start here:

    * **For Python Beginners:** :ref:`Installation Guide <installation>` - Basic
      guidance on installing with pip and similar tools

    * **For Python Veterans:** :doc:`SQLAlchemy Overview <intro>` - A brief
      architectural overview of SQLAlchemy

教程
----------------

Tutorials

.. tab:: 中文

    SQLAlchemy 的新用户以及旧 SQLAlchemy 发行版系列的老用户都应该从 :doc:`/tutorial/index` 开始，它涵盖了 Alchemist 使用 ORM 或 Core 时需要了解的所有内容。

    * **快速浏览：** :doc:`/orm/quickstart` - 使用 ORM 的简要概述

    * **适用于所有用户：** :doc:`/tutorial/index` - Core 和 ORM 使用的深入教程

.. tab:: 英文

    New users of SQLAlchemy, as well as veterans of older SQLAlchemy
    release series, should start with the
    :doc:`/tutorial/index`, which covers everything an Alchemist needs
    to know when using the ORM or just Core.

    * **For a quick glance:** :doc:`/orm/quickstart` - A brief overview of
      what working with the ORM looks like

    * **For all users:** :doc:`/tutorial/index` - In-depth tutorial for
      both Core and ORM usage

迁移说明
--------------------

Migration Notes

.. tab:: 中文

    升级到 SQLAlchemy 2.0 版的用户需要阅读：

    * :doc:`SQLAlchemy 2.1 中有哪些新功能？<changelog/migration_21>` - 2.1 版中的新功能和行为

    从 SQLAlchemy 1.x 版（例如 1.4 版）过渡的用户应先过渡到 2.0 版，然后再进行从 2.0 到 2.1 的较小过渡所需的任何其他更改。1.x 到 2.x 过渡的关键文档：

    * :doc:`迁移到 SQLAlchemy 2.0 <changelog/migration_20>` - 从 1.3 或 1.4 迁移到 2.0 的完整背景
    * :doc:`SQLAlchemy 2.0 中有哪些新功能？ <changelog/whatsnew_20>` - 2.0 版中引入的新功能和行为，超越了 1.x 迁移

    所有变更日志和迁移文档的索引位于：

    * :doc:`变更日志目录 <changelog/index>` - 所有 SQLAlchemy 版本的详细变更日志

.. tab:: 英文

    Users upgrading to SQLAlchemy version 2.0 will want to read:

    * :doc:`What's New in SQLAlchemy 2.1? <changelog/migration_21>` - New
      features and behaviors in version 2.1

    Users transitioning from version 1.x of SQLAlchemy (e.g., version 1.4)
    should first transition to version 2.0 before making any additional
    changes needed for the smaller transition from 2.0 to 2.1.
    Key documentation for the 1.x to 2.x transition:

    * :doc:`Migrating to SQLAlchemy 2.0 <changelog/migration_20>` - Complete
      background on migrating from 1.3 or 1.4 to 2.0
    * :doc:`What's New in SQLAlchemy 2.0? <changelog/whatsnew_20>` - New
      features and behaviors introduced in version 2.0 beyond the 1.x
      migration

    An index of all changelogs and migration documentation is available at:

    * :doc:`Changelog catalog <changelog/index>` - Detailed
      changelogs for all SQLAlchemy Versions


参考和操作方法
-------------------------

Reference and How To

ORM
~~~~~~~~

.. tab:: 中文

    **SQLAlchemy ORM** - 使用 ORM 的详细指南和 API 参考

    * **映射类：**
    
      - :doc:`映射 Python 类 <orm/mapper_config>` 
      - :doc:`关系配置 <orm/relationships>`

    * **使用 ORM：**
    
      - :doc:`使用 ORM 会话 <orm/session>` 
      - :doc:`ORM 查询指南 <orm/queryguide/index>` 
      - :doc:`使用 AsyncIO <orm/extensions/asyncio>`

    * **配置扩展：**
    
      - :doc:`关联代理 <orm/extensions/associationproxy>` 
      - :doc:`混合属性 <orm/extensions/hybrid>` 
      - :doc:`可变标量 <orm/extensions/mutable>` 
      - :doc:`自动映射 <orm/extensions/automap>` 
      - :doc:`所有扩展 <orm/extensions/index>`

    * **扩展 ORM：**
    
      - :doc:`ORM 事件和内部 <orm/extending>`

    * **其他：**
    
      - :doc:`示例简介 <orm/examples>`

.. tab:: 英文

    **SQLAlchemy ORM** - Detailed guides and API reference for using the ORM

    * **Mapping Classes:**
    
      - :doc:`Mapping Python Classes <orm/mapper_config>` 
      - :doc:`Relationship Configuration <orm/relationships>`

    * **Using the ORM:**
    
      - :doc:`Using the ORM Session <orm/session>` 
      - :doc:`ORM Querying Guide <orm/queryguide/index>` 
      - :doc:`Using AsyncIO <orm/extensions/asyncio>`

    * **Configuration Extensions:**
    
      - :doc:`Association Proxy <orm/extensions/associationproxy>` 
      - :doc:`Hybrid Attributes <orm/extensions/hybrid>` 
      - :doc:`Mutable Scalars <orm/extensions/mutable>` 
      - :doc:`Automap <orm/extensions/automap>` 
      - :doc:`All extensions <orm/extensions/index>`

    * **Extending the ORM:**
    
      :doc:`ORM Events and Internals <orm/extending>`

    * **Other:**
    
      :doc:`Introduction to Examples <orm/examples>`

核心
~~~~~~~~

CORE

.. tab:: 中文

    **SQLAlchemy Core** - 使用 Core 的详细指南和 API 参考

    * **引擎、连接、池：**
    
      - :doc:`引擎配置 <core/engines>` 
      - :doc:`连接、事务、结果 <core/connections>` 
      - :doc:`AsyncIO 支持 <orm/extensions/asyncio>` 
      - :doc:`连接池 <core/pooling>`

    * **模式定义：**
    
      - :doc:`概述 <core/schema>` 
      - :ref:`表和列 <metadata_describing_toplevel>` 
      - :ref:`数据库自省（反射）<metadata_reflection_toplevel>` 
      - :ref:`插入/更新默认值 <metadata_defaults_toplevel>` 
      - :ref:`约束和索引 <metadata_constraints_toplevel>` 
      - :ref:`使用数据定义语言 (DDL) <metadata_ddl_toplevel>`

    * **SQL 语句：**
    
      - :doc:`SQL 表达式元素 <core/sqlelement>` 
      - :doc:`运算符参考 <core/operators>` 
      - :doc:`SELECT 和相关构造 <core/selectable>` 
      - :doc:`INSERT、UPDATE、DELETE <core/dml>` 
      - :doc:`SQL 函数 <core/functions>` 
      - :doc:`目录 <core/expression_api>`

    * **数据类型：**
    
      - :ref:`概述 <types_toplevel>` 
      - :ref:`构建自定义类型 <types_custom>` 
      - :ref:`类型 API 参考 <types_api>`

    * **核心基础知识：**
    
      - :doc:`概述 <core/api_basics>` 
      - :doc:`运行时检查 API <core/inspection>` 
      - :doc:`事件系统 <core/event>` 
      - :doc:`核心事件接口 <core/events>` 
      - :doc:`创建自定义 SQL 构造 <core/compiler>`

.. tab:: 英文

    **SQLAlchemy Core** - Detailed guides and API reference for working with Core

    * **Engines, Connections, Pools:**
    
      - :doc:`Engine Configuration <core/engines>` 
      - :doc:`Connections, Transactions, Results <core/connections>` 
      - :doc:`AsyncIO Support <orm/extensions/asyncio>` 
      - :doc:`Connection Pooling <core/pooling>`

    * **Schema Definition:**
    
      - :doc:`Overview <core/schema>` 
      - :ref:`Tables and Columns <metadata_describing_toplevel>` 
      - :ref:`Database Introspection (Reflection) <metadata_reflection_toplevel>` 
      - :ref:`Insert/Update Defaults <metadata_defaults_toplevel>` 
      - :ref:`Constraints and Indexes <metadata_constraints_toplevel>` 
      - :ref:`Using Data Definition Language (DDL) <metadata_ddl_toplevel>`

    * **SQL Statements:**
    
      - :doc:`SQL Expression Elements <core/sqlelement>` 
      - :doc:`Operator Reference <core/operators>` 
      - :doc:`SELECT and related constructs <core/selectable>` 
      - :doc:`INSERT, UPDATE, DELETE <core/dml>` 
      - :doc:`SQL Functions <core/functions>` 
      - :doc:`Table of Contents <core/expression_api>`

    * **Datatypes:**
    
      - :ref:`Overview <types_toplevel>` 
      - :ref:`Building Custom Types <types_custom>` 
      - :ref:`Type API Reference <types_api>`

    * **Core Basics:**
    
      - :doc:`Overview <core/api_basics>` 
      - :doc:`Runtime Inspection API <core/inspection>` 
      - :doc:`Event System <core/event>` 
      - :doc:`Core Event Interfaces <core/events>` 
      - :doc:`Creating Custom SQL Constructs <core/compiler>`

方言文档
--------------------------

Dialect Documentation

.. tab:: 中文

    **方言** 是 SQLAlchemy 用于与各种类型的 DBAPI 和数据库进行通信的系统。
    本节介绍有关各个方言的说明、选项和使用模式。

    - :doc:`PostgreSQL <dialects/postgresql>` 
    - :doc:`MySQL 和 MariaDB <dialects/mysql>` 
    - :doc:`SQLite <dialects/sqlite>` 
    - :doc:`Oracle 数据库 <dialects/oracle>` 
    - :doc:`Microsoft SQL Server <dialects/mssql>`
    - :doc:`更多方言... <dialects/index>`

.. tab:: 英文

    The **dialect** is the system SQLAlchemy uses to communicate with
    various types of DBAPIs and databases.
    This section describes notes, options, and usage patterns regarding
    individual dialects.

    - :doc:`PostgreSQL <dialects/postgresql>` 
    - :doc:`MySQL and MariaDB <dialects/mysql>` 
    - :doc:`SQLite <dialects/sqlite>` 
    - :doc:`Oracle Database <dialects/oracle>` 
    - :doc:`Microsoft SQL Server <dialects/mssql>`
    - :doc:`More Dialects ... <dialects/index>`

补充
-----------------

Supplementary

.. tab:: 中文

    * :doc:`常见问题 <faq/index>` - 常见问题和解决方案的集合
    * :doc:`词汇表 <glossary>` - SQLAlchemy 文档中使用的术语定义
    * :doc:`错误消息指南 <errors>` - 许多 SQLAlchemy 错误的解释
    * :doc:`完整目录 <contents>` - 可用文档的完整列表
    * :ref:`索引 <genindex>` - 方便查找文档主题的索引

.. tab:: 英文

    * :doc:`Frequently Asked Questions <faq/index>` - A collection of common problems and solutions
    * :doc:`Glossary <glossary>` - Definitions of terms used in SQLAlchemy documentation
    * :doc:`Error Message Guide <errors>` - Explanations of many SQLAlchemy errors
    * :doc:`Complete table of of contents <contents>` - Full list of available documentation
    * :ref:`Index <genindex>` - Index for easy lookup of documentation topics
  

.. _contents:

目录
----------------------

Table of Contents

.. tab:: 中文

    完整目录。有关所有文档的高级概述，请参阅 :ref:`index_toplevel` 。

.. tab:: 英文

    Full table of contents.  For a high level overview of all
    documentation, see :ref:`index_toplevel`.

.. toctree::
   :titlesonly:
   :includehidden:

   intro
   tutorial/index
   orm/index
   core/index
   dialects/index
   faq/index
   errors
   changelog/index

索引表
------------------

Indices and tables

.. tab:: 中文

.. tab:: 英文

* :ref:`glossary`
* :ref:`genindex`