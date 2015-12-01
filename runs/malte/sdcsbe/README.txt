
=== About ===

Structure:

  - "megalutpkgs" contains all the required packages
  - "megalutconfig" contains settings (that you should not have to worry about!)
  - "megalutscript.py" is the script to run it (it takes command line arguments)
 
=== Installation ===

Add the "megalutpkgs" directory to the pythonpath, so that the contained packages can be imported.


=== Usage ===

Run:

	python megalutscript.py -h

... to get a description of the command line arguments.

Tip: to start with a small test, add the command line arguments "--ncpu 2 --onlyn 2".

The output gets written into the specified outdir, following the structure of the sbedatadir:

	outdir/thread_0/low_SN_image_0/MegaLUT_output.fits
	outdir/thread_0/low_SN_image_1/MegaLUT_output.fits
	...

So you could in principle give the sbedatadir also as outdir, if you want the script to write results in there.

