#!/usr/bin/env python3
# coding: utf-8
"""
Created on Apr 2020
@author: Nathan de Lara <ndelara@enst.fr>
"""

from typing import Union

import numpy as np
from scipy import sparse

from sknetwork.embedding.svd import GSVD
from sknetwork.embedding.base import BaseEmbedding
from sknetwork.utils.check import check_format, check_square, is_symmetric
from sknetwork.utils.format import directed2undirected


class FruchtermanReingold(BaseEmbedding):
    """Spring layout for displaying small graphs.

    Parameters
    ----------
    strength: float
        Intensity of the force that moves the nodes.
    n_iter: int
        Number of iterations to update positions.
    tol: float
        Minimum relative change in positions to continue updating.
    pos_init: str
        How to initialize the layout. If 'gsvd', use GSVD in dimension 2, otherwise, use random initialization.

    Attributes
    ----------
    embedding_: np.ndarray
        Layout in 2D.

    Notes
    -----
    Simple implementation designed to display small graphs in 2D.
    """
    def __init__(self, strength: float = None, n_iter: int = 50, tol: float = 1e-4, pos_init: str = 'gsvd'):
        super(FruchtermanReingold, self).__init__()
        self.strength = strength
        self.n_iter = n_iter
        self.tol = tol
        self.pos_init = pos_init

    def fit(self, adjacency: Union[sparse.csr_matrix, np.ndarray], pos_init: np.ndarray = None,
            n_iter: int = None) -> 'FruchtermanReingold':
        """Compute layout.

        Parameters
        ----------
        adjacency :
            Adjacency matrix of the graph, treated as undirected.
        pos_init : np.ndarray
            Custom initial positions of the nodes. Shape must be (n, 2).
            If None, use the value of self.pos_init.
        n_iter : int
            Number of iterations to update positions.
            If None, use the value of self.n_iter.

        Returns
        -------
        self
        """
        adjacency = check_format(adjacency)
        check_square(adjacency)
        if not is_symmetric(adjacency):
            adjacency = directed2undirected(adjacency)
        n = adjacency.shape[0]

        if pos_init is None:
            if self.pos_init == 'gsvd':
                pos = GSVD(n_components=2).fit_transform(adjacency)
            else:
                pos = np.random.randn(n, 2)
        elif isinstance(pos_init, np.ndarray):
            if pos_init.shape == (n, 2):
                pos = pos_init.copy()
            else:
                raise ValueError('Initial position has invalid shape.')
        else:
            raise TypeError('Unknown initial position, try "gsvd" or "random".')

        if n_iter is None:
            n_iter = self.n_iter

        if self.strength is None:
            strength = np.sqrt((1 / n))
        else:
            strength = self.strength

        delta_x: float = pos[:, 0].max() - pos[:, 0].min()
        delta_y: float = pos[:, 1].max() - pos[:, 1].min()
        step_max: float = 0.1 * max(delta_x, delta_y)
        step: float = step_max / (n_iter + 1)
        delta = np.zeros((n, 2))
        for iteration in range(n_iter):
            delta *= 0
            for i in range(n):
                indices = adjacency.indices[adjacency.indptr[i]:adjacency.indptr[i+1]]
                data = adjacency.data[adjacency.indptr[i]:adjacency.indptr[i+1]]

                grad: np.ndarray = (pos[i] - pos)  # shape (n, 2)
                distance: np.ndarray = np.linalg.norm(grad, axis=1)  # shape (n,)
                distance = np.where(distance < 0.01, 0.01, distance)

                attraction = np.zeros(n)
                attraction[indices] *= data * distance[indices] / strength

                repulsion = (strength * distance)**2

                delta[i]: np.ndarray = (grad * (repulsion - attraction)[:, np.newaxis]).sum(axis=0)  # shape (2,)
            length = np.linalg.norm(delta, axis=0)
            length = np.where(length < 0.01, 0.1, length)
            delta = delta * step_max / length
            pos += delta
            step_max -= step
            err: float = np.linalg.norm(delta) / n
            if err < self.tol:
                break

        self.embedding_ = pos
        return self