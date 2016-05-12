def subprocess_print(message: str, end='\n') -> None:
    print("\t" + message, end=end, flush=True)


def subprocess_print_append(message: str, end='\n') -> None:
    print(message, end=end)


def print_ok() -> None:
    print("ok.", flush=True)
