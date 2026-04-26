# Compatibility Policy

This project follows a best-effort compatibility approach.

## Policy Summary

- Backward compatibility is desirable but not a hard requirement.
- Breaking changes are allowed when they clearly improve architecture, language coverage, correctness, or execution UX.
- New APIs should prefer clear and consistent behavior over preserving historical quirks.

## When Breaking Changes Are Acceptable

A breaking change is acceptable when at least one of these applies:

- It removes architectural blockers for MiniZinc feature coverage.
- It significantly reduces complexity or duplicate logic.
- It eliminates hidden state or unsafe behavior.
- It improves correctness in ways that cannot be delivered compatibly.

## Deprecation Strategy

- Deprecated wrappers are added only when migration cost is high for users.
- If migration cost is low, the project may skip wrappers and document direct migration instead.
- Deprecations should be short-lived.
- The deprecation surface should stay small and be removed quickly after a transition window.

## Documentation Requirements For Breaking Changes

For each breaking change:

- Add an entry to migration notes with old behavior and new behavior.
- Include a minimal before/after code snippet when possible.
- Mention if a temporary wrapper exists and when it is expected to be removed.
