# roseter.py
#
# Class to hold the team roster
#

import pandas
import traceback

class Roster:

  index = 'num'
  cols = 'num first last'.split()

  def __init__(self):
    self.__data = pandas.DataFrame(columns=Roster.cols)
    self.__data.set_index(Roster.index, inplace=True)

  def set_from_excel(self, fin, dbg=0):
    '''Set roster from an excel file'''
    myname = 'set_from_excel'
    print(f"Setting roster from {fin}")
    shnam = 'roster'
    inam = Roster.index
    cols = [inam] + Roster.cols
    try:
      self.__data = pandas.read_excel(fin, sheet_name=shnam, header=0, index_col=inam,
                                      usecols=cols, converters={'first':str, 'last':str})
    except:
      traceback.print_exc()
      self.__data = pandas.DataFrame()

  def get(self):
    return self.__data

  def first_name(self, num):
    names = self.get()['first']
    if num in names.index:
      return names[num]
    return 'NoSuchRosterName'

  def display(self):
    print(self.get())
