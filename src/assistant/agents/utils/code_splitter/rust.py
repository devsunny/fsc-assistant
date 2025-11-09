import io
import re
import sys

from ..utils.cli.utils import read_text_file, write_text_file


def split_rust_codes(code_string: str):
    codes = io.StringIO(code_string)
    file_name = None
    incode_block = False
    codeblock = []
    reame = []

    for line in codes:
        if "Cargo.toml" in line:
            file_name = "Cargo.toml"
        elif re.match(r"^### [a-z0-9_/]+\.[a-z0-9]+$", line.strip(), re.IGNORECASE):
            file_name = line[4:].strip()
        elif file_name is not None and re.match(
            r"^```[a-z0-9]+$", line.strip(), re.IGNORECASE
        ):
            incode_block = True
        elif incode_block is True and line.strip() == "```":
            incode_block = False
            if file_name is not None and codeblock:
                write_text_file(file_name, codeblock)
            elif codeblock:
                reame.extend(codeblock)
            file_name = None
            codeblock = []
        elif incode_block is True and file_name is not None:
            codeblock.append(line)
        else:
            reame.append(line)

    write_text_file("README.md", reame)


def main():
    file_path = sys.argv[1]
    codes = read_text_file(file_path)
    split_rust_codes(codes)


if __name__ == "__main__":
    main()
