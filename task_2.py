import pickle

def rotate_left(byte, shift=2):
    return ((byte << shift) & 0xFF) | (byte >> (8 - shift))

def rotate_right(byte, shift=2):
    return (byte >> shift) | ((byte << (8 - shift)) & 0xFF)

def encrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as f:
        data = f.read()

    encrypted_bytes = bytearray()

    for byte in data:
        shifted = rotate_left(byte, 2)
        encrypted_byte = shifted ^ key
        encrypted_bytes.append(encrypted_byte)

    with open(output_path, 'wb') as pf:
        pickle.dump(encrypted_bytes, pf)

def decrypt_file(input_path, output_path, key):
    with open(input_path, 'rb') as pf:
        encrypted_bytes = pickle.load(pf)

    decrypted_bytes = bytearray()

    for encrypted_byte in encrypted_bytes:
        shifted = encrypted_byte ^ key
        original_byte = rotate_right(shifted, 2)
        decrypted_bytes.append(original_byte)

    with open(output_path, 'wb') as f:
        f.write(decrypted_bytes)