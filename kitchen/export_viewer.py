#!/usr/bin/env python3
"""Export BIBLE 6/7 viewer data from Neo4j; never calls a reader or changes Neo4j."""

import argparse

from viewer_export import copy_wording


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wording-only", action="store_true", help="copy UI labels; no database connection")
    args = parser.parse_args()
    if not args.wording_only:
        from db import run
        from export_entities import export as entities
        from export_districts import export as districts
        entities(run)
        districts(run)
    print({"wording_files_changed": copy_wording()[0]})


if __name__ == "__main__":
    main()
