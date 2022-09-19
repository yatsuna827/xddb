from typing import List, Tuple

from .lcg import LCG


def generate_quick_battle(lcg: LCG, p_tsv: int = 0x10000) -> Tuple[int, int, int]:
    """
    Returns:
        (p_team: int, e_team: int, code: int)
    """
    lcg.adv()
    p_team = lcg.rand(5)
    e_team = lcg.rand(5)

    lcg.adv()
    e_tsv = lcg.rand() ^ lcg.rand()

    hp = [0, 0, 0, 0]

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
    while True:
        if (lcg.rand() ^ lcg.rand() ^ p_tsv) >= 8:
            break
    hp[3] += _gen_evs(lcg) // 4

    return (
        p_team,
        e_team,
        (hp[0] << 24) + (hp[1] << 16) + (hp[2] << 8) + (hp[3]),
    )


def _gen_evs(lcg: LCG) -> int:
    evs = [0, 0, 0, 0, 0, 0]
    sum_evs = 0

    for i in range(0, 101):
        evs = [_ + lcg.rand(0x100) for _ in evs]
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
            if evs[i] != 0:
                evs[i] -= 1
                sum_evs -= 1


def _fill(evs: List[int], sum_evs: int) -> None:
    while True:
        for i in range(0, 6):
            if sum_evs == 510:
                return
            if evs[i] != 0:
                evs[i] += 1
                sum_evs += 1
