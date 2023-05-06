""" The :mod:`dollo_node_mutation_operators` module contains operators
for mutation of DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import copy
import random

from bitstring import BitArray

from anytree import search

from utils.logger import logger

from dollo_k_node.dollo_k_node import DolloKNode

from dollo_k_node.dollo_k_helpers import dollo_k_subtree_add_correct_minus_node

def mutation_dollo_k_add(labels,dollo_k,individual):
    """ Mutation of the individual, by randomly adding one node

    Args:
        labels (list): list of the labels of the nodes in the tree that should 
            be initialized.
        dollo_k(int): Value od the Dollo k parameter.
        individual (DolloKNode): individual that will be mutated.

    Returns:            
        pair where the first component is indicator of success and the second is
        individual that is mutated e.g. output of the mutation process.
    """
    is_ok = individual.is_correct(labels, dollo_k) 
    if(not is_ok[0]):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + is_ok[1] + "\n" 
                            + "individual: " + "\n", individual) 
    logger.debug("individual at begin:" )
    logger.debug(individual)
    random01 = random.random()
    label_is_plus = random01 < (len(labels)/float(1+len(individual.descendants)) ) 
    if(label_is_plus):
        # adding plus label and removing same plus label
        random_parent = random.choice(individual.descendants)
        random_label = random.choice(labels)
        while( random_label + '+' == random_parent.node_label):
            random_label = random.choice(labels)
        # this parent node will disappear, so its parent is provided for attach
        if( random_label + '-' == random_parent.node_label ):
            random_parent = random_parent.parent
        logger.debug("random_parent:")
        logger.debug( random_parent)
        logger.debug("random_label:")
        logger.debug(random_label)
        # remove old plus node
        old_plus_node = individual.tree_node_find(random_label+'+')
        parent_old_plus_node = old_plus_node.parent
        for child in old_plus_node.children:
            child.parent = parent_old_plus_node
        old_plus_node.parent = None
        num_removed = parent_old_plus_node.tree_remove_incorrect_minus_nodes()
        # create new leaf node
        new_bit_array = BitArray()
        new_node = DolloKNode(random_label+'+',new_bit_array)
        # attach leaf node
        random_parent.attach_child(new_node)
        # randomly add minus correct nodes
        for i in range(0,num_removed):
            dollo_k_subtree_add_correct_minus_node(individual, labels, dollo_k)
    else:
        # adding minus label and removing same plus label
        dollo_k_subtree_add_correct_minus_node(individual,labels,dollo_k)
    individual.tree_compact_vertical()
    individual.tree_compact_horizontal()
    individual.tree_rearrange_by_label()
    individual.tree_set_binary_tags(labels)
    logger.debug("individual at end: ")
    logger.debug(individual)
    is_ok, label = individual.is_correct(labels, dollo_k) 
    if(not is_ok and '-' in label):
        counter = 2 * dollo_k
        while not is_ok and counter >= 0:
            individual.tree_remove_node_by_label(label)
            counter -= 1
            is_ok, label = individual.is_correct(labels, dollo_k)
    if(not is_ok and '+' in label):
        individual.tree_add_leaf(label)
        individual.tree_set_binary_tags(labels)
        is_ok = True
    if(not is_ok):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + label + "\n" 
                            + "individual: " + "\n", individual) 
    return (True,individual)

def mutation_dollo_k_remove(labels, dollo_k, individual):
    """ Mutation of the individual, by randomly removing one node

    Args:
        labels (list): list of the labels of the nodes in the tree that should 
            be initialized.
        dollo_k(int): Value od the Dollo k parameter.
        individual (DolloKNode): individual that will be mutated.

    Returns:            
        pair where the first component is indicator of success and the second is
        individual that is mutated e.g. output of the mutation process.
    """
    is_ok = individual.is_correct(labels, dollo_k) 
    if(not is_ok[0]):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + is_ok[1] + "\n" 
                            + "individual: " + "\n", individual) 
    logger.debug("individual at start: ")
    logger.debug(individual)
    random_node = random.choice(individual.descendants)
    random_label = random_node.node_label[:-1]
    if(random_node.node_label==random_label+'-'):
        # delete minus node
        parent_random_node = random_node.parent
        for child in random_node.children:
            child.parent = parent_random_node
        random_node.parent = None
    elif(random_node.node_label==random_label+'+'):
        # delete plus node
        parent_random_node = random_node.parent
        for child in random_node.children:
            child.parent = parent_random_node
        random_node.parent = None
        num_removed = parent_random_node.tree_remove_incorrect_minus_nodes()
        # create new plus node and attach it
        parent_of_new_node = random.choice(individual.descendants)
        new_bit_array = BitArray()
        new_node = DolloKNode(random_label+'+',new_bit_array)
        parent_of_new_node.attach_child(new_node)
        for i in range(0,num_removed-1):
            dollo_k_subtree_add_correct_minus_node(parent_of_new_node, labels, dollo_k)
    individual.tree_compact_vertical()
    individual.tree_compact_horizontal()
    individual.tree_rearrange_by_label()
    individual.tree_set_binary_tags(labels)
    logger.debug("individual at end: ")
    logger.debug(individual)
    is_ok = individual.is_correct(labels, dollo_k) 
    if(not is_ok[0]):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + is_ok[1] + "\n" 
                            + "individual: " + "\n", individual) 
    return (True,individual)

def mutation_dollo_k_combine(labels, dollo_k, individual):
    """ Mutatuion of the individual.

    Args:
        labels (list): list of the labels of the nodes in the tree that should 
            be initialized.
        dollo_k(int): Value od the Dollo k parameter.
        individual (DolloKNode): individual that will be mutated.

    Returns:            
        tuple where the first elelemt is mutataed e.g. output of the
        mutation process.
    """
    is_ok = individual.is_correct(labels, dollo_k) 
    if(not is_ok[0]):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + is_ok[1] + "\n" 
                            + "individual: " + "\n", individual) 
    
    random01 = random.random()
    if(random01 <= 0.5): 
        (successfully,individual) = mutation_dollo_k_add(labels, dollo_k, individual)
        if(successfully):
            return (individual,)
        else:
            (successfully,individual) = mutation_dollo_k_remove(labels, dollo_k, individual)
            return (individual,)
    elif(random01 > 0.5): 
        (successfully,individual) = mutation_dollo_k_remove(labels, dollo_k, individual)
        if(successfully):
            return (individual,)
        else:
            (successfully,individual) = mutation_dollo_k_add(labels, dollo_k, individual)
            return (individual,)
    is_ok = individual.is_correct(labels, dollo_k) 
    if(not is_ok[0]):
        raise ValueError("Error!" + "\n" 
                            + "reason: " + is_ok[1] + "\n" 
                            + "individual: " + "\n", individual) 
    return (individual)


