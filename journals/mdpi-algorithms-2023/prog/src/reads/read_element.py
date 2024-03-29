""" The :mod:`read_element` module contains ReadInfo and ReadElement classes.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

class ReadInfo(object):
    """ Represents information about reads.
    
    """
    typeDescription = "ReadInfo"


class ReadElement(ReadInfo):  
    """ Represents one read.
    """
    
    def __init__(self, read_label, binary_read, unknown_read):
        """ Instance initialization.
        
        Args:
            read_label (str): Parameter `read_label`represents the label of the 
                read.
            binary_read (:BitArray): Parameter `binary_read` represents the
                binary number that indicate which mutation occures.
            unknown_read (:BitArray): Parameter `unknown_read` represents the
                binary number that indicate position where read is unknown.
        """
        super(ReadInfo, self).__init__()
        self._read_label = read_label
        self._binary_read = binary_read
        self._unknown_read = unknown_read
    
    def __repr__(self):
        """ Obtaining representation of the instance.

        Returns:
            str: Representation of the instance.
        """
        return "%5s: %s [%s]" % (self._read_label, self._binary_read.bin, self._unknown_read.bin)

    def __str__(self):
        """ Obtaining string representation of the instance.

        Returns:
            str: String representation of the instance.
        """
        return "%5s: %s [%s]" % (self._read_label, self._binary_read.bin, self._unknown_read.bin)

        
    
