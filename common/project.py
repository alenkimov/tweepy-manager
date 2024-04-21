from .utils import load_toml

PROJECT_INFO = load_toml('pyproject.toml')['tool']['poetry']
PROJECT_VERSION = PROJECT_INFO['version']
PROJECT_NAME = PROJECT_INFO['name']
PROJECT_DESCRIPTION = PROJECT_INFO['description']


def print_project_info():
    print(f'{PROJECT_NAME} v{PROJECT_VERSION}: {PROJECT_DESCRIPTION}')
