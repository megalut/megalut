
=== About ===

Structure of this directory:

  - "megalutpkgs" contains all the required packages
  - "megalutconfig" contains core-settings for MegaLUT itself
  - "megalutscript.py" is the script to run: it takes command line arguments
 
=== Installation ===

If GalSim is available, there should be nothing else to do.
Note that within megalutscript.py, we add the "megalutpkgs" directory to the pythonpath,
so that the 3 contained packages can be imported.

=== Usage ===

Run:

	python megalutscript.py -h

... to get a description of the command line arguments.

Tip: to start with a small test, add the command line arguments "--ncpu 2 --onlyn 2".

The output gets written into the specified outdir, following the structure of the sbedatadir:

	outdir/thread_0/low_SN_image_0_MegaLUT_output.fits
	outdir/thread_0/low_SN_image_1_MegaLUT_output.fits
	...

So you could in principle give the sbedatadir also as outdir, if you want the script to write results in there.


=== About the configuration ===

The configuration is split into two parts:

1) The "megalutconfig" directory contains the core settings related to MegaLUT itself, agnostic of any data structure.

2) The settings related to the wrapper, and to the structure of the SBE simulations,
are all grouped directly in the script (see the "settings" dict...), and can be controlled using
command line arguments.

