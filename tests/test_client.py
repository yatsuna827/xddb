import unittest

from xddb import EnemyTeam, PlayerTeam, XDDBClient


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


if __name__ == "__main__":
    unittest.main()
