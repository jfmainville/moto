#!/usr/bin/env python
# This updates the cache used by the dispatcher to find backends.
import importlib
import os
import re
from moto.backends import list_of_moto_modules
from pathlib import Path

import black
import pprint

import moto

output_file = "moto/backend_index.py"

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "..", output_file)

# Ignore the Moto API/Server/Proxy backends, as they do not represent AWS services
# Ignore the APIGatewayV2, as it's URL's are managed by APIGateway
# Ignore S3bucket_path, as the functionality is covered in the S3 service
# Ignore neptune, as it shares a URL with RDS
# Ignore OpenSearch, as it shares a URL with ElasticSearch
IGNORE_BACKENDS = ["moto_server", "moto_proxy", "apigatewayv2", "awslambda_simple", "batch_simple", "core", "dynamodb_v20111205", "packages", "utilities", "s3bucket_path", "neptune", "opensearch"]


def iter_backend_url_patterns():
    path = os.path.dirname(moto.__file__)
    for backend in list_of_moto_modules():
        # Special case
        if backend == "moto_api":
            backend = "moto_api._internal"
        if backend in IGNORE_BACKENDS:
            continue
        # otherwise we need to import the module
        url_module_name = f"moto.{backend}.urls"
        module = importlib.import_module(url_module_name)
        for pattern in getattr(module, "url_bases"):
            yield backend, pattern


def build_backend_url_pattern_index():
    """
    Builds an index between an url pattern and the associated backend.

    :rtype: List[Tuple[str, pattern]]
    """
    index = list()

    for backend, url_pattern in iter_backend_url_patterns():
        index.append((backend, re.compile(url_pattern)))

    return index


def main():
    with open(output_path, "w") as fd:
        fd.write("# autogenerated by %s\n" % __file__)
        fd.write("import re\n")

    print("build backend_url_patterns")
    index = build_backend_url_pattern_index()
    with open(output_path, "a") as fd:
        fd.write("backend_url_patterns = ")
        pprint.pprint(index, fd)
        fd.write(os.linesep)

    print("format with black")
    black.format_file_in_place(
        Path(output_path),
        fast=False,
        mode=black.FileMode(),
        write_back=black.WriteBack.YES,
    )


if __name__ == "__main__":
    main()
