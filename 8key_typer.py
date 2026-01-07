#!/usr/bin/env python3
"""
8キータイピングゲーム
ttyperライクなタイピング練習ツール
"""

import json
import sys
import os
import curses
import time
import random


class NormalTyper:
    """通常のQWERTYタイピングモード"""
    def __init__(self, target_words):
        self.target_text = target_words
        self.typed_words = []
        self.current_input = ""
        self.current_target = target_words[0] if target_words else ""
        
        # 統計
        self.start_time = None
        self.total_chars = 0
        self.correct_chars = 0
        self.errors = 0
        
    def calculate_wpm(self):
        """WPM計算"""
        if not self.start_time:
            return 0
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        words = self.correct_chars / 5
        minutes = elapsed / 60
        return int(words / minutes) if minutes > 0 else 0
    
    def calculate_accuracy(self):
        """正確性計算"""
        total = self.correct_chars + self.errors
        if total == 0:
            return 100
        return int((self.correct_chars / total) * 100)
    
    def check_completion(self):
        """完了チェック"""
        return len(self.typed_words) >= len(self.target_text)
    
    def draw_screen(self, stdscr):
        """画面描画"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # ヘッダー
        header = "⌨️  Normal Typing Mode"
        stdscr.addstr(0, 0, "=" * min(width - 1, 70))
        stdscr.addstr(1, (width - len(header)) // 2, header, curses.A_BOLD)
        stdscr.addstr(2, 0, "=" * min(width - 1, 70))
        
        y = 4
        
        # 統計
        wpm = self.calculate_wpm()
        accuracy = self.calculate_accuracy()
        progress = len(self.typed_words)
        total = len(self.target_text)
        
        stats = f"WPM: {wpm} | 正確性: {accuracy}% | 進捗: {progress}/{total}"
        stdscr.addstr(y, 0, stats, curses.A_BOLD)
        y += 2
        
        # 目標テキスト
        stdscr.addstr(y, 0, "📝 目標テキスト:", curses.A_BOLD)
        y += 1
        
        display_start = len(self.typed_words)
        display_words = self.target_text[display_start:display_start + 10]
        
        x = 2
        for i, word in enumerate(display_words):
            if i == 0:
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                attr = curses.A_NORMAL
            
            if x + len(word) + 1 < width:
                stdscr.addstr(y, x, word, attr)
                x += len(word) + 1
        
        y += 2
        
        # 現在の入力
        stdscr.addstr(y, 0, "⌨️  入力:", curses.A_BOLD)
        y += 1
        
        # 入力と目標を比較して色分け
        target = self.current_target
        typed = self.current_input
        
        display_text = ""
        for i in range(max(len(target), len(typed))):
            if i < len(typed):
                if i < len(target) and typed[i] == target[i]:
                    # 正しい
                    display_text += typed[i]
                else:
                    # 間違い
                    display_text += typed[i]
            elif i < len(target):
                # まだ入力されていない
                display_text += "_"
        
        stdscr.addstr(y, 2, display_text)
        
        # エラー表示
        if len(typed) > 0:
            if len(typed) <= len(target):
                is_correct = all(typed[i] == target[i] for i in range(len(typed)))
                if not is_correct:
                    y += 1
                    stdscr.addstr(y, 2, "❌ ミスタイプ！", curses.color_pair(2))
        
        y += 2
        
        # 確定済み
        if self.typed_words:
            stdscr.addstr(y, 0, "✅ 確定済み:", curses.A_BOLD)
            y += 1
            typed_text = " ".join(self.typed_words[-10:])
            if len(typed_text) > width - 5:
                typed_text = "..." + typed_text[-(width - 8):]
            stdscr.addstr(y, 2, typed_text[:width - 3])
        
        # ヘルプ
        help_y = height - 2
        if help_y > y + 2:
            stdscr.addstr(help_y, 0, "-" * min(width - 1, 70))
            help_text = "通常通り入力 | Space=次の単語 | BS=削除 | Ctrl+C=終了"
            stdscr.addstr(help_y + 1, 0, help_text[:width - 1])
        
        stdscr.refresh()
    
    def run(self, stdscr):
        """メインループ"""
        curses.curs_set(1)  # カーソル表示
        stdscr.nodelay(False)
        stdscr.keypad(True)
        
        # 色の設定
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        
        self.start_time = time.time()
        
        while True:
            self.draw_screen(stdscr)
            
            if self.check_completion():
                break
            
            try:
                key = stdscr.getch()
                
                # Ctrl+C で終了
                if key == 3:
                    return False
                
                # Backspace
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.current_input:
                        self.current_input = self.current_input[:-1]
                
                # Space または Enter で次の単語
                elif key in (32, 10, 13):
                    if self.current_input:
                        # 正解チェック
                        if self.current_input == self.current_target:
                            self.typed_words.append(self.current_input)
                            self.correct_chars += len(self.current_input)
                        else:
                            self.typed_words.append(f"[{self.current_input}]")
                            self.errors += abs(len(self.current_input) - len(self.current_target))
                        
                        # 次の単語
                        if len(self.typed_words) < len(self.target_text):
                            self.current_target = self.target_text[len(self.typed_words)]
                        
                        self.current_input = ""
                
                # 通常の文字入力
                elif 32 <= key <= 126:  # 印字可能なASCII文字
                    char = chr(key)
                    self.current_input += char
                
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {str(e)}")
                stdscr.refresh()
                stdscr.getch()
                return False
        
        return True


class EightKeyTyper:
    def __init__(self, dictionary_file, show_predictive=False):
        self.dictionary = {}
        self.load_dictionary(dictionary_file)
        self.valid_keys = set('asdfjkl;')
        self.show_predictive = show_predictive  # 予測候補を表示するか
        
        # タイピング統計
        self.start_time = None
        self.total_chars = 0
        self.correct_chars = 0
        self.errors = 0
        
        # 現在の状態
        self.target_text = []  # 目標の単語リスト
        self.typed_words = []  # 確定した単語
        self.current_word = ""  # 現在入力中の8キー
        self.current_target = ""  # 現在の目標単語
        self.candidates = []
        self.predictive_candidates = []  # 予測候補
        self.word_start_time = None
        
    def load_dictionary(self, json_file):
        """辞書を読み込む"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)
    
    def decode(self, eight_key_input):
        """8キー入力をデコード"""
        if not eight_key_input or eight_key_input not in self.dictionary:
            return []
        return [item['word'] for item in self.dictionary[eight_key_input]]
    
    def decode_with_predictive(self, eight_key_input):
        """
        8キー入力をデコード（予測候補付き）
        
        Returns:
            tuple: (完全マッチ候補リスト, 予測候補リスト)
        """
        if not eight_key_input:
            return [], []
        
        # 完全マッチ
        exact_matches = []
        if eight_key_input in self.dictionary:
            exact_matches = [item['word'] for item in self.dictionary[eight_key_input]]
        
        # 予測候補（現在の入力で始まるパターン）
        predictive_matches = []
        if self.show_predictive:
            for key, candidates in self.dictionary.items():
                if key.startswith(eight_key_input) and key != eight_key_input:
                    for candidate in candidates:
                        predictive_matches.append({
                            'word': candidate['word'],
                            'key': key,
                            'freq': candidate['freq']
                        })
            
            # 頻度順にソート
            predictive_matches.sort(key=lambda x: x['freq'], reverse=True)
        
        return exact_matches, predictive_matches
    
    def generate_target_text(self, word_count=20, difficulty='easy', min_freq=0):
        """練習用のテキストを生成"""
        # 辞書から単語を選択
        if difficulty == 'easy':
            # ユニークパターンのみ（候補が1つ）
            candidates = [k for k, v in self.dictionary.items() if len(v) == 1]
        elif difficulty == 'medium':
            # 候補が1-2個
            candidates = [k for k, v in self.dictionary.items() if 1 <= len(v) <= 2]
        else:  # hard
            # 全て
            candidates = list(self.dictionary.keys())
        
        # 頻度フィルタリング（最も頻度の高い単語を優先）
        if min_freq > 0:
            filtered_candidates = []
            for k in candidates:
                # そのキーの中で最も頻度の高い単語の頻度をチェック
                max_freq = max(item['freq'] for item in self.dictionary[k])
                if max_freq >= min_freq:
                    filtered_candidates.append(k)
            candidates = filtered_candidates if filtered_candidates else candidates
        
        # 頻度順にソートして選択
        candidates_with_freq = [(k, max(item['freq'] for item in self.dictionary[k])) for k in candidates]
        candidates_with_freq.sort(key=lambda x: x[1], reverse=True)
        
        # 上位から選択（ランダム性も少し残す）
        top_candidates = [k for k, _ in candidates_with_freq[:min(len(candidates_with_freq), word_count * 3)]]
        selected_keys = random.sample(top_candidates, min(word_count, len(top_candidates)))
        
        self.target_text = [self.dictionary[k][0]['word'] for k in selected_keys]
        self.current_target = self.target_text[0] if self.target_text else ""
        
    def calculate_wpm(self):
        """WPM（Words Per Minute）を計算"""
        if not self.start_time:
            return 0
        elapsed = time.time() - self.start_time
        if elapsed == 0:
            return 0
        # 標準: 5文字 = 1単語
        words = self.correct_chars / 5
        minutes = elapsed / 60
        return int(words / minutes) if minutes > 0 else 0
    
    def calculate_accuracy(self):
        """正確性を計算"""
        total = self.correct_chars + self.errors
        if total == 0:
            return 100
        return int((self.correct_chars / total) * 100)
    
    def get_8key_for_word(self, word):
        """単語から8キー入力を逆引き"""
        word_lower = word.lower()
        for key, candidates in self.dictionary.items():
            if any(c['word'].lower() == word_lower for c in candidates):
                return key
        return None
    
    def _apply_case_from_input(self, word, input_keys):
        """入力時の大文字小文字状態を単語に反映（辞書は大文字小文字統合済み）"""
        # 辞書は既に大文字小文字を統合しているため、辞書の形式をそのまま返す
        # 将来的に大文字入力をサポートする場合はここで変換
        return word
    
    def draw_screen(self, stdscr):
        """画面を描画"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # 最小サイズチェック
        if height < 20 or width < 40:
            try:
                stdscr.addstr(0, 0, "Terminal too small!")
                stdscr.addstr(1, 0, f"Need: 40x20, Got: {width}x{height}")
                stdscr.refresh()
            except:
                pass
            return
        
        # ヘッダー
        header = "🎮 8-Key Typing Game"
        try:
            stdscr.addstr(0, 0, "=" * min(width - 1, 70))
            stdscr.addstr(1, max(0, (width - len(header)) // 2), header, curses.A_BOLD)
            stdscr.addstr(2, 0, "=" * min(width - 1, 70))
        except:
            pass
        
        y = 4
        
        # 統計情報
        wpm = self.calculate_wpm()
        accuracy = self.calculate_accuracy()
        progress = len(self.typed_words)
        total = len(self.target_text)
        
        stats = f"WPM: {wpm} | 正確性: {accuracy}% | 進捗: {progress}/{total}"
        stdscr.addstr(y, 0, stats, curses.A_BOLD)
        y += 2
        
        # 目標テキスト表示
        stdscr.addstr(y, 0, "📝 目標テキスト:", curses.A_BOLD)
        y += 1
        
        # 表示する単語（現在位置から）
        display_start = len(self.typed_words)
        display_words = self.target_text[display_start:display_start + 10]
        
        x = 2
        for i, word in enumerate(display_words):
            if i == 0:
                # 現在の単語（ハイライト）
                attr = curses.A_REVERSE | curses.A_BOLD
            else:
                attr = curses.A_NORMAL
            
            if x + len(word) + 1 < width:
                stdscr.addstr(y, x, word, attr)
                x += len(word) + 1
        
        y += 2
        
        # 入力状態
        stdscr.addstr(y, 0, "⌨️  8キー入力:", curses.A_BOLD)
        y += 1
        
        if self.current_word:
            stdscr.addstr(y, 2, f"[{self.current_word}]", curses.A_REVERSE)
        else:
            stdscr.addstr(y, 2, "(入力開始してください)")
        
        y += 2
        
        # 候補
        if self.candidates or self.predictive_candidates:
            # 完全マッチ候補
            if self.candidates:
                stdscr.addstr(y, 0, "💡 変換候補 (完全マッチ):", curses.A_BOLD)
                y += 1
                
                # 現在の目標単語があるかチェック
                target_in_candidates = self.current_target.lower() in [c.lower() for c in self.candidates]
                
                for i, candidate in enumerate(self.candidates[:5]):
                    is_target = candidate.lower() == self.current_target.lower()
                    if is_target:
                        attr = curses.A_BOLD | curses.color_pair(1)  # 緑色
                    else:
                        attr = curses.A_NORMAL
                    
                    marker = "→" if is_target else " "
                    text = f" {marker} {i + 1}. {candidate}"
                    if y < height - 8:
                        stdscr.addstr(y, 2, text[:width - 3], attr)
                        y += 1
                
                if not target_in_candidates and self.current_target:
                    if y < height - 8:
                        stdscr.addstr(y, 2, f"⚠️  目標: '{self.current_target}' が候補にありません！", 
                                    curses.A_BOLD | curses.color_pair(2))
                        y += 1
            
            # 予測候補
            if self.predictive_candidates and y < height - 6:
                y += 1
                if y < height - 6:
                    stdscr.addstr(y, 0, "🔮 予測候補 (続きの可能性):", curses.A_BOLD | curses.color_pair(3))
                    y += 1
                    
                    displayed = 0
                    for pred in self.predictive_candidates[:10]:
                        if y >= height - 5:
                            break
                        
                        word = pred['word']
                        key = pred['key']
                        
                        # 目標単語かチェック
                        is_target = word.lower() == self.current_target.lower()
                        if is_target:
                            attr = curses.A_BOLD | curses.color_pair(1)
                            marker = "→"
                        else:
                            attr = curses.A_DIM
                            marker = " "
                        
                        text = f" {marker} [{key}] {word}"
                        stdscr.addstr(y, 2, text[:width - 3], attr)
                        y += 1
                        displayed += 1
                    
                    if len(self.predictive_candidates) > displayed:
                        if y < height - 5:
                            stdscr.addstr(y, 2, f"  ... 他 {len(self.predictive_candidates) - displayed} 個")
                            y += 1
        
        y += 1
        
        # 確定済み
        if self.typed_words:
            stdscr.addstr(y, 0, "✅ 確定済み:", curses.A_BOLD)
            y += 1
            typed_text = " ".join(self.typed_words[-10:])  # 最後の10単語
            if len(typed_text) > width - 5:
                typed_text = "..." + typed_text[-(width - 8):]
            stdscr.addstr(y, 2, typed_text[:width - 3])
        
        # ヘルプ（下部）
        help_y = height - 2
        if help_y > y + 2:
            stdscr.addstr(help_y, 0, "-" * min(width - 1, 70))
            help_text = "a-z/;=入力 | 1-9=選択 | BS=削除 | Ctrl+C=終了"
            stdscr.addstr(help_y + 1, 0, help_text[:width - 1])
        
        stdscr.refresh()
    
    def check_completion(self):
        """完了チェック"""
        return len(self.typed_words) >= len(self.target_text)
    
    def run(self, stdscr):
        """メインループ"""
        # cursesの設定
        curses.curs_set(0)
        stdscr.nodelay(False)
        stdscr.keypad(True)
        
        # 色の設定
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        
        self.start_time = time.time()
        self.word_start_time = time.time()
        
        while True:
            self.draw_screen(stdscr)
            
            # 完了チェック
            if self.check_completion():
                break
            
            try:
                key = stdscr.getch()
                
                # Ctrl+C で終了
                if key == 3:
                    return False
                
                # Backspace
                elif key in (curses.KEY_BACKSPACE, 127, 8):
                    if self.current_word:
                        self.current_word = self.current_word[:-1]
                        if self.current_word:
                            self.candidates, self.predictive_candidates = self.decode_with_predictive(self.current_word)
                        else:
                            self.candidates = []
                            self.predictive_candidates = []
                
                # 数字キーで候補選択
                elif 49 <= key <= 57:  # '1' to '9'
                    num = key - 48
                    if self.candidates and 1 <= num <= len(self.candidates):
                        selected = self.candidates[num - 1]
                        
                        # 入力時の大文字小文字状態を反映
                        selected_adjusted = self._apply_case_from_input(selected, self.current_word)
                        
                        # 正解チェック
                        if selected.lower() == self.current_target.lower():
                            self.typed_words.append(selected_adjusted)
                            self.correct_chars += len(selected_adjusted)
                            
                            # 次の単語へ
                            if len(self.typed_words) < len(self.target_text):
                                self.current_target = self.target_text[len(self.typed_words)]
                        else:
                            self.errors += len(selected_adjusted)
                        
                        self.current_word = ""
                        self.candidates = []
                        self.predictive_candidates = []
                        self.word_start_time = time.time()
                
                # 8キー入力
                elif chr(key).lower() in self.valid_keys:
                    self.current_word += chr(key).lower()
                    self.candidates, self.predictive_candidates = self.decode_with_predictive(self.current_word)
                    
                    # 候補が1つで、それが目標単語なら自動確定
                    if len(self.candidates) == 1 and self.candidates[0].lower() == self.current_target.lower():
                        self.typed_words.append(self.candidates[0])
                        self.correct_chars += len(self.candidates[0])
                        
                        if len(self.typed_words) < len(self.target_text):
                            self.current_target = self.target_text[len(self.typed_words)]
                        
                        self.current_word = ""
                        self.candidates = []
                        self.word_start_time = time.time()
                
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {str(e)}")
                stdscr.refresh()
                stdscr.getch()
                return False
        
        return True


def show_results(stdscr, typer, mode_name=""):
    """結果画面を表示"""
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    y = height // 2 - 8
    
    title = f"🎉 完了！ {mode_name}"
    stdscr.addstr(y, max(0, (width - len(title)) // 2), title, curses.A_BOLD)
    y += 2
    
    stdscr.addstr(y, 0, "=" * min(width - 1, 70))
    y += 2
    
    wpm = typer.calculate_wpm()
    accuracy = typer.calculate_accuracy()
    total_time = int(time.time() - typer.start_time) if typer.start_time else 0
    
    results = [
        f"⏱️  タイム: {total_time}秒",
        f"⚡ WPM: {wpm}",
        f"🎯 正確性: {accuracy}%",
        f"✅ 正解: {typer.correct_chars}文字",
        f"❌ エラー: {typer.errors}文字",
        f"📝 単語数: {len(typer.typed_words)}",
    ]
    
    for result in results:
        stdscr.addstr(y, max(0, (width - len(result)) // 2), result)
        y += 1
    
    y += 2
    stdscr.addstr(y, 0, "=" * min(width - 1, 70))
    y += 2
    
    msg = "何かキーを押して終了..."
    stdscr.addstr(y, max(0, (width - len(msg)) // 2), msg)
    
    stdscr.refresh()
    stdscr.getch()


def main():
    if len(sys.argv) < 2:
        dict_files = ['linux_words.json', 'common_words_3000.json', 'common_words_1000.json']
        dictionary_file = None
        
        for df in dict_files:
            if os.path.exists(df):
                dictionary_file = df
                break
        
        if not dictionary_file:
            print("エラー: 辞書ファイルが見つかりません")
            return
    else:
        dictionary_file = sys.argv[1]
    
    print("\n" + "=" * 70)
    print("  🎮 8-Key Typing Game")
    print("=" * 70)
    print("\n  8キー入力でタイピング練習！")
    print("  目標の単語を8キーで入力して、候補から選択してください\n")
    print("\nモードを選択:")
    print("  1. 8キーモード - 8キー入力で候補選択")
    print("  2. 通常モード   - QWERTYキーボードで直接入力")
    print("  3. 比較モード   - 両方のモードを続けてプレイ")
    
    mode_choice = input("\n選択 (1-3, デフォルト=1): ").strip() or '1'
    
    if mode_choice == '3':
        # 比較モードは後で処理
        pass
        print("難易度を選択:")
    print("  1. Easy   - 候補が1つだけの単語")
    print("  2. Medium - 候補が1-2個の単語")
    print("  3. Hard   - 全ての単語")
    
    difficulty_map = {'1': 'easy', '2': 'medium', '3': 'hard'}
    choice = input("\n選択 (1-3, デフォルト=1): ").strip() or '1'
    difficulty = difficulty_map.get(choice, 'easy')
    
    word_count = input("単語数 (デフォルト=20): ").strip()
    word_count = int(word_count) if word_count.isdigit() else 20
    
    # 頻度フィルタリングのオプション
    print("\n頻度フィルタを選択:")
    print("  1. 全ての単語     - 頻度に関係なく")
    print("  2. 高頻度のみ     - 頻度100以上")
    print("  3. 最高頻度のみ   - 頻度1000以上")
    
    freq_map = {'1': 0, '2': 100, '3': 1000}
    freq_choice = input("\n選択 (1-3, デフォルト=1): ").strip() or '1'
    min_freq = freq_map.get(freq_choice, 0)
    
    # 予測候補の表示オプション (8キーモードのみ)
    show_predictive = False
    if mode_choice in ['1', '3']:
        pred_choice = input("\n予測候補を表示しますか？ (y/n, デフォルト=n): ").strip().lower()
        show_predictive = (pred_choice == 'y')
    
    print("\n辞書を読み込んでいます...")
    typer = EightKeyTyper(dictionary_file, show_predictive=show_predictive)
    
    print("テキストを生成しています...")
    typer.generate_target_text(word_count, difficulty, min_freq)
    
    if mode_choice == '3':
        # 比較モード
        print("\n=== 比較モード ===")
        print("同じテキストを8キーモードと通常モードでタイプします\n")
        input("Enterキーを押して開始...")
        
        results = []
        
        # 8キーモード
        print("\n[1/2] 8キーモードでプレイ...")
        time.sleep(1)
        
        try:
            typer_8key = EightKeyTyper(dictionary_file, show_predictive=show_predictive)
            typer_8key.target_text = typer.target_text.copy()
            typer_8key.current_target = typer_8key.target_text[0]
            
            completed = curses.wrapper(typer_8key.run)
            if completed:
                results.append(('8キーモード', typer_8key))
        except KeyboardInterrupt:
            print("\n8キーモードをスキップしました")
        
        input("\n[2/2] 通常モードに進みます。Enterキーを押してください...")
        
        # 通常モード
        try:
            typer_normal = NormalTyper(typer.target_text.copy())
            completed = curses.wrapper(typer_normal.run)
            if completed:
                results.append(('通常モード', typer_normal))
        except KeyboardInterrupt:
            print("\n通常モードをスキップしました")
        
        # 比較結果を表示
        if len(results) == 2:
            print("\n" + "=" * 70)
            print("📊 比較結果")
            print("=" * 70)
            print()
            
            for mode_name, mode_typer in results:
                wpm = mode_typer.calculate_wpm()
                accuracy = mode_typer.calculate_accuracy()
                total_time = int(time.time() - mode_typer.start_time) if mode_typer.start_time else 0
                
                print(f"【{mode_name}】")
                print(f"  ⏱️  タイム: {total_time}秒")
                print(f"  ⚡ WPM: {wpm}")
                print(f"  🎯 正確性: {accuracy}%")
                print(f"  ✅ 正解: {mode_typer.correct_chars}文字")
                print(f"  ❌ エラー: {mode_typer.errors}文字")
                print()
            
            # 勝者判定
            wpm_8key = results[0][1].calculate_wpm()
            wpm_normal = results[1][1].calculate_wpm()
            
            if wpm_8key > wpm_normal:
                winner = "8キーモード"
                diff = wpm_8key - wpm_normal
            elif wpm_normal > wpm_8key:
                winner = "通常モード"
                diff = wpm_normal - wpm_8key
            else:
                winner = "引き分け"
                diff = 0
            
            print("=" * 70)
            if winner != "引き分け":
                print(f"🏆 勝者: {winner} (+{diff} WPM)")
            else:
                print("🏆 引き分け！")
            print("=" * 70)
        
        return
    
    elif mode_choice == '2':
        # 通常モードのみ
        normal_typer = NormalTyper(typer.target_text)
        input("\nEnterキーを押して開始...")
        
        try:
            completed = curses.wrapper(normal_typer.run)
            
            if completed:
                curses.wrapper(lambda stdscr: show_results(stdscr, normal_typer, "通常モード"))
            else:
                print("\n中断されました")
        except KeyboardInterrupt:
            print("\n\n中断されました")
        
        return
    
    # 8キーモードのみ (デフォルト)
    input("\nEnterキーを押して開始...")
    
    try:
        completed = curses.wrapper(typer.run)
        
        if completed:
            curses.wrapper(lambda stdscr: show_results(stdscr, typer, "8キーモード"))
        else:
            print("\n中断されました")
            
    except KeyboardInterrupt:
        print("\n\n中断されました")
    except Exception as e:
        print(f"\nエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
