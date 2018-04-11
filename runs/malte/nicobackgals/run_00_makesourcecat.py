
import os
import megalut
import config
import matplotlib.pyplot as plt
from megalut.tools.feature import Feature

import astropy.table
import numpy as np
import galsim

"""
Voila les donnees pour le training ! En attache un catalog de 10000 galaxies avec les colonnes suivantes :

X,Y,X,Y,mag,sersic index,half-light radius (arcsec), flux, e1, e2,0,0,0,X,Y

Il y a pas mal de colonnes inutiles qui sont la pour avoir le meme format avec le catalogue de galaxies faibles.
Tu peux utiliser les colonnes 1,2 pour le X,Y si tu veux faire une grille.
Attention les positions sont centrees sur le pixel dans le catalogue (le shift subpixel est ajoute apres).



"""

nico_cat_path = os.path.join(config.workdir, "bright_cat.cat")
catpath = os.path.join(config.workdir, "cat.pkl")


data = np.loadtxt(nico_cat_path)

#nico_cat = astropy.table.Table.read(nico_cat_path, format="ascii.tab")

pixel_size = 0.1 # arcsec / pixel
t_exp = 3*565.0 # s
gain = 3.1 # e-/ADU
readoutnoise = 4.2 # e-
sky_bkg = 22.35 # mag/arcsec2

#ZP = 37.46 # mag, but with a different definition of what a ZP is.
#ZP = 24.6 # mag
#ZP = 29.44 # mag
ZP = 24.14

cat = astropy.table.Table()

cat["tru_mag"] = data[:,4]
cat["tru_sersicn"] = data[:,5]
cat["tru_rad"] = data[:,6] / pixel_size # in pixel


#cat["tru_flux"] = data[:,7] * (t_exp/gain) # in ADU
# No, do not use "flux", but compute it from mag, given the above zeropoint

cat["tru_flux"] =  t_exp * 10**(-0.4 * (cat["tru_mag"] - ZP)) / gain # ADU
F_sky = (pixel_size**2) * t_exp * 10**(-0.4 * (sky_bkg - ZP)) # electrons

cat.meta["noise_sigma"] = np.sqrt(  F_sky +  readoutnoise**2  ) / gain # ADU, stationary for each pixel

# And now, we convert both tru_flux and noise_sigma from ADU to electrons / second, as we want the generated images to be in these units.
#cat.meta["noise_sigma"] = cat.meta["noise_sigma"] * (gain / t_exp) 
#cat["tru_flux"] = cat["tru_flux"] * (gain / t_exp) 
# No, we no longer want this!


print("Noise sigma is")
print(cat.meta["noise_sigma"])


#cat["tru_e1"] = data[:,8]
#cat["tru_e2"] = data[:,9]

#cat["tru_g1"] = np.ones(len(cat))
#cat["tru_g2"] = np.ones(len(cat))

#for row in cat:
	
#	shear = galsim.Shear(e1=row["tru_e1"], e2=row["tru_e2"])
#	row["tru_g1"] = shear.g1
#	row["tru_g2"] = shear.g2

#print cat["tru_flux", "tru_mag"]


megalut.tools.io.writepickle(cat, catpath)

"""
fig = plt.figure()
ax = plt.subplot(1, 1, 1)

megalut.plot.scatter.scatter(ax, cat, Feature("tru_g1"), Feature("tru_e1"), Feature("tru_e2"))


plt.show()
"""
