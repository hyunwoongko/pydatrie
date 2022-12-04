import time

import pandas as pd

from pydatrie import DoubleArrayTrie

if __name__ == "__main__":
    data_frame = pd.read_csv("data.csv")
    data_dict = {o["word"]: o for o in data_frame.to_dict("index").values()}
    data_trie = DoubleArrayTrie(data_dict)
    target_word = "가"

    dict_start = time.time()
    out_dict = [word for word in data_dict if word.startswith(target_word)]
    dict_elapse = time.time() - dict_start

    trie_start = time.time()
    out_trie = data_trie.keys(target_word)
    trie_elapse = time.time() - trie_start

    out_dict = sorted(out_dict)
    out_trie = sorted(out_trie)
    assert out_dict == out_trie

    print(f"dict elapse: {dict_elapse}")
    print(f"trie elapse: {trie_elapse}")
    print(f"pydatrie is {round(dict_elapse / trie_elapse, 5)} times faster than python dict.")
