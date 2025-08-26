# Standard libraries
import sys
import os
import sqlite3
import json

# Local modules
from db_utils import (create_users_database, insert_user, get_user, execute_query, 
                    create_database, delete_table, delete_database, get_databases_in_folder,
                    query_from_nl_to_sql)


# External libraries
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit,
                                QPushButton, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                                QTreeWidget, QTreeWidgetItem, QFileDialog)
from PyQt5.QtCore import Qt, QRectF, QTimer
from PyQt5.QtGui import QPainterPath, QRegion, QPixmap
import bcrypt


#######################################################
### Definine a class for windows with round corners ###
#######################################################


class RoundCornersWindow(QWidget):
    """
    This class is a starting sample for all the windows involved in
    the program.
    It is an extension of the QWidget class (a built-in class of PyQt5)
    wich extrends it with round corners (earned by the application of a
    visual mask) and with the possibility to drag the window
    (mousePressEvent/mouseReleaseEvent/MouseMoveEvent)
    """

    def __init__(self, width, height, background_color):
        super().__init__()
        self.resize(width, height)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(f"background-color: {background_color}")
        self.set_corner_radius(20)
        self._mouse_pos = None
    
    def set_corner_radius(self, radius):
        rect = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        polygon = path.toFillPolygon()
        region = QRegion(polygon.toPolygon())
        self.setMask(region)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._mouse_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self._mouse_pos:
            self.move(event.globalPos() - self._mouse_pos)
            event.accept()
        
    def mouseReleaseEvent(self, event):
        self._mouse_pos = None
        event.accept()


####################
### Login window ###
####################


class LoginWindow(RoundCornersWindow):


    def __init__(self, width, height, background_color):
        """
        extends RoundCornersWindow with a custom 
        user interface design
        Args:
        -width
        -height
        -background color
        """
        super().__init__(width, height, background_color)
        self.ui_design()
        
    def ui_design(self):

        # Title
        self.title = QLabel("MonkeyDB Database Manager", self)
        self.title.setStyleSheet("""
            font-size: 25px;
            font-weight: bold;
            color: white;        
        """
        )
        self.title.setGeometry(228, 70, 400, 30)

        # Title label
        self.title_label = QLabel("Please sign up or login to access your services", 
                                  self)
        self.title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
        """
        )
        self.title_label.setGeometry(228, 110, 400, 25)

        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.close_button.setGeometry(self.width() - 37, 5, 30, 30)
        self.close_button.clicked.connect(self.close)

        # Maximize button
        self.maximize_button = QPushButton("❐", self)
        self.maximize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.maximize_button.setGeometry(self.width() - 67, 5, 30, 30)
        self.maximize_button.clicked.connect(self.showMaximized)

        # Minimize button
        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.minimize_button.setGeometry(self.width() - 97, 5, 20, 30)
        self.minimize_button.clicked.connect(self.showMinimized)
        

        # Username
        self.insert_username = QLineEdit(self)
        self.insert_username.setPlaceholderText("Username")
        self.insert_username.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px
        """
        )
        self.insert_username.setGeometry(300, 180, 230, 42)
        
        # Password
        self.insert_password = QLineEdit(self)
        self.insert_password.setPlaceholderText("Password")
        self.insert_password.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px;
        """
        )
        self.insert_password.setEchoMode(QLineEdit.Password)
        self.insert_password.setGeometry(300, 250, 230, 42)

        # Login button
        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.login_button.setGeometry(300, 320, 90, 30)
        self.login_button.clicked.connect(self.authorize_login)

        # Sign-up button
        self.sign_up_button = QPushButton("Sign up", self)
        self.sign_up_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.sign_up_button.setGeometry(400, 320, 100, 30)
        self.sign_up_button.clicked.connect(self.go_to_signUp)

        # Toggle password button
        self.toggle_password_button = QPushButton("🙈", self)
        self.toggle_password_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: Orchid;
                border-radius: 10px;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px
            }
        """
        )
        self.toggle_password_button.clicked.connect(self.toggle_password)
        self.toggle_password_button.setGeometry(540, 255, 32, 32)

        # Image
        image_label = QLabel(self)
        pixmap = QPixmap("monkey.png")
        image_label.setPixmap(pixmap)
        image_label.setGeometry(0, 330, pixmap.width(), pixmap.height())
                        
        self.login_label = QLabel("", self)
        self.login_label.setGeometry(300, 370, 300, 22)
        self.login_label.hide()

    def toggle_password(self):
        """
        Toggle the visibility of the password input field
        Changes between QLineEdit.Normal and QLineEdit.Password
        """
        if self.insert_password.echoMode() == QLineEdit.Password:
            self.insert_password.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("🙉")
        else:
            self.insert_password.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("🙈")

    def authorize_login(self):
        """
        Verifies username and password with bcrypt
        It also updates a label wich comunicates to the user
        the outcome of the authentication process
        """
        self.username = self.insert_username.text()
        self.password = self.insert_password.text()
        user = get_user(self.username)
        
        if user and bcrypt.checkpw(self.password.encode("utf-8"), user[3]):
            self.login_label.setText(f"Welcome {self.username}!")
            self.login_label.setStyleSheet("""
                color: LimeGreen;
                font-size: 14px;
            """
            )
            self.login_label.show()
            self.close()
            workspace_window.title.setText(f"MonkeyDB Database Manager: {self.username}'s Workspace")
            workspace_window.show()
            return True
        
        elif user:
            self.login_label.setText("Wrong password or username")
            self.login_label.setStyleSheet("""
            color: Red;
            font-size: 14px;
            """
            )
            self.login_label.show()
            return False

        else:
            self.login_label.setText("Username not found, please sign up")
            self.login_label.setStyleSheet("""
            color: Red;
            font-size: 14px;
            """
            )
            self.login_label.show()
            return False
    
    def go_to_signUp(self):
        """
        changes from login window to signup window
        """
        self.close()
        signUp_window.show()

    def go_to_workspace(self):        
        """
        changes from login window to workspace window
        """
        if self.authorize_login():
            QTimer.singleShot(1000, self.close)
            workspace_window.title.setText(f"{self.username}'s WorkSpace")
            QTimer.singleShot(1000, workspace_window.show)
        else:
            return

######################
### Sign up window ###
######################

class SignUpWindow(RoundCornersWindow):


    def __init__(self, width, height, background_color):
        """
        Extends RoundCornersWindow with a custom
        user interface design
        Args:
        -width
        -height
        -background color
        """
        super().__init__(width, height, background_color)
        self.ui_design()

    def ui_design(self):
        
        # Title
        self.title = QLabel("Sign Up for free", self)
        self.title.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: white;
        """
        )
        self.title.setGeometry(300, 90, 480, 50)

        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """)
        self.close_button.setGeometry(self.width() - 37, 5, 30, 30)
        self.close_button.clicked.connect(self.close)

        # Maximize button
        self.maximize_button = QPushButton("❐", self)
        self.maximize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.maximize_button.setGeometry(self.width() - 67, 5, 30, 30)
        self.maximize_button.clicked.connect(self.showMaximized)

        # Minimize button
        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.minimize_button.setGeometry(self.width() - 97, 5, 20, 30)
        self.minimize_button.clicked.connect(self.showMinimized)

        # Name
        self.insert_name = QLineEdit(self)
        self.insert_name.setPlaceholderText("Name")
        self.insert_name.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px;
        """)
        self.insert_name.setGeometry(300, 180, 200, 42)

        # Surname
        self.insert_surname = QLineEdit(self)
        self.insert_surname.setPlaceholderText("Surname")
        self.insert_surname.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px;
        """
        )
        self.insert_surname.setGeometry(300, 230, 200, 42)
        

        # Username
        self.insert_username = QLineEdit(self)
        self.insert_username.setPlaceholderText("Username")
        self.insert_username.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px
        """
        )
        self.insert_username.setGeometry(300, 280, 230, 42)
        
        # Password
        self.insert_password = QLineEdit(self)
        self.insert_password.setPlaceholderText("Password")
        self.insert_password.setStyleSheet("""
            font-size: 17px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px;
        """
        )
        self.insert_password.setEchoMode(QLineEdit.Normal)
        self.insert_password.setGeometry(300, 330, 230, 42)

        # Toggle password
        self.toggle_password_button = QPushButton("🙉", self)
        self.toggle_password_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: Orchid;
                border-radius: 10px;
                color: white;
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px
            }
        """
        )
        self.toggle_password_button.clicked.connect(self.toggle_password)
        self.toggle_password_button.setGeometry(540, 335, 32, 32)

                        
        self.signUp_label = QLabel("", self)
        self.signUp_label.setGeometry(300, 440, 300, 22)
        self.signUp_label.hide()

        # Sign up button
        self.signUp_button = QPushButton("Sign Up", self)
        self.signUp_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.signUp_button.setGeometry(300, 390, 90, 30)
        self.signUp_button.clicked.connect(self.perform_registration)

        # "Go back to login" button
        self.login_button = QPushButton("Login", self)
        self.login_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """)
        self.login_button.setGeometry(400, 390, 90, 30)  
        self.login_button.clicked.connect(self.go_back_to_login)

        # Image
        image_label = QLabel(self)
        pixmap = QPixmap("monkey.png")
        image_label.setPixmap(pixmap)
        image_label.setGeometry(0, 330, pixmap.width(), pixmap.height())

    def perform_registration(self):
        name = self.insert_name.text()
        surname = self.insert_surname.text()
        username = self.insert_username.text()
        password = self.insert_password.text()

        if not name or not surname or not username or not password:
            self.signUp_label.setText("Please fill all the slots")
            self.signUp_label.setStyleSheet("""
                font-size: 14px;
                color: red;
            """)
            self.signUp_label.show()
        else:
            insert_user(name, surname, username, password)
            self.signUp_label.setText("Thank you for subscribing!")
            self.signUp_label.setStyleSheet("""
                font-size: 14px;
                color: LimeGreen;
            """)
            self.signUp_label.show()
            QTimer.singleShot(900, self.go_back_to_login)
        
    def toggle_password(self):
        if self.insert_password.echoMode() == QLineEdit.Password:
            self.insert_password.setEchoMode(QLineEdit.Normal)
            self.toggle_password_button.setText("🙉")
        else:
            self.insert_password.setEchoMode(QLineEdit.Password)
            self.toggle_password_button.setText("🙈")

    def go_back_to_login(self):
        """
        Closes the sign up window, sets all the entries
        of the QLineEdits back to "" and switches back to
        the login window
        """
        self.close()
        self.insert_name.setText("")
        self.insert_surname.setText("")
        self.insert_username.setText("")
        self.insert_password.setText("")
        self.signUp_label.setText("")
        login_window.show()


########################
### Workspace window ###
########################

class WorkspaceWindow(RoundCornersWindow):


    def __init__(self, width, height, background_color):
        """
        Extends RoundCornersWindow with an Empty title, to be
        formatted once the login is performed, a custom graphic
        interface, and the current_folder_path attribute with
        os.getcwd()
        """
        super().__init__(width, height, background_color)
        self.current_folder_path = os.getcwd()
        self.title_label = QLabel("", self)
        self.ui_design()
    
    def ui_design(self):

        # Title
        self.title = QLabel("", self)
        self.title.setStyleSheet("""
            font-size: 24px;
            color: white;
            font-weight: bold;
        """
        )
        self.title.setGeometry(500, 20, 800, 30)

        # Image 1
        image_label_1 = QLabel(self)
        pixmap_1 = QPixmap("monkey2.png")
        image_label_1.setPixmap(pixmap_1)
        image_label_1.setGeometry(1100, 110, pixmap_1.width(), pixmap_1.height())

        # Image 2
        image_label_2 = QLabel(self)
        pixmap_2 = QPixmap("monkey3.png")
        image_label_2.setPixmap(pixmap_2)
        image_label_2.setGeometry(370, 80, pixmap_2.width(), pixmap_2.height())

        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.close_button.setGeometry(self.width() - 37, 5, 30, 30)
        self.close_button.clicked.connect(self.close)

        # Maximize button
        self.maximize_button = QPushButton("❐", self)
        self.maximize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.maximize_button.setGeometry(self.width() - 67, 5, 30, 30)
        self.maximize_button.clicked.connect(self.showMaximized)

        # Minimize button
        self.minimize_button = QPushButton("—", self)
        self.minimize_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.minimize_button.setGeometry(self.width() - 97, 5, 20, 30)
        self.minimize_button.clicked.connect(self.showMinimized)

        # Query box
        self.input_query = QTextEdit(self)
        self.input_query.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_query.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_query.setPlaceholderText(
            "SELECT *\nFROM example\nWHERE ...\n"
            "or write what you want to retrieve in "
            "natural language and press \"Ask AI\" to "
            "get an SQL query.\n"
            "Remember to always check the queries before running them, "
            "AI can make mistakes"
        )
        self.input_query.setStyleSheet("""
            font-size: 20px;
            padding: 5px;
            background-color: MediumOrchid;
            border: none;
            border-radius: 10px;
        """
        )
        self.input_query.setGeometry(50, 500, 600, 400)

        # "Ask AI" button
        self.ask_ai_button = QPushButton("Ask AI", self)
        self.ask_ai_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: DarkOrchid;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.ask_ai_button.setGeometry(540, 470, 110, 25)
        self.ask_ai_button.clicked.connect(self.ask_ai)

        # "Excecute query" button
        self.execute_query_button = QPushButton("Excecute query", self)
        self.execute_query_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.execute_query_button.setGeometry(50, 920, 125, 30)
        self.execute_query_button.clicked.connect(self.execute_query_ui)

        # Clear button
        self.clear_button = QPushButton("Clear", self)
        self.clear_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: DarkOrchid;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.clear_button.setGeometry(185, 920, 75, 30)
        self.clear_button.clicked.connect(self.clear_query_editor)

        # Query label
        self.queryEditor_label = QLabel("SQL Query Editor", self)
        self.queryEditor_label.setStyleSheet("""
            font-size: 20px;
            color: white;
            font-weight: bold;
        """
        )
        self.queryEditor_label.setGeometry(50, 470, 300, 30)

        # Results table
        self.result_table = QTableWidget(self)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result_table.verticalHeader().setVisible(False)
        
        self.result_table.setStyleSheet("""
            QTableWidget {
                background-color: MediumOrchid;
                alternate-background-color: DarkOrchid;
                font-size: 15;
                color: white;
                border: none;
                gridline-color: Indigo;
                selection-background-color: LightCyan;
                selection-color: Levander;
                border: none;
                border-radius: 10px;
            }
            
            QHeaderView::section {
                background-color: DarkOrchid;
                color: white;
                font-weight: bold;
                padding: 5px;
                border-color: white    
            }
            
            QTableWidget::item {
                padding: 5px;                    
            }
            
        """
        )
        self.result_table.setGeometry(670, 500, 1000, 400)

        # "Clear result table" button
        self.clear_results_button = QPushButton("Clear Results", self)
        self.clear_results_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.clear_results_button.setGeometry(670, 920, 120, 30)
        self.clear_results_button.clicked.connect(self.clear_results)

        # Results label
        self.result_label = QLabel("Results", self)
        self.result_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 20px;
        """
        )
        self.result_label.setGeometry(670, 470, 100, 30)

        self.results_label_query = QLabel("", self)
        self.results_label_query.setGeometry(290, 925, 300, 20)
        self.results_label_query.setStyleSheet("""
            font-size: 14px;
            color: red;
        """
        )
        self.results_label_query.hide()

        # Query cronology
        self.query_cronology = QTextEdit(self)
        self.query_cronology.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.query_cronology.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.query_cronology.setReadOnly(False)
        self.query_cronology.setStyleSheet("""
            background-color: MediumOrchid;
            font-size: 13px;
            border: none;
            border-radius: 10px;
            padding: 5px;
        """
        )
        self.query_cronology.setGeometry(1420, 90, 250, 400)

        # Query cronology label
        self.query_cronology_label = QLabel("Cronology", self)
        self.query_cronology.setText("-"*46)
        self.query_cronology_label.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 15px;
        """
        )
        self.query_cronology_label.setGeometry(1420, 65, 100, 20)

        # Database & Tables Explorer
        self.db_tree = QTreeWidget(self)
        self.db_tree.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.db_tree.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.db_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.db_tree.setGeometry(50, 90, 300, 350)
        self.db_tree.setHeaderHidden(True)
        self.db_tree.setStyleSheet("""
            QTreeWidget {
                background-color: MediumOrchid;
                color: white;
                font-size: 15px;
                border: none;
                border-radius: 10px;
                padding: 5px;
            }
                                   
            QHeaderView::section{
                background-color: MediumOrchid;
                border: none;
                color: white;
                font-weight: bold;
            }
                                   
            QTreeWidget::item {
                padding: 5px;
            }
        """
        )

        self.populate_database_tree()

        # New database button
        self.newDB_button = QPushButton("New Database", self)
        self.newDB_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.newDB_button.setGeometry(370, 330, 130, 30)
        self.newDB_button.clicked.connect(self.addDB)
    
        # Delete table button
        self.delete_table_button = QPushButton("Delete table", self)
        self.delete_table_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: DarkOrchid;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.delete_table_button.setGeometry(370, 370, 130, 30)
        self.delete_table_button.clicked.connect(self.delete_table)

        # Delete database
        self.delete_db_button = QPushButton("Delete Database", self)
        self.delete_db_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.delete_db_button.setGeometry(370, 410, 130, 30)
        self.delete_db_button.clicked.connect(self.deleteDB)


        self.open_folder_button = QPushButton("Open Folder", self)
        self.open_folder_button.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                background-color: DarkOrchid;
                border-radius: 10px;
                color: white;
                border: 2px solid Fuchsia;
                font-weight: bold;                          
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.open_folder_button.setGeometry(50, 30, 100, 30)
        self.open_folder_button.clicked.connect(self.open_folder)
        
        # Button for json export
        self.export_to_json_button = QPushButton("Export to json", self)
        self.export_to_json_button.setStyleSheet("""
            QPushButton {
                font-size: 17px;
                background-color: DarkOrchid;
                border-radius: 10px;
                color: white;               
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.export_to_json_button.setGeometry(800, 920, 150, 30)
        self.export_to_json_button.clicked.connect(self.export_to_json)

    def populate_database_tree(self):
        """
        Populate the QTreeWidget with all .db files and their tables.

        This method scans the current working directory (or the user-selected folder),
        retrieves all SQLite database files, and adds each one as a top-level item
        in the tree view. For each database, it connects to it, queries the list of 
        tables, and adds those as child items under the corresponding database node.

        If a database cannot be accessed, the error is printed to the console.
        """
        self.db_tree.clear()
        db_paths = get_databases_in_folder(self.current_folder_path)
        
        for db_path in db_paths:
            db_name = os.path.basename(db_path)
            db_item = QTreeWidgetItem([db_name])
            db_item.setData(0, Qt.UserRole, db_path)
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT name
                    FROM sqlite_master
                    WHERE type='table';
                """
                )
                tables = cursor.fetchall()
                for table in tables:
                    table_name = table[0]
                    table_item = QTreeWidgetItem([table_name])
                    db_item.addChild(table_item)
                conn.close()
            except Exception as e:
                print(f"Error with {db_name}: {e}")
            
            self.db_tree.addTopLevelItem(db_item)

    def clear_results(self):
            
            self.result_table.clear()
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
            return

    def execute_query_ui(self):
        """
        This function exploits the cursor of sqlite3 to run queries on
        the selected database
        """
        selected_item = self.db_tree.selectedItems()    

        if not selected_item:
            self.results_label_query.setText("Please select the database you want to query")
            self.results_label_query.setStyleSheet("font-size: 14px; color: red;")
            self.results_label_query.show()
            return
        
        tree_item = selected_item[0]
        db_item = tree_item
        if tree_item.parent() is not None:
            self.results_label_query.setText("You must query a database --selected: table--")
            self.results_label_query.setStyleSheet("font-size: 14px; color: red;")
            self.results_label_query.show()
            return

        db_path = db_item.data(0, Qt.UserRole)
        if not db_path:
            self.results_label_query.setText("Path not found")
            self.results_label_query.setStyleSheet("font-size: 14px; color: red;")
            self.results_label_query.show()
            return
        
        query = self.input_query.toPlainText()
        if not query.strip():
            self.results_label_query.setText("Please insert an SQL query")
            self.results_label_query.setStyleSheet("font-size: 14px; color: red;")
            self.results_label_query.show()
            return
        
        try:
            results, columns = execute_query(db_path, query)
            self.result_table.clear()
            self.result_table.setRowCount(len(results))
            self.result_table.setColumnCount(len(columns))
            self.result_table.setHorizontalHeaderLabels(columns)

            header = self.result_table.horizontalHeader()
            header.setSectionResizeMode(QHeaderView.Stretch)

            for row_idx, row_data in enumerate(results):
                for col_idx, data in enumerate(row_data):
                    self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            
            self.results_label_query.setText("Query succesfully executed")
            self.results_label_query.setStyleSheet("font-size: 14px; color: LimeGreen;")            
        except Exception as e:
            self.results_label_query.setText(f"Error: {e}")
            self.results_label_query.setStyleSheet("font-size: 14px; color: Red;")
            self.result_table.setRowCount(0)
            self.result_table.setColumnCount(0)
        finally:
            self.populate_database_tree()
            current_cronology = self.query_cronology.toPlainText()
            current_query = self.input_query.toPlainText()
            spacer = "-"*46
            if self.query_cronology.toPlainText() == "":
                self.query_cronology.setText(current_query)
            else:
                self.query_cronology.setText(spacer + "\n" + current_query + "\n" + current_cronology)
    
    def open_folder(self):
        """
        This method opens the folder selected by the user
        """
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder", self.current_folder_path)
        if folder_selected:
            self.current_folder_path = folder_selected
            self.populate_database_tree()

    def clear_query_editor(self):
        self.input_query.setText("")

    def delete_table(self):
        self.delete_table_window = DeleteTableWindow(500, 200, "DarkOrchid")
        self.delete_table_window.show()
            
    def addDB(self):
        self.addDB_window = AddDBWindow(260, 200, "DarkOrchid")
        self.addDB_window.show()

    def deleteDB(self):
        self.deleteDB_window = DeleteDBWindow(600, 200, "DarkOrchid")
        self.deleteDB_window.show()

    def export_to_json(self):
        """
        Export the current query results from the result table to a JSON file.

        The method retrieves the data currently displayed in the QTableWidget,
        converts it into a list of dictionaries (one dictionary per row),
        and allows the user to choose a destination path with a save dialog.
        The results are then written to the chosen file in JSON format.

        If there are no results in the table, a warning message is shown instead.
        Feedback on success or failure is displayed to the user through a label.
        """
        
        rows_number = self.result_table.rowCount()
        columns_number = self.result_table.columnCount()

        if rows_number == 0:
            self.results_label_query.setText("No result to export")
            self.results_label_query.setStyleSheet("font-size: 14px; color: Red;")
            self.results_label_query.show()
            return
        
        columns = [self.result_table.horizontalHeaderItem(i).text() for i in range(columns_number)]
        data = []
        
        for row in range(rows_number):
            row_data = {}        
            for column in range(columns_number):
                item = self.result_table.item(row, column)
                if item is not None:
                    row_data[columns[column]] = item.text()
                else:
                    row_data[columns[column]] = None
            data.append(row_data)        
        # Save the file
        file_name, ph = QFileDialog.getSaveFileName(self, "Save Query Results", "",
                                                     "JSON Files (* .json);;All Files (*)")
        if file_name is not None:
            try:
                with open(file_name, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
                self.results_label_query.setText(f"Results Succesfully exported in: {os.path.basename(file_name)}")
                self.results_label_query.setStyleSheet("font-size: 14px; color: LimeGreen;")
                self.results_label_query.show()            
            except Exception as e:
                self.results_label_query.setText("Error in exporting the file: {e}")
                self.results_label_query.setStyleSheet("font-size: 14px; color: red;")
                self.results_label_query.show()

    def ask_ai(self):
        """
        Sends the input (written in the SQLite query port) to a NLP
        model to obtain a SQL query
        """
        try:
            text = self.input_query.toPlainText()
            
            if text != "":
                self.setCursor(Qt.WaitCursor)
                sql_query = query_from_nl_to_sql(text)
                self.input_query.setPlainText(sql_query)
            else:
                self.results_label_query.setText("Error, enter a valiud input")
                self.results_label_query.setStyleSheet("font-size: 14px; color: Red;")
                self.results_label_query.show()
        
        except Exception as e:
            self.results_label_query.setText(f"Error: {e}")
            return False
        finally:
            self.setCursor(Qt.ArrowCursor)
            

#################################################
### Pop-up window for creating a new database ###
#################################################


class AddDBWindow(RoundCornersWindow):
    """
    pop up window that opens when an add database operarion
    has to be performed
    """


    def __init__(self, width, height, background_color):
        super().__init__(width, height, background_color)
        self.ui_design()
    
    def ui_design(self):
        self.title = QLabel("New Database", self)
        self.title.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        self.title.setGeometry(10, -15, 160, 100)

        self.name = QLineEdit(self)
        self.name.setPlaceholderText("Name")
        self.name.setStyleSheet("""
            background-color: MediumOrchid;
            border: none;
            border-radius: 15px;
            color: white;            
        """
        )
        self.name.setGeometry(10, 60, 170, 40)
    
        self.create = QPushButton("Create", self)
        self.create.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.create.setGeometry(10, 115, 60, 30)
        self.create.clicked.connect(self.addDB)

        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.close_button.setGeometry(self.width() - 32, 0, 30, 30)
        self.close_button.clicked.connect(self.close)

        self.back_button = QPushButton("back", self)
        self.back_button.setStyleSheet("""QPushButton {
                font-size: 15px;
                background-color: Purple;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.back_button.setGeometry(100, 115, 60, 30)
        self.back_button.clicked.connect(self.close)

        self.result_label = QLabel("test", self)
        self.result_label.setGeometry(10, 150, 300, 17)
        self.result_label.hide()
        
    def addDB(self):
        name = self.name.text()
        if not name:
            self.result_label.setText("Error: the new db must be named")
            self.result_label.setStyleSheet("font-size: 14px; color: Red;")
            self.result_label.show()
            return        
        # Construct the full path
        db_full_path = os.path.join(workspace_window.current_folder_path, f"{name}.db")
        try:
            create_database(db_full_path.replace(".db", ""))
            workspace_window.populate_database_tree()
            self.result_label.setText(f"Database {name}.db created succesfully")
            self.result_label.setStyleSheet("font-size: 14px; color: LimeGreen;")
            self.result_label.show()
            QTimer.singleShot(1500, self.close)
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            self.result_label.setStyleSheet("font-size: 14px; color: Red;")
            self.result_label.show()


##########################################
### Pop-up window for deleting a table ###
##########################################

class DeleteTableWindow(RoundCornersWindow):
    """
    pop up window that pops up when a table has to be deleted
    with the button
    """

    def __init__(self, width, height, background_color):
        super().__init__(width, height, background_color)
        self.ui_design()
    
    def ui_design(self):

        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.close_button.setGeometry(self.width() - 32, 0, 30, 30)
        self.close_button.clicked.connect(self.close)

        self.title = QLabel("DELETE TABLE", self)
        self.title.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        self.title.setGeometry(15, -25, 160, 100)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setStyleSheet("""QPushButton {
                font-size: 15px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.delete_button.setGeometry(15, 130, 90, 25)
        self.delete_button.clicked.connect(self.delete)

        if len(workspace_window.db_tree.selectedItems()) > 0:
            self.item = workspace_window.db_tree.selectedItems()[0]
            if self.item.parent():
                self.db_item = self.item.parent()
                self.db_path = self.db_item.data(0, Qt.UserRole)
                self.table_name = self.item.text(0)
            else:     
                # If the selected item is a database
                self.db_item = None
                self.db_path = None
                self.table_name = None
        else:
            self.db_item = None
            self.db_path = None
            self.table_name = None

        if not self.db_path or not self.table_name:
            self.label = QLabel("No valid table has been selected", self)
            self.label.setStyleSheet("font-size: 16px; color: red; font-weight: bold;")
            self.label.setGeometry(15, 45, 400, 20)
            self.second_label = QLabel("", self)
            self.delete_button.setEnabled(False)
        else:
            self.label = QLabel(f"Are you sure to delete the table \"{self.table_name}\"?", self)
            self.label.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
            self.label.setGeometry(15, 45, 400, 20)
            self.second_label = QLabel("The operation is not reversible", self)
            self.second_label.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
            self.second_label.setGeometry(15, 75, 400, 20)
            self.delete_button.setEnabled(True)            
            
        self.back_button = QPushButton("back", self)
        self.back_button.setStyleSheet("""QPushButton {
                font-size: 15px;
                background-color: Purple;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.back_button.setGeometry(120, 130, 90, 25)
        self.back_button.clicked.connect(self.close)

        self.result_label = QLabel("", self)
        self.result_label.setGeometry(20, 170, 500, 15)

    def delete(self):
        """
        deletes a table from the selected database
        """
        try:
            delete_table(str(self.table_name), self.db_path)
            self.result_label.setText(f"Table {self.table_name} deleted successfully!")
            self.result_label.setStyleSheet("font-size: 14px; color: LimeGreen;")
        except Exception as e:
            self.result_label.setText(f"Error in the deletion: {e}")
            self.result_label.setStyleSheet("font-size: 14px; color: Red;")
        finally:
            workspace_window.populate_database_tree()
            QTimer.singleShot(1500, self.close)
            

#############################################
### Pop-up window for deleting a database ###
#############################################


class DeleteDBWindow(RoundCornersWindow):
    """
    pop up window that pops up when the deletion of database
    is performed
    """

    def __init__(self, width, height, background_color):
        super().__init__(width, height, background_color)
        self.ui_design()
    
    def ui_design(self):
        # Close button
        self.close_button = QPushButton("✕", self)
        self.close_button.setStyleSheet("""
            background-color: transparent;
            font-size: 19px;
            border: none;
            color: white;
            font-weight: bold;
        """
        )
        self.close_button.setGeometry(self.width() - 32, 0, 30, 30)
        self.close_button.clicked.connect(self.close)

        self.title = QLabel("DELETE DATABASE", self)
        self.title.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        self.title.setGeometry(15, -25, 160, 100)

        if len(workspace_window.db_tree.selectedItems()) > 0:
            items = workspace_window.db_tree.selectedItems()[0]
            self.db_name_str = items.text(0)
        else:
            self.db_name_str = ""
        
        self.label = QLabel(f"Are you sure to delete the database \"{self.db_name_str}\"?", self)
        self.label.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        self.label.setGeometry(15, 45, 600, 20)

        self.second_label = QLabel("The operation is not reversible (you might lose all your data)", self)
        self.second_label.setStyleSheet("font-size: 16px; color: white; font-weight: bold;")
        self.second_label.setGeometry(15, 75, 600, 20)

        self.delete_button = QPushButton("Delete", self)
        self.delete_button.setStyleSheet("""QPushButton {
                font-size: 15px;
                background-color: MediumVioletRed;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.delete_button.setGeometry(15, 130, 90, 25)
        self.delete_button.clicked.connect(self.delete_db)

        self.back_button = QPushButton("back", self)
        self.back_button.setStyleSheet("""QPushButton {
                font-size: 15px;
                background-color: Purple;
                border-radius: 10px;
                color: white;
                font-weight: bold;     
            }
            
            QPushButton:pressed {
                background-color: #a0d8d8;
                padding-left: 5px;
                padding-top: 5px;
            }
        """
        )
        self.back_button.setGeometry(120, 130, 90, 25)
        self.back_button.clicked.connect(self.close)

        self.result_label = QLabel("", self)
        self.result_label.hide()
        self.result_label.setGeometry(20, 170, 300, 15)

    def delete_db(self):
        """
        deletes a database given his path and updates
        the result label
        """
        try:
            selected_item = workspace_window.db_tree.selectedItems()[0]
            if not selected_item:
                self.result_label.setText("Select the database you want to remove")
                self.result_label.setStyleSheet("font-size: 14px; color: red;")
                return
            db_path = selected_item.data(0, Qt.UserRole)
            delete_database(db_path)
            self.result_label.setText("Database succesfully deleted")
            self.result_label.setStyleSheet("font-size: 14px; color: LimeGreen;")
            self.result_label.show()
            workspace_window.populate_database_tree()
            QTimer.singleShot(1500, self.close)
        except Exception as e:
            self.result_label.setText(f"Error: {e}")
            self.result_label.setStyleSheet("font-size: 14px; color: red;")
            self.result_label.show()

app = QApplication(sys.argv)
login_window = LoginWindow(800, 600, "Purple")
signUp_window = SignUpWindow(800, 600, "Purple")
workspace_window = WorkspaceWindow(1700, 1000, "Purple")

create_users_database()

if __name__ == "__main__":

    login_window.show()
    sys.exit(app.exec_())