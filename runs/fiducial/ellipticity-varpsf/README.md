Contents
========

This run of MegaLUT is a not so trivial simulation meant to be a stepping stone between very simple tests and an application to Great3.

This directory contains Sersic galaxies and varying parameters. This is a PSF variable run, see details in `psf.py`.

The scripts are meant to be executed in the following order:

1. Generate simulations

    - Edit `simparams.py` to control most of the simulation parameters (except noise and number of sims)
    - `python 11_run_sim_train.py` prepares the mock galaxies for training Tenbilac
    - `python 12_run_sim_validation.py` prepares the galaxies for the validation set. This must be large in order to test the bias at sufficiently low levels. You should draw O(1e6) galaxies at least.
    - `python 13_plot_distribs.py` plots some of the measured propreties of the galaxies against each other.

2. Train Tenbilac

    - Edit `config/name_of_data_config.cfg` to select the input and output features
    - Edit `config/name_of_Tenbilac_config.cfg` to set the parameters of Tenbilac (including the training)
    - `python 21_run_train.py` to train the algo. Make sure you do a sufficently high number of iterations. Comparing the convergence across committee member gives a good indication.

3. Evaluate the performance on both sets.

    - `python 22_plot_results_train.py` will output statistics and plots on the performance on Tenbilac on the known training set in terms of ellipticity.
	- `python 31_run_pred_valid.py` to predict the shear
    - `python 32_plot_results_validation.py` does the same plots for the validation in terms of shear. It is important to make sure that the validation set has not been seen previously during training.
    - `python 33_plot_fancy.py` generate the paper plots. 
    - Edit and run `34_analyse_res.py` which analyse the outliers (i.e. cases which have a bias above a manually set threshold).

4. Loop to improve the performance on the validation set


