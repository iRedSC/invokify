"""
Invokify

Allows the creation of parsible commands using decorators.
"""
__all__ = ["CommandAlreadyExists", "EngineRequired", "meta", "Command", "InvokeEngine"]

import functools
from dataclasses import dataclass, field
from typing import Union


class CommandAlreadyExists(Exception):
    """
    Will be raised when attempting to name a command/alias
    the same as one that already exists.
    """


class EngineRequired(Exception):
    """
    Will be raised when an engine was requested but not supplied.
    """


@dataclass(slots=True)
class meta:
    """Define requirements for a command, such as injecting itself into the function."""

    requires: dict[str, bool] = field(default_factory=dict)
    injections: dict[str, any] = field(default_factory=dict)
    func: callable = None
    helptext: str = ""

    @staticmethod
    def require(engine: bool = False, command: bool = False, **kwargs: bool) -> "meta":
        """
        Specifies the requirements for a command.
        `engine` and `command` are considered special and will be
        injected automatically when set to true.

        Any other value will be available in the command's "requires" property
        and can be used for evaluation.
        """

        def wrapper(func: any) -> "meta":
            if isinstance(func, meta):
                raise TypeError("meta.require cannot be passed a command object.")
            if not isinstance(func, Command):
                return meta(
                    requires={"engine": engine, "command": command, **kwargs},
                    injections={},
                    func=func,
                    helptext="",
                )
            func.requires = {"engine": engine, "command": command, **kwargs}

        return wrapper

    @staticmethod
    def inject(**kwargs: bool) -> "meta":
        """
        Specifies objects to inject into the function.
        The function's argument must match the injection's argument.
        """

        def wrapper(func: any):
            if isinstance(func, Command):
                raise TypeError("meta.inject cannot be passed a command object.")
            if not isinstance(func, meta):
                return meta(requires={}, injections=kwargs, func=func, helptext="")
            func.injections = kwargs
            return func

        return wrapper

    @staticmethod
    def help(text: str) -> "meta":
        """
        Creates a help text for a command.
        """

        def wrapper(func: any):
            if isinstance(func, Command):
                raise TypeError("meta.inject cannot be passed a command object.")
            if not isinstance(func, meta):
                return meta(requires={}, injections={}, func=func, helptext=text)
            func.helptext = text
            return func

        return wrapper


@dataclass(slots=True)
class Command:
    """A class that defines a command"""

    func: callable  # The function or method that was transformed into a Command.
    name: str
    aliases: list[str]
    requires: dict[
        str, bool
    ]  # The requirements for the command, this can be accessed for custom tests.
    injections: dict[
        str, any
    ]  # Objects that will be injected into the command as kwargs.
    children: dict[str, "Command"] = field(
        default_factory=dict
    )  # Similar to engine.commands; Lists the subcommands attached to a command.
    helptext: str = None

    def __call__(self, *args: any, engine: "InvokeEngine" = None, **kwargs: any) -> any:
        if self.requires.get("engine"):
            if engine is None:
                raise EngineRequired
            self.injections["engine"] = engine

        if self.requires.get("command"):
            self.injections["command"] = self

        return self.func(*args, **self.injections, **kwargs)

    def __repr__(self) -> str:
        return f"Command(func={self.func.__name__}, aliases={self.aliases})"

    @property
    def __name__(self) -> str:
        return self.func.__name__

    def subcommand(
        self,
        func: Union[callable, "Command", meta] = None,
        name: str = None,
        aliases: list[str] = None,
    ) -> "Command":
        """A decorator that turns a function into a subcommand"""

        return create_command(
            func=func,
            commanddict=self.children,
            name=name,
            aliases=aliases,
        )


def create_command(func: callable, commanddict: dict, name: str, aliases: list[str]):
    """Creates a command."""
    if aliases is None:
        aliases = []

    @functools.wraps(func)
    def wrapper(func: callable):
        nonlocal aliases
        nonlocal name

        requires = {}
        inject = {}
        helptext = None
        if isinstance(func, meta):
            requires = func.requires
            inject = func.injections
            helptext = func.helptext
            func = func.func

        if name is None:
            name = func.__name__

        command = func
        if not isinstance(func, Command):
            command = Command(
                func=func,
                name=name,
                aliases=aliases,
                requires=requires,
                injections=inject,
                helptext=helptext,
            )

        aliases.append(name)
        for name in aliases:
            if commanddict.get(name):
                raise CommandAlreadyExists
            commanddict[name] = command
        return command

    if func:
        return wrapper(func)
    return wrapper


@dataclass(slots=True)
class InvokeEngine:
    """A container for commands."""

    commands: dict[str, Command] = field(default_factory=dict)

    def parse(
        self,
        command_list: list[any],
        _command: Command = None,
        _callstack: list[Command] = None,
    ) -> tuple[Command, tuple[any, ...], tuple[Command, ...]]:
        """Parses a list to find the lowest level subcommand, and passes the rest of the arguments back."""
        if _callstack is None:
            _callstack = []
        else:
            _callstack.append(_command)

        if len(command_list) == 0:
            return (_command, command_list, tuple(_callstack))

        if _command is None:
            command = self.commands.get(command_list[0])
        else:
            command = _command.children.get(command_list[0])

        if command is None:
            return (_command, command_list, tuple(_callstack))

        return self.parse(
            command_list=command_list[1:], _command=command, _callstack=_callstack
        )

    def command(
        self,
        func: Union[callable, Command, meta] = None,
        name: str = None,
        aliases: list[str] = None,
    ) -> Command:
        """A decorator that turns a function into a command"""

        return create_command(
            func=func, commanddict=self.commands, name=name, aliases=aliases
        )
