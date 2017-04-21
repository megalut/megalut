import megalut
import config
import measfcts
import glob
import os
import numpy as np
import astropy

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)




cat = megalut.tools.io.readpickle("/vol/fohlen11/fohlen11_1/mtewes/Euclid/senstest/sample_data_2017-03-29/prods/sensitivity_testing_sample_noisy_0/meascat_sensitivity_testing_sample_noisy_0.pkl")


print megalut.tools.table.info(cat)


fig = plt.figure(figsize=(16, 10))
#fig = plt.figure(figsize=(8, 8))

ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("adamom_theta"), Feature("rotation"), sidehists=True)

ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("snr", 0, 50), Feature("adamom_sigma", 0, 6), sidehists=True)

ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("magnitude"), Feature("adamom_logflux", 2, 4), Feature("snr", 0, 50))

ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("sersic_index"), Feature("bulge_fraction"), sidehists=True)
ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("rotation"), Feature("tilt"), sidehists=True)
ax = fig.add_subplot(2, 3, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("spin"), Feature("bulge_axis_ratio"), sidehists=True)


plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
#plt.close(fig) # Helps releasing memory when calling in large loops.
