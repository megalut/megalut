"""
Attempt to reproduce some of the difficulties of ML with a minimal example,
without any shape measurement.
"""

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)


import numpy as np
import astropy.table
import megalut
import megalut.learn
import megalut.plot
import copy
import matplotlib.pyplot as plt
import matplotlib

np.random.seed(0)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/tests"

# Values of the true parameters:
n = 10000 #5000
param = np.random.triangular(0.1, 0.3, 2.0, size=n)
cat = astropy.table.Table(masked=True)
cat["param"] = param


# We define the observables, which depend of course on the true parameters.
def observe(cat):
	cat = copy.deepcopy(cat)
	obs = np.sqrt(4.0 + cat["param"]**2) + 0.2*np.random.randn(len(cat))	
	cat["data"] = obs
	return cat


#### ATTEMPT 1: calibrate the bias(truth) relation

"""
# And we make many realizations
nrea = 20 #100
reas = [observe(cat) for i in range(nrea)]

workdir = "/vol/fohlen11/fohlen11_1/mtewes/tests"
mlparams = megalut.learn.ml.MLParams("coucou", ["data"], ["param"], ["preparam"])
toolparams = megalut.learn.fannwrapper.FANNParams([5], max_iterations=500)
trainparams = [(mlparams, toolparams)]

calibtoolparams = megalut.learn.fannwrapper.FANNParams([3], max_iterations=500)

megalut.learn.calib.ontruth(reas, workdir, trainparams, calibtoolparams)
"""


#### ATTEMPT 2: calibrate the bias(prediction) relation


# We need only one realization for this scheme

cat = observe(cat)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/tests"
mlparams = megalut.learn.ml.MLParams("coucou", ["data"], ["param"], ["preparam"])
toolparams = megalut.learn.fannwrapper.FANNParams([5], max_iterations=500)
trainparams = [(mlparams, toolparams)]

calibtoolparams = megalut.learn.fannwrapper.FANNParams([3], max_iterations=500)

megalut.learn.calib.onpred(cat, workdir, trainparams, calibtoolparams)

exit()


