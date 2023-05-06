""" This module module contains an example how to use 
methods from EaNode class.

"""

from bitstring import BitArray

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from ea_node import EaNode


def main():
    """ This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)
    # creating GA tree
    root = EaNode('--', BitArray(bin = '0110000001100000'))
    my1 = EaNode('A+', BitArray(bin = '0111000001100000'), parent=root)
    my2 = EaNode('B+', BitArray(bin='0110100001100000'), parent=root)
    # printing GA tree
    logger.debug( root.tree_string_rep() )
    # rearanginig nodes
    my2.parent = my1
    # printing GA tree
    logger.debug( root.tree_string_rep() )
    
    # creating new root node
    my3 = EaNode('C+', BitArray(bin='0110110001100000'))
    # rearanginig nodes
    root.attach_child(my3)
    # printing GA tree
    logger.debug( root.tree_string_rep() )
    return


# this means that if this script is executed, then 
# main() will be executed
if __name__ == "__main__":
    main()



