import os
import subprocess
from PIL import Image

def get_zip_order(zip_path):
    """
    Extracts high-precision NTFS timestamps from the ZIP file using 7z.
    """
    cmd = ["7z", "l", "-slt", zip_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    data = []
    current_path = None
    for line in result.stdout.splitlines():
        if line.startswith('Path = '):
            current_path = line.split('=')[1].strip()
        elif line.startswith('Modified = ') and current_path:
            ts = line.split('=')[1].strip()
            # Only include files inside the strips directory
            if current_path.startswith('strips/') and not current_path.endswith('/'):
                data.append((current_path, ts))
            current_path = None
            
    # Sort by timestamp
    data.sort(key=lambda x: x[1])
    return [path.replace('strips/', '') for path, ts in data]

def reassemble():
    zip_path = "/home/ascend-x/Music/shredder_of_truth/shredder_of_truth.zip"
    strips_dir = "/home/ascend-x/Music/shredder_of_truth/strips"
    output_path = "/home/ascend-x/Music/shredder_of_truth/final_reconstruction.png"
    
    print("Extracting order from ZIP metadata...")
    ordered_files = get_zip_order(zip_path)
    
    if not ordered_files:
        print("No image strips found in ZIP metadata.")
        return

    print(f"Loading {len(ordered_files)} images...")
    images = {f: Image.open(os.path.join(strips_dir, f)).convert('RGB') for f in ordered_files}
    
    # Build final image
    widths, heights = zip(*(images[f].size for f in ordered_files))
    total_width = sum(widths)
    max_height = max(heights)
    
    print(f"Creating reassembled image ({total_width}x{max_height})...")
    new_im = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for f in ordered_files:
        new_im.paste(images[f], (x_offset, 0))
        x_offset += images[f].size[0]
        
    new_im.save(output_path)
    print(f"Success! Final photo saved to {output_path}")

if __name__ == "__main__":
    reassemble()
