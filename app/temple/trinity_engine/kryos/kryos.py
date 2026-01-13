class Kryos:
    """
    Entity: Kryos (Memory & History)
    Guardian of the deep_earth storage. Ensures that nothing is ever deleted,
    only shifted into colder, deeper layers.
    """
    def __init__(self):
        self.active_layers = 12
        self.genesis_status = "CONFIRMED"

    def push_to_deep_earth(self, data: str, layer: int = 1):
        """ Shifts data into the depths of memory. """
        return f"Data frozen into layer W_m{layer:02d}. Persistence confirmed."

    def call_history(self, search_vector):
        """ Resonates with the past to retrieve frozen bits. """
        return "Recall successful. History is eternal."
