import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt



cat = megalut.tools.io.readpickle(os.path.join(config.simmeasdir, config.datasets["si"], "groupmeascat.pkl"))

#print megalut.tools.table.info(cat)


fig = plt.figure(figsize=(20, 13))


snr = Feature("snr", 0, 50, nicename="Measured S/N")
tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
tru_mag = Feature("tru_mag", 20, 25, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 7, nicename="True Sersic index")

#snr = Feature("snr", nicename="Measured S/N")
#tru_rad = Feature("tru_rad", nicename="True half-light radius [pixel]")
#tru_mag = Feature("tru_mag", nicename="Magnitude")
#tru_sersicn = Feature("tru_sersicn", nicename="True Sersic index")


ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, tru_sersicn, tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, sidehists=True, sidehistkwargs={"bins":20})
ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, tru_mag,  tru_rad, snr)


ax = fig.add_subplot(2, 3, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1"), Feature("tru_e1"), Feature("tru_e2"))
ax.grid()
ax = fig.add_subplot(2, 3, 5)
megalut.plot.scatter.scatter(ax, cat, snr, tru_mag)
ax.grid()
ax = fig.add_subplot(2, 3, 6)
megalut.plot.hist.hist(ax, cat, snr)




plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


