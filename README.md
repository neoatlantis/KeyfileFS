KeyfileFS
=========

KeyfileFS is a weird FUSE filesystem. It generates deterministic keyfiles
for TrueCrypt/VeraCrypt, KeepassX or any such crypto applications. All you
need is to load this program with some credentials(passwords, a main keyfile,
or special smartcards), telling it where to save the salts(as a single .csv
file), and that's it!

## Why do I need this?

It's painful to remember where a keyfile is. And if that single file is lost,
there's more hurt. And since keyfiles are better to be random, how can one
manage a number of them?

You might also want to utilize various innovative methods as building blocks
for a encrypted storage. What about a simple cloud service that returns you a
secret when correct password is given, but destroys the secret once the
password goes wrong? You can easily incorporate that volatility in all your
encryption infrastructures by making a keyfile system upon it.
