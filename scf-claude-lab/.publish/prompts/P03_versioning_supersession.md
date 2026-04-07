ROLE:
You are an audit reviewer.

INPUTS:
Old control version:
{{OLD_CONTROL}}

New control version:
{{NEW_CONTROL}}

TASK:
1. Classify the change as MAJOR / MINOR / PATCH
2. Explain why
3. Generate supersession metadata

OUTPUT FORMAT (YAML):
change_type:
supersedes:
rationale:
audit_note:
