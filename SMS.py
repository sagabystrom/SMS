

import zipfile
import biplist
import sqlite3
import datetime
import os




output_file_path = "" #HTML filen
iphone_zip = "" #ZIP filen av mobilen
apple_madrid_plist = "/private/var/mobile/Library/Preferences/com.apple.madrid.plist"
MobileSMS_plist = "/private/var/mobile/Library/Preferences/com.apple.MobileSMS.plist"
sms_db = "" #DB filen
attachments = "" #Attachments filen


#Vi behöver en funktion som konverterar nanosekunder till läsbart format för oss
def convert_to_readable_date(timestamp_in_nanoseconds):
    # Konverterar nanosekunder från UTC 2001 till sekunder från och med Unix epoch
    timestamp_in_seconds = timestamp_in_nanoseconds / 1_000_000_000
    unix_epoch = datetime.datetime(1970, 1, 1)
    offset_2001 = datetime.timedelta(days=(365 * 31 + 8))
    timestamp_datetime = unix_epoch + datetime.timedelta(seconds=timestamp_in_seconds) + offset_2001
    return timestamp_datetime.strftime('%Y-%m-%d %H:%M:%S')


def get_plist(plist, title):
    with zipfile.ZipFile(iphone_zip, mode="r") as open_iphone_zip:
        for files in open_iphone_zip.namelist():
            if plist in files:
                output_file.write(f"<h2>{title} Plist: {plist} </h2>\n")
                plist_content = open_iphone_zip.read(files)
                plist_decode = biplist.readPlistFromString(plist_content)
                output_file.write("<h3>Plist Content:</h3>\n<ul>\n")
                for key, value in plist_decode.items():
                    output_file.write(f"<li>{key} = {value}</li>\n")
                output_file.write("</ul>\n")


def connect_to_db(select):
    connection = sqlite3.connect(sms_db)
    cursor = connection.cursor()
    cursor.execute(select)
    result = cursor.fetchall()
    connection.close()
    return result


def get_messages(text_contain, all = bool):

    if all:
        select_messages = "SELECT ROWID, text, service, account, date FROM message;"

    if text_contain != "":
        select_messages = f"SELECT ROWID, text, service, account, date FROM message WHERE text like '%{text_contain}%';"
    return connect_to_db(select_messages)


def get_attachments_connected_to_message(message_id):
    select_attachments = f"SELECT transfer_name FROM attachment LEFT JOIN message_attachment_join ON message_attachment_join.attachment_id = attachment.ROWID WHERE message_id = {message_id};"
    return connect_to_db(select_attachments)


def get_table(keyword):
    search_all = False


    if keyword != "":
        search_all = False
        title = f"SMS meddelanden från sms.db som matchar = {keyword}"
    else:
        search_all = True
        title = "SMS meddelanden från sms.db = alla"

    output_file.write(f"<h2>{title}</h2>\n")
    output_file.write("<table>\n<tr><th>ROWID</th><th>Text</th><th>Service</th><th>Account</th><th>Date</th><th>Attachment</th></tr>\n")
    attachment_string = ""


   
    for row_message in get_messages(keyword, search_all):
        for row_attachment in get_attachments_connected_to_message(row_message[0]):
            sokvag = ""
            for org_mapp, sub_mapp, final_mapp in os.walk(attachments):
                for fil in final_mapp:
                    fil_path = os.path.join(org_mapp, fil)
                    if fil == row_attachment[0]:
                        sokvag = fil_path.replace('\\', '/')
                        break

           
            if sokvag != "":
                
                attachment_string += f'<a href="{sokvag}" target="_blank" download>{row_attachment[0]}</a><br><br>'



        
        if attachment_string == "":
        
            attachment_string = ("Ingen attachment hittades")

     
        output_file.write("<tr>\n")
        output_file.write(f"<td>{row_message[0]}</td>")  # message.ROWID
        output_file.write(f"<td>{row_message[1]}</td>")  # message.text
        output_file.write(f"<td>{row_message[2]}</td>")  # message.service
        output_file.write(f"<td>{row_message[3]}</td>")  # message.account
        
        readable_date = convert_to_readable_date(row_message[4])
       
        output_file.write(f"<td>{readable_date}</td>")
        output_file.write(f"<td>{attachment_string}</td>")
        output_file.write("</tr>\n")
     
        attachment_string = ""

  
    output_file.write("</table>\n</body>\n</html>")



whatuwant= input("Vilka SMS artefakt vill du få reda på? \n Skriv A för alla typer av (SMS) artefakt \n Skriv B för apple_madrid_plist \n Skriv C för MobileSMS_plist \n Skriv D för alla plist filer \n Skriv E för SMS.db \n Skriv Q för att avsluta \nVänligen skriv bokstav = ").upper()




with open(output_file_path, "w", encoding="utf-8") as output_file:
 
    output_file.truncate(0)
 
    output_file.write("<!DOCTYPE html>\n<html>\n<head>\n<title>SMS Artefacts</title>\n<style>\n")


    output_file.write("body { font-family: 'lato', sans-serif; }\n")
    output_file.write("table { border-collapse: collapse; width: 100%;  }\n")
    output_file.write("th, td { border: 1px solid #dddddd; text-align: left; padding: 8px; }\n")
    output_file.write("th { background-color: #f2f2f2; }\n")
    output_file.write("h1, h2, p, h3 { color: pink; text-align: center; margin: 20px 0; }\n")
    output_file.write("tr:hover { background-color: #fefaad ; }\n")
    output_file.write("body { font-family: Arial, sans-serif; }\n")
    output_file.write("tr { border-bottom: 1px solid #ddd ;}")


    output_file.write("</style>\n</head>\n<body>\n")


    output_file.write("<h1>SMS Artefacts</h1>\n")


    if whatuwant == "A":
        keyword = input("Vill du ha ett specefik SMS (keyword search i sms.db)? Skriv isf ditt keyword du är intresserad av \n Inte intresseradav en keyword search, tryck 'enter' \n Vänligen skriv bokstav = ")
        get_plist(apple_madrid_plist, "Madrid")
        get_plist(MobileSMS_plist, "MobileSMS")
        get_table(keyword)


    elif whatuwant == "B":
        get_plist(apple_madrid_plist, "Madrid")

    elif whatuwant == "C":
        get_plist(MobileSMS_plist, "MobileSMS")


    elif whatuwant == "D":
        get_plist(apple_madrid_plist, "Madrid")
        get_plist(MobileSMS_plist, "MobileSMS")

    elif whatuwant == "E":
        keyword = input("Vill du ha ett specefik SMS (keyword search i sms.db)? Skriv isf ditt keyword du är intresserad av \n Inte intresseradav en keyword search, tryck 'enter' \n Vänligen skriv bokstav = ")
        get_table(keyword)




    elif whatuwant == "Q":
        print("Avslutar programmet!")
        exit()

    else:
        print("Vänligen skriv rätt bokstav, försök igen!")
