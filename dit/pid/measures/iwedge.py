"""
The I_wedge measure, as proposed by Griffith et al.
"""

from ..pid import BasePID
from ... import Distribution
from ...algorithms import insert_meet
from ...multivariate import coinformation


__all__ = (
    'PID_GK',
)


class PID_GK(BasePID):
    """
    The Griffith et al partial information decomposition.

    This PID is known to produce negative partial information values.
    """

    _name = "I_∧"

    @staticmethod
    def _measure(d, sources, target):
        """
        Compute I_wedge(sources : target) = I(meet(sources) : target)

        Parameters
        ----------
        d : Distribution
            The distribution to compute i_wedge for.
        sources : iterable of iterables
            The source variables.
        target : iterable
            The target variable.

        Returns
        -------
        iwedge : float
            The value of I_wedge.
        """
        d = d.coalesce(sources + (target,))
        d = Distribution(d.outcomes, d.pmf, sample_space=d.outcomes)
        d = insert_meet(d, -1, d.rvs[:-1])
        return coinformation(d, [d.rvs[-2], d.rvs[-1]])
