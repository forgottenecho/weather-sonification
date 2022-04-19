import pandas
import matplotlib.pyplot as plt
from midiutil import MIDIFile

def step_down(prev_note: int) -> int:
    pass

def step_up(prev_note: int) -> int:
    pass

def weather_to_midi(data_path: str, output_path: str, root_note: int, scale: int) -> None:

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
            note = step_down(last_note)
        elif tdelta > 0:
            # temp went up, step up the scale
            note = step_up(last_note)

        last_row = row
        last_note = note

    print('debug')

if __name__ == '__main__':
    weather_to_midi('nj_weather_data.csv', 'output.mid', 60, 0)