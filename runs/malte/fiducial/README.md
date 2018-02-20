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

vs-1 : for testing plots only
vs-2 : 10 Mgal
vs-3 : 50 Mgal, 1.1 TB, == Thibault's size, less than a night with 50 cpu


tw-1 : 1 Mgal, 32 GB
tw-2 : 10 Mgal, == Thibaults size

vo-1 : 1 Mgal, no SNC
vo-2 : 20 Mgal, 383 GB



Trainings
---------




ts-2 sum55 : 12 hours for 1000 iterations
ts-2 sum5



ts-e-1 sum55 : 3:44 for 1000 iterations 


tw-1 sum55w : 100 its on 1Mgal take 30 min
tw-1 sum55w : 1000 its take 4:40




Plots
-----



Can probably be deleted:
plot_4_paper


Todo
----


vs figure with vs-3 selected by SN > 10 to see if that looks acceptable.

launch ts-3-faint-ln ? fast, can do later.

- decide if min_tru_rad 3 or 4, and then maybe run sims ts-2-large



We generate many realizations per case for the weight training, so that the cost function is dominated by errors made on small/faint galaxies, not by shape noise.
However only few cases are needed, 100 is already large. Maybe 10 would work better (stochastic)
-> running tw-2 to see if it works at all now. No, it didnt, and it takes ages / stops early.

New idea: add more crap galaxies to the training, by lowering the min_tru_sb.
Makes it easier to see/learn the effect of weights

-> see how the trainigs on tw-4-faint look



If everything fails: add SNC to weight training set ?


Running
-------

	
- sim ts-2-easy
	Try to get a decently low contidional bias with this
- sim ts-3-ln
	Meant to be a fast way to generate pre-trained nets
	
Use flux instead of logflux with these, to reduce the impact of differences in low flux values



What I've learnt
----------------

- training ts-2, starting from ts-e-1
	Yes, looks at least as good as starting directly.

Check training on ts-2
-  comparing sum5 and sum55
-> sum55 is better!

Check trainings ts-e-1
- ts-2 or ts-e1
-> ts-e-1 seems better, but maybe ts-2 can still improve ?


- comparing ada4 and ada5
Check (using fast ts-e-1 ?) that ada5s1 is not better than ada4s1.
-> does not seem to make a difference. using ada5 is more straightforward.


--> go for ada5_sum55



To be discussed with Thib
-------------------------

Check that even for ts-e-1, the bright galaxise sometimes make the feature meas fail.
-> yes, this is the case. A bit weird. Make a project to investigate?

Check (using fast ts-e-1 ?) that ada5s1 is not better than ada4s1.

Euclid-like:
  * fix bincenters in conditional bias plots to be the mean x value of the actual points in each bin
  * use plasma_r




