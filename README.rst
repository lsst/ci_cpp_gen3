###########
ci_cpp_gen3
###########

``ci_cpp_gen3`` provides a test bed in which all calibration products are produced from raw exposures, and includes the processing of a science exposure using those generated calibration products.


Test data
=========

The test data for this package is available in the ``testdata_latiss_cpp`` package, which must be setup prior to building this package.

Usage
=====

Set up the package
------------------

Both ``testdata_latiss_cpp`` and ``ci_cpp_gen3`` must be setup in eups in order to run the tests in this package.

  $ cd PATH_TO_TESTDATA_LATISS_CPP
  $ setup -r .
  $ cd PATH_TO_CI_CPP_GEN3
  $ setup -kr .

Running the tests
-----------------

After setting up both packages, ``scons -j N`` can be used to start calibration production and execute tests on the output products.  The ``-j N`` parameter defines the number of concurrent processes that the individual ``pipetask`` commands will use.

All processing and output products will be produced in the ``DATA/`` subdirectory.  Each output product is generated into an output butler collection of the form ``ci_cpp_PRODUCT``.  The final repository size will be approximately 20GB after a successful run.

Cleaning up
-----------
This package cannot be resumed after a failure, so the ``scons -c`` command should be run prior to any rerun, regardless of the success status of the previous one.
