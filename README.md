# four_color_theorem_graph_coloring_utils

A dependency-free Python library that colors planar graphs with at most four colors using the linear-time algorithm of Chiba and Nishizeki.

## Usage

```python
from four_color_theorem_graph_coloring_utils import planar_graph_from_edges, four_color, is_valid_coloring

# A simple planar graph: a square with a diagonal.
edges = [(0, 1), (1, 2), (2, 3), (3, 0), (0, 2)]
g = planar_graph_from_edges(4, edges)
colors = four_color(g)
assert is_valid_coloring(g, colors)
assert max(colors) <= 3
print(colors)  # e.g. [0, 1, 2, 1]
```

The public API is:

- `Graph(n)` — an undirected simple graph on vertices `0 .. n-1`.
- `planar_graph_from_edges(n, edges)` — build a graph from an iterable of `(u, v)` pairs.
- `five_color(g)` — proper coloring using at most five colors.
- `four_color(g)` — proper coloring of a planar graph using at most four colors.
- `coloring(g, max_colors=4)` — convenience wrapper; for `max_colors >= 5` it is `five_color`, for `max_colors == 4` it is `four_color`, and for smaller values it still returns a proper coloring but may use more colors than requested.
- `is_valid_coloring(g, colors)` — check that every edge joins differently colored vertices.

## Why this library exists

The Four Color Theorem is famous for its computer-assisted proof, but the constructive algorithms are less well known. Chiba and Nishizeki gave a linear-time algorithm that produces a five-coloring, and the standard reduction step (Kempe chains) turns that into a four-coloring for planar graphs. This library packages that algorithm in a small, auditable module with no third-party dependencies, so it can be dropped into environments where installing packages is not an option.

The main trade-off is that the reduction step is heuristic in the sense that it may fail to eliminate the fifth color on non-planar inputs; the graph is then returned with a valid five-coloring. For planar inputs the algorithm is guaranteed to succeed, and the tests cover the standard planar cases.

## Awkward edge

The `Graph` class ignores self-loops and duplicate edges. This keeps degree counts and neighbor iteration deterministic, but means that if you rely on multigraph semantics you will need a different structure. Also, `coloring(g, max_colors=1)` does not raise an error for graphs that need more than one color; it returns a proper coloring that may use more colors than requested. The README documents this decision so callers can check the result with `is_valid_coloring` and the maximum color used.
