""" The :mod:`shaking_dollo_k_idle` module contains vns
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

from datetime import datetime

from typing import Optional

from bitstring import BitArray

from anytree import search

from utils.logger import logger

from dollo_k_solution.dollo_k_solution import DolloKSolution


""" shaking on the the individual tree, that does not change anything

Args:
    individual (DolloKNode): individual that will be changed.

Returns:            
    pair where the first component is indicator of success and the second is
    changed individual e.g. output of the local search process.
"""
class ShakingDolloKIdle():
    @staticmethod
    def shake_solution(solution_to_shake: DolloKSolution, alpha: float, beta: float,
            reads: list, labels: list = None, dollo_k: int = 2 ) -> Optional[DolloKSolution]:
        initial_solution = solution_to_shake
        logger.debug("initial_solution at begin of ShakingDolloKIdle:" )
        logger.debug(initial_solution)
        shaken_solution = solution_to_shake
        return shaken_solution