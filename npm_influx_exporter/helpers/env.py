import os
from distutils.util import strtobool


def get_env_bool(env_name: str, default: bool = False):
    value = os.getenv(key=env_name)
    if value is None:
        return default

    try:
        return bool(strtobool(value))
    except ValueError:
        return default
