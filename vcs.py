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

if __name__ == "__main__":
    main()
