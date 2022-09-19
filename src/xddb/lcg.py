from typing import List, Optional, Tuple

_mask = 0xFFFF_FFFF
_a, _b = 0x343FD, 0x269EC3
_a_rev, _b_rev = 0xB9B33155, 0xA170F641


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


_doubling = _precalc(_a, _b)


def _jump(seed: int, n: int) -> int:
    for i in range(0, 32):
        if n & (1 << i):
            a, b = _doubling[i]
            seed = (seed * a + b) & _mask
    return seed


class LCG(object):
    _cnt: int
    seed: int

    def __init__(self, seed: int, offset: int = 0) -> None:
        offset &= _mask
        self._cnt = offset
        self.seed = _jump(seed, offset) if offset else seed

    def _increment(self, n: int) -> None:
        self._cnt = (self._cnt + n) & _mask

    def adv(self, n: Optional[int] = None) -> "LCG":
        if n is None:
            self._increment(1)
            self.seed = (self.seed * _a + _b) & _mask
            return self
        else:
            self._increment(n)
            self.seed = _jump(self.seed, n)
            return self

    def back(self, n: Optional[int] = None) -> "LCG":
        if n is None:
            self._increment(-1)
            self.seed = (self.seed * _a_rev + _b_rev) & _mask
            return self
        else:
            self._increment(-n)
            self.seed = _jump(self.seed, (-n) & _mask)
            return self

    def rand(self, m: Optional[int] = None) -> int:
        rand = self.adv().seed >> 16
        return rand % m if m is not None else rand

    @property
    def index(self) -> int:
        return self._cnt

    def index_from(self, init_seed: int) -> int:
        idx = _calc_index(self.seed, _a, _b, 32)
        base = _calc_index(init_seed, _a, _b, 32)
        return (idx - base) & _mask
