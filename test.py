from itertools import cycle
import unittest
import random

from regex import E

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
WAVEFORM_MAX_LEN = 1e5
N_MIN = 10
N_MAX = 1e5
N_RESOLUTION = 10
S_OUT_RESOLUTION = 100


class TestBinarySearch(unittest.TestCase):
    @staticmethod
    def __init_fifo(fifo_trans_module):
        # 随机生成波形序列
        waveform_pts = []
        cycle_time = random.randint(1, WAVEFORM_PTS_MAX_LEN)
        for i in range(cycle_time):
            wave_l = random.randint(BL, WAVEFORM_MAX_LEN)
            waveform_pts.append(wave_l)
        fifo_trans_module.set_waveform_pts(waveform_pts)

        # 随机生成开始传输时间
        start_t_1st = random.uniform(0, T_REFI)
        fifo_trans_module.set_t_1st_start(start_t_1st)

        return fifo_trans_module

    def test_binary_search_n(self):
        fifo_trans_module = FifoTransModule(
            T_REFI=T_REFI, T_RTI=T_RTI, T_SW=T_SW
        )
        valid_n_min_number = 0
        for x in range(TEST_CYCLE_NUMBER):
            # 随机设置s_in
            s_in = random.uniform(S_IN_MIN, S_IN_MAX)
            fifo_trans_module.set_s_in(s_in)

            # 随机设置Sout
            s_out = random.uniform(S_OUT_MIN, s_in)
            fifo_trans_module.set_s_out(s_out)

            fifo_trans_module = TestBinarySearch.__init_fifo(fifo_trans_module)

            n_min = binary_search_n(
                fifo_trans_module, N_MIN, N_MAX, N_RESOLUTION)

            if n_min:
                self.assertTrue(n_min >= N_MIN and n_min <= N_MAX)

                fifo_trans_module.set_n(n_min)
                if_empty = fifo_trans_module.check_empty()
                self.assertTrue(not if_empty)

                valid_n_min_number += 1
            else:
                print(end="")  # debug用
        print(
            "valid_n_min_number: %d, TEST_CYCLE_NUMBER: %d" %
            (valid_n_min_number, TEST_CYCLE_NUMBER)
        )

    def test_binary_search_s_out(self):
        fifo_trans_module = FifoTransModule(
            T_REFI=T_REFI, T_RTI=T_RTI, T_SW=T_SW
        )
        valid_s_in_number = 0
        for x in range(TEST_CYCLE_NUMBER):
            # 随机设置s_in
            s_in = random.uniform(S_IN_MIN, S_IN_MAX)
            fifo_trans_module.set_s_in(s_in)

            # 随机设置n
            n = random.randint(N_MIN, N_MAX)
            fifo_trans_module.set_n(n)

            fifo_trans_module = TestBinarySearch.__init_fifo(fifo_trans_module)

            s_out_max = binary_search_s_out(
                fifo_trans_module, S_OUT_MIN, s_in, S_OUT_RESOLUTION)

            if s_out_max:
                self.assertTrue(s_out_max >= S_OUT_MIN and s_out_max <= s_in)

                fifo_trans_module.set_s_out(s_out_max)
                if_empty = fifo_trans_module.check_empty()
                self.assertTrue(not if_empty)

                valid_s_in_number += 1
            else:
                print(end="")  # debug用
        print(
            "valid_s_in_number: %d, TEST_CYCLE_NUMBER: %d" %
            (valid_s_in_number, TEST_CYCLE_NUMBER)
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
