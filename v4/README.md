Welcome
=======

This is MegaLUT v4 as implemented for GREAT3. Our primary repo for this was and still is on EPFL's SVN, here is just a copy of the main branch, not including the variable PSF part.


Installation
============

Get the project form SVN :

svn checkout https://svn.epfl.ch/svn/megalut-great3/trunk ./MegaLUT

Then add this directory to your python path, e.g. by adding something like this to your .profile ...

export PYTHONPATH=$PYTHONPATH:/users/mtewes/GREAT3/MegaLUT

From anywhere on your system, you can now import the "megalut" package

python
>>> import megalut



Usage
=====

Look at the great3_demo/ directory to get the main ideas!


great3_indiscripts
==================

Those are small individual scripts to perfom tests or make plots. They are not integrated into the pipeline, and are not necessary to get a GREAT3 submission.



Denoising
---------

Is optional. If you switch it on (run.denoise = "mydenoisedescription", and run.denoisethres=[...]), the measurement tasks will automatically be executed on denoised stuff.


If you then change the version, without changing the run.denoise label, the observations will not be denoised again !




