"""Core feature."""

from __future__ import annotations

__all__: tuple[str, ...] = ()

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Generic, TypeVar, cast, overload

if TYPE_CHECKING:
    from collections.abc import Callable


R = TypeVar("R")
Self = TypeVar("Self", bound="cached_[R]")  # type: ignore[valid-type]


class cached_(Generic[R]):  # noqa: N801
    def __init__(
        self,
        fget: Callable[[Any], R] | None = None,
        fset: Callable[[object, R], None] | None = None,
        fdel: Callable[[object], None] | None = None,
        doc: str | None = None,
    ) -> None:
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc
        self._name: str = ""
        self._name_private = "_"

    def __set_name__(self, owner: type, name: str, /) -> None:
        self._name = name
        self._name_private = "_" + name

    def __set__(self, obj: object, value: Any) -> None:
        if self.fset is None:
            f"property '{self._name}' has no setter"
            raise AttributeError
        self.fset(obj, value)

    def __delete__(self, obj: object) -> None:
        if self.fdel is None:
            msg = f"property '{self._name}' has no deleter"
            raise AttributeError(msg)
        self.fdel(obj)

    def getter(self: Self, fget: Callable[[Any], R]) -> Self:
        """Return a cached property with a new getter."""
        prop = type(self)(fget, self.fset, self.fdel, self.__doc__)
        prop._name = self._name
        prop._name_private = self._name_private
        return prop

    def setter(self: Self, fset: Callable[[object, R], None]) -> Self:
        """Return a cached property with a new setter."""
        prop = type(self)(self.fget, fset, self.fdel, self.__doc__)
        prop._name = self._name
        prop._name_private = self._name_private
        return prop

    def deleter(self: Self, fdel: Callable[[object], None]) -> Self:
        """Retrun a cached property with a new deleter."""
        prop: Self = type(self)(self.fget, self.fset, fdel, self.__doc__)
        prop._name = self._name
        prop._name_private = self._name_private
        return prop


class cached_property(cached_[R]):  # noqa: N801
    """Emulate PyProperty_Type() in Objects/descrobject.c."""

    @overload
    def __get__(self: Self, obj: None, objtype: type | None = None) -> Self:
        ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> R:
        ...

    def __get__(
        self: Self, obj: object | None, objtype: type | None = None
    ) -> Self | R:
        if obj is None:
            return self
        if not hasattr(obj, self._name_private):
            if self.fget is None:
                f"property '{self._name}' has no getter"
                raise AttributeError
            object.__setattr__(obj, self._name_private, self.fget(obj))
        return cast("R", getattr(obj, self._name_private))


@dataclass(frozen=True, slots=True)
class WrappedValue(Generic[R]):
    value: R

    def __call__(self) -> R:
        return self.value


class cached_noargmethod(cached_[R]):  # noqa: N801
    @overload
    def __get__(self: Self, obj: None, objtype: type | None = None) -> Self:
        ...

    @overload
    def __get__(self, obj: object, objtype: type | None = None) -> Callable[[], R]:
        ...

    def __get__(
        self: Self, obj: object | None, objtype: type | None = None
    ) -> Self | Callable[[], R]:
        if obj is None:
            return self
        if not hasattr(obj, self._name_private):
            if self.fget is None:
                f"property '{self._name}' has no getter"
                raise AttributeError

            object.__setattr__(obj, self._name_private, WrappedValue(self.fget(obj)))

        return cast("Callable[[], R]", getattr(obj, self._name_private))
