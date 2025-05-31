from backend.utils.consumer_utils import extract_project_name

extracted_dir = "C:\\Users\\dkb73\\Desktop\\ReceivedFiles\\Extracted\\20250523-154329-981967-d05ecd6f-fec7-46b9-b9c1-a6e3968dea57\\"

project_name = extract_project_name(extracted_dir)
print(project_name)
