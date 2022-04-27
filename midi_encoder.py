import pandas
import matplotlib.pyplot as plt
from midiutil import MIDIFile

class Scale():

    def __init__(self, root_note: int, scale_type: int):

        # general processing vars
        self._root_note = root_note
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
    
    # reset back to root note
    def reset(self):
        self._curr_note = self._root_note
        self._scale_ptr = 0

    # getter for _curr_note
    def get_note(self):
        return self._curr_note

def weather_to_midi(data_path: str, output_path: str, root_note: int, scale_type: int, tempo: int) -> None:

    # create a scale object for note processing
    scale = Scale(root_note, scale_type)

    # create and initialize midi object for midi file creation, one per variable
    midi_temp = MIDIFile(1) # 1 means 1 track
    midi_temp.addTempo(0, 0, tempo)

    midi_thunder = MIDIFile(1) # 1 means 1 track
    midi_thunder.addTempo(0, 0, tempo)

    midi_snow = MIDIFile(1) # 1 means 1 track
    midi_snow.addTempo(0, 0, tempo)


    # load up the data
    data = pandas.read_csv(data_path)

    # more convenient column names
    data.rename(columns={'WT03':'THDR'}, inplace=True)

    # some datavalues are unrecored, replace the NaN with a 0
    data.fillna(0, inplace=True)

    # compute threshold to separate strong storms from weaker ones,
    # I used a little less than one standard deviation above the mean
    storm_thresh = data['PRCP'].mean() + 0.75 * data['PRCP'].std()

    # compute treshold for lots of snow in the same manner
    snow_thresh = data['SNOW'].mean() + 0.75 * data['SNOW'].std()

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
            midi_temp.addNote(track=0, channel=0, pitch=root_note, time=i, duration=1, volume=100)
            last_row = row
            last_note = root_note
            continue

        # # end early for debug purposes
        # if i == 1000:
        #     break
        
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

        # see if not is too high pitched
        if scale.get_note() > 127:
            scale.reset()
            note = scale.get_note()

        # save the note to the ouput
        midi_temp.addNote(track=0, channel=0, pitch=note, time=i, duration=1, volume=100)

        # check if the precipitation was relativley high AND there was thunder
        if row['PRCP'] > storm_thresh and row['THDR'] == 1:
            # add it to the bass end of the piano roll
            midi_thunder.addNote(track=0, channel=0, pitch=root_note-24, time=i, duration=16, volume=100)
            midi_thunder.addNote(track=0, channel=0, pitch=root_note-24+4, time=i, duration=16, volume=100)
            midi_thunder.addNote(track=0, channel=0, pitch=root_note-24+12, time=i, duration=16, volume=100)
        

        # print(row['THDR'])

        # process snow
        if row['SNOW'] > snow_thresh:
            # add four, "snowflake" sounding, high-pitched piano strokes
            for j in range(4):
                midi_snow.addNote(track=0, channel=0, pitch=root_note+24, time=i+j, duration=1, volume=100)
                midi_snow.addNote(track=0, channel=0, pitch=root_note+24+12, time=i+j, duration=1, volume=100)


        # prepare for next iteration
        last_row = row
        last_note = note

    print('Saving to file {0}_temp.mid, {0}_thunder.mid, {0}_snow.mid...'.format(output_path))
    with open('{}_temp.mid'.format(output_path), 'wb') as output_file:
        midi_temp.writeFile(output_file)
    with open('{}_thunder.mid'.format(output_path), 'wb') as output_file:
        midi_thunder.writeFile(output_file)
    with open('{}_snow.mid'.format(output_path), 'wb') as output_file:
        midi_snow.writeFile(output_file)

if __name__ == '__main__':
    # # code for testing Scale class
    # scale = Scale(60, 0) # init obj
    # for i in range(10): # ten steps up the scale
    #     scale.step_up()
    #     print(scale.get_note())
    # for i in range(20): # 20 steps down the scale
    #     scale.step_down()
    #     print(scale.get_note())
    
    #FIXME make tempo a param below
    weather_to_midi('nj_weather_data.csv', 'nj', 60, 0, 200)