"""
The functional common information.
"""

from collections import deque
from itertools import combinations

from ..distconst import insert_rvf, modify_outcomes
from ..helpers import flatten, normalize_rvs
from ..math import close
from ..utils import partitions

from .entropy import entropy
from .dual_total_correlation import dual_total_correlation

__all__ = ['functional_common_information']

def add_partition(dist, part):
    """
    Add a function of the joint distribution.

    Parameters
    ----------
    dist : Distribution
        The distribution to add a function to.
    part : list of lists
        A partition of the outcomes. Each outcome will be mapped to the id of
        its partition element.

    Returns
    -------
    dist : Distribution
        The original `dist` with the function defined by `part` added.
    """
    invert_part = {e: (i,) for i, es in enumerate(part) for e in es}
    dist = insert_rvf(dist, lambda j: invert_part[j])
    return dist

def functional_markov_chain_naive(dist, rvs=None, crvs=None, rv_mode=None): # pragma: no cover
    """
    Add the smallest function of `dist` which renders `rvs` independent.

    Parameters
    ----------
    dist : Distribution
        The distribution for which the smallest function will be constructed.
    rvs : list, None
        A list of lists. Each inner list specifies the indexes of the random
        variables used to calculate the total correlation. If None, then the
        total correlation is calculated over all random variables, which is
        equivalent to passing `rvs=dist.rvs`.
    crvs : list, None
        A single list of indexes specifying the random variables to condition
        on. If None, then no variables are conditioned on.
    rv_mode : str, None
        Specifies how to interpret `rvs` and `crvs`. Valid options are:
        {'indices', 'names'}. If equal to 'indices', then the elements of
        `crvs` and `rvs` are interpreted as random variable indices. If equal
        to 'names', the the elements are interpreted as random variable names.
        If `None`, then the value of `dist._rv_mode` is consulted, which
        defaults to 'indices'.

    Returns
    -------
    d : Distribution
        The distribution `dist` with the additional variable added to the end.
    """
    rvs, crvs, rv_mode = normalize_rvs(dist, rvs, crvs, rv_mode)
    outcomes = dist.outcomes
    f = [len(dist.rvs)]
    parts = partitions(outcomes)
    dists = [ add_partition(dist, part) for part in parts ]
    B = lambda d: dual_total_correlation(d, rvs, crvs+f, rv_mode)
    dists = [ d for d in dists if close(B(d), 0) ]
    return min(dists, key=lambda d: entropy(d, rvs=f, rv_mode=rv_mode))

def functional_markov_chain(dist, rvs=None, crvs=None, rv_mode=None):
    """
    Add the smallest function of `dist` which renders `rvs` independent.

    Parameters
    ----------
    dist : Distribution
        The distribution for which the smallest function will be constructed.
    rvs : list, None
        A list of lists. Each inner list specifies the indexes of the random
        variables used to calculate the total correlation. If None, then the
        total correlation is calculated over all random variables, which is
        equivalent to passing `rvs=dist.rvs`.
    crvs : list, None
        A single list of indexes specifying the random variables to condition
        on. If None, then no variables are conditioned on.
    rv_mode : str, None
        Specifies how to interpret `rvs` and `crvs`. Valid options are:
        {'indices', 'names'}. If equal to 'indices', then the elements of
        `crvs` and `rvs` are interpreted as random variable indices. If equal
        to 'names', the the elements are interpreted as random variable names.
        If `None`, then the value of `dist._rv_mode` is consulted, which
        defaults to 'indices'.

    Returns
    -------
    d : Distribution
        The distribution `dist` with the additional variable added to the end.

    Notes
    -----
    The implimentation of this function is quite slow. It is approximately
    doubly exponential in the size of the sample space. This method is several
    times faster than the naive method however. It remains an open question as
    to whether a method to directly construct this variable exists (as it does
    with the GK common variable, minimal sufficient statistic, etc).
    """
    rvs, crvs, rv_mode = normalize_rvs(dist, rvs, crvs, rv_mode)

    dist = modify_outcomes(dist, lambda x: tuple(x))

    part = frozenset([ frozenset([o]) for o in dist.outcomes ]) # make copy

    W = [dist.outcome_length()]

    H = lambda d: entropy(d, W, rv_mode=rv_mode)
    B = lambda d: dual_total_correlation(d, rvs, crvs+W, rv_mode)

    optimal_b = dual_total_correlation(dist, rvs, crvs, rv_mode)

    initial = add_partition(dist, part)
    optimal = (H(initial), initial)

    queue = deque([part])

    checked = set()

    while queue: # pragma: no branch
        part = queue.popleft()

        checked.add(part)

        d = add_partition(dist, part)

        if close(B(d), 0):

            h = H(d)

            if h <= optimal[0]:
                optimal = (h, d)

            if close(h, optimal_b):
                break

            new_parts = [frozenset([ p for p in part if p not in pair ] +
                                   [pair[0]|pair[1]])
                         for pair in combinations(part, 2) ]
            new_parts = sorted([ part for part in new_parts if part not in checked ], key=lambda p: sorted(map(len, p)))
            queue.extendleft(new_parts)

    return optimal[1]

def functional_common_information(dist, rvs=None, crvs=None, rv_mode=None):
    """
    Compute the functional common information, F, of `dist`. It is the entropy
    of the smallest random variable W such that all the variables in `rvs` are
    rendered independent conditioned on W, and W is a function of `rvs`.

    Parameters
    ----------
    dist : Distribution
        The distribution from which the functional common information is
        computed.
    rvs : list, None
        A list of lists. Each inner list specifies the indexes of the random
        variables used to calculate the total correlation. If None, then the
        total correlation is calculated over all random variables, which is
        equivalent to passing `rvs=dist.rvs`.
    crvs : list, None
        A single list of indexes specifying the random variables to condition
        on. If None, then no variables are conditioned on.
    rv_mode : str, None
        Specifies how to interpret `rvs` and `crvs`. Valid options are:
        {'indices', 'names'}. If equal to 'indices', then the elements of
        `crvs` and `rvs` are interpreted as random variable indices. If equal
        to 'names', the the elements are interpreted as random variable names.
        If `None`, then the value of `dist._rv_mode` is consulted, which
        defaults to 'indices'.

    Returns
    -------
    F : float
        The functional common information.
    """
    d = functional_markov_chain(dist, rvs, crvs, rv_mode)
    return entropy(d, [dist.outcome_length()])