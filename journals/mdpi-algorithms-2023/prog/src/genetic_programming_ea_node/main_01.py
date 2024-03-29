""" The :mod:`main_gp_01` module contains an example how to use Deap for GP
that solves problem we are dealing with.

Example for command-line parameters:
inputFile=example_01.in randomSeed=1113 --debug

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import optparse
import random

from deap import base
from deap import creator
from deap import tools

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from utils.command_line_gp import get_execution_parameters
from utils.command_line_gp import default_parameters

from reads.read_input import read_labels_reads_format_in

from ea_node.ea_node import EaNode
from gp_ea_node_operators import init_ea_node_individual  
from gp_ea_node_operators import assign_reads_to_ea_tree 
from gp_ea_node_operators import evaluate_ea_node_individual
from gp_ea_node_operators import mutate_ea_node_individual

def main():
    """ This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)
    # reading command-line arguments and options
    parser = optparse.OptionParser()
    parser.set_defaults(debug=False,xls=False)
    parser.add_option('--debug', action='store_true', dest='debug')
    parser.add_option('--verbose', action='store_true', dest='verbose')
    (options, args) = parser.parse_args()
    
    # obtaining execution parameters
    parameters = get_execution_parameters(options, args, default_parameters)
    if(options.debug):
        logger.debug("Execution parameters: ", parameters);
    
    # seeding random process
    if( int(parameters['RandomSeed'])>0 ):
        random.seed(parameters['RandomSeed'])

    # reading read elements from input file
    (labels, reads) = read_labels_reads_format_in(options, parameters)
    if( options.debug):
        logger.debug("Mutatuion labels:", labels);
        logger.debug("Reads (from input):")
        for x in reads:
            logger.debug(x);
    
    # creating fitness function
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    # creating structure of the individual
    creator.create("Individual", EaNode, fitness=creator.FitnessMax)
    
    # creating toolbox for execution of the genetic algorithm
    toolbox = base.Toolbox()
    
    # registering boolean attribute to toolbox 
    toolbox.register("attr_bool", random.randint, 0, 1)
    # registering individual creation to toolbox 
    toolbox.register("individual", 
                        init_ea_node_individual, 
                        creator.Individual, 
                        labels=labels, 
                        size=3 * len(labels))
    # registering mutation operator to toolbox 
    toolbox.register("mutate", mutate_ea_node_individual)
    # registering population to toolbox 
    toolbox.register("population", 
                        tools.initRepeat, 
                        list, 
                        toolbox.individual)

    toolbox.register("evaluate", evaluate_ea_node_individual, reads)

    
    # creating one individual via toolbox
    test_ind = toolbox.individual()
    
    # printing test individual 
    logger.debug( test_ind )
    
    # testing if created individual is inherited from GaMode
    # and printing output
    if(issubclass(type(test_ind), EaNode)):
        logger.debug( "Class Individual is sublass of class EaNode")
    else:
        logger.debug( "Class Individual is NOT sublass of class EaNode")
    
    # setting fitness of the individual
    test_ind.fitness.values = (12, 0)
    
    # executiong mutation on the individual
    toolbox.mutate(test_ind)
    
    # assign reads to nodes and calculate total distance
    (assignment, diff) = assign_reads_to_ea_tree(test_ind, reads)
    logger.debug(assignment)
    logger.debug( diff )    
    return

# this means that if this script is executed, then 
# main() will be executed
if __name__ == '__main__':
    main()



