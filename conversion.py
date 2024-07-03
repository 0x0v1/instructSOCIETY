import binascii

def exe_to_hex(input_file, output_hex_file):
    # Read the binary content of the input executable file
    try:
        with open(input_file, 'rb') as exe_file:
            binary_data = exe_file.read()
    except FileNotFoundError:
        print("Input executable file not found.")
        return

    # Convert binary data to HEX and write to a HEX file
    hex_data = binascii.hexlify(binary_data).decode('utf-8')
    with open(output_hex_file, 'w') as hex_file:
        hex_file.write(hex_data)

    print(f"Conversion to HEX complete. HEX data written to {output_hex_file}")

def hex_to_xyz(input_hex_file, output_xyz_file, downsampling_factor=1):
    # Check if the downsampling factor is within the valid range (1 to 10)
    if downsampling_factor not in range(1, 11):
        print("Invalid downsampling factor. Please choose a value between 1 and 10.")
        return

    # Read HEX data from the input file
    try:
        with open(input_hex_file, 'r') as hex_file:
            hex_data = hex_file.read()
    except FileNotFoundError:
        print("Input HEX file not found.")
        return

    # Convert HEX data to XYZ coordinates with downsampling
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

    # Write XYZ data to a file
    with open(output_xyz_file, 'w') as xyz_file:
        for point in points:
            xyz_file.write(f"{point[0]} {point[1]} {point[2]}\n")

    print(f"Conversion to XYZ complete. Points written to {output_xyz_file}")

if __name__ == '__main__':
    # Get input parameters from the user
    input_exe_file = input("Enter the path to the input executable file: ")
    hex_file_name = "output.hex"
    xyz_file_name = "output.xyz"

    try:
        # Get and validate the downsampling factor input
        downsampling_factor = int(input("Enter the downsampling factor (1-10): "))
        if downsampling_factor not in range(1, 11):
            raise ValueError
    except ValueError:
        print("Invalid input. Downsampling factor must be an integer between 1 and 10.")
        exit()

    # Perform the conversion steps
    exe_to_hex(input_exe_file, hex_file_name)
    hex_to_xyz(hex_file_name, xyz_file_name, downsampling_factor)
