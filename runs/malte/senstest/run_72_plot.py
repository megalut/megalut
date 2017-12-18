"""
Runs the "wrong" trainings on the sensitivity test data and writes the output files

"""
import megalut.tools
import megalut.learn
import megalut
import astropy

import config
import numpy as np
import os
import glob

import matplotlib.pyplot as plt

from megalut.tools.feature import Feature

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)

####### config

#setname = "e_mine6_v4"
#setname = "p_dbshear_v4"
setname = "s_v4"

#######
varcode = setname[0:1] + "code"



resdir = os.path.join(config.workdir, "megalut", "res")

biaspaths = sorted(glob.glob(os.path.join(resdir, setname, "bias_measurements_MegaLUT_*.fits")))

values = {"m2":-0.2, "m1":-0.1, "p0":0.0, "p1":0.1, "p2":0.2}


fig = plt.figure(figsize=(8, 6))


txt = "Blabla"
if varcode == "scode":
	txt = "Sky Level"
elif varcode == "pcode":
	txt = "PSF Size"
elif varcode == "ecode":
	txt = r"$P(e)$"


plt.figtext(0.5, 0.93, txt, fontsize=20, ha="center")


#ax1 = fig.add_subplot(2, 2, 1)
#ax2 = fig.add_subplot(2, 2, 2)
#ax3 = fig.add_subplot(2, 2, 3)
#ax4 = fig.add_subplot(2, 2, 4)

h = 0.36
w = 0.33

ax1 = plt.axes([.14, .52, w, h])
ax2 = plt.axes([.63, .52, w, h])
ax3 = plt.axes([.14, .1, w, h])
ax4 = plt.axes([.63, .1, w, h])


for ax in [ax1, ax2, ax3, ax4]:
	ax.axhline(0.0, color="gray", alpha=0.5)
	ax.axvline(0.0, color="gray", alpha=0.5)


for biaspath in biaspaths:

	pcode = biaspath[-16:-13]
	scode = biaspath[-12:-9]
	ecode = biaspath[-8:-5]
	
	codeval = values[eval(varcode)[1:]]
	
	print biaspath
	print pcode, scode, ecode
	t = astropy.table.Table.read(biaspath)
	#print t

	
	ax1.errorbar(codeval, t["m"][1], yerr=t["m_err"][1], fmt='o', color="black")
	ax1.set_ylabel("$\mu_1$", fontsize=18)
	#ax1.set_xlabel("relative offset")

	ax2.errorbar(codeval, t["m"][2], yerr=t["m_err"][2], fmt='o', color="black")
	ax2.set_ylabel("$\mu_2$", fontsize=18)
	#ax2.set_xlabel("relative offset")

	ax3.errorbar(codeval, t["c"][1], yerr=t["c_err"][1], fmt='o', color="black")
	ax3.set_ylabel("$c_1$", fontsize=18)
	ax3.set_xlabel("Relative offset")

	ax4.errorbar(codeval, t["c"][2], yerr=t["c_err"][2], fmt='o', color="black")
	ax4.set_ylabel("$c_2$", fontsize=18)
	ax4.set_xlabel("Relative offset")



for ax in [ax1, ax2, ax3, ax4]:
	ax.set_xlim(-0.25, 0.25)


ax1.set_ylim(-0.2, 0.2)
ax2.set_ylim(-0.2, 0.2)
ax3.set_ylim(-0.002, 0.02)
ax4.set_ylim(-0.002, 0.02)


#plt.tight_layout()

#plt.show()
plt.savefig("{}.pdf".format(setname))
