# gamestats.py
#
# Class to hols the stats for one game.
#

import pandas
import traceback

class GameStats:
  '''
  Class to manage batting, pitching and defensive stats.
  Source batting stats:
    pa = Plate appearnces
    k = strike outs (need not reult in an out)
    out = out at-bat, i.e. not reaching 1B inclueing strikeout
    sac = sacrifice bunt (also included in out)
    sf = sacrifice fly (also included in out)
    fc = reached 1B on fielders choice; a runner might be out
    e = reached 1B on a fielding error
    bb = walk (including intentional)
    hbp = reached 1B on hit by pitch
    b1, b2, b3, hr - hit 1-4 bases
    rbi = runs batted in
    run = run scored; substitue runner gets the credit
    obo = makes an out on base (includes cs)
    cs = caught stealing
    sb = stolen base (includes DI for now)
    pbw = advances on passed balls and wild pitches
  Source pitching stats
    bf = batters faced
    ino = out recorded including at-bat and on-base =bpo+rpo
    b = balls
    s = strikes including called, swinging and foul
    bpo = batters put out including k
    rpo = runners put out
    k = strike outs (need not result in an out)
    bb = walks including intentional
    hbp = hit by pitch advancing to 1B
    hit = hit reaching 1B
    run = run scored including inherited runners and errors
    wpa = bases advanced on wild pitches excluding errors
  '''

  def tostr(f):
      return str(f)
  def toint(f):
      try:
          return int(f)
      except:
          try:
              if len(f) == 0: return 0
          except:
              myname = 'GameStats.toint'
              print(f"{myname}: WARNING: Ignoring invalid input value:'{f}'")
              return 0

  def name_match(nam1, nam2):
    '''
    Return if two names match.
    True if all the sub-names in the sharte ar include in the longer.
    '''
    if nam1 is None or nam2 is None or len(nam1)==0 or len(nam2)==0: return True
    snams1 = nam1.split()
    snams2 = nam2.split()
    if len(snams1) > len(snams2):
      return GameStats.name_match(nam2, nam1)
    for snam in snams1:
      if snam not in snams2: return False
    return True
      
  num_index = 'num'
  nam_names = ['name']
  bat_names = 'pa k out sac sf fc e bb hbp b1 b2 b3 hr rbi run obo cs sb pbw'.split()
  fld_names = 'po ast'.split()
  pit_names = 'bf ino b s bpo rpo k bb hbp hit run wpa'.split()
  all_bat_names = nam_names + bat_names
  idx_bat_names = [num_index] + all_bat_names
  all_fld_names = nam_names + fld_names
  idx_fld_names = [num_index] + all_fld_names
  all_pit_names = nam_names + pit_names
  idx_pit_names = [num_index] + all_pit_names
  bat_dict = {}
  bat_dict['name'] = ''
  for nam in bat_names:
      bat_dict[nam] = 0
  fld_dict = {}
  fld_dict['name'] = ''
  for nam in fld_names:
      fld_dict[nam] = 0
  pit_dict = {}
  pit_dict['name'] = ''
  for nam in pit_names:
      pit_dict[nam] = 0

  def __init__(self, olup=None, dlup=None, name=None, roster=None, fill=True, xfile=''):
    '''
    Create tables of statistics.
    If fill is true, it is created from the roste with all fields zeroed.
    '''
    self.name = name
    self.olup = olup
    self.dlup = dlup
    self.__roster = roster
    # Create batting stats
    self.__batstats = pandas.DataFrame(columns=GameStats.idx_bat_names, dtype=int)
    self.__batstats.name.astype(str)
    self.batstats_last = None
    self.__batstats.set_index(GameStats.num_index, inplace=True)
    # Create pitching stats
    self.__pitstats = pandas.DataFrame(columns=GameStats.idx_pit_names, dtype=int)
    self.__pitstats.name.astype(str)
    self.pitstats_last = None
    self.__pitstats.set_index(GameStats.num_index, inplace=True)
    # Create fielding stats
    self.__fldstats = None
    # Error counter.
    self.__nerror = 0
    if fill and self.roster() is not None:
      if self.roster() is None:
        print(f"{myname}: WARNING: Cannot fill without a roster.")
      else:
        rosdf = self.roster().get().copy()
        rosdf['name'] = rosdf['first']+ ' ' + rosdf['last']
        rosdf.drop(['first', 'last'], axis=1, inplace=True)
        batdf = rosdf.copy()
        for nam in GameStats.bat_names:
            batdf[nam] = int(0)
        self.__batstats = batdf
        pitdf = rosdf.copy()
        for nam in GameStats.pit_names:
            pitdf[nam] = int(0)
        self.__pitstats = pitdf
    if len(xfile):
      self.add_from_excel(xfile)

  def __adddf(self, olddf, rhsdf, nam, dbg):
    '''Add stats from another stats object.'''
    myname = 'GameStats.__adddf'
    if olddf is None: return
    if rhsdf is None: return
    if dbg > 0: print(f"Adding stats from")
    # Check names and find the number of the players to be updated.
    nums = []
    newdf = olddf
    updcols = GameStats.bat_names
    for num in olddf.index:
      if num not in rhsdf.index: continue
      oldnam = olddf.loc[num, 'name']
      rhsnam = rhsdf.loc[num, 'name']
      if not GameStats.name_match(rhsnam, oldnam):
        print(f"{myname}: WARNING: Player {num} new name {rhsnam} differs from existing name {oldnam}")
      if dbg > 1: print(f"{myname}: Updating {nam} stats for {num} {oldnam}.")
      newdf.loc[num, updcols] = olddf.loc[num, updcols] + rhsdf.loc[num, updcols]
    for num in rhsdf.index:
      if num not in olddf.index:
        print(f"{myname}: WARNING: Ignoring stats for new player {num} {rhsdf.loc[num,'name']}")
    if dbg > 1:
      print(f"{myname}: Old {nam} stats:\n{olddf}")
      print(f"{myname}: Add {nam} stats:\n{rhsdf}")
      print(f"{myname}: New {nam} stats:\n{newdf}")
    return newdf

  def add(self, rhs, dbg=0):
    '''Add stats from another stats object.'''
    myname = 'GameStats.add'
    self.__batsums = self.__adddf(self.bat_stats(), rhs.bat_stats(), 'bat', dbg)
    #TEMP self.__pitsums = self.__adddf(self.pitch_stats(), rhs.pitch_stats(), 'pit', dbg)
    return 0

  def add_from_excel(self, fin, dbg=0):
    '''Add stats from an excel file'''
    myname = 'add_from_excel'
    print(f"Adding stats from {fin}")
    shnam = 'batsum'
    inam = GameStats.num_index
    cols = GameStats.idx_bat_names
    try:
      if dbg > 0: print(f"{myname}: Reading batstats from {fin}")
      bstats = pandas.read_excel(fin, sheet_name=shnam, header=0, index_col=inam, usecols=cols)
      if dbg > 2: print(bstats.info());
    except:
      traceback.print_exc()
      bstats = pandas.DataFrame()
    # Check names.
    if self.roster() is not None:
      for num, row in bstats.iterrows():
        gamnam = row['name']
        rosnam = self.roster().first_name(num)
        if gamnam!= rosnam:
          print(f"{myname}: WARNING: Player {num} game name {gamnam} differs from roster name {rosnam}")
        else:
          if dbg > 1: print(f"{myname}: Player number {num} name {gamnam} is in roster.")
    else:
        print(f"{myname}: ERROR: Roster not found.")
    if len(bstats) == 0:
      print(f"{myname}: WARNING: No data found for sheet {shnam} in file {fin}")
    else:
      bstats.drop(columns='name', inplace=True)
      bstats = bstats.fillna(0).astype('int').sort_values(inam)
      self.batstats_last = bstats
      if dbg > 1:
        print(f"\n{myname}: Starting:")
        print(self.__batstats)
        print(f"\n{myname}: Adding ({len(bstats)} batters):")
        print(bstats)
      if len(self.__batstats) == 0:
        if dbg: print(f"\n{myname}: Creating bat stats.")
        self.__batstats = bstats
      else:
        if dbg: print(f"\n{myname}: Updating bat stats.")
        sumstats = self.__batstats.drop('name', axis=1).add(bstats, fill_value=0).astype('int')
        sumstats.insert(0, 'name', self.__batstats['name'])
        self.__batstats = sumstats
      if dbg > 1:
        print(f"{myname}: Summed batting stats:")
        print(self.__batstats)

  def add_batter(self, num, name=None):
    myname = 'GameStats.add_batter'
    dbg = 0
    if num in self.bat_stats().index:
      oldnam = bat_stats().loc[num, 'name']
      if oldnam is None:
        if name is None:
          print(f"{myname}: Batter {num} is already included without a name.")
        else:
          if dbg: print(f"{myname}: Assigning name to batter {num}: {name}.")
          bat_stats().loc[num, 'name'] = name
          return 0
      else:
        if name is None:
          print(f"{myname}: Batter {num} is already included.")
        elif name == oldnam:
          print(f"{myname}: Batter {num} is already included with the same name {oldnam}.")
        else:
          print(f"{myname}: Batter {num} is already included with name {oldnam}.")
          print(f"{myname}: New name {name} is ignored.")
      return 1
    if dbg: print(f"{myname}: Adding batter {num} {name}")
    newrow = pandas.DataFrame.from_dict({ num : GameStats.bat_dict }, orient='index')
    newrow.index.name = 'num'
    newrow['name'] = name
    self.__batstats = pandas.concat([self.__batstats, newrow])
    return 0

  def have_batter(self, num, name=None, add=False):
    myname = 'GameStats.have_batter'
    dbg = 0
    if num in self.bat_stats().index: return True
    if not add: return False
    assert(self.add_batter(num, name) == 0)
    return True

  def add_fielder(self, num, name=None):
    myname = 'GameStats.add_fielder'
    dbg = 1
    if num in self.fld_stats().index:
      oldnam = fld_stats().loc[num, 'name']
      if oldnam is None:
        if name is None:
          print(f"{myname}: Fielder {num} is already included without a name.")
        else:
          if dbg: print(f"{myname}: Assigning name to fielder {num}: {name}.")
          fld_stats().loc[num, 'name'] = name
          return 0
      else:
        if name is None:
          print(f"{myname}: Fielder {num} is already included.")
        elif name == oldnam:
          print(f"{myname}: Fielder {num} is already included with the same name {oldnam}.")
        else:
          print(f"{myname}: Fielder {num} is already included with name {oldnam}.")
          print(f"{myname}: New name {name} is ignored.")
      return 1
    if dbg: print(f"{myname}: Adding fielder {num} {name}")
    newrow = pandas.DataFrame.from_dict({ num : GameStats.fld_dict }, orient='index')
    newrow.index.name = 'num'
    newrow['name'] = name
    self.__fldstats = pandas.concat([self.__fldstats, newrow])
    return 0

  def have_fielder(self, num, name=None, add=False):
    myname = 'GameStats.have_fielder'
    dbg = 0
    if num in self.fld_stats().index: return True
    if not add: return False
    assert(self.add_fielder(num, name) == 0)
    return True

  def add_pitcher(self, num, name=None):
    myname = f"GameStats.add_pitcher: {self.name}"
    dbg = 0
    stas = self.pitch_stats()
    if num in stas.index:
      oldnam = stas.loc[num, 'name']
      if oldnam is None:
        if name is None:
          print(f"{myname}: Pitcher {num} is already included without a name.")
        else:
          if dbg: print(f"{myname}: Assigning name to pitcher {num}: {name}.")
          pitch_stats().loc[num, 'name'] = name
          return 0
      else:
        if name is None:
          print(f"{myname}: Pitcher {num} is already included.")
        elif name == oldnam:
          print(f"{myname}: Pitcher {num} is already included with the same name {oldnam}.")
        else:
          print(f"{myname}: Pitcher {num} is already included with name {oldnam}.")
          print(f"{myname}: New name {name} is ignored.")
      return 1
    if dbg: print(f"{myname}: Adding pitcher {num} {name}")
    newrow = pandas.DataFrame.from_dict({ num : GameStats.pit_dict }, orient='index')
    newrow.index.name = 'num'
    newrow['name'] = name
    self.__pitstats = pandas.concat([stas, newrow])
    return 0

  def have_pitcher(self, num, name=None, add=False):
    myname = 'GameStats.have_pitcher'
    dbg = 0
    if num in self.pitch_stats().index: return True
    if not add: return False
    assert(self.add_pitcher(num, name) == 0)
    return True

  def bat_stats(self, num=None):
    '''Return all stats or stats for player num.'''
    if num is None:
      return self.__batstats
    else:
      return self.__batstats.query(f"num={num}")

  def pitch_stats(self, num=None):
    '''Return all stats or stats for player num.'''
    if num is None:
      return self.__pitstats
    else:
      return self.__pitstats.query(f"num={num}")

  def increment_player_bat_stat(self, num, name, delta=1):
    '''Increment bat stats by player number.'''
    self.bat_stats().loc[num, name] += delta
    return 0

  def increment_position_bat_stat(self, pos, name, delta=1):
    '''Increment bat stats by player number.'''
    myname = f"GameStats.increment_position_bat_stat: {self.name}"
    if self.olup is None:
      print(f"{myname}: ERROR: Stats do not have the offesnive lineup")
      self.__nerror += 1
      return 2
    num = self.olup.get_player(pos)
    if num is None:
      print(f"{myname}: ERROR: No player is assigned to batting position {num}")
      self.__nerror += 1
      return 3
    return self.increment_player_bat_stat(mum, name, delta)

  def increment_pitch_stat(self, name, delta=1):
    myname = f"GameStats.increment_pitch_stat: {self.name}"
    num = self.dlup.get_player(1)
    if num is None:
      print(f"{myname}: ERROR: Cannot set pitch stat {name} without a pitcher.")
      print(f"{myname}: {self.dlup}")
      self.__nerror += 1
      return 1
    if name not in self.pitch_stats().columns:
      print(f"{myname}: ERROR: Cannot increment unknown stat {name}.")
      self.__nerror += 1
      return 2
    stas = self.pitch_stats()
    if num not in stas.index:
      self.add_pitcher(num)
      stas = self.pitch_stats()
    stas.loc[num, name] += delta
    return 0

  def display_bat_stats(self):
    print (self.__batstats)

  def display_field_stats(self):
    print (self.__fldstats)

  def display_pitch_stats(self):
    print (self.__pitstats)

  def roster(self):
    return self.__roster

  def nerror(self):
    return self.__nerror
