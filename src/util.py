import psMat
import os


def font_into_file(font, filename):
    # log("Status:", hex(font.validate()), filename)
    font.generate(filename, flags=("opentype",))
    font.close()


def font_clear_glyph(font, start, end=None):
    if end is None:
        font.selection.select(start)
    else:
        font.selection.select(("ranges",), start, end)
    font.clear()
    font.selection.none()


def fix_all_glyph_points(font):
    for glyph in font.glyphs():
        glyph.round()
        glyph.addExtrema("all")


def glyph_riseze_width(glyph, new_width):
    old_width = glyph.width
    mat = psMat.scale(float(new_width) / old_width, 1)
    glyph.transform(mat)
    glyph.width = new_width


def draw_square(glyphPen, center, width, height, clockwise=True):
    dx = round(width / 2)
    dy = round(height / 2)
    center = (round(center[0]), round(center[1]))
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


def log(*msg):
    print(*msg, flush=True)


_is_debug_mode = None


def _check_is_debug_mode():
    global _is_debug_mode
    if _is_debug_mode is not None:
        return
    env = os.getenv("PLECKJP_ENABLE_DEBUG", '0')
    try:
        value = int(env)
        _is_debug_mode = True if value > 0 else False
    except ValueError:
        _is_debug_mode = False


def debug(*msg):
    _check_is_debug_mode()
    if _is_debug_mode:
        log(*msg)
