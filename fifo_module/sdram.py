EXIT_INFO = "finished transfer"


class Sdram:
    def __init__(self, wfm_64byte_array) -> None:
        assert(len(wfm_64byte_array))

        self.__wfm_64byte_array = wfm_64byte_array
        self.__idx = 0
        self.__current_wfm_64byte = wfm_64byte_array[0]
        self.__in_sw = False
        self.__finished_tranfer = False

    def send_out(self):
        assert self.__current_wfm_64byte > 0
        
        self.__current_wfm_64byte -= 1

        if not self.__current_wfm_64byte:

            self.__idx += 1
            if self.__idx == len(self.__wfm_64byte_array):
                self.__finished_tranfer = True
                return

            self.__current_wfm_64byte = self.__wfm_64byte_array[self.__idx]

            self.__in_sw = True
        
        else:
            self.__in_sw = False
            # 注意 get_in_sw 和 send_out之间的调用顺序
    
    def get_in_sw(self):
        return self.__in_sw

    def get_finished_tranfer(self):
        return self.__finished_tranfer

