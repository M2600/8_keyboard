#!/usr/bin/env python3
"""
頻度マッピング作成スクリプト
frequencyList.tsvから単語→頻度の辞書を作成してJSONで出力
"""

import json
import sys


def create_frequency_mapping(tsv_file, output_json):
    """
    TSVファイルから単語→頻度のマッピングを作成
    
    Args:
        tsv_file: frequencyList.tsvのパス
        output_json: 出力JSONファイルのパス
    """
    freq_map = {}
    
    print(f"読み込み中: {tsv_file}")
    
    with open(tsv_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line_num == 1:  # ヘッダー行をスキップ
                continue
            
            # タブで分割
            parts = line.split('\t')
            if len(parts) >= 5:
                # フォーマット: LEMMA|POS \t LEMMA \t POS \t FREQUENCY \t INFLECTIONS
                # parts[1] = LEMMA (単語)
                # parts[3] = FREQUENCY
                # parts[4] = INFLECTIONS (変化形のカンマ区切りリスト)
                try:
                    frequency = int(parts[3])
                    
                    # INFLECTIONSから全ての変化形を取得
                    inflections = parts[4].split(',')
                    
                    # 各変化形を頻度マップに追加
                    for inflection in inflections:
                        word = inflection.strip().lower()  # 小文字に統一
                        if word:  # 空文字列でない場合のみ
                            # 同じ単語が複数行にある場合は最大の頻度を使用
                            if word in freq_map:
                                freq_map[word] = max(freq_map[word], frequency)
                            else:
                                freq_map[word] = frequency
                except (ValueError, IndexError) as e:
                    # デバッグ用: 最初の10個のエラーのみ表示
                    if line_num <= 15:
                        print(f"警告: 行 {line_num} をスキップ: {e}")
                    continue
    
    print(f"マッピング作成完了: {len(freq_map)} 単語")
    
    # JSON形式で保存
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(freq_map, f, ensure_ascii=False, indent=2)
    
    print(f"保存完了: {output_json}")
    
    # 統計情報を表示
    if freq_map:
        sorted_words = sorted(freq_map.items(), key=lambda x: x[1], reverse=True)
        print(f"\n最も頻度が高い10単語:")
        for word, freq in sorted_words[:10]:
            print(f"  {word}: {freq}")
    
    return freq_map


def main():
    if len(sys.argv) < 2:
        print("Usage: python create_freq_mapping.py <frequencyList.tsv> [output.json]")
        print("例: python create_freq_mapping.py Frequency-list/frequencyList.tsv freq_mapping.json")
        return
    
    input_tsv = sys.argv[1]
    output_json = sys.argv[2] if len(sys.argv) >= 3 else "freq_mapping.json"
    
    create_frequency_mapping(input_tsv, output_json)


if __name__ == '__main__':
    main()
