import os
from typing import IO
from zipfile import ZipFile
import tarfile
import logging

logge = logging.getLogger('Olympus')

_magic_dict = {
    "\x1f\x8b\x08".encode():"gz",
    "\x50\x4b\x03\x04".encode(): "zip",
    "\xFD\x37\x7A\x58\x5A\x00".encode(): "lzma",
    "\x75\x73\x74\x61\x72".encode(): "tar"
    }

class Decompressor:
    def _find_compression_type( file: IO[bytes] | str):
        max_len = max(len(x) for x in _magic_dict)
        
        f = None
        
        if isinstance(file, str):
            f = open(file, 'rb')
        else:
            f = file
        
        file_start = f.read(max_len)
        if isinstance(file, str):
            f.close()
        else:
            f.seek(0)        
        logging.debug(f"File magic number: {file_start}")
        for magic, filetype in _magic_dict.items():
            if file_start[0:len(magic)] == magic:
                return filetype
        return None

    def _decompress_zip(file, output_path):
        ZipFile(file, 'r').extractall(output_path)

    def _decompress_lzma(file, output_path):
        tarfile.open(fileobj=file, mode="r").extractall(output_path,  numeric_owner=True)

    def _decompress_gz(file, output_path):
        tarfile.open(fileobj=file, mode="r").extractall(output_path)

    def _decompress_tar(file, output_path):
        tarfile.open(fileobj=file, mode="r").extractall(output_path)
        
    def is_compressed(file: IO[bytes] | str):
        return Decompressor._find_compression_type(file) != None

    def decompress(file: IO[bytes] | str, output_path):
        _decompression_dict = {
            "zip": Decompressor._decompress_zip,
            "lzma": Decompressor._decompress_lzma,
            "tar": Decompressor._decompress_tar,
            "gz": Decompressor._decompress_gz
        }
        f = None
        if isinstance(file, str):
            filepath = os.path.abspath(file)
            f = open(filepath, 'r')
        else:
            f = file
        compression_type = Decompressor._find_compression_type(file)

        if compression_type:
            logging.debug("Detected compression type: '%s'", compression_type)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            _decompression_dict[compression_type](file, output_path)
        else:
            logging.warning("Unknown compression type: Attempting tar file decommpression")
            try:
                Decompressor._decompress_tar(file, output_path)
            except tarfile.ReadError as _:
                logging.warning(f"Unable to read '{file}' please check compression type")