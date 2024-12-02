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
より詳しくは [HowToBild.md](./HowToBuild.md) を確認してください。

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

## ライセンス

- フォントの合成スクリプトは MIT License にてライセンスされています。
- 合成元のフォントデータなどは別のライセンスが適用されています。
- 詳しくは [LICENSE](./LICENSE) を確認してください。
