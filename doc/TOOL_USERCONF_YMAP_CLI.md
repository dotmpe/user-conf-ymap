---
title: User-Conf ymap UI
status: draft
---

`uc-ymap` is the default command name for the CLI entrypoint.

UC_YMAP_OBJ_FILTER="yq -r '{}'"

## Commands

**merge** `[opts] <ymap> [maps...]`
  Produce JSON object(s) for selected or all config maps

  --profile
    Default 'settings', allows use of -D/-M. No other values at this time.
    The input 'UC_YMAP_PROFILE' can configure this via env instead
    ```
       UC_YMAP_PROFILE=settings,path.defs,path.maps
    ```

  -D, --definitions <dotpath>
  -M, --maps <dotpath>
    Look for definitions and maps at specified location.
    Default is literal, top-level object key.
