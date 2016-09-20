About
=====

The current (Fall 2016) approach to GREAT3.
We focus on the single-epoch known-PSF branches.

There is no sophisticated "configuration" scheme here. Many settings are directly hard-coded in the scripts, as this seems to  make development easier.


Contents
--------


- ``config_example.py``: Copy this into ``config.py`` and customize it with your settings.


- ``run_*_.py``: Main demonstration pipeline, reproducing the paper figures.






"Pipelines"
===========

Different paths can be followed to "run". Here we describe those we care about. 

We will at least try not to break these pipelines too badly when editing scripts.


Common training
---------------

Have one "common training" for a branch, that is, mix all PSFs from the different subfields.

Sept. 2016, Malte is working on this.

- run_0
- run_11
- run_12
- run_13
- run_22
- plot_1

