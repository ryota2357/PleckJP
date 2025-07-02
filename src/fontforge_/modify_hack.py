import sys
import fontforge
import psMat
import util
import properties as const

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
BUILD_FILE = sys.argv[2]


def main() -> None:
    font = fontforge.open(FONT_FILE)

    # Use IBMPlexSansJP glyph
    util.font_clear_glyph(font, 0x2003)  # 　(EM SPACE)
    util.font_clear_glyph(font, 0x266A)  # ♪

    # Use Nerd Font glyph
    util.font_clear_glyph(font, 0xE0A0, 0xE0B3)  # Private Use Area

    util.font_set_em(font, const.ASCENT, const.DESCENT, const.EM)
    util.font_resize_all_width(font, const.EM // 2)

    # TODO: Create glyph
    # 0x226a: ≪
    # 0x226b: ≫
    fix_subscript_numbers(font)
    create_up_tack(font)
    create_inverted_ohm_sign(font)

    modify_0(font)
    modify_m(font)

    util.fix_all_glyph_points(font, round=True)
    util.font_into_file(font, BUILD_FILE)
    util.log("Modified:", FONT_FILE, "->", BUILD_FILE)


def fix_subscript_numbers(font) -> None:
    def copy(from_: int | str, to: int | str):
        font.selection.select(from_)
        font.copy()
        font.selection.select(to)
        font.paste()
        font.selection.none()

    def fix_lookup(target: int | str, replace_old: str, replace_new: str) -> None:
        glyph = font[target]
        pos_subs = glyph.getPosSub("*")
        for pos_sub in pos_subs:
            # pos_sub: (subtable_name, lookup_type, replacement1, replacement2, ...)
            subtable = pos_sub[0]
            replacements = pos_sub[2:]
            if replace_old not in replacements:
                continue
            new_replacements = []
            for replacement in replacements:
                if replacement == replace_old:
                    new_replacements.append(replace_new)
                else:
                    new_replacements.append(replacement)
            glyph.removePosSub(subtable)
            if len(new_replacements) == 1:
                glyph.addPosSub(subtable, new_replacements[0])
            else:
                glyph.addPosSub(subtable, tuple(new_replacements))

    def uni(code: int) -> str:
        hex_str = hex(code)[2:].upper().zfill(4)
        return "uni" + hex_str

    for i in range(10):
        base = uni(0x30 + i)
        to = uni(0x2080 + i)
        copy(base + ".subs", to)
        fix_lookup(base, base + ".subs", to)
        util.font_clear_glyph(font, base + ".subs")


def create_up_tack(font) -> None:
    # 0x22a5 ⊥ (UP TACK)
    font.selection.select(0x22A4)  # ⊤
    font.copy()
    font.selection.select(0x22A5)
    font.paste()
    rot_mat = psMat.rotate(3.1415926535)
    move_mat = psMat.translate(const.EM // 2, 1065)
    font.transform(psMat.compose(rot_mat, move_mat), ("noWidth",))
    font.selection.none()


def create_inverted_ohm_sign(font) -> None:
    # 0x2127 ℧ (INVERTED OHM SIGN)
    font.selection.select(0x2126)  # Ω
    font.copy()
    font.selection.select(0x2127)
    font.paste()
    rot_mat = psMat.rotate(3.1415926535)
    move_mat = psMat.translate(const.EM // 2, 1214)
    font.transform(psMat.compose(rot_mat, move_mat), ("noWidth",))
    font.selection.none()


def modify_0(font) -> None:
    # Cover outer of 「0」
    pen = font[0x30].glyphPen(replace=False)
    util.draw_square(
        pen,
        (const.EM // 4, round(const.EM * 0.3)),
        round(const.EM * 0.45),
        round(const.EM * 0.67),
    )
    util.draw_square(
        pen,
        (const.EM // 4, round(const.EM * 0.3)),
        round(const.EM * 0.10),
        round(const.EM * 0.32),
        clockwise=False,
    )
    pen = None

    # Remove inner ellipse
    font.selection.select(0x30)
    font.intersect()
    font.selection.none()

    # Bring U+00B7 to center of 「0」
    font.selection.select(0xB7)  # ·
    font.copy()
    font.selection.select(0x30)
    font.pasteInto()
    font.selection.none()


def modify_m(font) -> None:
    # Hold original 「m」
    font.selection.select(0x6D)
    font.copy()

    # Extract where to remove
    glyph = font[0x6D]
    pen = glyph.glyphPen(replace=False)
    util.draw_square(
        pen,
        (const.EM // 4, round(const.EM * 0.05)),
        round(const.EM * 0.15),
        round(const.EM * 0.13),
    )
    font.intersect()

    # Create a cover that has a hole
    util.draw_square(pen, (const.EM // 4, const.EM // 4), const.EM, const.EM)
    pen = None
    font.correctDirection()

    # Add the cover to original 「m」then remove.
    font.pasteInto()
    font.intersect()
    font.selection.none()


if __name__ == "__main__":
    main()
