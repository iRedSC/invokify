# Welcome to Invokify

Invokify is a lightweight library that allows you to run functions from a string or list of values.


---

## Installing
Invokify is published on PyPI so you can easily install it with either `pip` or `poetry`.
```shell
pip install invokify
```
```shell
poetry add invokify
```
---
## Getting started

Let's create a simple command-line command.

We can start by importing the `InvokeEngine` from invokify:

```py
from invokify import InvokeEngine
```
Now we need to create an engine to hold our commands:
```py
engine = InvokeEngine()
```
Once we have our engine set up, all we need to do is decorate our target function using the engine's `command` method:
```py
@engine.command
def greet(user: str):
    print(f"Hello {user}!")
```
Congrats, that's all you need to do to create a command! Our next goal will be to parse our command by feeding our engine's `parse` method a list of values.
```py
cmd, args, callstack = engine.parse(["greet", "Jeff"])
```
The `parse` method will return a tuple containing three values:

1. The command if one was found. If no command was found, it will return `None` 
2. Any remaining arguments that were passed. The `parse` method will recursively look for subcommands until it cannot find any, and the remaining arguments will be passed back.
3. The callstack. A list of the commands and subcommands that were passed in.

Once you have your command, you can execute it easily just by calling it. If your command accept arguments, you can pass `args` to it.

```py
cmd(*args)
```
Output:
```
Hello Jeff!
```
---
To actually run commands on the command line, we can just set up a simple input loop.
Invokify has a simple built-in parser called `string_to_args()` that can turn a string into a list of arguments, keeping things like strings and lists intact, and converting numbers automatically.

```py
while True:
    user = input()

    cleaned = string_to_args(user)

    cmd, args, cs = engine.parse(cleaned)

    if cmd:
        cmd(*args)
    else:
        print("No command was found.")
```