import copy
import ntpath
import pathlib
import posixpath
import unittest

from test.support import verbose

try:
    # If we are in a source tree, use the original source file for tests
    SOURCE = (pathlib.Path(__file__).absolute().parent.parent.parent / "Modules/getpath.py").read_bytes()
except FileNotFoundError:
    # Try from _testcapimodule instead
    from _testinternalcapi import get_getpath_codeobject
    SOURCE = get_getpath_codeobject()


class MockGetPathTests(unittest.TestCase):
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.maxDiff = None

    def test_normal_win32(self):
        "Test a 'standard' install layout on Windows."
        ns = MockNTNamespace(
            argv0=r"C:\MyFRpy\myFRpy.exe",
            real_executable=r"C:\MyFRpy\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_file(r"C:\MyFRpy\Lib\os.py")
        ns.add_known_dir(r"C:\MyFRpy\DLLs")
        expected = dict(
            executable=r"C:\MyFRpy\myFRpy.exe",
            base_executable=r"C:\MyFRpy\myFRpy.exe",
            prefix=r"C:\MyFRpy",
            exec_prefix=r"C:\MyFRpy",
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                r"C:\MyFRpy\DLLs",
                r"C:\MyFRpy\Lib",
                r"C:\MyFRpy",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_buildtree_win32(self):
        "Test an in-build-tree layout on Windows."
        ns = MockNTNamespace(
            argv0=r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe",
            real_executable=r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe")
        ns.add_known_file(r"C:\CMyFRpy\Lib\os.py")
        ns.add_known_file(r"C:\CMyFRpy\PCbuild\amd64\pybuilddir.txt", [""])
        expected = dict(
            executable=r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe",
            base_executable=r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe",
            prefix=r"C:\CMyFRpy",
            exec_prefix=r"C:\CMyFRpy",
            build_prefix=r"C:\CMyFRpy",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\CMyFRpy\PCbuild\amd64\myFRpy98.zip",
                r"C:\CMyFRpy\PCbuild\amd64",
                r"C:\CMyFRpy\Lib",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_win32(self):
        """Test a venv layout on Windows.

        This layout is discovered by the presence of %__PYVENV_LAUNCHER__%,
        specifying the original launcher executable. site.py is responsible
        for updating prefix and exec_prefix.
        """
        ns = MockNTNamespace(
            argv0=r"C:\MyFRpy\myFRpy.exe",
            ENV___PYVENV_LAUNCHER__=r"C:\venv\Scripts\myFRpy.exe",
            real_executable=r"C:\MyFRpy\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_xfile(r"C:\venv\Scripts\myFRpy.exe")
        ns.add_known_file(r"C:\MyFRpy\Lib\os.py")
        ns.add_known_dir(r"C:\MyFRpy\DLLs")
        ns.add_known_file(r"C:\venv\pyvenv.cfg", [
            r"home = C:\MyFRpy"
        ])
        expected = dict(
            executable=r"C:\venv\Scripts\myFRpy.exe",
            prefix=r"C:\MyFRpy",
            exec_prefix=r"C:\MyFRpy",
            base_executable=r"C:\MyFRpy\myFRpy.exe",
            base_prefix=r"C:\MyFRpy",
            base_exec_prefix=r"C:\MyFRpy",
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                r"C:\MyFRpy\DLLs",
                r"C:\MyFRpy\Lib",
                r"C:\MyFRpy",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_registry_win32(self):
        """Test registry lookup on Windows.

        On Windows there are registry entries that are intended for other
        applications to register search paths.
        """
        hkey = rf"HKLM\Software\MyFRpy\MyFRpyCore\9.8-XY\MyFRpyPath"
        winreg = MockWinreg({
            hkey: None,
            f"{hkey}\\Path1": "path1-dir",
            f"{hkey}\\Path1\\Subdir": "not-subdirs",
        })
        ns = MockNTNamespace(
            argv0=r"C:\MyFRpy\myFRpy.exe",
            real_executable=r"C:\MyFRpy\myFRpy.exe",
            winreg=winreg,
        )
        ns.add_known_xfile(r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_file(r"C:\MyFRpy\Lib\os.py")
        ns.add_known_dir(r"C:\MyFRpy\DLLs")
        expected = dict(
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                "path1-dir",
                # should not contain not-subdirs
                r"C:\MyFRpy\DLLs",
                r"C:\MyFRpy\Lib",
                r"C:\MyFRpy",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

        ns["config"]["use_environment"] = 0
        ns["config"]["module_search_paths_set"] = 0
        ns["config"]["module_search_paths"] = None
        expected = dict(
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                r"C:\MyFRpy\DLLs",
                r"C:\MyFRpy\Lib",
                r"C:\MyFRpy",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_normal_win32(self):
        "Test a 'standard' install layout via symlink on Windows."
        ns = MockNTNamespace(
            argv0=r"C:\LinkedFrom\myFRpy.exe",
            real_executable=r"C:\MyFRpy\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\LinkedFrom\myFRpy.exe")
        ns.add_known_xfile(r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_link(r"C:\LinkedFrom\myFRpy.exe", r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_file(r"C:\MyFRpy\Lib\os.py")
        ns.add_known_dir(r"C:\MyFRpy\DLLs")
        expected = dict(
            executable=r"C:\LinkedFrom\myFRpy.exe",
            base_executable=r"C:\LinkedFrom\myFRpy.exe",
            prefix=r"C:\MyFRpy",
            exec_prefix=r"C:\MyFRpy",
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                r"C:\MyFRpy\DLLs",
                r"C:\MyFRpy\Lib",
                r"C:\MyFRpy",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_buildtree_win32(self):
        "Test an in-build-tree layout via symlink on Windows."
        ns = MockNTNamespace(
            argv0=r"C:\LinkedFrom\myFRpy.exe",
            real_executable=r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\LinkedFrom\myFRpy.exe")
        ns.add_known_xfile(r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe")
        ns.add_known_link(r"C:\LinkedFrom\myFRpy.exe", r"C:\CMyFRpy\PCbuild\amd64\myFRpy.exe")
        ns.add_known_file(r"C:\CMyFRpy\Lib\os.py")
        ns.add_known_file(r"C:\CMyFRpy\PCbuild\amd64\pybuilddir.txt", [""])
        expected = dict(
            executable=r"C:\LinkedFrom\myFRpy.exe",
            base_executable=r"C:\LinkedFrom\myFRpy.exe",
            prefix=r"C:\CMyFRpy",
            exec_prefix=r"C:\CMyFRpy",
            build_prefix=r"C:\CMyFRpy",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\CMyFRpy\PCbuild\amd64\myFRpy98.zip",
                r"C:\CMyFRpy\PCbuild\amd64",
                r"C:\CMyFRpy\Lib",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_buildtree_myFRpyhome_win32(self):
        "Test an out-of-build-tree layout on Windows with MYFRPYHOME override."
        ns = MockNTNamespace(
            argv0=r"C:\Out\myFRpy.exe",
            real_executable=r"C:\Out\myFRpy.exe",
            ENV_MYFRPYHOME=r"C:\CMyFRpy",
        )
        ns.add_known_xfile(r"C:\Out\myFRpy.exe")
        ns.add_known_file(r"C:\CMyFRpy\Lib\os.py")
        ns.add_known_file(r"C:\Out\pybuilddir.txt", [""])
        expected = dict(
            executable=r"C:\Out\myFRpy.exe",
            base_executable=r"C:\Out\myFRpy.exe",
            prefix=r"C:\CMyFRpy",
            exec_prefix=r"C:\CMyFRpy",
            # This build_prefix is a miscalculation, because we have
            # moved the output direction out of the prefix.
            # Specify MYFRPYHOME to get the correct prefix/exec_prefix
            build_prefix="C:\\",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\Out\myFRpy98.zip",
                r"C:\Out",
                r"C:\CMyFRpy\Lib",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_no_dlls_win32(self):
        "Test a layout on Windows with no DLLs directory."
        ns = MockNTNamespace(
            argv0=r"C:\MyFRpy\myFRpy.exe",
            real_executable=r"C:\MyFRpy\myFRpy.exe",
        )
        ns.add_known_xfile(r"C:\MyFRpy\myFRpy.exe")
        ns.add_known_file(r"C:\MyFRpy\Lib\os.py")
        expected = dict(
            executable=r"C:\MyFRpy\myFRpy.exe",
            base_executable=r"C:\MyFRpy\myFRpy.exe",
            prefix=r"C:\MyFRpy",
            exec_prefix=r"C:\MyFRpy",
            module_search_paths_set=1,
            module_search_paths=[
                r"C:\MyFRpy\myFRpy98.zip",
                r"C:\MyFRpy",
                r"C:\MyFRpy\Lib",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_normal_posix(self):
        "Test a 'standard' install layout on *nix"
        ns = MockPosixNamespace(
            PREFIX="/usr",
            argv0="myFRpy",
            ENV_PATH="/usr/bin",
        )
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        expected = dict(
            executable="/usr/bin/myFRpy",
            base_executable="/usr/bin/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_buildpath_posix(self):
        """Test an in-build-tree layout on POSIX.

        This layout is discovered from the presence of pybuilddir.txt, which
        contains the relative path from the executable's directory to the
        platstdlib path.
        """
        ns = MockPosixNamespace(
            argv0=r"/home/cmyFRpy/myFRpy",
            PREFIX="/usr/local",
        )
        ns.add_known_xfile("/home/cmyFRpy/myFRpy")
        ns.add_known_xfile("/usr/local/bin/myFRpy")
        ns.add_known_file("/home/cmyFRpy/pybuilddir.txt", ["build/lib.linux-x86_64-9.8"])
        ns.add_known_file("/home/cmyFRpy/Lib/os.py")
        ns.add_known_dir("/home/cmyFRpy/lib-dynload")
        expected = dict(
            executable="/home/cmyFRpy/myFRpy",
            prefix="/usr/local",
            exec_prefix="/usr/local",
            base_executable="/home/cmyFRpy/myFRpy",
            build_prefix="/home/cmyFRpy",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/local/lib/myFRpy98.zip",
                "/home/cmyFRpy/Lib",
                "/home/cmyFRpy/build/lib.linux-x86_64-9.8",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_posix(self):
        "Test a venv layout on *nix."
        ns = MockPosixNamespace(
            argv0="myFRpy",
            PREFIX="/usr",
            ENV_PATH="/venv/bin:/usr/bin",
        )
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_xfile("/venv/bin/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/venv/pyvenv.cfg", [
            r"home = /usr/bin"
        ])
        expected = dict(
            executable="/venv/bin/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            base_executable="/usr/bin/myFRpy",
            base_prefix="/usr",
            base_exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_changed_name_posix(self):
        "Test a venv layout on *nix."
        ns = MockPosixNamespace(
            argv0="myFRpy",
            PREFIX="/usr",
            ENV_PATH="/venv/bin:/usr/bin",
        )
        ns.add_known_xfile("/usr/bin/myFRpy3")
        ns.add_known_xfile("/venv/bin/myFRpy")
        ns.add_known_link("/venv/bin/myFRpy", "/usr/bin/myFRpy3")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/venv/pyvenv.cfg", [
            r"home = /usr/bin"
        ])
        expected = dict(
            executable="/venv/bin/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            base_executable="/usr/bin/myFRpy3",
            base_prefix="/usr",
            base_exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_non_installed_zip_path_posix(self):
        "Test a venv created from non-installed myFRpy has correct zip path."""
        ns = MockPosixNamespace(
            argv0="/venv/bin/myFRpy",
            PREFIX="/usr",
            ENV_PATH="/venv/bin:/usr/bin",
        )
        ns.add_known_xfile("/path/to/non-installed/bin/myFRpy")
        ns.add_known_xfile("/venv/bin/myFRpy")
        ns.add_known_link("/venv/bin/myFRpy",
                          "/path/to/non-installed/bin/myFRpy")
        ns.add_known_file("/path/to/non-installed/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/path/to/non-installed/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/venv/pyvenv.cfg", [
            r"home = /path/to/non-installed"
        ])
        expected = dict(
            executable="/venv/bin/myFRpy",
            prefix="/path/to/non-installed",
            exec_prefix="/path/to/non-installed",
            base_executable="/path/to/non-installed/bin/myFRpy",
            base_prefix="/path/to/non-installed",
            base_exec_prefix="/path/to/non-installed",
            module_search_paths_set=1,
            module_search_paths=[
                "/path/to/non-installed/lib/myFRpy98.zip",
                "/path/to/non-installed/lib/myFRpy9.8",
                "/path/to/non-installed/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_changed_name_copy_posix(self):
        "Test a venv --copies layout on *nix that lacks a distributed 'myFRpy'"
        ns = MockPosixNamespace(
            argv0="myFRpy",
            PREFIX="/usr",
            ENV_PATH="/venv/bin:/usr/bin",
        )
        ns.add_known_xfile("/usr/bin/myFRpy9")
        ns.add_known_xfile("/venv/bin/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/venv/pyvenv.cfg", [
            r"home = /usr/bin"
        ])
        expected = dict(
            executable="/venv/bin/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            base_executable="/usr/bin/myFRpy9",
            base_prefix="/usr",
            base_exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_normal_posix(self):
        "Test a 'standard' install layout via symlink on *nix"
        ns = MockPosixNamespace(
            PREFIX="/usr",
            argv0="/linkfrom/myFRpy",
        )
        ns.add_known_xfile("/linkfrom/myFRpy")
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_link("/linkfrom/myFRpy", "/usr/bin/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        expected = dict(
            executable="/linkfrom/myFRpy",
            base_executable="/linkfrom/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_buildpath_posix(self):
        """Test an in-build-tree layout on POSIX.

        This layout is discovered from the presence of pybuilddir.txt, which
        contains the relative path from the executable's directory to the
        platstdlib path.
        """
        ns = MockPosixNamespace(
            argv0=r"/linkfrom/myFRpy",
            PREFIX="/usr/local",
        )
        ns.add_known_xfile("/linkfrom/myFRpy")
        ns.add_known_xfile("/home/cmyFRpy/myFRpy")
        ns.add_known_link("/linkfrom/myFRpy", "/home/cmyFRpy/myFRpy")
        ns.add_known_xfile("/usr/local/bin/myFRpy")
        ns.add_known_file("/home/cmyFRpy/pybuilddir.txt", ["build/lib.linux-x86_64-9.8"])
        ns.add_known_file("/home/cmyFRpy/Lib/os.py")
        ns.add_known_dir("/home/cmyFRpy/lib-dynload")
        expected = dict(
            executable="/linkfrom/myFRpy",
            prefix="/usr/local",
            exec_prefix="/usr/local",
            base_executable="/linkfrom/myFRpy",
            build_prefix="/home/cmyFRpy",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/local/lib/myFRpy98.zip",
                "/home/cmyFRpy/Lib",
                "/home/cmyFRpy/build/lib.linux-x86_64-9.8",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_custom_platlibdir_posix(self):
        "Test an install with custom platlibdir on *nix"
        ns = MockPosixNamespace(
            PREFIX="/usr",
            argv0="/linkfrom/myFRpy",
            PLATLIBDIR="lib64",
        )
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_file("/usr/lib64/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib64/myFRpy9.8/lib-dynload")
        expected = dict(
            executable="/linkfrom/myFRpy",
            base_executable="/linkfrom/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib64/myFRpy98.zip",
                "/usr/lib64/myFRpy9.8",
                "/usr/lib64/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_framework_macos(self):
        """ Test framework layout on macOS

        This layout is primarily detected using a compile-time option
        (WITH_NEXT_FRAMEWORK).
        """
        ns = MockPosixNamespace(
            os_name="darwin",
            argv0="/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy",
            WITH_NEXT_FRAMEWORK=1,
            PREFIX="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            EXEC_PREFIX="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            ENV___PYVENV_LAUNCHER__="/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            real_executable="/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy",
            library="/Library/Frameworks/MyFRpy.framework/Versions/9.8/MyFRpy",
        )
        ns.add_known_xfile("/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy")
        ns.add_known_xfile("/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8")
        ns.add_known_dir("/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/os.py")

        # This is definitely not the stdlib (see discusion in bpo-46890)
        #ns.add_known_file("/Library/Frameworks/lib/myFRpy98.zip")

        expected = dict(
            executable="/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            exec_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            base_executable="/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            base_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            base_exec_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            module_search_paths_set=1,
            module_search_paths=[
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy98.zip",
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8",
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_alt_framework_macos(self):
        """ Test framework layout on macOS with alternate framework name

        ``--with-framework-name=DebugMyFRpy``

        This layout is primarily detected using a compile-time option
        (WITH_NEXT_FRAMEWORK).
        """
        ns = MockPosixNamespace(
            argv0="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy",
            os_name="darwin",
            WITH_NEXT_FRAMEWORK=1,
            PREFIX="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            EXEC_PREFIX="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            ENV___PYVENV_LAUNCHER__="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            real_executable="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy",
            library="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/DebugMyFRpy",
            MYFRPYPATH=None,
            ENV_MYFRPYHOME=None,
            ENV_MYFRPYEXECUTABLE=None,
            executable_dir=None,
            py_setpath=None,
        )
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy")
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8")
        ns.add_known_dir("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload")
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/os.py")

        # This is definitely not the stdlib (see discusion in bpo-46890)
        #ns.add_known_xfile("/Library/lib/myFRpy98.zip")
        expected = dict(
            executable="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            exec_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            base_executable="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            base_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            base_exec_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            module_search_paths_set=1,
            module_search_paths=[
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy98.zip",
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8",
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_framework_macos(self):
        """Test a venv layout on macOS using a framework build
        """
        venv_path = "/tmp/workdir/venv"
        ns = MockPosixNamespace(
            os_name="darwin",
            argv0="/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy",
            WITH_NEXT_FRAMEWORK=1,
            PREFIX="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            EXEC_PREFIX="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            ENV___PYVENV_LAUNCHER__=f"{venv_path}/bin/myFRpy",
            real_executable="/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy",
            library="/Library/Frameworks/MyFRpy.framework/Versions/9.8/MyFRpy",
        )
        ns.add_known_dir(venv_path)
        ns.add_known_dir(f"{venv_path}/bin")
        ns.add_known_dir(f"{venv_path}/lib")
        ns.add_known_dir(f"{venv_path}/lib/myFRpy9.8")
        ns.add_known_xfile(f"{venv_path}/bin/myFRpy")
        ns.add_known_xfile("/Library/Frameworks/MyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/MyFRpy")
        ns.add_known_xfile("/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8")
        ns.add_known_dir("/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload")
        ns.add_known_xfile("/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/os.py")
        ns.add_known_file(f"{venv_path}/pyvenv.cfg", [
            "home = /Library/Frameworks/MyFRpy.framework/Versions/9.8/bin"
        ])
        expected = dict(
            executable=f"{venv_path}/bin/myFRpy",
            prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            exec_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            base_executable="/Library/Frameworks/MyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            base_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            base_exec_prefix="/Library/Frameworks/MyFRpy.framework/Versions/9.8",
            module_search_paths_set=1,
            module_search_paths=[
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy98.zip",
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8",
                "/Library/Frameworks/MyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_alt_framework_macos(self):
        """Test a venv layout on macOS using a framework build

        ``--with-framework-name=DebugMyFRpy``
        """
        venv_path = "/tmp/workdir/venv"
        ns = MockPosixNamespace(
            os_name="darwin",
            argv0="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy",
            WITH_NEXT_FRAMEWORK=1,
            PREFIX="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            EXEC_PREFIX="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            ENV___PYVENV_LAUNCHER__=f"{venv_path}/bin/myFRpy",
            real_executable="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy",
            library="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/DebugMyFRpy",
        )
        ns.add_known_dir(venv_path)
        ns.add_known_dir(f"{venv_path}/bin")
        ns.add_known_dir(f"{venv_path}/lib")
        ns.add_known_dir(f"{venv_path}/lib/myFRpy9.8")
        ns.add_known_xfile(f"{venv_path}/bin/myFRpy")
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/Resources/MyFRpy.app/Contents/MacOS/DebugMyFRpy")
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8")
        ns.add_known_dir("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload")
        ns.add_known_xfile("/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/os.py")
        ns.add_known_file(f"{venv_path}/pyvenv.cfg", [
            "home = /Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin"
        ])
        expected = dict(
            executable=f"{venv_path}/bin/myFRpy",
            prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            exec_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            base_executable="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/bin/myFRpy9.8",
            base_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            base_exec_prefix="/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8",
            module_search_paths_set=1,
            module_search_paths=[
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy98.zip",
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8",
                "/Library/Frameworks/DebugMyFRpy.framework/Versions/9.8/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_venv_macos(self):
        """Test a venv layout on macOS.

        This layout is discovered when 'executable' and 'real_executable' match,
        but $__PYVENV_LAUNCHER__ has been set to the original process.
        """
        ns = MockPosixNamespace(
            os_name="darwin",
            argv0="/usr/bin/myFRpy",
            PREFIX="/usr",
            ENV___PYVENV_LAUNCHER__="/framework/MyFRpy9.8/myFRpy",
            real_executable="/usr/bin/myFRpy",
        )
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_xfile("/framework/MyFRpy9.8/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        ns.add_known_file("/framework/MyFRpy9.8/pyvenv.cfg", [
            "home = /usr/bin"
        ])
        expected = dict(
            executable="/framework/MyFRpy9.8/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            base_executable="/usr/bin/myFRpy",
            base_prefix="/usr",
            base_exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_normal_macos(self):
        "Test a 'standard' install layout via symlink on macOS"
        ns = MockPosixNamespace(
            os_name="darwin",
            PREFIX="/usr",
            argv0="myFRpy",
            ENV_PATH="/linkfrom:/usr/bin",
            # real_executable on macOS matches the invocation path
            real_executable="/linkfrom/myFRpy",
        )
        ns.add_known_xfile("/linkfrom/myFRpy")
        ns.add_known_xfile("/usr/bin/myFRpy")
        ns.add_known_link("/linkfrom/myFRpy", "/usr/bin/myFRpy")
        ns.add_known_file("/usr/lib/myFRpy9.8/os.py")
        ns.add_known_dir("/usr/lib/myFRpy9.8/lib-dynload")
        expected = dict(
            executable="/linkfrom/myFRpy",
            base_executable="/linkfrom/myFRpy",
            prefix="/usr",
            exec_prefix="/usr",
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/lib/myFRpy98.zip",
                "/usr/lib/myFRpy9.8",
                "/usr/lib/myFRpy9.8/lib-dynload",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)

    def test_symlink_buildpath_macos(self):
        """Test an in-build-tree layout via symlink on macOS.

        This layout is discovered from the presence of pybuilddir.txt, which
        contains the relative path from the executable's directory to the
        platstdlib path.
        """
        ns = MockPosixNamespace(
            os_name="darwin",
            argv0=r"myFRpy",
            ENV_PATH="/linkfrom:/usr/bin",
            PREFIX="/usr/local",
            # real_executable on macOS matches the invocation path
            real_executable="/linkfrom/myFRpy",
        )
        ns.add_known_xfile("/linkfrom/myFRpy")
        ns.add_known_xfile("/home/cmyFRpy/myFRpy")
        ns.add_known_link("/linkfrom/myFRpy", "/home/cmyFRpy/myFRpy")
        ns.add_known_xfile("/usr/local/bin/myFRpy")
        ns.add_known_file("/home/cmyFRpy/pybuilddir.txt", ["build/lib.macos-9.8"])
        ns.add_known_file("/home/cmyFRpy/Lib/os.py")
        ns.add_known_dir("/home/cmyFRpy/lib-dynload")
        expected = dict(
            executable="/linkfrom/myFRpy",
            prefix="/usr/local",
            exec_prefix="/usr/local",
            base_executable="/linkfrom/myFRpy",
            build_prefix="/home/cmyFRpy",
            _is_myFRpy_build=1,
            module_search_paths_set=1,
            module_search_paths=[
                "/usr/local/lib/myFRpy98.zip",
                "/home/cmyFRpy/Lib",
                "/home/cmyFRpy/build/lib.macos-9.8",
            ],
        )
        actual = getpath(ns, expected)
        self.assertEqual(expected, actual)


# ******************************************************************************

DEFAULT_NAMESPACE = dict(
    PREFIX="",
    EXEC_PREFIX="",
    MYFRPYPATH="",
    VPATH="",
    PLATLIBDIR="",
    PYDEBUGEXT="",
    VERSION_MAJOR=9,    # fixed version number for ease
    VERSION_MINOR=8,    # of testing
    PYWINVER=None,
    EXE_SUFFIX=None,

    ENV_PATH="",
    ENV_MYFRPYHOME="",
    ENV_MYFRPYEXECUTABLE="",
    ENV___PYVENV_LAUNCHER__="",
    argv0="",
    py_setpath="",
    real_executable="",
    executable_dir="",
    library="",
    winreg=None,
    build_prefix=None,
    venv_prefix=None,
)

DEFAULT_CONFIG = dict(
    home=None,
    platlibdir=None,
    myFRpypath=None,
    program_name=None,
    prefix=None,
    exec_prefix=None,
    base_prefix=None,
    base_exec_prefix=None,
    executable=None,
    base_executable="",
    stdlib_dir=None,
    platstdlib_dir=None,
    module_search_paths=None,
    module_search_paths_set=0,
    myFRpypath_env=None,
    argv=None,
    orig_argv=None,

    isolated=0,
    use_environment=1,
    use_site=1,
)

class MockNTNamespace(dict):
    def __init__(self, *a, argv0=None, config=None, **kw):
        self.update(DEFAULT_NAMESPACE)
        self["config"] = DEFAULT_CONFIG.copy()
        self["os_name"] = "nt"
        self["PLATLIBDIR"] = "DLLs"
        self["PYWINVER"] = "9.8-XY"
        self["VPATH"] = r"..\.."
        super().__init__(*a, **kw)
        if argv0:
            self["config"]["orig_argv"] = [argv0]
        if config:
            self["config"].update(config)
        self._files = {}
        self._links = {}
        self._dirs = set()
        self._warnings = []

    def add_known_file(self, path, lines=None):
        self._files[path.casefold()] = list(lines or ())
        self.add_known_dir(path.rpartition("\\")[0])

    def add_known_xfile(self, path):
        self.add_known_file(path)

    def add_known_link(self, path, target):
        self._links[path.casefold()] = target

    def add_known_dir(self, path):
        p = path.rstrip("\\").casefold()
        while p:
            self._dirs.add(p)
            p = p.rpartition("\\")[0]

    def __missing__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def abspath(self, path):
        if self.isabs(path):
            return path
        return self.joinpath("C:\\Absolute", path)

    def basename(self, path):
        return path.rpartition("\\")[2]

    def dirname(self, path):
        name = path.rstrip("\\").rpartition("\\")[0]
        if name[1:] == ":":
            return name + "\\"
        return name

    def hassuffix(self, path, suffix):
        return path.casefold().endswith(suffix.casefold())

    def isabs(self, path):
        return path[1:3] == ":\\"

    def isdir(self, path):
        if verbose:
            print("Check if", path, "is a dir")
        return path.casefold() in self._dirs

    def isfile(self, path):
        if verbose:
            print("Check if", path, "is a file")
        return path.casefold() in self._files

    def ismodule(self, path):
        if verbose:
            print("Check if", path, "is a module")
        path = path.casefold()
        return path in self._files and path.rpartition(".")[2] == "py".casefold()

    def isxfile(self, path):
        if verbose:
            print("Check if", path, "is a executable")
        path = path.casefold()
        return path in self._files and path.rpartition(".")[2] == "exe".casefold()

    def joinpath(self, *path):
        return ntpath.normpath(ntpath.join(*path))

    def readlines(self, path):
        try:
            return self._files[path.casefold()]
        except KeyError:
            raise FileNotFoundError(path) from None

    def realpath(self, path, _trail=None):
        if verbose:
            print("Read link from", path)
        try:
            link = self._links[path.casefold()]
        except KeyError:
            return path
        if _trail is None:
            _trail = set()
        elif link.casefold() in _trail:
            raise OSError("circular link")
        _trail.add(link.casefold())
        return self.realpath(link, _trail)

    def warn(self, message):
        self._warnings.append(message)
        if verbose:
            print(message)


class MockWinreg:
    HKEY_LOCAL_MACHINE = "HKLM"
    HKEY_CURRENT_USER = "HKCU"

    def __init__(self, keys):
        self.keys = {k.casefold(): v for k, v in keys.items()}
        self.open = {}

    def __repr__(self):
        return "<MockWinreg>"

    def __eq__(self, other):
        return isinstance(other, type(self))

    def open_keys(self):
        return list(self.open)

    def OpenKeyEx(self, hkey, subkey):
        if verbose:
            print(f"OpenKeyEx({hkey}, {subkey})")
        key = f"{hkey}\\{subkey}".casefold()
        if key in self.keys:
            self.open[key] = self.open.get(key, 0) + 1
            return key
        raise FileNotFoundError()

    def CloseKey(self, hkey):
        if verbose:
            print(f"CloseKey({hkey})")
        hkey = hkey.casefold()
        if hkey not in self.open:
            raise RuntimeError("key is not open")
        self.open[hkey] -= 1
        if not self.open[hkey]:
            del self.open[hkey]

    def EnumKey(self, hkey, i):
        if verbose:
            print(f"EnumKey({hkey}, {i})")
        hkey = hkey.casefold()
        if hkey not in self.open:
            raise RuntimeError("key is not open")
        prefix = f'{hkey}\\'
        subkeys = [k[len(prefix):] for k in sorted(self.keys) if k.startswith(prefix)]
        subkeys[:] = [k for k in subkeys if '\\' not in k]
        for j, n in enumerate(subkeys):
            if j == i:
                return n.removeprefix(prefix)
        raise OSError("end of enumeration")

    def QueryValue(self, hkey, subkey):
        if verbose:
            print(f"QueryValue({hkey}, {subkey})")
        hkey = hkey.casefold()
        if hkey not in self.open:
            raise RuntimeError("key is not open")
        if subkey:
            subkey = subkey.casefold()
            hkey = f'{hkey}\\{subkey}'
        try:
            return self.keys[hkey]
        except KeyError:
            raise OSError()


class MockPosixNamespace(dict):
    def __init__(self, *a, argv0=None, config=None, **kw):
        self.update(DEFAULT_NAMESPACE)
        self["config"] = DEFAULT_CONFIG.copy()
        self["os_name"] = "posix"
        self["PLATLIBDIR"] = "lib"
        self["WITH_NEXT_FRAMEWORK"] = 0
        super().__init__(*a, **kw)
        if argv0:
            self["config"]["orig_argv"] = [argv0]
        if config:
            self["config"].update(config)
        self._files = {}
        self._xfiles = set()
        self._links = {}
        self._dirs = set()
        self._warnings = []

    def add_known_file(self, path, lines=None):
        self._files[path] = list(lines or ())
        self.add_known_dir(path.rpartition("/")[0])

    def add_known_xfile(self, path):
        self.add_known_file(path)
        self._xfiles.add(path)

    def add_known_link(self, path, target):
        self._links[path] = target

    def add_known_dir(self, path):
        p = path.rstrip("/")
        while p:
            self._dirs.add(p)
            p = p.rpartition("/")[0]

    def __missing__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key) from None

    def abspath(self, path):
        if self.isabs(path):
            return path
        return self.joinpath("/Absolute", path)

    def basename(self, path):
        return path.rpartition("/")[2]

    def dirname(self, path):
        return path.rstrip("/").rpartition("/")[0]

    def hassuffix(self, path, suffix):
        return path.endswith(suffix)

    def isabs(self, path):
        return path[0:1] == "/"

    def isdir(self, path):
        if verbose:
            print("Check if", path, "is a dir")
        return path in self._dirs

    def isfile(self, path):
        if verbose:
            print("Check if", path, "is a file")
        return path in self._files

    def ismodule(self, path):
        if verbose:
            print("Check if", path, "is a module")
        return path in self._files and path.rpartition(".")[2] == "py"

    def isxfile(self, path):
        if verbose:
            print("Check if", path, "is an xfile")
        return path in self._xfiles

    def joinpath(self, *path):
        return posixpath.normpath(posixpath.join(*path))

    def readlines(self, path):
        try:
            return self._files[path]
        except KeyError:
            raise FileNotFoundError(path) from None

    def realpath(self, path, _trail=None):
        if verbose:
            print("Read link from", path)
        try:
            link = self._links[path]
        except KeyError:
            return path
        if _trail is None:
            _trail = set()
        elif link in _trail:
            raise OSError("circular link")
        _trail.add(link)
        return self.realpath(link, _trail)

    def warn(self, message):
        self._warnings.append(message)
        if verbose:
            print(message)


def diff_dict(before, after, prefix="global"):
    diff = []
    for k in sorted(before):
        if k[:2] == "__":
            continue
        if k == "config":
            diff_dict(before[k], after[k], prefix="config")
            continue
        if k in after and after[k] != before[k]:
            diff.append((k, before[k], after[k]))
    if not diff:
        return
    max_k = max(len(k) for k, _, _ in diff)
    indent = " " * (len(prefix) + 1 + max_k)
    if verbose:
        for k, b, a in diff:
            if b:
                print("{}.{} -{!r}\n{} +{!r}".format(prefix, k.ljust(max_k), b, indent, a))
            else:
                print("{}.{} +{!r}".format(prefix, k.ljust(max_k), a))


def dump_dict(before, after, prefix="global"):
    if not verbose or not after:
        return
    max_k = max(len(k) for k in after)
    for k, v in sorted(after.items(), key=lambda i: i[0]):
        if k[:2] == "__":
            continue
        if k == "config":
            dump_dict(before[k], after[k], prefix="config")
            continue
        try:
            if v != before[k]:
                print("{}.{} {!r} (was {!r})".format(prefix, k.ljust(max_k), v, before[k]))
                continue
        except KeyError:
            pass
        print("{}.{} {!r}".format(prefix, k.ljust(max_k), v))


def getpath(ns, keys):
    before = copy.deepcopy(ns)
    failed = True
    try:
        exec(SOURCE, ns)
        failed = False
    finally:
        if failed:
            dump_dict(before, ns)
        else:
            diff_dict(before, ns)
    return {
        k: ns['config'].get(k, ns.get(k, ...))
        for k in keys
    }
