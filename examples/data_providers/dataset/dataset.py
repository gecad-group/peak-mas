from peak import Properties, Property


class dataset(Properties):
    def build_dataset(self):
        with open("texts.txt") as f:
            lines = f.read().splitlines()

        self.add_property("message", Property(lines, loop=True))
