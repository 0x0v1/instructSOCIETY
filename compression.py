import subprocess
import sys
import os
import shutil

def compress_glb(input_glb_file, output_compressed_glb_file):
    # Check if the meshopt command-line tool is available
    if not shutil.which("meshopt"):
        print("Error: meshopt tool not found. Please make sure it is installed and in your PATH.")
        return

    # Compress the glb file using meshopt
    try:
        subprocess.run(["meshopt", "-c", input_glb_file, output_compressed_glb_file], check=True)
        print(f"Compression complete. Compressed glb data written to {output_compressed_glb_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error during compression: {e}")
        return

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python compress_glb.py input.glb output_compressed.glb")
    else:
        input_glb_file = sys.argv[1]
        output_compressed_glb_file = sys.argv[2]
        compress_glb(input_glb_file, output_compressed_glb_file)
