import csv

# session files
session_files = [
    "data/sessions/training/v_session_01.csv",
    "data/sessions/training/v_session_02.csv",
    "data/sessions/training/v_session_03.csv",
    "data/sessions/training/v_session_04.csv",
    "data/sessions/training/vivienne_session_01.csv",
    "data/sessions/training/vivienne_session_02.csv",
    "data/sessions/training/vivienne_session_03.csv",
    "data/sessions/training/vivienne_session_04.csv",
    "data/sessions/training/vivienne_session_05.csv",
    "data/sessions/training/vivienne_session_06.csv",
    "data/sessions/training/vivienne_session_07.csv",
    "data/sessions/training/vivienne_session_08.csv"
]

# csv headers
headers = ["timestamp","name","session","label","phase","repetition","fatigue",
           "ch_01","ch_02","ch_03","ch_04","ch_05","ch_06","ch_07","ch_08"]

# function to combine and clean CSV session files
def combine_cleaned_csv():
    # create combined csv file
    with open ("data/combined_data.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # write the headers into the csv file
        csv_writer.writerow(headers)

        # open each session file
        for session in session_files:
            with open(session, newline="") as sessionfile:
                # Dictreader looks up each value by its column name
                reader = csv.DictReader(sessionfile)

                # skip rows where "phase" = "moving"
                for row in reader:
                    if row["phase"].strip() == "moving":
                        continue

                    # write row
                    csv_writer.writerow([row[column] for column in headers])

combine_cleaned_csv()
