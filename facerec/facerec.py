from jsonargparse import CLI

class FaceRec:
    def __init__(self, model_path: str = "models/facerec.pkl"):
        self.model = model_path

    def serve(self):
        import uvicorn
        uvicorn.run('facerec.graphwalk.backend.main:app', port=8000)


def run():
    CLI(FaceRec)


if __name__ == "__main__":
    run()