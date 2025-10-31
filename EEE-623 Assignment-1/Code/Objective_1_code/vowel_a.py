import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# --- 1. USER SETTINGS: Change these values ---

# Make sure this WAV file is in the same folder as this Python script
FILENAME = 'vowel_a.wav'

# Picking a stable point in your vowel (in seconds).
# From my Praat image, 1.18s was a good spot for 'vowel_a'.
START_TIME_S = 1.18

# Frame duration (in seconds). 30ms is a good standard.
FRAME_DURATION_S = 0.030

# The range of pitch (F0) to search, in Hz.
# This helps avoid errors from very low/high frequencies.
MIN_PITCH_HZ = 75
MAX_PITCH_HZ = 300

# --- 2. LOAD AND PREPARE AUDIO FRAME ---

# Loading the audio file
try:
    sample_rate, data = wavfile.read(FILENAME)
except FileNotFoundError:
    print(f"Error: The file '{FILENAME}' was not found.")
    exit()

# If the audio is stereo, then I take only the first channel
if data.ndim > 1:
    data = data[:, 0]

# Converting data to floating point (e.g., -1.0 to 1.0)
# This handles different WAV bit-depths (e.g., 16-bit, 32-bit)
if np.issubdtype(data.dtype, np.integer):
    # Normalize 16-bit integer
    data = data.astype(np.float32) / 32768.0
else:
    # Assume it's already float
    data = data.astype(np.float32)

# Calculating frame properties in samples
start_sample = int(START_TIME_S * sample_rate)
frame_size = int(FRAME_DURATION_S * sample_rate)
end_sample = start_sample + frame_size

# Checking if the audio file is long enough
if end_sample > len(data):
    print("Error: The START_TIME_S is too close to the end of the file.")
    exit()

# Extracting the frame
frame = data[start_sample:end_sample]

# Applying a Hamming window to the frame, as is standard
frame = frame * np.hamming(frame_size)

# --- 3. CALCULATE AMDF (Average Magnitude Difference Function) ---

# Converting the F0 range (Hz) to a lag range (samples)
# F0 = sample_rate / lag  =>  lag = sample_rate / F0
max_lag = int(sample_rate / MIN_PITCH_HZ)
min_lag = int(sample_rate / MAX_PITCH_HZ)

# Creating a list of all lags (eta) to check
lag_range = range(min_lag, max_lag + 1)

# This list will hold the AMDF value for each lag
amdf_values = []

print(f"Analyzing frame of {frame_size} samples...")
print(f"Checking lags from {min_lag} to {max_lag} samples...")

# Loop through each lag (eta)
for eta in lag_range:
    
    # This is the AMDF formula from the slide:
    # AMDF(eta) = sum | x[m] - x[m + eta] |
    # We sum over the part of the frame that overlaps.
    
    current_sum = 0
    for m in range(0, frame_size - eta):
        diff = frame[m] - frame[m + eta]
        current_sum += np.abs(diff)
        
    amdf_values.append(current_sum)

# Converting the result list to a NumPy array for easier processing
amdf_values = np.array(amdf_values)

# --- 4. FIND PITCH (F0) ---

# Finding the index of the minimum value in our AMDF results.
# This index corresponds to the lag that gave the best "match".
min_index = np.argmin(amdf_values)

# Get the actual lag (eta) value from that index
# This is our pitch period in samples (eta_min)
eta_min = lag_range[min_index]

# Calculate the final F0 (Pitch) in Hz
f0 = sample_rate / eta_min

print("\n--- Analysis Results ---")
print(f"Minimum AMDF value found at lag (eta): {eta_min} samples")
print(f"Calculated Fundamental Frequency (F0): {f0:.2f} Hz")

# --- 5. PLOT THE RESULTS ---

plt.figure(figsize=(12, 7))
plt.plot(lag_range, amdf_values, 'b', label='AMDF Value')

# Marking the minimum point with a red dot
plt.plot(eta_min, amdf_values[min_index], 'ro', markersize=10, label=f"Minimum (True Pitch Period)")

# Adding annotation text to the plot
plt.annotate(f"Pitch Period: $\eta = {eta_min}$ samples\nCalculated $F_0 = {f0:.2f}$ Hz",
             xy=(eta_min, amdf_values[min_index]),
             xytext=(eta_min + 20, amdf_values[min_index] * 1.5), # Position text
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
             fontsize=12,
             fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

plt.xlabel('Lag (samples, $\eta$)', fontsize=14)
plt.ylabel('AMDF Value (Sum of Absolute Differences)', fontsize=14)
plt.title(f'AMDF Pitch Analysis for "{FILENAME}" at {START_TIME_S}s', fontsize=16)
plt.legend()
plt.grid(True)

# Saving the plot to a file
plot_filename = 'amdf_plot.png'
plt.savefig(plot_filename)
print(f"\nPlot saved as '{plot_filename}'")

# Show the plot
plt.show()