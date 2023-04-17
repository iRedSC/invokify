"""
Invokify

Allows the creation of parsible commands using decorators.
"""
__all__ = ["CommandAlreadyExists", "EngineRequired", "meta", "Command", "InvokeEngine"]

import functools
from dataclasses import dataclass, field
from typing import Any, Callable, Optional, Union


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
    injections: dict[str, Any] = field(default_factory=dict)
    func: Optional[Callable[..., Any]] = None
    helptext: str = ""

    @staticmethod
    def require(
        engine: bool = False, command: bool = False, **kwargs: bool
    ) -> Callable[[Callable[..., Any] | "meta"], "meta|Command"]:
        """
        Specifies the requirements for a command.
        `engine` and `command` are considered special and will be
        injected automatically when set to true.

        Any other value will be available in the command's "requires" property
        and can be used for evaluation.
        """

        def wrapper(func: Callable[..., Any] | "meta") -> meta | Command:
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
            return func

        return wrapper

    @staticmethod
    def inject(
        **kwargs: Any,
    ) -> Callable[[Callable[..., Any] | "meta"], "meta|Command"]:
        """
        Specifies objects to inject into the function.
        The function's argument must match the injection's argument.
        """

        def wrapper(func: Callable[..., Any] | "meta") -> "meta|Command":
            if isinstance(func, Command):
                raise TypeError("meta.inject cannot be passed a command object.")
            if not isinstance(func, meta):
                return meta(requires={}, injections=kwargs, func=func, helptext="")
            func.injections = kwargs
            return func

        return wrapper

    @staticmethod
    def help(text: str) -> Callable[[Callable[..., Any] | "meta"], "meta|Command"]:
        """
        Creates a help text for a command.
        """

        def wrapper(func: Callable[..., Any] | "meta") -> "meta|Command":
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

    func: Callable[
        ..., Any
    ]  # The function or method that was transformed into a Command.
    name: str
    aliases: list[str]
    requires: dict[
        str, bool
    ]  # The requirements for the command, this can be accessed for custom tests.
    injections: dict[
        str, Any
    ]  # Objects that will be injected into the command as kwargs.
    children: dict[str, "Command"] = field(
        default_factory=dict
    )  # Similar to engine.commands; Lists the subcommands attached to a command.
    helptext: Optional[str] = None

    def __call__(
        self, *args: Any, engine: Optional["InvokeEngine"] = None, **kwargs: Any
    ) -> Any:
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
        func: Optional[Union[Callable[..., Any], "Command", meta]] = None,
        name: Optional[str] = None,
        aliases: Optional[list[str]] = None,
    ) -> "Command":
        """A decorator that turns a function into a subcommand"""

        return create_command(
            func=func,
            commanddict=self.children,
            name=name,
            aliases=aliases,
        )


def create_command(
    func: Optional[Callable[..., Any] | meta],
    commanddict: dict[str, Command],
    name: Optional[str],
    aliases: Optional[list[str]],
) -> Command:
    """Creates a command."""
    if aliases is None:
        aliases = []

    @functools.wraps(func)  # type: ignore
    def wrapper(func: Callable[..., Any] | Command | meta) -> Command:
        nonlocal aliases
        nonlocal name

        requires = {}
        inject = {}
        helptext = None
        if isinstance(func, meta):
            requires = func.requires
            inject = func.injections
            helptext = func.helptext
            func = func.func  # type: ignore

        if name is None:
            name = func.__name__  # type: ignore

        command = func
        if not isinstance(func, Command):
            command = Command(
                func=func,  # type: ignore
                name=name,  # type: ignore
                aliases=aliases,
                requires=requires,
                injections=inject,
                helptext=helptext,
            )

        aliases.append(name)  # type: ignore
        for name in aliases:
            if commanddict.get(name):
                raise CommandAlreadyExists
            # This will always be set to a command because in the above code,
            # if command is not a Command, it will be set as one.
            commanddict[name] = command  # type: ignore
        return command  # type: ignore

    if func:
        return wrapper(func)
    return wrapper  # type: ignore


@dataclass(slots=True)
class InvokeEngine:
    """A container for commands."""

    commands: dict[str, Command] = field(default_factory=dict)

    def parse(
        self,
        command_list: list[Any],
        _command: Optional[Command] = None,
        _callstack: Optional[list[Command]] = None,
    ) -> tuple[Command, tuple[Any, ...], tuple[Command, ...]]:
        """Parses a list to find the lowest level subcommand, and passes the rest of the arguments back."""
        if _callstack is None:
            _callstack = []
        else:
            _callstack.append(_command)  # type: ignore

        if len(command_list) == 0:
            return (_command, command_list, tuple(_callstack))  # type: ignore

        if _command is None:
            command = self.commands.get(command_list[0])
        else:
            command = _command.children.get(command_list[0])

        if command is None:
            return (_command, command_list, tuple(_callstack))  # type: ignore

        return self.parse(
            command_list=command_list[1:], _command=command, _callstack=_callstack
        )

    def command(
        self,
        func: Optional[Union[Callable[..., Any], Command, meta]] = None,
        name: Optional[str] = None,
        aliases: Optional[list[str]] = None,
    ) -> Command:
        """A decorator that turns a function into a command"""

        return create_command(
            func=func, commanddict=self.commands, name=name, aliases=aliases
        )
