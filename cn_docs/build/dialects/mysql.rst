.. _mysql_toplevel:

MySQL 和 MariaDB
=================

MySQL and MariaDB

.. automodule:: sqlalchemy.dialects.mysql.base

MySQL SQL 构造
--------------------

MySQL SQL Constructs

.. currentmodule:: sqlalchemy.dialects.mysql

.. autoclass:: match
    :members:

MySQL 数据类型
----------------

MySQL Data Types

.. tab:: 中文

    与所有SQLAlchemy方言一样，所有已知对MySQL有效的UPPERCASE类型都可以从顶级方言中导入::

        from sqlalchemy.dialects.mysql import (
            BIGINT,
            BINARY,
            BIT,
            BLOB,
            BOOLEAN,
            CHAR,
            DATE,
            DATETIME,
            DECIMAL,
            DECIMAL,
            DOUBLE,
            ENUM,
            FLOAT,
            INTEGER,
            LONGBLOB,
            LONGTEXT,
            MEDIUMBLOB,
            MEDIUMINT,
            MEDIUMTEXT,
            NCHAR,
            NUMERIC,
            NVARCHAR,
            REAL,
            SET,
            SMALLINT,
            TEXT,
            TIME,
            TIMESTAMP,
            TINYBLOB,
            TINYINT,
            TINYTEXT,
            VARBINARY,
            VARCHAR,
            YEAR,
        )

    除了上述类型，MariaDB还支持以下类型::

        from sqlalchemy.dialects.mysql import (
            INET4,
            INET6,
        )

    特定于MySQL或MariaDB，或具有特定构造参数的类型如下：

.. tab:: 英文

    As with all SQLAlchemy dialects, all UPPERCASE types that are known to be
    valid with MySQL are importable from the top level dialect::

        from sqlalchemy.dialects.mysql import (
            BIGINT,
            BINARY,
            BIT,
            BLOB,
            BOOLEAN,
            CHAR,
            DATE,
            DATETIME,
            DECIMAL,
            DECIMAL,
            DOUBLE,
            ENUM,
            FLOAT,
            INTEGER,
            LONGBLOB,
            LONGTEXT,
            MEDIUMBLOB,
            MEDIUMINT,
            MEDIUMTEXT,
            NCHAR,
            NUMERIC,
            NVARCHAR,
            REAL,
            SET,
            SMALLINT,
            TEXT,
            TIME,
            TIMESTAMP,
            TINYBLOB,
            TINYINT,
            TINYTEXT,
            VARBINARY,
            VARCHAR,
            YEAR,
        )

    In addition to the above types, MariaDB also supports the following::

        from sqlalchemy.dialects.mysql import (
            INET4,
            INET6,
        )

    Types which are specific to MySQL or MariaDB, or have specific
    construction arguments, are as follows:

.. note: where :noindex: is used, indicates a type that is not redefined
in the dialect module, just imported from sqltypes.  this avoids warnings
in the sphinx build

.. currentmodule:: sqlalchemy.dialects.mysql

.. autoclass:: BIGINT
    :members: __init__


.. autoclass:: BINARY
    :noindex:
    :members: __init__


.. autoclass:: BIT
    :members: __init__


.. autoclass:: BLOB
    :members: __init__
    :noindex:


.. autoclass:: BOOLEAN
    :members: __init__
    :noindex:


.. autoclass:: CHAR
    :members: __init__


.. autoclass:: DATE
    :members: __init__
    :noindex:


.. autoclass:: DATETIME
    :members: __init__


.. autoclass:: DECIMAL
    :members: __init__


.. autoclass:: DOUBLE
    :members: __init__
    :noindex:

.. autoclass:: ENUM
    :members: __init__


.. autoclass:: FLOAT
    :members: __init__


.. autoclass:: INET4

.. autoclass:: INET6

.. autoclass:: INTEGER
    :members: __init__

.. autoclass:: JSON
    :members:

.. autoclass:: LONGBLOB
    :members: __init__


.. autoclass:: LONGTEXT
    :members: __init__


.. autoclass:: MEDIUMBLOB
    :members: __init__


.. autoclass:: MEDIUMINT
    :members: __init__


.. autoclass:: MEDIUMTEXT
    :members: __init__


.. autoclass:: NCHAR
    :members: __init__


.. autoclass:: NUMERIC
    :members: __init__


.. autoclass:: NVARCHAR
    :members: __init__


.. autoclass:: REAL
    :members: __init__


.. autoclass:: SET
    :members: __init__


.. autoclass:: SMALLINT
    :members: __init__


.. autoclass:: TEXT
    :members: __init__
    :noindex:


.. autoclass:: TIME
    :members: __init__


.. autoclass:: TIMESTAMP
    :members: __init__


.. autoclass:: TINYBLOB
    :members: __init__


.. autoclass:: TINYINT
    :members: __init__


.. autoclass:: TINYTEXT
    :members: __init__


.. autoclass:: VARBINARY
    :members: __init__
    :noindex:


.. autoclass:: VARCHAR
    :members: __init__


.. autoclass:: YEAR
    :members: __init__

MySQL DML 构造
-------------------------

MySQL DML Constructs

.. autofunction:: sqlalchemy.dialects.mysql.insert

.. autoclass:: sqlalchemy.dialects.mysql.Insert
  :members:

.. autofunction:: sqlalchemy.dialects.mysql.limit



mysqlclient（MySQL-Python 的分支）
----------------------------------

mysqlclient (fork of MySQL-Python)

.. automodule:: sqlalchemy.dialects.mysql.mysqldb

PyMySQL
-------

.. automodule:: sqlalchemy.dialects.mysql.pymysql

MariaDB-Connector
------------------

.. automodule:: sqlalchemy.dialects.mysql.mariadbconnector

MySQL-Connector
---------------

.. automodule:: sqlalchemy.dialects.mysql.mysqlconnector

.. _asyncmy:

asyncmy
-------

.. automodule:: sqlalchemy.dialects.mysql.asyncmy


.. _aiomysql:

aiomysql
--------

.. automodule:: sqlalchemy.dialects.mysql.aiomysql

cymysql
-------

.. automodule:: sqlalchemy.dialects.mysql.cymysql

pyodbc
------

.. automodule:: sqlalchemy.dialects.mysql.pyodbc
