from bbstat import Roster
from bbstat import GameStats
from bbstat import BatStats
from bbstat import Reader
import sys
import pandas

def main_test_stats(xcl=False):
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
  ros = Roster()
  ros.set_from_excel(dir + '/roster.xlsx')
  ros.display()
  gstat_sum = GameStats(ros)
  if xcl:
    for sgam in 'tob01 tob02 tob03 tob04 tob05'.split():
      gstats = GameStats(ros)
      fin = f"{dir}/{sgam}.xlsx"
      gstats.add_from_excel(fin)
  else:
    dbg = 0
    for ig in range(ng1, ng2+1):
      sgam = str(ig)
      if len(sgam) < 2: sgam = '0' + sgam
      sgam = 'tob' + sgam
      # xcl stats
      gstats = GameStats(ros)
      fin = f"{dir}/gamesums/{sgam}.xlsx"
      gstats.add_from_excel(fin)
      print(line, sgam)
      xdf = gstats.bat_stats()
      print(xdf)
      # Game stats
      gdir = '/Users/davidadams/sports/wildcats/wildcats2022/games'
      fnam = gdir + '/' + sgam + '.dat'
      print(line, sgam)
      rdr = Reader(fnam, dbg)
      game = rdr.game()
      if game.error:
          return 1
      gdf = game.teamstats().bat_stats().sort_index()
      gdf.drop('name', axis=1, inplace=True)
      print(gdf)
      print(line, sgam)
      print(xdf.compare(gdf))
      #game.teamstats().display_bat_stats()
      if ig == ng2: print(line)
