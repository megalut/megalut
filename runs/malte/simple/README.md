About
-----

This is a simple demo in "script style". It does not have a "run" class or a complicated configuration system, but instead just plainly calls megalut top-level functions.

It uses very simply simulations (Gaussian galaxies and PSFs).

It is also used as a benchmark on which to develop ideas.



Work
----

train30 : fiducial -2  -> converges, but not much better
train31 : -2, 2 -> converges, but idem
train32 : -1, 1  -> converges, but not sufficient
train33 : -4, 4
train34 : 2, -2, 2 restarted, check if it correctly reuses previous one (yes, but messed up the net myself, no prob).
			Looks not too bad, actually.



to test:
- don't add bias (isntead of killing it)
- compare with mse
- start from random



train41 : -2, 2 with mse --> doesn't work at all
train42 : -2, 2 starting from random
train43 : -2, 2 with tanh and mult-biases --> converges, but same as others
train44 : 3, 3 with mse (no mult!) --> MSE fails



train 51: 3,3,3, with g2.
train 52: 3,-3,3 otherwise identical
train 53: 3,-3,3 with high noise (0.5) in all weights
train 54: 3,3,3 with high noise (0.5) in all weights


- there always is one outlier, with high g. Is the problem that g2 is missing ?
- make msb robust, kick out the worst % ?

If no progress:
- feed in true rad
- profile code
- cascade train, somehow





