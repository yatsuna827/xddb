from typing import Tuple, Union

from lcg.gc import LCG
from typing_extensions import TypedDict

from .client import XDDBClient, _to_code
from .quick_battle import EnemyTeam, PlayerTeam, generate_quick_battle


def _qb_next(seed: int, tsv: int):
    lcg = LCG(seed)
    p, e, c, _ = generate_quick_battle(lcg, tsv)
    return (p, e, c), lcg.seed


_State = Union[
    "_FirstState",
    "_SecondState",
    "_ExtState",
]
PlayerInput = Tuple[PlayerTeam, int, int]
EnemyInput = Tuple[EnemyTeam, int, int]
_Context = TypedDict("_Context", {"tsv": int, "client": XDDBClient})


class _FirstState(object):
    def next(self, p: PlayerInput, e: EnemyInput, ctx: _Context):
        return None, _SecondState(p, e)


class _SecondState(object):
    def __init__(self, p: PlayerInput, e: EnemyInput) -> None:
        self._p, self._e = p, e

    def next(self, p: PlayerInput, e: EnemyInput, ctx: _Context):
        res = ctx["client"].search(self._p, self._e, p, e)
        return res, _ExtState(res)


class _ExtState(object):
    def __init__(self, seeds) -> None:
        self._seeds = seeds

    def next(self, p: PlayerInput, e: EnemyInput, ctx: _Context):
        correct = p[0], e[0], _to_code(p, e)
        res = {
            seed
            for tri, seed in [_qb_next(s, ctx["tsv"]) for s in self._seeds]
            if tri == correct
        }
        return res, _ExtState(res)


class QuickBattleSeedSearcher(object):
    """
    手続き的にseed特定を行うのを補助するクラスです.
    """

    def __init__(self, client: XDDBClient, tsv: int = 0x10000) -> None:
        self._state: _State = _FirstState()
        self._context: _Context = {"tsv": tsv, "client": client}

    def next(self, input_p: PlayerInput, input_e: EnemyInput):
        """
        入力に応じて現在のseedの候補を返します.
        入力が不足している場合はNoneが返却されます.
        """

        res, next = self._state.next(input_p, input_e, self._context)
        self._state = next

        return res

    def reset(self):
        self._state = _FirstState()
