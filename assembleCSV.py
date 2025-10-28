# Accumulate all relevant json data into one csv
import os
import json
import pandas as pd

#main business logic
def main():
    #folder containing json files
    source = 'C:\\Users\\scull\\Desktop\\macaque completed json'
    os.chdir(source)

    #make dataframe
    data = getData(source)
    df = pd.DataFrame(data, columns=['species', 'subject', 'time', 'hemisphere', 'gm_or_wm', 'sulcus', 'index_number', 'x', 'y', 'z'])

    # write to csv
    if os.path.exists('macaque_tracings.csv'):
        os.remove('macaque_tracings.csv')
    df.to_csv('macaque_tracings.csv', index=False)

#gets relevant data from al .json files
def getData(source_dir):
    data = []

    # assumes only .json files in folder, change later
    files =  os.listdir(source_dir)
    for f in files:
        for row in extractInfo(f):
            data.append(row)

    return data

# function to alert user if the orientation does not match the default
def checkOrientation(rawData, point):
    orientation = rawData['markups'][0]['controlPoints'][point]['orientation']

    if orientation != [-1.0, -0.0, -0.0, -0.0, -1.0, -0.0, 0.0, 0.0, 1.0]:
        print('Orientation DOES NOT MATCH')

# extracts relevant data from a single .json file
def extractInfo(file):
    # format ['species', 'subject', 'time', 'hemisphere', 'gm_or_wm', 'sulcus', 'index_number', 'x', 'y', 'z']
    rows = []

    # from file name
    species = 'macaque'
    header = file.split('_')

    subject = header[0]
    time = header[1]

    # handle the median longitudinal sulcus files differently
    if len(header) == 4:
        hemisphere = 'central'
        gm_or_wm = header[2]
        sulcus =  header[3][:-9]
    else:
        hemisphere = header[2]
        gm_or_wm = header[3]
        sulcus = header[4][:-9]

    # from .json

    # read json data
    with open(file, 'r') as f:
        rawData = json.load(f)

        # read point data
        for point in range(len(rawData['markups'][0]['controlPoints'])):
            index_number = rawData['markups'][0]['controlPoints'][point]['id']
            x = rawData['markups'][0]['controlPoints'][point]['position'][0]
            y = rawData['markups'][0]['controlPoints'][point]['position'][1]
            z = rawData['markups'][0]['controlPoints'][point]['position'][2]

            # inspect orientation
            checkOrientation(rawData, point)

            rows.append([species, subject, time, hemisphere, gm_or_wm, sulcus, index_number, x, y, z])

    return rows

main()
