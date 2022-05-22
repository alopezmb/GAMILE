import inspect
from pathlib import Path

DEBUG = False


def get_project_root() -> Path:
    return Path(__file__).parent.parent


def print_trace(message):

    if DEBUG:

        # Get file path (relative to project root)
        absolute_file_path = str(inspect.stack()[1][1])
        root_path = str(get_project_root())
        root_name = root_path.split('/')[-1]
        file_path = absolute_file_path.replace(root_path, root_name)

        # Name of function where trace is being called
        function_name = str(inspect.stack()[1][3])
        # Line number inside the file where trace is being called
        line_number = str(inspect.stack()[1][2])
        # File, function and line_number
        debug_info = f'{file_path}->{function_name}:{line_number}'

        # Prettify message
        header = ('#'*25) + ' ' + debug_info + ' ' + ('#'*25)
        footer = '#'*len(header)

        # Print debug info and message
        print(header)
        print(f'MESSAGE-> {message}')
        print(footer)
        print('\n')
