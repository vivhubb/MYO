from pyomyo import Myo, emg_mode

armband = Myo(mode=emg_mode.RAW)

armband.connect()
print("Myo connected.")
armband.power_off()
print("Myo sent do deep sleep.")
