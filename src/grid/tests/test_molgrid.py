# GRID is a numerical integration module for quantum chemistry.
#
# Copyright (C) 2011-2019 The GRID Development Team
#
# This file is part of GRID.
#
# GRID is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# GRID is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
# --
"""MolGrid test file."""
from unittest import TestCase

from grid.atomgrid import AtomGrid
from grid.basegrid import LocalGrid
from grid.becke import BeckeWeights
from grid.hirshfeld import HirshfeldWeights
from grid.molgrid import MolGrid
from grid.onedgrid import GaussLaguerre, UniformInteger
from grid.rtransform import ExpRTransform

# from importlib_resources import path
import numpy as np
from numpy.testing import assert_allclose, assert_almost_equal


class TestMolGrid(TestCase):
    """MolGrid test class."""

    def setUp(self):
        """Set up radial grid for integral tests."""
        pts = UniformInteger(100)
        tf = ExpRTransform(1e-5, 2e1)
        self.rgrid = tf.transform_1d_grid(pts)

    def test_integrate_hydrogen_single_1s(self):
        """Test molecular integral in H atom."""
        # numbers = np.array([1], int)
        coordinates = np.array([0.0, 0.0, -0.5], float)
        # rgrid = BeckeRTransform.transform_grid(oned, 0.001, 0.5)[0]
        # rtf = ExpRTransform(1e-3, 1e1, 100)
        # rgrid = RadialGrid(rtf)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates,
        )
        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([1]), [atg1], becke)
        # mg = BeckeMolGrid(coordinates, numbers, None, (rgrid, 110), random_rotate=False)
        dist0 = np.sqrt(((coordinates - mg.points) ** 2).sum(axis=1))
        fn = np.exp(-2 * dist0) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 1.0, decimal=6)

    def test_make_grid_integral(self):
        """Test molecular make_grid works as designed."""
        pts = UniformInteger(70)
        tf = ExpRTransform(1e-5, 2e1)
        rgrid = tf.transform_1d_grid(pts)
        numbers = np.array([1, 1])
        coordinates = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]], float)
        becke = BeckeWeights(order=3)
        # construct molgrid
        for grid_type, deci in (
            ("coarse", 3),
            ("medium", 4),
            ("fine", 5),
            ("veryfine", 6),
            ("ultrafine", 6),
            ("insane", 6),
        ):
            mg = MolGrid.from_preset(numbers, coordinates, rgrid, grid_type, becke)
            dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
            dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
            fn = np.exp(-2 * dist0) / np.pi + np.exp(-2 * dist1) / np.pi
            occupation = mg.integrate(fn)
            assert_almost_equal(occupation, 2.0, decimal=deci)

    def test_make_grid_different_grid_type(self):
        """Test different kind molgrid initizalize setting."""
        # three different radial grid
        rad2 = GaussLaguerre(50)
        rad3 = GaussLaguerre(70)
        # construct grid
        numbers = np.array([1, 8, 1])
        coordinates = np.array(
            [[0.0, 0.0, -0.5], [0.0, 0.0, 0.5], [0.0, 0.5, 0.0]], float
        )
        becke = BeckeWeights(order=3)

        # grid_type test with list
        mg = MolGrid.from_preset(
            numbers,
            coordinates,
            rad2,
            ["fine", "veryfine", "medium"],
            becke,
            store=True,
            rotate=False,
        )
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        dist2 = np.sqrt(((coordinates[2] - mg.points) ** 2).sum(axis=1))
        fn = (np.exp(-2 * dist0) + np.exp(-2 * dist1) + np.exp(-2 * dist2)) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 3, decimal=3)

        atgrid1 = AtomGrid.from_preset(
            rad2, atnum=numbers[0], preset="fine", center=coordinates[0]
        )
        atgrid2 = AtomGrid.from_preset(
            rad2, atnum=numbers[1], preset="veryfine", center=coordinates[1]
        )
        atgrid3 = AtomGrid.from_preset(
            rad2, atnum=numbers[2], preset="medium", center=coordinates[2]
        )
        assert_allclose(mg._atgrids[0].points, atgrid1.points)
        assert_allclose(mg._atgrids[1].points, atgrid2.points)
        assert_allclose(mg._atgrids[2].points, atgrid3.points)

        # grid type test with dict
        mg = MolGrid.from_preset(
            numbers,
            coordinates,
            rad3,
            {1: "fine", 8: "veryfine"},
            becke,
            store=True,
            rotate=False,
        )
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        dist2 = np.sqrt(((coordinates[2] - mg.points) ** 2).sum(axis=1))
        fn = (np.exp(-2 * dist0) + np.exp(-2 * dist1) + np.exp(-2 * dist2)) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 3, decimal=3)

        atgrid1 = AtomGrid.from_preset(
            rad3, atnum=numbers[0], preset="fine", center=coordinates[0]
        )
        atgrid2 = AtomGrid.from_preset(
            rad3, atnum=numbers[1], preset="veryfine", center=coordinates[1]
        )
        atgrid3 = AtomGrid.from_preset(
            rad3, atnum=numbers[2], preset="fine", center=coordinates[2]
        )
        assert_allclose(mg._atgrids[0].points, atgrid1.points)
        assert_allclose(mg._atgrids[1].points, atgrid2.points)
        assert_allclose(mg._atgrids[2].points, atgrid3.points)

    def test_make_grid_different_rad_type(self):
        """Test different radial grid input for make molgrid."""
        # radial grid test with list
        rad1 = GaussLaguerre(30)
        rad2 = GaussLaguerre(50)
        rad3 = GaussLaguerre(70)
        # construct grid
        numbers = np.array([1, 8, 1])
        coordinates = np.array(
            [[0.0, 0.0, -0.5], [0.0, 0.0, 0.5], [0.0, 0.5, 0.0]], float
        )
        becke = BeckeWeights(order=3)
        # construct molgrid
        mg = MolGrid.from_preset(
            numbers,
            coordinates,
            [rad1, rad2, rad3],
            {1: "fine", 8: "veryfine"},
            becke,
            store=True,
            rotate=False,
        )
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        dist2 = np.sqrt(((coordinates[2] - mg.points) ** 2).sum(axis=1))
        fn = (np.exp(-2 * dist0) + np.exp(-2 * dist1) + np.exp(-2 * dist2)) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 3, decimal=3)

        atgrid1 = AtomGrid.from_preset(
            rad1, atnum=numbers[0], preset="fine", center=coordinates[0]
        )
        atgrid2 = AtomGrid.from_preset(
            rad2, atnum=numbers[1], preset="veryfine", center=coordinates[1]
        )
        atgrid3 = AtomGrid.from_preset(
            rad3, atnum=numbers[2], preset="fine", center=coordinates[2]
        )
        assert_allclose(mg._atgrids[0].points, atgrid1.points)
        assert_allclose(mg._atgrids[1].points, atgrid2.points)
        assert_allclose(mg._atgrids[2].points, atgrid3.points)

        # radial grid test with dict
        mg = MolGrid.from_preset(
            numbers,
            coordinates,
            {1: rad1, 8: rad3},
            {1: "fine", 8: "veryfine"},
            becke,
            store=True,
            rotate=False,
        )
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        dist2 = np.sqrt(((coordinates[2] - mg.points) ** 2).sum(axis=1))
        fn = (np.exp(-2 * dist0) + np.exp(-2 * dist1) + np.exp(-2 * dist2)) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 3, decimal=3)

        atgrid1 = AtomGrid.from_preset(
            rad1, atnum=numbers[0], preset="fine", center=coordinates[0]
        )
        atgrid2 = AtomGrid.from_preset(
            rad3, atnum=numbers[1], preset="veryfine", center=coordinates[1]
        )
        atgrid3 = AtomGrid.from_preset(
            rad1, atnum=numbers[2], preset="fine", center=coordinates[2]
        )
        assert_allclose(mg._atgrids[0].points, atgrid1.points)
        assert_allclose(mg._atgrids[1].points, atgrid2.points)
        assert_allclose(mg._atgrids[2].points, atgrid3.points)

    def test_integrate_hydrogen_pair_1s(self):
        """Test molecular integral in H2."""
        coordinates = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]], float)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )
        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([1, 1]), [atg1, atg2], becke)
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        fn = np.exp(-2 * dist0) / np.pi + np.exp(-2 * dist1) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 2.0, decimal=6)

    def test_integrate_hydrogen_trimer_1s(self):
        """Test molecular integral in H3."""
        coordinates = np.array(
            [[0.0, 0.0, -0.5], [0.0, 0.0, 0.5], [0.0, 0.5, 0.0]], float
        )
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )
        atg3 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[2],
        )
        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([1, 1, 1]), [atg1, atg2, atg3], becke)
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        dist2 = np.sqrt(((coordinates[2] - mg.points) ** 2).sum(axis=1))
        fn = (
            np.exp(-2 * dist0) / np.pi
            + np.exp(-2 * dist1) / np.pi
            + np.exp(-2 * dist2) / np.pi
        )
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 3.0, decimal=4)

    """
    def test_all_elements():
        numbers = np.array([1, 118], int)
        coordinates = np.array([[0.0, 0.0, -1.0], [0.0, 0.0, 1.0]], float)
        rtf = ExpRTransform(1e-3, 1e1, 10)
        rgrid = RadialGrid(rtf)
        while numbers[0] < numbers[1]:
            BeckeMolGrid(coordinates, numbers, None, (rgrid, 110), random_rotate=False)
            numbers[0] += 1
            numbers[1] -= 1
    """

    def test_integrate_hydrogen_8_1s(self):
        """Test molecular integral in H2."""
        x, y, z = np.meshgrid(*(3 * [[-0.5, 0.5]]))
        centers = np.stack([x.ravel(), y.ravel(), z.ravel()], axis=1)
        atgs = [
            AtomGrid.from_pruned(
                self.rgrid,
                0.5,
                sectors_r=np.array([]),
                sectors_degree=np.array([17]),
                center=center,
            )
            for center in centers
        ]

        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([1] * len(centers)), atgs, becke)
        fn = 0
        for center in centers:
            dist = np.linalg.norm(center - mg.points, axis=1)
            fn += np.exp(-2 * dist) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, len(centers), decimal=2)

    def test_molgrid_attrs_subgrid(self):
        """Test sub atomic grid attributes."""
        # numbers = np.array([6, 8], int)
        coordinates = np.array([[0.0, 0.2, -0.5], [0.1, 0.0, 0.5]], float)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            1.228,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.945,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )
        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([6, 8]), [atg1, atg2], becke, store=True)
        # mg = BeckeMolGrid(coordinates, numbers, None, (rgrid, 110), mode='keep')

        assert mg.size == 2 * 110 * 100
        assert mg.points.shape == (mg.size, 3)
        assert mg.weights.shape == (mg.size,)
        assert mg.aim_weights.shape == (mg.size,)
        assert len(mg._indices) == 2 + 1
        # assert mg.k == 3
        # assert mg.random_rotate

        for i in range(2):
            atgrid = mg[i]
            assert isinstance(atgrid, AtomGrid)
            assert atgrid.size == 100 * 110
            assert atgrid.points.shape == (100 * 110, 3)
            assert atgrid.weights.shape == (100 * 110,)
            assert (atgrid.center == coordinates[i]).all()
        mg = MolGrid(np.array([6, 8]), [atg1, atg2], becke)
        for i in range(2):
            atgrid = mg[i]
            assert isinstance(atgrid, LocalGrid)
            assert_allclose(atgrid.center, mg._atcoords[i])

    def test_molgrid_attrs(self):
        """Test MolGrid attributes."""
        # numbers = np.array([6, 8], int)
        coordinates = np.array([[0.0, 0.2, -0.5], [0.1, 0.0, 0.5]], float)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            1.228,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.945,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )

        becke = BeckeWeights(order=3)
        mg = MolGrid(np.array([6, 8]), [atg1, atg2], becke, store=True)

        assert mg.size == 2 * 110 * 100
        assert mg.points.shape == (mg.size, 3)
        assert mg.weights.shape == (mg.size,)
        assert mg.aim_weights.shape == (mg.size,)
        assert mg.get_atomic_grid(0) is atg1
        assert mg.get_atomic_grid(1) is atg2

        simple_ag1 = mg.get_atomic_grid(0)
        simple_ag2 = mg.get_atomic_grid(1)
        assert_allclose(simple_ag1.points, atg1.points)
        assert_allclose(simple_ag1.weights, atg1.weights)
        assert_allclose(simple_ag2.weights, atg2.weights)

        # test molgrid is not stored
        mg2 = MolGrid(np.array([6, 8]), [atg1, atg2], becke, store=False)
        assert mg2._atgrids is None
        simple2_ag1 = mg2.get_atomic_grid(0)
        simple2_ag2 = mg2.get_atomic_grid(1)
        assert isinstance(simple2_ag1, LocalGrid)
        assert isinstance(simple2_ag2, LocalGrid)
        assert_allclose(simple2_ag1.points, atg1.points)
        assert_allclose(simple2_ag1.weights, atg1.weights)
        assert_allclose(simple2_ag2.weights, atg2.weights)
        # assert mg.subgrids is None
        # assert mg.k == 3
        # assert mg.random_rotate

    def test_different_aim_weights_h2(self):
        """Test different aim_weights for molgrid."""
        coordinates = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]], float)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )
        # use an array as aim_weights
        mg = MolGrid(np.array([1, 1]), [atg1, atg2], np.ones(22000))
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        fn = np.exp(-2 * dist0) / np.pi + np.exp(-2 * dist1) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 4.0, decimal=4)

    def test_from_size(self):
        """Test horton style grid."""
        nums = np.array([1, 1])
        coors = np.array([[0, 0, -0.5], [0, 0, 0.5]])
        becke = BeckeWeights(order=3)
        mol_grid = MolGrid.from_size(nums, coors, self.rgrid, 110, becke, rotate=False)
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coors[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coors[1],
        )
        ref_grid = MolGrid(nums, [atg1, atg2], becke, store=True)
        assert_allclose(ref_grid.points, mol_grid.points)
        assert_allclose(ref_grid.weights, mol_grid.weights)

    def test_raise_errors(self):
        """Test molgrid errors raise."""
        atg = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=np.array([0.0, 0.0, 0.0]),
        )

        # errors of aim_weight
        with self.assertRaises(TypeError):
            MolGrid(atnums=np.array([1]), atgrids=[atg], aim_weights="test")
        with self.assertRaises(ValueError):
            MolGrid(atnums=np.array([1]), atgrids=[atg], aim_weights=np.array(3))
        with self.assertRaises(TypeError):
            MolGrid(atnums=np.array([1]), atgrids=[atg], aim_weights=[3, 5])

        # integrate errors
        becke = BeckeWeights({1: 0.472_431_53}, order=3)
        molg = MolGrid(np.array([1]), [atg], becke)
        with self.assertRaises(ValueError):
            molg.integrate()
        with self.assertRaises(TypeError):
            molg.integrate(1)
        with self.assertRaises(ValueError):
            molg.integrate(np.array([3, 5]))
        with self.assertRaises(ValueError):
            molg.get_atomic_grid(-3)
        molg = MolGrid(np.array([1]), [atg], becke, store=True)
        with self.assertRaises(ValueError):
            molg.get_atomic_grid(-5)

        # test make_grid error
        pts = UniformInteger(70)
        tf = ExpRTransform(1e-5, 2e1)
        rgrid = tf.transform_1d_grid(pts)
        numbers = np.array([1, 1])
        becke = BeckeWeights(order=3)
        # construct molgrid
        with self.assertRaises(ValueError):
            MolGrid.from_preset(
                numbers, np.array([0.0, 0.0, 0.0]), rgrid, "fine", becke
            )
        with self.assertRaises(ValueError):
            MolGrid.from_preset(
                np.array([1, 1]), np.array([[0.0, 0.0, 0.0]]), rgrid, "fine", becke
            )
        with self.assertRaises(ValueError):
            MolGrid.from_preset(
                np.array([1, 1]), np.array([[0.0, 0.0, 0.0]]), rgrid, "fine", becke
            )
        with self.assertRaises(TypeError):
            MolGrid.from_preset(
                np.array([1, 1]),
                np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]]),
                {3, 5},
                "fine",
                becke,
            )
        with self.assertRaises(TypeError):
            MolGrid.from_preset(
                np.array([1, 1]),
                np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]]),
                rgrid,
                np.array([3, 5]),
                becke,
            )

    def test_get_localgrid_1s(self):
        """Test local grid for a molecule with one atom."""
        nums = np.array([1])
        coords = np.array([0.0, 0.0, 0.0])

        # initialize MolGrid with atomic grid
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coords,
        )
        grid = MolGrid(np.array([1]), [atg1], BeckeWeights(), store=False)
        fn = np.exp(-2 * np.linalg.norm(grid.points, axis=-1))
        assert_allclose(grid.integrate(fn), np.pi)
        # conventional local grid
        localgrid = grid.get_localgrid(coords, 12.0)
        localfn = np.exp(-2 * np.linalg.norm(localgrid.points, axis=-1))
        assert localgrid.size < grid.size
        assert localgrid.size == 10560
        assert_allclose(localgrid.integrate(localfn), np.pi)
        assert_allclose(fn[localgrid.indices], localfn)
        # "whole" loal grid, useful for debugging code using local grids
        wholegrid = grid.get_localgrid(coords, np.inf)
        assert wholegrid.size == grid.size
        assert_allclose(wholegrid.points, grid.points)
        assert_allclose(wholegrid.weights, grid.weights)
        assert_allclose(wholegrid.indices, np.arange(grid.size))

        # initialize MolGrid like horton
        grid = MolGrid.from_size(
            nums, coords[np.newaxis, :], self.rgrid, 110, BeckeWeights(), store=True
        )
        fn = np.exp(-4.0 * np.linalg.norm(grid.points, axis=-1))
        assert_allclose(grid.integrate(fn), np.pi / 8)
        localgrid = grid.get_localgrid(coords, 5.0)
        localfn = np.exp(-4.0 * np.linalg.norm(localgrid.points, axis=-1))
        assert localgrid.size < grid.size
        assert localgrid.size == 9900
        assert_allclose(localgrid.integrate(localfn), np.pi / 8, rtol=1e-5)
        assert_allclose(fn[localgrid.indices], localfn)

    def test_get_localgrid_1s1s(self):
        """Test local grid for a molecule with one atom."""
        nums = np.array([1, 3])
        coords = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]])
        grid = MolGrid.from_size(
            nums, coords, self.rgrid, 110, BeckeWeights(), store=True, rotate=False
        )
        fn0 = np.exp(-4.0 * np.linalg.norm(grid.points - coords[0], axis=-1))
        fn1 = np.exp(-8.0 * np.linalg.norm(grid.points - coords[1], axis=-1))
        assert_allclose(grid.integrate(fn0), np.pi / 8, rtol=1e-5)
        assert_allclose(grid.integrate(fn1), np.pi / 64)
        # local grid centered on atom 0 to evaluate fn0
        local0 = grid.get_localgrid(coords[0], 5.0)
        assert local0.size < grid.size
        localfn0 = np.exp(-4.0 * np.linalg.norm(local0.points - coords[0], axis=-1))
        assert_allclose(fn0[local0.indices], localfn0)
        assert_allclose(local0.integrate(localfn0), np.pi / 8, rtol=1e-5)
        # local grid centered on atom 1 to evaluate fn1
        local1 = grid.get_localgrid(coords[1], 2.5)
        assert local1.size < grid.size
        localfn1 = np.exp(-8.0 * np.linalg.norm(local1.points - coords[1], axis=-1))
        assert_allclose(local1.integrate(localfn1), np.pi / 64, rtol=1e-6)
        assert_allclose(fn1[local1.indices], localfn1)
        # approximate the sum of fn0 and fn2 by combining results from local grids.
        fnsum = np.zeros(grid.size)
        fnsum[local0.indices] += localfn0
        fnsum[local1.indices] += localfn1
        assert_allclose(grid.integrate(fnsum), np.pi * (1 / 8 + 1 / 64), rtol=1e-5)

    def test_integrate_hirshfeld_weights_single_1s(self):
        """Test molecular integral in H atom with Hirshfeld weights."""
        pts = UniformInteger(100)
        tf = ExpRTransform(1e-5, 2e1)
        rgrid = tf.transform_1d_grid(pts)
        coordinates = np.array([0.0, 0.0, -0.5])
        atg1 = AtomGrid.from_pruned(
            rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates,
        )
        mg = MolGrid(np.array([7]), [atg1], HirshfeldWeights())
        dist0 = np.sqrt(((coordinates - mg.points) ** 2).sum(axis=1))
        fn = np.exp(-2 * dist0) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 1.0, decimal=6)

    def test_integrate_hirshfeld_weights_pair_1s(self):
        """Test molecular integral in H2."""
        coordinates = np.array([[0.0, 0.0, -0.5], [0.0, 0.0, 0.5]])
        atg1 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[0],
        )
        atg2 = AtomGrid.from_pruned(
            self.rgrid,
            0.5,
            sectors_r=np.array([]),
            sectors_degree=np.array([17]),
            center=coordinates[1],
        )
        mg = MolGrid(np.array([1, 1]), [atg1, atg2], HirshfeldWeights())
        dist0 = np.sqrt(((coordinates[0] - mg.points) ** 2).sum(axis=1))
        dist1 = np.sqrt(((coordinates[1] - mg.points) ** 2).sum(axis=1))
        fn = np.exp(-2 * dist0) / np.pi + 1.5 * np.exp(-2 * dist1) / np.pi
        occupation = mg.integrate(fn)
        assert_almost_equal(occupation, 2.5, decimal=5)
