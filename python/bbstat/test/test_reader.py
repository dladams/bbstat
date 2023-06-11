import bbstat
import sys
import pandas

def main_test_reader():
    pandas.options.display.width = 0
    gnam = 'tob02'
    dbg = 0
    show = 'bat'
    if len(sys.argv) > 1:
        gnam = sys.argv[1]
    for arg in sys.argv[1:]:
        if   arg[0:3] ==   'dbg':
            dbg = 1
            vals = arg.split('=')
            if len(vals) > 1:
                dbg = int(vals[1])
        elif arg == 'pitch': show = 'pitch'
        elif arg ==   'bat': show = 'bat'
    print(f"Processing game {gnam}")
    gdir = '/Users/davidadams/Documents/sports/wildcats-2023/games'
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
    if game.nerror():
        print(f"***** ERROR: game has {game.nerror()} errors. *****")
    assert( rdr.nerr == 0 )
    print()
    print('Visitor stats:')
    if show == 'bat': game.vstats.display_bat_stats()
    if show == 'pitch': game.vstats.display_pitch_stats()
    print()
    print('Home stats:')
    if show == 'bat': game.hstats.display_bat_stats()
    if show == 'pitch': game.hstats.display_pitch_stats()
    return 0
