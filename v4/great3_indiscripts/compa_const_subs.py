import numpy as np
import matplotlib.pyplot as plt


ref = np.loadtxt("../submissions/GREAT3ExampleScript_RGC_Malte_2014-01-31.txt")

megalut = np.loadtxt("../submissions/out-real_galaxy-ground-constant-v3_mes_gs_29minf50.txt")

print ref.shape, megalut.shape


print np.alltrue(ref[:,0] == megalut[:,0])

plt.subplot("211")
plt.scatter(ref[:,1], megalut[:,1], lw=0, s = 4)
for i in range(200):
	plt.text(ref[i,1]+0.001, megalut[i,1], str(int(ref[i,0])), fontsize=7)
plt.plot([-1, 1], [-1, 1], color="black")
plt.xlabel("g1 ref")
plt.ylabel("g1 megalut")
plt.xlim([-0.07, 0.07])
plt.ylim([-0.07, 0.07])

plt.subplot("212")
plt.scatter(ref[:,2], megalut[:,2], lw=0, s = 4)
for i in range(200):
	plt.text(ref[i,2]+0.001, megalut[i,2], str(int(ref[i,0])), fontsize=7)
plt.plot([-1, 1], [-1, 1], color="black")
plt.xlabel("g2 ref")
plt.ylabel("g2 megalut")
plt.xlim([-0.07, 0.07])
plt.ylim([-0.07, 0.07])


plt.show()
