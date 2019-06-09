def fetch_url(coord,
              travelmode='walking'):
    destination = '%f,%f' % (coord[0], coord[1])
    return f'https://google.com/maps/dir/?api=1&destination={destination}&travelmode={travelmode}'
