import sys
import fontforge
import util

if len(sys.argv) < 3:
    raise ValueError("Invalid argument")

FONT_FILE = sys.argv[1]
PATCH_FILES = sys.argv[2:-1]
BUILD_FILE = sys.argv[-1]


def main():
    font = fontforge.open(FONT_FILE)
    for patch_file in PATCH_FILES:
        font.mergeFonts(patch_file)
        util.log("Patched:", patch_file, "->", BUILD_FILE)

    util.font_into_file(font, BUILD_FILE)
    util.log("Generated:", BUILD_FILE)


if __name__ == "__main__":
    main()
