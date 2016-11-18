import os
import megalut.sim as sim
import megalut.meas as meas
import megalut.tools as tools

import config
import mysimparams
import g3measfct as measfct

import megalutgreat3 as mg3

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)

# Loading the correct configuration!
great3 = config.load_run()


subfield = 6
cat = tools.io.readpickle(great3.get_path("obs", "img_%i_meascat.pkl" % subfield))



print tools.table.info(cat)
