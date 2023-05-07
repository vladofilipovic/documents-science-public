""" The :mod:`local_search_dollo_k_idle` module contains vns
local search procedures for DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import copy
import random
import numpy as np

from typing import Optional

from utils.logger import logger

from dollo_k_node.dollo_k_node import DolloKNode

from dollo_k_solution.dollo_k_solution import DolloKSolution


class LocalSearchDolloKIdle():
    @staticmethod
    def improve_solution(solution_to_improve: DolloKSolution, alpha, beta,
            reads: list, labels: list = None, dollo_k: int = 2) -> Optional[DolloKSolution]:
        # if obtained improvement is invalid, None should be returned
        # it should be used the first improvement strategy
        initial_solution = solution_to_improve
        logger.debug("initial_solution at begin of LocalSearchDolloKIdle:" )
        logger.debug(initial_solution)        
        return initial_solution

