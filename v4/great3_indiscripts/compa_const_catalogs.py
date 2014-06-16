import numpy as np
import matplotlib.pyplot as plt


gfit = np.loadtxt("gfit.txt")

megalut = np.loadtxt("megalut.txt")[:1000,:]

print gfit.shape, megalut.shape


print np.alltrue(gfit[:,0] == megalut[:,0])

plt.subplot("221")
plt.scatter(gfit[:,1], megalut[:,1], lw=0, s = 2)
plt.plot([-1, 1], [-1, 1], color="black")
plt.xlabel("g1 gfit")
plt.ylabel("g1 megalut")
plt.xlim([-1, 1])
plt.ylim([-1, 1])

plt.subplot("222")
plt.scatter(gfit[:,2], megalut[:,2], lw=0, s = 2)
plt.plot([-1, 1], [-1, 1], color="black")
plt.xlabel("g2 gfit")
plt.ylabel("g2 megalut")
plt.xlim([-1, 1])
plt.ylim([-1, 1])

plt.subplot("223")
plt.scatter(gfit[:,1], gfit[:,2], lw=0, s = 2)
plt.xlabel("g1 gfit")
plt.ylabel("g2 gfit")
plt.xlim([-1, 1])
plt.ylim([-1, 1])

plt.subplot("224")
plt.scatter(megalut[:,1], megalut[:,2], lw=0, s = 2)
plt.xlabel("g1 megalut")
plt.ylabel("g2 megalut")
plt.xlim([-1, 1])
plt.ylim([-1, 1])

plt.show()
