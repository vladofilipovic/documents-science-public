from datetime import datetime
from utils.logger import logger

from dollo_k_solution.dollo_k_solution import DolloKSolution

class Vns:
    @staticmethod
    def solve(initial_solution: DolloKSolution, shaking_neighborhood: list, ls_neighborhood: list, 
            alpha: float, beta: float, reads: list, labels: list, dollo_k: int = 2,
            max_iterations: int = 1000, max_time_sec: int = 0) -> DolloKSolution:
        x = initial_solution
        curr_iteration = 0
        start_time = datetime.now()
        while True:
            k = 0
            while k < len(shaking_neighborhood):
                cur_sh_neighborhood = shaking_neighborhood[k]
                x1 = cur_sh_neighborhood.shake_solution(x, alpha, beta, reads, labels, dollo_k)
                l = 0
                while l < len(ls_neighborhood):
                    cur_ls_neighborhood = ls_neighborhood[l]
                    x2 = cur_ls_neighborhood.improve_solution(x1, alpha, beta, reads, labels, dollo_k)
                    if x2 is not None and (x1 is None or x2.is_better(x1, reads)):
                        x1 = x2
                        l = 0
                    else:
                        l += 1
                if x1 is not None and x1.is_better(x, reads):
                    x = x1
                    k = 0
                else:
                    k += 1
            logger.info('Iteration: %d' % curr_iteration)
            logger.info('Solution: {}'.format(x))
            curr_iteration += 1
            if max_iterations > 0:
                if curr_iteration > max_iterations:
                    break
            if max_time_sec > 0:
                elapsed_time = datetime.now() - start_time
                if elapsed_time.total_seconds() > max_time_sec:
                    break
        return x