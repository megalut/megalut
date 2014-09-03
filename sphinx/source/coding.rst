Coding conventions
==================


Imports
-------

No using statements.

From within a subpackage or submodule, import other megalut modules usign relative paths, e.g.::

	from .. import utils

The __init__.py file of a package does not have to systematically import all subpackages. In particular, we try to avoid this when a submodule has special requirements (?).


Logging
-------

In any megalut module, write::

	import logging
	logger = logging.getLogger(__name__)
	
	# And then log with something like:
	logger.info("Hello world !")
	

General python
--------------

* tab indentation
* lowercase for all modules and packages
* lowercase for free functions, attributes, methods 
* Classes start with an uppercase

