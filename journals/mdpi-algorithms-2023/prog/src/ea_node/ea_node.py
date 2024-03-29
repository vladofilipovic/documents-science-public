"""
The :mod:`ea_node` module contains EaNodeInfo and EaNode classes.

EaNode class is an node of the mutation tree to be build and evaluated.
"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger

import random

from anytree import NodeMixin
from anytree import RenderTree, PostOrderIter
from anytree import PostOrderIter

from anytree.exporter import DotExporter

from utils.generate_formats_gp import anytree_node_name
from utils.generate_formats_gp import anytree_edge_attribute
from utils.generate_formats_gp import anytree_edge_type

from bitstring import BitArray

from functools import lru_cache 

from utils.collections_helper import remove_empty_set_occurences

class EaNodeInfo(object):
    """ Information about nodes of the EA Tree.
    """
    typeDescription = "EaNodeInfo"


class EaNode(EaNodeInfo, NodeMixin): 
    """ Node of the tree that is used in evolutionary algorithm.
    """
    
    def __init__(self, node_label, binary_tag, parent=None):
        """ Instance initialization.
        
        Args:
            node_label (str): Parameter `node_label`represents the label of the 
                node.
            binary_tag (:BitArray): Parameter `binary_tag` represents the
                binary number that is atached to node of the GaTree.
        """
        super(EaNodeInfo, self).__init__()
        self.node_label = node_label
        self.binary_tag = binary_tag
        self.parent = parent
        self.closest_node_in_tree = lru_cache(maxsize=1024)(self.closest_node_in_tree)

    def __repr__(self):
        """ Obtaining representation of the instance.

        Representation of the node instance is the whole tree formed by the 
        descendats of that nide instance.
    
        Returns:
            str: Representation of the instance.
        """
        s = self.tree_string_rep()
        s += '\n\r'
        s += self.tree_graphviz_rep()
        return s
    
    def __str__(self):
        """ Obtaining string representation of the instance.

        String representation of the node instance is the whole tree formed by 
        the descendants of that instance.

        Returns:
            str: String representation of the instance.
        """
        s = self.tree_string_rep()
        s += '\n\r'
        s += self.tree_graphviz_rep()
        return s
    
    def tree_string_rep( self ):
        """ Function for printing EA tree.

        Args:
            endS (str, optional): Parameter `endS` serve to decide what should be
                printed at the end of the method. Default value of this 
                parameter is new line.
        """
        s = u"\n"
        for pre, _, node in RenderTree(self):
            treestr = u"%s%s " % (pre, node.node_label)
            s += treestr.ljust( 10 ) + node.binary_tag.bin + u'\n'
        s += u'\n'
        return s
    
    def tree_graphviz_rep(self):
        s = ""
        dexp = DotExporter(self, 
            graph="graph",
            nodenamefunc=anytree_node_name,
            nodeattrfunc=lambda node: "shape=box",
            edgeattrfunc=anytree_edge_attribute,
            edgetypefunc=anytree_edge_type)
        for line in dexp:
            s += line + "\r\n"
        return s

    def attach_child(self, child):
        """ Function for adding child EA node.

        Args:
            child (EaNode): Parameter `child` is a EaNode that should be 
                attached as direct descendent of the current EaNode.
        """
        child.parent = self
        return

    def flip_node_label(self):
        """ Function for flipping the label of the node.
        
        If node label is finished with '+', its last character  will be flipped 
        to '-' and vice versa.
        """
        self.node_label = self.node_label.strip()
        if(self.node_label.endswith('+')):
            self.node_label = self.node_label[:-1] + '-'
        elif(self.node_label.endswith('-')): 
            self.node_label = self.node_label[:-1] + '+'
        return

    def tree_size(self):
        """ Function for obtaining size of the tree.
        
        Returns:
            size of the tree rooted with self.
        """
        return (len( self.descendants ) +1)

    def tree_node_at_position_postorder(self, position):
        """ Function for obtaining node in the tree at given position, where 
        nodes are visisted in postoreder maneer.
        
        Args:
            position (:int): Position of the node.
        
        Returns:
            node at given position. If position is too large, function will
                return None.
        """
        ret = None
        if( position == 0):
            ret = self
        else:
            j = 1
            for node in PostOrderIter(self):
                if( j== position):
                    ret = node
                    break
                else:
                    j += 1
        return ret

    def tree_node_ancesstor_find(self, label):
        """ Function for obtaining node in the tree, among ancestor nodes,
            that have adequate label.
        
        Args:
            label (:str): Label of node that is searched.
        
        Returns:
            ancesstor node with given label. If there is not such node among
            ancestors, function will return None.
        """
        ret = None
        anc = self 
        while(anc!= None):
            if(anc.node_label==label):
                ret = anc
                break
            else:
                anc = anc.parent
        return ret

    def tree_node_find(self, label):
        """ Function for obtaining node in the tree that have adequate label.
        
        Args:
            label (:str): Label of node that is searched.
        
        Returns:
            node with given label. If there is not such node in tree
            rooted with self, function will return None.
        """
        ret = None
        for node in PostOrderIter(self):
            if( node.node_label == label):
                return node
        return ret

    def tree_node_find_all(self, label):
        """ Function for obtaining set of nodes in the tree that have adequate label.
        
        Args:
            label (:str): Label of node that is searched.
        
        Returns:
            set of nodes with given label. If there is not such node in tree
            rooted with self, function will return empty set.
        """
        ret = set()
        for node in PostOrderIter(self):
            if( node.node_label == label):
                ret.add(node)
        return ret

    def children_set_binary_tags(self, labels):
        """ Set binary tag of all children according to label.
        
        Binary tag represents which mutations are activated and which are not.
        Hamming distance between binary tags of parent and child node should be 1.
        """
        for node in self.children:
            node.binary_tag.clear()
            node.binary_tag.append( self.binary_tag )
            current_label = node.node_label.strip()
            bit = -1
            if(current_label.endswith('+')):
                bit = 1
                current_label = current_label[:-1]
            elif(current_label.endswith('-')): 
                bit = 0
                current_label = current_label[:-1]
            if( bit != 1 and bit != 0):
                continue
            i = labels.index(current_label)
            if( i == -1):
                continue
            node.binary_tag[i] = bit
        return

    def tree_set_binary_tags(self, labels):
        """ Set binary tag of all descendants according to node label.
        
        Binary tag represents which mutations are activated and which are not.
        Hamming distance between binary tags of parent and child node should be 1.
        """
        self.children_set_binary_tags(labels)
        for node in self.children:
            node.tree_set_binary_tags(labels)
        return

    def tree_get_labels_contains(self):
        """ Obtain labels of all nodes that are within this tree.
        
        Returns:
            set: Set of labels of nodes within this tree.
        """
        ret = {*[]}
        for node in PostOrderIter(self):
            ret.add(node.node_label)
        return ret;

    def tree_get_plus_labels_contains(self):
        """ Obtain of all plus nodes that are within this tree.
        
        Returns:
            set: Set of plus nodes within this tree.
        """
        labels_within = self.tree_get_labels_contains()
        ret = {*[]}
        for lab in labels_within:
            if( lab[-1] == '+'):
                ret.add(lab)
        return ret;

    def tree_is_equal( self, another ):
        """ Finds the first difference between self and another tree.

        Args:
            another (EaNode): Parameter `another` indicate root node of
                another tree to be compared for equality
        
        Returns:
            Boolean: value that indicates if trees are equal.
        Note:
            This method requires that both trees have sorted siblings.
        """
        if( another is None ):
            return False
        if( self.node_label != another.node_label):
            return False
        if( self.children is None and another.children is None ):
            return True
        if( self.children is None and not(another.children is None) ):
            return False
        if( not (self.children is None) and another.children is None ):
            return False       
        num_children = len(self.children)
        a_num_children = len(another.children)
        if( num_children != a_num_children):
            return False
        for i in range(0,num_children):
            if( not self.children[i].tree_is_equal(another.children[i])):
                return False
        return True

    def tree_get_partition(self, partition):
        """ Function for obtaining partitions od the tree that is make by each
            of the plus nodes.
        
        Args:
            partition (dicitionary): Partition created so far.

        Returns:
            dicitionary: dictionary that have label of the plus node as key and
                a list of its partitions as value.
        """
        ret = partition
        if( self.node_label[-1]!='+' and self.node_label != "ooo"):
            return ret
        if( self.children is None):
            ret[self.node_label] = []
            return ret
        plus_sub_labels = self.tree_get_plus_labels_contains() 
        if( len(plus_sub_labels) == 0 
                or (len(plus_sub_labels)==1 and self.node_label in plus_sub_labels) ):
            ret[self.node_label] = []
            return ret
        l = []
        for x in self.children:
            l.append( x.tree_get_plus_labels_contains())
        ret[self.node_label] = l
        for x in self.children:
            ret = x.tree_get_partition(ret)
        ret2 = remove_empty_set_occurences(ret)
        return ret2


    def tree_rearrange_by_label(self, ascending = True):
        """ rearrange nodes of the tree so label of the sibling nodes are 
        sorted in given order.
        
        Args:
            ascending (Boolean, optional): Parameter `ascending` indicate 
                that nodes are arranged in ascending order, according to node 
                label. Default value for this parameter is True.                 
        """
        if( self.children is None):
            return
        num_children = len(self.children)
        ordered = []
        for i in range(0,num_children):
                if( ascending ):
                    if(len(ordered) == 0):
                        ordered.append( self.children[i] )
                    else:
                        j = 0
                        while(j<len(ordered) and self.children[i].node_label>ordered[j].node_label):
                            j+=1
                        ordered.insert(j,self.children[i])
                else:
                    if(len(ordered) == 0):
                        ordered.append(self.children[i] )
                    else:
                        j = 0
                        while(j<len(ordered) and self.children[i].node_label<ordered[j].node_label):
                            j+=1
                        ordered.insert(j,self.children[i])
        for x in ordered:
            x.parent = None
        for i in range(0,num_children):
            self.attach_child(ordered[i])
        for node in self.children:
            node.tree_rearrange_by_label(ascending)            
        return

    def tree_remove_node_by_label(self, label):
        """ Function for removing the first minus node within contained subtree.
        
        Args:
            label (string): Parameter `label` represents the label of minus node that should be removed 

        Returns:
            If removing takes place.

        """
        for node in PostOrderIter(self):
            if( node.node_label == label):
                anc_node = node.parent
                while(True and not(anc_node is None)):
                    if( node.node_label[:-1] == anc_node.node_label[:-1] 
                            and anc_node.node_label[:-1] ):
                        break
                    if( anc_node.parent is None):
                        break
                    anc_node = anc_node.parent
                for child in node.children:
                    child.parent = node.parent
                node.parent = None
                return True
        return False


    def children_compact_horizontal(self):
        """ Horizontal compaction of the children (direct descendents).
        
        Whenever there are two childs of the node that have the same label, tree
        should be compacted.
        """
        if( self.children is None):
            return
        num_children = len(self.children)
        to_remove = []
        for i in range(0,num_children):
            x =  self.children[i]
            for j in range(i+1, num_children):
                y =  self.children[j]
                if( not(i in to_remove) and x.node_label == y.node_label ):
                    to_remove.append(y)
                    for node in y.children:
                        node.parent = x
        if( not to_remove is None):
            for x in to_remove:
                x.parent = None
        return

    def tree_compact_horizontal(self):
        """ Horizontal compaction of the tree.
        
        Whenever there are two child of the node that have the same label, tree
        should be compacted.
        """
        self.children_compact_horizontal()
        for node in self.children:
            node.tree_compact_horizontal()
        return
        
    def tree_compact_vertical(self):
        """ Vertical compaction od the tree.

        Whenever there are parent and the child that have opposite labels, tree
        should be compacted.
        """
        compact_executed = True
        while(compact_executed): 
            compact_executed = False
            for node in self.descendants:
                if(node.is_leaf):
                    parent_node = node.parent
                    while(True and not(parent_node is None)):
                        n_s = node.node_label[-1]
                        p_s = parent_node.node_label[-1]
                        p_m = p_s == "+" and n_s == "-"
                        if( node.node_label[:-1] == parent_node.node_label[:-1] and p_m ):
                            for x in node.children:
                                x.parent = parent_node.parent
                            node.parent = None
                            compact_executed = True
                        if( parent_node == self or parent_node is None):
                            break
                        node = parent_node
                        parent_node = parent_node.parent
        return

    def tree_remove_incorrect_minus_nodes(self):
        """ Function for removing incorect minus nodes within contained subtree.
        
        Returns:
            Number of removed nodes.

        Note
            Minus node is incorrect if there is no relevant plus nodes up to 
            the root.

        """
        number_of_removed = 0
        for node in PostOrderIter(self):
            if( node.node_label[-1] == '-'):
                node_OK = False
                anc_node = node.parent
                while(True and not(anc_node is None)):
                    if( node.node_label[:-1] == anc_node.node_label[:-1] 
                    and anc_node.node_label[:-1] ):
                        node_OK = True
                        break
                    if( anc_node.parent is None):
                        break
                    anc_node = anc_node.parent
                if(not node_OK):
                    for child in node.children:
                        child.parent = node.parent
                    node.parent = None
                    number_of_removed += 1
        return number_of_removed;

    def closest_node_in_tree_ignore_unknowns( self, read ):
        """ Finds the closest node in the tree for the given read.
        
        Node is the closest according to metrics that is induced with Hamming
        distance.
        In this method, bitarray unknown_read within read element (that holds 
        information about unknown elements) is not consulted. 
        """
        closest = self
        closest_bit_array = self.binary_tag ^ read._binary_read 
        closest_distance = closest_bit_array.count(True)
        for node in PostOrderIter(self):
            current_bit_array = node.binary_tag ^ read._binary_read
            current_distance = current_bit_array.count(True)
            if( current_distance < closest_distance):
                closest = node
                closest_bit_array = current_bit_array
                closest_distance = current_distance
        return (closest, closest_distance)

    def closest_node_in_tree( self, read ):
        """ Finds the closest node in the tree for the given read.
        
        Node is the closest according to metrics that is induced with Hamming
        distance.
        This method consults information about unknown reads (that are stored 
        in BitArray unknown_read) within read element. 
        """
        len_r = read._binary_read.length
        num_unc_r = read._unknown_read.count(True) 
        weight = float(len_r-num_unc_r)/float(len_r)
        closest = self
        closest_bit_array = self.binary_tag ^ read._binary_read 
        mask = read._unknown_read.copy()
        mask.invert()
        logger.debug( "mask\t" + mask )
        closest_bit_array = closest_bit_array & mask
        closest_distance = closest_bit_array.count(True)*weight
        for node in PostOrderIter(self):
            current_bit_array = node.binary_tag ^ read._binary_read
            mask = read._unknown_read.copy()
            mask.invert() 
            current_bit_array &= mask
            current_distance = current_bit_array.count(True)*weight
            if( current_distance < closest_distance):
                closest = node
                closest_bit_array = current_bit_array
                closest_distance = current_distance
        return (closest, closest_distance)

    def tree_add_leaf(self, label):
        """ Function for adding leaf of the tree with specific label
        
        Args:
            label (string): Parameter `label`represents the label of the
                leaf to be added with suffix '+' or '-'.
        """
        leaf_bit_array = BitArray()
        leaf = EaNode(label, leaf_bit_array)
        # find the parent of the leaf node
        position = random.randint(0, len(self.descendants))
        if( position == 0):
            parent_of_leaf = self
        else:
            j = 1
            for node in PostOrderIter(self):
                if( j== position):
                    parent_of_leaf = node
                    break
                else:
                    j += 1    
        # attach leaf node
        parent_of_leaf.attach_child(leaf)
        self.tree_compact_vertical()
        self.tree_compact_horizontal()
        self.tree_rearrange_by_label()       
        return

    def tree_initialize(self, labels, size):
        """ Function for initialization od the tree.
        
        Args:
            labels (list): Parameter `labels`represents the list of the labels
                that are given to nodes with suffix '+' or '-'.
            size (:int): Parameter `size` represents nuber of the nodes in the 
                tree.
        """
        current_tree_size = 1
        probability_of_node_creation = 0.9
        for i in range( 2 * size ):
            if( random.random() < probability_of_node_creation):
                # create new leaf node
                label_to_insert = random.choice( labels ) + '+'
                leaf_bit_array = BitArray()
                leaf = EaNode(label_to_insert, leaf_bit_array)
                # find the parent of the leaf node
                position = random.randint(0, current_tree_size)
                if( position == 0):
                    parent_of_leaf = self
                else:
                    j = 1
                    for node in PostOrderIter(self):
                        if( j== position):
                            parent_of_leaf = node
                            break
                        else:
                            j += 1    
                # attach leaf node
                parent_of_leaf.attach_child(leaf)
                # reverse node label, if necessary
                node = leaf.parent
                while( node.parent != None):
                    if( leaf.node_label == node.node_label):
                        leaf.flip_node_label()
                        break
                    if( leaf.node_label[:-1] == node.node_label[:-1]):
                        break
                    node = node.parent
                current_tree_size += 1 
                # delete leaf is label is duplicate within siblings
                for node in leaf.parent.children:
                    if( node.node_label == leaf.node_label and node != leaf):
                        leaf.parent = None;
                        current_tree_size -= 1
                        break
                if( i > size ):
                    probability_of_node_creation *= 0.7
        self.tree_compact_vertical()
        self.tree_compact_horizontal()
        self.tree_rearrange_by_label()
        self.tree_set_binary_tags(labels)
        return




