"""Core feature."""

from __future__ import annotations

__all__: tuple[str, ...] = ()

from typing import TYPE_CHECKING, Any, Protocol

from stream_mapper.core._api import SupportsXP
from stream_mapper.core.typing import Array

if TYPE_CHECKING:
    from stream_mapper.core import Data, Params


class LnProbabilities(Protocol[Array]):
    """Protocol for objects that support probabilities."""

    def ln_likelihood(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Any,
    ) -> Array:
        r"""Elementwise log-likelihood :math:`\ln p(X | \theta)`.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Any
            Additional arguments.

        Returns
        -------
        Array[(N,)]
        """
        ...

    def ln_prior(self, mpars: Params[Array], /, data: Data[Array]) -> Array:
        r"""Elementwise log prior :math:`\ln p(\theta)`.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        ...

    def ln_evidence(self, data: Data[Array]) -> Array:
        r"""Log evidence :math:`\ln p(X)`.

        Parameters
        ----------
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        ...

    def ln_posterior(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        r"""Elementwise log posterior  :math:`\ln p(\theta | X)`.

        :math:`\ln p(\theta | X) = \ln p(X | \theta) + \ln p(\theta) - \ln p(X)`

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Arguments.

        Returns
        -------
        Array[(N,)]
        """
        return (
            self.ln_likelihood(mpars, data, where=where, **kwargs)
            + self.ln_prior(mpars, data)
            - self.ln_evidence(data)
        )


# ============================================================================


class TotalLnProbabilities(LnProbabilities[Array], SupportsXP[Array], Protocol[Array]):
    """Protocol for objects that support total probabilities."""

    def ln_likelihood_tot(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Total log-likelihood.

        This assumes that the data is independent.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Additional arguments.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.sum(self.ln_likelihood(mpars, data, where=where, **kwargs))

    def ln_prior_tot(self, mpars: Params[Array], /, data: Data[Array]) -> Array:
        """Total log-prior over the data set.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.sum(self.ln_prior(mpars, data))

    def ln_evidence_tot(self, data: Data[Array]) -> Array:
        """Total log-evidence over the data set.

        Parameters
        ----------
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.sum(self.ln_evidence(data))

    def ln_posterior_tot(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Sum of the log-posterior.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Keyword arguments. These are passed to the likelihood function.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.sum(self.ln_posterior(mpars, data, where=where, **kwargs))


# ============================================================================


class Probabilities(LnProbabilities[Array], SupportsXP[Array], Protocol[Array]):
    """Protocol for objects that support probabilities."""

    def likelihood(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Elementwise likelihood of the model.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Additional arguments.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_likelihood(mpars, data, where=where, **kwargs))

    def prior(self, mpars: Params[Array], /, data: Data[Array]) -> Array:
        """Elementwise prior.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_prior(mpars, data))

    def evidence(self, data: Data[Array]) -> Array:
        """Evidence.

        Parameters
        ----------
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_evidence(data))

    def posterior(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Elementwise posterior.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Arguments.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_posterior(mpars, data, where=where, **kwargs))


# ============================================================================


class TotalProbabilities(
    TotalLnProbabilities[Array], SupportsXP[Array], Protocol[Array]
):
    """Protocol for objects that support total probabilities."""

    def likelihood_tot(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Total likelihood, evaluated over the entire data set.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Additional arguments.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_likelihood_tot(mpars, data, where=where, **kwargs))

    def prior_tot(self, mpars: Params[Array], /, data: Data[Array]) -> Array:
        """Total prior, evaluated over the entire data set.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_prior_tot(mpars, data))

    def evidence_tot(self, data: Data[Array]) -> Array:
        """Total evidence, evaluated over the entire data set.

        Parameters
        ----------
        data : Data[Array[(N, F)]]
            Data.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_evidence_tot(data))

    def posterior_tot(
        self,
        mpars: Params[Array],
        /,
        data: Data[Array],
        *,
        where: Data[Array] | None = None,
        **kwargs: Array,
    ) -> Array:
        """Total posterior, evaluated over the entire data set.

        Parameters
        ----------
        mpars : Params[Array[(N,)]], positional-only
            Model parameters.
        data : Data[Array[(N, F)]]
            Data.

        where : Data[Array], optional keyword-only
            Where to evaluate the log-likelihood. If not provided, then the
            log-likelihood is evaluated at all data points.
        **kwargs : Array[(N,)]
            Keyword arguments. These are passed to the likelihood function.

        Returns
        -------
        Array[(N,)]
        """
        return self.xp.exp(self.ln_posterior_tot(mpars, data, where=where, **kwargs))


# ============================================================================


class AllProbabilities(
    TotalProbabilities[Array],
    Probabilities[Array],
    TotalLnProbabilities[Array],
    LnProbabilities[Array],
    SupportsXP[Array],
    Protocol,
):
    """Protocol for objects that support probabilities."""
