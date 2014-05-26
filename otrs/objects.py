import xml.etree.ElementTree as etree

class OTRSObject(object):
    CHILD_MAP = {}

    def __init__(self, *args, **kwargs):
        self.attrs = kwargs
        self.childs = {}

    def __getattr__(self, k):
        return autocast(self.attrs[k])

    @classmethod
    def from_xml(cls, xml_element):
        child_tags = cls.CHILD_MAP.keys()

        if not xml_element.tag.endswith(cls.XML_NAME):
            raise ValueError(
                'xml_element should be a {} node, not {}'.format(
                    cls.XML_NAME, xml_element.tag))
        attrs = {}
        childs = []
        for t in xml_element.getchildren():
            name = extract_tagname(t)
            if name in child_tags:
                SubClass = cls.CHILD_MAP[name]
                sub_obj = SubClass.from_xml(t)
                childs.append(sub_obj)
            else:
                attrs[name] = t.text
        obj = cls(**attrs)

        for i in childs:
            obj.add_child(i)

        return obj

    def add_child(self, childobj):
        xml_name = childobj.XML_NAME

        if self.childs.has_key(xml_name):
            self.childs[xml_name].append(childobj)
        else:
            self.childs[xml_name] = [childobj]



    def check_fields(self, fields):
        keys = self.attrs.keys()
        for i in fields:
            if isinstance(i, (tuple, list)):
                valid = self.attrs.has_key(i[0]) or self.attrs.has_key(i[1])
            else:
                valid = self.attrs.has_key(i)
            if not valid:
                raise ValueError('{} should be filled'.format(i))

    def to_xml(self):
        root = etree.Element(self.XML_NAME)
        for k, v in self.attrs.items():
            e = etree.Element(k)
            e.text = str(v)
            root.append(e)
        return root

def extract_tagname(element):
    qualified_name = element.tag
    try:
        return qualified_name.split('}')[1]
    except IndexError:
        # if it's not namespaced, then return the tag name itself
        return element.tag
        #raise ValueError('"{}" is not a tag name'.format(qualified_name))

def autocast(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

class Article(OTRSObject):
    XML_NAME = 'Article'

class Ticket(OTRSObject):
    XML_NAME = 'Ticket'
    CHILD_MAP = {'Article' : Article}

    def articles(self):
        try:
            return self.childs['Article']
        except KeyError:
            return []