
import os
import megalut
import config
import matplotlib.pyplot as plt
from megalut.tools.feature import Feature



import astropy.table
import numpy as np
import galsim




gemspath = os.path.join(config.gemsdir, "gems_20090807.fits")
catpath = os.path.join(config.workdir, "cat.pkl")


cat = astropy.table.Table.read(gemspath)
#print cat.colnames


cat.keep_columns(['ST_FLUX_RADIUS', 'ST_N_GALFIT', 'ST_MAG_GALFIT', 'ST_RE_GALFIT', 'ST_Q_GALFIT', "GEMS_FLAG", 'ST_MAG_BEST'])

cat["magdiff"] = np.fabs(cat["ST_MAG_BEST"] - cat["ST_MAG_GALFIT"])

# We select galaxies
s = megalut.tools.table.Selector("select", [
		("is", "GEMS_FLAG", 4),
		("max", "magdiff", 0.5),
		("in", "ST_MAG_GALFIT", 20.5, 26.0),
		("in", "ST_N_GALFIT", 0.3, 6.0),
		("in", "ST_RE_GALFIT", 0.0 / (0.03 / 0.1), 10.0 / (0.03 / 0.1)),
	])

cat = s.select(cat)


cat["tru_rad"] = (0.03 / 0.1) * cat["ST_RE_GALFIT"] # GEMS is 0.03 arcsec per pixel, and we want VIS pixels of 0.1 arcsec
cat["tru_mag"] = cat["ST_MAG_GALFIT"]
cat["tru_sersicn"] = cat["ST_N_GALFIT"]

# We reject any nans in the field that we want
s = megalut.tools.table.Selector("nonan", [
		("nomask", "tru_rad"),
		("nomask", "tru_mag"),
		("nomask", "tru_sersicn"),
	])
cat = s.select(cat)


fig = plt.figure(figsize=(20, 10))


maggal = Feature("ST_MAG_GALFIT")
magsex = Feature("ST_MAG_BEST")

sersicn = Feature("ST_N_GALFIT")
radsex = Feature("ST_FLUX_RADIUS")
radgal = Feature("ST_RE_GALFIT")


tru_mag = Feature("tru_mag", nicename="VIS magnitude")
tru_rad = Feature("tru_rad", nicename="Half-light radius [VIS pix]")
tru_sersicn = Feature("tru_sersicn", nicename="Sersic index")



ax = fig.add_subplot(2, 4, 1)
megalut.plot.scatter.scatter(ax, cat, magsex,  maggal, radsex, sidehists=True)

ax = fig.add_subplot(2, 4, 2)
megalut.plot.scatter.scatter(ax, cat, radsex,  radgal, maggal)

ax = fig.add_subplot(2, 4, 3)
megalut.plot.scatter.scatter(ax, cat, maggal,  radgal, sidehists=True)

ax = fig.add_subplot(2, 4, 4)
magbinlims = np.arange(20.0, 26.1, 0.5)
magbincents = 0.5*(magbinlims[:-1] + magbinlims[1:])
magcounts, bla = np.histogram(cat["tru_mag"], bins=magbinlims)
ax.plot(magbincents, magcounts, label="GEMS")
ax.set_yscale("log")
for magbinlim in magbinlims:
	ax.axvline(magbinlim, color="gray", lw=0.5)
ax.legend()



ax = fig.add_subplot(2, 4, 5)
megalut.plot.hist.hist(ax, cat, tru_sersicn)

ax = fig.add_subplot(2, 4, 6)
megalut.plot.scatter.scatter(ax, cat, tru_mag, tru_rad, tru_sersicn)

ax = fig.add_subplot(2, 4, 7)
megalut.plot.scatter.scatter(ax, cat, tru_mag, tru_rad, sidehists=True)


plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.

megalut.tools.io.writepickle(cat, catpath)



