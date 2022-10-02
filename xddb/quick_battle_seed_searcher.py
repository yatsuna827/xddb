from typing import Tuple

from lcg.gc import LCG

from .client import XDDBClient, _to_code
from .quick_battle import EnemyTeam, PlayerTeam, generate_quick_battle


def _qb_next(seed: int, tsv: int):
    lcg = LCG(seed)
    p, e, c, _ = generate_quick_battle(lcg, tsv)
    return (p, e, c), lcg.seed


class QuickBattleSeedSearcher(object):
    """
    手続き的にseed特定を行うのを補助するクラスです.
    """

    def __init__(self, client: XDDBClient, tsv: int = 0x10000) -> None:
        self._state = self._FirstState()
        self._context = {"tsv": tsv, "client": client}

    def next(
        self, input_p: Tuple[PlayerTeam, int, int], input_e: Tuple[EnemyTeam, int, int]
    ):
        """
        入力に応じて現在のseedの候補を返します.
        入力が不足している場合はNoneが返却されます.
        """

        res, next = self._state.next(input_p, input_e, self._context)
        self._state = next

        return res

    def reset(self):
        self._state = self._FirstState()

    class _FirstState(object):
        def next(self, p, e, ctx):
            return None, QuickBattleSeedSearcher._SecondState(p, e)

    class _SecondState(object):
        def __init__(self, p, e) -> None:
            self._p, self._e = p, e

        def next(self, p, e, ctx):
            res = ctx["client"].search(self._p, self._e, p, e)
            return res, QuickBattleSeedSearcher._ExtState(res)

    class _ExtState(object):
        def __init__(self, seeds) -> None:
            self._seeds = seeds

        def next(self, p, e, ctx):
            correct = p[0], e[0], _to_code(p, e)
            res = {
                seed
                for tri, seed in [_qb_next(s, ctx["tsv"]) for s in self._seeds]
                if tri == correct
            }
            return res, QuickBattleSeedSearcher._ExtState(res)
