import tempfile
from decompression import Decompressor
import shutil

with open ("./sd/hekate_ctcaer_6.1.1_Nyx_1.6.1.zip", 'rb') as f:

    with tempfile.SpooledTemporaryFile('rb+') as temp:
        shutil.copyfileobj(f, temp)
        
        temp.seek(0)

        Decompressor._decompress_zip(temp, './')