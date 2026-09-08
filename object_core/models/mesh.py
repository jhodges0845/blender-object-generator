# SPDX-License-Identifier: GPL-3.0-or-later
"""Immutable mesh data with no application-specific objects."""

from dataclasses import dataclass
from math import isfinite
from typing import Tuple


Vertex = Tuple[float, float, float]
Face = Tuple[int, ...]
UV = Tuple[float, float]
FaceUVs = Tuple[UV, ...]


@dataclass(frozen=True)
class MeshPart:
    """A named mesh with local, zero-based face indices and optional UVs.

    Coordinates are centimeters: X is left/right, Y is forward, Z is up.
    Faces use outward counterclockwise winding when viewed from outside.
    ``uvs`` stores one UV coordinate per face corner, aligned with ``faces``;
    this allows seams without duplicating geometry vertices. An empty tuple means
    the producer has not supplied UVs.
    Input sequences are copied into tuples to keep the result immutable.
    Basic structural validation is performed here; manifoldness, winding,
    nonzero face area, and UV overlap are responsibilities of producers.
    """

    name: str
    vertices: Tuple[Vertex, ...]
    faces: Tuple[Face, ...]
    uvs: Tuple[FaceUVs, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("name must be a nonempty string")
        vertices = []
        for vertex in self.vertices:
            if len(vertex) != 3:
                raise ValueError("each vertex must have three coordinates")
            normalized = []
            for coordinate in vertex:
                if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                    raise TypeError("vertex coordinates must be numbers")
                try:
                    number = float(coordinate)
                except OverflowError:
                    raise ValueError("vertex coordinates must be finite") from None
                if not isfinite(number):
                    raise ValueError("vertex coordinates must be finite")
                normalized.append(number)
            vertices.append(tuple(normalized))
        if not vertices:
            raise ValueError("vertices must not be empty")
        faces = []
        for face in self.faces:
            indices = tuple(face)
            if any(isinstance(index, bool) or not isinstance(index, int) for index in indices):
                raise TypeError("face indices must be integers")
            if len(indices) < 3 or len(set(indices)) != len(indices):
                raise ValueError("a face must contain at least three distinct indices")
            if any(index < 0 or index >= len(vertices) for index in indices):
                raise ValueError("face index is outside the vertex array")
            faces.append(indices)
        if not faces:
            raise ValueError("faces must not be empty")

        uvs = []
        if self.uvs:
            if len(self.uvs) != len(faces):
                raise ValueError("uvs must contain one entry per face")
            for face, face_uvs in zip(faces, self.uvs):
                if len(face_uvs) != len(face):
                    raise ValueError("each UV face must match its face corner count")
                normalized_face = []
                for uv in face_uvs:
                    if len(uv) != 2:
                        raise ValueError("each UV coordinate must contain two values")
                    normalized_uv = []
                    for coordinate in uv:
                        if isinstance(coordinate, bool) or not isinstance(coordinate, (int, float)):
                            raise TypeError("UV coordinates must be numbers")
                        try:
                            number = float(coordinate)
                        except OverflowError:
                            raise ValueError("UV coordinates must be finite") from None
                        if not isfinite(number):
                            raise ValueError("UV coordinates must be finite")
                        normalized_uv.append(number)
                    uvs.append(tuple(normalized_uv)) if False else normalized_face.append(tuple(normalized_uv))
                uvs.append(tuple(normalized_face))

        object.__setattr__(self, "vertices", tuple(vertices))
        object.__setattr__(self, "faces", tuple(faces))
        object.__setattr__(self, "uvs", tuple(uvs))


@dataclass(frozen=True)
class ObjectMesh:
    """One or more independent mesh parts."""

    parts: Tuple[MeshPart, ...]

    def __post_init__(self) -> None:
        parts = tuple(self.parts)
        if not parts:
            raise ValueError("parts must not be empty")
        if any(not isinstance(part, MeshPart) for part in parts):
            raise TypeError("parts must contain MeshPart instances")
        if len({part.name for part in parts}) != len(parts):
            raise ValueError("part names must be unique")
        object.__setattr__(self, "parts", parts)

    @property
    def vertex_count(self) -> int:
        return sum(len(part.vertices) for part in self.parts)

    @property
    def face_count(self) -> int:
        return sum(len(part.faces) for part in self.parts)

    @property
    def bounds_cm(self) -> Tuple[Vertex, Vertex]:
        """Axis-aligned minimum and maximum corners across all parts."""
        vertices = tuple(vertex for part in self.parts for vertex in part.vertices)
        return (tuple(min(vertex[axis] for vertex in vertices) for axis in range(3)),
                tuple(max(vertex[axis] for vertex in vertices) for axis in range(3)))
