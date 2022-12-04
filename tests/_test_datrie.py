from pydatrie import DoubleArrayTrie

# create trie
# the input dict type is Dict[str, Any]
trie = DoubleArrayTrie(
    {
        "AB": "1",
        "ABCD": "2",
        "EF": "3",
        "EFGH": "4",
    }
)

# exact matching search using `__getitem__`
trie["AB"]
# "1"
trie["EF"]
# "3"

# exact matching search using `get`, equivalent with `__getitem__`
trie.get("AB")
# "1"
trie.get("EF")
# "3"

# common prefix search using `prefixes`
trie.prefixes()
# ["AB", "ABCD", "EF", "EFGH"]
trie.prefixes("ABC")
# ["AB"]
trie.prefixes("ABCD")
# ["AB", "ABCD"]

# common prefix search with value using `prefix_items`
trie.prefix_items()
# [('AB', '1'), ('ABCD', '2'), ('EF', '3'), ('EFGH', '4')]
trie.prefix_items("ABC")
# [('AB', '1')]
trie.prefix_items("ABCD")
# [('AB', '1'), ('ABCD', '2')]

# longest prefix search using `longest_prefix`
trie.longest_prefix()
# ABCD
trie.longest_prefix("ABC")
# AB

# longest prefix search with value using `longest_prefix_item`
trie.longest_prefix_item()
# ('ABCD', '2')
trie.longest_prefix_item("ABC")
# ('AB', '1')

# shortest prefix search using `shortest_prefix`
trie.shortest_prefix()
# AB
trie.shortest_prefix("EFG")
# EF

# shortest prefix search with value using `shortest_prefix`
trie.shortest_prefix_item()
# ('AB', '1')
trie.shortest_prefix_item("EFG")
# ('EF', '3')

# check trie has the exact key using `__contains__`
"EF" in trie
# True
"EFG" in trie
# False

# check trie has any prefix using `has_prefix`
trie.has_prefix("EF")
# True
trie.has_prefix("EFG")
# True

# check trie has any key which starts with given prefix using `has_keys_with_prefix`
trie.has_keys_with_prefix("A")
# True
trie.has_keys_with_prefix("X")
# False

# search all the keys starts with given prefix using `keys`
trie.keys()
# ['AB', 'ABCD', 'EF', 'EFGH']
print(trie.keys("A"))
# ['AB', 'ABCD']
trie.keys("ABC")
# ['ABCD']

# search all the values matched with keys starts with given prefix using `keys`
trie.values()
# ['1', '2', '3', '4']
trie.values("A")
# ['1', '2']
trie.values("ABC")
# ['2']

# search all the keys and values matched with keys starts with given prefix using `keys`
trie.items()
# [('AB', '1'), ('ABCD', '2'), ('EF', '3'), ('EFGH', '4')]
trie.items("A")
# [('AB', '1'), ('ABCD', '2')]
trie.items("ABC")
# [('ABCD', '2')]

# common suffix search using `suffixes`
trie.suffixes()
# ['AB', 'ABCD', 'EF', 'EFGH']
trie.suffixes("A")
# ['B', 'BCD']

# check the size of trie using `__len__`
len(trie)
# 4

# save trie using `save`
trie.save("file.dat")

# load trie using `load`
trie2 = DoubleArrayTrie.load("file.dat")
trie2.items()
# [('AB', '1'), ('ABCD', '2'), ('EF', '3'), ('EFGH', '4')]
# it works same with original object!

# check sameness of two tries using `__eq__`
trie == trie2
# True

# print information of trie
print(trie)
# DoubleArrayTrie(size=4, keys=['AB', 'ABCD', 'EF', ...]), values=['1', '2', '3', ...])

# for loop using `__iter__` and `__next__`
for key in trie:
    print(key)
# AB
# ABCD
# EF
# EFGH

# modify value of given key using `modify_value`
trie.modify_value("AB", "99")
trie.items()
# [('AB', '99'), ('ABCD', '2'), ('EF', '3'), ('EFGH', '4')]
