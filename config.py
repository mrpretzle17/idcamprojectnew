import threading

class AppState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppState, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    @staticmethod #because its not recieving variables
    def get_instance():
        return AppState()

    def initialize(self):
        self.which_page = "login"
        # Camera and Threading Variables
        self.camera = None
        self.global_frame = None
        self.lock = threading.Lock()
        self.capture_thread = None

        # System States
        self.current_mode = "short"
        self.running = False


        # Face Recognition
        self.known_face_encodings = []
        self.known_face_labels = []
        self.known_class_of_face = []
        self.known_face_id = []
        self.PROCESS_EVERY_N_FRAMES = 2
        self.current_frame_count = 0
        self.firstface = True
        self.identnames = ["jhon", "sam"]
        self.identclass = [0, 0]
        self.identid = [0, 0]
        self.unknowns_fc = 0
        self.last_label = ""
        self.tess_smg = "yes"
        self.attendance_mode = False

        # School Data Lists
        self.grade_names_list = []
        self.class_names_list = []
        self.class_grade_id_list = []
        self.grade_id_list = []
        self.students_list = []
        self.class_id_list = []
