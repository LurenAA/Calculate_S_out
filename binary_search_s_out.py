from fifo_trans_module import FifoTransModule, FifoCantFull


def _fifo_not_empty_check(fifo_trans_module: FifoTransModule, s_out: float):
    fifo_trans_module.set_s_out(s_out)
    return not fifo_trans_module.check_empty()


def binary_search_s_out(
    fifo_trans_module: FifoTransModule,
    s_out_min: float, s_out_max: float, resolution: float
   ) -> (float or None):
    assert s_out_min >= 0 and s_out_max >= s_out_min

    try:
        while s_out_min + resolution <= s_out_max:
            s_out_mid = (s_out_min + s_out_max) / 2
            if _fifo_not_empty_check(fifo_trans_module, s_out_mid):
                s_out_min = s_out_mid
            else:
                s_out_max = s_out_mid
    except FifoCantFull:
        return None

    return (
        s_out_min
        if _fifo_not_empty_check(fifo_trans_module, s_out_min) else None
        )
