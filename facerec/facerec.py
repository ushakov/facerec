from jsonargparse import CLI

class FaceRec:
    def __init__(self, model_path: str = "models/facerec.pkl"):
        self.model = model_path

    def serve(self):
        import os
        os.chdir('graphwalk/backend')
        os.system('uvicorn main:app --reload')


def run():
    CLI(FaceRec)


if __name__ == "__main__":
    run()