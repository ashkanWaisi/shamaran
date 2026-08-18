# Tools

Tools publish a name, description, Pydantic input schema, safety level, and structured
result. The MVP includes five filesystem tools, one restricted terminal tool, and six
Git tools.

Filesystem paths normally refer to the writable workspace. Prefix a path with
`@project/` for read-only project inspection. There is intentionally no delete tool.
Terminal execution never starts a shell. Git tools intentionally omit push, reset,
clean, and remote mutation.
