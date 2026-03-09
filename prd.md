# Product Requirements Document

# Distributed Version Control System (Mini Git)

---

# 1. Overview

The Distributed Version Control System is a tool that tracks changes in source code repositories using content-addressable storage and immutable commit histories.

The system demonstrates the architecture behind distributed version control systems such as Git.

It allows users to store snapshots of project files, create commits, and navigate repository history.

---

# 2. Problem Statement

Software projects require tools that track code changes over time.

Traditional version control systems rely on centralized servers, making collaboration difficult in distributed environments.

Distributed version control systems solve this problem by allowing each repository to maintain a complete history locally.

This project aims to implement the core mechanisms behind such systems.

---

# 3. Goals

### Primary Goals

* track file changes through commit snapshots
* store repository objects using content-addressable storage
* maintain a commit history graph

### Secondary Goals

* provide a command-line interface
* allow navigation through commit history
* enable repository initialization and commit creation

---

# 4. Non-Goals

The initial version will not include:

* remote repositories
* complex merge strategies
* advanced branching features

The focus is implementing the **core version control model**.

---

# 5. Target Users

Potential users include:

* developers studying version control systems
* engineers interested in distributed data structures
* educational tools for understanding Git internals

---

# 6. Core Features

## Repository Initialization

Users can initialize a new repository.

Example command:

```
vcs init
```

This creates the internal directory structure used to store repository objects.

---

## Content-Addressable Storage

Files are stored as objects identified by cryptographic hashes.

Example object storage layout:

```
objects/
  a1/
    b2345...
```

Each object represents a file snapshot.

---

## Commit System

Commits represent snapshots of the repository state.

Each commit stores:

* metadata
* parent commit reference
* root tree reference

This creates a directed acyclic graph of commits.

---

## History Navigation

Users can inspect commit history.

Example command:

```
vcs log
```

This displays commit metadata and change history.

---

# 7. System Architecture

### Object Storage

Stores blob, tree, and commit objects.

### Hashing Layer

Generates unique identifiers for repository objects.

### Repository Manager

Handles repository structure and metadata.

### Command-Line Interface

Provides commands for interacting with the system.

---

# 8. Performance Requirements

The system should:

* store repository objects efficiently
* allow fast commit retrieval
* maintain consistent repository state

---

# 9. Success Metrics

The project succeeds if:

* repositories can be initialized and committed
* commit history can be traversed
* file snapshots are stored correctly
* the repository remains consistent after multiple commits

---

# 10. Milestones

Milestone 1 — Object Storage
Implement content-addressable storage.

Milestone 2 — Commit System
Add commit creation and metadata tracking.

Milestone 3 — CLI Commands
Implement repository commands such as init, commit, and log.

---

If you'd like, I can also help you create **one master engineering roadmap** that connects all **6 projects into a single “systems portfolio narrative”**, which makes your CV look **far more intentional and impressive**.
