from typing import List, Optional, Tuple


def _precalc(a: int, b: int) -> List[Tuple[int, int]]:
    cache = []
    for i in range(0, 32):
        cache.append((a, b))
        a, b = a * a & 0xFFFFFFFFF, (b * (1 + a)) & 0xFFFFFFFF
    return cache


_doubling_f = _precalc(0x343FD, 0x269EC3)
_doubling_f_inv = _precalc(0xB9B33155, 0xA170F641)


class LCG(object):
    seed: int

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def _jump(self, n: int, mem: List[Tuple[int, int]]) -> int:
        for i in range(0, 32):
            if n & (1 << i):
                a, b = mem[i]
                self.seed = (self.seed * a + b) & 0xFFFFFFFF
        return self.seed

    def adv(self, n: Optional[int] = None) -> int:
        if n is None:
            self.seed = (self.seed * 0x343FD + 0x269EC3) & 0xFFFFFFFF
            return self.seed
        else:
            return self._jump(n, _doubling_f)

    def back(self, n: Optional[int] = None) -> int:
        if n is None:
            self.seed = (self.seed * 0xB9B33155 + 0xA170F641) & 0xFFFFFFFF
            return self.seed
        else:
            return self._jump(n, _doubling_f_inv)

    def rand(self, m: Optional[int] = None) -> int:
        rand = self.adv() >> 16
        return rand % m if m is not None else rand
