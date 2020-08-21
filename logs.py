###########################################################################
#
#   File Name    Date       Owner                Description
#   ---------   -------    ---------           -----------------------
#
###########################################################################

import logging

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

def info_(prntstr):
    logging.info(prntstr)

def debug_(prntstr):
    logging.debug(prntstr)

