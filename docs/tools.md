# Tools

Tools publish a name, description, Pydantic input schema, safety level, and structured
result. The MVP includes five filesystem tools, one restricted terminal tool, six
Git tools, and one allowlisted desktop launcher.

Filesystem paths normally refer to the writable workspace. Prefix a path with
`@project/` for read-only project inspection. There is intentionally no delete tool.
Terminal execution never starts a shell. Git tools intentionally omit push, reset,
clean, and remote mutation.

`desktop.open` can visibly open This PC/My Computer, the home, Desktop, Documents,
or Downloads folder, Calculator, Notepad/TextEdit, or system Settings. Every desktop
action requires confirmation. It cannot accept arbitrary executable names, command
arguments, keystrokes, mouse input, or background automation.
