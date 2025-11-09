import io
import re
import sys

from ..utils.cli.utils import read_text_file, write_text_file


def main():
    file_path = sys.argv[1]
    codes = io.StringIO(read_text_file(file_path))
    file_name = None
    codeblock = []
    for line in codes:
        if line:
            match = re.match(r"^# ([A-Za-z0-9_]+\.py)$", line.strip(), re.IGNORECASE)
            if match:
                if codeblock and file_name:
                    write_text_file(file_name, codeblock)
                codeblock = []
                file_name = match.group(1)
            elif file_name is not None:
                codeblock.append(line)
        elif file_name is not None:
            codeblock.append(line)

    if file_name is not None and codeblock:
        write_text_file(file_name, codeblock)


if __name__ == "__main__":
    main()
