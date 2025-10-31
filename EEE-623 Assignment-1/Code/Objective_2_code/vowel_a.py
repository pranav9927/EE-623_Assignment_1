import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import find_peaks

# --- 1. USER SETTINGS: Please check these ---

# Ensure this WAV file is in the same folder as this script.
# This should be the same vowel 'अ' we've been using.
FILENAME = 'vowel_a.wav'

# This is the stable middle point of your vowel (from Praat)
# e.g., 1.18 seconds from your screenshot
START_TIME_S = 1.18

# --- 2. ANALYSIS PARAMETERS (Based on your assignment) ---

# "Considering at least 6 consecutive frames"
NUM_FRAMES = 6

# A standard frame size (20-30ms). 30ms is a good choice.
FRAME_DURATION_S = 0.030 

# A standard frame shift (10-15ms).
FRAME_SHIFT_S = 0.010 # 10ms

# N-point FFT. Must be a power of 2 >= frame_size
# 2048 is a good high-resolution choice.
N_FFT = 2048 

# This is the "low-time lifter" cutoff. It separates the
# "low quefrency" (formants) from the "high quefrency" (pitch).
# Any value from 30-50 is standard.
LIFTER_CUTOFF_SAMPLES = 40

# Pitch search range (from our Objective 1 success)
# We guide the cepstrum to look for peaks in this valid F0 range.
MIN_PITCH_HZ = 100
MAX_PITCH_HZ = 160

# --- 3. LOAD AUDIO FILE ---

try:
    # Read the WAV file. sample_rate will be 44100.
    sample_rate, data = wavfile.read(FILENAME)
except FileNotFoundError:
    print(f"Error: The file '{FILENAME}' was not found.")
    print("Please save your vowel as a WAV file (e.g., 'vowel_a.wav') in the same folder.")
    exit()

# If the audio is stereo (2 channels), just take the first channel.
if data.ndim > 1:
    data = data[:, 0]

# Normalize data to float (-1.0 to 1.0)
# This handles different WAV bit-depths (e.g., 16-bit, 32-bit float)
if np.issubdtype(data.dtype, np.integer):
    # Normalize 16-bit integer (dividing by 2^15)
    data = data.astype(np.float32) / 32768.0
else:
    # Assume it's already a float
    data = data.astype(np.float32)

# --- 4. PREPARE FOR ANALYSIS ---

# Convert our time-based parameters (seconds) into sample-based parameters
frame_size = int(FRAME_DURATION_S * sample_rate)
frame_shift = int(FRAME_SHIFT_S * sample_rate)
start_sample = int(START_TIME_S * sample_rate)

# Convert pitch search range (Hz) to lag range (samples)
# F0 = sample_rate / lag  =>  lag = sample_rate / F0
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

# Create the 6x2 plot grid (matching the 6 rows of your assignment)
fig, axes = plt.subplots(NUM_FRAMES, 2, figsize=(15, 20))
fig.suptitle('Objective 2: Framewise Cepstral Analysis', fontsize=20, y=1.02)

# --- 5. LOOP OVER 6 CONSECUTIVE FRAMES ---

print(f"Analyzing {NUM_FRAMES} frames...")

for i in range(NUM_FRAMES):
    
    # --- Step 1: Get a Frame ---
    # Calculate the start and end point for this frame
    current_start = start_sample + (i * frame_shift)
    current_end = current_start + frame_size
    
    # Safety check to make sure we don't run off the end of the file
    if current_end > len(data):
        print(f"Warning: Reached end of audio file at frame {i+1}.")
        break
        
    # Extract the frame and apply the Hamming window
    frame = data[current_start:current_end] * window
    
    # --- Step 2: Get Log Spectrum ---
    # Compute the N-point FFT of the frame
    frame_fft = np.fft.rfft(frame, n=N_FFT)
    # Get the log-magnitude spectrum. Add 1e-6 to avoid log(0).
    log_spectrum = np.log(np.abs(frame_fft) + 1e-6)

    # --- Step 3: Get Real Cepstrum (Your "Cepstral Sequence") ---
    # This is the "cepstral sequence" plot (Slide 30, Right)
    # We get it by taking the inverse FFT of the log spectrum.
    real_cepstrum = np.fft.irfft(log_spectrum, n=N_FFT)
    
    # --- Step 4: Find Pitch from Cepstrum ---
    # The pitch peak is the highest spike in the valid "high quefrency" range.
    # We only search between min_lag and max_lag.
    pitch_peak_index = np.argmax(real_cepstrum[min_lag:max_lag]) + min_lag
    pitch_period_samples = pitch_peak_index
    
    # Convert the sample period back to Hz
    f0 = sample_rate / pitch_period_samples
    results_f0.append(f0)
    
    # Plot the Cepstral Sequence (Left Column)
    ax = axes[i, 0]
    ax.plot(real_cepstrum)
    ax.axvline(pitch_period_samples, color='r', linestyle='--', label=f'Pitch Peak (T0 = {pitch_period_samples} samples)')
    ax.set_title(f'Frame {i+1}: Real Cepstrum (F0 = {f0:.2f} Hz)')
    ax.set_xlabel('Quefrency (samples, n)')
    ax.set_ylabel('Amplitude')
    ax.set_xlim(0, max_lag + 100) # Zoom in to see the pitch peak clearly
    ax.legend(loc='upper right')

    # --- Step 5: Get Smoothed Spectrum (Liftering) ---
    # This is the "cepstrally smoothed spectra" (Slide 30, Left, Red Line)
    
    # Create the low-time lifter (a simple low-pass filter)
    lifter = np.zeros(N_FFT)
    # Keep only the low-quefrency components (the formant envelope)
    lifter[0:LIFTER_CUTOFF_SAMPLES] = 1.0 
    
    # Apply lifter to get only the formant info
    liftered_cepstrum = real_cepstrum * lifter
    
    # --- THIS IS THE CORRECTED (BUG-FIXED) LINE ---
    # We FFT the liftered cepstrum back to the spectral domain.
    # We take the .real part (since it should be real) and *do not* log() again.
    smoothed_spectrum = np.fft.rfft(liftered_cepstrum, n=N_FFT).real
    
    # --- Step 6: Find Formants from Smoothed Spectrum ---
    # Find the peaks (F1, F2, F3) in the smoothed envelope.
    
    # Set a minimum distance between peaks (e.g., 400 Hz)
    min_dist_samples = int(400 / (sample_rate / N_FFT)) 
    
    # --- REMOVED THE 'min_height' LINE ---
    
    # We will find all peaks that are at least 400Hz apart
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
plot_filename = 'cepstral_analysis_corrected.png'
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



