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
import yaml

import lsst.daf.butler as dafButler
import lsst.utils.tests

from lsst.utils import getPackageDir

LEGACY_MODE = int(os.environ.get("CI_CPP_LEGACY", "0"))


class VerificationTestCases(lsst.utils.tests.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup butler."""
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
            # Ignoring these errors means there may be downstream test
            # failures.
            print("ARGH")
            pass
        return product

    def readExpectation(self, filename):
        """Read the archived yaml result for comparison.

        Parameters
        ----------
        filename : `str`
            File to read.  The subdirectory will be prepended.

        Returns
        -------
        result : `dict`
            The archived result dictionary.
        """
        if LEGACY_MODE > 0:
            fileLocation = os.path.join(
                getPackageDir("ci_cpp_gen3"),
                "tests",
                "data",
                "legacy_202409",
                filename,
            )
        else:
            fileLocation = os.path.join(getPackageDir("ci_cpp_gen3"), "tests", "data", filename)

        with open(fileLocation, 'r') as file:
            result = yaml.safe_load(file)

        return result

    def assertNumbersEqual(self, inputA, inputB, msg):
        if not (np.isnan(inputA) and np.isnan(inputB)):
            self.assertAlmostEqual(inputA, inputB, delta=0.05, msg=msg)

    def assertYamlEqual(self, inputA, inputB, msg=None):
        self.assertEqual(inputA.keys(), inputB.keys(), msg)
        for key in inputA.keys():
            self.assertEqual(type(inputA[key]), type(inputB[key]), msg)

            if isinstance(inputA[key], dict):
                self.assertYamlEqual(inputA[key], inputB[key], msg)
            elif isinstance(inputA[key], list):
                self.assertEqual(len(inputA[key]), len(inputB[key]), msg)
                for aa, bb in zip(inputA[key], inputB[key]):
                    if isinstance(aa, dict):
                        self.assertYamlEqual(aa, bb, msg)
                    elif isinstance(aa, list):
                        self.assertEqual(len(aa), len(bb))
                        for i in range(len(aa)):
                            self.assertNumbersEqual(aa[i], bb[i], msg)
                    elif isinstance(aa, (int, float)):
                        self.assertNumbersEqual(aa, bb, msg)
                    else:
                        self.assertEqual(aa, bb, msg)
            elif isinstance(inputA[key], (int, float)):
                self.assertNumbersEqual(inputA[key], inputB[key], msg)
            else:
                self.assertEqual(inputA[key], inputB[key], msg)

    def genericComparison(self, collections, dataId, componentMap):
        """Run common comparisons.

        Parameters
        ----------
        collections : `str`
            Collections to pull results from.
        dataId : `dict`
            Data id to look up results for.
        componentMap : `dict` [`str`, `tuple` [`str`, `str`]]
            Dictionary mapping butler data product to comparison yaml
            file.
        """
        if 'run' in componentMap:
            runStatDataType, runStatFile = componentMap['run']
            runStats = self.getExpectedProduct(runStatDataType, dataId=dataId, collections=collections)
            expectation = self.readExpectation(runStatFile)
            self.assertYamlEqual(runStats, expectation, "run level")

        if 'exp' in componentMap:
            expStatDataType, expStatFile = componentMap['exp']
            expStats = self.getExpectedProduct(expStatDataType, dataId=dataId, collections=collections)
            expectation = self.readExpectation(expStatFile)
            self.assertYamlEqual(expStats, expectation, "exposure level")

        if 'det' in componentMap:
            detStatDataType, detStatFile = componentMap['det']
            detStats = self.getExpectedProduct(detStatDataType, dataId=dataId, collections=collections)
            expectation = self.readExpectation(detStatFile)
            self.assertYamlEqual(detStats, expectation, "detector level")

    def test_biasVerify(self):
        """Run comparison for bias."""
        dataId = {'instrument': 'LATISS', 'detector': 0, 'exposure': 2021052500015}
        mapping = {'run': ('verifyBiasStats', 'biasRun.yaml'),
                   'exp': ('verifyBiasExpStats', 'biasExp.yaml'),
                   'det': ('verifyBiasDetStats', 'biasDet.yaml')}

        self.genericComparison('ci_cpv_bias', dataId, mapping)

    def test_darkVerify(self):
        """Run comparison for dark."""
        dataId = {'instrument': 'LATISS', 'detector': 0, 'exposure': 2021052500057}
        mapping = {'run': ('verifyDarkStats', 'darkRun.yaml'),
                   'exp': ('verifyDarkExpStats', 'darkExp.yaml'),
                   'det': ('verifyDarkDetStats', 'darkDet.yaml')}

        self.genericComparison('ci_cpv_dark', dataId, mapping)

    def test_flatVerify(self):
        """Run comparison for flat."""
        dataId = {
            "instrument": "LATISS",
            "detector": 0,
            "exposure": 2021052500080,
            "physical_filter": "RG610~empty",
        }
        mapping = {'run': ('verifyFlatStats', 'flatRun.yaml'),
                   'exp': ('verifyFlatExpStats', 'flatExp.yaml'),
                   'det': ('verifyFlatDetStats', 'flatDet.yaml')}

        self.genericComparison('ci_cpv_flat', dataId, mapping)

    def test_ptcVerify(self):
        """Run comparison for ptc."""
        dataId = {'instrument': 'LATISS', 'detector': 0}
        mapping = {'run': ('verifyPtcStats', 'ptcRun.yaml'),
                   'det': ('verifyPtcDetStats', 'ptcDet.yaml')}

        self.genericComparison('ci_cpv_ptc', dataId, mapping)

    def test_bfkVerify(self):
        """Run comparison for bfk.

        DM-40856 This has the same underlying problem as the
        linearizer.
        """
        # dataId = {'instrument': 'LATISS', 'detector': 0,
        #           'visit': 2021052500190}
        # mapping = {'run': ('verifyBfkStats', 'bfkRun.yaml'),
        #            'exp': ('verifyBfkExpStats', 'bfkExp.yaml'),
        #            'det': ('verifyBfkDetStats', 'bfkDet.yaml')}
        # self.genericComparison('ci_cpv_bfk', dataId, mapping)
        pass

    @unittest.skipIf(LEGACY_MODE > 0, "Skipping linearizer verify test.")
    def test_linearizerVerify(self):
        """Run comparison for linearizer.

        DM-40856 Linearity fits from ci_cpp are not stable.
        """
        dataId = {"instrument": "LATISS", "detector": 0}
        mapping = {"run": ("verifyLinearizerStats", "linearizerRun.yaml"),
                   "det": ("verifyLinearizerDetStats", "linearizerDet.yaml")}
        self.genericComparison("ci_cpv_linearizer", dataId, mapping)

    @unittest.skipIf(LEGACY_MODE == 0, "Skipping crosstalk verify test.")
    def test_crosstalkVerify(self):
        """Run comparison for crosstalk."""
        dataId = {'instrument': 'LATISS', 'detector': 0}
        mapping = {'run': ('verifyCrosstalkStats', 'crosstalkRun.yaml'),
                   'det': ('verifyCrosstalkDetStats', 'crosstalkDet.yaml')}

        self.genericComparison('ci_cpv_crosstalk', dataId, mapping)


class MemoryTester(lsst.utils.tests.MemoryTestCase):
    ignore_regexps = [r"/?gen3.sqlite3$"]


def setup_module(module):
    lsst.utils.tests.init()


if __name__ == "__main__":
    lsst.utils.tests.init()
    unittest.main()
