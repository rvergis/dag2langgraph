import argparse
import json
import sys
from typing import Any

from .converter import convert_dag_to_langgraph, DagValidationError


def main(argv: Any = None) -> int:
    parser = argparse.ArgumentParser(
        description="Convert a DAG JSON to LangGraph JSON."
    )
    parser.add_argument("input", help="Path to DAG JSON file (or '-' for stdin)")
    parser.add_argument(
        "-o", "--output", help="Path to output LangGraph JSON (default: stdout)", default="-"
    )
    args = parser.parse_args(argv)

    # Read input
    try:
        if args.input == "-":
            dag = json.load(sys.stdin)
        else:
            with open(args.input, "r", encoding="utf-8") as f:
                dag = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON input: {e}", file=sys.stderr)
        return 2
    except OSError as e:
        print(f"Error: cannot read input file: {e}", file=sys.stderr)
        return 2

    # Convert
    try:
        langgraph = convert_dag_to_langgraph(dag)
    except DagValidationError as e:
        print(str(e), file=sys.stderr)
        return 1

    # Write output
    try:
        data = json.dumps(langgraph, indent=2, ensure_ascii=False)
        if args.output == "-":
            print(data)
        else:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(data)
    except OSError as e:
        print(f"Error: cannot write output file: {e}", file=sys.stderr)
        return 2

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
