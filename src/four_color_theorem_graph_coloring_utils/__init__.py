"""Four Color Theorem graph coloring utilities.

This package implements the linear-time five-coloring algorithm of Chiba and
Nishizeki, then reduces the result to at most four colors on planar graphs.
"""

from .core import (
    Graph,
    coloring,
    five_color,
    four_color,
    is_valid_coloring,
    planar_graph_from_edges,
)

__all__ = [
    "Graph",
    "coloring",
    "five_color",
    "four_color",
    "is_valid_coloring",
    "planar_graph_from_edges",
]
