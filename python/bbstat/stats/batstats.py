# batstats.py
#
# Class to evalaute derived batting stats.
#

import pandas
import traceback

def krat(num, den):
  #print(f"{num}/{den}")
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

  def __init__(self, gstats, minpa=1, add_rname=False):
    myname = 'BatStats.init'
    s = gstats.bat_stats().copy()
    print(f"{myname}: Roster: {gstats.roster()}")
    if add_rname:
      if gstats.roster() is not None:
        s.insert(0, 'rname', gstats.roster().get()['first'])
      else:
        print(f"{myname}: WARNING: No roster found.")
    s['hit'] = s.b1 + s.b2 + s.b3 + s.hr
    s['atb'] = s.pa - s.bb - s.hbp - s.sf - s.sac
    #s['avg'] = 0
    #s.loc[s['atb']>0,'avg'] = round(1000*s.hit/s.atb).astype(int)
    #s.loc['avg2'] = krat(s.hit, s.atb)
    print(s)
    s.loc[:,'avg'] = s.apply(lambda x: krat(x.hit, x.atb), axis=1)
    s.loc[:,'slg'] = s.apply(lambda x: krat(x.b1 + 2*x.b2 + 3*x.b3 + 4*x.hr, x.atb), axis=1)
    s.loc[:,'obp'] = s.apply(lambda x: krat(x.hit + x.bb + x.hbp, x.atb + x.bb + x.hbp + x.sf), axis=1)
    s.loc[:,'ops'] = s.obp + s.slg
    #for idx, row in s.iterrows():
    #  BatStats.update_row(row)
    s = s.query(f"pa>{minpa}")
    #s = sort_values('ops', ascending=False)
    self.stats = s

  def get(self, view='all'):
    '''Return compiled stats'''
    return self.stats

  def display(self, view='all'):
    print (self.get(view))

  def report(self):
    self.report_fields = "Name | PA AB | AVG OBP SLG OPS | RS RBI | SB CS | K BB 1B 2B 3B HR".split()
    fmap = {}
    fmap['PA']  = 'pa'
    fmap['AB']  = 'atb'
    fmap['AVG'] = 'avg'
    fmap['OBP'] = 'obp'
    fmap['SLG'] = 'slg'
    fmap['OPS'] = 'ops'
    fmap['RUN'] = 'run'
    fmap['RS']  = 'run'
    fmap['RBI'] = 'rbi'
    fmap['SB']  = 'sb'
    fmap['CS']  = 'cs'
    fmap['1B']  = 'b1'
    fmap['2B']  = 'b2'
    fmap['3B']  = 'b3'
    fmap['HR']  = 'hr'
    fmap['BB']  = 'bb'
    fmap['K']   = 'k'
    # Max name length.
    lnam = 0
    for nam in self.stats.loc[:,'name'].values:
      if len(nam) > lnam: lnam = len(nam)
    # Build the header and separator line
    wnam = lnam + 1
    header = ''
    sep = ''
    wval = 5
    for fie in self.report_fields:
      if fie == 'Name':
        for i in range(wnam): sep += '-'
        header += f"{'Name':>{wnam}}"
      elif fie == '|':
        sep    += '-|'
        header += ' |'
      else:
        for i in range(wval): sep += '-'
        header += f"{fie:>{wval}}"
    print(header)
    count = 0
    for idx, x in self.stats.sort_values('ops', ascending=False).iterrows():
      if count == 0:
        print(sep)
      line = ''
      for fie in self.report_fields:
        if fie == 'Name':
          line += f"{x['name']:>{wnam}}"
        elif fie == '|':
          line += ' |'
        else:
          val = int(x[fmap[fie]])
          line += f"{val:>{wval}.0f}"
      print(line)
      count = (count + 1) % 4
    print(sep)
