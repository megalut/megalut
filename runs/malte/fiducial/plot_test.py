
import megalut
import os

from megalut.tools.feature import Feature
import config

import matplotlib
import matplotlib.pyplot as plt

import numpy as np


cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["vo"], "groupmeascat.pkl"))


mask = np.array(cat["adamom_g1"].mask, dtype=bool) # This is 2D, 1 means "is masked"

print mask.shape
print np.sum(mask)

print float(np.sum(mask)) / float(mask.size)


exit()


nrea = mask.shape[1]

tru_flux = np.array([cat["tru_flux"] for i in range(nrea)]).transpose()
high_flux = tru_flux > 500.0

mask = np.logical_and(mask, high_flux)


fail_tru_g1s = cat["tru_g1"][mask]
fail_tru_g2s = cat["tru_g2"][mask]

#fail_tru_s1s = cat["tru_s1"][cat["adamom_g1"].mask]
#fail_tru_s2s = cat["tru_s2"][cat["adamom_g1"].mask]


fail_tru_ixs = cat["ix"][mask]

tru_iys = np.array([cat["iy"] for i in range(nrea)]).transpose()
fail_tru_iys = tru_iys[mask]

tru_flux = np.array([cat["tru_flux"] for i in range(nrea)]).transpose()
tru_rad = np.array([cat["tru_rad"] for i in range(nrea)]).transpose()
fail_tru_flux = tru_flux[mask]


fail_tru_rad = tru_rad[mask]


#print megalut.tools.table.info(cat)

#exit()

"""
plt.scatter(fail_tru_ixs, fail_tru_g1s, c=fail_tru_flux)
plt.colorbar()
plt.show()
"""

plt.scatter(fail_tru_g1s, fail_tru_g2s, c=fail_tru_rad)
plt.title("adamom failures for bright sources (color=rad)")
plt.xlabel("g1")
plt.ylabel("g2")
plt.colorbar()
plt.show()


