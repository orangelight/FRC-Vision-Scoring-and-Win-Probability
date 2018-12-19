class ScoreState:
    def __init__(self, time, red_score, blue_score, scale_control, red_switch_control, blue_switch_control):
        self.time = time
        self.red_score = red_score
        self.blue_score = blue_score
        self.scale_control = scale_control
        self.red_switch_control = red_switch_control
        self.blue_switch_control = blue_switch_control

    def factory_normal(time, red_score, blue_score, scale_control, red_switch_control, blue_switch_control):
        return NormalState(time, red_score, blue_score, scale_control, red_switch_control, blue_switch_control)

    def factory_empty(time):
        return EmptyState(time, None, None, None, None, None)

    factory_normal = staticmethod(factory_normal)
    factory_empty = staticmethod(factory_empty)

    def __repr__(self):
        return str(self.time) + ' ' + str(self.red_score) + ' ' + str(self.blue_score) + ' ' +\
               str(self.scale_control) + ' ' + str(self.red_switch_control) + ' ' + str(self.blue_switch_control)


class NormalState(ScoreState):
    def get_sql_format(self):
        return (self.time, int(self.red_score), int(self.blue_score), int(self.scale_control.value),
                int(self.red_switch_control), int(self.blue_switch_control))


class EmptyState(ScoreState):
    def get_sql_format(self):
        return (self.time, None, None, None, None, None)


