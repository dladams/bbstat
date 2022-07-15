# batstats.py
#
# Class to evalaute derived batting stats.
#

import pandas
import traceback
from bbstat import GameStats

def krat(num, den):
  print(f"{num}/{den}")
  if int(den) == 0: return 0.0
  return int(round(1000*num/den))

class BatStats:
  '''Compile and return batting stats.
    atb - at-bats
  '''

  @classmethod
  def update_row(cls, row):
    print(row)
    row.loc['hit2'] = row['b1'] + row['b2'] + row.b3 + row.hr
    return row

  def __init__(self):
    bat_index = 'num'
    names = 'hit atb'
    self.stats = None

  def __init__(self, gstats):
    s = gstats.bat_stats()
    print(gstats.roster())
    if gstats.roster() is not None:
      s.insert(0, 'name', gstats.roster().get()['first'])
    s['hit'] = s.b1 + s.b2 + s.b3 + s.hr
    s['atb'] = s.k + s.e + s.out + s.fc + s.hit
    #s['avg'] = 0
    #s.loc[s['atb']>0,'avg'] = round(1000*s.hit/s.atb).astype(int)
    #s.loc['avg2'] = krat(s.hit, s.atb)
    s.loc[:,'avg'] = s.apply(lambda x: krat(x.hit, x.atb), axis=1)
    s.loc[:,'slg'] = s.apply(lambda x: krat(x.b1 + 2*x.b2 + 3*x.b3 + 4*x.hr, x.atb), axis=1)
    s.loc[:,'obp'] = s.apply(lambda x: krat(x.hit + x.bb + x.hbp, x.pa + x.bb + x.hbp + x.sf), axis=1)
    s.loc[:,'ops'] = s.obp + s.slg
    #for idx, row in s.iterrows():
    #  BatStats.update_row(row)
    self.stats = s

  def get(self, view='all'):
    '''Return compiled stats'''
    return self.stats

  def display(self, view='all'):
    print (self.get(view))

  def report(self):
    print("               PA  AVG  OBP  SLG  OPS    RS RBI")
    count = 0
    for idx, x in self.stats.sort_values('ops', ascending=False).iterrows():
      if count == 0:
        print('  ---------|--------------------------|--------')
      print(f"{x['name']:>10} | {x.pa:4d} {x.avg:4d} {x.obp:4d} {x.slg:4d} {x.ops:4d} | {x.run:3d} {x.rbi:3d}")
      count = (count + 1) % 4
