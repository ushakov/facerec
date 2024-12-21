# %%
import tqdm
import numpy as np

# %%
class FaceClustering:
    CLUSTER_SIZE_THRESHOLD = 10

    def __init__(self, faces):
        self.faces = faces
        self.assignments = {}
        self.cluster_sizes = {}
        self.suspicious_face_pairs = set()

    def mergeable(self, i, j, distance):
        return self.cluster_sizes[i] <= self.CLUSTER_SIZE_THRESHOLD or self.cluster_sizes[j] <= self.CLUSTER_SIZE_THRESHOLD

    def merge_clusters(self, face_id_i, face_id_j, distance):
        """
        Merge clusters based on size thresholds.
        """
        cluster_i = self.assignments[face_id_i]
        cluster_j = self.assignments[face_id_j]
        if not self.mergeable(cluster_i, cluster_j, distance):
            self.suspicious_face_pairs.add((min(face_id_i, face_id_j), max(face_id_i, face_id_j)))
            return cluster_i
        winning_id = cluster_i if self.cluster_sizes[cluster_i] >= self.cluster_sizes[cluster_j] else cluster_j
        other_id = cluster_j if winning_id == cluster_i else cluster_i
        for k in self.assignments:
            if self.assignments[k] == other_id:
                self.assignments[k] = winning_id
        self.cluster_sizes[winning_id] += self.cluster_sizes[other_id]
        del self.cluster_sizes[other_id]
        return winning_id

    def cluster_faces(self):
        """
        Cluster face vectors based on cosine similarity.
        """
        self.faces /= np.linalg.norm(self.faces, axis=1)[:, None]
        sum_sub01 = 0
        sum_sub02 = 0
        sum_sub03 = 0
        sum_sub04 = 0
        total = 0
        for i in tqdm.trange(len(self.faces)):
            vec = self.faces[i]
            cosines = 1 - np.sum(self.faces * vec[None, :], axis=1)
            top_k = np.argsort(cosines)
            for j in top_k:
                if j == i:
                    continue
                if cosines[j] > 0.4:
                    break
                sum_sub04 += 1
                if cosines[j] < 0.1:
                    sum_sub01 += 1
                elif cosines[j] < 0.2:
                    sum_sub02 += 1
                elif cosines[j] < 0.3:
                    sum_sub03 += 1
            total += 1
        print(f"avg_sub01: {sum_sub01 / total}")
        print(f"avg_sub02: {sum_sub02 / total}")
        print(f"avg_sub03: {sum_sub03 / total}")
        print(f"avg_sub04: {sum_sub04 / total}")

if __name__ == "__main__":
    data = np.load('faces.npz')
    faces = data['faces']
    face_ids = data['face_ids']
    del data

    clustering = FaceClustering(faces)
    clustering.cluster_faces()

    # np.savez('clustering.npz',
    #          assignments=clustering.assignments,
    #          cluster_sizes=clustering.cluster_sizes,
    #          suspicious_face_pairs=list(clustering.suspicious_face_pairs))
