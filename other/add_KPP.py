fsrar = 30000617779
kpp = 784105177

fsrar+=1
kpp+=1

fsrar = "0"+str(fsrar)

insert_0 = ("INSERT INTO Clients"
            "(Owner_ID, Full_Name, Short_Name, INN, KPP, Country_Code, Region_Code, Dejure_Address, Fact_Address, isLicense, Version_ts, pass_owner_id)"
            f" VALUES(N'{fsrar}', N'эс', N'спирт', N'7841051711', N'{784105177}', N'643', N'111', N'юр2', N'факт', 0, 0x00000000349752C5, N'43022397');")

print(insert_0)