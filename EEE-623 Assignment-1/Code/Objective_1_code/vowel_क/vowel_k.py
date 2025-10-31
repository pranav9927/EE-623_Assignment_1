import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

# --- 1. USER SETTINGS: Changed for 'plosive_k.wav' ---

# Make sure this WAV file is in the same folder as this Python script
# (You may need to save 'Sound plosive_क' as 'plosive_k.wav' from Praat)
FILENAME = 'plosive_k.wav'

# Picking a stable point in the VOWEL part of "ka"
# Your Praat image k.png shows the cursor at 1.010629s. 1.01 is a good start.
START_TIME_S = 1.01

# Frame duration (in seconds). 30ms is a good standard.
FRAME_DURATION_S = 0.030

# The range of pitch (F0) to search, in Hz.
# We set a tight, realistic range based on your Praat measurement (136.2 Hz)
MIN_PITCH_HZ = 100
MAX_PITCH_HZ = 160

# --- 2. LOAD AND PREPARE AUDIO FRAME ---

# Load the audio file
try:
    sample_rate, data = wavfile.read(FILENAME)
except FileNotFoundError:
    print(f"Error: The file '{FILENAME}' was not found.")
    print("Please save your 'Sound plosive_क' as 'plosive_k.wav' in the same folder.")
    exit()

# If the audio is stereo, take only the first channel
if data.ndim > 1:
    data = data[:, 0]

# Convert data to floating point (e.g., -1.0 to 1.0)
if np.issubdtype(data.dtype, np.integer):
    data = data.astype(np.float32) / 32768.0
else:
    data = data.astype(np.float32)

# Calculate frame properties in samples
start_sample = int(START_TIME_S * sample_rate)
frame_size = int(FRAME_DURATION_S * sample_rate)
end_sample = start_sample + frame_size

# Check if the audio file is long enough
if end_sample > len(data):
    print("Error: The START_TIME_S is too close to the end of the file.")
    exit()

# Extract the frame
frame = data[start_sample:end_sample]

# Apply a Hamming window to the frame
frame = frame * np.hamming(frame_size)

# --- 3. CALCULATE AMDF (Average Magnitude Difference Function) ---

# Convert the F0 range (Hz) to a lag range (samples)
max_lag = int(sample_rate / MIN_PITCH_HZ)
min_lag = int(sample_rate / MAX_PITCH_HZ)

# Create a list of all lags (eta) to check
lag_range = range(min_lag, max_lag + 1)

# This list will hold the AMDF value for each lag
amdf_values = []

print(f"Analyzing frame of {frame_size} samples from '{FILENAME}'...")
print(f"Checking lags from {min_lag} to {max_lag} samples...")

# Loop through each lag (eta)
for eta in lag_range:
    
    current_sum = 0
    for m in range(0, frame_size - eta):
        diff = frame[m] - frame[m + eta]
        current_sum += np.abs(diff)
        
    amdf_values.append(current_sum)

# Convert the result list to a NumPy array
amdf_values = np.array(amdf_values)

# --- 4. FIND PITCH (F0) ---

# Find the index of the minimum value
min_index = np.argmin(amdf_values)

# Get the actual lag (eta) value from that index
eta_min = lag_range[min_index]

# Calculate the final F0 (Pitch) in Hz
f0 = sample_rate / eta_min

print("\n--- Analysis Results ---")
print(f"Minimum AMDF value found at lag (eta): {eta_min} samples")
print(f"Calculated Fundamental Frequency (F0): {f0:.2f} Hz")

# --- 5. PLOT THE RESULTS ---

plt.figure(figsize=(12, 7))
plt.plot(lag_range, amdf_values, 'b', label='AMDF Value')

# Mark the minimum point with a red dot
plt.plot(eta_min, amdf_values[min_index], 'ro', markersize=10, label=f"Minimum (True Pitch Period)")

# Add annotation text to the plot
plt.annotate(f"Pitch Period: $\eta = {eta_min}$ samples\nCalculated $F_0 = {f0:.2f}$ Hz",
             xy=(eta_min, amdf_values[min_index]),
             xytext=(eta_min + 10, amdf_values[min_index] * 1.2), # Position text
             arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
             fontsize=12,
             fontweight='bold',
             bbox=dict(boxstyle="round,pad=0.3", fc="yellow", alpha=0.5))

plt.xlabel('Lag (samples, $\eta$)', fontsize=14)
plt.ylabel('AMDF Value (Sum of Absolute Differences)', fontsize=14)
plt.title(f'AMDF Pitch Analysis for "{FILENAME}" at {START_TIME_S}s', fontsize=16)
plt.legend()
plt.grid(True)

# Save the plot to a file
plot_filename = 'amdf_plot_k.png'
plt.savefig(plot_filename)
print(f"\nPlot saved as '{plot_filename}'")

# Show the plot
plt.show()