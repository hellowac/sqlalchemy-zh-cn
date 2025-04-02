.. highlight:: pycon+sql

.. |prev| replace:: :doc:`metadata`
.. |next| replace:: :doc:`data_insert`

.. include:: tutorial_nav_include.rst

.. rst-class:: core-header, orm-addin

.. _tutorial_working_with_data:

处理数据
==================

Working with Data

.. tab:: 中文

    在 :ref:`tutorial_working_with_transactions` 中，我们学习了如何与 Python DBAPI 及其事务状态进行交互的基础知识。然后，在 :ref:`tutorial_working_with_metadata` 中，我们学习了如何使用 :class:`_schema.MetaData` 和相关对象在 SQLAlchemy 中表示数据库表、列和约束。在本节中，我们将结合上述两个概念，在关系数据库中创建、选择和操作数据。我们与数据库的交互 **总是** 以事务的形式进行，即使我们将数据库驱动程序设置为在幕后使用 :ref:`自动提交 <dbapi_autocommit>`。

    本节的组成部分如下：

    * :ref:`tutorial_core_insert` - 为了将一些数据插入数据库，我们介绍并演示了 Core 的 :class:`_sql.Insert` 构造。ORM 视角的 INSERT 在下一节 :ref:`tutorial_orm_data_manipulation` 中描述。

    * :ref:`tutorial_selecting_data` - 本节将详细描述 :class:`_sql.Select` 构造，这是 SQLAlchemy 中最常用的对象。:class:`_sql.Select` 构造为 Core 和 ORM 中心应用程序发出 SELECT 语句，这两种用例将在此处描述。其他 ORM 用例也在后面的章节 :ref:`tutorial_select_relationships` 以及 :ref:`queryguide_toplevel` 中提到。

    * :ref:`tutorial_core_update_delete` - 完成数据的 INSERT 和 SELECT，本节将从 Core 视角描述 :class:`_sql.Update` 和 :class:`_sql.Delete` 构造的使用。特定于 ORM 的 UPDATE 和 DELETE 同样在 :ref:`tutorial_orm_data_manipulation` 部分中描述。

.. tab:: 英文

    In :ref:`tutorial_working_with_transactions`, we learned the basics of how to interact with the Python DBAPI and its transactional state.  Then, in :ref:`tutorial_working_with_metadata`, we learned how to represent database tables, columns, and constraints within SQLAlchemy using the :class:`_schema.MetaData` and related objects.  In this section we will combine both concepts above to create, select and manipulate data within a relational database.   Our interaction with the database is **always** in terms of a transaction, even if we've set our database driver to use :ref:`autocommit <dbapi_autocommit>` behind the scenes.

    The components of this section are as follows:

    * :ref:`tutorial_core_insert` - to get some data into the database, we introduce and demonstrate the Core :class:`_sql.Insert` construct.   INSERTs from an ORM perspective are described in the next section :ref:`tutorial_orm_data_manipulation`.

    * :ref:`tutorial_selecting_data` - this section will describe in detail the :class:`_sql.Select` construct, which is the most commonly used object in SQLAlchemy.  The :class:`_sql.Select` construct emits SELECT statements for both Core and ORM centric applications and both use cases will be described here.   Additional ORM use cases are also noted in the later section :ref:`tutorial_select_relationships` as well as the :ref:`queryguide_toplevel`.

    * :ref:`tutorial_core_update_delete` - Rounding out the INSERT and SELECTion of data, this section will describe from a Core perspective the use of the :class:`_sql.Update` and :class:`_sql.Delete` constructs.  ORM-specific UPDATE and DELETE is similarly described in the :ref:`tutorial_orm_data_manipulation` section.


.. toctree::
    :hidden:
    :maxdepth: 10

    data_insert
    data_select
    data_update
