""" The :mod:`dollo_node_evaluation_operators` module contains operators
for evaluation of DolloKNode individuals.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

import numpy as np

from functools import lru_cache 

from bitstring import BitArray

from reads.read_element import ReadElement

def evaluate_dollo_k_direct_2ba_falsePN_ignored(reads, alpha, beta, individual):
    """ Natural evaluation of the individual. 
    Based on three criteria: 
    1) number of exact/full matches of the reads among individual leaves
    2) number of different positions between reads and closest individual leaves (and recording those positions)
    3) length of the individual
    4) height of the individual 
    Full matches should be maximal, different positions and length should be minimal
    Doesn't count false positives.

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    num_full_match = 0
    num_dif_pos = 0
    read_count = len(reads)
    read_length = len(reads[0]._binary_read)
    united_mask = BitArray(read_length)
    for read in reads:
        (l, mask) = closest_leave( individual, read._binary_read )
        dif_pos = mask.count(True)
        if dif_pos == 0:
            num_full_match += 1
        num_dif_pos += dif_pos 
        united_mask |= mask
    individual_node_count = individual.tree_size()
    individual_height = individual.height
    objection_value = num_dif_pos - num_full_match / (read_count * 10) + individual_node_count / (read_count * 1000) + individual_height / (read_count * 100000)
    return [objection_value]

def evaluate_dollo_k_direct_012_falsePN_ignored(reads, alpha, beta, individual):
    """ Direct evaluation of the individual. 
    Based on three criteria: 
    1) number of exact/full matches of the reads among individual leaves
    2) number of different positions between reads and closest individual leaves (and recording those positions)
    3) length of the individual
    4) height of the individual 
    Full matches should be maximal, different positions and length should be minimal
    Doesn't count false negatives nor false positives.

    Args:
        reads (numpy 2D array): matrix with values 0,1,2.
        alpha: probability of false negative
        beta: probability of false positive
        individual (DoloNode): individual that should be evaluated.
    Returns:            
        objection value of the individual to be evaluated.    
    """
    num_full_match = 0
    num_dif_pos = 0
    shape = reads.shape
    read_count = shape[0]
    read_length = shape[1]
    united_mask = BitArray(read_length)
    for i in range(read_count):
        row = BitArray(read_length)
        for j in range(read_length):
            if reads[i,j] != 2:
                if reads[i,j] == 1:
                    row[j] = True
        (l, mask) = closest_leave( individual, row )
        dif_pos = mask.count(True)
        if dif_pos == 0:
            num_full_match += 1
        num_dif_pos += dif_pos 
        united_mask |= mask
    individual_node_count = individual.tree_size()
    individual_height = individual.height
    objection_value = num_dif_pos - num_full_match / (read_count * 10) + individual_node_count / (read_count * 1000) + individual_height / (read_count * 100000)
    return [objection_value]

def closest_leave(individual, bitarr):
    diff_mask = BitArray(len(bitarr))
    diff_mask.invert()
    sel_leave = None
    for leave in individual.leaves:
        lbitarr = leave.binary_tag
        rbitarr = bitarr ^ lbitarr
        if rbitarr.count(True) < diff_mask.count(True):
            sel_leave = leave
            diff_mask = rbitarr
    return (sel_leave, diff_mask)


def assign_reads_to_dollo_k(root, reads):
    """ Assigns all the reads to the closest nodes in the tree,
    respectively.
    
    Args:
        root (DolloKNode): root of the tree to whose nodes reads should be assigned.
        reads (list): list of the reads that should be assigned to various nodes in the tree.

    Returns:            
        list that contains two components: 
            1) list of the asignments  - list of pairs (node, read);
            2) sum of the distances among reads and the closest nodes that
            are assigned to those reads respectively.
    
    Note:
        Function uses the func:`~DolloKNode.closest_node_in_tree` function 
        from the :mod:`ga_node` module.
    """
    total_distance = 0
    complete_assignment = {}
    for read in reads:
        (node, d) = root.closest_node_in_tree( read )
        complete_assignment[read] = node
        total_distance += d
    return (complete_assignment, total_distance)    
    
@lru_cache(maxsize=8192, typed=True)
def dollo_k_closest_node_distance(individual, read):
    """ Finds the closest node within the tree for the given read, as well
        as distance betwwen that node and read.
    
    Args:
        individual (DoloNode): individual that represents root of the node.
        read : read that should be assigned to the node in the tree.

    Notes:    
        Node is the closest according to metrics that is induced with Hamming
        distance.
        This method consults information about unknown reads (that are stored 
        in bitarray unknown_read) within read element. 
    """
    (c_n,d) = individual.closest_node_in_tree(read)
    return (c_n,d)

def dollo_evaluate_direct_only_level0(reads, alpha, beta, individual):
    """ Evaluation of the individual. Doesnt't count false positives.

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = 0
    for read in reads:
        (node, d) = dollo_k_closest_node_distance(individual,read)
        objection_value += d
    return objection_value

def dollo_evaluate_direct_only_level1(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        one position.        

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = 0
    for read in reads:
        for i in range(0,read._binary_read.length):
            if( read._binary_read[i]):
                read2 = BitArray(read._binary_read)
                read2[i]=False
                re2 = ReadElement("XXX2", read2, read._unknown_read)
                (node, d) = dollo_k_closest_node_distance(individual,re2)
                objection_value += d
    return objection_value

def dollo_evaluate_direct_only_level2(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        two positions.        
    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = 0
    for read in reads:
        for i in range(0,read._binary_read.length):
            for j in range(i+1, read._binary_read.length):
                if( read._binary_read[i] and read._binary_read[j]):
                    read2 = BitArray(read._binary_read)
                    read2[i]=False
                    read2[j]=False
                    re2 = ReadElement("XXX2", read2, read._unknown_read)
                    (node, d) = dollo_k_closest_node_distance(individual,re2)
                    objection_value += d 
    return objection_value

def dollo_evaluate_direct_only_level3(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        three positions.        
    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = 0
    for read in reads:
        for i in range(0,read._binary_read.length):
            for j in range(i+1, read._binary_read.length):
                for k in range(j+1, read._binary_read.length):
                    if( read._binary_read[i] and read._binary_read[j] and read._binary_read[k]):
                        read2 = BitArray(read._binary_read)
                        read2[i]=False
                        read2[j]=False
                        read2[k]=False
                        re2 = ReadElement("XXX2", read2, read._unknown_read)
                        (node, d) = dollo_k_closest_node_distance(individual,re2)
                        objection_value += d * alpha * alpha * alpha
    return objection_value

def dollo_evaluate_direct_level0(reads, alpha, individual):
    """ Evaluation of the individual. Doesnt't count false positives.

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    return dollo_evaluate_direct_only_level0(reads, alpha, individual)

def dollo_evaluate_direct_level1(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        one position.        

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = dollo_evaluate_direct_only_level0(reads, alpha, beta, individual) * (1-alpha)
    objection_value += dollo_evaluate_direct_only_level1(reads, alpha, beta, individual) * alpha
    return objection_value

def dollo_evaluate_direct_level2(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        two positions.        
    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = dollo_evaluate_direct_only_level0(reads, alpha, beta, individual) * (1-alpha-alpha*alpha)
    objection_value += dollo_evaluate_direct_only_level1(reads, alpha, beta, individual) * alpha
    objection_value += dollo_evaluate_direct_only_level2(reads, alpha, beta, individual) * alpha * alpha
    return objection_value

def dollo_evaluate_direct_level3(reads, alpha, beta, individual):
    """ Evaluation of the individual. Takes into account false positives on
        three positions.        
    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        objection value of the individual to be evaluated.    
    """
    objection_value = dollo_evaluate_direct_only_level0(reads, alpha, beta, individual) * (1-alpha-alpha*alpha-alpha*alpha*alpha)
    objection_value += dollo_evaluate_direct_only_level1(reads, alpha, beta,  individual) * alpha
    objection_value += dollo_evaluate_direct_only_level2(reads, alpha, beta, individual) * alpha * alpha
    objection_value += dollo_evaluate_direct_only_level3(reads, alpha, beta, individual) * alpha * alpha * alpha
    return objection_value

def evaluate_dollo_node_direct(reads, individual, alpha, beta):
    """ Evaluation of the individual.

    Args:
        reads (list): list of the reads that should be assigned to various nodes in the tree.
        individual (DoloNode): individual that should be evaluated.
        alpha: probability of false positive
    Returns:            
        pair where first element is objection value of the individual to be
            evaluated.    
    """
    return (dollo_evaluate_direct_level1(reads, individual, alpha, beta),)    

