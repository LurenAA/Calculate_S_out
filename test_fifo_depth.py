import unittest
import random
import time
import math
import os


from fifo_trans_module import FifoTransModule


K = 34
N = 7
B = math.ceil(K/N)
T_REFI = 7.8e-6
T_SW = 30e-9
T_RTI = 190e-9
BL = 8
S_IN = math.ceil(1600e6 * 16 / 12)
S_OUT = math.floor((N * T_REFI - K * T_SW - N * T_RTI) / (N * T_REFI) * S_IN)
T_SEQ = (N * T_REFI - K * T_SW - N * T_RTI) / K
N_SEQ = math.ceil(T_SEQ * S_IN)
N_FIFO = math.ceil(abs(-(B*N - K)*(-B*N + K + N) / N * T_SW * S_IN -
                       (T_RTI + B * T_SW) * S_IN - K / N * T_SW * S_IN))

TEST_TIMES = 100
MAX_WAVEFORM_PTS_LEN = 1000
MAX_K = 100
MAX_N = 1000


class TestFifoDepth(unittest.TestCase):
    dir_str = (
        "./TestFifoDepth " +
        time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(time.time()))
    )
    file_index = 0

    def setUp(self) -> None:
        if not os.path.exists(TestFifoDepth.dir_str):
            os.mkdir(TestFifoDepth.dir_str)

    @staticmethod
    def __show_module_info(f):
        print("T_SEQ: %.3fns" % (T_SEQ * 1e9), file=f)
        print("N_SEQ: %d" % N_SEQ, file=f)

    @staticmethod
    def __initialize_fifo_trans_module(
            fifo_trans_module: FifoTransModule = None):
        if(fifo_trans_module is None):
            # 创建FIFO传输模型对象
            fifo_trans_module = FifoTransModule(
                T_REFI=T_REFI, T_RTI=T_RTI, T_SW=T_SW,
                S_IN=S_IN, S_OUT=S_OUT, N=N_FIFO
            )

        waveform_pts = [N_FIFO]

        # 随机生成波形序列
        random.seed(time.time_ns() + MAX_WAVEFORM_PTS_LEN)
        seq_num = random.randint(1, MAX_WAVEFORM_PTS_LEN)

        tmp_waveform_pts = [N_SEQ for j in range(seq_num)]
        waveform_pts.extend(tmp_waveform_pts)

        fifo_trans_module.set_waveform_pts(waveform_pts)

        # 随机生成开始传输时间
        random.seed(time.time_ns() + T_REFI)
        start_t_1st = round(random.uniform(0, T_REFI - T_SW), 9)
        fifo_trans_module.set_t_1st_start(start_t_1st)

        return fifo_trans_module

    def test_fifo_empty(self):
        fifo_trans_module = None

        for i in range(TEST_TIMES):
            fifo_trans_module = TestFifoDepth.__initialize_fifo_trans_module(
                fifo_trans_module)

            TestFifoDepth.file_index += 1
            with open(
                TestFifoDepth.dir_str + "/TestFifoDepth " +
                str(TestFifoDepth.file_index), 'w'
            ) as f:
                TestFifoDepth.__show_module_info(f)
                fifo_trans_module.print_fifo_trans_info(f)

                is_empty = fifo_trans_module.check_empty(True, f)
                self.assertTrue(not is_empty)

    def test_fifo_n(self):
        for i in range(TEST_TIMES):

            random.seed(time.time_ns() + MAX_K)
            k = random.randint(1, MAX_K)

            random.seed(time.time_ns() + MAX_N)
            n = random.randint(1, MAX_N)

            b = math.ceil(K/N)

            n_fifo = math.ceil(
                abs(-(b*n - k)*(-b*n + k + n) / n * T_SW * S_IN -
                    (T_RTI + b * T_SW) * S_IN - k / n * T_SW * S_IN)
            )

            TestFifoDepth.file_index += 1
            with open(
                TestFifoDepth.dir_str + "/TestFifoN " +
                str(TestFifoDepth.file_index), 'w'
            ) as f:
                print("k: %d, n: %d, n_fifo: %d" % (k, n, n_fifo), file = f)


if __name__ == '__main__':
    unittest.main()
