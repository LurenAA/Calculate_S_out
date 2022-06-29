import math

from fifo_ref_cycle import FifoRefCycle
from seg_info import build_seg_info_list
from fifo_seg import FifoSeg


class FifoTransModule:
    def __init__(self, waveform_pts: list,
                 t_1st_start: float,
                 T_REFI, T_RTI, T_SW, S_IN, S_OUT, N
                 ) -> None:
        # 获取序列传输信息的列表
        self.__seg_info_list = build_seg_info_list(
            waveform_pts, t_1st_start, T_REFI, T_RTI, T_SW, S_IN, N
        )

        self.__fifo_cycle_list = FifoTransModule.bulid_fifo_ref_cycle_list(
            self.__seg_info_list, t_1st_start, T_REFI, T_RTI, T_SW, S_IN, N
        )
        self.__t_1st_start = t_1st_start
        self.__T_REFI = T_REFI
        self.__T_RTI = T_RTI
        self.__T_SW = T_SW
        self.__S_IN = S_IN
        self.__S_OUT = S_OUT
        self.__N = N

    def display_fifo_cycle_list(self):
        for x in self.__fifo_cycle_list:
            x.display()
    
    def display_seg_info_list(self):
        for x in self.__seg_info_list:
            x.display()

    def check_empty(self, show_debug_info: bool = False) -> bool:
        '''
        测试FIFO在传输过程中是否会空
        '''
        current_fifo_n = self.__N
        for idx, cycle in enumerate(self.__fifo_cycle_list):
            if show_debug_info:
                print("cycle %2d" % (idx + 1))
            for seg in cycle:
                delta_n = math.ceil(
                    seg.t * (
                        (
                            (self.__S_IN - self.__S_OUT)
                            if seg.is_ram_2_fifo_trans else (-self.__S_OUT)
                        )
                    )
                )
                if show_debug_info:
                    print("\t", end="")
                    seg.display("\t")

                fifo_n_before = current_fifo_n
                current_fifo_n += delta_n
                if current_fifo_n >= self.__N:
                    current_fifo_n = self.__N

                if show_debug_info:
                    print(
                        ("fifo_n_before: %5d\t"
                         "delta_n: %5d\tfifo_n_after: %5d") % (
                            fifo_n_before, delta_n, current_fifo_n)
                    )

                if current_fifo_n < 0:
                    return True

        return False

    @staticmethod
    def bulid_fifo_ref_cycle_list(
        seg_info_list: list,
        t_1st_start: float,
        T_REFI: float,
        T_RTI: float, T_SW: float,
        S_IN: float, N: int
    ) -> list:
        '''
        通过波形点序列构建FifoRefCycle对象 t_1st_start指FIFO满后FIFO第一次开始输出的时间
        '''
        fifo_ref_cycle_list = list()
        current_ref_cycle = FifoRefCycle()
        if t_1st_start < T_RTI:  # 当FIFO开始输出时，SDRAM第一个序列还没有开始向FIFO输出
            current_ref_cycle.append_fifo_seg(
                FifoSeg(T_RTI - t_1st_start, False)
            )

        for i in range(0, len(seg_info_list)):
            # 新的序列开始和上一个序列在同一个刷新周期时，添加之间的断流时间
            if not seg_info_list[i].is_in_next_cycle:
                if i:
                    sw_interval = (
                        seg_info_list[i].t_start -
                        seg_info_list[i - 1].t_end
                    )
                    current_ref_cycle.append_fifo_seg(
                        FifoSeg(sw_interval, False)
                    )
            else:  # 新的序列开始和上一个序列不在同一个刷新周期时
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(T_REFI - seg_info_list[i - 1].t_end, False)
                )
                fifo_ref_cycle_list.append(current_ref_cycle)
                current_ref_cycle = FifoRefCycle()
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(T_RTI, False)
                )

            # 传输在当前周期就结束
            if seg_info_list[i].n_cycle_pass == 1:
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(
                        seg_info_list[i].t_end -
                        seg_info_list[i].t_start, True
                    )
                )
            else:  # 不在当前周期结束
                # 处理起始位置到该序列第一次刷新之间的传输
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(
                        T_REFI -
                        seg_info_list[i].t_start, True
                    )
                )
                fifo_ref_cycle_list.append(current_ref_cycle)
                current_ref_cycle = FifoRefCycle()

                # 处理中间传输完整刷新周期的部分
                for j in range(0, seg_info_list[i].n_cycle_pass - 2):
                    current_ref_cycle.append_fifo_seg(
                        FifoSeg(
                            T_RTI, False
                        )
                    )
                    current_ref_cycle.append_fifo_seg(
                        FifoSeg(
                            T_REFI - T_RTI, True
                        )
                    )
                    fifo_ref_cycle_list.append(current_ref_cycle)
                    current_ref_cycle = FifoRefCycle()

                # 处理最后传输结束的部分
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(
                        T_RTI, False
                    )
                )
                current_ref_cycle.append_fifo_seg(
                    FifoSeg(
                        seg_info_list[i].t_end - T_RTI, True
                    )
                )

        if current_ref_cycle and len(current_ref_cycle.get_fifo_seg_list()):
            fifo_ref_cycle_list.append(current_ref_cycle)

        return fifo_ref_cycle_list
