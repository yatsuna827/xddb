import unittest

from xddb.lcg import LCG


class TestLCG(unittest.TestCase):
    def test_advance(self):
        expected = [
            0x41A8D6F9,
            0x99313DD8,
            0x0288453B,
            0xFAA27B12,
            0xAA25F58D,
            0xF795321C,
            0x510A786F,
            0x3E51B176,
            0x0CB6E261,
            0x1546BBA0,
        ]
        lcg = LCG(0xC0FFEE)
        self.assertEqual(expected, [lcg.adv() for _ in range(0, 10)])

    def test_jump(self):
        lcg = LCG(0xBEEF)
        self.assertEqual(0x5ACCB204, lcg.adv(0x827827))

    def test_back(self):
        seed = 0xBADFACE
        lcg = LCG(seed)
        self.assertNotEqual(seed, lcg.adv())
        self.assertEqual(seed, lcg.back())

    def test_index(self):
        seed = 0xDEADBEEF
        lcg = LCG(seed)

        seed_12345 = lcg.adv(12345)
        self.assertEqual(12345, lcg.index)

        lcg.back(100)
        self.assertEqual(12245, lcg.index)

        lcg = LCG(seed_12345)
        self.assertEqual(12345, lcg.index_from(seed))


if __name__ == "__main__":
    unittest.main()
