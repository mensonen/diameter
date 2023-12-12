
## System requirements

The `diameter` package can be installed from PyPI:

```shell
~# pip install python-diameter
```

The minimum required Python version is 3.11, a fairly recent Linux kernel is
recommended. There is no Windows or Mac compatibility.

## SCTP

The `diameter` stack can operate in both TCP and SCTP modes. For connectivity
over the SCTP transport, an optional dependency for 
[pysctp](https://pypi.org/project/pysctp/) must be installed separately:

```shell
~# pip install pysctp
```

Note that installing the `pysctp` package requires at least an SCTP-aware kernel
and possibly additional OS packages installed prior installation. Refer to 
pysctp installation documentation for further instructions.

There is no need to make `diameter` package SCTP-aware. If pysctp is available,
it will be used automatically for any peer configured to use the SCTP 
transport protocol.