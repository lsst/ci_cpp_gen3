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
import numpy as np
import unittest

import lsst.afw.math as afwMath
import lsst.daf.butler as dafButler
import lsst.ip.isr as ipIsr
import lsst.utils.tests
from lsst.utils import getPackageDir

LEGACY_MODE = int(os.environ.get("CI_CPP_LEGACY", "0"))


# TODO: DM-26396
#       Update these tests to validate calibration construction.

@unittest.skipIf(LEGACY_MODE > 0, "Skipping new tests in legacy mode.")
class FlatTestCases(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup butler and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 5.1:

        Process an independent dark frame through the ISR including
        overscan correction, bias subtraction, dark subtraction.
        """
        repoDir = os.path.join(getPackageDir("ci_cpp_gen3"), "DATA/")
        butler = dafButler.Butler(repoDir, collections=['LATISS/raw/all', 'calib/v00', 'LATISS/calib'])

        config = ipIsr.IsrTaskLSSTConfig()
        config.doBias = True
        config.expectWcs = False
        config.doDefect = True
        config.doDark = True
        config.doFlat = True
        config.doDiffNonLinearCorrection = False
        config.doBootstrap = False
        config.doDeferredCharge = False
        config.doLinearize = True
        config.doCorrectGains = False
        config.doApplyGains = True
        config.doVariance = True
        config.doSaturation = True
        config.doSuspect = True
        config.doCrosstalk = True
        config.doWidenSaturationTrails = False
        config.doInterpolate = True
        config.doSetBadRegions = True
        config.doBrighterFatter = False

        isrTaskLSST = ipIsr.IsrTaskLSST(config=config)
        rawDataId = {"detector": 0, "exposure": 2021052500080, "instrument": "LATISS"}
        # TODO: DM-26396
        # This is not an independent frame.
        cls.raw = butler.get("raw", dataId=rawDataId)
        cls.bias = butler.get("bias", rawDataId)
        cls.camera = butler.get("camera", rawDataId)
        cls.ptc = butler.get("ptc", rawDataId)
        cls.linearizer = butler.get("linearizer", rawDataId)
        cls.crosstalk = butler.get("crosstalk", rawDataId)
        cls.defects = butler.get("defects", rawDataId)
        cls.dark = butler.get("dark", rawDataId)
        cls.flat = butler.get("flat", rawDataId)

        results = isrTaskLSST.run(
            cls.raw,
            camera=cls.camera,
            bias=cls.bias,
            ptc=cls.ptc,
            linearizer=cls.linearizer,
            crosstalk=cls.crosstalk,
            defects=cls.defects,
            dark=cls.dark,
            flat=cls.flat,
        )

        cls.exposure = results.outputExposure

    def test_independentFrameLevel(self):
        """Test image mean and sigma are plausible.

        Notes
        -----
        DMTN-101 10.X:
        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        sigma = afwMath.makeStatistics(self.exposure.getImage(), afwMath.STDEV).getValue()
        expectMean = 10282
        expectSigmaMax = 200
        self.assertLess(np.abs(mean - expectMean), sigma,
                        msg=f"Test 10.X: {mean} {expectMean} {sigma}")
        self.assertLess(sigma, expectSigmaMax,
                        msg=f"Test 10.X2: {sigma} {expectSigmaMax}")


@unittest.skipIf(LEGACY_MODE == 0, "Skipping legacy tests.")
class FlatTestCasesLegacy(FlatTestCases):
    @classmethod
    def setUpClass(cls):
        """Setup butler and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 5.1:

        Process an independent dark frame through the ISR including
        overscan correction, bias subtraction, dark subtraction.
        """
        repoDir = os.path.join(getPackageDir("ci_cpp_gen3"), "DATA/")
        butler = dafButler.Butler(repoDir, collections=['LATISS/raw/all', 'calib/v00', 'LATISS/calib'])

        config = ipIsr.IsrTaskConfig()
        config.doSaturation = True
        config.doSuspect = True
        config.doSetBadRegions = True
        config.doOverscan = True
        config.overscan.doParallelOverscan = True
        config.overscan.fitType = 'MEDIAN_PER_ROW'
        config.doBias = True
        config.doVariance = True
        config.doDark = True
        config.doFlat = True

        config.doLinearize = False
        config.doCrosstalk = False
        config.doWidenSaturationTrails = False
        config.doBrighterFatter = False
        config.doDefect = True
        config.doSaturationInterpolation = False
        config.doStrayLight = False
        config.doApplyGains = False
        config.doFringe = False
        config.doMeasureBackground = False
        config.doVignette = False
        config.doAttachTransmissionCurve = False
        config.doUseOpticsTransmission = False
        config.doUseFilterTransmission = False
        config.doUseSensorTransmission = False
        config.doUseAtmosphereTransmission = False

        isrTask = ipIsr.IsrTask(config=config)
        rawDataId = {'detector': 0, 'exposure': 2021052500080, 'instrument': 'LATISS'}
        # TODO: DM-26396
        # This is not an independent frame.
        cls.raw = butler.get('raw', rawDataId)
        cls.bias = butler.get('bias', rawDataId)
        cls.dark = butler.get('dark', rawDataId)
        cls.flat = butler.get('flat', rawDataId)
        cls.camera = butler.get('camera', rawDataId)
        cls.defects = butler.get('defects', rawDataId)

        results = isrTask.run(cls.raw, camera=cls.camera,
                              bias=cls.bias, dark=cls.dark,
                              flat=cls.flat, defects=cls.defects)
        cls.exposure = results.outputExposure

    def test_independentFrameLevel(self):
        """Test image mean and sigma are plausible.

        Notes
        -----
        DMTN-101 10.X:
        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        sigma = afwMath.makeStatistics(self.exposure.getImage(), afwMath.STDEV).getValue()
        expectMean = 10370
        expectSigmaMax = 3000
        self.assertLess(np.abs(mean - expectMean), sigma,
                        msg=f"Test 10.X: {mean} {expectMean} {sigma}")
        self.assertLess(sigma, expectSigmaMax,
                        msg=f"Test 10.X2: {sigma} {expectSigmaMax}")


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
