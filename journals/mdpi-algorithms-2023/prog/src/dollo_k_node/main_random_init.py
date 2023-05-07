"""  The :mod:`ga_node_ilustration_01` module contains an example how to use 
methods from `EaNode` class and functions from module `ea_node_operators`.

"""
import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from dollo_k_node import DolloKNode
from dollo_k_initialization import init_dollo_k_individual

import random


def main():
    """  This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)

    random.seed( 111133 )

    x = init_dollo_k_individual(DolloKNode, ['a','b','c','d','e','f'], 2, 2.5)  
    logger.debug( x.tree_string_rep() )
    
    y = init_dollo_k_individual(DolloKNode, ['a','b','c','d','e','f'], 2, 3.5)  
    logger.debug( y.tree_string_rep() )
    
    z = init_dollo_k_individual(DolloKNode, ['a','b','c','d','e', 'f'], 2, 4.5)  
    logger.debug( z.tree_string_rep() )

    return

# this means that if this script is executed, then 
# main() will be executed
if __name__ == '__main__':
    main()

