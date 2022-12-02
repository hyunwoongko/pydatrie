from pydatrie._datrie_impl import DoubleArrayTrie

if __name__ == "__main__":
    trie = DoubleArrayTrie(
        {
            "AB": "1",
            "ABCD": "2",
            "EF": "3",
            "EFGH": "4",
        }
    )

    print(trie["AB"])  # 1
    print(trie["EF"])  # 3
    print(trie.get("ABCD", prefix_search=True))  # ['1', '2']
    print(trie.get("EFGH", prefix_search=True))  # ['3', '4']

    filename = "file.dat"
    trie.save(filename)

    trie2 = DoubleArrayTrie.load(filename)
    print(trie2["AB"])  # 1
    print(trie2["EF"])  # 3
