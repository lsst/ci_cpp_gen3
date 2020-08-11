# -*- python -*-
import os
import yaml

from SCons.Script import SConscript, Environment, GetOption, Default
from lsst.sconsUtils.utils import libraryLoaderEnvironment
SConscript(os.path.join(".", "bin.src", "SConscript"))

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading; we're parallelising at a higher level


TESTDATA_ROOT = env.ProductDir("testdata_latiss_cpp")
PKG_ROOT = env.ProductDir("ci_cpp_gen3")
REPO_ROOT = os.path.join(PKG_ROOT, "DATA")
num_process = GetOption('num_jobs')

# Load exposure lists from testdata repo, to ensure consistency.
with open(os.path.join(TESTDATA_ROOT, "raw", "manifest.yaml")) as f:
    exposureDict = yaml.safe_load(f)

# Define the collections here, so they can be used by name below.
RAW_COLLECTION = 'LATISS/raw/all'
CALIB_COLLECTION = 'LATISS/calib'
USE_COLLECTION = 'calib/v00'

biasCollection = ",".join([RAW_COLLECTION, CALIB_COLLECTION])
genCollection = ",".join([RAW_COLLECTION, CALIB_COLLECTION, USE_COLLECTION])

# Copied from ci_hsc_gen3:
def getExecutableCmd(package, script, *args, directory=None):
    """
    Given the name of a package and a script or other executable which lies
    within the given subdirectory (defaults to "bin"), return an appropriate
    string which can be used to set up an appropriate environment and execute
    the command.
    This includes:
    * Specifying an explict list of paths to be searched by the dynamic linker;
    * Specifying a Python executable to be run (we assume the one on the
      default ${PATH} is appropriate);
    * Specifying the complete path to the script.
    """
    if directory is None:
        directory = "bin"
    cmds = [libraryLoaderEnvironment(), "python", os.path.join(env.ProductDir(package), directory, script)]
    cmds.extend(args)
    return " ".join(cmds)

def getPipeTaskCmd(stage, expList, inputCollections, pipelineFile):
    """
    Construct a pipetask command in a uniform way.
    """
    pipelineYaml = os.path.join(env.ProductDir('obs_lsst'), 'pipelines', 'latiss', pipelineFile)
    if not os.path.exists(pipelineYaml):
        pipelineYaml = os.path.join(env.ProductDir('cp_pipe'), 'pipelines', pipelineFile)

    cmds = ['pipetask run -j', str(num_process), '-d "detector=0 AND exposure IN (',
            ','.join(str(exp) for exp in expList), ')"',
            f"-b {REPO_ROOT}/butler.yaml", f"-i {inputCollections}",
            f"-o ci_cpp_{stage}", f"-p {pipelineYaml}",
            '--register-dataset-types', '--no-versions']
    return " ".join(cmds)

def getCertifyCmd(stage):
    """
    Construct a certify command in a uniform way.
    """
    return getExecutableCmd('cp_pipe', 'certifyCalibration.py',
                            f"{REPO_ROOT}", f"ci_cpp_{stage}",
                            USE_COLLECTION, '-b 1980-01-01',
                            '-e 2050-01-01', stage)


# Create butler
butler = env.Command(".scons_butler", "bin",
                     [getExecutableCmd("daf_butler", "butler", "create", REPO_ROOT),
                      Touch(".scons_butler")
                  ])
env.Alias("butler", butler)

# Register instrument.
instrument = env.Command(".scons_instrument", ".scons_butler",
                         [getExecutableCmd("daf_butler", "butler", "register-instrument", REPO_ROOT,
                                           "lsst.obs.lsst.Latiss"),
                          Touch(".scons_instrument")
                      ])
env.Alias("instrument", instrument)

# Ingest curated calibs
curatedCalibrations = env.Command(".scons_curated", ".scons_instrument",
                                  [getExecutableCmd("daf_butler", "butler", "write-curated-calibrations",
                                                    REPO_ROOT,
                                                    "-i", "lsst.obs.lsst.Latiss"),
                                   Touch(".scons_curated")
                               ])
env.Alias("curatedCalibrations", curatedCalibrations)
                     
# Ingest raws:
raws = env.Command(".scons_ingest", ".scons_curated",
                   [getExecutableCmd("daf_butler", "butler", "ingest-raws",
                                     REPO_ROOT,
                                     "-d", os.path.join(TESTDATA_ROOT, "raw", "2020-01-28")),
                    Touch(".scons_ingest")
                ])
ingest = env.Alias("ingest", raws)

# Bias
bias = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_bias'), ".scons_ingest",
                   [getPipeTaskCmd('bias', exposureDict['biasExposures'],
                                   biasCollection, 'cpBias.yaml'),
                    getCertifyCmd('bias')])
env.Alias('bias', bias)

# Dark
dark = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_dark'), bias,
                   [getPipeTaskCmd('dark', exposureDict['darkExposures'],
                                   genCollection, 'cpDark.yaml'),
                    getCertifyCmd('dark')])
env.Alias('dark', dark)

# Flat
flat = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_flat'), dark,
                   [getPipeTaskCmd('flat', exposureDict['flatExposures'],
                                   genCollection, 'cpFlat.yaml'),
                    getCertifyCmd('flat')])
env.Alias('flat', flat)

# Crosstalk
crosstalk = env.Command(os.path.join(REPO_ROOT, f'ci_cpp_crosstalk'), dark,
                        [getPipeTaskCmd('crosstalk', exposureDict['scienceExposures'],
                                        genCollection, 'measureCrosstalk.yaml'),
                         getCertifyCmd('crosstalk')])
env.Alias('crosstalk', crosstalk)

# Science
scienceYaml = os.path.join(PKG_ROOT, 'pipelines', 'runIsr.yaml')
sciExposures = ",".join([str(vv) for vv in exposureDict['scienceExposures']])
science = env.Command(os.path.join(REPO_ROOT, 'science'), [crosstalk, flat],
                      [getExecutableCmd('ctrl_mpexec', 'pipetask',
                                        'run -j', str(num_process),
                                        f'-d "detector=0 AND exposure IN ({sciExposures})"',
                                        f"-b {REPO_ROOT}/butler.yaml", f"-i {genCollection}",
                                        f"-o science",
                                        f"-p {scienceYaml}",
                                        '--register-dataset-types'
                                    )])
env.Alias('science', science)

# Tests and bookkeeping
everything = [butler, instrument, raws] 
everything.extend([bias, dark, flat, crosstalk, science])
# These need gen3 conversion first.
# everything.extend([ptc, bfk, linearity, defects, gains])

# everything.extend([tests])
SConscript(os.path.join(".", "bin.src", "SConscript"))
env.Alias("install", "SConstruct")

env.Alias("all", everything + ["tests"])
Default(everything)

env.Clean(everything, [y for x in everything for y in x] + ['DATA'])

