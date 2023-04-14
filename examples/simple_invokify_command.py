from invokify import InvokeEngine, meta, string_to_args

engine = InvokeEngine()


class Player:
    def __init__(self):
        self.money = 0

    def buy(self, amount: int) -> str:
        self.money -= amount
        return f"You have spent {amount} and now have {self.money}"

    def sell(self, amount: int) -> str:
        self.money += amount
        return f"You have made {amount} and now have {self.money}"


player = Player()


@engine.command
@meta.inject(obj=player)
@meta.require(engine=True)
def buy(amount: int, *args, obj: Player, responses: list = None, engine):
    if responses is None:
        responses = []
    responses.append(obj.buy(amount))
    cmd, cmd_args, _ = engine.parse(args)
    if cmd is not None:
        cmd(*cmd_args, responses=responses, engine=engine)
    return responses


@engine.command
@meta.inject(obj=player)
@meta.require(engine=True)
def sell(amount: int, *args, obj: Player, responses: list = None, engine):
    if responses is None:
        responses = []
    responses.append(obj.sell(amount))
    cmd, cmd_args, _ = engine.parse(args)
    if cmd is not None:
        cmd(*cmd_args, responses=responses, engine=engine)
    return responses


@engine.command
def test1():
    ...


@test1.subcommand
def test2():
    ...


@test2.subcommand
def test3():
    ...


while True:
    user = input()

    result = string_to_args(user)

    command, args, cs = engine.parse(result)

    print(cs)
    print("\n".join(command(*args, engine=engine)))
