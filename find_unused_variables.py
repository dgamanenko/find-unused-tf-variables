import os
import sys

import hcl


def get_variables_in_file(path):
    hcl_object = True
    try:
        with open(path) as tf:
            tf_definitions = hcl.load(tf)
    except ValueError as err:
        print("Error loading Terraform from {path}: {err}".format(path=path, err=err))
        hcl_object = False
        # raise ValueError("Error loading Terraform from {path}: {err}".format(path=path, err=err))

    if hcl_object:
        try:
            return set(tf_definitions["variable"].keys())
        except KeyError:
            return set()
    else:
        return set()


def tf_files_in_module(dirname):
    for f in os.listdir(dirname):
        if f.endswith(".tf"):
            yield f


def get_variables_in_module(dirname):
    all_variables = {}

    for f in tf_files_in_module(dirname):
        for varname in get_variables_in_file(os.path.join(dirname, f)):
            all_variables[varname] = f

    return all_variables


def find_unused_variables_in_module(dirname):
    unused_variables = get_variables_in_module(dirname)

    for f in tf_files_in_module(dirname):
        if not unused_variables:
            return {}

        tf_src = open(os.path.join(dirname, f)).read()
        for varname in list(unused_variables):
            if "var.{varname}".format(varname=varname) in tf_src:
                del unused_variables[varname]

    return unused_variables


def find_unused_variables_in_tree(root):
    for mod_root, _, filenames in os.walk(root):
        if not any(f.endswith(".tf") for f in filenames):
            continue

        unused_variables = find_unused_variables_in_module(mod_root)

        if unused_variables:
            print("Unused variables in {mod_root}:".format(mod_root=mod_root))
            for varname, filename in unused_variables.items():
                fname=os.path.join(mod_root, filename)
                print("* {varname} ~> {fname}".format(varname=varname, fname=fname))
            print("")


if __name__ == "__main__":
    try:
        root = sys.argv[1]
    except IndexError:
        root = "."

    find_unused_variables_in_tree(root)