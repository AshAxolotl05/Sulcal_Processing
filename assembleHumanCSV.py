# Accumulate all relevant json data into one csv
import math
import os
import json
import pandas as pd
import openpyxl

#main business logic
def main():
    # from excel
    tracker = pd.read_excel("C:\\Users\\scull\\Documents\\Information_Tracker.xlsx")

    #folder containing json files
    source = 'C:\\Users\\scull\\Desktop\\human completed json'
    os.chdir(source)

    if os.path.exists('human_tracings.csv'):
        os.remove('human_tracings.csv')

    #make dataframe
    data = getData(source, tracker)
    df = pd.DataFrame(data, columns=['species', 'record_id', 'group', 'subject', 'time', 'hemisphere', 'gm_or_wm', 'sulcus', 'index_number', 'x', 'y', 'z'])

    # write to csv
    df.to_csv('human_tracings.csv', index=False)

def getData(source_dir, excel):
    data = []

    # assumes only .json files in folder, change later
    files = os.listdir(source_dir)
    for f in files:
        for row in extractInfo(f, excel):
            data.append(row)

    return data

# extracts relevant data from a single .json file
def extractInfo(file, df):
    # format ['species', 'group', 'record_id', 'subject', 'time', 'hemisphere', 'gm_or_wm', 'sulcus', 'index_number', 'x', 'y', 'z']
    rows = []

    # from file name
    species = 'human'
    header = file.split('_')

    group = header[0]
    record_id = header[1]

    # handle the median longitudinal sulcus files differently
    if len(header) == 4:
        hemisphere = 'central'
        gm_or_wm = header[2]
        sulcus = header[3][:-9]

    else:
        hemisphere = header[2]
        gm_or_wm = header[3]
        sulcus = header[4][:-9]

    # from Excel
    print(record_id, group, sep=' ')
    row = df[(df['Record ID'] == record_id) & (df['Group'] == group)]
    subject = list(row['Subject'])[0]
    time = str(round(list(row['Months'])[0])) + 'months'

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

            rows.append([species, record_id, group, subject, time, hemisphere, gm_or_wm, sulcus, index_number, x, y, z])

    return rows

# function to alert user if the orientation does not match the default
def checkOrientation(rawData, point):
    orientation = rawData['markups'][0]['controlPoints'][point]['orientation']

    if orientation != [-1.0, -0.0, -0.0, -0.0, -1.0, -0.0, 0.0, 0.0, 1.0]:
        print('Orientation DOES NOT MATCH')


if __name__ == '__main__':
    main()


