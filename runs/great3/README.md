

About
=====


This code illustrates the use of MegaLUT on GREAT3 data and reproduces the related figures from our paper. The scripts might be useful to play with GREAT3, but are not meant and do not have the quality to be reused for other purposes or surveys.

We focus on the constant-shear single-epoch constant-PSF branches, but running on the corresponding variable-shear branches is equally simple.

A goal of this "pipeline" is to remain flexible enough to allow for easy experimentation. It should be relatively easy to test and compare different settings. 


Tutorial
========

In principle, we'll run the scripts one after the other, in there alphabetical order (given by the numbers in their filenames). A description of the workflow will be given below. But Before describing the scripts, here is a first overview of the configuration.


Overview of the configuration
-----------------------------

There is no centralised configuration scheme for these scripts.
Before starting to run anything, we suggest that you have a look at the following files, to get a feeling of what's in there:

  - config.py (or config_cgc.py etc):
  	This is the top-level configuration file. It contains:
  	- paths to the GREAT3 data, what branch and what subfields to process
	- which datasets (defined by "simnames") to use for training and validation (those are defined in run_21_sim.py and simparams.py, described below)
	- which configuration-files to use for the machine learning

	The contents of this config.py will depend on your environment. To get startet, copy one of our configs (e.g., config_cgc.py) into
	config.py and edit the various paths as needed.

  - measfcts.py :
    - settings related to the feature measurements, in particular what should get measured

  - simparams.py :
    - description of the simulations, galaxy parameter distributions 

  - run_21_sim.py :
  	Hardcoded in this script are the descriptions of the structures and sizes of the datasets to be simulated, i.e.
	the definition of the "simnames" encountered in config.py.

  - mlconfig/
  	Files in here are configurations for the machine learning with Tenbilac.
	There are two kinds of files:
	- ada*.cfg tell MegaLUT what features and inputs should be fed into Tenbilac, and how the predicted output data should be named.
	- sum*.cfg are actual Tenbilac configuration files, with all the Tenbilac settings.



Workflow
--------

If not mentionned otherwise, the scripts take no command line arguments. 

Before running any script, make sure to set the correct range of subfields on which you want to run in config.py.
The scripts typically contain loops over all the specified subfields.

Some scritps will use multiprocessing to run on several cpus. Related settings will also be described below.
And we'll also highlight some other settings.


Let's start!

First, copy the file config_cgc.py into config.py, and edit the obvious lines: set the datadir correctly, and point to an empty workdir (an create it) somewhere on your disk.
You can then launch the first script, also to test that everythign is in place:

- run_11_measstars.py

This is a rather fast one. It runs a shape measurement (apaptive moments) on the 9 "star" stamps of each subfield of the given branch.

MegaLUT uses astropy tables to hold all catalogs. And it saves these tables into python "pickle" files. The result of this script is such a catalog, in your workdir/subfield/obs: "star_meascat.pkl".

- run_12_measobsgals.py






To test the effect of different settings in the simparams.py, you can reduce the number of cases, 1000 galaxies are sufficient for nice histograms. Also, make sure you remove previous files of the same simname, or the new sims will be added to them, mixing settings!




To start discovering, simobscompa



After this, we manually duplicated the directory (within workdir) corresponding to the best PSF, adding 1000 to its number, to have a playground subfield to test settings. This is why some scripts might refer to, e.g., subfield 1194 for branch RSC, which is just a copy of subfield 194.














About
=====

The current (Spring 2017) approach to GREAT3.
We focus on the single-epoch known-PSF branches.

There is no sophisticated "configuration" scheme here. Many settings are directly hard-coded in the scripts.
This make development easier, plus you learn more about the code.


Contents
--------


- ``run_*_.py``: Main demonstration pipeline, reproducing the paper figures.






"Pipelines"
===========

Different paths can be followed to "run". Here we describe those we care about. 

We will at least try not to break these pipelines too badly when editing scripts.


Individual training
-------------------

One training per subfield, as the PSFs of different subfields are too different to mix them.

- run_11
- run_12
- run_13

- run_21


- run_3

- run_5
- run_51
- run_52



Common training
---------------

Have one "common training" for a branch, that is, mix all PSFs from the different subfields.

Sept. 2016, Malte is working on this.

- run_0
- run_11
- run_12
- run_13
- run_15, to find the best subfield

Then, if the sims are not yet tuned, iterate on
- editing simparams (snc_type can be set to 1, config.subfields just to the best subfield)
- run_22 (pick different sp.name for your tests)
- plot_1

