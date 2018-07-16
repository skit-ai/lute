"""
Build script for cython extensions
"""

from distutils.core import Extension
from Cython.Distutils import build_ext

extensions = [
    # Extension("lute.cython_module", ["lute/cython_module.pyx"])
]

def build(setup_kwargs):
    setup_kwargs.update({
        "ext_modules": extensions,
        "cmdclass": {
            "build_ext": build_ext
        }
    })
