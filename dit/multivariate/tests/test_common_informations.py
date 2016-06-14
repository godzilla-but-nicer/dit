"""
Tests for the various common informations.
"""

from nose.plugins.attrib import attr
from nose.tools import assert_less_equal

from dit import random_distribution
from dit.multivariate import (gk_common_information as K,
                              dual_total_correlation as B,
                              wyner_common_information as C,
                              exact_common_information as G,
                              functional_common_information as F,
                              mss_common_information as M
                             )


@attr('scipy')
@attr('slow')
def test_cis1():
    """
    Test that the common informations are ordered correctly.
    """
    for d in [random_distribution(2, 3) for _ in range(5)]:
        k = K(d)
        b = B(d)
        c = C(d)
        g = G(d)
        f = F(d)
        m = M(d)
        yield assert_less_equal, k, b + 1e-6
        yield assert_less_equal, b, c + 1e-6
        yield assert_less_equal, c, g + 1e-6
        yield assert_less_equal, g, f + 1e-6
        yield assert_less_equal, f, m + 1e-6

@attr('scipy')
@attr('slow')
def test_cis2():
    """
    Test that the common informations are ordered correctly.
    """
    for d in [random_distribution(3, 2) for _ in range(5)]:
        k = K(d)
        b = B(d)
        c = C(d)
        g = G(d)
        f = F(d)
        m = M(d)
        yield assert_less_equal, k, b + 1e-6
        yield assert_less_equal, b, c + 1e-6
        yield assert_less_equal, c, g + 1e-6
        yield assert_less_equal, g, f + 1e-6
        yield assert_less_equal, f, m + 1e-6