import numpy as np
import requests

def sample_area_around_old(rlayer, x, y, r=16):
    """
    Old version of the func
    is too slow
    use sample_area_around()
    """
    xvalues = np.arange(x-r, x+r)
    yvalues = np.arange(y-r, y+r)
    output = []
    for y in yvalues[::-1]:
        for x in xvalues:
            val, res = rlayer.dataProvider().sample(QgsPointXY(x, y), 1)
            output.append(val)
    return output

def showme(pixels):
    arr = np.array(pixels)
    a = int(np.sqrt(len(pixels)))
    arr = arr.reshape(a, a)
    plt.imshow(arr)
    plt.show()


def get_pixels_from_rlayer(rlayer, x, y, w, h):
    dp = rlayer.dataProvider()
    rec = QgsRectangle(QgsPointXY(x, y), QgsPointXY(x+w, y-h))
    out = dp.block(1, rec, w, h).data()
    return out

def sample_area_around(rlayer, x, y, r=16):
    _y = y-1 #off-by-one thing.
    dp = rlayer.dataProvider()
    rec = QgsRectangle(QgsPointXY(x-r, _y-r), QgsPointXY(x+r, _y+r))
    w = int(r*2)
    h = int(r*2)
    out = dp.block(1, rec, w, h)
    output = [x[0] for x in out.data()]
    return output

def rawd(rlayer, x, y, r=16):
    dp = rlayer.dataProvider()
    rec = QgsRectangle(QgsPointXY(x-r, y-r), QgsPointXY(x+r, y+r))
    w = int(r*2)
    h = int(r*2)
    out = dp.block(1, rec, w, h)
    return out

def make_request(pixels):
    url = "http://localhost:8501/detect/"
    body = {"instances": [pixels]}
    r = requests.post(url=url, json=body)
    return r.json()

def do_detection(rlayer, x, y, r=16):
    pixels = sample_area_around(rlayer, x, y, r=r)
    response = make_request(pixels)
    x, y, r = response['predictions']
    return x, y, r

class DetectedCircle(object):
    def __init__(self, rlayer, x_in, y_in, r_in=16):
        x, y, r = do_detection(rlayer, x_in, y_in, r=r_in)
        self.a = x_in + (x - r_in)
        self.b = y + (r_in - y)
        self.r = r

    @cached_property
    def center(self):
        #a = Line(self.vertices[0], self.vertices[1]).perpendicular_bisector()
        #b = Line(self.vertices[1], self.vertices[2]).perpendicular_bisector()
        return (self.a, self.b)

    @cached_property
    def radius(self):
        #return Line(self.center, self.vertices[0]).length
        return self.r

    @cached_property
    def diameter(self):
        return 2 * self.radius

    def point_at(self, theta):
        return Point(
            self.radius * math.cos(theta) + self.a,
            self.radius * math.sin(theta) + self.b
        )

    def to_polygon(self, segments=64):
        thetas = [(2 * math.pi) / segments * i for i in range(segments)]
        return [self.point_at(theta) for theta in thetas]

    def __repr__(self):
        return 'Circle({}, {}, {})'.format(self.a, self.b, self.r)