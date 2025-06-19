import csv
from pathlib import Path
import sys
import os

def convert_can_log_to_csv(input_file_path, output_file_path):
    # Verify input file exists
    if not Path(input_file_path).is_file():
        print(f"Error: Input file '{input_file_path}' does not exist.")
        return

    # Ensure output directory exists
    output_dir = Path(output_file_path).parent
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory '{output_dir}': {e}")
        return

    # First pass: Read messages, collect timestamps, and compute windows
    messages = []
    can_id_timestamps = {}  # Store timestamps for each CAN ID
    window_counts = {}      # Store message counts per CAN ID per window
    try:
        with open(input_file_path, 'r', encoding='utf-8') as log_file:
            for line in log_file:
                line = line.strip()
                if not line or not line.startswith('('):
                    continue
                try:
                    timestamp_end = line.find(')')
                    timestamp = line[1:timestamp_end]
                    remaining = line[timestamp_end+1:].strip()
                    parts = remaining.split(maxsplit=1)
                    if len(parts) == 2:
                        interface = parts[0]
                        can_data = parts[1]
                        if '#' in can_data:
                            can_id, payload = can_data.split('#', 1)
                            timestamp_float = float(timestamp)
                            messages.append({
                                'timestamp': timestamp_float,
                                'interface': interface,
                                'can_id': can_id,
                                'payload': payload
                            })
                            # Store timestamp for CAN ID
                            if can_id not in can_id_timestamps:
                                can_id_timestamps[can_id] = []
                            can_id_timestamps[can_id].append(timestamp_float)
                            # Compute window and update counts
                            window = int(timestamp_float // 10)
                            if can_id not in window_counts:
                                window_counts[can_id] = {}
                            window_counts[can_id][window] = window_counts[can_id].get(window, 0) + 1
                except:
                    continue
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if not messages:
        print("No valid messages found in the log file.")
        return

    # Compute CAN_ID_Inter_Arrival and mean per CAN ID
    can_id_inter_arrivals = {}
    can_id_means = {}
    all_means = []
    for can_id, timestamps in can_id_timestamps.items():
        timestamps = sorted(timestamps)
        inter_arrivals = []
        if len(timestamps) >= 2:
            # Calculate differences
            for i in range(1, len(timestamps)):
                diff = round(timestamps[i] - timestamps[i-1], 6)
                inter_arrivals.append(max(diff, 0.0))
            # Calculate mean for this CAN ID
            mean_inter_arrival = round(sum(inter_arrivals) / len(inter_arrivals), 6)
            can_id_means[can_id] = mean_inter_arrival
            all_means.append(mean_inter_arrival)
            # First message gets the mean, others get actual differences
            inter_arrivals = [mean_inter_arrival] + inter_arrivals
        else:
            # Single message: Will assign dataset-wide mean later
            inter_arrivals = [0.0]  # Placeholder
        can_id_inter_arrivals[can_id] = inter_arrivals

    # Calculate dataset-wide mean for single-message CAN IDs
    dataset_mean = round(sum(all_means) / len(all_means), 6) if all_means else 0.0001  # Fallback
    for can_id in can_id_timestamps:
        if len(can_id_timestamps[can_id]) == 1:
            can_id_means[can_id] = dataset_mean
            can_id_inter_arrivals[can_id] = [dataset_mean]

    # Second pass: Write to CSV
    try:
        # Check if output file is writable
        if Path(output_file_path).exists():
            try:
                with open(output_file_path, 'a') as test_file:
                    pass
            except PermissionError:
                print(f"Warning: Output file '{output_file_path}' may be read-only.")
                print("Suggestions:")
                print("- Close applications using the file (e.g., Excel).")
                print("- Pause OneDrive sync temporarily.")
                print("- Delete or rename the existing file.")
                print("- Check file permissions (Properties > Security).")
                print("- Use the alternative output path (e.g., 'C:\\Temp').")

        with open(output_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow([
                'Timestamp', 'Interface', 'CAN_ID', 'Payload', 'CAN_ID_Inter_Arrival', 'CAN_ID_Window_Count'
            ])

            # Track index for each CAN ID
            can_id_indices = {can_id: 0 for can_id in can_id_timestamps}
            for msg in messages:
                timestamp = msg['timestamp']
                interface = msg['interface']
                can_id = msg['can_id']
                payload = msg['payload']
                window = int(timestamp // 10)

                # CAN_ID_Inter_Arrival
                try:
                    current_index = can_id_indices[can_id]
                    can_id_inter_arrival = can_id_inter_arrivals[can_id][current_index]
                    can_id_indices[can_id] += 1
                except (KeyError, IndexError):
                    can_id_inter_arrival = can_id_means.get(can_id, dataset_mean)

                # CAN_ID_Window_Count
                window_count = window_counts.get(can_id, {}).get(window, 1)

                writer.writerow([
                    timestamp,              # Float, no quotes
                    f'="{interface}"',     # Quoted string
                    f'="{can_id}"',        # Quoted string
                    f'="{payload}"',       # Quoted string
                    can_id_inter_arrival,  # Float
                    window_count           # Integer
                ])
        print(f"✅ Conversion complete! CSV saved to: {output_file_path}")
        
        # Verify file is not read-only
        if os.access(output_file_path, os.W_OK):
            print("File is writable.")
        else:
            print("Warning: File may be read-only. Check permissions or OneDrive sync.")
    except PermissionError as e:
        print(f"PermissionError: Cannot write to '{output_file_path}'. {e}")
        print("Suggestions:")
        print("- Ensure the output file is not open in another application (e.g., Excel).")
        print("- Check write permissions for the directory.")
        print("- Try running the script as Administrator.")
        print("- Pause OneDrive sync temporarily.")
        print("- Use a different output path (e.g., 'C:\\Temp\\dosattack_data_canid_frequency.csv').")
        sys.exit(1)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    # Define input and output paths
    input_file_path = r"C:\Users\pc\OneDrive\Images\Bureau\VS_code_Projects\MLproject_Predictive_Maintenance_for_Vehicles_Using_CAN_Bus_Data\dataSet\raw\dos\full_data_capture.log"
    output_file_path = r"C:\Users\pc\OneDrive\Images\Bureau\VS_code_Projects\MLproject_Predictive_Maintenance_for_Vehicles_Using_CAN_Bus_Data\dataSet\raw\dos\IA_WC_normal.csv"
    
    convert_can_log_to_csv(input_file_path, output_file_path)

if __name__ == "__main__":
    main()
