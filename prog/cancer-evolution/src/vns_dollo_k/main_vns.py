"""  The :mod:`main_vns_direct` module represents an entry  point of the application.

Example for command-line parameters:
inputFile=example_01.in randomSeed=1113 --debug

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import optparse
import random

from bitstring import BitArray 

from datetime import datetime

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from utils.command_line_vns import get_execution_parameters
from utils.command_line_vns import default_parameters

from reads.read_input import read_labels_reads_format_in
from reads.read_input import read_labels_reads_format_012

from dollo_k_node.dollo_k_node import DolloKNode

from dollo_k_solution.dollo_k_solution import DolloKSolution

from dollo_k_node.dollo_k_initialization import init_dollo_k_individual

from dollo_k_node.dollo_k_evaluation_likelihood import evaluate_dollo_k_likelihood
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_2ba_falsePN_ignored
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_012_falsePN_ignored

from shaking_dollo_k_idle import ShakingDolloKIdle
from shaking_dollo_k_init_subtree_l_m0_m2 import ShakingDolloKInitSubtreeLevelM0M2
from shaking_dollo_k_init_subtree_l_m3_m5 import ShakingDolloKInitSubtreeLevelM3M5
from shaking_dollo_k_init_subtree_l_m6_m8 import ShakingDolloKInitSubtreeLevelM6M8
from shaking_dollo_k_init_subtree_l_m8_m import ShakingDolloKInitSubtreeLevelM8M

from local_search_dollo_k_idle import LocalSearchDolloKIdle
from local_search_dollo_k_add_leaf import LocalSearchDolloKAddLeaf
from local_search_dollo_k_remove_leaf import LocalSearchDolloKRemoveLeaf
from local_search_dollo_k_add_leaf_w_p import LocalSearchDolloKAddLeafWP
from local_search_dollo_k_remove_leaf_w_p import LocalSearchDolloKRemoveLeafWP
from local_search_dollo_k_add_leaf_w_p_p import LocalSearchDolloKAddLeafWPP
from local_search_dollo_k_remove_leaf_w_p_p import LocalSearchDolloKRemoveLeafWPP

from vns import Vns

def main():
    """ This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)
    logger.debug('Execution started.')    
    # reading command-line arguments and options
    parser = optparse.OptionParser()
    parser.set_defaults(debug=False,xls=False)
    parser.add_option('--debug', action='store_true', dest='debug')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    (options, args) = parser.parse_args()
    
    try:    
        # Obtaining execution parameters
        parameters = get_execution_parameters(options, args, default_parameters)
        logger.info('Execution parameters: {}'.format(parameters))

        input_format = parameters['InputFormat']
        evaluation_type = parameters['EvaluationType']

        # Reading read elements from input file
        if(input_format == '2ba'):
            (labels, reads) = read_labels_reads_format_in(options, parameters)
            logger.debug('Mutation labels (from input file):\n {}'.format(labels))
            logger.debug('2ba Reads [Unknowns] (from input file)::\n {}'.format(reads))
        elif(input_format == '012'):
            (labels, reads) = read_labels_reads_format_012(options, parameters)
            logger.debug('Mutation labels (from input file):\n {}'.format(labels))
            logger.debug('012 Reads (from input file)::\n {}'.format(reads))
        else:
            logger.info("Input format is not right: " + input_format + "\n" 
                    + "Should be one of: 2ba, 012 \n") 
            return

        #  Opening output file 
        output_file_name = parameters['InputFile'].split('/')[1]
        output_file_name = output_file_name.split('.')[0]
        dt = datetime.now()
        output_file_name = OUTPUT_DIR + '/' + output_file_name + '-vns-' + evaluation_type[:3] + '-' + dt.strftime("%Y-%m-%d-%H-%M-%S.%f") + '.txt'
        logger.debug("Output file name: {}".format(output_file_name))
        output_file = open(output_file_name, "w", encoding="utf-8")

        # Initial write to output file
        logger.info("VNS algorithm started")
        start_time = datetime.now()
        output_file.write("VNS algorithm started at: %s\n" % str(start_time))
        # Write execution parameters to output file
        output_file.write('Execution parameters: {}\n'.format(parameters))

        # Set random seed
        if( int(parameters['RandomSeed']) > 0 ):
            r_seed = int(parameters['RandomSeed'])
            logger.info("RandomSeed is predefined. Predefined seed value:  %d" % r_seed)
            output_file.write("RandomSeed is predefined. Predefined seed value:  %d\n" % r_seed)
            random.seed(r_seed)
        else:
            r_seed = random.randrange(sys.maxsize)
            logger.info("RandomSeed is not predefined. Generated seed value:  %d" % r_seed)
            output_file.write("RandomSeed is not predefined. Generated seed value:  %d\n" % r_seed)
            random.seed(r_seed)

        dollo_k = int(parameters['DolloK'])
        init_max_fill_factor = parameters['InitializationMaxFillFactor']
        
        # Probability of false positives and false negatives
        alpha = float(parameters['Alpha'])
        beta = float(parameters['Beta'])

        # Variable for maximum number of iterations    
        max_number_iterations = int(parameters['MaxNumberIterations'])
        # Variable for maximum time for execution (in seconds) 
        # value 0 means that time for execution is unlimited
        max_seconds_for_execution = int(parameters['MaxTimeForExecutionInSeconds'])

        if evaluation_type == 'direct-2ba':
            evaluation_fn = evaluate_dollo_k_direct_2ba_falsePN_ignored
        elif evaluation_type == 'direct-012':
            evaluation_fn = evaluate_dollo_k_direct_012_falsePN_ignored
        elif evaluation_type == 'likelihood-012':
            evaluation_fn = evaluate_dollo_k_likelihood
        else:
            logger.info("Incorrect evaluation type: " + evaluation_type + "\n" 
                    + "Should be one of: direct-012, direct-2ba, likelihood-012 \n") 
            return
        rootBitArray = BitArray(int = 0, length = len(labels) )
        root = DolloKNode('ooo', rootBitArray)
        root.tree_initialize(labels, dollo_k, init_max_fill_factor)
        initial_solution = DolloKSolution(root, evaluation_fn, None)
        initial_solution.determine_fitness(reads, alpha, beta)
        logger.info('Initial solution: {}'.format(initial_solution))
    
        # Shaking neighborhood
        shaking_neighborhood = [
            ShakingDolloKInitSubtreeLevelM0M2
            , ShakingDolloKInitSubtreeLevelM3M5
            , ShakingDolloKInitSubtreeLevelM6M8
            , ShakingDolloKInitSubtreeLevelM8M
            , ShakingDolloKIdle
        ]
        # Local Search neighborhood
        ls_neighborhood = [
            LocalSearchDolloKAddLeaf
            , LocalSearchDolloKRemoveLeaf
            , LocalSearchDolloKAddLeafWP
            , LocalSearchDolloKRemoveLeafWP
            , LocalSearchDolloKAddLeafWPP
            , LocalSearchDolloKRemoveLeafWPP
            , LocalSearchDolloKIdle
        ]

        final_solution = Vns.solve(initial_solution, shaking_neighborhood, ls_neighborhood, 
                alpha, beta, reads, labels, dollo_k,
                max_number_iterations, max_seconds_for_execution)
        
        logger.info('VNS algorithm finished.')
        output_file.write("VNS algorithm finished at: %s\n" % datetime.now())
        logger.info("Final solution (fitness: %f)" % final_solution._fitness[0])
        output_file.write("Final solution (fitness: %f)" % final_solution._fitness[0])
        logger.info(final_solution)
        output_file.write(str(final_solution))
        return
    except Exception as exp:
        if hasattr(exp, 'message'):
            logger.exception('Exception: %s\n' % exp.message)
        else:
            logger.exception('Exception: %s\n' % str(exp))
        


# this means that if this script is executed, then 
# main() will be executed
if __name__ == '__main__':
    main()



