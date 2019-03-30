#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'Kevin M. Jablonka'
__copyright__ = 'MIT License'
__maintainer__ = 'Kevin M. Jablonka'
__email__ = 'kevin.jablonka@epfl.ch'
__version__ = '0.1.0'
__date__ = '25.03.19'
__status__ = 'First Draft, Testing'

from glob import glob
import os
import functools
from .rmsd import parse_periodic_case, rmsd
from pymatgen import Structure
import numpy as np
from scipy import stats
import concurrent.futures
from sklearn.neighbors import KernelDensity
from pymatgen.analysis.graphs import StructureGraph
from pymatgen.analysis.local_env import JmolNN
import logging
logger = logging.getLogger()


def get_structure_list(directory: str, extension: str = 'cif') -> list:
    """
    :param directory: path to directory
    :param extension: fileextension
    :return:
    """
    logger.info('getting structure list')
    if extension:
        structure_list = glob(
            os.path.join(directory, ''.join(['*.', extension])))
    else:
        structure_list = glob(os.path.join(directory, '*'))
    return structure_list


@functools.lru_cache(maxsize=128, typed=False)
def get_rmsd(structure_a: Structure, structure_b: Structure) -> float:
    p_atoms, P, q_atoms, Q = parse_periodic_case(structure_a, structure_b)
    result = rmsd(P, Q)
    return result


def closest_index(array, target):
    return np.argmin(np.abs(array - target))


def kl_divergence(array_1, array_2, len=20):
    """
    KL divergence could be used a measure of covariate shift.
    """
    a = np.histogram(array_1, bins=len)
    b = np.histogram(array_2, bins=len)

    return stats.entropy(a, b)


def tanimoto_distance(array_1, array_2):
    """
    Continuous form of the Tanimoto distance measure.
    Args:
        array_1:
        array_2:

    Returns:

    """
    xy = np.dot(array_1, array_2)
    return xy / (np.linalg.norm(array_1) + np.linalg.norm(array_2) - xy)


def get_hash(structure: Structure):
    """
    This gets hash for the Niggli reduced cell

    Args:
        structure: pymatgen structure object

    Returns:

    """
    crystal = structure.get_reduced_structure()
    nn_strategy = JmolNN()
    sgraph_a = StructureGraph.with_local_env_strategy(crystal, nn_strategy)
    graph_hash = str(hash(sgraph_a.graph))
    comp_hash = str(hash(str(crystal.composition)))
    density_hash = str(hash(crystal.density))
    return graph_hash + comp_hash + density_hash
