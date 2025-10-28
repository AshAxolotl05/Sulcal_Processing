import os

def main():
    # folder containing json files
    source = 'C:\\Users\\scull\\Desktop\\human completed json'
    os.chdir(source)

    for file in os.listdir(source):
        if file.endswith('.json') and file.startswith('INF'):
            header = file.split('_')
            if len(header[1]) < 5:
                print('renamed', file, sep=' ')
                os.rename(file, 'INF_' + file)

if __name__ == '__main__':
    main()