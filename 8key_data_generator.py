# 8key_data_generator.py
"""
英単語・英文・日本語文から8キー入力ペアを生成するスクリプト
- 日本語はpykakasiでローマ字に変換してから8キー変換
- 日本語入力の複数のバリエーション（shougi/syougi等）に対応
- 入力: 1行ごとに単語または文が書かれたテキストファイル
- 出力: タブ区切りで [8キー入力]\t[元の単語/文] のペア
"""

import re
import itertools

# pykakasi をインポート
try:
    from pykakasi import kakasi
    kks = kakasi()
    HAS_PYKAKASI = True
except ImportError:
    print("警告: pykakasiがインストールされていません。日本語文は処理できません。")
    print("インストール: pip install pykakasi")
    HAS_PYKAKASI = False
    kks = None

# 指ごとのqwertyキー割り当て
FINGER_TO_KEYS = [
    set('qaz'),    # 左小指
    set('wsx'),    # 左薬指
    set('edc'),    # 左中指
    set('rfvtgb'), # 左人差指
    set('yhnujm'), # 右人差指
    set('ik,'),    # 右中指
    set('ol.'),    # 右薬指
    set('p;:/\'"?'),   # 右小指
]
# 8キーのラベル（a〜; など自由に変更可）
FINGER_LABELS = ['a','s','d','f','j','k','l',';']

# 文字→指ラベルの逆引き辞書
KEY_TO_FINGER = {}
for i, keys in enumerate(FINGER_TO_KEYS):
    for k in keys:
        KEY_TO_FINGER[k] = FINGER_LABELS[i]
        KEY_TO_FINGER[k.upper()] = FINGER_LABELS[i]

def is_japanese(text):
    """テキストに日本語文字（ひらがな、カタカナ、漢字）が含まれているか判定"""
    return bool(re.search(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', text))

def generate_romaji_variations(romaji):
    """
    ローマ字入力のバリエーションを生成
    日本語入力では複数の入力パターンがある
    例: shougi → shougi, syougi
        datte → datte (促音は入力時に自動変換されるので1パターン)
    """
    # 変換可能なパターンと置換候補
    patterns = [
        ('sha', ['sha', 'sya']),
        ('shi', ['shi', 'si']),
        ('shu', ['shu', 'syu']),
        ('sho', ['sho', 'syo']),
        ('cha', ['cha', 'tya', 'cya']),
        ('chi', ['chi', 'ti']),
        ('chu', ['chu', 'tyu', 'cyu']),
        ('cho', ['cho', 'tyo', 'cyo']),
        ('ja', ['ja', 'jya', 'zya']),
        ('ji', ['ji', 'zi']),
        ('ju', ['ju', 'jyu', 'zyu']),
        ('jo', ['jo', 'jyo', 'zyo']),
        ('fu', ['fu', 'hu']),
        ('tsu', ['tsu', 'tu']),
    ]
    
    # 文字列中のすべてのパターンを見つける
    variations_choices = []
    pos = 0
    result_parts = []
    
    while pos < len(romaji):
        matched = False
        # 長いパターンから試す（shaの前にshiをチェックしないように）
        for pattern, choices in sorted(patterns, key=lambda x: -len(x[0])):
            if romaji[pos:pos+len(pattern)] == pattern:
                variations_choices.append(choices)
                result_parts.append((pos, len(pattern), choices))
                pos += len(pattern)
                matched = True
                break
        
        if not matched:
            # パターンにマッチしない文字はそのまま
            result_parts.append((pos, 1, [romaji[pos]]))
            variations_choices.append([romaji[pos]])
            pos += 1
    
    # すべての組み合わせを生成（最大50パターンまで制限してメモリ節約）
    # ジェネレータを使用してメモリ効率を向上
    combinations_gen = itertools.product(*variations_choices)
    all_combinations = list(itertools.islice(combinations_gen, 50))
    
    variations = [''.join(combo) for combo in all_combinations]
    
    # 重複を削除してユニークなバリエーションのみ返す
    return list(set(variations))

def japanese_to_romaji(text):
    """日本語テキストをローマ字に変換（複数バリエーション）"""
    if not HAS_PYKAKASI:
        return [text]
    
    result = kks.convert(text)
    romaji_text = ''.join([item['hepburn'] for item in result])
    
    # 複数のバリエーションを生成
    variations = generate_romaji_variations(romaji_text)
    return variations

def to_8key(text):
    """元のテキストを8キー入力に変換"""
    return ''.join(KEY_TO_FINGER.get(c, c) for c in text)

def process_text(text):
    """
    テキストを処理して8キー入力に変換
    日本語の場合はローマ字のバリエーションを生成してから8キー変換
    
    Returns:
        list: 8キー変換されたテキストのリスト（英語は1つ、日本語は複数バリエーション）
    """
    if is_japanese(text):
        # 日本語の場合は複数のローマ字バリエーションを生成
        romaji_list = japanese_to_romaji(text)
        return [to_8key(romaji) for romaji in romaji_list]
    else:
        # 英語の場合はそのまま8キー変換（リストで返す）
        return [to_8key(text)]

def main():
    import sys
    if len(sys.argv) < 3:
        print('Usage: python 8key_data_generator.py input.txt output.tsv')
        return
    infile, outfile = sys.argv[1], sys.argv[2]
    
    count = 0
    jpn_count = 0
    eng_count = 0
    total_output_lines = 0
    
    # メモリ使用量を削減するため、バッファサイズを制限して開く
    with open(infile, encoding='utf-8') as fin, \
         open(outfile, 'w', encoding='utf-8', buffering=8192) as fout:
        for line in fin:
            line = line.strip()
            if not line: 
                continue
            
            # 日本語か英語かを判定
            is_jpn = is_japanese(line)
            if is_jpn:
                jpn_count += 1
            else:
                eng_count += 1
            
            # 8キー変換（日本語の場合は複数バリエーション）
            converted_list = process_text(line)
            
            # 8キー変換後に重複を削除（メモリ効率的な方法）
            seen = {}
            unique_converted = []
            for conv in converted_list:
                if conv not in seen:
                    seen[conv] = True
                    unique_converted.append(conv)
            
            # すべてのユニークなバリエーションを出力
            for converted in unique_converted:
                fout.write(f'{converted}\t{line}\n')
                total_output_lines += 1
            
            count += 1
            # より頻繁にフラッシュしてメモリを解放
            if count % 10000 == 0:
                fout.flush()
            if count % 100000 == 0:
                print(f'処理中... {count:,}行 (jpn: {jpn_count:,}, eng: {eng_count:,}, 出力: {total_output_lines:,}行)')
    
    print(f'完了！')
    print(f'入力: {count:,}行 (日本語: {jpn_count:,}, 英語: {eng_count:,})')
    print(f'出力: {total_output_lines:,}行 (バリエーション含む)')

if __name__ == '__main__':
    main()

