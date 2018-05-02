import megalut
import os
import config
import numpy as np

from megalut.tools.feature import Feature

import matplotlib
import matplotlib.pyplot as plt

#megalut.plot.figures.set_fancy(14)
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)


cat = megalut.tools.io.readpickle(os.path.join(config.workdir, "cat.pkl"))

print megalut.tools.table.info(cat)


fig = plt.figure(figsize=(4, 4))
plt.subplots_adjust(
	left  = 0.15,  # the left side of the subplots of the figure
	right = 0.95,    # the right side of the subplots of the figure
	bottom = 0.15,   # the bottom of the subplots of the figure
	top = 0.98,      # the top of the subplots of the figure
	wspace = 0.1,   # the amount of width reserved for blank space between subplots,
	                # expressed as a fraction of the average axis width
	hspace = 0.25,   # the amount of height reserved for white space between subplots,
					# expressed as a fraction of the average axis heightbottom=0.1, right=0.8, top=0.9)
	)


tru_rad = Feature("tru_rad", -1, 13, nicename="Half-light radius [VIS pix]")
tru_mag = Feature("tru_mag", 20, 25.5, nicename="Magnitude")
tru_sersicn = Feature("tru_sersicn", 0, 6.5, nicename=r"${\textrm{S\'ersic}$ index")


ax = fig.add_subplot(1, 1, 1)
megalut.plot.scatter.scatter(ax, cat, tru_mag, tru_rad, sidehists=True, sidehistkwargs={"bins":55}, rasterized=True, ms=2)


megalut.plot.figures.savefig(os.path.join(config.valdir, "sourcecat1"), fig, fancy=True, pdf_transparence=True, nocrop=True)

#plt.tight_layout()
plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.


