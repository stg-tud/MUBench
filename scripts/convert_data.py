#!/usr/bin/env python3
# coding=utf-8
import inspect
import os
from os.path import join, isdir, exists

import yaml

from benchmark.data.misuse import Misuse
from benchmark.utils.io import safe_open, copy_tree

script_location = os.path.dirname(
    os.path.realpath(inspect.stack()[0][1]))  # most reliable way to get the scripts absolute location
os.chdir(join(script_location, os.pardir))  # set the cwd to the MUBench folder

data_path = 'old_data'
new_data_path = 'data'

old_misuse_folders = [join(data_path, subdir) for subdir in os.listdir(data_path) if isdir(join(data_path, subdir))]

for old_misuse_folder in old_misuse_folders:
    old_misuse = Misuse(old_misuse_folder)
    old_meta = old_misuse.meta

    new_root_folder = join(new_data_path, old_misuse.project_name)

    project_file = join(new_root_folder, 'project.yml')
    if not exists(project_file):
        project_yaml = {"repository": {"type": old_meta["fix"]["repository"]["type"]}}
        if "url" in old_meta["fix"]["repository"]:
            project_yaml["repository"]["url"] = old_meta["fix"]["repository"]["url"]
        if "project" in old_meta:
            project_yaml["name"] = old_meta["project"]["name"]
            project_yaml["url"] = old_meta["project"]["url"]

        with safe_open(project_file, 'w+') as project_file_stream:
            yaml.dump(project_yaml, project_file_stream, default_flow_style=False)

    i = 1
    while exists(join(new_root_folder, 'misuses', str(i))):
        i += 1
    misuse_folder = join(new_root_folder, 'misuses', str(i))
    misuse_file = join(misuse_folder, 'misuse.yml')

    misuse_yaml = {"source": old_meta["source"], "report": old_meta.get("report"), "description": old_meta["description"],
                   "crash": old_meta["crash"], "internal": old_meta["internal"], "api": old_meta["api"],
                   "characteristics": old_meta["characteristics"], "pattern": old_meta["pattern"]}
    if "misuse" in old_meta:
        misuse_yaml["file"] = old_meta["misuse"]["file"]
        misuse_yaml["type"] = old_meta["misuse"]["type"]
        misuse_yaml["method"] = old_meta["misuse"]["method"]
        misuse_yaml["usage"] = old_meta["misuse"]["usage"]

    if "fix" in old_meta:
        fix_without_project = old_meta["fix"].copy()
        if "project" in fix_without_project:
            fix_without_project.pop("project")
        misuse_yaml["fix"] = fix_without_project
    with safe_open(misuse_file, 'w+') as misuse_file_stream:
        yaml.dump(misuse_yaml, misuse_file_stream, default_flow_style=False)

    misuse_patterns_folder = join(misuse_folder, 'patterns')
    old_patterns_folder = join(old_misuse.path, 'patterns')
    if exists(old_patterns_folder):
        copy_tree(old_patterns_folder, misuse_patterns_folder)

    project_version = old_misuse.project_version or "-1"
    version_folder = join(new_root_folder, project_version)
    version_file = join(version_folder, 'version.yml')

    version_yaml = {"build": old_meta["build"], "misuses": ["1"]}
    if "revision" in old_meta["fix"]:
        version_yaml["revision"] = old_meta["fix"]["revision"]

    with safe_open(version_file, 'w+') as version_file_stream:
        yaml.dump(version_yaml, version_file_stream, default_flow_style=False)

    compile_folder = join(version_folder, 'compile')
    old_compile_folder = join(old_misuse.path, 'compile')
    if exists(old_compile_folder):
        copy_tree(old_compile_folder, compile_folder)
