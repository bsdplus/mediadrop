# This file is a part of MediaCore CE (http://www.mediacorecommunity.org),
# Copyright 2009-2012 MediaCore Inc. and other contributors (for the exact
# contribution history, see the git revision history).


from mediacore.lib.test.db_testcase import DBTestCase
from mediacore.lib.test.pythonic_testcase import *
from mediacore.lib.test.request_mixin import RequestMixin


class DefaultPageTitleTest(DBTestCase, RequestMixin):
    def setUp(self):
        super(DefaultPageTitleTest, self).setUp()
        self.init_fake_request()
    
    def test_default_page_title_ignores_default_if_not_specified(self):
        # mediacore.lib.helpers imports 'pylons.request' on class load time
        # so we import the symbol locally after we injected a fake request
        from mediacore.lib.helpers import default_page_title
        assert_equals('MediaCore', default_page_title())


import unittest
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DefaultPageTitleTest))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
