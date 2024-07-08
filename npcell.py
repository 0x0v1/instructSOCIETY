import matplotlib.pyplot as plt
import numpy as np
import sys

def binary_visualization(file_path):
    try:
        # Read the binary data from the executable file
        with open(file_path, 'rb') as file:
            binary_data = file.read()

        # Convert the binary data to a binary string
        binary_string = ''.join(format(byte, '08b') for byte in binary_data)

        # Calculate the dimensions of the image
        length = len(binary_string)
        width = int(np.ceil(np.sqrt(length)))
        height = int(np.ceil(length / width))

        # Create the image array
        image_array = np.zeros((height, width), dtype=int)

        # Fill the image array with binary values
        for i in range(height):
            for j in range(width):
                if i * width + j < length:
                    image_array[i, j] = int(binary_string[i * width + j])

        return image_array
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

def display_image(image_array):
    plt.imshow(image_array, cmap='gray')
    plt.axis('off')
    plt.show()

if __name__ == '__main__':
    file_path = input("Enter the path of the executable file: ")
    image_array = binary_visualization(file_path)
    display_image(image_array)
