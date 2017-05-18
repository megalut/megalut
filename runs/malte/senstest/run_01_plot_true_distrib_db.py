import megalut
import astropy
import config
import glob
import os
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

from megalut.tools.feature import Feature


cat = megalut.tools.io.readpickle(os.path.join(config.truedistdir, "table.pkl"))
print megalut.tools.table.info(cat)

fig = plt.figure(figsize=(16, 10))

ax = fig.add_subplot(2, 3, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("hlr_bulge_arcsec"), Feature("hlr_disk_arcsec"), sidehists=True)
#megalut.plot.scatter.scatter(ax, cat, Feature("rotation"), Feature("hlr_disk_arcsec"), sidehists=True)


ax = fig.add_subplot(2, 3, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("bulge_axis_ratio"), Feature("bulge_ellipticity"), sidehists=True)
#megalut.plot.scatter.scatter(ax, cat, Feature("bulge_fraction"), Feature("disk_height_ratio"), sidehists=True)



ax = fig.add_subplot(2, 3, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("magnitude"), Feature("bulge_fraction"), sidehists=True)

ax = fig.add_subplot(2, 3, 4)
#megalut.plot.scatter.scatter(ax, cat, Feature("hlr_bulge_arcsec"), Feature("hlr_disk_arcsec"), Feature("magnitude"))
megalut.plot.scatter.scatter(ax, cat, Feature("disk_height_ratio"), Feature("bulge_axis_ratio"))

ax = fig.add_subplot(2, 3, 5)
#megalut.plot.scatter.scatter(ax, cat, Feature("rotation"), Feature("bulge_ellipticity"))
megalut.plot.scatter.scatter(ax, cat, Feature("bulge_ellipticity"), Feature("tilt"), Feature("disk_height_ratio"))

ax = fig.add_subplot(2, 3, 6)
#megalut.plot.scatter.scatter(ax, cat, Feature("bulge_ellipticity"), Feature("tilt"), Feature("bulge_axis_ratio"))
megalut.plot.scatter.scatter(ax, cat, Feature("bulge_ellipticity"), Feature("tilt"), Feature("bulge_axis_ratio"))

plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
#plt.close(fig) # Helps releasing memory when calling in large loops.
