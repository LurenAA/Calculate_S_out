class FifoSeg:
    '''
        表示刷新周期中一段长度为t的时间，
        is_trans表示这段时间SDRAM是否在向FIFO发送波形
    '''
    def __init__(self, t: float, is_trans: bool):
        assert t > 0

        self.t = t
        self.is_ram_2_fifo_trans = is_trans

    def display(self, end = '\n'):
        print("t: %8.3fns, is_ram_2_fifo_trans: %d" % (
            self.t * 1e9, self.is_ram_2_fifo_trans),
            end= end
            )
