import shutil, os

def In_NTFS(path):
   with open(path, 'rb+') as f:
       f.seek(0,2)  # Seek the end
       
       f.seek(0x0B)
       byte_per_sector_b = f.read(2)
       byte_per_sector = int.from_bytes(byte_per_sector_b, byteorder='little', signed=False)
       
       f.seek(0x0D)
       sector_per_cluster_b = f.read(1)
       sector_per_cluster = int.from_bytes(sector_per_cluster_b, byteorder='little', signed=False)
       
       f.seek(0x30)
       num_of_MFT_b = f.read(8)
       num_of_MFT = int.from_bytes(num_of_MFT_b, byteorder='little', signed=False)
       
       sector_MFT = num_of_MFT * sector_per_cluster
       search = (sector_MFT + 32) * byte_per_sector
       
       f.seek(search)
       f.seek(0xF2, 1)
       
       folder_f = []
       
       while True:
           i_UsnJrnl = f.read(16)
           if (i_UsnJrnl == b'\x24\x00\x55\x00\x73\x00\x6E\x00\x4A\x00\x72\x00\x6E\x00\x6C\x00'):
               break
           f.seek(-16, 1)
           f.seek(2 * byte_per_sector, 1)
           
       f.seek(-258, 1) #$UsnJrnl시작부분
       MFT_now = f.seek(2 * byte_per_sector, 1) #file정보 시작
       
       while True: 
            f.seek(MFT_now)

            signature = f.read(4)
            if (signature != b'\x46\x49\x4C\x45'):
                break

            f.seek(18, 1)
            folder_or_file = f.read(2)   #01=file, 03=folder

            f.seek(32, 1)

            while True:  #file 이름 가져오기
                find_Mname = f.read(4) #속성 Number구분
                size_b = f.read(4)
                size = int.from_bytes(size_b, byteorder='little', signed=False)
                
                if (find_Mname == b'\x30\x00\x00\x00'): #name속성을 찾으면
                    f.seek(80, 1)

                    name_length_b = f.read(2)
                    name_length = 2 * int.from_bytes(name_length_b, byteorder='little', signed=False)
                    
                    f_names = f.read(name_length).decode('utf-8')
                    f_name = []
                    
                    for i in range(0, name_length, 2):
                        f_name.append(f_names[i])
                        
                    f_name = ''.join(f_name)
                    
                    if(folder_or_file == b'\x03\x00'): #folder일 경우
                        folder_f = []
                        folder_f.append(f_name) #folder_f의 첫번째 인덱스에는 폴더 이름이 들어가 있음
                        os.makedirs(f_name)
                        f.seek(-(name_length+90), 1)
                        f.seek(size, 1)
                        
                        find_Mname = f.read(4)
                        
                        while(find_Mname != b'\x90\x00\x00\x00'):
                            size_b = f.read(4)
                            size = int.from_bytes(size_b, byteorder='little', signed=False)
                            f.seek(-8+size, 1)
                            find_Mname = f.read(4) #속성 Number구분
              
                        f.seek(132, 1)
                        is_file = f.read(8)
                            
                        while(is_file == b'\x20\x00\x00\x00\x00\x00\x00\x00'):
                            infolder_f_length_b = f.read(2)
                            infolder_f_length = 2 * int.from_bytes(infolder_f_length_b, byteorder='little', signed=False)
                            
                            infolder_fs = f.read(infolder_f_length).decode('utf-8')
                            infolder_f = []
                            
                            for i in range(0, infolder_f_length, 2):
                                infolder_f.append(infolder_fs[i])
                                
                            infolder_f = ''.join(infolder_f)
                            folder_f.append(infolder_f)
                            
                            f.seek(-(infolder_f_length + 2) + 96, 1)
                            is_file = f.read(8)
                        print(folder_f[0], ':', folder_f[1:])
                    
                    elif(folder_or_file == b'\x01\x00'): #file일 경우
                        
                        while True:
                                if(f.read(1)==b'\x80'):
                                    break
                        f.seek(7,1)
                        resident = f.read(1)

                        if(resident == b'\x01'): #non
                            f.seek(39, 1)
                            datasize_b = f.read(8)
                            datasize = int.from_bytes(datasize_b, byteorder='little', signed=False)
                            
                            f.seek(10, 1)
                            runoffset_b = f.read(2)
                            runoffset = int.from_bytes(runoffset_b, byteorder='little', signed=False)
                            
                            runlist = runoffset * 8 * byte_per_sector
                            
                            f.seek(runlist)
                            
                            with open(f_name, 'wb+') as file:
                                file.write(f.read(datasize)) #rundata
                            file.close()
                            print('\n', f_name, '\textracted\n') #추출
                            
                        elif(resident == b'\x00'): #resident
                            f.seek(7, 1)
                            datasize_b = f.read(4)
                            datasize = int.from_bytes(datasize_b, byteorder='little', signed=False)
                            
                            f.seek(4, 1)
                            with open(f_name, 'wb+') as file:
                                file.write(f.read(datasize)) 
                            file.close()
                            print('\n', f_name, '\textracted\n') #추출
                            
                        if(f_name in folder_f):
                            folder_name = folder_f[0]
                            save_path = '/'+folder_name+'/'
                            here = os.getcwd()+'/'
                            shutil.move(here + f_name, here+save_path+f_name)
                            
                    MFT_now = MFT_now + 2 * byte_per_sector
                    break

                #name속성 찾는 중
                else:
                    f.seek(-8, 1)    
                    f.seek(size, 1)

   print('\n Extract Finished \n')
   f.close()
       
path = input("Input path\n")
In_NTFS(path)

#print(hex(f.tell()))