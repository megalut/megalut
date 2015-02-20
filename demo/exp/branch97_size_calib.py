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
n = 1000 #5000
param = np.random.triangular(0.1, 0.3, 2.0, size=n)
cat = astropy.table.Table(masked=True)
cat["param"] = param


# We define the observables, which depend of course on the true parameters.
def observe(cat):
	cat = copy.deepcopy(cat)
	obs = np.sqrt(4.0 + cat["param"]**2) + 0.2*np.random.randn(len(cat))	
	cat["data"] = obs
	return cat


# And we make many realizations
nrea = 20 #100
reas = [observe(cat) for i in range(nrea)]


# We save those reas into different pickles ?



# Compute the averages 
#cat = megalut.tools.table.groupstats(reas, groupcols=["obs1"], removereas=False)


# First ML is to get point estimates:

workdir = "/vol/fohlen11/fohlen11_1/mtewes/tests"
mlparams = megalut.learn.ml.MLParams("coucou", ["data"], ["param"], ["preparam"])
toolparams = megalut.learn.fannwrapper.FANNParams([5], max_iterations=500)
trainparams = [(mlparams, toolparams)]

calibtoolparams = megalut.learn.fannwrapper.FANNParams([3], max_iterations=500)

megalut.learn.calib.train(reas, workdir, trainparams, calibtoolparams)



exit()


# We self-predict the catalog:

cat = megalut.learn.run.predict(cat, workdir, trainparams, tweakmode="all", totweak="_rea0")
#cat = megalut.learn.run.predict(cat, workdir, trainparams, mode="first") # To get pre1 (based on obs1_0)
cat = megalut.learn.run.predict(cat, workdir, trainparams, tweakmode="default")


# Bias correction

cat["bias1"] = cat["pre1_mean"] - cat["param1"]
cat["pre1_single"] = cat["param1"][:]
#cat["obs1_single"] = cat["obs1_rea0"][:]

mlparams = megalut.learn.ml.MLParams("bias1", ["pre1_single"], ["bias1"], ["prebias1"])
toolparams = megalut.learn.fannwrapper.FANNParams([5, 5], max_iterations=500)
trainparams = [(mlparams, toolparams)]
megalut.learn.run.train(cat, workdir, trainparams)

# Self-predict the bias correction
cat = megalut.learn.run.predict(cat, workdir, trainparams, tweakmode="default")
cat["prebias1"].name = "autoprebias1"


cat = megalut.learn.run.predict(cat, workdir, trainparams, tweakmode="all", totweak="_single")

# Gives prebias1_mean

# Correct bias, based on prediction:

#cat["pre1cor"] = cat["pre1"] - cat["prebias1"]

cat["bias2"] = cat["pre1_mean"] - cat["prebias1_mean"]  - cat["param1"]



param1 = megalut.plot.feature.Feature("param1", 0.0, 2.2, r"$\theta$")
obs1 = megalut.plot.feature.Feature("obs1_rea0", 1.5, 3.0, r"$d$")
obs1_mean = megalut.plot.feature.Feature("obs1_mean", 1.5, 3.0, r"$d$")
pre1 = megalut.plot.feature.Feature("pre1", 0.0, 2.2, r"$\hat{\theta}$")
pre1_mean = megalut.plot.feature.Feature("pre1_mean", 0.0, 2.2, r"$<\hat{\theta}>$")

bias1 = megalut.plot.feature.Feature("bias1", -1.0, 1.0, r"bias = mean$(\hat{\theta}) - \theta$")
prebias1 = megalut.plot.feature.Feature("prebias1", -1.0, 1.0, r"bias = mean$(\hat{\theta}) - \theta$")
autoprebias1 = megalut.plot.feature.Feature("autoprebias1", -1.0, 1.0, r"bias = mean$(\hat{\theta}) - \theta$")

pre1cor = megalut.plot.feature.Feature("pre1cor", 0.0, 2.2)
bias2 = megalut.plot.feature.Feature("bias2", -1.0, 1.0)



fig = plt.figure(figsize=(19, 12))
matplotlib.rcParams['axes.labelsize'] = "xx-large"

ax = fig.add_subplot(2, 3, 1)
#megalut.plot.scatter.scatter(ax, cat, param1, obs1_mean, color="orange", label="Average over realizations")
megalut.plot.scatter.scatter(ax, cat, pre1, obs1, color="red")
megalut.plot.scatter.scatter(ax, cat, param1, obs1, sidehists=True)


#ax.legend()
#ax.xaxis.label.set_size(30)
#ax.yaxis.label.set_size(30)

ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, param1, bias1)
megalut.plot.scatter.scatter(ax, cat, param1, autoprebias1, color="green")

ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, pre1, bias1)
megalut.plot.scatter.scatter(ax, cat, pre1, autoprebias1, color="green")

ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, pre1_mean, bias1)
megalut.plot.scatter.scatter(ax, cat, pre1_mean, autoprebias1, color="green")

ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, obs1, bias1)
megalut.plot.scatter.scatter(ax, cat, obs1, autoprebias1, color="green")

ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, cat, param1, bias2)

plt.tight_layout()
plt.show()


exit()

# And now the machine learning

# First ML is to get point estimates:

workdir = "/vol/fohlen11/fohlen11_1/mtewes/tests"
mlparams = megalut.learn.ml.MLParams("point", ["obs1_mean"], ["param1"], ["pre1"])
toolparams = megalut.learn.fannwrapper.FANNParams([5, 5], max_iterations=500)
trainparams = [(mlparams, toolparams)]
megalut.learn.run.train(cat, workdir, trainparams)

# We self-predict the catalog:

cat = megalut.learn.run.predict(cat, workdir, trainparams, mode="all") # To get pre1_std and other stats
cat = megalut.learn.run.predict(cat, workdir, trainparams, mode="first") # To get pre1 (based on obs1_0)



# Second ML to get uncertainty estimtates:

mlparams = megalut.learn.ml.MLParams("error", ["obs1_mean"], ["pre1_std"], ["pre1err"])
toolparams = megalut.learn.fannwrapper.FANNParams([5, 5], max_iterations=500)
trainparams = [(mlparams, toolparams)]
megalut.learn.run.train(cat, workdir, trainparams)

# Self-predicting them:

cat = megalut.learn.run.predict(cat, workdir, trainparams, mode="first") # To get pre1err (based on obs1_0)

# Computing a weight based on these errors:

cat["pre1err"] = np.clip(cat["pre1err"], 0.5, 10.0)
cat["pre1w"] = 1.0/cat["pre1err"]

# And now the plot
	
import matplotlib.pyplot as plt

r = 12 # radius to be displayed
param1 = megalut.plot.feature.Feature("param1", -r, r, "True parameter")
obs1 = megalut.plot.feature.Feature("obs1_0", -r, r, "Some observation")
obs1_mean = megalut.plot.feature.Feature("obs1_mean", -r, r)
pre1 = megalut.plot.feature.Feature("pre1", -r, r, "Predicted parameter", errcolname="pre1err")
pre1w = megalut.plot.feature.Feature("pre1w", nicename="Predicted weights")


fig = plt.figure(figsize=(14, 12))
ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, param1, obs1_mean, color="red", label="Training input")
megalut.plot.scatter.scatter(ax, cat, param1, obs1, sidehists=True, show_id_line=True, label="Actual observations")
ax.legend()

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, param1, pre1, sidehists=True, show_id_line=True, metrics=True)

ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, param1, pre1, pre1w)

ax = fig.add_subplot(2, 2, 4)
megalut.plot.hist.errhist(ax, cat, pre1, param1)

plt.tight_layout()
plt.show()
