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
"""RTransform test file."""

from unittest import TestCase

from grid.onedgrid import GaussLegendre
from grid.rtransform import (
    ExpRTransform,
    HyperbolicRTransform,
    IdentityRTransform,
    LinearInfiniteRTransform,
    PowerRTransform,
)

import numpy as np


class TestRTransform(TestCase):
    """Horton transform test class."""

    @staticmethod
    def check_consistency(rtf):
        """Check general consistency."""
        ts = np.random.uniform(0, 99, 200)
        # consistency between radius and radius_array
        rs = rtf.transform(ts)
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * ts[i]
            assert rs[i] == rtf.transform(rf_gd)[0]
        # consistency between deriv and deriv_array
        ds = rtf.deriv(ts)
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * ts[i]
            assert ds[i] == rtf.deriv(rf_gd)[0]
        # consistency between deriv2 and deriv2_array
        d2s = rtf.deriv2(ts)
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * ts[i]
            assert d2s[i] == rtf.deriv2(rf_gd)[0]
        # consistency between deriv3 and deriv3_array
        d3s = rtf.deriv3(ts)
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * ts[i]
            assert d3s[i] == rtf.deriv3(rf_gd)[0]
        # consistency between inv and inv_array
        ts[:] = 0.0
        ts = rtf.inverse(rs)
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * rs[i]
            assert ts[i] == rtf.inverse(rf_gd)[0]
        # consistency between inv and radius
        for i in range(ts.shape[0]):
            rf_gd = np.ones(200) * ts[i]
            assert abs(ts[i] - rtf.inverse(rtf.transform(rf_gd))[0]) < 1e-10

        # ts = np.arange(rtf.npoint, dtype=float)
        # # consistency of get_radii
        # assert (rtf.get_radii() == rtf.radius(ts)).all()
        # # consistency of get_deriv
        # assert (rtf.get_deriv() == rtf.deriv(ts)).all()
        # # consistency of get_deriv2
        # assert (rtf.get_deriv2() == rtf.deriv2(ts)).all()
        # # consistency of get_deriv3
        # assert (rtf.get_deriv3() == rtf.deriv3(ts)).all()

        # # radii must increase strictly
        # radii = rtf.get_radii()
        # assert (radii[1:] > radii[:-1]).all()

    @staticmethod
    def check_deriv(rtf):
        """Check derivative with fd."""
        ts = np.random.uniform(0, 99, 200)
        eps = 1e-5
        ts0 = ts - eps / 2
        ts1 = ts + eps / 2
        fns = [
            (rtf.transform, rtf.deriv),
            (rtf.deriv, rtf.deriv2),
            (rtf.deriv2, rtf.deriv3),
        ]
        for fnr, fnd in fns:
            ds = fnd(ts)
            dns = (fnr(ts1) - fnr(ts0)) / eps
            assert abs(ds - dns).max() < 1e-5

    # def check_chop(rtf1):
    #     assert rtf1.npoint == 100
    #     rtf2 = rtf1.chop(50)
    #     assert rtf1.__class__ == rtf2.__class__
    #     assert rtf2.npoint == 50
    #     assert abs(rtf1.get_radii()[:50] - rtf2.get_radii()).max() < 1e-8

    # def check_half(rtf1):
    #     radii1 = rtf1.get_radii()
    #     rtf2 = rtf1.half()
    #     radii2 = rtf2.get_radii()
    #     assert abs(radii1[1::2] - radii2).max() < 1e-9

    def test_identity_basics(self):
        """Test identity tf."""
        # gd = HortonLiner(100)
        rtf = IdentityRTransform()
        assert rtf.transform(0.0) == 0.0
        assert rtf.transform(99.0) == 99.0
        self.check_consistency(rtf)
        self.check_deriv(rtf)
        # check_chop(rtf)

    def test_linear_basics(self):
        """Test linear tf."""
        gd = np.ones(100) * 0
        rtf = LinearInfiniteRTransform(-0.7, 0.8)
        assert abs(rtf.transform(gd)[0] - -0.7) < 1e-15
        gd = np.ones(100) * 99
        assert abs(rtf.transform(gd)[0] - 0.8) < 1e-10
        self.check_consistency(rtf)
        self.check_deriv(rtf)
        # check_chop(rtf)
        # check_half(rtf)

    def test_exp_basics(self):
        """Test exponential tf."""
        rtf = ExpRTransform(0.1, 1e1)
        gd = np.ones(100) * 0
        assert abs(rtf.transform(gd)[0] - 0.1) < 1e-15
        gd = np.ones(100) * 99
        assert abs(rtf.transform(gd)[0] - 1e1) < 1e-10
        self.check_consistency(rtf)
        self.check_deriv(rtf)
        # check_chop(rtf)
        # check_half(rtf)

    @staticmethod
    def get_power_cases():
        """Set Helper function for power tf."""
        return [(1e-3, 1e2), (1e-3, 1e3), (1e-3, 1e4), (1e-3, 1e5)]

    def test_power_basics(self):
        """Test power tf."""
        cases = self.get_power_cases()
        for rmin, rmax in cases:
            gd = np.ones(100) * 99
            rtf = PowerRTransform(rmin, rmax)
            assert abs(rtf.transform(gd)[0] - rmax) < 1e-9
            self.check_consistency(rtf)
            self.check_deriv(rtf)
            # check_chop(rtf)
            # check_half(rtf)

    def test_hyperbolic_basics(self):
        """Test hyperbolic tf."""
        rtf = HyperbolicRTransform(0.4 / 450, 1.0 / 450)
        self.check_consistency(rtf)
        self.check_deriv(rtf)

    # def test_identity_properties():
    #     rtf = IdentityRTransform(100)
    #     assert rtf.npoint == 100

    def test_linear_properties(self):
        """Test linear tf properties."""
        rtf = LinearInfiniteRTransform(-0.7, 0.8)
        assert rtf.rmin == -0.7
        assert rtf.rmax == 0.8
        # assert rtf.npoint == 100
        # assert rtf.alpha > 0

    def test_exp_properties(self):
        """Test exponential tf properties."""
        rtf = ExpRTransform(0.1, 1e1)
        assert rtf.rmin == 0.1
        assert rtf.rmax == 1e1
        # assert rtf.npoint == 100
        # assert rtf.alpha > 0

    def test_power_properties(self):
        """Test power tf properties."""
        cases = self.get_power_cases()
        for rmin, rmax in cases:
            rtf = PowerRTransform(rmin, rmax)
            assert rtf.rmin == rmin
            assert rtf.rmax == rmax
            # assert rtf.npoint == 100
            # assert rtf.power >= 2

    def test_hyperbolic_properties(self):
        """Test hyperbolic tf properties."""
        rtf = HyperbolicRTransform(0.4 / 450, 1.0 / 450)
        assert rtf.a == 0.4 / 450
        assert rtf.b == 1.0 / 450
        # assert rtf.npoint == 450

    def test_domain(self):
        """Test domain errors."""
        rad = GaussLegendre(10)
        with self.assertRaises(ValueError):
            tf = IdentityRTransform()
            tf.transform_1d_grid(rad)
        with self.assertRaises(ValueError):
            tf = LinearInfiniteRTransform(0.1, 1.5)
            tf.transform_1d_grid(rad)
        with self.assertRaises(ValueError):
            tf = ExpRTransform(0.1, 1e1)
            tf.transform_1d_grid(rad)
        with self.assertRaises(ValueError):
            tf = PowerRTransform(1e-3, 1e2)
            tf.transform_1d_grid(rad)
        with self.assertRaises(ValueError):
            tf = HyperbolicRTransform(0.4 / 450, 1.0 / 450)
            tf.transform_1d_grid(rad)

    def test_linear_bounds(self):
        """Test linear tf raise errors."""
        with self.assertRaises(ValueError):
            LinearInfiniteRTransform(1.1, 0.9)

    def test_exp_bounds(self):
        """Test exponential tf raise errors."""
        with self.assertRaises(ValueError):
            ExpRTransform(-0.1, 1.0)
        with self.assertRaises(ValueError):
            ExpRTransform(0.1, -1.0)
        with self.assertRaises(ValueError):
            ExpRTransform(1.1, 0.9)

    def test_power_bounds(self):
        """Test power tf raise errors."""
        with self.assertRaises(ValueError):
            PowerRTransform(-1.0, 2.0)
        with self.assertRaises(ValueError):
            PowerRTransform(0.1, -2.0)
        with self.assertWarns(RuntimeWarning):
            a = np.ones(50)
            tf = PowerRTransform(1.0, 1.1)
            tf.transform(a)
        with self.assertRaises(ValueError):
            PowerRTransform(1.1, 1.0)

    def test_hyperbolic_bounds(self):
        """Test hyperbolic tf raise errors."""
        with self.assertRaises(ValueError):
            HyperbolicRTransform(0, 1.0 / 450)
        with self.assertRaises(ValueError):
            HyperbolicRTransform(-0.1, 1.0 / 450)
        a = np.ones(450)
        tf = HyperbolicRTransform(0.4, 1.0)
        with self.assertRaises(ValueError):
            tf.transform(a)
        with self.assertRaises(ValueError):
            tf.deriv(a)
        with self.assertRaises(ValueError):
            tf.deriv2(a)
        with self.assertRaises(ValueError):
            tf.deriv3(a)
        with self.assertRaises(ValueError):
            tf.inverse(a)
        with self.assertRaises(ValueError):
            a = np.ones(3)
            tf = HyperbolicRTransform(0.4, 0.5)
            tf.transform(a)
        with self.assertRaises(ValueError):
            HyperbolicRTransform(0.2, 0.0)
        with self.assertRaises(ValueError):
            HyperbolicRTransform(0.2, -1.0)


"""
def test_exception_string():
    with assert_raises(TypeError):
        RTransform.from_string("Fubar A 5")


def test_identiy_string():
    rtf1 = IdentityRTransform(45)
    s = rtf1.to_string()
    rtf2 = RTransform.from_string(s)
    assert rtf1.npoint == rtf2.npoint

    with assert_raises(ValueError):
        RTransform.from_string("IdentityRTransform A")
    with assert_raises(ValueError):
        RTransform.from_string("IdentityRTransform A 5 .1")

    rtf3 = RTransform.from_string("IdentityRTransform 8")
    assert rtf3.npoint == 8


def test_linear_string():
    rtf1 = LinearInfiniteRTransform(np.random.uniform(1e-5, 5e-5), np.random.uniform(1, 5), 88)
    s = rtf1.to_string()
    rtf2 = RTransform.from_string(s)
    assert rtf1.rmin == rtf2.rmin
    assert rtf1.rmax == rtf2.rmax
    assert rtf1.npoint == rtf2.npoint
    assert rtf1.alpha == rtf2.alpha

    with assert_raises(ValueError):
        RTransform.from_string("LinearInfiniteRTransform A 5")
    with assert_raises(ValueError):
        RTransform.from_string("LinearInfiniteRTransform A 5 .1")

    rtf3 = RTransform.from_string("LinearInfiniteRTransform -1.0 12.15643216847 77")
    assert rtf3.rmin == -1.0
    assert rtf3.rmax == 12.15643216847
    assert rtf3.npoint == 77
    assert rtf3.alpha > 0


def test_exp_string():
    rtf1 = ExpRTransform(np.random.uniform(1e-5, 5e-5), np.random.uniform(1, 5), 111)
    s = rtf1.to_string()
    rtf2 = RTransform.from_string(s)
    assert rtf1.rmin == rtf2.rmin
    assert rtf1.rmax == rtf2.rmax
    assert rtf1.npoint == rtf2.npoint
    assert rtf1.alpha == rtf2.alpha

    with assert_raises(ValueError):
        RTransform.from_string("ExpRTransform A 5")
    with assert_raises(ValueError):
        RTransform.from_string("ExpRTransform A 5 .1")

    rtf3 = RTransform.from_string("ExpRTransform 1.0 12.15643216847 5")
    assert rtf3.rmin == 1.0
    assert rtf3.rmax == 12.15643216847
    assert rtf3.npoint == 5
    assert rtf3.alpha > 0


def test_power_string():
    rtf1 = PowerRTransform(
        np.random.uniform(1e-3, 5e-3), np.random.uniform(2.0, 5.0), 11
    )
    s = rtf1.to_string()
    rtf2 = RTransform.from_string(s)
    assert rtf1.rmin == rtf2.rmin
    assert rtf1.rmax == rtf2.rmax
    assert rtf1.power == rtf2.power
    assert rtf1.npoint == rtf2.npoint

    with assert_raises(ValueError):
        RTransform.from_string("PowerRTransform A 5")
    with assert_raises(ValueError):
        RTransform.from_string("PowerRTransform A 5 .1")

    rtf3 = RTransform.from_string("PowerRTransform 0.02154 12.15643216847 5")
    assert rtf3.rmin == 0.02154
    assert rtf3.rmax == 12.15643216847
    assert rtf3.power > 2
    assert rtf3.npoint == 5


def test_hyperbolic_string():
    rtf1 = HyperbolicRTransform(0.4 / 450, 1.0 / 450, 450)
    s = rtf1.to_string()
    rtf2 = RTransform.from_string(s)
    assert rtf1.a == rtf2.a
    assert rtf1.b == rtf2.b
    assert rtf1.npoint == rtf2.npoint

    with assert_raises(ValueError):
        RTransform.from_string("HyperbolicRTransform A 5")
    with assert_raises(ValueError):
        RTransform.from_string("HyperbolicRTransform A 5 .1")

    rtf3 = RTransform.from_string("HyperbolicRTransform 0.01 0.02315479 5")
    assert rtf3.a == 0.01
    assert rtf3.b == 0.02315479
    assert rtf3.npoint == 5

def test_identity_bounds():
    for npoint in -1, 0, 1:
        with assert_raises(ValueError):
            IdentityRTransform(npoint)
"""
