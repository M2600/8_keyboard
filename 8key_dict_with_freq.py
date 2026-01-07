#!/usr/bin/env python3
"""
頻度情報付き8キー辞書生成スクリプト
既存の8key TSVファイルと頻度マッピングを結合してJSON形式で出力
"""

import json
import sys
from collections import defaultdict


def load_frequency_mapping(freq_json):
    """頻度マッピングJSONを読み込む"""
    with open(freq_json, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_8key_dict_with_freq(tsv_file, freq_map, output_json, default_freq=1):
    """
    8key TSVファイルと頻度マッピングを結合してJSON辞書を作成
    
    Args:
        tsv_file: 8key TSVファイル (例: common_words_1000_8key.tsv)
        freq_map: 単語→頻度の辞書
        output_json: 出力JSONファイル
        default_freq: 頻度が見つからない場合のデフォルト値
    
    出力形式:
    {
      "8key_pattern": [
        {"word": "word1", "freq": 12345},
        {"word": "word2", "freq": 6789}
      ]
    }
    """
    eight_key_dict = defaultdict(list)
    total_words = 0
    words_with_freq = 0
    
    print(f"読み込み中: {tsv_file}")
    
    # 大文字小文字をマージするための一時辞書
    word_tracker = {}  # (eight_key, word_lower) -> {"word": original, "freq": max_freq}
    
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t')
            if len(parts) == 2:
                eight_key, original_word = parts
                original_word_lower = original_word.lower()
                
                # 頻度を取得
                freq = freq_map.get(original_word_lower, default_freq)
                
                # 大文字小文字をマージ（より頻度の高い方、または小文字を優先）
                key = (eight_key, original_word_lower)
                if key not in word_tracker:
                    word_tracker[key] = {
                        "word": original_word,
                        "freq": freq
                    }
                    total_words += 1
                else:
                    # 既存のエントリと比較
                    existing = word_tracker[key]
                    if freq > existing["freq"]:
                        # より高い頻度の形式を採用
                        word_tracker[key] = {
                            "word": original_word,
                            "freq": freq
                        }
                    elif freq == existing["freq"] and original_word.islower():
                        # 同じ頻度なら小文字を優先
                        word_tracker[key]["word"] = original_word
                
                if freq > 0:
                    words_with_freq += 1
    
    # word_trackerから eight_key_dictに変換
    for (eight_key, _), word_data in word_tracker.items():
        eight_key_dict[eight_key].append(word_data)
    
    # 各8keyパターンの候補を頻度順にソート（降順）
    for eight_key in eight_key_dict:
        eight_key_dict[eight_key].sort(key=lambda x: x['freq'], reverse=True)
    
    print(f"処理完了: {total_words} 単語")
    print(f"頻度情報あり: {words_with_freq} 単語 ({words_with_freq/total_words*100:.1f}%)")
    
    # 衝突統計
    unique_patterns = 0
    collision_patterns = 0
    max_collision = 0
    max_collision_pattern = None
    
    for eight_key, candidates in eight_key_dict.items():
        if len(candidates) == 1:
            unique_patterns += 1
        else:
            collision_patterns += 1
            if len(candidates) > max_collision:
                max_collision = len(candidates)
                max_collision_pattern = eight_key
    
    total_patterns = unique_patterns + collision_patterns
    print(f"\n衝突統計:")
    print(f"  ユニークパターン: {unique_patterns} ({unique_patterns/total_patterns*100:.1f}%)")
    print(f"  衝突パターン: {collision_patterns} ({collision_patterns/total_patterns*100:.1f}%)")
    print(f"  最大衝突数: {max_collision} (パターン: {max_collision_pattern})")
    
    if max_collision_pattern:
        print(f"  最大衝突の候補: {[c['word'] for c in eight_key_dict[max_collision_pattern]]}")
    
    # JSON形式で保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(eight_key_dict, f, ensure_ascii=False, indent=2)
    
    print(f"\n保存完了: {output_json}")
    
    return eight_key_dict


def main():
    if len(sys.argv) < 3:
        print("Usage: python 8key_dict_with_freq.py <8key.tsv> <freq_mapping.json> [output.json]")
        print("例: python 8key_dict_with_freq.py common_words_1000_8key.tsv freq_mapping.json common_words_1000.json")
        return
    
    tsv_file = sys.argv[1]
    freq_json = sys.argv[2]
    output_json = sys.argv[3] if len(sys.argv) >= 4 else tsv_file.replace('_8key.tsv', '.json')
    
    print("=" * 60)
    print("頻度情報付き8キー辞書生成")
    print("=" * 60)
    
    # 頻度マッピングを読み込み
    freq_map = load_frequency_mapping(freq_json)
    print(f"頻度マッピング読み込み: {len(freq_map)} 単語\n")
    
    # 8キー辞書を作成
    create_8key_dict_with_freq(tsv_file, freq_map, output_json)


if __name__ == '__main__':
    main()
