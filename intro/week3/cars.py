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

            car_type = row[fields['car_type']]
            brand = row[fields['brand']]
            photo_file_name = row[fields['photo_file_name']]
            carrying = row[fields['carrying']]
            try:
                if car_type == 'car':
                    passenger_seats_count = row[fields['passenger_seats_count']]
                    cars.append(Car(brand, photo_file_name, carrying, passenger_seats_count))
                elif car_type == 'truck':
                    body_whl = row[fields['body_whl']]
                    cars.append(Truck(brand, photo_file_name, carrying, body_whl))
                elif car_type == 'spec_machine':
                    extra = row[fields['extra']]
                    cars.append(SpecMachine(brand, photo_file_name, carrying, extra))
            except CarBaseException:
                continue
    return cars

class CarBaseException(Exception):
    pass

class CarBase:
    allowed_exts = ('jpg', 'jpeg', 'png', 'gif')
    def __init__(self, brand, photo_file_name, carrying):
        self.photo_file_name = self.validate_input(photo_file_name)
        self.photo_filename_ext = self.validate_photo_ext(self.photo_file_name)
        self.brand = self.validate_input(brand)
        self.carrying = self.validate_carrying(carrying)
    def validate_carrying(self, carrying):
        try:
            return float(carrying)
        except ValueError as err:
            raise CarBaseException from err

    def validate_photo_ext(self, photo_file_name):
        photo_filename_ext = self.photo_file_name.split('.')[-1]
        if photo_filename_ext not in CarBase.allowed_exts:
            raise CarBaseException
        return '.' + photo_filename_ext

    def validate_input(self, input_):
        if len(input_) == 0:
            raise CarBaseException
        return input_
    def get_photo_file_ext(self):
        return self.photo_filename_ext
        
    
class Car(CarBase):
    car_type = 'car'
    def __init__(self, brand, photo_file_name, carrying, passenger_seats_count):
        super().__init__(brand, photo_file_name, carrying)
        
        try:
            self.passenger_seats_count = int(self.validate_input(passenger_seats_count))
        except ValueError as err:
            raise CarBaseException from err

class Truck(CarBase):
    car_type = 'truck'
    def __init__(self, brand, photo_file_name, carrying, body_whl):
        super().__init__(brand, photo_file_name, carrying)
        self._body_volume = self._calculate_volume(body_whl)
    def _calculate_volume(self, body_whl):
        zero_volume = 0.0
        self.body_width = 0.0
        self.body_height = 0.0
        self.body_length = 0.0
        if len(body_whl) == 0:
            return zero_volume
        body_whl_splitted = body_whl.split('x')
        if len(body_whl_splitted) < 3:
            return zero_volume
        try:
            l, w, h = list(map(float, body_whl_splitted))
        except ValueError:
            return zero_volume
        body_volume = w*h*l
        self.body_width = w
        self.body_height = h
        self.body_length = l
        return body_volume
        
    def get_body_volume(self):
        return self._body_volume
            
class SpecMachine(CarBase):
    car_type = 'spec_machine'
    def __init__(self, brand, photo_file_name, carrying, extra):
        super().__init__(brand, photo_file_name, carrying)
        self.extra = self.validate_input(extra)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Specify file to read")
        exit()
    filename = sys.argv[1]
    cars = get_car_list(filename)
    for car in cars:
        print(car.carrying)