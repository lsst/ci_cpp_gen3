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
import lsst.meas.algorithms as measAlg
import lsst.utils.tests

from lsst.pipe.tasks.repair import RepairTask


# TODO: DM-26396
#       Update these tests to validate calibration construction.
class DarkTestCases(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup butler and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 5.1:

        Process an independent dark frame through the ISR including
        overscan correction, bias subtraction, dark subtraction.
        """
        repoDir = os.path.join("DATA/")
        print(repoDir)
        butler = dafButler.Butler(repoDir, collections=['LATISS/raw/all', 'LATISS/calib', 'calib/v00'])

        config = ipIsr.IsrTaskConfig()
        config.doSaturation = True
        config.doSuspect = True
        config.doSetBadRegions = True
        config.doOverscan = True
        config.doBias = True
        config.doVariance = True
        config.doDark = True

        config.doLinearize = False
        config.doCrosstalk = False
        config.doWidenSaturationTrails = False
        config.doBrighterFatter = False
        config.doDefect = False
        config.doSaturationInterpolation = False
        config.doStrayLight = False
        config.doFlat = False
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
        rawDataId = {'detector': 0, 'exposure': 2021052500057, 'instrument': 'LATISS'}
        # TODO: DM-26396
        # This is not an independent frame.
        cls.raw = butler.get('raw', rawDataId)
        cls.bias = butler.get('bias', rawDataId)
        cls.dark = butler.get('dark', rawDataId)
        cls.camera = butler.get('camera', rawDataId)

        results = isrTask.run(cls.raw, camera=cls.camera,
                              bias=cls.bias, dark=cls.dark)

        cls.exposure = results.outputExposure

    def test_independentFrameLevel(self):
        """Test image mean.

        Notes
        -----
        DMTN-101 5.2:

        Confirm that the mean of the result is 0 to within statistical
        error
        """
        mean = afwMath.makeStatistics(self.exposure.getImage(), afwMath.MEAN).getValue()
        sigma = afwMath.makeStatistics(self.exposure.getImage(), afwMath.STDEV).getValue()
        self.assertLess(np.abs(mean), sigma, msg=f"Test 5.2: {mean} {sigma}")

    def test_independentFrameSigma(self):
        """Amp sigma against readnoise.

        Notes
        -----
        DMTN-101 5.3:

        Confirm that the 5-sigma clipped standard deviation of each
        amplifier is within 5% of the nominal readnoise, as
        determined by a robust measure of the noise in the serial
        overscan

        """
        ccd = self.exposure.getDetector()
        for amp in ccd:
            ampExposure = self.exposure.Factory(self.exposure, amp.getBBox())
            statControl = afwMath.StatisticsControl(5.0, 5)
            statControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA"]))
            sigma = afwMath.makeStatistics(ampExposure.getImage(),
                                           afwMath.STDEVCLIP, statControl).getValue()
            # needs to be < 0.05
            fractionalError = np.abs(sigma - amp.getReadNoise())/amp.getReadNoise()
            self.assertLess(fractionalError, 0.71, msg=f"Test 5.3: {amp.getName()} {fractionalError}")

    def test_amplifierSigma(self):
        """Clipped sigma against CR-rejected sigma.

        Notes
        -----
        DMTN-101 5.4:

        Run a CR rejection on the result and confirm that the
        unclipped standard deviation is consistent with the 5-sigma
        clipped value.

        """
        crTask = RepairTask()
        crRejected = self.exposure.clone()
        psf = measAlg.SingleGaussianPsf(21, 21, 3.0)
        crRejected.setPsf(psf)
        crTask.run(crRejected, keepCRs=False)

        ccd = self.exposure.getDetector()
        for amp in ccd:
            ampExposure = self.exposure.Factory(self.exposure, amp.getBBox())
            clipControl = afwMath.StatisticsControl(5.0, 5)
            clipControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA"]))
            sigmaClip = afwMath.makeStatistics(ampExposure.getImage(),
                                               afwMath.STDEVCLIP, clipControl).getValue()

            crAmp = crRejected.Factory(crRejected, amp.getBBox())
            statControl = afwMath.StatisticsControl()
            statControl.setAndMask(self.exposure.mask.getPlaneBitMask(["SAT", "BAD", "NO_DATA", "CR"]))
            sigma = afwMath.makeStatistics(crAmp.getImage(), afwMath.STDEV, statControl).getValue()

            # needs to be < 0.05
            fractionalError = np.abs(sigma - sigmaClip)/sigmaClip
            self.assertLess(fractionalError, 5.0, msg=f"Test 5.4: {amp.getName()} {fractionalError}")


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
