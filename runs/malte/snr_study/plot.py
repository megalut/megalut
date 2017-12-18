#import matplotlib
#matplotlib.use("AGG")

import os
import megalut
import megalut.plot
import numpy as np
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt



#### Parameters ###################

genworkdir = "/vol/fohlen11/fohlen11_1/mtewes/snr_study/"

name = "v1"

####################################


workdir = os.path.join(genworkdir, name)
catpath = os.path.join(workdir, "cat.pkl")

cat = megalut.tools.io.readpickle(catpath)


tru_flux = Feature("tru_flux", 0, 55000)
tru_cropper_snr = Feature("tru_cropper_snr")
gain1_snr_mean = Feature("gain1_snr_mean")
gain1_aper3hlr_snr_mean = Feature("gain1_aper3hlr_snr_mean")
sex_snr_iso_mean = Feature("sex_snr_iso_mean")
sex_snr_auto_mean = Feature("sex_snr_auto_mean", 0, 90)

fig = plt.figure(figsize=(8, 8))

ax = fig.add_subplot(1, 1, 1)
megalut.plot.scatter.scatter(ax, cat, tru_flux, tru_cropper_snr, sidehists=False, color="black", ls="-", alpha=1, lw=2, label="True SNR Copper 2016")
megalut.plot.scatter.scatter(ax, cat, tru_flux, gain1_snr_mean, sidehists=False, color="red", ls="-", alpha=1, lw=2, label="Measured SNR within 2 HLR")
megalut.plot.scatter.scatter(ax, cat, tru_flux, gain1_aper3hlr_snr_mean, sidehists=False, color="blue", ls="-", alpha=1, lw=2, label="Measured SNR within 3 HLR")
megalut.plot.scatter.scatter(ax, cat, tru_flux, sex_snr_iso_mean, sidehists=False, color="green", ls="-", alpha=1, lw=2, label="FLUX_ISO / FLUXERR_ISO")
megalut.plot.scatter.scatter(ax, cat, tru_flux, sex_snr_auto_mean, sidehists=False, color="purple", ls="-", alpha=1, lw=2, label="FLUX_AUTO / FLUXERR_AUTO")

plt.ylabel("SNR")

plt.legend()
plt.tight_layout()

plt.show()
