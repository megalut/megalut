import os
import logging

logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)

workdir = "./shear"

stampsize = 48

ncpu = 8

simdir = os.path.join(workdir, "sim")
simwdir = os.path.join(workdir, "simweights")
simvaldir = os.path.join(workdir, "simval")
psfimgpath = os.path.join(workdir, "psf.fits")
psfcatpath = os.path.join(workdir, "psfcat.pkl")