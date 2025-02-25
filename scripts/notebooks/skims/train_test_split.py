import os
os.environ['KMP_WARNINGS'] = 'off'
import sys
import git

import uproot as ut
import awkward as ak
import numpy as np
import math
import vector
import sympy as sp

import re
from tqdm import tqdm
import timeit
import re

sys.path.append( git.Repo('.', search_parent_directories=True).working_tree_dir )
from utils import *

from utils.notebookUtils import Notebook, required, dependency
from utils.notebookUtils.driver.run_skim import RunSkim

import json

# %%
def main():
    notebook = Notebook.from_parser()
    notebook.hello()
    notebook.run()

class Notebook(RunSkim):
    @staticmethod
    def add_parser(parser):
        parser.add_argument("--train", default=0.8, type=float)
        return parser

    def randomize_split(self, trees):
        (trees).apply(
            lambda t : t.extend(
                _random_split= ak.from_numpy( np.random.random(size=len(t)) < self.train )
            )
        )

    def write_split(self, trees):
        train_split = trees.copy()
        train_split = train_split.apply(EventFilter(f'train', filter=lambda t : t._random_split, cutflow=False))

        study.quick( 
            train_split,
            varlist=['jet_pt[:,0]']
        )

        def move_to_dir(f, dir):
            # f = fc.cleanpath(f)
            f =  f.replace('/output/',f'/{dir}/')
            f = f.replace('mkolosov','ekoenig')
            return f

        train_split.write(lambda f : move_to_dir(f, 'train'))

        test_split = trees.copy()
        test_split = test_split.apply(EventFilter(f'test', filter=lambda t : ~t._random_split, cutflow=False))

        study.quick( 
            test_split,
            varlist=['jet_pt[:,0]']
        )
        test_split.write(lambda f : move_to_dir(f, 'test'))


if __name__ == '__main__':
    main()