"""mask.py が生成した Masked バリアントの検証スクリプト。

    python3 src/fonttools_/mask_test.py [MASKED.ttf [BASE.ttf]]

BASE.ttf を省略した場合は、MASKED.ttf のパスから導出する
(`build/PleckJP Masked-*.ttf` 以外の場所を指定した場合は `build/PleckJP-<style>.ttf`)。

uharfbuzz が無い環境では SKIP して終了する (Docker イメージには入っていない)。
"""

import sys
from os.path import isfile

from fontTools.ttLib import TTFont

FAMILY = "PleckJP"
MASKED_FAMILY = "PleckJP Masked"
BASE_FONT = f"build/{FAMILY}-Regular.ttf"
MASKED_FONT = f"build/{MASKED_FAMILY}-Regular.ttf"
MASK_GLYPH = "mask.dot"

# 伏せ字になるべき入力
MASKED_CASES = [
    "sk-ant-api03-XXXX",
    "sk-abc123",
    "sk_live_abc123",
    "oc_sk_abc123",
    "--sk-abc",
    "key=sk-abc123",
]

# 伏せ字になってはいけない入力 (誤爆ブロッカー)
UNMASKED_CASES = [
    "task-runner",
    "risk_assessment",
    "desk-top",
    "xsk_foo",
    "SK-ABC",
]

# 伏せ字が止まるべき入力 (区切り文字の後)
STOP_CASES = [
    ("sk-abc def", "def"),
    ("sk-abc,next", "next"),
]

# 既存の見た目が変わっていないことを確認する入力 (ASCII / かな / 漢字 / 合字)
UNCHANGED_CASES = [
    "abcdefghijklmnopqrstuvwxyz",
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "0123456789 !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~",
    "あいうえおアイウエオ漢字日本語",
    "a -> b != c => d",
    "0123456789",
]


def main() -> int:
    try:
        import uharfbuzz as hb
    except ImportError:
        print("SKIP: uharfbuzz is not installed")
        return 0

    masked_path = sys.argv[1] if len(sys.argv) > 1 else MASKED_FONT
    base_path = sys.argv[2] if len(sys.argv) > 2 else resolve_base_path(masked_path)
    if base_path == masked_path:
        print(f"FAIL: base font and masked font are the same file: {base_path}")
        return 1
    for path in (base_path, masked_path):
        if not isfile(path):
            print(f"FAIL: not found: {path}")
            return 1
    base = Shaper(hb, base_path)
    masked = Shaper(hb, masked_path)

    failures = []

    for text in MASKED_CASES:
        glyphs = masked.shape(text)
        tail = glyphs[len(base.shape(text[: text.index("sk") + 3])) :]
        if not tail or any(g not in masked.maskable_glyphs for g in tail):
            failures.append(f"not masked: {text!r} -> {glyphs}")

    for text in UNMASKED_CASES:
        glyphs = masked.shape(text)
        if MASK_GLYPH in glyphs:
            failures.append(f"false positive: {text!r} -> {glyphs}")

    for text, word in STOP_CASES:
        glyphs = masked.shape(text)
        tail = base.shape(word)
        if glyphs[-len(tail) :] != tail:
            failures.append(f"masking did not stop before {word!r}: {glyphs}")

    for text in UNCHANGED_CASES:
        if base.shape(text) != masked.shape(text):
            failures.append(f"shaping changed: {text!r}")

    # グリフ順は「元のグリフ + mask.dot」でなければならない
    base_order = TTFont(base_path).getGlyphOrder()
    masked_order = TTFont(masked_path).getGlyphOrder()
    if masked_order[: len(base_order)] != base_order or masked_order[len(base_order) :] != [MASK_GLYPH]:
        failures.append("glyph order changed")

    family = TTFont(masked_path)["name"].getDebugName(1)
    if family != MASKED_FAMILY:
        failures.append(f"family name: {family!r}")

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print(f"OK: {masked_path} ({len(MASKED_CASES) + len(UNMASKED_CASES) + len(STOP_CASES) + len(UNCHANGED_CASES)} cases)")
    return 0


def resolve_base_path(masked_path: str) -> str:
    """MASKED 側のパスから、比較対象の通常フォントのパスを求める。"""
    base_path = masked_path.replace(MASKED_FAMILY, FAMILY)
    if base_path != masked_path:
        return base_path
    # ファイル名に "PleckJP Masked" が含まれない場合は name テーブルからスタイルを引く
    subfamily = TTFont(masked_path)["name"].getDebugName(2) or "Regular"
    return f"build/{FAMILY}-{subfamily}.ttf"


class Shaper:
    def __init__(self, hb, path: str):
        self.order = TTFont(path).getGlyphOrder()
        self.hb = hb
        self.font = hb.Font(hb.Face(hb.Blob.from_file_path(path)))
        cmap = TTFont(path).getBestCmap()
        # 伏せ字になってよいグリフ (mask.dot と、キー内部の区切り記号)
        self.maskable_glyphs = {MASK_GLYPH, cmap[ord("-")], cmap[ord("_")]}

    def shape(self, text: str) -> list:
        buffer = self.hb.Buffer()
        buffer.add_str(text)
        buffer.guess_segment_properties()
        self.hb.shape(self.font, buffer)
        return [self.order[info.codepoint] for info in buffer.glyph_infos]


if __name__ == "__main__":
    sys.exit(main())
