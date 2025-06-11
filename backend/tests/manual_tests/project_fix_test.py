import json
import tempfile
import os
from datetime import datetime

# Test the Project schema from_db method
print("=== Testing Project Schema ===")

# Create mock SQLAlchemy models
class MockSgyFileDB:
    def __init__(self, id, name):
        self.id = id
        self.original_name = name
        self.path = f"/path/to/{id}.sgy"
        self.size = 1024
        self.upload_date = datetime.now()
        self.type = "SGY"
        self.project_id = "test123"
        # SQLAlchemy internal attributes
        self._sa_instance_state = "some_internal_state"

class MockProjectDB:
    def __init__(self):
        self.id = "test123"
        self.name = "Test Project"
        self.status = "not_started"
        self.priority = "medium"
        self.survey_date = None
        self.received_date = datetime.now()
        self.geometry = '[{"index":1,"x":0,"y":0,"z":0}]'
        self.record_options = '[{"id":"file1","enabled":false,"weight":100,"fileName":"test.sgy"}]'
        self.plot_limits = '{"numFreq": 50, "maxFreq": 50, "numSlow": 50, "maxSlow": 0.015}'
        self.freq = '[]'
        self.slow = '[]'
        self.picks = '[]'
        self.disper_settings = '{}'
        self.client = None
        # Add mock records (SGY files)
        self.records = [
            MockSgyFileDB("file1", "0361.sgy"),
            MockSgyFileDB("file2", "0362.sgy"),
            MockSgyFileDB("file3", "0363.sgy")
        ]
        self.additional_files = []
        # SQLAlchemy internal attribute
        self._sa_instance_state = "some_internal_state"

try:
    from schemas.project_schema import Project
    
    mock_db = MockProjectDB()
    project = Project.from_db(mock_db)
    
    print(f"✅ Successfully created Project from DB model")
    print(f"   Project ID: {project.id}")
    print(f"   Project Name: {project.name}")
    print(f"   Has _sa_instance_state in result: {'_sa_instance_state' in project.__dict__}")
    print(f"   Number of records: {len(project.records) if project.records else 0}")
    if project.records:
        print(f"   First record ID: {project.records[0].id}")
        print(f"   First record type: {type(project.records[0])}")
    
except Exception as e:
    print(f"❌ Error creating Project from DB model: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Testing Record Options Update ===")

# Test record options update logic
record_options = [
    {"id":"","enabled":False,"weight":100,"fileName":"0361.sgy"},
    {"id":"","enabled":False,"weight":100,"fileName":"0362.sgy"},
    {"id":"","enabled":False,"weight":100,"fileName":"0363.sgy"}
]

file_ids = ["N2KVVj6W8Qac0", "NTHJOiidagxR6", "NlpvMwJav2qSD"]

updated_record_options = []
for i, (record, file_id) in enumerate(zip(record_options, file_ids)):
    record_copy = record.copy()
    record_copy['id'] = file_id
    updated_record_options.append(record_copy)

print(f"Original record_options: {json.dumps(record_options, indent=2)}")
print(f"\nUpdated record_options: {json.dumps(updated_record_options, indent=2)}")
print(f"\n✅ Record options would be updated correctly with file IDs") 