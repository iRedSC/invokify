# %%

from invokify import InvokeEngine, string_to_args

# %%
engine = InvokeEngine()


@engine.command
def main():
    print("main")


@engine.command
@main.subcommand
def sub1():
    print("sub1")


@engine.command
@main.subcommand
@sub1.subcommand
def sub2():
    print("sub2")


@engine.command
def stop():
    return "STOP"


# %%
result = None
while result != "STOP":
    user = string_to_args(input())

    cmd, _, cs = engine.parse(user)

    for cmd in cs:
        result = cmd()

# %%
1
