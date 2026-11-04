# PleckJP

> [Hack](https://sourcefoundry.org/hack/) と [IBM Plex Sans JP](https://www.ibm.com/plex/) を合成した日本語プログラミングフォント

次の 4 つのスタイルが用意されています。

- PleckJP-Regular
- PleckJP-Bold
- PleckJP-Italic
- PleckJP-BoldItalic

全てのスタイルで [Nerd Fonts](https://www.nerdfonts.com/) が合成されています。

## ダウンロード

[Release](https://github.com/ryota2357/PleckJP/releases) から zip ファイルがダウンロードできます。  
最新バージョンの zip ファイルの SHA256 checksum は `build/PleckJP_v*.sha256` にて確認ができます。

Homebrew (Mac) の場合は次のコマンドからもダウンロード可能です。

```sh
brew tap ryota2357/pleck-jp
brew install pleck-jp
```

Nix の場合は [NUR](https://nur.nix-community.org/) からインストールできます。

```nix
# flake input に追加
inputs.nur = {
  url = "github:nix-community/NUR";
  inputs.nixpkgs.follows = "nixpkgs";
};

# packages から参照
nur.repos.ryota2357.pleckjp-font
```

## スクリーンショット

![code-cpp-rust](./images/code-cpp-rust.png)

![chars](./images/chars.png)

![nerdfonts](./images/nerdfonts.png)

![gotop](./images/gotop.png)

## 関連記事

- [プログラミング用合成フォント PleckJP を作った](https://ryota2357.com/blog/2023/dev-font-pleckjp/)
- [プログラミング用合成フォント PleckJP の合成スクリプトの実装解説](https://ryota2357.com/blog/2023/pleck-jp-impl-exp/)

## ビルド

docker がインストールされている環境で次のコマンドでビルドを行います。

```sh
make
```

ビルドが完了すると `build/` ディレクトリに ttf ファイルが生成されます。
より詳しくは [HowToBuild.md](./HowToBuild.md) を確認してください。

<details>
<summary>リリースの方法</summary>

docker に加えて、python, sed (GNU sed), zip, sha256sum などが必要です。

推奨する環境の構築方法は docker と nix をインストールし、`nix develop` でシェルを起動する方法です。
nix-direnv を利用すると、ディレクトリに入るだけで自動的に環境が構築されます (`direnv allow` が必要)。

また、[Docker Hub の ryota2357/pleck-jp](https://hub.docker.com/repository/docker/ryota2357/pleckjp/general) に release イメージを公開する処理も含まれています。
不要な場合は適宜 `Makefile` を修正してください。

次のコマンドでリリースビルドを行います。

```sh
make release
```

ビルドが完了すると `build/` ディレクトリに .ttf, .zip, .sha256 ファイルが生成されます。

</details>

## Masked バリアント (API キーの伏せ字)

代表的なプロバイダーの API キーを伏せ字で表示する `PleckJP Masked` ファミリーを生成できます。
82 プロバイダー / 200+ プレフィックス (OpenAI, Anthropic, GitHub, GitLab, Slack, Stripe,
AWS, Cloudflare, DigitalOcean, Datadog, npm, Vercel, Supabase, Sentry, Hugging Face など) と、
`KEY="..."` 形式の代入コンテキスト、PEM ヘッダに対応しています。
通常の `make` や `make release` では生成されず、次のコマンドで明示的にビルドします。
入力に `build/PleckJP-*.ttf` を使うので、先に通常のビルドを済ませてください。

```sh
make masked   # build/PleckJP Masked-*.ttf が生成される
```

表示例:

```text
OPENAI_API_KEY=sk-proj-AbCdEf123456   ->   OPENAI_API_KEY=sk-proj-••••••••••••
gh auth token: ghp_16C7e42F292c6912   ->   gh auth token: ghp_••••••••••••••••
SLACK=xoxb-1234-5678-abcdef           ->   SLACK=xoxb-••••-••••-••••••
```

- 伏せ字になるのは、対応プレフィックスの直後に続く英数字です (`oc_sk_...` のような `_sk_` 連結も対象)
- 直前が英字の場合は伏せ字にしません (`task-runner`, `risk_assessment`, `desk-top` はそのまま)
- 長いプレフィックスが優先されます (`sk-ant-api03-XyZ` はプレフィックス全体を残して本文だけ伏せる)
- 伏せ字は空白・クォートなどの記号で止まります (`sk-abc def` の `def` はそのまま)
- キー内部の区切り (`-`, `_`) を挟んでも伏せ字は継続します (`xoxb-1234-5678-abc` は全体が伏せ字)
- ドット区切り (`ya29.a0Af...`, `dp.st....`) は最初の区間だけが伏せ字になります
- PEM ヘッダは末尾の `-----` だけが伏せ字になります (base64 本文は行をまたぐため対象外)
- `re_` や `pa-` のような短いプレフィックスは一般語にも当たります (`re_runner` は伏せ字)
- あくまで描画だけの変化です。コピーしたテキストは元のままなので、貼り付け先には正しいキーが入ります

プレフィックスの一覧は `src/fonttools_/mask.py` のデータテーブル
(`HYPHEN_PREFIXES` / `UNDERSCORE_PREFIXES` / `DOT_PREFIXES` / `CONTEXT_KEYS` / `PEM_HEADERS`)
にまとまっています。追加したいプロバイダーがあれば、そこに 1 行足すだけで反映されます。

仕組みは OpenType の `calt` (Contextual Alternates) フィーチャーを 1 つ追加しているだけで、
既存のフィーチャーやグリフには一切手を加えていません (追加グリフは `mask.dot` の 1 つだけ)。
そのため `calt` を無効にすれば、フォントを切り替えずに元の表示へ戻せます。

```jsonc
// 例: VS Code の settings.json
"editor.fontLigatures": "'calt' 0"
```

`calt` を適用するかどうかは描画側の実装に依存します。HarfBuzz を使うターミナルやエディタ
(WezTerm, Kitty, VS Code など) では既定で有効です。

動作確認は `src/fonttools_/mask_test.py` で行えます (uharfbuzz が必要。未インストール時は SKIP)。

```sh
python3 src/fonttools_/mask_test.py
```

## ライセンス

- フォントの合成スクリプトは MIT License にてライセンスされています。
- 合成元のフォントデータなどは別のライセンスが適用されています。
- 詳しくは [LICENSE](./LICENSE) を確認してください。
