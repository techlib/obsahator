#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
import os
from datetime import datetime

# CONVERTOR module


def convert_to_jpg(path_list):
    """
    Converts input image file to jpeg format
    :param path_list: list of paths to the image files to be converted
    :return: converted_files: list of converted files
    """
    converted_files = []
    for path in path_list:
        # get image name from path
        name = os.path.basename(path)
        dirpath = os.path.dirname(path)

        # get filename and extension from filename
        fn, ext = os.path.splitext(name)

        # construct output file name
        outfile = fn + '.jpg'

        # construct path to outfile
        outpath = os.path.join(dirpath, outfile)

        try:
            print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "INFO (CONVERSION): Converting {} to {}...".format(path, outpath))
            if path == outpath:
                print("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " +
                      "INFO (CONVERSION): File {} already exist, won't covert.".format(outpath))
                continue
            Image.open(path).save(outpath)
            converted_files.append(outpath)
        except IOError:
            raise IOError("{0:%Y-%m-%d %H:%M:%S}".format(datetime.now()) + " " + "ERROR (CONVERSION): Cannot convert", name)

    return converted_files



