from geopy.geocoders import Nominatim



def get_coord(adres):
    app = Nominatim(user_agent="tutorial")

    location = app.geocode(adres).raw
    print(location)

    # возвращает координаты

    return location




