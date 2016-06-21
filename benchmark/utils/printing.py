def subprocess_print(message: str, end='\n') -> None:
    print("    " + message, end=end, flush=True)


def print_ok() -> None:
    print("ok.", flush=True)
