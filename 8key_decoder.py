#!/usr/bin/env python3
"""
8キーデコーダー
8キー入力から元のテキストを復元（頻度順に候補を返す）
"""

import json
import sys


class EightKeyDecoder:
    def __init__(self):
        self.word_dict = {}  # 8キー入力 -> [{"word": "...", "freq": ...}]
        
    def load_dictionary(self, json_file):
        """JSON辞書を読み込む"""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.word_dict = json.load(f)
        
        print(f"辞書読み込み完了: {len(self.word_dict)}個の8キーパターン")
        
        # 統計情報
        total_words = sum(len(candidates) for candidates in self.word_dict.values())
        unique = sum(1 for candidates in self.word_dict.values() if len(candidates) == 1)
        collision = len(self.word_dict) - unique
        
        print(f"  総単語数: {total_words}")
        print(f"  ユニークパターン: {unique} ({unique/len(self.word_dict)*100:.1f}%)")
        print(f"  衝突パターン: {collision} ({collision/len(self.word_dict)*100:.1f}%)")
    
    def decode(self, eight_key_input, top_n=10):
        """
        8キー入力から元のテキストを推定（頻度順、大文字小文字は統合済み）
        
        Args:
            eight_key_input: 8キー入力文字列（例: "jdlll"）
            top_n: 返す候補の最大数
            
        Returns:
            list: 候補のリスト（頻度の高い順、大文字小文字は統合済み）
        """
        if eight_key_input in self.word_dict:
            candidates = self.word_dict[eight_key_input][:top_n]
            return [c['word'] for c in candidates]
        else:
            return []
    
    def decode_text(self, eight_key_text, separator=' '):
        """
        スペース区切りの8キー入力テキストをデコード
        
        Args:
            eight_key_text: 8キー入力テキスト（例: "jdlll sdjlll"）
            separator: 単語の区切り文字
            
        Returns:
            str: 復元されたテキスト
        """
        words = eight_key_text.split(separator)
        decoded_words = []
        
        for word in words:
            candidates = self.decode(word, top_n=1)
            if candidates:
                decoded_words.append(candidates[0])
            else:
                decoded_words.append(f"[?{word}?]")  # 復元できなかった場合
        
        return separator.join(decoded_words)


def main():
    if len(sys.argv) < 2:
        print("Usage: python 8key_decoder.py <dictionary.json> [8key_input]")
        print("例: python 8key_decoder.py common_words_1000.json jdlll")
        return
    
    dictionary_file = sys.argv[1]
    
    # デコーダーを初期化
    decoder = EightKeyDecoder()
    decoder.load_dictionary(dictionary_file)
    
    if len(sys.argv) >= 3:
        # コマンドライン引数から入力
        eight_key_input = sys.argv[2]
        candidates = decoder.decode(eight_key_input, top_n=10)
        print(f"\n8キー入力: {eight_key_input}")
        print(f"候補:")
        for i, candidate in enumerate(candidates, 1):
            print(f"  {i}. {candidate}")
    else:
        # インタラクティブモード
        print("\n8キーデコーダー（インタラクティブモード）")
        print("8キー入力を入力してください（終了: quit）\n")
        
        while True:
            try:
                user_input = input("8キー入力> ").strip()
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                if not user_input:
                    continue
                
                candidates = decoder.decode(user_input, top_n=10)
                if candidates:
                    print("候補:")
                    for i, candidate in enumerate(candidates, 1):
                        print(f"  {i}. {candidate}")
                else:
                    print("  (候補が見つかりませんでした)")
                print()
                
            except KeyboardInterrupt:
                print("\n終了します")
                break
            except EOFError:
                break


if __name__ == '__main__':
    main()
