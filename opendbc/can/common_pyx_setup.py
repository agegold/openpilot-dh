import os
import subprocess
import sysconfig
import platform
from distutils.core import Extension, setup  # pylint: disable=import-error,no-name-in-module

from Cython.Build import cythonize
from Cython.Distutils import build_ext


ANNOTATE = os.getenv('ANNOTATE') is not None
BASEDIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../../"))


def get_ext_filename_without_platform_suffix(filename):
  name, ext = os.path.splitext(filename)
  ext_suffix = sysconfig.get_config_var('EXT_SUFFIX')

  if ext_suffix == ext:
    return filename

  ext_suffix = ext_suffix.replace(ext, '')
  idx = name.find(ext_suffix)

  if idx == -1:
    return filename
  else:
    return name[:idx] + ext


class BuildExtWithoutPlatformSuffix(build_ext):
  def get_ext_filename(self, ext_name):
    filename = super().get_ext_filename(ext_name)
    return get_ext_filename_without_platform_suffix(filename)


extra_compile_args = ["-std=c++14"]
ARCH = subprocess.check_output(["uname", "-m"], encoding='utf8').rstrip()  # pylint: disable=unexpected-keyword-arg
if ARCH == "aarch64":
  extra_compile_args += ["-Wno-deprecated-register"]

if platform.system() == "Darwin":
  libdbc = "libdbc.dylib"
else:
  libdbc = "libdbc.so"

extra_link_args = [os.path.join(BASEDIR, 'opendbc', 'can', libdbc)]
include_dirs = [
  BASEDIR,
  os.path.join(BASEDIR, 'phonelibs'),
]

# Build CAN Parser

setup(name='CAN parser',
      cmdclass={'build_ext': BuildExtWithoutPlatformSuffix},
      ext_modules=cythonize(
        Extension(
          "parser_pyx",
          language="c++",
          sources=['parser_pyx.pyx'],
          extra_compile_args=extra_compile_args,
          include_dirs=include_dirs,
          extra_link_args=extra_link_args,
        ),
        nthreads=4,
        annotate=ANNOTATE
      ),
)

if platform.system() == "Darwin":
  os.system("install_name_tool -change opendbc/can/libdbc.dylib " + BASEDIR + "/opendbc/can/libdbc.dylib parser_pyx.so")


# Build CAN Packer

setup(name='CAN packer',
      cmdclass={'build_ext': BuildExtWithoutPlatformSuffix},
      ext_modules=cythonize(
        Extension(
          "packer_pyx",
          language="c++",
          sources=['packer_pyx.pyx'],
          extra_compile_args=extra_compile_args,
          include_dirs=include_dirs,
          extra_link_args=extra_link_args,
        ),
        nthreads=4,
        annotate=ANNOTATE
      ),
)

if platform.system() == "Darwin":
  os.system("install_name_tool -change opendbc/can/libdbc.dylib " + BASEDIR + "/opendbc/can/libdbc.dylib packer_pyx.so")
