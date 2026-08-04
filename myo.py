from pyomyo import Myo, emg_mode
import csv
import numpy as np
# import emg_toolbox.features as emgtool


# the name of the csv file that will store the processed data
filename = 'myo.csv'
# CSV file headers
headers = ["01_mav", "02_mav", "03_mav", "04_mav", "05_mav", "06_mav", "07_mav", "08_mav", 
           "01_rms", "02_rms", "03_rms", "04_rms", "05_rms", "06_rms", "07_rms", "08_rms",
           "01_iemg", "02_iemg", "03_iemg", "04_iemg", "05_iemg", "06_iemg", "07_iemg", "08_iemg",
           "01_var", "02_var", "03_var", "04_var", "05_var", "06_var", "07_var", "08_var",
           "01_wl", "02_wl", "03_wl", "04_wl", "05_wl", "06_wl", "07_wl", "08_wl",
           "01_zc", "02_zc", "03_zc", "04_zc", "05_zc", "06_zc", "07_zc", "08_zc"]

# list to store 40 most recent EMG samples
# each sample contains one value from each channel
raw_data = []
# list to store Zero Crossing thresholds from threshold.py
zc_thresholds = [2.0, 18.0, 6.0, 2.0, 4.0, 6.0, 4.0, 6.0]


# ====================== CSV FUNCTIONS
# function to create the csv file and write the column headers
def create_csv():
    # create csv file
    with open(filename, 'w', newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # write the headers into the csv file
        csv_writer.writerow(headers)

# function to write to the csv file
def add_to_csv(row):
    # open csv file in append mode
    with open(filename, 'a', newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(row)

create_csv()
# ========================================================================================


# ====================== HELPER FUNCTION
# function to get all values for one EMG channel
def get_channel_values(raw_data, channel):
    channel_values = []
    for sample in raw_data:
        # collect values and add to channel_values list
        channel_values.append(sample[channel])
    # convert to NumPy array
    np_channel_values = np.array(channel_values)

    return np_channel_values
# ========================================================================================


# ====================== CALCULATION FUNCTIONS

# function to calculate Mean Absolute Value (MAV)
def calculate_mav(raw_data):
    mav_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        # calculate MAV and add values to mav_results list
        mav_results.append(np.mean(abs(np_channel_values)))

    return mav_results

# function to calculate Root Mean Square (RMS) value
def calculate_rms(raw_data):
    rms_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        # calculate RMS and add values to rem_results list
        rms_results.append(np.sqrt(np.mean(np_channel_values**2)))

    return rms_results

# function to calculate Integrated EMG (IEMG) values
def calculate_iemg(raw_data):
    iemg_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        # calculate IEMG and add values to iemg_results list
        iemg_results.append(np.sum(np.abs(np_channel_values)))

    return iemg_results

# function to calculate Variance (VAR)
def calculate_var(raw_data):
    var_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        # calculate VAR and add values to var_results list
        var_results.append(np.var(np_channel_values))

    return var_results

# calculate Waveform Length (WL)
def calculate_wl(raw_data):
    wl_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        waveform_length = 0
        # 39 gaps in 40 samples
        for i in range(39):
            waveform_length += abs(np_channel_values[i+1] - np_channel_values[i])

        wl_results.append(waveform_length)

    return wl_results

# calculate Zero Crossings (ZC)
def calculate_zc(raw_data):
    zc_results = []

    # for all channels (8)
    for channel in range(8):
        np_channel_values = get_channel_values(raw_data, channel)
        # threshold assigned to the current channel
        threshold = zc_thresholds[channel]
        count = 0

        # compare the signs of the current_value and next_value
        for i in range(len(np_channel_values) - 1):
            current_value = np_channel_values[i]
            next_value = np_channel_values[i+1]

            # count ZC when the values have opposite sign and the difference > threshold
            if (
                current_value * next_value < 0
                and abs(next_value - current_value) >= threshold
                ):
                    count += 1

        zc_results.append(count)

    return zc_results
# ========================================================================================


# ====================== MYO DATA PROCESSING 
# function to get the raw data and do the calculations
def process_myo_data(emg, movement):
    # append sample data to the list
    raw_data.append(emg)
    # if more than 40 samples remove the oldest one
    if len(raw_data) > 40:
        raw_data.pop(0)
    # calculate and add to csv at 40 samples
    if len(raw_data) == 40:
        mav_values = calculate_mav(raw_data)
        rms_values = calculate_rms(raw_data)
        iemg_values = calculate_iemg(raw_data)
        var_values = calculate_var(raw_data)
        wl_values = calculate_wl(raw_data)
        zc_values = calculate_zc(raw_data)

        csv_row = mav_values + rms_values + iemg_values + var_values + wl_values + zc_values
        # write to csv
        add_to_csv(csv_row)
# ========================================================================================


# ====================== MAIN FUNCTION
def main():
    myo = Myo(mode=emg_mode.RAW)
    myo.connect()

    myo.add_emg_handler(process_myo_data)

    try:
        # run the program
        while True:
            myo.run()

    # until program is stopped with Ctrl+C
    except KeyboardInterrupt:
        print("\nQuitting...")

    # disconect Myo armband (without this it never turns off)
    finally:
        myo.disconnect()


if __name__ == "__main__":
    main()

# ========================================================================================

# print EMG data
# def print_raw_data(emg, movement):
#     print(emg)