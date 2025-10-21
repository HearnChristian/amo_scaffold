import argparse

def build_parser():
    p = argparse.ArgumentParser(prog="amo", description="AMO scaffold CLI")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("set", help="Set a device parameter")
    s.add_argument("target", help="e.g., laser.power")
    s.add_argument("value", type=float)

    g = sub.add_parser("get", help="Get a device parameter")
    g.add_argument("target", help="e.g., laser.power")

    st = sub.add_parser("status", help="Show device status")
    st.add_argument("device", help="e.g., laser")

    r = sub.add_parser("run", help="Run a YAML recipe")
    r.add_argument("recipe_path", help="recipes/demo.yaml")
    return p
