"""
.. tab:: 中文

    展示了“纵向表”（vertical table）映射方式。

    “纵向表”是一种技术，将对象的各个属性作为单独的行存储在表中。
    这种“纵向表”技术用于持久化那些属性集合不固定的对象，
    其代价是牺牲了查询的简洁性和控制的直接性。
    此技术常用于内容/文档管理系统中，以灵活地表示用户自定义的结构。

    此示例提供了两种变体方式。
    在第二种方式中，每一行会引用一个“数据类型”（datatype）对象，
    该对象包含有关该属性所存储信息的类型（如整数、字符串或日期）的信息。

    示例::

        shrew = Animal("shrew")
        shrew["cuteness"] = 5
        shrew["weasel-like"] = False
        shrew["poisonous"] = True

        session.add(shrew)
        session.flush()

        q = session.query(Animal).filter(
            Animal.facts.any(
                and_(AnimalFact.key == "weasel-like", AnimalFact.value == True)
            )
        )
        print("weasel-like animals", q.all())


.. tab:: 英文


    Illustrates "vertical table" mappings.

    A "vertical table" refers to a technique where individual attributes
    of an object are stored as distinct rows in a table. The "vertical
    table" technique is used to persist objects which can have a varied
    set of attributes, at the expense of simple query control and brevity.
    It is commonly found in content/document management systems in order
    to represent user-created structures flexibly.

    Two variants on the approach are given.  In the second, each row
    references a "datatype" which contains information about the type of
    information stored in the attribute, such as integer, string, or date.


    Example::

        shrew = Animal("shrew")
        shrew["cuteness"] = 5
        shrew["weasel-like"] = False
        shrew["poisonous"] = True

        session.add(shrew)
        session.flush()

        q = session.query(Animal).filter(
            Animal.facts.any(
                and_(AnimalFact.key == "weasel-like", AnimalFact.value == True)
            )
        )
        print("weasel-like animals", q.all())

.. autosource::

"""
