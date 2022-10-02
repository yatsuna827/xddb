import unittest

from xddb import EnemyTeam, PlayerTeam, QuickBattleSeedSearcher, XDDBClient


class TestXDDBClient(unittest.TestCase):

    cli = XDDBClient()

    def test_search(self):
        # testcase: https://github.com/yatsuna827/XDDatabase/issues/2
        res = self.cli.search(
            (PlayerTeam.デオキシス, 257, 648),
            (EnemyTeam.サンダー, 326, 281),
            (PlayerTeam.ジラーチ, 349, 325),
            (EnemyTeam.サンダー, 336, 313),
        )
        self.assertEqual({0x233F7EC1, 0xF03F7EC1}, res)

        res = self.cli.search(
            (PlayerTeam.デオキシス, 256, 650),
            (EnemyTeam.ファイヤー, 327, 256),
            (PlayerTeam.ミュウツー, 362, 349),
            (EnemyTeam.フリーザー, 320, 388),
        )
        self.assertEqual({0x4D1FFF4D}, res)

    def test_db_hash(self):
        hash = self.cli.db_hash
        self.assertEqual("d01348c9b687259e2e0467f4af6f979b", hash)

    def test_QuickBattleSeedSearcher(self):
        # init_seed = 0x481A5E2E

        searcher = QuickBattleSeedSearcher(self.cli)
        res = searcher.next((PlayerTeam.ミュウ, 340, 335), (EnemyTeam.フリーザー, 309, 344))
        self.assertEqual(None, res)
        res = searcher.next((PlayerTeam.ミュウ, 357, 321), (EnemyTeam.ラティアス, 289, 290))
        self.assertEqual({0x9F297767, 0x51297767, 0x03297767}, res)
        res = searcher.next((PlayerTeam.レックウザ, 347, 241), (EnemyTeam.サンダー, 321, 293))
        self.assertEqual({0x1257DEF0}, res)


if __name__ == "__main__":
    unittest.main()
