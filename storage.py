import hashlib
import os

def hash_object(data, obj_type="blob", write=True, repo=None):
    # Header format: type_name size\0
    header = f"{obj_type} {len(data)}".encode()
    full_data = header + b"\0" + data
    sha = hashlib.sha1(full_data).hexdigest()

    if write:
        if not repo:
            raise Exception("Repo instance required to write object")
        
        obj_dir = os.path.join(repo.vcsdir, "objects", sha[:2])
        obj_path = os.path.join(obj_dir, sha[2:])
        
        if not os.path.exists(obj_dir):
            os.makedirs(obj_dir)
        
        if not os.path.exists(obj_path):
            with open(obj_path, "wb") as f:
                f.write(full_data)
                
    return sha

def read_object(sha, repo):
    obj_path = os.path.join(repo.vcsdir, "objects", sha[:2], sha[2:])
    if not os.path.exists(obj_path):
        raise Exception(f"Object {sha} not found")
        
    with open(obj_path, "rb") as f:
        full_data = f.read()
        
    # Split header and data
    null_idx = full_data.find(b"\0")
    header = full_data[:null_idx].decode()
    data = full_data[null_idx+1:]
    
    obj_type, size = header.split(" ")
    return obj_type, data
