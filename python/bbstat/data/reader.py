# reader.py

import bbstat

class Reader:
    '''
    Reads the text description of a game.
    '''

    def __init__(self, fnam, dbg=0):
        '''
        __fnam - Name of the file containing the game description.
        __game - Constructed game
        '''
        myname = 'Reader::ctor'
        self.__fnam = fnam        # Name of the file being read
        self.__game = None        # Game description
        self.__dbg = dbg
        self.nerr = 0
        dbg = self.__dbg
        fin = open(fnam, 'r')
        lines = fin.readlines()
        ilin = 0
        inning = 0
        athome = True
        frm = None
        in_inning = False
        nbat_inning = 0  # Number of batters in the inning
        gameatts = {}
        for line in lines:
            ilin += 1
            line = line.strip()
            if len(line) == 0: continue
            if dbg: print(f"{myname}: {ilin:3d}: {line}")
            # Pitching substitution.
            if line[0:6] == 'PITCH#':
                pspec = '1#' + line[6:]
                olup = self.game().atbat().defensive_lineup()
                nerr, nset = olup.set_from_string(pspec)
            # Adjust defensive lineup.
            elif line[0:4] == 'DLUP':
                word = line[4:]
                dlup = self.game().atbat().defensive_lineup()
                nerr, nset = dlup.set_from_string(word)
                pfx = 'ERROR: ' if nerr else ''
                if dbg or nerr:
                    print(f"{myname}: {pfx}Set {nset} defensive positions with {nerr} errors..")
                if nerr: return
            # Score check.
            elif line[0:6] == 'SCORE:':
                chk_score = line[6:]
                gam_score = self.game().score()
                if chk_score != gam_score:
                    print(f"{myname}: ERROR Expected and game scores differ: {chk_score} != {gam_score}")
                    self.nerr += 1
                    self.game().error += 1
                    return
            # Inning outs check.
            elif line[0:5] == 'OUTS:':
                if frm.add_action(line):
                    self.game.error = 11
                    return
            # Start a new inning.
            elif line[0:7] == 'Inning ':
                # Start game if needed.
                if self.game() is None:
                    self.__game = bbstat.Game(gameatts, visi, home, vbat, 9, hbat, 9)
                # End the previous inning.
                if in_inning:
                    assert( atbat is not None )
                    self.game().end_half_inning()
                # Start this inning.
                old_inning = inning
                old_athome = athome
                nbat_inning = 0
                shin = line[7:]
                inning = int(shin[0:-1])
                svh = shin[-1]
                if svh in 'hb': athome = True
                elif svh in 'vt': athome = False
                else:
                    print(f"{myname}: ERROR: Invalid inning specification {shin} on line {ilin}: {line}")
                    self.nerr += 1
                    return
                if athome:
                    sathome = 'home'
                    if old_athome:
                        print(f"{myname}: ERROR: At home specifier must follow visiting. Line {ilin}: {line}")
                        self.nerr += 1
                        return
                    if old_inning != inning:
                        print(f"{myname}: ERROR: Home inning mus match preceding visiting. Line {ilin}: {line}")
                        self.nerr += 1
                        return
                else:
                    sathome = 'visiting'
                    if not old_athome:
                        print(f"{myname}: ERROR: Visiting specifier must follow at home. Line {ilin}: {line}")
                        self.nerr += 1
                        return
                    if inning != old_inning + 1:
                        print(f"{myname}: ERROR: Visiting inning must increment. Line {ilin}: {line}")
                        self.nerr += 1
                        return
                    if dbg>1: print(f"{myname}: Starting inning {inning} for the {sathome} team.")
                # Start game inning if not already done.
                if not self.game().is_active():
                    ing = self.game().start_half_inning()
                    msg = ''
                    if ing < 1: msg = "Unable to start half inning."
                    if len(msg):
                        print(f"{myname}: ERROR: {msg} Line {ilin}: {line}")
                        self.nerr += 1
                        return
                assert( self.game().is_active() )
                in_inning = True

            # End the game (including current inning).
            elif line in ['MERCY', 'TIME', 'WALKOFF']:
                if self.game().is_active():
                    self.game().end_half_inning()
                else:
                    print(f"{myname}: Cannot end game during inning for reason {line}")
                    self.error += 1
                    return
                self.game().call(line)
            # End the game (including current inning).
            elif line == 'END':
                self.game().end_half_inning()
            # New batter.
            elif in_inning and line[0:1].isdigit():
                words = line.split()
                # First word is the batting position number.
                atbat = self.game().atbat()
                word = words[0]
                words = words[1:]
                ibat = int(word[0:-1])
                if ibat <= 0 or word[-1] != '.':
                    print(f"{myname}: ERROR: Invalid play line {ilin}: {line}")
                    self.nerr += 1
                    return
                # Check if the next word is a player spec. If so, we need to set that
                # before starting the at bat and, if needed, the inning.
                word = words[0]
                if word[0] == '#':
                    words = words[1:]
                    word = word[1:]
                    # If there is '(', then append words until we have the closing ')'.
                    if word.find('(') != -1:
                        while word[-1] != ')':
                            if len(words) == 0:
                                print(f"{myname}: ERROR: Invalid player spec. Line {ilin}: {line}")
                                self.nerr += 1
                                return
                            word = word + ' ' + words[0]
                            words = words[1:]
                    pwords = word.split('(')
                    player = int(pwords[0])
                    name = ''
                    if len(pwords) > 1:
                        name = word[1:].split('(')[1].split(')')[0]
                    atbat.lineup().set(ibat, player, add=True)
                    assert( atbat.ostats.have_batter(player, name, add=True) )
                    if dbg > 1: atbat.lineup().display()
                # Start the next frame.
                frm = atbat.start_batter()
                if ibat != frm.lineup_position():
                    print(f"{myname}: ERROR: Inconsistent position: {ibat} != {frm.lineup_position()}")
                    self.nerr += 1
                    self.game.error += 1
                    return 1
                # Remaining words are actions to be handled by the frame.
                assert( frm is not None )
                for word in words:
                    sta = frm.add_action(word)
                    if sta:
                        ipos = frm.lineup_position()
                        hv = self.game().atbat_label()
                        self.nerr += 1
                        self.game().error += 1
                        print(f"{myname}: ERROR: Inning {self.game().inning()} {hv} frame {ipos}" \
                              f" action {word} failed.")
                        return
                    assert( sta == 0 )

            # Configuring game in header.
            elif not in_inning and self.game() is None:
                if line[0:5] == 'Date:':
                    gameatts['date'] = line[5:].strip()
                elif line[0:5] == 'Home:':
                    home = line[5:].strip()
                elif line[0:8] == 'Visitor:':
                    visi = line[9:].strip()
                elif line[0:5] == 'VBAT:':
                    vbat = int(line[5:].strip())
                elif line[0:6] == 'Title:':
                    gameatts['title'] = line[6:].strip()
                elif line[0:9] == 'Location:':
                    gameatts['location'] = line[9:].strip()
                elif line[0:5] == 'HBAT:':
                    hbat = int(line[5:].strip())
                else:
                    print(f"{myname}: ERROR: Invalid header line {ilin}: {line}")
                    self.nerr += 1
                    return

            else:
                print(f"{myname}: ERROR: Invalid line {ilin}: {line}")
                self.nerr += 1
                return

    def game(self):
        return self.__game


