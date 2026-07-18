# State Machines

Job, proposal, and application states are defined in `src/job_agent/core/states.py`. Invalid transitions raise errors and all user-facing transitions should be recorded as append-only events.
