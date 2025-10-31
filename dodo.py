from doit.tools import Interactive


def task_format():
    """format"""

    return {
        'actions': ["cd src/", "autopep8 -i *.py"]
    }
    # """format"""
    # return
    # {
    #     'actions': ["cd src/", "autopep8 -i *.py"],
    #     'argets': ["hello.txt"],}


def task_lint():
    """lint"""

    return {
        'actions': ["flake8 src/"]
    }


def task_mypy():
    """lint"""

    return {
        'actions': [Interactive("mypy src/ --check-untyped-defs")],
        'verbosity': 2
    }
