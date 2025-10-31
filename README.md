# EE-623_Assignment_1

This repository contains the complete submission for the EE623 (Speech Processing) assignment, focusing on the phonetic analysis of vowels and plosives in Hindi. The primary objective is to record and analyze Hindi speech sounds using short-time and cepstral analysis techniques to estimate key acoustic parameters like pitch ($F_0$) and formant frequencies (F1, F2, F3).

The analysis employs three methods:

Visual Spectrogram Analysis in Praat (Narrow-band for pitch, Wide-band for formants).

Computational Pitch Estimation using the Average Magnitude Difference Function (AMDF), implemented in Python.

Source-Filter Separation using Cepstral Analysis in Python to find the average $F_0$ and formant values over multiple frames.

## 1. Voice Sample Data (Deliverable)

This repository contains a collection of voice samples recorded for the assignment, located in the /data directory.

Language: Hindi

Recording Tool: Praat

Recording Parameters: 44.1 kHz sampling frequency, 16-bit resolution, mono.

Targeted Phonemes (from Report Section 2.2)

<table>
<thead>
<tr>
<th>Filename (in <code>/data</code>)</th>
<th>Hindi Phoneme</th>
<th>Description</th>
<th>Avg. Pitch (from Praat)</th>
</tr>
</thead>
<tbody>
<tr>
<td><code>vowel_a.wav</code></td>
<td><strong>अ</strong></td>
<td>Vowel (Unrounded low central)</td>
<td>131.5 Hz</td>
</tr>
<tr>
<td><code>vowel_aa.wav</code></td>
<td><strong>आ</strong></td>
<td>Vowel (Long, open)</td>
<td>119.2 Hz</td>
</tr>
<tr>
<td><code>vowel_i.wav</code></td>
<td><strong>इ</strong></td>
<td>Vowel (Unrounded high front)</td>
<td>133.9 Hz</td>
</tr>
<tr>
<td><code>vowel_ee.wav</code></td>
<td><strong>ई</strong></td>
<td>Vowel (Long, high front)</td>
<td>135.7 Hz</td>
</tr>
<tr>
<td><code>vowel_e.wav</code></td>
<td><strong>ए</strong></td>
<td>Vowel (Unrounded front)</td>
<td>125.9 Hz</td>
</tr>
<tr>
<td><code>vowel_ae.wav</code></td>
<td><strong>ऐ</strong></td>
<td>Vowel (Unrounded front)</td>
<td>137.9 Hz</td>
</tr>
<tr>
<td><code>plosive_k.wav</code></td>
<td><strong>क</strong></td>
<td>Plosive (Velar, Unaspirated, Voiceless)</td>
<td>136.2 Hz</td>
</tr>
<tr>
<td><code>plosive_kha.wav</code></td>
<td><strong>ख</strong></td>
<td>Plosive (Velar, Aspirated, Voiceless)</td>
<td>129.9 Hz</td>
</tr>
<tr>
<td><code>plosive_g.wav</code></td>
<td><strong>ग</strong></td>
<td>Plosive (Velar, Unaspirated, Voiced)</td>
<td>129.5 Hz</td>
</tr>
</tbody>
</table>

## 2. Python Codebase (Deliverable)

The Python scripts for the computational analysis are located in the /codebase directory.

Prerequisites

The code requires Python 3 and the following libraries:

numpy
scipy
matplotlib

You can install these dependencies using pip:

pip install numpy scipy matplotlib


How to Run

Objective 1: AMDF Pitch Analysis

This script (amdf_pitch_analysis.py) analyzes a single frame of a vowel to find its pitch using the AMDF method.

Prepare: Place the vowel_a.wav file (from the /data folder) into the /codebase folder.

Run:

python amdf_pitch_analysis.py


Output: The script will print the calculated $F_0$ (in Hz) and pitch period $T_0$ (in samples) to the console. It will also save a plot named amdf_plot.png showing the AMDF curve and the detected minimum.

Objective 2: Cepstral Analysis

This script (cepstral_analysis_v3.py) analyzes 6 consecutive frames of a vowel to find the average pitch and formant frequencies (F1, F2, F3).

Prepare: Ensure vowel_a.wav is in the /codebase directory. The script is pre-set to start its analysis at 1.18s.

Run:

python cepstral_analysis_v3.py


Output: The script will print a final table of the averaged F0, F1, F2, and F3 values to the console. It will also save a composite image named cepstral_analysis_corrected.png containing all 12 plots (6 cepstral sequences and 6 smoothed spectra).

3. Summary of Results (Vowel 'अ')

The final report presents a detailed comparison of all three methods. The results for the vowel 'अ' are highly consistent, validating the analysis.

<table>
<thead>
<tr>
<th>Method</th>
<th>Pitch ($F_0$)</th>
<th>Formant 1 (F1)</th>
<th>Formant 2 (F2)</th>
<th>Formant 3 (F3)</th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>Obj 1 (Praat Visual)</strong></td>
<td>131.5 Hz</td>
<td>~622.7 Hz</td>
<td>~2554 Hz</td>
<td>~3783 Hz</td>
</tr>
<tr>
<td><strong>Obj 1 (AMDF Script)</strong></td>
<td>131.25 Hz</td>
<td>-</td>
<td>-</td>
<td>-</td>
</tr>
<tr>
<td><strong>Obj 2 (Cepstral Script)</strong></td>
<td>129.47 Hz</td>
<td>732.13 Hz</td>
<td>2311.23 Hz</td>
<td>3617.58 Hz</td>
</tr>
</tbody>
</table>
