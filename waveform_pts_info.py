import math


class WaveFormPtsInfo:
    def __init__(self, n_seq, bandwidth=64,
                 bl=8, pt_len=16) -> None:
        # 64bit(bandwidth) * 8(BL) / (16 bit/pt)
        pts_transfer_per_bl = bandwidth * bl / pt_len  # pts/bl

        self.n_seq = n_seq
        self.n_trans = math.ceil(
            self.n_seq / pts_transfer_per_bl) * pts_transfer_per_bl
