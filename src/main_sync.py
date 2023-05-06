import os, csv
from time import sleep
import mysql.connector as sql
from telegram.ext import *
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

#Google Drive
scopes = ["https://www.googleapis.com/auth/drive"]
path_token = r"src/token.json"
folder = "15D5_93-iImEVtpFnXdQz0gGq9IAvDQxJ"

#telegram
admin = ["1063290918"]
token = "5922929317:AAHt3mXpmxnHnlnZFMWlTw0TwYtwtH4v8HU"

#database
host = "localhost"
user = "greenhouse"
password = "greenhouse"
database = "greenhouse"

def check_database(update, context):
    if str(update.message.from_user.id) not in admin:
        update.message.reply_text("Anda dengan UserID : %s tidak terdaftar dalam sistem kami.\nMohon melapor" % error)
        return None
    try:
        db = sql.connect(
            host = host,
            user = user,
            password = password,
            database = database
            )
        db.close()
        update.message.reply_text("Local database berhasil terhubung")
    except Exception as error:
        update.message.reply_text("Local database tidak terhubung\nError : %s" % error)

def get_data(update, context):
    try:
        db = sql.connect(
            host = host,
            user = user,
            password = password,
            database = database
            )
        cursor = db.cursor()
        cursor.execute("SELECT * FROM monitoring_daya ORDER BY timestamp DESC LIMIT 1")
        sensor = tuple(cursor.fetchall()[0])[1:]
        db.close()
        update.message.reply_text(
            "Monitoring Daya Greenhouse\n"\
            " - Timestamp : %s\n"\
            " - PV Voltage : %s Volt\n"\
            " - PV Current : %s Ampere\n"\
            " - PV Power : %s Watt\n"\
            " - VAWT Voltage : %s Volt\n"\
            " - VAWT Current : %s Ampere\n"\
            " - VAWT Power : %s Watt\n"\
            " - Anemometer : %s m/s\n"\
            " - Voltage Battery : N/A Volt"\
            % sensor
            )
    except Exception as error:
        update.message.reply_text("Local database tidak terhubung\nError : %s" % error)

async def get_csv(update, context):
    try:
        date = str(update.message.text).split("/get_csv ")[1]
        date_start = date.split(" ")[0]
        date_end = date.split(" ")[1]
        datetime.strptime(date_start, "%Y-%m-%d")
        datetime.strptime(date_end, "%Y-%m-%d")
        try:
            await update.message.reply_text("Mohon menunggu, sistem sedang memproses data.")
            db = sql.connect(
                host = host,
                user = user,
                password = password,
                database = database
            )
            cursor = db.cursor()
            cursor.execute("SELECT timestamp, v_pv, i_pv, p_pv, v_vawt, i_vawt, p_vawt, anemo "\
                            "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                            "ORDER BY id ASC" % (date_start, date_end))
            data = list(cursor.fetchall())
            db.close()

            column = ["Timestamp", "PV Voltage (Volt)", "PV Current (Ampere)", "PV Power (Watt)",\
                      "VAWT Voltage (Volt)", "VAWT Current (Ampere)", "VAWT Power (Watt)", "Anemometer (m/s)"]
            with open(r"cache_csv\Data Greenhouse %s to %s.csv" % (date_start, date_end), mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(column)
                writer.writerows(data)
                path = os.path.abspath(file.name)

            with open(path, "rb") as csv_file:
                await update.message.reply_document(csv_file, write_timeout=100, connect_timeout=100)
                # context.bot.send_document(update.message.chat_id, csv_file, write_timeout=100)

        except Exception as error:
            await update.message.reply_text("Mohon maaf, terjadi kesalahan sistem saat memproses data. Silahkan coba beberapa saat lagi.\n"\
                                      "Error : %s" % error)
    except:
        await update.message.reply_text("Perintah yang dimasukkan tidak benar\nFormat : /get_csv YYYY-MM-DD YYYY-MM-DD\n"\
                                  "Contoh : /get_csv 2023-01-01 2023-01-20")
    try:
        os.remove(path)
    except:
        pass

def get_drive(update, context):
    try:
        date = str(update.message.text).split("/get_drive ")[1]
        date_start = date.split(" ")[0]
        date_end = date.split(" ")[1]
        datetime.strptime(date_start, "%Y-%m-%d")
        datetime.strptime(date_end, "%Y-%m-%d")
        try:
            update.message.reply_text("Mohon menunggu, sistem sedang memproses data.")

            db = sql.connect(
                host = host,
                user = user,
                password = password,
                database = database
            )
            cursor = db.cursor()
            cursor.execute("SELECT timestamp, v_pv, i_pv, p_pv, v_vawt, i_vawt, p_vawt, anemo "\
                            "FROM monitoring_daya WHERE timestamp BETWEEN '%s 00:00:00' AND '%s 00:00:00' "\
                            "ORDER BY id ASC" % (date_start, date_end))
            data = list(cursor.fetchall())
            db.close()
            column = ["Timestamp", "PV Voltage (Volt)", "PV Current (Ampere)", "PV Power (Watt)",\
                      "VAWT Voltage (Volt)", "VAWT Current (Ampere)", "VAWT Power (Watt)", "Anemometer (m/s)"]
            
            with open(r"cache_drive\Data Greenhouse %s to %s.csv" % (date_start, date_end), mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(column)
                writer.writerows(data)
                path = os.path.abspath(file.name)
            
            creds = Credentials.from_authorized_user_file(path_token, scopes)
            service = build("drive", "v3", credentials=creds)

            file_metadata = {
                "name": "Data Greenhouse %s to %s.csv" % (date_start, date_end),
                "parents": [folder]}
            
            media = MediaFileUpload(
                path,
                mimetype="text/csv",
                resumable=True)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields="id").execute()
            media.__del__()

            permission = {
                "role": "reader",
                "type": "anyone"}
            service.permissions().create(
                fileId=file.get("id"),
                body=permission).execute()
            
            response_share_link = service.files().get(
                fileId=file.get("id"),
                fields="webViewLink").execute()
            
            update.message.reply_text("Link Google Drive: %s" % response_share_link.get("webViewLink"))

        except Exception as error:
            update.message.reply_text("Mohon maaf, terjadi kesalahan sistem saat memproses data. Silahkan coba beberapa saat lagi.\n"\
                                      "Error : %s" % error)
    except:
        update.message.reply_text("Perintah yang dimasukkan tidak benar\nFormat : /get_drive YYYY-MM-DD YYYY-MM-DD\n"\
                                  "Contoh : /get_drive 2023-01-01 2023-01-20")
    try:
        os.remove(path)
    except:
        pass

def error(update, context):
    print(f"Update {update} cause error: {context.error}")

if __name__ == "__main__":
    # updater = Updater(token, use_context = True)
    # for id in admin:
    #     updater.bot.sendMessage(chat_id = id, text = "Memulai Bot Greenhouse!")

    # dp = updater.dispatcher
    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("check_database", check_database))
    application.add_handler(CommandHandler("get_data", get_data))
    application.add_handler(CommandHandler("get_csv", get_csv))
    application.add_handler(CommandHandler("get_drive", get_drive))
    application.add_error_handler(error)

    application.run_polling()

    while True:
        try:
            pass
            sleep(0.1)
        except Exception as error:
            print("Main loop error : %s" % error)
    # updater.idle()