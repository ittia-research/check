This package connects to the ITTIA Check API.

More on this project and how to self-host one: https://github.com/ittia-research/check

## How-to
Demo on how to fact-check a text:
```python
import asyncio
from ittia_check import Check

base_url = "https://check.ittia.net"
format = "json"  # or markdown

check = Check(base_url=base_url, format=format)

query = "Germany hosted the 2024 Olympics"

result = asyncio.run(check(query))

print(result)
```
