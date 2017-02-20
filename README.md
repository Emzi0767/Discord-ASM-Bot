#Assembler Bot by Emzi0767

##ABOUT

A Discord bot built on top of [discord.py library](https://github.com/Rapptz/discord.py/). It's designed to allow quickly assembing x86, x86_64, and ARM assembly, and output resulting bytes.

ASM is built around LLVM.

##REQUIREMENTS

* Python 3.5 or newer
* PIP Packages:
   * `discord.py` 0.16.x
   * `psutil` 5.1.2
* (Recommended, Linux-only) `uvloop` 0.7.2

##SETUP

In order for bot to run, you will need to set up your environment. 

1. Create a directory for the bot.
2. Copy bot's files to the directory.
3. Copy `config.json` from `sample_configs` to bot's directory.
4. Edit `config.json` to match your configuration.

##RUNNING

Run `runasm.sh`. That's it, your bot is now running.

##REPORTING BUGS

Bugs happen, no software is perfect. If you happen to cause the software to crash or otherwise behave in an unintended manner, make sure to let me know using via [the issue tracker](https://github.com/Emzi0767/Discord-ASM-Bot/issues). If possible, include the list of steps you took that caused the problem.