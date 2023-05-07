""" The :mod:`local_search_dollo_k_add_leaf` module contains vns
local search procedures for DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import os
import copy
import random

from bitstring import BitArray
from datetime import datetime

from anytree import search, PreOrderIter

from typing import Optional

from utils.logger import logger
from utils.collections_helper import next_element_in_cyclic

from dollo_k_node.dollo_k_node import DolloKNode
from dollo_k_node.dollo_k_helpers import dollo_k_subtree_add_correct_minus_node
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_2ba_falsePN_ignored


from dollo_k_solution.dollo_k_solution import DolloKSolution


class LocalSearchDolloKAddLeaf():
    @staticmethod
    def improve_solution(solution_to_improve: DolloKSolution, alpha: float, beta: float,
            reads: list, labels: list = None, dollo_k: int = 2 ) -> Optional[DolloKSolution]:
        # if obtained improvement is invalid, None should be returned
        # it should be used the first improvement strategy
        logger.debug("solution_to_improve at begin of LocalSearchDolloKAddLeaf:" )
        logger.debug(solution_to_improve)
        improved_solution = copy.deepcopy(solution_to_improve) 
        individual = improved_solution._dollo_k_node
        # make the individual correct
        (is_ok, label) = individual.is_correct(labels, dollo_k) 
        if(not is_ok and '-'in label):
            counter = 2 * dollo_k
            while not is_ok and counter >= 0:
                individual.tree_remove_node_by_label(label)
                counter -= 1
                (is_ok, label) = individual.is_correct(labels, dollo_k)
        if(not is_ok and '+' in label):
            individual.tree_add_leaf(label)
            individual.tree_set_binary_tags(labels)
            is_ok = True
        if(not is_ok):
            raise ValueError("Error!" + "\n" 
                                + "reason: " + is_ok[1] + "\n" 
                                + "individual: " + "\n", individual) 
        # add plus node as leaf if such does not exists
        selected = list(PreOrderIter(individual, filter_=lambda node: node.is_leaf))
        for l in labels:
            if individual.tree_node_find(l+'+') == None:
                # plus label should be inserted in tree
                for parent in selected:
                    # create and attach new leaf node
                    new_bit_array = BitArray()
                    new_node = DolloKNode(l+'+',new_bit_array)
                    parent.attach_child(new_node)
                    # normalize tree and calculate fitness
                    parent.tree_compact_vertical()
                    parent.tree_compact_horizontal()
                    parent.tree_rearrange_by_label()                    
                    parent.tree_set_binary_tags(labels)
                    improved_solution.determine_fitness(reads, alpha, beta)
                    logger.debug("possibly improved solution during local search:" )
                    logger.debug(improved_solution)
                    if improved_solution.is_better(solution_to_improve, reads):
                        return improved_solution
                    else:
                        new_node.parent = None
                        parent.tree_compact_vertical()
                        parent.tree_compact_horizontal()
                        parent.tree_rearrange_by_label()                    
                        parent.tree_set_binary_tags(labels)
        # add minus node as leaf, if possible 
        for l in labels:
            for parent in selected:
                # check if there is plus ancestor
                found_plus = False
                curr = parent
                while curr != parent.root:
                    if curr.node_label == l+'+':
                        found_plus = True
                        break
                    curr = curr.parent
                if not found_plus:
                    continue
                # if there is, create and attach new leaf node
                new_bit_array = BitArray()
                new_node = DolloKNode(l+'-',new_bit_array)
                parent.attach_child(new_node)
                # normalize tree and calculate fitness 
                parent.tree_compact_vertical()
                parent.tree_compact_horizontal()
                parent.tree_rearrange_by_label()                    
                parent.tree_set_binary_tags(labels)
                improved_solution.determine_fitness(reads, alpha, beta)
                logger.debug("possibly improved solution during local search:" )
                logger.debug(improved_solution)
                if improved_solution.is_better(solution_to_improve, reads):
                    return improved_solution
                else:
                    new_node.parent = None
                    parent.tree_compact_vertical()
                    parent.tree_compact_horizontal()
                    parent.tree_rearrange_by_label()                    
                    parent.tree_set_binary_tags(labels)
        return None




