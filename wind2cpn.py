import os
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

def dms_to_dd(dms_str):
    """Convert DD°MM.MMM' to decimal degrees. Returns None if invalid."""
    try:
        match = re.match(r"(\d+)°(\d+\.\d+)'", dms_str)
        if match:
            deg, minutes = match.groups()
            deg = float(deg)
            minutes = float(minutes)
            # minutes should be < 60
            if minutes >= 60:
                return None
            return deg + minutes/60
    except Exception:
        pass
    return None

def txt_to_gpx(txt_file, gpx_file):
    with open(txt_file, 'r') as f:
        lines = f.readlines()
    
    # Keep only lines that look like coordinates
    data_lines = [l.strip() for l in lines if '°' in l]
    
    # Create GPX root
    gpx = Element('gpx', version="1.1", creator="WindPlotConverter")
    trk = SubElement(gpx, 'trk')
    trkseg = SubElement(trk, 'trkseg')
    
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 3:
            try:
                lat = dms_to_dd(parts[0])
                lon = dms_to_dd(parts[1])
                time = parts[2]
                if lat is None or lon is None:
                    continue  # skip invalid coordinates
                # West is negative
                trkpt = SubElement(trkseg, 'trkpt', lat=str(lat), lon=str(-lon))
                SubElement(trkpt, 'time').text = f"2008-06-21T{time}Z"
            except Exception:
                # Skip any line that produces an error
                continue
    
    # Write GPX file
    xmlstr = minidom.parseString(tostring(gpx)).toprettyxml(indent="  ")
    with open(gpx_file, 'w') as f:
        f.write(xmlstr)

# --- Batch process all files in folder ---
input_folder = r"CHANGE TO THE INPUT FOLDER YOU HAVE YOUR EXPORTED PC WINDPLOT TXT FILES IN"  #CHANGE
output_folder = r"CHANGE TO THE OUTPUT FOLDER THAT YOU WANT YOUR GPX FILES STORED IN" #CHANGE

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith('.txt'):
        txt_path = os.path.join(input_folder, filename)
        gpx_name = os.path.splitext(filename)[0] + '.gpx'
        gpx_path = os.path.join(output_folder, gpx_name)
        try:
            txt_to_gpx(txt_path, gpx_path)
            print(f"Converted {filename} → {gpx_name}")
        except Exception as e:
            print(f"Skipped {filename} due to error: {e}")

print("All done!")
