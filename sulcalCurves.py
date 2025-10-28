# Assumes existence of a .csv file in a given format
# ['species', 'subject', 'time', 'hemisphere', 'gm_or_wm', 'sulcus', 'index_number', 'x', 'y', 'z']
import sys

import numpy as np
from scipy.interpolate import BSpline
import pandas as pd
import matplotlib.pyplot as plt

# List of Sulci investigated for both hemispheres
M_PIAL_SULCI = ['ce', 'arc', 'pr', 'la', 'st', 'lu', 'po', 'of', 'ip', 'di', 'cb', 'io']
M_WHITE_SULCI = ['ce', 'arc', 'pr', 'la', 'st', 'lu', 'co', 'ci', 'po', 'of', 'ca', 'ip', 'di', 'io']

H_PIAL_SULCI = ['ar', 'cb', 'ce', 'hr', 'if', 'ip', 'it', 'la', 'of', 'pc', 'po', 'pt', 'sf', 'st']
H_WHITE_SULCI = ['ar', 'ca', 'ce', 'ci', 'co', 'hr', 'if', 'ip', 'it', 'la', 'of', 'pc', 'po', 'pt', 'sf', 'st']

# main business logic
def main():
    # get csv file
    path = input("Enter the path to the csv file: ")
    try:
        csv = pd.read_csv(path)
        df = csv.sort_values(by=['subject', 'time'])
    except FileNotFoundError:
        print("File not found")
        sys.exit()

    # VIEW ONE SULCUS FOR TESTING PURPOSES
    #points = filterPoints(df, 25, '72months', 'pi', 'rh','of')
    #curves = splineFromPoints(points[0], points[1], points[2])
    #plotSulcus(curves[0], curves[1], curves[2], points[0], points[1], points[2] )

    # setup plots
    allBrains = makeDictionary(df)

    # setup cycling
    c = 0
    surface = 'wh'
    brains = list(allBrains.keys())
    keyInput = input('Press Enter to view plot, type stop to quit')

    # cycle through brains with enter
    while keyInput != 'stop':
        if c == len(brains):
            c = 0

        # plot next brain
        brain = brains[c]
        plotBrain(allBrains, brain, surface)

        # handle input
        if keyInput == '' and surface == 'wh':
            surface = 'pi'
        elif keyInput == '':
            c = c + 1
            surface = 'wh'
        elif keyInput == 'stop':
            break
        elif keyInput != 'stop' and keyInput != '':
            print('Press Enter for next brain, type stop to quit')

        keyInput = input('Press Enter for next brain, type stop to quit')

# assembles an encyclopedia of all subjects at all times with wm and gm
def makeDictionary(df):
    print("Making visualizations...")
    brains = {}
    for subject in df.subject.unique():
        for time in df.time[df.subject == subject].unique():
            brain = {}
            for surface in ['wh', 'pi']:
                    brain[surface] = makeSplines(df, subject, time, surface)
            brains[str(subject) + '_' + time] = brain

    return brains

# find points corresponding to given sulcus
def filterPoints(df, subject, time, wm_gm, hemisphere, sulcus):
    # get relevant coordinates
    points = df[(df['subject'] == subject) & (df['time'] == time) & (df['gm_or_wm'] == wm_gm) & (df['hemisphere'] == hemisphere)
                & (df['sulcus'] == sulcus)]

    x = points['x']
    y = points['y']
    z = points['z']

    return x, y, z

# get b-spline corresponding to control points
def splineFromPoints(x, y, z):
    n_control_points = len(x)

    # Change degree to handle # of points
    if n_control_points < 3:
        degree = 1 # Degree of the B-spline
    elif n_control_points < 4:
        degree = 2 # Degree of the B-spline
    else:
        degree = 3 # Degree of the B-spline

    # Uniform knot vector with clamping at the ends
    # (length = n_control_points + degree + 1)
    # must have 2k + 2 knots
    # knot vector controls influence of each control point
    knots = np.concatenate((
        np.zeros(degree),
        np.linspace(0, 1, n_control_points - degree + 1),
        np.ones(degree)
    ))

    # make spline from knots
    t_values = np.linspace(0, 1, 100)  # 100 points resampled
    spline_x = BSpline(knots, x, degree)
    spline_y = BSpline(knots, y, degree)
    spline_z = BSpline(knots, z, degree)

    curve_x = spline_x(t_values)
    curve_y = spline_y(t_values)
    curve_z = spline_z(t_values)

    return curve_x, curve_y, curve_z

#store all splines and control points for a brain in a list of tuples
def makeSplines(df, subject, time, wm_gm):
    splines = []

    # choose sulci
    if wm_gm == 'wh' and list(df['species'])[0] == 'macaque':
        sulci = M_WHITE_SULCI
    elif list(df['species'])[0] == 'macaque':
        sulci = M_PIAL_SULCI
    elif wm_gm == 'wh' and list(df['species'])[0] == 'human':
        sulci = H_WHITE_SULCI
    else:
        sulci = H_PIAL_SULCI

    # get relevant splines as a list
    for sulcus in sulci:
        try:
            points_lh = filterPoints(df, subject, time, wm_gm, 'lh', sulcus)
            points_rh = filterPoints(df, subject, time, wm_gm, 'rh', sulcus)

            spline_lh = splineFromPoints(points_lh[0], points_lh[1], points_lh[2])
            spline_rh = splineFromPoints(points_rh[0], points_rh[1], points_rh[2])

            splines.append([spline_lh[0], spline_lh[1], spline_lh[2], points_lh[0], points_lh[1], points_lh[2]])
            splines.append([spline_rh[0], spline_rh[1], spline_rh[2], points_rh[0], points_rh[1], points_rh[2]])
        except ValueError:
            print(str(subject) + ' ' + time + ' ' + wm_gm + ' ' + sulcus + ' could not generate b-spline')

    # handle median longitudinal sulcus
    if wm_gm == 'pi':
        for sulcus in ['ol', 'pl', 'fl']:
            try:
                points_ce = filterPoints(df, subject, time, wm_gm, 'central', sulcus)
                spline_ce = splineFromPoints(points_ce[0], points_ce[1], points_ce[2])
                splines.append([spline_ce[0], spline_ce[1], spline_ce[2], points_ce[0], points_ce[1], points_ce[2]])
            except ValueError:
                print(str(subject) + ' ' + time + ' ' + wm_gm + ' ' + sulcus + ' could not generate b-spline')

    return splines

# plot a b-spline and corresponding control points
def plotSulcus(curve_x, curve_y, curve_z, x, y, z):
    #setup graph
    plt.figure()
    plt.axes(projection='3d')

    plt.plot(x, y, z, 'ro--', label="Control Points")  # Control polygon
    plt.plot(curve_x, curve_y, curve_z, 'b-', label="B-Spline Curve")  # B-spline curve
    plt.show()

# plot all sulci corresponding to a given subject, time, and surface
def plotBrain(brains, brain, surface):
    sulci = brains[brain][surface]
    print(str(len(sulci)) + " sulci found")

    #setup graph
    plt.figure()
    plt.axes(projection='3d')

    #search for matching sulci
    for sulcus in sulci:
        #control points
        x = sulcus[3]
        y=  sulcus[4]
        z = sulcus[5]

        #b spline
        curve_x = sulcus[0]
        curve_y = sulcus[1]
        curve_z = sulcus[2]

        #generate plot
        plt.plot(x, y, z, 'ro--', label="Control Points")  # Control polygon
        plt.plot(curve_x, curve_y, curve_z, 'b-', label="B-Spline Curve")  # B-spline curve
        plt.title(brain + ' ' + surface)

    plt.show()

if __name__ == '__main__':
    main()