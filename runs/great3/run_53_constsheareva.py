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

catpath = config.great3.path("summary_{}.pkl".format(config.predcode))
cat = megalut.tools.io.readpickle(catpath)

cat["pre_s1_res"] = cat["pre_s1"] - cat["tru_s1"]
cat["pre_s2_res"] = cat["pre_s2"] - cat["tru_s2"]

cat["pre_s1w_res"] = cat["pre_s1w"] - cat["tru_s1"]
cat["pre_s2w_res"] = cat["pre_s2w"] - cat["tru_s2"]


#print megalut.tools.table.info(cat)

mets = megalutgreat3.utils.metrics(cat, ("tru_s1", "tru_s2"), ("pre_s1w", "pre_s2w"), psfgcols=("tru_psf_g1", "tru_psf_g2"))


def labeloutliers(ax, cat, pre, tru, thr=0.01):
	cat["offset"] = cat[pre] - cat[tru]
	for row in cat:
		if np.fabs(row["offset"]) > thr:
			#print row[tru], row[pre], str(row["subfield"])
			ax.text(row[tru], row[pre] - row[tru], str(row["subfield"]))
	
	

sr = 0.07 # shear range
srp = 0.2 # shear range predictions
swrp = 0.02
fig = plt.figure(figsize=(22, 13))


ax = fig.add_subplot(3, 4, 1)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1_res", -srp, srp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s1", "tru_s1")
ax.set_title("Unweighted, wide")
ax = fig.add_subplot(3, 4, 2)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2_res", -srp, srp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s2", "tru_s2")

ax = fig.add_subplot(3, 4, 3)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1_res", -srp, srp), Feature("psf_adamom_g1"), yisres=True, showidline=True, idlinekwargs={"color":"black"})

ax = fig.add_subplot(3, 4, 4)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2_res", -srp, srp), Feature("psf_adamom_g2"), yisres=True, showidline=True, idlinekwargs={"color":"black"})



ax = fig.add_subplot(3, 4, 5)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1_res", -swrp, swrp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
ax.set_title("Unweighted, narrow")
ax = fig.add_subplot(3, 4, 6)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2_res", -swrp, swrp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})

ax = fig.add_subplot(3, 4, 7)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1_res", -swrp, swrp), Feature("psf_adamom_g1"), yisres=True, showidline=True, idlinekwargs={"color":"black"})

ax = fig.add_subplot(3, 4, 8)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2_res", -swrp, swrp), Feature("psf_adamom_g2"), yisres=True, showidline=True, idlinekwargs={"color":"black"})




ax = fig.add_subplot(3, 4, 9)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1w_res", -swrp, swrp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s1w", "tru_s1", thr=0.003)
ax.set_title("Weighted")
ax = fig.add_subplot(3, 4, 10)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2w_res", -swrp, swrp), Feature("psf_adamom_sigma"), yisres=True, metrics=True, showidline=True, idlinekwargs={"color":"black"})
labeloutliers(ax, cat, "pre_s2w", "tru_s2", thr=0.003)

ax = fig.add_subplot(3, 4, 11)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s1", -sr, sr), Feature("pre_s1w_res", -swrp, swrp), Feature("psf_adamom_g1"), yisres=True, showidline=True, idlinekwargs={"color":"black"})

ax = fig.add_subplot(3, 4, 12)
megalut.plot.scatter.scatter(ax, cat, Feature("tru_s2", -sr, sr), Feature("pre_s2w_res", -swrp, swrp), Feature("psf_adamom_g2"), yisres=True, showidline=True, idlinekwargs={"color":"black"})


plt.tight_layout()

#if filepath:
#	plt.savefig(filepath)
#else:

plt.show()
plt.close(fig) # Helps releasing memory when calling in large loops.
