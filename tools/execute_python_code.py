"""Commands to execute code"""

import logging
import os
import shlex
import subprocess
from pathlib import Path
from tempfile import NamedTemporaryFile

COMMAND_CATEGORY = "execute_code"
COMMAND_CATEGORY_TITLE = "Execute Code"

logger = logging.getLogger(__name__)


def execute_python_code(code: str) -> str:
    """
    Create and execute a Python file in a Docker container and return the STDOUT of the
    executed code.

    If the code generates any data that needs to be captured, use a print statement.

    Args:
        code (str): The Python code to run.
        agent (Agent): The Agent executing the command.

    Returns:
        str: The STDOUT captured from the code when it ran.
    """
    ensure_compilable(code)
    tmp_code_file = NamedTemporaryFile(
        "w", dir="./", suffix=".py", encoding="utf-8"
    )
    tmp_code_file.write(code)
    tmp_code_file.flush()

    try:
        return execute_python_file(tmp_code_file.name)  # type: ignore
    except Exception as e:
        raise Exception(*e.args)
    finally:
        tmp_code_file.close()


def execute_python_file(
        filename: Path, args: list[str] | str = []
) -> str:
    """Execute a Python file in a Docker container and return the output

    Args:
        filename (Path): The name of the file to execute
        args (list, optional): The arguments with which to run the python script

    Returns:
        str: The output of the file
        :param filename:
        :param args:
        :return:
    """
    logger.info(
        f"Executing python file '{filename}' "
        f"in working directory 'bitsplease'"
    )

    if isinstance(args, str):
        args = args.split()  # Convert space-separated string to a list

    if not str(filename).endswith(".py"):
        raise InvalidArgumentError("Invalid file type. Only .py files are allowed.")

    result = subprocess.run(
        ["python", "-B", str(filename)] + args,
        capture_output=True,
        encoding="utf8",
        # cwd=str(agent.workspace.root),
    )
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(result.stderr)


def ensure_compilable(code):
    try:
        compile(code, '<string>', 'exec')
    except Exception as e:
        raise Exception(f"Compilation error: {e}")
