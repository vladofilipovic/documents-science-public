"""
The :mod:`dollo_k_solution` module contains DolloKSolution class.

DolloKSolution class contains an DolloKNode of the mutation tree and the fitness of that node.
"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import random

from dollo_k_node.dollo_k_node import DolloKNode


class DolloKSolution:
    """ Information about solution.
    """

    def __init__(self, dollo_k_node, evaluation_fn, fitness=None):
        """ Instance initialization.
        
        Args:
            dollo_k_node (:DolloKNode): Parameter `dollo_k_node`represents the node.
            fitness (float): Parameter `fitness` represents the fitness of the node.
        """
        self._dollo_k_node = dollo_k_node
        self._fitness = fitness
        self._evaluation_fn = evaluation_fn

    def __repr__(self):
        """ Obtaining representation of the instance.

        Representation of the node instance is the whole tree formed by the 
        descendats of that nide instance.
    
        Returns:
            str: Representation of the instance.
        """
        ret = u""
        ret += str(self._dollo_k_node) + u'\n'
        if self._fitness == None:
            ret += "Fitness is not calculated yet"
        else:
            ret += "Fitness: " + str(self._fitness)
        return ret
    
    def __str__(self):
        """ Obtaining string representation of the instance.

        String representation of the node instance is the whole tree formed by 
        the descendats of that nide instance.

        Returns:
            str: String representation of the instance.
        """
        ret = u""
        ret += str(self._dollo_k_node) + u'\n'
        if self._fitness == None:
            ret += "Fitness is not calculated yet"
        else:
            ret += "Fitness: " + str(self._fitness)
        return ret

    def determine_fitness(self, reads, alpha, beta):
        self._fitness = self._evaluation_fn(reads, alpha, beta, self._dollo_k_node)

    def is_better(self, other, reads):
        if self._fitness == None:
            self.determine_fitness(reads, alpha, beta)
        if other._fitness == None:
            other.determine_fitness(reads, alpha, beta)
        return self._fitness < other._fitness

