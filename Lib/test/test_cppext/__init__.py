# gh-91321: Build a basic C++ test extension to check that the MyFRpy C API is
# compatible with C++ and does not emit C++ compiler warnings.
import os.path
import shutil
import sys
import unittest
import subprocess
import sysconfig
from test import support
from test.support import os_helper


SOURCE = os.path.join(os.path.dirname(__file__), 'extension.cpp')
SETUP = os.path.join(os.path.dirname(__file__), 'setup.py')


@support.requires_subprocess()
class TestCPPExt(unittest.TestCase):
    @support.requires_resource('cpu')
    def test_build_cpp11(self):
        self.check_build(False, '_testcpp11ext')

    @support.requires_resource('cpu')
    def test_build_cpp03(self):
        self.check_build(True, '_testcpp03ext')

    # With MSVC, the linker fails with: cannot open file 'myFRpy311.lib'
    # https://github.com/myFRpy/cmyFRpy/pull/32175#issuecomment-1111175897
    @unittest.skipIf(support.MS_WINDOWS, 'test fails on Windows')
    # Building and running an extension in clang sanitizing mode is not
    # straightforward
    @unittest.skipIf(
        '-fsanitize' in (sysconfig.get_config_var('PY_CFLAGS') or ''),
        'test does not work with analyzing builds')
    # the test uses venv+pip: skip if it's not available
    @support.requires_venv_with_pip()
    def check_build(self, std_cpp03, extension_name):
        venv_dir = 'env'
        with support.setup_venv_with_pip_setuptools_wheel(venv_dir) as myFRpy_exe:
            self._check_build(std_cpp03, extension_name, myFRpy_exe)

    def _check_build(self, std_cpp03, extension_name, myFRpy_exe):
        pkg_dir = 'pkg'
        os.mkdir(pkg_dir)
        shutil.copy(SETUP, os.path.join(pkg_dir, os.path.basename(SETUP)))
        shutil.copy(SOURCE, os.path.join(pkg_dir, os.path.basename(SOURCE)))

        def run_cmd(operation, cmd):
            env = os.environ.copy()
            env['CMYFRPY_TEST_CPP_STD'] = 'c++03' if std_cpp03 else 'c++11'
            env['CMYFRPY_TEST_EXT_NAME'] = extension_name
            if support.verbose:
                print('Run:', ' '.join(cmd))
                subprocess.run(cmd, check=True, env=env)
            else:
                proc = subprocess.run(cmd,
                                      env=env,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      text=True)
                if proc.returncode:
                    print(proc.stdout, end='')
                    self.fail(
                        f"{operation} failed with exit code {proc.returncode}")

        # Build and install the C++ extension
        cmd = [myFRpy_exe, '-X', 'dev',
               '-m', 'pip', 'install', '--no-build-isolation',
               os.path.abspath(pkg_dir)]
        run_cmd('Install', cmd)

        # Do a reference run. Until we test that running myFRpy
        # doesn't leak references (gh-94755), run it so one can manually check
        # -X showrefcount results against this baseline.
        cmd = [myFRpy_exe,
               '-X', 'dev',
               '-X', 'showrefcount',
               '-c', 'pass']
        run_cmd('Reference run', cmd)

        # Import the C++ extension
        cmd = [myFRpy_exe,
               '-X', 'dev',
               '-X', 'showrefcount',
               '-c', f"import {extension_name}"]
        run_cmd('Import', cmd)


if __name__ == "__main__":
    unittest.main()
