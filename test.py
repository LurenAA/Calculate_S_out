import unittest
import random
import time
import math
import os

from fifo_trans_module import FifoTransModule
from binary_search_s_out import binary_search_s_out
from binary_search_n import binary_search_n


T_REFI = 7.8e-6
T_RTI = 190.008e-9
S_IN = 22.21875e9
S_OUT = 12e9
T_SW = 30.008e-9
N = 2795
BL = 8

TEST_CYCLE_NUMBER = 100
S_IN_MIN = 1e9
S_IN_MAX = 5e10
S_OUT_MIN = 5e6
S_OUT_MAX = 5e10
WAVEFORM_PTS_MAX_LEN = 500
WAVEFORM_MAX_LEN = 2e6
N_MIN = 10
N_MAX = 1e5
N_RESOLUTION = 10
S_OUT_RESOLUTION = 100


class TestBinarySearch(unittest.TestCase):
    dir_str = (
        "./fifo_trans_info" +
        time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
    )
    file_index = 0

    @staticmethod
    def __init_fifo(fifo_trans_module):
        # 初始化FIFO模型对象的波形序列和开始传输时间

        # 随机生成波形序列
        waveform_pts = []
        random.seed(time.time_ns() + WAVEFORM_PTS_MAX_LEN)
        cycle_time = random.randint(1, WAVEFORM_PTS_MAX_LEN)
        for i in range(cycle_time):
            random.seed(math.cos(time.time_ns()) + i)
            wave_l = random.randint(BL, WAVEFORM_MAX_LEN)
            waveform_pts.append(wave_l)
        fifo_trans_module.set_waveform_pts(waveform_pts)

        # 随机生成开始传输时间
        random.seed(time.time_ns() + T_REFI)
        start_t_1st = random.uniform(0, T_REFI)
        fifo_trans_module.set_t_1st_start(start_t_1st)

        return fifo_trans_module

    @staticmethod
    def __print_fifo_trans_info(fifo_trans_module: FifoTransModule, f):
        # 打印FIFO传输的信息到文件

        # 创建文件夹
        print("T_REFI:%8.3fns" % (fifo_trans_module.get_t_refi() * 1e9),
              file=f)
        print("T_RTI:%8.3fns" % (fifo_trans_module.get_t_rti() * 1e9),
              file=f)
        print("T_SW:%8.3fns" % (fifo_trans_module.get_t_sw() * 1e9),
              file=f)
        print("Sin: %8.3fGSa/s\nSout: %8.3fGSa/s" %
              (fifo_trans_module.get_s_in() * 1e-9,
               fifo_trans_module.get_s_out() * 1e-9), file=f)
        print("get_t_1st_start: %8.3fns" %
              (fifo_trans_module.get_t_1st_start() * 1e9), file=f)
        print("FIFO N: %d" % (fifo_trans_module.get_n()), file=f)
        print("waveform_pts:\n", fifo_trans_module.get_waveform_pts(),
              file=f)
        print("display_fifo_cycle_list:", file=f)
        fifo_trans_module.display_fifo_cycle_list(f)
        print("display_seg_info_list:", file=f)
        fifo_trans_module.display_seg_info_list(f)

    def test_binary_search_n(self):
        fifo_trans_module = FifoTransModule(  # 创建FIFO传输模型对象
            T_REFI=T_REFI, T_RTI=T_RTI, T_SW=T_SW
        )
        valid_n_min_number = 0  # 记录找到的满足要求的Fifo容量N的数量
        for x in range(TEST_CYCLE_NUMBER):  # 循环测试TEST_CYCLE_NUMBER次
            # 随机设置s_in
            random.seed(time.time_ns() + S_IN_MIN)
            s_in = random.uniform(S_IN_MIN, S_IN_MAX)
            fifo_trans_module.set_s_in(s_in)

            # 随机设置Sout
            random.seed(time.time_ns() + S_OUT_MIN)
            s_out = random.uniform(S_OUT_MIN, s_in)
            fifo_trans_module.set_s_out(s_out)

            # 随机设置波形序列、开始传输时间
            fifo_trans_module = TestBinarySearch.__init_fifo(fifo_trans_module)

            n_min = binary_search_n(  # 二分查找FIFO容量N
                fifo_trans_module, N_MIN, N_MAX, N_RESOLUTION)

            if n_min:  # 检验FIFO容量N是否合法
                self.assertTrue(n_min >= N_MIN and n_min <= N_MAX)

                # 检查是否会断流
                fifo_trans_module.set_n(n_min)

                if not os.path.exists(TestBinarySearch.dir_str):
                    os.mkdir(TestBinarySearch.dir_str)

                TestBinarySearch.file_index += 1
                with open(
                    TestBinarySearch.dir_str + "/fifo_trans" +
                    str(TestBinarySearch.file_index), 'w'
                ) as f:
                    TestBinarySearch.__print_fifo_trans_info(
                        fifo_trans_module, f
                        )

                    if_empty = fifo_trans_module.check_empty(True, file=f)
                    self.assertTrue(not if_empty)

                    valid_n_min_number += 1  # 满足要求的Fifo容量N的数量加一
            else:
                print(end="")  # debug用

        print(  # 打印调试信息
            "valid_n_min_number: %d, TEST_CYCLE_NUMBER: %d" %
            (valid_n_min_number, TEST_CYCLE_NUMBER)
        )

    def test_binary_search_s_out(self):
        fifo_trans_module = FifoTransModule(  # 创建FIFO传输模型对象
            T_REFI=T_REFI, T_RTI=T_RTI, T_SW=T_SW
        )
        valid_s_out_number = 0  # 记录找到的满足要求的s_out的数量
        for x in range(TEST_CYCLE_NUMBER):  # 循环测试TEST_CYCLE_NUMBER次
            # 随机设置s_in
            random.seed(time.time_ns() + S_IN_MIN)
            s_in = random.uniform(S_IN_MIN, S_IN_MAX)
            fifo_trans_module.set_s_in(s_in)

            # 随机设置n
            random.seed(time.time_ns() + N_MIN)
            n = random.randint(N_MIN, N_MAX)
            fifo_trans_module.set_n(n)

            # 随机设置波形序列、开始传输时间
            fifo_trans_module = TestBinarySearch.__init_fifo(fifo_trans_module)

            # 二分查找s_out
            s_out_max = binary_search_s_out(
                fifo_trans_module, S_OUT_MIN, s_in, S_OUT_RESOLUTION)

            if s_out_max:  # 校验Sout
                self.assertTrue(s_out_max >= S_OUT_MIN and s_out_max <= s_in)

                fifo_trans_module.set_s_out(s_out_max)
                if not os.path.exists(TestBinarySearch.dir_str):
                    os.mkdir(TestBinarySearch.dir_str)

                TestBinarySearch.file_index += 1
                with open(
                    TestBinarySearch.dir_str + "/fifo_trans" +
                    str(TestBinarySearch.file_index), 'w'
                ) as f:
                    TestBinarySearch.__print_fifo_trans_info(
                        fifo_trans_module, f)
                    if_empty = fifo_trans_module.check_empty(True, file=f)
                    self.assertTrue(not if_empty)

                    valid_s_out_number += 1
            else:
                print(end="")  # debug用

        print(
            "valid_s_in_number: %d, TEST_CYCLE_NUMBER: %d" %
            (valid_s_out_number, TEST_CYCLE_NUMBER)
        )


if __name__ == '__main__':
    unittest.main()
    # waveform_pts = [2795, 173310, 173310]

    # fifo_trans_module = FifoTransModule(
    #     waveform_pts, 0, T_REFI, T_RTI, T_SW, S_IN, S_OUT, N)
    # # fifo_trans_module.display_fifo_cycle_list()

    # # if_empty = fifo_trans_module.check_empty(show_debug_info=True)
    # # print("if_empty: {}".format(if_empty))
    # s_out_max = binary_search_s_out(fifo_trans_module, 0, S_IN, 100)

    # fifo_trans_module.set_s_out(s_out_max)
    # # if_empty = fifo_trans_module.check_empty(show_debug_info=True)
    # # print("if_empty: {}".format(if_empty))
    # n_min = binary_search_n(fifo_trans_module, 0, N + 1000, 10)
    # fifo_trans_module.set_n(n_min)
    # if_empty = fifo_trans_module.check_empty(show_debug_info=True)
    # print("if_empty: {}".format(if_empty))
