import unittest

from four_color_theorem_graph_coloring_utils import (
    Graph,
    coloring,
    five_color,
    four_color,
    is_valid_coloring,
    planar_graph_from_edges,
)


class TestGraph(unittest.TestCase):
    def test_empty_graph(self):
        g = Graph(0)
        self.assertEqual(g.n, 0)
        self.assertEqual(g.edges(), [])
        self.assertEqual(g.neighbors(0) if False else [], [])  # no vertex 0

    def test_add_edge_and_duplicates(self):
        g = Graph(3)
        g.add_edge(0, 1)
        g.add_edge(1, 0)
        g.add_edge(0, 1)
        g.add_edge(1, 2)
        self.assertEqual(g.degree(0), 1)
        self.assertEqual(g.degree(1), 2)
        self.assertEqual(g.degree(2), 1)
        self.assertEqual(sorted(g.edges()), [(0, 1), (1, 2)])

    def test_self_loop_ignored(self):
        g = Graph(2)
        g.add_edge(0, 0)
        self.assertEqual(g.degree(0), 0)
        self.assertEqual(g.edges(), [])

    def test_out_of_range(self):
        g = Graph(2)
        with self.assertRaises(IndexError):
            g.add_edge(0, 5)
        with self.assertRaises(IndexError):
            g.neighbors(5)


class TestColoring(unittest.TestCase):
    def test_empty(self):
        g = Graph(0)
        self.assertEqual(five_color(g), [])
        self.assertEqual(four_color(g), [])
        self.assertEqual(coloring(g), [])

    def test_single_vertex(self):
        g = Graph(1)
        self.assertEqual(five_color(g), [0])
        self.assertEqual(four_color(g), [0])
        self.assertEqual(coloring(g), [0])

    def test_path(self):
        # 0 - 1 - 2 - 3
        g = planar_graph_from_edges(4, [(0, 1), (1, 2), (2, 3)])
        c = four_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertLessEqual(max(c) if c else -1, 3)

    def test_cycle(self):
        g = planar_graph_from_edges(4, [(0, 1), (1, 2), (2, 3), (3, 0)])
        c = four_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertLessEqual(max(c) if c else -1, 3)

    def test_complete_graph_k4(self):
        # K4 is planar and needs exactly 4 colors.
        g = planar_graph_from_edges(4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)])
        c = four_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertEqual(len(set(c)), 4)

    def test_odd_cycle(self):
        g = planar_graph_from_edges(5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)])
        c = four_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertLessEqual(max(c) if c else -1, 3)

    def test_five_color_valid(self):
        # A small planar graph; five_color should always be valid.
        g = planar_graph_from_edges(6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 3)])
        c = five_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertLessEqual(max(c) if c else -1, 4)

    def test_four_color_valid_on_planar(self):
        # A more complex planar graph: octahedron (6 vertices, 12 edges).
        edges = [
            (0, 1), (0, 2), (0, 3), (0, 4),
            (1, 2), (1, 3), (1, 5),
            (2, 4), (2, 5),
            (3, 4), (3, 5),
            (4, 5),
        ]
        g = planar_graph_from_edges(6, edges)
        c = four_color(g)
        self.assertTrue(is_valid_coloring(g, c))
        self.assertLessEqual(max(c) if c else -1, 3)

    def test_coloring_max_colors(self):
        g = planar_graph_from_edges(3, [(0, 1), (1, 2)])
        c4 = coloring(g, max_colors=4)
        self.assertTrue(is_valid_coloring(g, c4))
        c5 = coloring(g, max_colors=5)
        self.assertTrue(is_valid_coloring(g, c5))
        c1 = coloring(g, max_colors=1)
        self.assertTrue(is_valid_coloring(g, c1))
        with self.assertRaises(ValueError):
            coloring(g, max_colors=0)

    def test_is_valid_coloring_rejects_bad(self):
        g = planar_graph_from_edges(2, [(0, 1)])
        self.assertFalse(is_valid_coloring(g, [0, 0]))
        self.assertFalse(is_valid_coloring(g, [0]))
        self.assertFalse(is_valid_coloring(g, [-1, 0]))
        self.assertTrue(is_valid_coloring(g, [0, 1]))

    def test_non_planar_fallback(self):
        # K5 is not planar; five_color should still return a proper coloring
        # (possibly using more than five colors).
        edges = [(i, j) for i in range(5) for j in range(i + 1, 5)]
        g = planar_graph_from_edges(5, edges)
        c = five_color(g)
        self.assertTrue(is_valid_coloring(g, c))


if __name__ == "__main__":
    unittest.main()
