""" This module contains an example how to use bitstring
library.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from bitstring import BitArray

def main():
    """ This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)
    
    a = BitArray(bin='00101')
    b = BitArray(bin='10101')
    
    logger.debug(a)
    logger.debug(b)
    return

# this means that if this script is executed, then 
# main() will be executed
if __name__ == "__main__":
    main()
