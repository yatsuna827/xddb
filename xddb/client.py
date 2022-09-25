from bisect import bisect_left, bisect_right
from os.path import abspath, dirname, join, normpath
from sys import byteorder
from typing import List, Set, Tuple

from lcg.gc import LCG

from .quick_battle import EnemyTeam, PlayerTeam, generate_quick_battle

_path_file = normpath(join(dirname(abspath(__file__)), "./XDDB.bin"))


def _to_code(p: Tuple[PlayerTeam, int, int], e: Tuple[EnemyTeam, int, int]) -> int:
    p_team, p_hp_0, p_hp_1 = p
    e_team, e_hp_0, e_hp_1 = e

    e1, e2 = e_hp_0 - e_team.base_hp[0], e_hp_1 - e_team.base_hp[1]
    p1, p2 = p_hp_0 - p_team.base_hp[0], p_hp_1 - p_team.base_hp[1]
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

            p, e, code, _ = generate_quick_battle(lcg)
            if code != code1:
                continue
            if p != p_team1:
                continue
            if e != e_team1:
                continue

            p, e, code, _ = generate_quick_battle(lcg)
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
