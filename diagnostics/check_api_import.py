import sys
import os
import importlib

print("cwd:", os.getcwd())
print("sys.path[0]:", sys.path[0])

spec = importlib.util.find_spec("api")
print("importlib.util.find_spec('api'):", spec)

try:
    import api
    print("imported api package successfully, api.__file__=", getattr(api, '__file__', None))
except Exception as e:
    print("failed to import api:", e)
    raise
