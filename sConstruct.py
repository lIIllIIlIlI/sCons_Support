# Every call of sConstruct builds exactly one elf file

import os
import sys
import subprocess
import SCons

from SCons.Subst import quote_spaces
from pathlib import Path
from classes.buildInfoClass import loadBuildInfo

EnsureSConsVersion(4, 3, 0)

# buildInfo stores all kind of environment and build information
buildInfo = loadBuildInfo()


def print_cmd_line(s, target, source, env):
    """
    Override default SCons print routine.
    """
    # for linking, more than one source in specified
    # for compiling, exactly one source per target is specified.
    if len(source) > 1:
        print("\nLinking '{}' ... ".format(str(target[0])))
    else:
        print("Compiling '{}' ...".format(str(source[0])))
    # Regular output in python is buffered. Since the actual printing
    # is done by pop through subprocess, every print statement needs
    # to be enforced on the spot to allow smooth printing.
    sys.stdout.flush()

class ourSpawn:
    """
    Spawn class required to overcome problem with to long command lines see:
    https://github.com/SCons/scons/wiki/LongCmdLinesOnWin32
    """

    def ourspawn(self, sh, escape, cmd, args, env):
        newargs = ' '.join(args[1:])
        cmdline = cmd + " " + newargs
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        proc = subprocess.Popen(cmdline, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, startupinfo=startupinfo, shell=False, env=env)
        data, err = proc.communicate()
        rv = proc.wait()
        if rv:
            print("=====")
            print(err)
            print("=====")
        return rv

def SetupSpawn(env):
    """
        Generates class element required to overcome problem with to long command lines see:
        https://github.com/SCons/scons/wiki/LongCmdLinesOnWin32
    """
    if sys.platform == 'win32':
        buf = ourSpawn()
        buf.ourenv = env
        env['SPAWN'] = buf.ourspawn

# Place build results in outputPath directory instead of the source code directory
VariantDir(buildInfo.pathInfo.outputPath, buildInfo.pathInfo.sourceCodePath)

# pipes the outside PATH variable into scons
env = Environment(
    # pipes all output to the print_cmd_line function in order to use the custom logger
    # instead of simple print output
    # PRINT_CMD_LINE_FUNC=print_cmd_line,
    # sCons usually hides the user path variables in order to guarantee reproducable builds. Since bob already
    # takes care of this and we want to inject custom pathes, the user path variable is piped to scons.
    ENV={'PATH': os.environ['PATH']},
    # C flags. The current implmeenteation merges includes, defines and actual flags in this variable
    CCFLAGS = buildInfo.toolchain.compilerFlags,
    ASFLAGS = buildInfo.toolchain.assemblerFlags,
    LINKFLAGS = buildInfo.toolchain.linkerFlags,

    OBJSUFFIX = ".o",
    PROGSUFFIX = buildInfo.runInfo.elfSuffix,

    CCCOM = buildInfo.toolchain.CCompilerCommand,
    # 'CXXCOM' buildInfo.toolchain.CPlusPlusompilerCommand,
    ASCOM = buildInfo.toolchain.assemblerCommand,
    LINKCOM = buildInfo.toolchain.linkerCommand,

    CC = buildInfo.softwareInfo.getCompiler(buildInfo.runInfo.architecture),
    # 'CXX'= buildInfo.softwareInfo.getCPlusPlusCompiler(buildInfo.runInfo.architecture),
    AS = buildInfo.softwareInfo.getAssembler(buildInfo.runInfo.architecture),
    LINK = buildInfo.softwareInfo.getLinker(buildInfo.runInfo.architecture),
    TEMPFILEARGESCFUNC = tempfile_arg_esc_func
)

# when SetupSpawn is used on TLE987 toolchain, the compiler license cant be found
# anymore. Yet dealing with too long link commands is a problem that has to be 
# solved for TLE987 as well once the assembler problem is fixed. 
if buildInfo.runInfo.architecture != "TLE987":
    SetupSpawn(env)

sourceFiles = buildInfo.pathInfo.sourceCodeFiles

env.Program(buildInfo.pathInfo.hexFile, sourceFiles)



