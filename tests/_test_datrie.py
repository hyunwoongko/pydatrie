from pydatrie._datrie import DoubleArrayTrie

if __name__ == "__main__":
    trie = DoubleArrayTrie(
        {

        },
    )

    output = trie.suffixes("한나라")
    print(output)
