from doit.tools import Interactive


def task_format():
    """format"""

    return {
        # 'actions': ["cd src/", "autopep8 -i *.py"]
        'actions': ["black src/"]
    }


def task_lint():
    """lint"""

    return {
        'actions': ["flake8 src/ --extend-exclude=.cache,.mypy_cache,.venv"]
    }


def task_mypy():
    """lint"""

    return {
        'actions': [Interactive("mypy src/ --check-untyped-defs")],
        'verbosity': 2
    }
