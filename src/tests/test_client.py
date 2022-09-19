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


if __name__ == "__main__":
    unittest.main()
