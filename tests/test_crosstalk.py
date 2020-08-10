# This file is part of ci_cpp.
#
# Developed for the LSST Data Management System.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import unittest
import lsst.utils.tests


class CrosstalkTestCases(lsst.utils.tests.TestCase):

    def setup_independentFrame(self):
        """Missing data.

        Notes
        -----
        DMTN-101 9.1
        Fit the amplitude of each cross-talk image to the image of the
        "aggressor" spot, resulting in an 3024x3024 matrix (16*189).
        If appropriate, a 16x16 matrix may be sufficient.  Compare
        with the numbers provided by the camera team
        """
        pass

    def test_independentFrameLevel(self):
        """Missing data.

        Notes
        -----
        DMTN-101 9.2

        Using the all-amp-spots image, mask the direct spots, and
        confirm that the median and 5-sigma clipped means are equal to
        within statistical error.

        """
        pass


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
