import math


class SegInfo:
    '''
    序列的传输信息
    '''
    def __init__(
        self,
        t_start: float,
        t_end: float,
        n_cycle_pass: int,
        is_in_next_cycle: bool = False
       ) -> None:
        self.t_start = t_start
        self.t_end = t_end
        self.n_cycle_pass = n_cycle_pass
        self.is_in_next_cycle = is_in_next_cycle

    def display(self):
        print(
            ("t_start: %8.3fns, t_end: %8.3fns, "
             "n_cycle_pass: %d, is_in_next_cycle: %d") % (
                self.t_start * 1e9, self.t_end * 1e9,
                self.n_cycle_pass, self.is_in_next_cycle
                )
        )


def get_seg_trans_info(
    len: int, t_start: float,
    T_RTI: float, T_REFI: float,
    S_IN: float
   ) -> SegInfo:
    '''
    return t_end  n_cycle_pass
    通过序列长度、开始时间、输入速度计算出该序列传输结束后的位置
    以及经过的完整周期数
    '''
    try:
        assert T_RTI >= 0 and T_REFI >= 0 and S_IN >= 0
        assert len >= 0
        assert t_start >= 0
        assert t_start <= T_REFI
        assert T_RTI < T_REFI
    except Exception as x:
        raise x  # debug用

    if t_start < T_RTI:
        t_start = T_RTI

    len_2_1st_refresh = (T_REFI - t_start) * S_IN
    n_cycle_pass = 1
    t_end = 0

    if len <= len_2_1st_refresh:
        t_end = t_start + len / S_IN
    else:
        n_complete_cycle_pass = math.floor(
            (len - len_2_1st_refresh)
            /
            (S_IN * (T_REFI - T_RTI))
        )

        assert n_complete_cycle_pass >= 0
        n_cycle_pass += n_complete_cycle_pass if n_complete_cycle_pass else 1
        t_end = (
            len - len_2_1st_refresh -
            n_complete_cycle_pass * (S_IN) * (T_REFI - T_RTI)
            ) / S_IN + T_RTI

    return SegInfo(t_start, t_end, n_cycle_pass)


def get_next_seg_start(
    t_end: float, S_IN: float,
    T_SW: float, T_REFI: float,
    T_RTI: float, BL: int = 8
   ) -> tuple[bool, float]:
    '''
    return is_in_next_cycle t_next_start
    通过t_end计算下一个序列开始的位置
    假设：当前序列传输完毕后，刷新周期剩余时间过小，不足下一个序列传输一个burst时，SDRAM进入idle状态
         等待下一个刷新周期SDRAM刷新完成后，再传输下一个序列。
    '''
    assert t_end > 0 and T_SW > 0 and T_REFI > 0
    assert t_end <= T_REFI and T_SW < T_REFI

    is_in_next_cycle = bool((t_end + T_SW + BL / S_IN) > T_REFI)
    t_next_start = T_RTI if is_in_next_cycle else t_end + T_SW

    return is_in_next_cycle, t_next_start


def build_seg_info_list(
    waveform_pts: list,
    t_1st_start: float,
    T_REFI: float,
    T_RTI: float, T_SW: float,
    S_IN: float, N: int
   ) -> list:
    '''
       创建序列传输信息的列表
    '''
    assert len(waveform_pts) > 0

    # 先把FIFO填满
    waveform_pts = waveform_pts.copy()
    sum = 0
    idx = 0
    for idx, val in enumerate(waveform_pts):
        sum += val
        if sum >= N:
            break

    from fifo_trans_module import FifoCantFull
    # 序列太短FIFO无法充满
    if sum < N:
        raise FifoCantFull

    waveform_pts[idx] = sum - N
    waveform_pts = (
        waveform_pts[idx:] if waveform_pts[idx] else waveform_pts[idx + 1:]
    )

    # 构建序列传输信息的序列
    seg_info_list = list()
    seg_info_tmp = None
    for idx, val in enumerate(waveform_pts):
        if not idx:
            seg_info_tmp = get_seg_trans_info(
                val, t_1st_start, T_RTI, T_REFI, S_IN
               )
        else:
            is_in_next_cycle, t_next_start = get_next_seg_start(
                seg_info_list[idx - 1].t_end,
                S_IN, T_SW, T_REFI, T_RTI
                )
            seg_info_tmp = get_seg_trans_info(
                val, t_next_start, T_RTI, T_REFI, S_IN
               )
            seg_info_tmp.is_in_next_cycle = is_in_next_cycle
        seg_info_list.append(seg_info_tmp)

    return seg_info_list
