import binascii
import subprocess
import sys
import os
import shutil
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

def exe_to_hex(input_file, output_hex_file):
    try:
        with open(input_file, 'rb') as exe_file:
            binary_data = exe_file.read()
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    hex_data = binascii.hexlify(binary_data).decode('utf-8')
    with open(output_hex_file, 'w') as hex_file:
        hex_file.write(hex_data)

    print(f"Conversion to HEX complete. HEX data written to {output_hex_file}")

def hex_to_xyz(input_hex_file, output_xyz_file, downsampling_factor=1):
    if downsampling_factor not in range(1, 11):
        print("Invalid downsampling factor. Please choose a value between 1 and 10.")
        return

    try:
        with open(input_hex_file, 'r') as hex_file:
            hex_data = hex_file.read()
    except Exception as e:
        print(f"Error reading input HEX file: {e}")
        return

    points = []
    for i in range(0, len(hex_data), 6 * downsampling_factor):
        hex_coord = hex_data[i:i + 6]
        try:
            x = int(hex_coord[0:2], 16)
            y = int(hex_coord[2:4], 16)
            z = int(hex_coord[4:6], 16)
            points.append((x, y, z))
        except ValueError:
            print(f"Skipping invalid HEX coordinate: {hex_coord}")

    with open(output_xyz_file, 'w') as xyz_file:
        for point in points:
            xyz_file.write(f"{point[0]} {point[1]} {point[2]}\n")

    print(f"Conversion to XYZ complete. Points written to {output_xyz_file}")

def xyz_to_ply(input_xyz_file, output_ply_file):
    try:
        with open(input_xyz_file, 'r') as xyz_file:
            xyz_data = xyz_file.readlines()
    except Exception as e:
        print(f"Error reading input XYZ file: {e}")
        return

    with open(output_ply_file, 'w') as ply_file:
        ply_file.write("ply\n")
        ply_file.write("format ascii 1.0\n")
        ply_file.write(f"element vertex {len(xyz_data)}\n")
        ply_file.write("property float x\n")
        ply_file.write("property float y\n")
        ply_file.write("property float z\n")
        ply_file.write("end_header\n")

        for xyz_line in xyz_data:
            x, y, z = map(float, xyz_line.split())
            ply_file.write(f"{x} {y} {z}\n")

    print(f"Conversion to PLY complete. Points written to {output_ply_file}")

def compress_glb(input_glb_file, output_compressed_glb_file):
    if not shutil.which("meshopt"):
        print("Error: meshopt tool not found. Please make sure it is installed and in your PATH.")
        return

    try:
        subprocess.run(["meshopt", "-c", input_glb_file, output_compressed_glb_file], check=True, stderr=subprocess.PIPE)
        print(f"Compression complete. Compressed glb data written to {output_compressed_glb_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e.stderr.decode()}")
        return

def create_unique_colormap(num_colors):
    # Create a custom colormap with 'num_colors' distinct colors
    base_cmap = plt.get_cmap('viridis')
    color_list = [base_cmap(i) for i in np.linspace(0, 1, num_colors)]
    return ListedColormap(color_list)

def hilbert_index(coord, shape):
    x, y = coord
    width, height = shape
    index = 0
    for i in range(max(width, height)):
        index <<= 2
        if i < width:
            mask_x = 2 if (x >> (width - 1 - i)) & 1 else 0
            index |= mask_x
        if i < height:
            mask_y = 2 if (y >> (height - 1 - i)) & 1 else 0
            index |= mask_y
    return index

def get_curve_order(shape, curve_choice):
    coords = np.array(list(np.ndindex(shape)))

    curve_options = {
        '1': 'hilbert',
        '2': 'natural',
        '3': 'zigzag',
        '4': 'zorder'
    }

    if curve_choice not in curve_options:
        raise ValueError("Invalid curve choice. Please choose '1' for 'hilbert', '2' for 'natural', '3' for 'zigzag', or '4' for 'zorder'.")

    curve_name = curve_options[curve_choice]

    if curve_name == 'hilbert':
        order = np.argsort(np.array([hilbert_index(coord, shape) for coord in coords]))
    elif curve_name == 'natural':
        order = np.lexsort(coords.T)
    elif curve_name == 'zigzag':
        order = np.argsort(np.array([sum(coord) for coord in coords]))
    elif curve_name == 'zorder':
        order = np.argsort(np.array([np.packbits(np.array(coord) & 1) for coord in coords]))
    else:
        raise ValueError("Invalid curve choice. Please choose 'hilbert', 'natural', 'zigzag', or 'zorder'.")
    
    return order

def create_colored_byteplot(file_path, output_path, curve_choice, colors):
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

        # Get the order of the pixels based on the chosen curve
        pixel_order = get_curve_order(byte_matrix.shape, curve_choice)

        # Create a colormap from user-provided colors or use default
        if colors:
            cmap = ListedColormap(colors)
        else:
            # Default colormap
            num_unique_colors = np.unique(byte_matrix).shape[0]
            cmap = create_unique_colormap(num_unique_colors)

        # Display the byte plot using the specified order and colormap
        plt.figure(figsize=(12, 8))
        plt.imshow(byte_matrix.flatten()[pixel_order].reshape(byte_matrix.shape), cmap=cmap, aspect='auto', interpolation='none')
        plt.axis('off')

        # Save the artistic byte plot as a JPEG file
        plt.savefig(output_path, bbox_inches='tight', pad_inches=0, format='jpeg', dpi=300)
        plt.show()


if __name__ == '__main__':
    print("\033[96mWelcome to the instructionsociety binary visualization tool!\033[0m")

    print("Choose an option:")
    print("1. Convert EXE to XYZ and XYZ to PLY")
    print("2. Visualize binaries using space-filling curves")
    print("3. Compress a GLB file")

    try:
        option = int(input("Enter the option number: "))
    except ValueError:
        print("Invalid option. Exiting.")
        sys.exit(1)

    if option == 1:
        input_exe_file = input("Enter the path to the input executable file: ")

        if not input_exe_file:
            print("Input file path cannot be empty.")
            sys.exit(1)

        hex_file_name = input("Enter the output HEX file name (default: output.hex): ") or "output.hex"
        xyz_file_name = input("Enter the output XYZ file name (default: output.xyz): ") or "output.xyz"

        try:
            downsampling_factor = int(input("Enter the downsampling factor (1-10): "))
            if downsampling_factor not in range(1, 11):
                raise ValueError
        except ValueError:
            print("Invalid input. Downsampling factor must be an integer between 1 and 10.")
            sys.exit(1)

        exe_to_hex(input_exe_file, hex_file_name)
        hex_to_xyz(hex_file_name, xyz_file_name, downsampling_factor)

        convert_to_ply = input("Do you want to convert the XYZ file to PLY? (y/n): ").lower()
        if convert_to_ply == 'y':
            input_xyz_file = xyz_file_name
            ply_file_name = input("Enter the output PLY file name (default: output.ply): ") or "output.ply"
            xyz_to_ply(input_xyz_file, ply_file_name)

    elif option == 2:
        input_binary_file = input("Enter the path to the input binary file: ")
        output_byteplot_file = input("Enter the output colored Byteplot file name (default: colored_byteplot.png): ") or "colored_byteplot.png"
        
        print("Choose a space-filling curve:")
        print("1. Hilbert curve")
        print("2. Natural-order traversal")
        print("3. Zigzag traversal")
        print("4. Z-order curve")

        curve_choice = input("Enter the option number: ")

        if curve_choice not in ['1', '2', '3', '4']:
            print("Invalid choice. Exiting.")
            sys.exit(1)

        colors_input = input("Enter a list of colors in hexadecimal format (e.g., #RRGGBB,#RRGGBB,...) or press Enter for default colors: ")
        colors = colors_input.split(',') if colors_input else []

        create_colored_byteplot(input_binary_file, output_byteplot_file, curve_choice, colors)

    elif option == 3:
        input_glb_file = input("Enter the path to the input GLB file: ")
        output_compressed_glb_file = input("Enter the output compressed GLB file name (default: compressed.glb): ") or "compressed.glb"
        compress_glb(input_glb_file, output_compressed_glb_file)

    else:
        print("Invalid option. Exiting.")
        sys.exit(1)
