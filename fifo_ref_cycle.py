class FifoRefCycle:
    '''
    表示一个刷新周期，fifo_seg_list中存储FifoSeg对象。
    FifoSeg表示刷新周期中一段长度为t的时间（可能在传输或者断流）
    '''
    def __init__(self) -> None:
        self.__fifo_seg_list = list()

    def append_fifo_seg(self, fifo_seg):
        self.__fifo_seg_list.append(fifo_seg)

    def display(self):
        print("FifoRefCycle:")
        for x in self.__fifo_seg_list:
            print("\t", end="")
            x.display()

    def __iter__(self):
        return iter(self.__fifo_seg_list)

    def get_fifo_seg_list(self):
        return self.__fifo_seg_list
