

About
=====

This code illustrates the use of MegaLUT on GREAT3 data and reproduces the figures from our paper.
We focus on the constant-shear single-epoch constant-PSF branches, but running on the corresponding variable-shear branches is equally simple.

A goal of this "pipeline" is to remain flexible enough to allow for easy experimentation. It should be relatively easy to test and compare different settings. 

In principle, we'll run the scripts one after the other.
There is no centralised configuration scheme for these scripts. Before describing the scripts, here is a first overview of the configuration. You could have a look at those files, just to get a feeling of what's in there:

  - config.py
  	This is the top-level configuration file. It contains:
  	- paths to the GREAT3 data, what branch and what subfields to process
	- which datasets (defined by "simnames") to use for training and validation
	- which configuration-files to use for the machine learning

	The contents of this config.py depend on your environment. To get startet, copy one of our configs (e.g., config_cgc.py) into
	config.py and edit the various paths as needed.

  - measfcts.py
    - settings related to the feature measurements

  - simparams.py
    - description of the simulations, galaxy parameter distributions 

  - run_21_sim.py
  	Hardcoded in this script are the descriptions of the structures and sizes of the datasets to be simulated, i.e.
	the definition of the "simnames".

  - mlconfig/
  	Files in here are configurations for the machine learning with Tenbilac.




Tutorial
========


To start discovering, simobscompa
















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

