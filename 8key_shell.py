#!/usr/bin/env python3
"""
8キーシェル入力システム
ターミナル上でIME風の8キー入力を実現（リアルタイム版）
"""

import json
import sys
import os
import curses


class EightKeyShell:
    def __init__(self, dictionary_file):
        self.dictionary = {}
        self.load_dictionary(dictionary_file)
        self.valid_keys = set('asdfjkl;')
        self.confirmed_text = []
        self.current_word = ""
        self.candidates = []
        self.selected_index = 0
        
    def load_dictionary(self, json_file):
        """辞書を読み込む"""
        print(f"辞書を読み込んでいます: {json_file}")
        with open(json_file, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
        
        total_patterns = len(self.dictionary)
        total_words = sum(len(candidates) for candidates in self.dictionary.values())
        unique = sum(1 for candidates in self.dictionary.values() if len(candidates) == 1)
        
        print(f"✓ 読み込み完了")
        print(f"  総パターン: {total_patterns:,}")
        print(f"  総単語数: {total_words:,}")
        print(f"  ユニーク: {unique} ({unique/total_patterns*100:.1f}%)")
        print()
        
    def decode(self, eight_key_input):
        """8キー入力をデコード"""
        if not eight_key_input or eight_key_input not in self.dictionary:
            return []
        return [item['word'] for item in self.dictionary[eight_key_input]]
    
    def update_candidates(self):
        """現在の単語から候補を更新"""
        if self.current_word:
            self.candidates = self.decode(self.current_word)
            self.selected_index = 0
        else:
            self.candidates = []
            self.selected_index = 0
    
    def confirm_current_word(self):
        """現在の単語を確定"""
        if self.candidates and self.selected_index < len(self.candidates):
            self.confirmed_text.append(self.candidates[self.selected_index])
        elif self.current_word:
            self.confirmed_text.append(f"[{self.current_word}]")
        
        self.current_word = ""
        self.candidates = []
        self.selected_index = 0
    
    def draw_screen(self, stdscr):
        """画面を描画"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # ヘッダー
        header = "🎹 8-Key Shell Input System (IME Mode)"
        stdscr.addstr(0, 0, "=" * min(width - 1, 70))
        stdscr.addstr(1, 0, header[:width - 1])
        stdscr.addstr(2, 0, "=" * min(width - 1, 70))
        
        # 確定済みテキスト
        y = 4
        stdscr.addstr(y, 0, "📝 確定済み:", curses.A_BOLD)
        y += 1
        confirmed_display = " ".join(self.confirmed_text) if self.confirmed_text else "(空)"
        # 長いテキストは折り返し
        if len(confirmed_display) > width - 5:
            confirmed_display = confirmed_display[:width - 8] + "..."
        stdscr.addstr(y, 2, confirmed_display[:width - 3])
        
        # 現在の入力
        y += 2
        stdscr.addstr(y, 0, "⌨️  入力中:", curses.A_BOLD)
        y += 1
        if self.current_word:
            stdscr.addstr(y, 2, f"[{self.current_word}]", curses.A_REVERSE)
        else:
            stdscr.addstr(y, 2, "(入力待ち)")
        
        # 候補
        y += 2
        if self.candidates:
            stdscr.addstr(y, 0, "💡 変換候補:", curses.A_BOLD)
            y += 1
            for i, candidate in enumerate(self.candidates[:9]):
                attr = curses.A_REVERSE if i == self.selected_index else curses.A_NORMAL
                candidate_text = f" {i + 1}. {candidate} "
                if y < height - 3:
                    stdscr.addstr(y, 2, candidate_text[:width - 3], attr)
                    y += 1
            if len(self.candidates) > 9:
                stdscr.addstr(y, 2, f"  ... 他 {len(self.candidates) - 9} 個")
                y += 1
        
        # 使い方（下部）
        help_y = height - 2
        help_text = "a-z/;=入力 | Space=確定 | ↑↓=選択 | BS=削除 | Ctrl+C=終了"
        if help_y > y + 1:
            stdscr.addstr(help_y, 0, "-" * min(width - 1, 70))
            stdscr.addstr(help_y + 1, 0, help_text[:width - 1])
        
        stdscr.refresh()
    
    def run(self, stdscr):
        """メインループ（curses版）"""
        # cursesの設定
        curses.curs_set(0)  # カーソルを非表示
        stdscr.nodelay(False)  # キー入力待機
        stdscr.keypad(True)  # 特殊キーを有効化
        
        while True:
            self.draw_screen(stdscr)
            
            try:
                key = stdscr.getch()
                
                # Ctrl+C または ESC で終了
                if key == 3 or key == 27:
                    break
                
                # 矢印キーで候補選択
                elif key == curses.KEY_UP:
                    if self.candidates and self.selected_index > 0:
                        self.selected_index -= 1
                
                elif key == curses.KEY_DOWN:
                    if self.candidates and self.selected_index < len(self.candidates) - 1:
                        self.selected_index += 1
                
                # Backspace
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.current_word:
                        self.current_word = self.current_word[:-1]
                        self.update_candidates()
                    elif self.confirmed_text:
                        self.confirmed_text.pop()
                
                # Space または Enter で確定
                elif key in (32, 10, 13):  # Space, Enter
                    self.confirm_current_word()
                
                # 数字キーで直接選択
                elif 49 <= key <= 57:  # '1' to '9'
                    num = key - 48  # ASCIIコードから数値に変換
                    if self.candidates and 1 <= num <= len(self.candidates):
                        self.selected_index = num - 1
                        self.confirm_current_word()
                
                # 8キー入力
                elif chr(key).lower() in self.valid_keys:
                    self.current_word += chr(key).lower()
                    self.update_candidates()
                    
                    # 候補が1つだけの場合は自動的にその候補を選択
                    if len(self.candidates) == 1:
                        self.selected_index = 0
                
            except Exception as e:
                # エラー表示用（デバッグ）
                stdscr.addstr(0, 0, f"Error: {str(e)}")
                stdscr.refresh()
                stdscr.getch()
                break
        
        # 終了処理
        return " ".join(self.confirmed_text)


def main():
    if len(sys.argv) < 2:
        # デフォルトの辞書ファイルを使用
        dict_files = ['linux_words.json', 'common_words_3000.json', 'common_words_1000.json']
        dictionary_file = None
        
        for df in dict_files:
            if os.path.exists(df):
                dictionary_file = df
                break
        
        if not dictionary_file:
            print("エラー: 辞書ファイルが見つかりません")
            print("Usage: python 8key_shell.py [dictionary.json]")
            print("例: python 8key_shell.py linux_words.json")
            return
    else:
        dictionary_file = sys.argv[1]
        if not os.path.exists(dictionary_file):
            print(f"エラー: ファイルが見つかりません: {dictionary_file}")
            return
    
    print("\n" + "=" * 70)
    print("  🎹 8-Key Shell Input System へようこそ！")
    print("=" * 70)
    print("\n  8つのキー (a/s/d/f/j/k/l/;) だけでリアルタイム入力")
    print("  IMEのように一文字ごとに候補が表示されます\n")
    
    shell = EightKeyShell(dictionary_file)
    
    input("Enterキーを押して開始...")
    
    try:
        # cursesで実行
        result = curses.wrapper(shell.run)
        
        # 終了後の処理
        print("\n" + "=" * 70)
        print("📝 最終結果:")
        if result:
            print("  ", result)
            print("\n保存しますか? (y/n): ", end="")
            if input().lower().strip() == 'y':
                filename = "8key_output.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(result + "\n")
                print(f"✓ 保存しました: {filename}")
        print("\nご利用ありがとうございました！")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n終了しました")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
