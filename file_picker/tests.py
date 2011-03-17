import os
import file_picker

from django.db import models
from django.test import TestCase
from django.core.files import File
from django.utils import simplejson as json
from django.utils.text import capfirst

from file_picker.uploads import models as upload_models


class Image(models.Model):
    """
    Image Model for tests.
    """
    name = models.CharField(max_length=255)
    description_1 = models.TextField(blank=True)
    description_2 = models.TextField(blank=True)
    file = models.ImageField(upload_to='images/')    


class MockRequest(object):
    """
    Incomplete Mock Request object.
    """
    GET = {}
    
    def get(self, _dict):
        self.GET = _dict


class MockImagePicker(file_picker.ImagePickerBase):
    def __init__(self, name, model, columns, extra_headers):
        if columns:
            self.columns = columns
        if extra_headers:
            self.extra_headers = extra_headers
        super(MockImagePicker, self).__init__(name, model)


class TestListPage(TestCase):
    """
    Test listing page.
    """
    def setUp(self):
        self.path = os.path.abspath('%s' % os.path.dirname(__file__))
        self.image_file = File(open(os.path.join(self.path, 'static/img/attach.png')), "test_file.png")
        self.image = Image(
             name = 'Test Image',
             description_1 = 'test desc 1',
             description_2 = 'test desc 2',
             file = self.image_file,
            )
        self.image.save()
        self.request = MockRequest()
        self.field_names = Image._meta.get_all_field_names()
        self.field_names.remove('file')
        
    def test_all_fields(self):
        """
        Test neither columns nor extra_headers defined.
        """
        image_picker = MockImagePicker('image_test', Image, None, None)
        response = image_picker.list(self.request)
        list_resp = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.field_names, list_resp['columns'])
        self.assertEquals([capfirst(Image._meta.get_field(i).verbose_name) \
                for i in self.field_names], list_resp['extra_headers'])

    def test_columns(self):
        """
        Test only columns defined.
        """
        columns = ['description_2', 'name',]
        image_picker = MockImagePicker('image_test', Image, columns, None)
        response = image_picker.list(self.request)
        list_resp = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(columns, list_resp['columns'])
        extra_headers = [capfirst(Image._meta.get_field(i).verbose_name) \
                for i in columns]
        self.assertEquals(extra_headers, list_resp['extra_headers'])
        
    def test_extra_headers(self):
        """
        Test only extra headers defined.  Should ignore it completely.
        """
        image_picker = MockImagePicker('image_test', Image, None, ['Header'])
        response = image_picker.list(self.request)
        list_resp = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.field_names, list_resp['columns'])
        self.assertEquals([capfirst(Image._meta.get_field(i).verbose_name) \
                for i in self.field_names], list_resp['extra_headers'])
                
    def test_columns_and_headers(self):
        columns = ['description_2', 'name', 'description_1']
        extra_headers = ['Top Description', 'Image Name', 'Bottom Description']
        image_picker = MockImagePicker('image_test', Image, columns, extra_headers)
        response = image_picker.list(self.request)
        list_resp = json.loads(response.content)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(columns, list_resp['columns'])
        self.assertEquals(extra_headers, list_resp['extra_headers'])
