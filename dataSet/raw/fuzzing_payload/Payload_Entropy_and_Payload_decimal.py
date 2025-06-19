import csv
from pathlib import Path
import sys
import os
import numpy as np
from scipy.stats import entropy

def calc_entropy(payload):
    if not payload:
        return 0.0
    try:
        bytes_list = [int(payload[i:i+2], 16) for i in range(0, len(payload), 2)]
        value_counts = np.bincount(bytes_list, minlength=256)
        return entropy(value_counts[value_counts > 0])
    except ValueError:
        return 0.0

def payload_to_decimal(payload):
    try:
        return int(payload, 16)
    except ValueError:
        return 0

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

    # First pass: Read messages
    messages = []
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
                except:
                    continue
    except Exception as e:
        print(f"Error reading input file: {e}")
        return

    if not messages:
        print("No valid messages found in the log file.")
        return

    # Second pass: Write to CSV with Payload_Entropy and Payload_Decimal
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
                'Timestamp', 'Interface', 'CAN_ID', 'Payload',
                'Payload_Entropy', 'Payload_Decimal'
            ])

            for msg in messages:
                timestamp = msg['timestamp']
                interface = msg['interface']
                can_id = msg['can_id']
                payload = msg['payload']
                
                # Compute Payload_Entropy
                payload_entropy = calc_entropy(payload)
                payload_entropy = f"{payload_entropy:.5f}"  # Format to 5 decimal places
                
                # Compute Payload_Decimal
                payload_decimal = payload_to_decimal(payload)
                
                writer.writerow([
                    timestamp,                        # Float, no quotes
                    f'"""{interface}"""',            # Triple-quoted string
                    f'"""{can_id}"""',               # Triple-quoted string
                    f'"""{payload}"""',              # Triple-quoted string
                    payload_entropy,                 # Float, 5 decimal places
                    payload_decimal                  # Integer
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
        print("- Use a different output path (e.g., 'C:\\Temp\\suspension_entropy_decimal.csv').")
        sys.exit(1)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

def main():
    # Define input and output paths
    input_file_path = r"dataSet/raw/fuzzing_payload/full_data_capture.log"
    output_file_path = r"dataSet/raw/fuzzing_payload/normal_PE_PD.csv"
    
    convert_can_log_to_csv(input_file_path, output_file_path)

if __name__ == "__main__":
    main()