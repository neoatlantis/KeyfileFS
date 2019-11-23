KeyfileFS
=========

KeyfileFS is a weird FUSE filesystem. It generates deterministic keyfiles for
TrueCrypt/VeraCrypt, KeepassX or any such crypto applications. All you need is
to load this program with some credentials(passwords, a main keyfile, or
special smartcards), telling it where to find the salts(currently only from a
directory structure), and that's it!

## Why do I need this?

It's painful to remember where a keyfile is. If that single file is lost,
there's more hurt. And since keyfiles are better to be random, how can one
manage a number of them?

You might also want to utilize various innovative methods as building blocks
for a encrypted storage. What about a simple cloud service that returns you a
secret when correct password is given, but destroys the secret once the
password goes wrong? You can easily incorporate that volatility in all your
encryption infrastructures by making a keyfile system upon it.

## Usage

### Command-line

Call `python3 -m keyfilefs` to invoke this program. This is an example of
setting up KeyfileFS using a master keyfile and a directory. The directory is
used to supply "salts" based on filenames it hosted, which serve nothing more
than parameters for deriving different keyfiles. By choosing a directory
containing e.g. .kdbx password databases, you can ask KeyfileFS to derive
different keyfiles for different databases without remembering anything more.

### Use as a library

```python
from keyfilefs.fs import KeyfileFSOperations, mountKeyfileFS

keyfileFS = KeyfileFSOperations()
mountpoint = "/tmp/test"

keyfileFS.setSaltsFromDirectory(...)

keyfileFS.setSecret(...)
# or
# keyfileFS.setKeyfile(...)

keyfileFS.setRelease(True)

mountKeyfileFS(keyfileFS, mountpoint)
```

You can use `KeyfileFS` to wire your own system. Just ensure to set
deterministic secrets and salts for a same use case. `setRelease` call is used
to grant read permissions on keyfiles, which are by default not set right after
initialization. Write permissions, however, are currently not implemented and
will be restricted in the future also only to some config parameters, if any,
in `/(path to keyfilefs mountpoint)/config/*` files.
