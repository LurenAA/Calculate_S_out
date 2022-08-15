import math
import random
import unittest
import sys
import math
import os
import time

from clock import Clock
from fifo import Fifo, FifoEmpty
from sdram import Sdram

# T_REFI = 7.8e-6  # sec
# T_SW = 30e-9  # sec
# T_RTI = 190e-9  # sec
# BL = 8
# S_IN = 1600e6 / BL  # 64byte

BL = 8
S_IN = 1066e6 / BL
T_CK = 1 / 1066e6 * 2
T_RCD = 7 * T_CK
T_RP = 7 * T_CK
T_CL = 7 * T_CK
T_CCD = 4 * T_CK
T_RTP = max(4 * T_CK, 7.5e-9)
T_RFC = 160e-9

T_IN = 1 / S_IN
T_SW = math.ceil((T_RTP + T_RP + T_RCD - T_CCD) / T_IN) * T_IN
T_RTI = math.ceil((T_SW + T_RFC) / T_IN) * T_IN
T_REFI = math.floor(7.8e-6 / T_IN) * T_IN


NAX_N_SEQ_NUM = 100
MAX_K = 200
MAX_N = 100
TEST_TIMES = 1


class TestFifoModule(unittest.TestCase):
    dir_str = "./TestFifoModule"
    file_str = None

    def setUp(self) -> None:
        if not os.path.exists(TestFifoModule.dir_str):
            os.mkdir(TestFifoModule.dir_str)

    def test_if_empty(self):
        for o in range(TEST_TIMES):
            TestFifoModule.file_str = TestFifoModule.dir_str + "/" + \
                time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))

            # 随机生成K
            random.seed(time.time_ns() * 5 / 11)
            # K = random.randint(1, MAX_K)
            K = 4

            # 随机生成N
            random.seed(time.time_ns())
            # N = random.randint(1, MAX_N)
            N = 67

            B = math.ceil(K/N)

            S_OUT = (N * T_REFI - K * T_SW - N * T_RTI) / \
                (N * T_REFI) * S_IN  # 64byte
            T_SEQ = (N * T_REFI - K * T_SW - N * T_RTI) / K  # sec
            N_SEQ = math.ceil(T_SEQ * S_IN)  # 64byte
            N_FIFO = math.ceil(
                abs(
                    -(B*N - K)*(-B*N + K + N) / N * T_SW * S_IN -
                    (T_RTI + B * T_SW) * S_IN - K / N * T_SW * S_IN
                )
            )
            # 64byte

            # 随机生成序列长度
            random.seed(time.time_ns())
            # n_seq_num = random.randint(1, NAX_N_SEQ_NUM)
            n_seq_num = 67

            # 生成序列
            wfm_64byte_array = [N_SEQ for i in range(n_seq_num)]
            fifo_in_interval = 1 / S_IN
            # fifo_out_interval = math.ceil(1 / S_OUT * 1e12) / 1e12
            fifo_out_interval = 1 / S_OUT

            # 随机生成开始传输时间
            random.seed(time.time_ns())
            # t_start = round(random.uniform(0, T_REFI - T_SW), 9)
            t_start = 4049 * 1e-9

            ddr_sdram = Sdram(wfm_64byte_array)
            fifo = Fifo(N_FIFO)
            clock = Clock(fifo_in_interval, fifo_out_interval,
                          T_REFI, T_SW, T_RTI, t_start)

            with open(TestFifoModule.file_str, "w") as f:
                print_constant_parameter_info(
                    K, N, S_OUT, T_SEQ, N_SEQ, N_FIFO, f)
                print("fifo_in_interval: %.6f ns" %
                      (fifo_in_interval * 1e9), file=f)
                print("fifo_out_interval: %.6f ns" %
                      (fifo_out_interval * 1e9), file=f)
                print("wfm_64byte_array len: %d" % (n_seq_num), file=f)
                print("t_start: %.6f ns" % (t_start * 1e9), file=f)

                try:
                    while(not ddr_sdram.get_finished_tranfer()):
                        clock.run()
                        fin = clock.fifo_in_finish()
                        ffull = fifo.is_full()
                        fout = clock.fifo_out_finish()
                        dsw = clock.is_sw()

                        if fin and (not ffull):
                            ddr_sdram.send_out()
                            fifo.receive_in()

                            if ddr_sdram.get_in_sw():
                                clock.set_sw()

                        if fout:
                            fifo.send_out()

                        cur_fifo_n = fifo.get_n_64byte_fifo_current()
                        t_in_refi = clock.get_current_t_in_refi()
                        cur_wfm_64byte = ddr_sdram.get_current_wfm_64byte()
                        in_rti = clock.is_rti()

                        # 打印信息
                        print("t: %12.6fns" %
                              (t_in_refi * 1e9), end="\t", file=f)
                        print("fin: {:3}\t fout: {:3}\t dsw: {:3}".format(
                            fin, fout, dsw), end="\t", file=f)
                        print("rti: {:3}".format(in_rti), end="\t", file=f)
                        print(
                            "fifo_n: {:5}\t n_cycle: {:4}\t wfm_64byte: {:5}".
                            format(
                                cur_fifo_n, clock.get_current_cycle_num(),
                                cur_wfm_64byte),
                            file=f
                        )
                except FifoEmpty:
                    self.fail("FifoEmpty error happened")


def print_constant_parameter_info(
    K, N, S_OUT, T_SEQ, N_SEQ, N_FIFO, f=sys.stdout
):
    print("K: %d, N: %d" % (K, N), file=f)
    print("S_IN: %d  64bytes/s" % S_IN, file=f)
    print("S_OUT: %d  64bytes/s" % S_OUT, file=f)
    print("T_SEQ: %.6f ns" % (T_SEQ * 1e9), file=f)
    print("T_SW: %.6f ns" % (T_SW * 1e9), file=f)
    print("T_RTI: %.6f ns" % (T_RTI * 1e9), file=f)
    print("N_SEQ: %d  64bytes" % N_SEQ, file=f)
    print("N_FIFO: %d  64bytes" % N_FIFO, file=f)


if __name__ == '__main__':
    unittest.main()
