# git-remote-postgresql

example usage:

```
mkdir -p ~/.local/bin
cp git-remote-postgresql ~/.local/bin/
chmod +x ~/.local/bin/git-remote-postgresql
PATH=$PATH:~/.local/bin

git clone postgresql://127.0.0.1:5432/the_db
```

# TODO

* no pushing possible yet
  (not really shure if it would be a good idea to be able to)
* author of code changes cannot be detected
  * maybe there is a way by parsing comments in code?
  * maybe commit message would be possible, too?
  * still would be a problem if multiple authors change code
