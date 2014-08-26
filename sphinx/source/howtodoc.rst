Building this documentation
===========================

This documentation is made using Sphinx (`<http://sphinx-doc.org>`_).

To build the documentation by yourself (assuming you have the latest version of sphinx), ``cd`` into the ``sphinx`` directory of the MegaLUT distribution, and::

	[make clean]
	make apidoc
	make html 

You can then open ``index.html`` that you will find in ``build/html/`` with your browser...