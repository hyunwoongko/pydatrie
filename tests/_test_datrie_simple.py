from datrie._datrie_simple import SimpleDoubleArrayTrie

if __name__ == "__main__":
    trie = SimpleDoubleArrayTrie()
    trie.put("ABC")
    trie.put("DEF")

    print(f"AB: {trie.find('AB')}")  # PARTIAL_MATCH
    print(f"ABC: {trie.find('ABC')}")  # PERFECT_MATCH
    print(f"DE: {trie.find('DE')}")  # PARTIAL_MATCH
    print(f"DEF: {trie.find('DEF')}")  # PERFECT_MATCH
    print(f"EF: {trie.find('EF')}")  # NOT_FOUND

    trie.remove("ABC")
    print(f"ABC: {trie.find('ABC')}")  # NOT_FOUND
