from typing import List, Any, Dict, Set


class _Node:
    code: int = None
    depth: int = None
    left: int = None
    right: int = None

    def __str__(self):
        return f"Node(code={self.code}, depth={self.depth}, left={self.left}, right={self.right})"

    def __repr__(self):
        return self.__str__()


class DoubleArrayTrie:
    _unit_size: int = 8
    _check: List[int]
    _base: List[int]
    _codes: List[Set[int]]
    _used: List[bool]

    _size: int
    _alloc_size: int
    _key: List[str]
    _key_size: int
    _value: List[int]
    _progress: int
    _next_check_pos: int
    _error: int

    def __init__(self, data: Dict[str, Any]):
        self._check = None
        self._base = None
        self._used = None
        self._size = 0
        self._alloc_size = 0
        self._error = 0

        if data is not None and isinstance(data, dict):
            if len(data) > 0:
                self._build(data)
        else:
            raise ValueError("constructor param `data` is not a dictionary.")

        del self._used

    def _build(self, dictionary: Dict[str, Any]) -> int:
        dictionary = dict(sorted(dictionary.items(), key=lambda x: x[0]))
        self._value: List[Any] = list(dictionary.values())
        self._key: List[str] = list(dictionary.keys())
        self._key_size = len(self._key)
        self._progress = 0

        self._resize(65536 * 32)
        self._base[0] = 1
        self._next_check_pos = 0

        root_node = _Node()
        root_node.left = 0
        root_node.right = self._key_size
        root_node.depth = 0

        siblings: List[_Node] = []
        self._fetch(root_node, siblings)
        self._insert(siblings)
        self._codes = self._make_code_list()
        return self._error

    def _resize(self, new_size: int) -> int:
        new_base: List[int] = [0] * new_size
        new_check: List[int] = [0] * new_size
        new_used: List[bool] = [False] * new_size

        if self._alloc_size > 0:
            new_base[: self._alloc_size] = self._base[: self._alloc_size]
            new_check[: self._alloc_size] = self._check[: self._alloc_size]
            new_used[: self._alloc_size] = self._used[: self._alloc_size]

        self._base = new_base
        self._check = new_check
        self._used = new_used
        self._alloc_size = new_size
        return self._alloc_size

    def _fetch(self, parent: _Node, siblings: List[_Node]) -> int:
        if self._error < 0:
            return 0

        prev = 0
        for i in range(parent.left, parent.right):
            if len(self._key[i]) < parent.depth:
                continue

            tmp: str = self._key[i]
            cur: int = 0

            if len(tmp) != parent.depth:
                cur = ord(tmp[parent.depth]) + 1

            if prev > cur:
                self._error = -3
                return 0

            if cur != prev or len(siblings) == 0:
                tmp_node = _Node()
                tmp_node.depth = parent.depth + 1
                tmp_node.code = cur
                tmp_node.left = i

                if len(siblings) != 0:
                    siblings[len(siblings) - 1].right = i

                siblings.append(tmp_node)

            prev = cur

        if len(siblings) != 0:
            siblings[len(siblings) - 1].right = parent.right

        return len(siblings)

    def _insert(self, siblings: List[_Node]) -> int:
        if self._error < 0:
            return 0

        begin: int = 0
        pos = max(siblings[0].code + 1, self._next_check_pos) - 1
        nonzero_num = 0
        first = 0

        if self._alloc_size <= pos:
            self._resize(pos + 1)

        while True:
            pos += 1

            if self._alloc_size <= pos:
                self._resize(pos + 1)

            if self._check[pos] not in [0, None]:
                nonzero_num += 1
                continue

            elif first == 0:
                self._next_check_pos = pos
                first = 1

            begin = pos - siblings[0].code
            if self._alloc_size <= (begin + siblings[len(siblings) - 1].code):
                l: float = (
                    1.05
                    if (1.05 > 1.0 * self._key_size / (self._progress + 1))
                    else 1.0 * self._key_size / (self._progress + 1)
                )
                self._resize(int(self._alloc_size * l))

            if self._used[begin]:
                continue

            outer_continue = False
            for i in range(1, len(siblings)):
                if self._check[begin + siblings[i].code] != 0:
                    outer_continue = True
                    break
            if outer_continue:
                continue

            break

        if 1.0 * nonzero_num / (pos - self._next_check_pos + 1) >= 0.95:
            self._next_check_pos = pos

        self._used[begin] = True
        self._size = (
            self._size
            if self._size > begin + siblings[len(siblings) - 1].code + 1
            else begin + siblings[len(siblings) - 1].code + 1
        )

        for i in range(len(siblings)):
            self._check[begin + siblings[i].code] = begin

        for i in range(len(siblings)):
            new_siblings: List[_Node] = []
            if self._fetch(siblings[i], new_siblings) == 0:
                self._base[begin + siblings[i].code] = -siblings[i].left - 1
                self._progress += 1
            else:
                h: int = self._insert(new_siblings)
                self._base[begin + siblings[i].code] = h
        return begin

    def _make_code_list(self):
        codes = [set() for _ in range(len(self._check))]
        for i, c in enumerate(self._check):
            if c > 0:
                codes[c].add(i)
        return codes

    def _exact_match_search(
        self, key: str, pos: int = 0, _len: int = 0, node_pos: int = 0
    ):
        if _len <= 0:
            _len = len(key)

        if node_pos <= 0:
            node_pos = 0

        result: int = -1
        b: int = self._base[node_pos]
        p: int

        for i in range(pos, _len):
            p = b + ord(key[i]) + 1
            if b == self._check[p]:
                b = self._base[p]
            else:
                return result

        p = b
        n = self._base[p]
        if b == self._check[p] and n < 0:
            result = -n - 1
        return result

    def _prefixes(
        self,
        key: str,
        pos: int = 0,
        _len: int = 0,
        node_pos: int = 0,
    ):
        if _len <= 0:
            _len = len(key)

        if node_pos <= 0:
            node_pos = 0

        result: List = []
        b: int = self._base[node_pos]
        n: int
        p: int

        for i in range(pos, _len):
            p = b
            n = self._base[p]
            if b == self._check[p] and n < 0:
                result.append((key[:i], self._value[-n - 1]))

            p = b + ord(key[i]) + 1
            if b == self._check[p]:
                b = self._base[p]
            else:
                return result

        p = b
        n = self._base[p]
        if b == self._check[p] and n < 0:
            result.append((key, self._value[-n - 1]))

        return result

    def _search_recursive(self, node, outputs, with_value=False):
        transitions = set()
        p = node["b"] + ord(node["key"][-1]) + 1
        if node["b"] == self._check[p]:
            new_b = self._base[p]
            for idx in self._codes[new_b]:
                char_idx = idx - new_b - 1
                if char_idx >= 0:
                    transitions.add((new_b, chr(char_idx)))
                else:
                    transitions.add((new_b, ""))

        for transition in transitions:
            new_b, found_char = transition
            new_key = node["key"] + found_char
            if found_char != "":
                self._search_recursive(
                    {"b": new_b, "key": new_key}, outputs, with_value
                )
            else:
                if with_value:
                    p = new_b
                    n = self._base[p]
                    if new_b == self._check[p] and n < 0:
                        outputs.append((node["key"], self._value[-n - 1]))
                else:
                    outputs.append(node["key"])

    def _search(self, prefix: str, with_value: bool = False):
        len_key = len(prefix)
        b = self._base[0]

        for i in range(len_key - 1):
            p = b + ord(prefix[i]) + 1
            if b == self._check[p]:
                b = self._base[p]

        inputs = [{"b": b, "key": prefix}]
        outputs = []
        self._search_recursive(inputs[0], outputs, with_value)
        return list(reversed(outputs))

    def _has_keys_with_prefix(
        self,
        key: str,
        pos: int = 0,
        _len: int = 0,
        node_pos: int = 0,
    ):
        if _len <= 0:
            _len = len(key)

        if node_pos <= 0:
            node_pos = 0

        b: int = self._base[node_pos]
        p: int

        for i in range(pos, _len):
            p = b + ord(key[i]) + 1
            if b == self._check[p]:
                b = self._base[p]
                if i == _len - 1:
                    return True

        return False

    def get(self, key: str):
        idx = self._exact_match_search(key)
        if idx >= 0:
            return self._value[idx]
        return None

    def modify_value(self, key: str, val: str):
        index = self._exact_match_search(key)
        if index >= 0:
            self._value[index] = val
            return True
        return False

    def prefixes(self, key: str = None):
        if key is None or len(key) == 0:
            return self._key
        return [idx[0] for idx in self._prefixes(key)]

    def prefix_items(self, key: str = None):
        if key is None or len(key) == 0:
            return list(zip(self._key, self._value))
        return self._prefixes(key)

    def longest_prefix(self, key: str = None):
        prefixes = self.prefixes(key)
        if len(prefixes) != 0:
            return max(prefixes, key=len)
        else:
            return None

    def longest_prefix_item(self, key: str = None):
        prefixes = self.prefix_items(key)
        if len(prefixes) != 0:
            return max(prefixes, key=lambda x: len(x[0]))
        else:
            return None

    def shortest_prefix(self, key: str = None):
        prefixes = self.prefixes(key)
        if len(prefixes) != 0:
            return min(prefixes, key=len)
        else:
            return None

    def shortest_prefix_item(self, key: str = None):
        prefixes = self.prefix_items(key)
        if len(prefixes) != 0:
            return min(prefixes, key=lambda x: len(x[0]))
        else:
            return None

    def has_prefix(self, key: str):
        return len(self.prefixes(key)) != 0

    def has_keys_with_prefix(self, prefix: str):
        return self._has_keys_with_prefix(prefix)

    def keys(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return self._key
        return self._search(prefix, with_value=False)

    def values(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return self._value
        return [v for k, v in self._search(prefix, with_value=True)]

    def items(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return list(zip(self._key, self._value))
        return self._search(prefix, with_value=True)

    def suffixes(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return self._key
        suffixes = []
        for key in self._search(prefix, with_value=False):
            suffix = key[len(prefix): ]
            if len(suffix) != 0:
                suffixes.append(suffix)
        return suffixes

    def save(self, filename: str):
        import pickle

        with open(filename, mode="wb") as fp:
            pickle.dump(self.__dict__, fp)

    @classmethod
    def load(cls, filename: str) -> "DoubleArrayTrie":
        import pickle

        with open(filename, mode="rb") as fp:
            data = pickle.load(fp)

        obj = DoubleArrayTrie({})
        for key, val in data.items():
            setattr(obj, key, val)

        return obj

    def __contains__(self, item):
        return True if self.get(item) is not None else False

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __str__(self):
        return (
            f"DoubleArrayTrie("
            f"size={self._key_size}, "
            f"keys={str(self.keys()[:3])[:-1]}{', ...]' if len(self.keys()) > 3 else ']'}), "
            f"values={str(self.values()[:3])[:-1]}{', ...]' if len(self.values()) > 3 else ']'})"
        )

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        return self.keys().__iter__()

    def __next__(self):
        return self.keys().__iter__().__next__()

    def __len__(self):
        return self._key_size

    def __eq__(self, other):
        if isinstance(other, DoubleArrayTrie):
            if other.__dict__ == self.__dict__:
                return True
        return False
