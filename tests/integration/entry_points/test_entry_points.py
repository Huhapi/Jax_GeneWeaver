"""
Run this after you've installed your package locally, e.g.
    poetry install  (or)  pip install -e .
Then:
    python check_entry_points.py
"""

import importlib.metadata as ilm

GROUP = "jax.ats.plugins"

def main() -> None:
    eps = ilm.entry_points(group=GROUP)
    if not eps:
        print(f"No entry points found for group {GROUP}")
        return

    print(f"👍  Found {len(eps)} entry point(s) in '{GROUP}':")
    for ep in eps:
        try:
            cls = ep.load()        # import the class
            print(f"   • {ep.name} → {ep.value}  (import OK)")
        except Exception as exc:
            print(f"   • {ep.name} → {ep.value}  Import failed: {exc}")

if __name__ == "__main__":
    main()