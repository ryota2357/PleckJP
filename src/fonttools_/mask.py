"""API キーの伏せ字 (masked) バリアントを生成する。

`build/PleckJP-*.ttf` を入力に取り、GSUB へ `calt` フィーチャーを 1 つだけ追加した
`PleckJP Masked-*.ttf` を出力する。既存のフィーチャー・ルックアップには一切触れない
(新しいルックアップは LookupList の末尾に追加するので既存インデックスは不変)。

伏せ字の対象は `sk-` / `sk_` (および `oc_sk_` のような `_sk_` 連結) の直後に続く
英数字の連続。例:

    sk-ant-api03-XXXX   ->  sk-•••-•••••-••••
    oc_sk_abc123        ->  oc_sk_••••••
    task-runner         ->  task-runner      (誤爆しない)

使い方:

    python3 src/fonttools_/mask.py                       # build/ の 4 スタイル全部
    python3 src/fonttools_/mask.py IN.ttf OUT.ttf        # 1 ファイルだけ
"""

import sys
from copy import deepcopy
from os.path import join

from fontTools.otlLib.builder import buildSingleSubstSubtable
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables as ot

STYLES = ("Regular", "Bold", "Italic", "BoldItalic")

FAMILY = "PleckJP"
MASKED_FAMILY = "PleckJP Masked"
BUILD_DIR = "build"

FEATURE_TAG = "calt"
MASK_GLYPH = "mask.dot"

# 伏せ字にする文字 (キー本体に現れる英数字のみ。記号は残す)
ALNUM_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
LETTER_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
TRIGGER_CHARS = ("s", "k")
SEPARATOR_CHARS = ("-", "_")

# 伏せ字を継続させる連結記号 (キー内部に現れる区切り。空白やクォートで伏せ字は止まる)
GLUE_CHARS = ("-", "_")

# mask.dot のアウトラインを借りる元グリフ (先頭から順に探す)
MASK_SOURCE_GLYPHS = ("uni2022", "period", "uni25CF", "uni0041")


def main() -> None:
    args = sys.argv[1:]
    if not args:
        for style in STYLES:
            src = join(BUILD_DIR, f"{FAMILY}-{style}.ttf")
            dst = join(BUILD_DIR, f"{MASKED_FAMILY}-{style}.ttf")
            convert(src, dst)
        return
    if len(args) != 2:
        raise SystemExit("usage: mask.py [INPUT.ttf OUTPUT.ttf]")
    convert(args[0], args[1])


def convert(src_path: str, dst_path: str) -> None:
    font = TTFont(src_path)
    build_masked_variant(font)
    font.save(dst_path)
    print(f"masked: {src_path} -> {dst_path}")


def build_masked_variant(font: TTFont) -> None:
    gsub = font["GSUB"].table
    if FEATURE_TAG in {r.FeatureTag for r in gsub.FeatureList.FeatureRecord}:
        raise SystemExit(f"'{FEATURE_TAG}' already exists in {font.reader.file.name}")

    cmap = font.getBestCmap()
    mask_glyph = add_mask_glyph(font)
    lookups = add_mask_lookups(font, gsub, cmap, mask_glyph)
    add_feature(gsub, FEATURE_TAG, lookups)
    rename_family(font)


# ---------------------------------------------------------------- glyph


def add_mask_glyph(font: TTFont) -> str:
    """`mask.dot` を追加する。アウトラインは既存グリフを流用し、字幅は半角セルに合わせる。"""
    glyf = font["glyf"]
    hmtx = font["hmtx"]

    if MASK_GLYPH in font.getGlyphOrder():
        return MASK_GLYPH

    source = next((n for n in MASK_SOURCE_GLYPHS if n in glyf.glyphs), None)
    if source is None:
        raise SystemExit("no glyph to use as the mask dot")

    order = list(font.getGlyphOrder())
    order.append(MASK_GLYPH)
    font.setGlyphOrder(order)

    glyf.glyphs[MASK_GLYPH] = deepcopy(glyf[source])
    advance, lsb = hmtx[source]
    hmtx[MASK_GLYPH] = (advance, lsb)
    # Note: cmap には登録しない (伏せ字専用の内部グリフ)。
    #       サブセット化するツールでは落とされる可能性があるため、その場合は cmap 登録が必要。
    return MASK_GLYPH


# --------------------------------------------------------------- lookups


def add_mask_lookups(font: TTFont, gsub: ot.GSUB, cmap: dict, mask_glyph: str) -> list:
    """calt で使うルックアップを末尾に追加し、そのインデックスを返す。"""
    glyph = lambda ch: cmap[ord(ch)]  # noqa: E731

    alnum = [glyph(ch) for ch in ALNUM_CHARS]
    letter = [glyph(ch) for ch in LETTER_CHARS]
    s, k = (glyph(ch) for ch in TRIGGER_CHARS)

    # 誤爆ブロッカー用の無変換ルックアップ (letter を letter に置換するだけ)
    noop = add_lookup(gsub, 1, [buildSingleSubstSubtable({s: s})])
    mask = add_lookup(
        gsub, 1, [buildSingleSubstSubtable({g: mask_glyph for g in alnum})]
    )

    subtables = []
    for sep_char in SEPARATOR_CHARS:
        sep = glyph(sep_char)
        # 1) ブロッカー: 直前が英字なら何もしない (task- / risk_ / xsk_ を弾く)
        subtables.append(
            chain_rule(font, [letter], [[s], [k], [sep]], [(0, noop)])
        )
        # 2) トリガー: `sk-` / `sk_` の直後の英数字 1 文字を伏せ字にする
        subtables.append(
            chain_rule(font, [], [[s], [k], [sep], alnum], [(3, mask)])
        )
    # 3) 継続: 伏せ字の直後の英数字も伏せ字にする (英数字の連続を最後まで潰す)。
    #    キー内部の区切り (- _) を挟んでも継続させるが、区切りの直前が伏せ字である
    #    ことを条件にする (task-runner のような通常のハイフン連結を巻き込まない)。
    subtables.append(chain_rule(font, [[mask_glyph]], [alnum], [(0, mask)]))
    for glue_char in GLUE_CHARS:
        subtables.append(
            chain_rule(font, [[glyph(glue_char)], [mask_glyph]], [alnum], [(0, mask)])
        )

    chain = add_lookup(gsub, 6, subtables)
    return [chain]


def add_lookup(gsub: ot.GSUB, lookup_type: int, subtables: list) -> int:
    lookup = ot.Lookup()
    lookup.LookupType = lookup_type
    lookup.LookupFlag = 0
    lookup.SubTable = subtables
    lookup.SubTableCount = len(subtables)
    lookups = gsub.LookupList.Lookup
    lookups.append(lookup)
    gsub.LookupList.LookupCount = len(lookups)
    return len(lookups) - 1


def chain_rule(font: TTFont, backtrack: list, inputs: list, records: list) -> ot.ChainContextSubst:
    """ChainContextSubst (format 3) を 1 ルール分組み立てる。

    backtrack は「直前のグリフ」を先頭にした逆順のリスト、inputs は入力シーケンス
    (各要素はグリフ名のリスト = クラス)、records は (sequenceIndex, lookupIndex)。
    """
    subtable = ot.ChainContextSubst()
    subtable.Format = 3
    subtable.BacktrackCoverage = [coverage(font, g) for g in backtrack]
    subtable.InputCoverage = [coverage(font, g) for g in inputs]
    subtable.LookAheadCoverage = []
    subtable.SubstLookupRecord = [subst_record(i, lookup) for i, lookup in records]
    return subtable


def coverage(font: TTFont, glyphs: list) -> ot.Coverage:
    cov = ot.Coverage()
    cov.glyphs = sorted(set(glyphs), key=font.getGlyphID)
    return cov


def subst_record(sequence_index: int, lookup_index: int) -> ot.SubstLookupRecord:
    record = ot.SubstLookupRecord()
    record.SequenceIndex = sequence_index
    record.LookupListIndex = lookup_index
    return record


# --------------------------------------------------------------- feature


def add_feature(gsub: ot.GSUB, tag: str, lookup_indices: list) -> None:
    """FeatureList に tag を追加し、全 LangSys から参照させる。

    FeatureList はタグの昇順で並んでいる必要があるため挿入位置を保ち、
    FeatureIndex の繰り上がりを全 LangSys に反映する。
    """
    records = gsub.FeatureList.FeatureRecord
    tags = [r.FeatureTag for r in records]
    position = sum(1 for t in tags if t < tag)

    feature = ot.Feature()
    feature.FeatureParams = None
    feature.LookupListIndex = lookup_indices
    feature.LookupCount = len(lookup_indices)

    record = ot.FeatureRecord()
    record.FeatureTag = tag
    record.Feature = feature

    records.insert(position, record)
    gsub.FeatureList.FeatureCount = len(records)

    remap = [i if i < position else i + 1 for i in range(len(records) - 1)]
    for lang_sys in all_lang_systems(gsub):
        indices = [remap[i] for i in lang_sys.FeatureIndex]
        indices.insert(sum(1 for i in indices if i < position), position)
        lang_sys.FeatureIndex = indices
        lang_sys.FeatureCount = len(indices)


def all_lang_systems(gsub: ot.GSUB) -> list:
    lang_systems = []
    for script_record in gsub.ScriptList.ScriptRecord:
        script = script_record.Script
        if script.DefaultLangSys is not None:
            lang_systems.append(script.DefaultLangSys)
        lang_systems.extend(r.LangSys for r in script.LangSysRecord)
    return lang_systems


# ------------------------------------------------------------------ name


def rename_family(font: TTFont) -> None:
    """ファミリー名を `PleckJP Masked` にする (スタイル名はそのまま)。"""
    name = font["name"]
    family = name.getDebugName(1) or FAMILY
    if not family.startswith(FAMILY):
        raise SystemExit(f"unexpected family name: {family!r}")
    subfamily = name.getDebugName(2) or "Regular"
    suffix = family[len(FAMILY):]  # 空文字 (通常) か既存のサフィックス
    masked_family = f"{MASKED_FAMILY}{suffix}"

    for record in list(name.names):
        if record.nameID == 1:
            name.setName(masked_family, 1, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 3:
            unique_id = (name.getDebugName(3) or "").replace(
                f"{family} {subfamily}", f"{masked_family} {subfamily}"
            )
            name.setName(unique_id, 3, record.platformID, record.platEncID, record.langID)
        elif record.nameID == 4:
            name.setName(
                f"{masked_family} {subfamily}",
                4,
                record.platformID,
                record.platEncID,
                record.langID,
            )
        elif record.nameID == 6:
            postscript_name = f"{masked_family.replace(' ', '')}-{subfamily}"
            name.setName(postscript_name, 6, record.platformID, record.platEncID, record.langID)


if __name__ == "__main__":
    main()
