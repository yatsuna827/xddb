from typing import Optional


class LCG(object):
    seed: int

    def __init__(self, seed: int) -> None:
        self.seed = seed

    def adv(self) -> int:
        self.seed = (self.seed * 0x343FD + 0x269EC3) & 0xFFFFFFFF
        return self.seed

    def back(self) -> int:
        self.seed = (self.seed * 0xB9B33155 + 0xA170F641) & 0xFFFFFFFF
        return self.seed

    def rand(self, m: Optional[int] = None) -> int:
        rand = self.adv() >> 16
        return rand % m if m is not None else rand
