"""
Standalone demo illustrating the use of the ACF technique.
"""
import logging

from megalut.meas.acf import run
import megalut.sim

import pylab as plt
import numpy as np

logging.basicConfig(level=logging.INFO)

# First Create an image with a catalog (See draw_and_measure_sims.py for more info.).
class MySimParams(megalut.sim.params.Params):
    def get_flux(self):
        return 300
    
mysimparams = MySimParams()
# We make a catalog of 100 x 100 simulated galaxies :
simcat = megalut.sim.stampgrid.drawcat(mysimparams, n=20, stampsize=32)
# Now, we pass this catalog to drawimg, to generate the actual simulated images.
megalut.sim.stampgrid.drawimg(simcat, 
    simgalimgfilepath="simgalimg.fits",
    simtrugalimgfilepath="simtrugalimg.fits",
    simpsfimgfilepath="simpsfimg.fits"
    )

# Running the measurements
out=run("simgalimg.fits",simcat)

# Just plotting the raw results
plt.figure()
plt.plot(out["mes_acf_g1"],out["mes_acf_g2"],'.')
for i in range(2):        
    plt.subplot(1,2,i+1)
    plt.plot(simcat["tru_g%d" % (i+1)], out["mes_acf_g%d" % (i+1)], '+g', label='ACF')
    plt.plot(simcat["tru_g%d" % (i+1)], simcat["tru_g%d" % (i+1)], '.r', lw=2, label='True')
    plt.grid()
    plt.xlabel('g%d_tru' % (i+1))
    plt.ylabel('g%d_mes - g%d_tru' % (i+1,i+1))
    legend=plt.legend(loc='best')
plt.show()

print out