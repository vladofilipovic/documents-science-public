"""Questo modulo contiene le funzioni per il calcolo della funzione likelihood,
    evaluate_dollo_node_Evaluation e' la funzione principale e 
    sub evaluation e' la sotto funzione che prende una riga della matrice
    e il profilo genetico di un nodo.
    final matrix restituisce la matrice inferita E associata al valore likelihood di un albero
"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import numpy as np

from utils.logger import logger

from reads.read_element import ReadElement

from bitstring import BitArray
from anytree import RenderTree
import math

from functools import lru_cache


def evaluate_dollo_k_likelihood(reads,alpha,beta,individual):
    """ Evaluation of the individual by likelihood calculation. 
    Based on two criteria: 
    1) value of the likelihood between individual and relevant reads 
    2) length of the individual
    3) height of the individual 

    Args:
        reads (numpy 2D array): matrix with values 0,1,2.
        alpha: probability of false negative
        beta: probability of false positive
        individual (DoloNode): individual that should be evaluated.
    Returns:            
        objection value of the individual to be evaluated.    
    """

    likelihood=0
    read_count = len(reads)
    for read in reads:
        result={}
        for pre,_,node in RenderTree(individual):
            value=sub_evaluate(node.binary_tag.bin,read,alpha,beta)
            result[value]=node.binary_tag.bin
        max_single=max(result.keys())/read_count
        likelihood+=max_single
    individual_node_count = individual.tree_size()
    individual_height = individual.height
    objection_value = - likelihood + individual_node_count / (read_count * 1000) + individual_height / (read_count * 100000)
    return [objection_value]

def sub_evaluate(node_bin_tag, read, alpha, beta):

    likelihood=0
    for j in range(len(read)):
        if read[j] == 0:
            if node_bin_tag[j] == '0':
                likelihood += 1-beta
            elif node_bin_tag[j] == '1':
                likelihood += alpha
            else:
                raise ValueError("Error!" + "\n" 
                        + "reason:  node_bin_tag[j] is not correct" + "\n" 
                        + "node_bin_tag: " + "\n", node_bin_tag + "\n" 
                        + "j: " +  j + "\n" ) 
        elif read[j] == 1:
            if node_bin_tag[j] == '0':
                likelihood += beta
            elif node_bin_tag[j] == '1':
                likelihood += 1-alpha
            else:
                raise ValueError("Error!" + "\n" 
                        + "reason:  node_bin_tag[j] is not correct" + "\n" 
                        + "node_bin_tag: " + "\n", node_bin_tag + "\n" 
                        + "j: " +  j + "\n" ) 
        elif read[j] == 2:
            likelihood += 0
    return likelihood


@lru_cache(maxsize=8192, typed=True)
def sub_evaluate_bin(node,read,alpha,beta):

    likelihood=0
    for j in range(len(read._binary_read)):
        if read._binary_read.bin[j] == '0':
            if node[j] == '0':
                likelihood+=math.log(1-beta)
            elif node[j] == '1':
                likelihood+=math.log(alpha)
            elif node[j] == '-1':
                raise ValueError("Error!" + "\n" 
                        + "reason:  node[j] == '-1'" + "\n" 
                        + "node: " + "\n", node + "\n" 
                        + "j: " +  j + "\n" ) 
        elif read._binary_read.bin[j] == '1':
            if node[j] == '0':
                likelihood+=math.log(beta)
            elif node[j] == '1':
                likelihood+=math.log(1-alpha)
            elif node[j] == '-1':
                raise ValueError("Error!" + "\n" 
                        + "reason:  node[j] == '-1'" + "\n" 
                        + "node: " + "\n", node + "\n" 
                        + "j: " +  j + "\n" ) 
        elif read._binary_read.bin[j] == '2':
            likelihood+=0
    return likelihood
    
