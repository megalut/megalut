Coding conventions
==================


Imports
-------

No using statements.

From within a subpackage or submodule, import other megalut modules usign relative paths, e.g.::

	from .. import tools

The __init__.py file of a package does not have to systematically import all subpackages. In particular, we try to avoid this when a submodule has special requirements (?).


Logging
-------

In any megalut module, write::

	import logging
	logger = logging.getLogger(__name__)
	
	# And then log with something like:
	logger.info("Hello world !")

	
Use ``logger.debug`` for the not that useful stuff, to not clutter the terminal window.

Avoid logging (even debug) inside of any high-iteration loops (such as loops over sources) !


General python
--------------

* tab indentation
* lowercase for all modules and packages
* lowercase for free functions, attributes, methods
* we_try_to_avoid_too_many_underscores in method names, except to highlight a recuring structure, such as in get_x(), get_flux(), ... 
* CamelCase for classes



Assertions
----------

* It's a very good idea to use ``assert`` to make tests that should never fail, but give some extra confidence, and add useful information to the reader of the code!
  Remember that assert statements can potentially be turned off at runtime (but this is not a reason to favor assert instead of a normal if ... raise statement).

* For things that should always be tested, related for instance to use input, do not use ``assert``, but, for instance, a classical ``if not int(stampsize)%2 == 0: raise RuntimeError(...)``.

