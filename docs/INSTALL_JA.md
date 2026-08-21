# Frappe Helpdesk JP 導入手順

この文書は、Frappe Helpdeskの上流`develop`ブランチに対応する非公式日本語版をBench環境へ導入する手順です。

## 対応範囲

- Frappe Helpdeskのアプリケーション本体は上流の実装を維持します。
- 日本語対応は`helpdesk/locale/ja.po`で提供します。
- 2026年8月21日時点の`main.pot`にある1,499メッセージを収録しています。
- チケット、コメント、メール、ナレッジベースで日本語の入力・保存・全文検索に対応します。
- `pyproject.toml`が要求するFrappe Frameworkは`develop`系です。

## 前提条件

- Frappe Benchを実行できるLinux環境
- Frappe Framework `develop`
- Python 3.14以上（本リポジトリの`pyproject.toml`に準拠）
- Node.js、Yarn、Redis、MariaDBなど、Frappe Frameworkが要求する依存関係

Bench自体の準備は[Frappe FrameworkのInstallation](https://frappeframework.com/docs/user/en/installation)を参照してください。

## 新規導入

```bash
bench init --frappe-branch develop frappe-bench
cd frappe-bench

bench new-site helpdesk.test
bench --site helpdesk.test add-to-hosts

bench get-app https://github.com/frappe/telephony
bench get-app --branch jp https://github.com/katsushi2441/frappe-helpdesk-jp.git
bench --site helpdesk.test install-app helpdesk
bench build --app helpdesk
```

開発環境では次のコマンドで起動します。

```bash
bench start
```

ブラウザで`http://helpdesk.test:8000/helpdesk`を開きます。

## 日本語表示への切り替え

Helpdeskへログインし、次のいずれかで言語を`日本語`に変更します。

1. Helpdeskの`Settings`から`Preferences`、`Language & Time`を開く
2. Frappe Deskのユーザー設定で`Language`を`日本語`にする

変更後に表示が切り替わらない場合は、キャッシュを消去して再読み込みします。

```bash
bench --site helpdesk.test clear-cache
bench build --app helpdesk
```

## 既存のHelpdesk環境へ導入

作業前にサイトとデータベースをバックアップしてください。

```bash
cd /path/to/frappe-bench
bench --site your-site.example.com backup --with-files

cd apps/helpdesk
git remote add helpdesk-jp https://github.com/katsushi2441/frappe-helpdesk-jp.git
git fetch helpdesk-jp jp
git checkout -b helpdesk-jp helpdesk-jp/jp

cd ../..
bench setup requirements
bench --site your-site.example.com migrate
bench build --app helpdesk
bench --site your-site.example.com clear-cache
bench --site your-site.example.com execute helpdesk.search.build_index
bench --site your-site.example.com execute frappe.search.sqlite_search.build_index --kwargs '{"search_class_path":"helpdesk.search_sqlite.HelpdeskSearch","force":true}'
```

すでに`helpdesk-jp`リモートまたは同名のローカルブランチがある場合は、新規作成せず既存のものを利用してください。本番環境のプロセス再起動方法は、Supervisor、systemd、Dockerなど各環境の構成に従ってください。

## 日本語訳の更新

```bash
cd /path/to/frappe-bench/apps/helpdesk
git pull --rebase helpdesk-jp jp

cd ../..
bench build --app helpdesk
bench --site your-site.example.com clear-cache
bench --site your-site.example.com execute helpdesk.search.build_index
bench --site your-site.example.com execute frappe.search.sqlite_search.build_index --kwargs '{"search_class_path":"helpdesk.search_sqlite.HelpdeskSearch","force":true}'
```

最後の2コマンドは、ナレッジベース用Redis索引と、チケット・コメント・メール用SQLite索引を日本語検索対応の内容で再構築します。データ量が多い環境では完了まで時間がかかるため、利用の少ない時間帯に実行してください。

## 翻訳ファイルの検証

リポジトリ直下で実行します。

```bash
python3 scripts/validate_japanese_locale.py
```

検証内容は次のとおりです。

- 原文と日本語訳のメッセージ数およびIDの一致
- 未翻訳・fuzzyメッセージがないこと
- プレースホルダー、HTMLタグ、URL、エスケープ改行の保持
- BabelによるMO形式へのコンパイル

## 上流との関係

- 上流: <https://github.com/frappe/helpdesk>
- 公式ドキュメント: <https://docs.frappe.io/helpdesk>
- 公式翻訳: <https://crowdin.com/project/frappe>
- 日本語版フォーク: <https://github.com/katsushi2441/frappe-helpdesk-jp>

本リポジトリは非公式です。上流更新後は`main.pot`との差分を確認し、新規メッセージだけを翻訳して追従します。

## ライセンス

Frappe Helpdeskおよび本フォークはGNU Affero General Public License v3で提供されます。ネットワーク経由で改変版を提供する場合を含め、利用・配布時はライセンス条件を確認してください。
