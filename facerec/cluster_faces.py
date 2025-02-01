from pathlib import Path
import numpy as np
import tqdm
import json
import networkx as nx

from facerec import models


def build_graph(ctx: models.Context) -> None:
    if (ctx.data_root / "face_similarity.gexf").exists():
        return nx.read_gexf(str(ctx.data_root / "face_similarity.gexf"))
    faces, face_ids = ctx.get_embeddings()
    gr = nx.Graph()
    for i in tqdm.trange(faces.shape[0], desc="Building graph"):
        cosines = np.dot(faces, faces[i])
        order = np.argsort(cosines)[::-1]
        for j in order:
            if cosines[j] < 0.4:
                break
            if i != j:
                gr.add_edge(face_ids[i], face_ids[j], weight=cosines[j])
    nx.write_gexf(gr, str(ctx.data_root / "face_similarity.gexf"))
    return gr


def compute_communities(ctx: models.Context, gr: nx.Graph) -> list[list[int]]:
    communities = nx.community.louvain_communities(gr)
    with open(ctx.data_root / "louvain_communities.json", "w") as f:
        json.dump([list(c) for c in communities], f)



def cluster_faces(data_root: Path) -> None:
    ctx = models.Context(data_root)
    gr = build_graph(ctx)
    communities = compute_communities(ctx, gr)
    ctx.save()



# %%
if __name__ == '__main__':
    cluster_faces(Path('d'))

