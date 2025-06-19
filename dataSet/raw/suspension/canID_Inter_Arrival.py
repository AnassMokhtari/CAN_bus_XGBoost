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

    # First pass: Read messages and collect timestamps per CAN_ID
    messages = []
    can_id_timestamps = {}  # Store timestamps for each CAN ID
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
                except:
                    continue
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if not messages:
        print("No valid messages found in the log file.")
        return

    # Compute CAN_ID_Inter_Arrival per CAN_ID
    can_id_inter_arrivals = {}
    max_inter_arrivals = {}
    large_gap_count = 0
    max_expected_gap = 5.0  # 5 seconds to detect suspension attack
    for can_id, timestamps in can_id_timestamps.items():
        timestamps = sorted(timestamps)
        inter_arrivals = []
        for i in range(len(timestamps)):
            if i == 0:
                # First message: Use default (0.00001 seconds or 10 µs)
                inter_arrivals.append(0.00001)
                print(f"Debug: CAN_ID={can_id}, Index={i}, Timestamp={timestamps[i]}, First message, Inter_Arrival=0.00001")
            else:
                # Difference to previous message
                diff = timestamps[i] - timestamps[i-1]
                inter_arrivals.append(diff)
                if diff > max_expected_gap:
                    large_gap_count += 1
                    print(f"Warning: Large gap for CAN_ID={can_id}, Index={i}, Timestamp={timestamps[i]}, Prev_Timestamp={timestamps[i-1]}, Inter_Arrival={diff:.5f}")
                print(f"Debug: CAN_ID={can_id}, Index={i}, Timestamp={timestamps[i]}, Prev_Timestamp={timestamps[i-1]}, Inter_Arrival={diff:.5f}")
        can_id_inter_arrivals[can_id] = inter_arrivals
        max_inter_arrivals[can_id] = max(inter_arrivals) if inter_arrivals else 0.00001

    # Print summary of max_inter_arrival per CAN_ID
    print("\nSummary of Maximum CAN_ID_Inter_Arrival per CAN_ID:")
    for can_id, max_inter in max_inter_arrivals.items():
        if max_inter > max_expected_gap:
            print(f"⚠️ CAN_ID={can_id}: max_inter_arrival={max_inter:.5f}s (Possible suspension attack)")
        else:
            print(f"CAN_ID={can_id}: max_inter_arrival={max_inter:.5f}s")

    if large_gap_count > 0:
        print(f"Warning: Found {large_gap_count} inter-arrival times larger than {max_expected_gap}s. Likely indicates a suspension attack.")

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
            writer = csv.writer(csv_file, quoting=csv.QUOTE_MINIMAL, escapechar='\\')
            writer.writerow([
                'Timestamp', 'Interface', 'CAN_ID', 'Payload', 'CAN_ID_Inter_Arrival'
            ])

            # Track index for each CAN_ID
            can_id_indices = {can_id: 0 for can_id in can_id_timestamps}
            for msg in messages:
                timestamp = msg['timestamp']
                interface = msg['interface']
                can_id = msg['can_id']
                payload = msg['payload']
                # Get CAN_ID_Inter_Arrival
                current_index = can_id_indices[can_id]
                can_id_inter_arrival = can_id_inter_arrivals[can_id][current_index]
                can_id_indices[can_id] += 1
                # Format to 5 decimal places
                can_id_inter_arrival = f"{can_id_inter_arrival:.5f}"

                writer.writerow([
                    timestamp,                        # Float, no quotes
                    f'"""{interface}"""',            # Triple-quoted string
                    f'"""{can_id}"""',               # Triple-quoted string
                    f'"""{payload}"""',              # Triple-quoted string
                    can_id_inter_arrival             # Float, 5 decimal places
                ])
        print(f"✅ Conversion complete! CSV saved to: {output_file_path}")
        
        # Verify file is not read-only
        if os.access(output_file_path, os.W_OK):
            print("File is writable.")
        else:
            print("Warning: File is read-only. Check permissions or OneDrive sync.")
    except PermissionError as e:
        print(f"PermissionError: Cannot write to '{output_file_path}'. {e}")
        print("Suggestions:")
        print("- Ensure the output file is not open in another application (e.g., Excel).")
        print("- Check write permissions for the directory.")
        print("- Try running the script as Administrator.")
        print("- Pause OneDrive sync temporarily.")
        print("- Use a different output path (e.g., 'C:\\Temp\\suspension_can_id_inter_arrival.csv').")
        sys.exit(1)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    # Define input and output paths
    input_file_path = r"C:\Users\pc\OneDrive\Images\Bureau\VS_code_Projects\MLproject_Predictive_Maintenance_for_Vehicles_Using_CAN_Bus_Data\dataSet\raw\suspension\full_data_capture.log"
    output_file_path = r"C:\Users\pc\OneDrive\Images\Bureau\VS_code_Projects\MLproject_Predictive_Maintenance_for_Vehicles_Using_CAN_Bus_Data\dataSet\raw\suspension\normal_can_id_inter_arrival.csv"
    
    convert_can_log_to_csv(input_file_path, output_file_path)

if __name__ == "__main__":
    main()