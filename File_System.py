def find_rootdirectory(path):
    with open(path, 'rb+') as f:
        f.seek(0,2) # Seek the end
           
        f.seek(0x4418)
        blocksize_bytes = f.read(4)
        blocksize = int.from_bytes(blocksize_bytes, byteorder='little', signed=False)
        blocksize = blocksize * blocksize
       
        f.seek(0x4428)
        inode_numbers_per_group_bytes = f.read(4)
        inode_numbers_per_group = int.from_bytes(inode_numbers_per_group_bytes, byteorder='little', signed=False)
       
        f.seek(0x4458)
        inodesize_bytes = f.read(2)
        inodesize = int.from_bytes(inodesize_bytes, byteorder='little', signed=False)
        
        GDT = 17408 + 1024 * (blocksize - 1)
     
        f.seek(GDT)
        block_bitmap_address_bytes = f.read(4)
        block_bitmap_address = int.from_bytes(block_bitmap_address_bytes, byteorder='little', signed=False)
        block_bitmap_address = block_bitmap_address * 1024*blocksize + 4096*inodesize
       
        f.seek(GDT + 4)
        inode_bitmap_address_bytes = f.read(4)
        inode_bitmap_address = int.from_bytes(inode_bitmap_address_bytes, byteorder='little', signed=False)
        inode_bitmap_address = inode_bitmap_address * 1024*blocksize + 4096*inodesize
        
        f.seek(GDT + 8)
        inode_table_address_bytes = f.read(4)
        inode_table_address = int.from_bytes(inode_table_address_bytes, byteorder='little', signed=False)
        inode_table_address = inode_table_address * 1024*blocksize + 4096*inodesize
        
        f.seek(inode_table_address + 256 + 60)
        root_directory_bytes = f.read(2)
        root_directory = int.from_bytes(root_directory_bytes, byteorder='little', signed=False)
        root_directory = root_directory * 1024*blocksize + 4096*inodesize
    
        i = root_directory
    
        while(1):
            f.seek(i)
            lost_found = f.read(10)
            if lost_found == b"\x6C\x6F\x73\x74\x2B\x66\x6F\x75\x6E\x64" :
                f.seek(2, 1) #현재 위치에서 2byte 이동
                here = f.tell()
                
                while(1):
                    f.seek(here)
                    inode_number_bytes = f.read(4)
                    inode_number = int.from_bytes(inode_number_bytes, byteorder='little', signed=False)
                    
                    if inode_number_bytes == b"\x00\x00\x00\x00":
                        break    

                    f.seek(2, 1) #현재 위치에서 2byte 이동
                    
                    name_len_bytes = f.read(2)
                    name_len = int.from_bytes(name_len_bytes, byteorder='little', signed=False)
                    name_len = name_len % 256
                    
                    print('')
                    print(f.read(name_len).decode('utf-8', 'ignore'))
                    here = f.tell()
                
                    if(inode_number > 8176):
                        
                        go_blockgroup_num = (inode_number - 1) // inode_numbers_per_group
                        go_blockgroup = GDT + 32 * go_blockgroup_num
    
                        f.seek(go_blockgroup + 8)
                        intad_num = f.read(4)
                        intad_num = int.from_bytes(intad_num, byteorder='little', signed=False)
                        intad = intad_num  * 1024*blocksize + 4096*inodesize
    
                        f.seek(intad + 60)
                        go_bytes = f.read(4)
                        go_bytes = int.from_bytes(go_bytes, byteorder='little', signed=False)
                        go = go_bytes * 1024*blocksize + 4096*inodesize
    
                        f.seek(go)
                        
                        stand = f.read(4)
                        stand = int.from_bytes(stand, byteorder='little', signed=False)
                            
                        while(1):                          
                            f.seek(2, 1) #현재 위치에서 2byte 이동
                            
                            len_name_bytes = f.read(2)
                            len_name = int.from_bytes(len_name_bytes, byteorder='little', signed=False)
                            len_name = len_name % 256
                            
                            if(len_name > 1):
                                print('ㄴ',f.read(len_name).decode('utf-8', 'ignore'))
                                f.seek(go + 4 + 4)
                                
                            stand = stand + 1
                                      
                            while(1):
                                next_stand = f.read(4)
                                next_stand = int.from_bytes(next_stand, byteorder='little', signed=False)
                                
                                if(next_stand == stand):
                                    break
                                
                                elif(next_stand == 0):
                                    break
                                
                            if(len_name == 0):
                                break
                    
                    f.seek(here)
                    
                    bp = 0
                    while(1):
                        new_here = f.read(1)
                        if(new_here != b"\x00"):
                            here = f.tell()
                            here = int(hex(here - 1), 16)
                            break
                        
                        bp = bp + 1
                        if(bp > 10):
                            break
                
            elif lost_found == b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" :
                break     
            i = i + 1
                  
path = input("*** input file *** \n")
find_rootdirectory(path)