"""Built-in background models."""

from __future__ import annotations

__all__: list[str] = []

from dataclasses import KW_ONLY, dataclass
from typing import TYPE_CHECKING

from stream_ml.core._core.base import ModelBase
from stream_ml.core.builtin._stats.exponential import logpdf
from stream_ml.core.typing import Array, NNModel
from stream_ml.core.utils.compat import array_at

if TYPE_CHECKING:
    from stream_ml.core.data import Data
    from stream_ml.core.params import Params


@dataclass(unsafe_hash=True)
class Exponential(ModelBase[Array, NNModel]):
    r"""Tilted separately in each dimension.

    In each dimension the background is an exponential distribution between
    points ``a`` and ``b``. The rate parameter is ``m``.

    The non-zero portion of the PDF, where :math:`a < x < b` is

    .. math::

        f(x) = \frac{m * e^{-m * (x -a)}}{1 - e^{-m * (b - a)}}

    However, we use the order-3 Taylor expansion of the exponential function
    around m=0, to avoid the m=0 indeterminancy.

    .. math::

        f(x) =   \frac{1}{b-a}
               + m * (0.5 - \frac{x-a}{b-a})
               + \frac{m^2}{2} * (\frac{b-a}{6} - (x-a) + \frac{(x-a)^2}{b-a})
               + \frac{m^3}{12(b-a)} (2(x-a)-(b-a))(x-a)(b-x)
    """

    _: KW_ONLY
    require_mask: bool = False

    def __post_init__(self) -> None:
        super().__post_init__()

        # Pre-compute the associated constant factors
        _a = [a for k, (a, _) in self.coord_bounds.items() if k in self.params]
        _b = [b for k, (_, b) in self.coord_bounds.items() if k in self.params]

        self._a = self.xp.asarray(_a)[None, :]
        self._b = self.xp.asarray(_b)[None, :]
        self._bma = self._b - self._a

    # ========================================================================
    # Statistics

    def ln_likelihood(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        mask: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Log-likelihood of the background.

        Parameters
        ----------
        mpars : Params[Array], positional-only
            Model parameters. Note that these are different from the ML
            parameters.
        data : (N, F) Data[Array]
            Labelled data.

        mask : (N, F) Data[Array[bool]], keyword-only
            Data availability. True if data is available, False if not.
            Should have the same keys as `data`.
        **kwargs : Array
            Additional arguments.

        Returns
        -------
        (N,) Array
        """
        # The mask is used to indicate which data points are available. If the
        # mask is not provided, then all data points are assumed to be
        # available.
        if mask is not None:
            indicator = mask[tuple(self.coord_bounds.keys())].array
        elif self.require_mask:
            msg = "mask is required"
            raise ValueError(msg)
        else:
            indicator = self.xp.ones((len(data), 1), dtype=int)
            # This has shape (N, 1) so will broadcast correctly.

        # Data is x
        x = data[self.coord_names].array
        # Get the slope from `mpars` we check param names to see if the
        # slope is a parameter. If it is not, then we assume it is 0.
        # When the slope is 0, the log-likelihood reduces to a Uniform.
        ms = self.xp.stack(
            tuple(
                mpars[(k, "slope")]
                if (k, "slope") in self.params.flatskeys()
                else self.xp.zeros(len(x))
                for k in self.coord_names
            ),
            1,
        )
        n0 = ms != self.xp.asarray(0)
        zero = self.xp.zeros_like(x)

        # log-likelihood
        lnliks = self.xp.zeros_like(x)

        if self.coord_err_names is None:
            lnliks = array_at(lnliks, ~n0).set(  # Uniform
                -self.xp.log((zero + self._bma)[~n0])
            )
            lnliks = array_at(lnliks, n0).set(
                logpdf(
                    x[n0],
                    ms[n0],
                    (zero + self._a)[n0],
                    (zero + self._b)[n0],
                    xp=self.xp,
                    nil=-self.xp.inf,
                )
            )

            return (indicator * lnliks).sum(1)

        raise NotImplementedError