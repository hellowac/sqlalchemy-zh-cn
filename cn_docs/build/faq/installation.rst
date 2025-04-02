安装
=================

Installation

.. contents::
    :local:
    :class: faq
    :backlinks: none

.. _faq_asyncio_installation:

当我尝试使用 asyncio 时，出现有关未安装 greenlet 的错误
----------------------------------------------------------------------------------

I'm getting an error about greenlet not being installed when I try to use asyncio

.. tab:: 中文

    ``greenlet`` 依赖项默认情况下不会为 ``greenlet`` 未提供 `预构建二进制wheel <https://pypi.org/project/greenlet/#files>`_ 的CPU架构安装。
    特别是， **这包括 Apple M1** 。 要安装包括 ``greenlet`` 在内的包，请在 ``pip install`` 命令中添加 ``asyncio`` `setuptools extra <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-setuptools-extras>`_:

    .. sourcecode:: text

        pip install sqlalchemy[asyncio]

    有关更多背景信息，请参见 :ref:`asyncio_install`。

.. tab:: 英文

    The ``greenlet`` dependency does not install by default for CPU architectures
    for which ``greenlet`` does not supply a `pre-built binary wheel <https://pypi.org/project/greenlet/#files>`_.
    Notably, **this includes Apple M1**.    To install including ``greenlet``,
    add the ``asyncio`` `setuptools extra <https://packaging.python.org/en/latest/tutorials/installing-packages/#installing-setuptools-extras>`_
    to the ``pip install`` command:

    .. sourcecode:: text

        pip install sqlalchemy[asyncio]

    For more background, see :ref:`asyncio_install`.


.. seealso::

    :ref:`asyncio_install`


