# Pydatrie
Pydatire is a pure python implementation of double array trie.

## Installation
```
pip install pydatrie
```

## Usage
```python
from pydatrie import DoubleArrayTrie

# creation datrie
trie = DoubleArrayTrie(
    {
        "AB": "1",
        "ABCD": "2",
        "EF": "3",
        "EFGH": "4",
    }
)

# exact matching search using `__getitem__`
trie["AB"]  # "1"
trie["EF"]  # "3"

# exact matching search using `get`
trie.get("AB")  # "1"
trie.get("EF")  # "3"

# common prefix search using `get`
trie.get("ABCD", prefix_search=True)  # ['1', '2']
trie.get("EFGH", prefix_search=True)  # ['3', '4']

# save datrie
trie.save("file.dat")

# load datrie
trie2 = DoubleArrayTrie.load("file.dat")
trie2["AB"]  # 1
trie2["EF"]  # 3
```

## License
```
Copyright 2022 Hyunwoong Ko.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```