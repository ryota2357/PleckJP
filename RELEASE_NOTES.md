# Release Notes

## v2.2.0 (2026-08-10)

- 使用している NerdFonts を v3.5.0 に上げました。新規アイコンの追加や既存のグリフの改善などが含まれています。
- 本フォントのため独自に作成している NerdFonts 合成スクリプトのバグにより、本来のアイコン 240 個が欠落していたのを修正しました。
  - この欠落は v1.4.0 以降のすべてのバージョンにおいて発生していました。

NerdFontsの変更の詳細は https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.5.0 を確認してください。

**Full Changelog**: [v2.1.2...v2.2.0](https://github.com/ryota2357/PleckJP/compare/v2.1.2...v2.2.0)

## v2.1.2 (2026-03-05)

- 一部環境にて文字幅が想定外に大きく描画される問題を修正しました。

**Full Changelog**: [v2.1.1...v2.1.2](https://github.com/ryota2357/PleckJP/compare/v2.1.1...v2.1.2)

## v2.1.1 (2025-09-16)

- Nerd Fonts (アイコンフォント) のうち Octicons に由来するグリフ (300個程度) の位置を調整しました。

**Full Changelog**: [v2.1.0...v2.1.1](https://github.com/ryota2357/PleckJP/compare/v2.1.0...v2.1.1)

## v2.1.0 (2025-09-13)

- 使用している IBM Plex Sans JP のバージョンを 3.0.0 へ上げました。漢字グリフを中心に多くのグリフで改善・修正が行われています。

IBM Plex Sans JP の変更は https://github.com/IBM/plex/releases/tag/%40ibm%2Fplex-sans-jp%403.0.0 を確認してください。

また、今回のリリースより、GitHub の Immutable Releases を有効にしました。
> Immutable Releases は GitHub Tag や Release, Release assets を後から変更できないようにする機能です。
> 引用: [GitHub の Immutable Releases を有効にしてセキュリティインシデントを防ごう](https://zenn.dev/shunsuke_suzuki/articles/github-immutable-release)

**Full Changelog**: [v2.0.0...v2.1.0](https://github.com/ryota2357/PleckJP/compare/v2.0.0...v2.1.0)

## v2.0.0 (2025-07-03)

🎉 Version 2

- 使用している IBM Plex Sans JP のバージョンを 2.0.0 へ上げました。日本語グリフが新たに1万個以上追加されました。
- グリフの調整を行いました。主要な変更点は以下です。
  - ローマ数字 `Ⅰ Ⅱ Ⅲ` や `ⅰ ⅱ ⅲ` を適切に半角に収まるよう修正しました。
  - 将棋グリフ `☖ ☗` の形を整えました。
  - いくつかの (v1.6.0 まで IBM Plex Sans JP から合成していた) グリフを Hack から合成するように変更しました (`℧`, `ℵ` など)。

IBM Plex Sans JP の変更は https://github.com/IBM/plex/releases/tag/%40ibm%2Fplex-sans-jp%402.0.0 を確認してください。

**Full Changelog**: [v1.6.0...v2.0.0](https://github.com/ryota2357/PleckJP/compare/v1.6.0...v2.0.0)

## v1.6.0 (2025-05-02)

- 使用している NerdFonts を v3.4.0 に上げました。いくつかのグリフで小さな改善が行われています。

NerdFontsの変更の詳細は https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.4.0 を確認してください。

**Full Changelog**: [v1.5.0...v1.6.0](https://github.com/ryota2357/PleckJP/compare/v1.5.0...v1.6.0)

## v1.5.0 (2025-03-07)

- 使用している IBM Plex Sans JP のバージョンを 1.1.0 へ上げました。いくつかのグリフの追加・小さな改善がされています。
- NULL文字のグリフ幅が 0 になっていなかった問題を修正しました。この変更での表示等への影響はないはずです。

IBM Plex Sans JP の変更は https://github.com/IBM/plex/releases/tag/%40ibm%2Fplex-sans-jp%401.1.0 を確認してください。

**Full Changelog**: [v1.4.0...v1.5.0](https://github.com/ryota2357/PleckJP/compare/v1.4.0...v1.5.0)

## v1.4.0 (2024-12-01)

- 使用している NerdFonts を v3.3.0 に上げました。v3.3.0 には Devicons の破壊的変更が含まれているので注意してください。
- いくつかのアイコンフォントのグリフの調整を行いました。

NerdFontsの変更の詳細は https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.3.0 を確認してください。

また、このリリースから Docker Hub にビルドに使用した環境 (image) の公開を行うことにしました。利用方法については [Docker Hub: ryota2357/pleckjp](https://hub.docker.com/r/ryota2357/pleckjp) または README を確認してください。

**Full Changelog**: [v1.3.0...v1.4.0](https://github.com/ryota2357/PleckJP/compare/v1.3.0...v1.4.0)

## v1.3.0 (2024-04-05)

- 使用している NerdFonts を v3.2.0 に上げました。追加されたアイコンなどは[NerdFontsのリリース](https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.2.0)を参照してください。
- いくつかのアイコンフォントのグリフの調整を行いました。

**Full Changelog**: [v1.2.1...v1.3.0](https://github.com/ryota2357/PleckJP/compare/v1.2.1...v1.3.0)

## v1.2.1 (2023-11-27)

- 使用している NerdFonts を v3.1.1 に上げました。これによりTOMLアイコンが追加されました。

**Full Changelog**: [v1.2.0...v1.2.1](https://github.com/ryota2357/PleckJP/compare/v1.2.0...v1.2.1)

## v1.2.0 (2023-11-22)

- 使用している NerdFonts をv3.1.0に上げました。
- NerdFonts v3.1.0 の変更に伴い、一部グリフの調整を行いました。

NerdFontsの変更の詳細は https://github.com/ryanoasis/nerd-fonts/releases/tag/v3.1.0 を確認してください。

**Full Changelog**: [v1.1.0...v1.2.0](https://github.com/ryota2357/PleckJP/compare/v1.1.0...v1.2.0)

## v1.1.0 (2023-08-12)

- macOSで等幅フォントとして分類されるようにしました。

ビルドスクリプトに大きな変更を行ったため、マイナーバージョンを上げました。グリフに変更はありません。

## v1.0.2 (2023-07-10)

- 凰の幅が半角になっていたのを修正しました

## v1.0.1 (2023-06-17)

- フォントの一部メタデータの修正をしました。
- グリフに変更はありません。

**Full Changelog**: [v1.0.0...v1.0.1](https://github.com/ryota2357/PleckJP/compare/v1.0.0...v1.0.1)

## v1.0.0 (2023-06-16)

🎉 Version 1

- 8点点字グリフを追加しました。
- フォント内メタデータのコピーライトのタイポを修正しました。
- Deviconsフォントの合成を調整しました。

**Full Changelog**: [v0.4.1...v1.0.0](https://github.com/ryota2357/PleckJP/compare/v0.4.1...v1.0.0)

## v0.4.1 (2023-06-10)

- 使用している Nerd Fonts のグリフを v3.0.1 から v3.0.2 にアップデートしました。

**Full Changelog**: [v0.4.0...v0.4.1](https://github.com/ryota2357/PleckJP/compare/v0.4.0...v0.4.1)

## v0.4.0 (2023-06-04)

- Italic と BoldItalic において、斜体にするグリフを変更しました。
- Nerd Font の合成を独自のものに変更しました。

**Full Changelog**: [v0.3.0...v0.4.0](https://github.com/ryota2357/PleckJP/compare/v0.3.0...v0.4.0)

## v0.3.0 (2023-05-27)

- ascentを 1556 から 1618 に変更しました。
- descent を 492 から 430 に変更しました。
- underline の位置を -265 から -255 に変更しました。
- 0x22a5 (UP TACK) のグリフを追加しました。

**Full Changelog**: [v0.2.2...v0.3.0](https://github.com/ryota2357/PleckJP/compare/v0.2.2...v0.3.0)

## v0.2.2 (2023-05-20)

- Nerd Fonts のグリフ名を追加しました。
- 各フォントの合成手順を変更し、lookupやaltuniをより適切に合成されるように修正しました。

**Full Changelog**: [v0.2.1...v0.2.2](https://github.com/ryota2357/PleckJP/compare/v0.2.1...v0.2.2)

## v0.2.1 (2023-05-15)

- カーニング情報を削除しました。

**Full Changelog**: [v0.2.0...v0.2.1](https://github.com/ryota2357/PleckJP/compare/v0.2.0...v0.2.1)

## v0.2.0 (2023-05-12)

- フォントに埋め込まれたCopyrightに改行が不足していたので追加しました。
- 一部グリフ幅を正しいものに修正しました。
- 縦書きグリフとそのテーブルを削除しました。縦書きグリフは今後のアップデートで復活する可能性があります。
- 全角空白を可視化しました。

**Full Changelog**: [v0.1.1...v0.2.0](https://github.com/ryota2357/PleckJP/compare/v0.1.1...v0.2.0)

## v0.1.1 (2023-05-07)

日本語の一部グリフが欠けていたのを修正しました。

**Full Changelog**: [v0.1.0...v0.1.1](https://github.com/ryota2357/PleckJP/compare/v0.1.0...v0.1.1)

## v0.1.0 (2023-05-06)

🎉 First release!

- PleckJP-Regular
- PleckJP-Bold
- PleckJP-Italic
- PleckJP-BoldItalic
