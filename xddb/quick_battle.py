from enum import IntEnum
from typing import List, Optional, Set, Tuple, overload

from lcg.gc import LCG

_p_base_hp: List[Tuple[int, int]] = [
    (322, 340),
    (310, 290),
    (210, 620),
    (320, 230),
    (310, 310),
]

_e_base_hp: List[Tuple[int, int]] = [
    (290, 310),
    (290, 270),
    (290, 250),
    (320, 270),
    (270, 230),
]


class PlayerTeam(IntEnum):
    Mewtwo = 0
    ミュウツー = 0
    Mew = 1
    ミュウ = 1
    Deoxys = 2
    デオキシス = 2
    Rayquaza = 3
    レックウザ = 3
    Jirachi = 4
    ジラーチ = 4

    @property
    def base_hp(self):
        return _p_base_hp[self]


class EnemyTeam(IntEnum):
    Articuno = 0
    フリーザー = 0
    Zapdos = 1
    サンダー = 1
    Moltres = 2
    ファイヤー = 2
    Kangaskhan = 3
    ガルーラ = 3
    Latias = 4
    ラティアス = 4

    @property
    def base_hp(self):
        return _e_base_hp[self]


@overload
def generate_quick_battle(lcg: LCG) -> Tuple[PlayerTeam, EnemyTeam, int, Set[int]]:
    pass


@overload
def generate_quick_battle(lcg: LCG, p_tsv: int) -> Tuple[PlayerTeam, EnemyTeam, int]:
    pass


def generate_quick_battle(lcg: LCG, p_tsv: Optional[int] = None):
    """
    Returns:
        `(p_team: PlayerTeam, e_team: EnemyTeam, code: int, p_team_psvs: set[int])`
    """
    lcg.adv()
    p_team = PlayerTeam(lcg.rand(5))
    e_team = EnemyTeam(lcg.rand(5))

    lcg.adv()
    e_tsv = lcg.rand() ^ lcg.rand()

    hp = [0, 0, 0, 0]
    psv: Set[int] = Set()

    # 相手1匹目
    lcg.adv()
    lcg.adv()
    hp[0] = lcg.rand(32)
    lcg.adv()  # SCD
    lcg.adv()  # Ability
    while True:
        if (lcg.rand() ^ lcg.rand() ^ e_tsv) >= 8:
            break
    hp[0] += _gen_evs(lcg) // 4

    # 相手2匹目
    lcg.adv()
    lcg.adv()
    hp[1] = lcg.rand(32)
    lcg.adv()  # SCD
    lcg.adv()  # Ability
    while True:
        if (lcg.rand() ^ lcg.rand() ^ e_tsv) >= 8:
            break
    hp[1] += _gen_evs(lcg) // 4

    lcg.adv()
    lcg.adv()
    lcg.adv()

    # プレイヤー1匹目
    lcg.adv()
    lcg.adv()
    hp[2] = lcg.rand(32)
    lcg.adv()  # SCD
    lcg.adv()  # Ability
    if p_tsv is None:
        psv.add(lcg.rand() ^ lcg.rand())
    else:
        while True:
            if (lcg.rand() ^ lcg.rand() ^ p_tsv) >= 8:
                break
    hp[2] += _gen_evs(lcg) // 4

    # プレイヤー2匹目
    lcg.adv()
    lcg.adv()
    hp[3] = lcg.rand(32)
    lcg.adv()  # SCD
    lcg.adv()  # Ability
    if p_tsv is None:
        psv.add(lcg.rand() ^ lcg.rand())
    else:
        while True:
            if (lcg.rand() ^ lcg.rand() ^ p_tsv) >= 8:
                break
    hp[3] += _gen_evs(lcg) // 4

    result = (
        p_team,
        e_team,
        (hp[0] << 24) + (hp[1] << 16) + (hp[2] << 8) + (hp[3]),
    )

    if p_tsv is None:
        return (*result, psv)
    else:
        return result


def _gen_evs(lcg: LCG) -> int:
    evs = [0, 0, 0, 0, 0, 0]
    sum_evs = 0

    for i in range(0, 101):
        evs = [(_ + lcg.rand(0x100)) & 0xFF for _ in evs]
        sum_evs = sum(evs)

        if sum_evs == 510:
            return evs[0]
        if sum_evs <= 490:
            continue
        if sum_evs < 510:
            _fill(evs, sum_evs)
            return evs[0]
        if sum_evs < 530:
            _shave(evs, sum_evs)
            return evs[0]

        if i != 100:
            evs = [0, 0, 0, 0, 0, 0]

    if sum_evs < 510:
        _fill(evs, sum_evs)
    elif sum_evs > 510:
        _shave(evs, sum_evs)

    return evs[0]


def _shave(evs: List[int], sum_evs: int) -> None:
    while True:
        for i in range(0, 6):
            if sum_evs == 510:
                return
            if evs[i] > 0:
                evs[i] -= 1
                sum_evs -= 1


def _fill(evs: List[int], sum_evs: int) -> None:
    while True:
        for i in range(0, 6):
            if sum_evs == 510:
                return
            if evs[i] < 255:
                evs[i] += 1
                sum_evs += 1
