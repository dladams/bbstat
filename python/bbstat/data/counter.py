# counter.py
#
# David Adams
# May 2022
'''
Counter for bbstat.
Shared by bbstat Frames so they can by synchronized.
'''

class Counter:

    def __init__(self):
        self.__count = 0

    def get(self, update=False):
        '''
        Return the current index.
        if update is true, the first advance the counter.
        '''
        if update: return self.next()
        return self.__count

    def next(self):
        '''Advance the index and return the next value.'''
        self.__count += 1
        return self.__count

    @staticmethod
    def find_with_key(dic, inkey=None):
        '''
        For a dictionary dic indexed by counter indices, return the last
        entry with key less than or equal to inkey.
        if inkey is None or absent, the last value is returned.
        The value and the key are returned.
        '''
        if type(dic) is not dict:
            return None, None
        keys = list(dic.keys())
        nkey = len(keys)
        if nkey == 0 : return None, None
        if inkey is None:
            outkey = keys[-1]
            return dic[outkey], outkey
        if keys[0] > inkey: return None, None
        for ikey in range(nkey):
            if ikey+1 < nkey and keys[ikey+1] > inkey: break
        outkey = keys[ikey]
        return dic[outkey], outkey

    @staticmethod
    def find(dic, a_key=None):
        return Counter.find_with_key(dic, a_key)[0]

