"""Saint Capybara shared tooling package.

Everything under tools/capy_*.py that needs the beat schema, the sprite
system, the frame layout, or the theme palette imports from here. This is
the one deliberate exception to this repo's "no common.py" convention (see
../../README.md) -- justified because six-plus scripts for this type share
the same beat schema, layout constants, and plate renderer, and duplicating
those would be worse than one shared package.

Scripts run as `python tools/capy_x.py ...`, which puts tools/ on
sys.path, so `import capy` / `from capy import ...` works without
installation.
"""
