import os


def get_env_var(key: str, default: str = None) -> str:
    """
    Get environment variable
    :param key: Environment variable key
    :param default: Default value if key is not found
    :return value: Environment variable value
    """
    try:
        return os.environ[key]
    except KeyError:
        if default is not None:
            return default
        raise KeyError(f"Environment variable {key} not set")
