import arcpy
import os
import datetime
import sys
import smtplib
from email.mime.text import MIMEText

arcpy.SignInToPortal("https://www.arcgis.com", "****", "****")
arcpy.env.overwriteOutput = True

#Required Parameters
aprxFile = r"D:\services_running\BCPA_Data\Master_updated.aprx"

service_folder = 'BCPA'
save_location = r'D:\services_running\BCPA_Data\temp'
temp_location = r'D:\services_running\BCPA_Data\temp'

sddraft_output_filename = 'draft_service_definition.sddraft'

mailhost="****"
fromaddr="****"
toaddrs=["****"]
credentials=('', '')
secure=()


#Optional Parameters
share_public = True
share_organization = True
share_groups = ['BCPA']
overwriteService = True

summary = ''
tags = ''
description = ''



def main():
    f = open("log.txt", "w+")
##    try:
    aprx = arcpy.mp.ArcGISProject(aprxFile)
    m = aprx.listMaps()

    for map in m:
        mapName = map.name
        service = mapName
        print(f"Publishing {mapName}")

        # Create FeatureSharingDraft and set service properties
        sharing_draft = map.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", service)
        sharing_draft.summary = mapName
        sharing_draft.tags = 'BCPA'
        sharing_draft.description = description
        sharing_draft.credits = "My Credits"
        sharing_draft.useLimitations = "My Use Limitations"
        sharing_draft.overwriteExistingService = overwriteService
        sharing_draft.portalFolder = service_folder

        # Create Service Definition Draft file
        sharing_draft.exportToSDDraft(os.path.join(temp_location, sddraft_output_filename))
        outsddraft = os.path.join(temp_location, sddraft_output_filename)
        print("Service definition draft created")

        # Create Service Definition file
        sd_filename = service + ".sd"
        sd_output_filename = os.path.join(save_location, sd_filename)
        print("Start Staging")
        arcpy.StageService_server(outsddraft, sd_output_filename)

        # Upload to portal
        print("Start Uploading")
        output = arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services", in_override="OVERRIDE_DEFINITION",
                                                       in_public=share_public, in_organization=share_organization, in_groups=share_groups)
        print("Service published")

    f.write(f'last run {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    
        
##    except arcpy.ExecuteError:
##        e = arcpy.GetMessages(2)
##        emailer(e)
##        f.write(f'Fail occured on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
##        f.write(str(e))
##        f.write('\n')
##        f.write('\n')
##    except:
##        # By default any other errors will be caught here
##        e = sys.exc_info()[1].args[0]
##        emailer(e)
##        f.write(f'Fail occured on {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
##        f.write(str(e))
##        f.write('\n')
##        f.write('\n')

    f.close()




def emailer(e):
    SERVER = mailhost
    AUTH_USER = credentials[0]
    AUTH_PWD = credentials[1]

    mailserver = smtplib.SMTP(SERVER)
    mailserver.ehlo()

    message = "My CFA Service Upload failed." + "\n"
    message = "Run on " + os.environ['COMPUTERNAME'] + "\n"
    message = message + e

    subject = "BCPA AGOL Data Upload failed"

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = fromaddr
    msg['To'] = toaddrs[0]

    print(message)
    s = smtplib.SMTP(SERVER)
    s.sendmail(fromaddr, toaddrs, msg.as_string())



if __name__ == "__main__":
    main()
