def filenames_dataoffset(path):
    with open(path, 'rb+') as f:
        f.seek(0,2) # Seek the end
        num_bytes = f.tell() # Get the file size

        for i in range(num_bytes):
            f.seek(i)
            four_bytes = f.read(4)
            if four_bytes == b"\x50\x4B\x03\x04": #Local signature
                f.seek(i+26) #26 offset : 파일이름길이
                name_length_bytes = f.read(2)
                name_length = int.from_bytes(name_length_bytes, byteorder='little', signed=False)
                f.seek(i+30) #30 offset : 파일이름
                print("\n", f.read(name_length))
                
                f.seek(i+28) #28 offset : extra field길이
                extra_bytes = f.read(2)
                extra = int.from_bytes(extra_bytes, byteorder='little', signed=False)
                datastart_offset = int(i + 30 + name_length + extra)
                print('datastart_offset : ', datastart_offset)
                
                f.seek(i+18) #18 offset : 파일길이
                Compressed_Size = f.read(4)
                data_length = int.from_bytes(Compressed_Size, byteorder='little', signed=False)
                save_path = input("*** input save path *** \n")
                with open(save_path, 'wb+') as file:
                    f.seek(datastart_offset)
                    file.write(f.read(data_length))
                
path = input("*** input file*** \n")
filenames_dataoffset(path)
