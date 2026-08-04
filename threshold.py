import csv
import numpy as np
from pyomyo import Myo, emg_mode

# csv filename
filename = "threshold.csv"
# csv headers
headers = ["ch01", "ch02", "ch03", "ch04", "ch05", "ch06", "ch07", "ch08"]

# threshold multiplier
multiplier = 2


def get_channel_values(raw_data, channel):
    channel_values = []

    for sample in raw_data:
        # collect values for each channel
        channel_values.append(sample[channel])

    return np.array(channel_values)

# function to define the thresholds for each channel
def find_thresholds(raw_data):
    threshold_values = []

    for channel in range(8):
        channel_values = get_channel_values(raw_data, channel)

        median = np.median(channel_values)
        abs_difference = np.abs(channel_values - median)
        # calculate Mean Absolute Deviation (MAD)
        mad = np.median(abs_difference)

        # calculate threshold and add to list
        threshold = mad * multiplier
        threshold_values.append(threshold)

    return threshold_values

# main program function
def main():
    raw_data = []

    myo = Myo(mode=emg_mode.RAW)
    myo.connect()

    # create csv file for raw resting data
    with open(filename, 'w', newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(headers)    # add headers to csv

        def myoemg(emg, movement):
            raw_data.append(emg)
            csv_writer.writerow(emg)    # add emg readings to csv

        myo.add_emg_handler(myoemg)

        try:
            print("\nGetting RAW data.")

            while True:
                myo.run()

        except KeyboardInterrupt:
            print("\nQuitting...")

        finally:
            myo.disconnect()

    if raw_data:
        threshold_values = find_thresholds(raw_data)
        print("Zero Crossing Thresholds =", threshold_values)
    else:
        print("ERROR")


if __name__ == "__main__":
    main()