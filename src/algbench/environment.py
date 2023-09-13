"""
Gathering information of the environment the
code is running.
"""
import socket
import subprocess
import sys
import typing
from pathlib import Path

import __main__
import pkg_resources

__cached = None


def get_git_revision() -> typing.Optional[str]:
    """
    Return the git revision of the current working directory.
    """
    try:
        label = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .strip()
            .decode("ascii")
        )
    except subprocess.CalledProcessError:
        label = None
    return label

def get_python_file() -> typing.Optional[str]:
    """
    Return the path of the calling python file.
    """
    try:
        label = __main__.__file__
    except AttributeError:
        # Jupyter notebooks don't have __file__ attribute
        label = None
    return label


def get_environment_info(cached=True) -> dict:
    """
    Returns extensive information on the environment
    the code is running.
    The returned dictionary should be JSON-serializable.
    """
    global __cached
    if cached and __cached:
        return __cached
    __cached = {
        "hostname": socket.gethostname(),
        "python_version": sys.version,
        "python": sys.executable,
        "cwd": Path.cwd(),
        "environment": [
            {
                "name": str(pkg.project_name),
                "path": str(pkg.location),
                "version": str(pkg.parsed_version),
            }
            for pkg in pkg_resources.working_set
        ],
        "git_revision": get_git_revision(),
        "python_file": get_python_file(),
    }
    return __cached
