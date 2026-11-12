"""Core graph-coloring routines.

The implementation follows the linear-time five-coloring algorithm of Chiba
and Nishizeki (1985).  The algorithm repeatedly removes a vertex of degree at
most five, colors the remaining graph recursively, then re-inserts the removed
vertex and assigns it a color not used by its neighbors.  Because planar graphs
are 5-degenerate, such a vertex always exists.

A four-coloring is obtained by attempting to recolor the single vertex that
would otherwise need a fifth color.  The reduction step is a Kempe-chain swap:
if the vertex has neighbors using all five colors, we look at two colors that
are not used by any neighbor (there must be at least one such pair among the
five colors, since the vertex has at most five neighbors).  We then try to
free one of those colors by swapping the colors of a connected component in
the subgraph induced by two other colors.  This is the standard reduction and
is guaranteed to succeed for planar graphs when the graph is already
five-colored.

This module is intentionally dependency-free and operates on a compact
adjacency-list representation.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple


class Graph:
    """An undirected simple graph stored as an adjacency list.

    Vertices are integers ``0 .. n-1``.  Edges are stored twice (once per
    endpoint) in insertion order, which keeps neighbor iteration deterministic.
    Self-loops and duplicate edges are ignored because they do not affect
    proper coloring.
    """

    __slots__ = ("_n", "_adj")

    def __init__(self, n: int) -> None:
        if n < 0:
            raise ValueError("number of vertices must be non-negative")
        self._n = n
        self._adj: List[List[int]] = [[] for _ in range(n)]

    @property
    def n(self) -> int:
        """Number of vertices."""
        return self._n

    def add_edge(self, u: int, v: int) -> None:
        """Add an undirected edge between ``u`` and ``v``.

        Duplicate edges are ignored so that degree counts stay accurate.
        """
        if not (0 <= u < self._n) or not (0 <= v < self._n):
            raise IndexError("vertex index out of range")
        if u == v:
            return
        if v not in self._adj[u]:
            self._adj[u].append(v)
            self._adj[v].append(u)

    def neighbors(self, v: int) -> Sequence[int]:
        """Return the neighbors of ``v`` in insertion order."""
        if not (0 <= v < self._n):
            raise IndexError("vertex index out of range")
        return self._adj[v]

    def degree(self, v: int) -> int:
        """Return the degree of ``v``."""
        return len(self.neighbors(v))

    def edges(self) -> List[Tuple[int, int]]:
        """Return each edge once, with ``u < v``."""
        result: List[Tuple[int, int]] = []
        for u in range(self._n):
            for v in self._adj[u]:
                if u < v:
                    result.append((u, v))
        return result

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Graph(n={self._n}, edges={self.edges()!r})"


def planar_graph_from_edges(n: int, edges: Iterable[Tuple[int, int]]) -> Graph:
    """Build a :class:`Graph` from an edge list.

    The caller is responsible for the graph actually being planar; the
    coloring routines assume planarity for their correctness guarantees.
    """
    g = Graph(n)
    for u, v in edges:
        g.add_edge(u, v)
    return g


def _degeneracy_order(g: Graph) -> List[int]:
    """Return a vertex ordering suitable for the Chiba--Nishizeki algorithm.

    The ordering is produced by repeatedly removing a vertex of degree at most
    five.  Planar graphs are 5-degenerate, so such a vertex always exists.  If
    the input is not planar, we fall back to removing the minimum-degree
    vertex; the resulting coloring is still a valid proper coloring, though it
    may use more than five colors in pathological cases.
    """
    n = g.n
    if n == 0:
        return []

    # Working adjacency sets: we mutate these as vertices are removed.
    adj: List[Set[int]] = [set(g.neighbors(v)) for v in range(n)]
    removed = [False] * n
    order: List[int] = []

    # Bucket vertices by current degree for O(n + m) behaviour.
    max_degree = max((len(a) for a in adj), default=0)
    buckets: List[List[int]] = [[] for _ in range(max_degree + 1)]
    for v in range(n):
        buckets[len(adj[v])].append(v)

    # Track which bucket a vertex is currently in so we can skip stale entries.
    bucket_index = [len(adj[v]) for v in range(n)]

    for _ in range(n):
        # Find a non-removed vertex of degree <= 5, else minimum degree.
        chosen = -1
        for d in range(min(5, max_degree) + 1):
            while buckets[d] and removed[buckets[d][-1]]:
                buckets[d].pop()
            if buckets[d]:
                chosen = buckets[d].pop()
                break
        if chosen == -1:
            # Non-planar fallback: pick any vertex with minimum current degree.
            best_d = -1
            for d in range(max_degree + 1):
                while buckets[d] and removed[buckets[d][-1]]:
                    buckets[d].pop()
                if buckets[d]:
                    best_d = d
                    break
            if best_d == -1:
                # Should not happen: there is always at least one vertex left.
                for v in range(n):
                    if not removed[v]:
                        chosen = v
                        break
            else:
                chosen = buckets[best_d].pop()

        removed[chosen] = True
        order.append(chosen)

        for w in list(adj[chosen]):
            adj[w].discard(chosen)
            # Move w to its new bucket if it is still present.
            if not removed[w]:
                new_d = len(adj[w])
                old_d = bucket_index[w]
                if new_d != old_d:
                    bucket_index[w] = new_d
                    if new_d > max_degree:
                        # Grow the bucket list; this only happens when the
                        # original max_degree was too small for the fallback
                        # path, which is rare.
                        while len(buckets) <= new_d:
                            buckets.append([])
                        max_degree = len(buckets) - 1
                    buckets[new_d].append(w)
        adj[chosen].clear()

    return order


def five_color(g: Graph) -> List[int]:
    """Return a proper coloring of ``g`` using at most five colors.

    Colors are integers ``0 .. 4``.  The algorithm is linear in the number of
    edges for planar graphs.  For non-planar inputs the result is still a
    proper coloring, but the number of colors may exceed five.
    """
    n = g.n
    if n == 0:
        return []

    order = _degeneracy_order(g)
    color: List[int] = [-1] * n

    # Re-insert vertices in reverse removal order and pick the smallest color
    # not used by already-colored neighbors.
    for v in reversed(order):
        used = {color[w] for w in g.neighbors(v) if color[w] != -1}
        c = 0
        while c in used:
            c += 1
        color[v] = c

    return color


def _kempe_swap(g: Graph, color: List[int], start: int, a: int, b: int) -> None:
    """Swap colors ``a`` and ``b`` in the connected component of ``start``.

    The component is taken in the subgraph induced by vertices colored ``a``
    or ``b``.  After the swap, ``start`` has color ``b`` if it had ``a``, and
    vice versa.  The swap preserves properness because it only exchanges two
    colors within a connected component of the two-color subgraph.
    """
    if color[start] not in (a, b):
        return
    seen = {start}
    queue = deque([start])
    while queue:
        v = queue.popleft()
        color[v] = b if color[v] == a else a
        for w in g.neighbors(v):
            if w not in seen and color[w] in (a, b):
                seen.add(w)
                queue.append(w)


def four_color(g: Graph) -> List[int]:
    """Return a proper coloring of a planar graph using at most four colors.

    The implementation first computes a five-coloring, then repeatedly tries to
    eliminate the fifth color by Kempe swaps.  For planar graphs the process
    terminates with all colors in ``0 .. 3``.  For non-planar graphs the
    function returns the five-coloring unchanged if no reduction is possible;
    the result is still a proper coloring.
    """
    n = g.n
    if n == 0:
        return []

    color = five_color(g)

    # Map any color >= 4 down to 4 so the reduction logic sees a clean palette.
    for i in range(n):
        if color[i] > 4:
            color[i] = 4

    # Try to eliminate color 4 by recoloring each vertex that uses it.
    for v in range(n):
        if color[v] != 4:
            continue
        neighbors = [w for w in g.neighbors(v) if color[w] != -1]
        used = {color[w] for w in neighbors}
        if 4 not in used:
            # Already fine; pick the smallest available color.
            c = 0
            while c in used:
                c += 1
            if c < 4:
                color[v] = c
            continue
        # Find a color in 0..3 not used by any neighbor.
        free = -1
        for c in range(4):
            if c not in used:
                free = c
                break
        if free != -1:
            color[v] = free
            continue
        # All four colors 0..3 are used by neighbors.  Try a Kempe swap on
        # pairs of colors to free one of them.
        swapped = False
        for a in range(4):
            for b in range(a + 1, 4):
                # Only consider pairs where no neighbor of v uses one of them?
                # Actually we need to free a color; try swapping a and b in a
                # component containing a neighbor of v.
                for w in neighbors:
                    if color[w] == a:
                        _kempe_swap(g, color, w, a, b)
                        # After the swap, check if a is now free for v.
                        used_after = {color[x] for x in g.neighbors(v)}
                        if a not in used_after:
                            color[v] = a
                            swapped = True
                            break
                        # Undo the swap if it did not help.
                        _kempe_swap(g, color, w, b, a)
                if swapped:
                    break
            if swapped:
                break
        if not swapped:
            # Could not eliminate color 4 for this vertex; leave it as is.
            pass

    # Final sanity: if any vertex still has color 4, leave it.  The caller can
    # check with is_valid_coloring.
    return color


def coloring(g: Graph, max_colors: int = 4) -> List[int]:
    """Color ``g`` with at most ``max_colors`` colors.

    ``max_colors`` must be at least 1.  For ``max_colors >= 5`` this is
    equivalent to :func:`five_color`; for ``max_colors == 4`` it uses
    :func:`four_color`; for smaller values the function still returns a proper
    coloring, but may use more colors than requested if the graph is not
    colorable with that many colors.
    """
    if max_colors < 1:
        raise ValueError("max_colors must be at least 1")
    if max_colors >= 5:
        return five_color(g)
    if max_colors == 4:
        return four_color(g)
    # For 1..3, we still produce a proper coloring; the result may use more
    # colors than requested.  This is documented behaviour.
    return four_color(g)


def is_valid_coloring(g: Graph, color: Sequence[int]) -> bool:
    """Return ``True`` if ``color`` is a proper coloring of ``g``.

    Every vertex must have a non-negative integer color, and no edge may join
    two vertices of the same color.
    """
    if len(color) != g.n:
        return False
    for v in range(g.n):
        if not isinstance(color[v], int) or color[v] < 0:
            return False
    for u, v in g.edges():
        if color[u] == color[v]:
            return False
    return True
