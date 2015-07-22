import tenbilac
import os

import logging
#logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)

workdir = "/vol/fohlen11/fohlen11_1/mtewes/Euclid/sbe/benchmark_low_SN_workdir/ml/"

net = "ML_Tenbilac_g1_test7fast5"
#net = "ML_Tenbilac_g1_test20"

filepath = os.path.join(workdir, net, "Tenbilac.pkl")

train = tenbilac.utils.readpickle(filepath)

#train.net.setidentity()


tenbilac.plot.paramscurve(train)

#tenbilac.plot.outdistribs(train)

#tenbilac.plot.errors(train)
