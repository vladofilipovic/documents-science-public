"""  The :mod:`main_gp_direct` module represents an entry  point of the application.

Example for command-line parameters:
inputFile=example_01.in randomSeed=1113 --debug

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import optparse
import random

from datetime import datetime

DEAP_DIR = '../../--f--DEAP--deap'
sys.path.append(path.Path(DEAP_DIR).abspath())
from deap import base
from deap import creator
from deap import tools

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from utils.command_line_gp import get_execution_parameters
from utils.command_line_gp import default_parameters

from reads.read_input import read_labels_reads_format_in
from reads.read_input import read_labels_reads_format_012

from dollo_k_node.dollo_k_node import DolloKNode

from dollo_k_node.dollo_k_initialization import init_dollo_k_individual

from dollo_k_node.dollo_k_evaluation_likelihood import evaluate_dollo_k_likelihood
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_2ba_falsePN_ignored
from dollo_k_node.dollo_k_evaluation_direct import evaluate_dollo_k_direct_012_falsePN_ignored

from dollo_k_crossover_operators import crossover_dollo_k_exchange_parent_indices

from dollo_k_mutation_operators import mutation_dollo_k_combine

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
        output_file_name = OUTPUT_DIR + '/' + output_file_name + '-gp-' + evaluation_type[:3] + '-' + dt.strftime("%Y-%m-%d-%H-%M-%S.%f") + '.txt'
        logger.debug("Output file name: {}".format(output_file_name))
        output_file = open(output_file_name, "w", encoding="utf-8")

        # Initial write to output file
        logger.info("GP algorithm started")
        start_time = datetime.now()
        output_file.write("GP algorithm started at: %s\n" % str(start_time))
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

        # Create fitness function
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))

        # Create structure of the individual
        creator.create("Individual", DolloKNode, fitness=creator.FitnessMin)
        
        # Parameter k in Dollo model
        dollo_k = int(parameters['DolloK'])
        
        # Create toolbox for execution of the GP algorithm
        toolbox = base.Toolbox()
        
        # Register boolean attribute to toolbox 
        toolbox.register("attr_bool", random.randint, 0, 1)

        init_max_fill_factor = parameters['InitializationMaxFillFactor']
        
        # Register individual creation to toolbox 
        toolbox.register("individual", 
                            init_dollo_k_individual, 
                            creator.Individual, 
                            labels=labels, 
                            k=dollo_k,
                            init_max_fill_factor = init_max_fill_factor)

        # Register population to toolbox 
        toolbox.register("population", 
                            tools.initRepeat, 
                            list, 
                            toolbox.individual)

        # Probability of false positives and false negatives
        alpha = float(parameters['Alpha'])
        beta = float(parameters['Beta'])
        
        # Register evaluation function
        if evaluation_type == 'direct-2ba':
            toolbox.register("evaluate", 
                                evaluate_dollo_k_direct_2ba_falsePN_ignored, 
                                reads,
                                alpha,
                                beta)
        elif evaluation_type == 'direct-012':
            toolbox.register("evaluate", 
                                evaluate_dollo_k_direct_012_falsePN_ignored, 
                                reads,
                                alpha,
                                beta)
        elif evaluation_type == 'likelihood-012':
            toolbox.register("evaluate", 
                                evaluate_dollo_k_likelihood, 
                                reads,
                                alpha,
                                beta)
        else:
            logger.info("Incorrect evaluation type: " + evaluation_type + "\n" 
                    + "Should be one of: direct-2ba, direct-012, likelihood-012 \n") 
            return

        # Register the crossover operator
        toolbox.register("mate", 
                            crossover_dollo_k_exchange_parent_indices,
                            labels,
                            dollo_k)
        # Probability with which two individuals are crossed
        crossover_probability = float(parameters['CrossoverProbability'])
        
        # Register a mutation operator 
        toolbox.register("mutate", 
                            mutation_dollo_k_combine, 
                            labels,
                            dollo_k)
        # Probability for mutating an individual
        mutation_probability = float(parameters['MutationProbability'])

        # Operator for selecting individuals for breeding the next
        # generation: each individual of the current generation
        # is replaced by the 'fittest' (best) of three individuals
        # drawn randomly from the current generation.
        toolbox.register("select", 
                            tools.selTournamentFineGrained, 
                            fgtournsize=float(parameters['FineGrainedTournamentSize']))

        # Create an initial population, where each individual is a tree
        population_size = int(parameters['PopulationSize'])
        pop = toolbox.population(n=population_size)
        
        # Force uniqueness of the individuals in population
        for filled in range(1, len(pop)):
            is_novel = True
            for i in range(filled):
                if pop[filled].tree_is_equal(pop[i]):
                    is_novel = False
                    break
            while not is_novel:
                reserve = toolbox.population(n=1)[0]
                is_novel = True
                for i in range(filled):
                    if reserve.tree_is_equal(pop[i]):
                        is_novel = False
                        break
                if is_novel:
                    pop[filled] = reserve

        # Evaluate the entire population
        fitnesses = list(map(toolbox.evaluate, pop))
        logger.debug("Fitnesses of individuals in population - initial")
        logger.debug(fitnesses)
        # Assign fitness to individuals in population
        for ind, fit in zip(pop, fitnesses):
            ind.fitness.values = fit
        
        # Variable for maximum number of generations    
        max_number_generations = int(parameters['MaxNumberGenerations'])
        # Variable for keeping track of the number of generations
        generation = 0
        # Variable for maximum time for execution (in seconds) 
        # value 0 means that time for execution is unlimited
        max_seconds_for_execution = int(parameters['MaxTimeForExecutionInSeconds'])

        # Begin the evolution
        while True:
            logger.info("-- Generation %i --" % generation)
            for i in range(len(pop)):
                logger.debug("Individual %i (fitness %f):" % (i, pop[i].fitness.values[0]))
                logger.debug(pop[i])

            # Set the best "elite" individual on the beginning
            best_in_generation = tools.selBest(pop, 1)[0]
            pos_best_in_generation = 0
            for item in pop:
                if item.tree_is_equal(best_in_generation):
                    break
                pos_best_in_generation += 1
            tmp = pop[0]
            pop[0] = pop[pos_best_in_generation]
            pop[pos_best_in_generation] = tmp

            # display population summary
            fits = [ind.fitness.values[0] for ind in pop]
            length = len(pop)
            mean = sum(fits) / length
            sum2 = sum(x*x for x in fits)
            std = abs(sum2 / length - mean**2)**0.5
            logger.debug("Fitness: %s \nMin: %f Max: %f Avg: %f Std: %f \n" 
                            % (str(fits), min(fits), max(fits), mean, std) )
            logger.info('Best individual (fitness %f): ' % best_in_generation.fitness.values[0])
            logger.info(best_in_generation)
            
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
                    # Fitness values of the children must be recalculated later
                    del child1.fitness.values
                    del child2.fitness.values

            # Apply mutation on the offspring
            for mutant in offspring:
                # Mutate an individual with previously determined probability 
                if random.random() < mutation_probability:
                    toolbox.mutate(mutant)
                    # Fitness values of the mutants must be recalculated later
                    del mutant.fitness.values
        
            # Evaluate the individuals within offspring with an invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit

            # Elite individual should be saved on the first position
            best_off = tools.selBest(offspring, 1)[0]
            if( best_off.fitness.values[0] < pop[0].fitness.values[0]):
                pop[0] = best_off

            # The population is partially filled by the novel offsprings
            # that are unique among original population and the offspring
            # Remaining places are fill with unique element from old population
            pop_size = len(pop)
            filled = 1
            for off_ind in offspring:
                is_novel = True
                for i in range(0, len(pop)):
                    if off_ind.tree_is_equal(pop[i]):
                            is_novel = False
                            break
                if is_novel and filled < len(pop):
                    pop[filled] = off_ind
                filled += 1

            # Check if any of finishing criteria is meet
            # Criteria based on number of generations
            if max_number_generations > 0:
                if generation > max_number_generations:
                    break
            # Criteria based on elapsed time
            elapsed_time = datetime.now() - start_time
            if max_seconds_for_execution > 0:
                if elapsed_time.total_seconds() > max_seconds_for_execution:
                    break

        logger.info('GP algorithm finished.')
        output_file.write("GP algorithm finished at: %s\n" % datetime.now())
        logger.info("Execution time: %s Number of generations: %d" % (elapsed_time, generation-1))
        output_file.write("Execution time: %s Number of generations: %d\n" % (elapsed_time, generation-1))
        logger.info("Final solution (fitness: %f)" % pop[0].fitness.values)
        output_file.write("Final solution\n")
        logger.info(pop[0])
        output_file.write(str(pop[0]))
        output_file.write("Fitness: [%f]" % pop[0].fitness.values)
        logger.debug("Final population (size %d)\n"%len(pop))
        for i in range(len(pop)):
            logger.debug("Individual %i (fitness %f):" % (i, pop[i].fitness.values[0]))
            logger.debug(pop[i])
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



