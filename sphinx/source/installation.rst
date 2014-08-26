Download & Installation
=======================


Dependencies
------------

MegaLUT is currently developed using python 2.7 (but might be fine with older versions).

It uses the usual numpy, scipy, matplotlib, and

* GalSim
* astropy


Download
--------


Installation
------------

The easy answer, if you do not plan to tweak the code : cd into the ``megalut`` directory, and::

	python setup.py install

or maybe::

	python setup.py install --user

... if you don't have write access to the global site-packages directory of your machine. More info about this type of installation: `<http://docs.python.org/install/>`_. 


The longer answer: especially if you want to tweak/read the code and do frequent commits or updates, just add the directory containing ``megalut`` to your ``PYTHONPATH``.
That way you can keep MegaLUT in any convenient place on your system, and modify it on the fly, without having to ``python setup.py install`` after any modification.

For tcsh, add for instance something like this to your .tcshrc ::


	#setenv PYTHONPATH /path/to/MegaLUT
	# or, to add to the existing stuff :
	
	setenv PYTHONPATH ${PYTHONPATH}:/path/to/MegaLUT
	
or, if you use bash, to your .bash_profile or equivalent::

	export PYTHONPATH=${PYTHONPATH}:/path/to/MegaLUT/

... and then from any python you can simply ``import megalut``.


