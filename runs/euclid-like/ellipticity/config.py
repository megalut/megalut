import os
import logging

logging.basicConfig(format='PID %(process)06d | %(asctime)s | %(levelname)s: %(name)s(%(funcName)s): %(message)s',level=logging.INFO)

workdir = "./ellipticity"

# Euclid-like data
zeropoint = 24.6 # AB mag
pixelscale = 0.1
gain = 3.1 
exposuretime = 3.*565.
skylevel = 22.35 # AB mag/arcsec/arcsec
stampsize = 48
read_noise = 4.2

psfdir = "psf_stamp"

ncpu = 7

zpsimdir = os.path.join(workdir, "zpsim")
dbdir = os.path.join(workdir, "db")
psfimgpath = os.path.join(workdir, "psf.fits")
psfcatpath = os.path.join(workdir, "psfcat.pkl")
