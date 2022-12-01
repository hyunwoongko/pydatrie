from sortedcontainers import SortedSet

LEAF_BASE_VALUE = -2
ROOT_CHECK_VALUE = -3
EMPTY_VALUE = -1
INITIAL_ROOT_BASE = 1


class SearchResult:
    PERFECT_MATCH = "PERFECT_MATCH"
    PREFIX = "PREFIX"
    NOT_FOUND = "NOT_FOUND"


class SearchState:
    prefix = None
    index = None
    finished_at_state = None
    result = None


class DoubleArrayTrie(object):
    def __init__(self, alphabet_length=256):
        super().__init__()
        self.alphabet_length = alphabet_length
        self.base = []
        self.check = []
        self.free_positions = SortedSet()
        self.base.append(INITIAL_ROOT_BASE)
        self.check.append(ROOT_CHECK_VALUE)

    def get_alphabet_size(self):
        return self.alphabet_length

    def get_size(self):
        return len(self.base)

    def get_base(self, position):
        return self.base[position]

    def get_check(self, position):
        return self.check[position]

    def set_base(self, position, value):
        self.base[position] = value
        if value == EMPTY_VALUE:
            self.free_positions.add(position)
        else:
            if position in self.free_positions:
                self.free_positions.remove(position)

    def set_check(self, position, value):
        self.check[position] = value
        if value == EMPTY_VALUE:
            self.free_positions.add(position)
        else:
            if position in self.free_positions:
                self.free_positions.remove(position)

    def _next_available_hop(self, for_value):
        while self.free_positions.bisect_right(for_value) >= len(self.free_positions):
            self._ensure_reachable_index(self.get_size() + 1)

        result = (
            self.free_positions[self.free_positions.bisect_right(for_value)] - for_value
        )
        assert result >= 0

        return result

    def _ensure_reachable_index(self, limit):
        while self.get_size() <= limit:
            self.base.append(EMPTY_VALUE)
            self.check.append(EMPTY_VALUE)
            self.free_positions.add(self.get_size() - 1)

    def _find_consecutive_free(self, amount: int):
        assert amount >= 0

        if not len(self.free_positions):
            return -1

        i = 1
        _from = self.free_positions[0]
        previous = _from
        consecutive = 1

        while consecutive < amount and i < len(self.free_positions):
            current = self.free_positions[i]
            if current - previous == 1:
                previous = current
                consecutive += 1
            else:
                _from = current
                previous = _from
                consecutive = 1
            i += 1

        if consecutive == amount:
            return _from
        else:
            return -1

    def _next_available_move(self, values: SortedSet):
        if len(values) == 1:
            return self._next_available_hop(values[0])

        min_value = values[0]
        max_value = values[-1]
        needed_positions = max_value - min_value + 1
        possible = self._find_consecutive_free(needed_positions)

        if possible - min_value >= 0:
            return possible - min_value

        self._ensure_reachable_index(self.get_size() + needed_positions)
        return self.get_size() - needed_positions - min_value

    def _add_to_trie(self, inputs):
        changed = False
        state = 0
        transition = 0
        i = 0

        while i < len(inputs):
            assert state >= 0
            c = inputs[i]
            state_base = self.get_base(state)

            if i > 0 and state_base == LEAF_BASE_VALUE:
                self.set_base(transition, self._next_available_hop(c))
                changed = True
            else:
                assert self.get_base(state) >= 0

            transition = self.get_base(state) + c
            assert transition > 0

            self._ensure_reachable_index(transition)
            if self.get_check(transition) == EMPTY_VALUE:
                self.set_check(transition, state)
                if i == len(inputs) - 1:
                    self.set_base(transition, LEAF_BASE_VALUE)
                    changed = True
                else:
                    self.set_base(transition, self._next_available_hop(inputs[i + 1]))
                    changed = True
            else:
                if self.get_check(transition) != state:
                    self._resolve_conflict(state, c)
                    changed = True
                    continue

            state = transition
            i += 1
        return changed

    def _resolve_conflict(self, s, new_value):
        values = SortedSet()
        values.add(new_value)

        for c in range(self.alphabet_length):
            temp_next = self.get_base(s) + c
            if 0 <= temp_next < self.get_size() and self.get_check(temp_next) == s:
                values.add(c)

        new_location = self._next_available_move(values)
        values.remove(new_value)

        for i in range(len(values)):
            c = values[i]
            temp_next = self.get_base(s) + c
            assert temp_next < self.get_size()
            assert self.get_check(temp_next) == s
            assert self.get_check(new_location + c) == EMPTY_VALUE
            self.set_check(new_location + c, s)

            assert self.get_base(new_location + c) == EMPTY_VALUE
            self.set_base(new_location + c, self.get_base(self.get_base(s) + c))
            self._update_child_move(s, c)

            if self.get_base(self.get_base(s) + c) != LEAF_BASE_VALUE:
                for d in range(self.alphabet_length):
                    temp_next_child = self.get_base(self.get_base(s) + c) + d
                    if (
                        temp_next_child < self.get_size()
                        and self.get_check(temp_next_child) == self.get_base(s) + c
                    ):
                        self.set_check(
                            self.get_base(self.get_base(s) + c) + d, new_location + c
                        )

                    elif temp_next >= self.get_size():
                        break

                self.set_base(self.get_base(s) + c, EMPTY_VALUE)
                self.set_check(self.get_base(s) + c, EMPTY_VALUE)

        self.set_base(s, new_location)

    def _is_walkable(self, state: int, c: int):
        if not (state < self.get_size()):
            return False

        transition = self._walk(state, c)
        return transition < self.get_size() and self.get_check(transition) == state

    def _walk(self, state: int, c: int):
        return self.get_base(state) + c

    def _contains_prefix(self, prefix):
        return self._run_prefix(prefix).result

    def _run_prefix(self, prefix):
        state = 0
        i = 0
        result = SearchState()
        result.prefix = prefix
        result.result = SearchResult.PREFIX

        while i < len(prefix):
            current = prefix[i]
            assert current >= 0
            assert current < self.alphabet_length
            transition = self.get_base(state) + current

            if transition < self.get_size() and self.get_check(transition) == state:
                if self.get_base(transition) == LEAF_BASE_VALUE:
                    if i == len(prefix) - 1:
                        result.result = SearchResult.PERFECT_MATCH
                        break
                    else:
                        result.result = SearchResult.NOT_FOUND
                        break
                state = transition

            else:
                result.result = SearchResult.NOT_FOUND
                break

            i += 1

        result.finishedAtState = state
        result.index = i
        return result

    def _update_child_move(self, parent_index, for_character):
        assert (
            self.get_check(self.get_base(parent_index) + for_character) == parent_index
        )

    def _remove_from_trie(self, inputs):
        if self._contains_prefix(inputs) == SearchResult.PERFECT_MATCH:
            state = 0
            delete_from_state = 0
            delete_from_index = 0

            for i in range(len(inputs)):
                c = inputs[i]
                transition = self.get_base(state) + c

                for d in range(self.alphabet_length):
                    if d == c:
                        continue
                    if (
                        transition < self.get_size()
                        and self.get_check(transition) == state
                    ):
                        delete_from_state = state
                        delete_from_index = i

                state = transition

            state = delete_from_state

            for i in range(delete_from_index, len(inputs)):
                c = inputs[i]
                transition = self.get_base(state) + c
                self.set_base(state, EMPTY_VALUE)
                self.set_base(state, EMPTY_VALUE)
                state = transition
            return True
        else:
            return False

    @staticmethod
    def _create_unicode(inputs):
        return [s for s in inputs.encode("utf-8")]

    def put(self, inputs):
        self._add_to_trie(self._create_unicode(inputs))

    def find(self, inputs):
        return self._contains_prefix(self._create_unicode(inputs))

    def remove(self, inputs):
        return self._remove_from_trie(self._create_unicode(inputs))


if __name__ == "__main__":
    datrie = DoubleArrayTrie()
    datrie.put("안녕 반가워")
    datrie.put("잘가요")
    datrie.put("햄버거 먹고싶다")

    print(f"안녕 반가워: {datrie.find('안녕 반가워')}")
    print(f"잘가: {datrie.find('잘가')}")
    print(f"햄버거: {datrie.find('햄버거')}")
    print(f"햄버거 먹고싶다: {datrie.find('햄버거 먹고싶다')}")

    datrie.remove("햄버거 먹고싶다")
    print(f"햄버거 먹고싶다: {datrie.find('햄버거 먹고싶다')}")
