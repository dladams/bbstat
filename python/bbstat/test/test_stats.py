from bbstat import Roster
from bbstat import GameStats
from bbstat import BatStats
from bbstat import PitchStats
from bbstat import Reader
import sys
import pandas

def main_test_stats(xarg=''):
  pandas.options.display.width = 0
  dir = '/Users/davidadams/sports/wildcats/wildcats2022'
  line = '----------------------------'
  ng1 = 1
  if len(sys.argv) > 1:
      ng1 = int(sys.argv[1])
  if len(sys.argv) > 2:
      ng2 = int(sys.argv[2])
  else:
      ng2 = ng1
  if len(sys.argv) > 3:
      xarg = sys.argv[3]
  xonly  = len(xarg) and xarg == 'only'
  xcheck = len(xarg) and xarg == 'check'
  pfx = tob
  if xarg == dra:
    pfx = dra
  ros = Roster()
  ros.set_from_excel(dir + '/roster.xlsx')
  ros.display()
  xstat_sum = GameStats(ros, fill=True)
  gstat_sum = GameStats(ros, fill=True)
  count = 0
  if xonly:
    gstats = GameStats(ros, fill=True)
    for ig in range(ng1, ng2+1):
      sgam = str(ig)
      if len(sgam) < 2: sgam = '0' + sgam
      sgam = 'tob' + sgam
      fin = f"{dir}/gamesums/{sgam}.xlsx"
      print(line, sgam)
      gstats.add_from_excel(fin)
      print(line, 'xfile')
      xstats = GameStats(ros, xfile=fin)
      print(xstats.bat_stats())
      print(line, 'sum after ', sgam)
      gstats.add(xstats)
      print(gstats.bat_stats())
    print(line)
  else:
    dbg = 0
    for ig in range(ng1, ng2+1):
      sgam = str(ig)
      if len(sgam) < 2: sgam = '0' + sgam
      sgam = 'tob' + sgam
      # Game stats
      gdir = '/Users/davidadams/sports/wildcats/wildcats2022/games'
      fnam = gdir + '/' + sgam + '.dat'
      print(line, 'Game', sgam)
      rdr = Reader(fnam, dbg)
      game = rdr.game()
      if game.error:
          return 1
      gstat_sum.add(game.teamstats())
      gdf  = game.teamstats().bat_stats()
      gsdf = gstat_sum.bat_stats()
      print(gdf)
      print(line, 'Game sum ', sgam)
      print(gsdf)
      if xcheck:
        # xcl stats
        print(line, 'Excel game stats:', sgam)
        fin = f"{dir}/gamesums/{sgam}.xlsx"
        xstats = GameStats(ros, fin)
        xstats_sum.add(xstats)
        print(xstats.bat_stats())
        print(line, 'Excel sume stats:', sgam)
        print(xstats_sum.bat_stats())
        print(line, 'Last game comparison', sgam)
        xdf = sstats.bat_stats()
        print(xdf.compare(gdf))
        print(line, 'Game sum comparison', sgam)
        xsdf = gstat_sum.bat_stats()
        print(xsdf.compare(gsdf))
      if ig == ng2: print(line)
      count = count + 1
  print(line)
  bstats = BatStats(gstat_sum, minpa=20)
  bstats.display()
  print(line)
  pstats = PitchStats(gstat_sum, mininn=5)
  pstats.display()
  print(line, 'Stat sums')
  print(f"  Batting stat summary for {count} games")
  bstats.report()
  print(line)
  print(f"  Pitching stat summary for {count} games")
  print(line)
  pstats.report()
