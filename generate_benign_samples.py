# WINDOWS ONLY

import numpy as np
import os
from PIL import Image
import math
import hashlib

PATH = 'C:\\Windows\\System32'
SAVE_PATH = './benign_samples'
NUM_SAMPLES = 10000

# 1. Vectorize the file and read bytes
def vectorize_file(buffer):
    return np.frombuffer(buffer, dtype=np.uint8)

# 2. Calculate the image's width and height 
def calculate_image_dimensions(path):
    size_b = os.path.getsize(path)
    size_kb = size_b / 1024

    if size_kb < 10:
        width = 32
    elif size_kb >= 10 and size_kb < 30:
        width = 64
    elif size_kb >= 30 and size_kb < 60:
        width = 128
    elif size_kb >= 60 and size_kb < 100:
        width = 256
    elif size_kb >= 100 and size_kb < 200:
        width = 384
    elif size_kb >= 200 and size_kb < 500:
        width = 512 
    elif size_kb >= 500 and size_kb < 1000:
        width = 768
    else:
        width = 1024

    height = math.ceil(size_b / width)
    return height, width

# 3. Fill-in the missing bytes
def fill_missing_bytes(vector, H, W):
    N = len(vector)
    return np.pad(vector, (0, H*W-N), 'constant', constant_values=0)

# 4. Create the matrix
def generate_matrix(vector, H, W):
    return vector.reshape(H, W)

# 5. Generate the image
def generate_image(matrix):
    return Image.fromarray(matrix, mode='L')

# Pipeline
def generate_sample(path, buffer):
    vector = vectorize_file(buffer)
    height, width = calculate_image_dimensions(path)
    full_vector = fill_missing_bytes(vector, height, width)
    matrix = generate_matrix(full_vector, height, width)
    img = generate_image(matrix)
    return img

if __name__ == '__main__':
    sample_num = 0
    os.makedirs(SAVE_PATH, exist_ok=True)

    stop_execution = False

    for root, dirs, files in os.walk(PATH):
        if stop_execution:
            break

        for file in files:
            if sample_num >= NUM_SAMPLES:
                stop_execution = True
                break

            if file.lower().endswith(('.exe', '.dll')):
                full_path = os.path.join(root, file)

                try:
                    if os.path.getsize(full_path) == 0:
                        continue

                    with open(full_path, 'rb') as binary:
                        byte_buffer = binary.read()

                        hash_name = hashlib.sha256(byte_buffer).hexdigest()+'.png'
                        save_file_path = os.path.join(SAVE_PATH, hash_name)

                        if not os.path.exists(save_file_path):
                            img = generate_sample(full_path, byte_buffer)
                            img.save(save_file_path)
                            sample_num+=1   

                except (PermissionError, OSError, TypeError) as e:
                    print(f'Error accediendo a {full_path}: {e}')
