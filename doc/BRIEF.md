# Initial plan

A tool to process configuration for other projects.

Hosts with `py3` and `yq` can easily process some user definitions into JSON
and other formats. The exact structure and layering is owned externally, as
is aggregating files with definitions and mappings. The process here supports
building maps (ie. objects or dicts) from definition sets.

Sketch of a file myset.yaml with just one trivial key set and two provided maps:
```yaml
---
# The keys in the definitions are a signature for its kind, and its value can be
# overruled by a second set (from another user or project specified file). So
# these could be application defaults for a minimum or maximally customized
# config, plus maps for app defaults, or dist provided settings and maps. It
# could also be parts for a theme or profile in another organisation of
# settings, etc. The upper key 'profile' should be reserved to characterize the
# kinds of sets in the file.
definitions:
  myset:
    key: 123
    key2: true

maps:
  myconfigA:
    placeholderkey: "#{define.key|hex}"
  myconfigB:
    otherkey: "{define.key|int}"
    secondkey: "{key2|bit}"

# The external project now has two maps it can render, for use in expansion of
# configuration stanza's for example. Most maps will be one on one, and take a
# coordinated setting and format+map it into a specific configuration or program
# input.
```

This basis gives a path to map both style and application definitions into
signature sets. Outside of this project these can be used to coordinate both.

The concern for this project is understand some value types and serializing
filters. The YAML can filtered into JSON by external tools; by adding yq as
an installation dependency it does not add a direct link to ruamel (Python's
chosen but non-std YAML parser).

The pipeline can be simple for now; the UI is CLI style, the filters are
hardcoded and only the definitions and maps path are configurable.
Later extensions for other processes will use other keys and types of objects.
