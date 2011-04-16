# -*- coding: utf-8 -*-
from re_eat.tests.common import TestCase, get_app

from PyQt4.QtCore import QEvent
from PyQt4.QtGui import QFocusEvent
from PyQt4.QtTest import QTest
from re_eat.tags import TagsWidget
from re_eat.models import Session, Tag

class TagsWidgetTestCase(TestCase):
    def setUp(self):
        super(TagsWidgetTestCase, self).setUp()
        Session.add_all(Tag(t) for t in [u'lourd', u'pâtes', u'hiver'])
        self.app = get_app()

    def test_widget_is_empty_first(self):
        tw = TagsWidget()

        self.assertEqual(tw.listWidget.count(), 0)

    def test_adding_tags_in_the_widget(self):
        tw = TagsWidget()

        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag() # Called manually because we would need an event loop otherwise

        self.assertEqual(tw.listWidget.count(), 1)

    def test_invalid_tag_is_invalid(self):
        tw = TagsWidget()
        QTest.keyClicks(tw, 'trololo')
        tw.addTag()

        self.assertEqual(tw.listWidget.count(), 0)

    def test_cant_add_twice_the_same(self):
        tw = TagsWidget()

        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag()
        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag()

        self.assertEqual(tw.listWidget.count(), 1)

    def test_cant_add_twice_the_same_even_after_reload(self):
        tw = TagsWidget()
        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag()
        Session.add(Tag(u'Another tag'))
        Session.commit()
        tw.reload()

        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag()

        self.assertEqual(tw.listWidget.count(), 1)

    def test_getting_the_entered_tags(self):
        tw = TagsWidget()

        QTest.keyClicks(tw.lineEdit, 'lourd')
        tw.addTag()

        expected = [t.id for t in Session.query(Tag.id).filter(Tag.name == u'lourd').all()]
        self.assertEqual(tw.tags(), expected)

    def test_the_completion_popup_appears(self):
        tw = TagsWidget()

        tw.lineEdit.focusInEvent(QFocusEvent(QEvent.FocusIn))

        self.assert_(tw.lineEdit.completer().popup().isVisible(),
                     "Completion popup doesn't appear on focus")