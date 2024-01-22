import os
from distutils.util import strtobool


def get_env_bool(env_name: str, default: bool = False) -> bool:
    """
    Get the boolean value for an environment variable

    Args:
        env_name: str of environment variable name
        default: bool of default value

    Returns:
        bool of environment value if valid, otherwise the default value
    """

    value = os.getenv(key=env_name)
    if value is None:
        return default

    try:
        return bool(strtobool(value))
    except ValueError:
        return default
