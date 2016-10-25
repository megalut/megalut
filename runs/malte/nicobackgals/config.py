


import megalut
import megalut.learn
import os
import numpy as np

import logging

#logging.basicConfig(level=logging.INFO)
logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)




workdir = "/vol/fohlen11/fohlen11_1/mtewes/backgals-megalut/"


obsdir = os.path.join(workdir, "obs_Nicolas")
#obsdir = "/vol/euclid1/euclid1_raid1/nmartinet/CLUSTERING/condor/simulations"


obsworkdir = os.path.join(workdir, "obswork_Nicolas")

simdir = os.path.join(workdir, "sim")


psfimgpath = os.path.join(workdir, "psf.fits")
psfcatpath = os.path.join(workdir, "psfcat.pkl")


ncpu = 10


# Nicolas sims

stampsize = 60
nside = 100


