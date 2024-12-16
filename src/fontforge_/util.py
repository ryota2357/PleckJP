# pyright: reportMissingImports=false

import psMat


def font_into_file(font, filename: str) -> None:
    # log("Status:", hex(font.validate()), filename)
    font.generate(filename, flags=("opentype",))
    font.close()


def font_clear_glyph(font, start: int, end: int | None = None) -> None:
    if end is None:
        font.selection.select(start)
    else:
        font.selection.select(("ranges",), start, end)
    font.clear()
    font.selection.none()


def font_set_em(font, ascent: int, descent: int, em: int) -> None:
    old_em = font.em
    font.selection.all()
    font.unlinkReferences()
    font.ascent = round(float(ascent) / em * old_em)
    font.descent = round(float(descent) / em * old_em)
    font.em = em
    font.selection.none()


def font_resize_all_width(font, new_width: int) -> None:
    for glyph in font.glyphs():
        if glyph.width == new_width:
            continue
        if glyph.width != 0:
            fix_scale_mat = psMat.scale(float(new_width) / glyph.width)
            glyph.transform(fix_scale_mat)
        glyph.width = new_width


def fix_all_glyph_points(font, round: bool = False, addExtrema: bool = False) -> None:
    for glyph in font.glyphs():
        if round:
            glyph.round()
        if addExtrema:
            glyph.addExtrema("all")


def glyph_riseze_width(glyph, new_width: int) -> None:
    old_width = glyph.width
    mat = psMat.scale(float(new_width) / old_width, 1)
    glyph.transform(mat)
    glyph.width = new_width


def draw_square(
    glyphPen, center: tuple[int, int], width: int, height: int, clockwise: bool = True
) -> None:
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


def log(*msg) -> None:
    print(*msg, flush=True)
