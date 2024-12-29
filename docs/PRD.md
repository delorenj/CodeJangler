# Code Jangler

An agentic service that optimizes github pull requests by automatically breaking them into multiple, more-manageable commits.

## The CLI

This is the core interface and will be developed first.

### Stack

1. Python + Click for CLI
2. Celery for async jobs
3. Flower to monitor jobs
4. Redis for local persistance
5. CrewAI as agentic framework
6. Docker compose to manage stack
7. mise for versioning, tooling, and tasks
8. uv for venv and pip installs

### CLI Requirements

1. Given the url of a PR, it will clone the repository or checkout the branch (if ran within the an existing repo clone)

2. If run within a cloned repo with an up-to-date branch, it will find the matching PR or continue as though the PR has not yet been created.

3. When run, the service will kick off a CrewAI crew containing 3 agents that will work together to accomplish the given task

4. By default the task will run synchronously, outputting the entirety of the agent communication activity

5. Optionally, the task can be run asynchronously with the jobs managed by celery, monitored by flower, and storage handled by a local containerized redis store

6. When complete, a full analysis report will be generated outlining the viable split strategies it has determined before asking how to proceed.

7. Optionally, the client can provide feedback before doing another iteration taking into account the client's feedback.

8. Once a split strategy is decided upon, the crew proceeds to create the new stack of PRs using the various git tools necessary. For instance, it can cherry-pick commits if viable, but if necessary, it can rebuild new commits if a particular hash needs to be split.

9. All operations on the repo shall be non-destructive, allowing the client to always reset to start over.

10. If a crew agent determines there isn't enough test coverage in place to ensure a robust splitting experience that maintains functionality and parity pre and post split, it will suggest where the client needs to add tests.

11. After the commits are created, the crew proceeds to create the PR stack on github, including a description of each PR and how to merge them properly in the correct order

12. The CLI will provide a command that will maintain the PR stack's integrity by rebasing against any upstream commits that occur before the PRs are reviewed an merged.
