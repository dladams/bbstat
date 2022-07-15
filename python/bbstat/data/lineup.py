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

    def title(self):
        return self.__title

    def length(self):
        '''Return the current number of players in the lineup.'''
        return len(self.__data)

    def get_player(self, ipos, idx=None):
        '''
        Fetch a player number for a given position..
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
        if line[0] == '[' and line[-1] == ']':
            line = line[1:-1]
        words = line.split(',')
        nset = 0
        nerr = 0
        for word in words:
            posnum = word.strip
            posnum = word.split('#')
            if len(posnum)== 2:
                 ipos = int(posnum[0])
                 num = int(posnum[1].split('(')[0])   # For now, ignore the name
                 if self.set(ipos, num):
                     nerr = nerr + 1
                     print(f"{myname}: WARNING: Error setting player {num} in position {ipos}")
                 else:
                     nset = nset + 1
                     if dbg: print(f"{myname}: Set player {num} in position {ipos}")
            else:
                print(f"{myname}: WARNING: Ignoring invalid position field: {word}")
                nerr = nerr + 1
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
