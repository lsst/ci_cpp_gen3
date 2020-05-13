# -*- python -*-
import os
from SCons.Script import SConscript, Environment, GetOption, Default
from lsst.sconsUtils.utils import libraryLoaderEnvironment
SConscript(os.path.join(".", "bin.src", "SConscript"))

env = Environment(ENV=os.environ)
env["ENV"]["OMP_NUM_THREADS"] = "1"  # Disable threading; we're parallelising at a higher level


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

def runPipeline(calibName, calibDependency):
    output = env.Command(os.path.join(REPO_ROOT, "calibs", calibName), calibDependency,
                         ["bin/{}_pipeline.sh {}".format(calibName, num_process)])
    env.Alias(calibName, output)
    return(output)

TESTDATA_ROOT = env.ProductDir("testdata_latiss_cpp")
PKG_ROOT = env.ProductDir("ci_cpp_gen3")
print(PKG_ROOT)
REPO_ROOT = os.path.join(PKG_ROOT, "DATA")
num_process = GetOption('num_jobs')

# Create butler
butler = env.Command([os.path.join(REPO_ROOT, "butler.yaml"),
                      os.path.join(REPO_ROOT, "gen3.sqlite3")], "bin",
                     [getExecutableCmd("daf_butler", "butler", "create", REPO_ROOT)])
env.Alias("butler", butler)

# Register instrument.
instrument = env.Command(os.path.join(REPO_ROOT, "calib"), butler,
                         [getExecutableCmd("daf_butler", "butler", "register-instrument", REPO_ROOT,
                                           "-i", "lsst.obs.lsst.Latiss")])
env.Alias("instrument", instrument)

# Ingest curated calibs
# calibs = env.Command(os.path.join(REPO_ROOT, "defects"), instrument,
#                     [getExecutableCmd("daf_butler", "butler", "write-curated-calibrations", REPO_ROOT,
#                                       "-i", "lsst.obs.lsst.Latiss", "--output-run", "calib/latiss")])
# env.Alias("calibs", calibs)
                     
# Inegest raws:
raws = env.Command(os.path.join(REPO_ROOT, "raw"), instrument,
                   [getExecutableCmd("ci_cpp_gen3", "ingestRaws.py",
                                     REPO_ROOT,
                                     os.path.join(TESTDATA_ROOT, "raw"))])
env.Alias("ingest", raws)

# Copied pattern:
# bias = env.Command(os.path.join(REPO_ROOT, "calibs", "bias"), raws,
#                   ["bin/bias_pipeline.sh {}".format(num_process)])
# env.Alias("bias", bias)
# Rewritten to be less redundant:
# bias = runPipeline("bias", raws)

# linearity = runPipeline("linearity", bias)
# ct = runPipeline("crosstalk", linearity)
# defects = runPipeline("defects", ct)
# dark = runPipeline("dark", bias)  # defects?
# gain = runPipeline("gain", dark)
# bfkernel = runPipeline("bfkernel", gain)
# flat = runPipeline("flat", bfkernel)
# fringe = runPipeline("fringe", flat)

# science = runPipeline("science", flat)


everything = [butler, instrument, raws] 
# everything.extend([bias, dark, flat, science])
# everything.extend([linearity, ct, defects, gains])

env.Alias("install", "SConstruct")

env.Alias("all", everything)
Default(everything)

env.Clean(everything, [y for x in everything for y in x])

