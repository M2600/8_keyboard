#!/bin/bash
# 8キー入力システム - 各スクリプトの実行例

# ============================================================
# 1. 辞書生成
# ============================================================

# 大規模辞書（121,558語）
# python3 8key_dict_with_freq.py linux_words_8key.tsv freq_mapping.json linux_words.json

# 中規模辞書（3,000語）
# python3 8key_dict_with_freq.py common_words_3000_8key.tsv freq_mapping.json common_words_3000.json

# 小規模辞書（1,000語）
# python3 8key_dict_with_freq.py common_words_1000_8key.tsv freq_mapping.json common_words_1000.json

# 全ての辞書を一括生成
# python3 8key_dict_with_freq.py linux_words_8key.tsv freq_mapping.json linux_words.json && \
# python3 8key_dict_with_freq.py common_words_3000_8key.tsv freq_mapping.json common_words_3000.json && \
# python3 8key_dict_with_freq.py common_words_1000_8key.tsv freq_mapping.json common_words_1000.json


# ============================================================
# 2. タイピングゲーム
# ============================================================

# 基本的な起動（デフォルト辞書を自動選択）
# python3 8key_typer.py

# 辞書を指定して起動
# python3 8key_typer.py linux_words.json
# python3 8key_typer.py common_words_3000.json
# python3 8key_typer.py common_words_1000.json

# 起動後の選択例:
#   モード: 1 (8キーモード), 2 (通常モード), 3 (比較モード)
#   難易度: 1 (Easy), 2 (Medium), 3 (Hard)
#   単語数: 20 (デフォルト)
#   頻度フィルタ: 1 (全て), 2 (高頻度), 3 (最高頻度)
#   予測候補: y/n


# ============================================================
# 3. シェルIME
# ============================================================

# 基本的な起動（デフォルト辞書を自動選択）
# python3 8key_shell.py

# 辞書を指定して起動
# python3 8key_shell.py linux_words.json
# python3 8key_shell.py common_words_3000.json
# python3 8key_shell.py common_words_1000.json

# 操作方法:
#   a-z/; : 8キー入力
#   ↑↓   : 候補選択
#   Space : 確定
#   BS    : 削除
#   Ctrl+C: 終了


# ============================================================
# 4. デコーダー (CLI)
# ============================================================

# インタラクティブモード
# python3 8key_decoder.py linux_words.json
# python3 8key_decoder.py common_words_3000.json
# python3 8key_decoder.py common_words_1000.json

# 入力例:
#   fjd   → the
#   jdlll → hello
#   quit  → 終了


# ============================================================
# 5. Web UI
# ============================================================

# Webサーバー起動（ポート8001）
# python3 -m http.server 8001
# ブラウザで http://localhost:8001/8key_input.html を開く

# 別のポートを使用する場合
# python3 -m http.server 8080


# ============================================================
# 6. データ生成（上級者向け）
# ============================================================

# 単語リストから8キーTSVを生成
# python3 8key_data_generator.py linux_words.txt linux_words_8key.tsv

# 頻度マッピングを生成（frequencyList.tsvから）
# python3 create_freq_mapping.py


# ============================================================
# 便利なコマンド
# ============================================================

# 辞書の統計情報を表示
# python3 -c "
# import json
# with open('linux_words.json', 'r') as f:
#     d = json.load(f)
#     print(f'パターン数: {len(d):,}')
#     print(f'総単語数: {sum(len(v) for v in d.values()):,}')
#     unique = sum(1 for v in d.values() if len(v) == 1)
#     print(f'ユニーク: {unique} ({unique/len(d)*100:.1f}%)')
# "

# 辞書ファイルのサイズ確認
# du -h *.json

# 特定の8キーパターンの候補を確認
# python3 -c "
# import json, sys
# with open('linux_words.json', 'r') as f:
#     d = json.load(f)
#     pattern = 'fjd'  # ここを変更
#     if pattern in d:
#         print(f'{pattern} の候補:')
#         for item in d[pattern][:10]:
#             print(f\"  {item['word']} (freq: {item['freq']})\")
# "


# ============================================================
# よく使うコマンド例
# ============================================================

echo "8キー入力システム - 実行例"
echo ""
echo "辞書生成:"
echo "  python3 8key_dict_with_freq.py linux_words_8key.tsv freq_mapping.json linux_words.json"
echo ""
echo "タイピングゲーム:"
echo "  python3 8key_typer.py"
echo ""
echo "シェルIME:"
echo "  python3 8key_shell.py"
echo ""
echo "デコーダー:"
echo "  python3 8key_decoder.py linux_words.json"
echo ""
echo "Webサーバー:"
echo "  python3 -m http.server 8001"
echo "  → http://localhost:8001/8key_input.html"
echo ""
echo "詳細は examples.sh を確認してください"
