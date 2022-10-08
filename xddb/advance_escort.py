from typing import Union

from lcg.gc import LCG

from .quick_battle import EnemyTeam, PlayerTeam, generate_quick_battle
from .quick_battle_seed_searcher import EnemyInput, PlayerInput


def _decode(code: int, p: PlayerTeam, e: EnemyTeam):
    p1, p2 = p.base_hp
    e1, e2 = e.base_hp
    return (
        p1 + ((code >> 8) & 0xFF),
        p2 + (code & 0xFF),
        e1 + ((code >> 24) & 0xFF),
        e2 + ((code >> 16) & 0xFF),
    )


class Found(object):
    def __init__(self, seed: int, tsv: Union[int, None] = None) -> None:
        self._seed = seed
        self._tsv = tsv

    @property
    def current_seed(self):
        return self._seed

    @property
    def found_tsv(self):
        return self._tsv


class NotFound(object):
    pass


class QuickBattleAdvanceEscort(object):
    def __init__(self, current_seed: int, tsv: int = 0x10000) -> None:
        self.seed: Union[int, None] = current_seed
        self._tsv = tsv if tsv <= 0x10000 else 0x10000

    def expected_next(self):
        if self.seed is None:
            raise ValueError("現在のseedが未特定です")

        lcg = LCG(self.seed)
        p, e, code, _ = generate_quick_battle(lcg)
        p1, p2, e1, e2 = _decode(code, p, e)
        return (p, p1, p2), (e, e1, e2), lcg.seed

    def next(self, input_p: PlayerInput, input_e: EnemyInput) -> Union[Found, NotFound]:
        if self.seed is None:
            raise ValueError("現在のseedが未特定です")

        lcg = LCG(self.seed)
        p, e, code, psvs = generate_quick_battle(lcg, self._tsv)
        p1, p2, e1, e2 = _decode(code, p, e)

        arg_p, arg_p1, arg_p2 = input_p
        arg_e, arg_e1, arg_e2 = input_e

        # パーティor敵のHPが違っていたら修復不能
        if (p, e) != (arg_p, arg_e):
            self.seed = None
            return NotFound()
        if (e1, e2) != (arg_e1, arg_e2):
            self.seed = None
            return NotFound()

        if (p1, p2) == (arg_p1, arg_p2):
            self.seed = lcg.seed
            return Found(lcg.seed)

        # tsvが指定されていれば修復不能
        if self._tsv != 0x10000:
            return NotFound()

        # tsvを仮定して検索してみる
        for tsv in psvs:
            lcg = LCG(self.seed)
            p, e, code, _ = generate_quick_battle(lcg, tsv)
            p1, p2, _, _ = _decode(code, p, e)
            if (p1, p2) == (arg_p1, arg_p2):
                self._tsv = tsv
                self.seed = lcg.seed
                return Found(lcg.seed, tsv)

        # それでもダメなら修復不能
        self.seed = None
        return NotFound()
