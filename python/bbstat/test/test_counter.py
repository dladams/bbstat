import bbstat

def main_test_counter():
    ctr = bbstat.Counter()
    assert( ctr.get() == 0 )
    assert( ctr.next() == 1 )
    dic = {}
    find = bbstat.Counter.find
    assert( find(dic, 0) is None )
    dic[1] = 51
    assert( find(dic, 0) is None )
    assert( find(dic, 1) == 51 )
    assert( find(dic, 2) == 51 )
    dic[2] = 52
    assert( find(dic, 0) is None )
    assert( find(dic, 1) == 51 )
    assert( find(dic, 2) == 52 )
    print('All tests pass.')
    return 0
