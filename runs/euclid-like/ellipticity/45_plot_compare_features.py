import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker
import astropy.table

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

distribs = [
#os.path.join(config.workdir, "simnoisy", "EuclidLike_Ell", "groupmeascat.pkl"),
#os.path.join(config.workdir, "sim", "Uniform", "groupmeascat.pkl"),
os.path.join(config.workdir, "train_simple", "selfprecat.pkl"),
]

names = ["GEMS", "Uniform", "Fiducial"]

colors = ["#8080FE", "green", "red"]

outdir = os.path.join(config.workdir, "plots")

#------------------------------------------------------------

megalut.plot.figures.set_fancy(14)

fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(21, 6))#, sharex=True, sharey=True)
plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(right=0.92)
plt.subplots_adjust(left=0.11)

#------------------------------------------------------------

for c, name, distrib in zip(colors, names, distribs):
    cat = megalut.tools.io.readpickle(distrib)
    
    megalut.tools.table.addstats(cat, "snr")
    cat["adamom_frac"] = np.sum(cat["adamom_g1"].mask, axis=1)/float(cat["adamom_g1"].shape[1])
    
    s = megalut.tools.table.Selector("ok", [
    ("min", "snr_mean", 10),
    ("in", "tru_rad", 0.1, 2.),
    ("max", "adamom_frac", 0.01)
    ]
    )

    cat = s.select(cat)

    cat2 = astropy.table.Table()

    print len(cat)
    
    bins = np.arange(20, 24.25, 0.5)
    midbins = (bins[:-1] + bins[1:])/2
    counts, bins = np.histogram(cat["tru_mag"], bins=bins)
    density = np.asarray(counts, np.float) / 796. / 10.
    
    #------------------------------------------------------------ 
    
    weights = np.ones_like(cat['tru_g'])/float(len(cat['tru_g']))
    megalut.plot.hist.hist(ax1, 
        cat, 
        Feature("tru_g", nicename="Ellipticity"),
        bins=20, weights=weights, color=c, label=name
    )
    ax1.legend(loc=1)
    
    #------------------------------------------------------------
    print np.amin(cat['adamom_flux'])
    print np.amax(cat['adamom_flux'])
    bins = np.logspace(2, 5.5, 21)
    cat2["adamom_flux"] = np.ravel(cat["adamom_flux"])
    weights = np.ones_like(cat2['adamom_flux'])/float(len(cat2['adamom_flux']))
    megalut.plot.hist.hist(ax2, 
        cat2, 
        Feature("adamom_flux", nicename="Flux [counts]"),
        bins=bins, weights=np.ravel(weights), color=c
    )
    ax2.set_xscale('log', nonposy='clip')
    ax1.xaxis.set_ticks(np.arange(-1,1.1, 0.5))
    
    #------------------------------------------------------------
    
    cat2["rhl"] = np.ravel(cat["adamom_sigma"] * 1.177)
    weights = np.ones_like(cat2['rhl'])/float(len(cat2['rhl']))
    megalut.plot.hist.hist(ax3, 
        cat2, 
        Feature("rhl", nicename="Half light radius [pixels]"),
        bins=20, weights=weights.flatten(), color=c
    )
    
    #------------------------------------------------------------
    
    
    cat2["adamom_rho4"] = np.ravel(cat["adamom_rho4"])
    weights = np.ones_like(cat2['adamom_rho4'])/float(len(cat2['adamom_rho4']))
    megalut.plot.hist.hist(ax4, 
        cat2, 
        Feature("adamom_rho4", nicename="Concentration [UNIT?]"),
        bins=20, weights=weights, color=c
    )
    
    #------------------------------------------------------------

megalut.plot.figures.savefig(os.path.join(outdir, "compare_features"), fig, fancy=True, pdf_transparence=True)

plt.show()
