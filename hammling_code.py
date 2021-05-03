import math

class HammlingCode:
    #Nieużywana metoda do licznenia ile potrzebnych jest bitów kontrolnych
    @staticmethod
    def count_control_bits(primitive_frame):
        frame_lenght=len(primitive_frame)
        control_bits_counter=round(math.log(frame_lenght,2),0)+1;
        print(control_bits_counter)

    #Główna metoda tworzenia kodu Hammlinga
    @staticmethod
    def create_hammling_8(primitive_frame):
        hammling_code=primitive_frame
        slowa=[]
        hammling_code=HammlingCode.add_control_bits(hammling_code)
        HammlingCode.get_up_bits_position(hammling_code, slowa)
        hammling_code=HammlingCode.set_control_bits(hammling_code,slowa)
        print("Kod Hammlinga dla "+primitive_frame + " to " + hammling_code)

    #Metoda dodająca do słowa bity kontrolne
    @staticmethod
    def add_control_bits(primitive_frame):
        primitive_frame="00"+primitive_frame[:1]+'0'+primitive_frame[1:4]+'0'+primitive_frame[4:];
        return primitive_frame

    #Metoda zapisująca do listy pozycje jedynek w podanym słowie bitowym
    @staticmethod
    def get_up_bits_position(primitive_frame, slowa):
        for i in range(len(primitive_frame)):
            if primitive_frame[i] == '1':
                slowa.append(bin(i)[2:])
        for i in range(len(slowa)):
            while len(slowa[i]) < 4:
                slowa[i] = '0' + slowa[i]

    #Metoda obliczająca wartość bitów kontrolnych i ustawiająca je
    @staticmethod
    def set_control_bits(primitive_frame, slowa):
        x0 = 0
        x1 = 0
        x2 = 0
        x3 = 0
        for i in range(len(slowa)):
            x0 += int(slowa[i][0])
            x1 += int(slowa[i][1])
            x2 += int(slowa[i][2])
            x3 += int(slowa[i][3])
        list_buff=list(primitive_frame)
        list_buff[0] = str(x3 % 2)
        list_buff[1] = str(x2 % 2)
        list_buff[3] = str(x1 % 2)
        list_buff[7] = str(x0 % 2)
        primitive_frame="".join(list_buff)
        return primitive_frame





primitive_frame=input("Podaj słowo 8 bitowe");
HammlingCode.create_hammling_8(primitive_frame);
