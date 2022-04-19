import pandas
import matplotlib.pyplot as plt
from midiutil import MIDIFile

class Scale():

    def __init__(self, root_note: int, scale_type: int):

        # general processing vars
        self._curr_note = root_note
        self._scale_ptr = 0

        # determine stepping pattern based on scale type
        if scale_type == 0:
            # major scale
            self._steps = [2, 2, 1, 2, 2, 2, 1] # WWHWWWH
        elif scale_type == 1:
            # minor scale
            self._steps = [] # FIXME add steps
        else:
            # error, scale code did not match any of ours
            raise Exception('scale_type not recognized.')

    # makes one step down the scale
    def step_down(self):
        # decrement the ptr
        self._scale_ptr -= 1

        # wrap around if necessary
        if self._scale_ptr == -1:
            self._scale_ptr = len(self._steps) - 1
        
        # subtract the value from the current note to find new note
        self._curr_note -= self._steps[self._scale_ptr]


    # makes one step up the scale
    def step_up(self):
        # add the value to the current note to find new note
        self._curr_note += self._steps[self._scale_ptr]

        # increment the ptr
        self._scale_ptr += 1

        # wrap around if necessary
        if self._scale_ptr == len(self._steps):
            self._scale_ptr = 0
    
    # getter for _curr_note
    def get_note(self):
        return self._curr_note

def weather_to_midi(data_path: str, output_path: str, root_note: int, scale_type: int) -> None:

    # load up the data
    data = pandas.read_csv(data_path)

    # more convenient column names
    data.rename(columns={'WT03':'THDR'}, inplace=True)

    # some datavalues are unrecored, replace the NaN with a 0
    data.fillna(0, inplace=True)

    #
    #
    # I decided to loop through the dataframe instead of using more
    # efficient functions like apply() to process my data. I did this
    # because the midiutil only allows one note to be added at a time
    # so the time complexity savings are lost there.
    # Thus it is not worth the overhead of design an unreadable note-
    # mapping function to use apply(), but instead I will process each
    # day inside the loop and then add each day to the midi track.
    #
    #

    ## loop through each day in the dataset
    last_row = None
    output_notes = []
    for i, row in data.iterrows():

        # first data point has easy processing
        if i == 0:
            last_row = row
            last_note = root_note
            continue

        # end early for debug purposes
        if i == 10:
            break
        
        # handle first day's temp differenlty

        # find the temperature change
        tdelta = row['TMAX'] - last_row['TMAX']

        # assign the proper note for this day
        if tdelta == 0:
            # repeat the same note, no change
            note = last_note
        elif tdelta < 0:
            # temp went down, step down the scale
            scale.step_down()
            note = scale.get_note()
        elif tdelta > 0:
            # temp went up, step up the scale
            scale.step_up()
            note = scale.get_note()

        last_row = row
        last_note = note

    print('debug')

if __name__ == '__main__':
    # code for testing Scale class
    scale = Scale(60, 0) # init obj
    for i in range(10): # ten steps up the scale
        scale.step_up()
        print(scale.get_note())
    for i in range(20): # 20 steps down the scale
        scale.step_down()
        print(scale.get_note())
    
    weather_to_midi('nj_weather_data.csv', 'output.mid', 60, 0)