import math


class Clock:
    def __init__(self,
                 fifo_in_interval,
                 fifo_out_interval,
                 T_REFI,
                 T_SW,
                 T_RTI,
                 t_start=None) -> None:
        self.__fifo_in_t = 0
        self.__fifo_out_t = -1
        self.__send_start_flag = False
        self.__current_t = 0
        self.__t_start = t_start

        self.__fifo_in_interval = fifo_in_interval
        self.__fifo_out_interval = fifo_out_interval

        self.__fifo_in_finish = False
        self.__fifo_out_finish = False

        self.__T_REFI = T_REFI
        self.__T_SW = T_SW
        self.__T_RTI = T_RTI
        self.__current_cycle_num = 1

        self.__in_sw = False
        self.__sw_end_time = -1

    def set_t_start(self, t_start: float):
        if not self.__send_start_flag:
            self.__t_start = t_start

    def run(self):
        self.__fifo_in_finish = False
        self.__fifo_out_finish = False

        # FIFO没有开始向外输出
        if not self.__send_start_flag:

            self.__fifo_in_t += self.__fifo_in_interval
            self.__current_t = self.__fifo_in_t

            if(math.isclose(self.__current_t,
                            self.__t_start,
                            abs_tol=1e-11)
               or
                self.__t_start < self.__current_t
               ):
                self.__send_start_flag = True
                self.__fifo_out_t = self.__t_start
                self.set_sw()

            return

        # FIFO正在输出点数

        # 确定下一个时间
        fifo_in_t_tmp = self.__fifo_in_t + self.__fifo_in_interval
        fifo_out_t_tmp = self.__fifo_out_t + self.__fifo_out_interval
        fifo_in_time_flag = False
        fifo_out_time_flag = False

        if(fifo_in_t_tmp < fifo_out_t_tmp):
            self.__fifo_in_t = fifo_in_t_tmp
            self.__current_t = self.__fifo_in_t
            fifo_in_time_flag = True

        elif math.isclose(fifo_in_t_tmp, fifo_out_t_tmp, abs_tol=1e-11):
            self.__fifo_in_t = fifo_in_t_tmp
            self.__fifo_out_t = fifo_out_t_tmp
            self.__current_t = fifo_in_t_tmp
            fifo_in_time_flag = True
            fifo_out_time_flag = True

        else:
            self.__fifo_out_t = fifo_out_t_tmp
            self.__current_t = fifo_out_t_tmp
            fifo_out_time_flag = True

        if fifo_in_time_flag:
            # 确定该时间点处于刷新周期的位置
            t_in_refi = self.__current_t - \
                (self.__current_cycle_num - 1) * self.__T_REFI

            if(
                (not self.__in_sw) and
               t_in_refi > self.__T_RTI and
               (
                    (t_in_refi - self.__fifo_in_interval > self.__T_RTI)
                    or
                    math.isclose(
                    t_in_refi - self.__fifo_in_interval,
                    self.__T_RTI, abs_tol=1e-11
                    )
                )
               ):
                self.__fifo_in_finish = True

            if(self.__in_sw and
               (self.__current_t > self.__sw_end_time or
                math.isclose(self.__current_t,
                             self.__sw_end_time, abs_tol=1e-11))
               ):
                self.__in_sw = False
                self.__sw_end_time = -1

        if fifo_out_time_flag:
            self.__fifo_out_finish = True

        # 处理刷新周期
        if (
            math.isclose(
                self.__current_t,
                self.__current_cycle_num * self.__T_REFI,
                abs_tol=1e-11)
            or
            self.__current_t > self.__current_cycle_num * self.__T_REFI
        ):
            # self.__current_t = self.__current_cycle_num * self.__T_REFI
            self.__fifo_in_t = self.__current_cycle_num * self.__T_REFI
            self.__current_cycle_num += 1

    def fifo_in_finish(self):
        return self.__fifo_in_finish

    def fifo_out_finish(self):
        return self.__fifo_out_finish

    def get_current_t(self):
        return self.__current_t

    def get_current_t_in_refi(self):
        return self.__current_t - \
            (self.__current_cycle_num - 1) * self.__T_REFI

    def set_sw(self):
        self.__in_sw = True

        t_in_refi = self.__current_t - (self.__current_cycle_num - 1) *\
            self.__T_REFI

        if t_in_refi > self.__T_REFI - self.__T_SW:
            self.__sw_end_time = self.__current_cycle_num * self.__T_REFI +\
                self.__T_RTI
        else:
            self.__sw_end_time = self.__current_t + self.__T_SW

    def get_current_cycle_num(self):
        return self.__current_cycle_num

    def is_sw(self):
        # return (self.__sw_end_time - self.__current_t > 0
        #         or math.isclose(
        #             self.__current_t, self.__sw_end_time, abs_tol=1e-11
        #         )
        #         )
        return self.__in_sw

    def is_rti(self):
        t = self.get_current_t_in_refi()
        return (
            t < self.__T_RTI or
            math.isclose(t, self.__T_RTI, abs_tol=1e-11)
        )
