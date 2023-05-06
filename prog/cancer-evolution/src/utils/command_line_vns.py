""" The :mod:`command_line_vns` module is used for obtaining execution parameters for execution of the 
    variable neighborhood search algorithm.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger


import re

default_parameters = {'InputFile': 'XXX.in', 
                    'InputFormat': '2ba',
                    'RandomSeed': -1,
                    'InitializationMaxFillFactor': 1.8,
                    'DolloK': 2,
                    'Alpha': 0.35,
                    'Beta': 0.005,
                    'EvaluationType': 'direct-012',
                    'MaxNumberIterations': 10,
                    'MaxTimeForExecutionInSeconds': 0 }

def get_execution_parameters(options, args, parameters):
    """  Obtains execution parameters.

    Args:
        parameters (:dictionary) : Parameter 'parameters' represent initial 
            values of execution parameters
        options : Parameter `options` represents options of the execution.
        args (:list): Parameter `args` represents the argument list.
    Returns:
        dictionary: Execution parameters after reading command line.
    """

    if len(args) == 0:
        raise ValueError("Error!\nCommand line parameters:\n" + usage_explanation(parameters))
    if len(args) > 300:
        raise ValueError("Error!\nCommand line parameters:\n" + usage_explanation(parameters))

    if options.debug:
        logger.debug( 'option debug is activated')
    else:
        logger.debug( 'option debug is deactivated')       
    if options.verbose:
        print ('option verbose is activated')
    else:
        logger.debug( 'option verbose is deactivated')           
    if options.debug or options.verbose:
        logger.debug("Command-line parameters:")
        for arg in args:
            logger.debug( arg + " ")
        logger.debug('\n')     
    
    inputFile_re = re.compile(r'[I|i]nput[F|f]ile=.*/.*')
    inputFormat_re = re.compile(r'[I|i]nput[F|f]ormat=*')
    randomSeed_re = re.compile(r'[R|r]andom[S|s]eed=[0-9]+')
    initializationMaxFillFactor_re = re.compile(r'[I|i]nitialization[M|m]ax[F|f]ill[F|f]actor=[0-9].[0-9]+')
    dolloK_re = re.compile(r'[D|d]ollo[K|k]=[0-9]+')
    alpha_re = re.compile(r'[A|a]lpha=[0-9].[0-9]+')
    beta_re = re.compile(r'[B|b]eta=[0-9].[0-9]+')    
    evaluationType_re = re.compile(r'[E|e]valuation[T|t]ype=.*')
    maxNumberIterations_re = re.compile(r'[M|m]ax[N|n]umber[I|i]terations=[0-9]+')
    maxTimeForExecutionInSeconds_re = re.compile(r'[M|m]ax[T|t]ime[F|f]or[E|e]xecution[I|i]n[S|s]econds=[0-9]+')

    inputFileIsSet = False
    for arg in args:
        if inputFile_re.match(arg):
            parameters['InputFile'] = arg.split('=')[1]
            parameters['InputFormat'] = parameters['InputFormat'].split('.')[-1]
            inputFileIsSet = True
            break
    if not inputFileIsSet:
        raise ValueError("Error!\nCommand line parameters:\n" + usage_explanation(parameters))
    for arg in args:    
        if inputFormat_re.match(arg) :
            parameters['InputFormat'] = arg.split('=')[1]
            break
    for arg in args:    
        if randomSeed_re.match(arg) :
            parameters['RandomSeed'] = arg.split('=')[1]
            break        
    for arg in args:    
        if initializationMaxFillFactor_re.match(arg) :
            parameters['InitializationMaxFillFactor'] = arg.split('=')[1]
            break
    for arg in args:    
        if dolloK_re.match(arg) :
            parameters['DolloK'] = arg.split('=')[1]
            break        
    for arg in args:    
        if alpha_re.match(arg) :
            parameters['Alpha'] = arg.split('=')[1]
            break        
    for arg in args:    
        if beta_re.match(arg) :
            parameters['Beta'] = arg.split('=')[1]
            break        
    for arg in args:
        if evaluationType_re.match(arg):
            parameters['EvaluationType'] = arg.split('=')[1]
            break
    for arg in args:    
        if maxNumberIterations_re.match(arg) :
            parameters['MaxNumberIterations'] = arg.split('=')[1]
            break
    for arg in args:    
        if maxTimeForExecutionInSeconds_re.match(arg) :
            parameters['MaxTimeForExecutionInSeconds'] = arg.split('=')[1]
            break

    return parameters

def usage_explanation(parameters):
    """  Create usage explanation text.

    Args:
        parameters : Parameter `parameters` is a dictionary that represents parameters of the execution.
    """
    ret = ""
    ret += "InputFile=<file_name>\t(mandatory, string) \n"
    ret += "InputFormat='2ba'|'012'\t(optional, string - default value: '" + parameters['InputFormat'] + "')\n"
    ret += "RandomSeed=<seed_value>\t(optional, integer - default value: " + str(parameters['RandomSeed']) + ")\n"
    ret += "\t Note: if parameter RandomSeed is less or equal to 0, random number sequence will be initialized with current time\n"
    ret += "InitializationMaxFillFactor=<fill_factor>\t(optional, float - default value: '" + str(parameters['InitializationMaxFillFactor']) + "')\n"
    ret += "DolloK=<k_value>\t(optional, integer - default value: " + str(parameters['DolloK']) + ")\n"
    ret += "Alpha=<alpha_value>\t(optional, float - default value: '" + str(parameters['Alpha']) + "')\n"
    ret += "\t Note: Alpha is false negative rate of mutation. \n"
    ret += "\t Conditional probability for read to be 0 if final_outcome is 1 is equal to Alpha. \n"
    ret += "\t Conditional probability for read to be 1 if final_outcome is 1 is equal to 1-Alpha. \n"
    ret += "Beta=<beta_value>\t(optional, float - default value: '" + str(parameters['Beta']) + "')\n"
    ret += "\t Note: Beta is false positive rate of mutation. \n"
    ret += "\t Conditional probability for read to be 0 if final_outcome is 0 is equal to 1-Beta. \n"
    ret += "\t Conditional probability for read to be 1 if final_outcome is 0 is equal to Beta. \n"
    ret += "EvaluationType='direct-012'|'direct-2ba'|'likelihood-012'\t(optional, string - default value: '" + parameters['EvaluationType'] + "')\n"
    ret += "MaxNumberIterations=<max_num>\t(optional, integer - default value: '" + str(parameters['MaxNumberIterations']) + "')\n"
    ret += "\t Note: if parameter MaxNumberIterations is 0, number of iterations will not be consult as finish criteria\n"
    ret += "MaxTimeForExecutionInSeconds=<max_sec>\t(optional, integer - default value: '" + str(parameters['MaxTimeForExecutionInSeconds']) + "')\n"
    ret += "\nOptions: --debug --verbose "
    return ret
    