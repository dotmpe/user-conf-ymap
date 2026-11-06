A simple JSON loader and value renderer, using only py3 stdlib + `yq`.

- [x] DONE: merge settings according to [initial plan](doc/BRIEF.md)
- [ ] TODO: fix help; docstrings and manual [User-Conf ymap UI](doc/TOOL_USERCONF_YMAP_CLI.md)
- [ ] TODO: implement non-YAML path
- [ ] TODO: testing
- [ ] TODO: choose, set and follow project conventions
- [ ] TODO: more complex configurable object resolver and filter components

# Example
To process a merge, import `user_conf_ymap.merge` and use `run_merge(definitions, placeholders)` on dictionaries.

Or call the CLI:
```bash
uc-ymap merge example/myset.yml
````

```
{"placeholderkey": "#0x7b"}
{"otherkey": "123", "secondkey": "1", "thirdkey": "123.45"}
```

See [myset.yml](example/myset.yml) at the examples/ folder for the inputs.
