EXIT_INFO = "finished transfer"


class Sdram:
    def __init__(self, wfm_64byte_array) -> None:
        assert(len(wfm_64byte_array))

        self.__wfm_64byte_array = wfm_64byte_array
        # 要传输的波形序列
        self.__idx = 0
        # 播放到的序列id
        self.__current_wfm_64byte = wfm_64byte_array[0]
        self.__finished_tranfer = False

    def send_out(self):
        assert self.__current_wfm_64byte >= 0

        if not self.__current_wfm_64byte:

            self.__idx += 1
            if self.__idx == len(self.__wfm_64byte_array):
                self.__finished_tranfer = True
                return

            self.__current_wfm_64byte = self.__wfm_64byte_array[self.__idx]

        self.__current_wfm_64byte -= 1

    def get_in_sw(self):
        return not self.__current_wfm_64byte

    def get_finished_tranfer(self):
        return self.__finished_tranfer

    def get_current_wfm_64byte(self):
        return self.__current_wfm_64byte
