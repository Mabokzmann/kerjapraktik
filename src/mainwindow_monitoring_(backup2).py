# Impor modul-modul yang dibutuhkan
from PyQt5.QtCore import QTimer, QDate, QTime, QThread, pyqtSignal
from PyQt5 import QtWidgets, uic, QtCore, QtGui
from PyQt5.QtWidgets import *
from datetime import datetime, timedelta
from time import sleep, perf_counter
import mysql.connector as sqlc
from math import ceil
import sys, csv, os

# Instance untuk database
host_ = "192.168.1.5"
user_ = "greenhouse"
password_ = "greenhouse"
database_ = "greenhouse"

class Monitoring(QMainWindow):
    """Class untuk membuka window utama monitoring daya."""

    def __init__(self):
        super(Monitoring, self).__init__()

        # Muat file ui
        uic.loadUi("D:\\Undip\\Kerja Praktek\\Prototype PyQt5\\Prototype.Monitoring\\Main_window.monitoring.ui", self)

        # Atur ukuran window agar tetap
        self.setFixedSize(1120, 717)

        # Panggil label value yang dimonitor
        self.label_val1 = self.findChild(QLabel, "val1")   #Tegangan PV
        self.label_val2 = self.findChild(QLabel, "val1_2") #Tegangan VAWT
        self.label_val3 = self.findChild(QLabel, "val1_3") #Arus PV
        self.label_val4 = self.findChild(QLabel, "val1_4") #Daya PV
        self.label_val5 = self.findChild(QLabel, "val1_5") #Anemometer
        self.label_val6 = self.findChild(QLabel, "val1_6") #Arus VAWT
        self.label_val7 = self.findChild(QLabel, "val1_7") #Daya VAWT
        self.label_val8 = self.findChild(QLabel, "val1_8") #Tegangan Baterai

        # Panggil label tanggal dan jam
        self.label_date = self.findChild(QLabel, "label_date")
        self.label_time = self.findChild(QLabel, "label_time")

        # Atur timer untuk teks tanggal dan jam
        self.label_date.setText("2020-03-01")
        self.label_time.setText("13:59:35")
        self.timer_ = QTimer()
        self.timer_.timeout.connect(self.showDateTime)
        self.timer_.start(1000)

        # Panggil menu bar data dan sambungkan ke class Download dan Show
        self.download = self.findChild(QAction, "actionDownload_data_2")
        self.show_data = self.findChild(QAction, "actionShow_data_2")
        self.download.triggered.connect(self.download_)
        self.show_data.triggered.connect(self.show_)

        # Panggil menu exit
        self.exit = self.findChild(QAction, "actionExit")
        self.exit.triggered.connect(self.exit_) #Tutup aplikasi dari menu Bar

        # Panggil proses pengambilan data real time
        self.display = Fetch_Monitor()
        self.display.fetch.connect(self.display_monitor)
        self.display.start() 

        # Tampilkan window
        self.show()

    # Tampilkan data di label monitoring
    def display_monitor(self, display):
        self.label_val1.setText(str(display[2]) + " V")
        self.label_val2.setText(str(display[5]) + " V")
        self.label_val3.setText(str(display[3]) + " A")
        self.label_val4.setText(str(display[4]) + " W")
        self.label_val5.setText(str(display[8]) + " m/s")
        self.label_val6.setText(str(display[6]) + " A")
        self.label_val7.setText(str(display[7]) + " W")
        self.label_val8.setText(str(display[9]) + " V")

    # Atur tampilan tanggal dan waktu
    def showDateTime(self):
        date = QDate.currentDate()
        time = QTime.currentTime()
        dateDisplay=date.toString('yyyy-MM-dd')
        timeDisplay=time.toString('hh:mm:ss')
        self.label_date.setText(dateDisplay)
        self.label_time.setText(timeDisplay)
    
    # Buka window untuk menampilkan data
    def show_(self):
        self._show = ShowData()

    # Buka window untuk mengunduh data
    def download_(self):
        self._download = DownloadData()

    # Tutup window monitoring daya
    def exit_(self):
        self.close()



class Fetch_Monitor(QThread):
    """Class untuk menyimpan proses pengambilan data untuk dimonitor."""

    # Buat sinyal untuk pengambilan data
    fetch = pyqtSignal(tuple)

    def __init__(self):
        super().__init__()
    
    def run(self):

        # Loop pengambilan data
        while True:
            try:
                # Bangun koneksi ke database SQL 
                db = sqlc.connect(
                    host = host_,
                    user = user_,
                    password = password_,
                    database = database_
                ) 
                cursor = db.cursor()
                cursor.execute('SELECT * FROM monitoring_daya ORDER BY timestamp DESC LIMIT 1')
                # Hubungkan sinyal untuk mengambil data dari database SQL
                self.fetch.emit(cursor.fetchall()[0])

            except Exception as e:

                # Tampilkan error di console jika
                # koneksi tidak bisa dibangun.
                print(e)

                # Jika koneksi tidak bisa dibangun,
                # tampilkan nilai 0 di aplikasi monitoring.
                a = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
                self.fetch.emit(a) # Hubungkan sinyal
            sleep(0.5)



class Download(QThread):
    """Class untuk menyimpan proses pengunduhan data 
    ke bentuk file .csv."""

    # Inisialisasi sinyal
    num_download = pyqtSignal(int)
    iter_download = pyqtSignal(int)
    time_remaining = pyqtSignal(float)
    filepath = pyqtSignal(str)
    success_download = pyqtSignal()

    # Bangun objek untuk class Download
    def __init__(self, path, startdate, enddate):
        super().__init__()
        self.path = path
        self.startdate = startdate
        self.enddate = enddate

    # Proses pembuatan file .csv ke direktori komputer
    def run(self):
        num = 5000 # Inisialiasi iterasi

        # Bangun koneksi ke database SQL
        db = sqlc.connect(
            host = host_,
            user = user_,
            password = password_,
            database = database_
        )
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) "\
                       "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                       "ORDER BY id ASC" % (self.startdate, self.enddate))

        num_data = cursor.fetchall()[0][0]
        iter_data = ceil(num_data/num)
        self.num_download.emit(iter_data) 

        # Nama kolom di file .csv yang akan didonlot
        column = ["Timestamp", "PV Voltage (Volt)", "PV Current (Ampere)", "PV Power (Watt)",\
                    "VAWT Voltage (Volt)", "VAWT Current (Ampere)", "VAWT Power (Watt)", "Anemometer (m/s)",\
                    "Battery Voltage (Volt)"]

        # Mulai pengunduhan
        with open(r"%s\Data Greenhouse %s to %s.csv" % (self.path, self.startdate, self.enddate), mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(column)
            self.filepath.emit(os.path.abspath(file.name))
            iter_time = 0
            for iter in range(iter_data):
                time_start = perf_counter()
                if self.isInterruptionRequested():
                    break
                start = iter*num
                end = (iter+1)*num-1 if iter != iter_data-1 else num_data
                cursor.execute("SELECT timestamp, v_pv, i_pv, p_pv, v_vawt, i_vawt, p_vawt, anemo, v_bat "\
                            "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                            "ORDER BY id ASC LIMIT %s, %s" % (self.startdate, self.enddate, start, end - start + 1))
                result = cursor.fetchall()
                writer.writerows(result)

                iter_time = (iter_time*iter + (perf_counter() - time_start))/(iter + 1)

                self.time_remaining.emit(iter_time*(iter_data - iter -1))

                self.iter_download.emit(iter)
        
        # Sinyal menandakan proses pengunduhan sudah selesai
        self.success_download.emit()



class DownloadData(QMainWindow):
    """Window utama untuk pengaturan data yang akan didownload."""

    def __init__(self):
        super(DownloadData, self).__init__()

        # Ambil file .ui 
        uic.loadUi("D:\\Undip\\Kerja Praktek\\Prototype PyQt5\\Prototype.Download data\\Main-window.download-data.ui", self)
        
        # Atur ukuran window
        self.setFixedSize(1026, 672)

        # Panggil komponen dari file .ui
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.searchButton = self.findChild(QToolButton, "searchButton")
        self.label_yourdir = self.findChild(QLabel, "label_yourdir")
        self.f_date = self.findChild(QFrame, "f_date")

        # Direktori default
        self.path = r"C:\Users\ACER SWIFT 3\OneDrive\Documents"
        self.label_yourdir.setText(self.path)
        
        # Panggil komponen tanggal
        self.dateStart = self.findChild(QDateEdit, "dateStart")
        self.dateEnd = self.findChild(QDateEdit, "dateEnd")

        # Koneksi tombol ke fungsi dialog dan direktori
        self.pushButton.clicked.connect(self.openDialog)
        self.searchButton.clicked.connect(self.openDir)

        # Atur komponen tanggal awal      
        now = datetime.now()
        self.dateStart = QtWidgets.QDateEdit(self.f_date, calendarPopup=True)
        self.dateStart.setDate(QtCore.QDate(int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))))
        self.dateStart.setGeometry(QtCore.QRect(50, 30, 161, 41))
        self.dateStart.setObjectName("dateStart")

        # Atur komponen tanggal akhir
        now = datetime.now() + timedelta(days=1)
        self.dateEnd = QtWidgets.QDateEdit(self.f_date, calendarPopup=True)
        self.dateEnd.setDate(QtCore.QDate(int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))))
        self.dateEnd.setGeometry(QtCore.QRect(300, 30, 161, 41))
        self.dateEnd.setObjectName("dateEnd")

        # Tampilkan window
        self.show()

    # Fungsi untuk memilih direktori penyimpanan data
    def openDir(self):
        self.path = str(QFileDialog.getExistingDirectory(self, "Open Folder", directory = self.path)).replace("/", "\\")
        if self.path:
            self.label_yourdir.setText(self.path)

    # Fungsi untuk memanggil window dialog proses pengunduhan
    def openDialog(self):
        start = self.dateStart.dateTime().toString("yyyy-MM-dd")
        end = self.dateEnd.dateTime().toString("yyyy-MM-dd")
        self.ui = ProcessingDownload(self.path, start, end)



class ProcessingDownload(QDialog):
    """Class untuk menampilkan dialog 
    proses pengunduhan data."""

    def __init__(self, path, startdate, enddate):
        super(ProcessingDownload, self).__init__()

        # Atur ukuran window
        self.setFixedSize(400, 300)

        # Inisialisasi objek untuk class
        self.path = path
        self.startdate = startdate
        self.enddate = enddate
        self.state = False
        self.pathfile = ""

        # Muat file .ui
        uic.loadUi("D:\\Undip\\Kerja Praktek\\Prototype PyQt5\\Prototype.Download data\\Dialog-box.progress-download.ui", self)

        # Panggil komponen dari file .ui
        self.pushButton = self.findChild(QPushButton, "pushButton")
        self.progressBar = self.findChild(QProgressBar, "progressBar")
        self.label = self.findChild(QLabel, "label_2")
        
        # Atur tombol OK
        self.pushButton.setEnabled(False)
        self.pushButton.clicked.connect(self.click)

        # Tampilkan window
        self.show()
        
        # Koneksi ke proses pengunduhan
        self.download_data = Download(path, startdate, enddate)
        self.download_data.num_download.connect(self.progressBar.setMaximum)
        self.download_data.iter_download.connect(self.progressBar.setValue)
        self.download_data.time_remaining.connect(self.eta)
        self.download_data.filepath.connect(self.filepath)
        self.download_data.success_download.connect(self.success)
        self.download_data.finished.connect(self.finish)
        self.download_data.start()


    def eta(self, eta_time):
        print(timedelta(seconds=eta_time))

    def filepath(self, path):
        self.pathfile = path
        print(self.pathfile)

    # Menandai proses pengunduhan selesai
    def success(self):
        self.state = True
        self.progressBar.setValue(self.progressBar.maximum())
        self.label.setText("Download success!")
        self.pushButton.setEnabled(True)

    # Mengakhiri proses
    def finish(self):
        self.state = True
        del self.download_data

    # Jika window ditutup ketika proses 
    # pengunduhan belum selesai.
    def closeEvent(self, event: QtGui.QCloseEvent):
        if not self.state:
            reply = QMessageBox.question(self, 'Window Close', 'Are you sure you want to stop the download?',
				QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                try:
                    self.download_data.requestInterruption()
                    self.download_data.wait()
                    self.download_data.terminate()
                    os.remove(self.pathfile)
                except: pass
                event.accept()
            else:
                event.ignore()

        else:
            event.accept()
        
    # Tutup window dialog
    def click(self):
        self.close()



class ShowData(QMainWindow):
    """Class untuk window penampil data."""

    def __init__(self):
        super(ShowData, self).__init__()

        # Inisialisasi penghitungan
        self.slide = 0
        self.num_data = 0
        self.iter_data = 0
        self.prev = 0
        self.next = 0
        self.range_data = 50

        # Muat file .ui
        uic.loadUi("Showdata_monitoring.ui", self)

        # Atur ukuran window
        self.setFixedSize(1104, 784)

        # Ambil widget untuk tabel .ui
        self.data = self.findChild(QTableWidget, "tableWidget")

        # Ambil objek label dari .ui
        self.page = self.findChild(QLabel, "label_2")
 
        # Atur level opacity gambar di latar belakang
        self.bg_img = self.findChild(QLabel, "label")
        self.opacity_effect = QGraphicsOpacityEffect()
        self.opacity_effect.setOpacity(0.4)
        self.bg_img.setGraphicsEffect(self.opacity_effect)
        
        # Atur tanggal awal
        now = datetime.now()
        self.start = self.findChild(QDateEdit, "dateEdit")
        self.start.setDate(QtCore.QDate(int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))))
        self.stlabel = self.findChild(QLabel, "startdate_label")

        # Atur tanggal akhir
        now = datetime.now() + timedelta(days=1)
        self.end = self.findChild(QDateEdit, "dateEdit_2")
        self.end.setDate(QtCore.QDate(int(now.strftime("%Y")), int(now.strftime("%m")), int(now.strftime("%d"))))
        self.enlabel = self.findChild(QLabel, "enddate_label")

        # Ubah tampilan tanggal
        self.date_start = self.start.dateTime().toString("yyyy-MM-dd")
        self.date_end = self.end.dateTime().toString("yyyy-MM-dd")

        # Panggil objek tombol dari .ui
        self.ok = self.findChild(QPushButton, "pushButton")

        # Atur judul tiap kolom dalam tombol
        self.data.setHorizontalHeaderLabels(["Timestamp", "Tegangan PV (V)", "Arus PV (A)", 
            "Daya PV (W)", "Tegangan \n VAWT (V)", "Arus VAWT (A)", "Daya VAWT (W)", 
            "Anemometer \n (m/s)", "Baterai (V)"])

        # Ambil komponen tombol Previous dan Next
        # Koneksi ke fungsi tombol
        self.nextB = self.findChild(QPushButton, "nextButton")
        self.prevB = self.findChild(QPushButton, "prevButton")
        self.nextB.clicked.connect(self.nextdata)
        self.prevB.clicked.connect(self.prevdata)

        # Atur tombol tidak bisa ditekan
        # secara default.
        self.prevB.setEnabled(False)
        self.nextB.setEnabled(False)

        # Koneksi tombol OK
        self.ok.clicked.connect(self.ok_clicked)

        # Panggil tombol close dari .ui
        self.close_showwin = self.findChild(QPushButton, "pushButton_2")

        # Koneksi tombol close ke operasi penutupan window
        self.close_showwin.clicked.connect(self.close_clicked)

        # Tampilkan window
        self.show()
    
    # Fungsi untuk menutup window
    def close_clicked(self):
        self.close()
        
    # Fungsi untuk perhitungan data yang akan ditampilkan
    def calc_range(self, slide, iter, num):
        self.prev = slide*50
        self.next = ((slide + 1)*50-1 ) if (slide != iter - 1) else num
        self.range_data = self.next - self.prev + 1

    # Fungsi untuk mengganti page dengan tombol Next
    def nextdata(self):
        self.slide +=1
        self.calc_range(self.slide, self.iter_data, self.num_data)
        self.loadData()
    
    # Fungsi untuk mengganti page dengan tombol Previous
    def prevdata(self):
        self.slide -= 1
        self.calc_range(self.slide, self.iter_data, self.num_data)
        self.loadData()

    # Mengambil data dari database sesuai yang diminta
    def ok_clicked(self):
        self.slide = 0
        self.prev = 0
        self.next = 0
        self.date_start = self.start.dateTime().toString("yyyy-MM-dd")
        self.date_end = self.end.dateTime().toString("yyyy-MM-dd")
        db = sqlc.connect(
            host = host_,
            user = user_,
            password = password_,
            database = database_
        )
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) "\
                       "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                       "ORDER BY id ASC" % (self.date_start, self.date_end))
        self.num_data = cursor.fetchall()[0][0]
        self.iter_data = ceil(self.num_data/50)
        self.calc_range(self.slide, self.iter_data, self.num_data)
        self.loadData()

    # Menampilkan data yang telah diambil ke tabel 
    def loadData(self):
        if self.slide <= 0:
            self.prevB.setEnabled(False)
        else:
            self.prevB.setEnabled(True)
        
        if self.slide >= self.iter_data - 1:
            self.nextB.setEnabled(False)
        else:
            self.nextB.setEnabled(True)

        db = sqlc.connect(
            host = host_,
            user = user_,
            password = password_,
            database = database_
        )
        cursor = db.cursor()
        cursor.execute("SELECT timestamp, v_pv, i_pv, p_pv, v_vawt, i_vawt, p_vawt, anemo, v_bat "\
                       "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                       "ORDER BY id ASC LIMIT %s, %s" % (self.date_start, self.date_end, self.prev, self.range_data))
        result = cursor.fetchall()
        num_data = len(result)
        self.page.setText("%s of %s total data" % ("%s - %s" %(self.prev + 1, self.next + 1)\
            if num_data >= 50 else num_data, self.num_data))

        self.tableWidget.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.tableWidget.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.tableWidget.setItem(row_number, column_number, QtWidgets.QTableWidgetItem(str(data)))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = Monitoring()
    app.exec_()