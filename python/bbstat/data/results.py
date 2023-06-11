# results.py

class AtBatResult:
    """Describes the results of an at-bat."""
    

    @staticmethod
    def pitch_types():
        """
        Return the list of supported pitch types.
          b=ball, c=called strike, f=foul, s=swing (strike or in play)
        """
        return ['b', 'c', 's', 'f']

    @staticmethod
    def getpos(val):
        """
        If val is a position number (1-9), return that integer.
        Otherwise return 0.
        """
        try:
            ival = int(val)
            if ival > 0 and ival < 10: return ival
            return 0
        except:
            return 0


    def __init__(self, labc):
        """
        Describes the consequences of an an at-bat or an on-base out.
          labc - label, label:cause or lab:cause1:cause2, etc.
        Labels include:
          I-J - Pos I threw to pos J.
          FI - Pos I caught a fly ball
          FFI - Pos I caught a foul fly ball
          LI - Pos I caught a line drive
          etc
        Causes incllude:
          AB - from the at bat. This is the cause if none is given.
          TO - Tag out. Player tagged after sucessfully reaching base.
          DP - Play is part oa a double play.
          CS - On-base runner caught stealing.
        Dropped 3rd strike options:
          WP:KD, E2:KD, 2-3:KD 
        Consequences are derived from the label, e.g. "HBP" or "6-3"
        Consequences are returned as member data:
          pitchs - allowed last pitchs (client may check this)
          base - Base reached by batter: 0 for none (out)
          batter_out - True if batter is out
          runner_out - True if put out after reaching 1st
          putouts - position numbers making putouts
          assists - postion numbers awarded assists
          errors - position numbers assigned errors
          excellent - true if first contact was excellent
          is_k - True if batter struck out whether or not reached base.
          is_fc - True if batter reached on fielder's choice.
          is_error - True if batter reached on an error.
          is_walk - True if batter walked.
          is_hbp - True if batter is hit by pitch.
          hit_base - Return the base reached with a hit: 1=1B, ..., 4=HR
        """
        myname = 'AtBatResult.ctor'
        words = labc.split(':')
        assert( len(words) > 0 )
        lab = words[0]
        self.label = lab
        if lab[-1] == '!':
            self.excellent = True
            lab = lab [0:-1]
        else:
            self.excellent = False
        self.causes = ['AB'] if len(words) < 2 else words[1:]
        self.valid = True
        self.pitchs = ''
        self.base = None
        self.batter_out = 0
        self.putouts = None
        assists = None
        self.errors = []
        self.is_sacrifice_fly = False
        self.is_k = lab[0]=='K' or self.causes[0]=='K'
        self.is_fc = lab=='FC'
        self.is_error = lab[0]=='E'
        self.is_walk = lab=='BB' or lab=="IBB"
        self.is_hbp = lab=='HBP'
        if   lab == '1B': self.hit_base = 1
        elif lab == '2B': self.hit_base = 2
        elif lab == '3B': self.hit_base = 3
        elif lab == 'HR': self.hit_base = 4
        else:             self.hit_base = 0
        len2 = len(lab) == 2
        len3 = len(lab) == 3
        len5 = len(lab) == 5
        len6 = len(lab) == 6
        len7 = len(lab) == 7
        pos = []   # Position number for each character in lab
        isd = []   # True if char is '-'
        for val in lab:
            pos.append(AtBatResult.getpos(val))
            isd.append(val == '-')
        dash = []   # True if char is '-'
        #print(f"XXXXX: lab is {lab}, len3 is {len3}, pos is {pos}")
        for val in lab:
            dash.append(val=='-')
        # Batter safe
        if   lab == 'BB': self.__set('b')
        elif lab == 'IBB': self.__set('bs')
        elif lab == 'WP': self.__set('bs')  # Batter may reach on dropped 3rd strike
        elif lab == 'PP': self.__set('bs')
        elif lab =='HBP': self.__set('b')
        elif lab == 'KD': self.__set('s')     # Dropped 3rd strike
        elif lab == 'CI': self.__set('s')
        elif lab == '1B': self.__set('s')
        elif lab == '2B': self.__set('s', 2)
        elif lab == '3B': self.__set('s', 3)
        elif lab == 'HR': self.__set('s', 4)
        elif lab == 'FC':
            self.__set('s', 1)
        elif len2 and lab[0] == 'E' and pos[1]:
            self.__set('s', 1)
            self.errors=([pos[1]])
        # Batter out
        elif lab =='OUT': self.__set_out('s')
        elif lab == 'KS': self.__set_out('s') 
        elif lab == 'KC': self.__set_out('c')
        elif lab == 'KL': self.__set_out('c')
        elif lab == 'BI': self.__set_out('s')
        elif lab == 'IF': self.__set_out('s')      # Infield fly
        elif lab ==  'K': self.__set_out('cs')
        elif lab =='K23': self.__set_out('cs', [3], [2])
        elif lab =='KC23': self.__set_out('c', [3], [2])
        elif lab =='KS23': self.__set_out('s', [3], [2])
        elif lab =='K2U': self.__set_out('cs', [2])
        elif lab =='KC2U': self.__set_out('c', [2])
        elif lab =='KS2U': self.__set_out('s', [2])
        elif len2 and lab[0] == 'L' and pos[1]:        # L7
            self.__set_out('s', [pos[1]])
        elif len2 and lab[0] == 'F' and pos[1]:        # F7
            self.__set_out('s', [pos[1]])
        elif len3 and lab[0:2] == 'FF' and pos[2]:     # FF7
            self.__set_out('s', [pos[2]])
        elif len3 and lab[0:2] == 'SF' and pos[2]:     # SF7
            self.__set_out('s', [pos[2]], sacfly=True)
        elif len3 and lab[0:2] == 'FO' and pos[2]:     # FO7
            self.__set_out('s', [pos[2]])
        elif len2 and lab[1] in ['u', 'U'] and pos[0]:        # 3U
            self.__set_out('s', [pos[0]])
        elif len3 and pos[0] and isd[1] and pos[2]:    # 6-3
            self.__set_out('s', [pos[2]], [pos[0]])
        elif len5 and pos[0] and isd[1] and pos[2] and isd[3] and pos[4]:   # 6-4-3
            self.__set_out('s', [pos[4]], [pos[0]], pos[2])
        else:
            self.valid = False

    def __set(self, pitchs, base=1):
        """Set state with defaults for runner reaching base."""
        self.batter_out = False
        self.pitchs = pitchs
        self.base = base

    def __set_out(self, pitchs, putouts=[], assists=[], outs=1, base=None, \
                errors=[], sacfly=False):
        """Set state for batter out."""
        self.batter_out = True
        self.pitchs = pitchs
        self.base = base
        self.outs = outs
        self.putouts = putouts 
        self.assists = assists
        self.errors = errors
        self.is_sacrifice_fly = sacfly
           
