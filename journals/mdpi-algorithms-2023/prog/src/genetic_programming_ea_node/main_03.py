"""  The :mod:`cancer_gp` module represents an entry  point of the application.

Example for command-line parameters:
inputFile=example_01.in randomSeed=1113 --debug

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

import optparse
import random

from datetime import datetime

from deap import base
from deap import creator
from deap import tools


from utils.command_line_gp import get_execution_parameters
from utils.command_line_gp import default_parameters

from reads.read_input import read_labels_reads_format_in

from ea_node.ea_node import EaNode
from gp_ea_node_operators import init_ea_node_individual
from gp_ea_node_operators import evaluate_ea_node_individual 
from gp_ea_node_operators import crossover_ea_node_individuals
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
    if(options.debug or options.verbose):
        logger.debug("Execution parameters: ", parameters);
    
    # setting random seed
    if( int(parameters['RandomSeed']) > 0 ):
        random.seed(int(parameters['RandomSeed']))
    else:
        random.seed(datetime.now())

    # reading read elements from input file
    if( parameters['InputFormat'] == 'in' ):
        (labels, reads) = read_labels_reads_format_in(options, parameters)
        if(options.debug or options.verbose):
            logger.debug("Mutation labels:", labels);
            logger.debug("Reads (from input):")
            for x in reads:
                logger.debug(x);
    else:
        logger.debug("Input format is not right.")
        return
    
    # create fitness function
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
   
    # create structure of the individual
    creator.create("Individual", EaNode, fitness=creator.FitnessMin)
    
    # create toolbox for execution of the genetic algorithm
    toolbox = base.Toolbox()
    
    # register boolean attribute to toolbox 
    toolbox.register("attr_bool", random.randint, 0, 1)

    # register individual creation to toolbox 
    toolbox.register("individual", 
                     init_ea_node_individual, 
                     creator.Individual, 
                     labels=labels, 
                     size=2 * len(labels))
      
    # register population to toolbox 
    toolbox.register("population", 
                     tools.initRepeat, 
                     list, 
                     toolbox.individual)
 
    # register evaluation function
    toolbox.register("evaluate", 
                     evaluate_ea_node_individual, 
                     reads)

    # register the crossover operator
    toolbox.register("mate", 
                     crossover_ea_node_individuals)
    
    # register a mutation operator 
    toolbox.register("mutate", 
                     mutate_ea_node_individual)
     
    # operator for selecting individuals for breeding the next
    # generation: each individual of the current generation
    # is replaced by the 'fittest' (best) of three individuals
    # drawn randomly from the current generation.
    toolbox.register("select", 
                     tools.selTournament, 
                     tournsize=3)

    # create an initial population, where each individual is a GaTree
    population_size = 5
    pop = toolbox.population(n=population_size)
    if( options.verbose):
        logger.debug("Population (size %d) - initial\n"%len(pop))
        print (pop)
 
    # Probability with which two individuals are crossed
    crossover_probability = 0.5
       
    # Probability for mutating an individual
    mutation_probability = 0.2

    if( options.debug or options.verbose):
        logger.debug("Start of evolution")
 
    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    if( options.debug):
        logger.debug("Fitnesses of individuals in population - initial")
        print (fitnesses)
    
    # Assign fitness to individuals in population
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit
        
    # Variable keeping track of the number of generations
    generation = 0
  
    # Begin the evolution
    while True:
        if( options.debug or options.verbose):
            logger.debug("-- Generation %i --" % generation)

        if( options.debug or options.verbose):
            fits = [ind.fitness.values[0] for ind in pop]
            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            logger.debug("  Fitness: ", fits)
            logger.debug("  Min %s" % min(fits))
            logger.debug("  Max %s" % max(fits))
            logger.debug("  Avg %s" % mean)
            logger.debug("  Std %s" % std)
            best_in_generation = tools.selBest(pop, 1)[0]
            logger.debug("  Best individual: \n %s", best_in_generation)
      
        # A new generation
        generation += 1
        
        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))
    
        # Apply crossover on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # cross two individuals with previously determined probability 
            if random.random() < crossover_probability:
                toolbox.mate(child1, child2)
                # fitness values of the children
                # must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        # Apply mutation on the offspring
        for mutant in offspring:
            # mutate an individual with previously determined probability 
            if random.random() < mutation_probability:
                toolbox.mutate(mutant)
                # fitness values of the mutant
                # must be recalculated later
                del mutant.fitness.values
    
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        # The population is entirely replaced by the offspring
        pop[:] = offspring
        
        # Gather all the fitnesses in one list and print the stats
        
        # Check if any of finishing criteria is meet
        # Criteria based on number of generations
        if( generation > 10 ):
            break
        # Criteria based on standard deviation of fitness in population
        fits = [ind.fitness.values[0] for ind in pop]
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5 
        if( std <= 0):
            break
          
    if( options.debug or options.verbose):
        logger.debug("-- End of evolution --")
    if( options.verbose):
        logger.debug("Population (size %d) - at end\n"%len(pop))
        print (pop)  
    best_ind = tools.selBest(pop, 1)[0]
    logger.debug("Best individual is\n%s\n, with fitness %s" % (best_ind, best_ind.fitness.values))
    return

# this means that if this script is executed, then 
# main() will be executed
if __name__ == '__main__':
    main()



