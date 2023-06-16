import sys
import fontforge
import psMat
import util
import properties as const

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
BUILD_FILE = sys.argv[2]


def main():
    font = fontforge.open(FONT_FILE)

    # Use IBMPlexSansJP glyph
    util.font_clear_glyph(font, 0x2003)  # 　(EM SPACE)
    util.font_clear_glyph(font, 0x266a)  # ♪

    # Use Hack Nerd Font glyph
    util.font_clear_glyph(font, 0xe0a0, 0xe0b3)  # Private Use Area

    util.font_set_em(font, const.ASCENT, const.DESCENT, const.EM)
    util.font_resize_all_width(font, const.EM // 2)

    # TODO: Create glyph
    # 0x226a: ≪
    # 0x226b: ≫
    fix_subscript_numbers(font)
    create_up_tack(font)

    modify_0(font)
    modify_m(font)

    util.fix_all_glyph_points(font, round=True)
    util.font_into_file(font, BUILD_FILE)
    util.log("Modified:", FONT_FILE, "->", BUILD_FILE)


def fix_subscript_numbers(font):
    def cp(from_, to):
        font.selection.select(from_)
        font.copy()
        font.selection.select(to)
        font.paste()

    # NOTE: After 0x10000 Hack has different glyph.
    #       So, you can't use the encoding number.
    def subs(code):
        hex_str = hex(code)[2:].upper().zfill(4)
        return "uni" + hex_str + ".subs"
    for i in range(10):
        cp(subs(0x30 + i), 0x2080 + i)
    font.selection.none()


def create_up_tack(font):
    # 0x22a5 ⊥ (UP TACK)
    font.selection.select(0x22a4)  # ⊤
    font.copy()
    font.selection.select(0x22a5)
    font.paste()

    rot_mat = psMat.rotate(3.1415926535)
    move_mat = psMat.translate(const.EM // 2, 1065)
    mat = psMat.compose(rot_mat, move_mat)
    font.transform(mat, ("noWidth",))

    font.selection.none()


def modify_0(font):
    # Cover outer of 「0」
    pen = font[0x30].glyphPen(replace=False)
    util.draw_square(pen,
                     (const.EM // 4, const.EM * 0.3),
                     const.EM * 0.45, const.EM * 0.67)
    util.draw_square(pen,
                     (const.EM // 4, const.EM * 0.3),
                     const.EM * 0.10, const.EM * 0.32,
                     clockwise=False)
    pen = None

    # Remove inner ellipse
    font.selection.select(0x30)
    font.intersect()
    font.selection.none()

    # Bring U+00B7 to center of 「0」
    font.selection.select(0xb7)  # ·
    font.copy()
    font.selection.select(0x30)
    font.pasteInto()
    font.selection.none()


def modify_m(font):
    # Hold original 「m」
    font.selection.select(0x6D)
    font.copy()

    # Extract where to remove
    glyph = font[0x6D]
    pen = glyph.glyphPen(replace=False)
    util.draw_square(pen,
                     (const.EM // 4, const.EM * 0.05),
                     const.EM * 0.15, const.EM * 0.13)
    font.intersect()

    # Create a cover that has a hole
    util.draw_square(pen,
                     (const.EM // 4, const.EM // 4),
                     const.EM, const.EM)
    pen = None
    font.correctDirection()

    # Add the cover to original 「m」then remove.
    font.pasteInto()
    font.intersect()
    font.selection.none()


if __name__ == "__main__":
    main()
