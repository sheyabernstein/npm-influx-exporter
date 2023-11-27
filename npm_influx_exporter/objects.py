from collections import deque


class LimitedSizeSet:
    """
    FIFO set with limited size.
    """

    max_size: int

    def __init__(self, max_size: int = 256):
        self.max_size = max_size
        self.queue = deque(maxlen=max_size)
        self.set = set()

    def add(self, element):
        if element not in self.set:
            if len(self.queue) == self.max_size:
                removed_element = self.queue.popleft()
                self.set.remove(removed_element)
            self.queue.append(element)
            self.set.add(element)
        else:
            self.queue.remove(element)
            self.queue.append(element)

    def update(self, elements):
        for element in elements:
            self.add(element=element)

    def clear(self):
        return self.set.clear()

    def __contains__(self, element):
        return element in self.set

    def __len__(self):
        return len(self.set)

    def __iter__(self):
        return self.set.__iter__()
