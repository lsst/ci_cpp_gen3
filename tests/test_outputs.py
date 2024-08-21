# This file is part of ci_cpp_gen3.
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
import os
import unittest

import lsst.daf.butler as dafButler
import lsst.utils.tests

from lsst.afw.cameraGeom import Camera
from lsst.afw.image import Exposure
from lsst.ip.isr import (Defects, BrighterFatterKernel, CrosstalkCalib, DeferredChargeCalib, Linearizer,
                         PhotonTransferCurveDataset)
from lsst.utils import getPackageDir

LEGACY_MODE = int(os.environ.get("CI_CPP_LEGACY", "0"))


class OutputTestCases(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup butler, and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 4.1:

        Process an independent bias frame through the ISR including
        overscan correction and bias subtraction

        """
        repoDir = os.path.join(getPackageDir("ci_cpp_gen3"), "DATA/")
        cls.collections = ["LATISS/raw/all", "calib/v00", "LATISS/calib"]
        cls.butler = dafButler.Butler(repoDir, collections=cls.collections)
        cls.rawDataId = {'detector': 0, 'exposure': 2021052500015, 'instrument': 'LATISS'}

    def getExpectedProduct(self, datasetType, dataId=None, collections=None):
        """Get a product from the butler.

        Parameters
        ----------
        datasetType : `str`
            Dataset to retrieve.
        dataId : `dict`, optional
            If supplied, this will be the image used to look up the
            product.
        collections : `list` or `str`, optional
            Alternate collections to supply.

        Returns
        -------
        product :
            The dataset requested.

        """
        product = None
        dataId = dataId if dataId else self.rawDataId
        collections = collections if collections else self.collections

        try:
            product = self.butler.get(datasetType, dataId=dataId, collections=collections)
        except Exception:
            pass
        return product

    def test_cameraOutput(self):
        # This confirms curated calibrations were written correctly.
        self.assertIsInstance(self.getExpectedProduct('camera'), Camera)

    def test_biasOutput(self):
        self.assertIsInstance(self.getExpectedProduct('bias'), Exposure)

    def test_darkOutput(self):
        self.assertIsInstance(self.getExpectedProduct('dark'), Exposure)

    def test_flatOutput(self):
        self.assertIsInstance(self.getExpectedProduct('flat'), Exposure)

    def test_crosstalkOutput(self):
        self.assertIsInstance(self.getExpectedProduct('crosstalk'), CrosstalkCalib)

    def test_ptcOutput(self):
        self.assertIsInstance(self.getExpectedProduct('ptc'), PhotonTransferCurveDataset)

    @unittest.skipUnless(LEGACY_MODE > 0, "Skipping BFK test until we have BFK.")
    def test_bfkOutput(self):
        self.assertIsInstance(self.getExpectedProduct('bfk'), BrighterFatterKernel)

    @unittest.skipUnless(LEGACY_MODE > 0, "Skipping legacy partial ptc test.")
    def test_gainOutput(self):
        # These are certified on a per-exposure basis.
        dataId = {'detector': 0, 'exposure': 2021052500079, 'instrument': 'LATISS'}
        self.assertIsInstance(self.getExpectedProduct('cpPtcPartial', dataId=dataId),
                              PhotonTransferCurveDataset)

    def test_linearityOutput(self):
        self.assertIsInstance(self.getExpectedProduct('linearizer'), Linearizer)

    def test_defectsOutput(self):
        self.assertIsInstance(self.getExpectedProduct('defects'), Defects)

    def test_scienceOutput(self):
        # This needs one of the actual exposures and the specific
        # collection.
        dataId = {'detector': 0, 'exposure': 2021052500198, 'instrument': 'LATISS'}
        collections = ['ci_cpp_science']
        self.assertIsInstance(self.getExpectedProduct('postISRCCD', dataId=dataId, collections=collections),
                              Exposure)

    def test_skyOutput(self):
        self.assertIsInstance(self.getExpectedProduct('sky'), Exposure)

    @unittest.skipUnless(LEGACY_MODE > 0, "Skipping CTI test until we have CTI done.")
    def test_ctiOutput(self):
        self.assertIsInstance(self.getExpectedProduct('cti'), DeferredChargeCalib)

    @unittest.skipUnless(LEGACY_MODE > 0, "Skipping CTI processing test until we have CTI done.")
    def test_ctiProcOutput(self):
        # This needs one of the actual exposures and the specific
        # collection.
        dataId = {'detector': 0, 'exposure': 2021052500077, 'instrument': 'LATISS'}
        collections = ['ci_cpp_ctiProc']
        self.assertIsInstance(self.getExpectedProduct('postISRCCD', dataId=dataId, collections=collections),
                              Exposure)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    ignore_regexps = [r"/?gen3.sqlite3$"]


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
