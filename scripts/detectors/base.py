"""Detector base class. Subclass to add a new document-pattern detector."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path


class Detector(ABC):
    """A pattern detector that fires when the markdown matches a known shape.

    Detectors run in two phases:

    1. ``detect(text, path)`` returns a confidence score 0.0–1.0. If above the
       pipeline's threshold, the detector is "active" for this file.
    2. ``transform(text)`` rewrites the markdown source to inject HTML or
       custom markers that the renderer / CSS understands.

    Detectors must be **independent**: removing one never affects others.
    They should also be **conservative**: when in doubt, don't fire — a false
    positive disfigures a normal document, a false negative just means
    "treated as plain markdown", which is still acceptable.
    """

    name: str = "base"

    @abstractmethod
    def detect(self, text: str, path: Path) -> float:  # pragma: no cover
        ...

    @abstractmethod
    def transform(self, text: str) -> str:  # pragma: no cover
        ...
