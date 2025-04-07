"""
.. tab:: 中文

    演示了将多种类型的父对象与特定子对象关联的多种方法。

    这些示例全部使用了声明式扩展（declarative extension）和
    声明式混入类（declarative mixins）。每个示例最终展示的用例都是相同的：
    两个类 ``Customer`` 和 ``Supplier``，它们都继承自 ``HasAddresses`` 混入类，
    该混入类确保父类拥有一个 ``addresses`` 集合，该集合中包含了
    ``Address`` 对象。

    :viewsource:`.discriminator_on_association` 和 :viewsource:`.generic_fk` 脚本是
    2007 年博客文章
    `使用 SQLAlchemy 进行多态关联 <https://techspot.zzzeek.org/2007/05/29/polymorphic-associations-with-sqlalchemy/>`_
    中配方的现代化版本。


.. tab:: 英文

    Illustrates various methods of associating multiple types of
    parents with a particular child object.

    The examples all use the declarative extension along with
    declarative mixins.   Each one presents the identical use
    case at the end - two classes, ``Customer`` and ``Supplier``, both
    subclassing the ``HasAddresses`` mixin, which ensures that the
    parent class is provided with an ``addresses`` collection
    which contains ``Address`` objects.

    The :viewsource:`.discriminator_on_association` and :viewsource:`.generic_fk` scripts
    are modernized versions of recipes presented in the 2007 blog post
    `Polymorphic Associations with SQLAlchemy <https://techspot.zzzeek.org/2007/05/29/polymorphic-associations-with-sqlalchemy/>`_.

.. autosource::

"""  # noqa
