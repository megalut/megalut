#import matplotlib
#matplotlib.use("AGG")

import megalut
import megalut.tools
import megalut.plot
from megalut.tools.feature import Feature

import megalutgreat3
import astropy


import config
import numpy as np
import os
import matplotlib.pyplot as plt


import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

catpath = config.great3.path("pred", "summary_cat.pkl")
cat = megalut.tools.io.readpickle(catpath)

cat["pre_g1_res"] = cat["pre_g1"] - cat["tru_g1"]
cat["pre_g2_res"] = cat["pre_g2"] - cat["tru_g2"]

print megalut.tools.table.info(cat)



def labeloutliers(ax, cat, pre, tru):
	cat["offset"] = cat[pre] - cat[tru]
	for row in cat:
		if np.fabs(row["offset"]) > 0.01:
			#print row[tru], row[pre], str(row["subfield"])
			ax.text(row[tru], row[pre] - row[tru], str(row["subfield"]))
	
	

sr = 0.07
srp = 0.15
fig = plt.figure(figsize=(12, 10))


ax = fig.add_subplot(2, 2, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1", -sr, sr), Feature("pre_g1_res", -srp, srp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_g1", "tru_g1")

ax = fig.add_subplot(2, 2, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g2", -sr, sr), Feature("pre_g2_res", -srp, srp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_g2", "tru_g2")


ax = fig.add_subplot(2, 2, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1", -sr, sr), Feature("pre_g1_res", -srp, srp), Feature("psf_adamom_g1"), yisres=True, showidline=True, idlinekwargs={"color":"black"})

ax = fig.add_subplot(2, 2, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_g2", -sr, sr), Feature("pre_g2_res", -srp, srp), Feature("psf_adamom_g2"), yisres=True, showidline=True, idlinekwargs={"color":"black"})



plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.
