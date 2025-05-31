import numpy as np
from tereancore.ObspyMimics import CustomStream

# sgy_path = "C:\\Users\\dkb73\\IdeaProjects\\spark-collab\\docs\\Geometry\\samples\\sgy\\0078.sgy"
sgy_path = "C:\\Users\\dkb73\\Downloads\\MindenSampleData\\SGY\\0361.sgy"
sgy_data = CustomStream.from_sgy(sgy_path)
sgy_headers_df = sgy_data.headers
print(sgy_headers_df.columns)
for trace_idx, trace in enumerate(sgy_data.traces):
    print(f"'index': {trace_idx}, 'x': {trace.geometry.x}, 'y': {trace.geometry.y}, 'z': {trace.geometry.z}")
print(f"Average spacing: {sgy_data.geophone_spacing}")