---
title: User-Conf ymap UI
status: draft
---

`uc-ymap` is the default command name for the CLI entrypoint.

`UC_YMAP_OBJ_FILTER` configures the `yq` object resolver. The default command is `yq -r "${1}" "${2}"`. The selector and the source path are the two arguments after `--`.

## Commands

**merge** `[opts] <ymap> [maps...]`
: Produce JSON object(s) for selected or all config maps.

A profile is a named pipeline: an object resolver, an expander, a JSON store backend, and the selectors for definitions and maps. The merge command receives that pipeline already built.

Field by field, the first source that sets a value wins:

1. Explicit flags below.
2. `UC_YMAP_PROFILE=name[,defines[,maps]]`. Empty fields are unset. The store is not part of this string.
3. The document's top-level `profile` scalar, and only for the profile name.
4. The built-in `settings` profile.

The prelude reads that scalar only when the name is still unset. `-F` / `--from json` uses the stdlib JSON parser. Omitted `--from` means YAML and runs `yq -r .profile`. A missing scalar falls through to `settings`.

  --profile <name>
    Select a pipeline preset. Omitted leaves the name unset.

  -D, --defines <selector>
  -M, --maps <selector>
    Selectors for the definitions object and the maps object.
    On `settings` those default to `first(.definitions[]|select(type=="object"))` and `.maps`.

  --resolver <name>
    Object resolver. `yq` is the built-in.

  --expander <name>
    Map expander. `placeholder` is the built-in `{key|filter}` expander.
    Filters on that expander are `str`, `hex`, `bit`, and `revbit`.

  --store <name>
  --store-from <path>
    JSON store backend. `none` is the default and loads nothing.
    `json` opens one JSON document from `--store-from`. That file is the preloaded document. Merge does not read an index inside it yet, and still loads definitions and maps through the resolver.

###### vim:fenc=utf-8
