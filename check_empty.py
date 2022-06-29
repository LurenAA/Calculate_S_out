import math


def check_empty(
    fifo_ref_cycle_list: list,
    T_REFI: float, T_RTI: float, T_SW: float,
    S_IN: float, S_OUT: float, N: int
   ) -> bool:
    '''
    测试FIFO在传输过程中是否会空
    '''
    current_fifo_n = N
    for idx, cycle in enumerate(fifo_ref_cycle_list):
        print("cycle %2d" % (idx + 1))
        for seg in cycle.fifo_seg_list:
            delta_n = math.ceil(
                seg.t * (
                    (S_IN - S_OUT) if seg.is_ram_2_fifo_trans else (-S_OUT)
                    )
            )
            print("\t", end= "")
            seg.display("\t")
            
            fifo_n_before = current_fifo_n
            current_fifo_n += delta_n
            if current_fifo_n >= N:
                current_fifo_n = N
            
            print("fifo_n_before: %5d\tdelta_n: %5d\tfifo_n_after: %5d" % (
                fifo_n_before, delta_n, current_fifo_n
                ))
            
            if current_fifo_n < 0:
                return True

    return False
