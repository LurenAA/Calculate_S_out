import math
import sys

from fifo_ref_cycle import FifoRefCycle
from seg_info import build_seg_info_list
from fifo_seg import FifoSeg


# FIFO传输模型有参数没有设置
class FifoParameterNotSet(Exception):
    pass


# 最开始波形点数不够FIFO填满
class FifoCantFull(Exception):
    pass


class FifoTransModule:
    def __init__(self, waveform_pts: list = None,
                 t_1st_start: float = None,
                 T_REFI=None, T_RTI=None,
                 T_SW=None, S_IN=None,
                 S_OUT=None, N=None
                 ) -> None:
        # 获取序列传输信息的列表
        self.__waveform_pts = waveform_pts  # 波形点数长度的序列
        self.__t_1st_start = t_1st_start
        self.__T_REFI = T_REFI
        self.__T_RTI = T_RTI
        self.__T_SW = T_SW
        self.__S_IN = S_IN
        self.__S_OUT = S_OUT
        self.__N = N
        self.__seg_info_list = None  # 序列传输信息SegInfo的序列
        self.__fifo_cycle_list = None  # 刷新周期传输模型FifoRefCircle的序列

    def __refresh_seg_and_cycle_list(self):
        # 如果更改了FIFO传输模型的参数，更新两个序列
        if not (None in (self.__waveform_pts, self.__t_1st_start,
                self.__T_REFI, self.__T_RTI,
                self.__T_SW, self.__S_IN, self.__N)):
            self.__seg_info_list = build_seg_info_list(
                self.__waveform_pts, self.__t_1st_start,
                self.__T_REFI, self.__T_RTI,
                self.__T_SW, self.__S_IN, self.__N
            )

            self.__fifo_cycle_list = (
                FifoTransModule.bulid_fifo_ref_cycle_list(
                    self.__seg_info_list, self.__t_1st_start,
                    self.__T_REFI, self.__T_RTI,
                    self.__T_SW, self.__S_IN, self.__N
                )
            )

    def get_t_refi(self):
        return self.__T_REFI

    def get_t_rti(self):
        return self.__T_RTI

    def get_t_sw(self):
        return self.__T_SW

    def set_waveform_pts(self, waveform_pts):
        self.__waveform_pts = waveform_pts
        self.__refresh_seg_and_cycle_list()

    def get_waveform_pts(self):
        return self.__waveform_pts

    def get_t_1st_start(self):
        return self.__t_1st_start

    def set_t_1st_start(self, t_1st_start):
        self.__t_1st_start = t_1st_start
        self.__refresh_seg_and_cycle_list()

    def set_s_in(self, s_in):
        self.__S_IN = s_in
        self.__refresh_seg_and_cycle_list()

    def get_s_in(self):
        return self.__S_IN

    def get_n(self): return self.__N

    def set_n(self, n: int):
        assert n > 0

        if n != self.__N:
            self.__N = n
            self.__refresh_seg_and_cycle_list()

    def get_s_out(self): return self.__S_OUT

    def set_s_out(self, new_s_out: float):
        assert new_s_out > 0

        self.__S_OUT = new_s_out

    # 打印刷新周期传输模型FifoRefCircle的序列
    def display_fifo_cycle_list(self, file=sys.stdout):
        if self.__fifo_cycle_list is None:
            return
        for x in self.__fifo_cycle_list:
            x.display(file=file)

    # 打印序列传输信息SegInfo的序列
    def display_seg_info_list(self, file=sys.stdout):
        if self.__seg_info_list is None:
            return
        for x in self.__seg_info_list:
            x.display(file=file)

    def print_fifo_trans_info(self, f):
        # 打印FIFO传输的信息到文件

        # 创建文件夹
        print("T_REFI:%8.3fns" % (self.get_t_refi() * 1e9),
              file=f)
        print("T_RTI:%8.3fns" % (self.get_t_rti() * 1e9),
              file=f)
        print("T_SW:%8.3fns" % (self.get_t_sw() * 1e9),
              file=f)
        print("Sin: %8.3fGSa/s\nSout: %8.3fGSa/s" %
              (self.get_s_in() * 1e-9,
               self.get_s_out() * 1e-9), file=f)
        print("get_t_1st_start: %8.3fns" %
              (self.get_t_1st_start() * 1e9), file=f)
        print("FIFO N: %d" % (self.get_n()), file=f)
        print("waveform_pts:\n", self.get_waveform_pts(),
              file=f)
        print("display_seg_info_list:", file=f)
        self.display_seg_info_list(f)
        print("display_fifo_cycle_list:", file=f)
        self.display_fifo_cycle_list(f)

    # 检测传输过程中FIFO是否会断流
    def check_empty(
        self, show_debug_info: bool = False, file=sys.stdout
    ) -> bool:
        '''
        测试FIFO在传输过程中是否会空
        '''
        if (  # 缺少参数报错
            not self.__waveform_pts or
            not self.__S_OUT or
            not self.__N or
            not self.__T_REFI or
            self.__t_1st_start is None or
            not self.__S_IN or
            not self.__T_SW or
            not self.__T_RTI
        ):
            raise FifoParameterNotSet

        if show_debug_info:  # 调试信息
            print("check empty", file=file)
        current_fifo_n = self.__N  # 记录fifo当前点数
        for idx, cycle in enumerate(self.__fifo_cycle_list):
            if show_debug_info:  # 调试信息
                print("cycle %2d" % (idx + 1), file=file)
            for seg in cycle:
                delta_n = math.floor(  # 波形点变化量
                    seg.t * (
                        (
                            (self.__S_IN - self.__S_OUT)
                            if seg.is_ram_2_fifo_trans else (-self.__S_OUT)
                        )
                    )
                )
                if show_debug_info:  # 调试信息
                    print("\t", end="", file=file)
                    seg.display("\t", file=file)

                fifo_n_before = current_fifo_n  # 调试打印用
                current_fifo_n += delta_n
                if current_fifo_n >= self.__N:  # FIFO满了后不再增长
                    current_fifo_n = self.__N

                if show_debug_info:  # 调试信息
                    print(
                        ("fifo_n_before: %5d\t"
                         "delta_n: %5d\tfifo_n_after: %5d") % (
                            fifo_n_before, delta_n, current_fifo_n),
                        file=file,
                        flush=True
                    )

                if current_fifo_n < 0:  # 判断断流
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
        else:
            current_ref_cycle.append_fifo_seg(
                FifoSeg(T_SW, False)
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

        # 添加最后一个刷新周期模型对象
        if current_ref_cycle and len(current_ref_cycle.get_fifo_seg_list()):
            fifo_ref_cycle_list.append(current_ref_cycle)

        return fifo_ref_cycle_list
