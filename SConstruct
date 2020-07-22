# -*- python -*-
import os
from SCons.Script import SConscript, Environment, GetOption, Default
from lsst.sconsUtils.utils import libraryLoaderEnvironment
SConscript(os.path.join(".", "bin.src", "SConscript"))

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading; we're parallelising at a higher level


TESTDATA_ROOT = env.ProductDir("testdata_latiss_cpp")
PKG_ROOT = env.ProductDir("ci_cpp_gen3")
print(PKG_ROOT)
REPO_ROOT = os.path.join(PKG_ROOT, "DATA")
print(REPO_ROOT)
num_process = GetOption('num_jobs')

# Define the collections here, so they can be used by name below.
RAW_COLLECTION = 'raws/latiss'
CALIB_COLLECTION = 'calibs/latiss'
USE_COLLECTION = 'calib/v00'

biasCollection = ",".join([RAW_COLLECTION, CALIB_COLLECTION])
genCollection = ",".join([RAW_COLLECTION, CALIB_COLLECTION, USE_COLLECTION])

iteration = ''

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
            f"-o ci_cpp_{stage}{iteration}", f"-p {pipelineYaml}",
            '--register-dataset-types', '--no-versions']
    return " ".join(cmds)

def getCertifyCmd(stage):
    """
    Construct a certify command in a uniform way.
    """
    return getExecutableCmd('cp_pipe', 'blessCalibration.py',
                            f"{REPO_ROOT}", f"ci_cpp_{stage}{iteration}",
                            USE_COLLECTION, '-b 1980-01-01',
                            '-e 2050-01-01', stage)

# Create butler
butler = env.Command([os.path.join(REPO_ROOT, "butler.yaml"),
                      os.path.join(REPO_ROOT, "gen3.sqlite3")], "bin",
                     [getExecutableCmd("daf_butler", "butler", "create", REPO_ROOT)])
env.Alias("butler", butler)

# Register instrument.
instrument = env.Command(os.path.join(REPO_ROOT, "instrument"), butler,
                         [getExecutableCmd("daf_butler", "butler", "register-instrument", REPO_ROOT,
                                           "lsst.obs.lsst.Latiss"),
                          f"echo exists > {REPO_ROOT}/instrument"
                          ])
env.Alias("instrument", instrument)

# Ingest curated calibs
curatedCalibrations = env.Command(os.path.join(REPO_ROOT, "defects"), instrument,
                                  [getExecutableCmd("daf_butler", "butler", "write-curated-calibrations",
                                                    REPO_ROOT,
                                                    "-i", "lsst.obs.lsst.Latiss",
                                                    "--output-run", CALIB_COLLECTION)])
env.Alias("curatedCalibrations", curatedCalibrations)
                     
# Ingest raws:
raws = env.Command(os.path.join(REPO_ROOT, "raw"), [curatedCalibrations],
                   [getExecutableCmd("daf_butler", "butler", "ingest-raws",
                                     REPO_ROOT,
                                     "-d", os.path.join(TESTDATA_ROOT, "raw", "2020-01-28"),
                                     "--output-run", RAW_COLLECTION)])
ingest = env.Alias("ingest", raws)

# Bias
biasExposures = [2020012800007, 2020012800008, 2020012800009, 2020012800010]
bias = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_bias'), ingest,
                   [getPipeTaskCmd('bias', biasExposures, biasCollection, 'cpBias.yaml'),
                    getCertifyCmd('bias')])
env.Alias('bias', bias)

# Dark
darkExposures = [2020012800014, 2020012800015, 2020012800016, 2020012800019, 2020012800020,
                 2020012800021, 2020012800024, 2020012800025, 2020012800026]
dark = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_dark'), bias,
                   [getPipeTaskCmd('dark', darkExposures, genCollection, 'cpDark.yaml'),
                    getCertifyCmd('dark')])
env.Alias('dark', dark)

# Flat
# Use a subset of all the flats (which are needed for PTC).
flatExposures = [2020012800028, 2020012800029, 2020012800030, 2020012800031,
                 2020012800032, 2020012800033, 2020012800034, 2020012800035,
                 2020012800036, 2020012800037, 2020012800038, 2020012800039,
                 2020012800040, 2020012800041, 2020012800042, 2020012800043,
                 2020012800044, 2020012800045, 2020012800046, 2020012800047,
                 2020012800048, 2020012800049, 2020012800050, 2020012800051,
                 2020012800052, 2020012800053, 2020012800054, 2020012800055,
                 2020012800056, 2020012800057, 2020012800058, 2020012800059,
                 2020012800060, 2020012800061, 2020012800062, 2020012800063,
                 2020012800064, 2020012800065, 2020012800066, 2020012800067,
                 2020012800068, 2020012800069, 2020012800070, 2020012800071,
                 2020012800072, 2020012800073, 2020012800074, 2020012800075,
                 2020012800076, 2020012800077, 2020012800078, 2020012800079,
                 2020012800080, 2020012800081, 2020012800082, 2020012800083,
                 2020012800084, 2020012800085, 2020012800086, 2020012800087,
                 2020012800088, 2020012800089, 2020012800090, 2020012800091,
                 2020012800092, 2020012800093, 2020012800094, 2020012800095,
                 2020012800096, 2020012800097, 2020012800098, 2020012800099,
                 2020012800100, 2020012800101, 2020012800102, 2020012800103,
                 2020012800104, 2020012800105, 2020012800106, 2020012800107,
                 2020012800108]

flatExposures = [2020012800028, 2020012800032, 2020012800036, 2020012800040,
                 2020012800044, 2020012800048, 2020012800052, 2020012800056,
                 2020012800060, 2020012800064, 2020012800068, 2020012800072,
                 2020012800076, 2020012800080, 2020012800084, ]
flat = env.Command(os.path.join(REPO_ROOT, 'ci_cpp_flat'), dark,
                   [getPipeTaskCmd('flat', flatExposures, genCollection, 'cpFlat.yaml'),
                    getCertifyCmd('flat')])
env.Alias('flat', flat)

# Crosstalk
scienceExposures = [2020012800254, 2020012800256, 2020012800255, 2020012800257]

crosstalk = env.Command(os.path.join(REPO_ROOT, f'ci_cpp_crosstalk{iteration}'), dark,
                        [getPipeTaskCmd('crosstalk', scienceExposures,
                                        genCollection, 'measureCrosstalk.yaml'),
                         getCertifyCmd('crosstalk')])
env.Alias('crosstalk', crosstalk)

# Science

scienceYaml = os.path.join(PKG_ROOT, 'pipelines', 'runIsr.yaml')
science = env.Command(os.path.join(REPO_ROOT, 'science'), crosstalk,
                      [" ".join(
                          ['pipetask run -j', str(num_process), '-d "detector=0 AND exposure IN (',
                           ','.join(str(exp) for exp in scienceExposures), ')"',
                           f"-b {REPO_ROOT}/butler.yaml", f"-i {genCollection}",
                           f"-o science", f"-p {scienceYaml}",
                           '--register-dataset-types', '--no-versions'
                           ])])
env.Alias('science', science)

everything = [butler, instrument, raws] 
everything.extend([bias, dark, flat, science])
# everything.extend([linearity, ct, defects, gains])

env.Alias("install", "SConstruct")

env.Alias("all", everything)
Default(everything)

env.Clean(everything, [y for x in everything for y in x])

