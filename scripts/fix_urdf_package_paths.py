#!/usr/bin/env python3
"""
Replace package://<name>/ with absolute filesystem paths in all URDF files
under ddt_ros2_control/urdfs/

Usage:
    python fix_urdf_package_paths.py
"""

import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URDF_ROOT = os.path.join(ROOT, "ddt_ros2_control", "urdfs")


def find_package_dir(pkg_name, start_dir):
    """Walk up from start_dir to find a directory named pkg_name that
    contains package.xml. Also checks ROS2 install layout
    <prefix>/share/<pkg_name>/package.xml."""
    search = start_dir
    for _ in range(10):
        candidate = os.path.join(search, pkg_name)
        if os.path.isdir(candidate):
            if os.path.isfile(os.path.join(candidate, "package.xml")):
                return candidate
            # ROS2 install prefix: <prefix>/share/<pkg_name>/
            ros2_share = os.path.join(candidate, "share", pkg_name)
            if os.path.isfile(os.path.join(ros2_share, "package.xml")):
                return ros2_share
        parent = os.path.dirname(search)
        if parent == search:
            break
        search = parent
    return None


def fix_urdf(path):
    with open(path, "r") as f:
        content = f.read()

    packages = set(re.findall(r"package://([^/]+)/", content))
    if not packages:
        print(f"[skip]  {path}")
        return

    urdf_dir = os.path.dirname(path)
    for pkg_name in sorted(packages):
        pkg_path = find_package_dir(pkg_name, urdf_dir)
        if pkg_path is None:
            print(f"[warn]  cannot find package '{pkg_name}' for {path}")
            continue
        content = content.replace(f"package://{pkg_name}/", pkg_path + "/")
        print(f"  {pkg_name} -> {pkg_path}/")

    with open(path, "w") as f:
        f.write(content)
    print(f"[fixed] {path}")


for dirpath, _, filenames in os.walk(URDF_ROOT):
    for name in filenames:
        if name.endswith(".urdf"):
            fix_urdf(os.path.join(dirpath, name))
