import csv
from pathlib import Path


# ====================== VARIABLES ======================
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

# combined csv headers
combined_headers = ["timestamp","name","session","label","phase","repetition","fatigue",
           "ch_01","ch_02","ch_03","ch_04","ch_05","ch_06","ch_07","ch_08"]

# feature csv headers
features_headers = ["name", "session", "label", "repetition", 
                    "01_mav", "02_mav", "03_mav", "04_mav", "05_mav", "06_mav", "07_mav", "08_mav", 
                    "01_rms", "02_rms", "03_rms", "04_rms", "05_rms", "06_rms", "07_rms", "08_rms",
                    "01_iemg", "02_iemg", "03_iemg", "04_iemg", "05_iemg", "06_iemg", "07_iemg", "08_iemg",
                    "01_var", "02_var", "03_var", "04_var", "05_var", "06_var", "07_var", "08_var",
                    "01_wl", "02_wl", "03_wl", "04_wl", "05_wl", "06_wl", "07_wl", "08_wl",
                    "01_zc", "02_zc", "03_zc", "04_zc", "05_zc", "06_zc", "07_zc", "08_zc"]

# path to combined csv
combined_path = Path("data/combined_data.csv")
# path to non-overlapping csv
nsw_path = Path("data/feature_nsw.csv")
# path to overlapping csv
osw_path = Path("data/feature_osw.csv")


# ====================== COMBINE CSV ======================
# function to combine and clean CSV session files
def combine_cleaned_csv():
    # create combined csv file
    with open (combined_path, "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        # write the headers into the csv file
        csv_writer.writerow(combined_headers)

        # open each session file
        for session in session_files:
            with open(session, newline="") as sessionfile:
                # Dictreader looks up each value by its column name
                reader = csv.DictReader(sessionfile)

                # skip rows where "phase" = "moving" or "label" = "neutral"
                for row in reader:
                    if row["phase"].strip() == "moving":
                        continue
                    if row["label"].strip() == "neutral":
                        continue

                    # write row
                    csv_writer.writerow([row[column] for column in combined_headers])


# ====================== FEATURE CSV ======================
# function to write headers into feature CSV files
def create_feature_csv(filepath):
    with open(filepath, "w", newline="") as nswfile:
        csv_writer = csv.writer(nswfile)
        # write headers into the csv file
        csv_writer.writerow(features_headers)

# ====================== SLIDING WINDOWS ======================
# non-overlapping sliding window

# overlapping sliding window

# ====================== MAIN ======================
def main():
    combine_cleaned_csv()
    create_feature_csv(nsw_path)
    create_feature_csv(osw_path)


if __name__ == "__main__":
    main()
