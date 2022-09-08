from peak.management.cli.parser import df, webapp


def main(args):
    if args[0].lower() == "df":
        df.parse(args[1:])

    if args[0].lower() == "webapp":
        webapp.parse(args[1:])
