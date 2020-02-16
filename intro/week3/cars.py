import csv
import sys
def get_car_list(csv_file):
    cars = []
    
    with open(csv_file) as csv_fd:
        reader = csv.reader(csv_fd, delimiter=';')
        header = next(reader)
        fields = {field: i for i, field in enumerate(header)}
        #print(fields.items())
        for row in reader:
            if len(row) < 6:
                continue
            #print(row)
            carrying_ = row[fields['carrying']]
            try:
                carrying = float(carrying_)
                
            except ValueError:
                continue
            
            brand = row[fields['brand']]
            if len(brand) == 0:
                continue
            photo_file_name = row[fields['photo_file_name']]
            photo_file_name_ext = photo_file_name.split('.')[-1]
            if photo_file_name_ext not in ('jpg', 'jpeg', 'png', 'gif'):
                continue
            car_type = row[fields['car_type']]
            if car_type == 'car':
                try:
                    passenger_seats_count = int(row[fields['passenger_seats_count']])
                except ValueError:
                    continue
                assert isinstance(carrying, float)
                cars.append(Car(brand, photo_file_name, carrying, passenger_seats_count))
            elif car_type == 'truck':
                body_whl = row[fields['body_whl']]
                cars.append(Truck(brand, photo_file_name, carrying, body_whl))
            elif car_type == 'spec_machine':
                extra = row[fields['extra']]
                cars.append(SpecMachine(brand, photo_file_name, carrying, extra))
    return cars



class CarBase:
    def __init__(self, brand, photo_file_name, carrying):
        self.photo_file_name = photo_file_name
        self.photo_filename_ext = self.photo_file_name.split('.')[-1]
        self.brand = brand
        self.carrying = carrying
        assert isinstance(carrying, float)
    def get_photo_file_ext(self):
        return self.photo_filename_ext
    
class Car(CarBase):
    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        assert isinstance(carrying, str)
        super().__init__(brand, photo_file_name, carrying)
        self.car_type = 'car'
        self.passenger_seats_count = passenger_seats_count

class Truck(CarBase):
    def __init__(self, brand, photo_file_name, carrying, body_whl):
        super().__init__(brand, photo_file_name, carrying)
        self.car_type = 'truck'
        self._body_volume = self.calculate_volume(body_whl)
    def calculate_volume(self, body_whl):
        zero_volume = 0
        if len(body_whl) == 0:
            return zero_volume
        body_whl_splitted = body_whl.split('x')
        if len(body_whl_splitted) < 3:
            return zero_volume
        try:
            w, h, l = list(map(float, body_whl_splitted))
        except ValueError:
            return zero_volume
        body_volume = w*h*l
        return body_volume
        
    def get_body_volume(self):
        return self._body_volume
            
class SpecMachine(CarBase):
    def __init__(self, brand, photo_file_name, carrying, extra):
        super().__init__(brand, photo_file_name, carrying)
        self.car_type = 'spec_machine'
        self.extra = extra

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify file to read")
        exit()
    filename = sys.argv[1]
    cars = get_car_list(filename)
    for car in cars:
        print(car.carrying)