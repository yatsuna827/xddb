import unittest

from xddb import EnemyTeam, PlayerTeam
from xddb.advance_escort import Found, NotFound, QuickBattleAdvanceEscort


class TestAdvanceEscort(unittest.TestCase):
    def test_found(self):
        expected_next = ((PlayerTeam(2), 244, 696), (EnemyTeam(1), 304, 314))
        expected_next_seed = 0x761F0A91

        ae = QuickBattleAdvanceEscort(0xCAFECAFE)
        exp = ae.expected_next()

        self.assertEqual(exp[0:2], expected_next)
        self.assertEqual(exp[2], expected_next_seed)

        # expected_nextを呼んだときはseedは更新されない
        self.assertEqual(ae.seed, 0xCAFECAFE)

        res = ae.next(expected_next[0], expected_next[1])
        self.assertIsInstance(res, Found)
        self.assertEqual(res.current_seed, expected_next_seed)
        self.assertEqual(ae.seed, expected_next_seed)

    def test_not_found(self):
        ae = QuickBattleAdvanceEscort(0xCAFECAFE)

        # 入力ミスなどが発生
        res = ae.next((PlayerTeam(0), 244, 696), (EnemyTeam(1), 304, 314))
        self.assertIsInstance(res, NotFound)

        # 現在のseedが不明になった場合、seedもNoneになる
        self.assertEqual(ae.seed, None)

        # seedがNoneの状態でメソッドを呼ぶと例外
        with self.assertRaises(ValueError):
            ae.expected_next()
        with self.assertRaises(ValueError):
            ae.next((PlayerTeam(0), 244, 696), (EnemyTeam(1), 304, 314))

    def test_reroll(self):
        """
        プレイヤーのTSV依存の色回避処理が発生した場合
        """
        tsv = 28553
        expected_next = (PlayerTeam.Rayquaza, 329, 298), (EnemyTeam.Zapdos, 320, 316)
        expected_next_seed = 0xD71DC25E
        actually_next = (PlayerTeam.Rayquaza, 328, 274), (EnemyTeam.Zapdos, 320, 316)
        actually_next_seed = 0x27B193C8

        ae = QuickBattleAdvanceEscort(0xE83E76F5)
        exp = ae.expected_next()
        self.assertEqual(exp[0:2], expected_next)
        self.assertEqual(exp[2], expected_next_seed)

        res = ae.next(actually_next[0], actually_next[1])
        self.assertIsInstance(res, Found)
        self.assertEqual(res.current_seed, actually_next_seed)
        self.assertEqual(res.found_tsv, tsv)
        self.assertEqual(ae._tsv, tsv)


if __name__ == "__main__":
    unittest.main()
