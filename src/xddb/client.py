from bisect import bisect_left, bisect_right
from enum import IntEnum
from os.path import abspath, dirname, join, normpath
from sys import byteorder
from typing import List, Set, Tuple

from .lcg import LCG
from .quick_battle import generate_quick_battle

_path_file = normpath(join(dirname(abspath(__file__)), "./XDDB.bin"))


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


def _to_code(p: Tuple[PlayerTeam, int, int], e: Tuple[PlayerTeam, int, int]) -> int:
    p_team, p_hp_0, p_hp_1 = p
    e_team, e_hp_0, e_hp_1 = e

    e1, e2 = e_hp_0 - _e_base_hp[e_team][0], e_hp_1 - _e_base_hp[e_team][1]
    p1, p2 = p_hp_0 - _p_base_hp[p_team][0], p_hp_1 - _p_base_hp[p_team][1]
    return (e1 << 24) | (e2 << 16) | (p1 << 8) | p2


class XDDBClient(object):
    def __init__(self) -> None:
        self.seed_list: List[int] = []
        self.code_list: List[int] = []
        with open(_path_file, "rb") as reader:
            while True:
                code, seed = reader.read(4), reader.read(4)
                if not code:
                    break
                self.seed_list.append(int.from_bytes(seed, byteorder))
                self.code_list.append(int.from_bytes(code, byteorder))

    def search(
        self,
        first_p: Tuple[PlayerTeam, int, int],
        first_e: Tuple[EnemyTeam, int, int],
        second_p: Tuple[PlayerTeam, int, int],
        second_e: Tuple[EnemyTeam, int, int],
    ) -> Set[int]:
        code1 = _to_code(first_p, first_e)
        p_team1, _, _ = first_p
        e_team1, _, _ = first_e

        l = bisect_left(self.code_list, code1)
        r = bisect_right(self.code_list, code1)
        l24_list = self.seed_list[l:r]

        code2 = _to_code(second_p, second_e)
        p_team2, _, _ = second_p
        e_team2, _, _ = second_e

        res = set()
        for seed in [(h8 << 24) | l24 for l24 in l24_list for h8 in range(0, 0x100)]:
            lcg = LCG(seed)

            p, e, code = generate_quick_battle(lcg)
            if code != code1:
                continue
            if p != p_team1:
                continue
            if e != e_team1:
                continue

            p, e, code = generate_quick_battle(lcg)
            if code != code2:
                continue
            if p != p_team2:
                continue
            if e != e_team2:
                continue

            res.add(lcg.seed)
        return res

    @property
    def db_hash(self):
        from hashlib import md5

        with open(_path_file, "rb") as f:
            return md5(f.read()).hexdigest()
