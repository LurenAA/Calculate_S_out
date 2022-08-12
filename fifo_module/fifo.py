class FifoEmpty(Exception):
    pass


class Fifo:
    def __init__(self, N_64Byte_FIFO_MAX) -> None:
        self.__N_64Byte_FIFO_MAX = N_64Byte_FIFO_MAX
        self.__n_64byte_fifo_current = N_64Byte_FIFO_MAX

    def send_out(self):
        self.__n_64byte_fifo_current -= 1

        if self.__n_64byte_fifo_current < 0:
            raise FifoEmpty

    def receive_in(self):
        assert(self.__n_64byte_fifo_current <= self.__N_64Byte_FIFO_MAX)

        self.__n_64byte_fifo_current += 1

    def is_full(self):
        return self.__n_64byte_fifo_current == self.__N_64Byte_FIFO_MAX

    def get_n_64byte_fifo_current(self):
        return self.__n_64byte_fifo_current
