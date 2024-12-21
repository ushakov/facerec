# %%
import networkx as nx
import json
# %%
graph = nx.read_gexf("face_similarity.gexf")

# # %%
# betweeness = nx.edge_betweenness_centrality(graph)
# # %%
# with open("betweeness.json", "w") as f:
#     json.dump(list(betweeness.items()), f)
# # %%
# sorted_edges = sorted(betweeness.items(), key=lambda x: x[1], reverse=True)
# # %%
# len(sorted_edges)
# # %%
# sorted_edges[:10]
# # %%
# nx.approximation.diameter(graph)
# # %%
# components = list(nx.connected_components(graph))
# # %%
# len(components)
# # %%
# components = sorted(components, key=len, reverse=True)
# # %%
# [len(c) for c in components[:10]]
# # %%
# components[1500]
# # %%
# components[1]
# # %%
# with open("components.json", "w") as f:
#     json.dump([list(c) for c in components], f)
# %%
communities = nx.community.louvain_communities(graph)
# %%
with open("louvain_communities.json", "w") as f:
    json.dump([list(c) for c in communities], f)
# %%
len(communities)
# %%
len(communities[2475])
# %%
