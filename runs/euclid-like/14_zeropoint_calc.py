import os
import shutil

import megalut.sim
import megalut.meas
import measfcts
import simparams

import includes
import numpy as np
import pylab as plt 
import logging
logger = logging.getLogger(__name__)

simdir = includes.zpsimdir

goal = 10. / np.sqrt(3.)

print '1 observation would yield S/N=', goal

#res45 = megalut.tools.io.readpickle(os.path.join(includes.workdir, "zeropoint_meas_4.5.pkl"))
res42_2hlr = megalut.tools.io.readpickle(os.path.join(includes.workdir, "zeropoint_meas_4.2.pkl"))
res42_3hlr = megalut.tools.io.readpickle(os.path.join(includes.workdir, "zeropoint_meas_4.2x3.pkl"))
res45_3hlr = megalut.tools.io.readpickle(os.path.join(includes.workdir, "zeropoint_meas.pkl"))

plt.figure()
plt.errorbar(res42_2hlr[:,0], res42_2hlr[:,1], yerr=res42_2hlr[:,2], label=r"$RON=4.2,r=2r_h,mag=24.5$")
plt.errorbar(res42_3hlr[:,0], res42_3hlr[:,1], yerr=res42_3hlr[:,2], label=r"$RON=4.2,r=3r_h,mag=24.5$")
plt.errorbar(res45_3hlr[:,0], res45_3hlr[:,1], yerr=res45_3hlr[:,2], label=r"$RON=4.5,r=3r_h,mag=24.9$")
plt.axhline(10., c='k')
plt.axhline(goal, c='k')
plt.xlabel("AB magnitude")
plt.ylabel("S/N")
plt.legend(loc="best")
plt.show()
