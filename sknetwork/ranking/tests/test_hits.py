#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tests for hits.py"""

import unittest

from scipy import sparse

from sknetwork.ranking.hits import HITS
from sknetwork.toy_graphs import karate_club, painters, movie_actor


class TestHITS(unittest.TestCase):

    def setUp(self):
        self.undirected: sparse.csr_matrix = karate_club()
        self.directed: sparse.csr_matrix = painters()
        self.bipartite: sparse.csr_matrix = movie_actor()

    def test_hits_hubmode(self):
        hits = HITS(mode='hubs')

        n = self.undirected.shape[0]
        hits.fit(self.undirected)
        self.assertEqual(len(hits.score_), n)
        self.assertEqual(len(hits.coscore_), n)

        n = self.directed.shape[0]
        hits.fit(self.directed)
        self.assertEqual(len(hits.score_), n)
        self.assertEqual(len(hits.coscore_), n)

        n, m = self.bipartite.shape
        hits.fit(self.bipartite)
        self.assertEqual(len(hits.score_), n)
        self.assertEqual(len(hits.coscore_), m)

    def test_hits_autmode(self):
        hits = HITS(mode='authorities')

        n = self.undirected.shape[0]
        hits.fit(self.undirected)
        self.assertEqual(len(hits.score_), n)
        self.assertEqual(len(hits.coscore_), n)

        n = self.directed.shape[0]
        hits.fit(self.directed)
        self.assertEqual(len(hits.score_), n)
        self.assertEqual(len(hits.coscore_), n)

        n, m = self.bipartite.shape
        hits.fit(self.bipartite)
        self.assertEqual(len(hits.score_), m)
        self.assertEqual(len(hits.coscore_), n)

