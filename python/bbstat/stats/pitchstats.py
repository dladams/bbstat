# pitchstats.py
#
# Class to evalaute derived batting stats.
#

import pandas
import traceback
from bbstat import GameStats

def krat(num, den):
  #print(f"{num}/{den}")
  if int(den) == 0: return 0.0
  return int(round(1000*num/den))

class PitchStats:
  '''Compile and return batting stats.
    ino - inning outs = 3*innings
  '''

  @classmethod
  def update_row(cls, row):
    print(row)
    #row.loc['hit2'] = row['b1'] + row['b2'] + row.b3 + row.hr
    return row

  def __init__(self):
    num_index = 'num'
    names = 'inn pit'
    self.stats = None

  def __init__(self, gstats, mininn=5):
    s = gstats.pitch_stats().copy()
    print(gstats.roster())
    if gstats.roster() is not None:
      s.insert(0, 'rname', gstats.roster().get()['first'])
    s['inn'] = s.ino/3 + 0.1*(s.ino%3)
    s['pit'] = s.b + s.s
    #s.loc[:,'avg'] = s.apply(lambda x: krat(x.hit, x.atb), axis=1)
    #s.loc[:,'slg'] = s.apply(lambda x: krat(x.b1 + 2*x.b2 + 3*x.b3 + 4*x.hr, x.atb), axis=1)
    #s.loc[:,'obp'] = s.apply(lambda x: krat(x.hit + x.bb + x.hbp, x.pa + x.bb + x.hbp + x.sf), axis=1)
    #s.loc[:,'ops'] = s.obp + s.slg
    #s.sort_values('ops', ascending=False, inplace=True)
    self.stats = s

  def add(self, num):
    '''Add a pitcher as current'''
    
  def get(self, view='all'):
    '''Return compiled stats'''
    return self.stats

  def display(self, view='all'):
    print (self.get(view))

  def report(self):
    print("                      INN  PIT")
    count = 0
    for idx, x in self.stats.sort_values('inn', ascending=False).iterrows():
      if count == 0:
        print('  -----------------|--------------------------|--------')
      print(f"{x['name']:>18} | {x.inn:4.0f} {x.pit:4.0f}")
      count = (count + 1) % 4
