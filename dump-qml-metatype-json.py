#!/usr/bin/env python3
"""Extract QML metadata from Python code

This is a workaround for PYSIDE-1392. The generated .json files will be fed
to qmltyperegistrar to generate .qmltypes file.

https://bugreports.qt.io/browse/PYSIDE-1392
"""

import argparse
import ast
import fnmatch
import json
import os
import re
import sys

from typing import Any, Dict, Optional


def collect_files(paths, include_pat):
    for top in paths:
        if not os.path.isdir(top):
            if not include_pat.match(top):
                continue
            yield top
            continue

        for root, _dirs, files in os.walk(top):
            for f in files:
                if not include_pat.match(f):
                    continue
                yield os.path.join(root, f)


def dump_json(data, f):
    json.dump(data, f, indent=4, sort_keys=True)
    f.write("\n")


def map_to_qt_type(py_name: str) -> str:
    return {
        "float": "qreal",
        "str": "QString",
        # TODO: ...
    }.get(py_name, py_name)


def extract_constant(node: ast.expr) -> Any:
    if isinstance(node, ast.Constant):
        return node.value


def extract_name(node: ast.expr) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Call):
        return extract_name(node.func)


def process_file(name) -> Dict[str, Any]:
    with open(name, "r") as f:
        root = ast.parse(f.read(), name)

    classes_data = []
    for node in ast.walk(root):
        if isinstance(node, ast.ClassDef):
            d = maybe_process_class_def(node)
            if d:
                classes_data.append(d)

    return {
        "classes": classes_data,
        "inputFile": name,
    }


def maybe_process_class_def(class_node: ast.ClassDef) -> Optional[Dict[str, Any]]:
    if not any(extract_name(n) == "QmlElement" for n in class_node.decorator_list):
        return

    class_infos_data = [
        {"name": "QML.Element", "value": "auto"},
    ]
    for node in class_node.decorator_list:
        if extract_name(node) == "QmlUncreatable":
            assert isinstance(node, ast.Call)
            assert node.args
            reason = extract_constant(node.args[0])
            class_infos_data.extend(
                [
                    {"name": "QML.Creatable", "value": False},
                    {"name": "QML.UncreatableReason", "value": reason},
                ]
            )
        # TODO: process Qml*() decorators

    super_classes_data = [
        {"access": "public", "name": extract_name(n)} for n in class_node.bases
    ]

    # TODO: collect slots
    properties_data, signals_data = [], []
    for node in class_node.body:
        if isinstance(node, ast.Assign):
            d = maybe_process_signal_assign(node)
            if d:
                signals_data.append(d)
        elif isinstance(node, ast.FunctionDef):
            d = maybe_process_property_func_def(node)
            if d:
                properties_data.append(d)

    return {
        "className": class_node.name,
        "qualifiedClassName": class_node.name,  # TODO
        "superClasses": super_classes_data,
        "classInfos": class_infos_data,
        "object": True,
        "properties": properties_data,
        "signals": signals_data,
    }


def maybe_process_signal_assign(assign_node: ast.Assign) -> Optional[Dict[str, Any]]:
    if extract_name(assign_node.value) != "Signal":
        return
    if len(assign_node.targets) != 1:
        return
    signal_name = extract_name(assign_node.targets[0])
    if not signal_name:
        return
    return {
        "access": "public",
        "name": signal_name,
        "arguments": [],  # TODO
        "returnType": "void",  # TODO
    }


def maybe_process_property_func_def(
    func_node: ast.FunctionDef,
) -> Optional[Dict[str, Any]]:
    pcall_node = next(
        (n for n in func_node.decorator_list if extract_name(n) == "Property"), None
    )
    if not pcall_node:
        return
    if not pcall_node.args:
        return
    type_name = extract_name(pcall_node.args[0])
    if not type_name:
        return

    property_data = {
        "type": map_to_qt_type(type_name),
        "name": func_node.name,
        "read": func_node.name,
        "write": func_node.name,  # TODO
        # TODO: "constant"
        # TODO: ...
    }

    for node in pcall_node.keywords:
        if node.arg == "notify":
            property_data["notify"] = extract_name(node.value)

    return property_data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-I", "--include", action="append")
    ap.add_argument("-O", "--output-directory")
    ap.add_argument("paths", nargs="+")
    args = ap.parse_args()
    if args.include:
        include_pat = re.compile(
            "|".join("(?:%s)" % fnmatch.translate(p) for p in args.include)
        )
    else:
        include_pat = re.compile(fnmatch.translate("*.py"))
    files = sorted(map(os.path.relpath, collect_files(args.paths, include_pat)))

    if args.output_directory:
        os.makedirs(args.output_directory, exist_ok=True)

    for name in files:
        data = process_file(name)
        if args.output_directory:
            # TODO: how to deal with intermediate directory names?
            out_name = os.path.basename(name) + ".json"
            with open(os.path.join(args.output_directory, out_name), "w") as f:
                dump_json(data, f)
        else:
            dump_json(data, sys.stdout)


if __name__ == "__main__":
    main()
