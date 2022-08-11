from collections import OrderedDict
from bbstat import Counter
from bbstat import Lineup
from bbstat import Frame
from bbstat import GameStats

class HalfGame:
    '''
      A half game holds a game counter, inning numbers indexed by count, and
      initial frames indexed by inning number.
    '''

    def __init__(self, counter, team_bat, team_field, olup, dlup, ostats, dstats):
        '''
          team: Team name
          olup: Shared batting lineup for this team
          dlup: Shared defensive lineup for the opposing team
        '''
        myname = 'HalfGame.ctor'
        dbg = 0
        self.__counter = counter
        self.__team_bat = team_bat
        self.__team_field = team_field
        self.__olup = olup       # Batting lineup.
        self.__dlup = dlup       # Defensive lineup
        self.__frames = {}       # Initial frames indexed by inning (one per batter)
        self.__frame = None      # Current or last frame.
        self.__active = False    # True if we are in an active inning.
        self.__inning_runs = {}  # Runs indexed by inning
        self.ostats = ostats
        self.dstats = dstats
        self.__nerror = 0

    def counter(self):
        '''Return the indexer.'''
        return self.__counter

    def nerror(self):
        '''Return the error count.'''
        return self.__nerror

    def team(self):
        '''Return the batting team name.'''
        return self.__team_bat

    def team_field(self):
        '''Return the defense team name.'''
        return self.__team_field

    def index(self):
        '''Return the current index.'''
        return self.counter().get()

    def lineup(self, idx=None):
        '''Return the batting lineup.'''
        return self.__olup
        
    def lineup_map(self, idx=None):
        '''Return the map of player numbers indexed by batting position.'''
        if self.__olup is None: return {}
        return self.__olup.get(idx)
        
    def defensive_lineup(self):
        '''Return the defense lineup.'''
        return self.__dlup

    def defense(self, idx=None):
        '''Return the map of player numbers indexed by field position.'''
        if self.__dlup is None: return {}
        return self.__dlup.get(idx)
        
    def is_valid(self, verbose=True):
        '''Return if this is a valid half game.'''
        if self.counter() is None:
            if verbose: print(f"ERROR: Counter is not specified.")
            return False
        if self.lineup() is None:
            if verbose: print(f"ERROR: Lineup is not specified.")
            return False
        if self.lineup().length() < 8:
            if verbose: print(f"ERROR: Lineup has too few players.")
            return False
        return True

    def is_active(self):
        '''Return if an inning is in progress.'''
        return self.__active

    def innings(self):
        '''Return the list of innings'''
        return list(self.__frames.keys())

    def inning(self):
        '''Return the the current inning if active or last inning.'''
        return len(self.__frames)

    def inning_frames(self, a_inning=None):
        '''Return the (ordered) array of frames for an inning.'''
        if a_inning == None: inning = self.inning()
        if inning not in self.__frames: return []
        return self.__frames[inning].inning_frames()

    def frame(self):
        '''Return the frame for the current or last batter.'''
        if len(self.__frames) == 0: return None
        return self.inning_frames()[-1]

    def last_frame(self, ing):
        '''Return the last frame for inning ing.'''
        if ing not in self.__frames: return None
        return self.__frames[ing].following_frames()[-1]

    def inning_runs(ing):
        '''Return the number of runs scored in inning ing.'''
        if ing not in self.__inning_runs: return 0
        return self.__inning_runs[ing]

    def runs(self):
        '''Return the total number of runs scored.'''
        nrun = 0
        for irun in self.__inning_runs.values():
            nrun += irun
        if self.inning() > len(self.__inning_runs):
            nrun += self.frame().inning_runs()
        return nrun

    def start_inning(self):
        '''Start a new inning and return that inning number.'''
        myname = 'HalfGame.start_inning'
        dbg = 0
        if self.is_active():
            print(f"{myname}: ERROR: Inning is already in progress.")
            return None
        self.counter().next()
        self.__active = True
        self.__frame = None
        last_ing = len(self.__frames)
        ing = last_ing + 1
        if dbg: print(f"{myname}: Starting {self.team()} inning {ing}")
        assert( ing not in self.__frames )
        self.__frames[ing] = None
        assert( self.inning() == ing )
        return ing

    def end_inning(self, reason=None):
        myname = 'HalfGame.end_inning'
        dbg = 0
        if dbg: print(f"{myname}: Ending {self.team()} inning {self.inning()}")
        if not self.is_active():
            print(f"{myname}: ERROR: Inning is not in progress.")
            return None
        # If inning ended properly but unusually, close all the frames.
        check_outs = True
        if reason in ['MERCY', 'TIME', 'WALKOFF']:
            self.frame().end_inning()
            check_outs = False
        # Check the frames.
        ing = len(self.__frames)
        assert( self.inning_frames() == self.frame().inning_frames() )
        nout = 0
        for frm in self.inning_frames():
            idesc = f"{self.team()} inning {ing}"
            fdesc = f"{idesc} frame {frm.lineup_position()} player {frm.player()}"
            if frm.is_active():
                print(f"{myname}: ERROR: {fdesc} is active.")
                self.__nerror += 1
            if frm.out(): nout += 1
        if check_outs and nout != 3:
            print(f"{myname}: ERROR: {idesc} has {nout} outs")
            self.__nerror += 1
        if dbg:
            for frm in self.inning_frames():
                print(f"{myname}:   {frm.lineup_position():2d} out:{frm.out()} scored:{frm.scored()}")
        # Collect the runs.
        assert( ing == self.inning() )
        assert( ing not in self.__inning_runs )
        self.__inning_runs[ing] = self.frame().inning_runs()
        self.counter().next()
        self.__active = False
        self.__frame = None
        
    def start_batter(self, isxir=False):
        '''
        Start a new batter and return that frame.
        If isxir is true, then use the batter that ended the last inning
        and place him on second base.
        '''
        myname = 'HalfGame.start_batter'
        if not self.is_active():
            print(f"ERROR: Inning is not started.")
            return None
        self.counter().next()
        ing = self.inning()
        ipos = None    # Lineup position of the new batter
        # First batter of the inning.
        if self.__frame is None:
            assert( self.__frames[ing] is None )
            lasting = ing - 1
            lastfrm = self.last_frame(lasting)
            if lastfrm is None:
                ipos = 1
                assert(not isxir)
            elif lastfrm.left_atbat() or isxir:
                ipos = lastfrm.lineup_position()
        # Not the first batter of the inning.
        else:
            assert(not isxir)
            lastfrm = self.frame()
        if ipos is None:
            lastpos = lastfrm.lineup_position()
            ipos = lastpos % self.lineup().length() + 1
        player = self.lineup().get_player(ipos)
        if player is None:
            print(f"{myname}: WARNING: No player found for position {ipos}")
            self.lineup().display()
            assert(False)
        lastfrm_ing = None if self.__frame is None else lastfrm
        frm = Frame(self, ipos, player, self.ostats, self.dstats, lastfrm_ing)
        if isxir:
            frm.advance_base()
            frm.advance_base()
        self.__frame = frm
        if self.__frames[ing] is None: self.__frames[ing] = frm
        self.ipos = ipos
        return frm

class Game:
    '''
    A game holds home and visitor half games.
       data - string rep of date
       vname - Name of visiting team
       hname - Name of visiting team
       vbat - batting lineup of visiting team
       hbat - batting lineup of hiome team
       vdef - defensive lineup of visiting team
       hdef - defensive lineup of home team
       counter - index counter
    Lineups may be arrays of player numbers or the number of players.
    Defaults are for all are 9.
    '''

    def __init__(self, atts, vname, hname, vbat=9, vdef=9, hbat=9, hdef=9, counter=None):
        self.__counter = Counter() if counter is None else counter
        self.title    = '' if 'title'    not in atts else atts['title']
        self.date     = '' if 'date'     not in atts else atts['date']
        self.location = '' if 'location' not in atts else atts['location']
        self.holup = Lineup(f"{hname} batting", self.counter(), hbat)
        self.hdlup = Lineup(f"{hname} defense", self.counter(), 9)
        self.volup = Lineup(f"{vname} batting", self.counter(), vbat)
        self.vdlup = Lineup(f"{vname} defense", self.counter(), 9)
        self.hstats = GameStats(self.holup, self.hdlup, hname)
        self.vstats = GameStats(self.volup, self.vdlup, vname)
        self.home    = HalfGame(self.counter(), hname, vname, self.holup, self.vdlup, self.hstats, self.vstats)
        self.visitor = HalfGame(self.counter(), vname, hname, self.volup, self.hdlup, self.vstats, self.hstats)
        self.__index = 0
        self.__homebat = None    # current if active or last if not.
        self.__active = False
        self.__call_reason = ''   # Reason if game is called MERCY, TIME, ...
        self.expected_inning_count = 7
        self.error = 0            # Set nonzero to indicate any error

    def counter(self):
        '''Return the indexer.'''
        return self.__counter

    def index(self):
        '''Return the current index.'''
        return self.counter().get()

    def next_index(self):
        '''Increment and return the index.'''
        return self.counter().next()

    def nerror_game(self):
        '''Return the number of errors in processing the game.'''
        return self.home.nerror() + self.visitor.nerror()

    def nerror_stats(self):
        '''Return the number of errors in evaluating the stats.'''
        return self.hstats.nerror() + self.vstats.nerror()

    def nerror(self):
        '''Return the total number of errors.'''
        return self.nerror_game() + self.nerror_stats()

    def is_active(self):
        '''Return if game is active: started and not ended or between innnings.'''
        return self.__active

    def is_home_atbat(self):
        '''Return if the home team is at bat.'''
        return self.is_active() and self.__homebat

    def atbat_label(self):
        '''Returns 'home', 'visitor' or 'none'''
        if not self.is_active(): return 'none'
        if self.is_home_atbat(): return 'home'
        return 'visitor'
       
    def half_inning_label(self):
        '''Returns 'top', 'bottom' of 'none'.'''
        if not self.is_active(): return 'none'
        if self.is_home_atbat(): return 'bottom'
        return 'top'
       
    def teams(self):
        '''Return (label, half-game) tuples for the two teams.'''
        return [('Home', self.home), ('Visitor', self.visitor)]

    def teamstats(self, team ='Wildcats'):
        if self.home.team() == team: return self.hstats
        if self.visitor.team() == team: return self.vstats
        return None

    def atbat(self):
        '''Return half-game for the at-bat team.'''
        if self.is_active():
            if self.__homebat: return self.home
            else: return self.visitor
        return None
        
    def labeled_atbat(self):
        '''Return (label, half-game) for the at-bat team.'''
        if self.is_active():
            if self.__homebat: return ('Home', self.home)
            else: return ('Visitor', self.visitor)
        return None
        
    def start_game(self):
        '''Starts the game. Batter up.'''
        return start_half_inning()

    def start_half_inning(self, index=None):
        '''Starts the next half inning.'''
        if self.is_active():
            print(f"ERROR: Half inning is already in progress.")
            return None
        self.__active = True
        if self.__homebat is None or self.__homebat:
            self.__homebat = False
        else:
            self.__homebat = True
        atbat = self.atbat()
        frame = atbat.start_inning()
        assert(atbat.is_active())
        return frame

    def end_half_inning(self, reason=None, index=None):
        '''Ends the current half inning.'''
        myname = 'Game.end_half_inning'
        dbg = 0
        if not self.is_active():
            print(f"{myname}: ERROR: Half inning is not in progress.")
            return None
        self.atbat().end_inning(reason)
        self.__active = False
        if dbg: print(f"{myname}: Score is {self.score()}")

    def next_batter(self):
        return self.atbat().start_batter()

    def inning(self):
        '''Return the current inning.'''
        return self.atbat().inning()

    def score(self):
        '''Return the score as string 'NV-NH'.'''
        return str(self.visitor.runs()) + '-' + str(self.home.runs())

    def is_complete(self):
        '''Return if the game is complete.'''
        reas = ''
        if self.is_active(): reas = 'Frame is active.'
        if len(self.call_reason()): return True
        ein = self.expected_inning_count
        nrv = self.visitor.runs()
        nrh = self.home.runs()
        if nrv == nrh: reas = "Tie game."
        niv = len(self.visitor.innings())
        nih = len(self.home.innings())
        if niv < ein: reas = f"Visitor innings < {ein}"
        if nrh > nrv:
            if nih < ein - 1: reas = f"Home innings < {ein-1}"
        else:
            if nih < ein: reas = f"Home innings < {ein}"
        self.reason = reas
        return reas == ''

    def call(self, reason):
        '''Call the game, i.e. end it early for specified reason, e.g. MERCY or TIME.'''
        if self.is_active(): self.end_half_inning()
        self.__call_reason = reason

    def call_reason(self):
        '''Return the reason why game was called.'''
        return self.__call_reason
