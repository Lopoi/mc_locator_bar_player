import cv2
import numpy as np
import json
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert video into JSON file with color values")
    parser.add_argument("video_path", help="Path to input video file")
    parser.add_argument("output_json", help="Path to output JSON file")
    parser.add_argument("--rows", type=int, default=5, help="Number of grid rows per frame")
    parser.add_argument("--cols", type=int, default=5, help="Number of grid columns per frame")
    parser.add_argument("--num_frames", type=int, default=10, help="Number of frames to process")
    parser.add_argument("--method", choices=["average", "mode", "black_white"], default="average",
                        help="Color extraction method: 'average' or 'mode' (most common color)")
    return parser.parse_args()

def get_frame_indices(cap, num_frames):
    # Get total number of frames in video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if num_frames > total_frames:
        num_frames = total_frames
    # Evenly spaced frame indices from 0 to total_frames - 1
    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    return indices

def process_cell(cell_pixels, method):
    """
    Process a cell (subdivision of a frame) to compute the color.
    Assumes cell_pixels is a numpy array of shape (h, w, 3) in BGR order.
    Returns a color as a list of 3 integer values in RGB order.
    """
    if method == "average":
        # Compute per-channel average and convert from BGR (OpenCV) to RGB
        avg_color = np.mean(cell_pixels, axis=(0, 1))
        avg_color = [int(round(avg_color[2])), int(round(avg_color[1])), int(round(avg_color[0]))]
        # Convert to hex color string
        return '#' + ''.join(f'{c:02X}' for c in avg_color)
    elif method == "mode":
        # Flatten the cell to a list of pixels then find the most common color.
        # Here, we use numpy.unique to compute unique rows (colors) and counts.
        pixels = cell_pixels.reshape(-1, 3)
        # We use axis=0 unique on rows (colors)
        colors, counts = np.unique(pixels, axis=0, return_counts=True)
        # Get the index with the maximum count
        idx = np.argmax(counts)
        mode_color_bgr = colors[idx].tolist()  # still in BGR
        # Convert BGR to RGB
        mode_color = [mode_color_bgr[2], mode_color_bgr[1], mode_color_bgr[0]]
        # Convert to hex color string
        return '#' + ''.join(f'{c:02X}' for c in mode_color)
    elif method == "black_white":
        # returns black or white based on the average brightness of the cell
        gray_cell = cv2.cvtColor(cell_pixels, cv2.COLOR_BGR2GRAY)
        avg_brightness = np.mean(gray_cell)
        if avg_brightness < 128:
            return '#000000'  # black
        else:
            return '#FFFFFF'  # white
    else:
        raise ValueError("Unsupported method specified.")

def process_frame(frame, rows, cols, method):
    """Divides the frame into a grid and calculates the color of each cell."""
    frame_height, frame_width, _ = frame.shape
    cell_height = frame_height // rows
    cell_width = frame_width // cols

    grid_colors = []
    for i in range(rows):
        row_colors = []
        for j in range(cols):
            # Define cell boundaries (with basic bounds checking)
            y1 = i * cell_height
            y2 = (i + 1) * cell_height if i < rows - 1 else frame_height
            x1 = j * cell_width
            x2 = (j + 1) * cell_width if j < cols - 1 else frame_width

            cell = frame[y1:y2, x1:x2]
            color = process_cell(cell, method)
            row_colors.append(color)
        grid_colors.append(row_colors)
    return grid_colors

def main():
    args = parse_arguments()

    # Open video file
    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return

    # Get frame indices to extract
    frame_indices = get_frame_indices(cap, args.num_frames)
    
    data = {
        "rows": args.rows,
        "columns": args.cols,
        "frames": []
    }

    for idx in frame_indices:
        # Set the frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Could not read frame at index {idx}")
            continue

        # Process the frame by dividing it into a grid and calculating colors
        grid = process_frame(frame, args.rows, args.cols, args.method)
        data["frames"].append({
            "frame_index": int(idx),
            "grid": grid
        })
        print(f"Processed frame {idx}.")

    cap.release()

    # Save the JSON data to file
    with open(args.output_json, "w") as f:
        json.dump(data, f, indent=4)
    print(f"JSON file saved as {args.output_json}")

if __name__ == "__main__":
    main()
