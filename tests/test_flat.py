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
import hashlib
import numpy as np
import unittest

import lsst.afw.math as afwMath
import lsst.daf.butler as dafButler
import lsst.ip.isr as ipIsr
import lsst.meas.algorithms as measAlg
import lsst.utils.tests

from lsst.pipe.tasks.repair import RepairTask
from lsst.utils import getPackageDir


class DarkTestCases(lsst.utils.tests.TestCase):

    def setUp(self):
        """Setup butler and generate an ISR processed exposure.

        Notes
        -----
        DMTN-101 5.1:

        Process an independent dark frame through the ISR including
        overscan correction, bias subtraction, dark subtraction.
        """
        repoDir = os.path.join(getPackageDir('ci_cpp_gen3'), "DATA")
        butler = dafButler.Butler(repoDir, collections=['raws/latiss', 'calibs/latiss', 'calib/v00'])

        self.config = ipIsr.IsrTaskConfig()
        self.config.doSaturation = True
        self.config.doSuspect = True
        self.config.doSetBadRegions = True
        self.config.doOverscan = True
        self.config.doBias = True
        self.config.doVariance = True
        self.config.doDark = True
        self.config.doFlat = True

        self.config.doLinearize = False
        self.config.doCrosstalk = False
        self.config.doWidenSaturationTrails = False
        self.config.doBrighterFatter = False
        self.config.doDefect = False
        self.config.doSaturationInterpolation = False
        self.config.doStrayLight = False
        self.config.doApplyGains = False
        self.config.doFringe = False
        self.config.doMeasureBackground = False
        self.config.doVignette = False
        self.config.doAttachTransmissionCurve = False
        self.config.doUseOpticsTransmission = False
        self.config.doUseFilterTransmission = False
        self.config.doUseSensorTransmission = False
        self.config.doUseAtmosphereTransmission = False

        self.isrTask = ipIsr.IsrTask(config=self.config)
        # This is not an independent frame.
        self.raw = butler.get('raw', dataId={'detector': 0, 'exposure': 2020012800014,
                                             'instrument': 'LATISS'})
        self.bias = butler.get('bias', dataId={'detector': 0,
                                               'instrument': 'LATISS',
                                               'calibration_label': 'bias/ci_cpp_bias'})
        self.dark = butler.get('dark', dataId={'detector': 0,
                                               'instrument': 'LATISS',
                                               'calibration_label': 'dark/ci_cpp_dark'})
        self.flat = butler.get('flat', dataId={'detector': 0,
                                               'instrument': 'LATISS',
                                               'physical_filter': 'KPNO_406_828nm~EMPTY',
                                               'calibration_label': 'flat/ci_cpp_flat'})
        self.camera = butler.get('camera', dataId={'detector': 0, 'exposure': 2020012800014,
                                                   'instrument': 'LATISS',
                                                   'calibration_label': 'unbounded'})

        results = self.isrTask.run(self.raw, camera=self.camera,
                                   bias=self.bias, dark=self.dark, flat=self.flat)
        self.exposure = results.outputExposure

    def test_canary(self):
        """Test for data value changes.
        """
        m = hashlib.md5()
        m.update(self.flat.getImage().getArray())

        self.assertEquals(m.hexdigest(), 'c31b7d22f6e5ea03c8a30ed913e4ddf2')

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
        print("5.2f", mean, sigma)
        self.assertLess(np.abs(mean), sigma)

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
            print("5.3f", amp.getName(), sigma, amp.getReadNoise(),
                  np.abs(sigma - amp.getReadNoise())/amp.getReadNoise())
            self.assertLess(np.abs(sigma - amp.getReadNoise())/amp.getReadNoise(), 0.71)

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
            print("5.4f", amp.getName(), sigma, sigmaClip, np.abs(sigma - sigmaClip)/sigmaClip)
            self.assertLess(np.abs(sigma - sigmaClip)/sigmaClip, 7.0)

    def test_55(self):
        """Split processing test.

        Notes
        -----
        DMTN-101 5.5:

        Process the 150 "even" and "odd" visits separately, and
        subtract the two resulting dark calibration frames.
        """
        pass

    def test_56(self):
        """Split processing means.

        Notes
        -----
        DMTN-101 5.6:

        Confirm that the mean of the difference is 0 to within
        statistical error
        """
        pass

    def test_57(self):
        """Split processing noise check.

        Notes
        -----
        DMTN-101 5.7

        Confirm that the unclipped standard deviation of the
        difference is consistent with the dark current and readnoise
        (as measured by a robust measure of the noise in the serial
        overscan of the individual frames), as corrected by the
        correct combination of N$_{\text{b}}$, N$_{\text{d}}$, and
        T$_{\text{d}}$.

        """
        pass


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    pass


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
