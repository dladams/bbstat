from bbstat import Roster
from bbstat import GameStats
from bbstat import BatStats
from bbstat import PitchStats
from bbstat import Reader
import sys
import pandas

def main_test_stats():
  '''
  Usage: test_stats ssgam [opt1 opt2 ...]
  ssgams is a game: xxxII or
         a range xxxII-JJ: [xxxII,... xxxJJ] 
         or a comma-separated list of either
         opts include
           xonly - Only show excel stats
           xcheck - Compare excel and game stats
           minpa=N - Set minpa for bat stats to N
  '''
  pandas.options.display.width = 0
  dir = '/Users/davidadams/Documents/sports/wildcats-2023'
  line = '----------------------------'
  ssgam = sys.argv[1]
  sgams = []
  for ran in ssgam.split(','):
    jpos = ran.find('-')
    print(jpos)
    if jpos < 0:
      sgams.append(ran)
      print(sgams)
    else:
      ipos = jpos - 1
      snum2 = ran[jpos+1:]
      lnum = len(snum2)
      ipos = jpos - lnum
      snum1 = ran[ipos:jpos]
      while len(snum1) and snum1[0]=='0': snum1 = snum1[1:]
      while len(snum2) and snum2[0]=='0': snum2 = snum2[1:]
      pfx = ran[0:ipos]
      for inum in range(int(snum1), int(snum2)+1):
        sgam = pfx + str(inum).zfill(lnum)
        print('Adding game', sgam)
        sgams.append(sgam)
  print(f"Games: {sgams}")
  errgams = []
  xonly = False
  xcheck = False
  minpa = 20
  for opt in sys.argv[2:]:
    if   opt == 'xonly': xonly = True
    elif opt == 'xcheck': xcheck = True
    elif opt[0:6] == 'minpa=':
      minpa = int(opt[6:])
    else:
      print(f"Invalid option: {opt}")
      return 1
  ros = Roster()
  ros.set_from_excel(dir + '/roster.xlsx')
  ros.display()
  xstat_sum = GameStats(roster=ros, fill=True)
  gstat_sum = GameStats(roster=ros, fill=True)
  count = 0
  if xonly:
    gstats = GameStats(roster=ros, fill=True)
    for sgam in sgams:
      fin = f"{dir}/gamesums/{sgam}.xlsx"
      #print(line, sgam)
      #gstats.add_from_excel(fin)
      print(line, 'xfile')
      xstats = GameStats(roster=ros, xfile=fin)
      print(xstats.bat_stats())
      print(line, 'sum after ', sgam)
      gstats.add(xstats)
      print(gstats.bat_stats())
    print(line)
  else:
    dbg = 0
    for sgam in sgams:
      # Game stats
      gdir = '/Users/davidadams/Documents/sports/wildcats-2023/games'
      fnam = gdir + '/' + sgam + '.dat'
      print(line, 'Game', sgam)
      rdr = Reader(fnam, dbg)
      game = rdr.game()
      if game.error:
          return 1
      if game.nerror():
          errgams.append(sgam)
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
        xstats = GameStats(roster=ros, xfile=fin)
        xstat_sum.add(xstats)
        print(xstats.bat_stats())
        print(line, 'Excel sum stats:', sgam)
        print(xstat_sum.bat_stats())
        #print(line, 'Last game comparison', sgam)
        #xdf = xstats.bat_stats()
        #print(xdf.compare(gdf))
        print(line, 'Game sum comparison', sgam)
        xsdf = gstat_sum.bat_stats()
        print(xsdf.compare(gsdf))
      if count == len(sgams): print(line)
      count = count + 1
  print(line)
  bstats = BatStats(gstat_sum, minpa=minpa)
  bstats.display()
  print(line)
  pstats = PitchStats(gstat_sum, mininn=5)
  pstats.display()
  print(line, 'Stat sums')
  print(f"  Batting stat summary for {count} games ({ssgam})")
  bstats.report()
  print(line)
  print(f"  Pitching stat summary for {count} games")
  print(line)
  pstats.report()
  print(line)
  print(f"Games with errors: {errgams}")
