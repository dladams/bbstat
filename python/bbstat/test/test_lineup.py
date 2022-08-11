import bbstat

def test_decode():
    myname = 'test_decode'
    slup = '[ 1#12(Iam Twelve), 2#(I. Catch), #6(John Bench), 3#33(Oneb Error)), 4#44]'
    exp = []
    exp.append( (1, 12, 'Iam Twelve') )
    exp.append( (2, None, 'I. Catch') )
    exp.append( (None, 6, 'John Bench') )
    exp.append( (3, 33, None) )
    exp.append( (4, 44, None) )
    lup = bbstat.Lineup.decode(slup)
    llup = len(lup)
    assert( llup == len(exp) )
    for i in range(llup):
        print(f"{lup[i]} ?= {exp[i]}")
        assert( lup[i] == exp[i] )

def main_test_lineup():
    test_decode()
    myname = 'test_lineup'
    ttl = "Test defense"
    ctr = bbstat.Counter()
    lup = bbstat.Lineup(ttl, ctr, 10)
    print(f"{myname}: Empty lineup:")
    lup.display()
    assert( lup.title() == ttl )
    assert( lup.title() == ttl )
    assert( lup.length() == 10 )
    print(f"{myname}: One-player lineup:")
    lup.set(1, 51)
    lup.display()
    assert( lup.get_player(1) == 51 )
    assert( lup.get_player(2) is None )
    print(f"{myname}: Two-player lineup:")
    lup.set(2, 52)
    lup.display()
    assert( lup.get_player(1) == 51 )
    assert( lup.get_player(2) == 52 )
    assert( lup.get_player(3) is None )
    print(f"{myname}: Ten-player lineup:")
    lup = bbstat.Lineup(ttl, ctr, range(51, 61))
    lup.display()
    assert( lup.title() == ttl )
    assert( lup.length() == 10 )
    for ipos in range(1,11):
        assert( lup.get_player(ipos) == 50 + ipos )
    print(f"{myname}: Substitute players.")
    idx1 = ctr.get()
    idx2 = ctr.next()
    lup.set(2, 62)
    lup.set(3, 63)
    lup.display()
    assert( lup.get_player(2) == 62 )
    assert( lup.get_player(2, idx2) == 62 )
    assert( lup.get_player(2, idx1) == 52 )
    assert( lup.get_player(3) == 63 )
    assert( lup.get_player(3, idx2) == 63 )
    assert( lup.get_player(3, idx1) == 53 )
    print ("All tests passed.")
