import os
from pathlib import Path


print(os.path.join(os.path.dirname(__file__)))


cwd = Path.cwd()
print(cwd)

file = os.path.dirname(os.path.realpath('__file__'))
print(file)