import galsim


gal = galsim.Gaussian(flux=10.0, sigma=1.0)


gal.shear(g1=0.1, g2=0.2)

gal.shear(g1=0.1, g2=0.2)

print gal
