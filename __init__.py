import glob
import os

py_list = glob.glob('lib/*.py')
__all__ = list(map(lambda file_path: os.path.basename(file_path).split('.', 1)[0], py_list))
__all__.remove('__init__')
