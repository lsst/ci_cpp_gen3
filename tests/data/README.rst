This directory contains the target YAML files for the tests of the
``cp_verify`` output.  As the targets may change as the code evolves,
this document includes instructions on how to replace the now outdated
target with the one generated in the current run.

Please take care to understand what and why the results have changed
before simply copying the new results in place.

bfk
===

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bfk/*/verifyBfkStats/verifyBfkStats* ./bfkRun.yaml

Exposure level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bfk/*/verifyBfkExpStats/20210525/r/RG610~empty/2021052500190/verifyBfkExpStats* ./bfkExp.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bfk/*/verifyBfkDetStats/20210525/r/RG610~empty/2021052500190/* ./bfkDet.yaml

bias
====

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bias/*/verifyBiasStats/verifyBiasStats* ./biasRun.yaml

Exposure level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bias/*/verifyBiasExpStats/20210525/r/RG610~empty/AT_O_20210525_000015/verifyBiasExpStats* ./biasExp.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_bias/*/verifyBiasDetStats/20210525/AT_O_20210525_000015/verifyBiasDetStats* ./biasDet.yaml


crosstalk
=========

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_crosstalk/*/verifyCrosstalkStats/verifyCrosstalkStats* ./crosstalkRun.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_crosstalk/*/verifyCrosstalkDetStats/verifyCrosstalkDetStats* ./crosstalkDet.yaml


dark
====

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_dark/*/verifyDarkStats/verifyDarkStats* ./darkRun.yaml

Exposure level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_dark/*/verifyDarkExpStats/20210525/r/RG610~empty/AT_O_20210525_000057/verifyDarkExpStats* ./darkExp.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_dark/*/verifyDarkDetStats/20210525/AT_O_20210525_000057/verifyDarkDetStats* ./darkDet.yaml


flat
====

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_flat/*/verifyFlatStats/r/RG610~empty/* ./flatRun.yaml

Exposure level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_flat/*/verifyFlatExpStats/20210525/r/RG610~empty/AT_O_20210525_000080/verifyFlatExpStats* ./flatExp.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_flat/*/verifyFlatDetStats/20210525/AT_O_20210525_000080/verifyFlatDetStats* ./flatDet.yaml


linearity
=========

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_linearizer/*/verifyLinearizerStats/verifyLinearizerStats* ./linearizerRun.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_linearizer/*/verifyLinearizerDetStats/verifyLinearizerDetStats* ./linearizerDet.yaml


ptc
===

Run level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_ptc/*/verifyPtcStats/verifyPtcStats* ./ptcRun.yaml

Detector level:

.. code-block:: sh

   cp ../../DATA/ci_cpv_ptc/*/verifyPtcDetStats/verifyPtcDetStats* ./ptcDet.yaml

