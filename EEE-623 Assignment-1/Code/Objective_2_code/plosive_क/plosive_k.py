import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import find_peaks

# --- 1. USER SETTINGS: Modified for 'plosive_k' ---

# Make sure this WAV file is in the same folder as this Python script
# You must save "Sound plosive_क" from Praat as "plosive_k.wav"
FILENAME = 'plosive_k.wav'

# This is the stable middle point of the VOWEL in "ka"
# From your Praat screenshot, this is around 1.01s
START_TIME_S = 1.01

# --- 2. ANALYSIS PARAMETERS (Based on your assignment) ---

# "Considering at least 6 consecutive frames"
NUM_FRAMES = 6

# A standard frame size (20-30ms). 30ms is a good choice.
FRAME_DURATION_S = 0.030

# A standard frame shift (10-15ms).
FRAME_SHIFT_S = 0.010 # 10ms

# N-point FFT. Must be a power of 2 >= frame_size
N_FFT = 2048

# This is the "low-time lifter" cutoff. It separates the
# "low quefrency" (formants) from the "high quefrency" (pitch).
LIFTER_CUTOFF_SAMPLES = 40

# Pitch search range (from our Objective 1 success)
# Your Praat image shows F0 = 136.2 Hz, so this range is perfect.
MIN_PITCH_HZ = 100
MAX_PITCH_HZ = 160

# --- 3. LOAD AUDIO FILE ---

try:
    # Read the WAV file. sample_rate will be 44100.
    sample_rate, data = wavfile.read(FILENAME)
except FileNotFoundError:
    print(f"Error: The file '{FILENAME}' was not found.")
    print("Please save your 'Sound plosive_क' as 'plosive_k.wav' in the same folder.")
    exit()

# If the audio is stereo (2 channels), just take the first channel.
if data.ndim > 1:
    data = data[:, 0]

# Normalize data to float (-1.0 to 1.0)
if np.issubdtype(data.dtype, np.integer):
    data = data.astype(np.float32) / 32768.0
else:
    data = data.astype(np.float32)

# --- 4. PREPARE FOR ANALYSIS ---

# Convert our time-based parameters (seconds) into sample-based parameters
frame_size = int(FRAME_DURATION_S * sample_rate)
frame_shift = int(FRAME_SHIFT_S * sample_rate)
start_sample = int(START_TIME_S * sample_rate)

# Convert pitch search range (Hz) to lag range (samples)
min_lag = int(sample_rate / MAX_PITCH_HZ) # e.g., 44100 / 160 = 275 samples
max_lag = int(sample_rate / MIN_PITCH_HZ) # e.g., 44100 / 100 = 441 samples

# Create the Hamming window for tapering the frames
window = np.hamming(frame_size)

# Create the frequency axis for plotting (from 0 Hz to Nyquist)
freq_axis = np.fft.rfftfreq(N_FFT, 1.0 / sample_rate)

# Lists to store results from each frame for final averaging
results_f0 = []
results_f1 = []
results_f2 = []
results_f3 = []

# Create the 6x2 plot grid
fig, axes = plt.subplots(NUM_FRAMES, 2, figsize=(15, 20))
fig.suptitle(f'Objective 2: Framewise Cepstral Analysis for "{FILENAME}"', fontsize=20, y=1.02)

# --- 5. LOOP OVER 6 CONSECUTIVE FRAMES ---

print(f"Analyzing {NUM_FRAMES} frames from '{FILENAME}'...")

for i in range(NUM_FRAMES):

    # --- Step 1: Get a Frame ---
    current_start = start_sample + (i * frame_shift)
    current_end = current_start + frame_size
    if current_end > len(data):
        print(f"Warning: Reached end of audio file at frame {i+1}.")
        break
    frame = data[current_start:current_end] * window

    # --- Step 2: Get Log Spectrum ---
    frame_fft = np.fft.rfft(frame, n=N_FFT)
    log_spectrum = np.log(np.abs(frame_fft) + 1e-6)

    # --- Step 3: Get Real Cepstrum ("Cepstral Sequence") ---
    real_cepstrum = np.fft.irfft(log_spectrum, n=N_FFT)

    # --- Step 4: Find Pitch from Cepstrum ---
    pitch_peak_index = np.argmax(real_cepstrum[min_lag:max_lag]) + min_lag
    pitch_period_samples = pitch_peak_index
    f0 = sample_rate / pitch_period_samples
    results_f0.append(f0)

    # Plot the Cepstral Sequence (Left Column)
    ax = axes[i, 0]
    ax.plot(real_cepstrum)
    ax.axvline(pitch_period_samples, color='r', linestyle='--', label=f'Pitch Peak (T0 = {pitch_period_samples} samples)')
    ax.set_title(f'Frame {i+1}: Real Cepstrum (F0 = {f0:.2f} Hz)')
    ax.set_xlabel('Quefrency (samples, n)')
    ax.set_ylabel('Amplitude')
    ax.set_xlim(0, max_lag + 100)
    ax.legend(loc='upper right')

    # --- Step 5: Get Smoothed Spectrum (Liftering) ---
    lifter = np.zeros(N_FFT)
    lifter[0:LIFTER_CUTOFF_SAMPLES] = 1.0
    liftered_cepstrum = real_cepstrum * lifter

    # This is the correct, bug-fixed line
    smoothed_spectrum = np.fft.rfft(liftered_cepstrum, n=N_FFT).real

    # --- Step 6: Find Formants from Smoothed Spectrum ---
    min_dist_samples = int(400 / (sample_rate / N_FFT)) # 400 Hz min distance

    # We will find all peaks (no height minimum, as it caused 'nan' errors)
    peaks, _ = find_peaks(smoothed_spectrum, distance=min_dist_samples)

    # Store the first three formants found
    if len(peaks) >= 3:
        f1 = freq_axis[peaks[0]]
        f2 = freq_axis[peaks[1]]
        f3 = freq_axis[peaks[2]]
        results_f1.append(f1)
        results_f2.append(f2)
        results_f3.append(f3)
        formant_text = f'F1={f1:.0f} Hz, F2={f2:.0f} Hz, F3={f3:.0f} Hz'
    else:
        formant_text = 'Could not find 3 formants'

    # Plot the Smoothed Spectrum (Right Column)
    ax = axes[i, 1]
    ax.plot(freq_axis, smoothed_spectrum, 'r', label='Smoothed Spectrum (Formants)')
    ax.plot(freq_axis[peaks[:3]], smoothed_spectrum[peaks[:3]], 'kx', markersize=10, mew=2, label='Formant Peaks')
    ax.set_title(f'Frame {i+1}: Cepstrally Smoothed Spectrum')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Log Magnitude (relative)')
    ax.set_xlim(0, 5000) # Use 5000 Hz to match your Praat images
    ax.text(0.5, 0.9, formant_text, transform=ax.transAxes, ha='right', fontsize=10, bbox=dict(facecolor='white', alpha=0.8))
    ax.legend(loc='upper right')

print("Analysis complete. Saving plot...")

# --- 6. SAVE PLOTS AND CALCULATE AVERAGES ---

plt.tight_layout(rect=[0, 0, 1, 0.98]) # Adjust layout
plot_filename = 'cepstral_analysis_k.png' # Changed filename
plt.savefig(plot_filename)
print(f"All {NUM_FRAMES*2} plots saved to '{plot_filename}'")

# Calculate averages
avg_f0 = np.mean(results_f0)
avg_f1 = np.mean(results_f1)
avg_f2 = np.mean(results_f2)
avg_f3 = np.mean(results_f3)

# Print the final table for your report
print("\n--- Final Averages (for your report) ---")
print(f"Average Pitch (F0): {avg_f0:.2f} Hz")
print(f"Average Formant 1 (F1): {avg_f1:.2f} Hz")
print(f"Average Formant 2 (F2): {avg_f2:.2f} Hz")
print(f"Average Formant 3 (F3): {avg_f3:.2f} Hz")
print("------------------------------------------")

# Show the plot
plt.show()