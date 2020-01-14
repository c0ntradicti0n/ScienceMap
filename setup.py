from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

extensions = [Extension('cython_bow', ['cython_bow.pyx'], language='c++')]

setup(
    name='fast_bow',
    ext_modules=cythonize(
        extensions,
        annotate=True,
        compiler_directives={'language_level': '3'},
    )
)