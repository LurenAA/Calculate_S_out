import sys


class FifoRefCycle:
    '''
    表示一个刷新周期，fifo_seg_list中存储FifoSeg对象。
    FifoSeg表示刷新周期中一段长度为t的时间（可能在传输或者断流）
    '''
    def __init__(self) -> None:
        self.__fifo_seg_list = list()  # 存储FifoSeg传输信息对象

    def append_fifo_seg(self, fifo_seg):  # FifoSeg的序列添加元素
        self.__fifo_seg_list.append(fifo_seg)

    def display(self, file=sys.stdout):  # 打印调试信息
        print("FifoRefCycle:", file=file)
        for x in self.__fifo_seg_list:
            print("\t", end="", file=file)
            x.display(file=file)

    def __iter__(self):
        return iter(self.__fifo_seg_list)

    def get_fifo_seg_list(self):  # 获取FifoSeg传输信息对象的序列
        return self.__fifo_seg_list
