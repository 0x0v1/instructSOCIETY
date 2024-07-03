import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap

def create_unique_colormap(num_colors):
    # Create a custom colormap with 'num_colors' distinct colors
    base_cmap = plt.get_cmap('viridis')
    color_list = [base_cmap(i) for i in np.linspace(0, 1, num_colors)]
    return ListedColormap(color_list)

def create_colored_byteplot(file_path, output_path):
    with open(file_path, 'rb') as file:
        # Read the binary data from the file
        binary_data = file.read()

        # Determine the size of the image
        width = 256  # Assuming 256 bytes per row, adjust as needed
        height = len(binary_data) // width + 1

        # Reshape the binary data into a 2D array
        byte_matrix = np.frombuffer(binary_data, dtype=np.uint8)
        byte_matrix = np.append(byte_matrix, np.zeros(width - len(byte_matrix) % width, dtype=np.uint8))
        byte_matrix = byte_matrix.reshape((height, width))

        # Determine the number of unique colors needed
        num_unique_colors = np.unique(byte_matrix).shape[0]

        # Create a more artistic visualization with a custom colormap
        plt.figure(figsize=(12, 8))

        # Display the byte plot using a custom colormap with unique colors
        cmap = create_unique_colormap(num_unique_colors)
        plt.imshow(byte_matrix, cmap=cmap, aspect='auto', interpolation='none')

        # Add some additional styling for an artistic look
        plt.axis('off')

        # Save the artistic byte plot as a JPEG file
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, format='jpeg', dpi=300)
        plt.show()

if __name__ == "__main__":
    # Prompt the user for the executable path and output path
    executable_path = input("Enter the path to the executable: ")
    output_path = input("Enter the output file name (e.g., output_colored_byteplot.jpeg): ")

    create_colored_byteplot(executable_path, output_path)
