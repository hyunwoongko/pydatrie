from datrie._datrie_impl import DoubleArrayTrie

if __name__ == "__main__":
    trie = DoubleArrayTrie(
        {
            "아버지": "NNG",
            "가": "JKS",
            "방": "NNG",
            "에": "JKB",
            "들어오": "VV",
            "신다": "EP+EF",
            ".": "SP",
        }
    )

    print(trie["아버지"])  # NNG
    print(trie["신다"])  # EP+EF

    filename = "file.dat"
    trie.save(filename)

    trie2 = DoubleArrayTrie.load(filename)
    print(trie2["아버지"])  # NNG
    print(trie2["신다"])  # EP+EF
