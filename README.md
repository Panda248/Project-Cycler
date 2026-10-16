# Project Cycler

This is a script that launches/closes a list of projects at set intervals.

All projects use a `run.sh` startup script, launched through `bash` in a new
process session.

On Windows, the process tree is stopped with `taskkill /T`, using the launched
process's PID. On Linux and macOS, the session's process group is stopped with
`SIGTERM`, then `SIGKILL` if it does not exit within 10 seconds.

Projects without a `run.sh` startup file are skipped with a warning.

How to run:

run
```
python main.py --delay 30
```

`--delay` sets how long each project runs before switching, in seconds.
The default is 10 seconds. Use `python main.py --help` to see all options.