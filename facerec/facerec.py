from jsonargparse import CLI
from pathlib import Path

class FaceRec:
    def __init__(self, data_dir: Path = Path('.')):
        self.data_dir = data_dir

    def discover(self, src_dir: Path):
        from facerec.discover_dir import find_files
        find_files(src_dir, self.data_dir)


    def detect(self, force: bool = False):
        from facerec.detect_faces import process_new_images
        process_new_images(self.data_dir, force)

    def cluster(self):
        from facerec.cluster_faces import cluster_faces
        cluster_faces(self.data_dir)

    def serve(self):
        import uvicorn
        import facerec.graphwalk.backend.main as main
        main.settings.subgraph_dir = self.data_dir
        uvicorn.run(main.app, port=8000)


def run():
    CLI(FaceRec)


if __name__ == "__main__":
    run()