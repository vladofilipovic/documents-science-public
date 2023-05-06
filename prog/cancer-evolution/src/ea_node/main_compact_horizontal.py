""" This module module contains an example how to use 
methods from EaNode class.

"""
import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

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
    my1 = EaNode('E+', BitArray(bin = '0111000001100000'), parent=root)
    my2 = EaNode('F+', BitArray(bin='0110100001100000'), parent=root)
    my2a = EaNode('U+', BitArray(bin='0110100001100000'), parent=root)
    # rearanginig nodes
    my2.parent = my1    
    my2a.parent = my1    
    # creating new root node
    my3 = EaNode('G+', BitArray(bin='0110110001100000'))
    # rearanginig nodes
    root.attach_child(my3)

    my4 = EaNode('C+', BitArray(bin='0110110001100000')) 
    my4.parent = root
    my5 = EaNode('E+', BitArray(bin = '0110000001100000'))
    my6 = EaNode('A+', BitArray(bin = '0111000001100000'), parent=my5)
    my7 = EaNode('B+', BitArray(bin='0110100001100000'), parent=my6)
    my5.parent = root

    logger.debug( root.tree_string_rep() )
    
    root.tree_compact_horizontal()
    logger.debug( root.tree_string_rep() )

    return


# this means that if this script is executed, then 
# main() will be executed
if __name__ == "__main__":
    main()



