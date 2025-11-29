#!/usr/bin/env python
"""
Script untuk memotong file CSV besar menjadi beberapa bagian kecil.
Menggunakan chunk reading untuk menghindari MemoryError.
"""

import pandas as pd
import os

input_file = r'data/Final_Augmented_dataset_Diseases_and_Symptoms.csv'
chunk_size = 82000  # baris per bagian
output_prefix = r'data/Final_Augmented_part'

print(f"Memotong file: {input_file}")
print(f"Chunk size: {chunk_size} baris per bagian")
print()

part_num = 1
total_rows = 0

# Baca file dalam chunks
for chunk in pd.read_csv(input_file, chunksize=chunk_size):
    output_file = f'{output_prefix}_{part_num}.csv'
    chunk.to_csv(output_file, index=False)
    
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Part {part_num}: {len(chunk):,} baris, {file_size_mb:.2f} MB")
    
    total_rows += len(chunk)
    part_num += 1

print()
print(f"✅ Selesai! Total {part_num - 1} bagian, {total_rows:,} baris")
