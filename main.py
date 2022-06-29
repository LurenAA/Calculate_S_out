from fifo_trans_module import FifoTransModule


if __name__ == '__main__':
    T_REFI = 7.8e-6
    T_RTI = 190.008e-9
    S_IN = 22.21875e9
    S_OUT = 12e9
    T_SW = 30.008e-9
    N = 2795
    waveform_pts = [2795, 173310, 173310]

    fifo_trans_module = FifoTransModule(
        waveform_pts, 0, T_REFI, T_RTI, T_SW, S_IN, S_OUT, N)

    fifo_trans_module.display_fifo_cycle_list()

    if_empty = fifo_trans_module.check_empty(show_debug_info=True)
    print("if_empty: {}".format(if_empty))