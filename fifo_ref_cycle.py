from fifo_seg import FifoSeg
from seg_info import build_seg_info_list


class FifoRefCycle:
    '''
    表示一个刷新周期，fifo_seg_list中存储FifoSeg对象。
    FifoSeg表示刷新周期中一段长度为t的时间（可能在传输或者断流）
    '''
    def __init__(self) -> None:
        self.fifo_seg_list = list()

    def append_fifo_seg(self, fifo_seg):
        self.fifo_seg_list.append(fifo_seg)
    
    def display(self):
        print("FifoRefCycle:")
        for x in self.fifo_seg_list:
            print("\t", end= "")
            x.display()


def bulid_fifo_ref_cycle_list(
    waveform_pts: list,
    t_1st_start: float,
    T_REFI: float,
    T_RTI: float, T_SW: float,
    S_IN: float, N: int
   ) -> list:
    '''
    通过波形点序列构建FifoRefCycle对象 t_1st_start指FIFO满后FIFO第一次开始输出的时间
    '''
    # 获取序列传输信息的列表
    seg_info_list = build_seg_info_list(
        waveform_pts, t_1st_start, T_REFI, T_RTI, T_SW, S_IN, N
     )

    # 打印
    for x in seg_info_list:
        x.display()

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
    
    if current_ref_cycle and len(current_ref_cycle.fifo_seg_list):
        fifo_ref_cycle_list.append(current_ref_cycle)

    return fifo_ref_cycle_list
            
