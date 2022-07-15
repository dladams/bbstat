import bbstat
import sys
import pandas

def main_test_reader():
    pandas.options.display.width = 0
    gnam = 'tob07'
    dbg = 0
    if len(sys.argv) > 1:
        gnam = sys.argv[1]
    if len(sys.argv) > 2:
        dbg = int(sys.argv[2])
    print(f"Processing game {gnam}")
    gdir = '/Users/davidadams/sports/wildcats/wildcats2022/games'
    fnam = gdir + '/' + gnam + '.dat'
    print('Reader test of bbstat:')
    rdr = bbstat.Reader(fnam, dbg)
    print()
    game = rdr.game()
    if not game.is_complete():
        print(f"ERROR: Game is not complete: {game.reason}")
        return 1
    sttl = ' ' + game.title if len(game.title) else ''
    scall = ' (' + game.call_reason() + ')' if len(game.call_reason()) else ''
    print(f"Game{sttl} is complete{scall}.")
    print(f"{game.visitor.team()} @ {game.home.team()}")
    print(f"{game.date}")
    print(f"Location: {game.location}")
    print(f"Final score: {game.score()}")
    assert( rdr.nerr == 0 )
    print()
    print('Visitor stats:')
    game.vstats.display_bat_stats()
    print()
    print('Home stats:')
    game.hstats.display_bat_stats()
    return 0
