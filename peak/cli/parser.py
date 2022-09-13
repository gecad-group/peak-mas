from peak.cli import df, mas


def parse(args: list[str]):
    if len(args) == 0 or args[0].lower() == "-h":
        print("Help message - in development")
    elif args[0].lower() == "df":
        df.exec(args[1:])
    elif args[0].lower() == "run":
        mas.exec(args[1:])
    else:
        print("Help message - in development")
