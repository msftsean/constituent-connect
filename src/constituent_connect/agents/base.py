from __future__ import annotations

from typing import Protocol, TypeVar


T = TypeVar("T")


class DeterministicGate(Protocol[T]):
    """Marker contract for authoritative, non-generative policy gates."""

    def __call__(self, *args: object, **kwargs: object) -> T: ...
