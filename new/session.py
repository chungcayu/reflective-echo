from datetime import datetime


class Session:
    def __init__(self):
        self.session_id = None
        self.thread_id = None
        self.start_time = None
        self.end_time = None
        self.input_tokens = None
        self.output_tokens = None
        self.total_tokens = None
        self.session_status = None

    def get_session_id(self):
        pass

    def create_thread_id(self):
        """创建线程"""
        return self.thread_id

    def get_thread_id(self):
        """从数据库获取线程"""
        pass

    def start_session(self, thread_id):
        """开始会话"""
        self.start_time = datetime.now()
        self.session_status = "active"

    def end_session(self):
        """结束会话"""
        self.end_time = datetime.now()
        self.session_status = "inactive"
        self.input_tokens = self.get_input_tokens()
        self.output_tokens = self.get_output_tokens()
        self.total_tokens = self.get_total_tokens()

    def check_session_status(self, thread_id):
        """检查会话状态"""
        # 获取会话上一次结束的时间
        # 检查结束时间至今是否超过一定时间
        # 如果超过，会话状态更改为closed
        # 如果未超过，会话状态保持原有状态
        # 返回会话状态

    def continue_session(self):
        """继续进行已结束的会话"""
        self.thread_id = self.get_thread_id()
        self.session_status = self.check_session_status(self.thread_id)
        if self.session_status != "closed":
            self.start_session(self.thread_id)
        else:
            print("会话已关闭，无法继续，请重新开始一次新会话。")

    def add_message(self):
        """添加消息"""
        pass

    def get_input_tokens(self):
        pass

    def get_output_tokens(self):
        pass

    def get_total_tokens(self):
        pass
