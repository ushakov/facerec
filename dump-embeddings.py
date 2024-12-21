# %%
import numpy as np
import models
# %%
vdb = models.open_lancedb()
# %%
total_count = vdb.count_rows()
faces = np.zeros((total_count, 512))

# %%
all_faces = vdb.search().limit(-1).to_list()

# %%
face_ids = []
for i, face in enumerate(all_faces):
    faces[i, :] = face["vector"]
    face_ids.append(face["face_id"])

# %%
np.savez_compressed('faces.npz', faces=faces, face_ids=face_ids)
# %%
