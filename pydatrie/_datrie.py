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
    UNIT_SIZE: int = 8
    check: List[int]
    base: List[int]
    codes: List[Set[int]]
    used: List[bool]

    size: int
    alloc_size: int
    key: List[str]
    key_size: int
    length: List[int]
    value: List[int]
    progress: int
    next_check_pos: int
    max_length: int
    error: int

    def __init__(self, data: Dict[str, Any] = None):
        self.check = None
        self.base = None
        self.used = None
        self.size = 0
        self.alloc_size = 0
        self.error = 0

        if data is not None:
            self._build(data)

    def _build(self, dictionary: Dict[str, Any]) -> int:
        dictionary = dict(sorted(dictionary.items(), key=lambda x: x[0]))
        self.value: List[Any] = list(dictionary.values())
        self.key: List[str] = list(dictionary.keys())
        self.key_size = len(self.key)
        self.progress = 0

        self._resize(65536 * 32)
        self.base[0] = 1
        self.next_check_pos = 0

        root_node = _Node()
        root_node.left = 0
        root_node.right = self.key_size
        root_node.depth = 0

        siblings: List[_Node] = []
        self._fetch(root_node, siblings)
        self._insert(siblings)
        self.codes = self._make_code_list()
        del self.used
        return self.error

    def _resize(self, new_size: int) -> int:
        new_base: List[int] = [0] * new_size
        new_check: List[int] = [0] * new_size
        new_used: List[bool] = [False] * new_size

        if self.alloc_size > 0:
            new_base[: self.alloc_size] = self.base[: self.alloc_size]
            new_check[: self.alloc_size] = self.check[: self.alloc_size]
            new_used[: self.alloc_size] = self.used[: self.alloc_size]

        self.base = new_base
        self.check = new_check
        self.used = new_used
        self.alloc_size = new_size
        return self.alloc_size

    def _fetch(self, parent: _Node, siblings: List[_Node]) -> int:
        if self.error < 0:
            return 0

        prev = 0
        for i in range(parent.left, parent.right):
            if len(self.key[i]) < parent.depth:
                continue

            tmp: str = self.key[i]
            cur: int = 0

            if len(tmp) != parent.depth:
                cur = ord(tmp[parent.depth]) + 1

            if prev > cur:
                self.error = -3
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
        if self.error < 0:
            return 0

        begin: int = 0
        pos = max(siblings[0].code + 1, self.next_check_pos) - 1
        nonzero_num = 0
        first = 0

        if self.alloc_size <= pos:
            self._resize(pos + 1)

        while True:
            pos += 1

            if self.alloc_size <= pos:
                self._resize(pos + 1)

            if self.check[pos] not in [0, None]:
                nonzero_num += 1
                continue

            elif first == 0:
                self.next_check_pos = pos
                first = 1

            begin = pos - siblings[0].code
            if self.alloc_size <= (begin + siblings[len(siblings) - 1].code):
                l: float = (
                    1.05
                    if (1.05 > 1.0 * self.key_size / (self.progress + 1))
                    else 1.0 * self.key_size / (self.progress + 1)
                )
                self._resize(int(self.alloc_size * l))

            if self.used[begin]:
                continue

            outer_continue = False
            for i in range(1, len(siblings)):
                if self.check[begin + siblings[i].code] != 0:
                    outer_continue = True
                    break
            if outer_continue:
                continue

            break

        if 1.0 * nonzero_num / (pos - self.next_check_pos + 1) >= 0.95:
            self.next_check_pos = pos

        self.used[begin] = True
        self.size = (
            self.size
            if self.size > begin + siblings[len(siblings) - 1].code + 1
            else begin + siblings[len(siblings) - 1].code + 1
        )

        for i in range(len(siblings)):
            self.check[begin + siblings[i].code] = begin

        for i in range(len(siblings)):
            new_siblings: List[_Node] = []
            if self._fetch(siblings[i], new_siblings) == 0:
                self.base[begin + siblings[i].code] = -siblings[i].left - 1
                self.progress += 1
            else:
                h: int = self._insert(new_siblings)
                self.base[begin + siblings[i].code] = h
        return begin

    def _make_code_list(self):
        codes = [set() for _ in range(len(self.check))]
        for i, c in enumerate(self.check):
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
        b: int = self.base[node_pos]
        p: int

        for i in range(pos, _len):
            p = b + ord(key[i]) + 1
            if b == self.check[p]:
                b = self.base[p]
            else:
                return result

        p = b
        n = self.base[p]
        if b == self.check[p] and n < 0:
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
        b: int = self.base[node_pos]
        n: int
        p: int

        for i in range(pos, _len):
            p = b
            n = self.base[p]
            if b == self.check[p] and n < 0:
                result.append((key[:i], self.value[-n - 1]))

            p = b + ord(key[i]) + 1
            if b == self.check[p]:
                b = self.base[p]
            else:
                return result

        p = b
        n = self.base[p]
        if b == self.check[p] and n < 0:
            result.append((key, self.value[-n - 1]))

        return result

    def _search_recursive(self, node, outputs, with_value=False):
        transitions = set()
        p = node["b"] + ord(node["key"][-1]) + 1
        if node["b"] == self.check[p]:
            new_b = self.base[p]
            for idx in self.codes[new_b]:
                char_idx = idx - new_b - 1
                if char_idx >= 0:
                    transitions.add((new_b, chr(char_idx)))
                else:
                    transitions.add((new_b, ""))

        for transition in transitions:
            new_b, found_char = transition
            new_key = node["key"] + found_char
            if found_char == "":
                if with_value:
                    p = new_b
                    n = self.base[p]
                    if new_b == self.check[p] and n < 0:
                        outputs.append((node["key"], self.value[-n - 1]))
                else:
                    outputs.append(node["key"])
            else:
                self._search_recursive(
                    {"b": new_b, "key": new_key}, outputs, with_value
                )

    def _search(self, key: str, with_value: bool = False):
        len_key = len(key)
        b = self.base[0]

        for i in range(len_key - 1):
            p = b + ord(key[i]) + 1
            if b == self.check[p]:
                b = self.base[p]

        inputs = [{"b": b, "key": key}]
        outputs = []
        self._search_recursive(inputs[0], outputs, with_value)
        return outputs

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

        b: int = self.base[node_pos]
        p: int

        for i in range(pos, _len):
            p = b + ord(key[i]) + 1
            if b == self.check[p]:
                b = self.base[p]
                if i == _len - 1:
                    return True

        return False

    def get(self, key: str):
        idx = self._exact_match_search(key)
        if idx >= 0:
            return self.value[idx]
        return None

    def modify_value(self, key: str, val: str):
        index = self._exact_match_search(key)
        if index >= 0:
            self.value[index] = val
            return True
        return False

    def prefixes(self, key: str):
        return [idx[0] for idx in self._prefixes(key)]

    def prefix_items(self, key: str):
        return self._prefixes(key)

    def longest_prefix(self, key: str):
        prefixes = self.prefixes(key)
        if len(prefixes) != 0:
            return max(prefixes, key=len)
        else:
            return None

    def longest_prefix_item(self, key: str):
        prefixes = self.prefix_items(key)
        if len(prefixes) != 0:
            return max(prefixes, key=lambda x: len(x[0]))
        else:
            return None

    def has_prefix(self, key: str):
        return len(self.prefixes(key)) != 0

    def has_keys_with_prefix(self, key: str):
        return self._has_keys_with_prefix(key)

    def keys(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return self.key
        return self._search(prefix, with_value=False)

    def values(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return self.value
        return [v for k, v in self._search(prefix, with_value=True)]

    def items(self, prefix: str = None):
        if prefix is None or len(prefix) == 0:
            return list(zip(self.key, self.value))
        return self._search(prefix, with_value=True)

    def suffixes(self, prefix: str):
        len_prefix = len(prefix)
        if prefix is None or len_prefix == 0:
            return self.key
        return [keys[len_prefix:] for keys in self._search(prefix, with_value=False)]

    def save(self, filename: str):
        import pickle

        with open(filename, mode="wb") as fp:
            pickle.dump(self.__dict__, fp)

    @classmethod
    def load(cls, filename: str) -> "DoubleArrayTrie":
        import pickle

        with open(filename, mode="rb") as fp:
            data = pickle.load(fp)

        obj = DoubleArrayTrie()
        for key, val in data.items():
            setattr(obj, key, val)

        return obj

    def __contains__(self, item):
        return True if self.get(item) is not None else False

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

    def __str__(self):
        return
