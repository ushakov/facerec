# %%
import networkx as nx
import json
from pydantic_settings import BaseSettings, SettingsConfigDict


# %%
class Settings(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)

    distance_threshold: float = 0.3


settings = Settings()


# %%
graph = nx.read_gexf("face_similarity.gexf")

# %%
subgraph = nx.Graph()
subgraph.add_nodes_from(graph.nodes(data=True))
subgraph.add_edges_from((u, v, d) for u, v, d in graph.edges(data=True)
                       if d['distance'] < settings.distance_threshold)


# %%
components = list(nx.connected_components(subgraph))
# %%
len(components)
# %%
nontrivial_components = [c for c in components if len(c) > 1]

# %%
len(nontrivial_components)
# %%
sum(len(c) for c in nontrivial_components)
# %%
len(subgraph.nodes)
# %%
len(graph.nodes)
# %%
nontrivial_components[0]
# %%
with open(f'nontrivial_components_{settings.distance_threshold}.json', 'w') as f:
    json.dump([list(c) for c in nontrivial_components], f)
# %%
compgraph = nx.Graph()
revcomp = {node: compid for compid, nodes in enumerate(nontrivial_components) for node in nodes}
# %%
for u, v, d in graph.edges(data=True):
    left_comp = revcomp.get(u, None)
    right_comp = revcomp.get(v, None)
    if left_comp is not None and right_comp is not None and left_comp != right_comp:
        if compgraph.has_edge(left_comp, right_comp):
            compgraph[left_comp][right_comp]['distance'] = min(compgraph[left_comp][right_comp]['distance'], d['distance'])
        else:
            compgraph.add_edge(left_comp, right_comp, distance=d['distance'])

# %%
all_edges = list((u, v, d['distance']) for u, v, d in compgraph.edges(data=True))
# %%
sorted(all_edges, key=lambda x: x[2])[:10]

# %%
len(all_edges)
# %%
nx.write_gexf(compgraph, f"face_similarity_components_{settings.distance_threshold}.gexf")
# %%
