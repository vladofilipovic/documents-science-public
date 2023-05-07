""" The :mod:`dollo_node_initialization_operators` module contains operators
for initialization of DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from bitstring import BitArray

    
def init_dollo_k_individual(ind_class, labels, k, init_max_fill_factor):
    """ Initialization of the individual.
    Args:
        ind_class: class of the individual to be initialized - should be 
            DolloKNode.
        labels (list): list of the labels of the nodes in the tree that should 
            be initialized.
        k(int): Value od the Dollo k parameter.
    Returns: 
        DolloKNode: individual that is initialized.           
    """
    rootBitArray = BitArray(int = 0, length = len(labels) )
    root = ind_class('ooo', rootBitArray)
    root.tree_initialize(labels, k, init_max_fill_factor)
    return root

