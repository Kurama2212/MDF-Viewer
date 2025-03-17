import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QDoubleSpinBox, QTableView, QFileDialog, QWidget, QLabel
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from asammdf import MDF
from plot import plot_line

# Modello per la tabella
class PandasModel(QAbstractTableModel):
    def __init__(self, df):
        super().__init__()
        self._df = df

    def data(self, index, role = Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._df.iloc[index.row(), index.column()])
        return None

    def rowCount(self, _):
        return self._df.shape[0]

    def columnCount(self, _):
        return self._df.shape[1]

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            if orientation == Qt.Vertical:
                return str(self._df.index[section])
        return None

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tabella file MDF")
        self.setGeometry(100, 100, 1000, 400)

        self.double_spin = QDoubleSpinBox()
        self.double_spin.setMinimum(0.001)
        self.double_spin.setMaximum(0.1)
        self.double_spin.setDecimals(3)
        self.double_spin.setSingleStep(0.001)

        self.label = QLabel('Raster')
        self.tabella = QTableView()
        self.button = QPushButton('carica MDF')
        self.button.clicked.connect(lambda: self.caricaMDF(self.double_spin.value()))

        self.plot_button = QPushButton('Plot Column')
        self.plot_button.clicked.connect(self.enable_column_selection)
        
        self.plot_view = QWebEngineView()
        self.plot_view.setMinimumHeight(300)
        
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.double_spin)
        layout.addWidget(self.button)
        layout.addWidget(self.plot_button)
        layout.addWidget(self.plot_view)
        layout.addWidget(self.tabella)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.column_selection_enabled = False

    def caricaMDF(self, raster):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open file', '', 'MDF Files (*.mf4)')
        if file_path:
            self.df = MDF(file_path).to_dataframe(raster=raster)
            self.modello = PandasModel(self.df)
            self.tabella.setModel(self.modello)

    def enable_column_selection(self):
        self.column_selection_enabled = True
        self.tabella.clicked.connect(self.handle_column_selection)

    def handle_column_selection(self, index):
        if self.column_selection_enabled:
            try:
                column_name = self.df.columns[index.column()]
                print(f"Colonna selezionata: {column_name}")
                html_content = plot_line(self.df, column_name)
                self.plot_view.setHtml(html_content, baseUrl=QUrl("file://"))
                print("Grafico caricato nel QWebEngineView.")
            except Exception as e:
                print(f"Errore nel generare il grafico: {e}")
            finally:
                self.column_selection_enabled = False
                self.tabella.clicked.disconnect(self.handle_column_selection)

# Applicazione
app = QApplication(sys.argv)

# Finestra principale
finestra = MainWindow()
finestra.show()

sys.exit(app.exec_())