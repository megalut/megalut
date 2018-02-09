Nov 2017
========

Not a euclid-sized Gaussian PSF, but more a "ground-based" situation, to demonstrate PSF correction clearly.
Sky-limited observations with Gaussian noise
Mostly "uniform" distributions


Simulations
-----------

Dataset categories:

  * si : "simulation inspection" : a simple set of galaxies drawn from the parameter distributions, to test feature measurements etc.
  * ts : "train shear" : cases contain always the same galaxy, rotated on a ring
  * vs : "validate shear" : same structure as ts, to probe (conditional) biases of the shear point estimate (without weights)
  * tw : "train weights" : cases contain different galaxies, no SNC.
  * vo : "validate overall" : cases contain different galaxies (potentially with SNC) 


We have several configurations for each category:


ts-1 : 0.25 Mgal
ts-2 : 4 Mgal, 126 GB

vs-1
vs-2
vs-3 : 50 Mgal, 1.1 TB, less than a night with 50 cpu


tw-1 : 1 Mgal, 32 GB

vo-1 : 1 Mgal, no SNC
vo-2 : 20 Mgal, 383 GB



Trainings
---------




ts-2 sum55
ts-2 sum5




tw-1 : 100 its on 1Mgal take 30 min




Plots
-----

plot_4_paper
plot_5_paper

plot_6_paper


Todo
----


Euclid-like:
  * fix bincenters in conditional bias plots to be the mean x value of the actual points in each bin
  * use plasma_r




