# lineup.py
#
# David Adams
# May 2022
'''
Lineup for bbstat.
Each position (can be battting or defense) is a map so the
lineup can be returned for any index.
'''

from bbstat import Counter

class Lineup:

    @classmethod
    def decode(cls, line):
        '''
        Decode a string description of a player or list of players with format
            POS - position number, or
            #PLA - PLA = player number
            #PLA(NAME) - player number and name NAME, or
            POS#PLA, or
            POS#(NAME), or
            POS#PLA(NAME), or
            PP1, PP2, ... (PPi is any of the above), or
            [PP1, PP2, ...]
        Returns a list of tuples (POS, PLA, NAME) for each player
        with missing values recorded as None.
        '''
        myname = 'Lineup.decode'
        dbg = 0
        if line[0] == '[' and line[-1] == ']':
            line = line[1:-1]
        words = line.split(',')
        nset = 0
        nerr = 0
        out = []
        for word in words:
            pos = None
            num = None
            name = None
            word = word.strip()
            posnum = word.split('#')
            spos = posnum[0]
            if len(spos): pos = int(spos)
            if len(posnum) > 1:
                 numnam = posnum[1].split('(')
                 snum = numnam[0]
                 if len(snum) > 0:
                     num = int(snum)
                 if len(numnam) > 1:
                     snam = numnam[1].split(')')
                     if len(snam) == 2 and len(snam[1]) == 0:
                         name = snam[0]
                     else:
                         print(f"{myname}: WARNING: Ignoring invalid name in {word}")
            out.append((pos, num, name))        
        return out

    def __init__(self, title, counter, lineup):
        '''
        Create a lineup.
        Shared counter must be provided.
        Input lineup can be None, a count or an array of player numbers.
        '''
        myname = 'Lineup::ctor'
        self.__title = title
        self.__counter = counter
        self.__data = []
        if not isinstance(self.__counter, Counter):
            print(f"{myname}: ERROR: Counter must be provided.")
        if lineup is None:
            pass
        elif type(lineup) is int:
            for ival in range(lineup):
                self.__data.append({})
        else:
            idx = self.__counter.get()
            for ival in range(len(lineup)):
                self.__data.append({idx:lineup[ival]})

    def __str__(self):
        sout = f"Lineup {self.title()}"
        for kpos in range(self.length()):
            ipos = kpos + 1
            player = self.get_player(ipos)
            if player is None:
                sout += f"\n{ipos:4d}:   ?"
            else:
                sout += f"\n{ipos:4d}: {player:3d}"
        return sout

    def title(self):
        return self.__title

    def length(self):
        '''Return the current number of players in the lineup.'''
        return len(self.__data)

    def get_player(self, ipos, idx=None):
        '''
        Fetch a player number for a given position and index.
          ipos - position in the lineup starting at 1.
          idx - Game index. None for current.
        '''
        kpos = ipos - 1
        if kpos < 0: return None
        if kpos >= self.length(): return None
        return Counter.find(self.__data[kpos], idx)

    def get_lineup(self, idx=None):
        '''
        Return the lineup map for an index.
        None returns the current value.
        Player for position ipos is lineup[ipos].
        '''
        lineup = {}
        for kpos in range(self.length()):
            lineup[kpos+1], key = Counter.find_with_key(self.__data[kpos], idx)
        return lineup

    def has_position(self, pos, idx=None):
        '''
        Return if position number pos is in the lineup for index idx.
        Does not gurantee a player is assigned to the position.
        '''
        lineup = {}
        if pos < 1 : return False;
        if pos > self.length(): return False

    def has_player(self, num, idx=None):
        '''
        Return if player number num is in the lineup for index idx.
        '''
        lineup = {}
        for kpos in range(self.length()):
            lnum = Counter.find_with_key(self.__data[kpos], idx)
            if lnum == num: return True
        return False

    def set(self, ipos, player, idx=None, add=False, reset=False):
        '''
        Set a player for a given position and index.
        If the index is None, the current counter value is used.
        If add is true then positions will be added if needed.
        If reset is true, then an entry is added even if the player
        is already in the postion.
        '''
        myname = 'Lineup::set'
        dbg = 0
        assert( ipos > 0 )
        kpos = ipos - 1
        if idx is None:
            idx = self.__counter.get()
        if kpos >= len(self.__data):
            if not add:
                print(f"{myname}: Cannot add player {player} to position {ipos}")
                return 1
            while self.length() <= kpos:
                self.__data.append({})
        if not reset and self.get_player(ipos, idx) == player:
             return 0
        self.__data[kpos][idx] = player

    def set_from_string(self, line):
        '''
        Set one or more positions from a string with format
            POS#PLA (POS=position #, PLA=player numnber) or
            POS#PLA(NAME) (NAME is player name) or
            PP1, PP2, ... (PPi is either of the above) or
            [PP1, PP2, ...] or
        '''
        myname = 'Lineup.set_from_string'
        dbg = 0
        nset = 0
        nerr = 0
        for pos, num, nam in self.decode(line):
            if self.set(pos, num):
                nerr = nerr + 1
                print(f"{myname}: WARNING: Error setting player {num} in position {pos}")
            else:
                nset = nset + 1
                if dbg: print(f"{myname}: Set player {num} in position {pos}")
        return nerr, nset

    def display(self):
        print(f"{self.title()}:")
        for kpos in range(self.length()):
            ipos = kpos + 1
            player = self.get_player(ipos)
            if player is None:
                print(f"{ipos:4d}:   ?")
            else:
                print(f"{ipos:4d}: {player:3d}")
