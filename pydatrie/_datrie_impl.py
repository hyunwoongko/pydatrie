from typing import List, Any, Tuple, Dict


class Node:
    code: int
    depth: int
    left: int
    right: int

    def __str__(self):
        return f"Node(code={self.code}, depth={self.depth}, left={self.left}, right={self.right})"

    def __repr__(self):
        return self.__str__()


class DoubleArrayTrie:
    UNIT_SIZE: int = 8
    check: List[int]
    base: List[int]
    used: List[bool]

    size: int
    alloc_size: int
    key: List[str]
    key_size: int
    length: List[int]
    value: List[int]
    v: Any
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
            self.build_with_dict(data)

    def build_with_keys(self, keys: List[str]) -> int:
        assert len(keys) > 0
        return self._build(keys, None, None, len(keys))

    def build_with_keys_and_values(self, keys: List[str], values: List[Any]) -> int:
        assert len(keys) == len(values)
        assert len(keys) > 0
        self.v = values
        return self._build(keys, None, None, len(keys))

    def build_with_entries(self, entries: List[Tuple[str, Any]]) -> int:
        key_list = []
        value_list = []
        for key, val in entries:
            key_list.append(key)
            value_list.append(val)
        return self.build_with_keys_and_values(key_list, value_list)

    def build_with_dict(self, dictionary: Dict[str, Any]) -> int:
        assert dictionary is not None
        entries = list(dictionary.items())
        return self.build_with_entries(entries)

    def _build(
        self, _key: List[str], _length: List[int], _value: List[int], _key_size: int
    ) -> int:
        self.key = _key
        self.length = _length
        self.key_size = _key_size
        self.value = _value
        self.progress = 0

        self._resize(65536 * 32)

        self.base[0] = 1
        self.next_check_pos = 0

        root_node = Node()
        root_node.left = 0
        root_node.right = self.key_size
        root_node.depth = 0

        siblings: List[Node] = []
        self._fetch(root_node, siblings)
        self._insert(siblings)

        self.used = None
        self.key = None
        self.length = None

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

    def _fetch(self, parent: Node, siblings: List[Node]) -> int:
        if self.error < 0:
            return 0

        prev = 0
        for i in range(parent.left, parent.right):
            if (
                self.length[i] if self.length is not None else len(self.key[i])
            ) < parent.depth:
                continue

            tmp: str = self.key[i]
            cur: int = 0

            if (
                self.length[i] if self.length is not None else len(tmp)
            ) != parent.depth:
                cur = ord(tmp[parent.depth]) + 1

            # if prev > cur:
            #     self.error = -3
            #     return 0

            if cur != prev or len(siblings) == 0:
                tmp_node = Node()
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

    def _insert(self, siblings: List[Node]) -> int:
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
            new_siblings: List[Node] = []
            if self._fetch(siblings[i], new_siblings) == 0:
                self.base[begin + siblings[i].code] = (
                    -self.value[siblings[i].left] - 1
                    if self.value is not None
                    else -siblings[i].left - 1
                )

                if (self.value is not None) and (
                    -self.value[siblings[i].left] - 1 >= 0
                ):
                    self.error = -2
                    return 0

                self.progress += 1
            else:
                h: int = self._insert(new_siblings)
                self.base[begin + siblings[i].code] = h

        return begin

    def _exact_match_search(
        self, key: str, pos: int = 0, _len: int = 0, node_pos: int = 0
    ):
        if _len <= 0:
            _len = len(key)

        if node_pos <= 0:
            node_pos = 0

        result: int = -1
        key_chars: List[str] = [c for c in key]
        b: int = self.base[node_pos]
        p: int

        for i in range(pos, _len):
            p = b + ord(key_chars[i]) + 1
            if b == self.check[p]:
                b = self.base[p]
            else:
                return result

        p = b
        n = self.base[p]
        if b == self.check[p] and n < 0:
            result = -n - 1
        return result

    def _common_prefix_search(
        self, key: str, pos: int = 0, _len: int = 0, node_pos: int = 0
    ):
        if _len <= 0:
            _len = len(key)

        if node_pos <= 0:
            node_pos = 0

        result: List[int] = []
        key_chars: List[str] = [c for c in key]
        b: int = self.base[node_pos]
        n: int
        p: int

        for i in range(pos, _len):
            p = b + ord(key_chars[i]) + 1
            if b == self.check[p]:
                b = self.base[p]
            else:
                return result

            p = b
            n = self.base[p]
            if b == self.check[p] and n < 0:
                result.append(-n - 1)

        return result

    def _get_value(self, index) -> Any:
        return self.v[index]

    def get(self, key, prefix_search=False) -> Any:
        if prefix_search:
            indices = self._common_prefix_search(key)
            results = [self._get_value(i) for i in indices if i >= 0]
            if len(results) != 0:
                return results
        else:
            index = self._exact_match_search(key)
            if index >= 0:
                return self._get_value(index)
        return None

    def __getitem__(self, item: str) -> Any:
        return self.get(item)

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
