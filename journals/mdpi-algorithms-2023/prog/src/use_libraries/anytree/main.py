""" This module contains an example how to use anytree
library.

"""

import path
import sys
directory = path.Path(__file__).abspath()
sys.path.append(directory.parent.parent)

from utils.logger import logger
from utils.logger import ensure_dir 

OUTPUT_DIR = 'outputs'

from anytree import AnyNode, RenderTree


def main():    
    """ This function is an entry  point of the application.
    """
    ensure_dir(OUTPUT_DIR)
    root = AnyNode(id="root")
    s0 = AnyNode(id="sub0", parent=root)
    s0b = AnyNode(id="sub0B", parent=s0, foo=4, bar=109)
    s0a = AnyNode(id="sub0A", parent=s0)
    s1 = AnyNode(id="sub1", parent=root)
    s1a = AnyNode(id="sub1A", parent=s1)
    s1b = AnyNode(id="sub1B", parent=s1, bar=8)
    s1c = AnyNode(id="sub1C", parent=s1)
    s1ca = AnyNode(id="sub1Ca", parent=s1c)
    root
    logger.debug(RenderTree(root))
    return

# this means that if this script is executed, then 
# main() will be executed
if __name__ == '__main__':
    main()

