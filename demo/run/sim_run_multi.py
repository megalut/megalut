import megalut
import megalut.sim

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)




	
params = megalut.sim.params.Params("test1")


drawcatkwargs = {}
drawimgkwargs = {}

megalut.sim.run.multi(params, drawcatkwargs, drawimgkwargs)




