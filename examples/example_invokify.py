from invokify import InvokeEngine, meta, string_to_args


class Player:
    def __init__(self):
        self.money = 0

    def buy(self, amount: int) -> str:
        self.money -= amount
        return f"You have spent {amount} and now have {self.money}"

    def sell(self, amount: int) -> str:
        self.money += amount
        return f"You have made {amount} and now have {self.money}"


engine = InvokeEngine()
new_player = Player()


@engine.command
def buy(amount: int, player: Player):
    return player.buy(amount)


@engine.command
@meta.require(command=True)
def sell(amount: int, player: Player, command):
    return command.children


@sell.subcommand(aliases=["alot"])
def all(*_, player: Player):
    return player.sell(10000000)


while True:
    user = input()

    user = string_to_args(user)

    cmd, args, cs = engine.parse(user)

    result = cmd(100, player=new_player)

    print(result)
