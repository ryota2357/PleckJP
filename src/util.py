import psMat


def font_into_file(font, filename):
    # print("Status:", hex(font.validate()), filename)
    font.generate(filename, flags=("opentype",))
    font.close()


def font_clear_glyph(font, start, end=None):
    if end is None:
        font.selection.select(start)
    else:
        font.selection.select(("ranges",), start, end)
    font.clear()
    font.selection.none()


def glyph_riseze_width(glyph, new_width):
    old_width = glyph.width
    mat = psMat.scale(float(new_width) / old_width, 1)
    glyph.transform(mat)
    glyph.width = new_width


def draw_square(glyphPen, center, width, height, clockwise=True):
    dx = width // 2
    dy = height // 2
    glyphPen.moveTo((center[0] - dx, center[1] - dy))
    if clockwise:
        glyphPen.lineTo((center[0] - dx, center[1] + dy))
        glyphPen.lineTo((center[0] + dx, center[1] + dy))
        glyphPen.lineTo((center[0] + dx, center[1] - dy))
    else:
        glyphPen.lineTo((center[0] + dx, center[1] - dy))
        glyphPen.lineTo((center[0] + dx, center[1] + dy))
        glyphPen.lineTo((center[0] - dx, center[1] + dy))
    glyphPen.closePath()
