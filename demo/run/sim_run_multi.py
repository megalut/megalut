import megalut
import megalut.sim

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)




params = megalut.sim.params.Params("test1")

drawcatkwargs = {"n":100, "stampsize":64}
drawimgkwargs = {}

#simdir = "/vol/fohlen11/fohlen11_1/mtewes/foo"
simdir = "foo"

megalut.sim.run.multi(params, drawcatkwargs, drawimgkwargs, simdir=simdir, ncpu=4)


