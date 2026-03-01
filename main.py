import sys, json, os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase
from PyQt5 import QtGui
import requests

gamesURLList = {}
lastLibrary = ""

if os.path.exists("libraries/"):
    for file in os.listdir("libraries/"):
        if file.endswith('.json'):
            with open(os.path.join("libraries/", file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                gamesURLList[file.replace('.json', '')] = data

class Splash(QWidget):
    def __init__(self):
        super().__init__()
        self.main_window = None
        self.initUI()

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        pixmap = QPixmap('resources/splash.png')
        self.setFixedSize(pixmap.size())
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.splashImage = QLabel(self)
        self.splashImage.setPixmap(pixmap)
        self.splashImage.setScaledContents(True)
        layout.addWidget(self.splashImage)
        self.setLayout(layout)
        self.center()
        self.timer = QTimer()
        self.timer.timeout.connect(self.close_splash)
        self.timer.start(3000)

    def close_splash(self):
        self.timer.stop()
        self.hide()
        if self.main_window is None:
            self.main_window = Games()
        self.main_window.show()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

class DownloadGames(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Turbo Launcher / Меню")
        self.resize(400, 300)
        
        font_id = QFontDatabase.addApplicationFont('resources/fonts/Geologica.ttf')
        if font_id != -1:
            QApplication.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 10))
        
        self.setStyleSheet("QWidget{background-color:black;color:white} QPushButton{font-size:14px;color:black;border:2px solid gray;border-radius:15px;background-color:white;padding:5px 15px}")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.current_library = {}
        self.gamesList = QListWidget()
        
        try:
            req = requests.get("https://raw.githubusercontent.com/stepaandgddev/TurboLauncherGamesLists/refs/heads/main/Mains.json", timeout=10)
            if req.status_code == 200 and req.text.strip():
                try:
                    self.current_library = req.json()
                    for game_id, game_data in self.current_library.items():
                        if "name" in game_data:
                            self.gamesList.addItem(game_data["name"])
                except json.JSONDecodeError as e:
                    QMessageBox.critical(self, "Ошибка JSON", 
                                       f"Файл списка игр содержит ошибку:\n{str(e)}\n\n"
                                       f"Пожалуйста, сообщите разработчику.")
                    print(f"JSON Error at position {e.pos}: {e.doc[max(0, e.pos-50):e.pos+50]}")
            else:
                QMessageBox.warning(self, "Ошибка", 
                                   f"Не удалось загрузить список игр. Код ответа: {req.status_code}")
        except requests.RequestException as e:
            QMessageBox.critical(self, "Ошибка подключения", 
                               f"Не удалось подключиться к серверу:\n{str(e)}")
        
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)

        downloadButton = QPushButton("Скачать игру")
        downloadButton.setStyleSheet("QPushButton{font-size:12px;font-weight:bold;color:#03440E;border:3px solid #03440E;border-radius:15px;background-color:#63F87C;padding:5px 15px}")
        downloadButton.clicked.connect(self.download_game)

        infoButton = QPushButton("О игре")
        infoButton.clicked.connect(self.gameInfo)

        top_layout.addWidget(downloadButton)
        top_layout.addWidget(infoButton)
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.gamesList)
        self.setLayout(main_layout)
        self.center()

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))
    
    def gameInfo(self):
        item = self.gamesList.currentItem()
        if item and self.current_library:
            game_name = item.text()
            
            for game_id, game_data in self.current_library.items():
                if game_data["name"] == game_name:
                    QMessageBox.information(self, "О игре", f"Название: {game_name}\nОписание: {game_data['description']}\nURL: {game_data['url']}")
                    break
    


    def download_game(self):
        item = self.gamesList.currentItem()
        if item and self.current_library:
            game_name = item.text()

            for game_id, game_data in self.current_library.items():
                if game_data["name"] == game_name:
                    from PyQt5.QtCore import QUrl
                    from PyQt5.QtGui import QDesktopServices

                    url_string = game_data["url"]

                    reply = QMessageBox.question(self, "Подтверждение", 
                                               f"Открыть {url_string}?")
                    if reply == QMessageBox.Yes:
                        QDesktopServices.openUrl(QUrl(url_string))

                    
                    break

class AddGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))
        self.initUI()
        self.gamePath = ""

    def initUI(self):
        self.setWindowTitle("Turbo Launcher / Добавить игру")
        self.resize(400, 300)
        
        font_id = QFontDatabase.addApplicationFont('resources/fonts/Geologica.ttf')
        if font_id != -1:
            QApplication.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 10))
        
        self.setStyleSheet("QWidget{background-color:black;color:white} QPushButton{font-size:14px;color:black;border:2px solid gray;border-radius:15px;background-color:white;padding:5px 15px}")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.current_library = {}

        #self.gamesList.currentItemChanged.connect(self.on_game_selected)


        header = QLabel("Добавить игру")
        header.setStyleSheet("font-size: 16px;")


        addGameButton = QPushButton("Добавить игру")
        addGameButton.clicked.connect(self.addGame)


        gameNameField = QLineEdit()
        gameNameField.setPlaceholderText("Название игры")
        

        self.descriptionField = QLineEdit()
        self.descriptionField.setPlaceholderText("Описание игры")

        selectButton = QPushButton("Выбрать программу")
        selectButton.clicked.connect(self.selectGame)

        main_layout.addWidget(header)
        main_layout.addWidget(gameNameField)
        main_layout.addWidget(self.descriptionField)
        main_layout.addWidget(gameNameField)
        main_layout.addWidget(selectButton)
        main_layout.addWidget(addGameButton)

        self.setLayout(main_layout)
        self.center()
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))
    
    def addGame(self):
        game_name = self.findChild(QLineEdit).text()
        if not game_name or not self.gamePath:
            QMessageBox.warning(self, "Ошибка", "Напишите название игры и выберите файл")
            return
            
        try:
            with open(lastLibrary, 'r', encoding='utf-8') as file:
                file_data = json.load(file)
            
            gamedata = {
                "url": self.gamePath,
                "desc": self.descriptionField.text()
            }

            file_data["games"][game_name] = gamedata

            with open(lastLibrary, 'w', encoding='utf-8') as file:
                json.dump(file_data, file, indent=4, ensure_ascii=False)
            
            QMessageBox.information(self, "Успех", "Игра успешно добавлена!\nДля применения изменений, перезапустите лаунчер.")
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось добавить игру: {str(e)}")
    
    def selectGame(self):
        self.gamePath, _ = QFileDialog.getOpenFileName(
            None,
            "Выбери программу",
            "",
            "Файл (*)"
        )

class AddGameLib(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))
        self.initUI()
        self.gamePath = ""

    def initUI(self):
        self.setWindowTitle("Turbo Launcher / Добавить игру")
        self.resize(400, 300)
        
        font_id = QFontDatabase.addApplicationFont('resources/fonts/Geologica.ttf')
        if font_id != -1:
            QApplication.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 10))
        
        self.setStyleSheet("QWidget{background-color:black;color:white} QPushButton{font-size:14px;color:black;border:2px solid gray;border-radius:15px;background-color:white;padding:5px 15px}")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.current_library = {}


        header = QLabel("Добавить библеотеку")
        header.setStyleSheet("font-size: 16px;")


        addLibButton = QPushButton("Добавить библеотеку")
        addLibButton.clicked.connect(self.addLib)


        self.libNameField = QLineEdit()
        self.libNameField.setPlaceholderText("Название библеотеки")

        self.libIDField = QLineEdit()
        self.libIDField.setPlaceholderText("Айди библеотеки")
        

        self.descriptionField = QLineEdit()
        self.descriptionField.setPlaceholderText("Описание игры")


        main_layout.addWidget(header)
        main_layout.addWidget(self.libNameField)
        main_layout.addWidget(self.descriptionField)
        main_layout.addWidget(self.libIDField)
        main_layout.addWidget(addLibButton)

        self.setLayout(main_layout)
        self.center()
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))
    
    def addLib(self):
        if not self.libNameField.text() or not self.libIDField.text() or not self.descriptionField.text():
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
        else:
            try:
                libdata = {
                    "name": self.libNameField.text(),
                    "desc": self.descriptionField.text(),
                    "games": {}
                }

                with open(f"libraries/{self.libIDField.text()}.json", 'w', encoding='utf-8') as file:
                    json.dump(libdata, file, indent=4, ensure_ascii=False)
                
                QMessageBox.information(self, "Успех", "Библеотека успешно добавлена!\nДля применения изменений, перезапустите лаунчер.")
                self.close()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось добавить библеотеку: {str(e)}")
    

class Games(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QtGui.QIcon('resources/icon.png'))
        self.gamesList = None
        self.gameDownload = None
        self.current_library = None
        self.addGame = None
        self.addLib = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Turbo Launcher / Игры")
        self.resize(400, 300)
        
        font_id = QFontDatabase.addApplicationFont('resources/fonts/Geologica.ttf')
        if font_id != -1:
            QApplication.setFont(QFont(QFontDatabase.applicationFontFamilies(font_id)[0], 10))
        
        self.setStyleSheet("QWidget{background-color:black;color:white} QPushButton{font-size:14px;color:black;border:2px solid gray;border-radius:15px;background-color:white;padding:5px 15px}")
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        self.gamesList = QListWidget()
        self.gamesList.currentItemChanged.connect(self.on_game_selected)
        
        self.combobox = QComboBox()
        self.combobox.currentIndexChanged.connect(self.refreshGames)
        for lib in gamesURLList.values():
            self.combobox.addItem(lib["name"])
        
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignCenter)

        consoleButton = QPushButton("Console mode")
        # consoleButton.clicked.connect(self.consoleMode)

        addGameButton = QPushButton("Новая игра...")
        addGameButton.clicked.connect(self.addGameOpen)

        addLibraryButton = QPushButton("Новая библеотека...")
        addLibraryButton.clicked.connect(self.addLibrary)

        downloadButton = QPushButton("Библеотека игр")
        downloadButton.setStyleSheet("QPushButton{font-size:14px;font-weight:bold;color:#03440E;border:3px solid #03440E;border-radius:15px;background-color:#63F87C;padding:5px 15px}")
        downloadButton.clicked.connect(self.gamesLibrary)

        top_layout.addWidget(consoleButton)
        top_layout.addWidget(addGameButton)
        top_layout.addWidget(downloadButton)
        
        runButton = QPushButton("Запустить")
        runButton.setStyleSheet("QPushButton{font-size:14px;font-weight:bold;color:#03440E;border:3px solid #03440E;border-radius:15px;background-color:#63F87C;padding:5px 15px}")
        runButton.clicked.connect(self.runGame)

        
        infoButton = QPushButton("О игре")
        infoButton.clicked.connect(self.gameInfo)

        infoLibButton = QPushButton("О библеотеке")
        infoLibButton.clicked.connect(self.libInfo)
        
        bottom_layout = QHBoxLayout()
        bottom_layout.setAlignment(Qt.AlignRight)
        bottom_layout.addWidget(runButton)
        bottom_layout.addWidget(infoButton)
        bottom_layout.addWidget(infoLibButton)
        bottom_layout.addWidget(addLibraryButton)
        bottom_layout.addWidget(self.combobox)
        
        
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.gamesList)
        main_layout.addLayout(bottom_layout)
        self.setLayout(main_layout)
        self.center()
        
        if self.combobox.count() > 0:
            self.combobox.setCurrentIndex(0)

    def on_game_selected(self, current, previous):
        if current and self.current_library:
            print(f"Выбрана: {current.text()}")

    def gameInfo(self):
        item = self.gamesList.currentItem()
        if item and self.current_library:
            game = self.current_library["games"][item.text()]
            QMessageBox.information(self, "О игре", f"Название: {item.text()}\nОписание: {game['desc']}\nПуть: {game['url']}")
    
    def libInfo(self):
        name = self.combobox.currentText()
        for lib in gamesURLList.values():
            if lib["name"] == name:
                QMessageBox.information(self, "О игре", f"Название: {name}\nОписание: {lib["description"]}")
    
    def libInfo(self):
        name = self.combobox.currentText()
        for lib in gamesURLList.values():
            if lib["name"] == name:
                QMessageBox.information(self, "О игре", f"Название: {name}\nОписание: {lib["description"]}")

    def runGame(self):
        item = self.gamesList.currentItem()
        if item and self.current_library:
            game_name = item.text()
            path = self.current_library["games"][game_name]["url"]
            
            if os.path.exists(path):
                os.startfile(path)
            else:
                reply = QMessageBox.question(
                    self, 
                    "Ошибка", 
                    f"Игра '{game_name}' не найдена по пути:\n{path}\n\nВы хотите удалить ярлык этой игры из лаунчера?",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    try:
                        current_lib_name = None
                        for lib_key, lib_data in gamesURLList.items():
                            if lib_data == self.current_library:
                                current_lib_name = lib_key
                                break
                        
                        if current_lib_name:
                            lib_path = os.path.join("libraries", f"{current_lib_name}.json")

                            with open(lib_path, 'r', encoding='utf-8') as file:
                                file_data = json.load(file)

                            if game_name in file_data["games"]:
                                del file_data["games"][game_name]

                                with open(lib_path, 'w', encoding='utf-8') as file:
                                    json.dump(file_data, file, indent=4, ensure_ascii=False)

                                gamesURLList[current_lib_name] = file_data

                                self.current_library = file_data

                                self.gamesList.takeItem(self.gamesList.row(item))
                                
                                QMessageBox.information(
                                    self, 
                                    "Успех", 
                                    f"Игра '{game_name}' удалена из библиотеки."
                                )
                        else:
                            QMessageBox.warning(self, "Ошибка", "Не удалось определить файл библиотеки")
                            
                    except Exception as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось удалить игру: {str(e)}")

    
    def gamesLibrary(self):
        if self.gameDownload is None:
            self.gameDownload = DownloadGames()
        self.gameDownload.show()
    
    def addGameOpen(self):
        if self.addGame is None:
            self.addGame = AddGame()
        self.addGame.show()
    
    def addLibrary(self):
        if self.addLib is None:
            self.addLib = AddGameLib()
        self.addLib.show()

    def refreshGames(self, index):
        name = self.combobox.currentText()
        for lib_key, lib_data in gamesURLList.items():
            if lib_data["name"] == name:
                self.current_library = lib_data
                global lastLibrary
                lastLibrary = "libraries/" + lib_key + ".json"
                self.gamesList.clear()
                for game in lib_data["games"]:
                    self.gamesList.addItem(QListWidgetItem(game))
                break

    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(int((screen.width() - self.width()) / 2), int((screen.height() - self.height()) / 2))

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    splash = Splash()
    splash.show()
    sys.exit(app.exec_())