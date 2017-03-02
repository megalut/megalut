"""
Reads and saves the GREAT3Run object.
Can be useful to have this separated to overwrite settings (if you know what you are doing).
"""


import config

import logging
logging.basicConfig(format=config.loggerformat, level=logging.DEBUG)
logger = logging.getLogger(__name__)


# Create and save an instance of the GREAT3Run class
#great3 = config.new_run()
#great3.save_run()


