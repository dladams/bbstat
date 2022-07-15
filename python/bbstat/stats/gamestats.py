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
  bat_index = 'num'
  bat_names = 'num name pa k out sac sf fc e bb hbp b1 b2 b3 hr rbi run obo cs sb pbw'.split()
  bat_dict = {}
  con_dict = {}
  typ_dict = {}
  bat_dict['name'] = ''
  con_dict['name'] = tostr
  typ_dict['name'] = str
  for nam in bat_names[2:]:
      bat_dict[nam] = 0
      con_dict[nam] = toint
      typ_dict[nam] = int

  def __init__(self, roster=None):
    self.__roster = roster
    self.__batstats = pandas.DataFrame(columns=GameStats.bat_names, dtype=int)
    self.__batstats.astype(GameStats.typ_dict)
    self.__batstats.set_index(GameStats.bat_index, inplace=True)
    self.__fieldstats = None

  def add_from_excel(self, fin, dbg=0):
    '''Add stats from an excel file'''
    myname = 'add_from_excel'
    print(f"Adding stats from {fin}")
    shnam = 'batsum'
    inam = GameStats.bat_index
    cols = [inam] + GameStats.bat_names
    try:
      bstats = pandas.read_excel(fin, sheet_name=shnam, header=0, index_col=inam,
                                 usecols=cols, converters=GameStats.con_dict).fillna(0)
                                 #usecols=cols, dtype=GameStats.typ_dict).fillna(0)
      bstats.astype(GameStats.typ_dict)
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
        print(f"{myname}: ERROR: Roster not found.")
    if len(bstats) == 0:
      print(f"{myname}: WARNING: No data found for sheet {shnam} in file {fin}")
    else:
      bstats.drop(columns='name', inplace=True)
      bstats = bstats.fillna(0).astype('int').sort_values(inam)
      if dbg > 1:
        print(f"\n{myname}: start:")
        print(self.__batstats)
        print(f"{myname}: Read data for {len(bstats)} batters.")
        print(bstats)
      if len(self.__batstats) == 0:
        self.__batstats = bstats
      else:
        self.__batstats = self.__batstats.add(bstats, fill_value=0).astype('int')
      if dbg > 1:
        print(f"{myname}: result:")
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

  def increment_bat_stat(self, number, name, delta=1):
    self.bat_stats().loc[number, name] += delta

  def display_bat_stats(self):
    print (self.__batstats)

  def roster(self):
    return self.__roster
