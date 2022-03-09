Usage examples
**************
I am a fan of quick hands-on overviews to get to know software, that I might or might not use in the future.
Several hands-on examples can be found `here. <https://github.com/MS-Quality-hub/pymzqc/tree/main/jupyter>`_ 
A video version for ASMS'22 is `on youtube: <https://www.youtube.com/watch?v=vZXJuPl2yGw>`_

The copy&paste essentials:

Load
------------------------------

.. code-block:: python
    from mzqc import MZQCFile as qc
    with open("nameOfYourFile.mzQC", "r") as file:
        my_run_qualities = qc.JsonSerialisable.FromJson(file)

Access elements
------------------------------
see `schema <https://github.com/HUPO-PSI/mzQC/tree/main/schema>`_ for a general overview of available elements.

.. code-block:: python
    # An in-memory mzQC file will still have the same hierarchical structure as the schema
    print(my_run_qualities.description)

    # JSON arrays can be used like python lists
    for m in my_run_qualities.qualityMetrics:
        print(m.name)

    # You can traverse the hierarchy with standard python member access notation ('.') 
    # and get to the bottom of things (like a metric value).
    ms2_number = my_run_qualities.qualityMetrics[2].value

Store
------------------------------

.. code-block:: python
    inmem_file = qc.JsonSerialisable.ToJson(mzqc, readability=1)
    with open("nameOfYourFile.mzQC", "w") as file:
        file.write(inmem_file)
