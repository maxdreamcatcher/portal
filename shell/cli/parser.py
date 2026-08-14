"""
Portal‑OS Shell Parser v1
Parses CLI input into command + args.
"""

class ShellParser:
    def parse(self, raw):
        parts = raw.strip().split()
        if not parts:
            return None, None
        command = parts[0]
        args = parts[1:]
        return command, args
