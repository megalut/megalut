

About
=====


This code illustrates the use of MegaLUT on GREAT3 data and reproduces the related figures from our paper. The scripts might be useful to play with GREAT3, but are not meant and do not have the quality to be reused for other purposes or surveys.

We focus on the constant-shear single-epoch constant-PSF branches, but running on the corresponding variable-shear branches is equally simple.

A goal of this "pipeline" is to remain flexible enough to allow for easy experimentation. It should be relatively easy to test and compare different settings. 



Installation
============

The pipeline uses pyhton 2.7 and the usual "scipy stack" (numpy, scipy, matplotlib). In addition, you will need:

- GalSim (1.4 or above) https://github.com/GalSim-developers/GalSim
- astropy (1.1 or above)
- Tenbilac
	- ADD INFO HERE
- MegaLUT
	- ADD INFO HERE
- MegaLUT-GREAT3 wrapper
	- ADD INFO HERE



Tutorial
========

In principle, we'll run the scripts one after the other, in there alphabetical order (given by the numbers in their filenames). A description of the workflow will be given below. But before describing the scripts, here is a first overview of the configuration.

Note: in the following, we use the wording "shear estimator" even for ellipticity estimators. Regarding the code, the difference is very small.


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
	the definition of the names encountered in config.py.

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

Some scritps will use multiprocessing to run on several cpus. Related settings will be described in the following.


_Let's start!_

First, copy the file `config_cgc.py` into `config.py`, and edit the obvious lines: set the datadir correctly, and point to an empty workdir (an create it) somewhere on your disk.
You are then ready for the first script, also to test that everythign is in place:

### run_11_measstars.py

This is a rather fast one. It runs a shape measurement (apaptive moments) on the 9 "star" stamps of each subfield of the given branch.
We'll need this data for all subfields, but you could also start by setting `subfields = [0]` in your `config.py` to get a first idea. Afterwards, run it again with `subfields = range(0, 200)` (or `subfields = range(1, 200)`, as 0 is already done). Of course, such a split in subfields can also be done with all the other scripts.

MegaLUT uses astropy tables to hold all catalogs. And it saves these tables into python pickle files. The result of this script is such a catalog, in your workdir/subfield/obs: `star_meascat.pkl`. 

### run_12_measobsgals.py

This is a not-that-fast one, it measures the features on the GREAT3 galaxies (we call them "obs", for "observed", to distinguish them from MegaLUT-internal simulations).

This script uses multiprocessing: before starting it, set the option `ncpu` in config.py to the number of cpus you want to use. 

As for the previous one, this script also write its measurements into pkl catalogs.

### run_13_checkpsfs.py

This is very fast an easy: it just prints out a sorted table of subfields according to the measured PSF size.
It allows you to identify the subfield with the sharpest PSF (smallest `psf_adamom_sigma`), e.g. for checking that training galaxies match to the "observations".

**Hint**: in your workdir, duplicated the subfield-directory with the best PSF by adding 1000 (for CGC, that's `cp -r ./99 ./1099`). This is convenient to test scripts without messing up the actual subfields on which you want to run the full pipeline later.  

### run_21_sim.py

This script takes a command line argument (namely one "key" of the datasets-directory in config.py), and ultimately you'll run it several times to generate different datasets.

Let's start by checking that our simulation parameters roughly cover the GREAT3 galaxies. 

Start by setting `subfields = [1099]`, just for your tests.

Make sure that in your `config.py` datasets, "simobscompa" points to "simobscompa-G3". "G3" distributions are relatively close to GREAT3, while "train" distributions (i.e., `simobscompa-train`) are more uniform.

Then, run `python run_21_sim.py simobscompa` which draws one simulated "subfield" with 10'000 galaxies without shear, and directly runs the feature measruement on these galaxies. You'll find the generated files in the corresponding `sim` and `simmeas` directories in `workdir/1099`.

Once this is done, you can run `plot_1_simobscompa.py`, which compares the distribution of feature measurements on GREAT3 and on your simulations with many panels. **You can now also run paperfig_1_simobscompa.py to reproduce the related figure in our paper**.

To experiement with different distributions, you would make adjustements in `simparams.py`. Parameters regarding the "structure" and size of the simulations would have to be set directly in `run_21_sim.py`. Note that 1000 galaxies are sufficient for nice histograms. **Make sure to manually remove previous output files of the same simname, or the new sims will be added to them, mixing settings!**.

To proceed with the pipeline and train the machine learning, we need to simulate at least to datasets per subfield: one to train ellipticity estimates (called shear, but real shear estimatse turns out to be unnecessarily slow here, so in fact we'll learn to predict ellipticity of our simply Sersic profiles), and one to train weights. To get these datasets, for **each subfield**, we need:
- `python run_21_sim.py train-shear`
- `python run_21_sim.py train-weight`

These are both rather massive. The script uses multiprocessing, but this time the number of cpus is directly set into `run_21_sim.py` as it depends a bit on the structure of the dataset to generate.

Optional: if you want to perform some validations, typically to test machine learning settings, you could also generate
- `python run_21_sim.py valid-shear`
- `python run_21_sim.py valid-overall`
... but this is even more massive (it's an entire GREAT3 branch per subfield), and you certainly don't want this for every subfield.

Finally, you could also generate (for each subfield)
- `python run_21_sim.py mimic-great3`
... which creates 10'000 Sersic galaxies (including a simple shape noise cancellation) giving a "fiducial" branch whose galaxies share the same properties as the ones used for training.



### run_31_learn.py

This script trains the shear prediction. It uses the "train-shear" dataset from the previous step.
A training is controlled by 2 types of configurations, and the `shearconflist` of `config.py` contains, for each component, a tuple of 2 paths pointing at the corresponding configuration files:

- `mlconfig/ada*.cfg`
	- what features and inputs should be fed into Tenbilac, and how the predicted output data should be named.

- `mlconfig/sum*.cfg`
	- These are Tenbilac configuration files, with all the Tenbilac settings (what network architecture, which error function, how many iterations, etc).

Runnign the scirpt creates a directory in `workdir/subfield/ml` in which all the network parameters are saved. In addition, this script also saves two PNG plots about the training. One shows the evolution of the cost function value, the other one shows results of self-predictions on the training set.

### run_32_val.py

Optional: not required for further scripts.

This script tests the training, by appliying the neural networks on an independent "validation set". The plot style is the same as the "self-prediction" plot generated right after the training.

To run this, the "valid-shear" dataset is required for the same subfield.

Note: given the structure of GREAT3 with its 200 different PSFs, we don't spend enough resources (training dataset size) to get negligible "biases" for each individual PSF. You are likely to see residual biases here, but those depend mostly randomly on the realization of the training-set, and won't show up as "biases" over the full branch.

### run_33_valw.py

Same as 32, but also predicts weights. Can only be run if you already trained the weight predictions with the 4X scripts.


### run_41_predforw.py

We now come to the weight training, using the "train-weight" dataset.
Before we can start with the training itself, this script applies the above shear estimator to predict the shear for every galaxy of the "train-weight" dataset. The weight training depends on this existing shear estimator.


### run_42_learnw.py

Does the actual weight training. This is again relatively slow.
The settings are very similar to run_31_learn.py: it works with the files specified in `config.weightconflist`.

Advanced hint, "pre-training": the script accepts a subfield number as optional command line argument (`python run_42_learnw.py -s 1099`). If you specify this, the script will start by copying the training from this particular subfield to the one its currently working on, and then start the training of the neural networks from there. This allows you to first run a large number of iterations on a single subfield, and then use this as initial conditions for the training on the other subfields.



### run_43_valw.py

Applies both the shear estimator specified in `config.shearconflist` and the weight estimator `config.weightconflist` to the massive `valid-overall` dataset and generates a plot summarizing the results in terms of shear biases. 
Again, this is optional, but allows you to test the training. See the note about biases from script 32.


### run_51_predg3obs.py

Predicts shear and weights (using the shearconflist and weightconflist specified in `config.py`) for the GREAT3 subfield galaxies.

In `config.py`, you can specify a "predcode" at the very bottom. From this script on, change this number if you want to use several sets of shear estimators and/or weights. The number is used in filenames to distinguish between these repeated runs. Not changing it would overwrite files.


### run_52_groupg3obs.py

Computes the average weighted shear in each GREAT3 subfield, saving this (as well as the true shear, the orientation of the PSF) into a small table.

### run_53_evag3obs.py

Uses this small table to compute metrics and plot results.
 **You can now also run paperfig_2_evag3obs.py to reproduce the related figure in our paper**.

### run_61_prepsubmission.py
### run_62_officialevasubmission.py

These scripts 61 and 62 allow you to get the same metrics as the 52-53 scripts, but using the official GREAT3 evaluation code.
For this to work, clone `https://github.com/barnabytprowe/great3-public` on your system, and specify the `g3publicdir` (pointing to the clone) in your `config.py`.

### run_71_predg3mocks.py
### run_72_groupg3mocks.py
### run_73_evag3mocks.py

These 3 last scripts do the same as 5X, but run on the "fiducial" dataset (generated via `run_sim_21.py mimic-great3` instead of the 

Output files are different, this will not overwrite anything from the 5X or 6X scripts, but the `config.predcode` setting still applies, if you want to compare several results.










