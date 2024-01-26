EXIT_INFO = "finished transfer"


class Sdram1:
    def __init__(self, nArr) -> None:
        # assert(len(wfm_64byte_array))

        # self.__wfm_64byte_array = wfm_64byte_array

        self.__nArr = nArr
        # 要传输的波形序列
        self.__idx = 0
        # 播放到的序列id
        self.__current_wfm_64byte = nArr[0]
        # self.__finished_tranfer = False

    def send_out(self):
        assert self.__current_wfm_64byte >= 0

        if not self.__current_wfm_64byte:
            # 当前波形段输出完毕后

            self.__idx = (self.__idx + 1) % len(self.__nArr)
            # 访问下一个波形段
            self.__current_wfm_64byte = self.__nArr[self.__idx]
            # 设置波形长度

        self.__current_wfm_64byte -= 1

    def get_in_sw(self):
        return not self.__current_wfm_64byte

    # def get_finished_tranfer(self):
    #     return self.__finished_tranfer

    def get_current_wfm_64byte(self):
        return self.__current_wfm_64byte
