import numpy as np



subsampling = 100 # pixels per unit
sigma = 3
gridsize = 60 # 10 sigma in each direction 


size = gridsize * subsampling

# Prepare a coordinate grid
X, Y = np.mgrid[0:size, 0:size]+0.5 # So that the arrays contain the coordinates of the pixel *centers*: first pixel goes from 0.0 to 1.0

assert X.shape == (size, size)

center = size / 2.0



#print X

# Draw the Gaussian, centered on the grid


R = np.hypot(X-center, Y-center) / float(subsampling)
Z = (1.0/(2.0*np.pi*(sigma**2))) * np.exp( (-1.0 * (R**2)) / (2.0*(sigma**2)))

dxdy = 1.0/(subsampling**2)

print "Full integral of Profile:", np.sum(Z * dxdy)

print "Integrals in diffeerent fractions of sigma"
for f in np.linspace(1.175, 1.18, 100):
	
	print f, np.sum(Z[R <= f*sigma] * dxdy)
