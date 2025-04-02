.. _dialect_toplevel:

Dialects
========

.. tab:: 中文

    **dialect** 是 SQLAlchemy 用于与各种类型的 :term:`DBAPI` 实现和数据库通信的系统。
    接下来的部分包含每个后端使用的参考文档和特定说明，以及各种 DBAPI 的说明。

    所有 dialect 都需要安装适当的 DBAPI 驱动程序。

.. tab:: 英文

    The **dialect** is the system SQLAlchemy uses to communicate with various types of :term:`DBAPI` implementations and databases.
    The sections that follow contain reference documentation and notes specific to the usage of each backend, as well as notes
    for the various DBAPIs.

    All dialects require that an appropriate DBAPI driver is installed.

.. _included_dialects:

已包含的 dialect
-----------------

Included Dialects

.. toctree::
    :maxdepth: 1
    :glob:

    postgresql
    mysql
    sqlite
    oracle
    mssql

已包含的 dialect 支持的版本
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Supported versions for Included Dialects

.. tab:: 中文

    下表总结了每种方言的支持级别。

.. tab:: 英文

    The following table summarizes the support level for each included dialect.

.. dialect-table:: **Supported database versions for included dialects**
  :header-rows: 1

支持定义
^^^^^^^^^^^^^^^^^^^

Support Definitions

.. tab:: 中文

    .. glossary::

        Supported version
            **支持的版本(Supported version)** 表示大多数 SQLAlchemy 功能应适用于所提及的数据库版本。由于并非所有数据库版本都可在 ci 中测试，因此可能存在一些无法正常工作的极端情况。

        Best effort
            **尽力而为(Best effort)** 表示 SQLAlchemy 会尽力支持这些版本的基本功能，但很可能会出现不支持的功能或某些用例中的错误。可能会接受带有相关问题的拉取请求以继续支持旧版本，这些请求将根据具体情况进行审核。

.. tab:: 英文

    .. Fully tested in CI
    ..     **Fully tested in CI** indicates a version that is tested in the sqlalchemy
    ..     CI system and passes all the tests in the test suite.

    .. glossary::
        :no-index:

        Supported version
            **Supported version** indicates that most SQLAlchemy features should work
            for the mentioned database version. Since not all database versions may be
            tested in the ci there may be some not working edge cases.

        Best effort
            **Best effort** indicates that SQLAlchemy tries to support basic features on these
            versions, but most likely there will be unsupported features or errors in some use cases.
            Pull requests with associated issues may be accepted to continue supporting
            older versions, which are reviewed on a case-by-case basis.

.. _external_toplevel:

External Dialects
-----------------

.. tab:: 中文

    目前维护的 SQLAlchemy 外部方言项目包括：

.. tab:: 英文

    Currently maintained external dialect projects for SQLAlchemy include:

+------------------------------------------------+---------------------------------------+
| Database                                       | Dialect                               |
+================================================+=======================================+
| Actian Data Platform, Vector, Actian X, Ingres | sqlalchemy-ingres_                    |
+------------------------------------------------+---------------------------------------+
| Amazon Athena                                  | pyathena_                             |
+------------------------------------------------+---------------------------------------+
| Amazon Redshift (via psycopg2)                 | sqlalchemy-redshift_                  |
+------------------------------------------------+---------------------------------------+
| Apache Drill                                   | sqlalchemy-drill_                     |
+------------------------------------------------+---------------------------------------+
| Apache Druid                                   | pydruid_                              |
+------------------------------------------------+---------------------------------------+
| Apache Hive and Presto                         | PyHive_                               |
+------------------------------------------------+---------------------------------------+
| Apache Solr                                    | sqlalchemy-solr_                      |
+------------------------------------------------+---------------------------------------+
| Clickhouse                                     | clickhouse-sqlalchemy_                |
+------------------------------------------------+---------------------------------------+
| CockroachDB                                    | sqlalchemy-cockroachdb_               |
+------------------------------------------------+---------------------------------------+
| CrateDB                                        | sqlalchemy-cratedb_                   |
+------------------------------------------------+---------------------------------------+
| Databend                                       | databend-sqlalchemy_                  |
+------------------------------------------------+---------------------------------------+
| Databricks                                     | databricks_                           |
+------------------------------------------------+---------------------------------------+
| EXASolution                                    | sqlalchemy_exasol_                    |
+------------------------------------------------+---------------------------------------+
| Elasticsearch (readonly)                       | elasticsearch-dbapi_                  |
+------------------------------------------------+---------------------------------------+
| Firebird                                       | sqlalchemy-firebird_                  |
+------------------------------------------------+---------------------------------------+
| Firebolt                                       | firebolt-sqlalchemy_                  |
+------------------------------------------------+---------------------------------------+
| Google BigQuery                                | sqlalchemy-bigquery_                  |
+------------------------------------------------+---------------------------------------+
| Google Sheets                                  | gsheets_                              |
+------------------------------------------------+---------------------------------------+
| Greenplum                                      | sqlalchemy-greenplum_                 |
+------------------------------------------------+---------------------------------------+
| HyperSQL (hsqldb)                              | sqlalchemy-hsqldb_                    |
+------------------------------------------------+---------------------------------------+
| IBM DB2 and Informix                           | ibm-db-sa_                            |
+------------------------------------------------+---------------------------------------+
| IBM Netezza Performance Server [1]_            | nzalchemy_                            |
+------------------------------------------------+---------------------------------------+
| Impala                                         | impyla_                               |
+------------------------------------------------+---------------------------------------+
| Kinetica                                       | sqlalchemy-kinetica_                  |
+------------------------------------------------+---------------------------------------+
| Microsoft Access (via pyodbc)                  | sqlalchemy-access_                    |
+------------------------------------------------+---------------------------------------+
| Microsoft SQL Server (via python-tds)          | sqlalchemy-pytds_                     |
+------------------------------------------------+---------------------------------------+
| Microsoft SQL Server (via turbodbc)            | sqlalchemy-turbodbc_                  |
+------------------------------------------------+---------------------------------------+
| MonetDB                                        | sqlalchemy-monetdb_                   |
+------------------------------------------------+---------------------------------------+
| OpenGauss                                      | openGauss-sqlalchemy_                 |
+------------------------------------------------+---------------------------------------+
| Rockset                                        | rockset-sqlalchemy_                   |
+------------------------------------------------+---------------------------------------+
| SAP ASE (fork of former Sybase dialect)        | sqlalchemy-sybase_                    |
+------------------------------------------------+---------------------------------------+
| SAP Hana [1]_                                  | sqlalchemy-hana_                      |
+------------------------------------------------+---------------------------------------+
| SAP Sybase SQL Anywhere                        | sqlalchemy-sqlany_                    |
+------------------------------------------------+---------------------------------------+
| Snowflake                                      | snowflake-sqlalchemy_                 |
+------------------------------------------------+---------------------------------------+
| Teradata Vantage                               | teradatasqlalchemy_                   |
+------------------------------------------------+---------------------------------------+
| TiDB                                           | sqlalchemy-tidb_                      |
+------------------------------------------------+---------------------------------------+
| YDB                                            | ydb-sqlalchemy_                       |
+------------------------------------------------+---------------------------------------+
| YugabyteDB                                     | sqlalchemy-yugabytedb_                |
+------------------------------------------------+---------------------------------------+

.. [1] Supports version 1.3.x only at the moment.

.. _openGauss-sqlalchemy: https://gitee.com/opengauss/openGauss-sqlalchemy
.. _rockset-sqlalchemy: https://pypi.org/project/rockset-sqlalchemy
.. _sqlalchemy-ingres: https://github.com/ActianCorp/sqlalchemy-ingres
.. _nzalchemy: https://pypi.org/project/nzalchemy/
.. _ibm-db-sa: https://pypi.org/project/ibm-db-sa/
.. _PyHive: https://github.com/dropbox/PyHive#sqlalchemy
.. _teradatasqlalchemy: https://pypi.org/project/teradatasqlalchemy/
.. _sqlalchemy-bigquery: https://pypi.org/project/sqlalchemy-bigquery/
.. _sqlalchemy-redshift: https://pypi.org/project/sqlalchemy-redshift
.. _sqlalchemy-drill: https://github.com/JohnOmernik/sqlalchemy-drill
.. _sqlalchemy-hana: https://github.com/SAP/sqlalchemy-hana
.. _sqlalchemy-solr: https://github.com/aadel/sqlalchemy-solr
.. _sqlalchemy_exasol: https://github.com/blue-yonder/sqlalchemy_exasol
.. _sqlalchemy-sqlany: https://github.com/sqlanywhere/sqlalchemy-sqlany
.. _sqlalchemy-monetdb: https://github.com/MonetDB/sqlalchemy-monetdb
.. _snowflake-sqlalchemy: https://github.com/snowflakedb/snowflake-sqlalchemy
.. _sqlalchemy-pytds: https://pypi.org/project/sqlalchemy-pytds/
.. _sqlalchemy-cratedb: https://github.com/crate/sqlalchemy-cratedb
.. _sqlalchemy-access: https://pypi.org/project/sqlalchemy-access/
.. _elasticsearch-dbapi: https://github.com/preset-io/elasticsearch-dbapi/
.. _pydruid: https://github.com/druid-io/pydruid
.. _gsheets: https://github.com/betodealmeida/gsheets-db-api
.. _sqlalchemy-firebird: https://github.com/pauldex/sqlalchemy-firebird
.. _sqlalchemy-cockroachdb: https://github.com/cockroachdb/sqlalchemy-cockroachdb
.. _sqlalchemy-turbodbc: https://pypi.org/project/sqlalchemy-turbodbc/
.. _sqlalchemy-sybase: https://pypi.org/project/sqlalchemy-sybase/
.. _firebolt-sqlalchemy: https://pypi.org/project/firebolt-sqlalchemy/
.. _pyathena: https://github.com/laughingman7743/PyAthena/
.. _sqlalchemy-yugabytedb: https://pypi.org/project/sqlalchemy-yugabytedb/
.. _impyla: https://pypi.org/project/impyla/
.. _databend-sqlalchemy: https://github.com/datafuselabs/databend-sqlalchemy
.. _sqlalchemy-greenplum: https://github.com/PlaidCloud/sqlalchemy-greenplum
.. _sqlalchemy-hsqldb: https://pypi.org/project/sqlalchemy-hsqldb/
.. _databricks: https://docs.databricks.com/en/dev-tools/sqlalchemy.html
.. _clickhouse-sqlalchemy: https://pypi.org/project/clickhouse-sqlalchemy/
.. _sqlalchemy-kinetica: https://github.com/kineticadb/sqlalchemy-kinetica/
.. _sqlalchemy-tidb: https://github.com/pingcap/sqlalchemy-tidb
.. _ydb-sqlalchemy: https://github.com/ydb-platform/ydb-sqlalchemy/
