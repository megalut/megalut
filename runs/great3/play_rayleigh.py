import numpy as np

import matplotlib.pyplot as plt

def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))

def trun_rayleigh(sigma, max_val):
	"""
	A truncated Rayleigh distribution
	"""
	assert max_val > sigma
	tmp = max_val + 1.0
	while tmp > max_val:
		tmp = np.random.rayleigh(sigma)
	return tmp


n = 500000
sigma = 0.2
bins = 100

rs = [np.random.rayleigh(sigma) for i in range(n)]
crs = [contracted_rayleigh(sigma, 0.7, 4) for i in range(n)]
trs = [trun_rayleigh(sigma, 0.7) for i in range(n)]


plt.hist(rs, label="Rayleigh", range=(0, 1.0), alpha=0.5, bins=bins)
plt.hist(crs, label="Contracted Rayleigh", range=(0, 1.0), alpha=0.5, bins=bins)
plt.hist(trs, label="Truncated Rayleigh", range=(0, 1.0), alpha=0.5, bins=bins)

plt.legend()
plt.show()
