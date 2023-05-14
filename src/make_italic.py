import sys
import fontforge
import psMat
import util
import properties as const

if len(sys.argv) != 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
BUILD_FILE = sys.argv[2]

PI = 3.14159265358979323846


def main():
    font = fontforge.open(FONT_FILE)

    rot_rad = -1 * const.ITALICANGLE * PI / 180
    mat = psMat.skew(rot_rad)
    font.selection.all()
    font.transform(mat)
    font.round()
    font.selection.none()

    util.font_into_file(font, BUILD_FILE)
    util.log(FONT_FILE, " -> ", BUILD_FILE)


if __name__ == "__main__":
    main()
