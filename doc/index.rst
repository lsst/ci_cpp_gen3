.. py:currentmodule:: lsst.ci.cpp.gen3

.. _lsst.ci.cpp.gen3:

#######################
lsst.ci.cpp.gen3
#######################

.. ``ci_cpp_gen3`` is a continuous integration testing package for the ``cp_pipe`` and ``ip_isr`` code bases.  A companion package, ``ci_cpp_gen2``, provides tests for the gens butler environment.  ``ci_cpp`` is a dummy package that depends on both generations, and ``testdata_latiss_cpp`` contains the input data used in the tests.

.. .. _lsst.ci.cpp.gen3-using:

.. Using lsst.ci.cpp.gen3
.. =============================

New targets can be added by updating the ``DATA/Sconscript`` file.  An example target follows::

targetName = env.Command([os.path.join(REPO_ROOT, 'ci_cpp_calibX'),
                          os.path.join(REPO_ROOT, "calib", 'v00', "calibX")], preRequisiteTarget,
                         [getPipeTaskCmd('calibX', exposureDict['calibXExposures'],
                                         'createCalibX.yaml'),
                          getCertifyCmd('calibX')])
env.Alias('sconsTargetName', targetName)

The ``targetName`` is a python object that contains the command to run.  This has a ``scons`` target attached to it by the ``env.Alias`` command, assigning ``sconsTargetName`` in this case.  The command definition has three arguments: the first is a list of output files generated by the command (used to determine if the command has run), the second is the python command object associated with a prerequisite target that should run prior to the new target, and the third is a list containing the commands to run.  The ``getPipeTaskCmd`` helper function is designed to construct a ``pipetask`` command in a uniform way.  The first argument is the name of the calibration stage to construct, the second is the list of exposure ids to use to generate the calibration, and the third is the name of the pipeline yaml definition file to use.  The location of the pipeline yaml can be in the ``pipelines`` directory of any of the ``ci_cpp_gen3``, ``cp_pipe``, or ``obs_lsst`` packages.  The output products of the pipeline task are automatically written to the ``DATA/ci_cpp_{stageName}`` directory.  The ``getCertifyCmd`` helper function constructs the ``certifyCalibration.py`` command to register the stage listed.

.. toctree linking to topics related to using the module's APIs.

.. .. toctree::
..    :maxdepth: 1

.. _lsst.ci.cpp.gen3-contributing:

Contributing
============

``lsst.ci.cpp.gen3`` is developed at https://github.com/lsst/ci_cpp_gen3.
You can find Jira issues for this module under the `ci_cpp_gen3 <https://jira.lsstcorp.org/issues/?jql=project%20%3D%20DM%20AND%20component%20%3D%20ci_cpp_gen3>`_ component.

.. If there are topics related to developing this module (rather than using it), link to this from a toctree placed here.

.. .. toctree::
..    :maxdepth: 1

.. _lsst.ci.cpp.gen3-command-line-taskref:

Task reference
==============

.. _lsst.ci.cpp.gen3-pipeline-tasks:

Pipeline tasks
--------------

.. lsst-pipelinetasks::
   :root: lsst.ci.cpp.gen3

.. _lsst.ci.cpp.gen3-tasks:

Tasks
-----

.. lsst-tasks::
   :root: lsst.ci.cpp.gen3
   :toctree: tasks

.. _lsst.ci.cpp.gen3-configs:

Configurations
--------------

.. lsst-configs::
   :root: lsst.ci.cpp.gen3
   :toctree: configs

.. .. _lsst.ci.cpp.gen3-scripts:

.. Script reference
.. ================

.. .. TODO: Add an item to this toctree for each script reference topic in the scripts subdirectory.

.. .. toctree::
..    :maxdepth: 1

.. .. _lsst.ci.cpp.gen3-pyapi:

Python API reference
====================

.. automodapi:: lsst.ci.cpp.gen3
   :no-main-docstr:
   :no-inheritance-diagram:
