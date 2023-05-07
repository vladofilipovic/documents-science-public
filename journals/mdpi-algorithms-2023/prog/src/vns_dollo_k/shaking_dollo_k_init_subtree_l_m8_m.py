""" The :mod:`shaking_dollo_k_init_subtree` module contains vns
local search procedures for DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import os
import copy
import random
import pickle
import numpy as np

from typing import Optional

from datetime import datetime

from bitstring import BitArray

from anytree import search
from anytree.iterators.levelordergroupiter import LevelOrderGroupIter

from utils.logger import logger

from dollo_k_node.dollo_k_node import DolloKNode
from dollo_k_node.dollo_k_helpers import dollo_k_subtree_add_correct_minus_node
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_2ba_falsePN_ignored

from dollo_k_solution.dollo_k_solution import DolloKSolution


""" shaking on the the individual tree, that does not change anything

Args:
    individual (DolloKNode): individual that will be changed.

Returns:            
    pair where the first component is indicator of success and the second is
    changed individual e.g. output of the local search process.
"""
class ShakingDolloKInitSubtreeLevelM8M():
    @staticmethod
    def shake_solution(solution_to_shake: DolloKSolution, alpha: float, beta: float,
            reads: list, labels: list = None, dollo_k: int = 2 ) -> Optional[DolloKSolution]:
        logger.debug("solution to shake at beginning of ShakingDolloKInitSubtreeLM3:" )
        logger.debug(solution_to_shake)
        shaken_solution = copy.deepcopy(solution_to_shake) 
        individual = shaken_solution._dollo_k_node
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
        # add subtree on specified position
        random01 = random.random()
        # adding plus label and removing same plus label
        tree_height = individual.height
        min_level = 8
        max_level = 300
        possible_parents = [node for node in LevelOrderGroupIter(individual, maxlevel=tree_height-min_level)]
        while possible_parents == None or len(possible_parents) == 0:
            min_level -= 1
            possible_parents = [node for node in LevelOrderGroupIter(individual, maxlevel=tree_height-min_level)]
        possible_parents = possible_parents[min_level-max_level:]
        random_level = random.randint(0, len(possible_parents)-1)
        random_parent = random.choice(possible_parents[random_level])
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
        shaken_solution.determine_fitness(reads, alpha, beta)
        logger.debug("shaken solution:" )
        logger.debug(shaken_solution)
        return shaken_solution