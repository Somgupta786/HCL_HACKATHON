"""
Generate sample hospital data for the pipeline
"""
import csv
import json
import random
from datetime import datetime, timedelta

# Number of patients
NUM_PATIENTS = 300

# Generate EHR data
print("Generating ehr.csv...")
with open('ehr.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['patient_id', 'name', 'age', 'gender', 'admission_time'])
    
    first_names_male = ['James', 'John', 'Robert', 'Michael', 'William', 'David', 'Richard', 'Joseph', 'Thomas', 'Charles']
    first_names_female = ['Mary', 'Patricia', 'Jennifer', 'Linda', 'Elizabeth', 'Barbara', 'Susan', 'Jessica', 'Sarah', 'Karen']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
    
    for i in range(1, NUM_PATIENTS + 1):
        gender = random.choice(['M', 'F'])
        if gender == 'M':
            first_name = random.choice(first_names_male)
        else:
            first_name = random.choice(first_names_female)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        
        age = random.randint(18, 90)
        admission_time = datetime(2024, 1, random.randint(1, 31), 
                                 random.randint(0, 23), random.randint(0, 59), random.randint(0, 59))
        
        writer.writerow([i, name, age, gender, admission_time.strftime('%Y-%m-%d %H:%M:%S')])

print(f"✓ Created ehr.csv with {NUM_PATIENTS} patients")

# Generate vitals.jsonl
print("Generating vitals.jsonl...")
with open('vitals.jsonl', 'w') as f:
    for patient_id in range(1, NUM_PATIENTS + 1):
        base_time = datetime(2024, 1, 10, 12, 0, 0)
        
        for reading_num in range(5):
            timestamp = base_time + timedelta(hours=reading_num * 4)
            
            # Normal ranges with some variation
            hr = random.randint(60, 100)
            ox = random.randint(94, 100)
            sys = random.randint(110, 140)
            dia = random.randint(70, 90)
            
            # Add some anomalies (about 15%)
            if random.random() < 0.15:
                anomaly_type = random.choice(['hr', 'ox', 'bp'])
                if anomaly_type == 'hr':
                    hr = random.randint(121, 150)  # High HR
                elif anomaly_type == 'ox':
                    ox = random.randint(85, 91)  # Low oxygen
                else:
                    sys = random.randint(161, 180)  # High BP
                    dia = random.randint(101, 110)
            
            vitals_record = {
                'patientId': patient_id,
                'timestamp': int(timestamp.timestamp()),
                'hr': hr,
                'ox': ox,
                'sys': sys,
                'dia': dia
            }
            f.write(json.dumps(vitals_record) + '\n')

print(f"✓ Created vitals.jsonl with {NUM_PATIENTS * 5} vital readings")

# Generate labs.json
print("Generating labs.json...")
lab_tests = ['WBC', 'RBC', 'PLT', 'HGB', 'HCT', 'GLU', 'BUN', 'CRE', 'NA', 'K', 'CL', 'CO2']
lab_ranges = {
    'WBC': (4.5, 11.0),
    'RBC': (4.5, 5.9),
    'PLT': (150, 400),
    'HGB': (13.5, 17.5),
    'HCT': (38.8, 50.0),
    'GLU': (70, 100),
    'BUN': (7, 20),
    'CRE': (0.7, 1.3),
    'NA': (135, 145),
    'K': (3.5, 5.0),
    'CL': (96, 106),
    'CO2': (23, 29)
}

lab_records = []
for patient_id in range(1, NUM_PATIENTS + 1):
    base_time = datetime(2024, 1, 10, 12, 0, 0)
    
    for test_num in range(3):
        timestamp = base_time + timedelta(hours=test_num * 8)
        test = random.choice(lab_tests)
        min_val, max_val = lab_ranges[test]
        value = round(random.uniform(min_val, max_val), 2)
        
        lab_record = {
            'patient_id': patient_id,
            'test': test,
            'value': value,
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        lab_records.append(lab_record)

with open('labs.json', 'w') as f:
    json.dump(lab_records, f, indent=2)

print(f"✓ Created labs.json with {NUM_PATIENTS * 3} lab records")
print("\n✓ All sample data files generated successfully!")
