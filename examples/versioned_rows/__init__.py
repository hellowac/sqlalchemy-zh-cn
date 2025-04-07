"""
.. tab:: 中文

    几个示例说明了拦截更改的技术，这些更改最初会被解释为对某行的更新，而是将其转换为对新行的插入，而前一行则保持完整，作为历史版本。

    与 :ref:`examples_versioned_history` 示例相比，该示例将历史行写入单独的历史表。

.. tab:: 英文


    Several examples that illustrate the technique of intercepting changes that would be first interpreted as an UPDATE on a row, and instead turning it into an INSERT of a new row, leaving the previous row intact as a historical version.

    Compare to the :ref:`examples_versioned_history` example which writes a history row to a separate history table.

.. autosource::

"""
