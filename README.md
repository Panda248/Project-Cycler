# Project Cycler

This is a script that launches/closes a list of projects at set intervals

On Windows, each project is stopped with `taskkill /T`, using the launched
process's PID. This stops the project process and processes spawned by its
startup script when the project switches or the cycler exits.

How to run:

run
```
python main.py --delay 30
```

`--delay` sets how long each project runs before switching, in seconds.
The default is 10 seconds. Use `python main.py --help` to see all options.