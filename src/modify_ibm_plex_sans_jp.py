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

    set_all_em(font)

    # Shrink to 1:2
    util.glyph_riseze_width(font[0x2103], const.EM // 2)  # ℃
    util.glyph_riseze_width(font[0x2109], const.EM // 2)  # ℉
    util.glyph_riseze_width(font[0x2121], const.EM // 2)  # ℡
    util.glyph_riseze_width(font[0x212B], const.EM // 2)  # Å
    util.glyph_riseze_width(font[0xfb01], const.EM // 2)  # ﬁ
    util.glyph_riseze_width(font[0xfb02], const.EM // 2)  # ﬂ

    # Use Hack glyph
    util.font_clear_glyph(font, 0x20, 0x2044)    # number, alphabet, etc
    util.font_clear_glyph(font, 0x20ac)          # €
    util.font_clear_glyph(font, 0x2190, 0x21f5)  # arrow
    util.font_clear_glyph(font, 0x2200, 0x22A5)  # math symbol
    util.font_clear_glyph(font, 0x2116)          # №
    util.font_clear_glyph(font, 0x2122)          # ™
    util.font_clear_glyph(font, 0x23a7, 0x23ad)  # curly bracket
    util.font_clear_glyph(font, 0x2500, 0x2595)  # border symbol
    util.font_clear_glyph(font, 0x25a0, 0x25ef)  # block symbol

    resize_all_scale(font)

    util.font_into_file(font, BUILD_FILE)
    print(FONT_FILE, " -> ", BUILD_FILE)


def set_all_em(font):
    old_em = font.em
    font.selection.all()
    font.unlinkReferences()
    font.ascent = round(float(const.ASCENT) / const.EM * old_em)
    font.descent = round(float(const.DESCENT) / const.EM * old_em)
    font.em = const.EM
    font.selection.none()


def resize_all_scale(font):
    scale = 0.82
    x_to_center = const.EM * (1 - scale) / 2

    scale_mat = [psMat.scale(scale) for _ in range(2)]
    trans_mat = [psMat.translate(x) for x in (x_to_center, x_to_center / 2)]
    mat = [psMat.compose(scale_mat[i], trans_mat[i]) for i in range(2)]

    scaled = set()
    for glyph in font.glyphs():
        width = glyph.width
        unicode = glyph.unicode
        if unicode != -1 and unicode in scaled:
            util.debug(f"this is already scaled: {unicode:#x}")
            continue
        if width == const.EM:
            glyph.transform(mat[0])
            glyph.width = const.EM
        elif width == const.EM // 2:
            glyph.transform(mat[1])
            glyph.width = const.EM // 2
        else:
            name = glyph.glyphname
            print(f"unkown scale: {width} name: {name}")

    font.selection.all()
    font.round()
    font.selection.none()


if __name__ == "__main__":
    main()
