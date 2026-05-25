"""
Tests for Main Application Entry Point
Author: Inventions4All - github:TWeb79
"""

import pytest
import sys
from unittest.mock import patch, MagicMock
from neurosync.app.main import main


class TestMainApplication:
    """Tests for main application entry point."""

    @patch('neurosync.app.main.QApplication')
    @patch('neurosync.app.main.QWebEngineView')
    def test_main_creates_app(self, mock_view_class, mock_app_class):
        """Test that main creates QApplication."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.exec.return_value = 0
        
        result = main()
        
        mock_app_class.assert_called_once()
        assert result == 0

    @patch('neurosync.app.main.QApplication')
    @patch('neurosync.app.main.QWebEngineView')
    def test_main_creates_web_engine_view(self, mock_view_class, mock_app_class):
        """Test that main creates QWebEngineView."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.exec.return_value = 0
        mock_view = MagicMock()
        mock_view_class.return_value = mock_view
        
        main()
        
        mock_view_class.assert_called_once()
        mock_view.load.assert_called_once()

    @patch('neurosync.app.main.QApplication')
    @patch('neurosync.app.main.QWebEngineView')
    def test_main_sets_window_properties(self, mock_view_class, mock_app_class):
        """Test that window properties are set correctly."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.exec.return_value = 0
        mock_view = MagicMock()
        mock_view_class.return_value = mock_view
        
        main()
        
        mock_view.setWindowTitle.assert_called_once()
        mock_view.resize.assert_called_once_with(1200, 800)
        mock_view.show.assert_called_once()

    @patch('neurosync.app.main.QApplication')
    @patch('neurosync.app.main.QWebEngineView')
    def test_main_loads_html_file(self, mock_view_class, mock_app_class):
        """Test that HTML file is loaded."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.exec.return_value = 0
        mock_view = MagicMock()
        mock_view_class.return_value = mock_view
        
        main()
        
        # Verify load was called with a URL
        mock_view.load.assert_called_once()
        call_args = mock_view.load.call_args
        assert call_args is not None

    @patch('neurosync.app.main.QApplication')
    @patch('neurosync.app.main.QWebEngineView')
    def test_main_returns_exec_result(self, mock_view_class, mock_app_class):
        """Test that main returns the exec() result."""
        mock_app = MagicMock()
        mock_app_class.return_value = mock_app
        mock_app.exec.return_value = 42
        mock_view = MagicMock()
        mock_view_class.return_value = mock_view
        
        result = main()
        
        assert result == 42
        mock_app.exec.assert_called_once()
