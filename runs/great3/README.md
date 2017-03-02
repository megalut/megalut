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

