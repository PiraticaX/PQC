"""
QShield Enterprise
==================

File Utilities.

Provides:

- File operations
- Secure file handling
- File metadata extraction
- Directory management
- Temporary file helpers
- File integrity support

Used across:

- Reports
- Backups
- Storage integrations
- Upload services
- Workers

"""

from __future__ import annotations


import os


import shutil


import tempfile



from pathlib import Path



from typing import Any



# ============================================================
# Path Utilities
# ============================================================


def ensure_directory(
    path: str | Path,
) -> Path:
    """
    Create directory if missing.

    """

    directory = Path(

        path

    )


    directory.mkdir(

        parents=True,

        exist_ok=True,

    )


    return directory



def file_exists(
    path: str | Path,
) -> bool:
    """
    Check file existence.

    """

    return Path(

        path

    ).is_file()



def directory_exists(
    path: str | Path,
) -> bool:
    """
    Check directory existence.

    """

    return Path(

        path

    ).is_dir()



# ============================================================
# File Read / Write
# ============================================================


def read_file(
    path: str | Path,
    encoding: str = "utf-8",
) -> str:
    """
    Read text file.

    """

    with open(

        path,

        "r",

        encoding=encoding,

    ) as file:

        return file.read()



def write_file(
    path: str | Path,
    content: str,
    encoding: str = "utf-8",
):
    """
    Write text file.

    """

    path = Path(

        path

    )


    ensure_directory(

        path.parent

    )


    with open(

        path,

        "w",

        encoding=encoding,

    ) as file:

        file.write(

            content

        )



def read_bytes(
    path: str | Path,
) -> bytes:
    """
    Read binary file.

    """

    with open(

        path,

        "rb",

    ) as file:

        return file.read()



def write_bytes(
    path: str | Path,
    data: bytes,
):
    """
    Write binary file.

    """

    path = Path(

        path

    )


    ensure_directory(

        path.parent

    )


    with open(

        path,

        "wb",

    ) as file:

        file.write(

            data

        )



# ============================================================
# File Metadata
# ============================================================


def get_file_metadata(
    path: str | Path,
) -> dict[str, Any]:
    """
    Extract file information.

    """

    file = Path(

        path

    )


    stats = file.stat()



    return {

        "name":

            file.name,


        "extension":

            file.suffix,


        "size":

            stats.st_size,


        "created":

            stats.st_ctime,


        "modified":

            stats.st_mtime,

    }



# ============================================================
# File Size
# ============================================================


def get_file_size(
    path: str | Path,
) -> int:
    """
    Return file size bytes.

    """

    return Path(

        path

    ).stat().st_size



def format_file_size(
    size: int,
) -> str:
    """
    Convert bytes to readable format.

    """

    units = [

        "B",

        "KB",

        "MB",

        "GB",

        "TB",

    ]



    value = float(

        size

    )


    index = 0



    while value >= 1024 and index < len(units)-1:

        value /= 1024

        index += 1



    return f"{value:.2f} {units[index]}"



# ============================================================
# File Management
# ============================================================


def delete_file(
    path: str | Path,
) -> bool:
    """
    Delete file safely.

    """

    file = Path(

        path

    )


    if not file.exists():

        return False



    file.unlink()



    return True



def copy_file(
    source: str | Path,
    destination: str | Path,
):
    """
    Copy file.

    """

    destination = Path(

        destination

    )


    ensure_directory(

        destination.parent

    )


    shutil.copy2(

        source,

        destination,

    )



def move_file(
    source: str | Path,
    destination: str | Path,
):
    """
    Move file.

    """

    destination = Path(

        destination

    )


    ensure_directory(

        destination.parent

    )


    shutil.move(

        source,

        destination,

    )



# ============================================================
# Temporary Files
# ============================================================


def create_temp_file(
    suffix: str = "",
) -> str:
    """
    Create temporary file.

    """

    file = tempfile.NamedTemporaryFile(

        delete=False,

        suffix=suffix,

    )


    file.close()



    return file.name



def create_temp_directory() -> str:
    """
    Create temporary directory.

    """

    return tempfile.mkdtemp()



# ============================================================
# Directory Operations
# ============================================================


def list_files(
    directory: str | Path,
    pattern: str = "*",
) -> list[str]:
    """
    List files in directory.

    """

    path = Path(

        directory

    )


    return [

        str(file)

        for file in path.glob(

            pattern

        )

        if file.is_file()

    ]



def remove_directory(
    path: str | Path,
) -> bool:
    """
    Remove directory recursively.

    """

    directory = Path(

        path

    )


    if not directory.exists():

        return False



    shutil.rmtree(

        directory

    )


    return True



# ============================================================
# Secure Delete
# ============================================================


def secure_delete(
    path: str | Path,
):
    """
    Secure file deletion.

    Overwrites file before removal.

    """

    file = Path(

        path

    )


    if not file.exists():

        return False



    size = file.stat().st_size



    with open(

        file,

        "wb",

    ) as target:

        target.write(

            os.urandom(

                size

            )

        )



    file.unlink()



    return True