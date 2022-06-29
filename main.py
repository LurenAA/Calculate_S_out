from pickle import GLOBAL
from fifo_ref_cycle import bulid_fifo_ref_cycle_list
from check_empty import check_empty


if __name__ == '__main__':
    T_REFI = 7.8e-6
    T_RTI = 190.008e-9
    S_IN = 22.21875e9
    S_OUT = 12e9
    T_SW = 30.008e-9
    N = 2795
    waveform_pts = [2795, 173310, 173310]
    fifo_cycle_list = bulid_fifo_ref_cycle_list(
        waveform_pts, 0, T_REFI, T_RTI, T_SW, S_IN, N
        )
    for x in fifo_cycle_list:
        x.display()
    print(
        check_empty(
            fifo_cycle_list, T_REFI, T_RTI, T_SW, S_IN, S_OUT, N
            )
        )
