import sys
import argparse
from repository import Repository

def cmd_init(args):
    Repository.init()

def main():
    parser = argparse.ArgumentParser(description="Mini Version Control System")
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # init
    subparsers.add_parser("init", help="Initialize a new repository")

    # hash-object
    hash_parser = subparsers.add_parser("hash-object", help="Hash a file and optionally write it to storage")
    hash_parser.add_argument("file", help="File to hash")
    hash_parser.add_argument("-w", "--write", action="store_true", help="Write to storage")

    # cat-file
    cat_parser = subparsers.add_parser("cat-file", help="Provide content or type of repository objects")
    cat_parser.add_argument("object", help="Object SHA")

    # commit
    commit_parser = subparsers.add_parser("commit", help="Record changes to the repository")
    commit_parser.add_argument("-m", "--message", required=True, help="Commit message")

    # checkout
    checkout_parser = subparsers.add_parser("checkout", help="Restore workspace to a specific commit")
    checkout_parser.add_argument("object", help="Commit SHA to restore")

    # status
    subparsers.add_parser("status", help="Show the working tree status")

    # log
    log_parser = subparsers.add_parser("log", help="Show commit logs")
    log_parser.add_argument("object", nargs="?", help="Commit SHA to start from (default: HEAD)")

    args = parser.parse_args()

    repo = Repository()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "hash-object":
        cmd_hash_object(args, repo)
    elif args.command == "cat-file":
        cmd_cat_file(args, repo)
    elif args.command == "commit":
        cmd_commit(args, repo)
    elif args.command == "checkout":
        cmd_checkout(args, repo)
    elif args.command == "status":
        cmd_status(args, repo)
    elif args.command == "log":
        cmd_log(args, repo)
    else:
        parser.print_help()

def cmd_hash_object(args, repo):
    import os
    import storage
    with open(args.file, "rb") as f:
        data = f.read()
    sha = storage.hash_object(data, write=args.write, repo=repo)
    print(sha)

def cmd_cat_file(args, repo):
    import storage
    obj_type, data = storage.read_object(args.object, repo)
    sys.stdout.buffer.write(data)

def cmd_log(args, repo):
    from objects import Commit
    import storage
    
    sha = args.object or repo.get_head()
    
    while sha:
        obj_type, data = storage.read_object(sha, repo)
        if obj_type != "commit":
            raise Exception(f"Object {sha} is not a commit")
            
        commit = Commit(data)
        print(f"commit {sha}")
        print(f"Author: {commit.author}")
        print(f"\n    {commit.message}\n")
        
        sha = getattr(commit, "parent", None)

def cmd_commit(args, repo):
    from objects import Tree, Commit
    import storage
    
    tree_sha = Tree.write_tree(repo)
    parent_sha = repo.get_head()
    
    commit = Commit()
    commit.tree = tree_sha
    if parent_sha:
        commit.parent = parent_sha
    commit.author = "User <user@example.com>"
    commit.committer = "User <user@example.com>"
    commit.message = args.message
    
    commit_sha = storage.hash_object(commit.serialize(), "commit", write=True, repo=repo)
    repo.set_head(commit_sha)
    print(f"[{commit_sha}] {args.message}")

def cmd_checkout(args, repo):
    import storage
    from objects import Commit, Tree
    import os
    
    sha = args.object
    obj_type, data = storage.read_object(sha, repo)
    if obj_type != "commit":
        raise Exception(f"Object {sha} is not a commit")
        
    commit = Commit(data)
    
    # Clear working directory (simplified for demo)
    for root, dirs, files in os.walk("."):
        if ".vcs" in dirs: dirs.remove(".vcs")
        if ".git" in dirs: dirs.remove(".git")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        for f in files:
            if f not in ["vcs.py", "storage.py", "objects.py", "repository.py"]:
                os.remove(os.path.join(root, f))
        for d in dirs:
            os.rmdir(os.path.join(root, d)) # This will fail if dirs are not empty
            
    # Write tree to working directory
    Tree.read_tree(repo, commit.tree)
    
    repo.set_head(sha)
    print("Done.")

def get_tree_hashes(repo, sha, prefix=""):
    from objects import Tree
    import storage
    import os
    
    hashes = {}
    obj_type, data = storage.read_object(sha, repo)
    tree = Tree(data)
    
    for mode, type, item_sha, name in tree.items:
        full_name = os.path.join(prefix, name)
        if type == "tree":
            hashes.update(get_tree_hashes(repo, item_sha, full_name))
        else:
            hashes[full_name] = item_sha
    return hashes

def cmd_status(args, repo):
    from objects import Commit
    import storage
    import os
    
    head_sha = repo.get_head()
    if not head_sha:
        print("No commits yet.")
        return
        
    obj_type, data = storage.read_object(head_sha, repo)
    commit = Commit(data)
    
    # Get all files in currently committed tree
    head_files = get_tree_hashes(repo, commit.tree)
    
    # Get all files on disk (excluding .vcs, .git, etc.)
    disk_files = {}
    for root, dirs, files in os.walk("."):
        if ".vcs" in dirs: dirs.remove(".vcs")
        if ".git" in dirs: dirs.remove(".git")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), ".")
            if rel_path.startswith("./"): rel_path = rel_path[2:]
            
            with open(rel_path, "rb") as f:
                data = f.read()
            sha = storage.hash_object(data, "blob", write=False)
            disk_files[rel_path] = sha

    modified = []
    untracked = []
    deleted = []
    
    for path, sha in head_files.items():
        if path not in disk_files:
            deleted.append(path)
        elif disk_files[path] != sha:
            modified.append(path)
            
    for path in disk_files:
        if path not in head_files:
            untracked.append(path)
            
    if not modified and not untracked and not deleted:
        print("Working directory clean.")
        return
        
    if modified:
        print("\nModified files:")
        for f in modified: print(f"  modified: {f}")
        
    if deleted:
        print("\nDeleted files:")
        for f in deleted: print(f"  deleted:  {f}")
        
    if untracked:
        print("\nUntracked files:")
        for f in untracked: print(f"  untracked: {f}")
    print()

if __name__ == "__main__":
    main()
