# frame.py

from collections import OrderedDict
from bbstat import AtBatResult
from bbstat import Counter

class Frame:
    '''
    A frame corresponds to a box on a score sheet.
    It describes the progress of one player's at-bat
    It has a list of pitches and a list of results and substitions.
    at-bat, advance on the base paths or out.
      pitches - array with b=ball, c=called strike, l=looking strike
      pitch_idxs - Map of pitch indexes
      actions - array of actions after the pitches, starting with the at-bat result
      action_idxs
      players - Player numbers original and substitutes.
      base - Current base: 0 is at bat, 1-3 is occupied base, 4 is scored, 5 is out
    '''

    def __init__(self, halfgame, lineup_position, player, ostats, dstats, frame_last=None):
        '''
        Create a new frame.
          lineup_position - Position in the batting lineup: 1, 2, ..., nbatter
          player - Player number.
          index - Index when player came up to bat.
        '''
        self.__halfgame = halfgame
        self.__index_start = self.counter().get()   # Index when frame was created.
        self.__index_end = None              # Index when frame closed (out or end of inning).
        self.__ipos = lineup_position
        self.__players = {self.counter().get():player}
        self.__pitches = {}
        self.__actions = {}
        self.__tagactions = {}        # Unhandled tagged actions: lists indexed by tag.
        self.__bases = {self.__index_start:0}
        self.__out = 0                # Inning out (1-3 if this frame made an out)
        self.tag_last = None          # Latest tag
        self.frame_last = frame_last  # Preceding frame in the inning
        self.frame_next = None        # Following frame in the inning
        if self.frame_last is not None:
            self.frame_last.frame_next = self
        self.ostats = ostats
        self.dstats = dstats
        

# Getters.

    def __str__(self):
        sout = ''
        for pitch in self.__pitches: sout += pitch
        for action in self.__actions:
            sout += ':' + str(action)
        return sout

    def halfgame(self):
        return self.__halfgame

    def defense_player(self,ipos):
        '''Get the current player number for defense position number ipos.'''
        return halfgame().defensive_lineup().get_player(ipos)

    def pitcher(self,ipos):
        '''Get the current pitcher.'''

    def counter(self):
        '''Return the indexer.'''
        return self.halfgame().counter()

    def player(self, idx=None):
        '''Return the current player.'''
        return Counter.find(self.__players, idx)

    def is_active(self, idx=None):
        '''
        Return if the is frame is active, i.e. the player is at
        bat or on base.
        If not active, the player scored, was out or was left on
        base or at bat when the inning ended.
        '''
        if self.__index_end is None: return True
        if idx is None: return False
        return idx < self.__index_end

    def pitch_count(self, idx=None):
        '''Return the pitch count: (total, ball, strike)'''
        chk = idx is not None
        nball = 0
        nstri = 0
        for key, pit in self.__pitches.items():
            if chk and key > idx: break
            if pit == 'b': nball += 1
            else: nstri += 1
        return nball+nstri, nball, nstri

    def base(self, idx=None):
        '''
        Return the occupied base.
          0 - at bat
          1-3 - on base
          4 - scored
        '''
        bas = Counter.find(self.__bases, idx)
        if bas is None:
            print(f"{myname}: WARNING: No base found for index {idx} with bases {self.__bases}")
            bas = 0
        return bas
        
    def scored(self, idx=None):
        '''Scored a run.'''
        return self.base(idx) > 3

    def lob(self):
        '''Left on base'''
        if self.is_active(): return False
        base = self.base()
        return base > 0 and base < 4

    def out(self):
        '''Return out made 1-3. 0 for no out.'''
        return self.__out

    def atbat(self):
        '''
        Return if the frame is at bat.
        '''
        return self.is_active() and self.base() == 0

    def preceding_frames(self, __frms=None):
        '''
        Return the frames preceding this starting from the latest.
        '''
        frms = __frms
        if frms is None: frms = []
        if self.frame_last is None:
            return frms
        frms.append(self.frame_last)
        return self.frame_last.preceding_frames(frms)

    def following_frames(self, idx=None, __frms=None):
        '''
        Return the frames following this before index idx starting
        from the next frame.
        Index None means all current frames.
        '''
        frms = __frms
        if frms is None: frms = []
        if self.frame_next is None:
            return frms
        if idx is not None and self.frame_next.__index_start > idx:
            return frms
        frms.append(self.frame_next)
        return self.frame_next.following_frames(idx,  frms)

    def inning_frames(self, idx=None):
        '''
        Return all frames in this inning before index idx starting
        from the first.
        Index None means all current frames.
        '''
        frames = []
        frm = self
        while frm.frame_last is not None: frm = frm.frame_last
        while frm is not None:
            frames.append(frm)
            frm = frm.frame_next
        return frames

    def inning_out_frame_map(self, idx=None):
        '''
        Return a dictionary of frames making outs indexed by out number.
        '''
        myname = 'Frame.inning_out_frame_map'
        dbg = 0
        outs = {}
        for frm in self.inning_frames():
            out = frm.out()
            ipos = frm.lineup_position()
            if dbg: print(f"{myname}: Frame {ipos} out is {out}")
            if out:
                if frm.is_active(idx):
                    print(f"{myname}: WARNING: Ignoring out because frame is active.")
                    continue     # Out hasn't been made yet
                if frm.out in outs:
                    print(f"{myname}: WARNING: Ignoring duplicate out {out}.")
                    continue
                outs[out] = frm
        if dbg: print(f"{myname}: Returning {len(outs)} outs.")
        return outs

    def inning_out_frame(self, out, idx=None):
        '''
        Return the frame making out out.
        Returns None if the out was not made.
        '''
        ofrms = self.inning_out_frame_map(idx)
        if out in ofrms:
            return ofrms[out]
        return None

    def inning_outs(self, idx=None):
        '''
        Return the number of outs made in the inning.
        '''
        myname = 'Frame.inning_outs'
        dbg = 0
        outs = list(self.inning_out_frame_map(idx).keys())
        outs.sort()
        nout = len(outs)
        if dbg: print(f"{myname}: Returning {nout} outs.")
        if outs != list(range(1,nout+1)):
            print(f"{myname}: WARNING: Out values are inconsistent: {outs}")
            print(self.inning_out_frame_map(idx))
            assert(False)
        return nout
        
    def inning_runs(self, idx=None):
        '''Return the number of runs scored in the inning.'''
        myname = 'Frame.inning_runs'
        dbg = 0
        nrun = 0
        if dbg: print(f"{myname}: Checking inning runs.")
        for frm in self.inning_frames():
            if frm.scored(idx):
                nrun += 1
                if dbg: print(f"{myname}:   Position {frm.lineup_position():2d} scored")
            else:
                if dbg: print(f"{myname}:   Position {frm.lineup_position():2d} did not score")
        if dbg: print(f"{myname}: Run count is {nrun}.")
        return nrun

    def inning_base_frame(self, base, idx=None):
        '''
        Return the frame on base base at index idx.
        Return None for error or if base is unoccupied.
        '''
        myname = 'Frame.inning_base_frame'
        if base < 0 or base > 3:
            print("{myname}: ERROR: Cannot check base {base}")
            return None
        bfrm = None
        for frm in self.inning_frames():
            if frm.base(idx) == base:
                if bfrm is not None:
                     print("WARNING: Ignoring earlier player on base.")
                bfrm = frm
        return bfrm

    def left_atbat(self):
        '''
        Return if this frame was left at bat when the inning ended.
        I.e. if this batter should bat again at the top of the next inning.
        '''
        if self.is_active(): return False
        return len(self.__actions) == 0

    def left_onbase(self):
        '''
        Return if this frame was left at bat when the inning ended.
        I.e. if this batter should bat again at the top of the next inning.
        '''
        if self.is_active(): return False
        bas = self.base()
        return bas>0 and bas<4

# Setters.

    def set_out(self, out):
        myname = 'Frame.set_out'
        dbg = 0
        if dbg: print(f"{myname}: Setting player {self.player()} out.")
        if not self.is_active():
            print(f"ERROR: Cannot set out for an inactive frame.")
            return 1
        assert(self.__out == 0)
        ofrm = self.inning_out_frame(out)
        if ofrm is not None:
            print(f"{myname}: ERROR: Out {out} was already made by player {ofrm.player()}.")
            return 2
        self.__out = out
        self.__index_end = self.counter().get()
        self.dstats.increment_pitch_stat('ino')
        return 0

    def advance_base(self, nbase=1):
        '''
        Advance the frame by nbase bases.
        '''
        myname = 'Frame.advance_base'
        dbg = 0
        if not self.is_active():
            print(f"{myname}: Cannot advance player who is inactive.")
            return 1
        if self.base() > 3:
            print(f"{myname}: Cannot advance player who has scored")
            return 2
        base = self.base() + nbase
        if dbg>1: print(f"{myname}: Position {self.lineup_position()} player {self.player()}" \
                        f" advanced {nbase} bases to base {base}")
        if base >= 4 and nbase > 0:
            self.ostats.increment_player_bat_stat(self.player(),'run')
            self.dstats.increment_pitch_stat('run')
            if dbg: print(f"{myname}: Position {self.lineup_position()} player {self.player()}" \
                          f" is credited with a run.")
        if base > 4:
            print(f"WARNING: Advanced past home to {self.base()}")
            base = 4
        idx = self.counter().get()
        self.__bases[idx] = base
            
    def pitch(self, spits, action=''):
        '''
        Throw one or more pitches followed by an optional action.
          b - Ball
          c - Called strike
          s - Swinging strike
          f - Foul ball
        Counter is incremented before pitches are recorded.
        '''
        myname = 'Frame.pitch'
        dbg = 0
        if dbg: print(f"{myname}: Handling pitches {spits} and action {action}")
        self.counter().next()
        if not self.atbat():
            print(f"ERROR: Pitch thrown to player not at bat.")
            return 1
        nb = 0
        nk = 0
        for spit in spits:
            if spit not in AtBatResult.pitch_types():
                print(f"ERROR: Invalid pitch type: {spit}")
                return 2
            if spit == 'b': nb += 1
            else:           nk += 1
        self.dstats.increment_pitch_stat('b', nb)
        self.dstats.increment_pitch_stat('s', nk)
        idx = self.counter().next()
        self.__pitches[idx] = spits
        if len(action):
            self.add_action(action)
        return 0

    def add_action(self, action, dotag=False, update_counter=True):
        '''
        Add an action.
          action - the action to add
          dotag - If true on-base tagged actions are carried out. Otherwise, they are
                  recorded in the on-base action map.
        A frame is tagged after it receives its first counter tag.
        On-base actions.
          SB = Stolen base
          WP = Wild pitch
          SB = Passed ball
          T = Advance on throw
          B:A = Add action A to the player on base B
          A1,A2,... = Add actions A1, A2, ...
        '''
        myname = 'Frame.add_action'
        dbg = 0
        idx = self.counter().get(update_counter)
        ipos = self.lineup_position()
        myname = f"{myname}: Frame {ipos}"
        if len(action) == 0:
            print(f"{myname}: ERROR: Action string is empty.")
            return 1
            
        isout = False
        # Handle multiple actions.
        acts = action.split(',')
        if len(acts) > 1:
            if dbg: print(f"{myname}: Splitting action {action}")
            for act in acts:
                ret = self.add_action(act, dotag, False);
                if ret:
                    print(f"{myname}: ERROR: Subaction {act} in action {action} failed.")
                    return ret
            return 0
        # An action that starts with '@' is a tag reference. Use it to build the tag name
        # and then carry out all actions associated with that name.
        if action[0] == '@':
            tag = str(self.lineup_position())
            if len(action) > 1:
                tag += '.' + action[1:]
            counts = [0,0]
            for frm in self.preceding_frames():
                frm.add_tag_actions(tag, counts)
            if counts[1] != 0:
                print(f"{myname}: ERROR: Errors occured handling actions for tag {tag}.")
                return 1
            if counts[0] == 0:
                print(f"{myname}: ERROR: No actions found for tag {tag}.")
                return 1
            if dbg: print(f"{myname}: Tag {tag} action count is {counts[0]}")
            return 0
        # If the action starts with a tag, record it and strip it off.
        tag = None
        baseact = action.split(':')
        if action[0] == '<':
            # Do not record a new tag if the action is being handled.
            if dotag:
                print(f"{myname}: ERROR: Tag included in handled on-base action {action}")
                return 1 
            tagact = action[1:].split('>')
            if len(tagact) != 2:
                print(f"{myname}: ERROR: Invalid on-base action: {action}")
                return 1 
            tag = tagact[0]
            self.tag_last = tag
            if tag not in self.__tagactions:
                self.__tagactions[tag] = []
            action = tagact[1]
        # Otherwise, use the latest tag.
        # Except end-only actions are recorded there.
        elif len(self.__tagactions):
            if action in ['LOB', 'LAB']: tag = 'end'
            else: tag = self.tag_last
        # If the frame is tagged and dotag is False, then record the action instead
        # of handling it.
        if tag is not None and not dotag:
            if dbg: print(f"{myname}: Recording action {action} with tag {tag}")
            if tag not in self.__tagactions:
                self.__tagactions[tag] = [action]
            else:
                self.__tagactions[tag].append(action)
            return 0
        # Handle the action.
        if dbg: print(f"{myname}: Handling action {action}")
        # Handle onbase action.
        if action in ['SB', 'DI', 'WP', 'PB', 'T', 'AD', 'BALK']:
            if self.atbat():
                print(f"{myname}: ERROR: On-base action {action} requested for player at-bat.")
                return 5
            if action == 'SB':
                self.ostats.increment_player_bat_stat(self.player(),'sb')
            elif action in ['PB', 'WP']:
                self.ostats.increment_player_bat_stat(self.player(),'pbw')
            if action == 'WP':
                self.dstats.increment_pitch_stat('wpa')
            oldbase = self.base()
            if self.advance_base(): return 1
            newbase = self.base()
            if dbg: print(f"{myname}: Player advanced from base {oldbase} to base {newbase}")
            self.__actions[idx] = action
            return 0
        # Handle check of at bat.
        if action == 'ATBAT':
            if not dotag:
                self.__tagactions['end'] = action
                return 0
            if self.atbat(): return 0
            pos = self.lineup_position()
            print(f"{myname}: ERROR: Frame {pos} is not at bat.")
            return 1
        # Handle check of left at bat at then end of the inning.
        # Inning may not be over, e.g. mercy.
        if action == 'LAB':
            if self.atbat() or self.left_atbat(): return 0
            pos = self.lineup_position()
            print(f"{myname}: ERROR: Frame {pos} is not left at bat.")
            return 1
        # Handle check of left on base at the end of the inning.
        if action == 'LOB':
            if not dotag:
                if 'end' not in self.__tagactions:
                    self.__tagactions['end'] = [action]
                else: self.__tagactions['end'].append(action)
                return 0
            if self.left_onbase(): return 0
            print(f"{myname}: ERROR: Frame is not left on base.")
            return 1
        # Handle check of scored.
        if action[0:3] == 'RUN':
            if self.scored(): return 0
            print(f"{myname}: ERROR: Frame did not score.")
            return 1
        # Handle check of outs.
        if action[0:3] == 'OUT':
            if action[0:5] == 'OUTS:':
                assert( len(action) == 6 )
                chkout = int(action[5])
                if chkout != self.inning_outs():
                    print(f"{myname}: ERROR: Inconsistent inning out counts: {chkout} != {self.out()}")
                    return 1
            else:
                assert( len(action) == 4 )
                chkout = int(action[3])
                if chkout != self.out():
                    print(f"{myname}: ERROR: Inconsistent out counts: {chkout} != {self.out()}")
                    return 1
            return 0
        # Handle check of base.
        if action[0] == '[':
            if len(action) != 3 or action[2] != ']' or not action[1].isdigit():
                print(f"{myname}: ERROR: Invalid base check action: {action}")
                return 1
            base = int(action[1])
            if base != self.base():
                print(f"{myname}: ERROR: Expected base is incorrect: {base} != {self.base()}")
                return 1
            return 0
        # Handle RBI.
        if action == 'RBI':
            if dbg:
                print(f"{myname}: Handling RBI.")
            self.ostats.increment_player_bat_stat(self.player(),'rbi')
            return 0
        # Handle no RBI.
        if action == 'NORBI':
            if dbg:
                print(f"{myname}: Handling NORBI.")
            return 0
        # Handle productive out.
        if action == 'PO':
            if dbg:
                print(f"{myname}: Handling PO.")
            return 0
        # Handle double play.
        if action == 'DP':
            if dbg:
                print(f"{myname}: Handling DP.")
            return 0
        # Remainder require that player is active.
        if not self.is_active():
            print(f"{myname}: ERROR: Action {action} requested for a frame that is not active.")
            return 1
        # Handle pitches.
        if action[0:1] in AtBatResult.pitch_types():
            if not self.atbat():
                print(f"{myname}: Pitches {action} received when not at bat.")
                return 1
            sta = self.pitch(action)
            if sta: return sta
            return 0
        # Pitcher substitution.
        elif action[0:6] == 'PITCH#':
            pspec = '1#' + action[6:]
            dlup = self.halfgame().defensive_lineup()
            nerr, nset = dlup.set_from_string(pspec)
            if nerr:
                print(f"{myname}: ERROR: Unable to set pitcher with spec {pspec}")
            return nerr
        # Runner substitution.
        elif action[0:5] == 'RSUB#':
            if not self.is_active():
                print(f"{myname}: ERROR: Runner subsitution {action} requested for an inactive frame.")
                return 6
            if not self.base() in [1,2,3]:
                print(f"{myname}: ERROR: Runner substitution requested when not no base.")
                return 6
            num = int(action[5:])
            irun = int(action[5:])
            # Add runner to stats if needed.
            assert(self.ostats.have_batter(irun, add=True))
            self.__players[self.counter().get()] = num
        # Handle atbat action.
        else:
            if not self.is_active():
                print(f"{myname}: ERROR: At-bat action {action} requested for an inactive frame.")
                return 6
            res = AtBatResult(action)
            if res.valid:
                isout = res.batter_out
                iserr = len(res.errors) > 0
                # For player on base, the result must be an out or an error.
                oldbase = self.base()
                resbase = 0 if res.base is None else res.base
                advbase = resbase
                if oldbase:
                    if not isout and not iserr:
                        print(f"{myname}: ERROR: At-bat action {action} for a frame on base must be "
                              f"an out or an error.")
                        return 6
                    if iserr:
                        advbase = 1
                        resbase = oldbase + 1
                    if isout:
                        num = self.player()
                        if not self.ostats.have_batter(num):
                            print(f"{myname}: ERROR: On-base out made by unknown player number {num}")
                            return 1
                        self.ostats.increment_player_bat_stat(num,'obo')
                        self.dstats.increment_pitch_stat('rpo')
                        if 'CS' in res.causes:
                            self.ostats.increment_player_bat_stat(num,'cs')
                        del num
                if dbg: print(f"{myname}: At-bat result for action {action}: base={resbase}, "
                              f"isout={res.batter_out}")
                self.__actions[idx] = action
                if advbase:
                    self.advance_base(advbase)
                    if self.base() != resbase:
                        print(f"{myname}: ERROR: Action {action} advanced base {self.base()} " \
                              f"is not the expected {resbase}.")
                        return 7
                # Update batting stats if action is for a batter.
                if oldbase == 0:
                    self.ostats.increment_player_bat_stat(self.player(),'pa')
                    if res.is_k:
                        self.ostats.increment_player_bat_stat(self.player(),'k')
                        self.dstats.increment_pitch_stat('k')
                    if res.batter_out:
                        self.ostats.increment_player_bat_stat(self.player(),'out')
                        self.dstats.increment_pitch_stat('bpo')
                    if res.is_fc:
                        self.ostats.increment_player_bat_stat(self.player(),'fc')
                    if res.is_error:
                        self.ostats.increment_player_bat_stat(self.player(),'e')
                    if res.is_sacrifice_fly:
                        self.ostats.increment_player_bat_stat(self.player(),'sf')
                    if 'SAC' in res.causes:
                        self.ostats.increment_player_bat_stat(self.player(),'sac')
                    if res.is_walk:
                        self.ostats.increment_player_bat_stat(self.player(),'bb')
                        self.dstats.increment_pitch_stat('bb')
                    if res.is_hbp:
                        self.ostats.increment_player_bat_stat(self.player(),'hbp')
                        self.dstats.increment_pitch_stat('hbp')
                    if res.hit_base == 1:
                        self.ostats.increment_player_bat_stat(self.player(),'b1')
                    if res.hit_base == 2:
                        self.ostats.increment_player_bat_stat(self.player(),'b2')
                    if res.hit_base == 3:
                        self.ostats.increment_player_bat_stat(self.player(),'b3')
                    if res.hit_base == 4:
                        self.ostats.increment_player_bat_stat(self.player(),'hr')
                    if res.hit_base:
                        self.dstats.increment_pitch_stat('hit')
                    self.dstats.increment_pitch_stat('bf')
            else:
                print(f"{myname}: ERROR: Invalid atbat action: {action}")
                return 7
        # If we are out set the frame counter.
        if isout:
            nout_old = self.inning_outs()
            assert( nout_old >= 0 )
            assert( nout_old < 3 )
            self.set_out(nout_old + 1)
            nout = self.inning_outs()
            assert( nout == nout_old + 1 )
            if nout == 3:
                return self.end_inning()
        return 0

    def add_tag_actions(self, tag, counts=[0,0]):
        '''Execute all the actions for given tag.'''
        myname = 'Frame.add_tag_actions'
        dbg = 0
        ipos = self.lineup_position()
        if tag not in self.__tagactions:
            if dbg:
                print(f"{myname}: Frame {ipos} has no actions for tag {tag}.")
            return 0
        acts = self.__tagactions.pop(tag)
        if dbg:
            print(f"{myname}: Frame {self.lineup_position()} has {len(acts)} actions for tag {tag}.")
        for act in acts:
            ret = self.add_action(act, dotag=True)
            if ret: counts[1] += 1
            else: counts[0] += 1
        return counts[1]

    def end_inning(self):
        '''End the inning. Set all frames inactive for thsi inning.'''
        myname = 'Frame.end_inning'
        counts = [0,0]
        for frm in self.inning_frames():
            if frm.is_active(): frm.__index_end = self.counter().get() 
            frm.add_tag_actions('end', counts)
            tags = frm.__tagactions.keys()
            if len(tags):
                ipos = frm.lineup_position()
                print(f"{myname}: ERROR: Frame {ipos} has unhandled action tags: {tags}")
                return 1
        return 0

    def lineup_position(self):
        '''Return the lineup position of this frame (starts at 1).'''
        return self.__ipos

    def sequence(self):
        '''Return string with pitches and action sequence.'''
        sout = ''
        for pit in self.__pitches.values():
            sout += pit
        for act in self.__actions.values():
            if len(sout): sout += ' '
            sout += act
        return sout

    def get_onbase_frame(self, base, idx=None):
        '''
        Return the preceding frame with a player on the indicated base
        for counter index idx or current if idx is None.
        Returns None if the base is unoccupied.
        '''
        base_frames = []
        frm = self.frame_last
        while frm is not None:
            if frm.base(idx) == base:
                base_frames.append(frm)
            frm = frm.frame_last
        nfrm = len(base_frames)
        if nfrm == 0: return None
        if nfrm > 1:
            print(f"WARNING: There are mutiple players on base {base}")
        return base_frames[0]

