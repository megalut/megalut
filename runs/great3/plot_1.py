"""

Classic simobscompa plot

"""

import megalut
import megalutgreat3
import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import config

import os
import logging
logging.basicConfig(format=config.loggerformat, level=logging.INFO)


run = config.load_run()


"""
simcat = megalut.tools.io.readpickle(os.path.join(run.measdir, run.simparams.name, "groupmeascat_cases.pkl"))
print megalut.tools.table.info(simcat)
#print simcat
"""

I AM HERE, IDEA : use only sharpest PSF for these plots

obscat = 



exit()



rea = "full"

adamom_flux = Feature("adamom_flux", rea=rea)
adamom_sigma = Feature("adamom_sigma", 0, 30, rea=rea)
adamom_rho4 = Feature("adamom_rho4", 1.3, 2.6, rea=rea)
adamom_g1 = Feature("adamom_g1", -0.8, 0.8, rea=rea)
adamom_g2 = Feature("adamom_adamom_g2", -0.8, 0.8, rea=rea)

snr = Feature("snr", -5, 50, rea=rea)

aperphot_sb2 = Feature("aperphot_sb2", rea=rea)
aperphot_sb3 = Feature("aperphot_sb3", rea=rea)
aperphot_sb5 = Feature("aperphot_sb5", rea=rea)
aperphot_sb8 = Feature("aperphot_sb8", rea=rea)

skymad = Feature("skymad", rea=rea)
skystd = Feature("skystd", rea=rea)
skymed = Feature("skymed", rea=rea)
skymean = Feature("skymean", rea=rea)

psf_adamom_g1 = Feature("psf_adamom_g1", -0.06, 0.06, rea=rea)
psf_adamom_g2 = Feature("psf_adamom_g1", -0.06, 0.06, rea=rea)
psf_adamom_sigma = Feature("psf_adamom_sigma", rea=rea)



#cat["tru_g"] = np.hypot(cat["tru_g1"], cat["tru_g2"])


fig = plt.figure(figsize=(20, 13))
#fig = plt.figure(figsize=(8, 8))

ax = fig.add_subplot(3, 4, 1)

megalut.plot.hist.hist(ax, simcat, snr, color="red", label="Training")

#ax = fig.add_subplot(3, 4, 2)
#megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1"), Feature("tru_s2"))

plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
#plt.close(fig) # Helps releasing memory when calling in large loops.

