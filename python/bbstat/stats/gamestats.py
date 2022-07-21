# gamestats.py
#
# Class to hols the stats for one game.
#

import pandas
import traceback

class GameStats:

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
    True if all the sub-nmaes in the sharte ar include in the longer.
    '''
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
  pit_names = 'bf ino b s bpo rpo k bb hpb hit run wp'.split()
  all_bat_names = nam_names + bat_names
  idx_bat_names = [num_index] + all_bat_names
  all_pit_names = nam_names + pit_names
  idx_pit_names = [num_index] + all_pit_names
  bat_dict = {}
  bat_dict['name'] = ''
  for nam in bat_names:
      bat_dict[nam] = 0

  def __init__(self, roster=None, fill=True, xfile=''):
    '''
    Create tables of statistics.
    If fill is true, it is created from the roste with all fields zeroed.
    '''
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
    self.__fieldstats = None
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
    self.__pitsums = self.__adddf(self.pitch_stats(), rhs.pitch_stats(), 'pit', dbg)
    return 0

  def add_from_excel(self, fin, dbg=0):
    '''Add stats from an excel file'''
    myname = 'add_from_excel'
    print(f"Adding stats from {fin}")
    shnam = 'batsum'
    inam = GameStats.num_index
    cols = GameStats._idx_bat_names
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
        print(f"\n{myname}: Creating bat stats.")
        self.__batstats = bstats
      else:
        print(f"\n{myname}: Updating bat stats.")
        sumstats = self.__batstats.drop('name', axis=1).add(bstats, fill_value=0).astype('int')
        sumstats.insert(0, 'name', self.__batstats['name'])
        self.__batstats = sumstats
      if dbg > 1:
        print(f"{myname}: Summed batting stats:")
        print(self.__batstats)

  def have_batter(self, num, name=None, add=False):
    myname = 'GameStats.have_batter'
    dbg = 0
    if num in self.bat_stats().index: return True
    if not add: return False
    if dbg: print(f"{myname}: Adding player {num} {name}")
    newrow = pandas.DataFrame.from_dict({ num : GameStats.bat_dict }, orient='index')
    newrow.index.name = 'num'
    newrow['name'] = name
    self.__batstats = pandas.concat([self.__batstats, newrow])
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

  def increment_bat_stat(self, number, name, delta=1):
    self.bat_stats().loc[number, name] += delta

  def increment_pit_stat(self, number, name, delta=1):
    self.pit_stats().loc[number, name] += delta

  def display_bat_stats(self):
    print (self.__batstats)

  def display_pit_stats(self):
    print (self.__pitstats)

  def roster(self):
    return self.__roster
