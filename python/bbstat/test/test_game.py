import bbstat

def main_test_game():
    print('Game test of bbstat:')
    dir(bbstat)
    vbat = [11,12,13,14,15,16,17,18,19]
    hbat = [21,22,23,24,25,26,27,28,29]
    game = bbstat.Game("June 1, 2033", "Guests", "Homers", vbat, hbat)
    print(f"Game index is {game.index()}")
    print(f"Home index is {game.home.index()}")
    print(f"Visitor index is {game.visitor.index()}")
    assert(not game.home.is_valid(False))
    game.home.set_roster(list(range(10,30,1)))
    game.visitor.set_roster(list(range(21, 46)))
    #assert(game.home.is_valid())
    for label, team in game.teams():
        #assert(team.is_valid())
        print(f"{label:>9}: roster: {team.roster()}")
        print(f"{label:>9}: lineup: {team.lineup()}")
    frame = game.start_half_inning()
    print(f"  Inning: {game.half_inning_label()} {game.inning()}")
    print(f" Batting: {game.atbat().team()} ({game.atbat_label()}) {frame.player()} [{frame.lineup_index()}]")
    # Batter 1
    frame.pitch('b')
    frame.pitch('c')
    frame.pitch('s')
    frame.pitch('s', '1B')
    frame.add_action('1:SB')
    for idx in range(game.index()):
        print(f"{idx}: {frame.pitch_count(idx)}")
    frame = game.next_batter()
