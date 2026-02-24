---
shallow_toc: 4
---
API reference for `diameter.message.commands.reset`.

This module contains Reset Request and Answer messages for the S6a/S6d and 
S7a/S7d interfaces, implementing AVPs documented in 3GPP TS 29.272.

!!! Note
    The `Reset` command used to be defined in both ProSe function (TS 29.344),
    as command code 8388667, and in S6a/S67 (TS 29.272), as command code 322
    and name `3GPP-Reset`. Later versions of the standards have since dropped
    the ProSe-specific command code and has replaced it with the S6a/S67-specific
    command code 322.

    The old command code 8388667 maps currently to
    [`ProSeReset`][diameter.message.commands.ProSeReset], which is left as an
    undefined placeholder.

::: diameter.message.commands.reset.Reset
    options:
      show_root_heading: true
      show_root_full_path: false
      show_submodules: false


::: diameter.message.commands.reset.ResetAnswer
    options:
      show_root_heading: true
      show_root_full_path: false
      show_submodules: false
      show_if_no_docstring: true
      filters:
        - "!^_"
        - "!^avp_def"


::: diameter.message.commands.reset.ResetRequest
    options:
      show_root_heading: true
      show_root_full_path: false
      show_submodules: false
      show_if_no_docstring: true
      filters:
        - "!^_"
        - "!^avp_def"