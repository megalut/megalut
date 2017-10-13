import config
import measfcts
import os
import numpy as np
import matplotlib.ticker as ticker

import megalut.plot
from megalut.tools.feature import Feature
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)

distribs = [
os.path.join(config.workdir, "simnoisy", "EuclidLike_Ell", "groupmeascat.pkl"),
os.path.join(config.workdir, "sim", "Uniform", "groupmeascat.pkl"),
]

names = ["GEMS", "Uniform", "Fiducial"]

colors = ["#8080FE", "green", "red"]

outdir = os.path.join(config.workdir, "plots")

#------------------------------------------------------------

megalut.plot.figures.set_fancy(14)

fig, (ax1, ax2) = plt.subplots(1, 2)#, sharex=True, sharey=True)
plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(right=0.92)
plt.subplots_adjust(left=0.11)

#------------------------------------------------------------

for c, name, distrib in zip(colors, names, distribs):
    cat = megalut.tools.io.readpickle(distrib)
    
    s = megalut.tools.table.Selector("ok", [
    #("min", "snr_mean", 10),
    ("in", "tru_rad", 0.1, 2.),
    #("max", "adamom_frac", 0.01)
    ]
    )

    cat = s.select(cat)

    print len(cat)
    
    bins = np.arange(20, 24.25, 0.5)
    midbins = (bins[:-1] + bins[1:])/2
    counts, bins = np.histogram(cat["tru_mag"], bins=bins)
    density = np.asarray(counts, np.float) / 796. / 10.
    
    #------------------------------------------------------------ 
    
    ax1.plot(midbins, density, label=name, lw=2, c=c)
    ax1.set_yscale('log', nonposy='clip')
    ax1.set_xlim([19.75, 24.25])
    ax1.set_ylim([0.025, 5])
    ax1.set_xlabel("AB magnitude")
    ax1.set_ylabel(r"$N_\mathrm{gal}$ [per arcmin$^2$ per 0.5 mag]")
    ax1.legend(loc=4)
    ax1.grid(True)
    
    #------------------------------------------------------------
    
    print distrib 
    
    weights = np.ones_like(cat['tru_rad'])/float(len(cat['tru_rad']))
    megalut.plot.hist.hist(ax2, 
        cat, 
        Feature("tru_rad", nicename="Half light radius [arcsecond]"),
        bins=10, weights=weights, color=c
    )
    #(ax, simcat, obscat, featx, featy, sidehists, sidehistkwargs, title, legend, plotpoints)
    #ax2.plot(midbins, density)
    #ax1.set_yscale('log', nonposy='clip')
    #ax1.set_xlim([19.75, 24.25])
    #ax1.set_ylim([0.01, 5])
    #ax1.set_xlabel("AB magnitude")
    #ax1.set_ylabel(r"$N_\mathrm{gal}$ [per arcmin$^2$ per 0.5 mag]")
    
    #------------------------------------------------------------
    

    #(ax, simcat, obscat, featx, featy, sidehists, sidehistkwargs, title, legend, plotpoints)
    #ax2.plot(midbins, density)
    #ax1.set_yscale('log', nonposy='clip')
    #ax1.set_xlim([19.75, 24.25])
    #ax1.set_ylim([0.01, 5])
    #ax1.set_xlabel("AB magnitude")
    #ax1.set_ylabel(r"$N_\mathrm{gal}$ [per arcmin$^2$ per 0.5 mag]")
    
    #------------------------------------------------------------

megalut.plot.figures.savefig(os.path.join(outdir, "compare_indir"), fig, fancy=True, pdf_transparence=True)

plt.show()
