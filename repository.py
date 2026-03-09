import os

class Repository:
    def __init__(self, path="."):
        self.worktree = path
        self.vcsdir = os.path.join(path, ".vcs")

    @classmethod
    def init(cls, path="."):
        repo = cls(path)
        if os.path.exists(repo.vcsdir):
            print(f"Reinitialized existing VCS repository in {os.path.abspath(repo.vcsdir)}")
            return repo

        os.makedirs(repo.vcsdir)
        os.makedirs(os.path.join(repo.vcsdir, "objects"))
        os.makedirs(os.path.join(repo.vcsdir, "refs", "heads"), exist_ok=True)
        
        with open(os.path.join(repo.vcsdir, "HEAD"), "w") as f:
            f.write("ref: refs/heads/main\n")

        print(f"Initialized empty VCS repository in {os.path.abspath(repo.vcsdir)}")
        return repo

    def resolve_ref(self, ref):
        ref_path = os.path.join(self.vcsdir, ref)
        if not os.path.exists(ref_path):
            return None
        with open(ref_path, "r") as f:
            data = f.read().strip()
        if data.startswith("ref: "):
            return self.resolve_ref(data[5:])
        return data

    def get_head(self):
        return self.resolve_ref("HEAD")

    def set_head(self, sha):
        # Update the branch HEAD points to, or HEAD itself if detached
        with open(os.path.join(self.vcsdir, "HEAD"), "r") as f:
            data = f.read().strip()
        
        if data.startswith("ref: "):
            ref = data[5:]
            ref_path = os.path.join(self.vcsdir, ref)
            os.makedirs(os.path.dirname(ref_path), exist_ok=True)
            with open(ref_path, "w") as f:
                f.write(sha + "\n")
        else:
            with open(os.path.join(self.vcsdir, "HEAD"), "w") as f:
                f.write(sha + "\n")

    def find_repo(self, path=".", required=True):
        path = os.path.abspath(path)
        if os.path.isdir(os.path.join(path, ".vcs")):
            return Repository(path)
        
        parent = os.path.abspath(os.path.join(path, os.pardir))
        if parent == path: # Root
             if required:
                 raise Exception("Not a vcs repository")
             return None
        
        return self.find_repo(parent, required)
