import pickle
import cv2
import numpy as np
from flask import flash
from sqlclientsocket import send_sql
import dlib
from config import AppState
face_detector = dlib.get_frontal_face_detector()
face_recognition_model = dlib.face_recognition_model_v1("/home/jonahrpi/Desktop/idcamproject/dlib_face_recognition_resnet_model_v1.dat")
shape_predictor = dlib.shape_predictor("/home/jonahrpi/Desktop/idcamproject/shape_predictor_68_face_landmarks.dat")


state = AppState()

class DataEdit:
    # def set_student_to_database(studentname, studentid, student_class_id):
    #     print("student add db entered")
    #     try:
    #         # im using """ because the query is in two lines
    #         query = """INSERT INTO students (name, student_entered_id, pic_uploaded, profile_pic, class_id)
    #         VALUES (%s, %s, %s, %s, %s)"""
    #         params = (studentname, studentid, False, None, student_class_id)
    #         response = send_sql(query, params)

    #         if b"SUCCESS" in response:
    #             print(f"Student '{studentname}' added to the database.")
    #             flash(f"Student '{studentname}' added to the database.", "success")
    #         else:
    #             print(f"Insert failed: {response.decode()}")
    #             flash(f"Error adding student to the database. {response.decode()}", "error")

    #     except Exception as e:
    #         print(f"Error adding student to the database: {e}")
    #         flash("Error adding student to the database.", "error")

    # def add_face_to_database(image, label):
    #     try:
    #         success, encoded_img = cv2.imencode(".jpg", image)
    #         if not success:
    #             raise ValueError("Failed to encode image.")

    #         image_blob = encoded_img.tobytes()
    #         insert_query = "INSERT INTO people (name, face_image) VALUES (%s, %s)"
    #         result = send_sql(insert_query, (label, image_blob))

    #         if b"SUCCESS" in result:
    #             state.known_face_labels.append(label)
    #             flash("Student added successfully!", "success")
    #         else:
    #             print(f"Insert error: {result.decode()}")
    #             flash("Error adding student face to database.", "error")

    #     except Exception as err:
    #         print(f"Error: {err}")
    #         flash("Error during face insertion.", "error")

    # def remove_face_from_database(label):
    #     try:
    #         print("in db func remove face")

    #         delete_query = "DELETE FROM people WHERE name = %s"
    #         result = send_sql(delete_query, (label,))

    #         if b"SUCCESS" in result:
    #             print(state.known_face_labels)
    #             if label in state.known_face_labels:
    #                 index = state.known_face_labels.index(label)
    #                 del state.known_face_encodings[index]
    #                 del state.known_face_labels[index]
    #             print(state.known_face_labels)
    #             flash("Student removed successfully!", "success")
    #         else:
    #             print(f"Delete error: {result.decode()}")
    #             flash("Error removing student face from database.", "error")

    #     except Exception as err:
    #         print(f"Error: {err}")
    #         flash("Unexpected error removing face.", "error")

    def load_known_faces_from_database():
        # im errasing the infoso it doesnt double
        state.known_face_encodings = []
        state.known_face_labels = []
        state.known_class_of_face = []
        state.known_face_id = []

        print("==========loading known faces from database============")

        try:
            print("Querying 'students' table...")
            # ,() because i have no params but the socket code is set up to recive params
            response = send_sql("SELECT name, pic_uploaded, student_entered_id, profile_pic, class_id FROM students", ())
            student_results = pickle.loads(response)
            print(f"this is {len(student_results)} records from 'students'.")

            for name, pic_uploaded, student_entered_id, face_blob, class_id in student_results:
                try:
                    if not pic_uploaded:
                        continue
                    # turns it from blob back to image
                    face_image = cv2.imdecode(np.frombuffer(face_blob, np.uint8), cv2.IMREAD_COLOR)
                    if face_image is None:
                        print(f"[WARNING] Failed to decode face image for {name} (students table)")
                        continue
                    # truns it into rgb for face detection
                    rgb_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
                    faces = face_detector(rgb_image, 0)
                    print(f"[DEBUG] Detected {len(faces)} face(s) for '{name}' in students table")

                    if faces:
                        face = faces[0]
                        shape = shape_predictor(rgb_image, face)
                        encoding = np.array(face_recognition_model.compute_face_descriptor(rgb_image, shape))

                        state.known_face_encodings.append(encoding)
                        state.known_face_labels.append(name)
                        state.known_class_of_face.append(class_id)
                        state.known_face_id.append(student_entered_id)
                        print("in load faces:", state.known_face_labels)
                except Exception as e:
                    print(f"[ERROR] Failed processing face for {name} (students table): {e}")

        except Exception as e:
            print(f"[ERROR] Failed to load from 'students': {e}")

        print(f"[SUMMARY] Total known faces loaded: {len(state.known_face_labels)}")
        if state.known_face_labels:
            print(f"[SUMMARY] First known face: {state.known_face_labels[0]}")

    def set_grade_to_database(gname):
        try:

            state = AppState()
            check_query = "SELECT COUNT(*) FROM grades WHERE grade_name = %s"
            raw = send_sql(check_query, (gname,))
            rows = pickle.loads(raw)           # => e.g. [(0,)] or [(1,)]
            count = rows[0][0]
            print(f"Existing students with that name: {count}")

            if count == 0:
                insert_query = "INSERT INTO grades (grade_name) VALUES (%s)"
                result = send_sql(insert_query, (gname,))
                if b"SUCCESS" in result:
                    print(f"Grade '{gname}' added to the database.")
                    flash("Grade added successfully!", "success")
                    state.grade_names_list.append(gname)
                else:
                    print(f"Insert failed: {result.decode()}")
                    flash("Error adding grade to the database.", "error")
            else:
                print(f"Grade '{gname}' already exists in the database.")
                flash("Grade already exists in the database.", "info")

        except Exception as e:
            print(f"Error: {e}")
            flash(f"Unexpected error adding grade.{e}", "error")

    def remove_grade_from_database(gname):
        try:
            state = AppState()
            check_query = "SELECT COUNT(*) FROM grades WHERE grade_name = %s"
            raw = send_sql(check_query, (gname,))
            rows = pickle.loads(raw)           # => e.g. [(0,)] or [(1,)]
            count = rows[0][0]
            print(f"Existing students with that name: {count}")

            if count > 0:
                delete_query = "DELETE FROM grades WHERE grade_name = %s"
                result = send_sql(delete_query, (gname,))
                if b"SUCCESS" in result:
                    print(f"Grade '{gname}' removed from the database.")
                    flash("Grade removed from the database.", "success")
                    if gname in state.grade_names_list:
                        state.grade_names_list.remove(gname)
                else:
                    print(f"Failed to delete grade: {result.decode()}")
                    flash("Failed to remove grade from the database.", "error")
            else:
                print(f"Grade '{gname}' does not exist in the database.")
                flash("Grade does not exist in the database.", "warning")

        except Exception as e:
            print(f"Error: {e}")
            flash(f"Unexpected error removing grade.{e}", "error")

    def set_class_to_database(cname, gradeid):
        try:
            state = AppState()
            check_query = "SELECT COUNT(*) FROM grades WHERE grade_id = %s"
            response = send_sql(check_query, (gradeid,))
            rows = pickle.loads(response)           # => e.g. [(0,)] or [(1,)]
            grade_exists = rows[0][0]
            print(f"Existing students with that name: {grade_exists}")

            if grade_exists == 1:
                insert_query = "INSERT INTO classes (class_name, grade_id) VALUES (%s, %s)"
                result = send_sql(insert_query, (cname, gradeid))
                if b"SUCCESS" in result:
                    print(f"class '{cname}' added to the database.")
                    flash("class added to the database.", "success")
                    state.class_names_list.append(cname)
                else:
                    print(f"Failed to insert class: {result.decode()}")
                    flash("Error adding class to the database.", "error")
            else:
                print(f"class '{cname}' already exists or grade check failed.")
                flash("class already exists in the database or gresult isn't working.", "warning")

        except Exception as e:
            print(f"Error: {e}")
            flash(f"Unexpected error adding class. {e}", "error")

    def remove_class_from_database(cname, gradeid):
        try:
            # check_class_query = "SELECT COUNT(*) FROM classes WHERE class_name = %s"
            # check_class_response = send_sql(check_class_query, (cname,))
            # class_exists = int(check_class_response.decode().strip())

            state = AppState()
            check_class_query = "SELECT COUNT(*) FROM classes WHERE class_name = %s"
            check_class_response = send_sql(check_class_query, (cname,))
            rows = pickle.loads(check_class_response)           # => e.g. [(0,)] or [(1,)]
            class_exists = rows[0][0]
            print(f"Existing students with that name: {class_exists}")

            # check_grade_query = "SELECT COUNT(*) FROM grades WHERE grade_id = %s"
            # check_grade_response = send_sql(check_grade_query, (gradeid,))
            # grade_exists = int(check_grade_response.decode().strip())

            check_grade_query = "SELECT COUNT(*) FROM grades WHERE grade_id = %s"
            check_grade_response = send_sql(check_grade_query, (gradeid,))
            rows = pickle.loads(check_grade_response)           # => e.g. [(0,)] or [(1,)]
            grade_exists = rows[0][0]
            print(f"Existing students with that name: {grade_exists}")

            if class_exists == 1 and grade_exists == 1:
                delete_query = "DELETE FROM classes WHERE class_name = %s"
                delete_response = send_sql(delete_query, (cname,))
                if b"SUCCESS" in delete_response:
                    print(f"class '{cname}' removed from the database.")
                    flash("class removed from the database.", "success")
                    if cname in state.State().class_names_list:
                        state.class_names_list.remove(cname)
                else:
                    flash("Failed to remove class.", "error")
            else:
                print(f"class '{cname}' does not exist or grade mismatch.")
                flash("class doesn't exist in the database or gresult isn't working.", "warning")

        except Exception as err:
            print(f"Error: {err}")

    # def remove_student_from_database(studentname, studentid, student_class_id):
    #     try:
    #         print("in remove student")
    #         print("student name:", studentname, "student_class_id:", student_class_id)

    #         # check_name_query = "SELECT COUNT(*) FROM students WHERE name = %s AND class_id = %s"
    #         # response = send_sql(check_name_query, (studentname, student_class_id))
    #         # count = int(response.decode().strip())
    #         # 1) Check for existing student
    #         check_query  = "SELECT COUNT(*) FROM students WHERE name = %s AND class_id = %s"
    #         check_params = (studentid, student_class_id)
    #         raw          = send_sql(check_query, check_params)

    #         # *UNPICKLE* the result of the SELECT
    #         rows  = pickle.loads(raw)      # e.g. [(0,)] or [(1,)]
    #         count = rows[0][0]
    #         print(f"Existing count: {count}", flush=True)

    #         if count > 0:
    #             delete_query = "DELETE FROM students WHERE name = %s AND class_id = %s"
    #             result = send_sql(delete_query, (studentname, student_class_id))
    #             if b"SUCCESS" in result:
    #                 flash("Student removed successfully!", "success")
    #                 state.State().students_list = [s for s in state.State().students_list if not (s[1] == studentname and s[4] == student_class_id)]
    #             else:
    #                 flash("Error removing student by name.", "error")
    #         else:
    #             check_id_query = "SELECT COUNT(*) FROM students WHERE student_entered_id = %s AND class_id = %s"
    #             response = send_sql(check_id_query, (studentid, student_class_id))
    #             count = int(response.decode().strip())
    #             print(count)

    #             if count > 0:
    #                 delete_query = "DELETE FROM students WHERE student_entered_id = %s AND class_id = %s"
    #                 result = send_sql(delete_query, (studentid, student_class_id))
    #                 if b"SUCCESS" in result:
    #                     print(f"student '{studentname}' removed from the database.")
    #                     flash("Student removed successfully!", "success")
    #                     state.State().students_list = [s for s in state.State().students_list if not (s[2] == studentid and s[4] == student_class_id)]
    #                 else:
    #                     flash("Error removing student by ID.", "error")
    #             else:
    #                 flash("Student not there!", "warning")
    #                 print("student isn't in database")

    #     except Exception as e:
    #         print(f"Error removing student: {e}")
    #         print(f"Error in add_fullperson_to_database: {e}", flush=True)
            
    def remove_student_from_database(studentname, studentid, student_class_id):
        state = AppState()
        try:
            print("in remove student")
            print(f"student name: {studentname}, student id: {studentid}, class id: {student_class_id}")

            # 1) Try deleting by name
            check_query = "SELECT COUNT(*) FROM students WHERE name = %s AND class_id = %s"
            raw = send_sql(check_query, (studentname, student_class_id))
            rows = pickle.loads(raw)           # => e.g. [(0,)] or [(1,)]
            count = rows[0][0]
            print(f"Existing students with that name: {count}")

            if count > 0:
                delete_query = "DELETE FROM students WHERE name = %s AND class_id = %s"
                result = send_sql(delete_query, (studentname, student_class_id))
                if b"SUCCESS" in result:
                    flash("Student removed successfully!", "success")
                    # Remove from in‐memory list
                    
                    state.students_list = [
                        s for s in state.students_list
                        if not (s[1] == studentname and s[4] == student_class_id)
                    ]
                else:
                    flash("Error removing student by name.", "error")
                return  # done

            # 2) Try deleting by entered ID
            check_id_query = "SELECT COUNT(*) FROM students WHERE student_entered_id = %s AND class_id = %s"
            raw_id = send_sql(check_id_query, (studentid, student_class_id))
            rows_id = pickle.loads(raw_id)
            count_id = rows_id[0][0]
            print(f"Existing students with that entered_id: {count_id}")

            if count_id > 0:
                delete_id_query = "DELETE FROM students WHERE student_entered_id = %s AND class_id = %s"
                result = send_sql(delete_id_query, (studentid, student_class_id))
                if b"SUCCESS" in result:
                    flash("Student removed successfully!", "success")
                    state = state.State()
                    state.students_list = [
                        s for s in state.students_list
                        if not (s[2] == studentid and s[4] == student_class_id)
                    ]
                else:
                    flash("Error removing student by ID.", "error")
                return  # done

            # 3) Not found at all
            flash("Student not found in database.", "warning")
            print("Student isn't in database")

        except Exception as e:
            print(f"Error removing student: {e}")
            flash(f"Unexpected error removing student.{e}1", "error")

    def get_students_list():
        try:
            query = "SELECT student_id, name, student_entered_id, pic_uploaded, class_id FROM students"
            response = send_sql(query, ())
            state.students_list = pickle.loads(response)
            print(f"{state.students_list}")
        except Exception as e:
            print(f"Error get_students_list: {e}")
            state.students_list = []

    def get_grade_names_list():
        try:
            query = "SELECT grade_name FROM grades"
            response = send_sql(query, ())
            results = pickle.loads(response)
            state.grade_names_list = [row[0] for row in results]
            print(f"Grade names: {state.grade_names_list}")
        except Exception as e:
            print(f"Error get_grade_names_list: {e}")
            state.grade_names_list = []

    def get_class_id_list():
        try:
            query = "SELECT class_id FROM classes"
            response = send_sql(query, ())
            results = pickle.loads(response)
            state.class_id_list = [row[0] for row in results]
            print(f"class ids: {state.class_id_list}")
        except Exception as e:
            print(f"get_class_id_list error: {e}")
            state.class_id_list = []

    def get_grade_id_list():
        try:
            query = "SELECT grade_id FROM grades"
            response = send_sql(query, ())
            results = pickle.loads(response)
            state.grade_id_list = [row[0] for row in results]
            print(f"Grade ID list: {state.grade_id_list}")
        except Exception as e:
            print(f"get_grade_id_list error: {e}")
            state.grade_id_list = []

    def get_class_names_list():
        try:
            query = "SELECT class_name FROM classes"
            response = send_sql(query, ())
            results = pickle.loads(response)
            state.class_names_list = [row[0] for row in results]
            print(f"class names: {state.class_names_list}")
        except Exception as e:
            print(f"get_class_names_list error: {e}")
            state.class_names_list = []

    def get_class_grade_id_list():
        try:
            query = "SELECT grade_id FROM classes"
            response = send_sql(query, ())
            try:
                results = pickle.loads(response)
                state.class_grade_id_list = [row[0] for row in results]
                print(f"class grade IDs: {state.class_grade_id_list}")
            except Exception as decode_err:
                print(f"Failed to decode response: {decode_err}")
                state.class_grade_id_list = []
        except Exception as e:
            print(f"Error in get_class_grade_id_list: {e}")
            state.class_grade_id_list = []

    def add_fullperson_to_database(face_image, studentname, studentid, student_class_id):
        print("add_fullperson_to_database function activated", flush=True)
        try:
            # 1) Check for existing student
            check_query  = "SELECT COUNT(*) FROM students WHERE student_entered_id = %s AND class_id = %s"
            check_params = (studentid, student_class_id)
            raw          = send_sql(check_query, check_params)

            # *UNPICKLE* the result of the SELECT
            rows  = pickle.loads(raw)      # e.g. [(0,)] or [(1,)]
            count = rows[0][0]
            print(f"Existing count: {count}", flush=True)

            # 2) If not found, insert
            if count == 0:
                image_blob = cv2.imencode(".jpg", face_image)[1].tobytes()
                insert_query = """
                    INSERT INTO students
                    (name, student_entered_id, pic_uploaded, profile_pic, class_id)
                    VALUES (%s, %s, %s, %s, %s)
                """
                insert_params = (studentname, studentid, True, image_blob, student_class_id)

                resp = send_sql(insert_query, insert_params)
                if resp == b"SUCCESS":
                    flash(f"Student '{studentname}' added to the database.", "success")
                    print(f"Student '{studentname}' added to the database.", flush=True)
                else:
                    flash("Error adding student to the database", "error")
                    print(f"Insert failed – raw server reply: {resp}", flush=True)

            else:
                flash("Student already exists in this class.", "warning")
                print("Student already exists.", flush=True)

        except Exception as e:
            flash(f"Error adding student to the database: {e}", "error")
            print(f"Error in add_fullperson_to_database: {e}", flush=True)



    def make_lists():
        print("make_lists() called")
        DataEdit.get_students_list()
        DataEdit.get_grade_names_list()
        DataEdit.get_grade_id_list()
        DataEdit.get_class_names_list()
        DataEdit.get_class_id_list()
        DataEdit.get_class_grade_id_list()
