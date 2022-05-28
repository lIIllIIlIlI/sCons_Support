import os
import sys
import subprocess
import SCons

from SCons.Subst import quote_spaces
from pathlib import Path
from classes.buildInfoClass import loadBuildInfo

buildInfo = loadBuildInfo()

EnsureSConsVersion(4, 3, 0)

def LinkDir(src, trg):
    VariantDir(trg, src, duplicate = 1)
    return trg

linkedDir = LinkDir(buildInfo.pathInfo.sourceCodePath, buildInfo.pathInfo.outputPath)

# pipes the outside PATH variable into scons
env = Environment(
    # sCons usually hides the user path variables in order to guarantee reproducable builds. Since bob already
    # takes care of this and we want to inject custom pathes, the user path variable is piped to scons.
    ENV = os.environ,
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
)

moduleFlags = buildInfo.toolchain.generaleModuleCompilerFlags

sourceFiles = buildInfo.pathInfo.sourceCodeFiles

linkedSourceList = [linkedDir + "\\" + str(Path("06_MCAL/Adc") / Path(sourceFile).stem) for sourceFile in sourceFiles]
for source in sourceFiles:
    _ = LinkDir(Path(source).parent, str(Path(linkedDir) / Path(source).stem))

objectList = env.Object(linkedSourceList)

env.Program(buildInfo.pathInfo.elfFile, objectList)


