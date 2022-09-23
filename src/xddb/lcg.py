from typing import List, Optional, Tuple

_mask = 0xFFFF_FFFF


def _precalc(a: int, b: int) -> List[Tuple[int, int]]:
    cache = []
    for i in range(0, 32):
        cache.append((a, b))
        a, b = a * a & _mask, (b * (1 + a)) & _mask
    return cache


def _calc_index(seed: int, a: int, b: int, order: int) -> int:
    if order == 0:
        return 0

    if (seed & 1) == 0:
        a, b = (a * a) & _mask, (((a + 1) * b) & _mask) // 2
        return _calc_index(seed // 2, a, b, order - 1) * 2
    else:
        seed = (a * seed + b) & _mask
        a, b = (a * a) & _mask, (((a + 1) * b) & _mask) // 2
        return _calc_index(seed // 2, a, b, order - 1) * 2 - 1


class LCG(object):
    def __init__(self, seed: int, offset: int = 0) -> None:
        offset &= _mask
        self._cnt: int = offset
        self.seed: int = self._jump(seed, offset) if offset else seed

    _a, _b = 0x343FD, 0x269EC3
    _a_rev, _b_rev = 0xB9B33155, 0xA170F641
    _doubling = _precalc(_a, _b)

    @classmethod
    def _jump(self, seed: int, n: int) -> int:
        for i in range(0, 32):
            if n & (1 << i):
                a, b = self._doubling[i]
                seed = (seed * a + b) & _mask
        return seed

    def adv(self, n: Optional[int] = None):
        if n is None:
            self._cnt = (self._cnt + 1) & _mask
            self.seed = (self.seed * self._a + self._b) & _mask
            return self
        else:
            self._cnt = (self._cnt + n) & _mask
            self.seed = self._jump(self.seed, n)
            return self

    def back(self, n: Optional[int] = None):
        if n is None:
            self._cnt = (self._cnt - 1) & _mask
            self.seed = (self.seed * self._a_rev + self._b_rev) & _mask
            return self
        else:
            self._cnt = (self._cnt - n) & _mask
            self.seed = self._jump(self.seed, (-n) & _mask)
            return self

    def rand(self, m: Optional[int] = None) -> int:
        rand = self.adv().seed >> 16
        return rand % m if m is not None else rand

    @property
    def index(self) -> int:
        return self._cnt

    def index_from(self, init_seed: int) -> int:
        return self.get_index(self.seed, init_seed)

    @classmethod
    def gen_seed(self, seed: int, take: Optional[int] = None):
        if take is None:
            while True:
                yield seed
                seed = (seed * self._a + self._b) & _mask
        else:
            for _ in range(0, take):
                yield seed
                seed = (seed * self._a + self._b) & _mask

    @classmethod
    def get_index(self, seed: int, init_seed: int) -> int:
        idx = _calc_index(seed, self._a, self._b, 32)
        base = _calc_index(init_seed, self._a, self._b, 32)
        return (idx - base) & _mask
