pymzqc Modules
================

The main pymzqc module consists of three submodules and a compainon module for accessories.
Please note that most member attributes of the MZQCFile submodule classes and many functional elements do not conform to PEP8.
The element names of the mzQC JSON-schema need to be preserved in order to create a successful and automated JSON<=>pymzqc object mapping. 
Accordingly, other elements such as functions in all pymzqc modules will keep the JSON-schema names in their naming for consistency.


mzqc.MZQCFile submodule
-----------------------

.. automodule:: mzqc.MZQCFile
   :members:
   :undoc-members:
   :show-inheritance:

mzqc.SemanticCheck submodule
----------------------------

.. automodule:: mzqc.SemanticCheck
   :members:
   :undoc-members:
   :show-inheritance:

mzqc.SyntaxCheck submodule
--------------------------

.. automodule:: mzqc.SyntaxCheck
   :members:
   :undoc-members:
   :show-inheritance:

pymzqc Accessories Module
-------------------------

The compainon module for accessories to handle mzqc via tools (and CLI) rather than REPL can be useful when building processing chains or checking new files.

Any installation process using setup.py (e.g. pip) will create an additional module  `mzqcaccessories` 
exclusively for the `entry_points` scripts created (for use see :doc:`Accessories <./accessories>` page).
