import matplotlib
matplotlib.use('svg')

from matplotlib import rc
#rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
#rc('text', usetex=True)

import matplotlib.pyplot as plt
plt.rcParams['svg.fonttype'] = 'none'

import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...
import scipy.stats
import config

import itertools
import galsim

import measfcts
import os
import glob

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


import f2n


cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, "figstamps", "groupmeascat.pkl"))

fitspaths = glob.glob(os.path.join(config.simdir, "figstamps", "*", "*.fits"))
assert len(fitspaths) == 1

fitspath = fitspaths[0]

print(fitspath)

#exit()


image_array = f2n.read_fits(fitspath)

cat["textx"] = cat["x"] - 12
cat["texty"] = cat["y"] - 9


import matplotlib.colors

print(cat["x", "y", "tru_mag", "snr"])


sf = f2n.SimpleFigure(image_array, z1=-5, z2=40, scale=3, withframe=False)
sf.draw() # norm=matplotlib.colors.LogNorm(vmin=-3, vmax=20))
sf.annotate(cat, x="textx", y="texty", text="S/N = {row[snr]:.1f}", color="white", fontsize=14) # Futher kwargs are passed to matplotib Text
#sf.show()
sf.save_to_file(os.path.join(config.workdir, "stamps.svg"))
