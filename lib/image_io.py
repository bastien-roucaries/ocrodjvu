# encoding=UTF-8
# Copyright © 2008, 2009, 2010 Jakub Wilk <jwilk@jwilk.net>
#
# This package is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 2 dated June, 1991.
#
# This package is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

import struct

try:
    import djvu.decode
except ImportError, ex:
    ex.args = '%s; please install the python-djvulibre package <http://jwilk.net/software/python-djvulibre>' % str(ex),
    raise

class ImageFormat(object):

    extension = None

    def __init__(self, bpp):
        if bpp == 1:
            pixel_format = djvu.decode.PixelFormatPackedBits('>')
            pixel_format.rows_top_to_bottom = 1
            pixel_format.y_top_to_bottom = 1
        elif bpp == 24:
            pixel_format = djvu.decode.PixelFormatRgb()
            pixel_format.rows_top_to_bottom = 1
            pixel_format.y_top_to_bottom = 1
        else:
            raise NotImplementedError('Cannot output %d-bpp images' % bpp)
        self._pixel_format = pixel_format

    def write_image(self, page_job, render_layers, file):
        raise NotImplementedError

class PNM(ImageFormat):

    '''Binary PBM or PPM.'''

    extension = 'pnm'

    def __init__(self, bpp):
        ImageFormat.__init__(self, bpp)
        if bpp == 1:
            self.extension = 'pbm'
        elif bpp == 24:
            self.extension = 'ppm'

    def write_image(self, page_job, render_layers, file):
        size = page_job.size
        rect = (0, 0) + size
        if self._pixel_format.bpp == 1:
            file.write('P4 %d %d\n' % size)  # PBM header
        else:
            file.write('P6 %d %d 255\n' % size)  # PPM header
        data = page_job.render(
            render_layers,
            rect, rect,
            self._pixel_format
        )
        file.write(data)


class BMP(ImageFormat):

    '''Uncompressed Windows BMP.'''

    extension = 'bmp'

    def __init__(self, bpp):
        ImageFormat.__init__(self, bpp)
        self._pixel_format.rows_top_to_bottom = 0

    def write_image(self, page_job, render_layers, file):
        size = page_job.size
        rect = (0, 0) + size
        dpm = int(page_job.dpi * 39.37 + 0.5)
        data = page_job.render(
            render_layers,
            rect, rect,
            self._pixel_format,
            row_alignment=4,
        )
        n_palette_colors = 2 * (self._pixel_format.bpp == 1)
        headers_size = 54 + 4 * n_palette_colors
        file.write(struct.pack('<ccIHHI',
            'B', 'M', # magic
            len(data) + headers_size, # whole file size
            0, 0, # identification magic
            headers_size # offset to pixel data
        ))
        file.write(struct.pack('<IIIHHIIIIII',
            40, # size of this header
            size[0], size[1], # image size in pixels
            1, # number of color planes
            self._pixel_format.bpp, # number of bits per pixel
            0, # compression method
            len(data), # size of pixel data
            dpm, dpm, # resolution in pixels/meter
            n_palette_colors, # number of colors in the color pallete
            n_palette_colors # number of important colors
        ))
        if self._pixel_format.bpp == 1:
            # palette:
            file.write(struct.pack('<BBBB', 0xff, 0xff, 0xff, 0))
            file.write(struct.pack('<BBBB', 0, 0, 0, 0))
        file.write(data)

# vim:ts=4 sw=4 et
