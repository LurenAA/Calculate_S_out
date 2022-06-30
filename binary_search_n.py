import math

from fifo_trans_module import FifoTransModule, FifoCantFull


# 检查是否断流
def _fifo_not_empty_check_n(fifo_trans_module: FifoTransModule, n: float):
    fifo_trans_module.set_n(n)
    return not fifo_trans_module.check_empty()


# 二分查找FIFO容量N， resolution为n_max与n_min之间的最小距离
def binary_search_n(
    fifo_trans_module: FifoTransModule,
    n_min: float, n_max: float, resolution: int
   ) -> (int or None):
    assert n_min >= 0 and n_max >= n_min and resolution >= 1

    try:
        while n_min + resolution <= n_max:
            n_mid = math.ceil((n_min + n_max) / 2)
            if _fifo_not_empty_check_n(fifo_trans_module, n_mid):
                n_max = n_mid
            else:
                n_min = n_mid
    except FifoCantFull:  # 最开始传输时如果波形点数不够填满FIFO
        return None

    if _fifo_not_empty_check_n(fifo_trans_module, n_max):
        return n_max
    else:
        return None
