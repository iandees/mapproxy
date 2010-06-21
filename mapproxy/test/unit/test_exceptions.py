# This file is part of the MapProxy project.
# Copyright (C) 2010 Omniscale <http://omniscale.de>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import Image
from cStringIO import StringIO
from mapproxy.test.helper import Mocker, validate_with_dtd, validate_with_xsd
from mapproxy.test.image import is_png
from mapproxy.request.wms import WMSMapRequest
from mapproxy.request import url_decode
from mapproxy.exception import (RequestError, ExceptionHandler)
from mapproxy.request.wms.exception import (WMS100ExceptionHandler, WMS111ExceptionHandler,
                                     WMS130ExceptionHandler)
from nose.tools import eq_

class TestRequestError(Mocker):
    def test_render(self):
        req = self.mock(WMSMapRequest)
        ex_handler = self.mock(ExceptionHandler)
        
        req_ex = RequestError('the exception message', request=req)
        self.expect(req.exception_handler).result(ex_handler)
        self.expect(ex_handler.render(req_ex))
        
        self.replay()
        req_ex.render()

class ExceptionHandlerTest(Mocker):
    def setup(self):
        Mocker.setup(self)
        req = url_decode("""LAYERS=foo&FORMAT=image%2Fpng&SERVICE=WMS&VERSION=1.1.1&
REQUEST=GetMap&STYLES=&EXCEPTIONS=application%2Fvnd.ogc.se_xml&SRS=EPSG%3A900913&
BBOX=8,4,9,5&WIDTH=150&HEIGHT=100""".replace('\n', ''))
        self.req = req

class TestWMS111ExceptionHandler(Mocker):
    def test_render(self):
        req = self.mock(WMSMapRequest)
        req_ex = RequestError('the exception message', request=req)
        ex_handler = WMS111ExceptionHandler()
        self.expect(req.exception_handler).result(ex_handler)
        
        self.replay()
        response = req_ex.render()
        assert response.content_type == 'application/vnd.ogc.se_xml'
        expected_resp = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd">
<ServiceExceptionReport version="1.1.1">
    <ServiceException>the exception message</ServiceException>
</ServiceExceptionReport>
"""
        assert expected_resp.strip() == response.data
        assert validate_with_dtd(response.data, 'wms/1.1.1/exception_1_1_1.dtd')
    def test_render_w_code(self):
        req = self.mock(WMSMapRequest)
        req_ex = RequestError('the exception message', code='InvalidFormat',
                                  request=req)
        ex_handler = WMS111ExceptionHandler()
        self.expect(req.exception_handler).result(ex_handler)
        
        self.replay()
        response = req_ex.render()
        assert response.content_type == 'application/vnd.ogc.se_xml'
        expected_resp = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE ServiceExceptionReport SYSTEM "http://schemas.opengis.net/wms/1.1.1/exception_1_1_1.dtd">
<ServiceExceptionReport version="1.1.1">
    <ServiceException code="InvalidFormat">the exception message</ServiceException>
</ServiceExceptionReport>
"""
        assert expected_resp.strip() == response.data
        assert validate_with_dtd(response.data, 'wms/1.1.1/exception_1_1_1.dtd')

class TestWMS130ExceptionHandler(Mocker):
    def test_render(self):
        req = self.mock(WMSMapRequest)
        req_ex = RequestError('the exception message', request=req)
        ex_handler = WMS130ExceptionHandler()
        self.expect(req.exception_handler).result(ex_handler)
        
        self.replay()
        response = req_ex.render()
        assert response.content_type == 'text/xml; charset=utf-8'
        expected_resp = """
<?xml version='1.0' encoding="UTF-8"?>
<ServiceExceptionReport version="1.3.0"
  xmlns="http://www.opengis.net/ogc"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/ogc
http://schemas.opengis.net/wms/1.3.0/exceptions_1_3_0.xsd">
    <ServiceException>the exception message</ServiceException>
</ServiceExceptionReport>
"""
        assert expected_resp.strip() == response.data
        assert validate_with_xsd(response.data, 'wms/1.3.0/exceptions_1_3_0.xsd')
    def test_render_w_code(self):
        req = self.mock(WMSMapRequest)
        req_ex = RequestError('the exception message', code='InvalidFormat',
                                  request=req)
        ex_handler = WMS130ExceptionHandler()
        self.expect(req.exception_handler).result(ex_handler)
        
        self.replay()
        response = req_ex.render()
        assert response.content_type == 'text/xml; charset=utf-8'
        expected_resp = """
<?xml version='1.0' encoding="UTF-8"?>
<ServiceExceptionReport version="1.3.0"
  xmlns="http://www.opengis.net/ogc"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://www.opengis.net/ogc
http://schemas.opengis.net/wms/1.3.0/exceptions_1_3_0.xsd">
    <ServiceException code="InvalidFormat">the exception message</ServiceException>
</ServiceExceptionReport>
"""
        assert expected_resp.strip() == response.data
        assert validate_with_xsd(response.data, 'wms/1.3.0/exceptions_1_3_0.xsd')

class TestWMS100ExceptionHandler(Mocker):
    def test_render(self):
        req = self.mock(WMSMapRequest)
        req_ex = RequestError('the exception message', request=req)
        ex_handler = WMS100ExceptionHandler()
        self.expect(req.exception_handler).result(ex_handler)
        
        self.replay()
        response = req_ex.render()
        
        assert response.content_type == 'text/xml'
        expected_resp = """
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<WMTException version="1.0.0">
the exception message
</WMTException>
"""
        assert expected_resp.strip() == response.data

class TestWMSImageExceptionHandler(ExceptionHandlerTest):
    def test_exception(self):
        self.req.set('exceptions', 'inimage')
        self.req.set('transparent', 'true' )
        
        req = WMSMapRequest(self.req)
        req_ex = RequestError('the exception message', request=req)
        
        response = req_ex.render()
        assert response.content_type == 'image/png'
        data = StringIO(response.data)
        assert is_png(data)
        img = Image.open(data)
        assert img.size == (150, 100)
    def test_exception_w_transparent(self):
        self.req.set('exceptions', 'inimage')
        self.req.set('transparent', 'true' )
        
        req = WMSMapRequest(self.req)
        req_ex = RequestError('the exception message', request=req)
        
        response = req_ex.render()
        assert response.content_type == 'image/png'
        data = StringIO(response.data)
        assert is_png(data)
        img = Image.open(data)
        assert img.size == (150, 100)
        eq_(img.getpixel((0, 0)), 255)
        eq_([x for x in img.histogram() if x > 25],
            [377, 14623])

class TestWMSBlankExceptionHandler(ExceptionHandlerTest):
    def test_exception(self):
        self.req['exceptions'] = 'blank'
        req = WMSMapRequest(self.req)
        req_ex = RequestError('the exception message', request=req)
        
        response = req_ex.render()
        assert response.content_type == 'image/png'
        data = StringIO(response.data)
        assert is_png(data)
        img = Image.open(data)
        assert img.size == (150, 100)
        eq_(img.getpixel((0, 0)), 0) #pallete image
        eq_(img.getpalette()[0:3], [255, 255, 255])
    def test_exception_w_bgcolor(self):
        self.req.set('exceptions', 'blank')
        self.req.set('bgcolor', '0xff00ff')
        
        req = WMSMapRequest(self.req)
        req_ex = RequestError('the exception message', request=req)
        
        response = req_ex.render()
        assert response.content_type == 'image/png'
        data = StringIO(response.data)
        assert is_png(data)
        img = Image.open(data)
        assert img.size == (150, 100)
        eq_(img.getpixel((0, 0)), 0) #pallete image
        eq_(img.getpalette()[0:3], [255, 0, 255])
    def test_exception_w_transparent(self):
        self.req.set('exceptions', 'blank')
        self.req.set('transparent', 'true' )
        
        req = WMSMapRequest(self.req)
        req_ex = RequestError('the exception message', request=req)
        
        response = req_ex.render()
        assert response.content_type == 'image/png'
        data = StringIO(response.data)
        assert is_png(data)
        img = Image.open(data)
        assert img.size == (150, 100)        
        eq_(img.getpixel((0, 0)), 255)
    