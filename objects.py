import os
import storage

class VCSObject:
    def __init__(self, data=None):
        if data:
            self.deserialize(data)
            
    def serialize(self):
        raise NotImplementedError
        
    def deserialize(self, data):
        raise NotImplementedError

class Blob(VCSObject):
    def __init__(self, data=None):
        super().__init__(data)
        self.obj_type = "blob"
        
    def serialize(self):
        return self.blob_data
        
    def deserialize(self, data):
        self.blob_data = data

class Tree(VCSObject):
    def __init__(self, data=None):
        self.obj_type = "tree"
        self.items = [] # List of (mode, name, sha)
        super().__init__(data)
        
    def serialize(self):
        # Format: mode name\0sha (binary sha)
        # Note: git uses binary SHA, we'll use hex for simplicity but git format is better
        # Let's use a simpler text format for now to keep it easy to debug:
        # mode type sha name\n
        res = b""
        for mode, obj_type, sha, name in self.items:
            res += f"{mode} {obj_type} {sha} {name}\n".encode()
        return res
        
    def deserialize(self, data):
        self.items = []
        if not data:
            return
        lines = data.decode().split("\n")
        for line in lines:
            if not line: continue
            parts = line.split(" ", 3)
            self.items.append(tuple(parts))

    @classmethod
    def write_tree(cls, repo, path="."):
        tree = cls()
        entries = sorted(os.listdir(path))
        for name in entries:
            if name == ".vcs" or name == ".git" or name == "__pycache__":
                continue
            
            full_path = os.path.join(path, name)
            if os.path.isdir(full_path):
                sha = Tree.write_tree(repo, full_path)
                tree.items.append(("040000", "tree", sha, name))
            else:
                with open(full_path, "rb") as f:
                    data = f.read()
                sha = storage.hash_object(data, "blob", write=True, repo=repo)
                # mode 100644 for regular files
                tree.items.append(("100644", "blob", sha, name))
        
        sha = storage.hash_object(tree.serialize(), "tree", write=True, repo=repo)
        return sha

    @classmethod
    def read_tree(cls, repo, sha, path="."):
        obj_type, data = storage.read_object(sha, repo)
        if obj_type != "tree":
            raise Exception(f"Object {sha} is not a tree")
            
        tree = cls(data)
        if not os.path.exists(path):
            os.makedirs(path)
            
        for mode, item_type, item_sha, name in tree.items:
            full_path = os.path.join(path, name)
            if item_type == "tree":
                cls.read_tree(repo, item_sha, full_path)
            elif item_type == "blob":
                b_type, b_data = storage.read_object(item_sha, repo)
                with open(full_path, "wb") as f:
                    f.write(b_data)
                    
                # Restore executable bit if mode says so (simplified)
                if mode == "100755":
                    os.chmod(full_path, 0o755)

class Commit(VCSObject):
    def __init__(self, data=None):
        self.obj_type = "commit"
        super().__init__(data)
        
    def serialize(self):
        # Format:
        # tree <sha>
        # parent <sha> (optional)
        # author <name> <email> <timestamp>
        # committer <name> <email> <timestamp>
        #
        # message
        res = f"tree {self.tree}\n"
        if hasattr(self, "parent") and self.parent:
            res += f"parent {self.parent}\n"
        res += f"author {self.author}\n"
        res += f"committer {self.committer}\n"
        res += "\n"
        res += self.message
        return res.encode()
        
    def deserialize(self, data):
        lines = data.decode().split("\n")
        # Very simple parser
        idx = 0
        while lines[idx]:
            line = lines[idx]
            parts = line.split(" ", 1)
            if parts[0] == "tree":
                self.tree = parts[1]
            elif parts[0] == "parent":
                self.parent = parts[1]
            elif parts[0] == "author":
                self.author = parts[1]
            elif parts[0] == "committer":
                self.committer = parts[1]
            idx += 1
        self.message = "\n".join(lines[idx+1:])
