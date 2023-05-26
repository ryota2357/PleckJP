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

    # Remove kerning info
    for lookup in font.gpos_lookups:
        if lookup.startswith("'halt'") or \
           lookup.startswith("'vhal'") or \
           lookup.startswith("'palt'") or \
           lookup.startswith("'vpal'") or \
           lookup.startswith("'kern'") or \
           lookup.startswith("'vkrn'"):
            font.removeLookup(lookup)

    # Remove vertical fonts
    font.removeLookup("'vert' Vertical Alternates lookup 18")
    font.removeLookup("'vrt2' Vertical Rotation & Alternates lookup 19")
    for glyph in font.glyphs():
        if glyph.unicode != -1:
            continue
        name = glyph.glyphname
        if name.endswith(".rotat"):
            util.font_clear_glyph(font, name)

    # Use Hack glyph
    util.font_clear_glyph(font, 0x20, 0x2002)    # number, alphabet, etc
    util.font_clear_glyph(font, 0x2004, 0x2044)  # ← skipping 0x2003 (EM SPACE)
    util.font_clear_glyph(font, 0x20ac)          # €
    util.font_clear_glyph(font, 0x2190, 0x21f5)  # arrow
    util.font_clear_glyph(font, 0x2200, 0x22A5)  # math symbol
    util.font_clear_glyph(font, 0x2116)          # №
    util.font_clear_glyph(font, 0x2122)          # ™
    util.font_clear_glyph(font, 0x23a7, 0x23ad)  # curly bracket
    util.font_clear_glyph(font, 0x2500, 0x2595)  # border symbol
    util.font_clear_glyph(font, 0x25a0, 0x25ef)  # block symbol

    util.font_set_em(font, const.ASCENT, const.DESCENT, const.EM)

    # Shrink to 1:2
    util.glyph_riseze_width(font[0x2103], const.EM // 2)  # ℃
    util.glyph_riseze_width(font[0x2109], const.EM // 2)  # ℉
    util.glyph_riseze_width(font[0x2121], const.EM // 2)  # ℡
    util.glyph_riseze_width(font[0x212B], const.EM // 2)  # Å
    util.glyph_riseze_width(font[0xfb01], const.EM // 2)  # ﬁ
    util.glyph_riseze_width(font[0xfb02], const.EM // 2)  # ﬂ

    # Fix width (Note that I don't know the meaning of the following glyphs)
    # unkown scale: 1257 name: section
    # unkown scale: 1187 name: dagger.prop
    # unkown scale: 1187 name: daggerdbl.prop
    # unkown scale: 1396 name: paragraph
    # unkown scale: 2799 name: perthousand.full
    # unkown scale: 1003 name: degree
    # unkown scale: 1290 name: plusminus
    # unkown scale: 1290 name: multiply
    # unkown scale: 1290 name: divide
    # unkown scale: 1290 name: zero.zero
    # unkown scale: 2052 name: uni51F0
    # unkown scale: 1245 name: a.alt01
    # unkown scale: 1245 name: g.alt01
    # unkown scale: 1142 name: g.alt02
    # unkown scale: 1290 name: zero.alt01
    # unkown scale: 1228 name: minus
    for name in ("section", "dagger.prop", "daggerdbl.prop", "paragraph",
                 "degree", "plusminus", "multiply",
                 "divide", "zero.zero", "uni51F0", "a.alt01", "g.alt01",
                 "g.alt02", "zero.alt01", "minus"):
        util.glyph_riseze_width(font[name], const.EM // 2)
    util.glyph_riseze_width(font["perthousand.full"], const.EM)

    modify_whitespace(font)
    resize_all_scale(font)

    util.fix_all_glyph_points(font)
    util.font_into_file(font, BUILD_FILE)
    util.log(FONT_FILE, " -> ", BUILD_FILE)


def resize_all_scale(font):
    scale = 0.82
    x_to_center = const.EM * (1 - scale) / 2

    scale_mat = [psMat.scale(scale) for _ in range(2)]
    trans_mat = [psMat.translate(x) for x in (x_to_center, x_to_center / 2)]
    mat = [psMat.compose(scale_mat[i], trans_mat[i]) for i in range(2)]

    for glyph in font.glyphs():
        width = glyph.width
        if width == const.EM:
            glyph.transform(mat[0])
            glyph.width = const.EM
        elif width == const.EM // 2:
            glyph.transform(mat[1])
            glyph.width = const.EM // 2
        else:
            name = glyph.glyphname
            util.log(f"unkown scale: {width} name: {name}")


def modify_whitespace(font):
    # NOTE: if modify 0x3000, it also apply to 0x2003 (EM SPACE)
    pen = font[0x3000].glyphPen(replace=False)

    # draw square frame
    util.draw_square(pen,
                     (const.EM // 2, (const.EM - const.DESCENT) // 2),
                     const.EM * 0.8, const.EM * 0.8)
    util.draw_square(pen,
                     (const.EM // 2, (const.EM - const.DESCENT) // 2),
                     const.EM * 0.7, const.EM * 0.7,
                     clockwise=False)

    util.draw_square(pen,
                     (const.EM // 2, (const.EM - const.DESCENT) // 2),
                     const.EM * 0.35, const.EM * 2)
    util.draw_square(pen,
                     (0, (const.EM - const.DESCENT) // 2),
                     const.EM * 0.5, const.EM * 0.35)
    util.draw_square(pen,
                     (const.EM, (const.EM - const.DESCENT) // 2),
                     const.EM * 0.5, const.EM * 0.35)
    pen = None

    font.selection.select(0x3000)
    font.intersect()
    font.selection.none()


if __name__ == "__main__":
    main()
