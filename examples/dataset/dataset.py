from peak.mas import Properties, Property


class dataset(Properties):
    def build_dataset(self):
        with open("texts.txt") as f:
            lines = f.readlines()

        self.add_property(self.agent_name, "message", Property(lines, loop=True))
