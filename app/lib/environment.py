from typing import List, Dict

import dotenv
import sys
import os


class EnvNotFoundError(Exception):
    pass


sys.path.append("app")
dotenv.load_dotenv()


def get(env: str, type: type = str) -> str:
    value = os.environ.get(env)
    if value is None:
        raise EnvNotFoundError(f"Env variable {env} not found!")

    try:
        converted_value = type(value)
    except ValueError:
        raise TypeError(f"Env variable {env} not of type {type}")
    
    return converted_value


def get_environment(env_names: List[str]) -> Dict[str, str]:
    environment = {}
    for env in env_names:
        value = os.environ.get(env)
        if value is None:
            raise EnvNotFoundError(f"Env variable {env} not found!")

        environment[env] = value

    return environment
