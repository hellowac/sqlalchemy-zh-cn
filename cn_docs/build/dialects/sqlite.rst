.. _sqlite_toplevel:

SQLite
======

.. automodule:: sqlalchemy.dialects.sqlite.base

SQLite 数据类型
-----------------

SQLite Data Types

.. tab:: 中文

  与所有SQLAlchemy方言一样，所有已知对SQLite有效的UPPERCASE类型都可以从顶级方言中导入，无论它们是来自 :mod:`sqlalchemy.types` 还是来自本地方言::

      from sqlalchemy.dialects.sqlite import (
          BLOB,
          BOOLEAN,
          CHAR,
          DATE,
          DATETIME,
          DECIMAL,
          FLOAT,
          INTEGER,
          NUMERIC,
          JSON,
          SMALLINT,
          TEXT,
          TIME,
          TIMESTAMP,
          VARCHAR,
      )

.. tab:: 英文

    As with all SQLAlchemy dialects, all UPPERCASE types that are known to be
    valid with SQLite are importable from the top level dialect, whether
    they originate from :mod:`sqlalchemy.types` or from the local dialect::

        from sqlalchemy.dialects.sqlite import (
            BLOB,
            BOOLEAN,
            CHAR,
            DATE,
            DATETIME,
            DECIMAL,
            FLOAT,
            INTEGER,
            NUMERIC,
            JSON,
            SMALLINT,
            TEXT,
            TIME,
            TIMESTAMP,
            VARCHAR,
        )

.. module:: sqlalchemy.dialects.sqlite

.. autoclass:: DATETIME

.. autoclass:: DATE

.. autoclass:: JSON

.. autoclass:: TIME

SQLite DML 构造
-------------------------

SQLite DML Constructs

.. autofunction:: sqlalchemy.dialects.sqlite.insert

.. autoclass:: sqlalchemy.dialects.sqlite.Insert
  :members:

.. _pysqlite:

Pysqlite
--------

.. automodule:: sqlalchemy.dialects.sqlite.pysqlite

.. _aiosqlite:

Aiosqlite
---------

.. automodule:: sqlalchemy.dialects.sqlite.aiosqlite


.. _pysqlcipher:

Pysqlcipher
-----------

.. automodule:: sqlalchemy.dialects.sqlite.pysqlcipher
