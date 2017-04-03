

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

First, copy the file `config_cgc.py` into `config.py`, and edit the obvious lines: set the datadir correctly, and point to an empty workdir (an create it) somewhere on your disk.
You can then launch the first script, also to test that everythign is in place. We'll need this data for all subfields, but you could also start by setting `subfields = [0]` in your `config.py` to get a first idea. Afterwards, run it again with `subfields = range(0, 200)` (or `subfields = range(1, 200)`, as 0 is already done). Of course, this can also be done with all the other scripts.

### run_11_measstars.py

This is a rather fast one. It runs a shape measurement (apaptive moments) on the 9 "star" stamps of each subfield of the given branch.

MegaLUT uses astropy tables to hold all catalogs. And it saves these tables into python "pickle" files. The result of this script is such a catalog, in your workdir/subfield/obs: "star_meascat.pkl". 

### run_12_measobsgals.py

This is a not-that-fast one, it measures the features on the GREAT3 galaxies (we call them "obs", for "observed", to distinguish them from MegaLUT-internal simulations).

This script uses multiprocessing: before starting it, set the option `ncpu` in config.py to the number of cpus you want to use. 

As for the previous one, this script also write its measurements into pkl catalogs.

### run_13_checkpsfs.py


### run_21_sim.py

To test the effect of different settings in the simparams.py, you can reduce the number of cases, 1000 galaxies are sufficient for nice histograms. Also, make sure you remove previous files of the same simname, or the new sims will be added to them, mixing settings!


### run_31_learn.py
### run_32_val.py
### run_33_valw.py
### run_41_predforw.py
### run_42_learnw.py
### run_43_valw.py
### run_51_predg3obs.py
### run_52_groupg3obs.py
### run_53_evag3obs.py
### run_61_prepsubmission.py
### run_62_officialevasubmission.py
### run_71_predg3mocks.py
### run_72_groupg3mocks.py
### run_73_evag3mocks.py


To start discovering, simobscompa



After this, we manually duplicated the directory (within workdir) corresponding to the best PSF, adding 1000 to its number, to have a playground subfield to test settings. This is why some scripts might refer to, e.g., subfield 1194 for branch RSC, which is just a copy of subfield 194.














