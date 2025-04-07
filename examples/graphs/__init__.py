"""
.. tab:: 中文

    有向图结构持久性的示例。该图存储为边的集合，每个边都引用节点表中的“下”节点和“上”节点。下图说明了基本持久性和对下邻居和上邻居的查询::

        n2 = Node(2)
        n5 = Node(5)
        n2.add_neighbor(n5)
        print(n2.higher_neighbors())

.. tab:: 英文

    An example of persistence for a directed graph structure.   The
    graph is stored as a collection of edges, each referencing both a
    "lower" and an "upper" node in a table of nodes.  Basic persistence
    and querying for lower- and upper- neighbors are illustrated::

        n2 = Node(2)
        n5 = Node(5)
        n2.add_neighbor(n5)
        print(n2.higher_neighbors())

.. autosource::

"""
