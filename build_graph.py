# %%
import tqdm
import numpy as np
import networkx as nx

# %%
class FaceGraph:
    DIST_THRESHOLD = 0.4

    def __init__(self, faces, face_ids):
        self.faces = faces
        self.face_ids = face_ids

    def build_graph(self):
        """
        Build a graph based on cosine similarity.
        """
        self.faces /= np.linalg.norm(self.faces, axis=1)[:, None]
        graph = nx.Graph()
        for i in tqdm.trange(len(self.faces)):
            vec = self.faces[i]
            cosines = 1 - np.sum(self.faces * vec[None, :], axis=1)
            top_k = np.argsort(cosines)
            for j in top_k:
                if j == i:
                    continue
                if cosines[j] > self.DIST_THRESHOLD:
                    break
                graph.add_edge(self.face_ids[i], self.face_ids[j], distance=cosines[j])
        return graph


if __name__ == "__main__":
    data = np.load('faces.npz')
    faces = data['faces']
    face_ids = data['face_ids']
    del data

    graph = FaceGraph(faces, face_ids)
    graph = graph.build_graph()

    print(f"graph has {len(graph.nodes)} nodes and {len(graph.edges)} edges")

    # Save graph to file
    nx.write_gexf(graph, "face_similarity.gexf")

