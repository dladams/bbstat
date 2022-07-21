import pkg_resources  # part of setuptools
version = pkg_resources.require("bbstat")[0].version
__version__ = version

from .data.roster import Roster
from .data.results import AtBatResult
from .data.counter import Counter
from .data.lineup import Lineup
from .stats.gamestats import GameStats
from .data.frame import Frame
from .data.game import HalfGame
from .data.game import Game
from .data.reader import Reader
from .stats.batstats import BatStats
from .stats.pitchstats import PitchStats

from .test.test_counter import main_test_counter
from .test.test_lineup  import main_test_lineup
from .test.test_game    import main_test_game
from .test.test_stats   import main_test_stats
from .test.test_reader  import main_test_reader
