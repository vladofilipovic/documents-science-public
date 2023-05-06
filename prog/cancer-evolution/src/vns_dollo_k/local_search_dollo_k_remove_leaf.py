""" The :mod:`local_search_dollo_k_remove_leaf` module contains vns
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

class LocalSearchDolloKRemoveLeaf():
    @staticmethod
    def improve_solution(solution_to_improve: DolloKSolution, alpha: float, beta: float,
            reads: list, labels: list = None, dollo_k: int = 2 ) -> Optional[DolloKSolution]:
        # if obtained improvement is invalid, None should be returned
        # it should be used the first improvement strategy
        logger.debug("solution_to_improve at begin of LocalSearchDolloKRemoveLeaf:" )
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
        for elem in selected:
            if elem.node_label[-1:] == '-':
                # remove leaf
                elem_parent = elem.parent
                elem.parent = None
                # normalize tree and calculate fitness
                if elem_parent != None: 
                    elem_parent.tree_compact_vertical()
                    elem_parent.tree_compact_horizontal()
                    elem_parent.tree_rearrange_by_label()                    
                    elem_parent.tree_set_binary_tags(labels)
                improved_solution.determine_fitness(reads, alpha, beta)
                logger.debug("possibly improved solution during local search:" )
                logger.debug(improved_solution)
                if improved_solution.is_better(solution_to_improve, reads):
                    return improved_solution
                else: 
                    elem.parent = elem_parent
                    if elem_parent != None:
                        elem_parent.tree_compact_vertical()
                        elem_parent.tree_compact_horizontal()
                        elem_parent.tree_rearrange_by_label()                    
                        elem_parent.tree_set_binary_tags(labels)
        return None




